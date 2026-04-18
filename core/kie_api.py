"""
Kie AI API — Image & Video Generation

Handles async task creation, polling, and result retrieval.
Supports: Nano Banana 2, Kling 3.0, Veo 3.1, GPT Image 1.5
"""

import json
import time
import requests

from .config import (
    KIE_AI_API_KEY,
    KIE_AI_CREATE_TASK, KIE_AI_RECORD_INFO, KIE_AI_CREDIT,
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
        else:
            logger.error(f"❌ Task creation failed: {data}")
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

def create_veo_task(payload: dict) -> str | None:
    """Create Veo 3.1 task (uses separate endpoint)."""
    try:
        resp = requests.post(
            "https://api.kie.ai/api/v1/veo/generate",
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


def poll_veo_task(task_id: str) -> str | None:
    """Poll Veo 3.1 task. Returns video URL or None."""
    for attempt in range(1, POLL_MAX_ATTEMPTS_VIDEO + 1):
        time.sleep(POLL_INTERVAL_VIDEO)
        try:
            resp = requests.get(
                f"https://api.kie.ai/api/v1/veo/record-info?taskId={task_id}",
                headers=_headers(), timeout=30
            )
            data = resp.json().get("data", {})
            state = data.get("state", "unknown")

            if state == "success" or data.get("successFlag") == 1:
                video_url = data.get("video_url")
                if not video_url:
                    result_json = data.get("resultJson", "{}")
                    result = json.loads(result_json) if isinstance(result_json, str) else result_json
                    urls = result.get("resultUrls", [])
                    video_url = urls[0] if urls else None
                if video_url:
                    logger.info(f"✅ Veo video ready! ({attempt} polls)")
                    return video_url
            elif state in ("failed", "fail"):
                logger.error(f"❌ Veo failed: {data.get('failMsg', '?')}")
                return None
            else:
                logger.info(f"⏳ Veo: {state} ({attempt}/{POLL_MAX_ATTEMPTS_VIDEO})")
        except Exception as e:
            logger.warning(f"⚠️ Veo polling error: {e}")

    logger.error("❌ Veo timeout!")
    return None


def generate_veo_video(prompt: str, image_url: str = None, duration: str = "10", model: str = None) -> str | None:
    """Generate video with Veo 3.1. Returns URL or None. Retries with exponential backoff."""
    veo_model = model or CINEMATIC_VIDEO_MODEL
    logger.info(f"  🎬 VEO model: {veo_model}")
    payload = {
        "model": veo_model,
        "prompt": prompt,
        "duration": duration,
        "aspect_ratio": "9:16",
    }
    if image_url:
        payload["image_url"] = image_url

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
        result = poll_veo_task(task_id)
        if result:
            return result
        logger.warning(f"⚠️ Veo video generation failed (attempt {attempt}/{MAX_RETRY})")
        if attempt < MAX_RETRY:
            delay = backoff_delays[min(attempt - 1, len(backoff_delays) - 1)]
            logger.info(f"  ⏳ Waiting {delay}s before retry...")
            time.sleep(delay)
    return None


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


def generate_video(
    prompt: str,
    start_image_url: str = None,
    end_image_url: str = None,
    duration: str = None,
    model: str = None,
    sound: bool = True
) -> str | None:
    """Generate a video clip with Kling 2.6. Returns URL or None.
    Auto-selects image-to-video or text-to-video model based on whether images are provided.
    On server 500 errors, aborts immediately (no retry) so caller can fallback to VEO3.
    """
    # Build image list first to determine model type
    image_urls = []
    if start_image_url:
        image_urls.append(start_image_url)
    if end_image_url:
        image_urls.append(end_image_url)

    # Smart model selection: I2V when images present, T2V otherwise
    if model:
        active_model = model
    elif image_urls:
        active_model = DEFAULT_VIDEO_MODEL       # kling-2.6/image-to-video
    else:
        active_model = DEFAULT_VIDEO_MODEL_T2V   # kling-2.6/text-to-video

    logger.info(f"  🎥 Kling model: {active_model} ({'I2V' if image_urls else 'T2V'})")

    payload = {
        "model": active_model,
        "input": {
            "prompt": prompt,
            "duration": duration or DEFAULT_VIDEO_DURATION,
            "mode": DEFAULT_VIDEO_MODE,
            "aspect_ratio": DEFAULT_ASPECT_RATIO,  # 9:16 vertical
            "sound": sound,
        }
    }

    # Image-to-video: attach start/end frames
    if image_urls:
        payload["input"]["image_urls"] = image_urls
        payload["input"]["multi_shots"] = False

    backoff_delays = [10, 30]  # exponential backoff
    for attempt in range(1, MAX_RETRY + 1):
        try:
            url = generate_and_wait(payload, is_video=True)
            if url:
                return url
        except ServerError:
            logger.error(f"🚫 Kling server 500 — aborting retries (caller should fallback to VEO3)")
            return None  # fast-fail so pipeline can try VEO3
        logger.warning(f"⚠️ Video attempt {attempt} failed.")
        if attempt < MAX_RETRY:
            delay = backoff_delays[min(attempt - 1, len(backoff_delays) - 1)]
            time.sleep(delay)
            payload["input"]["prompt"] = prompt[:200]
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
