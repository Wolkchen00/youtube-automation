"""ROCK 4b: kare zincirini açmadan önce üretim güvenliği kanıtları."""

import json
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest

from series.bible import Bible
from series import critic, produce, series_runner
from series.shots import resolve_shot, resolve_visual_shot


def bible(*, chain=False, scope="episode", engine="omni", cross_opt_in=False):
    return Bible({
        "series": {
            "slug": "conditioning-test",
            "title": "Conditioning Test",
            "aspect_ratio": "9:16",
            "resolution": "1080p",
            "engine": engine,
            "chain_frames": chain,
            "chain_scope": scope,
            "allow_cross_episode_chaining": cross_opt_in,
            "omit_character_refs": True,
        },
        "art_style": "fixed style",
        "environments": [{
            "id": "bench",
            "ref_image_url": "https://refs.test/bench.jpg",
        }],
        "characters": [],
        "props": [{
            "id": "tool",
            "ref_image_url": "https://refs.test/tool.jpg",
        }],
    })


def plan():
    return {
        "episode": {"number": 7, "title": "Safe chain"},
        "prop_ref_urls": ["https://refs.test/object.jpg"],
        "shots": [
            {"n": 1, "duration": "6", "prompt": "first", "environment": "bench"},
            {"n": 2, "duration": "6", "prompt": "second", "environment": "bench"},
            {"n": 3, "duration": "6", "prompt": "third", "environment": "bench"},
        ],
    }


def test_chain_off_fleet_paths_keep_legacy_payload_and_skip_chain_work():
    """Filo güvenliği: kapalı zincir resolver/payload kararlarını değiştirmez."""
    b = bible(chain=False)
    p = plan()
    shot = {**p["shots"][0], "props": ["tool"]}

    resolved = resolve_shot(b, shot, p)
    expected_prompt = (
        "fixed style\n\nfirst\n\n"
        "[image 1] is the exact object: keep its shape, colour, scale and markings identical.\n"
        "[image 2] is the room and surface: keep the same surface and light."
    )
    assert resolved["kwargs"]["prompt"] == expected_prompt
    assert resolved["kwargs"]["image_urls"] == [
        "https://refs.test/object.jpg",
        "https://refs.test/bench.jpg",
        "https://refs.test/tool.jpg",
    ]
    assert "image_bindings" not in resolved
    assert resolve_visual_shot(b, shot)["start_image_url"] == "https://refs.test/bench.jpg"

    for candidate in (shot, {**shot, "engine": "seedance"}, {**shot, "engine": "omni"}):
        decision = produce.decide_shot_chain(candidate, None, False, "stale")
        assert decision.start_url is None
        assert decision.capture_last_frame is False


def test_series_scope_without_second_explicit_opt_in_refuses_before_credit(caplog):
    b = bible(chain=True, scope="series", cross_opt_in=False)
    fake_meta = SimpleNamespace()
    with mock.patch.object(produce.SeriesMeta, "load", return_value=fake_meta), \
            mock.patch.object(produce, "_doctrine_gate", return_value="digest"), \
            mock.patch.object(produce.Bible, "load", return_value=b), \
            mock.patch.object(produce, "check_credit") as credit:
        result = produce._produce_episode_impl("conditioning-test", plan())

    assert result is None
    credit.assert_not_called()
    assert "allow_cross_episode_chaining=true" in caplog.text
    assert produce.chain_configuration_error(
        bible(chain=True, scope="series", cross_opt_in=True)
    ) is None


def test_episode_scope_never_reads_or_uses_previous_episode_frame():
    class PoisonMeta(dict):
        def get(self, *_args, **_kwargs):
            raise AssertionError("önceki bölüm last_frame_url okunmamalı")

    b = bible(chain=True, scope="episode")
    meta = SimpleNamespace(data=PoisonMeta(last_frame_url="prior-episode"))
    assert series_runner._episode_chain_start(b, meta) is None
    assert produce._initial_chain_url(b, "prior-sidecar") is None


def test_binding_order_labels_and_urls_share_one_ordered_source():
    b = bible(chain=True)
    p = plan()
    shot = {**p["shots"][1], "props": ["tool"]}
    result = resolve_shot(b, shot, p, chain_url="https://frames.test/shot-1.jpg")

    urls = result["kwargs"]["image_urls"]
    bindings = result["image_bindings"]
    assert urls == [
        "https://frames.test/shot-1.jpg",
        "https://refs.test/object.jpg",
        "https://refs.test/bench.jpg",
        "https://refs.test/tool.jpg",
    ]
    assert [binding["url"] for binding in bindings] == urls
    for position, binding in enumerate(bindings, start=1):
        assert binding["index"] == position
        assert binding["label"].startswith(f"[image {position}] ")
        assert binding["label"] in result["kwargs"]["prompt"]


def test_accepted_shot_upload_failure_never_reuses_older_frame(tmp_path):
    b = bible(chain=True)
    p = plan()
    frame = tmp_path / "last.jpg"
    clip = tmp_path / "shot.mp4"
    with mock.patch.object(produce.ffmpeg_tools, "extract_last_frame", return_value=frame), \
            mock.patch.object(produce.critic, "review_chain_frame", return_value=(True, [])), \
            mock.patch.object(produce.critic, "log_chain_frame_event"), \
            mock.patch.object(produce, "upload_to_imgbb", side_effect=["frame-shot-1", None]):
        from_shot_1 = produce._next_chain_frame(
            b, p, p["shots"][0], p["shots"][1], clip,
            default_engine="omni", qc_cfg={}, object_ref=None, episode=7,
        )
        from_shot_2 = produce._next_chain_frame(
            b, p, p["shots"][1], p["shots"][2], clip,
            default_engine="omni", qc_cfg={}, object_ref=None, episode=7,
        )

    assert from_shot_1.url == "frame-shot-1"
    assert from_shot_2.url is None
    assert from_shot_2.canonical_reset is True
    next_decision = produce.decide_shot_chain(
        p["shots"][2], None, True, from_shot_2.url
    )
    assert next_decision.start_url is None
    assert next_decision.start_url != from_shot_1.url


def test_unsuitable_frame_uses_canonical_reset_and_writes_log_and_qc_journal(
        tmp_path, caplog):
    b = bible(chain=True)
    p = plan()
    frame = tmp_path / "last.jpg"
    clip = tmp_path / "shot.mp4"
    with mock.patch.object(produce.ffmpeg_tools, "extract_last_frame", return_value=frame), \
            mock.patch.object(
                produce.critic, "review_chain_frame",
                return_value=(False, ["obje pozu kararsız"]),
            ), mock.patch.object(critic, "data_dir", return_value=tmp_path):
        result = produce._next_chain_frame(
            b, p, p["shots"][0], p["shots"][1], clip,
            default_engine="omni", qc_cfg={}, object_ref=None, episode=7,
        )

    assert result.url is None
    assert result.canonical_reset is True
    assert result.error is None
    assert "Zincir karesi sıfırlandı" in caplog.text
    events = [json.loads(line) for line in (tmp_path / "qc_log.jsonl").read_text(
        encoding="utf-8"
    ).splitlines()]
    reset = events[-1]
    assert reset["event"] == "chain_frame_reset"
    assert reset["verdict"] == "canonical_reset"
    assert reset["reason"] == "unsuitable"
    assert reset["reasons"] == ["obje pozu kararsız"]
    assert reset["canonical_source"] == "omni_image_references"


def test_unsuitable_frame_without_canonical_scene_fails_closed(tmp_path):
    b = bible(chain=True, engine="seedance")
    b.data["environments"] = []
    p = plan()
    next_shot = {"n": 2, "duration": "6", "prompt": "text only"}
    with mock.patch.object(produce.ffmpeg_tools, "extract_last_frame", return_value=tmp_path / "x.jpg"), \
            mock.patch.object(produce.critic, "review_chain_frame", return_value=(False, ["glitch"])), \
            mock.patch.object(produce.critic, "log_chain_frame_event"):
        result = produce._next_chain_frame(
            b, p, p["shots"][0], next_shot, tmp_path / "shot.mp4",
            default_engine="seedance", qc_cfg={}, object_ref=None, episode=7,
        )
    assert result.url is None
    assert result.canonical_reset is False
    assert "text-only üretime düşülmedi" in result.error
