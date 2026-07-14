"""
FFmpeg Tools — Video Assembly & Processing

Merge clips, add crossfades, create seamless loops, export to 9:16 vertical.
"""

import subprocess
from pathlib import Path

from .env import (
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


def get_video_height(video_path: str | Path) -> int:
    """Get video height in pixels (0 on failure)."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=height", "-of", "csv=p=0", str(video_path)],
            capture_output=True, text=True, timeout=10
        )
        return int(result.stdout.strip().splitlines()[0])
    except Exception:
        return 0


def extract_last_frame(video_path: str | Path, output_path: str | Path = None) -> Path | None:
    """Extract the final frame of a video as a PNG.

    Used for 'endless journey' chaining: the last frame of one clip becomes
    the first frame (start image) of the next clip/part, so the motion flows
    seamlessly across shots and across episodes.
    """
    video_path = Path(video_path)
    if output_path is None:
        output_path = video_path.parent / f"{video_path.stem}_lastframe.png"
    output_path = Path(output_path)
    try:
        # -sseof seeks from end; grab the very last decodable frame
        subprocess.run(
            ["ffmpeg", "-y", "-sseof", "-0.5", "-i", str(video_path),
             "-update", "1", "-frames:v", "1", "-q:v", "2", str(output_path)],
            capture_output=True, check=True, timeout=60
        )
        if output_path.exists() and output_path.stat().st_size > 0:
            return output_path
    except Exception as e:
        logger.warning(f"⚠️ Last-frame extraction failed: {e}")
    return None


def sample_frames(video_path: str | Path, count: int = 8, width: int = 720,
                  out_dir: str | Path = None, prefix: str = "qcframe") -> list[Path]:
    """Klip boyunca eşit aralıklı `count` kare çıkar (JPEG, `width` px genişlik).

    Critic-QC için: kareler Gemini vision'a denetim girdisi olur. Kare sayısı
    süreden bağımsız sabittir — kısa klipte sıklaşır, uzun klipte seyrekleşir.
    """
    video_path = Path(video_path)
    out_dir = Path(out_dir) if out_dir else video_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    pattern = out_dir / f"{prefix}_%02d.jpg"
    duration = max(get_video_duration(video_path), 0.5)
    fps = count / duration
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(video_path),
             "-vf", f"fps={fps:.6f},scale={int(width)}:-2",
             "-frames:v", str(int(count)), "-q:v", "3", str(pattern)],
            capture_output=True, check=True, timeout=120
        )
    except Exception as e:
        logger.warning(f"⚠️ Frame sampling failed ({video_path.name}): {e}")
    frames = sorted(out_dir.glob(f"{prefix}_*.jpg"))
    return [f for f in frames if f.stat().st_size > 0]


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


def concatenate_audio_smooth(
    video_files: list,
    output_path: str | Path,
    clips_dir: Path = None,
    fade: float = 0.25,
    normalize: bool = True,
) -> Path:
    """Concatenate clips with HARD video cuts but SMOOTHED audio at every cut.

    Why: each AI shot carries its own ambient/score, so a plain concat makes the
    soundscape 'pop' and jump in loudness (often ~8-10 dB) at every transition,
    and leaves an audible gap when one clip ends quiet and the next starts loud.

    Fix, per clip, before joining:
      • loudness-normalise the audio (EBU R128) so shot-to-shot levels match,
      • short afade in + afade out so each boundary decays/rises instead of cutting.

    Video is concatenated as straight cuts (the visuals are fine as-is) and the
    fades live *inside* each clip's own duration, so total length is unchanged and
    audio stays in sync with video. Pair this with a continuous music bed
    (mix_background_music) to fully mask the seams.

    Falls back to a plain concat on any ffmpeg error so the nightly run never breaks.
    """
    output_path = Path(output_path)
    files = [Path(v) for v in video_files]
    if len(files) <= 1:
        return concatenate_simple(files, output_path, clips_dir=clips_dir)

    durations = [get_video_duration(f) for f in files]
    inputs = []
    for f in files:
        inputs.extend(["-i", str(f)])

    vfilters, afilters = [], []
    for i, d in enumerate(durations):
        # normalise geometry so the concat filter accepts every segment
        vfilters.append(f"[{i}:v]fps={FFMPEG_FPS},setsar=1,format=yuv420p[v{i}]")
        chain = []
        if normalize:
            chain.append("loudnorm=I=-18:TP=-1.5:LRA=11")
        out_st = max(0.0, d - fade)
        chain.append(f"afade=t=in:st=0:d={fade:.2f}")
        chain.append(f"afade=t=out:st={out_st:.2f}:d={fade:.2f}")
        afilters.append(f"[{i}:a]{','.join(chain)}[a{i}]")

    concat_in = "".join(f"[v{i}][a{i}]" for i in range(len(files)))
    full_filter = ";".join(
        vfilters + afilters + [f"{concat_in}concat=n={len(files)}:v=1:a=1[v][a]"]
    )

    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", full_filter,
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-crf", FFMPEG_CRF, "-preset", FFMPEG_PRESET,
        "-c:a", "aac", "-b:a", FFMPEG_AUDIO_BITRATE,
        "-r", FFMPEG_FPS,
        str(output_path),
    ]
    logger.info(f"🔗 Smooth-audio concat: {len(files)} clips (fade={fade}s, norm={normalize})")
    try:
        subprocess.run(cmd, capture_output=True, check=True, timeout=600)
        logger.info(f"✅ Merged (smooth audio): {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        logger.warning(f"⚠️ Smooth concat failed ({e}); falling back to simple concat")
        return concatenate_simple(files, output_path, clips_dir=clips_dir)


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


def concatenate_video_crossfade(
    video_files: list,
    output_path: str | Path,
    fade: float = 0.6,
) -> Path:
    """Klipleri sinematik VIDEO crossfade (xfade) ile birleştir — the__footnote tarzı
    dönem-daldırma kurgusu: her sahne bir sonrakinin içinde erir.

    Sesle uğraşmaz: kaynak sesler ATILIR, yerine sessiz bir stereo iz basılır.
    Bu yol, müziğin post'ta replace_original=True ile TEK ses olduğu anlatımsız
    seriler için tasarlandı — acrossfade'in 'sessiz/ses-siz klip = filtre çöker'
    tuzağına hiç girmez. xfade iki girdinin birebir aynı boyut/fps'te olmasını
    şart koştuğu için tüm girdiler önce 1080x1920'ye normalize edilir.
    Toplam süre = Σ süre − (N−1)·fade → çağıran taraf (produce) çekim ofsetlerini
    aynı kaymayla hizalamak zorundadır. Hata FIRLATIR — çağıran düz kesmeye düşer.
    """
    output_path = Path(output_path)
    files = [Path(v) for v in video_files]
    if len(files) < 2:
        import shutil
        shutil.copy2(str(files[0]), str(output_path))
        return output_path

    durations = [get_video_duration(f) for f in files]
    if any(d <= fade * 2 for d in durations):
        raise ValueError(f"crossfade için klip çok kısa (fade={fade}s, süreler="
                         f"{[round(d, 2) for d in durations]})")

    inputs = []
    for f in files:
        inputs.extend(["-i", str(f)])
    total = sum(durations) - fade * (len(files) - 1)

    parts = []
    for i in range(len(files)):
        parts.append(
            f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
            f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps={FFMPEG_FPS},setsar=1,"
            f"format=yuv420p[n{i}]"
        )
    prev, cum = "n0", 0.0
    for i in range(1, len(files)):
        cum += durations[i - 1]
        off = max(0.0, cum - i * fade)
        cur = "vout" if i == len(files) - 1 else f"x{i}"
        parts.append(f"[{prev}][n{i}]xfade=transition=fade:duration={fade:.2f}:"
                     f"offset={off:.3f}[{cur}]")
        prev = cur

    cmd = (["ffmpeg", "-y"] + inputs + [
        "-f", "lavfi", "-t", f"{total:.3f}",
        "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-filter_complex", ";".join(parts),
        "-map", "[vout]", "-map", f"{len(files)}:a",
        "-c:v", "libx264", "-crf", FFMPEG_CRF, "-preset", FFMPEG_PRESET,
        "-c:a", "aac", "-b:a", FFMPEG_AUDIO_BITRATE,
        "-r", FFMPEG_FPS, "-shortest",
        str(output_path),
    ])
    logger.info(f"🔗 Crossfade (video-only) merge: {len(files)} klip, fade={fade}s")
    subprocess.run(cmd, capture_output=True, check=True, timeout=900)
    if not output_path.exists() or output_path.stat().st_size == 0:
        raise RuntimeError("crossfade çıktısı boş")
    logger.info(f"✅ Merged (crossfade): {output_path}")
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


def upscale_lanczos(
    input_path: str | Path,
    output_path: str | Path,
    factor: int = 2,
    maxrate: str = "10M",
) -> Path:
    """Yerel 4K büyütme (Topaz API yedeği): lanczos ×factor + hafif keskinleştirme.

    Gerçek detay sentezlemez ama YouTube'un 4K bitrate merdivenini tetikler —
    aynı içerik 1080p yüklemeye göre gözle görülür daha temiz VP9/AV1 encode alır.
    maxrate, Upload-Post'un ~80MB gövde limitine sığmak için bitrate'i kapaklar.
    """
    output_path = Path(output_path)
    vf = (f"scale=iw*{int(factor)}:ih*{int(factor)}:flags=lanczos,"
          "unsharp=5:5:0.4:5:5:0.0")
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vf", vf,
        "-c:v", "libx264", "-crf", "18",
        "-maxrate", maxrate, "-bufsize", "20M",
        "-preset", "medium",
        "-c:a", "copy",
        "-movflags", "+faststart",
        str(output_path),
    ]
    logger.info(f"🔍 Lanczos ×{factor} upscale kodlanıyor...")
    subprocess.run(cmd, capture_output=True, check=True, timeout=1800)
    return output_path


def cap_bitrate(
    input_path: str | Path,
    output_path: str | Path,
    maxrate: str = "9500k",
    crf: str = "18",
    preset: str = "fast",
) -> Path:
    """Çözünürlüğü KORUYARAK bitrate'i kapakla (upload limitlerine sığdırma).

    Topaz 4K çıktısı ~100 Mbps gelebiliyor (4sn ≈ 50MB) — Upload-Post ~80MB üstü
    gövdeleri kesiyor. 9500k @ 60s ≈ 72MB → limite güvenle sığar; YouTube zaten
    kendi 4K VP9/AV1 encode'unu üretiyor, görünür kalite kaybı olmaz."""
    output_path = Path(output_path)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-c:v", "libx264", "-crf", crf,
        "-maxrate", maxrate, "-bufsize", "20M",
        "-preset", preset,
        "-c:a", "copy",
        "-movflags", "+faststart",
        str(output_path),
    ]
    subprocess.run(cmd, capture_output=True, check=True, timeout=1800)
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


def make_loop_video(input_path: str | Path, output_path: str | Path = None) -> Path:
    """Create a seamless loop by appending the video in reverse.

    Result: original + reversed = seamless infinite replay effect.
    """
    input_path = Path(input_path)
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_loop{input_path.suffix}"
    output_path = Path(output_path)

    reversed_path = input_path.parent / f"_reversed{input_path.suffix}"

    try:
        cmd_reverse = [
            "ffmpeg", "-y",
            "-i", str(input_path),
            "-vf", "reverse",
            "-af", "areverse",
            "-c:v", "libx264", "-crf", FFMPEG_CRF,
            "-preset", "fast",
            "-c:a", "aac", "-b:a", FFMPEG_AUDIO_BITRATE,
            str(reversed_path)
        ]
        subprocess.run(cmd_reverse, capture_output=True, check=True, timeout=180)

        concat_list = input_path.parent / "_loop_concat.txt"
        concat_list.write_text(
            f"file '{input_path.name}'\nfile '{reversed_path.name}'\n",
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
        subprocess.run(cmd_concat, capture_output=True, check=True, timeout=180)
        logger.info(f"♻️ Seamless loop created: {output_path.name}")
    except subprocess.CalledProcessError as e:
        logger.warning(f"⚠️ Loop creation failed (using original): {e}")
        import shutil
        shutil.copy2(str(input_path), str(output_path))
    finally:
        reversed_path.unlink(missing_ok=True)
        if (input_path.parent / "_loop_concat.txt").exists():
            (input_path.parent / "_loop_concat.txt").unlink(missing_ok=True)

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


def mix_background_music(
    video_path: str | Path,
    music_path: str | Path,
    output_path: str | Path = None,
    music_volume: float = 0.18,
    replace_original: bool = False,
) -> Path:
    """Mix a CONTINUOUS background-music bed into a video.

    The bed is what stops scene transitions from sounding like the audio
    'drops out' — it plays unbroken under the whole episode and only fades at
    the very start/end. To guarantee full coverage even when the source clip is
    short (Lyria gives 30s clips), the music is LOOPED to the video length, then
    trimmed, volume-set and faded.

    replace_original=False → amix (normalize=0) keeps program audio + adds bed.
    replace_original=True  → the video's ORIGINAL audio is DROPPED and the looped
        music becomes the SOLE soundtrack. Used for pure-visual channels (no
        narration) where each AI shot's own gappy ambient is the very thing that
        makes cuts 'pop'/go silent — a single continuous track removes every seam.

    Args:
        video_path: Input video file
        music_path: Background music audio file (may be shorter than the video)
        output_path: Output file (default: _music suffix)
        music_volume: Music volume (bed ≈0.18-0.3; as sole track ≈0.9)
        replace_original: If True, output audio = looped music only.

    Returns:
        Path to the mixed video.
    """
    video_path = Path(video_path)
    music_path = Path(music_path)
    if output_path is None:
        output_path = video_path.parent / f"{video_path.stem}_music{video_path.suffix}"
    output_path = Path(output_path)

    try:
        vid_duration = get_video_duration(video_path)
        fade_out_st = max(0.0, vid_duration - 1.5)

        bed = (f"[1:a]atrim=0:{vid_duration:.2f},asetpts=PTS-STARTPTS,"
               f"volume={music_volume},"
               f"afade=t=in:st=0:d=1.0,afade=t=out:st={fade_out_st:.2f}:d=1.5")
        if replace_original:
            # Music is the ONLY audio → no per-shot seams can exist.
            full_filter = f"{bed}[aout]"
        else:
            # Continuous bed UNDER the existing program audio.
            full_filter = f"{bed}[bg];[0:a][bg]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[aout]"

        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-stream_loop", "-1", "-i", str(music_path),   # loop bed to cover full video
            "-filter_complex", full_filter,
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", FFMPEG_AUDIO_BITRATE,
            "-shortest",
            str(output_path)
        ]

        subprocess.run(cmd, capture_output=True, check=True, timeout=180)
        logger.info(f"🎵 Music {'(sole track)' if replace_original else 'bed'} mixed "
                    f"(looped, vol={music_volume}): {output_path.name}")
    except subprocess.CalledProcessError as e:
        logger.warning(f"⚠️ Music mix failed (using original): {e}")
        import shutil
        shutil.copy2(str(video_path), str(output_path))

    return output_path


def _find_font(mono: bool = True) -> str | None:
    """Find a usable TTF font for drawtext (GitHub Actions ubuntu + local Windows/macOS).

    mono=True prefers a monospace face (CCTV/timestamp look)."""
    mono_first = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",   # ubuntu runner
        "C:/Windows/Fonts/consola.ttf",                          # Windows (Consolas)
        "C:/Windows/Fonts/lucon.ttf",
        "/System/Library/Fonts/Menlo.ttc",                       # macOS
    ]
    prop_first = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    candidates = (mono_first + prop_first) if mono else (prop_first + mono_first)
    for c in candidates:
        if Path(c).exists():
            return c
    return None


def _drawtext_escape(text: str) -> str:
    """Escape free text for a single-quoted drawtext value (args passed via
    subprocess list — only ffmpeg's own filtergraph/expansion parsing applies)."""
    s = (text or "").replace("\\", "\\\\")
    s = s.replace("'", "’")          # real apostrophes → typographic (no quote wars)
    s = s.replace(":", "\\:").replace("%", "%%")
    return s


def trim_head_tail(
    input_path: str | Path,
    output_path: str | Path,
    head: float = 0.3,
    tail: float = 0.3,
) -> Path:
    """Cut the first/last fraction of a clip before stitching.

    AI-generated shots tend to open and close on a static 'pose' beat, which makes
    a stitched episode read as N mini-videos instead of one flow. Shaving a few
    tenths of a second from both ends drops every clip into the middle of its own
    motion — the single cheapest fluidity win. Falls back to a plain copy when the
    clip is too short to trim safely.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    duration = get_video_duration(input_path)
    keep = duration - head - tail
    if keep < 2.0:
        import shutil
        logger.warning(f"⚠️ Clip too short to micro-trim ({duration:.1f}s) — copied as-is")
        shutil.copy2(str(input_path), str(output_path))
        return output_path

    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{head:.3f}",
        "-i", str(input_path),
        "-t", f"{keep:.3f}",
        "-c:v", "libx264", "-crf", FFMPEG_CRF,
        "-preset", FFMPEG_PRESET,
        "-c:a", "aac", "-b:a", FFMPEG_AUDIO_BITRATE,
        str(output_path)
    ]
    try:
        subprocess.run(cmd, capture_output=True, check=True, timeout=300)
        logger.info(f"✂️ Micro-trim {head:.2f}s/{tail:.2f}s → {output_path.name}")
    except subprocess.CalledProcessError as e:
        logger.warning(f"⚠️ Micro-trim failed (using original): {e}")
        import shutil
        shutil.copy2(str(input_path), str(output_path))
    return output_path


def cctv_overlay(
    input_path: str | Path,
    output_path: str | Path,
    camera_label: str = "CAM 01",
    date_text: str = "",
    epoch: int | None = None,
    fps: int | None = 18,
    grain: int = 7,
    caption: str | None = None,
    caption_start: float = 0.3,
    caption_duration: float = 4.4,
) -> Path:
    """Dress a clip as security-camera footage: ticking timestamp, camera label,
    blinking REC dot, sensor grain, muted colors, low frame rate.

    Applied PER SHOT before concat so each shot's clock starts at its own
    plan-provided time (real CCTV cuts jump minutes — that jump legitimizes any
    small visual discontinuity between AI shots). `epoch` is the UTC epoch the
    ticking HH:MM:SS starts from (drawtext pts:gmtime, %T avoids colon-escape
    pitfalls). The low fps stutter also masks AI motion artifacts.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    # Boyutlar 1080x1920 referansına göre tasarlandı; girdi farklıysa (Seedance
    # klipleri 720x1280 gelir) her şey yüksekliğe oranla ölçeklenir.
    scale = (get_video_height(input_path) or 1920) / 1920.0

    def px(v: float) -> int:
        return max(1, round(v * scale))

    font = _find_font(mono=True)
    # Windows sürücü iki noktası (C:) çift-katman filter parser'ını kırar → '\:' kaçışı
    fontarg = f"fontfile='{font.replace(':', chr(92) + ':')}':" if font else ""

    vf_parts = []
    if fps:
        vf_parts.append(f"fps={int(fps)}")
    vf_parts.append("eq=saturation=0.78:contrast=1.05:brightness=-0.015")
    if grain:
        vf_parts.append(f"noise=alls={int(grain)}:allf=t")

    common = f"shadowcolor=black@0.65:shadowx={px(2)}:shadowy={px(2)}"

    # ● REC — top-left, slow blink
    vf_parts.append(
        f"drawtext={fontarg}text='● REC':fontsize={px(38)}:fontcolor=0xE84040:"
        f"alpha='if(lt(mod(t,1.6),1.0),0.85,0.15)':x={px(44)}:y={px(64)}:{common}"
    )
    # Camera label — top-right
    if camera_label:
        vf_parts.append(
            f"drawtext={fontarg}text='{_drawtext_escape(camera_label)}':fontsize={px(34)}:"
            f"fontcolor=white@0.82:x=w-text_w-{px(44)}:y={px(64)}:{common}"
        )
    # Live-ticking date+time — top-right, second line. %{pts:gmtime:EPOCH}
    # renders 'YYYY-MM-DD HH:MM:SS' and TICKS with the clip (a 4th strftime arg
    # renders empty on ffmpeg 8 — don't add one).
    if epoch is not None:
        vf_parts.append(
            f"drawtext={fontarg}text='%{{pts\\:gmtime\\:{int(epoch)}}}':"
            f"fontsize={px(38)}:fontcolor=white@0.82:x=w-text_w-{px(44)}:y={px(116)}:{common}"
        )
    elif date_text:
        vf_parts.append(
            f"drawtext={fontarg}text='{_drawtext_escape(date_text)}':fontsize={px(38)}:"
            f"fontcolor=white@0.82:x=w-text_w-{px(44)}:y={px(116)}:{common}"
        )
    # Context caption — lower third, boxed, fade in/out. One drawtext PER LINE:
    # ffmpeg 8's text shaping draws embedded '\n' as a missing-glyph box, so
    # multi-line text via a single drawtext is not safe.
    if caption:
        import textwrap
        lines = textwrap.wrap(caption, width=34)
        c_end = caption_start + caption_duration
        c_in = caption_start + 0.4
        c_out = c_end - 0.5
        alpha = (
            f"if(lt(t,{caption_start}),0,"
            f"if(lt(t,{c_in}),(t-{caption_start})/0.4,"
            f"if(lt(t,{c_out}),1,if(lt(t,{c_end}),({c_end}-t)/0.5,0))))"
        )
        cap_fs, cap_gap = px(40), px(26)
        line_h = cap_fs + cap_gap          # boxborderw büyümesin diye satır arası boşluk
        base = f"h-{px(460)}-{len(lines)}*{line_h}"
        for i, line in enumerate(lines):
            vf_parts.append(
                f"drawtext={fontarg}text='{_drawtext_escape(line)}':fontsize={cap_fs}:"
                f"fontcolor=white:box=1:boxcolor=black@0.55:boxborderw={px(13)}:"
                f"x=(w-text_w)/2:y={base}+{i}*{line_h}:alpha='{alpha}'"
            )
    vf_parts.append("format=yuv420p")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vf", ",".join(vf_parts),
        "-c:v", "libx264", "-crf", FFMPEG_CRF,
        "-preset", FFMPEG_PRESET,
        "-c:a", "copy",
        str(output_path)
    ]
    try:
        subprocess.run(cmd, capture_output=True, check=True, timeout=300)
        logger.info(f"📹 CCTV overlay ({camera_label}) → {output_path.name}")
    except subprocess.CalledProcessError as e:
        err = (e.stderr or b"").decode(errors="replace")[-400:] if e.stderr else str(e)
        logger.warning(f"⚠️ CCTV overlay failed (using original): {err}")
        import shutil
        shutil.copy2(str(input_path), str(output_path))
    return output_path


def title_card_overlay(
    input_path: str | Path,
    output_path: str | Path,
    title: str,
    subtitle: str = "",
    duration: float = 3.0,
) -> Path:
    """Burn an opening title card (e.g. artifact name + region/year) over the
    first seconds of a FINISHED episode.

    Applied after the hook teaser is prepended, so the text sits on top of the
    cold-open — the viewer reads WHAT and WHERE on the very first frame. The
    card is fully visible from t=0 (no fade-in: frame one must already carry
    the text) and fades out over the last 0.5s of `duration`. Only drawtext is
    applied — the footage look is not altered (no fps/eq/noise like the CCTV
    dressing).
    """
    import textwrap

    input_path = Path(input_path)
    output_path = Path(output_path)

    # Boyutlar 1080x1920 referansına göre; farklı girdi yüksekliğe oranla ölçeklenir.
    scale = (get_video_height(input_path) or 1920) / 1920.0

    def px(v: float) -> int:
        return max(1, round(v * scale))

    font = _find_font(mono=False)
    # Windows sürücü iki noktası (C:) çift-katman filter parser'ını kırar → '\:' kaçışı
    fontarg = f"fontfile='{font.replace(':', chr(92) + ':')}':" if font else ""

    fade = 0.5
    end = max(fade + 0.1, float(duration))
    hold = end - fade
    # t=0'da TAM görünür; hold'a kadar sabit; 0.5s'de erir (fade-in YOK — ilk kare okunmalı).
    alpha = f"if(lt(t,{hold:.2f}),1,if(lt(t,{end:.2f}),({end:.2f}-t)/{fade},0))"

    title_fs, sub_fs = px(58), px(38)
    title_lh, sub_lh = title_fs + px(24), sub_fs + px(18)

    # Bir drawtext PER LINE (ffmpeg 8 çok-satır tuzağı — cctv_overlay'deki çözümle aynı).
    rows: list[tuple[str, int, str]] = []   # (metin, fontsize, renk)
    for line in textwrap.wrap((title or "").upper(), width=24):
        rows.append((line, title_fs, "white"))
    for line in textwrap.wrap(subtitle or "", width=36):
        rows.append((line, sub_fs, "white@0.92"))
    if not rows:
        import shutil
        shutil.copy2(str(input_path), str(output_path))
        return output_path

    vf_parts = []
    y = px(320)   # Shorts üst ikon bölgesinin altı, alt UI'ın çok üstü
    for text, fs, color in rows:
        vf_parts.append(
            f"drawtext={fontarg}text='{_drawtext_escape(text)}':fontsize={fs}:"
            f"fontcolor={color}:box=1:boxcolor=black@0.45:boxborderw={px(16)}:"
            f"x=(w-text_w)/2:y={y}:alpha='{alpha}'"
        )
        y += title_lh if fs == title_fs else sub_lh
    vf_parts.append("format=yuv420p")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vf", ",".join(vf_parts),
        "-c:v", "libx264", "-crf", FFMPEG_CRF,
        "-preset", FFMPEG_PRESET,
        "-c:a", "copy",
        str(output_path)
    ]
    try:
        subprocess.run(cmd, capture_output=True, check=True, timeout=300)
        logger.info(f"🪧 Title card ('{title}') → {output_path.name}")
    except subprocess.CalledProcessError as e:
        err = (e.stderr or b"").decode(errors="replace")[-400:] if e.stderr else str(e)
        logger.warning(f"⚠️ Title card failed (using original): {err}")
        import shutil
        shutil.copy2(str(input_path), str(output_path))
    return output_path


def fact_captions_overlay(
    input_path: str | Path,
    output_path: str | Path,
    captions: list[dict],
    hold: float = 2.6,
    fade: float = 0.3,
) -> Path:
    """Burn short, synced 'fact captions' into the LOWER third of a finished
    episode — the retention lever for faceless history Shorts. Each item is
    {'text': '45 METERS DEEP', 'at': <second in the FINAL video>, 'hold': <s>?}:
    the caption pops in at `at` (a beat tied to the shot that shows that fact),
    holds ~2.6s and fades out. Sits well below the top title card (different
    screen region) and above the Shorts bottom UI. One ffmpeg pass; one drawtext
    PER LINE (ffmpeg multi-line trap — same as title_card_overlay). On any error
    the original is copied through, so a caption failure never blocks a publish."""
    import textwrap

    input_path = Path(input_path)
    output_path = Path(output_path)
    caps = [c for c in (captions or []) if str(c.get("text") or "").strip()]
    if not caps:
        import shutil
        shutil.copy2(str(input_path), str(output_path))
        return output_path

    scale = (get_video_height(input_path) or 1920) / 1920.0

    def px(v: float) -> int:
        return max(1, round(v * scale))

    font = _find_font(mono=False)
    fontarg = f"fontfile='{font.replace(':', chr(92) + ':')}':" if font else ""

    fs = px(52)
    lh = fs + px(20)
    y_base = px(1330)   # alt-üçlük: üst künye (y≈320) ile alt Shorts UI arasında güvenli
    fade = max(0.1, float(fade))

    vf_parts: list[str] = []
    for c in caps:
        text = str(c.get("text") or "").strip().upper()
        at = max(0.0, float(c.get("at", 0.0)))
        h = max(fade * 2 + 0.2, float(c.get("hold", hold)))
        t0, t1 = at, at + h
        # Yamuk (trapez) alpha: fade-in → tam → fade-out. Tırnak içinde virgül
        # ffmpeg filtergraph'ında literaldir (title_card_overlay'de kanıtlı desen).
        alpha = (f"if(lt(t,{t0:.2f}),0,"
                 f"if(lt(t,{t0 + fade:.2f}),(t-{t0:.2f})/{fade:.2f},"
                 f"if(lt(t,{t1 - fade:.2f}),1,"
                 f"if(lt(t,{t1:.2f}),({t1:.2f}-t)/{fade:.2f},0))))")
        lines = textwrap.wrap(text, width=22) or [text]
        # Blok alt-hizalı: son satır y_base'te, üste doğru yığılır.
        y = y_base - (len(lines) - 1) * lh
        for line in lines:
            vf_parts.append(
                f"drawtext={fontarg}text='{_drawtext_escape(line)}':fontsize={fs}:"
                f"fontcolor=white:box=1:boxcolor=black@0.5:boxborderw={px(18)}:"
                f"x=(w-text_w)/2:y={y}:alpha='{alpha}'"
            )
            y += lh
    vf_parts.append("format=yuv420p")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vf", ",".join(vf_parts),
        "-c:v", "libx264", "-crf", FFMPEG_CRF,
        "-preset", FFMPEG_PRESET,
        "-c:a", "copy",
        str(output_path)
    ]
    try:
        subprocess.run(cmd, capture_output=True, check=True, timeout=300)
        logger.info(f"💬 {len(caps)} fact-caption bindirildi → {output_path.name}")
    except subprocess.CalledProcessError as e:
        err = (e.stderr or b"").decode(errors="replace")[-400:] if e.stderr else str(e)
        logger.warning(f"⚠️ Fact captions failed (using original): {err}")
        import shutil
        shutil.copy2(str(input_path), str(output_path))
    return output_path


def extract_clip(
    input_path: str | Path,
    output_path: str | Path,
    start: float,
    duration: float,
) -> Path:
    """Extract a [start, start+duration] excerpt (re-encoded — frame-exact).

    Used for the retention hook: a beat from the episode's climax shot is
    prepended as a cold-open teaser."""
    input_path = Path(input_path)
    output_path = Path(output_path)
    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{max(0.0, start):.3f}",
        "-i", str(input_path),
        "-t", f"{duration:.3f}",
        "-c:v", "libx264", "-crf", FFMPEG_CRF,
        "-preset", "fast",
        "-c:a", "aac", "-b:a", FFMPEG_AUDIO_BITRATE,
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True, timeout=120)
    return output_path


def mix_voiceover(
    video_path: str | Path,
    voiceover_path: str | Path,
    output_path: str | Path = None,
    voice_volume: float = 1.0,
    bg_duck: float = 0.3,
) -> Path:
    """Mix voiceover narration into a video, ducking original audio.

    Args:
        video_path: Input video file
        voiceover_path: Voiceover audio file (TTS generated)
        output_path: Output file (default: _narrated suffix)
        voice_volume: Voiceover volume (default 1.0 = full)
        bg_duck: Original audio ducking level when voice is present (0.3 = -10dB)

    Returns:
        Path to the narrated video.
    """
    video_path = Path(video_path)
    voiceover_path = Path(voiceover_path)
    if output_path is None:
        output_path = video_path.parent / f"{video_path.stem}_narrated{video_path.suffix}"
    output_path = Path(output_path)

    try:
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(voiceover_path),
            "-filter_complex",
            f"[0:a]volume={bg_duck}[bg];"
            f"[1:a]volume={voice_volume}[vo];"
            f"[bg][vo]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", FFMPEG_AUDIO_BITRATE,
            "-shortest",
            str(output_path)
        ]

        subprocess.run(cmd, capture_output=True, check=True, timeout=180)
        logger.info(f"🎙️ Voiceover mixed: {output_path.name}")
    except subprocess.CalledProcessError as e:
        logger.warning(f"⚠️ Voiceover mix failed (using original): {e}")
        import shutil
        shutil.copy2(str(video_path), str(output_path))

    return output_path
