# VERSIÓN FINAL Y COMPLETA

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
import json

# Tus importaciones de la lógica del chatbot
from rag.retriever import retrieve_chunks
from llm.router import route_question
from llm.evaluator import are_chunks_sufficient
from llm.generator import generate_rag_answer, generate_fallback_answer

# Importación actualizada para la nueva ubicación del archivo
from feedback.database import get_db, FeedbackLog

router = APIRouter()

# --- MODELOS ---
class QuestionRequest(BaseModel):
    question: str
    chat_history: Optional[List[Dict[str, str]]] = None

class FeedbackPayload(BaseModel):
    question: str
    answer: str
    chat_id: str
    feedback_type: str
    feedback_details: Optional[str] = None
    retrieved_chunks: Optional[list] = []

# --- ENDPOINT /ask (CON TU LÓGICA ORIGINAL COMPLETA) ---
@router.post("/ask")
async def ask(request: QuestionRequest):
    try:
        # Si la pregunta es muy corta (una o dos palabras), la transformamos en una pregunta real
        # para los modelos de lenguaje.
        question_for_llms = request.question
        if len(request.question.split()) <= 2:
            question_for_llms = f"Explica en detalle qué es y cuáles son las características de: '{request.question}'"
            print(f"Pregunta original transformada a: '{question_for_llms}'")

        # La búsqueda inicial en la BD se sigue haciendo con la pregunta original y corta
        route = route_question(request.question) 
        print(f"Ruta decidida: {route}")

        bot_answer = ""
        retrieved_chunks_for_response = []

        if route == "GENERAL_CHAT":
            bot_answer = generate_fallback_answer(question_for_llms, request.chat_history)

        elif route == "FINANCE_RAG":
            chunks = retrieve_chunks(request.question, top_k=3)
            retrieved_chunks_for_response = chunks

            # Usamos la pregunta transformada para el evaluador y el generador
            if are_chunks_sufficient(question_for_llms, chunks):
                print("Los chunks son suficientes. Usando RAG.")
                bot_answer = generate_rag_answer(question_for_llms, chunks, request.chat_history)
            else:
                print("Los chunks NO son suficientes. Usando Fallback.")
                bot_answer = generate_fallback_answer(question_for_llms, request.chat_history)

        return {
            "question": request.question,
            "answer": bot_answer,
            "retrieved_chunks": retrieved_chunks_for_response
        }

    except Exception as e:
        print(f"ERROR CRÍTICO EN EL ENDPOINT /ask: {e}")
        raise HTTPException(status_code=500, detail=f"Error inesperado en el backend: {e}")

# --- ENDPOINT /feedback (Versión final que guarda en la DB) ---
@router.post("/feedback")
async def handle_feedback(payload: FeedbackPayload, db: Session = Depends(get_db)):
    try:
        chunks_str = json.dumps(payload.retrieved_chunks)
        new_feedback = FeedbackLog(
            chat_id=payload.chat_id,
            question=payload.question,
            answer=payload.answer,
            feedback_type=payload.feedback_type,
            feedback_details=payload.feedback_details,
            retrieved_chunks=chunks_str
        )
        db.add(new_feedback)
        db.commit()
        db.refresh(new_feedback)
        return {"status": "success", "message": "Feedback guardado en la DB."}
    except Exception as e:
        db.rollback()
        print(f"ERROR CRÍTICO EN EL ENDPOINT /feedback: {e}")
        raise HTTPException(status_code=500, detail="No se pudo guardar el feedback en la DB.")