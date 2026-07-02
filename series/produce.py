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
from core.kie_api import (
    generate_image, check_credit,
    generate_seedance_video, generate_veo_video, generate_video,
)
from core import ffmpeg_tools, cost_tracker

from .bible import Bible, refs_dir, episode_dir, shots_dir, resolve_voice_id
from .omni_api import register_audio, register_character, generate_omni_shot, build_omni_payload
from .shots import resolve_shot, resolve_visual_shot, validate_plan, load_plan, plan_summary
from . import report
from .voices import is_preset


# ─── Çok-motorlu görsel klip üretimi (Omni-dışı ucuz motorlar) ──────────────────

def _generate_visual_clip(engine: str, prompt: str, start_url: str | None,
                          duration, aspect_ratio: str, resolution: str,
                          sound: bool = True) -> dict | None:
    """Omni-DIŞI ucuz motorlarla tek klip üret. Dönüş: {"url", "credits"} | None.
    Seedance native ses + I2V (en ucuz); Veo Lite/Fast yedek; Kling son çare.
    """
    eng = (engine or "seedance").lower()
    dur = str(duration)
    if eng in ("seedance", "seedance-2", "seedance_fast", "bytedance/seedance-2-fast"):
        return generate_seedance_video(prompt, first_frame_url=start_url, duration=dur,
                                       aspect_ratio=aspect_ratio, resolution="720p", sound=sound)
    if eng in ("veo3_lite", "veo_lite"):
        url = generate_veo_video(prompt, image_url=start_url, duration=dur, model="veo3_lite")
        return {"url": url, "credits": None} if url else None
    if eng in ("veo3_fast", "veo_fast", "veo3", "veo"):
        url = generate_veo_video(prompt, image_url=start_url, duration=dur, model="veo3_fast")
        return {"url": url, "credits": None} if url else None
    if eng in ("kling", "kling-2.6"):
        try:
            url = generate_video(prompt, start_image_url=start_url, duration=dur, sound=sound)
        except Exception:
            url = None
        return {"url": url, "credits": None} if url else None
    # bilinmeyen → Seedance'e düş
    return generate_seedance_video(prompt, first_frame_url=start_url, duration=dur,
                                   aspect_ratio=aspect_ratio, resolution="720p", sound=sound)


def _post_process(bible: Bible, plan: dict, final_ep: Path) -> Path:
    """Final videoya anlatım (narration) + SÜREKLİ müzik ekle (best-effort).

    Ses tasarımı (kullanıcı geri bildirimi): her AI çekiminin kendi 'native' sesi
    çekim sınırlarında 'pop'lar ve boşluk/sessizlik bırakır. Çözüm:
      • Anlatım varsa  → gappy native ses TAMAMEN düşürülür (bg_duck=0); temiz tek
        anlatım + sürekli müzik bedi kalır.
      • Anlatım yoksa (saf görsel şölen kanalları) → müzik TEK ses olur (native
        atılır) → çekim kesişlerinde boşluk imkânsız.
    Müzik HER VİDEO için ayrı üretilir (kanal stiline sadık ama her video benzersiz).
    """
    out = final_ep
    number = plan.get("episode", {}).get("number", 1)
    narr_cfg = bible.narration
    narr_text = (plan.get("narration") or "").strip()
    narration_ok = False

    if narr_cfg.get("channel") and narr_text:
        try:
            from core.narration import create_narration_for_channel
            wav = episode_dir(bible.slug, number) / "narration.wav"
            audio_path, style = create_narration_for_channel(narr_cfg["channel"], narr_text, wav)
            if audio_path and Path(audio_path).exists():
                narrated = out.parent / f"{out.stem}_narrated.mp4"
                # bg_duck=0 → gappy native sesi at; anlatım tek temiz ses olsun
                ffmpeg_tools.mix_voiceover(str(out), str(audio_path), str(narrated),
                                           voice_volume=1.0, bg_duck=0.0)
                if narrated.exists() and narrated.stat().st_size > 0:
                    out = narrated
                    narration_ok = True
                    logger.info(f"🎙️ Anlatım eklendi ({style})")
        except Exception as e:
            logger.warning(f"⚠️ Anlatım atlandı: {e}")

    if bible.music:
        try:
            from core.music_generator import generate_background_music
            ch = narr_cfg.get("channel") or bible.slug
            # Her video kendi müziğini alsın → benzersiz dosya = benzersiz üretim
            music_file = episode_dir(bible.slug, number) / "bg_music.mp3"
            music_path = generate_background_music(ch, output_path=music_file)
            if music_path and Path(music_path).exists():
                music_out = out.parent / f"{out.stem}_music.mp4"
                if narration_ok:
                    # anlatım + sürekli müzik bedi (boşluk zaten kalmadı)
                    ffmpeg_tools.mix_background_music(out, music_path, music_out, music_volume=0.28)
                else:
                    # saf görsel: müzik TEK sürekli ses olsun (gappy native atılır)
                    ffmpeg_tools.mix_background_music(out, music_path, music_out,
                                                      music_volume=0.9, replace_original=True)
                if music_out.exists() and music_out.stat().st_size > 0:
                    out = music_out
                    logger.info("🎵 Müzik eklendi" + ("" if narration_ok else " (tek/sürekli ses)"))
        except Exception as e:
            logger.warning(f"⚠️ Müzik atlandı: {e}")

    return out


# ─── Kurgu-öncesi çekim hazırlığı (micro_trim + CCTV giydirme; opt-in) ─────────

def _cam_epoch(date_str: str | None, cam_time: str | None) -> int | None:
    """'2026-06-14' + '02:47[:33]' → UTC epoch (CCTV saatinin işlemeye başlayacağı an)."""
    if not cam_time:
        return None
    try:
        import calendar
        import time as _time
        d = (date_str or "2026-01-01").strip()
        hms = str(cam_time).strip()
        if len(hms.split(":")) == 2:
            hms += ":00"
        return calendar.timegm(_time.strptime(f"{d} {hms}", "%Y-%m-%d %H:%M:%S"))
    except Exception:
        return None


def _cam_date_text(date_str: str | None) -> str:
    """ISO tarih ('2026-06-14') → CCTV overlay tarih metni ('06/14/2026')."""
    try:
        y, m, d = (int(x) for x in (date_str or "").split("-"))
        return f"{m:02d}/{d:02d}/{y}"
    except Exception:
        return date_str or ""


def _prep_shot_clip(bible: Bible, plan: dict, shot: dict, src: Path) -> Path:
    """Kurguya girmeden önce çekimi hazırla (opt-in): micro_trim + CCTV giydirme.

    Çıktı yan dosyada cache'lenir (*_prep.mp4) → yarım kalan koşular idempotent.
    Kare zinciri (chain_frames) HAM klipten beslenmeye devam eder — yakılan
    timestamp/grain bir sonraki çekimin başlangıç karesine sızmaz. Her adım
    best-effort: hazırlık başarısızsa ham klip kullanılır, gece koşusu durmaz."""
    cfg = bible.cctv
    trim = bible.micro_trim
    if not cfg and not trim:
        return src
    prep = src.parent / f"{src.stem}_prep.mp4"
    if prep.exists() and prep.stat().st_size > 0:
        return prep
    work = src
    try:
        if trim:
            tpath = src.parent / f"{src.stem}_trim.mp4"
            work = ffmpeg_tools.trim_head_tail(src, tpath, head=trim, tail=trim)
            if not cfg:
                Path(work).replace(prep)   # sadece kırpma → cache sözleşmesi korunur
                return prep
        pcfg = {**cfg, **(plan.get("cctv") or {})}   # bible varsayılan, plan bölüme özgü
        ffmpeg_tools.cctv_overlay(
            work, prep,
            camera_label=pcfg.get("camera", "CAM 01"),
            date_text=_cam_date_text(pcfg.get("date")),
            epoch=_cam_epoch(pcfg.get("date"), shot.get("cam_time")),
            fps=pcfg.get("fps", 18),
            grain=pcfg.get("grain", 7),
            caption=shot.get("caption"),
        )
        if prep.exists() and prep.stat().st_size > 0:
            return prep
    except Exception as e:
        logger.warning(f"⚠️ Çekim hazırlığı başarısız ({src.name}): {e} — ham klip kullanılacak")
    return src


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

def produce_episode(slug: str, plan, dry_run: bool = False,
                    chain_start_url: str | None = None) -> Path | None:
    """Bir bölümü üret: çekimler → indir → birleştir → (anlatım/müzik) → rapor.

    Çok-motorlu: her çekim bible.engine (veya shot['engine']) ile 'omni' VEYA ucuz
    görsel motor (seedance/veo/kling) kullanır.
    bible.chain_frames=True ise 'bitmeyen yolculuk': her çekimin son karesi sonrakinin
    başlangıç karesi olur; chain_start_url önceki BÖLÜMün son karesidir (parçalar arası).
    plan: dict veya episode_plan.json yolu.
    """
    bible = Bible.load(slug)
    if not bible:
        return None
    if isinstance(plan, (str, Path)):
        plan = load_plan(plan)

    number = plan.get("episode", {}).get("number", 1)
    default_engine = bible.engine
    chaining = bible.chain_frames
    logger.info(f"🎬 {plan_summary(plan)} (motor={default_engine}, zincir={chaining}, dry_run={dry_run})")

    # Doğrulama — 7-birim kota / ses yalnız OMNI çekimleri için geçerli.
    v = validate_plan(plan, bible)
    for w in v["warnings"]:
        logger.warning(f"⚠️ {w}")
    for e in v["errors"]:
        logger.error(f"❌ {e}")
    # Omni-dışı varsayılan motorda kota hataları üretimi durdurmaz (Omni'ye özgü).
    if v["errors"] and default_engine == "omni" and not dry_run:
        logger.error("Plan hataları nedeniyle üretim durduruldu.")
        return None

    sdir = shots_dir(slug, number)
    sdir.mkdir(parents=True, exist_ok=True)

    if not dry_run:
        check_credit()  # ücretsiz okuma — başlangıç bakiyesi loglanır

    chain_url = chain_start_url if chaining else None
    last_frame_url = None
    shot_files: list[Path] = []
    shot_offsets: dict[int, float] = {}   # kanca için: çekim n → birleşik videodaki başlangıç sn
    running = 0.0

    for shot in plan["shots"]:
        n = shot.get("n")
        out_file = sdir / f"shot_{int(n):02d}.mp4"
        shot_engine = (shot.get("engine") or default_engine).lower()

        # İdempotent: bu çekim zaten üretildiyse atla; zincir için son karesini yine de al
        if not dry_run and out_file.exists() and out_file.stat().st_size > 0:
            logger.info(f"⏭️ Çekim {n} zaten var, atlanıyor: {out_file.name}")
            prep = _prep_shot_clip(bible, plan, shot, out_file)
            shot_offsets[int(n)] = running
            running += ffmpeg_tools.get_video_duration(prep)
            shot_files.append(prep)
            if chaining:
                lf = ffmpeg_tools.extract_last_frame(out_file)
                if lf:
                    up = upload_to_imgbb(lf)
                    if up:
                        chain_url = up
                        last_frame_url = up
            continue

        # ── OMNI çekimi (karakter + ses tutarlılığı) ──────────────────────────
        if shot_engine == "omni":
            res = resolve_shot(bible, shot)
            kwargs = res["kwargs"]
            # Bitmeyen yolculuk: önceki çekimin/bölümün son karesini referans olarak ekle
            if chaining and chain_url:
                kwargs["image_urls"] = [chain_url] + list(kwargs.get("image_urls") or [])
            char_names = [bible.get_character(c).get("name", c)
                          for c in shot.get("characters", []) if bible.get_character(c)]
            if dry_run:
                payload = build_omni_payload(**kwargs)
                logger.info(f"[dry-run] Çekim {n} OMNI ({res['units']} birim):\n"
                            f"{json.dumps(payload, ensure_ascii=False, indent=2)[:700]}")
                continue
            result = generate_omni_shot(**kwargs)
            # GÜVENLİK AĞI: İçerik filtresi en sık KONUŞAN İNSAN (audio_ids) çekimlerini
            # 'flagged content' diye reddeder. Sesli çekim başarısızsa sesi düşürüp SESSİZ
            # görsel olarak bir kez daha dene — anlatım zaten post'ta eklendiği için seri
            # tamamen durmaz (bir dizinin günlerce sessizce çökmesini engeller).
            if (not result or not result.get("url")) and kwargs.get("audio_ids"):
                logger.warning("⚠️ Sesli çekim başarısız (muhtemelen içerik filtresi) → "
                               "SESSİZ görsel olarak yeniden deneniyor (ses post-anlatıma bırakılır)")
                fb_kwargs = dict(kwargs)
                fb_kwargs["audio_ids"] = []
                result = generate_omni_shot(**fb_kwargs)
            credits, status, video_url = None, "FAIL", ""
            if result and result.get("url"):
                video_url = result["url"]
                credits = result.get("credits")
                if download_file(video_url, out_file):
                    prep = _prep_shot_clip(bible, plan, shot, out_file)
                    shot_offsets[int(n)] = running
                    running += ffmpeg_tools.get_video_duration(prep)
                    shot_files.append(prep)
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
            if chaining and status == "ok":
                lf = ffmpeg_tools.extract_last_frame(out_file)
                if lf:
                    up = upload_to_imgbb(lf)
                    if up:
                        chain_url = up
                        last_frame_url = up
            continue

        # ── Ucuz görsel motor (seedance / veo / kling) ────────────────────────
        rv = resolve_visual_shot(bible, shot, chain_url=chain_url)
        if dry_run:
            src = "zincir" if chain_url else ("ortam/figür" if rv["start_image_url"] else "yok")
            logger.info(f"[dry-run] Çekim {n} {shot_engine.upper()} | başlangıç={src} | "
                        f"{rv['duration']}s | {rv['prompt'][:140]}...")
            continue
        result = _generate_visual_clip(shot_engine, rv["prompt"], rv["start_image_url"],
                                       rv["duration"], bible.aspect_ratio, bible.resolution,
                                       sound=bible.native_audio)
        credits, status, video_url = None, "FAIL", ""
        if result and result.get("url"):
            video_url = result["url"]
            credits = result.get("credits")
            if download_file(video_url, out_file):
                prep = _prep_shot_clip(bible, plan, shot, out_file)
                shot_offsets[int(n)] = running
                running += ffmpeg_tools.get_video_duration(prep)
                shot_files.append(prep)
                status = "ok"
            if credits is not None:
                cost_tracker.log_cost(f"series:{slug}", f"{shot_engine}_ep{number}_shot{n}",
                                      shot_engine, credits)
        report.append_row(slug, report.make_row(
            episode=number, shot_n=n, characters=[], audio_ids=[],
            duration=rv["duration"], resolution="720p", seed=None,
            credits=credits, status=status, video_url=video_url, local_file=out_file,
        ))
        if chaining and status == "ok":
            lf = ffmpeg_tools.extract_last_frame(out_file)
            if lf:
                up = upload_to_imgbb(lf)
                if up:
                    chain_url = up
                    last_frame_url = up

    if dry_run:
        logger.info("[dry-run] Simülasyon bitti — dosya/kredi harcanmadı.")
        return None

    if not shot_files:
        logger.error("❌ Hiç çekim üretilemedi, bölüm oluşturulamadı.")
        return None

    # Birleştir → final export (9:16 dikey)
    raw_ep = episode_dir(slug, number) / f"ep{int(number):02d}_raw.mp4"
    if bible.audio_smooth:
        # Atmosfer/müzik kanalları: çekim sınırlarında sesi yumuşat (pop/boşluk gider).
        ffmpeg_tools.concatenate_audio_smooth(shot_files, raw_ep, clips_dir=sdir)
    else:
        # Diyalog kanalları: düz birleştir (söz baş/sonu kırpılmasın).
        ffmpeg_tools.concatenate_simple(shot_files, raw_ep, clips_dir=sdir)
    final_ep = episode_dir(slug, number) / f"ep{int(number):02d}.mp4"
    ffmpeg_tools.final_export(raw_ep, final_ep)

    # Anlatım (narration) + arka plan müziği (best-effort)
    final_ep = _post_process(bible, plan, final_ep)

    # Açılış kancası (opt-in): doruk çekimden kısa bir kesit videonun EN BAŞINA
    # eklenir — ilk 1-2 saniyede 'olağandışı an' görünmezse Shorts'ta kaydırılır.
    # Müzik/anlatımdan SONRA yapılır ki kesit sesiyle birlikte gelsin.
    hook = bible.hook_teaser
    if hook and shot_offsets:
        try:
            ns = sorted(shot_offsets)
            hn = int(plan.get("hook_shot") or (ns[-2] if len(ns) >= 2 else ns[-1]))
            if hn not in shot_offsets:
                raise ValueError(f"hook_shot={hn} üretilen çekimler arasında değil")
            d = float(hook.get("duration", 1.4))
            skip = float(hook.get("offset_in_shot", 1.6))
            total = ffmpeg_tools.get_video_duration(final_ep)
            start = min(shot_offsets[hn] + skip, max(0.0, total - d - 0.25))
            teaser = episode_dir(slug, number) / "hook_teaser.mp4"
            ffmpeg_tools.extract_clip(final_ep, teaser, start, d)
            hooked = Path(final_ep).parent / f"{Path(final_ep).stem}_hooked.mp4"
            ffmpeg_tools.concatenate_simple([teaser, Path(final_ep)], hooked,
                                            clips_dir=Path(final_ep).parent)
            if hooked.exists() and hooked.stat().st_size > 0:
                final_ep = hooked
                logger.info(f"🎣 Kanca: çekim {hn} dorukundan {d:.1f}s (t={start:.1f}s) başa eklendi")
        except Exception as e:
            logger.warning(f"⚠️ Kanca eklenemedi (video kancasız yayınlanır): {e}")

    # Parçalar arası zincir: bölümün son karesini sonraki bölüm için sakla (sidecar).
    # chain_scope="episode" ise bölümler arası taşıma YOK — sidecar yazılmaz.
    if chaining and bible.chain_scope == "series":
        if not last_frame_url:
            lf = ffmpeg_tools.extract_last_frame(final_ep)
            if lf:
                last_frame_url = upload_to_imgbb(lf)
        if last_frame_url:
            (episode_dir(slug, number) / "last_frame.txt").write_text(last_frame_url, encoding="utf-8")
            logger.info("🔗 Son kare bir sonraki bölüm için saklandı (bitmeyen yolculuk).")

    report.export_xlsx(slug)
    summary = report.summarize(slug)
    logger.info(f"🎉 Bölüm hazır: {final_ep}")
    logger.info(f"   📊 {summary['başarılı']}/{summary['çekim_sayısı']} çekim, "
                f"{summary['toplam_kredi']} kredi (~${summary['toplam_dolar']})")
    return final_ep
