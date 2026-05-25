from __future__ import annotations

import os
import sys

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# .env에서 HF_HOME 등 환경변수를 자동 로드 (이미 설정된 값은 덮어쓰지 않음)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"), override=False)

_model: SentenceTransformer | None = None

MODEL_NAME = "BAAI/bge-m3"


def get_embedder() -> SentenceTransformer:
    global _model
    if _model is None:
        hf_home = os.environ.get("HF_HOME")
        if hf_home:
            os.environ["HF_HOME"] = hf_home
        try:
            _model = SentenceTransformer(MODEL_NAME)
        except Exception as e:
            print(f"[embedder] 모델 로드 실패 ({MODEL_NAME}): {e}", file=sys.stderr)
            sys.exit(1)
    return _model
