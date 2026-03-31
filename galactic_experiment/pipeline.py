"""
Galactic Experiment — Full Video Production Pipeline

UPDATED: Uses VEO3 for voice narration over space visuals.
Each clip has a narration prompt that generates AI voice-over
describing planet facts, approach details, and scientific data.

Daily: space topic → Gemini narration script → frames → VEO3 narrated clips → merge → publish.
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
    """Run the Galactic Experiment pipeline with VEO3 voice narration.

    Key difference from other channels:
    - Uses VEO3 (not Kling 3.0) for video generation
    - VEO3 generates actual voice narration from the prompt text
    - No text overlays — narration is spoken by AI voice
    - Each clip has a narration script segment
    """
    today = date.today().isoformat()
    start_time = time.time()
    dirs = CHANNEL_DIRS[CHANNEL]
    duration_cfg = CHANNEL_DURATION[CHANNEL]

    logger.info("\n" + "=" * 60)
    logger.info(f"🌌 GALACTIC EXPERIMENT — Daily Pipeline — {today}")
    logger.info("=" * 60)

    credit = check_credit()

    # ── 1. Topic selection ────────────────────────────────────────────────
    if topic:
        daily_topic = {"topic": topic, "category": "default"}
    else:
        daily_topic = get_daily_topic()

    logger.info(f"📋 Topic: {daily_topic['topic']}")

    # ── 2. Generate narration script via Gemini ───────────────────────────
    logger.info("\n📝 GENERATING NARRATION SCRIPT...")
    script = generate_script(CHANNEL, daily_topic["topic"])
    if not script:
        logger.error("❌ Script generation failed!")
        return None

    title = script.get("title", daily_topic["topic"][:100])
    hook = script.get("hook", "")
    narration = script.get("narration", "")
    description = script.get("description", "")
    hashtags = script.get("hashtags", "#shorts #space #universe #science")
    if isinstance(hashtags, list):
        hashtags = " ".join(hashtags)

    # Extract narration segments (for VEO3 voice-over per clip)
    narration_segments = script.get("narration_segments", [])
    if not narration_segments and narration:
        # Split narration into ~3 segments for 3 clips
        sentences = [s.strip() for s in narration.replace("...", ".").split(".") if s.strip()]
        chunk_size = max(1, len(sentences) // 3)
        narration_segments = []
        for i in range(0, len(sentences), chunk_size):
            segment = ". ".join(sentences[i:i + chunk_size]) + "."
            narration_segments.append(segment)
        narration_segments = narration_segments[:3]  # max 3 segments

    logger.info(f"   Title: {title}")
    logger.info(f"   Narration segments: {len(narration_segments)}")

    if dry_run:
        logger.info("🏃 DRY RUN — Skipping.")
        return {"date": today, "topic": daily_topic["topic"], "title": title, "dry_run": True}

    # ── 3. Generate visual prompts ────────────────────────────────────────
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

    # ── 4. Generate frames ────────────────────────────────────────────────
    logger.info(f"\n🖼️ GENERATING {len(visual_prompts)} COSMIC FRAMES...")
    frames = []
    previous_url = None

    for i, vp in enumerate(visual_prompts):
        frame_prompt = vp.get("frame_prompt", "")
        logger.info(f"  Frame {i+1}/{len(visual_prompts)}...")

        url = generate_image(
            prompt=frame_prompt,
            reference_url=previous_url,
        )

        # Retry once with simplified prompt if first attempt fails
        if not url:
            logger.warning(f"⚠️ Frame {i+1} failed, retrying with simplified prompt...")
            url = generate_image(
                prompt=frame_prompt[:300],
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

    if len(frames) < 3:
        logger.error("❌ Not enough frames (need at least 3)!")
        return None

    # ── 5. Generate VEO3 narrated video clips ─────────────────────────────
    # VEO3 generates actual AI voice narration from the prompt text
    # Each clip gets a narration segment spoken by VEO3's AI voice
    logger.info(f"\n🎬 GENERATING {len(frames)-1} VEO3 NARRATED CLIPS...")
    clips = []

    for i in range(len(frames) - 1):
        start_frame = frames[i]
        end_frame = frames[i + 1] if (i + 1) < len(frames) else None
        vp = visual_prompts[i] if i < len(visual_prompts) else visual_prompts[-1]

        # Build VEO3 prompt with narration
        visual_desc = vp.get("video_prompt", "Cinematic space visualization.")

        # Get narration segment for this clip
        if i < len(narration_segments):
            narr_text = narration_segments[i]
        elif narration:
            narr_text = narration
        else:
            narr_text = f"Exploring the wonders of {daily_topic['topic'][:50]}."

        # VEO3 prompt format: visual description + narration script
        veo_prompt = (
            f"{visual_desc} "
            f"A calm, authoritative male narrator speaks in English: \"{narr_text}\" "
            f"Cinematic orchestral background music. "
            f"No text on screen. No subtitles. Voice-over only."
        )

        logger.info(f"  Clip {i+1}: VEO3 narrated")
        logger.info(f"    Narration: {narr_text[:80]}...")

        video_url = generate_veo_video(
            prompt=veo_prompt,
            image_url=start_frame["url"],
            duration="8",
        )

        if not video_url:
            # Fallback: Try Kling video generation
            logger.warning(f"⚠️ VEO3 Clip {i+1} failed, trying Kling fallback...")
            try:
                video_url = generate_video(
                    prompt=visual_desc[:200],
                    start_image_url=start_frame["url"],
                    end_image_url=end_frame["url"] if end_frame else None,
                )
            except Exception as e:
                logger.warning(f"⚠️ Kling fallback error: {e}")
                video_url = None

        if video_url:
            save_path = dirs["clips"] / f"{project_name}_clip_{i+1:02d}.mp4"
            local = download_file(video_url, save_path)
            if local:
                clips.append({"url": video_url, "local_path": local, "clip_number": i + 1})
                logger.info(f"  ✅ Clip {i+1} ready")
        else:
            logger.warning(f"⚠️ Clip {i+1} failed (both VEO3 + Kling)!")

    if len(clips) < 2:
        logger.error("❌ Not enough video clips! Need at least 2.")
        return None

    if len(clips) < 3:
        logger.warning(f"⚠️ Only {len(clips)} clips — video may be short but publishing anyway.")

    # ── 6. FFmpeg merge with crossfades ───────────────────────────────────
    logger.info("\n🔗 MERGING NARRATED CLIPS...")
    if not check_ffmpeg():
        return None

    clip_files = [c["local_path"] for c in clips]
    merged_path = dirs["final"] / f"{project_name}_merged.mp4"
    concatenate_crossfade(clip_files, merged_path, crossfade=0.5)

    final_path = dirs["final"] / f"{project_name}_FINAL.mp4"
    final_export(merged_path, final_path)

    duration = get_video_duration(final_path)
    if duration > duration_cfg["max"]:
        trimmed = dirs["final"] / f"{project_name}_TRIMMED.mp4"
        trim_to_duration(final_path, trimmed, duration_cfg["max"])
        final_path = trimmed

    elapsed = time.time() - start_time
    logger.info(f"\n✅ Narrated video ready: {final_path}")
    logger.info(f"⏱️ Time: {elapsed/60:.1f} minutes")

    # ── 7. Publish ────────────────────────────────────────────────────────
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
