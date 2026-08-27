"""qc_log.jsonl içindeki gerçek Gemini QC denemelerini salt-okunur raporla."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JOURNAL = PROJECT_ROOT / "sentinal_ihsan" / "unnatural-lab" / "qc_log.jsonl"
OUTCOMES = ("ok", "429", "error")


def read_journal(path: Path) -> tuple[list[dict], int]:
    """Geçerli JSON nesnelerini ve okunamayan satır sayısını döndür."""
    events: list[dict] = []
    malformed = 0
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return events, malformed
    for line in lines:
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            malformed += 1
            continue
        if isinstance(event, dict):
            events.append(event)
        else:
            malformed += 1
    return events, malformed


def summarize(events: list[dict], episode: int) -> dict:
    attempts = [
        event for event in events
        if event.get("event") == "qc_api_attempt"
        and event.get("episode") == episode
    ]
    attempt_ids = {
        event.get("attempt_id") for event in attempts
        if isinstance(event.get("attempt_id"), str)
    }
    results_by_attempt: dict[str, list[dict]] = defaultdict(list)
    for event in events:
        attempt_id = event.get("attempt_id")
        if (event.get("event") == "qc_api_result"
                and isinstance(attempt_id, str)
                and attempt_id in attempt_ids):
            results_by_attempt[attempt_id].append(event)

    outcomes = Counter(
        result.get("outcome")
        for result_list in results_by_attempt.values()
        for result in result_list
        if result.get("outcome") in OUTCOMES
    )
    unmatched = [
        event.get("attempt_id") for event in attempts
        if not results_by_attempt.get(event.get("attempt_id"))
    ]
    duplicate_results = sum(
        max(0, len(result_list) - 1)
        for result_list in results_by_attempt.values()
    )
    fallback = sum(event.get("is_fallback") is True for event in attempts)
    historical = sum(
        event.get("episode") == episode
        and event.get("event") not in ("qc_api_attempt", "qc_api_result")
        for event in events
    )
    return {
        "episode": episode,
        "attempts": len(attempts),
        "outcomes": {outcome: outcomes[outcome] for outcome in OUTCOMES},
        "unmatched_attempts": unmatched,
        "duplicate_results": duplicate_results,
        "fallback_attempts": fallback,
        "fallback_share": (fallback / len(attempts)) if attempts else None,
        "historical_non_api_events": historical,
    }


def render(report: dict, path: Path, malformed: int = 0) -> str:
    outcomes = report["outcomes"]
    share = report["fallback_share"]
    lines = [
        f"QC API journal: {path}",
        f"Episode: {report['episode']}",
        f"Attempts: {report['attempts']}",
        "Results: " + ", ".join(f"{name}={outcomes[name]}" for name in OUTCOMES),
        f"Unmatched attempts (unknown/crash): {len(report['unmatched_attempts'])}",
        f"Duplicate matching results: {report['duplicate_results']}",
        (
            f"Fallback share: {report['fallback_attempts']}/{report['attempts']} "
            f"({share:.1%})"
            if share is not None else
            "Fallback share: n/a (no qc_api_attempt records)"
        ),
        f"Historical non-API QC events for episode: {report['historical_non_api_events']}",
        f"Malformed journal lines skipped: {malformed}",
    ]
    if report["unmatched_attempts"]:
        lines.append("Unknown attempt IDs: " + ", ".join(report["unmatched_attempts"]))
    if report["attempts"] == 0 and report["historical_non_api_events"]:
        lines.append(
            "Historical limitation: this episode predates qc_api_attempt/qc_api_result "
            "instrumentation. Old verdict events cannot reveal the real Gemini attempt count, "
            "retries, 429s, or fallback share."
        )
    elif report["attempts"] == 0:
        lines.append("No QC API attempt records exist for this episode.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Bir bölümün gerçek Gemini QC denemelerini qc_log.jsonl'dan sayar."
    )
    parser.add_argument("journal", nargs="?", type=Path, default=DEFAULT_JOURNAL)
    parser.add_argument("--episode", type=int, default=22)
    args = parser.parse_args(argv)

    events, malformed = read_journal(args.journal)
    report = summarize(events, args.episode)
    print(render(report, args.journal, malformed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
