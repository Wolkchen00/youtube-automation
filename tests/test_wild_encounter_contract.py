"""Live contract for the wild-encounter lane (RF-PLAN-WILD-ENCOUNTER, SPM round 2).

Every other test in this cycle uses a synthetic bible, so a live switch could be
flipped back (music on, QC gate off, anchors off) while the suite stayed green.
This file pins the switches the Core Focus depends on, and the lane that
publishes automatically every day.

It SKIPS when the series folder is gone, so archiving the series retires this
contract instead of breaking the suite the way the 2026-09-10 archive did.
"""

from __future__ import annotations

import json
import pathlib

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SERIES_DIR = REPO_ROOT / "sentinal_ihsan" / "wild-encounter"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "wild-encounter.yml"

pytestmark = pytest.mark.skipif(
    not (SERIES_DIR / "bible.json").exists(),
    reason="wild-encounter arsive kaldirilmis: canli sozlesme emekli",
)


def _json(name: str) -> dict:
    return json.loads((SERIES_DIR / name).read_text(encoding="utf-8"))


def test_music_bed_is_off_and_mastering_still_targets_minus_14():
    bible = _json("bible.json")
    assert bible["music"] is False, "muzik yatagi geri acilmis"
    assert bible["series"]["master_lufs"] == -14


def test_raw_audio_review_stays_on_to_catch_model_generated_music():
    assert _json("bible.json")["series"]["qc"]["native_audio_review"] is True


def test_episode_anchors_and_continuity_gate_are_on():
    series_cfg = _json("bible.json")["series"]
    assert series_cfg["episode_anchors"] is True
    assert series_cfg["qc"]["require_continuity"] is True, "set kaymasi yine gozlem olur"


def test_qc_notes_point_at_the_shot_paragraph_and_carry_no_mechanism():
    notes = _json("bible.json")["series"]["qc"]["notes"]
    assert "THE BEAT OF EACH SHOT IS WRITTEN IN ITS OWN PROMPT" in notes
    lowered = notes.lower()
    for stale in ("hatch", "real outdoor location", "both shots", "music bed"):
        assert stale not in lowered, f"QC notu bayat ifade tasiyor: {stale}"


def test_shot_plan_is_the_single_beat_source():
    plan_lines = _json("series.json")["auto_replenish"]["shot_plan"]
    assert len(plan_lines) == 3
    for index, line in enumerate(plan_lines, start=1):
        assert line.startswith(f"SHOT {index},"), line[:40]


def test_art_style_describes_the_studio_format():
    art = _json("bible.json")["art_style"].lower()
    assert "behind-the-scenes" in art and "studio stage" in art
    assert "real outdoor location" not in art


def test_only_built_sets_are_offered_to_the_plan_writer():
    envs = {env["id"] for env in _json("bible.json")["environments"]}
    assert envs == {"jungle_set", "ocean_tank_set", "desert_ruins_set"}


def test_daily_lane_publishes_automatically_with_the_series_face_pinned():
    series = _json("series.json")
    assert series["status"] == "active"
    assert series["publish_mode"] == "auto"
    replenish_cfg = series["auto_replenish"]
    assert replenish_cfg["enabled"] is True
    assert replenish_cfg["required_characters"] == ["ihsan_field"]
    assert replenish_cfg["format_version"] == "plato-3x8"
    assert replenish_cfg["shots"] == 3 and replenish_cfg["shot_seconds"] == "8"


def test_published_episodes_are_recorded_so_the_lane_cannot_repeat_them():
    series = _json("series.json")
    published = {n for n, part in series["parts"].items() if part.get("status") == "published"}
    assert {"5", "6"} <= published
    assert series["next_part"] > max(int(n) for n in published)
    registry_parts = {entry["part"] for entry in _json("published.json")}
    assert {5, 6} <= registry_parts


def test_the_workflow_runs_this_slug_on_a_schedule():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "--series wild-encounter" in text
    assert "cron:" in text and "schedule:" in text
    assert "sentinal_ihsan/wild-encounter/published.json" in text
