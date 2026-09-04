"""last_run.json'i GERCEK yayin kanitindan yaz, adimin cikis kodundan degil.

Neden var: `last_run.json` panoyu ve Akilli_Watchdog'u besleyen dosya. Eski hali
yalnizca `steps.produce.outcome`'a bakiyordu, yani "adim patlamadi" = "success".
2026-09-03T19:26'da event-horizon icin `{"outcome":"success"}` yazildi; o kosuda
SIFIR video uretildi ve Galactic dort gundur sessizdi. Yesil isik yalan soyledi.

Bu betik outcome'u su siraya gore turetir:
  1. adim basarisiz  -> "failure"
  2. adim basarili AMA bu kosuda dogrulanmis YouTube yayini YOK -> "no_video"
  3. adim basarili VE bu kosuda dogrulanmis YouTube yayini VAR  -> "success"

"Bu kosuda" sarti onemli: eski bir yayin kaydi bugunku sessizligi ORTMEMELI.
Bu yuzden kanit `--since` damgasindan sonra olmak zorundadir.

Instagram veya TikTok'un tek basina basarili olmasi YETMEZ: dort kanal da
YouTube kanalidir, olculen sey YouTube yayinidir.

Kullanim (seri hatti):
    python scripts/kosu_sonucu_yaz.py --out <seri>/last_run.json \
        --run-id 123 --raw-outcome success --since 2026-09-04T20:00:00Z \
        --published-json <seri>/published.json

Kullanim (fear-slide hatti):
    python scripts/kosu_sonucu_yaz.py --out AImagine-Fear/last_run.json \
        --run-id 123 --raw-outcome success --since 2026-09-04T20:00:00Z \
        --yayin-jsonl AImagine-Fear/yayin.jsonl
"""
from __future__ import annotations

import argparse
import datetime
import io
import json
import pathlib
import sys


def _zaman(deger) -> datetime.datetime | None:
    """ISO damgasini UTC'ye cevir; okunamazsa None."""
    if not isinstance(deger, str) or not deger.strip():
        return None
    metin = deger.strip().replace("Z", "+00:00")
    try:
        d = datetime.datetime.fromisoformat(metin)
    except ValueError:
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=datetime.timezone.utc)
    return d.astimezone(datetime.timezone.utc)


def _youtube_id(results) -> str | None:
    """Hem seri hem fear-slide bicimlerinden YouTube kimligini cikar."""
    if not isinstance(results, dict):
        return None
    yt = results.get("youtube")
    if isinstance(yt, str) and yt.strip():
        return yt.strip()
    if isinstance(yt, dict):
        if yt.get("success") is False:
            return None
        ic = yt.get("results")
        if isinstance(ic, dict):
            ic_yt = ic.get("youtube")
            if isinstance(ic_yt, dict):
                pid = ic_yt.get("post_id")
                if isinstance(pid, str) and pid.strip():
                    return pid.strip()
            if isinstance(ic_yt, str) and ic_yt.strip():
                return ic_yt.strip()
        pid = yt.get("post_id")
        if isinstance(pid, str) and pid.strip():
            return pid.strip()
        if yt.get("success") is True:
            return "onaylandi"
    return None


def _published_json_kaniti(path: pathlib.Path, since):
    if not path.exists():
        return None
    try:
        kayitlar = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(kayitlar, list):
        return None
    en_iyi = None
    for k in kayitlar:
        if not isinstance(k, dict):
            continue
        ts = _zaman(k.get("ts") or k.get("published_at"))
        if ts is None or (since is not None and ts < since):
            continue
        vid = _youtube_id(k.get("results"))
        if not vid:
            continue
        if en_iyi is None or ts > en_iyi["ts"]:
            en_iyi = {"ts": ts, "part": k.get("part"), "youtube_id": vid}
    return en_iyi


def _yayin_jsonl_kaniti(path: pathlib.Path, since):
    if not path.exists():
        return None
    en_iyi = None
    for satir in io.open(path, encoding="utf-8"):
        satir = satir.strip()
        if not satir:
            continue
        try:
            k = json.loads(satir)
        except Exception:
            continue
        ts = _zaman(k.get("ts_utc"))
        if ts is None or (since is not None and ts < since):
            continue
        vid = _youtube_id(k.get("results"))
        if not vid:
            continue
        if en_iyi is None or ts > en_iyi["ts"]:
            en_iyi = {"ts": ts, "part": None, "youtube_id": vid}
    return en_iyi


def sonucu_hesapla(raw_outcome: str, kanit) -> str:
    if str(raw_outcome).strip().lower() != "success":
        return "failure"
    return "success" if kanit else "no_video"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="kosu_sonucu_yaz")
    p.add_argument("--out", required=True)
    p.add_argument("--run-id", required=True)
    p.add_argument("--raw-outcome", required=True)
    p.add_argument("--since", default=None,
                   help="kosu baslangici (ISO). Daha eski kanit SAYILMAZ.")
    p.add_argument("--published-json", default=None)
    p.add_argument("--yayin-jsonl", default=None)
    a = p.parse_args(argv)

    since = _zaman(a.since) if a.since else None
    kanit = None
    if a.published_json:
        kanit = _published_json_kaniti(pathlib.Path(a.published_json), since)
    if kanit is None and a.yayin_jsonl:
        kanit = _yayin_jsonl_kaniti(pathlib.Path(a.yayin_jsonl), since)

    outcome = sonucu_hesapla(a.raw_outcome, kanit)
    kayit = {
        "ts": datetime.datetime.now(datetime.timezone.utc)
        .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "outcome": outcome,
        "raw_outcome": a.raw_outcome,
        "run_id": a.run_id,
        "published_part": kanit["part"] if kanit else None,
        "published_at": kanit["ts"].strftime("%Y-%m-%dT%H:%M:%SZ") if kanit else None,
        "youtube_id": kanit["youtube_id"] if kanit else None,
    }
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(kayit, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(kayit, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
