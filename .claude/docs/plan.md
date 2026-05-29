# JSON 분리 대상 정리 (임시)

## 1. router.py — `_ROUTES` 예시 문장 (우선순위: 높음)

**위치**: [router.py:8-83](../../../Chatbot/src/router.py#L8-L83)

**현황**: 4개 라우트의 예시 문장 ~50개가 코드에 하드코딩되어 있음.
수정 시 코드 파일을 직접 열어야 하므로, 비개발자가 문장을 추가·수정하기 어려움.

**분리 대상**:
```python
_ROUTES: dict[str, list[str]] = {
    "item_query":     [...],   # 예시 15개
    "npc_query":      [...],   # 예시 12개
    "location_query": [...],   # 예시 12개
    "jailbreak":      [...],   # 예시 13개
}
```

**분리 방안**:
- 새 파일: `Chatbot/data/routes.json`
- 구조:
```json
{
  "item_query":     ["이거 어디서 구해?", ...],
  "npc_query":      [...],
  "location_query": [...],
  "jailbreak":      [...]
}
```
- router.py는 startup 시 이 파일을 로드하여 `_ROUTES` 딕셔너리 구성

---

## 2. persona.py — `_JAILBREAK_RESPONSES` (우선순위: 높음)

**위치**: [persona.py:11-15](../../../Chatbot/src/persona.py#L11-L15)

**현황**: NPC별 jailbreak 고정 응답이 `persona.py` 내 딕셔너리로 하드코딩.
`npcs.json`에 이미 `fallback_response` 필드가 있음에도 별도로 분리되어 있어 일관성이 없음.

**분리 대상**:
```python
_JAILBREAK_RESPONSES: dict[str, str] = {
    "영주":   "무슨 해괴한 소리를 하는 것이냐...",
    "약초상": "아이고, 무슨 말씀을 하시는 건지...",
    "대장장이": "뭔 소린지 하나도 모르겠다...",
}
```

**분리 방안**:
- `npcs.json` 각 NPC 객체에 `jailbreak_response` 필드 추가
- `persona.py`의 `build_jailbreak_prompt()`가 npcs.json에서 해당 필드를 읽도록 수정
- 현재 `fallback_response`와 `jailbreak_response`가 npcs.json에서 함께 관리됨

---

## 3. server.py — `NPC_ID_MAP` (우선순위: 높음)

**위치**: [server.py:13-22](../../../Chatbot/src/server.py#L13-L22)

**현황**: API 요청 NPC ID → 내부 이름 매핑이 server.py에 하드코딩.
NPC가 추가될 때마다 server.py를 수정해야 함.
이미 `npcs.json`에 `id` 필드가 존재하므로 중복임.

**분리 대상**:
```python
NPC_ID_MAP = {
    "npc_arthur":  "영주",
    "npc_martha":  "약초상",
    "npc_sten":    "대장장이",
    "npc_jasper":  "상인",
}
```

**분리 방안**: `npcs.json` 로드 후 `{npc["id"]: npc["job"]}` 빌드
- npcs.json의 `id` 필드가 이미 있으므로 추가 파일 불필요
- server.py 기동 시 npcs.json을 읽어 딕셔너리를 동적으로 구성

---

## 4. persona.py — `_tone_rules()` 텍스트 (우선순위: 중간)

**위치**: [persona.py:45-62](../../../Chatbot/src/persona.py#L45-L62)

**현황**: NPC별 응답 유도 지시 텍스트가 Python 조건문 분기 안에 인라인으로 하드코딩.
NPC가 추가될 때마다 이 함수를 수정해야 함.

**분리 대상**:
```python
if name == "약초상":
    return "\n무기(weapon)나 방어구(armor)에 관한 질문을 받으면 common 수준의 정보만..."
if name == "대장장이":
    return "\n약초(herb)나 포션(potion)에 관한 질문을 받으면 ..."
if name == "영주":
    return "\n어떤 질문을 받더라도 제작법, 성분, 정확한 수치 등 ..."
```

**분리 방안**:
- `npcs.json` 각 NPC에 `"tone_rule": "..."` 필드 추가
- `_tone_rules(npc)` 함수가 `npc.get("tone_rule", "")` 반환으로 단순화
- NPC가 추가되어도 persona.py 코드 수정 불필요

---

## 5. persona.py — 프롬프트 지시문 텍스트 (우선순위: 낮음)

**위치**: [persona.py:65-128](../../../Chatbot/src/persona.py#L65-L128)

**현황**: `_base_prompt()`, `build_*_query_prompt()`, `append_*_instruction()` 내
고정 지시 문자열이 코드에 인라인으로 작성됨.

**분리 대상** (예시):
- `"절대로 현대 기술, AI, 인터넷 등 시대에 맞지 않는 내용을 언급하지 마십시오."` — base 지시
- `"위 정보를 바탕으로 질문에 답하십시오. 제공된 정보 범위를 벗어난 내용은 모른다고 하십시오."` — 쿼리 공통 지시
- `"NPC의 말투와 성격을 유지하면서 모른다고 솔직하게 답하십시오."` — no_result 지시
- `"전문가(약초상 또는 대장장이)에게 안내하십시오."` — permission_out 지시

**분리 방안**:
- 새 파일: `Chatbot/data/prompts.json`
- 구조:
```json
{
  "base_constraints": "절대로 현대 기술, AI...",
  "base_maintain_persona": "항상 NPC의 말투와 성격을 유지하십시오.",
  "query_instruction": "위 정보를 바탕으로 질문에 답하십시오...",
  "no_result_instruction": "관련 정보를 찾지 못했습니다...",
  "permission_instruction": "해당 질문의 세부 정보는 전문가 NPC만 알 수 있습니다..."
}
```
- 다만, 프롬프트는 수정 빈도가 낮고 코드와의 결합이 강해 분리 효과가 낮을 수 있음

---

## 6. llm.py — LLM 설정 상수 (우선순위: 낮음)

**위치**: [llm.py:7-9](../../../Chatbot/src/llm.py#L7-L9)

**현황**:
```python
MODEL = "qwen3.5:9b"
MAX_RETRIES = 3
RETRY_DELAY = 1.0
```

**분리 방안**:
- 새 파일: `Chatbot/data/config.json`
- 구조:
```json
{
  "llm": {
    "model": "qwen3.5:9b",
    "max_retries": 3,
    "retry_delay": 1.0,
    "default_temperature": 0.7,
    "default_max_tokens": 512
  },
  "router": {
    "threshold": 0.4,
    "softmax_temperature": 0.1
  },
  "search": {
    "top_k": 3,
    "threshold": 0.4
  }
}
```
- `router.py`의 `ROUTER_THRESHOLD`, `_SOFTMAX_TEMPERATURE`와 `search.py`의 `TOP_K`, `SEARCH_THRESHOLD`도 여기에 통합 가능
- 모델 교체·임계값 튜닝 시 코드 수정 없이 JSON만 변경 가능

---

## 작업 순서 제안

| 순서 | 대상 | 변경 파일 | 이유 |
|------|------|-----------|------|
| 1 | NPC_ID_MAP (server.py) | server.py, npcs.json | npcs.json에 id 이미 존재, 중복 제거 효과 큼 |
| 2 | _JAILBREAK_RESPONSES (persona.py) | persona.py, npcs.json | npcs.json 단일 소스화 |
| 3 | _tone_rules 텍스트 (persona.py) | persona.py, npcs.json | NPC 추가 시 코드 수정 불필요 |
| 4 | _ROUTES (router.py) | router.py, routes.json(신규) | 문장 추가·수정 편의성 |
| 5 | 설정 상수 통합 | llm.py, router.py, search.py, config.json(신규) | 튜닝 편의성 |
| 6 | 프롬프트 지시문 | persona.py, prompts.json(신규) | 선택적 |
