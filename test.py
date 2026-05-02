from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import uvicorn

# ─────────────────────────────────────────────
# FastAPI 앱 설정
# ─────────────────────────────────────────────
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# vLLM 연결 (같은 PC의 8000번 포트)
# ─────────────────────────────────────────────
MODEL_NAME = "QuantTrio/Qwen3.5-4B-AWQ"

client = OpenAI(
    base_url="http://127.0.0.1:8000/v1",
    api_key="dummy"
)

SYSTEM_PROMPT = (
    "당신은 친절한 AI입니다. "
    "사용자에게 항상 한국어로만 답하세요. "
    "답변은 자연스러운 구어체로, 짧고 간결하게 1~2문장으로 답하세요."
)

# ─────────────────────────────────────────────
# 세션별 대화 히스토리
# ─────────────────────────────────────────────
sessions: dict[str, list] = {}

MAX_TURNS = 20  # system 제외 최근 N개 메시지만 유지


# ─────────────────────────────────────────────
# 요청 / 응답 모델
# ─────────────────────────────────────────────
class ChatRequest(BaseModel):
    session_id: str = "default"
    message: str


class ChatResponse(BaseModel):
    reply: str


# ─────────────────────────────────────────────
# 엔드포인트
# ─────────────────────────────────────────────
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # 새 세션이면 system 프롬프트로 초기화
    if req.session_id not in sessions:
        sessions[req.session_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    history = sessions[req.session_id]
    history.append({"role": "user", "content": req.message})

    # 히스토리 길이 제한 (system + 최근 MAX_TURNS개)
    if len(history) > MAX_TURNS + 1:
        history = [history[0]] + history[-(MAX_TURNS):]
        sessions[req.session_id] = history

    # vLLM에 요청
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=history,
        temperature=0.7,
        max_tokens=100,
        top_p=0.9,
        extra_body={
            "chat_template_kwargs": {
                "enable_thinking": False
            }
        }
    )

    answer = response.choices[0].message.content
    history.append({"role": "assistant", "content": answer})

    return ChatResponse(reply=answer)


@app.post("/reset")
def reset_session(session_id: str = "default"):
    """대화 히스토리 초기화"""
    sessions.pop(session_id, None)
    return {"status": "ok", "message": f"세션 '{session_id}' 초기화 완료"}


@app.get("/health")
def health_check():
    """서버 상태 확인용"""
    return {"status": "running"}


# ─────────────────────────────────────────────
# 실행
# ─────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)