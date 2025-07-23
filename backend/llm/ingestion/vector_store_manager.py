import time
import logging
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from config import VECTOR_DIR, EMBEDDING_MODEL

logger = logging.getLogger(__name__)

class VectorStoreManager:
    """Maneja las operaciones de la base vectorial"""
    
    def __init__(self):
        self.embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        self.vector_dir = VECTOR_DIR
        logger.info(f"VectorStoreManager inicializado con modelo: {EMBEDDING_MODEL}")
    
    def clean_existing_store(self):
        """Limpia la base vectorial existente"""
        try:
            logger.info("🧹 Limpiando base vectorial anterior...")
            clean_vector_store(self.vector_dir)
            logger.info("✅ Base vectorial limpiada exitosamente")
        except Exception as e:
            logger.error(f"❌ Error limpiando base vectorial: {e}")
            raise
    
    def save_documents(self, documents):
        """
        Guarda documentos en la base vectorial
        
        Args:
            documents (list): Lista de documentos a guardar
            
        Returns:
            float: Tiempo que tomó guardar los documentos
        """
        if not documents:
            logger.warning("⚠️ No hay documentos para guardar")
            return 0
        
        try:
            logger.info(f"💾 Guardando {len(documents):,} documentos en ChromaDB...")
            start_time = time.time()
            
            # Crear la base vectorial
            vectorstore = Chroma.from_documents(
                documents, 
                embedding=self.embedding_function, 
                persist_directory=self.vector_dir
            )
            
            save_time = time.time() - start_time
            
            logger.info(f"✅ Documentos guardados exitosamente en {save_time:.1f}s")
            return save_time
            
        except Exception as e:
            logger.error(f"❌ Error guardando documentos: {e}")
            raise
    
    def get_store_info(self):
        """
        Obtiene información sobre la base vectorial
        
        Returns:
            dict: Información de la base vectorial
        """
        try:
            vectorstore = Chroma(
                persist_directory=self.vector_dir,
                embedding_function=self.embedding_function
            )
            
            collection = vectorstore._collection
            count = collection.count()
            
            return {
                'document_count': count,
                'vector_dir': self.vector_dir,
                'embedding_model': EMBEDDING_MODEL
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo información de la base vectorial: {e}")
            return {
                'document_count': 0,
                'vector_dir': self.vector_dir,
                'embedding_model': EMBEDDING_MODEL,
                'error': str(e)
            }
    
    def verify_store_integrity(self):
        """
        Verifica la integridad de la base vectorial
        
        Returns:
            bool: True si la base vectorial está íntegra
        """
        try:
            vectorstore = Chroma(
                persist_directory=self.vector_dir,
                embedding_function=self.embedding_function
            )
            
            # Realizar una consulta simple para verificar que funciona
            test_results = vectorstore.similarity_search("test", k=1)
            
            logger.info("✅ Base vectorial verificada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error verificando integridad de la base vectorial: {e}")
            return False