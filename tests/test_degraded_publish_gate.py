"""ROCK 1d: bozulmus yayin kapisi (degraded publish gate) kanitlari."""

from __future__ import annotations

import json
from contextlib import ExitStack
from pathlib import Path
from unittest import mock

import pytest

from series.bible import Bible
from series.produce import ProduceResult
from series.series_meta import SeriesMeta
from series import series_runner


def _bible(slug: str, *, block_degraded_publish: bool = False) -> Bible:
    data = {
        "series": {
            "slug": slug,
            "title": slug,
            "engine": "omni",
            "state_machine_version": 2,
            "duration_band": [14, 22],
        },
        "characters": [],
        "environments": [],
        "props": [],
    }
    if block_degraded_publish:
        data["series"]["block_degraded_publish"] = True
    return Bible(data)


def _meta(slug: str, *, version_parts: int = 1,
          mode: str = "auto", parts: dict | None = None) -> SeriesMeta:
    return SeriesMeta({
        "slug": slug,
        "base_title": slug,
        "total_parts": version_parts,
        "next_part": 1,
        "status": "active",
        "publish_mode": mode,
        "upload_profile": "test-profile",
        "platforms": ["youtube"],
        "parts": parts or {},
    })


def _plan(number: int = 1, shots: list[dict] | None = None) -> dict:
    return {
        "episode": {"number": number, "title": f"Bölüm {number}"},
        "shots": [] if shots is None else shots,
    }


def _runner_stack(meta: SeriesMeta, bible: Bible, plan_path: Path, plan: dict,
                  producer, *, publisher=None, spent: float = 0) -> ExitStack:
    """Koşucuyu ağdan, gerçek defterden ve gerçek seri dosyasından ayır."""
    stack = ExitStack()
    stack.enter_context(mock.patch.object(series_runner.SeriesMeta, "load", return_value=meta))
    stack.enter_context(mock.patch("series.bible.Bible.load", return_value=bible))
    stack.enter_context(mock.patch.object(meta, "save"))
    stack.enter_context(mock.patch.object(meta, "save_atomic"))
    stack.enter_context(mock.patch.object(series_runner, "_channel_published_today", return_value=None))
    stack.enter_context(mock.patch.object(series_runner, "part_plan_path", return_value=plan_path))
    stack.enter_context(mock.patch.object(series_runner, "load_plan", return_value=plan))
    stack.enter_context(mock.patch.object(series_runner, "check_credit", return_value={"credits": 5000}))
    stack.enter_context(mock.patch.object(series_runner.credit_gate, "run_gate", return_value=True))
    stack.enter_context(mock.patch.object(series_runner.credit_gate, "reserve", return_value=True))
    stack.enter_context(mock.patch.object(series_runner.credit_gate, "reconcile"))
    stack.enter_context(mock.patch.object(series_runner, "_actual_episode_spent", return_value=spent))
    stack.enter_context(mock.patch.object(series_runner.produce, "episode_spent", return_value=spent))
    stack.enter_context(mock.patch.object(series_runner.produce, "produce_episode", side_effect=producer))
    stack.enter_context(mock.patch.object(
        series_runner, "_publish_part",
        side_effect=publisher if publisher is not None else lambda *a, **k: ["youtube"],
    ))
    stack.enter_context(mock.patch.object(series_runner, "_alert"))
    return stack


def test_degraded_episode_is_never_published_when_the_gate_is_on(tmp_path: Path):
    """Kapali kapida bozulmus bolum asla yayinlanmaz; qc_retry'ye dusmeli."""
    slug = "degraded-gate-on"
    meta = _meta(slug)
    bible = _bible(slug, block_degraded_publish=True)
    plan_path = tmp_path / "part01.json"
    plan_path.write_text("{}", encoding="utf-8")
    video = tmp_path / "episode.mp4"
    video.write_bytes(b"dummy")

    degraded_coherence = {
        "loop_closed": False,
        "narration_delivered": False,
        "arc_roles_missing": ["loop_seam"],
        "duration_s": 11.1,
        "duration_in_band": False,
        "degraded": True,
    }

    publisher_calls = []

    def producer(*args, **kwargs):
        return ProduceResult("ok", video, coherence=degraded_coherence, dropped_shots=[])

    def publisher(*args, **kwargs):
        publisher_calls.append(args)
        return ["youtube"]

    with _runner_stack(meta, bible, plan_path, _plan(), producer, publisher=publisher):
        result = series_runner.run_next(slug, publish=True, force=True)

    assert publisher_calls == [], "yayinlayici asla cagrilmamali"
    part = meta.get_part(1)
    assert part["status"] == "qc_retry"
    assert part["retry_count"] == 1
    assert part["last_reason_code"] == "EPISODE_DEGRADED"
    assert result is False


def test_unmeasured_duration_is_also_held(tmp_path: Path):
    """Olculmemis sure (duration_in_band: None) de kapida tutulmali."""
    slug = "unmeasured-duration"
    meta = _meta(slug)
    bible = _bible(slug, block_degraded_publish=True)
    plan_path = tmp_path / "part01.json"
    plan_path.write_text("{}", encoding="utf-8")
    video = tmp_path / "episode.mp4"
    video.write_bytes(b"dummy")

    unmeasured_coherence = {
        "loop_closed": True,
        "narration_delivered": True,
        "arc_roles_missing": [],
        "duration_s": 18.4,
        "duration_in_band": None,
        "degraded": False,
    }

    publisher_calls = []

    def producer(*args, **kwargs):
        return ProduceResult("ok", video, coherence=unmeasured_coherence, dropped_shots=[])

    def publisher(*args, **kwargs):
        publisher_calls.append(args)
        return ["youtube"]

    with _runner_stack(meta, bible, plan_path, _plan(), producer, publisher=publisher):
        result = series_runner.run_next(slug, publish=True, force=True)

    assert publisher_calls == [], "yayinlayici asla cagrilmamali"
    part = meta.get_part(1)
    assert part["status"] == "qc_retry"
    assert part["retry_count"] == 1
    assert part["last_reason_code"] == "EPISODE_DEGRADED"
    assert result is False


def test_healthy_episode_still_publishes_with_the_gate_on(tmp_path: Path):
    """Saglikli bolum kapida olsa bile yayinlanmali."""
    slug = "healthy-gate-on"
    meta = _meta(slug)
    bible = _bible(slug, block_degraded_publish=True)
    plan_path = tmp_path / "part01.json"
    plan_path.write_text("{}", encoding="utf-8")
    video = tmp_path / "episode.mp4"
    video.write_bytes(b"dummy")

    healthy_coherence = {
        "loop_closed": True,
        "narration_delivered": True,
        "arc_roles_missing": [],
        "duration_s": 18.4,
        "duration_in_band": True,
        "degraded": False,
    }

    publisher_calls = []

    def producer(*args, **kwargs):
        return ProduceResult("ok", video, coherence=healthy_coherence, dropped_shots=[])

    def publisher(*args, **kwargs):
        publisher_calls.append(args)
        return ["youtube"]

    with _runner_stack(meta, bible, plan_path, _plan(), producer, publisher=publisher):
        result = series_runner.run_next(slug, publish=True, force=True)

    assert len(publisher_calls) == 1, "yayinlayici cagrilmali"
    part = meta.get_part(1)
    assert part["status"] == "published"
    assert result is True


def test_series_without_the_flag_publishes_a_degraded_episode_exactly_as_before(tmp_path: Path):
    """Bayrak yoksa bozulmus bolum onceki davranisla yayinlanmali (fleet guard)."""
    slug = "no-gate-flag"
    meta = _meta(slug)
    # block_degraded_publish AUSENT (key yok)
    bible = _bible(slug, block_degraded_publish=False)
    plan_path = tmp_path / "part01.json"
    plan_path.write_text("{}", encoding="utf-8")
    video = tmp_path / "episode.mp4"
    video.write_bytes(b"dummy")

    degraded_coherence = {
        "loop_closed": False,
        "narration_delivered": False,
        "arc_roles_missing": ["loop_seam"],
        "duration_s": 11.1,
        "duration_in_band": False,
        "degraded": True,
    }

    publisher_calls = []

    def producer(*args, **kwargs):
        return ProduceResult("ok", video, coherence=degraded_coherence, dropped_shots=[])

    def publisher(*args, **kwargs):
        publisher_calls.append(args)
        return ["youtube"]

    with _runner_stack(meta, bible, plan_path, _plan(), producer, publisher=publisher):
        result = series_runner.run_next(slug, publish=True, force=True)

    assert len(publisher_calls) == 1, "bayrak yoksa yayinlanmali"
    part = meta.get_part(1)
    assert part["status"] == "published"
    assert result is True


def test_three_degraded_attempts_end_in_needs_human_and_the_queue_moves_on(tmp_path: Path):
    """Uc bozulmus deneme sonrasi needs_human ve kuyruk ilerlemeli."""
    slug = "three-degraded-advances"
    meta = _meta(slug, version_parts=3)
    bible = _bible(slug, block_degraded_publish=True)
    plan_path = tmp_path / "part.json"
    plan_path.write_text("{}", encoding="utf-8")
    video = tmp_path / "episode.mp4"
    video.write_bytes(b"dummy")

    degraded_coherence = {
        "loop_closed": False,
        "narration_delivered": False,
        "arc_roles_missing": ["loop_seam"],
        "duration_s": 11.1,
        "duration_in_band": False,
        "degraded": True,
    }

    publisher_calls = []
    attempt = 0

    def producer(*args, **kwargs):
        nonlocal attempt
        attempt += 1
        return ProduceResult("ok", video, coherence=degraded_coherence, dropped_shots=[])

    def publisher(*args, **kwargs):
        publisher_calls.append(args)
        return ["youtube"]

    with _runner_stack(meta, bible, plan_path, _plan(), producer, publisher=publisher):
        # 1. deneme
        r1 = series_runner.run_next(slug, publish=True, force=True)
        assert r1 is False
        assert meta.get_part(1)["status"] == "qc_retry"
        assert meta.get_part(1)["retry_count"] == 1
        assert meta.next_part == 1

        # 2. deneme
        r2 = series_runner.run_next(slug, publish=True, force=True)
        assert r2 is False
        assert meta.get_part(1)["status"] == "qc_retry"
        assert meta.get_part(1)["retry_count"] == 2
        assert meta.next_part == 1

        # 3. deneme -> needs_human ve kuyruk ilerler
        r3 = series_runner.run_next(slug, publish=True, force=True)
        # Ucuncu cagri part 1'i needs_human yapar, kuyruk part 2'ye ilerler,
        # ama part 2 icin de ayni bozulmus coherence dondugu icin o da qc_retry'ye duser.
        # Bu yuzden donus degeri False olur. Onemli olan state'dir.
        assert r3 is False
        assert meta.get_part(1)["status"] == "needs_human"
        assert meta.get_part(1)["retry_count"] == 3
        assert meta.next_part == 2

    assert publisher_calls == [], "hicbir denemede yayinlanmamali"


def test_episode_degraded_is_a_valid_reason_code():
    """EPISODE_DEGRADED gecerli bir reason_code olmali; bilinmeyen kod hata vermeli."""
    # Gecerli kod - hata vermemeli
    result = ProduceResult("qc_hold", reason="test", reason_code="EPISODE_DEGRADED")
    assert result.reason_code == "EPISODE_DEGRADED"

    # Gecersiz kod - ValueError vermeli
    with pytest.raises(ValueError):
        ProduceResult("qc_hold", reason="test", reason_code="NOT_A_REAL_CODE")