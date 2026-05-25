## Python 환경

### 실제 사용 인터프리터
```
/volume/Capstone_OpenSourceLLM_Fine-Tuning/llm_env/bin/python3   # Python 3.13.13
```
- PATH 최우선이므로 `python3` 명령 = 이 인터프리터
- 모든 패키지(chromadb, sentence-transformers, fastapi 등)가 여기에 설치됨
- **스크립트 실행 시 별도 conda activate 불필요**, 그냥 `python3` 사용

### 절대 사용 금지
```
/root/miniconda/envs/llm_env/bin/python   # Python 3.10, 패키지 전무
conda run -n llm_env python ...           # 위와 동일한 빈 환경 호출
```
- 이름이 `llm_env`로 같아 혼동 발생
- 패키지가 하나도 없어 import 오류 발생

---

## 환경변수

### HF_HOME (HuggingFace 캐시 경로)
- `Chatbot/.env`에 정의: `HF_HOME=/volume/Capstone_OpenSourceLLM_Fine-Tuning/hf_cache`
- `embedder.py`가 import될 때 `load_dotenv()`로 자동 로드됨
- **셸에서 직접 실행할 때도 prefix 불필요** (embedder import 시 자동 처리)
- bge-m3 캐시 위치: `hf_cache/hub/models--BAAI--bge-m3`

### OLLAMA_MODELS
- `Chatbot/.env`에 정의: `/volume/Capstone_OpenSourceLLM_Fine-Tuning/ollama_models`
- Ollama는 서비스로 실행 중 (`ollama list`로 확인)
- 현재 모델: `qwen3.5:9b` (6.6GB)

---

## 스크립트 실행 방법

```bash
# Chatbot/ 디렉터리에서 실행 (상대경로 기준점)
cd /volume/Capstone_OpenSourceLLM_Fine-Tuning/Chatbot

# 색인 (1회)
python3 src/ingest.py

# 서버 실행 (6단계 이후)
python3 src/server.py
```

**주의**: `src/` 안의 스크립트는 `sys.path.insert(0, os.path.dirname(__file__))`로  
`from embedder import get_embedder` 형태의 상대 import를 처리합니다.  
`Chatbot/` 디렉터리가 아닌 다른 곳에서 실행하면 경로가 어긋납니다.

---

## 설치 패키지 (llm_env venv)

| 패키지 | 버전 |
|--------|------|
| chromadb | 1.5.9 |
| sentence-transformers | 5.5.1 |
| semantic-router | 0.1.14 |
| ollama | 0.6.2 |
| fastapi | 0.136.1 |
| uvicorn | 0.47.0 |
| python-dotenv | (설치됨) |
| torch | 2.12.0+cu130 |
| numpy | 2.4.6 |

---

## 알려진 경고 (무시 가능)

```
UserWarning: CUDA initialization: The NVIDIA driver on your system is too old
```
- GPU 드라이버(12090)가 PyTorch 요구 버전보다 낮음
- CPU로 fallback되어 동작에는 문제없음
- bge-m3 인코딩은 CPU로 정상 실행됨

```
Warning: You are sending unauthenticated requests to the HF Hub.
```
- 이미 캐시된 모델은 재다운로드 없이 로드됨
- `HF_TOKEN` 없어도 동작에 지장 없음
