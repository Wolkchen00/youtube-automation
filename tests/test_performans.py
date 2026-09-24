import json
from datetime import datetime, timedelta, timezone

import pytest

from series import performans


NOW = datetime(2026, 9, 24, 12, 0, tzinfo=timezone.utc)


class Response:
    def __init__(self, payload, status=200):
        self.payload = payload
        self.status_code = status

    def json(self):
        return self.payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class Meta:
    upload_profile = "profile"


def setup_series(monkeypatch, tmp_path, published):
    (tmp_path / "series.json").write_text("{}", encoding="utf-8")
    (tmp_path / "published.json").write_text(
        json.dumps(published), encoding="utf-8"
    )
    monkeypatch.setattr(performans, "data_dir", lambda slug: tmp_path)
    monkeypatch.setattr(performans.SeriesMeta, "load", classmethod(lambda cls, slug: Meta()))
    return tmp_path / "performans.json"


def published_part(part=1, age_hours=50, results=None):
    if results is None:
        results = {"youtube": f"yt{part}", "instagram": f"ig{part}", "tiktok": f"tt{part}"}
    return {
        "part": part,
        "subtitle": f"Part {part}",
        "ts": (NOW - timedelta(hours=age_hours)).isoformat(),
        "results": results,
    }


def upload_post_get(url, **kwargs):
    if url == performans.UPLOAD_POST_ANALYTICS:
        platform = kwargs["params"]["platform"]
        post_id = kwargs["params"]["platform_post_id"]
        return Response({"success": True, "post": {"request_id": f"req-{platform}-{post_id}"}})
    platform = url.split("req-", 1)[1].split("-", 1)[0]
    return Response(
        {
            "success": True,
            "platforms": {platform: {"post_metrics": {"views": 100, "likes": 4}}},
        }
    )


def test_under_44_hours_is_recorded_but_unscored(monkeypatch, tmp_path):
    path = setup_series(monkeypatch, tmp_path, [published_part(age_hours=20)])

    result = performans.collect_series_performance(
        "sample", now=NOW, http_get=upload_post_get, upload_post_api_key="key"
    )

    assert path.exists()
    assert result["parts"][0]["olcumler"][0]["yas_saat"] == 20
    assert result["parts"][0]["etiket"] == "olculmemis"
    assert result["parts"][0]["puan"] is None


def test_old_measured_part_is_frozen_and_not_requested(monkeypatch, tmp_path):
    path = setup_series(monkeypatch, tmp_path, [published_part(age_hours=9 * 24)])
    path.write_text(
        json.dumps(
            {
                "series": "sample",
                "parts": [
                    {
                        "part": 1,
                        "post_ids": {"youtube": "yt1"},
                        "request_ids": {"youtube": "cached"},
                        "olcumler": [{"ts": "old", "yas_saat": 50, "youtube": {"views": 7}}],
                        "donduruldu": False,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    def no_network(*args, **kwargs):
        raise AssertionError("frozen part must not use the network")

    result = performans.collect_series_performance(
        "sample", now=NOW, http_get=no_network, upload_post_api_key="key"
    )
    assert result["parts"][0]["donduruldu"] is True
    assert result["api_cagrilari"] == 0


def test_cached_request_id_is_not_looked_up_again(monkeypatch, tmp_path):
    path = setup_series(
        monkeypatch,
        tmp_path,
        [published_part(results={"youtube": "yt1"})],
    )
    path.write_text(
        json.dumps(
            {
                "parts": [
                    {
                        "part": 1,
                        "post_ids": {"youtube": "yt1"},
                        "request_ids": {"youtube": "cached-request"},
                        "olcumler": [],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    urls = []

    def get(url, **kwargs):
        urls.append(url)
        return Response({"platforms": {"youtube": {"post_metrics": {"views": 12}}}})

    result = performans.collect_series_performance(
        "sample", now=NOW, http_get=get, upload_post_api_key="key"
    )
    assert urls == [f"{performans.UPLOAD_POST_ANALYTICS}/cached-request"]
    assert result["parts"][0]["request_ids"]["youtube"] == "cached-request"


def test_429_stops_and_writes_partial_result(monkeypatch, tmp_path):
    path = setup_series(monkeypatch, tmp_path, [published_part()])
    calls = 0

    def get(url, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            return Response({"post": {"request_id": "youtube-request"}})
        if calls == 2:
            return Response({"platforms": {"youtube": {"post_metrics": {"views": 44}}}})
        return Response({}, status=429)

    result = performans.collect_series_performance(
        "sample", now=NOW, http_get=get, upload_post_api_key="key"
    )
    on_disk = json.loads(path.read_text(encoding="utf-8"))
    assert calls == 3
    assert result["api_cagrilari"] == 3
    assert on_disk["parts"][0]["olcumler"][0]["youtube"]["views"] == 44


def test_missing_upload_key_exits_zero_with_warning(monkeypatch, tmp_path):
    setup_series(monkeypatch, tmp_path, [published_part()])
    monkeypatch.setattr(performans, "UPLOAD_POST_API_KEY", "")
    warnings = []
    monkeypatch.setattr(performans.logger, "warning", lambda message, *args: warnings.append(message % args))

    assert performans.main(["--series", "sample"]) == 0
    assert any("UPLOAD_POST_API_KEY eksik" in message for message in warnings)


@pytest.mark.parametrize("results", [None, {}, {"youtube": None}, "old-shape"])
def test_null_absent_and_non_dict_platform_ids_are_tolerated(monkeypatch, tmp_path, results):
    entry = published_part(results={})
    entry["results"] = results
    setup_series(monkeypatch, tmp_path, [entry])

    def no_network(*args, **kwargs):
        raise AssertionError("missing post IDs must not use the network")

    result = performans.collect_series_performance(
        "sample", now=NOW, http_get=no_network, upload_post_api_key="key"
    )
    assert result["parts"][0]["post_ids"] == {}
    assert result["api_cagrilari"] == 0


def scored_document(view_rows, age_hours=50):
    parts = []
    for number, row in enumerate(view_rows, 1):
        measurement = {"ts": "x", "yas_saat": age_hours}
        for platform, views in row.items():
            measurement[platform] = {"views": views}
        parts.append({"part": number, "olcumler": [measurement]})
    return performans.score_performance({"parts": parts})


def test_each_platform_needs_five_measured_parts_for_a_median():
    result = scored_document(
        [
            {"youtube": 10, "instagram": 10},
            {"youtube": 20, "instagram": 20},
            {"youtube": 30, "instagram": 30},
            {"youtube": 40, "instagram": 40},
            {"youtube": 50},
        ]
    )
    assert result["medyanlar"] == {"youtube": 30}
    assert "instagram" not in result["parts"][0]["oranlar"]


def test_series_relative_labels_cover_winner_loser_and_middle():
    result = scored_document(
        [
            {"youtube": 200},
            {"youtube": 50},
            {"youtube": 100},
            {"youtube": 100},
            {"youtube": 100},
        ],
        age_hours=100,
    )
    assert result["medyanlar"]["youtube"] == 100
    assert [part["etiket"] for part in result["parts"][:3]] == [
        "kazanan",
        "kaybeden",
        "orta",
    ]


def test_50_hour_low_ratios_stay_middle_with_early_note():
    result = scored_document(
        [{"youtube": 40}, {"youtube": 100}, {"youtube": 100}, {"youtube": 100}, {"youtube": 100}],
        age_hours=50,
    )
    assert result["parts"][0]["etiket"] == "orta"
    assert result["parts"][0]["etiket_notu"] == "kaybeden icin erken"


def test_100_hour_low_ratios_are_losers():
    result = scored_document(
        [{"youtube": 40}, {"youtube": 100}, {"youtube": 100}, {"youtube": 100}, {"youtube": 100}],
        age_hours=100,
    )
    assert result["parts"][0]["etiket"] == "kaybeden"
    assert "etiket_notu" not in result["parts"][0]


def test_50_hour_ratio_three_is_still_a_winner():
    result = scored_document(
        [{"youtube": 300}, {"youtube": 100}, {"youtube": 100}, {"youtube": 100}, {"youtube": 100}],
        age_hours=50,
    )
    assert result["parts"][0]["oranlar"]["youtube"] == 3
    assert result["parts"][0]["etiket"] == "kazanan"
    assert "etiket_notu" not in result["parts"][0]


def test_youtube_data_api_fallback_when_upload_post_has_no_metrics(monkeypatch, tmp_path):
    setup_series(
        monkeypatch,
        tmp_path,
        [published_part(results={"youtube": "yt1"})],
    )
    calls = []

    def get(url, **kwargs):
        calls.append((url, kwargs.get("params")))
        if url == performans.UPLOAD_POST_ANALYTICS:
            return Response({"post": {"request_id": "request-1"}})
        if url.endswith("/request-1"):
            return Response({"platforms": {"youtube": {"success": True}}})
        assert url == performans.YOUTUBE_VIDEOS
        return Response({"items": [{"id": "yt1", "statistics": {"viewCount": "321"}}]})

    result = performans.collect_series_performance(
        "sample",
        now=NOW,
        http_get=get,
        upload_post_api_key="key",
        youtube_api_key="youtube-key",
    )
    assert len(calls) == 3
    assert calls[-1][1]["id"] == "yt1"
    assert result["parts"][0]["olcumler"][0]["youtube"]["views"] == 321


def test_corrupt_existing_file_starts_fresh(monkeypatch, tmp_path):
    path = setup_series(
        monkeypatch,
        tmp_path,
        [published_part(results={})],
    )
    path.write_text("{broken", encoding="utf-8")

    result = performans.collect_series_performance(
        "sample", now=NOW, http_get=lambda *a, **k: None, upload_post_api_key="key"
    )
    assert result["series"] == "sample"
    assert result["parts"][0]["part"] == 1
    assert json.loads(path.read_text(encoding="utf-8"))["series"] == "sample"


def test_api_call_budget_never_exceeds_sixty(monkeypatch, tmp_path):
    entries = [
        published_part(part=number, results={"instagram": f"ig{number}"})
        for number in range(1, 32)
    ]
    setup_series(monkeypatch, tmp_path, entries)
    calls = 0

    def get(url, **kwargs):
        nonlocal calls
        calls += 1
        if url == performans.UPLOAD_POST_ANALYTICS:
            return Response({"post": {"request_id": f"request-{calls}"}})
        return Response({"platforms": {"instagram": {"post_metrics": {"views": 10}}}})

    result = performans.collect_series_performance(
        "sample", now=NOW, http_get=get, upload_post_api_key="key"
    )
    assert calls == performans.MAX_API_CALLS == 60
    assert result["api_cagrilari"] == 60
    assert len(result["parts"][29]["olcumler"]) == 1
    assert result["parts"][30]["olcumler"] == []


def test_atomic_write_falls_back_when_replace_is_blocked(monkeypatch, tmp_path):
    path = tmp_path / "performans.json"
    monkeypatch.setattr(
        performans.os,
        "replace",
        lambda source, target: (_ for _ in ()).throw(PermissionError("blocked")),
    )

    performans._atomic_write_json(path, {"ok": True})

    assert json.loads(path.read_text(encoding="utf-8")) == {"ok": True}
    assert list(tmp_path.glob("performans.json.tmp-*")) == []


def test_dry_run_never_uses_network_or_writes(monkeypatch, tmp_path, capsys):
    path = setup_series(monkeypatch, tmp_path, [published_part()])
    path.write_text(json.dumps(scored_document([{"youtube": 10}] * 5)), encoding="utf-8")
    before = path.read_bytes()
    monkeypatch.setattr(
        performans.requests,
        "get",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("network used")),
    )

    assert performans.main(["--series", "sample", "--dry"]) == 0
    assert path.read_bytes() == before
    assert "part\tyas\tyoutube" in capsys.readouterr().out


def test_dry_run_reports_missing_performance_file(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(performans, "data_dir", lambda slug: tmp_path)

    assert performans.main(["--series", "sample", "--dry"]) == 0
    assert capsys.readouterr().out.strip() == f"performans.json yok: {tmp_path / 'performans.json'}"
