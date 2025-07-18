# APP FastAPI

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello from Backend FastAPI!"}

# Aquí irá la lógica de tu chatbot, endpoints para preguntas, etc.
# Puedes añadir un endpoint de prueba para verificar que el backend funciona
# @app.post("/ask")
# async def ask_question(question: str):
#     # ... lógica de recuperación y generación ...
#     return {"answer": f"You asked: {question}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
