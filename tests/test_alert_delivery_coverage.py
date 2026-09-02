"""ROCK 2: operasyon alarmlarının Markdown'a geri dönmesini engelleyen kanıtlar."""

from __future__ import annotations

import ast
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from core import narration
from series import approver, critic, notifier, produce, replenish, series_runner
from series.bible import Bible


ROOT = Path(__file__).resolve().parents[1]
LIVE_ENTITY_ERROR = (
    "Bad Request: can't parse entities: Can't find end of the entity "
    "starting at byte offset 93"
)


class _Response:
    def __init__(self, payload: dict, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code

    def json(self) -> dict:
        return self._payload


@pytest.fixture(autouse=True)
def _isolated_alert_delivery(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token-never-log")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "test-chat-never-log")
    monkeypatch.setattr(
        notifier,
        "alert_outbox_path",
        lambda slug: tmp_path / slug / "alert_outbox.json",
    )
    series_runner._FAILED_ALERT_SLUGS.clear()
    yield
    series_runner._FAILED_ALERT_SLUGS.clear()


def _outbox(slug: str) -> list[dict]:
    path = notifier.alert_outbox_path(slug)
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def _enclosing_function(node: ast.AST, parents: dict[ast.AST, ast.AST]) -> str:
    parent = parents.get(node)
    while parent is not None:
        if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return parent.name
        parent = parents.get(parent)
    return "<module>"


def test_only_explicit_presentation_sites_may_call_markdown_send_message():
    """Yeni bir operasyon alarmı varsayılan Markdown yoluna sessizce eklenemesin."""
    allowed = {
        ("approver.py", "_publish_approved"): "✅ *Part ",
        ("approver.py", "process"): "❌ *Part ",
        ("calibrate.py", "_send_summary"): "text",
    }
    found: dict[tuple[str, str], list[ast.Call]] = {}

    for path in sorted((ROOT / "series").glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        parents = {
            child: parent
            for parent in ast.walk(tree)
            for child in ast.iter_child_nodes(parent)
        }
        for node in ast.walk(tree):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "notifier"
                and node.func.attr == "send_message"
            ):
                continue
            key = (path.name, _enclosing_function(node, parents))
            found.setdefault(key, []).append(node)

    assert set(found) == set(allowed)
    for key, calls in found.items():
        assert len(calls) == 1, f"{key} içinde yeni/tekrarlı Markdown çağrısı var"
        assert calls[0].args
        assert allowed[key] in ast.unparse(calls[0].args[0])

    # Filo tükenmesi açıkça operasyon sitesidir; sunum allowlist'ine geri giremez.
    runner_tree = ast.parse(
        (ROOT / "series" / "series_runner.py").read_text(encoding="utf-8")
    )
    runner_parents = {
        child: parent
        for parent in ast.walk(runner_tree)
        for child in ast.iter_child_nodes(parent)
    }
    fleet_alerts = [
        node
        for node in ast.walk(runner_tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_fleet_alert"
    ]
    assert len(fleet_alerts) == 1
    assert _enclosing_function(fleet_alerts[0], runner_parents) == "run_all"
    assert "Aktif seri kalmadı" in ast.unparse(fleet_alerts[0].args[0])

    # Operasyon modülleri aynı slug-scoped runner yoluna bağlanmalı; ikinci outbox yok.
    expected_plain_routes = {
        "approver.py": 2,
        "critic.py": 1,
        "produce.py": 2,
        "replenish.py": 1,
        # Yayin acil turu (ROCK 2) iki yeni routed alarm ekledi: eksik cekimle
        # yayin bildirimi ve zorunlu platform dogrulanamadi bildirimi. ROCK 3d
        # ucuncusunu ekledi: altyapi butcesi dolunca needs_human bildirimi.
        "series_runner.py": 12,
    }
    for filename, expected_count in expected_plain_routes.items():
        tree = ast.parse((ROOT / "series" / filename).read_text(encoding="utf-8"))
        routed = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "_series_alert"
        ]
        assert len(routed) == expected_count, filename


def _dispatch_converted_site(
    site: str, slug: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    if site == "replenish":
        replenish._alert(slug, "❌ *Quota_Lab* RESOURCE_EXHAUSTED")
    elif site == "critic":
        critic._notify("🚨 *QC KOTA-DIŞI* `RESOURCE_EXHAUSTED`", slug=slug)
    elif site == "produce_tts":
        bible = Bible({
            "series": {"slug": slug, "title": "Signal_Lab"},
            "narration": {"channel": "test-channel"},
        })
        video = tmp_path / "episode.mp4"
        video.write_bytes(b"video")
        monkeypatch.setattr(
            narration,
            "create_narration_for_channel",
            lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("TTS yok")),
        )
        produce._post_process(
            bible,
            {"episode": {"number": 7}, "narration": "Anlatım metni"},
            video,
        )
    elif site == "produce_audio":
        bible = Bible({"series": {"slug": slug, "title": "Audio_Lab"}})
        monkeypatch.setattr(produce.ffmpeg_tools, "measure_mean_volume", lambda path: -80.0)
        produce._verify_native_audio_delivery(bible, 7, tmp_path / "episode.mp4")
    elif site == "approver_missing_video":
        monkeypatch.setattr(approver, "_download_release", lambda tag: None)
        approver._publish_approved(
            SimpleNamespace(slug=slug), 7, {"release_tag": None, "video": None}
        )
    elif site == "approver_publish_failure":
        video = tmp_path / "approved.mp4"
        video.write_bytes(b"video")
        monkeypatch.setattr(approver, "_download_release", lambda tag: video)
        monkeypatch.setattr(approver, "_publish_part", lambda *args, **kwargs: [])
        approver._publish_approved(
            SimpleNamespace(slug=slug), 7, {"release_tag": "v7", "subtitle": ""}
        )
    else:  # pragma: no cover - parametre listesinin kendi sigortası
        raise AssertionError(site)


@pytest.mark.parametrize(
    "site",
    [
        "replenish",
        "critic",
        "produce_tts",
        "produce_audio",
        "approver_missing_video",
        "approver_publish_failure",
    ],
)
def test_each_converted_site_queues_a_telegram_400(
    site: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(
        notifier.requests,
        "post",
        lambda *args, **kwargs: _Response(
            {"ok": False, "description": LIVE_ENTITY_ERROR}, 400
        ),
    )
    slug = f"alert-{site}"

    _dispatch_converted_site(site, slug, tmp_path, monkeypatch)

    entries = _outbox(slug)
    assert len(entries) == 1
    assert entries[0]["series_slug"] == slug
    assert entries[0]["text"]
    assert entries[0]["attempt_count"] == 1
    assert "parse entities" in entries[0]["last_error"]
    assert slug in series_runner._FAILED_ALERT_SLUGS
    assert series_runner._outboxes_empty([slug]) is False


def test_live_replenish_resource_exhausted_message_is_delivered_plain(
    monkeypatch: pytest.MonkeyPatch,
):
    calls: list[dict] = []

    def post(url, data=None, files=None, timeout=None):
        calls.append(dict(data or {}))
        if (data or {}).get("parse_mode") == "Markdown":
            return _Response({"ok": False, "description": LIVE_ENTITY_ERROR}, 400)
        return _Response({"ok": True, "result": {"message_id": 913}})

    monkeypatch.setattr(notifier.requests, "post", post)
    text = (
        "❌ *Quota_Lab* oto-ikmal BAŞARISIZ: Gemini ikmal çağrısı başarısız: "
        "429 RESOURCE_EXHAUSTED\n"
        "Kuyrukta 1 part kaldı ,  kuyruk biterse bu kanala video çıkmaz."
    )

    assert replenish._alert("quota-lab", text) is True
    assert calls == [{"chat_id": "test-chat-never-log", "text": text}]
    assert _outbox("quota-lab") == []


def test_no_active_series_alert_is_plain_queued_red_and_retried(
    monkeypatch: pytest.MonkeyPatch,
):
    home = "completed-fleet-home"
    alert_text = (
        "ℹ️ *Seri otomasyonu:* Aktif seri kalmadı ,  tüm diziler tamamlandı. "
        "Yeni sezon/part eklenene kadar bu kanallara yeni video ÇIKMAYACAK."
    )
    first_calls: list[dict] = []

    monkeypatch.setattr(
        series_runner,
        "_outbox_slugs",
        lambda slug: [slug] if slug else [home],
    )
    monkeypatch.setattr(series_runner, "list_active_series", lambda: [])
    monkeypatch.setattr(replenish, "replenish_all", lambda dry_run=False: None)

    def failing_post(url, data=None, files=None, timeout=None):
        first_calls.append(dict(data or {}))
        return _Response({"ok": False, "description": LIVE_ENTITY_ERROR}, 400)

    monkeypatch.setattr(notifier.requests, "post", failing_post)

    with pytest.raises(SystemExit) as exc:
        series_runner.main([])

    assert exc.value.code == 1
    assert first_calls == [{"chat_id": "test-chat-never-log", "text": alert_text}]
    assert len(_outbox(home)) == 1
    assert _outbox(home)[0]["text"] == alert_text

    retry_calls: list[dict] = []

    def successful_post(url, data=None, files=None, timeout=None):
        retry_calls.append(dict(data or {}))
        return _Response({"ok": True, "result": {"message_id": 914}})

    monkeypatch.setattr(notifier.requests, "post", successful_post)

    series_runner.main([])

    assert retry_calls == [
        {"chat_id": "test-chat-never-log", "text": alert_text},
        {"chat_id": "test-chat-never-log", "text": alert_text},
    ]
    assert _outbox(home) == []


def test_approval_card_still_uses_markdown(monkeypatch: pytest.MonkeyPatch):
    calls: list[dict] = []

    def post(url, data=None, files=None, timeout=None):
        calls.append(dict(data or {}))
        return _Response({"ok": True, "result": {"message_id": 41}})

    monkeypatch.setattr(notifier.requests, "post", post)

    message_id = notifier.request_approval(7, "Human Card", slug="human-card")

    assert message_id == 41
    assert calls[0]["parse_mode"] == "Markdown"
    assert "reply_markup" in calls[0]
    assert "*human-card* Part 7" in calls[0]["text"]


def test_approver_run_ends_red_then_retries_shared_outbox(
    monkeypatch: pytest.MonkeyPatch,
):
    slug = "approval-alert"
    attempts = 0

    def failing_post(*args, **kwargs):
        nonlocal attempts
        attempts += 1
        return _Response({"ok": False, "description": LIVE_ENTITY_ERROR}, 400)

    monkeypatch.setattr(notifier.requests, "post", failing_post)
    monkeypatch.setattr(
        approver,
        "process",
        lambda item: series_runner._series_alert(item, "⚠️ *Onay operasyon alarmı*"),
    )

    with pytest.raises(SystemExit) as exc:
        approver.main(["--series", slug])

    assert exc.value.code == 1
    assert attempts == 1
    assert len(_outbox(slug)) == 1

    monkeypatch.setattr(
        notifier.requests,
        "post",
        lambda *args, **kwargs: _Response(
            {"ok": True, "result": {"message_id": 52}}
        ),
    )
    monkeypatch.setattr(approver, "process", lambda item: True)

    approver.main(["--series", slug])

    assert _outbox(slug) == []


def test_replenish_run_ends_red_then_retries_shared_outbox(
    monkeypatch: pytest.MonkeyPatch,
):
    slug = "replenish-alert"
    attempts = 0

    def failing_post(*args, **kwargs):
        nonlocal attempts
        attempts += 1
        return _Response({"ok": False, "description": LIVE_ENTITY_ERROR}, 400)

    monkeypatch.setattr(notifier.requests, "post", failing_post)
    monkeypatch.setattr(
        replenish,
        "replenish",
        lambda item, dry_run=False: replenish._alert(
            item, "🔁 *İkmal başarı operasyon alarmı*"
        ),
    )

    with pytest.raises(SystemExit) as exc:
        replenish.main(["--series", slug])

    assert exc.value.code == 1
    assert attempts == 1
    assert len(_outbox(slug)) == 1

    monkeypatch.setattr(
        notifier.requests,
        "post",
        lambda *args, **kwargs: _Response(
            {"ok": True, "result": {"message_id": 53}}
        ),
    )
    monkeypatch.setattr(replenish, "replenish", lambda item, dry_run=False: True)

    replenish.main(["--series", slug])

    assert _outbox(slug) == []
