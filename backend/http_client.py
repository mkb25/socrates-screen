"""Shared async HTTP client for outbound API calls."""

from __future__ import annotations

from typing import Optional

import httpx


_http_client: Optional[httpx.AsyncClient] = None


def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0, connect=5.0),
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=50),
        )
    return _http_client


async def close_http_client() -> None:
    if _http_client and not _http_client.is_closed:
        await _http_client.aclose()
