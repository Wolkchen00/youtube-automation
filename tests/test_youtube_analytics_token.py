from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from googleapiclient.errors import HttpError
from httplib2 import Response


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "get_youtube_analytics_token.py"


@pytest.fixture
def mod():
    spec = importlib.util.spec_from_file_location("get_youtube_analytics_token", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def isolated(mod, tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config = [
        {
            "kanal": "shadowedhistory",
            "youtube_channel_id": "expected-id",
            "upload_post_profile": "shad0wedhistory",
            "secret_adi": "YT_ANALYTICS_TOKEN_SHADOWEDHISTORY",
            "dogrulandi": True,
        }
    ]
    config_path = config_dir / "audience_channels.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(mod, "CHANNELS_CONFIG", config_path)
    monkeypatch.setattr(mod, "SECRETS_DIR", tmp_path / "secrets_local")
    monkeypatch.setattr(mod, "MASTER_ENV", tmp_path / "missing-master.env")
    monkeypatch.delenv("YOUTUBE_CLIENT_ID", raising=False)
    monkeypatch.delenv("YOUTUBE_CLIENT_SECRET", raising=False)
    return config[0]


def credentials(refresh_token="refresh-value"):
    return SimpleNamespace(
        token="access-value",
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id="client-id",
        client_secret="client-secret-value",
        scopes=None,
    )


def client_json(tmp_path):
    path = tmp_path / "oauth.json"
    path.write_text(
        json.dumps(
            {
                "installed": {
                    "client_id": "client-id",
                    "client_secret": "client-secret-value",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost"],
                }
            }
        ),
        encoding="utf-8",
    )
    return path


def google_build_with_channel(channel_id, title="Chosen Channel"):
    request = MagicMock()
    request.execute.return_value = {
        "items": [{"id": channel_id, "snippet": {"title": title}}]
    }
    service = MagicMock()
    service.channels.return_value.list.return_value = request
    return service


def install_flow(mod, monkeypatch, creds):
    flow = MagicMock()
    flow.run_local_server.return_value = creds
    factory = MagicMock(return_value=flow)
    monkeypatch.setattr(mod.InstalledAppFlow, "from_client_config", factory)
    return factory, flow


def test_channel_mismatch_saves_nothing_and_exits_2(
    mod, isolated, tmp_path, monkeypatch, capsys
):
    _, flow = install_flow(mod, monkeypatch, credentials())
    monkeypatch.setattr(
        mod, "build", MagicMock(return_value=google_build_with_channel("wrong-id", "Yanlis Kanal"))
    )

    result = mod.main(
        ["--kanal", "shadowedhistory", "--client-secret", str(client_json(tmp_path))]
    )

    assert result == 2
    assert not (tmp_path / "secrets_local").exists()
    assert "Yanlis Kanal" in capsys.readouterr().out
    flow.run_local_server.assert_called_once_with(
        port=8765, open_browser=True, access_type="offline", prompt="consent"
    )


def test_match_saves_refresh_token_and_prints_gh_command(
    mod, isolated, tmp_path, monkeypatch, capsys
):
    creds = credentials()
    install_flow(mod, monkeypatch, creds)
    monkeypatch.setattr(
        mod, "build", MagicMock(return_value=google_build_with_channel("expected-id"))
    )

    result = mod.main(
        ["--kanal", "shadowedhistory", "--client-secret", str(client_json(tmp_path))]
    )

    token_path = tmp_path / "secrets_local" / "yt_analytics_shadowedhistory.json"
    assert result == 0
    assert json.loads(token_path.read_text(encoding="utf-8"))["refresh_token"] == "refresh-value"
    output = capsys.readouterr().out
    assert (
        "gh secret set YT_ANALYTICS_TOKEN_SHADOWEDHISTORY < "
        "secrets_local/yt_analytics_shadowedhistory.json" in output
    )
    assert "client-secret-value" not in output
    assert "refresh-value" not in output


def test_missing_credentials_is_clear_error(mod, isolated, capsys):
    result = mod.main(["--kanal", "shadowedhistory"])

    assert result == 1
    output = capsys.readouterr().out
    assert "OAuth istemci bilgisi eksik" in output
    assert "YOUTUBE_CLIENT_ID" in output
    assert "client_secret_*.json" in output


def test_probe_builds_exact_query(mod, monkeypatch):
    query = MagicMock()
    query.execute.return_value = {"rows": [[0.0, 1.0, 0.5]]}
    reports = MagicMock()
    reports.query.return_value = query
    analytics = MagicMock()
    analytics.reports.return_value = reports
    build_mock = MagicMock(return_value=analytics)
    monkeypatch.setattr(mod, "build", build_mock)

    assert mod.retention_kontrolu(credentials(), "video123") is True

    reports.query.assert_called_once_with(
        ids="channel==MINE",
        startDate="2020-01-01",
        endDate=mod.date.today().isoformat(),
        dimensions="elapsedVideoTimeRatio",
        metrics="audienceWatchRatio,relativeRetentionPerformance",
        filters="video==video123",
    )


def test_access_not_configured_prints_turkish_enable_message(mod, monkeypatch, capsys):
    error_body = {
        "error": {
            "code": 403,
            "message": (
                "API disabled. Enable at "
                "https://console.developers.google.com/apis/api/youtubeanalytics.googleapis.com/overview?project=123"
            ),
            "errors": [{"reason": "accessNotConfigured"}],
        }
    }
    query = MagicMock()
    query.execute.side_effect = HttpError(
        Response({"status": "403"}), json.dumps(error_body).encode("utf-8")
    )
    analytics = MagicMock()
    analytics.reports.return_value.query.return_value = query
    monkeypatch.setattr(mod, "build", MagicMock(return_value=analytics))

    assert mod.retention_kontrolu(credentials(), "video123") is False

    output = capsys.readouterr().out
    assert "HTTP 403 - accessNotConfigured" in output
    assert "YouTube Analytics API" in output
    assert "etkinlestirilmelidir" in output
    assert "https://console.developers.google.com/" in output


def test_kontrol_uses_saved_file_without_browser(
    mod, isolated, tmp_path, monkeypatch
):
    token_dir = tmp_path / "secrets_local"
    token_dir.mkdir()
    token_file = token_dir / "yt_analytics_shadowedhistory.json"
    token_file.write_text(
        json.dumps(
            {
                "token": "old-access",
                "refresh_token": "saved-refresh",
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": "client-id",
                "client_secret": "saved-secret",
                "scopes": mod.SCOPES,
            }
        ),
        encoding="utf-8",
    )
    saved_creds = credentials("saved-refresh")
    saved_creds.refresh = MagicMock()
    from_info = MagicMock(return_value=saved_creds)
    monkeypatch.setattr(mod.Credentials, "from_authorized_user_info", from_info)
    browser = MagicMock()
    monkeypatch.setattr(mod.InstalledAppFlow, "from_client_config", browser)
    monkeypatch.setattr(
        mod, "build", MagicMock(return_value=google_build_with_channel("expected-id"))
    )

    assert mod.main(["--kanal", "shadowedhistory", "--kontrol"]) == 0

    browser.assert_not_called()
    saved_creds.refresh.assert_called_once()
    assert token_file.exists()


def test_gitignore_contains_secrets_local():
    lines = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert "secrets_local/" in lines
