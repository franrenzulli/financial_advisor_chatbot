# APP FastAPI - backend_fastapi/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # <--- ¡IMPORTA ESTO!
from feedback.database import init_db # Asegúrate que la importación sea correcta

# import all endpoints from /api/endpoints.py
from api.endpoints import router as api_router

init_db()


app = FastAPI()

# --- ¡AGREGA ESTA SECCIÓN PARA LA CONFIGURACIÓN CORS! ---
# Esto es CRUCIAL para que tu frontend React (que correrá en un puerto diferente)
# pueda hacer peticiones a este backend.
origins = [
    "http://localhost:3000",   # El puerto de desarrollo de tu aplicación React (Create React App)
    "http://localhost:5173",   # El puerto de desarrollo de tu aplicación React (Vite)
    # Si despliegas tu frontend en un dominio específico, añádelo aquí también:
    # "https://tu-dominio-frontend-en-produccion.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permite todos los encabezados HTTP
)
# --- FIN DE LA SECCIÓN CORS ---

@app.get("/")
async def read_root():
    return {"message": "Hello from Backend FastAPI!"}

# include all endpoints in /api/endpoints.py
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
