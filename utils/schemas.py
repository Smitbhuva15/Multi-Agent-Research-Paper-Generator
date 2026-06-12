from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class SourceItem(BaseModel):
    title: str = Field(min_length=2)
    url: str = Field(min_length=5)
    snippet: str = ""


class ResearchOutput(BaseModel):
    topic: str
    queries: List[str] = Field(default_factory=list)
    sources: List[SourceItem] = Field(default_factory=list, min_length=5, max_length=10)


class CriticOutput(BaseModel):
    score: int = Field(ge=1, le=10)
    weaknesses: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)


class PipelineState(BaseModel):
    topic: str
    research: Optional[ResearchOutput] = None
    draft_paper: Optional[str] = None
    review: Optional[CriticOutput] = None
    final_paper: Optional[str] = None
