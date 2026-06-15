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
from series.series_meta import SeriesMeta, part_plan_path, list_active_series
from series.shots import load_plan


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
    plan_path = part_plan_path(slug, n)
    if not plan_path.exists():
        logger.error(f"❌ Part planı yok: {plan_path}")
        return False
    plan = load_plan(plan_path)
    subtitle = plan.get("episode", {}).get("title", "")
    logger.info(f"🎬 '{meta.base_title}' Part {n}/{meta.total_parts} — {subtitle}")

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

    # 2) Yayınla
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
