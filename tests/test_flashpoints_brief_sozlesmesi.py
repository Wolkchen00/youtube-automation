# -*- coding: utf-8 -*-
"""flashpoints uretim prompt'u sozlesme testleri.

Bu dosya METNI degil, MODELE GIDEN IKI KANALI denetler:
`_build_prompt` -> (contents, system_instruction).

Gerekce: brief'i duzeltmek ancak prompt'a girdigi olcude bir sey degistirir.
Config'e dogru cumleyi yazip prompt'un onu tasidigini VARSAYMAK bos bir kanittir.
"""

import copy
import json
import pathlib
import re
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from series.bible import Bible                      # noqa: E402
from series.series_meta import SeriesMeta           # noqa: E402
from series.replenish import _build_prompt          # noqa: E402

SERIES_JSON = REPO_ROOT / "shadowedhistory" / "flashpoints" / "series.json"
BRIEF_BASLIK = "CREATIVE BRIEF for new episodes:"

# Kunye kuralinin OPERATIF parcalari. Yalniz orneklere bakmak, tersine cevrilmis
# ya da disi sokulmus bir kurali da gecirirdi; bu yuzden yasak, yerine-koyma
# talimati ve duzeltilmis ornek AYRI AYRI aranir.
KURAL_YASAK = "that name must NOT go on the card"
KURAL_YERINE = "write the recognisable thing from the story instead"
KURAL_ORNEK = "EMPTY ISLAND INVASION"

# Brief blogunda BULUNMAMASI gereken sayi kaliplari (tek kaynak: yapisal config).
SURE_KALIBI = re.compile(r"\d+\s*(?:sn|saniye|second)", re.IGNORECASE)
KELIME_KALIBI = re.compile(r"\d+\s*[-,]\s*\d+\s*kelime", re.IGNORECASE)


def _prompt(cfg_ustu=None):
    """flashpoints icin (contents, system_instruction) uret.

    cfg_ustu verilirse auto_replenish'in KOPYASI uzerinde uygulanir; diskteki
    dosya degismez.
    """
    meta = SeriesMeta.load("flashpoints")
    bible = Bible.load("flashpoints")
    cfg = copy.deepcopy(meta.auto_replenish)
    if cfg_ustu:
        cfg.update(cfg_ustu)
    return _build_prompt(meta, bible, cfg, start=99, batch=1, history=[])


def _brief_blogu(contents):
    """contents icindeki CREATIVE BRIEF bolumunu izole et.

    Brief tek satirdir (test: test_brief_tek_satir), yani baslik satirindan
    sonraki TEK satir. Blok siniri boyle kesin cizilir; tum contents icinde
    sayi aramak baska bolumlerin sayilarini yakalardi.
    """
    assert BRIEF_BASLIK in contents, "CREATIVE BRIEF bolumu prompt'ta yok"
    sonrasi = contents.split(BRIEF_BASLIK, 1)[1]
    return sonrasi.lstrip("\n").split("\n", 1)[0]


class FlashpointsPromptContractTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.contents, cls.system = _prompt()
        cls.ar = json.loads(SERIES_JSON.read_text(encoding="utf-8"))["auto_replenish"]

    # ---- 1-2: iki kanal ve yerleri -------------------------------------
    def test_brief_contents_icinde_kural_system_icinde(self):
        """Ayrim onemli: kullanici metni sistem kuralini ezemez, bu yuzden
        kunye kurali system_instruction'da OLMALI."""
        self.assertIn(BRIEF_BASLIK, self.contents)
        self.assertNotIn(BRIEF_BASLIK, self.system)
        self.assertIn("- TITLE_CARD:", self.system)
        self.assertNotIn("- TITLE_CARD:", self.contents)

    def test_brief_tek_satir(self):
        """_brief_blogu bu varsayima dayaniyor; kirilirsa izolasyon bozulur."""
        self.assertNotIn("\n", self.ar["brief"])

    # ---- 3: brief SAYI TASIMIYOR ---------------------------------------
    def test_brief_blogunda_sure_sayisi_yok(self):
        blok = _brief_blogu(self.contents)
        bulunan = SURE_KALIBI.findall(blok)
        self.assertEqual(bulunan, [], "brief sure sayisi tasiyor: %r" % bulunan)

    def test_brief_blogunda_kelime_araligi_yok(self):
        blok = _brief_blogu(self.contents)
        bulunan = KELIME_KALIBI.findall(blok)
        self.assertEqual(bulunan, [], "brief kelime araligi tasiyor: %r" % bulunan)

    # ---- 4: sistem talimati sayiyi YAPISAL CONFIG'ten basiyor -----------
    def test_narration_araligi_yapisal_configten_geliyor(self):
        wmin = self.ar["narration"]["min_words"]
        wmax = self.ar["narration"]["max_words"]
        self.assertIn("- NARRATION: %d-%d words" % (wmin, wmax), self.system)

    # ---- 5: dayanak guncel ----------------------------------------------
    def test_dayanak_v18(self):
        blok = _brief_blogu(self.contents)
        self.assertIn("v1.8", blok)
        self.assertNotIn("v1.6", blok)

    # ---- 6: kunye kurali sistem talimatinda, OPERATIF haliyle ------------
    def test_kunye_kurali_operatif_haliyle_sistemde(self):
        for parca in (KURAL_YASAK, KURAL_YERINE, KURAL_ORNEK):
            with self.subTest(parca=parca):
                self.assertIn(parca, self.system)

    # ---- 7: sema yer tutucusu artik "ozne adi" dayatmiyor ---------------
    def test_sema_yer_tutucusu_yansiz(self):
        self.assertNotIn("<subject name, max 40 chars>", self.system)
        self.assertIn("<title, max 40 chars>", self.system)

    # ---- 8: BOS GECMEYEN CAPA -------------------------------------------
    def test_capa_ayar_bosken_yalniz_kanal_isaretleri_kaybolur(self):
        """Codex turu 1 [KILL]: 'her sey kaybolsun' imkansizdi , yapisal
        config'ten gelenler brief bosken de durmalidir."""
        contents, system = _prompt({"brief": "", "title_card_style": ""})

        # kanal isaretleri KAYBOLMALI
        self.assertNotIn(BRIEF_BASLIK, contents)
        for parca in (KURAL_YASAK, KURAL_YERINE, KURAL_ORNEK):
            self.assertNotIn(parca, system)

        # yapisal config'ten gelenler KALMALI
        wmin = self.ar["narration"]["min_words"]
        wmax = self.ar["narration"]["max_words"]
        self.assertIn("- NARRATION: %d-%d words" % (wmin, wmax), system)
        self.assertIn("- TITLE_CARD:", system)
        self.assertIn("Return STRICT JSON ONLY", system)

    # ---- 9: ayar yokken BUGUNKU metin bit bit uretilir -------------------
    def test_ayar_yokken_varsayilan_metin_birebir(self):
        """title_card_style TASIMAYAN kanallar (event-horizon, unnatural-lab,
        drowned-history...) bu kosudan etkilenmemeli."""
        _, system = _prompt({"title_card_style": ""})
        self.assertIn(
            '- TITLE_CARD: "title" = the subject/site name (max 40 chars); '
            '"subtitle" = place and year exactly as the CREATIVE BRIEF instructs '
            "(max 48 chars).",
            system,
        )
        self.assertIn('"title_card": {"title": "<subject name, max 40 chars>", '
                      '"subtitle": "<max 48 chars>"},', system)

    def test_celestial_kolu_sizmiyor(self):
        """year_required False kolu (event-horizon'a ait) flashpoints'e sizmamali,
        ne ayar varken ne ayar yokken."""
        self.assertNotIn("celestial subject name", self.system)
        _, system_ayarsiz = _prompt({"title_card_style": ""})
        self.assertNotIn("celestial subject name", system_ayarsiz)

    # ---- 10: JSON butunlugu ---------------------------------------------
    def test_json_butunlugu(self):
        d = json.loads(SERIES_JSON.read_text(encoding="utf-8"))
        ar = d["auto_replenish"]
        self.assertEqual(ar["shots"], 2)
        self.assertEqual(ar["shot_seconds"], "10")
        self.assertEqual(ar["narration"], {"min_words": 26, "max_words": 36})
        self.assertEqual(len(ar["topic_pool"]), 54)
        self.assertEqual(d["next_part"], 31)
        self.assertIn("title_style", ar)
        self.assertTrue(ar["title_style"].startswith("a punchy English"))


if __name__ == "__main__":
    unittest.main()
