"""Experiment CLI asamalarinin tek kaynaktan cozuldugunu kanitlar."""

import json
from pathlib import Path
from unittest import mock

import pytest

from series import experiment


ROOT = Path(__file__).resolve().parents[1]
LIVE_LEDGER = json.loads(
    (ROOT / "experiments_ledger.json").read_text(encoding="utf-8")
)
LIVE_EXPERIMENT_STAGES = [
    (experiment_id, stage)
    for experiment_id, entry in LIVE_LEDGER["experiments"].items()
    for stage in entry["stage_caps"]
]


@pytest.fixture
def ledger_path(tmp_path, monkeypatch):
    path = tmp_path / "experiments_ledger.json"
    path.write_text(json.dumps({
        "experiments": {
            "fixture-exp": {
                "total_cap": 100,
                "stage_caps": {
                    "pilot": 20,
                    "pilot2": 20,
                    "preflight": 20,
                    "bakeoff": 0,
                    "holdout": 0,
                },
                "reservations": [],
                "measurements": [],
            },
        },
    }), encoding="utf-8")
    monkeypatch.setattr(experiment, "LEDGER_PATH", path)
    return path


@pytest.mark.parametrize("experiment_id,stage", LIVE_EXPERIMENT_STAGES)
def test_run_experiment_accepts_every_stage_in_live_ledger(experiment_id, stage):
    missing_plan = ROOT / "does-not-exist-stage-gate-proof.json"

    # FileNotFoundError, asama kapisinin gecilip plan okumaya ulasildigini kanitlar.
    with pytest.raises(FileNotFoundError):
        experiment.run_experiment(
            "fixture-slug", missing_plan, experiment_id, stage=stage, dry_run=True
        )


def test_live_ledger_zero_cap_does_not_invalidate_ledger():
    """Sifir kapak, canli defteri gecersiz kilmadan kapali asamayi temsil eder."""
    loaded = experiment._load()
    stage_caps = loaded["experiments"]["exp-2026-08-gerceklik"]["stage_caps"]

    # Defterdeki KAPAK DEGERLERI operasyonel karardir ve degisir; testin pinledigi
    # sey degismezdir: sifir kapakli bir asamanin varligi defteri gecersiz KILMAZ.
    assert "pilot2" in stage_caps
    zero_capped = [name for name, cap in stage_caps.items() if cap == 0]
    assert zero_capped, "regresyonu olcebilmek icin en az bir sifir kapak gerekli"
    assert all(cap >= 0 for cap in stage_caps.values())


def test_unknown_stage_fails_closed_and_lists_valid_stages(ledger_path):
    with pytest.raises(experiment.UnknownExperimentStageError) as caught:
        experiment.run_experiment(
            "fixture-slug", "missing-plan.json", "fixture-exp", stage="pilotX"
        )

    message = str(caught.value)
    assert "bilinmeyen asama 'pilotX'" in message
    assert (
        "gecerli asamalar: bakeoff, holdout, pilot, pilot2, preflight" in message
    )


def test_unknown_stage_is_rejected_during_cli_dry_run(ledger_path, capsys):
    exit_code = experiment.main([
        "run", "fixture-slug", "--plan", "missing-plan.json",
        "--experiment-id", "fixture-exp", "--stage", "pilotX", "--dry-run",
    ])

    captured = capsys.readouterr()
    assert exit_code != 0
    assert "bilinmeyen asama 'pilotX'" in captured.err
    assert "bakeoff, holdout, pilot, pilot2, preflight" in captured.err
    assert "Traceback" not in captured.err


def test_reserve_keeps_unknown_stage_last_line_of_defense(ledger_path, caplog):
    before = ledger_path.read_bytes()
    with mock.patch(
        "core.cost_tracker.conservative_credit_estimate", return_value=1.0
    ):
        reserved = experiment._reserve(
            "fixture-exp", "pilotX", "main_shot", "seedance", "4"
        )

    assert reserved is None
    assert "EXPERIMENT GATE REFUSED unknown stage" in caplog.text
    assert ledger_path.read_bytes() == before


def test_zero_cap_stage_refuses_paid_reservation_without_changing_ledger(
        ledger_path, caplog):
    before = ledger_path.read_bytes()
    with mock.patch(
        "core.cost_tracker.conservative_credit_estimate", return_value=1.0
    ):
        reserved = experiment._reserve(
            "fixture-exp", "bakeoff", "main_shot", "seedance", "4"
        )

    assert reserved is None
    assert "EXPERIMENT GATE REFUSED stage cap overflow" in caplog.text
    assert ledger_path.read_bytes() == before


@pytest.mark.parametrize(
    "invalid_cap",
    [-1, True, float("nan")],
    ids=["negative", "bool", "nan"],
)
def test_invalid_stage_caps_are_rejected_as_corrupt_ledgers(
        ledger_path, invalid_cap):
    data = json.loads(ledger_path.read_text(encoding="utf-8"))
    data["experiments"]["fixture-exp"]["stage_caps"]["pilot"] = invalid_cap
    ledger_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(experiment.ExperimentLedgerCorruptError):
        experiment._load()

    assert list(ledger_path.parent.glob("experiments_ledger.corrupt-*.json"))
