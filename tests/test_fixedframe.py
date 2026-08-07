"""Rock 1 fixed-frame engine proof matrix (fully offline, plain unittest)."""

import contextlib
import copy
import hashlib
import io
import json
import os
import pathlib
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core import cost_tracker, music_generator
from series import bible as bible_module
from series import critic, preflight, produce, replenish, series_runner
from series.bible import Bible
from series.credit_gate import HardCreditCap
from series.series_meta import SeriesMeta


sys.stdout.reconfigure(encoding="utf-8")
REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
GOLDEN = REPO_ROOT / "tests" / "golden" / "fixedframe_prompts.json"
FIXEDFRAME_AUTO_OPT_IN_KEYS = frozenset({
    "chain_breaks", "hook_shot", "shot_plan", "title_patterns", "credit_hard_cap",
})
REQUIRED_KEYLESS_GOLDEN_SERIES = frozenset({
    "could-you-survive",
    "drowned-history",
    "event-horizon",
    "flashpoints",
    "footnotes",
    "night-archive",
    "the-drift",
    "the-vast",
    "time-witness",
    "unnatural-lab",
})
ROCK2_EXPECTED_OPT_IN_SERIES = frozenset({"from-scratch"})
FROM_SCRATCH_ROCK2_AUTO_KEYS = frozenset({
    "chain_breaks", "hook_shot", "shot_plan", "title_patterns", "credit_hard_cap",
})


def bible_data(slug="fixed-test", *, chain=True, require_all=False,
               required_layers=None, music=False, hook=False, engine="seedance"):
    return {
        "series": {
            "slug": slug,
            "title": slug,
            "aspect_ratio": "9:16",
            "resolution": "1080p",
            "engine": engine,
            "chain_frames": chain,
            "chain_scope": "episode",
            "native_audio": False,
            "qc": {"enabled": False, "require_all_shots": require_all},
            "required_layers": list(required_layers or []),
            "hook_teaser": (
                {"enabled": True, "duration": 1.2, "offset_in_shot": 1.0}
                if hook else {"enabled": False}
            ),
        },
        "art_style": "Photoreal locked tripod frame.",
        "music": music,
        "characters": [],
        "environments": [],
        "props": [],
    }


def fixed_cfg(shots=3):
    return {
        "enabled": True,
        "shots": shots,
        "shot_seconds": "10",
        "chain_breaks": [1, shots],
        "hook_shot": shots,
        "shot_plan": [f"LOCKED PHASE {number}" for number in range(1, shots + 1)],
        "families": ["alpha", "beta"],
        "title_patterns": [
            {"regex": r"Build [A-Z]+", "families": ["alpha"]},
            {"regex": r"Transform [A-Z]+", "families": ["beta"]},
        ],
    }


def raw_fixed_plan(number=1, shots=3):
    values = []
    for shot_number in range(1, shots + 1):
        values.append({
            "n": shot_number,
            "duration": "10",
            "prompt": (
                f"A detailed continuous construction action for phase {shot_number}, "
                "with visible material movement and a locked camera."
            ),
            "seed": None,
            "chain": shot_number not in {1, shots},
        })
    return {
        "episode": {"number": number, "title": "Build CABIN"},
        "synopsis": "A cabin is built in one locked view.",
        "hook_shot": shots,
        "narration": "",
        "family": "alpha",
        "shots": values,
    }


def normalized_fixed_plan(cfg=None):
    cfg = cfg or fixed_cfg()
    plan = raw_fixed_plan(shots=cfg["shots"])
    episodes = [plan]
    errors = replenish._validate_batch(
        episodes, Bible(bible_data()), 1, 1, set(), cfg
    )
    if errors:
        raise AssertionError(errors)
    return episodes[0]


class ChainDecisionTests(unittest.TestCase):
    def test_normal_segmented_flow_and_lookahead(self):
        shots = [
            {"n": 1, "chain": False},
            {"n": 2, "chain": True},
            {"n": 3, "chain": False},
        ]
        first = produce.decide_shot_chain(shots[0], shots[1], True, "stale")
        self.assertTrue(first.reset_before)
        self.assertIsNone(first.start_url)
        self.assertTrue(first.capture_last_frame)
        second = produce.decide_shot_chain(shots[1], shots[2], True, "frame-1")
        self.assertEqual(second.start_url, "frame-1")
        self.assertFalse(second.capture_last_frame)

    def test_cross_episode_start_isolated_by_runner(self):
        meta = SimpleNamespace(data={"last_frame_url": "prior-episode"})
        episode = Bible(bible_data(chain=True))
        series_data = bible_data(chain=True)
        series_data["series"]["chain_scope"] = "series"
        self.assertIsNone(series_runner._episode_chain_start(episode, meta))
        self.assertEqual(
            series_runner._episode_chain_start(Bible(series_data), meta),
            "prior-episode",
        )

    def test_chain_false_prevents_stale_frame_leakage(self):
        decision = produce.decide_shot_chain(
            {"n": 4, "chain": False}, {"n": 5, "chain": False}, True, "stale-frame"
        )
        self.assertIsNone(decision.start_url)
        self.assertTrue(decision.reset_before)
        self.assertFalse(decision.capture_last_frame)

    def test_chain_true_without_previous_frame_fails_closed(self):
        decision = produce.decide_shot_chain(
            {"n": 2, "chain": True}, None, True, None
        )
        self.assertIsNotNone(decision.error)
        self.assertIn("önceki son kare yok", decision.error)

    def test_legacy_missing_chain_field_keeps_old_behavior(self):
        decision = produce.decide_shot_chain({"n": 1}, None, True, "legacy-frame")
        self.assertFalse(decision.explicit)
        self.assertEqual(decision.start_url, "legacy-frame")
        self.assertTrue(decision.capture_last_frame)


class ReplenishValidationTests(unittest.TestCase):
    def errors(self, plan, cfg=None):
        return replenish._validate_batch(
            [plan], Bible(bible_data()), 1, 1, set(), fixed_cfg() if cfg is None else cfg
        )

    def test_exact_shot_count(self):
        plan = raw_fixed_plan()
        plan["shots"].pop()
        self.assertTrue(any("çekim sayısı tam 3" in error for error in self.errors(plan)))

    def test_exact_shot_duration(self):
        plan = raw_fixed_plan()
        plan["shots"][1]["duration"] = "8"
        self.assertTrue(any("süre tam 10" in error for error in self.errors(plan)))

    def test_exact_shot_number_set(self):
        plan = raw_fixed_plan()
        plan["shots"][1]["n"] = 1
        self.assertTrue(any("numaraları tam [1..3]" in error for error in self.errors(plan)))

    def test_chain_matches_chain_breaks(self):
        plan = raw_fixed_plan()
        plan["shots"][1]["chain"] = False
        self.assertTrue(any("chain=True olmalı" in error for error in self.errors(plan)))

    def test_hook_shot_matches_config(self):
        plan = raw_fixed_plan()
        plan["hook_shot"] = 2
        self.assertTrue(any("hook_shot 3 olmalı" in error for error in self.errors(plan)))

    def test_title_requires_fullmatch(self):
        plan = raw_fixed_plan()
        plan["episode"]["title"] = "Build CABIN extra"
        self.assertTrue(any("fullmatch" in error for error in self.errors(plan)))

    def test_title_family_constraint_rejects_wrong_family(self):
        plan = raw_fixed_plan()
        plan["family"] = "beta"
        self.assertTrue(any("ailesine izin vermiyor" in error for error in self.errors(plan)))

    def test_from_scratch_value_hook_money_forms_and_families(self):
        cfg = SeriesMeta.load("from-scratch").auto_replenish
        patterns = replenish._compiled_title_patterns(cfg)
        cases = (
            ("He Turned Scrap Into A $100,000 Home! ♻️✨", 3, "dönüşüm"),
            ("He Turned Silos Into A $250K Home! ♻️✨", 3,
             "geri dönüşüm / off-grid dönüşüm"),
            ("Building A $1.2M Cliff Home From Scratch! ✨", 4,
             "saklı/mühendislik harikası"),
            ("Building A $80,000 Cabin From Scratch! ✨", 4, "fantezi konutlar"),
        )
        for title, pattern_index, family in cases:
            with self.subTest(title=title):
                pattern, allowed = patterns[pattern_index]
                self.assertIsNotNone(pattern.fullmatch(title))
                self.assertIn(family, allowed)
        for pattern_index, title in (
            (3, "He Turned Scrap Into A $ Home! ♻️✨"),
            (3, "He Turned Scrap Into A $abc Home! ♻️✨"),
            (4, "Building A $ Cabin From Scratch! ✨"),
            (4, "Building A $abc Cabin From Scratch! ✨"),
        ):
            with self.subTest(title=title):
                self.assertIsNone(patterns[pattern_index][0].fullmatch(title))

    def test_61_character_title_is_rejected_once(self):
        cfg = fixed_cfg()
        cfg["title_patterns"] = [{"regex": r".{61}", "families": ["alpha"]}]
        plan = raw_fixed_plan()
        plan["episode"]["title"] = "X" * 61
        title_errors = [error for error in self.errors(plan, cfg) if "başlık" in error]
        self.assertEqual(title_errors, ["part 1: başlık boş veya 60 karakterden uzun"])

    def test_title_pattern_violation_is_reported_once(self):
        plan = raw_fixed_plan()
        plan["episode"]["title"] = "Build CABIN extra"
        violations = [error for error in self.errors(plan) if "fullmatch" in error]
        self.assertEqual(len(violations), 1)

    def test_bad_regex_is_config_error(self):
        cfg = fixed_cfg()
        cfg["title_patterns"][0]["regex"] = "(unclosed"
        self.assertTrue(any("bozuk regex" in error
                            for error in replenish.validate_replenish_config(cfg)))

    def test_cfg_loader_checks_breaks_hook_and_shot_plan(self):
        cfg = fixed_cfg()
        cfg["chain_breaks"] = [1, 1]
        cfg["hook_shot"] = 9
        cfg["shot_plan"] = ["one", ""]
        errors = replenish.validate_replenish_config(cfg)
        self.assertTrue(any("benzersiz" in error for error in errors))
        self.assertTrue(any("hook_shot" in error for error in errors))
        self.assertTrue(any("shot_plan" in error for error in errors))

    def test_normalizer_preserves_chain_and_prefixes_every_prompt(self):
        cfg = fixed_cfg()
        plan = raw_fixed_plan()
        episodes = [plan]
        self.assertEqual(replenish._validate_batch(
            episodes, Bible(bible_data()), 1, 1, set(), cfg
        ), [])
        plan = episodes[0]
        self.assertEqual([shot["chain"] for shot in plan["shots"]], [False, True, False])
        for index, shot in enumerate(plan["shots"]):
            self.assertTrue(shot["prompt"].startswith(cfg["shot_plan"][index] + "\n\n"))

    def test_generation_rejects_short_content_with_or_without_returned_prefix(self):
        cfg = fixed_cfg()
        prefix = cfg["shot_plan"][1] + "\n\n"
        for prompt in ("x", prefix + "x"):
            with self.subTest(prompt=prompt):
                plan = raw_fixed_plan()
                plan["shots"][1]["prompt"] = prompt
                self.assertTrue(any(
                    "prompt bo\u015f/\u00e7ok k\u0131sa" in error
                    for error in self.errors(plan, cfg)
                ))

    def test_generation_without_shot_plan_still_rejects_short_content(self):
        cfg = fixed_cfg()
        del cfg["shot_plan"]
        plan = raw_fixed_plan()
        plan["shots"][1]["prompt"] = "x"
        self.assertTrue(any(
            "prompt bo\u015f/\u00e7ok k\u0131sa" in error for error in self.errors(plan, cfg)
        ))

    def test_pre_spend_rejects_short_content_with_or_without_returned_prefix(self):
        cfg = fixed_cfg()
        prefix = cfg["shot_plan"][1] + "\n\n"
        for prompt in ("x", prefix + "x"):
            with self.subTest(prompt=prompt):
                plan = normalized_fixed_plan(cfg)
                plan["shots"][1]["prompt"] = prompt
                self.assertTrue(any(
                    "prompt bo\u015f/\u00e7ok k\u0131sa" in error
                    for error in replenish.validate_plan_against_config(plan, cfg)
                ))

    def test_pre_spend_without_shot_plan_still_rejects_short_content(self):
        cfg = fixed_cfg()
        del cfg["shot_plan"]
        plan = raw_fixed_plan()
        plan["shots"][1]["prompt"] = "x"
        self.assertTrue(any(
            "prompt bo\u015f/\u00e7ok k\u0131sa" in error
            for error in replenish.validate_plan_against_config(plan, cfg)
        ))


class CriticStatusTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.clip = pathlib.Path(self.tempdir.name) / "shot_01.mp4"
        self.clip.write_bytes(b"clip")
        self.bible = Bible(bible_data())
        self.bible.data["series"]["qc"] = {"enabled": True, "max_regens_per_shot": 1}

    def call(self, review, *, bible=None, budget=0, regen=None):
        with mock.patch.object(critic, "review_clip", return_value=review), \
                mock.patch.object(critic, "_log_event"), \
                mock.patch.object(critic, "_notify"):
            return critic.qc_shot(
                bible or self.bible, {"n": 1}, self.clip, "prompt", regen,
                episode=1, budget={"left": budget},
            )

    def test_pass_status_is_explicit(self):
        path, credits, status = self.call(({"artifact_score": 0}, "pass", [], []))
        self.assertEqual((path, credits, status), (self.clip, 0.0, "pass"))

    def test_skip_status_is_explicit_and_legacy_passes_through(self):
        path, credits, status = self.call((None, "skip", ["offline"], []))
        self.assertEqual((path, credits, status), (self.clip, 0.0, "skip"))

    def test_fail_status_is_explicit(self):
        path, credits, status = self.call(
            ({"fix_notes": ["fix"]}, "fail", ["artifact"], []), regen=lambda _: None
        )
        self.assertEqual((path, credits, status), (None, 0.0, "fail"))

    def test_require_all_accepts_unreviewable_clip(self):
        strict = Bible(bible_data(require_all=True))
        strict.data["series"]["qc"]["enabled"] = True
        with mock.patch.object(critic.time, "sleep"):
            path, credits, status = self.call(
                (None, "skip", ["offline"], []), bible=strict
            )
        self.assertEqual((path, credits, status), (self.clip, 0.0, "skip"))
        self.assertTrue(self.clip.exists())

    def test_require_all_still_rejects_failed_clip_without_regen_budget(self):
        strict = Bible(bible_data(require_all=True))
        strict.data["series"]["qc"]["enabled"] = True
        path, credits, status = self.call(
            ({"fix_notes": ["düzelt"]}, "fail", ["artifact"], []),
            bible=strict, budget=0, regen=lambda _prompt: None,
        )
        self.assertEqual((path, credits, status), (None, 0.0, "fail"))
        self.assertFalse(self.clip.exists())
        self.assertTrue(list(self.clip.parent.glob("shot_01_qcfail*.mp4")))


class HardCapPathTests(unittest.TestCase):
    def test_main_omni_boundary_passes_and_overage_blocks(self):
        kwargs = {"prompt": "p", "duration": "10", "image_urls": [],
                  "audio_ids": [], "character_ids": []}
        allowed = HardCreditCap(200, 0)
        with mock.patch.object(produce, "generate_omni_shot", return_value={"url": "ok"}) as call:
            result = produce._gen_omni_with_fallback(
                kwargs, before_call=lambda: allowed.authorize("main_shot", "omni", "10")
            )
        self.assertEqual(result["url"], "ok")
        call.assert_called_once()

        blocked = HardCreditCap(199, 0)
        with mock.patch.object(produce, "generate_omni_shot") as call:
            self.assertIsNone(produce._gen_omni_with_fallback(
                kwargs, before_call=lambda: blocked.authorize("main_shot", "omni", "10")
            ))
        call.assert_not_called()

    def test_qc_regen_boundary_passes_and_overage_blocks(self):
        bible = Bible(bible_data())
        bible.data["series"]["qc"] = {"enabled": True, "max_regens_per_shot": 1}
        with tempfile.TemporaryDirectory() as td:
            clip = pathlib.Path(td) / "shot.mp4"

            def download(_url, target):
                pathlib.Path(target).write_bytes(b"regen")
                return True

            clip.write_bytes(b"bad")
            allowed = HardCreditCap(200, 0)
            reviews = [
                ({"fix_notes": ["fix"]}, "fail", ["artifact"], []),
                ({"artifact_score": 0}, "pass", [], []),
            ]
            with mock.patch.object(critic, "review_clip", side_effect=reviews), \
                    mock.patch.object(critic, "download_file", side_effect=download), \
                    mock.patch.object(critic, "_log_event"), \
                    mock.patch.object(critic, "_notify"):
                result = critic.qc_shot(
                    bible, {"n": 1}, clip, "prompt",
                    lambda _: ({"url": "regen"} if allowed.authorize(
                        "qc_regen", "omni", "10") else None),
                    episode=1, budget={"left": 1},
                )
            self.assertEqual(result[2], "pass")

            clip.write_bytes(b"bad-again")
            blocked = HardCreditCap(199, 0)
            with mock.patch.object(
                    critic, "review_clip",
                    return_value=({"fix_notes": ["fix"]}, "fail", ["artifact"], [])), \
                    mock.patch.object(critic, "_log_event"), \
                    mock.patch.object(critic, "_notify"):
                result = critic.qc_shot(
                    bible, {"n": 1}, clip, "prompt",
                    lambda _: ({"url": "regen"} if blocked.authorize(
                        "qc_regen", "omni", "10") else None),
                    episode=1, budget={"left": 1},
                )
            self.assertEqual(result[2], "fail")

    def test_paid_music_boundary_passes_and_overage_blocks(self):
        bible = Bible(bible_data(music=True))
        plan = {"episode": {"number": 1, "title": "Score"}, "music": "custom score"}
        with tempfile.TemporaryDirectory() as td:
            video = pathlib.Path(td) / "video.mp4"
            audio = pathlib.Path(td) / "music.mp3"
            video.write_bytes(b"video")
            audio.write_bytes(b"music")

            def mix(_video, _music, target, **_kwargs):
                pathlib.Path(target).write_bytes(b"mixed")

            allowed = HardCreditCap(80, 0)
            with mock.patch.object(music_generator, "generate_background_music", return_value=audio), \
                    mock.patch.object(produce.ffmpeg_tools, "mix_background_music", side_effect=mix), \
                    mock.patch.object(produce.cost_tracker, "log_cost"):
                self.assertIsNotNone(produce._post_process(
                    bible, plan, video, hard_cap=allowed, required_music=True
                ))

            blocked = HardCreditCap(79, 0)
            with mock.patch.object(music_generator, "generate_background_music") as generate, \
                    mock.patch.object(produce.cost_tracker, "log_cost"):
                self.assertIsNone(produce._post_process(
                    bible, plan, video, hard_cap=blocked, required_music=True
                ))
            generate.assert_not_called()

    def test_unknown_paid_call_fails_closed(self):
        cap = HardCreditCap(10_000, 0)
        self.assertFalse(cap.authorize("main_shot", "unlisted-engine", "10"))
        self.assertIn("bilinmeyen maliyet", cap.blocked_reason)


class GoldenNeutralityTests(unittest.TestCase):
    def assert_prechange_prompt_golden(self, slug, golden):
        meta = SeriesMeta.load(slug)
        bible = Bible.load(slug)
        contents, system = replenish._build_prompt(
            meta, bible, meta.auto_replenish, 1, 1, []
        )
        self.assertEqual(contents, golden["contents"])
        self.assertEqual(system, golden["system_instruction"])

    def test_required_keyless_series_stay_keyless_and_match_prechange_goldens(self):
        expected = json.loads(GOLDEN.read_text(encoding="utf-8"))
        self.assertEqual(
            set(expected),
            REQUIRED_KEYLESS_GOLDEN_SERIES | ROCK2_EXPECTED_OPT_IN_SERIES,
        )
        for slug in sorted(REQUIRED_KEYLESS_GOLDEN_SERIES):
            with self.subTest(slug=slug):
                meta = SeriesMeta.load(slug)
                opted_in = FIXEDFRAME_AUTO_OPT_IN_KEYS & set(meta.auto_replenish)
                self.assertFalse(
                    opted_in,
                    f"{slug} must remain fixed-frame-keyless; found {sorted(opted_in)}",
                )
                self.assert_prechange_prompt_golden(slug, expected[slug])

    def test_from_scratch_has_one_explicit_rock2_transition_path(self):
        expected = json.loads(GOLDEN.read_text(encoding="utf-8"))
        slug = next(iter(ROCK2_EXPECTED_OPT_IN_SERIES))
        meta = SeriesMeta.load(slug)
        opted_in = FIXEDFRAME_AUTO_OPT_IN_KEYS & set(meta.auto_replenish)
        if not opted_in:
            # Rock 1 state: it is still keyless, so the pre-change bytes remain binding.
            self.assert_prechange_prompt_golden(slug, expected[slug])
            return

        # Rock 2 state: only the reviewed from-scratch opt-in may bypass its old prompt.
        self.assertEqual(opted_in, FROM_SCRATCH_ROCK2_AUTO_KEYS)
        self.assertEqual(meta.auto_replenish.get("shots"), 6)
        self.assertEqual(meta.auto_replenish.get("shot_seconds"), "10")

    def test_keyless_normalizer_does_not_introduce_new_fields(self):
        plan = {
            "episode": {"number": 1, "title": "Legacy"},
            "synopsis": "Legacy behavior.",
            "hook_shot": 2,
            "narration": "",
            "shots": [
                {"n": 9, "duration": "8", "prompt": "A detailed legacy opening visual with motion."},
                {"n": 8, "duration": "8", "prompt": "A detailed legacy closing visual with motion."},
            ],
        }
        episodes = [plan]
        self.assertEqual(replenish._validate_batch(
            episodes, Bible(bible_data(slug="legacy", chain=False)), 1, 1, set(), {}
        ), [])
        plan = episodes[0]
        self.assertEqual([shot["n"] for shot in plan["shots"]], [1, 2])
        self.assertTrue(all("chain" not in shot for shot in plan["shots"]))
        for key in ("family", "seed_id", "music", "title_card", "caption"):
            self.assertNotIn(key, plan)


class EngineFixture(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = pathlib.Path(self.tempdir.name)
        self.channel = self.root / "channel"
        self.channel.mkdir()
        self.output = self.root / "output" / "series"
        self.slug = "engine-test"
        self.patchers = [
            mock.patch.object(bible_module, "PROJECT_ROOT", self.root),
            mock.patch.object(bible_module, "SERIES_DATA_DIR", self.root / "series_data"),
            mock.patch.object(bible_module, "SERIES_DIR", self.output),
            mock.patch.object(bible_module, "_SEARCH_ROOTS", [self.channel]),
            mock.patch.object(cost_tracker, "COST_LOG", self.root / "cost.json"),
        ]
        for patcher in self.patchers:
            patcher.start()
            self.addCleanup(patcher.stop)

    def write_series(self, *, cfg=None, bible=None, pin=False):
        folder = self.channel / self.slug
        folder.mkdir(exist_ok=True)
        doctrine = "Fixed frame test doctrine.\n"
        (self.channel / "KONSEPT.md").write_text(doctrine, encoding="utf-8")
        meta = {
            "slug": self.slug,
            "base_title": "Engine Test",
            "logline": "Offline proof.",
            "total_parts": 1,
            "next_part": 1,
            "status": "active",
            "parts": {},
        }
        if cfg is not None:
            meta["auto_replenish"] = cfg
        if pin:
            meta["doctrine_sha256"] = hashlib.sha256(doctrine.encode("utf-8")).hexdigest()
        (folder / "series.json").write_text(json.dumps(meta), encoding="utf-8")
        data = bible or bible_data(slug=self.slug)
        (folder / "bible.json").write_text(json.dumps(data), encoding="utf-8")
        return folder, meta.get("doctrine_sha256")

    def plan(self, *, explicit=False):
        shots = []
        for number in (1, 2):
            shot = {
                "n": number,
                "duration": "10",
                "prompt": f"Detailed offline engine test shot {number} with visible continuous motion.",
            }
            if explicit:
                shot["chain"] = number != 1
            shots.append(shot)
        return {
            "episode": {"number": 1, "title": "Offline"},
            "synopsis": "Offline engine test.",
            "hook_shot": 2,
            "narration": "",
            "shots": shots,
        }

    def precreate(self, plan):
        folder = self.output / self.slug / "episodes" / "ep01" / "shots"
        folder.mkdir(parents=True, exist_ok=True)
        for shot in plan["shots"]:
            (folder / f"shot_{shot['n']:02d}.mp4").write_bytes(b"cached")

    @contextlib.contextmanager
    def media_fakes(self, *, generation=None, hook_error=False):
        def write_second(*args, **_kwargs):
            pathlib.Path(args[1]).parent.mkdir(parents=True, exist_ok=True)
            pathlib.Path(args[1]).write_bytes(b"video")
            return pathlib.Path(args[1])

        def download(_url, target):
            pathlib.Path(target).parent.mkdir(parents=True, exist_ok=True)
            pathlib.Path(target).write_bytes(b"download")
            return True

        def last_frame(source):
            target = pathlib.Path(source).with_suffix(".jpg")
            target.write_bytes(b"frame")
            return target

        with contextlib.ExitStack() as stack:
            mocks = {}
            mocks["check"] = stack.enter_context(mock.patch.object(produce, "check_credit"))
            mocks["generate"] = stack.enter_context(mock.patch.object(
                produce, "_generate_visual_clip",
                side_effect=generation if generation is not None else None,
                return_value=None if generation is not None else {"url": "video", "credits": 0},
            ))
            stack.enter_context(mock.patch.object(produce, "download_file", side_effect=download))
            mocks["last"] = stack.enter_context(mock.patch.object(
                produce.ffmpeg_tools, "extract_last_frame", side_effect=last_frame
            ))
            stack.enter_context(mock.patch.object(
                produce, "upload_to_imgbb", side_effect=lambda path: f"frame://{path.stem}"
            ))
            stack.enter_context(mock.patch.object(
                produce.ffmpeg_tools, "get_video_duration", return_value=10.0
            ))
            mocks["concat"] = stack.enter_context(mock.patch.object(
                produce.ffmpeg_tools, "concatenate_simple", side_effect=write_second
            ))
            mocks["smooth"] = stack.enter_context(mock.patch.object(
                produce.ffmpeg_tools, "concatenate_audio_smooth", side_effect=write_second
            ))
            stack.enter_context(mock.patch.object(
                produce.ffmpeg_tools, "final_export", side_effect=write_second
            ))
            if hook_error:
                stack.enter_context(mock.patch.object(
                    produce.ffmpeg_tools, "extract_clip", side_effect=RuntimeError("hook failed")
                ))
            stack.enter_context(mock.patch.object(produce.report, "append_row"))
            stack.enter_context(mock.patch.object(produce.report, "export_xlsx"))
            stack.enter_context(mock.patch.object(
                produce.report, "summarize",
                return_value={"başarılı": 2, "çekim_sayısı": 2,
                              "toplam_kredi": 0, "toplam_dolar": 0},
            ))
            yield mocks

    def test_idempotent_skip_obeys_reset_and_lookahead(self):
        data = bible_data(slug=self.slug, chain=True)
        self.write_series(bible=data)
        plan = self.plan(explicit=True)
        shots = self.output / self.slug / "episodes" / "ep01" / "shots"
        shots.mkdir(parents=True)
        (shots / "shot_01.mp4").write_bytes(b"cached")
        starts = []

        def generate(_engine, _prompt, start, *_args, **_kwargs):
            starts.append(start)
            return {"url": "shot-two", "credits": 0}

        with self.media_fakes(generation=generate) as calls:
            result = produce.produce_episode(self.slug, plan)
        self.assertIsNotNone(result)
        self.assertEqual(starts, ["frame://shot_01"])
        self.assertEqual(calls["last"].call_count, 1)

    def test_require_all_shots_blocks_merge_when_any_shot_missing(self):
        data = bible_data(slug=self.slug, chain=False, require_all=True)
        self.write_series(bible=data)
        responses = iter(({"url": "one", "credits": 0}, None))
        with self.media_fakes(generation=lambda *_a, **_k: next(responses)) as calls:
            result = produce.produce_episode(self.slug, self.plan())
        self.assertIsNone(result)
        calls["concat"].assert_not_called()
        calls["smooth"].assert_not_called()

    def test_production_validation_runs_before_credit_or_generation(self):
        cfg = fixed_cfg(shots=2)
        data = bible_data(slug=self.slug, chain=True)
        self.write_series(cfg=cfg, bible=data)
        plan = raw_fixed_plan(shots=2)
        plan["shots"][0]["duration"] = "8"
        with mock.patch.object(produce, "check_credit") as credit, \
                mock.patch.object(produce, "_generate_visual_clip") as generate:
            self.assertIsNone(produce.produce_episode(self.slug, plan))
        credit.assert_not_called()
        generate.assert_not_called()

    def test_final_omni_kwargs_enforce_seven_unit_limit_after_chain_frame(self):
        cfg = fixed_cfg(shots=2)
        cfg["chain_breaks"] = [1]
        data = bible_data(slug=self.slug, chain=True, engine="omni")
        data["characters"] = [{"id": "worker", "name": "Worker", "character_id": "cid"}]
        data["environments"] = [{"id": "env", "ref_image_url": "env-url"}]
        data["props"] = [
            {"id": f"p{i}", "ref_image_url": f"p{i}-url"} for i in range(1, 6)
        ]
        self.write_series(cfg=cfg, bible=data)
        raw = raw_fixed_plan(shots=2)
        raw["shots"][1]["chain"] = True
        episodes = [raw]
        self.assertEqual(replenish._validate_batch(
            episodes, Bible(data), 1, 1, set(), cfg
        ), [])
        plan = episodes[0]
        for shot in plan["shots"]:
            shot["characters"] = ["worker"]
            shot["environment"] = "env"
            shot["props"] = [f"p{i}" for i in range(1, 6)]
        with self.assertLogs(produce.logger.name, level="ERROR") as logs:
            self.assertIsNone(produce.produce_episode(self.slug, plan, dry_run=True))
        self.assertIn("zincir karesi sonrası 7-birim kotası", "\n".join(logs.output))

    def test_required_hook_teaser_failure_blocks_delivery(self):
        data = bible_data(
            slug=self.slug, chain=False, required_layers=["hook_teaser"], hook=True
        )
        self.write_series(bible=data)
        plan = self.plan()
        self.precreate(plan)
        with self.media_fakes(hook_error=True):
            self.assertIsNone(produce.produce_episode(self.slug, plan))

    def test_required_music_failure_blocks_delivery(self):
        data = bible_data(
            slug=self.slug, chain=False, required_layers=["music"], music=True
        )
        self.write_series(bible=data)
        plan = self.plan()
        plan["music"] = "custom episode score"
        self.precreate(plan)
        with self.media_fakes(), mock.patch.object(
            music_generator, "generate_background_music", return_value=None
        ):
            self.assertIsNone(produce.produce_episode(self.slug, plan))

    def test_keyless_delivery_keeps_teaser_and_music_fail_open(self):
        data = bible_data(slug=self.slug, chain=False, music=True, hook=True)
        self.write_series(bible=data)
        plan = self.plan()
        plan["music"] = "custom episode score"
        self.precreate(plan)
        with self.media_fakes(hook_error=True), mock.patch.object(
            music_generator, "generate_background_music", return_value=None
        ):
            result = produce.produce_episode(self.slug, plan)
        self.assertIsNotNone(result)
        self.assertTrue(pathlib.Path(result).exists())

    def test_absent_hard_cap_keeps_legacy_main_call_fail_open(self):
        cfg = {"enabled": True, "shots": 2, "shot_seconds": "10"}
        data = bible_data(slug=self.slug, chain=False)
        self.write_series(cfg=cfg, bible=data)
        with mock.patch.dict(os.environ, {"EPISODE_CREDIT_CAP": "1"}), self.media_fakes() as calls:
            result = produce.produce_episode(self.slug, self.plan())
        self.assertIsNotNone(result)
        self.assertEqual(calls["generate"].call_count, 2)

    def test_preflight_positive_and_corrupted_plan_nonzero(self):
        cfg = fixed_cfg(shots=2)
        data = bible_data(slug=self.slug, chain=True)
        folder, digest = self.write_series(cfg=cfg, bible=data, pin=True)
        plan = normalized_fixed_plan(cfg)
        plan["doctrine_sha256"] = digest
        path = folder / "plan.json"
        path.write_text(json.dumps(plan), encoding="utf-8")
        errors, trace = preflight.inspect(self.slug, path)
        self.assertEqual(errors, [])
        self.assertEqual([entry["status"] for entry in trace], ["ok", "ok"])
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(preflight.run(self.slug, path), 0)

        broken = copy.deepcopy(plan)
        broken["shots"][0]["chain"] = True
        path.write_text(json.dumps(broken), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertNotEqual(preflight.run(self.slug, path), 0)


if __name__ == "__main__":
    unittest.main()
