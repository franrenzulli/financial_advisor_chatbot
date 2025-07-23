# FastAPI Backend (e.g., main.py o wherever your router is defined)

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Optional # Importar para tipos de historial

from rag.retriever import retrieve_chunks
from llm.generator import generate_answer

router = APIRouter()

class QuestionRequest(BaseModel):
    question: str
    # Nuevo campo para el historial de conversación
    # Será una lista de diccionarios, donde cada dict tiene 'role' y 'content'
    chat_history: Optional[List[Dict[str, str]]] = None # Puede ser opcional/vacío

@router.post("/ask")
async def ask_question(request: QuestionRequest):
    try:
        # Obtiene los chunks
        retrieved_chunks = retrieve_chunks(request.question, top_k=3)

        # Pasa la pregunta, los chunks Y EL HISTORIAL al generador
        bot_answer = generate_answer(
            question=request.question,
            chunks=retrieved_chunks,
            chat_history=request.chat_history # Pasamos el historial recibido
        )

        return {
            "question": request.question,
            "answer": bot_answer,
            "retrieved_chunks": retrieved_chunks
        }

    except Exception as e:
        print(f"ERROR BACKEND: {e}")
        return {
            "question": request.question,
            "answer": f"Error inesperado en el backend: {e}",
            "retrieved_chunks": []
        }
