"""plato-3x8 creature and set anchors (RF-PLAN-WILD-ENCOUNTER, ROCK 4).

Every paid call is mocked; nothing here touches the network or a live channel
config. The money rules under test: authorize before paying, persist each
image right after its upload, never pay twice for the same anchor.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest import mock

import pytest

from series import critic, produce
from series.bible import Bible
from series.shots import resolve_shot

ENV_DESC = "A built jungle set inside a film studio: dense practical foliage and low haze."
DESCRIPTOR = "a colossal olive-green crocodile head prop with pale yellow eyes and ivory teeth"
ANOMALY = "The crocodile head is a built practical prop whose jaws can be pushed open by hand."
_ABSENT = object()


def _bible(*, anchors=True, env_url=None) -> Bible:
    series = {
        "slug": "plato-anchor-proof",
        "title": "Plato Anchor Proof",
        "engine": "omni",
        "aspect_ratio": "9:16",
        "resolution": "1080p",
        "state_machine_version": 2,
        "chain_frames": True,
        "qc": {"enabled": True, "native_audio_review": True},
    }
    if anchors is not _ABSENT:
        series["episode_anchors"] = anchors
    return Bible({
        "series": series,
        "art_style": "Vertical 9:16 photoreal behind-the-scenes footage of a film shoot.",
        "music": False,
        "characters": [{
            "id": "ihsan_field",
            "name": "Ihsan",
            "character_id": "cid-ihsan",
            "ref_image_url": "https://i.ibb.co/ihsan.jpg",
        }],
        "environments": [{"id": "jungle_set", "desc": ENV_DESC, "ref_image_url": env_url}],
        "props": [],
    })


def _plan(fmt: str = "plato-3x8") -> dict:
    return {
        "episode": {"number": 6, "title": "This GIANT CROCODILE Is NOT Real"},
        "format_version": fmt,
        "object_card": {
            "name": "giant crocodile head practical prop",
            "descriptor": DESCRIPTOR,
            "environment": "jungle_set",
            "anomaly_descriptor": ANOMALY,
        },
        "shots": [
            {
                "n": n,
                "duration": "8",
                "characters": ["ihsan_field"],
                "environment": "jungle_set",
                "prompt": f"SHOT {n}, BEAT.\n\nbody of shot {n}",
            }
            for n in (1, 2, 3)
        ],
    }


class _Paid:
    """Stand-in for _generate_uploaded_reference that records every paid call."""

    def __init__(self, *results):
        self.calls: list[tuple[str, str]] = []
        self._results = list(results)

    def __call__(self, bible, prompt, save_path, hard_cap, number, operation, **_kwargs):
        self.calls.append((operation, prompt))
        if self._results:
            result = self._results.pop(0)
            if isinstance(result, BaseException):
                raise result
            return result
        return f"https://i.ibb.co/{operation}.png"

    @property
    def operations(self) -> list[str]:
        return [operation for operation, _ in self.calls]


def _run(bible, plan, plan_path, tmp_path, paid, *, dry_run=False):
    with mock.patch.object(produce, "_generate_uploaded_reference", side_effect=paid):
        return produce.ensure_episode_refs(
            bible, plan, plan_path, hard_cap=mock.Mock(), dry_run=dry_run,
            output_area=tmp_path,
        )


def _disk(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("anchors", [False, None, "true", _ABSENT])
def test_flag_not_exactly_true_changes_nothing(tmp_path, anchors):
    bible, plan, plan_path = _bible(anchors=anchors), _plan(), tmp_path / "part06.json"
    before_plan, before_bible = json.dumps(plan), json.dumps(bible.data)
    paid = _Paid()

    assert _run(bible, plan, plan_path, tmp_path, paid) is True

    assert paid.calls == []
    assert json.dumps(plan) == before_plan
    assert json.dumps(bible.data) == before_bible
    assert not plan_path.exists()
    assert not (tmp_path / "bible.json").exists()


def test_flag_does_not_route_other_formats_into_plato_anchors():
    bible = _bible(anchors=True)
    assert produce._plato_anchors_enabled(bible, _plan("plato-3x8")) is True
    assert produce._plato_anchors_enabled(bible, _plan("tek-obje-4x6")) is False
    assert produce._plato_anchors_enabled(bible, _plan("tanik-2x8")) is False


def test_first_run_makes_one_set_plate_then_one_creature_and_persists_each(tmp_path):
    bible, plan, plan_path = _bible(), _plan(), tmp_path / "part06.json"
    paid = _Paid()

    assert _run(bible, plan, plan_path, tmp_path, paid) is True

    assert paid.operations == ["environment_ref_jungle_set", "creature_ref"]
    env_prompt, creature_prompt = (prompt for _, prompt in paid.calls)
    assert "built film set" in env_prompt and "foliage and low haze. One wide" in env_prompt
    assert DESCRIPTOR in creature_prompt and "built film set" in creature_prompt
    assert "pushed open by hand" not in creature_prompt  # the reveal stays out

    disk_bible = _disk(tmp_path / "bible.json")
    assert disk_bible["environments"][0]["ref_image_url"] == (
        "https://i.ibb.co/environment_ref_jungle_set.png"
    )
    disk_plan = _disk(plan_path)
    assert disk_plan["prop_ref_urls"] == ["https://i.ibb.co/creature_ref.png"]
    assert len(disk_plan["ref_prompt_sha256"]) == 64


def test_second_run_pays_nothing(tmp_path):
    bible, plan, plan_path = _bible(), _plan(), tmp_path / "part06.json"
    _run(bible, plan, plan_path, tmp_path, _Paid())
    again = _Paid()

    assert _run(bible, plan, plan_path, tmp_path, again) is True
    assert again.calls == []


def test_changed_descriptor_regenerates_only_the_creature(tmp_path):
    bible, plan, plan_path = _bible(), _plan(), tmp_path / "part06.json"
    _run(bible, plan, plan_path, tmp_path, _Paid())
    plan["object_card"]["descriptor"] = DESCRIPTOR + ", with a scarred left brow"
    again = _Paid()

    assert _run(bible, plan, plan_path, tmp_path, again) is True
    assert again.operations == ["creature_ref"]


def test_changed_set_description_regenerates_both_anchors(tmp_path):
    # The set description feeds both prompts, so a changed set leaves the old plate
    # showing the previous set: both anchors go stale together.
    bible, plan, plan_path = _bible(), _plan(), tmp_path / "part06.json"
    _run(bible, plan, plan_path, tmp_path, _Paid())
    bible.get("environments", "jungle_set")["desc"] = ENV_DESC + " Wet stone underfoot."
    again = _Paid()

    assert _run(bible, plan, plan_path, tmp_path, again) is True
    assert again.operations == ["environment_ref_jungle_set", "creature_ref"]


def test_plate_without_a_hash_is_treated_as_stale(tmp_path):
    bible, plan, plan_path = _bible(), _plan(), tmp_path / "part06.json"
    _run(bible, plan, plan_path, tmp_path, _Paid())
    del bible.get("environments", "jungle_set")["ref_prompt_sha256"]
    again = _Paid()

    assert _run(bible, plan, plan_path, tmp_path, again) is True
    assert again.operations == ["environment_ref_jungle_set"]


def test_crash_after_the_set_plate_never_pays_for_the_plate_again(tmp_path):
    bible, plan, plan_path = _bible(), _plan(), tmp_path / "part06.json"
    crashing = _Paid("https://i.ibb.co/plate.png", RuntimeError("process died"))

    with pytest.raises(RuntimeError):
        _run(bible, plan, plan_path, tmp_path, crashing)

    # A real crash loses memory: restart from what reached the disk.
    restarted = Bible(_disk(tmp_path / "bible.json"))
    assert restarted.get("environments", "jungle_set")["ref_image_url"] == (
        "https://i.ibb.co/plate.png"
    )
    retry = _Paid()
    assert _run(restarted, _plan(), plan_path, tmp_path, retry) is True
    assert retry.operations == ["creature_ref"]


def test_set_plate_failure_stops_before_the_creature(tmp_path):
    bible, plan, plan_path = _bible(), _plan(), tmp_path / "part06.json"
    paid = _Paid(None)

    assert _run(bible, plan, plan_path, tmp_path, paid) is False
    assert paid.operations == ["environment_ref_jungle_set"]
    assert "prop_ref_urls" not in plan
    assert not plan_path.exists()


def test_creature_failure_returns_false_and_leaves_the_plan_unanchored(tmp_path):
    bible, plan, plan_path = _bible(), _plan(), tmp_path / "part06.json"
    paid = _Paid("https://i.ibb.co/plate.png", None)

    assert _run(bible, plan, plan_path, tmp_path, paid) is False
    assert "prop_ref_urls" not in plan
    assert not plan_path.exists()
    # the plate that was paid for is kept
    assert _disk(tmp_path / "bible.json")["environments"][0]["ref_image_url"] == (
        "https://i.ibb.co/plate.png"
    )


def test_refused_credit_gate_makes_no_paid_call(tmp_path):
    bible, plan, plan_path = _bible(), _plan(), tmp_path / "part06.json"
    cap = mock.Mock()
    cap.authorize.return_value = False

    with mock.patch.object(produce, "generate_image") as generate:
        ok = produce.ensure_episode_refs(
            bible, plan, plan_path, hard_cap=cap, output_area=tmp_path,
        )

    assert ok is False
    cap.authorize.assert_called_once()
    generate.assert_not_called()
    assert not plan_path.exists()


def test_dry_run_reports_and_pays_nothing(tmp_path):
    bible, plan, plan_path = _bible(), _plan(), tmp_path / "part06.json"
    paid = _Paid()

    assert _run(bible, plan, plan_path, tmp_path, paid, dry_run=True) is True
    assert paid.calls == []
    assert not plan_path.exists()


def test_malformed_existing_creature_url_is_refused_without_paying(tmp_path):
    bible, plan, plan_path = _bible(), _plan(), tmp_path / "part06.json"
    plan["prop_ref_urls"] = ["http://insecure.example/croc.png"]
    paid = _Paid()

    assert _run(bible, plan, plan_path, tmp_path, paid) is False
    assert paid.calls == []


def test_anchored_payload_order_and_unit_budget(tmp_path):
    bible, plan, plan_path = _bible(), _plan(), tmp_path / "part06.json"
    _run(bible, plan, plan_path, tmp_path, _Paid())
    creature = "https://i.ibb.co/creature_ref.png"
    plate = "https://i.ibb.co/environment_ref_jungle_set.png"
    chain = "https://i.ibb.co/chain/last-frame.png"

    first = resolve_shot(bible, plan["shots"][0], plan=plan)
    second = resolve_shot(bible, plan["shots"][1], plan=plan, chain_url=chain)

    assert first["kwargs"]["image_urls"] == [creature, plate]
    assert first["kwargs"]["character_ids"] == ["cid-ihsan"]
    assert second["kwargs"]["image_urls"] == [chain, creature, plate]
    assert second["kwargs"]["character_ids"] == ["cid-ihsan"]
    labels = [binding["label"] for binding in second["image_bindings"]]
    assert "previous accepted shot" in labels[0]
    assert "exact object" in labels[1]
    assert "room and surface" in labels[2]
    for result in (first, second):
        assert result["units"] <= 7
        assert result["warnings"] == []


def test_anchor_does_not_switch_on_the_anomaly_gate():
    # ROCK B's anomaly gate is config-only (qc.enforce); a creature reference
    # on the plan must not be what turns it on.
    assert critic._has_enforced_rb_gate(_bible().data["series"]["qc"]) is False
