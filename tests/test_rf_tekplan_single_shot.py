"""RF-PLAN-TEKPLAN10 Rock 2: tek çekimli Plato motor sözleşmesi."""

from __future__ import annotations

import copy

from series import replenish
from series.bible import Bible
from series.series_meta import SeriesMeta


SHOT_PLAN = (
    "ONE CONTINUOUS BEAT. The threat, the man taken into the mouth, the crew opening "
    "the jaws and the man's exit all occur in order."
)


def _bible() -> Bible:
    return Bible({
        "series": {
            "slug": "plato-single-proof",
            "title": "Plato Single Proof",
            "engine": "omni",
            "chain_frames": False,
        },
        "art_style": "Vertical 9:16 photoreal behind-the-scenes footage in clear studio air.",
        "music": False,
        "characters": [
            {"id": "ihsan_field", "name": "Ihsan", "character_id": "cid-ihsan"},
        ],
        "environments": [
            {"id": "desert_set", "desc": "A minimal sand island on a studio floor."},
        ],
        "props": [],
    })


def _cfg(**overrides) -> dict:
    cfg = {
        "enabled": True,
        "format_version": "plato-3x8",
        "shots": 1,
        "shot_seconds": "10",
        "shot_refs": True,
        "humans": "featured",
        "required_characters": ["ihsan_field"],
        "shot_plan": [SHOT_PLAN],
        "brief": "A single unbroken creature encounter with ambient set sound.",
    }
    cfg.update(overrides)
    return cfg


def _meta(cfg: dict) -> SeriesMeta:
    return SeriesMeta({
        "slug": "plato-single-proof",
        "base_title": "Plato Single Proof",
        "logline": "A practical creature encounter unfolds in one take.",
        "total_parts": 20,
        "next_part": 8,
        "status": "active",
        "auto_replenish": cfg,
        "parts": {},
    })


def _system(cfg: dict | None = None) -> str:
    cfg = cfg or _cfg()
    _contents, system = replenish._build_prompt(
        _meta(cfg), _bible(), cfg, start=8, batch=1, history=[]
    )
    return system


def _episode() -> dict:
    return {
        "episode": {"number": 8, "title": "This GIANT LION Is NOT Real"},
        "synopsis": "A giant lion takes Ihsan before the crew open its practical jaws.",
        "format_version": "plato-3x8",
        "object_card": {
            "name": "giant lion",
            "descriptor": (
                "a colossal tawny lion four metres tall with coarse fur amber eyes and ivory teeth"
            ),
            "environment": "desert_set",
            "framing": "A slow continuous push-in moves from the wide set toward the lion.",
            "anomaly_descriptor": "Crew hands pull the practical hinged jaws open in the final reveal.",
        },
        "hook_shot": 1,
        "narration": "",
        "shots": [{
            "n": 1,
            "duration": "10",
            "environment": "desert_set",
            "characters": ["ihsan_field"],
            "prompt": (
                "A colossal tawny lion threatens Ihsan, takes him into its mouth, and the crew rush "
                "forward. In the final seconds crew members pull the practical hinged jaws open and "
                "Ihsan steps out unharmed. Ambient sound only: footsteps on sand, studio air handling "
                "and crew movement."
            ),
            "seed": None,
        }],
    }


def test_single_shot_plato_batch_is_accepted_and_keeps_structural_validation():
    cfg = _cfg()
    episodes = [_episode()]

    assert replenish._validate_batch(
        episodes, _bible(), 8, 1, set(), cfg, history=[]
    ) == []
    assert len(episodes[0]["shots"]) == 1
    assert episodes[0]["format_version"] == "plato-3x8"
    assert episodes[0]["object_card"]["name"] == "giant lion"

    wrong_format = _episode()
    wrong_format["format_version"] = "another-format"
    errors = replenish._validate_batch(
        [wrong_format], _bible(), 8, 1, set(), cfg, history=[]
    )
    assert any("format_version tam 'plato-3x8' olmalı" in error for error in errors)


def test_single_shot_featured_header_uses_ambient_sound_and_keeps_one_take():
    system = _system()

    assert "ONE single unbroken shot of exactly 10 seconds" in system
    assert "ambient natural\nsound from the set only" in system
    assert "the musical score is the only sound" not in system


def test_single_shot_plato_prompt_uses_blue_screen_and_slow_push_in():
    system = _system()
    lowered = system.lower()

    assert "blue screen" in lowered
    assert "slow continuous push-in" in lowered
    assert "haze" not in lowered
    assert "locked-off" not in lowered
    assert "shot 3" not in lowered


def test_single_shot_plato_has_its_own_shape_and_no_fixed_object_instructions():
    system = _system()

    assert '"name": "<real recognisable giant animal name>"' in system
    assert '"environment": "<ref id, optional>"' in system
    assert "violation_observation" not in system
    assert "state_carry" not in system
    assert "same everyday surface" not in system
    assert "natural lived-in unlabeled surfaces" not in system


def test_single_shot_plato_preserves_ordered_final_seconds_reveal():
    system = _system().lower()

    threat = system.index("threatened man")
    mouth = system.index("takes him into its mouth", threat)
    opened = system.index("crew open the jaws", mouth)
    exits = system.index("he exits", opened)
    final_seconds = system.index("final seconds", exits)
    assert threat < mouth < opened < exits < final_seconds


def test_single_shot_plato_final_system_prompt_has_no_conflicting_promises():
    system = " ".join(_system().lower().split())

    assert "voice is added later as narration" not in system
    assert "no withheld reveal" not in system
    assert "no closing gesture" not in system


def test_generic_non_plato_single_shot_arc_is_unchanged():
    cfg = _cfg(format_version="", shot_refs=False, humans="", required_characters=[])
    system = " ".join(_system(cfg).lower().split())

    assert "no withheld reveal" in system
    assert "no closing gesture" in system
    assert "locked camera that never pans, tilts, orbits or follows" in system


def test_multishot_plato_still_rejects_early_construction_language():
    cfg = _cfg(
        shots=3,
        shot_seconds="8",
        shot_plan=["Threat", "Taken", "Reveal"],
    )
    episode = _episode()
    episode["shots"] = [copy.deepcopy(episode["shots"][0]) for _ in range(3)]
    for number, shot in enumerate(episode["shots"], start=1):
        shot["n"] = number
        shot["duration"] = "8"
    episode["shots"][0]["prompt"] += " The animatronic mechanism rests beside the crew."
    errors = replenish._validate_batch(
        [episode], _bible(), 8, 1, set(), cfg, history=[]
    )

    assert any("yapım dili" in error and "çekim 1" in error for error in errors)
