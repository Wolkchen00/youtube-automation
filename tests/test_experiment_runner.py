"""ROCK 5 experiment budget, isolation, and preflight proofs (offline)."""

import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

from series import credit_gate, experiment, produce  # noqa: E402
from series.bible import Bible  # noqa: E402


class ExperimentLedgerTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = pathlib.Path(self.tempdir.name)
        self.ledger = self.root / "experiments_ledger.json"
        patcher = mock.patch.object(experiment, "LEDGER_PATH", self.ledger)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_stage_subcap_overflow_and_settlement_release_margin(self):
        experiment.configure_experiment(
            "r5", total_cap=200,
            stage_caps={"pilot": 60, "preflight": 200},
        )
        gate = experiment.ExperimentGate("r5", "pilot")
        self.assertTrue(gate.authorize("main_shot", "seedance", "4"))
        self.assertTrue(gate.settle_last(20))
        self.assertTrue(gate.authorize("main_shot", "seedance", "4"))
        self.assertFalse(gate.authorize("main_shot", "seedance", "4"))

        data = json.loads(self.ledger.read_text(encoding="utf-8"))
        calls = data["experiments"]["r5"]["reservations"]
        self.assertEqual([call["actual"] for call in calls], [20.0, None])
        self.assertEqual(sum(
            call["reserved"] if call["actual"] is None else call["actual"]
            for call in calls
        ), 60.0)

    def test_total_cap_refuses_even_when_second_stage_has_room(self):
        experiment.configure_experiment(
            "r5", total_cap=70,
            stage_caps={"pilot": 200, "preflight": 200},
        )
        self.assertTrue(experiment.authorize(
            "r5", "pilot", "main_shot", "seedance", "4"
        ))
        self.assertFalse(experiment.authorize(
            "r5", "preflight", "main_shot", "seedance", "4"
        ))

    def test_corrupt_experiment_ledger_is_fatal_for_paid_calls(self):
        original = b"{not-json"
        self.ledger.write_bytes(original)
        gate = experiment.ExperimentGate("r5", "pilot")
        self.assertFalse(gate.authorize("main_shot", "seedance", "4"))
        self.assertTrue(gate.blocked)
        self.assertEqual(self.ledger.read_bytes(), original)
        backups = list(self.root.glob("experiments_ledger.corrupt-*.json"))
        self.assertGreaterEqual(len(backups), 1)
        self.assertTrue(all(path.read_bytes() == original for path in backups))

    def test_composite_authorizes_and_settles_both_caps(self):
        experiment.configure_experiment(
            "r5", total_cap=100,
            stage_caps={"pilot": 100},
        )
        episode_gate = credit_gate.HardCreditCap(100, 0)
        experiment_gate = experiment.ExperimentGate("r5", "pilot")
        combined = credit_gate.CompositeCreditCap(episode_gate, experiment_gate)
        self.assertTrue(combined.authorize("main_shot", "seedance", "4"))
        self.assertTrue(combined.settle_last(31))
        self.assertEqual(episode_gate.spent, 31)
        data = json.loads(self.ledger.read_text(encoding="utf-8"))
        self.assertEqual(
            data["experiments"]["r5"]["reservations"][0]["actual"], 31.0
        )


class ExperimentRunnerTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = pathlib.Path(self.tempdir.name)
        self.production = self.root / "production"
        self.production.mkdir()
        self.series_json = self.production / "series.json"
        self.bible_json = self.production / "bible.json"
        self.plan_json = self.production / "part07.json"
        self.series_json.write_text(json.dumps({
            "slug": "lab", "next_part": 7,
            "parts": {"7": {"status": "planned"}},
        }), encoding="utf-8")
        bible_data = {
            "series": {
                "slug": "lab", "title": "Lab", "aspect_ratio": "9:16",
                "resolution": "1080p", "engine": "seedance",
                "chain_frames": False, "credit_hard_cap_value": 100,
            },
            "art_style": "Neutral test style.", "music": False,
            "characters": [], "environments": [], "props": [],
        }
        self.bible_json.write_text(json.dumps(bible_data), encoding="utf-8")
        self.bible = Bible(bible_data)
        self.plan_json.write_text(json.dumps({
            "episode": {"number": 7, "title": "Experiment"},
            "shots": [{"n": 1, "duration": "4", "prompt": "Offline shot."}],
        }), encoding="utf-8")
        self.output_root = self.root / "output" / "experiments"
        self.ledger = self.root / "experiments_ledger.json"

    def test_runner_preserves_series_next_part_and_parts_and_isolates_outputs(self):
        before = {
            path: path.read_bytes()
            for path in (self.series_json, self.bible_json, self.plan_json)
        }

        def fake_produce(_slug, isolated_plan, **kwargs):
            self.assertIsInstance(kwargs["hard_cap"], credit_gate.CompositeCreditCap)
            self.assertTrue(kwargs["hard_cap"].authorize(
                "main_shot", "seedance", "4"
            ))
            self.assertTrue(kwargs["hard_cap"].settle_last(30))
            area = pathlib.Path(kwargs["output_area"])
            artifact = area / "ep07.mp4"
            artifact.write_bytes(b"offline-video")
            self.assertEqual(pathlib.Path(isolated_plan).parent, area)
            return produce.ProduceResult("ok", artifact)

        with mock.patch.object(experiment, "EXPERIMENT_OUTPUT_ROOT", self.output_root), \
             mock.patch.object(experiment, "LEDGER_PATH", self.ledger), \
             mock.patch.object(experiment, "series_meta_path", return_value=self.series_json), \
             mock.patch.object(experiment, "bible_path", return_value=self.bible_json), \
             mock.patch.object(experiment.Bible, "load", return_value=self.bible), \
             mock.patch.object(experiment.produce, "produce_episode", side_effect=fake_produce):
            result = experiment.run_experiment(
                "lab", self.plan_json, "rock5", stage="pilot"
            )

        self.assertEqual(result.status, "ok")
        for path, content in before.items():
            self.assertEqual(path.read_bytes(), content)
        state = json.loads(self.series_json.read_text(encoding="utf-8"))
        self.assertEqual(state["next_part"], 7)
        self.assertEqual(state["parts"], {"7": {"status": "planned"}})
        area = self.output_root / "rock5" / "lab-part07"
        self.assertTrue((area / "plan.json").is_file())
        self.assertTrue((area / "bible.json").is_file())
        self.assertTrue((area / "ep07.mp4").is_file())
        self.assertEqual(
            {path for path in (self.root / "output").rglob("*") if path.is_file()},
            {area / "plan.json", area / "bible.json", area / "ep07.mp4"},
        )

    def test_dry_run_is_passed_through_without_authorizer(self):
        observed = {}

        def fake_produce(_slug, _plan, **kwargs):
            observed.update(kwargs)
            return produce.ProduceResult("generation_fail")

        with mock.patch.object(experiment, "EXPERIMENT_OUTPUT_ROOT", self.output_root), \
             mock.patch.object(experiment, "series_meta_path", return_value=self.series_json), \
             mock.patch.object(experiment, "bible_path", return_value=self.bible_json), \
             mock.patch.object(experiment.Bible, "load", return_value=self.bible), \
             mock.patch.object(experiment.produce, "produce_episode", side_effect=fake_produce):
            experiment.run_experiment(
                "lab", self.plan_json, "rock5-dry", dry_run=True
            )
        self.assertTrue(observed["dry_run"])
        self.assertIsNone(observed["hard_cap"])


class PreflightPriceTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.ledger = pathlib.Path(self.tempdir.name) / "experiments_ledger.json"
        patcher = mock.patch.object(experiment, "LEDGER_PATH", self.ledger)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_preflight_invokes_one_mocked_adapter_and_records_balance_delta(self):
        balances = mock.Mock(side_effect=[{"credits": 1000}, {"credits": 963}])
        generator = mock.Mock(return_value={"url": "https://example.test/video.mp4"})
        params = {"prompt": "offline", "duration": "4"}
        measured = experiment.preflight_price(
            "r5-price", "seedance", params,
            balance_checker=balances, generator=generator, fleet_reserve=0,
        )
        generator.assert_called_once_with("seedance", params)
        self.assertEqual(measured["measured_credits"], 37.0)
        data = json.loads(self.ledger.read_text(encoding="utf-8"))
        entry = data["experiments"]["r5-price"]
        self.assertEqual(entry["reservations"][0]["actual"], 37.0)
        self.assertEqual(entry["measurements"][0]["engine"], "seedance")
        self.assertEqual(entry["measurements"][0]["params"], params)


if __name__ == "__main__":
    unittest.main()
