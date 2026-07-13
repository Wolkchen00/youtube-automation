"""
YouTube Multi-Channel Automation — Central Configuration

Kanal-BAĞIMSIZ kısım (env yükleme, anahtarlar, endpoint'ler, üretim/poll/ffmpeg
varsayılanları, logger) core/env.py "yaprak" modülüne taşındı ve buradan aynı
adlarla re-export edilir — mevcut `from core.config import X` kullanımları
değişmeden çalışır. Bu dosyada kanal-SPESİFİK ayarlar ve klasör kurulumu kalır.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

from .env import *  # noqa: F401,F403 — yaprak sembollerinin tamamı aynı adlarla
from .env import logger, setup_logging, PROJECT_ROOT, LOGS_DIR  # açık garanti

# ─── API Keys (kanal-spesifik) ────────────────────────────────────────────────
SENTINAL_FACE_REF = os.getenv("SENTINAL_FACE_REF", "")

# ─── Upload-Post Profile Names ────────────────────────────────────────────────
UPLOAD_USERS = {
    "aimagine": os.getenv("UPLOAD_USER_AIMAGINE", "Youtube"),
    "shadowedhistory": os.getenv("UPLOAD_USER_SHADOWEDHISTORY", "shad0wedhistory"),
    "galactic_experiment": os.getenv("UPLOAD_USER_GALACTIC", "galacticexperiment"),
    "sentinal_ihsan": os.getenv("UPLOAD_USER_SENTINAL", "sentinalihsandaily"),
}

# ─── Project Directories ──────────────────────────────────────────────────────
OUTPUT_DIR = PROJECT_ROOT / "output"
SERIES_DIR = OUTPUT_DIR / "series"   # Gemini Omni mini-series workspace (bible/refs/shots/episodes)

# Per-channel output directories
CHANNEL_NAMES = ["shadowedhistory", "sentinal_ihsan", "galactic_experiment", "aimagine"]

CHANNEL_DIRS = {}
for ch in CHANNEL_NAMES:
    ch_out = OUTPUT_DIR / ch
    CHANNEL_DIRS[ch] = {
        "frames": ch_out / "frames",
        "clips": ch_out / "clips",
        "final": ch_out / "final",
    }
    for d in CHANNEL_DIRS[ch].values():
        d.mkdir(parents=True, exist_ok=True)

LOGS_DIR.mkdir(parents=True, exist_ok=True)
SERIES_DIR.mkdir(parents=True, exist_ok=True)

# Per-channel video model strategy:
# - Visual channels (AIMagine, Sentinal): Kling 2.6 I2V (40 credits) — high quality visuals
# - Narration channels (GE, SH): VEO3 Lite (60 credits) — built-in AI voice narration
CHANNEL_VEO_MODEL = {
    "sentinal_ihsan": None,                              # Kling primary — visual quality matters most
    "aimagine": None,                                    # Kling primary — construction detail matters
    "galactic_experiment": None,                          # Kling primary + separate TTS narration
    "shadowedhistory": None,                              # Kling primary + separate TTS narration
}

# Duration constraints per channel (seconds)
CHANNEL_DURATION = {
    "shadowedhistory": {"min": 30, "max": 90},
    "sentinal_ihsan": {"min": 15, "max": 90},
    "galactic_experiment": {"min": 30, "max": 90},
    "aimagine": {"min": 15, "max": 30},
}

PIPELINE_TIMEOUT_MINUTES = 80  # Hard timeout per channel pipeline (GitHub Actions limit = 120min)

# ─── Platforms per channel ─────────────────────────────────────────────────────
CHANNEL_PLATFORMS = {
    "shadowedhistory": ["youtube", "instagram", "tiktok"],
    "sentinal_ihsan": ["youtube", "instagram", "tiktok"],
    "galactic_experiment": ["youtube", "instagram", "tiktok"],
    "aimagine": ["youtube", "instagram", "tiktok"],
}

# ─── Growth Tactics Config ─────────────────────────────────────────────────────
# Seamless loop: DISABLED for all channels (removed per user request)
CHANNEL_LOOP_ENABLED = {
    "galactic_experiment": False,
    "shadowedhistory": False,
    "sentinal_ihsan": False,
    "aimagine": False,
}

# Dual-upload scheduling (2 videos/day per channel)
VIDEO_SLOTS = {
    "morning": {
        "galactic_experiment": "06:30",   # PST (UTC 13:30)
        "shadowedhistory":     "06:35",
        "sentinal_ihsan":      "06:40",
        "aimagine":            "06:45",
    },
    "evening": {
        "galactic_experiment": "14:30",   # PST (UTC 21:30)
        "shadowedhistory":     "14:35",
        "sentinal_ihsan":      "14:40",
        "aimagine":            "14:45",
    },
}

# Auto-cleanup: minimum views after 48h to keep video alive
MIN_VIEWS_THRESHOLD = {
    "galactic_experiment": 50,
    "shadowedhistory": 30,
    "sentinal_ihsan": 30,
    "aimagine": 30,
}


def validate_api_keys() -> dict:
    """Check which API keys are present."""
    keys = {
        "KIE_AI_API_KEY": bool(KIE_AI_API_KEY),
        "IMGBB_API_KEY": bool(IMGBB_API_KEY),
        "GEMINI_API_KEY": bool(GEMINI_API_KEY),
        "UPLOAD_POST_API_KEY": bool(UPLOAD_POST_API_KEY),
    }
    missing = [k for k, v in keys.items() if not v]
    if missing:
        logger.warning(f"⚠️ Missing API keys: {', '.join(missing)}")
    else:
        logger.info("✅ All API keys present.")
    return keys


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("YouTube Multi-Channel Automation — Config Check")
    logger.info("=" * 60)
    logger.info(f"Project root: {PROJECT_ROOT}")
    logger.info(f"Python: {sys.version}")
    validate_api_keys()
    for ch, dirs in CHANNEL_DIRS.items():
        logger.info(f"  {ch}: {dirs['final']}")
