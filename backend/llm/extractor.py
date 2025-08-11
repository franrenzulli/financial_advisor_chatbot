# /app/llm/extractor.py
import os
import google.generativeai as genai
from typing import Tuple

try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    print(f"Error al configurar la API de Gemini: {e}")
    model = None

def extract_financial_info(question: str, sub_route: str) -> Tuple[str, str, str]:
    if not model:
        print("El modelo de Gemini no está disponible. No se puede extraer la información.")
        return "", "", ""

    if sub_route == "API_COTIZACION":
        prompt = f"""
        Eres un asistente experto en finanzas. Tu única tarea es extraer el símbolo de la acción de la siguiente pregunta.
        Si la pregunta menciona una empresa como Apple, devuelve su símbolo (AAPL). Si es Microsoft, devuelve MSFT.
        Si no contiene un símbolo o nombre de empresa, devuelve la cadena "no_encontrado".
        Ejemplo: "precio de las acciones de Apple hoy?" -> "AAPL"
        
        Pregunta del usuario: "{question}"
        Símbolo:
        """
        try:
            response = model.generate_content(prompt)
            symbol = response.text.strip().upper()
            return (symbol if symbol != "NO_ENCONTRADO" else "", "", "")
        except Exception as e:
            print(f"Error al extraer el símbolo de acción con Gemini: {e}")
            return "", "", ""

    elif sub_route == "TIPO_DE_CAMBIO":
        prompt = f"""
        Eres un asistente experto en finanzas. Tu única tarea es extraer la cantidad y los tickers de las monedas de la siguiente pregunta.
        Formato de respuesta: 'CANTIDAD,MONEDA_ORIGEN,MONEDA_DESTINO'. Si no encuentras la información, usa 'no_encontrado'.
        Ejemplos:
        - "cuánto es 100 dolares en euros?" -> "100,USD,EUR"
        - "convertir 500 yenes a libras" -> "500,JPY,GBP"
        - "tipo de cambio del euro" -> "no_encontrado"
        - "cómo estás?" -> "no_encontrado"
        
        Pregunta del usuario: "{question}"
        Resultado:
        """
        try:
            response = model.generate_content(prompt)
            result = response.text.strip().upper()
            if result != "NO_ENCONTRADO":
                parts = result.split(',')
                if len(parts) == 3:
                    return parts[1], parts[2], parts[0]
            return "", "", ""
        except Exception as e:
            print(f"Error al extraer tickers de divisas con Gemini: {e}")
            return "", "", ""

    elif sub_route == "NOTICIAS":
        prompt = f"""
        Eres un asistente experto. Tu única tarea es extraer el tema o nombre de la empresa de la que el usuario quiere noticias.
        Si la pregunta no contiene un nombre de empresa o un tema claro, devuelve la cadena "no_encontrado".

        Ejemplos:
        - ¿Cuáles son las últimas noticias sobre Google? -> "Google"
        - Últimas noticias de la bolsa de valores. -> "bolsa de valores"
        - Noticias recientes de Tesla. -> "Tesla"
        
        Pregunta del usuario: "{question}"
        Resultado:
        """
        try:
            response = model.generate_content(prompt)
            entity = response.text.strip()
            return (entity if entity != "no_encontrado" else "", "", "")
        except Exception as e:
            print(f"Error al extraer la entidad para noticias con Gemini: {e}")
            return "", "", ""

    return "", "", ""