"""Family kilidi bir daha kanal olduremesin (ROCK D).

`_validate_batch` kurali: ardisik iki part ayni `family` degerini kullanamaz.
Havuz YEREL bir kisitla tuketiliyor ama KURESEL fizibilite gozetilmiyor: cesitli
family'ler erken harcaniyor, dibe ayni family'den tohumlar birikiyor. Kalan TUM
tohumlarin family'si son bolumunkiyle ayni oldugunda ilk bolume sunulan aday
listesi BOSALIYOR ve gorev matematiksel olarak cozulemez oluyor.

2026-09-01..04: Galactic Experiment dort gun sessiz (kalan {14,24}, ikisi de
'olcek soku'); shadowedhistory ertesi gun olecekti (kalan {12,16}, 'efsane vs kayit').

Gevseme YALNIZ baska care kalmadiginda ve YALNIZ ilk bolum icin gecerlidir.
"""
from __future__ import annotations

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from series import replenish  # noqa: E402

FAMILIES = ["alfa", "beta", "gama"]


def cfg(topics, families=FAMILIES):
    return {"families": list(families), "topic_pool": list(topics)}


def gecmis(*aile_ler):
    """Son elemanin family'si 'yasak family' olur."""
    return [{"n": i + 1, "title": f"E{i}", "synopsis": f"S{i}",
             "seed_id": 900 + i, "family": f}
            for i, f in enumerate(aile_ler)]


class KararTests(unittest.TestCase):
    """Saf karar fonksiyonu: yalniz gercekten cozumsuzken True."""

    def test_kalan_tohumlarin_HEPSI_yasak_family_ise_gevser(self):
        c = cfg([{"id": 1, "topic": "t1", "family": "alfa"},
                 {"id": 2, "topic": "t2", "family": "alfa"}])
        self.assertTrue(replenish.first_family_relaxed(c, gecmis("alfa"), {}))

    def test_ALTERNATIF_family_varsa_GEVSEMEZ(self):
        """Eski davranis korunmali; stil rotasyonu bosuna feda edilmez."""
        c = cfg([{"id": 1, "topic": "t1", "family": "alfa"},
                 {"id": 2, "topic": "t2", "family": "beta"}])
        self.assertFalse(replenish.first_family_relaxed(c, gecmis("alfa"), {}))

    def test_havuz_TAMAMEN_bossa_gevsemez(self):
        """Sorun family degil tedarik; gevsetmek cozmez, gizler."""
        c = cfg([])
        self.assertFalse(replenish.first_family_relaxed(c, gecmis("alfa"), {}))

    def test_gecmis_yoksa_gevsemez(self):
        c = cfg([{"id": 1, "topic": "t1", "family": "alfa"}])
        self.assertFalse(replenish.first_family_relaxed(c, [], {}))

    def test_kullanilmis_tohumlar_hesaba_katilir(self):
        """Beta tohumu KULLANILMISSA geriye yalniz alfa kalir -> gevser."""
        c = cfg([{"id": 1, "topic": "t1", "family": "alfa"},
                 {"id": 2, "topic": "t2", "family": "beta"}])
        h = [{"n": 1, "title": "E0", "synopsis": "S0", "seed_id": 2, "family": "beta"},
             {"n": 2, "title": "E1", "synopsis": "S1", "seed_id": 9, "family": "alfa"}]
        self.assertTrue(replenish.first_family_relaxed(c, h, {}))


class DogrulayiciTests(unittest.TestCase):
    """Gevseme YALNIZ ilk ogede; batch ici komsuluklar aynen zorunlu."""

    def _bolum(self, no, family, seed_id, baslik):
        return {"episode": {"number": no, "title": baslik, "synopsis": "s"},
                "family": family, "seed_id": seed_id,
                "shots": [{"n": 1, "prompt": "p"}, {"n": 2, "prompt": "p"}]}

    def _dogrula(self, episodes, c, h):
        from series.bible import Bible
        return replenish._validate_batch(
            episodes, Bible.load("flashpoints"), 1, len(episodes),
            set(), c, h, {},
        )

    def test_KACINILMAZ_ilk_tekrar_KABUL_edilir(self):
        c = cfg([{"id": 1, "topic": "t1", "family": "alfa"},
                 {"id": 2, "topic": "t2", "family": "alfa"}])
        h = gecmis("alfa")
        hatalar = self._dogrula([self._bolum(1, "alfa", 1, "Bir")], c, h)
        aile_hatasi = [e for e in hatalar if "ardışık iki part" in e]
        self.assertFalse(aile_hatasi, f"kacinilmaz ilk tekrar reddedildi: {hatalar}")

    def test_batch_ICINDEKI_ikinci_ardisik_tekrar_HALA_REDDEDILIR(self):
        """Gevseme yalniz ILK ogeyi kapsar; sonrasi disiplin aynen surer."""
        c = cfg([{"id": 1, "topic": "t1", "family": "alfa"},
                 {"id": 2, "topic": "t2", "family": "alfa"}])
        h = gecmis("alfa")
        hatalar = self._dogrula(
            [self._bolum(1, "alfa", 1, "Bir"), self._bolum(2, "alfa", 2, "Iki")],
            c, h,
        )
        aile_hatasi = [e for e in hatalar if "ardışık iki part" in e]
        self.assertTrue(aile_hatasi,
                        "batch icindeki ikinci ardisik tekrar gecti, kural coktu")

    def test_alternatif_varken_yasak_family_HALA_REDDEDILIR(self):
        c = cfg([{"id": 1, "topic": "t1", "family": "alfa"},
                 {"id": 2, "topic": "t2", "family": "beta"}])
        h = gecmis("alfa")
        hatalar = self._dogrula([self._bolum(1, "alfa", 1, "Bir")], c, h)
        aile_hatasi = [e for e in hatalar if "ardışık iki part" in e]
        self.assertTrue(aile_hatasi,
                        "alternatif family varken yasak family kabul edildi")


class PromptTests(unittest.TestCase):
    """Prompt bir sey deyip dogrulayici baskasini beklerse plan yine reddedilir."""

    def _prompt(self, c, h):
        from series.bible import Bible
        from series.series_meta import SeriesMeta
        contents, sysins = replenish._build_prompt(
            SeriesMeta.load("flashpoints"), Bible.load("flashpoints"),
            c, 1, 2, h, calibration={},
        )
        # Kurallar system instruction'da, tohum havuzu contents'te durur.
        # Ikisi birlikte modelin gordugu TAM prompt'tur.
        return contents + chr(10) + sysins

    def test_gevsemede_prompt_YALNIZ_ilk_tekrara_izin_verir(self):
        c = cfg([{"id": 1, "topic": "t1", "family": "alfa"},
                 {"id": 2, "topic": "t2", "family": "alfa"}])
        metin = self._prompt(c, gecmis("alfa"))
        self.assertIn("FAMILY EXCEPTION FOR EPISODE 1", metin)
        self.assertNotIn("CRITICAL FAMILY BLOCK", metin)
        self.assertNotIn("must never use the same family", metin,
                         "celiskili mutlak kural hala prompt'ta")
        self.assertIn("Episodes after 1 must not repeat", metin)

    def test_gevseme_YOKKEN_prompt_ESKISI_gibi_katidir(self):
        c = cfg([{"id": 1, "topic": "t1", "family": "alfa"},
                 {"id": 2, "topic": "t2", "family": "beta"}])
        metin = self._prompt(c, gecmis("alfa"))
        self.assertIn("CRITICAL FAMILY BLOCK FOR EPISODE 1", metin)
        self.assertIn("must never use the same family", metin)
        self.assertNotIn("FAMILY EXCEPTION", metin)


if __name__ == "__main__":
    unittest.main()
