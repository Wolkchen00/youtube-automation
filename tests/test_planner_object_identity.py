"""Planlayici kurali: descriptor ile anomaly_descriptor ayni obje durumunu tarif eder.

part23 (sabun) uc kez ust uste dustu; QC her seferinde "obje referansla ayni fiziksel
obje degil" dedi. Sebep hero referans prompt'unun KENDI ICINDE celismesiydi: kimlik
"smooth rounded edges", anomali "sharp conchoidal fracture edges and glossy shards".
Gorsel model ikisini birden cizemez.

Calisan karsit ornek part22: descriptor'u objeyi ZATEN anomali-aktif haliyle tarif
ediyor ("split into two matching halves, ... revealing a tiny ancient stone spiral
staircase descending inside") ve bolum pilot-1'de gecti.
"""

import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from series import replenish
from series.bible import Bible
from series.series_meta import SeriesMeta

REPO = pathlib.Path(__file__).resolve().parents[1]
GOLDEN = REPO / "tests" / "golden" / "fixedframe_prompts.json"
KURAL = "OBJECT IDENTITY AND ANOMALY MUST AGREE"


class PlannerRuleTests(unittest.TestCase):
    def test_kural_uretilen_talimatta_var(self):
        meta = SeriesMeta.load("unnatural-lab")
        bible = Bible.load("unnatural-lab")
        _contents, system = replenish._build_prompt(
            meta, bible, meta.auto_replenish, 1, 1, []
        )
        self.assertIn(KURAL, system)
        # E3'un shot-1 kurali kaybolmamis olmali.
        self.assertIn("SHOT 1 ONSET", system)

    def test_kural_her_iki_dalda_da_tanimli(self):
        """Kaynakta iki obje-planlama dali var; biri unutulursa sessizce bozulur."""
        kaynak = (REPO / "series" / "replenish.py").read_text(encoding="utf-8")
        self.assertEqual(kaynak.count(KURAL), 2)

    def test_diger_serilerin_planlayici_prompt_u_degismedi(self):
        """P9: opt-in olmayan seriler bu degisiklikten ETKILENMEZ."""
        golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
        for slug, beklenen in golden.items():
            if slug == "unnatural-lab":
                continue
            with self.subTest(slug=slug):
                self.assertNotIn(KURAL, beklenen["system_instruction"])

    def test_calisan_ornek_part22_kurala_uyuyor(self):
        """Regresyon capasi: gecen bolumun descriptor'u anomalisiyle celismiyor."""
        plan = json.loads(
            (REPO / "sentinal_ihsan/unnatural-lab/plans/part22.json").read_text(
                encoding="utf-8"
            )
        )
        kart = plan["object_card"]
        # Anomali objenin icini tarif ediyor ve descriptor onu ZATEN iceriyor.
        self.assertIn("staircase", kart["descriptor"])
        self.assertIn("stair", kart["anomaly_descriptor"])


if __name__ == "__main__":
    unittest.main()
