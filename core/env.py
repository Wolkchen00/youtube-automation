"""
core.env — yan-etkisiz "yaprak" konfigürasyon modülü.

core/config.py'nin kanal-BAĞIMSIZ kısmı: .env yükleme, API anahtarları,
endpoint sabitleri, üretim/poll/ffmpeg varsayılanları ve logger.

Neden ayrı: core kütüphane modülleri (kie_api, ffmpeg_tools, imgbb, utils,
narration, music_generator) ve series/omni_api dış projelerden (director-studio)
kütüphane olarak import edilir. core.config import anında kanal klasörleri
yaratır; bu modül yalnız logger'ı kurar (logs/ + youtube.log — eski davranışla
aynı), kanal klasörü YARATMAZ. core.config bu modülü yıldızla re-export eder —
mevcut tüm `from core.config import X` kullanımları aynen çalışır.

Kural: bu dosya core içinden HİÇBİR modülü import etmez (gerçek yaprak).
load_dotenv override etmez → dış proje kendi .env'ini ÖNCE yüklerse o kazanır.
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

# ─── Kie AI API Endpoints ─────────────────────────────────────────────────────
KIE_AI_BASE_URL = "https://api.kie.ai/api/v1"
KIE_AI_CREATE_TASK = f"{KIE_AI_BASE_URL}/jobs/createTask"
KIE_AI_RECORD_INFO = f"{KIE_AI_BASE_URL}/jobs/recordInfo"
KIE_AI_CREDIT = f"{KIE_AI_BASE_URL}/chat/credit"
KIE_AI_OMNI_AUDIO = f"{KIE_AI_BASE_URL}/omni/audio/create"          # Gemini Omni voice registration
KIE_AI_OMNI_CHARACTER = f"{KIE_AI_BASE_URL}/omni/character/create"  # Gemini Omni character registration
KIE_AI_FILE_UPLOAD = "https://kieai.redpandaai.co/api/file-stream-upload"  # geçici dosya deposu (3 gün) — URL isteyen modellere yerel dosya beslemek için (api.kie.ai'de DEĞİL — docs curl örneğindeki host)
IMGBB_UPLOAD_URL = "https://api.imgbb.com/1/upload"

# ─── Logs ──────────────────────────────────────────────────────────────────────
LOGS_DIR = PROJECT_ROOT / "logs"   # mkdir setup_logging içinde — import yan etkisi yok

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

# ─── Gemini Omni (mini-series) Settings ───────────────────────────────────────
OMNI_MODEL = "gemini-omni-video"
OMNI_DEFAULT_RESOLUTION = "1080p"             # 720p and 1080p cost the same on Kie → use 1080p
OMNI_DEFAULT_ASPECT = "9:16"                  # vertical, matches existing channels + uploader
OMNI_VALID_DURATIONS = ("4", "6", "8", "10")  # seconds per Omni shot (max 10)
OMNI_MAX_REF_UNITS = 7                        # (images×1)+(videos×2)+(character_ids×1) ≤ 7 / request

# Polling settings
POLL_INTERVAL_IMAGE = 10
POLL_INTERVAL_VIDEO = 15
POLL_MAX_ATTEMPTS_IMAGE = 20   # 20 × 10s = ~3.3min timeout per image (was 30 = 5min)
POLL_MAX_ATTEMPTS_VIDEO = 40   # 40 × 15s = ~10min timeout per clip (VEO3 rarely succeeds after 10min)
MAX_RETRY = 2                  # 2 retries max — fail faster, fallback sooner

# FFmpeg settings
FFMPEG_CRF = "18"
FFMPEG_PRESET = "slow"
FFMPEG_FPS = "30"
FFMPEG_AUDIO_BITRATE = "128k"
CROSSFADE_DURATION = 0.5


# ─── Logging ───────────────────────────────────────────────────────────────────
def setup_logging(name: str = "youtube", level: int = logging.INFO) -> logging.Logger:
    """Create a project-wide logger."""
    _logger = logging.getLogger(name)
    if _logger.handlers:
        return _logger
    _logger.setLevel(level)

    # Windows konsolu cp1252 → emoji/Türkçe/box karakterler için UTF-8'e geç (no-op if already utf-8)
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

    formatter = logging.Formatter(
        "%(asctime)s │ %(levelname)-8s │ %(name)-25s │ %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    _logger.addHandler(console)

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(LOGS_DIR / f"{name}.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    _logger.addHandler(file_handler)

    return _logger


logger = setup_logging()


__all__ = [
    "PROJECT_ROOT", "LOGS_DIR",
    "KIE_AI_API_KEY", "IMGBB_API_KEY", "GEMINI_API_KEY", "UPLOAD_POST_API_KEY",
    "KIE_AI_BASE_URL", "KIE_AI_CREATE_TASK", "KIE_AI_RECORD_INFO", "KIE_AI_CREDIT",
    "KIE_AI_OMNI_AUDIO", "KIE_AI_OMNI_CHARACTER", "KIE_AI_FILE_UPLOAD", "IMGBB_UPLOAD_URL",
    "DEFAULT_ASPECT_RATIO", "DEFAULT_RESOLUTION", "DEFAULT_OUTPUT_FORMAT",
    "DEFAULT_VIDEO_DURATION", "DEFAULT_VIDEO_MODEL", "DEFAULT_VIDEO_MODEL_T2V",
    "DEFAULT_VIDEO_MODE", "DEFAULT_IMAGE_MODEL",
    "CINEMATIC_VIDEO_MODEL", "CINEMATIC_VIDEO_MODEL_LITE",
    "OMNI_MODEL", "OMNI_DEFAULT_RESOLUTION", "OMNI_DEFAULT_ASPECT",
    "OMNI_VALID_DURATIONS", "OMNI_MAX_REF_UNITS",
    "POLL_INTERVAL_IMAGE", "POLL_INTERVAL_VIDEO",
    "POLL_MAX_ATTEMPTS_IMAGE", "POLL_MAX_ATTEMPTS_VIDEO", "MAX_RETRY",
    "FFMPEG_CRF", "FFMPEG_PRESET", "FFMPEG_FPS", "FFMPEG_AUDIO_BITRATE",
    "CROSSFADE_DURATION",
    "setup_logging", "logger",
]
