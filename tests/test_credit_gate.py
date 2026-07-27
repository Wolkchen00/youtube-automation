"""Kredi kapısı için ağsız birim testleri."""

import datetime
import json
import os
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from series import credit_gate


sys.stdout.reconfigure(encoding="utf-8")


class CreditGateTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.ledger = pathlib.Path(self.tempdir.name) / "credits_ledger.json"
        self.path_patch = mock.patch.object(credit_gate, "LEDGER_PATH", self.ledger)
        self.path_patch.start()
        self.addCleanup(self.path_patch.stop)
        self.env_patch = mock.patch.dict(
            os.environ,
            {"EPISODE_CREDIT_CAP": "100", "MONTHLY_CREDIT_CAP": "1000"},
        )
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)

    @staticmethod
    def current_month():
        return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m")

    def write_entries(self, entries):
        self.ledger.write_text(
            json.dumps({"entries": entries}, ensure_ascii=False),
            encoding="utf-8",
        )

    def entry(self, month, reserved, actual=None, series="test", part=1):
        return {
            "month": month,
            "series": series,
            "part": part,
            "reserved": reserved,
            "actual": actual,
            "ts": "2026-07-27T00:00:00+00:00",
        }

    def test_reserve_and_reconcile_happy_path(self):
        self.assertTrue(credit_gate.reserve("lab", 3))
        credit_gate.reconcile("lab", 3, 72)
        data = json.loads(self.ledger.read_text(encoding="utf-8"))
        self.assertEqual(len(data["entries"]), 1)
        self.assertEqual(data["entries"][0]["reserved"], 100)
        self.assertEqual(data["entries"][0]["actual"], 72)

    def test_month_total_uses_actual_or_reservation(self):
        month = self.current_month()
        self.write_entries([
            self.entry(month, 100, 40, part=1),
            self.entry(month, 100, None, part=2),
            self.entry("1999-01", 900, None, part=3),
        ])
        self.assertEqual(credit_gate.month_total(month), 140)

    def test_monthly_cap_blocks_reservation(self):
        month = self.current_month()
        self.write_entries([self.entry(month, 950, None)])
        self.assertFalse(credit_gate.reserve("lab", 2))
        data = json.loads(self.ledger.read_text(encoding="utf-8"))
        self.assertEqual(len(data["entries"]), 1)

    def test_crash_reservation_still_counts_fully(self):
        with mock.patch.dict(
            os.environ,
            {"EPISODE_CREDIT_CAP": "100", "MONTHLY_CREDIT_CAP": "150"},
        ):
            self.assertTrue(credit_gate.reserve("lab", 1))
            self.assertEqual(credit_gate.month_total(self.current_month()), 100)
            self.assertFalse(credit_gate.reserve("lab", 2))

    def test_run_gate_threshold_and_none_balance(self):
        self.assertFalse(credit_gate.run_gate(None))
        self.assertFalse(credit_gate.run_gate(149))
        self.assertTrue(credit_gate.run_gate(150))
        self.assertTrue(credit_gate.run_gate(151))

    def test_corrupt_ledger_is_sidelined(self):
        original = b"{not-json"
        self.ledger.write_bytes(original)
        self.assertEqual(credit_gate.month_total(self.current_month()), 0)
        backups = list(self.ledger.parent.glob("credits_ledger.corrupt-*.json"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), original)
        self.assertEqual(
            json.loads(self.ledger.read_text(encoding="utf-8")),
            {"entries": []},
        )

    def test_empty_environment_values_use_defaults(self):
        with mock.patch.dict(
            os.environ,
            {"EPISODE_CREDIT_CAP": "", "MONTHLY_CREDIT_CAP": ""},
        ):
            self.assertEqual(credit_gate.episode_cap(), 900)
            month = self.current_month()
            self.write_entries([self.entry(month, 19101, None)])
            self.assertFalse(credit_gate.reserve("lab", 2))


if __name__ == "__main__":
    unittest.main()
