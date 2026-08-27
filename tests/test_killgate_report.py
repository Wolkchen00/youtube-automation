"""Kill-gate olcumu: esikler, olgunluk reddi ve alarm.

En onemli davranis, karar VERMEYI reddedebilmesidir: eksik ya da olgunlasmamis veriyle
uretilen bir kill-gate karari, kanali ya haksiz oldurur ya da bos yere yasatir.
"""

import pathlib
import sys
import unittest
from datetime import date, datetime, timedelta, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core import killgate


def snapshot(day: date, channel: str, videos: dict) -> tuple[date, dict]:
    return day, {"channels": {channel: {"videos": videos}}}


def episode(video_id, likes, comments, views=1000, published=None, reason=None,
            measured_at=None):
    return killgate.EpisodeMetric(
        video_id=video_id,
        published=published or datetime(2026, 8, 1, tzinfo=timezone.utc),
        views=views, likes=likes, comments=comments,
        measured_at=measured_at or date(2026, 8, 4), reason=reason,
    )


class MeasurementTests(unittest.TestCase):
    CHANNEL = "sentinal"

    def test_uses_the_first_snapshot_after_72_hours(self):
        published = datetime(2026, 8, 1, 6, tzinfo=timezone.utc)
        snapshots = [
            snapshot(date(2026, 8, 2), self.CHANNEL, {"v1": {"views": 100, "likes": 1, "comments": 0}}),
            snapshot(date(2026, 8, 4), self.CHANNEL, {"v1": {"views": 1000, "likes": 45, "comments": 2}}),
            snapshot(date(2026, 8, 6), self.CHANNEL, {"v1": {"views": 4000, "likes": 90, "comments": 9}}),
        ]
        metric = killgate.measure_episode(snapshots, self.CHANNEL, "v1", published)
        self.assertEqual((metric.views, metric.likes, metric.comments), (1000, 45, 2))
        self.assertEqual(metric.measured_at, date(2026, 8, 4))
        self.assertAlmostEqual(metric.likes_per_1k, 45.0)
        self.assertAlmostEqual(metric.comments_per_1k, 2.0)

    def test_missing_snapshot_is_immature_not_zero(self):
        published = datetime(2026, 8, 1, tzinfo=timezone.utc)
        metric = killgate.measure_episode([], self.CHANNEL, "v1", published)
        self.assertFalse(metric.mature)
        self.assertEqual(metric.reason, "olgunlasmadi")
        self.assertIsNone(metric.likes_per_1k)

    def test_snapshot_gap_beyond_seven_days_is_rejected(self):
        published = datetime(2026, 8, 1, tzinfo=timezone.utc)
        snapshots = [snapshot(date(2026, 8, 20), self.CHANNEL,
                              {"v1": {"views": 900, "likes": 40, "comments": 1}})]
        metric = killgate.measure_episode(snapshots, self.CHANNEL, "v1", published)
        self.assertEqual(metric.reason, "gec_snapshot")

    def test_zero_views_is_unmeasurable_not_zero_ratio(self):
        published = datetime(2026, 8, 1, tzinfo=timezone.utc)
        snapshots = [snapshot(date(2026, 8, 4), self.CHANNEL,
                              {"v1": {"views": 0, "likes": 0, "comments": 0}})]
        metric = killgate.measure_episode(snapshots, self.CHANNEL, "v1", published)
        self.assertFalse(metric.mature)
        self.assertEqual(metric.reason, "izlenme_yok")
        self.assertIsNone(metric.likes_per_1k)


class VerdictTests(unittest.TestCase):
    def build(self, episodes, window=10):
        return killgate.build_report(episodes, window=window)

    def test_refuses_to_decide_on_a_short_window(self):
        report = self.build([episode(f"v{i}", 40, 2) for i in range(9)])
        self.assertEqual(report.verdict, "karar_yok")
        self.assertTrue(any("pencere dolmadi" in r for r in report.reasons))

    def test_refuses_to_decide_when_an_episode_is_immature(self):
        episodes = [episode(f"v{i}", 40, 2) for i in range(9)]
        episodes.append(episode("v9", None, None, views=None, reason="olgunlasmadi"))
        report = self.build(episodes)
        self.assertEqual(report.verdict, "karar_yok")
        self.assertTrue(any("olgun olcum 9/10" in r for r in report.reasons))

    def test_kill_below_ten_likes_per_1k(self):
        report = self.build([episode(f"v{i}", 9, 1) for i in range(10)])
        self.assertEqual(report.verdict, "oldur")

    def test_middle_band_between_ten_and_thirty(self):
        report = self.build([episode(f"v{i}", 15, 1) for i in range(10)])
        self.assertEqual(report.verdict, "ara_bant")

    def test_success_requires_both_thresholds(self):
        report = self.build([episode(f"v{i}", 35, 2) for i in range(10)])
        self.assertEqual(report.verdict, "basari")

    def test_high_likes_but_dead_comments_is_not_success(self):
        report = self.build([episode(f"v{i}", 40, 0) for i in range(10)])
        self.assertEqual(report.verdict, "ara_bant")
        self.assertTrue(report.comment_alarm)
        self.assertTrue(any("YORUM ALARMI" in r for r in report.reasons))

    def test_boundaries_are_inclusive_as_written_in_the_plan(self):
        exactly_ten = self.build([episode(f"v{i}", 10, 1) for i in range(10)])
        self.assertEqual(exactly_ten.verdict, "ara_bant", "L/1k=10 oldurmemeli")
        exactly_thirty = self.build([episode(f"v{i}", 30, 1) for i in range(10)])
        self.assertEqual(exactly_thirty.verdict, "basari")
        alarm_edge = self.build([episode(f"v{i}", 40, 0.3 * 1000 / 1000) for i in range(10)])
        self.assertFalse(alarm_edge.comment_alarm, "C/1k=0.3 alarm esiginde alarm vermemeli")

    def test_report_text_names_the_refusal(self):
        report = self.build([episode("v0", 40, 2)])
        text = killgate.format_report(report, series="unnatural-lab")
        self.assertIn("KARAR: karar_yok", text)
        self.assertIn("pencere dolmadi", text)


if __name__ == "__main__":
    unittest.main()
