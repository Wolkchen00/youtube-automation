"""RF prompt denetcisi icin BAGIMSIZ saldiri testleri (Visionary yazdi, Codex gormedi).

Codex'in kendi paketi spec maddelerini kanitliyor. Bu dosya spec'in KENARLARINI zorlar:
sinir degerleri (45/46, 60/61, 0.300/0.301), Turkce metin, bozuk girdi, ve ucdan uca yol.
"""

import json
import pathlib
import sys
import unittest


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from tools import rf_prompt_lint


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SERIES_ROOT = REPO_ROOT / "aimagine" / "from-scratch"


class BoundaryTests(unittest.TestCase):
    """Klasik bir-eksik hatasi: sinirin kendisi gecmeli, bir fazlasi dusmeli."""

    def test_shot_plan_45_words_passes_46_fails(self):
        line45 = " ".join(["alpha"] * 45)
        line46 = " ".join(["alpha"] * 46)
        self.assertEqual(rf_prompt_lint.word_count(line45), 45)
        self.assertEqual(rf_prompt_lint.lint_shot_plan([line45]), [])
        hits = rf_prompt_lint.lint_shot_plan([line46])
        self.assertTrue(any(v["rule"] == "length" for v in hits))

    def test_plan_body_60_words_passes_61_fails(self):
        art = "Clean style."
        plan60 = {"shots": [{"n": 1, "prompt": "PREFIX.\n\n" + " ".join(["alpha"] * 60)}]}
        plan61 = {"shots": [{"n": 1, "prompt": "PREFIX.\n\n" + " ".join(["alpha"] * 61)}]}
        self.assertEqual(
            [v for v in rf_prompt_lint.lint_plan_data(plan60, art, [], "p") if v["rule"] == "length"],
            [],
        )
        self.assertTrue(
            any(v["rule"] == "length"
                for v in rf_prompt_lint.lint_plan_data(plan61, art, [], "p"))
        )

    def test_repetition_exactly_30_percent_passes(self):
        """Spec 'oran > 0,30 ise hata' diyor; tam 0,30 GECMELI."""
        # 17 sozcuklu govde -> 10 adet 8-gram. Bunlarin 3'u onekle ortak = 0,30.
        body_words = [f"w{i}" for i in range(17)]
        body = " ".join(body_words)
        prefix = " ".join(body_words[0:10])  # ilk 10 sozcuk -> 3 ortak 8-gram
        ratio = rf_prompt_lint.repetition_ratio(prefix, body)
        self.assertAlmostEqual(ratio, 0.30, places=6)
        plan = {"shots": [{"n": 1, "prompt": f"{prefix}\n\n{body}"}]}
        self.assertEqual(
            [v for v in rf_prompt_lint.lint_plan_data(plan, "", [], "p")
             if v["rule"] == "repetition"],
            [],
        )

    def test_identical_prefix_and_body_is_full_repetition(self):
        text = " ".join(f"w{i}" for i in range(20))
        self.assertEqual(rf_prompt_lint.repetition_ratio(text, text), 1.0)


class RobustnessTests(unittest.TestCase):
    """Bozuk, bos ve Turkce girdi denetciyi patlatmamali."""

    def test_empty_and_none_inputs_do_not_crash(self):
        for value in ("", None, "   ", "\n\n"):
            with self.subTest(value=repr(value)):
                self.assertEqual(rf_prompt_lint.find_negations(value), [])
                self.assertEqual(rf_prompt_lint.find_prohibited_nouns(value), [])
                self.assertEqual(rf_prompt_lint.word_count(value), 0)
                self.assertEqual(rf_prompt_lint.lint_qc_notes(value), [])

    def test_turkish_text_neither_crashes_nor_false_positives(self):
        turkce = ("Isik kaynagi, yalniz sira, kanit, tani, anlam, notlar, nokta, "
                  "ışık kaynağı, yalnız sıra, kanıt, tanı, nörolojik, sınır")
        self.assertEqual(rf_prompt_lint.find_negations(turkce), [])
        self.assertEqual(rf_prompt_lint.find_prohibited_nouns(turkce), [])

    def test_curly_apostrophe_dont_is_caught(self):
        self.assertIn("don't", rf_prompt_lint.find_negations("we don’t show text"))
        self.assertIn("don't", rf_prompt_lint.find_negations("we don't show text"))

    def test_free_of_across_newline_is_caught(self):
        self.assertIn("free of", rf_prompt_lint.find_negations("surfaces free\nof marks"))

    def test_malformed_plan_reports_format_not_crash(self):
        for bad in ({}, {"shots": "nope"}, {"shots": [None]}, {"shots": [{"n": 1}]}):
            with self.subTest(bad=bad):
                out = rf_prompt_lint.lint_plan_data(bad, "art", [], "p")
                self.assertIsInstance(out, list)

    def test_missing_series_dir_reports_config_violation(self):
        out = rf_prompt_lint.lint_series(REPO_ROOT / "yok-boyle-bir-klasor")
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["surface"], "config")

    def test_prefix_with_empty_body_does_not_crash(self):
        prefix = "CAMERA A, CHAIN BREAK: open a fresh exterior scene."
        plan = {"shots": [{"n": 1, "prompt": prefix}]}
        out = rf_prompt_lint.lint_plan_data(plan, "", [prefix], "p")
        self.assertEqual([v for v in out if v["rule"] in ("length", "repetition")], [])


class NounScopeTests(unittest.TestCase):
    """Yasakli nesne taramasinin gercekten calistigi ve kacirdigi yerler."""

    def test_plural_and_case_are_caught(self):
        for text in ("Neon LOGOS on the wall", "two Screens", "a Billboard", "license plates"):
            with self.subTest(text=text):
                self.assertTrue(rf_prompt_lint.find_prohibited_nouns(text), text)

    def test_multiword_noun_tolerates_extra_space(self):
        self.assertIn("license plate",
                      rf_prompt_lint.find_prohibited_nouns("a license  plate"))

    def test_design_does_not_trigger_sign(self):
        self.assertEqual(rf_prompt_lint.find_prohibited_nouns("design language"), [])
        self.assertEqual(rf_prompt_lint.find_prohibited_nouns("designed assignment"), [])

    def test_shot_plan_and_art_style_are_also_noun_scanned(self):
        """KAPSAM: elle duzenlenen iki alan da yasakli nesneye karsi korunmali."""
        self.assertTrue(
            any(v["rule"] == "prohibited_noun"
                for v in rf_prompt_lint.lint_shot_plan(["Install a large display panel."])),
            "shot_plan yasakli nesne taramasi yapmiyor",
        )
        self.assertTrue(
            any(v["rule"] == "prohibited_noun"
                for v in rf_prompt_lint.lint_art_style("Style with a neon logo.")),
            "art_style yasakli nesne taramasi yapmiyor",
        )


class LiveSurfaceTests(unittest.TestCase):
    """Ucdan uca: canli dosyalarda uc statik yuzey SIFIR ihlal vermeli."""

    def test_lint_series_reports_zero_for_static_surfaces(self):
        violations = rf_prompt_lint.lint_series(SERIES_ROOT)
        static = [v for v in violations
                  if v["surface"] in ("art_style", "qc.notes", "shot_plan")]
        self.assertEqual(static, [], f"statik yuzeylerde ihlal var: {static}")

    def test_pending_plans_still_dirty_before_rock2(self):
        """ROCK 2 oncesi bekleyen planlar KIRLI olmali; temizse denetci korlesmis demektir."""
        violations = rf_prompt_lint.lint_series(SERIES_ROOT)
        pending = [v for v in violations if v["surface"] == "pending_plan"]
        self.assertTrue(pending, "bekleyen planlar temiz gorunuyor, denetci calismiyor olabilir")

    def test_live_shot_plan_is_six_lines_within_limit(self):
        series = json.loads((SERIES_ROOT / "series.json").read_text(encoding="utf-8"))
        lines = series["auto_replenish"]["shot_plan"]
        self.assertEqual(len(lines), 6)
        for i, line in enumerate(lines, 1):
            with self.subTest(shot=i):
                self.assertLessEqual(rf_prompt_lint.word_count(line), 45)

    def test_live_qc_notes_never_mentions_artifact(self):
        bible = json.loads((SERIES_ROOT / "bible.json").read_text(encoding="utf-8"))
        notes = bible["series"]["qc"]["notes"].lower()
        self.assertNotIn("artifact", notes)

    def test_live_art_style_dropped_hands_and_crews(self):
        bible = json.loads((SERIES_ROOT / "bible.json").read_text(encoding="utf-8"))
        art = bible["art_style"].lower()
        self.assertNotIn("crews", art)
        self.assertNotIn("skilled hands", art)


if __name__ == "__main__":
    unittest.main()
