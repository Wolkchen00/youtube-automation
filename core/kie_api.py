"""
Kie AI API — Image & Video Generation

Handles async task creation, polling, and result retrieval.
Supports: Nano Banana 2, Kling 3.0, Veo 3.1, GPT Image 1.5
"""

import json
import time
import requests

from pathlib import Path
from urllib.parse import urlparse

from . import ffmpeg_tools

from .env import (
    KIE_AI_API_KEY,
    KIE_AI_CREATE_TASK, KIE_AI_RECORD_INFO, KIE_AI_CREDIT, KIE_AI_FILE_UPLOAD,
    DEFAULT_IMAGE_MODEL, DEFAULT_VIDEO_MODEL, DEFAULT_VIDEO_MODEL_T2V, DEFAULT_VIDEO_MODE,
    DEFAULT_ASPECT_RATIO, DEFAULT_RESOLUTION, DEFAULT_OUTPUT_FORMAT,
    DEFAULT_VIDEO_DURATION, CINEMATIC_VIDEO_MODEL,
    POLL_INTERVAL_IMAGE, POLL_INTERVAL_VIDEO,
    POLL_MAX_ATTEMPTS_IMAGE, POLL_MAX_ATTEMPTS_VIDEO,
    MAX_RETRY, logger
)


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {KIE_AI_API_KEY}",
        "Content-Type": "application/json"
    }


# ─── Core Task Functions ──────────────────────────────────────────────────────

def create_task(payload: dict) -> str | None:
    """Create a new Kie AI task. Returns taskId or None.
    Raises ServerError on HTTP 500 to allow callers to fallback fast.
    """
    try:
        resp = requests.post(KIE_AI_CREATE_TASK, json=payload, headers=_headers(), timeout=30)
        data = resp.json()
        if data.get("code") == 200:
            task_id = data["data"]["taskId"]
            logger.info(f"✅ Task created: {task_id}")
            return task_id
        elif data.get("code") == 500:
            logger.error(f"❌ Server 500 error — API is down: {data.get('msg', '')}")
            raise ServerError(f"Kie AI 500: {data.get('msg', '')}")
        elif resp.status_code == 422 or data.get("code") == 422:
            logger.error(f"❌ HTTP 422 — Invalid parameters: {data.get('msg', '')}")
            raise ServerError(f"Kie AI 422: {data.get('msg', '')}")
        else:
            logger.error(f"❌ Task creation failed (code={data.get('code')}): {data}")
            return None
    except ServerError:
        raise  # re-raise so callers can handle
    except Exception as e:
        logger.error(f"❌ API connection error: {e}")
        return None


class ServerError(Exception):
    """Raised when Kie AI returns HTTP 500 — signals callers to fallback to another model."""


def poll_task(task_id: str, is_video: bool = False) -> dict | None:
    """Poll until task completes. Returns {urls, result} or None."""
    interval = POLL_INTERVAL_VIDEO if is_video else POLL_INTERVAL_IMAGE
    max_attempts = POLL_MAX_ATTEMPTS_VIDEO if is_video else POLL_MAX_ATTEMPTS_IMAGE
    task_type = "Video" if is_video else "Image"

    for attempt in range(1, max_attempts + 1):
        time.sleep(interval)
        try:
            resp = requests.get(
                f"{KIE_AI_RECORD_INFO}?taskId={task_id}",
                headers=_headers(), timeout=30
            )
            data = resp.json().get("data", {})
            state = data.get("state", "unknown")

            if state == "success":
                result_json = data.get("resultJson", "{}")
                result = json.loads(result_json) if isinstance(result_json, str) else result_json
                urls = result.get("resultUrls", [])
                logger.info(f"✅ {task_type} succeeded! ({attempt} polls)")
                return {"urls": urls, "result": result}
            elif state in ("failed", "fail"):
                logger.error(f"❌ {task_type} failed: {data.get('failMsg', '?')}")
                return None
            else:
                logger.info(f"⏳ {task_type} {state} ({attempt}/{max_attempts})")
        except Exception as e:
            logger.warning(f"⚠️ Polling error: {e} (attempt {attempt})")

    logger.error(f"❌ {task_type} timeout! ({max_attempts} attempts)")
    return None


def generate_and_wait(payload: dict, is_video: bool = False) -> str | None:
    """Create task → poll → return first result URL."""
    task_id = create_task(payload)
    if not task_id:
        return None
    result = poll_task(task_id, is_video=is_video)
    if result and result.get("urls"):
        return result["urls"][0]
    return None


# ─── Veo 3.1 (Different endpoint) ─────────────────────────────────────────────

VEO_GENERATE_URL = "https://api.kie.ai/api/v1/veo/generate"
VEO_RECORD_INFO_URL = "https://api.kie.ai/api/v1/veo/record-info"
VEO_MODE_TEXT = "TEXT_2_VIDEO"
VEO_MODE_FLF = "FIRST_AND_LAST_FRAMES_2_VIDEO"
VEO_MODE_REFERENCE = "REFERENCE_2_VIDEO"
VEO_GENERATION_TYPES = {VEO_MODE_TEXT, VEO_MODE_FLF, VEO_MODE_REFERENCE}
VEO_MODE_IMAGE_LIMITS = {
    VEO_MODE_TEXT: (0, 0),
    VEO_MODE_FLF: (1, 2),
    VEO_MODE_REFERENCE: (1, 3),
}


class VeoContractError(ValueError):
    """A request cannot be represented by the current Kie Veo contract."""


class VeoDurationError(RuntimeError):
    """A downloaded Veo clip does not have the requested real duration."""


def _https_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def build_veo_payload(prompt: str, *, generation_type: str = VEO_MODE_TEXT,
                      image_urls: list[str] | tuple[str, ...] | None = None,
                      duration: str | int = 8, model: str | None = None,
                      aspect_ratio: str = "9:16",
                      resolution: str = "1080p") -> dict:
    """Build and validate the current generation-mode-aware Kie Veo request."""
    veo_model = model or CINEMATIC_VIDEO_MODEL
    if veo_model not in ("veo3_fast", "veo3", "veo3_lite"):
        raise VeoContractError(f"unsupported Veo model: {veo_model!r}")
    if generation_type not in VEO_GENERATION_TYPES:
        raise VeoContractError(f"unsupported Veo generationType: {generation_type!r}")
    if aspect_ratio not in ("9:16", "16:9"):
        raise VeoContractError(f"unsupported Veo aspectRatio: {aspect_ratio!r}")
    if resolution not in ("720p", "1080p"):
        raise VeoContractError(f"unsupported Veo resolution: {resolution!r}")
    try:
        duration_value = int(duration)
    except (TypeError, ValueError) as error:
        raise VeoContractError(f"invalid Veo duration: {duration!r}") from error
    if duration_value not in (4, 6, 8):
        raise VeoContractError("Veo duration must be one of 4, 6, or 8 seconds")
    if generation_type == VEO_MODE_REFERENCE and duration_value != 8:
        raise VeoContractError("REFERENCE_2_VIDEO has a fixed duration of 8 seconds")

    ordered_urls = list(image_urls or [])
    minimum, maximum = VEO_MODE_IMAGE_LIMITS[generation_type]
    if not minimum <= len(ordered_urls) <= maximum:
        raise VeoContractError(
            f"{generation_type} requires {minimum}-{maximum} imageUrls; "
            f"received {len(ordered_urls)}"
        )
    if any(not _https_url(url) for url in ordered_urls):
        raise VeoContractError("Veo imageUrls must contain only https URLs")

    payload = {
        "model": veo_model,
        "prompt": str(prompt),
        "aspectRatio": aspect_ratio,
        "generationType": generation_type,
        "duration": duration_value,
        "resolution": resolution,
    }
    if ordered_urls:
        # Preserve caller order: FLF uses first then last; reference mode uses
        # the submitted ingredient ordering.
        payload["imageUrls"] = ordered_urls
    return payload

def create_veo_task(payload: dict) -> str | None:
    """Create Veo 3.1 task (uses separate endpoint)."""
    try:
        resp = requests.post(
            VEO_GENERATE_URL,
            json=payload, headers=_headers(), timeout=30
        )
        data = resp.json()
        if data.get("code") == 200:
            task_id = data["data"]["taskId"]
            logger.info(f"✅ Veo task created: {task_id}")
            return task_id
        else:
            logger.error(f"❌ Veo task error: {data}")
            return None
    except Exception as e:
        logger.error(f"❌ Veo connection error: {e}")
        return None


def poll_veo_task(task_id: str, max_attempts: int = None) -> str | None:
    """Poll the current Veo record contract and return its first result URL."""
    attempts = max_attempts or POLL_MAX_ATTEMPTS_VIDEO

    for attempt in range(1, attempts + 1):
        time.sleep(POLL_INTERVAL_VIDEO)
        try:
            resp = requests.get(
                f"{VEO_RECORD_INFO_URL}?taskId={task_id}",
                headers=_headers(), timeout=30
            )
            envelope = resp.json() or {}
            if envelope.get("code") != 200:
                logger.error(f"❌ Veo record-info error: {str(envelope)[:200]}")
                return None
            data = envelope.get("data") or {}
            success_flag = data.get("successFlag")
            if success_flag == 1:
                response = data.get("response") or {}
                urls = response.get("resultUrls") or []
                video_url = urls[0] if urls and isinstance(urls[0], str) else None
                if not video_url:
                    logger.error("❌ Veo success response contains no resultUrls")
                    return None
                credits = response.get("creditsConsumed")
                logger.info(
                    f"✅ Veo video ready! ({attempt} polls, "
                    f"{attempt * POLL_INTERVAL_VIDEO}s, credits={credits})"
                )
                return video_url
            if success_flag in (2, 3):
                logger.error(
                    f"❌ Veo failed (successFlag={success_flag}): "
                    f"{data.get('errorMessage') or data.get('failMsg') or '?'}"
                )
                return None
            if success_flag == 0:
                if attempt % 10 == 0:  # Log every 10th poll to reduce noise
                    logger.info(
                        f"⏳ Veo pending ({attempt}/{attempts}, "
                        f"~{attempt * POLL_INTERVAL_VIDEO}s elapsed)"
                    )
                continue
            logger.error(f"❌ Veo record-info has invalid successFlag: {success_flag!r}")
            return None
        except Exception as e:
            logger.warning(f"⚠️ Veo polling error: {e}")

    logger.error(f"❌ Veo timeout after {attempts * POLL_INTERVAL_VIDEO}s!")
    return None


def generate_veo_video(prompt: str, image_url: str = None,
                       duration: str | int = 8, model: str = None,
                       max_poll_attempts: int = None, *,
                       generation_type: str = VEO_MODE_TEXT,
                       image_urls: list[str] | tuple[str, ...] | None = None,
                       aspect_ratio: str = "9:16",
                       resolution: str = "1080p") -> str | None:
    """Generate a Veo clip using the current mode-aware request contract.

    ``image_url`` remains only as a source-compatible legacy argument.  It is
    ignored in default TEXT_2_VIDEO mode so an old character reference cannot
    accidentally become a first frame.  New callers use ordered ``image_urls``.
    """
    if image_urls is None and image_url and generation_type != VEO_MODE_TEXT:
        image_urls = [image_url]
    elif image_url and generation_type == VEO_MODE_TEXT:
        logger.warning("Legacy Veo image_url ignored in TEXT_2_VIDEO mode")
    payload = build_veo_payload(
        prompt,
        generation_type=generation_type,
        image_urls=image_urls,
        duration=duration,
        model=model,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
    )
    logger.info(
        f"  🎬 VEO model: {payload['model']} "
        f"(mode={payload['generationType']}, duration={payload['duration']}s)"
    )

    backoff_delays = [10, 30]  # exponential backoff: 10s, 30s
    for attempt in range(1, MAX_RETRY + 1):
        task_id = create_veo_task(payload)
        if not task_id:
            logger.warning(f"⚠️ Veo task creation failed (attempt {attempt}/{MAX_RETRY})")
            if attempt < MAX_RETRY:
                delay = backoff_delays[min(attempt - 1, len(backoff_delays) - 1)]
                logger.info(f"  ⏳ Waiting {delay}s before retry...")
                time.sleep(delay)
            continue
        result = poll_veo_task(task_id, max_attempts=max_poll_attempts)
        if result:
            return result
        logger.warning(f"⚠️ Veo video generation failed (attempt {attempt}/{MAX_RETRY})")
        if attempt < MAX_RETRY:
            delay = backoff_delays[min(attempt - 1, len(backoff_delays) - 1)]
            logger.info(f"  ⏳ Waiting {delay}s before retry...")
            time.sleep(delay)
    return None


def assert_veo_flf_duration(video_path: str | Path,
                            requested_duration: float = 6.0,
                            tolerance: float = 0.25) -> float:
    """Return ffprobe duration or reject a non-conforming downloaded FLF clip."""
    measured = float(ffmpeg_tools.get_video_duration(video_path))
    if abs(measured - float(requested_duration)) > float(tolerance):
        message = (
            "Veo FIRST_AND_LAST_FRAMES_2_VIDEO real-duration guard failed: "
            f"requested={float(requested_duration):g}s, measured={measured:g}s, "
            f"tolerance={float(tolerance):g}s, file={Path(video_path)}"
        )
        logger.error(message)
        raise VeoDurationError(message)
    return measured


# ─── High-Level Generation Functions ──────────────────────────────────────────

def generate_image(
    prompt: str,
    reference_url: str = None,
    model: str = None,
    aspect_ratio: str = None
) -> str | None:
    """Generate an image. Returns URL or None."""
    payload = {
        "model": model or DEFAULT_IMAGE_MODEL,
        "input": {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio or DEFAULT_ASPECT_RATIO,
            "resolution": DEFAULT_RESOLUTION,
            "output_format": DEFAULT_OUTPUT_FORMAT,
        }
    }
    if reference_url:
        payload["input"]["image_input"] = [reference_url]

    for attempt in range(1, MAX_RETRY + 1):
        url = generate_and_wait(payload, is_video=False)
        if url:
            return url
        logger.warning(f"⚠️ Image attempt {attempt} failed.")
        if attempt < MAX_RETRY:
            payload["input"]["prompt"] = prompt[:300]
    return None


def _sanitize_kling_duration(duration: str | None) -> str:
    """Sanitize duration to valid Kling 2.6 values: '5' or '10' only.
    Any other value gets rounded to the nearest valid option.
    """
    if not duration:
        return DEFAULT_VIDEO_DURATION  # "10"
    try:
        val = int(float(duration))
    except (ValueError, TypeError):
        return DEFAULT_VIDEO_DURATION
    # Kling 2.6 ONLY accepts "5" or "10" — anything else = 500 error
    if val <= 7:
        return "5"
    return "10"


def generate_video(
    prompt: str,
    start_image_url: str = None,
    end_image_url: str = None,   # DEPRECATED — kept for API compat, always ignored
    duration: str = None,
    model: str = None,
    sound: bool = True
) -> str | None:
    """Generate a video clip with Kling 2.6. Returns URL or None.
    Auto-selects image-to-video or text-to-video model based on whether images are provided.
    CRITICAL: Kling 2.6 I2V only accepts exactly 1 image — end_image_url is IGNORED.
    On server 500 errors, aborts immediately (no retry) so caller can fallback to VEO3.
    """
    if end_image_url:
        logger.info("  ℹ️ end_image_url ignored — Kling 2.6 I2V only accepts 1 image")

    # Smart model selection: I2V when start image present, T2V otherwise
    has_image = bool(start_image_url)
    if model:
        active_model = model
    elif has_image:
        active_model = DEFAULT_VIDEO_MODEL       # kling-2.6/image-to-video
    else:
        active_model = DEFAULT_VIDEO_MODEL_T2V   # kling-2.6/text-to-video

    # CRITICAL: Sanitize duration — Kling 2.6 ONLY accepts "5" or "10"
    safe_duration = _sanitize_kling_duration(duration)
    logger.info(f"  🎥 Kling model: {active_model} ({'I2V' if has_image else 'T2V'}) duration={safe_duration}s")

    payload = {
        "model": active_model,
        "input": {
            "prompt": prompt,
            "duration": safe_duration,
            "mode": DEFAULT_VIDEO_MODE,
            "aspect_ratio": DEFAULT_ASPECT_RATIO,  # 9:16 vertical
            "sound": sound,
        }
    }

    # Image-to-video: attach ONLY the start frame (1 image max)
    if has_image:
        payload["input"]["image_urls"] = [start_image_url]
        payload["input"]["multi_shots"] = False

    backoff_delays = [10, 30]  # exponential backoff
    for attempt in range(1, MAX_RETRY + 1):
        try:
            url = generate_and_wait(payload, is_video=True)
            if url:
                return url
        except ServerError as e:
            logger.error(f"🚫 Kling server error ({e}) — aborting retries (caller should fallback)")
            raise  # re-raise so caller can distinguish 422 vs 500
        logger.warning(f"⚠️ Video attempt {attempt} failed.")
        if attempt < MAX_RETRY:
            delay = backoff_delays[min(attempt - 1, len(backoff_delays) - 1)]
            time.sleep(delay)
            payload["input"]["prompt"] = prompt[:200]
    return None


# ─── Seedance 2.0 Fast (cheap visual engine, native audio, I2V chaining) ──────

def _poll_video_with_credits(task_id: str, max_attempts: int = None) -> dict | None:
    """Poll a generic /jobs task and return {url, urls, credits}.
    Like poll_task but also surfaces the real creditsConsumed for cost logging.
    """
    attempts = max_attempts or POLL_MAX_ATTEMPTS_VIDEO
    for attempt in range(1, attempts + 1):
        time.sleep(POLL_INTERVAL_VIDEO)
        try:
            resp = requests.get(
                f"{KIE_AI_RECORD_INFO}?taskId={task_id}",
                headers=_headers(), timeout=30
            )
            data = resp.json().get("data", {}) or {}
            state = data.get("state", "unknown")
            if state == "success":
                result_json = data.get("resultJson", "{}")
                result = json.loads(result_json) if isinstance(result_json, str) else (result_json or {})
                urls = result.get("resultUrls", [])
                credits = data.get("creditsConsumed")
                logger.info(f"✅ Video ready! ({attempt} polls, credits={credits})")
                return {"url": urls[0] if urls else None, "urls": urls, "credits": credits}
            elif state in ("fail", "failed"):
                logger.error(f"❌ Video failed: {data.get('failMsg', '?')}")
                return None
            elif attempt % 5 == 0:
                logger.info(f"⏳ Video {state} ({attempt}/{attempts})")
        except Exception as e:
            logger.warning(f"⚠️ Polling error: {e} (attempt {attempt})")
    logger.error(f"❌ Video timeout ({attempts} attempts)")
    return None


def generate_seedance_video(
    prompt: str,
    first_frame_url: str = None,
    last_frame_url: str = None,
    duration: str = None,
    aspect_ratio: str = None,
    resolution: str = "720p",
    sound: bool = True,
    model: str = "bytedance/seedance-2-fast",
) -> dict | None:
    """Generate a clip with Seedance 2.0 Fast — cheapest engine with native audio.

    Uses the generic /jobs/createTask endpoint. Supports image-to-video via
    first_frame_url (and optional last_frame_url) — ideal for 'endless journey'
    frame chaining. Seedance duration is an integer 4-15s; resolution 480p/720p.
    Returns {"url": str, "credits": float|None} or None.
    """
    try:
        dur = int(float(duration)) if duration else 8
    except (ValueError, TypeError):
        dur = 8
    dur = max(4, min(15, dur))

    inp = {
        "prompt": prompt[:20000],
        "aspect_ratio": aspect_ratio or DEFAULT_ASPECT_RATIO,
        "resolution": resolution if resolution in ("480p", "720p") else "720p",
        "duration": dur,
        "generate_audio": bool(sound),
    }
    if first_frame_url:
        inp["first_frame_url"] = first_frame_url
    if last_frame_url:
        inp["last_frame_url"] = last_frame_url

    payload = {"model": model, "input": inp}
    backoff_delays = [10, 30]
    for attempt in range(1, MAX_RETRY + 1):
        try:
            task_id = create_task(payload)
        except ServerError as e:
            logger.error(f"🚫 Seedance server error ({e}) — aborting retries")
            task_id = None
        if task_id:
            result = _poll_video_with_credits(task_id)
            if result and result.get("url"):
                return result
        logger.warning(f"⚠️ Seedance attempt {attempt}/{MAX_RETRY} failed.")
        if attempt < MAX_RETRY:
            time.sleep(backoff_delays[min(attempt - 1, len(backoff_delays) - 1)])
            inp["prompt"] = prompt[:300]
    return None


# ─── File Upload (geçici depo) & Topaz 4K Upscale ─────────────────────────────

def upload_file_to_kie(file_path: str | Path, upload_path: str = "videos") -> str | None:
    """Yerel dosyayı Kie'nin geçici deposuna yükle → downloadUrl (3 gün saklanır).

    'URL ister' modellere (ör. topaz/video-upscale) yerel dosya beslemek için.
    Multipart yükleme; Content-Type requests tarafından atanır (elle set etme).
    """
    p = Path(file_path)
    if not p.exists() or p.stat().st_size == 0:
        logger.error(f"❌ Kie upload: dosya yok/boş: {p}")
        return None
    size_mb = p.stat().st_size / (1024 * 1024)
    try:
        with open(p, "rb") as f:
            resp = requests.post(
                KIE_AI_FILE_UPLOAD,
                headers={"Authorization": f"Bearer {KIE_AI_API_KEY}"},
                files={"file": (p.name, f, "video/mp4")},
                data={"uploadPath": upload_path.strip("/"), "fileName": p.name},
                timeout=600,
            )
        data = resp.json()
        payload = data.get("data") or data
        url = payload.get("downloadUrl") or payload.get("fileUrl") or payload.get("file_url")
        if data.get("code") in (0, 200) and url:
            logger.info(f"📤 Kie deposuna yüklendi ({size_mb:.0f}MB): {p.name}")
            return url
        logger.error(f"❌ Kie upload hatası (code={data.get('code')}): {str(data)[:200]}")
        return None
    except Exception as e:
        logger.error(f"❌ Kie upload bağlantı hatası: {e}")
        return None


def generate_topaz_upscale(video_url: str, upscale_factor: str = "2",
                           max_attempts: int = 60) -> dict | None:
    """Topaz Video Upscale (topaz/video-upscale): kareyi yeniden inşa ederek büyütür
    (1080p ×2 → 2160x3840 4K master). Girdi bir URL olmalı — yerel dosya için önce
    upload_file_to_kie. Girdi limiti ~50MB. Başarısız görev kredi harcamaz.
    Ölçülen maliyet: ~8 kredi/sn (2026-07-03 testi: 4sn=32 kredi → 40sn ≈ 320 kredi).
    Dönüş: {"url": str, "credits": float|None} veya None.
    """
    factor = str(upscale_factor)
    if factor not in ("1", "2", "4"):
        logger.warning(f"⚠️ Geçersiz upscale_factor '{upscale_factor}' → '2'")
        factor = "2"
    payload = {
        "model": "topaz/video-upscale",
        "input": {"video_url": video_url, "upscale_factor": factor},
    }
    try:
        task_id = create_task(payload)
    except ServerError as e:
        logger.error(f"🚫 Topaz create_task sunucu hatası: {e}")
        return None
    if not task_id:
        return None
    return _poll_video_with_credits(task_id, max_attempts=max_attempts)


# ─── Suno Music (kie suno-api; ayrı endpoint ailesi) ──────────────────────────

SUNO_GENERATE = "https://api.kie.ai/api/v1/generate"
SUNO_RECORD_INFO = "https://api.kie.ai/api/v1/generate/record-info"
# Suno webhook zorunlu alan ama biz poll ediyoruz — placeholder yeterli.
SUNO_CALLBACK_PLACEHOLDER = "https://example.com/suno-callback"


def generate_suno_music(style_prompt: str, title: str = "Score",
                        model: str = "V5", instrumental: bool = True,
                        max_attempts: int = 40, poll_interval: int = 10) -> dict | None:
    """Suno ile GERÇEK müzik üret (kie suno-api). Dönüş: {"url", "duration"} | None.

    customMode=true + instrumental=true → 'style' alanı türü/ruh halini belirler
    (V4_5+/V5'te 1000 karaktere kadar). Suno ~1-4 dk'lık tam parça üretir; video
    tarafı (mix_background_music) parçayı zaten video boyuna kırpar + fade'ler,
    o yüzden style prompt'u 'parça HEMEN atmosferle başlasın' diye kurulmalı.
    Sonuç 14 gün saklanır → aynı koşuda indirilmeli. Başarısız görev kredi yakmaz.
    """
    payload = {
        "prompt": style_prompt[:2800],
        "style": style_prompt[:950],
        "title": (title or "Score")[:80],
        "customMode": True,
        "instrumental": bool(instrumental),
        "model": model,
        "callBackUrl": SUNO_CALLBACK_PLACEHOLDER,
    }
    try:
        resp = requests.post(SUNO_GENERATE, json=payload, headers=_headers(), timeout=30)
        data = resp.json()
    except Exception as e:
        logger.error(f"❌ Suno bağlantı hatası: {e}")
        return None
    if data.get("code") != 200:
        logger.error(f"❌ Suno görev hatası (code={data.get('code')}): {str(data)[:200]}")
        return None
    task_id = (data.get("data") or {}).get("taskId")
    if not task_id:
        logger.error(f"❌ Suno taskId yok: {str(data)[:200]}")
        return None
    logger.info(f"🎼 Suno görevi oluşturuldu: {task_id}")

    for attempt in range(1, max_attempts + 1):
        time.sleep(poll_interval)
        try:
            r = requests.get(f"{SUNO_RECORD_INFO}?taskId={task_id}",
                             headers=_headers(), timeout=30)
            d = (r.json() or {}).get("data") or {}
            status = str(d.get("status") or "").upper()
            # FIRST_SUCCESS'te ilk parça hazır — beklemeyi kısaltır.
            if status in ("SUCCESS", "FIRST_SUCCESS"):
                tracks = ((d.get("response") or {}).get("sunoData")) or []
                for t in tracks:
                    url = t.get("audioUrl") or t.get("audio_url") or t.get("sourceAudioUrl")
                    if url:
                        dur = t.get("duration")
                        logger.info(f"✅ Suno müzik hazır ({attempt} poll, {dur}s): {t.get('title','')}")
                        return {"url": url, "duration": dur}
                if status == "SUCCESS":
                    logger.error(f"❌ Suno SUCCESS ama audioUrl yok: {str(d)[:200]}")
                    return None
            elif "FAIL" in status or status in ("CREATE_TASK_FAILED", "GENERATE_AUDIO_FAILED",
                                                "SENSITIVE_WORD_ERROR"):
                logger.error(f"❌ Suno başarısız ({status}): {d.get('errorMessage', '?')}")
                return None
            elif attempt % 6 == 0:
                logger.info(f"⏳ Suno {status or 'PENDING'} ({attempt}/{max_attempts})")
        except Exception as e:
            logger.warning(f"⚠️ Suno poll hatası: {e} (deneme {attempt})")
    logger.error(f"❌ Suno zaman aşımı ({max_attempts * poll_interval}s)")
    return None


# ─── Credit Check ─────────────────────────────────────────────────────────────

def check_credit() -> dict | None:
    """Query Kie AI credit balance."""
    try:
        resp = requests.get(KIE_AI_CREDIT, headers=_headers(), timeout=15)
        data = resp.json()
        if data.get("code") == 200:
            credit_data = data.get("data", {})
            logger.info(f"💰 Credit info: {credit_data}")
            return credit_data
        else:
            logger.warning(f"⚠️ Credit query failed: {data}")
            return None
    except Exception as e:
        logger.error(f"❌ Credit check error: {e}")
        return None
