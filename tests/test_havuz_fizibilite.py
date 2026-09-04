"""Oto-ikmal konu havuzu şeması ve tam parti fizibilitesi için ağsız testler."""

import copy
import json
from collections import Counter
from contextlib import ExitStack
from functools import lru_cache
from unittest import mock

import pytest

from series import bible as bible_module
from series import replenish
from series.bible import Bible
from series.series_meta import SeriesMeta


REQUIRED_SERIES = {"event-horizon", "flashpoints"}


def _configured_integer_pools():
    """Integer kimlikli havuz şeması yapılandırılmış etkin serileri döndür."""
    configured = {}
    for slug, folder in bible_module.all_series_dirs().items():
        data = json.loads((folder / "series.json").read_text(encoding="utf-8"))
        cfg = data.get("auto_replenish")
        if (
            isinstance(cfg, dict)
            and cfg.get("enabled") is True
            and isinstance(cfg.get("topic_pool"), list)
        ):
            configured[slug] = (data, cfg)
    return configured


def _has_complete_family_order(families, previous_family, batch):
    """Seçilebilir tohumlardan ``batch`` uzunluğunda geçerli bir sıra var mı?"""
    counts = Counter(families)
    names = tuple(sorted(counts))
    initial = tuple(counts[name] for name in names)

    @lru_cache(maxsize=None)
    def search(remaining_counts, previous, slots):
        if slots == 0:
            return True
        for index, family in enumerate(names):
            if family == previous or remaining_counts[index] == 0:
                continue
            next_counts = list(remaining_counts)
            next_counts[index] -= 1
            if search(tuple(next_counts), family, slots - 1):
                return True
        return False

    return search(initial, previous_family, batch)


CONFIGURED_POOLS = _configured_integer_pools()


def test_integer_topic_pool_scope_includes_both_locked_series():
    assert REQUIRED_SERIES.issubset(CONFIGURED_POOLS), sorted(CONFIGURED_POOLS)


@pytest.mark.parametrize("slug", sorted(CONFIGURED_POOLS))
def test_installed_pool_schema_and_effective_batch_are_feasible(slug):
    _, cfg = CONFIGURED_POOLS[slug]
    pool = cfg["topic_pool"]
    families = cfg.get("families") or []
    ids = [item.get("id") if isinstance(item, dict) else None for item in pool]

    assert all(isinstance(item, dict) for item in pool), f"{slug}: havuz girdileri nesne olmalı"
    assert all(type(seed_id) is int for seed_id in ids), f"{slug}: tüm id'ler bool olmayan int olmalı"
    assert len(ids) == len(set(ids)), f"{slug}: id'ler havuz içinde benzersiz olmalı"
    assert all(
        isinstance(item.get("topic"), str) and item["topic"].strip() for item in pool
    ), f"{slug}: topic boş olmayan string olmalı"
    assert all(item.get("family") in families for item in pool), (
        f"{slug}: tüm family değerleri kanonik olmalı"
    )

    history = replenish._episode_history(slug)
    assert history, f"{slug}: plan geçmişi bulunamadı"
    previous_family = replenish._previous_family(history)
    unused = replenish._unused_topics(cfg, history)
    batch = min(10, max(1, int(cfg.get("batch", replenish.DEFAULT_BATCH))), len(unused))
    unused_families = [item["family"] for item in unused]

    problems = []
    if not any(family != previous_family for family in unused_families):
        problems.append(
            f"son family {previous_family!r} dışında kullanılmamış tohum yok; "
            f"kalan family'ler={unused_families!r}"
        )
    if not _has_complete_family_order(unused_families, previous_family, batch):
        problems.append(
            f"etkin batch={batch} için tam geçerli sıralama yok; "
            f"son family={previous_family!r}, kalan family'ler={unused_families!r}"
        )
    assert not problems, f"{slug}: " + "; ".join(problems)


@pytest.mark.parametrize(
    ("case", "topic_pool"),
    [
        (
            "int olmayan id",
            [
                {"id": "1", "topic": "Invalid id topic.", "family": "alpha"},
                {"id": 2, "topic": "Valid topic.", "family": "beta"},
            ],
        ),
        (
            "tekrarlı id",
            [
                {"id": 1, "topic": "First topic.", "family": "alpha"},
                {"id": 1, "topic": "Second topic.", "family": "beta"},
            ],
        ),
        (
            "bool id",
            [{"id": True, "topic": "Invalid bool id topic.", "family": "alpha"}],
        ),
        (
            "boş topic",
            [{"id": 1, "topic": "  ", "family": "alpha"}],
        ),
        (
            "kanonik olmayan family",
            [{"id": 1, "topic": "Valid topic.", "family": "gamma"}],
        ),
    ],
)
def test_invalid_pool_fails_through_replenish_without_gemini_or_mutation(
    case, topic_pool
):
    slug = "invalid-pool"
    cfg = {
        "enabled": True,
        "batch": 1,
        "min_queue": 2,
        "shots": 2,
        "shot_seconds": "6",
        "families": ["alpha", "beta"],
        "topic_pool": topic_pool,
    }
    meta = SeriesMeta({
        "slug": slug,
        "base_title": slug,
        "status": "active",
        "total_parts": 0,
        "next_part": 1,
        "auto_replenish": cfg,
    })
    bible = Bible({
        "series": {"slug": slug, "title": slug, "chain_frames": False},
        "art_style": "Network-free test style.",
        "characters": [],
        "environments": [],
        "props": [],
    })
    before = copy.deepcopy(meta.data)
    missing_plan = mock.Mock()
    missing_plan.exists.return_value = False

    with ExitStack() as stack:
        stack.enter_context(mock.patch.object(replenish.SeriesMeta, "load", return_value=meta))
        stack.enter_context(mock.patch.object(replenish.Bible, "load", return_value=bible))
        stack.enter_context(mock.patch.object(replenish, "_load_calibration", return_value={}))
        stack.enter_context(
            mock.patch.object(replenish, "part_plan_path", return_value=missing_plan)
        )
        stack.enter_context(mock.patch.object(replenish, "_episode_history", return_value=[]))
        stack.enter_context(
            mock.patch.object(replenish, "_doctrine_gate", return_value="a" * 64)
        )
        stack.enter_context(mock.patch.object(replenish, "_alert"))
        write_plan = stack.enter_context(mock.patch.object(replenish, "atomic_write_json"))
        gemini = stack.enter_context(
            mock.patch.object(replenish, "_gen_json", return_value={"episodes": []})
        )
        save = stack.enter_context(mock.patch.object(meta, "save"))
        result = replenish.replenish(slug)

    assert result is False, case
    gemini.assert_not_called()
    write_plan.assert_not_called()
    save.assert_not_called()
    assert meta.data == before, case
