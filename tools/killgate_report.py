"""Kill-gate raporu CLI: bir serinin son N yayinini sabit yasta olcup karar uretir.

Kullanim:
    py -X utf8 tools/killgate_report.py --series unnatural-lab --channel sentinal_ihsan
    py -X utf8 tools/killgate_report.py --series unnatural-lab --window 10 --json

Karar olgunlasmamis veride URETILMEZ (bkz. core/killgate). Cikis kodu:
    0  karar uretildi (basari / ara_bant)
    1  oldur karari ya da yorum alarmi
    2  karar verilemedi (veri olgun degil)
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from dataclasses import asdict
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core import killgate
from core.analytics import load_snapshots
from core.stack_fingerprint import fingerprint

REPO = pathlib.Path(__file__).resolve().parents[1]


def _series_path(series: str) -> pathlib.Path:
    matches = [p for p in REPO.glob(f"*/{series}/series.json")
               if "output" not in p.parts and "_archive" not in p.parts]
    if not matches:
        raise SystemExit(f"seri bulunamadi: {series}")
    return matches[0]


def _published_parts(series: str, window: int) -> list[dict]:
    data = json.loads(_series_path(series).read_text(encoding="utf-8"))
    parts = []
    for key, part in (data.get("parts") or {}).items():
        if part.get("status") != "published" or not part.get("published_at"):
            continue
        parts.append({
            "part": int(key),
            "title": str(part.get("subtitle") or "").strip(),
            "published_at": part["published_at"],
            "stack_sha256": part.get("stack_sha256"),
        })
    parts.sort(key=lambda p: p["published_at"])
    return parts[-window:]


def _video_index(snapshots, channel: str) -> dict[str, tuple[str, str]]:
    """Baslik -> (video_id, published). Seri defteri video kimligi tutmuyor."""
    index: dict[str, tuple[str, str]] = {}
    for _, snapshot in reversed(snapshots):
        videos = ((snapshot.get("channels") or {}).get(channel) or {}).get("videos") or {}
        for video_id, body in videos.items():
            title = str(body.get("title") or "").strip()
            if title and title not in index:
                index[title] = (video_id, str(body.get("published") or ""))
    return index


def main() -> int:
    parser = argparse.ArgumentParser(description="Kill-gate raporu")
    parser.add_argument("--series", required=True)
    parser.add_argument("--channel", default="sentinal_ihsan")
    parser.add_argument("--window", type=int, default=killgate.DEFAULT_WINDOW)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--stack",
        action="store_true",
        help="yalniz mevcut stack parmak izini yaz",
    )
    args = parser.parse_args()

    if args.stack:
        print(fingerprint(args.series))
        return 0

    snapshots = load_snapshots()
    if not snapshots:
        print("snapshot yok: analytics_data/daily bos")
        return 2
    index = _video_index(snapshots, args.channel)

    metrics = []
    for part in _published_parts(args.series, args.window):
        entry = index.get(part["title"])
        if entry is None:
            metrics.append(killgate.EpisodeMetric(
                video_id=f"part{part['part']}",
                published=datetime.fromisoformat(part["published_at"]),
                stack_sha256=part["stack_sha256"],
                reason="analitikte_bulunamadi",
            ))
            continue
        video_id, published_raw = entry
        try:
            published = datetime.fromisoformat(published_raw.replace("Z", "+00:00"))
        except ValueError:
            published = datetime.fromisoformat(part["published_at"])
        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)
        metrics.append(
            killgate.measure_episode(
                snapshots,
                args.channel,
                video_id,
                published,
                stack_sha256=part["stack_sha256"],
            )
        )

    report = killgate.build_report(metrics, window=args.window)
    if args.json:
        payload = asdict(report)
        payload["episodes"] = [
            {**asdict(e), "published": e.published.isoformat(),
             "measured_at": e.measured_at.isoformat() if e.measured_at else None,
             "likes_per_1k": e.likes_per_1k, "comments_per_1k": e.comments_per_1k}
            for e in report.episodes
        ]
        print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    else:
        print(killgate.format_report(report, series=args.series))
    if report.verdict == "karar_yok":
        return 2
    if report.verdict == "oldur" or report.comment_alarm:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
