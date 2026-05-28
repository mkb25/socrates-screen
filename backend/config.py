"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).with_name(".env"))


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    tmdb_api_key: str
    tmdb_base_url: str
    cloudflare_worker_url: str
    allowed_origins: list[str]
    required_film_count: int = 3
    max_recommendation_attempts: int = 3
    quick_max_runtime_minutes: int = 110


settings = Settings(
    tmdb_api_key=os.environ.get("TMDB_API_KEY", ""),
    tmdb_base_url="https://api.themoviedb.org/3",
    cloudflare_worker_url=os.environ.get(
        "CLOUDFLARE_WORKER_URL",
        "https://tmdb-proxy.example.workers.dev",
    ),
    allowed_origins=_split_csv(
        os.environ.get(
            "ALLOWED_ORIGINS",
            "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173",
        )
    ),
)
