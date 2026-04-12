"""
Video Monitor — Auto-Cleanup System

Monitors uploaded YouTube videos and deletes underperformers after 48 hours.
Uses YouTube Data API v3 for view counts and video deletion.

Flow:
1. Read video_registry.json (uploaded video IDs + timestamps)
2. Check view counts via YouTube Data API
3. If views < threshold after 48h → delete video
4. Log deletion and mark for re-generation

SAFETY: First 7 days run in dry-run mode (log only, no deletions).
"""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from core.config import PROJECT_ROOT, MIN_VIEWS_THRESHOLD, logger

REGISTRY_FILE = PROJECT_ROOT / "logs" / "video_registry.json"
CLEANUP_LOG = PROJECT_ROOT / "logs" / "cleanup_log.json"

# Safety: dry-run for first 7 days after deployment
DEPLOYMENT_DATE = datetime(2026, 4, 12, tzinfo=timezone.utc)
SAFETY_PERIOD_DAYS = 7
VIDEO_AGE_HOURS = 48  # Check videos older than 48h


def load_registry() -> list[dict]:
    """Load the video registry."""
    if not REGISTRY_FILE.exists():
        return []
    try:
        return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_registry(registry: list[dict]):
    """Save the video registry."""
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_FILE.write_text(
        json.dumps(registry, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def log_cleanup_action(action: dict):
    """Append to cleanup log."""
    history = []
    if CLEANUP_LOG.exists():
        try:
            history = json.loads(CLEANUP_LOG.read_text(encoding="utf-8"))
        except Exception:
            history = []
    history.append(action)
    CLEANUP_LOG.parent.mkdir(parents=True, exist_ok=True)
    CLEANUP_LOG.write_text(
        json.dumps(history[-500:], ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def get_youtube_service(channel_name: str = None):
    """Build YouTube Data API v3 service using per-channel OAuth credentials.

    Tries in order:
    1. YOUTUBE_OAUTH_{CHANNEL} env var (per-channel token)
    2. YOUTUBE_OAUTH_CREDENTIALS env var (shared token)
    3. Local token file
    """
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        creds_json = None

        # 1. Try per-channel token
        if channel_name:
            env_key = f"YOUTUBE_OAUTH_{channel_name.upper()}"
            creds_json = os.getenv(env_key)
            if creds_json:
                logger.info(f"🔑 Using per-channel OAuth: {env_key}")

        # 2. Fallback: shared token
        if not creds_json:
            creds_json = os.getenv("YOUTUBE_OAUTH_CREDENTIALS")

        if creds_json:
            creds_data = json.loads(creds_json)
            creds = Credentials.from_authorized_user_info(creds_data)
            return build("youtube", "v3", credentials=creds)

        # 3. Fallback: local file
        if channel_name:
            local_file = PROJECT_ROOT / f"youtube_token_{channel_name}.json"
            if local_file.exists():
                creds_data = json.loads(local_file.read_text())
                creds = Credentials.from_authorized_user_info(creds_data)
                return build("youtube", "v3", credentials=creds)

        logger.warning("⚠️ No YouTube OAuth credentials found")
        return None
    except Exception as e:
        logger.error(f"❌ YouTube API setup failed: {e}")
        return None


def get_video_views(youtube, video_id: str) -> int | None:
    """Get view count for a YouTube video."""
    try:
        response = youtube.videos().list(
            part="statistics",
            id=video_id
        ).execute()

        items = response.get("items", [])
        if items:
            return int(items[0]["statistics"].get("viewCount", 0))
        return None  # Video not found (already deleted?)
    except Exception as e:
        logger.error(f"❌ Failed to get views for {video_id}: {e}")
        return None


def delete_youtube_video(youtube, video_id: str) -> bool:
    """Delete a YouTube video. THIS IS PERMANENT."""
    try:
        youtube.videos().delete(id=video_id).execute()
        logger.info(f"🗑️ Deleted YouTube video: {video_id}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to delete {video_id}: {e}")
        return False


def run_cleanup(dry_run: bool = False):
    """Main cleanup routine — check views, delete underperformers."""
    now = datetime.now(timezone.utc)

    # Safety check: force dry-run during safety period
    if now < DEPLOYMENT_DATE + timedelta(days=SAFETY_PERIOD_DAYS):
        days_left = (DEPLOYMENT_DATE + timedelta(days=SAFETY_PERIOD_DAYS) - now).days
        logger.info(f"🛡️ SAFETY MODE: {days_left} days until live deletions. Logging only.")
        dry_run = True

    registry = load_registry()
    if not registry:
        logger.info("📋 No videos in registry. Nothing to clean up.")
        return

    # Filter: only check videos older than 48h that are still active
    candidates = []
    for entry in registry:
        if entry.get("status") != "active":
            continue
        uploaded_at = datetime.fromisoformat(entry["uploaded_at"])
        age_hours = (now - uploaded_at).total_seconds() / 3600
        if age_hours >= VIDEO_AGE_HOURS:
            candidates.append(entry)

    if not candidates:
        logger.info(f"📋 No videos older than {VIDEO_AGE_HOURS}h to check.")
        return

    logger.info(f"🔍 Checking {len(candidates)} videos for cleanup...")

    # Build per-channel YouTube services
    youtube_services = {}
    for entry in candidates:
        ch = entry.get("channel", "unknown")
        if ch not in youtube_services:
            youtube_services[ch] = get_youtube_service(ch)

    deleted_count = 0
    kept_count = 0

    for entry in candidates:
        video_id = entry.get("youtube_video_id")
        channel = entry.get("channel", "unknown")
        threshold = MIN_VIEWS_THRESHOLD.get(channel, 30)

        if not video_id:
            continue

        youtube = youtube_services.get(channel)
        views = get_video_views(youtube, video_id) if youtube else 0

        if views is None:
            # Video already deleted or not found
            entry["status"] = "missing"
            logger.info(f"❓ {channel}/{video_id} — not found (already deleted?)")
            continue

        if views < threshold:
            action = {
                "timestamp": now.isoformat(),
                "channel": channel,
                "video_id": video_id,
                "title": entry.get("title", ""),
                "views": views,
                "threshold": threshold,
                "action": "DELETE" if not dry_run else "DRY_RUN_DELETE",
            }

            if dry_run:
                logger.info(f"🏃 [DRY RUN] Would delete {channel}/{video_id}: {views} views < {threshold} threshold")
            else:
                success = delete_youtube_video(youtube, video_id)
                if success:
                    entry["status"] = "deleted"
                    entry["deleted_at"] = now.isoformat()
                    entry["views_at_deletion"] = views
                    deleted_count += 1
                    logger.info(f"🗑️ Deleted {channel}/{video_id}: {views} views < {threshold}")

            log_cleanup_action(action)
        else:
            kept_count += 1
            logger.info(f"✅ Keeping {channel}/{video_id}: {views} views ≥ {threshold}")

    save_registry(registry)
    logger.info(f"\n📊 Cleanup summary: {deleted_count} deleted, {kept_count} kept, {len(candidates)} checked")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="YouTube Video Cleanup Monitor")
    parser.add_argument("--dry-run", action="store_true", help="Log only, don't delete")
    args = parser.parse_args()

    run_cleanup(dry_run=args.dry_run)
