"""Uretilen videoyu denetler: teknik kimlik, sahne kesmeleri, kontakt sayfasi, transkript.

Kullanim:
    python tools/kontrol.py out/vegas-15/video/vegas-15_seedance_01.mp4

"Pipeline basarili dedi" kalite kaniti degildir. Bu script kanit uretir, karari sen verirsin.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return (proc.stdout or "") + (proc.stderr or "")


def probe(video: Path) -> dict:
    out = run([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration,size",
        "-show_entries", "stream=codec_type,width,height,r_frame_rate,channels",
        "-of", "default=noprint_wrappers=1", str(video),
    ])
    return dict(re.findall(r"^(\w+)=(.+)$", out, re.M))


def scene_cuts(video: Path, threshold: float) -> list[float]:
    out = run([
        "ffmpeg", "-hide_banner", "-i", str(video),
        "-filter:v", "select='gt(scene,%s)',showinfo" % threshold,
        "-f", "null", "-",
    ])
    return [float(t) for t in re.findall(r"pts_time:([0-9.]+)", out)]


def contact_sheet(video: Path, duration: float, out_path: Path) -> Path:
    cols = 5
    rows = max(1, int(duration + 0.999) // cols + (1 if int(duration + 0.999) % cols else 0))
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(video),
        "-vf", "fps=1,scale=260:-1,tile=%dx%d:padding=6:margin=6:color=white" % (cols, rows),
        "-frames:v", "1", "-y", str(out_path),
    ])
    return out_path


def transcribe(video: Path) -> list[str]:
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return ["(faster-whisper kurulu degil)"]
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(video), beam_size=5, vad_filter=False)
    lines = ["dil: %s (%.2f)" % (info.language, info.language_probability)]
    for seg in segments:
        lines.append("[%5.2f - %5.2f] %s" % (seg.start, seg.end, seg.text.strip()))
    if len(lines) == 1:
        lines.append("(konusma bulunamadi)")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("video")
    parser.add_argument("--threshold", type=float, default=0.25)
    parser.add_argument("--no-transcript", action="store_true")
    args = parser.parse_args()

    video = Path(args.video)
    if not video.exists():
        sys.exit("Video yok: %s" % video)

    info = probe(video)
    duration = float(info.get("duration", 0) or 0)
    print("=== TEKNIK KIMLIK ===")
    print("dosya    : %s" % video.name)
    print("sure     : %.3f sn" % duration)
    print("cozunurluk: %sx%s" % (info.get("width"), info.get("height")))
    print("fps      : %s" % info.get("r_frame_rate"))
    print("boyut    : %.1f MB" % (int(info.get("size", 0)) / 1e6))
    print("ses      : %s kanal" % info.get("channels", "YOK"))

    cuts = scene_cuts(video, args.threshold)
    print()
    print("=== SAHNE KESMELERI (esik %.2f) ===" % args.threshold)
    if cuts:
        print("%d tetikleme: %s" % (len(cuts), ", ".join("%.2f" % c for c in cuts)))
        print("NOT: tetikleme her zaman kesme demek degil; su patlamasi da tetikler.")
        print("Kontakt sayfasindan gozle dogrula.")
    else:
        print("Sifir tetikleme. Tek kesintisiz cekim.")

    sheet = contact_sheet(video, duration, video.with_suffix(".kontakt.png"))
    print()
    print("=== KONTAKT SAYFASI ===")
    print(sheet)

    if not args.no_transcript:
        print()
        print("=== TRANSKRIPT ===")
        for line in transcribe(video):
            print(line)

    print()
    print("=== GOZLE KONTROL LISTESI ===")
    for item in [
        "Yuz, sac, el, kol, govde HIC gorunuyor mu? (gorunuyorsa format bozuk)",
        "Ufuk bukuluyor mu? (balik gozu yoksa yukseklik hissi yok)",
        "Kaydiragin altindan sehir gorunuyor mu? (seffaflik korkuyu ureten sey)",
        "Iki bacak iki ayak, alt ucte birde, simetrik mi?",
        "Tek doygun renk kadraji yonetiyor mu?",
        "Virajda bacaklar yerinde durup dunya mi donuyor?",
        "Havuz ulasilmadan once ileride goruldu mu?",
        "Sehir dogru sehir mi? (kaynak kanal bunu kontrol etmiyor, biz edecegiz)",
        "Kesme var mi?",
        "Muzik var mi? (olmamali)",
    ]:
        print("  [ ] " + item)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
