

from chromadb.utils import embedding_functions
from chromadb import Client
from typing import List

# --- Configuración de Chroma ---
CHROMA_DB_PATH = "./chroma_db"  # Carpeta donde se guardan los datos
COLLECTION_NAME = "documents"   # Nombre de la colección

def retrieve_relevant_chunks(question_embedding, top_k: int = 3) -> List[str]:
    """
    Busca en ChromaDB los chunks más similares al embedding de la pregunta.
    Devuelve una lista de textos relevantes.
    """
    # Conexión al cliente de Chroma
    chroma_client = Client(settings={"persist_directory": CHROMA_DB_PATH})
    
    # Obtener la colección ya existente con los embeddings indexados
    collection = chroma_client.get_collection(name=COLLECTION_NAME)

    # Ejecutar búsqueda
    results = collection.query(
        query_embeddings=[question_embedding.tolist()],  # debe ser lista de listas
        n_results=top_k
    )

    # results['documents'] es una lista de listas → flatten
    retrieved_chunks = results["documents"][0]

    return retrieved_chunks
