---
description: 임베딩 모델 공용 로더 규칙
globs: Chatbot/src/embedder.py
---

## Paths
- `Chatbot/src/embedder.py`

## Rules

- 모델: `BAAI/bge-m3` 고정
- 싱글톤 패턴으로 구현 — 프로세스 내 1회만 로드
- `router.py`와 `search.py` 양쪽에서 import하여 공유 (중복 로드 금지)
- `HF_HOME` 환경변수로 HuggingFace 캐시 경로 지정 가능하도록 구현
- 모델 로드 실패 시 명확한 에러 메시지 출력 후 종료
- 로더 함수·객체 외 다른 책임 갖지 않음 (단일 책임 원칙)
