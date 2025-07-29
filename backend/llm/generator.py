# backend/llm/generator.py

import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict, Optional

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def _format_history_for_openai(chat_history: Optional[List[Dict[str, str]]]) -> list:
    if not chat_history:
        return []
    # Esta función ya es correcta, la mantenemos igual.
    return [{"role": msg["role"], "content": msg["content"]} for msg in chat_history]

def generate_rag_answer(question: str, chunks: list[str], chat_history: Optional[List[Dict[str, str]]]) -> str:
    """
    Genera una respuesta BASADA EN DOCUMENTOS. Es llamado cuando los chunks son suficientes.
    """
    formatted_chat_history = _format_history_for_openai(chat_history)
    context_str = "\n".join(chunks)

    system_prompt = """
    Eres un asistente financiero experto. Tu tarea es responder la 'Pregunta actual' del usuario basándote ESTRICTA y ÚNICAMENTE en los 'Chunks de contexto' proporcionados.
    Mantén la coherencia con el 'Historial de conversación'.
    Si la respuesta no se encuentra en el contexto, indícalo claramente. No uses conocimiento externo.
    """

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(formatted_chat_history)
    messages.append({
        "role": "user",
        "content": f"""
        Historial de conversación: ... (ya incluido)

        Chunks de contexto:
        ---
        {context_str}
        ---
        Pregunta actual: {question}
        """
    })

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.2, # Más bajo para respuestas basadas en hechos
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error en generate_rag_answer: {e}")
        return "Hubo un error al procesar la respuesta con los documentos."

def generate_fallback_answer(question: str, chat_history: Optional[List[Dict[str, str]]]) -> str:
    """
    Genera una respuesta de CONOCIMIENTO GENERAL o cuando los documentos no son suficientes.
    Incluye una barrera de seguridad (guardrail) fuerte.
    """
    formatted_chat_history = _format_history_for_openai(chat_history)

    system_prompt = """
    Eres un asistente conversacional. Responde a la pregunta del usuario de manera útil.
    IMPORTANTE: Eres un experto en finanzas. Si te preguntan algo sobre ese tema y no estás 100% seguro de la respuesta o si requiere datos muy específicos y recientes, DEBES NEGARTE a responder. 
    En su lugar, di: 'Sobre ese tema financiero específico, no tengo la información suficiente para dar una respuesta precisa. Te recomiendo consultar a un asesor.'
    Para preguntas generales (saludos, etc.), responde con normalidad.
    """
    
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(formatted_chat_history)
    messages.append({"role": "user", "content": question})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Puede ser un modelo más rápido/económico
            messages=messages,
            temperature=0.7, # Más creativo para conversación
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error en generate_fallback_answer: {e}")
        return "Hubo un error al generar una respuesta."