"""
Oto-ikmal (auto-replenish) ,  'sonsuz içerik' motoru.

Plan kuyruğu azalan serilere Gemini yönetmeniyle YENİ part planları yazar
(<seri-veri-klasörü>/plans/partNN.json ,  konum bible.data_dir(slug)), total_parts'ı büyütür ve makinenin
'completed'e düşürdüğü seriyi yeniden 'active' yapar. Kie kredisi HARCAMAZ , 
yalnız ücretsiz Gemini text çağrısı (planlama), üretim yine series_runner'da.

Kurallar:
  • Yalnız series.json'da "auto_replenish": {"enabled": true} olan seriler (opt-in).
  • 'paused' / 'draft' ASLA diriltilmez (insan kararı). 'completed' makine kararıdır
    (advance() kuyruk bitince yazar) → ikmal açıkken yeniden 'active' olur.
    DURDURMA ANAHTARI: status="paused" veya auto_replenish.enabled=false.
  • Var olan plan dosyasının üzerine ASLA yazılmaz; koşu başına en fazla 1 batch.
  • Yarıda çökme güvenliği: önce plan dosyaları yazılır, sayaç SONRA güncellenir;
    ortada kalan dosyalar bir sonraki koşuda sahiplenilir (_adopt_orphans) , 
    Gemini çıktısı asla çöpe gitmez, yeniden istenmez.

series.json şeması:
  "auto_replenish": {
    "enabled": true,        // zorunlu anahtar; false/yok = kapalı
    "batch": 5,             // ops. (1-10): her ikmalde kaç yeni bölüm
    "min_queue": 2,         // ops. (>=1): bekleyen bölüm bunun altına inince ikmal
    "brief": "...",         // ops.: Gemini'ye seriye özgü yaratıcı yön (Türkçe olabilir)
    "format_version": "tek-obje-4x6", // ops.: format-bazlı şema + fail-closed doğrulama
    "music_prompt": true,   // ops.: bölüm başına sahne-eşleşmeli 'music' alanı istenir (Suno)
    "caption": true,        // ops.: bölüm başına 'caption' (yazılı hikâye) + 'hashtags' istenir
                            //       (the__footnote formatı: hikâye videoda değil açıklamada)
    "shots": 4,             // ops.: bölüm başına çekim sayısı
    "shot_seconds": "8",    // ops.: çekim süresi ("4"|"6"|"8"|"10")
    "chain_breaks": [1, 4], // ops.: bu çekimler chain=false; diğerleri chain=true
    "hook_shot": 4,         // ops.: zorunlu teaser-source çekim numarası
    "shot_plan": ["..."],   // ops.: çekim başına deterministik prompt öneki
    "title_patterns": [      // ops.: fullmatch + izinli family kuralları
      {"regex": "...", "families": ["..."]}
    ],
    "credit_hard_cap": true,// ops.: her ücretli çağrıda tahmini sert tavan
    "last_run": {...}       // makine yazar
  }

Kullanım (yerel):
  python -m series.replenish                      # tüm ikmalli seriler
  python -m series.replenish --series infinite-trip
  python -m series.replenish --dry-run            # ne yapılacağını söyler, yazmaz
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Mapping

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from core.config import GEMINI_API_KEY, logger
from core.ffmpeg_tools import NARRATION_MAX_TEMPO
from series import notifier
from series.bible import (
    Bible,
    atomic_write_json,
    data_dir,
    doctrine_path,
    doctrine_repo_path,
    doctrine_sha256,
)
from series.series_meta import SeriesMeta, part_plan_path, plans_dir
from series.shots import OBJECT_CARD_FIELDS, TEK_OBJE_FORMAT, validate_plan

REPLENISH_MODEL = "gemini-2.5-flash"
REPLENISH_MODEL_FALLBACK = "gemini-flash-latest"
DEFAULT_BATCH = 5
DEFAULT_MIN_QUEUE = 2
DEFAULT_SHOTS = 4          # bölüm başına çekim
DEFAULT_SHOT_SECONDS = "8" # çekim süresi (motor enum'u: 4/6/8/10)
VALID_DURATIONS = ("4", "6", "8", "10")


def _compiled_title_patterns(cfg: dict) -> list[tuple[re.Pattern, set[str]]]:
    """Compile structured title rules. Invalid config raises ``ValueError``."""
    raw = cfg.get("title_patterns")
    if raw is None:
        return []
    if not isinstance(raw, list) or not raw:
        raise ValueError("title_patterns boş olmayan bir liste olmalı")
    compiled = []
    canonical = {
        str(value).strip() for value in (cfg.get("families") or []) if str(value).strip()
    }
    for index, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"title_patterns[{index}] nesne olmalı")
        regex = item.get("regex")
        families = item.get("families")
        if not isinstance(regex, str) or not regex:
            raise ValueError(f"title_patterns[{index}].regex boş olamaz")
        if not isinstance(families, list) or not families:
            raise ValueError(f"title_patterns[{index}].families boş olmayan liste olmalı")
        allowed = {str(value).strip() for value in families if str(value).strip()}
        if len(allowed) != len(families):
            raise ValueError(f"title_patterns[{index}].families boş/tekrarlı değer içeriyor")
        if canonical and not allowed.issubset(canonical):
            unknown = sorted(allowed - canonical)
            raise ValueError(f"title_patterns[{index}] kanonik olmayan aile içeriyor: {unknown}")
        try:
            pattern = re.compile(regex)
        except re.error as error:
            raise ValueError(f"title_patterns[{index}] bozuk regex: {error}") from error
        compiled.append((pattern, allowed))
    return compiled


def validate_replenish_config(cfg: dict) -> list[str]:
    """Validate only Rock 1 opt-in config fields; legacy configs are untouched."""
    errors: list[str] = []
    try:
        shots = int(cfg.get("shots", DEFAULT_SHOTS))
    except (TypeError, ValueError):
        shots = 0
    format_version = cfg.get("format_version")
    if "format_version" in cfg and (
        not isinstance(format_version, str) or not format_version.strip()
    ):
        errors.append("format_version boş olmayan string olmalı")
    if format_version == TEK_OBJE_FORMAT and (shots != 4):
        errors.append("tek-obje-4x6 formatında shots tam 4 olmalı")
    if format_version == TEK_OBJE_FORMAT and (
        str(cfg.get("shot_seconds", DEFAULT_SHOT_SECONDS)).strip() != "6"
    ):
        errors.append("tek-obje-4x6 formatında shot_seconds tam 6 olmalı")

    fixedframe_keys = (
        "chain_breaks", "hook_shot", "shot_plan", "title_patterns", "format_version"
    )
    if any(key in cfg for key in fixedframe_keys) and not (2 <= shots <= 6):
        errors.append("shots 2..6 aralığında tam sayı olmalı")
    if any(key in cfg for key in fixedframe_keys):
        duration = str(cfg.get("shot_seconds", DEFAULT_SHOT_SECONDS)).strip()
        if duration not in VALID_DURATIONS:
            errors.append("shot_seconds 4/6/8/10 değerlerinden biri olmalı")

    if "chain_breaks" in cfg:
        breaks = cfg.get("chain_breaks")
        if not isinstance(breaks, list) or any(
            not isinstance(value, int) or isinstance(value, bool) for value in (breaks or [])
        ):
            errors.append("chain_breaks tam sayı listesi olmalı")
        elif len(set(breaks)) != len(breaks):
            errors.append("chain_breaks benzersiz olmalı")
        elif any(value < 1 or value > shots for value in breaks):
            errors.append(f"chain_breaks değerleri 1..{shots} aralığında olmalı")

    if "hook_shot" in cfg:
        hook = cfg.get("hook_shot")
        if not isinstance(hook, int) or isinstance(hook, bool) or not (1 <= hook <= shots):
            errors.append(f"hook_shot 1..{shots} aralığında tam sayı olmalı")

    if "shot_plan" in cfg:
        shot_plan = cfg.get("shot_plan")
        if not isinstance(shot_plan, list) or len(shot_plan) != shots:
            errors.append(f"shot_plan tam {shots} satır içermeli")
        elif any(not isinstance(line, str) or not line.strip() for line in shot_plan):
            errors.append("shot_plan boş satır içeremez")

    if "title_patterns" in cfg:
        try:
            _compiled_title_patterns(cfg)
        except ValueError as error:
            errors.append(str(error))
    return errors


def strict_plan_validation_enabled(cfg: dict) -> bool:
    """The pre-spend validator is opt-in through Rock 1 plan config keys."""
    return any(key in cfg for key in (
        "chain_breaks", "hook_shot", "shot_plan", "title_patterns", "format_version"
    ))


def _prompt_content(prompt, shot_plan_prefix: str | None = None) -> str:
    """Return the actual shot description, excluding an echoed shot-plan prefix."""
    content = str(prompt or "").strip()
    prefix = str(shot_plan_prefix or "").strip()
    if prefix and content.startswith(prefix):
        remainder = content[len(prefix):]
        if not remainder or remainder[0].isspace():
            content = remainder.strip()
    return content


def validate_plan_against_config(plan: dict, cfg: dict) -> list[str]:
    """Strict, non-normalizing plan validation used by replenish/produce/preflight."""
    errors = list(validate_replenish_config(cfg))
    if errors or not strict_plan_validation_enabled(cfg):
        return errors
    shots_expected = int(cfg.get("shots", DEFAULT_SHOTS))
    duration_expected = str(cfg.get("shot_seconds", DEFAULT_SHOT_SECONDS)).strip()
    format_version = str(cfg.get("format_version") or "").strip()
    if format_version and plan.get("format_version") != format_version:
        errors.append(f"plan format_version tam {format_version!r} olmalı")
    shots = plan.get("shots")
    if not isinstance(shots, list):
        return errors + ["plan shots listesi yok"]
    if len(shots) != shots_expected:
        errors.append(f"çekim sayısı tam {shots_expected} olmalı (gelen: {len(shots)})")
    numbers = [shot.get("n") if isinstance(shot, dict) else None for shot in shots]
    if (len(numbers) != shots_expected or any(
            not isinstance(number, int) or isinstance(number, bool) for number in numbers
        ) or sorted(numbers) != list(range(1, shots_expected + 1))):
        errors.append(f"çekim numaraları tam [1..{shots_expected}] olmalı (gelen: {numbers})")
    for index, shot in enumerate(shots, start=1):
        if not isinstance(shot, dict):
            continue
        if str(shot.get("duration", "")).strip() != duration_expected:
            errors.append(
                f"çekim {shot.get('n', index)} süresi tam {duration_expected} olmalı"
            )
        prefix = None
        if "shot_plan" in cfg and index <= len(cfg["shot_plan"]):
            prefix = cfg["shot_plan"][index - 1].strip() + "\n\n"
        if len(_prompt_content(shot.get("prompt"), prefix)) < 30:
            errors.append(f"çekim {shot.get('n', index)} prompt boş/çok kısa")
    if "chain_breaks" in cfg:
        breaks = set(cfg["chain_breaks"])
        for index, shot in enumerate(shots, start=1):
            if not isinstance(shot, dict):
                continue
            number = shot.get("n", index)
            expected = number not in breaks
            if shot.get("chain") is not expected:
                errors.append(
                    f"çekim {number} chain={expected} olmalı (chain_breaks={sorted(breaks)})"
                )
    if "hook_shot" in cfg and plan.get("hook_shot") != cfg["hook_shot"]:
        errors.append(f"hook_shot tam {cfg['hook_shot']} olmalı")
    if "shot_plan" in cfg:
        for index, shot in enumerate(shots, start=1):
            if not isinstance(shot, dict) or index > len(cfg["shot_plan"]):
                continue
            prefix = cfg["shot_plan"][index - 1].strip() + "\n\n"
            if not str(shot.get("prompt") or "").startswith(prefix):
                errors.append(f"çekim {index} prompt'u shot_plan önekiyle başlamalı")
    patterns = _compiled_title_patterns(cfg) if "title_patterns" in cfg else []
    if patterns:
        title = str((plan.get("episode") or {}).get("title") or "")
        family = str(plan.get("family") or "").strip()
        matching = [(pattern, allowed) for pattern, allowed in patterns if pattern.fullmatch(title)]
        if not matching:
            errors.append(f"başlık title_patterns fullmatch sağlamıyor: {title!r}")
        elif not any(family in allowed for _, allowed in matching):
            errors.append(f"başlık kalıbı family={family!r} ailesine izin vermiyor")
    return errors


# ─── Gemini JSON yardımcıları (omni-studio director kalıbı) ────────────────────

def _parse_json(txt: str):
    """Gemini çıktısını kurtarıcı ayrıştırma: ```json çiti / kırpık uçlar tolere edilir."""
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


def _gen_json(contents: str, system_instruction: str,
              temperature: float = 0.9, max_tries: int = 4) -> dict:
    """Gemini'den JSON iste. Bozuk JSON → aynı modelde tekrar; 429/503 → backoff;
    model ölürse yedek modele geç."""
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY tanımlı değil ,  oto-ikmal için gerekli.")
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=GEMINI_API_KEY)
    cfg = types.GenerateContentConfig(
        system_instruction=system_instruction,
        response_mime_type="application/json",
        temperature=temperature,
    )
    last_err = None
    for model in (REPLENISH_MODEL, REPLENISH_MODEL_FALLBACK):
        for attempt in range(1, max_tries + 1):
            try:
                resp = client.models.generate_content(model=model, contents=contents, config=cfg)
                return _parse_json(resp.text or "")
            except Exception as e:
                last_err = e
                msg = str(e)
                # Bozuk JSON şans işidir ,  AYNI modelden taze üretim genelde geçer;
                # yedek modeli buna harcama.
                bad_json = isinstance(e, json.JSONDecodeError)
                transient = any(s in msg for s in
                                ("503", "429", "500", "UNAVAILABLE", "RESOURCE_EXHAUSTED",
                                 "INTERNAL", "deadline"))
                if (transient or bad_json) and attempt < max_tries:
                    wait = 3 if bad_json else min(5 * attempt, 20)
                    label = "bozuk JSON" if bad_json else "geçici hata"
                    logger.warning(f"⚠️ ikmal {model} {label} ({msg[:60]}…) ,  {wait}s sonra tekrar")
                    time.sleep(wait)
                    continue
                logger.warning(f"⚠️ ikmal {model} başarısız: {msg[:120]}")
                break  # yedek modele geç
    raise RuntimeError(f"Gemini ikmal çağrısı başarısız: {last_err}")


def _alert(msg: str) -> None:
    """Telegram'a sessizce bildir (token yoksa no-op) ,  series_runner._alert eşleniği."""
    try:
        if notifier.enabled():
            notifier.send_message(msg)
    except Exception as e:
        logger.warning(f"⚠️ İkmal bildirimi gönderilemedi: {e}")


# ─── Geçmiş / durum yardımcıları ───────────────────────────────────────────────

def _norm_title(t: str) -> str:
    """Başlık karşılaştırması için normalize et (küçük harf, noktalama at)."""
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def _episode_history(slug: str) -> list[dict]:
    """Plan geçmişini başlık, özet, seed_id ve family alanlarıyla sıralı döndür. Özet yoksa
    (eski elle yazılmış planlar) ilk çekim prompt'unun başı özet sayılır."""
    out: list[dict] = []
    pdir = plans_dir(slug)
    if not pdir.exists():
        return out
    for f in sorted(pdir.glob("part*.json")):
        try:
            plan = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        ep = plan.get("episode") or {}
        syn = str(plan.get("synopsis") or "").strip()
        if not syn:
            shots = plan.get("shots") or []
            if shots:
                syn = str((shots[0] or {}).get("prompt") or "").strip()[:140]
        out.append({"n": ep.get("number"), "title": str(ep.get("title") or "").strip(),
                    "synopsis": syn, "seed_id": plan.get("seed_id"),
                    "family": str(plan.get("family") or "").strip()})
    out.sort(key=lambda item: int(item["n"]) if isinstance(item.get("n"), int) else -1)
    return out


def _adopt_orphans(meta: SeriesMeta) -> int:
    """total_parts'tan büyük numaralı ARDIŞIK plan dosyalarını sahiplen (yarıda kesilmiş
    ikmal veya elle eklenmiş planlar): sayaç dosya sistemine hizalanır, Gemini yeniden
    HARCANMAZ. meta.data güncellenir; kaydetmek çağıranın işi. Sahiplenilen adet döner."""
    n = 0
    total = meta.total_parts
    while part_plan_path(meta.slug, total + 1).exists():
        total += 1
        n += 1
    if n:
        meta.data["total_parts"] = total
    return n


def _doctrine_gate(meta: SeriesMeta) -> str | None:
    """Doktrin dosyasını, içeriğini ve varsa pin'ini doğrula; başarıda hash döndür."""
    path = doctrine_path(meta.slug)
    if path is None:
        logger.error(f"❌ HATA {meta.slug}: doktrin dosyası bulunamadı.")
        return None
    try:
        text = path.read_bytes().decode("utf-8").replace("\r\n", "\n")
    except (OSError, UnicodeError) as exc:
        logger.error(f"❌ HATA {meta.slug}: doktrin okunamadı: {exc}")
        return None
    if not text.strip():
        logger.error(f"❌ HATA {meta.slug}: doktrin dosyası boş.")
        return None
    digest = doctrine_sha256(path)
    if "doctrine_sha256" in meta.data:
        pinned = str(meta.data.get("doctrine_sha256") or "").strip().lower()
        if pinned != digest:
            logger.error(f"❌ HATA {meta.slug}: doctrine_sha256 pin'i güncel doktrinle eşleşmiyor.")
            return None
    logger.info(f"Doktrin: {doctrine_repo_path(path)} sha256={digest}")
    return digest


def _topic_pool(cfg: dict) -> dict[int, dict]:
    """Yapılandırılmış konu havuzunu id ile indeksle."""
    pool: dict[int, dict] = {}
    for item in cfg.get("topic_pool") or []:
        if not isinstance(item, dict):
            continue
        seed_id = item.get("id")
        if not isinstance(seed_id, int) or isinstance(seed_id, bool):
            continue
        pool[seed_id] = item
    return pool


def _unused_topics(cfg: dict, history: list[dict]) -> list[dict]:
    """Mevcut planlarda kullanılmamış havuz girdilerini sıra korunarak döndür."""
    used: set[int] = set()
    for item in history:
        seed_id = item.get("seed_id")
        if isinstance(seed_id, int) and not isinstance(seed_id, bool):
            used.add(seed_id)
    return [item for seed_id, item in _topic_pool(cfg).items() if seed_id not in used]


def _previous_family(history: list[dict]) -> str:
    """Geçmişte family taşıyan son bölümün kanonik değerini döndür."""
    for item in reversed(history):
        family = str(item.get("family") or "").strip()
        if family:
            return family
    return ""


def _freeze(value):
    """Calibration kopyasini kosu boyunca degistirilemez hale getir."""
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def _load_calibration(slug: str) -> Mapping:
    """calibration.json'u bir kez yukle; yok/bozuk dosyada fail-open bos kopya don."""
    path = data_dir(slug) / "calibration.json"
    if not path.exists():
        logger.warning(f"⚠️ {slug}: calibration.json yok, kalibrasyon eki atlandi.")
        return MappingProxyType({})
    try:
        content = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(content, dict):
            raise ValueError("kok JSON nesnesi degil")
        if not content:
            logger.warning(f"⚠️ {slug}: calibration.json bos, kalibrasyon eki atlandi.")
        return _freeze(content)
    except Exception as exc:
        logger.warning(f"⚠️ {slug}: calibration.json bozuk, kalibrasyon eki atlandi: {exc}")
        return MappingProxyType({})


def _card_topics(calibration: Mapping | None) -> dict[str, dict]:
    """Bu kosunun onayli #15 kartlarini id ile indeksle."""
    cards: dict[str, dict] = {}
    for item in (calibration or {}).get("extra_topics") or ():
        if not isinstance(item, Mapping):
            continue
        seed_id = str(item.get("id") or "")
        page_id = str(item.get("page_id") or "")
        topic = str(item.get("topic") or "").strip()
        if not re.fullmatch(r"n15-[0-9a-f]{32}", seed_id) or not page_id or not topic:
            continue
        cards[seed_id] = {
            "id": seed_id,
            "topic": topic[:180],
            "page_id": page_id,
            "claimed_at": str(item.get("claimed_at") or ""),
        }
    return cards


def _unused_cards(calibration: Mapping | None, history: list[dict]) -> list[dict]:
    used = {
        str(item.get("seed_id"))
        for item in history
        if isinstance(item.get("seed_id"), str)
    }
    return [
        item for seed_id, item in _card_topics(calibration).items()
        if seed_id not in used
    ]


# ─── Gemini yönetmen promptu ───────────────────────────────────────────────────

def _build_prompt(meta: SeriesMeta, bible: Bible, cfg: dict, start: int, batch: int,
                  history: list[dict], fix_errors: list[str] | None = None,
                  calibration: Mapping | None = None) -> tuple[str, str]:
    """(contents, system_instruction) döndür. Kurallar salt-görsel, zincir-uyumlu
    (her çekim öncekinin son karesinden morf eder) ve içerik-filtresi-güvenlidir."""
    shots = max(2, int(cfg.get("shots", DEFAULT_SHOTS)))
    sec = str(cfg.get("shot_seconds", DEFAULT_SHOT_SECONDS)).strip()
    if sec not in VALID_DURATIONS:
        sec = DEFAULT_SHOT_SECONDS
    end = start + batch - 1

    # ── Opt-in format bayrakları (auto_replenish cfg; hiçbiri yoksa davranış ESKİSİYLE AYNI) ──
    # narration: true | {"min_words":95,"max_words":125} → bölüm başına anlatım metni istenir
    # title_card: true → plan'a title_card {title, subtitle} alanı istenir (produce künyesi)
    # humans: "silent" → insan figürü serbest (asla konuşmaz/yüz yakın planı yok)
    #         "historical" → dönem insanları yakın planda serbest (the__footnote formatı;
    #         gerçek isimli kişiler prompt'ta ASLA isimle değil görünümle tarif edilir)
    # eerie_ok: true → 'frightening' yasağı kalkar (korku-tonlu kanallar; gore yine yasak)
    # title_style: "<metin>" → başlık kuralını değiştirir (ör. haber-kancası cümle başlıklar)
    # shot_refs: true → çekimler bible'daki characters/environment id'lerini kullanabilir
    # caption: true → bölüm başına 'caption' (yazılı hikâye) + 'hashtags' istenir
    narr_cfg = cfg.get("narration")
    if narr_cfg is True:
        narr_cfg = {}
    narrated = isinstance(narr_cfg, dict)
    wmin = int((narr_cfg or {}).get("min_words", 95))
    wmax = int((narr_cfg or {}).get("max_words", 125))
    # voiceover_continuity (opt-in, shadowedhistory/flashpoints): anlatim yavas
    # belgesel temposunda okunur, TAM CUMLEYLE biter ve cekimler tek kesintisiz
    # seslendirmenin altinda birbirinin devami olur. Bayrak YOKSA prompt eskisiyle
    # BIT-BIT AYNIDIR , diger anlatimli serilerin kelime butcesi bu pencereye gore
    # hesaplanmadigi icin kural onlara dayatilmaz.
    vo_continuity = narrated and bool(cfg.get("voiceover_continuity"))
    speech_window = shots * int(sec) - shots * 2 * bible.micro_trim - 0.7
    want_tc = bool(cfg.get("title_card"))
    want_fc = bool(cfg.get("fact_captions"))
    want_music = bool(cfg.get("music_prompt"))
    want_caption = bool(cfg.get("caption"))
    format_version = str(cfg.get("format_version") or "").strip()
    formatted_object = bool(format_version)
    compose_object_prompt = format_version == TEK_OBJE_FORMAT
    families = [str(v).strip() for v in (cfg.get("families") or []) if str(v).strip()]
    previous_family = _previous_family(history) if families else ""
    pool = _topic_pool(cfg)
    cards = _unused_cards(calibration, history)
    humans_mode = str(cfg.get("humans") or "").strip().lower()
    face_hidden = bible.face_visible is False
    humans_historical = humans_mode == "historical"
    humans_featured = humans_mode == "featured" and not face_hidden
    humans_hands_only = humans_mode == "featured" and face_hidden
    humans_silent = humans_mode in ("silent", "silent-masked", "allowed")
    eerie_ok = bool(cfg.get("eerie_ok"))
    title_style = str(cfg.get("title_style") or "").strip()
    shot_refs = bool(cfg.get("shot_refs")) and not bible.omit_character_refs
    humans_present = (
        humans_historical or humans_featured or humans_hands_only or humans_silent
    )

    if narrated:
        head = (f"You are the showrunner of an endless vertical (9:16) YouTube Shorts series told through\n"
                f"SILENT visual shots plus a POST-PRODUCTION voice-over narration.\n"
                f"Every episode is a STANDALONE ~{shots * int(sec)}-second piece: {shots} consecutive shots (each ONE\n"
                f"continuous moment of {sec} seconds) that flow into one another, plus ONE narration script\n"
                f"({wmin}-{wmax} words) recorded separately and laid over the finished edit. No dialogue, no lip-sync.")
        narr_shape = f'"<{wmin}-{wmax} word English voice-over script>"'
    elif humans_present:
        # Anlatımsız ama İNSANLI seri (the__footnote formatı): tek ses = müzik.
        head = (f"You are the showrunner of an endless, NARRATION-FREE vertical (9:16) Shorts series told\n"
                f"through SILENT cinematic shots ,  the musical score is the only sound.\n"
                f"Every episode is a STANDALONE ~{shots * int(sec)}-second piece: {shots} consecutive shots (each ONE\n"
                f"continuous moment of {sec} seconds). No dialogue, no narration, no lip-sync.")
        narr_shape = '""'
    else:
        head = (f"You are the showrunner of an endless, VISUAL-ONLY vertical (9:16) YouTube Shorts series.\n"
                f"Every episode is a STANDALONE ~{shots * int(sec)}-second visual trip: {shots} consecutive shots (each ONE\n"
                f"continuous moment of {sec} seconds) that morph seamlessly into one another. No dialogue,\n"
                f"no narration, no characters ,  pure visuals.")
        narr_shape = '""'

    tc_shape = ('\n   "title_card": {"title": "<subject name, max 40 chars>", '
                '"subtitle": "<max 48 chars>"},') if want_tc else ""
    music_shape = ('\n   "music": "<40-90 word instrumental music style prompt '
                   'matched to THIS episode>",') if want_music else ""
    cap_shape = ('\n   "caption": "<70-140 word written story of the episode>",'
                 '\n   "hashtags": "<#Tag1 #Tag2 ... 6-9 tags>",') if want_caption else ""
    face_shape = '\n   "face_visible": false,' if face_hidden else ""
    format_shape = (
        f'\n   "format_version": {json.dumps(format_version)},'
        '\n   "object_card": {"name": "<ordinary object name>", '
        '"descriptor": "<colour + material + size + one distinguishing mark, at least 12 words>", '
        '"environment": "<available environment id>", '
        '"framing": "<one fixed-composition sentence>", "anomaly_descriptor": "<how the impossible property LOOKS on screen: material + geometry + light, at least 10 words>"},'
        if formatted_object else ""
    )
    shot_fields = f'"n": <int>, "duration": "{sec}", "prompt": "<visual description>", "seed": null'
    chain_breaks = cfg.get("chain_breaks") if "chain_breaks" in cfg else None
    if chain_breaks is not None:
        shot_fields += ', "chain": <bool>'
    if shot_refs:
        shot_fields += ', "characters": ["<ref id, optional>"], "environment": "<ref id, optional>"'
    elif formatted_object:
        shot_fields += ', "environment": "<object_card.environment>"'
        shot_fields += (', "violation_observation": "<one positive, observable outcome of the impossible property in THIS shot>"'
                        ', "state_carry": "<optional: a lasting trace this shot leaves for the NEXT shot>"')
    if want_fc:
        shot_fields += ', "fact": "<2-5 word on-screen fact, optional>"'

    title_rule = title_style or ('2-4 words, poetic, curiosity-driven ,  the title IS the YouTube title of a\n'
                                 '  standalone video (like "Bloom" or "The Last Door"). No drug slang, no clickbait\n'
                                 '  punctuation.')
    narr_pace_rule = (
        f" It will be read at a measured documentary pace of ~2 words per second; the total "
        f"speaking window is {speech_window:.1f} seconds, and the complete narration must fit inside it."
        f"\n- NARRATION COMPLETENESS: The voice-over is ONE continuous, unbroken spoken flow and "
        f"must end with a complete sentence. Never end mid-sentence, with an ellipsis (\"...\"), "
        f"or with a cliffhanger fragment. If a sentence crosses the cut, it must be heard as one "
        f"unbroken sentence."
    ) if vo_continuity else ""
    narr_rule = ((f"\n- NARRATION: {wmin}-{wmax} words of spoken English voice-over for the WHOLE episode ,  "
                  f"flowing prose, no camera directions, no shot numbers; follow the CREATIVE BRIEF strictly."
                  + narr_pace_rule)
                 if narrated else "")
    tc_rule = ('\n- TITLE_CARD: "title" = the subject/site name (max 40 chars); "subtitle" = place and year '
               'exactly as the CREATIVE BRIEF instructs (max 48 chars).' if want_tc else "")
    fact_rule = ('\n- FACT_CAPTIONS: give a "fact" to 2-4 shots ,  a punchy 2-5 word hard fact from the entry '
                 'that is literally on screen in THAT shot (a depth, an age, a count, a death toll, a date), '
                 'e.g. "45 METERS DEEP", "2,000 YEARS OLD", "ONE DIVER DIED". They are burned low on screen '
                 'while the viewer watches. NO "fact" on the final resolve shot; omit "fact" where the shot '
                 'shows nothing concrete. NEVER invent a number ,  every fact must come from the brief entry.'
                 if want_fc else "")
    music_style = str(cfg.get("music_style") or "").strip()
    music_rule = ('\n- MUSIC: "music" = a 40-90 word ENGLISH prompt for an AI music generator, composed '
                  'TOGETHER with the visuals so score and image share one soul: name genre, mood, 2-4 '
                  'instruments, rough tempo (slow/glacial), and an arc that mirrors the episode (open '
                  'atmospheric → swell → sustained emotional peak → gentle end). INSTRUMENTAL only, no '
                  'vocals, no drums unless the scene demands a pulse. The track starts playing from its '
                  'very first second, so it must open with immediate atmosphere ,  no long silent intro. '
                  'Each episode gets a CLEARLY different musical color (vary instruments/scale/texture).'
                  if want_music else "")
    if want_music and music_style:
        music_rule = (
            '\n- MUSIC: "music" = a 40-90 word ENGLISH prompt for an AI music generator. '
            f'Follow this SERIES MUSIC STYLE exactly: {music_style}'
        )
    cap_rule = ('\n- CAPTION: "caption" = the post\'s WRITTEN STORY (70-140 words of flowing English '
                'prose; separate paragraphs with \\n\\n). Open with "City, YEAR." plus ONE vivid '
                'scene-setting line, then short 1-2 sentence paragraphs that tell the REAL event like '
                'a documentary: context, escalation, the event itself, one human moment (a real name '
                'where history records one), the precise date, and a final line about what it left '
                'behind. Every name, number and date must be real and verifiable from the CREATIVE '
                'BRIEF ,  NEVER invent or embellish a fact; when unsure of a number, leave it out.'
                '\n- HASHTAGS: "hashtags" = 6-9 space-separated tags: the city, the event name, the '
                '4-digit year, the country or people, plus 2-3 broad history tags. Each tag starts '
                'with # and contains no spaces.' if want_caption else "")
    if formatted_object:
        refs_rule = (
            '\n- ENVIRONMENT: every shot must set "environment" to the object_card.environment id, '
            'chosen exactly from AVAILABLE REFERENCES.'
        )
    else:
        refs_rule = ('\n- Shots MAY reference ONLY the ids listed under AVAILABLE REFERENCES via "characters" / '
                     '"environment"; follow the brief about when to use them.' if shot_refs else "")
    if humans_historical:
        humans_rule = ("period-accurate people MAY appear in clear close-up, mid and wide shots and "
                       "carry the episode's emotion, but must NEVER speak, lip-sync or move their lips "
                       "as if talking (the score is the only voice); when the story involves a real "
                       "named person, shot prompts describe them ONLY by appearance, age, dress and "
                       "role ,  never by name,")
    elif humans_featured:
        humans_rule = ("the recurring lead character (see AVAILABLE REFERENCES) MAY appear in clear close-up, "
                       "mid and wide shots and is the emotional anchor of the episode, but must NEVER speak, "
                       "lip-sync or move their lips as if talking (the voice is added later as narration); "
                       "other people may appear around them,")
    elif humans_hands_only:
        humans_rule = ("the recurring worker is represented by hands and forearms working at bench level, "
                       "and every composition keeps the face outside the frame,")
    elif humans_silent:
        humans_rule = ("human figures may appear but must NEVER speak, lip-sync or show a clear close-up face "
                       "(masked, distant, silhouetted or from behind only),")
    else:
        humans_rule = "no humans or human faces,"
    tone_tail = "nothing gory, violent or graphic." if eerie_ok else "nothing gory, violent or frightening."
    # Kare zinciri AÇIK serilerde çekimler tek kesintisiz morf akışıdır; zincirsiz
    # serilerde (chain_frames=false, ör. footnotes) her çekim AYRI bir sinematik
    # tablodur ,  kurgu bunları crossfade/kesme ile bağlar.
    if formatted_object:
        chain_rule = (
            "- FIXED COMPOSITION: All shots share ONE fixed composition on the same everyday "
            "surface in the same light; the cuts are jumps in time only."
        )
    elif chain_breaks is not None:
        chain_rule = (
            "- SEGMENTED CHAIN (the engine enforces this mechanically): shots "
            f"{json.dumps(chain_breaks)} MUST have chain=false and start a fresh scene; every other "
            "shot MUST have chain=true and begin from the previous shot's final frame. A chained shot "
            "may never reset, cut, teleport, or change the locked camera established by its segment."
        )
    elif bible.chain_frames:
        chain_rule = ("- SEAMLESS CHAIN (the engine literally starts each shot from the PREVIOUS shot's final\n"
                      "  frame): shot 1 opens a brand-new striking scene; every later shot's prompt must\n"
                      "  describe ONE continuous transformation that begins EXACTLY at the previous shot's end\n"
                      "  state and evolves into somewhere new. No cuts, no teleports, no scene resets inside\n"
                      "  an episode.")
    elif vo_continuity:
        cont_lead = ("Shot 2 directly continues shot 1's exact same moment and scene"
                     if shots == 2 else
                     "Each shot directly continues the previous shot's exact same moment and scene")
        chain_rule = ("- VOICE-OVER CONTINUITY: Shots are silent visual segments beneath one continuous "
                      f"voice-over. {cont_lead}; the cut "
                      "must not reset the location or open a new scene. The spoken sentence remains audibly "
                      "unbroken across the cut.")
    else:
        chain_rule = ("- SCENE FLOW: shots are DISTINCT cinematic tableaux joined in post by soft transitions , \n"
                      "  each shot may open a new angle, location or moment of the SAME story; order them so the\n"
                      "  episode reads as one continuous emotional arc with no confusing jumps.")

    object_rule = (
        '\n- OBJECT_CARD: output exactly one object_card. Its descriptor states colour, material, '
        'size and one distinguishing mark in at least 12 words. Write one fixed-composition sentence '
        'in object_card.framing. Each shot\'s "prompt" field contains ONLY that shot\'s specific '
        'action and state, described only by what IS visible and happening. FORBIDDEN WORDS in every '
        'shot prompt (they poison the video model): no, not, never, nothing, neither, nor, without, '
        'cannot, cant, dont, doesnt, isnt, arent, wont, absent, lacks, lacking, avoid. State what '
        'happens in positive terms; the construction "instead of" is forbidden too. Write '
        '"the shell stays whole" rather than "the shell does not crack". '
        'It must NOT repeat the descriptor, the framing sentence or the room description because '
        'the pipeline composes them mechanically. Anchor the descriptor\'s identity in large '
        'durable marks (body colour, surface texture, cut faces); leave out fragile micro-details '
        'such as stems, leaves or printed labels. Choose the object_card.environment id of the '
        'room where this exact object naturally lives in a real home; all four shots use that '
        'same id.'
        ' Also write object_card.anomaly_descriptor: how the impossible property itself '
        'LOOKS on screen (material, geometry, light) in at least 10 words; the pipeline '
        'composes it into every shot, so do NOT repeat it inside the shot text. '
        'For every shot give violation_observation: ONE positive, directly observable '
        'outcome of the impossible property in that shot, written so a viewer could '
        'confirm it from the frames alone; never phrase it as something that fails to '
        'happen. Where a shot leaves a lasting trace the next shot must still show '
        '(a puddle, a crushed can, a groove), add state_carry to the shot that CREATES '
        'it; the pipeline copies that exact state_carry sentence verbatim into the NEXT '
        'shot prompt, so the next action must agree with it. The final shot never carries state_carry. '
        'SHOT 1 ONSET: describe the anomaly as an ongoing, visible STATE already at its most '
        'extreme in the very first frame. Onset phrases such as "begins to" and "starts to" '
        'are forbidden in shot 1. BAD: "the soap stays rigid and begins to crack like glass". '
        'GOOD: "the bar is already split along a bright conchoidal fracture, its glassy '
        'translucent edge glinting under the water". '
        'OBJECT IDENTITY AND ANOMALY MUST AGREE: descriptor and anomaly_descriptor are composed into ONE hero reference image, so they must never contradict each other about the same surfaces, edges or material. Write object_card.descriptor as the object LOOKS WHILE the anomaly is active; when the anomaly changes the object\'s own geometry or material, describe the changed object, never its intact "before" state. BAD: descriptor "smooth rounded edges" with anomaly "sharp fracture edges and glossy shards". GOOD: descriptor "one bright glassy break face along its long edge" with anomaly "sharp conchoidal fracture edges and glossy translucent shards".'
        if compose_object_prompt else
        '\n- OBJECT_CARD: output exactly one object_card. Its descriptor states colour, material, '
        'size and one distinguishing mark in at least 12 words. Copy that descriptor VERBATIM '
        'into every one of the four shot prompts. Write one framing sentence in object_card.framing '
        'Write object_card.anomaly_descriptor as well: how the impossible property '
        'itself LOOKS on screen (material, geometry, light) in at least 10 words, and '
        'copy THAT verbatim into every shot prompt too. '
        'and copy it VERBATIM into every shot prompt. All four shots use the same '
        'object_card.environment id. Shot prompts use positive visual language only. '
        'SHOT 1 ONSET: describe the anomaly as an ongoing, visible STATE already at its most '
        'extreme in the very first frame. Onset phrases such as "begins to" and "starts to" '
        'are forbidden in shot 1. BAD: "the soap stays rigid and begins to crack like glass". '
        'GOOD: "the bar is already split along a bright conchoidal fracture, its glassy '
        'translucent edge glinting under the water". '
        'OBJECT IDENTITY AND ANOMALY MUST AGREE: descriptor and anomaly_descriptor are composed into ONE hero reference image, so they must never contradict each other about the same surfaces, edges or material. Write object_card.descriptor as the object LOOKS WHILE the anomaly is active; when the anomaly changes the object\'s own geometry or material, describe the changed object, never its intact "before" state. BAD: descriptor "smooth rounded edges" with anomaly "sharp fracture edges and glossy shards". GOOD: descriptor "one bright glassy break face along its long edge" with anomaly "sharp conchoidal fracture edges and glossy translucent shards".'
        if formatted_object else ""
    )
    episode_arc_rule = (
        "- EPISODE ARC: All shots share ONE fixed composition on the same everyday surface in "
        "the same light; the cuts are jumps in time only."
        if formatted_object else
        "- EPISODE ARC: striking opening → build → peak spectacle → gentle, loopable resolve."
    )
    prompts_rule = (
        "- PROMPTS: All shots share ONE fixed composition on the same everyday surface in the "
        "same light; the cuts are jumps in time only. Use rich visual language for motion, "
        "geometry, light and color within that composition. The series art style is automatically "
        "prefixed to every shot at production; stay inside it."
        if formatted_object else
        "- PROMPTS: rich visual language ,  motion, geometry, light, color, camera flow. The\n"
        "  series art style is automatically prefixed to every shot at production; do NOT restate\n"
        "  it wholesale, but stay inside it."
    )
    hard_limits_rule = (
        f"- HARD LIMITS: {humans_rule} natural lived-in unlabeled surfaces and grounded safe "
        "everyday home activity fill the frame. English only."
        if formatted_object else
        f"- HARD LIMITS: {humans_rule} no readable text/letters/logos/watermarks,\n"
        f"  {tone_tail} English only."
    )

    family_shape = '\n   "family": "<canonical family>",' if families else ""
    seed_shape = '\n   "seed_id": <int or "n15-32hex">,' if (pool or cards) else ""
    family_rule = (
        "\n- FAMILY: every episode must include one \"family\" chosen exactly from this canonical list: "
        + json.dumps(families, ensure_ascii=False)
        + ". Consecutive episodes must never use the same family."
        if families else ""
    )
    first_family_rule = (
        f'\n- CRITICAL FAMILY BLOCK FOR EPISODE {start}: The previous episode used '
        f'{json.dumps(previous_family, ensure_ascii=False)}, so episode {start} must not use '
        f'{json.dumps(previous_family, ensure_ascii=False)}.'
        if previous_family else ""
    )
    if cards:
        seed_rule = (
            "\n- TOPIC POOL: every episode must include \"seed_id\" from the runtime pools in the "
            "input and use only that seed's topic. Card topics are approved external signals and "
            "MUST be consumed first. Integer seeds must copy their seed family exactly; card seeds "
            "choose one canonical family. Never invent a topic."
        )
    elif pool:
        seed_rule = (
            "\n- TOPIC POOL: every episode must include integer \"seed_id\" from the runtime pool in the "
            "input, use only that seed's topic, and copy that seed's family exactly. Never invent a topic."
        )
    else:
        seed_rule = ""
    face_rule = (
        '\n- FACE FRAMING: set "face_visible" to false; compose every shot around the hands, '
        'forearms, object and work surface, with the face outside the frame.'
        if face_hidden else ""
    )
    if pool and previous_family:
        seed_rule += (
            f' For integer seed_id in episode {start}, choose only from the runtime pool explicitly '
            'labeled for the first episode. Later episodes may use the later-episode pool.'
        )
    if "hook_shot" in cfg:
        hook_rule = (
            f'- "hook_shot" MUST be {int(cfg["hook_shot"])}. That shot is the teaser source.'
        )
    elif meta.slug == "from-scratch":
        hook_rule = (
            '- "hook_shot" MUST be 4. Shot 4 is the final reveal and the teaser source.'
        )
    else:
        hook_rule = (
            '- "hook_shot" = the n of the single most spectacular, jaw-dropping shot '
            "(usually 2 or 3)."
        )

    shot_plan = cfg.get("shot_plan") if "shot_plan" in cfg else None
    shot_plan_rule = ""
    if shot_plan is not None:
        numbered = "\n".join(
            f"  Shot {index}: {str(line).strip()}"
            for index, line in enumerate(shot_plan, start=1)
        )
        shot_plan_rule = (
            "\n- SHOT_PLAN: obey every numbered line exactly; the engine also prefixes the matching "
            f"line to each production prompt:\n{numbered}"
        )

    system_instruction = f"""{head}

Return STRICT JSON ONLY, exactly this shape:
{{"episodes": [
  {{"episode": {{"number": <int>, "title": "<title>"}},
   "synopsis": "<one sentence>",{face_shape}{format_shape}
   "hook_shot": <int>,{family_shape}{seed_shape}
   "narration": {narr_shape},{tc_shape}{music_shape}{cap_shape}
   "shots": [{{{shot_fields}}}]}}
]}}

RULES:
- Produce EXACTLY {batch} episodes, numbered {start} to {end}, in this order.{first_family_rule}
- Each episode has EXACTLY {shots} shots, every shot with "duration": "{sec}".
- TITLES: {title_rule} All {batch} titles must be distinct from each other AND from every
  EXISTING episode listed in the input; never repeat or lightly reword one.
- "synopsis": ONE specific sentence describing this episode (it is
  stored and used to keep future episodes fresh).{family_rule}{seed_rule}{narr_rule}{tc_rule}{fact_rule}{music_rule}{cap_rule}{refs_rule}{face_rule}{object_rule}
{chain_rule}{shot_plan_rule}
{episode_arc_rule}
{hook_rule}
{prompts_rule}
{hard_limits_rule}"""

    lines = [f"SERIES: {meta.base_title} ,  {meta.logline}".strip()]
    art = (bible.art_style or "").strip()
    if art:
        lines.append(f"\nART STYLE (auto-prefixed to every shot at production):\n{art}")
    brief = str(cfg.get("brief") or "").strip()
    if brief:
        lines.append(f"\nCREATIVE BRIEF for new episodes:\n{brief}")
    brief_note = str((calibration or {}).get("brief_note") or "").strip()
    if brief_note:
        lines.append(
            "\nCALIBRATION (weekly measured audience feedback, follow unless it contradicts the brief):\n"
            + brief_note
        )
    if cards:
        lines.append(
            "\nRUNTIME APPROVED CARD TOPICS. Card topics are approved external signals "
            "and MUST be consumed first:"
        )
        lines.append(json.dumps(cards, ensure_ascii=False, indent=2))
    if pool:
        unused_topics = _unused_topics(cfg, history)
        if previous_family:
            first_topics = [
                item for item in unused_topics
                if str(item.get("family") or "").strip() != previous_family
            ]
            lines.append(
                f"\nRUNTIME UNUSED TOPIC POOL FOR FIRST EPISODE {start}. "
                f"Family {json.dumps(previous_family, ensure_ascii=False)} is forbidden here; "
                "its seeds are intentionally not offered for this position:"
            )
            lines.append(json.dumps(first_topics, ensure_ascii=False, indent=2))
            if batch > 1:
                lines.append(
                    f"\nRUNTIME UNUSED TOPIC POOL FOR LATER EPISODES {start + 1}-{end}. "
                    "Use each seed_id at most once across the batch; seeds omitted from the first "
                    "position remain valid here:"
                )
                lines.append(json.dumps(unused_topics, ensure_ascii=False, indent=2))
        else:
            lines.append("\nRUNTIME UNUSED TOPIC POOL. Use each seed_id at most once:")
            lines.append(json.dumps(unused_topics, ensure_ascii=False, indent=2))
    if shot_refs or formatted_object:
        refs_lines = []
        ref_kinds = ("characters", "environments") if shot_refs else ("environments",)
        for kind in ref_kinds:
            items = bible.data.get(kind) or []
            entries = [f"{it.get('id')} ,  {(it.get('name') or it.get('desc') or '')[:60]}"
                       for it in items if it.get("id")]
            if entries:
                refs_lines.append(f"{kind}: " + "; ".join(entries))
        if refs_lines:
            lines.append("\nAVAILABLE REFERENCES (use these ids only):\n" + "\n".join(refs_lines))
    if history:
        lines.append("\nEXISTING EPISODES (title ,  synopsis). NEVER repeat or reword these:")
        for h in history:
            n = h.get("n")
            tag = f"{int(n):02d}" if isinstance(n, int) else "??"
            lines.append(f"{tag}. {h['title']} ,  {h['synopsis']}")
    if fix_errors:
        lines.append("\nYOUR PREVIOUS ATTEMPT WAS REJECTED. Fix ALL of these problems:")
        lines.extend(f"- {e}" for e in fix_errors)
    lines.append(f"\nWrite episodes {start}-{end} now. Each episode picks a FRESH theme "
                 f"and color palette, clearly different from the existing episodes.")
    return "\n".join(lines), system_instruction


def _validate_batch(episodes, bible: Bible, start: int, batch: int,
                    existing_titles: set[str], cfg: dict | None = None,
                    history: list[dict] | None = None,
                    calibration: Mapping | None = None) -> list[str]:
    """Sert doğrulama + normalizasyon (yerinde): numaralar/çekim n'leri düzeltilir,
    bilinmeyen alanlar atılır. Hata listesi döner (boş = geçerli).
    cfg (auto_replenish) format bayraklarını taşır: narration/title_card/shot_refs , 
    bkz. _build_prompt; bayrak yoksa davranış eskisiyle birebir aynıdır."""
    if not isinstance(episodes, list) or len(episodes) != batch:
        got = len(episodes) if isinstance(episodes, list) else type(episodes).__name__
        return [f"'episodes' tam {batch} bölüm olmalı (gelen: {got})"]

    cfg = cfg or {}
    cfg_errors = validate_replenish_config(cfg)
    if cfg_errors:
        return [f"auto_replenish cfg: {error}" for error in cfg_errors]
    if "chain_breaks" in cfg and not bible.chain_frames:
        return ["auto_replenish cfg: chain_breaks için bible.series.chain_frames=true olmalı"]
    narr_cfg = cfg.get("narration")
    if narr_cfg is True:
        narr_cfg = {}
    narrated = isinstance(narr_cfg, dict)
    wmin = int((narr_cfg or {}).get("min_words", 95))
    wmax = int((narr_cfg or {}).get("max_words", 125))
    want_tc = bool(cfg.get("title_card"))
    want_fc = bool(cfg.get("fact_captions"))
    want_music = bool(cfg.get("music_prompt"))
    want_caption = bool(cfg.get("caption"))
    shot_refs = bool(cfg.get("shot_refs")) and not bible.omit_character_refs
    format_version = str(cfg.get("format_version") or "").strip()
    formatted_object = bool(format_version)
    compose_object_prompt = format_version == TEK_OBJE_FORMAT
    families = [str(v).strip() for v in (cfg.get("families") or []) if str(v).strip()]
    pool = _topic_pool(cfg)
    history = history or []
    cards = _card_topics(calibration)
    unused_cards = {
        item["id"]: item for item in _unused_cards(calibration, history)
    }
    used_seed_ids: set[int] = set()
    used_card_ids: set[str] = set()
    for item in history:
        seed_id = item.get("seed_id")
        if isinstance(seed_id, int) and not isinstance(seed_id, bool):
            used_seed_ids.add(seed_id)
        elif isinstance(seed_id, str):
            used_card_ids.add(seed_id)
    previous_family = _previous_family(history)

    errors: list[str] = []
    seen = set(existing_titles)
    for i, plan in enumerate(episodes):
        want = start + i
        if not isinstance(plan, dict):
            errors.append(f"part {want}: bölüm JSON nesnesi değil")
            continue
        ep = plan.get("episode") or {}
        if ep.get("number") != want:
            logger.warning(f"⚠️ İkmal: bölüm numarası {ep.get('number')!r} → {want} düzeltildi")
        title = str(ep.get("title") or "").strip()
        if not title or len(title) > 60:
            errors.append(f"part {want}: başlık boş veya 60 karakterden uzun")
        else:
            nt = _norm_title(title)
            if nt in seen:
                errors.append(f"part {want}: başlık tekrarı ('{title}') ,  özgün başlık gerekli")
            seen.add(nt)

        family = str(plan.get("family") or "").strip()
        if families:
            if not family:
                errors.append(f"part {want}: family alanı zorunlu")
            elif family not in families:
                errors.append(f"part {want}: family kanonik listede değil ({family!r})")
            if family and previous_family and family == previous_family:
                errors.append(
                    f"part {want}: ardışık iki part aynı family değerini kullanamaz "
                    f"(yasak family: {previous_family!r})"
                )
            if family:
                previous_family = family

        if "title_patterns" in cfg and title:
            matches = [
                allowed for pattern, allowed in _compiled_title_patterns(cfg)
                if pattern.fullmatch(title)
            ]
            if not matches:
                errors.append(f"part {want}: başlık title_patterns fullmatch sağlamıyor: {title!r}")
            elif not any(family in allowed for allowed in matches):
                errors.append(
                    f"part {want}: başlık kalıbı family={family!r} ailesine izin vermiyor"
                )

        seed_id = None
        card = None
        if pool or cards:
            raw_seed = plan.get("seed_id")
            if isinstance(raw_seed, str):
                seed_id = raw_seed
                if seed_id not in cards:
                    errors.append(f"part {want}: seed_id bu kosunun kart havuzunda yok ({seed_id})")
                elif seed_id in used_card_ids:
                    errors.append(f"part {want}: kart seed_id daha once kullanilmis ({seed_id})")
                else:
                    card = cards[seed_id]
                    used_card_ids.add(seed_id)
            elif isinstance(raw_seed, int) and not isinstance(raw_seed, bool):
                seed_id = raw_seed
            else:
                errors.append(f"part {want}: seed_id tam sayi veya onayli kart id olmali")
            if isinstance(seed_id, int):
                if seed_id not in pool:
                    errors.append(f"part {want}: seed_id konu havuzunda yok ({seed_id})")
                elif seed_id in used_seed_ids:
                    errors.append(f"part {want}: seed_id daha önce kullanılmış ({seed_id})")
                else:
                    expected_family = str(pool[seed_id].get("family") or "").strip()
                    if family != expected_family:
                        errors.append(f"part {want}: family seed_id {seed_id} ile eşleşmiyor")
                    used_seed_ids.add(seed_id)

        raw_card = plan.get("object_card")
        card_descriptor = (
            raw_card.get("descriptor")
            if isinstance(raw_card, dict) and isinstance(raw_card.get("descriptor"), str)
            else ""
        )
        card_anomaly = (
            raw_card.get("anomaly_descriptor")
            if isinstance(raw_card, dict) and isinstance(raw_card.get("anomaly_descriptor"), str)
            else ""
        )
        card_framing = (
            raw_card.get("framing")
            if isinstance(raw_card, dict) and isinstance(raw_card.get("framing"), str)
            else ""
        )
        # Oda gerçekçiliği mekanik kilittir: ortam tarifi bible'dan alınır ve
        # prompt'a kodla eklenir; LLM'den odayı yeniden yazması istenmez.
        card_env_desc = ""
        if isinstance(raw_card, dict) and isinstance(raw_card.get("environment"), str):
            card_env_entry = bible.get("environments", raw_card["environment"]) or {}
            card_env_desc = str(card_env_entry.get("desc") or "").strip()
        raw_shots = plan.get("shots")
        clean_shots: list[dict] = []
        previous_state_carry = ""
        fact_count = 0
        strict_chain = "chain_breaks" in cfg
        strict_structure = strict_chain or formatted_object
        expected_shots = int(cfg.get("shots", DEFAULT_SHOTS))
        if formatted_object and plan.get("format_version") != format_version:
            errors.append(f"part {want}: format_version tam {format_version!r} olmalı")
        if strict_structure and isinstance(raw_shots, list) and len(raw_shots) != expected_shots:
            errors.append(
                f"part {want}: çekim sayısı tam {expected_shots} olmalı (gelen: {len(raw_shots)})"
            )
        if not isinstance(raw_shots, list) or not (2 <= len(raw_shots) <= 6):
            got = len(raw_shots) if isinstance(raw_shots, list) else "yok"
            errors.append(f"part {want}: çekim sayısı 2-6 olmalı (gelen: {got})")
        else:
            if strict_structure:
                raw_numbers = [
                    shot.get("n") if isinstance(shot, dict) else None for shot in raw_shots
                ]
                if (any(not isinstance(number, int) or isinstance(number, bool)
                        for number in raw_numbers)
                        or sorted(raw_numbers) != list(range(1, expected_shots + 1))):
                    errors.append(
                        f"part {want}: çekim numaraları tam [1..{expected_shots}] olmalı "
                        f"(gelen: {raw_numbers})"
                    )
                else:
                    raw_shots = sorted(raw_shots, key=lambda shot: shot["n"])
            for k, shot in enumerate(raw_shots, start=1):
                shot = shot if isinstance(shot, dict) else {}
                model_action_text = str(shot.get("prompt") or "").strip()
                prompt = model_action_text
                shot_number = shot.get("n") if strict_structure else k
                prefix = None
                if ("shot_plan" in cfg and isinstance(shot_number, int)
                        and 1 <= shot_number <= len(cfg["shot_plan"])):
                    prefix = cfg["shot_plan"][shot_number - 1].strip() + "\n\n"
                    if not prompt.startswith(prefix):
                        prompt = prefix + prompt
                if len(_prompt_content(prompt, prefix)) < 30:
                    errors.append(f"part {want} çekim {k}: prompt boş/çok kısa")
                if compose_object_prompt:
                    composed_action_text = prompt
                    prompt = " ".join(part for part in (
                        card_descriptor if card_descriptor not in composed_action_text else "",
                        # ROCK B: anomalinin görsel imzası da MEKANİK eklenir;
                        # LLM'den tekrar etmesi istenmez (descriptor kilidiyle aynı felsefe).
                        card_anomaly if card_anomaly not in composed_action_text else "",
                        card_framing if card_framing not in composed_action_text else "",
                        card_env_desc if card_env_desc not in composed_action_text else "",
                        previous_state_carry
                        if previous_state_carry not in composed_action_text else "",
                        composed_action_text,
                    ) if part)
                try:
                    dur = str(int(float(str(shot.get("duration", "")).strip() or "0")))
                except (TypeError, ValueError):
                    dur = ""
                if dur not in VALID_DURATIONS:
                    errors.append(f"part {want} çekim {k}: süre {shot.get('duration')!r} "
                                  f"geçersiz (4/6/8/10 olmalı)")
                if strict_chain and dur != str(cfg.get("shot_seconds", DEFAULT_SHOT_SECONDS)).strip():
                    errors.append(
                        f"part {want} çekim {shot_number}: süre tam "
                        f"{str(cfg.get('shot_seconds', DEFAULT_SHOT_SECONDS)).strip()} olmalı"
                    )
                if formatted_object and shot.get("duration") != "6":
                    errors.append(f"part {want} çekim {shot_number}: süre tam '6' string olmalı")
                # Yalnız bilinen alanlar; model karakter/diyalog uydurduysa sessizce atılır.
                clean = {"n": shot_number, "duration": dur, "prompt": prompt, "seed": None}
                if strict_chain:
                    expected_chain = shot_number not in set(cfg["chain_breaks"])
                    if shot.get("chain") is not expected_chain:
                        errors.append(
                            f"part {want} çekim {shot_number}: chain={expected_chain} olmalı"
                        )
                    clean["chain"] = shot.get("chain")
                if shot_refs:
                    # Opt-in: bible'da GERÇEKTEN var olan referans id'leri korunur.
                    env = shot.get("environment")
                    if env and bible.get("environments", str(env)):
                        clean["environment"] = str(env)
                    chars = [c for c in (shot.get("characters") or [])
                             if isinstance(c, str) and bible.get_character(c)]
                    if chars:
                        clean["characters"] = chars
                elif formatted_object:
                    env = shot.get("environment")
                    if env is not None:
                        clean["environment"] = env
                if compose_object_prompt:
                    for field in ("violation_observation", "state_carry"):
                        value = shot.get(field)
                        if isinstance(value, str) and value.strip():
                            clean[field] = value.strip()
                    previous_state_carry = clean.get("state_carry", "")
                if want_fc:
                    # Opt-in: kısa ekran-içi 'fact' (≤40 karakter); produce alt üçlüğe basar.
                    fv = str(shot.get("fact") or "").strip()
                    if fv:
                        clean["fact"] = fv[:40].strip()
                        fact_count += 1
                clean_shots.append(clean)

        if want_fc and clean_shots and fact_count < 2:
            errors.append(f"part {want}: fact_captions açık ,  en az 2 çekimde 'fact' olmalı "
                          f"(gelen: {fact_count})")

        hook = plan.get("hook_shot")
        try:
            hook = int(hook)
            if not (1 <= hook <= len(clean_shots)):
                raise ValueError
        except (TypeError, ValueError):
            hook = None   # produce.py'nin 'sondan bir önceki' varsayılanı devreye girer
        if "hook_shot" in cfg and hook != cfg["hook_shot"]:
            errors.append(f"part {want}: hook_shot {cfg['hook_shot']} olmalı")
        elif "hook_shot" not in cfg and bible.slug == "from-scratch" and hook != 4:
            errors.append(f"part {want}: from-scratch hook_shot 4 olmalı")

        ntext = str(plan.get("narration") or "").strip()
        if narrated:
            wc = len(ntext.split())
            # Hedef aralik (wmin-wmax) prompt'ta; kabul araligi mikser payiyla genisler:
            # TTS mikseri 1.15x hizlandirmayi karsilar (ffmpeg_tools.mix_voiceover tavani),
            # alt sinirda %15 pay ince ama teknik olarak sorunsuz anlatimi gecirir.
            # Olcusuz eski 0.7x-1.35x toleransi DEGIL; sinir mikser kapasitesidir.
            lo = max(1, int(wmin * 0.85))
            # voiceover_continuity acikken tolerans MIKSORUN GERCEK tavanina
            # baglidir (NARRATION_MAX_TEMPO). Sabit 1.15 birakilirsa miksor
            # tavani dustugu icin band uyusmaz ve her bolumde video uzatilir.
            tolerance = NARRATION_MAX_TEMPO if cfg.get("voiceover_continuity") else 1.15
            hi = int(wmax * tolerance + 0.999)
            if not (lo <= wc <= hi):
                errors.append(f"part {want}: anlatım {wc} kelime ,  hedef {wmin}-{wmax} "
                              f"(kabul {lo}-{hi}) dışında")
        else:
            ntext = ""   # anlatımsız seri: eski davranış (boş string zorlanır)

        normalized = {"episode": {"number": want, "title": title},
                      "synopsis": str(plan.get("synopsis") or "").strip()[:300],
                      "narration": ntext,
                      "shots": clean_shots}
        if formatted_object:
            normalized["format_version"] = plan.get("format_version")
            normalized["object_card"] = (
                {field: raw_card.get(field) for field in OBJECT_CARD_FIELDS}
                if isinstance(raw_card, dict) else raw_card
            )
        if bible.face_visible is False:
            if plan.get("face_visible") is not False:
                errors.append(f"part {want}: face_visible tam false olmalı")
            normalized["face_visible"] = False
        if families:
            normalized["family"] = family
        if (pool or cards) and seed_id is not None:
            normalized["seed_id"] = seed_id
        if card is not None:
            normalized["card_page_id"] = card["page_id"]
            normalized["card_topic"] = card["topic"]
        if want_music:
            mtext = str(plan.get("music") or "").strip()
            mwc = len(mtext.split())
            if not (20 <= mwc <= 140):
                errors.append(f"part {want}: music prompt {mwc} kelime ,  40-90 hedef "
                              f"(kabul 20-140) dışında")
            else:
                normalized["music"] = mtext
        if want_tc:
            tcv = plan.get("title_card") or {}
            tt = str(tcv.get("title") or "").strip()
            ts = str(tcv.get("subtitle") or "").strip()
            # Künye GERÇEK bir 4-haneli yıl taşımalı (1000-2099) ,  başlıkta VEYA alt
            # yazıda (footnotes formatı yılı başlığa koyar: 'Barcelona, 1909'; drowned
            # alt yazıya: '… ,  found 1901'). Ekrana basılan tarih doğruluğu güvencesi:
            # model tarihi düşürür ya da uydurursa batch reddedilir → Gemini yeniden
            # dener (brief: yıl DOĞRUDAN kaynak kayıttan kopyalanır).
            anchor_text = f"{tt} {ts}"
            has_year = bool(re.search(r"\b(1[0-9]{3}|20[0-9]{2})\b", anchor_text))
            if bible.slug == "flashpoints":
                has_year = has_year or bool(
                    re.search(
                        r"\b(?:\d{1,4}\s*(?:BCE|BC|CE|AD)|"
                        r"(?:BCE|BC|CE|AD)\s*\d{1,4})\b|"
                        r"\b(?:1[0-9]{3}|20[0-9]{2})s\b|"
                        r"\b\d{1,2}(?:st|nd|rd|th)\s+century\b",
                        anchor_text,
                        re.IGNORECASE,
                    )
                )
            if not tt or not ts or len(tt) > 60 or len(ts) > 60:
                errors.append(f"part {want}: title_card.title ve .subtitle zorunlu (≤60 karakter)")
            elif not has_year and bible.slug == "flashpoints":
                errors.append(
                    f"part {want}: title_card 4-haneli yıl veya çağ çıpası içermeli "
                    f"(ör. 'Zanzibar, 1896', 'Egypt, 69 BCE', 'Pompeii, AD 79'); "
                    f"gelen: {tt!r} / {ts!r}"
                )
            elif not has_year:
                errors.append(f"part {want}: title_card 4-haneli bir yıl içermeli (başlıkta "
                              f"'City, 1909' ya da alt yazıda '… ,  found 1901') ,  "
                              f"gelen: {tt!r} / {ts!r}")
            else:
                normalized["title_card"] = {"title": tt, "subtitle": ts}
        if want_caption:
            # Opt-in (the__footnote formatı): yazılı hikâye + bölüme-özgü etiketler.
            cap = str(plan.get("caption") or "").strip()
            cwc = len(cap.split())
            if not (40 <= cwc <= 220):
                errors.append(f"part {want}: caption {cwc} kelime ,  70-140 hedef "
                              f"(kabul 40-220) dışında")
            elif not re.search(r"\b(1[0-9]{3}|20[0-9]{2})\b", cap):
                errors.append(f"part {want}: caption gerçek bir 4-haneli yıl içermeli")
            else:
                normalized["caption"] = cap
            tags = [t if t.startswith("#") else "#" + t
                    for t in str(plan.get("hashtags") or "").split()
                    if re.sub(r"[#\W]", "", t)]
            if len(tags) < 3:
                errors.append(f"part {want}: hashtags en az 3 etiket olmalı "
                              f"(gelen: {len(tags)})")
            else:
                normalized["hashtags"] = " ".join(tags[:12])
        if hook:
            normalized["hook_shot"] = hook
        episodes[i] = normalized

        if strict_plan_validation_enabled(cfg):
            for error in validate_plan_against_config(normalized, cfg):
                surfaced = f"part {want}: {error}"
                if surfaced not in errors:
                    errors.append(surfaced)

        # Motorun kendi doğrulaması (Omni kota vb.) ,  hatalar batch'i düşürür.
        v = validate_plan(normalized, bible)
        errors.extend(f"part {want}: {e}" for e in v.get("errors", []))
    required_cards = min(len(unused_cards), batch)
    used_distinct_cards = len(set(unused_cards).intersection(used_card_ids))
    if used_distinct_cards < required_cards:
        errors.append(
            f"batch: en az {required_cards} farkli kart kullanilmali "
            f"(gelen: {used_distinct_cards})"
        )
    return errors


def generate_plans(meta: SeriesMeta, bible: Bible, cfg: dict,
                   start: int, batch: int,
                   calibration: Mapping | None = None) -> list[dict]:
    """TEK Gemini çağrısıyla batch adet bölüm planı üret. 3 semantik deneme:
    her başarısız denemenin hataları sonraki prompt'a geri beslenir."""
    history = _episode_history(meta.slug)
    existing = {_norm_title(h["title"]) for h in history if h.get("title")}
    errors: list[str] | None = None
    for attempt in (1, 2, 3, 4, 5, 6):
        contents, sysins = _build_prompt(meta, bible, cfg, start, batch, history,
                                         fix_errors=errors, calibration=calibration)
        data = _gen_json(contents, sysins, temperature=0.9)
        episodes = data.get("episodes") if isinstance(data, dict) else None
        errors = _validate_batch(
            episodes, bible, start, batch, existing, cfg, history, calibration
        )
        if not errors:
            return episodes
        logger.warning(f"⚠️ İkmal doğrulaması geçmedi ({attempt}. deneme): {errors[:4]}")
    forbidden_family = _previous_family(history) if cfg.get("families") else ""
    forbidden_note = (
        f"; ilk bölüm {start} için yasak family: {forbidden_family!r}"
        if forbidden_family else ""
    )
    raise RuntimeError(
        f"Gemini planları doğrulamadan geçemedi{forbidden_note}; "
        f"başarısız kurallar: {'; '.join(errors)}"
    )


# ─── Ana akış ──────────────────────────────────────────────────────────────────

def replenish(slug: str, dry_run: bool = False) -> bool:
    """Bir serinin plan kuyruğunu gerekiyorsa doldur. True = sorun yok (no-op dahil)."""
    calibration = _load_calibration(slug)
    meta = SeriesMeta.load(slug)
    if not meta:
        return True
    cfg = meta.auto_replenish
    if not cfg:
        return True   # opt-in değil ,  dokunma
    cfg_errors = validate_replenish_config(cfg)
    if cfg_errors:
        logger.error(f"❌ HATA {slug}: auto_replenish cfg geçersiz: {'; '.join(cfg_errors)}")
        return False
    if meta.status not in ("active", "completed"):
        logger.info(f"⏸️ {slug}: status={meta.status} (insan kararı) ,  ikmal yapılmaz.")
        return True
    bible = Bible.load(slug)
    if not bible:
        logger.warning(f"⚠️ {slug}: bible.json yok ,  ikmal atlandı.")
        return True

    adopted = _adopt_orphans(meta)
    if adopted and not dry_run:
        meta.save()
        logger.info(f"🧩 {slug}: {adopted} öksüz plan sahiplenildi → total_parts={meta.total_parts}")

    pending = max(0, meta.total_parts - meta.next_part + 1)
    min_q = max(1, int(cfg.get("min_queue", DEFAULT_MIN_QUEUE)))
    if pending >= min_q:
        return True
    batch = min(10, max(1, int(cfg.get("batch", DEFAULT_BATCH))))
    history = _episode_history(slug)
    unused_ints = _unused_topics(cfg, history)
    unused_cards = _unused_cards(calibration, history)
    if cfg.get("topic_pool") is not None or _card_topics(calibration):
        available = len(unused_ints) + len(unused_cards)
        if not available:
            logger.error(f"❌ HATA {slug}: kullanılmamış birleşik konu havuzu kalmadı.")
            return False
        batch = min(batch, available)
    start = meta.total_parts + 1
    end = start + batch - 1

    if dry_run:
        logger.info(f"[dry-run] {slug}: kuyruk {pending} < {min_q} → part {start}-{end} üretilirdi.")
        return True

    digest = _doctrine_gate(meta)
    if digest is None:
        return False

    logger.info(f"🔁 {slug}: kuyruk {pending} < {min_q} → Gemini part {start}-{end} yazıyor…")
    try:
        episodes = generate_plans(meta, bible, cfg, start, batch, calibration)

        # 1) Önce plan dosyaları (çökme güvenliği: sayaç sonra; öksüzler sonraki koşuda sahiplenilir)
        for i, plan in enumerate(episodes):
            plan["doctrine_sha256"] = digest
            pp = part_plan_path(slug, start + i)
            if pp.exists():   # sigorta ,  _adopt_orphans sonrası imkânsız olmalı
                raise RuntimeError(f"plan dosyası zaten var, üzerine yazılmaz: {pp.name}")
            atomic_write_json(pp, plan)

        # 2) Sonra sayaç + durum ('completed' makine kararıydı → diril)
        meta.data["total_parts"] = end
        if meta.status == "completed":
            meta.data["status"] = "active"
            logger.info(f"▶️ {slug}: içerik tükenmişti (completed) → yeniden 'active'.")
        cfg["last_run"] = {"at": datetime.now(timezone.utc).isoformat(),
                           "parts": f"{start}-{end}"}
        meta.data["auto_replenish"] = cfg
        meta.save()

        titles = ", ".join(p["episode"]["title"] for p in episodes)
        logger.info(f"🔁 {slug}: part {start}-{end} planlandı → {titles}")
        _alert(f"🔁 *{meta.base_title}*: {batch} yeni bölüm planlandı (Part {start}-{end}: "
               f"{titles}) ,  kanal kesintisiz devam ediyor.")
        return True
    except Exception as e:
        logger.error(f"❌ {slug} oto-ikmal başarısız: {e}")
        _alert(f"❌ *{meta.base_title}* oto-ikmal BAŞARISIZ: {str(e)[:200]}\n"
               f"Kuyrukta {pending} part kaldı ,  kuyruk biterse bu kanala video çıkmaz.")
        return False


def replenish_all(dry_run: bool = False) -> None:
    """auto_replenish açık tüm serileri dolaş. Hata seriye hapsolur ,  günlük yayın
    koşusunu asla bloklamaz."""
    from series.bible import all_series_dirs
    for slug in all_series_dirs():
        try:
            replenish(slug, dry_run=dry_run)
        except Exception as e:
            logger.error(f"❌ {slug} ikmal denetimi çöktü: {e}")


def main(argv: list[str]) -> None:
    dry = "--dry-run" in argv
    slug = None
    if "--series" in argv:
        i = argv.index("--series")
        if i + 1 < len(argv):
            slug = argv[i + 1]
    if slug:
        ok = replenish(slug, dry_run=dry)
        if not dry and ok is False:
            sys.exit(1)
    else:
        replenish_all(dry_run=dry)


if __name__ == "__main__":
    main(sys.argv[1:])
