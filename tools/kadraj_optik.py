"""Kadrajin OPTIK imzasini olc: keskinlik kareye yayilmis mi, bir yerde mi toplanmis.

Fotografik goruntude keskinlik dardir (sig alan derinligi + hareket bulanikligi);
sentetik render'da kare bastan basa keskindir. 20 Eylul 2026 olcumu:

    referans reel DcVUi14TlS7   %12,5 / %8,8
    referans reel DcYBduSzf-A   %4,0  / %9,3
    ep09 wuuu02K2hPc            %41,5 / %42,4
    ep11 4cdvxPh_mE8            %41,6 / %34,4
    ep13 n0bBTtIWt7k            %32,4 / %33,5

Ortusme YOK. Sikistirma elendi: ep09 referanslarin bit hizina indirilip yeniden
olculdu, %42,6 cikti, yani fark kodlamadan DEGIL optikten geliyor.

Bu bir KAPI DEGILDIR, olcerdir. Esigi kapiya cevirmeden once kendi bolumlerimizde
yeni kadrajla olcum biriktir: yanlis ret kredi yakar (seri dersi, RF-ISSUES).

Kullanim:
    py -X utf8 tools/kadraj_optik.py video.mp4 [video2.mp4 ...] [--an 0 3 6]
"""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

KESKIN_ESIK = 100.0
# Referanslarin tavani %12,5, bizim tabanimiz %32,4. Arasi genis; 18 bilerek
# referans tarafina yakin secildi ama KAPI DEGIL, yalniz raporda isaretlenir.
HEDEF_UST_SINIR = 18.0


def _yerel_ayrinti(gray: np.ndarray, k: int = 5) -> np.ndarray:
    g = gray.astype(np.float32)
    lap = (-4 * g + np.roll(g, 1, 0) + np.roll(g, -1, 0)
           + np.roll(g, 1, 1) + np.roll(g, -1, 1))
    kare = lap ** 2
    cs = np.pad(np.cumsum(np.cumsum(kare, 0), 1), ((1, 0), (1, 0)))
    H, W = kare.shape
    pad = k // 2
    y0 = np.clip(np.arange(H) - pad, 0, H)
    y1 = np.clip(np.arange(H) + pad + 1, 0, H)
    x0 = np.clip(np.arange(W) - pad, 0, W)
    x1 = np.clip(np.arange(W) + pad + 1, 0, W)
    A = cs[np.ix_(y1, x1)]
    B = cs[np.ix_(y0, x1)]
    C = cs[np.ix_(y1, x0)]
    D = cs[np.ix_(y0, x0)]
    return (A - B - C + D) / np.maximum(np.outer(y1 - y0, x1 - x0), 1)


def keskin_pay(kare_yolu: pathlib.Path) -> float:
    """Karenin yuzde kaci esigin uzerinde keskin."""
    gray = np.asarray(Image.open(kare_yolu).convert("L").resize((540, 960)))
    return float((_yerel_ayrinti(gray) > KESKIN_ESIK).mean() * 100.0)


def video_olc(video: pathlib.Path, anlar: list[float]) -> list[tuple[float, float]]:
    sonuc: list[tuple[float, float]] = []
    with tempfile.TemporaryDirectory(prefix="kadraj-optik-") as gecici:
        for an in anlar:
            hedef = pathlib.Path(gecici) / f"t{an}.jpg"
            islem = subprocess.run(
                ["ffmpeg", "-y", "-v", "quiet", "-ss", str(an), "-i", str(video),
                 "-frames:v", "1", str(hedef)],
                capture_output=True,
            )
            if islem.returncode != 0 or not hedef.exists():
                continue
            sonuc.append((an, keskin_pay(hedef)))
    return sonuc


def main(argv: list[str] | None = None) -> int:
    ayristirici = argparse.ArgumentParser(description="Kadrajin optik imzasini olc")
    ayristirici.add_argument("videolar", nargs="+")
    ayristirici.add_argument("--an", nargs="*", type=float, default=[0.0, 3.0, 6.0])
    args = ayristirici.parse_args(argv)

    print(f"{'video':44s} {'an':>6s} {'keskin%':>9s}")
    isaretli = 0
    for ham in args.videolar:
        video = pathlib.Path(ham)
        if not video.exists():
            print(f"{video.name[:42]:44s} {'-':>6s} {'DOSYA YOK':>9s}")
            continue
        for an, pay in video_olc(video, args.an):
            bayrak = "  <- yayilmis keskinlik" if pay > HEDEF_UST_SINIR else ""
            isaretli += 1 if pay > HEDEF_UST_SINIR else 0
            print(f"{video.name[:42]:44s} {an:6.1f} {pay:8.1f}%{bayrak}")
    print(f"\nOlcer, kapi degil. Esik {HEDEF_UST_SINIR:.0f}% ustu: {isaretli} kare.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
