from __future__ import annotations

import json
import os

NPC_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "npcPrompt.json")
_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "config.json")

_config_cache: dict | None = None


def _load_config() -> dict:
    global _config_cache
    if _config_cache is None:
        with open(_CONFIG_PATH, encoding="utf-8") as f:
            _config_cache = json.load(f)
    return _config_cache

_npc_cache: dict[str, dict] | None = None


def _load_npcs() -> dict[str, dict]:
    global _npc_cache
    if _npc_cache is None:
        with open(NPC_DATA_PATH, encoding="utf-8") as f:
            npcs = json.load(f)
        _npc_cache = {}
        for npc in npcs:
            _npc_cache[npc["name"]] = npc
            _npc_cache[npc["job"]] = npc
    return _npc_cache


def get_npc(name: str) -> dict:
    npcs = _load_npcs()
    if name not in npcs:
        raise ValueError(f"NPC '{name}' not found")
    return npcs[name]


def _base_prompt(npc: dict) -> str:
    return (
        f"당신은 판타지 세계 알데란 영지의 NPC '{npc['name']}({npc['job']})'입니다.\n"
        f"성격: {npc['personality']}\n"
        f"말투: {npc['tone']}\n"
        f"배경: {npc['background']}\n"
        "절대로 현대 기술, AI, 인터넷 등 시대에 맞지 않는 내용을 언급하지 마십시오.\n"
        "항상 NPC의 말투와 성격을 유지하십시오."
    )


def _item_tone_rules(npc: dict) -> str:
    """카테고리별 NPC 안내 규칙 — 아이템 관련 쿼리에만 적용."""
    rule = npc.get("item_tone_rule", "")
    return f"\n{rule}" if rule else ""


def build_chitchat_prompt(npc_name: str) -> str:
    npc = get_npc(npc_name)
    return (
        _base_prompt(npc)
        + "\n자유로운 대화에 NPC 성격에 맞게 자연스럽게 응답하십시오."
    )


def build_combined_query_prompt(npc_name: str, contexts: dict[str, str]) -> str:
    """다중 라우트 검색 결과를 합산한 프롬프트.

    contexts = {"item": "...", "npc": "...", "location": "..."}
    비어있는 섹션은 포함하지 않는다.
    """
    npc = get_npc(npc_name)

    LABELS = {
        "item": "관련 아이템 정보",
        "npc": "관련 NPC 정보",
        "location": "관련 장소 정보",
        "lore": "관련 세계관 정보",
    }

    sections = ""
    has_item = bool(contexts.get("item"))

    for key, label in LABELS.items():
        content = contexts.get(key, "")
        if content:
            sections += f"\n\n[{label}]\n{content}"

    prompt = _base_prompt(npc)
    if has_item:
        prompt += _item_tone_rules(npc)
    prompt += sections
    prompt += "\n\n위 정보를 바탕으로 질문에 답하십시오. 제공된 정보 범위를 벗어난 내용은 모른다고 하십시오."
    return prompt


def build_jailbreak_prompt(npc_name: str) -> str:
    """LLM 미사용 — NPC 말투에 맞는 고정 응답 문자열 반환."""
    npc = get_npc(npc_name)
    return npc.get("jailbreak_response", "그건 이해할 수 없는 말이오.")


def append_no_result_instruction(base_prompt: str) -> str:
    text = _load_config()["instructions"]["no_result"]
    return base_prompt + f"\n\n[지시] {text}"


def append_permission_instruction(base_prompt: str, expert: str | None = None) -> str:
    template = _load_config()["instructions"]["permission_gap"]
    text = template.format(expert=expert if expert else "담당 전문가")
    return base_prompt + f"\n\n[지시] {text}"
