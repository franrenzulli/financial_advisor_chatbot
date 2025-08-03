import logging
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_core.documents import Document
from ingestion.config import CHROMA_PERSIST_DIR # Usamos la ruta centralizada

logger = logging.getLogger(__name__)

# --- CONFIGURACIÓN ---
COLLECTION_NAME = "financial_documents"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# --- INICIALIZACIÓN ---
try:
    print(" retriever.py: Cargando modelo de embeddings...")
    embedding_function = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    print(" retriever.py: Modelo de embeddings cargado exitosamente.")
except Exception as e:
    logger.critical(f" retriever.py: No se pudo cargar el modelo de embeddings: {e}")
    embedding_function = None

def retrieve_chunks(query: str, top_k: int = 3) -> list[Document]:
    """
    Recupera los chunks más relevantes de ChromaDB de forma obligatoria.
    Devuelve una lista vacía si no hay resultados o si ocurre un error.
    """
    print("\n--- retrieve_chunks ---")
    print(f"DEBUG: Iniciando búsqueda para la query: '{query}'")

    if not embedding_function:
        logger.error(" retriever.py: El embedding_function no está disponible. No se puede buscar.")
        print("DEBUG: Finalizando por falta de modelo de embeddings.")
        return []

    try:
        print(f"DEBUG: Intentando conectar a ChromaDB en: {CHROMA_PERSIST_DIR}")
        vectorstore = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embedding_function,
            persist_directory=CHROMA_PERSIST_DIR
        )
        print("DEBUG: Conexión a ChromaDB exitosa.")

        print(f"DEBUG: Ejecutando similarity_search con k={top_k}...")
        results = vectorstore.similarity_search(query, k=top_k)
        
        if not results:
            print("DEBUG: La búsqueda no arrojó resultados. La base de datos puede estar vacía o el contenido no es relevante.")
            print("--- Fin de retrieve_chunks ---\n")
            return []

        print(f"DEBUG: Búsqueda real encontró {len(results)} chunks.")
        print("--- Fin de retrieve_chunks ---\n")
        return results

    except Exception as e:
        logger.error(f" retriever.py: Error crítico al conectar o buscar en ChromaDB: {e}")
        print(f"DEBUG: La excepción fue: {e}")
        print("DEBUG: Devolviendo lista vacía debido a un error.")
        print("--- Fin de retrieve_chunks ---\n")
        return []