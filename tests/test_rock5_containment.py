"""ROCK 5 bütçe adaleti ve çekim hata yalıtımı kanıtları, tamamen çevrimdışı."""

import contextlib
import pathlib
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

from series import critic, produce  # noqa: E402
from series.bible import Bible  # noqa: E402
from series.credit_gate import HardCreditCap  # noqa: E402


def make_bible(*, chain=False, max_per_shot=3, per_episode=None,
               require_all=False, hard_cap=False):
    qc = {
        "enabled": True,
        "max_regens_per_shot": max_per_shot,
        "qc_review_retries": 0,
        "require_all_shots": require_all,
    }
    if per_episode is not None:
        qc["max_regens_per_episode"] = per_episode
    return Bible({
        "series": {
            "slug": "rock5-test",
            "title": "Rock 5 Test",
            "aspect_ratio": "9:16",
            "resolution": "1080p",
            "engine": "seedance",
            "chain_frames": chain,
            "chain_scope": "episode",
            "credit_hard_cap": hard_cap,
            "qc": qc,
        },
        "art_style": "Photoreal.",
        "music": False,
        "characters": [],
        "environments": [],
        "props": [],
    })


def make_plan(count=4, *, chain=False, durations=None):
    durations = durations or ["10"] * count
    shots = []
    for index in range(count):
        shot = {
            "n": index + 1,
            "duration": durations[index],
            "prompt": f"Çekim {index + 1} için yeterince uzun çevrimdışı test promptu.",
        }
        if chain:
            shot["chain"] = index != 0
        shots.append(shot)
    return {
        "episode": {"number": 1, "title": "Containment"},
        "synopsis": "Tek bozuk çekim bölümü yok etmez.",
        "shots": shots,
    }


class OfflineEpisodeHarness:
    def __init__(self, bible, plan, review=None, qc_shot=None, cap=None):
        self.bible = bible
        self.plan = plan
        self.review = review
        self.qc_shot = qc_shot
        self.cap = cap
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tempdir.name)
        self.shot_dir = self.root / "shots"
        self.episode_dir = self.root / "episode"
        self.shot_dir.mkdir()
        self.episode_dir.mkdir()
        self.chain_inputs = {}
        self.generate_calls = []

    @staticmethod
    def _write_result(_url, target):
        pathlib.Path(target).write_bytes(b"video")
        return True

    @staticmethod
    def _write_video(_clips, target, **_kwargs):
        pathlib.Path(target).write_bytes(b"merged")

    @staticmethod
    def _final_export(_source, target):
        pathlib.Path(target).write_bytes(b"final")

    def _resolve(self, _bible, shot, chain_url=None):
        self.chain_inputs[shot["n"]] = chain_url
        return {
            "prompt": shot["prompt"],
            "start_image_url": chain_url,
            "duration": shot["duration"],
        }

    def _generate(self, engine, prompt, start_image_url, duration,
                  aspect_ratio, resolution, sound=True):
        self.generate_calls.append({
            "engine": engine,
            "prompt": prompt,
            "start_image_url": start_image_url,
            "duration": duration,
        })
        return {"url": f"offline://{len(self.generate_calls)}"}

    def run(self):
        meta = SimpleNamespace(
            slug=self.bible.slug,
            data={},
            auto_replenish={"credit_hard_cap": True} if self.cap else {},
        )
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch.object(produce.SeriesMeta, "load", return_value=meta))
            stack.enter_context(mock.patch.object(produce, "_doctrine_gate", return_value="digest"))
            stack.enter_context(mock.patch.object(produce.Bible, "load", return_value=self.bible))
            stack.enter_context(mock.patch.object(
                produce, "validate_plan", return_value={"warnings": [], "errors": []}
            ))
            stack.enter_context(mock.patch.object(produce, "_reserve_plan_music", return_value=None))
            stack.enter_context(mock.patch.object(produce, "shots_dir", return_value=self.shot_dir))
            stack.enter_context(mock.patch.object(produce, "episode_dir", return_value=self.episode_dir))
            stack.enter_context(mock.patch.object(produce, "check_credit"))
            stack.enter_context(mock.patch.object(produce, "resolve_visual_shot", side_effect=self._resolve))
            stack.enter_context(mock.patch.object(produce, "_generate_visual_clip", side_effect=self._generate))
            stack.enter_context(mock.patch.object(produce, "download_file", side_effect=self._write_result))
            stack.enter_context(mock.patch.object(critic, "download_file", side_effect=self._write_result))
            stack.enter_context(mock.patch.object(produce, "_prep_shot_clip", side_effect=lambda *a: a[3]))
            stack.enter_context(mock.patch.object(produce.ffmpeg_tools, "get_video_duration", return_value=1.0))
            stack.enter_context(mock.patch.object(
                produce.ffmpeg_tools, "concatenate_simple", side_effect=self._write_video
            ))
            stack.enter_context(mock.patch.object(
                produce.ffmpeg_tools, "final_export", side_effect=self._final_export
            ))
            stack.enter_context(mock.patch.object(
                produce, "_post_process", side_effect=lambda _b, _p, path, **_kw: path
            ))
            stack.enter_context(mock.patch.object(
                produce, "_upscale_master", side_effect=lambda _b, _n, path: path
            ))
            stack.enter_context(mock.patch.object(produce.report, "make_row", return_value={}))
            stack.enter_context(mock.patch.object(produce.report, "append_row"))
            stack.enter_context(mock.patch.object(produce.report, "export_xlsx"))
            stack.enter_context(mock.patch.object(
                produce.report, "summarize",
                return_value={"başarılı": 1, "çekim_sayısı": len(self.plan["shots"]),
                              "toplam_kredi": 0, "toplam_dolar": 0},
            ))
            stack.enter_context(mock.patch.object(produce.cost_tracker, "log_cost"))
            stack.enter_context(mock.patch.object(critic, "lint_prompt", return_value=[]))
            stack.enter_context(mock.patch.object(critic, "_log_event"))
            stack.enter_context(mock.patch.object(critic, "_notify"))
            if self.review is not None:
                stack.enter_context(mock.patch.object(
                    critic, "review_clip", side_effect=self.review
                ))
            if self.qc_shot is not None:
                stack.enter_context(mock.patch.object(
                    critic, "qc_shot", side_effect=self.qc_shot
                ))
            if self.cap is not None:
                stack.enter_context(mock.patch.object(
                    produce.credit_gate, "HardCreditCap", return_value=self.cap
                ))
            return produce.produce_episode(self.bible.slug, self.plan)

    def close(self):
        self.tempdir.cleanup()


class FairShareProofTests(unittest.TestCase):
    def test_p1_stubborn_first_shot_cannot_starve_later_shots(self):
        bible = make_bible(max_per_shot=3)
        budget = {"left": 4, "total": 4, "shot_count": 4}
        regen_counts = {n: 0 for n in range(1, 5)}

        def download(_url, target):
            pathlib.Path(target).write_bytes(b"regen")
            return True

        with tempfile.TemporaryDirectory() as temp_dir, \
                mock.patch.object(
                    critic, "review_clip",
                    return_value=({"fix_notes": ["artifact"]}, "fail", ["artifact"], []),
                ), mock.patch.object(critic, "download_file", side_effect=download), \
                mock.patch.object(critic, "_log_event"), \
                mock.patch.object(critic, "_notify"):
            for n in range(1, 5):
                clip = pathlib.Path(temp_dir) / f"shot_{n:02d}.mp4"
                clip.write_bytes(b"bad")

                def regen(_prompt, shot_n=n):
                    regen_counts[shot_n] += 1
                    return {"url": f"offline://regen/{shot_n}"}

                path, _credits, status = critic.qc_shot(
                    bible, {"n": n}, clip, "prompt", regen,
                    episode=1, budget=budget,
                )
                self.assertIsNone(path)
                self.assertEqual(status, "fail")

        self.assertEqual(regen_counts, {1: 1, 2: 1, 3: 1, 4: 1})
        self.assertEqual(budget["left"], 0)

    def test_plain_left_only_budget_keeps_legacy_per_shot_behavior(self):
        bible = make_bible(max_per_shot=2)
        budget = {"left": 2}
        clip_dir = tempfile.TemporaryDirectory()
        self.addCleanup(clip_dir.cleanup)
        clip = pathlib.Path(clip_dir.name) / "shot.mp4"
        clip.write_bytes(b"bad")
        regen = mock.Mock(return_value={"url": "offline://regen"})

        def download(_url, target):
            pathlib.Path(target).write_bytes(b"regen")
            return True

        with mock.patch.object(
                critic, "review_clip",
                return_value=({"fix_notes": ["artifact"]}, "fail", ["artifact"], [])), \
                mock.patch.object(critic, "download_file", side_effect=download), \
                mock.patch.object(critic, "_log_event"), \
                mock.patch.object(critic, "_notify"):
            result = critic.qc_shot(
                bible, {"n": 1}, clip, "prompt", regen, episode=1, budget=budget
            )

        self.assertEqual(result[2], "fail")
        self.assertEqual(regen.call_count, 2)


class EpisodeContainmentProofTests(unittest.TestCase):
    def run_harness(self, bible, plan, **kwargs):
        harness = OfflineEpisodeHarness(bible, plan, **kwargs)
        self.addCleanup(harness.close)
        return harness, harness.run()

    def test_p2_episode_survives_one_drop_and_later_shots_pass(self):
        calls = {n: 0 for n in range(1, 5)}

        def review(_bible, shot, _clip, _prompt, _qc):
            calls[shot["n"]] += 1
            if shot["n"] == 1 or (shot["n"] in (2, 3) and calls[shot["n"]] == 1):
                return {"fix_notes": ["artifact"]}, "fail", ["artifact"], []
            return {"artifact_score": 0}, "pass", [], []

        harness, result = self.run_harness(
            make_bible(require_all=False), make_plan(), review=review
        )

        self.assertIsNotNone(result)
        self.assertTrue(result.exists())
        self.assertEqual(calls, {1: 2, 2: 2, 3: 2, 4: 1})
        self.assertEqual(len(harness.generate_calls), 7)

    def test_p3_dropped_shot_breaks_chain_and_next_shot_has_no_start_frame(self):
        calls = {1: 0, 2: 0}

        def review(_bible, shot, _clip, _prompt, _qc):
            calls[shot["n"]] += 1
            if shot["n"] == 1:
                return {"fix_notes": ["artifact"]}, "fail", ["artifact"], []
            return {"artifact_score": 0}, "pass", [], []

        bible = make_bible(chain=True, require_all=False)
        harness = OfflineEpisodeHarness(bible, make_plan(2, chain=True), review=review)
        self.addCleanup(harness.close)
        with self.assertLogs(produce.logger, level="WARNING") as logs:
            result = harness.run()

        self.assertIsNotNone(result)
        self.assertIsNone(harness.chain_inputs[2])
        shot2_main = [call for call in harness.generate_calls if call["prompt"].startswith("Çekim 2")]
        self.assertEqual(len(shot2_main), 1)
        self.assertIsNone(shot2_main[0]["start_image_url"])
        self.assertTrue(any(
            "önceki çekim düştüğü için son kare yok" in line and "başlangıç karesiz" in line
            for line in logs.output
        ))

    def test_p4_genuine_missing_initial_chain_frame_is_still_fatal(self):
        bible = make_bible(chain=True)
        plan = make_plan(2, chain=True)
        plan["shots"][0]["chain"] = True
        harness = OfflineEpisodeHarness(bible, plan)
        self.addCleanup(harness.close)

        with self.assertLogs(produce.logger, level="ERROR") as logs:
            result = harness.run()

        self.assertIsNone(result)
        self.assertEqual(harness.generate_calls, [])
        self.assertTrue(any("chain=true fakat önceki son kare yok" in line for line in logs.output))

        disabled_bible = make_bible(chain=False)
        disabled_plan = make_plan(1)
        disabled_plan["shots"][0]["chain"] = True
        disabled = OfflineEpisodeHarness(disabled_bible, disabled_plan)
        self.addCleanup(disabled.close)
        with self.assertLogs(produce.logger, level="ERROR") as disabled_logs:
            disabled_result = disabled.run()
        self.assertIsNone(disabled_result)
        self.assertEqual(disabled.generate_calls, [])
        self.assertTrue(any(
            "chain=true için bible.series.chain_frames=true olmalı" in line
            for line in disabled_logs.output
        ))

    def test_p5_optional_qc_refusal_does_not_abort_later_mandatory_shot(self):
        cap = HardCreditCap(115, 0)

        def review(_bible, shot, _clip, _prompt, _qc):
            if shot["n"] == 1:
                return {"fix_notes": ["artifact"]}, "fail", ["artifact"], []
            return {"artifact_score": 0}, "pass", [], []

        harness, result = self.run_harness(
            make_bible(hard_cap=True),
            make_plan(2, durations=["10", "4"]),
            review=review,
            cap=cap,
        )

        self.assertIsNotNone(result)
        self.assertFalse(cap.blocked)
        self.assertEqual(cap.spent, 115)
        self.assertEqual([item["call_type"] for item in cap.reservations],
                         ["main_shot", "main_shot"])
        self.assertEqual(len(harness.generate_calls), 2)

        mandatory_main = HardCreditCap(74, 0)
        self.assertFalse(mandatory_main.authorize("main_shot", "seedance", "10"))
        self.assertTrue(mandatory_main.blocked)
        mandatory_music = HardCreditCap(79, 0)
        self.assertFalse(mandatory_music.authorize("music", "suno"))
        self.assertTrue(mandatory_music.blocked)

    def test_p6_default_budget_is_shot_count_and_explicit_value_wins(self):
        def capture_run(per_episode):
            seen = []

            def qc_pass(_bible, _shot, clip, _prompt, _regen, episode, budget):
                seen.append(dict(budget))
                return pathlib.Path(clip), 0.0, "pass"

            bible = make_bible(per_episode=per_episode)
            harness, result = self.run_harness(
                bible, make_plan(5), qc_shot=qc_pass
            )
            self.assertIsNotNone(result)
            self.assertEqual(len(harness.generate_calls), 5)
            return seen[0]

        default_seen = capture_run(None)
        explicit_seen = capture_run(2)
        self.assertEqual(default_seen, {"left": 5, "total": 5, "shot_count": 5})
        self.assertEqual(explicit_seen, {"left": 2, "total": 2, "shot_count": 5})


if __name__ == "__main__":
    unittest.main()
