"""ROCK 2 aile rotasyonu oto-ikmal regresyonları, tamamen çevrimdışı."""

import copy
import json
import pathlib
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from series import replenish
from series.bible import Bible
from series.series_meta import SeriesMeta
from _archived_fixture import archived_search_roots


sys.stdout.reconfigure(encoding="utf-8")


# Bu testler flashpoints yapilandirmasini okur. Seri 2026-09-13'te ARSIVLENDI
# (Ihsan karari: kanal gelecek temali yeni bir konsepte geciyor), yani veri artik
# DONDURULMUS fixture'dan gelir ve ilerlemez. Sabit part numarasi yazmak yine de
# YASAK: asagidaki `live_position()` turetme mantigi, seri bir gun geri
# acilirsa dogru calismaya devam etsin diye korunuyor.
# (2026-08-07: ikmal canlida part 6-10'u yazdi, sabit "6" varsayan surum kirilmisti.)


def flashpoints_context():
    with archived_search_roots():
        meta = SeriesMeta.load("flashpoints")
        bible = Bible.load("flashpoints")
        history = replenish._episode_history("flashpoints")
    if meta is None or bible is None:
        raise AssertionError("flashpoints gerçek yapılandırması yüklenemedi")
    return meta, bible, meta.auto_replenish, history


def live_position():
    """İkmalin YAZACAĞI ilk part numarası ve o part için yasak family.

    DİKKAT: geçmiş, YAYINLANAN değil PLANLANAN bölümleri kapsar (plan dosyalarından
    okunur). Bu yüzden başlangıç `meta.next_part` DEĞİL, son planın bir fazlasıdır.
    """
    _meta, _bible, _cfg, history = flashpoints_context()
    last = max((int(h["n"]) for h in history if h.get("n") is not None), default=0)
    return last + 1, replenish._previous_family(history)


def seed_for_family(cfg, family):
    """Konu havuzunda `family` ailesine ait ILK seed_id.

    Seed'i SABIT yazmak kirilgandir: dogrulayici once "family seed_id ile
    eslesiyor mu" kuralini isletir, yani ailesi tutmayan bir seed verildiginde
    test'in olcmek istedigi ARDISIK-AILE kurali hic calismaz. Yasak aile
    kosu aninda turetildigi icin seed de burada turetilir.
    """
    for entry in cfg.get("topic_pool") or []:
        if entry.get("family") == family:
            # Havuz girdisi anahtari "id", plandaki karsiligi "seed_id".
            return entry.get("seed_id", entry.get("id"))
    raise AssertionError(f"konu havuzunda '{family}' ailesinden seed yok")


def pool_markers(start, end):
    return (f"RUNTIME UNUSED TOPIC POOL FOR FIRST EPISODE {start}.",
            f"RUNTIME UNUSED TOPIC POOL FOR LATER EPISODES {start + 1}-{end}.")


def decode_pool_after(contents, marker):
    tail = contents.split(marker, 1)[1]
    start = tail.index("[")
    pool, _ = json.JSONDecoder().raw_decode(tail[start:])
    return pool


def model_plan(number, seed_id, family, title):
    return {
        "episode": {"number": number, "title": title},
        "synopsis": "A specific verified historical event is reconstructed from surviving records.",
        "hook_shot": 1,
        "narration": (
            "In 1850, this verified historical event overturned expectations as witnesses watched "
            "the extraordinary moment unfold, leaving physical evidence that researchers and "
            "public records still document clearly today."
        ),
        "family": family,
        "seed_id": seed_id,
        "music": (
            "Fast tense percussion with sharp frame drums, low strings, metallic pulses, and urgent "
            "bass drives immediately forward, sustains pressure, then stops abruptly mid-rhythm "
            "for looping."
        ),
        "title_card": {"title": "Archive Evidence", "subtitle": "History, 1850"},
        "shots": [
            {
                "n": 1,
                "duration": "8",
                "prompt": (
                    "Vertical close view of period hands moving a documented historical object "
                    "through hard window light as witnesses react in the background."
                ),
                "seed": None,
            },
            {
                "n": 2,
                "duration": "8",
                "prompt": (
                    "Tight macro view of the surviving evidence turning under lamplight while "
                    "the same deliberate action continues and returns toward the opening frame."
                ),
                "seed": None,
            },
        ],
    }


class Rock2ReplenishFamilyTests(unittest.TestCase):
    # flashpoints ARSIVLENDI: seri klasoru canli agacta yok. Yama SINIF
    # duzeyinde durur cunku `generate_plans` gibi cagrilar geçmisi KENDI
    # icinde yeniden okur; yalniz yardimci fonksiyonu sarmalamak yetmez
    # (yama disinda gecmis BOS doner ve aile kurali hic islemez).
    @classmethod
    def setUpClass(cls):
        cls._arsiv = archived_search_roots()
        cls._arsiv.start()

    @classmethod
    def tearDownClass(cls):
        cls._arsiv.stop()

    def test_prompt_names_forbidden_family_and_filters_only_first_position(self):
        meta, bible, cfg, history = flashpoints_context()
        start, forbidden = live_position()
        self.assertTrue(forbidden, "geçmişte family taşıyan bölüm bulunmalı")
        self.assertEqual(history[-1]["n"], start - 1)

        contents, system_instruction = replenish._build_prompt(
            meta, bible, cfg, start, 5, history, calibration={}
        )
        quoted = json.dumps(forbidden, ensure_ascii=False)
        exact_rule = (
            f'- CRITICAL FAMILY BLOCK FOR EPISODE {start}: The previous episode used '
            f'{quoted}, so episode {start} must not use {quoted}.'
        )
        self.assertIn(exact_rule, system_instruction)

        first_marker, later_marker = pool_markers(start, start + 4)
        first_pool = decode_pool_after(contents, first_marker)
        later_pool = decode_pool_after(contents, later_marker)
        stored_unused = replenish._unused_topics(cfg, history)

        self.assertTrue(all(item["family"] != forbidden for item in first_pool))
        # Yasak ailenin tohumları HAVUZDAN SİLİNMEZ, yalnız ilk pozisyonda sunulmaz.
        if any(item["family"] == forbidden for item in stored_unused):
            self.assertTrue(any(item["family"] == forbidden for item in later_pool))

    def test_validator_rejects_history_repeat_and_names_forbidden_family(self):
        _meta, bible, cfg, history = flashpoints_context()
        start, forbidden = live_position()
        self.assertTrue(forbidden)
        repeated = model_plan(
            start, 2, forbidden, "How Oxford Predated An Empire In 1096!"
        )
        errors = replenish._validate_batch(
            [repeated], bible, start, 1, set(), cfg, history, {}
        )
        family_errors = [error for error in errors if "ardışık iki part" in error]
        self.assertEqual(len(family_errors), 1)
        self.assertIn(f"part {start}", family_errors[0])
        self.assertIn(forbidden, family_errors[0])

    def test_generation_exhausts_attempts_and_final_report_names_rule_and_family(self):
        meta, bible, cfg, _history = flashpoints_context()
        start, forbidden = live_position()
        self.assertTrue(forbidden)
        seed = seed_for_family(cfg, forbidden)

        def rejected_response(*_args, **_kwargs):
            return {
                "episodes": [copy.deepcopy(model_plan(
                    start, seed, forbidden, "How Oxford Predated An Empire In 1096!"
                ))]
            }

        with mock.patch.object(replenish, "_gen_json", side_effect=rejected_response) as gemini:
            with self.assertRaises(RuntimeError) as raised:
                replenish.generate_plans(meta, bible, cfg, start, 1, calibration={})

        self.assertEqual(gemini.call_count, 6)  # ROCK 4: format doğrulaması için deneme sayısı 3→6
        message = str(raised.exception)
        self.assertIn("ardışık iki part aynı family", message)
        self.assertIn(forbidden, message)

    def test_validator_preserves_cross_batch_family_guard(self):
        _meta, bible, cfg, history = flashpoints_context()
        start, forbidden = live_position()
        # Yasak OLMAYAN bir aile seç ki hata yalnız batch içi tekrardan gelsin.
        families = [str(f) for f in (cfg.get("families") or []) if str(f) != forbidden]
        self.assertTrue(families, "kanonik aile listesi boş olamaz")
        picked = families[0]
        episodes = [
            model_plan(start, 9, picked, "The Real Reason Tomato Pills Were Medicine"),
            model_plan(start + 1, 21, picked, "The Real Reason The Moon Hid The Great Wall"),
        ]
        errors = replenish._validate_batch(
            episodes, bible, start, 2, set(), cfg, history, {}
        )
        family_errors = [error for error in errors if "ardışık iki part" in error]
        self.assertEqual(len(family_errors), 1)
        self.assertIn(f"part {start + 1}", family_errors[0])
        self.assertIn(picked, family_errors[0])


if __name__ == "__main__":
    unittest.main()
