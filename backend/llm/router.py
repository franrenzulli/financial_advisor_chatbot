# backend/llm/router.py

from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def route_question(question: str) -> str:
    """
    Clasifica la pregunta del usuario para decidir la ruta a seguir.
    """
    system_prompt = """
    Tu tarea es clasificar la pregunta del usuario en una de dos categorías:
    1. 'FINANCE_RAG': Si la pregunta trata sobre finanzas, inversiones, mercados, economía, o cualquier tema que requiera conocimiento especializado de una base de datos.
    2. 'GENERAL_CHAT': Si la pregunta es un saludo, una despedida, o una pregunta de conocimiento general que no es de finanzas (ej: '¿cómo estás?', '¿quién eres?', '¿qué tiempo hace?').
    
    Responde únicamente con la etiqueta de la categoría, y nada más.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Usamos un modelo rápido y económico para clasificación
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0,
            max_tokens=10 
        )
        route = response.choices[0].message.content.strip()
        
        # Asegurarnos de que la respuesta sea una de las dos categorías
        if route in ["FINANCE_RAG", "GENERAL_CHAT"]:
            return route
        return "GENERAL_CHAT" # Por defecto, si el modelo responde algo inesperado

    except Exception as e:
        print(f"Error en el enrutador: {e}")
        return "GENERAL_CHAT" # En caso de error, tratar como chat general