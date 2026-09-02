"""
Telegram bildirim + onay katmanı (ihsan_Ai_Bot / @Ihsan357_Ai_bot).

Kimlik bilgileri ortamdan okunur (asla koda gömülmez ,  repo public):
  TELEGRAM_BOT_TOKEN  ,  BotFather token'ı (GitHub secret)
  TELEGRAM_CHAT_ID    ,  İhsan'ın chat id'si (GitHub secret)

Akış: dizi üretilir → request_approval() kareler + "Yayınlansın mı? ✅/❌" yollar →
approver.py getUpdates ile cevabı okuyup yayınlar/atlar.
"""

import os
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import requests

from core.env import logger

_API = "https://api.telegram.org/bot{token}/{method}"


@dataclass(frozen=True)
class SendResult:
    """Telegram teslim sonucunu ve ham API sonucunu birlikte tasir."""

    delivered: bool
    error: str | None = None
    result: Any = None

    def __bool__(self) -> bool:
        return self.delivered

    @property
    def message_id(self) -> int | None:
        if isinstance(self.result, dict):
            return self.result.get("message_id")
        return None

    def get(self, key: str, default=None):
        """Eski ``send_message(...).get('message_id')`` kullanimini koru."""
        if isinstance(self.result, dict):
            return self.result.get(key, default)
        return default


def _failed(error: str) -> SendResult:
    return SendResult(delivered=False, error=error)


def _token() -> str:
    return os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()


def _chat() -> str:
    return os.environ.get("TELEGRAM_CHAT_ID", "").strip()


def enabled() -> bool:
    return bool(_token() and _chat())


def _call(method: str, data: dict | None = None,
          files: dict | None = None) -> SendResult:
    tok = _token()
    if not tok:
        logger.warning("⚠️ TELEGRAM_BOT_TOKEN yok ,  Telegram adımı atlanıyor")
        return _failed("TELEGRAM_BOT_TOKEN yok")
    try:
        r = requests.post(_API.format(token=tok, method=method), data=data, files=files, timeout=60)
        j = r.json()
        if not j.get("ok"):
            error = str(j.get("description") or f"HTTP {r.status_code}")
            logger.error(f"❌ Telegram {method} hata: {error}")
            return _failed(error)
        return SendResult(delivered=True, result=j.get("result"))
    except Exception as e:
        # Istisna metni istek URL'sini (dolayisiyla bot tokenini) icerebilir.
        error = f"{type(e).__name__}: Telegram baglanti hatasi"
        logger.error(f"❌ Telegram {method} bağlantı hatası ({type(e).__name__})")
        return _failed(error)


def send_message(text: str, reply_markup: dict | None = None,
                 chat_id: str | None = None,
                 parse_mode: str | None = "Markdown") -> SendResult:
    """Metin gonder; sunum mesajlari varsayilan olarak Markdown kullanir."""
    data = {"chat_id": chat_id or _chat(), "text": text}
    if parse_mode is not None:
        data["parse_mode"] = parse_mode
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    return _call("sendMessage", data)


def send_plain_message(text: str, chat_id: str | None = None) -> SendResult:
    """Kritik alarmlari Telegram entity ayrismasi olmadan duz metin gonder."""
    return send_message(text, chat_id=chat_id, parse_mode=None)


def alert_outbox_path(slug: str) -> Path:
    from series.bible import data_dir

    return data_dir(slug) / "alert_outbox.json"


def _read_alert_outbox(slug: str, *, strict: bool = False) -> list[dict]:
    path = alert_outbox_path(slug)
    if not path.exists():
        return []
    try:
        entries = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        error = ValueError(f"Alarm outbox okunamadi: {type(e).__name__}")
        if strict:
            raise error from e
        logger.error(f"❌ '{slug}' alarm outbox gecersiz: {error}")
        return []
    if not isinstance(entries, list) or not all(isinstance(item, dict) for item in entries):
        error = ValueError("Alarm outbox kok degeri liste degil")
        if strict:
            raise error
        logger.error(f"❌ '{slug}' alarm outbox gecersiz: {error}")
        return []
    return entries


def _write_alert_outbox(slug: str, entries: list[dict]) -> None:
    path = alert_outbox_path(slug)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f"{path.name}.tmp-{os.getpid()}")
    try:
        temp.write_text(
            json.dumps(entries, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def enqueue_critical_alert(slug: str, text: str, error: str | None) -> None:
    """Teslim edilemeyen kritik alarmi seri veri dizinine kalici yaz."""
    entries = _read_alert_outbox(slug, strict=True)
    entries.append({
        "ts": datetime.now(timezone.utc).isoformat(),
        "series_slug": slug,
        "text": text,
        "attempt_count": 1,
        "last_error": error or "bilinmeyen Telegram hatasi",
    })
    _write_alert_outbox(slug, entries)


def has_pending_critical_alerts(slug: str) -> bool:
    try:
        return bool(_read_alert_outbox(slug, strict=True))
    except ValueError as e:
        logger.error(f"❌ '{slug}' alarm outbox gecersiz: {e}")
        return True


def drain_critical_alerts(slug: str) -> bool:
    """Outbox'i sirayla yeniden dene; yalniz teslim edilen girdileri kaldir."""
    try:
        entries = _read_alert_outbox(slug, strict=True)
    except ValueError as e:
        logger.error(f"❌ '{slug}' alarm outbox bosaltilamadi: {e}")
        return False
    if not entries:
        return True

    remaining: list[dict] = []
    for entry in entries:
        result = send_plain_message(str(entry.get("text") or ""))
        if result.delivered:
            continue
        updated = dict(entry)
        try:
            attempts = int(updated.get("attempt_count", 0))
        except (TypeError, ValueError):
            attempts = 0
        updated["attempt_count"] = attempts + 1
        updated["last_error"] = result.error or "bilinmeyen Telegram hatasi"
        remaining.append(updated)
    _write_alert_outbox(slug, remaining)
    return not remaining


def send_media_group(photo_paths: list, caption: str = ""):
    """Birden fazla kareyi tek albümde gönder (ilk karede caption)."""
    paths = [p for p in photo_paths if p and os.path.exists(p)][:10]
    if not paths:
        return None
    media, files, handles = [], {}, []
    try:
        for i, p in enumerate(paths):
            key = f"photo{i}"
            m = {"type": "photo", "media": f"attach://{key}"}
            if i == 0 and caption:
                m["caption"] = caption[:1000]
                m["parse_mode"] = "Markdown"
            media.append(m)
            fh = open(p, "rb")
            handles.append(fh)
            files[key] = fh
        return _call("sendMediaGroup", {"chat_id": _chat(), "media": json.dumps(media)}, files=files).result
    finally:
        for fh in handles:
            try:
                fh.close()
            except Exception:
                pass


def send_video(video_path: str, caption: str = "") -> dict | None:
    """Bitmiş videoyu Telegram'a gönder (sendVideo). Bot limiti ~50MB."""
    tok = _token()
    if not tok or not video_path or not os.path.exists(video_path):
        return None
    try:
        size_mb = os.path.getsize(video_path) / (1024 * 1024)
        if size_mb > 49:
            logger.warning(f"⚠️ Video {size_mb:.0f}MB > 50MB ,  Telegram sendVideo atlanıyor, karelere düşülecek")
            return None
        with open(video_path, "rb") as fh:
            files = {"video": (os.path.basename(video_path), fh, "video/mp4")}
            data = {
                "chat_id": _chat(),
                "caption": caption[:1000],
                "parse_mode": "Markdown",
                "supports_streaming": "true",
            }
            r = requests.post(_API.format(token=tok, method="sendVideo"),
                              data=data, files=files, timeout=180)
            j = r.json()
            if not j.get("ok"):
                logger.error(f"❌ Telegram sendVideo hata: {j.get('description')}")
                return None
            logger.info(f"📹 Telegram'a video gönderildi ({size_mb:.1f}MB)")
            return j.get("result")
    except Exception as e:
        # Istisna URL'si bot tokenini icerebilir; yalniz hata sinifini logla.
        logger.error(f"❌ Telegram sendVideo bağlantı hatası ({type(e).__name__})")
        return None


def request_approval(part_n: int, title: str, video_path: str = None,
                     frame_paths: list = None, slug: str = None) -> int | None:
    """Bitmiş VİDEOYU + onay butonlu mesajı gönder. Video gönderilemezse karelere düşer.
    Gönderilen onay mesajının message_id'sini döndürür.

    slug verilirse callback verisi seri-kimlikli yazılır (vd:<slug>:approve:<n>).
    Bu zorunlu: birden çok seri aynı part numarasında onay beklerken slug'sız
    callback tek tıkla TÜM serileri yayınlatabilirdi (2026-07-29 canlı bulgusu)."""
    sent_video = None
    if video_path:
        sent_video = send_video(video_path, caption=f"🎬 *{title}*\nYeni bölüm hazır ,  izle ve karar ver.")
    if not sent_video and frame_paths:  # video gidemezse (büyük/hatalı) karelere düş
        send_media_group(frame_paths, caption=f"🎬 *{title}*\nYeni bölüm üretildi (önizleme kareleri).")
    mid = f"{slug}:" if slug else ""
    kb = {"inline_keyboard": [[
        {"text": "✅ Yayınla", "callback_data": f"vd:{mid}approve:{part_n}"},
        {"text": "❌ Atla", "callback_data": f"vd:{mid}reject:{part_n}"},
    ]]}
    etiket = f"*{slug}* Part {part_n}" if slug else f"*Part {part_n}*"
    res = send_message(f"📺 {etiket} ,  3 platforma yayınlansın mı?", reply_markup=kb)
    return res.message_id


def get_updates(offset: int | None = None) -> list:
    data = {"timeout": 0, "allowed_updates": json.dumps(["callback_query", "message"])}
    if offset is not None:
        data["offset"] = offset
    return _call("getUpdates", data).result or []


def answer_callback(callback_query_id: str, text: str = ""):
    return _call("answerCallbackQuery", {"callback_query_id": callback_query_id, "text": text}).result


def edit_message_text(message_id: int, text: str, chat_id: str | None = None):
    return _call("editMessageText", {
        "chat_id": chat_id or _chat(), "message_id": message_id,
        "text": text, "parse_mode": "Markdown",
    }).result


def get_chat_id_from_updates() -> str | None:
    """İlk gelen mesajdaki chat id'yi döndür (kurulum yardımcı)."""
    for u in get_updates():
        msg = u.get("message") or u.get("edited_message") or {}
        cid = (msg.get("chat") or {}).get("id")
        if cid:
            return str(cid)
    return None
