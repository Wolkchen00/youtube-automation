"""20 Eylul 2026: iki canli kanal ayni gece karanlik kaldi, kapilar burada.

Olculen arizalar:

  * still-home ep05 cekim 3 (kosu 35473217835): QC gomulu yazi yuzunden RED
    verdi, regen prompt'u ise saglayicida "Request blocked: The input content
    was flagged for containing a prominent public figure" ile 5/5 reddedildi.
    Prompt "Christ the Redeemer" yaziyordu; doktrin (KONSEPT.md 7) bunu zaten
    yasakliyordu ama hicbir kapi denetlemiyordu. Cekim dustu, min_shots=4
    bolumu oldurdu.

  * wild-encounter ep12 (kosu 35468775939): QC "ham native seste istenmeyen
    konusma" dedi, uretilen duzeltme ise "Frame only the hands, forearms,
    object, and the surface it rests on" oldu. Ses arizasina KADRAJ talimati
    gitti, uc uretim (378 kredi) bosa yandi ve bolum oldu. Kok sebep:
    positive_correction alt-dize eslestiriyordu ve ses notunun sonundaki
    "surface" kelimesi "face" dalini tetikliyordu.
"""

import json
import pathlib
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from series import critic, omni_api

REPO = pathlib.Path(__file__).resolve().parents[1]

SES_NOTU = ("Keep the soundtrack limited to natural foley from the visible hands, "
            "object, material, and surface.")
BLOK_MESAJI = ("Request blocked: The input content was flagged for containing a "
               "prominent public figure.")


class DuzeltmeYonlendirmesi(unittest.TestCase):
    """positive_correction KELIME SINIRIYLA yollar, alt-dizeyle DEGIL."""

    def test_surface_kelimesi_yuz_dalini_tetiklemez(self):
        # Olculen ariza: 'face' in 'surface' -> True idi.
        self.assertEqual(critic.correction_category(SES_NOTU), "audio")
        self.assertNotIn("forearms", critic.positive_correction(SES_NOTU))

    def test_ses_arizasi_ses_duzeltmesi_uretir(self):
        for gerekce in ("ham native seste istenmeyen konusma var",
                        "unwanted speech in the raw native audio",
                        "background music is present"):
            self.assertEqual(critic.correction_category(gerekce), "audio", gerekce)

    def test_diger_kategoriler_dogru_yollanir(self):
        beklenen = {
            "gömülü yazı/watermark": "text",
            "anatomi bozuk": "anatomy",
            "yüz referansla uyuşmuyor": "face",
            "Do not change the object colour.": "object",
            "Keep motion stable. Add another camera move.": "generic",
        }
        for gerekce, kategori in beklenen.items():
            self.assertEqual(critic.correction_category(gerekce), kategori, gerekce)

    def test_duzeltme_tek_olumlu_cumledir(self):
        for kategori in critic._CORRECTION_LEXICON:
            cumle = critic._CORRECTION_LEXICON[kategori]
            self.assertTrue(cumle.endswith("."), kategori)
            self.assertNotRegex(cumle.lower(), r"\b(?:not|never|don't|without|no)\b")


class SeriyeOzelDuzeltmeDili(unittest.TestCase):
    """Atolye dili baska konsepte SIZAMAZ."""

    def _lexicon(self, rel):
        data = json.loads((REPO / rel).read_text(encoding="utf-8"))
        return data["series"]["qc"].get("correction_lexicon")

    def test_iki_canli_seri_kendi_sozlugunu_tasir(self):
        for rel in ("sentinal_ihsan/wild-encounter/bible.json",
                    "shadowedhistory/still-home/bible.json"):
            lexicon = self._lexicon(rel)
            self.assertIsInstance(lexicon, dict, rel)
            self.assertEqual(set(lexicon), set(critic._CORRECTION_LEXICON), rel)

    def test_atolye_sozcukleri_baska_seriye_sizmaz(self):
        sizinti = ("workshop", "forearms", "bench")
        for rel in ("sentinal_ihsan/wild-encounter/bible.json",
                    "shadowedhistory/still-home/bible.json"):
            lexicon = self._lexicon(rel)
            for kategori, cumle in lexicon.items():
                for sozcuk in sizinti:
                    self.assertNotIn(sozcuk, cumle.lower(),
                                     f"{rel} / {kategori}: {sozcuk!r} sizdi")

    def test_wild_encounter_ses_arizasina_ses_cevabi_verir(self):
        lexicon = self._lexicon("sentinal_ihsan/wild-encounter/bible.json")
        cevap = critic.positive_correction(SES_NOTU, lexicon=lexicon)
        self.assertIn("sound", cevap.lower())
        self.assertNotIn("hands", cevap.lower())

    def test_bilinmeyen_anahtar_sessizce_yok_sayilir(self):
        table = critic.correction_lexicon({"uydurma": "x", "text": "Positive line."})
        self.assertNotIn("uydurma", table)
        self.assertEqual(table["text"], "Positive line.")


class ModerasyonBlogu(unittest.TestCase):
    """Girdi tarafi blogu seed ile COZULMEZ, metin temizligiyle cozulur."""

    def test_blok_mesaji_taninir(self):
        self.assertTrue(omni_api.is_moderation_block(BLOK_MESAJI))

    def test_gecici_ariza_moderasyon_sayilmaz(self):
        for mesaj in ("Internal Error", "timeout", "", None):
            self.assertFalse(omni_api.is_moderation_block(mesaj), repr(mesaj))

    def test_kisi_aniti_gecen_cumle_dusurulur(self):
        prompt = ("The mechanism fills most of the frame. The recognizable form of "
                  "Christ the Redeemer statue is visible past the mechanism. "
                  "One slow camera move only.")
        temiz, dusen = omni_api.sanitize_public_figures(prompt)
        self.assertEqual(dusen, ["christ the redeemer"])
        self.assertNotIn("Redeemer", temiz)
        self.assertIn("The mechanism fills most of the frame.", temiz)
        self.assertIn("One slow camera move only.", temiz)

    def test_temiz_prompt_aynen_doner(self):
        prompt = "Sugarloaf Mountain stands at the mouth of the bay."
        self.assertEqual(omni_api.sanitize_public_figures(prompt), (prompt, []))

    def test_her_cumle_dusecekse_prompt_korunur(self):
        prompt = "Christ the Redeemer stands on the hill."
        self.assertEqual(omni_api.sanitize_public_figures(prompt), (prompt, []))

    def test_blokta_metin_temizlenip_yeniden_denenir(self):
        """Olculen ariza: bes deneme de AYNI metni gonderdi ve bes kez bloklandi."""
        gonderilen: list[str] = []

        def sahte_create(payload):
            gonderilen.append(payload["input"]["prompt"])
            return f"task{len(gonderilen)}"

        def sahte_poll(task_id, max_attempts=None):
            # Kisi aniti hala metindeyse blok, cikinca uretim basarili.
            if "christ the redeemer" in gonderilen[-1].lower():
                return {"url": None, "credits": None, "fail_msg": BLOK_MESAJI}
            return {"url": "https://ornek/klip.mp4", "credits": 63.0}

        prompt = ("The camera is close to the transit line. The recognizable form of "
                  "Christ the Redeemer statue is visible past the mechanism. "
                  "One slow camera move only.")
        with mock.patch.object(omni_api, "create_task", sahte_create), \
             mock.patch.object(omni_api, "poll_omni_task", sahte_poll), \
             mock.patch.object(omni_api.time, "sleep", lambda *_: None):
            sonuc = omni_api.generate_omni_shot(prompt, duration="4")

        self.assertEqual(sonuc["url"], "https://ornek/klip.mp4")
        self.assertEqual(len(gonderilen), 2, "temizlenmis metinle TEK yeniden deneme")
        self.assertIn("Christ the Redeemer", gonderilen[0])
        self.assertNotIn("Christ the Redeemer", gonderilen[1])

    def test_temizlenecek_ad_yoksa_blok_erken_birakilir(self):
        """Bes deneme ayni uc dakikalik pencereye sigiyordu; olcum blogun
        saatler icinde gectigini gosterdi, pencereyi zorlamanin degeri yok."""
        cagri = {"n": 0}

        def sahte_create(payload):
            cagri["n"] += 1
            return f"task{cagri['n']}"

        def sahte_poll(task_id, max_attempts=None):
            return {"url": None, "credits": None, "fail_msg": BLOK_MESAJI}

        with mock.patch.object(omni_api, "create_task", sahte_create), \
             mock.patch.object(omni_api, "poll_omni_task", sahte_poll), \
             mock.patch.object(omni_api.time, "sleep", lambda *_: None):
            sonuc = omni_api.generate_omni_shot("A clean city aerial.", duration="4")

        self.assertIsNone(sonuc)
        self.assertEqual(cagri["n"], omni_api._MODERATION_ATTEMPT_LIMIT)

    def test_gecici_ariza_hala_bes_kez_denenir(self):
        """Moderasyon sinirlamasi GECICI arizanin butcesini kisaltmamali."""
        cagri = {"n": 0}

        def sahte_create(payload):
            cagri["n"] += 1
            return f"task{cagri['n']}"

        with mock.patch.object(omni_api, "create_task", sahte_create), \
             mock.patch.object(omni_api, "poll_omni_task",
                               lambda *a, **k: {"url": None, "fail_msg": "Internal Error"}), \
             mock.patch.object(omni_api.time, "sleep", lambda *_: None):
            sonuc = omni_api.generate_omni_shot("A clean city aerial.", duration="4")

        self.assertIsNone(sonuc)
        self.assertEqual(cagri["n"], 5)


class CanliKuyrukTemiz(unittest.TestCase):
    """Doktrin kural 7 canli veride de gecerli olmali."""

    def test_bekleyen_planlarda_kisi_aniti_yok(self):
        seri = REPO / "shadowedhistory" / "still-home"
        siradaki = int(json.loads((seri / "series.json").read_text(encoding="utf-8"))
                       .get("next_part") or 1)
        bakilan = 0
        for yol in sorted((seri / "plans").glob("part*.json")):
            if int(yol.stem.replace("part", "")) < siradaki:
                continue
            bakilan += 1
            metin = yol.read_text(encoding="utf-8").lower()
            for ad in omni_api.PUBLIC_FIGURE_SUBJECTS:
                self.assertNotIn(ad, metin, f"{yol.name}: {ad!r}")
        self.assertGreater(bakilan, 0, "denetlenecek bekleyen plan yok")

    def test_konu_havuzunda_kisi_aniti_yok(self):
        cfg = json.loads((REPO / "shadowedhistory" / "still-home" / "series.json")
                         .read_text(encoding="utf-8"))["auto_replenish"]
        for konu in cfg["topic_pool"]:
            dusuk = konu["topic"].lower()
            for ad in omni_api.PUBLIC_FIGURE_SUBJECTS:
                self.assertNotIn(ad, dusuk, f"konu {konu['id']}: {ad!r}")

    def test_ikmal_motoru_kisi_anitini_yazamaz(self):
        cfg = json.loads((REPO / "shadowedhistory" / "still-home" / "series.json")
                         .read_text(encoding="utf-8"))["auto_replenish"]
        from series.replenish import _banned_phrases
        yasak = _banned_phrases(cfg, 3)
        self.assertIn("christ the redeemer", yasak)
        self.assertIn("statue of liberty", yasak)


class CaptionIkiDilli(unittest.TestCase):
    """Kural 14: once Ingilizce blok, sonra SEHRIN KENDI DILI.

    Bu kusur yayini durdurmaz, erisimi yariya dusurur: video anlatimsiz oldugu
    icin caption HIKAYENIN KENDISIDIR ve yerel blok o sehirde yasayanlara
    hitap eder. 20 Eylul 2026'da kuyrukta IKI plan birden tek dilliydi
    (part05 Rio/Portekizce, part06 Tokyo/Japonca) ve hicbir kapi bakmiyordu.

    Denetim aracinda UYARI, burada SERT kural: uretim kapisini caption yuzunden
    kapatmak gunun videosunu oldururdu, ama gelistirme sirasinda sessizce
    gecmesi de yasak.
    """

    def _kurulum(self):
        import tools.siluet_denetim as sd
        seri = REPO / "shadowedhistory" / "still-home"
        meta = json.loads((seri / "series.json").read_text(encoding="utf-8"))
        return sd, seri, meta

    def test_bekleyen_planlarin_caption_dili_dogru(self):
        sd, seri, meta = self._kurulum()
        havuz = (meta.get("auto_replenish") or {}).get("topic_pool") or []
        siradaki = int(meta.get("next_part") or 1)
        bakilan = 0
        for yol in sorted((seri / "plans").glob("part*.json")):
            if int(yol.stem.replace("part", "")) < siradaki:
                continue
            bakilan += 1
            plan = json.loads(yol.read_text(encoding="utf-8"))
            self.assertEqual(sd.caption_uyarilari(plan, havuz), [], yol.name)
        self.assertGreater(bakilan, 0, "denetlenecek bekleyen plan yok")

    def test_ingilizce_sehirde_tek_blok_dogru_sayilir(self):
        sd, _, meta = self._kurulum()
        havuz = (meta.get("auto_replenish") or {}).get("topic_pool") or []
        plan = {
            "title_card": {"title": "NEW YORK 2512"},
            "caption": ("New York built something.\n\n"
                        f"{sd.INGILIZCE_KUNYE}\n\nWhat would you build?"),
        }
        self.assertEqual(sd.caption_uyarilari(plan, havuz), [])

    def test_tek_dilli_yerel_sehir_yakalanir(self):
        sd, _, meta = self._kurulum()
        havuz = (meta.get("auto_replenish") or {}).get("topic_pool") or []
        plan = {
            "title_card": {"title": "TOKYO 2512"},
            "caption": ("Tokyo built something.\n\n"
                        f"{sd.INGILIZCE_KUNYE}\n\nWhat would you build?"),
        }
        uyarilar = sd.caption_uyarilari(plan, havuz)
        self.assertTrue(any("TEK DILLI" in u for u in uyarilar), uyarilar)
        self.assertTrue(any("yazi sistemi" in u for u in uyarilar), uyarilar)

    def test_caption_uyarisi_cikis_kodunu_etkilemez(self):
        """Denetim araci caption yuzunden uretimi KAPATMAZ."""
        sd, seri, _ = self._kurulum()
        kod = sd.main(["--plan", str(seri / "plans" / "part06.json")])
        self.assertEqual(kod, 0)

    def test_kural_TEK_kaynakta_yasar(self):
        """Denetim araci kurali KOPYALAMAZ, replenish'ten alir.

        Iki kopya kacinilmaz olarak ayrisir: 7b44efa ses cumlesini duzeltti
        ama qc_shot icindeki ikinci kopya eski kaldi ve duzeltme tutmadi.
        """
        import tools.siluet_denetim as sd
        from series import replenish
        self.assertFalse(hasattr(sd, "YAZI_ARALIKLARI"),
                         "denetim araci yazi tablosunu KOPYALAMIS")
        self.assertTrue(hasattr(replenish, "CAPTION_SCRIPT_RANGES"))

    def test_ikmal_dongusu_tek_dilli_captioni_reddeder(self):
        """Bozuk parti kredi harcanmadan yeniden yazdirilir."""
        from series.replenish import caption_language_errors
        _, seri, meta = self._kurulum()
        cfg = meta["auto_replenish"]
        plan = json.loads((seri / "plans" / "part06.json").read_text(encoding="utf-8"))
        self.assertEqual(caption_language_errors(plan, cfg), [])
        bozuk = dict(plan)
        bozuk["caption"] = plan["caption"].split("2512年")[0].strip()
        self.assertTrue(caption_language_errors(bozuk, cfg))

    def test_kapi_yalniz_yapilandirma_yaziliysa_calisir(self):
        """Anahtari olmayan seriler ETKILENMEZ."""
        from series.replenish import caption_language_errors
        _, seri, meta = self._kurulum()
        plan = json.loads((seri / "plans" / "part06.json").read_text(encoding="utf-8"))
        plan["caption"] = "English only, no local block."
        kapali = {"topic_pool": meta["auto_replenish"]["topic_pool"]}
        self.assertEqual(caption_language_errors(plan, kapali), [])


if __name__ == "__main__":
    unittest.main()
