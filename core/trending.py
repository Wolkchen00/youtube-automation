"""
Trending Topic Engine — Gemini-Powered Trend-Based Topic Selection

UPGRADED: No longer just hooks/hashtags — now the PRIMARY topic selector.
Each channel gets a daily topic based on real-time trends + proven viral patterns.

Flow:
  1. Ask Gemini what's trending today for the channel's niche
  2. Combine trend with the channel's proven viral FORMAT (from analytics)
  3. Return a complete topic ready for script generation
  4. Fallback: original static topic lists if Gemini fails

Used by each channel's topics.py / competitor.py as the primary selector.
"""

import json
import time
import random
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

# ─── Proven Viral Patterns (from channel analytics) ─────────────────────────

VIRAL_PATTERNS = {
    "sentinal_ihsan": {
        "top_formats": [
            '"I Found/Tried [X]" + mystery/gizem element',
            '"Can I Turn [A] Into [B]?!" transformation format',
            '"[X] + [Unexpected Material] = INSANE Result!"',
            'Satisfying experiment with unexpected outcome',
        ],
        "proven_hooks": [
            "UPPERCASE keywords for key words (UNNATURAL, PERFECT, DISASTER, BRICK)",
            "Emoji usage: 🤯 especially effective",
            "First-person discovery narrative",
            "Before→After transformation reveal",
        ],
        "top_categories": ["experiment", "transformation", "satisfying", "discovery"],
        "example_hits": [
            "I Found UNNATURAL Objects on the Beach... And They STARTED To Change! (3.3K)",
            "I Tried to Carve a PERFECT Jell-O Cube (It Was a DISASTER) (1.9K)",
            "Can I Turn A Sponge Into A BRICK?! (Polymer Injection) (1.4K)",
            "Anti-Gravity Oobleck Tower Challenge (1.4K)",
        ],
    },
    "shadowedhistory": {
        "top_formats": [
            '"The [Hidden/Real/Secret] Story of [X]" reveal format',
            'Abandoned/forgotten places and their dark stories',
            '"How [Impossible Thing] Actually Happened" engineering marvel',
            '"[Ancient Weapon/Method]: The Science of [X]" format',
            '"Fact or [Ancient Propaganda]?" question format',
        ],
        "proven_hooks": [
            "Abandoned/dark places = HIGHEST views (4.3K #1 video)",
            "Ancient warfare & weapons = consistent performers",
            "Irony & paradox titles (doctor jailed for saving lives)",
            "Question-asking titles drive curiosity",
        ],
        "top_categories": ["abandoned_places", "ancient_warfare", "engineering_marvels", "dark_history"],
        "example_hits": [
            "The history of north brother island (4.3K)",
            "How Ships Crossed Land in 1453! (1.6K)",
            "Forging a Samurai Katana! (1.6K)",
            "The Real Reason Pirates Wore Eye Patches (1.5K)",
        ],
    },
    "galactic_experiment": {
        "top_formats": [
            '"[Planet/Star]\'s [Sleeping/Hidden] [Giant/Secret]: [Name]" format',
            '"What If [Impossible Cosmic Scenario]?" speculation',
            '"The Universe\'s [Biggest/Final/Inevitable] [X]" epic scale',
            '"[Planet] [Dramatic Action]: [Poetic Description]" format',
        ],
        "proven_hooks": [
            "Apocalypse/destruction scenarios = top performers",
            "MASSIVE scale structures (Olympus Mons = #1 at 4.2K)",
            "Time compression ('13.8 Billion Years in 60 Seconds')",
            "'What If' scenarios drive engagement",
            "Mysterious cosmic voids/structures = curiosity gap",
        ],
        "top_categories": ["apocalypse", "megastructures", "what_if", "cosmic_mystery"],
        "example_hits": [
            "Mars' Sleeping Giant: Olympus Mons (4.2K)",
            "The Universe's Entire 13.8 Billion Year History in 60 Seconds (1.7K)",
            "Earth's Fiery End: The Sun's Inevitable Betrayal (1.7K)",
            "What if Earth Had Rings? Beauty and Terror (1.5K)",
        ],
    },
    "aimagine": {
        "top_formats": [
            '"Building a [UNUSUAL/FANTASY THING] From Scratch!" + emoji format',
            '"Building a [SHAPE]-Shaped [STRUCTURE]!" unique shape',
            '"He Turned a [TRASH] Into an EPIC [LUXURY]!" transformation',
            '"[BRAND/GAME] [Object] IRL! Building [Method]!" crossover',
        ],
        "proven_hooks": [
            "'Building X From Scratch' is THE winning format (3/4 top videos)",
            "Fantasy/unusual subjects (Hobbit Hole = #1 at 5K)",
            "Emoji pairs matching the subject 🧙‍♂️🌿🎸🏊🦖",
            "Cultural/gaming crossovers (Minecraft House IRL)",
            "'In 30 Seconds' speed element for food content",
        ],
        "top_categories": ["fantasy_builds", "unique_shapes", "crossover_builds", "transformation"],
        "example_hits": [
            "Building a Hobbit Hole From Scratch! 🧙‍♂️🌿 (5K)",
            "Building a GUITAR Pool From Scratch! 🎸🏊 (4.6K)",
            "Building a DINOSAUR Playground! 🦖🏗️ (3.7K)",
            "Minecraft House IRL! Building Block by Block! (1.8K)",
        ],
    },
}

# ─── Trending Topic Prompt (the core engine) ────────────────────────────────

TRENDING_TOPIC_PROMPT = """You are a YouTube Shorts trend analyst AND viral content strategist.

CHANNEL NICHE: {niche}

YOUR JOB: Generate ONE unique video topic that combines:
1. Something CURRENTLY trending on YouTube, TikTok, Google Trends, or in the news TODAY
2. The channel's PROVEN viral format (based on analytics of what actually gets views)

PROVEN VIRAL PATTERNS FOR THIS CHANNEL:
{viral_patterns}

TOP PERFORMING EXAMPLES (with actual view counts):
{example_hits}

RULES:
- The topic MUST feel timely/relevant to TODAY (reference current events, trends, memes)
- The topic MUST follow the channel's proven viral FORMAT (the structure that gets views)
- Combine the trend with the format: e.g., if trend is "Baldur's Gate" and format is "Building X From Scratch",
  then: "Building BALDUR'S GATE Castle From Scratch! 🏰⚔️"
- Make the title include UPPERCASE keywords for key words
- Include relevant emoji in the title
- Be SPECIFIC — generic topics get 0 views

{extra_instructions}

Respond in this exact JSON format:
{{
    "topic": "Full detailed description of the video topic (2-3 sentences with specifics)",
    "title": "The exact YouTube title (under 100 chars, with emoji, UPPERCASE keywords)",
    "category": "One of: {categories}",
    "trending_hook": "What current trend this connects to (1 sentence)",
    "setting": "Where this would be filmed/set",
    "action_steps": "What physically happens in the video (for non-narration channels)"
}}"""

# Channel-specific extra instructions
CHANNEL_EXTRA = {
    "sentinal_ihsan": (
        "EXTRA RULES FOR SENTINAL IHSAN:\n"
        "- Topic must involve PHYSICAL INTERACTION (painting, pouring, building, crushing)\n"
        "- Character films with front camera, talking to viewers\n"
        "- Must have a satisfying VISUAL PAYOFF at the end\n"
        "- Think: what would a 25yo guy want to try that looks INSANE on camera?"
    ),
    "shadowedhistory": (
        "EXTRA RULES FOR SHADOWEDHISTORY:\n"
        "- Topic must be a REAL historical event, place, or person\n"
        "- Include the REAL geographic location\n"
        "- Favor abandoned places, dark history, ancient warfare, or engineering marvels\n"
        "- The title should create a CURIOSITY GAP — make viewers NEED to know more"
    ),
    "galactic_experiment": (
        "EXTRA RULES FOR GALACTIC EXPERIMENT:\n"
        "- Topic must be scientifically accurate (use real data, temperatures, distances)\n"
        "- Favor apocalypse scenarios, massive structures, or cosmic mysteries\n"
        "- Include at least one specific scientific fact in the topic description\n"
        "- The narration should build WONDER and end with an existential question"
    ),
    "aimagine": (
        "EXTRA RULES FOR AIMAGINE:\n"
        "- Topic must be a CONSTRUCTION/BUILDING project\n"
        "- The structure must be something UNUSUAL or FANTASY (not a normal house)\n"
        "- Use 'Building [X] From Scratch!' format whenever possible\n"
        "- Include construction stages: excavation → foundation → build → reveal\n"
        "- The final reveal should be SPECTACULAR (lights, water, landscaping)"
    ),
}


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


def generate_trending_topic(channel: str) -> dict | None:
    """Generate a trending topic for a channel using Gemini + viral analytics.

    This is the PRIMARY topic selector — replaces static lists.
    Falls back to None so callers can use their static lists as backup.

    Returns:
        {"topic": str, "title": str, "category": str, "trending_hook": str,
         "setting": str, "action_steps": str} or None
    """
    # Check cache first (one topic per channel per day)
    cache = _load_cache()
    cache_key = f"trending_topic_{channel}"
    cached = cache.get(cache_key)
    if cached:
        logger.info(f"🔥 Trending topic (cached): {cached.get('title', '')[:50]}")
        return cached

    if not GEMINI_API_KEY:
        logger.warning("⚠️ No Gemini API key — cannot generate trending topic")
        return None

    niche = CHANNEL_NICHES.get(channel, "general viral content")
    patterns = VIRAL_PATTERNS.get(channel, {})
    extra = CHANNEL_EXTRA.get(channel, "")

    # Build the prompt with analytics data
    viral_pattern_text = "\n".join(
        f"  - {fmt}" for fmt in patterns.get("top_formats", [])
    )
    hooks_text = "\n".join(
        f"  - {h}" for h in patterns.get("proven_hooks", [])
    )
    example_text = "\n".join(
        f"  - {ex}" for ex in patterns.get("example_hits", [])
    )
    categories = ", ".join(patterns.get("top_categories", ["general"]))

    full_patterns = f"WINNING FORMATS:\n{viral_pattern_text}\n\nPROVEN HOOKS:\n{hooks_text}"

    prompt = TRENDING_TOPIC_PROMPT.format(
        niche=niche,
        viral_patterns=full_patterns,
        example_hits=example_text,
        extra_instructions=extra,
        categories=categories,
    )

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")

        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=1.0,  # High creativity for trending topics
            ),
        )

        result = json.loads(response.text)

        if result and result.get("topic"):
            logger.info(f"🔥 Trending topic for {channel}: {result.get('title', '')[:60]}")
            logger.info(f"   Trend hook: {result.get('trending_hook', 'N/A')[:60]}")

            # Cache it for the day
            cache[cache_key] = result
            _save_cache(cache)

            return result

    except Exception as e:
        logger.warning(f"⚠️ Trending topic generation failed for {channel}: {e}")

    return None


# ─── Legacy functions (kept for backward compatibility) ─────────────────────

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
}}"""


def get_trending_hooks(channel: str) -> dict:
    """Get trending hooks and hashtags for a channel.

    Returns:
        {"hooks": [...], "hashtags": [...], "trending_topic": "..."}
    """
    # Check cache first
    cache = _load_cache()
    cached_channel = cache.get(channel)
    if cached_channel and "hooks" in cached_channel:
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
