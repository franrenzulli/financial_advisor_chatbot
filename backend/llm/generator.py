# Prompting and OpenAI calls

import os
from openai import OpenAI
from dotenv import load_dotenv
import json # Necesario para manejar posibles serializaciones/deserializaciones si se envían objetos complejos

# Carga las variables de entorno desde el archivo .env
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Nueva función para adaptar el historial de Streamlit al formato de OpenAI
def _format_history_for_openai(chat_history: list[dict]) -> list[dict]:
    """
    Adapta el historial de conversación de Streamlit (o similar)
    al formato de mensajes que espera la API de OpenAI.
    """
    formatted_messages = []
    for message in chat_history:
        # Aquí asumimos que los mensajes ya tienen 'role' y 'content'
        # como 'user' o 'assistant'. Si tu Streamlit los guarda diferente, ajusta.
        formatted_messages.append({"role": message["role"], "content": message["content"]})
    return formatted_messages


def generate_answer(question: str, chunks: list[str], chat_history: list[dict] = None) -> str:
    """
    Genera una respuesta utilizando la API de OpenAI, basándose en la pregunta
    original, los chunks de contexto recuperados y el historial de conversación.
    """
    if chat_history is None:
        chat_history = []

    # 1. Preparar el historial para el LLM
    # No queremos repetir el mensaje actual del usuario en el historial si ya está en 'question'
    # Así que el historial incluirá turnos pasados del usuario y el asistente.
    formatted_chat_history = _format_history_for_openai(chat_history)

    # 2. Construir el prompt con contexto y historial
    context_str = "\n".join(
        [f"Chunk {i+1}: {chunk}" for i, chunk in enumerate(chunks)]
    )

    if not chunks:
        context_str = "No se ha encontrado información relevante en la base de datos de conocimiento."

    # Definir los mensajes para el modelo de chat (formato de API de OpenAI)
    # El rol de 'system' define el comportamiento general.
    # El historial de chat pasado se inserta ANTES de la pregunta actual del usuario y el contexto.
    messages = [
        {
            "role": "system",
            "content": "Eres un asistente útil y conversacional. Responde a la pregunta del usuario basándote estrictamente en los 'Chunks de contexto' y el historial de conversación. Si la respuesta no se puede encontrar en los chunks, indica claramente que no tienes información suficiente para responder esa pregunta específica basándote en las fuentes proporcionadas. Mantén la coherencia con la conversación anterior.",
        },
    ]

    # Añadir los mensajes pasados del historial
    messages.extend(formatted_chat_history)

    # Añadir la pregunta actual del usuario y el contexto
    messages.append(
        {
            "role": "user",
            "content": f"""
            **Pregunta actual:** {question}

            **Chunks de contexto relevantes:**
            {context_str}

            Por favor, responde a la pregunta actual de manera concisa, usando el historial y el contexto proporcionado.
            """,
        }
    )

    try:
        # Llamada a la API de OpenAI
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Puedes cambiar a "gpt-4" si lo tienes disponible
            messages=messages,
            temperature=0.7,        # Un valor entre 0 y 1. Mayor valor = más creativo, menor = más conciso.
            max_tokens=500,         # Límite de tokens para la respuesta del LLM
        )

        llm_response = chat_completion.choices[0].message.content
        return llm_response

    except Exception as e:
        print(f"Error al llamar a la API de OpenAI en generate_answer: {e}")
        return f"Lo siento, hubo un problema al generar la respuesta con la IA: {e}"
