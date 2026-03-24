"""
ImgBB — Image Hosting

Uploads local images to ImgBB for use as Kie AI reference URLs.
"""

import requests
from pathlib import Path

from .config import IMGBB_API_KEY, IMGBB_UPLOAD_URL, logger


def upload_to_imgbb(local_path: str | Path) -> str | None:
    """Upload a local image to ImgBB. Returns public URL or None."""
    try:
        with open(local_path, "rb") as f:
            resp = requests.post(
                IMGBB_UPLOAD_URL,
                data={"key": IMGBB_API_KEY},
                files={"image": f},
                timeout=30
            )
        data = resp.json()
        if data.get("success"):
            url = data["data"]["url"]
            logger.info(f"📤 ImgBB uploaded: {url[:60]}...")
            return url
        else:
            logger.error(f"❌ ImgBB upload error: {data}")
            return None
    except Exception as e:
        logger.error(f"❌ ImgBB error: {e}")
        return None
