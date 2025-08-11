# /app/llm/router.py

import os
import google.generativeai as genai
from typing import Tuple

try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    print(f"Error al configurar la API de Gemini: {e}")
    model = None
    
def route_question(question: str) -> Tuple[str, str]:
    if not model:
        print("El modelo de Gemini no está disponible. Usando ruta por defecto.")
        return ("CONVERSACIONAL", "CONSEJO_GENERAL")

    prompt = f"""
    Eres un clasificador de preguntas de un asistente virtual financiero.
    Tu tarea es clasificar la siguiente pregunta del usuario en la categoría más relevante.

    Categorías y Sub-categorías:
    - CATEGORIA: CONVERSACIONAL
        - SUB-CATEGORIA: CONSEJO_GENERAL (para saludos, preguntas abiertas como 'deberia invertir en bonos' o despedidas)
        - SUB-CATEGORIA: FUERA_DE_TEMA (para preguntas no relacionadas con finanzas, ej: 'qué tiempo hace?')
    - CATEGORIA: CALCULOS_Y_PROYECCIONES
        - SUB-CATEGORIA: INTERES_COMPUESTO (si pregunta por el valor futuro de una inversion)
        - SUB-CATEGORIA: TIPO_DE_CAMBIO (si pregunta por el valor de una divisa en otra, ej: 'cuánto es 100 dolares en euros')
        - SUB-CATEGORIA: CALCULO_GENERAL (para otros cálculos matemáticos simples)
    - CATEGORIA: DATOS_ESPECIFICOS
        - SUB-CATEGORIA: API_COTIZACION (si pide el precio actual de una acción o un índice, ej: 'precio de las acciones de Apple hoy')
        - SUB-CATEGORIA: RAG_NASDAQ (si pregunta por historia, características, datos de una empresa del nasdaq que requieran nuestra base de conocimiento)
        - SUB-CATEGORIA: NOTICIAS (si pregunta por noticias o eventos recientes de una empresa o tema, ej: 'últimas noticias de Tesla')
    - CATEGORIA: CONSEJO_FINANCIERO
        - SUB-CATEGORIA: RECOMENDACION_COMPRA (si pregunta qué acciones comprar)
        - SUB-CATEGORIA: RECOMENDACION_PORTAFOLIO (si pregunta cómo armar un portafolio)
        - SUB-CATEGORIA: CONSEJO_DE_INVERSION (si pide consejo sobre dónde invertir, como 'debo invertir en bonos?')

    Responde únicamente con el nombre de la CATEGORIA y la SUB-CATEGORIA, separados por una coma.
    Ejemplo:
    Pregunta: "últimas noticias de Amazon" -> DATOS_ESPECIFICOS,NOTICIAS
    
    ---
    Pregunta a clasificar: "{question}"

    Categoría,Sub-categoría:
    """

    try:
        response = model.generate_content(prompt)
        route_str = response.text.strip()
        
        if ',' in route_str:
            route, sub_route = route_str.split(',', 1)
            route = route.strip()
            sub_route = sub_route.strip()
            
            valid_routes = ["CONVERSACIONAL", "CALCULOS_Y_PROYECCIONES", "DATOS_ESPECIFICOS", "CONSEJO_FINANCIERO"]
            if route in valid_routes:
                return (route, sub_route)
        
        print(f"Respuesta inesperada del router: '{route_str}'. Usando fallback.")
        return ("CONVERSACIONAL", "CONSEJO_GENERAL")
    
    except Exception as e:
        print(f"Error en el enrutador con Gemini: {e}")
        return ("CONVERSACIONAL", "CONSEJO_GENERAL")