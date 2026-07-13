"""
Telegram bildirim + onay katmanı (ihsan_Ai_Bot / @Ihsan357_Ai_bot).

Kimlik bilgileri ortamdan okunur (asla koda gömülmez — repo public):
  TELEGRAM_BOT_TOKEN  — BotFather token'ı (GitHub secret)
  TELEGRAM_CHAT_ID    — İhsan'ın chat id'si (GitHub secret)

Akış: dizi üretilir → request_approval() kareler + "Yayınlansın mı? ✅/❌" yollar →
approver.py getUpdates ile cevabı okuyup yayınlar/atlar.
"""

import os
import json
import requests

from core.env import logger

_API = "https://api.telegram.org/bot{token}/{method}"


def _token() -> str:
    return os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()


def _chat() -> str:
    return os.environ.get("TELEGRAM_CHAT_ID", "").strip()


def enabled() -> bool:
    return bool(_token() and _chat())


def _call(method: str, data: dict | None = None, files: dict | None = None):
    tok = _token()
    if not tok:
        logger.warning("⚠️ TELEGRAM_BOT_TOKEN yok — Telegram adımı atlanıyor")
        return None
    try:
        r = requests.post(_API.format(token=tok, method=method), data=data, files=files, timeout=60)
        j = r.json()
        if not j.get("ok"):
            logger.error(f"❌ Telegram {method} hata: {j.get('description')}")
            return None
        return j.get("result")
    except Exception as e:
        logger.error(f"❌ Telegram {method} bağlantı hatası: {e}")
        return None


def send_message(text: str, reply_markup: dict | None = None, chat_id: str | None = None):
    data = {"chat_id": chat_id or _chat(), "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    return _call("sendMessage", data)


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
        return _call("sendMediaGroup", {"chat_id": _chat(), "media": json.dumps(media)}, files=files)
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
            logger.warning(f"⚠️ Video {size_mb:.0f}MB > 50MB — Telegram sendVideo atlanıyor, karelere düşülecek")
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
        logger.error(f"❌ Telegram sendVideo bağlantı hatası: {e}")
        return None


def request_approval(part_n: int, title: str, video_path: str = None,
                     frame_paths: list = None) -> int | None:
    """Bitmiş VİDEOYU + onay butonlu mesajı gönder. Video gönderilemezse karelere düşer.
    Gönderilen onay mesajının message_id'sini döndürür."""
    sent_video = None
    if video_path:
        sent_video = send_video(video_path, caption=f"🎬 *{title}*\nYeni bölüm hazır — izle ve karar ver.")
    if not sent_video and frame_paths:  # video gidemezse (büyük/hatalı) karelere düş
        send_media_group(frame_paths, caption=f"🎬 *{title}*\nYeni bölüm üretildi (önizleme kareleri).")
    kb = {"inline_keyboard": [[
        {"text": "✅ Yayınla", "callback_data": f"vd:approve:{part_n}"},
        {"text": "❌ Atla", "callback_data": f"vd:reject:{part_n}"},
    ]]}
    res = send_message(f"📺 *Part {part_n}* — 3 platforma yayınlansın mı?", reply_markup=kb)
    return (res or {}).get("message_id")


def get_updates(offset: int | None = None) -> list:
    data = {"timeout": 0, "allowed_updates": json.dumps(["callback_query", "message"])}
    if offset is not None:
        data["offset"] = offset
    return _call("getUpdates", data) or []


def answer_callback(callback_query_id: str, text: str = ""):
    return _call("answerCallbackQuery", {"callback_query_id": callback_query_id, "text": text})


def edit_message_text(message_id: int, text: str, chat_id: str | None = None):
    return _call("editMessageText", {
        "chat_id": chat_id or _chat(), "message_id": message_id,
        "text": text, "parse_mode": "Markdown",
    })


def get_chat_id_from_updates() -> str | None:
    """İlk gelen mesajdaki chat id'yi döndür (kurulum yardımcı)."""
    for u in get_updates():
        msg = u.get("message") or u.get("edited_message") or {}
        cid = (msg.get("chat") or {}).get("id")
        if cid:
            return str(cid)
    return None
