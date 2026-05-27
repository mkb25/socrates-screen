"""
main.py – Socrates Screen FastAPI Backend

Endpoints:
  POST /api/recommend  → Full pipeline: LLM → TMDB search → URL rewrite → response

Environment variables required (see .env.example):
  GROQ_API_KEY          or CEREBRAS_API_KEY
  TMDB_API_KEY          (Bearer token from https://www.themoviedb.org/settings/api)
  CLOUDFLARE_WORKER_URL (e.g. https://tmdb-proxy.your-account.workers.dev)
  ALLOWED_ORIGINS       (comma-separated list, defaults to localhost dev URLs)
"""

from __future__ import annotations

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Optional
from urllib.parse import quote

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from llm_service import (
    BaselineProfile,
    RecommendationRequest,
    SessionState,
    get_recommendation,
)

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

load_dotenv()  # load from .env in project root

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("main")

# ---------------------------------------------------------------------------
# Config (from environment)
# ---------------------------------------------------------------------------

TMDB_API_KEY: str = os.environ.get("TMDB_API_KEY", "")
TMDB_BASE_URL: str = "https://api.themoviedb.org/3"
CLOUDFLARE_WORKER_URL: str = os.environ.get(
    "CLOUDFLARE_WORKER_URL",
    "https://tmdb-proxy.example.workers.dev",  # replace with your worker URL
)
ALLOWED_ORIGINS_RAW: str = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173",
)
ALLOWED_ORIGINS: list[str] = [o.strip() for o in ALLOWED_ORIGINS_RAW.split(",")]

# ---------------------------------------------------------------------------
# Shared async HTTP client (reused across requests for connection pooling)
# ---------------------------------------------------------------------------

_http_client: Optional[httpx.AsyncClient] = None


def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0, connect=5.0),
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=50),
        )
    return _http_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Socrates Screen API…")
    get_http_client()  # warm up the connection pool
    yield
    logger.info("Shutting down…")
    if _http_client and not _http_client.is_closed:
        await _http_client.aclose()


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Socrates Screen API",
    description="Movie recommendation engine powered by Llama 3 + TMDB",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class RecommendPayload(BaseModel):
    """Body accepted by POST /api/recommend."""
    baseline_profile: BaselineProfile
    session_state: SessionState
    seen_titles: list[str] = Field(default_factory=list)  # titles already shown


class MovieCard(BaseModel):
    """Full recommendation returned to the frontend."""
    title: str
    year: str
    reason: str
    poster_url: Optional[str] = None      # Cloudflare-proxied image URL
    tmdb_id: Optional[int] = None
    original_language: Optional[str] = None
    vote_average: Optional[float] = None


class MovieCardList(BaseModel):
    """List of 3 recommendations returned to the frontend."""
    films: list[MovieCard]


# ---------------------------------------------------------------------------
# TMDB helpers
# ---------------------------------------------------------------------------


def _rewrite_poster_url(poster_path: str) -> str:
    """
    Convert TMDB's raw poster_path into a Cloudflare Worker URL.

    TMDB provides paths like: /abc123def.jpg
    We build: https://<worker>/?path=/abc123def.jpg

    The Worker fetches https://image.tmdb.org/t/p/w500/abc123def.jpg and
    relays it with long-lived cache headers, bypassing Indian ISP blocks.
    """
    worker_base = CLOUDFLARE_WORKER_URL.rstrip("/")
    encoded_path = quote(poster_path, safe="/")
    return f"{worker_base}/?path={encoded_path}"


async def _search_tmdb(title: str, year: str) -> Optional[dict]:
    """
    Search TMDB for a movie by title + optional year.
    Returns the best-matching result dict or None.
    """
    if not TMDB_API_KEY:
        logger.warning("TMDB_API_KEY not set – skipping poster lookup")
        return None

    client = get_http_client()
    params: dict = {
        "query": title,
        "include_adult": "false",
        "language": "en-US",
        "page": "1",
    }
    # year narrows results significantly; use it only when available
    if year and year.isdigit():
        params["year"] = year

    headers = {"Accept": "application/json"}

    # Dynamically support both v3 API Keys (32-char hex) and v4 Access Tokens (JWT)
    cleaned_key = TMDB_API_KEY.strip()
    if len(cleaned_key) == 32 and all(c in "0123456789abcdefABCDEF" for c in cleaned_key):
        params["api_key"] = cleaned_key
    else:
        headers["Authorization"] = f"Bearer {cleaned_key}"

    try:
        response = await client.get(
            f"{TMDB_BASE_URL}/search/movie",
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        if not results:
            logger.info("TMDB returned 0 results for '%s' (%s)", title, year)
            return None
        # Return the highest-popularity result (first by default TMDB ordering)
        return results[0]
    except httpx.HTTPStatusError as exc:
        logger.error("TMDB HTTP error %s: %s", exc.response.status_code, exc)
        return None
    except Exception as exc:
        logger.error("TMDB search failed: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/health", tags=["meta"])
async def health_check():
    return {
        "status": "ok",
        "groq_configured": bool(os.environ.get("GROQ_API_KEY")),
        "cerebras_configured": bool(os.environ.get("CEREBRAS_API_KEY")),
        "tmdb_configured": bool(TMDB_API_KEY),
        "cloudflare_worker": CLOUDFLARE_WORKER_URL,
    }


@app.post("/api/recommend", response_model=MovieCardList, tags=["recommendations"])
async def recommend(payload: RecommendPayload) -> MovieCardList:
    """
    Full recommendation pipeline:

    1. Receive baseline profile + 3-tap session state
    2. Ask LLM for 3 perfect movies (title, year, reason each)
    3. Fetch TMDB metadata for all 3 in parallel
    4. Rewrite poster_path → Cloudflare Worker URL for each
    5. Return MovieCardList to frontend
    """
    # ── Step 1: LLM — returns list of 3 RecommendationOutput ──────────────────
    try:
        llm_results = await get_recommendation(
            RecommendationRequest(
                baseline_profile=payload.baseline_profile,
                session_state=payload.session_state,
                seen_titles=payload.seen_titles,
            )
        )
    except EnvironmentError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("LLM call failed")
        raise HTTPException(status_code=500, detail=f"AI engine error: {exc}") from exc

    logger.info(
        "LLM recommended %d films for taps [%s|%s|%s]: %s",
        len(llm_results),
        payload.session_state.energy,
        payload.session_state.reality,
        payload.session_state.commitment,
        [r.title for r in llm_results],
    )

    # ── Step 2: TMDB lookups in parallel ─────────────────────────────────────
    tmdb_results = await asyncio.gather(
        *[_search_tmdb(r.title, r.year) for r in llm_results]
    )

    # ── Step 3: Assemble MovieCard for each film ──────────────────────────────
    films: list[MovieCard] = []
    for llm_r, tmdb_data in zip(llm_results, tmdb_results):
        poster_url: Optional[str] = None
        tmdb_id: Optional[int] = None
        original_language: Optional[str] = None
        vote_average: Optional[float] = None

        if tmdb_data:
            tmdb_id = tmdb_data.get("id")
            original_language = tmdb_data.get("original_language")
            vote_average = tmdb_data.get("vote_average")
            raw_poster = tmdb_data.get("poster_path")
            if raw_poster:
                poster_url = _rewrite_poster_url(raw_poster)
                logger.info("%s → poster %s", llm_r.title, poster_url)

        films.append(MovieCard(
            title=llm_r.title,
            year=llm_r.year,
            reason=llm_r.reason,
            poster_url=poster_url,
            tmdb_id=tmdb_id,
            original_language=original_language,
            vote_average=vote_average,
        ))

    return MovieCardList(films=films)


# ---------------------------------------------------------------------------
# Dev entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
