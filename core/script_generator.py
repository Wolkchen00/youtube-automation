"""
Script Generator — Gemini-Powered Content Creation

Generates video scripts, titles, descriptions, and hashtags
using Google Gemini API. Each channel has its own system prompt.

Supports retry with model fallback for rate limits.
"""

import time
import json
import google.generativeai as genai

from .config import GEMINI_API_KEY, logger

# Gemini model priority: try primary, fallback to lite/older
GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash"]

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ─── Channel System Prompts ───────────────────────────────────────────────────

SYSTEM_PROMPTS = {
    "shadowedhistory": """You are a historian who uncovers forgotten, dusty secrets from history.
Your style is dark, mysterious, and captivating — like reading from ancient manuscripts by candlelight.
You create SHORT video scripts (30-60 seconds narration) about obscure historical facts.
Topics: lost civilizations, forgotten inventions, suppressed discoveries, mysterious disappearances,
dark secrets of famous figures, banned books that changed history.
Always write in English. Be dramatic but factual. Hook viewers in the first 3 seconds.
Format: Return a JSON object with keys: hook, narration, title, description, hashtags""",

    "sentinal_ihsan": """You are Sentinal Ihsan, a viral content creator known for incredible ocean discoveries,
animal rescues, and finding impossible things in nature. You always appear in your own videos.
Your brand: You're a modern-day ocean explorer who discovers surreal, mind-blowing things on beaches, 
in the ocean, and from your boat. You rescue marine animals (baby dolphins, sea turtles, seals).
Settings: beaches, boats, ocean, cliffs, coastal roads (motorcycle rides), golden hour lighting.
Style: hyper-realistic, emotional, POV/selfie angles, curiosity-gap hooks.
Example hooks: "I couldn't believe what washed up on the beach today...", 
"Far offshore, something impossible happened...", "This creature needed help - watch what I did..."
Always write in English. Be dramatic but genuine. ALWAYS include Sentinal Ihsan as the protagonist.
Format: Return a JSON object with keys: hook, scene_descriptions (list of 4-5 scene descriptions that 
include Sentinal Ihsan in the scene), title, description, hashtags""",

    "galactic_experiment": """You are a cosmic narrator who makes space feel real and terrifying.
Your channel creates visual spectacles about space — simulations, hypotheticals, and real events.
Topics: "What if the Sun disappeared?", "A black hole appears near Earth",
"What would happen if a neutron star entered our solar system?",
NASA discoveries, ISS events, Mars missions, exoplanet findings.
Always write in English. Be scientifically accurate but dramatically cinematic.
Format: Return a JSON object with keys: hook, narration, scene_descriptions (list of 4-5),
title, description, hashtags""",

    "aimagine": """You are a visual artist who creates mesmerizing, satisfying loop videos.
Your content is hypnotic — videos where the beginning and end are the same frame,
creating an infinite loop effect. No narration needed.
Topics: morphing objects, endless staircases, rotating mechanical structures,
nature cycles (water, fire, clouds), abstract art transformations,
satisfying construction loops, impossible geometry, fractal animations.
Always write in English. Focus on VISUAL descriptions, not narration.
Format: Return a JSON object with keys: concept_name, loop_description,
start_end_frame_prompt (the shared start/end frame),
intermediate_prompts (list of 2-3 intermediate stages),
title, description, hashtags"""
}


def _call_gemini(system_prompt: str, user_prompt: str, temperature: float = 0.9) -> dict | list | None:
    """Call Gemini with automatic model fallback on rate limits."""
    last_error = None

    for model_name in GEMINI_MODELS:
        try:
            model = genai.GenerativeModel(
                model_name,
                system_instruction=system_prompt,
            )

            response = model.generate_content(
                user_prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=temperature,
                ),
            )

            result = json.loads(response.text)
            logger.info(f"  Gemini OK ({model_name})")
            return result

        except Exception as e:
            last_error = e
            error_str = str(e).lower()
            if "quota" in error_str or "rate" in error_str or "429" in error_str or "resource" in error_str:
                logger.warning(f"  {model_name} rate limited, trying next...")
                time.sleep(5)
                continue
            else:
                logger.error(f"  Gemini error: {e}")
                return None

    logger.error(f"All Gemini models failed: {last_error}")
    return None


def generate_script(channel: str, topic: str) -> dict | None:
    """Generate a video script using Gemini."""
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not set!")
        return None

    system_prompt = SYSTEM_PROMPTS.get(channel)
    if not system_prompt:
        logger.error(f"No system prompt for channel: {channel}")
        return None

    user_prompt = f"""Create a viral short video script about: {topic}

Remember:
- Hook must grab attention in the first 3 seconds
- Content must be in English
- Video format is vertical (9:16) for YouTube Shorts / Instagram Reels / TikTok
- Keep it between 30-90 seconds of content
- Return ONLY valid JSON, no markdown fences"""

    result = _call_gemini(system_prompt, user_prompt, temperature=0.9)
    if result and isinstance(result, dict):
        logger.info(f"Script generated for {channel}: {result.get('title', topic)[:50]}...")
        return result
    return None


def generate_visual_prompts(channel: str, script: dict) -> list[dict] | None:
    """Generate detailed visual prompts from a script using Gemini."""
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not set!")
        return None

    system_prompt = """You are a visual prompt engineer for AI image and video generation.
Given a video script, create detailed frame-by-frame visual prompts.
Each frame prompt must be highly detailed, photorealistic, and cinematic.
Always specify: camera angle, lighting, color palette, atmosphere, details.
Format: 9:16 vertical. Style: cinematic, high quality, 4K.
Return ONLY valid JSON array of objects with keys: frame_number, frame_prompt, video_prompt, duration_seconds"""

    script_text = json.dumps(script, ensure_ascii=False)
    user_prompt = f"Create 4-6 detailed visual frame prompts for this video script:\n{script_text}\n\nReturn ONLY valid JSON array."

    result = _call_gemini(system_prompt, user_prompt, temperature=0.7)

    if result:
        if isinstance(result, dict) and "frames" in result:
            result = result["frames"]
        if not isinstance(result, list):
            result = [result]
        logger.info(f"Generated {len(result)} visual prompts")
        return result

    return None
