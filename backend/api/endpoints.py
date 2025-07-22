# FASTApi routes

from fastapi import APIRouter
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer 
import os 

router = APIRouter()

# --- Cargar el modelo de sentence-transformers una sola vez al inicio ---

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

embedding_model = None # Inicializar a None por si falla la carga

try:
    print(f"DEBUG BACKEND: Intentando cargar el modelo de embedding: '{EMBEDDING_MODEL_NAME}'...")
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    print(f"DEBUG BACKEND: Modelo de embedding '{EMBEDDING_MODEL_NAME}' cargado exitosamente.")
except Exception as e:
    print(f"ERROR BACKEND: Error al cargar el modelo de embedding: {e}")

# pydantic model for user request
class QuestionRequest(BaseModel):
    question: str

@router.post("/ask")
async def ask_question(request: QuestionRequest):
    print(f"DEBUG BACKEND: Pregunta recibida desde el frontend: '{request.question}'")

    # Verificar si el modelo de embedding se cargó correctamente al inicio
    if embedding_model is None:
        print("ERROR BACKEND: El modelo de embedding no está disponible. Respondiendo con error.")
        return {"answer": "Error interno del servidor: El modelo de procesamiento de lenguaje no está cargado. Intente más tarde o contacte al administrador."}

    try:
        # Paso 3: Convertir la pregunta en un vector numérico (embedding)
        question_embedding = embedding_model.encode(request.question)
        print(f"DEBUG BACKEND: Pregunta convertida a embedding. Forma del vector: {question_embedding.shape}")

        # --- AQUÍ VA EL SIGUIENTE PASO DE TU ARQUITECTURA (PASO 5: Búsqueda en ChromaDB) ---
        # Usar 'question_embedding' para buscar chunks similares en tu ChromaDB.
        # Esto implicaría conectar con ChromaDB y realizar una consulta de similitud.
        # Ejemplo (requeriría más código y configuración de ChromaDB aquí):
        # from langchain_chroma import Chroma
        # import chromadb
        # # Asume que CHROMA_HOST y CHROMA_PORT están disponibles aquí, o los obtienes de env vars
        # chroma_client = chromadb.HttpClient(host=os.getenv("CHROMADB_HOST", "vector_db"), port=int(os.getenv("CHROMADB_PORT", "8000")))
        # vector_store = Chroma(
        #     client=chroma_client,
        #     collection_name="financial_documents", # Usar el mismo nombre de la colección que en ingest.py
        #     embedding_function=embedding_model # Usar el mismo modelo de embedding
        # )
        # similar_docs = vector_store.similarity_search_by_vector(question_embedding, k=5)
        # print(f"DEBUG BACKEND: Documentos similares encontrados: {len(similar_docs)}")
        # # Luego, construirías el prompt para el LLM con estos documentos (Paso 6)
        # # Y llamarías a la API de OpenAI (Paso 7)
        # # assistant_response_content = your_llm_call_function(prompt_for_llm)

        # Por ahora, devolvemos una confirmación detallada para que veas que funciona:
        return {
            "answer": f"Backend dice: Recibí tu pregunta '{request.question}'. "
                      f"La convertí a un embedding de forma {question_embedding.shape}! "
                      f"¡Ahora haríamos la búsqueda en ChromaDB y generaríamos la respuesta."
        }

    except Exception as e:
        print(f"ERROR BACKEND: Error al generar el embedding de la pregunta o durante el procesamiento: {e}")
        return {"answer": f"Ocurrió un error interno al procesar tu pregunta. Por favor, intenta de nuevo. Detalles: {e}"}
