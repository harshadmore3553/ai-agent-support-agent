from __future__ import annotations

import logging
import uuid

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .agent import SupportAgent
from .config import LOG_LEVEL

logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper(), logging.INFO))

app = FastAPI(title="Aster & Row Reliable Support Agent", version="1.0.0")
agent = None
sessions: dict[str, list[dict[str, str]]] = {}

class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    session_id: str | None = None
    debug: bool = False

class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: list[dict[str, str]]
    handoff: bool
    tool_used: str | None = None
    trace: dict = {}

@app.on_event("startup")
def startup():
    global agent
    agent = SupportAgent()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    history = sessions.setdefault(session_id, [])

    result = agent.respond(req.message, history)
    history.append({"role": "user", "content": req.message})
    history.append({"role": "assistant", "content": result["answer"]})

    if not req.debug:
        result["trace"] = {}

    return ChatResponse(session_id=session_id, **result)
