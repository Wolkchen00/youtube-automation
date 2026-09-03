from __future__ import annotations

from pathlib import Path

import pytest

import build


SOURCE_ROOT = Path(build.__file__).resolve().parent


def _copy_text(source: Path, destination: Path) -> None:
    build.write_utf8(destination, build.read_utf8(source))


def _beat_text(word_count: int) -> str:
    filler = " ".join("detail" for _ in range(word_count))
    intervals = (
        ("0.0", "4.0", "The rider waits above the city while water gathers nearby."),
        ("4.0", "8.0", "The rider enters the transparent slide and starts descending."),
        ("8.0", "12.0", "The connected slide banks while the city rotates continuously."),
        ("12.0", "16.0", "The landing pool approaches and grows steadily below her feet."),
        ("16.0", "20.0", "The rider reaches the pool, surfaces, and floats safely."),
    )
    return "\n\n".join(
        f"[{start}-{end}] {description} {filler}"
        for start, end, description in intervals
    )


def _route_text(
    *,
    beats: str | None = None,
    opening: str | None = None,
    voice: str | None = None,
    end_state: str | None = None,
    caption: str | None = None,
    beat_filler_words: int = 105,
    omit_field: str | None = None,
    omit_section: str | None = None,
) -> str:
    fields = {
        "SLUG": "test-city-green-rain",
        "DESTINATION": "Test City",
        "LANDMARK": "the Test Tower",
        "DURATION": "20",
        "NEON": "bright green",
        "LEGWEAR": "black full-length leggings",
        "WEATHER": "steady night rain",
        "SOURCE": "synthetic test route",
    }
    if omit_field is not None:
        fields.pop(omit_field)

    state_filler = " ".join("visible" for _ in range(35))
    values = {
        "OPENING STATE": opening
        or (
            "The rider waits barefoot above Test City with the transparent slide "
            f"visible ahead and every surface wet. {state_filler}"
        ),
        "BEATS": beats or _beat_text(beat_filler_words),
        "END STATE": end_state
        or (
            "The rider floats in the rooftop pool while Test Tower remains visible "
            f"above the surrounding buildings. {state_filler}"
        ),
        "VOICE": voice or '[0.0-2.0] "Oh my god."',
        "CAPTION": caption
        or (
            "You're falling from the Test Tower above Test City. Every second gets "
            "faster, lower, and louder.\n\n"
            "#MegaSlideFear #TestTower #WaterSlide #POVReels #CGIAdventure #ViralReels"
        ),
    }
    if omit_section is not None:
        values.pop(omit_section)

    field_block = "\n".join(f"{key}: {value}" for key, value in fields.items())
    section_block = "\n\n".join(
        f"## {name}\n\n{value}" for name, value in values.items()
    )
    return f"# ROUTE\n\n{field_block}\n\n{section_block}\n"


def _make_project(tmp_path: Path, route_text: str | None = None) -> Path:
    for name in ("MASTER-BLOCK.md", "NEGATIVES.md", "CAPTION.md"):
        _copy_text(SOURCE_ROOT / "canon" / name, tmp_path / "canon" / name)
    build.write_utf8(
        tmp_path / "routes" / "test-city-green-rain.md",
        route_text or _route_text(),
    )
    return tmp_path


def _failure(tmp_path: Path, route_text: str) -> str:
    root = _make_project(tmp_path, route_text)
    with pytest.raises(build.BuildError) as captured:
        build.build_project(root, check=True)
    return str(captured.value)


def test_valid_route_passes_and_writes_exact_outputs(tmp_path: Path) -> None:
    root = _make_project(tmp_path)
    routes = build.build_project(root, check=True)

    assert [route.slug for route in routes] == ["test-city-green-rain"]
    prompt = build.read_utf8(root / "out" / routes[0].slug / "PROMPT.txt")
    caption = build.read_utf8(root / "out" / routes[0].slug / "CAPTION.txt")
    voice = build.read_utf8(root / "out" / routes[0].slug / "VOICE.txt")
    assert prompt.startswith("FORMAT\nCreate a single continuous 20-second")
    assert "WORLD\nTest City, real, recognisable" in prompt
    assert "black full-length leggings" in prompt
    assert "<<LEGWEAR>>" not in prompt
    assert "OPENING STATE\nAt frame one: " in prompt
    assert "\n\nTIMELINE\n[0.0-4.0]" in prompt
    assert prompt.endswith(build.load_canon(root).negative + "\n")
    assert caption == build.load_route(routes[0].path, root).sections["CAPTION"] + "\n"
    assert voice == '[0.0-2.0] "Oh my god."\n'


def test_beats_gap_fails(tmp_path: Path) -> None:
    beats = _beat_text(105).replace("[4.0-8.0]", "[5.0-8.0]")
    message = _failure(tmp_path, _route_text(beats=beats))
    assert "gap from 4.0 to 5.0" in message


def test_beats_overlap_fails(tmp_path: Path) -> None:
    beats = _beat_text(105).replace("[4.0-8.0]", "[3.0-8.0]")
    message = _failure(tmp_path, _route_text(beats=beats))
    assert "overlap from 3.0 to 4.0" in message


def test_final_beat_must_end_at_duration(tmp_path: Path) -> None:
    beats = _beat_text(105).replace("[16.0-20.0]", "[16.0-19.0]")
    message = _failure(tmp_path, _route_text(beats=beats))
    assert "not DURATION 20" in message


@pytest.mark.parametrize("field", ("SOURCE", "LEGWEAR"))
def test_missing_required_field_fails(tmp_path: Path, field: str) -> None:
    message = _failure(tmp_path, _route_text(omit_field=field))
    assert f"missing or empty required field {field}" in message


def test_missing_required_section_fails(tmp_path: Path) -> None:
    message = _failure(tmp_path, _route_text(omit_section="END STATE"))
    assert "missing or empty required section END STATE" in message


def test_list_b_phrase_in_beats_fails(tmp_path: Path) -> None:
    beats = _beat_text(105).replace(
        "The rider enters", "In slow motion the rider enters", 1
    )
    message = _failure(tmp_path, _route_text(beats=beats))
    assert "TIMELINE" in message
    assert "List B banned phrase 'slow motion'" in message


def test_list_b_phrase_in_canon_and_negative_is_exempt(tmp_path: Path) -> None:
    root = _make_project(tmp_path)
    master_path = root / "canon" / "MASTER-BLOCK.md"
    master = build.read_utf8(master_path)
    master = master.replace(
        "## FORMAT\n\n", "## FORMAT\n\nNo slow motion is requested here.\n\n", 1
    )
    build.write_utf8(master_path, master)
    assert "slow motion" in build.read_utf8(root / "canon" / "NEGATIVES.md").casefold()

    build.build_project(root, check=True)


def test_list_a_phrase_in_beats_fails(tmp_path: Path) -> None:
    beats = _beat_text(105).replace(
        "The rider enters", "The next clip starts as the rider enters", 1
    )
    message = _failure(tmp_path, _route_text(beats=beats))
    assert "TIMELINE" in message
    assert "List A banned phrase 'next clip'" in message


def test_list_a_phrase_in_negative_fails(tmp_path: Path) -> None:
    root = _make_project(tmp_path)
    negative_path = root / "canon" / "NEGATIVES.md"
    negative = build.read_utf8(negative_path)
    build.write_utf8(negative_path, negative + "The next clip is forbidden.\n")

    with pytest.raises(build.BuildError) as captured:
        build.build_project(root, check=True)
    message = str(captured.value)
    assert "NEGATIVE" in message
    assert "List A banned phrase 'next clip'" in message


def test_opening_state_cannot_name_final_frame(tmp_path: Path) -> None:
    opening = (
        "The final frame is anticipated while the rider waits above the city. "
        + " ".join("visible" for _ in range(70))
    )
    message = _failure(tmp_path, _route_text(opening=opening))
    assert "OPENING STATE" in message
    assert "state text must not contain 'final frame'" in message


def test_voice_time_outside_duration_fails(tmp_path: Path) -> None:
    message = _failure(tmp_path, _route_text(voice='[19.0-21.0] "Help!"'))
    assert "VOICE" in message
    assert "outside 0.0-20" in message


@pytest.mark.parametrize(
    "caption",
    (
        (
            "You're falling above Test City.\n\n"
            "#MegaSlideFear #TestTower #WaterSlide #POVReels #ViralReels"
        ),
        (
            "You're falling above Test City.\n\n"
            "#MegaSlideFear #TestTower #POVReels #WaterSlide #CGIAdventure #ViralReels"
        ),
    ),
)
def test_caption_missing_or_misordered_tags_fails(
    tmp_path: Path, caption: str
) -> None:
    message = _failure(tmp_path, _route_text(caption=caption))
    assert "expected exactly 6 hashtags" in message


def test_route_word_count_under_600_fails(tmp_path: Path) -> None:
    message = _failure(tmp_path, _route_text(beat_filler_words=5))
    assert "route-authored word count" in message
    assert "outside 600-1000" in message


def test_route_word_count_over_1000_fails(tmp_path: Path) -> None:
    message = _failure(tmp_path, _route_text(beat_filler_words=190))
    assert "route-authored word count" in message
    assert "outside 600-1000" in message


def test_same_input_twice_produces_identical_bytes(tmp_path: Path) -> None:
    root = _make_project(tmp_path)
    build.build_project(root, check=True)
    output_dir = root / "out" / "test-city-green-rain"
    first = {path.name: path.read_bytes() for path in output_dir.iterdir()}

    build.build_project(root, check=True)
    second = {path.name: path.read_bytes() for path in output_dir.iterdir()}

    assert first == second


def test_underscore_template_is_not_processed(tmp_path: Path) -> None:
    root = _make_project(tmp_path)
    build.write_utf8(root / "routes" / "_TEMPLATE.md", "not a valid route\n")

    routes = build.build_project(root, check=True)

    assert [route.slug for route in routes] == ["test-city-green-rain"]
    assert not (root / "out" / "_TEMPLATE").exists()


def test_duplicate_slugs_fail_before_writing(tmp_path: Path) -> None:
    root = _make_project(tmp_path)
    copied_path = root / "routes" / "copied-route.md"
    build.write_utf8(copied_path, _route_text())

    with pytest.raises(build.BuildError) as captured:
        build.build_project(root, check=True)

    message = str(captured.value)
    assert "duplicate SLUG 'test-city-green-rain'" in message
    assert "routes/test-city-green-rain.md" in message
    assert "routes/copied-route.md" in message
    assert not (root / "out" / "test-city-green-rain").exists()


def test_traversal_slug_fails_without_writing_outside_out(tmp_path: Path) -> None:
    route_text = _route_text().replace(
        "SLUG: test-city-green-rain", "SLUG: ../../kacti", 1
    )
    root = _make_project(tmp_path, route_text)
    escaped_path = (root / "out" / "../../kacti").resolve()
    assert not escaped_path.exists()

    with pytest.raises(build.BuildError) as captured:
        build.build_project(root, check=True)

    assert "invalid SLUG '../../kacti'" in str(captured.value)
    assert not escaped_path.exists()
    assert not (root / "out").exists()


@pytest.mark.parametrize("slug", ("has space", "Has-Uppercase"))
def test_slug_with_space_or_uppercase_fails(tmp_path: Path, slug: str) -> None:
    route_text = _route_text().replace(
        "SLUG: test-city-green-rain", f"SLUG: {slug}", 1
    )
    message = _failure(tmp_path, route_text)
    assert f"invalid SLUG {slug!r}" in message


def test_empty_routes_directory_fails(tmp_path: Path) -> None:
    for name in ("MASTER-BLOCK.md", "NEGATIVES.md", "CAPTION.md"):
        _copy_text(SOURCE_ROOT / "canon" / name, tmp_path / "canon" / name)
    (tmp_path / "routes").mkdir()

    with pytest.raises(build.BuildError) as captured:
        build.build_project(tmp_path, check=True)

    assert "no processable route files found" in str(captured.value)


def test_crlf_route_is_processed_and_output_remains_lf(tmp_path: Path) -> None:
    root = _make_project(tmp_path)
    route_path = root / "routes" / "test-city-green-rain.md"
    crlf_route = _route_text().replace("\n", "\r\n").encode("utf-8")
    with route_path.open("wb") as handle:
        handle.write(crlf_route)

    build.build_project(root, check=True)

    output_dir = root / "out" / "test-city-green-rain"
    for output_path in output_dir.iterdir():
        assert b"\r\n" not in output_path.read_bytes()


def test_final_beat_after_duration_fails(tmp_path: Path) -> None:
    beats = _beat_text(105).replace("[16.0-20.0]", "[16.0-21.0]")
    message = _failure(tmp_path, _route_text(beats=beats))
    assert "final interval ends at 21.0, not DURATION 20" in message


def test_equivalent_decimal_final_beat_passes(tmp_path: Path) -> None:
    beats = _beat_text(105).replace("[16.0-20.0]", "[16.0-20.00]")
    root = _make_project(tmp_path, _route_text(beats=beats))

    routes = build.build_project(root, check=True)

    assert [route.slug for route in routes] == ["test-city-green-rain"]


def test_real_routes_generate_and_validate(tmp_path: Path) -> None:
    for name in ("MASTER-BLOCK.md", "NEGATIVES.md", "CAPTION.md"):
        _copy_text(SOURCE_ROOT / "canon" / name, tmp_path / "canon" / name)
    for name in (
        "_TEMPLATE.md",
        "toronto-cn-red-dusk.md",
        "vegas-strat-blue-rain.md",
    ):
        _copy_text(SOURCE_ROOT / "routes" / name, tmp_path / "routes" / name)

    routes = build.build_project(tmp_path, check=True)

    assert [route.slug for route in routes] == [
        "toronto-cn-red-dusk",
        "vegas-strat-blue-rain",
    ]
    for route in routes:
        output_dir = tmp_path / "out" / route.slug
        assert sorted(path.name for path in output_dir.iterdir()) == [
            "CAPTION.txt",
            "PROMPT.txt",
            "VOICE.txt",
        ]
