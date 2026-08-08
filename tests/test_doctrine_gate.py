"""FAZ 3 doktrin kapısı ve seri sözleşmesi için ağsız testler."""

import copy
import hashlib
import json
import pathlib
import re
import sys
import tempfile
import types
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

# Narration register testi TTS SDK'sına gitmez; eksik opsiyonel SDK'yı importta ağsız taklit et.
google_package = sys.modules.setdefault("google", types.ModuleType("google"))
generativeai_module = types.ModuleType("google.generativeai")
sys.modules.setdefault("google.generativeai", generativeai_module)
setattr(google_package, "generativeai", generativeai_module)

from core import music_generator, narration
from series import bible as bible_module
from series import produce, replenish
from series.bible import Bible
from series.series_meta import SeriesMeta, part_plan_path


sys.stdout.reconfigure(encoding="utf-8")
REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]


def _digest(text):
    normalized = text.replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _bible(slug, narration_channel=None, title_card=False, hook=False):
    data = {
        "series": {
            "slug": slug,
            "title": slug,
            "aspect_ratio": "9:16",
            "resolution": "1080p",
            "engine": "omni",
            "chain_frames": False,
            "title_card": title_card,
            "hook_teaser": {"enabled": hook},
            "qc": {"enabled": True, "notes": "Network-free test."},
        },
        "art_style": "Photoreal vertical test footage.",
        "music": True,
        "characters": [],
        "environments": [],
        "props": [],
    }
    if narration_channel:
        data["narration"] = {"channel": narration_channel}
    return data


def _plan(number=1, words=22, family=None, seed_id=None, duration="6", stamp=None):
    plan = {
        "episode": {"number": number, "title": f"Valid Test Title {number}"},
        "synopsis": "One exact test subject rendered as a complete episode.",
        "hook_shot": 2,
        "narration": " ".join(f"word{i}" for i in range(words)),
        "shots": [
            {
                "n": 1,
                "duration": duration,
                "prompt": "A photoreal opening action with enough concrete visual detail for validation.",
                "seed": None,
            },
            {
                "n": 2,
                "duration": duration,
                "prompt": "A photoreal closing action that continues motion and creates a seamless loop.",
                "seed": None,
            },
        ],
    }
    if family is not None:
        plan["family"] = family
    if seed_id is not None:
        plan["seed_id"] = seed_id
    if stamp is not None:
        plan["doctrine_sha256"] = stamp
    return plan


class DoctrineGateTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = pathlib.Path(self.tempdir.name)
        self.series_data = self.root / "series_data"
        self.series_data.mkdir()
        self.search_roots = [self.series_data]

        patches = [
            mock.patch.object(bible_module, "PROJECT_ROOT", self.root),
            mock.patch.object(bible_module, "SERIES_DATA_DIR", self.series_data),
            mock.patch.object(bible_module, "SERIES_DIR", self.root / "output" / "series"),
            mock.patch.object(bible_module, "_SEARCH_ROOTS", self.search_roots),
            mock.patch.object(replenish, "_alert"),
        ]
        for patcher in patches:
            patcher.start()
            self.addCleanup(patcher.stop)

    def _make_series(
        self,
        slug,
        *,
        status="active",
        enabled=True,
        doctrine_text="Doctrine\n",
        pin=False,
        explicit=None,
        cfg=None,
    ):
        channel = self.root / f"channel_{slug}"
        self.search_roots.insert(0, channel)
        folder = channel / slug
        folder.mkdir(parents=True)
        if doctrine_text is not None:
            (channel / "KONSEPT.md").write_text(doctrine_text, encoding="utf-8")
        config = {
            "enabled": enabled,
            "batch": 1,
            "min_queue": 2,
            "shots": 2,
            "shot_seconds": "6",
        }
        if cfg:
            config.update(copy.deepcopy(cfg))
        data = {
            "slug": slug,
            "base_title": slug,
            "language": "en",
            "status": status,
            "total_parts": 0,
            "next_part": 1,
            "auto_replenish": config,
        }
        if explicit is not None:
            data["doctrine"] = explicit
        if pin:
            data["doctrine_sha256"] = _digest(doctrine_text or "")
        (folder / "series.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (folder / "bible.json").write_text(
            json.dumps(_bible(slug), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return folder

    def test_doctrine_path_channel_rule_explicit_priority_and_missing(self):
        folder = self._make_series("paths")
        self.assertEqual(bible_module.doctrine_path("paths"), folder.parent / "KONSEPT.md")
        explicit = self.root / "explicit.md"
        explicit.write_text("Explicit doctrine", encoding="utf-8")
        meta = json.loads((folder / "series.json").read_text(encoding="utf-8"))
        meta["doctrine"] = "explicit.md"
        (folder / "series.json").write_text(json.dumps(meta), encoding="utf-8")
        self.assertEqual(bible_module.doctrine_path("paths"), explicit)
        explicit.unlink()
        self.assertIsNone(bible_module.doctrine_path("paths"))

    def test_doctrine_hash_is_crlf_lf_equivalent(self):
        lf = self.root / "lf.md"
        crlf = self.root / "crlf.md"
        lf.write_bytes(b"Line one\nLine two\n")
        crlf.write_bytes(b"Line one\r\nLine two\r\n")
        self.assertEqual(
            bible_module.doctrine_sha256(lf),
            bible_module.doctrine_sha256(crlf),
        )

    def test_missing_empty_and_completed_doctrine_fail_before_gemini(self):
        for slug, status, text in (
            ("missing", "active", None),
            ("empty", "active", " \n\t"),
            ("completed", "completed", None),
        ):
            folder = self._make_series(slug, status=status, doctrine_text=text)
            with self.subTest(slug=slug), mock.patch.object(replenish, "_gen_json") as gemini:
                with self.assertLogs(replenish.logger.name, level="ERROR") as logs:
                    self.assertFalse(replenish.replenish(slug))
                gemini.assert_not_called()
                self.assertIn("HATA", "\n".join(logs.output))
                self.assertFalse((folder / "plans" / "part01.json").exists())

    def test_paused_and_draft_keep_noop_without_gate(self):
        for slug, status in (("paused", "paused"), ("draft", "draft")):
            self._make_series(slug, status=status, doctrine_text=None)
            with mock.patch.object(
                replenish, "doctrine_path", side_effect=AssertionError("Kapı çağrılmamalı")
            ):
                self.assertTrue(replenish.replenish(slug))

    def test_hash_log_pin_and_written_plan_stamp(self):
        text = "Line one\nLine two\n"
        folder = self._make_series("hash-ok", doctrine_text=text, pin=True)
        response = {"episodes": [_plan(words=0)]}
        with mock.patch.object(replenish, "_gen_json", return_value=response):
            with self.assertLogs(replenish.logger.name, level="INFO") as logs:
                self.assertTrue(replenish.replenish("hash-ok"))
        digest = _digest(text)
        self.assertIn(
            f"Doktrin: channel_hash-ok/KONSEPT.md sha256={digest}",
            "\n".join(logs.output),
        )
        saved = json.loads((folder / "plans" / "part01.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["doctrine_sha256"], digest)
        self.assertEqual(SeriesMeta.load("hash-ok").total_parts, 1)

        bad = self._make_series("hash-bad", doctrine_text="Pinned")
        meta_path = bad / "series.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["doctrine_sha256"] = "0" * 64
        meta_path.write_text(json.dumps(meta), encoding="utf-8")
        with mock.patch.object(replenish, "_gen_json") as gemini:
            self.assertFalse(replenish.replenish("hash-bad"))
            gemini.assert_not_called()

    def test_produce_gate_and_plan_stamp_rules(self):
        text = "Production doctrine\n"
        digest = _digest(text)
        self._make_series("prod-pinned", doctrine_text=text, pin=True)
        with mock.patch.object(produce, "build_omni_payload", wraps=produce.build_omni_payload):
            with self.assertLogs(produce.logger.name, level="INFO") as logs:
                self.assertIsNone(
                    produce.produce_episode(
                        "prod-pinned", _plan(words=0, stamp=digest), dry_run=True
                    )
                )
        self.assertIn(
            f"Doktrin: channel_prod-pinned/KONSEPT.md sha256={digest}",
            "\n".join(logs.output),
        )
        with self.assertLogs(produce.logger.name, level="ERROR"):
            self.assertIsNone(produce.produce_episode("prod-pinned", _plan(words=0), dry_run=True))
            self.assertIsNone(
                produce.produce_episode(
                    "prod-pinned", _plan(words=0, stamp="f" * 64), dry_run=True
                )
            )

        self._make_series("prod-legacy", doctrine_text=text, pin=False)
        with self.assertLogs(produce.logger.name, level="INFO") as legacy_logs:
            self.assertIsNone(produce.produce_episode("prod-legacy", _plan(words=0), dry_run=True))
        self.assertIn("🎬", "\n".join(legacy_logs.output))
        with self.assertLogs(produce.logger.name, level="ERROR"):
            self.assertIsNone(
                produce.produce_episode(
                    "prod-legacy", _plan(words=0, stamp="e" * 64), dry_run=True
                )
            )

        self._make_series("prod-missing", doctrine_text=None)
        with mock.patch.object(produce, "check_credit") as network:
            with self.assertLogs(produce.logger.name, level="ERROR"):
                self.assertIsNone(produce.produce_episode("prod-missing", _plan(words=0)))
            network.assert_not_called()

    def test_word_budget_with_mixer_margin(self):
        # Hedef 20-30; kabul araligi mikser payiyla 17-35 (min*0.85 asagi, max*1.15 yukari).
        flash = Bible(_bible("flash"))
        cfg = {"narration": {"min_words": 20, "max_words": 30}, "shots": 2}
        low = replenish._validate_batch([_plan(words=16)], flash, 1, 1, set(), cfg)
        edge_low = replenish._validate_batch([_plan(words=17)], flash, 1, 1, set(), cfg)
        inside = replenish._validate_batch([_plan(words=25)], flash, 1, 1, set(), cfg)
        edge_high = replenish._validate_batch([_plan(words=35)], flash, 1, 1, set(), cfg)
        high = replenish._validate_batch([_plan(words=36)], flash, 1, 1, set(), cfg)
        self.assertTrue(any("16 kelime" in error for error in low))
        self.assertEqual(edge_low, [])
        self.assertEqual(inside, [])
        self.assertEqual(edge_high, [])
        self.assertTrue(any("36 kelime" in error for error in high))

    def test_flashpoints_like_valid_plan_is_written(self):
        cfg = {
            "narration": {"min_words": 20, "max_words": 30},
            "title_card": True,
            "music_prompt": True,
            "families": ["tuhaf savaş"],
            "topic_pool": [
                {"id": 1, "topic": "A verified event in 1896.", "family": "tuhaf savaş"}
            ],
        }
        folder = self._make_series(
            "flashpoints", doctrine_text="Flash doctrine", pin=True, cfg=cfg
        )
        bible_data = _bible("flashpoints", narration_channel="shadowedhistory", title_card=True)
        (folder / "bible.json").write_text(json.dumps(bible_data), encoding="utf-8")
        plan = _plan(1, 20, "tuhaf savaş", 1)
        plan["title_card"] = {"title": "Zanzibar, 1896", "subtitle": "The Shortest War"}
        plan["music"] = " ".join(f"beat{i}" for i in range(40))
        with mock.patch.object(replenish, "_gen_json", return_value={"episodes": [plan]}):
            self.assertTrue(replenish.replenish("flashpoints"))
        written = json.loads((folder / "plans" / "part01.json").read_text(encoding="utf-8"))
        self.assertEqual(written["family"], "tuhaf savaş")
        self.assertEqual(written["seed_id"], 1)
        self.assertEqual(written["doctrine_sha256"], _digest("Flash doctrine"))

        bce_plan = _plan(1, 20, "tuhaf savaş", 1)
        bce_plan["title_card"] = {"title": "Egypt, 69 BCE", "subtitle": "A Verified Event"}
        bce_plan["music"] = " ".join(f"beat{i}" for i in range(40))
        self.assertEqual(
            replenish._validate_batch([bce_plan], Bible.load("flashpoints"), 1, 1, set(), cfg),
            [],
        )

        no_anchor = _plan(1, 20, "tuhaf savaş", 1)
        no_anchor["title_card"] = {"title": "Egypt", "subtitle": "A Verified Event"}
        no_anchor["music"] = " ".join(f"beat{i}" for i in range(40))
        errors = replenish._validate_batch(
            [no_anchor], Bible.load("flashpoints"), 1, 1, set(), cfg
        )
        self.assertTrue(any("4-haneli yıl veya çağ çıpası" in error for error in errors))

    def test_topic_pool_and_family_validation_is_dynamic(self):
        cfg = {
            "shots": 2,
            "families": ["alpha", "beta"],
            "topic_pool": [
                {"id": 1, "topic": "First.", "family": "alpha"},
                {"id": 2, "topic": "Second.", "family": "beta"},
                {"id": 13, "topic": "Later.", "family": "alpha"},
            ],
        }
        b = Bible(_bible("pool"))

        def errors(plan, history=None):
            return replenish._validate_batch([plan], b, 1, 1, set(), cfg, history)

        self.assertTrue(any("havuzunda yok" in e for e in errors(_plan(1, 0, "alpha", 99))))
        self.assertTrue(
            any(
                "daha önce" in e
                for e in errors(
                    _plan(1, 0, "alpha", 1),
                    [{"seed_id": 1, "family": "beta"}],
                )
            )
        )
        self.assertEqual(errors(_plan(1, 0, "alpha", 13)), [])
        self.assertTrue(any("eşleşmiyor" in e for e in errors(_plan(1, 0, "beta", 1))))
        self.assertTrue(any("family alanı" in e for e in errors(_plan(1, 0, seed_id=1))))
        self.assertTrue(any("kanonik" in e for e in errors(_plan(1, 0, "other", 1))))
        self.assertTrue(
            any(
                "ardışık" in e
                for e in errors(
                    _plan(1, 0, "alpha", 1),
                    [{"seed_id": 2, "family": "alpha"}],
                )
            )
        )
        batch = [_plan(1, 0, "alpha", 1), _plan(2, 0, "alpha", 13)]
        self.assertTrue(
            any(
                "ardışık" in e
                for e in replenish._validate_batch(batch, b, 1, 2, set(), cfg)
            )
        )

    def test_partial_pool_batch_and_exhaustion(self):
        cfg = {
            "batch": 5,
            "families": ["alpha", "beta"],
            "topic_pool": [
                {"id": 1, "topic": "Used.", "family": "alpha"},
                {"id": 2, "topic": "Fresh.", "family": "beta"},
                {"id": 3, "topic": "Fresh two.", "family": "alpha"},
            ],
        }
        folder = self._make_series("partial", doctrine_text="Pool doctrine", pin=True, cfg=cfg)
        plans = folder / "plans"
        plans.mkdir()
        (plans / "part01.json").write_text(
            json.dumps(_plan(1, 0, "alpha", 1)), encoding="utf-8"
        )
        meta_path = folder / "series.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["total_parts"] = 1
        meta["next_part"] = 2
        meta_path.write_text(json.dumps(meta), encoding="utf-8")
        response = {
            "episodes": [
                _plan(2, 0, "beta", 2),
                _plan(3, 0, "alpha", 3),
            ]
        }
        with mock.patch.object(replenish, "_gen_json", return_value=response) as gemini:
            self.assertTrue(replenish.replenish("partial"))
            gemini.assert_called_once()
        self.assertTrue((plans / "part02.json").is_file())
        self.assertTrue((plans / "part03.json").is_file())
        self.assertEqual(SeriesMeta.load("partial").total_parts, 3)

        exhausted = self._make_series(
            "exhausted",
            doctrine_text="Pool doctrine",
            cfg={
                "topic_pool": [{"id": 1, "topic": "Only.", "family": "alpha"}],
                "families": ["alpha"],
            },
        )
        (exhausted / "plans").mkdir()
        (exhausted / "plans" / "part01.json").write_text(
            json.dumps(_plan(1, 0, "alpha", 1)), encoding="utf-8"
        )
        meta_path = exhausted / "series.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["total_parts"] = 1
        meta["next_part"] = 2
        meta_path.write_text(json.dumps(meta), encoding="utf-8")
        with mock.patch.object(replenish, "_gen_json") as gemini:
            with self.assertLogs(replenish.logger.name, level="ERROR") as logs:
                self.assertFalse(replenish.replenish("exhausted"))
            gemini.assert_not_called()
        self.assertIn("HATA", "\n".join(logs.output))

    def test_music_style_override_and_default_prompt(self):
        self._make_series("prompt", doctrine_text="Prompt doctrine")
        meta = SeriesMeta.load("prompt")
        b = Bible.load("prompt")
        style = "Exact channel music style."
        _, styled = replenish._build_prompt(
            meta, b, {"music_prompt": True, "music_style": style}, 1, 1, []
        )
        _, default = replenish._build_prompt(meta, b, {"music_prompt": True}, 1, 1, [])
        self.assertIn(style, styled)
        self.assertIn("SERIES MUSIC STYLE", styled)
        self.assertIn("name genre, mood", default)


class InstalledSeriesTests(unittest.TestCase):
    def test_unnatural_lab_doctrine_regression(self):
        path = bible_module.doctrine_path("unnatural-lab")
        self.assertEqual(path, REPO_ROOT / "sentinal_ihsan" / "KONSEPT.md")

    def test_new_series_load_with_effective_values(self):
        detailed = {
            "flashpoints": ("shad0wedhistory", 2, "8", (26, 38), 6, 27),
            "event-horizon": ("galacticexperimet", 3, "6", (30, 44), 6, 27),
            "from-scratch": ("Youtube", 6, "10", None, 6, 0),
        }
        for slug, values in detailed.items():
            profile, shots, seconds, word_range, family_count, pool_size = values
            meta = SeriesMeta.load(slug)
            cfg = meta.auto_replenish
            self.assertEqual(meta.upload_profile, profile)
            self.assertEqual(cfg["shots"], shots)
            self.assertEqual(cfg["shot_seconds"], seconds)
            self.assertEqual(len(cfg["families"]), family_count)
            self.assertEqual(len(cfg.get("topic_pool", [])), pool_size)
            if word_range:
                self.assertEqual(
                    (cfg["narration"]["min_words"], cfg["narration"]["max_words"]),
                    word_range,
                )
            else:
                self.assertNotIn("narration", cfg)

        expected = {
            "flashpoints": (2, "8", False),
            "event-horizon": (3, "6", False),
            "from-scratch": (6, "10", True),
        }
        for slug, (shots, seconds, teaser) in expected.items():
            with self.subTest(slug=slug):
                meta = SeriesMeta.load(slug)
                bible = Bible.load(slug)
                self.assertIsNotNone(meta)
                self.assertIsNotNone(bible)
                self.assertTrue(meta.standalone)
                self.assertEqual(meta.status, "active")
                self.assertEqual(meta.priority, 999)
                self.assertEqual(meta.auto_replenish["shots"], shots)
                self.assertEqual(meta.auto_replenish["shot_seconds"], seconds)
                self.assertEqual(bool(bible.hook_teaser), teaser)
                self.assertTrue(bible.qc)
        flash = Bible.load("flashpoints")
        self.assertTrue(flash.title_card)
        scratch = Bible.load("from-scratch")
        self.assertNotIn("narration", scratch.data)
        self.assertTrue(scratch.chain_frames)
        self.assertEqual(scratch.chain_scope, "episode")
        self.assertEqual(scratch.required_layers, ["hook_teaser", "music"])
        # KARAR-2 (Ihsan, 2026-08-08): require_all_shots KAPATILDI. Motor yetenegi hala
        # test_fixedframe.py::test_require_all_shots_blocks_merge_when_any_shot_missing'de korunuyor.
        self.assertFalse(scratch.require_all_shots)
        self.assertEqual(scratch.hook_teaser["offset_in_shot"], 7.0)

        scratch_meta = SeriesMeta.load("from-scratch")
        scratch_cfg = scratch_meta.auto_replenish
        canonical_families = [
            "oyun/film üsleri",
            "fantezi konutlar",
            "absürt eğlence mimarisi",
            "dönüşüm",
            "saklı/mühendislik harikası",
            "geri dönüşüm / off-grid dönüşüm",
        ]
        self.assertGreaterEqual(
            scratch_meta.total_parts,
            len(scratch_meta.data.get("parts", {})),
        )
        self.assertEqual(scratch_meta.data["hashtags"], "#shorts #satisfying #construction #diy")
        self.assertEqual(scratch_cfg["shots"], 6)
        self.assertEqual(scratch_cfg["shot_seconds"], "10")
        self.assertEqual(scratch_cfg["hook_shot"], 6)
        self.assertEqual(scratch_cfg["chain_breaks"], [1, 4])
        self.assertTrue(scratch_cfg["credit_hard_cap"])
        self.assertEqual(scratch_cfg["families"], canonical_families)
        self.assertEqual(len(scratch_cfg["shot_plan"]), 6)
        expected_pattern_families = [
            canonical_families,
            canonical_families,
            ["dönüşüm"],
            ["dönüşüm", "geri dönüşüm / off-grid dönüşüm"],
            canonical_families,
        ]
        self.assertEqual(len(scratch_cfg["title_patterns"]), 5)
        for rule, expected_families in zip(
                scratch_cfg["title_patterns"], expected_pattern_families):
            re.compile(rule["regex"])
            self.assertEqual(rule["families"], expected_families)
        doctrine = REPO_ROOT / "aimagine" / "KONSEPT.md"
        self.assertEqual(scratch_meta.data["doctrine_sha256"],
                         bible_module.doctrine_sha256(doctrine))

    def test_from_scratch_workflow_credit_cap(self):
        raw = (REPO_ROOT / ".github" / "workflows" / "from-scratch.yml").read_text(
            encoding="utf-8"
        )
        values = re.findall(r"^\s*EPISODE_CREDIT_CAP=(\d+)\s*$", raw, re.MULTILINE)
        self.assertEqual(values, ["1900"])

    def test_from_scratch_post_process_skips_narration_and_uses_alias(self):
        bible = Bible.load("from-scratch")
        with tempfile.TemporaryDirectory() as td:
            video = pathlib.Path(td) / "video.mp4"
            video.write_bytes(b"test")
            with mock.patch.object(
                narration, "create_narration_for_channel"
            ) as narrate, mock.patch.object(
                music_generator, "generate_background_music", return_value=None
            ) as music:
                self.assertEqual(
                    produce._post_process(bible, {"episode": {"number": 1}}, video),
                    video,
                )
            narrate.assert_not_called()
            self.assertEqual(music.call_args.args[0], "from-scratch")
        self.assertEqual(music_generator.MUSIC_PROMPT_ALIASES["from-scratch"], "aimagine")

    def test_narration_register_names_unchanged_and_instructions_updated(self):
        shadow = narration.CHANNEL_NARRATION_CONFIG["shadowedhistory"]
        galactic = narration.CHANNEL_NARRATION_CONFIG["galactic_experiment"]
        self.assertEqual(shadow["voice"], "Charon")
        self.assertEqual(galactic["voice"], "Charon")
        self.assertIn("fast", shadow["instruction"])
        self.assertIn("one short pause", shadow["instruction"])
        self.assertIn("18-second", galactic["instruction"])
        self.assertIn("never let the delivery drag", galactic["instruction"])


class ApprovalCallbackTests(unittest.TestCase):
    """Slug'li onay callback eslesmesi: coklu-seri carpisma guvenligi (2026-07-29)."""

    def test_new_format_matches_only_own_slug(self):
        from series.approver import match_decision
        self.assertEqual(match_decision("vd:flashpoints:approve:1", "flashpoints", 1, None, None), "approve")
        self.assertEqual(match_decision("vd:flashpoints:reject:1", "flashpoints", 1, None, None), "reject")
        self.assertIsNone(match_decision("vd:flashpoints:approve:1", "event-horizon", 1, None, None))
        self.assertIsNone(match_decision("vd:flashpoints:approve:2", "flashpoints", 1, None, None))

    def test_legacy_format_requires_message_id_match(self):
        from series.approver import match_decision
        self.assertEqual(match_decision("vd:approve:3", "unnatural-lab", 3, 346, 346), "approve")
        self.assertEqual(match_decision("vd:reject:3", "unnatural-lab", 3, 346, 346), "reject")
        self.assertIsNone(match_decision("vd:approve:3", "unnatural-lab", 3, 346, 999))
        self.assertIsNone(match_decision("vd:approve:1", "flashpoints", 1, None, 555))
        self.assertIsNone(match_decision("vd:approve:1", "event-horizon", 1, None, None))


if __name__ == "__main__":
    unittest.main()
