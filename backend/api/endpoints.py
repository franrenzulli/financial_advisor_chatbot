# /app/api/endpoints.py

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
import json
import sqlite3
import os
import time
from datetime import datetime

# --- TUS IMPORTS ACTUALES ---
from rag.retriever import retrieve_chunks
from llm.router import route_question
from llm.evaluator import are_chunks_sufficient
from llm.generator import generate_rag_answer, generate_fallback_answer, handle_conversational_and_calculations
from external_apis.financial_data import get_stock_quote, get_exchange_rate
from llm.extractor import extract_financial_info
from external_apis.news_api import get_financial_news
from llm.generator import generate_news_summary
from feedback.database import get_db, FeedbackLog

# --- LÓGICA PARA CREAR LA BASE DE DATOS DE CHATS AL ARRANCAR ---
try:
    # 1. Definir la ruta a la carpeta y al archivo de la base de datos
    api_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.dirname(api_dir)
    db_folder_path = os.path.join(app_dir, 'chats')
    db_file_path = os.path.join(db_folder_path, 'chats.sqlite')

    # 2. Crear la carpeta si no existe
    os.makedirs(db_folder_path, exist_ok=True)

    # 3. Función para obtener una conexión a la DB de chats
    def get_chats_db_conn():
        conn = sqlite3.connect(db_file_path)
        conn.row_factory = sqlite3.Row 
        return conn

    # 4. Conectar y crear tablas si no existen
    conn = get_chats_db_conn()
    cursor = conn.cursor()
    print("✅ Conectado a la base de datos SQLite para chats.")
    print(f"   Ruta: {db_file_path}")

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY, email TEXT UNIQUE, name TEXT
    )''')
    print("   - Tabla 'users' lista.")

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chats (
      id TEXT PRIMARY KEY, user_id TEXT NOT NULL, title TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    print("   - Tabla 'chats' lista.")

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id TEXT NOT NULL,
      role TEXT NOT NULL, content TEXT NOT NULL,
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (chat_id) REFERENCES chats (id)
    )''')
    print("   - Tabla 'messages' lista.")

    conn.commit()
    conn.close()
    print("✅ Base de datos de chats verificada y lista.")

except sqlite3.Error as e:
    print(f"❌ Error en la base de datos de chats: {e}")

print("-" * 50)
# --- FIN DE LA LÓGICA DE INICIALIZACIÓN ---


router = APIRouter()

# --- MODELOS Pydantic ---
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

class ChatCreateRequest(BaseModel):
    userId: str
    email: Optional[str] = None
    name: Optional[str] = None
    title: str

# --- ENDPOINTS ---

# ✅ NUEVO ENDPOINT PARA OBTENER LOS CHATS DE UN USUARIO
@router.get("/chats/{user_id}")
def get_user_chats(user_id: str):
    conn = None
    try:
        conn = get_chats_db_conn()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, title, created_at FROM chats WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        
        chats_from_db = cursor.fetchall()
        
        # Convertimos las filas de la DB a una lista de diccionarios
        # y agregamos el array de mensajes vacío que el frontend necesita
        chats = [
            {
                "id": row["id"],
                "title": row["title"],
                "created_at": row["created_at"],
                "messages": [] 
            } 
            for row in chats_from_db
        ]
        
        return chats

    except sqlite3.Error as e:
        print(f"ERROR al obtener chats: {e}")
        raise HTTPException(status_code=500, detail="Error de base de datos al obtener los chats")
    finally:
        if conn:
            conn.close()

@router.post("/chats", status_code=status.HTTP_201_CREATED)
def create_chat(chat_request: ChatCreateRequest):
    chat_id = str(int(time.time() * 1000))
    conn = None
    try:
        conn = get_chats_db_conn()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (id, email, name) VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET email=excluded.email, name=excluded.name",
            (chat_request.userId, chat_request.email, chat_request.name)
        )

        cursor.execute(
            "INSERT INTO chats (id, user_id, title) VALUES (?, ?, ?)",
            (chat_id, chat_request.userId, chat_request.title)
        )
        conn.commit()

        new_chat = {
            "id": chat_id,
            "user_id": chat_request.userId,
            "title": chat_request.title,
            "created_at": datetime.utcnow().isoformat(),
            "messages": [] # Se lo devolvemos al frontend para que no crashee
        }
        print(f"Chat creado: {new_chat}")
        return new_chat

    except sqlite3.Error as e:
        print(f"ERROR al crear chat: {e}")
        raise HTTPException(status_code=500, detail="Error de base de datos al crear el chat")
    finally:
        if conn:
            conn.close()

@router.delete("/chats/{chat_id}", status_code=status.HTTP_200_OK)
def delete_chat(chat_id: str):
    conn = None
    try:
        conn = get_chats_db_conn()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
        cursor.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
        conn.commit()

        if cursor.rowcount == 0:
             raise HTTPException(status_code=404, detail="Chat no encontrado")

        print(f"Chat borrado: {chat_id}")
        return {"message": "Chat y mensajes asociados borrados exitosamente"}

    except sqlite3.Error as e:
        print(f"ERROR al borrar chat: {e}")
        raise HTTPException(status_code=500, detail="Error de base de datos al borrar el chat")
    finally:
        if conn:
            conn.close()


# --- ENDPOINT /ask (TU LÓGICA ACTUAL) ---
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
                stock_symbol, _, _ = extract_financial_info(request.question, sub_route)
                if stock_symbol:
                    bot_answer = get_stock_quote(stock_symbol)
                else:
                    bot_answer = "No pude identificar el símbolo de la acción en tu pregunta. Por favor, sé más específico."

            elif sub_route == "NOTICIAS":
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

# --- ENDPOINT /feedback (TU LÓGICA ACTUAL) ---
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
