# -*- coding: utf-8 -*-
"""tamlik.py birim testleri , uretim tamligi ve ozne etiketleri.

Hicbir test gercek depoyu okumaz: her vaka tmp_path icinde sahte bir uretim
klasoru kurar ve `BEYIN_URETIM_KOK` ile oraya yonlendirir.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

MODUL_KLASORU = Path(__file__).resolve().parent.parent
if str(MODUL_KLASORU) not in sys.path:
    sys.path.insert(0, str(MODUL_KLASORU))

import tamlik  # noqa: E402


# ------------------------------------------------------------ yardimcilar

def uretim_kur(kok: Path, kanal_yolu: str = "shadowedhistory/flashpoints",
               published=None, series=None, planlar=None) -> Path:
    """tmp_path icinde sahte bir kanal uretim klasoru kurar."""
    hedef = kok / kanal_yolu
    (hedef / "plans").mkdir(parents=True, exist_ok=True)
    if published is not None:
        (hedef / "published.json").write_text(
            json.dumps(published, ensure_ascii=False), encoding="utf-8")
    if series is not None:
        (hedef / "series.json").write_text(
            json.dumps(series, ensure_ascii=False), encoding="utf-8")
    for part, sureler in (planlar or {}).items():
        plan = {"shots": [{"n": i + 1, "duration": s}
                          for i, s in enumerate(sureler)]}
        (hedef / "plans" / ("part%02d.json" % part)).write_text(
            json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    return hedef


def yayin(part: int, vid: str) -> dict:
    return {"part": part, "subtitle": "b%d" % part, "ts": "2026-09-01T00:00:00Z",
            "results": {"youtube": vid, "instagram": None, "tiktok": None}}


@pytest.fixture
def kok(tmp_path, monkeypatch):
    monkeypatch.setenv("BEYIN_URETIM_KOK", str(tmp_path))
    return tmp_path


# ------------------------------------------------------------ production_root

def test_production_root_env_degiskenini_kullanir(tmp_path, monkeypatch):
    monkeypatch.setenv("BEYIN_URETIM_KOK", str(tmp_path))
    assert Path(tamlik.production_root()).resolve() == tmp_path.resolve()


def test_production_root_env_yoksa_cwd_ustune_duser(tmp_path, monkeypatch):
    monkeypatch.delenv("BEYIN_URETIM_KOK", raising=False)
    alt = tmp_path / "gunluk_beyin"
    alt.mkdir()
    monkeypatch.chdir(alt)
    assert Path(tamlik.production_root()).resolve() == tmp_path.resolve()


def test_production_root_cagri_aninda_hesaplanir(tmp_path, monkeypatch):
    """Import aninda donmus olmamali, yoksa testler yonlendiremez."""
    monkeypatch.setenv("BEYIN_URETIM_KOK", str(tmp_path / "a"))
    ilk = Path(tamlik.production_root())
    monkeypatch.setenv("BEYIN_URETIM_KOK", str(tmp_path / "b"))
    assert Path(tamlik.production_root()) != ilk


# ------------------------------------------------------------ production_dir

def test_uretim_kaydi_olmayan_kanal_none(kok):
    assert tamlik.production_dir("aimagine-fear") is None


def test_bilinmeyen_kanal_none(kok):
    assert tamlik.production_dir("boyle-bir-kanal-yok") is None


# ------------------------------------------------- episode_completeness

def test_dropped_shots_tek_basina_yeterli(kok):
    """Plan dosyasi HIC yokken bile dropped_shots eksik demek icin yeter."""
    uretim_kur(kok, published=[yayin(26, "vidA")],
               series={"parts": {"26": {"dropped_shots": [2]}}})
    sonuc = tamlik.episode_completeness("flashpoints")
    assert sonuc["vidA"]["complete"] is False
    assert "dropped_shots" in sonuc["vidA"]["reason"]


def test_sure_orani_dusukse_eksik(kok):
    uretim_kur(kok, published=[yayin(22, "vidB")], series={"parts": {}},
               planlar={22: ["8", "8"]})
    sonuc = tamlik.episode_completeness("flashpoints", durations={"vidB": 7.32})
    assert sonuc["vidB"]["complete"] is False
    assert sonuc["vidB"]["ratio"] == pytest.approx(0.4575, abs=1e-3)


def test_sure_orani_yuksekse_tam(kok):
    uretim_kur(kok, published=[yayin(25, "vidC")], series={"parts": {}},
               planlar={25: ["10", "10"]})
    sonuc = tamlik.episode_completeness("flashpoints", durations={"vidC": 19.04})
    assert sonuc["vidC"]["complete"] is True


@pytest.mark.parametrize("olculen,beklenen", [(13.8, False), (14.2, True)])
def test_esik_siniri_iki_yone_de_dogru(kok, olculen, beklenen):
    """0.70 esigi: 0.69 eksik, 0.71 tam."""
    uretim_kur(kok, published=[yayin(9, "vidD")], series={"parts": {}},
               planlar={9: ["10", "10"]})
    sonuc = tamlik.episode_completeness("flashpoints", durations={"vidD": olculen})
    assert sonuc["vidD"]["complete"] is beklenen


def test_bilgi_yoksa_none_doner_false_degil(kok):
    """BILINMIYOR, EKSIK demek DEGILDIR , sessiz veri kaybi olmamali."""
    uretim_kur(kok, published=[yayin(3, "vidE")], series={"parts": {}})
    sonuc = tamlik.episode_completeness("flashpoints")
    assert sonuc["vidE"]["complete"] is None


def test_olcum_verilmezse_sure_karari_verilmez(kok):
    uretim_kur(kok, published=[yayin(3, "vidE")], series={"parts": {}},
               planlar={3: ["10", "10"]})
    sonuc = tamlik.episode_completeness("flashpoints", durations=None)
    assert sonuc["vidE"]["complete"] is None


def test_part_numarasi_sifirla_doldurulur(kok):
    """part 5 -> plans/part05.json"""
    uretim_kur(kok, published=[yayin(5, "vidF")], series={"parts": {}},
               planlar={5: ["10", "10"]})
    sonuc = tamlik.episode_completeness("flashpoints", durations={"vidF": 4.0})
    assert sonuc["vidF"]["complete"] is False


def test_uretim_kaydi_olmayan_kanal_bos_doner(kok):
    assert tamlik.episode_completeness("aimagine-fear") == {}


def test_klasor_yoksa_bos_doner_patlamaz(kok):
    assert tamlik.episode_completeness("flashpoints") == {}


def test_youtube_id_olmayan_kayit_atlanir(kok):
    uretim_kur(kok, series={"parts": {}}, published=[
        {"part": 11, "results": {"youtube": None}},
        yayin(12, "vidG"),
    ])
    sonuc = tamlik.episode_completeness("flashpoints")
    assert set(sonuc) == {"vidG"}


@pytest.mark.parametrize("dosya", ["published.json", "series.json"])
def test_bozuk_json_patlatmaz(kok, dosya):
    hedef = uretim_kur(kok, published=[yayin(1, "vidH")], series={"parts": {}})
    (hedef / dosya).write_text("{bozuk json", encoding="utf-8")
    tamlik.episode_completeness("flashpoints", durations={"vidH": 5.0})


def test_bozuk_plan_json_patlatmaz(kok):
    hedef = uretim_kur(kok, published=[yayin(1, "vidI")], series={"parts": {}})
    (hedef / "plans" / "part01.json").write_text("[[[", encoding="utf-8")
    sonuc = tamlik.episode_completeness("flashpoints", durations={"vidI": 5.0})
    assert sonuc["vidI"]["complete"] is None


def test_published_liste_degilse_bos_doner(kok):
    uretim_kur(kok, published={"liste": "degil"}, series={"parts": {}})
    assert tamlik.episode_completeness("flashpoints") == {}


def test_dropped_shots_bos_liste_eksik_saymaz(kok):
    uretim_kur(kok, published=[yayin(4, "vidJ")],
               series={"parts": {"4": {"dropped_shots": []}}},
               planlar={4: ["10", "10"]})
    sonuc = tamlik.episode_completeness("flashpoints", durations={"vidJ": 19.0})
    assert sonuc["vidJ"]["complete"] is True


def test_sure_alani_bozuksa_sifir_sayilir(kok):
    """Okunamayan duration 0 katkida bulunur; toplam 0 ise karar verilmez."""
    uretim_kur(kok, published=[yayin(6, "vidK")], series={"parts": {}},
               planlar={6: ["abc", None]})
    sonuc = tamlik.episode_completeness("flashpoints", durations={"vidK": 9.0})
    assert sonuc["vidK"]["complete"] is None


# ------------------------------------------------------ read_subject_labels

def etiket_yaz(kok: Path, kanal: str, icerik) -> None:
    hedef = kok / "kanallar" / kanal / "ozne.json"
    hedef.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(icerik, str):
        hedef.write_text(icerik, encoding="utf-8")
    else:
        hedef.write_text(json.dumps(icerik, ensure_ascii=False), encoding="utf-8")


def test_etiketler_okunur(tmp_path):
    etiket_yaz(tmp_path, "flashpoints", {"a": "SEY", "b": "OLAY", "c": "KISI"})
    assert tamlik.read_subject_labels("flashpoints", tmp_path) == {
        "a": "SEY", "b": "OLAY", "c": "KISI"}


def test_gecersiz_etiket_atilir(tmp_path):
    etiket_yaz(tmp_path, "flashpoints",
               {"a": "SEY", "b": "SEYLER", "c": 5, "d": None})
    assert tamlik.read_subject_labels("flashpoints", tmp_path) == {"a": "SEY"}


@pytest.mark.parametrize("icerik", ["", "{bozuk", "[1,2,3]", '"metin"'])
def test_bozuk_etiket_dosyasi_patlatmaz(tmp_path, icerik):
    etiket_yaz(tmp_path, "flashpoints", icerik)
    assert tamlik.read_subject_labels("flashpoints", tmp_path) == {}


def test_etiket_dosyasi_yoksa_bos(tmp_path):
    assert tamlik.read_subject_labels("flashpoints", tmp_path) == {}
