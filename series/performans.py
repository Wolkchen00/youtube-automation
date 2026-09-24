"""Published series performance snapshots and series-relative scoring.

The collector deliberately has no effect on publishing: callers can run it before
replenishment, and ``main`` turns every operational failure into a warning and a
successful exit.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
from statistics import median
import time
from typing import Any, Callable

import requests

from core.config import UPLOAD_POST_API_KEY, logger
from .bible import data_dir
from .series_meta import SeriesMeta


PLATFORMS = ("youtube", "instagram", "tiktok")
METRIC_FIELDS = ("views", "likes", "comments", "shares", "saves", "reach")
UPLOAD_POST_ANALYTICS = "https://api.upload-post.com/api/uploadposts/post-analytics"
YOUTUBE_VIDEOS = "https://www.googleapis.com/youtube/v3/videos"
MIN_SCORE_AGE_HOURS = 44.0
MIN_LOSER_AGE_HOURS = 96.0
FREEZE_AGE_HOURS = 8 * 24.0
MIN_MEDIAN_PARTS = 5
MAX_API_CALLS = 60


class _StopRun(Exception):
    """Internal control flow for a rate limit or exhausted call budget."""


def _utc_now(value: datetime | Callable[[], datetime] | None) -> datetime:
    current = value() if callable(value) else value
    if current is None:
        current = datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return current.astimezone(timezone.utc)


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _number(value: Any) -> int | float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)) and math.isfinite(value):
        return value
    if isinstance(value, str):
        try:
            parsed = float(value)
        except ValueError:
            return None
        if not math.isfinite(parsed):
            return None
        return int(parsed) if parsed.is_integer() else parsed
    return None


def _clean_metrics(value: Any) -> dict[str, int | float] | None:
    if not isinstance(value, dict):
        return None
    cleaned = {}
    for field in METRIC_FIELDS:
        number = _number(value.get(field))
        if number is not None:
            cleaned[field] = number
    return cleaned or None


def _parts(document: dict) -> list[dict]:
    value = document.get("parts")
    if isinstance(value, list):
        return [part for part in value if isinstance(part, dict)]
    # Be liberal when reading an early/manual file which used a part-number map.
    if isinstance(value, dict):
        result = []
        for key, part in value.items():
            if not isinstance(part, dict):
                continue
            item = deepcopy(part)
            item.setdefault("part", key)
            result.append(item)
        return result
    return []


def _latest_eligible_metrics(part: dict, platform: str) -> dict | None:
    latest = None
    for measurement in part.get("olcumler", []):
        if not isinstance(measurement, dict):
            continue
        age = _number(measurement.get("yas_saat"))
        metrics = _clean_metrics(measurement.get(platform))
        if age is not None and age >= MIN_SCORE_AGE_HOURS and metrics is not None:
            latest = metrics
    return latest


def _latest_eligible_age(part: dict) -> int | float | None:
    latest = None
    for measurement in part.get("olcumler", []):
        if not isinstance(measurement, dict):
            continue
        age = _number(measurement.get("yas_saat"))
        if age is not None and age >= MIN_SCORE_AGE_HOURS:
            latest = age
    return latest


def score_performance(document: dict) -> dict:
    """Return a scored deep copy of *document* without performing I/O.

    Each part contributes at most one (its latest eligible) view count to a
    platform median, so frequent snapshots cannot give a part extra weight.
    """
    scored = deepcopy(document) if isinstance(document, dict) else {}
    parts = _parts(scored)
    medians: dict[str, int | float] = {}
    latest: dict[tuple[int, str], dict] = {}

    for platform in PLATFORMS:
        values = []
        for index, part in enumerate(parts):
            metrics = _latest_eligible_metrics(part, platform)
            if metrics is None:
                continue
            views = _number(metrics.get("views"))
            if views is None:
                continue
            latest[(index, platform)] = metrics
            values.append(views)
        if len(values) >= MIN_MEDIAN_PARTS:
            medians[platform] = median(values)

    for index, part in enumerate(parts):
        part.pop("etiket_notu", None)
        ratios = {}
        platform_metrics = {}
        for platform, platform_median in medians.items():
            metrics = latest.get((index, platform))
            if metrics is None or platform_median <= 0:
                continue
            views = _number(metrics.get("views"))
            if views is None:
                continue
            ratios[platform] = round(views / platform_median, 6)
            platform_metrics[platform] = metrics

        part["oranlar"] = ratios
        part["puanlanan_metrikler"] = platform_metrics
        if not ratios:
            part["puan"] = None
            part["etiket"] = "olculmemis"
            continue
        part["puan"] = max(ratios.values())
        if part["puan"] >= 2:
            part["etiket"] = "kazanan"
        elif (
            all(ratio <= 0.5 for ratio in ratios.values())
            and (_latest_eligible_age(part) or 0) >= MIN_LOSER_AGE_HOURS
        ):
            part["etiket"] = "kaybeden"
        elif all(ratio <= 0.5 for ratio in ratios.values()):
            part["etiket"] = "orta"
            part["etiket_notu"] = "kaybeden icin erken"
        else:
            part["etiket"] = "orta"

    scored["parts"] = parts
    scored["medyanlar"] = medians
    return scored


def _read_json(path: Path, default: Any, label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return deepcopy(default)
    except (OSError, json.JSONDecodeError, UnicodeError) as exc:
        logger.warning("%s okunamadi; temiz baslanacak: %s", label, exc)
        return deepcopy(default)


def _atomic_write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    temporary = path.with_name(f"{path.name}.tmp-{os.getpid()}-{time.time_ns()}")
    try:
        temporary.write_text(text, encoding="utf-8")
        try:
            os.replace(temporary, path)
        except OSError as exc:
            # Some mounted/sandboxed filesystems reject replace even though a
            # normal write is allowed. Durability is preferable to losing data.
            logger.warning("Atomik performans yazimi kullanilamadi, dogrudan yaziliyor: %s", exc)
            path.write_text(text, encoding="utf-8")
    finally:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass


def _published_parts(path: Path) -> list[dict]:
    value = _read_json(path, [], "published.json")
    return value if isinstance(value, list) else []


def _new_document(slug: str) -> dict:
    return {"series": slug, "guncellendi": None, "medyanlar": {}, "parts": []}


def _merge_published(document: dict, published: list[dict]) -> list[dict]:
    indexed: dict[int, dict] = {}
    for existing in _parts(document):
        try:
            number = int(existing.get("part"))
        except (TypeError, ValueError):
            continue
        existing["part"] = number
        existing.setdefault("post_ids", {})
        existing.setdefault("request_ids", {})
        existing.setdefault("olcumler", [])
        existing.setdefault("donduruldu", False)
        indexed[number] = existing

    for entry in published:
        if not isinstance(entry, dict):
            continue
        try:
            number = int(entry.get("part"))
        except (TypeError, ValueError):
            continue
        part = indexed.setdefault(
            number,
            {
                "part": number,
                "post_ids": {},
                "request_ids": {},
                "olcumler": [],
                "donduruldu": False,
            },
        )
        part["yayin_zamani"] = entry.get("ts")
        if isinstance(entry.get("subtitle"), str):
            part["subtitle"] = entry["subtitle"]
        results = entry.get("results") if isinstance(entry.get("results"), dict) else {}
        post_ids = part.setdefault("post_ids", {})
        request_ids = part.setdefault("request_ids", {})
        for platform in PLATFORMS:
            raw_id = results.get(platform)
            post_id = str(raw_id).strip() if raw_id is not None else ""
            if not post_id:
                continue
            if post_ids.get(platform) != post_id:
                post_ids[platform] = post_id
                request_ids.pop(platform, None)
    return [indexed[number] for number in sorted(indexed)]


class _Api:
    def __init__(self, get: Callable[..., Any], upload_key: str):
        self.get = get
        self.upload_key = upload_key
        self.calls = 0

    def request(self, url: str, *, upload_post: bool = False, **kwargs: Any) -> Any:
        if self.calls >= MAX_API_CALLS:
            logger.warning("API cagri tavani (%s) doldu; kosu burada durdu", MAX_API_CALLS)
            raise _StopRun
        self.calls += 1
        if upload_post:
            headers = dict(kwargs.pop("headers", {}) or {})
            headers["Authorization"] = f"Apikey {self.upload_key}"
            kwargs["headers"] = headers
        response = self.get(url, timeout=30, **kwargs)
        if getattr(response, "status_code", None) == 429:
            logger.warning("Upload-Post/YouTube 429 dondu; eldeki olcumler yazilip kosu durduruluyor")
            raise _StopRun
        if hasattr(response, "raise_for_status"):
            response.raise_for_status()
        return response


def _json_response(response: Any) -> dict:
    value = response.json()
    if not isinstance(value, dict):
        raise ValueError("API yaniti JSON nesnesi degil")
    return value


def _lookup_request_id(api: _Api, profile: str, platform: str, post_id: str) -> str | None:
    response = api.request(
        UPLOAD_POST_ANALYTICS,
        upload_post=True,
        params={"user": profile, "platform": platform, "platform_post_id": post_id},
    )
    payload = _json_response(response)
    post = payload.get("post")
    request_id = post.get("request_id") if isinstance(post, dict) else None
    return str(request_id).strip() if request_id else None


def _request_metrics(api: _Api, request_id: str, platform: str) -> dict | None:
    response = api.request(f"{UPLOAD_POST_ANALYTICS}/{request_id}", upload_post=True)
    payload = _json_response(response)
    platforms = payload.get("platforms")
    platform_data = platforms.get(platform) if isinstance(platforms, dict) else None
    metrics = platform_data.get("post_metrics") if isinstance(platform_data, dict) else None
    return _clean_metrics(metrics)


def _youtube_fallback(
    api: _Api,
    pending: list[tuple[dict, str]],
    youtube_key: str,
) -> None:
    if not pending:
        return
    if not youtube_key:
        logger.warning("YouTube Upload-Post metrigi olmayan kayitlar var ama YOUTUBE_API_KEY eksik")
        return
    for offset in range(0, len(pending), 50):
        batch = pending[offset : offset + 50]
        response = api.request(
            YOUTUBE_VIDEOS,
            params={"part": "statistics", "id": ",".join(post_id for _, post_id in batch), "key": youtube_key},
        )
        payload = _json_response(response)
        by_id = {}
        for item in payload.get("items", []):
            if not isinstance(item, dict):
                continue
            statistics = item.get("statistics")
            views = _number(statistics.get("viewCount")) if isinstance(statistics, dict) else None
            if item.get("id") is not None and views is not None:
                by_id[str(item["id"])] = views
        for run_metrics, post_id in batch:
            if post_id in by_id:
                run_metrics.setdefault("youtube", {})["views"] = by_id[post_id]


def collect_series_performance(
    slug: str,
    *,
    now: datetime | Callable[[], datetime] | None = None,
    http_get: Callable[..., Any] | None = None,
    upload_post_api_key: str | None = None,
    youtube_api_key: str | None = None,
) -> dict:
    """Collect one series, persist it, and return the scored document."""
    current = _utc_now(now)
    directory = data_dir(slug)
    output_path = directory / "performans.json"
    existing = _read_json(output_path, _new_document(slug), "performans.json")
    if not isinstance(existing, dict):
        logger.warning("performans.json koku nesne degil; temiz baslanacak")
        existing = _new_document(slug)
    existing["series"] = slug
    parts = _merge_published(existing, _published_parts(directory / "published.json"))
    existing["parts"] = parts

    meta = SeriesMeta.load(slug)
    if meta is None:
        raise FileNotFoundError(f"series.json bulunamadi: {directory}")
    profile = str(meta.upload_profile or "").strip()
    if not profile:
        raise ValueError(f"{slug}: upload_profile bos")

    upload_key = UPLOAD_POST_API_KEY if upload_post_api_key is None else upload_post_api_key
    upload_key = str(upload_key or "").strip()
    if not upload_key:
        logger.warning("%s: UPLOAD_POST_API_KEY eksik; performans toplanmadi", slug)
        return score_performance(existing)
    youtube_key = (
        os.getenv("YOUTUBE_API_KEY", "") if youtube_api_key is None else youtube_api_key
    )
    api = _Api(http_get or requests.get, upload_key)
    youtube_pending: list[tuple[dict, str]] = []
    run_records: list[tuple[dict, dict[str, dict], float | None]] = []
    stopped = False

    for part in parts:
        published_at = _parse_datetime(part.get("yayin_zamani"))
        age_hours = (
            max(0.0, (current - published_at).total_seconds() / 3600.0)
            if published_at is not None
            else None
        )
        measurements = part.get("olcumler")
        if not isinstance(measurements, list):
            measurements = []
            part["olcumler"] = measurements
        if age_hours is not None and age_hours > FREEZE_AGE_HOURS and measurements:
            part["donduruldu"] = True
        if part.get("donduruldu"):
            continue

        run_metrics: dict[str, dict] = {}
        run_records.append((part, run_metrics, age_hours))
        post_ids = part.get("post_ids") if isinstance(part.get("post_ids"), dict) else {}
        request_ids = part.get("request_ids") if isinstance(part.get("request_ids"), dict) else {}
        part["post_ids"] = post_ids
        part["request_ids"] = request_ids
        for platform in PLATFORMS:
            post_id = post_ids.get(platform)
            if not post_id:
                continue
            try:
                request_id = request_ids.get(platform)
                if not request_id:
                    request_id = _lookup_request_id(api, profile, platform, str(post_id))
                    if request_id:
                        request_ids[platform] = request_id
                metrics = _request_metrics(api, str(request_id), platform) if request_id else None
                if metrics:
                    run_metrics[platform] = metrics
                if platform == "youtube" and (not metrics or "views" not in metrics):
                    youtube_pending.append((run_metrics, str(post_id)))
            except _StopRun:
                stopped = True
                break
            except Exception as exc:
                logger.warning("%s part %s %s metrigi alinamadi: %s", slug, part.get("part"), platform, exc)
                if platform == "youtube":
                    youtube_pending.append((run_metrics, str(post_id)))
        if stopped:
            break

    if not stopped:
        try:
            _youtube_fallback(api, youtube_pending, str(youtube_key or "").strip())
        except _StopRun:
            stopped = True
        except Exception as exc:
            logger.warning("YouTube Data API yedegi basarisiz: %s", exc)

    # Attach exactly one snapshot per visited part after the batch fallback has
    # had a chance to add YouTube views. A stopped run still keeps its partials.
    for part, run_metrics, age_hours in run_records:
        measurements = part.get("olcumler", [])
        if run_metrics:
            measurement = {
                "ts": current.isoformat(),
                "yas_saat": round(age_hours, 3) if age_hours is not None else None,
            }
            measurement.update(run_metrics)
            measurements.append(measurement)
        if age_hours is not None and age_hours > FREEZE_AGE_HOURS and measurements:
            part["donduruldu"] = True

    existing["guncellendi"] = current.isoformat()
    existing["api_cagrilari"] = api.calls
    scored = score_performance(existing)
    _atomic_write_json(output_path, scored)
    return scored


def _print_score_table(document: dict) -> None:
    print("part\tyas\tyoutube\tinstagram\ttiktok\tpuan\tetiket")
    for part in _parts(document):
        measurements = part.get("olcumler", [])
        latest = measurements[-1] if isinstance(measurements, list) and measurements else {}
        age = latest.get("yas_saat", "-") if isinstance(latest, dict) else "-"
        views = []
        for platform in PLATFORMS:
            metrics = latest.get(platform) if isinstance(latest, dict) else None
            views.append(metrics.get("views", "-") if isinstance(metrics, dict) else "-")
        score = part.get("puan")
        score_text = "-" if score is None else f"{score:.3f}"
        print(f"{part.get('part', '-')}\t{age}\t{views[0]}\t{views[1]}\t{views[2]}\t{score_text}\t{part.get('etiket', 'olculmemis')}")


def _dry_run(slug: str) -> dict:
    path = data_dir(slug) / "performans.json"
    if not path.exists():
        print(f"performans.json yok: {path}")
        return _new_document(slug)
    document = _read_json(path, _new_document(slug), "performans.json")
    if not isinstance(document, dict):
        document = _new_document(slug)
    scored = score_performance(document)
    _print_score_table(scored)
    return scored


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Seri performans metriklerini topla")
    parser.add_argument("--series", required=True, help="Seri slug'i")
    parser.add_argument("--dry", action="store_true", help="Aga cikmadan mevcut puan tablosunu bas")
    args = parser.parse_args(argv)
    try:
        if args.dry:
            _dry_run(args.series)
        else:
            document = collect_series_performance(args.series)
            _print_score_table(document)
    except Exception as exc:
        logger.warning("%s performans toplayici hata verdi; yayin akisi devam ediyor: %s", args.series, exc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
