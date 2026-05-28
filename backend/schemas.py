"""Pydantic schemas shared by routes and services."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from llm_service import BaselineProfile, SessionState


class RecommendPayload(BaseModel):
    """Body accepted by POST /api/recommend."""

    baseline_profile: BaselineProfile
    session_state: SessionState
    seen_titles: list[str] = Field(default_factory=list)


class MovieCard(BaseModel):
    """Full recommendation returned to the frontend."""

    title: str
    year: str
    reason: str
    poster_url: Optional[str] = None
    tmdb_id: Optional[int] = None
    original_language: Optional[str] = None
    vote_average: Optional[float] = None
    runtime_minutes: Optional[int] = None


class MovieCardList(BaseModel):
    """List of verified recommendations returned to the frontend."""

    films: list[MovieCard]
