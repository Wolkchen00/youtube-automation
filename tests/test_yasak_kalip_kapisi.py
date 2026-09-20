"""Yasak kalip kapisi: kuyruktaki plan da, yeni yazilan plan da denetlenir.

19 Eylul 2026 arizasi: wild-encounter part12 planinda "Ambient sound only: ...
and crew commands." yaziyordu. Komut konusmadir; seri doktrini konusmayi
yasaklar. Omni uc denemede de konusma uretti, ham ses QC ucunu de reddetti,
bolum 378 kredi yakarak oldu ve kanal o gun karanlik kaldi.

Kapi ikmalin ICINDE vardi ama yalniz YENI yazilan plani goruyordu; kuyrukta
duran plan bir daha hic okunmadi. Bu dosya kapinin artik uretim yolunda da
kostugunu ve gercek kuyrugun temiz oldugunu kanitlar.
"""

import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from series import critic, replenish

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
WILD = REPO_ROOT / "sentinal_ihsan" / "wild-encounter"

SHOT_PLAN_LINE = "ONE CONTINUOUS TAKE. The crew hold their positions."


def cfg(*, phrases=None, shots=1):
    config = {
        "enabled": True,
        "shots": shots,
        "shot_seconds": "10",
        "format_version": "plato-3x8",
        "shot_plan": [SHOT_PLAN_LINE for _ in range(shots)],
    }
    if phrases is not None:
        config["forbidden_phrases"] = phrases
    return config


def plan(tail, *, shots=1):
    return {
        "format_version": "plato-3x8",
        "episode": {"number": 12, "title": "Deneme"},
        "shots": [
            {
                "n": number,
                "duration": "10",
                "prompt": f"{SHOT_PLAN_LINE}\n\nA giant creature faces one man. {tail}",
            }
            for number in range(1, shots + 1)
        ],
    }


class YasakKalipKapisi(unittest.TestCase):
    def test_kuyruktaki_plan_yasak_kalipta_reddedilir(self):
        """Ariza planinin BIREBIR kalibi: ikmal degil, uretim kapisi yakalar."""
        errors = replenish.validate_plan_against_config(
            plan("Ambient sound only: footsteps, studio air handling, and crew commands."),
            cfg(phrases={"*": ["command", "voice"]}),
        )
        self.assertTrue(
            any("yasak kalıp" in error and "'command'" in error for error in errors),
            errors,
        )

    def test_temiz_plan_gecer(self):
        """Ariza duzeltmesinin kendisi: 'crew movement' kapidan gecmeli."""
        self.assertEqual(
            replenish.validate_plan_against_config(
                plan("Ambient sound only: footsteps, studio air handling, and crew movement."),
                cfg(phrases={"*": ["command", "voice"]}),
            ),
            [],
        )

    def test_kanonik_sablon_satiri_kapiyi_tetiklemez(self):
        """Yasak kelime shot_plan'in KENDISINDE ise plan sucsuzdur.

        Kapi yalniz modelin yazdigi metne bakar; aksi halde seri sablonunu
        degistirmek butun kuyrugu bir anda hatali yapardi."""
        config = cfg(phrases={"*": ["crew"]})
        config["shot_plan"] = ["ONE CONTINUOUS TAKE. The crew hold their positions."]
        candidate = {
            "format_version": "plato-3x8",
            "episode": {"number": 12, "title": "Deneme"},
            "shots": [{
                "n": 1,
                "duration": "10",
                "prompt": "ONE CONTINUOUS TAKE. The crew hold their positions."
                          "\n\nA giant creature faces one man on the built set.",
            }],
        }
        self.assertEqual(replenish.validate_plan_against_config(candidate, config), [])

    def test_cekim_numarali_anahtar_da_kosar(self):
        errors = replenish.validate_plan_against_config(
            plan("The performer is speaking to the crew.", shots=2),
            cfg(phrases={"2": ["speak"]}, shots=2),
        )
        self.assertEqual(
            [error for error in errors if "yasak kalıp" in error and "çekim 2" in error],
            [error for error in errors if "yasak kalıp" in error],
        )
        self.assertTrue(errors)

    def test_liste_yoksa_geriye_donuk_uyumlu(self):
        self.assertEqual(
            replenish.validate_plan_against_config(
                plan("Ambient sound only: crew commands everywhere."), cfg()
            ),
            [],
        )


class WildEncounterCanliKuyruk(unittest.TestCase):
    """Canli seri: yayinlanan yapilandirma ve kuyruk bu kapidan gecmeli."""

    def setUp(self):
        self.meta = json.loads((WILD / "series.json").read_text(encoding="utf-8"))
        self.cfg = self.meta["auto_replenish"]

    def test_konusma_sozlugu_yapilandirmada_duruyor(self):
        banned = self.cfg["forbidden_phrases"]["*"]
        for word in ("command", "speak", "voice", "shout", "narrat"):
            self.assertIn(word, banned)

    def test_alkis_ve_ayak_sesi_yasaklanmadi(self):
        """Liste sesi degil INSAN SESINI hedefler; eski bolumler alkis kullandi."""
        banned = self.cfg["forbidden_phrases"]["*"]
        for word in ("applause", "footsteps", "rustling", "water"):
            self.assertNotIn(word, banned)

    def test_kuyruktaki_planlarin_hepsi_temiz(self):
        next_part = int(self.meta["next_part"])
        total = int(self.meta["total_parts"])
        checked = 0
        for number in range(next_part, total + 1):
            path = WILD / "plans" / f"part{number:02d}.json"
            if not path.exists():
                continue
            checked += 1
            errors = replenish.validate_plan_against_config(
                json.loads(path.read_text(encoding="utf-8")), self.cfg, engine="omni"
            )
            self.assertEqual(errors, [], f"{path.name}: {errors}")
        if not checked:
            # Son bolum yayinlandiktan sonra kuyruk mesru olarak bostur.
            self.skipTest("kuyruk su an bos, ikmal bekleniyor")


class SesDuzeltmeMetni(unittest.TestCase):
    """Regen duzeltmesi BASKA bir dizinin kadrajini tarif etmemeli."""

    def test_ses_duzeltmesi_tezgah_kadrajini_varsaymaz(self):
        correction = critic.positive_correction("ham native seste istenmeyen konuşma var")
        lowered = correction.lower()
        self.assertNotIn("hands", lowered)
        self.assertNotIn("object", lowered)
        self.assertIn("silent", lowered)

    def test_ses_duzeltmesi_hala_foley_istiyor(self):
        correction = critic.positive_correction("unwanted music in the audio")
        self.assertIn("foley", correction.lower())


if __name__ == "__main__":
    unittest.main()
