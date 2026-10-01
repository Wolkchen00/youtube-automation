from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"

EXPECTED_SCHEDULES = {
    "wild-encounter.yml": ["13 7 * * *"],
    "fear-slide.yml": ["13 11 * * *", "30 21 * * *"],
    "dark-fact.yml": ["43 11 * * *"],
    "galactic-daily.yml": ["17 12 * * *"],
}

EXPECTED_KIE_WORKFLOWS = {
    "calibrate.yml",
    "event-horizon.yml",
    "fear-slide.yml",
    "fear-slide-hazir.yml",
    "flashpoints.yml",
    "footnotes.yml",
    "from-scratch.yml",
    "galactic-daily.yml",
    "next-stop.yml",
    "one-variable.yml",
    "planetfall.yml",
    "series.yml",
    "still-home.yml",
    "dark-fact.yml",
    "unnatural-lab.yml",
    "wild-encounter.yml",
}


@pytest.fixture(autouse=True)
def _eski_series_data_kokunu_izole_et():
    """This metadata-only test does not need the suite's writable series-data fixture."""


def _load_workflow(path):
    with path.open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def _triggers(workflow):
    # PyYAML's YAML 1.1 loader interprets an unquoted `on` key as boolean True.
    return workflow.get("on", workflow.get(True))


def test_live_lane_cron_saatleri():
    for filename, expected_crons in EXPECTED_SCHEDULES.items():
        workflow = _load_workflow(WORKFLOWS / filename)
        schedule = _triggers(workflow)["schedule"]
        assert [entry["cron"] for entry in schedule] == expected_crons


def test_kie_uretim_kuyrugu_tum_workflowlarda_max():
    kie_workflows = {}
    for path in WORKFLOWS.glob("*.yml"):
        workflow = _load_workflow(path)
        concurrency = workflow.get("concurrency")
        if isinstance(concurrency, dict) and concurrency.get("group") == "kie-uretim":
            kie_workflows[path.name] = concurrency

    assert set(kie_workflows) == EXPECTED_KIE_WORKFLOWS
    for filename, concurrency in kie_workflows.items():
        assert concurrency.get("queue") == "max", filename
        assert concurrency.get("cancel-in-progress") is not True, filename


def test_still_home_zamanlamasi_kapali():
    """1 Ekim 2026: still-home durduruldu, kanal dark-fact'e gecti. Iki hat ayni
    kanala yayin yapar; ikisinin birden zamanli olmasi gunde-1 kilidine dayanir."""
    triggers = _triggers(_load_workflow(WORKFLOWS / "still-home.yml"))
    assert "schedule" not in triggers
