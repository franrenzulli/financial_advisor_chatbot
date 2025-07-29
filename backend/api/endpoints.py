from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

# ... (tus otras importaciones no cambian) ...
from rag.retriever import retrieve_chunks
from llm.router import route_question
from llm.evaluator import are_chunks_sufficient
from llm.generator import generate_rag_answer, generate_fallback_answer

router = APIRouter()

class QuestionRequest(BaseModel):
    question: str
    chat_history: Optional[List[Dict[str, str]]] = None

@router.post("/ask")
async def ask(request: QuestionRequest):
    try:
        # --- INICIO DEL NUEVO CÓDIGO ---
        
        # Si la pregunta es muy corta (una o dos palabras), la transformamos en una pregunta real
        # para los modelos de lenguaje.
        question_for_llms = request.question
        if len(request.question.split()) <= 2:
            question_for_llms = f"Explica en detalle qué es y cuáles son las características de: '{request.question}'"
            print(f"Pregunta original transformada a: '{question_for_llms}'")

        # --- FIN DEL NUEVO CÓDIGO ---
        
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
        print(f"ERROR CRÍTICO EN EL ENDPOINT: {e}")
        raise HTTPException(status_code=500, detail=f"Error inesperado en el backend: {e}")
