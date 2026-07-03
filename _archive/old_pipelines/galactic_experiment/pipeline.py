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

from core.config import CHANNEL_DIRS, CHANNEL_DURATION, CHANNEL_VEO_MODEL, CINEMATIC_VIDEO_MODEL_LITE, PIPELINE_TIMEOUT_MINUTES, logger
from core.kie_api import generate_image, generate_video, generate_veo_video, check_credit, ServerError
from core.imgbb import upload_to_imgbb
from core.narration import create_narration_for_channel
from core.ffmpeg_tools import (
    check_ffmpeg, concatenate_simple, concatenate_crossfade, final_export,
    get_video_duration, trim_to_duration, make_loop_video, prepend_teaser
)
from core.uploader import publish_video
from core.script_generator import generate_script, generate_visual_prompts
from core.utils import download_file, sanitize_filename
from core.video_vault import vault

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

    # Trending hook — boost title with daily trending keywords
    from core.trending import enhance_title_with_trend, get_trending_hashtags
    title = enhance_title_with_trend(title, CHANNEL)
    trending_tags = get_trending_hashtags(CHANNEL)
    if trending_tags:
        hashtags = f"{hashtags} {trending_tags}"

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
                "duration_seconds": 10,
            })

    project_name = sanitize_filename(title)

    # ── 4. Generate frames ────────────────────────────────────────────────
    logger.info(f"\n🖼️ GENERATING {len(visual_prompts)} COSMIC FRAMES...")
    frames = []
    previous_url = None

    for i, vp in enumerate(visual_prompts):
        # Pipeline timeout check
        elapsed_min = (time.time() - start_time) / 60
        if elapsed_min > PIPELINE_TIMEOUT_MINUTES * 0.5:
            logger.warning(f"⏰ Pipeline timeout ({elapsed_min:.0f}min), stopping frames")
            break

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

    # ── 5. Generate video clips — KLING PRIMARY (fast, reliable) ─────────
    # VEO3 was too slow (10min+ per clip, frequent timeouts).
    # Kling generates clips in 1-2 min. Narration added via Gemini TTS after.
    logger.info(f"\n🎬 GENERATING {len(frames)-1} CLIPS (Kling primary)...")
    clips = []

    for i in range(len(frames) - 1):
        # Pipeline timeout check
        elapsed_min = (time.time() - start_time) / 60
        if elapsed_min > PIPELINE_TIMEOUT_MINUTES * 0.75:
            logger.warning(f"⏰ Pipeline timeout ({elapsed_min:.0f}min), stopping clips")
            break

        start_frame = frames[i]
        vp = visual_prompts[i] if i < len(visual_prompts) else visual_prompts[-1]

        visual_desc = vp.get("video_prompt", "Cinematic space visualization.")

        logger.info(f"  Clip {i+1}: Kling I2V")

        video_url = None

        # Primary: Kling (fast, ~1-2 min per clip)
        try:
            video_url = generate_video(
                prompt=visual_desc[:200],
                start_image_url=start_frame["url"],
            )
        except ServerError as e:
            logger.warning(f"⚠️ Kling server error: {e} — trying shorter prompt")
            try:
                video_url = generate_video(
                    prompt=visual_desc[:100],
                    start_image_url=start_frame["url"],
                )
            except Exception:
                video_url = None
        except Exception as e:
            logger.warning(f"⚠️ Kling error: {e}")
            video_url = None

        # Last resort fallback: VEO3 Lite (7min timeout)
        if not video_url:
            logger.warning(f"⚠️ Kling Clip {i+1} failed, trying VEO3 fallback (7min timeout)...")
            video_url = generate_veo_video(
                prompt=f"{visual_desc[:150]} Cosmic space documentary.",
                image_url=start_frame["url"],
                duration="10",
                model=CINEMATIC_VIDEO_MODEL_LITE,
                max_poll_attempts=28,  # 28 x 15s = ~7min
            )

        if video_url:
            save_path = dirs["clips"] / f"{project_name}_clip_{i+1:02d}.mp4"
            local = download_file(video_url, save_path)
            if local:
                clips.append({"url": video_url, "local_path": local, "clip_number": i + 1})
                logger.info(f"  ✅ Clip {i+1} ready")
        else:
            logger.warning(f"⚠️ Clip {i+1} failed (both Kling + VEO3)!")

    if len(clips) < 2:
        logger.error("❌ Not enough video clips! Need at least 2.")
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
                    "topic": daily_topic["topic"],
                    "title": vault_video["title"],
                    "vault_fallback": True,
                    "duration_min": round((time.time() - start_time) / 60, 1),
                }
        return None

    if len(clips) < 3:
        logger.warning(f"⚠️ Only {len(clips)} clips — video may be short but publishing anyway.")

    # ── 6. FFmpeg merge — hard cut (cleaner transitions) ──────────────────
    logger.info("\n🔗 MERGING NARRATED CLIPS...")
    if not check_ffmpeg():
        return None

    clip_files = [c["local_path"] for c in clips]
    merged_path = dirs["final"] / f"{project_name}_merged.mp4"
    concatenate_simple(clip_files, merged_path)  # hard cut — space narration flows naturally

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

    # ── 6b. TTS Cosmic Narration (replaces VEO3 built-in voice) ──────────
    full_narration = narration
    if not full_narration and narration_segments:
        full_narration = " ".join(narration_segments)
    if full_narration:
        logger.info("\n🎙️ ADDING COSMIC NARRATION (Gemini TTS)...")
        try:
            from core.ffmpeg_tools import mix_voiceover
            narration_wav = dirs["final"] / f"{project_name}_narration.wav"
            audio_path, style_name = create_narration_for_channel(
                channel=CHANNEL,
                narration_text=full_narration,
                output_path=narration_wav,
            )
            if audio_path and audio_path.exists():
                narrated_path = dirs["final"] / f"{project_name}_NARRATED.mp4"
                mix_voiceover(str(final_path), str(audio_path), str(narrated_path),
                              voice_volume=1.0, bg_duck=0.15)
                if narrated_path.exists() and narrated_path.stat().st_size > 0:
                    final_path = narrated_path
                    logger.info(f"🎙️ Cosmic narration added ({style_name})")
        except Exception as e:
            logger.warning(f"⚠️ Narration step skipped: {e}")

    # ── 6b. Growth: Seamless Loop + Retention Teaser ────────────────────────
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

    # ── 7. Save to Vault & Publish ─────────────────────────────────────────
    full_description = f"{hook}\n\n{description}\n\n{hashtags}"
    clip_urls = [c.get("url", "") for c in clips if c.get("url")]
    vault.save_video(
        channel=CHANNEL, title=title, description=full_description,
        video_path=str(final_path), clip_urls=clip_urls,
    )

    if not skip_upload:
        logger.info("\n📤 PUBLISHING...")
        results = publish_video(
            video_path=final_path, title=title,
            description=full_description, channel_name=CHANNEL,
        )
        logger.info(f"📊 Publish results: {results}")
        if any(v for v in results.values() if v):
            vault.mark_published(CHANNEL, title)
    else:
        logger.info("⏭️ Upload skipped.")

    report = {
        "date": today, "channel": CHANNEL, "topic": daily_topic["topic"],
        "title": title, "frames": len(frames), "clips": len(clips),
        "duration_min": round(elapsed / 60, 1), "final_video": str(final_path),
    }
    logger.info(f"\n🎉 GALACTIC EXPERIMENT DAILY COMPLETE: {title}")
    return report
