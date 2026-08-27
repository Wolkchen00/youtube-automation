"""ROCK A teslim sesini ve katman dengesini çevrimdışı doğrula."""

from __future__ import annotations

import argparse
import array
import json
import math
import statistics
import subprocess
import sys
from pathlib import Path


SAMPLE_RATE = 8000
WINDOW_SECONDS = 0.1
WINDOW_SAMPLES = int(SAMPLE_RATE * WINDOW_SECONDS)
SPEECH_FREE_FRACTION = 0.08
NATIVE_PRESENCE_CORRELATION_MIN = 0.55
DYNAMIC_GAIN_DIFFERENCE_MAX_DB = 4.0


def _run(args: list[str], *, text: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        args,
        capture_output=True,
        text=text,
        timeout=600,
    )


def _probe(path: Path) -> dict:
    result = _run([
        "ffprobe", "-v", "error", "-select_streams", "a:0",
        "-show_entries", "stream=sample_rate,channels,channel_layout",
        "-show_entries", "format=duration", "-of", "json", str(path),
    ], text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe başarısız ({path}): {result.stderr.strip()}")
    data = json.loads(result.stdout)
    streams = data.get("streams") or []
    if not streams:
        raise RuntimeError(f"ses akışı yok: {path}")
    stream = streams[0]
    duration = float((data.get("format") or {}).get("duration"))
    return {
        "sample_rate": int(stream["sample_rate"]),
        "channels": int(stream["channels"]),
        "channel_layout": str(stream.get("channel_layout") or "unknown"),
        "duration": duration,
    }


def _measure_native(path: Path) -> dict[str, float]:
    # Kanal düzeni ve örnekleme oranına dokunma: LUFS/TP final teslimin kendisinde ölçülür.
    result = _run([
        "ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vn",
        "-af", "ebur128=peak=true", "-f", "null", "-",
    ], text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ebur128 başarısız ({path}): {result.stderr.strip()}")
    import re

    loudness = re.findall(
        r"Integrated loudness:\s*I:\s*(-?(?:\d+(?:\.\d+)?|inf))\s*LUFS",
        result.stderr,
        re.IGNORECASE,
    )
    true_peak = re.findall(
        r"True peak:\s*Peak:\s*(-?(?:\d+(?:\.\d+)?|inf))\s*dBFS",
        result.stderr,
        re.IGNORECASE,
    )
    if not loudness or not true_peak:
        raise RuntimeError(f"ebur128 özeti ayrıştırılamadı: {path}")
    measured = {
        "integrated_lufs": float(loudness[-1]),
        "true_peak_dbtp": float(true_peak[-1]),
    }
    if not all(math.isfinite(value) for value in measured.values()):
        raise RuntimeError(f"ebur128 sonlu değer döndürmedi: {path}")
    return measured


def _pcm_from_command(args: list[str]) -> array.array:
    result = _run(args)
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"zarf PCM üretimi başarısız: {stderr.strip()}")
    samples = array.array("h")
    samples.frombytes(result.stdout)
    if sys.byteorder != "little":
        samples.byteswap()
    return samples


def _decode_envelope_pcm(path: Path) -> array.array:
    return _pcm_from_command([
        "ffmpeg", "-v", "error", "-i", str(path), "-vn", "-map", "0:a:0",
        "-ac", "1", "-ar", str(SAMPLE_RATE), "-c:a", "pcm_s16le",
        "-f", "s16le", "-",
    ])


def _production_bed_pcm(
    path: Path,
    duration: float,
    music_volume: float,
) -> array.array:
    fade_out_start = max(0.0, duration - 1.5)
    bed = (
        f"[0:a]atrim=0:{duration:.2f},asetpts=PTS-STARTPTS,"
        f"volume={music_volume},"
        f"afade=t=in:st=0:d=1.0,"
        f"afade=t=out:st={fade_out_start:.2f}:d=1.5[bed]"
    )
    return _pcm_from_command([
        "ffmpeg", "-v", "error", "-stream_loop", "-1", "-i", str(path),
        "-filter_complex", bed, "-map", "[bed]", "-ac", "1",
        "-ar", str(SAMPLE_RATE), "-c:a", "pcm_s16le", "-f", "s16le", "-",
    ])


def _pad(samples: array.array, size: int) -> array.array:
    if len(samples) >= size:
        return samples
    samples.extend([0] * (size - len(samples)))
    return samples


def _window_rms(samples: array.array, count: int) -> list[float]:
    values: list[float] = []
    for index in range(count):
        start = index * WINDOW_SAMPLES
        window = samples[start:start + WINDOW_SAMPLES]
        energy = sum(float(value) * float(value) for value in window)
        values.append(math.sqrt(energy / WINDOW_SAMPLES) / 32768.0)
    return values


def _dbfs(value: float) -> float:
    return 20.0 * math.log10(value) if value > 0.0 else float("-inf")


def _median_db(values: list[float]) -> float:
    if not values:
        raise RuntimeError("medyan için pencere yok")
    return _dbfs(statistics.median(values))


def _correlation(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or len(left) < 2:
        return float("nan")
    left_mean = statistics.fmean(left)
    right_mean = statistics.fmean(right)
    numerator = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right))
    left_energy = sum((value - left_mean) ** 2 for value in left)
    right_energy = sum((value - right_mean) ** 2 for value in right)
    denominator = math.sqrt(left_energy * right_energy)
    return numerator / denominator if denominator > 0.0 else float("nan")


def _fmt(value: float) -> str:
    if math.isnan(value):
        return "nan"
    if math.isinf(value):
        return "-inf" if value < 0 else "inf"
    return f"{value:.3f}"


def _share(flags: list[bool]) -> float:
    return sum(flags) / len(flags) if flags else 1.0


def check(args: argparse.Namespace) -> int:
    delivery = Path(args.delivery)
    ref_raw = Path(args.ref_raw)
    ref_tts = Path(args.ref_tts)
    ref_bed = Path(args.ref_bed)
    ref_premaster = Path(args.ref_premaster)
    baseline = Path(args.baseline_final) if args.baseline_final else None
    for path in (delivery, ref_raw, ref_tts, ref_bed, ref_premaster, baseline):
        if path is not None and (not path.exists() or path.stat().st_size == 0):
            raise RuntimeError(f"dosya yok veya boş: {path}")

    info = _probe(delivery)
    measured = _measure_native(delivery)
    print(f"delivery={delivery}")
    print(f"native_sample_rate_hz={info['sample_rate']}")
    print(f"native_channels={info['channels']}")
    print(f"native_channel_layout={info['channel_layout']}")
    print(f"duration_s={info['duration']:.6f}")
    print(f"integrated_lufs={measured['integrated_lufs']:.3f}")
    print(f"true_peak_dbtp={measured['true_peak_dbtp']:.3f}")

    violations: list[str] = []
    loudness_bad = abs(measured["integrated_lufs"] - args.target_lufs) > args.lufs_tolerance
    peak_bad = measured["true_peak_dbtp"] > args.true_peak_max
    print(f"loudness_violation_share={1.0 if loudness_bad else 0.0:.6f}")
    print(f"true_peak_violation_share={1.0 if peak_bad else 0.0:.6f}")
    if loudness_bad:
        violations.append(
            f"integrated loudness hedef dışında: {measured['integrated_lufs']:.1f} LUFS"
        )
    if peak_bad:
        violations.append(f"true peak aşıldı: {measured['true_peak_dbtp']:.1f} dBTP")

    teaser_samples = round(max(0.0, args.teaser_len) * SAMPLE_RATE)
    final_pcm = _decode_envelope_pcm(delivery)
    if teaser_samples >= len(final_pcm):
        raise RuntimeError("teaser_len teslim süresinden uzun")
    final_body = final_pcm[teaser_samples:]
    raw_pcm = _decode_envelope_pcm(ref_raw)
    premaster_pcm = _decode_envelope_pcm(ref_premaster)
    if teaser_samples >= len(premaster_pcm):
        raise RuntimeError("teaser_len pre-master referans süresinden uzun")
    premaster_body = premaster_pcm[teaser_samples:]
    body_duration = min(len(final_body), len(raw_pcm)) / SAMPLE_RATE
    bed_pcm = _production_bed_pcm(ref_bed, body_duration, args.music_volume)
    tts_pcm = _pad(_decode_envelope_pcm(ref_tts), len(raw_pcm))

    baseline_body = None
    if baseline is not None:
        baseline_info = _probe(baseline)
        baseline_pcm = _decode_envelope_pcm(baseline)
        if teaser_samples >= len(baseline_pcm):
            raise RuntimeError("teaser_len baseline süresinden uzun")
        baseline_body = baseline_pcm[teaser_samples:]
        print(f"baseline_final={baseline}")
        print(f"baseline_native_sample_rate_hz={baseline_info['sample_rate']}")
        print(f"baseline_native_channels={baseline_info['channels']}")
        print(f"baseline_native_channel_layout={baseline_info['channel_layout']}")

    lengths = [
        len(final_body), len(raw_pcm), len(tts_pcm), len(bed_pcm), len(premaster_body),
    ]
    if baseline_body is not None:
        lengths.append(len(baseline_body))
    window_count = min(lengths) // WINDOW_SAMPLES
    if window_count < 1:
        raise RuntimeError("100 ms zarf penceresi üretilemedi")
    final_env = _window_rms(final_body, window_count)
    raw_env = _window_rms(raw_pcm, window_count)
    tts_env = _window_rms(tts_pcm, window_count)
    bed_env = _window_rms(bed_pcm, window_count)
    premaster_env = _window_rms(premaster_body, window_count)
    baseline_env = (
        _window_rms(baseline_body, window_count) if baseline_body is not None else None
    )
    tts_peak = max(tts_env)
    if tts_peak <= 0.0:
        raise RuntimeError("TTS referans zarfı sessiz")
    speech_free = [index for index, value in enumerate(tts_env)
                   if value < SPEECH_FREE_FRACTION * tts_peak]
    speech_active = [index for index, value in enumerate(tts_env)
                     if value >= SPEECH_FREE_FRACTION * tts_peak]
    if not speech_free or not speech_active:
        raise RuntimeError("konuşmalı/konuşmasız pencere kümeleri oluşturulamadı")

    valid_gain = [
        index for index in range(window_count)
        if final_env[index] > 0.0 and premaster_env[index] > 0.0
    ]
    if len(valid_gain) < 2:
        raise RuntimeError("master kazancı için yeterli sesli pencere yok")
    gain_db_by_index = {
        index: _dbfs(final_env[index]) - _dbfs(premaster_env[index])
        for index in valid_gain
    }
    gain_values = list(gain_db_by_index.values())
    gain_median = statistics.median(gain_values)
    gain_linear = [
        10.0 ** (gain_db_by_index.get(index, gain_median) / 20.0)
        for index in range(window_count)
    ]
    delivered_bed_env = [
        bed_env[index] * gain_linear[index] for index in range(window_count)
    ]
    quiet_loud_count = min(40, len(valid_gain) // 2)
    ordered_gain = sorted(valid_gain, key=lambda index: premaster_env[index])
    quiet_gain = statistics.median(
        gain_db_by_index[index] for index in ordered_gain[:quiet_loud_count]
    )
    loud_gain = statistics.median(
        gain_db_by_index[index] for index in ordered_gain[-quiet_loud_count:]
    )
    quiet_loud_gain_difference = quiet_gain - loud_gain
    dynamics_bad = abs(quiet_loud_gain_difference) > DYNAMIC_GAIN_DIFFERENCE_MAX_DB

    final_free = [final_env[index] for index in speech_free]
    raw_free = [raw_env[index] for index in speech_free]
    bed_free = [bed_env[index] for index in speech_free]
    delivered_bed_free = [delivered_bed_env[index] for index in speech_free]
    program_median = _median_db(final_free)
    native_median = _median_db(raw_free)
    bed_premaster_median = _median_db(bed_free)
    bed_median = _median_db(delivered_bed_free)
    foley_bed_delta = program_median - bed_median
    native_residual_free = [
        math.sqrt(max(program * program - bed * bed, 0.0))
        for program, bed in zip(final_free, delivered_bed_free)
    ]
    raw_native_correlation = _correlation(final_free, raw_free)
    native_presence_correlation = _correlation(native_residual_free, raw_free)
    native_presence_bad = (
        not math.isfinite(native_presence_correlation)
        or native_presence_correlation < NATIVE_PRESENCE_CORRELATION_MIN
    )
    foley_level_flags = [_dbfs(final_env[index]) < -30.0 for index in speech_free]
    foley_bed_flags = [
        _dbfs(final_env[index]) - _dbfs(delivered_bed_env[index]) < 6.0
        for index in speech_free
    ]
    print(f"teaser_len_s={args.teaser_len:.6f}")
    print(f"envelope_sample_rate_hz={SAMPLE_RATE}")
    print(f"envelope_window_ms={WINDOW_SECONDS * 1000:.0f}")
    print(f"music_volume={args.music_volume:.6f}")
    print("music_volume_source=cli")
    print(f"ref_premaster={ref_premaster}")
    print(f"window_count={window_count}")
    print(f"master_gain_window_count={len(valid_gain)}")
    print(f"master_gain_median_db={_fmt(gain_median)}")
    print(f"master_gain_min_db={_fmt(min(gain_values))}")
    print(f"master_gain_max_db={_fmt(max(gain_values))}")
    print(f"master_gain_quiet_loud_window_count={quiet_loud_count}")
    print(f"master_gain_quiet_median_db={_fmt(quiet_gain)}")
    print(f"master_gain_loud_median_db={_fmt(loud_gain)}")
    print(f"master_gain_quiet_minus_loud_db={_fmt(quiet_loud_gain_difference)}")
    print(f"master_gain_quiet_minus_loud_max_db={DYNAMIC_GAIN_DIFFERENCE_MAX_DB:.3f}")
    print(f"dynamic_gain_violation_share={1.0 if dynamics_bad else 0.0:.6f}")
    print(f"speech_free_threshold_fraction={SPEECH_FREE_FRACTION:.6f}")
    print(f"tts_peak_window_dbfs={_fmt(_dbfs(tts_peak))}")
    print(f"speech_free_window_count={len(speech_free)}")
    print(f"speech_active_window_count={len(speech_active)}")
    print(f"speech_free_program_median_dbfs={_fmt(program_median)}")
    print(f"speech_free_native_reference_median_dbfs={_fmt(native_median)}")
    print(f"speech_free_bed_reference_premaster_median_dbfs={_fmt(bed_premaster_median)}")
    print(f"speech_free_bed_reference_delivered_median_dbfs={_fmt(bed_median)}")
    print(f"foley_over_bed_median_db={_fmt(foley_bed_delta)}")
    print(f"foley_level_violation_share={_share(foley_level_flags):.6f}")
    print(f"foley_over_bed_violation_share={_share(foley_bed_flags):.6f}")
    print(f"speech_free_program_native_correlation={_fmt(raw_native_correlation)}")
    print(f"speech_free_bed_residual_native_correlation={_fmt(native_presence_correlation)}")
    print(f"native_presence_correlation_min={NATIVE_PRESENCE_CORRELATION_MIN:.3f}")
    print(f"native_presence_violation_share={1.0 if native_presence_bad else 0.0:.6f}")
    if dynamics_bad:
        violations.append(
            "master dinamik kazanç farkı yüksek: "
            f"{quiet_loud_gain_difference:+.1f} dB"
        )
    if program_median < -30.0:
        violations.append(f"foley/program medyanı düşük: {program_median:.1f} dBFS")
    if foley_bed_delta < 6.0:
        violations.append(f"foley/yatak farkı düşük: {foley_bed_delta:.1f} dB")
    if native_presence_bad:
        violations.append(
            "native foley varlığı doğrulanamadı: "
            f"korelasyon={native_presence_correlation:.3f}"
        )

    if baseline_env is not None:
        after_free_median = _median_db(final_free)
        before_free_median = _median_db([baseline_env[index] for index in speech_free])
        after_active_median = _median_db([final_env[index] for index in speech_active])
        before_active_median = _median_db([baseline_env[index] for index in speech_active])
        after_balance = after_active_median - after_free_median
        before_balance = before_active_median - before_free_median
        balance_change = after_balance - before_balance
        per_window_changes = [
            (_dbfs(final_env[index]) - after_free_median)
            - (_dbfs(baseline_env[index]) - before_free_median)
            for index in speech_active
        ]
        balance_flags = [abs(value) > 1.5 for value in per_window_changes]
        print(f"baseline_narration_to_bed_db={_fmt(before_balance)}")
        print(f"delivery_narration_to_bed_db={_fmt(after_balance)}")
        print(f"narration_to_bed_change_db={_fmt(balance_change)}")
        print(f"narration_to_bed_violation_share={_share(balance_flags):.6f}")
        if abs(balance_change) > 1.5:
            violations.append(
                f"anlatım/yatak değişimi bant dışında: {balance_change:+.1f} dB"
            )

    if violations:
        for violation in violations:
            print(f"VIOLATION: {violation}")
        print("RESULT=FAIL")
        return 1
    print("RESULT=PASS")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("delivery")
    parser.add_argument("--ref-raw", required=True)
    parser.add_argument("--ref-tts", required=True)
    parser.add_argument("--ref-bed", required=True)
    parser.add_argument("--ref-premaster", required=True)
    parser.add_argument("--baseline-final")
    parser.add_argument("--teaser-len", type=float, default=0.0)
    parser.add_argument("--music-volume", type=float, required=True)
    parser.add_argument("--target-lufs", type=float, default=-14.0)
    parser.add_argument("--lufs-tolerance", type=float, default=1.0)
    parser.add_argument("--true-peak-max", type=float, default=-1.0)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        return check(args)
    except Exception as error:
        print(f"ERROR: {error}")
        print("RESULT=FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
