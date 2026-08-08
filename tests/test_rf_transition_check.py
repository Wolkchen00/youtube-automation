"""FROM SCRATCH gecis kapisi icin agsiz regresyon testleri."""

import hashlib
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from tools import rf_transition_check


DOCTRINE_SHA = "a" * 64
CHECKPOINT_SHA = "b" * 40


class RfTransitionCheckTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temporary.name) / "from-scratch"
        (self.root / "plans").mkdir(parents=True)
        self.doctrine = pathlib.Path(self.temporary.name) / "KONSEPT.md"
        self.doctrine.write_text("donmus doktrin\n", encoding="utf-8")
        self.digest = rf_transition_check.doctrine_sha256(self.doctrine)
        self.series = {
            "slug": "from-scratch",
            "total_parts": 10,
            "next_part": 6,
            "doctrine_sha256": self.digest,
            "parts": {"2": {"status": "published"}, "1": {"status": "published"}},
        }
        self._write_series()
        (self.root / "published.json").write_bytes(b'[{"video_id":"x"}]\n')
        for number in rf_transition_check.REQUIRED_PARTS:
            self._write_plan(number)

        self.patches = [
            mock.patch.object(rf_transition_check, "data_dir", return_value=self.root),
            mock.patch.object(rf_transition_check, "doctrine_path", return_value=self.doctrine),
            mock.patch.object(rf_transition_check, "_checkpoint_sha", return_value=CHECKPOINT_SHA),
            mock.patch.object(rf_transition_check.preflight, "run", return_value=0),
        ]
        for patcher in self.patches:
            patcher.start()

    def tearDown(self):
        for patcher in reversed(self.patches):
            patcher.stop()
        self.temporary.cleanup()

    def _write_series(self):
        (self.root / "series.json").write_text(
            json.dumps(self.series, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _write_plan(self, number, digest=None):
        plan = {
            "episode": {"number": number, "title": f"Bolum {number}"},
            "doctrine_sha256": digest or self.digest,
            "shots": [],
        }
        (self.root / "plans" / f"part{number:02d}.json").write_text(
            json.dumps(plan), encoding="utf-8"
        )

    def _snapshot(self):
        self.assertEqual(rf_transition_check.snapshot(self.root), 0)
        return json.loads((self.root / ".rf_transition.json").read_text(encoding="utf-8"))

    def test_canonical_parts_hash_is_key_order_independent(self):
        left = {"2": {"b": 2, "a": "ş"}, "1": {"x": True}}
        right = {"1": {"x": True}, "2": {"a": "ş", "b": 2}}
        self.assertEqual(
            rf_transition_check.canonical_parts_sha256(left),
            rf_transition_check.canonical_parts_sha256(right),
        )

    def test_snapshot_records_required_fields_and_raw_published_hash(self):
        record = self._snapshot()
        raw = (self.root / "published.json").read_bytes()
        self.assertEqual(record["checkpoint_sha"], CHECKPOINT_SHA)
        self.assertEqual(record["doctrine_sha256"], self.digest)
        self.assertEqual(record["total_parts"], 10)
        self.assertEqual(record["next_part"], 6)
        self.assertEqual(
            record["parts_sha256"],
            rf_transition_check.canonical_parts_sha256(self.series["parts"]),
        )
        self.assertEqual(record["published_sha256"], hashlib.sha256(raw).hexdigest())

    def test_snapshot_overwrite_preserves_old_record_under_previous(self):
        first = self._snapshot()
        second = self._snapshot()
        self.assertEqual(second["previous"], first)

    def test_verify_accepts_exact_transition_and_runs_all_preflights(self):
        self._snapshot()
        self.assertEqual(rf_transition_check.verify(self.root), 0)
        self.assertEqual(rf_transition_check.preflight.run.call_count, 5)

    def test_verify_rejects_protected_parts_or_published_change(self):
        self._snapshot()
        self.series["parts"]["1"]["status"] = "damaged"
        self._write_series()
        (self.root / "published.json").write_bytes(b"[]\n")
        self.assertEqual(rf_transition_check.verify(self.root), 1)

    def test_verify_rejects_missing_stale_and_overflow_plans(self):
        self._snapshot()
        (self.root / "plans" / "part06.json").unlink()
        self._write_plan(7, digest="c" * 64)
        self._write_plan(11)
        self.assertEqual(rf_transition_check.verify(self.root), 1)

    def test_verify_rejects_counter_or_stale_snapshot_doctrine(self):
        self._snapshot()
        self.series["total_parts"] = 9
        self.series["next_part"] = 7
        self._write_series()
        sidecar_path = self.root / ".rf_transition.json"
        sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
        sidecar["doctrine_sha256"] = "d" * 64
        sidecar_path.write_text(json.dumps(sidecar), encoding="utf-8")
        self.assertEqual(rf_transition_check.verify(self.root), 1)

    def test_verify_propagates_preflight_failure(self):
        self._snapshot()
        rf_transition_check.preflight.run.return_value = 1
        self.assertEqual(rf_transition_check.verify(self.root), 1)


if __name__ == "__main__":
    unittest.main()
