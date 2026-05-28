"""
main.py - Socrates Screen FastAPI backend.

This file only wires the web app together. Recommendation orchestration, TMDB
validation, schemas, and shared HTTP client lifecycle live in separate modules.
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from http_client import close_http_client, get_http_client
from recommendation_service import recommendation_service
from schemas import MovieCardList, RecommendPayload


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Socrates Screen API...")
    get_http_client()
    yield
    logger.info("Shutting down...")
    await close_http_client()


app = FastAPI(
    title="Socrates Screen API",
    description="Movie recommendation engine powered by Llama 3 + TMDB",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)


@app.get("/health", tags=["meta"])
async def health_check():
    return {
        "status": "ok",
        "groq_configured": bool(os.environ.get("GROQ_API_KEY")),
        "cerebras_configured": bool(os.environ.get("CEREBRAS_API_KEY")),
        "tmdb_configured": bool(settings.tmdb_api_key),
        "cloudflare_worker": settings.cloudflare_worker_url,
    }


@app.post("/api/recommend", response_model=MovieCardList, tags=["recommendations"])
async def recommend(payload: RecommendPayload) -> MovieCardList:
    """
    Generate candidates with the LLM, verify them with TMDB, and return 3 films.
    """
    return await recommendation_service.build_movie_list(payload)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
