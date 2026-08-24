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

import json
import re
import subprocess
import tempfile
import time
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
}

QC_REVIEW_RETRY_DELAY = 0.05


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


def _review_frames(frames: list[Path], ref_face: bytes | None,
                   prompt: str, notes: str, max_tries: int = 3,
                   require_no_face: bool = False) -> dict | None:
    """Kareleri Gemini vision'a ver → zorunlu JSON karar. Hata = None (çağıran kapı karar verir).
    replenish._gen_json retry kalıbı: geçici hata → backoff; model ölürse yedek model."""
    if not GEMINI_API_KEY:
        logger.warning("⚠️ QC: GEMINI_API_KEY yok — denetim atlanıyor")
        return None
    try:
        from google import genai
        from google.genai import types
    except ImportError as e:
        logger.warning(f"⚠️ QC: google-genai import edilemedi ({e}) — denetim atlanıyor")
        return None

    parts = []
    if ref_face:
        parts.append(types.Part.from_bytes(data=ref_face, mime_type="image/jpeg"))
    for f in frames:
        parts.append(types.Part.from_bytes(data=f.read_bytes(), mime_type="image/jpeg"))
    text = []
    if ref_face:
        text.append("The FIRST image is the REFERENCE FACE of the recurring character; "
                    "all following images are the sampled clip frames in time order.")
    else:
        text.append("All images are the sampled clip frames in time order.")
    text.append(f"GENERATION PROMPT:\n{prompt}")
    if notes:
        text.append(f"CHANNEL-SPECIFIC INSPECTION NOTES:\n{notes}")
    parts.append(types.Part.from_text(text="\n\n".join(text)))

    client = genai.Client(api_key=GEMINI_API_KEY)
    cfg = types.GenerateContentConfig(
        system_instruction=(
            _QC_SYSTEM + _NO_FACE_QC_ADDENDUM if require_no_face else _QC_SYSTEM
        ),
        response_mime_type="application/json",
        temperature=0.1,
    )
    last_err = None
    for model in (QC_MODEL, QC_MODEL_FALLBACK):
        for attempt in range(1, max_tries + 1):
            try:
                resp = client.models.generate_content(model=model, contents=parts, config=cfg)
                return _parse_json(resp.text or "")
            except Exception as e:
                last_err = e
                msg = str(e)
                bad_json = isinstance(e, json.JSONDecodeError)
                transient = any(s in msg for s in
                                ("503", "429", "500", "UNAVAILABLE", "RESOURCE_EXHAUSTED",
                                 "INTERNAL", "deadline"))
                if (transient or bad_json) and attempt < max_tries:
                    wait = 3 if bad_json else min(5 * attempt, 15)
                    logger.warning(f"⚠️ QC {model} geçici hata ({msg[:60]}…) — {wait}s sonra tekrar")
                    time.sleep(wait)
                    continue
                logger.warning(f"⚠️ QC {model} başarısız: {msg[:120]}")
                break  # yedek modele geç
    logger.warning(f"⚠️ QC denetimi yapılamadı ({last_err}) — klip DENETİMSİZ kabul ediliyor")
    return None


# ─── 2) Klip denetimi + karar ──────────────────────────────────────────────────

def _decide(review: dict, qc: dict, has_ref: bool) -> tuple[str, list[str]]:
    """Gemini kararını pass/fail'e çevir. Nedenler insan-okur (log + Telegram)."""
    reasons: list[str] = []
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
        face_present = review.get("face_present")
        if type(face_present) is not bool:
            reasons.append("zorunlu yüz görünürlüğü alanı doğrulanamadı")
        elif face_present:
            reasons.append("örneklenen karelerde insan yüzü görünüyor")
    score = review.get("artifact_score")
    if isinstance(score, (int, float)) and score >= qc["artifact_threshold"]:
        reasons.append(f"artifact skoru {score}/10 (eşik {qc['artifact_threshold']})")
    return ("fail" if reasons else "pass"), reasons


def review_clip(bible: Bible, shot: dict, clip_path: Path, prompt: str,
                qc: dict) -> tuple[dict | None, str, list[str], list[Path]]:
    """Bir klibi denetle. Dönüş: (gemini_kararı|None, 'pass'|'fail'|'skip', nedenler, kareler).
    Legacy 'skip' klibi korur; require_no_face aynı hatayı fail-closed RED yapar."""
    clip_path = Path(clip_path)
    frames = ffmpeg_tools.sample_frames(
        clip_path, count=int(qc["frames"]), width=int(qc["frame_width"]),
        out_dir=clip_path.parent / "qc", prefix=clip_path.stem,
    )
    if not frames:
        verdict = "fail" if qc.get("require_no_face") else "skip"
        return None, verdict, ["denetim karesi çıkarılamadı"], []
    ref_face = (
        _fetch_ref_face(bible, shot)
        if shot.get("characters") and not qc.get("require_no_face") else None
    )
    review = _review_frames(
        frames, ref_face, prompt, str(qc.get("notes") or ""),
        require_no_face=bool(qc.get("require_no_face")),
    )
    if review is None:
        verdict = "fail" if qc.get("require_no_face") else "skip"
        reason = (
            "zorunlu yüz görünürlüğü denetimi başarısız"
            if qc.get("require_no_face")
            else "Gemini denetimi başarısız (klip denetimsiz kabul edildi)"
        )
        return None, verdict, [reason], frames
    verdict, reasons = _decide(review, qc, has_ref=ref_face is not None)
    return review, verdict, reasons, frames


# ─── 3) Regen döngüsü ──────────────────────────────────────────────────────────

def strengthen_prompt(prompt: str, fix_notes: list[str]) -> str:
    """Reddedilen üretimin fix_notes'larını prompt'a zorunlu-düzeltme bloğu olarak ekle."""
    notes = [n.strip() for n in (fix_notes or []) if n and n.strip()]
    if not notes:
        notes = ["render all human figures with strictly correct anatomy: one head facing "
                 "a natural direction, two arms, two legs, five fingers per hand"]
    block = "CRITICAL CORRECTIONS — the previous take FAILED quality control. You MUST fix:\n" \
            + "\n".join(f"- {n}" for n in notes)
    return f"{prompt.rstrip()}\n\n{block}"


def _log_event(slug: str, entry: dict) -> None:
    """QC olayını seri veri klasörüne (data_dir(slug)/qc_log.jsonl) ekle (workflow commit'ler →
    ilk hafta eşik kalibrasyonu bu logdan yapılır). Best-effort."""
    try:
        p = data_dir(slug) / "qc_log.jsonl"
        p.parent.mkdir(parents=True, exist_ok=True)
        entry = {"ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), **entry}
        with open(p, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.warning(f"⚠️ QC log yazılamadı: {e}")


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


def _review_audio(audio_path: Path, max_tries: int = 3) -> dict | None:
    """Send an extracted audio sample to Gemini using the clip-QC retry/model pattern."""
    if not GEMINI_API_KEY:
        logger.warning("⚠️ Ses QC: GEMINI_API_KEY yok — ses doğrulanamıyor")
        return None
    try:
        from google import genai
        from google.genai import types
    except ImportError as error:
        logger.warning(f"⚠️ Ses QC: google-genai import edilemedi ({error})")
        return None

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
    client = genai.Client(api_key=GEMINI_API_KEY)
    cfg = types.GenerateContentConfig(
        system_instruction=_AUDIO_QC_SYSTEM,
        response_mime_type="application/json",
        temperature=0.1,
    )
    last_error = None
    for model in (QC_MODEL, QC_MODEL_FALLBACK):
        for attempt in range(1, max_tries + 1):
            try:
                response = client.models.generate_content(
                    model=model, contents=parts, config=cfg
                )
                return _parse_json(response.text or "")
            except Exception as error:
                last_error = error
                message = str(error)
                bad_json = isinstance(error, json.JSONDecodeError)
                transient = any(
                    marker in message
                    for marker in (
                        "503", "429", "500", "UNAVAILABLE", "RESOURCE_EXHAUSTED",
                        "INTERNAL", "deadline",
                    )
                )
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
    return None


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


def _review_raw_native_audio(audio_path: Path, max_tries: int = 3) -> dict | None:
    """Review one persisted raw WAV stem with the native-audio schema."""
    if not GEMINI_API_KEY:
        logger.warning("⚠️ Ham ses QC: GEMINI_API_KEY yok — denetim başarısız")
        return None
    try:
        from google import genai
        from google.genai import types
    except ImportError as error:
        logger.warning(f"⚠️ Ham ses QC: google-genai import edilemedi ({error})")
        return None

    try:
        audio = audio_path.read_bytes()
    except OSError as error:
        logger.warning(f"⚠️ Ham ses QC: stem okunamadı ({error})")
        return None
    parts = [
        types.Part.from_bytes(data=audio, mime_type="audio/wav"),
        types.Part.from_text(text="Inspect this raw shot-audio stem for every required field."),
    ]
    client = genai.Client(api_key=GEMINI_API_KEY)
    cfg = types.GenerateContentConfig(
        system_instruction=_RAW_AUDIO_QC_SYSTEM,
        response_mime_type="application/json",
        temperature=0.1,
    )
    last_error = None
    for model in (QC_MODEL, QC_MODEL_FALLBACK):
        for attempt in range(1, max_tries + 1):
            try:
                response = client.models.generate_content(
                    model=model, contents=parts, config=cfg
                )
                return _parse_json(response.text or "")
            except Exception as error:
                last_error = error
                message = str(error)
                bad_json = isinstance(error, json.JSONDecodeError)
                transient = any(
                    marker in message
                    for marker in (
                        "503", "429", "500", "UNAVAILABLE", "RESOURCE_EXHAUSTED",
                        "INTERNAL", "deadline",
                    )
                )
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
    return None


def review_raw_native_audio(bible: Bible, shot: dict, clip_path: Path,
                            episode: int, attempt: int) -> tuple[
                                dict | None, str, list[str], Path | None
                            ]:
    """Persist and review a raw shot stem; unavailable/invalid review fails closed."""
    shot_number = int(shot.get("n") or 0)
    stems = episode_dir(bible.slug, episode) / "stems"
    stem = stems / f"shot_{shot_number:02d}_attempt_{int(attempt):02d}.wav"
    extracted = ffmpeg_tools.extract_audio(clip_path, stem)
    if extracted is None:
        return None, "fail", ["ham native ses stem'i çıkarılamadı"], None

    review = _review_raw_native_audio(extracted)
    valid = (
        isinstance(review, dict)
        and type(review.get("has_foley")) is bool
        and type(review.get("unwanted_speech")) is bool
        and type(review.get("unwanted_music")) is bool
        and isinstance(review.get("notes"), str)
    )
    if not valid:
        return None, "fail", ["ham native ses denetimi zorunlu alanları doğrulamadı"], extracted

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


def qc_audio(path: str | Path) -> dict | None:
    """Verify the first 60 seconds of delivered audio with strict Gemini JSON."""
    media_path = Path(path)
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
            review = _review_audio(sample)
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
            regen_fn, episode: int, budget: dict) -> tuple[Path | None, float, str]:
    """Üretilmiş bir çekimi denetle; REDse regen_fn(güçlendirilmiş_prompt) ile yeniden
    üret (çekim başına maks max_regens_per_shot, bölüm başına budget["left"]).

    Dönüş: (kullanılacak_klip_yolu | None, regen'lerin ek kredisi,
    ``"pass"|"skip"|"fail"``). Legacy görsel denetimde ``skip`` korunur; opt-in
    zorunlu yüz ve ham-ses kapıları denetlenemezse ``fail`` olur.
    None = çekim eşiği geçemedi → çağıran onu üretim-FAIL gibi işler (bölümden düşer).
    Sözleşme: dönüşte clip_path adında dosya YA onaylıdır YA hiç yoktur — reddedilenler
    *_qcfail*.mp4'e taşınır, idempotent 'atla' yolu asla bozuk klip devralmaz."""
    qc = qc_config(bible)
    if not qc:
        return Path(clip_path), 0.0, "pass"
    clip_path = Path(clip_path)
    slug, n = bible.slug, shot.get("n")
    extra_credits = 0.0
    all_fix_notes: list[str] = []
    attempt = 0  # 0 = ilk üretim; 1..max = regen'ler
    shot_regen_limit = int(qc["max_regens_per_shot"])
    if "total" in budget and "shot_count" in budget:
        try:
            shot_count = int(budget["shot_count"])
            if shot_count > 0:
                fair_share = max(1, int(budget["total"]) // shot_count)
                shot_regen_limit = min(shot_regen_limit, fair_share)
        except (TypeError, ValueError):
            # Eski veya bozuk ek alanlar çekim başı mevcut davranışa geri döner.
            pass

    while True:
        review_try = 0
        review_retries = max(0, int(qc["qc_review_retries"]))
        frames: list[Path] = []
        audio_failure = False
        if qc.get("native_audio_review"):
            review, verdict, reasons, stem = review_raw_native_audio(
                bible, shot, clip_path, episode, attempt
            )
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
            })
            audio_failure = verdict != "pass"

        if not audio_failure:
            while True:
                review, verdict, reasons, frames = review_clip(
                    bible, shot, clip_path, prompt, qc
                )
                if qc.get("require_no_face"):
                    face_present = (review or {}).get("face_present")
                    if face_present is not False:
                        verdict = "fail"
                        gate_reason = (
                            "örneklenen karelerde insan yüzü görünüyor"
                            if face_present is True
                            else "zorunlu yüz görünürlüğü alanı doğrulanamadı"
                        )
                        if gate_reason not in reasons:
                            reasons = [*reasons, gate_reason]
                _log_event(slug, {
                    "event": "review", "episode": episode, "shot": n, "attempt": attempt,
                    "review_try": review_try, "verdict": verdict, "reasons": reasons,
                    "artifact_score": (review or {}).get("artifact_score"),
                    "issues": (review or {}).get("issues"),
                    "fix_notes": (review or {}).get("fix_notes"),
                    "clip": clip_path.name,
                })
                if verdict != "skip" or review_try >= review_retries:
                    break
                review_try += 1
                wait = QC_REVIEW_RETRY_DELAY * review_try
                logger.warning(
                    f"⚠️ QC denetimi atlandı: çekim {n}, aynı klip "
                    f"{wait:.2f}s sonra yeniden denenecek ({review_try}/{review_retries})"
                )
                time.sleep(wait)

        if verdict in ("pass", "skip"):
            if verdict == "pass":
                score = (review or {}).get("artifact_score")
                extra = f" (regen {attempt} sonrası)" if attempt else ""
                logger.info(f"🔍 QC GEÇTİ: çekim {n}, artifact {score}/10{extra}")
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
                })
                _notify(
                    f"⚠️ *QC DENETİMSİZ KABUL, {bible.title}* ep{episode} çekim {n}\n"
                    f"{review_try + 1} denetim denemesi sonuçsuz kaldı. "
                    f"Klip RED almadığı için kabul edildi. Neden: {reason_text}",
                    frames=frames,
                )
            return clip_path, extra_credits, verdict

        # ── RED ──
        logger.warning(f"🔍 QC RED: çekim {n} (deneme {attempt}): {'; '.join(reasons)}")
        if audio_failure:
            current_fix_notes = [
                "Keep the soundtrack limited to natural foley from the visible hands, "
                "object, material, and workbench."
            ]
        elif qc.get("require_no_face") and (review or {}).get("face_present") is not False:
            current_fix_notes = [
                "Frame only the hands, forearms, object, and workbench, with the face "
                "outside the frame."
            ]
        else:
            current_fix_notes = (review or {}).get("fix_notes") or reasons
        all_fix_notes.extend(current_fix_notes)

        can_regen = (regen_fn is not None
                     and attempt < shot_regen_limit
                     and budget.get("left", 0) > 0)
        # Reddedilen klip out_file adını BOŞALTIR (skip-yolu sözleşmesi)
        rejected = clip_path.parent / f"{clip_path.stem}_qcfail{attempt}{clip_path.suffix}"
        try:
            clip_path.replace(rejected)
        except Exception as e:
            logger.warning(f"⚠️ QC: reddedilen klip taşınamadı ({e})")

        if not can_regen:
            why = ("regen hakkı bitti" if regen_fn is not None and budget.get("left", 0) <= 0
                   else "çekim adil payı doldu"
                   if regen_fn is not None and shot_regen_limit < int(qc["max_regens_per_shot"])
                   else "çekim regen limiti doldu" if regen_fn is not None else "regen kapalı")
            logger.error(f"❌ QC: çekim {n} eşiği geçemedi ({why}) — çekim bölümden düşürüldü, ELLE BAK")
            _log_event(slug, {"event": "final_reject", "episode": episode, "shot": n,
                              "attempts": attempt, "reasons": reasons})
            _notify(f"🔍❌ *QC RED — {bible.title}* ep{episode} çekim {n}\n"
                    f"Nedenler: {'; '.join(reasons)}\n"
                    f"{attempt} regen denendi, eşik geçilemedi → çekim bölümden ÇIKARILDI. "
                    f"Bölüm kalan çekimlerle hazırlanıyor — yayın öncesi elle bak.",
                    frames=frames)
            return None, extra_credits, "fail"

        budget["left"] -= 1
        attempt += 1
        fixed_prompt = strengthen_prompt(prompt, all_fix_notes)
        logger.info(f"♻️ QC regen {attempt}/{shot_regen_limit}: çekim {n} "
                    f"düzeltilmiş prompt + yeni seed ile yeniden üretiliyor "
                    f"(bölüm hakkı: {budget['left']})")
        _log_event(slug, {"event": "regen", "episode": episode, "shot": n,
                          "attempt": attempt, "fix_notes": all_fix_notes})
        _clean_sidecars(clip_path)

        result = None
        try:
            result = regen_fn(fixed_prompt)
        except Exception as e:
            logger.warning(f"⚠️ QC regen üretimi hata verdi: {e}")
        if result and result.get("credits"):
            extra_credits += float(result["credits"])
        if not (result and result.get("url") and download_file(result["url"], clip_path)
                and clip_path.exists() and clip_path.stat().st_size > 0):
            logger.error(f"❌ QC regen üretimi başarısız — çekim {n} bölümden düşürüldü, ELLE BAK")
            _log_event(slug, {"event": "regen_failed", "episode": episode, "shot": n,
                              "attempt": attempt})
            _notify(f"🔍❌ *QC — {bible.title}* ep{episode} çekim {n}: klip QC'den geçemedi ve "
                    f"yeniden üretim de başarısız → çekim bölümden ÇIKARILDI (elle bak).",
                    frames=frames)
            return None, extra_credits, "fail"
        # döngü başa döner → yeni klip denetlenir
