"""Saglayici arizasi ICERIK yeniden-deneme butcesini tuketmemeli.

18 Eylul 2026 olayi: Kie Omni saatlerce "Internal Error, Please try again
later" dondu. Bes deneme de dustu, en az cekim kapisi karsilanamadi ve
`produce` `None` dondurdu. `series_runner` `None`'i UNKNOWN sayar, UNKNOWN da
ICERIK sayacina yazilir (limit 3). Yani ust uste uc saglayici kesintisi,
icerigiyle hicbir sorunu olmayan bir bolumu `needs_human` yapip kuyruktan
dusurecekti , kanal da o bolumu bir daha hic denemeyecekti.

Ayrim zaten kodda vardi ve kullanilmiyordu:
  status == "FAIL"                -> motor hic klip teslim etmedi (ALTYAPI)
  status == "qc_fail" / "qc_skip" -> QC icerigi reddetti  (ICERIK)
"""

from unittest import mock

import pytest

from series import series_runner
from series.produce import ProduceResult, _min_shot_gate_result
from series.series_meta import SeriesMeta


def test_qc_reddinde_eski_davranis_korunur():
    """QC icerigi reddettiyse sonuc None kalir (UNKNOWN -> icerik sayaci)."""
    assert _min_shot_gate_result([]) is None


def test_motor_klip_teslim_etmediyse_altyapi_kodu_doner():
    sonuc = _min_shot_gate_result([1, 3])
    assert sonuc is not None
    assert sonuc.status == "qc_hold"
    assert sonuc.reason_code == "TRANSIENT_INFRA"
    assert "1, 3" in sonuc.reason


def test_altyapi_kodu_series_runner_tarafindan_infra_dalina_yonlenir():
    """Asil kazanc burada: icerik sayaci 2/3'te DURUR, bolum dusmez."""
    meta = SeriesMeta({
        "slug": "motor-arizasi-fixture",
        "base_title": "Motor Arizasi Fixture",
        "total_parts": 10,
        "next_part": 4,
        "status": "active",
        "publish_mode": "auto",
        "upload_profile": "p",
        "platforms": ["youtube"],
        "parts": {"4": {"retry_count": 2, "status": "qc_retry"}},
    })
    sonuc = _min_shot_gate_result([1])
    with mock.patch.object(meta, "save"), \
            mock.patch.object(meta, "save_atomic", create=True), \
            mock.patch.object(series_runner, "_series_alert", return_value=True):
        ilerledi = series_runner._record_recoverable_failure(meta, 4, sonuc)

    part = meta.get_part(4)
    assert ilerledi is False, "saglayici arizasi bolumu kuyruktan dusurmemeli"
    assert part["retry_count"] == 2, "ICERIK sayaci saglayici arizasiyla artti"
    assert part["infra_retry_count"] == 1
    assert part["last_reason_code"] == "TRANSIENT_INFRA"


@pytest.mark.parametrize("dusen,beklenen", [([], None), ([2], "TRANSIENT_INFRA")])
def test_karar_yalniz_motor_arizasina_bakar(dusen, beklenen):
    sonuc = _min_shot_gate_result(dusen)
    assert (sonuc.reason_code if sonuc else None) == beklenen
