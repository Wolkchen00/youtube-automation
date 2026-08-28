import json
import time
from types import SimpleNamespace
from unittest import mock

import pytest

from core import uploader
from series import series_runner


PART22_ASYNC_RESPONSE = {
    "success": True,
    "message": (
        "Upload initiated successfully in background. Your synchronous request "
        "was taking too long and has been durably handed off to the upload worker. "
        "Check its status with GET /api/uploadposts/status?request_id="
        "e8e8d371f3ee481094941b47a79794e2. Docs: "
        "https://docs.upload-post.com/api/upload-status"
    ),
    "request_id": "e8e8d371f3ee481094941b47a79794e2",
    "total_platforms": 1,
    "job_id": "714b4b40855d4dad9fc7b4582de09a12",
}

PART22_REAL_TERMINAL_RESPONSE = {
    "status": "completed",
    "completed": 1,
    "total": 1,
    "results": [{
        "platform": "instagram",
        "success": False,
        "platform_post_id": None,
        "post_url": None,
        "error_code": "account_reauth_required",
        "failure_stage": "precheck",
        "error_message": (
            "Error validating access token: The session has been invalidated because "
            "the user changed their password or Facebook has changed the session for "
            "security reasons. Please reconnect your Instagram account at "
            "https://app.upload-post.com/manage-users."
        ),
        "request_id": "e8e8d371f3ee481094941b47a79794e2",
        "job_id": "714b4b40855d4dad9fc7b4582de09a12",
    }],
    "external_id": None,
    "request_id": "e8e8d371f3ee481094941b47a79794e2",
}


class FakeResponse:
    def __init__(self, body=None, status_code=200, json_error=None):
        self.body = body
        self.status_code = status_code
        self.content = b"json"
        self.json_error = json_error

    def json(self):
        if self.json_error:
            raise self.json_error
        return self.body


class FakeClock:
    def __init__(self):
        self.now = 0.0
        self.sleeps = []

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


@pytest.fixture(autouse=True)
def clean_upload_state(monkeypatch):
    uploader._LAST_UPLOAD_FAILURES.clear()
    monkeypatch.setattr(uploader, "UPLOAD_POST_API_KEY", "test-key")


def _upload(tmp_path, platform="instagram"):
    video = tmp_path / "video.mp4"
    video.write_bytes(b"small fixture")
    return uploader.upload_to_platform(
        video,
        "Test title",
        "Test description",
        user="test-user",
        platform=platform,
    )


def _processing_status(platform="instagram"):
    return {
        "request_id": PART22_ASYNC_RESPONSE["request_id"],
        "job_id": PART22_ASYNC_RESPONSE["job_id"],
        "status": "processing",
        "scheduler_status": "running",
        "completed": 0,
        "failed": 0,
        "retryable": 0,
        "skipped": 0,
        "total": 1,
        "results": [{
            "platform": platform,
            "status": "processing",
            "attempts": 1,
            "success": False,
        }],
        "external_id": None,
        "message": "Upload is currently being processed",
    }


def test_sync_publication_id_keeps_return_and_makes_no_status_request(tmp_path, monkeypatch, caplog):
    body = {"success": True, "results": {"youtube": {"video_id": "vKus2kyMIN0"}}}
    post = mock.Mock(return_value=FakeResponse(body))
    get = mock.Mock()
    monkeypatch.setattr(uploader.requests, "post", post)
    monkeypatch.setattr(uploader.requests, "get", get)

    result = _upload(tmp_path, platform="youtube")

    assert result is body
    assert post.call_count == 1
    get.assert_not_called()
    assert "✅ YOUTUBE uploaded: Test title..." in caplog.text


def test_async_completed_success_is_confirmed_and_preserves_identity_and_url(tmp_path, monkeypatch):
    status = {
        "request_id": PART22_ASYNC_RESPONSE["request_id"],
        "job_id": PART22_ASYNC_RESPONSE["job_id"],
        "status": "completed",
        "completed": 1,
        "failed": 0,
        "results": [{
            "platform": "instagram",
            "status": "completed",
            "success": True,
            "platform_post_id": "ig-123",
            "post_url": "https://www.instagram.com/reel/ig-123/",
        }],
    }
    post = mock.Mock(return_value=FakeResponse(PART22_ASYNC_RESPONSE))
    get = mock.Mock(return_value=FakeResponse(status))
    monkeypatch.setattr(uploader.requests, "post", post)
    monkeypatch.setattr(uploader.requests, "get", get)

    result = _upload(tmp_path)

    assert result
    assert result["publication_id"] == "ig-123"
    assert result["_async_confirmation"]["request_id"] == PART22_ASYNC_RESPONSE["request_id"]
    get.assert_called_once_with(
        uploader.UPLOAD_POST_STATUS_URL,
        headers={"Authorization": "Apikey test-key"},
        params={"request_id": PART22_ASYNC_RESPONSE["request_id"]},
        timeout=uploader.ASYNC_STATUS_REQUEST_TIMEOUT,
    )


def test_confirmed_async_identity_and_post_url_are_written_to_registry(tmp_path, monkeypatch):
    result = {
        "publication_id": "7679191703630171406",
        "results": [{
            "platform": "tiktok",
            "success": True,
            "platform_post_id": "7679191703630171406",
            "post_url": "https://www.tiktok.com/@sentinal.ihsan.daily/video/7679191703630171406",
        }],
        "_async_confirmation": {"request_id": "req-1", "job_id": "job-1"},
    }
    monkeypatch.setattr("series.bible.data_dir", lambda slug: tmp_path)

    series_runner._append_publish_registry("fixture", 22, "Async", {"tiktok": result})

    registry = json.loads((tmp_path / "published.json").read_text(encoding="utf-8"))
    assert registry[0]["results"] == {"tiktok": "7679191703630171406"}
    assert registry[0]["post_urls"] == {
        "tiktok": "https://www.tiktok.com/@sentinal.ihsan.daily/video/7679191703630171406"
    }


def test_async_terminal_failure_is_not_platform_success(tmp_path, monkeypatch, caplog):
    failed = {
        "status": "failed",
        "completed": 0,
        "failed": 1,
        "results": [{
            "platform": "instagram", "status": "failed", "success": False,
        }],
        "message": "Platform rejected the upload",
    }
    monkeypatch.setattr(uploader.requests, "post", mock.Mock(return_value=FakeResponse(PART22_ASYNC_RESPONSE)))
    monkeypatch.setattr(uploader.requests, "get", mock.Mock(return_value=FakeResponse(failed)))

    assert _upload(tmp_path) is None
    failure = uploader.pop_upload_failure("instagram")
    assert failure["request_id"] == PART22_ASYNC_RESPONSE["request_id"]
    assert "terminal başarısızlık" in failure["reason"]
    assert PART22_ASYNC_RESPONSE["request_id"] in caplog.text


def test_processing_timeout_fails_closed_without_real_sleep_and_alerts(tmp_path, monkeypatch, caplog):
    clock = FakeClock()
    monkeypatch.setattr(uploader, "ASYNC_UPLOAD_CONFIRM_TIMEOUT", 20)
    monkeypatch.setattr(uploader, "ASYNC_UPLOAD_POLL_INTERVALS", (5, 15, 30))
    monkeypatch.setattr(uploader, "_ASYNC_SLEEP", clock.sleep)
    monkeypatch.setattr(uploader, "_ASYNC_MONOTONIC", clock.monotonic)
    post = mock.Mock(return_value=FakeResponse(PART22_ASYNC_RESPONSE))
    get = mock.Mock(return_value=FakeResponse(_processing_status()))
    monkeypatch.setattr(uploader.requests, "post", post)
    monkeypatch.setattr(uploader.requests, "get", get)
    alert = mock.Mock()
    monkeypatch.setattr(series_runner, "_alert", alert)
    monkeypatch.setattr(series_runner, "_append_publish_registry", mock.Mock())
    # Asenkron-belirsiz iş telafi POST'una girmemeli; 90 saniyelik sleep çağrısı hata olur.
    monkeypatch.setattr(series_runner.time, "sleep", mock.Mock(side_effect=AssertionError("telafi sleep çağrıldı")))
    video = tmp_path / "video.mp4"
    video.write_bytes(b"small fixture")
    meta = SimpleNamespace(
        slug="fixture",
        base_title="Fixture Series",
        upload_profile="profile",
        platforms=["instagram"],
        hashtags="#fixture",
        title_for=lambda n, subtitle: "Fixture title",
        description_for=lambda n, subtitle: "Fixture description",
    )

    wall_started = time.perf_counter()
    ok = series_runner._publish_part(meta, 22, video, "Timeout")
    wall_elapsed = time.perf_counter() - wall_started

    assert ok == []
    assert wall_elapsed < 1
    assert clock.sleeps == [5, 15]
    assert get.call_count == 3
    assert post.call_count == 1
    alert.assert_called_once()
    alarm = alert.call_args.args[0]
    assert "INSTAGRAM" in alarm
    assert "zaman aşımı" in alarm
    assert PART22_ASYNC_RESPONSE["request_id"] in alarm
    assert PART22_ASYNC_RESPONSE["request_id"] in caplog.text


def test_series_ok_and_registry_include_only_verified_platforms(tmp_path, monkeypatch):
    youtube = {"success": True, "results": {"youtube": {"video_id": "yt-1"}}}
    failure = {
        "async": True,
        "reason": "20s doğrulama zaman aşımı",
        "request_id": "ig-request",
        "job_id": "ig-job",
    }
    upload = mock.Mock(side_effect=[youtube, None])
    pop_failure = mock.Mock(side_effect=lambda platform: failure if platform == "instagram" else None)
    registry = mock.Mock()
    alert = mock.Mock()
    monkeypatch.setattr(series_runner, "upload_to_platform", upload)
    monkeypatch.setattr(series_runner, "pop_upload_failure", pop_failure)
    monkeypatch.setattr(series_runner, "_append_publish_registry", registry)
    monkeypatch.setattr(series_runner, "_alert", alert)
    monkeypatch.setattr(series_runner.time, "sleep", mock.Mock(side_effect=AssertionError("telafi sleep çağrıldı")))
    video = tmp_path / "video.mp4"
    video.write_bytes(b"fixture")
    meta = SimpleNamespace(
        slug="fixture",
        base_title="Fixture Series",
        upload_profile="profile",
        platforms=["youtube", "instagram"],
        hashtags="#fixture",
        title_for=lambda n, subtitle: "Fixture title",
        description_for=lambda n, subtitle: "Fixture description",
    )

    ok = series_runner._publish_part(meta, 22, video)

    assert ok == ["youtube"]
    assert upload.call_count == 2
    registry.assert_called_once()
    assert registry.call_args.args[3] == {"youtube": youtube}
    assert registry.call_args.kwargs["unconfirmed"] == {"instagram": failure}
    assert "ig-request" in alert.call_args.args[0]


@pytest.mark.parametrize(
    "status_response, expected",
    [
        (FakeResponse({"error": "down"}, status_code=503), "HTTP 503"),
        (FakeResponse(json_error=ValueError("not json")), "bozuk JSON"),
    ],
)
def test_status_endpoint_error_or_bad_json_fails_closed(
    tmp_path, monkeypatch, caplog, status_response, expected
):
    monkeypatch.setattr(uploader.requests, "post", mock.Mock(return_value=FakeResponse(PART22_ASYNC_RESPONSE)))
    monkeypatch.setattr(uploader.requests, "get", mock.Mock(return_value=status_response))

    assert _upload(tmp_path) is None
    assert expected in caplog.text
    assert PART22_ASYNC_RESPONSE["request_id"] in caplog.text


def test_part22_completed_job_but_platform_not_published_is_failure():
    """İş completed dese de platform düşmediyse sonuç yayın başarısı değildir."""
    assert "failed" not in PART22_REAL_TERMINAL_RESPONSE
    assert "status" not in PART22_REAL_TERMINAL_RESPONSE["results"][0]

    outcome, detail = uploader._status_outcome(PART22_REAL_TERMINAL_RESPONSE, "instagram")

    assert outcome == "failure"
    assert "success=false" in detail


def test_part22_completed_job_but_platform_not_published_end_to_end(tmp_path, monkeypatch):
    """Canlı part22 gövdesi upload_to_platform boyunca None ve request_id üretir."""
    post = mock.Mock(return_value=FakeResponse(dict(PART22_ASYNC_RESPONSE)))
    get = mock.Mock(return_value=FakeResponse(PART22_REAL_TERMINAL_RESPONSE))
    monkeypatch.setattr(uploader.requests, "post", post)
    monkeypatch.setattr(uploader.requests, "get", get)

    result = _upload(tmp_path)
    failure = uploader.pop_upload_failure("instagram")

    assert result is None
    assert failure["request_id"] == "e8e8d371f3ee481094941b47a79794e2"
    assert post.call_count == 1
    assert get.call_count == 1
    assert get.call_args.kwargs["params"] == {
        "request_id": "e8e8d371f3ee481094941b47a79794e2"
    }


def test_completed_success_for_another_platform_is_not_our_success(tmp_path, monkeypatch):
    terminal = {
        "status": "completed",
        "completed": 1,
        "total": 1,
        "results": [{
            "platform": "tiktok",
            "success": True,
            "platform_post_id": "tt-123",
            "post_url": "https://www.tiktok.com/@fixture/video/tt-123",
        }],
    }
    monkeypatch.setattr(uploader, "ASYNC_UPLOAD_CONFIRM_TIMEOUT", 0)
    monkeypatch.setattr(
        uploader.requests,
        "post",
        mock.Mock(return_value=FakeResponse(dict(PART22_ASYNC_RESPONSE))),
    )
    get = mock.Mock(return_value=FakeResponse(terminal))
    monkeypatch.setattr(uploader.requests, "get", get)

    assert _upload(tmp_path, platform="instagram") is None
    assert get.call_count == 1


@pytest.mark.parametrize(
    "terminal",
    [
        {},
        {"status": "completed"},
        {"results": "bozuk"},
        {"results": []},
    ],
    ids=["empty", "completed-only", "results-wrong-type", "results-empty"],
)
def test_incomplete_status_bodies_fail_closed_without_sleep(tmp_path, monkeypatch, terminal):
    monkeypatch.setattr(uploader, "ASYNC_UPLOAD_CONFIRM_TIMEOUT", 0)
    monkeypatch.setattr(
        uploader.requests,
        "post",
        mock.Mock(return_value=FakeResponse(dict(PART22_ASYNC_RESPONSE))),
    )
    get = mock.Mock(return_value=FakeResponse(terminal))
    monkeypatch.setattr(uploader.requests, "get", get)
    sleep = mock.Mock(side_effect=AssertionError("gerçek sleep çağrıldı"))
    monkeypatch.setattr(uploader, "_ASYNC_SLEEP", sleep)

    assert _upload(tmp_path) is None
    assert get.call_count == 1
    sleep.assert_not_called()


def test_job_id_is_used_when_request_id_is_absent(tmp_path, monkeypatch):
    accepted = {"success": True, "job_id": "job-only"}
    completed = {
        "status": "completed",
        "completed": 1,
        "failed": 0,
        "results": [{"platform": "tiktok", "status": "completed", "success": True}],
    }
    monkeypatch.setattr(uploader.requests, "post", mock.Mock(return_value=FakeResponse(accepted)))
    get = mock.Mock(return_value=FakeResponse(completed))
    monkeypatch.setattr(uploader.requests, "get", get)

    assert _upload(tmp_path, platform="tiktok")
    assert get.call_args.kwargs["params"] == {"job_id": "job-only"}
