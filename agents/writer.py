from __future__ import annotations

from utils.formatters import format_sources_for_prompt
from utils.llm import chat_completion
from utils.prompts import render_prompt
from utils.schemas import ResearchOutput
from utils.validators import find_missing_sections


def run_writer(topic: str, research: ResearchOutput) -> str:
    source_block = format_sources_for_prompt(research.sources)
    prompt = render_prompt(
        "writer_prompt.md",
        {
            "TOPIC": topic,
            "SOURCES": source_block,
        },
    )

    draft = chat_completion(
        messages=[
            {
                "role": "system",
                "content": "You write rigorous research papers in clear markdown.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.35,
        max_tokens=5000,
    )

    missing = find_missing_sections(draft)
    if missing:
        repair_prompt = (
            "Revise the draft so it includes all mandatory sections with academic quality.\n"
            f"Missing sections: {', '.join(missing)}\n\n"
            "Keep citations grounded in the provided sources only.\n"
            "Return markdown only.\n\n"
            f"Topic:\n{topic}\n\n"
            f"Sources:\n{source_block}\n\n"
            f"Current draft:\n{draft}"
        )
        draft = chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": "You repair research papers without adding invented references.",
                },
                {
                    "role": "user",
                    "content": repair_prompt,
                },
            ],
            temperature=0.2,
            max_tokens=5000,
        )

    return draft.strip()
