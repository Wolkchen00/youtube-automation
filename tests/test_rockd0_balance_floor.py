"""ROCK D0: kuresel Kie bakiye tabani.

Olculen sorun: ne bolum defteri ne deney defteri baska workflow'larin ortak bakiyeyi
tuketmesini durdurabiliyordu. Bu paket tabanin gercekten koruma yaptigini, kapalıyken
hicbir sey degistirmedigini ve yarista tek kazanan biraktigini kanitlar.
"""

import json
import pathlib
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from series import balance_floor as bf
from series.credit_gate import HardCreditCap


class FloorBase(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.state = pathlib.Path(self.tempdir.name) / "kie_reservations.json"
        patcher = mock.patch.object(bf, "STATE_PATH", self.state)
        patcher.start()
        self.addCleanup(patcher.stop)

    def set_floor(self, value):
        patcher = mock.patch.dict("os.environ", {"KIE_BALANCE_FLOOR": str(value)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def clear_floor(self):
        patcher = mock.patch.dict("os.environ", {}, clear=False)
        patcher.start()
        self.addCleanup(patcher.stop)
        import os
        os.environ.pop("KIE_BALANCE_FLOOR", None)


class DisabledByDefaultTests(FloorBase):
    """P9: taban kapaliyken davranis degismez ve bakiye SORGULANMAZ."""

    def test_absent_floor_allows_without_touching_the_balance(self):
        self.clear_floor()
        checker = mock.Mock(return_value=10.0)
        decision = bf.authorize_spend(5000, balance_checker=checker, path=self.state)
        self.assertTrue(decision.allowed)
        checker.assert_not_called()
        self.assertFalse(self.state.exists(), "taban kapaliyken defter yazilmamali")

    def test_zero_and_garbage_floor_are_treated_as_disabled(self):
        for raw in ("0", "-5", "abc", ""):
            with self.subTest(raw=raw):
                with mock.patch.dict("os.environ", {"KIE_BALANCE_FLOOR": raw}):
                    self.assertIsNone(bf.floor_value())


class FloorArithmeticTests(FloorBase):
    def test_refuses_when_the_call_would_break_the_floor(self):
        self.set_floor(1000)
        decision = bf.authorize_spend(
            800, balance_checker=lambda: 1500.0, path=self.state
        )
        self.assertFalse(decision.allowed)
        self.assertIn("taban korumasi", decision.reason)

    def test_other_owners_reservation_is_subtracted(self):
        self.set_floor(1000)
        bf.reserve("killgate", 3500, path=self.state)
        decision = bf.authorize_spend(
            800, balance_checker=lambda: 5000.0, path=self.state
        )
        self.assertFalse(decision.allowed, "baskasinin rezervasyonu hesaba katilmadi")
        self.assertEqual(decision.outstanding_others, 3500.0)
        # Rezervasyon YOKSAYILSAYDI ayni cagri gecerdi: 5000 - 1000 = 4000 >= 800.
        self.assertGreaterEqual(5000.0 - 1000.0, 800.0)

    def test_owner_may_spend_its_own_reservation(self):
        self.set_floor(1000)
        bf.reserve("killgate", 3500, path=self.state)
        decision = bf.authorize_spend(
            800, owner="killgate", balance_checker=lambda: 5000.0, path=self.state
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.consumed, 800.0)
        self.assertEqual(bf.outstanding(path=self.state), 2700.0)

    def test_balance_unreadable_is_fail_closed(self):
        self.set_floor(1000)
        decision = bf.authorize_spend(10, balance_checker=lambda: None, path=self.state)
        self.assertFalse(decision.allowed)
        self.assertIn("bakiye okunamadi", decision.reason)

    def test_corrupt_ledger_is_fatal_not_silently_empty(self):
        self.set_floor(1000)
        self.state.write_text("{bozuk", encoding="utf-8")
        with self.assertRaises(bf.BalanceFloorError):
            bf.authorize_spend(10, balance_checker=lambda: 9999.0, path=self.state)


class InFlightTests(FloorBase):
    """Yetkilendirilen ama henuz uzlastirilmayan cagri da korunur."""

    def test_second_concurrent_call_is_refused(self):
        self.set_floor(1000)
        first = bf.authorize_spend(600, balance_checker=lambda: 2000.0, path=self.state)
        self.assertTrue(first.allowed)
        self.assertIsNotNone(first.inflight_id)
        second = bf.authorize_spend(600, balance_checker=lambda: 2000.0, path=self.state)
        self.assertFalse(second.allowed, "ucusta kayit korumadi: ikisi de gecti")

    def test_settle_releases_the_inflight_hold(self):
        self.set_floor(1000)
        first = bf.authorize_spend(600, balance_checker=lambda: 2000.0, path=self.state)
        bf.settle(None, 600, 600, inflight_id=first.inflight_id, path=self.state)
        self.assertEqual(bf.outstanding(path=self.state), 0.0)
        again = bf.authorize_spend(600, balance_checker=lambda: 2000.0, path=self.state)
        self.assertTrue(again.allowed)

    def test_expired_inflight_stops_protecting(self):
        self.set_floor(1000)
        bf.authorize_spend(600, balance_checker=lambda: 2000.0, path=self.state)
        data = json.loads(self.state.read_text(encoding="utf-8"))
        data["reservations"][0]["expires_at"] = time.time() - 1
        self.state.write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(bf.outstanding(path=self.state), 0.0)

    def test_parallel_threads_produce_exactly_one_winner(self):
        self.set_floor(1000)
        results = []
        barrier = threading.Barrier(2)

        def attempt():
            barrier.wait()
            results.append(bf.authorize_spend(
                600, balance_checker=lambda: 2000.0, path=self.state
            ).allowed)

        threads = [threading.Thread(target=attempt) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(sorted(results), [False, True], f"yaris sonucu: {results}")


class SettleTests(FloorBase):
    def test_unspent_estimate_returns_to_the_owner_reservation(self):
        self.set_floor(1000)
        bf.reserve("killgate", 1000, path=self.state)
        bf.authorize_spend(500, owner="killgate", balance_checker=lambda: 9999.0,
                           path=self.state)
        self.assertEqual(bf.outstanding(path=self.state), 500.0)
        bf.settle("killgate", 500, 300, path=self.state)
        self.assertEqual(bf.outstanding(path=self.state), 700.0)


class EpisodeGateIntegrationTests(FloorBase):
    """Bolum kapisi tabana gercekten bagli mi?"""

    def test_episode_cap_refuses_when_the_floor_refuses(self):
        self.set_floor(1000)
        bf.reserve("killgate", 4000, path=self.state)
        cap = HardCreditCap(cap=10_000, spent=0.0)
        with mock.patch.object(bf, "STATE_PATH", self.state), \
                mock.patch("core.kie_api.check_credit", return_value=4500.0):
            allowed = cap.authorize("main_shot", "omni", "6")
        self.assertFalse(allowed)
        self.assertIn("ortak bakiye tabani", cap.blocked_reason or "")

    def test_episode_cap_untouched_when_floor_is_disabled(self):
        self.clear_floor()
        cap = HardCreditCap(cap=10_000, spent=0.0)
        with mock.patch("core.kie_api.check_credit") as checker:
            self.assertTrue(cap.authorize("main_shot", "omni", "6"))
        checker.assert_not_called()
        self.assertIsNone(cap.blocked_reason)

    def test_settling_the_actual_cost_releases_the_inflight_hold(self):
        self.set_floor(1000)
        cap = HardCreditCap(cap=10_000, spent=0.0)
        with mock.patch.object(bf, "STATE_PATH", self.state),                 mock.patch("core.kie_api.check_credit", return_value=5000.0):
            self.assertTrue(cap.authorize("main_shot", "omni", "6"))
            held = bf.outstanding(path=self.state)
            self.assertGreater(held, 0.0, "yetkilendirme ucusta kayit birakmadi")
            self.assertTrue(cap.settle_last(84))
        self.assertEqual(
            bf.outstanding(path=self.state), 0.0,
            "gercek maliyet islendigi halde koruma birakilmadi",
        )

    def test_owner_tagged_episode_may_use_its_reservation(self):
        self.set_floor(1000)
        bf.reserve("killgate", 4000, path=self.state)
        cap = HardCreditCap(cap=10_000, spent=0.0, balance_owner="killgate")
        with mock.patch.object(bf, "STATE_PATH", self.state), \
                mock.patch("core.kie_api.check_credit", return_value=4500.0):
            allowed = cap.authorize("main_shot", "omni", "6")
        self.assertTrue(allowed, "kill-gate kendi rezervasyonunu harcayamadi")


if __name__ == "__main__":
    unittest.main()
