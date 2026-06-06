# npcs.json 구조 변경 계획

## 완료된 변경

### 1. `tone_rule` → `tone`에 병합
- `npcPrompt.json`: `tone` 끝에 `tone_rule` 내용 이어붙임, `tone_rule` 필드 삭제
- `persona.py`: `_tone_rules()` 함수 및 호출부 제거

### 2. `knowledge_scope` 제거
- `npcPrompt.json`: `knowledge_scope` 필드 삭제
- `search.py` `filter_by_permission`: `detail_categories` 비어있는지 여부로 분기
- `chatbot.py` `_has_permission_gap`: `knowledge_scope` 참조 제거

### 3. `item_tone_rule` 내용 수정
- `npcPrompt.json`: 권한·리다이렉션 문구 제거, 아이템 답변 방향성만 남김

### 4. 파일 구조 재편
- `data/npcs.json` → `data/npcPrompt.json`
- `data/content/npcs.json` 신규 생성 (`id`, `name`, `common` 구조)
- `persona.py`, `search.py`, `server.py`: 경로 → `npcPrompt.json`
- `ingest.py` `ingest_npcs()`: `content/npcs.json` 읽도록 변경
- `search.py` `search_npc()`: `common` 필드로 변경

### 5. `append_permission_instruction` NPC-aware + 지시 텍스트 외부화
- `config.json`: `instructions` (no_result, permission_gap 템플릿) 추가
- `persona.py`: config에서 텍스트 로드, `append_permission_instruction(base, expert)` 시그니처 변경
- `chatbot.py`: `_get_redirect_expert()` 추가, expert 전달

### 6. `category_experts` 중복 제거
- `config.json`: `category_experts` 섹션 삭제
- `chatbot.py`: `npcPrompt.json`의 `detail_categories`에서 런타임 역방향 빌드
  ```python
  _CATEGORY_EXPERTS = {
      cat: npc["name"]
      for npc in json.load(_f)
      for cat in npc.get("detail_categories", [])
  }
  ```
