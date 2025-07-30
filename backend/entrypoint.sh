#!/bin/bash
set -e

# Ejecuta el proceso de ingestion en segundo plano
python ingestion/process_s3_documents.py &

# Inicia el servidor de la API
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
