import time
import logging
import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from config import CHROMA_PERSIST_DIR, EMBEDDING_MODEL

logger = logging.getLogger(__name__)

class VectorStoreManager:
    """Maneja las operaciones de la base vectorial"""
    
    def __init__(self):
        self.embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        # --- CORRECCIÓN AQUÍ ---
        # Usamos la variable correcta importada desde config.py
        self.vector_dir = CHROMA_PERSIST_DIR
        self.collection_name = "financial_documents"
        logger.info(f"VectorStoreManager inicializado con modelo: {EMBEDDING_MODEL}")
    
    def initialize_store(self):
        """
        Asegura que el directorio para la base de datos persistente exista.
        """
        try:
            logger.info(f"Inicializando o verificando el directorio del vector store en: {self.vector_dir}")
            os.makedirs(self.vector_dir, exist_ok=True)
            _ = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embedding_function,
                persist_directory=self.vector_dir
            )
            logger.info("✅ Directorio del Vector Store listo para usarse.")
        except Exception as e:
            logger.error(f"❌ No se pudo inicializar el directorio del Vector Store: {e}")
            raise

    def save_documents(self, documents):
        """
        Guarda documentos en la base vectorial. Si ya existe, añade los nuevos.
        """
        if not documents:
            logger.warning("⚠️ No hay documentos para guardar")
            return 0
        
        try:
            logger.info(f"💾 Guardando {len(documents):,} documentos en ChromaDB...")
            start_time = time.time()
            
            Chroma.from_documents(
                documents, 
                embedding=self.embedding_function, 
                persist_directory=self.vector_dir,
                collection_name=self.collection_name
            )
            
            save_time = time.time() - start_time
            
            logger.info(f"✅ Documentos guardados exitosamente en {save_time:.1f}s")
            return save_time
            
        except Exception as e:
            logger.error(f"❌ Error guardando documentos: {e}")
            raise
    
    def get_store_info(self):
        """Obtiene información sobre la base vectorial"""
        try:
            vectorstore = Chroma(
                persist_directory=self.vector_dir,
                embedding_function=self.embedding_function,
                collection_name=self.collection_name
            )
            count = vectorstore._collection.count()
            return {'document_count': count}
        except Exception as e:
            logger.error(f"❌ Error obteniendo información: {e}")
            return {'document_count': 0, 'error': str(e)}
    
    def verify_store_integrity(self):
        """Verifica la integridad de la base vectorial"""
        try:
            vectorstore = Chroma(
                persist_directory=self.vector_dir,
                embedding_function=self.embedding_function,
                collection_name=self.collection_name
            )
            _ = vectorstore.similarity_search("test", k=1)
            logger.info("✅ Base vectorial verificada exitosamente")
            return True
        except Exception as e:
            logger.error(f"❌ Error verificando integridad: {e}")
            return False