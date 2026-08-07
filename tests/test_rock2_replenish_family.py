"""ROCK 2 aile rotasyonu oto-ikmal regresyonları, tamamen çevrimdışı."""

import copy
import json
import pathlib
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from series import replenish
from series.bible import Bible
from series.series_meta import SeriesMeta


sys.stdout.reconfigure(encoding="utf-8")


FORBIDDEN_FAMILY = "zaman çarpması"
FIRST_POOL_MARKER = "RUNTIME UNUSED TOPIC POOL FOR FIRST EPISODE 6."
LATER_POOL_MARKER = "RUNTIME UNUSED TOPIC POOL FOR LATER EPISODES 7-10."


def flashpoints_context():
    meta = SeriesMeta.load("flashpoints")
    bible = Bible.load("flashpoints")
    history = replenish._episode_history("flashpoints")
    if meta is None or bible is None:
        raise AssertionError("flashpoints gerçek yapılandırması yüklenemedi")
    return meta, bible, meta.auto_replenish, history


def decode_pool_after(contents, marker):
    tail = contents.split(marker, 1)[1]
    start = tail.index("[")
    pool, _ = json.JSONDecoder().raw_decode(tail[start:])
    return pool


def model_plan(number, seed_id, family, title):
    return {
        "episode": {"number": number, "title": title},
        "synopsis": "A specific verified historical event is reconstructed from surviving records.",
        "hook_shot": 1,
        "narration": (
            "In 1850, this verified historical event overturned expectations as witnesses watched "
            "the extraordinary moment unfold, leaving physical evidence that researchers and "
            "public records still document clearly today."
        ),
        "family": family,
        "seed_id": seed_id,
        "music": (
            "Fast tense percussion with sharp frame drums, low strings, metallic pulses, and urgent "
            "bass drives immediately forward, sustains pressure, then stops abruptly mid-rhythm "
            "for looping."
        ),
        "title_card": {"title": "Archive Evidence", "subtitle": "History, 1850"},
        "shots": [
            {
                "n": 1,
                "duration": "8",
                "prompt": (
                    "Vertical close view of period hands moving a documented historical object "
                    "through hard window light as witnesses react in the background."
                ),
                "seed": None,
            },
            {
                "n": 2,
                "duration": "8",
                "prompt": (
                    "Tight macro view of the surviving evidence turning under lamplight while "
                    "the same deliberate action continues and returns toward the opening frame."
                ),
                "seed": None,
            },
        ],
    }


class Rock2ReplenishFamilyTests(unittest.TestCase):
    def test_prompt_names_forbidden_family_and_filters_only_first_position(self):
        meta, bible, cfg, history = flashpoints_context()
        self.assertEqual(history[-1]["n"], 5)
        self.assertEqual(history[-1]["family"], FORBIDDEN_FAMILY)

        contents, system_instruction = replenish._build_prompt(
            meta, bible, cfg, 6, 5, history, calibration={}
        )
        exact_rule = (
            '- CRITICAL FAMILY BLOCK FOR EPISODE 6: The previous episode used '
            '"zaman çarpması", so episode 6 must not use "zaman çarpması".'
        )
        self.assertIn(exact_rule, system_instruction)

        first_pool = decode_pool_after(contents, FIRST_POOL_MARKER)
        later_pool = decode_pool_after(contents, LATER_POOL_MARKER)
        stored_unused = replenish._unused_topics(cfg, history)

        self.assertTrue(first_pool)
        self.assertTrue(all(item["family"] != FORBIDDEN_FAMILY for item in first_pool))
        self.assertTrue(any(item["family"] == FORBIDDEN_FAMILY for item in later_pool))
        self.assertTrue(any(item["family"] == FORBIDDEN_FAMILY for item in stored_unused))

    def test_validator_rejects_history_repeat_and_names_forbidden_family(self):
        _meta, bible, cfg, history = flashpoints_context()
        repeated = model_plan(
            6, 2, FORBIDDEN_FAMILY, "How Oxford Predated An Empire In 1096!"
        )
        errors = replenish._validate_batch(
            [repeated], bible, 6, 1, set(), cfg, history, {}
        )
        family_errors = [error for error in errors if "ardışık iki part" in error]
        self.assertEqual(len(family_errors), 1)
        self.assertIn("part 6", family_errors[0])
        self.assertIn(FORBIDDEN_FAMILY, family_errors[0])

    def test_generation_makes_three_attempts_and_final_report_names_rule_and_family(self):
        meta, bible, cfg, _history = flashpoints_context()

        def rejected_response(*_args, **_kwargs):
            return {
                "episodes": [copy.deepcopy(model_plan(
                    6, 2, FORBIDDEN_FAMILY, "How Oxford Predated An Empire In 1096!"
                ))]
            }

        with mock.patch.object(replenish, "_gen_json", side_effect=rejected_response) as gemini:
            with self.assertRaises(RuntimeError) as raised:
                replenish.generate_plans(meta, bible, cfg, 6, 1, calibration={})

        self.assertEqual(gemini.call_count, 3)
        message = str(raised.exception)
        self.assertIn("ardışık iki part aynı family", message)
        self.assertIn(FORBIDDEN_FAMILY, message)

    def test_validator_preserves_cross_batch_family_guard(self):
        _meta, bible, cfg, history = flashpoints_context()
        episodes = [
            model_plan(6, 9, "yanılgı kırıcı", "The Real Reason Tomato Pills Were Medicine"),
            model_plan(7, 21, "yanılgı kırıcı", "The Real Reason The Moon Hid The Great Wall"),
        ]
        errors = replenish._validate_batch(
            episodes, bible, 6, 2, set(), cfg, history, {}
        )
        family_errors = [error for error in errors if "ardışık iki part" in error]
        self.assertEqual(len(family_errors), 1)
        self.assertIn("part 7", family_errors[0])
        self.assertIn("yanılgı kırıcı", family_errors[0])


if __name__ == "__main__":
    unittest.main()
