"""
Upload-Post.com — Multi-Platform Video Publisher

Publishes videos to YouTube Shorts, Instagram Reels, and TikTok
via the Upload-Post.com API.
"""

import requests
from pathlib import Path

from .config import UPLOAD_POST_API_KEY, UPLOAD_USERS, CHANNEL_PLATFORMS, logger


UPLOAD_POST_URL = "https://api.upload-post.com/api/upload"

# Bu boyutun üzerindeki dosyalar yüklenmeden önce bitrate-kapaklı bir 'delivery'
# kopyasına çevrilir. Upload-Post büyük gövdeleri akış ortasında kesiyor
# (ConnectionReset 10054) — grain'li/CRF'li kaynaklar 45s'de 140MB'ı aşabiliyor;
# Shorts zaten platformda ~2-6 Mbps'e yeniden kodlanıyor, kalite kaybı görünmez.
MAX_UPLOAD_MB = 80
_DELIVERY_MAXRATE = "6500k"
_DELIVERY_BUFSIZE = "13M"


def _delivery_copy(video_path: Path) -> Path:
    """Dosya MAX_UPLOAD_MB'ı aşıyorsa yükleme için sıkıştırılmış kopya döndür.

    Kaynak dosyaya dokunmaz; kopya yanına '<ad>_delivery.mp4' olarak cache'lenir
    (idempotent). Herhangi bir hatada orijinal yol döner (yükleme yine denenir)."""
    try:
        size_mb = video_path.stat().st_size / (1024 * 1024)
        if size_mb <= MAX_UPLOAD_MB:
            return video_path
        delivery = video_path.parent / f"{video_path.stem}_delivery.mp4"
        if delivery.exists() and delivery.stat().st_size > 0:
            return delivery
        import subprocess
        cmd = [
            "ffmpeg", "-y", "-i", str(video_path),
            "-c:v", "libx264", "-crf", "26",
            "-maxrate", _DELIVERY_MAXRATE, "-bufsize", _DELIVERY_BUFSIZE,
            "-preset", "fast",
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart",
            str(delivery),
        ]
        logger.info(f"📦 {size_mb:.0f}MB > {MAX_UPLOAD_MB}MB → delivery kopyası kodlanıyor...")
        subprocess.run(cmd, capture_output=True, check=True, timeout=900)
        if delivery.exists() and delivery.stat().st_size > 0:
            new_mb = delivery.stat().st_size / (1024 * 1024)
            logger.info(f"📦 Delivery hazır: {new_mb:.0f}MB ({delivery.name})")
            return delivery
    except Exception as e:
        logger.warning(f"⚠️ Delivery kopyası üretilemedi ({e}) — orijinal dosya denenecek")
    return video_path


def _platform_result(body: dict, platform: str) -> dict | None:
    """Upload-Post yanıtındaki tek platforma ait sonucu bul (varsa)."""
    if not isinstance(body, dict):
        return None
    results = body.get("results")
    if isinstance(results, dict):
        entry = results.get(platform)
        if isinstance(entry, dict):
            return entry
    return None


def _body_indicates_failure(body: dict, platform: str) -> bool:
    """HTTP 200 olsa bile gövde açıkça başarısızlık bildiriyor mu?

    Muhafazakâr davranır: yalnızca success alanı AÇIKÇA False ise True döner.
    Alan yoksa (eski/farklı şema) işi bozmamak için False (başarı) kabul edilir.
    """
    if not isinstance(body, dict):
        return False
    entry = _platform_result(body, platform)
    if entry is not None and entry.get("success") is False:
        return True
    return body.get("success") is False


def _extract_error(body: dict, platform: str) -> str:
    """Yanıttan insan-okur hata mesajını çıkar (loglamak için)."""
    entry = _platform_result(body, platform) or {}
    for src in (entry, body if isinstance(body, dict) else {}):
        for k in ("error", "message", "error_message", "detail"):
            v = src.get(k)
            if v:
                return str(v)[:300]
    return str(body)[:300]


def upload_to_platform(
    video_path: Path,
    title: str,
    description: str,
    user: str,
    platform: str = "youtube",
    privacy: str = "public",
    tags: str = "",
    social_caption: str = ""
) -> dict | None:
    """Upload video to a single platform via Upload-Post.com.

    social_caption (opt-in): IG/TikTok'ta 'title' yerine geçen UZUN caption metni.
    Upload-Post, Instagram'da instagram_title'ı ve TikTok'ta tiktok_title'ı post
    caption'ı olarak kullanır (global 'description' bu iki platformda YOK sayılır;
    TikTok video caption limiti 2.200 karakter). Boş bırakılırsa eski davranış —
    caption = title."""
    if not UPLOAD_POST_API_KEY:
        logger.error("❌ UPLOAD_POST_API_KEY not set!")
        return None

    if not video_path.exists():
        logger.error(f"❌ Video not found: {video_path}")
        return None

    # Büyük dosya → akış ortasında kesilme (10054). Gerekirse sıkıştırılmış kopya yükle.
    video_path = _delivery_copy(Path(video_path))

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
        if social_caption:
            data["instagram_title"] = social_caption[:2100]
    elif platform == "tiktok":
        data["privacy_level"] = "PUBLIC_TO_EVERYONE"
        if social_caption:
            data["tiktok_title"] = social_caption[:2100]

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

            result = response.json() if response.content else {}

            # ⚠️ Upload-Post HTTP 200 dönse BİLE gövdede başarısızlık bildirebilir
            # (ör. TikTok geçici kısıtlaması, sosyal hesap kopması). Sadece HTTP
            # koduna güvenmek, kanala hiç düşmeyen videoyu "✅ yayınlandı" gösterir.
            # Bu yüzden gövdedeki success alanını da kontrol ediyoruz.
            body_failed = _body_indicates_failure(result, platform)

            if response.status_code == 200 and not body_failed:
                logger.info(f"✅ {platform.upper()} uploaded: {title[:50]}...")
                return result

            err = _extract_error(result, platform)
            if response.status_code == 200 and body_failed:
                # API isteği geçti ama platforma gerçekte düşmedi → bu koşuda yeniden
                # denemek anlamsız (TikTok 'birkaç saat sonra' der). Sessizce başarı
                # sayma; None dön ki seri bu platformu 'OK' işaretlemesin.
                logger.error(f"❌ {platform.upper()} REDDEDİLDİ (HTTP 200 ama success=false): {err}")
                return None

            logger.error(f"❌ {platform.upper()} upload error (HTTP {response.status_code}): {err}")
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

    # Track YouTube video ID in registry for auto-cleanup monitoring
    youtube_result = results.get("youtube")
    if youtube_result and isinstance(youtube_result, dict):
        _register_video(
            channel_name=channel_name,
            title=title,
            youtube_result=youtube_result,
        )

    return results


def _register_video(channel_name: str, title: str, youtube_result: dict):
    """Save video info to registry for cleanup monitoring."""
    import json
    from datetime import datetime, timezone
    from .config import PROJECT_ROOT

    registry_file = PROJECT_ROOT / "logs" / "video_registry.json"

    registry = []
    if registry_file.exists():
        try:
            registry = json.loads(registry_file.read_text(encoding="utf-8"))
        except Exception:
            registry = []

    # Extract video ID from Upload-Post response
    video_id = youtube_result.get("id") or youtube_result.get("video_id") or ""

    entry = {
        "channel": channel_name,
        "title": title,
        "youtube_video_id": video_id,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "status": "active",
    }

    registry.append(entry)
    registry_file.parent.mkdir(parents=True, exist_ok=True)
    registry_file.write_text(
        json.dumps(registry[-200:], ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    logger.info(f"📋 Registered video: {channel_name}/{video_id}")
