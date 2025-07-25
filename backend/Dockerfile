# Dockerfile del servicio 'backend'
FROM python:3.9-slim-buster 

WORKDIR /app

COPY llm/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- AGREGAR ESTAS LÍNEAS PARA PRECARGAR EL MODELO ---
# Esto descargará el modelo durante la construcción de la imagen.
# Asegúrate de que 'sentence-transformers' ya esté en tu requirements.txt.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

COPY . . 

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# (Ajusta 'main:app' si tu aplicación FastAPI se llama diferente o está en otro archivo)
