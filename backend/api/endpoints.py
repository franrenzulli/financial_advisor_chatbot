from rag.retriever import retrieve_chunks

@router.post("/ask")
async def ask_question(request: QuestionRequest):
    try:
        # Recuperar chunks relevantes para la pregunta
        retrieved_chunks = retrieve_chunks(request.question, top_k=3)

        return {
            "question": request.question,
            "retrieved_chunks": retrieved_chunks
        }

    except Exception as e:
        print(f"ERROR BACKEND: {e}")
        return {"answer": f"Error inesperado: {e}"}
