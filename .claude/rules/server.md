---
description: FastAPI API 서버 규칙
globs: Chatbot/src/server.py
---

## Paths
- `Chatbot/src/server.py`

## Rules

### 엔드포인트
- `POST /chat`: 요청 `{npc: str, message: str}` → 응답 `{response: str}`
- `GET /health`: 서버 상태 확인, `{"status": "ok"}` 반환

### CORS
- `CORSMiddleware` 적용: `allow_origins=["*"]`, `allow_methods=["GET", "POST"]`, `allow_headers=["Content-Type"]`
- Unity WebGL 및 ngrok URL 포함 모든 출처 허용

### 실행 설정
- 호스트: `0.0.0.0`
- 포트: `8000`
- 실행: `uvicorn` 사용
- 외부 노출: `ngrok http 8000` (실행 순서는 프로젝트 루트 `ollama.txt` 참조)

### 공통
- 엔드포인트 핸들러는 `chatbot.py`의 `chat()` 함수를 호출하는 얇은 래퍼로 유지
- 입력 검증은 Pydantic 모델로 처리
- 서버 로직(비즈니스 로직)을 이 파일에 직접 구현하지 않음
- `NPC_ID_MAP`은 서버 기동 시 `data/npcs.json`에서 동적 빌드 (`{npc["id"]: npc["name"]}`)
- `npc` 값이 npcs.json에 없는 ID인 경우 422 응답 반환
