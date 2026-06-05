---
description: 게임 데이터 JSON 파일 작성 및 수정 규칙
globs: Chatbot/data/*.json
---

## Paths
- `Chatbot/data/items.json`
- `Chatbot/data/npcs.json`
- `Chatbot/data/locations.json`
- `Chatbot/data/worldlore.json`
- `Chatbot/data/routes.json`
- `Chatbot/data/config.json`

## Rules

### items.json
- 최상위 키: `id`, `name`, `category`, `common`, `detail`
- `category` 허용값: `herb`, `potion`, `weapon`, `armor`, `food`, `decoration`, `ore`, `fish`, `junk`, `mushroom`, `crystal`, `elixir`, `material`
- `common`: 일반인 수준 정보 (외형, 대략적 용도, 일반 획득처)
- `detail`: 전문가 전용 정보 (제작 레시피, 정확한 수치, 부작용)
- 항목 수: 30~50개

### npcs.json
- 등장 NPC: 영주, 약초상, 대장장이, 상인 (총 4명)
- 필수 필드: `id`, `name`, `job`, `personality`, `tone`, `background`, `knowledge_scope`, `detail_categories`, `tone_rule`, `item_tone_rule`, `fallback_response`, `jailbreak_response`
- `knowledge_scope` 허용값: `common_only`, `category_detail`
- `tone_rule`: NPC별 응답 유도 지시 텍스트 (없으면 빈 문자열 `""`)
- `jailbreak_response`: jailbreak 감지 시 LLM 없이 반환할 고정 응답
- NPC별 권한 규칙
  - 영주: 모든 컬렉션 `common_only`
  - 약초상: items는 `category_detail` (herb, potion만), 나머지 `common_only`
  - 대장장이: items는 `category_detail` (weapon, armor만), 나머지 `common_only`
  - 상인: 모든 컬렉션 `common_only`

### routes.json
- 라우터 예시 문장 정의 파일 (router.py가 startup 시 로드)
- 최상위 키: `item_query`, `npc_query`, `location_query`, `jailbreak`
- 각 키의 값: 예시 문장 배열 (라우트당 10~15개)
- `chitchat`은 포함하지 않음 (default fallback이므로)

### config.json
- LLM·라우터·검색 설정 상수 통합 파일
- 구조:
  ```json
  {
    "llm":    { "model", "max_retries", "retry_delay", "default_temperature", "default_max_tokens" },
    "router": { "threshold", "softmax_temperature" },
    "search": { "top_k", "threshold" }
  }
  ```
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
