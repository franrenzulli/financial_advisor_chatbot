FROM python:3.10-slim

WORKDIR /app

# Instala dependencias del sistema necesarias para procesamiento de PDFs
RUN apt-get update && apt-get install -y \
    curl \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Precarga modelos necesarios
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Copia el código de la aplicación
COPY . .

# El comando se especifica en docker-compose para flexibilidad
CMD ["python", "ingestion/process_s3_documents.py"]