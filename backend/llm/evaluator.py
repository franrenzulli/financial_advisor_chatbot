import os
import google.generativeai as genai

# 1. Se configura el cliente de Gemini usando la variable de entorno
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    # 2. Se elige un modelo rápido y económico para la tarea de evaluación
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"Error al configurar la API de Gemini: {e}")
    model = None

def are_chunks_sufficient(question: str, chunks: list) -> bool:
    """
    Evalúa si los chunks de texto recuperados contienen la información 
    necesaria para responder a la pregunta del usuario usando Gemini.

    Args:
        question: La pregunta original del usuario.
        chunks: La lista de fragmentos de texto recuperados (objetos Document de LangChain).

    Returns:
        True si los chunks son suficientes, False en caso contrario.
    """
    # Si el modelo no se pudo inicializar, no podemos evaluar.
    if not model:
        print("El modelo de Gemini no está disponible. Asumiendo que los chunks no son suficientes.")
        return False
        
    # Si no se recuperó ningún chunk, no son suficientes.
    if not chunks:
        return False

    # Unimos el contenido de los chunks en un solo bloque de texto.
    # Asumimos que 'chunks' es una lista de objetos Document con un atributo 'page_content'.
    context_str = "\n---\n".join([chunk.page_content for chunk in chunks])
    
    # 3. Se crea un prompt único para Gemini.
    prompt = f"""
    Tu única tarea es evaluar si el 'Contexto' proporcionado contiene información suficiente y relevante para responder de manera directa a la 'Pregunta'.
    Responde únicamente con la palabra 'sí' o 'no', sin ninguna otra explicación.

    Contexto:
    ---
    {context_str}
    ---
    Pregunta: {question}

    ¿Suficiente? (sí/no):
    """
    
    try:
        # 4. Se llama a la API de Gemini en lugar de a la de OpenAI.
        response = model.generate_content(prompt)
        
        # Limpiamos la respuesta para asegurarnos de que solo leemos sí o no.
        decision = response.text.strip().lower()
        
        # Devolvemos True si la respuesta contiene "sí".
        return "sí" in decision

    except Exception as e:
        print(f"Error en el evaluador de suficiencia con Gemini: {e}")
        # En caso de error, es más seguro asumir que los chunks no son suficientes.
        return False