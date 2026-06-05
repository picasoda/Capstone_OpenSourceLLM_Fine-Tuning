---
description: 챗봇 메인 파이프라인 로직 규칙
globs: Chatbot/src/chatbot.py
---

## Paths
- `Chatbot/src/chatbot.py`

## Rules

### 파이프라인 순서
1. `router.py`로 입력 분류 → 라우트 목록(`list[str]`) 결정
2. 각 라우트마다 `search.py`(검색·권한 필터링) 호출 → 컨텍스트 합산
3. `persona.py`로 합산 컨텍스트 기반 프롬프트 빌드
4. `llm.py`로 응답 생성 후 반환

### 라우트별 분기
- `["chitchat"]`: chitchat 프롬프트 + LLM 호출
- `["jailbreak"]`: jailbreak 고정 응답 반환 (LLM 미사용)
- 정보 라우트 1개 이상 (`item_query` / `npc_query` / `location_query` / `lore_query` 조합):
  1. 각 라우트마다 해당 search 함수 호출
  2. 결과를 `contexts` 딕셔너리로 합산 (`{"item": "...", "npc": "...", "location": "...", "lore": "..."}`)
  3. `build_combined_query_prompt(npc_name, contexts)` 호출
  4. 상황별 추가 프롬프트 결합 (`no_result` 또는 `permission_gap` 조건 확인)
  5. LLM 호출

### Fallback 처리
- 모든 라우트 검색 결과가 비어있음: `append_no_result_instruction` 적용 후 LLM 호출
- item_query 결과에 권한 밖 카테고리(common만 반환): `append_permission_instruction` 적용 후 LLM 호출
- LLM 재시도 전부 실패: npcs.json의 최후 수단 고정 응답 반환

### 공통
- 각 모듈(router, search, persona, llm)을 조합하는 역할만 담당
- 비즈니스 로직을 이 파일에 직접 구현하지 않음
