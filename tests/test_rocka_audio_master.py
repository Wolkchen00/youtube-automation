"""ROCK A ses master zinciri regresyon ve fail-closed kanıtları."""

import contextlib
import hashlib
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
from series import produce
from series.bible import Bible


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
PILOT_DIR = (
    REPO_ROOT / "output" / "experiments" / "exp-2026-08-gerceklik"
    / "unnatural-lab-part22"
)


class LegacyByteIdentityTests(unittest.TestCase):
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

    @staticmethod
    def _sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def _video_and_audio(self):
        video = self.root / "program.mp4"
        voice = self.root / "voice.wav"
        music = self.root / "music.wav"
        self._ffmpeg(
            "-f", "lavfi", "-i", "color=c=black:s=160x90:d=1.5:r=30",
            "-f", "lavfi", "-i", "sine=frequency=330:duration=1.5:sample_rate=48000",
            "-shortest", "-c:v", "mpeg4", "-c:a", "aac", video,
        )
        self._ffmpeg(
            "-f", "lavfi", "-i", "sine=frequency=660:duration=0.8:sample_rate=48000",
            "-c:a", "pcm_s16le", voice,
        )
        self._ffmpeg(
            "-f", "lavfi", "-i", "sine=frequency=220:duration=0.7:sample_rate=48000",
            "-c:a", "pcm_s16le", music,
        )
        return video, voice, music

    def test_narrated_series_without_opt_in_is_byte_identical(self):
        video, voice, _music = self._video_and_audio()
        expected = self.root / "expected_narrated.mp4"
        actual = self.root / "actual_narrated.mp4"
        bible = Bible({"series": {"slug": "legacy-narrated"}})
        self.assertIsNone(bible.master_lufs)
        self._ffmpeg(
            "-i", video, "-i", voice,
            "-filter_complex",
            "[0:a]volume=0.5[bg];[1:a]volume=1.0[vo];"
            "[bg][vo]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "0:v", "-map", "[aout]", "-c:v", "copy",
            "-c:a", "aac", "-b:a", ffmpeg_tools.FFMPEG_AUDIO_BITRATE,
            "-shortest", expected,
        )
        ffmpeg_tools.mix_voiceover(
            video, voice, actual, voice_volume=1.0, bg_duck=0.5,
            amix_normalize=bible.master_lufs is None,
        )
        self.assertEqual(self._sha(expected), self._sha(actual))

    def test_replace_original_music_series_without_opt_in_is_byte_identical(self):
        video, _voice, music = self._video_and_audio()
        expected = self.root / "expected_music.mp4"
        actual = self.root / "actual_music.mp4"
        bible = Bible({"series": {"slug": "legacy-music"}})
        self.assertIsNone(bible.master_lufs)
        duration = ffmpeg_tools.get_video_duration(video)
        fade_out = max(0.0, duration - 1.5)
        bed = (
            f"[1:a]atrim=0:{duration:.2f},asetpts=PTS-STARTPTS,volume=0.9,"
            f"afade=t=in:st=0:d=1.0,afade=t=out:st={fade_out:.2f}:d=1.5[aout]"
        )
        self._ffmpeg(
            "-i", video, "-stream_loop", "-1", "-i", music,
            "-filter_complex", bed, "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "aac", "-b:a",
            ffmpeg_tools.FFMPEG_AUDIO_BITRATE, "-shortest", expected,
        )
        ffmpeg_tools.mix_background_music(
            video, music, actual, music_volume=0.9, replace_original=True,
        )
        self.assertEqual(self._sha(expected), self._sha(actual))


class InstalledBibleOptInTests(unittest.TestCase):
    def test_only_unnatural_lab_has_master_lufs(self):
        found = []
        for root_name in (
            "aimagine", "sentinal_ihsan", "shadowedhistory",
            "galactic_experience", "series_data",
        ):
            for path in (REPO_ROOT / root_name).glob("*/bible.json"):
                data = json.loads(path.read_text(encoding="utf-8"))
                if "master_lufs" in data.get("series", {}):
                    found.append((path, data["series"]["master_lufs"]))
        expected = REPO_ROOT / "sentinal_ihsan" / "unnatural-lab" / "bible.json"
        self.assertEqual(found, [(expected, -14)])


class ProductionMasterFailureTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = pathlib.Path(self.tempdir.name)
        self.channel = self.root / "channel"
        self.channel.mkdir()
        self.output = self.root / "output" / "series"
        self.slug = "rocka-production-test"
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

    def _write_series(self, *, upscale=False):
        folder = self.channel / self.slug
        folder.mkdir()
        (self.channel / "KONSEPT.md").write_text("ROCK A offline doctrine.\n", encoding="utf-8")
        (folder / "series.json").write_text(json.dumps({
            "slug": self.slug,
            "base_title": "ROCK A",
            "total_parts": 1,
            "next_part": 1,
            "status": "active",
            "parts": {},
        }), encoding="utf-8")
        series = {
            "slug": self.slug,
            "title": "ROCK A",
            "engine": "seedance",
            "chain_frames": False,
            "audio_smooth": False,
            "master_lufs": -14,
            "qc": {"enabled": False},
        }
        if upscale:
            series["upscale"] = {"enabled": True, "provider": "lanczos", "factor": "2"}
        (folder / "bible.json").write_text(json.dumps({
            "series": series,
            "music": False,
            "characters": [],
            "environments": [],
            "props": [],
        }), encoding="utf-8")
        plan = {
            "episode": {"number": 1, "title": "Offline"},
            "synopsis": "ROCK A offline proof.",
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
            target.write_bytes(b"video-with-audio")
            return target

        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch.object(produce, "check_credit"))
            stack.enter_context(mock.patch.object(
                produce.ffmpeg_tools, "get_video_duration", return_value=10.0
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
                produce.report, "summarize", return_value={
                    "başarılı": 2,
                    "çekim_sayısı": 2,
                    "toplam_kredi": 0,
                    "toplam_dolar": 0,
                },
            ))
            yield stack

    def test_mastering_failure_returns_qc_hold(self):
        plan = self._write_series()
        with self._media_fakes(), mock.patch.object(
            produce.ffmpeg_tools, "master_audio", side_effect=RuntimeError("measure failed")
        ):
            result = produce.produce_episode(self.slug, plan, typed_result=True)
        self.assertEqual(result.status, "qc_hold")
        self.assertIn("mastering", result.reason)

    def test_missing_audio_after_4k_remux_returns_qc_hold(self):
        plan = self._write_series(upscale=True)

        def master(_src, target, **_kwargs):
            target = pathlib.Path(target)
            target.write_bytes(b"mastered-audio")
            return target

        def upscale(_bible, _number, src, **_kwargs):
            target = pathlib.Path(src).with_name("returned_4k.mp4")
            target.write_bytes(b"4k-video-with-corrupt-audio")
            return target

        def measured(path):
            if pathlib.Path(path).name == "delivery_1080.mp4":
                return {"integrated_lufs": -14.0, "true_peak_dbtp": -1.0}
            return None

        with self._media_fakes(), \
                mock.patch.object(produce.ffmpeg_tools, "master_audio", side_effect=master), \
                mock.patch.object(produce, "_upscale_master", side_effect=upscale), \
                mock.patch.object(produce.ffmpeg_tools, "remux_audio") as remux, \
                mock.patch.object(
                    produce.ffmpeg_tools, "measure_audio_loudness", side_effect=measured
                ):
            result = produce.produce_episode(self.slug, plan, typed_result=True)
        remux.assert_called_once()
        self.assertEqual(result.status, "qc_hold")
        self.assertIn("4K", result.reason)


class CheckerFailureTests(unittest.TestCase):
    def test_off_target_pilot_delivery_exits_one(self):
        required = [
            PILOT_DIR / "ep22_narrated_music.mp4",
            PILOT_DIR / "ep22_raw.mp4",
            PILOT_DIR / "narration.wav",
            PILOT_DIR / "bg_music.mp3",
        ]
        if not all(path.exists() for path in required):
            self.skipTest("offline pilot fixture is not installed")
        command = [
            sys.executable, "-X", "utf8", str(REPO_ROOT / "tools" / "audio_master_check.py"),
            str(required[0]), "--ref-raw", str(required[1]),
            "--ref-tts", str(required[2]), "--ref-bed", str(required[3]),
            "--ref-premaster", str(required[0]), "--music-volume", "0.28",
            "--baseline-final", str(required[0]),
        ]
        result = subprocess.run(command, capture_output=True, text=True, timeout=600)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("integrated_lufs=-24.500", result.stdout)
        self.assertIn("RESULT=FAIL", result.stdout)

    def test_buried_foley_master_exits_one(self):
        required = [
            PILOT_DIR / "ep22.mp4",
            PILOT_DIR / "ep22_raw.mp4",
            PILOT_DIR / "narration.wav",
            PILOT_DIR / "bg_music.mp3",
            PILOT_DIR / "ep22_narrated_music.mp4",
        ]
        if not all(path.exists() for path in required):
            self.skipTest("offline pilot fixture is not installed")
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = pathlib.Path(temp_dir)
            narrated = temp / "buried_narrated.mp4"
            premaster = temp / "buried_premaster.mp4"
            mastered = temp / "buried_master.mp4"
            ffmpeg_tools.mix_voiceover(
                required[0], required[2], narrated,
                voice_volume=1.0, bg_duck=0.05, amix_normalize=False,
            )
            ffmpeg_tools.mix_background_music(
                narrated, required[3], premaster,
                music_volume=0.9,
            )
            ffmpeg_tools.master_audio(premaster, mastered)
            metadata = json.loads(
                mastered.with_suffix(".audio_master.json").read_text(encoding="utf-8")
            )
            self.assertEqual(metadata["apply_pass"]["normalization_type"], "dynamic")
            command = [
                sys.executable, "-X", "utf8",
                str(REPO_ROOT / "tools" / "audio_master_check.py"),
                str(mastered), "--ref-raw", str(required[1]),
                "--ref-tts", str(required[2]), "--ref-bed", str(required[3]),
                "--ref-premaster", str(premaster), "--music-volume", "0.9",
                "--baseline-final", str(required[4]),
            ]
            result = subprocess.run(command, capture_output=True, text=True, timeout=600)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("native_presence_violation_share=1.000000", result.stdout)
        self.assertIn("RESULT=FAIL", result.stdout)


if __name__ == "__main__":
    unittest.main()
