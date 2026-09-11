"""Kanarya kilidi: basarisiz bir kanarya her gun para yakmasin.

Codex incelemesinin 1 numarali BLOCKER'i. Kilit olmadan su oluyordu:
kapi dusurur -> yayin olmaz -> deftere dogrulanmis satir dusmez ->
sirdaki() ertesi gun AYNI rotayi secer -> ayni kombinasyon yeniden uretilir.
Gunde ~615 kredi (~3 dolar), suresiz, ve cuzdan dort kanalla ORTAK.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJE_KOKU = Path(__file__).resolve().parent.parent
if str(PROJE_KOKU) not in sys.path:
    sys.path.insert(0, str(PROJE_KOKU))

import profil as profil_modulu  # noqa: E402
from tools import gunluk  # noqa: E402


ANAHTAR = ("bytedance/seedance-2", 15, "1080p", 24)


def _kilit_kur(tmp_path: Path, monkeypatch, anahtar=ANAHTAR, hash_=None) -> Path:
    yol = tmp_path / "kanarya_basarisiz.json"
    yol.write_text(json.dumps({
        "anahtar": [str(p) for p in anahtar],
        "profil_hash": hash_ if hash_ is not None else profil_modulu.profil_hash(),
        "sebep": "istendi 1080p, geldi 720x1280",
        "ts": "2026-09-10T20:00:00+00:00",
    }), encoding="utf-8")
    monkeypatch.setattr(gunluk, "KANARYA_KILIDI", yol)
    return yol


def test_kilit_ayni_kombinasyonu_kapatir(tmp_path: Path, monkeypatch) -> None:
    _kilit_kur(tmp_path, monkeypatch)
    kilitli, mesaj = gunluk.kanarya_kilitli_mi(ANAHTAR)
    assert kilitli is True
    assert "kapida kaldi" in mesaj


def test_kilit_BASKA_kombinasyonu_kapatmaz(tmp_path: Path, monkeypatch) -> None:
    _kilit_kur(tmp_path, monkeypatch)
    baska = ("bytedance/seedance-2", 15, "720p", 24)
    assert gunluk.kanarya_kilitli_mi(baska)[0] is False


def test_profil_degisince_kilit_dusuyor(tmp_path: Path, monkeypatch) -> None:
    """Profil duzeltilirse yeniden denemeye deger, kilit engel olmamali."""
    _kilit_kur(tmp_path, monkeypatch, hash_="eski-hash")
    assert gunluk.kanarya_kilitli_mi(ANAHTAR)[0] is False


def test_kilit_yoksa_veya_bozuksa_engel_yok(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(gunluk, "KANARYA_KILIDI", tmp_path / "yok.json")
    assert gunluk.kanarya_kilitli_mi(ANAHTAR)[0] is False
    bozuk = tmp_path / "bozuk.json"
    bozuk.write_text("{ bu json degil", encoding="utf-8")
    monkeypatch.setattr(gunluk, "KANARYA_KILIDI", bozuk)
    assert gunluk.kanarya_kilitli_mi(ANAHTAR)[0] is False


# ----------------------------------------------------------------------
# EN KRITIK: kilitliyken SIFIR kredi, SIFIR uretim
# ----------------------------------------------------------------------
def test_kilitliyken_uretim_ve_kredi_HIC_calismaz(tmp_path: Path, monkeypatch) -> None:
    slug = "istanbul-camlica-amber-sicak"
    _kilit_kur(tmp_path, monkeypatch)
    monkeypatch.setattr(gunluk, "DEFTER", tmp_path / "yayin.jsonl")
    monkeypatch.setattr(gunluk, "defter", lambda: [])
    monkeypatch.setattr(gunluk, "kredi", lambda: pytest.fail("KREDI OKUNDU"))

    def _tuzak(cmd, cwd):
        pytest.fail("SUBPROCESS CALISTI: %s" % cmd)

    monkeypatch.setattr(gunluk, "kosa", _tuzak)
    assert gunluk.main(["--sehir", slug, "--profil", "1080p"]) == 1


def test_kapida_kalan_kanarya_kilidi_YAZAR(tmp_path: Path, monkeypatch) -> None:
    """Ilk basarisizlik kilidi kurmali, yoksa ertesi gun yine para yanar."""
    slug = "test-slug"
    kilit = tmp_path / "kanarya_basarisiz.json"
    monkeypatch.setattr(gunluk, "KOK", tmp_path)
    monkeypatch.setattr(gunluk, "KANARYA_KILIDI", kilit)
    monkeypatch.setattr(gunluk, "DEFTER", tmp_path / "yayin.jsonl")
    monkeypatch.setattr(gunluk, "ONAY_DOSYASI", tmp_path / "onay.json")
    cikti = tmp_path / "out" / slug
    (cikti / "video").mkdir(parents=True)
    (cikti / "video" / "test_gunluk_1.mp4").write_bytes(b"raw")
    (cikti / "CAPTION.txt").write_text("caption #Tag", encoding="utf-8")
    (cikti / "TITLE.txt").write_text(
        "Test Tower glass drop #shorts\nI slid off the Test Tower #shorts",
        encoding="utf-8",
    )
    monkeypatch.setattr(gunluk, "defter", lambda: [])
    monkeypatch.setattr(gunluk, "kredi", lambda: 10000)  # 1080p is ~1530 ister
    monkeypatch.setattr(gunluk, "rota_suresi", lambda s, kok=None: 15)
    monkeypatch.setattr(gunluk, "rota_paleti", lambda s, kok=None: "neon")
    monkeypatch.setattr(gunluk, "sha256_dosya", lambda p: "s" * 64)
    monkeypatch.setattr(gunluk, "ses_olcumleri", lambda m: {"lufs": -14.0, "true_peak": -1.2})
    monkeypatch.setattr(
        gunluk, "kosa",
        lambda cmd, cwd: type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})(),
    )

    def _master(kaynak, hedef, **kw):
        Path(hedef).parent.mkdir(parents=True, exist_ok=True)
        Path(hedef).write_bytes(b"master")

    monkeypatch.setattr("core.ffmpeg_tools.master_audio", _master)
    # Model sessizce dusurdu
    monkeypatch.setattr(
        gunluk, "denetle",
        lambda m, s, p: (["istendi 1080p, geldi 720x1280 - model sessizce dusurdu"],
                         {"fps": 24.0, "sure": 15.0}),
    )
    monkeypatch.setattr(gunluk, "yayinla", lambda *a, **k: pytest.fail("YAYINLANDI"))

    assert gunluk.main(["--sehir", slug, "--profil", "1080p"]) == 1
    assert kilit.exists(), "kapida kalindi ama kilit YAZILMADI, ertesi gun yine yanar"
    veri = json.loads(kilit.read_text(encoding="utf-8"))
    assert veri["anahtar"] == [str(p) for p in ANAHTAR]
    assert "sessizce dusurdu" in veri["sebep"]


# ----------------------------------------------------------------------
# onayla() kendi modulunun kabul edecegi onay uretmeli
# ----------------------------------------------------------------------
def test_elle_onay_kendi_modulunce_kabul_edilir(tmp_path: Path, monkeypatch) -> None:
    """onayla() olcum yazmazsa yayin_izni onu REDDEDER , kendi kendini yiyen kapi."""
    master = tmp_path / "m.mp4"
    master.write_bytes(b"master")
    sha = gunluk.sha256_dosya(master)
    profil = gunluk.PROFILLER["1080p"]
    kayit = {
        "master_sha": sha,
        "denetim_sonucu": "basarili",
        "istenen_profil": "1080p",
        "model": gunluk.MODEL,
        "beklenen_sure": 15,
        "slug": "s",
        "profil_hash": profil_modulu.profil_hash(),
        "olculen": {
            "genislik": profil["genislik"], "yukseklik": profil["yukseklik"],
            "fps": profil["beklenen_fps"], "sure": 15.0,
        },
        "ses": {"lufs": -14.0, "true_peak": -1.2},
    }
    onay_yolu = tmp_path / "onay.json"
    monkeypatch.setattr(gunluk, "ONAY_DOSYASI", onay_yolu)
    monkeypatch.setattr(gunluk, "uretim_kaydi_bul", lambda *a: kayit)
    assert gunluk.onayla(master) == 0

    # Ve simdi ayni modul bu onayi KABUL etmeli
    izinli, durum = gunluk.yayin_izni("1080p", 15)
    assert izinli is True, "onayla() kendi modulunun reddettigi onay yazdi: %s" % durum
