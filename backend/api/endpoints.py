# FastAPI Backend (e.g., main.py o wherever your router is defined)
from fastapi import APIRouter
from pydantic import BaseModel

from rag.retriever import retrieve_chunks # Solo necesitamos el retriever

router = APIRouter()

class QuestionRequest(BaseModel):
    question: str

@router.post("/ask")
async def ask_question(request: QuestionRequest):
    try:
        # Solo recuperamos los chunks, ¡sin generar nada!
        retrieved_chunks = retrieve_chunks(request.question, top_k=3)

        return {
            "question": request.question,         # La pregunta original del usuario
            "retrieved_chunks": retrieved_chunks # Los chunks que se recuperaron
        }

    except Exception as e:
        print(f"ERROR BACKEND: {e}")
        return {
            "question": request.question, # Aún devolvemos la pregunta en caso de error
            "retrieved_chunks": [],      # Y una lista vacía de chunks
            "error": f"Error inesperado en el backend: {e}" # Para depuración
        }
