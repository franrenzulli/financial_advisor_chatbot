"""
Sistema modular de procesamiento de documentos PDF desde S3

Este paquete proporciona un pipeline completo para:
- Descargar PDFs desde AWS S3
- Procesar y fragmentar documentos
- Crear embeddings usando HuggingFace
- Almacenar en base vectorial ChromaDB
"""

from .config import setup_logging
from .s3_client import S3Client
from .pdf_processor import PDFProcessor
from .file_tracker import FileTracker
from .parallel_processor import ParallelProcessor
from .vector_store_manager import VectorStoreManager

__version__ = "1.0.0"
__author__ = "group-3"

# Configurar logging al importar el paquete
logger = setup_logging()

__all__ = [
    'S3Client',
    'PDFProcessor', 
    'FileTracker',
    'ParallelProcessor',
    'VectorStoreManager',
    'setup_logging'
]