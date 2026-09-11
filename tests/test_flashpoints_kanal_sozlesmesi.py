"""Flashpoints kanal yapılandırması sözleşme testleri."""

import copy
import inspect
import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from series import produce
from series.bible import Bible
from series.preflight import validate_min_shots
from series.series_meta import SeriesMeta


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
PART31_PATH = REPO_ROOT / "shadowedhistory" / "flashpoints" / "plans" / "part31.json"


class FlashpointsChannelContractTests(unittest.TestCase):
    def test_master_lufs_is_minus_14(self):
        bible = Bible.load("flashpoints")
        self.assertEqual(bible.master_lufs, -14.0)

    def test_mastering_mixer_side_effects(self):
        bible = Bible.load("flashpoints")
        amix_normalize = bible.master_lufs is None
        limit_mix_peak = bible.master_lufs is not None
        music_volume = 0.50 if bible.master_lufs is not None else 0.28

        self.assertFalse(amix_normalize)
        self.assertTrue(limit_mix_peak)
        self.assertEqual(music_volume, 0.50)

        function_source = inspect.getsource(produce._post_process)
        self.assertIn("amix_normalize=bible.master_lufs is None", function_source)
        self.assertIn(
            "music_volume = 0.50 if bible.master_lufs is not None else 0.28",
            function_source,
        )
        self.assertIn("limit_mix_peak=bible.master_lufs is not None", function_source)

    def test_harden_downloads_is_enabled(self):
        bible = Bible.load("flashpoints")
        self.assertIs(bible.qc["harden_downloads"], True)

    def test_true_peak_margin_is_set(self):
        """Pay 0 olursa limiter yakinsamiyor ve bolum awaiting_approval'da kaliyor.

        Canli kanit (2026-09-10, part31): master_lufs acildiktan sonraki ILK kosu
        "true-peak -0.4 dBTP > -1.0 dBTP, 3 denemede tutulamadi" diyerek bolumu
        tuttu ve o gun kanala video cikmadi. Geri cekilme tam olarak asim kadar
        oldugu icin (pay=0) AAC kodlamasi ayni asimi geri ekliyor ve dongu
        esigin altina hic inmiyor. galactic_experience/event-horizon ayni
        sorunu 0.2 ile cozmustu.
        """
        bible = Bible.load("flashpoints")
        self.assertGreater(bible.master_true_peak_margin_db, 0.0)
        self.assertEqual(bible.master_true_peak_margin_db, 0.2)

    def test_required_shot_count_and_control(self):
        bible = Bible.load("flashpoints")
        self.assertEqual(produce._required_shot_count(bible, 2), 2)

        control_data = copy.deepcopy(bible.data)
        del control_data["series"]["qc"]["min_shots"]
        control_bible = Bible(control_data)
        self.assertEqual(produce._required_shot_count(control_bible, 2), 1)

    def test_part31_one_shot_copy_is_rejected_and_original_passes(self):
        bible = Bible.load("flashpoints")
        plan = json.loads(PART31_PATH.read_text(encoding="utf-8"))
        self.assertEqual(len(plan["shots"]), 2)
        self.assertEqual(validate_min_shots(bible, plan), [])

        one_shot_plan = copy.deepcopy(plan)
        one_shot_plan["shots"] = one_shot_plan["shots"][:1]
        errors = validate_min_shots(bible, one_shot_plan)
        self.assertTrue(errors)
        self.assertTrue(any("min_shots" in error for error in errors))

    def test_fact_captions_escape_hatches_remain_absent(self):
        bible = Bible.load("flashpoints")
        meta = SeriesMeta.load("flashpoints")
        self.assertNotIn("fact_captions", bible.data["series"])
        self.assertNotIn("fact_captions", meta.auto_replenish)

    def test_shot_seconds_remains_doctrine_v18_value(self):
        meta = SeriesMeta.load("flashpoints")
        self.assertEqual(meta.auto_replenish["shot_seconds"], "10")


if __name__ == "__main__":
    unittest.main()
