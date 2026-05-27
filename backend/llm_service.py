"""
llm_service.py – Socrates Screen AI Engine

Uses the Groq SDK (OpenAI-compatible) for ultra-low-latency Llama 3 inference.
Falls back to Cerebras if GROQ_API_KEY is absent.

The system prompt is written to ensure:
  • Strict JSON output (parseable without markdown fences)
  • Indian regional cinema awareness (Bollywood, Tollywood, Kollywood, Mollywood)
  • Mood-to-genre mapping via the 3-Tap state
  • Respect for user dealbreakers / baseline preferences
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

from groq import AsyncGroq
from pydantic import BaseModel, Field

logger = logging.getLogger("llm_service")

# ---------------------------------------------------------------------------
# Pydantic I/O models
# ---------------------------------------------------------------------------

class BaselineProfile(BaseModel):
    """Captured during onboarding – persisted in localStorage on the client."""
    favorite_movies: list[str] = Field(default_factory=list)
    favorite_genres: list[str] = Field(default_factory=list)
    dealbreakers: list[str] = Field(default_factory=list)  # e.g. ["gore", "subtitles"]
    preferred_language: str = "any"                         # e.g. "Hindi", "English", "any"


class SessionState(BaseModel):
    """3-Tap selection for this recommendation session."""
    # Tap 1 – Energy / Mental mode
    energy: str  # "think" | "brain_off" | "feel"
    # Tap 2 – Reality anchor
    reality: str  # "grounded" | "escapism"
    # Tap 3 – Time commitment
    commitment: str  # "quick" | "epic"


class RecommendationRequest(BaseModel):
    baseline_profile: BaselineProfile
    session_state: SessionState
    seen_titles: list[str] = Field(
        default_factory=list,
        description="Titles already shown to the user — the LLM must exclude all of these.",
    )


class RecommendationOutput(BaseModel):
    title: str
    year: str
    reason: str  # 1–2 sentences, warm and personal


# ---------------------------------------------------------------------------
# System prompt – the heart of Socrates Screen
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are **Socrates Screen**, a world-class, deeply opinionated personal film curator.
Your entire personality is built around the belief that the perfect film for RIGHT NOW
exists — your job is to surface it from ALL of human cinema, not just Hollywood.

━━━ YOUR CINEMA UNIVERSE ━━━
You are as comfortable with:
• Bollywood / Hindi cinema (Golden Era, New Wave, modern blockbusters)
• Tollywood / Telugu cinema (Baahubali, RRR, Arjun Reddy, Pushpa)
• Kollywood / Tamil cinema (Mani Ratnam, Pa. Ranjith, Lokesh Kanagaraj universe)
• Mollywood / Malayalam cinema (the Renaissance wave: Jallikattu, Kumbalangi Nights, etc.)
• Kannada, Marathi, Bengali, Punjabi regional cinema
• Classic and contemporary Hollywood, European arthouse, Korean, Japanese, Iranian cinema
…as you are with prestige TV films or obscure festival darlings.

━━━ 3-TAP MOOD DECODER ━━━
The user's session state comes from 3 taps. Interpret them as follows:

ENERGY (Tap 1):
  • "think"     → Cerebral, layered narratives. Ambiguous endings welcome.
  • "brain_off" → Pure entertainment: action, comedy, masala, popcorn spectacle.
  • "feel"      → Emotionally resonant. Drama, romance, coming-of-age, grief.

REALITY (Tap 2):
  • "grounded"  → Realism, slice-of-life, true stories, naturalistic performances.
  • "escapism"  → Fantasy, sci-fi, mythology, over-the-top worlds.

COMMITMENT (Tap 3):
  • "quick"     → Under 110 minutes. Do not recommend anything longer.
  • "epic"      → 130 minutes or longer is fine. Sagas, sprawling narratives welcome.

Cross the three axes to derive a precise genre intersection:
  think + grounded + quick  → psychological thriller / noir short-form
  brain_off + escapism + epic → masala spectacle / superhero / fantasy blockbuster
  feel + grounded + quick   → intimate drama, short coming-of-age
  feel + escapism + epic    → epic romance, mythological drama
  …and so on. Use your taste.

━━━ STRICT RULES ━━━
1. DEALBREAKERS are absolute. If the user lists "gore", never pick a gore film. If "subtitles", only recommend films in their preferred_language or widely dubbed versions.
2. NEVER repeat a movie from favorite_movies list.
3. Prefer SPECIFIC, surprising picks over generic safe choices. Avoid recommending The Dark Knight, Inception, 3 Idiots unless they are genuinely the BEST fit and unambiguously superior.
4. Your recommendation must FEEL personal, as if you've watched the film yourself and know exactly why this user needs it tonight.
5. The "reason" field must be 1–2 warm, conversational sentences. No spoilers. No bullet points inside reason.

━━━ OUTPUT FORMAT ━━━
Respond with ONLY a valid JSON object containing a "films" array of exactly 3 recommendations.
No markdown fences, no preamble, no explanation:
{"films": [
  {"title": "Movie Title 1", "year": "YYYY", "reason": "..."},
  {"title": "Movie Title 2", "year": "YYYY", "reason": "..."},
  {"title": "Movie Title 3", "year": "YYYY", "reason": "..."}
]}

Rules for the 3 picks:
- Pick 1 is your STRONGEST recommendation — the most precise mood match.
- Pick 2 offers a different genre or regional cinema angle for the same mood.
- Pick 3 is a wildcard — surprising, less obvious, but still a perfect fit.
- No two picks from the same director, franchise, or decade unless unavoidable.
"""


# ---------------------------------------------------------------------------
# LLM client factory
# ---------------------------------------------------------------------------

def _build_groq_client() -> AsyncGroq:
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY is not set. "
            "Get a free key at https://console.groq.com/keys"
        )
    return AsyncGroq(api_key=api_key)


def _build_cerebras_client():
    """
    Cerebras uses an OpenAI-compatible endpoint.
    Install: pip install cerebras-cloud-sdk
    """
    try:
        from cerebras.cloud.sdk import AsyncCerebras  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "cerebras-cloud-sdk not installed. "
            "Run: pip install cerebras-cloud-sdk"
        ) from exc

    api_key = os.environ.get("CEREBRAS_API_KEY", "")
    if not api_key:
        raise EnvironmentError("CEREBRAS_API_KEY is not set.")
    return AsyncCerebras(api_key=api_key)


# ---------------------------------------------------------------------------
# Core recommendation function
# ---------------------------------------------------------------------------

def _build_user_prompt(req: RecommendationRequest) -> str:
    bp = req.baseline_profile
    ss = req.session_state

    favorites_str = (
        ", ".join(f'"{m}"' for m in bp.favorite_movies)
        if bp.favorite_movies
        else "none provided"
    )
    genres_str = (
        ", ".join(bp.favorite_genres) if bp.favorite_genres else "no preference"
    )
    dealbreakers_str = (
        ", ".join(bp.dealbreakers) if bp.dealbreakers else "none"
    )

    seen_str = ""
    if req.seen_titles:
        titles_list = "\n".join(f"- {t}" for t in req.seen_titles)
        seen_str = f"""

CRITICAL INSTRUCTION - ALREADY SEEN FILMS:
The user has already been recommended the following films in this session:
{titles_list}

DO NOT recommend these films again. You MUST pick 3 completely different films. If you repeat any of the films listed above, you have failed your objective."""

    action = "3 new and different" if req.seen_titles else "3"

    return f"""\
USER BASELINE PROFILE:
  Favourite movies: {favorites_str}
  Preferred genres: {genres_str}
  Dealbreakers: {dealbreakers_str}
  Preferred language: {bp.preferred_language}

CURRENT 3-TAP STATE:
  Tap 1 – Energy:     {ss.energy}
  Tap 2 – Reality:    {ss.reality}
  Tap 3 – Commitment: {ss.commitment}{seen_str}

Please recommend exactly {action} movies for right now, ordered from best fit to wildcard.
Return only the JSON object with the "films" array.
"""


def _extract_json(raw: str) -> dict[str, Any]:
    """
    Robustly extract a JSON object from LLM output.
    Handles spurious markdown fences that some models insert despite instructions.
    """
    cleaned = re.sub(r"```(?:json)?", "", raw).strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in LLM output: {raw!r}")
    return json.loads(match.group(0))


async def get_recommendation(req: RecommendationRequest) -> list[RecommendationOutput]:
    """
    Primary entry point called by the FastAPI route.
    Tries Groq first; falls back to Cerebras if GROQ_API_KEY is absent.
    Returns a list of 3 RecommendationOutput objects.
    """
    use_groq = bool(os.environ.get("GROQ_API_KEY"))
    use_cerebras = bool(os.environ.get("CEREBRAS_API_KEY"))

    if not use_groq and not use_cerebras:
        raise EnvironmentError(
            "No LLM API key configured. Set GROQ_API_KEY or CEREBRAS_API_KEY."
        )

    user_prompt = _build_user_prompt(req)

    if use_groq:
        raw_output = await _call_groq(user_prompt)
    else:
        raw_output = await _call_cerebras(user_prompt)

    logger.debug("Raw LLM output: %s", raw_output)
    data = _extract_json(raw_output)

    films_raw = data.get("films", [])
    if not films_raw:
        # Fallback: if model returned a single-film object, wrap it
        if "title" in data:
            films_raw = [data]
        else:
            raise ValueError(f"LLM returned unexpected structure: {data!r}")

    return [
        RecommendationOutput(
            title=f.get("title", "Unknown"),
            year=str(f.get("year", "")),
            reason=f.get("reason", ""),
        )
        for f in films_raw[:3]  # guard against model returning more than 3
    ]


async def _call_groq(user_prompt: str) -> str:
    client = _build_groq_client()
    # llama-3.3-70b-versatile: best quality at ~250 tok/s on Groq
    # llama-3.1-8b-instant: fastest, good for quick sessions
    model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

    completion = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.95,
        max_tokens=768,         # 3 picks × ~200 tokens each
        top_p=0.9,
        stream=False,
        response_format={"type": "json_object"},  # Groq enforces JSON mode
    )
    return completion.choices[0].message.content or ""


async def _call_cerebras(user_prompt: str) -> str:
    client = _build_cerebras_client()
    model = os.environ.get("CEREBRAS_MODEL", "llama3.1-70b")

    completion = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.85,
        max_tokens=768,
    )
    return completion.choices[0].message.content or ""
