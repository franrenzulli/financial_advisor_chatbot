# retriever.py
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
import os
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "documents"

embedding_function = SentenceTransformerEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# --- Chunks de ejemplo sobre el NASDAQ para simulación ---
SIMULATED_NASDAQ_CHUNKS = [
    "El **NASDAQ Composite** es un índice bursátil que incluye a casi todas las acciones ordinarias que cotizan en el mercado de valores NASDAQ.",
    "Fundado en 1971, el NASDAQ fue el primer mercado de valores electrónico del mundo, revolucionando la forma de operar con acciones.",
    "Las empresas tecnológicas, como Apple, Microsoft, Amazon y Google (Alphabet), dominan el NASDAQ 100.",
    "El **NASDAQ 100** es un índice que agrupa a las 100 mayores empresas no financieras, tanto estadounidenses como internacionales, que cotizan en el NASDAQ.",
    "A diferencia del S&P 500 o el Dow Jones, el NASDAQ Composite es conocido por su fuerte exposición a las empresas de alto crecimiento y tecnología.",
    "La **volatilidad** es una característica común en el NASDAQ debido a la naturaleza de las empresas que lo componen, a menudo startups y compañías en crecimiento.",
    "El horario de negociación principal del NASDAQ es de 9:30 a.m. a 4:00 p.m. ET, de lunes a viernes.",
    "Un gran número de ofertas públicas iniciales (IPO) de empresas tecnológicas se realizan en el NASDAQ, consolidándolo como un mercado clave para la innovación.",
    "El rendimiento del NASDAQ a menudo se considera un barómetro de la salud del sector tecnológico global.",
    "Los inversores a menudo monitorean el NASDAQ para identificar tendencias en la economía digital y la innovación tecnológica."
]

# Pre-calcular los embeddings para los chunks simulados
# Esto se hace una vez al inicio del script para eficiencia
print("Calculando embeddings para los chunks simulados...")
SIMULATED_CHUNK_EMBEDDINGS = embedding_function.embed_documents(SIMULATED_NASDAQ_CHUNKS)
print("Embeddings simulados calculados.")


def _simulate_semantic_search(query: str, top_k: int) -> list[str]:
    """
    Simula una búsqueda semántica entre los chunks predefinidos.
    """
    query_embedding = embedding_function.embed_query(query)
    
    # Calcular similitud del coseno entre la query y todos los chunks simulados
    similarities = cosine_similarity(
        np.array(query_embedding).reshape(1, -1),
        np.array(SIMULATED_CHUNK_EMBEDDINGS)
    )[0]

    # Ordenar los chunks por similitud en orden descendente
    # y obtener los índices de los top_k
    top_k_indices = np.argsort(similarities)[::-1][:top_k]

    # Devolver los chunks correspondientes a los top_k índices
    simulated_results = [SIMULATED_NASDAQ_CHUNKS[i] for i in top_k_indices]
    
    print(f"Simulación: Query '{query}' -> Chunks seleccionados por similitud.")
    return simulated_results


def retrieve_chunks(query: str, top_k: int = 3):
    """
    Recupera los chunks más relevantes de ChromaDB.
    Si la colección está vacía o no existe, realiza una simulación de búsqueda semántica
    sobre chunks predefinidos del NASDAQ.
    """
    # Si no existe la carpeta de Chroma, devolvemos chunks simulados
    if not os.path.exists(CHROMA_DB_PATH):
        print("⚠️ ChromaDB no inicializado. Realizando simulación.")
        return _simulate_semantic_search(query, top_k)

    # Conectar al vector store
    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_function,
        persist_directory=CHROMA_DB_PATH
    )

    try:
        # Intentar una búsqueda real si la base de datos existe
        # Antes de la búsqueda, verifica si la colección no está vacía
        # Esto puede requerir una forma de verificar la cantidad de elementos en Chroma
        # Langchain Chroma no tiene un método directo para verificar si una colección está vacía
        # sin hacer una búsqueda. La forma más segura es intentar la búsqueda y manejar la excepción
        # o verificar si results es vacío.

        results = vectorstore.similarity_search(query, k=top_k)

        if not results:
            print("⚠️ Búsqueda real no encontró resultados. Devolviendo chunks simulados.")
            return _simulate_semantic_search(query, top_k)

        return [doc.page_content for doc in results]

    except Exception as e:
        print(f"⚠️ Error consultando ChromaDB: {e}. Realizando simulación.")
        return _simulate_semantic_search(query, top_k)
