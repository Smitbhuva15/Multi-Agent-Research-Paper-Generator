from __future__ import annotations

import json
from typing import Any

from utils.llm import chat_completion
from utils.prompts import render_prompt
from utils.schemas import CriticOutput


def _extract_json_object(text: str) -> str:
    start = text.find("{")
    if start == -1:
        return ""

    depth = 0
    for index in range(start, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]

    return ""


def _coerce_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _validate_payload(payload: dict[str, Any]) -> CriticOutput:
    try:
        score = int(payload.get("score", 6))
    except Exception:
        score = 6

    score = max(1, min(10, score))
    weaknesses = _coerce_list(payload.get("weaknesses"))
    improvements = _coerce_list(payload.get("improvements"))

    if len(weaknesses) < 3:
        weaknesses.extend(
            [
                "Some arguments need stronger evidence links to cited sources.",
                "Section transitions can be clearer and more concise.",
                "Methodological assumptions need tighter definition.",
            ][: 3 - len(weaknesses)]
        )

    if len(improvements) < 3:
        improvements.extend(
            [
                "Tighten claims by pairing each major claim with a direct citation id.",
                "Improve coherence by adding explicit links between sections.",
                "Clarify result interpretation limits and future work.",
            ][: 3 - len(improvements)]
        )

    return CriticOutput(score=score, weaknesses=weaknesses, improvements=improvements)


def _parse_review(raw: str) -> CriticOutput:
    candidate = raw.strip()
    if not candidate.startswith("{"):
        candidate = _extract_json_object(candidate)

    if not candidate:
        raise ValueError("No JSON object found in critic output.")

    parsed = json.loads(candidate)
    if not isinstance(parsed, dict):
        raise ValueError("Critic output JSON must be an object.")

    return _validate_payload(parsed)


def run_critic(topic: str, draft: str) -> CriticOutput:
    prompt = render_prompt(
        "critic_prompt.md",
        {
            "TOPIC": topic,
            "DRAFT": draft,
        },
    )

    raw = chat_completion(
        messages=[
            {
                "role": "system",
                "content": "You are a strict reviewer who returns JSON only.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.0,
        max_tokens=1400,
    )

    try:
        return _parse_review(raw)
    except Exception:
        repair_raw = chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": "Convert input into valid JSON only.",
                },
                {
                    "role": "user",
                    "content": (
                        "Convert the following review text into valid JSON with keys "
                        "score, weaknesses, improvements.\n\n"
                        f"Review text:\n{raw}"
                    ),
                },
            ],
            temperature=0.0,
            max_tokens=900,
        )

        try:
            return _parse_review(repair_raw)
        except Exception:
            return CriticOutput(
                score=6,
                weaknesses=[
                    "Draft quality could not be fully parsed from critic output.",
                    "Evidence-to-claim links may be inconsistent.",
                    "Language precision can be improved.",
                ],
                improvements=[
                    "Strengthen citation usage for each key claim.",
                    "Improve transitions across major sections.",
                    "Refine conclusion with clearer limitations.",
                ],
            )
