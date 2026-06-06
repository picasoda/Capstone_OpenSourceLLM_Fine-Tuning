---
description: NPC 페르소나 및 프롬프트 빌더 규칙
globs: Chatbot/src/persona.py
---

## Paths
- `Chatbot/src/persona.py`
- `Chatbot/data/npcPrompt.json` (참조)
- `Chatbot/data/config.json` (참조)

## Rules

### NPC 조회
- `get_npc(name)` — `npc["name"]`(아서, 마사 등) 또는 `npc["job"]`(영주, 약초상 등) 양쪽으로 조회 가능
- 내부 캐시는 `{name: npc, job: npc}` 양방향으로 빌드

### 프롬프트 빌더
- `npcPrompt.json`에서 NPC 데이터 로드하여 베이스 프롬프트 생성
- 빌더 함수 목록
  - `build_chitchat_prompt(npc_name)` — 잡담용
  - `build_combined_query_prompt(npc_name, contexts: dict)` — 단일/복합 정보 쿼리 통합 빌더
    - `contexts = {"item": "...", "npc": "...", "location": "...", "lore": "..."}` 형태, 비어있는 섹션 제외
    - contexts에 "item" 키가 있을 때만 `item_tone_rule` 포함
  - `build_jailbreak_prompt(npc_name)` — LLM 미사용, `npcPrompt.json`의 `jailbreak_response` 필드 반환

### 응답 톤 규칙
- `tone` — 말투 묘사 + 응답 형식 지시 통합, **모든 라우트** `_base_prompt`에 포함
- `item_tone_rule` — 아이템 답변 방향성 지시, **아이템 쿼리에만** 적용 (`_item_tone_rules`)

### 상황별 추가 프롬프트
- `append_no_result_instruction(base_prompt)`: 검색 결과 없음 → config의 `instructions.no_result` 텍스트 추가
- `append_permission_instruction(base_prompt, expert)`: 권한 밖 결과 → config의 `instructions.permission_gap` 텍스트에 담당 NPC명 치환 후 추가
- 두 함수는 기존 base_prompt 문자열에 `[지시]` 태그와 함께 덧붙여 반환

### 공통
- 프롬프트 조합 외 다른 책임 갖지 않음 (LLM 호출 금지)
