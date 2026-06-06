from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

_NPC_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "npcPrompt.json")
with open(_NPC_DATA_PATH, encoding="utf-8") as _f:
    _CATEGORY_EXPERTS: dict[str, str] = {
        cat: npc["name"]
        for npc in json.load(_f)
        for cat in npc.get("detail_categories", [])
    }

from llm import generate
from persona import (
    append_no_result_instruction,
    append_permission_instruction,
    build_chitchat_prompt,
    build_combined_query_prompt,
    build_jailbreak_prompt,
    get_npc,
)
from router import classify
from search import search_item, search_location, search_lore, search_npc


def _format_context(results: list[dict]) -> str:
    return "\n".join(f"- {r['name']}: {r['content']}" for r in results)


def _has_permission_gap(results: list[dict], npc: dict) -> bool:
    """전문가 NPC가 권한 밖 카테고리 결과를 받은 경우."""
    if not npc.get("detail_categories"):
        return False
    return any(r.get("permission") == "common_only" for r in results)


def _get_redirect_expert(results: list[dict], npc: dict) -> str | None:
    """권한 밖 카테고리를 담당하는 전문가 NPC명 반환."""
    npc_name = npc["name"]
    experts: set[str] = set()
    for r in results:
        if r.get("permission") == "common_only":
            expert = _CATEGORY_EXPERTS.get(r.get("category", ""))
            if expert and expert != npc_name:
                experts.add(expert)
    return ", ".join(experts) if experts else None


_SEARCH_FN = {
    "item_query": search_item,
    "npc_query": search_npc,
    "location_query": search_location,
    "lore_query": search_lore,
}

_CONTEXT_LABEL = {
    "item_query": "item",
    "npc_query": "npc",
    "location_query": "location",
    "lore_query": "lore",
}


def chat(npc_name: str, message: str) -> str:
    npc = get_npc(npc_name)
    routes = classify(message)

    if routes == ["jailbreak"]:
        return build_jailbreak_prompt(npc_name)

    if routes == ["chitchat"]:
        prompt = build_chitchat_prompt(npc_name)
        try:
            return generate(prompt, message)
        except RuntimeError:
            return npc["fallback_response"]

    # 정보 라우트: 각 라우트마다 검색 후 컨텍스트 합산
    contexts: dict[str, str] = {}
    has_permission_gap = False
    redirect_expert: str | None = None
    all_empty = True

    for route in routes:
        results = _SEARCH_FN[route](message, npc_name)
        label = _CONTEXT_LABEL[route]

        if results:
            all_empty = False
            contexts[label] = _format_context(results)
            if route == "item_query" and _has_permission_gap(results, npc):
                has_permission_gap = True
                redirect_expert = _get_redirect_expert(results, npc)
        else:
            contexts[label] = ""

    prompt = build_combined_query_prompt(npc_name, contexts)

    if all_empty:
        prompt = append_no_result_instruction(prompt)
    elif has_permission_gap:
        prompt = append_permission_instruction(prompt, redirect_expert)

    try:
        return generate(prompt, message)
    except RuntimeError:
        return npc["fallback_response"]
