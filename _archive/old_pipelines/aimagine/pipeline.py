"""
AImagine — DIY Crafts Fixed-Camera Pipeline

Creates 24-second viral DIY transformation videos.
Inspired by @diycraftstvofficial (5.2M IG, 319K YT).
Pipeline: concept selection → 4 frames (chained) → 3 video clips → merge → publish.

Format: 9:16 vertical, fixed tripod camera, 1-2 workers, satisfying transformation.
"""

import time
from datetime import date
from pathlib import Path

from core.config import CHANNEL_DIRS, CHANNEL_DURATION, CHANNEL_VEO_MODEL, PIPELINE_TIMEOUT_MINUTES, logger
from core.kie_api import generate_image, generate_video, generate_veo_video, check_credit, ServerError
from core.imgbb import upload_to_imgbb
from core.ffmpeg_tools import (
    check_ffmpeg, concatenate_simple, concatenate_crossfade, final_export,
    get_video_duration, trim_to_duration, prepend_teaser
)
from core.uploader import publish_video
from core.utils import download_file, sanitize_filename
from core.video_vault import vault

from .timelapse_concepts import get_daily_concept, TIMELAPSE_CONCEPTS


CHANNEL = "aimagine"


def run_pipeline(concept_name: str = None, dry_run: bool = False, skip_upload: bool = False) -> dict | None:
    """Run the AImagine construction timelapse pipeline.

    Flow:
        1. Select concept (20+ viral themes)
        2. Generate 4 frames with chained image references for consistency
        3. Generate 3 video clips (frame pairs) with construction timelapse prompts
        4. Crossfade merge → single seamless timelapse
        5. Publish to YouTube/Instagram/TikTok
    """
    today = date.today().isoformat()
    start_time = time.time()
    dirs = CHANNEL_DIRS[CHANNEL]
    duration_cfg = CHANNEL_DURATION[CHANNEL]

    logger.info("\n" + "=" * 60)
    logger.info(f"🏗️ AIMAGINE — DIY Crafts Pipeline — {today}")
    logger.info("=" * 60)

    credit = check_credit()

    # ── 1. Select concept ─────────────────────────────────────────────────
    if concept_name:
        concept = next(
            (c for c in TIMELAPSE_CONCEPTS if c["name"].lower() == concept_name.lower()),
            None
        )
        if not concept:
            logger.error(f"Concept not found: {concept_name}")
            return None
    else:
        concept = get_daily_concept()

    logger.info(f"📋 Concept: {concept['name']}")
    logger.info(f"   Hook: {concept['hook']}")

    title = concept.get("title", f"🏗️ {concept['name']}")
    description = concept.get("description", f"Incredible DIY transformation: {concept['name']}")
    hashtags = concept.get("hashtags", "#shorts #diy #transformation #satisfying #crafts")

    # Trending hook — boost title with daily trending keywords
    from core.trending import enhance_title_with_trend, get_trending_hashtags
    title = enhance_title_with_trend(title, CHANNEL)
    trending_tags = get_trending_hashtags(CHANNEL)
    if trending_tags:
        hashtags = f"{hashtags} {trending_tags}"

    if dry_run:
        logger.info("🏃 DRY RUN — Skipping generation.")
        return {"date": today, "concept": concept["name"], "title": title, "dry_run": True}

    project_name = sanitize_filename(concept["name"])
    frame_prompts = concept["frame_prompts"]
    video_prompts = concept["video_prompts"]

    # Note: Frame and video prompts from concepts are used as-is.
    # Each concept has its own coherent visual story (exterior → interior reveal).

    # ── 3. Generate 4 frames with chained references ──────────────────────
    logger.info(f"\n🖼️ GENERATING {len(frame_prompts)} DIY FRAMES...")
    frames = []
    previous_url = None

    for i, prompt in enumerate(frame_prompts):
        # Pipeline timeout check
        elapsed_min = (time.time() - start_time) / 60
        if elapsed_min > PIPELINE_TIMEOUT_MINUTES * 0.5:
            logger.warning(f"⏰ Pipeline timeout ({elapsed_min:.0f}min), stopping frames")
            break

        stage_names = ["Before/Empty", "Early Progress", "Major Progress", "Finished Result"]
        stage = stage_names[i] if i < len(stage_names) else f"Stage {i+1}"
        logger.info(f"  Frame {i+1}/{len(frame_prompts)}: {stage}...")

        # Chain reference: each frame uses the previous as reference
        # This ensures consistent camera angle, surroundings, and lighting
        url = generate_image(
            prompt=prompt,
            reference_url=previous_url,
        )

        if url:
            save_path = dirs["frames"] / f"{project_name}_frame_{i:02d}.png"
            local = download_file(url, save_path)
            if local:
                frames.append({
                    "url": url,
                    "local_path": local,
                    "frame_number": i,
                    "stage": stage,
                })
                # Upload to imgbb for next frame's reference
                imgbb_url = upload_to_imgbb(local)
                previous_url = imgbb_url or url
                logger.info(f"  ✅ Frame {i+1} ready: {stage}")
        else:
            logger.warning(f"⚠️ Frame {i+1} ({stage}) failed!")

    if len(frames) < 2:
        logger.error("❌ Not enough frames generated!")
        return None

    # ── 3. Generate 3 video clips (frame pairs) ──────────────────────────
    actual_clips_needed = len(frames) - 1
    logger.info(f"\n🎬 GENERATING {actual_clips_needed} DIY VIDEO CLIPS...")
    clips = []

    for i in range(actual_clips_needed):
        # Pipeline timeout check
        elapsed_min = (time.time() - start_time) / 60
        if elapsed_min > PIPELINE_TIMEOUT_MINUTES * 0.75:
            logger.warning(f"⏰ Pipeline timeout ({elapsed_min:.0f}min), stopping clips")
            break

        start_frame = frames[i]
        end_frame = frames[i + 1]
        vp = video_prompts[i] if i < len(video_prompts) else "Fixed tripod camera, DIY transformation timelapse, satisfying progress. 8 seconds."

        logger.info(f"  Clip {i+1}: {start_frame['stage']} → {end_frame['stage']}")

        video_url = None

        # VEO3 Lite primary (30 credits vs Kling 112)
        veo_model = CHANNEL_VEO_MODEL.get(CHANNEL)
        if veo_model:
            video_url = generate_veo_video(
                prompt=vp,
                image_url=start_frame["url"],
                duration="10",
                model=veo_model,
            )

        # Kling fallback if VEO3 fails
        if not video_url:
            if veo_model:
                logger.warning(f"⚠️ VEO3 Clip {i+1} failed, trying Kling fallback...")
            try:
                video_url = generate_video(
                    prompt=vp,
                    start_image_url=start_frame["url"],
                    duration="10",
                    sound=True,
                )
            except ServerError as e:
                logger.warning(f"⚠️ Kling server error: {e} — trying shorter prompt")
                try:
                    video_url = generate_video(
                        prompt=vp[:100],
                        start_image_url=start_frame["url"],
                        duration="10",
                        sound=True,
                    )
                except Exception:
                    video_url = None
            except Exception as e:
                logger.warning(f"⚠️ Kling error: {e}")
                video_url = None

        if video_url:
            save_path = dirs["clips"] / f"{project_name}_clip_{i+1:02d}.mp4"
            local = download_file(video_url, save_path)
            if local:
                clips.append({
                    "url": video_url,
                    "local_path": local,
                    "clip_number": i + 1,
                    "transition": f"{start_frame['stage']} → {end_frame['stage']}",
                })
                logger.info(f"  ✅ Clip {i+1} ready")
        else:
            logger.warning(f"⚠️ Clip {i+1} failed!")

    if not clips:
        logger.error("❌ No video clips generated!")
        # ── VAULT FALLBACK: Reuse a previously generated video ──────────
        vault_video = vault.get_unpublished(CHANNEL)
        if vault_video:
            logger.info(f"📦 VAULT FALLBACK: Reusing '{vault_video['title'][:50]}'")
            fallback_path = None
            if vault_video.get("video_path") and Path(vault_video["video_path"]).exists():
                fallback_path = Path(vault_video["video_path"])
            elif vault_video.get("video_url"):
                fb_name = sanitize_filename(vault_video["title"])
                fallback_path = dirs["final"] / f"vault_{fb_name}.mp4"
                fallback_path = download_file(vault_video["video_url"], fallback_path)

            if fallback_path and Path(fallback_path).exists():
                vault.increment_attempt(CHANNEL, vault_video["title"])
                if not skip_upload:
                    logger.info("📤 PUBLISHING VAULT VIDEO...")
                    v_desc = vault_video.get("description", description)
                    results = publish_video(
                        video_path=Path(fallback_path),
                        title=vault_video["title"],
                        description=v_desc,
                        channel_name=CHANNEL,
                    )
                    if any(v for v in results.values() if v):
                        vault.mark_published(CHANNEL, vault_video["title"])
                        logger.info("✅ Vault video published successfully!")
                    else:
                        logger.warning("⚠️ Vault video publish failed")

                return {
                    "date": today, "channel": CHANNEL,
                    "title": vault_video["title"],
                    "vault_fallback": True,
                    "duration_min": round((time.time() - start_time) / 60, 1),
                }
        return None

    # ── 4. FFmpeg crossfade merge ─────────────────────────────────────────
    logger.info("\n🔗 MERGING CLIPS WITH CROSSFADE...")
    if not check_ffmpeg():
        return None

    clip_files = [c["local_path"] for c in clips]
    merged_path = dirs["final"] / f"{project_name}_merged.mp4"

    # Use 0.5s crossfade for smooth construction transition feel
    concatenate_simple(clip_files, merged_path)  # hard cut — cleaner transitions (rebornspacestv style)

    # Duration check
    duration = get_video_duration(merged_path)
    logger.info(f"   Merged duration: {duration:.1f}s")

    if duration > duration_cfg["max"]:
        trimmed = dirs["final"] / f"{project_name}_trimmed.mp4"
        trim_to_duration(merged_path, trimmed, duration_cfg["max"])
        merged_path = trimmed

    # ── 5. Final export ───────────────────────────────────────────────────
    final_path = dirs["final"] / f"{project_name}_FINAL.mp4"
    final_export(merged_path, final_path)

    elapsed = time.time() - start_time
    logger.info(f"\n✅ Timelapse video ready: {final_path}")
    logger.info(f"⏱️ Time: {elapsed/60:.1f} minutes")

    # ── 5b. Female Voiceover Narration ─────────────────────────────────────
    narration_style = "none"
    try:
        from core.narration import create_narration_for_concept
        from core.ffmpeg_tools import mix_voiceover
        narration_audio, narration_style = create_narration_for_concept(
            concept_name=concept["name"],
            hook=concept["hook"],
            output_path=dirs["final"] / f"{project_name}_narration.wav",
        )
        if narration_audio and narration_audio.exists():
            narrated_out = dirs["final"] / f"{project_name}_NARRATED.mp4"
            mix_voiceover(
                final_path, narration_audio, narrated_out,
                voice_volume=1.0,   # Full voice volume
                bg_duck=0.2,        # Duck original audio to 20%
            )
            if narrated_out.exists() and narrated_out.stat().st_size > 0:
                final_path = narrated_out
                logger.info(f"🎙️ Voiceover narration added (style: {narration_style})")
    except Exception as e:
        logger.warning(f"⚠️ Narration step skipped: {e}")

    # ── 5c. Background Music (layered on top of narration) ──────────────────
    try:
        from core.music_generator import generate_background_music
        from core.ffmpeg_tools import mix_background_music
        music_path = generate_background_music(CHANNEL)
        if music_path and music_path.exists():
            music_out = dirs["final"] / f"{project_name}_MUSIC.mp4"
            # Lower music volume when narration is present
            vol = 0.08 if narration_style != "none" else 0.15
            mix_background_music(final_path, music_path, music_out, music_volume=vol)
            if music_out.exists() and music_out.stat().st_size > 0:
                final_path = music_out
                logger.info("🎵 Background music added")
    except Exception as e:
        logger.warning(f"⚠️ Music step skipped: {e}")

    # ── 5d. Retention Teaser ───────────────────────────────────────────────
    teased = dirs["final"] / f"{project_name}_TEASED.mp4"
    prepend_teaser(str(final_path), str(teased), teaser_duration=1.0)
    if teased.exists() and teased.stat().st_size > 0:
        final_path = teased
        logger.info("🎣 Retention teaser hook added")

    # ── 6. Save to Vault & Publish ─────────────────────────────────────────────
    full_description = f"{concept['hook']}\n\n{description}\n\n{hashtags}"
    clip_urls = [c.get("url", "") for c in clips if c.get("url")]
    vault.save_video(
        channel=CHANNEL, title=title, description=full_description,
        video_path=str(final_path), clip_urls=clip_urls,
    )

    if not skip_upload:
        logger.info("\n📤 PUBLISHING...")
        results = publish_video(
            video_path=final_path,
            title=title,
            description=full_description,
            channel_name=CHANNEL,
        )
        logger.info(f"📊 Publish results: {results}")
        if any(v for v in results.values() if v):
            vault.mark_published(CHANNEL, title)
    else:
        logger.info("⏭️ Upload skipped.")

    report = {
        "date": today,
        "channel": CHANNEL,
        "concept": concept["name"],
        "title": title,
        "narration_style": narration_style,
        "frames": len(frames),
        "clips": len(clips),
        "duration_min": round(elapsed / 60, 1),
        "final_video": str(final_path),
    }
    logger.info(f"\n🎉 AIMAGINE DAILY COMPLETE: {concept['name']}")
    return report
