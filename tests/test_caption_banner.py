"""Kalici ust metin banti: geometri ve mevcut serileri etkilememe kanitlari.

Dayanak olcum: sentinal_ihsan/REELYZE-RAPOR.md, 18 Eylul 2026. Referans video
daOYkiaV5rQ (8,1M izlenme) 720x1280 karede su oranlari tasiyor: ust bos serit
%13,7, beyaz bant %11,0, goruntu %65,9, alt bos serit %9,5.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from core import ffmpeg_tools
from series.bible import Bible

ROOT = Path(__file__).resolve().parents[1]


def _bible(series_extra: dict) -> Bible:
    data = {
        "series": {"slug": "t", "title": "T", **series_extra},
        "art_style": "x",
        "characters": [],
        "environments": [],
    }
    return Bible(data)


def test_alan_yoksa_kapali_mevcut_seriler_etkilenmez():
    """Alan yazilmamis her seri icin bant KAPALI kalmali."""
    assert _bible({}).caption_banner == {}
    assert _bible({"caption_banner": {"enabled": False}}).caption_banner == {}


def test_canli_seri_bibleleri_bandi_acmiyor():
    """Dort canli hattin hicbiri bu alani tasimamali (regresyon kilidi)."""
    for path in sorted(ROOT.glob("*/*/bible.json")):
        if "_surumler" in path.parts or "output" in path.parts:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "caption_banner" not in data.get("series", {}), (
            f"{path} bandi acmis; bu degisiklik mevcut serileri degistirmemeli"
        )


def test_enabled_true_sozlege_cevrilir():
    assert _bible({"caption_banner": True}).caption_banner == {"enabled": True}


def test_preserve_case_bool_olmali():
    with pytest.raises(ValueError):
        _bible({"caption_banner": {"enabled": True, "preserve_case": "evet"}}).caption_banner


def _probe(path: Path) -> tuple[int, int]:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True).stdout.strip()
    w, h = out.split(",")[:2]
    return int(w), int(h)


@pytest.mark.skipif(
    subprocess.run(["ffmpeg", "-version"], capture_output=True).returncode != 0,
    reason="ffmpeg yok",
)
def test_geometri_referansla_ayni_ve_cozunurluk_korunur(tmp_path):
    """Bant referans oranlarini tutturmali ve cikti boyu girdiyle AYNI kalmali.

    Cikti boyu kilidi bos degil: oransal pad yuvarlama kaymasi 1920'yi 1918'e
    dusuruyordu (18 Eylul 2026'da olculdu ve mutlak piksele cevrildi).
    """
    src = tmp_path / "src.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
         "-i", "testsrc=size=1080x1920:rate=30:duration=2",
         "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(src)],
        check=True, capture_output=True)

    dst = tmp_path / "dst.mp4"
    ffmpeg_tools.caption_banner_overlay(src, dst, title="BASLIK", subtitle="(alt)")

    assert _probe(dst) == (1080, 1920), "cikti cozunurlugu girdiyle ayni kalmali"

    kare = tmp_path / "k.png"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1", "-i", str(dst),
                    "-frames:v", "1", str(kare)], check=True, capture_output=True)

    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(kare), "-vf", "format=gray",
         "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    rows = [sum(raw[y * 1080:(y + 1) * 1080]) / 1080 for y in range(1920)]

    # Ust serit siyah, bandin ortasi beyaz, goruntu alani ikisi de degil.
    assert rows[100] < 12, "ust serit siyah olmali"
    assert rows[round(1920 * 0.19)] > 200, "bant beyaz olmali"
    assert rows[1900] < 12, "alt serit siyah olmali"
    # Goruntu penceresi dogru yerde baslamali (%24,7).
    assert 12 <= rows[round(1920 * 0.30)] <= 250, "goruntu alani bantta olmamali"


@pytest.mark.skipif(
    subprocess.run(["ffmpeg", "-version"], capture_output=True).returncode != 0,
    reason="ffmpeg yok",
)
def test_bos_metin_required_degilse_dosyayi_kopyalar(tmp_path):
    src = tmp_path / "src.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
         "-i", "testsrc=size=1080x1920:rate=30:duration=1",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", str(src)],
        check=True, capture_output=True)
    dst = tmp_path / "dst.mp4"
    ffmpeg_tools.caption_banner_overlay(src, dst, title="", subtitle="")
    assert dst.exists() and dst.stat().st_size == src.stat().st_size

    with pytest.raises(RuntimeError):
        ffmpeg_tools.caption_banner_overlay(src, tmp_path / "x.mp4",
                                            title="", subtitle="", required=True)
