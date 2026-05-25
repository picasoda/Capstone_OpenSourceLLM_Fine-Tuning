---
description: 게임 데이터 JSON 파일 작성 및 수정 규칙
globs: Chatbot/data/*.json
---

## Paths
- `Chatbot/data/items.json`
- `Chatbot/data/npcs.json`
- `Chatbot/data/locations.json`
- `Chatbot/data/worldlore.json`

## Rules

### items.json
- 최상위 키: `id`, `name`, `category`, `common`, `detail`
- `category` 허용값: `herb`, `potion`, `weapon`, `armor`
- `common`: 일반인 수준 정보 (외형, 대략적 용도, 일반 획득처)
- `detail`: 전문가 전용 정보 (제작 레시피, 정확한 수치, 부작용)
- 항목 수: 30~50개

### npcs.json
- 등장 NPC: 영주, 약초상, 대장장이 (총 3명)
- 필수 필드: `name`, `personality`, `tone`, `background`, `knowledge_scope`, `detail_categories`
- `knowledge_scope` 허용값: `common_only`, `category_detail`
- NPC별 권한 규칙
  - 영주: 모든 컬렉션 `common_only`
  - 약초상: items는 `category_detail` (herb, potion만), 나머지 `common_only`
  - 대장장이: items는 `category_detail` (weapon, armor만), 나머지 `common_only`

### locations.json
- 구조: `common` / `detail` 분리
- 항목 수: 10~15개

### worldlore.json
- 구조: `common` 정보 위주
- 항목 수: 5~10개

### 공통
- JSON 형식은 배열(`[]`) 최상위 구조 사용
- 필드명은 snake_case 사용
- 기존 데이터 항목 삭제 금지 (추가·수정만 허용)
