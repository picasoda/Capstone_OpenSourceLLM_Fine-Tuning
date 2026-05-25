import os
import sys
from sentence_transformers import SentenceTransformer

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
