from __future__ import annotations

from utils.formatters import format_review_for_prompt, format_sources_for_prompt
from utils.llm import chat_completion
from utils.prompts import render_prompt
from utils.schemas import CriticOutput, ResearchOutput
from utils.validators import find_missing_sections


def run_editor(
    topic: str,
    draft: str,
    review: CriticOutput,
    research: ResearchOutput,
) -> str:
    source_block = format_sources_for_prompt(research.sources)
    review_block = format_review_for_prompt(review)

    prompt = render_prompt(
        "editor_prompt.md",
        {
            "TOPIC": topic,
            "SOURCES": source_block,
            "REVIEW": review_block,
            "DRAFT": draft,
        },
    )

    polished = chat_completion(
        messages=[
            {
                "role": "system",
                "content": "You are a careful editor that improves without fabricating citations.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.25,
        max_tokens=5200,
    )

    missing = find_missing_sections(polished)
    if missing:
        repair_prompt = (
            "Revise the paper so all required sections are present and high quality.\n"
            f"Missing sections: {', '.join(missing)}\n\n"
            "Use only source citations already provided.\n"
            "Return markdown only.\n\n"
            f"Current paper:\n{polished}"
        )
        polished = chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": "You are a strict markdown editor.",
                },
                {
                    "role": "user",
                    "content": repair_prompt,
                },
            ],
            temperature=0.2,
            max_tokens=5200,
        )

    return polished.strip()
