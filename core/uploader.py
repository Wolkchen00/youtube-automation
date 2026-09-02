"""
Upload-Post.com — Multi-Platform Video Publisher

Publishes videos to YouTube Shorts, Instagram Reels, and TikTok
via the Upload-Post.com API.
"""

import re
import time

import requests
from pathlib import Path

from .config import UPLOAD_POST_API_KEY, UPLOAD_USERS, CHANNEL_PLATFORMS, logger
from .utils import normalize_title


UPLOAD_POST_URL = "https://api.upload-post.com/api/upload"
UPLOAD_POST_STATUS_URL = "https://api.upload-post.com/api/uploadposts/status"

# Arka plan işini sonsuza dek beklemek cron koşusunu kilitler. Bu değerler modül
# düzeyinde tutulur; üretimde güvenli bir tavan verirken testler sleep/saati kolayca
# enjekte edebilir.
ASYNC_UPLOAD_CONFIRM_TIMEOUT = 600
ASYNC_UPLOAD_POLL_INTERVALS = (5, 15, 30)
ASYNC_STATUS_REQUEST_TIMEOUT = 30

_ASYNC_SLEEP = time.sleep
_ASYNC_MONOTONIC = time.monotonic
_LAST_UPLOAD_FAILURES: dict[str, dict] = {}

# Bu boyutun üzerindeki dosyalar yüklenmeden önce bitrate-kapaklı bir 'delivery'
# kopyasına çevrilir. Upload-Post büyük gövdeleri akış ortasında kesiyor
# (ConnectionReset 10054) — grain'li/CRF'li kaynaklar 45s'de 140MB'ı aşabiliyor;
# Shorts zaten platformda ~2-6 Mbps'e yeniden kodlanıyor, kalite kaybı görünmez.
MAX_UPLOAD_MB = 80
_DELIVERY_MAXRATE = "6500k"
_DELIVERY_BUFSIZE = "13M"



# Mukerrer-baslik kapisi. 2026-09-02'de kanalda "Next Stop: The Deep" 3, "Next Stop:
# Hell" 5 kez birikmisti: ne gunluk boru hatti ne elle yayin, hicbiri yuklemeden
# once kanala bakmiyordu. Kapi upload_to_platform icindedir cunku olculen TEK
# tikanma noktasi orasi (cagiranlar: publish_video, series_runner:336).
# Onbellek modul duzeyindedir: bir bolumun youtube/instagram/tiktok cagrilari
# arasinda yasar, boylece bolum basina en fazla 1 RSS istegi atilir.
_channel_titles_cache: dict[str, set[str] | None] = {}

YOUTUBE_FEED_URL = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
CHANNEL_FEED_TIMEOUT = 5


def _channel_id_for_user(user: str) -> str | None:
    """Yukleme profilinden (ornegin 'Youtube') kanal kimligini coz."""
    from .analytics import CHANNELS  # dongusel import olmasin diye fonksiyon icinde

    hedef = str(user or "").strip().lower()
    if not hedef:
        return None
    for kanal_adi, profil in UPLOAD_USERS.items():
        if str(profil).strip().lower() == hedef:
            for kanal in CHANNELS:
                if kanal.get("name") == kanal_adi:
                    return kanal.get("channel_id")
    return None


def channel_recent_titles(user: str) -> set[str] | None:
    """Kanalin son yuklemelerinin normalize basliklari; DOGRULANAMAZSA None.

    None her zaman "kontrol edilemedi" demektir ve cagiran tarafta fail-open'a
    dusurur: bilinmeyen bir ag hatasi gunluk kanali karartmamali. Bu bilincli bir
    takas; kapi bir emniyet kemeri, kilit degil.
    """
    channel_id = _channel_id_for_user(user)
    if not channel_id:
        return None
    if channel_id in _channel_titles_cache:
        return _channel_titles_cache[channel_id]

    sonuc: set[str] | None = None
    try:
        resp = requests.get(
            YOUTUBE_FEED_URL.format(channel_id=channel_id),
            timeout=CHANNEL_FEED_TIMEOUT,
        )
        if resp.status_code == 200:
            basliklar = re.findall(
                r"<entry>.*?<title>(.*?)</title>", resp.text, re.S
            )
            if basliklar:
                sonuc = {normalize_title(b) for b in basliklar}
    except Exception as error:  # ag, zaman asimi, bozuk XML: hepsi ayni kova
        logger.warning(f"⚠️ Kanal akisi okunamadi ({user}): {error}")
        sonuc = None

    _channel_titles_cache[channel_id] = sonuc
    return sonuc

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


def _publication_identifier(body: dict, platform: str) -> str | None:
    """Yanıtta platforma ait gerçek yayın kimliği var mı, onu bul.

    request_id/job_id iş kimliğidir; özellikle anahtar listesine alınmaz. Böylece
    kuyruğa kabul edilen iş, platformda oluşmuş bir gönderiyle karıştırılmaz.
    """
    if not isinstance(body, dict):
        return None

    preferred_keys = (
        f"{platform}_id",
        "platform_post_id",
        "video_id",
        "post_id",
        "media_id",
        "publication_id",
        "platform_id",
        "external_id",
        "videoId",
        "postId",
        "mediaId",
        "id",
    )

    def _search(value) -> str | None:
        if isinstance(value, dict):
            for key in preferred_keys:
                found = value.get(key)
                if found is not None and not isinstance(found, (dict, list, bool)):
                    text = str(found).strip()
                    if text:
                        return text
            for nested in value.values():
                found = _search(nested)
                if found:
                    return found
        elif isinstance(value, list):
            for nested in value:
                found = _search(nested)
                if found:
                    return found
        return None

    entry = _platform_result(body, platform) or _status_platform_result(body, platform)
    found = _search(entry)
    if found:
        return found

    # Üst düzey kimlik eski senkron şemada meşrudur; buna karşılık body içindeki
    # rastgele bir nested `id` (ör. job/user id) platform yayın kimliği sayılamaz.
    for key in preferred_keys:
        value = body.get(key)
        if value is not None and not isinstance(value, (dict, list, bool)):
            text = str(value).strip()
            if text:
                return text
    return None


def _status_platform_result(body: dict, platform: str) -> dict | None:
    """Durum endpoint'inin liste şemasından ilgili platform girdisini bul."""
    if not isinstance(body, dict):
        return None
    results = body.get("results")
    if not isinstance(results, list):
        return None
    for entry in results:
        if isinstance(entry, dict) and str(entry.get("platform", "")).lower() == platform.lower():
            return entry
    return None


def _async_reference(body: dict) -> tuple[str | None, str | None]:
    """İş durumunu sorgulamak için request_id'yi, yoksa job_id'yi çıkar."""
    if not isinstance(body, dict):
        return None, None
    request_id = body.get("request_id")
    job_id = body.get("job_id")
    return (
        str(request_id).strip() if request_id else None,
        str(job_id).strip() if job_id else None,
    )


def _record_async_failure(
    platform: str,
    reason: str,
    request_id: str | None,
    job_id: str | None,
) -> None:
    """Seri koşucusunun mevcut uyarı yolunda kullanacağı tanı bağlamını sakla."""
    _LAST_UPLOAD_FAILURES[platform] = {
        "async": True,
        "reason": reason,
        "request_id": request_id,
        "job_id": job_id,
    }


def pop_upload_failure(platform: str) -> dict | None:
    """Son başarısız yüklemenin tanısını bir kez tüketilecek şekilde döndür."""
    return _LAST_UPLOAD_FAILURES.pop(platform, None)


def _status_outcome(body: dict, platform: str) -> tuple[str, str]:
    """Durum gövdesini success/failure/pending kararına indir."""
    entry = _status_platform_result(body, platform)
    entry_status = str((entry or {}).get("status") or "").lower()
    top_status = str(body.get("status") or "").lower()
    terminal_failures = {
        "failed", "error", "cancelled", "canceled", "rejected", "skipped",
    }
    terminal_states = terminal_failures | {"completed", "complete", "succeeded", "success", "published"}

    if entry is not None and entry.get("success") is True:
        return "success", "platform sonucu success=true"

    failed = body.get("failed")
    if isinstance(failed, (int, float)) and not isinstance(failed, bool) and failed >= 1:
        return "failure", f"failed={failed}"

    if entry is not None and entry.get("success") is False and entry_status in terminal_failures:
        return "failure", f"platform durumu={entry_status}"

    if entry is not None and entry.get("success") is False and (
        entry_status in terminal_states or top_status in terminal_states
    ):
        return "failure", f"terminal durumda platform success=false ({entry_status or top_status})"

    if top_status in terminal_failures:
        return "failure", f"iş durumu={top_status}"

    completed = body.get("completed")
    failed_is_zero = (
        isinstance(failed, (int, float)) and not isinstance(failed, bool) and failed == 0
    )
    platform_failed = entry is not None and entry.get("success") is False
    listed_results = body.get("results")
    platform_missing = isinstance(listed_results, list) and bool(listed_results) and entry is None
    if (
        isinstance(completed, (int, float))
        and not isinstance(completed, bool)
        and completed >= 1
        and failed_is_zero
        and not platform_failed
        and not platform_missing
    ):
        return "success", f"completed={completed}, failed=0"

    return "pending", str(body.get("message") or entry_status or top_status or "belirsiz durum")[:300]


def _confirmed_async_result(
    status_body: dict,
    platform: str,
    request_id: str | None,
    job_id: str | None,
) -> dict:
    """Doğrulama kanıtını, registry'nin kimlik/URL kaydedebileceği biçimde döndür."""
    confirmed = dict(status_body)
    confirmed.setdefault("request_id", request_id)
    confirmed.setdefault("job_id", job_id)
    confirmed["_async_confirmation"] = {
        "platform": platform,
        "request_id": request_id,
        "job_id": job_id,
    }
    identifier = _publication_identifier(status_body, platform)
    if identifier:
        # series_runner'ın mevcut kimlik çıkarıcısı publication_id'yi zaten tanır.
        confirmed.setdefault("publication_id", identifier)
    return confirmed


def _confirm_async_upload(
    initial_body: dict,
    platform: str,
    headers: dict,
    *,
    timeout: float | None = None,
    poll_intervals: tuple[float, ...] | list[float] | None = None,
    sleep_fn=None,
    monotonic_fn=None,
) -> dict | None:
    """Kuyruğa alınan işi terminal duruma kadar sorgula; belirsizlikte fail-closed."""
    request_id, job_id = _async_reference(initial_body)
    lookup_key = "request_id" if request_id else "job_id"
    lookup_value = request_id or job_id
    timeout = ASYNC_UPLOAD_CONFIRM_TIMEOUT if timeout is None else max(0, timeout)
    intervals = tuple(poll_intervals or ASYNC_UPLOAD_POLL_INTERVALS)
    if not intervals:
        intervals = (30,)
    sleep_fn = sleep_fn or _ASYNC_SLEEP
    monotonic_fn = monotonic_fn or _ASYNC_MONOTONIC
    started = monotonic_fn()
    poll_index = 0
    last_detail = "durum henüz alınmadı"

    logger.info(
        f"⏳ {platform.upper()} yüklemesi arka planda kabul edildi; yayın doğrulanıyor "
        f"(request_id={request_id or '-'}, job_id={job_id or '-'})"
    )

    while True:
        try:
            response = requests.get(
                UPLOAD_POST_STATUS_URL,
                headers=headers,
                params={lookup_key: lookup_value},
                timeout=ASYNC_STATUS_REQUEST_TIMEOUT,
            )
        except Exception as exc:
            reason = f"durum endpoint'i sorgulanamadı: {exc}"
            _record_async_failure(platform, reason, request_id, job_id)
            logger.error(
                f"❌ {platform.upper()} YAYIN DOĞRULANAMADI: {reason} "
                f"(request_id={request_id or '-'}, job_id={job_id or '-'})"
            )
            return None

        if response.status_code != 200:
            reason = f"durum endpoint'i HTTP {response.status_code} döndürdü"
            _record_async_failure(platform, reason, request_id, job_id)
            logger.error(
                f"❌ {platform.upper()} YAYIN DOĞRULANAMADI: {reason} "
                f"(request_id={request_id or '-'}, job_id={job_id or '-'})"
            )
            return None

        try:
            status_body = response.json()
            if not isinstance(status_body, dict):
                raise ValueError("JSON kökü nesne değil")
        except Exception as exc:
            reason = f"durum endpoint'i bozuk JSON döndürdü: {exc}"
            _record_async_failure(platform, reason, request_id, job_id)
            logger.error(
                f"❌ {platform.upper()} YAYIN DOĞRULANAMADI: {reason} "
                f"(request_id={request_id or '-'}, job_id={job_id or '-'})"
            )
            return None

        outcome, detail = _status_outcome(status_body, platform)
        last_detail = detail
        if outcome == "success":
            logger.info(
                f"✅ {platform.upper()} yayını doğrulandı: {detail} "
                f"(request_id={request_id or '-'}, job_id={job_id or '-'})"
            )
            return _confirmed_async_result(status_body, platform, request_id, job_id)
        if outcome == "failure":
            reason = f"durum endpoint'i terminal başarısızlık bildirdi: {detail}"
            _record_async_failure(platform, reason, request_id, job_id)
            logger.error(
                f"❌ {platform.upper()} YAYIN DOĞRULANAMADI: {reason} "
                f"(request_id={request_id or '-'}, job_id={job_id or '-'})"
            )
            return None

        elapsed = monotonic_fn() - started
        if elapsed >= timeout:
            reason = f"{timeout:g}s doğrulama zaman aşımı; son durum={last_detail}"
            _record_async_failure(platform, reason, request_id, job_id)
            logger.error(
                f"❌ {platform.upper()} YAYIN DOĞRULANAMADI: {reason} "
                f"(request_id={request_id or '-'}, job_id={job_id or '-'})"
            )
            return None

        delay = max(0.001, float(intervals[min(poll_index, len(intervals) - 1)]))
        remaining = timeout - elapsed
        sleep_fn(min(delay, remaining))
        poll_index += 1


def upload_to_platform(
    video_path: Path,
    title: str,
    description: str,
    user: str,
    platform: str = "youtube",
    privacy: str = "public",
    tags: str = "",
    social_caption: str = "",
    allow_duplicate_title: bool = False
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

    # Mukerrer-baslik kapisi. Yalniz YouTube: kanal gorunurlugumuz orada var, ve
    # YouTube gecip IG/TikTok dustugunde yapilan yeniden deneme tum yayini degil
    # sadece YouTube'u atlamali.
    if str(platform).strip().lower() == "youtube" and not allow_duplicate_title:
        kanal_basliklari = channel_recent_titles(user)
        if kanal_basliklari is None:
            logger.warning(
                "⚠️ Kanal dogrulanamadi; mukerrer kontrolu atlandi ve yayina "
                "devam ediliyor."
            )
        elif normalize_title(title) in kanal_basliklari:
            logger.error(
                f"❌ Mukerrer baslik: '{title}' bu kanalda zaten var; YouTube "
                "yuklemesi ATLANDI. Bilerek ikinci kez yayinlamak icin "
                "allow_duplicate_title=True."
            )
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

    MAX_UPLOAD_ATTEMPTS = 3
    UPLOAD_BACKOFF = [10, 30, 60]  # seconds between retries

    # Önceki çağrıdan kalan tanı, bu platformun yeni sonucuna sızmamalı.
    _LAST_UPLOAD_FAILURES.pop(platform, None)

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
                request_id, job_id = _async_reference(result)
                if not _publication_identifier(result, platform) and (request_id or job_id):
                    return _confirm_async_upload(result, platform, headers)
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
    platforms: list[str] | None = None,
    allow_duplicate_title: bool = False
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
            allow_duplicate_title=allow_duplicate_title,
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
