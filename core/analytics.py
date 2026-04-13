"""
Analytics Dashboard — YouTube Performance Tracking

Generates weekly performance reports for all 4 channels using
YouTube Data API v3. Uses per-channel OAuth tokens from GitHub Secrets.

Metrics: views, likes, comments, subscriber count, top performing videos.
"""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from core.config import PROJECT_ROOT, logger

REPORT_DIR = PROJECT_ROOT / "logs" / "analytics"

# Channel name to YouTube channel mapping
CHANNELS = [
    "shadowedhistory",
    "sentinal_ihsan",
    "galactic_experiment",
    "aimagine",
]


def _get_youtube_service(channel_name: str):
    """Build YouTube service for a specific channel."""
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        env_key = f"YOUTUBE_OAUTH_{channel_name.upper()}"
        creds_json = os.getenv(env_key)

        if not creds_json:
            # Try local file
            local_file = PROJECT_ROOT / f"youtube_token_{channel_name}.json"
            if local_file.exists():
                creds_json = local_file.read_text()

        if not creds_json:
            logger.warning(f"No OAuth token for {channel_name}")
            return None

        creds_data = json.loads(creds_json)
        creds = Credentials.from_authorized_user_info(creds_data)
        return build("youtube", "v3", credentials=creds)
    except Exception as e:
        logger.error(f"YouTube API error for {channel_name}: {e}")
        return None


def get_channel_stats(channel_name: str) -> dict | None:
    """Get channel-level statistics (subscribers, views, videos)."""
    youtube = _get_youtube_service(channel_name)
    if not youtube:
        return None

    try:
        response = youtube.channels().list(
            part="statistics,snippet",
            mine=True
        ).execute()

        items = response.get("items", [])
        if not items:
            return None

        ch = items[0]
        stats = ch["statistics"]
        return {
            "channel": channel_name,
            "channel_title": ch["snippet"]["title"],
            "subscribers": int(stats.get("subscriberCount", 0)),
            "total_views": int(stats.get("viewCount", 0)),
            "total_videos": int(stats.get("videoCount", 0)),
        }
    except Exception as e:
        logger.error(f"Channel stats error for {channel_name}: {e}")
        return None


def get_recent_videos(channel_name: str, days: int = 7) -> list[dict]:
    """Get performance data for videos uploaded in the last N days."""
    youtube = _get_youtube_service(channel_name)
    if not youtube:
        return []

    try:
        # Get channel's uploads playlist
        ch_response = youtube.channels().list(
            part="contentDetails",
            mine=True
        ).execute()

        items = ch_response.get("items", [])
        if not items:
            return []

        uploads_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

        # Get recent uploads
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        videos = []
        next_page = None

        for _ in range(5):  # Max 5 pages
            pl_response = youtube.playlistItems().list(
                part="snippet",
                playlistId=uploads_id,
                maxResults=50,
                pageToken=next_page
            ).execute()

            for item in pl_response.get("items", []):
                published = item["snippet"]["publishedAt"]
                if published >= cutoff:
                    videos.append({
                        "video_id": item["snippet"]["resourceId"]["videoId"],
                        "title": item["snippet"]["title"],
                        "published": published,
                    })

            next_page = pl_response.get("nextPageToken")
            if not next_page:
                break

        if not videos:
            return []

        # Get stats for these videos
        video_ids = [v["video_id"] for v in videos]
        stats_response = youtube.videos().list(
            part="statistics",
            id=",".join(video_ids[:50])
        ).execute()

        stats_map = {}
        for item in stats_response.get("items", []):
            s = item["statistics"]
            stats_map[item["id"]] = {
                "views": int(s.get("viewCount", 0)),
                "likes": int(s.get("likeCount", 0)),
                "comments": int(s.get("commentCount", 0)),
            }

        for v in videos:
            v.update(stats_map.get(v["video_id"], {"views": 0, "likes": 0, "comments": 0}))

        # Sort by views descending
        videos.sort(key=lambda x: x["views"], reverse=True)
        return videos

    except Exception as e:
        logger.error(f"Recent videos error for {channel_name}: {e}")
        return []


def generate_weekly_report() -> dict:
    """Generate a comprehensive weekly performance report for all channels."""
    now = datetime.now(timezone.utc)
    report = {
        "generated_at": now.isoformat(),
        "period": f"{(now - timedelta(days=7)).strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}",
        "channels": [],
        "summary": {},
    }

    total_views = 0
    total_new_videos = 0
    best_video = None

    for channel_name in CHANNELS:
        logger.info(f"\n--- Analyzing {channel_name} ---")

        stats = get_channel_stats(channel_name)
        videos = get_recent_videos(channel_name, days=7)

        channel_data = {
            "name": channel_name,
            "stats": stats,
            "recent_videos": videos[:10],  # Top 10
            "weekly_views": sum(v["views"] for v in videos),
            "weekly_likes": sum(v["likes"] for v in videos),
            "weekly_comments": sum(v["comments"] for v in videos),
            "videos_posted": len(videos),
        }

        total_views += channel_data["weekly_views"]
        total_new_videos += len(videos)

        if videos and (best_video is None or videos[0]["views"] > best_video.get("views", 0)):
            best_video = {**videos[0], "channel": channel_name}

        report["channels"].append(channel_data)
        logger.info(f"  Subscribers: {stats['subscribers'] if stats else 'N/A'}")
        logger.info(f"  Weekly views: {channel_data['weekly_views']}")
        logger.info(f"  Videos posted: {len(videos)}")

    report["summary"] = {
        "total_weekly_views": total_views,
        "total_videos_posted": total_new_videos,
        "best_video": best_video,
    }

    # Save report
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"weekly_{now.strftime('%Y-%m-%d')}.json"
    report_path = REPORT_DIR / filename
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    logger.info(f"\nReport saved: {report_path}")

    # Generate markdown summary
    _generate_markdown_report(report, REPORT_DIR / f"weekly_{now.strftime('%Y-%m-%d')}.md")

    return report


def _generate_markdown_report(report: dict, output_path: Path):
    """Generate a human-readable markdown report."""
    summary = report["summary"]
    lines = [
        f"# Weekly YouTube Report",
        f"**Period:** {report['period']}",
        f"**Generated:** {report['generated_at'][:19]}",
        "",
        "## Summary",
        f"- Total Views: **{summary['total_weekly_views']:,}**",
        f"- Videos Posted: **{summary['total_videos_posted']}**",
    ]

    if summary.get("best_video"):
        bv = summary["best_video"]
        lines.extend([
            f"- Best Video: **{bv['title']}** ({bv['channel']}) — {bv['views']:,} views",
        ])

    lines.append("")
    lines.append("## Channel Breakdown")
    lines.append("")
    lines.append("| Channel | Subscribers | Weekly Views | Videos | Likes |")
    lines.append("|---------|------------|-------------|--------|-------|")

    for ch in report["channels"]:
        subs = ch["stats"]["subscribers"] if ch["stats"] else "?"
        lines.append(
            f"| {ch['name']} | {subs} | {ch['weekly_views']:,} | "
            f"{ch['videos_posted']} | {ch['weekly_likes']:,} |"
        )

    for ch in report["channels"]:
        if ch["recent_videos"]:
            lines.append(f"\n### {ch['name']} — Top Videos")
            lines.append("| # | Title | Views | Likes |")
            lines.append("|---|-------|-------|-------|")
            for i, v in enumerate(ch["recent_videos"][:5], 1):
                lines.append(f"| {i} | {v['title'][:50]} | {v['views']:,} | {v['likes']:,} |")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info(f"Markdown report: {output_path}")


if __name__ == "__main__":
    report = generate_weekly_report()
    print(json.dumps(report["summary"], indent=2))
