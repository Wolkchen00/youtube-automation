"""Seri bazli QC anahtari onceligi ve gizlilik kanitlari."""

import logging
import pathlib
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from series import critic


class PerSeriesKeyResolutionTests(unittest.TestCase):
    def setUp(self):
        critic._QC_KEY_SOURCE_LOGGED = False

    def test_per_series_key_is_chosen_and_only_source_name_is_logged(self):
        secret = "sentinal-seri-gizli-anahtari"
        env = {
            "GEMINI_API_KEY_QC_UNNATURAL_LAB": secret,
            "GEMINI_API_KEY_QC": "filo-qc-anahtari",
        }
        with self.assertLogs("youtube", level=logging.INFO) as captured, \
                mock.patch.dict("os.environ", env, clear=True), \
                mock.patch.object(critic, "GEMINI_API_KEY", "uretim-anahtari"):
            result = critic._qc_api_key("unnatural-lab")

        self.assertEqual(
            result, (secret, "GEMINI_API_KEY_QC_UNNATURAL_LAB")
        )
        logged = "\n".join(captured.output)
        self.assertIn(
            "QC anahtar kaynagi: GEMINI_API_KEY_QC_UNNATURAL_LAB", logged
        )
        self.assertNotIn(secret, logged)
        self.assertNotIn("filo-qc-anahtari", logged)
        self.assertNotIn("uretim-anahtari", logged)

    def test_blank_per_series_key_falls_through_to_fleet_key(self):
        for blank in ("", "   "):
            with self.subTest(blank=repr(blank)), \
                    mock.patch.dict("os.environ", {
                        "GEMINI_API_KEY_QC_UNNATURAL_LAB": blank,
                        "GEMINI_API_KEY_QC": "filo-qc-anahtari",
                    }, clear=True):
                result = critic._qc_api_key("unnatural-lab")
            self.assertEqual(result, ("filo-qc-anahtari", "GEMINI_API_KEY_QC"))

    def test_absent_per_series_key_preserves_fleet_key_behaviour(self):
        with mock.patch.dict(
                "os.environ", {"GEMINI_API_KEY_QC": "filo-qc-anahtari"}, clear=True
        ):
            result = critic._qc_api_key("unnatural-lab")
        self.assertEqual(result, ("filo-qc-anahtari", "GEMINI_API_KEY_QC"))

    def test_absent_qc_keys_preserve_production_key_fallback(self):
        with mock.patch.dict("os.environ", {}, clear=True), \
                mock.patch.object(critic, "GEMINI_API_KEY", "uretim-anahtari"):
            result = critic._qc_api_key("unnatural-lab")
        self.assertEqual(result, ("uretim-anahtari", "GEMINI_API_KEY"))

    def test_slug_normalisation_keeps_digits_and_replaces_each_separator(self):
        cases = (
            ("unnatural-lab", "GEMINI_API_KEY_QC_UNNATURAL_LAB"),
            ("series-2", "GEMINI_API_KEY_QC_SERIES_2"),
            ("lab.-2", "GEMINI_API_KEY_QC_LAB__2"),
        )
        for slug, source in cases:
            with self.subTest(slug=slug), mock.patch.dict(
                    "os.environ", {source: "seri-anahtari"}, clear=True
            ):
                result = critic._qc_api_key(slug)
            self.assertEqual(result, ("seri-anahtari", source))

    def test_different_series_does_not_pick_up_another_series_key(self):
        with mock.patch.dict("os.environ", {
            "GEMINI_API_KEY_QC_UNNATURAL_LAB": "unnatural-gizli",
            "GEMINI_API_KEY_QC": "filo-qc-anahtari",
        }, clear=True):
            result = critic._qc_api_key("different-series")
        self.assertEqual(result, ("filo-qc-anahtari", "GEMINI_API_KEY_QC"))

    def test_visual_qc_threads_slug_to_key_resolution(self):
        with mock.patch.object(
                critic, "_qc_api_key", return_value=(None, "GEMINI_API_KEY")
        ) as resolve:
            with self.assertRaises(critic.QCApiExhausted):
                critic._review_frames(
                    [], None, "prompt", "notes",
                    slug="unnatural-lab", episode=22, shot=1,
                )
        resolve.assert_called_once_with("unnatural-lab")


if __name__ == "__main__":
    unittest.main()
