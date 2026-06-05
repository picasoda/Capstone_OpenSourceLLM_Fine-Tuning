---
description: NPC 페르소나 및 프롬프트 빌더 규칙
globs: Chatbot/src/persona.py
---

## Paths
- `Chatbot/src/persona.py`
- `Chatbot/data/npcs.json` (참조)

## Rules

### NPC 조회
- `get_npc(name)` — `npc["name"]`(아서, 마사 등) 또는 `npc["job"]`(영주, 약초상 등) 양쪽으로 조회 가능
- 내부 캐시는 `{name: npc, job: npc}` 양방향으로 빌드

### 프롬프트 빌더
- `npcs.json`에서 NPC 데이터(이름, 성격, 말투, 배경)를 로드하여 베이스 프롬프트 생성
- 빌더 함수 목록
  - `build_chitchat_prompt(npc_name)` — 잡담용
  - `build_combined_query_prompt(npc_name, contexts: dict)` — 단일/복합 정보 쿼리 통합 빌더
    - `contexts = {"item": "...", "npc": "...", "location": "..."}` 형태, 비어있는 섹션 제외
  - `build_jailbreak_prompt(npc_name)` — LLM 미사용, `npcs.json`의 `jailbreak_response` 필드 반환

### 응답 톤 규칙 (프롬프트에 포함)
- `tone_rule` — 말투·문장 길이 규칙, **모든 라우트**에 적용 (`_tone_rules`)
- `item_tone_rule` — 카테고리별 다른 NPC 안내, **아이템 관련 쿼리에만** 적용 (`_item_tone_rules`)
  - `build_combined_query_prompt`에서 contexts에 "item" 키가 있을 때만 포함
- 약초상이 광석(ore/material) 질문 받을 때 → 스텐에게 유도
- 대장장이가 약초(herb/potion/elixir) 질문 받을 때 → 마사에게 유도
- 영주는 모든 아이템에 대해 detail 모른다고 명시

### 상황별 추가 프롬프트
- `append_no_result_instruction(base_prompt)`: 검색 결과 0개 또는 임계값 미달 → "NPC 말투로 모른다고 답하라" 지시 추가
- `append_permission_instruction(base_prompt)`: 권한 밖(common만 반환) → "전문가 NPC에게 유도하라" 지시 추가
- 두 함수는 기존 base_prompt 문자열에 지시를 덧붙여 반환

### 공통
- 프롬프트 조합 외 다른 책임 갖지 않음 (LLM 호출 금지)
