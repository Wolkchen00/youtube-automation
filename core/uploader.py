"""
Upload-Post.com — Multi-Platform Video Publisher

Publishes videos to YouTube Shorts, Instagram Reels, and TikTok
via the Upload-Post.com API.
"""

import requests
from pathlib import Path

from .config import UPLOAD_POST_API_KEY, UPLOAD_USERS, CHANNEL_PLATFORMS, logger


UPLOAD_POST_URL = "https://api.upload-post.com/api/upload"


def upload_to_platform(
    video_path: Path,
    title: str,
    description: str,
    user: str,
    platform: str = "youtube",
    privacy: str = "public",
    tags: str = ""
) -> dict | None:
    """Upload video to a single platform via Upload-Post.com."""
    if not UPLOAD_POST_API_KEY:
        logger.error("❌ UPLOAD_POST_API_KEY not set!")
        return None

    if not video_path.exists():
        logger.error(f"❌ Video not found: {video_path}")
        return None

    headers = {"Authorization": f"Apikey {UPLOAD_POST_API_KEY}"}

    data = {
        "title": title[:100],
        "user": user,
        "platform[]": platform,
    }

    if platform == "youtube":
        data["description"] = description[:5000]
        data["privacy"] = privacy
        if tags:
            data["tags"] = tags
    elif platform == "instagram":
        data["media_type"] = "REELS"
        data["share_to_feed"] = "true"
    elif platform == "tiktok":
        data["privacy_level"] = "PUBLIC_TO_EVERYONE"

    import time

    MAX_UPLOAD_ATTEMPTS = 3
    UPLOAD_BACKOFF = [10, 30, 60]  # seconds between retries

    for attempt in range(MAX_UPLOAD_ATTEMPTS):
        try:
            with open(video_path, "rb") as f:
                files = {"video": (video_path.name, f, "video/mp4")}
                response = requests.post(
                    UPLOAD_POST_URL,
                    headers=headers,
                    data=data,
                    files=files,
                    timeout=300
                )

            result = response.json()
            if response.status_code == 200:
                logger.info(f"✅ {platform.upper()} uploaded: {title[:50]}...")
                return result
            else:
                logger.error(f"❌ {platform.upper()} upload error (HTTP {response.status_code}): {result}")
                # Don't retry on auth/client errors (4xx)
                if 400 <= response.status_code < 500:
                    return None
                # Retry on server errors (5xx)
                if attempt < MAX_UPLOAD_ATTEMPTS - 1:
                    wait = UPLOAD_BACKOFF[attempt]
                    logger.info(f"  ⏳ Retrying in {wait}s (attempt {attempt + 2}/{MAX_UPLOAD_ATTEMPTS})...")
                    time.sleep(wait)
                    continue
                return None

        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
            logger.error(f"❌ Upload-Post connection error (attempt {attempt + 1}/{MAX_UPLOAD_ATTEMPTS}): {e}")
            if attempt < MAX_UPLOAD_ATTEMPTS - 1:
                wait = UPLOAD_BACKOFF[attempt]
                logger.info(f"  ⏳ SSL/Connection error, retrying in {wait}s...")
                time.sleep(wait)
                continue
            return None

        except Exception as e:
            logger.error(f"❌ Upload-Post unexpected error: {e}")
            return None

    return None


def publish_video(
    video_path: Path,
    title: str,
    description: str,
    channel_name: str,
    platforms: list[str] | None = None
) -> dict:
    """Publish video to all configured platforms for a channel.

    Args:
        video_path: Path to the video file
        title: Video title
        description: Video description/caption
        channel_name: Channel key (e.g., "shadowedhistory", "aimagine")
        platforms: Override platform list (default: use channel config)

    Returns:
        {platform: result} dict
    """
    upload_user = UPLOAD_USERS.get(channel_name, channel_name)
    target_platforms = platforms or CHANNEL_PLATFORMS.get(channel_name, ["youtube"])

    results = {}
    for platform in target_platforms:
        logger.info(f"📤 Publishing to {platform.upper()} (user: {upload_user})...")
        result = upload_to_platform(
            video_path=video_path,
            title=title,
            description=description,
            user=upload_user,
            platform=platform,
        )
        results[platform] = result

    success = sum(1 for v in results.values() if v)
    logger.info(f"📊 Upload summary: {success}/{len(target_platforms)} platforms OK")
    return results
