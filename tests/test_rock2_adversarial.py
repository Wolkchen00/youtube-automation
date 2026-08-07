"""ROCK 2 bagimsiz nobetci testleri (Visionary, Codex suitinin disindaki vakalar).

Codex'in test_rock2_replenish_family.py suiti yasak-aile yolunu kapsar. Bu dosya
onun KACIRDIGI geri-uyumluluk vakalarini tutar: families tanimsiz seri, family
tasimayan gecmis, batch=1 ve "gecerli cevap bosuna yeniden denenmiyor".
"""

import copy
import json
import pathlib
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from series import replenish                  # noqa: E402
from series.bible import Bible                # noqa: E402
from series.series_meta import SeriesMeta     # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")

BLOCK_MARKER = "CRITICAL FAMILY BLOCK"
CLASSIC_POOL = "RUNTIME UNUSED TOPIC POOL. Use each seed_id at most once:"


def ctx():
    meta = SeriesMeta.load("flashpoints")
    bible = Bible.load("flashpoints")
    history = replenish._episode_history("flashpoints")
    assert meta is not None and bible is not None
    return meta, bible, copy.deepcopy(meta.auto_replenish), history


def prompt_text(meta, bible, cfg, start, batch, history):
    contents, sysins = replenish._build_prompt(
        meta, bible, cfg, start, batch, history)
    return f"{contents}\n{sysins}"


class BackwardCompatibility(unittest.TestCase):
    # B1 ,  families tanimsizsa davranis ESKISIYLE ayni kalmali
    def test_b1_series_without_families_is_untouched(self):
        meta, bible, cfg, history = ctx()
        cfg.pop("families", None)
        text = prompt_text(meta, bible, cfg, 6, 5, history)
        self.assertNotIn(BLOCK_MARKER, text)
        self.assertNotIn("FOR FIRST EPISODE", text)
        if replenish._topic_pool(cfg):
            self.assertIn(CLASSIC_POOL, text)

    # B2 ,  gecmiste hic family yoksa (ilk bolumler) blok kurali uretilmemeli
    def test_b2_history_without_family_produces_no_block(self):
        meta, bible, cfg, _history = ctx()
        text = prompt_text(meta, bible, cfg, 1, 5, [])
        self.assertNotIn(BLOCK_MARKER, text)
        self.assertEqual(replenish._previous_family([]), "")
        self.assertEqual(
            replenish._previous_family([{"family": ""}, {"family": "  "}]), "")

    # B3 ,  batch=1 iken "sonraki bolumler havuzu" bolumu basilmamali
    def test_b3_single_episode_batch_has_no_later_pool_section(self):
        meta, bible, cfg, history = ctx()
        text = prompt_text(meta, bible, cfg, 6, 1, history)
        self.assertIn(BLOCK_MARKER, text)
        self.assertIn("FOR FIRST EPISODE 6", text)
        self.assertNotIn("FOR LATER EPISODES", text)

    # B4 ,  _previous_family en SON family tasiyan kaydi almali, sonuncuyu degil
    def test_b4_previous_family_skips_trailing_familyless_entries(self):
        hist = [{"family": "a"}, {"family": "b"}, {"family": None}, {}]
        self.assertEqual(replenish._previous_family(hist), "b")


class NoWastedAttempts(unittest.TestCase):
    # B5 ,  gecerli cevap ILK denemede kabul edilmeli (3 deneme tavan, kota degil)
    def test_b5_valid_first_response_is_not_retried(self):
        meta, bible, cfg, history = ctx()
        families = [f for f in (cfg.get("families") or [])]
        forbidden = replenish._previous_family(history)
        ok_family = next(f for f in families if f != forbidden)

        captured = {}

        def fake_validate(episodes, *a, **kw):
            captured["seen"] = True
            return []          # hatasiz

        with mock.patch.object(replenish, "_gen_json",
                               return_value={"episodes": [{"episode": {"number": 6}}]}) as gen, \
                mock.patch.object(replenish, "_validate_batch", side_effect=fake_validate):
            out = replenish.generate_plans(meta, bible, cfg, 6, 1)

        self.assertEqual(gen.call_count, 1, "gecerli cevap yeniden denenmemeli")
        self.assertTrue(captured.get("seen"))
        self.assertEqual(len(out), 1)
        self.assertTrue(ok_family)   # fixture saglikli


if __name__ == "__main__":
    unittest.main()
