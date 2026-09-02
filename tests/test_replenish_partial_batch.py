"""Oto-ikmal HEP-YA-HIC degildir: gecerli bas parca kabul edilir.

Canli ariza (2026-09-02, kosu 33658009710 ve elle calistirma): alti denemenin
ALTISINDA da gecerli bolumler uretildi, ama partide tek bir kotu kelime kalinca
besinin besi de cope gitti. Gunlukten:

    2. deneme hatalari: part 30, 31, 32   -> part 28 ve 29 TEMIZDI
    4. deneme hatalari: part 28 (yalniz)
    6. deneme hatalari: part 28 (yalniz)

min_queue yalnizca 2 oldugu icin 2. denemedeki 28+29 kanali kurtarmaya yeterdi.
Kanal bunun yerine plansiz kaldi ve uretim "Part plani yok: part27.json" ile oldu.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from unittest import mock

import pytest

from series import replenish
from series.bible import Bible
from series.series_meta import SeriesMeta


REPO = Path(__file__).resolve().parents[1]
LIVE_PLAN = REPO / "sentinal_ihsan" / "unnatural-lab" / "plans" / "part27.json"
LIVE_SERIES = REPO / "sentinal_ihsan" / "unnatural-lab" / "series.json"


@pytest.fixture(scope="module")
def live_cfg() -> dict:
    return json.loads(LIVE_SERIES.read_text(encoding="utf-8-sig"))["auto_replenish"]


@pytest.fixture(scope="module")
def bible() -> Bible:
    return Bible.load("unnatural-lab")


# Ardisik iki bolum ayni family'yi kullanamaz; fixture bunu numaraya gore
# dondurur ki testin konusu (kismi kabul) family kuraliyla karismasin.
_FAMILIES = ("impossible-state-change", "reversed-physics",
             "impossible-material", "impossible-behaviour")


def _episode(number: int, *, title: str, broken: bool = False) -> dict:
    """Canli, dogrulanmis part27 planindan tureyen gercek sekilli bolum."""
    plan = json.loads(LIVE_PLAN.read_text(encoding="utf-8-sig"))
    plan["episode"] = {"number": number, "title": title}
    plan["family"] = _FAMILIES[number % len(_FAMILIES)]
    if broken:
        # Canli arizanin baskin sebebi: shot prompt'unda olumsuz dil.
        plan["shots"][0]["prompt"] += " The frost does not melt on the warm stone."
    return plan


def _titles(episodes) -> list[str]:
    return [e["episode"]["title"] for e in episodes]


def test_live_shaped_episode_is_actually_valid(bible, live_cfg):
    """Once temeli kanitla: uretilen fixture GERCEKTEN dogrulamayi geciyor."""
    errors = replenish._validate_batch(
        [_episode(28, title="Something Is WRONG With This ICE CUBE A")],
        bible, 28, 1, set(), live_cfg, [], None,
    )
    assert errors == [], errors


def test_broken_episode_is_actually_rejected(bible, live_cfg):
    """Ve bozuk fixture GERCEKTEN reddediliyor , yoksa test hicbir sey kanitlamaz."""
    errors = replenish._validate_batch(
        [_episode(28, title="Something Is WRONG With This ICE CUBE B", broken=True)],
        bible, 28, 1, set(), live_cfg, [], None,
    )
    assert any("olumlu görsel dil" in e for e in errors), errors


def test_prefix_stops_at_the_first_broken_episode(bible, live_cfg):
    """CANLI SENARYO: 28, 29 temiz; 30 bozuk -> yalniz 28 ve 29 kabul edilir."""
    episodes = [
        _episode(28, title="Something Is WRONG With This ICE CUBE A"),
        _episode(29, title="Something Is WRONG With This ICE CUBE B"),
        _episode(30, title="Something Is WRONG With This ICE CUBE C", broken=True),
        _episode(31, title="Something Is WRONG With This ICE CUBE D"),
    ]
    prefix = replenish._longest_valid_prefix(
        episodes, bible, 28, set(), live_cfg, [], None
    )
    assert len(prefix) == 2
    assert _titles(prefix) == [
        "Something Is WRONG With This ICE CUBE A",
        "Something Is WRONG With This ICE CUBE B",
    ]


def test_gap_is_never_created_even_when_a_later_episode_is_clean(bible, live_cfg):
    """ADVERSARIAL: 28 bozuk, 29-31 temiz -> HICBIRI alinmaz.

    29'u yazip 28'i atlamak isaretciyi bos bir numarada kilitler; uretim
    bolumleri sirayla isler. Bosluk asla acilmamali.
    """
    episodes = [
        _episode(28, title="Something Is WRONG With This ICE CUBE A", broken=True),
        _episode(29, title="Something Is WRONG With This ICE CUBE B"),
        _episode(30, title="Something Is WRONG With This ICE CUBE C"),
    ]
    prefix = replenish._longest_valid_prefix(
        episodes, bible, 28, set(), live_cfg, [], None
    )
    assert prefix == []


def test_full_valid_batch_is_not_shortened(bible, live_cfg):
    """Hepsi temizse kismi kabul devreye GIRMEZ; tam parti aynen doner."""
    episodes = [
        _episode(28, title="Something Is WRONG With This ICE CUBE A"),
        _episode(29, title="Something Is WRONG With This ICE CUBE B"),
    ]
    errors = replenish._validate_batch(
        copy.deepcopy(episodes), bible, 28, 2, set(), live_cfg, [], None
    )
    assert errors == []


def test_generate_plans_returns_partial_instead_of_raising(bible, live_cfg, monkeypatch):
    """Alti deneme de tam partiyi gecirmezse SIFIR degil, en uzun bas parca doner."""
    meta = SeriesMeta({
        "slug": "unnatural-lab", "base_title": "Unnatural Lab", "total_parts": 30,
        "next_part": 28, "status": "active", "publish_mode": "auto",
        "upload_profile": "p", "platforms": ["youtube"], "parts": {},
    })
    batch = [
        _episode(28, title="Partial Proof A"),
        _episode(29, title="Partial Proof B"),
        _episode(30, title="Partial Proof C", broken=True),
    ]
    monkeypatch.setattr(replenish, "_episode_history", lambda slug: [])
    monkeypatch.setattr(replenish, "_build_prompt",
                        lambda *a, **k: ("contents", "sysins"))
    monkeypatch.setattr(replenish, "_gen_json",
                        lambda *a, **k: {"episodes": copy.deepcopy(batch)})
    alerts: list[str] = []
    monkeypatch.setattr(replenish, "_alert",
                        lambda slug, text: alerts.append(text))

    out = replenish.generate_plans(meta, bible, live_cfg, 28, 3, None)

    assert len(out) == 2, "kismi kabul calismadi"
    assert _titles(out) == ["Partial Proof A", "Partial Proof B"]
    assert alerts and "KISMİ" in alerts[0], "kismi kabul SESSIZ olmamali"


def test_generate_plans_still_raises_when_nothing_is_valid(bible, live_cfg, monkeypatch):
    """Ilk bolum bile bozuksa kabul edilecek bir sey YOKTUR; sessizce gecilmez."""
    meta = SeriesMeta({
        "slug": "unnatural-lab", "base_title": "Unnatural Lab", "total_parts": 30,
        "next_part": 28, "status": "active", "publish_mode": "auto",
        "upload_profile": "p", "platforms": ["youtube"], "parts": {},
    })
    batch = [
        _episode(28, title="Nothing Valid A", broken=True),
        _episode(29, title="Nothing Valid B", broken=True),
    ]
    monkeypatch.setattr(replenish, "_episode_history", lambda slug: [])
    monkeypatch.setattr(replenish, "_build_prompt",
                        lambda *a, **k: ("contents", "sysins"))
    monkeypatch.setattr(replenish, "_gen_json",
                        lambda *a, **k: {"episodes": copy.deepcopy(batch)})
    monkeypatch.setattr(replenish, "_alert", lambda slug, text: None)

    with pytest.raises(RuntimeError):
        replenish.generate_plans(meta, bible, live_cfg, 28, 2, None)


def test_full_batch_short_circuits_without_partial_scan(bible, live_cfg, monkeypatch):
    """Tam parti gecerse tek denemede doner, bosuna prefix taramasi yapilmaz."""
    meta = SeriesMeta({
        "slug": "unnatural-lab", "base_title": "Unnatural Lab", "total_parts": 30,
        "next_part": 28, "status": "active", "publish_mode": "auto",
        "upload_profile": "p", "platforms": ["youtube"], "parts": {},
    })
    batch = [
        _episode(28, title="Clean Batch A"),
        _episode(29, title="Clean Batch B"),
    ]
    calls = {"gen": 0, "prefix": 0}

    def gen(*_a, **_k):
        calls["gen"] += 1
        return {"episodes": copy.deepcopy(batch)}

    real_prefix = replenish._longest_valid_prefix

    def counting_prefix(*a, **k):
        calls["prefix"] += 1
        return real_prefix(*a, **k)

    monkeypatch.setattr(replenish, "_episode_history", lambda slug: [])
    monkeypatch.setattr(replenish, "_build_prompt",
                        lambda *a, **k: ("contents", "sysins"))
    monkeypatch.setattr(replenish, "_gen_json", gen)
    monkeypatch.setattr(replenish, "_longest_valid_prefix", counting_prefix)

    out = replenish.generate_plans(meta, bible, live_cfg, 28, 2, None)

    assert len(out) == 2
    assert calls["gen"] == 1, "tam parti gecerken fazladan Gemini cagrisi yapildi"
    assert calls["prefix"] == 0, "gereksiz prefix taramasi"


# ── Alan onarim katmani ────────────────────────────────────────────────────────

def test_repair_fixes_negative_language_and_keeps_required_anchors(
        bible, live_cfg, monkeypatch):
    """Onarim olumsuz dili temizler ve zorunlu birebir ifadeleri KORUR."""
    plan = _episode(28, title="Repair Proof A", broken=True)
    seen: dict = {}

    def fake_repair(text, rules, must_keep):
        seen["must_keep"] = list(must_keep)
        # Olumsuz cumleyi at, capalari koru.
        return text.replace(" The frost does not melt on the warm stone.", "")

    monkeypatch.setattr(replenish, "_repair_text", fake_repair)
    budget = [12]
    fixed = replenish._repair_episode_fields(plan, 20, 28, budget)

    assert fixed == 1
    assert not replenish.NEGATIVE_VIDEO_LANGUAGE.search(plan["shots"][0]["prompt"])
    card = plan["object_card"]
    assert card["descriptor"] in plan["shots"][0]["prompt"]
    assert card["anomaly_descriptor"] in plan["shots"][0]["prompt"]
    assert card["descriptor"] in seen["must_keep"]
    assert budget[0] == 11, "onarim butcesi harcanmadi"


def test_repair_that_is_still_invalid_is_rejected(bible, live_cfg, monkeypatch):
    """ADVERSARIAL: model kotu bir onarim dondurse bile orijinal KORUNUR."""
    plan = _episode(28, title="Repair Proof B", broken=True)
    original = plan["shots"][0]["prompt"]
    monkeypatch.setattr(replenish, "_repair_text",
                        lambda text, rules, keep: "the ice does not melt at all")
    fixed = replenish._repair_episode_fields(plan, 20, 28, [12])
    assert fixed == 0
    assert plan["shots"][0]["prompt"] == original, "kotu onarim yazildi"


def test_repair_that_drops_a_required_anchor_is_rejected(monkeypatch):
    """ADVERSARIAL: capayi silen onarim kabul edilmez (plan_lint'i kirardi)."""
    plan = _episode(28, title="Repair Proof C", broken=True)
    original = plan["shots"][0]["prompt"]
    monkeypatch.setattr(replenish, "_repair_text",
                        lambda text, rules, keep: "hands rest on the counter")
    assert replenish._repair_episode_fields(plan, 20, 28, [12]) == 0
    assert plan["shots"][0]["prompt"] == original


def test_repair_budget_bounds_the_number_of_calls(monkeypatch):
    """Kotu bir tur sonsuz Gemini cagrisina donusmemeli."""
    plan = _episode(28, title="Repair Proof D", broken=True)
    for shot in plan["shots"]:
        shot["violation_observation"] = "the frost never stops spreading"
    calls = {"n": 0}

    def fake_repair(text, rules, keep):
        calls["n"] += 1
        return None

    monkeypatch.setattr(replenish, "_repair_text", fake_repair)
    replenish._repair_episode_fields(plan, 20, 28, [2])
    assert calls["n"] <= 2, f"butce asildi: {calls['n']}"


def test_repair_fixes_overlong_narration(monkeypatch):
    """Anlatim kelime butcesi de onarilabilir bir alandir."""
    plan = _episode(28, title="Repair Proof E")
    plan["narration"] = " ".join(["word"] * 45)
    monkeypatch.setattr(replenish, "_repair_text",
                        lambda text, rules, keep: " ".join(["word"] * 24))
    fixed = replenish._repair_episode_fields(plan, 20, 28, [12])
    assert fixed == 1
    assert len(plan["narration"].split()) == 24


def test_clean_episode_needs_no_repair_calls(monkeypatch):
    """Temiz bolum icin tek bir onarim cagrisi bile yapilmaz."""
    plan = _episode(28, title="Repair Proof F")
    calls = {"n": 0}

    def fake_repair(text, rules, keep):
        calls["n"] += 1
        return text

    monkeypatch.setattr(replenish, "_repair_text", fake_repair)
    assert replenish._repair_episode_fields(plan, 20, 28, [12]) == 0
    assert calls["n"] == 0


def test_repair_budget_is_shared_across_all_attempts(bible, live_cfg, monkeypatch):
    """ADVERSARIAL: butce deneme basina sifirlanmamali.

    Sifirlansaydi alti deneme x REPAIR_BUDGET onarim kadar Gemini cagrisi
    yapilir ve workflow suresi yenirdi.
    """
    meta = SeriesMeta({
        "slug": "unnatural-lab", "base_title": "Unnatural Lab", "total_parts": 40,
        "next_part": 28, "status": "active", "publish_mode": "auto",
        "upload_profile": "p", "platforms": ["youtube"], "parts": {},
    })
    batch = [_episode(28, title="Budget Proof A", broken=True)]
    calls = {"n": 0}

    def fake_repair(text, rules, keep):
        calls["n"] += 1
        return None

    monkeypatch.setattr(replenish, "_episode_history", lambda slug: [])
    monkeypatch.setattr(replenish, "_build_prompt",
                        lambda *a, **k: ("contents", "sysins"))
    monkeypatch.setattr(replenish, "_gen_json",
                        lambda *a, **k: {"episodes": copy.deepcopy(batch)})
    monkeypatch.setattr(replenish, "_repair_text", fake_repair)
    monkeypatch.setattr(replenish, "_alert", lambda slug, text: None)

    with pytest.raises(RuntimeError):
        replenish.generate_plans(meta, bible, live_cfg, 28, 1, None)

    assert calls["n"] <= replenish.REPAIR_BUDGET, (
        f"butce deneme basina sifirlandi: {calls['n']} cagri")
