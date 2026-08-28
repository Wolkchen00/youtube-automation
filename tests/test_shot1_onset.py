import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from series import replenish
from series.bible import Bible
from series.shots import TEK_OBJE_FORMAT, validate_plan
from tools import plan_lint


DESCRIPTOR = (
    "A rectangular bar of light pink soap with smooth rounded edges and one faint "
    "brand imprint on top"
)
ANOMALY = (
    "glass-hard soap with sharp conchoidal fracture edges and glossy translucent "
    "shards catching hard specular light"
)
FRAMING = "The fixed close view holds the sink basin at one unchanging angle."
ENVIRONMENT = "bathroom_sink"
OLD_SHOT1 = (
    "Hands hold the bar under running water; the soap stays perfectly rigid and "
    "begins to crack like glass."
)
FIXED_SHOT1 = (
    "The bar is already split along a bright conchoidal fracture; its glassy "
    "translucent edge throws hard specular glints under the water while the broken "
    "face holds a mirror-smooth shine and water beads roll off the sharp facets."
)


def bible_data(slug="onset-test"):
    return {
        "series": {"slug": slug, "aspect_ratio": "9:16", "resolution": "1080p"},
        "art_style": "",
        "characters": [],
        "environments": [{"id": ENVIRONMENT, "desc": "A lived-in bathroom sink."}],
        "props": [],
    }


def plan_with_actions(actions=None, *, format_version=TEK_OBJE_FORMAT):
    actions = actions or [
        FIXED_SHOT1,
        "Hands tap the wet bar and a clean translucent shard breaks free.",
        "Hands stack the sharp glassy shards along the ceramic sink edge.",
        "Hands lift the largest section while the wet facets keep shining.",
    ]
    shots = [
        {
            "n": number,
            "duration": "6",
            "prompt": f"{DESCRIPTOR}. {ANOMALY}. {FRAMING} {action}",
            "environment": ENVIRONMENT,
        }
        for number, action in enumerate(actions, start=1)
    ]
    return {
        "episode": {"number": 1, "title": "Glass Soap"},
        "format_version": format_version,
        "object_card": {
            "name": "bar of soap",
            "descriptor": DESCRIPTOR,
            "environment": ENVIRONMENT,
            "framing": FRAMING,
            "anomaly_descriptor": ANOMALY,
        },
        "shots": shots,
    }


def onset_errors(plan):
    result = validate_plan(plan, Bible(bible_data()))
    return [error for error in result["errors"] if "BAŞLATIYOR" in error]


def test_old_part23_shot1_is_rejected_and_fixed_real_text_is_clean():
    old = plan_with_actions([
        OLD_SHOT1,
        "Hands tap the wet bar and a clean translucent shard breaks free.",
        "Hands stack the sharp glassy shards along the ceramic sink edge.",
        "Hands lift the largest section while the wet facets keep shining.",
    ])
    errors = onset_errors(old)
    assert len(errors) == 1
    assert "'begins to'" in errors[0]
    assert onset_errors(plan_with_actions()) == []


def test_legacy_plan_with_same_text_is_unchanged():
    legacy = plan_with_actions([OLD_SHOT1] * 4, format_version=None)
    assert onset_errors(legacy) == []


def test_onset_language_is_allowed_in_shots_two_through_four():
    plan = plan_with_actions([
        FIXED_SHOT1,
        "The wet shard begins to bend between two fingers.",
        "The fracture begins to branch across the rigid face.",
        "The largest shard begins to settle beside the bar.",
    ])
    assert onset_errors(plan) == []


@pytest.mark.parametrize(
    "phrase",
    [
        "begins to crack",
        "begin to crack",
        "starts to crack",
        "start to crack",
        "starting to crack",
        "beginning to crack",
        "begins crumbling",
        "starts crumbling",
        "Begins To crack",
    ],
)
def test_all_onset_forms_are_case_insensitive(phrase):
    plan = plan_with_actions([f"The rigid bar {phrase} under the water."] + [
        "Hands tap the wet bar and a clean translucent shard breaks free.",
        "Hands stack the sharp glassy shards along the ceramic sink edge.",
        "Hands lift the largest section while the wet facets keep shining.",
    ])
    assert len(onset_errors(plan)) == 1


@pytest.mark.parametrize(
    "text",
    [
        "A beginner studies the rigid glassy bar under running water.",
        "The bar restarts to its rigid pose under running water.",
    ],
)
def test_word_internal_fragments_do_not_match(text):
    assert onset_errors(plan_with_actions([text] + [
        "Hands tap the wet bar and a clean translucent shard breaks free.",
        "Hands stack the sharp glassy shards along the ceramic sink edge.",
        "Hands lift the largest section while the wet facets keep shining.",
    ])) == []


def _write_lint_series(root, *, bad):
    folder = root / "channel" / "lint-test"
    plans = folder / "plans"
    plans.mkdir(parents=True)
    (folder / "series.json").write_text(
        json.dumps({
            "slug": "lint-test",
            "next_part": 2,
            "total_parts": 2,
            "parts": {"1": {"status": "published"}},
        }),
        encoding="utf-8",
    )
    (folder / "bible.json").write_text(json.dumps(bible_data("lint-test")), encoding="utf-8")
    queued = plan_with_actions([
        OLD_SHOT1 if bad else FIXED_SHOT1,
        "Hands tap the wet bar and a clean translucent shard breaks free.",
        "Hands stack the sharp glassy shards along the ceramic sink edge.",
        "Hands lift the largest section while the wet facets keep shining.",
    ])
    queued["episode"]["number"] = 2
    (plans / "part02.json").write_text(json.dumps(queued), encoding="utf-8")
    # Yayınlanmış eski plan hatalı olsa bile kuyruk linti onu denetlemez.
    (plans / "part01.json").write_text(json.dumps(plan_with_actions([OLD_SHOT1] * 4)), encoding="utf-8")


@pytest.mark.parametrize(("bad", "exit_code"), [(True, 1), (False, 0)])
def test_plan_lint_exit_code_depends_only_on_errors(tmp_path, bad, exit_code, capsys):
    _write_lint_series(tmp_path, bad=bad)
    assert plan_lint.main(["--series", "lint-test"], repo=tmp_path) == exit_code
    output = capsys.readouterr().out
    assert "part02.json:" in output
    assert "part01.json:" not in output
    assert "1 plan denetlendi" in output


def test_planner_onset_rule_is_present_in_both_object_prompt_branches():
    meta = type("Meta", (), {
        "slug": "onset-test",
        "base_title": "Onset Test",
        "logline": "One object behaves impossibly.",
    })()
    bible = Bible(bible_data())
    for format_version in (TEK_OBJE_FORMAT, "other-object-format"):
        _, instruction = replenish._build_prompt(
            meta,
            bible,
            {"format_version": format_version, "shots": 4, "shot_seconds": "6"},
            1,
            1,
            [],
        )
        assert "SHOT 1 ONSET" in instruction
        assert 'BAD: "the soap stays rigid and begins to crack like glass"' in instruction
        assert 'GOOD: "the bar is already split along a bright conchoidal fracture' in instruction
