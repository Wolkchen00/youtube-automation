"""Kirpilan anlatim artik SESSIZ kalmiyor.

Bulunan hata: mix_voiceover, anlatim 1.05x hiz ve 3.0 sn uzatmaya ragmen videoya
sigmayinca sesin sonunu kesiyordu. Bunu YALNIZ log'a yaziyor, cagirana
soylemiyordu. Sonuc: produce narration_ok=True kuruyor, coherence
"narration_delivered": true diyor, yayin kapisi geciyor ve bolum SONU KESIK
anlatimla yayinlaniyordu. Yani part 29'u durdurmak icin kurulan kapinin
yanindan ayni kusur baska bir kapidan giriyordu.

Duzeltme: opsiyonel `report` sozlugu. Verilmezse davranis birebir eski.
"""
from __future__ import annotations

import ast
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core import ffmpeg_tools  # noqa: E402

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]


def _ffmpeg(*args):
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-nostats", *args],
                   capture_output=True, check=True, timeout=300)


class NarrationCappedReportTests(unittest.TestCase):
    """Gercek ffmpeg ile: kirpma olunca rapor bunu SOYLEMELI."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = pathlib.Path(tempfile.mkdtemp(prefix="narr_cap_"))
        cls.addClassCleanup(shutil.rmtree, cls.tmp, ignore_errors=True)
        cls.kisa_video = cls.tmp / "kisa.mp4"
        cls.uzun_video = cls.tmp / "uzun.mp4"
        cls.uzun_ses = cls.tmp / "uzun.wav"
        cls.kisa_ses = cls.tmp / "kisa.wav"
        _ffmpeg("-f", "lavfi", "-i", "color=c=black:s=270x480:d=3",
                "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-shortest",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
                str(cls.kisa_video))
        _ffmpeg("-f", "lavfi", "-i", "color=c=black:s=270x480:d=20",
                "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-shortest",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
                str(cls.uzun_video))
        _ffmpeg("-f", "lavfi", "-i", "sine=frequency=440:duration=20",
                str(cls.uzun_ses))
        _ffmpeg("-f", "lavfi", "-i", "sine=frequency=440:duration=2",
                str(cls.kisa_ses))

    def test_sigmayan_anlatim_raporda_capped_isaretlenir(self):
        """3 sn video + 20 sn anlatim: 1.05x hiz ve 3 sn uzatma yetmez."""
        rapor: dict = {}
        cikti = self.tmp / "kesik.mp4"
        ffmpeg_tools.mix_voiceover(self.kisa_video, self.uzun_ses, cikti,
                                   report=rapor)
        self.assertTrue(cikti.exists() and cikti.stat().st_size > 0)
        self.assertTrue(rapor.get("capped"),
                        "anlatim kesildi ama rapor capped demedi: %r" % rapor)

    def test_sigan_anlatim_capped_isaretlenmez(self):
        rapor: dict = {}
        cikti = self.tmp / "tam.mp4"
        ffmpeg_tools.mix_voiceover(self.uzun_video, self.kisa_ses, cikti,
                                   report=rapor)
        self.assertTrue(cikti.exists() and cikti.stat().st_size > 0)
        self.assertFalse(rapor.get("capped"),
                         "anlatim rahat siginca capped isaretlendi: %r" % rapor)

    def test_rapor_verilmezse_davranis_degismez(self):
        """Uc kanal bu fonksiyonu raporsuz cagiriyor; ciktilari ayni kalmali."""
        raporsuz = self.tmp / "raporsuz.mp4"
        raporlu = self.tmp / "raporlu.mp4"
        ffmpeg_tools.mix_voiceover(self.uzun_video, self.kisa_ses, raporsuz)
        ffmpeg_tools.mix_voiceover(self.uzun_video, self.kisa_ses, raporlu,
                                   report={})
        self.assertTrue(raporsuz.exists() and raporsuz.stat().st_size > 0)
        self.assertEqual(
            ffmpeg_tools.get_video_duration(raporsuz),
            ffmpeg_tools.get_video_duration(raporlu),
        )


class NarrationCappedWiringTests(unittest.TestCase):
    """Uretim yolu: kirpma coherence'a ULASMALI.

    Davranis testi ucretli yolu gerektirdigi icin burada kaynak uzerinden
    cakiyoruz; repo bu tekniği alarm nobetcilerinde de kullaniyor.
    """

    @classmethod
    def setUpClass(cls):
        cls.kaynak = (REPO_ROOT / "series" / "produce.py").read_text(encoding="utf-8")
        cls.agac = ast.parse(cls.kaynak)

    def test_produce_mix_voiceover_cagrisina_rapor_gecirir(self):
        cagrilar = [
            node for node in ast.walk(self.agac)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "mix_voiceover"
        ]
        self.assertEqual(len(cagrilar), 1, "mix_voiceover cagri sayisi degisti")
        anahtarlar = {kw.arg for kw in cagrilar[0].keywords}
        self.assertIn("report", anahtarlar,
                      "produce raporu istemiyor; kirpma yine sessiz kalir")

    def test_narration_ok_kirpmayi_hesaba_katar(self):
        self.assertIn(
            'status["narration_ok"] = bool(narration_ok and not narration_capped)',
            self.kaynak,
            "kirpilan anlatim hala 'teslim edildi' sayiliyor",
        )

    def test_kirpma_sessiz_gecmiyor(self):
        self.assertIn("if narration_capped:", self.kaynak)
        self.assertIn("SONU KESILDI", self.kaynak)


if __name__ == "__main__":
    unittest.main()
