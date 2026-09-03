"""Korku kaydiragi videosunu AImagine kanalina yayinlar (YouTube + Instagram + TikTok).

Kullanim (Projeler/Youtube kokunden ya da her yerden):
    python AImagine-Fear/tools/yayinla.py <video.mp4> --caption-file <caption.txt> --title "..."
    python AImagine-Fear/tools/yayinla.py <video.mp4> --caption-file <c.txt> --dry

Neden publish_video degil de platform basina upload_to_platform:
publish_video() social_caption parametresini GECIRMIYOR, bu yuzden IG ve TikTok'ta
caption yerine baslik kullaniliyor ve 100 karaktere kirpiliyor. Etiketler kayboluyor.
Bkz. core/uploader.py:527-534 ile :384-392 karsilastirmasi.

AImagine-Fear seri motoruna kayitli DEGIL, yani published.json'a otomatik satir dusmez.
Bu yuzden mukerrer yayin korumasini ve kaydi bu script kendi tutar: yayin.jsonl.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent      # AImagine-Fear/
YT_KOK = KOK.parent                                # depo koku, hem Windows hem CI'da dogru
DEFTER = KOK / "yayin.jsonl"
LA = timezone(timedelta(hours=-7))  # PDT


def _yukleyici():
    sys.path.insert(0, str(YT_KOK))
    import os

    os.chdir(YT_KOK)  # core/env.py PROJECT_ROOT/.env yolundan okuyor
    from core.uploader import upload_to_platform
    from core.config import UPLOAD_USERS, CHANNEL_PLATFORMS

    return upload_to_platform, UPLOAD_USERS, CHANNEL_PLATFORMS


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def defter_oku() -> list[dict]:
    if not DEFTER.exists():
        return []
    return [json.loads(l) for l in DEFTER.read_text(encoding="utf-8").splitlines() if l.strip()]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("video")
    p.add_argument("--caption-file", required=True)
    p.add_argument("--title", default="")
    p.add_argument("--channel", default="aimagine")
    p.add_argument("--dry", action="store_true", help="gonderme, sadece ne gidecegini yaz")
    p.add_argument("--allow-same-day", action="store_true",
                   help="ayni gune ikinci videoyu bilerek koy")
    p.add_argument("--skip-if-published", action="store_true",
                   help="video zaten yayinlandiysa HATA verme, 0 ile cik. "
                        "Tekrarlayan cron'lar icin: kapinin calismasi hata degildir.")
    args = p.parse_args()

    video = Path(args.video).resolve()
    if not video.exists():
        sys.exit("Video yok: %s" % video)
    cap_path = Path(args.caption_file).resolve()
    if not cap_path.exists():
        sys.exit("Caption yok: %s" % cap_path)
    caption = cap_path.read_text(encoding="utf-8").strip()
    title = args.title or caption.splitlines()[0][:95]

    parmak = sha(video)
    gecmis = defter_oku()
    for k in gecmis:
        if k.get("sha") == parmak:
            mesaj = "BU VIDEO ZATEN YAYINLANDI (%s). Mukerrer yayin engellendi." % k.get("ts")
            if args.skip_if_published:
                print(mesaj)
                print("--skip-if-published verildi, bu bir hata degil. Cikis 0.")
                return 0
            sys.exit(mesaj)

    simdi = datetime.now(LA)
    bugun = [k for k in gecmis if k.get("ts", "").startswith(simdi.strftime("%Y-%m-%d"))]
    if bugun and not args.allow_same_day:
        sys.exit("Bugun bu kanala zaten %d video kondu. Bilerek istiyorsan --allow-same-day ver."
                 % len(bugun))

    upload_to_platform, UPLOAD_USERS, CHANNEL_PLATFORMS = _yukleyici()
    kullanici = UPLOAD_USERS.get(args.channel)
    platformlar = CHANNEL_PLATFORMS.get(args.channel)
    if not kullanici or not platformlar:
        sys.exit("Kanal tanimsiz: %r. Tanimli olanlar: %s" % (args.channel, list(UPLOAD_USERS)))

    print("=" * 62)
    print("kanal      : %s  ->  Upload-Post profili %r" % (args.channel, kullanici))
    print("platformlar: %s" % ", ".join(platformlar))
    print("video      : %s (%.1f MB, sha %s)" % (video.name, video.stat().st_size / 1e6, parmak))
    print("baslik     : %s" % title)
    print("caption    : %d karakter, %d etiket" % (len(caption), caption.count("#")))
    print("-" * 62)
    print(caption)
    print("=" * 62)

    if args.dry:
        print("KURU KOSU. Hicbir sey gonderilmedi.")
        return 0

    sonuclar = {}
    for platform in platformlar:
        print("\n>> %s yukleniyor..." % platform.upper(), flush=True)
        try:
            r = upload_to_platform(
                video_path=video,
                title=title,
                description=caption,
                user=kullanici,
                platform=platform,
                social_caption=caption,
            )
        except Exception as e:
            r = {"hata": str(e)}
        sonuclar[platform] = r
        print("   sonuc: %s" % json.dumps(r, ensure_ascii=False)[:300])

    kayit = {
        "ts": simdi.strftime("%Y-%m-%d %H:%M") + " PDT",
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "video": str(video),
        "sha": parmak,
        "channel": args.channel,
        "title": title,
        "results": sonuclar,
    }
    with DEFTER.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(kayit, ensure_ascii=False) + "\n")
    print("\ndeftere yazildi: %s" % DEFTER)

    basarili = sum(1 for v in sonuclar.values() if v and "hata" not in v)
    print("ozet: %d/%d platform" % (basarili, len(platformlar)))
    return 0 if basarili else 1


if __name__ == "__main__":
    raise SystemExit(main())
