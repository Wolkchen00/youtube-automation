"""
Galactic config gates ,  lock in the new opt-in gates for event-horizon and
verify fleet isolation + malformed-value rejection.
"""

import unittest
from series.bible import Bible
from tests._archived_fixture import archived_search_roots


class EventHorizonConfigTest(unittest.TestCase):
    """event-horizon must opt into every new gate with the exact values."""

    def test_event_horizon_opts_into_every_new_gate(self):
        bible = Bible.load("event-horizon")
        self.assertIsNotNone(bible, "event-horizon bible should load")

        series = bible.data["series"]

        self.assertEqual(series.get("state_machine_version"), 2)
        self.assertEqual(bible.master_lufs, -14)
        self.assertEqual(bible.master_true_peak_margin_db, 0.2)
        self.assertTrue(bible.block_degraded_publish)
        self.assertEqual(bible.duration_band, (14.0, 22.0))
        self.assertEqual(bible.required_layers, ["title_card"])
        self.assertEqual(
            bible.title_card,
            {
                "enabled": True,
                "duration": 2.0,
                "year_required": False,
                "preserve_case": True,
            },
        )


class FleetIsolationTest(unittest.TestCase):
    """The other three active series must NOT have picked up the new gates."""

    def setUp(self):
        # unnatural-lab 2026-09-10'da arsivlendi: onun alt testi dondurulmus config'i
        # okur; flashpoints ve next-stop canli kalir (tests/_archived_fixture.py).
        roots = archived_search_roots()
        roots.start()
        self.addCleanup(roots.stop)

    def test_other_series_did_not_inherit_the_new_gates(self):
        slugs = ["flashpoints", "next-stop", "unnatural-lab"]

        for slug in slugs:
            with self.subTest(series=slug):
                bible = Bible.load(slug)
                self.assertIsNotNone(bible, f"{slug} bible should load")

                series = bible.data["series"]

                # master_lufs: flashpoints bu alani 2026-09-10'da BASKA bir ajanin
                # kendi turunda kazandi (ROCK: "flashpoints ses mastering'i ac").
                # Bizim turumuzun getirdigi alanlar DEGIL; onlar asagida ayrica
                # kontrol ediliyor. next-stop hala mastering disinda.
                if slug == "next-stop":
                    self.assertIsNone(bible.master_lufs)
                else:  # flashpoints ve unnatural-lab
                    self.assertEqual(bible.master_lufs, -14)

                # master_true_peak_margin_db: bu alan bu turda event-horizon icin
                # eklendi. Amac SIZMAYI yakalamak, yani alani hic istemeyen bir
                # seride kazara acilmasini.
                #
                # 2026-09-10: flashpoints bu payi BILEREK aldi (d4abc8e). Sebep
                # olculmus bir yayin arizasi: master_lufs acildiktan sonraki ilk
                # kosuda teslim "true-peak -0.4 dBTP > -1.0" ile tuttu ve o gun
                # kanala video CIKMADI. Yani bu sizma degil, kasitli benimseme.
                #
                # Test yine de sert kaliyor: payi benimsemeyen seriler 0.0'da
                # olmali, yoksa kazara acilmasi buradan gecerdi.
                if slug == "flashpoints":
                    self.assertEqual(
                        bible.master_true_peak_margin_db, 0.2,
                        "flashpoints payi bilerek 0.2; degistiyse d4abc8e'nin "
                        "duzelttigi yayin arizasi geri gelmis olabilir",
                    )
                else:  # next-stop ve unnatural-lab payi ISTEMEDI
                    self.assertEqual(
                        bible.master_true_peak_margin_db, 0.0,
                        "%s bu alani hic benimsemedi; 0.0 disinda bir deger "
                        "sizma demektir" % slug,
                    )

                # block_degraded_publish ,  all three must be False
                self.assertFalse(bible.block_degraded_publish)

                # state_machine_version
                if slug == "unnatural-lab":
                    self.assertEqual(bible.state_machine_version, 2)
                else:
                    self.assertEqual(bible.state_machine_version, 1)


class MalformedConfigTest(unittest.TestCase):
    """Bible properties must raise ValueError on malformed values."""

    def test_margin_rejects_bool_negative_and_infinite(self):
        # bool
        with self.assertRaises(ValueError):
            Bible({"series": {"master_true_peak_margin_db": True}}).master_true_peak_margin_db
        # negative
        with self.assertRaises(ValueError):
            Bible({"series": {"master_true_peak_margin_db": -0.1}}).master_true_peak_margin_db
        # infinite
        with self.assertRaises(ValueError):
            Bible({"series": {"master_true_peak_margin_db": float("inf")}}).master_true_peak_margin_db
        # string "0.2" is ACCEPTED (floated)
        self.assertEqual(
            Bible({"series": {"master_true_peak_margin_db": "0.2"}}).master_true_peak_margin_db,
            0.2,
        )

    def test_block_degraded_publish_requires_a_real_boolean(self):
        # string "true"
        with self.assertRaises(ValueError):
            Bible({"series": {"block_degraded_publish": "true"}}).block_degraded_publish
        # string "false"
        with self.assertRaises(ValueError):
            Bible({"series": {"block_degraded_publish": "false"}}).block_degraded_publish
        # integer 0
        with self.assertRaises(ValueError):
            Bible({"series": {"block_degraded_publish": 0}}).block_degraded_publish
        # integer 1
        with self.assertRaises(ValueError):
            Bible({"series": {"block_degraded_publish": 1}}).block_degraded_publish
        # real JSON boolean works
        self.assertFalse(Bible({"series": {"block_degraded_publish": False}}).block_degraded_publish)
        self.assertTrue(Bible({"series": {"block_degraded_publish": True}}).block_degraded_publish)

    def test_title_card_flags_require_real_booleans(self):
        # year_required: string "false" must raise
        with self.assertRaises(ValueError):
            Bible({"series": {"title_card": {"enabled": True, "year_required": "false"}}}).title_card
        # preserve_case: string "false" must raise
        with self.assertRaises(ValueError):
            Bible({"series": {"title_card": {"enabled": True, "preserve_case": "false"}}}).title_card
        # real booleans work
        tc = Bible({"series": {"title_card": {"enabled": True, "year_required": False, "preserve_case": True}}}).title_card
        self.assertFalse(tc["year_required"])
        self.assertTrue(tc["preserve_case"])


if __name__ == "__main__":
    unittest.main()