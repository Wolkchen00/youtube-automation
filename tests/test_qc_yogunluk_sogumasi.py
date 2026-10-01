"""1 Ekim 2026: Gemini "503 high demand" firtinasi QC'yi tek turda dusurmesin.

29 ve 30 Eylul'de dort modellik sira ~1 dakikada tukendi, bolum QC HOLD'a
gitti ve wild-encounter iki gun video cikarmadi. Soguma yalniz GECICI sunucu
hatasinda beklenir; kota, odeme, yetki ve bozuk JSON sogumayla acilmaz.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from series import critic  # noqa: E402

SERVER_503 = RuntimeError("503 UNAVAILABLE. This model is currently experiencing high demand.")


@pytest.fixture(autouse=True)
def _temiz_butce(monkeypatch):
    monkeypatch.setattr(critic, "_OVERLOAD_WAITED", 0.0)


def test_transient_server_storm_waits_then_retries():
    with mock.patch.object(critic.time, "sleep") as slept:
        assert critic._overload_cooldown("Gorsel QC", 0, "server", SERVER_503) is True
    slept.assert_called_once_with(critic.QC_OVERLOAD_COOLDOWNS[0])


@pytest.mark.parametrize("reason, error", [
    ("quota", RuntimeError("429 RESOURCE_EXHAUSTED")),
    ("billing", RuntimeError("402 prepayment credits are depleted")),
    ("auth", RuntimeError("403 PERMISSION_DENIED")),
    ("parse", ValueError("not json")),
])
def test_non_transient_classes_never_cool_down(reason, error):
    with mock.patch.object(critic.time, "sleep") as slept:
        assert critic._overload_cooldown("Gorsel QC", 0, reason, error) is False
    slept.assert_not_called()


def test_server_class_without_a_transient_marker_does_not_wait():
    """400 INVALID_ARGUMENT de 'server' sinifina duser ama beklemekle duzelmez."""
    with mock.patch.object(critic.time, "sleep") as slept:
        assert critic._overload_cooldown(
            "Gorsel QC", 0, "server", RuntimeError("400 INVALID_ARGUMENT")) is False
    slept.assert_not_called()


def test_rounds_are_finite():
    last = len(critic.QC_OVERLOAD_COOLDOWNS)
    with mock.patch.object(critic.time, "sleep") as slept:
        assert critic._overload_cooldown("Gorsel QC", last, "server", SERVER_503) is False
    slept.assert_not_called()


def test_process_cap_bounds_the_total_cooldown(monkeypatch):
    """Bolumdeki her QC cagrisi ayri ayri yedi dakika beklerse workflow 120 dakikayi asar."""
    monkeypatch.setattr(critic, "_OVERLOAD_WAITED", critic.QC_OVERLOAD_PROCESS_CAP - 10.0)
    with mock.patch.object(critic.time, "sleep") as slept:
        assert critic._overload_cooldown("Gorsel QC", 2, "server", SERVER_503) is True
        assert critic._overload_cooldown("Gorsel QC", 0, "server", SERVER_503) is False
    slept.assert_called_once_with(10.0)
    assert sum(critic.QC_OVERLOAD_COOLDOWNS) <= critic.QC_OVERLOAD_PROCESS_CAP
    assert critic.QC_OVERLOAD_PROCESS_CAP <= 1800


def test_shared_episode_budget_also_limits_the_cooldown():
    budget = critic.QCWaitBudget(waited=critic.QC_MAX_EPISODE_WAIT)
    with mock.patch.object(critic.time, "sleep") as slept:
        assert critic._overload_cooldown(
            "Gorsel QC", 0, "server", SERVER_503, budget) is False
    slept.assert_not_called()
