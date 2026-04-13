"""
Narration Generator — AIMagine Building Stories with Female Voice

Generates engaging narration scripts and converts to audio using
Gemini TTS. Each build gets a different storytelling style for A/B testing.

Model: gemini-2.5-flash-tts (low-latency, natural speech)
Voice: Kore (female, energetic)
"""

import json
import wave
import random
from pathlib import Path

import google.generativeai as genai

from .config import GEMINI_API_KEY, PROJECT_ROOT, logger

NARRATION_CACHE = PROJECT_ROOT / "assets" / "narration"

# Different narration styles — A/B testing which resonates best
NARRATION_STYLES = [
    {
        "name": "excited_reveal",
        "instruction": "Speak with high energy and excitement, like you're revealing a secret. "
                       "Build anticipation, pause for dramatic effect before the reveal. "
                       "Sound genuinely amazed at each construction stage.",
        "template": (
            "Write a 20-second energetic narration for a construction timelapse video. "
            "The building is: {concept_name}. "
            "Hook: {hook}. "
            "Style: Start with 'You won't believe what they built!' — build excitement "
            "as the construction progresses — climax with the interior reveal. "
            "Keep it punchy, use short sentences, lots of energy. "
            "MUST be under 60 words total. English only."
        ),
    },
    {
        "name": "storyteller",
        "instruction": "Speak like a captivating documentary narrator. Warm but dramatic. "
                       "Each sentence should pull the viewer deeper into the story. "
                       "Use pauses between key moments for impact.",
        "template": (
            "Write a 20-second story narration for a construction timelapse video. "
            "The building is: {concept_name}. "
            "Hook: {hook}. "
            "Style: Tell a mini-story — 'They said it couldn't be done...' "
            "Build drama around the construction challenge, end with the beautiful reveal. "
            "Emotional, inspiring, cinematic feel. "
            "MUST be under 60 words total. English only."
        ),
    },
    {
        "name": "asmr_whisper",
        "instruction": "Speak in a soft, satisfying whisper-like tone. Slow and deliberate. "
                       "Almost ASMR quality. Make each word feel satisfying. "
                       "Pause between phrases to let the visuals breathe.",
        "template": (
            "Write a 20-second soft, satisfying narration for a construction timelapse. "
            "The building is: {concept_name}. "
            "Hook: {hook}. "
            "Style: Soft, calming, satisfying descriptions — 'Watch the concrete pour... "
            "smooth... perfect...' Focus on textures, materials, the satisfaction of building. "
            "MUST be under 60 words total. English only."
        ),
    },
    {
        "name": "hype_countdown",
        "instruction": "Speak like an energetic sports commentator building towards a big moment. "
                       "Fast-paced, hyped up, counting down to the reveal. "
                       "Maximum energy and enthusiasm.",
        "template": (
            "Write a 20-second hyped-up narration for a construction timelapse video. "
            "The building is: {concept_name}. "
            "Hook: {hook}. "
            "Style: 'HERE WE GO! The foundation is IN! Walls going UP!' — "
            "commentate like a sports play-by-play building to the big reveal. "
            "Fast, energetic, breathless excitement. "
            "MUST be under 60 words total. English only."
        ),
    },
    {
        "name": "mystery_reveal",
        "instruction": "Speak with mystery and intrigue, like uncovering something hidden. "
                       "Start quiet and curious, build to an excited revelation. "
                       "Create suspense with your delivery.",
        "template": (
            "Write a 20-second mysterious narration for a construction timelapse video. "
            "The building is: {concept_name}. "
            "Hook: {hook}. "
            "Style: 'Something incredible is taking shape... but what is it?' — "
            "build mystery about what's being built, tease the reveal, "
            "then blow minds with the final result. "
            "MUST be under 60 words total. English only."
        ),
    },
]


def generate_narration_script(concept_name: str, hook: str, style: dict = None) -> str | None:
    """Use Gemini to write a narration script for a building concept.

    Args:
        concept_name: Name of the building concept
        hook: The concept hook/description
        style: Optional specific style dict (random if None)

    Returns:
        Narration text string, or None if failed.
    """
    if not GEMINI_API_KEY:
        return None

    if style is None:
        style = random.choice(NARRATION_STYLES)

    prompt = style["template"].format(concept_name=concept_name, hook=hook)

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        script = response.text.strip().strip('"')
        logger.info(f"📝 Narration script ({style['name']}): {script[:80]}...")
        return script
    except Exception as e:
        logger.warning(f"Narration script generation failed: {e}")
        return None


def generate_voiceover(
    text: str,
    output_path: str | Path = None,
    style_instruction: str = None,
) -> Path | None:
    """Convert text to speech using Gemini TTS with female voice.

    Args:
        text: The narration text to speak
        output_path: Output WAV file path
        style_instruction: Speaking style instruction

    Returns:
        Path to WAV file, or None if failed.
    """
    if not GEMINI_API_KEY:
        return None

    NARRATION_CACHE.mkdir(parents=True, exist_ok=True)
    if output_path is None:
        output_path = NARRATION_CACHE / "narration.wav"
    output_path = Path(output_path)

    try:
        from google import genai as genai_new
        from google.genai import types

        client = genai_new.Client(api_key=GEMINI_API_KEY)

        # Use Kore voice (female, clear, energetic)
        voice_config = types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Kore"
            )
        )

        speech_config = types.SpeechConfig(voice_config=voice_config)

        # Add style instruction to the text if provided
        if style_instruction:
            full_prompt = f"[{style_instruction}] {text}"
        else:
            full_prompt = text

        response = client.models.generate_content(
            model="gemini-2.5-flash-tts",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["audio"],
                speech_config=speech_config,
            ),
        )

        # Extract audio
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                audio_bytes = part.inline_data.data
                with wave.open(str(output_path), "wb") as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(24000)
                    wav_file.writeframes(audio_bytes)

                size_kb = output_path.stat().st_size / 1024
                logger.info(f"🎙️ Voiceover saved: {output_path.name} ({size_kb:.0f} KB)")
                return output_path

        logger.warning("No audio data in TTS response")
        return None

    except ImportError:
        logger.warning("google-genai SDK not installed for TTS")
        return None
    except Exception as e:
        logger.warning(f"TTS generation failed: {e}")
        return None


def create_narration_for_concept(
    concept_name: str,
    hook: str,
    output_path: str | Path = None,
) -> tuple[Path | None, str]:
    """Complete narration pipeline: script → voiceover.

    Returns:
        (audio_path, style_name) tuple
    """
    style = random.choice(NARRATION_STYLES)
    logger.info(f"🎭 Narration style: {style['name']}")

    # Step 1: Generate script
    script = generate_narration_script(concept_name, hook, style)
    if not script:
        return None, style["name"]

    # Step 2: Generate voiceover
    NARRATION_CACHE.mkdir(parents=True, exist_ok=True)
    if output_path is None:
        safe_name = concept_name.lower().replace(" ", "_")[:30]
        output_path = NARRATION_CACHE / f"{safe_name}_narration.wav"

    audio = generate_voiceover(
        text=script,
        output_path=output_path,
        style_instruction=style["instruction"],
    )

    return audio, style["name"]
