from fastapi import APIRouter
from pydantic import BaseModel
import os 

# Importa la función de utilidad para convertir preguntas de usuarios en embeddings
from rag.embedder import get_embedding_for_question

# Importa funcion para consultar chunks similares al embedding
from rag.retriever import retrieve_relevant_chunks

router = APIRouter()

# pydantic model for user request
class QuestionRequest(BaseModel):
    question: str

@router.post("/ask")
async def ask_question(request: QuestionRequest):

    try:
        # Convertir la pregunta en un vector numérico (embedding)

        question_embedding = get_embedding_for_question(request.question)

        # El retriever usa el embedding conseguido arriba para traer los chunks mas parecidos que se usaran para el prompt de openAI
        relevant_chunks = retrieve_relevant_chunks(question_embedding, top_k=3)


        return {
            "answer": f"Backend dice: Recibí tu pregunta '{request.question}'. "
                      f"La convertí a un embedding de forma {question_embedding.shape}! "
                      f"¡Listo para los siguientes pasos!"
        }

    except RuntimeError as e: # Captura la excepción que lanzaría get_embedding_for_question si el modelo no cargó
        print(f"ERROR BACKEND: {e}")
        return {"answer": f"Error interno del servidor: {e}. No se pudo generar el embedding."}
    except Exception as e:
        print(f"ERROR BACKEND: Error inesperado al procesar la pregunta: {e}")
        return {"answer": f"Ocurrió un error inesperado. Por favor, intenta de nuevo. Detalles: {e}"}
