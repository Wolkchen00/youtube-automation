"""KAPI rotasinin baslangic gorselini hazirlar, Seedance'e verilecek URL'yi dondurur.

Neden: 2026-10-01 mevsim kapisi ornekleri metinden videoda bacaklari bozdu (bilekte
siyah kayis, iki bacak tek govdeye kaynasti, havada isik cizgisi). Ayni promptu bir
BASLANGIC GORSELINDEN baslatinca iki uretimde de bacaklar bastan sona ayri kaldi.
Bkz. AImagine-Fear/REELYZE-RAPOR.md "Ornek uretimi (1 Ekim)".

Oncelik sirasi:
  1. ilk_kare/<slug>.jpg (ya da .png): gozle ONAYLANMIS gorsel, depoda. Kie'nin
     gecici deposuna yuklenir, uretim yapilmaz. Rastlantiya yer birakmaz.
  2. Yoksa out/<slug>/ILK_KARE.txt -> nano-banana-2 -> kamera silme duzenlemesi.
     Duzenleme her zaman kosar: ilk denemede gogus kamerasi kadrajin altinda
     gorundu ve prompttaki yasak tek basina yetmedi.

Kullanim (elle onay icin):
    python tools/ilk_kare.py <slug>            # uretir, out/<slug>/ilk_kare.png yazar
    python tools/ilk_kare.py <slug> --onayla   # ayrica ilk_kare/<slug>.jpg olarak kaydeder
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import requests

KOK = Path(__file__).resolve().parent.parent
YT_KOK = KOK.parent
ONAYLI_KLASOR = KOK / "ilk_kare"
YUKLEME = "https://kieai.redpandaai.co/api/file-stream-upload"
MODEL = "nano-banana-2"
# Uretim + duzenleme, iki gorsel. 2026-10-01 bakiye farkindan: uc gorsel 88 kredi.
# Tahmindir; gunluk.py kredi on kontrolune pay olarak eklenir.
KREDI = 70
DUZELTME = (
    "Edit this photo. Remove any action camera, chest mount, strap or harness visible at "
    "the bottom of the frame; in its place show only the black high-cut one-piece swimsuit "
    "at the hips and the clear transparent slide. If there is no camera, change nothing. "
    "Keep everything else exactly identical: the two bare legs, the feet, the slide, the "
    "glowing rims, the landmark, the sky, the clouds, the light and the framing."
)


class IlkKareHatasi(RuntimeError):
    """Baslangic gorseli hazirlanamadi; Seedance'e gidilmez, kredi yanmaz."""


def _anahtar() -> str:
    sys.path.insert(0, str(KOK / "tools"))
    import kie_uret

    return kie_uret.api_key()


def onayli_yol(slug: str, klasor: Path | None = None) -> Path | None:
    klasor = klasor or ONAYLI_KLASOR
    for uzanti in (".jpg", ".png"):
        yol = klasor / (slug + uzanti)
        if yol.is_file() and yol.stat().st_size > 0:
            return yol
    return None


def yukle(yol: Path) -> str:
    """Yerel gorseli Kie'nin gecici deposuna yukler (3 gun saklanir), URL dondurur."""
    tur = "image/png" if yol.suffix.lower() == ".png" else "image/jpeg"
    with yol.open("rb") as dosya:
        yanit = requests.post(
            YUKLEME,
            headers={"Authorization": "Bearer " + _anahtar()},
            files={"file": (yol.name, dosya, tur)},
            data={"uploadPath": "images", "fileName": yol.name},
            timeout=300,
        )
    try:
        veri = yanit.json()
    except ValueError:
        raise IlkKareHatasi("yukleme yaniti JSON degil (HTTP %s)" % yanit.status_code)
    govde = veri.get("data") or veri
    url = govde.get("downloadUrl") or govde.get("fileUrl") or govde.get("file_url")
    if not url:
        raise IlkKareHatasi("yukleme URL dondurmedi: %s" % str(veri)[:300])
    return url


def _gorsel(prompt: str, referans: str | None = None) -> str:
    """nano-banana-2 ile tek gorsel. core.kie_api.generate_image KULLANILMAZ: hata
    aldiginda promptu 300 karaktere kirpip yeniden deniyor, o da sahne tarifi
    olmayan bir kare uretir ve video ona kilitlenir."""
    os.environ.setdefault("KIE_AI_API_KEY", _anahtar())
    if str(YT_KOK) not in sys.path:
        sys.path.insert(0, str(YT_KOK))
    from core import kie_api

    girdi = {"prompt": prompt, "aspect_ratio": "9:16", "resolution": "1K",
             "output_format": "png"}
    if referans:
        girdi["image_input"] = [referans]
    url = kie_api.generate_and_wait({"model": MODEL, "input": girdi}, is_video=False)
    if not url:
        raise IlkKareHatasi("%s gorsel uretemedi" % MODEL)
    return url


def uret(prompt: str, hedef: Path) -> str:
    """Sahneyi uretir, kamerayi sildirir, sonucu hedef'e kaydeder, URL dondurur."""
    ham = _gorsel(prompt)
    try:
        temiz = _gorsel(DUZELTME, referans=ham)
    except IlkKareHatasi as hata:
        # 2026-10-01: Rushmore'da duzenleme gecisi bir kez bos dondu. Kamerasi
        # gorunebilecek bir kare, o gunun hic videosuz kalmasindan iyidir.
        print("UYARI: kamera silme gecisi basarisiz (%s), ham gorsel kullaniliyor" % hata)
        temiz = ham
    hedef.parent.mkdir(parents=True, exist_ok=True)
    hedef.write_bytes(requests.get(temiz, timeout=120).content)
    if hedef.stat().st_size == 0:
        raise IlkKareHatasi("indirilen gorsel bos: %s" % temiz)
    return temiz


def hazirla(slug: str, kok: Path | None = None) -> tuple[str, str]:
    """(url, kaynak) dondurur; kaynak 'onayli' ya da 'uretildi'."""
    kok = kok or KOK
    onayli = onayli_yol(slug, kok / "ilk_kare")
    if onayli is not None:
        return yukle(onayli), "onayli:%s" % onayli.name
    prompt_yolu = kok / "out" / slug / "ILK_KARE.txt"
    if not prompt_yolu.is_file():
        raise IlkKareHatasi("ILK_KARE.txt yok (build.py kostu mu?): %s" % prompt_yolu)
    prompt = prompt_yolu.read_text(encoding="utf-8").strip()
    return uret(prompt, kok / "out" / slug / "ilk_kare.png"), "uretildi"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--onayla", action="store_true",
                    help="uretilen gorseli ilk_kare/<slug>.jpg olarak depoya koy")
    args = ap.parse_args(argv)
    prompt_yolu = KOK / "out" / args.slug / "ILK_KARE.txt"
    if not prompt_yolu.is_file():
        print("ILK_KARE.txt yok, once: python build.py", file=sys.stderr)
        return 1
    hedef = KOK / "out" / args.slug / "ilk_kare.png"
    url = uret(prompt_yolu.read_text(encoding="utf-8").strip(), hedef)
    print("URL   :", url)
    print("dosya :", hedef)
    if args.onayla:
        ONAYLI_KLASOR.mkdir(exist_ok=True)
        onay = ONAYLI_KLASOR / (args.slug + ".jpg")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(hedef), "-q:v", "2",
                        str(onay)], check=True)
        print("onayli:", onay)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
