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
    # Tek plan sozlesmesi: vurus, promptun "ONE CONTINUOUS" paragrafinda yazili.
    assert "ONE SINGLE UNCUT SHOT" in notes
    assert "ONE CONTINUOUS" in notes
    lowered = notes.lower()
    for stale in ("hatch", "real outdoor location", "both shots", "music bed",
                  "all three shots", "shot 1", "shot 2", "shot 3"):
        assert stale not in lowered, f"QC notu bayat ifade tasiyor: {stale}"
    # 13 Eylul olcumu: sis kaybedenlerde var, kazananlarda yok. QC notu artik
    # sisi BEKLENEN set ogesi olarak saymamali ve perde MAVI olmali.
    assert "haze are EXPECTED" not in notes
    assert "green screen" not in lowered
    assert "blue screen" in lowered
    assert "the air is clear" in lowered


def test_shot_plan_is_the_single_beat_source():
    plan_lines = _json("series.json")["auto_replenish"]["shot_plan"]
    # Tek kesintisiz cekim: tek vurus paragrafi, uc vurus da onun icinde.
    assert len(plan_lines) == 1
    tek = plan_lines[0]
    assert tek.startswith("ONE CONTINUOUS TAKE, NO CUTS."), tek[:48]
    for vurus in ("jaws open wide", "out of sight", "push its", "climbs out"):
        assert vurus in tek, f"vurus eksik: {vurus}"
    # 20 Eylul 2026: "pushes in slowly from the wide establishing frame"
    # KALDIRILDI. Olcum: referans reel'lerde karenin %4-13'u keskin, bizim
    # uc bolumumuzde %32-42; fark sikistirma degil OPTIK (ep09 referans bit
    # hizina indirilince %42,6 ile degismedi). Genis acilis her seyi ayni
    # uzakliga koyuyor, yani odaklanacak derinlik BIRAKMIYOR.
    assert "wide establishing" not in tek.lower()
    for optik in ("low and close", "shallow depth of field", "out of focus",
                  "motion blur"):
        assert optik in tek.lower(), f"kadraj sozlesmesi eksik: {optik}"
    dusuk = tek.lower()
    assert "blue screen" in dusuk
    for yasak in ("haze", "fog", "green screen"):
        assert yasak not in dusuk, f"shot_plan yasak terim tasiyor: {yasak}"


def test_art_style_describes_the_studio_format():
    art = _json("bible.json")["art_style"].lower()
    assert "behind-the-scenes" in art and "studio stage" in art
    assert "real outdoor location" not in art
    # 13 Eylul olcumu: tek kesintisiz plan, yavas push-in, MAVI perde, temiz hava.
    assert "one continuous uncut shot" in art
    assert "pushes in slowly" in art
    assert "blue screen" in art
    assert "the air is clear" in art
    for yasak in ("haze", "fog", "green screen"):
        assert yasak not in art, f"art_style yasak terim tasiyor: {yasak}"


def test_only_built_sets_are_offered_to_the_plan_writer():
    envs = {env["id"] for env in _json("bible.json")["environments"]}
    assert envs == {"jungle_set", "ocean_tank_set", "desert_ruins_set"}


def test_full_frame_creature_still_feeds_the_production_gate():
    """Yaratık kareyi doldurur AMA yapım öğesi kareden çıkmaz.

    20 Eylul 2026 Ihsan karari: yaratik kareyi TAMAMEN doldursun (referans
    DcYBduSzf-A kalibi). Bu tek basina bible qc.notes'taki kapiyla celisirdi:
    "THE PRODUCTION MUST BE VISIBLE ... A clip in which no production element
    is visible, so that it reads as location footage, is a FAIL." Kapi klibi
    kredi HARCANDIKTAN SONRA reddeder, yani celiski dogrudan karanlik gun
    demektir. Referansin kendisi cozumu gosteriyor: timsah kafasi tum kareyi
    kapliyor ve sag altta bir ekipman kasasi duruyor.

    Bu test iki ifadenin birlikte durdugunu kilitler. Biri silinirse kirmizi
    yanar, sessizce kredi yakmaz.
    """
    tek = _json("series.json")["auto_replenish"]["shot_plan"][0].lower()
    assert "fills the whole frame" in tek
    assert "production element" in tek, "yapim ogesi kareden cikarilmis"
    assert "blue screen" in tek, "ikinci yapim ogesi kareden cikarilmis"
    notes = _json("bible.json")["series"]["qc"]["notes"]
    assert "THE PRODUCTION MUST BE VISIBLE" in notes, (
        "kapi metni degismis, shot_plan ile birlikte gozden gecir"
    )


def test_daily_lane_publishes_the_single_shot_format_automatically():
    """13 Eylul: tek plan 10 sn formati CANLI.

    Sira: format cevrildi -> seri gecici PAUSED -> part08 (dev anakonda) elle
    uretildi -> Ihsan izleyip onayladi -> 3 platforma yayinlandi -> ACTIVE.
    Cron dosyasina hic dokunulmadi; yayini durduran ve acan sey status alani.
    """
    series = _json("series.json")
    # "completed" MAKINE durumudur: son bolum yayinlaninca yazilir ve bir
    # sonraki kosuda replenish onu "active"e geri cevirir (replenish.py:2226).
    # Testin yalniz "active" kabul etmesi, her son-bolum gununde yanlis
    # alarm uretiyordu. Insan karari olan "paused"/"draft" HALA reddedilir.
    assert series["status"] in ("active", "completed"), series["status"]
    assert series["publish_mode"] == "auto"
    replenish_cfg = series["auto_replenish"]
    assert replenish_cfg["enabled"] is True
    assert replenish_cfg["required_characters"] == ["ihsan_field"]
    # Format anahtari DEGISMEDI: davranis anahtari, sadece etiket degil.
    assert replenish_cfg["format_version"] == "plato-3x8"
    assert replenish_cfg["shots"] == 1 and replenish_cfg["shot_seconds"] == "10"


def test_single_shot_geometry_is_locked_in_the_bible():
    """Tek plan formatinin olculmus geometrisi."""
    series_cfg = _json("bible.json")["series"]
    assert series_cfg["duration_band"] == [9, 11]
    assert series_cfg["chain_frames"] is False, "tek cekimde zincirlenecek cekim yok"
    assert series_cfg["micro_trim"] == 0, "tek klipte uc kirpmasi 10 sn'yi kisaltir"
    assert series_cfg["qc"]["min_shots"] == 1
    # scene_cut_fail hala OLU bir ayar (critic.py her zaman gated=False yaziyor);
    # gercek kapi ayri bir is olarak RF-ISSUES'ta duruyor.
    assert series_cfg["qc"]["scene_cut_fail"] is False


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
