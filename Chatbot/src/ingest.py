from __future__ import annotations

import json
import os
import sys

import chromadb

sys.path.insert(0, os.path.dirname(__file__))
from embedder import get_embedder

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DB_DIR = os.path.join(os.path.dirname(__file__), "..", "db")


def _load_json(filename: str) -> list:
    path = os.path.join(DATA_DIR, filename)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


COSINE_METADATA = {"hnsw:space": "cosine"}


def _get_or_create(client: chromadb.Client, name: str):
    try:
        return client.get_collection(name)
    except Exception:
        return client.create_collection(name, metadata=COSINE_METADATA)


def ingest_items(client: chromadb.Client, embedder) -> None:
    collection = _get_or_create(client, "items")
    existing_ids = set(collection.get()["ids"])

    items = _load_json("items.json")
    ids, documents, embeddings, metadatas = [], [], [], []

    for item in items:
        if item["id"] in existing_ids:
            continue
        text = f"{item['common']} {item['detail']}"
        ids.append(item["id"])
        documents.append(text)
        embeddings.append(embedder.encode(text).tolist())
        metadatas.append({
            "name": item["name"],
            "category": item["category"],
            "common": item["common"],
            "detail": item["detail"],
        })

    if ids:
        collection.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
        print(f"[ingest] items: {len(ids)}개 추가")
    else:
        print("[ingest] items: 이미 색인됨, 건너뜀")


def ingest_npcs(client: chromadb.Client, embedder) -> None:
    collection = _get_or_create(client, "npcs")
    existing_ids = set(collection.get()["ids"])

    npcs = _load_json("npcs.json")
    ids, documents, embeddings, metadatas = [], [], [], []

    for npc in npcs:
        if npc["id"] in existing_ids:
            continue
        text = f"{npc['name']} {npc['personality']} {npc['background']}"
        ids.append(npc["id"])
        documents.append(text)
        embeddings.append(embedder.encode(text).tolist())
        metadatas.append({
            "name": npc["name"],
            "personality": npc["personality"],
            "tone": npc["tone"],
            "background": npc["background"],
        })

    if ids:
        collection.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
        print(f"[ingest] npcs: {len(ids)}개 추가")
    else:
        print("[ingest] npcs: 이미 색인됨, 건너뜀")


def ingest_locations(client: chromadb.Client, embedder) -> None:
    collection = _get_or_create(client, "locations")
    existing_ids = set(collection.get()["ids"])

    locations = _load_json("locations.json")
    ids, documents, embeddings, metadatas = [], [], [], []

    for loc in locations:
        if loc["id"] in existing_ids:
            continue
        text = f"{loc['common']} {loc.get('detail', '')}"
        ids.append(loc["id"])
        documents.append(text)
        embeddings.append(embedder.encode(text).tolist())
        metadatas.append({
            "name": loc["name"],
            "common": loc["common"],
            "detail": loc.get("detail", ""),
        })

    if ids:
        collection.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
        print(f"[ingest] locations: {len(ids)}개 추가")
    else:
        print("[ingest] locations: 이미 색인됨, 건너뜀")


def ingest_lore(client: chromadb.Client, embedder) -> None:
    collection = _get_or_create(client, "lore")
    existing_ids = set(collection.get()["ids"])

    lore = _load_json("worldlore.json")
    ids, documents, embeddings, metadatas = [], [], [], []

    for entry in lore:
        if entry["id"] in existing_ids:
            continue
        text = entry["common"]
        ids.append(entry["id"])
        documents.append(text)
        embeddings.append(embedder.encode(text).tolist())
        metadatas.append({
            "name": entry["name"],
            "common": entry["common"],
        })

    if ids:
        collection.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
        print(f"[ingest] lore: {len(ids)}개 추가")
    else:
        print("[ingest] lore: 이미 색인됨, 건너뜀")


def run_ingest() -> None:
    embedder = get_embedder()
    client = chromadb.PersistentClient(path=DB_DIR)

    ingest_items(client, embedder)
    ingest_npcs(client, embedder)
    ingest_locations(client, embedder)
    ingest_lore(client, embedder)

    print("[ingest] 색인 완료")


if __name__ == "__main__":
    run_ingest()
