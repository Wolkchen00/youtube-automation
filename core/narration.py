"""
Narration Generator ,  AIMagine Building Stories with Female Voice

Generates engaging narration scripts and converts to audio using
Gemini TTS. Each build gets a different storytelling style for A/B testing.

Model: gemini-2.5-flash-preview-tts (low-latency, natural speech)
Voice: Kore (female, energetic)
"""

import json
import wave
import random
from pathlib import Path

import google.generativeai as genai

from .env import GEMINI_API_KEY, PROJECT_ROOT, logger

NARRATION_CACHE = PROJECT_ROOT / "assets" / "narration"

# Surum-sabit model adi emekliye ayrilinca 404 doner ve anlatim SESSIZCE duser:
# 2026-09-02'de part27 tam boyle anlatimsiz (muzik-only) yayinlandi
# ("404 models/gemini-2.0-flash is no longer available"). Takma ad kullaniyoruz ki
# model kusagi degistiginde hat kendiliginden kirilmasin.
TEXT_MODEL = "gemini-flash-latest"

# Different narration styles ,  A/B testing which resonates best
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
            "Style: Start with 'You won't believe what they built!' ,  build excitement "
            "as the construction progresses ,  climax with the interior reveal. "
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
            "Style: Tell a mini-story ,  'They said it couldn't be done...' "
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
            "Style: Soft, calming, satisfying descriptions ,  'Watch the concrete pour... "
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
            "Style: 'HERE WE GO! The foundation is IN! Walls going UP!' ,  "
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
            "Style: 'Something incredible is taking shape... but what is it?' ,  "
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
        model = genai.GenerativeModel(TEXT_MODEL)
        response = model.generate_content(prompt)
        script = response.text.strip().strip('"')
        logger.info(f"📝 Narration script ({style['name']}): {script[:80]}...")
        return script
    except Exception as e:
        logger.warning(f"Narration script generation failed: {e}")
        return None


def shorten_narration_for_duration(narration_text: str, target_seconds: float,
                                   planned_seconds: float) -> str | None:
    """Rewrite a narration as complete sentences for a shorter partial episode."""
    if not GEMINI_API_KEY or not narration_text.strip():
        return None
    source_words = len(narration_text.split())
    if planned_seconds <= 0 or target_seconds <= 0:
        return None
    ratio = min(1.0, target_seconds / planned_seconds)
    max_words = max(6, int(source_words * ratio * 0.8))
    prompt = (
        "Shorten the English voiceover below so every sentence remains complete and the "
        f"result is at most {max_words} words. Preserve its first-person casual vlog tone, "
        "meaning, and final question when possible. Return only the rewritten voiceover, "
        "with no quotes or commentary.\n\n"
        f"VOICEOVER:\n{narration_text.strip()}"
    )
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(TEXT_MODEL)
        response = model.generate_content(prompt)
        rewritten = str(response.text or "").strip().strip('"')
        if not rewritten or len(rewritten.split()) > max_words:
            logger.warning("⚠️ Kısaltılmış anlatım kelime sınırını doğrulamadı")
            return None
        logger.info(
            f"✂️ Anlatım kısaltıldı: {source_words} -> {len(rewritten.split())} kelime"
        )
        return rewritten
    except Exception as error:
        logger.warning(f"⚠️ Anlatım kısaltılamadı: {error}")
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
            model="gemini-2.5-flash-preview-tts",
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


# ─── Channel-Specific Narration ─────────────────────────────────────────────

CHANNEL_NARRATION_CONFIG = {
    "shadowedhistory": {
        "voice": "Charon",  # Deep male voice ,  documentary
        "instruction": (
            "Speak at a measured documentary pace, with clear pronunciation and a firm, "
            "confident voice. State the claim itself in the first sentence. Pause naturally "
            "just before the twist, then complete the thought without rushing. Keep the "
            "delivery calm and unhurried for a roughly 19-second video."
        ),
    },
    "galactic_experiment": {
        "voice": "Charon",  # Deep male voice ,  cosmic
        "instruction": (
            "Keep the voice warm and full of cosmic awe, but hold a tight pace for a roughly "
            "18-second video. Use one short pause only at the scale-reveal moment. "
            "State the claim itself in the first sentence and never let the delivery drag."
        ),
    },
    "aimagine": {
        "voice": "Kore",  # Female voice ,  construction
        "instruction": None,  # Uses existing NARRATION_STYLES
    },
    "sentinal_ihsan": {
        # İhsan geri bildirimi (2026-07-03, Night Archive P1): fısıltı ürkütücü/irite
        # edici duruyor ,  "sessiz olsun ama fısıldamasın". Sakin ama NORMAL sesle anlat.
        # Algieba = influencer personasıyla aynı ses (marka sesi tek).
        "voice": "Algieba",  # Warm male voice ,  calm late-night storyteller
        "instruction": (
            "Speak in a calm, steady, first-person storyteller voice at NORMAL speaking volume ,  "
            "like a man matter-of-factly recounting something strange that happened on his night "
            "shift. Measured pace, grounded and confident, subtle tension in the pauses only. "
            "Do NOT whisper. No breathy or hushed delivery, no ASMR tone. Never shout either ,  "
            "just quiet, composed, natural speech."
        ),
    },
    "sentinal_vlog": {
        # İhsan kararı (2026-07-24, KONSEPT.md v2.1): steril sessizlik "AI hissi" veriyor,
        # izleyici mesafeleniyor → unnatural-lab GÜNDELİK VLOG voiceover'a geçti. Ses yine
        # Algieba (marka sesi tek) ama register tamamen farklı: anlatıcı değil, telefonuyla
        # çekim yapan adamın doğal konuşması. Fısıltı yasağı (2026-07-03) burada da geçerli.
        "voice": "Algieba",
        "instruction": (
            "Speak like a real guy casually talking over a video he just shot on his phone ,  "
            "first person, relaxed, mildly amused, completely natural and fluent. Conversational "
            "pace with tiny human imperfections: a brief pause mid-thought, a small exhale or "
            "half-chuckle where it fits, throwaway words like 'okay so...' delivered off-the-cuff. "
            "He is talking to a friend, not to an audience. Absolutely NO announcer, documentary, "
            "salesman or ASMR tone; do NOT whisper, do not perform, do not over-enunciate. "
            "Just a normal dude who can't quite believe what his kitchen is doing right now."
        ),
    },
}


def create_narration_for_channel(
    channel: str,
    narration_text: str,
    output_path: str | Path = None,
) -> tuple[Path | None, str]:
    """Generate voiceover narration for any channel.

    Uses channel-specific voice and style for consistent branding.
    SH: Deep male documentary narrator
    GE: Cosmic philosopher narrator
    AIM: Female construction narrator (existing)

    Args:
        channel: Channel name
        narration_text: Full narration script text
        output_path: Output WAV file path

    Returns:
        (audio_path, style_name) tuple
    """
    config = CHANNEL_NARRATION_CONFIG.get(channel, {})
    voice_name = config.get("voice")
    instruction = config.get("instruction")

    if not voice_name:
        logger.info(f"ℹ️ No narration configured for {channel}")
        return None, "none"

    if not narration_text or not narration_text.strip():
        logger.warning("⚠️ Empty narration text ,  skipping")
        return None, "none"

    if not GEMINI_API_KEY:
        return None, "none"

    NARRATION_CACHE.mkdir(parents=True, exist_ok=True)
    if output_path is None:
        output_path = NARRATION_CACHE / f"{channel}_narration.wav"
    output_path = Path(output_path)

    try:
        from google import genai as genai_new
        from google.genai import types

        client = genai_new.Client(api_key=GEMINI_API_KEY)

        voice_config = types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name=voice_name
            )
        )
        speech_config = types.SpeechConfig(voice_config=voice_config)

        # Add style instruction to narration
        full_prompt = f"[{instruction}] {narration_text}" if instruction else narration_text

        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["audio"],
                speech_config=speech_config,
            ),
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                audio_bytes = part.inline_data.data
                with wave.open(str(output_path), "wb") as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(24000)
                    wav_file.writeframes(audio_bytes)

                size_kb = output_path.stat().st_size / 1024
                logger.info(f"🎙️ {channel} narration saved: {output_path.name} ({size_kb:.0f} KB)")
                return output_path, f"{channel}_{voice_name}"

        logger.warning("No audio data in TTS response")
        return None, "none"

    except ImportError:
        logger.warning("google-genai SDK not installed for TTS")
        return None, "none"
    except Exception as e:
        logger.warning(f"⚠️ {channel} narration failed: {e}")
        return None, "none"
