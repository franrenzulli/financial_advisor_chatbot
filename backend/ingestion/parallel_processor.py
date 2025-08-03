import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from threading import Lock
from s3_client import S3Client
from pdf_processor import PDFProcessor
from file_tracker import FileTracker

logger = logging.getLogger(__name__)

class ParallelProcessor:
    """Maneja el procesamiento paralelo de PDFs"""
    
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self.s3_client = S3Client()
        self.pdf_processor = PDFProcessor()
        self.file_tracker = FileTracker()
        
        self.stats_lock = Lock()
        self.total_pdfs_processed_in_run = 0
        self.total_chunks_generated_in_run = 0
        self.errors_in_run = []
        
        logger.info(f"ParallelProcessor inicializado con {max_workers} workers")
    
    def _process_single_pdf(self, key):
        """Procesa un solo PDF (sin cambios en esta función)"""
        try:
            pdf_data = self.s3_client.download_with_retry(key)
            docs, error = self.pdf_processor.process_pdf_content(pdf_data, key)
            
            if error:
                self.file_tracker.add_problematic_file(key)
                return [], error
            
            with self.stats_lock:
                self.total_pdfs_processed_in_run += 1
                self.total_chunks_generated_in_run += len(docs)
            
            self.file_tracker.save_processed_key(key)
            return docs, None
            
        except Exception as e:
            error_msg = f"Error procesando {key}: {str(e)}"
            logger.error(error_msg)
            self.file_tracker.add_problematic_file(key)
            return [], error_msg
    
    def process_batch(self, pdf_keys_batch: list) -> list:
        """
        Procesa un lote de PDFs en paralelo y devuelve los documentos.
        """
        batch_docs = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="PDFWorker") as executor:
            future_to_key = {executor.submit(self._process_single_pdf, key): key for key in pdf_keys_batch}
            
            for future in as_completed(future_to_key):
                key = future_to_key[future]
                try:
                    docs, error = future.result(timeout=300) # Timeout de 5 mins por PDF
                    
                    if error:
                        self.errors_in_run.append((key, error))
                    elif docs:
                        batch_docs.extend(docs)
                        
                except Exception as e:
                    error_msg = f"Error inesperado en future para {key}: {str(e)}"
                    logger.error(f"💥 {error_msg}")
                    self.errors_in_run.append((key, error_msg))
                    self.file_tracker.add_problematic_file(key)
        
        return batch_docs
    
    def get_stats(self):
        """Retorna las estadísticas del procesamiento"""
        stats = {
            'total_pdfs': self.total_pdfs_processed_in_run,
            'total_chunks': self.total_chunks_generated_in_run,
            'total_errors': len(self.errors_in_run),
            'errors': self.errors_in_run,
            'problematic_files': self.file_tracker.get_problematic_files()
        }
        # Reiniciar contadores para la siguiente ejecución si es necesario
        self.total_pdfs_processed_in_run = 0
        self.total_chunks_generated_in_run = 0
        self.errors_in_run = []
        return stats