"""ROCK 2: kritik Telegram alarmlari, outbox ve workflow sirasi kanitlari."""

from __future__ import annotations

import ast
import inspect
import json
from contextlib import ExitStack
from pathlib import Path
from unittest import mock

import pytest
import requests

from series import notifier, series_runner
from series.bible import Bible
from series.produce import ProduceResult
from series.series_meta import SeriesMeta


class _Response:
    def __init__(self, payload: dict, status_code: int = 200):
        self.payload = payload
        self.status_code = status_code

    def json(self) -> dict:
        return self.payload


@pytest.fixture(autouse=True)
def _isolated_alerts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
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


def test_critical_alert_with_markdown_characters_is_delivered_as_plain_text(monkeypatch):
    sent: list[dict] = []

    def post(url, data=None, files=None, timeout=None):
        sent.append(dict(data or {}))
        return _Response({"ok": True, "result": {"message_id": 731}})

    monkeypatch.setattr(notifier.requests, "post", post)
    text = "Durum awaiting_approval; *kritik* [kanal] karanlik."

    result = notifier.send_plain_message(text)
    assert isinstance(result, notifier.SendResult)
    assert result.delivered is True
    assert result.error is None
    assert result.message_id == 731
    assert result.get("message_id") == 731
    assert sent == [{"chat_id": "test-chat-never-log", "text": text}]
    assert series_runner._series_alert("unnatural-lab", text) is True
    assert _outbox("unnatural-lab") == []


def test_telegram_400_entity_error_is_structured_and_not_silently_swallowed(monkeypatch):
    description = "Bad Request: can't parse entities: Can't find end of the entity"
    monkeypatch.setattr(
        notifier.requests,
        "post",
        lambda *a, **k: _Response({"ok": False, "description": description}, 400),
    )

    delivered = series_runner._series_alert(
        "unnatural-lab", "Durum awaiting_approval; *kritik* [kanal]."
    )

    assert delivered is False
    entries = _outbox("unnatural-lab")
    assert len(entries) == 1
    assert entries[0]["attempt_count"] == 1
    assert entries[0]["last_error"] == description


def test_network_error_returns_false_and_routes_critical_alert_to_outbox(monkeypatch, caplog):
    def fail(*args, **kwargs):
        raise requests.ConnectionError(
            "https://api.telegram.org/bottest-token-never-log/sendMessage failed"
        )

    monkeypatch.setattr(notifier.requests, "post", fail)
    text = "awaiting_approval ag hatasi"

    assert series_runner._series_alert("unnatural-lab", text) is False
    entries = _outbox("unnatural-lab")
    assert entries[0]["series_slug"] == "unnatural-lab"
    assert entries[0]["text"] == text
    assert entries[0]["attempt_count"] == 1
    assert "ConnectionError" in entries[0]["last_error"]
    assert "test-token-never-log" not in caplog.text
    assert "test-chat-never-log" not in caplog.text


def test_next_run_drains_outbox_as_plain_text_and_removes_delivered_entry(monkeypatch):
    notifier.enqueue_critical_alert("unnatural-lab", "eski_alert * [", "network")
    sent: list[dict] = []

    def post(url, data=None, files=None, timeout=None):
        sent.append(dict(data or {}))
        return _Response({"ok": True, "result": {"message_id": 99}})

    monkeypatch.setattr(notifier.requests, "post", post)

    assert series_runner.main([
        "--series", "unnatural-lab", "--drain-alerts-only",
    ]) is None
    assert _outbox("unnatural-lab") == []
    assert sent == [{
        "chat_id": "test-chat-never-log",
        "text": "eski_alert * [",
    }]


def test_nonempty_outbox_does_not_stop_production_but_run_still_ends_red(
    tmp_path, monkeypatch,
):
    slug = "unnatural-lab"
    notifier.enqueue_critical_alert(slug, "hala teslim edilmedi", "network")
    monkeypatch.setattr(
        notifier.requests,
        "post",
        lambda *a, **k: _Response({"ok": False, "description": "still down"}, 503),
    )

    # Workflow'un erken drain adimi outbox doluyken bile basarili tamamlanir.
    assert series_runner.main([
        "--series", slug, "--drain-alerts-only",
    ]) is None

    stack, producer, publisher = _successful_runner_stack(tmp_path, slug)
    with stack, pytest.raises(SystemExit) as exc:
        series_runner.main(["--series", slug, "--force"])

    assert exc.value.code == 1
    producer.assert_called_once()
    publisher.assert_called_once()
    entries = _outbox(slug)
    assert entries[0]["attempt_count"] == 3
    assert entries[0]["last_error"] == "still down"


def _legacy_meta(slug: str) -> SeriesMeta:
    return SeriesMeta({
        "slug": slug,
        "base_title": "Unnatural_Lab [Critical]",
        "total_parts": 1,
        "next_part": 1,
        "status": "active",
        "publish_mode": "auto",
        "upload_profile": "test-profile",
        "platforms": ["youtube"],
        "parts": {},
    })


def _legacy_bible(slug: str) -> Bible:
    return Bible({
        "series": {
            "slug": slug,
            "title": slug,
            "engine": "omni",
            "state_machine_version": 1,
            "credit_hard_cap": True,
            "credit_hard_cap_value": 800,
        },
        "characters": [],
        "environments": [],
        "props": [],
    })


def _successful_runner_stack(tmp_path: Path, slug: str):
    meta = _legacy_meta(slug)
    plan_path = tmp_path / f"{slug}-part01.json"
    plan_path.write_text("{}", encoding="utf-8")
    video = tmp_path / f"{slug}.mp4"
    video.write_bytes(b"video")
    producer = mock.Mock(return_value=ProduceResult("ok", video))
    publisher = mock.Mock(return_value=["youtube"])

    stack = ExitStack()
    stack.enter_context(mock.patch.object(series_runner.SeriesMeta, "load", return_value=meta))
    stack.enter_context(mock.patch("series.bible.Bible.load", return_value=_legacy_bible(slug)))
    stack.enter_context(mock.patch.object(meta, "save"))
    stack.enter_context(mock.patch.object(series_runner, "_channel_published_today", return_value=None))
    stack.enter_context(mock.patch.object(series_runner, "part_plan_path", return_value=plan_path))
    stack.enter_context(mock.patch.object(series_runner, "load_plan", return_value={
        "episode": {"number": 1, "title": "Gunluk video"}, "shots": [],
    }))
    stack.enter_context(mock.patch.object(series_runner, "check_credit", return_value={"credit": 5000}))
    stack.enter_context(mock.patch.object(series_runner.credit_gate, "run_gate", return_value=True))
    stack.enter_context(mock.patch.object(series_runner.credit_gate, "reserve", return_value=True))
    stack.enter_context(mock.patch.object(series_runner.credit_gate, "reconcile"))
    stack.enter_context(mock.patch.object(series_runner, "_actual_episode_spent", return_value=0))
    stack.enter_context(mock.patch.object(series_runner.produce, "produce_episode", producer))
    stack.enter_context(mock.patch.object(series_runner, "_publish_part", publisher))
    return stack, producer, publisher


def test_corrupt_outbox_does_not_stop_production_or_escape_runner(tmp_path):
    slug = "unnatural-lab"
    path = notifier.alert_outbox_path(slug)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{bozuk-json", encoding="utf-8")

    # Bozuk JSON drain'den istisna olarak kacmaz; pending/failure olarak kalir.
    assert series_runner._drain_outboxes([slug]) is False
    stack, producer, publisher = _successful_runner_stack(tmp_path, slug)
    with stack, pytest.raises(SystemExit) as exc:
        series_runner.main(["--series", slug, "--force"])

    assert exc.value.code == 1
    producer.assert_called_once()
    publisher.assert_called_once()
    assert path.read_text(encoding="utf-8") == "{bozuk-json"


def test_live_qc_hold_path_exits_red_and_persists_critical_outbox(tmp_path, monkeypatch):
    """Canli awaiting_approval dalini notifier maketi yerine runner icinden sur."""
    slug = "unnatural-lab"
    meta = _legacy_meta(slug)
    plan_path = tmp_path / "part01.json"
    plan_path.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(
        notifier.requests,
        "post",
        lambda *a, **k: _Response({"ok": False, "description": "network unavailable"}, 503),
    )

    with mock.patch.object(series_runner.SeriesMeta, "load", return_value=meta), \
            mock.patch("series.bible.Bible.load", return_value=_legacy_bible(slug)), \
            mock.patch.object(meta, "save"), \
            mock.patch.object(series_runner, "_channel_published_today", return_value=None), \
            mock.patch.object(series_runner, "part_plan_path", return_value=plan_path), \
            mock.patch.object(series_runner, "load_plan", return_value={
                "episode": {"number": 1, "title": "Bug"}, "shots": [],
            }), \
            mock.patch.object(series_runner, "check_credit", return_value={"credit": 5000}), \
            mock.patch.object(series_runner.credit_gate, "run_gate", return_value=True), \
            mock.patch.object(series_runner.credit_gate, "reserve", return_value=True), \
            mock.patch.object(series_runner.credit_gate, "reconcile"), \
            mock.patch.object(series_runner, "_actual_episode_spent", return_value=0), \
            mock.patch.object(
                series_runner.produce,
                "produce_episode",
                return_value=ProduceResult(
                    "qc_hold", reason="reference timeout", reason_code="REF_DOWNLOAD"
                ),
            ):
        with pytest.raises(SystemExit) as exc:
            series_runner.main(["--series", slug, "--force"])

    assert exc.value.code == 1
    entries = _outbox(slug)
    assert len(entries) == 1
    assert entries[0]["series_slug"] == slug
    assert "awaiting_approval" in entries[0]["text"]
    assert "*Unnatural_Lab [Critical]*" in entries[0]["text"]


def test_every_runner_critical_callsite_uses_the_outbox_routing_helper():
    tree = ast.parse(inspect.getsource(series_runner))
    routed = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_series_alert"
    ]
    direct = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_alert"
    ]

    # Filo bos alarmi, async dogrulama, iki terminal dal, iki kredi kapisi,
    # QC hold, uretim hatasi ve tum-platform yayin hatasi. Yayin acil turu (ROCK 2)
    # ikisini ekledi: eksik cekimle yayin bildirimi ve zorunlu platform dogrulanamadi.
    # ROCK 3d ucuncusunu ekledi: altyapi butcesi dolunca needs_human bildirimi.
    # Bolum butunlugu denetimi dordunculeyi ekledi: yayinlandi ama kusurlu.
    assert len(routed) == 13
    assert len(direct) == 2  # _series_alert delegasyonu + evsiz filo alarmi fallback'i
    source = inspect.getsource(series_runner)
    for fragment in (
        "request_id={request_id}",
        "terminal duruma",
        "needs_human",
        "kredi kapısında",
        "aylik tavan",
        "awaiting_approval",
        "ÜRETİLEMEDİ",
        "YAYINLANAMADI",
        "Aktif seri kalmadı",
    ):
        assert fragment in source


def test_approval_card_and_media_group_keep_markdown_and_message_id(monkeypatch, tmp_path):
    frame = tmp_path / "preview.jpg"
    frame.write_bytes(b"jpeg")
    calls: list[tuple[str, dict]] = []

    def post(url, data=None, files=None, timeout=None):
        method = url.rsplit("/", 1)[-1]
        calls.append((method, dict(data or {})))
        if method == "sendMediaGroup":
            return _Response({"ok": True, "result": [{"message_id": 40}]})
        return _Response({"ok": True, "result": {"message_id": 41}})

    monkeypatch.setattr(notifier.requests, "post", post)

    message_id = notifier.request_approval(
        23,
        "Unnatural Lab",
        video_path=None,
        frame_paths=[str(frame)],
        slug="unnatural-lab",
    )

    assert message_id == 41
    assert [method for method, _ in calls] == ["sendMediaGroup", "sendMessage"]
    media = json.loads(calls[0][1]["media"])
    assert media[0]["parse_mode"] == "Markdown"
    assert calls[1][1]["parse_mode"] == "Markdown"
    assert "reply_markup" in calls[1][1]


def test_workflow_drains_before_persist_and_has_checkout_independent_fallback():
    root = Path(__file__).resolve().parents[1]
    workflow = (root / ".github" / "workflows" / "unnatural-lab.yml").read_text(
        encoding="utf-8"
    )

    drain = workflow.index("--drain-alerts-only")
    approval = workflow.index("Onay kuyrugunu isle")
    produce = workflow.index("Produce + publish")
    persist = workflow.index("Persist series state")
    fallback = workflow.index("Checkout'tan bagimsiz kritik hata bildirimi")
    assert drain < approval < produce < persist < fallback
    assert "sentinal_ihsan/" in workflow[workflow.index("Persist series state"):fallback]

    final_step = workflow[fallback:]
    assert "if: failure()" in final_step
    assert "continue-on-error: true" in final_step
    assert "curl --silent" in final_step
    assert "parse_mode" not in final_step
    assert "python" not in final_step.lower()
    assert "|| true" in final_step


def test_notifier_never_writes_last_run_json():
    assert "last_run.json" not in inspect.getsource(notifier)
