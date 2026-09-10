"""Gunluk korku kaydiragi: profil kapisi, master, denetim ve yayin."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from fractions import Fraction
from pathlib import Path


KOK = Path(__file__).resolve().parent.parent
YT_KOK = KOK.parent
if str(KOK) not in sys.path:
    sys.path.insert(0, str(KOK))
if str(YT_KOK) not in sys.path:
    sys.path.insert(0, str(YT_KOK))

from profil import (  # noqa: E402
    PROFILLER,
    VARSAYILAN_PROFIL,
    YETENEK_MATRISI,
    matris_anahtari,
    profil_hash,
    uretim_kaydi_bul,
)


PY = sys.executable
LA = timezone(timedelta(hours=-7))
DEFTER = KOK / "yayin.jsonl"
ONAY_DOSYASI = KOK / "profil_onay.json"
MIN_KREDI = 700
MODEL = "bytedance/seedance-2"
SURE = 15  # Rota DURATION okuma Rock 2'nin kapsami.

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
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def defter() -> list[dict]:
    if not DEFTER.exists():
        return []
    return [
        json.loads(satir)
        for satir in DEFTER.read_text(encoding="utf-8").splitlines()
        if satir.strip()
    ]


def kredi() -> float | None:
    """Anahtar cozumunu kie_uret ile paylas."""
    import requests

    sys.path.insert(0, str(KOK / "tools"))
    import kie_uret

    try:
        anahtar = kie_uret.api_key()
    except SystemExit:
        return None
    yanit = requests.get(
        "https://api.kie.ai/api/v1/chat/credit",
        headers={"Authorization": "Bearer " + anahtar},
        timeout=30,
    )
    return (yanit.json() or {}).get("data") if yanit.status_code == 200 else None


def sirdaki(gecmis: list[dict]) -> str:
    kullanilmis = [kayit.get("slug") for kayit in gecmis if kayit.get("slug")]
    for slug in SIRA:
        if slug not in kullanilmis:
            return slug
    son: dict[str, int] = {}
    for sira, kayit in enumerate(gecmis):
        if kayit.get("slug"):
            son[kayit["slug"]] = sira
    return min(SIRA, key=lambda slug: son.get(slug, -1))


def sha256_dosya(path: Path) -> str:
    ozet = hashlib.sha256()
    with path.open("rb") as handle:
        for parca in iter(lambda: handle.read(1 << 20), b""):
            ozet.update(parca)
    return ozet.hexdigest()


def uretim_komutu(slug: str, sure: int, profil: dict) -> list[str]:
    """Secili profil ile Kie sarmalayicisinin tam argv'sini kur."""
    return [
        PY,
        "tools/kie_uret.py",
        slug,
        "--model",
        MODEL,
        "--n-frames",
        str(sure),
        "--resolution",
        str(profil["cozunurluk"]),
        "--tag",
        "gunluk",
        "--max-wait",
        "1500",
    ]


def _fps(r_frame_rate: object) -> float | None:
    try:
        return float(Fraction(str(r_frame_rate)))
    except (ValueError, ZeroDivisionError):
        return None


def akis_olcumleri(probe_json: dict) -> dict:
    """ffprobe JSON'undan video akisini acikca secerek olcumleri cikar."""
    akislar = probe_json.get("streams") or []
    video = next(
        (akis for akis in akislar if akis.get("codec_type") == "video"), None
    )
    bicim = probe_json.get("format") or {}
    try:
        sure = float(bicim.get("duration"))
    except (TypeError, ValueError):
        sure = None
    return {
        "genislik": video.get("width") if video else None,
        "yukseklik": video.get("height") if video else None,
        "fps": _fps(video.get("r_frame_rate")) if video else None,
        "sure": sure,
        "video_var": video is not None,
        "ses_var": any(akis.get("codec_type") == "audio" for akis in akislar),
    }


def denetle_akislar(
    probe_json: dict,
    dosya_boyutu: int,
    beklenen_sure: int | float,
    istenen_profil: dict,
) -> list[str]:
    """Saf teknik kapi. Bos liste temiz teslim demektir."""
    sorunlar: list[str] = []
    olculen = akis_olcumleri(probe_json)
    if not olculen["video_var"]:
        sorunlar.append("video akisi YOK")
    sure = olculen["sure"]
    tolerans = float(istenen_profil["sure_tolerans"])
    if sure is None or not (beklenen_sure - tolerans <= sure <= beklenen_sure + tolerans):
        gosterim = "YOK" if sure is None else "%.2f" % sure
        sorunlar.append("sure %s sn, beklenen ~%s" % (gosterim, beklenen_sure))

    genislik = olculen["genislik"]
    yukseklik = olculen["yukseklik"]
    beklenen_genislik = istenen_profil["genislik"]
    beklenen_yukseklik = istenen_profil["yukseklik"]
    if (genislik, yukseklik) != (beklenen_genislik, beklenen_yukseklik):
        gelen = "%sx%s" % (genislik, yukseklik)
        if (
            istenen_profil["cozunurluk"] == "1080p"
            and (genislik, yukseklik) == (720, 1280)
        ):
            sorunlar.append("istendi 1080p, geldi 720x1280 - model sessizce dusurdu")
        else:
            sorunlar.append(
                "cozunurluk %s, beklenen %dx%d"
                % (gelen, beklenen_genislik, beklenen_yukseklik)
            )

    fps = olculen["fps"]
    beklenen_fps = float(istenen_profil["beklenen_fps"])
    if fps is None or abs(fps - beklenen_fps) > float(istenen_profil["fps_tolerans"]):
        gosterim = "YOK" if fps is None else "%.3f" % fps
        sorunlar.append("fps %s, beklenen ~%g" % (gosterim, beklenen_fps))
    if not olculen["ses_var"]:
        sorunlar.append("ses akisi YOK")
    if dosya_boyutu < int(istenen_profil["min_bayt"]):
        sorunlar.append("dosya cok kucuk: %.1f MB" % (dosya_boyutu / 1e6))
    return sorunlar


def ffprobe_json(video: Path) -> tuple[dict | None, str | None]:
    sonuc = kosa(
        [
            "ffprobe", "-v", "error", "-print_format", "json",
            "-show_streams", "-show_format", str(video),
        ],
        KOK,
    )
    if sonuc.returncode != 0:
        return None, "ffprobe basarisiz: " + (sonuc.stderr or "").strip()
    try:
        veri = json.loads(sonuc.stdout)
    except (json.JSONDecodeError, TypeError) as error:
        return None, "ffprobe bozuk JSON: %s" % error
    if not isinstance(veri, dict):
        return None, "ffprobe JSON koku nesne degil"
    return veri, None


def ses_denetle(master: Path) -> list[str]:
    sidecar = master.with_suffix(".audio_master.json")
    try:
        veri = json.loads(sidecar.read_text(encoding="utf-8"))
        son = veri["delivery_limiter"]["attempts"][-1]
        lufs = float(son["integrated_lufs"])
        tepe = float(son["true_peak_dbtp"])
    except (OSError, json.JSONDecodeError, KeyError, IndexError, TypeError, ValueError):
        return ["audio master sidecar okunamadi: %s" % sidecar]
    sorunlar = []
    if abs(lufs - (-14.0)) > 1.0:
        sorunlar.append("ses I %.1f LUFS, beklenen -14.0 +/- 1.0" % lufs)
    if tepe > -1.0:
        sorunlar.append("ses TP %.1f dBTP, tavan -1.0" % tepe)
    return sorunlar


def denetle(
    video: Path,
    beklenen_sure: int | float = SURE,
    istenen_profil: dict | None = None,
) -> tuple[list[str], dict]:
    """Son master dosyasini teknik, loudness ve yukleme boyutu icin denetle."""
    profil = istenen_profil or PROFILLER[VARSAYILAN_PROFIL]
    probe, hata = ffprobe_json(video)
    if hata:
        return [hata], {"genislik": None, "yukseklik": None, "fps": None, "sure": None}
    olculen = akis_olcumleri(probe)
    sorunlar = denetle_akislar(probe, video.stat().st_size, beklenen_sure, profil)
    sorunlar.extend(ses_denetle(video))

    from core import uploader

    boyut_mb = video.stat().st_size / (1024 * 1024)
    if boyut_mb > uploader.MAX_UPLOAD_MB:
        sorunlar.append(
            "master %.1f MB, yukleme tavani %s MB; denetimsiz delivery transcode yasak"
            % (boyut_mb, uploader.MAX_UPLOAD_MB)
        )
    return sorunlar, {
        "genislik": olculen["genislik"],
        "yukseklik": olculen["yukseklik"],
        "fps": olculen["fps"],
        "sure": olculen["sure"],
    }


def _onay_oku() -> tuple[dict | None, str]:
    try:
        veri = json.loads(ONAY_DOSYASI.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "profil_onay.json yok"
    except (OSError, json.JSONDecodeError, TypeError):
        return None, "profil_onay.json bozuk"
    if not isinstance(veri, dict):
        return None, "profil_onay.json bozuk"
    return veri, ""


def _onay_kombinasyonu(onay: dict) -> tuple | None:
    try:
        return matris_anahtari(onay["model"], onay["sure"], onay["cozunurluk"], onay["fps"])
    except (KeyError, TypeError, ValueError):
        return None


def yayin_izni(profil_adi: str) -> tuple[bool, str]:
    profil = PROFILLER[profil_adi]
    anahtar = matris_anahtari(MODEL, SURE, profil["cozunurluk"], profil["beklenen_fps"])
    durum = YETENEK_MATRISI.get(anahtar)
    if durum == "dogrulandi":
        return True, durum
    if durum != "kanarya":
        return False, "matriste yok"
    onay, hata = _onay_oku()
    if onay is None:
        return False, "kanarya; " + hata
    if _onay_kombinasyonu(onay) != anahtar:
        return False, "kanarya; kalici onay kombinasyonu farkli"
    if onay.get("profil_hash") != profil_hash():
        return False, "kanarya; profil.py hash'i degismis"
    if not isinstance(onay.get("master_sha"), str) or not onay["master_sha"]:
        return False, "kanarya; onay master SHA'si yok"
    return True, "dogrulandi (kalici onay)"


def uretim_kaydi_yaz(slug: str, kayit: dict) -> Path:
    hedef = KOK / "out" / slug / "uretim" / (kayit["master_sha"] + ".json")
    if hedef.exists():
        return hedef
    hedef.parent.mkdir(parents=True, exist_ok=True)
    with hedef.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(kayit, ensure_ascii=False, indent=2) + "\n")
    return hedef


def onayla(master: Path) -> int:
    if not master.exists():
        log("DUR: master yok: %s" % master)
        return 1
    master_sha = sha256_dosya(master)
    kayit = uretim_kaydi_bul(master_sha, KOK)
    if kayit is None:
        log("DUR: bu master icin uretim kaydi yok veya bozuk")
        return 1
    if kayit.get("denetim_sonucu") != "basarili":
        log("DUR: uretim kaydinin denetimi basarili degil")
        return 1
    if kayit.get("model") != MODEL:
        log("DUR: uretim kaydindaki model farkli")
        return 1
    if kayit.get("master_sha") != master_sha:
        log("DUR: master SHA uretim kaydiyla uyusmuyor")
        return 1
    if kayit.get("profil_hash") != profil_hash():
        log("DUR: uretim kaydinin profil hash'i guncel profil.py ile uyusmuyor")
        return 1
    profil_adi = kayit.get("istenen_profil")
    if profil_adi not in PROFILLER:
        log("DUR: uretim kaydindaki profil bilinmiyor")
        return 1
    profil = PROFILLER[profil_adi]
    anahtar = matris_anahtari(
        MODEL, kayit.get("beklenen_sure"), profil["cozunurluk"], profil["beklenen_fps"]
    )
    if anahtar not in YETENEK_MATRISI:
        log("DUR: uretim kombinasyonu yetenek matrisinde yok")
        return 1
    onay = {
        "model": anahtar[0], "sure": anahtar[1], "cozunurluk": anahtar[2],
        "fps": anahtar[3], "master_sha": master_sha, "profil_hash": profil_hash(),
    }
    ONAY_DOSYASI.write_text(
        json.dumps(onay, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n",
    )
    log("ONAYLANDI: %s artik dogrulandi" % (anahtar,))
    log("profil_onay.json dosyasini commit'leyin: %s" % ONAY_DOSYASI)
    return 0


def _yayin_komutu(master: Path, slug: str, allow_same_day: bool) -> list[str] | None:
    caption = KOK / "out" / slug / "CAPTION.txt"
    if not caption.exists():
        log("DUR: CAPTION.txt yok: %s" % caption)
        return None
    satirlar = caption.read_text(encoding="utf-8").strip().splitlines()
    if not satirlar:
        log("DUR: CAPTION.txt bos: %s" % caption)
        return None
    komut = [
        PY, "-X", "utf8", str(KOK / "tools" / "yayinla.py"), str(master),
        "--caption-file", str(caption), "--title", satirlar[0][:95],
    ]
    if allow_same_day:
        komut.append("--allow-same-day")
    return komut


def yayinla(master: Path, slug: str, allow_same_day: bool) -> int:
    komut = _yayin_komutu(master, slug, allow_same_day)
    if komut is None:
        return 1
    log("yayinlaniyor")
    sonuc = kosa(komut, YT_KOK)
    print(sonuc.stdout[-2500:])
    if sonuc.returncode != 0:
        log("YAYIN BASARISIZ:\n" + (sonuc.stderr or "")[-1200:])
        return 1
    kayitlar = DEFTER.read_text(encoding="utf-8").splitlines()
    if kayitlar:
        son = json.loads(kayitlar[-1])
        son["slug"] = slug
        kayitlar[-1] = json.dumps(son, ensure_ascii=False)
        DEFTER.write_text("\n".join(kayitlar) + "\n", encoding="utf-8", newline="\n")
    log("BITTI: %s yayinlandi" % slug)
    return 0


def yayinla_mevcut(master: Path, allow_same_day: bool) -> int:
    if not master.exists():
        log("DUR: master yok: %s" % master)
        return 1
    master_sha = sha256_dosya(master)
    kayit = uretim_kaydi_bul(master_sha, KOK)
    if kayit is None or kayit.get("denetim_sonucu") != "basarili":
        log("DUR: master'in basarili uretim kaydi yok")
        return 1
    onay, hata = _onay_oku()
    if onay is None:
        log("DUR: %s" % hata)
        return 1
    if onay.get("master_sha") != master_sha:
        log("DUR: --yayinla-mevcut master SHA'si profil onayiyla uyusmuyor")
        return 1
    if onay.get("profil_hash") != profil_hash():
        log("DUR: profil.py hash'i onaydan sonra degismis")
        return 1
    profil_adi = kayit.get("istenen_profil")
    if profil_adi not in PROFILLER:
        log("DUR: kayittaki profil bilinmiyor")
        return 1
    profil = PROFILLER[profil_adi]
    anahtar = matris_anahtari(
        kayit.get("model"), kayit.get("beklenen_sure"),
        profil["cozunurluk"], profil["beklenen_fps"],
    )
    if _onay_kombinasyonu(onay) != anahtar:
        log("DUR: onay kombinasyonu uretim kaydiyla uyusmuyor")
        return 1
    return yayinla(master, kayit["slug"], allow_same_day)


def _kontakt_uret(master: Path, master_sha: str, sure: float) -> Path:
    from tools import kontrol

    hedef = master.parent.parent / "kontakt" / (master_sha + ".png")
    hedef.parent.mkdir(parents=True, exist_ok=True)
    hedef.unlink(missing_ok=True)
    kontrol.contact_sheet(master, sure, hedef)
    return hedef


def _argumanlar(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    kip = parser.add_mutually_exclusive_group()
    kip.add_argument("--dry", action="store_true")
    kip.add_argument("--yayinlama", action="store_true")
    kip.add_argument("--onayla", type=Path, metavar="MASTER")
    kip.add_argument("--yayinla-mevcut", type=Path, metavar="MASTER")
    parser.add_argument("--profil", choices=tuple(PROFILLER), default=VARSAYILAN_PROFIL)
    parser.add_argument("--sehir")
    parser.add_argument("--allow-same-day", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _argumanlar(argv)
    if args.onayla is not None:
        return onayla(args.onayla.resolve())
    if args.yayinla_mevcut is not None:
        return yayinla_mevcut(args.yayinla_mevcut.resolve(), args.allow_same_day)

    gecmis = defter()
    slug = args.sehir or sirdaki(gecmis)
    profil = PROFILLER[args.profil]
    anahtar = matris_anahtari(MODEL, SURE, profil["cozunurluk"], profil["beklenen_fps"])
    ham_durum = YETENEK_MATRISI.get(anahtar, "matriste yok")

    if args.dry:
        print("sirdaki slug : %s" % slug)
        print("sure         : %s" % SURE)
        print(
            "profil       : %s (%dx%d, %s fps)"
            % (args.profil, profil["genislik"], profil["yukseklik"], profil["beklenen_fps"])
        )
        print("matris       : %s" % ham_durum)
        print("KURU KOSU. Uretim ve yayin yapilmadi.")
        return 0

    log("sirdaki sehir : %s" % slug)
    log("sure          : %s" % SURE)
    log("profil        : %s" % args.profil)
    log("matris        : %s" % ham_durum)
    izinli, izin_durumu = yayin_izni(args.profil)
    if not args.yayinlama and not izinli:
        log(
            "DUR: kombinasyon yayinlanamaz (%s). Kanarya uretimi icin --yayinlama kullanin."
            % izin_durumu
        )
        return 1

    bugun = datetime.now(LA).strftime("%Y-%m-%d")
    bugunku = [kayit for kayit in gecmis if kayit.get("ts", "").startswith(bugun)]
    log("bugunku yayin : %d" % len(bugunku))
    if bugunku and not args.allow_same_day and not args.yayinlama:
        log("DUR: bugun zaten yayin var. --allow-same-day ile zorlanabilir.")
        return 0

    log("build --check calisiyor")
    sonuc = kosa([PY, "build.py", "--check", "--profil", args.profil], KOK)
    if sonuc.returncode != 0:
        log("DUR: build dogrulamasi patladi:\n" + (sonuc.stdout + sonuc.stderr)[:1500])
        return 1
    caption = KOK / "out" / slug / "CAPTION.txt"
    if not caption.exists() or not caption.read_text(encoding="utf-8").strip():
        log("DUR: CAPTION.txt yok veya bos: %s" % caption)
        return 1
    log("build temiz")

    bakiye = kredi()
    log("kredi         : %s (= $%.2f)" % (bakiye, (bakiye or 0) * 0.005))
    if bakiye is None:
        log("DUR: kredi okunamadi.")
        return 1
    if bakiye < MIN_KREDI:
        log("DUR: kredi %s < taban %s. Yukleme yapilmali." % (bakiye, MIN_KREDI))
        return 1

    log("uretim basliyor: %s, %d sn, %s" % (MODEL, SURE, profil["cozunurluk"]))
    sonuc = kosa(uretim_komutu(slug, SURE, profil), KOK)
    print(sonuc.stdout[-2500:])
    if sonuc.returncode != 0:
        log("DUR: uretim basarisiz:\n" + (sonuc.stderr or "")[-1200:])
        return 1

    videolar = sorted(
        (KOK / "out" / slug / "video").glob("*_gunluk_*.mp4"),
        key=lambda path: path.stat().st_mtime,
    )
    if not videolar:
        log("DUR: uretilen video bulunamadi.")
        return 1
    ham = videolar[-1]
    master = KOK / "out" / slug / "master" / (ham.stem + "_master.mp4")
    log("ham video: %s (%.1f MB)" % (ham.name, ham.stat().st_size / 1e6))

    try:
        from core.ffmpeg_tools import master_audio

        master_audio(ham, master, target_i=-14.0, target_tp=-1.0)
    except Exception as error:
        log("DUR: ses master basarisiz: %s" % error)
        return 1
    master_sha = sha256_dosya(master)
    sorunlar, olculen = denetle(master, SURE, profil)
    kayit = {
        "sema_surumu": 1,
        "model": MODEL,
        "istenen_profil": args.profil,
        "profil_hash": profil_hash(),
        "slug": slug,
        "beklenen_sure": SURE,
        "olculen": olculen,
        "denetim_sonucu": "basarili" if not sorunlar else "basarisiz",
        "master_sha": master_sha,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    kayit_yolu = uretim_kaydi_yaz(slug, kayit)
    log("uretim kaydi : %s" % kayit_yolu)
    if sorunlar:
        log("DUR: denetim kaldi, YAYINLANMADI. Sorunlar: " + "; ".join(sorunlar))
        return 1
    log("denetim temiz: %s" % master)

    if args.yayinlama:
        kontakt = _kontakt_uret(master, master_sha, float(olculen["sure"]))
        if not kontakt.exists() or kontakt.stat().st_size == 0:
            log("DUR: kontakt sayfasi olusmadi: %s" % kontakt)
            return 1
        log("master        : %s" % master)
        log("kontakt       : %s" % kontakt)
        log("YAYINLANMADI: gozle kontrolden sonra --onayla %s" % master)
        return 0

    return yayinla(master, slug, args.allow_same_day)


if __name__ == "__main__":
    raise SystemExit(main())
