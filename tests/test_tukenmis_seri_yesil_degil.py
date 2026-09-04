"""Hicbir sey yayinlamayan kosu YESIL donmemeli (ROCK E1 + E2).

2026-09-01..04: Galactic Experiment dort gun sessiz kaldi ve Event Horizon Daily
her gun `success` raporladi. Zincir suydu: event-horizon kuyrugu tukendi,
`run_next` erken donuste `return True` verdi, `main()` exit 0 dondu, workflow
yesil oldu, nobetci sagliklı sandi. Ariza ancak YouTube RSS okunarak gorulebildi.

Bu dosya iki kusuru birden capalar:
  E1 , `--series` ayristiricisi: eksik/bozuk deger `run_all()` yoluna dusuyordu
       ve PARASI ODENMIS, istenmeyen bir bolum uretebiliyordu.
  E2 , tukenmis ama kendini besleyen seri, ACIKCA istendiginde BASARISIZ olmali;
       bilerek duraklatilmis seri ise kirmizi YANMAMALI (alarm gurultusu).
"""
from __future__ import annotations

import pathlib
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from series import series_runner  # noqa: E402


class SahteMeta:
    def __init__(self, *, status, next_part, total_parts, replenish_enabled,
                 base_title="Test Serisi"):
        self.status = status
        self.next_part = next_part
        self.total_parts = total_parts
        self.auto_replenish = {"enabled": replenish_enabled}
        self.base_title = base_title
        self.data = {}


class ArgparseTests(unittest.TestCase):
    """E1 , bozuk cagri PARA yakmadan reddedilmeli."""

    def test_degeri_olmayan_series_reddedilir(self):
        with self.assertRaises(SystemExit):
            series_runner._parse_args(["--series"])

    def test_bayrak_deger_gibi_yutulmaz(self):
        """`--series --dry-run` eskiden slug='--dry-run' yapiyordu."""
        with self.assertRaises(SystemExit):
            series_runner._parse_args(["--series", "--dry-run"])

    def test_bos_series_reddedilir(self):
        with self.assertRaises(SystemExit):
            series_runner._parse_args(["--series", "   "])

    def test_gecerli_cagrilar_calisir(self):
        a = series_runner._parse_args(["--series", "flashpoints"])
        self.assertEqual(a.slug, "flashpoints")
        self.assertFalse(a.dry_run)
        b = series_runner._parse_args([])
        self.assertIsNone(b.slug)
        c = series_runner._parse_args(["--series", "next-stop", "--force"])
        self.assertEqual((c.slug, c.force), ("next-stop", True))
        d = series_runner._parse_args(
            ["--series", "unnatural-lab", "--drain-alerts-only"])
        self.assertTrue(d.drain_alerts_only)


class TukenmisSeriTests(unittest.TestCase):
    """E2 , 'uretilecek bolum yok' her zaman basari degildir."""

    def _kos(self, meta, *, strict_empty, dry_run=False):
        with mock.patch.object(series_runner.SeriesMeta, "load", return_value=meta), \
             mock.patch.object(series_runner, "_series_alert") as alarm:
            sonuc = series_runner.run_next(
                "test-seri", dry_run=dry_run, publish=False,
                strict_empty=strict_empty,
            )
        return sonuc, alarm

    def test_tukenmis_ikmalli_seri_ACIKCA_istendiginde_BASARISIZ(self):
        """Galactic'in birebir durumu: completed, 26/25, auto_replenish acik."""
        meta = SahteMeta(status="completed", next_part=26, total_parts=25,
                         replenish_enabled=True)
        sonuc, alarm = self._kos(meta, strict_empty=True)
        self.assertFalse(sonuc, "kuyruk bos ve ikmal yazamadi ,  YESIL donmemeli")
        alarm.assert_called_once()
        self.assertIn("video", alarm.call_args[0][1].lower())

    def test_bilerek_duraklatilmis_seri_KIRMIZI_YANMAZ(self):
        """from-scratch / next-stop gibi 10+ pasif seri alarm gurultusu yapmamali."""
        for durum in ("paused", "draft"):
            with self.subTest(durum=durum):
                meta = SahteMeta(status=durum, next_part=11, total_parts=15,
                                 replenish_enabled=True)
                sonuc, alarm = self._kos(meta, strict_empty=True)
                self.assertTrue(sonuc, f"{durum} bir ariza degil")
                alarm.assert_not_called()

    def test_sonlu_seri_dogal_bitisi_BASARIDIR(self):
        """auto_replenish KAPALI, sonlu seri: bitmesi tasarimin kendisi."""
        meta = SahteMeta(status="completed", next_part=11, total_parts=10,
                         replenish_enabled=False)
        sonuc, alarm = self._kos(meta, strict_empty=True)
        self.assertTrue(sonuc)
        alarm.assert_not_called()

    def test_ana_kuyruk_yolu_ETKILENMEZ(self):
        """strict_empty=False (run_all yolu) eski davranisi korur."""
        meta = SahteMeta(status="completed", next_part=26, total_parts=25,
                         replenish_enabled=True)
        sonuc, alarm = self._kos(meta, strict_empty=False)
        self.assertTrue(sonuc, "run_all yolunun sozlesmesi degismemeli")
        alarm.assert_not_called()

    def test_kuru_kosu_DIS_ALARM_GONDERMEZ(self):
        meta = SahteMeta(status="completed", next_part=26, total_parts=25,
                         replenish_enabled=True)
        sonuc, alarm = self._kos(meta, strict_empty=True, dry_run=True)
        self.assertFalse(sonuc, "kuru kosuda da sonuc basarisiz olmali")
        alarm.assert_not_called()


class MainCikisKoduTests(unittest.TestCase):
    """CLI gercekten exit 1 veriyor mu."""

    def test_tukenmis_seri_exit_1(self):
        meta = SahteMeta(status="completed", next_part=26, total_parts=25,
                         replenish_enabled=True)
        with mock.patch.object(series_runner.SeriesMeta, "load", return_value=meta), \
             mock.patch.object(series_runner, "_series_alert"), \
             mock.patch.object(series_runner, "_drain_outboxes", return_value=True), \
             mock.patch.object(series_runner, "_outboxes_empty", return_value=True):
            with self.assertRaises(SystemExit) as ctx:
                series_runner.main(["--series", "event-horizon"])
        self.assertEqual(ctx.exception.code, 1)

    def test_duraklatilmis_seri_exit_0(self):
        meta = SahteMeta(status="paused", next_part=7, total_parts=9,
                         replenish_enabled=False)
        with mock.patch.object(series_runner.SeriesMeta, "load", return_value=meta), \
             mock.patch.object(series_runner, "_series_alert"), \
             mock.patch.object(series_runner, "_drain_outboxes", return_value=True), \
             mock.patch.object(series_runner, "_outboxes_empty", return_value=True):
            series_runner.main(["--series", "next-stop"])  # SystemExit YOK


if __name__ == "__main__":
    unittest.main()
