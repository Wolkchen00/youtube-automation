"""
Gemini Omni Video — Kie AI mini-dizi üretim API katmanı.

core.kie_api'deki generic create_task / _headers yeniden kullanılır.
Omni'ye özel:
  - register_audio       : özel ses üret (omni/audio/create → kieAudioId)
  - register_character   : karakter kaydet (omni/character/create → characterId)
  - build_omni_payload   : istek gövdesini kur (dry-run için API'siz)
  - generate_omni_shot   : tek çekim üret (create_task → poll)
  - poll_omni_task       : sonucu bekle (video URL + gerçek creditsConsumed)
"""

import json
import random
import time
import requests

from core.kie_api import create_task, _headers, ServerError
from core.config import (
    OMNI_MODEL, OMNI_DEFAULT_RESOLUTION, OMNI_DEFAULT_ASPECT,
    OMNI_VALID_DURATIONS, OMNI_MAX_REF_UNITS,
    KIE_AI_OMNI_AUDIO, KIE_AI_OMNI_CHARACTER, KIE_AI_RECORD_INFO,
    POLL_INTERVAL_VIDEO, POLL_MAX_ATTEMPTS_VIDEO,
    logger,
)


# ─── Doğrulama yardımcıları ────────────────────────────────────────────────────

def validate_duration(duration) -> str:
    """Süreyi geçerli Omni enum'una (4/6/8/10) sabitle. Geçersizse 8'e düşür."""
    d = str(duration).strip()
    if d not in OMNI_VALID_DURATIONS:
        logger.warning(f"⚠️ Geçersiz süre '{duration}' → 8s (geçerli: {OMNI_VALID_DURATIONS})")
        return "8"
    return d


def validate_ref_units(image_urls=None, character_ids=None, video_list=None) -> tuple[bool, int]:
    """7-birim kotasını kontrol et: (görsel) + (video×2) + (karakter) ≤ 7.
    Dönüş: (geçerli_mi, kullanılan_birim)."""
    imgs = len(image_urls or [])
    chars = len(character_ids or [])
    vids = len(video_list or [])
    units = imgs + vids * 2 + chars
    ok = units <= OMNI_MAX_REF_UNITS
    if not ok:
        logger.error(
            f"❌ Referans birimi aşıldı: {imgs} görsel + {vids} video×2 + {chars} karakter "
            f"= {units} > {OMNI_MAX_REF_UNITS}"
        )
    return ok, units


# ─── Özel ses kaydı (omni/audio/create) ────────────────────────────────────────

def register_audio(base_voice: str, name: str,
                   voice_description: str = "", example_dialogue: str = "") -> str | None:
    """Bir preset sesi (base_voice) temel alıp özel ses üret.
    Dönüş: kieAudioId veya None.
    """
    payload = {"audio_id": base_voice, "name": (name or base_voice)[:210]}
    if voice_description:
        payload["voice_description"] = voice_description[:20000]
    if example_dialogue:
        payload["example_dialogue"] = example_dialogue[:120]
    try:
        resp = requests.post(KIE_AI_OMNI_AUDIO, json=payload, headers=_headers(), timeout=30)
        data = resp.json()
        if data.get("code") in (0, 200):
            kid = (data.get("data") or {}).get("kieAudioId")
            logger.info(f"🎙️ Özel ses kaydedildi: {name} → {kid}")
            return kid
        logger.error(f"❌ Ses kaydı hatası (code={data.get('code')}): {data.get('msg')}")
        return None
    except Exception as e:
        logger.error(f"❌ Ses kaydı bağlantı hatası: {e}")
        return None


# ─── Karakter kaydı (omni/character/create) ────────────────────────────────────

def register_character(descriptions: str, image_url, audio_ids: list | None = None,
                       character_name: str | None = None) -> str | None:
    """Karakteri görünüm + (opsiyonel) sesle kaydet → characterId.
    image_url: tek URL veya URL listesi (genelde boydan fotoğraf).
    """
    img_list = [image_url] if isinstance(image_url, str) else list(image_url)
    payload = {"descriptions": descriptions, "image_urls": img_list}
    if audio_ids:
        payload["audio_ids"] = list(audio_ids)[:3]
    if character_name:
        payload["character_name"] = character_name
    try:
        resp = requests.post(KIE_AI_OMNI_CHARACTER, json=payload, headers=_headers(), timeout=30)
        data = resp.json()
        if data.get("code") in (0, 200):
            cid = (data.get("data") or {}).get("characterId")
            logger.info(f"🧍 Karakter kaydedildi: {character_name or '?'} → {cid}")
            return cid
        logger.error(f"❌ Karakter kaydı hatası (code={data.get('code')}): {data.get('msg')}")
        return None
    except Exception as e:
        logger.error(f"❌ Karakter kaydı bağlantı hatası: {e}")
        return None


# ─── Çekim payload'u ───────────────────────────────────────────────────────────

def build_omni_payload(prompt: str, image_urls: list | None = None,
                       audio_ids: list | None = None, character_ids: list | None = None,
                       duration="8", aspect_ratio: str | None = None,
                       resolution: str | None = None, seed=None) -> dict:
    """Gemini Omni Video createTask gövdesini kur (API çağırmadan — dry-run için de kullanılır)."""
    inp = {
        "prompt": prompt,
        "duration": validate_duration(duration),
        "aspect_ratio": aspect_ratio or OMNI_DEFAULT_ASPECT,
        "resolution": resolution or OMNI_DEFAULT_RESOLUTION,
    }
    if image_urls:
        inp["image_urls"] = list(image_urls)
    if audio_ids:
        inp["audio_ids"] = list(audio_ids)[:3]
    if character_ids:
        inp["character_ids"] = list(character_ids)[:3]
    if seed is not None:
        inp["seed"] = int(seed)
    return {"model": OMNI_MODEL, "input": inp}


# ─── Polling ───────────────────────────────────────────────────────────────────

def poll_omni_task(task_id: str, max_attempts: int | None = None) -> dict | None:
    """Omni görevini bekle. Dönüş: {url, credits, raw} veya None.
    core.poll_task'tan farkı: gerçek maliyet (creditsConsumed) da döner.
    """
    attempts = max_attempts or POLL_MAX_ATTEMPTS_VIDEO
    for attempt in range(1, attempts + 1):
        time.sleep(POLL_INTERVAL_VIDEO)
        try:
            resp = requests.get(f"{KIE_AI_RECORD_INFO}?taskId={task_id}",
                                headers=_headers(), timeout=30)
            data = resp.json().get("data", {}) or {}
            state = data.get("state", "unknown")

            if state == "success":
                result_json = data.get("resultJson", "{}")
                result = json.loads(result_json) if isinstance(result_json, str) else (result_json or {})
                urls = result.get("resultUrls", [])
                credits = data.get("creditsConsumed")
                logger.info(f"✅ Omni klip hazır! ({attempt} poll, kredi={credits})")
                return {"url": urls[0] if urls else None, "credits": credits, "raw": data}
            elif state in ("fail", "failed"):
                logger.error(f"❌ Omni başarısız: {data.get('failMsg', '?')}")
                return None
            elif attempt % 5 == 0:
                logger.info(f"⏳ Omni {state} ({attempt}/{attempts})")
        except Exception as e:
            logger.warning(f"⚠️ Omni polling hatası: {e} (deneme {attempt})")

    logger.error(f"❌ Omni zaman aşımı ({attempts} deneme)")
    return None


# ─── Yüksek seviye: tek çekim üret ─────────────────────────────────────────────

def generate_omni_shot(prompt: str, image_urls: list | None = None,
                       audio_ids: list | None = None, character_ids: list | None = None,
                       duration="8", aspect_ratio: str | None = None,
                       resolution: str | None = None, seed=None,
                       max_retry: int = 5) -> dict | None:
    """Tek bir Gemini Omni çekimi üret. Geçici Kie 500 'Internal Error' VE içerik
    filtresi (ör. PROMINENT_PEOPLE) hatalarında otomatik yeniden dener.
    Dönüş: {url, credits, raw} veya None.
    Not: başarısız görevler 0 kredi harcar, bu yüzden yeniden deneme güvenlidir.
    """
    ok, _ = validate_ref_units(image_urls, character_ids)
    if not ok:
        return None
    backoff = [10, 20, 30]
    for attempt in range(1, max_retry + 1):
        # Her denemede TAZE seed: içerik filtresi sabit payload'da hep aynı kareyi üretip
        # hep takılır. Seed değişince farklı kare üretilir → filtreden geçme şansı artar.
        attempt_seed = seed if (seed is not None and attempt == 1) else random.randint(1, 2_000_000_000)
        payload = build_omni_payload(prompt, image_urls, audio_ids, character_ids,
                                     duration, aspect_ratio, resolution, attempt_seed)
        try:
            task_id = create_task(payload)
        except ServerError as e:
            logger.error(f"🚫 Omni create_task sunucu hatası (HTTP 500, geçici): {e}")
            task_id = None
        if task_id:
            result = poll_omni_task(task_id)
            if result and result.get("url"):
                return result
        if attempt < max_retry:
            wait = backoff[min(attempt - 1, len(backoff) - 1)]
            logger.warning(f"⚠️ Omni çekim denemesi {attempt}/{max_retry} başarısız — {wait}s sonra tekrar (seed değişiyor)")
            time.sleep(wait)
    logger.error(f"❌ Omni çekim {max_retry} denemede üretilemedi")
    return None
