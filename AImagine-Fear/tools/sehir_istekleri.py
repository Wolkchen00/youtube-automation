"""Son fear-slide yayinlarindaki sehir isteklerini sayar.

Mevcut rota denetimi iki kanonik kaynagi birlestirir: ``sehir_ekle.SEHIRLER``
degerlerindeki ``sehir`` alanlari ve ``routes/*.md`` dosyalarinin ust bilgi
``DESTINATION`` alanlari. Basit adlar icin normalize edilmis dosya adi da yedektir.

Kullanim:
    python AImagine-Fear/tools/sehir_istekleri.py [--gun 14] [--dry]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs, urlparse

import requests


KOK = Path(__file__).resolve().parent.parent
YT_KOK = KOK.parent
if str(KOK) not in sys.path:
    sys.path.insert(0, str(KOK))
if str(YT_KOK) not in sys.path:
    sys.path.insert(0, str(YT_KOK))

from core.config import (  # noqa: E402
    GEMINI_API_KEY,
    UPLOAD_POST_API_KEY,
    UPLOAD_USERS,
)
from series.performans import _atomic_write_json  # noqa: E402
from tools.sehir_ekle import SEHIRLER  # noqa: E402


DEFTER = KOK / "yayin.jsonl"
ETKILESIM = KOK / "canon" / "ETKILESIM.json"
ROTA_KLASORU = KOK / "routes"
CIKTI = KOK / "veri" / "sehir_istekleri.json"
YORUM_URL = "https://api.upload-post.com/api/uploadposts/comments"
GEMINI_MODEL = "gemini-2.5-flash"  # series/replenish.py ile ayni birincil model
PLATFORMLAR = ("instagram", "youtube", "tiktok")
AZAMI_SAYFA = 5
AZAMI_HTTP = 80
AZAMI_YORUM = 400


class GeminiHatasi(RuntimeError):
    """Cikti dosyasina dokunulmamasi gereken Gemini hatasi."""


def _uyari(mesaj: str) -> None:
    print("UYARI: " + mesaj, file=sys.stderr)


def _zaman(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        result = datetime.fromisoformat(text)
    except ValueError:
        # Upload-Post yorum ornegi: 2026-09-23T23:17:46+0000
        try:
            result = datetime.strptime(text, "%Y-%m-%dT%H:%M:%S%z")
        except ValueError:
            return None
    if result.tzinfo is None:
        result = result.replace(tzinfo=timezone.utc)
    return result.astimezone(timezone.utc)


def _ic_ice_degerler(value: Any, key: str) -> list[Any]:
    bulunan: list[Any] = []
    if isinstance(value, dict):
        if key in value:
            bulunan.append(value[key])
        for child in value.values():
            bulunan.extend(_ic_ice_degerler(child, key))
    elif isinstance(value, list):
        for child in value:
            bulunan.extend(_ic_ice_degerler(child, key))
    return bulunan


def _url_post_id(platform: str, url: str) -> str | None:
    if not isinstance(url, str):
        return None
    parsed = urlparse(url)
    if platform == "youtube":
        if parsed.hostname and parsed.hostname.lower().endswith("youtu.be"):
            return parsed.path.strip("/").split("/")[0] or None
        return (parse_qs(parsed.query).get("v") or [None])[0]
    if platform == "tiktok":
        match = re.search(r"/video/(\d+)(?:[/?#]|$)", parsed.path + "?")
        return match.group(1) if match else None
    # Instagram reel shortcode'u comments API platform_post_id'si degildir.
    return None


def post_id_cikar(platform: str, platform_sonucu: Any) -> str | None:
    """Iki defter kusagini ve gelecekteki dict/list sarmallarini tolere et."""
    for key in ("platform_post_id", "post_id"):
        for value in _ic_ice_degerler(platform_sonucu, key):
            if isinstance(value, (str, int)) and str(value).strip():
                return str(value).strip()
    for key in ("post_url", "url"):
        for value in _ic_ice_degerler(platform_sonucu, key):
            found = _url_post_id(platform, value)
            if found:
                return found
    return None


def yayin_postlari(
    defter_yolu: Path,
    gun: int,
    simdi: datetime,
) -> list[tuple[str, str]]:
    cutoff = simdi.astimezone(timezone.utc) - timedelta(days=gun)
    found: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    try:
        lines = defter_yolu.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except (json.JSONDecodeError, TypeError):
            _uyari("yayin.jsonl satir %d bozuk, atlandi" % number)
            continue
        ts = _zaman(row.get("ts_utc")) if isinstance(row, dict) else None
        if not isinstance(row, dict) or row.get("kullanildi") is not True or ts is None or ts < cutoff:
            continue
        results = row.get("results")
        if not isinstance(results, dict):
            continue
        for platform in PLATFORMLAR:
            post_id = post_id_cikar(platform, results.get(platform))
            key = (platform, post_id or "")
            if post_id and key not in seen:
                seen.add(key)
                found.append((platform, post_id))
    return found


def _response_json(response: Any) -> dict:
    try:
        value = response.json()
    except Exception:
        return {}
    return value if isinstance(value, dict) else {}


def yorumlari_topla(
    posts: list[tuple[str, str]],
    profile: str,
    api_key: str,
    get: Callable[..., Any] | None = None,
) -> tuple[list[dict], int]:
    """Yorumlari topla; donus (yorumlar, HTTP cagri sayisi)."""
    get = get or requests.get
    comments: list[dict] = []
    calls = 0
    tiktok_disabled = False
    stop = False
    for platform, post_id in posts:
        if stop:
            break
        if platform == "tiktok" and tiktok_disabled:
            continue
        after: str | None = None
        seen_comment_ids: set[str] = set()
        for _page in range(AZAMI_SAYFA):
            if calls >= AZAMI_HTTP:
                stop = True
                break
            params = {"user": profile, "platform": platform, "post_id": post_id}
            if after:
                params["after"] = after
            try:
                response = get(
                    YORUM_URL,
                    headers={"Authorization": "Apikey " + api_key},
                    params=params,
                    timeout=30,
                )
            except Exception as exc:
                _uyari("%s %s yorumlari alinamadi: %s" % (platform, post_id, exc))
                break
            calls += 1
            payload = _response_json(response)
            status = getattr(response, "status_code", 200)
            if status == 429:
                _uyari("Upload-Post 429 verdi; eldeki yorumlarla devam ediliyor")
                stop = True
                break
            if platform == "tiktok" and status == 400 and payload.get("error_code") == "tiktok_reconnect_required":
                tiktok_disabled = True
                break
            if status >= 400 or payload.get("success") is False:
                _uyari("%s %s yorum API hatasi (HTTP %s)" % (platform, post_id, status))
                break
            page_comments = payload.get("comments")
            new_comment_ids = 0
            if isinstance(page_comments, list):
                for comment in page_comments:
                    if isinstance(comment, dict):
                        raw_id = comment.get("id") or comment.get("comment_id")
                        comment_id = str(raw_id).strip() if raw_id is not None else ""
                        if comment_id:
                            if comment_id in seen_comment_ids:
                                continue
                            seen_comment_ids.add(comment_id)
                            new_comment_ids += 1
                        tagged = dict(comment)
                        tagged["_platform"] = platform
                        comments.append(tagged)
            if new_comment_ids == 0:
                break
            pagination = payload.get("pagination")
            if not isinstance(pagination, dict) or not pagination.get("has_next"):
                break
            next_cursor = pagination.get("next_cursor")
            if not isinstance(next_cursor, (str, int)) or not str(next_cursor):
                break
            after = str(next_cursor)
    return comments, calls


def _kimlik(comment: dict) -> str:
    """Sayim kimligi: kanal id'si, sonra gorunen yazar/kullanici adi."""
    channel_id = comment.get("author_channel_id")
    if isinstance(channel_id, dict):
        channel_id = channel_id.get("value") or channel_id.get("id")
    if isinstance(channel_id, (str, int)) and str(channel_id).strip():
        return str(channel_id).strip()

    author = comment.get("author")
    if isinstance(author, (str, int)) and str(author).strip():
        return str(author).strip()

    candidates = [
        comment.get("username"),
        comment.get("author_username"),
        comment.get("authorDisplayName"),
        comment.get("author_name"),
        comment.get("authorName"),
        comment.get("author"),
    ]
    for key in ("user", "author"):
        value = comment.get(key)
        if isinstance(value, dict):
            candidates.extend(
                (
                    value.get("username"),
                    value.get("name"),
                    value.get("display_name"),
                    value.get("displayName"),
                )
            )
    snippet = comment.get("snippet")
    if isinstance(snippet, dict):
        candidates.extend((snippet.get("authorDisplayName"), snippet.get("authorChannelId")))
    for value in candidates:
        if isinstance(value, (str, int)) and str(value).strip():
            return str(value).strip()
    return ""


def _kendi_hesap_adi(comment: dict, own_accounts: set[str]) -> bool:
    candidates: list[Any] = [
        comment.get("author"),
        comment.get("username"),
        comment.get("author_username"),
        comment.get("authorDisplayName"),
        comment.get("author_name"),
        comment.get("authorName"),
    ]
    for key in ("user", "author"):
        value = comment.get(key)
        if isinstance(value, dict):
            candidates.extend(
                (
                    value.get("username"),
                    value.get("name"),
                    value.get("display_name"),
                    value.get("displayName"),
                )
            )
    snippet = comment.get("snippet")
    if isinstance(snippet, dict):
        candidates.append(snippet.get("authorDisplayName"))
    return any(
        _hesap_norm(str(value)) in own_accounts
        for value in candidates
        if isinstance(value, (str, int)) and str(value).strip()
    )


def _hesap_norm(value: str) -> str:
    return value.strip().lstrip("@").casefold()


def _yorum_zamani(comment: dict) -> datetime | None:
    for value in (
        comment.get("timestamp"),
        comment.get("published_at"),
        comment.get("publishedAt"),
        comment.get("created_at"),
    ):
        parsed = _zaman(value)
        if parsed is not None:
            return parsed
    snippet = comment.get("snippet")
    if isinstance(snippet, dict):
        return _zaman(snippet.get("publishedAt") or snippet.get("published_at"))
    return None


def etkilesim_oku(path: Path) -> tuple[set[str], set[str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    own = {
        _hesap_norm(value)
        for value in data.get("kendi_hesaplar", [])
        if isinstance(value, str) and value.strip()
    }
    first = {
        value for value in data.get("first_comments", []) if isinstance(value, str)
    }
    return own, first


def yorumlari_hazirla(
    comments: list[dict],
    own_accounts: set[str],
    first_comments: set[str],
) -> list[dict]:
    prepared: list[dict] = []
    seen_ids: set[str] = set()
    for index, comment in enumerate(comments):
        text = comment.get("text")
        if not isinstance(text, str) or not text.strip() or text in first_comments:
            continue
        if _kendi_hesap_adi(comment, own_accounts):
            continue
        identity = _kimlik(comment)
        raw_id = comment.get("id") or comment.get("comment_id")
        comment_id = str(raw_id).strip() if raw_id is not None else ""
        if not comment_id:
            comment_id = "eksik-id-%d" % index
        if comment_id in seen_ids:
            continue
        seen_ids.add(comment_id)
        prepared.append(
            {
                "comment_id": comment_id,
                "text": text,
                "gemini_text": text[:300],
                "identity": identity,
                "platform": str(comment.get("_platform") or ""),
                "timestamp": _yorum_zamani(comment),
            }
        )
    minimum = datetime.min.replace(tzinfo=timezone.utc)
    prepared.sort(key=lambda item: item["timestamp"] or minimum, reverse=True)
    return prepared[:AZAMI_YORUM]


def gemini_sehirleri(comments: list[dict], api_key: str) -> list[dict]:
    if not api_key:
        raise GeminiHatasi("GEMINI_API_KEY tanimli degil")
    from google import genai
    from google.genai import types

    prompt_comments = [
        {"comment_id": item["comment_id"], "text": item["gemini_text"]}
        for item in comments
    ]
    instruction = (
        "Extract a requested city from each social-media comment. Return ONLY a JSON list "
        'of {"comment_id","city","landmark"}. city must be the canonical English city '
        "name, or null when no city is requested. landmark is optional and may be null. "
        "Keep comment_id exactly as supplied; do not invent comments."
    )
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=json.dumps(prompt_comments, ensure_ascii=False),
            config=types.GenerateContentConfig(
                system_instruction=instruction,
                response_mime_type="application/json",
                temperature=0,
            ),
        )
        parsed = json.loads(response.text or "")
    except Exception as exc:
        raise GeminiHatasi("Gemini cagrisi/JSON yaniti basarisiz: %s" % exc) from exc
    if not isinstance(parsed, list):
        raise GeminiHatasi("Gemini yaniti JSON listesi degil")
    valid: list[dict] = []
    for item in parsed:
        if not isinstance(item, dict) or "comment_id" not in item or "city" not in item:
            raise GeminiHatasi("Gemini yanit semasi gecersiz")
        comment_id = item.get("comment_id")
        city = item.get("city")
        landmark = item.get("landmark")
        if not isinstance(comment_id, (str, int)) or not (
            city is None or isinstance(city, str)
        ) or not (landmark is None or isinstance(landmark, str)):
            raise GeminiHatasi("Gemini yanit alan turleri gecersiz")
        valid.append({"comment_id": str(comment_id), "city": city, "landmark": landmark})
    return valid


def _ad_norm(value: str) -> str:
    return "".join(character for character in value.casefold() if character.isalnum())


def mevcut_rota_adlari(routes_dir: Path = ROTA_KLASORU) -> tuple[set[str], list[str]]:
    exact: set[str] = set()
    stems: list[str] = []
    for value in SEHIRLER.values():
        if isinstance(value, dict) and isinstance(value.get("sehir"), str):
            exact.add(_ad_norm(value["sehir"]))
    if not routes_dir.exists():
        return exact, stems
    for path in routes_dir.glob("*.md"):
        if path.name.startswith("_"):
            continue
        stems.append(_ad_norm(path.stem))
        try:
            for line in path.read_text(encoding="utf-8").splitlines()[:20]:
                if line.upper().startswith("DESTINATION:"):
                    exact.add(_ad_norm(line.split(":", 1)[1].strip()))
                    break
        except OSError:
            continue
    return exact, stems


def _rota_var(city: str, route_names: tuple[set[str], list[str]]) -> bool:
    normalized = _ad_norm(city)
    exact, stems = route_names
    if not normalized:
        return False
    if normalized in exact:
        return True
    return len(normalized) >= 5 and any(normalized in stem for stem in stems)


def sonucu_kur(
    comments: list[dict],
    extracted: list[dict],
    gun: int,
    source_post_count: int,
    fetched_comment_count: int,
    now: datetime,
    route_names: tuple[set[str], list[str]] | None = None,
) -> dict:
    by_id = {item["comment_id"]: item for item in comments}
    cities: dict[str, dict] = {}
    for item in extracted:
        comment = by_id.get(item["comment_id"])
        city = item.get("city")
        if comment is None or not isinstance(city, str) or not city.strip():
            continue
        display = city.strip()
        key = display.casefold()
        record = cities.setdefault(
            key,
            {"sehir": display, "users": set(), "comments": set(), "examples": []},
        )
        comment_id = comment["comment_id"]
        if comment_id in record["comments"]:
            continue
        record["comments"].add(comment_id)
        identity_value = comment["identity"]
        identity = _hesap_norm(identity_value) if identity_value else comment_id
        user_key = (comment["platform"], identity)
        example = comment["text"][:140]
        if len(record["examples"]) < 3 and example not in record["examples"]:
            record["examples"].append(example)
        record["users"].add(user_key)
    routes = route_names if route_names is not None else mevcut_rota_adlari()
    rows = [
        {
            "sehir": value["sehir"],
            "kullanici_sayisi": len(value["users"]),
            "yorum_sayisi": len(value["comments"]),
            "ornek_yorumlar": value["examples"],
            "var": _rota_var(value["sehir"], routes),
        }
        for value in cities.values()
    ]
    rows.sort(key=lambda item: (-item["kullanici_sayisi"], item["sehir"]))
    return {
        "guncellendi": now.astimezone(timezone.utc).isoformat(),
        "gun": gun,
        "kaynak_post_sayisi": source_post_count,
        "yorum_sayisi": fetched_comment_count,
        "sayilan_yorum": len(comments),
        "kimlik_notu": "Instagram yorumcu adini vermiyor; Instagram'da her yorum ayri kisi sayilir.",
        "sehirler": rows,
    }


def calistir(
    gun: int = 14,
    *,
    now: datetime | None = None,
    get: Callable[..., Any] | None = None,
    extractor: Callable[[list[dict], str], list[dict]] | None = None,
) -> dict | None:
    if not UPLOAD_POST_API_KEY:
        _uyari("UPLOAD_POST_API_KEY tanimli degil; mevcut dosya korunuyor")
        return None
    if not GEMINI_API_KEY:
        _uyari("GEMINI_API_KEY tanimli degil; mevcut dosya korunuyor")
        return None
    now = now or datetime.now(timezone.utc)
    posts = yayin_postlari(DEFTER, gun, now)
    comments, _calls = yorumlari_topla(
        posts, UPLOAD_USERS["aimagine"], UPLOAD_POST_API_KEY, get=get
    )
    own, first = etkilesim_oku(ETKILESIM)
    prepared = yorumlari_hazirla(comments, own, first)
    if prepared:
        try:
            extracted = (extractor or gemini_sehirleri)(prepared, GEMINI_API_KEY)
        except Exception as exc:
            _uyari(str(exc) + "; mevcut dosya korunuyor")
            return None
    else:
        extracted = []
    result = sonucu_kur(prepared, extracted, gun, len(posts), len(comments), now)
    _atomic_write_json(CIKTI, result)
    for row in result["sehirler"][:10]:
        print("%d\t%s\tvar=%s" % (row["kullanici_sayisi"], row["sehir"], str(row["var"]).lower()))
    return result


def _args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gun", type=int, default=14)
    parser.add_argument("--dry", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        args = _args(argv)
        if args.dry:
            if CIKTI.exists():
                print(CIKTI.read_text(encoding="utf-8"), end="")
            else:
                print("sehir_istekleri.json yok: %s" % CIKTI)
            return 0
        if args.gun <= 0:
            _uyari("--gun pozitif olmali; mevcut dosya korunuyor")
            return 0
        calistir(args.gun)
    except SystemExit as exc:
        # argparse hatasi bile yayin is akisina hata kodu tasimamalidir.
        if exc.code:
            _uyari("gecersiz komut satiri; sayac calistirilmadi")
    except Exception as exc:
        _uyari("sehir istekleri sayaci basarisiz: %s" % exc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
