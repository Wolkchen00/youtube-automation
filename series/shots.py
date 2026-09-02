"""
Shot / Episode Plan — bir bölümün çekim listesi, doğrulaması ve Omni parametrelerine çevirimi.

episode_plan.json şeması:
{
  "episode": {"number": 1, "title": "Bölüm adı"},
  "format_version": "tek-obje-4x6",    # opsiyonel format doğrulayıcısı
  "object_card": {                      # tek-obje-4x6 için zorunlu
    "name": "...", "descriptor": "...", "environment": "garden", "framing": "..."
  },
  "prop_ref_urls": ["https://..."],     # bölüm-başı obje referansı
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
import re
from urllib.parse import urlparse

from core.config import logger
from .bible import Bible, resolve_voice_id
from .omni_api import validate_duration, validate_ref_units


TEK_OBJE_FORMAT = "tek-obje-4x6"
OBJECT_CARD_FIELDS = ("name", "descriptor", "environment", "framing",
                       "anomaly_descriptor")
NEGATIVE_VIDEO_LANGUAGE = re.compile(
    r"\b(?:no|not|never|nothing|neither|nor|without|cannot|can't|don't|doesn't|"
    r"isn't|aren't|won't|absent|lacks?|lacking|avoid)\b|\binstead\s+of\b",
    re.IGNORECASE,
)
# Shot 1 anomalinin başladığı anı değil, ilk karede zaten süren hâlini göstermeli.
SHOT1_ONSET_LANGUAGE = re.compile(
    r"\b(?:begins?|starts?|beginning|starting)\s+to\b|"
    r"\b(?:begins|starts)\s+[a-z]+ing\b",
    re.IGNORECASE,
)
TEMPORAL_OVERREACH = re.compile(
    r"\b(?:never|always|forever|eventually)\b|"
    r"\bstill\b[^.!?]{0,80}\bafter\b|"
    r"\bkeeps?\b[^.!?]{0,80}\b\w+ing\b[^.!?]{0,40}\bindefinitely\b",
    re.IGNORECASE,
)


def _is_https_url(value) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def format_plan_errors(plan: dict, bible: Bible) -> list[str]:
    """Fail-closed checks owned by the ``tek-obje-4x6`` plan format."""
    if plan.get("format_version") != TEK_OBJE_FORMAT:
        return []

    errors: list[str] = []
    card = plan.get("object_card")
    card_ok = isinstance(card, dict)
    if not card_ok:
        errors.append("object_card nesnesi zorunlu")
        card = {}

    values: dict[str, str] = {}
    for field in OBJECT_CARD_FIELDS:
        value = card.get(field)
        if not isinstance(value, str) or not value.strip() or value != value.strip():
            errors.append(f"object_card.{field} boş olmayan, kırpılmış string olmalı")
        else:
            values[field] = value

    descriptor = values.get("descriptor", "")
    if descriptor and len(descriptor.split()) < 12:
        errors.append("object_card.descriptor en az 12 kelime olmalı")

    # ROCK B: anomalinin KENDİ görsel imzası. descriptor objeyi kilitler, bu alan
    # imkânsız özelliğin ekranda nasıl göründüğünü kilitler (pilot-1 ölçümü: limon
    # aynı kaldı ama içindeki merdiven çekim 1/3/4'te başka başka çıktı).
    anomaly = values.get("anomaly_descriptor", "")
    if anomaly and len(anomaly.split()) < 10:
        errors.append("object_card.anomaly_descriptor en az 10 kelime olmalı")

    env_id = values.get("environment", "")
    if env_id and not bible.get("environments", env_id):
        errors.append(f"object_card.environment bible.environments içinde yok ({env_id!r})")

    shots = plan.get("shots")
    if not isinstance(shots, list) or len(shots) != 4:
        got = len(shots) if isinstance(shots, list) else "yok"
        errors.append(f"tek-obje-4x6 tam 4 çekim içermeli (gelen: {got})")
        shots = shots if isinstance(shots, list) else []
    numbers = [shot.get("n") if isinstance(shot, dict) else None for shot in shots]
    if len(shots) == 4 and numbers != [1, 2, 3, 4]:
        errors.append(f"tek-obje-4x6 çekim numaraları tam [1, 2, 3, 4] olmalı (gelen: {numbers})")

    framing = values.get("framing", "")
    if framing:
        sentence_marks = re.findall(r"[.!?](?=\s|$)", framing)
        if len(sentence_marks) != 1 or framing[-1] not in ".!?":
            errors.append("object_card.framing tam bir cümle olmalı")
    for index, shot in enumerate(shots, start=1):
        if not isinstance(shot, dict):
            errors.append(f"çekim {index} JSON nesnesi olmalı")
            continue
        number = shot.get("n", index)
        if shot.get("duration") != "6":
            errors.append(f"çekim {number} süresi tam '6' string olmalı")
        prompt = shot.get("prompt")
        if not isinstance(prompt, str):
            prompt = ""
        if index == 1:
            onset = SHOT1_ONSET_LANGUAGE.search(prompt)
            if onset:
                errors.append(
                    f"çekim 1 anomaliyi BAŞLATIYOR ({onset.group(0)!r}); shot 1'de "
                    "anomali kameradan önce başlamış ve ilk karede zaten sürer olmalı "
                    "(brief kural 4). Süren bir DURUM yaz, başlayan bir OLAY değil."
                )
        if NEGATIVE_VIDEO_LANGUAGE.search(prompt):
            errors.append(f"çekim {number} prompt'u yalnız olumlu görsel dil kullanmalı")
        if descriptor and descriptor not in prompt:
            errors.append(f"çekim {number} object_card.descriptor metnini birebir içermeli")
        if anomaly and anomaly not in prompt:
            errors.append(
                f"çekim {number} object_card.anomaly_descriptor metnini birebir içermeli"
            )
        observation = shot.get("violation_observation")
        if observation is not None:
            if (not isinstance(observation, str) or not observation.strip()
                    or observation != observation.strip()):
                errors.append(
                    f"çekim {number} violation_observation boş olmayan, kırpılmış string olmalı"
                )
            elif len(observation.split()) < 4:
                errors.append(f"çekim {number} violation_observation en az 4 kelime olmalı")
            elif (NEGATIVE_VIDEO_LANGUAGE.search(observation)
                  or TEMPORAL_OVERREACH.search(observation)):
                errors.append(
                    f"çekim {number} violation_observation OLUMLU ve gözlemlenebilir olmalı; "
                    f"olumsuz ya da zaman-ötesi iddia yasak"
                )
        carry = shot.get("state_carry")
        if carry is not None:
            if (not isinstance(carry, str) or not carry.strip()
                    or carry != carry.strip()):
                errors.append(
                    f"çekim {number} state_carry boş olmayan, kırpılmış string olmalı"
                )
            elif len(carry.split()) < 3:
                errors.append(f"çekim {number} state_carry en az 3 kelime olmalı")
            elif number >= len(shots):
                errors.append(
                    f"çekim {number} state_carry tanımlı ama ardıl çekim yok; iz yalnız bir "
                    f"SONRAKİ çekime karşı değerlendirilir"
                )
            elif isinstance(carry, str) and carry.strip() == carry:
                next_shot = shots[index] if index < len(shots) else None
                next_prompt = (
                    next_shot.get("prompt") if isinstance(next_shot, dict) else None
                )
                if not isinstance(next_prompt, str) or carry not in next_prompt:
                    errors.append(
                        f"çekim {number} state_carry metni ardıl çekim prompt'unda "
                        f"birebir bulunmalı"
                    )
        if framing and framing not in prompt:
            errors.append(f"çekim {number} object_card.framing cümlesini birebir içermeli")
        if env_id and shot.get("environment") != env_id:
            errors.append(f"çekim {number} environment tam {env_id!r} olmalı")

    ref_hash = plan.get("ref_prompt_sha256")
    if ref_hash is not None and (
        not isinstance(ref_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", ref_hash)
    ):
        errors.append("ref_prompt_sha256 64 haneli küçük harf hex olmalı")

    refs = plan.get("prop_ref_urls")
    if refs is not None and (
        not isinstance(refs, list)
        or not refs
        or not all(_is_https_url(url) for url in refs)
    ):
        errors.append("prop_ref_urls bir veya daha fazla https URL içermeli")
    for shot in shots:
        if not isinstance(shot, dict) or "prop_ref_urls" not in shot:
            continue
        shot_refs = shot.get("prop_ref_urls")
        if (not isinstance(shot_refs, list) or not shot_refs
                or not all(_is_https_url(url) for url in shot_refs)):
            errors.append(
                f"çekim {shot.get('n', '?')} prop_ref_urls bir veya daha fazla https URL içermeli"
            )
        elif shot_refs != refs:
            errors.append(
                f"çekim {shot.get('n', '?')} prop_ref_urls plan düzeyi listeyle birebir aynı olmalı"
            )
    if NEGATIVE_VIDEO_LANGUAGE.search(bible.art_style or ""):
        errors.append("bible.art_style tek-obje-4x6 için yalnız olumlu görsel dil kullanmalı")
    return errors


def load_plan(path: str | Path) -> dict:
    """episode_plan.json yükle."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _assert_image_bindings(image_urls: list[str], bindings: list[dict]) -> None:
    """Numaralı prompt bağlarının payload sırasından kopmasına izin verme."""
    assert len(image_urls) == len(bindings), "görsel URL/etiket sayısı eşleşmiyor"
    for index, (url, binding) in enumerate(zip(image_urls, bindings), start=1):
        assert binding == {
            "index": index,
            "url": url,
            "label": binding["label"],
        }, f"görsel {index} URL/etiket eşleşmesi bozuk"
        assert binding["label"].startswith(f"[image {index}] "), (
            f"görsel {index} etiketi yanlış konumu söylüyor"
        )


def resolve_shot(bible: Bible, shot: dict, plan: dict | None = None,
                 chain_url: str | None = None) -> dict:
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

    character_ids: list[str] = []
    image_references: list[dict[str, str]] = []
    binding_lines: list[str] = []

    # Zincir karesi de dahil TAM payload sırası önce burada kurulur. Etiketler aşağıda
    # aynı listeden türetilir; sonradan prepend ederek numaraları kaydırmak yasaktır.
    if chain_url:
        image_references.append({"url": chain_url, "role": "chain"})

    # Bölüm-başı obje referansları her zaman ilk sıradadır. Shot düzeyi alan,
    # gerektiğinde plan düzeyi alanı bilinçli olarak geçersiz kılar.
    prop_ref_urls = (
        shot.get("prop_ref_urls")
        if "prop_ref_urls" in shot
        else (plan or {}).get("prop_ref_urls")
    )
    if isinstance(prop_ref_urls, list):
        for url in prop_ref_urls:
            if not _is_https_url(url):
                warnings.append(f"Obje referans URL'i geçersiz: {url!r}")
                continue
            image_references.append({"url": url, "role": "object"})
            binding_lines.append(
                f"[image {len(image_references)}] is the exact object: keep its shape, colour, "
                "scale and markings identical."
            )
    object_refs_added = any(ref["role"] == "object" for ref in image_references)

    # Ortam referansı obje referanslarından hemen sonra gelir. Bu sıra formatın
    # video payload sözleşmesidir ve sonraki legacy referanslardan bağımsızdır.
    env_id = shot.get("environment")
    if object_refs_added and env_id:
        env = bible.get("environments", env_id)
        if not env:
            warnings.append(f"Ortam '{env_id}' bible'da yok")
        elif env.get("ref_image_url"):
            image_references.append({"url": env["ref_image_url"], "role": "environment"})
            if prop_ref_urls:
                binding_lines.append(
                    f"[image {len(image_references)}] is the room and surface: keep the same surface and light."
                )
        else:
            warnings.append(f"Ortam '{env_id}' referans görseli yok")

    # Karakterler → characterId (yoksa referans görsel). Yüzsüz formatlar bu
    # teknik referans katmanını opt-in olarak tamamen kaldırabilir.
    if not bible.omit_character_refs:
        for cid in shot.get("characters", []):
            ch = bible.get_character(cid)
            if not ch:
                warnings.append(f"Karakter '{cid}' bible'da yok")
                continue
            if ch.get("character_id"):
                character_ids.append(ch["character_id"])
            elif ch.get("ref_image_url"):
                image_references.append({"url": ch["ref_image_url"], "role": "character"})
                warnings.append(f"Karakter '{cid}' henüz kaydedilmemiş → referans görsel kullanılıyor")
            else:
                warnings.append(f"Karakter '{cid}' için characterId/referans görsel yok")

    # Legacy sıra byte/behavior uyumu: obje referansı yokken karakter görselleri
    # ortamdan önce gelmeye devam eder.
    if not object_refs_added and env_id:
        env = bible.get("environments", env_id)
        if not env:
            warnings.append(f"Ortam '{env_id}' bible'da yok")
        elif env.get("ref_image_url"):
            image_references.append({"url": env["ref_image_url"], "role": "environment"})
        else:
            warnings.append(f"Ortam '{env_id}' referans görseli yok")

    # Aksesuarlar → image_urls
    for pid in shot.get("props", []) or []:
        pr = bible.get("props", pid)
        if not pr:
            warnings.append(f"Aksesuar '{pid}' bible'da yok")
        elif pr.get("ref_image_url"):
            image_references.append({"url": pr["ref_image_url"], "role": "prop"})
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

    image_urls = [reference["url"] for reference in image_references]
    image_bindings: list[dict] = []
    if chain_url:
        labels = {
            "chain": "is the previous accepted shot's suitable last frame: continue its camera, surface, light and object state.",
            "object": "is the exact object: keep its shape, colour, scale and markings identical.",
            "environment": "is the room and surface: keep the same surface and light.",
            "character": "is a character reference: keep that character's identity consistent.",
            "prop": "is a prop reference: keep that prop's identity consistent.",
        }
        image_bindings = [
            {
                "index": index,
                "url": reference["url"],
                "label": f"[image {index}] {labels[reference['role']]}",
            }
            for index, reference in enumerate(image_references, start=1)
        ]
        _assert_image_bindings(image_urls, image_bindings)
        binding_lines = [binding["label"] for binding in image_bindings]

    if binding_lines:
        base_prompt = f"{base_prompt}\n\n" + "\n".join(binding_lines)
    prompt = f"{art}\n\n{base_prompt}" if art else base_prompt

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
    result = {"kwargs": kwargs, "warnings": warnings, "units": units}
    if chain_url:
        result["image_bindings"] = image_bindings
    return result


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
    if not start_url and not bible.omit_character_refs:
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
    if not isinstance(shots, list) or not shots:
        errors.append("Plan'da 'shots' yok veya boş")
        return {"errors": errors, "warnings": warnings}

    if bible.face_visible is False and plan.get("face_visible") is not False:
        errors.append("Plan'da 'face_visible' tam false olmalı")

    errors.extend(format_plan_errors(plan, bible))

    for shot in shots:
        if not isinstance(shot, dict):
            errors.append("Plan'daki her çekim JSON nesnesi olmalı")
            continue
        n = shot.get("n", "?")
        dur = str(shot.get("duration", "8")).strip()
        if dur not in ("4", "6", "8", "10"):
            warnings.append(f"Çekim {n}: süre '{dur}' geçersiz → 8s'ye düşürülecek")
        res = resolve_shot(bible, shot, plan)
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
