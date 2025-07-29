from openai import OpenAI
import os

# Asegúrate de que las variables de entorno estén cargadas
# (normalmente se hace en el punto de entrada de la aplicación)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def are_chunks_sufficient(question: str, chunks: list[str]) -> bool:
    """
    Evalúa si los chunks de texto recuperados contienen la información 
    necesaria para responder a la pregunta del usuario.

    Args:
        question: La pregunta original del usuario.
        chunks: La lista de fragmentos de texto recuperados de la base de datos.

    Returns:
        True si los chunks son suficientes, False en caso contrario.
    """
    # Si no se recuperó ningún chunk, no son suficientes.
    if not chunks:
        return False

    # Unimos los chunks en un solo bloque de texto para el contexto.
    context_str = "\n---\n".join(chunks)
    
    system_prompt = """
    Tu única tarea es evaluar si el 'Contexto' proporcionado contiene información suficiente y relevante para responder de manera directa a la 'Pregunta'.
    Responde únicamente con la palabra 'sí' o 'no', sin ninguna otra explicación.
    """
    
    user_prompt = f"""
    Contexto:
    ---
    {context_str}
    ---
    Pregunta: {question}
    """
    
    try:
        # Usamos un modelo rápido y económico para esta tarea de clasificación.
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0,  # Queremos una respuesta determinista.
            max_tokens=5    # Solo necesitamos una palabra.
        )
        
        decision = response.choices[0].message.content.strip().lower()
        
        # Devolvemos True si la respuesta contiene "sí".
        return "sí" in decision

    except Exception as e:
        print(f"Error en el evaluador de suficiencia: {e}")
        # En caso de error, es más seguro asumir que los chunks no son suficientes.
        return False