"""ROCK 2 object-card/reference-lock proofs; all external calls are mocked."""

import copy
import json
import pathlib
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from series import produce, replenish
from series.bible import Bible, atomic_write_json
from series.credit_gate import HardCreditCap
from series.omni_api import build_omni_payload
from series.shots import (
    NEGATIVE_VIDEO_LANGUAGE,
    TEK_OBJE_FORMAT,
    load_plan,
    resolve_shot,
    validate_plan,
)
from series.series_meta import SeriesMeta


DESCRIPTOR = (
    "A palm-sized matte cobalt-blue ceramic cube with one thin white diagonal "
    "scratch across its front edge"
)
ANOMALY = (
    "a solid blue dust ribbon holding a firm glassy arch that keeps its even "
    "width and matte sheen"
)
FRAMING = (
    "The close bench-level view stays in one fixed composition with the workbench "
    "edge aligned identically throughout the shot."
)
ENV_ID = "workbench_main"
ENV_URL = "https://i.ibb.co/rock2/environment.png"
OBJECT_URL = "https://i.ibb.co/rock2/object.png"


def bible_data(*, environment_url=None):
    return {
        "series": {
            "slug": "rock2-test",
            "title": "Rock 2 Test",
            "aspect_ratio": "9:16",
            "resolution": "1080p",
            "engine": "omni",
            "chain_frames": False,
        },
        "art_style": "Natural workshop footage with realistic daylight and worn wood.",
        "characters": [],
        "environments": [{
            "id": ENV_ID,
            "desc": "worn wooden workbench in a small home workshop corner with side daylight",
            "ref_image_url": environment_url,
        }],
        "props": [],
    }


def raw_plan(number=1, *, action_only=False):
    shots = []
    actions = (
        "Two hands rotate the cube while its scratch releases a slow ribbon of solid blue dust.",
        "Two hands press the cube and the same ribbon bends upward into a firm arch.",
        "Two hands tap the cube and the arch extends across the worn surface in branching loops.",
        "Two hands return the cube to its opening position while the ribbon continues flowing.",
    )
    for index, action in enumerate(actions, start=1):
        shots.append({
            "n": index,
            "duration": "6",
            "prompt": action if action_only else f"{DESCRIPTOR}. {ANOMALY}. {FRAMING} {action}",
            "seed": None,
            "environment": ENV_ID,
        })
    return {
        "episode": {"number": number, "title": "The Cube Keeps Drawing"},
        "synopsis": "A marked ceramic cube extrudes a solid ribbon that keeps drawing loops.",
        "hook_shot": 3,
        "narration": "",
        "format_version": TEK_OBJE_FORMAT,
        "object_card": {
            "name": "ceramic cube",
            "descriptor": DESCRIPTOR,
            "environment": ENV_ID,
            "framing": FRAMING,
            "anomaly_descriptor": ANOMALY,
        },
        "shots": shots,
    }


FORMAT_CFG = {
    "format_version": TEK_OBJE_FORMAT,
    "shots": 4,
    "shot_seconds": "6",
}


class EndToEndReferenceChainTests(unittest.TestCase):
    def test_raw_llm_to_atomic_disk_to_final_omni_kwargs_and_idempotent_refs(self):
        bible = Bible(bible_data())
        meta = SimpleNamespace(
            slug="rock2-test",
            base_title="Rock 2 Test",
            logline="One object in one fixed workshop composition.",
        )
        response = {"episodes": [raw_plan(action_only=True)]}
        with mock.patch.object(replenish, "_gen_json", return_value=response) as llm:
            episodes = replenish.generate_plans(meta, bible, FORMAT_CFG, 1, 1)
        llm.assert_called_once()
        self.assertEqual(episodes[0]["format_version"], TEK_OBJE_FORMAT)
        self.assertEqual(episodes[0]["object_card"]["descriptor"], DESCRIPTOR)
        self.assertEqual(validate_plan(episodes[0], bible)["errors"], [])
        locked_prefix = f"{DESCRIPTOR} {ANOMALY} {FRAMING} "
        for shot in episodes[0]["shots"]:
            self.assertTrue(shot["prompt"].startswith(locked_prefix))
            self.assertEqual(shot["prompt"].count(DESCRIPTOR), 1)
            self.assertEqual(shot["prompt"].count(FRAMING), 1)

        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            plan_path = root / "plans" / "part01.json"
            bible_path = root / "bible.json"
            atomic_write_json(plan_path, episodes[0])
            atomic_write_json(bible_path, bible.data)
            disk_plan = load_plan(plan_path)

            upload_urls = iter((ENV_URL, OBJECT_URL))

            def fake_download(_url, target):
                pathlib.Path(target).parent.mkdir(parents=True, exist_ok=True)
                pathlib.Path(target).write_bytes(b"image")
                return True

            cap = HardCreditCap(cap=100, spent=0)
            with mock.patch.object(produce, "bible_path", return_value=bible_path), \
                    mock.patch.object(produce, "refs_dir", side_effect=lambda _s, kind: root / "refs" / kind), \
                    mock.patch.object(produce, "generate_image", side_effect=(
                        "https://generation.invalid/environment.png",
                        "https://generation.invalid/object.png",
                    )) as generate, \
                    mock.patch.object(produce, "download_file", side_effect=fake_download), \
                    mock.patch.object(produce, "upload_to_imgbb", side_effect=lambda _p: next(upload_urls)), \
                    mock.patch.object(produce.cost_tracker, "log_cost") as log_cost, \
                    mock.patch.object(produce.report, "append_row") as append_row:
                self.assertTrue(produce.ensure_episode_refs(
                    bible, disk_plan, plan_path, hard_cap=cap
                ))
                first_call_count = generate.call_count

                persisted_plan = load_plan(plan_path)
                persisted_bible = Bible(json.loads(bible_path.read_text(encoding="utf-8")))
                self.assertTrue(produce.ensure_episode_refs(
                    persisted_bible, persisted_plan, plan_path, hard_cap=cap
                ))

            self.assertEqual(first_call_count, 2)
            self.assertEqual(generate.call_count, first_call_count)
            self.assertEqual(log_cost.call_count, 2)
            self.assertEqual(append_row.call_count, 2)
            self.assertEqual(
                [reservation["call_type"] for reservation in cap.reservations],
                ["reference_image", "reference_image"],
            )
            self.assertEqual(cap.spent, 16)
            operations = [call.args[1] for call in log_cost.call_args_list]
            self.assertEqual(
                operations,
                ["environment_ref_workbench_main_estimate_ep1", "object_ref_estimate_ep1"],
            )
            self.assertEqual(persisted_plan["prop_ref_urls"], [OBJECT_URL])
            self.assertEqual(
                persisted_bible.get("environments", ENV_ID)["ref_image_url"], ENV_URL
            )
            self.assertFalse(list(root.rglob("*.tmp-*")))

            for shot in persisted_plan["shots"]:
                resolved = resolve_shot(persisted_bible, shot, persisted_plan)
                kwargs = resolved["kwargs"]
                payload = build_omni_payload(**kwargs)
                self.assertIn(DESCRIPTOR, kwargs["prompt"])
                self.assertIn(FRAMING, kwargs["prompt"])
                self.assertIsNone(NEGATIVE_VIDEO_LANGUAGE.search(kwargs["prompt"]))
                self.assertEqual(kwargs["image_urls"], [OBJECT_URL, ENV_URL])
                self.assertEqual(payload["input"]["image_urls"], [OBJECT_URL, ENV_URL])
                self.assertIn(
                    "[image 1] is the exact object: keep its shape, colour, scale and markings identical.",
                    kwargs["prompt"],
                )
                self.assertIn(
                    "[image 2] is the room and surface: keep the same surface and light.",
                    kwargs["prompt"],
                )
                self.assertEqual(resolved["units"], 2)

    def test_reference_image_call_is_blocked_before_generation_when_cap_is_too_small(self):
        bible = Bible(bible_data())
        plan = raw_plan()
        with tempfile.TemporaryDirectory() as temp, \
                mock.patch.object(produce, "generate_image") as generate:
            self.assertFalse(produce.ensure_episode_refs(
                bible,
                plan,
                pathlib.Path(temp) / "part01.json",
                hard_cap=HardCreditCap(cap=7, spent=0),
            ))
        generate.assert_not_called()


class FormatValidationTests(unittest.TestCase):
    def test_format_plan_is_valid_and_mutations_fail_closed(self):
        bible = Bible(bible_data())
        self.assertEqual(validate_plan(raw_plan(), bible)["errors"], [])

        mutations = []
        short = raw_plan()
        short["object_card"]["descriptor"] = "small blue ceramic cube with a white mark"
        mutations.append(short)
        missing_descriptor = raw_plan()
        missing_descriptor["shots"][2]["prompt"] = missing_descriptor["shots"][2]["prompt"].replace(
            DESCRIPTOR, "the cube"
        )
        mutations.append(missing_descriptor)
        missing_framing = raw_plan()
        missing_framing["shots"][1]["prompt"] = missing_framing["shots"][1]["prompt"].replace(
            FRAMING, "A close view holds steady."
        )
        mutations.append(missing_framing)
        wrong_environment = raw_plan()
        wrong_environment["shots"][0]["environment"] = "elsewhere"
        mutations.append(wrong_environment)
        wrong_duration = raw_plan()
        wrong_duration["shots"][0]["duration"] = "8"
        mutations.append(wrong_duration)
        wrong_count = raw_plan()
        wrong_count["shots"].pop()
        mutations.append(wrong_count)
        multiple_framing_sentences = raw_plan()
        multiple_framing_sentences["object_card"]["framing"] = f"{FRAMING} Hands remain central."
        for shot in multiple_framing_sentences["shots"]:
            shot["prompt"] = shot["prompt"].replace(
                FRAMING, multiple_framing_sentences["object_card"]["framing"]
            )
        mutations.append(multiple_framing_sentences)
        negative_prompt = raw_plan()
        negative_prompt["shots"][0]["prompt"] += " No extra object enters the frame."
        mutations.append(negative_prompt)

        for index, plan in enumerate(mutations):
            with self.subTest(case=index):
                self.assertTrue(validate_plan(plan, bible)["errors"])

    def test_validate_batch_rejects_numeric_six_and_keeps_card_and_tag(self):
        bible = Bible(bible_data())
        episodes = [raw_plan()]
        self.assertEqual(replenish._validate_batch(
            episodes, bible, 1, 1, set(), FORMAT_CFG
        ), [])
        self.assertEqual(episodes[0]["object_card"]["descriptor"], DESCRIPTOR)
        self.assertEqual(episodes[0]["format_version"], TEK_OBJE_FORMAT)

        bad = raw_plan()
        bad["shots"][0]["duration"] = 6
        errors = replenish._validate_batch([bad], bible, 1, 1, set(), FORMAT_CFG)
        self.assertTrue(any("tam '6' string" in error for error in errors))

    def test_validate_batch_does_not_duplicate_an_embedded_exact_descriptor(self):
        bible = Bible(bible_data())
        plan = raw_plan(action_only=True)
        plan["shots"][0]["prompt"] = (
            f"Two hands rotate {DESCRIPTOR} while its scratch releases a solid blue ribbon."
        )
        episodes = [plan]

        self.assertEqual(
            replenish._validate_batch(episodes, bible, 1, 1, set(), FORMAT_CFG), []
        )
        prompt = episodes[0]["shots"][0]["prompt"]
        self.assertEqual(prompt.count(DESCRIPTOR), 1)
        self.assertEqual(prompt.count(FRAMING), 1)
        self.assertEqual(validate_plan(episodes[0], bible)["errors"], [])

    def test_validate_batch_checks_positive_language_after_composition(self):
        bible = Bible(bible_data())
        plan = raw_plan(action_only=True)
        plan["shots"][0]["prompt"] = (
            "Two hands turn the cube without changing the fixed arrangement of the tools."
        )
        episodes = [plan]

        errors = replenish._validate_batch(episodes, bible, 1, 1, set(), FORMAT_CFG)

        self.assertTrue(any("yalnız olumlu görsel dil" in error for error in errors))
        self.assertTrue(
            episodes[0]["shots"][0]["prompt"].startswith(f"{DESCRIPTOR} {ANOMALY} {FRAMING} ")
        )

    def test_legacy_resolve_order_and_validation_are_unchanged(self):
        bible = Bible({
            **bible_data(environment_url=ENV_URL),
            "characters": [{"id": "worker", "ref_image_url": "https://legacy/worker.png"}],
            "props": [{"id": "tool", "ref_image_url": "https://legacy/tool.png"}],
        })
        legacy = {
            "episode": {"number": 1, "title": "Legacy"},
            "shots": [{
                "n": 1,
                "duration": "8",
                "prompt": "A detailed legacy workshop action continues under natural window light.",
                "characters": ["worker"],
                "environment": ENV_ID,
                "props": ["tool"],
            }],
        }
        self.assertEqual(validate_plan(legacy, bible)["errors"], [])
        self.assertEqual(
            resolve_shot(bible, legacy["shots"][0])["kwargs"]["image_urls"],
            ["https://legacy/worker.png", ENV_URL, "https://legacy/tool.png"],
        )

    def test_existing_object_reference_list_stays_before_environment(self):
        bible = Bible(bible_data(environment_url=ENV_URL))
        plan = raw_plan()
        plan["prop_ref_urls"] = [OBJECT_URL, "https://i.ibb.co/rock2/object-detail.png"]
        resolved = resolve_shot(bible, plan["shots"][0], plan)
        self.assertEqual(
            resolved["kwargs"]["image_urls"],
            [OBJECT_URL, "https://i.ibb.co/rock2/object-detail.png", ENV_URL],
        )
        self.assertIn(
            "[image 3] is the room and surface: keep the same surface and light.",
            resolved["kwargs"]["prompt"],
        )

    def test_hand_edited_format_plan_stops_produce_before_refs_or_video_engine(self):
        bad = raw_plan(999)
        bad["shots"][0]["prompt"] = bad["shots"][0]["prompt"].replace(
            DESCRIPTOR, "a drifting object"
        )
        with mock.patch.object(produce, "ensure_episode_refs") as ensure, \
                mock.patch.object(produce, "generate_omni_shot") as engine, \
                mock.patch.object(produce, "check_credit") as credit:
            self.assertIsNone(produce.produce_episode("unnatural-lab", bad))
        ensure.assert_not_called()
        engine.assert_not_called()
        credit.assert_not_called()


class PlannerIsolationTests(unittest.TestCase):
    def test_opt_in_prompt_has_object_schema_and_fixed_composition_rules(self):
        meta = SeriesMeta.load("unnatural-lab")
        bible = Bible.load("unnatural-lab")
        contents, system = replenish._build_prompt(
            meta, bible, meta.auto_replenish, 30, 1, []
        )
        self.assertIn('"format_version": "tek-obje-4x6"', system)
        self.assertIn('"object_card": {"name"', system)
        self.assertIn(
            'Each shot\'s "prompt" field contains ONLY that shot\'s specific action and state',
            system,
        )
        self.assertIn("the pipeline composes them mechanically", system)
        self.assertNotIn("Copy that descriptor VERBATIM", system)
        self.assertIn(
            "All shots share ONE fixed composition on the same everyday surface in "
            "the same light; the cuts are jumps in time only.",
            system,
        )
        self.assertNotIn("each shot may open a new angle", system)
        self.assertNotIn("camera flow", system)
        self.assertNotIn("striking opening → build → peak spectacle", system)
        self.assertIn("environments: kitchen_counter", contents)
        self.assertIn("workbench_main", contents)

    def test_legacy_planner_prompt_remains_byte_identical_to_golden(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        golden = json.loads(
            (root / "tests" / "golden" / "fixedframe_prompts.json").read_text(
                encoding="utf-8"
            )
        )["flashpoints"]
        meta = SeriesMeta.load("flashpoints")
        bible = Bible.load("flashpoints")
        contents, system = replenish._build_prompt(
            meta, bible, meta.auto_replenish, 1, 1, []
        )
        self.assertEqual(contents, golden["contents"])
        self.assertEqual(system, golden["system_instruction"])

    def test_environment_description_is_composed_mechanically(self):
        bible = Bible(bible_data())
        meta = SimpleNamespace(
            slug="rock2-test",
            base_title="Rock 2 Test",
            logline="One object in one fixed workshop composition.",
        )
        env_desc = bible_data()["environments"][0]["desc"]
        response = {"episodes": [raw_plan(action_only=True)]}
        with mock.patch.object(replenish, "_gen_json", return_value=response):
            episodes = replenish.generate_plans(meta, bible, FORMAT_CFG, 1, 1)
        for shot in episodes[0]["shots"]:
            self.assertTrue(
                shot["prompt"].startswith(f"{DESCRIPTOR} {ANOMALY} {FRAMING} {env_desc} ")
            )
            self.assertEqual(shot["prompt"].count(env_desc), 1)

    def test_environment_description_is_not_duplicated_when_action_contains_it(self):
        bible = Bible(bible_data())
        meta = SimpleNamespace(
            slug="rock2-test",
            base_title="Rock 2 Test",
            logline="One object in one fixed workshop composition.",
        )
        env_desc = bible_data()["environments"][0]["desc"]
        plan = raw_plan(action_only=True)
        plan["shots"][0]["prompt"] = (
            f"Two hands rotate the cube above the {env_desc} while the scratch glows."
        )
        response = {"episodes": [plan]}
        with mock.patch.object(replenish, "_gen_json", return_value=response):
            episodes = replenish.generate_plans(meta, bible, FORMAT_CFG, 1, 1)
        self.assertEqual(episodes[0]["shots"][0]["prompt"].count(env_desc), 1)

    def test_workflow_persists_bible_through_series_tree(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        workflow = (root / ".github" / "workflows" / "unnatural-lab.yml").read_text(
            encoding="utf-8"
        )
        persist = workflow.split("- name: Persist series state", 1)[1]
        self.assertIn("sentinal_ihsan/", persist)


if __name__ == "__main__":
    unittest.main()
