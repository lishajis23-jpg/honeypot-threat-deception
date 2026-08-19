from fastapi import FastAPI
from pydantic import BaseModel

from agent.agent import run_agent


app = FastAPI(
    title="TechNova AI Agent",
    version="1.0"
)


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    answer: str


@app.get("/")
def root():
    return {
        "message": "TechNova AI Agent is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    answer = run_agent(request.query)

    return {
        "answer": answer
    }