import os
from dotenv import load_dotenv
from botocore.config import Config
import logging

load_dotenv()

# Configuración de AWS
AWS_BUCKET = os.getenv("AWS_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
PREFIX = os.getenv("PREFIX")

# Configuración de archivos y directorios
VECTOR_DIR = "/app/vector-store"
PROCESSED_FILES_PATH = "ingestion/processed_pdfs.txt"
PROBLEMATIC_FILES_PATH = "ingestion/problematic_files.txt"
LOG_FILE_PATH = "ingestion/pdf_processing.log"

# Configuración de procesamiento
WORKERS = int(os.getenv("WORKERS", 4))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 10))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))

# Configuración de archivos PDF
MIN_FILE_SIZE = 1024  # 1KB
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_RETRIES = 3

# Configuración mejorada del cliente S3
S3_CONFIG = Config(
    retries={
        'max_attempts': 5,
        'mode': 'adaptive'
    },
    connect_timeout=30,
    read_timeout=120,
    max_pool_connections=50
)

# Configuración de logging
def setup_logging():
    """Configura el sistema de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_FILE_PATH)
        ]
    )
    return logging.getLogger(__name__)

# Configuración de embeddings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"