# 게임 NPC RAG 챗봇 — Feature 명세

## Feature 1. 게임 데이터 관리

### 1.1 아이템 데이터
- 파일: `data/items.json`
- 구조: 공통 정보(common)와 상세 정보(detail) 분리
- 필드
  - id, name, category (예: herb, potion, weapon, armor)
  - common: 일반인이 알 만한 정보 (외형 설명, 대략적 용도, 일반 획득처)
  - detail: 전문가만 아는 정보 (제작 레시피, 정확한 수치, 부작용 등)
- 규모: 30~50개
- *정보필요*: 실제 아이템 항목 데이터

### 1.2 NPC 데이터
- 파일: `data/npcs.json`
- 등장 NPC: 영주, 약초상, 대장장이 (3명)
- 필드: 이름, 성격, 말투, 배경
- 권한 필드
  - knowledge_scope: 컬렉션별 접근 수준 (`common_only` / `category_detail`)
  - detail_categories: 상세 정보 접근 가능한 아이템 카테고리 목록
- NPC별 권한
  - 영주: 모든 컬렉션 접근 가능, 단 전부 common_only
  - 약초상: items는 category_detail (herb, potion만 상세), 나머지는 common_only
  - 대장장이: items는 category_detail (weapon, armor만 상세), 나머지는 common_only
- *정보필요*: NPC별 성격, 말투, 배경 세부 내용

### 1.3 장소 데이터
- 파일: `data/locations.json`
- 구조: common / detail 분리
- 규모: 10~15개
- *정보필요*: 실제 장소 항목 데이터, common/detail 분리 기준

### 1.4 세계관 데이터
- 파일: `data/worldlore.json`
- 구조: common 정보 위주
- 규모: 5~10개
- *정보필요*: 실제 세계관 항목 데이터

---

## Feature 2. 임베딩 모델 공용 로더

### 2.1 단일 로드
- 파일: `src/embedder.py`
- `BAAI/bge-m3` 모델을 한 번만 로드하여 라우터와 RAG에서 공유
- 메모리 중복 방지

---

## Feature 3. Semantic Router

### 3.1 입력 분류
- 인코더: 공용 임베딩 모델 사용
- 플레이어 입력을 임베딩하여 등록된 라우트와 유사도 비교
- 가장 가까운 라우트 이름을 분기 변수로 반환
- 어떤 라우트와도 임계값(SIMILARITY_THRESHOLD = 0.4) 이상 가깝지 않으면 chitchat으로 fallback

### 3.2 라우트 종류
- item_query: 아이템 관련 질문
- npc_query: NPC 관련 질문
- location_query: 장소 관련 질문
- jailbreak: 시스템 조작 시도, 시대 부적합 발언 (현대 기술, AI 언급 등)
- chitchat: 명시적 예시 없음, 위 라우트에 분류되지 않은 모든 입력의 기본값

### 3.3 혼합 입력 처리
- 정보 질문 라우트의 예시에는 순수 질문과 잡담이 섞인 변형 모두 포함
- 정보 질문이 감지되면 그쪽으로 우선 라우팅

### 3.4 라우트별 예시 문장
- 라우트당 10~15개 등록 (chitchat 제외)
- *정보필요*: item_query, npc_query, location_query, jailbreak 각각의 예시 문장

---

## Feature 4. 벡터 DB 및 검색

### 4.1 임베딩 및 색인
- 벡터 DB: ChromaDB (`./db/`)
- 컬렉션 분리: items, npcs, locations, lore
- 아이템 색인 시 common + detail을 합친 텍스트로 임베딩
- 메타데이터에 category 포함

### 4.2 카테고리별 검색 함수
- `search_item(query, npc)`, `search_npc(query, npc)`, `search_location(query, npc)`
- 공통 파라미터: `TOP_K = 3`, `SIMILARITY_THRESHOLD = 0.4`
- 임계값 미달 결과는 제외
- 검색 결과가 0개인 경우 "정보 없음" 신호 반환

### 4.3 데이터 레벨 권한 필터링
- 검색 후 NPC의 knowledge_scope에 따라 반환 필드 결정
  - common_only → common 필드만 반환
  - category_detail + 아이템 카테고리가 detail_categories에 포함 → common + detail 반환
  - category_detail + 카테고리 불일치 → common만 반환
- 권한 밖 정보는 데이터 단계에서 잘려나가므로 LLM은 애초에 보지 못함

---

## Feature 5. LLM 연동

### 5.1 Ollama 클라이언트
- 모델: `qwen3.5:9b`
- 시스템 프롬프트 + 유저 메시지 전달 후 응답 수신
- temperature, max_tokens 등 파라미터 조정 가능

---

## Feature 6. NPC 페르소나 및 응답 규칙

### 6.1 라우트별 시스템 프롬프트
- NPC 데이터(이름, 성격, 말투, 배경)를 베이스로, 라우트별 지시를 결합한 프롬프트 구성
- 라우트별 프롬프트
  - chitchat: 잡담/인사용 가벼운 톤, 참고 정보 없음
  - item_query: 아이템 정보 응답용
  - npc_query: 다른 NPC 정보 응답용
  - location_query: 장소 정보 응답용
- jailbreak는 LLM 미사용 (고정 응답)
- *정보필요*: 각 라우트별 프롬프트 본문

### 6.2 응답 톤 규칙 (프롬프트에 포함)
- 데이터 레벨 필터링으로 common만 받은 경우, 디테일은 모른다고 답하거나 전문가에게 유도하도록 지시
  - 약초상이 무기 질문: common만 답하고 대장장이로 유도
  - 대장장이가 약초 질문: common만 답하고 약초상으로 유도
  - 영주: 모든 질문에 디테일은 모른다고 답변

### 6.3 상황별 추가 프롬프트
- 정보 질문 라우트(item_query / npc_query / location_query)에서 다음 조건 발생 시
  라우트별 기본 프롬프트에 추가 지시를 덧붙여 LLM 호출
- 조건과 추가 지시
  - 검색 결과 0개 또는 검색 결과가 모두 검색 임계값 미달 (라우터 임계값과 별개)
    → "참고할 정보가 없으니, NPC 말투로 자연스럽게 모른다고 답하라"
  - 권한 밖 카테고리 질문 (common만 반환된 경우)
    → "디테일은 모르는 상태로, 전문가 NPC에게 가보라고 유도하라"

---

## Feature 7. 챗봇 메인 로직

### 7.1 파이프라인
입력 → Feature 3(라우터)로 분류 → 라우트 변수에 따라 Feature 4(검색/필터링)와 Feature 6(라우트별 프롬프트) 호출 → 응답 반환

### 7.2 Fallback 처리
- Feature 6.3의 트리거 조건 충족 시 LLM 호출 없이 Fallback 응답 반환

---

## Feature 8. API 서버(8.2주소 부분 수정예정)

### 8.1 엔드포인트
- POST `/chat`: 입력 `{npc, message}` → 출력 `{response}`
- GET `/health`: 서버 상태 확인

### 8.2 실행
- FastAPI + uvicorn
- 호스트 `0.0.0.0`, 포트 `8000`
