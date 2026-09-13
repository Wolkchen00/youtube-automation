#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Onceden uretilmis TEK bir videoyu serinin kanalina yayinlar (uc platform).

Seri motorunun uretim yolundan GECMEZ. Deney klasorunde ya da `hazir/` altinda
duran, QC'den gecmis ve elle onaylanmis bir dosyayi yayinlamak icindir.
Girdap (one-variable part 93) bu yolla elle yayinlandi; bu arac o adimlari
tekrarlanabilir hale getirir.

Kullanim:
    python tools/hazir_yayinla.py <video.mp4> --seri infinite-places --part 2 \
        --baslik "Infinite Neighborhood" --caption-dosya <caption.txt> [--yt-ek "#shorts"]
    ... --dry      (hicbir sey gondermez, ne gidecegini yazar)

Neden `publish_video` degil de platform basina `upload_to_platform`:
publish_video() social_caption parametresini GECIRMIYOR, IG ve TikTok'ta caption
yerine baslik kullaniliyor ve 100 karaktere kirpiliyor.

Mukerrer yayin korumasi: serinin `published.json` defterinde ayni part zaten
DOGRULANMIS bir YouTube kimligiyle duruyorsa yayin yapilmaz.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
if str(KOK) not in sys.path:
    sys.path.insert(0, str(KOK))


def _seri_oku(slug: str) -> dict:
    from series.bible import data_dir
    yol = data_dir(slug) / "series.json"
    if not yol.exists():
        sys.exit(f"seri bulunamadi: {yol}")
    return json.loads(yol.read_text(encoding="utf-8"))


def _zaten_yayinlandi(slug: str, part: int) -> str | None:
    """Ayni part dogrulanmis bir YouTube kimligiyle deftere gectiyse onu dondur."""
    from series.bible import data_dir
    yol = data_dir(slug) / "published.json"
    if not yol.exists():
        return None
    try:
        kayitlar = json.loads(yol.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(kayitlar, list):
        return None
    for k in kayitlar:
        if isinstance(k, dict) and k.get("part") == part:
            kimlik = (k.get("results") or {}).get("youtube")
            if kimlik and str(kimlik).strip():
                return str(kimlik).strip()
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--seri", required=True, help="seri slug'i (kanal profili ve defter buradan gelir)")
    ap.add_argument("--part", type=int, required=True, help="defter kaydinin part numarasi")
    ap.add_argument("--baslik", required=True, help="YouTube basligi")
    ap.add_argument("--caption-dosya", required=True, help="IG/TikTok caption metni (dosya)")
    ap.add_argument("--yt-ek", default="", help="YouTube aciklamasina eklenecek satir, orn. '#shorts'")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--atla-yayinlandiysa", action="store_true",
                    help="part zaten yayinlandiysa HATA verme, 0 ile cik (tekrarlayan cron icin)")
    a = ap.parse_args()

    video = Path(a.video)
    if not video.is_absolute():
        video = (KOK / video).resolve()
    if not video.exists() or video.stat().st_size == 0:
        sys.exit(f"video yok ya da bos: {video}")

    cap_yolu = Path(a.caption_dosya)
    if not cap_yolu.is_absolute():
        cap_yolu = (KOK / cap_yolu).resolve()
    if not cap_yolu.exists():
        sys.exit(f"caption dosyasi yok: {cap_yolu}")
    caption = cap_yolu.read_text(encoding="utf-8").strip()
    if not caption:
        sys.exit("caption bos")

    seri = _seri_oku(a.seri)
    profil = str(seri.get("upload_profile") or "").strip()
    platformlar = seri.get("platforms") or ["youtube", "instagram", "tiktok"]
    if not profil:
        sys.exit(f"{a.seri}: series.json icinde upload_profile yok")

    onceki = _zaten_yayinlandi(a.seri, a.part)
    if onceki:
        mesaj = f"part {a.part} zaten yayinlanmis (youtube={onceki}); mukerrer yayin engellendi."
        if a.atla_yayinlandiysa:
            print(mesaj + " --atla-yayinlandiysa verildi, cikis 0.")
            return 0
        sys.exit(mesaj)

    # YouTube aciklamasi caption + opsiyonel ek satir; IG/TikTok caption'i CIPLAK kalir.
    aciklama = f"{caption}\n\n{a.yt_ek}".strip() if a.yt_ek else caption

    print("=" * 66)
    print("seri       :", a.seri, "| part", a.part)
    print("kanal      :", profil, "|", ", ".join(platformlar))
    print("video      : %s (%.1f MB)" % (video.name, video.stat().st_size / 1e6))
    print("baslik     :", a.baslik)
    print("-" * 66)
    print("IG/TikTok caption:", caption)
    print("YouTube aciklamasi:", aciklama.replace("\n", " \\n "))
    print("=" * 66)
    if a.dry:
        print("KURU KOSU , hicbir sey gonderilmedi.")
        return 0

    from core.uploader import upload_to_platform
    from series.series_runner import _append_publish_registry

    sonuc: dict[str, dict] = {}
    for plat in platformlar:
        print(f"\n>> {plat.upper()} yukleniyor...", flush=True)
        try:
            r = upload_to_platform(
                video_path=video,
                title=a.baslik,
                description=aciklama[:4900],
                user=profil,
                platform=plat,
                social_caption=caption,
            )
        except Exception as exc:  # noqa: BLE001
            r = {"hata": str(exc)}
        sonuc[plat] = r if isinstance(r, dict) else {}
        print("   sonuc:", json.dumps(r, ensure_ascii=False)[:300])

    basarili = {p: r for p, r in sonuc.items() if r and "hata" not in r}
    _append_publish_registry(a.seri, a.part, a.baslik, basarili)

    from series.series_runner import _publish_identifier
    yt = _publish_identifier(sonuc.get("youtube") or {}, "youtube")
    print(f"\nozet: {len(basarili)}/{len(platformlar)} platform | youtube kimligi: {yt or 'YOK'}")
    if "youtube" in platformlar and not yt:
        print("YOUTUBE YAYINI DOGRULANAMADI , kosu basarisiz sayiliyor.")
        return 1
    return 0 if basarili else 1


if __name__ == "__main__":
    raise SystemExit(main())
