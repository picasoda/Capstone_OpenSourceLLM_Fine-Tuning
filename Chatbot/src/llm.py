from __future__ import annotations

import json
import os
import time

import ollama

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "config.json")
with open(_CONFIG_PATH, encoding="utf-8") as _f:
    _cfg = json.load(_f)["llm"]

MODEL: str = _cfg["model"]
MAX_RETRIES: int = _cfg["max_retries"]
RETRY_DELAY: float = _cfg["retry_delay"]
DEFAULT_TEMPERATURE: float = _cfg["default_temperature"]
DEFAULT_MAX_TOKENS: int = _cfg["default_max_tokens"]


def generate(
    system_prompt: str,
    user_message: str,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> str:
    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            response = ollama.chat(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                options={"temperature": temperature, "num_predict": max_tokens},
                think=False,
            )
            return response.message.content
        except Exception as exc:
            last_error = exc
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    raise RuntimeError(
        f"LLM call failed after {MAX_RETRIES} attempts: {last_error}"
    ) from last_error
