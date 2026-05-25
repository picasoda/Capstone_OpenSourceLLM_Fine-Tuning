from __future__ import annotations

import json
import os
import sys

import chromadb

sys.path.insert(0, os.path.dirname(__file__))
from embedder import get_embedder

DB_DIR = os.path.join(os.path.dirname(__file__), "..", "db")
NPC_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "npcs.json")

TOP_K = 3
SEARCH_THRESHOLD = 0.4

_client: chromadb.Client | None = None


def _get_client() -> chromadb.Client:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=DB_DIR)
    return _client


def _load_npc(npc_name: str) -> dict:
    with open(NPC_DATA_PATH, encoding="utf-8") as f:
        npcs = json.load(f)
    for npc in npcs:
        if npc["name"] == npc_name:
            return npc
    raise ValueError(f"NPC '{npc_name}' not found")


def _query_collection(collection_name: str, query: str) -> list[dict]:
    embedder = get_embedder()
    client = _get_client()
    collection = client.get_collection(collection_name)

    query_embedding = embedder.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K,
        include=["metadatas", "distances"],
    )

    hits = []
    for meta, dist in zip(results["metadatas"][0], results["distances"][0]):
        # ChromaDB distance: L2 or cosine. bge-m3 uses cosine → distance = 1 - similarity
        similarity = 1.0 - dist
        if similarity >= SEARCH_THRESHOLD:
            hits.append({"metadata": meta, "score": similarity})

    return hits


def filter_by_permission(hits: list[dict], npc: dict) -> list[dict]:
    scope = npc.get("knowledge_scope", "common_only")
    detail_categories = set(npc.get("detail_categories", []))

    filtered = []
    for hit in hits:
        meta = hit["metadata"]
        category = meta.get("category", "")

        if scope == "common_only":
            filtered.append({
                "name": meta.get("name", ""),
                "content": meta.get("common", ""),
                "score": hit["score"],
                "permission": "common_only",
            })
        elif scope == "category_detail":
            if category and category in detail_categories:
                filtered.append({
                    "name": meta.get("name", ""),
                    "content": meta.get("common", "") + "\n" + meta.get("detail", ""),
                    "score": hit["score"],
                    "permission": "full",
                    "category": category,
                })
            else:
                filtered.append({
                    "name": meta.get("name", ""),
                    "content": meta.get("common", ""),
                    "score": hit["score"],
                    "permission": "common_only",
                    "category": category,
                })
        else:
            filtered.append({
                "name": meta.get("name", ""),
                "content": meta.get("common", ""),
                "score": hit["score"],
                "permission": "common_only",
            })

    return filtered


def search_item(query: str, npc: str) -> list[dict]:
    hits = _query_collection("items", query)
    if not hits:
        return []
    npc_data = _load_npc(npc)
    return filter_by_permission(hits, npc_data)


def search_npc(query: str, npc: str) -> list[dict]:
    hits = _query_collection("npcs", query)
    if not hits:
        return []
    # NPC 정보는 항상 common 수준으로 반환
    return [
        {
            "name": h["metadata"].get("name", ""),
            "content": (
                h["metadata"].get("personality", "") + " " +
                h["metadata"].get("background", "")
            ).strip(),
            "score": h["score"],
            "permission": "common_only",
        }
        for h in hits
    ]


def search_location(query: str, npc: str) -> list[dict]:
    hits = _query_collection("locations", query)
    if not hits:
        return []
    # 장소는 모든 NPC에게 common 수준으로 반환
    return [
        {
            "name": h["metadata"].get("name", ""),
            "content": h["metadata"].get("common", ""),
            "score": h["score"],
            "permission": "common_only",
        }
        for h in hits
    ]
