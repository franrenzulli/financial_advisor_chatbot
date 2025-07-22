FROM python:3.10-slim

WORKDIR /app

# Copia requirements.txt desde su ubicación
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# El código se montará mediante volumen, no necesita COPY