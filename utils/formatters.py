from __future__ import annotations

from utils.schemas import CriticOutput, SourceItem


def format_sources_for_prompt(sources: list[SourceItem]) -> str:
    blocks: list[str] = []
    for index, source in enumerate(sources, start=1):
        snippet = " ".join(source.snippet.split())
        blocks.append(
            f"[S{index}] Title: {source.title}\n"
            f"URL: {source.url}\n"
            f"Snippet: {snippet}"
        )
    return "\n\n".join(blocks)


def format_review_for_prompt(review: CriticOutput) -> str:
    weaknesses = "\n".join(f"- {item}" for item in review.weaknesses)
    improvements = "\n".join(f"- {item}" for item in review.improvements)
    return (
        f"Score: {review.score}/10\n"
        f"Weaknesses:\n{weaknesses or '- None provided'}\n\n"
        f"Improvements:\n{improvements or '- None provided'}"
    )
