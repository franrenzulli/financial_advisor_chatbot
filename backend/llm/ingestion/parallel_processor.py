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
    
    def __init__(self, max_workers=4, batch_size=10):
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.s3_client = S3Client()
        self.pdf_processor = PDFProcessor()
        self.file_tracker = FileTracker()
        
        # Variables para estadísticas thread-safe
        self.stats_lock = Lock()
        self.total_pdfs = 0
        self.total_chunks = 0
        self.errors = []
        
        logger.info(f"ParallelProcessor inicializado: {max_workers} workers, lotes de {batch_size}")
    
    def _process_single_pdf(self, key):
        """
        Procesa un solo PDF
        
        Args:
            key (str): Clave del PDF en S3
            
        Returns:
            tuple: (documentos, error_mensaje)
        """
        try:
            # Descargar PDF
            pdf_data = self.s3_client.download_with_retry(key)
            
            # Procesar PDF
            docs, error = self.pdf_processor.process_pdf_content(pdf_data, key)
            
            if error:
                self.file_tracker.add_problematic_file(key)
                return [], error
            
            # Actualizar estadísticas
            with self.stats_lock:
                self.total_pdfs += 1
                self.total_chunks += len(docs)
            
            # Marcar como procesado
            self.file_tracker.save_processed_key(key)
            
            return docs, None
            
        except Exception as e:
            error_msg = f"Error procesando {key}: {str(e)}"
            logger.error(error_msg)
            self.file_tracker.add_problematic_file(key)
            return [], error_msg
    
    def process_pdfs_in_parallel(self, pdf_keys):
        """
        Procesa PDFs en paralelo con control de lotes
        
        Args:
            pdf_keys (list): Lista de claves de PDFs a procesar
            
        Returns:
            list: Lista de documentos procesados
        """
        all_docs = []
        processed = 0
        
        for i in range(0, len(pdf_keys), self.batch_size):
            batch = pdf_keys[i:i + self.batch_size]
            batch_docs = []
            
            batch_num = i // self.batch_size + 1
            total_batches = (len(pdf_keys) + self.batch_size - 1) // self.batch_size
            
            logger.info(f"\n🔄 Procesando lote {batch_num}/{total_batches}")
            logger.info(f"📦 PDFs en este lote: {len(batch)}")
            
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="PDFWorker") as executor:
                future_to_key = {
                    executor.submit(self._process_single_pdf, key): key 
                    for key in batch
                }
                
                for future in as_completed(future_to_key):
                    key = future_to_key[future]
                    try:
                        docs, error = future.result(timeout=300)
                        
                        if error:
                            self.errors.append((key, error))
                        elif docs:
                            batch_docs.extend(docs)
                        
                        processed += 1
                        
                        # Mostrar progreso cada 10 PDFs
                        if processed % 10 == 0:
                            self._log_progress(processed, len(pdf_keys), start_time)
                            
                    except TimeoutError:
                        error_msg = f"Timeout procesando {key}"
                        logger.error(f"⏰ {error_msg}")
                        self.errors.append((key, error_msg))
                        self.file_tracker.add_problematic_file(key)
                    except Exception as e:
                        error_msg = f"Error inesperado: {str(e)}"
                        logger.error(f"💥 {error_msg}")
                        self.errors.append((key, error_msg))
                        self.file_tracker.add_problematic_file(key)
            
            all_docs.extend(batch_docs)
            batch_time = time.time() - start_time
            
            logger.info(f"✅ Lote completado en {batch_time:.1f}s")
            logger.info(f"📈 Fragmentos generados: {len(batch_docs)}")
            
            # Pausa entre lotes para reducir carga
            if i + self.batch_size < len(pdf_keys):
                time.sleep(2)
        
        return all_docs
    
    def _log_progress(self, processed, total, start_time):
        """Registra el progreso del procesamiento"""
        elapsed = time.time() - start_time
        rate = processed / elapsed if elapsed > 0 else 0
        remaining = total - processed
        eta = remaining / rate if rate > 0 else 0
        
        logger.info(
            f"📊 Progreso: {processed}/{total} "
            f"({processed/total*100:.1f}%) "
            f"- Velocidad: {rate:.1f} PDFs/min "
            f"- ETA: {eta/60:.1f} min"
        )
    
    def get_stats(self):
        """Retorna las estadísticas del procesamiento"""
        return {
            'total_pdfs': self.total_pdfs,
            'total_chunks': self.total_chunks,
            'total_errors': len(self.errors),
            'errors': self.errors,
            'problematic_files': self.file_tracker.get_problematic_files()
        }