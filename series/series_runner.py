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
    """Part'ı serinin profilinden tüm platformlara yayınla. Başarılı platformları döndür."""
    title = meta.title_for(n, subtitle)
    desc = meta.description_for(n, subtitle)
    ok: list[str] = []
    for plat in meta.platforms:
        logger.info(f"📤 {plat.upper()} → {title}")
        res = upload_to_platform(Path(video_path), title, desc,
                                 user=meta.upload_profile, platform=plat,
                                 tags=meta.hashtags)
        if res:
            ok.append(plat)
    logger.info(f"📊 Yayın: {len(ok)}/{len(meta.platforms)} platform OK")
    return ok


def run_next(slug: str, dry_run: bool = False, publish: bool = True) -> bool:
    """Serinin sıradaki part'ını üret + yayınla + durumu ilerlet."""
    meta = SeriesMeta.load(slug)
    if not meta:
        return False
    if meta.status != "active" or meta.next_part > meta.total_parts:
        logger.info(f"✅ '{slug}' tamamlandı (part {meta.total_parts}/{meta.total_parts}).")
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

    # 1) Üret (idempotent — yarım kalmışsa sadece eksik çekimi üretir)
    video = produce.produce_episode(slug, plan, dry_run=dry_run)
    if dry_run:
        logger.info(f"[dry-run] Başlık olurdu: {meta.title_for(n, subtitle)}")
        return True
    if not video:
        logger.error(f"❌ Part {n} üretilemedi — durum ilerletilmedi (sonraki çalıştırmada tekrar denenir).")
        return False
    meta.mark_produced(n, video, subtitle)
    meta.save()

    # 2a) ONAY MODU: videoyu sakla + Telegram'a "Yayınlansın mı?" sor; YAYINLAMA, İLERLETME.
    if mode == "approval":
        tag = _persist_release(slug, n, video)
        frames = _sample_frames(video, 3)
        msg_id = None
        if notifier.enabled():
            msg_id = notifier.request_approval(n, meta.title_for(n, subtitle), frames)
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
    return False


def run_all(dry_run: bool = False, publish: bool = True):
    """Tüm aktif serilerin sıradaki part'ını çalıştır."""
    slugs = list_active_series()
    if not slugs:
        logger.info("Aktif seri yok.")
        return
    logger.info(f"Aktif seriler: {', '.join(slugs)}")
    for slug in slugs:
        run_next(slug, dry_run=dry_run, publish=publish)


def main(argv: list[str]):
    dry = "--dry-run" in argv
    no_pub = "--no-publish" in argv
    slug = None
    if "--series" in argv:
        i = argv.index("--series")
        if i + 1 < len(argv):
            slug = argv[i + 1]
    if slug:
        run_next(slug, dry_run=dry, publish=not no_pub)
    else:
        run_all(dry_run=dry, publish=not no_pub)


if __name__ == "__main__":
    main(sys.argv[1:])
