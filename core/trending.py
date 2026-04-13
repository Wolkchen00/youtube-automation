"""
Trending Topic Hook — Gemini-Powered Trend Integration

Queries Gemini to identify current trending topics and generates
hook keywords to append to video titles for better discoverability.

Used by script_generator.py to boost titles with trending context.
"""

import json
import time
from datetime import date, timedelta
from pathlib import Path

import google.generativeai as genai

from .config import GEMINI_API_KEY, PROJECT_ROOT, logger

# Cache file — refresh once per day
TRENDING_CACHE = PROJECT_ROOT / "logs" / "trending_cache.json"
CACHE_TTL_HOURS = 12

CHANNEL_NICHES = {
    "shadowedhistory": "history, ancient civilizations, mysteries, archaeology, dark history",
    "sentinal_ihsan": "viral experiments, DIY hacks, satisfying transformations, life hacks, product tests",
    "galactic_experiment": "space, astronomy, planets, universe, NASA, black holes, alien life",
    "aimagine": "architecture, construction, luxury homes, interior design, dream houses, off-grid living",
}

TRENDING_PROMPT = """You are a YouTube Shorts trend analyst. Your job is to identify 
what's CURRENTLY trending on YouTube Shorts, TikTok, and Instagram Reels.

For the niche: {niche}

Generate exactly 5 trending hook phrases that can be appended to video titles 
to boost discoverability. These should be:
- Currently viral or trending keywords/phrases
- Relevant to the niche
- Short (2-4 words each)
- Include trending challenge names, viral sounds references, or hot topics

Also generate 5 trending hashtags for this niche.

Respond in this exact JSON format:
{{
    "hooks": ["hook1", "hook2", "hook3", "hook4", "hook5"],
    "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
    "trending_topic": "Brief description of the hottest trend right now"
}}
"""


def _load_cache() -> dict:
    """Load trending cache from disk."""
    if not TRENDING_CACHE.exists():
        return {}
    try:
        data = json.loads(TRENDING_CACHE.read_text(encoding="utf-8"))
        # Check if cache is still fresh
        cached_date = data.get("date", "")
        if cached_date == date.today().isoformat():
            return data
        return {}  # Stale cache
    except Exception:
        return {}


def _save_cache(data: dict):
    """Save trending cache to disk."""
    data["date"] = date.today().isoformat()
    TRENDING_CACHE.parent.mkdir(parents=True, exist_ok=True)
    TRENDING_CACHE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def get_trending_hooks(channel: str) -> dict:
    """Get trending hooks and hashtags for a channel.

    Returns:
        {"hooks": [...], "hashtags": [...], "trending_topic": "..."}
    """
    # Check cache first
    cache = _load_cache()
    cached_channel = cache.get(channel)
    if cached_channel:
        logger.info(f"🔥 Trending hooks (cached): {cached_channel.get('hooks', [])[:3]}")
        return cached_channel

    # Query Gemini for fresh trends
    niche = CHANNEL_NICHES.get(channel, "general viral content")

    if not GEMINI_API_KEY:
        logger.warning("⚠️ No Gemini API key — skipping trending hooks")
        return {"hooks": [], "hashtags": [], "trending_topic": ""}

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")

        response = model.generate_content(
            TRENDING_PROMPT.format(niche=niche),
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.9,
            ),
        )

        result = json.loads(response.text)
        logger.info(f"🔥 Fresh trending hooks for {channel}: {result.get('hooks', [])[:3]}")

        # Save to cache
        cache[channel] = result
        _save_cache(cache)

        return result

    except Exception as e:
        logger.warning(f"⚠️ Trending hook fetch failed: {e}")
        return {"hooks": [], "hashtags": [], "trending_topic": ""}


def enhance_title_with_trend(title: str, channel: str) -> str:
    """Add a trending hook to a video title if possible.

    Keeps title under 100 chars for YouTube optimization.
    """
    trends = get_trending_hooks(channel)
    hooks = trends.get("hooks", [])

    if not hooks:
        return title

    import random
    hook = random.choice(hooks[:3])  # Pick from top 3

    enhanced = f"{title} — {hook}"
    if len(enhanced) > 100:
        enhanced = f"{title} | {hook}"
    if len(enhanced) > 100:
        return title  # Original title already long enough

    return enhanced


def get_trending_hashtags(channel: str) -> str:
    """Get trending hashtags string for a channel."""
    trends = get_trending_hooks(channel)
    hashtags = trends.get("hashtags", [])
    return " ".join(hashtags) if hashtags else ""
