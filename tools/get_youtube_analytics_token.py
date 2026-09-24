"""Kanal bazli, salt okunur YouTube Analytics OAuth yardimcisi."""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import date
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


REPO_ROOT = Path(__file__).resolve().parent.parent
CHANNELS_CONFIG = REPO_ROOT / "config" / "audience_channels.json"
SECRETS_DIR = REPO_ROOT / "secrets_local"
MASTER_ENV = (REPO_ROOT / ".." / ".." / "_knowledge" / "credentials" / "master.env").resolve()

SCOPES = [
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/youtube.readonly",
]


class KullaniciHatasi(Exception):
    """Kullanici tarafindan giderilebilen, secret icermeyen hata."""


def kanallari_yukle(path: Path | None = None) -> dict[str, dict[str, Any]]:
    """Kanal ayarlarini ada gore indeksle."""
    config_path = path or CHANNELS_CONFIG
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise KullaniciHatasi(f"Kanal ayari okunamadi: {config_path}") from exc
    if not isinstance(raw, list):
        raise KullaniciHatasi("Kanal ayari bir JSON listesi olmali.")
    channels: dict[str, dict[str, Any]] = {}
    for item in raw:
        if not isinstance(item, dict) or not item.get("kanal"):
            raise KullaniciHatasi("Kanal ayarinda gecersiz kayit var.")
        channels[str(item["kanal"])] = item
    return channels


def _ortami_yukle() -> None:
    """Mevcut ortam degerlerini ezmeden yerel env dosyalarini yukle."""
    load_dotenv(REPO_ROOT / ".env", override=False)
    if MASTER_ENV.is_file():
        load_dotenv(MASTER_ENV, override=False)


def _json_oku(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise KullaniciHatasi(f"OAuth istemci dosyasi bulunamadi: {path}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise KullaniciHatasi(f"OAuth istemci dosyasi okunamadi: {path}") from exc
    if not isinstance(value, dict):
        raise KullaniciHatasi("OAuth istemci dosyasi bir JSON nesnesi olmali.")
    return value


def istemci_yapilandirmasi(client_secret: str | None) -> dict[str, Any]:
    """Acik dosya, env veya repodaki tek istemci JSON'undan ayar uret."""
    _ortami_yukle()
    if client_secret:
        return _json_oku(Path(client_secret).expanduser())

    client_id = os.getenv("YOUTUBE_CLIENT_ID", "").strip()
    client_secret_value = os.getenv("YOUTUBE_CLIENT_SECRET", "").strip()
    if client_id and client_secret_value:
        return {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret_value,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"],
            }
        }

    candidates = sorted(REPO_ROOT.glob("client_secret_*.json"))
    if len(candidates) == 1:
        return _json_oku(candidates[0])
    if len(candidates) > 1:
        raise KullaniciHatasi(
            "Birden fazla client_secret_*.json bulundu. --client-secret ile birini secin."
        )
    raise KullaniciHatasi(
        "OAuth istemci bilgisi eksik. YOUTUBE_CLIENT_ID ve YOUTUBE_CLIENT_SECRET "
        "degiskenlerini tanimlayin veya repo kokune tek bir client_secret_*.json koyun."
    )


def yeni_yetki_al(channel: dict[str, Any], client_secret: str | None) -> Credentials:
    """Tarayicida bir kez acilan Desktop OAuth akisini calistir."""
    client_config = istemci_yapilandirmasi(client_secret)
    print(
        "Acilan sayfada Google hesabini sec, sonra kanal listesinden "
        f"'{channel['kanal']}' kanalini sec ve izin ver."
    )
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    return flow.run_local_server(
        port=0,  # 0 = bos bir yerel kapi; 8765 baska bir programda dolu cikti (24 Eyl)
        open_browser=True,
        access_type="offline",
        prompt="consent",
    )


def _yeniden_yetkilendirme_mesaji() -> None:
    print("Hata: Google bir refresh_token dondurmedi; dosya kaydedilmedi.")
    print(
        "https://myaccount.google.com/permissions adresinde onceki uygulama erisimini "
        "kaldirin, sonra ayni komutu yeniden calistirip tekrar izin verin."
    )


def kayitli_yetkiyi_yukle(channel: dict[str, Any]) -> Credentials:
    """Kayitli refresh token'i yukle ve tarayici acmadan yenile."""
    path = token_yolu(channel)
    try:
        info = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise KullaniciHatasi(f"Kayitli token bulunamadi: {path}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise KullaniciHatasi(f"Kayitli token okunamadi: {path}") from exc
    if not isinstance(info, dict) or not info.get("refresh_token"):
        raise KullaniciHatasi(
            "Kayitli dosyada refresh_token yok. Onceki Google erisimini "
            "https://myaccount.google.com/permissions adresinden kaldirip yeniden yetki verin."
        )
    credentials = Credentials.from_authorized_user_info(info, SCOPES)
    try:
        credentials.refresh(Request())
    except Exception as exc:
        raise KullaniciHatasi(
            "Kayitli yetki yenilenemedi. Google erisimini kaldirip yeniden yetki verin."
        ) from exc
    return credentials


def kanal_kimligini_dogrula(
    credentials: Credentials, channel: dict[str, Any]
) -> tuple[bool, str, str]:
    """Yetkinin gercekte hangi YouTube kanalina ait oldugunu bul."""
    youtube = build("youtube", "v3", credentials=credentials, cache_discovery=False)
    response = youtube.channels().list(part="id,snippet", mine=True).execute()
    items = response.get("items") or []
    if not items:
        return False, "kanal bulunamadi", "bilinmiyor"
    selected = items[0]
    selected_id = str(selected.get("id") or "bilinmiyor")
    selected_name = str((selected.get("snippet") or {}).get("title") or selected_id)
    return selected_id == channel["youtube_channel_id"], selected_name, selected_id


def token_yolu(channel: dict[str, Any]) -> Path:
    return SECRETS_DIR / f"yt_analytics_{channel['kanal']}.json"


def tokeni_kaydet(credentials: Credentials, channel: dict[str, Any]) -> Path:
    """Gerekli OAuth alanlarini yerel, gitignored dosyaya yaz."""
    path = token_yolu(channel)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": list(SCOPES),
    }
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return path


def _activation_url(value: Any) -> str | None:
    """Google hata JSON'undaki acik etkinlestirme baglantisini bul."""
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() == "activationurl" and isinstance(child, str):
                return child
            found = _activation_url(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _activation_url(child)
            if found:
                return found
    return None


def _http_hata_ayrintisi(exc: HttpError) -> tuple[int | str, str, str | None]:
    status = getattr(getattr(exc, "resp", None), "status", "bilinmiyor")
    try:
        content = exc.content.decode("utf-8", errors="replace")
    except AttributeError:
        content = str(exc.content)
    reason = "bilinmeyen neden"
    activation_url: str | None = None
    try:
        body = json.loads(content)
        error = body.get("error") or {}
        errors = error.get("errors") or []
        details = error.get("details") or []
        if errors and errors[0].get("reason"):
            reason = str(errors[0]["reason"])
        else:
            for detail in details:
                if detail.get("reason"):
                    reason = str(detail["reason"])
                    break
        activation_url = _activation_url(body)
        searchable = json.dumps(body, ensure_ascii=False)
    except (TypeError, ValueError, AttributeError):
        searchable = content
    match = re.search(
        r"https://console\.(?:developers\.google\.com|cloud\.google\.com)/[^\s\"'<>]+",
        searchable,
    )
    if not activation_url and match:
        activation_url = match.group(0).replace("\\u0026", "&")
    return status, reason, activation_url


def retention_kontrolu(credentials: Credentials, video_id: str) -> bool:
    """Tek video icin YouTube Analytics retention sorgusunu kanitla."""
    params = {
        "ids": "channel==MINE",
        "startDate": "2020-01-01",
        "endDate": date.today().isoformat(),
        "dimensions": "elapsedVideoTimeRatio",
        "metrics": "audienceWatchRatio,relativeRetentionPerformance",
        "filters": f"video=={video_id}",
    }
    try:
        analytics = build(
            "youtubeAnalytics", "v2", credentials=credentials, cache_discovery=False
        )
        response = analytics.reports().query(**params).execute()
    except HttpError as exc:
        status, reason, activation_url = _http_hata_ayrintisi(exc)
        print(f"YouTube Analytics API hatasi: HTTP {status} - {reason}")
        content_text = (
            exc.content.decode("utf-8", errors="replace")
            if isinstance(exc.content, bytes)
            else str(exc.content)
        )
        if reason in {"accessNotConfigured", "SERVICE_DISABLED"} or any(
            marker in content_text for marker in ("accessNotConfigured", "SERVICE_DISABLED")
        ):
            print(
                "YouTube Analytics API, OAuth istemcisinin Google Cloud projesinde "
                "etkinlestirilmelidir."
            )
            if activation_url:
                print(f"Etkinlestirme adresi: {activation_url}")
        return False
    rows = response.get("rows") or []
    print(f"Retention satir sayisi: {len(rows)}")
    print("Ilk 3 satir:")
    print(json.dumps(rows[:3], ensure_ascii=False))
    return True


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Kanal bazli salt okunur YouTube Analytics yetkisi al ve dogrula."
    )
    parser.add_argument("--kanal", required=True, help="config/audience_channels.json kanal adi")
    parser.add_argument("--client-secret", help="Desktop OAuth client JSON dosyasi")
    parser.add_argument("--probe-video", metavar="VIDEO_ID", help="Retention raporunu dene")
    parser.add_argument(
        "--kontrol",
        action="store_true",
        help="Tarayici acmadan kayitli token'i yenile ve kanal kimligini dogrula",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        channels = kanallari_yukle()
        if args.kanal not in channels:
            known = ", ".join(sorted(channels))
            raise KullaniciHatasi(
                f"Bilinmeyen kanal: {args.kanal}. Gecerli kanallar: {known}"
            )
        channel = channels[args.kanal]
        credentials = (
            kayitli_yetkiyi_yukle(channel)
            if args.kontrol
            else yeni_yetki_al(channel, args.client_secret)
        )

        matched, selected_name, selected_id = kanal_kimligini_dogrula(
            credentials, channel
        )
        if not matched:
            print(
                f"Hata: '{selected_name}' kanali secildi ({selected_id}); "
                f"beklenen '{channel['kanal']}' kanaliydi "
                f"({channel['youtube_channel_id']}). Hicbir dosya kaydedilmedi."
            )
            return 2

        print(
            f"Kanal dogrulandi: {channel['kanal']} ({channel['youtube_channel_id']})"
        )
        if not credentials.refresh_token:
            _yeniden_yetkilendirme_mesaji()
            return 1

        if not args.kontrol:
            path = tokeni_kaydet(credentials, channel)
            print(f"Token yerel dosyaya kaydedildi: {path}")
            relative_path = f"secrets_local/yt_analytics_{channel['kanal']}.json"
            print(f"gh secret set {channel['secret_adi']} < {relative_path}")

        if args.probe_video and not retention_kontrolu(credentials, args.probe_video):
            return 1
        return 0
    except KullaniciHatasi as exc:
        print(f"Hata: {exc}")
        return 1
    except HttpError as exc:
        status, reason, _ = _http_hata_ayrintisi(exc)
        print(f"Google API hatasi: HTTP {status} - {reason}")
        return 1
    except Exception as exc:
        print(f"Beklenmeyen hata ({type(exc).__name__}); hicbir secret degeri yazdirilmadi.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
