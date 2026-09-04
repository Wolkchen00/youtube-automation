"""
Seri Koşucusu ,  günlük otomasyon.

Her çalıştırmada bir serinin SIRADAKİ part'ını üretir, 3 platforma (upload-post)
yayınlar ve durumu ilerletir. GitHub Actions cron ile günde bir tetiklenir.

Kullanım:
  python -m series.series_runner                      # tüm aktif serilerin sıradaki part'ı
  python -m series.series_runner --series yaris        # sadece bu seri
  python -m series.series_runner --series yaris --dry-run     # üretim/yayın simülasyonu
  python -m series.series_runner --series yaris --no-publish  # üret ama yayınlama
"""

import os
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path
import sys
import time

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from core.config import logger
from core.kie_api import check_credit
from core.uploader import pop_upload_failure, upload_to_platform
from series import produce
from series import credit_gate
from series import notifier
from series.series_meta import SeriesMeta, part_plan_path, list_active_series
from series.shots import load_plan

import shutil
import subprocess

# GitHub Actions GITHUB_REPOSITORY'yi otomatik set eder; yerelde varsayılan.
REPO = os.environ.get("GITHUB_REPOSITORY", "Wolkchen00/youtube-automation")

_ALERT_SLUG: ContextVar[str | None] = ContextVar("series_alert_slug", default=None)
_FAILED_ALERT_SLUGS: set[str] = set()


def _alert(msg: str) -> bool:
    """Kritik alarmi duz metin gonder; basarisizsa kalici outbox'a yaz."""
    slug = _ALERT_SLUG.get()
    try:
        result = notifier.send_plain_message(msg)
        if result.delivered:
            return True
        if slug:
            _FAILED_ALERT_SLUGS.add(slug)
            notifier.enqueue_critical_alert(slug, msg, result.error)
        else:
            logger.error("❌ Kritik alarm teslim edilemedi; seri slug'i bulunamadi.")
        return False
    except Exception as e:
        if slug:
            _FAILED_ALERT_SLUGS.add(slug)
        logger.error(f"❌ Kritik alarm islenemedi ({type(e).__name__})")
        return False


def _series_alert(slug: str, msg: str) -> bool:
    """_alert icin seri baglamini kur ve teslim sonucunu cagirina tasir."""
    token = _ALERT_SLUG.set(slug)
    try:
        return _alert(msg)
    finally:
        _ALERT_SLUG.reset(token)


def _fleet_alert(msg: str) -> bool:
    """Filo alarmını mevcut drain'in ziyaret ettiği tek bir seri outbox'ına bağla."""
    known_slugs = _outbox_slugs(None)
    if known_slugs:
        return _series_alert(known_slugs[0], msg)
    # Henüz hiçbir seri dizini yoksa outbox evi de yoktur; yine düz gönder ve kırmızı dön.
    return _alert(msg)


def _balance_value(data) -> int | None:
    """Kie kredi yanıtını tek bir tam sayı bakiyeye indir."""
    if isinstance(data, (int, float)):
        return int(data)
    if isinstance(data, dict):
        for key in ("balance", "credit", "remaining"):
            value = data.get(key)
            if isinstance(value, (int, float)):
                return int(value)
    return None


def _actual_episode_spent(slug: str, part: int) -> int | None:
    """Maliyet izleyicisindeki bölüm toplamını yukarı doğru tam sayıya yuvarla."""
    spent = produce.episode_spent(slug, part)
    if spent is None:
        return None
    whole = int(spent)
    return whole if spent == whole else whole + 1


def _episode_chain_start(bible, meta: SeriesMeta) -> str | None:
    """Yalnız ayrı açık izin verilmişse önceki bölüm karesini oku."""
    if (bible and bible.chain_frames and bible.chain_scope == "series"
            and bible.allow_cross_episode_chaining):
        return meta.data.get("last_frame_url")
    return None


def _sample_frames(video_path, count: int = 3) -> list[str]:
    """Final videodan önizleme kareleri çıkar (Telegram onay mesajı için)."""
    ff = shutil.which("ffmpeg")
    if not ff:
        return []
    try:
        from core.ffmpeg_tools import get_video_duration
        dur = get_video_duration(video_path) or 8.0
    except Exception:
        dur = 8.0
    out_dir = Path(video_path).parent / "_frames"
    out_dir.mkdir(parents=True, exist_ok=True)
    frames: list[str] = []
    for i in range(1, count + 1):
        t = round(dur * i / (count + 1), 2)
        fp = out_dir / f"preview_{i}.jpg"
        try:
            subprocess.run([ff, "-loglevel", "error", "-y", "-ss", str(t), "-i", str(video_path),
                            "-frames:v", "1", "-q:v", "3", str(fp)], check=True)
            if fp.exists():
                frames.append(str(fp))
        except Exception:
            pass
    return frames


def _persist_release(slug: str, n: int, video_path) -> str | None:
    """Üretilen videoyu GitHub Release asset'i olarak sakla ,  üretim ve onay AYRI bulut
    koşularında olduğu için video kalıcı bir yerde durmalı. Release tag'ini döndürür."""
    gh = shutil.which("gh")
    if not gh:
        logger.warning("⚠️ gh CLI yok ,  Release persistence atlandı")
        return None
    tag = f"pending-{slug}-part{n}"
    subprocess.run([gh, "release", "delete", tag, "-R", REPO, "-y", "--cleanup-tag"],
                   capture_output=True, text=True)
    r = subprocess.run([gh, "release", "create", tag, str(video_path), "-R", REPO,
                        "--title", f"Pending {slug} Part {n}",
                        "--notes", "Telegram onayı bekliyor (otomatik)."],
                       capture_output=True, text=True)
    if r.returncode != 0:
        logger.error(f"❌ Release oluşturulamadı: {r.stderr.strip()}")
        return None
    logger.info(f"📦 Video Release'e yüklendi: {tag}")
    return tag


def _publish_identifier(result: dict, platform: str) -> str | None:
    """Upload-Post yanıtından platform video veya post kimliğini bul."""
    if not isinstance(result, dict):
        return None

    platform_result = None
    results = result.get("results")
    if isinstance(results, dict) and isinstance(results.get(platform), dict):
        platform_result = results[platform]

    preferred_keys = (
        f"{platform}_id",
        "video_id",
        "post_id",
        "media_id",
        "publication_id",
        "platform_id",
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

    return _search(platform_result) or _search(result)


def _async_publish_post_url(result: dict) -> str | None:
    """Yalnız doğrulanmış asenkron yanıttaki platform gönderi URL'sini bul.

    Senkron registry yolunu bit-değişmez bırakmak için bu ek alan yalnız uploader'ın
    doğrulama işareti varsa değerlendirilir.
    """
    if not isinstance(result, dict) or not result.get("_async_confirmation"):
        return None

    def _search(value) -> str | None:
        if isinstance(value, dict):
            found = value.get("post_url")
            if isinstance(found, str) and found.strip():
                return found.strip()
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

    return _search(result)


def _append_publish_registry(
    slug: str,
    n: int,
    subtitle: str,
    upload_results: dict[str, dict],
    unconfirmed: dict[str, dict] | None = None,
) -> None:
    """Başarılı part yayınını seri veri klasöründeki registry'ye ekle.

    Registry hiçbir koşulda asıl yayın akışını başarısız yapamaz.
    """
    try:
        import json
        from datetime import datetime, timezone
        from series.bible import data_dir

        registry_path = data_dir(slug) / "published.json"
        registry = []
        if registry_path.exists():
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            if not isinstance(registry, list):
                raise ValueError("published.json kökü liste değil")

        identifiers = {
            platform: _publish_identifier(result, platform)
            for platform, result in upload_results.items()
        }
        entry = {
            "part": n,
            "subtitle": str(subtitle),
            "ts": datetime.now(timezone.utc).isoformat(),
            "results": identifiers,
        }
        post_urls = {
            platform: url
            for platform, result in upload_results.items()
            if (url := _async_publish_post_url(result))
        }
        if post_urls:
            entry["post_urls"] = post_urls
        if unconfirmed:
            # Başarısız/belirsiz platform results/platforms_ok içine girmez; fakat
            # operatör işi sonradan durum endpoint'inde bulabilsin diye iş kimlikleri
            # ayrı ve açıkça "doğrulanmadı" alanında kalıcı tutulur.
            entry["unconfirmed"] = {
                platform: {
                    "reason": failure.get("reason"),
                    "request_id": failure.get("request_id"),
                    "job_id": failure.get("job_id"),
                }
                for platform, failure in unconfirmed.items()
            }
        # Kimlik çıkarılamayan platformun HAM yanıtını sakla: IG/TikTok kimlikleri
        # part 3'ten beri null geliyor ve yanıt şekli bilinmediği için _publish_identifier
        # körlemesine düzeltilemiyor. Bu alan bir sonraki yayında şekli görünür kılar.
        unresolved = {
            platform: str(upload_results.get(platform))[:600]
            for platform, ident in identifiers.items()
            if not ident
        }
        if unresolved:
            entry["results_raw"] = unresolved
            logger.warning(
                f"⚠️ Part {n}: {', '.join(sorted(unresolved))} için yayın kimliği "
                f"çıkarılamadı; ham yanıt registry'ye 'results_raw' olarak yazıldı."
            )
        registry.append(entry)
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        registry_path.write_text(
            json.dumps(registry, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info(f"📋 Part {n} yayın registry'sine eklendi: {registry_path}")
    except Exception as e:
        logger.warning(f"⚠️ Part {n} yayın registry'si yazılamadı: {e}")


def _publish_part(meta: SeriesMeta, n: int, video_path, subtitle: str = "",
                  caption: str = "") -> list[str]:
    """Part'ı serinin profilinden tüm platformlara yayınla. Başarılı platformları döndür.

    caption (opt-in, plan['caption'] ,  the__footnote formatı): bölümün YAZILI HİKÂYESİ.
    Verilirse YouTube açıklaması bu metin olur ve IG/TikTok'ta da (Upload-Post
    instagram_title/tiktok_title alanları üzerinden) uzun caption olarak basılır , 
    video sessiz-sinematik kalır, hikâyeyi açıklama anlatır. Boşsa eski davranış.

    4K master (bible.upscale) varsa yalnız YouTube'a gider; IG/TikTok 1080p
    delivery kopyasını alır ,  iki platform da videoyu zaten 1080p'ye yeniden
    kodladığı için 4K oraya sadece upload süresi/riski demek."""
    title = meta.title_for(n, subtitle)
    desc = (caption or meta.description_for(n, subtitle))[:4900]
    from series.bible import episode_dir
    delivery = episode_dir(meta.slug, n) / "delivery_1080.mp4"
    has_delivery = delivery.exists() and delivery.stat().st_size > 0
    ok: list[str] = []
    upload_results: dict[str, dict] = {}
    async_failures: dict[str, dict] = {}

    def _try(plat: str) -> bool:
        src = Path(video_path)
        if plat in ("instagram", "tiktok") and has_delivery and src.stem.endswith("_4k"):
            src = delivery
            logger.info(f"📤 {plat.upper()} → {title} (1080p delivery)")
        else:
            logger.info(f"📤 {plat.upper()} → {title}")
        res = upload_to_platform(src, title, desc,
                                 user=meta.upload_profile, platform=plat,
                                 tags=meta.hashtags, social_caption=caption)
        if res:
            upload_results[plat] = res if isinstance(res, dict) else {}
            async_failures.pop(plat, None)
        else:
            failure = pop_upload_failure(plat)
            if failure and failure.get("async"):
                async_failures[plat] = failure
        return bool(res)

    for plat in meta.platforms:
        if _try(plat):
            ok.append(plat)

    # Telafi turu: upload-post'un geçici arızası (SSL/5xx) bir platformu düşürdüyse,
    # API'ye toparlanma payı bırakıp başarısızları BİR kez daha dene. (2026-07-03
    # dersi: night-archive P1'de YouTube tam arıza penceresine denk geldi; IG/TikTok
    # 2 dk sonra sorunsuz geçmişti ,  tek tur telafi YouTube'u kurtarırdı.)
    # Kuyruğa kabul edilmiş fakat doğrulanamamış işi yeniden POST etmek çift yayın
    # doğurabilir. Bu işler telafi turuna değil, request_id'li operatör alarmına gider.
    failed = [p for p in meta.platforms if p not in ok and p not in async_failures]
    if failed:
        logger.info(f"🔁 Telafi turu: {', '.join(failed)} için 90s sonra yeniden denenecek…")
        time.sleep(90)
        for plat in failed:
            if _try(plat):
                ok.append(plat)

    for plat, failure in async_failures.items():
        if plat in ok:
            continue
        request_id = failure.get("request_id") or "-"
        job_id = failure.get("job_id") or "-"
        reason = failure.get("reason") or "belirsiz asenkron durum"
        _series_alert(meta.slug,
            f"⚠️ *{meta.base_title}* Part {n}: {plat.upper()} yayını doğrulanamadı. "
            f"Neden: {reason}. request_id={request_id}, job_id={job_id}"
        )

    logger.info(f"📊 Yayın: {len(ok)}/{len(meta.platforms)} platform OK")
    if ok:
        _append_publish_registry(
            meta.slug, n, subtitle, upload_results, unconfirmed=async_failures,
        )
    return ok


def _channel_published_today(meta: SeriesMeta) -> str | None:
    """Bu serinin KANALINA (upload_profile) bugün (UTC) yayın yapıldıysa 'slug Part N'
    döndür; yoksa None. Aynı profili paylaşan TÜM seriler taranır ,  böylece bir kanala
    farklı serilerden/şeritlerden aynı gün 2. video çıkamaz. Profil boşsa yalnız
    serinin kendi part geçmişine bakılır."""
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).date().isoformat()

    def _hit(m: SeriesMeta) -> str | None:
        for pn, p in (m.data.get("parts") or {}).items():
            if str(p.get("published_at", ""))[:10] == today:
                return f"{m.slug} Part {pn}"
        return None

    profile = meta.upload_profile
    if not profile:
        return _hit(meta)
    from series.bible import all_series_dirs
    for slug in all_series_dirs():
        m = meta if slug == meta.slug else SeriesMeta.load(slug)
        if m and m.upload_profile == profile:
            found = _hit(m)
            if found:
                return found
    return None


_NON_RETRYABLE_REASON_CODES = frozenset({"CONTENT_REJECT", "BUDGET_EXHAUSTED"})

# ROCK 3d: altyapi arizasi icerik reddi DEGILDIR ve icerik sayacini yakmamalidir.
# Gemini kotasi bitti diye bolum "insan baksin"a dusmemeli; ama altyapinin da
# SONSUZ hakki yoktur, yoksa kalici billing arizasinda hat her gun sessizce
# yeniden dener ve kimse haberdar olmaz. Bu yuzden ayri, SONLU bir butce.
_INFRA_REASON_CODES = frozenset({"QUOTA", "TRANSIENT_INFRA"})
_INFRA_RETRY_LIMIT = 6
_INFRA_MAX_AGE_HOURS = 48.0


def _infra_budget_spent(part: dict, count: int) -> tuple[bool, str]:
    """Altyapi butcesi doldu mu; dolduysa insana ne soylenecek."""
    if count >= _INFRA_RETRY_LIMIT:
        return True, f"{count} altyapi denemesi ({_INFRA_RETRY_LIMIT} hak) tukendi"
    started = part.get("first_infra_held_at")
    if started:
        try:
            age = (datetime.now(timezone.utc)
                   - datetime.fromisoformat(str(started))).total_seconds() / 3600.0
        except (TypeError, ValueError):
            return False, ""
        if age >= _INFRA_MAX_AGE_HOURS:
            return True, f"altyapi arizasi {age:.0f} saattir surüyor"
    return False, ""


def _approval_artifacts_complete(part: dict) -> bool:
    """Onay durumunun erişilebilir video, Release ve mesaj kimliği sözleşmesi."""
    return all(part.get(key) for key in ("video", "release_tag", "approval_msg_id"))


def migrate_malformed_approval_holds(meta: SeriesMeta, bible) -> bool:
    """Sürüm 2 serilerindeki çıkışsız eski onay kayıtlarını bir kez sınıflandır.

    Serbest metin hiçbir zaman sınıflandırmaya katılmaz. Eski kayıtta tipli kod yoksa
    güvenli varsayılan ``UNKNOWN`` olur ve yeniden denenebilir sayılır.
    """
    if not bible or bible.state_machine_version < 2:
        return False
    changed = False
    now = datetime.now(timezone.utc).isoformat()
    valid_codes = {
        "QUOTA", "REF_DOWNLOAD", "FRAME_EXTRACT", "AUDIO_MASTER",
        "CONTENT_REJECT", "BUDGET_EXHAUSTED", "TRANSIENT_INFRA", "UNKNOWN",
    }
    for part in meta.parts().values():
        if part.get("status") != "awaiting_approval" or _approval_artifacts_complete(part):
            continue
        code = part.get("last_reason_code")
        if code not in valid_codes:
            code = "UNKNOWN"
        try:
            retry_count = max(0, int(part.get("retry_count", 0)))
        except (TypeError, ValueError):
            retry_count = 0
        part["last_reason_code"] = code
        part["retry_count"] = retry_count
        part.setdefault("first_held_at", now)
        if code == "BUDGET_EXHAUSTED":
            part["status"] = "budget_exhausted"
        elif code == "CONTENT_REJECT" or retry_count >= 3:
            part["status"] = "needs_human"
        else:
            part["status"] = "qc_retry"
        changed = True
    if changed:
        meta.save()
        logger.info("♻️ Bozuk awaiting_approval kayıtları sürüm 2 durumlarına geçirildi.")
    return changed


def _terminalize_failure(meta: SeriesMeta, n: int, status: str,
                         result: produce.ProduceResult) -> None:
    """Terminal kayıt ile kuyruk ilerlemesini üretimden önce atomik kalıcılaştır."""
    part = meta.get_part(n)
    fields = {
        "hold_reason": result.reason or "üretim nedeni bilinmiyor",
        "last_reason_code": result.reason_code,
        "retry_count": int(part.get("retry_count", 0) or 0),
    }
    if part.get("first_held_at"):
        fields["first_held_at"] = part["first_held_at"]
    meta.terminalize_and_advance(n, status, **fields)


def _record_recoverable_failure(meta: SeriesMeta, n: int,
                                result: produce.ProduceResult) -> bool:
    """Hata durumunu yaz; işaretçi ilerlediyse True, yeniden denenecekse False."""
    code = result.reason_code
    if code in _NON_RETRYABLE_REASON_CODES:
        status = "budget_exhausted" if code == "BUDGET_EXHAUSTED" else "needs_human"
        _terminalize_failure(meta, n, status, result)
        _series_alert(meta.slug,
            f"🚨 *{meta.base_title}* Part {n} terminal duruma alındı: "
            f"{status} ({code}). Kuyruk sonraki bölüme ilerledi."
        )
        return True

    part = meta.get_part(n)
    now = datetime.now(timezone.utc).isoformat()

    # ROCK 3d: altyapi kaynakli hold ICERIK sayacini artirmaz, kendi sonlu
    # butcesinden harcar. Butce dolunca (deneme sayisi VEYA yas esigi) yine
    # insana devredilir; sessiz sonsuz dongu olusmaz.
    if code in _INFRA_REASON_CODES:
        try:
            infra_count = int(part.get("infra_retry_count", 0)) + 1
        except (TypeError, ValueError):
            infra_count = 1
        part.setdefault("first_held_at", now)
        part.setdefault("first_infra_held_at", now)
        part["infra_retry_count"] = infra_count
        part["last_reason_code"] = code
        part["hold_reason"] = result.reason or "üretim nedeni bilinmiyor"
        spent, why = _infra_budget_spent(part, infra_count)
        if spent:
            _terminalize_failure(meta, n, "needs_human", result)
            logger.error(
                f"🚨 Part {n} altyapi butcesi doldu ({why}); needs_human."
            )
            _series_alert(
                meta.slug,
                f"🚨 *{meta.base_title}* Part {n} altyapi arizasi giderilemedi "
                f"({why}, neden={code}). needs_human; kuyruk ilerledi.",
            )
            return True
        part["status"] = "qc_retry"
        meta.save()
        logger.warning(
            f"🔁 Part {n} altyapi yeniden denemesi "
            f"({infra_count}/{_INFRA_RETRY_LIMIT}, neden={code}); "
            f"icerik sayaci {int(part.get('retry_count', 0) or 0)}/3'te KORUNDU."
        )
        return False

    try:
        retry_count = int(part.get("retry_count", 0)) + 1
    except (TypeError, ValueError):
        retry_count = 1
    part.setdefault("first_held_at", now)
    part["retry_count"] = retry_count
    part["last_reason_code"] = code
    part["hold_reason"] = result.reason or "üretim nedeni bilinmiyor"
    if retry_count >= 3:
        _terminalize_failure(meta, n, "needs_human", result)
        logger.error(
            f"🚨 Part {n} üç başarısız denemeden sonra needs_human; kuyruktan düşürüldü."
        )
        _series_alert(meta.slug,
            f"🚨 *{meta.base_title}* Part {n} üç denemeden sonra needs_human. "
            "Kuyruk sonraki bölüme ilerledi."
        )
        return True
    part["status"] = "qc_retry"
    meta.save()
    logger.warning(
        f"🔁 Part {n} qc_retry ({retry_count}/3, neden={code}); sonraki koşuda yeniden üretilecek."
    )
    return False


def _budget_failure(slug: str, n: int, bible, plan: dict) -> produce.ProduceResult | None:
    """Ücretli işe başlamadan kalan çekimlerin korumacı tamamlanma tabanını denetle."""
    minimum = produce.minimum_remaining_completion_cost(slug, n, bible, plan)
    spent = produce.episode_spent(slug, n)
    cap = produce.episode_credit_cap(bible)
    remaining = None if spent is None else max(0.0, float(cap) - float(spent))
    if minimum is not None and remaining is not None and remaining >= minimum:
        return None
    reason = (
        f"kalan bölüm kredisi tamamlanma tabanına yetmiyor: kalan={remaining}, "
        f"asgari={minimum}, tavan={cap}"
    )
    return produce.ProduceResult(
        "generation_fail", reason=reason, reason_code="BUDGET_EXHAUSTED"
    )


def _continue_after_terminal(meta: SeriesMeta, slug: str, *, dry_run: bool,
                             publish: bool, force: bool) -> bool:
    """Kuyrukta bölüm kaldıysa devam et; yoksa terminal hatayı başarı diye sunma."""
    if meta.status != "active" or meta.next_part > meta.total_parts:
        return False
    return run_next(slug, dry_run=dry_run, publish=publish, force=force)


def run_next(slug: str, dry_run: bool = False, publish: bool = True,
             force: bool = False, strict_empty: bool = False) -> bool:
    """Serinin sıradaki part'ını üret + yayınla + durumu ilerlet.

    ``strict_empty``: koşu bu seriyi AÇIKÇA istediyse (``--series <slug>``) True
    gelir. O zaman "üretilecek bölüm yok" bir BAŞARI değildir. 2026-09-01..04
    arasında Galactic dört gün sessiz kaldı ve Event Horizon her gün ``success``
    raporladı: kuyruk tükenmişti, bu dal ``True`` dönüyordu, ``main()`` exit 0
    veriyordu. Aynı fonksiyonun 'Video ÇIKMAYAN her koşu KIRMIZI görünsün'
    sözü tam burada çiğneniyordu.

    Ayrım ``status`` ile DEĞİL, "bu kanal bugün yayın yapabilir miydi" ile
    yapılır; çünkü tükenen seriyi ``SeriesMeta.advance()`` kendiliğinden
    ``completed`` yapar, yani ``status`` tek başına niyeti ayırt etmez.
    """
    meta = SeriesMeta.load(slug)
    if not meta:
        return False
    if meta.status != "active" or meta.next_part > meta.total_parts:
        # (a) İhsan bilerek durdurmuş: bu bir arıza değil, kırmızı yanmamalı.
        #     from-scratch, next-stop ve 10+ pasif seri bu daldan geçer;
        #     hepsini kırmızıya çevirmek gerçek alarmı gürültüde boğardı.
        if meta.status in ("paused", "draft"):
            logger.info(f"⏸️ '{slug}' bilerek duraklatılmış (status={meta.status}) ,  yapacak iş yok.")
            return True

        tukendi = meta.next_part > meta.total_parts
        ikmal_acik = bool((meta.auto_replenish or {}).get("enabled"))

        # (b) Kendini besleyen bir seri tükendiyse kuyruğu dolduran mekanizma
        #     başarısız olmuş demektir. Koşu bu seriyi açıkça istediyse bu bir
        #     ARIZADIR: kanal o gün yayın yapamayacak.
        if tukendi and ikmal_acik and strict_empty:
            mesaj = (f"'{slug}' kuyruğu boş (part {meta.next_part}/{meta.total_parts}) ve "
                     f"oto-ikmal yeni bölüm yazamadı ,  bu kanala bugün video ÇIKMIYOR.")
            logger.error(f"❌ {mesaj}")
            if not dry_run:
                # Kuru koşu dış dünyaya alarm göndermez.
                _series_alert(slug, f"🔴 *{meta.base_title}*: {mesaj}")
            return False

        # (c) Sonlu, kendini beslemeyen seri doğal olarak bitti: tasarım böyle.
        logger.info(f"✅ '{slug}' tamamlandı (part {meta.total_parts}/{meta.total_parts}).")
        return True

    from series.bible import Bible, episode_dir
    bible = Bible.load(slug)
    chain_error = produce.chain_configuration_error(bible) if bible else None
    if chain_error:
        logger.error(f"❌ ZİNCİR GÜVENLİK KAPISI: {chain_error}")
        return False
    new_state_machine = bool(bible and bible.state_machine_version >= 2)
    if new_state_machine:
        migrate_malformed_approval_holds(meta, bible)

    n = meta.next_part
    mode = meta.data.get("publish_mode", "auto")

    # A QC hold is stronger than publish mode: later cron runs neither regenerate
    # nor publish until a human changes the part state.
    if meta.get_part(n).get("status") in ("awaiting_approval", "needs_human"):
        logger.info(f"⏳ Part {n} zorunlu QC/onay bekliyor ,  üretim ve yayın atlandı.")
        return True

    # GÜNDE-1 KİLİDİ (KANAL başına ,  İhsan kuralı 2026-07-03: "günde sadece 1 video").
    # Bu serinin KANALINA (upload_profile; aynı profili paylaşan TÜM seriler dahil)
    # BUGÜN zaten bir part yayınlandıysa üretme. Ana kuyruk (series.yml) + özel günlük
    # şeritler aynı güne/kanala denk geldiğinde çifte üretimi/krediyi ve aynı kanala
    # 2. videoyu önler. --force ile aşılır (İhsan bilerek aynı gün ikinci video isterse).
    if not force:
        prev = _channel_published_today(meta)
        if prev:
            logger.info(f"⏭️ Günde-1 kilidi: '{prev}' bugün aynı kanala "
                        f"({meta.upload_profile or slug}) yayınlandı ,  '{slug}' üretimi yarına bırakıldı.")
            return True

    plan_path = part_plan_path(slug, n)
    if not plan_path.exists():
        logger.error(f"❌ Part planı yok: {plan_path}")
        return False
    plan = load_plan(plan_path)
    from series.preflight import validate_required_platforms
    platform_errors = validate_required_platforms(bible, meta)
    if platform_errors:
        for error in platform_errors:
            logger.error(f"❌ {error}")
        logger.error("required_platforms hatası nedeniyle üretim kredi harcamadan durduruldu.")
        return False
    subtitle = plan.get("episode", {}).get("title", "")
    logger.info(f"🎬 '{meta.base_title}' Part {n}/{meta.total_parts} ,  {subtitle} (mod={mode})")

    # Hikâye-caption (opt-in, the__footnote formatı): plan 'caption' taşıyorsa bölümün
    # yazılı hikâyesi + bölüme-özgü etiketler + serinin marka etiketleri tek metinde
    # birleşir ve YT açıklaması + IG/TikTok caption'ı olur. Alan yoksa eski davranış.
    caption = str(plan.get("caption") or "").strip()
    if caption:
        tags = " ".join(t for t in (str(plan.get("hashtags") or "").strip(),
                                    meta.hashtags.strip()) if t)
        if tags:
            caption = f"{caption}\n\n{tags}"

    # 'Bitmeyen yolculuk' ,  önceki bölümün son karesinden devam (parçalar arası zincir).
    # Bulutta her koşu temiz checkout olduğu için son kare URL'i git'li series.json'da tutulur.
    # chain_scope="episode" ise zincir yalnız bölüm içi → önceki bölümün karesi OKUNMAZ.
    chain_start_url = _episode_chain_start(bible, meta)
    if chain_start_url:
        logger.info("🔗 Bitmeyen yolculuk: önceki bölümün son karesinden devam ediliyor.")

    # 1) Üret (idempotent ,  yarım kalmışsa sadece eksik çekimi üretir)
    if new_state_machine and not dry_run:
        budget_result = _budget_failure(slug, n, bible, plan)
        if budget_result is not None:
            _record_recoverable_failure(meta, n, budget_result)
            logger.error(f"💸 Part {n} budget_exhausted; ücretli çağrı başlatılmadı.")
            return _continue_after_terminal(
                meta, slug, dry_run=dry_run, publish=publish, force=force
            )

    reserved = False
    cap_value = produce.episode_credit_cap(bible) if bible else credit_gate.episode_cap()
    series_monthly_limit = produce.series_monthly_credit_cap(bible) if bible else None
    monthly_cap_value = (
        series_monthly_limit if series_monthly_limit is not None
        else credit_gate.monthly_cap()
    )
    durable_episode = bool(
        bible and bible.data["series"].get("durable_credit_ledger")
    )
    if not dry_run:
        balance = _balance_value(check_credit())
        threshold = cap_value * 1.5
        if not credit_gate.run_gate(balance, cap=cap_value):
            logger.error(
                f"❌ Kredi başlangıç kapısı kapalı: bakiye={balance}, eşik={threshold:g}"
            )
            _series_alert(meta.slug,
                f"❌ *{meta.base_title}* Part {n} kredi kapısında durdu. "
                f"bakiye={balance}, esik={threshold:g}"
            )
            return False
        if not credit_gate.reserve(
            slug, n, cap=cap_value, resume_episode=durable_episode,
            monthly_limit=series_monthly_limit,
        ):
            logger.error(
                f"❌ Aylık kredi tavanı üretimi durdurdu: "
                f"bölüm={cap_value}, tavan={monthly_cap_value}"
            )
            _series_alert(meta.slug,
                f"❌ *{meta.base_title}* Part {n} aylik tavan nedeniyle durdu. "
                f"bolum={cap_value}, tavan={monthly_cap_value}"
            )
            return False
        reserved = True
    try:
        produced = produce.produce_episode(
            slug, plan, dry_run=dry_run, chain_start_url=chain_start_url,
            typed_result=True,
        )
    finally:
        if reserved:
            actual_spent = _actual_episode_spent(slug, n)
            credit_gate.reconcile(slug, n, actual_spent, cap=cap_value)
    if dry_run:
        logger.info(f"[dry-run] Başlık olurdu: {meta.title_for(n, subtitle)}")
        return True
    if isinstance(produced, produce.ProduceResult):
        result = produced
    elif produced:
        result = produce.ProduceResult("ok", Path(produced))
    else:
        result = produce.ProduceResult("generation_fail")
    if new_state_machine and result.status != "ok":
        advanced = _record_recoverable_failure(meta, n, result)
        if advanced:
            # Terminal kayıt ile next_part aynı atomik yazımda tamamlandı. Yeni
            # bölüm üretimi ancak bu noktadan sonra başlayabilir.
            return _continue_after_terminal(
                meta, slug, dry_run=dry_run, publish=publish, force=force
            )
        return False
    if result.status == "qc_hold":
        part = meta.get_part(n)
        part["status"] = "awaiting_approval"
        part["hold_reason"] = result.reason or "mandatory QC could not be evaluated"
        meta.save()
        logger.error(f"⏸️ Part {n} QC HOLD ,  durum awaiting_approval; yayın bloke edildi.")
        _series_alert(meta.slug,
            f"⏸️ *{meta.base_title}* Part {n} zorunlu QC tarafından değerlendirilemedi. "
            "Durum awaiting_approval; otomatik üretim ve yayın durduruldu."
        )
        return True
    video = result.path
    if result.status != "ok" or not video:
        logger.error(f"❌ Part {n} üretilemedi ,  durum ilerletilmedi (sonraki çalıştırmada tekrar denenir).")
        _series_alert(
            meta.slug,
            f"❌ *{meta.base_title}* Part {n} ÜRETİLEMEDİ (içerik filtresi / motor hatası olabilir). "
            f"Bu kanala video çıkmadı ,  plan/prompt kontrol edilmeli.",
        )
        return False
    meta.mark_produced(n, video, subtitle)
    # Zincir: bu bölümün son karesini sonraki bölüm için series.json'a yaz (bulut-kalıcı).
    if (bible and bible.chain_frames and bible.chain_scope == "series"
            and bible.allow_cross_episode_chaining):
        sidecar = episode_dir(slug, n) / "last_frame.txt"
        if sidecar.exists():
            meta.data["last_frame_url"] = sidecar.read_text(encoding="utf-8").strip()
    meta.save()

    # 2a) ONAY MODU: videoyu sakla + Telegram'a "Yayınlansın mı?" sor; YAYINLAMA, İLERLETME.
    if mode == "approval":
        tag = _persist_release(slug, n, video)
        frames = _sample_frames(video, 3)
        msg_id = None
        if notifier.enabled():
            msg_id = notifier.request_approval(n, meta.title_for(n, subtitle), video, frames,
                                               slug=slug)
        else:
            logger.warning("⚠️ Telegram kapalı (token/chat yok) ,  onay mesajı gönderilemedi.")
        part = meta.get_part(n)
        part["release_tag"] = tag
        part["approval_msg_id"] = msg_id
        if new_state_machine and not _approval_artifacts_complete(part):
            missing = [
                key for key in ("video", "release_tag", "approval_msg_id")
                if not part.get(key)
            ]
            artifact_result = produce.ProduceResult(
                "generation_fail",
                reason=f"onay artefaktları eksik: {', '.join(missing)}",
                reason_code="UNKNOWN",
            )
            advanced = _record_recoverable_failure(meta, n, artifact_result)
            if advanced:
                return _continue_after_terminal(
                    meta, slug, dry_run=dry_run, publish=publish, force=force
                )
            return False
        part["status"] = "awaiting_approval"
        meta.save()
        logger.info(f"📨 Part {n} onaya gönderildi (Telegram). Yayın İhsan onayına bağlı.")
        return True

    # 2b) OTOMATİK MOD (eski davranış)
    if not publish:
        meta.advance()
        meta.save()
        logger.info(f"✅ Part {n} üretildi (yayın atlandı, --no-publish).")
        return True

    if not meta.upload_profile:
        logger.warning("⚠️ upload_profile boş ,  yayın atlandı. series.json'a upload_profile ekle.")
        return False

    ok = _publish_part(meta, n, video, subtitle, caption=caption)
    required_platforms = set(bible.required_platforms) if bible else set()
    # Iki taraf da kucuk harfe indirgenir: bible.required_platforms zaten
    # normalize edilir, ama yayinci "YouTube" dondururse zorunlu platform
    # sessizce "dogrulanmadi" sayilip kanali gereksiz yere karanlikta birakirdi.
    published_platforms = {str(p).strip().lower() for p in (ok or [])}
    publish_complete = bool(ok) and required_platforms.issubset(published_platforms)
    if publish_complete:
        dropped_roles = {
            str(shot_n): (
                "cold_open" if shot_n == 1
                else "loop_seam" if shot_n == len(plan.get("shots", []))
                else "episode_body"
            )
            for shot_n in result.dropped_shots
        }
        meta.mark_published(
            n, ok,
            dropped_shots=result.dropped_shots or None,
            dropped_shot_roles=dropped_roles or None,
            coherence=result.coherence or None,
        )
        meta.advance()
        meta.save()
        logger.info(f"🎉 Part {n} yayınlandı ({', '.join(ok)}): {meta.title_for(n, subtitle)}")
        if result.dropped_shots:
            role_text = ", ".join(
                f"çekim {shot_n} ({dropped_roles[str(shot_n)]})"
                for shot_n in result.dropped_shots
            )
            _series_alert(
                meta.slug,
                f"⚠️ *{meta.base_title}* Part {n} eksik çekimle yayınlandı. "
                f"Düşen roller: {role_text}.",
            )
        coherence = result.coherence or {}
        if coherence.get("degraded"):
            eksikler = []
            if coherence.get("loop_closed") is False:
                eksikler.append("loop kapanmadi")
            if coherence.get("narration_delivered") is False:
                eksikler.append("anlatim cikmadi")
            if coherence.get("duration_in_band") is False:
                eksikler.append(f"sure bant disi ({coherence.get('duration_s')} sn)")
            roller = coherence.get("arc_roles_missing") or []
            if roller:
                eksikler.append("dusen roller: " + ", ".join(roller))
            _series_alert(
                meta.slug,
                f"⚠️ *{meta.base_title}* Part {n} YAYINLANDI ama bölüm bütünlüğü "
                f"kusurlu: {'; '.join(eksikler)}. Kayıt part'ta 'coherence' altında.",
            )
        return True
    if ok and required_platforms:
        missing = sorted(required_platforms - published_platforms)
        logger.error(
            f"❌ Part {n} zorunlu platformlara yayınlanamadı: {', '.join(missing)}; "
            "durum ve işaretçi ilerletilmedi."
        )
        _series_alert(
            meta.slug,
            f"❌ *{meta.base_title}* Part {n} üretildi ancak zorunlu platformlar "
            f"doğrulanmadı: {', '.join(missing)}. Part yayınlandı sayılmadı.",
        )
        return False
    logger.error(f"❌ Part {n} hiçbir platforma yayınlanamadı ,  durum ilerletilmedi (yarın tekrar denenir).")
    _series_alert(
        meta.slug,
        f"❌ *{meta.base_title}* Part {n} ÜRETİLDİ ama hiçbir platforma YAYINLANAMADI "
        f"(upload-post / hesap bağlantısı kontrol edilmeli).",
    )
    return False


def _priority(slug: str) -> int:
    """Serinin günde-1 sırası (series.json['priority']; okunamazsa varsayılan 100)."""
    m = SeriesMeta.load(slug)
    return m.priority if m else 100


def run_all(dry_run: bool = False, publish: bool = True) -> bool:
    """GÜNDE TEK SERİ üret+yayınla (kredi tavanı) ,  İhsan kararı 2026-07-02.

    Her koşuda aktif seriler öncelik sırasına dizilir (series.json['priority'],
    küçük=önce, eşitlikte slug) ve yalnız İLK seri üretilir; kalanlar sırada
    bekler. Bir seri tamamlanınca (completed) listeden düşer → ertesi gün
    sıradaki otomatik devreye girer. Böylece tüm seriler günde 1 videoyla,
    elle müdahale gerekmeden art arda akar. Belirli bir seriyi elle koşturmak
    için --series (workflow_dispatch 'series' girdisi) tavandan etkilenmez.
    Üretim başarısız olursa BAŞKA seriye geçilmez (aynı gün ikinci üretim =
    çifte kredi); ertesi gün aynı seri kaldığı çekimden devam eder.
    """
    # Oto-ikmal: kuyruğu azalan auto_replenish'li serilere Gemini yeni planlar yazar.
    # Kie kredisi harcamaz; sırası gelmeden planların hazır olmasını sağlar.
    try:
        from series.replenish import replenish_all
        replenish_all(dry_run=dry_run)
    except Exception as e:
        logger.warning(f"⚠️ Oto-ikmal atlandı: {e}")
    slugs = list_active_series()
    if not slugs:
        logger.info("Aktif seri yok.")
        return _fleet_alert(
            "ℹ️ *Seri otomasyonu:* Aktif seri kalmadı ,  tüm diziler tamamlandı. "
            "Yeni sezon/part eklenene kadar bu kanallara yeni video ÇIKMAYACAK."
        )
    slugs.sort(key=lambda s: (_priority(s), s))
    chosen, waiting = slugs[0], slugs[1:]
    logger.info(f"🎯 Günde-1 tavanı: bugün '{chosen}' üretilecek"
                + (f" (sırada: {', '.join(waiting)})" if waiting else ""))
    return run_next(chosen, dry_run=dry_run, publish=publish)


def _outbox_slugs(slug: str | None) -> list[str]:
    if slug:
        return [slug]
    from series.bible import all_series_dirs

    return sorted(all_series_dirs())


def _drain_outboxes(slugs: list[str]) -> bool:
    """Uretimden once tum kritik alarmlari yeniden teslim etmeyi dene."""
    all_empty = True
    for item in slugs:
        _FAILED_ALERT_SLUGS.discard(item)
        if not notifier.drain_critical_alerts(item):
            all_empty = False
    return all_empty


def _outboxes_empty(slugs: list[str]) -> bool:
    return not any(
        item in _FAILED_ALERT_SLUGS or notifier.has_pending_critical_alerts(item)
        for item in slugs
    )


def _parse_args(argv: list[str]):
    """CLI'i KATI ayrıştır. Eksik/bozuk ``--series`` değeri PARA yakar.

    Eski hâli ``if "--series" in argv: slug = argv[i+1] if i+1 < len(argv)``
    idi. İki sessiz tuzağı vardı:
      1. ``--series`` son argümansa slug None kalır ve koşu ``run_all()`` yoluna
         düşer: istenmeyen, PARASI ÖDENMİŞ bir bölüm üretilir.
      2. ``--series --dry-run`` çağrısında slug "--dry-run" olur; seri bulunamaz,
         hata sebebi görünmez.
    argparse ikisini de çağrı anında reddeder.
    """
    import argparse

    p = argparse.ArgumentParser(
        prog="series.series_runner",
        description="Serinin sıradaki bölümünü üret + yayınla.",
    )
    p.add_argument("--series", dest="slug", default=None,
                   help="yalnız bu seriyi koştur (boş bırakılamaz)")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--no-publish", action="store_true")
    p.add_argument("--force", action="store_true",
                   help="günde-1 kilidini aş (bilerek aynı gün 2. video)")
    p.add_argument("--drain-alerts-only", action="store_true")
    args = p.parse_args(argv)
    if args.slug is not None and not str(args.slug).strip():
        p.error("--series boş olamaz")
    if args.slug is not None and str(args.slug).startswith("-"):
        p.error(f"--series bir seçenek değil, seri adı bekler: {args.slug!r}")
    return args


def main(argv: list[str]):
    args = _parse_args(argv)
    dry = args.dry_run
    no_pub = args.no_publish
    force = args.force          # günde-1 kilidini aş (bilerek aynı gün 2. video)
    drain_only = args.drain_alerts_only
    slug = args.slug
    outbox_slugs = _outbox_slugs(slug)
    if not _drain_outboxes(outbox_slugs):
        logger.error("❌ Kritik alarm outbox bos degil; uretim devam edecek, kosu sonda kirmizi olacak.")
    if drain_only:
        return
    if slug:
        # Koşu bu seriyi AÇIKÇA istedi: "üretilecek bölüm yok" başarı sayılmaz.
        # run_all yolu list_active_series ile tükenmiş serileri zaten eliyor,
        # bu yüzden ana kuyruk bu katılıktan etkilenmez.
        ok = run_next(slug, dry_run=dry, publish=not no_pub, force=force,
                      strict_empty=True)
    else:
        ok = run_all(dry_run=dry, publish=not no_pub)
    # Video ÇIKMAYAN her koşu KIRMIZI görünsün (sessiz 'success' yerine): üretim/yayın
    # hatası, kredi kapısı ve aylık tavan dahil. 2026-08-09..12 dört kanalın kredi
    # kapısında sessizce (yeşil) durması bu satırın 'ok is False' halinden kaynaklandı.
    if not dry and (ok is not True or not _outboxes_empty(outbox_slugs)):
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
