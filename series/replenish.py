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

    system_instruction = f"""You are the showrunner of an endless, VISUAL-ONLY vertical (9:16) YouTube Shorts series.
Every episode is a STANDALONE ~{shots * int(sec)}-second visual trip: {shots} consecutive shots (each ONE
continuous moment of {sec} seconds) that morph seamlessly into one another. No dialogue,
no narration, no characters — pure visuals.

Return STRICT JSON ONLY, exactly this shape:
{{"episodes": [
  {{"episode": {{"number": <int>, "title": "<2-4 words>"}},
   "synopsis": "<one sentence>",
   "hook_shot": <int>,
   "narration": "",
   "shots": [{{"n": <int>, "duration": "{sec}", "prompt": "<visual description>", "seed": null}}]}}
]}}

RULES:
- Produce EXACTLY {batch} episodes, numbered {start} to {end}, in this order.
- Each episode has EXACTLY {shots} shots, every shot with "duration": "{sec}".
- TITLES: 2-4 words, poetic, curiosity-driven — the title IS the YouTube title of a
  standalone video (like "Bloom" or "The Last Door"). No drug slang, no clickbait
  punctuation. All {batch} titles must be distinct from each other AND from every
  EXISTING episode listed in the input; never repeat or lightly reword one.
- "synopsis": ONE specific sentence describing this episode's visual journey (it is
  stored and used to keep future episodes fresh).
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
- HARD LIMITS: no humans or human faces, no readable text/letters/logos/watermarks,
  nothing gory, violent or frightening. English only."""

    lines = [f"SERIES: {meta.base_title} — {meta.logline}".strip()]
    art = (bible.art_style or "").strip()
    if art:
        lines.append(f"\nART STYLE (auto-prefixed to every shot at production):\n{art}")
    brief = str(cfg.get("brief") or "").strip()
    if brief:
        lines.append(f"\nCREATIVE BRIEF for new episodes:\n{brief}")
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
                    existing_titles: set[str]) -> list[str]:
    """Sert doğrulama + normalizasyon (yerinde): numaralar/çekim n'leri düzeltilir,
    bilinmeyen alanlar atılır. Hata listesi döner (boş = geçerli)."""
    if not isinstance(episodes, list) or len(episodes) != batch:
        got = len(episodes) if isinstance(episodes, list) else type(episodes).__name__
        return [f"'episodes' tam {batch} bölüm olmalı (gelen: {got})"]

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
        if not isinstance(raw_shots, list) or not (3 <= len(raw_shots) <= 6):
            got = len(raw_shots) if isinstance(raw_shots, list) else "yok"
            errors.append(f"part {want}: çekim sayısı 3-6 olmalı (gelen: {got})")
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
                clean_shots.append({"n": k, "duration": dur, "prompt": prompt, "seed": None})

        hook = plan.get("hook_shot")
        try:
            hook = int(hook)
            if not (1 <= hook <= len(clean_shots)):
                raise ValueError
        except (TypeError, ValueError):
            hook = None   # produce.py'nin 'sondan bir önceki' varsayılanı devreye girer

        normalized = {"episode": {"number": want, "title": title},
                      "synopsis": str(plan.get("synopsis") or "").strip()[:300],
                      "narration": "",
                      "shots": clean_shots}
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
        errors = _validate_batch(episodes, bible, start, batch, existing)
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
