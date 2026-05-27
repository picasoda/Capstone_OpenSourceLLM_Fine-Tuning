import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
import uvicorn

from chatbot import chat

app = FastAPI()

NPC_ID_MAP = {
    "npc_arthur":    "영주",
    "npc_martha":    "약초상",
    "npc_sten":      "대장장이",
    "npc_jasper":    "상인",
    # JSON id 형식도 허용
    "npc_lord":        "영주",
    "npc_herbalist":   "약초상",
    "npc_blacksmith":  "대장장이",
}

ALLOWED_NPC_IDS = set(NPC_ID_MAP.keys())


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
