---
description: 벡터 DB 색인 및 검색 규칙
globs: Chatbot/src/{ingest,search}.py
---

## Paths
- `Chatbot/src/ingest.py`
- `Chatbot/src/search.py`
- `Chatbot/db/` (ChromaDB 저장 경로)

## Rules

### ingest.py — 색인
- ChromaDB 클라이언트 경로: `./db/`
- 컬렉션 4개: `items`, `npcs`, `locations`, `lore`
- 아이템 색인 시 `common` + `detail` 텍스트를 합쳐서 임베딩, 메타데이터에 `category` 반드시 포함
- NPC 색인: `data/content/npcs.json` 읽음 (페르소나 설정인 `npcPrompt.json`과 별개)
- 색인 스크립트는 1회 실행용 (멱등성 보장)

### search.py — 검색
- 검색 함수: `search_item(query, npc)`, `search_npc(query, npc)`, `search_location(query, npc)`, `search_lore(query, npc)`
- 상수: `TOP_K`, `SEARCH_THRESHOLD`는 `data/config.json`의 `search` 섹션에서 로드
- `SEARCH_THRESHOLD` 미달 결과는 반환 목록에서 제외
- 검색 결과 0개이면 빈 리스트 반환
- `search_npc()`: 메타데이터의 `common` 필드를 content로 반환
- `search_lore`: NPC 권한 구분 없이 항상 `common` 필드만 반환

### 권한 필터링 (`filter_by_permission`)
- NPC의 `detail_categories`에 따라 반환 필드 결정
  - `detail_categories`가 비어있음 → `common` 필드만 반환
  - 아이템 카테고리가 `detail_categories`에 포함 → `common` + `detail` 반환
  - 카테고리 불일치 → `common` 필드만 반환
- 권한 외 정보는 이 단계에서 잘라냄 — LLM에 전달 금지

### 공통
- 공용 임베딩 모델(`embedder.py`) import하여 사용 (독자 로드 금지)
