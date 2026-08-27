"""ROCK B: anomali kimligi, ihlal okunurlugu, sahne durumu ve ortam-notr dil.

P7 geregi uc yeni alan LOG-ONLY baslar; bu paket hem olcum yolunu hem de terfi
edildiginde kapinin nasil davrandigini kanitlar.
"""

import hashlib
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from series import critic, produce, replenish
from series.bible import Bible
from series.shots import TEK_OBJE_FORMAT, format_plan_errors

REPO = pathlib.Path(__file__).resolve().parents[1]


def unnatural_plan(part: int = 23) -> dict:
    path = REPO / "sentinal_ihsan" / "unnatural-lab" / "plans" / f"part{part}.json"
    return json.loads(path.read_text(encoding="utf-8"))


class SchemaTests(unittest.TestCase):
    """Anomali imzasi ve cekim alanlari fail-closed dogrulanir."""

    def setUp(self):
        self.bible = Bible.load("unnatural-lab")
        self.plan = unnatural_plan()
        self.assertEqual(self.plan.get("format_version"), TEK_OBJE_FORMAT)
        self.assertEqual(format_plan_errors(self.plan, self.bible), [])

    def test_missing_anomaly_descriptor_is_rejected(self):
        plan = unnatural_plan()
        plan["object_card"].pop("anomaly_descriptor")
        errors = format_plan_errors(plan, self.bible)
        self.assertTrue(any("anomaly_descriptor" in error for error in errors), errors)

    def test_short_anomaly_descriptor_is_rejected(self):
        plan = unnatural_plan()
        short = "grey stone steps"
        plan["object_card"]["anomaly_descriptor"] = short
        for shot in plan["shots"]:
            shot["prompt"] = shot["prompt"] + " " + short
        errors = format_plan_errors(plan, self.bible)
        self.assertTrue(any("en az 10 kelime" in error for error in errors), errors)

    def test_anomaly_must_appear_verbatim_in_every_shot(self):
        plan = unnatural_plan()
        anomaly = plan["object_card"]["anomaly_descriptor"]
        plan["shots"][2]["prompt"] = plan["shots"][2]["prompt"].replace(anomaly, "a vague shimmer")
        errors = format_plan_errors(plan, self.bible)
        self.assertTrue(any("anomaly_descriptor metnini birebir" in e for e in errors), errors)

    def test_violation_observation_rejects_negative_claims(self):
        plan = unnatural_plan()
        plan["shots"][0]["violation_observation"] = "the water never reaches the counter"
        errors = format_plan_errors(plan, self.bible)
        flat = " ".join(errors).replace("ö", "o").replace("ü", "u")
        self.assertIn("OLUMLU ve gozlemlenebilir", flat)

    def test_violation_observation_rejects_temporal_overreach(self):
        claims = (
            "the water always drains down the stone steps",
            "the water flows down the steps forever",
            "the water eventually reaches the dark shaft",
            "the stone remains still wet after the pour ends",
            "the stream keeps running down the steps indefinitely",
        )
        for claim in claims:
            with self.subTest(claim=claim):
                plan = unnatural_plan()
                plan["shots"][0]["violation_observation"] = claim
                errors = format_plan_errors(plan, self.bible)
                self.assertTrue(any("zaman-ötesi" in error for error in errors), errors)

    def test_instead_of_is_rejected_in_composed_prompt(self):
        plan = unnatural_plan()
        plan["shots"][0]["prompt"] += " The water pools instead of draining."
        errors = format_plan_errors(plan, self.bible)
        self.assertTrue(any("olumlu görsel dil" in error for error in errors), errors)

    def test_state_carry_on_the_last_shot_is_rejected(self):
        plan = unnatural_plan()
        plan["shots"][-1]["state_carry"] = "a wet ring stays on the surface"
        errors = format_plan_errors(plan, self.bible)
        self.assertTrue(any("state_carry" in e for e in errors), errors)

    def test_state_carry_missing_from_next_prompt_is_rejected(self):
        plan = unnatural_plan(25)
        carry = plan["shots"][0]["state_carry"]
        plan["shots"][1]["prompt"] = plan["shots"][1]["prompt"].replace(carry, "")
        errors = format_plan_errors(plan, self.bible)
        self.assertTrue(any("ardıl çekim prompt'unda birebir" in e for e in errors), errors)

    def test_migrated_part22_through_part26_pass_strengthened_validator(self):
        for part in range(22, 27):
            with self.subTest(part=part):
                self.assertEqual(format_plan_errors(unnatural_plan(part), self.bible), [])

    def test_ref_prompt_hash_must_be_hex(self):
        plan = unnatural_plan()
        plan["ref_prompt_sha256"] = "not-a-hash"
        errors = format_plan_errors(plan, self.bible)
        self.assertTrue(any("ref_prompt_sha256" in e for e in errors), errors)


class VerdictTableTests(unittest.TestCase):
    """Terfi edilen alanin karar tablosu; edilmeyen alan hicbir seyi durdurmaz."""

    BASE = {"artifact_score": 0}

    def decide(self, value, *, enforced=True, field="violation_reads"):
        qc = {"artifact_threshold": 6, "_rb_requested": (field,)}
        if enforced:
            qc["enforce"] = {field: True}
        review = dict(self.BASE)
        review[field] = value
        return critic._decide(review, qc, False, 1)

    def test_true_passes(self):
        self.assertEqual(self.decide({"value": True, "visible": True, "confidence": 0.9})[0], "pass")

    def test_visible_false_fails(self):
        verdict, reasons = self.decide({"value": False, "visible": True, "confidence": 0.9})
        self.assertEqual(verdict, "fail")
        self.assertTrue(reasons)

    def test_invisible_null_passes(self):
        self.assertEqual(self.decide({"value": None, "visible": False, "confidence": 0.9})[0], "pass")

    def test_unjustified_null_holds(self):
        self.assertEqual(self.decide({"value": None, "visible": True, "confidence": 0.9})[0], "hold")

    def test_low_confidence_holds(self):
        self.assertEqual(self.decide({"value": True, "visible": True, "confidence": 0.3})[0], "hold")

    def test_schema_violation_holds(self):
        self.assertEqual(self.decide("yes")[0], "hold")

    def test_missing_confidence_holds(self):
        self.assertEqual(self.decide({"value": True, "visible": True})[0], "hold")

    def test_extra_key_holds(self):
        value = {"value": True, "visible": True, "confidence": 0.9, "notes": "extra"}
        self.assertEqual(self.decide(value)[0], "hold")

    def test_contradictory_shapes_hold(self):
        for value in (True, False):
            with self.subTest(value=value):
                result = {"value": value, "visible": False, "confidence": 0.9}
                self.assertEqual(self.decide(result)[0], "hold")

    def test_log_only_field_never_blocks(self):
        for value in ({"value": False, "visible": True, "confidence": 1.0},
                      {"value": None, "visible": True, "confidence": 1.0},
                      "sema disi"):
            with self.subTest(value=value):
                self.assertEqual(self.decide(value, enforced=False)[0], "pass")


class PlumbingTests(unittest.TestCase):
    """Plan -> review_clip -> Gemini talimati zinciri gercekten tasiyor."""

    def test_fields_reach_the_review_call(self):
        anomaly = "weathered grey stone treads descending into an unlit shaft below the rind"
        observation = "the poured water disappears into the dark shaft"
        carry = "water glistens on the stone steps"
        captured = {}

        def fake_review_frames(frames, ref_face, prompt, notes, **kwargs):
            captured.update(kwargs)
            return {"artifact_score": 0}

        bible = Bible.load("unnatural-lab")
        shot = {"n": 3, "violation_observation": observation}
        with mock.patch.object(critic, "_review_frames", side_effect=fake_review_frames), \
                mock.patch.object(critic.ffmpeg_tools, "sample_frames",
                                  return_value=[pathlib.Path("f1.jpg")]):
            verdict = critic.review_clip(
                bible, shot, pathlib.Path("clip.mp4"), "prompt",
                critic.qc_config(bible),
                object_ref=b"reference-bytes",
                previous_frame=pathlib.Path("prev.jpg"),
                anomaly_descriptor=anomaly,
                violation_observation=observation,
                state_carry_expected=carry,
                episode=23,
            )
        self.assertIsNotNone(verdict[0], "review cagrisi hic yapilmadi")
        self.assertEqual(captured.get("anomaly_descriptor"), anomaly)
        self.assertEqual(captured.get("violation_observation"), observation)
        self.assertEqual(captured.get("state_carry_expected"), carry)

    def test_raw_planner_fields_survive_normalization_and_reach_review(self):
        response = {"episodes": [unnatural_plan(25)]}
        bible = Bible.load("unnatural-lab")
        errors = replenish._validate_batch(
            response["episodes"], bible, 25, 1, set(),
            {"format_version": TEK_OBJE_FORMAT, "shots": 4, "shot_seconds": "6"},
        )
        self.assertEqual(errors, [])
        normalized = response["episodes"][0]
        observation = normalized["shots"][1]["violation_observation"]
        carry = normalized["shots"][0]["state_carry"]
        self.assertIn(carry, normalized["shots"][1]["prompt"])
        captured = {}

        def fake_review_frames(frames, ref_face, prompt, notes, **kwargs):
            captured.update(kwargs)
            return {"artifact_score": 0}

        with mock.patch.object(critic, "_review_frames", side_effect=fake_review_frames), \
                mock.patch.object(critic.ffmpeg_tools, "sample_frames",
                                  return_value=[pathlib.Path("f1.jpg")]):
            critic.review_clip(
                bible, normalized["shots"][1], pathlib.Path("clip.mp4"), "prompt",
                critic.qc_config(bible), object_ref=b"reference-bytes",
                previous_frame=pathlib.Path("prev.jpg"),
                anomaly_descriptor=normalized["object_card"]["anomaly_descriptor"],
                violation_observation=observation,
                state_carry_expected=carry,
                episode=25,
            )
        self.assertEqual(captured.get("violation_observation"), observation)
        self.assertEqual(captured.get("state_carry_expected"), carry)

    def test_addenda_carry_the_exact_text_and_the_visibility_rule(self):
        anomaly = "weathered grey stone treads descending into an unlit shaft"
        text = critic._anomaly_addendum(anomaly)
        self.assertIn(anomaly, text)
        self.assertIn("visible=true and value=false", " ".join(text.split()))
        observation = "the sugar cube vanishes into the dark turn"
        violation_text = critic._violation_addendum(observation)
        self.assertIn(observation, violation_text)
        self.assertIn("only partly true", violation_text)
        compact_violation = " ".join(violation_text.split())
        self.assertIn("contradicting outcome", compact_violation)
        self.assertIn("water descending the steps AND", compact_violation)
        carry = "a deep groove remains in the wood"
        self.assertIn(carry, critic._state_carry_addendum(carry))

    def test_enforced_field_is_a_mandatory_gate_and_disables_fail_open(self):
        qc = {
            "frames": 12, "frame_width": 640, "artifact_threshold": 7,
            "api_fail_open": True, "enforce": {"violation_reads": True},
        }
        with mock.patch.object(critic.ffmpeg_tools, "sample_frames", return_value=[]):
            result = critic.review_clip(
                Bible.load("unnatural-lab"), {"n": 1}, pathlib.Path("clip.mp4"),
                "prompt", qc, violation_observation="water descends the stone steps",
            )
        self.assertEqual(result[1], "hold")
        self.assertTrue(critic._has_mandatory_gate(qc))
        self.assertFalse(critic._api_fail_open(qc))

    def test_qc_pass_event_contains_all_rock_b_fields(self):
        values = {
            "anomaly_match": {"value": True, "visible": True, "confidence": 0.9},
            "violation_reads": {"value": True, "visible": True, "confidence": 0.9},
            "state_carry_ok": {"value": None, "visible": False, "confidence": 0.9},
        }
        review = {"artifact_score": 0, **values}
        events = []
        qc = {
            "artifact_threshold": 7, "max_regens_per_shot": 0,
            "qc_review_retries": 0,
        }
        with mock.patch.object(critic, "qc_config", return_value=qc), \
                mock.patch.object(critic, "review_clip",
                                  return_value=(review, "pass", [], [])), \
                mock.patch.object(critic, "content_sha256", return_value="a" * 64), \
                mock.patch.object(critic, "_log_event",
                                  side_effect=lambda slug, event, **kwargs: events.append(event)):
            result = critic.qc_shot(
                Bible.load("unnatural-lab"),
                {"n": 2, "violation_observation": "water descends the stone steps"},
                pathlib.Path("clip.mp4"), "prompt", None, 25, {"left": 0},
                anomaly_descriptor="weathered stone steps descend into a dark shaft below the fruit",
                state_carry_expected="water glistens on the stone steps",
            )
        self.assertEqual(result[2], "pass")
        pass_event = next(event for event in events if event["event"] == "qc_pass")
        for field, value in values.items():
            self.assertEqual(pass_event[field], value)


class CachedPassTests(unittest.TestCase):
    def test_pass_recorded_before_enforcement_does_not_satisfy_new_field(self):
        digest = "b" * 64
        old_pass = {
            "event": "qc_pass", "episode": 25, "shot": 2,
            "content_sha256": digest,
        }
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            (root / "qc_log.jsonl").write_text(json.dumps(old_pass) + "\n", encoding="utf-8")
            with mock.patch.object(critic, "data_dir", return_value=root):
                self.assertFalse(critic.qc_pass_exists(
                    "unnatural-lab", 25, 2, digest,
                    {"enforce": {"violation_reads": True}},
                ))


class ReferenceStalenessTests(unittest.TestCase):
    """Descriptor veya anomali degisirse kayitli referans BAYAT sayilir."""

    @staticmethod
    def _object_calls(gen):
        return [c for c in gen.call_args_list if "object_ref" in c.args]

    def _ensure(self, plan, tmp, name="plan.json"):
        plan_path = tmp / name
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        bible = Bible.load("unnatural-lab")
        with mock.patch.object(produce, "_generate_uploaded_reference",
                               return_value="https://i.ibb.co/new/ref.png") as gen:
            ok = produce.ensure_episode_refs(
                bible, plan, plan_path, output_area=tmp
            )
        return ok, gen, json.loads(plan_path.read_text(encoding="utf-8"))

    def test_matching_hash_reuses_the_existing_reference(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            seed = unnatural_plan()
            seed.pop("prop_ref_urls", None)
            seed.pop("ref_prompt_sha256", None)
            ok, gen, saved = self._ensure(seed, tmp, "seed.json")
            self.assertTrue(ok)
            self.assertEqual(len(self._object_calls(gen)), 1)
            good_hash = saved["ref_prompt_sha256"]

            plan = unnatural_plan()
            plan["prop_ref_urls"] = ["https://i.ibb.co/old/ref.png"]
            plan["ref_prompt_sha256"] = good_hash
            ok, gen, saved = self._ensure(plan, tmp)
            self.assertTrue(ok)
            self.assertEqual(self._object_calls(gen), [])
            self.assertEqual(saved["prop_ref_urls"], ["https://i.ibb.co/old/ref.png"])

    def test_generation_model_identity_invalidates_the_reference(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            seed = unnatural_plan()
            seed.pop("prop_ref_urls", None)
            seed.pop("ref_prompt_sha256", None)
            ok, _, saved = self._ensure(seed, tmp, "seed.json")
            self.assertTrue(ok)

            plan = unnatural_plan()
            plan["prop_ref_urls"] = ["https://i.ibb.co/old/ref.png"]
            plan["ref_prompt_sha256"] = saved["ref_prompt_sha256"]
            with mock.patch.object(produce, "REFERENCE_IMAGE_MODEL", "future-image-model"):
                ok, gen, _ = self._ensure(plan, tmp)
            self.assertTrue(ok)
            self.assertEqual(len(self._object_calls(gen)), 1)

    def test_shot_level_reference_override_must_match_plan(self):
        plan = unnatural_plan()
        plan["prop_ref_urls"] = ["https://i.ibb.co/plan/ref.png"]
        plan["shots"][0]["prop_ref_urls"] = ["https://i.ibb.co/shot/ref.png"]
        errors = format_plan_errors(plan, Bible.load("unnatural-lab"))
        self.assertTrue(any("plan düzeyi listeyle birebir" in error for error in errors), errors)

    def test_changed_prompt_invalidates_the_reference(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            plan = unnatural_plan()
            plan["prop_ref_urls"] = ["https://i.ibb.co/old/ref.png"]
            plan["ref_prompt_sha256"] = hashlib.sha256(b"eski-prompt").hexdigest()
            ok, gen, saved = self._ensure(plan, tmp)
            self.assertTrue(ok)
            self.assertEqual(len(self._object_calls(gen)), 1)
            self.assertEqual(saved["prop_ref_urls"], ["https://i.ibb.co/new/ref.png"])
            self.assertNotEqual(saved["ref_prompt_sha256"],
                                hashlib.sha256(b"eski-prompt").hexdigest())

    def test_reference_prompt_shows_the_anomaly(self):
        captured = {}

        def capture(bible, prompt, *args, **kwargs):
            if "object_ref" in args:
                captured["prompt"] = prompt
            return "https://i.ibb.co/new/ref.png"

        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            plan = unnatural_plan()
            plan.pop("prop_ref_urls", None)
            plan.pop("ref_prompt_sha256", None)
            plan_path = tmp / "plan.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            with mock.patch.object(produce, "_generate_uploaded_reference", side_effect=capture):
                produce.ensure_episode_refs(
                    Bible.load("unnatural-lab"), plan, plan_path, output_area=tmp
                )
        self.assertIn(plan["object_card"]["anomaly_descriptor"], captured.get("prompt", ""))


class EnvironmentNeutralityTests(unittest.TestCase):
    """B9: paylasilan prompt yuzeylerinde atolye dili kalmadi."""

    def test_bathroom_qc_reference_and_regeneration_surfaces_have_no_bench_language(self):
        bible = Bible.load("unnatural-lab")
        plan = unnatural_plan(23)
        shot = plan["shots"][2]
        card = plan["object_card"]
        qc_surface = "\n".join((
            critic._QC_SYSTEM,
            critic._CONTINUITY_QC_ADDENDUM,
            critic._anomaly_addendum(card["anomaly_descriptor"]),
            critic._violation_addendum(shot["violation_observation"]),
            critic._state_carry_addendum(plan["shots"][1]["state_carry"]),
            shot["prompt"],
            critic.qc_config(bible)["notes"],
        ))
        env = bible.get("environments", card["environment"])
        regen_surface = critic.strengthen_prompt(
            shot["prompt"], ["continuity and state mismatch"], structured=True,
            environment=env["desc"],
        )
        reference_surfaces = []

        def capture(_bible, prompt, *args, **kwargs):
            reference_surfaces.append(prompt)
            return "https://i.ibb.co/new/ref.png"

        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            plan_path = tmp / "plan.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            with mock.patch.object(produce, "_generate_uploaded_reference", side_effect=capture):
                self.assertTrue(produce.ensure_episode_refs(
                    bible, plan, plan_path, output_area=tmp
                ))

        surfaces = {"qc": qc_surface, "regeneration": regen_surface}
        surfaces.update({f"reference-{index}": value
                         for index, value in enumerate(reference_surfaces, start=1)})
        for name, surface in surfaces.items():
            with self.subTest(surface=name):
                self.assertNotRegex(surface.lower(), r"\b(?:workbench|bench)\b")

    def test_environmentless_regeneration_keeps_legacy_bytes(self):
        expected = (
            "Continue from the established bench, lighting, object position, and "
            "transformation state shown in the previous shot."
        )
        self.assertEqual(critic.positive_correction("continuity mismatch"), expected)

    def test_series_qc_notes_are_environment_neutral(self):
        data = json.loads(
            (REPO / "sentinal_ihsan" / "unnatural-lab" / "bible.json").read_text(encoding="utf-8")
        )
        self.assertNotIn("bench", data["series"]["qc"]["notes"].lower())

    def test_bathroom_episode_uses_its_own_room(self):
        plan = unnatural_plan(23)
        self.assertEqual(plan["object_card"]["environment"], "bathroom_sink")
        env = Bible.load("unnatural-lab").get("environments", "bathroom_sink")
        self.assertIn("bathroom", str(env.get("desc", "")).lower())


if __name__ == "__main__":
    unittest.main()
