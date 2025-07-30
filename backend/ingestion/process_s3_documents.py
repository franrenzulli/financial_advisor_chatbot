#!/usr/bin/env python3
"""
Sistema modular para procesamiento de documentos PDF desde S3
Crea una base vectorial usando ChromaDB y embeddings de HuggingFace
"""

import os
import time
from config import (
    AWS_BUCKET, PREFIX, WORKERS, BATCH_SIZE,
    setup_logging
)
from s3_client import S3Client
from parallel_processor import ParallelProcessor
from vector_store_manager import VectorStoreManager
from file_tracker import FileTracker


# Configurar logging
logger = setup_logging()

class DocumentIngestionPipeline:
    """Pipeline principal para ingestión de documentos"""
    
    def __init__(self):
        self.s3_client = S3Client()
        self.processor = ParallelProcessor(max_workers=WORKERS, batch_size=BATCH_SIZE)
        self.vector_manager = VectorStoreManager()
        self.file_tracker = FileTracker()
        
        logger.info("🚀 Pipeline de ingestión inicializado")
        self._log_environment_info()
    
    def _log_environment_info(self):
        """Registra información del entorno"""
        logger.info(f"🖥️ Directorio actual: {os.getcwd()}")
        logger.info(f"🖥️ Ruta del script: {os.path.dirname(os.path.abspath(__file__))}")
        logger.info(f"⚙️ Workers: {WORKERS}, Batch size: {BATCH_SIZE}")
        logger.info(f"📦 Bucket: {AWS_BUCKET}, Prefijo: {PREFIX or 'Sin prefijo'}")
    
    def get_pdfs_to_process(self):
        """
        Obtiene la lista de PDFs que necesitan ser procesados
        
        Returns:
            list: Lista de claves de PDFs no procesados
        """
        logger.info("🔍 Obteniendo lista de PDFs desde S3...")
        all_pdf_keys = self.s3_client.get_pdf_keys(PREFIX)
        
        if not all_pdf_keys:
            logger.warning("⚠️ No se encontraron PDFs en S3")
            return []
        
        # Filtrar PDFs ya procesados
        unprocessed_keys = self.file_tracker.filter_unprocessed_keys(all_pdf_keys)
        
        return unprocessed_keys
    
    def process_documents(self, pdf_keys_batch):
        """
        Procesa los documentos PDF
        
        Args:
            pdf_keys (list): Lista de claves de PDFs a procesar
            
        Returns:
            list: Lista de documentos procesados
        """
        if not pdf_keys_batch:
            logger.info("✅ No hay PDFs nuevos para procesar")
            return []
        
        logger.info(f"📋 Procesando {len(pdf_keys_batch)} PDFs...")
        
        # Procesar PDFs en paralelo
        documents = self.processor.process_pdfs_in_parallel(pdf_keys_batch)
        
        if not documents:
            logger.warning("⚠️ No se generaron documentos válidos")
            return []
        
        logger.info(f"📄 Total de documentos generados: {len(documents):,}")
        return documents
    
    def save_to_vector_store(self, documents):
        """
        Guarda documentos en la base vectorial
        
        Args:
            documents (list): Lista de documentos a guardar
        """
        if not documents:
            logger.warning("⚠️ No hay documentos para guardar")
            return
        
        # Limpiar base vectorial anterior
        # self.vector_manager.clean_existing_store()
        
        # Guardar documentos
        save_time = self.vector_manager.save_documents(documents)
        
        # Verificar integridad
        if self.vector_manager.verify_store_integrity():
            logger.info("✅ Base vectorial creada y verificada exitosamente")
        else:
            logger.error("❌ Error en la verificación de la base vectorial")
    
    def log_final_stats(self, total_time):
        """
        Registra las estadísticas finales del procesamiento
        
        Args:
            total_time (float): Tiempo total de procesamiento
        """
        stats = self.processor.get_stats()
        
        logger.info("\n" + "="*60)
        logger.info("✅ PROCESO FINALIZADO")
        logger.info("="*60)
        logger.info("📊 Resumen final:")
        logger.info(f"  - PDFs procesados exitosamente: {stats['total_pdfs']:,}")
        logger.info(f"  - Fragmentos generados: {stats['total_chunks']:,}")
        logger.info(f"  - Errores encontrados: {stats['total_errors']:,}")
        logger.info(f"  - Tiempo total: {total_time/60:.1f} minutos")
        logger.info(f"  - Velocidad promedio: {stats['total_pdfs']/(total_time/60):.1f} PDFs/min")
        
        if stats['problematic_files']:
            logger.info(f"⚠️ Archivos problemáticos: {stats['problematic_files']}")
            self.file_tracker.save_problematic_files()
        
        # Información de la base vectorial
        vector_info = self.vector_manager.get_store_info()
        logger.info(f"💾 Documentos en base vectorial: {vector_info.get('document_count', 'N/A'):,}")
    
    def run(self):
        """Ejecuta el pipeline completo"""
        try:
            logger.info("🚀 Iniciando proceso de ingestión desde S3...")
            start_total = time.time()
            
            # 1. Obtener PDFs a procesar
            pdf_keys = self.get_pdfs_to_process()
            
            if not pdf_keys:
                logger.info("✅ Todos los PDFs ya fueron procesados.")
                return
            
            logger.info(f"📋 Total PDFs por procesar: {len(pdf_keys)}")

            total_documents_saved = 0
            total_batches = (len(pdf_keys) + BATCH_SIZE - 1) // BATCH_SIZE

            for batch_num, batch_start in enumerate(range(0, len(pdf_keys), BATCH_SIZE)):
                batch_end = min(batch_start + BATCH_SIZE, len(pdf_keys))
                current_batch = pdf_keys[batch_start:batch_end]

                batch_documents = self.process_documents(current_batch)

                if not batch_documents:
                    logger.warning("⚠️ No se procesaron documentos válidos. Finalizando.")
                    return

                saved_count = self.save_to_vector_store(batch_documents)
        
                logger.info(f"🔄 Procesando lote {batch_num}/{total_batches} ({len(current_batch)} PDFs)")

                logger.info(f"💾 Lote {batch_num} guardado: {saved_count} fragmentos")
                logger.info(f"📊 Progreso total: {batch_end}/{len(pdf_keys)} PDFs ({(batch_end/len(pdf_keys)*100):.1f}%)")

            
            # 4. Mostrar estadísticas finales
            total_time = time.time() - start_total
            self.log_final_stats(total_time)
            
        except KeyboardInterrupt:
            logger.info("⏹️ Proceso interrumpido por el usuario")
            raise
        except Exception as e:
            logger.critical(f"💥 Error crítico en el pipeline: {e}", exc_info=True)
            raise


def main():
    """Función principal"""
    try:
        pipeline = DocumentIngestionPipeline()
        pipeline.run()
        
    except KeyboardInterrupt:
        logger.info("👋 Proceso cancelado por el usuario")
    except Exception as e:
        logger.critical(f"💥 Error fatal: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()