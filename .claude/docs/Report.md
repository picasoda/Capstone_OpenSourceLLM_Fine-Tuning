# 설계 결정 보고서

각 단계에서 왜 그런 선택을 했는지 기록한 문서입니다.

---

## 1단계 — 환경 구성

### 실제 사용 Python 환경
프로젝트 루트의 `llm_env\` 로컬 venv를 사용합니다 (Python 3.12.4).

활성화:
```
llm_env\Scripts\activate.bat
```

### HF_HOME 설정
`Chatbot/.env`에 `HF_HOME=C:\Users\wormq\.cache\huggingface`로 정의됩니다. `embedder.py` import 시 `load_dotenv()`로 자동 로드되므로 별도 주입 불필요합니다.

---

## 2단계 — 게임 데이터 작성

### common / detail 분리 이유
NPC별 정보 접근 권한을 데이터 레벨에서 구현하기 위함입니다. LLM에 전달하기 전에 search.py가 권한 밖 정보(`detail`)를 잘라내므로, LLM이 권한 외 정보를 절대 볼 수 없습니다. 프롬프트 수준의 접근 제어보다 훨씬 확실합니다.

### category 필드 이유
약초상은 `herb/potion`의 detail만, 대장장이는 `weapon/armor`의 detail만 접근 가능합니다. 검색 결과에 category 메타데이터가 없으면 이 분기가 불가능하므로, 색인 시 반드시 포함해야 합니다.

---

## 3단계 — embedder.py (싱글톤 임베딩 로더)

### 싱글톤 패턴 이유
`BAAI/bge-m3`는 로드 시 약 2~3GB 메모리를 사용합니다. router.py와 search.py 둘 다 임베딩이 필요한데, 각자 독립 로드하면 메모리가 2배 소비됩니다. `get_embedder()`를 통해 프로세스 내 단 1회만 로드합니다.

### bge-m3 선택 이유
한국어 성능이 우수한 다국어 모델입니다. 라우팅(router.py)과 RAG 검색(search.py)에 동일 모델을 쓰므로 임베딩 공간이 일치해 검색 품질이 보장됩니다.

---

## 4단계 — router.py (Semantic Router)

### semantic-router 라이브러리 미사용 이유
설치된 버전(0.1.2)이 `RouteLayer`, `BaseEncoder` 등 예전 API를 지원하지 않아 사용 불가 상태였습니다. 라우팅 로직 자체는 단순하므로 numpy 기반으로 직접 구현했습니다.

### 예시 문장 전략
- **아이템명 미포함**: 라우터의 역할은 의도(intent) 분류이지 개체명 인식이 아닙니다. 특정 아이템명을 넣으면 그 이름에만 과적합되어, 데이터에 없는 새 아이템 질문에 취약해집니다.
- **패턴 위주 단문**: `"이거 어디서 구해?"`, `"만드는 법 알아?"` 처럼 의도 패턴만 담습니다.
- **잡담 섞인 변형 포함**: `"저기, 이것 어디서 구할 수 있는지 알아?"` 처럼 실제 대화체 변형도 등록해 혼합 입력에 강하게 합니다.

### ROUTER_THRESHOLD = 0.4 + softmax 보정
bge-m3는 한국어 문장 간 코사인 유사도가 전반적으로 높아(0.4~0.6), 순수 임계값(0.4)을 적용하면 chitchat 질문도 모두 라우트로 분류됩니다.

해결 방법: 라우트별 평균 유사도에 softmax(T=0.1)를 적용해 **확률(0~1)**로 변환합니다.
- chitchat 쿼리: 모든 라우트 유사도가 비슷 → softmax 확률이 고르게 분산 → 최대값 ≈ 0.25~0.35 → 0.4 미달 → chitchat 반환
- 정보 쿼리: 해당 라우트 유사도만 높음 → 해당 라우트 확률이 집중 → 최대값 ≈ 0.40~0.70 → 정상 라우팅

0.4 상수의 의미가 "라우트 4개 중 확실히 우위인가"로 재해석됩니다(랜덤 확률 = 0.25, 임계값 = 0.4).

### jailbreak 예시 주의사항
한국어 명령형 어미(~해줘, ~대답해, ~봐)를 쓰는 예시는 일반 잡담과 임베딩 공간이 겹칩니다. 이 때문에 "별로 할 말 없네" 같은 chitchat이 jailbreak로 오분류되는 현상이 발생했고, 원인 예시를 교체해 해결했습니다.

---

---

## 5단계 — ingest.py / search.py (벡터 DB 및 검색)

### ChromaDB cosine 메트릭 필수 지정 이유
chromadb 기본 거리 함수는 L2(유클리드)입니다. bge-m3가 반환하는 임베딩은 정규화된 단위 벡터이므로 cosine 거리 함수를 사용해야 합니다.

L2 거리로 컬렉션을 생성하면:
- 실제 cosine 유사도 0.53인 문서 쌍의 L2 거리 ≈ 0.97
- `similarity = 1 - 0.97 = 0.03` → SEARCH_THRESHOLD(0.4) 미달 → 모든 결과 필터링

해결: 컬렉션 생성 시 `metadata={"hnsw:space": "cosine"}` 명시. cosine 메트릭에서 distance = 1 - cosine_similarity이므로 `similarity = 1 - distance` 계산이 올바르게 적용됩니다.

### Python 3.13에서 `X | None` 타입 힌트 런타임 오류
`chromadb.Client`는 클래스가 아닌 팩토리 함수이므로 `chromadb.Client | None` 표현식이 런타임 TypeError를 발생시킵니다. `from __future__ import annotations`를 파일 상단에 추가해 모든 어노테이션을 지연(string) 평가로 전환해 해결했습니다.

### filter_by_permission 설계
권한 필터링을 검색 단계에서 처리함으로써 LLM이 권한 외 정보를 절대 볼 수 없게 합니다.
- `common_only` NPC: 모든 아이템의 `common` 필드만 반환
- `category_detail` NPC + 해당 카테고리: `common + detail` 반환 (`permission: "full"`)
- `category_detail` NPC + 불일치 카테고리: `common`만 반환 (`permission: "common_only"`)

반환 딕셔너리에 `permission` 필드를 포함하여 chatbot.py에서 `append_permission_instruction` 적용 여부를 판단할 수 있도록 했습니다.

---

## 6단계 — llm.py (Ollama 래퍼)

### MAX_RETRIES = 3, RETRY_DELAY = 1.0s
LLM 호출은 네트워크/프로세스 일시 오류에 의해 간헐적으로 실패할 수 있습니다. 3회 재시도 + 1초 대기로 안정성을 높이되, 전부 실패 시 RuntimeError를 호출부(chatbot.py)로 전파합니다. fallback 처리는 LLM 래퍼의 책임이 아닙니다.

### response.message.content (dot notation)
ollama Python 라이브러리 0.6.x는 `ChatResponse` 데이터클래스를 반환합니다. `response['message']['content']` 딕셔너리 접근 대신 `response.message.content` dot notation을 사용해 타입 힌트와 IDE 지원을 활용합니다.

---

## 7단계 — persona.py (NPC 프롬프트 빌더)

### build_jailbreak_prompt가 LLM 프롬프트가 아닌 고정 응답 반환
jailbreak 입력에 LLM을 쓰면 LLM이 시스템 조작 시도에 노출됩니다. chatbot.md 규칙대로 jailbreak는 LLM 미사용, NPC 말투에 맞는 고정 문자열을 반환합니다. 함수 이름은 규칙 파일 명세를 그대로 따랐습니다.

### _tone_rules 분리
NPC별 유도 규칙(약초상↔대장장이 교차 유도, 영주 디테일 불가)은 모든 라우트 프롬프트에 공통 적용됩니다. `_base_prompt` + `_tone_rules`로 분리해 각 빌더 함수에서 결합하면 중복 없이 일관성을 유지할 수 있습니다.

### 상황별 추가 프롬프트를 별도 함수로
`append_no_result_instruction`, `append_permission_instruction`은 기존 프롬프트 문자열에 지시를 덧붙이는 순수 함수입니다. chatbot.py가 조건에 따라 선택적으로 호출하므로 persona.py는 빌딩 블록만 제공합니다.

---

## 8단계 — chatbot.py (메인 파이프라인)

### jailbreak에서 LLM 즉시 차단
jailbreak 라우트는 프롬프트 빌딩 없이 `build_jailbreak_prompt()`의 고정 문자열을 바로 반환합니다. LLM 호출 자체가 없으므로 어떠한 시스템 조작 시도도 모델에 전달되지 않습니다.

### _has_permission_gap: category_detail NPC + common_only 결과
권한 밖 유도 지시(`append_permission_instruction`)는 item_query에서만 의미 있습니다. npc_query·location_query는 search.py에서 항상 common_only를 반환하므로, `knowledge_scope == "category_detail"` 조건을 먼저 확인해 영주(common_only NPC)에게는 지시가 붙지 않도록 합니다.

### RuntimeError만 catch → NPC fallback 반환
router, search, persona 오류는 로직 버그이므로 상위로 전파합니다. LLM 재시도 전부 실패(RuntimeError)만 잡아 npcs.json의 `fallback_response`를 반환합니다. 이렇게 하면 예상치 못한 오류가 조용히 묻히지 않습니다.

---

## Todo 외 리팩터링 — JSON 분리 (2026-05-30)

### 하드코딩 데이터를 JSON으로 분리한 이유
코드 수정 없이 예시 문장·NPC 응답·설정값을 변경할 수 있도록, 파이썬 파일에 인라인으로 박혀 있던 데이터를 data/ 폴더 JSON 파일로 분리했습니다.

### routes.json 분리 (router.py → data/routes.json)
라우터 예시 문장 ~50개가 router.py에 하드코딩되어 있었습니다. 예시 추가·수정이 코드 파일 직접 편집을 요구했으므로, `data/routes.json`으로 분리하고 router.py는 startup 시 로드합니다.

### config.json 통합 (llm.py, router.py, search.py → data/config.json)
`MODEL`, `MAX_RETRIES`, `ROUTER_THRESHOLD`, `TOP_K` 등 튜닝 상수가 각 모듈에 분산되어 있었습니다. `data/config.json` 단일 파일로 통합해 모델 교체·임계값 조정 시 JSON 하나만 수정하면 됩니다.

### jailbreak_response, tone_rule 필드를 npcs.json으로 이동
`persona.py`의 `_JAILBREAK_RESPONSES` 딕셔너리와 `_tone_rules()` 함수 내 NPC별 분기 텍스트를 npcs.json의 각 NPC 객체 필드(`jailbreak_response`, `tone_rule`)로 이동했습니다. NPC가 추가될 때 persona.py 코드를 수정할 필요가 없어졌습니다.

### NPC_ID_MAP 동적 빌드 (server.py)
`NPC_ID_MAP`이 server.py에 하드코딩되어 npcs.json의 `id` 필드와 중복이었습니다. 서버 기동 시 npcs.json을 읽어 `{npc["id"]: npc["name"]}` 딕셔너리를 동적으로 구성하도록 변경했습니다. NPC 추가 시 server.py 수정 불필요.

### _base_prompt full_name 버그 수정 (persona.py)
`_base_prompt`가 존재하지 않는 `npc['full_name']` 필드를 참조하는 버그가 있었습니다. `npc['name'](npc['job'])` 형식(`아서(영주)`)으로 수정했습니다.

### 모델 변경 (qwen3.5:9b → qwen3.5:1.7b)
경량 모델로 교체. config.json에서 관리하므로 이후 변경은 JSON 수정으로 충분합니다.

---

## 9단계 — server.py (FastAPI 서버)

### 유니티 ID → 한글 이름 매핑
유니티 ScriptableObject의 NPC ID(`npc_arthur`, `npc_martha`, `npc_sten`, `npc_jasper`)가 내부 한글 이름과 다릅니다. server.py의 `NPC_ID_MAP` 딕셔너리에서 변환하므로 chatbot.py 이하 레이어는 한글 이름만 사용합니다. JSON id 형식(`npc_lord` 등)도 호환 허용합니다.

### Pydantic field_validator로 NPC 검증
허용되지 않은 NPC ID는 422 Unprocessable Entity를 반환합니다. FastAPI의 Pydantic 통합을 그대로 활용해 별도 if문 없이 검증합니다.

### 상인(jasper) 추가
유니티에 npc_jasper(예스퍼 상인)가 존재하나 기존 시스템에 없었습니다. `common_only` 권한으로 npcs.json에 추가했습니다. 전문 정보는 모르고 전문가에게 유도하는 역할입니다.

---

## Todo 외 작업 — Unity 외부 통신 환경 구성

### CORS 미들웨어 추가 (server.py)
Unity WebGL 빌드는 브라우저 컨텍스트에서 실행되어 CORS 정책이 적용됩니다. `allow_origins=["*"]`로 설정해 ngrok URL 포함 모든 출처를 허용했습니다. 스탠드얼론(Windows/Android 등)은 CORS 불필요이나 미리 적용해 WebGL 대응을 마쳤습니다.

### ngrok 선택 이유
로컬 FastAPI 서버(port 8000)를 Unity에서 접근하려면 공개 URL이 필요합니다. ngrok은 별도 서버 없이 터널링만으로 HTTPS 외부 URL을 제공하므로 개발 단계에서 가장 빠른 선택입니다. 무료 플랜은 재시작마다 URL이 바뀌므로 고정이 필요하면 ngrok static domain 또는 클라우드 배포로 전환이 필요합니다.

### 실행 순서 문서
`ollama.txt` (프로젝트 루트) — Ollama → FastAPI → ngrok → Unity 호출 순서 및 C# 예시 포함.

---
