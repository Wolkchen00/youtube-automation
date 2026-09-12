#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Referans videodan URETIME HAZIR prompt cikarir (tersine muhendislik).

NE YAPAR, NE YAPMAZ , once bunu oku:

Bir videonun URETILDIGI PROMPT dosyada YOKTUR. Olculdu: @earthimpacts25 reel'inin
mp4'unde tek metadata `encoder=Lavf62.3.100` ve `VPC Coding`, yani Instagram'in
kendi yeniden kodlamasi. Uretici modelin adi, prompt'u, seed'i, surumu hicbir yerde
gecmiyor. Yani "orijinal prompt'u cikarmak" MUMKUN DEGIL, kimse icin degil.

Bu arac bunun yerine sunu yapar: kareleri ve olculen anatomiyi Gemini vision'a
verir ve ayni SONUCU ureten YENI bir prompt yazdirir. Cikti bizim bible'imizin
dilinde ve kendi doktrinimize uygundur, o videonun kopyasi degildir.

Kullanim:
    python tools/tersine_prompt.py <video_url_veya_dosya> [...] \
        [--seri one-variable] [--kare 6] [--cikti out.json] [--plan-yaz 6]

    --seri      cikti prompt'u bu serinin art_style + shot_plan diline yazilir
    --kare      Gemini'ye gonderilecek kare sayisi (varsayilan 6)
    --cikti     JSON rapor yolu
    --plan-yaz  verilen bolum numarasindan baslayarak plans/partNN.json yazar

Gerekenler: yt-dlp (URL icin), ffmpeg/ffprobe, GEMINI_API_KEY.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

MODEL = "gemini-2.5-flash"
MODEL_YEDEK = "gemini-flash-latest"


# ─── Olcum (ffmpeg) ───────────────────────────────────────────────────────────

def _kos(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=300)


def indir(hedef: str, klasor: Path) -> Path:
    """URL ise indir, dosyaysa oldugu gibi dondur."""
    if not hedef.lower().startswith(("http://", "https://")):
        p = Path(hedef)
        if not p.exists():
            raise SystemExit(f"dosya yok: {hedef}")
        return p
    cikti = klasor / "kaynak.%(ext)s"
    r = _kos([sys.executable, "-m", "yt_dlp", "--no-warnings", "-f", "bv*+ba/b",
              "-o", str(cikti), hedef])
    bulunan = sorted(klasor.glob("kaynak.*"))
    if not bulunan:
        raise SystemExit(f"indirilemedi: {hedef}\n{r.stderr[-500:]}")
    return bulunan[0]


def olc(video: Path) -> dict:
    """Sure, fps, cozunurluk, kesme zamanlari, LUFS/TP/LRA ve saniyelik ses egrisi."""
    r = _kos(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(video)])
    meta = json.loads(r.stdout or "{}")
    v = next((s for s in meta.get("streams", []) if s.get("codec_type") == "video"), {})
    sure = float(meta.get("format", {}).get("duration") or 0)
    fps_ham = str(v.get("r_frame_rate") or "0/1")
    try:
        pay, payda = fps_ham.split("/")
        fps = round(float(pay) / float(payda), 2)
    except (ValueError, ZeroDivisionError):
        fps = None

    # Sahne kesmeleri
    r = _kos(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video),
              "-filter:v", "select='gt(scene,0.3)',showinfo", "-f", "null", "-"])
    kesmeler = [round(float(m), 2) for m in re.findall(r"pts_time:([0-9.]+)", r.stderr)]

    # EBU R128
    r = _kos(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video),
              "-af", "ebur128=peak=true", "-f", "null", "-"])
    def _son(pat):
        bulgular = re.findall(pat, r.stderr)
        try:
            return float(bulgular[-1])
        except (IndexError, ValueError):
            return None
    lufs = _son(r"I:\s*(-?[\d.]+)\s*LUFS")
    lra = _son(r"LRA:\s*(-?[\d.]+)\s*LU")
    tp = _son(r"Peak:\s*(-?[\d.]+)\s*dBFS")

    # Saniyelik ses egrisi , "sessizlik sonra carpma" sekli buradan okunur
    egri = []
    t = 0.0
    while t < sure - 0.05 and t < 120:
        rr = _kos(["ffmpeg", "-hide_banner", "-nostats", "-ss", f"{t}", "-t", "1",
                   "-i", str(video), "-af", "volumedetect", "-f", "null", "-"])
        m = re.search(r"mean_volume:\s*(-?[\d.]+)", rr.stderr)
        if m:
            egri.append({"sn": round(t, 1), "ort_db": float(m.group(1))})
        t += 1

    sicrama = None
    if len(egri) >= 2:
        farklar = [(egri[i]["ort_db"] - egri[i - 1]["ort_db"], egri[i]["sn"])
                   for i in range(1, len(egri))]
        en_buyuk = max(farklar, key=lambda x: x[0])
        sicrama = {"an_sn": en_buyuk[1], "artis_db": round(en_buyuk[0], 1)}

    return {
        "sure_sn": round(sure, 2),
        "cozunurluk": f"{v.get('width')}x{v.get('height')}",
        "fps": fps,
        "kesme_sayisi": len(kesmeler),
        "kesme_zamanlari": kesmeler,
        "en_uzun_plan_sn": round(max([kesmeler[0] if kesmeler else sure]
                                     + [kesmeler[i] - kesmeler[i - 1] for i in range(1, len(kesmeler))]
                                     + [sure - kesmeler[-1] if kesmeler else 0], default=sure), 2),
        "lufs": lufs,
        "true_peak_dbfs": tp,
        "lra": lra,
        "ses_egrisi": egri,
        "en_buyuk_ses_sicramasi": sicrama,
    }


def kareler(video: Path, klasor: Path, adet: int, sure: float) -> list[Path]:
    """Videoyu esit araliklarla ornekle. Ilk kare HER ZAMAN 0,0'dan alinir."""
    out = []
    for i in range(adet):
        t = 0.0 if i == 0 else round(sure * i / adet, 2)
        p = klasor / f"kare_{i:02d}.jpg"
        _kos(["ffmpeg", "-v", "error", "-ss", f"{t}", "-i", str(video),
              "-frames:v", "1", "-q:v", "3", str(p), "-y"])
        if p.exists() and p.stat().st_size > 0:
            out.append(p)
    return out


# ─── Gemini vision ────────────────────────────────────────────────────────────

SISTEM = """You are a reverse-engineering analyst for AI video production.

You receive ordered still frames from ONE short AI-generated video plus its measured
technical anatomy. The original generation prompt is NOT recoverable and you must not
pretend otherwise. Your job is to write a NEW prompt that would produce the same KIND
of result on a different engine.

Return STRICT JSON ONLY, exactly this shape:
{
  "gozlem": {
    "yer": "<the real place or subject you can identify, or 'belirsiz'>",
    "tek_degisken": "<the single impossible or altered element, in one clause>",
    "kamera": "<locked | slow push | pan | orbit | handheld>",
    "bakis": "<orbital | high aerial | ground level | other>",
    "isik": "<direction, time of day, quality>",
    "ekran_yazisi": <true|false>,
    "insan_var": <true|false>,
    "ses_tahmini": "<what the audio most likely is, from the level curve and the images>"
  },
  "uretim_prompt": "<a single production-ready English shot prompt, 90-160 words>",
  "neden": "<2-3 sentences: which visual choices carry this shot, in English>",
  "riskler": ["<what an AI engine will most likely get wrong in this shot>"]
}

RULES for "uretim_prompt":
- Describe ONE continuous shot. Name what is in the very first frame explicitly.
- Describe the camera as locked unless the frames clearly show otherwise.
- Describe the natural sound the scene would make, including where it gets quiet and
  where it swells, using the measured level curve you were given.
- Use positive visual language only. Never use: no, not, without, avoid, instead of.
- Never include on-screen text, captions, logos, watermarks or human faces.
- Do NOT copy a style label or brand name; describe what is actually visible.
"""


def gemini(kare_yollari: list[Path], olcum: dict, seri_stili: str | None) -> dict | None:
    try:
        from google import genai
        from google.genai import types
    except ImportError as e:
        raise SystemExit(f"google-genai yok: {e}")

    anahtar = os.environ.get("GEMINI_API_KEY_QC") or os.environ.get("GEMINI_API_KEY")
    if not anahtar:
        env = _ROOT / ".env"
        if env.exists():
            for line in env.read_text(encoding="utf-8").splitlines():
                if line.startswith("GEMINI_API_KEY=") and not anahtar:
                    anahtar = line.split("=", 1)[1].strip()
    if not anahtar:
        raise SystemExit("GEMINI_API_KEY yok (.env ya da ortam degiskeni)")

    parcalar = []
    for p in kare_yollari:
        parcalar.append(types.Part.from_bytes(data=p.read_bytes(), mime_type="image/jpeg"))
    metin = ("Frames are in time order, first frame first.\n\nMEASURED ANATOMY:\n"
             + json.dumps(olcum, ensure_ascii=False, indent=1))
    if seri_stili:
        metin += ("\n\nTARGET SERIES ART STYLE , write uretim_prompt so it sits inside this "
                  "style without restating it wholesale:\n" + seri_stili)
    parcalar.append(types.Part.from_text(text=metin))

    istemci = genai.Client(api_key=anahtar)
    cfg = types.GenerateContentConfig(
        system_instruction=SISTEM, response_mime_type="application/json", temperature=0.3,
    )
    for model in (MODEL, MODEL_YEDEK):
        try:
            y = istemci.models.generate_content(model=model, contents=parcalar, config=cfg)
            return json.loads(y.text)
        except Exception as e:
            print(f"  ! {model}: {str(e)[:160]}", file=sys.stderr)
    return None


# ─── Ana akis ─────────────────────────────────────────────────────────────────

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Referans videodan uretime hazir prompt cikarir")
    ap.add_argument("hedef", nargs="+", help="video URL'leri veya yerel dosyalar")
    ap.add_argument("--seri", help="cikti bu serinin art_style diline yazilir (or. one-variable)")
    ap.add_argument("--kare", type=int, default=6, help="Gemini'ye gidecek kare sayisi")
    ap.add_argument("--cikti", help="JSON rapor yolu")
    ap.add_argument("--plan-yaz", type=int, metavar="N",
                    help="N'den baslayarak plans/partNN.json yazar (--seri zorunlu)")
    a = ap.parse_args(argv)

    stil = None
    bible = None
    if a.seri:
        from series.bible import Bible
        bible = Bible.load(a.seri)
        if bible is None:
            raise SystemExit(f"bible bulunamadi: {a.seri}")
        stil = bible.data.get("art_style")

    sonuclar = []
    for hedef in a.hedef:
        print(f"\n{'=' * 70}\n{hedef}")
        with tempfile.TemporaryDirectory(prefix="tersine-") as td:
            tmp = Path(td)
            video = indir(hedef, tmp)
            olcum = olc(video)
            print(f"  sure {olcum['sure_sn']} sn | kesme {olcum['kesme_sayisi']} | "
                  f"LUFS {olcum['lufs']} | TP {olcum['true_peak_dbfs']} | LRA {olcum['lra']} | "
                  f"{olcum['cozunurluk']} {olcum['fps']}fps")
            if olcum["en_buyuk_ses_sicramasi"]:
                s = olcum["en_buyuk_ses_sicramasi"]
                print(f"  en buyuk ses sicramasi: {s['an_sn']}. saniyede +{s['artis_db']} dB")
            kl = kareler(video, tmp, a.kare, olcum["sure_sn"])
            print(f"  {len(kl)} kare -> Gemini")
            cevap = gemini(kl, olcum, stil)
        if cevap is None:
            print("  ! Gemini cevap vermedi, atlandi")
            continue
        g = cevap.get("gozlem", {})
        print(f"\n  YER          : {g.get('yer')}")
        print(f"  TEK DEGISKEN : {g.get('tek_degisken')}")
        print(f"  KAMERA       : {g.get('kamera')} | BAKIS: {g.get('bakis')}")
        print(f"  SES TAHMINI  : {g.get('ses_tahmini')}")
        print(f"\n  URETIM PROMPT:\n  {cevap.get('uretim_prompt', '')}")
        if cevap.get("riskler"):
            print("\n  RISKLER:")
            for r in cevap["riskler"]:
                print(f"    - {r}")
        sonuclar.append({"hedef": hedef, "olcum": olcum, "cozumleme": cevap})

    if a.cikti:
        Path(a.cikti).write_text(json.dumps(sonuclar, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\nrapor: {a.cikti}")

    if a.plan_yaz is not None:
        if not a.seri:
            raise SystemExit("--plan-yaz icin --seri gerekli")
        from series.bible import data_dir, doctrine_path, doctrine_sha256
        from series.series_meta import SeriesMeta
        meta = SeriesMeta.load(a.seri)
        cfg = meta.auto_replenish
        onek = (cfg.get("shot_plan") or [""])[0].strip()
        damga = doctrine_sha256(doctrine_path(a.seri))
        pdir = data_dir(a.seri) / "plans"
        pdir.mkdir(parents=True, exist_ok=True)
        for i, s in enumerate(sonuclar):
            n = a.plan_yaz + i
            yol = pdir / f"part{n:02d}.json"
            if yol.exists():
                print(f"  ATLANDI (zaten var): {yol.name}")
                continue
            prompt = s["cozumleme"].get("uretim_prompt", "").strip()
            plan = {
                "episode": {"number": n, "title": "TASLAK , baslik elle yazilacak"},
                "synopsis": s["cozumleme"].get("neden", ""),
                "narration": "",
                "caption": "TASLAK , caption elle yazilacak",
                "hashtags": "",
                "hook_shot": 1,
                "doctrine_sha256": damga,
                "shots": [{"n": 1, "duration": str(cfg.get("shot_seconds", "8")),
                           "prompt": (onek + "\n\n" + prompt) if onek else prompt,
                           "seed": None}],
                "_kaynak": s["hedef"],
                "_not": "tools/tersine_prompt.py ile uretildi; baslik, caption, family ve "
                        "seed_id ELLE doldurulmali, sonra preflight'tan gecirilmeli",
            }
            yol.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"  yazildi: {yol}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
