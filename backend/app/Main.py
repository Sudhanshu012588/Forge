from fastapi import FastAPI
from app.api.agent import router as agent_router

app = FastAPI(title="Forge API")

app.include_router(agent_router)

@app.get("/")
def root():
    return {"message": "Welcome to Forge"}