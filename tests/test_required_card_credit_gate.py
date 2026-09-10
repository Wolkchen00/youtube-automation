"""
Tests for the early title_card guard in _produce_episode_impl.

The guard sits before ANY paid work: no shot is generated, no credit is spent.
It must fire for a plan whose required title card is missing or blank, and it
must accept a valid one and move on.
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from series.bible import Bible
from series.produce import produce_episode
from series.series_meta import SeriesMeta


class _ReachedPaidWork(Exception):
    """Raised to stop produce the moment it gets past the guard."""


def _make_bible() -> Bible:
    """Build a real Bible object with required_layers containing title_card."""
    return Bible({
        "series": {
            "slug": "guard-test",
            "title": "Guard Test",
            "engine": "seedance",
            "state_machine_version": 2,
            "required_layers": ["title_card"],
            "title_card": {"enabled": True, "year_required": False},
            "qc": {"enabled": True, "require_all_shots": True, "max_regens_per_shot": 0},
        },
        "music": False,
        "narration": {},
        "characters": [],
        "environments": [],
        "props": [],
    })


def _make_meta() -> SeriesMeta:
    """Build a real SeriesMeta with minimal dict (same shape as test_min_shots.py)."""
    return SeriesMeta({
        "slug": "guard-test",
        "base_title": "Guard Test",
        "total_parts": 1,
        "next_part": 1,
        "status": "active",
        "publish_mode": "auto",
        "upload_profile": "proof-profile",
        "platforms": ["youtube", "instagram"],
        "parts": {},
    })


def _base_plan() -> dict:
    """A minimal valid plan without title_card."""
    return {
        "episode": {"number": 1, "title": "Test Episode"},
        "shots": [
            {"n": 1, "duration": "6", "prompt": "shot 1"},
            {"n": 2, "duration": "6", "prompt": "shot 2"},
        ],
    }


class RequiredCardCreditGateTest(unittest.TestCase):

    def setUp(self):
        self.bible = _make_bible()
        self.meta = _make_meta()
        self.plan = _base_plan()

    @patch("series.produce.SeriesMeta.load")
    @patch("series.produce._doctrine_gate")
    @patch("series.produce.Bible.load")
    @patch("series.produce.check_credit")
    def test_missing_card_is_refused_before_any_paid_call(
        self, mock_check_credit, mock_bible_load, mock_doctrine_gate, mock_meta_load
    ):
        """Plan has no 'title_card' key at all. Guard must refuse and check_credit never called."""
        mock_meta_load.return_value = self.meta
        mock_doctrine_gate.return_value = "digest"
        mock_bible_load.return_value = self.bible

        result = produce_episode("guard-test", self.plan, typed_result=True)

        # Guard returns None internally, but produce_episode wraps it into ProduceResult("generation_fail")
        self.assertIsNotNone(result)
        self.assertEqual(result.status, "generation_fail")
        mock_check_credit.assert_not_called()

    @patch("series.produce.SeriesMeta.load")
    @patch("series.produce._doctrine_gate")
    @patch("series.produce.Bible.load")
    @patch("series.produce.check_credit")
    def test_blank_card_is_refused_before_any_paid_call(
        self, mock_check_credit, mock_bible_load, mock_doctrine_gate, mock_meta_load
    ):
        """Plan has blank title_card. Guard must refuse and check_credit never called."""
        mock_meta_load.return_value = self.meta
        mock_doctrine_gate.return_value = "digest"
        mock_bible_load.return_value = self.bible

        plan = dict(self.plan)
        plan["title_card"] = {"title": "", "subtitle": ""}

        result = produce_episode("guard-test", plan, typed_result=True)

        self.assertIsNotNone(result)
        self.assertEqual(result.status, "generation_fail")
        mock_check_credit.assert_not_called()

    @patch("series.produce.SeriesMeta.load")
    @patch("series.produce._doctrine_gate")
    @patch("series.produce.Bible.load")
    @patch("series.produce.check_credit")
    def test_oversized_card_is_refused(
        self, mock_check_credit, mock_bible_load, mock_doctrine_gate, mock_meta_load
    ):
        """Plan card title exceeds 40 chars (year_required=False). Guard must refuse."""
        mock_meta_load.return_value = self.meta
        mock_doctrine_gate.return_value = "digest"
        mock_bible_load.return_value = self.bible

        plan = dict(self.plan)
        plan["title_card"] = {"title": "A" * 41, "subtitle": "ok"}

        result = produce_episode("guard-test", plan, typed_result=True)

        self.assertIsNotNone(result)
        self.assertEqual(result.status, "generation_fail")
        mock_check_credit.assert_not_called()

    @patch("series.produce.SeriesMeta.load")
    @patch("series.produce._doctrine_gate")
    @patch("series.produce.Bible.load")
    @patch("series.produce.check_credit", side_effect=_ReachedPaidWork)
    @patch("series.replenish.validate_title_card")
    def test_valid_card_passes_the_guard(
        self, mock_validate_title_card, mock_check_credit, mock_bible_load,
        mock_doctrine_gate, mock_meta_load
    ):
        """Valid title_card passes the guard. Prove by asserting how the guard called the validator."""
        mock_meta_load.return_value = self.meta
        mock_doctrine_gate.return_value = "digest"
        mock_bible_load.return_value = self.bible

        # Make the mock return empty list (valid card)
        mock_validate_title_card.return_value = []

        plan = dict(self.plan)
        plan["title_card"] = {"title": "WASP-12b", "subtitle": "Its star is devouring it"}

        # We don't care what happens after the guard; just that the guard didn't stop it.
        # Reaching check_credit proves the guard let the episode through.
        with self.assertRaises(_ReachedPaidWork):
            produce_episode("guard-test", plan, typed_result=True)

        mock_validate_title_card.assert_called_once()
        # Prove the guard passed the real bible, the real plan card, and required=True
        args, kwargs = mock_validate_title_card.call_args
        self.assertIs(args[0], self.bible)
        self.assertEqual(args[1]["title_card"]["title"], "WASP-12b")
        self.assertTrue(kwargs.get("required"))

    @patch("series.produce.SeriesMeta.load")
    @patch("series.produce._doctrine_gate")
    @patch("series.produce.Bible.load")
    @patch("series.produce.check_credit", side_effect=_ReachedPaidWork)
    @patch("series.replenish.validate_title_card")
    def test_a_series_without_the_required_layer_never_consults_the_guard(
        self, mock_validate_title_card, mock_check_credit, mock_bible_load,
        mock_doctrine_gate, mock_meta_load
    ):
        """Bible has no 'required_layers' key. validate_title_card must NEVER be called."""
        # Bible without required_layers
        bible_no_required = Bible({
            "series": {
                "slug": "guard-test",
                "title": "Guard Test",
                "engine": "seedance",
                "state_machine_version": 2,
                # No required_layers key
                "title_card": {"enabled": True, "year_required": False},
                "qc": {"enabled": True, "require_all_shots": True, "max_regens_per_shot": 0},
            },
            "music": False,
            "narration": {},
            "characters": [],
            "environments": [],
            "props": [],
        })

        mock_meta_load.return_value = self.meta
        mock_doctrine_gate.return_value = "digest"
        mock_bible_load.return_value = bible_no_required

        # Reaching check_credit proves the guard let the episode through.
        with self.assertRaises(_ReachedPaidWork):
            produce_episode("guard-test", self.plan, typed_result=True)

        mock_validate_title_card.assert_not_called()

    @patch("series.produce.SeriesMeta.load")
    @patch("series.produce._doctrine_gate")
    @patch("series.produce.Bible.load")
    @patch("series.produce.check_credit")
    def test_plan_given_as_a_file_path_is_also_guarded(
        self, mock_check_credit, mock_bible_load, mock_doctrine_gate, mock_meta_load
    ):
        """Pass a JSON plan file path with BLANK title_card. Must be refused same way."""
        mock_meta_load.return_value = self.meta
        mock_doctrine_gate.return_value = "digest"
        mock_bible_load.return_value = self.bible

        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "part01.json"
            plan = dict(self.plan)
            plan["title_card"] = {"title": "", "subtitle": ""}
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            result = produce_episode("guard-test", str(plan_path), typed_result=True)

            self.assertIsNotNone(result)
            self.assertEqual(result.status, "generation_fail")
            mock_check_credit.assert_not_called()


if __name__ == "__main__":
    unittest.main()