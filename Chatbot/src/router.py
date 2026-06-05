import json
import os

import numpy as np
from embedder import get_embedder

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "config.json")
_ROUTES_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "routes.json")

with open(_CONFIG_PATH, encoding="utf-8") as _f:
    _router_cfg = json.load(_f)["router"]

ROUTER_THRESHOLD: float = _router_cfg["threshold"]
# bge-m3는 배경 유사도가 높아 softmax로 라우트 간 상대적 우위를 비교함
_SOFTMAX_TEMPERATURE: float = _router_cfg["softmax_temperature"]

with open(_ROUTES_PATH, encoding="utf-8") as _f:
    _ROUTES: dict[str, list[str]] = json.load(_f)

# 라우트 인덱스 (지연 초기화)
_embeddings: np.ndarray | None = None
_labels: list[str] = []


def _build_index() -> None:
    global _embeddings, _labels
    model = get_embedder()
    sentences: list[str] = []
    labels: list[str] = []
    for route, utterances in _ROUTES.items():
        for utt in utterances:
            sentences.append(utt)
            labels.append(route)
    _embeddings = model.encode(sentences, normalize_embeddings=True)
    _labels = labels


def classify(query: str) -> list[str]:
    """임계값 이상인 모든 라우트를 반환한다.

    - jailbreak 포함 시 즉시 ["jailbreak"] 반환
    - 임계값 이상 라우트가 없으면 ["chitchat"] 반환
    """
    global _embeddings, _labels
    if _embeddings is None:
        _build_index()

    model = get_embedder()
    q_emb = model.encode([query], normalize_embeddings=True)[0]

    # 코사인 유사도 (정규화된 벡터의 내적)
    raw: np.ndarray = _embeddings @ q_emb

    # 라우트별 평균 유사도 계산
    route_names: list[str] = list(_ROUTES.keys())
    means: list[float] = []
    idx = 0
    for route in route_names:
        n = len(_ROUTES[route])
        means.append(float(np.mean(raw[idx : idx + n])))
        idx += n

    # softmax로 상대적 우위를 확률로 변환 (bge-m3 배경 유사도 보정)
    arr = np.array(means) / _SOFTMAX_TEMPERATURE
    probs = np.exp(arr - arr.max())
    probs /= probs.sum()

    matched = [
        route_names[i] for i, p in enumerate(probs) if float(p) >= ROUTER_THRESHOLD
    ]

    if not matched:
        return ["chitchat"]

    if "jailbreak" in matched:
        return ["jailbreak"]

    return matched
