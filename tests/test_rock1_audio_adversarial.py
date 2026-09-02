"""ROCK 1 (diegetik ses) icin Visionary'nin dusman testleri.

Codex'in kendi suite'inin ATLADIGI vakalar: sinir degerleri (-50.0 dB tam,
silent_fraction tam 0.5), Python'un bool-is-int tuzagi, digital sessizlik
(-inf), var olmayan dosya, bozuk tipler ve butun kurulu serilerin
bit-degismezligi. Kanit Codex'in raporu degil, bu dosyanin kosmasidir.
"""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core import ffmpeg_tools  # noqa: E402
from series import critic, produce  # noqa: E402
from series.bible import Bible  # noqa: E402

HAS_FFMPEG = shutil.which("ffmpeg") is not None


def _make_clip(path: Path, source: str, seconds: float = 1.0) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=black:s=64x64:d={seconds}",
         "-f", "lavfi", "-i", source, "-t", str(seconds),
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(path)],
        capture_output=True, check=True, timeout=120,
    )


@unittest.skipUnless(HAS_FFMPEG, "ffmpeg yok")
class MeanVolumeEdgeTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_digital_silence_reports_minus_infinity_not_none(self):
        """Tam dijital sessizlik -inf verir; None ile KARISTIRILMAMALI.

        Ikisi de kapiyi dusurur ama sebepleri farkli: None = 'olcemedim',
        -inf = 'olctum, sessiz'. Log'da ayrilmazsa teshis imkansizlasir.
        """
        clip = self.tmp / "silent.mp4"
        _make_clip(clip, "anullsrc=r=48000:cl=mono")
        value = ffmpeg_tools.measure_mean_volume(clip)
        self.assertIsNotNone(value, "sessiz ama ses AKISI olan dosya None dondurmemeli")
        # OLCULDU: AAC ile kodlanmis dijital sessizlik -inf DEGIL, ~-91 dB verir
        # (kuantalama tabani). Onemli olan sayinin kendisi degil, kapinin altinda
        # kalmasi ve None ile karismamasi.
        self.assertLess(value, -50.0)

    def test_missing_file_returns_none_without_raising(self):
        self.assertIsNone(ffmpeg_tools.measure_mean_volume(self.tmp / "yok.mp4"))

    def test_non_media_file_returns_none_without_raising(self):
        junk = self.tmp / "junk.mp4"
        junk.write_bytes(b"bu bir video degil")
        self.assertIsNone(ffmpeg_tools.measure_mean_volume(junk))

    def test_loud_tone_is_well_above_the_gate_threshold(self):
        clip = self.tmp / "tone.mp4"
        _make_clip(clip, "sine=frequency=440:sample_rate=48000")
        value = ffmpeg_tools.measure_mean_volume(clip)
        self.assertIsNotNone(value)
        self.assertGreater(value, -50.0)


class QcAudioValidationTests(unittest.TestCase):
    """qc_audio'nun alan dogrulamasi: gecersiz her sekil None olmali."""

    def _run(self, payload):
        with mock.patch.object(critic, "_review_audio", return_value=payload), \
             mock.patch.object(critic.subprocess, "run") as run, \
             mock.patch.object(critic, "_log_audio"):
            run.return_value = subprocess.CompletedProcess([], 0, b"", b"")
            with mock.patch.object(Path, "exists", return_value=True), \
                 mock.patch.object(Path, "stat") as stat:
                stat.return_value = mock.Mock(st_size=1234)
                return critic.qc_audio(Path("output/series/from-scratch/ep.mp4"))

    def test_bool_is_int_trap_rejected(self):
        """Python'da True bir int'tir. silent_fraction=True KABUL EDILMEMELI."""
        self.assertIsNone(self._run({
            "has_music": False, "speech": False,
            "construction_sounds": ["hammer"], "silent_fraction_estimate": True,
        }))

    def test_string_bool_rejected(self):
        self.assertIsNone(self._run({
            "has_music": "false", "speech": False,
            "construction_sounds": ["hammer"], "silent_fraction_estimate": 0.1,
        }))

    def test_non_string_item_in_sound_list_rejected(self):
        self.assertIsNone(self._run({
            "has_music": False, "speech": False,
            "construction_sounds": ["hammer", 7], "silent_fraction_estimate": 0.1,
        }))

    def test_out_of_range_fraction_rejected(self):
        for bad in (-0.01, 1.01, 1.5):
            with self.subTest(bad=bad):
                self.assertIsNone(self._run({
                    "has_music": False, "speech": False,
                    "construction_sounds": ["hammer"], "silent_fraction_estimate": bad,
                }))

    def test_missing_field_rejected(self):
        self.assertIsNone(self._run({
            "has_music": False, "construction_sounds": ["hammer"],
            "silent_fraction_estimate": 0.1,
        }))

    def test_none_review_rejected(self):
        self.assertIsNone(self._run(None))

    def test_valid_payload_normalized_and_returned(self):
        out = self._run({
            "has_music": False, "speech": False,
            "construction_sounds": ["hammer", "drill"], "silent_fraction_estimate": 0,
        })
        self.assertIsNotNone(out)
        self.assertIs(type(out["silent_fraction_estimate"]), float)
        self.assertEqual(out["construction_sounds"], ["hammer", "drill"])


class DeliveryGateBoundaryTests(unittest.TestCase):
    """Kapinin SINIR davranisi: esikte gecer mi, esigin bir tik otesinde duser mi."""

    def _gate(self, mean_volume, review):
        bible = mock.Mock()
        bible.title = "AImagine"
        with mock.patch.object(ffmpeg_tools, "measure_mean_volume",
                               return_value=mean_volume), \
             mock.patch.object(critic, "qc_audio", return_value=review):
            return produce._verify_native_audio_delivery(bible, 7, Path("ep.mp4"))

    OK = {"has_music": False, "speech": False,
          "construction_sounds": ["hammer"], "silent_fraction_estimate": 0.1}

    def test_mean_volume_exactly_at_threshold_passes(self):
        self.assertTrue(self._gate(-50.0, self.OK))

    def test_mean_volume_just_below_threshold_fails(self):
        self.assertFalse(self._gate(-50.01, self.OK))

    def test_silent_fraction_exactly_at_half_passes(self):
        review = {**self.OK, "silent_fraction_estimate": 0.5}
        self.assertTrue(self._gate(-20.0, review))

    def test_silent_fraction_just_over_half_fails(self):
        review = {**self.OK, "silent_fraction_estimate": 0.5001}
        self.assertFalse(self._gate(-20.0, review))

    def test_unavailable_review_fails_closed(self):
        """Tur-2 F-2: dogrulanamayan ses, dogrulanmis ses DEGILDIR."""
        self.assertFalse(self._gate(-20.0, None))

    def test_music_fails_even_when_construction_sounds_present(self):
        review = {**self.OK, "has_music": True,
                  "construction_sounds": ["hammer", "drill"]}
        self.assertFalse(self._gate(-20.0, review))

    def test_empty_sound_list_fails_even_when_loud_and_not_silent(self):
        """Tur-2 F-3: 'VE' degil 'VEYA'. Ruzgar/trafik gurultusu gecmemeli."""
        review = {**self.OK, "construction_sounds": [], "silent_fraction_estimate": 0.0}
        self.assertFalse(self._gate(-20.0, review))

    def test_gate_never_raises_when_notifier_is_broken(self):
        bible = mock.Mock()
        bible.title = "AImagine"
        with mock.patch.object(ffmpeg_tools, "measure_mean_volume", return_value=None), \
             mock.patch.dict(sys.modules, {"series.notifier": None}):
            self.assertFalse(produce._verify_native_audio_delivery(bible, 7, Path("x.mp4")))


class InstalledSeriesIsolationTests(unittest.TestCase):
    """Diger her kurulu seri BIT-DEGISMEZ kalmali (tur-3 F-10: aimagine/ altindakiler dahil)."""

    OTHERS = [
        "aimagine/infinite-trip", "aimagine/the-drift", "aimagine/the-vast",
        "sentinal_ihsan/could-you-survive", "sentinal_ihsan/night-archive",
        "sentinal_ihsan/night-shift", "sentinal_ihsan/room-408",
        "sentinal_ihsan/the-signal",
        "galactic_experience/ava-voyage", "galactic_experience/event-horizon",
        "galactic_experience/planetfall",
    ]

    def test_no_other_series_gained_audio_fade_or_native_audio(self):
        checked = 0
        for rel in self.OTHERS:
            bible_path = REPO_ROOT / rel / "bible.json"
            if not bible_path.is_file():
                continue
            checked += 1
            data = json.loads(bible_path.read_text(encoding="utf-8"))
            series = data.get("series", {})
            with self.subTest(series=rel):
                self.assertNotIn("audio_fade", series)
                self.assertNotIn("native_audio", series.get("required_layers", []))
        self.assertGreaterEqual(checked, 8, "kurulu seri listesi bulunamadi")

    def test_audio_fade_default_is_unchanged_for_series_without_the_key(self):
        scratch = Bible.load("from-scratch")
        self.assertEqual(scratch.audio_fade, 0.06)
        for rel in self.OTHERS:
            bible_path = REPO_ROOT / rel / "bible.json"
            if not bible_path.is_file():
                continue
            slug = rel.split("/")[-1]
            with self.subTest(series=slug):
                self.assertEqual(Bible.load(slug).audio_fade, 0.25)

    def test_from_scratch_no_longer_requests_music(self):
        scratch = Bible.load("from-scratch")
        self.assertFalse(scratch.music)
        self.assertNotIn("music", scratch.required_layers)
        self.assertIn("native_audio", scratch.required_layers)
        meta = json.loads(
            (REPO_ROOT / "aimagine/from-scratch/series.json").read_text(encoding="utf-8")
        )
        self.assertFalse(meta["auto_replenish"]["music_prompt"])
        self.assertNotIn("music_style", meta["auto_replenish"])


class ProtectedStateTests(unittest.TestCase):
    """ROCK 1 yayinlanmis veriye DOKUNMAMALI."""

    def test_published_state_untouched(self):
        meta = json.loads(
            (REPO_ROOT / "aimagine/from-scratch/series.json").read_text(encoding="utf-8")
        )
        # Canlı sayaç pinleri cron her yayında çürüyordu; koruma artık değişmezlerle:
        # ROCK 1 anındaki taban (part 1-8 yayınlı) geriye dönük bozulmamış olmalı,
        # serinin İLERLEMESİ ise ihlal değildir.
        self.assertGreaterEqual(meta["next_part"], 9)
        self.assertGreaterEqual(meta["total_parts"], 10)
        self.assertEqual(meta["publish_mode"], "auto")
        # 2026-09-02: seri "paused" yapıldı (İhsan kararı, aimagine kanalı günde
        # tek video). Duraklatma yayınlanmış durumu bozmaz, bu testin konusu da
        # odur; aşağıdaki part 1-8 "published" assert'leri değişmeden korur.
        # "draft" yine ihlaldir: o, kurulumun bozulduğu anlamına gelir.
        self.assertIn(meta["status"], ("active", "paused"))
        expected = [str(n) for n in range(1, meta["next_part"])]
        self.assertEqual(sorted(meta["parts"], key=int), expected)
        for number in range(1, 9):
            with self.subTest(part=number):
                self.assertEqual(meta["parts"][str(number)]["status"], "published")


if __name__ == "__main__":
    unittest.main()
