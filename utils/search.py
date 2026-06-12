from __future__ import annotations

import importlib
import re
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from utils.schemas import SourceItem

_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "with",
}

_HIGH_TRUST_MARKERS = (
    ".edu",
    ".gov",
    "nature.com",
    "sciencedirect.com",
    "springer.com",
    "ieee.org",
    "acm.org",
    "nih.gov",
    "who.int",
    "arxiv.org",
)


def _tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return {word for word in words if len(word) > 2 and word not in _STOPWORDS}


def _domain_score(url: str) -> int:
    host = urlparse(url).netloc.lower()
    if any(marker in host for marker in _HIGH_TRUST_MARKERS):
        return 3
    if host.endswith(".org"):
        return 2
    return 1


def _clean_text(text: str, max_len: int) -> str:
    compact = " ".join((text or "").split())
    return compact[:max_len]


def _keyword_overlap(topic: str, title: str, snippet: str) -> int:
    topic_tokens = _tokenize(topic)
    body_tokens = _tokenize(f"{title} {snippet}")
    return len(topic_tokens.intersection(body_tokens))


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    clean_query_pairs = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=False):
        key_l = key.lower()
        if key_l.startswith("utm_") or key_l in {"ref", "source", "fbclid", "gclid"}:
            continue
        clean_query_pairs.append((key, value))

    cleaned = parsed._replace(
        query=urlencode(clean_query_pairs, doseq=True),
        fragment="",
    )
    return urlunparse(cleaned)


def build_query_variants(topic: str) -> list[str]:
    candidates = [
        topic,
        f"{topic} scholarly review",
        f"{topic} methodology research",
        f"{topic} recent findings",
        f"{topic} site:edu OR site:gov",
    ]
    deduped: list[str] = []
    seen: set[str] = set()
    for query in candidates:
        q = " ".join(query.split()).strip()
        if q and q.lower() not in seen:
            deduped.append(q)
            seen.add(q.lower())
    return deduped


def _resolve_ddgs_class():
    for module_name in ("ddgs", "duckduckgo_search"):
        try:
            module = importlib.import_module(module_name)
            return getattr(module, "DDGS")
        except Exception:
            continue

    raise RuntimeError(
        "Could not import DDGS client. Install `ddgs` or `duckduckgo-search`."
    )


def _ddg_text_search(query: str, max_results: int) -> list[dict]:
    ddgs_class = _resolve_ddgs_class()
    with ddgs_class() as ddgs:
        return list(ddgs.text(query, max_results=max_results))


def collect_sources(
    topic: str,
    min_sources: int = 5,
    max_sources: int = 10,
    max_results_per_query: int = 8,
) -> tuple[list[SourceItem], list[str]]:
    queries = build_query_variants(topic)
    candidates: list[tuple[int, SourceItem]] = []
    seen_urls: set[str] = set()

    for query in queries:
        try:
            results = _ddg_text_search(query, max_results=max_results_per_query)
        except Exception:
            continue

        for rank, item in enumerate(results):
            raw_url = str(item.get("href") or item.get("url") or "").strip()
            title = _clean_text(str(item.get("title") or "Untitled source"), max_len=220)
            snippet = _clean_text(str(item.get("body") or item.get("snippet") or ""), max_len=600)

            if not raw_url:
                continue

            normalized = normalize_url(raw_url)
            if not normalized or normalized in seen_urls:
                continue

            seen_urls.add(normalized)
            score = (
                _domain_score(raw_url) * 3
                + _keyword_overlap(topic, title, snippet) * 2
                + max(0, 10 - rank)
            )
            candidates.append((score, SourceItem(title=title, url=raw_url, snippet=snippet)))

    candidates.sort(key=lambda row: row[0], reverse=True)
    selected = [row[1] for row in candidates[:max_sources]]

    if len(selected) < min_sources:
        raise ValueError(
            "Could not find enough reliable sources. Try a broader topic or run again."
        )

    return selected, queries
