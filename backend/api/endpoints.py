# FASTApi routes

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# pydantic model for user request
class QuestionRequest(BaseModel):
    question: str

@router.post("/ask") 
async def ask_question(request: QuestionRequest):

    print(f"Pregunta recibida desde el frontend: {request.question}") 
    return {"answer": f"Backend dice: Recibí tu pregunta '{request.question}'. ¡Todo bien por ahora!"}
