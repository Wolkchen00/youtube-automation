"""Master geri donusu: son deneme bozulursa onceki teslim edilebilir deneme teslim edilir.

2026-09-28, wild-encounter Part 18 (kosu 36499804066). Klip odendi, QC gecti,
sonra ses master'inda cope gitti:

    deneme 1: -1.0 dBTP / -15.4 LUFS   (tavan ve -18 tabani tutuyor)
    deneme 2: -0.7 dBTP / -14.3 LUFS   (+1.4 dB telafi, AAC tepeyi tasirdi)
    deneme 3: -0.4 dBTP / -14.4 LUFS   (tavan -1.5'e indi, tepe DAHA da tasti)

Politika sesi yukseltmeyi denemekte hakliydi; hata, elde teslim edilebilir bir
master varken son denemenin reddiyle o master'in da atilmasiydi. Bu testler
geri donusu, sinirlarini ve iz birakmasini kilitler.
"""

from __future__ import annotations

import json
import pathlib
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core import ffmpeg_tools  # noqa: E402


_REPORT = (
    '{ "input_i" : "-18.0", "input_tp" : "-2.0", "input_lra" : "7.0",'
    ' "input_thresh" : "-28.0", "output_i" : "-14.0", "output_tp" : "-1.0",'
    ' "output_lra" : "7.0", "output_thresh" : "-24.0",'
    ' "normalization_type" : "linear", "target_offset" : "0.0" }'
)

PART18 = (
    {"integrated_lufs": -15.4, "true_peak_dbtp": -1.0},
    {"integrated_lufs": -14.3, "true_peak_dbtp": -0.7},
    {"integrated_lufs": -14.4, "true_peak_dbtp": -0.4},
)


class MasterFallbackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="rf_geri_donus_"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.src = self.tmp / "premaster.mp4"
        self.src.write_bytes(b"premaster")
        self.out = self.tmp / "master.mp4"
        self.encodes = 0
        patcher = mock.patch.object(ffmpeg_tools, "LOGS_DIR", self.tmp / "logs")
        patcher.start()
        self.addCleanup(patcher.stop)

    def _fake_run(self, command, **_kwargs):
        if "-f" in command and "null" in command:
            return mock.Mock(returncode=0, stdout="", stderr=(
                '{ "input_i" : "-18.0", "input_tp" : "-2.0", "input_lra" : "7.0",'
                ' "input_thresh" : "-28.0", "target_offset" : "0.0" }'
            ))
        self.encodes += 1
        # Her deneme ayirt edilebilir bayt yazar: hangisinin teslim edildigi okunur.
        self.out.write_bytes(f"deneme-{self.encodes}".encode())
        return mock.Mock(returncode=0, stdout="", stderr=_REPORT)

    def _run(self, readings, **kw):
        it = iter(readings)
        last = readings[-1]
        with mock.patch.object(ffmpeg_tools.subprocess, "run", side_effect=self._fake_run), \
             mock.patch.object(ffmpeg_tools, "measure_audio_loudness",
                               side_effect=lambda _p: next(it, last)):
            return ffmpeg_tools.master_audio(
                self.src, self.out, target_i=-14.0, target_tp=-1.0, **kw
            )

    def test_part18_numbers_deliver_the_first_attempt_instead_of_nothing(self):
        result = self._run(PART18, lufs_floor=-18.0)
        self.assertEqual(pathlib.Path(result).read_bytes(), b"deneme-1",
                         "teslim edilen dosya deneme 1 olmali, bozuk son deneme degil")
        self.assertEqual(self.encodes, 3, "politika yine de yukseltmeyi denemeli")

    def test_the_fallback_is_never_silent(self):
        self._run(PART18, lufs_floor=-18.0)
        written = list((self.tmp / "logs").glob("master_attempts_*.json"))
        self.assertTrue(written, "geri donus logs/ altina iz birakmali")
        reason = json.loads(written[-1].read_text(encoding="utf-8"))["reason"]
        self.assertIn("deneme 1 teslim edildi", reason)
        self.assertIn("floor", reason)

    def test_metadata_describes_the_delivered_attempt(self):
        self._run(PART18, lufs_floor=-18.0)
        meta = json.loads(self.out.with_suffix(".audio_master.json").read_text(encoding="utf-8"))
        self.assertEqual(len(meta["delivery_limiter"]["attempts"]), 3)
        self.assertAlmostEqual(meta["delivery_limiter"]["limit"], 10 ** (-1.0 / 20.0), places=6,
                               msg="teslim edilen denemenin tavani yazilmali")

    def test_no_leftover_side_file(self):
        self._run(PART18, lufs_floor=-18.0)
        self.assertEqual(
            sorted(p.name for p in self.tmp.glob("master_teslim_edilebilir*")), [],
            "kenara kopya teslimden sonra silinmeli",
        )

    def test_without_a_floor_the_strict_contract_still_raises(self):
        """Taban secmemis seri eskisi gibi kalir: pencere disi teslim yok."""
        with self.assertRaises(RuntimeError) as caught:
            self._run(PART18)
        self.assertIn("denemede", str(caught.exception))

    def test_a_peak_over_the_ceiling_is_never_a_fallback(self):
        """Tavan asan deneme hicbir zaman kenara alinmaz: taban tepeyi affetmez."""
        readings = (
            {"integrated_lufs": -15.4, "true_peak_dbtp": -0.9},
            {"integrated_lufs": -15.0, "true_peak_dbtp": -0.6},
            {"integrated_lufs": -14.6, "true_peak_dbtp": -0.3},
        )
        with self.assertRaises(RuntimeError):
            self._run(readings, lufs_floor=-18.0)

    def test_below_the_floor_is_never_a_fallback(self):
        readings = (
            {"integrated_lufs": -19.0, "true_peak_dbtp": -1.2},
            {"integrated_lufs": -17.4, "true_peak_dbtp": -0.6},
            {"integrated_lufs": -17.2, "true_peak_dbtp": -0.3},
        )
        with self.assertRaises(RuntimeError):
            self._run(readings, lufs_floor=-18.0)

    def test_the_latest_deliverable_attempt_wins(self):
        """Iki teslim edilebilir deneme varsa yuksek (hedefe yakin) olan, yani sonraki."""
        readings = (
            {"integrated_lufs": -15.5, "true_peak_dbtp": -1.2},
            {"integrated_lufs": -15.2, "true_peak_dbtp": -1.1},
            {"integrated_lufs": -14.8, "true_peak_dbtp": -0.5},
        )
        result = self._run(readings, lufs_floor=-18.0)
        self.assertEqual(self.encodes, 3)
        self.assertEqual(pathlib.Path(result).read_bytes(), b"deneme-2")

    def test_the_delivered_file_passes_the_production_verifier(self):
        """Iki kapi ayni sozlesmeyi konusmali (20 Eyl ep12 dersi)."""
        from series import produce

        self._run(PART18, lufs_floor=-18.0)
        with mock.patch.object(produce.ffmpeg_tools, "measure_audio_loudness",
                               return_value=dict(PART18[0])):
            self.assertTrue(produce._verify_audio_master(self.out, -14.0, lufs_floor=-18.0))


if __name__ == "__main__":
    unittest.main()
