"""
Music Generator — Lyria 3 Background Music

Generates channel-specific background music using Google's Lyria 3 model.
Only used for AIMagine and ShadowedHistory channels.

Model: lyria-3-clip-preview (30-second clips)
SDK: google-genai
"""

import os
from pathlib import Path

from .env import GEMINI_API_KEY, PROJECT_ROOT, logger

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
    # the-drift (cinematic dreamcore): sıcak, sinematik, rüya gibi ambient skor
    "the-drift": (
        "Cinematic dreamlike ambient score. Slow warm string swells, soft felt piano "
        "notes with long reverb tails, airy ethereal choir pad, deep gentle sub bass. "
        "Emotional, nostalgic, awe-inspiring — like drifting through a half-remembered "
        "dream. Continuous and seamless, NO percussion hits, NO abrupt changes. "
        "Instrumental only, no vocals. Similar to the quiet epic moments of an A24 film score."
    ),
    # planetfall (gezegen iniş yolculukları): epik-sinematik keşif skoru
    "planetfall": (
        "Epic cinematic space-exploration score. Warm evolving orchestral strings "
        "and distant horns over a deep sub-bass drone, slow majestic build, "
        "shimmering celestial bell and choir textures — a feeling of awe and "
        "discovery, like descending onto an alien world for the first time. "
        "Continuous seamless flow, NO hard percussion hits, NO abrupt changes, "
        "no hard ending. Instrumental only, no vocals. Similar to an "
        "Interstellar-style ambient-orchestral score."
    ),
    # night-shift (CCTV anthology): realistic empty-building room tone, NOT music
    "night-shift": (
        "Ultra-quiet realistic room tone of an empty building at night, as heard "
        "on a security-camera recording: steady fluorescent light hum, faint "
        "electrical buzz, distant HVAC air rumble. Constant and seamless, almost "
        "subliminal. NO melody, NO rhythm, NO music, NO vocals — just a real, "
        "slightly uneasy quiet building."
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


# ─── Yerel sentez ambient bed (Lyria erişimi yoksa kesin çalışan yedek) ──────────
# Lyria 3 ücretli/allowlist model → ücretsiz Gemini anahtarında limit=0 (429). O yüzden
# müzik HİÇ üretilemiyordu ve videolarda sürekli ses bedi yoktu (kesintilerde boşluk).
# Bu yedek, ffmpeg ile kanala özgü, her video benzersiz, KESİNTİSİZ bir ambient bed
# üretir → API/kota bağımlılığı yok, asla başarısız olmaz.
AMBIENT_PROFILES = {
    # drone/fifth = düşük pad frekansları; lp = lowpass (yumuşaklık); trem = yavaş volüm LFO
    # NOT: ffmpeg 'tremolo' f >= 0.1 Hz şart → tüm trem değerleri 0.12+ ve ayrıca clamp'li.
    "galactic_experiment": {"drone": 65.0, "fifth": 97.5, "lp": 650, "trem": 0.13},   # kozmik/ethereal
    "infinite-trip":       {"drone": 73.4, "fifth": 110.0, "lp": 950, "trem": 0.18},  # hipnotik/psychedelic
    "shadowedhistory":     {"drone": 55.0, "fifth": 82.4, "lp": 520, "trem": 0.12},   # ağırbaşlı/brooding
    "the-signal":          {"drone": 46.3, "fifth": 69.3, "lp": 430, "trem": 0.14},   # tekinsiz/sub drone
    # 60 Hz = şebeke uğultusu + 120 Hz harmoniği → floresan/trafo vızıltısı; dar lowpass
    # + pembe gürültü = uzak havalandırma. Müzik değil, 'boş bina gece sesi'.
    "night-shift":         {"drone": 60.0, "fifth": 120.0, "lp": 330, "trem": 0.11},
    "the-drift":           {"drone": 69.3, "fifth": 103.8, "lp": 820, "trem": 0.14},  # sıcak/rüyamsı sinematik
    "planetfall":          {"drone": 61.7, "fifth": 92.5, "lp": 720, "trem": 0.13},   # epik/kozmik keşif
}
DEFAULT_AMBIENT = {"drone": 60.0, "fifth": 90.0, "lp": 700, "trem": 0.13}


def _synth_ambient_bed(channel: str, output_path: Path, duration: int = 30) -> Path | None:
    """ffmpeg ile kanala özgü, sürekli, yumuşak ambient müzik bedi üret (yedek).
    Her video için benzersiz (output yoluna göre seed → pad frekansı/LFO hafif değişir).
    mix_background_music bunu zaten video boyuna LOOP'lar, o yüzden 30s yeterli.
    """
    import shutil, subprocess, random
    if not shutil.which("ffmpeg"):
        logger.warning("⚠️ ffmpeg yok — ambient bed üretilemedi")
        return None
    p = AMBIENT_PROFILES.get(channel, DEFAULT_AMBIENT)
    rnd = random.Random(str(output_path))            # video başına benzersiz ama deterministik
    drone = p["drone"] * (1 + rnd.uniform(-0.03, 0.03))
    fifth = p["fifth"] * (1 + rnd.uniform(-0.03, 0.03))
    detune = fifth * 1.004                            # hafif akort kayması → canlı 'beating'
    trem = max(0.1, p["trem"] + rnd.uniform(-0.02, 0.02))   # ffmpeg tremolo min f = 0.1 Hz
    lp = p["lp"]
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    flt = (
        f"[0:a]volume=0.5[d];[1:a]volume=0.32[f];[2:a]volume=0.30[g];"
        f"[3:a]lowpass=f={lp},highpass=f=38,volume=0.55[n];"
        f"[d][f][g]amix=inputs=3:normalize=0,tremolo=f={trem:.3f}:d=0.5[pad];"
        f"[pad][n]amix=inputs=2:normalize=0,lowpass=f={lp+250},"
        f"afade=t=in:st=0:d=2.5,volume=1.7[a]"
    )
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=frequency={drone:.2f}:duration={duration}",
        "-f", "lavfi", "-i", f"sine=frequency={fifth:.2f}:duration={duration}",
        "-f", "lavfi", "-i", f"sine=frequency={detune:.2f}:duration={duration}",
        "-f", "lavfi", "-i", f"anoisesrc=color=pink:duration={duration}:amplitude=0.28",
        "-filter_complex", flt, "-map", "[a]",
        "-c:a", "libmp3lame", "-q:a", "5", str(output_path),
    ]
    try:
        subprocess.run(cmd, capture_output=True, check=True, timeout=120)
        if output_path.exists() and output_path.stat().st_size > 0:
            logger.info(f"🎛️ Ambient müzik bedi sentezlendi ({channel}, drone={drone:.0f}Hz): {output_path.name}")
            return output_path
        return None
    except Exception as e:
        logger.warning(f"⚠️ Ambient bed sentezi başarısız: {e}")
        return None


def _try_lyria_music(channel: str, custom_prompt: str, output_path: Path) -> Path | None:
    """Lyria 3 ile GERÇEK müzik üretmeyi dene (yalnızca ücretli/erişimli anahtarda çalışır)."""
    key = MUSIC_PROMPT_ALIASES.get(channel, channel)
    prompt = custom_prompt or MUSIC_PROMPTS.get(key, "")
    if not prompt or not GEMINI_API_KEY:
        return None
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        logger.info(f"🎵 Lyria müzik deneniyor ({channel})...")
        response = client.models.generate_content(model="lyria-3-clip-preview", contents=prompt)
        for part in response.parts:
            if part.inline_data and part.inline_data.data:
                output_path.write_bytes(part.inline_data.data)
                logger.info(f"🎵 Lyria müzik kaydedildi: {output_path.name}")
                return output_path
        return None
    except Exception as e:
        # Lyria ücretsiz tier'da limit=0 (429) → sessizce yedeğe düş
        logger.info(f"ℹ️ Lyria kullanılamadı ({str(e)[:80]}...) → ambient bed'e düşülüyor")
        return None


def generate_background_music(
    channel: str,
    custom_prompt: str = None,
    output_path: str | Path = None,
) -> Path | None:
    """Sürekli arka plan müziği üret. Önce Lyria (gerçek müzik), olmazsa yerel ambient bed.

    HER VİDEO için benzersiz dosya verilirse (output_path) benzersiz müzik döner.
    Dönüş: ses dosyası yolu veya None.
    """
    key = MUSIC_PROMPT_ALIASES.get(channel, channel)
    if key not in MUSIC_PROMPTS and not custom_prompt:
        logger.info(f"Music generation skipped for {channel} (no music config)")
        return None

    MUSIC_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if output_path is None:
        output_path = MUSIC_CACHE_DIR / f"{channel}_bg_music.mp3"
    output_path = Path(output_path)

    # 1) Gerçek müzik (Lyria) — varsa en iyisi
    real = _try_lyria_music(channel, custom_prompt, output_path)
    if real:
        return real
    # 2) Yedek: yerel ffmpeg ambient bed (kota yok → asla boşluk kalmaz)
    return _synth_ambient_bed(key, output_path)
