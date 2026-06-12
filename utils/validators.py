from __future__ import annotations

import re

REQUIRED_SECTIONS = [
    "Abstract",
    "Introduction",
    "Literature Review",
    "Methodology",
    "Results",
    "Conclusion",
    "References",
]


def find_missing_sections(markdown_text: str) -> list[str]:
    missing: list[str] = []
    for section in REQUIRED_SECTIONS:
        pattern = rf"^\s*#{{1,6}}\s*{re.escape(section)}\s*$"
        if not re.search(pattern, markdown_text, flags=re.IGNORECASE | re.MULTILINE):
            missing.append(section)
    return missing
