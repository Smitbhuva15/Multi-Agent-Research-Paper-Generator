from __future__ import annotations

import os

from utils.schemas import ResearchOutput
from utils.search import collect_sources


def run_researcher(topic: str) -> ResearchOutput:
    configured_max = os.getenv("MAX_SOURCES", "8")
    try:
        max_sources = int(configured_max)
    except ValueError:
        max_sources = 8

    max_sources = max(5, min(10, max_sources))

    sources, queries = collect_sources(
        topic=topic,
        min_sources=5,
        max_sources=max_sources,
        max_results_per_query=8,
    )
    return ResearchOutput(topic=topic, queries=queries, sources=sources)
