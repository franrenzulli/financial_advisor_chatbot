import os
import google.generativeai as genai
from typing import List, Dict, Optional

# 1. Se configura el cliente de Gemini y se inicializan los modelos
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    # Un modelo potente para RAG y uno más rápido para fallback
    generation_config = {"response_mime_type": "text/plain"}
    rag_model = genai.GenerativeModel('gemini-1.5-pro-latest')
    fallback_model = genai.GenerativeModel('gemini-1.5-flash-latest', generation_config=generation_config)
except Exception as e:
    print(f"Error al configurar la API de Gemini: {e}")
    rag_model = None
    fallback_model = None

def _format_chat_history_for_prompt(chat_history: Optional[List[Dict[str, str]]]) -> str:
    """Formatea el historial de chat en un string para incluirlo en el prompt."""
    if not chat_history:
        return "No hay historial de conversación previo."
    
    history_str = ""
    for msg in chat_history:
        # Asume que los roles son 'user' y 'bot'
        role = "Usuario" if msg.get("role") == "user" else "Asistente"
        history_str += f"{role}: {msg.get('content')}\n"
    return history_str

def generate_rag_answer(question: str, chunks: list, chat_history: Optional[List[Dict[str, str]]]) -> str:
    """
    Genera una respuesta BASADA EN DOCUMENTOS usando Gemini.
    """
    if not rag_model:
        return "Error: El modelo de Gemini para RAG no está disponible."

    # Se prepara el contexto y el historial para un único prompt
    context_str = "\n".join([chunk.page_content for chunk in chunks])
    formatted_history = _format_chat_history_for_prompt(chat_history)

    # 2. Se crea un prompt único que incluye todas las instrucciones.
    prompt = f"""
    Eres un asistente financiero experto. Tu tarea es responder la 'Pregunta actual' del usuario basándote ESTRICTA y ÚNICAMENTE en los 'Chunks de contexto' proporcionados.
    Mantén la coherencia con el 'Historial de conversación'.
    Si la respuesta no se encuentra en el contexto, indícalo claramente. No uses conocimiento externo.

    FORMATO (OBLIGATORIO):
    - Responde en **Markdown** limpio.
    - Usa títulos (`##`), listas con viñetas y numeradas cuando ayude.
    - Pon en **negrita** conceptos clave.
    - Mantén párrafos con líneas en blanco entre secciones.
    - Si hay pasos o recomendaciones, usa listas.
    - Si incluyes código/consultas, usa bloque con triple backticks.

    ---
    HISTORIAL DE CONVERSACIÓN:
    {formatted_history}
    ---
    CHUNKS DE CONTEXTO:
    {context_str}
    ---
    PREGUNTA ACTUAL: {question}
    ---
    RESPUESTA PRECISA Y BASADA EN EL CONTEXTO:
    """

    try:
        # 3. Se llama a la API de Gemini con el prompt.
        response = rag_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error en generate_rag_answer con Gemini: {e}")
        return "Hubo un error al procesar la respuesta con los documentos."

def generate_fallback_answer(question: str, chat_history: Optional[List[Dict[str, str]]]) -> str:
    """
    Genera una respuesta de CONOCIMIENTO GENERAL o cuando los documentos no son suficientes, usando Gemini.
    """
    if not fallback_model:
        return "Error: El modelo de Gemini para fallback no está disponible."
        
    formatted_history = _format_chat_history_for_prompt(chat_history)

    # 4. Se crea un prompt único con las instrucciones de seguridad (guardrail).
    prompt = f"""
    Eres un asistente conversacional experto en finanzas.
    IMPORTANTE: Si te preguntan algo sobre finanzas que requiera datos muy específicos, recientes o consejo financiero y no estás 100% seguro de la respuesta, DEBES NEGARTE a responder. En su lugar, di: 'Sobre ese tema financiero específico, no tengo la información suficiente para dar una respuesta precisa. Te recomiendo consultar a un asesor.'
    Para preguntas generales (saludos, quién eres, etc.), responde con normalidad.

    FORMATO (OBLIGATORIO):
    - Responde en **Markdown** limpio.
    - Usa `##` para títulos, listas y **negritas** para resaltar puntos clave.
    - Párrafos separados por líneas en blanco.

    ---
    HISTORIAL DE CONVERSACIÓN:
    {formatted_history}
    ---
    PREGUNTA ACTUAL: {question}
    ---
    RESPUESTA:
    """

    try:
        # 5. Se llama a la API de Gemini con el modelo más rápido.
        response = fallback_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error en generate_fallback_answer con Gemini: {e}")
        return "Hubo un error al generar una respuesta."