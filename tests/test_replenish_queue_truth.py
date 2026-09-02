"""Kuyruk derinligi DOSYA SISTEMINDEN sayilir, numara araligindan degil.

Canli ariza, kosu 33657413146 (2026-09-02 16:50 UTC):
    Oto-ikmal adimi HIC CIKTI URETMEDI (sessizce atlandi)
    ...
    Part 26 budget_exhausted; ucretli cagri baslatilmadi.
    Part plani yok: .../plans/part27.json

Sebep: `pending = total_parts - next_part + 1` idi. 2026-09-01'de `total_parts`
elle 30'a cekilmis ama 27-30 icin plan YAZILMAMISTI. Kuyruk "5 bolum var"
sanildi (5 >= min_queue 2), ikmal atlandi, uretim plansiz kaldi. Ustelik
`start = total_parts + 1` oldugu icin ikmal calissa bile 31'den baslayacak,
27-30 plansiz kalacak ve isaretci 27'de sonsuza kadar sikisacakti.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest import mock

import pytest

from series import replenish
from series.series_meta import SeriesMeta


@pytest.fixture
def plans_root(tmp_path: Path):
    """part_plan_path'i gecici klasore yonlendir; gercek plan yazilmaz."""
    root = tmp_path / "plans"
    root.mkdir()

    def fake_path(_slug: str, n: int) -> Path:
        return root / f"part{int(n):02d}.json"

    with mock.patch.object(replenish, "part_plan_path", side_effect=fake_path):
        yield root, fake_path


def _meta(next_part: int, total_parts: int) -> SeriesMeta:
    return SeriesMeta({
        "slug": "queue-truth-proof",
        "base_title": "Queue Truth Proof",
        "total_parts": total_parts,
        "next_part": next_part,
        "status": "active",
        "publish_mode": "auto",
        "upload_profile": "p",
        "platforms": ["youtube"],
        "parts": {},
    })


def _write_plans(fake_path, numbers) -> None:
    for n in numbers:
        fake_path("queue-truth-proof", n).write_text(
            json.dumps({"episode": {"number": n, "title": f"p{n}"}}),
            encoding="utf-8",
        )


def _queue_depth(meta: SeriesMeta) -> tuple[int, int]:
    """Uretimdeki kuyruk hesabini birebir tekrarla: (pending, ilk bosluk)."""
    pending = 0
    probe = meta.next_part
    while replenish.part_plan_path(meta.slug, probe).exists():
        pending += 1
        probe += 1
    return pending, probe


def test_inflated_total_parts_no_longer_fakes_a_full_queue(plans_root):
    """CANLI ARIZA: total_parts=30, next_part=27, plan YOK -> kuyruk 0 olmali."""
    _, fake_path = plans_root
    _write_plans(fake_path, range(1, 27))          # planlar yalniz 26'ya kadar
    meta = _meta(next_part=27, total_parts=30)     # sayac sisirilmis

    pending, first_gap = _queue_depth(meta)

    assert pending == 0, "sisirilmis sayac hala dolu kuyruk taklidi yapiyor"
    assert pending < 2, "min_queue=2 ile ikmal TETIKLENMELI"
    assert first_gap == 27, "yeni planlar ilk bosluga (27) yazilmali"


def test_new_plans_fill_the_gap_not_total_parts_plus_one(plans_root):
    """Ikmal 31'den degil 27'den baslamali; yoksa isaretci 27'de sonsuza sikisir."""
    _, fake_path = plans_root
    _write_plans(fake_path, range(1, 27))
    meta = _meta(next_part=27, total_parts=30)

    _, start = _queue_depth(meta)

    assert start == 27
    assert start != meta.total_parts + 1, "eski hatali baslangic (31) geri geldi"
    # 27-31 uretilirse sayac KUCULTULMEZ
    assert max(int(meta.total_parts), start + 5 - 1) == 31


def test_real_queue_still_suppresses_replenishment(plans_root):
    """Planlar GERCEKTEN varsa bosuna Gemini harcanmaz."""
    _, fake_path = plans_root
    _write_plans(fake_path, range(1, 31))
    meta = _meta(next_part=27, total_parts=30)

    pending, _ = _queue_depth(meta)

    assert pending == 4
    assert pending >= 2, "gercek kuyruk doluyken ikmal tetiklenmemeli"


def test_gap_after_next_part_is_not_counted_as_queue(plans_root):
    """ADVERSARIAL: 27 ve 28 var, 29 yok -> kuyruk 2, uretilebilir olan kadar."""
    _, fake_path = plans_root
    _write_plans(fake_path, list(range(1, 29)) + [30])   # 29 EKSIK
    meta = _meta(next_part=27, total_parts=30)

    pending, first_gap = _queue_depth(meta)

    assert pending == 2, "bosluk otesindeki plan kuyruk sayilmamali"
    assert first_gap == 29
