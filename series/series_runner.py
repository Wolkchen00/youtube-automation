"""
Seri Koşucusu — günlük otomasyon.

Her çalıştırmada bir serinin SIRADAKİ part'ını üretir, 3 platforma (upload-post)
yayınlar ve durumu ilerletir. GitHub Actions cron ile günde bir tetiklenir.

Kullanım:
  python -m series.series_runner                      # tüm aktif serilerin sıradaki part'ı
  python -m series.series_runner --series yaris        # sadece bu seri
  python -m series.series_runner --series yaris --dry-run     # üretim/yayın simülasyonu
  python -m series.series_runner --series yaris --no-publish  # üret ama yayınlama
"""

import os
import sys
import time

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from pathlib import Path

from core.config import logger
from core.uploader import upload_to_platform
from series import produce
from series import notifier
from series.series_meta import SeriesMeta, part_plan_path, list_active_series
from series.shots import load_plan

import shutil
import subprocess

# GitHub Actions GITHUB_REPOSITORY'yi otomatik set eder; yerelde varsayılan.
REPO = os.environ.get("GITHUB_REPOSITORY", "Wolkchen00/youtube-automation")


def _alert(msg: str) -> None:
    """Telegram'a sessizce uyarı gönder (token/chat yoksa no-op). Üretim/yayın
    başarısızlıklarının GÜNLERCE fark edilmeden geçmesini engeller."""
    try:
        if notifier.enabled():
            notifier.send_message(msg)
    except Exception as e:
        logger.warning(f"⚠️ Uyarı bildirimi gönderilemedi: {e}")


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
    """Üretilen videoyu GitHub Release asset'i olarak sakla — üretim ve onay AYRI bulut
    koşularında olduğu için video kalıcı bir yerde durmalı. Release tag'ini döndürür."""
    gh = shutil.which("gh")
    if not gh:
        logger.warning("⚠️ gh CLI yok — Release persistence atlandı")
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


def _publish_part(meta: SeriesMeta, n: int, video_path, subtitle: str = "") -> list[str]:
    """Part'ı serinin profilinden tüm platformlara yayınla. Başarılı platformları döndür.

    4K master (bible.upscale) varsa yalnız YouTube'a gider; IG/TikTok 1080p
    delivery kopyasını alır — iki platform da videoyu zaten 1080p'ye yeniden
    kodladığı için 4K oraya sadece upload süresi/riski demek."""
    title = meta.title_for(n, subtitle)
    desc = meta.description_for(n, subtitle)
    from series.bible import episode_dir
    delivery = episode_dir(meta.slug, n) / "delivery_1080.mp4"
    has_delivery = delivery.exists() and delivery.stat().st_size > 0
    ok: list[str] = []

    def _try(plat: str) -> bool:
        src = Path(video_path)
        if plat in ("instagram", "tiktok") and has_delivery and src.stem.endswith("_4k"):
            src = delivery
            logger.info(f"📤 {plat.upper()} → {title} (1080p delivery)")
        else:
            logger.info(f"📤 {plat.upper()} → {title}")
        res = upload_to_platform(src, title, desc,
                                 user=meta.upload_profile, platform=plat,
                                 tags=meta.hashtags)
        return bool(res)

    for plat in meta.platforms:
        if _try(plat):
            ok.append(plat)

    # Telafi turu: upload-post'un geçici arızası (SSL/5xx) bir platformu düşürdüyse,
    # API'ye toparlanma payı bırakıp başarısızları BİR kez daha dene. (2026-07-03
    # dersi: night-archive P1'de YouTube tam arıza penceresine denk geldi; IG/TikTok
    # 2 dk sonra sorunsuz geçmişti — tek tur telafi YouTube'u kurtarırdı.)
    failed = [p for p in meta.platforms if p not in ok]
    if failed:
        logger.info(f"🔁 Telafi turu: {', '.join(failed)} için 90s sonra yeniden denenecek…")
        time.sleep(90)
        for plat in failed:
            if _try(plat):
                ok.append(plat)

    logger.info(f"📊 Yayın: {len(ok)}/{len(meta.platforms)} platform OK")
    return ok


def _channel_published_today(meta: SeriesMeta) -> str | None:
    """Bu serinin KANALINA (upload_profile) bugün (UTC) yayın yapıldıysa 'slug Part N'
    döndür; yoksa None. Aynı profili paylaşan TÜM seriler taranır — böylece bir kanala
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
    from series.bible import SERIES_DATA_DIR
    from series.series_meta import series_meta_path
    if not SERIES_DATA_DIR.exists():
        return _hit(meta)
    for d in sorted(SERIES_DATA_DIR.iterdir()):
        if not (d.is_dir() and series_meta_path(d.name).exists()):
            continue
        m = meta if d.name == meta.slug else SeriesMeta.load(d.name)
        if m and m.upload_profile == profile:
            found = _hit(m)
            if found:
                return found
    return None


def run_next(slug: str, dry_run: bool = False, publish: bool = True,
             force: bool = False) -> bool:
    """Serinin sıradaki part'ını üret + yayınla + durumu ilerlet."""
    meta = SeriesMeta.load(slug)
    if not meta:
        return False
    if meta.status != "active" or meta.next_part > meta.total_parts:
        logger.info(f"✅ '{slug}' tamamlandı (part {meta.total_parts}/{meta.total_parts}).")
        return True

    # GÜNDE-1 KİLİDİ (KANAL başına — İhsan kuralı 2026-07-03: "günde sadece 1 video").
    # Bu serinin KANALINA (upload_profile; aynı profili paylaşan TÜM seriler dahil)
    # BUGÜN zaten bir part yayınlandıysa üretme. Ana kuyruk (series.yml) + özel günlük
    # şeritler aynı güne/kanala denk geldiğinde çifte üretimi/krediyi ve aynı kanala
    # 2. videoyu önler. --force ile aşılır (İhsan bilerek aynı gün ikinci video isterse).
    if not force:
        prev = _channel_published_today(meta)
        if prev:
            logger.info(f"⏭️ Günde-1 kilidi: '{prev}' bugün aynı kanala "
                        f"({meta.upload_profile or slug}) yayınlandı — '{slug}' üretimi yarına bırakıldı.")
            return True

    n = meta.next_part
    mode = meta.data.get("publish_mode", "auto")

    # Onay modu: bu part zaten onay bekliyorsa YENİDEN ÜRETME (approver yayınlayacak).
    if mode == "approval" and meta.get_part(n).get("status") == "awaiting_approval":
        logger.info(f"⏳ Part {n} zaten Telegram onayı bekliyor — üretim atlandı.")
        return True

    plan_path = part_plan_path(slug, n)
    if not plan_path.exists():
        logger.error(f"❌ Part planı yok: {plan_path}")
        return False
    plan = load_plan(plan_path)
    subtitle = plan.get("episode", {}).get("title", "")
    logger.info(f"🎬 '{meta.base_title}' Part {n}/{meta.total_parts} — {subtitle} (mod={mode})")

    # 'Bitmeyen yolculuk' — önceki bölümün son karesinden devam (parçalar arası zincir).
    # Bulutta her koşu temiz checkout olduğu için son kare URL'i git'li series.json'da tutulur.
    # chain_scope="episode" ise zincir yalnız bölüm içi → önceki bölümün karesi OKUNMAZ.
    from series.bible import Bible, episode_dir
    bible = Bible.load(slug)
    chain_start_url = None
    if bible and bible.chain_frames and bible.chain_scope == "series":
        chain_start_url = meta.data.get("last_frame_url")
        if chain_start_url:
            logger.info("🔗 Bitmeyen yolculuk: önceki bölümün son karesinden devam ediliyor.")

    # 1) Üret (idempotent — yarım kalmışsa sadece eksik çekimi üretir)
    video = produce.produce_episode(slug, plan, dry_run=dry_run, chain_start_url=chain_start_url)
    if dry_run:
        logger.info(f"[dry-run] Başlık olurdu: {meta.title_for(n, subtitle)}")
        return True
    if not video:
        logger.error(f"❌ Part {n} üretilemedi — durum ilerletilmedi (sonraki çalıştırmada tekrar denenir).")
        _alert(f"❌ *{meta.base_title}* Part {n} ÜRETİLEMEDİ (içerik filtresi / motor hatası olabilir). "
               f"Bu kanala video çıkmadı — plan/prompt kontrol edilmeli.")
        return False
    meta.mark_produced(n, video, subtitle)
    # Zincir: bu bölümün son karesini sonraki bölüm için series.json'a yaz (bulut-kalıcı).
    if bible and bible.chain_frames and bible.chain_scope == "series":
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
            msg_id = notifier.request_approval(n, meta.title_for(n, subtitle), video, frames)
        else:
            logger.warning("⚠️ Telegram kapalı (token/chat yok) — onay mesajı gönderilemedi.")
        part = meta.get_part(n)
        part["status"] = "awaiting_approval"
        part["release_tag"] = tag
        part["approval_msg_id"] = msg_id
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
        logger.warning("⚠️ upload_profile boş — yayın atlandı. series.json'a upload_profile ekle.")
        return False

    ok = _publish_part(meta, n, video, subtitle)
    if ok:
        meta.mark_published(n, ok)
        meta.advance()
        meta.save()
        logger.info(f"🎉 Part {n} yayınlandı ({', '.join(ok)}): {meta.title_for(n, subtitle)}")
        return True
    logger.error(f"❌ Part {n} hiçbir platforma yayınlanamadı — durum ilerletilmedi (yarın tekrar denenir).")
    _alert(f"❌ *{meta.base_title}* Part {n} ÜRETİLDİ ama hiçbir platforma YAYINLANAMADI "
           f"(upload-post / hesap bağlantısı kontrol edilmeli).")
    return False


def _priority(slug: str) -> int:
    """Serinin günde-1 sırası (series.json['priority']; okunamazsa varsayılan 100)."""
    m = SeriesMeta.load(slug)
    return m.priority if m else 100


def run_all(dry_run: bool = False, publish: bool = True) -> bool:
    """GÜNDE TEK SERİ üret+yayınla (kredi tavanı) — İhsan kararı 2026-07-02.

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
        _alert("ℹ️ *Seri otomasyonu:* Aktif seri kalmadı — tüm diziler tamamlandı. "
               "Yeni sezon/part eklenene kadar bu kanallara yeni video ÇIKMAYACAK.")
        return True
    slugs.sort(key=lambda s: (_priority(s), s))
    chosen, waiting = slugs[0], slugs[1:]
    logger.info(f"🎯 Günde-1 tavanı: bugün '{chosen}' üretilecek"
                + (f" (sırada: {', '.join(waiting)})" if waiting else ""))
    return run_next(chosen, dry_run=dry_run, publish=publish)


def main(argv: list[str]):
    dry = "--dry-run" in argv
    no_pub = "--no-publish" in argv
    force = "--force" in argv   # günde-1 kilidini aş (bilerek aynı gün 2. video)
    slug = None
    if "--series" in argv:
        i = argv.index("--series")
        if i + 1 < len(argv):
            slug = argv[i + 1]
    if slug:
        ok = run_next(slug, dry_run=dry, publish=not no_pub, force=force)
    else:
        ok = run_all(dry_run=dry, publish=not no_pub)
    # Gerçek bir üretim/yayın başarısızlığında iş KIRMIZI görünsün (sessiz 'success' yerine).
    if not dry and ok is False:
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
