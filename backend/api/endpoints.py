# /app/api/endpoints.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
import json

from rag.retriever import retrieve_chunks
from llm.router import route_question
from llm.evaluator import are_chunks_sufficient
from llm.generator import generate_rag_answer, generate_fallback_answer, handle_conversational_and_calculations
from external_apis.financial_data import get_stock_quote, get_exchange_rate
from llm.extractor import extract_financial_info
from external_apis.news_api import get_financial_news # ¡Nueva importación!
from llm.generator import generate_news_summary # ¡Nueva importación!


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

# --- ENDPOINT /ask (CON LÓGICA COMPLETA) ---
@router.post("/ask")
async def ask(request: QuestionRequest):
    try:
        route, sub_route = route_question(request.question)
        print(f"Ruta principal: {route}, Sub-ruta: {sub_route}")

        bot_answer = ""
        retrieved_chunks_for_response = []

        if route == "CONVERSACIONAL":
            bot_answer = handle_conversational_and_calculations(request.question, sub_route, request.chat_history)
        
        elif route == "DATOS_ESPECIFICOS":
            if sub_route == "RAG_NASDAQ":
                chunks = retrieve_chunks(request.question, top_k=3)
                retrieved_chunks_for_response = chunks

                if are_chunks_sufficient(request.question, chunks):
                    print("Los chunks son suficientes. Usando RAG.")
                    bot_answer = generate_rag_answer(request.question, chunks, request.chat_history)
                else:
                    print("Los chunks NO son suficientes. Usando Fallback.")
                    bot_answer = generate_fallback_answer(request.question, request.chat_history)
            
            elif sub_route == "API_COTIZACION":
                # Lógica para extraer el símbolo de la acción de la pregunta
                # Por simplicidad, usaremos un mock. En un caso real, esto sería un LLM.
                stock_symbol, _, _ = extract_financial_info(request.question, sub_route)
                if stock_symbol:
                    bot_answer = get_stock_quote(stock_symbol)
                else:
                    bot_answer = "No pude identificar el símbolo de la acción en tu pregunta. Por favor, sé más específico."

            elif sub_route == "NOTICIAS": # ¡Nueva ruta!
                entity, _, _ = extract_financial_info(request.question, sub_route)
                if entity:
                    news_articles = get_financial_news(entity)
                    bot_answer = generate_news_summary(news_articles, entity)
                else:
                    bot_answer = "No pude identificar la empresa o el tema para buscar noticias. Por favor, sé más específico."

        elif route == "CALCULOS_Y_PROYECCIONES":
            if sub_route == "TIPO_DE_CAMBIO":
                from_currency, to_currency, amount_str = extract_financial_info(request.question, sub_route)
                try:
                    if from_currency and to_currency and amount_str:
                        amount = float(amount_str)
                        bot_answer = get_exchange_rate(amount, from_currency, to_currency)
                    else:
                        bot_answer = "No pude entender la conversión de monedas que solicitas. Por favor, especifica una cantidad, la moneda de origen y la de destino (ej: '100 USD a EUR')."
                except ValueError:
                    bot_answer = "Por favor, ingresa una cantidad numérica válida para la conversión."

        return {
            "question": request.question,
            "answer": (bot_answer or "").strip(),
            "retrieved_chunks": serialize_chunks(retrieved_chunks_for_response),
        }

    except Exception as e:
        print(f"ERROR CRÍTICO EN EL ENDPOINT /ask: {e}")
        raise HTTPException(status_code=500, detail=f"Error inesperado en el backend: {e}")

# --- ENDPOINT /feedback se mantiene igual ---
@router.post("/feedback")
async def handle_feedback(payload: FeedbackPayload, db: Session = Depends(get_db)):
    try:
        chunks_str = json.dumps(payload.retrieved_chunks or [])
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
    
def serialize_chunks(chunks):
    def _one(c):
        return {
            "page_content": getattr(c, "page_content", None),
            "metadata": getattr(c, "metadata", None),
        }
    return [_one(c) for c in chunks or []]