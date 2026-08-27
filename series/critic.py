"""
Critic-QC — üretilen her klibin Gemini vision denetimi + otomatik regen (opt-in).

director-studio PLAN §5'in Faz 0 yaması (İhsan şikâyeti: "ters kafa, el-ayak
karışımı hatalar yayına çıkıyor"). Üç adım:
  1. lint_prompt()  — üretimden ÖNCE ücretsiz ön-denetim (kıyafet yazılı mı,
     riskli kompozisyon var mı) → sadece uyarı loglar, prompt'a DOKUNMAZ.
  2. review_clip()  — üretimden SONRA klipten eşit aralıklı kareler çıkarılır,
     Gemini 2.5 Flash vision zorunlu-JSON kararı verir (anatomi / yüz-referans
     eşleşmesi / kıyafet / dönem / gömülü yazı / artifact skoru).
  3. qc_shot()      — RED verilen klip fix_notes'la güçlendirilmiş prompt + yeni
     seed ile otomatik yeniden üretilir (çekim başına maks 2; bölüm başına
     ~çekim_sayısı/2 = PLAN'daki +%50 maliyet tavanı). Hâlâ REDse çekim bölümden
     düşer + Telegram'a kare albümü gider ("elle bak"), bölüm kalanlarla devam eder.

Sözleşmeler:
  • Reddedilen klip ASLA shot_NN.mp4 adıyla diskte bırakılmaz → produce'un
    idempotent "zaten var, atla" yolu QC bilmeden güvenli kalır.
  • Legacy QC/Gemini hatası = "skip" (klip aynen kullanılır). Opt-in zorunlu
    yüz/ham-ses kapıları denetlenemezse fail-closed biçimde RED olur.
  • Her karar seri veri klasörüne (bible.data_dir(slug)/qc_log.jsonl) yazılır (workflow commit'ler)
    → ilk hafta false-positive kalibrasyonu bu logdan yapılır.
Maliyet: denetim <$0.01/video (Gemini Flash); kie'de FAIL görev 0 kredi, regen
yalnız "başarılı-fakat-bozuk" üretimde kredi yakar.
"""

import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import requests

from core.config import GEMINI_API_KEY, logger
from core import ffmpeg_tools
from core.utils import download_file
from .bible import Bible, data_dir, episode_dir

QC_MODEL = "gemini-2.5-flash"
QC_MODEL_FALLBACK = "gemini-flash-latest"

QC_DEFAULTS = {
    "frames": 8,                # klipten örneklenecek kare sayısı
    "artifact_threshold": 6,    # 0-10; bu ve üstü artifact_score = RED
    "max_regens_per_shot": 2,   # çekim başına yeniden üretim hakkı
    "frame_width": 720,         # denetim karesi genişliği (dikeyde 720x1280)
    "qc_review_retries": 2,     # skip sonrası aynı klibi ek denetleme sayısı
    "scene_cut_fail": False,    # measure-only until real-clip calibration is complete
}

QC_REVIEW_RETRY_DELAY = 0.05
QC_HOLD_REASONS = frozenset({"quota", "auth", "server", "parse", "logging"})


class QCApiExhausted(RuntimeError):
    """QC API deneme politikası sonuç vermeden tükendi."""

    def __init__(self, reason: str, detail: str = ""):
        if reason not in QC_HOLD_REASONS:
            raise ValueError(f"bilinmeyen QC hold nedeni: {reason}")
        self.reason = reason
        self.detail = detail
        super().__init__(detail or reason)


def qc_config(bible: Bible) -> dict:
    """Etkinse varsayılanlarla birleşik QC ayarı, değilse {} döndür.
    bible.json → "series" → "qc": {"enabled": true, ...} (diğer opt-in katmanlarla aynı desen)."""
    v = bible.data["series"].get("qc") or {}
    if not (isinstance(v, dict) and v.get("enabled")):
        return {}
    return {**QC_DEFAULTS, **v}


# ─── 1) Ön-denetim (ücretsiz prompt linter) ────────────────────────────────────

_WARDROBE_WORDS = (
    "wearing", "dressed", "clothing", "clothes", "wears", "attire", "garment",
    "tunic", "toga", "robe", "armor", "armour", "uniform", "cloak", "coat",
    "suit", "dress", "vest", "shirt", "trousers", "gown", "chiton", "kaftan",
    "loincloth", "period-appropriate", "period clothing", "costume",
    "jacket", "sweater", "beanie", "boots", "sandals", "hat", "gloves",
    "wetsuit", "parka", "jeans", "outfit",
)

_RISKY_PATTERNS = (
    (r"close[- ]?up[^.]{0,50}\b(hand|hands|finger|fingers)\b",
     "el/parmak yakın planı — anatomi riski yüksek; bel-üstü plan veya 'hands relaxed, below frame' düşün"),
    (r"\b(handshake|shaking hands|holding hands|intertwined fingers)\b",
     "el sıkışma / el ele — parmak karışımı riski"),
    (r"\b(barefoot|bare feet|toes)\b",
     "çıplak ayak — ayak parmağı riski"),
    (r"\b(crowd of|crowded|dozens of people|hundreds of people|many people)\b",
     "kalabalık sahne — çoklu figürde anatomi bozulması riski"),
    (r"\b(fingers|palms)\s+(visible|extended|spread|outstretched)\b",
     "parmak vurgusu — anatomi riski"),
)


def lint_prompt(bible: Bible, shot: dict, prompt: str) -> list[str]:
    """Üretimden önce ücretsiz denetim. Uyarı listesi döndürür (prompt'u DEĞİŞTİRMEZ).
    07 Tem dersi: character_id YÜZÜ kilitler, KIYAFETİ kilitlemez — insanlı çekimde
    kıyafet tarifsiz prompt en sık bozulma kaynağıdır.
    NOT: buraya HAM çekim promptu verilmeli (art_style'sız) — art_style'lar genel
    'clothing' kuralları içerir ve birleşik metinde kıyafet denetimini köreltir."""
    warns: list[str] = []
    p = (prompt or "").lower()
    if shot.get("characters") and not any(w in p for w in _WARDROBE_WORDS):
        warns.append("insanlı çekimde KIYAFET tarifi yok — character_id kıyafeti kilitlemez; "
                     "prompt'a dönem/konsept kıyafetini açıkça yaz")
    for rx, msg in _RISKY_PATTERNS:
        if re.search(rx, p):
            warns.append(f"riskli kompozisyon: {msg}")
    return warns


# ─── Gemini vision yardımcıları ────────────────────────────────────────────────

_QC_SYSTEM = """You are a ruthless quality-control inspector for AI-generated video clips.
You receive frames sampled uniformly in time from ONE generated clip, plus the generation prompt.
If a REFERENCE FACE image is provided it is always the FIRST image and is labeled in the text.

Inspect EVERY frame for AI-generation defects and answer with STRICT JSON only:
{
  "anatomy_ok": bool,          // humans/animals: no extra/missing/fused limbs or fingers, no twisted or backwards heads/necks/joints/torsos, hands and feet natural. true if no living figure appears.
  "face_match": bool | null,   // ONLY when a REFERENCE FACE is provided: is the main character clearly the SAME person in every frame (ignore lighting/expression/period styling)? null if no reference given.
  "wardrobe_ok": bool | null,  // if the prompt states clothing requirements (e.g. period-appropriate dress, no modern items): are they respected? null if the prompt has no clothing requirement or no human appears.
  "era_ok": bool | null,       // if the prompt specifies a historical period or setting: no anachronisms (modern objects, clothing, materials, vehicles, lights)? null if not applicable.
  "unwanted_text": bool,       // burned-in OVERLAY text stamped over the image: captions, subtitles, watermarks, logos, timestamps or UI graphics (overlays are added later in post — the raw clip must contain NONE). Text that exists naturally INSIDE the scene (a sign, an engraving, a book page, a screen that is part of the set) is NOT unwanted unless the prompt explicitly forbids it.
  "forbidden_elements": bool,  // the prompt explicitly forbids elements (e.g. "no people", "no faces", "no text", "no modern objects") and a frame clearly shows one.
  "artifact_score": int,       // 0-10 severity of AI defects across ALL frames judged at the WORST moment: morphing/melting geometry, duplicated or broken objects, impossible physics, glitch frames. 0 = flawless, 10 = unusable.
  "issues": [string],          // short list of concrete problems seen (empty if clean).
  "fix_notes": [string]        // 1-3 short imperative English instructions to append to a REGENERATION prompt to avoid these defects (e.g. "keep the man's head facing forward with a natural neck", "show hands relaxed at his sides, no close-up of fingers"). Empty if clean.
}

Be STRICT on anatomy — a single twisted head, backwards body or six-fingered hand in ANY frame means anatomy_ok=false.
Be TOLERANT of film grain, motion blur, compression, artistic color grading and stylization: they are NOT defects.
Return ONLY the JSON object."""

_NO_FACE_QC_ADDENDUM = """

FACE VISIBILITY GATE (mandatory for this series): add this required field to the same JSON object:
  "face_present": bool       // true when any recognizable human face is visible in any sampled frame, including partial or background faces; false only when every face stays outside the sampled frames.
This field must always be a JSON boolean. Inspect every sampled frame before answering."""

_OBJECT_QC_ADDENDUM = """

OBJECT IDENTITY GATE (mandatory for this series): add these required fields:
  "object_match": bool,
  "object_notes": string
The image labeled [REFERENCE OBJECT] is the episode's physical hero object. Decide
whether the object in every sampled clip frame is that SAME physical object, matching
its shape, colour, scale, material, and distinguishing markings. object_match must
always be a JSON boolean."""

_CONTINUITY_QC_ADDENDUM = """

CROSS-SHOT CONTINUITY GATE (mandatory for this shot): add these required fields:
  "continuity_ok": bool,
  "continuity_notes": string
Compare [PREVIOUS SHOT LAST FRAME] with this shot. Require the same room and surface,
composition, lighting, physical object identity, and a coherent object-state lineage.
continuity_ok must always be a JSON boolean."""

_FIRST_FRAME_QC_ADDENDUM = """

VIEWER-VISIBLE FIRST-FRAME GATE (mandatory for shot 1): add these required fields:
  "first_frame_ok": bool,
  "first_frame_notes": string
Judge [OPENING FRAME] as one standalone frame. The episode's impossible property must
already be active and readable in this exact frame, and the object must fill a large
share of the frame. first_frame_ok must always be a JSON boolean."""


def _parse_json(txt: str):
    """Gemini çıktısını kurtarıcı ayrıştırma (replenish kalıbı): ```json çiti / kırpık uçlar tolere edilir."""
    txt = (txt or "").strip()
    if txt.startswith("```"):
        txt = txt.strip("`")
        nl = txt.find("\n")
        if nl != -1 and txt[:nl].strip().lower() in ("json", ""):
            txt = txt[nl + 1:]
    try:
        return json.loads(txt)
    except Exception:
        i, j = txt.find("{"), txt.rfind("}")
        if i != -1 and j != -1 and j > i:
            return json.loads(txt[i:j + 1])
        raise


def _parse_response_json(response):
    """SDK yanıt metni yoksa bunu da unusable-body/parse olarak sınıflandır."""
    try:
        text = response.text
    except Exception as error:
        raise json.JSONDecodeError("QC response text unavailable", "", 0) from error
    return _parse_json(text or "")


def _classify_api_error(error: Exception) -> str:
    """Gemini/taşıma hatasını dondurulmuş C1 hold sınıflarına indirger."""
    if isinstance(error, json.JSONDecodeError):
        return "parse"
    message = str(error).upper()
    if "429" in message or "RESOURCE_EXHAUSTED" in message:
        return "quota"
    if any(marker in message for marker in (
        "401", "403", "UNAUTHENTICATED", "PERMISSION_DENIED", "API_KEY_INVALID",
        "API KEY", "CREDENTIAL", "FORBIDDEN",
    )):
        return "auth"
    return "server"


def _is_transient_api_error(error: Exception) -> bool:
    message = str(error).upper()
    return any(marker in message for marker in (
        "503", "502", "501", "500", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED",
        "INTERNAL", "DEADLINE", "TIMEOUT", "CONNECTION",
    ))


def _strict_log_event(slug: str, entry: dict, *,
                      experiment_id: str | None = None) -> None:
    """QC olayını append + flush + fsync ile yaz; hiçbir hatayı yutma."""
    path = data_dir(slug) / "qc_log.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {"ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), **entry}
    if experiment_id is not None:
        record["experiment_id"] = experiment_id
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _generate_content_recorded(client, *, model: str, contents, config,
                               slug: str, episode: int | None, shot: int | None,
                               task_type: str, is_fallback: bool,
                               experiment_id: str | None = None):
    """Bir Gemini çağrısını, ücret/kota tüketiminden önce kalıcı olarak kaydet."""
    attempt_id = uuid.uuid4().hex
    try:
        _strict_log_event(slug, {
            "event": "qc_api_attempt",
            "attempt_id": attempt_id,
            "task_type": task_type,
            "model": model,
            "is_fallback": bool(is_fallback),
            "episode": episode,
            "shot": shot,
        }, experiment_id=experiment_id)
    except Exception as error:
        raise QCApiExhausted("logging", str(error)) from error

    try:
        response = client.models.generate_content(
            model=model, contents=contents, config=config
        )
    except Exception as error:
        outcome = "429" if _classify_api_error(error) == "quota" else "error"
        try:
            _strict_log_event(slug, {
                "event": "qc_api_result",
                "attempt_id": attempt_id,
                "outcome": outcome,
            }, experiment_id=experiment_id)
        except Exception as log_error:
            raise QCApiExhausted("logging", str(log_error)) from log_error
        raise

    try:
        _strict_log_event(slug, {
            "event": "qc_api_result",
            "attempt_id": attempt_id,
            "outcome": "ok",
        }, experiment_id=experiment_id)
    except Exception as error:
        raise QCApiExhausted("logging", str(error)) from error
    return response


_REF_IMAGE_CACHE: dict[str, bytes] = {}


def _fetch_ref_face(bible: Bible, shot: dict) -> bytes | None:
    """Çekimdeki İLK karakterin referans yüz görselini indir (koşu boyunca cache'li)."""
    for cid in shot.get("characters", []) or []:
        ch = bible.get_character(cid)
        url = (ch or {}).get("ref_image_url")
        if not url:
            continue
        if url in _REF_IMAGE_CACHE:
            return _REF_IMAGE_CACHE[url]
        try:
            r = requests.get(url, timeout=30)
            if r.ok and r.content:
                _REF_IMAGE_CACHE[url] = r.content
                return r.content
        except Exception as e:
            logger.warning(f"⚠️ QC: referans yüz indirilemedi ({e}) — face_match denetimsiz")
        return None
    return None


def fetch_object_reference(plan: dict) -> bytes | None:
    """Download ``prop_ref_urls[0]`` once and return the exact reviewer bytes."""
    urls = plan.get("prop_ref_urls")
    url = urls[0] if isinstance(urls, list) and urls else None
    if not isinstance(url, str) or not url.strip():
        return None
    if url in _REF_IMAGE_CACHE:
        return _REF_IMAGE_CACHE[url]
    for attempt in range(1, 4):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            content = response.content
            if content:
                _REF_IMAGE_CACHE[url] = content
                return content
            raise ValueError("empty reference image")
        except Exception as error:
            logger.warning(
                f"⚠️ QC: obje referansı indirilemedi ({attempt}/3, {error})"
            )
            if attempt < 3:
                time.sleep(0.25 * attempt)
    return None


def _image_mime(data: bytes) -> str:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "image/webp"
    return "image/jpeg"


def _review_frames(frames: list[Path], ref_face: bytes | None,
                   prompt: str, notes: str, max_tries: int = 3,
                   require_no_face: bool = False,
                   object_ref: bytes | None = None,
                   previous_frame: Path | None = None,
                   opening_frame: Path | None = None,
                   require_object_match: bool = False,
                   require_continuity: bool = False,
                   require_first_frame: bool = False, *,
                   anomaly_descriptor: str | None = None,
                   violation_observation: str | None = None,
                   state_carry_expected: str | None = None,
                   slug: str, episode: int | None, shot: int | None,
                   experiment_id: str | None = None) -> dict | None:
    """Send explicitly labeled visual groups to Gemini and parse strict JSON."""
    if not GEMINI_API_KEY:
        raise QCApiExhausted("auth", "GEMINI_API_KEY yok")
    try:
        from google import genai
        from google.genai import types
    except ImportError as error:
        raise QCApiExhausted("server", f"google-genai import edilemedi: {error}") from error

    parts = []
    if ref_face:
        parts.extend((types.Part.from_text(text="[REFERENCE FACE]"),
                      types.Part.from_bytes(data=ref_face, mime_type="image/jpeg")))
    if object_ref:
        parts.extend((types.Part.from_text(text="[REFERENCE OBJECT]"),
                      types.Part.from_bytes(
                          data=object_ref, mime_type=_image_mime(object_ref)
                      )))
    if previous_frame:
        parts.extend((types.Part.from_text(text="[PREVIOUS SHOT LAST FRAME]"),
                      types.Part.from_bytes(data=previous_frame.read_bytes(), mime_type="image/jpeg")))
    if opening_frame:
        parts.extend((types.Part.from_text(text="[OPENING FRAME]"),
                      types.Part.from_bytes(data=opening_frame.read_bytes(), mime_type="image/jpeg")))
    parts.append(types.Part.from_text(text="[SAMPLED CLIP FRAMES IN TIME ORDER]"))
    parts.extend(types.Part.from_bytes(data=frame.read_bytes(), mime_type="image/jpeg")
                 for frame in frames)
    request_text = [
        "Every image group is explicitly labeled. Judge each mandatory gate against its labeled reference.",
        f"GENERATION PROMPT:\n{prompt}",
    ]
    if notes:
        request_text.append(f"CHANNEL-SPECIFIC INSPECTION NOTES:\n{notes}")
    parts.append(types.Part.from_text(text="\n\n".join(request_text)))

    instruction = _QC_SYSTEM
    if require_no_face:
        instruction += _NO_FACE_QC_ADDENDUM
    if require_object_match:
        instruction += _OBJECT_QC_ADDENDUM
    if require_continuity:
        instruction += _CONTINUITY_QC_ADDENDUM
    if require_first_frame:
        instruction += _FIRST_FRAME_QC_ADDENDUM
    if anomaly_descriptor:
        instruction += _anomaly_addendum(anomaly_descriptor)
    if violation_observation:
        instruction += _violation_addendum(violation_observation)
    if state_carry_expected:
        instruction += _state_carry_addendum(state_carry_expected)
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        config = types.GenerateContentConfig(
            system_instruction=instruction,
            response_mime_type="application/json",
            temperature=0.1,
        )
    except Exception as error:
        raise QCApiExhausted(_classify_api_error(error), str(error)) from error
    last_error: Exception | None = None
    last_reason = "server"
    for model_index, model in enumerate((QC_MODEL, QC_MODEL_FALLBACK)):
        for attempt in range(1, max_tries + 1):
            response_received = False
            try:
                response = _generate_content_recorded(
                    client, model=model, contents=parts, config=config,
                    slug=slug, episode=episode, shot=shot, task_type="visual_review",
                    is_fallback=model_index > 0, experiment_id=experiment_id,
                )
                response_received = True
                return _parse_response_json(response)
            except QCApiExhausted:
                raise
            except Exception as error:
                last_error = error
                message = str(error)
                bad_json = response_received
                last_reason = "parse" if bad_json else _classify_api_error(error)
                transient = _is_transient_api_error(error)
                if (transient or bad_json) and attempt < max_tries:
                    time.sleep(3 if bad_json else min(5 * attempt, 15))
                    continue
                logger.warning(f"⚠️ QC {model} başarısız: {message[:120]}")
                break
    logger.warning(f"⚠️ QC denetimi yapılamadı ({last_error})")
    raise QCApiExhausted(last_reason, str(last_error or "bilinmeyen hata"))


# ─── 2) Klip denetimi + karar ──────────────────────────────────────────────────

ROCK_B_FIELDS = ("anomaly_match", "violation_reads", "state_carry_ok")

_RB_LABELS = {
    "anomaly_match": "anomali kimliği",
    "violation_reads": "ihlal okunurluğu",
    "state_carry_ok": "sahne durumu sürekliliği",
}

_RB_SHAPE = """Every field named below is an object with EXACTLY this shape:
  {"value": true|false|null, "visible": true|false, "confidence": 0.0-1.0}
"visible" describes whether the REGION or ACTION that would carry the property is
inside the sampled frames and readable, NOT whether the property is present. If that
region is readable but the property looks wrong or is missing, answer
visible=true and value=false. Use visible=false, value=null ONLY when the region is
out of frame, occluded, too small, or too dark to judge. "confidence" is your certainty
in "value"."""


def _anomaly_addendum(anomaly_descriptor: str) -> str:
    return f"""

ANOMALY IDENTITY FIELD: add this required field:
  "anomaly_match": {{"value": bool|null, "visible": bool, "confidence": number}}
The episode's impossible property must look like this on screen:
{anomaly_descriptor}
Decide whether the sampled frames show that same anomaly, with the same material,
geometry and light signature, in every frame where it is readable.
{_RB_SHAPE}"""


def _violation_addendum(observation: str) -> str:
    return f"""

VIOLATION READABILITY FIELD: add this required field:
  "violation_reads": {{"value": bool|null, "visible": bool, "confidence": number}}
In this shot a viewer should be able to observe exactly this:
{observation}
Judge only the sampled frames, in order. value=true when the frames show that outcome.
{_RB_SHAPE}"""


def _state_carry_addendum(expected: str) -> str:
    return f"""

CARRIED STATE FIELD: add this required field:
  "state_carry_ok": {{"value": bool|null, "visible": bool, "confidence": number}}
The previous shot left this lasting trace, and this shot must still show it:
{expected}
{_RB_SHAPE}"""


def _parse_rb_field(raw) -> tuple | None:
    """ROCK B alanını katı biçimde ayrıştır; şema dışıysa None."""
    if not isinstance(raw, dict):
        return None
    if "value" not in raw or "visible" not in raw:
        return None
    value = raw.get("value")
    visible = raw.get("visible")
    confidence = raw.get("confidence", 1.0)
    if value is not None and type(value) is not bool:
        return None
    if type(visible) is not bool:
        return None
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        return None
    if not 0.0 <= float(confidence) <= 1.0:
        return None
    return value, visible, float(confidence)


def _rb_enforced(qc: dict, field: str) -> bool:
    """Alan terfi etti mi? Varsayılan HAYIR (P7: önce ölçüm, sonra kapı)."""
    enforce = qc.get("enforce")
    return bool(isinstance(enforce, dict) and enforce.get(field))



def _decide(review: dict, qc: dict, has_ref: bool,
            shot_n: int = 1) -> tuple[str, list[str]]:
    reasons: list[str] = []
    unevaluated: list[str] = []
    if review.get("anatomy_ok") is False:
        reasons.append("anatomi bozuk")
    if has_ref and review.get("face_match") is False:
        reasons.append("yüz referansla uyuşmuyor")
    if review.get("wardrobe_ok") is False:
        reasons.append("kıyafet gereksinime aykırı")
    if review.get("era_ok") is False:
        reasons.append("dönem-dışı öğe (anakronizm)")
    if review.get("unwanted_text") is True:
        reasons.append("gömülü yazı/watermark")
    if review.get("forbidden_elements") is True:
        reasons.append("prompt'un yasakladığı öğe görünüyor")
    if qc.get("require_no_face"):
        value = review.get("face_present")
        if type(value) is not bool:
            unevaluated.append("zorunlu yüz görünürlüğü alanı doğrulanamadı")
        elif value:
            reasons.append("örneklenen karelerde insan yüzü görünüyor")
    if qc.get("require_object_match"):
        value = review.get("object_match")
        if type(value) is not bool:
            unevaluated.append("zorunlu obje kimliği alanı doğrulanamadı")
        elif not value:
            reasons.append("obje referansla aynı fiziksel obje değil")
    if qc.get("require_continuity") and 2 <= int(shot_n) <= 4:
        value = review.get("continuity_ok")
        if type(value) is not bool:
            unevaluated.append("zorunlu çekimler arası süreklilik alanı doğrulanamadı")
        elif not value:
            reasons.append("çekimler arası tezgâh, ışık veya obje-durumu sürekliliği bozuk")
    if qc.get("require_first_frame") and int(shot_n) == 1:
        value = review.get("first_frame_ok")
        if type(value) is not bool:
            unevaluated.append("zorunlu açılış karesi alanı doğrulanamadı")
        elif not value:
            reasons.append("izleyici açılış karesinde imkânsız özelliği okuyamıyor")
    # ROCK B alanları: her zaman ÖLÇÜLÜR, yalnız terfi edenler kapı olur (P7).
    for field in qc.get("_rb_requested") or ():
        label = _RB_LABELS.get(field, field)
        parsed = _parse_rb_field(review.get(field))
        if not _rb_enforced(qc, field):
            continue
        if parsed is None:
            unevaluated.append(f"{label} alanı şema dışı ya da eksik")
            continue
        value, visible, confidence = parsed
        if confidence < 0.5:
            unevaluated.append(f"{label}: güven {confidence:.2f} < 0.50")
        elif value is None and visible:
            unevaluated.append(f"{label}: bölge görünür ama karar verilmedi")
        elif value is False and visible:
            reasons.append(f"{label} tutmuyor")

    score = review.get("artifact_score")
    if isinstance(score, (int, float)) and score >= qc["artifact_threshold"]:
        reasons.append(f"artifact skoru {score}/10 (eşik {qc['artifact_threshold']})")
    if unevaluated:
        return "hold", [*reasons, *unevaluated]
    return ("fail" if reasons else "pass"), reasons


def review_clip(bible: Bible, shot: dict, clip_path: Path, prompt: str,
                 qc: dict, *, object_ref: bytes | None = None,
                 previous_frame: Path | None = None,
                 opening_frame: Path | None = None,
                 episode: int | None = None,
                 experiment_id: str | None = None,
                 api_fail_closed: bool = False,
                 anomaly_descriptor: str | None = None,
                 violation_observation: str | None = None,
                 state_carry_expected: str | None = None,
                 ) -> tuple[dict | None, str, list[str], list[Path]]:
    clip_path = Path(clip_path)
    shot_n = int(shot.get("n") or 0)
    if episode is None:
        episode = qc.get("_api_episode")
    if experiment_id is None:
        experiment_id = qc.get("_api_experiment_id")
    api_fail_closed = bool(api_fail_closed or qc.get("_api_fail_closed"))
    mandatory = bool(
        qc.get("require_no_face") or qc.get("require_object_match")
        or (qc.get("require_continuity") and 2 <= shot_n <= 4)
        or (qc.get("require_first_frame") and shot_n == 1)
    )
    frames = ffmpeg_tools.sample_frames(
        clip_path, count=int(qc["frames"]), width=int(qc["frame_width"]),
        out_dir=clip_path.parent / "qc", prefix=clip_path.stem,
    )
    if not frames:
        return None, ("hold" if mandatory else "skip"), ["denetim karesi çıkarılamadı"], []
    if qc.get("require_object_match") and object_ref is None:
        return None, "hold", ["zorunlu obje referansı indirilemedi"], frames
    if qc.get("require_continuity") and 2 <= shot_n <= 4 and previous_frame is None:
        return None, "hold", ["önceki onaylı çekimin son karesi çıkarılamadı"], frames
    if qc.get("require_first_frame") and shot_n == 1 and opening_frame is None:
        return None, "hold", ["izleyici açılış karesi çıkarılamadı"], frames
    ref_face = (
        _fetch_ref_face(bible, shot)
        if shot.get("characters") and not qc.get("require_no_face") else None
    )
    review = _review_frames(
        frames, ref_face, prompt, str(qc.get("notes") or ""),
        require_no_face=bool(qc.get("require_no_face")),
        object_ref=object_ref, previous_frame=previous_frame,
        opening_frame=opening_frame,
        require_object_match=bool(qc.get("require_object_match")),
        require_continuity=bool(qc.get("require_continuity") and 2 <= shot_n <= 4),
        require_first_frame=bool(qc.get("require_first_frame") and shot_n == 1),
        slug=bible.slug, episode=episode, shot=shot_n,
        experiment_id=experiment_id,
        anomaly_descriptor=anomaly_descriptor,
        violation_observation=violation_observation,
        state_carry_expected=state_carry_expected,
    )
    if review is None:
        if qc.get("require_no_face"):
            reason = "zorunlu yüz görünürlüğü ve diğer QC alanları denetlenemedi"
        elif mandatory:
            reason = "zorunlu QC alanları denetlenemedi"
        else:
            reason = "Gemini denetimi başarısız (klip denetimsiz kabul edildi)"
        return None, ("hold" if mandatory else "skip"), [reason], frames
    if not isinstance(review, dict):
        reason = "QC yanıtı zorunlu JSON nesnesi değil"
        if api_fail_closed:
            raise QCApiExhausted("parse", reason)
        return None, ("hold" if mandatory else "skip"), [reason], frames
    requested = tuple(field for field, wanted in (
        ("anomaly_match", anomaly_descriptor),
        ("violation_reads", violation_observation),
        ("state_carry_ok", state_carry_expected),
    ) if wanted)
    decide_qc = {**qc, "_rb_requested": requested} if requested else qc
    verdict, reasons = _decide(review, decide_qc, ref_face is not None, shot_n)
    return review, verdict, reasons, frames


# ─── 3) Regen döngüsü ──────────────────────────────────────────────────────────

def positive_correction(issue: str) -> str:
    """Turn one issue into one positive imperative without copying negative prose."""
    raw = " ".join(str(issue or "").strip().split())
    lowered = raw.lower()
    if any(word in lowered for word in ("face", "yüz")):
        return ("Frame only the hands, forearms, object, and the surface it rests on, "
                "keeping the face outside the frame.")
    if any(word in lowered for word in ("audio", "music", "speech", "foley", "ses", "müzik")):
        return ("Keep the soundtrack limited to natural foley from the visible hands, "
                "object, material, and surface.")
    if any(word in lowered for word in (
        "object", "obje", "shape", "colour", "color", "scale", "marking", "reference",
    )):
        return ("Match the reference object's exact shape, colour, scale, material, and "
                "distinguishing markings in every frame.")
    if any(word in lowered for word in (
        "continu", "bench", "light", "lineage", "state", "tezg", "sürekl",
    )):
        return ("Continue from the established bench, lighting, object position, and "
                "transformation state shown in the previous shot.")
    if any(word in lowered for word in ("opening", "first frame", "ilk kare", "açılış")):
        return ("Open with the impossible property visibly active and readable as the "
                "object fills most of the frame.")
    if any(word in lowered for word in (
        "anatom", "hand", "finger", "limb", "head", "neck", "parmak", "el ",
    )):
        return ("Render every human figure with natural anatomy, one head, two arms, two "
                "legs, and five fingers on each hand.")
    if any(word in lowered for word in ("text", "watermark", "caption", "logo", "yazı")):
        return "Show a clean workshop image filled only with natural scene detail."
    return "Render a coherent realistic take with stable geometry, lighting, materials, and motion."


def strengthen_prompt(prompt: str, fix_notes: list[str], *,
                      structured: bool = False) -> str:
    """Keep legacy bytes by default; ROCK 3 opts into positive structured rewrites."""
    if not structured:
        notes = [n.strip() for n in (fix_notes or []) if n and n.strip()]
        if not notes:
            notes = ["render all human figures with strictly correct anatomy: one head facing "
                     "a natural direction, two arms, two legs, five fingers per hand"]
        block = "CRITICAL CORRECTIONS — the previous take FAILED quality control. You MUST fix:\n" \
                + "\n".join(f"- {note}" for note in notes)
        return f"{prompt.rstrip()}\n\n{block}"
    source = [note for note in (fix_notes or []) if str(note or "").strip()] or ["anatomy"]
    corrections = list(dict.fromkeys(positive_correction(note) for note in source))
    block = "QUALITY TARGETS — render this take with:\n" \
            + "\n".join(f"- {correction}" for correction in corrections)
    return f"{prompt.rstrip()}\n\n{block}"


def _log_event(slug: str, entry: dict, *,
               experiment_id: str | None = None) -> None:
    """QC olayını seri veri klasörüne (data_dir(slug)/qc_log.jsonl) ekle (workflow commit'ler →
    ilk hafta eşik kalibrasyonu bu logdan yapılır). Best-effort."""
    try:
        p = data_dir(slug) / "qc_log.jsonl"
        p.parent.mkdir(parents=True, exist_ok=True)
        entry = {"ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), **entry}
        if experiment_id is not None:
            entry["experiment_id"] = experiment_id
        with open(p, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.warning(f"⚠️ QC log yazılamadı: {e}")


def notify_qc_exhaustion(title: str, episode: int, reason: str,
                         shot: int | None = None, *, blocking: bool = True) -> None:
    """Kota tükenmesini kota-dışı QC arızalarından açıkça ayır.

    blocking=False: seride zorunlu kapı yok, bölüm QC'siz devam ediyor. Sessiz
    geçiş YASAK olduğu için mesaj yine gider ama sonucu doğru anlatır.
    """
    target = f"ep{episode}" + (f" çekim {shot}" if shot is not None else "")
    outcome = ("Bölüm QC HOLD; yayınlanmayacak." if blocking else
               "Seride zorunlu kapı yok: bölüm QC'SİZ devam ediyor, elle bak.")
    if reason == "quota":
        _notify(
            f"🚨 *QC KOTA TÜKENDİ: {title}* {target}\n"
            f"Gemini 429 denemeleri tükendi. {outcome}"
        )
    else:
        _notify(
            f"🚨 *QC KOTA-DIŞI TÜKENME: {title}* {target}\n"
            f"Neden: `{reason}`. {outcome}"
        )


def _api_fail_open(qc: dict) -> bool:
    """Seri, degerlendirilemeyen QC'de ACIK bicimde devam etmeyi secmis mi?

    Varsayilan fail-closed'dur. `qc.api_fail_open` YALNIZ zorunlu kapisi olmayan
    serilerde gecerlidir: ilan edilmis bir kapidan muafiyet satin alinamaz.
    P9 gerekcesi: tek bir Gemini kota tukenmesi, ayri QC anahtari (ROCK C2) hazir
    olmadan canli kanallari birden susturmamali; ama sessizce de gecilmez, alarm gider.
    """
    return bool(qc.get("api_fail_open")) and not _has_mandatory_gate(qc)



def _has_mandatory_gate(qc: dict) -> bool:
    """Seri, değerlendirilemeyen QC'de bölümü durduracak bir kapı ilan etmiş mi?"""
    return bool(
        qc.get("require_no_face") or qc.get("require_object_match")
        or qc.get("require_continuity") or qc.get("require_first_frame")
        or qc.get("native_audio_review")
    )



def allocate_regen_rounds(shots: list[int], spent: float, cap: float,
                          estimate: float, max_per_shot: int) -> list[int]:
    """Pure round-robin allocation: every shot's first token precedes seconds."""
    if estimate <= 0 or cap <= spent or max_per_shot <= 0:
        return []
    tokens = int((float(cap) - float(spent)) // float(estimate))
    allocation = []
    ordered = [int(shot) for shot in shots]
    for _round in range(int(max_per_shot)):
        for shot in ordered:
            if len(allocation) >= tokens:
                return allocation
            allocation.append(shot)
    return allocation


class CapAwareRegenAllocator:
    """Conservative two-pass token allocator for the tek-obje format.

    It protects every not-yet-authorized main shot and one first-round regen for
    every not-yet-complete shot before granting surplus second-round tokens.
    """

    def __init__(self, hard_cap, estimates: dict[int, float], max_per_shot: int):
        self.hard_cap = hard_cap
        self.estimates = {int(key): float(value) for key, value in estimates.items()}
        self.max_per_shot = max(0, int(max_per_shot))
        self._main_authorized: set[int] = set()
        self._complete: set[int] = set()
        self._granted = {shot: 0 for shot in self.estimates}

    def mark_main_authorized(self, shot: int) -> None:
        self._main_authorized.add(int(shot))

    def mark_complete(self, shot: int) -> None:
        self._complete.add(int(shot))

    def request(self, shot: int, _attempt: int | None = None) -> bool:
        shot = int(shot)
        estimate = self.estimates.get(shot)
        used = self._granted.get(shot, 0)
        requested_round = used + 1 if _attempt is None else int(_attempt)
        if (estimate is None or used >= self.max_per_shot
                or requested_round != used + 1):
            return False
        remaining = self.hard_cap.remaining
        if remaining is None:
            return False
        protected_main = sum(
            value for candidate, value in self.estimates.items()
            if candidate not in self._main_authorized
        )
        protected_first_round = 0.0
        if requested_round >= 2:
            protected_first_round = sum(
                value for candidate, value in self.estimates.items()
                if candidate != shot and candidate not in self._complete
                and self._granted.get(candidate, 0) == 0
            )
        if remaining + 1e-9 < estimate + protected_main + protected_first_round:
            return False
        self._granted[shot] = self._granted.get(shot, 0) + 1
        return True


def content_sha256(path: str | Path) -> str | None:
    try:
        digest = hashlib.sha256()
        with open(path, "rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return None


def qc_pass_exists(slug: str, episode: int, shot: int,
                   content_hash: str | None, qc: dict | None = None, *,
                   experiment_id: str | None = None) -> bool:
    """Return whether this exact clip passed every currently enabled QC gate."""
    if not content_hash:
        return False
    try:
        lines = (data_dir(slug) / "qc_log.jsonl").read_text(encoding="utf-8").splitlines()
    except OSError:
        return False
    for line in reversed(lines):
        try:
            event = json.loads(line)
            if (event.get("event") != "qc_pass"
                    or int(event.get("episode")) != int(episode)
                    or int(event.get("shot")) != int(shot)
                    or event.get("content_sha256") != content_hash
                    or event.get("experiment_id") != experiment_id):
                continue
            required = qc or {}
            if required.get("require_no_face") and event.get("face_present") is not False:
                continue
            if required.get("require_object_match") and event.get("object_match") is not True:
                continue
            if required.get("require_continuity"):
                continuity = event.get("continuity_ok")
                if 2 <= int(shot) <= 4:
                    if continuity is not True:
                        continue
                elif continuity != "n/a":
                    continue
            if required.get("require_first_frame"):
                first_frame = event.get("first_frame_ok")
                if int(shot) == 1:
                    if first_frame is not True:
                        continue
                elif first_frame != "n/a":
                    continue
            return True
        except (TypeError, ValueError, json.JSONDecodeError):
            continue
    return False


def log_scene_cut_scan(slug: str, episode: int, shot: int,
                       clip_path: str | Path, *,
                       experiment_id: str | None = None) -> dict:
    timestamps = ffmpeg_tools.detect_scene_cuts(clip_path, threshold=0.2, height=270)
    event = {
        "event": "scene_cut_scan", "episode": int(episode), "shot": int(shot),
        "threshold": 0.2, "height": 270,
        "count": None if timestamps is None else len(timestamps),
        "timestamps": timestamps,
        "status": "measure_error" if timestamps is None else "measured",
        "gated": False,
        "clip": Path(clip_path).name,
    }
    _log_event(slug, event, experiment_id=experiment_id)
    return event


def _clean_sidecars(clip_path: Path) -> None:
    """Regen öncesi eski klibin türev dosyalarını sil — bayat prep/trim/lastframe
    cache'i yeni klibin yerine kurguya girmesin."""
    for suffix in ("_prep.mp4", "_trim.mp4", "_lastframe.png"):
        try:
            side = clip_path.parent / f"{clip_path.stem}{suffix}"
            if side.exists():
                side.unlink()
        except Exception:
            pass


def _notify(msg: str, frames: list[Path] | None = None) -> None:
    """Telegram'a best-effort bildir (token yoksa no-op)."""
    try:
        from series import notifier
        if not notifier.enabled():
            return
        if frames:
            notifier.send_media_group([str(f) for f in frames[:4]], caption=msg)
        else:
            notifier.send_message(msg)
    except Exception as e:
        logger.warning(f"⚠️ QC bildirimi gönderilemedi: {e}")


_AUDIO_QC_SYSTEM = """You are a strict audio quality-control inspector for a construction video.
Listen to the supplied audio and answer with STRICT JSON only:
{
  "has_music": bool,
  "speech": bool,
  "construction_sounds": [string],
  "silent_fraction_estimate": float
}
Set has_music true for any musical score, song, melody, beat, or rhythmic music bed.
List only clearly audible construction or building-work sounds in construction_sounds.
Estimate the fraction of the supplied audio that is effectively silent from 0.0 to 1.0.
Return ONLY the JSON object."""


def _review_audio(audio_path: Path, max_tries: int = 3, *,
                  slug: str, episode: int | None, shot: int | None = None,
                  experiment_id: str | None = None) -> dict | None:
    """Send an extracted audio sample to Gemini using the clip-QC retry/model pattern."""
    if not slug:
        raise QCApiExhausted("logging", "ses QC günlüğü için seri kimliği belirlenemedi")
    if not GEMINI_API_KEY:
        raise QCApiExhausted("auth", "GEMINI_API_KEY yok")
    try:
        from google import genai
        from google.genai import types
    except ImportError as error:
        raise QCApiExhausted("server", f"google-genai import edilemedi: {error}") from error

    try:
        audio = audio_path.read_bytes()
    except OSError as error:
        logger.warning(f"⚠️ Ses QC: geçici mp3 okunamadı ({error})")
        return None
    parts = [
        types.Part.from_bytes(data=audio, mime_type="audio/mpeg"),
        types.Part.from_text(
            text="Inspect this video's first 60 seconds of audio for the required fields."
        ),
    ]
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        cfg = types.GenerateContentConfig(
            system_instruction=_AUDIO_QC_SYSTEM,
            response_mime_type="application/json",
            temperature=0.1,
        )
    except Exception as error:
        raise QCApiExhausted(_classify_api_error(error), str(error)) from error
    last_error: Exception | None = None
    last_reason = "server"
    for model_index, model in enumerate((QC_MODEL, QC_MODEL_FALLBACK)):
        for attempt in range(1, max_tries + 1):
            response_received = False
            try:
                response = _generate_content_recorded(
                    client, model=model, contents=parts, config=cfg,
                    slug=slug, episode=episode, shot=shot,
                    task_type="delivery_audio_review", is_fallback=model_index > 0,
                    experiment_id=experiment_id,
                )
                response_received = True
                return _parse_response_json(response)
            except QCApiExhausted:
                raise
            except Exception as error:
                last_error = error
                message = str(error)
                bad_json = response_received
                last_reason = "parse" if bad_json else _classify_api_error(error)
                transient = _is_transient_api_error(error)
                if (transient or bad_json) and attempt < max_tries:
                    wait = 3 if bad_json else min(5 * attempt, 15)
                    logger.warning(
                        f"⚠️ Ses QC {model} geçici hata ({message[:60]}…) — "
                        f"{wait}s sonra tekrar"
                    )
                    time.sleep(wait)
                    continue
                logger.warning(f"⚠️ Ses QC {model} başarısız: {message[:120]}")
                break
    logger.warning(f"⚠️ Ses QC yapılamadı ({last_error})")
    raise QCApiExhausted(last_reason, str(last_error or "bilinmeyen hata"))


_RAW_AUDIO_QC_SYSTEM = """You are a strict quality-control inspector for raw native audio from one generated video shot.
Listen to the supplied audio and answer with STRICT JSON only:
{
  "has_foley": bool,
  "unwanted_speech": bool,
  "unwanted_music": bool,
  "notes": string
}
Set has_foley true when audible actions in the shot produce natural object, hand, tool, surface, room, or material sounds.
Set unwanted_speech true for any spoken, whispered, sung, or intelligible human voice.
Set unwanted_music true for any musical score, melody, beat, song, or rhythmic music bed.
Use notes for one concise observation. Return ONLY the JSON object."""


def _review_raw_native_audio(audio_path: Path, max_tries: int = 3, *,
                             slug: str, episode: int | None, shot: int | None,
                             experiment_id: str | None = None) -> dict | None:
    """Review one persisted raw WAV stem with the native-audio schema."""
    if not GEMINI_API_KEY:
        raise QCApiExhausted("auth", "GEMINI_API_KEY yok")
    try:
        from google import genai
        from google.genai import types
    except ImportError as error:
        raise QCApiExhausted("server", f"google-genai import edilemedi: {error}") from error

    try:
        audio = audio_path.read_bytes()
    except OSError as error:
        logger.warning(f"⚠️ Ham ses QC: stem okunamadı ({error})")
        return None
    parts = [
        types.Part.from_bytes(data=audio, mime_type="audio/wav"),
        types.Part.from_text(text="Inspect this raw shot-audio stem for every required field."),
    ]
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        cfg = types.GenerateContentConfig(
            system_instruction=_RAW_AUDIO_QC_SYSTEM,
            response_mime_type="application/json",
            temperature=0.1,
        )
    except Exception as error:
        raise QCApiExhausted(_classify_api_error(error), str(error)) from error
    last_error: Exception | None = None
    last_reason = "server"
    for model_index, model in enumerate((QC_MODEL, QC_MODEL_FALLBACK)):
        for attempt in range(1, max_tries + 1):
            response_received = False
            try:
                response = _generate_content_recorded(
                    client, model=model, contents=parts, config=cfg,
                    slug=slug, episode=episode, shot=shot,
                    task_type="native_audio_review", is_fallback=model_index > 0,
                    experiment_id=experiment_id,
                )
                response_received = True
                return _parse_response_json(response)
            except QCApiExhausted:
                raise
            except Exception as error:
                last_error = error
                message = str(error)
                bad_json = response_received
                last_reason = "parse" if bad_json else _classify_api_error(error)
                transient = _is_transient_api_error(error)
                if (transient or bad_json) and attempt < max_tries:
                    wait = 3 if bad_json else min(5 * attempt, 15)
                    logger.warning(
                        f"⚠️ Ham ses QC {model} geçici hata ({message[:60]}…) — "
                        f"{wait}s sonra tekrar"
                    )
                    time.sleep(wait)
                    continue
                logger.warning(f"⚠️ Ham ses QC {model} başarısız: {message[:120]}")
                break
    logger.warning(f"⚠️ Ham ses QC yapılamadı ({last_error})")
    raise QCApiExhausted(last_reason, str(last_error or "bilinmeyen hata"))


def review_raw_native_audio(bible: Bible, shot: dict, clip_path: Path,
                            episode: int, attempt: int, *,
                            output_dir: str | Path | None = None,
                            experiment_id: str | None = None) -> tuple[
                                dict | None, str, list[str], Path | None
                            ]:
    """Persist and review a raw shot stem; unavailable/invalid review fails closed."""
    shot_number = int(shot.get("n") or 0)
    stems = (
        Path(output_dir) / "stems"
        if output_dir is not None else episode_dir(bible.slug, episode) / "stems"
    )
    stem = stems / f"shot_{shot_number:02d}_attempt_{int(attempt):02d}.wav"
    extracted = ffmpeg_tools.extract_audio(clip_path, stem)
    if extracted is None:
        return None, "fail", ["ham native ses stem'i çıkarılamadı"], None

    review = _review_raw_native_audio(
        extracted, slug=bible.slug, episode=episode, shot=shot_number,
        experiment_id=experiment_id,
    )
    valid = (
        isinstance(review, dict)
        and type(review.get("has_foley")) is bool
        and type(review.get("unwanted_speech")) is bool
        and type(review.get("unwanted_music")) is bool
        and isinstance(review.get("notes"), str)
    )
    if not valid:
        raise QCApiExhausted(
            "parse", "ham native ses denetimi zorunlu alanları doğrulamadı"
        )

    normalized = {
        "has_foley": review["has_foley"],
        "unwanted_speech": review["unwanted_speech"],
        "unwanted_music": review["unwanted_music"],
        "notes": review["notes"].strip(),
    }
    reasons: list[str] = []
    if normalized["unwanted_speech"]:
        reasons.append("ham native seste istenmeyen konuşma var")
    if normalized["unwanted_music"]:
        reasons.append("ham native seste istenmeyen müzik var")
    return normalized, ("fail" if reasons else "pass"), reasons, extracted


def _audio_slug(path: Path) -> str | None:
    """Infer output/series/<slug>/... so qc_audio can append the series QC log."""
    parts = path.resolve().parts
    lowered = [part.lower() for part in parts]
    for index in range(len(parts) - 2):
        if lowered[index:index + 2] == ["output", "series"]:
            return parts[index + 2]
    return None


def _log_audio(path: Path, **values) -> None:
    slug = _audio_slug(path)
    if slug:
        _log_event(slug, {"event": "audio", "file": path.name, **values})


def qc_audio(path: str | Path, *, slug: str | None = None,
             episode: int | None = None, shot: int | None = None,
             experiment_id: str | None = None,
             api_fail_closed: bool = False) -> dict | None:
    """Verify the first 60 seconds of delivered audio with strict Gemini JSON."""
    media_path = Path(path)
    journal_slug = slug or _audio_slug(media_path)
    try:
        with tempfile.TemporaryDirectory(prefix="series-audio-qc-") as temp_dir:
            sample = Path(temp_dir) / "sample.mp3"
            result = subprocess.run(
                [
                    "ffmpeg", "-y", "-i", str(media_path), "-t", "60", "-vn",
                    "-ac", "1", "-ar", "16000", "-codec:a", "libmp3lame", str(sample),
                ],
                capture_output=True, check=True, timeout=180,
            )
            if result.returncode != 0 or not sample.exists() or sample.stat().st_size == 0:
                _log_audio(media_path, status="extract_failed")
                return None
            review = _review_audio(
                sample, slug=journal_slug or "", episode=episode, shot=shot,
                experiment_id=experiment_id,
            )
    except QCApiExhausted:
        raise
    except Exception as error:
        logger.warning(f"⚠️ Ses QC örneği çıkarılamadı ({error})")
        _log_audio(media_path, status="extract_failed")
        return None

    valid = (
        isinstance(review, dict)
        and type(review.get("has_music")) is bool
        and type(review.get("speech")) is bool
        and isinstance(review.get("construction_sounds"), list)
        and all(isinstance(item, str) for item in review["construction_sounds"])
        and isinstance(review.get("silent_fraction_estimate"), (int, float))
        and not isinstance(review.get("silent_fraction_estimate"), bool)
        and 0.0 <= review["silent_fraction_estimate"] <= 1.0
    )
    if not valid:
        logger.warning("⚠️ Ses QC zorunlu JSON alanları geçersiz")
        _log_audio(media_path, status="invalid_json")
        if api_fail_closed:
            raise QCApiExhausted("parse", "ses QC zorunlu JSON alanları geçersiz")
        return None

    normalized = {
        "has_music": review["has_music"],
        "speech": review["speech"],
        "construction_sounds": review["construction_sounds"],
        "silent_fraction_estimate": float(review["silent_fraction_estimate"]),
    }
    _log_audio(media_path, status="ok", **normalized)
    return normalized


def qc_shot(bible: Bible, shot: dict, clip_path: Path, prompt: str,
             regen_fn, episode: int, budget: dict, *,
             object_ref: bytes | None = None,
             previous_clip: str | Path | None = None,
             experiment_id: str | None = None,
             anomaly_descriptor: str | None = None,
             state_carry_expected: str | None = None,
             ) -> tuple[Path | None, float, str]:
    """Review and optionally regenerate one clip.

    ``hold`` means a mandatory gate could not be evaluated.  A confident ``fail``
    may regenerate; a hold never spends another credit and never enters assembly.
    """
    qc = qc_config(bible)
    if not qc:
        return Path(clip_path), 0.0, "pass"
    clip_path = Path(clip_path)
    slug, n = bible.slug, int(shot.get("n") or 0)
    budget.pop("hold_reason", None)
    extra_credits = 0.0
    all_fix_notes: list[str] = []
    attempt = 0
    current_prompt = prompt
    allocator = budget.get("allocator")
    shot_regen_limit = int(qc["max_regens_per_shot"])
    if not budget.get("dynamic") and "total" in budget and "shot_count" in budget:
        try:
            shot_count = int(budget["shot_count"])
            if shot_count > 0:
                fair_share = max(1, int(budget["total"]) // shot_count)
                shot_regen_limit = min(shot_regen_limit, fair_share)
        except (TypeError, ValueError):
            pass

    previous_frame = None
    if qc.get("require_continuity") and 2 <= n <= 4 and previous_clip:
        previous_frame = ffmpeg_tools.extract_last_frame(
            previous_clip,
            clip_path.parent / "qc" / f"ep{int(episode):02d}_shot{n - 1:02d}_accepted_last.jpg",
        )

    while True:
        review_try = 0
        review_retries = max(0, int(qc["qc_review_retries"]))
        frames: list[Path] = []
        opening_frame = None
        opening_metrics = None
        if qc.get("require_first_frame") and n == 1:
            opening_frame = ffmpeg_tools.extract_frame_at(
                clip_path, bible.micro_trim,
                clip_path.parent / "qc" / f"{clip_path.stem}_opening_{attempt}.jpg",
                width=int(qc["frame_width"]),
            )
            if opening_frame:
                opening_metrics = ffmpeg_tools.frame_metrics(opening_frame, width=270)

        audio_failure = False
        api_hold_reason = None
        if qc.get("native_audio_review"):
            try:
                review, verdict, reasons, stem = review_raw_native_audio(
                    bible, shot, clip_path, episode, attempt,
                    output_dir=clip_path.parent.parent if experiment_id is not None else None,
                    experiment_id=experiment_id,
                )
            except QCApiExhausted as error:
                review, verdict, stem = None, "hold", None
                reasons = [f"QC API deneme politikası tükendi ({error.reason})"]
                api_hold_reason = error.reason
            if review is None:
                verdict = "hold"
                reasons = [*reasons, "zorunlu ham ses denetimi değerlendirilemedi"]
            if review is not None and review["has_foley"] is False:
                budget["no_foley_count"] = int(budget.get("no_foley_count", 0)) + 1
            _log_event(slug, {
                "event": "native_audio_review", "episode": episode, "shot": n,
                "attempt": attempt, "verdict": verdict, "reasons": reasons,
                "has_foley": (review or {}).get("has_foley"),
                "unwanted_speech": (review or {}).get("unwanted_speech"),
                "unwanted_music": (review or {}).get("unwanted_music"),
                "notes": (review or {}).get("notes"),
                "no_foley_count": int(budget.get("no_foley_count", 0)),
                "stem": stem.name if stem else None,
                "clip": clip_path.name,
            }, experiment_id=experiment_id)
            audio_failure = verdict == "fail"

        audio_hold = bool(qc.get("native_audio_review") and verdict == "hold")
        if not audio_hold and not audio_failure:
            review_qc = {
                **qc,
                "_api_episode": episode,
                "_api_experiment_id": experiment_id,
                "_api_fail_closed": True,
            }
            while True:
                    review_kwargs = {}
                    if qc.get("require_object_match"):
                        review_kwargs["object_ref"] = object_ref
                    if qc.get("require_continuity") and 2 <= n <= 4:
                        review_kwargs["previous_frame"] = previous_frame
                    if qc.get("require_first_frame") and n == 1:
                        review_kwargs["opening_frame"] = opening_frame
                    if anomaly_descriptor:
                        review_kwargs["anomaly_descriptor"] = anomaly_descriptor
                    observation = shot.get("violation_observation")
                    if observation:
                        review_kwargs["violation_observation"] = observation
                    if state_carry_expected:
                        review_kwargs["state_carry_expected"] = state_carry_expected
                    try:
                        review, verdict, reasons, frames = review_clip(
                            bible, shot, clip_path, current_prompt, review_qc,
                            **review_kwargs,
                        )
                    except QCApiExhausted as error:
                        review, frames = None, []
                        verdict = "skip" if _api_fail_open(qc) else "hold"
                        reasons = [f"QC API deneme politikası tükendi ({error.reason})"]
                        api_hold_reason = error.reason
                    mandatory_visual = bool(
                        qc.get("require_no_face")
                        or qc.get("require_object_match")
                        or (qc.get("require_continuity") and 2 <= n <= 4)
                        or (qc.get("require_first_frame") and n == 1)
                    )
                    if mandatory_visual and verdict == "skip":
                        verdict = "hold"
                        reasons = [*reasons, "zorunlu görsel QC değerlendirilemedi"]
                    event = {
                        "event": "review", "episode": episode, "shot": n,
                        "attempt": attempt, "review_try": review_try,
                        "verdict": verdict, "reasons": reasons,
                        "artifact_score": (review or {}).get("artifact_score"),
                        "issues": (review or {}).get("issues"),
                        "fix_notes": (review or {}).get("fix_notes"),
                        "clip": clip_path.name,
                    }
                    for rb_field in ROCK_B_FIELDS:
                        if rb_field in (review or {}):
                            event[rb_field] = (review or {}).get(rb_field)
                    if qc.get("require_no_face"):
                        event["face_present"] = (review or {}).get("face_present")
                    if qc.get("require_object_match"):
                        event["object_match"] = (review or {}).get("object_match")
                        event["object_notes"] = (review or {}).get("object_notes")
                    if qc.get("require_continuity"):
                        event["continuity_ok"] = (
                            (review or {}).get("continuity_ok") if 2 <= n <= 4 else "n/a"
                        )
                        event["continuity_notes"] = (
                            (review or {}).get("continuity_notes") if 2 <= n <= 4 else "n/a"
                        )
                    if qc.get("require_first_frame"):
                        event["first_frame_ok"] = (
                            (review or {}).get("first_frame_ok") if n == 1 else "n/a"
                        )
                        event["first_frame_notes"] = (
                            (review or {}).get("first_frame_notes") if n == 1 else "n/a"
                        )
                        event["opening_frame_luma_contrast_proxy"] = (
                            (opening_metrics or {}).get("luma_contrast_proxy") if n == 1 else "n/a"
                        )
                        event["opening_frame_sharpness_proxy"] = (
                            (opening_metrics or {}).get("sharpness_proxy") if n == 1 else "n/a"
                        )
                    _log_event(slug, event, experiment_id=experiment_id)
                    if verdict not in ("skip", "hold") or review_try >= review_retries:
                        break
                    review_try += 1
                    wait = QC_REVIEW_RETRY_DELAY * review_try
                    logger.warning(
                        f"⚠️ QC denetimi sonuçsuz: çekim {n}, aynı klip "
                        f"{wait:.2f}s sonra yeniden denenecek ({review_try}/{review_retries})"
                    )
                    time.sleep(wait)

        if api_hold_reason is not None and verdict == "skip":
            # P9 (filo riski): API tükenmesi HER ZAMAN yüksek sesle raporlanır, ama
            # bölümü yalnız ZORUNLU kapısı olan seride durdurur. Zorunlu kapısı
            # olmayan seriler (bugün from-scratch, event-horizon) eskisi gibi
            # QC'siz devam eder — aksi hâlde tek bir Gemini kota tükenmesi, ayrı QC
            # anahtarı (ROCK C2) hazır olmadan canlı kanalları birden susturur.
            # Sessizlik değil, sesli devam: alarm + defter kaydı aşağıda yazılır.
            if not _api_fail_open(qc):
                verdict = "hold"
                reasons = [*reasons, f"QC API tükenmesi giderilemedi ({api_hold_reason})"]
            else:
                reasons = [*reasons,
                           f"QC API tükenmesi ({api_hold_reason}) — seride zorunlu kapı "
                           f"yok, bölüm QC'siz sürüyor"]
                notify_qc_exhaustion(bible.title, episode, api_hold_reason, n,
                                     blocking=False)
                _log_event(slug, {
                    "event": "qc_api_exhausted_open",
                    "episode": episode, "shot": n, "attempt": attempt,
                    "reason": api_hold_reason, "reasons": reasons,
                    "clip": clip_path.name,
                }, experiment_id=experiment_id)
        if verdict == "hold":
            if api_hold_reason is not None:
                budget["hold_reason"] = api_hold_reason
                notify_qc_exhaustion(bible.title, episode, api_hold_reason, n)
            held = clip_path.parent / f"{clip_path.stem}_qchold{attempt}{clip_path.suffix}"
            try:
                clip_path.replace(held)
            except Exception as error:
                logger.warning(f"⚠️ QC: beklemeye alınan klip taşınamadı ({error})")
            _log_event(slug, {
                "event": "qc_hold", "episode": episode, "shot": n,
                "attempt": attempt, "reason": api_hold_reason,
                "reasons": reasons, "clip": held.name,
            }, experiment_id=experiment_id)
            logger.error(f"⏸️ QC HOLD: çekim {n} zorunlu kapıda değerlendirilemedi")
            return None, extra_credits, "hold"

        if verdict in ("pass", "skip"):
            if verdict == "pass":
                score = (review or {}).get("artifact_score")
                extra = f" (regen {attempt} sonrası)" if attempt else ""
                logger.info(f"🔍 QC GEÇTİ: çekim {n}, artifact {score}/10{extra}")
                pass_event = {
                    "event": "qc_pass", "episode": episode, "shot": n,
                    "attempt": attempt, "content_sha256": content_sha256(clip_path),
                    "clip": clip_path.name,
                }
                if qc.get("require_no_face"):
                    pass_event["face_present"] = (review or {}).get("face_present")
                if qc.get("require_object_match"):
                    pass_event["object_match"] = (review or {}).get("object_match")
                    pass_event["object_notes"] = (review or {}).get("object_notes")
                if qc.get("require_continuity"):
                    pass_event["continuity_ok"] = (
                        (review or {}).get("continuity_ok") if 2 <= n <= 4 else "n/a"
                    )
                    pass_event["continuity_notes"] = (
                        (review or {}).get("continuity_notes") if 2 <= n <= 4 else "n/a"
                    )
                if qc.get("require_first_frame"):
                    pass_event["first_frame_ok"] = (
                        (review or {}).get("first_frame_ok") if n == 1 else "n/a"
                    )
                    pass_event["first_frame_notes"] = (
                        (review or {}).get("first_frame_notes") if n == 1 else "n/a"
                    )
                    pass_event["opening_frame_luma_contrast_proxy"] = (
                        (opening_metrics or {}).get("luma_contrast_proxy") if n == 1 else "n/a"
                    )
                    pass_event["opening_frame_sharpness_proxy"] = (
                        (opening_metrics or {}).get("sharpness_proxy") if n == 1 else "n/a"
                    )
                _log_event(slug, pass_event, experiment_id=experiment_id)
                if attempt:
                    _notify(f"🔍 *{bible.title}* ep{episode} çekim {n}: QC {attempt}. regen'de GEÇTİ "
                            f"(nedenler: {'; '.join(all_fix_notes[:3]) or 'anatomi'}) ✅")
            else:
                reason_text = "; ".join(reasons)
                logger.warning(
                    f"⚠️ QC DENETİMSİZ KABUL: çekim {n}, "
                    f"{review_try + 1} deneme sonuçsuz kaldı; {reason_text}"
                )
                _log_event(slug, {
                    "event": "qc_skip_accepted", "episode": episode, "shot": n,
                    "attempt": attempt, "review_attempts": review_try + 1,
                    "reasons": reasons, "clip": clip_path.name,
                }, experiment_id=experiment_id)
                _notify(
                    f"⚠️ *QC DENETİMSİZ KABUL, {bible.title}* ep{episode} çekim {n}\n"
                    f"{review_try + 1} denetim denemesi sonuçsuz kaldı. "
                    f"Klip RED almadığı için kabul edildi. Neden: {reason_text}",
                    frames=frames,
                )
            if allocator is not None:
                allocator.mark_complete(n)
            return clip_path, extra_credits, verdict

        logger.warning(f"🔍 QC RED: çekim {n} (deneme {attempt}): {'; '.join(reasons)}")
        if audio_failure:
            current_fix_notes = [
                "Keep the soundtrack limited to natural foley from the visible hands, "
                "object, material, and surface."
            ]
        elif qc.get("require_no_face") and (review or {}).get("face_present") is True:
            current_fix_notes = [
                "Frame only the hands, forearms, object, and the surface it rests on, "
                "keeping the face outside the frame."
            ]
        else:
            current_fix_notes = (review or {}).get("fix_notes") or reasons
        all_fix_notes.extend(current_fix_notes)

        can_regen = (regen_fn is not None
                     and attempt < shot_regen_limit
                     and budget.get("left", 0) > 0)
        if can_regen and allocator is not None:
            can_regen = allocator.request(n, attempt + 1)
        rejected = clip_path.parent / f"{clip_path.stem}_qcfail{attempt}{clip_path.suffix}"
        try:
            clip_path.replace(rejected)
        except Exception as error:
            logger.warning(f"⚠️ QC: reddedilen klip taşınamadı ({error})")

        if not can_regen:
            why = ("regen hakkı bitti" if regen_fn is not None and budget.get("left", 0) <= 0
                   else "çekim adil payı doldu"
                   if regen_fn is not None and shot_regen_limit < int(qc["max_regens_per_shot"])
                   else "dinamik kredi payı doldu" if allocator is not None
                   else "çekim regen limiti doldu" if regen_fn is not None else "regen kapalı")
            logger.error(f"❌ QC: çekim {n} eşiği geçemedi ({why}) — çekim bölümden düşürüldü, ELLE BAK")
            _log_event(slug, {"event": "final_reject", "episode": episode, "shot": n,
                              "attempts": attempt, "reasons": reasons},
                       experiment_id=experiment_id)
            _notify(f"🔍❌ *QC RED — {bible.title}* ep{episode} çekim {n}\n"
                    f"Nedenler: {'; '.join(reasons)}\n"
                    f"{attempt} regen denendi, eşik geçilemedi → çekim bölümden ÇIKARILDI. "
                    f"Bölüm kalan çekimlerle hazırlanıyor — yayın öncesi elle bak.",
                    frames=frames)
            return None, extra_credits, "fail"

        budget["left"] -= 1
        attempt += 1
        current_prompt = strengthen_prompt(
            prompt, all_fix_notes,
            structured=bool(qc.get("structured_positive_corrections")),
        )
        logger.info(f"♻️ QC regen {attempt}/{shot_regen_limit}: çekim {n} "
                    f"yapılandırılmış olumlu prompt ile yeniden üretiliyor "
                    f"(bölüm hakkı: {budget['left']})")
        regen_event = {
            "event": "regen", "episode": episode, "shot": n, "attempt": attempt,
        }
        if qc.get("structured_positive_corrections"):
            regen_event["corrections"] = [
                positive_correction(note) for note in all_fix_notes
            ]
        else:
            regen_event["fix_notes"] = list(all_fix_notes)
        _log_event(slug, regen_event, experiment_id=experiment_id)
        _clean_sidecars(clip_path)

        result = None
        try:
            result = regen_fn(current_prompt)
        except Exception as error:
            logger.warning(f"⚠️ QC regen üretimi hata verdi: {error}")
        if result and result.get("credits"):
            extra_credits += float(result["credits"])
        download_kwargs = {"hardened": True} if qc.get("harden_downloads") else {}
        if not (result and result.get("url")
                and download_file(result["url"], clip_path, **download_kwargs)
                and clip_path.exists() and clip_path.stat().st_size > 0):
            logger.error(f"❌ QC regen üretimi başarısız — çekim {n} bölümden düşürüldü, ELLE BAK")
            _log_event(slug, {"event": "regen_failed", "episode": episode, "shot": n,
                              "attempt": attempt}, experiment_id=experiment_id)
            _notify(f"🔍❌ *QC — {bible.title}* ep{episode} çekim {n}: klip QC'den geçemedi ve "
                    f"yeniden üretim de başarısız → çekim bölümden ÇIKARILDI (elle bak).",
                    frames=frames)
            return None, extra_credits, "fail"
