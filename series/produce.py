"""
Üretim Orkestrasyonu — Gemini Omni mini-dizi.

İki ana akış:
  setup_references(slug)  → referans görseller (üret/yükle) + ses + karakter kaydı (bible.json'a yazar)
  produce_episode(slug, plan) → her çekimi üret, indir, birleştir, raporla

dry_run=True her ikisinde de API/kredi harcamadan adımları simüle eder.
"""

import json
from pathlib import Path

from core.config import logger
from core.utils import download_file, sanitize_filename
from core.imgbb import upload_to_imgbb
from core.kie_api import generate_image, check_credit
from core import ffmpeg_tools, cost_tracker

from .bible import Bible, refs_dir, episode_dir, shots_dir, resolve_voice_id
from .omni_api import register_audio, register_character, generate_omni_shot, build_omni_payload
from .shots import resolve_shot, validate_plan, load_plan, plan_summary
from . import report
from .voices import is_preset


# ─── Referans görsel (Karışık: yerel görsel varsa yükle, yoksa Nano Banana ile üret) ──

def _ref_prompt(kind: str, item: dict, style: str) -> str:
    """Referans görsel için Nano Banana 2 prompt'u kur."""
    style_suffix = f" {style}" if style else ""
    if kind == "characters":
        body = item.get("appearance") or item.get("bio") or item.get("name", "")
        return (f"Full-body character reference, front view, standing, full figure visible "
                f"head to toe, plain neutral studio background, no text, no labels, no watermark, no captions. "
                f"{body}.{style_suffix}")
    if kind == "environments":
        return (f"Establishing wide shot of {item.get('desc') or item.get('name','')}. "
                f"Empty scene, no people, no text.{style_suffix}")
    # props
    return (f"Single product/prop reference of {item.get('desc') or item.get('name','')}, "
            f"centered, plain neutral background, no text.{style_suffix}")


def ensure_ref_image(bible: Bible, kind: str, item: dict, dry_run: bool = False) -> str | None:
    """Bir referans öğesi için ImgBB URL'i garanti et.
    Öncelik: mevcut URL → kullanıcı yerel görseli → Nano Banana 2 ile üret.
    Sonucu item içine cache'ler.
    """
    if item.get("ref_image_url"):
        return item["ref_image_url"]

    folder = refs_dir(bible.slug, kind)
    folder.mkdir(parents=True, exist_ok=True)

    # 1) Kullanıcı yerel görsel verdiyse → ImgBB'ye yükle
    local = item.get("ref_image_local")
    if local:
        lp = Path(local)
        if not lp.is_absolute():
            lp = folder / local
        if lp.exists():
            if dry_run:
                logger.info(f"[dry-run] {kind}/{item['id']}: yerel görsel ImgBB'ye yüklenecek ({lp.name})")
                return None
            url = upload_to_imgbb(lp)
            if url:
                item["ref_image_url"] = url
            return url
        logger.warning(f"⚠️ {kind}/{item['id']}: yerel görsel yok ({lp}) → AI üretimine geçiliyor")

    # 2) AI ile üret (Nano Banana 2) → indir → ImgBB
    if dry_run:
        logger.info(f"[dry-run] {kind}/{item['id']}: Nano Banana 2 ile üretilecek (kredi harcanır)")
        return None
    gen_url = generate_image(_ref_prompt(kind, item, bible.art_style), aspect_ratio=bible.aspect_ratio)
    if not gen_url:
        logger.error(f"❌ {kind}/{item['id']}: görsel üretilemedi")
        return None
    save_path = folder / f"{sanitize_filename(item['id'])}.png"
    download_file(gen_url, save_path)
    url = upload_to_imgbb(save_path) or gen_url
    item["ref_image_local"] = str(save_path)
    item["ref_image_url"] = url
    return url


# ─── Ses garantisi ─────────────────────────────────────────────────────────────

def ensure_voice(bible: Bible, ch: dict, dry_run: bool = False) -> str | None:
    """Karakterin sesini garanti et.
    voice = {audio_id, kie_audio_id, custom:{base,name,voice_description,example_dialogue}}
    - kie_audio_id varsa: hazır.
    - custom varsa: omni/audio/create ile üret → kie_audio_id.
    - audio_id (preset veya hash) varsa: doğrudan kullanılır.
    """
    voice = ch.setdefault("voice", {})
    if voice.get("kie_audio_id"):
        return voice["kie_audio_id"]

    custom = voice.get("custom")
    if custom:
        if dry_run:
            logger.info(f"[dry-run] Karakter '{ch['id']}': özel ses üretilecek (base={custom.get('base')})")
            return None
        kid = register_audio(
            custom.get("base", "callirrhoe"),
            custom.get("name", ch.get("name", ch["id"])),
            custom.get("voice_description", ""),
            custom.get("example_dialogue", ""),
        )
        if kid:
            voice["kie_audio_id"] = kid
        return kid

    if voice.get("audio_id"):
        return voice["audio_id"]

    logger.warning(f"⚠️ Karakter '{ch['id']}': ses tanımlı değil (voice.audio_id veya voice.custom ekle)")
    return None


# ─── Karakter kaydı ────────────────────────────────────────────────────────────

def ensure_character_registration(bible: Bible, ch: dict, dry_run: bool = False) -> str | None:
    """Karakteri Omni'ye kaydet (görünüm + ses) → characterId. Idempotent."""
    if ch.get("character_id"):
        return ch["character_id"]

    img_url = ch.get("ref_image_url")
    if not img_url:
        logger.warning(f"⚠️ Karakter '{ch['id']}': referans görsel yok, kayıt atlanıyor")
        return None

    descriptions = ch.get("appearance") or ch.get("bio") or ch.get("name", ch["id"])
    voice_id = resolve_voice_id(ch)
    audio_ids = [voice_id] if voice_id else None

    if dry_run:
        logger.info(f"[dry-run] Karakter '{ch['id']}': omni/character/create (ses={voice_id})")
        return None

    cid = register_character(descriptions, img_url, audio_ids=audio_ids,
                             character_name=ch.get("name", ch["id"]))
    if cid:
        ch["character_id"] = cid
    return cid


# ─── Referans kurulumu (tüm bible) ─────────────────────────────────────────────

def setup_references(slug: str, dry_run: bool = False) -> Bible | None:
    """Bible'daki tüm referansları hazırla. Idempotent — tamamlananı atlar."""
    bible = Bible.load(slug)
    if not bible:
        return None

    logger.info(f"🗂️  Referans kurulumu başladı: {slug} (dry_run={dry_run})")

    # 1) Görseller (karakter / ortam / aksesuar)
    for kind in ("characters", "environments", "props"):
        for item in bible.items(kind):
            ensure_ref_image(bible, kind, item, dry_run=dry_run)

    # 2) Karakter sesleri + karakter kaydı
    for ch in bible.characters:
        ensure_voice(bible, ch, dry_run=dry_run)
        ensure_character_registration(bible, ch, dry_run=dry_run)

    if not dry_run:
        bible.save()
    logger.info("✅ Referans kurulumu bitti")
    return bible


# ─── Bölüm üretimi ─────────────────────────────────────────────────────────────

def produce_episode(slug: str, plan, dry_run: bool = False) -> Path | None:
    """Bir bölümü üret: çekimler → indir → birleştir → rapor.
    plan: dict veya episode_plan.json yolu.
    """
    bible = Bible.load(slug)
    if not bible:
        return None
    if isinstance(plan, (str, Path)):
        plan = load_plan(plan)

    number = plan.get("episode", {}).get("number", 1)
    logger.info(f"🎬 {plan_summary(plan)} (dry_run={dry_run})")

    # Doğrulama
    v = validate_plan(plan, bible)
    for w in v["warnings"]:
        logger.warning(f"⚠️ {w}")
    for e in v["errors"]:
        logger.error(f"❌ {e}")
    if v["errors"] and not dry_run:
        logger.error("Plan hataları nedeniyle üretim durduruldu.")
        return None

    sdir = shots_dir(slug, number)
    sdir.mkdir(parents=True, exist_ok=True)

    if not dry_run:
        check_credit()  # ücretsiz okuma — başlangıç bakiyesi loglanır

    shot_files: list[Path] = []
    for shot in plan["shots"]:
        n = shot.get("n")
        out_file = sdir / f"shot_{int(n):02d}.mp4"

        # İdempotent: bu çekim zaten üretildiyse atla → yeniden çalıştırmada sadece eksikler üretilir
        if not dry_run and out_file.exists() and out_file.stat().st_size > 0:
            logger.info(f"⏭️ Çekim {n} zaten var, atlanıyor: {out_file.name}")
            shot_files.append(out_file)
            continue

        res = resolve_shot(bible, shot)
        kwargs = res["kwargs"]
        char_names = [bible.get_character(c).get("name", c)
                      for c in shot.get("characters", []) if bible.get_character(c)]

        if dry_run:
            payload = build_omni_payload(**kwargs)
            logger.info(f"[dry-run] Çekim {n} ({res['units']} birim) payload:\n"
                        f"{json.dumps(payload, ensure_ascii=False, indent=2)}")
            continue

        result = generate_omni_shot(**kwargs)
        credits = None
        status = "FAIL"
        video_url = ""
        if result and result.get("url"):
            video_url = result["url"]
            credits = result.get("credits")
            if download_file(video_url, out_file):
                shot_files.append(out_file)
                status = "ok"
            if credits is not None:
                cost_tracker.log_cost(f"series:{slug}", f"omni_ep{number}_shot{n}",
                                      "gemini-omni-video", credits)

        report.append_row(slug, report.make_row(
            episode=number, shot_n=n, characters=char_names,
            audio_ids=kwargs["audio_ids"], duration=kwargs["duration"],
            resolution=kwargs["resolution"], seed=kwargs["seed"],
            credits=credits, status=status, video_url=video_url, local_file=out_file,
        ))

    if dry_run:
        logger.info("[dry-run] Simülasyon bitti — dosya/kredi harcanmadı.")
        return None

    if not shot_files:
        logger.error("❌ Hiç çekim üretilemedi, bölüm oluşturulamadı.")
        return None

    # Birleştir → final export (9:16 dikey)
    raw_ep = episode_dir(slug, number) / f"ep{int(number):02d}_raw.mp4"
    ffmpeg_tools.concatenate_simple(shot_files, raw_ep, clips_dir=sdir)
    final_ep = episode_dir(slug, number) / f"ep{int(number):02d}.mp4"
    ffmpeg_tools.final_export(raw_ep, final_ep)

    report.export_xlsx(slug)
    summary = report.summarize(slug)
    logger.info(f"🎉 Bölüm hazır: {final_ep}")
    logger.info(f"   📊 {summary['başarılı']}/{summary['çekim_sayısı']} çekim, "
                f"{summary['toplam_kredi']} kredi (~${summary['toplam_dolar']})")
    return final_ep
