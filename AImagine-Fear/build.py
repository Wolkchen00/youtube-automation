from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent

MASTER_SECTIONS = (
    "FORMAT",
    "INDEPENDENCE NOTE",
    "CAMERA",
    "RIDER",
    "SLIDE",
    "MOTION AND GRAVITY",
    "WORLD",
    "AUDIO",
)
ROUTE_FIELDS = (
    "SLUG",
    "DESTINATION",
    "LANDMARK",
    "DURATION",
    "NEON",
    "LEGWEAR",
    "WEATHER",
    "SOURCE",
)
ROUTE_SECTIONS = (
    "OPENING STATE",
    "BEATS",
    "END STATE",
    "VOICE",
    "CAPTION",
)
PROMPT_SECTIONS = (
    *MASTER_SECTIONS,
    "OPENING STATE",
    "TIMELINE",
    "VOICE",
    "END STATE",
    "NEGATIVE",
)

TOKEN_FIELDS = {
    "<<DURATION>>": "DURATION",
    "<<NEON>>": "NEON",
    "<<LEGWEAR>>": "LEGWEAR",
    "<<WEATHER>>": "WEATHER",
    "<<CITY>>": "DESTINATION",
    "<<LANDMARK>>": "LANDMARK",
}

LIST_A_PHRASES = (
    "clip 1",
    "clip 2",
    "next clip",
    "previous clip",
    "part 1",
    "part 2",
    "part one",
    "part two",
    "first clip",
    "second clip",
)
LIST_B_PHRASES = (
    "cut to",
    "slow motion",
    "slow-motion",
    "time lapse",
    "timelapse",
    "drone shot",
    "selfie",
    "voiceover",
    "voice-over",
    "background music",
    "soundtrack",
    "third person",
    "third-person",
)
STATE_PHRASES = (
    "frame one",
    "first frame",
    "last frame",
    "final frame",
)
# Liste C, GORSEL TETIKLEYICILER. Kapsam: uretilen PROMPT.txt'nin TAMAMI, istisnasiz.
# Difuzyon modeli olumsuzlamayi degil ISMI goruyor: "no detached loop" yazmak halkayi
# CIZDIRIYOR. Olculdu 2026-09-03: bozulan kirpik surumde 2 tetik vardi, "sertlestirilmis"
# kanonda 9'a cikti ve uretimde havada asili halkalar belirdi; tetiksiz surumde yok.
# Bu kelimeler promptta HICBIR bicimde, olumlu ya da olumsuz, gecmemelidir.
TRIGGER_PHRASES = (
    "loop",
    "corkscrew",
    "spiral",
    "ribbon",
    "curl",
    "hoop",
    "coil",
    "swirl",
)
FIXED_TRAILING_TAGS = (
    "#WaterSlide",
    "#POVReels",
    "#CGIAdventure",
    "#ViralReels",
)

INTERVAL_RE = re.compile(
    r"^\[([0-9]+(?:\.[0-9]+)?)-([0-9]+(?:\.[0-9]+)?)\]\s+(.+)$"
)
FIELD_RE = re.compile(r"^([A-Z][A-Z ]*):[ \t]*(.*)$")
HASHTAG_RE = re.compile(r"#[A-Za-z0-9_]+")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class BuildError(RuntimeError):
    """One or more project inputs or generated files failed validation."""

    def __init__(self, messages: Iterable[str]):
        self.messages = tuple(messages)
        super().__init__("\n".join(self.messages))


@dataclass(frozen=True)
class Canon:
    master: dict[str, str]
    negative: str


@dataclass(frozen=True)
class Route:
    path: Path
    fields: dict[str, str]
    sections: dict[str, str]

    @property
    def slug(self) -> str:
        return self.fields["SLUG"]


def read_utf8(path: Path) -> str:
    with path.open("r", encoding="utf-8", newline="\n") as handle:
        text = handle.read()
    return text.replace("\r\n", "\n").replace("\r", "\n")


def write_utf8(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def _trim_blank_lines(lines: list[str]) -> str:
    start = 0
    end = len(lines)
    while start < end and not lines[start].strip():
        start += 1
    while end > start and not lines[end - 1].strip():
        end -= 1
    return "\n".join(lines[start:end])


def parse_sections(text: str, path: Path) -> dict[str, str]:
    sections: dict[str, str] = {}
    current: str | None = None
    lines: list[str] = []

    def finish_section() -> None:
        nonlocal lines
        if current is not None:
            if current in sections:
                raise BuildError((f"{path}: duplicate section {current}",))
            sections[current] = _trim_blank_lines(lines)
        lines = []

    for line in text.splitlines():
        if line.startswith("## "):
            finish_section()
            current = line[3:].strip()
        elif current is not None:
            lines.append(line)
    finish_section()
    return sections


def _display_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _issue(
    root: Path,
    path: Path,
    route: str,
    reason: str,
    section: str | None = None,
    line: int | None = None,
) -> str:
    location = _display_path(path, root)
    details = ""
    if section is not None:
        details += f" {section}"
    if line is not None:
        details += f" line {line}"
    return f"{location} [{route}]{details}: {reason}"


def load_canon(root: Path) -> Canon:
    master_path = root / "canon" / "MASTER-BLOCK.md"
    negative_path = root / "canon" / "NEGATIVES.md"
    master_all = parse_sections(read_utf8(master_path), master_path)
    negative_all = parse_sections(read_utf8(negative_path), negative_path)
    messages: list[str] = []

    for name in MASTER_SECTIONS:
        if not master_all.get(name, "").strip():
            messages.append(
                _issue(root, master_path, "all routes", f"missing or empty section {name}")
            )
    if not negative_all.get("NEGATIVE", "").strip():
        messages.append(
            _issue(
                root,
                negative_path,
                "all routes",
                "missing or empty section NEGATIVE",
            )
        )
    if messages:
        raise BuildError(messages)

    return Canon(
        master={name: master_all[name] for name in MASTER_SECTIONS},
        negative=negative_all["NEGATIVE"],
    )


def load_route(path: Path, root: Path) -> Route:
    text = read_utf8(path)
    sections = parse_sections(text, path)
    fields: dict[str, str] = {}
    messages: list[str] = []

    for line in text.splitlines():
        if line.startswith("## "):
            break
        match = FIELD_RE.fullmatch(line)
        if match:
            key, value = match.groups()
            if key in fields:
                messages.append(
                    _issue(root, path, path.stem, f"duplicate required field {key}")
                )
            fields[key] = value.strip()

    route_name = fields.get("SLUG") or path.stem
    for key in ROUTE_FIELDS:
        if not fields.get(key, "").strip():
            messages.append(
                _issue(root, path, route_name, f"missing or empty required field {key}")
            )
    for name in ROUTE_SECTIONS:
        if not sections.get(name, "").strip():
            messages.append(
                _issue(root, path, route_name, f"missing or empty required section {name}")
            )
    slug = fields.get("SLUG", "")
    if slug and not SLUG_RE.fullmatch(slug):
        messages.append(
            _issue(
                root,
                path,
                route_name,
                f"invalid SLUG {slug!r}; expected ^[a-z0-9]+(-[a-z0-9]+)*$",
            )
        )
    if messages:
        raise BuildError(messages)

    return Route(
        path=path,
        fields={key: fields[key] for key in ROUTE_FIELDS},
        sections={name: sections[name] for name in ROUTE_SECTIONS},
    )


def discover_route_paths(root: Path) -> list[Path]:
    routes_dir = root / "routes"
    return sorted(
        (
            path
            for path in routes_dir.glob("*.md")
            if not path.name.startswith("_")
        ),
        key=lambda path: path.name,
    )


def render_route(canon: Canon, route: Route) -> dict[str, str]:
    prompt_parts: list[str] = []
    for name in MASTER_SECTIONS:
        body = canon.master[name]
        for token, field in TOKEN_FIELDS.items():
            body = body.replace(token, route.fields[field])
        prompt_parts.append(f"{name}\n{body}")

    prompt_parts.extend(
        (
            "OPENING STATE\nAt frame one: " + route.sections["OPENING STATE"],
            "TIMELINE\n" + route.sections["BEATS"],
            "VOICE\n" + route.sections["VOICE"],
            "END STATE\nAt the final frame: " + route.sections["END STATE"],
            "NEGATIVE\n" + canon.negative,
        )
    )
    return {
        "PROMPT.txt": "\n\n".join(prompt_parts) + "\n",
        "CAPTION.txt": route.sections["CAPTION"] + "\n",
        "VOICE.txt": route.sections["VOICE"] + "\n",
    }


def _parse_duration(route: Route, root: Path) -> tuple[Decimal | None, list[str]]:
    try:
        duration = Decimal(route.fields["DURATION"])
    except InvalidOperation:
        return None, [
            _issue(
                root,
                route.path,
                route.slug,
                f"DURATION is not a number: {route.fields['DURATION']!r}",
            )
        ]
    if not duration.is_finite() or duration < 0:
        return None, [
            _issue(
                root,
                route.path,
                route.slug,
                f"DURATION must be a finite nonnegative number: {route.fields['DURATION']!r}",
            )
        ]
    return duration, []


def _intervals(
    route: Route,
    root: Path,
    section: str,
) -> tuple[list[tuple[Decimal, Decimal, int]], list[str]]:
    intervals: list[tuple[Decimal, Decimal, int]] = []
    messages: list[str] = []
    for line_number, line in enumerate(route.sections[section].splitlines(), start=1):
        if not line.strip():
            continue
        match = INTERVAL_RE.fullmatch(line)
        if not match:
            messages.append(
                _issue(
                    root,
                    route.path,
                    route.slug,
                    "expected '[a-b] text'",
                    "TIMELINE" if section == "BEATS" else section,
                    line_number,
                )
            )
            continue
        start, end = Decimal(match.group(1)), Decimal(match.group(2))
        if end < start:
            messages.append(
                _issue(
                    root,
                    route.path,
                    route.slug,
                    f"interval ends before it starts ({start}-{end})",
                    "TIMELINE" if section == "BEATS" else section,
                    line_number,
                )
            )
        intervals.append((start, end, line_number))
    return intervals, messages


def _validate_beats(route: Route, root: Path, duration: Decimal) -> list[str]:
    intervals, messages = _intervals(route, root, "BEATS")
    if len(intervals) < 5:
        messages.append(
            _issue(
                root,
                route.path,
                route.slug,
                f"TIMELINE has {len(intervals)} intervals; at least 5 are required",
                "TIMELINE",
            )
        )
    if not intervals:
        return messages
    if intervals[0][0] != Decimal("0.0"):
        messages.append(
            _issue(
                root,
                route.path,
                route.slug,
                f"first interval starts at {intervals[0][0]}, not 0.0",
                "TIMELINE",
                intervals[0][2],
            )
        )
    for previous, current in zip(intervals, intervals[1:]):
        previous_end = previous[1]
        current_start = current[0]
        if previous_end < current_start:
            reason = f"gap from {previous_end} to {current_start}"
        elif previous_end > current_start:
            reason = f"overlap from {current_start} to {previous_end}"
        else:
            continue
        messages.append(
            _issue(
                root,
                route.path,
                route.slug,
                reason,
                "TIMELINE",
                current[2],
            )
        )
    if intervals[-1][1] != duration:
        messages.append(
            _issue(
                root,
                route.path,
                route.slug,
                f"final interval ends at {intervals[-1][1]}, not DURATION {duration}",
                "TIMELINE",
                intervals[-1][2],
            )
        )
    return messages


def _validate_voice(route: Route, root: Path, duration: Decimal) -> list[str]:
    intervals, messages = _intervals(route, root, "VOICE")
    for start, end, line_number in intervals:
        if start < 0 or start > duration or end < 0 or end > duration:
            messages.append(
                _issue(
                    root,
                    route.path,
                    route.slug,
                    f"interval {start}-{end} is outside 0.0-{duration}",
                    "VOICE",
                    line_number,
                )
            )
    return messages


def _section_for_prompt_line(line: str, current: str) -> str:
    if line in PROMPT_SECTIONS:
        return line
    return current


def _validate_banned_phrases(
    route: Route,
    root: Path,
    outputs: dict[str, str],
) -> list[str]:
    messages: list[str] = []
    current_section = "PROMPT"
    prompt_path = root / "out" / route.slug / "PROMPT.txt"
    for line_number, line in enumerate(outputs["PROMPT.txt"].splitlines(), start=1):
        current_section = _section_for_prompt_line(line, current_section)
        lowered = line.casefold()
        for phrase in LIST_A_PHRASES:
            if phrase.casefold() in lowered:
                messages.append(
                    _issue(
                        root,
                        prompt_path,
                        route.slug,
                        f"List A banned phrase {phrase!r}",
                        current_section,
                        line_number,
                    )
                )

    scoped_sections = (
        ("OPENING STATE", route.sections["OPENING STATE"], route.path),
        ("TIMELINE", route.sections["BEATS"], route.path),
        ("VOICE", route.sections["VOICE"], route.path),
        ("END STATE", route.sections["END STATE"], route.path),
        (
            "CAPTION",
            route.sections["CAPTION"],
            root / "out" / route.slug / "CAPTION.txt",
        ),
    )
    for section, text, path in scoped_sections:
        for line_number, line in enumerate(text.splitlines(), start=1):
            lowered = line.casefold()
            for phrase in LIST_B_PHRASES:
                if phrase.casefold() in lowered:
                    messages.append(
                        _issue(
                            root,
                            path,
                            route.slug,
                            f"List B banned phrase {phrase!r}",
                            section,
                            line_number,
                        )
                    )
    return messages


def _validate_triggers(
    route: Route,
    root: Path,
    outputs: dict[str, str],
) -> list[str]:
    """Liste C: gorsel tetikleyici kelimeler, uretilen promptun tamaminda yasak."""
    messages: list[str] = []
    prompt_path = root / "out" / route.slug / "PROMPT.txt"
    current_section = "PROMPT"
    for line_number, line in enumerate(outputs["PROMPT.txt"].splitlines(), start=1):
        current_section = _section_for_prompt_line(line, current_section)
        lowered = line.casefold()
        for phrase in TRIGGER_PHRASES:
            if phrase in lowered:
                messages.append(
                    _issue(
                        root,
                        prompt_path,
                        route.slug,
                        "Liste C gorsel tetikleyici %r; model bu ismi olumsuz cumlede bile cizer, "
                        "kelimeyi kaldir ve yerine fiziksel tarif koy" % phrase,
                        current_section,
                        line_number,
                    )
                )
    return messages


def _validate_states(route: Route, root: Path) -> list[str]:
    messages: list[str] = []
    for section in ("OPENING STATE", "END STATE"):
        for line_number, line in enumerate(route.sections[section].splitlines(), start=1):
            lowered = line.casefold()
            for phrase in STATE_PHRASES:
                if phrase.casefold() in lowered:
                    messages.append(
                        _issue(
                            root,
                            route.path,
                            route.slug,
                            f"state text must not contain {phrase!r}",
                            section,
                            line_number,
                        )
                    )
    return messages


def _validate_tokens(
    route: Route,
    root: Path,
    outputs: dict[str, str],
) -> list[str]:
    messages: list[str] = []
    for filename, text in outputs.items():
        for line_number, line in enumerate(text.splitlines(), start=1):
            if "<<" in line or ">>" in line:
                messages.append(
                    _issue(
                        root,
                        root / "out" / route.slug / filename,
                        route.slug,
                        "unresolved token marker",
                        line=line_number,
                    )
                )
    return messages


def _validate_lengths(
    route: Route,
    root: Path,
    outputs: dict[str, str],
) -> list[str]:
    messages: list[str] = []
    prompt_words = len(outputs["PROMPT.txt"].split())
    route_words = sum(
        len(route.sections[name].split())
        for name in ("OPENING STATE", "BEATS", "VOICE", "END STATE")
    )
    if not 1800 <= prompt_words <= 2800:
        messages.append(
            _issue(
                root,
                root / "out" / route.slug / "PROMPT.txt",
                route.slug,
                f"total word count {prompt_words} is outside 1800-2800",
            )
        )
    if not 600 <= route_words <= 1000:
        messages.append(
            _issue(
                root,
                route.path,
                route.slug,
                f"route-authored word count {route_words} is outside 600-1000",
            )
        )
    return messages


def _validate_caption(route: Route, root: Path) -> list[str]:
    messages: list[str] = []
    caption_path = root / "out" / route.slug / "CAPTION.txt"
    first_line = route.sections["CAPTION"].splitlines()[0]
    if not first_line.startswith("You're"):
        messages.append(
            _issue(
                root,
                caption_path,
                route.slug,
                "first line must start with \"You're\"",
                "CAPTION",
                1,
            )
        )
    hashtags = HASHTAG_RE.findall(route.sections["CAPTION"])
    valid_tags = (
        len(hashtags) == 6
        and hashtags[0] == "#MegaSlideFear"
        and tuple(hashtags[2:]) == FIXED_TRAILING_TAGS
    )
    if not valid_tags:
        messages.append(
            _issue(
                root,
                caption_path,
                route.slug,
                "expected exactly 6 hashtags with #MegaSlideFear first and "
                + " ".join(FIXED_TRAILING_TAGS)
                + " last",
                "CAPTION",
            )
        )
    return messages


def validate_route(
    canon: Canon,
    route: Route,
    outputs: dict[str, str],
    root: Path,
) -> list[str]:
    messages: list[str] = []
    duration, duration_messages = _parse_duration(route, root)
    messages.extend(duration_messages)
    if duration is not None:
        messages.extend(_validate_beats(route, root, duration))
        messages.extend(_validate_voice(route, root, duration))
    messages.extend(_validate_tokens(route, root, outputs))
    messages.extend(_validate_banned_phrases(route, root, outputs))
    messages.extend(_validate_triggers(route, root, outputs))
    messages.extend(_validate_states(route, root))
    messages.extend(_validate_lengths(route, root, outputs))
    messages.extend(_validate_caption(route, root))

    second_render = render_route(canon, route)
    for filename in sorted(outputs):
        if outputs[filename].encode("utf-8") != second_render[filename].encode("utf-8"):
            messages.append(
                _issue(
                    root,
                    root / "out" / route.slug / filename,
                    route.slug,
                    "rendering the same input twice produced different bytes",
                )
            )
    return messages


def build_project(root: Path = ROOT, check: bool = False) -> list[Route]:
    root = Path(root).resolve()
    canon = load_canon(root)
    messages: list[str] = []
    routes: list[Route] = []
    route_paths = discover_route_paths(root)

    if not route_paths:
        raise BuildError(
            (
                _issue(
                    root,
                    root / "routes",
                    "no routes",
                    "no processable route files found",
                ),
            )
        )

    for path in route_paths:
        try:
            routes.append(load_route(path, root))
        except BuildError as error:
            messages.extend(error.messages)

    routes_by_slug: dict[str, list[Route]] = {}
    for route in routes:
        routes_by_slug.setdefault(route.slug, []).append(route)
    for slug, matching_routes in routes_by_slug.items():
        if len(matching_routes) < 2:
            continue
        paths = [_display_path(route.path, root) for route in matching_routes]
        messages.append(
            f"{', '.join(paths)} [{slug}]: duplicate SLUG {slug!r} declared by "
            + ", ".join(paths)
        )

    if messages:
        raise BuildError(messages)

    for route in routes:
        outputs = render_route(canon, route)
        output_dir = root / "out" / route.slug
        for filename, text in outputs.items():
            write_utf8(output_dir / filename, text)
        if check:
            messages.extend(validate_route(canon, route, outputs, root))

    if messages:
        raise BuildError(messages)
    return routes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate route prompts, captions, and voice timelines."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate every generated route and exit 1 on any failure",
    )
    args = parser.parse_args(argv)

    try:
        routes = build_project(ROOT, check=args.check)
    except (BuildError, OSError) as error:
        print(error, file=sys.stderr)
        return 1

    if args.check:
        print(f"Built and validated {len(routes)} routes.")
    else:
        print(f"Built {len(routes)} routes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
