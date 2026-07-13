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
  • QC/Gemini hatası = "skip" (klip aynen kullanılır) — QC bir kalite katmanıdır,
    yayını tek başına durduramaz (the-signal dersi: sessiz zincirleme çökme yok).
  • Her karar series_data/<slug>/qc_log.jsonl'e yazılır (workflow bunu commit'ler)
    → ilk hafta false-positive kalibrasyonu bu logdan yapılır.
Maliyet: denetim <$0.01/video (Gemini Flash); kie'de FAIL görev 0 kredi, regen
yalnız "başarılı-fakat-bozuk" üretimde kredi yakar.
"""

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

from core.config import GEMINI_API_KEY, logger
from core import ffmpeg_tools
from core.utils import download_file
from .bible import Bible, data_dir

QC_MODEL = "gemini-2.5-flash"
QC_MODEL_FALLBACK = "gemini-flash-latest"

QC_DEFAULTS = {
    "frames": 8,                # klipten örneklenecek kare sayısı
    "artifact_threshold": 6,    # 0-10; bu ve üstü artifact_score = RED
    "max_regens_per_shot": 2,   # çekim başına yeniden üretim hakkı
    "frame_width": 720,         # denetim karesi genişliği (dikeyde 720x1280)
}


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
                   prompt: str, notes: str, max_tries: int = 3) -> dict | None:
    """Kareleri Gemini vision'a ver → zorunlu JSON karar. Hata = None (pass-through).
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
        system_instruction=_QC_SYSTEM,
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
    score = review.get("artifact_score")
    if isinstance(score, (int, float)) and score >= qc["artifact_threshold"]:
        reasons.append(f"artifact skoru {score}/10 (eşik {qc['artifact_threshold']})")
    return ("fail" if reasons else "pass"), reasons


def review_clip(bible: Bible, shot: dict, clip_path: Path, prompt: str,
                qc: dict) -> tuple[dict | None, str, list[str], list[Path]]:
    """Bir klibi denetle. Dönüş: (gemini_kararı|None, 'pass'|'fail'|'skip', nedenler, kareler).
    'skip' = denetim yapılamadı → klip aynen kullanılır (QC yayını durduramaz)."""
    clip_path = Path(clip_path)
    frames = ffmpeg_tools.sample_frames(
        clip_path, count=int(qc["frames"]), width=int(qc["frame_width"]),
        out_dir=clip_path.parent / "qc", prefix=clip_path.stem,
    )
    if not frames:
        return None, "skip", ["denetim karesi çıkarılamadı"], []
    ref_face = _fetch_ref_face(bible, shot) if shot.get("characters") else None
    review = _review_frames(frames, ref_face, prompt, str(qc.get("notes") or ""))
    if review is None:
        return None, "skip", ["Gemini denetimi başarısız (klip denetimsiz kabul edildi)"], frames
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
    """QC olayını series_data/<slug>/qc_log.jsonl'e ekle (workflow commit'ler →
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


def qc_shot(bible: Bible, shot: dict, clip_path: Path, prompt: str,
            regen_fn, episode: int, budget: dict) -> tuple[Path | None, float]:
    """Üretilmiş bir çekimi denetle; REDse regen_fn(güçlendirilmiş_prompt) ile yeniden
    üret (çekim başına maks max_regens_per_shot, bölüm başına budget["left"]).

    Dönüş: (kullanılacak_klip_yolu | None, regen'lerin ek kredisi).
    None = çekim eşiği geçemedi → çağıran onu üretim-FAIL gibi işler (bölümden düşer).
    Sözleşme: dönüşte clip_path adında dosya YA onaylıdır YA hiç yoktur — reddedilenler
    *_qcfail*.mp4'e taşınır, idempotent 'atla' yolu asla bozuk klip devralmaz."""
    qc = qc_config(bible)
    if not qc:
        return Path(clip_path), 0.0
    clip_path = Path(clip_path)
    slug, n = bible.slug, shot.get("n")
    extra_credits = 0.0
    all_fix_notes: list[str] = []
    attempt = 0  # 0 = ilk üretim; 1..max = regen'ler

    while True:
        review, verdict, reasons, frames = review_clip(bible, shot, clip_path, prompt, qc)
        _log_event(slug, {
            "event": "review", "episode": episode, "shot": n, "attempt": attempt,
            "verdict": verdict, "reasons": reasons,
            "artifact_score": (review or {}).get("artifact_score"),
            "issues": (review or {}).get("issues"),
            "fix_notes": (review or {}).get("fix_notes"),
            "clip": clip_path.name,
        })

        if verdict in ("pass", "skip"):
            if verdict == "pass":
                score = (review or {}).get("artifact_score")
                extra = f" (regen {attempt} sonrası)" if attempt else ""
                logger.info(f"🔍 QC GEÇTİ: çekim {n}, artifact {score}/10{extra}")
                if attempt:
                    _notify(f"🔍 *{bible.title}* ep{episode} çekim {n}: QC {attempt}. regen'de GEÇTİ "
                            f"(nedenler: {'; '.join(all_fix_notes[:3]) or 'anatomi'}) ✅")
            else:
                logger.warning(f"🔍 QC ATLANDI: çekim {n} — {'; '.join(reasons)}")
            return clip_path, extra_credits

        # ── RED ──
        logger.warning(f"🔍 QC RED: çekim {n} (deneme {attempt}): {'; '.join(reasons)}")
        all_fix_notes.extend((review or {}).get("fix_notes") or reasons)

        can_regen = (regen_fn is not None
                     and attempt < int(qc["max_regens_per_shot"])
                     and budget.get("left", 0) > 0)
        # Reddedilen klip out_file adını BOŞALTIR (skip-yolu sözleşmesi)
        rejected = clip_path.parent / f"{clip_path.stem}_qcfail{attempt}{clip_path.suffix}"
        try:
            clip_path.replace(rejected)
        except Exception as e:
            logger.warning(f"⚠️ QC: reddedilen klip taşınamadı ({e})")

        if not can_regen:
            why = ("regen hakkı bitti" if regen_fn is not None and budget.get("left", 0) <= 0
                   else "çekim regen limiti doldu" if regen_fn is not None else "regen kapalı")
            logger.error(f"❌ QC: çekim {n} eşiği geçemedi ({why}) — çekim bölümden düşürüldü, ELLE BAK")
            _log_event(slug, {"event": "final_reject", "episode": episode, "shot": n,
                              "attempts": attempt, "reasons": reasons})
            _notify(f"🔍❌ *QC RED — {bible.title}* ep{episode} çekim {n}\n"
                    f"Nedenler: {'; '.join(reasons)}\n"
                    f"{attempt} regen denendi, eşik geçilemedi → çekim bölümden ÇIKARILDI. "
                    f"Bölüm kalan çekimlerle hazırlanıyor — yayın öncesi elle bak.",
                    frames=frames)
            return None, extra_credits

        budget["left"] -= 1
        attempt += 1
        fixed_prompt = strengthen_prompt(prompt, all_fix_notes)
        logger.info(f"♻️ QC regen {attempt}/{qc['max_regens_per_shot']}: çekim {n} "
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
            return None, extra_credits
        # döngü başa döner → yeni klip denetlenir
