---
description: Semantic Router 입력 분류 규칙
globs: Chatbot/src/router.py
---

## Paths
- `Chatbot/src/router.py`

## Rules

### 라우트 정의
- 명시적 라우트 4종: `item_query`, `npc_query`, `location_query`, `jailbreak`
- `chitchat`은 예시 없는 default fallback (명시적 라우트 미해당 시 자동 분류)

### 예시 문장
- 명시적 라우트당 예시 문장 10~15개 등록
- `item_query`, `npc_query`, `location_query` 예시에는 순수 질문 + 잡담 섞인 변형 모두 포함
- `jailbreak` 예시: 시스템 조작 시도, 현대 기술·AI 언급 등 시대 부적합 발언

### 임계값 및 Fallback
- `ROUTER_THRESHOLD = 0.4` 상수로 정의
- 가장 유사한 라우트 점수가 임계값 미달이면 `chitchat` 반환
- 정보 질문 라우트가 감지되면 chitchat보다 우선 라우팅

### 인터페이스
- 공용 임베딩 모델(`embedder.py`) import하여 사용 (독자 로드 금지)
- 반환값: 라우트 이름 문자열 (`item_query` / `npc_query` / `location_query` / `jailbreak` / `chitchat`)
- 라우트 분류 외 다른 책임 갖지 않음
