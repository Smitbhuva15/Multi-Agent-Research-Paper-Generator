from __future__ import annotations

import importlib
from functools import lru_cache
from typing import Callable, Optional, TypedDict

from agents.critic import run_critic
from agents.editor import run_editor
from agents.researcher import run_researcher
from agents.writer import run_writer
from utils.schemas import CriticOutput, PipelineState, ResearchOutput
from utils.validators import find_missing_sections

StageCallback = Optional[Callable[[str, str], None]]


class GraphState(TypedDict, total=False):
    topic: str
    research: ResearchOutput
    draft_paper: str
    review: CriticOutput
    final_paper: str
    stage_callback: StageCallback


def _emit(state: GraphState, stage: str, message: str) -> None:
    callback = state.get("stage_callback")
    if callback is not None:
        callback(stage, message)


def _get_langgraph_primitives():
    try:
        graph_module = importlib.import_module("langgraph.graph")
    except Exception as exc:
        raise RuntimeError(
            "LangGraph is required but not installed. Install dependencies from requirements.txt."
        ) from exc

    return graph_module.START, graph_module.END, graph_module.StateGraph


def _researcher_node(state: GraphState) -> GraphState:
    topic = state["topic"]
    _emit(state, "Researcher", "Collecting 5 to 10 reliable sources.")
    research = run_researcher(topic)
    source_count = len(research.sources)
    if not (5 <= source_count <= 10):
        raise ValueError("Researcher must return between 5 and 10 sources.")
    _emit(state, "Researcher", f"Collected {source_count} sources.")
    return {"research": research}


def _writer_node(state: GraphState) -> GraphState:
    topic = state["topic"]
    research = state["research"]
    _emit(state, "Writer", "Generating paper draft.")
    draft = run_writer(topic, research)
    draft_missing = find_missing_sections(draft)
    if draft_missing:
        raise ValueError(
            "Draft is missing required sections: " + ", ".join(draft_missing)
        )
    return {"draft_paper": draft}


def _critic_node(state: GraphState) -> GraphState:
    topic = state["topic"]
    draft = state["draft_paper"]
    _emit(state, "Critic", "Reviewing draft quality.")
    review = run_critic(topic, draft)
    _emit(state, "Critic", f"Draft scored {review.score}/10.")
    return {"review": review}


def _editor_node(state: GraphState) -> GraphState:
    topic = state["topic"]
    draft = state["draft_paper"]
    review = state["review"]
    research = state["research"]
    _emit(state, "Editor", "Polishing final paper.")
    final_paper = run_editor(
        topic=topic,
        draft=draft,
        review=review,
        research=research,
    )

    final_missing = find_missing_sections(final_paper)
    if final_missing:
        raise ValueError(
            "Final paper is missing required sections: " + ", ".join(final_missing)
        )

    return {"final_paper": final_paper}


@lru_cache(maxsize=1)
def _compiled_graph():
    start, end, state_graph = _get_langgraph_primitives()
    graph = state_graph(GraphState)
    graph.add_node("researcher", _researcher_node)
    graph.add_node("writer", _writer_node)
    graph.add_node("critic", _critic_node)
    graph.add_node("editor", _editor_node)

    graph.add_edge(start, "researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", "critic")
    graph.add_edge("critic", "editor")
    graph.add_edge("editor", end)
    return graph.compile()


def run_pipeline(topic: str, stage_callback: StageCallback = None) -> PipelineState:
    clean_topic = " ".join(topic.split()).strip()
    if not clean_topic:
        raise ValueError("Topic cannot be empty.")

    initial_state: GraphState = {
        "topic": clean_topic,
        "stage_callback": stage_callback,
    }

    _emit(initial_state, "Supervisor", "Starting multi-agent workflow.")
    final_state = _compiled_graph().invoke(initial_state)
    _emit(final_state, "Supervisor", "Workflow complete.")

    return PipelineState(
        topic=clean_topic,
        research=final_state.get("research"),
        draft_paper=final_state.get("draft_paper"),
        review=final_state.get("review"),
        final_paper=final_state.get("final_paper"),
    )
