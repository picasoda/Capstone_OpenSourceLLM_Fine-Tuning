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

### 실행 설정
- 호스트: `0.0.0.0`
- 포트: `8000`
- 실행: `uvicorn` 사용

### 공통
- 엔드포인트 핸들러는 `chatbot.py`의 `chat()` 함수를 호출하는 얇은 래퍼로 유지
- 입력 검증은 Pydantic 모델로 처리
- 서버 로직(비즈니스 로직)을 이 파일에 직접 구현하지 않음
- `npc` 값이 허용된 NPC 이름(영주, 약초상, 대장장이)이 아닌 경우 422 응답 반환
