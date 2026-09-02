import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
MERGER_PATH = REPO_ROOT / "scripts" / "merge_credits_ledger.py"
LIVE_LEDGER_PATH = REPO_ROOT / "credits_ledger.json"

SPEC = importlib.util.spec_from_file_location("merge_credits_ledger", MERGER_PATH)
MERGER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MERGER)


class LedgerMergeTests(unittest.TestCase):
    def git(self, repo, *args, input_bytes=None):
        return subprocess.run(
            ["git", "-C", str(repo), *args],
            input=input_bytes,
            capture_output=True,
            check=True,
        )

    def blob(self, repo, doc):
        content = (json.dumps(doc, ensure_ascii=False) + "\n").encode("utf-8")
        result = self.git(repo, "hash-object", "-w", "--stdin", input_bytes=content)
        return result.stdout.decode("ascii").strip()

    def run_merge(self, base, ours, theirs):
        with tempfile.TemporaryDirectory() as temp:
            repo = pathlib.Path(temp)
            self.git(repo, "init", "-q")
            hashes = [self.blob(repo, doc) for doc in (base, ours, theirs)]
            index = "".join(
                f"100644 {blob_hash} {stage}\tcredits_ledger.json\n"
                for stage, blob_hash in enumerate(hashes, start=1)
            ).encode("ascii")
            self.git(repo, "update-index", "--index-info", input_bytes=index)
            result = subprocess.run(
                [sys.executable, str(MERGER_PATH), "credits_ledger.json"],
                cwd=repo,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            output_path = repo / "credits_ledger.json"
            raw = output_path.read_bytes() if output_path.exists() else None
            merged = json.loads(raw.decode("utf-8")) if raw is not None else None
            return result, merged, raw

    def test_disjoint_episode_spend_keys_both_survive(self):
        base = {"entries": [], "episode_spend": {}}
        ours = {"entries": [], "episode_spend": {"seri:1": 125}}
        theirs = {"entries": [], "episode_spend": {"seri:2": 240}}

        result, merged, _ = self.run_merge(base, ours, theirs)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(merged["episode_spend"], {"seri:1": 125, "seri:2": 240})

    def test_divergent_same_key_uses_documented_numeric_rule_and_floor(self):
        base = {"entries": [], "episode_spend": {"seri:1": 100, "seri:2": 100}}
        ours = {"entries": [], "episode_spend": {"seri:1": 130, "seri:2": 40}}
        theirs = {"entries": [], "episode_spend": {"seri:1": 125, "seri:2": 30}}

        result, merged, _ = self.run_merge(base, ours, theirs)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(merged["episode_spend"]["seri:1"], 155)
        self.assertGreaterEqual(
            merged["episode_spend"]["seri:1"],
            max(ours["episode_spend"]["seri:1"], theirs["episode_spend"]["seri:1"]),
        )
        self.assertEqual(merged["episode_spend"]["seri:2"], 40)
        self.assertGreaterEqual(
            merged["episode_spend"]["seri:2"],
            max(ours["episode_spend"]["seri:2"], theirs["episode_spend"]["seri:2"]),
        )

    def test_episode_spend_survives_when_only_entries_conflict(self):
        base = {
            "entries": [{"ts": "2026-08-01T00:00:00Z", "id": "base"}],
            "episode_spend": {"seri:1": 42},
        }
        ours = {
            "entries": base["entries"] + [{"ts": "2026-08-03T00:00:00Z", "id": "ours"}],
            "episode_spend": {"seri:1": 42},
        }
        theirs = {
            "entries": base["entries"] + [{"ts": "2026-08-02T00:00:00Z", "id": "theirs"}],
            "episode_spend": {"seri:1": 42},
        }

        result, merged, _ = self.run_merge(base, ours, theirs)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(merged["episode_spend"], {"seri:1": 42})
        self.assertEqual([entry["id"] for entry in merged["entries"]], ["base", "theirs", "ours"])

    def test_entries_dedup_and_ts_ordering_are_unchanged(self):
        first_attempt = {"series": "seri", "part": 7, "ts": "2026-08-03T00:00:00Z"}
        repeated_attempt = {"series": "seri", "part": 7, "ts": "2026-08-04T00:00:00Z"}
        earlier = {"series": "başka", "part": 1, "ts": "2026-08-01T00:00:00Z"}
        base = {"entries": [first_attempt], "episode_spend": {"seri:7": 10}}
        ours = {"entries": [first_attempt, repeated_attempt], "episode_spend": {"seri:7": 10}}
        theirs = {"entries": [earlier, first_attempt], "episode_spend": {"seri:7": 10}}

        result, merged, raw = self.run_merge(base, ours, theirs)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(merged["entries"], [earlier, first_attempt, repeated_attempt])
        self.assertEqual(merged["episode_spend"], {"seri:7": 10})
        self.assertTrue(raw.endswith(b"\n"))
        self.assertNotIn(b"\r\n", raw)

    def test_unknown_identical_and_one_sided_keys_are_preserved_in_stable_order(self):
        base = {"entries": [], "episode_spend": {"seri:1": 5}}
        ours = {
            "entries": [],
            "episode_spend": {"seri:1": 5},
            "z_future": {"mode": "safe"},
            "a_future": [1, 2],
        }
        theirs = {
            "entries": [],
            "episode_spend": {"seri:1": 5},
            "z_future": {"mode": "safe"},
        }

        result, merged, _ = self.run_merge(base, ours, theirs)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            list(merged), ["entries", "episode_spend", "a_future", "z_future"]
        )
        self.assertEqual(merged["a_future"], [1, 2])
        self.assertEqual(merged["z_future"], {"mode": "safe"})
        self.assertEqual(merged["episode_spend"], {"seri:1": 5})
        self.assertIn("a_future", result.stderr)
        self.assertIn("z_future", result.stderr)

    def test_unknown_divergence_fails_closed_and_names_key(self):
        base = {"entries": [], "episode_spend": {}}
        ours = {"entries": [], "episode_spend": {}, "future_schema": {"v": 1}}
        theirs = {"entries": [], "episode_spend": {}, "future_schema": {"v": 2}}

        result, merged, _ = self.run_merge(base, ours, theirs)

        self.assertEqual(result.returncode, 1)
        self.assertIsNone(merged)
        self.assertIn("future_schema", result.stderr)

    def test_non_numeric_or_negative_episode_spend_fails_closed_anywhere(self):
        valid = {"entries": [], "episode_spend": {"seri:1": 5}}
        cases = (
            ("base", {"entries": [], "episode_spend": {"seri:1": "5"}}, valid, valid),
            ("ours", valid, {"entries": [], "episode_spend": {"seri:1": -1}}, valid),
            ("theirs", valid, valid, {"entries": [], "episode_spend": {"seri:1": True}}),
        )
        for side, base, ours, theirs in cases:
            with self.subTest(side=side):
                result, merged, _ = self.run_merge(base, ours, theirs)
                self.assertEqual(result.returncode, 1)
                self.assertIsNone(merged)
                self.assertIn("episode_spend", result.stderr)

    def test_live_entries_and_episode_spend_schema_is_accepted(self):
        with LIVE_LEDGER_PATH.open(encoding="utf-8") as stream:
            live = json.load(stream)
        self.assertEqual(set(live), {"entries", "episode_spend"})
        self.assertTrue(MERGER.is_ledger(live))

        result, merged, _ = self.run_merge(live, live, live)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(set(merged), {"entries", "episode_spend"})
        self.assertEqual(merged["episode_spend"], live["episode_spend"])


if __name__ == "__main__":
    unittest.main()
