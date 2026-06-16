"""
Shot / Episode Plan — bir bölümün çekim listesi, doğrulaması ve Omni parametrelerine çevirimi.

episode_plan.json şeması:
{
  "episode": {"number": 1, "title": "Bölüm adı"},
  "shots": [
    {
      "n": 1,
      "duration": "8",                  # 4 / 6 / 8 / 10
      "prompt": "Sahnede ne oluyor + diyalog",
      "characters": ["nil"],            # sahnedeki karakter id'leri → character_ids
      "speakers": ["nil"],              # konuşan karakter id'leri → audio_ids (≤3)
      "environment": "garden",          # ortam id → image_urls
      "props": ["watering_can"],        # aksesuar id'leri → image_urls
      "seed": null
    }
  ]
}
"""

import json
from pathlib import Path

from core.config import logger
from .bible import Bible, resolve_voice_id
from .omni_api import validate_duration, validate_ref_units


def load_plan(path: str | Path) -> dict:
    """episode_plan.json yükle."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def resolve_shot(bible: Bible, shot: dict) -> dict:
    """Bir çekimi generate_omni_shot için somut parametrelere çevir.

    Dönüş: {
      "kwargs": {prompt, image_urls, audio_ids, character_ids, duration, aspect_ratio, resolution, seed},
      "warnings": [str, ...],
      "units": int
    }
    Karakter kaydedilmişse characterId, değilse referans görseli kullanılır (dry-run uyumu).
    """
    warnings: list[str] = []

    base_prompt = (shot.get("prompt") or "").strip()
    art = bible.art_style.strip()
    prompt = f"{art}\n\n{base_prompt}" if art else base_prompt

    character_ids: list[str] = []
    image_urls: list[str] = []

    # Karakterler → characterId (yoksa referans görsel)
    for cid in shot.get("characters", []):
        ch = bible.get_character(cid)
        if not ch:
            warnings.append(f"Karakter '{cid}' bible'da yok")
            continue
        if ch.get("character_id"):
            character_ids.append(ch["character_id"])
        elif ch.get("ref_image_url"):
            image_urls.append(ch["ref_image_url"])
            warnings.append(f"Karakter '{cid}' henüz kaydedilmemiş → referans görsel kullanılıyor")
        else:
            warnings.append(f"Karakter '{cid}' için characterId/referans görsel yok")

    # Ortam → image_url
    env_id = shot.get("environment")
    if env_id:
        env = bible.get("environments", env_id)
        if not env:
            warnings.append(f"Ortam '{env_id}' bible'da yok")
        elif env.get("ref_image_url"):
            image_urls.append(env["ref_image_url"])
        else:
            warnings.append(f"Ortam '{env_id}' referans görseli yok")

    # Aksesuarlar → image_urls
    for pid in shot.get("props", []) or []:
        pr = bible.get("props", pid)
        if not pr:
            warnings.append(f"Aksesuar '{pid}' bible'da yok")
        elif pr.get("ref_image_url"):
            image_urls.append(pr["ref_image_url"])
        else:
            warnings.append(f"Aksesuar '{pid}' referans görseli yok")

    # Konuşmacılar → audio_ids (sıra korunarak tekilleştir)
    audio_ids: list[str] = []
    for sid in shot.get("speakers", []) or []:
        ch = bible.get_character(sid)
        if not ch:
            warnings.append(f"Konuşmacı '{sid}' bible'da yok")
            continue
        vid = resolve_voice_id(ch)
        if vid:
            audio_ids.append(vid)
        else:
            warnings.append(f"Konuşmacı '{sid}' için ses tanımlı değil")
    audio_ids = list(dict.fromkeys(audio_ids))

    # Bütçe / limit kontrolleri
    ok, units = validate_ref_units(image_urls, character_ids)
    if not ok:
        warnings.append(f"7-birim kotası AŞILDI ({units} birim) — bu çekim reddedilir")
    if len(audio_ids) > 3:
        warnings.append(f"3'ten fazla ses ({len(audio_ids)}) — yalnızca ilk 3 kullanılır")
    if len(character_ids) > 3:
        warnings.append(f"3'ten fazla karakter ({len(character_ids)}) — yalnızca ilk 3 kullanılır")

    kwargs = {
        "prompt": prompt,
        "image_urls": image_urls,
        "audio_ids": audio_ids,
        "character_ids": character_ids,
        "duration": validate_duration(shot.get("duration", "8")),
        "aspect_ratio": bible.aspect_ratio,
        "resolution": bible.resolution,
        "seed": shot.get("seed"),
    }
    return {"kwargs": kwargs, "warnings": warnings, "units": units}


def resolve_visual_shot(bible: Bible, shot: dict, chain_url: str | None = None) -> dict:
    """Bir çekimi Omni-DIŞI ucuz motorlar (Seedance / Veo / Kling) için çöz.

    Omni'nin karakter/ses kaydı YOK; sadece (prompt + başlangıç görseli + süre) gerekir.
    Başlangıç görseli önceliği:
      1) chain_url  — 'bitmeyen yolculuk' zinciri (önceki çekimin son karesi)
      2) ortam referans görseli (environment)
      3) ilk karakterin referans görseli (figür kamera önündeyse — ucuz modelde tek kare)
      4) None — saf text-to-video
    Dönüş: {"prompt", "start_image_url", "duration"}
    """
    base_prompt = (shot.get("prompt") or "").strip()
    art = bible.art_style.strip()
    prompt = f"{art}\n\n{base_prompt}" if art else base_prompt

    start_url = chain_url
    if not start_url:
        env_id = shot.get("environment")
        if env_id:
            env = bible.get("environments", env_id)
            if env and env.get("ref_image_url"):
                start_url = env["ref_image_url"]
    if not start_url:
        for cid in shot.get("characters", []):
            ch = bible.get_character(cid)
            if ch and ch.get("ref_image_url"):
                start_url = ch["ref_image_url"]
                break

    return {
        "prompt": prompt,
        "start_image_url": start_url,
        "duration": validate_duration(shot.get("duration", "8")),
    }


def validate_plan(plan: dict, bible: Bible) -> dict:
    """Bölüm planını bible'a karşı doğrula.
    Dönüş: {"errors": [...], "warnings": [...]}
    """
    errors: list[str] = []
    warnings: list[str] = []

    shots = plan.get("shots")
    if not shots:
        errors.append("Plan'da 'shots' yok veya boş")
        return {"errors": errors, "warnings": warnings}

    for shot in shots:
        n = shot.get("n", "?")
        dur = str(shot.get("duration", "8")).strip()
        if dur not in ("4", "6", "8", "10"):
            warnings.append(f"Çekim {n}: süre '{dur}' geçersiz → 8s'ye düşürülecek")
        res = resolve_shot(bible, shot)
        for w in res["warnings"]:
            # Kota aşımı = hata, diğerleri uyarı
            if "AŞILDI" in w:
                errors.append(f"Çekim {n}: {w}")
            else:
                warnings.append(f"Çekim {n}: {w}")

    return {"errors": errors, "warnings": warnings}


def plan_summary(plan: dict) -> str:
    """Planın kısa özetini (toplam süre, çekim sayısı) döndür."""
    shots = plan.get("shots", [])
    total = sum(int(str(s.get("duration", "8")).strip() or 8) for s in shots)
    ep = plan.get("episode", {})
    return (f"Bölüm {ep.get('number', '?')} — {ep.get('title', '')}: "
            f"{len(shots)} çekim, ~{total} sn toplam")
