"""1 Ekim 2026: baslik kapisi yalniz AYNI hayvan adini reddediyordu.

Kuyrukta GIANT ALLIGATOR (part20) ve GIANT CAIMAN (part25) vardi; ikisi de
part06 dev timsahla izleyici gozunde ayni video. Benzer-hayvan grubu kullanilmissa
o gruptan yeni hayvan yazilamaz. Yazar promptu ve dogrulayici ayni tabloyu okur.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from series import replenish  # noqa: E402
from series.bible import Bible  # noqa: E402

SERIES_DIR = ROOT / "sentinal_ihsan" / "wild-encounter"


def _meta():
    return json.loads((SERIES_DIR / "series.json").read_text(encoding="utf-8"))


def _cfg():
    return _meta()["auto_replenish"]


def _plans():
    out = {}
    for path in sorted((SERIES_DIR / "plans").glob("part*.json")):
        out[int(path.stem[4:])] = json.loads(path.read_text(encoding="utf-8"))
    return out


def _history(plans):
    rows = []
    for number, plan in sorted(plans.items()):
        title = plan["episode"]["title"]
        rows.append({"n": number, "title": title, "synopsis": plan.get("synopsis", ""),
                     "seed_id": plan.get("seed_id"), "family": plan.get("family", ""),
                     "creature": replenish.creature_name(plan, title)})
    return rows


@pytest.mark.parametrize("name, group", [
    ("giant alligator", "crocodilian"),
    ("giant caiman", "crocodilian"),
    ("giant crocodile head practical prop", "crocodilian"),
    ("giant grizzly bear", "bear"),
    ("giant tiger shark", "shark"),
    ("giant tiger", "tiger"),
    ("giant sea lion", "seal"),
    ("giant mountain lion", "cougar"),
    ("giant alligator snapping turtle", "turtle"),
    ("giant eagle owl", "owl"),
    ("giant rhinoceros beetle", "beetle"),
    ("giant lionfish", None),
    ("giant chameleon", None),
])
def test_longest_phrase_decides_the_group(name, group):
    assert replenish.lookalike_group(name, _cfg()) == group


def test_title_is_the_fallback_when_there_is_no_object_card():
    assert replenish.creature_name({}, "This GIANT ALLIGATOR Is NOT Real") == "ALLIGATOR"
    assert replenish.lookalike_group("ALLIGATOR", _cfg()) == "crocodilian"


def test_config_rejects_a_phrase_in_two_groups():
    errors = replenish.validate_replenish_config(
        {"lookalike_groups": {"a": ["crocodile"], "b": ["Crocodile"]}})
    assert any("iki grupta" in error for error in errors)


def test_series_config_itself_is_valid():
    assert replenish._lookalike_config_errors(_cfg()["lookalike_groups"]) == []


def _batch_errors(creature: str, title: str) -> list[str]:
    plans = _plans()
    last = max(plans)
    episode = copy.deepcopy(plans[last])
    episode["episode"] = {"number": last + 1, "title": title}
    episode["object_card"]["name"] = creature
    bible = Bible(json.loads((SERIES_DIR / "bible.json").read_text(encoding="utf-8")))
    history = _history(plans)
    titles = {replenish._norm_title(row["title"]) for row in history}
    return replenish._validate_batch([episode], bible, last + 1, 1, titles,
                                     _cfg(), history)


def test_validator_rejects_a_new_crocodilian():
    errors = _batch_errors("giant gharial", "This GIANT GHARIAL Is NOT Real")
    assert any("benzer hayvan" in error and "crocodilian" in error for error in errors)


def test_validator_lets_an_unused_group_through():
    errors = _batch_errors("giant hippo", "This GIANT HIPPO Is NOT Real")
    assert not any("benzer hayvan" in error for error in errors)


def test_prompt_lists_the_used_groups_for_the_writer():
    plans = _plans()
    used = replenish.used_lookalike_groups(_history(plans), _cfg())
    assert {"crocodilian", "bear", "snake", "great ape"} <= set(used)


def test_live_queue_has_no_lookalike_repeat():
    """Regresyon kilidi: kuyruktaki her plan ONCEKI planlarin gruplarindan farkli."""
    meta = _meta()
    cfg = meta["auto_replenish"]
    plans = _plans()
    for number in range(int(meta["next_part"]), int(meta["total_parts"]) + 1):
        earlier = {n: p for n, p in plans.items() if n < number}
        used = replenish.used_lookalike_groups(_history(earlier), cfg)
        plan = plans[number]
        group = replenish.lookalike_group(
            replenish.creature_name(plan, plan["episode"]["title"]), cfg)
        assert group is None or group not in used, (number, group, used.get(group))
