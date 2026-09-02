"""
Utility Functions — Download, sanitize, formatting helpers.
"""

import os
import re
import subprocess
import time
from pathlib import Path

import requests

from .env import logger


def _valid_video_file(path: Path) -> bool:
    """Return whether ffprobe can read a real video stream from ``path``."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(path)],
            capture_output=True, text=True, timeout=30,
        )
        return result.returncode == 0 and "video" in result.stdout.split()
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False


def download_file(url: str, save_path: str | Path, *, hardened: bool = False,
                  retries: int = 3, backoff: float = 0.25) -> Path | None:
    """Download a file.

    Legacy callers retain their direct single-attempt write. Paid shot downloads
    opt into three attempts, same-directory temporary output, ffprobe validation,
    and an atomic rename that never exposes partial media at the final path.
    """
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    # Preserve the historical code path byte-for-byte for callers that have not
    # opted into hardened media downloads.
    if not hardened:
        try:
            resp = requests.get(url, timeout=120, stream=True, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            })
            resp.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            size_mb = save_path.stat().st_size / (1024 * 1024)
            logger.info(f"📥 Downloaded: {save_path.name} ({size_mb:.1f} MB)")
            return save_path
        except Exception as e:
            logger.error(f"❌ Download error: {e}")
            return None

    attempts = max(1, int(retries))
    temp_path = save_path.with_name(
        f".{save_path.name}.part-{os.getpid()}-{time.time_ns()}"
    )
    last_error = None
    try:
        for attempt in range(1, attempts + 1):
            try:
                if temp_path.exists():
                    temp_path.unlink()
                resp = requests.get(url, timeout=120, stream=True, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                })
                resp.raise_for_status()
                with open(temp_path, "wb") as handle:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            handle.write(chunk)
                if not temp_path.exists() or temp_path.stat().st_size == 0:
                    raise ValueError("download is empty")
                if hardened and not _valid_video_file(temp_path):
                    raise ValueError("ffprobe found no valid video stream")
                if hardened:
                    os.replace(temp_path, save_path)
                size_mb = save_path.stat().st_size / (1024 * 1024)
                logger.info(f"📥 Downloaded: {save_path.name} ({size_mb:.1f} MB)")
                return save_path
            except Exception as error:
                last_error = error
                if hardened and temp_path.exists():
                    temp_path.unlink()
                if attempt < attempts:
                    delay = max(0.0, float(backoff)) * (2 ** (attempt - 1))
                    logger.warning(
                        f"⚠️ Download attempt {attempt}/{attempts} failed: {error}; "
                        f"retrying in {delay:.2f}s"
                    )
                    time.sleep(delay)
        logger.error(f"❌ Download error after {attempts} attempt(s): {last_error}")
        return None
    finally:
        if hardened and temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass


def sanitize_filename(name: str) -> str:
    """Make a string safe for filenames."""
    name = name.lower().strip()
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[\s]+', '_', name)
    return name[:50]


def format_duration(seconds: float) -> str:
    """Convert seconds to mm:ss."""
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"

def normalize_title(t: str) -> str:
    """Baslik karsilastirmasi icin normalize et (kucuk harf, noktalama ve emoji at).

    Yayin kapisi ile replenish AYNI fonksiyonu kullanir. Ayrisirlarsa bir baslik
    replenish'ten gecip kapida takilir ve gunluk video sessizce eksik platformla
    cikar; bu yuzden tek kaynak burasidir.
    """
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()
