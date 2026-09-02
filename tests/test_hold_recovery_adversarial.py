"""ROCK 1c düşman testleri , Visionary incelemesi.

Codex'in tests/test_hold_recovery.py dosyası sözleşmedeki (a)-(i)'yi kapsıyor.
Bu dosya diff'i okurken gördüğüm İKİ inceliği kovalar:

  1. `run_next` hem `awaiting_approval` hem `needs_human` üzerinde BLOKLUYOR.
     Ölü-mektup yolu işaretçiyi ilerlettiği için bu normalde erişilemez olmalı.
     Ama erişilebilirse kuyu YENİDEN AÇILIR, sadece adı değişmiş olur.
  2. `_continue_after_terminal` kendini `run_next` üzerinden çağırıyor. Arka arkaya
     terminal olan bölümlerde özyineleme derinliği ve SONLANMA kanıtlanmalı.
"""
from __future__ import annotations

import json
from unittest import mock

import pytest

from series.bible import Bible
from series.produce import ProduceResult
from series.series_meta import SeriesMeta
from series import series_runner
from tests.test_hold_recovery import _runner_stack, _plan


def _bible(slug="advers", version=2):
    return Bible({
        "series": {"slug": slug, "title": slug, "engine": "omni",
                   "state_machine_version": version, "credit_hard_cap": True,
                   "credit_hard_cap_value": 800, "durable_credit_ledger": True},
        "characters": [], "environments": [], "props": [],
    })


def _meta(slug="advers", total=4, next_part=1, parts=None):
    return SeriesMeta({
        "slug": slug, "base_title": slug, "total_parts": total,
        "next_part": next_part, "status": "active", "publish_mode": "auto",
        "upload_profile": "p", "platforms": ["youtube"],
        "parts": parts or {},
    })


# ---------------------------------------------------------------------------
# 1. Kuyu YENİDEN açılıyor mu? İşaretçi needs_human'a bakabilir mi?
# ---------------------------------------------------------------------------

def test_migration_never_leaves_pointer_on_a_blocking_state(tmp_path):
    """Göç, işaretçinin durduğu bölümü BLOKLAYAN bir duruma sokmamalı.

    Eski bozuk kayıtta `retry_count` alanı YOKTUR (yeni alan) ve
    `last_reason_code` da yoktur -> UNKNOWN + 0 -> qc_retry beklenir.
    qc_retry bloklanmaz, yani hat yeniden üretmeye devam eder.
    Bu test bunu KİLİTLER: göç sonrası işaretçideki durum asla
    awaiting_approval/needs_human olmamalı.
    """
    meta = _meta(next_part=2, parts={
        "2": {"status": "awaiting_approval", "hold_reason": "server"},
    })
    # Sentetik fixture gercek series_data/ agacini kirletmesin.
    with mock.patch.object(meta, "save"):
        series_runner.migrate_malformed_approval_holds(meta, _bible())
    state = meta.get_part(2)["status"]
    assert state not in ("awaiting_approval", "needs_human"), (
        f"göç işaretçiyi bloklayan duruma soktu: {state} , kuyu yeniden açıldı"
    )
    assert state == "qc_retry"


def test_migration_of_exhausted_record_would_block_the_channel(tmp_path):
    """Bilinen sınır: retry_count>=3 taşıyan bir kayıt göçte needs_human olur.

    Ölü-mektup yolu bu durumu işaretçiyi ilerleterek yazdığı için üretimde
    erişilemez olmalıdır. Yine de DAVRANIŞI kayıt altına alıyoruz: eğer böyle
    bir kayıt işaretçide durursa `run_next` bloklar ve hat susar. Bu test
    kırmızıya dönerse, ya göç ya da blok kuralı değişmiş demektir.
    """
    meta = _meta(next_part=2, parts={
        "2": {"status": "awaiting_approval", "retry_count": 3, "hold_reason": "x"},
    })
    with mock.patch.object(meta, "save"):
        series_runner.migrate_malformed_approval_holds(meta, _bible())
    assert meta.get_part(2)["status"] == "needs_human"
    # ve bu durumda run_next gerçekten bloklar (işaretçi ilerlemez)
    with mock.patch.object(series_runner, "SeriesMeta") as SM, \
         mock.patch("series.bible.Bible.load", return_value=_bible()), \
         mock.patch.object(series_runner.produce, "produce_episode") as prod:
        SM.load.return_value = meta
        ok = series_runner.run_next("advers", publish=False)
    assert ok is True, "bloklanan bölüm başarısızlık gibi raporlanmamalı"
    assert prod.call_count == 0, "bloklu durumda üretim çağrılmamalı"
    assert meta.next_part == 2, "blok işaretçiyi ilerletmemeli"


def test_dead_letter_never_parks_pointer_on_needs_human():
    """Ölü-mektup yazıldığında işaretçi O bölümün ÖTESİNE geçmeli.

    Kuyunun yeniden açılmamasının tek garantisi budur.
    """
    meta = _meta(next_part=1, total=3, parts={"1": {"status": "qc_retry", "retry_count": 2}})
    res = ProduceResult("generation_fail", reason="yine", reason_code="UNKNOWN")
    # Sentetik fixture gercek series_data/advers durumunu veya alarm outbox'ini kirletmesin.
    with mock.patch.object(meta, "save_atomic"), mock.patch.object(series_runner, "_alert"):
        advanced = series_runner._record_recoverable_failure(meta, 1, res)
    assert advanced is True
    assert meta.get_part(1)["status"] == "needs_human"
    assert meta.next_part == 2, "işaretçi ölü-mektubun üzerinde bırakıldı , kuyu!"


def test_terminalize_refuses_when_pointer_moved_underneath():
    """Yarış koruması: n != next_part ise atomik geçiş REDDEDİLMELİ."""
    meta = _meta(next_part=5, total=9)
    with pytest.raises(ValueError):
        meta.terminalize_and_advance(4, "needs_human")


# ---------------------------------------------------------------------------
# 2. Özyineleme: arka arkaya terminal bölümlerde sonlanıyor mu?
# ---------------------------------------------------------------------------

def test_consecutive_terminal_episodes_terminate_and_do_not_recurse_forever(tmp_path):
    """Kalan TÜM bölümler bütçe yüzünden terminal olursa run_next SONLANMALI.

    `_continue_after_terminal` kendini run_next uzerinden cagiriyor; her cagri
    isaretciyi ilerlettigi icin sonlanmali ve seri `completed` olmali.
    """
    total = 6
    meta = _meta(next_part=1, total=total)
    plan_path = tmp_path / "p.json"
    plan_path.write_text(json.dumps(_plan(1)), encoding="utf-8")
    calls = {"n": 0}

    def fake_budget(slug, n, bible, plan):
        calls["n"] += 1
        return ProduceResult("generation_fail", reason="butce yok",
                             reason_code="BUDGET_EXHAUSTED")

    def producer(*a, **k):
        raise AssertionError("butce kapisina takilan bolumde URETIM cagrildi")

    with _runner_stack(meta, _bible(), plan_path, _plan(1), producer), \
         mock.patch.object(series_runner, "_budget_failure", side_effect=fake_budget):
        series_runner.run_next("advers", publish=False)

    assert calls["n"] <= total, f"ozyineleme bolum sayisini asti: {calls['n']}"
    assert meta.next_part > total, "isaretci sonuna kadar ilerlemedi"
    assert meta.status == "completed"
    for i in range(1, total + 1):
        assert meta.get_part(i)["status"] == "budget_exhausted"


def test_budget_gate_runs_before_credit_reservation(tmp_path):
    """Butce kapisi kredi REZERVASYONUNDAN once calismali; sifir harcama."""
    meta = _meta(next_part=1, total=1)
    plan_path = tmp_path / "p.json"
    plan_path.write_text(json.dumps(_plan(1)), encoding="utf-8")

    def producer(*a, **k):
        raise AssertionError("butce yetersizken uretim cagrildi")

    budget_hit = ProduceResult("generation_fail", reason="yok",
                               reason_code="BUDGET_EXHAUSTED")
    with _runner_stack(meta, _bible(), plan_path, _plan(1), producer), \
         mock.patch.object(series_runner, "_budget_failure", return_value=budget_hit), \
         mock.patch.object(series_runner.credit_gate, "reserve") as reserve:
        series_runner.run_next("advers", publish=False)

    assert reserve.call_count == 0, "butce yetersizken kredi REZERVE EDILDI"
    assert meta.get_part(1)["status"] == "budget_exhausted"


# ---------------------------------------------------------------------------
# 3. Sürüm 1 gerçekten dokunulmamış mı (12 workflow bu motoru çağırıyor)
# ---------------------------------------------------------------------------

def test_version_1_does_not_migrate_anything():
    """Filo güvenliği: sürüm 1'de göç ASLA çalışmamalı."""
    parts = {"2": {"status": "awaiting_approval", "hold_reason": "server"}}
    meta = _meta(next_part=2, parts=parts)
    changed = series_runner.migrate_malformed_approval_holds(meta, _bible(version=1))
    assert changed is False
    assert meta.get_part(2)["status"] == "awaiting_approval", "sürüm 1 kaydı değişti"


def test_version_defaults_to_1_when_missing_or_garbage():
    for raw in (None, "abc", -5, 0, [], {}):
        b = Bible({"series": {"slug": "s", "title": "s", "state_machine_version": raw},
                   "characters": [], "environments": [], "props": []})
        assert b.state_machine_version >= 1
        if raw in (None, "abc", -5, 0):
            assert b.state_machine_version == 1, f"{raw!r} güvenli varsayılana düşmedi"


def test_bible_without_the_key_is_version_1():
    b = Bible({"series": {"slug": "s", "title": "s"},
               "characters": [], "environments": [], "props": []})
    assert b.state_machine_version == 1
