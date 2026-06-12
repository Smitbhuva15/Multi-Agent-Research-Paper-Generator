from __future__ import annotations

from pathlib import Path

_PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"


def load_prompt(template_name: str) -> str:
    prompt_path = _PROMPT_DIR / template_name
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")


def render_prompt(template_name: str, replacements: dict[str, str]) -> str:
    rendered = load_prompt(template_name)
    for key, value in replacements.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return rendered
