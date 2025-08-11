# /app/llm/generator.py

import os
import google.generativeai as genai
from typing import List, Dict, Optional

try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    generation_config = {"response_mime_type": "text/plain"}
    rag_model = genai.GenerativeModel('gemini-1.5-pro-latest')
    fallback_model = genai.GenerativeModel('gemini-1.5-flash-latest', generation_config=generation_config)
except Exception as e:
    print(f"Error al configurar la API de Gemini: {e}")
    rag_model = None
    fallback_model = None

def _format_chat_history_for_prompt(chat_history: Optional[List[Dict[str, str]]]) -> str:
    if not chat_history:
        return "No hay historial de conversación previo."
    
    history_str = ""
    for msg in chat_history:
        role = "Usuario" if msg.get("role") == "user" else "Asistente"
        history_str += f"{role}: {msg.get('content')}\n"
    return history_str

def generate_rag_answer(question: str, chunks: list, chat_history: Optional[List[Dict[str, str]]]) -> str:
    if not rag_model:
        return "Error: El modelo de Gemini para RAG no está disponible."

    context_str = "\n".join([chunk.page_content for chunk in chunks])
    formatted_history = _format_chat_history_for_prompt(chat_history)

    prompt = f"""
    Eres un asistente financiero experto. Tu tarea es responder la 'Pregunta actual' del usuario basándote ESTRICTA y ÚNICAMENTE en los 'Chunks de contexto' proporcionados.
    Mantén la coherencia con el 'Historial de conversación'.
    Si la respuesta no se encuentra en el contexto, indícalo claramente. No uses conocimiento externo.

    FORMATO (OBLIGATORIO):
    - Responde en **Markdown** limpio.
    - Usa títulos (`##`), listas con viñetas y numeradas cuando ayude.
    - Pon en **negrita** conceptos clave.
    - Mantén párrafos con líneas en blanco entre secciones.

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
        response = rag_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error en generate_rag_answer con Gemini: {e}")
        return "Hubo un error al procesar la respuesta con los documentos."

def generate_fallback_answer(question: str, chat_history: Optional[List[Dict[str, str]]]) -> str:
    if not fallback_model:
        return "Error: El modelo de Gemini para fallback no está disponible."
        
    formatted_history = _format_chat_history_for_prompt(chat_history)

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
        response = fallback_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error en generate_fallback_answer con Gemini: {e}")
        return "Hubo un error al generar una respuesta."

def handle_conversational_and_calculations(question: str, sub_route: str, chat_history: Optional[List[Dict[str, str]]]) -> str:
    if not fallback_model:
        return "Error: El modelo de Gemini para la generación conversacional no está disponible."

    if sub_route == "FUERA_DE_TEMA":
        return "Lo siento, mi propósito es asistirte con preguntas sobre finanzas e inversiones. Por favor, hazme una pregunta sobre esos temas."
    
    if sub_route == "INTERES_COMPUESTO":
        # Aquí iría la lógica para extraer datos y hacer el cálculo
        # Por ahora, solo devolvemos un mensaje mock.
        return "La funcionalidad de calculadora de interés compuesto está en desarrollo."

    # Lógica para CONSEJO_GENERAL, CALCULO_GENERAL y otros que usan LLM
    formatted_history = _format_chat_history_for_prompt(chat_history)
    
    prompt = f"""
    Eres un asistente conversacional experto en finanzas.
    Tu tarea es responder a la 'Pregunta actual' del usuario.
    Si la pregunta es un saludo o una pregunta abierta, responde de manera amigable y general.
    Si la pregunta es un cálculo simple, dame la respuesta directamente.
    Si te piden consejo financiero directo, por favor, sé cauteloso y dile que lo mejor es consultar a un asesor profesional.
    No des información sobre cotizaciones de bolsa actuales, ya que no tienes acceso a datos en tiempo real.
    
    FORMATO:
    - Responde en Markdown limpio.

    ---
    HISTORIAL DE CONVERSACIÓN:
    {formatted_history}
    ---
    PREGUNTA ACTUAL: {question}
    ---
    RESPUESTA:
    """
    
    try:
        response = fallback_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error en handle_conversational_and_calculations con Gemini: {e}")
        return "Hubo un error al generar una respuesta."
    
def generate_news_summary(news_articles: list, entity: str) -> str:
    if not rag_model:
        return "Error: El modelo de Gemini no está disponible para generar resúmenes."
        
    if not news_articles:
        return f"No se encontraron noticias recientes sobre {entity}."

    articles_text = "\n\n".join([f"Título: {a['title']}\nDescripción: {a['description']}\nFuente: {a['source']['name']}" for a in news_articles])

    prompt = f"""
    Eres un asistente financiero. Lee los siguientes artículos de noticias y crea un resumen breve y neutral sobre el tema '{entity}'.
    Responde solo con el resumen, sin añadir introducciones ni conclusiones.
    Si los artículos no contienen información relevante, di que no se encontraron noticias.

    ---
    Artículos:
    {articles_text}
    ---
    Resumen para '{entity}':
    """

    try:
        response = rag_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error al generar el resumen de noticias con Gemini: {e}")
        return "Hubo un error al generar el resumen de noticias."