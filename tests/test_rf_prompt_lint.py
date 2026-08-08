"""FROM SCRATCH prompt denetcisi icin agsiz regresyon testleri."""

import json
import pathlib
import sys
import unittest


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from tools import rf_prompt_lint


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SERIES_ROOT = REPO_ROOT / "aimagine" / "from-scratch"
OLD_ART_STYLE = (
    "Photoreal construction timelapse realism in vertical 9:16, bright daylight, saturated "
    "but believable color, tactile real materials, coherent site geography, skilled hands "
    "and crews in safe working conditions, and satisfying build progression. LOCKED-OFF "
    "TRIPOD camera: the exact same fixed camera position and angle, only slow zoom allowed. "
    "One recurring silent builder in a dark cap, dark crew-neck and work gloves, seen from "
    "behind or mid-distance, face never in close-up. No CGI sheen, no text, no logos, no "
    "watermarks."
)
OLD_QC_NOTES = (
    "Exactly one structure and one final reveal are allowed. Any locked-camera drift, change "
    "in the recurring USTA's dark cap, dark crew-neck, work gloves, or established appearance, "
    "break in the structure's material or design language, or composition-lock violation "
    "within a chained shot is an artifact."
)


class RfPromptLintTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bible = json.loads((SERIES_ROOT / "bible.json").read_text(encoding="utf-8"))
        cls.series = json.loads((SERIES_ROOT / "series.json").read_text(encoding="utf-8"))

    def test_old_art_style_fails_and_new_value_passes(self):
        self.assertTrue(rf_prompt_lint.lint_art_style(OLD_ART_STYLE))
        self.assertEqual(
            rf_prompt_lint.lint_art_style(self.bible["art_style"]),
            [],
        )

    def test_stale_part08_shot4_fixture_fails_for_display(self):
        plan = {"shots": [{
            "n": 4,
            "prompt": "Install holographic display systems across the curved interior wall.",
        }]}
        violations = rf_prompt_lint.lint_plan_data(
            plan,
            self.bible["art_style"],
            self.series["auto_replenish"]["shot_plan"],
            "part08.json",
        )
        matches = [
            item for item in violations
            if item["rule"] == "prohibited_noun"
            and item["shot"] == 4
            and "display" in item["detail"]
        ]
        self.assertTrue(matches)

    def test_stale_part06_fixture_fails_for_prefix_repetition(self):
        prefix = self.series["auto_replenish"]["shot_plan"][0]
        plan = {"shots": [{"n": 1, "prompt": f"{prefix}\n\n{prefix}"}]}
        violations = rf_prompt_lint.lint_plan_data(
            plan,
            self.bible["art_style"],
            self.series["auto_replenish"]["shot_plan"],
            "part06.json",
        )
        self.assertTrue(any(item["rule"] == "repetition" for item in violations))

    def test_old_qc_notes_fail_and_new_value_passes(self):
        self.assertTrue(rf_prompt_lint.lint_qc_notes(OLD_QC_NOTES))
        notes = self.bible["series"]["qc"]["notes"]
        self.assertEqual(rf_prompt_lint.lint_qc_notes(notes), [])

    def test_canonical_nouns_match_brief_item_7_exactly(self):
        brief = self.series["auto_replenish"]["brief"]
        marker = "doğururlar: "
        self.assertIn(
            marker,
            brief,
            "Brief madde (7) yasaklı nesne başlangıcı 'doğururlar: ' bulunamadı",
        )
        noun_text = brief.split(marker, 1)[1].split(". Yerine:", 1)[0]
        brief_nouns = tuple(item.strip() for item in noun_text.split(","))
        self.assertEqual(rf_prompt_lint.PROHIBITED_NOUNS, brief_nouns)

    def test_false_positive_traps_pass(self):
        for text in ("north", "nozzle", "design language", "nothing"):
            with self.subTest(text=text):
                self.assertEqual(rf_prompt_lint.find_negations(text), [])
                self.assertEqual(rf_prompt_lint.find_prohibited_nouns(text), [])

    def test_signage_free_is_caught(self):
        self.assertIn("-free", rf_prompt_lint.find_negations("signage-free surfaces"))

    def test_replaced_static_surfaces_have_zero_violations(self):
        shot_plan = self.series["auto_replenish"]["shot_plan"]
        self.assertEqual(rf_prompt_lint.lint_art_style(self.bible["art_style"]), [])
        self.assertEqual(
            rf_prompt_lint.lint_qc_notes(self.bible["series"]["qc"]["notes"]),
            [],
        )
        self.assertEqual(rf_prompt_lint.lint_shot_plan(shot_plan), [])


if __name__ == "__main__":
    unittest.main()
