from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

# Configuración
CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "documents"

# Inicializamos embeddings (mismo modelo que usaste para indexar)
embedding_function = SentenceTransformerEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def retrieve_chunks(query: str, top_k: int = 3):
    """
    Usa LangChain + Chroma para recuperar los chunks más relevantes.
    Devuelve solo texto plano de cada chunk.
    """
    # Conectar al vector store persistido
    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_function,
        persist_directory=CHROMA_DB_PATH
    )

    # Recuperar documentos más similares
    results = vectorstore.similarity_search(query, k=top_k)

    # Extraer solo el contenido de los chunks
    return [doc.page_content for doc in results]
