"""Frozen PLAN_GERCEKCILIK_v1 ROCK 1 proofs (offline except local FFmpeg)."""

import array
import json
import math
import pathlib
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

# The narration unit tests never call the legacy SDK; keep collection offline when
# that optional package is absent, matching the existing doctrine tests.
google_package = sys.modules.setdefault("google", types.ModuleType("google"))
generativeai_module = types.ModuleType("google.generativeai")
sys.modules.setdefault("google.generativeai", generativeai_module)
setattr(google_package, "generativeai", generativeai_module)

from core import ffmpeg_tools, narration
from series import critic, produce, replenish
from series.bible import Bible
from series.series_meta import SeriesMeta
from series.shots import resolve_shot, resolve_visual_shot, validate_plan


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
UNNATURAL_ROOT = REPO_ROOT / "sentinal_ihsan" / "unnatural-lab"
ART_STYLE = (
    "Vertical 9:16 real-world footage: a pair of hands working with one ordinary "
    "object on a fixed workbench. The view stays in one unchanging position for "
    "the whole shot; the framing remains identical. Slight sensor grain in the shadows; "
    "window light clips to white on the bench edge; mixed warm lamp and cool daylight "
    "colour. Worn wood, real dust, natural imperfect surfaces. The face stays outside "
    "the frame. Exactly ONE impossible property is visibly active; everything else "
    "behaves normally."
)


def bible_data(*, slug="legacy-series", opt_in=False, narration_cfg=None):
    qc = {"enabled": True, "max_regens_per_shot": 1, "qc_review_retries": 0}
    series = {
        "slug": slug,
        "title": slug,
        "aspect_ratio": "9:16",
        "resolution": "1080p",
        "engine": "omni",
        "chain_frames": False,
        "qc": qc,
    }
    if opt_in:
        series.update({"face_visible": False, "omit_character_refs": True})
        qc.update({"native_audio_review": True, "require_no_face": True})
    return {
        "series": series,
        "art_style": "Recorded workshop footage.",
        "music": False,
        "narration": dict(narration_cfg or {}),
        "characters": [
            {
                "id": "registered",
                "name": "Registered",
                "character_id": "character-123",
                "ref_image_url": "https://example.invalid/registered.jpg",
            },
            {
                "id": "image-only",
                "name": "Image Only",
                "ref_image_url": "https://example.invalid/image-only.jpg",
            },
        ],
        "environments": [],
        "props": [],
    }


def visual_review(**values):
    review = {
        "anatomy_ok": True,
        "face_match": None,
        "wardrobe_ok": True,
        "era_ok": None,
        "unwanted_text": False,
        "forbidden_elements": False,
        "artifact_score": 0,
        "issues": [],
        "fix_notes": [],
        "face_present": False,
    }
    review.update(values)
    return review


def raw_review(*, foley=True, speech=False, music=False, notes="clean"):
    return {
        "has_foley": foley,
        "unwanted_speech": speech,
        "unwanted_music": music,
        "notes": notes,
    }


class NativeMixTests(unittest.TestCase):
    def _post_process_mix_level(self, narration_cfg):
        bible = Bible(bible_data(narration_cfg=narration_cfg))
        with tempfile.TemporaryDirectory() as temp_dir:
            root = pathlib.Path(temp_dir)
            video = root / "video.mp4"
            voice = root / "voice.wav"
            video.write_bytes(b"video")
            voice.write_bytes(b"voice")

            def mix(_video, _voice, target, **_kwargs):
                pathlib.Path(target).write_bytes(b"mixed")

            with mock.patch.object(
                narration, "create_narration_for_channel", return_value=(voice, "test")
            ), mock.patch.object(
                produce.ffmpeg_tools, "mix_voiceover", side_effect=mix
            ) as mixer:
                result = produce._post_process(
                    bible,
                    {"episode": {"number": 1}, "narration": "A short voice-over."},
                    video,
                )
        self.assertIsNotNone(result)
        return bible, mixer.call_args.kwargs["bg_duck"]

    def test_native_mix_level_flows_to_voiceover_mix(self):
        bible, level = self._post_process_mix_level(
            {"channel": "sentinal_vlog", "native_mix_level": 0.5}
        )
        self.assertEqual(bible.native_mix_level, 0.5)
        self.assertEqual(level, 0.5)

    def test_absent_native_mix_level_keeps_zero(self):
        bible, level = self._post_process_mix_level({"channel": "sentinal_vlog"})
        self.assertEqual(bible.native_mix_level, 0.0)
        self.assertEqual(level, 0.0)

    @unittest.skipUnless(shutil.which("ffmpeg"), "FFmpeg is required for media proof")
    def test_static_half_level_retains_native_tone_and_extractable_stem(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = pathlib.Path(temp_dir)
            source = root / "native.mp4"
            voice = root / "voice.wav"
            mixed = root / "mixed.mp4"
            stem = root / "stems" / "shot_01_attempt_00.wav"
            subprocess.run(
                [
                    "ffmpeg", "-loglevel", "error", "-y",
                    "-f", "lavfi", "-i", "color=c=black:s=64x64:r=25:d=1",
                    "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=16000:duration=1",
                    "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", str(source),
                ],
                check=True, capture_output=True, timeout=60,
            )
            subprocess.run(
                [
                    "ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
                    "sine=frequency=880:sample_rate=16000:duration=1", str(voice),
                ],
                check=True, capture_output=True, timeout=60,
            )
            with mock.patch.object(
                ffmpeg_tools, "get_video_duration", side_effect=[2.0, 1.0]
            ):
                ffmpeg_tools.mix_voiceover(source, voice, mixed, bg_duck=0.5)

            decoded = subprocess.run(
                [
                    "ffmpeg", "-loglevel", "error", "-i", str(mixed), "-map", "0:a:0",
                    "-ac", "1", "-ar", "16000", "-f", "f32le", "-",
                ],
                check=True, capture_output=True, timeout=60,
            ).stdout
            samples = array.array("f")
            samples.frombytes(decoded)

            def amplitude(frequency):
                count = len(samples)
                real = sum(
                    sample * math.cos(2 * math.pi * frequency * index / 16000)
                    for index, sample in enumerate(samples)
                )
                imag = sum(
                    sample * math.sin(2 * math.pi * frequency * index / 16000)
                    for index, sample in enumerate(samples)
                )
                return 2.0 * math.hypot(real, imag) / count

            self.assertGreater(amplitude(440), 0.01)
            self.assertGreater(amplitude(440), amplitude(880) * 0.25)
            self.assertEqual(ffmpeg_tools.extract_audio(source, stem), stem)
            astats = subprocess.run(
                [
                    "ffmpeg", "-hide_banner", "-i", str(stem), "-af", "astats",
                    "-f", "null", "-",
                ],
                check=True, capture_output=True, text=True, encoding="utf-8", timeout=60,
            )
            self.assertIn("RMS level dB", astats.stderr)
            self.assertNotIn("RMS level dB: -inf", astats.stderr)


class FaceGateTests(unittest.TestCase):
    def setUp(self):
        self.bible = Bible(bible_data(opt_in=True))
        self.qc = critic.qc_config(self.bible)
        self.frames = [pathlib.Path("frame.jpg")]

    def review(self, result):
        with mock.patch.object(
            critic.ffmpeg_tools, "sample_frames", return_value=self.frames
        ), mock.patch.object(critic, "_review_frames", return_value=result), mock.patch.object(
            critic, "_fetch_ref_face"
        ) as fetch:
            outcome = critic.review_clip(
                self.bible, {"n": 1, "characters": ["registered"]},
                pathlib.Path("clip.mp4"), "prompt", self.qc,
            )
        fetch.assert_not_called()
        return outcome

    def test_visible_face_fails_clip(self):
        review, verdict, reasons, _frames = self.review(
            visual_review(face_present=True)
        )
        self.assertTrue(review["face_present"])
        self.assertEqual(verdict, "fail")
        self.assertTrue(any("yüz" in reason for reason in reasons))

    def test_missing_or_null_face_field_and_reviewer_error_hold_closed(self):
        missing = visual_review()
        missing.pop("face_present")
        for response in (missing, visual_review(face_present=None), None):
            with self.subTest(response=response):
                _review, verdict, reasons, _frames = self.review(response)
                self.assertEqual(verdict, "hold")
                self.assertTrue(any("yüz" in reason for reason in reasons))

    def test_explicit_false_passes_face_gate(self):
        _review, verdict, reasons, _frames = self.review(visual_review())
        self.assertEqual(verdict, "pass")
        self.assertEqual(reasons, [])

    def test_qc_loop_cannot_auto_accept_face_reviewer_skip(self):
        self.bible.data["series"]["qc"]["native_audio_review"] = False
        with tempfile.TemporaryDirectory() as temp_dir:
            clip = pathlib.Path(temp_dir) / "shot.mp4"
            clip.write_bytes(b"clip")
            with mock.patch.object(
                critic, "review_clip", return_value=(None, "skip", ["offline"], [])
            ), mock.patch.object(critic, "_log_event"), mock.patch.object(
                critic, "_notify"
            ):
                result = critic.qc_shot(
                    self.bible, {"n": 1}, clip, "prompt", None,
                    episode=1, budget={"left": 0},
                )
        self.assertEqual(result[2], "hold")


class RawAudioGateTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = pathlib.Path(self.tempdir.name)

    def make_clip(self, name="shot_01.mp4"):
        clip = self.root / name
        clip.write_bytes(b"clip")
        return clip

    def opt_bible(self):
        return Bible(bible_data(slug="raw-audio-test", opt_in=True))

    def test_stem_is_persisted_under_episode_stems(self):
        clip = self.make_clip()

        def extract(_clip, target):
            target = pathlib.Path(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"wav")
            return target

        with mock.patch.object(
            critic, "episode_dir", return_value=self.root / "ep07"
        ), mock.patch.object(
            critic.ffmpeg_tools, "extract_audio", side_effect=extract
        ), mock.patch.object(
            critic, "_review_raw_native_audio", return_value=raw_review()
        ):
            review, verdict, reasons, stem = critic.review_raw_native_audio(
                self.opt_bible(), {"n": 3}, clip, episode=7, attempt=2
            )
        self.assertEqual(verdict, "pass")
        self.assertEqual(reasons, [])
        self.assertTrue(review["has_foley"])
        self.assertEqual(stem, self.root / "ep07" / "stems" / "shot_03_attempt_02.wav")
        self.assertTrue(stem.exists())

    def test_raw_schema_maps_speech_and_music_to_fail_and_no_foley_to_pass(self):
        clip = self.make_clip()

        def extract(_clip, target):
            target = pathlib.Path(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"wav")
            return target

        cases = (
            (raw_review(speech=True), "fail", "konuşma"),
            (raw_review(music=True), "fail", "müzik"),
            (raw_review(foley=False), "pass", None),
        )
        for payload, expected, reason_word in cases:
            with self.subTest(payload=payload), mock.patch.object(
                critic, "episode_dir", return_value=self.root / "ep01"
            ), mock.patch.object(
                critic.ffmpeg_tools, "extract_audio", side_effect=extract
            ), mock.patch.object(
                critic, "_review_raw_native_audio", return_value=payload
            ):
                review, verdict, reasons, _stem = critic.review_raw_native_audio(
                    self.opt_bible(), {"n": 1}, clip, episode=1, attempt=0
                )
            self.assertEqual(verdict, expected)
            self.assertEqual(review, payload)
            if reason_word:
                self.assertTrue(any(reason_word in reason for reason in reasons))
            else:
                self.assertEqual(reasons, [])

    def _assert_unwanted_layer_regenerates(self, review):
        clip = self.make_clip()
        bible = self.opt_bible()
        budget = {"left": 1}

        def download(_url, target):
            pathlib.Path(target).write_bytes(b"regen")
            return True

        with mock.patch.object(
            critic, "review_raw_native_audio",
            side_effect=[(review, "fail", ["unwanted"], self.root / "bad.wav"),
                         (raw_review(), "pass", [], self.root / "good.wav")],
        ), mock.patch.object(
            critic, "review_clip", return_value=(visual_review(), "pass", [], [])
        ), mock.patch.object(
            critic, "download_file", side_effect=download
        ), mock.patch.object(critic, "_log_event"), mock.patch.object(critic, "_notify"):
            path, credits, status = critic.qc_shot(
                bible, {"n": 1}, clip, "prompt",
                lambda _prompt: {"url": "regen", "credits": 84},
                episode=1, budget=budget,
            )
        self.assertEqual((path, credits, status), (clip, 84.0, "pass"))
        self.assertEqual(budget["left"], 0)

    def test_unwanted_speech_and_music_each_use_existing_regen_path(self):
        for review in (
            raw_review(speech=True, notes="speech"),
            raw_review(music=True, notes="music"),
        ):
            with self.subTest(review=review):
                self._assert_unwanted_layer_regenerates(review)

    def test_no_foley_logs_counter_but_does_not_fail_or_regenerate(self):
        clip = self.make_clip()
        bible = self.opt_bible()
        regen = mock.Mock()
        budget = {"left": 1}
        with mock.patch.object(
            critic, "review_raw_native_audio",
            return_value=(raw_review(foley=False), "pass", [], self.root / "stem.wav"),
        ), mock.patch.object(
            critic, "review_clip", return_value=(visual_review(), "pass", [], [])
        ), mock.patch.object(critic, "_log_event") as log_event, mock.patch.object(
            critic, "_notify"
        ):
            result = critic.qc_shot(
                bible, {"n": 1}, clip, "prompt", regen, episode=1, budget=budget
            )
        self.assertEqual(result, (clip, 0.0, "pass"))
        regen.assert_not_called()
        self.assertEqual(budget["left"], 1)
        self.assertEqual(budget["no_foley_count"], 1)
        native_logs = [
            call.args[1] for call in log_event.call_args_list
            if call.args[1].get("event") == "native_audio_review"
        ]
        self.assertEqual(native_logs[0]["no_foley_count"], 1)
        self.assertFalse(native_logs[0]["has_foley"])

    def test_raw_audio_reviewer_error_fails_closed(self):
        clip = self.make_clip()
        with mock.patch.object(
            critic, "review_raw_native_audio",
            return_value=(None, "fail", ["reviewer error"], None),
        ), mock.patch.object(critic, "review_clip") as visual, mock.patch.object(
            critic, "_log_event"
        ), mock.patch.object(critic, "_notify"):
            result = critic.qc_shot(
                self.opt_bible(), {"n": 1}, clip, "prompt", None,
                episode=1, budget={"left": 0},
            )
        self.assertEqual(result[2], "hold")
        visual.assert_not_called()


class ConfigIsolationTests(unittest.TestCase):
    def test_non_opt_in_series_keeps_character_refs_and_skips_raw_review(self):
        bible = Bible(bible_data())
        shot = {"n": 1, "duration": "6", "prompt": "Hands work.",
                "characters": ["registered", "image-only"]}
        resolved = resolve_shot(bible, shot)["kwargs"]
        visual = resolve_visual_shot(bible, shot)
        self.assertEqual(resolved["character_ids"], ["character-123"])
        self.assertEqual(resolved["image_urls"], ["https://example.invalid/image-only.jpg"])
        self.assertEqual(visual["start_image_url"], "https://example.invalid/registered.jpg")
        self.assertEqual(bible.native_mix_level, 0.0)

        with tempfile.TemporaryDirectory() as temp_dir:
            clip = pathlib.Path(temp_dir) / "shot.mp4"
            clip.write_bytes(b"clip")
            with mock.patch.object(
                critic, "review_clip", return_value=(visual_review(), "pass", [], [])
            ), mock.patch.object(
                critic, "review_raw_native_audio"
            ) as raw_audio, mock.patch.object(critic, "_log_event"), mock.patch.object(
                critic, "_notify"
            ):
                result = critic.qc_shot(
                    bible, {"n": 1}, clip, "prompt", None,
                    episode=1, budget={"left": 0},
                )
        self.assertEqual(result, (clip, 0.0, "pass"))
        raw_audio.assert_not_called()
        self.assertEqual(critic._decide(visual_review(face_present=True),
                                        critic.qc_config(bible), False), ("pass", []))

    def test_unnatural_config_removes_refs_and_requires_face_false_plan(self):
        bible = Bible(bible_data(opt_in=True))
        shot = {"n": 1, "duration": "6", "prompt": "Hands work.",
                "characters": ["registered", "image-only"]}
        self.assertEqual(resolve_shot(bible, shot)["kwargs"]["character_ids"], [])
        self.assertEqual(resolve_shot(bible, shot)["kwargs"]["image_urls"], [])
        self.assertIsNone(resolve_visual_shot(bible, shot)["start_image_url"])
        plan = {"shots": [shot]}
        self.assertTrue(validate_plan(plan, bible)["errors"])
        plan["face_visible"] = False
        self.assertEqual(validate_plan(plan, bible)["errors"], [])

    def test_planner_disables_featured_face_encouragement_only_for_opt_in_bible(self):
        meta = SeriesMeta.load("unnatural-lab")
        bible = Bible.load("unnatural-lab")
        contents, system = replenish._build_prompt(
            meta, bible, meta.auto_replenish, 30, 1, []
        )
        self.assertIn('"face_visible": false', system)
        self.assertIn("hands and forearms working at bench level", system)
        self.assertNotIn("emotional anchor of the episode", system)
        self.assertIn("environments: workbench_main", contents)
        self.assertNotIn("characters: ihsan_maker", contents)
        self.assertNotIn('"characters": ["<ref id, optional>"]', system)

    def test_normalizer_persists_face_visible_false_for_opt_in_bible(self):
        bible = Bible(bible_data(opt_in=True))
        raw = {
            "episode": {"number": 1, "title": "Hands Work"},
            "synopsis": "Hands work with one object.",
            "face_visible": False,
            "narration": "",
            "shots": [
                {"n": 1, "duration": "8", "prompt": "Hands guide one object across worn wood."},
                {"n": 2, "duration": "8", "prompt": "Hands turn the same object in window light."},
            ],
        }
        episodes = [raw]
        self.assertEqual(
            replenish._validate_batch(episodes, bible, 1, 1, set(), {}), []
        )
        self.assertIs(episodes[0]["face_visible"], False)


class LiveConfigTests(unittest.TestCase):
    def test_art_style_is_exact_frozen_text_and_flags_are_opt_in(self):
        data = json.loads((UNNATURAL_ROOT / "bible.json").read_text(encoding="utf-8"))
        self.assertEqual(data["art_style"], ART_STYLE)
        self.assertEqual(data["narration"]["native_mix_level"], 0.5)
        self.assertIs(data["series"]["face_visible"], False)
        self.assertIs(data["series"]["omit_character_refs"], True)
        self.assertIs(data["series"]["qc"]["native_audio_review"], True)
        self.assertIs(data["series"]["qc"]["require_no_face"], True)

    def test_pending_plans_and_workflow_carry_rock1_gates(self):
        for number in range(22, 26):
            plan = json.loads(
                (UNNATURAL_ROOT / "plans" / f"part{number:02d}.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertIs(plan["face_visible"], False)
        workflow = (REPO_ROOT / ".github" / "workflows" / "unnatural-lab.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("output/series/unnatural-lab/episodes/*/stems/", workflow)
        self.assertIn("unnatural-lab-raw-audio-${{ github.run_number }}", workflow)
        self.assertGreaterEqual(workflow.count("retention-days: 7"), 2)


if __name__ == "__main__":
    unittest.main()
