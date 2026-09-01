"""
Üretim Orkestrasyonu — Gemini Omni mini-dizi.

İki ana akış:
  setup_references(slug)  → referans görseller (üret/yükle) + ses + karakter kaydı (bible.json'a yazar)
  produce_episode(slug, plan) → her çekimi üret, indir, birleştir, raporla

dry_run=True her ikisinde de API/kredi harcamadan adımları simüle eder.
"""

import hashlib
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from core.config import logger
from core.utils import download_file, sanitize_filename
from core.imgbb import upload_to_imgbb
from core.kie_api import (
    generate_image, check_credit,
    generate_seedance_video, generate_veo_video, generate_video,
    upload_file_to_kie, generate_topaz_upscale,
)
from core import ffmpeg_tools, cost_tracker

from .bible import (
    Bible,
    atomic_write_json,
    bible_path,
    doctrine_path,
    doctrine_repo_path,
    doctrine_sha256,
    refs_dir,
    episode_dir,
    shots_dir,
    resolve_voice_id,
)
from .omni_api import (
    register_audio, register_character, generate_omni_shot, build_omni_payload,
    validate_ref_units,
)
from .series_meta import SeriesMeta, part_plan_path
from .shots import (
    TEK_OBJE_FORMAT,
    resolve_shot,
    resolve_visual_shot,
    validate_plan,
    load_plan,
    plan_summary,
)
from . import credit_gate, critic, report
from .voices import is_preset


@dataclass(frozen=True)
class ChainDecision:
    """Pure per-shot chain decision used by production and preflight tracing."""

    start_url: str | None
    reset_before: bool
    require_previous: bool
    capture_last_frame: bool
    explicit: bool
    error: str | None = None


@dataclass(frozen=True)
class ProduceResult:
    """Typed production outcome used by the scheduler's fail-closed state machine."""

    status: Literal["ok", "qc_hold", "generation_fail"]
    path: Path | None = None
    reason: str | None = None

    def __post_init__(self):
        if self.status not in ("ok", "qc_hold", "generation_fail"):
            raise ValueError(f"unknown ProduceResult status: {self.status}")
        if self.status == "ok" and self.path is None:
            raise ValueError("ok ProduceResult requires a path")
        if self.status != "ok" and self.path is not None:
            raise ValueError("non-ok ProduceResult cannot carry a final path")


def decide_shot_chain(shot: dict, next_shot: dict | None, chain_frames: bool,
                      available_url: str | None) -> ChainDecision:
    """Decide current input/reset and look-ahead frame capture without side effects.

    A missing ``chain`` field is the exact legacy mode. Explicit fields enable the
    segmented fail-closed semantics.
    """
    if "chain" not in shot:
        return ChainDecision(
            start_url=available_url if chain_frames else None,
            reset_before=False,
            require_previous=False,
            capture_last_frame=bool(chain_frames),
            explicit=False,
        )
    value = shot.get("chain")
    if not isinstance(value, bool):
        return ChainDecision(None, False, False, False, True, "chain bool olmalı")
    if value and not chain_frames:
        return ChainDecision(
            None, False, False, False, True,
            "chain=true için bible.series.chain_frames=true olmalı",
        )
    next_chained = False
    if next_shot is not None:
        next_chained = (
            next_shot.get("chain") is True
            if "chain" in next_shot else bool(chain_frames)
        )
    if value is False:
        return ChainDecision(None, True, False, next_chained, True)
    if not available_url:
        return ChainDecision(
            None, False, True, next_chained, True,
            "chain=true fakat önceki son kare yok",
        )
    return ChainDecision(available_url, False, True, next_chained, True)


def episode_spent(slug: str, number: int) -> float | None:
    """Maliyet izleyicisinden bu serinin bu bölüm toplam kredisini oku."""
    bible = Bible.load(slug)
    if bible and bible.data["series"].get("durable_credit_ledger"):
        return credit_gate.episode_spent(slug, number)
    path = cost_tracker.COST_LOG
    if not path.exists():
        return 0.0
    try:
        history = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(history, list):
            raise ValueError("maliyet kaydı liste değil")
    except Exception as error:
        logger.error(f"❌ Bölüm kredi toplamı okunamadı: {error}")
        return None
    marker = f"_ep{int(number)}"
    total = 0.0
    for entry in history:
        if not isinstance(entry, dict) or entry.get("channel") != f"series:{slug}":
            continue
        operation = str(entry.get("operation") or "")
        pos = operation.find(marker)
        if pos < 0:
            continue
        suffix = operation[pos + len(marker):]
        if suffix and not suffix.startswith("_"):
            continue
        try:
            total += float(entry.get("credits") or 0)
        except (TypeError, ValueError):
            logger.error(f"❌ Geçersiz kredi kaydı: {entry}")
            return None
    return total


def episode_credit_cap(bible: Bible) -> int:
    """Use a reviewed series cap when configured; legacy series keep the env cap."""
    value = bible.data["series"].get("credit_hard_cap_value")
    if value is None:
        return credit_gate.episode_cap()
    try:
        cap = int(value)
    except (TypeError, ValueError):
        return 0
    return cap if cap > 0 else 0


def series_monthly_credit_cap(bible: Bible) -> int | None:
    """Return an opt-in per-series monthly cap; legacy series remain global."""
    value = bible.data["series"].get("credit_monthly_cap_value")
    if value is None:
        return None
    try:
        cap = int(value)
    except (TypeError, ValueError):
        return 0
    return cap if cap > 0 else 0


def _record_episode_cost(bible: Bible, number: int, operation: str,
                         model: str, credits: float | int | None, *,
                         isolated: bool = False) -> bool:
    """Write the legacy cost log and, when opted in, the durable episode ledger."""
    if credits is None:
        return True
    if isolated:
        # The experiment ledger is the sole durable spend record for isolated
        # runs. Never contaminate production episode/monthly accounting.
        return True
    if bible.data["series"].get("durable_credit_ledger"):
        if not credit_gate.record_episode_spend(bible.slug, number, float(credits)):
            return False
    cost_tracker.log_cost(f"series:{bible.slug}", operation, model, credits)
    return True


def _revalidate_cached_shot(slug: str, episode: int, shot: int,
                            path: Path, qc: dict | None = None,
                            experiment_id: str | None = None) -> bool:
    """Bind a cache hit to valid media and an exact content-hash QC pass."""
    content_hash = critic.content_sha256(path)
    media_ok = ffmpeg_tools.validate_media(path)
    pass_ok = critic.qc_pass_exists(
        slug, episode, shot, content_hash, qc,
        experiment_id=experiment_id,
    )
    if media_ok and pass_ok:
        return True
    suffix = (content_hash or "unreadable")[:12]
    stale = path.with_name(f"{path.stem}_stale_{suffix}{path.suffix}")
    serial = 1
    while stale.exists():
        stale = path.with_name(f"{path.stem}_stale_{suffix}_{serial}{path.suffix}")
        serial += 1
    critic._clean_sidecars(path)
    path.replace(stale)
    logger.warning(
        f"⚠️ Bayat çekim cache'i ayrıldı: {stale.name} "
        f"(media_ok={media_ok}, qc_hash_pass={pass_ok})"
    )
    return False


def _episode_work_dir(slug: str, number: int,
                      output_area: str | Path | None = None) -> Path:
    return Path(output_area) if output_area is not None else episode_dir(slug, number)


def _shots_work_dir(slug: str, number: int,
                    output_area: str | Path | None = None) -> Path:
    return (
        Path(output_area) / "shots"
        if output_area is not None else shots_dir(slug, number)
    )


def _refs_work_dir(slug: str, kind: str,
                   output_area: str | Path | None = None) -> Path:
    return (
        Path(output_area) / "refs" / kind
        if output_area is not None else refs_dir(slug, kind)
    )


def _qc_regen_allowed(slug: str, number: int) -> bool:
    """QC regen öncesinde bölümün harcanan kredi tavanını denetle."""
    spent = episode_spent(slug, number)
    cap = credit_gate.episode_cap()
    if spent is None:
        logger.warning("⏭️ QC regen atlandı: harcanan kredi okunamadı")
        return False
    if spent >= cap:
        logger.warning(
            f"⏭️ QC regen atlandı: harcanan={spent:g}, bölüm_tavanı={cap}"
        )
        return False
    return True


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


def _gen_omni_with_fallback(kwargs: dict, before_call=None) -> dict | None:
    """Omni çekimi üret; sesli çekim başarısızsa sesi düşürüp SESSİZ görsel olarak
    bir kez daha dene. GÜVENLİK AĞI: içerik filtresi en sık KONUŞAN İNSAN (audio_ids)
    çekimlerini 'flagged content' diye reddeder — anlatım zaten post'ta eklendiği için
    seri tamamen durmaz (bir dizinin günlerce sessizce çökmesini engeller)."""
    if before_call is not None and not before_call():
        return None
    result = generate_omni_shot(**kwargs)
    if (not result or not result.get("url")) and kwargs.get("audio_ids"):
        logger.warning("⚠️ Sesli çekim başarısız (muhtemelen içerik filtresi) → "
                       "SESSİZ görsel olarak yeniden deneniyor (ses post-anlatıma bırakılır)")
        fb_kwargs = dict(kwargs)
        fb_kwargs["audio_ids"] = []
        if before_call is not None and not before_call():
            return None
        result = generate_omni_shot(**fb_kwargs)
    return result


def _reserve_plan_music(bible: Bible, plan: dict,
                        hard_cap,
                        number: int, *, isolated: bool = False) -> bool | None:
    """Suno müziğini çekimlerden önce ayır.

    True rezervasyon yapıldığını, None rezervasyon gerekmediğini, False ise sert
    tavanın rezervasyonu engellediğini belirtir.
    """
    music_prompt = str(plan.get("music") or "").strip()
    if (hard_cap is None or not bible.music or not music_prompt
            or bible.data["series"].get("credit_excludes_music")):
        return None
    if not hard_cap.authorize("music", "suno"):
        return False
    # Suno creditsConsumed döndürmüyor. Üretim daha sonra başarısız olsa bile
    # korumacı tahmin harcanmış sayılır.
    if not _record_episode_cost(
        bible, number, f"suno_estimate_ep{number}", "suno", hard_cap.last_estimate,
        isolated=isolated,
    ):
        return False
    return True


def _post_process(bible: Bible, plan: dict, final_ep: Path,
                  hard_cap=None,
                  required_music: bool = False,
                  music_reserved: bool = False, *,
                  output_area: str | Path | None = None,
                  isolated: bool = False) -> Path | None:
    """Final videoya anlatım (narration) + SÜREKLİ müzik ekle (best-effort).

    Ses tasarımı (kullanıcı geri bildirimi): her AI çekiminin kendi 'native' sesi
    çekim sınırlarında 'pop'lar ve boşluk/sessizlik bırakır. Çözüm:
      • Anlatım varsa → narration.native_mix_level ham sese bütün miks boyunca
        sabit çarpan uygular; alan yoksa tarihsel 0.0 davranışı korunur.
      • Anlatım yoksa (saf görsel şölen kanalları) → müzik TEK ses olur (native
        atılır) → çekim kesişlerinde boşluk imkânsız.
    Müzik HER VİDEO için ayrı üretilir (kanal stiline sadık ama her video benzersiz).
    """
    out = final_ep
    number = plan.get("episode", {}).get("number", 1)
    narr_cfg = bible.narration
    narr_text = (plan.get("narration") or "").strip()
    narration_ok = False
    music_ok = False

    if narr_cfg.get("channel") and narr_text:
        try:
            from core.narration import create_narration_for_channel
            wav = _episode_work_dir(bible.slug, number, output_area) / "narration.wav"
            audio_path, style = create_narration_for_channel(narr_cfg["channel"], narr_text, wav)
            if audio_path and Path(audio_path).exists():
                narrated = out.parent / f"{out.stem}_narrated.mp4"
                # Adı legacy kalsa da bg_duck sidechain değildir; bütün klip boyunca
                # native sese uygulanan sabit seviye çarpanıdır.
                ffmpeg_tools.mix_voiceover(str(out), str(audio_path), str(narrated),
                                           voice_volume=1.0,
                                           bg_duck=bible.native_mix_level,
                                           amix_normalize=bible.master_lufs is None)
                if narrated.exists() and narrated.stat().st_size > 0:
                    out = narrated
                    narration_ok = True
                    logger.info(f"🎙️ Anlatım eklendi ({style})")
        except Exception as e:
            logger.warning(f"⚠️ Anlatım atlandı: {e}")

    # Anlatım BEKLENEN seride TTS başarısızsa sessiz kalma (the-signal dersi: sessiz
    # başarısızlık günlerce fark edilmez) — video müzik-only çıkar ama Telegram'a haber ver.
    if narr_cfg.get("channel") and narr_text and not narration_ok:
        try:
            from series import notifier
            if notifier.enabled():
                notifier.send_message(f"⚠️ *{bible.title}* ep{number}: anlatım (TTS) üretilemedi — "
                                      f"video anlatımsız (müzik-only) yayınlanacak.")
        except Exception:
            pass

    if bible.music:
        try:
            from core.music_generator import generate_background_music
            ch = narr_cfg.get("channel") or bible.slug
            # Her video kendi müziğini alsın → benzersiz dosya = benzersiz üretim
            music_file = _episode_work_dir(bible.slug, number, output_area) / "bg_music.mp3"
            # Plan sahneye-özel müzik prompt'u taşıyorsa (plan['music'], Gemini
            # yönetmen sahneyle birlikte yazar) müzik motoru Suno'ya gider →
            # her videonun skoru görüntünün ruhuna birebir eşleşir. Alan yoksa
            # davranış ESKİSİYLE AYNI (Lyria → ambient bed).
            music_prompt = str(plan.get("music") or "").strip() or None
            ep_title = str(plan.get("episode", {}).get("title") or "").strip()
            if (music_prompt and hard_cap is not None and not music_reserved
                    and not bible.data["series"].get("credit_excludes_music")):
                if not hard_cap.authorize("music", "suno"):
                    return None
                # Doğrudan çağrılarda ön rezervasyon yoktur; eski güvenli davranış
                # korunur ve Suno tahmini burada bir kez ayrılır.
                if not _record_episode_cost(
                    bible, number, f"suno_estimate_ep{number}", "suno",
                    hard_cap.last_estimate, isolated=isolated,
                ):
                    return None
            music_path = generate_background_music(ch, custom_prompt=music_prompt,
                                                   output_path=music_file, title=ep_title)
            if music_path and Path(music_path).exists():
                music_out = out.parent / f"{out.stem}_music.mp4"
                if narration_ok:
                    # anlatım + sürekli müzik bedi (boşluk zaten kalmadı)
                    # normalize=0 programı legacy mikse göre 6,1 LU yükselttiği için
                    # opt-in yatak 0.50'ye eşlendi (foley/yatak +6,19 dB;
                    # anlatım/yatak değişimi +0,42 dB). Legacy yol 0.28 kalır.
                    music_volume = 0.50 if bible.master_lufs is not None else 0.28
                    ffmpeg_tools.mix_background_music(
                        out, music_path, music_out, music_volume=music_volume
                    )
                else:
                    # saf görsel: müzik TEK sürekli ses olsun (gappy native atılır)
                    ffmpeg_tools.mix_background_music(out, music_path, music_out,
                                                      music_volume=0.9, replace_original=True)
                if music_out.exists() and music_out.stat().st_size > 0:
                    out = music_out
                    music_ok = True
                    logger.info("🎵 Müzik eklendi" + ("" if narration_ok else " (tek/sürekli ses)"))
        except Exception as e:
            logger.warning(f"⚠️ Müzik atlandı: {e}")

    if required_music and not music_ok:
        logger.error("❌ Zorunlu teslimat katmanı üretilemedi: music")
        return None

    return out


def _verify_native_audio_delivery(bible: Bible, number: int, final_ep: Path, *,
                                  experiment_id: str | None = None) -> bool:
    """Fail-closed delivery gate for a required native construction soundtrack."""
    mean_volume = ffmpeg_tools.measure_mean_volume(final_ep)
    logger.info(f"🔊 Diegetik ses ölçümü: mean_volume={mean_volume!r} dB")
    audio_review = None
    failure = None
    if mean_volume is None:
        failure = "mean_volume ölçülemedi veya ses akışı yok"
    elif mean_volume < -50.0:
        failure = f"mean_volume çok düşük ({mean_volume:.1f} dB < -50.0 dB)"
    else:
        audio_review = critic.qc_audio(
            final_ep, slug=bible.slug, episode=number,
            experiment_id=experiment_id, api_fail_closed=True,
        )
        logger.info(
            "🔊 Diegetik ses Gemini ölçümü: "
            + json.dumps(audio_review, ensure_ascii=False, sort_keys=True)
        )
        if audio_review is None:
            failure = "Gemini ses denetimi doğrulanamadı (API/anahtar/JSON hatası)"
        elif audio_review["has_music"] is True:
            failure = "müzik algılandı"
        elif audio_review["speech"] is True:
            failure = "konuşma algılandı"
        elif not audio_review["construction_sounds"]:
            failure = "inşaat sesi algılanmadı"
        elif audio_review["silent_fraction_estimate"] > 0.5:
            failure = (
                "sessiz bölüm oranı çok yüksek "
                f"({audio_review['silent_fraction_estimate']:.3f} > 0.5)"
            )
    if not failure:
        logger.info("✅ Diegetik ses kapısı geçti: müziksiz inşaat sesi doğrulandı")
        return True

    message = (
        f"❌ Zorunlu teslimat katmanı doğrulanamadı: native_audio — {failure}. "
        "Yayın durduruldu; ELLE BAK."
    )
    logger.error(message)
    try:
        from series import notifier
        if notifier.enabled():
            notifier.send_message(f"🔊 *{bible.title}* ep{number}: {message}")
    except Exception as error:
        logger.warning(f"⚠️ Diegetik ses kapısı bildirimi gönderilemedi: {error}")
    return False


def _verify_audio_master(path: Path, target_lufs: float) -> bool:
    """Master teslimini fail-closed LUFS/true-peak kapısından geçir."""
    measured = ffmpeg_tools.measure_audio_loudness(path)
    if measured is None:
        logger.error(f"❌ Ses master doğrulaması ölçülemedi: {path}")
        return False
    loudness = measured["integrated_lufs"]
    true_peak = measured["true_peak_dbtp"]
    logger.info(
        f"🎚️ Ses master doğrulaması {path.name}: "
        f"I={loudness:.1f} LUFS, TP={true_peak:.1f} dBTP"
    )
    return abs(loudness - target_lufs) <= 1.0 and true_peak <= -1.0


def _audio_master_hold(reason: str) -> ProduceResult:
    logger.error(f"❌ Ses master teslimatı QC hold: {reason}")
    return ProduceResult("qc_hold", reason=reason)


# ─── 4K master (opt-in: bible.upscale; best-effort) ───────────────────────────

# ROCK B: referans prompt sablonunun surumu; sablon metni degistiginde ARTIRILIR,
# boylece eski hash tutmaz ve tum referanslar yeniden uretilir.
REF_PROMPT_TEMPLATE_VERSION = "rb1"
REFERENCE_IMAGE_MODEL = "nano-banana-2"

TOPAZ_INPUT_LIMIT_MB = 50   # topaz/video-upscale girdi dosya limiti


def _upscale_master(bible: Bible, number: int, src: Path, *, hard_cap=None,
                    isolated: bool = False) -> Path:
    """Final videoyu 4K master'a yükselt (bible.upscale açıksa).

    Birincil yol: Kie 'topaz/video-upscale' — kareyi yeniden inşa eder (gerçek detay).
      Akış: yerel final → Kie geçici deposu (3 gün) → upscale görevi → 4K indir.
    Yedek yol: yerel ffmpeg lanczos ×2 — API başarısızsa bile 4K konteyner garanti.
    Yan ürün: 1080p kaynak episode_dir/delivery_1080.mp4 olarak saklanır; yayında
    IG/TikTok bunu alır (4K yalnız YouTube'a gider — diğerleri zaten 1080p'ye kodlar).
    Her iki yol da başarısızsa 1080p final döner — yayın hiçbir koşulda durmaz."""
    cfg = bible.upscale
    if not cfg:
        return src
    out = src.parent / f"{src.stem}_4k.mp4"
    delivery = src.parent / "delivery_1080.mp4"
    try:
        if not delivery.exists() or delivery.stat().st_size == 0:
            shutil.copy2(src, delivery)
    except Exception as e:
        logger.warning(f"⚠️ delivery_1080 kopyalanamadı: {e}")
    if out.exists() and out.stat().st_size > 0:
        logger.info(f"⏭️ 4K master zaten var: {out.name}")
        return out

    factor = str(cfg.get("factor", "2"))
    # provider: "topaz" (varsayılan; gerçek detay, ölçülen ~8 kredi/sn → 40sn ≈ 320 kredi)
    #           "lanczos" (bedava; yalnız YouTube 4K bitrate merdiveni kazancı)
    provider = str(cfg.get("provider", "topaz")).strip().lower()

    # 1) Topaz (gerçek detay sentezi)
    if provider == "topaz":
        duration = ffmpeg_tools.get_video_duration(src) or 40.0
        if not (isolated and hard_cap is not None):
            spent = episode_spent(bible.slug, number)
            projected = 8 * duration
            cap = episode_credit_cap(bible)
            if spent is None or spent + projected > cap:
                shown = "bilinmiyor" if spent is None else f"{spent:g}"
                logger.warning(
                    f"⏭️ 4K upscale atlandı: harcanan={shown}, "
                    f"tahmini_upscale={projected:g}, bölüm_tavanı={cap}; 1080p kullanılacak"
                )
                return src
        try:
            topaz_in = src
            # Girdi limiti ~50MB: uzun bölümlerin CRF-18 finali aşabilir →
            # çözünürlüğü koruyan bitrate-kapaklı kopya Topaz'a gönderilir
            # (Topaz kareyi zaten yeniden inşa ediyor; 6M 1080p girdi yeterli).
            if src.stat().st_size / (1024 * 1024) > TOPAZ_INPUT_LIMIT_MB:
                shrunk = src.parent / f"{src.stem}_topaz_in.mp4"
                if not shrunk.exists() or shrunk.stat().st_size == 0:
                    ffmpeg_tools.cap_bitrate(src, shrunk, maxrate="6000k", crf="23")
                topaz_in = shrunk
            src_url = upload_file_to_kie(topaz_in, upload_path="series-upscale")
            if src_url:
                if (isolated and hard_cap is not None
                        and not hard_cap.authorize(
                            "upscale", "topaz/video-upscale", duration
                        )):
                    return src
                res = generate_topaz_upscale(src_url, factor)
                raw = src.parent / f"{src.stem}_4k_raw.mp4"
                if (res and res.get("url") and download_file(res["url"], raw)
                        and raw.exists() and raw.stat().st_size > 0):
                    if res.get("credits") is not None:
                        if isolated and hard_cap is not None:
                            if not hard_cap.settle_last(res["credits"]):
                                return src
                        else:
                            cost_tracker.log_cost(
                                f"series:{bible.slug}", f"topaz_ep{number}",
                                "topaz/video-upscale", res["credits"],
                            )
                    # Topaz ~100 Mbps çıkarıyor (40sn ≈ 500MB) → Upload-Post'un
                    # ~80MB limitine sığması için bitrate normalize edilir.
                    if raw.stat().st_size / (1024 * 1024) > 78:
                        ffmpeg_tools.cap_bitrate(raw, out, maxrate="9500k", crf="18")
                    else:
                        raw.replace(out)
                    if out.exists() and out.stat().st_size > 0:
                        logger.info(f"🔍 4K master hazır (Topaz ×{factor}): {out.name}")
                        return out
        except Exception as e:
            logger.warning(f"⚠️ Topaz upscale hatası: {e}")
        logger.warning("⚠️ Topaz yolu başarısız — yerel lanczos yedeğine geçiliyor")

    # 2) Yerel lanczos yedeği
    try:
        ffmpeg_tools.upscale_lanczos(src, out, factor=int(factor))
        if out.exists() and out.stat().st_size > 0:
            logger.info(f"🔍 4K master hazır (lanczos ×{factor}): {out.name}")
            return out
    except Exception as e:
        logger.warning(f"⚠️ Lanczos upscale de başarısız: {e} — 1080p yayınlanacak")
    return src


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


def _valid_https_urls(value, *, count: int | None = None) -> bool:
    if not isinstance(value, list) or (count is not None and len(value) != count):
        return False
    if not value:
        return False
    return all(
        isinstance(url, str)
        and urlparse(url).scheme == "https"
        and bool(urlparse(url).netloc)
        for url in value
    )


def _generate_uploaded_reference(
    bible: Bible,
    prompt: str,
    save_path: Path,
    hard_cap,
    number: int,
    operation: str,
    *,
    isolated: bool = False,
    report_output_dir: str | Path | None = None,
) -> str | None:
    """Cost-authorize one NB2 image, then download and publish it through ImgBB."""
    if not hard_cap.authorize("reference_image", REFERENCE_IMAGE_MODEL):
        return None
    # Image polling exposes no actual charge, so persist the conservative amount
    # before entering the paid call. A crash cannot erase this episode spend.
    estimate = hard_cap.last_estimate
    if estimate is not None:
        if not _record_episode_cost(
            bible, number, f"{operation}_estimate_ep{number}",
            REFERENCE_IMAGE_MODEL, estimate, isolated=isolated,
        ):
            return None
    generated_url = generate_image(
        prompt,
        model=REFERENCE_IMAGE_MODEL,
        aspect_ratio=bible.aspect_ratio,
    )
    if not generated_url:
        logger.error(f"❌ {operation}: Nano Banana 2 referansı üretilemedi")
        return None

    save_path.parent.mkdir(parents=True, exist_ok=True)
    downloaded = download_file(generated_url, save_path)
    uploaded_url = upload_to_imgbb(save_path) if downloaded else None
    status = "ok" if _valid_https_urls([uploaded_url], count=1) else "FAIL"
    report.append_row(bible.slug, report.make_row(
        episode=number,
        shot_n=operation,
        characters=[],
        audio_ids=[],
        duration="",
        resolution="1K",
        seed=None,
        credits=estimate,
        status=status,
        video_url=uploaded_url or generated_url,
        local_file=save_path if downloaded else "",
    ), output_dir=report_output_dir)
    if not downloaded:
        logger.error(f"❌ {operation}: üretilen referans indirilemedi")
        return None
    if status != "ok":
        logger.error(f"❌ {operation}: ImgBB geçerli bir https URL döndürmedi")
        return None
    return uploaded_url


def ensure_episode_refs(
    bible: Bible,
    plan: dict,
    plan_path: str | Path,
    hard_cap=None,
    dry_run: bool = False,
    *,
    output_area: str | Path | None = None,
    isolated: bool = False,
) -> bool:
    """Persist the opt-in episode object ref and its shared environment ref.

    Existing valid URLs are reused. Each new image is authorized before the paid
    call, logged against the episode, and persisted atomically before returning.
    """
    if plan.get("format_version") != TEK_OBJE_FORMAT:
        return True

    try:
        number = int((plan.get("episode") or {}).get("number"))
    except (TypeError, ValueError):
        logger.error("❌ Referans üretimi için geçerli episode.number zorunlu")
        return False
    card = plan.get("object_card")
    if not isinstance(card, dict):
        logger.error("❌ Referans üretimi için object_card zorunlu")
        return False
    env_id = str(card.get("environment") or "").strip()
    environment = bible.get("environments", env_id)
    if not environment:
        logger.error(f"❌ Referans ortamı bible'da yok: {env_id!r}")
        return False

    existing_props = plan.get("prop_ref_urls")
    if existing_props is not None and not _valid_https_urls(existing_props):
        logger.error("❌ prop_ref_urls bir veya daha fazla https URL içermeli")
        return False
    existing_env = environment.get("ref_image_url")
    if existing_env is not None and not _valid_https_urls([existing_env], count=1):
        logger.error(f"❌ Ortam referansı geçerli https URL değil: {env_id}")
        return False

    # ROCK B: referans gorseli objeyi VE anomali imzasini gostermek zorundadir,
    # cunku anomaly_match tam bu referansa karsi olculur. Prompt bilesenlerinden
    # herhangi biri degisirse (isim, descriptor, anomali, ortam, sablon surumu)
    # kayitli referans BAYAT sayilir ve yeniden uretilir.
    ref_name = str(card.get("name") or "object").strip()
    ref_descriptor = str(card.get("descriptor") or "").strip()
    ref_anomaly = str(card.get("anomaly_descriptor") or "").strip()
    ref_env_desc = str(environment.get("desc") or environment.get("name") or env_id).strip()
    object_prompt = (
        f"Hero reference image of one {ref_name} on a plain neutral section of the matching "
        f"surface. Exact object identity: {ref_descriptor}. "
        + (f"The impossible property is visible and looks like this: {ref_anomaly}. "
           if ref_anomaly else "")
        + f"Environment context: {ref_env_desc}. "
        "The entire object is clearly visible at realistic scale with its colour, material "
        "texture and distinguishing mark sharply readable."
    )
    generation_identity = json.dumps({
        "model": REFERENCE_IMAGE_MODEL,
        "aspect_ratio": bible.aspect_ratio,
    }, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    expected_ref_hash = hashlib.sha256(
        f"{REF_PROMPT_TEMPLATE_VERSION}|{generation_identity}|{object_prompt}".encode("utf-8")
    ).hexdigest()
    stale_ref = (
        existing_props is not None
        and plan.get("ref_prompt_sha256") != expected_ref_hash
    )
    if stale_ref:
        logger.warning(
            "♻️ Obje referansi bayat (prompt bilesenleri degisti); yeniden uretilecek"
        )

    missing_env = not existing_env
    missing_object = existing_props is None or stale_ref
    if not missing_env and not missing_object:
        return True
    if dry_run:
        logger.info(
            f"[dry-run] ep{number}: referanslar hazırlanacak "
            f"(ortam={missing_env}, obje={missing_object})"
        )
        return True

    if hard_cap is None:
        spent = episode_spent(bible.slug, number)
        if spent is None:
            logger.error("❌ Referans kredi kapısı: bölüm harcaması okunamadı")
            return False
        hard_cap = credit_gate.HardCreditCap(
            episode_credit_cap(bible), spent,
            durable_ledger=bool(bible.data["series"].get("durable_credit_ledger")),
        )

    if missing_env:
        env_desc = str(environment.get("desc") or environment.get("name") or env_id).strip()
        env_prompt = (
            f"Consistent room and surface reference for a vertical video series: {env_desc}. "
            "One fixed composition shows the full surface, its natural wear, the plain wall "
            "and the established daylight with realistic lived-in detail."
        )
        env_file = _refs_work_dir(
            bible.slug, "environments", output_area
        ) / f"{sanitize_filename(env_id)}.png"
        env_url = _generate_uploaded_reference(
            bible, env_prompt, env_file, hard_cap, number,
            f"environment_ref_{sanitize_filename(env_id)}",
            isolated=isolated, report_output_dir=output_area,
        )
        if not env_url:
            return False
        environment["ref_image_url"] = env_url
        atomic_write_json(
            Path(output_area) / "bible.json" if output_area is not None
            else bible_path(bible.slug),
            bible.data,
        )

    if missing_object:
        # prompt ve hash yukarida kanonik olarak hesaplandi
        object_file = (
            _refs_work_dir(bible.slug, "props", output_area)
            / f"ep{number:02d}_{sanitize_filename(ref_name)}.png"
        )
        object_url = _generate_uploaded_reference(
            bible, object_prompt, object_file, hard_cap, number, "object_ref",
            isolated=isolated, report_output_dir=output_area,
        )
        if not object_url:
            return False
        plan["prop_ref_urls"] = [object_url]
        plan["ref_prompt_sha256"] = expected_ref_hash
        atomic_write_json(plan_path, plan)
    return True


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

def _doctrine_gate(meta: SeriesMeta) -> str | None:
    """Üretim öncesi doktrin dosyasını, içeriğini ve varsa pin'ini doğrula."""
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


def _produce_episode_impl(slug: str, plan, dry_run: bool = False,
                          chain_start_url: str | None = None, *,
                          hard_cap=None,
                          output_area: str | Path | None = None,
                          experiment_id: str | None = None) -> Path | ProduceResult | None:
    """Bir bölümü üret: çekimler → indir → birleştir → (anlatım/müzik) → rapor.

    Çok-motorlu: her çekim bible.engine (veya shot['engine']) ile 'omni' VEYA ucuz
    görsel motor (seedance/veo/kling) kullanır.
    bible.chain_frames=True ise 'bitmeyen yolculuk': her çekimin son karesi sonrakinin
    başlangıç karesi olur; chain_start_url önceki BÖLÜMün son karesidir (parçalar arası).
    plan: dict veya episode_plan.json yolu.
    """
    supplied_plan_path = Path(plan) if isinstance(plan, (str, Path)) else None
    meta = SeriesMeta.load(slug)
    if not meta:
        return None
    digest = _doctrine_gate(meta)
    if digest is None:
        return None

    bible = Bible.load(slug)
    if not bible:
        return None
    series_cfg = bible.data["series"]
    if "chain_scope" in series_cfg and str(series_cfg.get("chain_scope")).strip().lower() not in (
        "series", "episode"
    ):
        logger.error("❌ bible.series.chain_scope yalnız 'series' veya 'episode' olabilir")
        return None
    if "required_layers" in series_cfg:
        raw_layers = series_cfg.get("required_layers")
        if (not isinstance(raw_layers, list)
                or any(not isinstance(layer, str) or not layer.strip() for layer in raw_layers)
                or len(set(raw_layers)) != len(raw_layers)):
            logger.error("❌ bible.series.required_layers benzersiz, boş olmayan string listesi olmalı")
            return None
    try:
        bible.audio_fade
        bible.master_lufs
    except ValueError as error:
        logger.error(f"❌ {error}")
        return None
    required_layers = set(bible.required_layers)
    unknown_layers = required_layers - {"hook_teaser", "music", "native_audio"}
    if unknown_layers:
        logger.error(
            f"❌ Bilinmeyen zorunlu teslimat katmanı: {', '.join(sorted(unknown_layers))}"
        )
        return None
    if isinstance(plan, (str, Path)):
        plan = load_plan(plan)
    plan_digest = str(plan.get("doctrine_sha256") or "").strip().lower()
    if "doctrine_sha256" in meta.data:
        if not plan_digest:
            logger.error(f"❌ HATA {slug}: pinli serinin planında doctrine_sha256 damgası yok.")
            return None
        if plan_digest != digest:
            logger.error(f"❌ HATA {slug}: plan doktrin damgası güncel doktrinle eşleşmiyor.")
            return None
    elif plan_digest and plan_digest != digest:
        logger.error(f"❌ HATA {slug}: legacy plan doktrin damgası güncel doktrinle eşleşmiyor.")
        return None

    number = plan.get("episode", {}).get("number", 1)
    default_engine = bible.engine
    chaining = bible.chain_frames
    logger.info(f"🎬 {plan_summary(plan)} (motor={default_engine}, zincir={chaining}, dry_run={dry_run})")

    cfg = meta.auto_replenish
    from .replenish import strict_plan_validation_enabled, validate_plan_against_config
    strict_plan = strict_plan_validation_enabled(cfg)
    if strict_plan:
        cfg_errors = validate_plan_against_config(plan, cfg)
        if "chain_breaks" in cfg and not bible.chain_frames:
            cfg_errors.append("chain_breaks için bible.series.chain_frames=true olmalı")
        if cfg_errors:
            for error in cfg_errors:
                logger.error(f"❌ Plan/cfg uyumsuzluğu: {error}")
            logger.error("Plan/cfg hataları nedeniyle üretim kredi harcamadan durduruldu.")
            return None

    # Doğrulama — 7-birim kota / ses yalnız OMNI çekimleri için geçerli.
    v = validate_plan(plan, bible)
    for w in v["warnings"]:
        logger.warning(f"⚠️ {w}")
    for e in v["errors"]:
        logger.error(f"❌ {e}")
    # Omni-dışı varsayılan motorda kota hataları üretimi durdurmaz (Omni'ye özgü).
    if v["errors"] and (
        plan.get("format_version") == TEK_OBJE_FORMAT
        or (default_engine == "omni" and not dry_run)
    ):
        logger.error("Plan hataları nedeniyle üretim durduruldu.")
        return None

    external_hard_cap = hard_cap is not None
    isolated = output_area is not None
    hard_cap_enabled = bool(
        cfg.get("credit_hard_cap")
        or bible.data["series"].get("credit_hard_cap")
        or cfg.get("format_version")
        or external_hard_cap
    )
    if hard_cap_enabled and not dry_run and hard_cap is None:
        cap_value = episode_credit_cap(bible)
        if cap_value <= 0:
            logger.error("❌ Kredi sert tavanı pozitif tam sayı olmalı")
            return None
        hard_cap = credit_gate.HardCreditCap(
            cap=cap_value,
            spent=episode_spent(slug, number),
            durable_ledger=bool(series_cfg.get("durable_credit_ledger")),
        )
        if hard_cap.spent is None:
            logger.error("❌ Kredi sert tavanı: mevcut bölüm harcaması okunamadı")
            return None

    # Zorunlu Suno müziği hiçbir ücretli görsel/video harcamasının gerisinde kalamaz.
    # _post_process music_reserved=True aldığında aynı rezervasyonu ikinci kez saymaz.
    music_reservation = _reserve_plan_music(
        bible, plan, hard_cap, number, isolated=isolated
    )
    if music_reservation is False:
        return None

    persistent_plan_path = supplied_plan_path or part_plan_path(slug, number)
    if not ensure_episode_refs(
        bible, plan, persistent_plan_path, hard_cap=hard_cap, dry_run=dry_run,
        output_area=output_area, isolated=isolated,
    ):
        logger.error("❌ Bölüm/ortam referansları hazırlanamadı; üretim durduruldu.")
        return None

    # Yeni URL'ler bellekteki bible/plan'a da işlendi; Omni kota dahil son sözleşmeyi
    # ücretli video çağrısından hemen önce yeniden doğrula.
    if plan.get("format_version") == TEK_OBJE_FORMAT and not dry_run:
        post_ref_validation = validate_plan(plan, bible)
        if post_ref_validation["errors"]:
            for error in post_ref_validation["errors"]:
                logger.error(f"❌ Referans sonrası plan hatası: {error}")
            return None

    sdir = _shots_work_dir(slug, number, output_area)
    sdir.mkdir(parents=True, exist_ok=True)

    # Critic-QC (opt-in, bible."series"."qc"): varsayılan bölüm tavanı çekim sayısıdır.
    # Toplam ve çekim sayısı, QC katmanının çekim başı adil payı hesaplamasını sağlar.
    qc_cfg = critic.qc_config(bible)
    qc_budget = None
    if qc_cfg and not dry_run:
        dynamic_regens = bool(
            plan.get("format_version") == TEK_OBJE_FORMAT
            or qc_cfg.get("dynamic_regens")
        )
        per_ep = qc_cfg.get("max_regens_per_episode")
        total_budget = (
            len(plan["shots"]) * int(qc_cfg["max_regens_per_shot"])
            if dynamic_regens else
            int(per_ep) if per_ep is not None else len(plan["shots"])
        )
        qc_budget = {
            "left": total_budget,
            "total": total_budget,
            "shot_count": len(plan["shots"]),
        }
        if dynamic_regens and hard_cap is not None:
            qc_budget["dynamic"] = True
            estimates = {}
            for candidate in plan["shots"]:
                candidate_engine = (candidate.get("engine") or default_engine).lower()
                estimate = cost_tracker.conservative_credit_estimate(
                    "qc_regen", candidate_engine, candidate.get("duration")
                )
                if estimate is not None:
                    estimates[int(candidate["n"])] = float(estimate)
            qc_budget["allocator"] = critic.CapAwareRegenAllocator(
                hard_cap, estimates, int(qc_cfg["max_regens_per_shot"])
            )
        logger.info(f"🔍 Critic-QC AÇIK — kare={qc_cfg['frames']}, eşik={qc_cfg['artifact_threshold']}, "
                    f"çekim regen≤{qc_cfg['max_regens_per_shot']}, "
                    f"regen modu={'dinamik-cap' if dynamic_regens else qc_budget['left']}")

    object_ref_bytes = None
    if qc_cfg and qc_cfg.get("require_object_match") and not dry_run:
        object_ref_bytes = critic.fetch_object_reference(plan)
        if object_ref_bytes is None:
            logger.error("⏸️ QC HOLD: [REFERENCE OBJECT] indirilemedi")
            return ProduceResult("qc_hold", reason="reference object could not be downloaded")

    if not dry_run:
        check_credit()  # ücretsiz okuma — başlangıç bakiyesi loglanır

    chain_url = chain_start_url if chaining else None
    last_frame_url = None
    shot_files: list[Path] = []
    shot_offsets: dict[int, float] = {}   # kanca için: çekim n → birleşik videodaki başlangıç sn
    running = 0.0
    previous_shot_dropped = False
    previous_accepted_clip: Path | None = None

    for shot_index, shot in enumerate(plan["shots"]):
        n = shot.get("n")
        out_file = sdir / f"shot_{int(n):02d}.mp4"
        shot_engine = (shot.get("engine") or default_engine).lower()
        next_shot = plan["shots"][shot_index + 1] if shot_index + 1 < len(plan["shots"]) else None
        chain_decision = decide_shot_chain(shot, next_shot, chaining, chain_url)
        if chain_decision.error:
            if previous_shot_dropped and chain_decision.require_previous:
                logger.warning(
                    f"⚠️ Çekim {n} zinciri kırıldı: önceki çekim düştüğü için son kare yok; "
                    "çekim kendi promptuyla başlangıç karesiz üretilecek"
                )
                chain_decision = ChainDecision(
                    start_url=None,
                    reset_before=True,
                    require_previous=False,
                    capture_last_frame=chain_decision.capture_last_frame,
                    explicit=chain_decision.explicit,
                )
            else:
                logger.error(f"❌ Çekim {n} zincir kapısı: {chain_decision.error}")
                return None
        chain_url = chain_decision.start_url

        # Idempotent legacy cache, or ROCK 3 media+content-hash QC revalidation.
        if not dry_run and out_file.exists() and out_file.stat().st_size > 0:
            cache_ok = True
            if qc_cfg and qc_cfg.get("revalidate_cache"):
                cache_ok = _revalidate_cached_shot(
                    slug, number, int(n), out_file, qc_cfg,
                    experiment_id=experiment_id,
                )
            if cache_ok:
                logger.info(f"⏭️ Çekim {n} doğrulanmış cache'de: {out_file.name}")
                if qc_cfg and qc_cfg.get("scene_cut_scan"):
                    if experiment_id is not None:
                        critic.log_scene_cut_scan(
                            slug, number, int(n), out_file,
                            experiment_id=experiment_id,
                        )
                    else:
                        critic.log_scene_cut_scan(slug, number, int(n), out_file)
                prep = _prep_shot_clip(bible, plan, shot, out_file)
                shot_offsets[int(n)] = running
                running += ffmpeg_tools.get_video_duration(prep)
                shot_files.append(prep)
                previous_accepted_clip = out_file
                if qc_budget and qc_budget.get("allocator"):
                    qc_budget["allocator"].mark_main_authorized(int(n))
                    qc_budget["allocator"].mark_complete(int(n))
                if chain_decision.capture_last_frame:
                    lf = ffmpeg_tools.extract_last_frame(out_file)
                    if lf:
                        up = upload_to_imgbb(lf)
                        if up:
                            chain_url = up
                            last_frame_url = up
                previous_shot_dropped = False
                continue

        # ── OMNI çekimi (karakter + ses tutarlılığı) ──────────────────────────
        if shot_engine == "omni":
            res = resolve_shot(bible, shot, plan)
            kwargs = res["kwargs"]
            # Bitmeyen yolculuk: önceki çekimin/bölümün son karesini referans olarak ekle
            if chain_decision.start_url:
                kwargs["image_urls"] = [chain_url] + list(kwargs.get("image_urls") or [])
            if strict_plan:
                units_ok, final_units = validate_ref_units(
                    kwargs.get("image_urls"), kwargs.get("character_ids")
                )
                if not units_ok:
                    logger.error(
                        f"❌ Çekim {n}: zincir karesi sonrası 7-birim kotası aşıldı "
                        f"({final_units} birim); üretim kredi harcamadan durduruldu"
                    )
                    return None
            char_names = [bible.get_character(c).get("name", c)
                          for c in shot.get("characters", []) if bible.get_character(c)]
            if qc_cfg:
                # HAM çekim promptu — art_style'ın genel 'clothing' metni denetimi köreltmesin
                for w in critic.lint_prompt(bible, shot, shot.get("prompt") or ""):
                    logger.warning(f"🧹 QC-lint çekim {n}: {w}")
            if dry_run:
                payload = build_omni_payload(**kwargs)
                logger.info(f"[dry-run] Çekim {n} OMNI ({res['units']} birim):\n"
                            f"{json.dumps(payload, ensure_ascii=False, indent=2)[:700]}")
                if chain_decision.capture_last_frame:
                    chain_url = f"dry-run://shot/{n}/last-frame"
                continue
            result = _gen_omni_with_fallback(
                kwargs,
                before_call=(
                    None if hard_cap is None else
                    lambda _duration=kwargs["duration"]: hard_cap.authorize(
                        "main_shot", "omni", _duration
                    )
                ),
            )
            if qc_budget and qc_budget.get("allocator"):
                qc_budget["allocator"].mark_main_authorized(int(n))
            if hard_cap is not None and hard_cap.blocked:
                return None
            credits, status, video_url = None, "FAIL", ""
            if result and result.get("url"):
                video_url = result["url"]
                credits = result.get("credits")
                if (credits is not None and hard_cap is not None
                        and (external_hard_cap
                             or series_cfg.get("durable_credit_ledger"))):
                    hard_cap.settle_last(credits)
                if credits is not None:
                    if not _record_episode_cost(
                        bible, number, f"omni_ep{number}_shot{n}",
                        "gemini-omni-video", credits, isolated=isolated,
                    ):
                        return None
                elif hard_cap is not None and hard_cap.last_estimate is not None:
                    if not _record_episode_cost(
                        bible, number, f"omni_estimate_ep{number}_shot{n}",
                        "gemini-omni-video", hard_cap.last_estimate,
                        isolated=isolated,
                    ):
                        return None
                if hard_cap is not None and hard_cap.blocked:
                    return None
                download_kwargs = {"hardened": True} if qc_cfg and qc_cfg.get("harden_downloads") else {}
                if download_file(video_url, out_file, **download_kwargs):
                    status = "ok"
            # Critic-QC (opt-in): bozuk klip kurguya giremez — REDde fix_notes'lu
            # prompt + taze seed ile otomatik regen; eşiği geçemeyen çekim düşer.
            if status == "ok" and qc_budget is not None:
                def _regen_omni(fixed_prompt, _kw=kwargs):
                    if hard_cap is None and not _qc_regen_allowed(slug, number):
                        return None
                    kw = dict(_kw)
                    kw["prompt"] = fixed_prompt
                    kw["seed"] = None   # None → generate_omni_shot taze seed üretir

                    def _authorize_regen(_duration=kw["duration"]):
                        allowed = hard_cap.authorize(
                            "qc_regen", "omni", _duration, optional=True
                        )
                        if not allowed:
                            qc_budget["left"] = 0
                        return allowed

                    regen_result = _gen_omni_with_fallback(
                        kw,
                        before_call=(
                            None if hard_cap is None else
                            _authorize_regen
                        ),
                    )
                    if (regen_result and regen_result.get("credits") is not None
                            and hard_cap is not None
                            and (external_hard_cap
                                 or series_cfg.get("durable_credit_ledger"))):
                        hard_cap.settle_last(regen_result["credits"])
                    if (regen_result and regen_result.get("credits") is None
                            and hard_cap is not None and hard_cap.last_estimate is not None):
                        regen_result = {**regen_result, "credits": hard_cap.last_estimate}
                    return regen_result
                qc_context = {}
                if qc_cfg.get("require_object_match"):
                    qc_context["object_ref"] = object_ref_bytes
                if qc_cfg.get("require_continuity") and 2 <= int(n) <= 4:
                    qc_context["previous_clip"] = previous_accepted_clip
                # ROCK B: anomali imzasi plandan, ihlal gozlemi cekimden, tasinan iz
                # ONCEKI cekimden gelir (iz yalnız bir sonraki cekime karsi olculur).
                rb_card = (plan.get("object_card") or {}) if isinstance(plan, dict) else {}
                rb_anomaly = rb_card.get("anomaly_descriptor")
                if rb_anomaly:
                    qc_context["anomaly_descriptor"] = rb_anomaly
                rb_prev = None
                if isinstance(plan, dict) and int(n) >= 2:
                    for candidate in (plan.get("shots") or []):
                        if isinstance(candidate, dict) and int(candidate.get("n") or 0) == int(n) - 1:
                            rb_prev = candidate.get("state_carry")
                if rb_prev:
                    qc_context["state_carry_expected"] = rb_prev
                if experiment_id is not None:
                    qc_context["experiment_id"] = experiment_id
                qc_path, qc_credits, qc_status = critic.qc_shot(
                    bible, shot, out_file, kwargs["prompt"],
                    _regen_omni, episode=number, budget=qc_budget,
                    **qc_context,
                )
                if qc_credits:
                    if not _record_episode_cost(
                        bible, number, f"qc_regen_ep{number}_shot{n}",
                        "gemini-omni-video", qc_credits, isolated=isolated,
                    ):
                        return None
                    credits = (credits or 0) + qc_credits
                if qc_path is None:
                    if qc_status == "hold":
                        return ProduceResult(
                            "qc_hold", reason=qc_budget.get("hold_reason")
                            or f"mandatory QC unavailable for shot {n}"
                        )
                    status = "qc_skip" if qc_status == "skip" else "qc_fail"
                    if bible.require_all_shots:
                        return None
                if hard_cap is not None and hard_cap.blocked:
                    return None
            if status == "ok":
                if qc_cfg and qc_cfg.get("scene_cut_scan"):
                    if experiment_id is not None:
                        critic.log_scene_cut_scan(
                            slug, number, int(n), out_file,
                            experiment_id=experiment_id,
                        )
                    else:
                        critic.log_scene_cut_scan(slug, number, int(n), out_file)
                prep = _prep_shot_clip(bible, plan, shot, out_file)
                shot_offsets[int(n)] = running
                running += ffmpeg_tools.get_video_duration(prep)
                shot_files.append(prep)
                previous_accepted_clip = out_file
            report.append_row(slug, report.make_row(
                episode=number, shot_n=n, characters=char_names,
                audio_ids=kwargs["audio_ids"], duration=kwargs["duration"],
                resolution=kwargs["resolution"], seed=kwargs["seed"],
                credits=credits, status=status, video_url=video_url, local_file=out_file,
            ), output_dir=output_area)
            if chain_decision.capture_last_frame and status == "ok":
                lf = ffmpeg_tools.extract_last_frame(out_file)
                if lf:
                    up = upload_to_imgbb(lf)
                    if up:
                        chain_url = up
                        last_frame_url = up
            previous_shot_dropped = status != "ok"
            if previous_shot_dropped:
                chain_url = None
            continue

        # ── Ucuz görsel motor (seedance / veo / kling) ────────────────────────
        rv = resolve_visual_shot(bible, shot, chain_url=chain_decision.start_url)
        if qc_cfg:
            # HAM çekim promptu — art_style'ın genel 'clothing' metni denetimi köreltmesin
            for w in critic.lint_prompt(bible, shot, shot.get("prompt") or ""):
                logger.warning(f"🧹 QC-lint çekim {n}: {w}")
        if dry_run:
            src = "zincir" if chain_url else ("ortam/figür" if rv["start_image_url"] else "yok")
            logger.info(f"[dry-run] Çekim {n} {shot_engine.upper()} | başlangıç={src} | "
                        f"{rv['duration']}s | {rv['prompt'][:140]}...")
            if chain_decision.capture_last_frame:
                chain_url = f"dry-run://shot/{n}/last-frame"
            continue
        reserved_estimate = None
        if hard_cap is not None:
            if not hard_cap.authorize("main_shot", shot_engine, rv["duration"]):
                return None
            reserved_estimate = hard_cap.last_estimate
        if qc_budget and qc_budget.get("allocator"):
            qc_budget["allocator"].mark_main_authorized(int(n))
        result = _generate_visual_clip(shot_engine, rv["prompt"], rv["start_image_url"],
                                       rv["duration"], bible.aspect_ratio, bible.resolution,
                                       sound=bible.native_audio)
        credits, status, video_url = None, "FAIL", ""
        if result and result.get("url"):
            video_url = result["url"]
            credits = result.get("credits")
            if (credits is not None and hard_cap is not None
                    and (external_hard_cap
                         or series_cfg.get("durable_credit_ledger"))):
                hard_cap.settle_last(credits)
            if credits is not None:
                if not _record_episode_cost(
                    bible, number, f"{shot_engine}_ep{number}_shot{n}",
                    shot_engine, credits, isolated=isolated,
                ):
                    return None
            elif reserved_estimate is not None:
                if not _record_episode_cost(
                    bible, number, f"{shot_engine}_estimate_ep{number}_shot{n}",
                    shot_engine, reserved_estimate, isolated=isolated,
                ):
                    return None
            if hard_cap is not None and hard_cap.blocked:
                return None
            download_kwargs = {"hardened": True} if qc_cfg and qc_cfg.get("harden_downloads") else {}
            if download_file(video_url, out_file, **download_kwargs):
                status = "ok"
        # Critic-QC (opt-in): ucuz motorlarda seed parametresi yok — düzeltilmiş
        # prompt + modelin doğal varyasyonu regen'i çeşitlendirir.
        if status == "ok" and qc_budget is not None:
            def _regen_visual(fixed_prompt, _rv=rv, _eng=shot_engine):
                if hard_cap is None and not _qc_regen_allowed(slug, number):
                    return None
                if hard_cap is not None and not hard_cap.authorize(
                    "qc_regen", _eng, _rv["duration"], optional=True
                ):
                    qc_budget["left"] = 0
                    return None
                regen_result = _generate_visual_clip(
                    _eng, fixed_prompt, _rv["start_image_url"], _rv["duration"],
                    bible.aspect_ratio, bible.resolution, sound=bible.native_audio,
                )
                if (regen_result and regen_result.get("credits") is not None
                        and hard_cap is not None
                        and (external_hard_cap
                             or series_cfg.get("durable_credit_ledger"))):
                    hard_cap.settle_last(regen_result["credits"])
                if (regen_result and regen_result.get("credits") is None
                        and hard_cap is not None and hard_cap.last_estimate is not None):
                    regen_result = {**regen_result, "credits": hard_cap.last_estimate}
                return regen_result
            qc_context = {}
            if qc_cfg.get("require_object_match"):
                qc_context["object_ref"] = object_ref_bytes
            if qc_cfg.get("require_continuity") and 2 <= int(n) <= 4:
                qc_context["previous_clip"] = previous_accepted_clip
            # ROCK B: anomali imzasi plandan, ihlal gozlemi cekimden, tasinan iz
            # ONCEKI cekimden gelir (iz yalnız bir sonraki cekime karsi olculur).
            rb_card = (plan.get("object_card") or {}) if isinstance(plan, dict) else {}
            rb_anomaly = rb_card.get("anomaly_descriptor")
            if rb_anomaly:
                qc_context["anomaly_descriptor"] = rb_anomaly
            rb_prev = None
            if isinstance(plan, dict) and int(n) >= 2:
                for candidate in (plan.get("shots") or []):
                    if isinstance(candidate, dict) and int(candidate.get("n") or 0) == int(n) - 1:
                        rb_prev = candidate.get("state_carry")
            if rb_prev:
                qc_context["state_carry_expected"] = rb_prev
            if experiment_id is not None:
                qc_context["experiment_id"] = experiment_id
            qc_path, qc_credits, qc_status = critic.qc_shot(
                bible, shot, out_file, rv["prompt"],
                _regen_visual, episode=number, budget=qc_budget,
                **qc_context,
            )
            if qc_credits:
                if not _record_episode_cost(
                    bible, number, f"qc_regen_ep{number}_shot{n}",
                    shot_engine, qc_credits, isolated=isolated,
                ):
                    return None
                credits = (credits or 0) + qc_credits
            if qc_path is None:
                if qc_status == "hold":
                    return ProduceResult(
                        "qc_hold", reason=qc_budget.get("hold_reason")
                        or f"mandatory QC unavailable for shot {n}"
                    )
                status = "qc_skip" if qc_status == "skip" else "qc_fail"
                if bible.require_all_shots:
                    return None
            if hard_cap is not None and hard_cap.blocked:
                return None
        if status == "ok":
            if qc_cfg and qc_cfg.get("scene_cut_scan"):
                if experiment_id is not None:
                    critic.log_scene_cut_scan(
                        slug, number, int(n), out_file,
                        experiment_id=experiment_id,
                    )
                else:
                    critic.log_scene_cut_scan(slug, number, int(n), out_file)
            prep = _prep_shot_clip(bible, plan, shot, out_file)
            shot_offsets[int(n)] = running
            running += ffmpeg_tools.get_video_duration(prep)
            shot_files.append(prep)
            previous_accepted_clip = out_file
        report.append_row(slug, report.make_row(
            episode=number, shot_n=n, characters=[], audio_ids=[],
            duration=rv["duration"], resolution="720p", seed=None,
            credits=credits, status=status, video_url=video_url, local_file=out_file,
        ), output_dir=output_area)
        if chain_decision.capture_last_frame and status == "ok":
            lf = ffmpeg_tools.extract_last_frame(out_file)
            if lf:
                up = upload_to_imgbb(lf)
                if up:
                    chain_url = up
                    last_frame_url = up
        previous_shot_dropped = status != "ok"
        if previous_shot_dropped:
            chain_url = None

    if dry_run:
        logger.info("[dry-run] Simülasyon bitti — dosya/kredi harcanmadı.")
        return None

    if bible.require_all_shots and len(shot_files) != len(plan["shots"]):
        logger.error(
            f"❌ require_all_shots kapısı: {len(shot_files)}/{len(plan['shots'])} çekim hazır; "
            "bölüm birleştirilmeyecek/yayınlanmayacak"
        )
        return None

    if not shot_files:
        logger.error("❌ Hiç çekim üretilemedi, bölüm oluşturulamadı.")
        return None

    # Birleştir → final export (9:16 dikey)
    work_dir = _episode_work_dir(slug, number, output_area)
    raw_ep = work_dir / f"ep{int(number):02d}_raw.mp4"
    merged = False
    xf = bible.transitions
    if xf and len(shot_files) >= 2:
        # Sinematik crossfade (opt-in, the__footnote formatı): sahneler birbirinin
        # içinde erir. Ses birleştirmede atılır — müzik post'ta TEK ses olur
        # (replace_original), o yüzden yalnız anlatımsız müzikli serilerde açılmalı.
        fade = max(0.2, min(1.5, float(xf.get("duration", 0.6))))
        try:
            ffmpeg_tools.concatenate_video_crossfade(shot_files, raw_ep, fade=fade)
            # Her geçiş 'fade' sn örtüşür → k'inci klip k·fade erken başlar.
            # Kanca/fact-caption zamanlamaları şaşmasın diye ofsetler hizalanır.
            for i, sn in enumerate(sorted(shot_offsets, key=shot_offsets.get)):
                shot_offsets[sn] = max(0.0, shot_offsets[sn] - i * fade)
            merged = True
        except Exception as e:
            logger.warning(f"⚠️ Crossfade birleştirme başarısız ({e}) — düz kesmeye dönülüyor")
    if not merged:
        if bible.audio_smooth:
            # Atmosfer/müzik kanalları: çekim sınırlarında sesi yumuşat (pop/boşluk gider).
            ffmpeg_tools.concatenate_audio_smooth(
                shot_files, raw_ep, clips_dir=sdir, fade=bible.audio_fade
            )
        else:
            # Diyalog kanalları: düz birleştir (söz baş/sonu kırpılmasın).
            ffmpeg_tools.concatenate_simple(shot_files, raw_ep, clips_dir=sdir)
    final_ep = work_dir / f"ep{int(number):02d}.mp4"
    ffmpeg_tools.final_export(raw_ep, final_ep)

    # Anlatım (narration) + arka plan müziği (best-effort)
    final_ep = _post_process(
        bible, plan, final_ep, hard_cap=hard_cap,
        required_music="music" in required_layers,
        music_reserved=music_reservation is True,
        output_area=output_area, isolated=isolated,
    )
    if final_ep is None:
        return None

    # Açılış kancası (opt-in): doruk çekimden kısa bir kesit videonun EN BAŞINA
    # eklenir — ilk 1-2 saniyede 'olağandışı an' görünmezse Shorts'ta kaydırılır.
    # Müzik/anlatımdan SONRA yapılır ki kesit sesiyle birlikte gelsin.
    teaser_len = 0.0   # kanca kesiti eklenirse tüm gövde bu kadar kayar (fact-caption sync'i için)
    teaser_ok = False
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
            teaser = work_dir / "hook_teaser.mp4"
            ffmpeg_tools.extract_clip(final_ep, teaser, start, d)
            hooked = Path(final_ep).parent / f"{Path(final_ep).stem}_hooked.mp4"
            ffmpeg_tools.concatenate_simple([teaser, Path(final_ep)], hooked,
                                            clips_dir=Path(final_ep).parent)
            if hooked.exists() and hooked.stat().st_size > 0:
                final_ep = hooked
                teaser_ok = True
                teaser_len = ffmpeg_tools.get_video_duration(teaser) or d
                logger.info(f"🎣 Kanca: çekim {hn} dorukundan {d:.1f}s (t={start:.1f}s) başa eklendi")
        except Exception as e:
            logger.warning(f"⚠️ Kanca eklenemedi (video kancasız yayınlanır): {e}")

    if "hook_teaser" in required_layers and not teaser_ok:
        logger.error("❌ Zorunlu teslimat katmanı üretilemedi: hook_teaser")
        return None

    # Açılış künyesi (opt-in): plan'daki eser adı + bölge/yıl videonun İLK
    # saniyelerine yazılır. Kancadan SONRA uygulanır ki künye, başa eklenen
    # doruk-kesitinin üzerine binsin (izleyici ilk karede NE ve NEREDE okur);
    # upscale'den ÖNCE uygulanır ki 4K master da IG/TikTok delivery kopyası da
    # yazıyı taşısın.
    tc_cfg = bible.title_card
    tc = plan.get("title_card") or {}
    # Next Stop kancasi: durak adi ZATEN bolum basliginda ve title_patterns ile
    # garanti altinda ("Next Stop: <DURAK> <emoji>"). Bu yuzden kunye plandan
    # degil BASLIKTAN turetilebilir: Gemini'ye fazladan alan sordurmuyoruz, yil
    # zorunlulugu olan title_card dogrulamasina takilmiyoruz ve kuyrukta HAZIR
    # bekleyen planlar da kunyeyi kendiliginden kazaniyor. Opt-in:
    # bible.series.title_card = {"enabled": true, "from_episode_title": true}
    if tc_cfg and tc_cfg.get("from_episode_title") and not (tc.get("title") or tc.get("subtitle")):
        ep_title = str((plan.get("episode") or {}).get("title") or "").strip()
        if ep_title:
            # sondaki emoji/sembolleri at, "Next Stop:" onekini koru, tek satir yap
            dest = re.sub(r"^\s*next\s*stop\s*:\s*", "", ep_title, flags=re.IGNORECASE)
            dest = "".join(c for c in dest if c.isalnum() or c in " '-,.&").strip()
            if dest:
                tc = {"title": f"NEXT STOP: {dest}", "subtitle": ""}
                logger.info(f"🪷 Kunye bolum basligindan turetildi: {tc['title']}")
    if tc_cfg and (tc.get("title") or tc.get("subtitle")):
        try:
            titled = Path(final_ep).parent / f"{Path(final_ep).stem}_titled.mp4"
            ffmpeg_tools.title_card_overlay(
                final_ep, titled,
                title=str(tc.get("title") or ""),
                subtitle=str(tc.get("subtitle") or ""),
                duration=float(tc_cfg.get("duration", 3.0)),
            )
            if titled.exists() and titled.stat().st_size > 0:
                final_ep = titled
                logger.info(f"🪧 Künye bindirildi: {tc.get('title') or tc.get('subtitle')}")
        except Exception as e:
            logger.warning(f"⚠️ Künye eklenemedi (video künyesiz yayınlanır): {e}")

    # Senkron fact-caption'lar (opt-in): her çekimin shot['fact']'i (kısa sert bilgi)
    # o çekimin FINAL zaman çizgisindeki anına — kanca kaymasi (teaser_len) dahil —
    # alt üçlüğe yazılır (üst=künye / alt=fact, çakışmaz). Künyeden SONRA, upscale'den
    # ÖNCE uygulanır ki 4K master da IG/TikTok kopyası da yazıyı taşısın. shot['fact']
    # olmayan planlar (eski/anlatımsız) hiç etkilenmez.
    fc_cfg = bible.fact_captions
    facts = [(int(s["n"]), str(s.get("fact") or "").strip())
             for s in plan.get("shots", []) if str(s.get("fact") or "").strip()]
    if fc_cfg and facts and shot_offsets:
        try:
            total = ffmpeg_tools.get_video_duration(final_ep)
            tc_hold = float(tc_cfg.get("duration", 3.0)) if tc_cfg else 0.0
            hold = float(fc_cfg.get("hold", 2.6))
            items, last_at = [], -1e9
            for n, text in facts:
                if n not in shot_offsets:
                    continue
                at = shot_offsets[n] + teaser_len + 0.7        # çekime biraz girince belir
                at = max(at, tc_hold + 0.4)                    # açılış künyesiyle yarışma
                at = min(at, max(0.0, total - hold - 0.3))     # sondan taşma
                if at - last_at < hold + 0.3:                  # üst üste binmesin
                    continue
                items.append({"text": text, "at": at, "hold": hold})
                last_at = at
            if items:
                capped = Path(final_ep).parent / f"{Path(final_ep).stem}_capped.mp4"
                ffmpeg_tools.fact_captions_overlay(final_ep, capped, items, hold=hold)
                if capped.exists() and capped.stat().st_size > 0:
                    final_ep = capped
                    logger.info(f"💬 {len(items)} fact-caption bindirildi")
        except Exception as e:
            logger.warning(f"⚠️ Fact-caption'lar eklenemedi (video onlarsız yayınlanır): {e}")

    # 4K master (opt-in): en-son final Topaz ile ×2 büyütülür (YouTube 4K);
    # IG/TikTok için 1080p delivery kopyası yanına bırakılır. Ses master alanı
    # yoksa aşağıdaki legacy çağrı sırası ve dosya yolu birebir korunur.
    master_lufs = bible.master_lufs
    if master_lufs is None:
        if isolated:
            final_ep = _upscale_master(
                bible, number, Path(final_ep), hard_cap=hard_cap, isolated=True
            )
        else:
            final_ep = _upscale_master(bible, number, Path(final_ep))
    else:
        source_1080 = Path(final_ep)
        mastered_1080 = source_1080.parent / f"{source_1080.stem}_mastered.mp4"
        try:
            ffmpeg_tools.master_audio(
                source_1080, mastered_1080,
                target_i=master_lufs, target_tp=-1.0, target_lra=11.0,
            )
        except Exception as error:
            return _audio_master_hold(f"mastering başarısız: {error}")

        if bible.upscale:
            if isolated:
                upscaled = _upscale_master(
                    bible, number, mastered_1080, hard_cap=hard_cap, isolated=True
                )
            else:
                upscaled = _upscale_master(bible, number, mastered_1080)
            upscaled = Path(upscaled)
            delivery_1080 = mastered_1080.parent / "delivery_1080.mp4"
            try:
                # Önceki koşudan kalan delivery kopyası mastering'i atlayamaz.
                shutil.copy2(mastered_1080, delivery_1080)
                if upscaled.resolve() == mastered_1080.resolve():
                    return _audio_master_hold("4K master üretilemedi")
                ffmpeg_tools.remux_audio(upscaled, mastered_1080, upscaled)
            except Exception as error:
                return _audio_master_hold(f"4K master ses remux başarısız: {error}")
            if not _verify_audio_master(delivery_1080, master_lufs):
                return _audio_master_hold("delivery_1080 ses doğrulaması başarısız")
            if not _verify_audio_master(upscaled, master_lufs):
                return _audio_master_hold("4K master ses doğrulaması başarısız")
            final_ep = upscaled
        else:
            if not _verify_audio_master(mastered_1080, master_lufs):
                return _audio_master_hold("final ses doğrulaması başarısız")
            final_ep = mastered_1080

    if "native_audio" in required_layers:
        try:
            native_audio_ok = _verify_native_audio_delivery(
                bible, number, final_ep, experiment_id=experiment_id
            )
        except critic.QCApiExhausted as error:
            critic.notify_qc_exhaustion(bible.title, number, error.reason)
            critic._log_event(slug, {
                "event": "qc_hold", "episode": number, "shot": None,
                "reason": error.reason,
                "reasons": [f"QC API deneme politikası tükendi ({error.reason})"],
                "clip": Path(final_ep).name,
            }, experiment_id=experiment_id)
            return ProduceResult("qc_hold", reason=error.reason)
        if not native_audio_ok:
            return None

    # Parçalar arası zincir: bölümün son karesini sonraki bölüm için sakla (sidecar).
    # chain_scope="episode" ise bölümler arası taşıma YOK — sidecar yazılmaz.
    if chaining and bible.chain_scope == "series":
        if not last_frame_url:
            lf = ffmpeg_tools.extract_last_frame(final_ep)
            if lf:
                last_frame_url = upload_to_imgbb(lf)
        if last_frame_url:
            (work_dir / "last_frame.txt").write_text(last_frame_url, encoding="utf-8")
            logger.info("🔗 Son kare bir sonraki bölüm için saklandı (bitmeyen yolculuk).")

    report.export_xlsx(slug, output_dir=output_area)
    summary = report.summarize(slug, output_dir=output_area)
    logger.info(f"🎉 Bölüm hazır: {final_ep}")
    logger.info(f"   📊 {summary['başarılı']}/{summary['çekim_sayısı']} çekim, "
                f"{summary['toplam_kredi']} kredi (~${summary['toplam_dolar']})")
    return final_ep


def produce_episode(slug: str, plan, dry_run: bool = False,
                    chain_start_url: str | None = None, *,
                    typed_result: bool = False,
                    hard_cap=None,
                    output_area: str | Path | None = None,
                    experiment_id: str | None = None) -> Path | ProduceResult | None:
    """Produce an episode, with an opt-in typed adapter for scheduler callers.

    Direct/legacy callers still receive ``Path | None``.  The runner requests the
    typed result so a QC hold remains distinct from a generation failure.
    """
    raw = _produce_episode_impl(
        slug, plan, dry_run=dry_run, chain_start_url=chain_start_url,
        hard_cap=hard_cap, output_area=output_area,
        experiment_id=experiment_id,
    )
    if isinstance(raw, ProduceResult):
        result = raw
    elif raw is None:
        result = ProduceResult("generation_fail")
    else:
        result = ProduceResult("ok", Path(raw))
    return result if typed_result else result.path
