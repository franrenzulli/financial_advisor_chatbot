import os
import logging
from threading import Lock
from config import PROCESSED_FILES_PATH, PROBLEMATIC_FILES_PATH

logger = logging.getLogger(__name__)

class FileTracker:
    """Maneja el seguimiento de archivos procesados y problemáticos"""
    
    def __init__(self):
        self.file_lock = Lock()
        self.processed_set = set()
        self.problematic_set = set()
        self._load_processed_files()
    
    def _load_processed_files(self):
        """Carga la lista de archivos ya procesados"""
        if os.path.exists(PROCESSED_FILES_PATH):
            try:
                with open(PROCESSED_FILES_PATH, 'r') as f:
                    self.processed_set = {line.strip() for line in f if line.strip()}
                logger.info(f"📂 Cargados {len(self.processed_set)} archivos procesados previamente")
            except Exception as e:
                logger.warning(f"⚠️ Error cargando archivos procesados: {e}")
                self.processed_set = set()
    
    def get_processed_keys(self):
        """Retorna el conjunto de claves ya procesadas"""
        return self.processed_set.copy()
    
    def save_processed_key(self, key):
        """
        Guarda una clave como procesada
        
        Args:
            key (str): Clave del archivo procesado
        """
        with self.file_lock:
            if key not in self.processed_set:
                try:
                    with open(PROCESSED_FILES_PATH, 'a') as f:
                        f.write(f"{key}\n")
                    self.processed_set.add(key)
                    logger.debug(f"📝 Guardado en processed_pdfs.txt: {key}")
                except Exception as e:
                    logger.error(f"❌ Error guardando clave procesada {key}: {e}")
    
    def add_problematic_file(self, key):
        """
        Marca un archivo como problemático
        
        Args:
            key (str): Clave del archivo problemático
        """
        with self.file_lock:
            self.problematic_set.add(key)
    
    def save_problematic_files(self):
        """Guarda la lista de archivos problemáticos en disco"""
        if self.problematic_set:
            try:
                with open(PROBLEMATIC_FILES_PATH, "w") as f:
                    for file in sorted(self.problematic_set):
                        f.write(f"{file}\n")
                logger.info(f"⚠️ Guardados {len(self.problematic_set)} archivos problemáticos")
            except Exception as e:
                logger.error(f"❌ Error guardando archivos problemáticos: {e}")
    
    def get_problematic_files(self):
        """Retorna el conjunto de archivos problemáticos"""
        return self.problematic_set.copy()
    
    def filter_unprocessed_keys(self, pdf_keys):
        """
        Filtra las claves para obtener solo las no procesadas
        
        Args:
            pdf_keys (list): Lista de claves de PDFs
            
        Returns:
            list: Lista de claves no procesadas
        """
        unprocessed = [key for key in pdf_keys if key not in self.processed_set]
        logger.info(f"📋 Total PDFs: {len(pdf_keys)}, Ya procesados: {len(pdf_keys) - len(unprocessed)}, Por procesar: {len(unprocessed)}")
        return unprocessed