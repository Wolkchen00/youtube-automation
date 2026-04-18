"""
Video Vault — Reuse Previously Generated Videos

Tracks all successfully generated videos. When a pipeline fails to produce
new clips, the vault provides unpublished videos for fallback publishing.

Key design:
  - Stores video URLs (not local paths) — GitHub Actions runners are ephemeral
  - Videos are re-downloaded from Kie AI CDN when reused
  - Expired URLs are auto-cleaned on access
  - Thread-safe JSON file storage
"""

import json
import requests
from datetime import datetime, timezone
from pathlib import Path

from .config import PROJECT_ROOT, LOGS_DIR, logger


VAULT_FILE = LOGS_DIR / "video_vault.json"


class VideoVault:
    """Manages a persistent vault of generated videos for fallback reuse."""

    def __init__(self):
        self._vault_path = VAULT_FILE
        self._ensure_file()

    def _ensure_file(self):
        """Create vault file if it doesn't exist."""
        self._vault_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._vault_path.exists():
            self._vault_path.write_text("[]", encoding="utf-8")

    def _load(self) -> list[dict]:
        """Load vault entries from disk."""
        try:
            data = json.loads(self._vault_path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception as e:
            logger.warning(f"⚠️ Vault load error: {e}")
            return []

    def _save(self, entries: list[dict]):
        """Save vault entries to disk. Keep last 200 entries max."""
        try:
            self._vault_path.write_text(
                json.dumps(entries[-200:], ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception as e:
            logger.error(f"❌ Vault save error: {e}")

    # ─── Public API ────────────────────────────────────────────────────────

    def save_video(
        self,
        channel: str,
        title: str,
        description: str,
        video_path: str,
        video_url: str = None,
        clip_urls: list[str] = None,
    ):
        """Save a successfully generated video to the vault.

        Args:
            channel: Channel name (e.g., "aimagine")
            title: Video title
            description: Full description with hashtags
            video_path: Local path to final video (for current run)
            video_url: CDN URL to the final merged video (if available)
            clip_urls: List of individual clip CDN URLs (for re-download)
        """
        entries = self._load()

        entry = {
            "channel": channel,
            "title": title,
            "description": description,
            "video_path": str(video_path),
            "video_url": video_url,
            "clip_urls": clip_urls or [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "unpublished",
            "published_at": None,
            "publish_attempts": 0,
        }

        entries.append(entry)
        self._save(entries)
        logger.info(f"📦 Vault: Saved video for {channel} — {title[:50]}")

    def get_unpublished(self, channel: str) -> dict | None:
        """Get the oldest unpublished video for a channel.

        Returns:
            Video entry dict or None if no unpublished videos exist.
        """
        entries = self._load()

        for entry in entries:
            if entry.get("channel") == channel and entry.get("status") == "unpublished":
                # Check if video URL is still valid
                if entry.get("video_url"):
                    if self._is_url_valid(entry["video_url"]):
                        logger.info(f"📦 Vault: Found unpublished video for {channel}: {entry['title'][:50]}")
                        return entry
                    else:
                        logger.warning(f"⚠️ Vault: URL expired for: {entry['title'][:50]}")
                        entry["status"] = "expired"

                # Try clip URLs as fallback
                elif entry.get("clip_urls"):
                    valid_clips = [url for url in entry["clip_urls"] if self._is_url_valid(url)]
                    if valid_clips:
                        entry["clip_urls"] = valid_clips
                        logger.info(f"📦 Vault: Found {len(valid_clips)} valid clips for {channel}")
                        return entry
                    else:
                        logger.warning(f"⚠️ Vault: All clip URLs expired for: {entry['title'][:50]}")
                        entry["status"] = "expired"

                # Local path fallback (only works on same machine, not GH Actions)
                elif entry.get("video_path") and Path(entry["video_path"]).exists():
                    logger.info(f"📦 Vault: Found local video for {channel}: {entry['title'][:50]}")
                    return entry

        # Save any status changes (expired entries)
        self._save(entries)
        return None

    def mark_published(self, channel: str, title: str):
        """Mark a vault video as published."""
        entries = self._load()

        for entry in entries:
            if (entry.get("channel") == channel
                    and entry.get("title") == title
                    and entry.get("status") == "unpublished"):
                entry["status"] = "published"
                entry["published_at"] = datetime.now(timezone.utc).isoformat()
                logger.info(f"✅ Vault: Marked as published — {title[:50]}")
                break

        self._save(entries)

    def increment_attempt(self, channel: str, title: str):
        """Increment publish attempt counter for a vault video."""
        entries = self._load()

        for entry in entries:
            if (entry.get("channel") == channel
                    and entry.get("title") == title
                    and entry.get("status") == "unpublished"):
                entry["publish_attempts"] = entry.get("publish_attempts", 0) + 1
                # Give up after 3 failed attempts
                if entry["publish_attempts"] >= 3:
                    entry["status"] = "failed"
                    logger.warning(f"⚠️ Vault: Giving up on {title[:50]} after 3 attempts")
                break

        self._save(entries)

    def get_stats(self) -> dict:
        """Get vault statistics."""
        entries = self._load()
        stats = {
            "total": len(entries),
            "unpublished": sum(1 for e in entries if e.get("status") == "unpublished"),
            "published": sum(1 for e in entries if e.get("status") == "published"),
            "expired": sum(1 for e in entries if e.get("status") == "expired"),
            "failed": sum(1 for e in entries if e.get("status") == "failed"),
        }

        # Per-channel breakdown
        channels = set(e.get("channel", "unknown") for e in entries)
        stats["by_channel"] = {}
        for ch in channels:
            ch_entries = [e for e in entries if e.get("channel") == ch]
            stats["by_channel"][ch] = {
                "total": len(ch_entries),
                "unpublished": sum(1 for e in ch_entries if e.get("status") == "unpublished"),
            }

        return stats

    @staticmethod
    def _is_url_valid(url: str) -> bool:
        """Check if a CDN URL is still accessible (HEAD request)."""
        try:
            resp = requests.head(url, timeout=10, allow_redirects=True)
            return resp.status_code == 200
        except Exception:
            return False


# ─── Module-level convenience instance ─────────────────────────────────────────
vault = VideoVault()
"""
Convenience: Import and use `from core.video_vault import vault`
- vault.save_video(channel, title, description, video_path, video_url, clip_urls)
- vault.get_unpublished(channel) -> dict | None
- vault.mark_published(channel, title)
"""
