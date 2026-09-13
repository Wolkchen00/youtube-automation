"""RF-PLAN-TEKPLAN10 Rock 1: çok çekimli davranışın altın kopyaları."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from series import replenish
from series.bible import Bible
from series.series_meta import SeriesMeta


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "rf_tekplan_golden"


def _meta(slug: str) -> SeriesMeta:
    return SeriesMeta({
        "slug": slug,
        "base_title": f"Golden {slug}",
        "logline": "A deterministic regression series.",
        "total_parts": 20,
        "next_part": 8,
        "status": "active",
        "publish_mode": "auto",
        "upload_profile": "test",
        "platforms": ["youtube"],
        "parts": {},
    })


def _bible(slug: str, *, chain_frames: bool, face_visible: bool = True) -> Bible:
    return Bible({
        "series": {
            "slug": slug,
            "title": f"Golden {slug}",
            "engine": "omni",
            "chain_frames": chain_frames,
            "face_visible": face_visible,
            "micro_trim": 0.25,
        },
        "art_style": "Vertical 9:16 photoreal footage with natural practical light.",
        "music": True,
        "music_style": "Sparse tactile percussion with a restrained low pulse.",
        "characters": [
            {"id": "ihsan_field", "name": "Ihsan", "character_id": "cid-ihsan"},
        ],
        "environments": [
            {"id": "jungle_set", "desc": "A dressed jungle set inside a film studio."},
            {"id": "kitchen_counter", "desc": "A worn stone counter in a lived-in kitchen."},
        ],
        "props": [],
    })


def _plato_case() -> tuple[SeriesMeta, Bible, dict, list[dict]]:
    cfg = {
        "enabled": True,
        "format_version": "plato-3x8",
        "shots": 3,
        "shot_seconds": "8",
        "shot_refs": True,
        "humans": "featured",
        "required_characters": ["ihsan_field"],
        "shot_plan": [
            "SHOT 1, THE THREAT ON SET. One giant animal faces exactly one man.",
            "SHOT 2, TAKEN INSIDE. The animal closes its jaws around the man.",
            "SHOT 3, THE PRACTICAL REVEAL. Crew open the jaws and the man exits.",
        ],
        "brief": "A fake behind-the-scenes creature shoot with a delayed practical reveal.",
    }
    card = {
        "name": "giant crocodile",
        "descriptor": (
            "a colossal olive crocodile four metres tall with rough scales dark eyes and ivory teeth"
        ),
        "environment": "jungle_set",
        "framing": "A locked-off studio camera observes the entire dressed set.",
        "anomaly_descriptor": "Crew hands pull the practical hinged jaws open for the final reveal.",
    }
    shots = [
        {
            "n": number,
            "duration": "8",
            "prompt": (
                f"The same colossal olive crocodile advances through the dressed set in beat {number}. "
                "Ambient sound only: footsteps, studio air handling and distant crew movement."
            ),
            "seed": None,
            "environment": "jungle_set",
            "characters": ["ihsan_field"],
        }
        for number in (1, 2, 3)
    ]
    episode = {
        "episode": {"number": 8, "title": "This GIANT CROCODILE Is NOT Real"},
        "synopsis": "A giant crocodile takes a man before the crew reveal the practical build.",
        "format_version": "plato-3x8",
        "object_card": card,
        "hook_shot": 2,
        "narration": "",
        "shots": shots,
    }
    return _meta("plato-golden"), _bible("plato-golden", chain_frames=True), cfg, [episode]


def _fixed_object_case() -> tuple[SeriesMeta, Bible, dict, list[dict]]:
    cfg = {
        "enabled": True,
        "format_version": "tek-obje-4x6",
        "shots": 4,
        "shot_seconds": "6",
        "humans": "featured",
        "narration": {"min_words": 20, "max_words": 28},
        "music_prompt": True,
        "brief": "One ordinary household object displays exactly one impossible property.",
    }
    episode = {
        "episode": {"number": 8, "title": "This SOAP BENDS LIGHT!"},
        "synopsis": "A bar of soap bends a bright ribbon of window light across a counter.",
        "format_version": "tek-obje-4x6",
        "object_card": {
            "name": "soap bar",
            "descriptor": "a palm-sized amber soap bar with cloudy edges and one deep diagonal groove",
            "environment": "kitchen_counter",
            "framing": "A fixed waist-high composition faces the worn stone counter.",
            "anomaly_descriptor": "A bright ribbon of light curves visibly through its translucent amber body.",
        },
        "hook_shot": 3,
        "narration": (
            "I held this ordinary soap beneath the window, and the daylight curved through it "
            "like a ribbon trapped inside glass."
        ),
        "music": (
            "Sparse dry wooden taps keep a slow pulse beneath a quiet sustained bass tone, "
            "leaving generous space for tactile room sound and movement."
        ),
        "shots": [
            {
                "n": number,
                "duration": "6",
                "prompt": f"Hands rotate the amber soap while the curved light ribbon shifts in beat {number}.",
                "seed": None,
                "environment": "kitchen_counter",
                "violation_observation": "The bright light ribbon visibly curves inside the amber soap.",
            }
            for number in (1, 2, 3, 4)
        ],
    }
    return (
        _meta("fixed-object-golden"),
        _bible("fixed-object-golden", chain_frames=True, face_visible=False),
        cfg,
        [episode],
    )


def _formatless_case() -> tuple[SeriesMeta, Bible, dict, list[dict]]:
    cfg = {
        "enabled": True,
        "shots": 3,
        "shot_seconds": "8",
        "brief": "Three distinct cinematic tableaux tell one compact visual story.",
    }
    episode = {
        "episode": {"number": 8, "title": "The Returning Light"},
        "synopsis": "A beam of sunrise moves from a window to an old photograph.",
        "hook_shot": 2,
        "narration": "",
        "shots": [
            {
                "n": number,
                "duration": "8",
                "prompt": f"Warm sunrise crosses the quiet room and reaches the photograph in tableau {number}.",
                "seed": None,
            }
            for number in (1, 2, 3)
        ],
    }
    return _meta("formatless-golden"), _bible("formatless-golden", chain_frames=False), cfg, [episode]


CASES = {
    "plato_3x8": _plato_case,
    "tek_obje_4x6": _fixed_object_case,
    "formatless_multishot": _formatless_case,
}


def _current_result(case_name: str) -> dict:
    meta, bible, cfg, episodes = CASES[case_name]()
    contents, system_instruction = replenish._build_prompt(
        meta, bible, cfg, start=8, batch=1, history=[]
    )
    errors = replenish._validate_batch(
        copy.deepcopy(episodes), bible, 8, 1, set(), cfg, history=[]
    )
    return {
        "contents": contents,
        "system_instruction": system_instruction,
        "validation_errors": errors,
    }


@pytest.mark.parametrize("case_name", CASES)
def test_multishot_prompt_and_validation_match_exact_golden(case_name: str):
    expected = json.loads(
        (FIXTURE_DIR / f"{case_name}.json").read_text(encoding="utf-8")
    )
    actual = _current_result(case_name)

    # Hash ya da alt dize değil: üç çıktı da tam metin olarak korunur.
    assert actual["contents"] == expected["contents"]
    assert actual["system_instruction"] == expected["system_instruction"]
    assert actual["validation_errors"] == expected["validation_errors"]
