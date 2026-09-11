"""Music-free delivery: bible.music False skips the bed, mastering still runs.

wild-encounter (2026-09-11) drops its music bed and keeps the diegetic sound.
The measured risk is a silent video: the music-free body sits at -17.6 LUFS,
so the delivery depends on mastering running on that body even when no music
is produced. These tests pin the engine behavior with a synthetic bible; they
never read a live channel config.
"""

from __future__ import annotations

import ast
from pathlib import Path
from unittest import mock

from series import produce
from series.bible import Bible


def _bible(*, music: bool, master_lufs=-14) -> Bible:
    series = {
        "slug": "music-off-proof",
        "title": "Music Off Proof",
        "engine": "omni",
        "state_machine_version": 2,
        "qc": {"enabled": True, "require_all_shots": True},
        "chain_frames": False,
    }
    if master_lufs is not None:
        series["master_lufs"] = master_lufs
    return Bible({
        "series": series,
        "music": music,
        "narration": None,
        "characters": [],
        "environments": [],
        "props": [],
    })


def _plan() -> dict:
    # A leftover per-episode music prompt must not switch the bed back on.
    return {
        "episode": {"number": 6, "title": "Proof"},
        "music": "a sparse low bed that should never be generated",
        "shots": [{"n": n, "duration": "8", "prompt": f"shot {n}"} for n in (1, 2, 3)],
    }


def test_music_off_returns_the_native_body_untouched(tmp_path: Path):
    video = tmp_path / "ep06.mp4"
    video.write_bytes(b"native-body")
    status: dict = {}

    with mock.patch(
        "core.music_generator.generate_background_music"
    ) as generator, mock.patch.object(
        produce.ffmpeg_tools, "mix_background_music"
    ) as mixer:
        result = produce._post_process(_bible(music=False), _plan(), video, status=status)

    generator.assert_not_called()
    mixer.assert_not_called()
    assert result == video
    assert result.read_bytes() == b"native-body"
    assert status["music_ok"] is False
    assert status["narration_expected"] is False


def test_music_off_reserves_no_suno_credit_even_with_a_plan_music_prompt():
    hard_cap = mock.Mock()

    reserved = produce._reserve_plan_music(_bible(music=False), _plan(), hard_cap, 6)

    assert reserved is None
    hard_cap.authorize.assert_not_called()


def test_music_off_with_music_required_is_a_hard_stop(tmp_path: Path):
    # Documents the only contradictory setup: requiring the music layer on a
    # music-free series stops the episode instead of shipping it silently.
    video = tmp_path / "ep06.mp4"
    video.write_bytes(b"native-body")

    with mock.patch("core.music_generator.generate_background_music") as generator:
        result = produce._post_process(
            _bible(music=False), _plan(), video, required_music=True
        )

    generator.assert_not_called()
    assert result is None


def _parents(tree: ast.AST) -> dict:
    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    return parents


def test_mastering_is_gated_by_master_lufs_and_never_by_music():
    produce_path = Path(produce.__file__)
    tree = ast.parse(produce_path.read_text(encoding="utf-8"))
    parents = _parents(tree)
    calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "master_audio"
    ]
    assert len(calls) == 1, "exactly one master_audio call expected in produce.py"

    guards = []
    function = None
    node = calls[0]
    while node in parents:
        node = parents[node]
        if isinstance(node, (ast.If, ast.While, ast.IfExp)):
            guards.append(ast.unparse(node.test))
        if function is None and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            function = node

    assert any("master_lufs" in guard for guard in guards), guards
    assert not any("music" in guard for guard in guards), (
        "mastering must not depend on the music branch", guards,
    )

    # The guard can also be coupled through data flow; every value bound to
    # master_lufs in the enclosing function must come from the bible field
    # alone, with no music condition folded in.
    assert function is not None
    bound = [
        ast.unparse(assign.value)
        for assign in ast.walk(function)
        if isinstance(assign, (ast.Assign, ast.AnnAssign))
        and any(
            isinstance(target, ast.Name) and target.id == "master_lufs"
            for target in (assign.targets if isinstance(assign, ast.Assign) else [assign.target])
        )
    ]
    assert bound, "master_lufs is expected to be bound in the mastering function"
    assert all(value == "bible.master_lufs" for value in bound), bound

    # The loudness target itself must be that value, not a literal that could drift
    # away from the series config (SPM round 2: the AST proof was too shallow).
    keywords = {kw.arg: ast.unparse(kw.value) for kw in calls[0].keywords}
    assert keywords.get("target_i") == "master_lufs", keywords
    assert keywords.get("target_tp") == "-1.0", keywords
