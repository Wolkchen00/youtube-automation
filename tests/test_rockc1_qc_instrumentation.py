"""ROCK C1: dayanıklı QC API muhasebesi ve tükenmede fail-closed kanıtı."""

import contextlib
import json
import pathlib
import sys
import tempfile
import types
import unittest
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core import cost_tracker
from series import bible as bible_module
from series import critic, produce
from tools import qc_api_report


def passing_review():
    return {
        "anatomy_ok": True,
        "face_match": None,
        "wardrobe_ok": None,
        "era_ok": None,
        "unwanted_text": False,
        "forbidden_elements": False,
        "artifact_score": 0,
        "issues": [],
        "fix_notes": [],
    }


class FakeGemini:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = 0

        class Part:
            @staticmethod
            def from_text(*, text):
                return {"text": text}

            @staticmethod
            def from_bytes(*, data, mime_type):
                return {"data": data, "mime_type": mime_type}

        class Config:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

        self.types = types.ModuleType("google.genai.types")
        self.types.Part = Part
        self.types.GenerateContentConfig = Config
        self.genai = types.ModuleType("google.genai")
        self.genai.types = self.types
        owner = self

        class Models:
            def generate_content(self, **_kwargs):
                owner.calls += 1
                outcome = owner.outcomes.pop(0) if owner.outcomes else owner.default
                if isinstance(outcome, BaseException):
                    raise outcome
                return SimpleNamespace(text=outcome)

        self.default = json.dumps(passing_review())
        self.genai.Client = lambda **_kwargs: SimpleNamespace(models=Models())
        self.google = types.ModuleType("google")
        self.google.genai = self.genai

    def modules(self):
        return {
            "google": self.google,
            "google.genai": self.genai,
            "google.genai.types": self.types,
        }


class EpisodeHarness(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = pathlib.Path(self.tempdir.name)
        self.channel = self.root / "channel"
        self.channel.mkdir()
        self.output = self.root / "output" / "series"
        self.slug = "rockc1-test"
        self.folder = self.channel / self.slug
        self.folder.mkdir()
        (self.channel / "KONSEPT.md").write_text("ROCK C1 çevrimdışı doktrin.\n", encoding="utf-8")
        (self.folder / "series.json").write_text(json.dumps({
            "slug": self.slug,
            "base_title": "ROCK C1",
            "total_parts": 1,
            "next_part": 1,
            "status": "active",
            "parts": {},
        }), encoding="utf-8")
        (self.folder / "bible.json").write_text(json.dumps({
            "series": {
                "slug": self.slug,
                "title": "ROCK C1",
                "engine": "seedance",
                "chain_frames": False,
                "audio_smooth": False,
                "qc": {
                    "enabled": True,
                    "frames": 1,
                    "qc_review_retries": 0,
                    "max_regens_per_shot": 0,
                    "scene_cut_scan": True,
                },
            },
            "music": False,
            "characters": [],
            "environments": [],
            "props": [],
        }), encoding="utf-8")
        self.plan = {
            "episode": {"number": 7, "title": "C1 Offline"},
            "synopsis": "Dayanıklı QC deneme günlüğü.",
            "narration": "",
            "shots": [{
                "n": 1,
                "duration": "10",
                "prompt": "A stable object remains centered under neutral light.",
            }],
        }
        self.frame = self.root / "frame.jpg"
        self.frame.write_bytes(b"frame")
        self.patchers = [
            mock.patch.object(bible_module, "PROJECT_ROOT", self.root),
            mock.patch.object(bible_module, "SERIES_DATA_DIR", self.root / "series_data"),
            mock.patch.object(bible_module, "SERIES_DIR", self.output),
            mock.patch.object(bible_module, "_SEARCH_ROOTS", [self.channel]),
            mock.patch.object(cost_tracker, "COST_LOG", self.root / "cost.json"),
        ]
        for patcher in self.patchers:
            patcher.start()
            self.addCleanup(patcher.stop)

    @contextlib.contextmanager
    def run_context(self, fake: FakeGemini):
        def download(_url, target, **_kwargs):
            path = pathlib.Path(target)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"generated-video")
            return True

        def write_video(_source, target, **_kwargs):
            path = pathlib.Path(target)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"final-video")
            return path

        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch.dict(sys.modules, fake.modules()))
            stack.enter_context(mock.patch.object(critic, "GEMINI_API_KEY", "test-key"))
            stack.enter_context(mock.patch.object(critic.time, "sleep"))
            stack.enter_context(mock.patch.object(critic.ffmpeg_tools, "sample_frames", return_value=[self.frame]))
            stack.enter_context(mock.patch.object(critic.ffmpeg_tools, "detect_scene_cuts", return_value=[1.25]))
            stack.enter_context(mock.patch.object(produce, "ensure_episode_refs", return_value=True))
            stack.enter_context(mock.patch.object(produce, "check_credit"))
            stack.enter_context(mock.patch.object(produce, "resolve_visual_shot", return_value={
                "prompt": self.plan["shots"][0]["prompt"],
                "start_image_url": None,
                "duration": "10",
            }))
            stack.enter_context(mock.patch.object(
                produce, "_generate_visual_clip",
                return_value={"url": "offline://shot", "credits": 0},
            ))
            stack.enter_context(mock.patch.object(produce, "download_file", side_effect=download))
            stack.enter_context(mock.patch.object(produce, "_prep_shot_clip", side_effect=lambda _b, _p, _s, path: path))
            stack.enter_context(mock.patch.object(produce.ffmpeg_tools, "get_video_duration", return_value=10.0))
            stack.enter_context(mock.patch.object(produce.ffmpeg_tools, "concatenate_simple", side_effect=write_video))
            stack.enter_context(mock.patch.object(produce.ffmpeg_tools, "final_export", side_effect=write_video))
            stack.enter_context(mock.patch.object(produce, "_post_process", side_effect=lambda _b, _p, path, **_k: path))
            stack.enter_context(mock.patch.object(produce, "_upscale_master", side_effect=lambda _b, _n, path, **_k: path))
            stack.enter_context(mock.patch.object(produce.report, "append_row"))
            stack.enter_context(mock.patch.object(produce.report, "export_xlsx"))
            stack.enter_context(mock.patch.object(produce.report, "summarize", return_value={
                "başarılı": 1, "çekim_sayısı": 1, "toplam_kredi": 0, "toplam_dolar": 0,
            }))
            yield stack

    def journal(self):
        path = self.folder / "qc_log.jsonl"
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    def produce(self, fake):
        return produce.produce_episode(
            self.slug, self.plan, typed_result=True, experiment_id="exp-c1"
        )


class InstrumentationTests(EpisodeHarness):
    def test_both_audio_call_sites_use_the_same_durable_attempt_contract(self):
        delivery = json.dumps({
            "has_music": False,
            "speech": False,
            "construction_sounds": ["tool"],
            "silent_fraction_estimate": 0.1,
        })
        native = json.dumps({
            "has_foley": True,
            "unwanted_speech": False,
            "unwanted_music": False,
            "notes": "natural tool sound",
        })
        fake = FakeGemini([delivery, native])
        mp3 = self.root / "sample.mp3"
        wav = self.root / "stem.wav"
        mp3.write_bytes(b"mp3")
        wav.write_bytes(b"wav")
        with mock.patch.dict(sys.modules, fake.modules()), \
                mock.patch.object(critic, "GEMINI_API_KEY", "test-key"):
            critic._review_audio(
                mp3, slug=self.slug, episode=7, shot=None,
                experiment_id="exp-c1",
            )
            critic._review_raw_native_audio(
                wav, slug=self.slug, episode=7, shot=2,
                experiment_id="exp-c1",
            )

        attempts = [
            event for event in self.journal() if event.get("event") == "qc_api_attempt"
        ]
        results = [
            event for event in self.journal() if event.get("event") == "qc_api_result"
        ]
        self.assertEqual(fake.calls, 2)
        self.assertEqual(
            [event["task_type"] for event in attempts],
            ["delivery_audio_review", "native_audio_review"],
        )
        self.assertEqual([event["shot"] for event in attempts], [None, 2])
        self.assertEqual([event["outcome"] for event in results], ["ok", "ok"])

    def test_healthy_episode_has_one_result_per_real_call_and_scene_scan_is_local(self):
        fake = FakeGemini([json.dumps(passing_review())])
        with self.run_context(fake):
            result = self.produce(fake)

        self.assertEqual(result.status, "ok")
        events = self.journal()
        attempts = [event for event in events if event.get("event") == "qc_api_attempt"]
        results = [event for event in events if event.get("event") == "qc_api_result"]
        scans = [event for event in events if event.get("event") == "scene_cut_scan"]
        self.assertEqual(len(attempts), fake.calls)
        self.assertEqual((len(attempts), len(results), len(scans)), (1, 1, 1))
        matches = {
            attempt["attempt_id"]: [
                item for item in results if item["attempt_id"] == attempt["attempt_id"]
            ]
            for attempt in attempts
        }
        self.assertTrue(all(len(items) == 1 for items in matches.values()))
        self.assertEqual(results[0]["outcome"], "ok")
        self.assertEqual(attempts[0]["task_type"], "visual_review")
        self.assertEqual(attempts[0]["model"], critic.QC_MODEL)
        self.assertFalse(attempts[0]["is_fallback"])
        self.assertEqual(attempts[0]["episode"], 7)
        self.assertEqual(attempts[0]["shot"], 1)
        self.assertEqual(attempts[0]["experiment_id"], "exp-c1")

    def test_single_429_then_success_is_not_a_hold_and_both_results_are_durable(self):
        fake = FakeGemini([
            RuntimeError("429 RESOURCE_EXHAUSTED"),
            json.dumps(passing_review()),
        ])
        with self.run_context(fake), mock.patch.object(critic, "_notify") as notify:
            result = self.produce(fake)

        self.assertEqual(result.status, "ok")
        events = self.journal()
        attempts = [event for event in events if event.get("event") == "qc_api_attempt"]
        outcomes = [
            event["outcome"] for event in events if event.get("event") == "qc_api_result"
        ]
        self.assertEqual(fake.calls, 2)
        self.assertEqual(len(attempts), 2)
        self.assertEqual(outcomes, ["429", "ok"])
        self.assertFalse(any(event.get("event") == "qc_hold" for event in events))
        notify.assert_not_called()

    def test_durable_attempt_write_failure_blocks_call_and_holds_episode_as_logging(self):
        fake = FakeGemini([json.dumps(passing_review())])
        with self.run_context(fake), mock.patch.object(
            critic, "_strict_log_event", side_effect=PermissionError("disk read-only")
        ), mock.patch.object(critic, "_notify") as notify:
            result = self.produce(fake)

        self.assertEqual((result.status, result.reason), ("qc_hold", "logging"))
        self.assertEqual(fake.calls, 0)
        self.assertFalse(any(event.get("event") == "qc_skip_accepted" for event in self.journal()))
        self.assertIn("KOTA-DIŞI", notify.call_args.args[0])

    def test_all_five_exhaustion_classes_hold_with_exact_reason_and_never_accept(self):
        cases = {
            "quota": RuntimeError("429 RESOURCE_EXHAUSTED"),
            "auth": RuntimeError("403 PERMISSION_DENIED"),
            "server": RuntimeError("503 UNAVAILABLE transport failure"),
            "parse": None,
            "logging": PermissionError("journal unavailable"),
        }
        for reason, failure in cases.items():
            with self.subTest(reason=reason):
                fake = FakeGemini(
                    ["not-json"] * 6 if reason == "parse" else [failure] * 6
                )
                strict_patch = (
                    mock.patch.object(critic, "_strict_log_event", side_effect=failure)
                    if reason == "logging" else contextlib.nullcontext()
                )
                with self.run_context(fake), strict_patch, \
                        mock.patch.object(critic, "_notify") as notify:
                    result = self.produce(fake)

                self.assertEqual((result.status, result.reason), ("qc_hold", reason))
                self.assertFalse(any(
                    event.get("event") == "qc_skip_accepted" for event in self.journal()
                ))
                alert = notify.call_args.args[0]
                if reason == "quota":
                    self.assertIn("QC KOTA TÜKENDİ", alert)
                    self.assertNotIn("KOTA-DIŞI", alert)
                else:
                    self.assertIn("QC KOTA-DIŞI TÜKENME", alert)


class ReportingTests(unittest.TestCase):
    def test_crash_gap_is_reported_as_one_unknown_unmatched_attempt(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            with mock.patch.object(critic, "data_dir", return_value=root):
                critic._strict_log_event("report-test", {
                    "event": "qc_api_attempt",
                    "attempt_id": "crashed-attempt",
                    "task_type": "visual_review",
                    "model": critic.QC_MODEL,
                    "is_fallback": False,
                    "episode": 22,
                    "shot": 3,
                })
            journal = root / "qc_log.jsonl"
            events, malformed = qc_api_report.read_journal(journal)
            report = qc_api_report.summarize(events, 22)
            text = qc_api_report.render(report, journal, malformed)

        self.assertEqual(report["attempts"], 1)
        self.assertEqual(report["unmatched_attempts"], ["crashed-attempt"])
        self.assertIn("Unmatched attempts (unknown/crash): 1", text)
        self.assertIn("Fallback share: 0/1 (0.0%)", text)

    def test_pre_c1_history_does_not_invent_attempt_counts(self):
        events = [{"event": "review", "episode": 22, "verdict": "pass"}]
        report = qc_api_report.summarize(events, 22)
        text = qc_api_report.render(report, pathlib.Path("qc_log.jsonl"))
        self.assertEqual(report["attempts"], 0)
        self.assertIn("cannot reveal the real Gemini attempt count", text)


if __name__ == "__main__":
    unittest.main()
