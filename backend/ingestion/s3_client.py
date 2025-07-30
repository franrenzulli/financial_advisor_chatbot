import boto3
import time
import logging
from botocore.exceptions import ClientError
import botocore.exceptions
from botocore.config import Config
from config import AWS_BUCKET, AWS_REGION, S3_CONFIG, MIN_FILE_SIZE, MAX_FILE_SIZE, MAX_RETRIES

logger = logging.getLogger(__name__)

class S3Client:
    """Cliente S3 con funcionalidades específicas para procesamiento de PDFs"""
    
    def __init__(self):
        self.client = boto3.client("s3", config=S3_CONFIG)
        logger.info(f"Cliente S3 inicializado para bucket: {AWS_BUCKET}")
    
    def get_pdf_keys(self, prefix=""):
        """Obtiene claves de PDFs con paginación"""
        pdf_keys = []
        try:
            paginator = self.client.get_paginator('list_objects_v2')
            params = {'Bucket': AWS_BUCKET}
            
            if prefix:
                params['Prefix'] = prefix
                logger.info(f"🔍 Buscando PDFs con prefijo: {prefix}")
            
            page_iterator = paginator.paginate(
                **params,
                PaginationConfig={'PageSize': 1000}
            )
            
            total_objects = 0
            for page in page_iterator:
                if "Contents" in page:
                    batch_pdfs = [
                        item["Key"] 
                        for item in page["Contents"] 
                        if (item["Key"].endswith(".pdf") and 
                            MIN_FILE_SIZE <= item["Size"] <= MAX_FILE_SIZE)
                    ]
                    pdf_keys.extend(batch_pdfs)
                    total_objects += len(page["Contents"])
            
            logger.info(f"📊 Resumen: {total_objects} objetos, {len(pdf_keys)} PDFs válidos")
            return pdf_keys
            
        except Exception as e:
            logger.error(f"❌ Error al obtener objetos de S3: {e}")
            return []
    
    def download_with_retry(self, key):
        """Descarga un archivo con reintentos automáticos"""
        for attempt in range(MAX_RETRIES):
            try:
                # Obtener tamaño primero para timeout adaptativo
                head = self.client.head_object(Bucket=AWS_BUCKET, Key=key)
                size_mb = head['ContentLength'] / (1024 * 1024)
                timeout = min(300, 30 + size_mb)  # 30s base + 1s por MB
                
                # Configurar timeout para esta descarga
                custom_config = Config(
                    read_timeout=timeout,
                    retries={'max_attempts': 3}
                )
                temp_s3 = boto3.client('s3', config=custom_config)
                
                logger.info(f"⌛ [{key}] Descargando ({size_mb:.1f}MB) con timeout {timeout}s...")
                response = temp_s3.get_object(Bucket=AWS_BUCKET, Key=key)
                return response['Body'].read()
                
            except (ClientError, botocore.exceptions.ReadTimeoutError, 
                   botocore.exceptions.IncompleteReadError) as e:
                if attempt == MAX_RETRIES - 1:
                    raise
                wait_time = 2 ** attempt  # Espera exponencial
                logger.warning(f"⚠️ [{key}] Reintento {attempt + 1}/{MAX_RETRIES} en {wait_time}s...")
                time.sleep(wait_time)