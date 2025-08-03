import os
import google.generativeai as genai

# 1. Se configura el cliente de Gemini y se elige un modelo rápido
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    print(f"Error al configurar la API de Gemini: {e}")
    model = None

def route_question(question: str) -> str:
    """
    Clasifica la pregunta del usuario para decidir la ruta a seguir usando Gemini.
    """
    if not model:
        print("El modelo de Gemini no está disponible. Usando ruta GENERAL_CHAT por defecto.")
        return "GENERAL_CHAT"

    # 2. Se crea un prompt único y claro para la tarea de clasificación.
    prompt = f"""
    Tu tarea es clasificar la siguiente pregunta del usuario en una de dos categorías:
    1. 'FINANCE_RAG': Si la pregunta trata sobre finanzas, inversiones, mercados, economía, o cualquier tema que requiera conocimiento especializado de una base de datos.
    2. 'GENERAL_CHAT': Si la pregunta es un saludo, una despedida, o una pregunta de conocimiento general que no es de finanzas (ej: '¿cómo estás?', '¿quién eres?', '¿qué tiempo hace?').
    
    Responde únicamente con la etiqueta de la categoría, y nada más.

    Pregunta a clasificar: "{question}"

    Categoría:
    """
    
    try:
        # 3. Se llama a la API de Gemini.
        response = model.generate_content(prompt)
        route = response.text.strip()
        
        # 4. Se valida que la respuesta sea una de las dos categorías esperadas.
        if route in ["FINANCE_RAG", "GENERAL_CHAT"]:
            return route
        
        # Si el modelo responde algo inesperado, se usa la ruta general por seguridad.
        print(f"Respuesta inesperada del router: '{route}'. Usando GENERAL_CHAT.")
        return "GENERAL_CHAT"

    except Exception as e:
        print(f"Error en el enrutador con Gemini: {e}")
        # En caso de error con la API, es más seguro tratarlo como chat general.
        return "GENERAL_CHAT"