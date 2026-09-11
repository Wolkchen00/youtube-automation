"""Probe every way of listing a channel's uploads, print which ones work here.

Why this exists: the daily brain died in GitHub Actions with
`HTTP Error 404` on https://www.youtube.com/feeds/videos.xml, while the same
runner had no trouble reading https://www.youtube.com/watch?v=... pages.
So the block is specific to the feed endpoint, not to YouTube as a whole.

Rather than guess a fix, run this on the machine that is actually failing and
read the table. Every strategy returns the same shape, so whichever one passes
can be wired into `arac/kanal.py` unchanged.

Usage:
    python tools/probe_feed.py                    # default channel
    python tools/probe_feed.py UCUdp0KLBh4EeeSgVbwS_DhA
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

DEFAULT_CHANNEL = "UCUdp0KLBh4EeeSgVbwS_DhA"  # shadowedhistory / flashpoints
TIMEOUT = 45

CHROME_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0 Safari/537.36"
)


def fetch(url, headers, timeout=TIMEOUT):
    """Return (body, error). Exactly one of them is None."""
    try:
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8", "replace"), None
    except Exception as exc:  # noqa: BLE001 - we want the message, whatever it is
        return None, "%s: %s" % (type(exc).__name__, exc)


def count_entries(xml):
    return xml.count("<yt:videoId>")


# --- strategies -------------------------------------------------------------
# Each returns (ok, detail). `ok` means we got a real, parseable video list.


def strat_rss_current(channel_id):
    """Exactly what arac/kanal.py sends today."""
    headers = {"User-Agent": CHROME_UA, "Accept-Language": "en-US,en;q=0.9"}
    url = "https://www.youtube.com/feeds/videos.xml?channel_id=" + channel_id
    body, error = fetch(url, headers)
    if error:
        return False, error
    n = count_entries(body)
    return n > 0, "%d entries, %d bytes" % (n, len(body))


def strat_rss_no_ua(channel_id):
    """No headers at all - maybe the Chrome UA is what trips the block."""
    url = "https://www.youtube.com/feeds/videos.xml?channel_id=" + channel_id
    body, error = fetch(url, {})
    if error:
        return False, error
    n = count_entries(body)
    return n > 0, "%d entries, %d bytes" % (n, len(body))


def strat_rss_feed_headers(channel_id):
    """Ask like a feed reader, not like a browser."""
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; feedparser/6.0)",
        "Accept": "application/atom+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    url = "https://www.youtube.com/feeds/videos.xml?channel_id=" + channel_id
    body, error = fetch(url, headers)
    if error:
        return False, error
    n = count_entries(body)
    return n > 0, "%d entries, %d bytes" % (n, len(body))


def strat_rss_googleusercontent(channel_id):
    """The same feed served from a different host name."""
    headers = {"User-Agent": CHROME_UA}
    url = "https://youtube.com/feeds/videos.xml?channel_id=" + channel_id
    body, error = fetch(url, headers)
    if error:
        return False, error
    n = count_entries(body)
    return n > 0, "%d entries, %d bytes" % (n, len(body))


def strat_channel_page(channel_id):
    """Scrape the /videos page - a normal page, and pages do load from here."""
    headers = {"User-Agent": CHROME_UA, "Accept-Language": "en-US,en;q=0.9"}
    url = "https://www.youtube.com/channel/%s/videos" % channel_id
    body, error = fetch(url, headers)
    if error:
        return False, error
    ids = set()
    marker = '"videoId":"'
    start = 0
    while True:
        i = body.find(marker, start)
        if i < 0:
            break
        i += len(marker)
        j = body.find('"', i)
        if j > i:
            ids.add(body[i:j])
        start = j
    return len(ids) > 0, "%d distinct videoIds, %d bytes" % (len(ids), len(body))


def strat_data_api(channel_id):
    """YouTube Data API v3. This is the path core/analytics.py already uses,
    and that workflow succeeded on a runner today."""
    key = (os.getenv("YOUTUBE_API_KEY") or "").strip()
    if not key:
        return False, "YOUTUBE_API_KEY not set - cannot test"
    uploads = "UU" + channel_id[2:]
    query = urllib.parse.urlencode({
        "part": "snippet,contentDetails",
        "playlistId": uploads,
        "maxResults": 6,
        "key": key,
    })
    url = "https://www.googleapis.com/youtube/v3/playlistItems?" + query
    body, error = fetch(url, {"Accept": "application/json"})
    if error:
        return False, error
    try:
        data = json.loads(body)
    except ValueError as exc:
        return False, "not JSON: %s" % exc
    items = data.get("items") or []
    if not items:
        return False, "empty items"
    first = items[0]
    return True, "%d items, newest=%s %s" % (
        len(items),
        first.get("contentDetails", {}).get("videoId"),
        first.get("contentDetails", {}).get("videoPublishedAt"),
    )


def strat_watch_page(channel_id):
    """Control case: does a plain watch page load? `topla` suggested it does."""
    headers = {"User-Agent": CHROME_UA, "Accept-Language": "en-US,en;q=0.9"}
    body, error = fetch("https://www.youtube.com/watch?v=dQw4w9WgXcQ", headers)
    if error:
        return False, error
    has_views = '"viewCount":"' in body
    return has_views, "viewCount present=%s, %d bytes" % (has_views, len(body))


STRATEGIES = [
    ("rss_current       ", strat_rss_current),
    ("rss_no_ua         ", strat_rss_no_ua),
    ("rss_feed_headers  ", strat_rss_feed_headers),
    ("rss_bare_host     ", strat_rss_googleusercontent),
    ("channel_videos_page", strat_channel_page),
    ("data_api_v3       ", strat_data_api),
    ("watch_page (control)", strat_watch_page),
]


def main():
    channel_id = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CHANNEL
    print("probing channel %s" % channel_id)
    print("=" * 78)
    results = {}
    for name, fn in STRATEGIES:
        started = time.time()
        try:
            ok, detail = fn(channel_id)
        except Exception as exc:  # noqa: BLE001
            ok, detail = False, "raised %s: %s" % (type(exc).__name__, exc)
        elapsed = time.time() - started
        results[name.strip()] = ok
        print("%-22s %-4s %5.1fs  %s" % (name, "OK" if ok else "FAIL", elapsed, detail))
        time.sleep(1)
    print("=" * 78)
    working = [n for n, ok in results.items() if ok]
    print("working strategies: %s" % (", ".join(working) if working else "NONE"))


if __name__ == "__main__":
    main()
