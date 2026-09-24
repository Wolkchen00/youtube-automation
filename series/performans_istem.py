"""Pure formatting for series-relative performance feedback in planner prompts."""

from __future__ import annotations

import math
from typing import Mapping


MAX_BLOCK_CHARS = 1500
MEASURED_LABELS = {"kazanan", "kaybeden", "orta"}
PLATFORMS = ("youtube", "instagram", "tiktok")

_HEADER = (
    "PERFORMANCE MEMORY (measured on this series' own history, not a universal target)"
)
_INSTRUCTIONS = (
    "Lean toward the shared traits of winners (subject type, scale, and family). "
    "Move away from the shared traits of losers. Never repeat an existing subject or title. "
    "Do not over-generalize from a single example."
)


def _finite_number(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def _part_number(part: dict) -> int | None:
    value = part.get("part")
    if isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _plan_for(plans: Mapping, part_number: int) -> dict | None:
    plan = plans.get(part_number)
    if plan is None:
        plan = plans.get(str(part_number))
    return plan if isinstance(plan, dict) else None


def _text(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.split())


def _topic_fields(plan: dict) -> list[str]:
    fields = []
    family = _text(plan.get("family"))
    if family:
        fields.append(f"family={family}")
    seed_id = plan.get("seed_id")
    if isinstance(seed_id, (str, int)) and not isinstance(seed_id, bool):
        fields.append(f"seed_id={seed_id}")
    card_topic = _text(plan.get("card_topic"))
    if card_topic:
        fields.append(f"card_topic={card_topic}")
    object_card = plan.get("object_card")
    object_name = _text(object_card.get("name")) if isinstance(object_card, dict) else ""
    if object_name:
        fields.append(f"object={object_name}")
    return fields


def _metrics(part: dict) -> str:
    ratios = part.get("oranlar")
    scored_metrics = part.get("puanlanan_metrikler")
    if not isinstance(ratios, dict) or not isinstance(scored_metrics, dict):
        return ""
    values = []
    ordered = list(PLATFORMS)
    ordered.extend(key for key in ratios if key not in PLATFORMS)
    for platform in ordered:
        ratio = _finite_number(ratios.get(platform))
        metrics = scored_metrics.get(platform)
        views = _finite_number(metrics.get("views")) if isinstance(metrics, dict) else None
        if ratio is None or views is None:
            continue
        values.append(f"{platform} {int(round(views))} views/{ratio:.1f}x")
    return ", ".join(values)


def _entry(part: dict, plan: dict) -> dict:
    episode = plan.get("episode")
    title = _text(episode.get("title")) if isinstance(episode, dict) else ""
    if not title:
        title = _text(part.get("subtitle"))
    synopsis = _text(plan.get("synopsis"))
    details = _topic_fields(plan)
    metrics = _metrics(part)
    if metrics:
        details.append(metrics)
    return {
        "part": _part_number(part),
        "title": title or "Untitled",
        "synopsis": synopsis,
        "details": details,
    }


def _entry_line(entry: dict) -> str:
    line = f"- Part {entry['part']}: {entry['title']}"
    if entry["synopsis"]:
        line += f" | synopsis: {entry['synopsis']}"
    if entry["details"]:
        line += " | " + "; ".join(entry["details"])
    return line


def _render(winners: list[dict], losers: list[dict]) -> str:
    lines = [_HEADER, _INSTRUCTIONS]
    if winners:
        lines.append("WINNERS (highest score first):")
        lines.extend(_entry_line(entry) for entry in winners)
    if losers:
        lines.append("LOSERS (lowest score first):")
        lines.extend(_entry_line(entry) for entry in losers)
    return "\n".join(lines)


def _truncate_synopses(winners: list[dict], losers: list[dict]) -> None:
    """Spend the character overage on synopsis text before entries are dropped."""
    entries = winners + losers
    while True:
        overage = len(_render(winners, losers)) - MAX_BLOCK_CHARS
        if overage <= 0:
            return
        candidates = [entry for entry in entries if entry["synopsis"]]
        if not candidates:
            return
        entry = max(candidates, key=lambda item: len(item["synopsis"]))
        synopsis = entry["synopsis"]
        # Removing a synopsis also removes its separator and label, so prefer it
        # once only a tiny fragment would remain.
        if len(synopsis) <= overage + 3:
            entry["synopsis"] = ""
            continue
        keep = max(1, len(synopsis) - overage - 1)
        entry["synopsis"] = synopsis[:keep].rstrip() + "…"


def build_performance_block(scored_document: dict, plans: Mapping) -> str:
    """Build a bounded performance-memory block from already-scored data.

    ``plans`` maps part numbers (integer or string) to loaded plan dictionaries.
    The function performs no I/O and trusts labels only because its input contract
    explicitly requires a document returned by ``score_performance``.
    """
    if not isinstance(scored_document, dict) or not isinstance(plans, Mapping):
        return ""
    raw_parts = scored_document.get("parts")
    if not isinstance(raw_parts, list):
        return ""
    parts = [part for part in raw_parts if isinstance(part, dict)]
    measured = [part for part in parts if part.get("etiket") in MEASURED_LABELS]
    if len(measured) < 6:
        return ""

    winners = [part for part in measured if part.get("etiket") == "kazanan"]
    losers = [part for part in measured if part.get("etiket") == "kaybeden"]
    if not winners and not losers:
        return ""

    def winner_score(part: dict) -> float:
        score = _finite_number(part.get("puan"))
        return score if score is not None else float("-inf")

    def loser_score(part: dict) -> float:
        score = _finite_number(part.get("puan"))
        return score if score is not None else float("inf")

    winners.sort(key=winner_score, reverse=True)
    losers.sort(key=loser_score)

    def enrich(selected: list[dict]) -> list[dict]:
        result = []
        for part in selected:
            number = _part_number(part)
            if number is None:
                continue
            plan = _plan_for(plans, number)
            if plan is None:
                continue
            result.append(_entry(part, plan))
            if len(result) == 4:
                break
        return result

    winner_entries = enrich(winners)
    loser_entries = enrich(losers)
    if not winner_entries and not loser_entries:
        return ""

    _truncate_synopses(winner_entries, loser_entries)
    block = _render(winner_entries, loser_entries)
    while len(block) > MAX_BLOCK_CHARS and (winner_entries or loser_entries):
        if loser_entries:
            loser_entries.pop()
        else:
            winner_entries.pop()
        if not winner_entries and not loser_entries:
            return ""
        block = _render(winner_entries, loser_entries)
    return block


# A concise Turkish alias keeps the module pleasant to use from local tooling.
performans_istem_blogu = build_performance_block
