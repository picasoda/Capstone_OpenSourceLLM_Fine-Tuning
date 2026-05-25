---
description: LLM(Ollama) 클라이언트 연동 규칙
globs: Chatbot/src/llm.py
---

## Paths
- `Chatbot/src/llm.py`

## Rules

- 모델: `qwen3.5:9b` (Ollama)
- 인터페이스: 시스템 프롬프트 + 유저 메시지를 받아 응답 문자열 반환
- `temperature`, `max_tokens` 등 파라미터는 함수 인자로 노출
- 호출 실패 시 재시도 로직 구현 (최대 재시도 횟수 상수로 정의)
- 재시도 전부 실패 시 호출부로 예외 전파 (chatbot.py에서 fallback 처리)
- LLM 호출 외 다른 책임 갖지 않음 (프롬프트 조합 금지)
