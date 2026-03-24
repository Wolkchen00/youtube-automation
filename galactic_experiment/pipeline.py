"""
Galactic Experiment — Full Video Production Pipeline

Daily: space topic → Gemini script → cosmic visuals → cinematic video → publish.
Uses Veo 3.1 for higher quality cinematic space videos.
"""

import time
from datetime import date
from pathlib import Path

from core.config import CHANNEL_DIRS, CHANNEL_DURATION, logger
from core.kie_api import generate_image, generate_video, generate_veo_video, check_credit
from core.imgbb import upload_to_imgbb
from core.ffmpeg_tools import (
    check_ffmpeg, concatenate_crossfade, final_export,
    get_video_duration, trim_to_duration
)
from core.uploader import publish_video
from core.script_generator import generate_script, generate_visual_prompts
from core.utils import download_file, sanitize_filename

from .topics import get_daily_topic
from .prompts import FRAME_TEMPLATES, VIDEO_PROMPTS, get_scene_sequence


CHANNEL = "galactic_experiment"


def run_pipeline(topic: str = None, dry_run: bool = False, skip_upload: bool = False) -> dict | None:
    """Run the full Galactic Experiment pipeline."""
    today = date.today().isoformat()
    start_time = time.time()
    dirs = CHANNEL_DIRS[CHANNEL]
    duration_cfg = CHANNEL_DURATION[CHANNEL]

    logger.info("\n" + "=" * 60)
    logger.info(f"🌌 GALACTIC EXPERIMENT — Daily Pipeline — {today}")
    logger.info("=" * 60)

    credit = check_credit()

    # Topic selection
    if topic:
        daily_topic = {"topic": topic, "category": "default"}
    else:
        daily_topic = get_daily_topic()

    logger.info(f"📋 Topic: {daily_topic['topic']}")

    # Generate script
    logger.info("\n📝 GENERATING SPACE SCRIPT...")
    script = generate_script(CHANNEL, daily_topic["topic"])
    if not script:
        logger.error("❌ Script generation failed!")
        return None

    title = script.get("title", daily_topic["topic"][:100])
    hook = script.get("hook", "")
    description = script.get("description", "")
    hashtags = script.get("hashtags", "#shorts #space #universe #science")
    if isinstance(hashtags, list):
        hashtags = " ".join(hashtags)

    logger.info(f"   Title: {title}")

    if dry_run:
        logger.info("🏃 DRY RUN — Skipping.")
        return {"date": today, "topic": daily_topic["topic"], "title": title, "dry_run": True}

    # Visual prompts
    logger.info("\n🎨 GENERATING VISUAL PROMPTS...")
    visual_prompts = generate_visual_prompts(CHANNEL, script)

    if not visual_prompts or len(visual_prompts) < 3:
        logger.warning("⚠️ Using template-based space prompts...")
        scene_seq = get_scene_sequence(daily_topic["category"])
        video_keys = list(VIDEO_PROMPTS.keys())
        visual_prompts = []
        for i, sk in enumerate(scene_seq):
            visual_prompts.append({
                "frame_number": i,
                "frame_prompt": f"{FRAME_TEMPLATES.get(sk, FRAME_TEMPLATES['deep_space'])} Context: {daily_topic['topic'][:80]}",
                "video_prompt": VIDEO_PROMPTS[video_keys[i % len(video_keys)]],
                "duration_seconds": 8,
            })

    project_name = sanitize_filename(title)

    # Generate frames — use GPT Image 1.5 for photorealistic space
    logger.info(f"\n🖼️ GENERATING {len(visual_prompts)} COSMIC FRAMES...")
    frames = []
    previous_url = None

    for i, vp in enumerate(visual_prompts):
        frame_prompt = vp.get("frame_prompt", "")
        logger.info(f"  Frame {i+1}/{len(visual_prompts)}...")

        # Using Nano Banana 2 (5cr) instead of GPT Image 1.5 (20cr) — 4x cheaper
        # NB2 is sufficient quality with reference chaining for consistency
        url = generate_image(
            prompt=frame_prompt,
            reference_url=previous_url,
        )

        if url:
            save_path = dirs["frames"] / f"{project_name}_frame_{i:02d}.png"
            local = download_file(url, save_path)
            if local:
                frames.append({"url": url, "local_path": local, "frame_number": i, "prompt": vp})
                imgbb_url = upload_to_imgbb(local)
                previous_url = imgbb_url or url
        else:
            logger.warning(f"⚠️ Frame {i+1} failed!")

    if len(frames) < 2:
        logger.error("❌ Not enough frames!")
        return None

    # Generate video clips — use Kling 3.0 for cinematic space
    logger.info(f"\n🎬 GENERATING {len(frames)-1} SPACE VIDEO CLIPS...")
    clips = []

    for i in range(len(frames) - 1):
        start_frame = frames[i]
        end_frame = frames[i + 1]
        vp = visual_prompts[i] if i < len(visual_prompts) else visual_prompts[-1]

        logger.info(f"  Clip {i+1}: Frame {i} → Frame {i+1}")

        video_url = generate_video(
            prompt=vp.get("video_prompt", "Cinematic space transition. 8 seconds."),
            start_image_url=start_frame["url"],
            end_image_url=end_frame["url"],
            duration=str(vp.get("duration_seconds", 8)),
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
        logger.error("❌ No video clips!")
        return None

    # FFmpeg merge with slow crossfades for cinematic feel
    logger.info("\n🔗 MERGING CLIPS...")
    if not check_ffmpeg():
        return None

    clip_files = [c["local_path"] for c in clips]
    merged_path = dirs["final"] / f"{project_name}_merged.mp4"
    concatenate_crossfade(clip_files, merged_path, crossfade=1.0)  # Slow crossfade for space

    final_path = dirs["final"] / f"{project_name}_FINAL.mp4"
    final_export(merged_path, final_path)

    duration = get_video_duration(final_path)
    if duration > duration_cfg["max"]:
        trimmed = dirs["final"] / f"{project_name}_TRIMMED.mp4"
        trim_to_duration(final_path, trimmed, duration_cfg["max"])
        final_path = trimmed

    elapsed = time.time() - start_time
    logger.info(f"\n✅ Video ready: {final_path}")
    logger.info(f"⏱️ Time: {elapsed/60:.1f} minutes")

    # Publish
    if not skip_upload:
        logger.info("\n📤 PUBLISHING...")
        full_description = f"{hook}\n\n{description}\n\n{hashtags}"
        results = publish_video(
            video_path=final_path, title=title,
            description=full_description, channel_name=CHANNEL,
        )
        logger.info(f"📊 Publish results: {results}")
    else:
        logger.info("⏭️ Upload skipped.")

    report = {
        "date": today, "channel": CHANNEL, "topic": daily_topic["topic"],
        "title": title, "frames": len(frames), "clips": len(clips),
        "duration_min": round(elapsed / 60, 1), "final_video": str(final_path),
    }
    logger.info(f"\n🎉 GALACTIC EXPERIMENT DAILY COMPLETE: {title}")
    return report
