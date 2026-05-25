---
description: 챗봇 메인 파이프라인 로직 규칙
globs: Chatbot/src/chatbot.py
---

## Paths
- `Chatbot/src/chatbot.py`

## Rules

### 파이프라인 순서
1. `router.py`로 입력 분류 → 라우트 변수 결정
2. 라우트에 따라 `search.py`(검색·권한 필터링) + `persona.py`(프롬프트 빌드) 호출
3. `llm.py`로 응답 생성 후 반환

### 라우트별 분기
- `chitchat`: chitchat 프롬프트 + LLM 호출
- `jailbreak`: jailbreak 고정 응답 반환 (LLM 미사용)
- `item_query` / `npc_query` / `location_query`:
  1. 검색 호출
  2. 권한 필터링
  3. 상황별 추가 프롬프트 결합 (`no_result` 또는 `permission_out` 조건 확인)
  4. LLM 호출

### Fallback 처리
- 검색 결과 없음 또는 임계값 미달: `append_no_result_instruction` 적용 후 LLM 호출
- 권한 밖 카테고리(common만 반환): `append_permission_instruction` 적용 후 LLM 호출
- LLM 재시도 전부 실패: npcs.json의 최후 수단 고정 응답 반환

### 공통
- 각 모듈(router, search, persona, llm)을 조합하는 역할만 담당
- 비즈니스 로직을 이 파일에 직접 구현하지 않음
