"""
YouTube Multi-Channel Automation — Central Configuration

Loads environment variables, sets up paths, logging, and per-channel settings.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# ─── Project Root ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# ─── API Keys ──────────────────────────────────────────────────────────────────
KIE_AI_API_KEY = os.getenv("KIE_AI_API_KEY", "")
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
UPLOAD_POST_API_KEY = os.getenv("UPLOAD_POST_API_KEY", "")
SENTINAL_FACE_REF = os.getenv("SENTINAL_FACE_REF", "")

# ─── Upload-Post Profile Names ────────────────────────────────────────────────
UPLOAD_USERS = {
    "aimagine": os.getenv("UPLOAD_USER_AIMAGINE", "Youtube"),
    "shadowedhistory": os.getenv("UPLOAD_USER_SHADOWEDHISTORY", "shad0wedhistory"),
    "galactic_experiment": os.getenv("UPLOAD_USER_GALACTIC", "galacticexperimet"),
    "sentinal_ihsan": os.getenv("UPLOAD_USER_SENTINAL", "sentinalihsandaily"),
}

# ─── Kie AI API Endpoints ─────────────────────────────────────────────────────
KIE_AI_BASE_URL = "https://api.kie.ai/api/v1"
KIE_AI_CREATE_TASK = f"{KIE_AI_BASE_URL}/jobs/createTask"
KIE_AI_RECORD_INFO = f"{KIE_AI_BASE_URL}/jobs/recordInfo"
KIE_AI_CREDIT = f"{KIE_AI_BASE_URL}/chat/credit"
IMGBB_UPLOAD_URL = "https://api.imgbb.com/1/upload"

# ─── Project Directories ──────────────────────────────────────────────────────
OUTPUT_DIR = PROJECT_ROOT / "output"
LOGS_DIR = PROJECT_ROOT / "logs"

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

# ─── Default Generation Settings ──────────────────────────────────────────────
DEFAULT_ASPECT_RATIO = "9:16"       # Vertical / Shorts format
DEFAULT_RESOLUTION = "1K"
DEFAULT_OUTPUT_FORMAT = "png"
DEFAULT_VIDEO_DURATION = "10"       # seconds per clip (Kling 2.6 accepts "5" or "10" only)
DEFAULT_VIDEO_MODEL = "kling-2.6/image-to-video"  # Kling 2.6 Image-to-Video (pipeline uses start frames)
DEFAULT_VIDEO_MODEL_T2V = "kling-2.6/text-to-video"  # Kling 2.6 Text-to-Video (fallback when no image)
DEFAULT_VIDEO_MODE = "std"               # std = Standard quality, good balance
DEFAULT_IMAGE_MODEL = "nano-banana-2"
CINEMATIC_VIDEO_MODEL = "veo3_fast"      # Kie AI model names: veo3 (quality) or veo3_fast (fast)
CINEMATIC_VIDEO_MODEL_LITE = "veo3_lite" # 60 credits per 8s clip — includes voice narration

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

# Polling settings
POLL_INTERVAL_IMAGE = 10
POLL_INTERVAL_VIDEO = 15
POLL_MAX_ATTEMPTS_IMAGE = 20   # 20 × 10s = ~3.3min timeout per image (was 30 = 5min)
POLL_MAX_ATTEMPTS_VIDEO = 40   # 40 × 15s = ~10min timeout per clip (VEO3 rarely succeeds after 10min)
MAX_RETRY = 2                  # 2 retries max — fail faster, fallback sooner
PIPELINE_TIMEOUT_MINUTES = 80  # Hard timeout per channel pipeline (GitHub Actions limit = 120min)

# FFmpeg settings
FFMPEG_CRF = "18"
FFMPEG_PRESET = "slow"
FFMPEG_FPS = "30"
FFMPEG_AUDIO_BITRATE = "128k"
CROSSFADE_DURATION = 0.5

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

# ─── Logging ───────────────────────────────────────────────────────────────────
def setup_logging(name: str = "youtube", level: int = logging.INFO) -> logging.Logger:
    """Create a project-wide logger."""
    _logger = logging.getLogger(name)
    if _logger.handlers:
        return _logger
    _logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s │ %(levelname)-8s │ %(name)-25s │ %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    _logger.addHandler(console)

    file_handler = logging.FileHandler(LOGS_DIR / f"{name}.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    _logger.addHandler(file_handler)

    return _logger


logger = setup_logging()


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
