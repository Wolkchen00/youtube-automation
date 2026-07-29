"""
Onay Yoklayıcı ,  Telegram'dan İhsan'ın ✅/❌ cevabını okuyup yayınlar/atlar.

GitHub Actions'ta sık cron ile çalışır (her ~10 dk). Onay bekleyen part varsa
getUpdates ile callback'i okur:
  ✅ Yayınla → Release'ten videoyu indir → 3 platforma yayınla → durumu ilerlet
  ❌ Atla    → part'ı atla, ilerlet
getUpdates offset'i series.json'da (tg_offset) tutulur ,  tekrar işlemeyi önler.

Kullanım: python -m series.approver [--series viral-detective]
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import shutil
import subprocess
from pathlib import Path

from core.config import logger, OUTPUT_DIR
from series import notifier
from series.series_meta import SeriesMeta, list_active_series
from series.series_runner import _publish_part, REPO


def match_decision(data: str, slug: str, n: int,
                   stored_msg_id, cb_msg_id) -> str | None:
    """Callback verisini karara çevir; seri-kimlikli yeni biçim + güvenli eski biçim.

    Yeni biçim: vd:<slug>:approve:<n> / vd:<slug>:reject:<n> (2026-07-29).
    Eski biçim (vd:approve:<n>) YALNIZ kayıtlı onay mesajının message_id'si
    callback'inkiyle eşleşiyorsa kabul edilir: birden çok seri aynı part
    numarasında beklerken slug'sız veri tek tıkla hepsini yayınlatabilirdi."""
    if data == f"vd:{slug}:approve:{n}":
        return "approve"
    if data == f"vd:{slug}:reject:{n}":
        return "reject"
    legacy_ok = stored_msg_id and cb_msg_id and stored_msg_id == cb_msg_id
    if legacy_ok and data == f"vd:approve:{n}":
        return "approve"
    if legacy_ok and data == f"vd:reject:{n}":
        return "reject"
    return None


def _download_release(tag: str) -> Path | None:
    gh = shutil.which("gh")
    if not gh or not tag:
        return None
    dest_dir = OUTPUT_DIR / "_approve"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{tag}.mp4"
    r = subprocess.run([gh, "release", "download", tag, "-R", REPO,
                        "--pattern", "*.mp4", "--output", str(dest), "--clobber"],
                       capture_output=True, text=True)
    if r.returncode != 0 or not dest.exists():
        logger.error(f"❌ Release indirilemedi ({tag}): {r.stderr.strip()}")
        return None
    return dest


def _cleanup_release(tag: str):
    gh = shutil.which("gh")
    if gh and tag:
        subprocess.run([gh, "release", "delete", tag, "-R", REPO, "-y", "--cleanup-tag"],
                       capture_output=True, text=True)


def _publish_approved(meta: SeriesMeta, n: int, part: dict) -> bool:
    """Onaylanmış part'ı yayınla ,  idempotent retry. Başarısızsa part['approved']=True
    kalır → sonraki kontrolde Telegram'a bakmadan TEKRAR denenir (onay kaybolmaz)."""
    video = _download_release(part.get("release_tag"))
    if not video:
        lv = part.get("video")
        video = Path(lv) if lv and Path(lv).exists() else None
    if not video:
        notifier.send_message(f"⚠️ *Part {n}* videosu bulunamadı (Release yok). Üretim tekrar gerekebilir.")
        logger.error(f"Part {n}: onaylandı ama video yok.")
        return False

    ok = _publish_part(meta, n, video, part.get("subtitle", ""))
    if ok:
        meta.mark_published(n, ok)
        meta.advance()
        meta.save()
        _cleanup_release(part.get("release_tag"))
        notifier.send_message(f"✅ *Part {n}* yayınlandı: {', '.join(ok)} 🎉")
        logger.info(f"Part {n} yayınlandı: {ok}")
        return True
    notifier.send_message(f"⚠️ *Part {n}* onaylandı ama yayın başarısız (platform hatası). Sonraki kontrolde tekrar denenecek.")
    logger.error(f"Part {n}: yayın başarısız (onay kayıtlı, retry edilecek).")
    return False


def process(slug: str) -> bool:
    meta = SeriesMeta.load(slug)
    if not meta:
        return False
    n = meta.next_part
    part = meta.get_part(n)
    if part.get("status") != "awaiting_approval":
        logger.info(f"'{slug}' Part {n}: onay bekleyen yok (status={part.get('status')}).")
        return True

    # Onay daha önce KAYDEDİLDİYSE (✅ okundu ama yayın takıldı) → Telegram'a bakmadan
    # doğrudan yayını tekrar dene. Böylece onay tg_offset tükense bile kaybolmaz.
    if part.get("approved"):
        logger.info(f"'{slug}' Part {n}: onay kayıtlı, yayın yeniden deneniyor.")
        return _publish_approved(meta, n, part)

    if not notifier.enabled():
        logger.warning("⚠️ Telegram kapalı (token/chat yok) ,  onay okunamıyor.")
        return False

    # Kart kimliği kayıpsa (persist arızası) kartı yeniden gönder: aksi halde İhsan'ın
    # elindeki eski kart güvenli eşleşme kuralına takılır ve onay yolu kilitlenir.
    if not part.get("approval_msg_id"):
        logger.warning(f"'{slug}' Part {n}: onay kartı kimliği yok, kart yeniden gönderiliyor.")
        video = _download_release(part.get("release_tag"))
        if video:
            msg_id = notifier.request_approval(
                n, meta.title_for(n, part.get("subtitle")), str(video), None, slug=slug)
            if msg_id:
                part["approval_msg_id"] = msg_id
                meta.save()
                logger.info(f"'{slug}' Part {n}: yeni onay kartı gönderildi (msg {msg_id}).")
        else:
            logger.error(f"'{slug}' Part {n}: release indirilemedi, kart yenilenemedi.")

    offset = meta.data.get("tg_offset")
    updates = notifier.get_updates(offset)
    decision = None
    cb_id = None
    new_offset = offset
    for u in updates:
        new_offset = max(new_offset or 0, u.get("update_id", 0) + 1)
        cq = u.get("callback_query")
        if not cq:
            continue
        verdict = match_decision(cq.get("data", ""), slug, n,
                                 part.get("approval_msg_id"),
                                 (cq.get("message") or {}).get("message_id"))
        if verdict:
            decision, cb_id = verdict, cq.get("id")
    if new_offset != offset:
        meta.data["tg_offset"] = new_offset
        meta.save()

    if not decision:
        logger.info(f"Part {n}: yeni onay/ret yok, bekleniyor.")
        return True

    notifier.answer_callback(cb_id, "İşleniyor…")

    # ❌ RET → atla
    if decision == "reject":
        part["status"] = "rejected"
        meta.advance()
        meta.save()
        _cleanup_release(part.get("release_tag"))
        notifier.send_message(f"❌ *Part {n}* atlandı (yayınlanmadı).")
        logger.info(f"Part {n} reddedildi → atlandı.")
        return True

    # ✅ ONAY → önce KALICI işaretle (offset tükense/yayın takılsa bile kaybolmaz), sonra yayınla
    part["approved"] = True
    meta.save()
    return _publish_approved(meta, n, part)


def main(argv: list):
    slug = None
    if "--series" in argv:
        i = argv.index("--series")
        if i + 1 < len(argv):
            slug = argv[i + 1]
    slugs = [slug] if slug else list_active_series()
    if not slugs:
        logger.info("Aktif seri yok.")
        return
    for s in slugs:
        process(s)


if __name__ == "__main__":
    main(sys.argv[1:])
