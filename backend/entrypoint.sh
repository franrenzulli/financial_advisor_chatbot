#!/bin/bash
set -e

# Inicia el servidor de la API
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
