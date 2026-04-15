"""
ShadowedHistory — Full Video Production Pipeline

Daily pipeline: topic → Gemini script → visual frames → video clips → FFmpeg merge → publish.
"""

import time
from datetime import date
from pathlib import Path

from core.config import CHANNEL_DIRS, CHANNEL_DURATION, CHANNEL_VEO_MODEL, PIPELINE_TIMEOUT_MINUTES, logger
from core.kie_api import generate_image, generate_video, generate_veo_video, check_credit
from core.imgbb import upload_to_imgbb
from core.ffmpeg_tools import (
    check_ffmpeg, concatenate_simple, concatenate_crossfade, final_export,
    get_video_duration, trim_to_duration, add_text_overlay,
    make_loop_video, prepend_teaser
)
from core.uploader import publish_video
from core.script_generator import generate_script, generate_visual_prompts
from core.utils import download_file, sanitize_filename

from .topics import get_daily_topic
from .prompts import FRAME_TEMPLATES, VIDEO_PROMPTS, get_scene_sequence, BASE_STYLE


CHANNEL = "shadowedhistory"


def run_pipeline(topic: str = None, dry_run: bool = False, skip_upload: bool = False) -> dict | None:
    """Run the full ShadowedHistory pipeline.

    Args:
        topic: Override topic (default: daily auto-select)
        dry_run: If True, only generate script, don't produce video
        skip_upload: If True, generate video but don't publish

    Returns:
        Report dict or None on failure
    """
    today = date.today().isoformat()
    start_time = time.time()
    dirs = CHANNEL_DIRS[CHANNEL]
    duration_cfg = CHANNEL_DURATION[CHANNEL]

    logger.info("\n" + "=" * 60)
    logger.info(f"📜 SHADOWEDHISTORY — Daily Pipeline — {today}")
    logger.info("=" * 60)

    # 1. Credit check
    credit = check_credit()

    # 2. Select topic
    if topic:
        daily_topic = {"topic": topic, "category": "default"}
    else:
        daily_topic = get_daily_topic()

    logger.info(f"📋 Topic: {daily_topic['topic']}")
    logger.info(f"📂 Category: {daily_topic['category']}")

    # 3. Generate script with Gemini (with template fallback)
    logger.info("\n📝 GENERATING SCRIPT...")
    script = generate_script(CHANNEL, daily_topic["topic"])
    if not script:
        logger.warning("⚠️ Gemini script failed, using template script...")
        topic_text = daily_topic["topic"]
        script = {
            "title": f"The Secret They Hid: {topic_text[:50]}",
            "hook": f"This forgotten piece of history will change everything you know...",
            "narration": f"Deep in the archives of history, a secret was buried. {topic_text}. "
                         f"For centuries, this knowledge was hidden from public view. "
                         f"Now, for the first time, the truth is revealed.",
            "description": f"Discover the forgotten truth about {topic_text}. #shorts #history",
            "hashtags": "#shorts #history #facts #mystery #hidden #secrets",
        }

    title = script.get("title", daily_topic["topic"][:100])
    hook = script.get("hook", "")
    description = script.get("description", "")
    location_name = script.get("location_name", "")
    hashtags = script.get("hashtags", "#shorts #history #facts")
    if isinstance(hashtags, list):
        hashtags = " ".join(hashtags)

    # Trending hook — boost title with daily trending keywords
    from core.trending import enhance_title_with_trend, get_trending_hashtags
    title = enhance_title_with_trend(title, CHANNEL)
    trending_tags = get_trending_hashtags(CHANNEL)
    if trending_tags:
        hashtags = f"{hashtags} {trending_tags}"

    logger.info(f"   Title: {title}")
    logger.info(f"   Hook: {hook}")
    if location_name:
        logger.info(f"   📍 Location: {location_name}")

    if dry_run:
        logger.info("🏃 DRY RUN — Skipping video production.")
        return {"date": today, "topic": daily_topic["topic"], "title": title, "dry_run": True}

    # 4. Generate visual prompts
    logger.info("\n🎨 GENERATING VISUAL PROMPTS...")
    visual_prompts = generate_visual_prompts(CHANNEL, script)

    if not visual_prompts or len(visual_prompts) < 3:
        # Fallback: use template-based prompts
        logger.warning("⚠️ Gemini visual prompts insufficient, using templates...")
        scene_seq = get_scene_sequence(daily_topic["category"])
        visual_prompts = []
        for i, scene_key in enumerate(scene_seq):
            frame_prompt = FRAME_TEMPLATES.get(scene_key, FRAME_TEMPLATES["artifact_reveal"])
            video_prompt = VIDEO_PROMPTS.get(
                list(VIDEO_PROMPTS.keys())[i % len(VIDEO_PROMPTS)],
                "Cinematic transition. 8 seconds."
            )
            visual_prompts.append({
                "frame_number": i,
                "frame_prompt": f"{frame_prompt} Topic context: {daily_topic['topic'][:100]}",
                "video_prompt": video_prompt,
                "duration_seconds": 8,
            })

    project_name = sanitize_filename(title)

    # 5. Generate frames (images)
    logger.info(f"\n🖼️ GENERATING {len(visual_prompts)} FRAMES...")
    frames = []
    previous_url = None

    for i, vp in enumerate(visual_prompts):
        # Pipeline timeout check
        elapsed_min = (time.time() - start_time) / 60
        if elapsed_min > PIPELINE_TIMEOUT_MINUTES * 0.6:  # 60% of timeout = stop making new frames
            logger.warning(f"⏰ Pipeline timeout approaching ({elapsed_min:.0f}min), stopping frame generation")
            break

        frame_prompt = vp.get("frame_prompt", "")
        logger.info(f"  Frame {i+1}/{len(visual_prompts)}...")

        url = generate_image(
            prompt=frame_prompt,
            reference_url=previous_url,
        )

        if url:
            save_path = dirs["frames"] / f"{project_name}_frame_{i:02d}.png"
            local = download_file(url, save_path)
            if local:
                frames.append({
                    "url": url, "local_path": local,
                    "frame_number": i, "prompt": vp
                })
                # Upload to ImgBB for next reference
                imgbb_url = upload_to_imgbb(local)
                previous_url = imgbb_url or url
        else:
            logger.warning(f"⚠️ Frame {i+1} failed!")

    if len(frames) < 2:
        logger.error("❌ Not enough frames generated!")
        return None

    # 6. Generate video clips
    logger.info(f"\n🎬 GENERATING {len(frames)-1} VIDEO CLIPS...")
    clips = []

    for i in range(len(frames) - 1):
        # Pipeline timeout check
        elapsed_min = (time.time() - start_time) / 60
        if elapsed_min > PIPELINE_TIMEOUT_MINUTES * 0.85:  # 85% of timeout = stop, publish what we have
            logger.warning(f"⏰ Pipeline timeout approaching ({elapsed_min:.0f}min), stopping clip generation")
            break

        start_frame = frames[i]
        end_frame = frames[i + 1]
        vp = visual_prompts[i] if i < len(visual_prompts) else visual_prompts[-1]

        logger.info(f"  Clip {i+1}: Frame {i} → Frame {i+1}")

        # Try VEO3 first (more stable), fall back to Kling
        veo_model = CHANNEL_VEO_MODEL.get(CHANNEL)
        video_prompt = vp.get("video_prompt", "Cinematic transition. 8 seconds.")

        video_url = None
        if veo_model:
            # VEO3 Lite: text-to-video with image reference
            veo_prompt = f"{video_prompt} Historical documentary narration. Deep dramatic voice."
            video_url = generate_veo_video(
                prompt=veo_prompt,
                image_url=start_frame["url"],
                duration=str(vp.get("duration_seconds", 8)),
                model=veo_model,
            )

        # Fallback to Kling if VEO3 fails
        if not video_url:
            logger.info(f"  🔄 Falling back to Kling for clip {i+1}...")
            video_url = generate_video(
                prompt=video_prompt,
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

    # 7. Add location text overlay to FIRST clip (3 seconds, fade in/out)
    if location_name and clips:
        logger.info(f"\n📍 Adding location overlay: {location_name}")
        first_clip = clips[0]["local_path"]
        overlaid_path = dirs["clips"] / f"{project_name}_clip_01_overlaid.mp4"
        add_text_overlay(
            input_path=first_clip,
            output_path=overlaid_path,
            text=location_name,
            duration=3.0,
            fontsize=42,
        )
        clips[0]["local_path"] = overlaid_path

    # 8. FFmpeg merge
    logger.info("\n🔗 MERGING CLIPS...")
    if not check_ffmpeg():
        return None

    clip_files = [c["local_path"] for c in clips]
    merged_path = dirs["final"] / f"{project_name}_merged.mp4"
    concatenate_simple(clip_files, merged_path)  # hard cut — cleaner than crossfade

    # 9. Final export (1080x1920)
    final_path = dirs["final"] / f"{project_name}_FINAL.mp4"
    final_export(merged_path, final_path)

    # 9. Duration check
    duration = get_video_duration(final_path)
    if duration > duration_cfg["max"]:
        trimmed_path = dirs["final"] / f"{project_name}_TRIMMED.mp4"
        trim_to_duration(final_path, trimmed_path, duration_cfg["max"])
        final_path = trimmed_path

    elapsed = time.time() - start_time
    logger.info(f"\n✅ Video ready: {final_path}")
    logger.info(f"⏱️ Time: {elapsed/60:.1f} minutes")

    # 9b. Background Music
    try:
        from core.music_generator import generate_background_music
        from core.ffmpeg_tools import mix_background_music
        music_path = generate_background_music(CHANNEL)
        if music_path and music_path.exists():
            music_out = dirs["final"] / f"{project_name}_MUSIC.mp4"
            mix_background_music(final_path, music_path, music_out, music_volume=0.12)
            if music_out.exists() and music_out.stat().st_size > 0:
                final_path = music_out
                logger.info("🎵 Background music added")
    except Exception as e:
        logger.warning(f"⚠️ Music step skipped: {e}")

    # 9c. Growth: Seamless Loop + Retention Teaser
    from core.config import CHANNEL_LOOP_ENABLED
    if CHANNEL_LOOP_ENABLED.get(CHANNEL, False):
        looped = dirs["final"] / f"{project_name}_LOOP.mp4"
        make_loop_video(str(final_path), str(looped))
        if looped.exists() and looped.stat().st_size > 0:
            final_path = looped
            logger.info("♻️ Seamless loop applied")

    teased = dirs["final"] / f"{project_name}_TEASED.mp4"
    prepend_teaser(str(final_path), str(teased), teaser_duration=1.0)
    if teased.exists() and teased.stat().st_size > 0:
        final_path = teased
        logger.info("🎣 Retention teaser hook added")

    # 10. Publish
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

    # 11. Report
    report = {
        "date": today,
        "channel": CHANNEL,
        "topic": daily_topic["topic"],
        "category": daily_topic["category"],
        "title": title,
        "frames": len(frames),
        "clips": len(clips),
        "duration_min": round(elapsed / 60, 1),
        "final_video": str(final_path),
    }

    logger.info(f"\n🎉 SHADOWEDHISTORY DAILY COMPLETE: {title}")
    return report
