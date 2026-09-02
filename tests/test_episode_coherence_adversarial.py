"""Bolum tutarliligi raporu , Visionary dusman testleri.

Nemotron'un kendi seti (tests/test_episode_coherence.py) sozlesmedeki 13 vakayi
kapsiyor. Bu dosya onun KAPSAMADIGI tuzaklari kovaliyor: Python'un bool/int
ozdesligi, tek seferlik iteratorler, NaN ve sonsuz sure, tekrarli dusus kaydi.
Bunlarin hepsi "asla patlamaz ve None asla degraded uretmez" sozunu sinar.
"""

from __future__ import annotations

import math

import pytest

from series.episode_coherence import episode_coherence_report


def _report(**over):
    base = dict(
        shot_numbers=[1, 2, 3, 4],
        dropped_shots=[],
        narration_expected=True,
        narration_ok=True,
        duration_s=24.0,
        duration_band=[14, 41],
    )
    base.update(over)
    return episode_coherence_report(
        base.pop("shot_numbers"), base.pop("dropped_shots"), **base
    )


# ── 1. bool/int ozdesligi: Python'da True == 1 ────────────────────────────────

def test_bool_in_dropped_shots_is_not_silently_shot_one():
    """TUZAK: Python'da `True in [1,2,3]` True'dur.

    dropped_shots icine kazara bool sizarsa (JSON'dan gelen bozuk veri, bir
    bayragin yanlislikla listeye konmasi) rapor cekim 1'i dusmus SAYABILIR ve
    bolumu sahte olarak 'degraded' isaretler. Rapor bir kalite kaydi oldugu
    icin yanlis pozitif, yanlis negatif kadar zararlidir.
    """
    report = _report(dropped_shots=[True])
    assert report["arc_roles_missing"] == [], (
        "bool, cekim 1 sanildi: " + repr(report["arc_roles_missing"]))
    assert report["degraded"] is False


def test_bool_as_last_shot_does_not_break_loop_closed():
    report = _report(shot_numbers=[1, 2, 3, 4], dropped_shots=[False])
    assert report["loop_closed"] is True


# ── 2. tek seferlik iterator ──────────────────────────────────────────────────

def test_generator_dropped_shots_is_not_consumed_twice():
    """TUZAK: dropped_shots iki kez okunuyor.

    Sozlesme `iterable[int]` diyor. Bir generator tek seferliktir: ilk kullanim
    (loop_closed) onu tuketirse ikinci kullanim (arc_roles_missing) BOS gorur ve
    dusen cekimler sessizce kaybolur. Tam olarak raporun yakalamasi gereken sey
    kaybolmus olur.
    """
    report = episode_coherence_report(
        [1, 2, 3, 4], (n for n in [4]),
        narration_expected=True, narration_ok=True,
        duration_s=18.0, duration_band=[14, 41],
    )
    assert report["loop_closed"] is False
    assert report["arc_roles_missing"] == ["loop_seam"], (
        "generator tuketildi, dusen cekim kayboldu: "
        + repr(report["arc_roles_missing"]))
    assert report["degraded"] is True


# ── 3. NaN ve sonsuz sure ─────────────────────────────────────────────────────

def test_nan_duration_does_not_fake_a_quality_defect():
    """NaN bir OLCUM arizasidir, kalite kusuru degil.

    `nan <= x` daima False oldugu icin naif kod duration_in_band=False yazar ve
    saglam bir bolumu 'degraded' ilan eder. Olculemeyen sey None olmali.
    """
    report = _report(duration_s=float("nan"))
    assert report["duration_in_band"] is not False, (
        "NaN sure sahte kusur uretti")
    assert report["degraded"] is False
    assert not math.isnan(report["duration_s"]), "rapora NaN sizdi"


def test_infinite_duration_is_treated_as_unmeasured():
    report = _report(duration_s=float("inf"))
    assert report["duration_in_band"] is not False
    assert report["degraded"] is False


# ── 4. tekrarli ve bozuk dusus kaydi ──────────────────────────────────────────

def test_duplicate_dropped_shot_is_recorded_once():
    """Ayni cekim iki kez dusemez; rapor da iki kez yazmamali."""
    report = _report(dropped_shots=[2, 2])
    assert report["arc_roles_missing"] == ["episode_body"], repr(
        report["arc_roles_missing"])


def test_roles_follow_shot_order_not_list_order():
    report = _report(dropped_shots=[4, 1])
    assert report["arc_roles_missing"] == ["cold_open", "loop_seam"]


# ── 5. None asla degraded uretmez (sozlesmenin kalbi) ────────────────────────

@pytest.mark.parametrize("over", [
    {"duration_band": None},
    {"duration_band": "14-41"},
    {"duration_band": [41, 14]},
    {"duration_band": [True, 41]},
    {"duration_band": [14]},
    {"narration_expected": False, "narration_ok": False},
    {"duration_s": None},
    {"duration_s": "abc"},
])
def test_unmeasurable_inputs_never_mark_a_clean_episode_degraded(over):
    """Olculemeyen her sey None'a duser; saglam bolum kusurlu ilan EDILMEZ."""
    report = _report(**over)
    assert report["degraded"] is False, f"{over} -> {report}"


# ── 6. hicbir girdi patlatmaz ────────────────────────────────────────────────

@pytest.mark.parametrize("args", [
    (None, None),
    ([], []),
    ("abc", [1]),
    ([1, 2, 3, 4], "xyz"),
    ([1, 2, 3, 4], {4}),
    ((1, 2, 3, 4), (4,)),
    ([-3, -2, -1], [-1]),
])
def test_hostile_inputs_never_raise(args):
    shots, dropped = args
    report = episode_coherence_report(
        shots, dropped,
        narration_expected=True, narration_ok=False,
        duration_s=None, duration_band=None,
    )
    assert set(report) == {
        "loop_closed", "narration_delivered", "arc_roles_missing",
        "duration_s", "duration_in_band", "degraded",
    }


def test_single_shot_episode_last_is_loop_seam():
    report = _report(shot_numbers=[1], dropped_shots=[1], duration_s=6.0)
    assert report["arc_roles_missing"] == ["loop_seam"]
    assert report["loop_closed"] is False
