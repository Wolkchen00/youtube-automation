"""plato-3x8 auto-replenish (RF-PLAN-WILD-ENCOUNTER, ROCK 5).

Measured on 2026-09-11 with the live config: all six Gemini attempts failed
because the validator demanded "6"-second shots from an 8-second format, and
nothing guaranteed the series face in every shot. These tests pin the fixes
with a synthetic bible; no Gemini call, no live channel config.
"""

from __future__ import annotations

import copy

from series import replenish
from series.bible import Bible
from series.series_meta import SeriesMeta

SHOT_PLAN = [
    "SHOT 1, THE THREAT ON SET. One giant creature faces exactly one man on a built set.",
    "SHOT 2, TAKEN INSIDE. The creature's jaws close over exactly one man.",
    "SHOT 3, THE PRACTICAL REVEAL. Crew hands push the jaws open and the man climbs out.",
]
FAMILIES = ["predator-armour", "aquatic-land", "scale-giant"]
PARAGRAPH = chr(10) * 2  # blank line between the beat line and the shot details


def _bible() -> Bible:
    return Bible({
        "series": {"slug": "plato-replenish-proof", "title": "Plato Proof",
                   "engine": "omni", "chain_frames": True},
        "art_style": "Vertical 9:16 photoreal behind-the-scenes footage of a film shoot.",
        "music": False,
        "characters": [
            {"id": "ihsan_field", "name": "Ihsan", "character_id": "cid-ihsan"},
            {"id": "crew_lead", "name": "Crew Lead"},
        ],
        "environments": [{"id": "jungle_set", "desc": "A built jungle set in a film studio."}],
        "props": [],
    })


def _cfg(**overrides) -> dict:
    cfg = {
        "enabled": True,
        "format_version": "plato-3x8",
        "shots": 3,
        "shot_seconds": "8",
        "shot_refs": True,
        "humans": "featured",
        "families": list(FAMILIES),
        "shot_plan": list(SHOT_PLAN),
        "required_characters": ["ihsan_field"],
        "title_patterns": [{
            "regex": "This [A-Z][A-Z]+(?: [A-Z]+){0,2} Is NOT Real",
            "families": list(FAMILIES),
        }],
        "brief": "fake behind-the-scenes creature shoot",
    }
    cfg.update(overrides)
    return cfg


def _episode(n: int = 7, *, duration: str = "8", characters=None,
             title: str = "This GIANT PRAYING MANTIS Is NOT Real") -> dict:
    shots = []
    for k in (1, 2, 3):
        shot = {
            "n": k,
            "duration": duration,
            "environment": "jungle_set",
            "prompt": (
                f"Shot {k} detail: a colossal green praying mantis prop with glossy compound "
                "eyes and spiked forelegs looms over the man on the dressed jungle set. "
                "Ambient sound only: dripping water and studio air handling."
            ),
            "seed": None,
        }
        if characters is not None:
            shot["characters"] = list(characters)
        shots.append(shot)
    return {
        "episode": {"number": n, "title": title},
        "synopsis": "A giant mantis prop takes a performer into its jaws on a jungle set.",
        "format_version": "plato-3x8",
        "family": "scale-giant",
        "hook_shot": 2,
        "object_card": {
            "name": "giant praying mantis practical prop",
            "descriptor": "a colossal bright green praying mantis prop, three metres tall, with "
                          "glossy compound eyes and spiked forelegs",
            "environment": "jungle_set",
            "framing": "A locked-off studio camera behind two camera operators.",
            "anomaly_descriptor": "The crew pull the hinged mandibles apart by hand.",
        },
        "narration": "",
        "shots": shots,
    }


def _validate(episode: dict, cfg: dict | None = None) -> list[str]:
    """Validate one episode; the normalized plan replaces it IN the batch list, so the
    caller's dict is refreshed from that list afterwards."""
    batch = [episode]
    errors = replenish._validate_batch(
        batch, _bible(), 7, 1, set(), cfg or _cfg(), history=[], calibration=None,
    )
    if batch[0] is not episode:
        episode.clear()
        episode.update(batch[0])
    return errors


def test_eight_second_plato_shots_are_accepted():
    episode = _episode()
    assert _validate(episode) == []
    assert [shot["duration"] for shot in episode["shots"]] == ["8", "8", "8"]


def test_wrong_duration_names_the_configured_value_not_six():
    errors = _validate(_episode(duration="6"))
    duration_errors = [e for e in errors if "süre tam" in e]
    assert duration_errors, errors
    assert all("'8'" in e for e in duration_errors), duration_errors
    assert not any("'6'" in e for e in duration_errors), duration_errors


def test_series_face_is_injected_when_gemini_omits_characters():
    episode = _episode(characters=None)
    assert _validate(episode) == []
    assert [shot["characters"] for shot in episode["shots"]] == [["ihsan_field"]] * 3


def test_required_character_comes_first_and_other_valid_characters_survive():
    episode = _episode(characters=["crew_lead", "ghost_id", "ihsan_field"])
    assert _validate(episode) == []
    for shot in episode["shots"]:
        assert shot["characters"] == ["ihsan_field", "crew_lead"]


def test_required_character_missing_from_bible_is_a_config_error():
    errors = _validate(_episode(), _cfg(required_characters=["nobody"]))
    assert errors and "required_characters bible'da yok" in errors[0]


def test_required_characters_must_be_a_non_empty_id_list():
    for bad in ("ihsan_field", [], [""], [3]):
        errors = replenish.validate_replenish_config(_cfg(required_characters=bad))
        assert any("required_characters" in e for e in errors), (bad, errors)


def test_series_without_required_characters_is_unchanged():
    cfg = _cfg()
    del cfg["required_characters"]
    episode = _episode(characters=None)
    assert _validate(episode, cfg) == []
    assert all("characters" not in shot for shot in episode["shots"])


def test_three_word_creature_title_fits_the_pattern_and_four_words_do_not():
    assert _validate(_episode(title="This GIANT PRAYING MANTIS Is NOT Real")) == []
    errors = _validate(_episode(title="This VERY GIANT PRAYING MANTIS Is NOT Real"))
    assert any("title_patterns" in e for e in errors), errors


def _system_prompt(cfg: dict) -> str:
    meta = SeriesMeta({
        "slug": "plato-replenish-proof", "base_title": "Plato Proof", "total_parts": 6,
        "next_part": 7, "status": "active", "publish_mode": "auto",
        "upload_profile": "p", "platforms": ["youtube"], "parts": {},
        "auto_replenish": cfg,
    })
    _contents, system = replenish._build_prompt(meta, _bible(), cfg, 7, 1, [])
    return system


def test_echoed_beat_line_is_replaced_not_duplicated():
    episode = _episode()
    # Gemini echoed a truncated copy of the beat line (measured on part07 shot 1).
    echoed = SHOT_PLAN[0][:60]
    episode["shots"][0]["prompt"] = echoed + PARAGRAPH + episode["shots"][0]["prompt"]
    assert _validate(episode) == []
    first = episode["shots"][0]["prompt"]
    assert first.startswith(SHOT_PLAN[0] + PARAGRAPH)
    assert first.count("SHOT 1,") == 1


def test_unrelated_first_paragraph_is_kept():
    episode = _episode()
    body = "A wide dressed jungle set." + PARAGRAPH + episode["shots"][0]["prompt"]
    episode["shots"][0]["prompt"] = body
    assert _validate(episode) == []
    assert "A wide dressed jungle set." in episode["shots"][0]["prompt"]


def test_plato_prompt_uses_the_creature_rule():
    system = _system_prompt(_cfg())
    assert "CREATURE_CARD" in system
    assert "revealed only in shot 3" in system
    assert "natural anatomy" in system and "natural habitat" in system
    assert "FORBIDDEN WORDS" in system
    # the other formats' rule would spend the reveal in shot 1
    assert "copy THAT verbatim into every shot prompt too" not in system
    assert "SHOT 1 ONSET" not in system


def test_other_formatted_series_keep_their_old_object_rule():
    cfg = _cfg(format_version="tanik-2x8")
    system = _system_prompt(cfg)
    assert "CREATURE_CARD" not in system
    assert "copy THAT verbatim into every shot prompt too" in system
    assert "SHOT 1 ONSET" in system


def test_plato_rule_does_not_leak_into_the_config_it_was_built_from():
    cfg = _cfg()
    before = copy.deepcopy(cfg)
    _system_prompt(cfg)
    assert cfg == before
