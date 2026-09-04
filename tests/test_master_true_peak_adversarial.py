"""ROCK A karsi-test (Visionary). Codex'in kendi paketinin ATLADIGI vakalar.

Uc saldiri ekseni:
  1. Gercek ariza buyuklugu. Uretimdeki ep28 tasmasi 3.1 dB idi
     (limiter -3.0 dBTP, teslim +0.1 dBTP). Codex'in fiksturu yalnizca 0.1 dB
     tasma uretti, yani duzeltmeyi gercek siddette hic sinamadi.
  2. Yakinsama, emniyet payi YOK. Geri cekme tam olarak tasma kadar
     (limiter_db -= overshoot). Sabit tasmali bir codec'te bu SINIRA oturur;
     kayan nokta bir tik yukari kacarsa kapi kapanir.
  3. EN ONEMLISI: master_audio dongusu yalnizca TRUE-PEAK'e bakiyor.
     LUFS'a BAKMIYOR. Limiter cok geri cekilirse teslim sessizlesir,
     master_audio "basarili" doner ama series/produce.py:_verify_audio_master
     ayni dosyayi LUFS yariminda reddeder. O zaman bolum yine olur, ustelik
     bu kez sebebi gorunmez olur.
"""
from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core import ffmpeg_tools  # noqa: E402


def _has_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


class RetryConvergenceTests(unittest.TestCase):
    """Yeniden deneme matematigi, gercek ffmpeg olmadan, kontrollu tasma ile."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="rf_adv_")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.src = pathlib.Path(self.tmp) / "premaster.mp4"
        self.src.write_bytes(b"premaster")
        self.out = pathlib.Path(self.tmp) / "master.mp4"
        self.applied_limits: list[float] = []
        self.input_paths: list[str] = []

    def _fake_run(self, command, **_kwargs):
        """loudnorm olcum gecisi + uygulama gecisini taklit et."""
        text = " ".join(str(c) for c in command)
        if "-f" in command and "null" in command:
            return mock.Mock(returncode=0, stdout="", stderr=(
                '{ "input_i" : "-18.0", "input_tp" : "-2.0", "input_lra" : "7.0",'
                ' "input_thresh" : "-28.0", "target_offset" : "0.0" }'
            ))
        # uygulama gecisi: limiter degerini ve GIRDI dosyasini kaydet
        for token in text.split(","):
            if "alimiter=limit=" in token:
                self.applied_limits.append(
                    float(token.split("alimiter=limit=")[1].split(":")[0])
                )
        idx = command.index("-i")
        self.input_paths.append(str(command[idx + 1]))
        self.out.write_bytes(b"mastered")
        # Gercek loudnorm uygulama gecisi input_* VE output_* alanlarini birlikte
        # basar; _loudnorm_json blogu "input_i" ile ariyor.
        return mock.Mock(returncode=0, stdout="", stderr=(
            '{ "input_i" : "-18.0", "input_tp" : "-2.0", "input_lra" : "7.0",'
            ' "input_thresh" : "-28.0", "output_i" : "-14.0", "output_tp" : "-1.0",'
            ' "output_lra" : "7.0", "output_thresh" : "-24.0",'
            ' "normalization_type" : "linear", "target_offset" : "0.0" }'
        ))

    @staticmethod
    def _db(linear: float) -> float:
        import math
        return 20.0 * math.log10(linear)

    def test_gercek_ep28_siddetinde_tasma_yakinsiyor(self):
        """3.1 dB SABIT codec tasmasi: dongu yakinsamali, fail-closed OLMAMALI."""
        overshoot = 3.1

        def measure(path):
            limit_db = self._db(self.applied_limits[-1])
            return {"integrated_lufs": -14.0,
                    "true_peak_dbtp": round(limit_db + overshoot, 4)}

        with mock.patch.object(ffmpeg_tools.subprocess, "run", side_effect=self._fake_run), \
             mock.patch.object(ffmpeg_tools, "measure_audio_loudness", side_effect=measure):
            ffmpeg_tools.master_audio(self.src, self.out, target_i=-14.0, target_tp=-1.0)

        self.assertLessEqual(len(self.applied_limits), 3,
                             "3 denemeden fazla kosmamali")
        son_tp = self._db(self.applied_limits[-1]) + overshoot
        self.assertLessEqual(round(son_tp, 3), -1.0,
                             f"gercek ep28 siddetinde yakinsamadi: {son_tp:.2f} dBTP")

    def test_her_deneme_DEGISMEMIS_premasterdan_uretiliyor(self):
        """Onceki AAC ciktisi bir sonraki gecise GIRDI olmamali."""
        overshoot = 3.1

        def measure(path):
            limit_db = self._db(self.applied_limits[-1])
            return {"integrated_lufs": -14.0,
                    "true_peak_dbtp": round(limit_db + overshoot, 4)}

        with mock.patch.object(ffmpeg_tools.subprocess, "run", side_effect=self._fake_run), \
             mock.patch.object(ffmpeg_tools, "measure_audio_loudness", side_effect=measure):
            ffmpeg_tools.master_audio(self.src, self.out, target_i=-14.0, target_tp=-1.0)

        self.assertGreater(len(self.input_paths), 1, "en az iki deneme beklenir")
        for p in self.input_paths:
            self.assertEqual(pathlib.Path(p), self.src,
                             "bir deneme premaster yerine ciktidan uretilmis")

    def test_cozulemez_tasma_fail_closed(self):
        """Limiter'dan BAGIMSIZ sabit tepe: 3 denemede tutulamaz, patlamali."""
        def measure(path):
            return {"integrated_lufs": -14.0, "true_peak_dbtp": 0.5}

        with mock.patch.object(ffmpeg_tools.subprocess, "run", side_effect=self._fake_run), \
             mock.patch.object(ffmpeg_tools, "measure_audio_loudness", side_effect=measure):
            with self.assertRaises(RuntimeError):
                ffmpeg_tools.master_audio(self.src, self.out,
                                          target_i=-14.0, target_tp=-1.0)
        self.assertEqual(len(self.applied_limits), 3, "tam 3 deneme olmali")

    def test_LUFS_bantta_kalinca_dongu_YINE_yakinsiyor(self):
        """Mutlu yol: iki yarim da saglanabiliyorsa LUFS kontrolu ENGEL OLMAMALI.

        Limiter geri cekilirken entegre seviye ancak cok az duser (gercekci:
        loudnorm linear modda hedefi zaten tutturur, limiter sadece tepe trasar).
        Burada hem TP hem LUFS saglanabilir; dongu basariyla donmelidir.
        """
        def measure(path):
            limit_db = self._db(self.applied_limits[-1])
            return {"integrated_lufs": -14.0 + (limit_db + 1.0) * 0.15,
                    "true_peak_dbtp": round(limit_db + 3.1, 4)}

        with mock.patch.object(ffmpeg_tools.subprocess, "run", side_effect=self._fake_run),              mock.patch.object(ffmpeg_tools, "measure_audio_loudness", side_effect=measure):
            ffmpeg_tools.master_audio(self.src, self.out, target_i=-14.0, target_tp=-1.0)

        son_limit_db = self._db(self.applied_limits[-1])
        self.assertLessEqual(round(son_limit_db + 3.1, 3), -1.0)
        son_lufs = -14.0 + (son_limit_db + 1.0) * 0.15
        self.assertLessEqual(abs(son_lufs + 14.0), 1.0)

    def test_LUFS_bantta_DEGILSE_fail_closed_ve_sebep_LUFS_demeli(self):
        """KRITIK: dongu sozlesmenin YALNIZ yarisina bakiyor.

        Limiter buyuk tasmayi telafi etmek icin cok geri cekilince yogun
        malzemede entegre seviye de duser. Bu senaryoda TP saglanabilir ama
        LUFS saglanamaz; iki yarim AYNI ANDA tutmaz.

        Dogru davranis: master_audio "basarili" DONMEMELI. Aksi halde
        series/produce.py:_verify_audio_master ayni dosyayi LUFS yariminda
        reddeder, bolum yine oOlur, ustelik log "master hazir" dedigi icin
        teshis oncekinden daha zor olur.

        Bu yuzden: RuntimeError beklenir VE mesaj hangi yarimin tutmadigini,
        yani LUFS'u, acikca soylemelidir.
        """
        def measure(path):
            limit_db = self._db(self.applied_limits[-1])
            # 1 dB limiter geri cekilmesi = 1 dB entegre seviye dususu.
            # TP icin limiter <= -4.1, LUFS icin limiter >= -2.0 gerekir:
            # kesisim BOS, yani cozum yok.
            return {"integrated_lufs": -14.0 + (limit_db + 1.0) * 1.0,
                    "true_peak_dbtp": round(limit_db + 3.1, 4)}

        with mock.patch.object(ffmpeg_tools.subprocess, "run", side_effect=self._fake_run),              mock.patch.object(ffmpeg_tools, "measure_audio_loudness", side_effect=measure):
            with self.assertRaises(RuntimeError) as ctx:
                ffmpeg_tools.master_audio(self.src, self.out,
                                          target_i=-14.0, target_tp=-1.0)

        mesaj = str(ctx.exception).lower()
        self.assertTrue(
            "lufs" in mesaj,
            f"fail-closed oldu ama sebep LUFS demiyor, teshis edilemez: {ctx.exception!r}"
        )


@unittest.skipUnless(_has_ffmpeg(), "ffmpeg yok")
class HarsherRealMaterialTests(unittest.TestCase):
    """Codex'in fiksturunden DAHA sert gercek malzeme."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="rf_adv_real_")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def _p(self, name: str) -> pathlib.Path:
        return pathlib.Path(self.tmp) / name

    def _ffmpeg(self, *args):
        subprocess.run(["ffmpeg", "-y", "-hide_banner", "-nostats", *[str(a) for a in args]],
                       capture_output=True, check=True, timeout=300)

    def test_asiri_sert_uc_katman_sozlesmeyi_saglar(self):
        """Nyquist'e daha yakin, daha yuksek genlikli, kirpik uc katman."""
        native, voice, music = self._p("n.mp4"), self._p("v.wav"), self._p("m.wav")
        narrated, premaster = self._p("nar.mp4"), self._p("pre.mp4")
        mastered = self._p("out.mp4")

        # Codex'in fiksturunden daha sert: genlikler 1.0'a dayali, faz kaymali
        # kare dalgalar, uc bilesen. AAC decode'da ornekler-arasi tepe maksimum.
        n_sig = ("aevalsrc=0.98*sgn(sin(2*PI*18700*t))+"
                 "0.42*sgn(sin(2*PI*21100*t+0.3)):d=6:s=48000")
        v_sig = ("aevalsrc=0.96*sgn(sin(2*PI*19900*t+0.9))+"
                 "0.38*sgn(sin(2*PI*17300*t+2.1)):d=6:s=48000")
        m_sig = ("aevalsrc=0.94*sgn(sin(2*PI*20500*t+1.7))+"
                 "0.40*sgn(sin(2*PI*16100*t+0.5)):d=6:s=48000")

        self._ffmpeg("-f", "lavfi", "-i", "color=c=black:s=160x90:d=6:r=30",
                     "-f", "lavfi", "-i", n_sig, "-shortest",
                     "-c:v", "mpeg4", "-c:a", "aac", "-b:a", "192k", native)
        self._ffmpeg("-f", "lavfi", "-i", v_sig, "-c:a", "pcm_f32le", voice)
        self._ffmpeg("-f", "lavfi", "-i", m_sig, "-c:a", "pcm_f32le", music)

        ffmpeg_tools.mix_voiceover(native, voice, narrated, voice_volume=1.0,
                                   bg_duck=0.5, amix_normalize=False)
        ffmpeg_tools.mix_background_music(narrated, music, premaster,
                                          music_volume=0.5, limit_mix_peak=True)
        ffmpeg_tools.master_audio(premaster, mastered)

        measured = ffmpeg_tools.measure_audio_loudness(mastered)
        self.assertIsNotNone(measured)
        # produce.py:_verify_audio_master ile BIREBIR ayni kapi
        self.assertLessEqual(measured["true_peak_dbtp"], -1.0,
                             f"true-peak sozlesmesi tutmadi: {measured}")
        self.assertLessEqual(abs(measured["integrated_lufs"] + 14.0), 1.0,
                             f"LUFS sozlesmesi tutmadi: {measured}")


if __name__ == "__main__":
    unittest.main()
