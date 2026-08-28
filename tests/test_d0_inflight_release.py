"""ROCK D0: ucusta kayitlari deney yolunda SERBEST BIRAKILIR.

2026-08-28 pilot kosulari kie_reservations.json'da 19 adet kapanmamis
`kind: "inflight"` kaydi biraktu: series/experiment.py authorize_spend'in
dondurdugu inflight_id'yi kullanmiyordu. Kayitlar yalniz 900 sn TTL ile dusuyordu.

Sonuc fail-closed yondeydi (fazla harcamaz, fazla REDDEDER) ama koruma tam da
bakiye daraldiginda - yani en cok gerektigi anda - yanlis calisiyordu.
"""

import json
import pathlib
import sys
from unittest import mock

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from series import balance_floor, experiment


@pytest.fixture
def kurulum(tmp_path, monkeypatch):
    """Hem deney defterini hem taban defterini tmp'ye tasi."""
    deney = tmp_path / "experiments_ledger.json"
    deney.write_text(json.dumps({"experiments": {"e1": {
        "total_cap": 10000,
        "stage_caps": {"pilot": 5000},
        "reservations": [],
        "measurements": [],
    }}}), encoding="utf-8")
    monkeypatch.setattr(experiment, "LEDGER_PATH", deney)

    taban = tmp_path / "kie_reservations.json"
    monkeypatch.setattr(balance_floor, "STATE_PATH", taban)
    monkeypatch.setattr(balance_floor, "LOCK_PATH", taban.with_suffix(".lock"))
    monkeypatch.setenv("KIE_BALANCE_FLOOR", "1000")
    monkeypatch.setattr(balance_floor, "check_credit", lambda: 5000.0, raising=False)
    return deney, taban


def _acik_ucusta(taban: pathlib.Path) -> list:
    if not taban.exists():
        return []
    kayitlar = json.loads(taban.read_text(encoding="utf-8"))["reservations"]
    return [r for r in kayitlar if r.get("kind") == "inflight"]


def _yetkilendir(estimate=100.0):
    with mock.patch("core.cost_tracker.conservative_credit_estimate",
                    return_value=estimate),             mock.patch("core.kie_api.check_credit", return_value=5000.0):
        return experiment._reserve("e1", "pilot", "main_shot", "omni", "6")


def test_uzlastirma_ucusta_kaydini_birakiyor(kurulum):
    deney, taban = kurulum
    sonuc = _yetkilendir()
    assert sonuc is not None
    rezervasyon_id, _ = sonuc
    assert len(_acik_ucusta(taban)) == 1, "yetkilendirmeden sonra ucusta kaydi olmali"

    assert experiment.record("e1", 84.0, reservation_id=rezervasyon_id) is True
    assert _acik_ucusta(taban) == [], "uzlastirmadan sonra ucusta kaydi KALMAMALI"
    assert balance_floor.outstanding(path=taban) == 0.0


def test_ard_arda_uc_cagri_sizinti_birakmiyor(kurulum):
    """Asil olculen olay: pilot kosusunda 19 kayit birikmisti."""
    deney, taban = kurulum
    for _ in range(3):
        sonuc = _yetkilendir()
        assert sonuc is not None
        experiment.record("e1", 84.0, reservation_id=sonuc[0])
    assert _acik_ucusta(taban) == []
    assert balance_floor.outstanding(path=taban) == 0.0


def test_basarisiz_cagri_da_birakiliyor(kurulum):
    """settle_last(0) yolu: cagri patladi, ama kredi 15 dakika tutulmamali."""
    deney, taban = kurulum
    sonuc = _yetkilendir()
    experiment.record("e1", 0.0, reservation_id=sonuc[0])
    assert _acik_ucusta(taban) == []


def test_defter_yazilamazsa_ucusta_kaydi_birakiliyor(kurulum, monkeypatch):
    """Yetkilendirme gecti ama defter kaydedilemedi: tutulan kredi geri verilmeli."""
    deney, taban = kurulum

    def patla(*_args, **_kwargs):
        raise OSError("disk dolu")

    monkeypatch.setattr(experiment, "_save", patla)
    assert _yetkilendir() is None
    assert _acik_ucusta(taban) == [], "kayit basarisiz oldu ama kredi tutulmaya devam etti"


def test_taban_kapaliyken_defter_hic_olusmuyor(tmp_path, monkeypatch):
    """P9: taban opt-in degilse davranis bit-degismez, bakiye bile sorulmaz."""
    deney = tmp_path / "experiments_ledger.json"
    deney.write_text(json.dumps({"experiments": {"e1": {
        "total_cap": 10000, "stage_caps": {"pilot": 5000},
        "reservations": [], "measurements": [],
    }}}), encoding="utf-8")
    monkeypatch.setattr(experiment, "LEDGER_PATH", deney)
    taban = tmp_path / "kie_reservations.json"
    monkeypatch.setattr(balance_floor, "STATE_PATH", taban)
    monkeypatch.setattr(balance_floor, "LOCK_PATH", taban.with_suffix(".lock"))
    monkeypatch.delenv("KIE_BALANCE_FLOOR", raising=False)

    cagrildi = []
    with mock.patch("core.cost_tracker.conservative_credit_estimate", return_value=100.0),             mock.patch("core.kie_api.check_credit",
                       side_effect=lambda: cagrildi.append(1)):
        sonuc = experiment._reserve("e1", "pilot", "main_shot", "omni", "6")
    assert sonuc is not None
    assert cagrildi == [], "taban kapaliyken bakiye SORULMAMALI"
    assert not taban.exists(), "taban kapaliyken defter dosyasi OLUSMAMALI"
