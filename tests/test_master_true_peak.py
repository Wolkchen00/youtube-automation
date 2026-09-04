"""ROCK A true-peak teslimi ve seri izolasyonu kanitlari."""

import inspect
import json
import pathlib
import shutil
import subprocess
import sys
import unittest
import uuid
from types import SimpleNamespace
from unittest import mock


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core import ffmpeg_tools
from series import produce


TEST_ROOT = pathlib.Path(__file__).resolve().parent


class MasterTruePeakTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
            raise unittest.SkipTest("ffmpeg/ffprobe kurulu degil")

    def setUp(self):
        self.prefix = f"_master_true_peak_{uuid.uuid4().hex}_"
        self.root = TEST_ROOT
        self.addCleanup(self._cleanup)

    def _path(self, name: str) -> pathlib.Path:
        return self.root / f"{self.prefix}{name}"

    def _cleanup(self):
        for path in self.root.glob(f"{self.prefix}*"):
            path.unlink(missing_ok=True)

    def _ffmpeg(self, *args):
        subprocess.run(
            ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *map(str, args)],
            capture_output=True,
            check=True,
            timeout=180,
        )

    def _three_layer_premaster(self, *, harsh: bool) -> pathlib.Path:
        """Native + anlatim + muzik benzeri gercek, kayipli iki miks kur."""
        native = self._path("native.mp4")
        voice = self._path("voice.wav")
        music = self._path("music.wav")
        narrated = self._path("narrated.mp4")
        premaster = self._path("premaster.mp4")
        duration = 6

        if harsh:
            # Nyquist'e yakin, fazlari farkli karemsi katmanlar AAC decode ve
            # 96 -> 48 kHz donusumunde ornekler-arasi tepeyi belirginlestirir.
            native_signal = (
                "aevalsrc=0.72*sgn(sin(2*PI*17300*t))+"
                "0.24*sin(2*PI*19100*t):d=6:s=48000"
            )
            voice_signal = (
                "aevalsrc=0.78*sgn(sin(2*PI*18100*t+0.7))+"
                "0.18*sin(2*PI*15700*t):d=6:s=48000"
            )
            music_signal = (
                "aevalsrc=0.75*sgn(sin(2*PI*16700*t+1.1))+"
                "0.20*sin(2*PI*19900*t):d=6:s=48000"
            )
        else:
            native_signal = "sine=frequency=997:duration=6:sample_rate=48000"
            voice_signal = "sine=frequency=2200:duration=6:sample_rate=48000"
            music_signal = "sine=frequency=440:duration=6:sample_rate=48000"

        self._ffmpeg(
            "-f", "lavfi", "-i", "color=c=black:s=160x90:d=6:r=30",
            "-f", "lavfi", "-i", native_signal,
            "-shortest", "-c:v", "mpeg4", "-c:a", "aac", "-b:a", "192k", native,
        )
        self._ffmpeg("-f", "lavfi", "-i", voice_signal, "-c:a", "pcm_f32le", voice)
        self._ffmpeg("-f", "lavfi", "-i", music_signal, "-c:a", "pcm_f32le", music)

        ffmpeg_tools.mix_voiceover(
            native,
            voice,
            narrated,
            voice_volume=1.0,
            bg_duck=0.5,
            amix_normalize=False,
        )
        ffmpeg_tools.mix_background_music(
            narrated,
            music,
            premaster,
            music_volume=0.5,
            limit_mix_peak=True,
        )
        return premaster

    def _assert_delivery_contract(self, source: pathlib.Path, name: str):
        mastered = self._path(name)
        ffmpeg_tools.master_audio(source, mastered)
        measured = ffmpeg_tools.measure_audio_loudness(mastered)
        self.assertIsNotNone(measured, "teslim sesi olculemedi")
        self.assertLessEqual(measured["true_peak_dbtp"], -1.0)
        self.assertLessEqual(abs(measured["integrated_lufs"] + 14.0), 1.0)

    def test_hf_three_layer_delivery_meets_lufs_and_true_peak(self):
        self._assert_delivery_contract(
            self._three_layer_premaster(harsh=True), "hf_mastered.mp4"
        )

    def test_previously_passing_unnatural_input_still_passes(self):
        self._assert_delivery_contract(
            self._three_layer_premaster(harsh=False), "baseline_mastered.mp4"
        )


class MixIsolationTests(unittest.TestCase):
    def test_background_mix_peak_limit_defaults_off(self):
        parameter = inspect.signature(
            ffmpeg_tools.mix_background_music
        ).parameters["limit_mix_peak"]
        self.assertIs(parameter.default, False)

    def test_produce_enables_music_peak_limit_only_with_master_lufs(self):
        function_source = inspect.getsource(produce._post_process)
        self.assertIn("limit_mix_peak=bible.master_lufs is not None", function_source)

    def test_both_opted_in_normalize_zero_mixes_have_limiter(self):
        with mock.patch.object(
            ffmpeg_tools, "get_video_duration", side_effect=[10.0, 5.0]
        ), mock.patch.object(ffmpeg_tools.subprocess, "run") as run:
            ffmpeg_tools.mix_voiceover(
                "native.mp4", "voice.wav", "narrated.mp4", amix_normalize=False
            )
        command = run.call_args.args[0]
        voice_filter = command[command.index("-filter_complex") + 1]
        self.assertIn("normalize=0", voice_filter)
        self.assertIn("alimiter=limit=", voice_filter)

        with mock.patch.object(
            ffmpeg_tools, "get_video_duration", return_value=10.0
        ), mock.patch.object(ffmpeg_tools.subprocess, "run") as run:
            ffmpeg_tools.mix_background_music(
                "narrated.mp4", "music.wav", "mixed.mp4", limit_mix_peak=True
            )
        command = run.call_args.args[0]
        music_filter = command[command.index("-filter_complex") + 1]
        self.assertIn("normalize=0", music_filter)
        self.assertIn("alimiter=limit=", music_filter)


class MasterRetryControlTests(unittest.TestCase):
    def setUp(self):
        self.prefix = f"_master_retry_{uuid.uuid4().hex}_"
        self.source = TEST_ROOT / f"{self.prefix}source.mp4"
        self.output = TEST_ROOT / f"{self.prefix}output.mp4"
        self.source.write_bytes(b"premaster")
        self.addCleanup(self._cleanup)

    def _cleanup(self):
        for path in TEST_ROOT.glob(f"{self.prefix}*"):
            path.unlink(missing_ok=True)

    @staticmethod
    def _measure_values():
        return {
            "input_i": -14.0,
            "input_tp": 0.0,
            "input_lra": 1.0,
            "input_thresh": -24.0,
            "target_offset": 0.0,
        }

    @staticmethod
    def _apply_report():
        return {
            "normalization_type": "linear",
            "output_i": "-14.0",
            "output_tp": "-1.0",
            "output_lra": "1.0",
            "output_thresh": "-24.0",
        }

    def _run_side_effect(self, command, **_kwargs):
        if command[-1] != "-":
            pathlib.Path(command[-1]).write_bytes(b"delivery")
        return SimpleNamespace(returncode=0, stderr="ok", stdout="")

    def test_retry_feedback_always_renders_from_unchanged_premaster(self):
        measurements = [
            {"integrated_lufs": -14.0, "true_peak_dbtp": -0.4},
            {"integrated_lufs": -14.1, "true_peak_dbtp": -1.1},
        ]
        with mock.patch.object(
            ffmpeg_tools.subprocess, "run", side_effect=self._run_side_effect
        ) as run, mock.patch.object(
            ffmpeg_tools, "_loudnorm_measurement", return_value=self._measure_values()
        ), mock.patch.object(
            ffmpeg_tools, "_loudnorm_json", return_value=self._apply_report()
        ), mock.patch.object(
            ffmpeg_tools, "measure_audio_loudness", side_effect=measurements
        ):
            ffmpeg_tools.master_audio(self.source, self.output)

        apply_commands = [
            call.args[0] for call in run.call_args_list if call.args[0][-1] != "-"
        ]
        self.assertEqual(len(apply_commands), 2)
        self.assertTrue(all(
            command[command.index("-i") + 1] == str(self.source)
            for command in apply_commands
        ))
        metadata = json.loads(
            self.output.with_suffix(".audio_master.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(metadata["delivery_limiter"]["attempts"]), 2)
        self.assertLess(
            metadata["delivery_limiter"]["attempts"][1]["limit_db"],
            metadata["delivery_limiter"]["attempts"][0]["limit_db"],
        )

    def test_three_failed_attempts_fail_closed(self):
        off_target = {"integrated_lufs": -14.0, "true_peak_dbtp": -0.4}
        with mock.patch.object(
            ffmpeg_tools.subprocess, "run", side_effect=self._run_side_effect
        ), mock.patch.object(
            ffmpeg_tools, "_loudnorm_measurement", return_value=self._measure_values()
        ), mock.patch.object(
            ffmpeg_tools, "_loudnorm_json", return_value=self._apply_report()
        ), mock.patch.object(
            ffmpeg_tools, "measure_audio_loudness", return_value=off_target
        ) as measured:
            with self.assertRaisesRegex(RuntimeError, "3 denemede"):
                ffmpeg_tools.master_audio(self.source, self.output)

        self.assertEqual(measured.call_count, 3)
        self.assertFalse(self.output.exists())
        self.assertFalse(self.output.with_suffix(".audio_master.json").exists())


if __name__ == "__main__":
    unittest.main()
