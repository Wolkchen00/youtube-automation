"""ROCK 1c: kurtarılabilir hold, ölü-mektup ve bütçe durum makinesi kanıtları."""

from __future__ import annotations

import copy
import json
from contextlib import ExitStack
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

import pytest

from series.bible import Bible
from series.produce import ProduceResult
from series.series_meta import SeriesMeta
from series import produce, series_runner


def _bible(slug: str, version: int) -> Bible:
    return Bible({
        "series": {
            "slug": slug,
            "title": slug,
            "engine": "omni",
            "state_machine_version": version,
            "credit_hard_cap": True,
            "credit_hard_cap_value": 800,
            "durable_credit_ledger": True,
        },
        "characters": [],
        "environments": [],
        "props": [],
    })


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


def test_legacy_off_qc_hold_is_byte_for_byte_old_state_and_blocks_next_run(tmp_path: Path):
    """Sürüm 1 filo güvenliği: yeni alan, retry veya yeniden üretim yok."""
    slug = "legacy-hold-proof"
    meta = _meta(slug)
    bible = _bible(slug, 1)
    plan_path = tmp_path / "part01.json"
    plan_path.write_text("{}", encoding="utf-8")
    result = ProduceResult("qc_hold", reason="reviewer timeout", reason_code="QUOTA")
    calls = 0

    def counted(*args, **kwargs):
        nonlocal calls
        calls += 1
        return result

    with _runner_stack(meta, bible, plan_path, _plan(), counted):
        assert series_runner.run_next(slug, publish=True, force=True) is True
        legacy_bytes = json.dumps(meta.get_part(1), ensure_ascii=False, separators=(",", ":"))
        assert legacy_bytes == (
            '{"status":"awaiting_approval",'
            '"hold_reason":"reviewer timeout"}'
        )
        assert series_runner.run_next(slug, publish=True, force=True) is True
    assert calls == 1


def test_v2_retryable_hold_retries_on_next_run_and_publishes(tmp_path: Path):
    slug = "retry-publish-proof"
    meta = _meta(slug)
    bible = _bible(slug, 2)
    plan_path = tmp_path / "part01.json"
    plan_path.write_text("{}", encoding="utf-8")
    video = tmp_path / "episode.mp4"
    attempts = iter([
        ProduceResult("qc_hold", reason="referans yok", reason_code="REF_DOWNLOAD"),
        ProduceResult("ok", video),
    ])

    with _runner_stack(meta, bible, plan_path, _plan(), lambda *a, **k: next(attempts)):
        assert series_runner.run_next(slug, publish=True, force=True) is False
        held = meta.get_part(1)
        assert held["status"] == "qc_retry"
        assert held["retry_count"] == 1
        assert held["last_reason_code"] == "REF_DOWNLOAD"
        assert held["first_held_at"]
        assert series_runner.run_next(slug, publish=True, force=True) is True

    assert meta.get_part(1)["status"] == "published"
    assert meta.next_part == 2


@pytest.mark.parametrize(
    ("code", "expected_status", "advanced"),
    [
        ("REF_DOWNLOAD", "qc_retry", False),
        ("CONTENT_REJECT", "needs_human", True),
        ("BUDGET_EXHAUSTED", "budget_exhausted", True),
    ],
)
def test_reason_code_alone_controls_retryability(code: str, expected_status: str,
                                                 advanced: bool):
    meta = _meta(f"reason-{code.lower()}", version_parts=2)
    # Metin bilerek tersini ima eder; karar yalnız tipli koddan çıkmalıdır.
    result = ProduceResult("generation_fail", reason="quota geçici olabilir", reason_code=code)
    with mock.patch.object(meta, "save"), mock.patch.object(meta, "save_atomic"), \
            mock.patch.object(series_runner, "_alert"):
        assert series_runner._record_recoverable_failure(meta, 1, result) is advanced
    assert meta.get_part(1)["status"] == expected_status
    assert meta.next_part == (2 if advanced else 1)


def test_third_attempt_dead_letters_then_produces_next_with_pointer_already_advanced(
        tmp_path: Path):
    slug = "dead-letter-order-proof"
    meta = _meta(slug, version_parts=2)
    bible = _bible(slug, 2)
    plan_path = tmp_path / "part.json"
    plan_path.write_text("{}", encoding="utf-8")
    snapshots: list[dict] = []
    produced_parts: list[int] = []

    def save_snapshot():
        snapshots.append(copy.deepcopy(meta.data))

    def producer(*args, **kwargs):
        produced_parts.append(meta.next_part)
        if len(produced_parts) <= 3:
            # Bu testin konusu SIRALAMA: terminal kayit + isaretci, sonraki bolum
            # uretilmeden ONCE diske yazilmis olmali. Vasita olarak ICERIK kodu
            # kullanilir. QUOTA artik ROCK 3d ile ayri altyapi butcesinden
            # harcadigi icin ucuncu denemede olmez; onun sonlu butcesi
            # tests/test_qc_backoff.py icinde ayrica kanitlanir.
            return ProduceResult("qc_hold", reason="geçici API", reason_code="UNKNOWN")
        # Yeni bölüm başlamadan önce terminal kayıt ve işaretçi diske yazılmış olmalı.
        assert any(
            snap["next_part"] == 2
            and snap["parts"]["1"]["status"] == "needs_human"
            for snap in snapshots
        )
        assert meta.next_part == 2
        return ProduceResult("ok", tmp_path / "part02.mp4")

    def publisher(_meta, n, *args, **kwargs):
        assert n == 2
        assert _meta.next_part == 2
        return ["youtube"]

    with _runner_stack(meta, bible, plan_path, _plan(), producer, publisher=publisher):
        with mock.patch.object(meta, "save", side_effect=save_snapshot), \
                mock.patch.object(meta, "save_atomic", side_effect=save_snapshot):
            assert series_runner.run_next(slug, publish=True, force=True) is False
            assert series_runner.run_next(slug, publish=True, force=True) is False
            assert series_runner.run_next(slug, publish=True, force=True) is True

    assert produced_parts == [1, 1, 1, 2]
    assert meta.get_part(1)["status"] == "needs_human"
    assert meta.get_part(2)["status"] == "published"
    assert meta.next_part == 3  # İşaretçi yayımlanmış part üzerinde bırakılmadı.


@pytest.mark.parametrize("missing", ["video", "release_tag", "approval_msg_id"])
def test_approval_state_requires_all_three_artifacts(tmp_path: Path, missing: str):
    slug = f"approval-missing-{missing}"
    meta = _meta(slug, mode="approval")
    bible = _bible(slug, 2)
    plan_path = tmp_path / f"{missing}.json"
    plan_path.write_text("{}", encoding="utf-8")
    video = tmp_path / "episode.mp4"

    with _runner_stack(
        meta, bible, plan_path, _plan(),
        lambda *a, **k: ProduceResult("ok", video),
    ):
        if missing == "video":
            def mark_without_video(n, path, subtitle=""):
                meta.get_part(n)["status"] = "produced"
            mark_video = mock.patch.object(meta, "mark_produced", side_effect=mark_without_video)
        else:
            mark_video = mock.patch.object(meta, "mark_produced", wraps=meta.mark_produced)
        tag = None if missing == "release_tag" else "release-v1"
        msg = None if missing == "approval_msg_id" else 123
        with mark_video, \
                mock.patch.object(series_runner, "_persist_release", return_value=tag), \
                mock.patch.object(series_runner, "_sample_frames", return_value=[]), \
                mock.patch.object(series_runner.notifier, "enabled", return_value=True), \
                mock.patch.object(series_runner.notifier, "request_approval", return_value=msg):
            assert series_runner.run_next(slug, publish=True, force=True) is False

    part = meta.get_part(1)
    assert part["status"] == "qc_retry"
    assert part["status"] != "awaiting_approval"


def test_run_next_explicitly_blocks_needs_human(tmp_path: Path):
    slug = "needs-human-block-proof"
    meta = _meta(slug, parts={"1": {"status": "needs_human"}})
    bible = _bible(slug, 2)
    plan_path = tmp_path / "part01.json"
    plan_path.write_text("{}", encoding="utf-8")
    calls = 0

    def producer(*args, **kwargs):
        nonlocal calls
        calls += 1

    with _runner_stack(meta, bible, plan_path, _plan(), producer):
        assert series_runner.run_next(slug, publish=True, force=True) is True
    assert calls == 0
    assert meta.next_part == 1


def test_insufficient_remaining_budget_terminalizes_advances_and_spends_zero(tmp_path: Path):
    slug = "budget-zero-paid-calls-proof"
    meta = _meta(slug)
    bible = _bible(slug, 2)
    shots = [{"n": n, "duration": "6"} for n in range(1, 5)]
    plan = _plan(shots=shots)
    plan_path = tmp_path / "part01.json"
    plan_path.write_text("{}", encoding="utf-8")
    paid_producer_calls = 0
    uploader_calls = 0
    shot_root = tmp_path / "shots"

    def producer(*args, **kwargs):
        nonlocal paid_producer_calls
        paid_producer_calls += 1

    def uploader(*args, **kwargs):
        nonlocal uploader_calls
        uploader_calls += 1

    with _runner_stack(meta, bible, plan_path, plan, producer, publisher=uploader, spent=512):
        with mock.patch.object(produce, "shots_dir", return_value=shot_root), \
                mock.patch.object(series_runner, "check_credit", wraps=series_runner.check_credit) as balance, \
                mock.patch.object(series_runner.credit_gate, "reserve", wraps=series_runner.credit_gate.reserve) as reserve:
            assert series_runner.run_next(slug, publish=True, force=True) is False
            balance.assert_not_called()
            reserve.assert_not_called()

    assert paid_producer_calls == 0
    assert uploader_calls == 0
    part = meta.get_part(1)
    assert part["status"] == "budget_exhausted"
    assert part["last_reason_code"] == "BUDGET_EXHAUSTED"
    assert meta.next_part == 2


def test_migration_is_idempotent_and_version_scoped():
    malformed = {
        "1": {"status": "awaiting_approval", "hold_reason": "eski serbest metin"},
        "2": {
            "status": "awaiting_approval", "video": "v.mp4",
            "release_tag": "r", "approval_msg_id": 7,
        },
    }
    v2_meta = _meta("migration-v2", version_parts=2, parts=copy.deepcopy(malformed))
    v1_meta = _meta("migration-v1", version_parts=2, parts=copy.deepcopy(malformed))

    with mock.patch.object(v2_meta, "save") as save_v2:
        assert series_runner.migrate_malformed_approval_holds(v2_meta, _bible("migration-v2", 2))
        first = copy.deepcopy(v2_meta.data)
        assert not series_runner.migrate_malformed_approval_holds(v2_meta, _bible("migration-v2", 2))
    assert save_v2.call_count == 1
    assert v2_meta.data == first
    assert v2_meta.get_part(1)["status"] == "qc_retry"
    assert v2_meta.get_part(1)["last_reason_code"] == "UNKNOWN"
    assert v2_meta.get_part(2)["status"] == "awaiting_approval"

    with mock.patch.object(v1_meta, "save") as save_v1:
        assert not series_runner.migrate_malformed_approval_holds(v1_meta, _bible("migration-v1", 1))
    save_v1.assert_not_called()
    assert v1_meta.data["parts"] == malformed


def test_produce_result_reason_code_domain_is_exact():
    allowed = {
        "QUOTA", "REF_DOWNLOAD", "FRAME_EXTRACT", "AUDIO_MASTER",
        "CONTENT_REJECT", "BUDGET_EXHAUSTED", "UNKNOWN",
    }
    assert {ProduceResult("generation_fail", reason_code=code).reason_code for code in allowed} == allowed
    with pytest.raises(ValueError):
        ProduceResult("generation_fail", reason_code="TRANSIENT")  # type: ignore[arg-type]
