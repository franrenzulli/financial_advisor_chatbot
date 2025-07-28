FROM python:3.10-slim

WORKDIR /app

# Instala dependencias del sistema si son necesarias
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Precarga el modelo de sentence-transformers durante la construcción
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Copia el código de la aplicación
COPY . .

# Expone el puerto 8001 (diferente del API)
EXPOSE 8001

# Comando para ejecutar el servicio RAG
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]