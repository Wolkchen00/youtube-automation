"""
Tests for the four queued plans (part32–part35) in event-horizon.
Their titles and title cards were rewritten by hand and must match the
approved table exactly.
"""

import json
import pathlib
import subprocess
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
PLANS_DIR = REPO_ROOT / "galactic_experience" / "event-horizon" / "plans"

# The approved table
APPROVED = {
    32: {
        "episode_title": "This Star Is EATING Its Own Planet",
        "card_title": "WASP-12b",
        "card_subtitle": "Its star is devouring it",
    },
    33: {
        "episode_title": "These Galaxies Are Leaving Us Forever",
        "card_title": "Cosmic expansion",
        "card_subtitle": "Distant galaxies leave our sky",
    },
    34: {
        "episode_title": "This Star Rips ATOMS Apart",
        "card_title": "Magnetar",
        "card_subtitle": "It pulls atoms apart",
    },
    35: {
        "episode_title": "This Moon Leaks Its OCEAN Into Space",
        "card_title": "Enceladus",
        "card_subtitle": "Its ocean escapes into space",
    },
}

# Keys that must NOT have changed from the baseline commit
IMMUTABLE_KEYS = (
    "synopsis",
    "narration",
    "shots",
    "family",
    "seed_id",
    "music",
    "hook_shot",
    "doctrine_sha256",
)

BASELINE_COMMIT = "9eec629"


class QueuedPlanTitleTest(unittest.TestCase):
    """Verify the four queued plans match the approved titles and cards."""

    def test_titles_and_cards_match_the_approved_table(self):
        for part in range(32, 36):
            with self.subTest(part=part):
                path = PLANS_DIR / f"part{part}.json"
                with path.open("r", encoding="utf-8") as f:
                    data = json.load(f)

                approved = APPROVED[part]
                self.assertEqual(data["episode"]["title"], approved["episode_title"])
                self.assertEqual(data["title_card"]["title"], approved["card_title"])
                self.assertEqual(data["title_card"]["subtitle"], approved["card_subtitle"])

    def test_cards_fit_the_event_horizon_length_contract(self):
        for part in range(32, 36):
            with self.subTest(part=part):
                path = PLANS_DIR / f"part{part}.json"
                with path.open("r", encoding="utf-8") as f:
                    data = json.load(f)

                card = data["title_card"]
                title = card["title"]
                subtitle = card["subtitle"]

                self.assertTrue(title, "title_card.title must be non-empty")
                self.assertLessEqual(len(title), 40, "title_card.title must be <= 40 chars")
                self.assertTrue(subtitle, "title_card.subtitle must be non-empty")
                self.assertLessEqual(len(subtitle), 48, "title_card.subtitle must be <= 48 chars")

    def test_titles_carry_no_emoji_or_hashtag_and_at_most_one_all_caps_word(self):
        for part in range(32, 36):
            with self.subTest(part=part):
                path = PLANS_DIR / f"part{part}.json"
                with path.open("r", encoding="utf-8") as f:
                    data = json.load(f)

                title = data["episode"]["title"]

                # No '#' character
                self.assertNotIn("#", title, "episode.title must not contain '#'")

                # All ASCII
                self.assertTrue(title.isascii(), "episode.title must be ASCII only")

                # At most ONE all-caps word
                # An ALL-CAPS word: whitespace-separated token, len > 1, only ASCII letters, equals its .upper()
                words = title.split()
                all_caps_count = 0
                for w in words:
                    if len(w) > 1 and w.isalpha() and w == w.upper():
                        all_caps_count += 1
                self.assertLessEqual(
                    all_caps_count,
                    1,
                    f"episode.title must have at most one ALL-CAPS word, found {all_caps_count}",
                )

    def test_titles_follow_the_anomaly_pattern(self):
        for part in range(32, 36):
            with self.subTest(part=part):
                path = PLANS_DIR / f"part{part}.json"
                with path.open("r", encoding="utf-8") as f:
                    data = json.load(f)

                title = data["episode"]["title"]
                self.assertTrue(
                    title.startswith("This ") or title.startswith("These "),
                    f"episode.title must start with 'This ' or 'These ', got: {title!r}",
                )

    def test_untouched_fields_still_match_the_baseline_commit(self):
        for part in range(32, 36):
            with self.subTest(part=part):
                # Current file
                current_path = PLANS_DIR / f"part{part}.json"
                with current_path.open("r", encoding="utf-8") as f:
                    current = json.load(f)

                # Baseline from git - force UTF-8 decoding to avoid mojibake on Windows
                result = subprocess.run(
                    [
                        "git",
                        "show",
                        f"{BASELINE_COMMIT}:galactic_experience/event-horizon/plans/part{part}.json",
                    ],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    encoding="utf-8",
                    check=True,
                )
                baseline = json.loads(result.stdout)

                # Assert immutable keys are byte-identical
                for key in IMMUTABLE_KEYS:
                    self.assertEqual(
                        current.get(key),
                        baseline.get(key),
                        f"Key {key!r} must not have changed from baseline",
                    )

                # Baseline must NOT have title_card
                self.assertNotIn("title_card", baseline, "Baseline must not have title_card")

                # Current MUST have title_card
                self.assertIn("title_card", current, "Current file must have title_card")


if __name__ == "__main__":
    unittest.main()