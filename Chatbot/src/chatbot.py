from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from llm import generate
from persona import (
    append_no_result_instruction,
    append_permission_instruction,
    build_chitchat_prompt,
    build_item_query_prompt,
    build_jailbreak_prompt,
    build_location_query_prompt,
    build_npc_query_prompt,
    get_npc,
)
from router import classify
from search import search_item, search_location, search_npc


def _format_context(results: list[dict]) -> str:
    return "\n".join(f"- {r['name']}: {r['content']}" for r in results)


def _has_permission_gap(results: list[dict], npc: dict) -> bool:
    """category_detail NPC가 권한 밖 카테고리 결과를 받은 경우."""
    if npc.get("knowledge_scope") != "category_detail":
        return False
    return any(r.get("permission") == "common_only" for r in results)


def chat(npc_name: str, message: str) -> str:
    npc = get_npc(npc_name)

    route = classify(message)

    # jailbreak: LLM 미사용, 고정 응답 반환
    if route == "jailbreak":
        return build_jailbreak_prompt(npc_name)

    # 프롬프트 결정
    if route == "chitchat":
        prompt = build_chitchat_prompt(npc_name)
    elif route == "item_query":
        results = search_item(message, npc_name)
        prompt = build_item_query_prompt(npc_name, _format_context(results))
        if not results:
            prompt = append_no_result_instruction(prompt)
        elif _has_permission_gap(results, npc):
            prompt = append_permission_instruction(prompt)
    elif route == "npc_query":
        results = search_npc(message, npc_name)
        prompt = build_npc_query_prompt(npc_name, _format_context(results))
        if not results:
            prompt = append_no_result_instruction(prompt)
    elif route == "location_query":
        results = search_location(message, npc_name)
        prompt = build_location_query_prompt(npc_name, _format_context(results))
        if not results:
            prompt = append_no_result_instruction(prompt)
    else:
        prompt = build_chitchat_prompt(npc_name)

    try:
        return generate(prompt, message)
    except RuntimeError:
        return npc["fallback_response"]
