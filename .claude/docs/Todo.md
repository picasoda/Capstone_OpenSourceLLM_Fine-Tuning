# 게임 NPC RAG 챗봇 — TODO

## 1. 환경 구성

- [x] Python 3.10 환경 준비 (현재 3.8이라 일부 라이브러리 호환 문제 발생 가능)
  - conda 환경 `llm_env`로 Python 3.10 사용
- [x] 작업 폴더 `Chatbot/` 및 하위 폴더 생성
  - `data/`, `db/`, `src/`
- [x] `requirements.txt` 작성 및 설치
  - chromadb, sentence-transformers, semantic-router, ollama, fastapi, uvicorn
- [x] Ollama에서 `qwen3.5:9b` 모델 pull 확인
- [x] HuggingFace 캐시 경로(`HF_HOME`)를 볼륨으로 지정

---

## 2. 게임 데이터 작성 (`data/`)

- [x] `items.json` 작성 (common / detail 분리 구조)
  - id, name, category, common, detail
  - 30~50개
- [x] `npcs.json` 작성 (영주, 약초상, 대장장이)
  - 이름, 성격, 말투, 배경
  - knowledge_scope, detail_categories
  - 라우트별 최후 수단 고정 응답
- [x] `locations.json` 작성 (common / detail 분리)
  - 10~15개
- [x] `worldlore.json` 작성
  - 5~10개

---

## 3. 임베딩 모델 공용 로더 (`src/embedder.py`)

- [x] `BAAI/bge-m3` 모델 단일 로드 (싱글톤)
- [x] 라우터와 RAG에서 import해서 공유

---

## 4. Semantic Router (`src/router.py`)

- [x] 라우트 4종 정의 (item_query, npc_query, location_query, jailbreak)
  - 라우트당 예시 문장 10~15개
  - 정보 질문 라우트에는 잡담 섞인 변형도 포함
- [x] chitchat은 default 처리 (예시 없음)
- [x] `ROUTER_THRESHOLD = 0.4` 미달 시 chitchat으로 fallback
- [x] 입력 → 라우트 변수 반환 함수 작성

---

## 5. 벡터 DB 및 검색 <- 현재 (`src/ingest.py`, `src/search.py`)

### 5.1 색인 (`ingest.py`)
- [ ] ChromaDB 클라이언트 초기화 (`./db/`)
- [ ] 컬렉션 4개 생성: items, npcs, locations, lore
- [ ] JSON → 문서 변환 (아이템은 common + detail 합쳐서 임베딩)
- [ ] 메타데이터에 category 포함
- [ ] 색인 스크립트 1회 실행

### 5.2 검색 (`search.py`)
- [ ] `search_item(query, npc)`, `search_npc(query, npc)`, `search_location(query, npc)` 작성
- [ ] `TOP_K = 3`, `SEARCH_THRESHOLD = 0.4` 적용
- [ ] 검색 결과 0개 신호 반환 로직
- [ ] NPC 권한 필터링 함수 (`filter_by_permission`)
  - common_only / category_detail / 카테고리 불일치 분기

---

## 6. LLM 연동 (`src/llm.py`)

- [ ] Ollama 클라이언트 래퍼 함수 작성
- [ ] 시스템 프롬프트 + 유저 메시지 → 응답
- [ ] temperature, max_tokens 등 파라미터 인자화
- [ ] 호출 실패 시 재시도 로직

---

## 7. NPC 페르소나 및 프롬프트 (`src/persona.py`)

- [ ] `npcs.json` 로드 함수
- [ ] 라우트별 시스템 프롬프트 빌더
  - chitchat용
  - item_query용
  - npc_query용
  - location_query용
  - jailbreak용
- [ ] 응답 톤 규칙 프롬프트에 포함
  - 약초상이 무기 질문 → 대장장이로 유도
  - 대장장이가 약초 질문 → 약초상으로 유도
  - 영주는 디테일 모름 명시
- [ ] 상황별 추가 프롬프트 함수
  - 검색 결과 없음 → "모른다고 답하라" 지시 추가
  - 권한 밖 카테고리(common만) → "전문가에게 유도하라" 지시 추가

---

## 8. 챗봇 메인 로직 (`src/chatbot.py`)

- [ ] 메인 chat 함수 작성
  - 입력 → router 호출 → 라우트 변수 결정
- [ ] 라우트별 분기 처리
  - chitchat → chitchat 프롬프트 + LLM
  - jailbreak → jailbreak 프롬프트 + LLM
  - item/npc/location_query → search 호출 → 권한 필터링 → 상황별 추가 프롬프트 결합 → LLM
- [ ] LLM 에러 시 재시도 → 실패하면 최후 수단 고정 응답 반환

---

## 9. API 서버 (`src/server.py`)

- [ ] FastAPI 앱 초기화
- [ ] POST `/chat` 엔드포인트 (`{npc, message}` → `{response}`)
- [ ] GET `/health` 엔드포인트
- [ ] uvicorn 실행 (`0.0.0.0:8000`)
