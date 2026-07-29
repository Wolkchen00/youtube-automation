"""Snapshot tabanlı analitik raporu için ağsız testler."""

import json
import pathlib
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core import analytics
from series import notifier


sys.stdout.reconfigure(encoding="utf-8")


class AnalyticsReportTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.data_dir = pathlib.Path(self.tempdir.name) / "analytics_data"
        self.daily_dir = self.data_dir / "daily"
        self.daily_dir.mkdir(parents=True)

        data_patch = mock.patch.object(analytics, "DATA_DIR", self.data_dir)
        data_patch.start()
        self.addCleanup(data_patch.stop)
        network_patch = mock.patch.object(
            analytics.requests,
            "get",
            side_effect=AssertionError("Rapor testi ağ isteği yapmamalı"),
        )
        network_patch.start()
        self.addCleanup(network_patch.stop)
        telegram_patch = mock.patch.object(notifier, "enabled", return_value=False)
        telegram_patch.start()
        self.addCleanup(telegram_patch.stop)

        self._write_fixture_snapshots()

    @staticmethod
    def _video(title, published, views):
        return {
            "title": title,
            "published": published,
            "views": views,
            "likes": 1,
            "comments": 1,
        }

    def _write_snapshot(self, day, generated_at, videos):
        snapshot = {
            "generated_at": generated_at,
            "channels": {
                "shadowedhistory": {
                    "stats": {
                        "subs": 123,
                        "total_views": 4567,
                        "total_videos": len(videos),
                    },
                    "videos": videos,
                }
            },
        }
        (self.daily_dir / f"{day}.json").write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _write_fixture_snapshots(self):
        old_published = "2026-07-20T13:00:00+00:00"
        mature_published = "2026-07-24T06:00:00+00:00"
        young_published = "2026-07-26T18:00:00+00:00"

        self._write_snapshot(
            "2026-07-20",
            "2026-07-20T12:00:00+00:00",
            {"old": self._video("Eski video", old_published, 10)},
        )
        self._write_snapshot(
            "2026-07-22",
            "2026-07-22T12:00:00+00:00",
            {"old": self._video("Eski video", old_published, 120)},
        )
        self._write_snapshot(
            "2026-07-25",
            "2026-07-25T12:00:00+00:00",
            {
                "old": self._video("Eski video", old_published, 250),
                "mature": self._video("Olgun video", mature_published, 80),
            },
        )
        self._write_snapshot(
            "2026-07-27",
            "2026-07-27T12:00:00+00:00",
            {
                "old": self._video("Eski video", old_published, 300),
                "mature": self._video("Olgun video", mature_published, 100),
                "young": self._video("Yeni video", young_published, 10000),
            },
        )

    def _report(self):
        return analytics.generate_weekly_report(
            now=datetime(2026, 7, 27, 13, 0, tzinfo=timezone.utc)
        )

    def _video_from_report(self, report, video_id):
        videos = report["channels"]["shadowedhistory"]["videos_last_7_days"]
        return next(video for video in videos if video["video_id"] == video_id)

    def test_views_48h_uses_first_snapshot_on_or_after_two_days(self):
        report = self._report()
        old_video = self._video_from_report(report, "old")
        self.assertEqual(old_video["views"], 300)
        self.assertEqual(old_video["views_48h"], 120)
        self.assertIsNone(old_video["views_48h_reason"])

    def test_views_48h_is_warmup_when_history_is_insufficient(self):
        report = self._report()
        young_video = self._video_from_report(report, "young")
        self.assertIsNone(young_video["views_48h"])
        self.assertEqual(young_video["views_48h_reason"], "warmup")

    def test_30_day_median_excludes_videos_younger_than_48_hours(self):
        report = self._report()
        channel = report["channels"]["shadowedhistory"]
        self.assertEqual(channel["views_30d_median"], 200.0)

    def test_json_and_markdown_reports_are_written(self):
        self._report()
        json_path = self.data_dir / "weekly_2026-07-27.json"
        markdown_path = self.data_dir / "weekly_2026-07-27.md"
        self.assertTrue(json_path.is_file())
        self.assertTrue(markdown_path.is_file())
        self.assertIn(
            "shadowedhistory",
            json.loads(json_path.read_text(encoding="utf-8"))["channels"],
        )
        self.assertIn(
            "# Haftalık YouTube Raporu",
            markdown_path.read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
