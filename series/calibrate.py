"""
FAZ 4 geri besleme halkasi.

En yeni gunluk analytics snapshot'ini seri yayin registry'leriyle birlestirir,
her seri icin calibration.json dosyasini atomik olarak yazar ve Telegram ozeti
gonderir. Notion #15 koprusunun tek mesru yazari GitHub Actions calibrate
cron'udur. Lokal kosular varsayilan olarak Notion'a yazmaz; acik ``--notion``
bayragi gerekir. ``--no-notion`` her ortamda kopruyu kapatir.

Notion claim'i calibration persist'inden once yapilir. Atomik persist uc
denemede de basarisiz olursa kosu kirmizi biter ve claim 24 saatlik lease ile
bir sonraki calibrate kosusunda telafi edilir. Bu gecikmeli telafi tasarimin
kabul edilmis parcasidir.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import time
import uuid
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import median
from typing import Any

import requests

from core.analytics import load_snapshots
from core.config import logger
from series import notifier
from series.bible import all_series_dirs, data_dir
from series.series_meta import SeriesMeta, plans_dir

CHANNEL_BY_SLUG = {
    "unnatural-lab": "sentinal_ihsan",
    "from-scratch": "aimagine",
    "event-horizon": "galactic_experiment",
    "flashpoints": "shadowedhistory",
    "the-vast": "aimagine",
    "footnotes": "shadowedhistory",
    "planetfall": "galactic_experiment",
}

NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
HTTP_TIMEOUT = 20
CARD_ID_RE = re.compile(r"^n15-[0-9a-f]{32}$")
BLOCKED_TEXT_RE = re.compile(
    r"\b(?:ignore|disregard|system|instruction|prompt)\b",
    re.IGNORECASE,
)
URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)


class NotionHTTPError(RuntimeError):
    def __init__(self, status: int, detail: str):
        super().__init__(f"Notion HTTP {status}: {detail}")
        self.status = status


class CalibrationPersistError(RuntimeError):
    """Uc atomik yazim denemesinin de bittigini bildirir."""


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_datetime(value: Any) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except (TypeError, ValueError):
        return None


def _number(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def sanitize_text(value: Any, limit: int) -> str:
    """Prompt'a girecek metni deterministik ve tek satirli hale getir."""
    text = str(value or "").replace("`", " ")
    text = text.replace("\r", " ").replace("\n", " ")
    text = URL_RE.sub(" ", text)
    text = BLOCKED_TEXT_RE.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit].rstrip()


def _plan_records(slug: str) -> list[dict]:
    records: list[dict] = []
    pdir = plans_dir(slug)
    if not pdir.exists():
        return records
    for path in sorted(pdir.glob("part*.json")):
        try:
            plan = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(plan, dict):
                continue
            episode = plan.get("episode") or {}
            number = episode.get("number")
            if not isinstance(number, int) or isinstance(number, bool):
                match = re.fullmatch(r"part(\d+)", path.stem)
                number = int(match.group(1)) if match else None
            records.append(
                {
                    "part": number,
                    "family": str(plan.get("family") or "").strip(),
                    "seed_id": plan.get("seed_id"),
                }
            )
        except Exception as exc:
            logger.warning(f"⚠️ {slug}: plan okunamadi ({path.name}): {exc}")
    return records


def _used_card_ids(slug: str) -> set[str]:
    return {
        str(item["seed_id"])
        for item in _plan_records(slug)
        if isinstance(item.get("seed_id"), str)
    }


def _load_previous(slug: str) -> dict:
    path = data_dir(slug) / "calibration.json"
    if not path.exists():
        return {}
    try:
        content = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(content, dict):
            raise ValueError("kok JSON nesnesi degil")
        return content
    except Exception as exc:
        logger.warning(f"⚠️ {slug}: onceki calibration okunamadi: {exc}")
        return {}


def _load_published(slug: str) -> tuple[list[dict], list[str]]:
    """Her part icin ts'i en yeni, YouTube kimligi dolu registry kaydini sec."""
    path = data_dir(slug) / "published.json"
    if not path.exists():
        return [], ["published.json yok"]
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise ValueError("kok liste degil")
    except Exception as exc:
        logger.warning(f"⚠️ {slug}: published.json okunamadi: {exc}")
        return [], [f"published.json bozuk: {exc}"]

    valid_by_part: dict[int, list[dict]] = defaultdict(list)
    null_parts: set[int] = set()
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        part = entry.get("part")
        if not isinstance(part, int) or isinstance(part, bool):
            continue
        youtube = (entry.get("results") or {}).get("youtube")
        if youtube is None or not str(youtube).strip():
            null_parts.add(part)
            continue
        ts = _parse_datetime(entry.get("ts"))
        valid_by_part[part].append(
            {
                "part": part,
                "video_id": str(youtube).strip(),
                "ts": ts,
                "ts_raw": str(entry.get("ts") or ""),
            }
        )

    chosen: list[dict] = []
    minimum = datetime.min.replace(tzinfo=timezone.utc)
    for part, entries in valid_by_part.items():
        chosen.append(max(entries, key=lambda item: item["ts"] or minimum))
    chosen.sort(key=lambda item: (item["ts"] or minimum, item["part"]))
    notes = [f"youtube kimligi olmayan part: {part}" for part in sorted(null_parts)]
    return chosen, notes


def _snapshot_time(snapshot_date: date, snapshot: dict) -> datetime:
    parsed = _parse_datetime(snapshot.get("generated_at"))
    if parsed:
        return parsed
    return datetime.combine(snapshot_date, datetime.max.time(), tzinfo=timezone.utc)


def _channel_day_count(snapshots: list[tuple[date, dict]], channel_name: str) -> int:
    return len(
        {
            snapshot_date
            for snapshot_date, snapshot in snapshots
            if isinstance((snapshot.get("channels") or {}).get(channel_name), dict)
        }
    )


def _first_48h_views(
    snapshots: list[tuple[date, dict]],
    channel_name: str,
    video_id: str,
    published: datetime,
) -> int | None:
    threshold = published + timedelta(hours=48)
    for snapshot_date, snapshot in snapshots:
        if _snapshot_time(snapshot_date, snapshot) < threshold:
            continue
        channel = (snapshot.get("channels") or {}).get(channel_name)
        video = (channel.get("videos") or {}).get(video_id) if isinstance(channel, dict) else None
        if isinstance(video, dict):
            return _number(video.get("views"))
    return None


def _video_metric(
    mode: str,
    snapshots: list[tuple[date, dict]],
    selected_snapshot: dict,
    channel_name: str,
    video_id: str,
    published: datetime,
) -> int | None:
    if mode == "yas_normalize":
        return _first_48h_views(snapshots, channel_name, video_id, published)
    channel = (selected_snapshot.get("channels") or {}).get(channel_name)
    video = (channel.get("videos") or {}).get(video_id) if isinstance(channel, dict) else None
    return _number(video.get("views")) if isinstance(video, dict) else None


def _channel_median(
    mode: str,
    snapshots: list[tuple[date, dict]],
    selected_date: date,
    selected_snapshot: dict,
    channel_name: str,
) -> float | None:
    generated = _snapshot_time(selected_date, selected_snapshot)
    channel = (selected_snapshot.get("channels") or {}).get(channel_name)
    videos = channel.get("videos") if isinstance(channel, dict) else {}
    metrics: list[int] = []
    for video_id, video in (videos or {}).items():
        if not isinstance(video, dict):
            continue
        published = _parse_datetime(video.get("published"))
        if not published:
            continue
        age = generated - published
        if age.total_seconds() < 48 * 3600 or age > timedelta(days=30):
            continue
        metric = _video_metric(
            mode, snapshots, selected_snapshot, channel_name, str(video_id), published
        )
        if metric is not None:
            metrics.append(metric)
    return float(median(metrics)) if metrics else None


def _explore_family(
    families: list[str],
    published: list[dict],
    plans: list[dict],
) -> str | None:
    if not families:
        return None
    family_by_part = {
        item["part"]: item["family"]
        for item in plans
        if isinstance(item.get("part"), int) and item.get("family") in families
    }
    counts = Counter()
    if published:
        newest = sorted(
            published,
            key=lambda item: item.get("ts") or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )[:14]
        counts.update(
            family_by_part[item["part"]]
            for item in newest
            if item.get("part") in family_by_part
        )
    else:
        counts.update(
            item["family"] for item in plans if item.get("family") in families
        )
    return min(families, key=lambda family: (counts[family], families.index(family)))


def _brief_note(
    mode: str,
    boost_families: list[str],
    explore_family: str | None,
    double_down: list[dict],
) -> str:
    pieces: list[str] = []
    if mode == "gecici_baseline":
        pieces.append("early baseline, limited data.")
    if boost_families:
        pieces.append("Prioritize proven families: " + ", ".join(boost_families) + ".")
    if explore_family:
        pieces.append(f"Reserve an exploration slot for {explore_family}.")
    if double_down:
        pattern = sorted({str(item.get("family") or "") for item in double_down if item.get("family")})
        if pattern:
            pieces.append("Double down on breakout patterns in: " + ", ".join(pattern) + ".")
    return sanitize_text(" ".join(pieces), 600)


def _boost_families(
    family_stats: list[dict], channel_median: float | None
) -> list[str]:
    if channel_median is None:
        return []
    eligible = [
        item
        for item in family_stats
        if item["n"] >= 3 and item["median"] > channel_median
    ]
    eligible.sort(key=lambda item: (-item["median"], -item["n"], item["family"]))
    return [item["family"] for item in eligible[:4]]


def _rollback_history(previous: dict, current: float | None) -> tuple[list[Any], bool]:
    old = ((previous.get("rollback") or {}).get("history") or [])
    history = list(old)[-2:] + [current]
    history = history[-3:]
    triggered = (
        len(history) >= 3
        and all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in history)
        and history[0] > history[1] > history[2]
    )
    return history, triggered


def _build_calibration(
    slug: str,
    meta: SeriesMeta,
    snapshots: list[tuple[date, dict]],
    previous: dict,
    now: datetime,
) -> tuple[dict, list[str]]:
    channel_name = CHANNEL_BY_SLUG[slug]
    selected_date, selected_snapshot = snapshots[-1]
    generated = _snapshot_time(selected_date, selected_snapshot)
    days = _channel_day_count(snapshots, channel_name)
    mode = "gecici_baseline" if days < 14 else "yas_normalize"
    channel_median = _channel_median(
        mode, snapshots, selected_date, selected_snapshot, channel_name
    )
    published, notes = _load_published(slug)
    plans = _plan_records(slug)
    family_by_part = {
        item["part"]: item["family"]
        for item in plans
        if isinstance(item.get("part"), int)
    }

    comparable: list[dict] = []
    latest_channel = (selected_snapshot.get("channels") or {}).get(channel_name) or {}
    latest_videos = latest_channel.get("videos") or {}
    for item in published:
        current_video = latest_videos.get(item["video_id"])
        if not isinstance(current_video, dict):
            notes.append(f"snapshot'ta bulunamayan video: {item['video_id']}")
            continue
        published_at = _parse_datetime(current_video.get("published"))
        if not published_at:
            notes.append(f"published zamani bozuk video: {item['video_id']}")
            continue
        age_h = (generated - published_at).total_seconds() / 3600
        if age_h < 48:
            continue
        metric = _video_metric(
            mode,
            snapshots,
            selected_snapshot,
            channel_name,
            item["video_id"],
            published_at,
        )
        if metric is None:
            continue
        comparable.append(
            {
                "part": item["part"],
                "video_id": item["video_id"],
                "family": family_by_part.get(item["part"], ""),
                "metric": metric,
                "age_h": round(age_h, 3),
            }
        )

    series_median = (
        float(median([item["metric"] for item in comparable])) if comparable else None
    )
    grouped: dict[str, list[int]] = defaultdict(list)
    for item in comparable:
        if item["family"]:
            grouped[item["family"]].append(item["metric"])
    family_stats = [
        {"family": family, "n": len(values), "median": float(median(values))}
        for family, values in grouped.items()
    ]
    family_stats.sort(key=lambda item: item["family"])

    double_down: list[dict] = []
    evaluation_reason = ""
    if channel_median is None or channel_median <= 0:
        evaluation_reason = "kanal medyani yok veya sifir; double-down ve pilot kapali"
    else:
        for item in comparable:
            ratio = item["metric"] / channel_median
            if ratio >= 5.0 and item["age_h"] >= 48:
                double_down.append(
                    {
                        "part": item["part"],
                        "video_id": item["video_id"],
                        "family": item["family"],
                        "metric": item["metric"],
                        "ratio": round(ratio, 4),
                    }
                )

    families = [
        str(value).strip()
        for value in (meta.auto_replenish.get("families") or [])
        if str(value).strip()
    ]
    zero_data = not published or not comparable
    boost = []
    explore = None
    empty_reason = None
    if zero_data:
        empty_reason = "veri_yok"
    else:
        boost = _boost_families(family_stats, channel_median)
        explore = _explore_family(families, published, plans)

    history, rollback_active = _rollback_history(previous, series_median)
    if rollback_active:
        boost = []
        explore = None
        empty_reason = "rollback"

    pilot = False
    pilot_detail = evaluation_reason
    if not evaluation_reason:
        if 3 <= len(published) <= 5 and len(comparable) >= 3:
            pilot = bool(series_median is not None and series_median < channel_median)
            pilot_detail = (
                "KARAR KARTI: pilot kanal medyaninin altinda"
                if pilot
                else "pilot esigi tetiklenmedi"
            )
        else:
            pilot_detail = "pilot penceresi veya karsilastirilabilir veri kosulu saglanmadi"

    recommendations = {
        "boost_families": boost,
        "explore_family": explore,
        "empty_reason": empty_reason,
    }
    brief = ""
    if empty_reason is None and (boost or explore):
        brief = _brief_note(mode, boost, explore, double_down)

    calibration = {
        "version": 1,
        "generated_at": now.astimezone(timezone.utc).isoformat(),
        "source_snapshot": selected_date.isoformat(),
        "mode": mode,
        "channel_median_30d": channel_median,
        "series_stats": {
            "n_published": len(published),
            "n_comparable": len(comparable),
            "series_median": series_median,
            "videos": comparable,
        },
        "family_stats": family_stats,
        "recommendations": recommendations,
        "double_down": double_down,
        "pilot_kill": {"triggered": pilot, "detail": pilot_detail},
        "rollback": {"active": rollback_active, "history": history},
        "brief_note": brief,
        "extra_topics": [],
    }
    return calibration, notes


def _atomic_write(path: Path, payload: dict, attempts: int = 3) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        temp_name = ""
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp",
                delete=False,
            ) as handle:
                temp_name = handle.name
                handle.write(encoded)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, path)
            return
        except Exception as exc:
            last_error = exc
            if temp_name:
                try:
                    os.unlink(temp_name)
                except OSError:
                    pass
            logger.warning(f"⚠️ {path}: atomik yazim denemesi {attempt}/3 basarisiz: {exc}")
    raise CalibrationPersistError(
        f"calibration persist uc denemede basarisiz: {last_error}"
    )


def _rich_text_value(prop: dict) -> str:
    values = prop.get("rich_text") or prop.get("title") or []
    return "".join(str(item.get("plain_text") or "") for item in values if isinstance(item, dict))


def _status_value(page: dict) -> str:
    prop = ((page.get("properties") or {}).get("Durum") or {})
    selected = prop.get("select") or prop.get("status") or {}
    return str(selected.get("name") or "")


def _claim_time(page: dict) -> datetime | None:
    prop = ((page.get("properties") or {}).get("Claim Zamani") or {})
    return _parse_datetime((prop.get("date") or {}).get("start"))


def _claim_token(page: dict) -> str:
    prop = ((page.get("properties") or {}).get("Claim Kosu") or {})
    return _rich_text_value(prop)


def _page_name(page: dict) -> str:
    props = page.get("properties") or {}
    return _rich_text_value(props.get("Name") or props.get("Ad") or {})


def _page_source(page: dict) -> str:
    prop = ((page.get("properties") or {}).get("Kaynak") or {})
    return str(prop.get("url") or "").strip()


def _notion_request(
    method: str,
    path: str,
    token: str,
    body: dict | None = None,
) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }
    last_status = 0
    last_detail = ""
    for attempt in range(1, 4):
        response = requests.request(
            method,
            f"{NOTION_API_BASE}/{path.lstrip('/')}",
            headers=headers,
            json=body,
            timeout=HTTP_TIMEOUT,
        )
        last_status = response.status_code
        if response.status_code == 429 or response.status_code >= 500:
            last_detail = response.text[:500]
            if attempt < 3:
                time.sleep(attempt)
                continue
        if not response.ok:
            raise NotionHTTPError(response.status_code, response.text[:500])
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("Notion yaniti JSON nesnesi degil")
        return data
    raise NotionHTTPError(last_status, last_detail)


def _query_pages(token: str, database_id: str, status: str) -> list[dict]:
    pages: list[dict] = []
    cursor: str | None = None
    while True:
        body: dict[str, Any] = {
            "filter": {"property": "Durum", "select": {"equals": status}},
            "page_size": 100,
        }
        if cursor:
            body["start_cursor"] = cursor
        result = _notion_request("POST", f"databases/{database_id}/query", token, body)
        pages.extend(page for page in (result.get("results") or []) if isinstance(page, dict))
        if not result.get("has_more"):
            break
        cursor = result.get("next_cursor")
        if not cursor:
            break
    return pages


def _ensure_notion_schema(token: str, database_id: str) -> None:
    database = _notion_request("GET", f"databases/{database_id}", token)
    properties = database.get("properties") or {}
    status_prop = properties.get("Durum") or {}
    status_select = status_prop.get("select")
    if not isinstance(status_select, dict):
        raise NotionHTTPError(400, "Durum select property degil")
    changes: dict[str, dict] = {}
    options = list(status_select.get("options") or [])
    if not any(option.get("name") == "Claimed" for option in options if isinstance(option, dict)):
        changes["Durum"] = {
            "select": {
                "options": options + [{"name": "Claimed", "color": "default"}]
            }
        }
    if "Claim Zamani" not in properties:
        changes["Claim Zamani"] = {"date": {}}
    if "Claim Kosu" not in properties:
        changes["Claim Kosu"] = {"rich_text": {}}
    if changes:
        _notion_request("PATCH", f"databases/{database_id}", token, {"properties": changes})


def _page_patch(token: str, page_id: str, properties: dict) -> dict:
    return _notion_request(
        "PATCH", f"pages/{page_id}", token, {"properties": properties}
    )


def _status_property(name: str) -> dict:
    return {"select": {"name": name}}


def _bridge_notion(
    slug: str,
    previous_topics: list[dict],
    used_cards: set[str],
    now: datetime,
    enabled: bool,
) -> tuple[list[dict], list[str]]:
    """Kopru bozulursa yeni claim'leri atar, onceki tuketilmemis listeyi korur."""
    retained = [
        dict(item)
        for item in previous_topics
        if isinstance(item, dict) and str(item.get("id") or "") not in used_cards
    ]
    notes: list[str] = []
    if slug != "event-horizon" or not enabled:
        return retained, notes
    token = os.getenv("NOTION_REELS_TOKEN", "").strip()
    database_id = os.getenv("NOTION_TOPIC_DB_ID", "").strip()
    if not token or not database_id:
        notes.append("Notion env yok; kopru atlandi")
        return retained, notes

    run_token = os.getenv("GITHUB_RUN_ID", "").strip() or uuid.uuid4().hex
    try:
        _ensure_notion_schema(token, database_id)

        for card_id in sorted(used_cards):
            if not CARD_ID_RE.fullmatch(card_id):
                continue
            page_id = card_id.removeprefix("n15-")
            _page_patch(
                token,
                page_id,
                {
                    "Durum": _status_property("Üretildi"),
                    "Claim Zamani": {"date": None},
                    "Claim Kosu": {"rich_text": []},
                },
            )

        approved_from_lease: list[dict] = []
        for page in _query_pages(token, database_id, "Claimed"):
            page_id = str(page.get("id") or "")
            normalized_id = "n15-" + page_id.replace("-", "").lower()
            claimed_at = _claim_time(page)
            if page_id and normalized_id in used_cards:
                _page_patch(
                    token,
                    page_id,
                    {
                        "Durum": _status_property("Üretildi"),
                        "Claim Zamani": {"date": None},
                        "Claim Kosu": {"rich_text": []},
                    },
                )
                continue
            if (
                page_id
                and normalized_id not in used_cards
                and claimed_at is not None
                and now - claimed_at > timedelta(hours=24)
            ):
                released = _page_patch(
                    token,
                    page_id,
                    {
                        "Durum": _status_property("Onaylandı"),
                        "Claim Zamani": {"date": None},
                        "Claim Kosu": {"rich_text": []},
                    },
                )
                approved_from_lease.append(released)

        approved = _query_pages(token, database_id, "Onaylandı") + approved_from_lease
        known = {str(item.get("id") or "") for item in retained}
        new_topics: list[dict] = []
        seen_pages: set[str] = set()
        for page in approved:
            page_id = str(page.get("id") or "")
            full_hex = page_id.replace("-", "").lower()
            card_id = "n15-" + full_hex
            if not page_id or not re.fullmatch(r"[0-9a-f]{32}", full_hex):
                continue
            if page_id in seen_pages or card_id in known:
                continue
            if card_id in used_cards:
                _page_patch(
                    token,
                    page_id,
                    {
                        "Durum": _status_property("Üretildi"),
                        "Claim Zamani": {"date": None},
                        "Claim Kosu": {"rich_text": []},
                    },
                )
                seen_pages.add(page_id)
                continue
            seen_pages.add(page_id)
            if not _page_source(page):
                notes.append(f"kaynaksiz kart: {sanitize_text(_page_name(page), 80) or page_id}")
                continue
            topic = sanitize_text(_page_name(page), 180)
            if not topic:
                notes.append(f"adi bos kart: {page_id}")
                continue
            claimed_at = now.astimezone(timezone.utc).isoformat()
            _page_patch(
                token,
                page_id,
                {
                    "Durum": _status_property("Claimed"),
                    "Claim Zamani": {"date": {"start": claimed_at}},
                    "Claim Kosu": {
                        "rich_text": [{"type": "text", "text": {"content": run_token}}]
                    },
                },
            )
            reread = _notion_request("GET", f"pages/{page_id}", token)
            if _claim_token(reread) != run_token:
                notes.append(f"CAS yabanci claim: {page_id}")
                continue
            new_topics.append(
                {
                    "id": card_id,
                    "topic": topic,
                    "page_id": page_id,
                    "claimed_at": claimed_at,
                }
            )
            known.add(card_id)
        return retained + new_topics, notes
    except Exception as exc:
        notes.append(f"Notion koprusu fail-closed: {exc}")
        logger.warning(f"⚠️ {slug}: {notes[-1]}")
        return retained, notes


def _summary(slug: str, calibration: dict, notes: list[str]) -> str:
    stats = calibration["series_stats"]
    median_value = stats["series_median"]
    median_text = "yok" if median_value is None else f"{median_value:g}"
    line1 = (
        f"📊 *{slug}* {calibration['mode']}: "
        f"{stats['n_comparable']}/{stats['n_published']} karsilastirilabilir, "
        f"seri medyani {median_text}"
    )
    decisions: list[str] = []
    if calibration["rollback"]["active"]:
        decisions.append("ROLLBACK: iki ardisik siki dusus")
    if calibration["pilot_kill"]["triggered"]:
        decisions.append(calibration["pilot_kill"]["detail"])
    decisions.extend(notes)
    return line1 + (("\n" + " | ".join(decisions)) if decisions else "")


def _send_summary(text: str) -> None:
    try:
        if notifier.enabled():
            notifier.send_message(text)
    except Exception as exc:
        logger.warning(f"⚠️ Kalibrasyon Telegram ozeti gonderilemedi: {exc}")


def calibrate_series(
    slug: str,
    snapshots: list[tuple[date, dict]],
    *,
    notion_enabled: bool,
    telegram_enabled: bool,
    now: datetime | None = None,
) -> dict:
    if slug not in CHANNEL_BY_SLUG:
        raise ValueError(f"analytics kanal eslemesi yok: {slug}")
    meta = SeriesMeta.load(slug)
    if not meta:
        raise ValueError("series.json okunamadi")
    previous = _load_previous(slug)
    current_time = now or _utc_now()
    calibration, notes = _build_calibration(
        slug, meta, snapshots, previous, current_time
    )
    previous_topics = previous.get("extra_topics") or []
    used_cards = _used_card_ids(slug)
    calibration["extra_topics"], bridge_notes = _bridge_notion(
        slug,
        previous_topics if isinstance(previous_topics, list) else [],
        used_cards,
        current_time,
        notion_enabled,
    )
    notes.extend(bridge_notes)
    try:
        _atomic_write(data_dir(slug) / "calibration.json", calibration)
    except Exception as exc:
        raise CalibrationPersistError(str(exc)) from exc
    logger.info(
        f"✅ {slug}: calibration.json yazildi "
        f"({calibration['mode']}, n={calibration['series_stats']['n_comparable']})"
    )
    if telegram_enabled:
        _send_summary(_summary(slug, calibration, notes))
    return calibration


def _eligible_slugs(requested: str | None = None) -> list[str]:
    candidates = [requested] if requested else list(all_series_dirs())
    eligible: list[str] = []
    for slug in candidates:
        if not slug:
            continue
        meta = SeriesMeta.load(slug)
        if not meta:
            continue
        if meta.status != "active" or not meta.auto_replenish.get("enabled"):
            if requested:
                logger.info(f"ℹ️ {slug}: aktif auto_replenish serisi degil, atlandi")
            continue
        if slug not in CHANNEL_BY_SLUG:
            logger.warning(f"⚠️ {slug}: analytics kanal eslemesi yok, kalibrasyon disi")
            continue
        eligible.append(slug)
    return sorted(eligible)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "FAZ 4 kalibrasyonu. Lokal kosuda Notion varsayilan kapali; "
            "yalniz --notion ile acilir."
        )
    )
    parser.add_argument("--series", help="Yalniz verilen seri slug'ini kalibre et")
    parser.add_argument("--no-telegram", action="store_true", help="Telegram ozetlerini kapat")
    notion_group = parser.add_mutually_exclusive_group()
    notion_group.add_argument(
        "--no-notion", action="store_true", help="Notion #15 koprusunu kapat"
    )
    notion_group.add_argument(
        "--notion", action="store_true", help="Lokal kosuda Notion #15 koprusunu ac"
    )
    args = parser.parse_args(argv)

    in_actions = bool(os.getenv("GITHUB_ACTIONS"))
    notion_enabled = not args.no_notion and (in_actions or args.notion)
    if not notion_enabled and not args.no_notion and not in_actions:
        logger.info("ℹ️ Lokal kosu: Notion koprusu varsayilan olarak kapali; --notion ile acilir")

    try:
        snapshots = load_snapshots()
    except Exception as exc:
        logger.error(f"❌ Snapshotlar okunamadi: {exc}")
        return 1
    if not snapshots:
        logger.error("❌ Gunluk analytics snapshot'i yok")
        return 1

    written = 0
    persist_failed = False
    for slug in _eligible_slugs(args.series):
        try:
            calibrate_series(
                slug,
                snapshots,
                notion_enabled=notion_enabled,
                telegram_enabled=not args.no_telegram,
            )
            written += 1
        except CalibrationPersistError as exc:
            persist_failed = True
            logger.exception(f"❌ {slug}: calibration persist basarisiz: {exc}")
        except Exception as exc:
            if isinstance(exc, CalibrationPersistError):
                persist_failed = True
            logger.exception(f"❌ {slug}: kalibrasyon basarisiz: {exc}")
    if written == 0:
        logger.error("❌ Hicbir seri calibration.json yazamadi")
        return 1
    if persist_failed:
        logger.error("❌ En az bir calibration persist uc denemede basarisiz; kosu kirmizi")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
