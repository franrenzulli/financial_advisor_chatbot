# APP FastAPI

from fastapi import FastAPI

# import all endpoints from /api/endpoints.py
from api.endpoints import router as api_router

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello from Backend FastAPI!"}

# include all endpoints in /api/endpoints.py
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
