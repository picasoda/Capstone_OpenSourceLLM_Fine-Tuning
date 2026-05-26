from __future__ import annotations

import json
import os

NPC_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "npcs.json")

_npc_cache: dict[str, dict] | None = None

# jailbreak 고정 응답 (LLM 미사용)
_JAILBREAK_RESPONSES: dict[str, str] = {
    "영주": "무슨 해괴한 소리를 하는 것이냐. 그런 이치에 닿지 않는 말은 삼가도록 하라.",
    "약초상": "아이고, 무슨 말씀을 하시는 건지 전혀 모르겠네요. 저는 약초만 알지, 그런 건 몰라요.",
    "대장장이": "뭔 소린지 하나도 모르겠다. 그런 거 묻지 마.",
}


def _load_npcs() -> dict[str, dict]:
    global _npc_cache
    if _npc_cache is None:
        with open(NPC_DATA_PATH, encoding="utf-8") as f:
            npcs = json.load(f)
        _npc_cache = {npc["name"]: npc for npc in npcs}
    return _npc_cache


def get_npc(name: str) -> dict:
    npcs = _load_npcs()
    if name not in npcs:
        raise ValueError(f"NPC '{name}' not found")
    return npcs[name]


def _base_prompt(npc: dict) -> str:
    return (
        f"당신은 판타지 세계 알데란 왕국의 NPC '{npc['full_name']}({npc['name']})'입니다.\n"
        f"성격: {npc['personality']}\n"
        f"말투: {npc['tone']}\n"
        f"배경: {npc['background']}\n"
        "절대로 현대 기술, AI, 인터넷 등 시대에 맞지 않는 내용을 언급하지 마십시오.\n"
        "항상 NPC의 말투와 성격을 유지하십시오."
    )


def _tone_rules(npc: dict) -> str:
    name = npc["name"]
    if name == "약초상":
        return (
            "\n무기(weapon)나 방어구(armor)에 관한 질문을 받으면 "
            "common 수준의 정보만 간략히 답하고, 자세한 건 대장장이에게 가보라고 안내하십시오."
        )
    if name == "대장장이":
        return (
            "\n약초(herb)나 포션(potion)에 관한 질문을 받으면 "
            "common 수준의 정보만 간략히 답하고, 자세한 건 약초상 할머니에게 가보라고 안내하십시오."
        )
    if name == "영주":
        return (
            "\n어떤 질문을 받더라도 제작법, 성분, 정확한 수치 등 세부 전문 지식은 "
            "모른다고 명확히 밝히십시오. 왕국 전체의 흐름만 파악하고 있습니다."
        )
    return ""


def build_chitchat_prompt(npc_name: str) -> str:
    npc = get_npc(npc_name)
    return (
        _base_prompt(npc)
        + _tone_rules(npc)
        + "\n자유로운 대화에 NPC 성격에 맞게 자연스럽게 응답하십시오."
    )


def build_item_query_prompt(npc_name: str, context: str) -> str:
    npc = get_npc(npc_name)
    return (
        _base_prompt(npc)
        + _tone_rules(npc)
        + f"\n\n[관련 아이템 정보]\n{context}\n\n"
        "위 정보를 바탕으로 질문에 답하십시오. "
        "제공된 정보 범위를 벗어난 내용은 모른다고 하십시오."
    )


def build_npc_query_prompt(npc_name: str, context: str) -> str:
    npc = get_npc(npc_name)
    return (
        _base_prompt(npc)
        + _tone_rules(npc)
        + f"\n\n[관련 NPC 정보]\n{context}\n\n"
        "위 정보를 바탕으로 질문에 답하십시오. "
        "제공된 정보 범위를 벗어난 내용은 모른다고 하십시오."
    )


def build_location_query_prompt(npc_name: str, context: str) -> str:
    npc = get_npc(npc_name)
    return (
        _base_prompt(npc)
        + _tone_rules(npc)
        + f"\n\n[관련 장소 정보]\n{context}\n\n"
        "위 정보를 바탕으로 질문에 답하십시오. "
        "제공된 정보 범위를 벗어난 내용은 모른다고 하십시오."
    )


def build_jailbreak_prompt(npc_name: str) -> str:
    """LLM 미사용 — NPC 말투에 맞는 고정 응답 문자열 반환."""
    return _JAILBREAK_RESPONSES.get(
        npc_name,
        "그건 이해할 수 없는 말이오.",
    )


def append_no_result_instruction(base_prompt: str) -> str:
    return (
        base_prompt
        + "\n\n[지시] 관련 정보를 찾지 못했습니다. "
        "NPC의 말투와 성격을 유지하면서 모른다고 솔직하게 답하십시오."
    )


def append_permission_instruction(base_prompt: str) -> str:
    return (
        base_prompt
        + "\n\n[지시] 해당 질문의 세부 정보는 전문가 NPC만 알 수 있습니다. "
        "NPC 말투로 간략히 답하고, 전문가(약초상 또는 대장장이)에게 안내하십시오."
    )
