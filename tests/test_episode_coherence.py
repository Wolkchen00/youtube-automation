"""
episode_coherence_report fonksiyonu icin pytest testleri.
"""

import pytest
from series.episode_coherence import episode_coherence_report


def test_four_shots_nothing_dropped_narration_ok_duration_in_band():
    """4 shot, hic dusmemis, anlatim bekleniyor ve tamam, sure band icinde."""
    result = episode_coherence_report(
        shot_numbers=[1, 2, 3, 4],
        dropped_shots=[],
        narration_expected=True,
        narration_ok=True,
        duration_s=30.0,
        duration_band=[20, 40],
    )
    assert result["loop_closed"] is True
    assert result["narration_delivered"] is True
    assert result["arc_roles_missing"] == []
    assert result["duration_s"] == 30.0
    assert result["duration_in_band"] is True
    assert result["degraded"] is False


def test_shot_4_of_4_dropped():
    """4 shot, son shot (4) dusmus -> loop_closed False, loop_seam eksik, degraded True."""
    result = episode_coherence_report(
        shot_numbers=[1, 2, 3, 4],
        dropped_shots=[4],
        narration_expected=True,
        narration_ok=True,
        duration_s=30.0,
        duration_band=[20, 40],
    )
    assert result["loop_closed"] is False
    assert "loop_seam" in result["arc_roles_missing"]
    assert result["degraded"] is True


def test_shot_1_of_4_dropped():
    """4 shot, ilk shot (1) dusmus -> cold_open eksik, loop_closed True."""
    result = episode_coherence_report(
        shot_numbers=[1, 2, 3, 4],
        dropped_shots=[1],
        narration_expected=True,
        narration_ok=True,
        duration_s=30.0,
        duration_band=[20, 40],
    )
    assert result["loop_closed"] is True
    assert "cold_open" in result["arc_roles_missing"]


def test_shot_2_of_4_dropped():
    """4 shot, orta shot (2) dusmus -> episode_body eksik."""
    result = episode_coherence_report(
        shot_numbers=[1, 2, 3, 4],
        dropped_shots=[2],
        narration_expected=True,
        narration_ok=True,
        duration_s=30.0,
        duration_band=[20, 40],
    )
    assert "episode_body" in result["arc_roles_missing"]


def test_narration_expected_but_not_ok():
    """Anlatim bekleniyor ama yapilmamis -> narration_delivered False, degraded True."""
    result = episode_coherence_report(
        shot_numbers=[1, 2, 3, 4],
        dropped_shots=[],
        narration_expected=True,
        narration_ok=False,
        duration_s=30.0,
        duration_band=[20, 40],
    )
    assert result["narration_delivered"] is False
    assert result["degraded"] is True


def test_narration_not_expected():
    """Anlatim beklenmiyor -> narration_delivered None, hicbir sey kotu degilse degraded False."""
    result = episode_coherence_report(
        shot_numbers=[1, 2, 3, 4],
        dropped_shots=[],
        narration_expected=False,
        narration_ok=False,
        duration_s=30.0,
        duration_band=[20, 40],
    )
    assert result["narration_delivered"] is None
    assert result["degraded"] is False


def test_duration_outside_band():
    """Sure band disinda -> duration_in_band False, degraded True."""
    result = episode_coherence_report(
        shot_numbers=[1, 2, 3, 4],
        dropped_shots=[],
        narration_expected=True,
        narration_ok=True,
        duration_s=50.0,
        duration_band=[20, 40],
    )
    assert result["duration_in_band"] is False
    assert result["degraded"] is True


def test_duration_band_none():
    """duration_band None -> duration_in_band None, degraded False."""
    result = episode_coherence_report(
        shot_numbers=[1, 2, 3, 4],
        dropped_shots=[],
        narration_expected=True,
        narration_ok=True,
        duration_s=30.0,
        duration_band=None,
    )
    assert result["duration_in_band"] is None
    assert result["degraded"] is False


def test_invalid_band_reversed_and_bool():
    """Gecersiz band: ters sirali [41, 14] ve bool iceren band -> duration_in_band None, degraded False."""
    # Ters sirali band
    result1 = episode_coherence_report(
        shot_numbers=[1, 2, 3, 4],
        dropped_shots=[],
        narration_expected=True,
        narration_ok=True,
        duration_s=30.0,
        duration_band=[41, 14],
    )
    assert result1["duration_in_band"] is None
    assert result1["degraded"] is False

    # Bool iceren band
    result2 = episode_coherence_report(
        shot_numbers=[1, 2, 3, 4],
        dropped_shots=[],
        narration_expected=True,
        narration_ok=True,
        duration_s=30.0,
        duration_band=[True, 40],
    )
    assert result2["duration_in_band"] is None
    assert result2["degraded"] is False


def test_duration_s_none():
    """duration_s None -> rapor duration_s 0.0."""
    result = episode_coherence_report(
        shot_numbers=[1, 2, 3, 4],
        dropped_shots=[],
        narration_expected=True,
        narration_ok=True,
        duration_s=None,
        duration_band=[20, 40],
    )
    assert result["duration_s"] == 0.0


def test_dropped_not_in_shot_numbers_ignored():
    """shot_numbers icinde olmayan dusen shot sayilmaz."""
    result = episode_coherence_report(
        shot_numbers=[1, 2, 3, 4],
        dropped_shots=[5, 99],
        narration_expected=True,
        narration_ok=True,
        duration_s=30.0,
        duration_band=[20, 40],
    )
    assert result["arc_roles_missing"] == []
    assert result["loop_closed"] is True


def test_hostile_input_no_raise():
    """Kotu girdiler hata firlatmaz: None, string, bool."""
    result = episode_coherence_report(
        shot_numbers=None,
        dropped_shots=None,
        narration_expected=True,
        narration_ok=True,
        duration_s="abc",
        duration_band="14-41",
    )
    # Hata firlatmamis olmali, guvenli degerler donmeli
    assert result["loop_closed"] is False
    assert result["narration_delivered"] is True
    assert result["arc_roles_missing"] == []
    assert result["duration_s"] == 0.0
    assert result["duration_in_band"] is None
    assert result["degraded"] is True  # loop_closed False oldugu icin


def test_multiple_drops_sorted_by_shot_number():
    """Coklu dusme shot numarasina gore sirali roller uretir."""
    result = episode_coherence_report(
        shot_numbers=[1, 2, 3, 4, 5],
        dropped_shots=[4, 2, 5],
        narration_expected=True,
        narration_ok=True,
        duration_s=30.0,
        duration_band=[20, 40],
    )
    # Sirali: 2 -> episode_body, 4 -> episode_body, 5 -> loop_seam
    assert result["arc_roles_missing"] == ["episode_body", "episode_body", "loop_seam"]
    assert result["loop_closed"] is False  # son shot (5) dusmus


if __name__ == "__main__":
    pytest.main([__file__, "-v"])