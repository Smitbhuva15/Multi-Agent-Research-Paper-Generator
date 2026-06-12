from __future__ import annotations

import os
from typing import Sequence

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_GROQ_BASE_URL = "https://api.groq.com/openai/v1"
_DEFAULT_MODEL = "llama-3.3-70b-versatile"


def get_client() -> OpenAI:
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Missing GROQ_API_KEY in environment variables.")

    return OpenAI(api_key=api_key, base_url=_GROQ_BASE_URL)


def chat_completion(
    messages: Sequence[dict[str, str]],
    model: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 4096,
) -> str:
    client = get_client()
    model_name = (model or os.getenv("GROQ_MODEL", _DEFAULT_MODEL)).strip() or _DEFAULT_MODEL

    response = client.chat.completions.create(
        model=model_name,
        messages=list(messages),
        temperature=temperature,
        max_tokens=max_tokens,
    )

    content = response.choices[0].message.content
    return (content or "").strip()
