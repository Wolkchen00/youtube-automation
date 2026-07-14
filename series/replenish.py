"""
Oto-ikmal (auto-replenish) — 'sonsuz içerik' motoru.

Plan kuyruğu azalan serilere Gemini yönetmeniyle YENİ part planları yazar
(series_data/<slug>/plans/partNN.json), total_parts'ı büyütür ve makinenin
'completed'e düşürdüğü seriyi yeniden 'active' yapar. Kie kredisi HARCAMAZ —
yalnız ücretsiz Gemini text çağrısı (planlama), üretim yine series_runner'da.

Kurallar:
  • Yalnız series.json'da "auto_replenish": {"enabled": true} olan seriler (opt-in).
  • 'paused' / 'draft' ASLA diriltilmez (insan kararı). 'completed' makine kararıdır
    (advance() kuyruk bitince yazar) → ikmal açıkken yeniden 'active' olur.
    DURDURMA ANAHTARI: status="paused" veya auto_replenish.enabled=false.
  • Var olan plan dosyasının üzerine ASLA yazılmaz; koşu başına en fazla 1 batch.
  • Yarıda çökme güvenliği: önce plan dosyaları yazılır, sayaç SONRA güncellenir;
    ortada kalan dosyalar bir sonraki koşuda sahiplenilir (_adopt_orphans) —
    Gemini çıktısı asla çöpe gitmez, yeniden istenmez.

series.json şeması:
  "auto_replenish": {
    "enabled": true,        // zorunlu anahtar; false/yok = kapalı
    "batch": 5,             // ops. (1-10): her ikmalde kaç yeni bölüm
    "min_queue": 2,         // ops. (>=1): bekleyen bölüm bunun altına inince ikmal
    "brief": "...",         // ops.: Gemini'ye seriye özgü yaratıcı yön (Türkçe olabilir)
    "music_prompt": true,   // ops.: bölüm başına sahne-eşleşmeli 'music' alanı istenir (Suno)
    "shots": 4,             // ops.: bölüm başına çekim sayısı
    "shot_seconds": "8",    // ops.: çekim süresi ("4"|"6"|"8"|"10")
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

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from core.config import GEMINI_API_KEY, logger
from series import notifier
from series.bible import Bible, SERIES_DATA_DIR
from series.series_meta import SeriesMeta, part_plan_path, plans_dir, series_meta_path
from series.shots import validate_plan

REPLENISH_MODEL = "gemini-2.5-flash"
REPLENISH_MODEL_FALLBACK = "gemini-flash-latest"
DEFAULT_BATCH = 5
DEFAULT_MIN_QUEUE = 2
DEFAULT_SHOTS = 4          # bölüm başına çekim
DEFAULT_SHOT_SECONDS = "8" # çekim süresi (motor enum'u: 4/6/8/10)
VALID_DURATIONS = ("4", "6", "8", "10")


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
        raise RuntimeError("GEMINI_API_KEY tanımlı değil — oto-ikmal için gerekli.")
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
                # Bozuk JSON şans işidir — AYNI modelden taze üretim genelde geçer;
                # yedek modeli buna harcama.
                bad_json = isinstance(e, json.JSONDecodeError)
                transient = any(s in msg for s in
                                ("503", "429", "500", "UNAVAILABLE", "RESOURCE_EXHAUSTED",
                                 "INTERNAL", "deadline"))
                if (transient or bad_json) and attempt < max_tries:
                    wait = 3 if bad_json else min(5 * attempt, 20)
                    label = "bozuk JSON" if bad_json else "geçici hata"
                    logger.warning(f"⚠️ ikmal {model} {label} ({msg[:60]}…) — {wait}s sonra tekrar")
                    time.sleep(wait)
                    continue
                logger.warning(f"⚠️ ikmal {model} başarısız: {msg[:120]}")
                break  # yedek modele geç
    raise RuntimeError(f"Gemini ikmal çağrısı başarısız: {last_err}")


def _alert(msg: str) -> None:
    """Telegram'a sessizce bildir (token yoksa no-op) — series_runner._alert eşleniği."""
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
    """plans/partNN.json → [{"n","title","synopsis"}] sıralı. synopsis alanı yoksa
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
                    "synopsis": syn})
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


# ─── Gemini yönetmen promptu ───────────────────────────────────────────────────

def _build_prompt(meta: SeriesMeta, bible: Bible, cfg: dict, start: int, batch: int,
                  history: list[dict], fix_errors: list[str] | None = None) -> tuple[str, str]:
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
    # eerie_ok: true → 'frightening' yasağı kalkar (korku-tonlu kanallar; gore yine yasak)
    # title_style: "<metin>" → başlık kuralını değiştirir (ör. haber-kancası cümle başlıklar)
    # shot_refs: true → çekimler bible'daki characters/environment id'lerini kullanabilir
    narr_cfg = cfg.get("narration")
    if narr_cfg is True:
        narr_cfg = {}
    narrated = isinstance(narr_cfg, dict)
    wmin = int((narr_cfg or {}).get("min_words", 95))
    wmax = int((narr_cfg or {}).get("max_words", 125))
    want_tc = bool(cfg.get("title_card"))
    want_fc = bool(cfg.get("fact_captions"))
    want_music = bool(cfg.get("music_prompt"))
    humans_mode = str(cfg.get("humans") or "").strip().lower()
    humans_featured = humans_mode == "featured"
    humans_silent = humans_mode in ("silent", "silent-masked", "allowed")
    eerie_ok = bool(cfg.get("eerie_ok"))
    title_style = str(cfg.get("title_style") or "").strip()
    shot_refs = bool(cfg.get("shot_refs"))

    if narrated:
        head = (f"You are the showrunner of an endless vertical (9:16) YouTube Shorts series told through\n"
                f"SILENT visual shots plus a POST-PRODUCTION voice-over narration.\n"
                f"Every episode is a STANDALONE ~{shots * int(sec)}-second piece: {shots} consecutive shots (each ONE\n"
                f"continuous moment of {sec} seconds) that flow into one another, plus ONE narration script\n"
                f"({wmin}-{wmax} words) recorded separately and laid over the finished edit. No dialogue, no lip-sync.")
        narr_shape = f'"<{wmin}-{wmax} word English voice-over script>"'
    else:
        head = (f"You are the showrunner of an endless, VISUAL-ONLY vertical (9:16) YouTube Shorts series.\n"
                f"Every episode is a STANDALONE ~{shots * int(sec)}-second visual trip: {shots} consecutive shots (each ONE\n"
                f"continuous moment of {sec} seconds) that morph seamlessly into one another. No dialogue,\n"
                f"no narration, no characters — pure visuals.")
        narr_shape = '""'

    tc_shape = ('\n   "title_card": {"title": "<subject name, max 40 chars>", '
                '"subtitle": "<max 48 chars>"},') if want_tc else ""
    music_shape = ('\n   "music": "<40-90 word instrumental music style prompt '
                   'matched to THIS episode>",') if want_music else ""
    shot_fields = f'"n": <int>, "duration": "{sec}", "prompt": "<visual description>", "seed": null'
    if shot_refs:
        shot_fields += ', "characters": ["<ref id, optional>"], "environment": "<ref id, optional>"'
    if want_fc:
        shot_fields += ', "fact": "<2-5 word on-screen fact, optional>"'

    title_rule = title_style or ('2-4 words, poetic, curiosity-driven — the title IS the YouTube title of a\n'
                                 '  standalone video (like "Bloom" or "The Last Door"). No drug slang, no clickbait\n'
                                 '  punctuation.')
    narr_rule = (f"\n- NARRATION: {wmin}-{wmax} words of spoken English voice-over for the WHOLE episode — "
                 f"flowing prose, no camera directions, no shot numbers; follow the CREATIVE BRIEF strictly."
                 if narrated else "")
    tc_rule = ('\n- TITLE_CARD: "title" = the subject/site name (max 40 chars); "subtitle" = place and year '
               'exactly as the CREATIVE BRIEF instructs (max 48 chars).' if want_tc else "")
    fact_rule = ('\n- FACT_CAPTIONS: give a "fact" to 2-4 shots — a punchy 2-5 word hard fact from the entry '
                 'that is literally on screen in THAT shot (a depth, an age, a count, a death toll, a date), '
                 'e.g. "45 METERS DEEP", "2,000 YEARS OLD", "ONE DIVER DIED". They are burned low on screen '
                 'while the viewer watches. NO "fact" on the final resolve shot; omit "fact" where the shot '
                 'shows nothing concrete. NEVER invent a number — every fact must come from the brief entry.'
                 if want_fc else "")
    music_rule = ('\n- MUSIC: "music" = a 40-90 word ENGLISH prompt for an AI music generator, composed '
                  'TOGETHER with the visuals so score and image share one soul: name genre, mood, 2-4 '
                  'instruments, rough tempo (slow/glacial), and an arc that mirrors the episode (open '
                  'atmospheric → swell → sustained emotional peak → gentle end). INSTRUMENTAL only, no '
                  'vocals, no drums unless the scene demands a pulse. The track starts playing from its '
                  'very first second, so it must open with immediate atmosphere — no long silent intro. '
                  'Each episode gets a CLEARLY different musical color (vary instruments/scale/texture).'
                  if want_music else "")
    refs_rule = ('\n- Shots MAY reference ONLY the ids listed under AVAILABLE REFERENCES via "characters" / '
                 '"environment"; follow the brief about when to use them.' if shot_refs else "")
    if humans_featured:
        humans_rule = ("the recurring lead character (see AVAILABLE REFERENCES) MAY appear in clear close-up, "
                       "mid and wide shots and is the emotional anchor of the episode, but must NEVER speak, "
                       "lip-sync or move their lips as if talking (the voice is added later as narration); "
                       "other people may appear around them,")
    elif humans_silent:
        humans_rule = ("human figures may appear but must NEVER speak, lip-sync or show a clear close-up face "
                       "(masked, distant, silhouetted or from behind only),")
    else:
        humans_rule = "no humans or human faces,"
    tone_tail = "nothing gory, violent or graphic." if eerie_ok else "nothing gory, violent or frightening."

    system_instruction = f"""{head}

Return STRICT JSON ONLY, exactly this shape:
{{"episodes": [
  {{"episode": {{"number": <int>, "title": "<title>"}},
   "synopsis": "<one sentence>",
   "hook_shot": <int>,
   "narration": {narr_shape},{tc_shape}{music_shape}
   "shots": [{{{shot_fields}}}]}}
]}}

RULES:
- Produce EXACTLY {batch} episodes, numbered {start} to {end}, in this order.
- Each episode has EXACTLY {shots} shots, every shot with "duration": "{sec}".
- TITLES: {title_rule} All {batch} titles must be distinct from each other AND from every
  EXISTING episode listed in the input; never repeat or lightly reword one.
- "synopsis": ONE specific sentence describing this episode (it is
  stored and used to keep future episodes fresh).{narr_rule}{tc_rule}{fact_rule}{music_rule}{refs_rule}
- SEAMLESS CHAIN (the engine literally starts each shot from the PREVIOUS shot's final
  frame): shot 1 opens a brand-new striking scene; every later shot's prompt must
  describe ONE continuous transformation that begins EXACTLY at the previous shot's end
  state and evolves into somewhere new. No cuts, no teleports, no scene resets inside
  an episode.
- EPISODE ARC: striking opening → build → peak spectacle → gentle, loopable resolve.
  "hook_shot" = the n of the single most spectacular, jaw-dropping shot (usually 2 or 3).
- PROMPTS: rich visual language — motion, geometry, light, color, camera flow. The
  series art style is automatically prefixed to every shot at production; do NOT restate
  it wholesale, but stay inside it.
- HARD LIMITS: {humans_rule} no readable text/letters/logos/watermarks,
  {tone_tail} English only."""

    lines = [f"SERIES: {meta.base_title} — {meta.logline}".strip()]
    art = (bible.art_style or "").strip()
    if art:
        lines.append(f"\nART STYLE (auto-prefixed to every shot at production):\n{art}")
    brief = str(cfg.get("brief") or "").strip()
    if brief:
        lines.append(f"\nCREATIVE BRIEF for new episodes:\n{brief}")
    if shot_refs:
        refs_lines = []
        for kind in ("characters", "environments"):
            items = bible.data.get(kind) or []
            entries = [f"{it.get('id')} — {(it.get('name') or it.get('desc') or '')[:60]}"
                       for it in items if it.get("id")]
            if entries:
                refs_lines.append(f"{kind}: " + "; ".join(entries))
        if refs_lines:
            lines.append("\nAVAILABLE REFERENCES (use these ids only):\n" + "\n".join(refs_lines))
    if history:
        lines.append("\nEXISTING EPISODES (title — synopsis). NEVER repeat or reword these:")
        for h in history:
            n = h.get("n")
            tag = f"{int(n):02d}" if isinstance(n, int) else "??"
            lines.append(f"{tag}. {h['title']} — {h['synopsis']}")
    if fix_errors:
        lines.append("\nYOUR PREVIOUS ATTEMPT WAS REJECTED. Fix ALL of these problems:")
        lines.extend(f"- {e}" for e in fix_errors)
    lines.append(f"\nWrite episodes {start}-{end} now. Each episode picks a FRESH theme "
                 f"and color palette, clearly different from the existing episodes.")
    return "\n".join(lines), system_instruction


def _validate_batch(episodes, bible: Bible, start: int, batch: int,
                    existing_titles: set[str], cfg: dict | None = None) -> list[str]:
    """Sert doğrulama + normalizasyon (yerinde): numaralar/çekim n'leri düzeltilir,
    bilinmeyen alanlar atılır. Hata listesi döner (boş = geçerli).
    cfg (auto_replenish) format bayraklarını taşır: narration/title_card/shot_refs —
    bkz. _build_prompt; bayrak yoksa davranış eskisiyle birebir aynıdır."""
    if not isinstance(episodes, list) or len(episodes) != batch:
        got = len(episodes) if isinstance(episodes, list) else type(episodes).__name__
        return [f"'episodes' tam {batch} bölüm olmalı (gelen: {got})"]

    cfg = cfg or {}
    narr_cfg = cfg.get("narration")
    if narr_cfg is True:
        narr_cfg = {}
    narrated = isinstance(narr_cfg, dict)
    wmin = int((narr_cfg or {}).get("min_words", 95))
    wmax = int((narr_cfg or {}).get("max_words", 125))
    want_tc = bool(cfg.get("title_card"))
    want_fc = bool(cfg.get("fact_captions"))
    want_music = bool(cfg.get("music_prompt"))
    shot_refs = bool(cfg.get("shot_refs"))

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
                errors.append(f"part {want}: başlık tekrarı ('{title}') — özgün başlık gerekli")
            seen.add(nt)

        raw_shots = plan.get("shots")
        clean_shots: list[dict] = []
        fact_count = 0
        if not isinstance(raw_shots, list) or not (2 <= len(raw_shots) <= 6):
            got = len(raw_shots) if isinstance(raw_shots, list) else "yok"
            errors.append(f"part {want}: çekim sayısı 2-6 olmalı (gelen: {got})")
        else:
            for k, shot in enumerate(raw_shots, start=1):
                shot = shot if isinstance(shot, dict) else {}
                prompt = str(shot.get("prompt") or "").strip()
                if len(prompt) < 30:
                    errors.append(f"part {want} çekim {k}: prompt boş/çok kısa")
                try:
                    dur = str(int(float(str(shot.get("duration", "")).strip() or "0")))
                except (TypeError, ValueError):
                    dur = ""
                if dur not in VALID_DURATIONS:
                    errors.append(f"part {want} çekim {k}: süre {shot.get('duration')!r} "
                                  f"geçersiz (4/6/8/10 olmalı)")
                # Yalnız bilinen alanlar; model karakter/diyalog uydurduysa sessizce atılır.
                clean = {"n": k, "duration": dur, "prompt": prompt, "seed": None}
                if shot_refs:
                    # Opt-in: bible'da GERÇEKTEN var olan referans id'leri korunur.
                    env = shot.get("environment")
                    if env and bible.get("environments", str(env)):
                        clean["environment"] = str(env)
                    chars = [c for c in (shot.get("characters") or [])
                             if isinstance(c, str) and bible.get_character(c)]
                    if chars:
                        clean["characters"] = chars
                if want_fc:
                    # Opt-in: kısa ekran-içi 'fact' (≤40 karakter); produce alt üçlüğe basar.
                    fv = str(shot.get("fact") or "").strip()
                    if fv:
                        clean["fact"] = fv[:40].strip()
                        fact_count += 1
                clean_shots.append(clean)

        if want_fc and clean_shots and fact_count < 2:
            errors.append(f"part {want}: fact_captions açık — en az 2 çekimde 'fact' olmalı "
                          f"(gelen: {fact_count})")

        hook = plan.get("hook_shot")
        try:
            hook = int(hook)
            if not (1 <= hook <= len(clean_shots)):
                raise ValueError
        except (TypeError, ValueError):
            hook = None   # produce.py'nin 'sondan bir önceki' varsayılanı devreye girer

        ntext = str(plan.get("narration") or "").strip()
        if narrated:
            wc = len(ntext.split())
            lo, hi = max(30, int(wmin * 0.7)), int(wmax * 1.35)
            if not (lo <= wc <= hi):
                errors.append(f"part {want}: anlatım {wc} kelime — hedef {wmin}-{wmax} "
                              f"(kabul {lo}-{hi}) dışında")
        else:
            ntext = ""   # anlatımsız seri: eski davranış (boş string zorlanır)

        normalized = {"episode": {"number": want, "title": title},
                      "synopsis": str(plan.get("synopsis") or "").strip()[:300],
                      "narration": ntext,
                      "shots": clean_shots}
        if want_music:
            mtext = str(plan.get("music") or "").strip()
            mwc = len(mtext.split())
            if not (20 <= mwc <= 140):
                errors.append(f"part {want}: music prompt {mwc} kelime — 40-90 hedef "
                              f"(kabul 20-140) dışında")
            else:
                normalized["music"] = mtext
        if want_tc:
            tcv = plan.get("title_card") or {}
            tt = str(tcv.get("title") or "").strip()
            ts = str(tcv.get("subtitle") or "").strip()
            # Künye alt yazısı GERÇEK bir 4-haneli yıl taşımalı (1000-2099).
            # Ekrana basılan tarih doğruluğu güvencesi: model tarihi düşürür ya da
            # uydurursa batch reddedilir → Gemini yeniden dener (brief: yıl DOĞRUDAN
            # FACT BANK kaydından kopyalanır). Tek boşluk kalan doğrulama buydu.
            has_year = bool(re.search(r"\b(1[0-9]{3}|20[0-9]{2})\b", ts))
            if not tt or not ts or len(tt) > 60 or len(ts) > 60:
                errors.append(f"part {want}: title_card.title ve .subtitle zorunlu (≤60 karakter)")
            elif not has_year:
                errors.append(f"part {want}: title_card.subtitle 4-haneli bir yıl içermeli "
                              f"(ör. '… — found 1901') — gelen: {ts!r}")
            else:
                normalized["title_card"] = {"title": tt, "subtitle": ts}
        if hook:
            normalized["hook_shot"] = hook
        episodes[i] = normalized

        # Motorun kendi doğrulaması (Omni kota vb.) — hatalar batch'i düşürür.
        v = validate_plan(normalized, bible)
        errors.extend(f"part {want}: {e}" for e in v.get("errors", []))
    return errors


def generate_plans(meta: SeriesMeta, bible: Bible, cfg: dict,
                   start: int, batch: int) -> list[dict]:
    """TEK Gemini çağrısıyla batch adet bölüm planı üret. 2 semantik deneme:
    ilk denemenin hataları ikinci denemede prompt'a geri beslenir."""
    history = _episode_history(meta.slug)
    existing = {_norm_title(h["title"]) for h in history if h.get("title")}
    errors: list[str] | None = None
    for attempt in (1, 2):
        contents, sysins = _build_prompt(meta, bible, cfg, start, batch, history,
                                         fix_errors=errors)
        data = _gen_json(contents, sysins, temperature=0.9)
        episodes = data.get("episodes") if isinstance(data, dict) else None
        errors = _validate_batch(episodes, bible, start, batch, existing, cfg)
        if not errors:
            return episodes
        logger.warning(f"⚠️ İkmal doğrulaması geçmedi ({attempt}. deneme): {errors[:4]}")
    raise RuntimeError(f"Gemini planları doğrulamadan geçemedi: {'; '.join(errors[:4])}")


# ─── Ana akış ──────────────────────────────────────────────────────────────────

def replenish(slug: str, dry_run: bool = False) -> bool:
    """Bir serinin plan kuyruğunu gerekiyorsa doldur. True = sorun yok (no-op dahil)."""
    meta = SeriesMeta.load(slug)
    if not meta:
        return True
    cfg = meta.auto_replenish
    if not cfg:
        return True   # opt-in değil — dokunma
    if meta.status not in ("active", "completed"):
        logger.info(f"⏸️ {slug}: status={meta.status} (insan kararı) — ikmal yapılmaz.")
        return True
    bible = Bible.load(slug)
    if not bible:
        logger.warning(f"⚠️ {slug}: bible.json yok — ikmal atlandı.")
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
    start = meta.total_parts + 1
    end = start + batch - 1

    if dry_run:
        logger.info(f"[dry-run] {slug}: kuyruk {pending} < {min_q} → part {start}-{end} üretilirdi.")
        return True

    logger.info(f"🔁 {slug}: kuyruk {pending} < {min_q} → Gemini part {start}-{end} yazıyor…")
    try:
        episodes = generate_plans(meta, bible, cfg, start, batch)

        # 1) Önce plan dosyaları (çökme güvenliği: sayaç sonra; öksüzler sonraki koşuda sahiplenilir)
        for i, plan in enumerate(episodes):
            pp = part_plan_path(slug, start + i)
            if pp.exists():   # sigorta — _adopt_orphans sonrası imkânsız olmalı
                raise RuntimeError(f"plan dosyası zaten var, üzerine yazılmaz: {pp.name}")
            pp.parent.mkdir(parents=True, exist_ok=True)
            pp.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

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
               f"{titles}) — kanal kesintisiz devam ediyor.")
        return True
    except Exception as e:
        logger.error(f"❌ {slug} oto-ikmal başarısız: {e}")
        _alert(f"❌ *{meta.base_title}* oto-ikmal BAŞARISIZ: {str(e)[:200]}\n"
               f"Kuyrukta {pending} part kaldı — kuyruk biterse bu kanala video çıkmaz.")
        return False


def replenish_all(dry_run: bool = False) -> None:
    """auto_replenish açık tüm serileri dolaş. Hata seriye hapsolur — günlük yayın
    koşusunu asla bloklamaz."""
    if not SERIES_DATA_DIR.exists():
        return
    for d in sorted(SERIES_DATA_DIR.iterdir()):
        if not (d.is_dir() and series_meta_path(d.name).exists()):
            continue
        try:
            replenish(d.name, dry_run=dry_run)
        except Exception as e:
            logger.error(f"❌ {d.name} ikmal denetimi çöktü: {e}")


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
