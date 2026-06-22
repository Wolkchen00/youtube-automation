"""
Music Generator — Lyria 3 Background Music

Generates channel-specific background music using Google's Lyria 3 model.
Only used for AIMagine and ShadowedHistory channels.

Model: lyria-3-clip-preview (30-second clips)
SDK: google-genai
"""

import os
from pathlib import Path

from .config import GEMINI_API_KEY, PROJECT_ROOT, logger

# Channel-specific music prompts.
# NOTE: these play as a CONTINUOUS bed under the whole episode (looped + faded),
# so they must be smooth and seamless — no abrupt hits, no hard endings.
MUSIC_PROMPTS = {
    "aimagine": (
        "Cinematic construction timelapse music. "
        "Deep bass drone, percussive industrial hits, rising tension. "
        "Metallic textures, epic orchestral swells building to a climax. "
        "Satisfying reveal moment at the end. "
        "Instrumental only, no vocals. Modern, sleek, architectural. "
        "Similar to construction reveal TV shows."
    ),
    "shadowedhistory": (
        "Epic cinematic historical documentary score. "
        "Deep war drums, dramatic orchestral strings, ancient brass horns. "
        "Mysterious Middle Eastern and Egyptian textures. "
        "Dark, brooding atmosphere building to a powerful crescendo. "
        "Instrumental only, no vocals. "
        "Similar to BBC history documentary music."
    ),
    # ava-voyage (narration channel = galactic_experiment): cosmic awe
    "galactic_experiment": (
        "Ethereal cinematic space ambient. Slow evolving synth pads, deep sub-bass "
        "drone, distant ethereal choir, shimmering bell and crystal textures. "
        "A sense of awe, vastness and infinite cosmos. Continuous flowing soundscape "
        "with NO percussion hits and NO abrupt changes — seamless and immersive. "
        "Instrumental only, no vocals. Similar to an interstellar documentary score."
    ),
    # infinite-trip: hypnotic psychedelic bed
    "infinite-trip": (
        "Continuous psychedelic ambient music. Hypnotic flowing synth arpeggios, "
        "warm analog pads, gentle steady pulse, dreamy reverb, textures that morph "
        "seamlessly into one another. Meditative, immersive, downtempo psybient. "
        "NO abrupt changes, NO hard stops. Instrumental only, no vocals."
    ),
    # the-signal (found-footage alien series): eerie sound-design drone, NOT a score
    "the-signal": (
        "Subtle eerie sub-bass drone for a realistic found-footage night. A low, "
        "almost-subliminal hum with a slow rhythmic pulse — like a faint distant "
        "signal. Cold, tense, minimal sound design. NO melody, NO percussion hits, "
        "NO vocals. Sits quietly under wind and silence to build dread. "
        "Seamless and continuous, never resolving."
    ),
}

# Slug → music-prompt-key aliases (so callers can pass either the narration channel
# OR the series slug and still get the right bed).
MUSIC_PROMPT_ALIASES = {
    "ava-voyage": "galactic_experiment",
    "secrets-anatolia": "shadowedhistory",
    "sentinal_ihsan": "the-signal",   # narration channel adı → the-signal müzik (eerie drone)
}

# Cache directory for generated music
MUSIC_CACHE_DIR = PROJECT_ROOT / "assets" / "music"


def generate_background_music(
    channel: str,
    custom_prompt: str = None,
    output_path: str | Path = None,
) -> Path | None:
    """Generate a 30-second background music clip using Lyria 3.

    Args:
        channel: Channel name (aimagine or shadowedhistory)
        custom_prompt: Optional custom music prompt (overrides default)
        output_path: Optional output path for the audio file

    Returns:
        Path to the generated audio file, or None if failed.
    """
    key = MUSIC_PROMPT_ALIASES.get(channel, channel)
    if key not in MUSIC_PROMPTS and not custom_prompt:
        logger.info(f"Music generation skipped for {channel} (no music config)")
        return None

    prompt = custom_prompt or MUSIC_PROMPTS.get(key, "")
    if not prompt:
        return None

    if not GEMINI_API_KEY:
        logger.warning("No Gemini API key — skipping music generation")
        return None

    # Setup output path
    MUSIC_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if output_path is None:
        output_path = MUSIC_CACHE_DIR / f"{channel}_bg_music.mp3"
    output_path = Path(output_path)

    try:
        from google import genai

        client = genai.Client(api_key=GEMINI_API_KEY)

        logger.info(f"🎵 Generating background music for {channel}...")
        response = client.models.generate_content(
            model="lyria-3-clip-preview",
            contents=prompt,
        )

        # Extract audio bytes from response
        for part in response.parts:
            if part.inline_data and part.inline_data.data:
                output_path.write_bytes(part.inline_data.data)
                size_kb = output_path.stat().st_size / 1024
                logger.info(f"🎵 Music saved: {output_path.name} ({size_kb:.0f} KB)")
                return output_path

        logger.warning("No audio data in Lyria response")
        return None

    except ImportError:
        logger.warning("google-genai SDK not installed. Run: pip install google-genai")
        return None
    except Exception as e:
        logger.warning(f"Music generation failed: {e}")
        return None
