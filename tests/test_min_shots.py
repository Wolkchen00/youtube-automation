from contextlib import ExitStack
from pathlib import Path
from unittest import mock

from core import narration
from series import preflight, produce, series_runner
from series.bible import Bible
from series.series_meta import SeriesMeta


_ABSENT = object()


def _bible(*, min_shots=_ABSENT, narration_enabled=False,
           music=False, required_platforms=_ABSENT) -> Bible:
    qc = {"enabled": True, "require_all_shots": True, "max_regens_per_shot": 0}
    if min_shots is not _ABSENT:
        qc["min_shots"] = min_shots
    series = {
        "slug": "min-shots-proof",
        "title": "Min Shots Proof",
        "engine": "seedance",
        "state_machine_version": 2,
        "qc": qc,
        "chain_frames": False,
    }
    if required_platforms is not _ABSENT:
        series["required_platforms"] = required_platforms
    return Bible({
        "series": series,
        "music": music,
        "narration": {"channel": "sentinal_vlog"} if narration_enabled else {},
        "characters": [],
        "environments": [],
        "props": [],
    })


def _plan() -> dict:
    return {
        "episode": {"number": 1, "title": "Proof"},
        "narration": (
            "Making a quick snack and the cutlery literally started grabbing the fruit. "
            "I tried washing it but it keeps doing it. Should I throw it out?"
        ),
        "shots": [
            {"n": n, "duration": "6", "prompt": f"shot {n}"}
            for n in range(1, 5)
        ],
    }


def _meta() -> SeriesMeta:
    return SeriesMeta({
        "slug": "min-shots-proof",
        "base_title": "Min Shots Proof",
        "total_parts": 1,
        "next_part": 1,
        "status": "active",
        "publish_mode": "auto",
        "upload_profile": "proof-profile",
        "platforms": ["youtube", "instagram"],
        "parts": {},
    })


def _produce_with_drops(tmp_path: Path, drops: set[int], *, min_shots=_ABSENT):
    bible = _bible(min_shots=min_shots)
    meta = _meta()
    plan = _plan()

    def download(_url, target, **_kwargs):
        Path(target).parent.mkdir(parents=True, exist_ok=True)
        Path(target).write_bytes(b"clip")
        return Path(target)

    def qc_shot(_bible, shot, clip, *_args, **_kwargs):
        if int(shot["n"]) in drops:
            return None, 0.0, "fail"
        return Path(clip), 0.0, "pass"

    def write_video(_inputs, output, **_kwargs):
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_bytes(b"video")
        return Path(output)

    with ExitStack() as stack:
        stack.enter_context(mock.patch.object(produce.SeriesMeta, "load", return_value=meta))
        stack.enter_context(mock.patch.object(produce.Bible, "load", return_value=bible))
        stack.enter_context(mock.patch.object(produce, "_doctrine_gate", return_value="digest"))
        stack.enter_context(mock.patch.object(
            produce, "validate_plan", return_value={"warnings": [], "errors": []}
        ))
        stack.enter_context(mock.patch.object(produce, "ensure_episode_refs", return_value=True))
        stack.enter_context(mock.patch.object(produce, "check_credit"))
        stack.enter_context(mock.patch.object(
            produce, "resolve_visual_shot",
            side_effect=lambda _b, shot, **_k: {
                "prompt": shot["prompt"], "start_image_url": None,
                "duration": shot["duration"],
            },
        ))
        stack.enter_context(mock.patch.object(
            produce, "_generate_visual_clip",
            side_effect=lambda *_a, **_k: {"url": "https://proof/clip", "credits": 0},
        ))
        stack.enter_context(mock.patch.object(produce, "download_file", side_effect=download))
        stack.enter_context(mock.patch.object(produce.critic, "qc_shot", side_effect=qc_shot))
        stack.enter_context(mock.patch.object(
            produce, "_prep_shot_clip", side_effect=lambda _b, _p, _s, path: Path(path)
        ))
        stack.enter_context(mock.patch.object(
            produce.ffmpeg_tools, "get_video_duration", return_value=6.0
        ))
        stack.enter_context(mock.patch.object(
            produce.ffmpeg_tools, "concatenate_simple", side_effect=write_video
        ))
        stack.enter_context(mock.patch.object(
            produce.ffmpeg_tools, "concatenate_audio_smooth", side_effect=write_video
        ))
        stack.enter_context(mock.patch.object(
            produce.ffmpeg_tools, "final_export",
            side_effect=lambda _src, dst: write_video([], dst),
        ))
        stack.enter_context(mock.patch.object(
            produce, "_post_process", side_effect=lambda _b, _p, path, **_k: Path(path)
        ))
        stack.enter_context(mock.patch.object(produce, "_record_episode_cost", return_value=True))
        stack.enter_context(mock.patch.object(produce.report, "append_row"))
        stack.enter_context(mock.patch.object(produce.report, "export_xlsx"))
        stack.enter_context(mock.patch.object(
            produce.report, "summarize",
            return_value={"başarılı": 3, "çekim_sayısı": 4,
                          "toplam_kredi": 0, "toplam_dolar": 0},
        ))
        return produce.produce_episode(
            bible.slug, plan, typed_result=True, output_area=tmp_path
        )


def test_three_of_four_with_minimum_three_assembles_and_records_drop(tmp_path: Path):
    result = _produce_with_drops(tmp_path, {2}, min_shots=3)
    assert result.status == "ok"
    assert result.dropped_shots == [2]
    assert result.path and result.path.exists()


def test_two_of_four_with_minimum_three_is_cancelled(tmp_path: Path):
    result = _produce_with_drops(tmp_path, {2, 3}, min_shots=3)
    assert result.status == "generation_fail"


def test_missing_minimum_keeps_require_all_shots_behavior(tmp_path: Path):
    result = _produce_with_drops(tmp_path, {2})
    assert result.status == "generation_fail"


def test_drop_position_one_can_publish_three_of_four(tmp_path: Path):
    assert _produce_with_drops(tmp_path, {1}, min_shots=3).dropped_shots == [1]


def test_drop_position_two_can_publish_three_of_four(tmp_path: Path):
    assert _produce_with_drops(tmp_path, {2}, min_shots=3).dropped_shots == [2]


def test_drop_position_three_can_publish_three_of_four(tmp_path: Path):
    assert _produce_with_drops(tmp_path, {3}, min_shots=3).dropped_shots == [3]


def test_drop_position_four_can_publish_three_of_four(tmp_path: Path):
    assert _produce_with_drops(tmp_path, {4}, min_shots=3).dropped_shots == [4]


def _invalid_minimum_stops_before_generation(tmp_path: Path, value):
    bible = _bible(min_shots=value)
    meta = _meta()
    generated = mock.Mock()
    with mock.patch.object(produce.SeriesMeta, "load", return_value=meta), \
            mock.patch.object(produce.Bible, "load", return_value=bible), \
            mock.patch.object(produce, "_doctrine_gate", return_value="digest"), \
            mock.patch.object(produce, "validate_plan", return_value={"warnings": [], "errors": []}), \
            mock.patch.object(produce, "_generate_visual_clip", generated):
        result = produce.produce_episode(
            bible.slug, _plan(), typed_result=True, output_area=tmp_path
        )
    assert result.status == "generation_fail"
    generated.assert_not_called()


def test_min_shots_bool_is_rejected_before_paid_call(tmp_path: Path):
    _invalid_minimum_stops_before_generation(tmp_path, True)


def test_min_shots_zero_is_rejected_before_paid_call(tmp_path: Path):
    _invalid_minimum_stops_before_generation(tmp_path, 0)


def test_min_shots_negative_is_rejected_before_paid_call(tmp_path: Path):
    _invalid_minimum_stops_before_generation(tmp_path, -1)


def test_min_shots_above_plan_count_is_rejected_before_paid_call(tmp_path: Path):
    _invalid_minimum_stops_before_generation(tmp_path, 5)


def test_partial_eighteen_second_variant_keeps_complete_narration_without_cap(
        tmp_path: Path):
    bible = _bible(min_shots=3, narration_enabled=True)
    video = tmp_path / "video.mp4"
    voice = tmp_path / "voice.wav"
    video.write_bytes(b"video")
    voice.write_bytes(b"voice")

    def mix(_video, _voice, output, **_kwargs):
        Path(output).write_bytes(b"narrated")

    shortened = "The fork grabbed my snack again. Washing changed nothing. Should I keep it?"
    with mock.patch.object(
        narration, "shorten_narration_for_duration", return_value=shortened
    ) as shorten, mock.patch.object(
        narration, "create_narration_for_channel", return_value=(voice, "proof")
    ) as tts, mock.patch.object(
        produce.ffmpeg_tools, "get_video_duration", side_effect=[18.0, 18.0, 21.0]
    ), mock.patch.object(
        produce.ffmpeg_tools, "mix_voiceover", side_effect=mix
    ) as mixer, mock.patch.object(series_runner, "_series_alert") as alert:
        result = produce._post_process(
            bible, _plan(), video, dropped_shots=[2]
        )

    assert result and result.name.endswith("_narrated.mp4")
    shorten.assert_called_once()
    assert tts.call_args.args[1] == shortened
    mixer.assert_called_once()
    alert.assert_not_called()


def test_unfittable_partial_narration_becomes_music_only_and_alerts(tmp_path: Path):
    bible = _bible(min_shots=3, narration_enabled=True, music=True)
    video = tmp_path / "video.mp4"
    voice = tmp_path / "voice.wav"
    music_file = tmp_path / "music.mp3"
    video.write_bytes(b"video")
    voice.write_bytes(b"voice")
    music_file.write_bytes(b"music")

    def music_mix(_video, _music, output, **_kwargs):
        Path(output).write_bytes(b"music-only")

    with mock.patch.object(
        narration, "shorten_narration_for_duration", return_value="A complete short sentence."
    ), mock.patch.object(
        narration, "create_narration_for_channel", return_value=(voice, "proof")
    ), mock.patch.object(
        produce.ffmpeg_tools, "get_video_duration", side_effect=[18.0, 18.0, 28.0]
    ), mock.patch.object(
        produce.ffmpeg_tools, "mix_voiceover"
    ) as voice_mix, mock.patch(
        "core.music_generator.generate_background_music", return_value=music_file
    ), mock.patch.object(
        produce.ffmpeg_tools, "mix_background_music", side_effect=music_mix
    ) as background_mix, mock.patch.object(series_runner, "_series_alert") as alert:
        result = produce._post_process(
            bible, _plan(), video, dropped_shots=[2]
        )

    voice_mix.assert_not_called()
    assert background_mix.call_args.kwargs["replace_original"] is True
    alert.assert_called_once()
    assert "müzik-only" in alert.call_args.args[1]
    assert result and result.read_bytes() == b"music-only"


def _run_publish_case(tmp_path: Path, required_platforms, published_platforms):
    bible = _bible(min_shots=3, required_platforms=required_platforms)
    meta = _meta()
    plan = _plan()
    plan_path = tmp_path / "part01.json"
    plan_path.write_text("{}", encoding="utf-8")
    video = tmp_path / "episode.mp4"
    video.write_bytes(b"video")
    with mock.patch.object(series_runner.SeriesMeta, "load", return_value=meta), \
            mock.patch("series.bible.Bible.load", return_value=bible), \
            mock.patch.object(meta, "save"), \
            mock.patch.object(series_runner, "_channel_published_today", return_value=None), \
            mock.patch.object(series_runner, "part_plan_path", return_value=plan_path), \
            mock.patch.object(series_runner, "load_plan", return_value=plan), \
            mock.patch.object(series_runner, "_budget_failure", return_value=None), \
            mock.patch.object(series_runner, "check_credit", return_value={"credits": 5000}), \
            mock.patch.object(series_runner.credit_gate, "run_gate", return_value=True), \
            mock.patch.object(series_runner.credit_gate, "reserve", return_value=True), \
            mock.patch.object(series_runner.credit_gate, "reconcile"), \
            mock.patch.object(series_runner, "_actual_episode_spent", return_value=0), \
            mock.patch.object(
                series_runner.produce, "produce_episode",
                return_value=produce.ProduceResult("ok", video),
            ), mock.patch.object(
                series_runner, "_publish_part", return_value=published_platforms
            ), mock.patch.object(series_runner, "_series_alert"):
        outcome = series_runner.run_next(bible.slug, publish=True, force=True)
    return outcome, meta


def test_youtube_failure_blocks_publish_and_pointer_even_if_instagram_succeeds(
        tmp_path: Path):
    outcome, meta = _run_publish_case(tmp_path, ["youtube"], ["instagram"])
    assert outcome is False
    assert meta.get_part(1)["status"] != "published"
    assert meta.next_part == 1


def test_absent_required_platforms_keeps_any_platform_success_behavior(tmp_path: Path):
    outcome, meta = _run_publish_case(tmp_path, _ABSENT, ["instagram"])
    assert outcome is True
    assert meta.get_part(1)["status"] == "published"
    assert meta.next_part == 2
