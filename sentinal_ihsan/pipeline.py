"""
Sentinal Ihsan — Full Video Production Pipeline

Daily pipeline: trend analysis → Gemini script → face-enhanced visuals → video → publish.
"""

import time
from datetime import date
from pathlib import Path

from core.config import CHANNEL_DIRS, CHANNEL_DURATION, SENTINAL_FACE_REF, logger
from core.kie_api import generate_image, generate_video, check_credit
from core.imgbb import upload_to_imgbb
from core.ffmpeg_tools import (
    check_ffmpeg, concatenate_crossfade, final_export,
    get_video_duration, trim_to_duration
)
from core.uploader import publish_video
from core.script_generator import generate_script, generate_visual_prompts
from core.utils import download_file, sanitize_filename

from .competitor import get_daily_topic, get_trending_with_gemini
from .prompts import FRAME_TEMPLATES, VIDEO_PROMPTS


CHANNEL = "sentinal_ihsan"


def run_pipeline(topic: str = None, dry_run: bool = False, skip_upload: bool = False) -> dict | None:
    """Run the full Sentinal Ihsan pipeline."""
    today = date.today().isoformat()
    start_time = time.time()
    dirs = CHANNEL_DIRS[CHANNEL]
    duration_cfg = CHANNEL_DURATION[CHANNEL]

    logger.info("\n" + "=" * 60)
    logger.info(f"🎬 SENTINAL IHSAN — Daily Pipeline — {today}")
    logger.info("=" * 60)

    # 1. Credit check
    credit = check_credit()

    # 2. Select topic (try Gemini trending first, fallback to pre-built)
    if topic:
        daily_topic = {"topic": topic, "category": "manual"}
    else:
        daily_topic = get_trending_with_gemini()
        if not daily_topic:
            daily_topic = get_daily_topic()

    logger.info(f"📋 Topic: {daily_topic['topic']}")

    # 3. Generate script
    logger.info("\n📝 GENERATING VIRAL SCRIPT...")
    script = generate_script(CHANNEL, daily_topic["topic"])
    if not script:
        logger.warning("⚠️ Gemini script failed, using template...")
        topic_text = daily_topic["topic"]
        script = {
            "title": f"You Won't BELIEVE This! 🤯 {topic_text[:40]}",
            "hook": "Wait for it... you're NOT ready for this!",
            "scene_descriptions": [
                f"Close-up reaction shot, person looking shocked at camera",
                f"Wide shot showing the setup for: {topic_text}",
                f"Action shot of the experiment in progress",
                f"Mind-blown reaction, jaw drop moment",
            ],
            "description": f"Watch what happens when we try {topic_text}! #shorts",
            "hashtags": "#shorts #viral #experiment #mindblown #satisfying",
        }

    title = script.get("title", daily_topic["topic"][:100])
    hook = script.get("hook", "")
    description = script.get("description", "")
    hashtags = script.get("hashtags", "#shorts #viral #experiment")
    if isinstance(hashtags, list):
        hashtags = " ".join(hashtags)

    logger.info(f"   Title: {title}")
    logger.info(f"   Hook: {hook}")

    if dry_run:
        logger.info("🏃 DRY RUN — Skipping video production.")
        return {"date": today, "topic": daily_topic["topic"], "title": title, "dry_run": True}

    # 4. Generate visual prompts
    logger.info("\n🎨 GENERATING VISUAL PROMPTS...")
    visual_prompts = generate_visual_prompts(CHANNEL, script)

    if not visual_prompts or len(visual_prompts) < 3:
        logger.warning("⚠️ Using template-based prompts...")
        scene_keys = ["intro_talking", "concept_reveal", "interaction", "reaction_close"]
        video_keys = list(VIDEO_PROMPTS.keys())
        visual_prompts = []
        for i, sk in enumerate(scene_keys[:4]):
            visual_prompts.append({
                "frame_number": i,
                "frame_prompt": f"{FRAME_TEMPLATES[sk]} Related to: {daily_topic['topic'][:80]}",
                "video_prompt": VIDEO_PROMPTS[video_keys[i % len(video_keys)]],
                "duration_seconds": 8,
            })

    project_name = sanitize_filename(title)

    # 5. Generate frames (with face reference for character consistency)
    logger.info(f"\n🖼️ GENERATING {len(visual_prompts)} FRAMES...")
    frames = []
    previous_url = None
    face_ref = SENTINAL_FACE_REF if SENTINAL_FACE_REF else None

    for i, vp in enumerate(visual_prompts):
        frame_prompt = vp.get("frame_prompt", "")

        # Use face reference for first and last frames (reaction shots)
        ref_url = face_ref if (i == 0 or i == len(visual_prompts) - 1) else previous_url

        logger.info(f"  Frame {i+1}/{len(visual_prompts)}...")
        url = generate_image(prompt=frame_prompt, reference_url=ref_url)

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

    # 6. Generate video clips
    logger.info(f"\n🎬 GENERATING {len(frames)-1} VIDEO CLIPS...")
    clips = []

    for i in range(len(frames) - 1):
        start_frame = frames[i]
        end_frame = frames[i + 1]
        vp = visual_prompts[i] if i < len(visual_prompts) else visual_prompts[-1]

        logger.info(f"  Clip {i+1}: Frame {i} → Frame {i+1}")
        video_url = generate_video(
            prompt=vp.get("video_prompt", "Fast-paced viral transition. 8 seconds."),
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
        logger.error("❌ No video clips generated!")
        return None

    # 7. FFmpeg merge + export
    logger.info("\n🔗 MERGING CLIPS...")
    if not check_ffmpeg():
        return None

    clip_files = [c["local_path"] for c in clips]
    merged_path = dirs["final"] / f"{project_name}_merged.mp4"
    concatenate_crossfade(clip_files, merged_path, crossfade=0.3)  # Quick cuts for viral feel

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

    # 8. Publish
    if not skip_upload:
        logger.info("\n📤 PUBLISHING...")
        full_description = f"{hook}\n\n{description}\n\n{hashtags}"
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
        "date": today, "channel": CHANNEL, "topic": daily_topic["topic"],
        "title": title, "frames": len(frames), "clips": len(clips),
        "duration_min": round(elapsed / 60, 1), "final_video": str(final_path),
    }
    logger.info(f"\n🎉 SENTINAL IHSAN DAILY COMPLETE: {title}")
    return report
