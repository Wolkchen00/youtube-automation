"""Gemini ODEME arizasi (402, on odemeli kredi bitti) kalici duzeltmesinin kanitlari.

26-28 Eyl 2026'da uc kanal (sentinal_ihsan, galactic, shadowedhistory) uc gun
video cikaramadi. Sebep tekti: AI Studio on odemeli bakiyesi sifirlandi ve iki
Gemini anahtari da 402 dondu. Kod bunu gecici 429 sandi:
  * QC her modelde 30 sn araliklarla yeniden denedi, sonra ayni hesaptaki yedek
    modeli denedi;
  * Kie klibi QC'den ~28 dk ONCE odendigi icin her gun klip cope gitti
    (~1.100 kredi);
  * bolum "altyapi yeniden denemesi" sayildi, 48 saatte needs_human oldu ve
    ayni kosu hemen sonraki bolume de para odedi;
  * alarm "Gemini 429 denemeleri tukendi" dedi, yani yanlis sebebi soyledi.

Kilitlenen sozlesme:
  1. 402 / on odeme metni "billing" sinifidir; 429 (govdesinde "billing details"
     gecse bile) "quota" kalir.
  2. billing'de tek saniye beklenmez ve yedek model denenmez.
  3. Kosu basindaki yoklama billing/auth/gunluk kotada ucretli uretimi HIC
     baslatmaz, bolum durumuna dokunmaz ve anlasilir bir alarm gonderir.
  4. BILLING kodlu hold hicbir sayaci yakmaz, bolumu ASLA kuyruktan dusurmez.
  5. Altyapi butcesi dolup bolum insana devredildiginde ayni kosuda sonraki
     bolume para odenmez.
"""

from __future__ import annotations

import sys
from contextlib import ExitStack
from pathlib import Path
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from series import critic, produce, replenish, series_runner  # noqa: E402
from series.bible import Bible  # noqa: E402
from series.gemini_odeme import AI_STUDIO_URL, is_billing_error  # noqa: E402
from series.produce import ProduceResult  # noqa: E402
from series.series_meta import SeriesMeta  # noqa: E402
from tests.test_hold_recovery import _meta as _runner_meta  # noqa: E402
from tests.test_hold_recovery import _plan, _runner_stack  # noqa: E402
from tests.test_qc_backoff import (  # noqa: E402
    QUOTA_DAILY,
    QUOTA_PER_MINUTE,
    SERVER_503,
    _FakeGemini,
)

# 28 Eyl 2026 wild-encounter kosusundaki (36443139268) gercek govde.
BILLING_402 = (
    "402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment "
    "credits are depleted. Please go to AI Studio at https://ai.studio/projects to "
    "manage your project and billing. Learn more at "
    "https://ai.google.dev/gemini-api/docs/billing#prepay. ', "
    "'status': 'RESOURCE_EXHAUSTED'}}"
)
# Gercek 429 govdeleri "plan and billing details" der; bu ODEME arizasi DEGILDIR.
QUOTA_WITH_BILLING_WORD = (
    "429 RESOURCE_EXHAUSTED. {'error': {'code': 429, 'message': 'You exceeded your "
    "current quota, please check your plan and billing details.', "
    "'status': 'RESOURCE_EXHAUSTED'}}"
)

_FIXTURE_SLUG = "gemini-odeme-fixture"


@pytest.fixture(autouse=True)
def _never_touch_real_series_state():
    """Hicbir test gercek seri durumunu diske yazamaz."""
    with mock.patch.object(SeriesMeta, "save"), \
            mock.patch.object(SeriesMeta, "save_atomic"):
        yield


# ---------------------------------------------------------------------------
# 1) Siniflandirma
# ---------------------------------------------------------------------------

def test_402_prepay_depleted_is_billing_not_quota():
    assert critic._classify_api_error(RuntimeError(BILLING_402)) == "billing"
    assert is_billing_error(RuntimeError(BILLING_402))


def test_sdk_error_code_402_is_billing_even_without_the_message():
    error = RuntimeError("RESOURCE_EXHAUSTED")
    error.code = 402
    assert critic._classify_api_error(error) == "billing"


@pytest.mark.parametrize("body", [QUOTA_DAILY, QUOTA_PER_MINUTE, QUOTA_WITH_BILLING_WORD])
def test_every_429_stays_quota_even_when_it_mentions_billing(body):
    """ADVERSARIAL: 'billing details' kelimesi 429'u odeme arizasina CEVIRMEZ."""
    assert critic._classify_api_error(RuntimeError(body)) == "quota"
    assert not is_billing_error(RuntimeError(body))


def test_server_error_classification_is_unchanged():
    assert critic._classify_api_error(RuntimeError(SERVER_503)) == "server"


def test_billing_never_sleeps_before_retry():
    with mock.patch.object(critic.time, "sleep") as slept:
        proceed = critic._wait_for_qc_retry(
            RuntimeError(BILLING_402), 1, 3,
            response_received=False, wait_budget=None,
            label="Ham ses QC", model=critic.QC_MODEL,
        )
    assert proceed is False
    slept.assert_not_called()


def test_billing_maps_to_its_own_reason_code():
    assert produce._qc_api_reason_code("billing") == "BILLING"
    assert produce._qc_api_reason_code("quota") == "QUOTA"
    ProduceResult("qc_hold", reason="kredi bitti", reason_code="BILLING")


# ---------------------------------------------------------------------------
# 2) QC cagri donguleri: tek cagri, bekleme yok, yedek model yok
# ---------------------------------------------------------------------------

def _gemini_context(stack: ExitStack, fake: _FakeGemini):
    stack.enter_context(mock.patch.dict(sys.modules, fake.modules()))
    stack.enter_context(mock.patch.object(critic, "GEMINI_API_KEY", "test-key"))
    stack.enter_context(mock.patch.object(critic, "_strict_log_event", lambda *a, **k: None))
    return stack.enter_context(mock.patch.object(critic.time, "sleep"))


def test_visual_review_stops_after_one_call_on_billing(tmp_path):
    frame = tmp_path / "frame.png"
    frame.write_bytes(b"png")
    fake = _FakeGemini({
        critic.QC_MODEL: [RuntimeError(BILLING_402)] * 3,
        critic.QC_MODEL_FALLBACK: [RuntimeError(BILLING_402)] * 3,
    })
    with ExitStack() as stack:
        slept = _gemini_context(stack, fake)
        with pytest.raises(critic.QCApiExhausted) as caught:
            critic._review_frames(
                [frame], None, "prompt", "notes",
                slug=_FIXTURE_SLUG, episode=18, shot=1,
            )
    assert caught.value.reason == "billing"
    assert fake.calls == [critic.QC_MODEL], "402'de yedek model / tekrar denendi"
    slept.assert_not_called()


def test_raw_audio_review_stops_after_one_call_on_billing(tmp_path):
    """Loglardaki '"Ham ses QC yapilamadi" yolu: 26-28 Eyl'de 6 cagri + 2 dk bekleme."""
    stem = tmp_path / "stem.wav"
    stem.write_bytes(b"RIFFwav")
    fake = _FakeGemini({
        critic.QC_MODEL: [RuntimeError(BILLING_402)] * 3,
        critic.QC_MODEL_FALLBACK: [RuntimeError(BILLING_402)] * 3,
    })
    with ExitStack() as stack:
        slept = _gemini_context(stack, fake)
        with pytest.raises(critic.QCApiExhausted) as caught:
            critic._review_raw_native_audio(
                stem, slug=_FIXTURE_SLUG, episode=18, shot=1,
            )
    assert caught.value.reason == "billing"
    assert fake.calls == [critic.QC_MODEL]
    slept.assert_not_called()


def test_billing_alert_names_the_real_cause_and_the_fix():
    sent: list[str] = []
    with mock.patch.object(critic, "_notify",
                           side_effect=lambda text, **_: sent.append(text)):
        critic.notify_qc_exhaustion("Wild Encounter", 18, "billing", 1,
                                    slug=_FIXTURE_SLUG)
    assert len(sent) == 1
    assert "KREDİSİ BİTTİ" in sent[0]
    assert "429" not in sent[0], "odeme arizasi 429 diye raporlandi"
    assert AI_STUDIO_URL in sent[0]
    assert "auto-reload" in sent[0]


# ---------------------------------------------------------------------------
# 3) Kosu basi yoklamasi (probe)
# ---------------------------------------------------------------------------

@pytest.mark.gercek_gemini_yoklamasi
@pytest.mark.parametrize(
    ("outcome", "expected"),
    [
        ("OK", "ok"),
        (RuntimeError(BILLING_402), "billing"),
        (RuntimeError(QUOTA_DAILY), "daily_quota"),
        (RuntimeError(QUOTA_PER_MINUTE), "transient"),
        (RuntimeError(SERVER_503), "transient"),
        (RuntimeError("400 INVALID_ARGUMENT API key not valid"), "auth"),
    ],
)
def test_probe_classifies_the_one_cheap_call(outcome, expected):
    fake = _FakeGemini({critic.QC_MODEL: [outcome]})
    with ExitStack() as stack:
        _gemini_context(stack, fake)
        stack.enter_context(mock.patch.dict("os.environ", {}, clear=False))
        status, _detail = critic.probe_qc_access(_FIXTURE_SLUG)
    assert status == expected
    assert fake.calls == [critic.QC_MODEL], "yoklama tek cagridan fazlasini yapti"


@pytest.mark.gercek_gemini_yoklamasi
def test_probe_without_any_key_is_auth():
    with mock.patch.object(critic, "_qc_api_key", return_value=(None, "GEMINI_API_KEY")):
        status, _ = critic.probe_qc_access(_FIXTURE_SLUG)
    assert status == "auth"


def _qc_bible(slug: str) -> Bible:
    return Bible({
        "series": {
            "slug": slug,
            "title": slug,
            "engine": "omni",
            "state_machine_version": 2,
            "credit_hard_cap": True,
            "credit_hard_cap_value": 800,
            "durable_credit_ledger": True,
            "qc": {"enabled": True, "native_audio_review": True},
        },
        "characters": [],
        "environments": [],
        "props": [],
    })


def _run_with_probe(tmp_path: Path, probe_status: str, producer, *, slug: str,
                    part: dict | None = None):
    meta = _runner_meta(slug, version_parts=3, parts={"1": dict(part or {})})
    bible = _qc_bible(slug)
    plan_path = tmp_path / "part01.json"
    plan_path.write_text("{}", encoding="utf-8")
    alerts: list[str] = []
    with _runner_stack(meta, bible, plan_path, _plan(), producer) as stack:
        probe = stack.enter_context(mock.patch.object(
            critic, "probe_qc_access", return_value=(probe_status, "detay"),
        ))
        reserve = series_runner.credit_gate.reserve
        stack.enter_context(mock.patch.object(
            series_runner, "_series_alert",
            side_effect=lambda _slug, text: alerts.append(text) or True,
        ))
        ok = series_runner.run_next(slug, publish=True, force=True)
        reserved = reserve.call_count
    return ok, meta, alerts, probe, reserved


@pytest.mark.parametrize("status", ["billing", "auth", "daily_quota"])
def test_blocking_probe_spends_nothing_and_leaves_the_part_untouched(tmp_path, status):
    slug = f"probe-block-{status}"
    before = {"status": "qc_retry", "retry_count": 1, "infra_retry_count": 2,
              "first_infra_held_at": "2026-09-26T12:19:03+00:00"}
    producer = mock.Mock(side_effect=AssertionError("ucretli uretim baslatildi"))
    ok, meta, alerts, probe, reserved = _run_with_probe(
        tmp_path, status, producer, slug=slug, part=before,
    )
    assert ok is False, "video cikmayan kosu yesil gorundu"
    producer.assert_not_called()
    assert reserved == 0, "kredi rezervasyonu yapildi"
    assert meta.get_part(1) == before, "yoklama bolum durumunu degistirdi"
    assert meta.next_part == 1
    assert len(alerts) == 1 and "harcanmadı" in alerts[0]
    probe.assert_called_once_with(slug)


def test_billing_probe_alert_tells_the_human_how_to_fix_it(tmp_path):
    producer = mock.Mock(side_effect=AssertionError("ucretli uretim baslatildi"))
    _ok, _meta, alerts, _probe, _ = _run_with_probe(
        tmp_path, "billing", producer, slug="probe-billing-text",
    )
    assert "BİTTİ" in alerts[0]
    assert AI_STUDIO_URL in alerts[0]


@pytest.mark.parametrize("status", ["ok", "transient"])
def test_passing_or_uncertain_probe_lets_production_run(tmp_path, status):
    video = tmp_path / "episode.mp4"
    producer = mock.Mock(return_value=ProduceResult("ok", video))
    ok, meta, _alerts, _probe, reserved = _run_with_probe(
        tmp_path, status, producer, slug=f"probe-pass-{status}",
    )
    producer.assert_called_once()
    assert reserved == 1
    assert ok is True
    assert meta.get_part(1)["status"] == "published"


def test_series_without_qc_is_never_probed(tmp_path):
    slug = "probe-no-qc"
    meta = _runner_meta(slug)
    bible = _qc_bible(slug)
    bible.data["series"]["qc"] = {"enabled": False}
    plan_path = tmp_path / "part01.json"
    plan_path.write_text("{}", encoding="utf-8")
    video = tmp_path / "episode.mp4"
    with _runner_stack(meta, bible, plan_path, _plan(),
                       lambda *a, **k: ProduceResult("ok", video)) as stack:
        probe = stack.enter_context(mock.patch.object(critic, "probe_qc_access"))
        assert series_runner.run_next(slug, publish=True, force=True) is True
    probe.assert_not_called()


# ---------------------------------------------------------------------------
# 4) BILLING hold'u bolumu asla kuyruktan dusurmez
# ---------------------------------------------------------------------------

def _state_meta(part: dict) -> SeriesMeta:
    return SeriesMeta({
        "slug": _FIXTURE_SLUG,
        "base_title": "Gemini Odeme Fixture",
        "total_parts": 30,
        "next_part": 18,
        "status": "active",
        "publish_mode": "auto",
        "upload_profile": "p",
        "platforms": ["youtube"],
        "parts": {"18": part},
    })


def test_billing_hold_burns_no_counter_and_never_goes_to_needs_human():
    """Part 18 senaryosu: altyapi sayaci 5/6, saat 3 gundur isliyor. Yine de dusmez."""
    meta = _state_meta({
        "retry_count": 2,
        "infra_retry_count": series_runner._INFRA_RETRY_LIMIT - 1,
        "first_infra_held_at": "2026-09-20T00:00:00+00:00",
        "status": "qc_retry",
    })
    result = ProduceResult("qc_hold", reason="kredi bitti", reason_code="BILLING")
    with mock.patch.object(meta, "save"), \
            mock.patch.object(series_runner, "_series_alert") as alert:
        advanced = series_runner._record_recoverable_failure(meta, 18, result)
    part = meta.get_part(18)
    assert advanced is False
    assert part["status"] == "qc_retry"
    assert part["retry_count"] == 2, "icerik sayaci odeme yuzunden artti"
    assert part["infra_retry_count"] == series_runner._INFRA_RETRY_LIMIT - 1
    assert part["last_reason_code"] == "BILLING"
    assert meta.next_part == 18
    alert.assert_not_called()  # QC kendi alarmini zaten gonderdi; cift alarm yok


def test_qc_billing_hold_reaches_the_runner_as_billing_through_produce(tmp_path):
    """Uctan uca kod zinciri: critic 'billing' -> produce 'BILLING' -> runner bekler."""
    code = produce._qc_api_reason_code(critic.QCApiExhausted("billing", "402").reason)
    meta = _state_meta({})
    with mock.patch.object(meta, "save"), mock.patch.object(series_runner, "_series_alert"):
        advanced = series_runner._record_recoverable_failure(
            meta, 18, ProduceResult("qc_hold", reason="402", reason_code=code),
        )
    assert code == "BILLING"
    assert advanced is False
    assert "infra_retry_count" not in meta.get_part(18)


# ---------------------------------------------------------------------------
# 5) Altyapi terminali ayni kosuda sonraki bolume para odetmez
# ---------------------------------------------------------------------------

def test_infra_dead_letter_does_not_pay_for_the_next_part_in_the_same_run(tmp_path):
    """28 Eyl: Part 18 needs_human oldu, 60 sn sonra Part 19'a 134 kredi odendi."""
    slug = "infra-no-cascade"
    meta = _runner_meta(slug, version_parts=3, parts={"1": {
        "infra_retry_count": series_runner._INFRA_RETRY_LIMIT - 1,
        "first_infra_held_at": "2026-09-26T12:19:03+00:00",
        "status": "qc_retry",
    }})
    bible = _qc_bible(slug)
    bible.data["series"]["qc"] = {"enabled": False}
    plan_path = tmp_path / "part01.json"
    plan_path.write_text("{}", encoding="utf-8")
    producer = mock.Mock(return_value=ProduceResult(
        "qc_hold", reason="kota", reason_code="QUOTA",
    ))
    with _runner_stack(meta, bible, plan_path, _plan(), producer) as stack:
        stack.enter_context(mock.patch.object(series_runner, "_series_alert"))
        ok = series_runner.run_next(slug, publish=True, force=True)
    assert ok is False
    assert producer.call_count == 1, "ayni kosuda sonraki bolume de para odendi"
    assert meta.get_part(1)["status"] == "needs_human"
    assert meta.next_part == 2, "insana devredilen bolum kuyrugu ilerletmedi"


def test_content_dead_letter_still_continues_to_the_next_part(tmp_path):
    """Icerik yolu DEGISMEDI: icerik reddi sonraki bolumu ayni kosuda uretir."""
    slug = "content-still-continues"
    meta = _runner_meta(slug, version_parts=2, parts={"1": {"retry_count": 2}})
    bible = _qc_bible(slug)
    bible.data["series"]["qc"] = {"enabled": False}
    plan_path = tmp_path / "part01.json"
    plan_path.write_text("{}", encoding="utf-8")
    video = tmp_path / "episode.mp4"
    outcomes = iter([
        ProduceResult("qc_hold", reason="icerik", reason_code="UNKNOWN"),
        ProduceResult("ok", video),
    ])
    producer = mock.Mock(side_effect=lambda *a, **k: next(outcomes))
    with _runner_stack(meta, bible, plan_path, _plan(), producer) as stack:
        stack.enter_context(mock.patch.object(series_runner, "_series_alert"))
        assert series_runner.run_next(slug, publish=True, force=True) is True
    assert producer.call_count == 2


# ---------------------------------------------------------------------------
# 6) Oto-ikmal: tek cagri, anlasilir Turkce sebep
# ---------------------------------------------------------------------------

def test_replenish_fails_fast_and_readable_on_billing():
    fake = _FakeGemini({
        replenish.REPLENISH_MODEL: [RuntimeError(BILLING_402)] * 4,
        replenish.REPLENISH_MODEL_FALLBACK: [RuntimeError(BILLING_402)] * 4,
    })
    with ExitStack() as stack:
        stack.enter_context(mock.patch.dict(sys.modules, fake.modules()))
        stack.enter_context(mock.patch.object(replenish, "GEMINI_API_KEY", "test-key"))
        slept = stack.enter_context(mock.patch.object(replenish.time, "sleep"))
        with pytest.raises(RuntimeError) as caught:
            replenish._gen_json("prompt", "system")
    assert fake.calls == [replenish.REPLENISH_MODEL]
    slept.assert_not_called()
    assert "BİTTİ" in str(caught.value)
    assert AI_STUDIO_URL in str(caught.value)


def test_replenish_still_retries_a_real_transient_429():
    fake = _FakeGemini({
        replenish.REPLENISH_MODEL: [RuntimeError(QUOTA_PER_MINUTE), '{"episodes": []}'],
    })
    with ExitStack() as stack:
        stack.enter_context(mock.patch.dict(sys.modules, fake.modules()))
        stack.enter_context(mock.patch.object(replenish, "GEMINI_API_KEY", "test-key"))
        stack.enter_context(mock.patch.object(replenish.time, "sleep"))
        assert replenish._gen_json("prompt", "system") == {"episodes": []}
    assert fake.calls == [replenish.REPLENISH_MODEL, replenish.REPLENISH_MODEL]


def test_probe_blocking_set_is_exactly_the_non_waitable_failures():
    assert critic.PROBE_BLOCKING == {"billing", "auth", "daily_quota"}
    assert "billing" in critic.QC_HOLD_REASONS
