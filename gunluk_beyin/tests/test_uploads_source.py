"""Adversarial tests for arac/uploads.py and the brain's use of it.

Context these tests defend: on 2026-09-10 the YouTube Atom feed started
returning 404/500 to everyone (our channels, MrBeast, Google alike). The brain
listed new videos from that feed and nothing else, so `olc` stopped dead in CI.
The replacement puts Data API v3 first and keeps RSS as a fallback.

The failure mode worth guarding hardest is NOT "the source is down" - that one
is loud. It is "the source is down and we report success with an empty list",
because an empty list is indistinguishable from "no new videos" and freezes the
ledger while every run stays green.
"""
import io
import json
import os
import sys
import types
import urllib.error

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "arac")
for path in (ROOT, TOOLS):
    if path not in sys.path:
        sys.path.insert(0, path)

import uploads  # noqa: E402


# --------------------------------------------------------------- helpers

def item(video_id, published, title="t"):
    return {
        "snippet": {"title": title, "resourceId": {"videoId": video_id}},
        "contentDetails": {"videoId": video_id, "videoPublishedAt": published},
    }


def page(items, next_token=None):
    body = {"items": items}
    if next_token:
        body["nextPageToken"] = next_token
    return body


def fake_api(pages, calls=None):
    """Return an _api_get replacement that serves `pages` in order."""
    queue = list(pages)

    def _get(resource, params, timeout=None, attempts=3):
        if calls is not None:
            calls.append(dict(params))
        if not queue:
            return page([]), None
        nxt = queue.pop(0)
        if isinstance(nxt, str):
            return None, nxt
        return nxt, None

    return _get


# --------------------------------------------------- uploads_playlist

def test_playlist_id_swaps_uc_for_uu():
    assert uploads.uploads_playlist("UCUdp0KLBh4EeeSgVbwS_DhA") == \
        "UUUdp0KLBh4EeeSgVbwS_DhA"


def test_playlist_id_keeps_leading_dash_channels():
    # UC-Aht8... is a real channel of ours; a naive lstrip("UC") would eat
    # more than the prefix on ids that start with those letters again.
    assert uploads.uploads_playlist("UC-Aht8VqAUMTUKYRQA3agYQ") == \
        "UU-Aht8VqAUMTUKYRQA3agYQ"


def test_playlist_id_does_not_eat_repeated_prefix_letters():
    assert uploads.uploads_playlist("UCUCUCabc") == "UUUCUCabc"


@pytest.mark.parametrize("bad", ["", "UC", "x", "PLabcdef", "uc-lowercase"])
def test_playlist_id_rejects_non_channel_ids(bad):
    with pytest.raises(ValueError):
        uploads.uploads_playlist(bad)


# ------------------------------------------------------------- from_api

def test_from_api_without_key_reports_error_not_empty_success(monkeypatch):
    monkeypatch.setattr(uploads, "api_key", lambda: "")
    rows, error = uploads.from_api("UCabc", 5)
    assert rows == []
    assert error, "anahtarsizlik SESSIZCE bos liste donmemeli"


def test_from_api_shape_matches_ledger_fields(monkeypatch):
    monkeypatch.setattr(uploads, "_api_get",
                        fake_api([page([item("aaa", "2026-09-09T22:51:30Z", "Baslik")])]))
    rows, error = uploads.from_api("UCabc", 5, key="k")
    assert error is None
    assert rows == [{
        "video_id": "aaa",
        "baslik": "Baslik",
        "tarih": "2026-09-09",
        "yayin_ts": "2026-09-09T22:51:30Z",
        "rss_izlenme": None,
    }]


def test_from_api_drops_items_without_publish_timestamp(monkeypatch):
    # Deleted/private entries keep a videoId but lose videoPublishedAt. Letting
    # one through would hand the 24h age gate a missing date and it would be
    # treated as "old enough", then measurement would fail on a dead video.
    bad = {"snippet": {"title": "Private video"},
           "contentDetails": {"videoId": "ghost"}}
    monkeypatch.setattr(uploads, "_api_get",
                        fake_api([page([bad, item("ok1", "2026-09-08T10:00:00Z")])]))
    rows, error = uploads.from_api("UCabc", 5, key="k")
    assert error is None
    assert [r["video_id"] for r in rows] == ["ok1"]


def test_from_api_all_items_unusable_is_an_error(monkeypatch):
    bad = {"snippet": {"title": "Deleted video"}, "contentDetails": {}}
    monkeypatch.setattr(uploads, "_api_get", fake_api([page([bad])]))
    rows, error = uploads.from_api("UCabc", 5, key="k")
    assert rows == []
    assert error, "hicbir kullanilabilir kayit yokken hata bildirilmeli"


def test_from_api_sorts_newest_first_even_if_api_does_not(monkeypatch):
    monkeypatch.setattr(uploads, "_api_get", fake_api([page([
        item("old", "2026-09-01T00:00:00Z"),
        item("new", "2026-09-09T00:00:00Z"),
        item("mid", "2026-09-05T00:00:00Z"),
    ])]))
    rows, _ = uploads.from_api("UCabc", 5, key="k")
    assert [r["video_id"] for r in rows] == ["new", "mid", "old"]


def test_from_api_respects_limit_and_page_size(monkeypatch):
    calls = []
    monkeypatch.setattr(uploads, "_api_get", fake_api([
        page([item("v%d" % i, "2026-09-%02dT00:00:00Z" % (i + 1)) for i in range(50)],
             next_token="p2"),
        page([item("w%d" % i, "2026-08-%02dT00:00:00Z" % (i + 1)) for i in range(50)]),
    ], calls=calls))
    rows, error = uploads.from_api("UCabc", 60, key="k")
    assert error is None
    assert len(rows) == 60
    assert calls[0]["maxResults"] == 50, "sayfa boyutu 50'yi asamaz"
    assert calls[1]["maxResults"] == 10, "ikinci sayfa sadece kalani istemeli"
    assert calls[1]["pageToken"] == "p2"


def test_from_api_stops_when_no_next_page(monkeypatch):
    calls = []
    monkeypatch.setattr(uploads, "_api_get",
                        fake_api([page([item("a", "2026-09-09T00:00:00Z")])], calls=calls))
    rows, error = uploads.from_api("UCabc", 100, key="k")
    assert error is None and len(rows) == 1
    assert len(calls) == 1, "nextPageToken yokken tekrar istenmemeli"


def test_from_api_propagates_quota_error(monkeypatch):
    monkeypatch.setattr(uploads, "_api_get",
                        fake_api(["HTTP 403 quotaExceeded"]))
    rows, error = uploads.from_api("UCabc", 5, key="k")
    assert rows == []
    assert "403" in error


# -------------------------------------------------------------- _api_get

class _Resp:
    def __init__(self, payload):
        self._payload = json.dumps(payload).encode()

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_api_get_does_not_retry_permanent_errors(monkeypatch):
    tries = []

    def boom(request, timeout=None):
        tries.append(1)
        raise urllib.error.HTTPError(
            request.full_url, 403, "Forbidden", {}, io.BytesIO(b"quota"))

    monkeypatch.setattr(uploads.urllib.request, "urlopen", boom)
    monkeypatch.setattr(uploads.time, "sleep", lambda s: None)
    body, error = uploads._api_get("playlistItems", {"key": "k"})
    assert body is None and "403" in error
    assert len(tries) == 1, "403 tekrar denenmemeli, kota geri gelmez"


def test_api_get_retries_transient_then_succeeds(monkeypatch):
    state = {"n": 0}

    def flaky(request, timeout=None):
        state["n"] += 1
        if state["n"] < 3:
            raise urllib.error.HTTPError(
                request.full_url, 503, "busy", {}, io.BytesIO(b""))
        return _Resp({"items": []})

    monkeypatch.setattr(uploads.urllib.request, "urlopen", flaky)
    monkeypatch.setattr(uploads.time, "sleep", lambda s: None)
    body, error = uploads._api_get("playlistItems", {"key": "k"})
    assert error is None and body == {"items": []}
    assert state["n"] == 3


def test_api_get_gives_up_after_attempts(monkeypatch):
    def always(request, timeout=None):
        raise urllib.error.HTTPError(
            request.full_url, 500, "boom", {}, io.BytesIO(b""))

    monkeypatch.setattr(uploads.urllib.request, "urlopen", always)
    monkeypatch.setattr(uploads.time, "sleep", lambda s: None)
    body, error = uploads._api_get("playlistItems", {"key": "k"}, attempts=2)
    assert body is None and "500" in error


def test_api_get_error_string_does_not_leak_the_key(monkeypatch):
    # The key travels in the query string. CI prints whatever error we return,
    # and GitHub only masks values it knows are secrets in THAT job - a leaked
    # key in an artifact or a pasted log is a real exposure.
    secret = "AIzaSyTOTALLY-NOT-A-REAL-KEY"

    def boom(request, timeout=None):
        raise urllib.error.HTTPError(
            request.full_url, 400, "Bad Request", {},
            io.BytesIO(b"keyInvalid"))

    monkeypatch.setattr(uploads.urllib.request, "urlopen", boom)
    monkeypatch.setattr(uploads.time, "sleep", lambda s: None)
    body, error = uploads._api_get("playlistItems", {"key": secret})
    assert body is None
    assert secret not in error, "hata metni API anahtarini sizdiriyor"


# ----------------------------------------------------------- list_uploads

def test_list_uploads_prefers_api(monkeypatch):
    monkeypatch.setattr(uploads, "_api_get",
                        fake_api([page([item("a", "2026-09-09T00:00:00Z")])]))
    called = []
    rows, error, source = uploads.list_uploads(
        "UCabc", 5, key="k", rss_fn=lambda *a: called.append(1) or ([], None))
    assert error is None and source == "api" and len(rows) == 1
    assert not called, "API calisirken RSS'e gidilmemeli"


def test_list_uploads_falls_back_to_rss(monkeypatch):
    monkeypatch.setattr(uploads, "_api_get", fake_api(["HTTP 403 quota"]))
    rss_rows = [{"video_id": "r1", "baslik": "b", "tarih": "2026-09-09",
                 "yayin_ts": "2026-09-09T00:00:00Z", "rss_izlenme": 7}]
    rows, error, source = uploads.list_uploads(
        "UCabc", 5, key="k", rss_fn=lambda cid, lim: (rss_rows, None))
    assert error is None and source == "rss" and rows == rss_rows


def test_list_uploads_errors_when_both_sources_fail(monkeypatch):
    monkeypatch.setattr(uploads, "_api_get", fake_api(["HTTP 403 quota"]))
    rows, error, source = uploads.list_uploads(
        "UCabc", 5, key="k", rss_fn=lambda cid, lim: ([], "HTTP 404"))
    assert rows == [] and source is None
    assert "403" in error and "404" in error, \
        "iki kaynagin da neden dustugu raporda gorunmeli"


def test_list_uploads_treats_empty_rss_as_failure(monkeypatch):
    # THE silent-green trap: RSS says "fine" and hands back nothing. If that
    # counted as success the brain would print "0 new videos" forever.
    monkeypatch.setattr(uploads, "_api_get", fake_api(["HTTP 500"]))
    rows, error, source = uploads.list_uploads(
        "UCabc", 5, key="k", rss_fn=lambda cid, lim: ([], None))
    assert rows == [] and source is None and error


def test_list_uploads_never_returns_empty_and_ok(monkeypatch):
    """Property: (rows == [] and error is None) must be unreachable."""
    scenarios = [
        (["HTTP 403"], ([], None)),
        (["HTTP 403"], ([], "HTTP 404")),
        ([page([])], ([], None)),
        ([page([{"snippet": {}, "contentDetails": {}}])], ([], None)),
    ]
    for api_pages, rss_result in scenarios:
        monkeypatch.setattr(uploads, "_api_get", fake_api(api_pages))
        rows, error, _ = uploads.list_uploads(
            "UCabc", 5, key="k", rss_fn=lambda cid, lim: rss_result)
        assert not (rows == [] and error is None), \
            "bos liste + hatasiz = sessiz yesil, yasak"


# ------------------------------------------------------------- api_key

def test_api_key_prefers_environment(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "from-env")
    assert uploads.api_key() == "from-env"


def test_api_key_falls_back_to_repo_env_file(monkeypatch, tmp_path):
    module_home = tmp_path / "gunluk_beyin" / "arac"
    module_home.mkdir(parents=True)
    (tmp_path / ".env").write_text(
        "\n".join(["KIE_AI_API_KEY=other", "YOUTUBE_API_KEY=from-dotenv", ""]),
        encoding="utf-8")
    monkeypatch.setattr(uploads, "__file__", str(module_home / "uploads.py"))
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    assert uploads.api_key() == "from-dotenv"


def test_api_key_ignores_blank_environment(monkeypatch, tmp_path):
    module_home = tmp_path / "gunluk_beyin" / "arac"
    module_home.mkdir(parents=True)
    (tmp_path / ".env").write_text("YOUTUBE_API_KEY=real\n", encoding="utf-8")
    monkeypatch.setattr(uploads, "__file__", str(module_home / "uploads.py"))
    monkeypatch.setenv("YOUTUBE_API_KEY", "   ")
    assert uploads.api_key() == "real", \
        "bosluk dolu degisken gercek anahtari golgelememeli"


def test_api_key_returns_empty_when_nothing_is_configured(monkeypatch, tmp_path):
    # env_candidates() deliberately ends at the automation repo's own .env so
    # the /reel-analiz copy of this module can find the key from anywhere.
    # That means "nothing configured" can only be tested with the candidate
    # list pinned, otherwise this asserts against the developer's real key.
    monkeypatch.setattr(uploads, "env_candidates",
                        lambda: [str(tmp_path / "absent.env")])
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    assert uploads.api_key() == ""


def test_api_key_skips_env_files_with_a_blank_value(monkeypatch, tmp_path):
    empty = tmp_path / "empty.env"
    empty.write_text("YOUTUBE_API_KEY=\n", encoding="utf-8")
    real = tmp_path / "real.env"
    real.write_text("YOUTUBE_API_KEY=second-file\n", encoding="utf-8")
    monkeypatch.setattr(uploads, "env_candidates",
                        lambda: [str(empty), str(real)])
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    assert uploads.api_key() == "second-file", \
        "bos degerli .env aramayi erken bitirmemeli"


def test_env_candidates_walks_up_and_ends_at_the_repo(monkeypatch, tmp_path):
    module_home = tmp_path / "a" / "b" / "c"
    module_home.mkdir(parents=True)
    monkeypatch.setattr(uploads, "__file__", str(module_home / "uploads.py"))
    found = uploads.env_candidates()
    assert str(module_home / ".env") == found[0]
    assert str(tmp_path / "a" / ".env") in found, "yukari dogru yurumeli"
    assert found[-1].endswith(os.path.join("Youtube", ".env")), \
        "son care otomasyon deposunun .env'i olmali"


# ------------------------------------------- brain stops on a dead source

def _install_fakes(monkeypatch, uploads_result, measured=None):
    """Put fake `uploads` and `olc` modules where cmd_measure will find them."""
    fake_uploads = types.ModuleType("uploads")
    fake_uploads.list_uploads = lambda cid, limit: uploads_result
    fake_olc = types.ModuleType("olc")
    fake_olc.tek = lambda url, workdir, flag: (measured or {"olcum": {}})
    monkeypatch.setitem(sys.modules, "uploads", fake_uploads)
    monkeypatch.setitem(sys.modules, "olc", fake_olc)


def test_brain_stops_when_listing_fails(monkeypatch, tmp_path):
    import beyin
    monkeypatch.chdir(tmp_path)
    _install_fakes(monkeypatch, ([], "API: HTTP 403 | RSS: HTTP 404", None))
    channel = sorted(beyin.CHANNELS)[0]
    with pytest.raises(SystemExit) as exc:
        beyin.cmd_measure(channel, limit=5)
    message = str(exc.value)
    assert "DUR" in message and "403" in message
    assert not os.path.exists(beyin.ledger_path(channel)), \
        "kaynak olukken deftere dokunulmamali"


def test_brain_holds_fresh_videos_without_writing(monkeypatch, tmp_path):
    import beyin
    monkeypatch.chdir(tmp_path)
    fresh = beyin.now_iso() if hasattr(beyin, "now_iso") else None
    assert fresh, "now_iso bekleniyordu"
    rows = [{"video_id": "fresh1", "baslik": "b", "tarih": fresh[:10],
             "yayin_ts": fresh, "rss_izlenme": None}]
    _install_fakes(monkeypatch, (rows, None, "api"))
    channel = sorted(beyin.CHANNELS)[0]
    beyin.cmd_measure(channel, limit=5)
    assert not os.path.exists(beyin.ledger_path(channel)), \
        "24 saatten taze video olculmemeli"


# -------------------------------------------------------------- stats_for

def fake_videos_api(pages, calls=None):
    queue = list(pages)

    def _get(resource, params, timeout=None, attempts=3):
        if calls is not None:
            calls.append(dict(params))
        if not queue:
            return {"items": []}, None
        nxt = queue.pop(0)
        if isinstance(nxt, str):
            return None, nxt
        return nxt, None

    return _get


def stat_item(video_id, views, likes=None, duration=None):
    numbers = {"viewCount": str(views)}
    if likes is not None:
        numbers["likeCount"] = str(likes)
    body = {"id": video_id, "statistics": numbers}
    if duration:
        body["contentDetails"] = {"duration": duration}
    return body


def test_stats_for_empty_input_is_not_an_error():
    stats, error = uploads.stats_for([])
    assert stats == {} and error is None


def test_stats_for_reads_counts_and_duration(monkeypatch):
    monkeypatch.setattr(uploads, "_api_get", fake_videos_api(
        [{"items": [stat_item("a", 1234, 56, "PT1M23S")]}]))
    stats, error = uploads.stats_for(["a"], key="k")
    assert error is None
    assert stats == {"a": {"izlenme": 1234, "begeni": 56, "sure_sn": 83}}


def test_stats_for_batches_fifty_at_a_time(monkeypatch):
    calls = []
    ids = ["v%03d" % i for i in range(120)]
    monkeypatch.setattr(uploads, "_api_get", fake_videos_api([
        {"items": [stat_item(v, 1) for v in ids[0:50]]},
        {"items": [stat_item(v, 1) for v in ids[50:100]]},
        {"items": [stat_item(v, 1) for v in ids[100:120]]},
    ], calls=calls))
    stats, error = uploads.stats_for(ids, key="k")
    assert error is None and len(stats) == 120
    assert len(calls) == 3
    assert len(calls[0]["id"].split(",")) == 50
    assert len(calls[2]["id"].split(",")) == 20


def test_stats_for_deduplicates_ids(monkeypatch):
    calls = []
    monkeypatch.setattr(uploads, "_api_get", fake_videos_api(
        [{"items": [stat_item("a", 5)]}], calls=calls))
    uploads.stats_for(["a", "a", "a", ""], key="k")
    assert calls[0]["id"] == "a"


def test_stats_for_omits_videos_the_api_did_not_answer_for(monkeypatch):
    # Asked for two, told about one. The missing one must be ABSENT, not zero:
    # a zero would be written into the ledger as a real measurement.
    monkeypatch.setattr(uploads, "_api_get", fake_videos_api(
        [{"items": [stat_item("a", 10)]}]))
    stats, error = uploads.stats_for(["a", "gone"], key="k")
    assert error is None
    assert "gone" not in stats and stats["a"]["izlenme"] == 10


def test_stats_for_skips_items_with_hidden_counts(monkeypatch):
    hidden = {"id": "h", "statistics": {"likeCount": "3"}}
    monkeypatch.setattr(uploads, "_api_get", fake_videos_api(
        [{"items": [hidden, stat_item("a", 7)]}]))
    stats, _ = uploads.stats_for(["h", "a"], key="k")
    assert "h" not in stats and "a" in stats


def test_stats_for_returns_partial_results_with_the_error(monkeypatch):
    ids = ["v%03d" % i for i in range(60)]
    monkeypatch.setattr(uploads, "_api_get", fake_videos_api([
        {"items": [stat_item(v, 1) for v in ids[0:50]]},
        "HTTP 403 quotaExceeded",
    ]))
    stats, error = uploads.stats_for(ids, key="k")
    assert "403" in error
    assert len(stats) == 50, "ilk sayfanin sonucu atilmamali"


def test_stats_for_without_key_is_an_error(monkeypatch):
    monkeypatch.setattr(uploads, "api_key", lambda: "")
    stats, error = uploads.stats_for(["a"])
    assert stats == {} and error


@pytest.mark.parametrize("text,expected", [
    ("PT15S", 15),
    ("PT1M23S", 83),
    ("PT2H", 7200),
    ("PT1H2M3S", 3723),
    ("PT0S", 0),
    ("P1D", None),          # days are not handled; say so rather than guess
    ("PT1M23", None),       # trailing number with no unit
    ("", None),
    (None, None),
    ("garbage", None),
    # Without the PT prefix check these parse from character 2 onward and
    # return a plausible-looking number for input that is not a duration at
    # all - a silent wrong answer, which is worse than None.
    ("1M23S", None),
    ("XT15S", None),
    ("PPT15S", None),
])
def test_parse_duration(text, expected):
    assert uploads.parse_iso8601_duration(text) == expected


# ------------------------------------------------- zero is a measurement

def _install_collect_fakes(monkeypatch, batch, batch_error=None, page=None):
    fake_uploads = types.ModuleType("uploads")
    fake_uploads.stats_for = lambda ids: (batch, batch_error)
    fake_kanal = types.ModuleType("kanal")
    fake_kanal.youtube_canli = lambda vid: (page or {}).get(vid, {})
    monkeypatch.setitem(sys.modules, "uploads", fake_uploads)
    monkeypatch.setitem(sys.modules, "kanal", fake_kanal)


def _seed_ledger(beyin, channel, video_ids):
    beyin.write_ledger(channel, [
        {"video_id": v, "kanal": channel, "tarih": "2026-08-24",
         "yayin_ts": "2026-08-24T10:00:00+00:00", "baslik": v,
         "olcum": {}, "sonuc": {"izlenme": None, "gecmis": []}}
        for v in video_ids])


def test_collect_records_a_genuine_zero(monkeypatch, tmp_path):
    # flashpoints 6GgIn4roshE: public, 18 days old, 0 views. `if not views`
    # skipped it every run, so the worst-performing video never entered the
    # comparison at all - exactly the video the brain most needs to see.
    import beyin
    monkeypatch.chdir(tmp_path)
    channel = sorted(beyin.CHANNELS)[0]
    _seed_ledger(beyin, channel, ["zero", "some"])
    _install_collect_fakes(monkeypatch, {
        "zero": {"izlenme": 0, "begeni": 0},
        "some": {"izlenme": 42},
    })
    beyin.cmd_collect(channel)
    rows, _ = beyin.read_ledger(channel)
    by_id = {r["video_id"]: r for r in rows}
    assert by_id["zero"]["sonuc"]["izlenme"] == 0
    assert len(by_id["zero"]["sonuc"]["gecmis"]) == 1, \
        "sifir izlenme de zaman serisine yazilmali"
    assert by_id["some"]["sonuc"]["izlenme"] == 42


def test_collect_still_skips_a_real_no_reading(monkeypatch, tmp_path):
    # A second, readable row is needed: cmd_collect deliberately stops hard
    # when NOTHING could be read, because that is a network outage rather than
    # a set of unreadable videos.
    import beyin
    monkeypatch.chdir(tmp_path)
    channel = sorted(beyin.CHANNELS)[0]
    _seed_ledger(beyin, channel, ["unknown", "readable"])
    _install_collect_fakes(monkeypatch, {"readable": {"izlenme": 3}})
    beyin.cmd_collect(channel)
    by_id = {r["video_id"]: r for r in beyin.read_ledger(channel)[0]}
    assert by_id["unknown"]["sonuc"]["gecmis"] == [], \
        "okuma yokken uydurma kayit dusulmemeli"
    assert by_id["unknown"]["sonuc"]["izlenme"] is None
    assert by_id["readable"]["sonuc"]["izlenme"] == 3


def test_collect_stops_when_nothing_at_all_could_be_read(monkeypatch, tmp_path):
    import beyin
    monkeypatch.chdir(tmp_path)
    channel = sorted(beyin.CHANNELS)[0]
    _seed_ledger(beyin, channel, ["a", "b"])
    _install_collect_fakes(monkeypatch, {}, batch_error="HTTP 403")
    with pytest.raises(SystemExit) as exc:
        beyin.cmd_collect(channel)
    assert "DUR" in str(exc.value)


def test_collect_falls_back_to_page_scrape(monkeypatch, tmp_path):
    import beyin
    monkeypatch.chdir(tmp_path)
    channel = sorted(beyin.CHANNELS)[0]
    _seed_ledger(beyin, channel, ["only-on-page"])
    _install_collect_fakes(monkeypatch, {}, batch_error="HTTP 403",
                          page={"only-on-page": {"izlenme": 9}})
    beyin.cmd_collect(channel)
    rows, _ = beyin.read_ledger(channel)
    assert rows[0]["sonuc"]["izlenme"] == 9
