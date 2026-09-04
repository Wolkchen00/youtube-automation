"""last_run.json artik GERCEK yayin kanitindan turetiliyor (ROCK E4).

Onceki hali `steps.produce.outcome`'a bakiyordu ve 2026-09-03T19:26'da
event-horizon icin sifir video uretilen kosuya `{"outcome":"success"}` yazdi.
Panoyu ve nobetciyi besleyen dosya buydu; Galactic'in dort gunluk sessizligi
bu yuzden hicbir yerde gorunmedi.
"""
from __future__ import annotations

import importlib.util
import io
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location(
    "kosu_sonucu_yaz", ROOT / "scripts" / "kosu_sonucu_yaz.py"
)
kosu_sonucu = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kosu_sonucu)

SINCE = "2026-09-04T20:00:00Z"
ONCE = "2026-09-03T22:54:07.354811+00:00"   # bayat kanit
SONRA = "2026-09-04T20:31:00.000000+00:00"  # bu kosunun kaniti


class SeriHattiTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="rf_e4_"))
        self.addCleanup(__import__("shutil").rmtree, self.tmp, ignore_errors=True)
        self.out = self.tmp / "last_run.json"
        self.pub = self.tmp / "published.json"

    def _yaz(self, kayitlar):
        self.pub.write_text(json.dumps(kayitlar, ensure_ascii=False), encoding="utf-8")

    def _kos(self, raw="success"):
        kosu_sonucu.main([
            "--out", str(self.out), "--run-id", "999",
            "--raw-outcome", raw, "--since", SINCE,
            "--published-json", str(self.pub),
        ])
        return json.loads(self.out.read_text(encoding="utf-8"))

    def test_bu_kosuda_youtube_yayini_varsa_success(self):
        self._yaz([{"part": 25, "ts": SONRA, "results": {"youtube": "abc123"}}])
        d = self._kos()
        self.assertEqual(d["outcome"], "success")
        self.assertEqual(d["published_part"], 25)
        self.assertEqual(d["youtube_id"], "abc123")

    def test_BAYAT_kanit_success_SAYILMAZ(self):
        """Galactic tuzagi: dunku video bugunku sessizligi ortmemeli."""
        self._yaz([{"part": 24, "ts": ONCE, "results": {"youtube": "eski"}}])
        d = self._kos()
        self.assertEqual(d["outcome"], "no_video")
        self.assertIsNone(d["youtube_id"])

    def test_hic_yayin_yoksa_no_video(self):
        self._yaz([])
        self.assertEqual(self._kos()["outcome"], "no_video")

    def test_published_json_hic_yoksa_no_video(self):
        self.assertEqual(self._kos()["outcome"], "no_video")

    def test_adim_patladiysa_failure(self):
        self._yaz([{"part": 25, "ts": SONRA, "results": {"youtube": "abc"}}])
        self.assertEqual(self._kos(raw="failure")["outcome"], "failure")

    def test_YALNIZ_instagram_tiktok_success_SAYILMAZ(self):
        """Dort kanal da YouTube kanali; olculen sey YouTube yayinidir."""
        self._yaz([{"part": 25, "ts": SONRA,
                    "results": {"instagram": "111", "tiktok": "222"}}])
        self.assertEqual(self._kos()["outcome"], "no_video")


class FearSlideHattiTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="rf_e4b_"))
        self.addCleanup(__import__("shutil").rmtree, self.tmp, ignore_errors=True)
        self.out = self.tmp / "last_run.json"
        self.jsonl = self.tmp / "yayin.jsonl"

    def _yaz(self, kayitlar):
        with io.open(self.jsonl, "w", encoding="utf-8") as fh:
            for k in kayitlar:
                fh.write(json.dumps(k, ensure_ascii=False) + "\n")

    def _kos(self, raw="success"):
        kosu_sonucu.main([
            "--out", str(self.out), "--run-id", "888",
            "--raw-outcome", raw, "--since", SINCE,
            "--yayin-jsonl", str(self.jsonl),
        ])
        return json.loads(self.out.read_text(encoding="utf-8"))

    def test_ic_ice_youtube_yapisi_okunuyor(self):
        """yayinla.py results.youtube.results.youtube.post_id seklinde yaziyor."""
        self._yaz([{"ts_utc": SONRA, "results": {"youtube": {
            "success": True,
            "results": {"youtube": {"success": True, "post_id": "H-2ZqZcrle8"}}}}}])
        d = self._kos()
        self.assertEqual(d["outcome"], "success")
        self.assertEqual(d["youtube_id"], "H-2ZqZcrle8")

    def test_youtube_basarisizsa_no_video(self):
        """yayinla.py tek platform basarili olunca 0 donuyor; bu YETMEZ."""
        self._yaz([{"ts_utc": SONRA, "results": {
            "youtube": {"success": False},
            "instagram": {"success": True, "post_id": "ig1"}}}])
        self.assertEqual(self._kos()["outcome"], "no_video")

    def test_bayat_satir_success_sayilmaz(self):
        self._yaz([{"ts_utc": ONCE, "results": {"youtube": {
            "success": True,
            "results": {"youtube": {"post_id": "eski"}}}}}])
        self.assertEqual(self._kos()["outcome"], "no_video")


class WorkflowBaglantiTests(unittest.TestCase):
    """Betik yazilmis ama workflow onu CAGIRMIYORSA hicbir sey degismez."""

    HATLAR = {
        "event-horizon.yml", "flashpoints.yml", "unnatural-lab.yml",
        "from-scratch.yml", "next-stop.yml", "fear-slide.yml",
    }

    def test_alti_hat_da_sonuc_betigini_cagiriyor(self):
        wf = ROOT / ".github" / "workflows"
        eksik = []
        for ad in sorted(self.HATLAR):
            metin = (wf / ad).read_text(encoding="utf-8")
            if "kosu_sonucu_yaz.py" not in metin:
                eksik.append(ad)
        self.assertFalse(
            eksik,
            "su hatlar last_run.json'i hala kendi shell'inde yaziyor, yani "
            f"yayin kaniti gozetilmiyor: {eksik}",
        )

    def test_kosu_baslangici_damgalaniyor(self):
        """--since damgasi olmadan BAYAT kanit success sayilir."""
        wf = ROOT / ".github" / "workflows"
        eksik = [ad for ad in sorted(self.HATLAR)
                 if "KOSU_BASLANGIC" not in (wf / ad).read_text(encoding="utf-8")]
        self.assertFalse(eksik, f"kosu baslangic damgasi yok: {eksik}")


if __name__ == "__main__":
    unittest.main()
