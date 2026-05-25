---
description: NPC 페르소나 및 프롬프트 빌더 규칙
globs: Chatbot/src/persona.py
---

## Paths
- `Chatbot/src/persona.py`
- `Chatbot/data/npcs.json` (참조)

## Rules

### 프롬프트 빌더
- `npcs.json`에서 NPC 데이터(이름, 성격, 말투, 배경)를 로드하여 베이스 프롬프트 생성
- 라우트별 시스템 프롬프트 빌더 함수 제공
  - `build_chitchat_prompt(npc)`
  - `build_item_query_prompt(npc, context)`
  - `build_npc_query_prompt(npc, context)`
  - `build_location_query_prompt(npc, context)`
  - `build_jailbreak_prompt(npc)` — LLM 미사용, 고정 응답 반환

### 응답 톤 규칙 (프롬프트에 포함)
- 약초상이 무기(weapon/armor) 질문 받을 때 → common만 답하고 대장장이에게 유도
- 대장장이가 약초(herb/potion) 질문 받을 때 → common만 답하고 약초상에게 유도
- 영주는 모든 질문에 detail 모른다고 명시

### 상황별 추가 프롬프트
- `append_no_result_instruction(base_prompt)`: 검색 결과 0개 또는 임계값 미달 → "NPC 말투로 모른다고 답하라" 지시 추가
- `append_permission_instruction(base_prompt)`: 권한 밖(common만 반환) → "전문가 NPC에게 유도하라" 지시 추가
- 두 함수는 기존 base_prompt 문자열에 지시를 덧붙여 반환

### 공통
- 프롬프트 조합 외 다른 책임 갖지 않음 (LLM 호출 금지)
