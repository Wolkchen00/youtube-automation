"""YouTube kanalları için kimlik güvenli ölçüm omurgası.

Snapshot modu yalnızca sabit kanal kimlikleri ve ``YOUTUBE_API_KEY`` kullanır.
Rapor modu ağa çıkmaz; repo içindeki günlük snapshot dosyalarından hesaplanır.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from statistics import median
from typing import Any

import requests

from core.config import PROJECT_ROOT, logger

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
DATA_DIR = PROJECT_ROOT / "analytics_data"
REQUEST_TIMEOUT = 30

CHANNELS = (
    {
        "name": "shadowedhistory",
        "channel_id": "UCUdp0KLBh4EeeSgVbwS_DhA",
        "uploads": "UUUdp0KLBh4EeeSgVbwS_DhA",
    },
    {
        "name": "sentinal_ihsan",
        "channel_id": "UC-Aht8VqAUMTUKYRQA3agYQ",
        "uploads": "UU-Aht8VqAUMTUKYRQA3agYQ",
    },
    {
        "name": "galactic_experiment",
        "channel_id": "UCVCRWrQYrIHW6csOsw9bDNw",
        "uploads": "UUVCRWrQYrIHW6csOsw9bDNw",
    },
    {
        "name": "aimagine",
        "channel_id": "UCCgbHTzYKYawUT6zEo0nlDg",
        "uploads": "UUCgbHTzYKYawUT6zEo0nlDg",
    },
)


def _utc_now() -> datetime:
    """Saat bağımlı işlemler için tek UTC zaman kaynağı."""
    return datetime.now(timezone.utc)


def _integer(value: Any) -> int:
    """YouTube'un metin sayılarını güvenli biçimde tam sayıya çevir."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _parse_datetime(value: str) -> datetime:
    """ISO tarih-saat metnini UTC ve timezone-aware datetime olarak oku."""
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _api_get(resource: str, params: dict[str, Any], api_key: str) -> dict:
    """YouTube Data API GET isteğini yap ve JSON nesnesi döndür."""
    response = requests.get(
        f"{YOUTUBE_API_BASE}/{resource}",
        params={**params, "key": api_key},
        timeout=REQUEST_TIMEOUT,
    )
    if not response.ok:
        try:
            detail = response.json()
        except ValueError:
            detail = response.text[:500]
        raise RuntimeError(f"{resource} HTTP {response.status_code}: {detail}")
    body = response.json()
    if not isinstance(body, dict):
        raise ValueError(f"{resource} yanıtı JSON nesnesi değil")
    return body


def _fetch_channel(channel: dict[str, str], api_key: str) -> dict:
    """Tek kanalın istatistiklerini ve tam uploads listesini indir."""
    channel_response = _api_get(
        "channels",
        {
            "part": "statistics",
            "id": channel["channel_id"],
            "maxResults": 1,
        },
        api_key,
    )
    channel_items = channel_response.get("items") or []
    if not channel_items:
        raise RuntimeError(f"sabit kanal kimliği bulunamadı: {channel['channel_id']}")

    raw_stats = channel_items[0].get("statistics") or {}
    stats = {
        "subs": _integer(raw_stats.get("subscriberCount")),
        "total_views": _integer(raw_stats.get("viewCount")),
        "total_videos": _integer(raw_stats.get("videoCount")),
    }

    playlist_videos: dict[str, dict[str, Any]] = {}
    page_token: str | None = None
    while True:
        params: dict[str, Any] = {
            "part": "snippet,contentDetails",
            "playlistId": channel["uploads"],
            "maxResults": 50,
        }
        if page_token:
            params["pageToken"] = page_token
        playlist_response = _api_get("playlistItems", params, api_key)
        for item in playlist_response.get("items") or []:
            snippet = item.get("snippet") or {}
            content = item.get("contentDetails") or {}
            resource = snippet.get("resourceId") or {}
            video_id = content.get("videoId") or resource.get("videoId")
            if not video_id:
                continue
            playlist_videos[str(video_id)] = {
                "title": str(snippet.get("title") or ""),
                "published": str(
                    content.get("videoPublishedAt") or snippet.get("publishedAt") or ""
                ),
                "views": 0,
                "likes": 0,
                "comments": 0,
            }
        page_token = playlist_response.get("nextPageToken")
        if not page_token:
            break

    video_ids = list(playlist_videos)
    for offset in range(0, len(video_ids), 50):
        batch = video_ids[offset : offset + 50]
        videos_response = _api_get(
            "videos",
            {
                "part": "snippet,statistics",
                "id": ",".join(batch),
                "maxResults": 50,
            },
            api_key,
        )
        for item in videos_response.get("items") or []:
            video_id = str(item.get("id") or "")
            if video_id not in playlist_videos:
                continue
            snippet = item.get("snippet") or {}
            raw_video_stats = item.get("statistics") or {}
            playlist_videos[video_id] = {
                "title": str(snippet.get("title") or playlist_videos[video_id]["title"]),
                "published": str(
                    snippet.get("publishedAt") or playlist_videos[video_id]["published"]
                ),
                "views": _integer(raw_video_stats.get("viewCount")),
                "likes": _integer(raw_video_stats.get("likeCount")),
                "comments": _integer(raw_video_stats.get("commentCount")),
            }

    return {"stats": stats, "videos": playlist_videos}


def take_snapshot(api_key: str | None = None, now: datetime | None = None) -> dict | None:
    """Tüm sabit kanalları ölç, başarılı sonuçları günlük dosyaya yaz.

    Bir kanalın isteği bozulursa diğer kanallar devam eder. Dört kanalın tamamı
    başarısızsa dosya yazılmaz ve ``None`` döner.
    """
    key = (api_key if api_key is not None else os.getenv("YOUTUBE_API_KEY", "")).strip()
    if not key:
        logger.error("YOUTUBE_API_KEY boş veya tanımsız; snapshot fail-closed durduruldu.")
        return None

    generated = (now or _utc_now()).astimezone(timezone.utc)
    channels: dict[str, dict] = {}
    for channel in CHANNELS:
        name = channel["name"]
        try:
            logger.info(f"{name}: kanal ve video istatistikleri alınıyor.")
            channels[name] = _fetch_channel(channel, key)
            logger.info(f"{name}: {len(channels[name]['videos'])} video ölçüldü.")
        except Exception as exc:
            logger.exception(f"{name}: YouTube API ölçümü başarısız: {exc}")

    if not channels:
        logger.error("Tüm kanal ölçümleri başarısız; boş snapshot yazılmadı.")
        return None

    snapshot = {
        "generated_at": generated.isoformat(),
        "channels": channels,
    }
    daily_dir = DATA_DIR / "daily"
    daily_dir.mkdir(parents=True, exist_ok=True)
    output_path = daily_dir / f"{generated.date().isoformat()}.json"
    output_path.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info(f"Günlük snapshot yazıldı: {output_path}")
    return snapshot


def load_snapshots() -> list[tuple[date, dict]]:
    """Günlük snapshot dosyalarını dosya tarihine göre sıralı yükle."""
    daily_dir = DATA_DIR / "daily"
    snapshots: list[tuple[date, dict]] = []
    for path in sorted(daily_dir.glob("*.json")):
        try:
            snapshot_date = date.fromisoformat(path.stem)
            content = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(content, dict) or not isinstance(content.get("channels"), dict):
                raise ValueError("channels nesnesi yok")
            snapshots.append((snapshot_date, content))
        except Exception as exc:
            raise ValueError(f"Snapshot okunamadı: {path}: {exc}") from exc
    return sorted(snapshots, key=lambda item: item[0])


def _snapshot_time(snapshot_date: date, snapshot: dict) -> datetime:
    """Snapshot'ın ölçüm saatini, yoksa dosya gününün sonunu döndür."""
    generated_at = snapshot.get("generated_at")
    if generated_at:
        try:
            return _parse_datetime(str(generated_at))
        except (TypeError, ValueError):
            pass
    return datetime.combine(snapshot_date, time.max, tzinfo=timezone.utc)


def _views_after_48h(
    snapshots: list[tuple[date, dict]],
    channel_name: str,
    video_id: str,
    published: datetime,
) -> tuple[int | None, str | None]:
    """İlk uygun günlük snapshot'tan videonun 48 saat metriğini çıkar."""
    target_date = published.date() + timedelta(days=2)
    latest_usable_date = published.date() + timedelta(days=7)
    candidate: tuple[date, dict] | None = next(
        (
            (snapshot_date, snapshot)
            for snapshot_date, snapshot in snapshots
            if snapshot_date >= target_date
        ),
        None,
    )

    if candidate is None or candidate[0] > latest_usable_date:
        return None, "warmup"

    channel = (candidate[1].get("channels") or {}).get(channel_name)
    if not isinstance(channel, dict):
        return None, "warmup"
    video = (channel.get("videos") or {}).get(video_id)
    if not isinstance(video, dict):
        return None, "warmup"
    return _integer(video.get("views")), None


def _channel_report(
    channel_name: str,
    newest_date: date,
    newest_snapshot: dict,
    snapshots: list[tuple[date, dict]],
) -> dict:
    """Tek kanalın haftalık video listesini ve 30 günlük medyanını hesapla."""
    channel = (newest_snapshot.get("channels") or {}).get(channel_name) or {}
    videos = channel.get("videos") or {}
    as_of = _snapshot_time(newest_date, newest_snapshot)
    week_cutoff = as_of - timedelta(days=7)
    month_cutoff = as_of - timedelta(days=30)
    recent: list[dict] = []
    median_values: list[int] = []

    for video_id, video in videos.items():
        try:
            published = _parse_datetime(str(video.get("published") or ""))
        except (TypeError, ValueError):
            logger.warning(f"{channel_name}/{video_id}: yayın tarihi geçersiz, rapordan atlandı.")
            continue

        age = as_of - published
        if month_cutoff <= published <= as_of and age >= timedelta(hours=48):
            median_values.append(_integer(video.get("views")))

        if week_cutoff <= published <= as_of:
            views_48h, reason = _views_after_48h(
                snapshots, channel_name, str(video_id), published
            )
            item = {
                "video_id": str(video_id),
                "title": str(video.get("title") or ""),
                "published": str(video.get("published") or ""),
                "views": _integer(video.get("views")),
                "views_48h": views_48h,
                "views_48h_reason": reason,
            }
            recent.append(item)

    recent.sort(key=lambda item: item["published"], reverse=True)
    rolling_median = median(median_values) if median_values else None
    return {
        "stats": {
            "subs": _integer((channel.get("stats") or {}).get("subs")),
            "total_views": _integer((channel.get("stats") or {}).get("total_views")),
            "total_videos": _integer((channel.get("stats") or {}).get("total_videos")),
        },
        "videos_last_7_days": recent,
        "views_30d_median": rolling_median,
    }


def _markdown_cell(value: Any) -> str:
    """Markdown tablo hücresindeki ayırıcıları ve satır sonlarını temizle."""
    return str(value).replace("|", r"\|").replace("\r", " ").replace("\n", " ")


def _write_markdown(report: dict, output_path: Path) -> None:
    """JSON raporunun kısa, insan-okur Markdown karşılığını yaz."""
    lines = [
        "# Haftalık YouTube Raporu",
        "",
        f"**Dönem:** {report['period']}",
        f"**Snapshot tarihi:** {report['snapshot_date']}",
        f"**Üretim zamanı:** {report['generated_at']}",
        "",
        "## Kanal Özeti",
        "",
        "| Kanal | Abone | Toplam görüntüleme | Toplam video | 30 günlük medyan |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, channel in report["channels"].items():
        stats = channel["stats"]
        median_value = channel["views_30d_median"]
        median_text = "-" if median_value is None else f"{median_value:,}"
        lines.append(
            f"| {name} | {stats['subs']:,} | {stats['total_views']:,} | "
            f"{stats['total_videos']:,} | {median_text} |"
        )

    for name, channel in report["channels"].items():
        lines.extend(
            [
                "",
                f"## {name}",
                "",
                "| Video | Yayın zamanı | Güncel görüntüleme | 48 saat görüntüleme |",
                "|---|---|---:|---:|",
            ]
        )
        videos = channel["videos_last_7_days"]
        if not videos:
            lines.append("| Son 7 günde video yok | - | - | - |")
            continue
        for video in videos:
            metric = (
                "warmup"
                if video["views_48h"] is None
                else f"{video['views_48h']:,}"
            )
            lines.append(
                f"| {_markdown_cell(video['title'])} | {video['published']} | "
                f"{video['views']:,} | {metric} |"
            )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info(f"Markdown raporu yazıldı: {output_path}")


def _send_telegram_summary(report: dict) -> None:
    """Telegram açıksa kısa haftalık özeti gönder; hata raporu bozmasın."""
    try:
        from series import notifier

        if not notifier.enabled():
            return
        channel_count = len(report["channels"])
        video_count = sum(
            len(channel["videos_last_7_days"])
            for channel in report["channels"].values()
        )
        notifier.send_message(
            f"Haftalık YouTube analitiği hazır.\n"
            f"Kanal: {channel_count}, son 7 gün videosu: {video_count}\n"
            f"Snapshot: {report['snapshot_date']}"
        )
    except Exception as exc:
        logger.warning(f"Telegram analitik özeti gönderilemedi: {exc}")


def generate_weekly_report(now: datetime | None = None) -> dict:
    """Mevcut günlük snapshot'lardan haftalık JSON ve Markdown raporu üret."""
    snapshots = load_snapshots()
    if not snapshots:
        raise FileNotFoundError(f"Günlük snapshot bulunamadı: {DATA_DIR / 'daily'}")

    newest_date, newest_snapshot = snapshots[-1]
    generated = (now or _utc_now()).astimezone(timezone.utc)
    newest_channels = newest_snapshot["channels"]
    channels = {
        channel["name"]: _channel_report(
            channel["name"], newest_date, newest_snapshot, snapshots
        )
        for channel in CHANNELS
        if channel["name"] in newest_channels
    }
    report = {
        "generated_at": generated.isoformat(),
        "snapshot_date": newest_date.isoformat(),
        "period": (
            f"{(newest_date - timedelta(days=6)).isoformat()} "
            f"to {newest_date.isoformat()}"
        ),
        "channels": channels,
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    report_date = generated.date().isoformat()
    json_path = DATA_DIR / f"weekly_{report_date}.json"
    markdown_path = DATA_DIR / f"weekly_{report_date}.md"
    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info(f"Haftalık JSON raporu yazıldı: {json_path}")
    _write_markdown(report, markdown_path)
    _send_telegram_summary(report)
    return report


def main(argv: list[str] | None = None) -> int:
    """Komut satırı modunu çalıştır ve süreç çıkış kodunu döndür."""
    parser = argparse.ArgumentParser(description="YouTube snapshot ve haftalık rapor")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--snapshot", action="store_true", help="Günlük snapshot al")
    modes.add_argument("--report", action="store_true", help="Haftalık rapor üret")
    args = parser.parse_args(argv)

    if args.snapshot:
        return 0 if take_snapshot() is not None else 1

    try:
        generate_weekly_report()
        return 0
    except Exception as exc:
        logger.exception(f"Haftalık rapor üretilemedi: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
