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
                        "olcumler": [{"ts": "old", "yas_saat": 168, "youtube": {"views": 7}}],
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


def test_old_part_with_only_50h_measurement_is_measured_once_then_frozen(monkeypatch, tmp_path):
    path = setup_series(
        monkeypatch,
        tmp_path,
        [published_part(age_hours=9 * 24, results={"youtube": "yt1"})],
    )
    path.write_text(
        json.dumps(
            {
                "parts": [
                    {
                        "part": 1,
                        "post_ids": {"youtube": "yt1"},
                        "request_ids": {"youtube": "cached"},
                        "olcumler": [
                            {"ts": "old", "yas_saat": 50, "youtube": {"views": 7}}
                        ],
                        # A file written by the flawed freezer must recover too.
                        "donduruldu": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    calls = []

    def get(url, **kwargs):
        calls.append(url)
        return Response({"platforms": {"youtube": {"post_metrics": {"views": 9}}}})

    result = performans.collect_series_performance(
        "sample", now=NOW, http_get=get, upload_post_api_key="key"
    )
    part = result["parts"][0]
    assert calls == [f"{performans.UPLOAD_POST_ANALYTICS}/cached"]
    assert [measurement["yas_saat"] for measurement in part["olcumler"]] == [50, 216]
    assert part["donduruldu"] is True
    assert part["yargi_anligi"] is None


def test_newest_part_beats_dead_backlog_and_old_part_freezes_after_two_empty_visits(
    monkeypatch, tmp_path
):
    published = [
        published_part(part=number, age_hours=9 * 24)
        for number in range(1, 21)
    ]
    published.append(
        published_part(part=21, age_hours=44, results={"youtube": "yt21"})
    )
    path = setup_series(monkeypatch, tmp_path, published)
    path.write_text(
        json.dumps(
            {
                "parts": [
                    {
                        "part": 21,
                        "post_ids": {"youtube": "yt21"},
                        "request_ids": {"youtube": "fresh-request"},
                        "olcumler": [],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    def get(url, **kwargs):
        if url.endswith("/fresh-request"):
            return Response(
                {"platforms": {"youtube": {"post_metrics": {"views": 123}}}}
            )
        assert url == performans.UPLOAD_POST_ANALYTICS
        return Response({"post": {}})

    first = performans.collect_series_performance(
        "sample", now=NOW, http_get=get, upload_post_api_key="key"
    )
    newest = next(part for part in first["parts"] if part["part"] == 21)
    dead = next(part for part in first["parts"] if part["part"] == 1)
    assert newest["olcumler"][0]["youtube"]["views"] == 123
    assert dead["gec_bos_deneme"] == 1
    assert dead["donduruldu"] is False

    second = performans.collect_series_performance(
        "sample", now=NOW, http_get=get, upload_post_api_key="key"
    )
    dead = next(part for part in second["parts"] if part["part"] == 1)
    assert dead["gec_bos_deneme"] == 2
    assert dead["donduruldu"] is True


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


@pytest.mark.parametrize(
    ("age", "expected"),
    [
        (43.9, set()),
        (44, {"s48"}),
        (96.1, set()),
        (144, {"s7g"}),
        (240.1, {"omur"}),
    ],
)
def test_snapshot_selection_boundaries(age, expected):
    result = performans.score_performance(
        {"parts": [{"part": 1, "olcumler": [{"yas_saat": age, "youtube": {"views": 1}}]}]}
    )
    assert set(result["parts"][0]["anlik"]) == expected


def test_omur_is_kept_even_when_s48_exists():
    result = performans.score_performance(
        {
            "parts": [
                {
                    "part": 1,
                    "olcumler": [
                        {"yas_saat": 48, "youtube": {"views": 1}},
                        {"yas_saat": 240.1, "youtube": {"views": 2}},
                    ],
                }
            ]
        }
    )
    assert set(result["parts"][0]["anlik"]) == {"s48", "omur"}


def test_omur_uses_earliest_measurement_after_240_hours():
    result = performans.score_performance(
        {
            "parts": [
                {
                    "part": 1,
                    "olcumler": [
                        {"yas_saat": 300, "youtube": {"views": 3}},
                        {"yas_saat": 250, "youtube": {"views": 1}},
                        {"yas_saat": 260, "youtube": {"views": 2}},
                    ],
                }
            ]
        }
    )
    assert result["parts"][0]["anlik"]["omur"]["youtube"]["yas_saat"] == 250


def test_measurements_with_early_snapshots_still_get_settled_omur():
    measurements = [
        {"yas_saat": age, "youtube": {"views": views}}
        for age, views in [(20, 1), (44, 2), (68, 3), (260, 4)]
    ]
    result = performans.score_performance(
        {"parts": [{"part": 1, "olcumler": measurements}]}
    )
    snapshots = result["parts"][0]["anlik"]
    assert snapshots["s48"]["youtube"]["yas_saat"] == 44
    assert snapshots["omur"]["youtube"]["yas_saat"] == 260


def test_per_snapshot_medians_are_independent():
    parts = []
    for number, (views_48, views_7d) in enumerate(
        zip([10, 20, 30, 40, 50], [100, 200, 300, 400, 500]), 1
    ):
        parts.append(
            {
                "part": number,
                "olcumler": [
                    {"yas_saat": 48, "youtube": {"views": views_48}},
                    {"yas_saat": 168, "youtube": {"views": views_7d}},
                ],
            }
        )
    result = performans.score_performance({"parts": parts})
    assert result["medyanlar"] == {
        "s48": {"youtube": 30},
        "oturmus": {"youtube": 300},
    }
    assert result["parts"][0]["yargi_anligi"] == "oturmus"


def test_live_wild_encounter_settled_cohort_pools_s7g_and_omur():
    live_rows = [
        (5, 317, 2869, None, 137),
        (6, 308, 3880, 1024, 177),
        (7, 282, 303, 350, 107),
        (8, 258, 6931, 2232, 824),
        (9, 233, 35901, 1746, 583),
        (10, 205, 3158, 911, 428),
    ]
    parts = []
    for number, age, youtube, instagram, tiktok in live_rows:
        measurement = {
            "yas_saat": age,
            "youtube": {"views": youtube},
            "tiktok": {"views": tiktok},
        }
        if instagram is not None:
            measurement["instagram"] = {"views": instagram}
        parts.append({"part": number, "olcumler": [measurement]})

    result = performans.score_performance({"parts": parts})

    assert "youtube" in result["medyanlar"]["oturmus"]
    assert next(part for part in result["parts"] if part["part"] == 9)["etiket"] == "kazanan"
    assert sum(part["yargi_anligi"] == "oturmus" for part in result["parts"]) >= 6


def test_s48_snapshot_is_selected_per_platform_when_a_run_is_partial():
    parts = []
    for number, views in enumerate([10, 20, 30, 40, 50], 1):
        parts.append(
            {
                "part": number,
                "olcumler": [
                    {"yas_saat": 44, "youtube": {"views": views}},
                    {"yas_saat": 68, "tiktok": {"views": views}},
                ],
            }
        )
    result = performans.score_performance({"parts": parts})
    first = result["parts"][0]
    assert result["medyanlar"]["s48"]["tiktok"] == 30
    assert first["anlik"]["s48"]["youtube"]["yas_saat"] == 44
    assert first["anlik"]["s48"]["tiktok"]["yas_saat"] == 68


def test_missing_settled_median_falls_back_to_s48_judgement():
    parts = []
    for number, views in enumerate([300, 100, 100, 100, 100], 1):
        measurements = [{"yas_saat": 48, "youtube": {"views": views}}]
        if number == 1:
            measurements.append({"yas_saat": 168, "youtube": {"views": 999}})
        parts.append({"part": number, "olcumler": measurements})

    result = performans.score_performance({"parts": parts})
    first = result["parts"][0]
    assert "oturmus" not in result["medyanlar"]
    assert first["yargi_anligi"] == "s48"
    assert first["etiket"] == "kazanan"


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
    assert result["medyanlar"] == {"s48": {"youtube": 30}}
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
        age_hours=168,
    )
    assert result["medyanlar"]["oturmus"]["youtube"] == 100
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


def test_7_day_low_ratios_are_losers():
    result = scored_document(
        [{"youtube": 40}, {"youtube": 100}, {"youtube": 100}, {"youtube": 100}, {"youtube": 100}],
        age_hours=168,
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


@pytest.mark.parametrize("age", [168, 250])
def test_loser_is_allowed_only_from_settled_cohort(age):
    result = scored_document(
        [{"youtube": 40}, {"youtube": 100}, {"youtube": 100}, {"youtube": 100}, {"youtube": 100}],
        age_hours=age,
    )
    assert result["parts"][0]["yargi_anligi"] == "oturmus"
    assert result["parts"][0]["etiket"] == "kaybeden"


def test_arbitrary_numeric_metrics_and_retention_are_kept_without_inventing_missing_fields():
    retention = list(range(250))
    cleaned = performans._clean_metrics(
        {
            "views": 12,
            "average_watch_time": 7.5,
            "rewatches": "3",
            "retention_curve": retention,
            "audience_retention": [{"x": "0", "y": 100}, {"x": 1, "y": 80.5}],
            "invalid_retention": [1, "bad"],
        }
    )
    assert cleaned["average_watch_time"] == 7.5
    assert cleaned["rewatches"] == 3
    assert cleaned["retention_curve"] == retention[:200]
    assert cleaned["audience_retention"] == [{"x": 0, "y": 100}, {"x": 1, "y": 80.5}]
    assert "likes" not in cleaned
    assert "invalid_retention" not in cleaned


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
    corrupt = b"{broken"
    path.write_bytes(corrupt)

    result = performans.collect_series_performance(
        "sample", now=NOW, http_get=lambda *a, **k: None, upload_post_api_key="key"
    )
    assert result["series"] == "sample"
    assert result["parts"][0]["part"] == 1
    assert json.loads(path.read_text(encoding="utf-8"))["series"] == "sample"
    backup = tmp_path / "performans.json.bozuk-20260924T120000"
    assert backup.read_bytes() == corrupt


def test_bom_performance_file_loads_without_being_quarantined(monkeypatch, tmp_path):
    path = setup_series(monkeypatch, tmp_path, [])
    path.write_text(
        json.dumps(
            {
                "series": "sample",
                "parts": [
                    {
                        "part": 7,
                        "yayin_zamani": (NOW - timedelta(hours=50)).isoformat(),
                        "olcumler": [
                            {"yas_saat": 50, "youtube": {"views": 77}}
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8-sig",
    )

    result = performans.collect_series_performance(
        "sample", now=NOW, http_get=lambda *a, **k: None, upload_post_api_key="key"
    )

    assert result["parts"][0]["part"] == 7
    assert result["parts"][0]["olcumler"][0]["youtube"]["views"] == 77
    assert list(tmp_path.glob("performans.json.bozuk-*")) == []


def test_old_flat_medians_file_loads_without_crashing(monkeypatch, tmp_path):
    path = setup_series(
        monkeypatch,
        tmp_path,
        [published_part(results={})],
    )
    path.write_text(
        json.dumps(
            {
                "series": "sample",
                "medyanlar": {"youtube": 100},
                "parts": [{"part": 1, "olcumler": [{"yas_saat": 50, "youtube": {"views": 10}}]}],
            }
        ),
        encoding="utf-8",
    )
    result = performans.collect_series_performance(
        "sample", now=NOW, http_get=lambda *a, **k: None, upload_post_api_key="key"
    )
    assert result["medyanlar"] == {}
    assert result["parts"][0]["yargi_anligi"] is None


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
