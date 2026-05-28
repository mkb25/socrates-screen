"""Recommendation orchestration: LLM candidates -> TMDB-verified movies."""

from __future__ import annotations

import asyncio
import logging

from fastapi import HTTPException

from config import Settings, settings
from llm_service import (
    RecommendationOutput,
    RecommendationRequest,
    get_recommendation,
)
from schemas import MovieCard, MovieCardList, RecommendPayload
from tmdb_service import TMDBService, normalize_title, tmdb_service


logger = logging.getLogger("recommendation_service")


class RecommendationService:
    def __init__(
        self,
        movie_service: TMDBService = tmdb_service,
        app_settings: Settings = settings,
    ):
        self.movie_service = movie_service
        self.settings = app_settings

    async def build_movie_list(self, payload: RecommendPayload) -> MovieCardList:
        """Return exactly 3 TMDB-verified recommendations or raise an API error."""
        if not self.movie_service.is_configured:
            raise HTTPException(
                status_code=503,
                detail="TMDB_API_KEY is required to verify movie recommendations.",
            )

        accepted_movies: list[MovieCard] = []
        accepted_tmdb_ids: set[int] = set()
        accepted_titles: list[str] = []
        rejected_titles: list[str] = []

        for attempt in range(1, self.settings.max_recommendation_attempts + 1):
            excluded_titles = dedupe_titles(
                [*payload.seen_titles, *accepted_titles, *rejected_titles]
            )
            candidates = await self._load_candidates(payload, excluded_titles, attempt)
            hydrated_movies = await asyncio.gather(
                *[
                    self.movie_service.hydrate_candidate(
                        candidate,
                        payload.session_state,
                    )
                    for candidate in candidates
                ]
            )

            for candidate, movie in zip(candidates, hydrated_movies):
                if len(accepted_movies) >= self.settings.required_film_count:
                    break

                if not movie or not movie.tmdb_id:
                    rejected_titles.append(candidate.title)
                    continue

                if self._is_duplicate_or_excluded(
                    movie,
                    candidate.title,
                    accepted_tmdb_ids,
                    excluded_titles,
                ):
                    rejected_titles.append(candidate.title)
                    continue

                accepted_movies.append(movie)
                accepted_titles.append(movie.title)
                accepted_tmdb_ids.add(movie.tmdb_id)

            if len(accepted_movies) >= self.settings.required_film_count:
                return MovieCardList(
                    films=accepted_movies[: self.settings.required_film_count]
                )

            logger.info(
                "Only %d verified films after attempt %d; retrying for replacements",
                len(accepted_movies),
                attempt,
            )

        raise HTTPException(
            status_code=502,
            detail=(
                "Could not verify enough real movies from the AI recommendations. "
                "Please try again."
            ),
        )

    async def _load_candidates(
        self,
        payload: RecommendPayload,
        excluded_titles: list[str],
        attempt: int,
    ) -> list[RecommendationOutput]:
        try:
            candidates = await get_recommendation(
                RecommendationRequest(
                    baseline_profile=payload.baseline_profile,
                    session_state=payload.session_state,
                    seen_titles=excluded_titles,
                )
            )
        except EnvironmentError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except Exception as exc:
            logger.exception("LLM call failed")
            raise HTTPException(status_code=500, detail=f"AI engine error: {exc}") from exc

        logger.info(
            "LLM attempt %d recommended %d films for taps [%s|%s|%s]: %s",
            attempt,
            len(candidates),
            payload.session_state.energy,
            payload.session_state.reality,
            payload.session_state.commitment,
            [candidate.title for candidate in candidates],
        )
        return candidates

    @staticmethod
    def _is_duplicate_or_excluded(
        movie: MovieCard,
        original_title: str,
        accepted_tmdb_ids: set[int],
        excluded_titles: list[str],
    ) -> bool:
        excluded_keys = {normalize_title(title) for title in excluded_titles}
        return (
            movie.tmdb_id in accepted_tmdb_ids
            or normalize_title(movie.title) in excluded_keys
            or normalize_title(original_title) in excluded_keys
        )


def dedupe_titles(titles: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for title in titles:
        normalized = normalize_title(title)
        if normalized and normalized not in seen:
            seen.add(normalized)
            deduped.append(title)
    return deduped


recommendation_service = RecommendationService()
