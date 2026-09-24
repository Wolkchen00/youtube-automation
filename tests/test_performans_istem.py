from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from series import replenish
from series.bible import Bible
from series.performans_istem import MAX_BLOCK_CHARS, build_performance_block
from series.series_meta import SeriesMeta


def _part(number: int, label: str, score: float, *, views: int = 100) -> dict:
    return {
        "part": number,
        "subtitle": f"Fallback {number}",
        "etiket": label,
        "puan": score,
        "yargi_anligi": "oturmus",
        "oranlar": {"youtube": score},
        "puanlanan_metrikler": {"youtube": {"views": views}},
    }


def _plan(number: int, *, synopsis: str = "A concise episode synopsis.") -> dict:
    return {
        "episode": {"number": number, "title": f"Title {number}"},
        "synopsis": synopsis,
        "family": f"family-{number}",
        "seed_id": number,
        "card_topic": f"topic-{number}",
        "object_card": {"name": f"object-{number}"},
    }


def _scored(parts: list[dict]) -> dict:
    return {"medyanlar": {"oturmus": {"youtube": 100}}, "parts": parts}


def _prompt_inputs(data: dict | None = None):
    meta_data = {
        "slug": "feedback-test",
        "base_title": "Feedback Test",
        "logline": "A deterministic series.",
    }
    if data:
        meta_data.update(data)
    meta = SeriesMeta(meta_data)
    bible = Bible({
        "series": {
            "slug": "feedback-test",
            "title": "Feedback Test",
            "engine": "omni",
            "chain_frames": False,
        },
        "art_style": "Natural vertical footage.",
        "music": False,
        "narration": {},
        "characters": [],
        "environments": [],
        "props": [],
    })
    cfg = {"shots": 1, "shot_seconds": "8"}
    return meta, bible, cfg


def test_block_has_winners_losers_plan_fields_and_rounded_ratios():
    parts = [
        _part(1, "kazanan", 2.64, views=1234),
        _part(2, "kaybeden", 0.24, views=12),
        *[_part(n, "orta", 1.0) for n in range(3, 7)],
    ]
    block = build_performance_block(_scored(parts), {n: _plan(n) for n in range(1, 7)})

    assert "measured on this series' own history, not a universal target" in block
    assert "Title 1" in block and "Title 2" in block
    assert "family=family-1" in block and "seed_id=1" in block
    assert "card_topic=topic-1" in block and "object=object-1" in block
    assert "youtube 1234 views/2.6x @7d+" in block
    assert "youtube 12 views/0.2x @7d+" in block
    assert "Lean toward the shared traits of winners" in block
    assert "Move away from the shared traits of losers" in block
    assert "Never repeat an existing subject or title" in block
    assert "Do not over-generalize from a single example" in block


def test_needs_six_measured_parts_and_a_winner_or_loser():
    five = [_part(1, "kazanan", 2.0), *[_part(n, "orta", 1.0) for n in range(2, 6)]]
    assert build_performance_block(_scored(five), {n: _plan(n) for n in range(1, 6)}) == ""
    six_middle = [_part(n, "orta", 1.0) for n in range(1, 7)]
    assert build_performance_block(
        _scored(six_middle), {n: _plan(n) for n in range(1, 7)}
    ) == ""


def test_winner_and_loser_ordering_and_four_entry_caps():
    winners = [_part(n, "kazanan", float(n)) for n in range(1, 7)]
    losers = [_part(n, "kaybeden", n / 100) for n in range(7, 13)]
    plans = {n: _plan(n) for n in range(1, 13)}
    block = build_performance_block(_scored(winners + losers), plans)

    assert block.index("Title 6") < block.index("Title 5") < block.index("Title 4")
    assert "- Part 1:" not in block and "- Part 2:" not in block
    assert block.index("Title 7") < block.index("Title 8") < block.index("Title 9")
    assert "- Part 11:" not in block and "- Part 12:" not in block


def test_block_truncates_synopses_then_drops_tail_under_1500_chars():
    parts = [
        *[_part(n, "kazanan", 10 - n) for n in range(1, 5)],
        *[_part(n, "kaybeden", n / 100) for n in range(5, 9)],
    ]
    plans = {n: _plan(n, synopsis=(f"synopsis-{n} " * 200)) for n in range(1, 9)}
    block = build_performance_block(_scored(parts), plans)

    assert block
    assert len(block) <= MAX_BLOCK_CHARS
    assert "synopsis-1" not in block or "…" in block


def _raw_performance() -> dict:
    views = [10, 100, 100, 100, 100, 300]
    return {
        "parts": [
            {
                "part": index,
                "subtitle": f"Fallback {index}",
                # Deliberately stale and wrong; replenish must re-score.
                "etiket": "kaybeden" if index == 6 else "kazanan",
                "puan": 99,
                "olcumler": [{"yas_saat": 168, "youtube": {"views": value}}],
            }
            for index, value in enumerate(views, start=1)
        ]
    }


def _write_fixture(root: Path, document: dict | str, missing_plan: int | None = None) -> None:
    root.mkdir(parents=True, exist_ok=True)
    text = document if isinstance(document, str) else json.dumps(document)
    (root / "performans.json").write_text(text, encoding="utf-8")
    plans = root / "plans"
    plans.mkdir()
    for number in range(1, 7):
        if number == missing_plan:
            continue
        (plans / f"part{number:02d}.json").write_text(
            json.dumps(_plan(number)), encoding="utf-8"
        )


def test_loader_rescores_stale_labels_and_skips_missing_plan(tmp_path):
    _write_fixture(tmp_path, _raw_performance(), missing_plan=1)
    meta = SimpleNamespace(slug="feedback-test", data={"performance_feedback": True})
    with mock.patch.object(replenish, "data_dir", return_value=tmp_path), mock.patch.object(
        replenish, "part_plan_path", side_effect=lambda _slug, n: tmp_path / "plans" / f"part{n:02d}.json"
    ):
        block = replenish._performance_feedback_block(meta)

    assert "WINNERS" in block and "Title 6" in block
    assert "LOSERS" not in block
    assert "Title 1" not in block
    assert "youtube 300 views/3.0x @7d+" in block


def test_corrupt_performance_json_and_missing_file_return_no_block(tmp_path):
    meta = SimpleNamespace(slug="feedback-test", data={"performance_feedback": True})
    with mock.patch.object(replenish, "data_dir", return_value=tmp_path):
        assert replenish._performance_feedback_block(meta) == ""
        (tmp_path / "performans.json").write_text("{broken", encoding="utf-8")
        assert replenish._performance_feedback_block(meta) == ""


def test_flag_off_and_insufficient_data_leave_prompt_byte_identical(tmp_path):
    meta, bible, cfg = _prompt_inputs()
    baseline = replenish._build_prompt(meta, bible, cfg, 1, 1, [])

    enabled, _, _ = _prompt_inputs({"performance_feedback": True})
    _write_fixture(tmp_path, {"parts": []})
    with mock.patch.object(replenish, "data_dir", return_value=tmp_path):
        assert replenish._build_prompt(enabled, bible, cfg, 1, 1, []) == baseline


def test_test_double_without_data_keeps_baseline_prompt():
    meta, bible, cfg = _prompt_inputs()
    baseline = replenish._build_prompt(meta, bible, cfg, 1, 1, [])
    double = SimpleNamespace(
        slug=meta.slug, base_title=meta.base_title, logline=meta.logline
    )
    assert replenish._build_prompt(double, bible, cfg, 1, 1, []) == baseline


def test_flag_on_appends_memory_to_contents_not_strict_json_system(tmp_path):
    _write_fixture(tmp_path, _raw_performance())
    meta, bible, cfg = _prompt_inputs({"performance_feedback": True})
    with mock.patch.object(replenish, "data_dir", return_value=tmp_path), mock.patch.object(
        replenish, "part_plan_path", side_effect=lambda _slug, n: tmp_path / "plans" / f"part{n:02d}.json"
    ):
        contents, system = replenish._build_prompt(meta, bible, cfg, 1, 1, [])

    assert "PERFORMANCE MEMORY" in contents
    assert "Title 6" in contents and "3.0x" in contents
    assert "PERFORMANCE MEMORY" not in system
    assert "Return STRICT JSON ONLY" in system
