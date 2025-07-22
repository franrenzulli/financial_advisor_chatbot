import os
from sentence_transformers import SentenceTransformer





# Carga del modelo de sentence-transformers para generar embeddings
_embedding_model_instance = None
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

def load_embedding_model():
    """Carga el modelo de Sentence-Transformers si aún no ha sido cargado."""
    global _embedding_model_instance
    if _embedding_model_instance is None:
        try:
            print(f"DEBUG UTILS: Intentando cargar el modelo de embedding: '{EMBEDDING_MODEL_NAME}'...")
            _embedding_model_instance = SentenceTransformer(EMBEDDING_MODEL_NAME)
            print(f"DEBUG UTILS: Modelo de embedding '{EMBEDDING_MODEL_NAME}' cargado exitosamente.")
        except Exception as e:
            print(f"ERROR UTILS: Error al cargar el modelo de embedding: {e}")
            _embedding_model_instance = None # Asegurarse de que sea None si falla la carga

    return _embedding_model_instance


# Convertir pregunta del usuario en embedding 
def get_embedding_for_question(question: str):
    """
    Genera el embedding para una pregunta dada utilizando el modelo cargado.
    Llama a load_embedding_model() para asegurar que el modelo esté disponible.
    """
    model = load_embedding_model()
    if model is None:
        raise RuntimeError("El modelo de embedding no está disponible. Fallo en la inicialización.")
    return model.encode(question)

# Opcional: Llamar a la función de carga al importar el módulo para inicializarlo al inicio del backend
load_embedding_model()
