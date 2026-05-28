"""TMDB search, validation, details fetching, and poster URL rewriting."""

from __future__ import annotations

import logging
import re
import unicodedata
from typing import Optional
from urllib.parse import quote

import httpx

from config import Settings, settings
from http_client import get_http_client
from llm_service import RecommendationOutput, SessionState
from schemas import MovieCard


logger = logging.getLogger("tmdb_service")


def normalize_title(title: str) -> str:
    normalized = unicodedata.normalize("NFKD", title or "")
    ascii_title = normalized.encode("ascii", "ignore").decode("ascii")
    compacted = re.sub(r"[^a-z0-9]+", " ", ascii_title.lower()).strip()
    return re.sub(r"^(the|a|an) ", "", compacted)


def release_year(movie_data: dict) -> Optional[str]:
    release_date = movie_data.get("release_date") or ""
    if len(release_date) >= 4 and release_date[:4].isdigit():
        return release_date[:4]
    return None


class TMDBService:
    def __init__(self, app_settings: Settings = settings):
        self.settings = app_settings

    @property
    def is_configured(self) -> bool:
        return bool(self.settings.tmdb_api_key)

    async def hydrate_candidate(
        self,
        candidate: RecommendationOutput,
        session_state: SessionState,
    ) -> Optional[MovieCard]:
        """
        Convert one LLM candidate into a verified MovieCard.

        Candidates are rejected when they cannot be confidently matched in TMDB,
        details cannot be fetched, or hard runtime constraints fail.
        """
        tmdb_data = await self.search_movie(candidate.title, candidate.year)
        if not tmdb_data:
            logger.info(
                "Rejected unverified LLM title: %s (%s)",
                candidate.title,
                candidate.year,
            )
            return None

        tmdb_id = tmdb_data.get("id")
        if not isinstance(tmdb_id, int):
            logger.info("Rejected TMDB result with missing id for: %s", candidate.title)
            return None

        details = await self.fetch_details(tmdb_id)
        if not details:
            logger.info(
                "Rejected %s because TMDB details could not be fetched",
                candidate.title,
            )
            return None

        if not self._passes_runtime_constraints(details, session_state):
            logger.info(
                "Rejected %s due to runtime %s for commitment '%s'",
                details.get("title") or candidate.title,
                details.get("runtime"),
                session_state.commitment,
            )
            return None

        return self._to_movie_card(candidate, tmdb_data, details)

    async def search_movie(self, title: str, year: str) -> Optional[dict]:
        """Search TMDB and return the first confident title/year match."""
        if not self.is_configured:
            logger.warning("TMDB_API_KEY not set - cannot validate movie candidates")
            return None

        params: dict = {
            "query": title,
            "include_adult": "false",
            "language": "en-US",
            "page": "1",
        }
        if year and year.isdigit():
            params["year"] = year

        try:
            response = await get_http_client().get(
                f"{self.settings.tmdb_base_url}/search/movie",
                params=params,
                headers=self._auth_headers(params),
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error("TMDB search HTTP error %s: %s", exc.response.status_code, exc)
            return None
        except Exception as exc:
            logger.error("TMDB search failed: %s", exc)
            return None

        results = response.json().get("results", [])
        if not results:
            logger.info("TMDB returned 0 results for '%s' (%s)", title, year)
            return None

        for result in results:
            if self._is_confident_match(title, year, result):
                return result

        logger.info("TMDB returned no confident match for '%s' (%s)", title, year)
        return None

    async def fetch_details(self, tmdb_id: int) -> Optional[dict]:
        """Fetch authoritative runtime and metadata for a verified TMDB movie."""
        if not self.is_configured:
            return None

        params = {"language": "en-US"}
        try:
            response = await get_http_client().get(
                f"{self.settings.tmdb_base_url}/movie/{tmdb_id}",
                params=params,
                headers=self._auth_headers(params),
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            logger.error("TMDB details HTTP error %s: %s", exc.response.status_code, exc)
            return None
        except Exception as exc:
            logger.error("TMDB details fetch failed: %s", exc)
            return None

    def poster_url(self, poster_path: str) -> str:
        worker_base = self.settings.cloudflare_worker_url.rstrip("/")
        encoded_path = quote(poster_path, safe="/")
        return f"{worker_base}/?path={encoded_path}"

    def _auth_headers(self, params: dict) -> dict:
        headers = {"Accept": "application/json"}
        cleaned_key = self.settings.tmdb_api_key.strip()
        if len(cleaned_key) == 32 and all(
            c in "0123456789abcdefABCDEF" for c in cleaned_key
        ):
            params["api_key"] = cleaned_key
        else:
            headers["Authorization"] = f"Bearer {cleaned_key}"
        return headers

    def _is_confident_match(self, title: str, year: str, tmdb_data: dict) -> bool:
        requested_title = normalize_title(title)
        candidate_titles = {
            normalize_title(tmdb_data.get("title", "")),
            normalize_title(tmdb_data.get("original_title", "")),
        }

        if not self._title_matches(requested_title, candidate_titles):
            return False

        requested_year = year.strip()
        candidate_year = release_year(tmdb_data)
        if (
            requested_year.isdigit()
            and candidate_year
            and requested_year != candidate_year
        ):
            return False

        return bool(tmdb_data.get("id"))

    @staticmethod
    def _title_matches(requested_title: str, candidate_titles: set[str]) -> bool:
        if requested_title in candidate_titles:
            return True
        if len(requested_title) < 12:
            return False
        return any(
            candidate.startswith(requested_title) or requested_title.startswith(candidate)
            for candidate in candidate_titles
            if candidate
        )

    def _passes_runtime_constraints(
        self,
        details: dict,
        session_state: SessionState,
    ) -> bool:
        runtime = details.get("runtime")
        if session_state.commitment != "quick":
            return True
        return (
            isinstance(runtime, int)
            and runtime > 0
            and runtime <= self.settings.quick_max_runtime_minutes
        )

    def _to_movie_card(
        self,
        candidate: RecommendationOutput,
        tmdb_data: dict,
        details: dict,
    ) -> MovieCard:
        raw_poster = details.get("poster_path") or tmdb_data.get("poster_path")
        poster_url = self.poster_url(raw_poster) if raw_poster else None
        if poster_url:
            logger.info(
                "%s -> poster %s",
                details.get("title") or candidate.title,
                poster_url,
            )

        return MovieCard(
            title=details.get("title") or tmdb_data.get("title") or candidate.title,
            year=release_year(details) or release_year(tmdb_data) or candidate.year,
            reason=candidate.reason,
            poster_url=poster_url,
            tmdb_id=tmdb_data.get("id"),
            original_language=details.get("original_language")
            or tmdb_data.get("original_language"),
            vote_average=details.get("vote_average") or tmdb_data.get("vote_average"),
            runtime_minutes=details.get("runtime"),
        )


tmdb_service = TMDBService()
