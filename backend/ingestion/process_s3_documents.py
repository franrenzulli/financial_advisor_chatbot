import os
import time
from config import AWS_BUCKET, PREFIX, WORKERS, BATCH_SIZE, setup_logging
from s3_client import S3Client
from parallel_processor import ParallelProcessor
from vector_store_manager import VectorStoreManager
from file_tracker import FileTracker

logger = setup_logging()

class DocumentIngestionPipeline:
    """Pipeline principal para ingestión de documentos"""
    
    def __init__(self):
        self.s3_client = S3Client()
        self.processor = ParallelProcessor(max_workers=WORKERS)
        self.vector_manager = VectorStoreManager()
        self.file_tracker = FileTracker()
        logger.info("🚀 Pipeline de ingestión inicializado")

    def run(self):
        """Ejecuta el pipeline completo"""
        try:
            logger.info("🚀 Iniciando proceso de ingestión desde S3...")
            start_total = time.time()
            
            # 1. Asegurarse que el Vector Store esté listo desde el principio
            self.vector_manager.initialize_store()

            # 2. Obtener PDFs a procesar
            all_pdf_keys = self.s3_client.get_pdf_keys(PREFIX)
            pdf_keys_to_process = self.file_tracker.filter_unprocessed_keys(all_pdf_keys)
            
            if not pdf_keys_to_process:
                logger.info("✅ No hay PDFs nuevos para procesar. Todo está actualizado.")
                return

            logger.info(f"📋 Total PDFs por procesar: {len(pdf_keys_to_process)}")
            total_batches = (len(pdf_keys_to_process) + BATCH_SIZE - 1) // BATCH_SIZE
            
            # 3. Procesar y guardar en lotes
            for i, batch_start in enumerate(range(0, len(pdf_keys_to_process), BATCH_SIZE)):
                batch_num = i + 1
                batch_end = min(batch_start + BATCH_SIZE, len(pdf_keys_to_process))
                current_batch_keys = pdf_keys_to_process[batch_start:batch_end]
                
                logger.info(f"\n--- 🔄 Procesando Lote {batch_num}/{total_batches} ({len(current_batch_keys)} PDFs) ---")
                
                # Procesar el lote actual
                batch_docs = self.processor.process_batch(current_batch_keys)
                
                if not batch_docs:
                    logger.warning(f"⚠️ Lote {batch_num} no generó documentos.")
                    continue

                # Guardar los documentos del lote actual en ChromaDB
                logger.info(f"💾 Guardando {len(batch_docs)} fragmentos del lote {batch_num} en ChromaDB...")
                self.vector_manager.save_documents(batch_docs)
                logger.info(f"✅ Lote {batch_num} guardado exitosamente.")
                
                # Log de progreso general
                progress_percent = (batch_end / len(pdf_keys_to_process)) * 100
                logger.info(f"📊 Progreso Total: {batch_end}/{len(pdf_keys_to_process)} PDFs ({progress_percent:.1f}%)")

            total_time = time.time() - start_total
            logger.info(f"🎉 Proceso de ingestión completado en {total_time/60:.2f} minutos.")

        except Exception as e:
            logger.critical(f"💥 Error crítico en el pipeline de ingestión: {e}", exc_info=True)

def main():
    try:
        pipeline = DocumentIngestionPipeline()
        pipeline.run()
    except Exception:
        logger.critical("💥 El pipeline de ingestión ha fallado.")

if __name__ == "__main__":
    main()