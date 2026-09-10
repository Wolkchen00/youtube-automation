"""
Tests for series.replenish.validate_title_card year exemption logic.
"""

import unittest
from series.bible import Bible
from series.replenish import validate_title_card


class TitleCardYearExemptionTest(unittest.TestCase):
    """Validate the year-free title card contract and legacy defaults."""

    def test_year_free_card_is_accepted_when_year_is_not_required(self):
        bible = Bible({
            "series": {
                "slug": "event-horizon",
                "title_card": {"enabled": True, "year_required": False},
            }
        })
        plan = {
            "title_card": {
                "title": "WASP-12b",
                "subtitle": "Its star is devouring it",
            }
        }
        errors = validate_title_card(bible, plan, required=False)
        self.assertEqual(errors, [])

    def test_year_free_card_is_rejected_under_the_legacy_default(self):
        bible = Bible({
            "series": {
                "slug": "event-horizon",
                "title_card": {"enabled": True},  # no year_required key
            }
        })
        plan = {
            "title_card": {
                "title": "WASP-12b",
                "subtitle": "Its star is devouring it",
            }
        }
        errors = validate_title_card(bible, plan, required=False)
        self.assertNotEqual(errors, [], "Legacy default must require a year")

    def test_length_contract_is_tighter_when_year_is_not_required(self):
        bible = Bible({
            "series": {
                "slug": "event-horizon",
                "title_card": {"enabled": True, "year_required": False},
            }
        })

        # 41 char title -> rejected
        plan = {"title_card": {"title": "A" * 41, "subtitle": "ok"}}
        errors = validate_title_card(bible, plan, required=False)
        self.assertNotEqual(errors, [], "41-char title must be rejected")

        # 40 char title -> accepted
        plan = {"title_card": {"title": "A" * 40, "subtitle": "ok"}}
        errors = validate_title_card(bible, plan, required=False)
        self.assertEqual(errors, [], "40-char title must be accepted")

        # 49 char subtitle -> rejected
        plan = {"title_card": {"title": "ok", "subtitle": "A" * 49}}
        errors = validate_title_card(bible, plan, required=False)
        self.assertNotEqual(errors, [], "49-char subtitle must be rejected")

        # 48 char subtitle -> accepted
        plan = {"title_card": {"title": "ok", "subtitle": "A" * 48}}
        errors = validate_title_card(bible, plan, required=False)
        self.assertEqual(errors, [], "48-char subtitle must be accepted")

    def test_missing_or_blank_fields_are_always_rejected(self):
        bible = Bible({
            "series": {
                "slug": "event-horizon",
                "title_card": {"enabled": True, "year_required": False},
            }
        })

        # empty title
        plan = {"title_card": {"title": "", "subtitle": "ok"}}
        errors = validate_title_card(bible, plan, required=False)
        self.assertNotEqual(errors, [], "Empty title must be rejected")

        # empty subtitle
        plan = {"title_card": {"title": "ok", "subtitle": ""}}
        errors = validate_title_card(bible, plan, required=False)
        self.assertNotEqual(errors, [], "Empty subtitle must be rejected")

        # no title_card key at all, required=True
        plan = {}
        errors = validate_title_card(bible, plan, required=True)
        self.assertNotEqual(errors, [], "Missing title_card with required=True must be rejected")

    def test_flashpoints_era_anchor_still_works(self):
        # flashpoints with legacy config (year_required absent/True) and era anchor
        bible = Bible({
            "series": {
                "slug": "flashpoints",
                "title_card": {"enabled": True},  # legacy default
            }
        })
        plan = {"title_card": {"title": "Pompeii", "subtitle": "AD 79"}}
        errors = validate_title_card(bible, plan, required=False)
        self.assertEqual(errors, [], "flashpoints era anchor must be accepted")

        # non-flashpoints slug with same card -> rejected
        bible2 = Bible({
            "series": {
                "slug": "event-horizon",
                "title_card": {"enabled": True},
            }
        })
        errors = validate_title_card(bible2, plan, required=False)
        self.assertNotEqual(errors, [], "Non-flashpoints must reject era anchor without year")

    def test_required_needs_an_enabled_title_card(self):
        # bible with no title_card at all
        bible = Bible({"series": {"slug": "event-horizon"}})
        plan = {"title_card": {"title": "X", "subtitle": "Y"}}
        errors = validate_title_card(bible, plan, required=True)
        self.assertNotEqual(errors, [], "required=True with no title_card must error")


if __name__ == "__main__":
    unittest.main()