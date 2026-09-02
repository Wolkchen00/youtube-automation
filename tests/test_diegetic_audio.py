"""ROCK 1 diegetic-audio delivery proofs."""

import contextlib
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core import cost_tracker, ffmpeg_tools
from series import bible as bible_module
from series import critic, preflight, produce, series_runner
from series.bible import Bible


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]


class MeanVolumeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("ffmpeg"):
            raise unittest.SkipTest("ffmpeg is not installed")

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = pathlib.Path(self.tempdir.name)

    def _ffmpeg(self, *args):
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", *map(str, args)],
            capture_output=True,
            check=True,
            timeout=60,
        )

    def test_tone_and_silence_are_distinguished(self):
        tone = self.root / "tone.mp4"
        silence = self.root / "silence.mp4"
        self._ffmpeg(
            "-f", "lavfi", "-i", "color=c=black:s=160x90:d=2",
            "-f", "lavfi", "-i", "sine=frequency=440:duration=2",
            "-shortest", "-c:v", "mpeg4", "-c:a", "aac", tone,
        )
        self._ffmpeg(
            "-f", "lavfi", "-i", "color=c=black:s=160x90:d=2",
            "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
            "-shortest", "-c:v", "mpeg4", "-c:a", "aac", silence,
        )
        self.assertGreater(ffmpeg_tools.measure_mean_volume(tone), -50.0)
        silent_volume = ffmpeg_tools.measure_mean_volume(silence)
        self.assertTrue(silent_volume is None or silent_volume < -50.0)

    def test_video_without_audio_stream_returns_none(self):
        video = self.root / "no-audio.mp4"
        self._ffmpeg(
            "-f", "lavfi", "-i", "color=c=black:s=160x90:d=2",
            "-an", "-c:v", "mpeg4", video,
        )
        self.assertIsNone(ffmpeg_tools.measure_mean_volume(video))


class AudioConfigAndQCTests(unittest.TestCase):
    def test_audio_fade_default_opt_in_and_range(self):
        self.assertEqual(Bible({"series": {"slug": "x"}}).audio_fade, 0.25)
        self.assertEqual(
            Bible({"series": {"slug": "x", "audio_fade": 0.06}}).audio_fade,
            0.06,
        )
        for value in (-0.01, 1.01, "invalid", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                Bible({"series": {"slug": "x", "audio_fade": value}}).audio_fade

    def test_qc_audio_requires_every_field_and_removes_temp_mp3(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            media = pathlib.Path(temp_dir) / "delivery.mp4"
            media.write_bytes(b"video")
            samples = []

            def extract(args, **_kwargs):
                sample = pathlib.Path(args[-1])
                sample.write_bytes(b"mp3")
                samples.append(sample)
                return mock.Mock(returncode=0)

            valid = {
                "has_music": False,
                "speech": False,
                "construction_sounds": ["hammer"],
                "silent_fraction_estimate": 0.1,
            }
            with mock.patch.object(critic.subprocess, "run", side_effect=extract), \
                    mock.patch.object(critic, "_review_audio", return_value=valid):
                self.assertEqual(critic.qc_audio(media), valid)
            self.assertTrue(samples)
            self.assertTrue(all(not sample.exists() for sample in samples))

            invalid = [
                {**valid, "has_music": 0},
                {**valid, "speech": "false"},
                {**valid, "construction_sounds": "hammer"},
                {**valid, "construction_sounds": [1]},
                {**valid, "silent_fraction_estimate": True},
                {**valid, "silent_fraction_estimate": 1.1},
                {key: value for key, value in valid.items() if key != "speech"},
                None,
            ]
            for response in invalid:
                with self.subTest(response=response), \
                        mock.patch.object(critic.subprocess, "run", side_effect=extract), \
                        mock.patch.object(critic, "_review_audio", return_value=response):
                    self.assertIsNone(critic.qc_audio(media))

    def test_delivery_gate_has_exactly_one_pass_case(self):
        bible = Bible({"series": {"slug": "audio-test", "title": "Audio Test"}})
        final = pathlib.Path("delivery.mp4")
        good = {
            "has_music": False,
            "speech": False,
            "construction_sounds": ["hammer"],
            "silent_fraction_estimate": 0.1,
        }
        failures = [
            {**good, "has_music": True},
            {**good, "speech": True},
            {**good, "construction_sounds": []},
            {**good, "silent_fraction_estimate": 0.8},
            None,
        ]
        for review in failures:
            with self.subTest(review=review), \
                    mock.patch.object(
                        produce.ffmpeg_tools, "measure_mean_volume", return_value=-20.0
                    ), mock.patch.object(produce.critic, "qc_audio", return_value=review), \
                    mock.patch.object(series_runner, "_series_alert") as send:
                self.assertFalse(produce._verify_native_audio_delivery(bible, 1, final))
                send.assert_called_once()
                self.assertIn("ELLE BAK", send.call_args.args[1])

        with mock.patch.object(
            produce.ffmpeg_tools, "measure_mean_volume", return_value=-20.0
        ), mock.patch.object(produce.critic, "qc_audio", return_value=good), \
                mock.patch.object(series_runner, "_series_alert") as send:
            self.assertTrue(produce._verify_native_audio_delivery(bible, 1, final))
            send.assert_not_called()


class ProductionIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = pathlib.Path(self.tempdir.name)
        self.channel = self.root / "channel"
        self.channel.mkdir()
        self.output = self.root / "output" / "series"
        self.slug = "audio-engine-test"
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

    def _write_series(self, required_layers, audio_fade=0.06):
        folder = self.channel / self.slug
        folder.mkdir()
        doctrine = "Audio test doctrine.\n"
        (self.channel / "KONSEPT.md").write_text(doctrine, encoding="utf-8")
        meta = {
            "slug": self.slug,
            "base_title": "Audio Test",
            "total_parts": 1,
            "next_part": 1,
            "status": "active",
            "parts": {},
        }
        (folder / "series.json").write_text(json.dumps(meta), encoding="utf-8")
        bible = {
            "series": {
                "slug": self.slug,
                "title": "Audio Test",
                "engine": "seedance",
                "chain_frames": False,
                "required_layers": required_layers,
                "audio_smooth": True,
                "audio_fade": audio_fade,
                "qc": {"enabled": False},
            },
            "music": False,
            "characters": [],
            "environments": [],
            "props": [],
        }
        (folder / "bible.json").write_text(json.dumps(bible), encoding="utf-8")
        plan = {
            "episode": {"number": 1, "title": "Offline"},
            "synopsis": "Offline audio proof.",
            "narration": "",
            "shots": [
                {"n": 1, "duration": "10", "prompt": "First detailed build action."},
                {"n": 2, "duration": "10", "prompt": "Second detailed build action."},
            ],
        }
        shots = self.output / self.slug / "episodes" / "ep01" / "shots"
        shots.mkdir(parents=True)
        for shot in plan["shots"]:
            (shots / f"shot_{shot['n']:02d}.mp4").write_bytes(b"cached")
        return plan

    @contextlib.contextmanager
    def _media_fakes(self):
        def write_output(*args, **_kwargs):
            target = pathlib.Path(args[1])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"video")
            return target

        with contextlib.ExitStack() as stack:
            calls = {}
            stack.enter_context(mock.patch.object(produce, "check_credit"))
            stack.enter_context(mock.patch.object(
                produce.ffmpeg_tools, "get_video_duration", return_value=10.0
            ))
            calls["smooth"] = stack.enter_context(mock.patch.object(
                produce.ffmpeg_tools, "concatenate_audio_smooth", side_effect=write_output
            ))
            stack.enter_context(mock.patch.object(
                produce.ffmpeg_tools, "concatenate_simple", side_effect=write_output
            ))
            stack.enter_context(mock.patch.object(
                produce.ffmpeg_tools, "final_export", side_effect=write_output
            ))
            stack.enter_context(mock.patch.object(produce.report, "append_row"))
            stack.enter_context(mock.patch.object(produce.report, "export_xlsx"))
            stack.enter_context(mock.patch.object(
                produce.report,
                "summarize",
                return_value={
                    "başarılı": 2,
                    "çekim_sayısı": 2,
                    "toplam_kredi": 0,
                    "toplam_dolar": 0,
                },
            ))
            yield calls

    def test_smooth_concat_receives_bible_audio_fade(self):
        plan = self._write_series([])
        with self._media_fakes() as calls:
            self.assertIsNotNone(produce.produce_episode(self.slug, plan))
        self.assertEqual(calls["smooth"].call_args.kwargs["fade"], 0.06)

    def test_produce_invalid_audio_fade_stops_cleanly_before_paid_call(self):
        plan = self._write_series([], audio_fade="invalid")
        with mock.patch.object(produce, "check_credit") as paid_call, \
                self.assertLogs(produce.logger.name, level="ERROR") as logs:
            self.assertIsNone(produce.produce_episode(self.slug, plan))
        paid_call.assert_not_called()
        self.assertIn("audio_fade", "\n".join(logs.output))

    def test_preflight_invalid_audio_fade_reports_error(self):
        plan = self._write_series([], audio_fade=1.01)
        plan_path = self.root / "plan.json"
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        errors, _trace = preflight.inspect(self.slug, plan_path)
        self.assertTrue(any("audio_fade" in error for error in errors), errors)

    def test_required_native_audio_silent_final_returns_none(self):
        plan = self._write_series(["native_audio"])
        with self._media_fakes(), mock.patch.object(
            produce.ffmpeg_tools, "measure_mean_volume", return_value=-80.0
        ), mock.patch.object(produce.critic, "qc_audio") as audio_qc, \
                mock.patch.object(series_runner, "_series_alert") as send:
            self.assertIsNone(produce.produce_episode(self.slug, plan))
        audio_qc.assert_not_called()
        send.assert_called_once()


class InstalledSeriesAssertions(unittest.TestCase):
    def test_from_scratch_is_the_only_audio_fade_opt_in(self):
        scratch = Bible.load("from-scratch")
        self.assertFalse(scratch.music)
        self.assertNotIn("music", scratch.required_layers)
        self.assertIn("native_audio", scratch.required_layers)
        self.assertEqual(scratch.audio_fade, 0.06)

        roots = [
            REPO_ROOT / "aimagine",
            REPO_ROOT / "sentinal_ihsan",
            REPO_ROOT / "shadowedhistory",
            REPO_ROOT / "galactic_experience",
        ]
        for root in roots:
            for path in root.glob("*/bible.json"):
                if path == REPO_ROOT / "aimagine" / "from-scratch" / "bible.json":
                    continue
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertNotIn("audio_fade", data.get("series", {}), str(path))

if __name__ == "__main__":
    unittest.main()
