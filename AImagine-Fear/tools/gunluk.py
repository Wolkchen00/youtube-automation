"""Gunluk korku kaydiragi kosusu: sirdaki sehri sec, uret, DENETLE, yayinla.

Kullanim:
    python tools/gunluk.py            # tam kosu
    python tools/gunluk.py --dry      # sadece sirdaki sehri ve plani yaz
    python tools/gunluk.py --sehir tokyo-skytree-mor-yagmur   # sirayi atla

Guvenlik kapilari (hepsi kosudan ONCE):
  1. Kredi tabani: bakiye MIN_KREDI altindaysa hic baslamaz.
  2. Ayni gun kilidi: bugun zaten yayin varsa durur.
  3. build --check: dogrulanmamis prompt uretime GITMEZ.
  4. Uretim sonrasi denetim: sure, cozunurluk, ses, kesme. Kalirsa YAYINLANMAZ.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent      # AImagine-Fear/
YT_KOK = KOK.parent                                # depo koku, hem Windows hem CI'da dogru
PY = sys.executable
LA = timezone(timedelta(hours=-7))
DEFTER = KOK / "yayin.jsonl"
MIN_KREDI = 700          # bir kosu 615 kredi; altina inersek hic baslama
MODEL = "bytedance/seedance-2"
SURE = 15
COZUNURLUK = "720p"

# Gunluk donusum sirasi. Elle yazilan iki rota da havuzda.
SIRA = [
    "vegas-strat-blue-rain-15",
    "tokyo-skytree-mor-yagmur",
    "newyork-empire-magenta-kar",
    "dubai-burj-altin",
    "toronto-cn-red-dusk",
    "paris-eyfel-beyaz-cise",
    "sanghay-inci-yesil-sis",
]


def log(msg: str) -> None:
    print("[%s] %s" % (datetime.now(LA).strftime("%H:%M:%S"), msg), flush=True)


def kosa(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def defter() -> list[dict]:
    if not DEFTER.exists():
        return []
    return [json.loads(l) for l in DEFTER.read_text(encoding="utf-8").splitlines() if l.strip()]


def kredi() -> float | None:
    """Anahtar cozumunu kie_uret ile PAYLAS, iki yerde ayri mantik olmasin."""
    import requests
    sys.path.insert(0, str(KOK / "tools"))
    import kie_uret

    try:
        anahtar = kie_uret.api_key()
    except SystemExit:
        return None
    r = requests.get("https://api.kie.ai/api/v1/chat/credit",
                     headers={"Authorization": "Bearer " + anahtar}, timeout=30)
    return (r.json() or {}).get("data") if r.status_code == 200 else None


def sirdaki(gecmis: list[dict]) -> str:
    kullanilmis = [k.get("slug") for k in gecmis if k.get("slug")]
    for s in SIRA:
        if s not in kullanilmis:
            return s
    # hepsi kullanildiysa en eski kullanilana don
    son = {}
    for i, k in enumerate(gecmis):
        if k.get("slug"):
            son[k["slug"]] = i
    return min(SIRA, key=lambda s: son.get(s, -1))


def denetle(video: Path) -> list[str]:
    """Yayina engel olan sorunlari dondur. Bos liste = temiz."""
    sorunlar = []
    r = kosa(["ffprobe", "-v", "error", "-show_entries", "format=duration",
              "-show_entries", "stream=codec_type,width,height",
              "-of", "default=noprint_wrappers=1", str(video)], KOK)
    alanlar = dict(re.findall(r"^(\w+)=(.+)$", r.stdout, re.M))
    sure = float(alanlar.get("duration", 0) or 0)
    if not (SURE - 1.5 <= sure <= SURE + 1.5):
        sorunlar.append("sure %.2f sn, beklenen ~%d" % (sure, SURE))
    if alanlar.get("width") != "720" or alanlar.get("height") != "1280":
        sorunlar.append("cozunurluk %sx%s, beklenen 720x1280" % (alanlar.get("width"), alanlar.get("height")))
    if "audio" not in r.stdout:
        sorunlar.append("ses akisi YOK")
    if video.stat().st_size < 3_000_000:
        sorunlar.append("dosya cok kucuk: %.1f MB" % (video.stat().st_size / 1e6))
    return sorunlar


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dry", action="store_true")
    p.add_argument("--sehir")
    p.add_argument("--allow-same-day", action="store_true")
    a = p.parse_args()

    gecmis = defter()
    slug = a.sehir or sirdaki(gecmis)
    bugun = datetime.now(LA).strftime("%Y-%m-%d")
    bugunku = [k for k in gecmis if k.get("ts", "").startswith(bugun)]

    log("sirdaki sehir : %s" % slug)
    log("bugunku yayin : %d" % len(bugunku))

    if bugunku and not a.allow_same_day:
        log("DUR: bugun zaten yayin var. --allow-same-day ile zorlanabilir.")
        return 0

    k = kredi()
    log("kredi         : %s (= $%.2f)" % (k, (k or 0) * 0.005))
    if k is None:
        log("DUR: kredi okunamadi.")
        return 1
    if k < MIN_KREDI:
        log("DUR: kredi %s < taban %s. Yukleme yapilmali." % (k, MIN_KREDI))
        return 1

    log("build --check calisiyor")
    r = kosa([PY, "build.py", "--check"], KOK)
    if r.returncode != 0:
        log("DUR: build dogrulamasi patladi:\n" + (r.stdout + r.stderr)[:1500])
        return 1
    log("build temiz")

    if a.dry:
        log("KURU KOSU. Uretim ve yayin yapilmadi.")
        return 0

    log("uretim basliyor: %s, %d sn, %s" % (MODEL, SURE, COZUNURLUK))
    r = kosa([PY, "tools/kie_uret.py", slug, "--model", MODEL, "--n-frames", str(SURE),
              "--resolution", COZUNURLUK, "--tag", "gunluk", "--max-wait", "1500"], KOK)
    print(r.stdout[-2500:])
    if r.returncode != 0:
        log("DUR: uretim basarisiz:\n" + (r.stderr or "")[-1200:])
        return 1

    videolar = sorted((KOK / "out" / slug / "video").glob("*_gunluk_*.mp4"),
                      key=lambda f: f.stat().st_mtime)
    if not videolar:
        log("DUR: uretilen video bulunamadi.")
        return 1
    video = videolar[-1]
    log("video: %s (%.1f MB)" % (video.name, video.stat().st_size / 1e6))

    sorunlar = denetle(video)
    if sorunlar:
        log("DUR: denetim kaldi, YAYINLANMADI. Sorunlar: " + "; ".join(sorunlar))
        return 1
    log("denetim temiz")

    caption = KOK / "out" / slug / "CAPTION.txt"
    if not caption.exists():
        log("DUR: CAPTION.txt yok: %s" % caption)
        return 1

    baslik = caption.read_text(encoding="utf-8").strip().splitlines()[0][:95]
    log("yayinlaniyor")
    cmd = [PY, "-X", "utf8", str(KOK / "tools" / "yayinla.py"), str(video),
           "--caption-file", str(caption), "--title", baslik]
    if a.allow_same_day:
        cmd.append("--allow-same-day")
    r = kosa(cmd, YT_KOK)
    print(r.stdout[-2500:])
    if r.returncode != 0:
        log("YAYIN BASARISIZ:\n" + (r.stderr or "")[-1200:])
        return 1

    # slug'i deftere isle ki donusum ilerlesin
    kayitlar = DEFTER.read_text(encoding="utf-8").splitlines()
    if kayitlar:
        son = json.loads(kayitlar[-1])
        son["slug"] = slug
        kayitlar[-1] = json.dumps(son, ensure_ascii=False)
        DEFTER.write_text("\n".join(kayitlar) + "\n", encoding="utf-8", newline="\n")
    log("BITTI: %s yayinlandi" % slug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
