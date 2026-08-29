"""Teslim ornekleme orani regresyonu.

29.08.2026'da part22'nin Instagram yeniden gonderimi su degisikligi raporladi:

    "audio: -> AAC 128k [44100, 48000] stereo (got 96000Hz, ch=2)"

Yani master'i 96 kHz teslim ettigimiz icin Instagram sesi KENDI encoder'iyla
yeniden kodladi. Bu, ROCK A'nin tum amacini - R128 garantisinin platforma kadar
BOZULMADAN gitmesini - sessizce iptal eder. 96 kHz yalniz limiter'in codec-arasi
tepeleri gorebilmesi icin asiri ornekleme alanidir; TESLIM bicimi degildir.
"""

import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core import ffmpeg_tools


class DeliverySampleRateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
            raise unittest.SkipTest("ffmpeg/ffprobe kurulu degil")

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = pathlib.Path(self.tempdir.name)

    def _source(self, sample_rate):
        """En kotu vaka: kaynak zaten platform disi bir oranda."""
        src = self.root / f"src_{sample_rate}.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
             "-f", "lavfi", "-i", "color=c=black:s=160x90:d=2:r=30",
             "-f", "lavfi", "-i",
             "aevalsrc=0.6*sin(2*PI*220*t)|0.5*sin(2*PI*440*t)"
             f":d=2:s={sample_rate}",
             "-c:v", "mpeg4", "-c:a", "aac", "-shortest", str(src)],
            capture_output=True, check=True, timeout=120,
        )
        return src

    @staticmethod
    def _audio_stream(path):
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a:0",
             "-show_entries", "stream=sample_rate,codec_name", "-of", "json",
             str(path)],
            capture_output=True, text=True, check=True, timeout=60,
        )
        return json.loads(probe.stdout)["streams"][0]

    def test_delivery_is_platform_native_rate(self):
        """Kaynak 96 kHz olsa bile teslim 48 kHz olmali."""
        out = self.root / "out96.mp4"
        ffmpeg_tools.master_audio(self._source(96000), out)
        stream = self._audio_stream(out)
        self.assertEqual(
            int(stream["sample_rate"]),
            ffmpeg_tools.DELIVERY_SAMPLE_RATE_HZ,
            "teslim orani platformun native kabul ettigi oranda degil; "
            "platform sesi yeniden kodlar ve master garantisi kaybolur",
        )
        self.assertEqual(stream["codec_name"], "aac")

    def test_delivery_rate_is_accepted_by_instagram_and_tiktok(self):
        """Instagram'in kabul ettigi oranlar: 44100 ve 48000 (canli olarak raporlandi)."""
        self.assertIn(ffmpeg_tools.DELIVERY_SAMPLE_RATE_HZ, (44100, 48000))

    def test_limiter_still_runs_oversampled(self):
        """Duzeltme, limiter'in asiri ornekleme korumasini KALDIRMAMALI."""
        self.assertGreater(
            ffmpeg_tools.LIMITER_OVERSAMPLE_HZ,
            ffmpeg_tools.DELIVERY_SAMPLE_RATE_HZ,
        )
        source = pathlib.Path(ffmpeg_tools.__file__).read_text(encoding="utf-8")
        limiter_index = source.index("alimiter=limit=")
        oversample_index = source.index("aresample={LIMITER_OVERSAMPLE_HZ}")
        downsample_index = source.index("aresample={DELIVERY_SAMPLE_RATE_HZ}")
        self.assertLess(oversample_index, limiter_index,
                        "asiri ornekleme limiter'den ONCE gelmeli")
        self.assertLess(limiter_index, downsample_index,
                        "asagi ornekleme limiter'den SONRA gelmeli")

    def test_delivery_preserves_r128_target(self):
        """Asagi ornekleme R128 hedefini bozmamali."""
        out = self.root / "loud.mp4"
        ffmpeg_tools.master_audio(self._source(48000), out, target_i=-14.0)
        measure = subprocess.run(
            ["ffmpeg", "-hide_banner", "-nostats", "-i", str(out), "-vn",
             "-af", "loudnorm=I=-14:TP=-1:LRA=11:print_format=json",
             "-f", "null", "-"],
            capture_output=True, text=True, timeout=180,
        )
        values = ffmpeg_tools._loudnorm_json(measure.stderr)
        self.assertAlmostEqual(float(values["input_i"]), -14.0, delta=1.0)
        self.assertLessEqual(float(values["input_tp"]), -1.0)

    def test_metadata_records_both_rates(self):
        """Operator, hangi oranin limiter hangisinin teslim oldugunu gorebilmeli."""
        out = self.root / "meta.mp4"
        ffmpeg_tools.master_audio(self._source(48000), out)
        meta = json.loads(
            out.with_suffix(".audio_master.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            meta["delivery_limiter"]["oversample_rate_hz"],
            ffmpeg_tools.LIMITER_OVERSAMPLE_HZ,
        )
        self.assertEqual(
            meta["delivery_limiter"]["delivery_rate_hz"],
            ffmpeg_tools.DELIVERY_SAMPLE_RATE_HZ,
        )


if __name__ == "__main__":
    unittest.main()
