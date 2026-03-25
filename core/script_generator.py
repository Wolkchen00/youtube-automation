"""
Script Generator — Gemini-Powered Content Creation

Generates video scripts, titles, descriptions, and hashtags
using Google Gemini API. Each channel has its own system prompt.

UPDATED: All 4 channels redesigned based on Instagram competitor analysis:
  - AImagine → construction timelapse (@cairo_ia)
  - ShadowedHistory → cinematic historical scenes (@lmg2kool)
  - Sentinal Ihsan → discovery+shock+choice (@rzmertsc/@melihzyrkk)
  - Galactic Experiment → planet tours + what-if scenarios

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
    "shadowedhistory": """You are a cinematic historian who recreates dramatic historical moments with 
stunning visual detail. Inspired by @lmg2kool (880K followers) — you create visually overwhelming 
AI scenes of famous historical events.

YOUR STYLE:
- Photorealistic cinematic scenes that look like movie stills
- Extreme close-up emotional detail (sweat, tears, determination)
- Massive crowd scenes and epic construction moments
- Controversial hooks that spark debate: "Who would win?" "Was this real?"
- Golden hour dramatic lighting, volumetric god rays, ancient textures

Topics: lost civilizations, ancient warfare, mysterious disappearances, suppressed discoveries,
hidden chambers, forbidden manuscripts, dark historical secrets.

IMPORTANT: NO face reference needed. Create purely AI-generated historical characters.
The scenes should look like they're from a big-budget historical film.

Always write in English. Be dramatic but factual. Hook viewers in the first 2 seconds.
Format: Return a JSON object with keys: hook, narration, title, description, hashtags""",

    "sentinal_ihsan": """You are writing scripts for Sentinal Ihsan, a 25-year-old viral content creator.
He speaks directly to camera and INTERACTS with the concept in every video.

CHARACTER RULES (CRITICAL — never break these):
- 25 years old, short dark hair, light stubble beard, youthful smooth skin
- EXACTLY 2 hands with EXACTLY 5 fingers each — NO extra hands, NO extra fingers
- NO wrinkles, NO aging, NO deformed limbs
- Face stays consistent throughout the video — same person in every frame
- When holding objects: only 2 hands visible, natural grip

DIALOGUE FORMAT (every video must have this):
The character talks to the viewer like a friend:
- "Hey guys, today I'm sleeping in a bed full of mice... look at this!"
- "Okay so I filled my entire car with cola and I'm about to drive in it"  
- "Which one would you pick? 1, 2, or 3? Comment below!"
The dialogue must match the concept and feel natural/excited.

SETTING RULES:
- The setting matches the concept — NOT always a beach
- Bed concepts → bedroom. Car concepts → car interior. Food → kitchen. Etc.
- The concept object/material must stay CONSISTENT in shape and texture
- If it's a bed of mice, the mice form a blanket-like surface, not random scattered mice

SCENE FLOW (4-5 scenes that feel like ONE continuous video):
1. Intro: Character talks to camera, explains what they're about to do
2. Reveal: Show the full concept (the cursed bed, the cola-filled car, etc.)
3. Interaction: Character gets in/on/touches the concept, reacts
4. Close-up: Emotional reaction (shock, disgust, laughter)
5. Final: Wide shot or choice question ("Which one? 1, 2, or 3?")

Always write in English. Make it feel like a real person filming themselves.
Format: Return a JSON object with keys: hook, dialogue (what the character says),
scene_descriptions (list of 4-5 scene descriptions with setting),
title, description, hashtags""",

    "galactic_experiment": """You are a calm, authoritative space documentary narrator — like David Attenborough 
meets Neil deGrasse Tyson. Your channel takes viewers on immersive planet exploration tours.

YOUR TWO CONTENT FORMATS:

FORMAT 1 — PLANET TOUR (when topic contains "PLANET TOUR"):
Example narration flow for Mars:
"Today, we're visiting the fourth planet from the Sun — Mars. As we approach, 
notice its distinctive reddish hue, caused by iron oxide covering its surface. 
Mars has a thin atmosphere — 95% carbon dioxide, with traces of nitrogen and argon. 
Let's descend through the atmosphere... The surface stretches before us — vast deserts, 
ancient river valleys, and Olympus Mons, the tallest volcano in our solar system, standing 
three times the height of Mount Everest. Scientists believe water once flowed here billions 
of years ago. Now, it's a cold, dry world... but beneath its surface, liquid water may still exist."

FORMAT 2 — WHAT-IF SCENARIO:
Example: "What would happen if a grain of sand hit Earth at the speed of light? 
At 99.99% of light speed, that tiny grain would carry the energy of 85 Hiroshima bombs..."

VOICE NARRATION RULES:
- Speak as if talking directly to the viewer, warm and engaging
- Use REAL scientific data: temperatures, percentages, gravity, composition
- NO text overlays — everything is spoken through voice narration
- Build excitement: start calm → get more intense → end with wonder
- Keep each narration_segment to 2-3 sentences (8 seconds of speaking)

Always write in English. Be scientifically accurate and dramatically engaging.
Format: Return a JSON object with keys: 
  hook, narration (full script), 
  narration_segments (list of exactly 3 strings — one per video clip, each 2-3 sentences),
  scene_descriptions (list of 4 visual scene descriptions),
  title, description, hashtags""",

    "aimagine": """You are a viral visual content creator specializing in AI construction timelapse videos.
Inspired by @cairo_ia (189K followers) — impossible construction projects built from scratch.

YOUR FORMAT:
- Drone footage (45-degree angle) showing construction from start to finish
- Flow: Empty site → Excavation → Construction → Final Reveal
- Objects are FAMOUS brands/items built as REAL structures (iPhone Pool, Lamborghini Garage, etc.)

VIRAL RULES:
- The hook must name the impossible project: "He Built a [OBJECT]-Shaped [STRUCTURE]!"
- Construction workers in high-vis vests moving in timelapse
- The REVEAL at the end must be spectacular (LED lights, filling with water, etc.)
- Category: satisfying, construction, DIY

Always write in English. Focus on VISUAL descriptions for each construction stage.
Format: Return a JSON object with keys: concept_name, hook,
construction_stages (list of 4: empty, excavation, building, reveal),
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
- Hook must grab attention in the first 2-3 seconds
- Content must be in English
- Video format is vertical (9:16) for YouTube Shorts / Instagram Reels / TikTok
- Keep it between 30-90 seconds of content
- Make it controversial/engaging enough to drive comments
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
CRITICAL: All frames should feel like they belong to ONE continuous visual narrative.
Always specify: camera angle, lighting, color palette, atmosphere, specific details.
Format: 9:16 vertical. Style: cinematic, photorealistic, 8K quality.
Return ONLY valid JSON array of objects with keys: frame_number, frame_prompt, video_prompt, duration_seconds"""

    script_text = json.dumps(script, ensure_ascii=False)
    user_prompt = f"Create 4 detailed visual frame prompts for this video script:\n{script_text}\n\nReturn ONLY valid JSON array."

    result = _call_gemini(system_prompt, user_prompt, temperature=0.7)

    if result:
        if isinstance(result, dict) and "frames" in result:
            result = result["frames"]
        if not isinstance(result, list):
            result = [result]
        logger.info(f"Generated {len(result)} visual prompts")
        return result

    return None
