"""Taban kabulu iki kapida da ayni anlama gelmeli.

20 Eylul 2026, wild-encounter ep12: core.master_policy "Delivered QUIET:
LUFS=-15.50 ... at or above the -18.00 LUFS floor ... This material does not
reach the target at any gain." deyip teslimi KABUL etti. Bir satir sonra
produce._verify_audio_master ayni dosyayi olctu, tabandan haberi olmadigi icin
[-15, -13] penceresine vurdu ve bolumu QC hold'a dusurdu. Klip hazirdi, ses
yayinlanabilirdi, kanal yine karanlik kalacakti.

Bu dosya iki kapinin ayni sozlesmeyi konustugunu kanitlar.
"""

import pathlib
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core import master_policy
from series import produce

TARGET = -14.0
FLOOR = -18.0


def verify(lufs, *, floor=None, true_peak=-1.5):
    measurement = {"integrated_lufs": lufs, "true_peak_dbtp": true_peak}
    with mock.patch.object(produce.ffmpeg_tools, "measure_audio_loudness",
                           return_value=measurement):
        return produce._verify_audio_master(
            pathlib.Path("ep.mp4"), TARGET, floor
        )


class TabanKabulu(unittest.TestCase):
    def test_arizanin_birebir_sayisi_kabul_edilir(self):
        """ep12'nin olculen degeri: -15,5 LUFS, taban -18."""
        self.assertTrue(verify(-15.5, floor=FLOOR))

    def test_taban_yokken_eski_kati_sozlesme_korunur(self):
        """Taban tanimlamayan seriler icin davranis DEGISMEZ."""
        self.assertFalse(verify(-15.5))
        self.assertTrue(verify(-14.4))

    def test_tabanin_altina_dusen_teslim_reddedilir(self):
        self.assertFalse(verify(-18.5, floor=FLOOR))

    def test_taban_sinirindaki_teslim_kabul_edilir(self):
        self.assertTrue(verify(FLOOR, floor=FLOOR))

    def test_hedefin_USTU_taban_varken_bile_affedilmez(self):
        """Taban yalniz SESSIZ teslimi mazur gorur, gurultulu olani asla."""
        self.assertFalse(verify(-12.5, floor=FLOOR))

    def test_true_peak_kapisi_taban_tarafindan_delinmez(self):
        self.assertFalse(verify(-15.5, floor=FLOOR, true_peak=-0.5))
        self.assertFalse(verify(-14.0, floor=FLOOR, true_peak=-0.5))

    def test_olculemeyen_master_reddedilir(self):
        with mock.patch.object(produce.ffmpeg_tools, "measure_audio_loudness",
                               return_value=None):
            self.assertFalse(
                produce._verify_audio_master(pathlib.Path("ep.mp4"), TARGET, FLOOR)
            )


class IkiKapiAyniSozlesme(unittest.TestCase):
    """master_policy KABUL ederse dogrulayici da KABUL etmeli."""

    def _policy_accepts(self, lufs):
        decision = master_policy.next_master_step(
            attempt=3, max_attempts=3, limiter_db=-2.5,
            target_tp=-1.0, target_i=TARGET,
            measured_tp=-1.5, measured_lufs=lufs,
            max_total_reduction=6.0, margin=0.2,
            gain_db=2.0, max_total_gain=2.0, lufs_floor=FLOOR,
        )
        return decision.action == "accept"

    def test_politika_kabul_ettigi_her_degeri_dogrulayici_da_gecirir(self):
        checked = 0
        for tenth in range(-200, -119):
            lufs = tenth / 10.0
            if not self._policy_accepts(lufs):
                continue
            checked += 1
            self.assertTrue(
                verify(lufs, floor=FLOOR),
                f"politika {lufs} LUFS'u kabul etti, dogrulayici reddetti",
            )
        self.assertGreater(checked, 0, "politika hicbir degeri kabul etmedi")


if __name__ == "__main__":
    unittest.main()
