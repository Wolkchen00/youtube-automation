"""
Utility Functions — Download, sanitize, formatting helpers.
"""

import re
import requests
from pathlib import Path

from .config import logger


def download_file(url: str, save_path: str | Path) -> Path | None:
    """Download a file from URL."""
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

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
