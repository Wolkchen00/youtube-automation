"""Zincir muafiyetinin URETIM DONGUSUNDE gercekten tasindiginin kaniti.

Neden ayri dosya: tests/test_chain_reset_continuity.py muafiyeti `_decide()`
seviyesinde dogruluyor, yani "bayrak verilirse dogru davranir" diyor. Kanali 5
gun karanlikta birakan hata ise TAM OLARAK bayragin hic verilmemesiydi:
part26 cekimlerinde `chain` alani yok, bu yuzden `decide_shot_chain()` legacy
dala giriyor, `chain_decision.error` uretmiyor ve produce.py:1452'deki
`chain_reset_pending` dali HIC calismiyor; degisken 1480'de sessizce
sifirlaniyor. Asagidaki testler bayragin `qc_shot`'a ULASTIGINI kanitlar.

Canli kanit, kosu 33594947982 (2026-09-02 05:30 UTC):
    Zincir karesi sifirlandi: cekim 3 -> 4; neden=unsuitable
    QC RED: cekim 4 (deneme 0/1/2): ... surekliligi bozuk
"""

from __future__ import annotations

from contextlib import ExitStack
from pathlib import Path
from unittest import mock

import pytest

from series import produce
from series.bible import Bible
from series.series_meta import SeriesMeta


def _bible(min_shots: int | None = None) -> Bible:
    return Bible({
        "series": {
            "slug": "chain-plumbing-proof",
            "title": "Chain Plumbing Proof",
            "engine": "seedance",
            "state_machine_version": 2,
            "chain_frames": True,
            "chain_scope": "episode",
            "qc": {
                "enabled": True,
                "require_continuity": True,
                "require_all_shots": True,
                "max_regens_per_shot": 0,
                **({} if min_shots is None else {"min_shots": min_shots}),
            },
        },
        "music": False,
        "narration": {},
        "characters": [],
        "environments": [],
        "props": [],
    })


def _plan() -> dict:
    # part26 ile ayni sekil: cekimlerde "chain" alani YOK (legacy dal).
    return {
        "episode": {"number": 26, "title": "This FORK Grabs FOOD!"},
        "narration": "",
        "shots": [
            {"n": 1, "duration": "6", "prompt": "shot 1",
             "state_carry": "the four tines curled shut around a blueberry"},
            {"n": 2, "duration": "6", "prompt": "shot 2",
             "state_carry": "the curled tines holding the blueberry clear"},
            {"n": 3, "duration": "6", "prompt": "shot 3",
             "state_carry": "the tines stretched long and empty above the counter"},
            {"n": 4, "duration": "6", "prompt": "shot 4"},
        ],
    }


def _meta() -> SeriesMeta:
    return SeriesMeta({
        "slug": "chain-plumbing-proof",
        "base_title": "Chain Plumbing Proof",
        "total_parts": 1,
        "next_part": 26,
        "status": "active",
        "publish_mode": "auto",
        "upload_profile": "proof-profile",
        "platforms": ["youtube"],
        "parts": {},
    })


def _run(tmp_path: Path, *, reset_after: set[int] = frozenset(),
         drops: set[int] = frozenset(), min_shots: int | None = None):
    """Bolumu uret; her cekim icin qc_shot'a gelen continuity_exempt'i topla."""
    seen: dict[int, bool] = {}

    def qc_shot(_bible, shot, clip, *_args, **kwargs):
        n = int(shot["n"])
        seen[n] = bool(kwargs.get("continuity_exempt"))
        if n in drops:
            return None, 0.0, "fail"
        return Path(clip), 0.0, "pass"

    def next_chain_frame(_bible, _plan, shot, *_args, **_kwargs):
        # Kaynak cekim reset listesindeyse zincir karesi KANONIGE duser.
        if int(shot.get("n") or 0) in reset_after:
            return produce.NextChainFrame(None, True, None)
        return produce.NextChainFrame("https://proof/frame.png", False, None)

    def download(_url, target, **_kwargs):
        Path(target).parent.mkdir(parents=True, exist_ok=True)
        Path(target).write_bytes(b"clip")
        return Path(target)

    def write_video(_inputs, output, **_kwargs):
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_bytes(b"video")
        return Path(output)

    bible, meta, plan = _bible(min_shots), _meta(), _plan()
    with ExitStack() as stack:
        p = lambda *a, **k: stack.enter_context(mock.patch.object(*a, **k))  # noqa: E731
        p(produce.SeriesMeta, "load", return_value=meta)
        p(produce.Bible, "load", return_value=bible)
        p(produce, "_doctrine_gate", return_value="digest")
        p(produce, "validate_plan", return_value={"warnings": [], "errors": []})
        p(produce, "ensure_episode_refs", return_value=True)
        p(produce, "check_credit")
        p(produce, "_next_chain_frame", side_effect=next_chain_frame)
        p(produce, "resolve_visual_shot", side_effect=lambda _b, shot, **_k: {
            "prompt": shot["prompt"], "start_image_url": None,
            "duration": shot["duration"],
        })
        p(produce, "_generate_visual_clip",
          side_effect=lambda *_a, **_k: {"url": "https://proof/clip", "credits": 0})
        p(produce, "download_file", side_effect=download)
        p(produce.critic, "qc_shot", side_effect=qc_shot)
        p(produce, "_prep_shot_clip", side_effect=lambda _b, _pl, _s, path: Path(path))
        p(produce.ffmpeg_tools, "get_video_duration", return_value=6.0)
        p(produce.ffmpeg_tools, "concatenate_simple", side_effect=write_video)
        p(produce.ffmpeg_tools, "concatenate_audio_smooth", side_effect=write_video)
        p(produce.ffmpeg_tools, "final_export",
          side_effect=lambda _src, dst: write_video([], dst))
        p(produce, "_post_process", side_effect=lambda _b, _pl, path, **_k: Path(path))
        p(produce, "_record_episode_cost", return_value=True)
        p(produce.report, "append_row")
        p(produce.report, "export_xlsx")
        p(produce.report, "summarize", return_value={
            "başarılı": 4, "çekim_sayısı": 4, "toplam_kredi": 0, "toplam_dolar": 0})
        result = produce.produce_episode(
            bible.slug, plan, typed_result=True, output_area=tmp_path
        )
    return result, seen


def test_live_failure_replay_reset_three_to_four_exempts_only_shot_four(tmp_path):
    """CANLI ARIZA TEKRARI: 3 -> 4 sifirlaninca YALNIZ cekim 4 muaf olur."""
    result, seen = _run(tmp_path, reset_after={3})
    assert result.status == "ok", "bolum yine olmemeli"
    assert seen[4] is True, "cekim 4 muaf DEGIL , canli arizanin ta kendisi"
    assert seen[2] is False
    assert seen[3] is False


def test_exemption_does_not_leak_to_the_shot_after_a_recovered_chain(tmp_path):
    """ADVERSARIAL: 1 -> 2 sifirlanir, 2 -> 3 saglamdir.

    Cekim 2 muaf olmali ama cekim 3 TEKRAR sert kapiya girmeli; yoksa tek bir
    reset butun bolumun sureklilik denetimini sessizce kapatirdi.
    """
    _, seen = _run(tmp_path, reset_after={1})
    assert seen[2] is True
    assert seen[3] is False, "muafiyet sonraki cekime SIZDI"
    assert seen[4] is False


def test_dropped_shot_also_breaks_the_anchor_for_the_next_shot(tmp_path):
    """Cekim dusunce de cipa kirilir; sonraki cekim surekliligi kanitlayamaz."""
    # min_shots verilmezse cekim 2 dusunce bolum ZATEN erken iptal olur
    # (kabul=1 + kalan=2 < gerekli=4), cekim 3 hic uretilmez. Kismi yayin
    # acikken cekim 3 uretilir ve cipasi kirik oldugu icin muaf olmalidir.
    _, seen = _run(tmp_path, drops={2}, min_shots=2)
    assert seen[3] is True, "dusen cekimden sonraki cekim muaf degil"


def test_clean_chain_never_exempts_anything(tmp_path):
    """Zincir hic kirilmazsa hicbir cekim muaf olmaz , kapi sert kalir."""
    _, seen = _run(tmp_path)
    assert seen == {1: False, 2: False, 3: False, 4: False}
