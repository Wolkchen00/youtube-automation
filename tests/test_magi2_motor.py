"""MAGI-2 motoru: sure, maliyet tahmini ve zaman araligi kapisi (27 Kasim 2026)."""
import json
from pathlib import Path

import pytest

from core import cost_tracker
from series.replenish import magi2_time_segments, valid_durations, validate_plan_against_config
from series.shots import validate_visual_duration

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def _eski_series_data_kokunu_izole_et():
    """Yalniz metadata okunur; yazilabilir seri verisi fixture'i gerekmez."""


def test_magi2_sureleri_4_30():
    assert valid_durations("magi2") == tuple(str(s) for s in range(4, 31))
    assert validate_visual_duration("15", "magi2") == "15"
    assert validate_visual_duration("40", "magi2") == "30"
    assert validate_visual_duration("2", "magi2") == "4"


def test_magi2_tahmini_gercek_fiyatin_ustunde():
    for saniye in (8, 15, 30):
        tahmin = cost_tracker.conservative_credit_estimate("main_shot", "magi2", str(saniye))
        assert tahmin is not None and tahmin >= 17.6 * saniye
    assert cost_tracker.conservative_credit_estimate("qc_regen", "magi-2/image-to-video", "15") is not None


@pytest.mark.parametrize("metin", [
    "Seconds 0-4 are calm", "from four to six seconds the camera", "during seconds six to eight",
    "[2.0-4.0] she sits", "Shot 2: the storm", "at second 6 the wave", "through seconds 1-5",
])
def test_zaman_araligi_yakalanir(metin):
    assert magi2_time_segments(metin)


@pytest.mark.parametrize("metin", [
    "A single continuous 15-second first-person flight", "in the final moments", "an 8-second shot",
    "within seconds the flood spreads",
])
def test_temiz_metin_gecer(metin):
    assert magi2_time_segments(metin) == []


@pytest.mark.parametrize("slug", ["one-variable", "flythrough"])
def test_galactic_magi2_kuyrugu_temiz(slug):
    folder = ROOT / "galactic_experience" / slug
    bible = json.loads((folder / "bible.json").read_text(encoding="utf-8"))
    meta = json.loads((folder / "series.json").read_text(encoding="utf-8"))
    assert bible["series"]["engine"] == "magi2"
    cfg = meta["auto_replenish"]
    assert magi2_time_segments(bible["art_style"]) == []
    assert all(magi2_time_segments(line) == [] for line in cfg["shot_plan"])
    for part in range(meta["next_part"], meta["total_parts"] + 1):
        plan_path = folder / "plans" / f"part{part:02d}.json"
        if not plan_path.exists():
            plan_path = folder / "plans" / f"part{part}.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        assert validate_plan_against_config(plan, cfg, engine="magi2") == [], plan_path.name
