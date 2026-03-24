"""
AImagine — Seamless Loop Video Pipeline

Creates 15-30 second videos where beginning = ending frame.
Pipeline: concept → anchor frame → intermediate frames → video clips → reverse merge → loop video.
"""

import time
from datetime import date
from pathlib import Path

from core.config import CHANNEL_DIRS, CHANNEL_DURATION, logger
from core.kie_api import generate_image, generate_video, check_credit
from core.imgbb import upload_to_imgbb
from core.ffmpeg_tools import (
    check_ffmpeg, concatenate_simple, make_loop_video,
    final_export, get_video_duration, trim_to_duration
)
from core.uploader import publish_video
from core.script_generator import generate_script
from core.utils import download_file, sanitize_filename

from .concepts import get_daily_concept, LOOP_CONCEPTS
from .prompts import BASE_STYLE


CHANNEL = "aimagine"


def run_pipeline(concept_name: str = None, dry_run: bool = False, skip_upload: bool = False) -> dict | None:
    """Run the full AImagine seamless loop pipeline.

    Key approach: Generate forward video (A→B→C), then reverse it (C→B→A),
    creating a seamless loop since the first and last frames are identical.
    """
    today = date.today().isoformat()
    start_time = time.time()
    dirs = CHANNEL_DIRS[CHANNEL]
    duration_cfg = CHANNEL_DURATION[CHANNEL]

    logger.info("\n" + "=" * 60)
    logger.info(f"🔁 AIMAGINE — Daily Loop Pipeline — {today}")
    logger.info("=" * 60)

    credit = check_credit()

    # Select concept
    if concept_name:
        concept = next((c for c in LOOP_CONCEPTS if c["name"].lower() == concept_name.lower()), None)
        if not concept:
            logger.error(f"Concept not found: {concept_name}")
            return None
    else:
        concept = get_daily_concept()

    logger.info(f"📋 Concept: {concept['name']}")

    # Generate title/description with Gemini
    logger.info("\n📝 GENERATING METADATA...")
    script = generate_script(CHANNEL, concept["name"])

    if script:
        title = script.get("title", concept.get("title", concept["name"]))
        description = script.get("description", concept.get("description", f"Mesmerizing loop: {concept['name']}"))
        hashtags = script.get("hashtags", concept.get("hashtags", "#shorts #satisfying #loop"))
        if isinstance(hashtags, list):
            hashtags = " ".join(hashtags)
    else:
        # Use concept's built-in title/description (from @hellopersonality analysis)
        title = concept.get("title", f"🔁 {concept['name']}")
        description = concept.get("description", f"Mesmerizing seamless loop: {concept['name']}")
        hashtags = concept.get("hashtags", "#shorts #satisfying #loop #mesmerizing #aiart #psychedelic")

    if dry_run:
        logger.info("🏃 DRY RUN — Skipping.")
        return {"date": today, "concept": concept["name"], "title": title, "dry_run": True}

    project_name = sanitize_filename(concept["name"])

    # 1. Generate anchor frame (start = end)
    logger.info("\n🖼️ GENERATING ANCHOR FRAME (start=end)...")
    anchor_prompt = concept.get("anchor_prompt", concept.get("loop_prompt", ""))
    full_anchor_prompt = f"{anchor_prompt}, {BASE_STYLE}"
    anchor_url = generate_image(prompt=full_anchor_prompt)
    if not anchor_url:
        logger.error("❌ Anchor frame failed!")
        return None

    anchor_path = dirs["frames"] / f"{project_name}_anchor.png"
    download_file(anchor_url, anchor_path)
    anchor_imgbb = upload_to_imgbb(anchor_path) or anchor_url

    # 2. Generate intermediate frames
    intermediates = concept.get("intermediate_prompts", concept.get("intermediates", []))
    logger.info(f"\n🖼️ GENERATING {len(intermediates)} INTERMEDIATE FRAMES...")

    frames = [{"url": anchor_imgbb, "local_path": anchor_path, "frame_number": 0}]
    prev_url = anchor_imgbb

    for i, prompt in enumerate(intermediates):
        logger.info(f"  Intermediate frame {i+1}/{len(intermediates)}...")
        url = generate_image(prompt=prompt, reference_url=prev_url)
        if url:
            save_path = dirs["frames"] / f"{project_name}_inter_{i:02d}.png"
            local = download_file(url, save_path)
            if local:
                frames.append({"url": url, "local_path": local, "frame_number": i + 1})
                imgbb_url = upload_to_imgbb(local)
                prev_url = imgbb_url or url
        else:
            logger.warning(f"⚠️ Intermediate {i+1} failed!")

    # Add anchor again as final frame (for video generation between last intermediate → anchor)
    frames.append({"url": anchor_imgbb, "local_path": anchor_path, "frame_number": len(frames)})

    if len(frames) < 3:
        logger.error("❌ Not enough frames for loop!")
        return None

    # 3. Generate video clips (forward direction: anchor → inter1 → inter2 → ... → anchor)
    video_prompts = concept.get("video_prompts", [])
    logger.info(f"\n🎬 GENERATING {len(frames)-1} VIDEO CLIPS...")
    clips = []

    for i in range(len(frames) - 1):
        start_f = frames[i]
        end_f = frames[i + 1]
        vp = video_prompts[i] if i < len(video_prompts) else "Smooth mesmerizing transition. 8 seconds."

        logger.info(f"  Clip {i+1}: Frame {i} → Frame {i+1}")
        video_url = generate_video(
            prompt=vp,
            start_image_url=start_f["url"],
            end_image_url=end_f["url"],
            duration="8",
            sound=True,
        )

        if video_url:
            save_path = dirs["clips"] / f"{project_name}_clip_{i+1:02d}.mp4"
            local = download_file(video_url, save_path)
            if local:
                clips.append({"url": video_url, "local_path": local, "clip_number": i + 1})
        else:
            logger.warning(f"⚠️ Clip {i+1} failed!")

    if not clips:
        logger.error("❌ No clips generated!")
        return None

    # 4. FFmpeg merge (simple concat — no crossfade to preserve loop)
    logger.info("\n🔗 MERGING CLIPS...")
    if not check_ffmpeg():
        return None

    clip_files = [c["local_path"] for c in clips]
    merged_path = dirs["final"] / f"{project_name}_forward.mp4"
    concatenate_simple(clip_files, merged_path, clips_dir=dirs["clips"])

    # 5. Check duration and handle loop
    duration = get_video_duration(merged_path)
    logger.info(f"   Forward video duration: {duration:.1f}s")

    # If video is short enough, create loop by making it forward + reverse
    if duration < duration_cfg["min"]:
        logger.info("🔄 Video too short — creating forward+reverse loop...")
        loop_path = dirs["final"] / f"{project_name}_loop.mp4"
        make_loop_video(merged_path, loop_path)
        merged_path = loop_path

    # If too long, trim
    duration = get_video_duration(merged_path)
    if duration > duration_cfg["max"]:
        trimmed = dirs["final"] / f"{project_name}_trimmed.mp4"
        trim_to_duration(merged_path, trimmed, duration_cfg["max"])
        merged_path = trimmed

    # 6. Final export
    final_path = dirs["final"] / f"{project_name}_FINAL.mp4"
    final_export(merged_path, final_path)

    elapsed = time.time() - start_time
    logger.info(f"\n✅ Loop video ready: {final_path}")
    logger.info(f"⏱️ Time: {elapsed/60:.1f} minutes")

    # 7. Publish
    if not skip_upload:
        logger.info("\n📤 PUBLISHING...")
        full_description = f"{description}\n\n{hashtags}"
        results = publish_video(
            video_path=final_path, title=title,
            description=full_description, channel_name=CHANNEL,
        )
        logger.info(f"📊 Publish results: {results}")
    else:
        logger.info("⏭️ Upload skipped.")

    report = {
        "date": today, "channel": CHANNEL, "concept": concept["name"],
        "title": title, "frames": len(frames), "clips": len(clips),
        "duration_min": round(elapsed / 60, 1), "final_video": str(final_path),
    }
    logger.info(f"\n🎉 AIMAGINE DAILY COMPLETE: {concept['name']}")
    return report
