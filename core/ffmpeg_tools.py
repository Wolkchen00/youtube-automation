"""
FFmpeg Tools — Video Assembly & Processing

Merge clips, add crossfades, create seamless loops, export to 9:16 vertical.
"""

import subprocess
from pathlib import Path

from .config import (
    FFMPEG_CRF, FFMPEG_PRESET, FFMPEG_FPS,
    FFMPEG_AUDIO_BITRATE, CROSSFADE_DURATION,
    logger
)


def check_ffmpeg() -> bool:
    """Check if FFmpeg is installed."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            version = result.stdout.split("\n")[0]
            logger.info(f"✅ FFmpeg: {version}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    logger.error("❌ FFmpeg not found!")
    return False


def get_video_duration(video_path: str | Path) -> float:
    """Get video duration in seconds."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(video_path)],
            capture_output=True, text=True, timeout=10
        )
        return float(result.stdout.strip())
    except Exception:
        return 5.0


def concatenate_simple(video_files: list, output_path: str | Path, clips_dir: Path = None) -> Path:
    """Concatenate videos without transitions."""
    import shutil
    output_path = Path(output_path)

    if len(video_files) == 0:
        logger.error("❌ No video files to concatenate!")
        return output_path

    if len(video_files) == 1:
        shutil.copy2(str(video_files[0]), str(output_path))
        logger.info(f"📋 Single clip copied: {output_path}")
        return output_path

    temp_dir = clips_dir or output_path.parent
    concat_list = temp_dir / "concat_list.txt"

    with open(concat_list, "w", encoding="utf-8") as f:
        for video in video_files:
            escaped = str(Path(video).resolve()).replace("'", "'\\''")
            f.write(f"file '{escaped}'\n")

    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c:v", "libx264", "-crf", FFMPEG_CRF,
        "-preset", FFMPEG_PRESET,
        "-c:a", "aac", "-b:a", FFMPEG_AUDIO_BITRATE,
        "-r", FFMPEG_FPS,
        str(output_path)
    ]

    logger.info(f"🔗 Concatenating {len(video_files)} clips...")
    subprocess.run(cmd, capture_output=True, check=True)
    logger.info(f"✅ Merged: {output_path}")

    # Cleanup
    concat_list.unlink(missing_ok=True)
    return output_path


def concatenate_crossfade(
    video_files: list,
    output_path: str | Path,
    crossfade: float = None
) -> Path:
    """Concatenate videos with crossfade transitions."""
    cf = crossfade or CROSSFADE_DURATION
    output_path = Path(output_path)

    if len(video_files) < 2:
        import shutil
        shutil.copy2(str(video_files[0]), str(output_path))
        return output_path

    durations = [get_video_duration(v) for v in video_files]
    inputs = []
    for video in video_files:
        inputs.extend(["-i", str(video)])

    # Build video crossfade filter
    vfilter_parts = []
    afilter_parts = []
    running_offset = durations[0] - cf

    vfilter_parts.append(
        f"[0:v][1:v]xfade=transition=fade:duration={cf}:offset={running_offset:.2f}[v01]"
    )
    afilter_parts.append(
        f"[0:a][1:a]acrossfade=d={cf}:c1=tri:c2=tri[a01]"
    )

    for i in range(2, len(video_files)):
        vprev = f"v{str(i-2).zfill(2)}{str(i-1).zfill(2)}" if i > 2 else "v01"
        aprev = f"a{str(i-2).zfill(2)}{str(i-1).zfill(2)}" if i > 2 else "a01"
        is_last = (i == len(video_files) - 1)
        vcurr = "vout" if is_last else f"v{str(i-1).zfill(2)}{str(i).zfill(2)}"
        acurr = "aout" if is_last else f"a{str(i-1).zfill(2)}{str(i).zfill(2)}"
        running_offset += durations[i] - cf
        vfilter_parts.append(
            f"[{vprev}][{i}:v]xfade=transition=fade:duration={cf}:offset={running_offset:.2f}[{vcurr}]"
        )
        afilter_parts.append(
            f"[{aprev}][{i}:a]acrossfade=d={cf}:c1=tri:c2=tri[{acurr}]"
        )

    vfinal = "vout" if len(video_files) > 2 else "v01"
    afinal = "aout" if len(video_files) > 2 else "a01"

    full_filter = ";".join(vfilter_parts + afilter_parts)

    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", full_filter,
        "-map", f"[{vfinal}]",
        "-map", f"[{afinal}]",
        "-c:v", "libx264", "-crf", FFMPEG_CRF,
        "-preset", FFMPEG_PRESET,
        "-c:a", "aac", "-b:a", FFMPEG_AUDIO_BITRATE,
        "-r", FFMPEG_FPS,
        str(output_path)
    ]

    logger.info(f"🔗 Crossfade merge (with audio): {len(video_files)} clips, cf={cf}s")
    try:
        subprocess.run(cmd, capture_output=True, check=True)
    except subprocess.CalledProcessError:
        # Fallback: some clips may not have audio, try video-only crossfade
        logger.warning("⚠️ Audio crossfade failed, merging video only with silent audio...")
        cmd_fallback = ["ffmpeg", "-y"] + inputs + [
            "-filter_complex", ";".join(vfilter_parts),
            "-map", f"[{vfinal}]",
            "-c:v", "libx264", "-crf", FFMPEG_CRF,
            "-preset", FFMPEG_PRESET,
            "-r", FFMPEG_FPS,
            str(output_path)
        ]
        subprocess.run(cmd_fallback, capture_output=True, check=True)

    logger.info(f"✅ Merged: {output_path}")
    return output_path


def make_loop_video(input_path: str | Path, output_path: str | Path) -> Path:
    """Create a seamless loop by appending reversed video.

    Result: forward + reversed = starts and ends on the same frame.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    temp_reversed = input_path.parent / f"{input_path.stem}_reversed.mp4"

    # Reverse the video
    cmd_reverse = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-vf", "reverse",
        "-af", "areverse",
        "-c:v", "libx264", "-crf", FFMPEG_CRF,
        str(temp_reversed)
    ]
    logger.info("🔄 Creating reversed copy...")
    subprocess.run(cmd_reverse, capture_output=True, check=True)

    # Merge forward + reversed
    concatenate_simple([input_path, temp_reversed], output_path, clips_dir=input_path.parent)

    # Cleanup
    temp_reversed.unlink(missing_ok=True)
    logger.info(f"🔁 Loop video created: {output_path}")
    return output_path


def trim_to_duration(
    input_path: str | Path,
    output_path: str | Path,
    max_duration: float
) -> Path:
    """Trim video to max_duration seconds if it exceeds."""
    input_path = Path(input_path)
    output_path = Path(output_path)
    current = get_video_duration(input_path)

    if current <= max_duration:
        import shutil
        shutil.copy2(str(input_path), str(output_path))
        return output_path

    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-t", str(max_duration),
        "-c:v", "libx264", "-crf", FFMPEG_CRF,
        "-c:a", "aac",
        str(output_path)
    ]
    logger.info(f"✂️ Trimming {current:.1f}s → {max_duration}s")
    subprocess.run(cmd, capture_output=True, check=True)
    return output_path


def final_export(
    input_path: str | Path,
    output_path: str | Path
) -> Path:
    """Final export: 1080x1920 vertical, H.264, 30fps, AAC audio."""
    output_path = Path(output_path)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-c:v", "libx264", "-crf", FFMPEG_CRF,
        "-preset", FFMPEG_PRESET,
        "-c:a", "aac", "-b:a", FFMPEG_AUDIO_BITRATE,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
        "-r", FFMPEG_FPS,
        "-movflags", "+faststart",
        str(output_path)
    ]

    logger.info("🏁 Final export starting...")
    subprocess.run(cmd, capture_output=True, check=True)

    size_mb = output_path.stat().st_size / (1024 * 1024)
    duration = get_video_duration(output_path)
    logger.info(f"✅ FINAL VIDEO READY!")
    logger.info(f"   📁 File: {output_path}")
    logger.info(f"   📐 Size: {size_mb:.1f} MB")
    logger.info(f"   ⏱️ Duration: {duration:.1f}s")
    return output_path


def add_text_overlay(
    input_path: str | Path,
    output_path: str | Path,
    text: str,
    duration: float = 3.0,
    fontsize: int = 42,
    fade_in: float = 0.5,
    fade_out: float = 0.5,
) -> Path:
    """Add a text overlay to the first N seconds of a video.

    Text appears bottom-center with white font, black shadow,
    fades in and fades out. Used for location names in ShadowedHistory.

    Args:
        input_path: Input video file path
        output_path: Output video file path
        text: Text to display (e.g., "Cappadocia, Turkey")
        duration: How long the text stays on screen (seconds)
        fontsize: Font size for the text
        fade_in: Fade-in duration (seconds)
        fade_out: Fade-out duration (seconds)
    """
    output_path = Path(output_path)

    # Escape special characters for FFmpeg drawtext
    safe_text = text.replace("'", "'\\''").replace(":", "\\:")

    # drawtext filter with fade in/out using alpha expression
    # Text appears at bottom-center, white with black shadow
    fade_end = duration - fade_out
    alpha_expr = (
        f"if(lt(t\\,{fade_in})\\,t/{fade_in}\\,"
        f"if(lt(t\\,{fade_end})\\,1\\,"
        f"if(lt(t\\,{duration})\\,(1-(t-{fade_end})/{fade_out})\\,0)))"
    )

    drawtext_filter = (
        f"drawtext=text='{safe_text}'"
        f":fontsize={fontsize}"
        f":fontcolor=white"
        f":shadowcolor=black@0.7:shadowx=2:shadowy=2"
        f":x=(w-text_w)/2"
        f":y=h-th-100"
        f":alpha='{alpha_expr}'"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vf", drawtext_filter,
        "-c:v", "libx264", "-crf", FFMPEG_CRF,
        "-preset", FFMPEG_PRESET,
        "-c:a", "copy",
        str(output_path)
    ]

    logger.info(f"📝 Adding text overlay: '{text}' ({duration}s)")
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        logger.info(f"✅ Text overlay added: {output_path}")
    except subprocess.CalledProcessError as e:
        logger.warning(f"⚠️ Text overlay failed (using original): {e}")
        import shutil
        shutil.copy2(str(input_path), str(output_path))

    return output_path


def prepend_teaser(input_path: str | Path, output_path: str | Path = None,
                   teaser_duration: float = 1.0) -> Path:
    """Prepend the last N seconds of the video as a 'result teaser' retention hook.

    Takes the final `teaser_duration` seconds and places them at the very start,
    creating a 'wait for it...' effect that hooks viewers immediately.
    """
    input_path = Path(input_path)
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_teased{input_path.suffix}"
    output_path = Path(output_path)

    total_duration = get_video_duration(input_path)
    if total_duration <= teaser_duration * 2:
        logger.warning(f"⚠️ Video too short for teaser ({total_duration:.1f}s), skipping")
        import shutil
        shutil.copy2(str(input_path), str(output_path))
        return output_path

    teaser_start = total_duration - teaser_duration

    # Extract teaser (last N seconds)
    teaser_path = input_path.parent / f"_teaser_clip{input_path.suffix}"
    cmd_teaser = [
        "ffmpeg", "-y",
        "-ss", str(teaser_start),
        "-i", str(input_path),
        "-t", str(teaser_duration),
        "-c:v", "libx264", "-crf", FFMPEG_CRF,
        "-preset", "fast",
        "-c:a", "aac", "-b:a", FFMPEG_AUDIO_BITRATE,
        str(teaser_path)
    ]

    # Concatenate: teaser + original
    concat_list = input_path.parent / "_teaser_concat.txt"

    try:
        subprocess.run(cmd_teaser, capture_output=True, check=True, timeout=120)

        concat_list.write_text(
            f"file '{teaser_path.name}'\nfile '{input_path.name}'\n",
            encoding="utf-8"
        )

        cmd_concat = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_list),
            "-c:v", "libx264", "-crf", FFMPEG_CRF,
            "-preset", FFMPEG_PRESET,
            "-c:a", "aac", "-b:a", FFMPEG_AUDIO_BITRATE,
            str(output_path)
        ]
        subprocess.run(cmd_concat, capture_output=True, check=True, timeout=120)
        logger.info(f"🎬 Retention teaser added: {teaser_duration}s hook → {output_path.name}")
    except subprocess.CalledProcessError as e:
        logger.warning(f"⚠️ Teaser prepend failed (using original): {e}")
        import shutil
        shutil.copy2(str(input_path), str(output_path))
    finally:
        teaser_path.unlink(missing_ok=True)
        concat_list.unlink(missing_ok=True)

    return output_path
