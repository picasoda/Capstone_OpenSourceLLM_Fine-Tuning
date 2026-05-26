from __future__ import annotations

import time

import ollama

MODEL = "qwen3.5:9b"
MAX_RETRIES = 3
RETRY_DELAY = 1.0


def generate(
    system_prompt: str,
    user_message: str,
    temperature: float = 0.7,
    max_tokens: int = 512,
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
