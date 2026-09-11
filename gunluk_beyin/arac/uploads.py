"""List a channel's recent uploads, from whichever source is actually alive.

Measured 2026-09-10, from a home IP and from a GitHub Actions runner alike:

    https://www.youtube.com/feeds/videos.xml?channel_id=UC...   ->  404 / 500

That is not our channels and not a datacenter-IP block: MrBeast's and Google's
feeds return 404 too, and the `playlist_id=UU...` variant returns 404 as well.
The public Atom feed is simply not serving. Meanwhile a plain `watch?v=` page
loads fine from both places, which is why refreshing view counts kept working
while listing new videos did not.

So the feed cannot be the only source. Data API v3 is primary here: it is
authenticated, it is the same path `core/analytics.py` already runs green in
CI, and it answers with a real publish timestamp. RSS stays as a fallback for
the day it comes back or the day we run out of API quota.

Returns rows in the shape the ledger already stores, so callers do not change:

    {"video_id", "baslik", "tarih", "yayin_ts", "rss_izlenme"}

`rss_izlenme` is None on the API path. Nothing depends on it being a number,
and `beyin.py topla` replaces it with a live count on the next run anyway.
"""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

API_BASE = "https://www.googleapis.com/youtube/v3"
API_PAGE_SIZE = 50          # hard maximum the endpoint accepts
API_TIMEOUT = 45
RETRY_STATUS = (429, 500, 502, 503, 504)


def api_key():
    """Read YOUTUBE_API_KEY from the environment, then from the repo `.env`.

    CI supplies it as an env var. Locally the repo `.env` is the one place the
    other tools already look, and it is gitignored.
    """
    key = (os.getenv("YOUTUBE_API_KEY") or "").strip()
    if key:
        return key
    here = os.path.dirname(os.path.abspath(__file__))
    repo_env = os.path.join(os.path.dirname(os.path.dirname(here)), ".env")
    try:
        with open(repo_env, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                if line.startswith("YOUTUBE_API_KEY="):
                    return line.split("=", 1)[1].strip()
    except OSError:
        pass
    return ""


def uploads_playlist(channel_id):
    """Every channel's uploads live in a playlist whose id is the channel id
    with the `UC` prefix swapped for `UU`."""
    if not channel_id.startswith("UC") or len(channel_id) < 3:
        raise ValueError("not a channel id: %r" % (channel_id,))
    return "UU" + channel_id[2:]


def _api_get(resource, params, timeout=API_TIMEOUT, attempts=3):
    """GET one Data API page. Returns (body, error); exactly one is None."""
    url = "%s/%s?%s" % (API_BASE, resource, urllib.parse.urlencode(params))
    last = None
    for i in range(max(1, attempts)):
        if i:
            time.sleep(1 + 2 * i)
        try:
            request = urllib.request.Request(
                url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8", "replace")), None
        except urllib.error.HTTPError as exc:
            detail = ""
            try:
                detail = exc.read().decode("utf-8", "replace")[:200]
            except Exception:  # noqa: BLE001 - the status is what matters
                pass
            last = "HTTP %s %s" % (exc.code, detail)
            if exc.code not in RETRY_STATUS:
                # 400/401/403/404 will not get better by asking again.
                return None, last
        except Exception as exc:  # noqa: BLE001 - network, DNS, JSON, anything
            last = "%s: %s" % (type(exc).__name__, exc)
    return None, last


def from_api(channel_id, limit, key=None):
    """List uploads through Data API v3. Returns (rows, error)."""
    key = key if key is not None else api_key()
    if not key:
        return [], "YOUTUBE_API_KEY yok"
    try:
        playlist = uploads_playlist(channel_id)
    except ValueError as exc:
        return [], str(exc)

    rows, page_token = [], None
    while len(rows) < limit:
        params = {
            "part": "snippet,contentDetails",
            "playlistId": playlist,
            "maxResults": min(API_PAGE_SIZE, limit - len(rows)),
            "key": key,
        }
        if page_token:
            params["pageToken"] = page_token
        body, error = _api_get("playlistItems", params)
        if error:
            return [], error
        items = body.get("items") or []
        if not items:
            break
        for item in items:
            content = item.get("contentDetails") or {}
            snippet = item.get("snippet") or {}
            video_id = content.get("videoId") or (
                snippet.get("resourceId") or {}).get("videoId")
            published = content.get("videoPublishedAt") or ""
            if not video_id or not published:
                # No publish timestamp means deleted or private. It cannot be
                # measured and it must not be age-gated on a guessed date.
                continue
            rows.append({
                "video_id": str(video_id),
                "baslik": str(snippet.get("title") or "").strip(),
                "tarih": published[:10],
                "yayin_ts": published,
                "rss_izlenme": None,
            })
        page_token = body.get("nextPageToken")
        if not page_token:
            break

    if not rows:
        return [], "API bos liste dondurdu (playlist %s)" % playlist
    # The uploads playlist is newest-first already, but sorting makes that a
    # guarantee rather than an assumption the age gate silently depends on.
    rows.sort(key=lambda r: r["yayin_ts"], reverse=True)
    return rows[:limit], None


def list_uploads(channel_id, limit, key=None, rss_fn=None):
    """Best available upload list.

    Returns (rows, error, source). `error` is not None only when EVERY source
    failed - callers must stop in that case, because an empty list from a dead
    source is indistinguishable from "no new videos" and would silently freeze
    the ledger.
    """
    rows, api_error = from_api(channel_id, limit, key=key)
    if not api_error:
        return rows, None, "api"

    if rss_fn is None:
        try:
            from kanal import youtube_rss_ex as rss_fn  # noqa: PLC0415
        except Exception as exc:  # noqa: BLE001
            return [], "API: %s | RSS yuklenemedi: %s" % (api_error, exc), None
    rss_rows, rss_error = rss_fn(channel_id, limit)
    if not rss_error and rss_rows:
        return rss_rows, None, "rss"

    return [], "API: %s | RSS: %s" % (
        api_error, rss_error or "bos liste"), None
