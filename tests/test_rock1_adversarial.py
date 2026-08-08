"""ROCK 1 bagimsiz nobetci testleri (Visionary, Codex suitinin disindaki vakalar).

Codex'in test_rock1_budget_and_qcskip.py suiti T1-T7'yi kapsar. Bu dosya onun
KACIRDIGI vakalari tutar: retry opt-out, retry'de ortaya cikan gercek RED, regen
sonrasi klibin retry korumasi, bozuk ayar, gercek from-scratch bible'i ve
tek-ucret garantisinin fiilen tasiyici oldugu.
"""

import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

from series import critic, produce            # noqa: E402
from series.bible import Bible                # noqa: E402
from series.credit_gate import HardCreditCap  # noqa: E402


def qc_bible(*, require_all=True, retries=None, music=False):
    qc = {"enabled": True, "require_all_shots": require_all, "max_regens_per_shot": 2}
    if retries is not None:
        qc["qc_review_retries"] = retries
    return Bible({
        "series": {"slug": "adv-test", "title": "Adv", "aspect_ratio": "9:16",
                   "resolution": "1080p", "engine": "omni", "chain_frames": False,
                   "qc": qc},
        "art_style": "Photoreal.", "music": music,
        "characters": [], "environments": [], "props": [],
    })


class RetryContract(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.clip = pathlib.Path(self.td.name) / "shot_01.mp4"
        self.clip.write_bytes(b"clip")

    def run_qc(self, bible, reviews, *, budget=3, regen=None):
        kw = {"side_effect": reviews} if isinstance(reviews, list) else {"return_value": reviews}
        with mock.patch.object(critic, "review_clip", **kw) as review, \
                mock.patch.object(critic.time, "sleep") as sleep, \
                mock.patch.object(critic, "_log_event"), \
                mock.patch.object(critic, "_notify"):
            out = critic.qc_shot(bible, {"n": 1}, self.clip, "prompt", regen,
                                 episode=1, budget={"left": budget})
        return out, review, sleep

    # A1 ,  retries=0 opt-out: tek denetim, uyku yok, skip yine kabul
    def test_a1_retries_zero_is_a_real_optout(self):
        b = qc_bible(retries=0)
        (path, _c, status), review, sleep = self.run_qc(
            b, (None, "skip", ["cevrimdisi"], []))
        self.assertEqual(review.call_count, 1, "retries=0 iken tek denetim olmali")
        sleep.assert_not_called()
        self.assertEqual((path, status), (self.clip, "skip"))
        self.assertTrue(self.clip.exists())

    # A2 ,  yeniden denetim GERCEK RED ortaya cikarirsa skip diye yutulmamali
    def test_a2_retry_revealing_fail_goes_down_red_path(self):
        b = qc_bible(retries=2)
        regen = mock.Mock(return_value=None)   # regen yok -> final_reject
        (path, _c, status), review, _s = self.run_qc(
            b,
            [(None, "skip", ["gecici"], []),
             ({"fix_notes": ["anatomi"]}, "fail", ["anatomi"], [])],
            budget=0, regen=regen)
        self.assertEqual(review.call_count, 2)
        self.assertEqual(status, "fail", "retry'de cikan gercek RED kabul edilemez")
        self.assertIsNone(path)
        self.assertFalse(self.clip.exists())

    # A3 ,  regen SONRASI klip de skip donerse retry dongusu orada da calismali
    def test_a3_retry_loop_also_guards_the_regenerated_clip(self):
        b = qc_bible(retries=2)

        def download(_url, target):
            pathlib.Path(target).write_bytes(b"regen")
            return True

        reviews = [
            ({"fix_notes": ["anatomi"]}, "fail", ["anatomi"], []),   # ilk uretim RED
            (None, "skip", ["gecici"], []),                          # regen sonrasi skip
            (None, "skip", ["gecici"], []),                          # retry 1
            (None, "skip", ["gecici"], []),                          # retry 2
        ]
        with mock.patch.object(critic, "review_clip", side_effect=reviews) as review, \
                mock.patch.object(critic, "download_file", side_effect=download), \
                mock.patch.object(critic.time, "sleep"), \
                mock.patch.object(critic, "_log_event"), \
                mock.patch.object(critic, "_notify"):
            path, credits, status = critic.qc_shot(
                b, {"n": 1}, self.clip, "prompt",
                lambda _p: {"url": "regen", "credits": 200},
                episode=1, budget={"left": 3})
        self.assertEqual(review.call_count, 4, "regen sonrasi da 1+2 denetim beklenir")
        self.assertEqual(status, "skip")
        self.assertIsNotNone(path, "denetlenemeyen regen klibi de kabul edilmeli")
        self.assertEqual(credits, 200.0)

    # A4 ,  bozuk ayar cokmemeli
    def test_a4_garbage_retry_setting_does_not_crash(self):
        for bad in (-5, "3", 0):
            with self.subTest(bad=bad):
                b = qc_bible(retries=bad)
                (path, _c, status), review, _s = self.run_qc(
                    b, (None, "skip", ["x"], []))
                self.assertEqual(status, "skip")
                self.assertIsNotNone(path)
                self.assertGreaterEqual(review.call_count, 1)


class RealSeriesContract(unittest.TestCase):
    # A5 ,  GERCEK from-scratch bible'i retry ayarini fiilen aliyor mu
    def test_a5_real_from_scratch_bible_has_retries_and_require_all(self):
        b = Bible.load("from-scratch")
        qc = critic.qc_config(b)
        self.assertTrue(qc, "from-scratch'te QC acik olmali")
        self.assertEqual(qc["qc_review_retries"], 2)
        # KARAR-2 (Ihsan, 2026-08-08): kurulu deger artik False. Iddia zayiflamiyor, yeni
        # dogru degere civileniyor, biri yanlislikla geri acarsa bu test duser.
        self.assertFalse(qc.get("require_all_shots"))

    # A6 ,  cift ucretlendirme GERCEKTEN tavani patlatir (tek-ucret yuku tasiyici mi)
    def test_a6_double_charging_music_would_actually_blow_the_cap(self):
        plan = json.loads(
            (ROOT / "aimagine" / "from-scratch" / "plans" / "part06.json")
            .read_text(encoding="utf-8"))
        cap = HardCreditCap(1900, 0)
        ok = [cap.authorize("music", "suno")]
        ok += [cap.authorize("main_shot", "omni", s["duration"]) for s in plan["shots"]]
        ok += [cap.authorize("qc_regen", "omni", "10") for _ in range(3)]
        self.assertTrue(all(ok))
        self.assertEqual(cap.spent, 1880)
        # ikinci muzik ucreti (regresyon senaryosu) tavani asmali
        self.assertFalse(cap.authorize("music", "suno"),
                         "1880+80=1960 > 1900 olmali; tek-ucret garantisi tasiyici")

    # A7 ,  seri duzeyinde muzik kapaliysa plan muzik tasisa bile rezervasyon olmaz
    def test_a7_series_music_off_means_no_reservation(self):
        b = qc_bible(music=False)
        cap = HardCreditCap(1900, 0)
        with mock.patch.object(produce.cost_tracker, "log_cost") as log_cost:
            reserved = produce._reserve_plan_music(
                b, {"episode": {"number": 6}, "music": "score"}, cap, 6)
        self.assertIsNone(reserved)
        self.assertEqual(cap.spent, 0)
        log_cost.assert_not_called()


if __name__ == "__main__":
    unittest.main()
