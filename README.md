# Multi-Agent Research Paper Generator

A reproducible multi-agent pipeline that generates full research papers in Markdown from a user-provided topic. The project orchestrates a small agent graph — Researcher, Writer, Critic, Editor — managed by a Supervisor to collect sources, draft a paper, critique it, and produce a polished final manuscript.

**Status:** Prototype — Streamlit UI for interactive generation.

**Key goals:**
- Produce evidence-backed research papers using curated web sources.
- Keep citations grounded in discovered sources (no invented references).
- Provide iterative review and polishing via automated critic and editor agents.

**Highlights**
- Modular agent implementations in `agents/` that separate concerns (research, writing, review, editing).
- Source discovery with simple quality heuristics in `utils/search.py`.
- GROQ/OpenAI-compatible LLM adapter in `utils/llm.py` (uses `OpenAI` client with a configurable base URL).
- Streamlit app at the root provides a minimal UI to run the pipeline and download results.


## Overview

This repository demonstrates a multi-agent workflow for producing academic-style documents. Given a short topic, the system:

1. Collects 5–10 reliable sources for the topic.
2. Uses those sources to generate an initial draft (writer).
3. Runs a critic to score and list weaknesses and improvements.
4. Applies an editor to produce a polished Markdown paper.

The flow is orchestrated in `agents/supervisor.py` with a compiled graph that runs:
Researcher → Writer → Critic → Editor.

## Architecture

- Supervisor: builds and invokes the agent graph.
- Researcher: discovers and ranks web sources.
- Writer: generates the first draft.
- Critic: returns a JSON review (score, weaknesses, improvements).
- Editor: polishes the draft according to the critic and sources.

## Quickstart

Prerequisites
- Python 3.10+ recommended
- A compatible LLM API key (GROQ-compatible key used by `utils/llm.py`)

Install dependencies (example):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install streamlit python-dotenv pydantic openai langgraph ddgs duckduckgo-search
```

Run the app:

```bash
# Add your GROQ-compatible API key to environment or .env
export GROQ_API_KEY="your_key_here"
streamlit run app.py
```

Open the Streamlit UI, enter a topic, and click "Generate Paper". The UI shows intermediate status, source table, critic review, draft preview, and final paper with a download button.

## Configuration

Environment variables used by the project:
- `GROQ_API_KEY` (required) — API key used by `utils/llm.get_client()`.
- `GROQ_MODEL` (optional) — override default model name used when calling the LLM.
- `MAX_SOURCES` (optional) — integer to control how many sources the researcher collects (bounded 5–10).

Tip: Create a `.env` file at the project root with `GROQ_API_KEY=<key>` for local runs.


