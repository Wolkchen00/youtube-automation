# -*- coding: utf-8 -*-
"""Kunye kapisi + sabit muzik sozlesmesi (still-home v2.0, 15 Eylul 2026).

Iki GERCEK ariza bu dosyada kilitleniyor:

1. Kunye kapisi TERS calisiyordu. `_validate_batch` icinde iki ayri dal vardi ve
   `year_required: true` olan dal alt yaziyi KOSULSUZ zorunlu tutup
   `subtitle_required: false` alanini hic okumuyordu. Sonuc: still-home'un
   DOGRU kunyesi ("ISTANBUL 2512" / "") reddediliyor, YANLISI
   ("Eiffel Tower: Energy Spine" / "Paris, France 2512") kabul ediliyordu ,
   cunku yil kontrolu alt yazidan geciyordu. Kurulusta bes plan ELLE yazildigi
   icin hata ilk otomatik ikmale kadar gorulmedi.

2. Muzik prompt'u doktrinden kaciyordu. Doktrin tek, sabit, vurussuz, melodisiz
   derin drone istiyor ama ikmalin yazdigi bes planin besinde de piyano, yayli
   ve kreskendo belirdi. Yayinlanmis iki bolumun metni ise harfi harfine
   ayniydi, yani alan zaten DEGISKEN DEGILDI.

Ikisi de paylasilan kodda: butun seritler ayni fonksiyonlari kullaniyor, bu
yuzden testler eski davranisin korundugunu da dogruluyor.
"""

import copy
import json
import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from series.bible import Bible                                  # noqa: E402
from series.replenish import validate_title_card, _validate_batch  # noqa: E402


def _bible(**series_extra) -> Bible:
    data = {
        "series": {
            "slug": "t",
            "title_card": {"enabled": True, "year_required": True},
            **series_extra,
        },
        "art_style": "x",
        "characters": [], "environments": [], "props": [],
    }
    b = Bible.__new__(Bible)
    b.data = data
    return b


def _card(title, subtitle=""):
    return {"title_card": {"title": title, "subtitle": subtitle}}


class TekSatirlikKunyeTests(unittest.TestCase):
    """subtitle_required: false + year_required: true birlikte calismali."""

    def test_bos_alt_yazi_kabul_edilir(self):
        b = _bible(title_card={"enabled": True, "year_required": True,
                               "subtitle_required": False})
        self.assertEqual(validate_title_card(b, _card("ISTANBUL 2512"), required=True), [])

    def test_iki_satirli_kunye_de_hala_kabul(self):
        """Gerileme korumasi: subtitle_required varsayilani True olan seritler."""
        b = _bible()
        self.assertEqual(
            validate_title_card(b, _card("Zanzibar, 1896", "The Shortest War"), required=True),
            [])

    def test_alt_yazi_zorunluyken_bos_alt_yazi_reddedilir(self):
        b = _bible()
        self.assertTrue(validate_title_card(b, _card("Zanzibar, 1896"), required=True))

    def test_yil_hala_zorunlu(self):
        b = _bible(title_card={"enabled": True, "year_required": True,
                               "subtitle_required": False})
        errors = validate_title_card(b, _card("ISTANBUL"), required=True)
        self.assertTrue(any("4-haneli" in e for e in errors), errors)


class KunyeBicimKapisiTests(unittest.TestCase):
    """title_pattern / subtitle_pattern , opt-in kalip zorlamasi."""

    PATTERN = r"[A-Z][A-Z0-9' .-]{1,28} 2512"

    def _b(self):
        return _bible(title_card={
            "enabled": True, "year_required": True, "subtitle_required": False,
            "title_pattern": self.PATTERN, "subtitle_pattern": "",
        })

    def test_kanonik_kunye_gecer(self):
        for title in ("ISTANBUL 2512", "NEW YORK 2512", "MACHU PICCHU 2512"):
            with self.subTest(title=title):
                self.assertEqual(validate_title_card(self._b(), _card(title), required=True), [])

    def test_modelin_uydurdugu_kunye_reddedilir(self):
        errors = validate_title_card(
            self._b(),
            _card("Eiffel Tower: Energy Spine", "Paris, France 2512"),
            required=True)
        self.assertTrue(any("kalibina uymuyor" in e for e in errors), errors)

    def test_kucuk_harf_ve_yanlis_yil_reddedilir(self):
        for title in ("Paris 2512", "PARIS 2500", "PARIS"):
            with self.subTest(title=title):
                self.assertTrue(validate_title_card(self._b(), _card(title), required=True))

    def test_dolu_alt_yazi_bos_kalibi_bozar(self):
        errors = validate_title_card(self._b(), _card("PARIS 2512", "France"), required=True)
        self.assertTrue(any("subtitle" in e for e in errors), errors)

    def test_kalip_yoksa_davranis_eskisiyle_ayni(self):
        """Alan yazilmamis seritlerde hicbir sey degismez."""
        self.assertEqual(
            validate_title_card(_bible(), _card("Zanzibar, 1896", "The Shortest War"),
                                required=True),
            [])

    def test_bozuk_duzenli_ifade_fail_closed(self):
        b = _bible(title_card={"enabled": True, "year_required": True,
                               "subtitle_required": False, "title_pattern": "[unclosed"})
        errors = validate_title_card(b, _card("PARIS 2512"), required=True)
        self.assertTrue(any("gecersiz duzenli ifade" in e for e in errors), errors)


class SabitMuzikTests(unittest.TestCase):
    """bible.series.music_fixed , degismeyen alani modele yazdirma."""

    CANON = ("A single sustained sub-bass drone at one steady level for the whole duration, "
             "built from deep low-frequency air and distant structural resonance. It holds the "
             "same volume from the first second to the last, stays free of percussion, rhythm, "
             "melody, vocals and high frequencies, and ends mid-tone so the loop is seamless.")

    def test_alan_yoksa_None(self):
        self.assertIsNone(_bible().music_fixed)

    def test_bos_string_None_sayilir(self):
        self.assertIsNone(_bible(music_fixed="   ").music_fixed)

    def test_dolu_alan_kirpilarak_doner(self):
        self.assertEqual(_bible(music_fixed=f"  {self.CANON}  ").music_fixed, self.CANON)

    def test_canli_seri_kanonik_metni_tasiyor(self):
        b = Bible.load("still-home")
        self.assertEqual(b.music_fixed, self.CANON)


class CanliSeriSozlesmesiTests(unittest.TestCase):
    """still-home v2.0 sozlesmesi , Ihsan direktifi 15 Eylul 2026."""

    def setUp(self):
        root = REPO_ROOT / "shadowedhistory" / "still-home"
        self.bible = json.loads((root / "bible.json").read_text(encoding="utf-8"))["series"]
        self.meta = json.loads((root / "series.json").read_text(encoding="utf-8"))
        self.plans_dir = root / "plans"

    def test_dort_cekim_uc_gecis(self):
        self.assertEqual(self.meta["auto_replenish"]["shots"], 4)
        self.assertEqual(str(self.meta["auto_replenish"]["shot_seconds"]), "4")
        self.assertEqual(len(self.meta["auto_replenish"]["shot_plan"]), 4)

    def test_micro_trim_10_saniye_verir(self):
        """4 x 4 sn ham, iki uctan 0,75 -> 4 x 2,5 = 10,0 sn."""
        trim = self.bible["micro_trim"]
        kesilmis = 4.0 - 2 * trim
        self.assertAlmostEqual(kesilmis, 2.5)
        # trim_head_tail kalan < 2,0 ise kirpmayi REDDEDER
        self.assertGreaterEqual(kesilmis, 2.0, "micro_trim 4 sn'lik klipte en fazla 1,0 olabilir")
        low, high = self.bible["duration_band"]
        self.assertLessEqual(low, 4 * kesilmis, "duration_band 10,0 sn'yi kapsamali")
        self.assertGreaterEqual(high, 4 * kesilmis)

    def test_kunye_cekim_1_icine_sigar(self):
        self.assertLessEqual(self.bible["title_card"]["duration"], 4.0 - 2 * self.bible["micro_trim"],
                             "kunye ilk kesmeden sonra ekranda kalamaz")

    def test_regen_adil_payi_cekim_basina_iki(self):
        qc = self.bible["qc"]
        fair_share = qc["max_regens_per_episode"] // self.meta["auto_replenish"]["shots"]
        self.assertEqual(fair_share, 2)

    def test_konu_havuzu_teknoloji_aileleri(self):
        ar = self.meta["auto_replenish"]
        felaket = {"su yukseldi", "cole donustu", "ortu altinda", "asagi indi",
                   "yukari buyudu", "yesile donustu"}
        self.assertFalse(felaket & set(ar["families"]),
                         "v1.0'in felaket aileleri havuzda kalamaz")
        self.assertEqual(len(ar["topic_pool"]), 36)
        aileler = [t["family"] for t in ar["topic_pool"]]
        self.assertTrue(all(a in ar["families"] for a in aileler))
        ardisik = [i for i in range(len(aileler) - 1) if aileler[i] == aileler[i + 1]]
        self.assertEqual(ardisik, [], "ardisik iki bolum ayni aileden olamaz")

    def test_yayinlanmis_sehirlerin_id_leri_korundu(self):
        """seed_id eslesmesi bozulsa Istanbul ve New York havuza geri donerdi."""
        pool = {t["id"]: t["topic"] for t in self.meta["auto_replenish"]["topic_pool"]}
        self.assertTrue(pool[1].startswith("Istanbul"))
        self.assertTrue(pool[2].startswith("New York"))

    def test_kuyruktaki_planlar_sozlesmeye_uyuyor(self):
        plans = sorted(self.plans_dir.glob("part0[3-9].json"))
        self.assertTrue(plans, "kuyruk bos")
        for path in plans:
            plan = json.loads(path.read_text(encoding="utf-8"))
            with self.subTest(plan=path.name):
                self.assertEqual(len(plan["shots"]), 4)
                self.assertEqual({s["duration"] for s in plan["shots"]}, {"4"})
                self.assertEqual(plan["title_card"]["subtitle"], "")
                self.assertRegex(plan["title_card"]["title"], r"^[A-Z][A-Z0-9' .-]{1,28} 2512$")
                self.assertEqual(plan["music"], SabitMuzikTests.CANON)


class IkmalUctanUcaTests(unittest.TestCase):
    """_validate_batch still-home'un gercek yapilandirmasiyla dogru karar veriyor mu."""

    def setUp(self):
        root = REPO_ROOT / "shadowedhistory" / "still-home"
        self.bible = Bible.load("still-home")
        self.cfg = json.loads((root / "series.json").read_text(encoding="utf-8"))["auto_replenish"]
        self.plan = json.loads((root / "plans" / "part03.json").read_text(encoding="utf-8"))

    def _episode(self, card):
        ep = copy.deepcopy(self.plan)
        ep["title"] = "Paris Powers Its Own Tower"
        ep["title_card"] = card
        ep.pop("episode", None)
        return ep

    def _kunye_hatalari(self, card):
        errors = _validate_batch([self._episode(card)], self.bible, 3, 1, set(),
                                 cfg=self.cfg, history=[])
        return [e for e in errors if "title_card" in e]

    def test_dogru_kunye_kabul(self):
        self.assertEqual(self._kunye_hatalari({"title": "PARIS 2512", "subtitle": ""}), [])

    def test_modelin_uydurdugu_kunye_red(self):
        self.assertTrue(self._kunye_hatalari(
            {"title": "Eiffel Tower: Energy Spine", "subtitle": "Paris, France 2512"}))


if __name__ == "__main__":
    unittest.main()
