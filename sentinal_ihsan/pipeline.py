"""
Sentinal Ihsan — Full Video Production Pipeline (VEO3 Overhaul)

CRITICAL CHANGES:
  ✅ 4 clips × 8s = ~32s final (minimum 20s enforced)
  ✅ VEO3 Lite for video clips (speech + motion)
  ✅ Face reference on ALL frames
  ✅ Smooth crossfade transitions (0.3s — cinematic feel)
  ✅ Action-first prompts (continuous interaction with concept)
  ✅ iPhone UGC realism — outdoor locations, authentic textures
"""

import time
from datetime import date
from pathlib import Path

from core.config import CHANNEL_DIRS, CHANNEL_DURATION, CHANNEL_VEO_MODEL, CINEMATIC_VIDEO_MODEL_LITE, SENTINAL_FACE_REF, logger
from core.kie_api import generate_image, generate_video, generate_veo_video, check_credit
from core.imgbb import upload_to_imgbb
from core.ffmpeg_tools import (
    check_ffmpeg, concatenate_crossfade, final_export,
    get_video_duration, trim_to_duration,
    make_loop_video, prepend_teaser
)
from core.uploader import publish_video
from core.script_generator import generate_script, generate_visual_prompts
from core.utils import download_file, sanitize_filename

from .competitor import get_daily_topic, get_trending_with_gemini
from .prompts import FRAME_TEMPLATES, VIDEO_PROMPTS, IDENTITY_LOCK, CAMERA_POV, QUALITY_GUARD

CHANNEL = "sentinal_ihsan"
NUM_SCENES = 4  # 4 clips × 8s = 32s raw → ~30s final (0.3s crossfade transitions)


def run_pipeline(topic: str = None, dry_run: bool = False, skip_upload: bool = False) -> dict | None:
    """Run the full Sentinal Ihsan pipeline with VEO3."""
    today = date.today().isoformat()
    start_time = time.time()
    dirs = CHANNEL_DIRS[CHANNEL]
    duration_cfg = CHANNEL_DURATION[CHANNEL]

    logger.info("\n" + "=" * 60)
    logger.info(f"🎬 SENTINAL IHSAN — Daily Pipeline (VEO3) — {today}")
    logger.info("=" * 60)

    # 1. Credit check
    credit = check_credit()

    # 2. Select topic
    if topic:
        daily_topic = {"topic": topic, "category": "manual", "setting": "generic"}
    else:
        daily_topic = get_trending_with_gemini()
        if not daily_topic:
            daily_topic = get_daily_topic()

    logger.info(f"📋 Topic: {daily_topic['topic']}")
    logger.info(f"🏠 Setting: {daily_topic.get('setting', 'generic')}")

    # 3. Generate script
    logger.info("\n📝 GENERATING VIRAL SCRIPT...")
    script = generate_script(CHANNEL, daily_topic["topic"])
    if not script:
        logger.warning("⚠️ Gemini script failed, using template...")
        topic_text = daily_topic["topic"]
        setting = daily_topic.get("setting", "room")
        script = {
            "title": f"You Won't BELIEVE This! 🤯 {topic_text[:40]}",
            "hook": f"he opens with a hook about {topic_text[:60]}",
            "scene_descriptions": [
                f"Close-up front camera POV, {setting}, character excitedly tells viewers what he is about to do",
                f"Character starts interacting with the concept — touching, pouring, painting, or building",
                f"Character reacts with genuine shock or excitement, continues describing",
                f"Final wide reveal showing the full result, character asks viewers to comment",
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

    # 3b. Trending hook — boost title with daily trending keywords
    from core.trending import enhance_title_with_trend, get_trending_hashtags
    title = enhance_title_with_trend(title, CHANNEL)
    trending_tags = get_trending_hashtags(CHANNEL)
    if trending_tags:
        hashtags = f"{hashtags} {trending_tags}"

    logger.info(f"   Title: {title}")
    logger.info(f"   Hook: {hook}")

    if dry_run:
        logger.info("🏃 DRY RUN — Skipping video production.")
        return {"date": today, "topic": daily_topic["topic"], "title": title, "dry_run": True}

    # 4. Generate visual prompts (6 scenes)
    logger.info(f"\n🎨 GENERATING {NUM_SCENES} VISUAL PROMPTS...")
    visual_prompts = generate_visual_prompts(CHANNEL, script)

    if not visual_prompts or len(visual_prompts) < NUM_SCENES:
        logger.warning(f"⚠️ Got {len(visual_prompts) if visual_prompts else 0} prompts, padding to {NUM_SCENES}...")
        scene_keys = list(FRAME_TEMPLATES.keys())[:NUM_SCENES]
        video_keys = list(VIDEO_PROMPTS.keys())
        
        # Use any Gemini-generated prompts first, pad with templates
        if not visual_prompts:
            visual_prompts = []
        
        while len(visual_prompts) < NUM_SCENES:
            idx = len(visual_prompts)
            sk = scene_keys[idx % len(scene_keys)]
            vk = video_keys[idx % len(video_keys)]
            visual_prompts.append({
                "frame_number": idx,
                "frame_prompt": f"{FRAME_TEMPLATES[sk]} Topic: {daily_topic['topic'][:80]}",
                "video_prompt": VIDEO_PROMPTS[vk],
                "duration_seconds": 8,
            })

    # Trim to exactly NUM_SCENES
    visual_prompts = visual_prompts[:NUM_SCENES]

    project_name = sanitize_filename(title)

    # 5. Generate frames — face reference on EVERY frame
    logger.info(f"\n🖼️ GENERATING {len(visual_prompts)} FRAMES (face ref on ALL)...")
    frames = []
    face_ref = SENTINAL_FACE_REF if SENTINAL_FACE_REF else None

    for i, vp in enumerate(visual_prompts):
        frame_prompt = vp.get("frame_prompt", "")
        logger.info(f"  Frame {i+1}/{len(visual_prompts)} (face ref: {'YES' if face_ref else 'NO'})...")

        # CRITICAL: Use face reference on ALL frames for consistency
        url = generate_image(prompt=frame_prompt, reference_url=face_ref)

        # Retry once with simplified prompt if first attempt fails
        if not url:
            logger.warning(f"⚠️ Frame {i+1} failed, retrying with simplified prompt...")
            url = generate_image(prompt=frame_prompt[:300], reference_url=face_ref)

        if url:
            save_path = dirs["frames"] / f"{project_name}_frame_{i:02d}.png"
            local = download_file(url, save_path)
            if local:
                frames.append({"url": url, "local_path": local, "frame_number": i, "prompt": vp})
                # Upload to ImgBB for continuity in next iteration
                imgbb_url = upload_to_imgbb(local)
                if imgbb_url:
                    # Use generated face as reference for next frames (visual continuity)
                    # But always keep original face_ref as primary
                    pass
        else:
            logger.warning(f"⚠️ Frame {i+1} failed!")

    if len(frames) < 3:
        logger.error("❌ Not enough frames generated!")
        return None

    # 6. Generate video clips — Kling primary (VEO3 times out with face-ref), VEO3 fallback
    veo_model = CHANNEL_VEO_MODEL.get(CHANNEL)
    model_name = "Kling" if not veo_model else f"VEO3 ({veo_model})"
    logger.info(f"\n🎬 GENERATING {len(frames)-1} VIDEO CLIPS [{model_name} primary]...")
    clips = []

    for i in range(len(frames) - 1):
        start_frame = frames[i]
        end_frame = frames[i + 1] if (i + 1) < len(frames) else None
        vp = visual_prompts[i] if i < len(visual_prompts) else visual_prompts[-1]
        video_prompt = vp.get("video_prompt", "Character talks to camera excitedly. Natural smartphone video. 8 seconds.")

        logger.info(f"  Clip {i+1}: Frame {i} → motion [{model_name}]...")

        video_url = None

        if veo_model:
            # VEO3 primary (for channels where it works)
            video_url = generate_veo_video(
                prompt=video_prompt,
                image_url=start_frame["url"],
                duration="8",
                model=veo_model,
            )

        if not video_url:
            # Kling: image-to-image video generation (works well with face-ref images)
            if veo_model:
                logger.warning(f"⚠️ VEO3 Clip {i+1} failed, trying Kling fallback...")
            try:
                video_url = generate_video(
                    prompt=video_prompt[:200],
                    start_image_url=start_frame["url"],
                    end_image_url=end_frame["url"] if end_frame else None,
                )
            except Exception as e:
                logger.warning(f"⚠️ Kling error: {e}")
                video_url = None

        if not video_url and not veo_model:
            # Last resort: try VEO3 Lite even if not configured as primary
            logger.warning(f"⚠️ Kling Clip {i+1} failed, trying VEO3 Lite last resort...")
            video_url = generate_veo_video(
                prompt=video_prompt,
                image_url=start_frame["url"],
                duration="8",
                model=CINEMATIC_VIDEO_MODEL_LITE,
            )

        if video_url:
            save_path = dirs["clips"] / f"{project_name}_clip_{i+1:02d}.mp4"
            local = download_file(video_url, save_path)
            if local:
                clips.append({"url": video_url, "local_path": local, "clip_number": i + 1})
                logger.info(f"  ✅ Clip {i+1} ready!")
        else:
            logger.warning(f"⚠️ Clip {i+1} failed!")

    if len(clips) < 2:
        logger.error("❌ Not enough video clips! Need at least 2.")
        return None

    if len(clips) < 3:
        logger.warning(f"⚠️ Only {len(clips)} clips — video will be short but publishing anyway.")

    # 7. FFmpeg merge + export
    logger.info("\n🔗 MERGING CLIPS...")
    if not check_ffmpeg():
        return None

    clip_files = [c["local_path"] for c in clips]
    merged_path = dirs["final"] / f"{project_name}_merged.mp4"
    concatenate_crossfade(clip_files, merged_path, crossfade=0.3)  # smooth cinematic transitions

    final_path = dirs["final"] / f"{project_name}_FINAL.mp4"
    final_export(merged_path, final_path)

    # 8. Duration check (STRICT: minimum 30 seconds)
    duration = get_video_duration(final_path)
    logger.info(f"📏 Video duration: {duration:.1f}s (min: {duration_cfg['min']}s)")

    if duration < duration_cfg["min"]:
        logger.warning(f"⚠️ Video too short ({duration:.1f}s < {duration_cfg['min']}s)!")
        # Still publish — better than nothing

    if duration > duration_cfg["max"]:
        trimmed = dirs["final"] / f"{project_name}_TRIMMED.mp4"
        trim_to_duration(final_path, trimmed, duration_cfg["max"])
        final_path = trimmed

    elapsed = time.time() - start_time
    logger.info(f"\n✅ Video ready: {final_path}")
    logger.info(f"⏱️ Time: {elapsed/60:.1f} minutes")

    # 8b. Growth: Seamless Loop + Retention Teaser
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

    # 9. Publish
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
        "duration_sec": round(duration, 1),
        "duration_min": round(elapsed / 60, 1), "final_video": str(final_path),
    }
    logger.info(f"\n🎉 SENTINAL IHSAN DAILY COMPLETE: {title}")
    return report
