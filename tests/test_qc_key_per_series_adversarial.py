"""ROCK 1b (anahtar izolasyonu) düşman testleri , Visionary incelemesi.

Codex'in tests/test_qc_key_per_series.py dosyası sözleşmedeki (a)-(g)'yi kapsıyor.
Bu dosya ÜRETİMDE patlayacak olanı kovalar: tanımsız bir GitHub secret'ının
`.env`'e BOŞ satır olarak düşmesi, seriler arası sızıntı, slug çakışması ve
anahtarın loga hiç sızmadığının gerçek log yakalamasıyla doğrulanması.
"""
import importlib
import logging
import os
import unittest
from unittest import mock

import series.critic as critic


def resolve(slug=None, **env):
    """_qc_api_key'i izole bir ortamda çağır; (kaynak_adı, anahtar) döndür."""
    clean = {k: v for k, v in os.environ.items()
             if not k.startswith("GEMINI_API_KEY")}
    clean.update(env)
    with mock.patch.dict(os.environ, clean, clear=True):
        importlib.reload(critic)
        critic._QC_KEY_SOURCE_LOGGED = True   # log gürültüsünü sustur
        key, source = critic._qc_api_key(slug)
    return source, key


class Adversarial(unittest.TestCase):

    # --- 1. ÜRETİM SENARYOSU: tanımsız secret boş string olarak gelir --------
    def test_unset_github_secret_renders_empty_and_degrades_silently(self):
        """`GEMINI_API_KEY_QC_UNNATURAL_LAB=` (boş) -> filo anahtarına düşmeli.

        unnatural-lab.yml heredoc'unda secret tanımsızsa satır BOŞ değerle
        yazılır. Bu, İhsan projeyi açana kadar geçerli olacak gerçek durumdur;
        koşu kırılmamalı.
        """
        source, key = resolve(
            "unnatural-lab",
            GEMINI_API_KEY_QC_UNNATURAL_LAB="",
            GEMINI_API_KEY_QC="filo-anahtari",
            GEMINI_API_KEY="uretim-anahtari",
        )
        self.assertEqual(source, "GEMINI_API_KEY_QC")
        self.assertEqual(key, "filo-anahtari")

    def test_unset_secret_with_only_whitespace_also_degrades(self):
        source, key = resolve(
            "unnatural-lab",
            GEMINI_API_KEY_QC_UNNATURAL_LAB="   \t ",
            GEMINI_API_KEY_QC="filo-anahtari",
            GEMINI_API_KEY="uretim-anahtari",
        )
        self.assertEqual(source, "GEMINI_API_KEY_QC")

    def test_all_qc_vars_empty_falls_all_the_way_to_production_key(self):
        """Hepsi bossa uretim anahtarina duser , BUGUNKU davranisin aynisi.

        Not: `GEMINI_API_KEY` core/env.py:31'de IMPORT ANINDA okunan bir modul
        sabitidir (os.getenv), cagri aninda env'den okunmaz. Bu davranis
        origin/main ile birebir ayni; bu rock onu DEGISTIRMEDI. Bu yuzden test
        env'i degil modul niteligini yamalar.
        """
        clean = {k: v for k, v in os.environ.items()
                 if not k.startswith("GEMINI_API_KEY")}
        clean.update(GEMINI_API_KEY_QC_UNNATURAL_LAB="", GEMINI_API_KEY_QC="")
        with mock.patch.dict(os.environ, clean, clear=True):
            importlib.reload(critic)
            critic._QC_KEY_SOURCE_LOGGED = True
            with mock.patch.object(critic, "GEMINI_API_KEY", "uretim-anahtari"):
                key, source = critic._qc_api_key("unnatural-lab")
        self.assertEqual(source, "GEMINI_API_KEY")
        self.assertEqual(key, "uretim-anahtari")

    # --- 2. Seriler arası sızıntı -------------------------------------------
    def test_no_cross_series_leak(self):
        """flashpoints, Sentinal'in ayrılmış anahtarını ASLA kullanmamalı.

        İzolasyonun bütün amacı bu; sızarsa ayrı proje anlamsızlaşır.
        """
        env = dict(GEMINI_API_KEY_QC_UNNATURAL_LAB="sentinal-ozel",
                   GEMINI_API_KEY_QC="filo-anahtari",
                   GEMINI_API_KEY="uretim-anahtari")
        s_sent, k_sent = resolve("unnatural-lab", **env)
        s_flash, k_flash = resolve("flashpoints", **env)
        self.assertEqual(k_sent, "sentinal-ozel")
        self.assertEqual(k_flash, "filo-anahtari", "BAŞKA SERİ Sentinal anahtarını aldı")
        self.assertNotEqual(k_sent, k_flash)

    def test_slug_none_is_todays_behaviour(self):
        source, key = resolve(
            None,
            GEMINI_API_KEY_QC_UNNATURAL_LAB="sentinal-ozel",
            GEMINI_API_KEY_QC="filo-anahtari",
            GEMINI_API_KEY="uretim-anahtari",
        )
        self.assertEqual(source, "GEMINI_API_KEY_QC")

    # --- 3. Slug normalizasyonu ve çakışma ----------------------------------
    def test_slug_normalisation_shapes(self):
        for slug, expected in [
            ("unnatural-lab", "GEMINI_API_KEY_QC_UNNATURAL_LAB"),
            ("next-stop", "GEMINI_API_KEY_QC_NEXT_STOP"),
            ("room-408", "GEMINI_API_KEY_QC_ROOM_408"),
            ("could-you-survive", "GEMINI_API_KEY_QC_COULD_YOU_SURVIVE"),
        ]:
            with self.subTest(slug=slug):
                source, key = resolve(slug, **{expected: "hedef", "GEMINI_API_KEY": "u"})
                self.assertEqual(source, expected)
                self.assertEqual(key, "hedef")

    def test_separator_collision_is_documented(self):
        """`a-b` ve `a_b` AYNI değişkene normalize olur , bilinen çakışma.

        Bugün zararsız (mevcut slug'ların hiçbiri çakışmıyor) ama yeni bir seri
        eklenirken sürpriz olmasın diye kayıt altında.
        """
        env = {"GEMINI_API_KEY_QC_A_B": "ortak", "GEMINI_API_KEY": "u"}
        self.assertEqual(resolve("a-b", **env)[1], "ortak")
        self.assertEqual(resolve("a_b", **env)[1], "ortak")

    # --- 4. Anahtar loga SIZMIYOR (gerçek log yakalamasıyla) ----------------
    def test_key_value_never_appears_in_logs(self):
        secret = "COK-GIZLI-ANAHTAR-DEGERI-123"
        clean = {k: v for k, v in os.environ.items()
                 if not k.startswith("GEMINI_API_KEY")}
        clean.update(GEMINI_API_KEY_QC_UNNATURAL_LAB=secret, GEMINI_API_KEY="u")
        with mock.patch.dict(os.environ, clean, clear=True):
            importlib.reload(critic)
            critic._QC_KEY_SOURCE_LOGGED = False      # loglamayı BİLEREK aç
            with self.assertLogs(level=logging.INFO) as caught:
                key, source = critic._qc_api_key("unnatural-lab")
            blob = "\n".join(caught.output)
        self.assertEqual(key, secret)
        self.assertNotIn(secret, blob, "ANAHTAR DEĞERİ LOGA SIZDI")
        self.assertIn("GEMINI_API_KEY_QC_UNNATURAL_LAB", blob,
                      "kaynak adı loglanmalı ki hangi havuz kullanıldığı görülsün")

    # --- 5. Workflow gerçekten bağlamış mı ----------------------------------
    def test_workflow_wires_the_secret_and_only_for_sentinal(self):
        import pathlib
        wf = pathlib.Path(__file__).resolve().parents[1] / ".github" / "workflows"
        sentinal = (wf / "unnatural-lab.yml").read_text(encoding="utf-8")
        self.assertIn("GEMINI_API_KEY_QC_UNNATURAL_LAB=${{ secrets.GEMINI_API_KEY_QC_UNNATURAL_LAB }}",
                      sentinal, "secret unnatural-lab.yml'e bağlanmamış")
        for other in wf.glob("*.yml"):
            if other.name == "unnatural-lab.yml":
                continue
            self.assertNotIn("GEMINI_API_KEY_QC_UNNATURAL_LAB",
                             other.read_text(encoding="utf-8"),
                             f"{other.name} kapsam dışıyken değiştirilmiş")


if __name__ == "__main__":
    unittest.main()
