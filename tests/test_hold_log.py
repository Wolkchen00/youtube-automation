"""Tutulma defteri: yayina giremeyen bolum OLAY ANINDA iz birakir.

series.json yalnizca ANLIK durumu tutar. Bir bolum takilip sonraki kosuda kendini
toparlarsa geriye bakan hicbir arac o hatayi goremez; olculdu: unnatural-lab
part 33 AUDIO_MASTER ile takildi, yeniden denemede yayinlandi ve series.json'da
hicbir iz kalmadi. Gunluk beyin "dun su kadar bolum tutuldu" diyebilsin diye
motor artik olay aninda hold_log.jsonl'a yaziyor.

Bu defter uretimi ASLA durdurmamali: yazilamazsa kosu devam eder.
"""
from __future__ import annotations

import ast
import json
import pathlib
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from series import series_runner  # noqa: E402
from series.produce import ProduceResult  # noqa: E402
from series.series_meta import SeriesMeta  # noqa: E402

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]


def _meta(slug="hold-log-test"):
    return SeriesMeta({
        "slug": slug, "base_title": slug, "total_parts": 3, "next_part": 1,
        "status": "active", "publish_mode": "auto", "upload_profile": "p",
        "platforms": ["youtube"], "parts": {},
    })


class HoldLogWriteTests(unittest.TestCase):
    def test_tutulma_olay_aninda_yazilir(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            hedef = pathlib.Path(tmp)
            with mock.patch("series.bible.data_dir", return_value=hedef):
                series_runner._append_hold_log(
                    _meta(), 33, "qc_retry",
                    ProduceResult("qc_hold", reason="mastering basarisiz",
                                  reason_code="AUDIO_MASTER",
                                  coherence={"degraded": True}),
                )
            path = hedef / "hold_log.jsonl"
            self.assertTrue(path.exists(), "hold_log yazilmadi")
            satir = json.loads(path.read_text(encoding="utf-8").strip())
            self.assertEqual(satir["part"], 33)
            self.assertEqual(satir["durum"], "qc_retry")
            self.assertEqual(satir["kod"], "AUDIO_MASTER")
            self.assertIn("mastering", satir["neden"])
            self.assertEqual(satir["coherence"], {"degraded": True})
            self.assertIn("ts", satir)

    def test_ayni_bolum_her_olayda_yeni_satir_ekler(self):
        """Toparlanan hata da iz birakmali: defter append-only."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            hedef = pathlib.Path(tmp)
            with mock.patch("series.bible.data_dir", return_value=hedef):
                for kod in ("AUDIO_MASTER", "EPISODE_DEGRADED"):
                    series_runner._append_hold_log(
                        _meta(), 7, "qc_retry",
                        ProduceResult("qc_hold", reason="x", reason_code=kod))
            satirlar = (hedef / "hold_log.jsonl").read_text(
                encoding="utf-8").strip().splitlines()
            self.assertEqual(len(satirlar), 2,
                             "defter uzerine yazdi, eklemedi: %r" % satirlar)
            self.assertEqual([json.loads(s)["kod"] for s in satirlar],
                             ["AUDIO_MASTER", "EPISODE_DEGRADED"])

    def test_defter_yazilamazsa_uretim_durmaz(self):
        """En onemli sozlesme: gunluk kayit tutmak yayini ASLA olduremez."""
        with mock.patch("series.bible.data_dir",
                        side_effect=OSError("disk dolu")):
            series_runner._append_hold_log(
                _meta(), 1, "needs_human",
                ProduceResult("generation_fail", reason_code="UNKNOWN"))
        # istisna sizmadiysa test gecer


class HoldLogWiringTests(unittest.TestCase):
    """Defter, bolumun tutuldugu HER yoldan cagrilmali."""

    @classmethod
    def setUpClass(cls):
        cls.kaynak = (REPO_ROOT / "series" / "series_runner.py").read_text(
            encoding="utf-8")
        cls.agac = ast.parse(cls.kaynak)

    def _cagri_sayisi(self):
        return len([
            node for node in ast.walk(self.agac)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "_append_hold_log"
        ])

    def test_uc_tutulma_yolunun_hepsi_deftere_yazar(self):
        """terminal (needs_human/budget_exhausted), altyapi retry, icerik retry."""
        self.assertEqual(self._cagri_sayisi(), 3,
                         "tutulma yollarindan biri deftere yazmiyor")

    def test_defter_yazimi_kendi_hatasini_yutar(self):
        govde = self.kaynak.split("def _append_hold_log")[1].split("\ndef ")[0]
        self.assertIn("except Exception", govde,
                      "defter yazimi uretimi durdurabilir")


if __name__ == "__main__":
    unittest.main()
