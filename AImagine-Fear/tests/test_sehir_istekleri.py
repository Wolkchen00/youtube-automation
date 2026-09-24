from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tools import sehir_istekleri as mod


NOW = datetime(2026, 9, 24, 12, tzinfo=timezone.utc)


class Response:
    def __init__(self, payload, status=200):
        self.payload = payload
        self.status_code = status

    def json(self):
        return self.payload


def _row(ts, *, used=True, results=None):
    return {
        "ts_utc": ts.isoformat(),
        "kullanildi": used,
        "results": results or {},
    }


def _comment(comment_id, text, username="user", timestamp="2026-09-23T23:17:46+0000"):
    return {
        "id": comment_id,
        "text": text,
        "timestamp": timestamp,
        "username": username,
    }


def _page(comments=(), cursor=None):
    return {
        "success": True,
        "comments": list(comments),
        "pagination": {"has_next": cursor is not None, "next_cursor": cursor},
    }


def _isolated_run(monkeypatch, tmp_path: Path, rows):
    ledger = tmp_path / "yayin.jsonl"
    ledger.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    interaction = tmp_path / "ETKILESIM.json"
    interaction.write_text(
        json.dumps(
            {
                "kendi_hesaplar": ["aimagine357", "aimagine_._", "@aimagine_._"],
                "first_comments": ["OWN FIRST COMMENT"],
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "sehir_istekleri.json"
    monkeypatch.setattr(mod, "DEFTER", ledger)
    monkeypatch.setattr(mod, "ETKILESIM", interaction)
    monkeypatch.setattr(mod, "CIKTI", output)
    monkeypatch.setattr(mod, "UPLOAD_POST_API_KEY", "upload-key")
    monkeypatch.setattr(mod, "GEMINI_API_KEY", "gemini-key")
    monkeypatch.setattr(mod, "UPLOAD_USERS", {"aimagine": "profile"})
    return output


def test_ledger_extracts_both_id_shapes_and_skips_old_unverified(tmp_path):
    recent = NOW - timedelta(days=1)
    rows = [
        _row(
            recent,
            results={
                "youtube": {"results": {"youtube": {"post_id": "old-shape"}}},
                "instagram": {"results": [{"platform_post_id": "ig-id"}]},
            },
        ),
        _row(
            recent,
            results={"youtube": {"results": [{"platform_post_id": "new-shape"}]}},
        ),
        _row(recent, used=False, results={"youtube": {"post_id": "unverified"}}),
        _row(NOW - timedelta(days=15), results={"youtube": {"post_id": "too-old"}}),
    ]
    path = tmp_path / "yayin.jsonl"
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    assert mod.yayin_postlari(path, 14, NOW) == [
        ("instagram", "ig-id"),
        ("youtube", "old-shape"),
        ("youtube", "new-shape"),
    ]


def test_url_fallback_only_for_derivable_platform_ids():
    assert mod.post_id_cikar("youtube", {"post_url": "https://youtube.com/watch?v=abc123"}) == "abc123"
    assert mod.post_id_cikar("tiktok", {"post_url": "https://tiktok.com/@a/video/7688063708911734029"}) == "7688063708911734029"
    assert mod.post_id_cikar("instagram", {"post_url": "https://instagram.com/reel/SHORT/"}) is None


def test_own_accounts_and_exact_first_comments_are_excluded():
    comments = [
        _comment("1", "Tokyo", "@AIMAGINE_._"),
        _comment("2", "OWN FIRST COMMENT", "viewer"),
        _comment("3", "OWN FIRST COMMENT ", "viewer"),
        {"id": "4", "text": "Paris", "user": {"username": "Other"}},
    ]
    prepared = mod.yorumlari_hazirla(
        comments,
        {"aimagine357", "aimagine_._"},
        {"OWN FIRST COMMENT"},
    )
    assert [item["comment_id"] for item in prepared] == ["3", "4"]


def test_comments_are_newest_first_capped_and_truncated_for_gemini():
    comments = [
        _comment(
            str(index),
            "x" * 350,
            timestamp=(NOW - timedelta(seconds=index)).isoformat(),
        )
        for index in reversed(range(401))
    ]
    prepared = mod.yorumlari_hazirla(comments, set(), set())
    assert len(prepared) == 400
    assert prepared[0]["comment_id"] == "0"
    assert prepared[-1]["comment_id"] == "399"
    assert all(len(item["gemini_text"]) == 300 for item in prepared)


def test_pagination_uses_after_and_stops_after_five_pages():
    calls = []

    def get(_url, **kwargs):
        calls.append(kwargs["params"].copy())
        page = len(calls)
        return Response(_page([_comment(str(page), "Tokyo")], "c%d" % page))

    comments, call_count = mod.yorumlari_topla(
        [("instagram", "post")], "profile", "key", get=get
    )
    assert call_count == 5
    assert len(comments) == 5
    assert calls[0].get("after") is None
    assert calls[1]["after"] == "c1"
    assert all("cursor" not in params for params in calls)


def test_pagination_stops_when_page_has_zero_new_comment_ids():
    calls = []

    def get(_url, **kwargs):
        calls.append(kwargs["params"].copy())
        return Response(_page([_comment("same", "Tokyo")], "next"))

    comments, call_count = mod.yorumlari_topla(
        [("instagram", "post")], "profile", "key", get=get
    )
    assert call_count == 2
    assert len(comments) == 1
    assert calls[1]["after"] == "next"


def test_tiktok_reconnect_skips_rest_of_tiktok_but_keeps_other_platforms():
    calls = []

    def get(_url, **kwargs):
        platform = kwargs["params"]["platform"]
        calls.append((platform, kwargs["params"]["post_id"]))
        if platform == "tiktok":
            return Response({"error_code": "tiktok_reconnect_required"}, 400)
        return Response(_page([_comment("yt", "Paris")]))

    comments, _ = mod.yorumlari_topla(
        [("tiktok", "tt1"), ("tiktok", "tt2"), ("youtube", "yt1")],
        "profile",
        "key",
        get=get,
    )
    assert calls == [("tiktok", "tt1"), ("youtube", "yt1")]
    assert comments[0]["_platform"] == "youtube"


def test_unique_users_platforms_unknown_ids_and_var_flag_from_sehirler(tmp_path):
    comments = [
        {"comment_id": "1", "text": "Tokyo please", "identity": "same", "platform": "instagram"},
        {"comment_id": "2", "text": "Tokyo again", "identity": "same", "platform": "instagram"},
        {"comment_id": "3", "text": "Tokyo!", "identity": "same", "platform": "youtube"},
        {"comment_id": "4", "text": "Tokyo no name", "identity": "", "platform": "youtube"},
    ]
    extracted = [
        {"comment_id": item["comment_id"], "city": "Tokyo", "landmark": None}
        for item in comments
    ] + [{"comment_id": "unknown", "city": "Paris", "landmark": None}]
    result = mod.sonucu_kur(
        comments,
        extracted,
        14,
        2,
        4,
        NOW,
        # Bos rota klasorunde Tokyo yalniz sehir_ekle.SEHIRLER kaynagindan gelir.
        route_names=mod.mevcut_rota_adlari(tmp_path),
    )
    assert result["sehirler"] == [
        {
            "sehir": "Tokyo",
            "kullanici_sayisi": 3,
            "yorum_sayisi": 4,
            "ornek_yorumlar": ["Tokyo please", "Tokyo again", "Tokyo!"],
            "var": True,
        }
    ]
    assert result["kimlik_notu"] == "Instagram yorumcu adini vermiyor; Instagram'da her yorum ayri kisi sayilir."


def test_instagram_null_user_counts_each_comment_as_a_person():
    raw = [
        {"id": "ig-1", "text": "Tokyo", "user": {"id": None, "username": None}, "_platform": "instagram"},
        {"id": "ig-2", "text": "Tokyo too", "user": {"id": None, "username": None}, "_platform": "instagram"},
    ]
    comments = mod.yorumlari_hazirla(raw, set(), set())
    extracted = [
        {"comment_id": item["comment_id"], "city": "Tokyo", "landmark": None}
        for item in comments
    ]
    city = mod.sonucu_kur(comments, extracted, 14, 1, 2, NOW, route_names=(set(), []))["sehirler"][0]
    assert [item["identity"] for item in comments] == ["", ""]
    assert city["kullanici_sayisi"] == 2
    assert city["yorum_sayisi"] == 2


def test_youtube_author_channel_id_deduplicates_before_author_name():
    raw = [
        {"id": "yt-1", "text": "Paris", "author": "@old-handle", "author_channel_id": "UC123", "_platform": "youtube"},
        {"id": "yt-2", "text": "Paris again", "author": "@new-handle", "author_channel_id": "UC123", "_platform": "youtube"},
    ]
    comments = mod.yorumlari_hazirla(raw, set(), set())
    extracted = [
        {"comment_id": item["comment_id"], "city": "Paris", "landmark": None}
        for item in comments
    ]
    city = mod.sonucu_kur(comments, extracted, 14, 1, 2, NOW, route_names=(set(), []))["sehirler"][0]
    assert [item["identity"] for item in comments] == ["UC123", "UC123"]
    assert city["kullanici_sayisi"] == 1
    assert city["yorum_sayisi"] == 2


def test_invalid_gemini_json_leaves_existing_file_untouched(monkeypatch, tmp_path):
    row = _row(NOW, results={"youtube": {"post_id": "yt"}})
    output = _isolated_run(monkeypatch, tmp_path, [row])
    output.write_text('{"old": true}\n', encoding="utf-8")

    def get(*_args, **_kwargs):
        return Response(_page([_comment("1", "Tokyo")]))

    class Models:
        def generate_content(self, **_kwargs):
            return type("GeminiResponse", (), {"text": "{invalid"})()

    class Client:
        models = Models()

    from google import genai

    monkeypatch.setattr(genai, "Client", lambda **_kwargs: Client())
    assert mod.calistir(now=NOW, get=get) is None
    assert output.read_text(encoding="utf-8") == '{"old": true}\n'


def test_run_counts_filters_sorts_and_writes_atomically(monkeypatch, tmp_path):
    row = _row(
        NOW,
        results={
            "instagram": {"platform_post_id": "ig"},
            "youtube": {"post_id": "yt"},
        },
    )
    output = _isolated_run(monkeypatch, tmp_path, [row])

    def get(_url, **kwargs):
        platform = kwargs["params"]["platform"]
        if platform == "instagram":
            return Response(_page([_comment("1", "Tokyo", "one"), _comment("2", "OWN FIRST COMMENT", "x")]))
        return Response(_page([_comment("3", "Paris", "two")]))

    def extractor(comments, key):
        assert key == "gemini-key"
        assert [comment["comment_id"] for comment in comments] == ["1", "3"]
        return [
            {"comment_id": "1", "city": "Tokyo", "landmark": None},
            {"comment_id": "3", "city": "Paris", "landmark": None},
        ]

    result = mod.calistir(now=NOW, get=get, extractor=extractor)
    assert result["kaynak_post_sayisi"] == 2
    assert result["yorum_sayisi"] == 3
    assert result["sayilan_yorum"] == 2
    assert json.loads(output.read_text(encoding="utf-8")) == result


def test_empty_prepared_comments_write_empty_result_without_gemini(monkeypatch, tmp_path):
    row = _row(NOW, results={"youtube": {"post_id": "yt"}})
    output = _isolated_run(monkeypatch, tmp_path, [row])

    def get(*_args, **_kwargs):
        return Response(_page([_comment("1", "OWN FIRST COMMENT", "viewer")]))

    def extractor(*_args, **_kwargs):
        raise AssertionError("Gemini must not be called")

    result = mod.calistir(now=NOW, get=get, extractor=extractor)
    assert result["sayilan_yorum"] == 0
    assert result["sehirler"] == []
    assert json.loads(output.read_text(encoding="utf-8")) == result


def test_missing_upload_key_exits_zero_without_network(monkeypatch):
    monkeypatch.setattr(mod, "UPLOAD_POST_API_KEY", "")
    monkeypatch.setattr(mod, "CIKTI", Path("must-not-exist"))
    monkeypatch.setattr(mod.requests, "get", lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("network")))
    assert mod.main([]) == 0


def test_missing_gemini_key_exits_zero_without_network(monkeypatch):
    monkeypatch.setattr(mod, "UPLOAD_POST_API_KEY", "upload-key")
    monkeypatch.setattr(mod, "GEMINI_API_KEY", "")
    monkeypatch.setattr(mod.requests, "get", lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("network")))
    assert mod.main([]) == 0


def test_invalid_cli_argument_does_not_raise():
    assert mod.main(["--gun", "not-a-number"]) == 0


def test_http_budget_never_exceeds_eighty():
    calls = 0

    def get(_url, **_kwargs):
        nonlocal calls
        calls += 1
        return Response(_page([_comment(str(calls), "Tokyo")], "more"))

    posts = [("youtube", "post-%d" % index) for index in range(30)]
    _, call_count = mod.yorumlari_topla(posts, "profile", "key", get=get)
    assert calls == call_count == 80


def test_short_city_name_does_not_use_filename_substring_match():
    stems = ["newyorkempire", "riocristokobalt", "tokyoskytree"]
    assert mod._rota_var("York", (set(), stems)) is False
    assert mod._rota_var("Rio", (set(), stems)) is False
    assert mod._rota_var("Tokyo", (set(), stems)) is True
    assert mod._rota_var("Rio", ({"rio"}, stems)) is True


def test_429_stops_fetching_but_writes_from_collected_comments(monkeypatch, tmp_path):
    rows = [
        _row(NOW, results={"instagram": {"platform_post_id": "ig"}, "youtube": {"post_id": "yt"}})
    ]
    output = _isolated_run(monkeypatch, tmp_path, rows)
    calls = 0

    def get(_url, **_kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            return Response(_page([_comment("1", "Tokyo")]))
        return Response({}, 429)

    result = mod.calistir(
        now=NOW,
        get=get,
        extractor=lambda comments, _key: [
            {"comment_id": comments[0]["comment_id"], "city": "Tokyo", "landmark": None}
        ],
    )
    assert calls == 2
    assert result["sehirler"][0]["sehir"] == "Tokyo"
    assert output.exists()


def test_dry_run_prints_current_file_without_network(monkeypatch, tmp_path, capsys):
    output = tmp_path / "sehir_istekleri.json"
    output.write_text('{"current": true}\n', encoding="utf-8")
    monkeypatch.setattr(mod, "CIKTI", output)
    monkeypatch.setattr(mod.requests, "get", lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("network")))
    assert mod.main(["--dry"]) == 0
    assert capsys.readouterr().out == '{"current": true}\n'


def test_workflow_has_secret_counter_order_and_persist_path():
    workflow = (mod.YT_KOK / ".github" / "workflows" / "fear-slide.yml").read_text(encoding="utf-8")
    assert "GEMINI_API_KEY=${{ secrets.GEMINI_API_KEY }}" in workflow
    counter = "python -X utf8 AImagine-Fear/tools/sehir_istekleri.py"
    assert workflow.index("python -X utf8 AImagine-Fear/tools/gunluk.py") < workflow.index(counter)
    assert workflow.index(counter) < workflow.index("Uretim sonucunu kaydet")
    assert "continue-on-error: true" in workflow[workflow.index("Sehir isteklerini say"):workflow.index(counter)]
    assert "AImagine-Fear/veri/sehir_istekleri.json" in workflow
