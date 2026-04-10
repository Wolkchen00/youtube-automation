"""
AImagine — AI Construction Timelapse Pipeline

Creates 24-second viral construction timelapse videos.
Pipeline: concept selection → 4 frames (chained) → 3 video clips → crossfade merge → publish.

Cost per video: ~128 credits ($0.64)
Format: 9:16 vertical, 3 clips × 8s = 24s
"""

import time
from datetime import date
from pathlib import Path

from core.config import CHANNEL_DIRS, CHANNEL_DURATION, logger
from core.kie_api import generate_image, generate_video, check_credit
from core.imgbb import upload_to_imgbb
from core.ffmpeg_tools import (
    check_ffmpeg, concatenate_simple, concatenate_crossfade, final_export,
    get_video_duration, trim_to_duration
)
from core.uploader import publish_video
from core.utils import download_file, sanitize_filename

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
    logger.info(f"🏗️ AIMAGINE — Construction Timelapse Pipeline — {today}")
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
    description = concept.get("description", f"Incredible construction timelapse: {concept['name']}")
    hashtags = concept.get("hashtags", "#shorts #construction #timelapse #satisfying #diy")

    if dry_run:
        logger.info("🏃 DRY RUN — Skipping generation.")
        return {"date": today, "concept": concept["name"], "title": title, "dry_run": True}

    project_name = sanitize_filename(concept["name"])
    frame_prompts = concept["frame_prompts"]
    video_prompts = concept["video_prompts"]

    # ── 2. Generate 4 frames with chained references ──────────────────────
    logger.info(f"\n🖼️ GENERATING {len(frame_prompts)} CONSTRUCTION FRAMES...")
    frames = []
    previous_url = None

    for i, prompt in enumerate(frame_prompts):
        stage_names = ["Empty Site", "Excavation", "Construction", "Final Reveal"]
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
    logger.info(f"\n🎬 GENERATING {actual_clips_needed} TIMELAPSE VIDEO CLIPS...")
    clips = []

    for i in range(actual_clips_needed):
        start_frame = frames[i]
        end_frame = frames[i + 1]
        vp = video_prompts[i] if i < len(video_prompts) else "Fast construction timelapse. Fixed drone angle. 8 seconds."

        logger.info(f"  Clip {i+1}: {start_frame['stage']} → {end_frame['stage']}")

        video_url = generate_video(
            prompt=vp,
            start_image_url=start_frame["url"],
            end_image_url=end_frame["url"],
            duration="8",
            sound=True,
        )

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

    # ── 6. Publish ────────────────────────────────────────────────────────
    if not skip_upload:
        logger.info("\n📤 PUBLISHING...")
        full_description = f"{concept['hook']}\n\n{description}\n\n{hashtags}"
        results = publish_video(
            video_path=final_path,
            title=title,
            description=full_description,
            channel_name=CHANNEL,
        )
        logger.info(f"📊 Publish results: {results}")
    else:
        logger.info("⏭️ Upload skipped.")

    report = {
        "date": today,
        "channel": CHANNEL,
        "concept": concept["name"],
        "title": title,
        "frames": len(frames),
        "clips": len(clips),
        "duration_min": round(elapsed / 60, 1),
        "final_video": str(final_path),
    }
    logger.info(f"\n🎉 AIMAGINE DAILY COMPLETE: {concept['name']}")
    return report
