---
description: 게임 데이터 JSON 파일 작성 및 수정 규칙
globs: Chatbot/data/*.json
---

## Paths
- `Chatbot/data/npcPrompt.json`
- `Chatbot/data/content/npcs.json`
- `Chatbot/data/items.json`
- `Chatbot/data/locations.json`
- `Chatbot/data/worldlore.json`
- `Chatbot/data/routes.json`
- `Chatbot/data/config.json`

## Rules

### npcPrompt.json
- NPC 페르소나·권한 설정 파일 (코드에서 직접 로드, 색인 대상 아님)
- 등장 NPC: 영주, 약초상, 대장장이, 상인 (총 4명)
- 필수 필드: `id`, `name`, `job`, `personality`, `tone`, `background`, `detail_categories`, `item_tone_rule`, `fallback_response`, `jailbreak_response`
- `tone`: 말투 묘사 + 응답 형식 지시 (문장 길이 등) 통합
- `detail_categories`: 빈 배열이면 common_only, 값이 있으면 해당 카테고리만 detail 반환
- `item_tone_rule`: 아이템 쿼리 시 응답 방향성 지시 (권한·리다이렉션 내용 포함 금지)
- `jailbreak_response`: jailbreak 감지 시 LLM 없이 반환할 고정 응답
- NPC별 권한 규칙
  - 영주: `detail_categories: []` → 모든 아이템 common_only
  - 약초상: `detail_categories: ["herb", "potion", "elixir", "mushroom", "crystal"]`
  - 대장장이: `detail_categories: ["ore", "material", "weapon", "armor"]`
  - 상인: `detail_categories: ["food", "decoration"]`

### content/npcs.json
- npc_query 검색용 NPC 소개 데이터 (ChromaDB `npcs` 컬렉션에 색인)
- 필수 필드: `id`, `name`, `common`
- `common`: 플레이어가 알 수 있는 NPC 소개 (직함 포함하여 자연스럽게 작성)

### items.json
- 최상위 키: `id`, `name`, `category`, `common`, `detail`
- `category` 허용값: `herb`, `potion`, `weapon`, `armor`, `food`, `decoration`, `ore`, `fish`, `junk`, `mushroom`, `crystal`, `elixir`, `material`
- `common`: 일반인 수준 정보 (외형, 대략적 용도, 일반 획득처)
- `detail`: 전문가 전용 정보 (제작 레시피, 정확한 수치, 부작용)
- 항목 수: 30~50개

### routes.json
- 라우터 예시 문장 정의 파일 (router.py가 startup 시 로드)
- 최상위 키: `item_query`, `npc_query`, `location_query`, `lore_query`, `jailbreak`
- 각 키의 값: 예시 문장 배열 (라우트당 10~15개)
- `chitchat`은 포함하지 않음 (default fallback이므로)

### config.json
- LLM·라우터·검색·지시문 설정 통합 파일
- 구조:
  ```json
  {
    "llm":    { "model", "max_retries", "retry_delay", "default_temperature", "default_max_tokens" },
    "router": { "threshold", "softmax_temperature" },
    "search": { "top_k", "threshold" },
    "instructions": { "no_result", "permission_gap" }
  }
  ```
- `instructions.permission_gap`: `{expert}` 플레이스홀더 포함, 런타임에 담당 NPC명으로 치환
- 모델 교체·임계값 변경은 이 파일만 수정

### locations.json
- 구조: `common` / `detail` 분리
- 항목 수: 10~15개

### worldlore.json
- 구조: `common` 정보 위주
- 항목 수: 5~10개

### 공통
- JSON 형식은 배열(`[]`) 최상위 구조 사용 (config.json, routes.json 제외 — 객체 구조)
- 필드명은 snake_case 사용
- 기존 데이터 항목 삭제 금지 (추가·수정만 허용)
