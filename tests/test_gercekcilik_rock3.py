"""ROCK 3 fail-closed QC, state, cache, download, and budget proofs."""

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core import utils
from series import credit_gate, critic, produce, series_runner
from series.bible import Bible
from series.series_meta import SeriesMeta


def rock3_bible(slug="rock3-test"):
    return Bible({
        "series": {
            "slug": slug,
            "title": "Rock 3",
            "aspect_ratio": "9:16",
            "resolution": "1080p",
            "engine": "omni",
            "micro_trim": 0.25,
            "qc": {
                "enabled": True,
                "qc_review_retries": 0,
                "max_regens_per_shot": 2,
                "require_no_face": True,
                "require_object_match": True,
                "require_continuity": True,
                "require_first_frame": True,
                "require_all_shots": True,
            },
        },
        "art_style": "workshop",
        "music": False,
        "narration": {},
        "characters": [],
        "environments": [],
        "props": [],
    })


def passing_review():
    return {
        "anatomy_ok": True,
        "face_match": None,
        "wardrobe_ok": True,
        "era_ok": True,
        "unwanted_text": False,
        "forbidden_elements": False,
        "artifact_score": 0,
        "issues": [],
        "fix_notes": [],
        "face_present": False,
        "object_match": True,
        "object_notes": "same mark",
        "continuity_ok": True,
        "continuity_notes": "same state",
        "first_frame_ok": True,
        "first_frame_notes": "active and large",
    }


class MandatoryGateTests(unittest.TestCase):
    def setUp(self):
        self.qc = critic.qc_config(rock3_bible())

    def test_each_new_gate_is_false_fail_and_missing_hold(self):
        cases = (
            ("object_match", 1),
            ("continuity_ok", 2),
            ("first_frame_ok", 1),
        )
        for field, shot in cases:
            with self.subTest(field=field):
                failed = passing_review()
                failed[field] = False
                self.assertEqual(critic._decide(failed, self.qc, False, shot)[0], "fail")
                missing = passing_review()
                missing.pop(field)
                self.assertEqual(critic._decide(missing, self.qc, False, shot)[0], "hold")
                invalid = passing_review()
                invalid[field] = "true"
                self.assertEqual(critic._decide(invalid, self.qc, False, shot)[0], "hold")

    def _logged_review(self, shot_number):
        bible = rock3_bible()
        review = passing_review()
        with tempfile.TemporaryDirectory() as temp:
            clip = pathlib.Path(temp) / f"shot_{shot_number:02d}.mp4"
            clip.write_bytes(b"clip")
            prior = pathlib.Path(temp) / "prior.mp4"
            prior.write_bytes(b"prior")
            with mock.patch.object(
                critic, "review_clip", return_value=(review, "pass", [], [])
            ), mock.patch.object(
                critic.ffmpeg_tools, "extract_frame_at", return_value=pathlib.Path(temp) / "open.jpg"
            ), mock.patch.object(
                critic.ffmpeg_tools, "frame_metrics",
                return_value={"luma_contrast_proxy": 40.0, "sharpness_proxy": 12.0},
            ), mock.patch.object(
                critic.ffmpeg_tools, "extract_last_frame", return_value=pathlib.Path(temp) / "last.jpg"
            ), mock.patch.object(critic, "_log_event") as logged, mock.patch.object(
                critic, "_notify"
            ):
                result = critic.qc_shot(
                    bible, {"n": shot_number}, clip, "prompt", None,
                    episode=1, budget={"left": 0}, object_ref=b"object",
                    previous_clip=prior if shot_number > 1 else None,
                )
        self.assertEqual(result[2], "pass")
        return next(
            call.args[1] for call in logged.call_args_list
            if call.args[1].get("event") == "review"
        )

    def test_non_applicable_fields_are_literal_n_a(self):
        first = self._logged_review(1)
        self.assertEqual(first["continuity_ok"], "n/a")
        self.assertEqual(first["continuity_notes"], "n/a")
        self.assertIs(first["first_frame_ok"], True)
        self.assertEqual(first["opening_frame_luma_contrast_proxy"], 40.0)
        later = self._logged_review(2)
        self.assertIs(later["continuity_ok"], True)
        self.assertEqual(later["first_frame_ok"], "n/a")
        self.assertEqual(later["first_frame_notes"], "n/a")
        self.assertEqual(later["opening_frame_sharpness_proxy"], "n/a")

    def test_viewer_opening_timestamp_and_previous_accepted_frame_are_forwarded(self):
        bible = rock3_bible()
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            current = root / "shot_02.mp4"
            previous = root / "shot_01.mp4"
            opening = root / "opening.jpg"
            last = root / "accepted-last.jpg"
            for path in (current, previous, opening, last):
                path.write_bytes(b"fixture")
            with mock.patch.object(
                critic.ffmpeg_tools, "extract_last_frame", return_value=last
            ) as extract_last, mock.patch.object(
                critic.ffmpeg_tools, "extract_frame_at", return_value=opening
            ) as extract_open, mock.patch.object(
                critic, "review_clip", return_value=(passing_review(), "pass", [], [])
            ) as review, mock.patch.object(critic, "_log_event"), mock.patch.object(
                critic, "_notify"
            ):
                critic.qc_shot(
                    bible, {"n": 2}, current, "prompt", None,
                    episode=1, budget={"left": 0}, object_ref=b"object",
                    previous_clip=previous,
                )
                previous_frame = review.call_args.kwargs["previous_frame"]
                self.assertEqual(previous_frame, last)
                extract_last.assert_called_once()
                extract_open.assert_not_called()

            shot_one = root / "shot_01.mp4"
            shot_one.write_bytes(b"fixture")
            with mock.patch.object(
                critic.ffmpeg_tools, "extract_frame_at", return_value=opening
            ) as extract_open, mock.patch.object(
                critic.ffmpeg_tools, "frame_metrics",
                return_value={"luma_contrast_proxy": 1.0, "sharpness_proxy": 2.0},
            ), mock.patch.object(
                critic, "review_clip", return_value=(passing_review(), "pass", [], [])
            ) as review, mock.patch.object(critic, "_log_event"), mock.patch.object(
                critic, "_notify"
            ):
                critic.qc_shot(
                    bible, {"n": 1}, shot_one, "prompt", None,
                    episode=1, budget={"left": 0}, object_ref=b"object",
                )
                self.assertEqual(extract_open.call_args.args[1], bible.micro_trim)
                self.assertEqual(review.call_args.kwargs["opening_frame"], opening)

    def test_non_object_reviewer_payload_is_a_hold_for_mandatory_gates(self):
        bible = rock3_bible()
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            clip = root / "shot_01.mp4"
            frame = root / "frame.jpg"
            opening = root / "opening.jpg"
            for path in (clip, frame, opening):
                path.write_bytes(b"fixture")
            with mock.patch.object(
                critic.ffmpeg_tools, "sample_frames", return_value=[frame]
            ), mock.patch.object(critic, "_review_frames", return_value=[]):
                review, verdict, _reasons, _frames = critic.review_clip(
                    bible, {"n": 1}, clip, "prompt", self.qc,
                    object_ref=b"object", opening_frame=opening,
                )
        self.assertIsNone(review)
        self.assertEqual(verdict, "hold")


class RunnerHoldStateTests(unittest.TestCase):
    def test_two_auto_runs_hold_then_block_produce_and_publish(self):
        meta = SeriesMeta({
            "slug": "hold-series", "base_title": "Hold", "total_parts": 1,
            "next_part": 1, "status": "active", "publish_mode": "auto",
            "upload_profile": "profile", "platforms": ["youtube"], "parts": {},
        })
        bible = rock3_bible("hold-series")
        plan = {"episode": {"number": 1, "title": "Held"}, "shots": []}
        with tempfile.TemporaryDirectory() as temp:
            plan_path = pathlib.Path(temp) / "part01.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            with mock.patch.object(series_runner.SeriesMeta, "load", return_value=meta), \
                    mock.patch.object(meta, "save"), \
                    mock.patch.object(series_runner, "_channel_published_today", return_value=None), \
                    mock.patch.object(series_runner, "part_plan_path", return_value=plan_path), \
                    mock.patch.object(series_runner, "load_plan", return_value=plan), \
                    mock.patch("series.bible.Bible.load", return_value=bible), \
                    mock.patch.object(series_runner, "_episode_chain_start", return_value=None), \
                    mock.patch.object(series_runner, "check_credit", return_value={"credits": 5000}), \
                    mock.patch.object(series_runner.credit_gate, "run_gate", return_value=True), \
                    mock.patch.object(series_runner.credit_gate, "reserve", return_value=True), \
                    mock.patch.object(series_runner.credit_gate, "reconcile"), \
                    mock.patch.object(series_runner, "_actual_episode_spent", return_value=0), \
                    mock.patch.object(series_runner.produce, "episode_credit_cap", return_value=800), \
                    mock.patch.object(
                        series_runner.produce, "produce_episode",
                        return_value=produce.ProduceResult("qc_hold", reason="reviewer timeout"),
                    ) as production, mock.patch.object(
                        series_runner, "_publish_part"
                    ) as publishing, mock.patch.object(series_runner, "_alert"):
                self.assertTrue(series_runner.run_next("hold-series", publish=True, force=True))
                self.assertEqual(meta.get_part(1)["status"], "awaiting_approval")
                self.assertTrue(series_runner.run_next("hold-series", publish=True, force=True))
        self.assertEqual(production.call_count, 1)
        publishing.assert_not_called()


class CacheAndDownloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tempdir = tempfile.TemporaryDirectory()
        cls.media = pathlib.Path(cls.tempdir.name) / "fixture.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=blue:s=64x64:d=0.25",
            "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(cls.media),
        ], check=True, capture_output=True, timeout=60)
        cls.scene_media = pathlib.Path(cls.tempdir.name) / "scene-fixture.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error",
            "-f", "lavfi", "-i", "color=c=red:s=64x64:d=1:r=10",
            "-f", "lavfi", "-i", "color=c=blue:s=64x64:d=1:r=10",
            "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0,format=yuv420p",
            "-c:v", "libx264", "-g", "100", str(cls.scene_media),
        ], check=True, capture_output=True, timeout=60)

    @classmethod
    def tearDownClass(cls):
        cls.tempdir.cleanup()

    def test_cache_hash_mismatch_has_no_qc_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            clip = root / "shot.mp4"
            clip.write_bytes(self.media.read_bytes())
            digest = critic.content_sha256(clip)
            log = root / "qc_log.jsonl"
            log.write_text(json.dumps({
                "event": "qc_pass", "episode": 1, "shot": 1,
                "content_sha256": "0" * 64,
            }) + "\n", encoding="utf-8")
            with mock.patch.object(critic, "data_dir", return_value=root):
                self.assertFalse(critic.qc_pass_exists("s", 1, 1, digest))
                with open(log, "a", encoding="utf-8") as handle:
                    handle.write(json.dumps({
                        "event": "qc_pass", "episode": 1, "shot": 1,
                        "content_sha256": digest,
                    }) + "\n")
                self.assertTrue(critic.qc_pass_exists("s", 1, 1, digest))

    def test_cache_pass_must_cover_current_mandatory_gates(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            clip = root / "shot.mp4"
            clip.write_bytes(self.media.read_bytes())
            digest = critic.content_sha256(clip)
            log = root / "qc_log.jsonl"
            base = {
                "event": "qc_pass", "episode": 1, "shot": 1,
                "content_sha256": digest,
            }
            log.write_text(json.dumps(base) + "\n", encoding="utf-8")
            qc = critic.qc_config(rock3_bible())
            with mock.patch.object(critic, "data_dir", return_value=root):
                self.assertFalse(critic.qc_pass_exists("s", 1, 1, digest, qc))
                with open(log, "a", encoding="utf-8") as handle:
                    handle.write(json.dumps({
                        **base,
                        "face_present": False,
                        "object_match": True,
                        "continuity_ok": "n/a",
                        "first_frame_ok": True,
                    }) + "\n")
                self.assertTrue(critic.qc_pass_exists("s", 1, 1, digest, qc))

    def test_cache_hash_mismatch_is_moved_aside_for_fresh_generation_and_qc(self):
        with tempfile.TemporaryDirectory() as temp:
            cached = pathlib.Path(temp) / "shot_01.mp4"
            cached.write_bytes(self.media.read_bytes())
            with mock.patch.object(produce.ffmpeg_tools, "validate_media", return_value=True), \
                    mock.patch.object(produce.critic, "qc_pass_exists", return_value=False):
                self.assertFalse(produce._revalidate_cached_shot("s", 1, 1, cached))
            self.assertFalse(cached.exists())
            self.assertEqual(len(list(cached.parent.glob("shot_01_stale_*.mp4"))), 1)

    def test_scene_cut_scan_is_measure_only_log(self):
        with mock.patch.object(
            critic.ffmpeg_tools, "detect_scene_cuts", return_value=[0.75, 1.5]
        ), mock.patch.object(critic, "_log_event") as logged:
            critic.log_scene_cut_scan("s", 1, 2, pathlib.Path("shot_02.mp4"))
        event = logged.call_args.args[1]
        self.assertEqual(event["event"], "scene_cut_scan")
        self.assertEqual(event["count"], 2)
        self.assertEqual(event["timestamps"], [0.75, 1.5])

    def test_real_scene_cut_detector_finds_fixture_transition(self):
        timestamps = critic.ffmpeg_tools.detect_scene_cuts(
            self.scene_media, threshold=0.2, height=270
        )
        self.assertIsNotNone(timestamps)
        self.assertTrue(any(abs(timestamp - 1.0) < 0.2 for timestamp in timestamps))

    def test_hardened_download_retries_validates_and_atomically_renames(self):
        class Response:
            def __init__(self, payload):
                self.payload = payload

            def raise_for_status(self):
                return None

            def iter_content(self, chunk_size=8192):
                return (self.payload[i:i + chunk_size]
                        for i in range(0, len(self.payload), chunk_size))

        with tempfile.TemporaryDirectory() as temp:
            target = pathlib.Path(temp) / "shot.mp4"
            target.write_bytes(b"old-good-target")
            seen = []
            responses = iter((OSError("network"), Response(b"broken"), Response(self.media.read_bytes())))

            def request(*_args, **_kwargs):
                seen.append(target.read_bytes())
                item = next(responses)
                if isinstance(item, Exception):
                    raise item
                return item

            with mock.patch.object(utils.requests, "get", side_effect=request) as get, \
                    mock.patch.object(utils.time, "sleep"):
                self.assertEqual(
                    utils.download_file("https://example.invalid/shot", target,
                                        hardened=True, retries=3, backoff=0),
                    target,
                )
            self.assertEqual(get.call_count, 3)
            self.assertEqual(seen, [b"old-good-target"] * 3)
            self.assertTrue(utils._valid_video_file(target))
            self.assertEqual(list(target.parent.glob("*.part-*")), [])

    def test_hardened_download_final_failure_cleans_temp_and_preserves_target(self):
        with tempfile.TemporaryDirectory() as temp:
            target = pathlib.Path(temp) / "shot.mp4"
            target.write_bytes(b"existing")
            with mock.patch.object(
                utils.requests, "get", side_effect=OSError("offline")
            ) as get, mock.patch.object(utils.time, "sleep"):
                self.assertIsNone(utils.download_file(
                    "https://example.invalid/shot", target,
                    hardened=True, retries=3, backoff=0,
                ))
            self.assertEqual(get.call_count, 3)
            self.assertEqual(target.read_bytes(), b"existing")
            self.assertEqual(list(target.parent.glob("*.part-*")), [])


class DurableBudgetAndPromptTests(unittest.TestCase):
    def test_durable_spend_survives_fresh_state_and_blocks_over_cap(self):
        with tempfile.TemporaryDirectory() as temp:
            ledger = pathlib.Path(temp) / "credits_ledger.json"
            ledger.write_text('{"entries": []}', encoding="utf-8")
            with mock.patch.object(credit_gate, "LEDGER_PATH", ledger):
                self.assertTrue(credit_gate.record_episode_spend("lab", 9, 550))
                self.assertEqual(credit_gate.episode_spent("lab", 9), 550)
                cap = credit_gate.HardCreditCap(
                    800, credit_gate.episode_spent("lab", 9), durable_ledger=True
                )
                self.assertTrue(cap.authorize("qc_regen", "omni", "6"))
                self.assertTrue(cap.authorize("qc_regen", "omni", "6"))
                self.assertFalse(cap.authorize("qc_regen", "omni", "6"))

    def test_dynamic_allocator_orders_first_round_before_second(self):
        self.assertEqual(
            critic.allocate_regen_rounds([1, 2, 3, 4], 300, 800, 100, 2),
            [1, 2, 3, 4, 1],
        )
        cap = credit_gate.HardCreditCap(800, 416)
        allocator = critic.CapAwareRegenAllocator(
            cap, {1: 100, 2: 100, 3: 100, 4: 100}, 2
        )
        for shot in (1, 2, 3, 4):
            allocator.mark_main_authorized(shot)
        self.assertTrue(allocator.request(1, 1))
        self.assertTrue(cap.authorize("qc_regen", "omni", "6"))
        self.assertFalse(allocator.request(1, 2))
        self.assertTrue(allocator.request(2, 1))
        self.assertTrue(cap.authorize("qc_regen", "omni", "6"))
        self.assertTrue(allocator.request(3, 1))
        self.assertTrue(cap.authorize("qc_regen", "omni", "6"))
        self.assertFalse(allocator.request(4, 1))

    def test_negative_reviewer_note_becomes_positive_structured_correction(self):
        raw = "Do not change the object colour and never add a second object."
        rewritten = critic.strengthen_prompt("BASE", [raw], structured=True)
        self.assertNotIn(raw, rewritten)
        self.assertNotRegex(rewritten.lower(), r"\b(?:not|never|don't|without)\b")
        self.assertIn("Match the reference object's exact shape", rewritten)

    def test_legacy_prompt_path_is_byte_identical(self):
        expected = (
            "BASE\n\nCRITICAL CORRECTIONS — the previous take FAILED quality control. "
            "You MUST fix:\n- raw note"
        )
        self.assertEqual(critic.strengthen_prompt("BASE", ["raw note"]), expected)

    def test_installed_series_enables_only_measure_scene_scan_and_800_cap(self):
        path = pathlib.Path(__file__).resolve().parents[1] / "sentinal_ihsan/unnatural-lab/bible.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        qc = data["series"]["qc"]
        self.assertEqual(data["series"]["credit_hard_cap_value"], 800)
        self.assertEqual(data["series"]["credit_monthly_cap_value"], 14000)
        self.assertTrue(qc["require_all_shots"])
        self.assertTrue(qc["require_object_match"])
        self.assertTrue(qc["require_continuity"])
        self.assertTrue(qc["require_first_frame"])
        self.assertTrue(qc["scene_cut_scan"])
        self.assertIs(qc["scene_cut_fail"], False)


if __name__ == "__main__":
    unittest.main()
