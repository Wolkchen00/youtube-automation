"""ROCK 1 bütçe ve QC skip kanıtları, tamamen çevrimdışı."""

import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core import music_generator
from series import critic, produce
from series.bible import Bible
from series.credit_gate import HardCreditCap


sys.stdout.reconfigure(encoding="utf-8")
REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
PART06 = REPO_ROOT / "aimagine" / "from-scratch" / "plans" / "part06.json"


def qc_bible(*, require_all=True, retries=None):
    qc = {"enabled": True, "require_all_shots": require_all,
          "max_regens_per_shot": 2}
    if retries is not None:
        qc["qc_review_retries"] = retries
    return Bible({
        "series": {
            "slug": "rock1-test",
            "title": "Rock 1 Test",
            "aspect_ratio": "9:16",
            "resolution": "1080p",
            "engine": "omni",
            "chain_frames": False,
            "qc": qc,
        },
        "art_style": "Photoreal.",
        "music": False,
        "characters": [],
        "environments": [],
        "props": [],
    })


class BudgetProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads(PART06.read_text(encoding="utf-8"))

    @staticmethod
    def run_budget(cap_value):
        cap = HardCreditCap(cap_value, 0)
        allowed = [cap.authorize("music", "suno")]
        allowed.extend(
            cap.authorize("main_shot", "omni", shot["duration"])
            for shot in BudgetProofTests.plan["shots"]
        )
        allowed.extend(cap.authorize("qc_regen", "omni", "10") for _ in range(3))
        return cap, allowed

    def test_t1_real_plan_fits_1900_in_required_order(self):
        cap, allowed = self.run_budget(1900)
        self.assertTrue(all(allowed))
        self.assertEqual(cap.spent, 1880)
        self.assertEqual(
            [item["call_type"] for item in cap.reservations],
            ["music"] + ["main_shot"] * 6 + ["qc_regen"] * 3,
        )

    def test_t2_same_plan_is_blocked_at_1400(self):
        cap, allowed = self.run_budget(1400)
        self.assertFalse(all(allowed))
        self.assertTrue(cap.blocked)
        self.assertIn("sert tavan aşımı", cap.blocked_reason)

    def test_t3_pre_reserved_music_is_charged_exactly_once(self):
        bible = qc_bible()
        bible.data["music"] = True
        plan = {"episode": {"number": 6, "title": "Arcade"},
                "music": "custom score"}
        cap = HardCreditCap(1900, 0)
        with tempfile.TemporaryDirectory() as temp_dir:
            video = pathlib.Path(temp_dir) / "video.mp4"
            audio = pathlib.Path(temp_dir) / "music.mp3"
            video.write_bytes(b"video")
            audio.write_bytes(b"music")

            def mix(_video, _music, target, **_kwargs):
                pathlib.Path(target).write_bytes(b"mixed")

            with mock.patch.object(produce.cost_tracker, "log_cost") as log_cost, \
                    mock.patch.object(
                        music_generator, "generate_background_music", return_value=audio
                    ), mock.patch.object(
                        produce.ffmpeg_tools, "mix_background_music", side_effect=mix
                    ):
                reserved = produce._reserve_plan_music(bible, plan, cap, 6)
                result = produce._post_process(
                    bible, plan, video, hard_cap=cap, required_music=True,
                    music_reserved=reserved is True,
                )

        self.assertIsNotNone(result)
        self.assertEqual(cap.spent, 80)
        self.assertEqual(len(cap.reservations), 1)
        self.assertEqual(log_cost.call_count, 1)

    def test_t4_musicless_plan_makes_no_music_reservation(self):
        bible = qc_bible()
        bible.data["music"] = True
        cap = HardCreditCap(1900, 0)
        with mock.patch.object(produce.cost_tracker, "log_cost") as log_cost:
            reserved = produce._reserve_plan_music(
                bible, {"episode": {"number": 1}}, cap, 1
            )
        self.assertIsNone(reserved)
        self.assertEqual(cap.spent, 0)
        self.assertEqual(cap.reservations, [])
        log_cost.assert_not_called()


class QCSkipProofTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.clip = pathlib.Path(self.tempdir.name) / "shot_01.mp4"
        self.clip.write_bytes(b"clip")
        self.bible = qc_bible()

    def test_t5_skip_then_pass_uses_clip_without_regen(self):
        budget = {"left": 3}
        regen = mock.Mock()
        reviews = [
            (None, "skip", ["geçici hata"], []),
            ({"artifact_score": 0}, "pass", [], []),
        ]
        with mock.patch.object(critic, "review_clip", side_effect=reviews) as review, \
                mock.patch.object(critic.time, "sleep") as sleep, \
                mock.patch.object(critic, "_log_event"), \
                mock.patch.object(critic, "_notify"):
            path, credits, status = critic.qc_shot(
                self.bible, {"n": 1}, self.clip, "prompt", regen,
                episode=1, budget=budget,
            )
        self.assertEqual((path, credits, status), (self.clip, 0.0, "pass"))
        self.assertEqual(review.call_count, 2)
        sleep.assert_called_once()
        regen.assert_not_called()
        self.assertEqual(budget["left"], 3)

    def test_t6_exhausted_skips_are_accepted_under_require_all(self):
        budget = {"left": 3}
        regen = mock.Mock()
        skipped = (None, "skip", ["Gemini çevrimdışı"], [])
        with mock.patch.object(critic, "review_clip", return_value=skipped) as review, \
                mock.patch.object(critic.time, "sleep"), \
                mock.patch.object(critic, "_log_event") as log_event, \
                mock.patch.object(critic, "_notify") as notify:
            path, credits, status = critic.qc_shot(
                self.bible, {"n": 1}, self.clip, "prompt", regen,
                episode=1, budget=budget,
            )
        self.assertEqual(critic.qc_config(self.bible)["qc_review_retries"], 2)
        self.assertEqual(review.call_count, 3)
        self.assertEqual((path, credits, status), (self.clip, 0.0, "skip"))
        self.assertTrue(self.clip.exists())
        regen.assert_not_called()
        self.assertEqual(budget["left"], 3)
        self.assertTrue(any(
            call.args[1].get("event") == "qc_skip_accepted"
            for call in log_event.call_args_list
        ))
        notify.assert_called_once()

    def test_t7_persistent_fail_still_drops_rejected_clip(self):
        budget = {"left": 1}
        reviews = [
            ({"fix_notes": ["anatomi"]}, "fail", ["anatomi bozuk"], []),
            ({"fix_notes": ["anatomi"]}, "fail", ["anatomi bozuk"], []),
        ]

        def download(_url, target):
            pathlib.Path(target).write_bytes(b"regen")
            return True

        with mock.patch.object(critic, "review_clip", side_effect=reviews), \
                mock.patch.object(critic, "download_file", side_effect=download), \
                mock.patch.object(critic, "_log_event") as log_event, \
                mock.patch.object(critic, "_notify"):
            path, credits, status = critic.qc_shot(
                self.bible, {"n": 1}, self.clip, "prompt",
                lambda _prompt: {"url": "regen", "credits": 200},
                episode=1, budget=budget,
            )
        self.assertEqual((path, credits, status), (None, 200.0, "fail"))
        self.assertEqual(budget["left"], 0)
        self.assertFalse(self.clip.exists())
        self.assertEqual(len(list(self.clip.parent.glob("shot_01_qcfail*.mp4"))), 2)
        self.assertTrue(any(
            call.args[1].get("event") == "final_reject"
            for call in log_event.call_args_list
        ))


if __name__ == "__main__":
    unittest.main()
