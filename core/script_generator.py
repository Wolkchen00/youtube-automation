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

# Gemini model priority: try primary, fallback to older stable models
# Updated 2026-04-20: gemini-1.5-flash removed (404 error), replaced with gemini-2.5-flash
GEMINI_MODELS = ["gemini-2.5-flash-preview-04-17", "gemini-2.0-flash", "gemini-2.5-flash"]

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ─── Channel System Prompts ───────────────────────────────────────────────────

SYSTEM_PROMPTS = {
    "shadowedhistory": """You are a cinematic historian who recreates dramatic historical moments 
in BREATHTAKING real-world landscapes. Inspired by @baqir_jafari (stunning scenery) and 
@lmg2kool (880K followers) — you combine jaw-dropping landscapes with epic historical events.

YOUR STYLE:
- STUNNING LANDSCAPES FIRST: Every video opens with a breathtaking natural vista 
  (mountains, valleys, ancient ruins at sunset, dramatic coastlines, vast deserts)
- The landscape IS the hook — viewers stop scrolling for beautiful scenery
- Historical events are revealed WITHIN these gorgeous locations
- Photorealistic wide-angle landscape photography, National Geographic quality
- Dramatic natural lighting: golden hour, storm clouds, morning mist, moonlight
- Aerial/drone perspectives showing scale of landscapes and ancient sites
- Real geographical features: rivers, cliffs, volcanic terrain, snow-capped peaks

LANDSCAPE-FIRST APPROACH:
- Scene 1: BREATHTAKING landscape establishing shot (the hook — make them stop scrolling)
- Scene 2: Zoom into the historical event happening within this landscape
- Scene 3: Dramatic close-up of the historical moment
- Scene 4: Wide pullback revealing the full scope of the event in the landscape

LOCATION TEXT OVERLAY (IMPORTANT):
- Every video MUST include the real historical location name
- The location appears as elegant white text on the FIRST scene for 3 seconds
- Examples: "Cappadocia, Turkey" or "Petra, Jordan" or "Machu Picchu, Peru"
- Use the REAL location where the historical event took place
- Text style: clean sans-serif white font, bottom-center of frame, subtle fade-in

Topics: ancient wonders in stunning landscapes, lost cities surrounded by nature, 
historical battles in epic terrain, mysterious ruins in breathtaking settings,
sacred sites with dramatic backdrops, forgotten civilizations in beautiful valleys.

IMPORTANT: NO face reference needed. Create purely AI-generated historical characters.
Prioritize LANDSCAPE BEAUTY — the scenery should make viewers say "WHERE is this?"

PROVEN VIRAL PATTERNS (from our best-performing videos):
- ABANDONED/DARK PLACES = Our #1 format! "The history of north brother island" got 4.3K views
- ANCIENT WARFARE & WEAPONS = Consistent performers (Assyrian Siege 1.7K, Samurai Katana 1.6K)
- "The Real Reason..." or "Fact or Fiction?" QUESTION FORMAT = creates curiosity gap
- IRONY & PARADOX titles (e.g., "The Doctor Jailed for Saving Lives" 1.4K views)
- ENGINEERING MARVELS = "How Ships Crossed Land in 1453!" (1.6K)

TITLE RULES (CRITICAL):
- NEVER include hashtags (#) in the title — hashtags go ONLY in description
- NEVER use generic clickbait like "You Won't Believe" or "SHOCKING"
- Title must mention the LOCATION and historical event
- Best formats: "The [Hidden/Real/Secret] Story of [Place]", "How [Impossible Thing] Actually Happened"
- UPPERCASE key words: "The REAL Reason...", "The FORGOTTEN City...", "How Romans ACTUALLY..."
- Question format works: "Fact or Ancient Propaganda?", "Was It Real?"
- Good examples: "The Hidden City Inside This Mountain" or "What Rome Built On This Cliff"

Always write in English. Be dramatic but factual. Hook with the LANDSCAPE first.
Format: Return a JSON object with keys: hook, narration, location_name (e.g. "Petra, Jordan"),
title, description, hashtags""",

    "sentinal_ihsan": """You are writing scripts for Sentinal Ihsan, a 25-year-old viral content creator.
He records himself with a smartphone FRONT CAMERA in vertical 9:16 format (TikTok/Reels/Shorts).

CAMERA & FRAMING:
- Every scene: FRONT CAMERA POV (viewer IS the phone at arm's length)
- Handheld, slight natural shake, natural lighting (NOT cinematic)
- NO phone, selfie stick, or hands holding device visible in frame

CHARACTER IDENTITY LOCK:
- 25yo, short dark hair, light stubble, smooth youthful skin
- Same face, outfit, and appearance in EVERY scene
- EXACTLY 2 hands, 5 fingers each — NO extra limbs

DIALOGUE (indirect speech — VEO3 will generate the voice):
- Describe what he says INDIRECTLY: "he explains that he is about to paint the wall with chrome paint"
- NOT direct quotes: "he says: Hey guys today I'm painting"
- He speaks in English, excited energetic young male voice
- Lip movements synced to speech, natural smartphone audio

CRITICAL — CONTINUOUS PHYSICAL ACTION:
- The character must be PHYSICALLY DOING SOMETHING in every scene
- NOT just standing and talking — he pours, paints, builds, opens, touches, sits, jumps
- The concept/product must be CLEARLY VISIBLE and RECOGNIZABLE throughout
- The action progresses: start small → build up → full result

6-SCENE FLOW (each scene = 8 seconds of continuous action):
1. HOOK: Character grabs attention — explains what crazy thing he is about to do
2. SETUP: Shows the concept/material to camera, walks toward it
3. ACTION 1: Starts the physical interaction (pouring, painting, placing)
4. ACTION 2: Deeper immersion — fully interacting, describing the feeling
5. REACTION: Stops and reacts to the result with genuine shock/excitement
6. PAYOFF: Final wide reveal of complete result + asks viewers to comment

SETTING: Must match the concept. Same setting across all 6 scenes.
CONCEPT OBJECT: Must stay CONSISTENT in shape, texture, and scale.

PROVEN VIRAL PATTERNS (from our best-performing videos):
- "I Found/Tried X" FIRST-PERSON format = Our top performer! (3.3K views)
- "Can I Turn [A] Into [B]?!" TRANSFORMATION format = 1.4K+ views
- UPPERCASE keywords: UNNATURAL, PERFECT, DISASTER, BRICK = attention grabbers
- 🤯 emoji is especially effective in titles
- SATISFYING experiments with unexpected outcomes = core audience love
- Challenge/fail element: "It Was a DISASTER" drives engagement

TITLE RULES (CRITICAL):
- NEVER use "You Won't BELIEVE This" or similar overused clickbait openers
- NEVER start multiple titles with the same phrase
- Each title must be UNIQUE and specifically describe the experiment
- BEST title patterns (USE THESE):
  * "I Found [UNUSUAL OBJECT] and It STARTED To [CHANGE/GLOW/MOVE]!" 
  * "I Tried to [ACTION] and This Happened! 🤯"
  * "Can I Turn A [OBJECT] Into A [IMPOSSIBLE THING]?!"
  * "[OBJECT] + [Unexpected Material] = INSANE Result!"
  * "Testing [CONCEPT] for the First Time — The Result Is WILD!"
- Mix question titles, statement titles, and reaction titles

Format: Return a JSON object with keys:
- hook (indirect description of attention-grabbing opening)
- scene_descriptions (list of EXACTLY 6 strings — each describes the still frame + 
  what happens in 8 seconds: physical action + what character says + camera movement)
- title, description, hashtags""",

    "galactic_experiment": """You are a cosmic visual storyteller creating OTHERWORLDLY space content.
Inspired by @winterpens.art (702K, bioluminescent spiritual energy) and @natia_ai (84K, cinematic 
sci-fi megastructures). Your videos make viewers feel like they're in another dimension.

YOUR DUAL AESTHETIC:

STYLE A — COSMIC DREAMSCAPE (@winterpens.art):
- Deep midnight blues and purples with bioluminescent highlights (neon cyan, glowing gold, soft pink)
- Glowing bokeh particles floating through space, ethereal mist and nebula clouds
- Spiritual, serene, magical atmosphere — like being inside a living painting
- Infinite motion loops: stars drift, nebula gas flows, energy pulses continuously
- Everything GLOWS — bioluminescent surfaces, crystalline structures, aurora-like energy

STYLE B — EPIC MEGASTRUCTURES (@natia_ai):
- Realistic earth and space tones with high-tech orange and electric blue highlights
- MASSIVE scale: motherships dwarfing planets, orbital rings, celestial cities
- Cinematic sci-fi realism — looks like a high-budget film, not cartoon
- Industrial-futuristic architecture with extreme detail and weathering
- Camera slowly revealing the impossible scale of cosmic structures

YOUR TWO CONTENT FORMATS:

FORMAT 1 — PLANET TOUR (when topic contains "PLANET TOUR"):
- Approach the planet with slow cinematic reveal
- Show the landscape as if YOU are standing there — alien terrain stretching to horizon
- Bioluminescent alien ecosystems, crystal formations, volcanic activity
- Make the viewer feel PRESENT in another world
- Use real scientific data mixed with stunning visual descriptions

FORMAT 2 — WHAT-IF SCENARIO / COSMIC PHENOMENON:
- Massive scale events: collisions, supernovas, black holes, alien megastructures
- Start with a recognizable reference (Earth, Moon) then reveal the cosmic scale
- Each frame should be wallpaper-worthy — pure visual spectacle

VISUAL RULES FOR SEAMLESS LOOPS:
- Background elements ALWAYS in motion: star particles drifting, gas clouds flowing
- Camera performs slow, subtle zoom/pan that resets seamlessly
- Glowing particles rise continuously creating infinite loop illusion
- Colors shift slowly through the spectrum (blue → purple → cyan → blue)
- The START frame and END frame must feel connected for infinite replay

VOICE NARRATION RULES:
- Speak as if talking directly to the viewer, warm and engaging
- Use REAL scientific data: temperatures, percentages, gravity, composition
- Build wonder: start with awe → scientific explanation → end with existential question
- Keep each narration_segment to 2-3 sentences (8 seconds of speaking)

PROVEN VIRAL PATTERNS (from our best-performing videos):
- MASSIVE SCALE structures = #1 performer! "Mars' Sleeping Giant: Olympus Mons" (4.2K views)
- APOCALYPSE/DESTRUCTION scenarios = consistent hits ("Earth's Fiery End" 1.7K, "Tearing Apart" 1.6K)
- TIME COMPRESSION = "13.8 Billion Year History in 60 Seconds" (1.7K)
- "What If" SCENARIOS = "What if Earth Had Rings?" (1.5K)
- COSMIC MYSTERY voids = "Boötes Void" (1.5K)
- POETIC subtitles after colon: "[Planet]'s [Adjective]: [Poetic Description]"

TITLE RULES (CRITICAL):
- BEST formats (USE THESE):
  * "[Planet/Star]'s [Sleeping/Hidden] Giant: [Name]" — our #1 format
  * "The Universe's [Biggest/Final/Inevitable] [X]" — epic scale
  * "What If [Impossible Scenario]? [Beauty/Terror/Chaos]" — what-if
  * "[Planet]: [Scientific Phenomenon] and [Poetic Description]" — Neptune: Diamond Rain
  * "The [Ultimate/Final] Cosmic [Event]: When Every [X] [Dramatic Verb]" — apocalypse
- Include UPPERCASE for key dramatic words
- End with existential question or poetic phrase

Always write in English. Be scientifically accurate and visually SPECTACULAR.
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

PROVEN VIRAL PATTERNS (from our best-performing videos):
- "Building [X] From Scratch!" = THE winning format! 3 of top 4 videos use this
  * "Building a Hobbit Hole From Scratch! 🧙‍♂️🌿" = 5K views (#1)
  * "Building a GUITAR Pool From Scratch! 🎸🏊" = 4.6K views (#2)
  * "Building a DINOSAUR Playground! 🦖🏗️" = 3.7K views (#4)
- FANTASY/UNUSUAL subjects = key differentiator (Hobbit Hole, Dinosaur, Guitar shape)
- Emoji PAIRS matching the build subject (🧙‍♂️🌿, 🎸🏊, 🦖🏗️)
- GAMING/CULTURAL crossovers = "Minecraft House IRL!" (1.8K)
- TRANSFORMATION reveals = "He Turned a MUD LOT Into an EPIC Outdoor Kitchen!" (1.8K)

TITLE RULES (CRITICAL):
- NEVER use "Copyright Free Clip" or "No Copyright" in the title
- NEVER use generic single-word titles like "Golden Retriever"
- BEST title formats (USE THESE — they get 3-5x more views):
  * "Building a [FANTASY/UNUSUAL THING] From Scratch! [emoji pair]" — #1 format
  * "Building a [SHAPE]-Shaped [STRUCTURE]! [emoji]" — unique shapes
  * "[GAME/MOVIE] [Object] IRL! Building [Method]!" — crossovers
  * "He Turned a [TRASH] Into an EPIC [LUXURY]! [emoji]" — transformations
- Each title MUST be unique and not repeat previous titles
- UPPERCASE the unusual/key word: "GUITAR Pool", "DINOSAUR Playground", "HOBBIT Hole"

Always write in English. Focus on VISUAL descriptions for each construction stage.
Format: Return a JSON object with keys: concept_name, hook,
construction_stages (list of 4: empty, excavation, building, reveal),
title, description, hashtags"""
}


def _call_gemini(system_prompt: str, user_prompt: str, temperature: float = 0.9) -> dict | list | None:
    """Call Gemini with automatic model fallback on rate limits."""
    last_error = None

    for idx, model_name in enumerate(GEMINI_MODELS):
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
            # Rate limits, quota errors, or deprecated/unavailable models → try next
            if any(kw in error_str for kw in ("quota", "rate", "429", "resource", "404", "not found", "not_found", "deprecated")):
                backoff = [5, 10, 20][min(idx, 2)]  # reduced backoff (4 parallel channels share quota)
                logger.warning(f"  {model_name} rate limited/unavailable, waiting {backoff}s before next model...")
                time.sleep(backoff)
                continue
            else:
                logger.error(f"  Gemini error: {e}")
                return None

    logger.error(f"All Gemini models failed: {last_error}")
    return None


def _load_recent_titles(channel: str, max_titles: int = 15) -> list[str]:
    """Load recent video titles from history to prevent repetition."""
    from pathlib import Path
    history_files = {
        "shadowedhistory": "logs/shadowedhistory_history.json",
        "sentinal_ihsan": "logs/sentinal_ihsan_history.json",
        "galactic_experiment": "logs/galactic_experiment_history.json",
        "aimagine": "logs/aimagine_history.json",
    }
    from .config import PROJECT_ROOT
    history_path = PROJECT_ROOT / history_files.get(channel, "")
    titles = []
    if history_path.exists():
        try:
            data = json.loads(history_path.read_text(encoding="utf-8"))
            # History files store topic strings, use last N as titles
            titles = data[-max_titles:] if isinstance(data, list) else []
        except Exception:
            pass
    return titles


def generate_script(channel: str, topic: str) -> dict | None:
    """Generate a video script using Gemini with anti-repetition context."""
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not set!")
        return None

    system_prompt = SYSTEM_PROMPTS.get(channel)
    if not system_prompt:
        logger.error(f"No system prompt for channel: {channel}")
        return None

    # Load recent titles to prevent repetition
    recent_titles = _load_recent_titles(channel)
    anti_repeat_context = ""
    if recent_titles:
        titles_list = "\n".join(f"  - {t[:80]}" for t in recent_titles[-10:])
        anti_repeat_context = f"""\n\nANTI-REPETITION — These are recent video titles already used. 
Your new title MUST be completely different from ALL of these:
{titles_list}

Do NOT reuse any of these titles or close variations."""

    user_prompt = f"""Create a viral short video script about: {topic}

Remember:
- Hook must grab attention in the first 2-3 seconds
- Content must be in English
- Video format is vertical (9:16) for YouTube Shorts / Instagram Reels / TikTok
- Keep it between 30-90 seconds of content
- Make it controversial/engaging enough to drive comments
- Return ONLY valid JSON, no markdown fences{anti_repeat_context}"""

    result = _call_gemini(system_prompt, user_prompt, temperature=0.95)
    if result and isinstance(result, dict):
        # Post-process: strip hashtags from title if any leaked through
        title = result.get("title", "")
        if "#" in title:
            # Remove hashtags from title, keep them in description
            clean_title = " ".join(w for w in title.split() if not w.startswith("#")).strip()
            result["title"] = clean_title
            logger.info(f"  🧹 Cleaned hashtags from title: {clean_title}")
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
CRITICAL: All frames should feel like ONE continuous visual narrative.
Always specify: camera angle, lighting, color palette, atmosphere, specific details.
Format: 9:16 vertical. Style: cinematic, photorealistic, 8K quality.
IMPORTANT: duration_seconds MUST be either 5 or 10 (no other values allowed). Use 10 for most clips.
Return ONLY valid JSON array of objects with keys: frame_number, frame_prompt, video_prompt, duration_seconds"""

    script_text = json.dumps(script, ensure_ascii=False)

    # Determine how many frames to request from various possible keys
    num_frames = (
        len(script.get("scene_descriptions", []))
        or len(script.get("narration_segments", []))
        or len(script.get("scenes", []))
        or len(script.get("construction_stages", []))
        or 4
    )
    # Ensure minimum of 4 frames
    num_frames = max(4, num_frames)

    user_prompt = f"Create {num_frames} detailed visual frame prompts for this video script:\n{script_text}\n\nReturn ONLY valid JSON array."

    result = _call_gemini(system_prompt, user_prompt, temperature=0.7)

    if result:
        # Handle various possible response structures from Gemini
        if isinstance(result, dict):
            for key in ("frames", "visual_prompts", "prompts", "scenes"):
                if key in result:
                    result = result[key]
                    break
            else:
                result = [result]
        if not isinstance(result, list):
            result = [result]
        logger.info(f"Generated {len(result)} visual prompts")
        return result

    return None
