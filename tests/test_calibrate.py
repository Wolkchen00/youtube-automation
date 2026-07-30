"""FAZ 4 geri besleme halkasi icin tamamen agsiz sozlesme testleri."""

import copy
import hashlib
import json
import os
import pathlib
import re
import sys
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from unittest import mock

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from series import bible as bible_module
from series import calibrate, replenish
from series.bible import Bible
from series.series_meta import SeriesMeta


sys.stdout.reconfigure(encoding="utf-8")
REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]


def _bible(slug):
    return {
        "series": {
            "slug": slug,
            "title": slug,
            "aspect_ratio": "9:16",
            "resolution": "1080p",
            "engine": "omni",
            "chain_frames": False,
            "qc": {"enabled": True},
        },
        "art_style": "Photoreal vertical test footage.",
        "music": False,
        "characters": [],
        "environments": [],
        "props": [],
    }


def _plan(number, family="alpha", seed_id=None):
    plan = {
        "episode": {"number": number, "title": f"Test Episode {number}"},
        "synopsis": "A complete and exact test episode.",
        "hook_shot": 2,
        "narration": "",
        "family": family,
        "shots": [
            {
                "n": 1,
                "duration": "6",
                "prompt": "A detailed photoreal opening scene with continuous visible motion.",
                "seed": None,
            },
            {
                "n": 2,
                "duration": "6",
                "prompt": "A detailed photoreal closing scene that completes the visual loop.",
                "seed": None,
            },
        ],
    }
    if seed_id is not None:
        plan["seed_id"] = seed_id
    return plan


def _video(published, views):
    return {
        "title": "Fixture",
        "published": published,
        "views": views,
        "likes": 0,
        "comments": 0,
    }


def _snapshot(day, generated, channel, videos, other=None):
    channels = {channel: {"stats": {}, "videos": videos}}
    if other:
        channels.update(other)
    return date.fromisoformat(day), {"generated_at": generated, "channels": channels}


def _page(page_id, name="Approved topic", source="https://source.test", status="Onaylandı",
          claim_time=None, claim_token=""):
    return {
        "id": page_id,
        "properties": {
            "Name": {"title": [{"plain_text": name}]},
            "Kaynak": {"url": source},
            "Durum": {"select": {"name": status}},
            "Claim Zamani": {"date": {"start": claim_time} if claim_time else None},
            "Claim Kosu": {
                "rich_text": [{"plain_text": claim_token}] if claim_token else []
            },
        },
    }


class Phase4Fixture(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = pathlib.Path(self.tempdir.name)
        self.series_root = self.root / "galactic_experience"
        self.series_root.mkdir()
        self.search_roots = [self.series_root]
        patches = [
            mock.patch.object(bible_module, "PROJECT_ROOT", self.root),
            mock.patch.object(bible_module, "SERIES_DATA_DIR", self.root / "series_data"),
            mock.patch.object(bible_module, "SERIES_DIR", self.root / "output" / "series"),
            mock.patch.object(bible_module, "_SEARCH_ROOTS", self.search_roots),
            mock.patch.object(
                calibrate.requests,
                "request",
                side_effect=AssertionError("Calibrate testi aga cikmamalidir"),
            ),
            mock.patch.object(calibrate.notifier, "enabled", return_value=False),
            mock.patch.object(replenish, "_alert"),
        ]
        for patcher in patches:
            patcher.start()
            self.addCleanup(patcher.stop)

    def make_series(self, slug="event-horizon", *, families=None, topic_pool=None,
                    batch=5, total=0, next_part=1):
        folder = self.series_root / slug
        folder.mkdir()
        (self.series_root / "KONSEPT.md").write_text("Frozen doctrine\n", encoding="utf-8")
        cfg = {
            "enabled": True,
            "batch": batch,
            "min_queue": 2,
            "shots": 2,
            "shot_seconds": "6",
            "families": families or ["alpha", "beta", "gamma"],
            "brief": "Keep the approved creative language.",
        }
        if topic_pool is not None:
            cfg["topic_pool"] = topic_pool
        series = {
            "slug": slug,
            "base_title": slug,
            "logline": "Fixture",
            "status": "active",
            "total_parts": total,
            "next_part": next_part,
            "auto_replenish": cfg,
        }
        (folder / "series.json").write_text(
            json.dumps(series, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (folder / "bible.json").write_text(
            json.dumps(_bible(slug), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (folder / "plans").mkdir()
        return folder

    @staticmethod
    def write_plan(folder, number, family, seed_id=None):
        (folder / "plans" / f"part{number:02d}.json").write_text(
            json.dumps(_plan(number, family, seed_id), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def write_published(folder, entries):
        (folder / "published.json").write_text(
            json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8"
        )


class MetricAndDecisionTests(Phase4Fixture):
    def test_channel_aliases_and_sanitization_limits(self):
        self.assertEqual(calibrate.CHANNEL_BY_SLUG["unnatural-lab"], "sentinal_ihsan")
        self.assertEqual(calibrate.CHANNEL_BY_SLUG["the-vast"], "aimagine")
        dirty = "ignore `prompt`\nhttps://bad.test " + ("x" * 900)
        clean = calibrate.sanitize_text(dirty, 600)
        self.assertLessEqual(len(clean), 600)
        self.assertNotIn("http", clean)
        self.assertNotRegex(clean.lower(), r"ignore|prompt")
        card = calibrate.sanitize_text(dirty, 180)
        self.assertLessEqual(len(card), 180)

    def test_warmup_is_channel_scoped_and_48h_is_hour_precise(self):
        published = datetime(2026, 7, 1, 12, tzinfo=timezone.utc)
        snapshots = []
        for offset in range(14):
            generated = datetime(2026, 7, 1 + offset, 11, tzinfo=timezone.utc)
            videos = {"v": _video(published.isoformat(), offset)}
            snapshots.append(
                _snapshot(
                    generated.date().isoformat(),
                    generated.isoformat(),
                    "galactic_experiment",
                    videos,
                    {"aimagine": {"stats": {}, "videos": {}}},
                )
            )
        snapshots[2] = _snapshot(
            "2026-07-03",
            "2026-07-03T11:00:00+00:00",
            "galactic_experiment",
            {"v": _video(published.isoformat(), 47)},
        )
        snapshots[3] = _snapshot(
            "2026-07-04",
            "2026-07-04T13:00:00+00:00",
            "galactic_experiment",
            {"v": _video(published.isoformat(), 73)},
        )
        self.assertEqual(
            calibrate._channel_day_count(snapshots, "galactic_experiment"), 14
        )
        self.assertEqual(
            calibrate._first_48h_views(
                snapshots, "galactic_experiment", "v", published
            ),
            73,
        )
        self.assertIsNone(
            calibrate._first_48h_views(
                snapshots, "galactic_experiment", "missing", published
            )
        )

    def test_double_down_thresholds_and_disabled_median_reason(self):
        folder = self.make_series()
        self.write_plan(folder, 1, "alpha")
        self.write_plan(folder, 2, "beta")
        self.write_plan(folder, 3, "gamma")
        generated = datetime(2026, 7, 29, 12, tzinfo=timezone.utc)
        videos = {
            **{
                f"base{i}": _video("2026-07-20T00:00:00+00:00", 100)
                for i in range(10)
            },
            "five": _video("2026-07-26T12:00:00+00:00", 500),
            "young": _video("2026-07-27T12:06:00+00:00", 900),
            "low": _video("2026-07-26T12:00:00+00:00", 490),
        }
        self.write_published(folder, [
            {"part": 1, "ts": "2026-07-27T00:00:00Z", "results": {"youtube": "five"}},
            {"part": 2, "ts": "2026-07-28T00:00:00Z", "results": {"youtube": "young"}},
            {"part": 3, "ts": "2026-07-29T00:00:00Z", "results": {"youtube": "low"}},
        ])
        snapshots = [_snapshot("2026-07-29", generated.isoformat(),
                               "galactic_experiment", videos)]
        result, _ = calibrate._build_calibration(
            "event-horizon", SeriesMeta.load("event-horizon"), snapshots, {}, generated
        )
        self.assertEqual([item["video_id"] for item in result["double_down"]], ["five"])

        for video in videos.values():
            video["views"] = 0
        disabled, _ = calibrate._build_calibration(
            "event-horizon", SeriesMeta.load("event-horizon"), snapshots, {}, generated
        )
        self.assertEqual(disabled["double_down"], [])
        self.assertIn("kapali", disabled["pilot_kill"]["detail"])

    def test_boost_sort_cap_ties_and_explore_rules(self):
        families = ["a", "b", "c", "d", "e", "f"]
        published = [
            {"part": n, "ts": datetime(2026, 7, n, tzinfo=timezone.utc)}
            for n in range(1, 17)
        ]
        plans = [
            {"part": n, "family": "a" if n <= 2 else "b", "seed_id": n}
            for n in range(1, 17)
        ]
        self.assertEqual(
            calibrate._explore_family(families, published, plans), "a"
        )
        self.assertEqual(
            calibrate._explore_family(
                ["a", "b"], [], [{"part": 1, "family": "a"}]
            ),
            "b",
        )

        eligible = [
            {"family": "z", "n": 4, "median": 200.0},
            {"family": "a", "n": 4, "median": 200.0},
            {"family": "b", "n": 5, "median": 200.0},
            {"family": "c", "n": 3, "median": 190.0},
            {"family": "d", "n": 3, "median": 180.0},
            {"family": "too-small", "n": 2, "median": 999.0},
            {"family": "equal", "n": 3, "median": 100.0},
        ]
        self.assertEqual(
            calibrate._boost_families(eligible, 100.0), ["b", "a", "z", "c"]
        )
        self.assertEqual(calibrate._boost_families(eligible, None), [])

    def test_boost_rules_run_through_calibration_builder(self):
        families = ["a", "b", "c", "d", "e", "small", "equal", "unused"]
        folder = self.make_series(families=families)
        specs = (
            [("a", 200)] * 3
            + [("b", 200)] * 3
            + [("c", 200)] * 4
            + [("d", 190)] * 3
            + [("e", 180)] * 3
            + [("small", 999)] * 2
            + [("equal", 100)] * 3
        )
        videos = {
            f"base{i}": _video("2026-07-20T00:00:00+00:00", 100)
            for i in range(50)
        }
        registry = []
        for number, (family, views) in enumerate(specs, start=1):
            self.write_plan(folder, number, family)
            video_id = f"series{number}"
            videos[video_id] = _video("2026-07-20T00:00:00+00:00", views)
            registry.append({
                "part": number,
                "ts": f"2026-07-{min(number, 28):02d}T00:00:00Z",
                "results": {"youtube": video_id},
            })
        self.write_published(folder, registry)
        generated = datetime(2026, 7, 29, 12, tzinfo=timezone.utc)
        result, _ = calibrate._build_calibration(
            "event-horizon",
            SeriesMeta.load("event-horizon"),
            [_snapshot(
                "2026-07-29", generated.isoformat(),
                "galactic_experiment", videos
            )],
            {},
            generated,
        )
        self.assertEqual(result["channel_median_30d"], 100.0)
        self.assertEqual(
            result["recommendations"]["boost_families"], ["c", "a", "b", "d"]
        )

    def test_rollback_and_pilot_decisions(self):
        history, active = calibrate._rollback_history(
            {"rollback": {"history": [30.0, 20.0]}}, 10.0
        )
        self.assertEqual(history, [30.0, 20.0, 10.0])
        self.assertTrue(active)
        self.assertFalse(
            calibrate._rollback_history(
                {"rollback": {"history": [30.0, 30.0]}}, 10.0
            )[1]
        )
        self.assertFalse(
            calibrate._rollback_history(
                {"rollback": {"history": [30.0, None]}}, 10.0
            )[1]
        )
        self.assertFalse(
            calibrate._rollback_history(
                {"rollback": {"history": [30.0]}}, 10.0
            )[1]
        )
        decision = {
            "mode": "gecici_baseline",
            "series_stats": {
                "n_published": 4,
                "n_comparable": 4,
                "series_median": 10.0,
            },
            "rollback": {"active": True},
            "pilot_kill": {
                "triggered": True,
                "detail": "KARAR KARTI: pilot kanal medyaninin altinda",
            },
        }
        summary = calibrate._summary(
            "event_horizon",
            decision,
            ["Notion_error [bad] *oops* `raw`"],
        )
        self.assertIn("ROLLBACK", summary)
        self.assertIn("KARAR KARTI", summary)
        self.assertIn("gecici baseline", summary)
        self.assertIn(r"*event\_horizon*", summary)
        self.assertIn(r"Notion\_error \[bad\] \*oops\* \`raw\`", summary)
        self.assertNotRegex(summary, r"(?<!\\)_")

    def test_pilot_card_telegram_mock_and_comparable_floor(self):
        folder = self.make_series()
        videos = {
            **{
                f"base{i}": _video("2026-07-20T00:00:00+00:00", 100)
                for i in range(20)
            },
            **{
                f"series{i}": _video("2026-07-20T00:00:00+00:00", 10)
                for i in range(1, 5)
            },
        }
        registry = []
        for number in range(1, 5):
            self.write_plan(folder, number, ["alpha", "beta", "gamma"][number % 3])
            registry.append({
                "part": number,
                "ts": f"2026-07-2{number}T00:00:00Z",
                "results": {"youtube": f"series{number}"},
            })
        self.write_published(folder, registry)
        generated = datetime(2026, 7, 29, 12, tzinfo=timezone.utc)
        snapshots = [_snapshot(
            "2026-07-29", generated.isoformat(),
            "galactic_experiment", videos
        )]
        with mock.patch.object(calibrate.notifier, "enabled", return_value=True), \
                mock.patch.object(calibrate.notifier, "send_message") as send:
            result = calibrate.calibrate_series(
                "event-horizon", snapshots, notion_enabled=False,
                telegram_enabled=True, now=generated,
            )
        self.assertTrue(result["pilot_kill"]["triggered"])
        self.assertIn("KARAR KARTI", send.call_args.args[0])
        self.assertNotIn("_", send.call_args.args[0])
        videos.pop("series3")
        videos.pop("series4")
        low, _ = calibrate._build_calibration(
            "event-horizon", SeriesMeta.load("event-horizon"),
            snapshots, {}, generated,
        )
        self.assertFalse(low["pilot_kill"]["triggered"])

    def test_published_real_schema_duplicate_null_and_corruption(self):
        folder = self.make_series()
        self.write_published(folder, [
            {"part": 1, "ts": "2026-07-20T00:00:00Z",
             "results": {"youtube": "old"}},
            {"part": 1, "ts": "2026-07-21T00:00:00Z",
             "results": {"youtube": "new"}},
            {"part": 2, "ts": "2026-07-22T00:00:00Z",
             "results": {"youtube": None}},
        ])
        entries, notes = calibrate._load_published("event-horizon")
        self.assertEqual(entries[0]["video_id"], "new")
        self.assertTrue(any("part: 2" in note for note in notes))
        (folder / "published.json").write_text("{bad", encoding="utf-8")
        self.assertEqual(calibrate._load_published("event-horizon")[0], [])
        (folder / "published.json").unlink()
        self.assertEqual(calibrate._load_published("event-horizon")[0], [])

    def test_zero_data_writes_empty_calibration_and_preserves_read_only_inputs(self):
        folder = self.make_series()
        protected = [folder / "series.json", folder / "bible.json"]
        before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in protected}
        snapshots = [_snapshot(
            "2026-07-29", "2026-07-29T12:00:00+00:00",
            "galactic_experiment", {}
        )]
        result = calibrate.calibrate_series(
            "event-horizon", snapshots, notion_enabled=False,
            telegram_enabled=False,
            now=datetime(2026, 7, 29, 13, tzinfo=timezone.utc),
        )
        self.assertEqual(result["recommendations"]["empty_reason"], "veri_yok")
        self.assertEqual(result["brief_note"], "")
        self.assertTrue((folder / "calibration.json").is_file())
        after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in protected}
        self.assertEqual(before, after)

    def test_atomic_replace_failure_leaves_old_file_intact(self):
        path = self.root / "calibration.json"
        path.write_text('{"old": true}', encoding="utf-8")
        with mock.patch.object(calibrate.os, "replace", side_effect=OSError("boom")):
            with self.assertRaises(RuntimeError):
                calibrate._atomic_write(path, {"new": True})
        self.assertEqual(path.read_text(encoding="utf-8"), '{"old": true}')
        self.assertEqual(list(self.root.glob("*.tmp")), [])


class NotionBridgeTests(Phase4Fixture):
    def test_request_retries_429_and_5xx_with_timeout(self):
        class Response:
            def __init__(self, status, data=None):
                self.status_code = status
                self.ok = status == 200
                self.text = "retry"
                self._data = data or {}

            def json(self):
                return self._data

        responses = [Response(429), Response(500), Response(200, {"ok": True})]
        with mock.patch.object(
            calibrate.requests, "request", side_effect=responses
        ) as request, mock.patch.object(calibrate.time, "sleep"):
            self.assertEqual(
                calibrate._notion_request("GET", "databases/db", "token"),
                {"ok": True},
            )
        self.assertEqual(request.call_count, 3)
        self.assertTrue(all(call.kwargs["timeout"] == 20 for call in request.call_args_list))

    def test_query_pagination_and_schema_preserves_options(self):
        calls = []

        def fake(method, path, token, body=None):
            calls.append((method, path, body))
            if method == "GET":
                return {
                    "properties": {
                        "Durum": {
                            "select": {
                                "options": [
                                    {"name": "Onaylandi"},
                                    {"name": "Uretildi"},
                                ]
                            }
                        }
                    }
                }
            if path == "databases/db" and method == "PATCH":
                return {}
            if "query" in path:
                if body.get("start_cursor"):
                    return {"results": [{"id": "2"}], "has_more": False}
                return {"results": [{"id": "1"}], "has_more": True, "next_cursor": "next"}
            raise AssertionError((method, path, body))

        with mock.patch.object(calibrate, "_notion_request", side_effect=fake):
            names_by_role = calibrate._ensure_notion_schema("token", "db")
            pages = calibrate._query_pages("token", "db", "Onaylandi")
        self.assertEqual([page["id"] for page in pages], ["1", "2"])
        self.assertEqual(names_by_role, {
            "approved": "Onaylandi",
            "produced": "Uretildi",
            "claimed": "Claimed",
        })
        update = next(body for method, path, body in calls
                      if method == "PATCH" and path == "databases/db")
        names = [item["name"] for item in update["properties"]["Durum"]["select"]["options"]]
        self.assertEqual(names, ["Onaylandi", "Uretildi", "Claimed"])
        self.assertIn("Claim Zamani", update["properties"])
        self.assertIn("Claim Kosu", update["properties"])

    def test_bridge_cas_source_lease_produced_and_idempotence(self):
        self.make_series()
        old_id = "1" * 32
        new_id = "2" * 32
        foreign_id = "3" * 32
        missing_id = "4" * 32
        used_id = "n15-" + ("5" * 32)
        token = "run-77"
        now = datetime(2026, 7, 29, 12, tzinfo=timezone.utc)
        patched = []
        queried_statuses = []

        def fake(method, path, auth, body=None):
            if method == "GET" and path == "databases/db":
                return {
                    "properties": {
                        "Durum": {
                            "select": {
                                "options": [
                                    {"name": "Aday"},
                                    {"name": "Onaylandi"},
                                    {"name": "Reddedildi"},
                                    {"name": "Uretildi"},
                                    {"name": "Claimed"},
                                ]
                            }
                        },
                        "Claim Zamani": {"date": {}},
                        "Claim Kosu": {"rich_text": {}},
                    }
                }
            if method == "POST" and path.endswith("/query"):
                status = body["filter"]["select"]["equals"]
                queried_statuses.append(status)
                if status == "Claimed":
                    return {
                        "results": [_page(
                            old_id, status="Claimed",
                            claim_time=(now - timedelta(hours=25)).isoformat()
                        )],
                        "has_more": False,
                    }
                return {
                    "results": [
                        _page(new_id, status="Onaylandi"),
                        _page(foreign_id, status="Onaylandi"),
                        _page(missing_id, source="", status="Onaylandi"),
                    ],
                    "has_more": False,
                }
            if method == "PATCH" and path.startswith("pages/"):
                page_id = path.split("/", 1)[1]
                patched.append((page_id, body))
                status = body["properties"]["Durum"]["select"]["name"]
                if status == "Onaylandi":
                    return _page(page_id, status="Onaylandi")
                return _page(page_id, status=status, claim_token=token)
            if method == "GET" and path == f"pages/{new_id}":
                return _page(new_id, status="Claimed", claim_token=token)
            if method == "GET" and path == f"pages/{foreign_id}":
                return _page(foreign_id, status="Claimed", claim_token="other")
            if method == "GET" and path == f"pages/{old_id}":
                return _page(old_id, status="Claimed", claim_token=token)
            raise AssertionError((method, path, body))

        previous = [{
            "id": used_id,
            "topic": "Consumed",
            "page_id": "5" * 32,
            "claimed_at": now.isoformat(),
        }]
        env = {
            "NOTION_REELS_TOKEN": "token",
            "NOTION_TOPIC_DB_ID": "db",
            "GITHUB_RUN_ID": token,
        }
        with mock.patch.dict(os.environ, env, clear=False), mock.patch.object(
            calibrate, "_notion_request", side_effect=fake
        ):
            topics, notes = calibrate._bridge_notion(
                "event-horizon", previous, {used_id}, now, True
            )
        ids = {item["id"] for item in topics}
        self.assertIn("n15-" + old_id, ids)
        self.assertIn("n15-" + new_id, ids)
        self.assertNotIn("n15-" + foreign_id, ids)
        self.assertNotIn(used_id, ids)
        self.assertTrue(any("kaynaksiz kart" in note for note in notes))
        self.assertEqual(queried_statuses, ["Claimed", "Onaylandi"])
        produced_patch = next(body for page, body in patched if page == "5" * 32)
        self.assertEqual(
            produced_patch["properties"]["Durum"]["select"]["name"], "Uretildi"
        )

    def test_disabled_env_and_schema_drift_preserve_only_unconsumed(self):
        now = datetime(2026, 7, 29, tzinfo=timezone.utc)
        previous = [
            {"id": "n15-" + "1" * 32, "topic": "keep", "page_id": "1" * 32},
            {"id": "n15-" + "2" * 32, "topic": "drop", "page_id": "2" * 32},
        ]
        expected = [previous[0]]
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(
                calibrate._bridge_notion(
                    "event-horizon", previous, {previous[1]["id"]}, now, False
                )[0],
                expected,
            )
            topics, notes = calibrate._bridge_notion(
                "event-horizon", previous, {previous[1]["id"]}, now, True
            )
        self.assertEqual(topics, expected)
        self.assertTrue(any("env yok" in note for note in notes))
        with mock.patch.dict(
            os.environ,
            {"NOTION_REELS_TOKEN": "x", "NOTION_TOPIC_DB_ID": "db"},
            clear=True,
        ), mock.patch.object(
            calibrate, "_ensure_notion_schema",
            side_effect=calibrate.NotionHTTPError(400, "drift"),
        ):
            topics, notes = calibrate._bridge_notion(
                "event-horizon", previous, {previous[1]["id"]}, now, True
            )
        self.assertEqual(topics, expected)
        self.assertTrue(any("fail-closed" in note for note in notes))


class ReplenishCalibrationTests(Phase4Fixture):
    def write_calibration(self, folder, cards=None, brief="Measured brief."):
        data = {
            "version": 1,
            "brief_note": brief,
            "extra_topics": cards or [],
        }
        (folder / "calibration.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    @staticmethod
    def cards(count):
        return [
            {
                "id": f"n15-{number:032x}",
                "topic": f"Approved topic {number}",
                "page_id": f"{number:032x}",
                "claimed_at": "2026-07-29T00:00:00+00:00",
            }
            for number in range(1, count + 1)
        ]

    def test_prompt_note_card_first_and_missing_broken_fail_open(self):
        folder = self.make_series(topic_pool=[{"id": 1, "topic": "Int", "family": "alpha"}])
        cards = self.cards(1)
        calibration = {"brief_note": "Measured brief.", "extra_topics": cards}
        contents, system = replenish._build_prompt(
            SeriesMeta.load("event-horizon"), Bible.load("event-horizon"),
            SeriesMeta.load("event-horizon").auto_replenish,
            1, 1, [], calibration=calibration,
        )
        self.assertIn(
            "CALIBRATION (weekly measured audience feedback, follow unless it contradicts the brief):",
            contents,
        )
        self.assertLess(contents.index("RUNTIME APPROVED CARD TOPICS"),
                        contents.index("RUNTIME UNUSED TOPIC POOL"))
        self.assertIn("MUST be consumed first", system)
        self.assertEqual(dict(replenish._load_calibration("event-horizon")), {})
        (folder / "calibration.json").write_text("{bad", encoding="utf-8")
        self.assertEqual(dict(replenish._load_calibration("event-horizon")), {})
        self.write_calibration(folder, brief="")
        contents, _ = replenish._build_prompt(
            SeriesMeta.load("event-horizon"), Bible.load("event-horizon"),
            SeriesMeta.load("event-horizon").auto_replenish,
            1, 1, [], calibration=replenish._load_calibration("event-horizon"),
        )
        self.assertNotIn("\nCALIBRATION (", contents)

    def test_card_validator_quota_unknown_reuse_and_normalized_stamps(self):
        self.make_series(topic_pool=[])
        cards = self.cards(7)
        calibration = {"extra_topics": cards, "brief_note": ""}
        episodes = [
            _plan(i + 1, "alpha" if i % 2 == 0 else "beta", cards[i]["id"])
            for i in range(5)
        ]
        errors = replenish._validate_batch(
            episodes, Bible.load("event-horizon"), 1, 5, set(),
            SeriesMeta.load("event-horizon").auto_replenish, [], calibration,
        )
        self.assertEqual(errors, [])
        for plan, card in zip(episodes, cards):
            self.assertEqual(plan["seed_id"], card["id"])
            self.assertEqual(plan["card_page_id"], card["page_id"])
            self.assertEqual(plan["card_topic"], card["topic"])

        missing = [_plan(i + 1, "alpha" if i % 2 == 0 else "beta") for i in range(5)]
        errors = replenish._validate_batch(
            missing, Bible.load("event-horizon"), 1, 5, set(),
            SeriesMeta.load("event-horizon").auto_replenish, [], calibration,
        )
        self.assertTrue(any("farkli kart" in error for error in errors))
        unknown = [_plan(1, "alpha", "n15-" + "f" * 32)]
        errors = replenish._validate_batch(
            unknown, Bible.load("event-horizon"), 1, 1, set(),
            SeriesMeta.load("event-horizon").auto_replenish, [], calibration,
        )
        self.assertTrue(any("kart havuzunda yok" in error for error in errors))
        reused = [_plan(2, "beta", cards[0]["id"])]
        errors = replenish._validate_batch(
            reused, Bible.load("event-horizon"), 2, 1, set(),
            SeriesMeta.load("event-horizon").auto_replenish,
            [{"seed_id": cards[0]["id"], "family": "alpha"}], calibration,
        )
        self.assertTrue(any("daha once" in error for error in errors))

    def test_int_pool_empty_two_cards_effective_batch_and_single_load(self):
        folder = self.make_series(topic_pool=[], batch=5)
        cards = self.cards(2)
        self.write_calibration(folder, cards)
        self.write_plan(folder, 99, "gamma")
        existing_plan = folder / "plans" / "part99.json"
        existing_hash = hashlib.sha256(existing_plan.read_bytes()).hexdigest()
        response = {
            "episodes": [
                _plan(1, "alpha", cards[0]["id"]),
                _plan(2, "beta", cards[1]["id"]),
            ]
        }
        original_series = json.loads((folder / "series.json").read_text(encoding="utf-8"))
        with mock.patch.object(
            replenish, "_load_calibration", wraps=replenish._load_calibration
        ) as loader, mock.patch.object(
            replenish, "_gen_json", return_value=response
        ):
            self.assertTrue(replenish.replenish("event-horizon"))
        loader.assert_called_once_with("event-horizon")
        self.assertTrue((folder / "plans" / "part01.json").is_file())
        self.assertTrue((folder / "plans" / "part02.json").is_file())
        self.assertEqual(
            hashlib.sha256(existing_plan.read_bytes()).hexdigest(), existing_hash
        )
        updated = json.loads((folder / "series.json").read_text(encoding="utf-8"))
        self.assertEqual(updated["total_parts"], 2)
        self.assertEqual(updated["next_part"], original_series["next_part"])
        expected_cfg = copy.deepcopy(original_series["auto_replenish"])
        expected_cfg["last_run"] = updated["auto_replenish"]["last_run"]
        self.assertEqual(updated["auto_replenish"], expected_cfg)
        for name in original_series:
            if name not in {"total_parts", "auto_replenish"}:
                self.assertEqual(updated[name], original_series[name])


class WorkflowAndCliTests(unittest.TestCase):
    def test_workflow_static_contract(self):
        path = REPO_ROOT / ".github" / "workflows" / "calibrate.yml"
        raw = path.read_text(encoding="utf-8")
        workflow = yaml.load(raw, Loader=yaml.BaseLoader)
        self.assertEqual(workflow["on"]["schedule"][0]["cron"], "0 9 * * 0")
        self.assertEqual(workflow["concurrency"]["group"], "kie-uretim")
        self.assertEqual(workflow["permissions"]["contents"], "write")
        # FAZ 7 M1 (2026-07-30): persist ortak scripts/persist_state.sh betigine tasindi;
        # sozlesme artik betik cagrisinin 4 kalibrasyon glob'unu arguman tasimasi.
        self.assertIn("bash scripts/persist_state.sh", raw)
        staged = re.findall(r"^\s*'([^']*calibration\.json)' \\?$", raw, re.MULTILINE)
        self.assertEqual(staged, [
            "sentinal_ihsan/*/calibration.json",
            "aimagine/*/calibration.json",
            "galactic_experience/*/calibration.json",
            "shadowedhistory/*/calibration.json",
        ])
        self.assertNotIn("git add ", raw)
        self.assertNotIn("FFmpeg", raw)
        self.assertNotIn("GEMINI_API_KEY", raw)
        self.assertIn("python -X utf8 -m series.calibrate", raw)

    def test_cli_local_default_and_explicit_flags(self):
        snapshot = _snapshot(
            "2026-07-29", "2026-07-29T12:00:00+00:00",
            "galactic_experiment", {}
        )
        with mock.patch.object(calibrate, "load_snapshots", return_value=[snapshot]), \
                mock.patch.object(calibrate, "_eligible_slugs", return_value=["event-horizon"]), \
                mock.patch.object(calibrate, "calibrate_series", return_value={}) as run, \
                mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(calibrate.main(["--no-telegram"]), 0)
            self.assertFalse(run.call_args.kwargs["notion_enabled"])
            self.assertFalse(run.call_args.kwargs["telegram_enabled"])
        with mock.patch.object(calibrate, "load_snapshots", return_value=[snapshot]), \
                mock.patch.object(calibrate, "_eligible_slugs", return_value=["event-horizon"]), \
                mock.patch.object(calibrate, "calibrate_series", return_value={}) as run, \
                mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(calibrate.main(["--notion"]), 0)
            self.assertTrue(run.call_args.kwargs["notion_enabled"])


class InstalledReadOnlyInvariantTests(unittest.TestCase):
    def test_calibrate_never_mutates_concepts_series_plans_or_published(self):
        series = {
            "unnatural-lab": REPO_ROOT / "sentinal_ihsan" / "unnatural-lab",
            "from-scratch": REPO_ROOT / "aimagine" / "from-scratch",
            "event-horizon": REPO_ROOT / "galactic_experience" / "event-horizon",
            "flashpoints": REPO_ROOT / "shadowedhistory" / "flashpoints",
        }
        protected = [
            REPO_ROOT / "sentinal_ihsan" / "KONSEPT.md",
            REPO_ROOT / "aimagine" / "KONSEPT.md",
            REPO_ROOT / "galactic_experience" / "KONSEPT.md",
            REPO_ROOT / "shadowedhistory" / "KONSEPT.md",
        ]
        for folder in series.values():
            protected.append(folder / "series.json")
            protected.extend(sorted((folder / "plans").glob("part*.json")))
            if (folder / "published.json").exists():
                protected.append(folder / "published.json")
        before = {
            path: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in protected
        }
        channels = {
            channel: {"stats": {}, "videos": {}}
            for channel in set(calibrate.CHANNEL_BY_SLUG.values())
        }
        snapshots = [(
            date(2026, 7, 29),
            {
                "generated_at": "2026-07-29T12:00:00+00:00",
                "channels": channels,
            },
        )]
        with mock.patch.object(calibrate, "_atomic_write") as write:
            for slug in series:
                calibrate.calibrate_series(
                    slug,
                    snapshots,
                    notion_enabled=False,
                    telegram_enabled=False,
                    now=datetime(2026, 7, 29, 13, tzinfo=timezone.utc),
                )
        self.assertEqual(write.call_count, 4)
        after = {
            path: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in protected
        }
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
