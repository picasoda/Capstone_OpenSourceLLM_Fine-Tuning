import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
import uvicorn

import ollama

from chatbot import chat
from embedder import get_embedder
from llm import MODEL


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_embedder()
    try:
        ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": "."}],
            options={"num_predict": 1},
            think=False,
        )
    except Exception:
        pass
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

_NPC_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "npcs.json")

with open(_NPC_DATA_PATH, encoding="utf-8") as _f:
    _npcs = json.load(_f)

NPC_ID_MAP: dict[str, str] = {npc["id"]: npc["name"] for npc in _npcs}
ALLOWED_NPC_IDS: set[str] = set(NPC_ID_MAP.keys())


class ChatRequest(BaseModel):
    npc: str
    message: str

    @field_validator("npc")
    @classmethod
    def validate_npc(cls, v: str) -> str:
        if v not in ALLOWED_NPC_IDS:
            raise ValueError(f"허용되지 않은 npc ID: {v}")
        return v


class ChatResponse(BaseModel):
    response: str


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    npc_name = NPC_ID_MAP[req.npc]
    result = chat(npc_name=npc_name, message=req.message)
    return ChatResponse(response=result)


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
