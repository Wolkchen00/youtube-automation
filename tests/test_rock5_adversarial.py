"""ROCK 5 bagimsiz nobetci testleri (Visionary).

Bugun canli kosu 31204975714'te gorulen ariza birebir taklit edilir: 4 cekimlik
bolumde inatci cekim 1, bolum regen butcesinin TAMAMINI yiyip cekim 2-3-4'u sifir
hakla birakti ve bolum "hic cekim uretilemedi" ile oldu. Ek olarak geri-uyumluluk,
adil pay tabani ve sert tavan zehirleme asimetrisi denetlenir.
"""

import pathlib
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from series import critic                      # noqa: E402
from series.bible import Bible                 # noqa: E402
from series.credit_gate import HardCreditCap   # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")


def qc_bible(max_per_shot=2):
    return Bible({
        "series": {"slug": "adv5", "title": "Adv5", "aspect_ratio": "9:16",
                   "resolution": "1080p", "engine": "omni", "chain_frames": False,
                   "qc": {"enabled": True, "max_regens_per_shot": max_per_shot,
                          "qc_review_retries": 0}},
        "art_style": "Photoreal.", "music": False,
        "characters": [], "environments": [], "props": [],
    })


class FairShare(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)

    def stubborn_shot(self, n, budget, bible):
        """Hep RED donen bir cekim; kac regen harcadigini dondurur."""
        clip = pathlib.Path(self.td.name) / f"shot_{n:02d}.mp4"
        clip.write_bytes(b"clip")
        calls = {"regen": 0}

        def regen(_prompt):
            calls["regen"] += 1
            return {"url": "u", "credits": 84}

        def download(_url, target):
            pathlib.Path(target).write_bytes(b"regen")
            return True

        with mock.patch.object(critic, "review_clip",
                               return_value=({"fix_notes": ["x"]}, "fail", ["kotu"], [])), \
                mock.patch.object(critic, "download_file", side_effect=download), \
                mock.patch.object(critic, "_log_event"), \
                mock.patch.object(critic, "_notify"), \
                mock.patch.object(critic.time, "sleep"):
            path, _cr, status = critic.qc_shot(bible, {"n": n}, clip, "p", regen,
                                               episode=1, budget=budget)
        return calls["regen"], path, status

    # C1 ,  BUGUNKU ARIZANIN BIREBIR TEKRARI (unnatural-lab sekli)
    def test_c1_stubborn_first_shot_cannot_starve_the_others(self):
        bible = qc_bible(max_per_shot=2)
        budget = {"left": 4, "total": 4, "shot_count": 4}
        used = []
        for n in (1, 2, 3, 4):
            r, path, status = self.stubborn_shot(n, budget, bible)
            used.append(r)
            self.assertIsNone(path)
            self.assertEqual(status, "fail")
        # Adil pay = max(1, 4//4) = 1 -> her cekim TAM 1 regen alir
        self.assertEqual(used, [1, 1, 1, 1],
                         f"cekim basina regen dagilimi adil degil: {used}")
        self.assertEqual(budget["left"], 0)

    # C1b ,  ESKI DAVRANIS bu testte kirilirdi (regresyon nobetcisi)
    def test_c1b_old_shared_pool_would_have_starved_shots(self):
        bible = qc_bible(max_per_shot=2)
        eski = {"left": 2}          # total/shot_count YOK -> eski davranis
        r1, _p, _s = self.stubborn_shot(1, eski, bible)
        self.assertEqual(r1, 2, "geri uyumlulukta cekim 1 hala 2 regen alabilmeli")
        r2, _p, _s = self.stubborn_shot(2, eski, bible)
        self.assertEqual(r2, 0, "eski davranista cekim 2 ac kalirdi (kanit)")

    # C2 ,  adil pay TABANI: butce cekim sayisindan kucukse bile en az 1
    def test_c2_fair_share_floor_is_one(self):
        bible = qc_bible(max_per_shot=2)
        budget = {"left": 2, "total": 2, "shot_count": 6}   # 2//6 = 0
        r1, _p, _s = self.stubborn_shot(1, budget, bible)
        self.assertEqual(r1, 1, "taban 1 olmali, 0 degil")
        r2, _p, _s = self.stubborn_shot(2, budget, bible)
        self.assertEqual(r2, 1)
        r3, _p, _s = self.stubborn_shot(3, budget, bible)
        self.assertEqual(r3, 0, "havuz bitince regen olmamali")

    # C3 ,  bozuk/eksik ek alanlar cokmemeli
    def test_c3_garbage_budget_fields_degrade_safely(self):
        bible = qc_bible(max_per_shot=2)
        for bad in ({"left": 3, "total": "x", "shot_count": 4},
                    {"left": 3, "total": 4, "shot_count": 0},
                    {"left": 3, "total": None, "shot_count": None}):
            with self.subTest(bad=bad):
                r, _p, status = self.stubborn_shot(1, dict(bad), bible)
                self.assertEqual(status, "fail")
                self.assertLessEqual(r, 2)


class CapPoisoning(unittest.TestCase):
    # C4 ,  istege bagli ret zehirlemez, zorunlu ret zehirler
    def test_c4_optional_refusal_does_not_poison_the_cap(self):
        cap = HardCreditCap(100, 0)
        self.assertFalse(cap.authorize("qc_regen", "omni", "10", optional=True))
        self.assertFalse(cap.blocked, "istege bagli ret sert tavani zehirlememeli")
        self.assertIsNone(cap.blocked_reason)
        # ayni tavan hala kullanilabilir olmali
        self.assertTrue(cap.authorize("music", "suno"))

        cap2 = HardCreditCap(100, 0)
        self.assertFalse(cap2.authorize("main_shot", "omni", "10"))
        self.assertTrue(cap2.blocked, "zorunlu ret tavani zehirlemeli")
        self.assertIn("sert tavan", cap2.blocked_reason)

    # C5 ,  istege bagli ret rezervasyon da yazmamali
    def test_c5_optional_refusal_reserves_nothing(self):
        cap = HardCreditCap(100, 0)
        before = list(cap.reservations)
        cap.authorize("qc_regen", "omni", "10", optional=True)
        self.assertEqual(cap.reservations, before)
        self.assertEqual(cap.spent, 0)


if __name__ == "__main__":
    unittest.main()
