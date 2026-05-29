## Python 환경

### 가상환경 위치
```
Capstone_OpenSourceLLM_Fine-Tuning/llm_env/   # 프로젝트 루트 내 venv
```

### 활성화 방법 (PowerShell)
```powershell
# 프로젝트 루트에서
llm_env\Scripts\Activate.ps1
```

- 모든 패키지(chromadb, sentence-transformers, fastapi 등)가 이 venv에 설치됨
- 스크립트 실행 전 반드시 활성화 필요

---

## 환경변수

### HF_HOME (HuggingFace 캐시 경로)
- `Chatbot/.env`에 정의: `HF_HOME=C:\Users\wormq\.cache\huggingface`
- `embedder.py`가 import될 때 `load_dotenv()`로 자동 로드됨
- bge-m3 캐시 위치: `C:\Users\wormq\.cache\huggingface\hub\models--BAAI--bge-m3`

### OLLAMA_MODELS
- Ollama는 로컬에서 실행 중 (`ollama list`로 확인)
- 현재 모델: `qwen3.5:4b`

---

## 스크립트 실행 방법

```powershell
# 프로젝트 루트에서 가상환경 활성화
llm_env\Scripts\Activate.ps1

# Chatbot/ 디렉터리로 이동 (상대경로 기준점)
cd Chatbot

# 색인 (1회)
python src/ingest.py

# 서버 실행
python src/server.py
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

---

## 알려진 경고 (무시 가능)

```
Warning: You are sending unauthenticated requests to the HF Hub.
```
- 이미 캐시된 모델은 재다운로드 없이 로드됨
- `HF_TOKEN` 없어도 동작에 지장 없음
