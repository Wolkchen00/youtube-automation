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
from types import SimpleNamespace
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from series import critic, produce, replenish, series_runner  # noqa: E402
from series.bible import Bible  # noqa: E402
from series.gemini_odeme import (  # noqa: E402
    AI_STUDIO_URL,
    billing_headline,
    is_billing_error,
    is_spend_cap_error,
)
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
# Google'in faturalama belgesindeki aylik tavan govdeleri: 429 ama beklemeyle acilmaz,
# servis ayin 1'ine kadar durur.
SPEND_CAP_ACCOUNT_429 = (
    "429 RESOURCE_EXHAUSTED. {'error': {'code': 429, 'message': 'Your billing account "
    "has exceeded its monthly spending cap. Please go to AI Studio at "
    "https://aistudio.google.com to manage your billing.', 'status': 'RESOURCE_EXHAUSTED'}}"
)
SPEND_CAP_PROJECT_429 = (
    "429 RESOURCE_EXHAUSTED. {'error': {'code': 429, 'message': 'Your project has "
    "exceeded its monthly spending cap.', 'status': 'RESOURCE_EXHAUSTED'}}"
)
# Ucretsiz katmanin DAKIKALIK 429'u: metrik adi ve quotaId soneki gunlukle AYNI,
# yalniz "PerMinute" ayirir. Gunluk sanilirsa yoklama butun gunu karartir.
FREE_TIER_PER_MINUTE = (
    "429 RESOURCE_EXHAUSTED. {'error': {'code': 429, 'message': 'You exceeded your "
    "current quota. Quota exceeded for metric: "
    "generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 10, "
    "model: gemini-2.5-flash', 'status': 'RESOURCE_EXHAUSTED', 'details': [{'@type': "
    "'type.googleapis.com/google.rpc.QuotaFailure', 'violations': [{'quotaId': "
    "'GenerateRequestsPerMinutePerProjectPerModel-FreeTier'}]}, {'@type': "
    "'type.googleapis.com/google.rpc.RetryInfo', 'retryDelay': '21s'}]}}"
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


@pytest.mark.parametrize("body", [SPEND_CAP_ACCOUNT_429, SPEND_CAP_PROJECT_429])
def test_monthly_spend_cap_429_is_billing_not_a_waitable_quota(body):
    """ADVERSARIAL (denetim bulgusu): tavan 429 doner ama ayin 1'ine kadar acilmaz.

    Eski siniflandirma onu dakikalik kota sayardi; yoklama 'transient' der, Kie
    klibi her gun odenip cope giderdi. Otomatik yukleme acildiktan sonra sirada
    bekleyen sinir tam budur.
    """
    error = RuntimeError(body)
    assert is_spend_cap_error(error)
    assert is_billing_error(error)
    assert critic._classify_api_error(error) == "billing"
    assert billing_headline(body) == "Gemini aylık harcama tavanı DOLDU"


def test_prepay_headline_is_the_402_text():
    assert billing_headline(BILLING_402) == "Gemini ön ödemeli kredisi BİTTİ (402)"


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


def test_delivery_audio_review_stops_after_one_call_on_billing(tmp_path):
    """Ucuncu dongu (teslimat sesi) da ayni sozlesmeye bagli: tek cagri, yedek yok."""
    audio = tmp_path / "delivery.mp3"
    audio.write_bytes(b"ID3mp3")
    fake = _FakeGemini({
        critic.QC_MODEL: [RuntimeError(BILLING_402)] * 3,
        critic.QC_MODEL_FALLBACK: [RuntimeError(BILLING_402)] * 3,
    })
    with ExitStack() as stack:
        slept = _gemini_context(stack, fake)
        with pytest.raises(critic.QCApiExhausted) as caught:
            critic._review_audio(audio, slug=_FIXTURE_SLUG, episode=18)
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
    assert "ÖDEME SINIRI" in sent[0]
    assert "kredi bitti" in sent[0] and "harcama" in sent[0]
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
        (RuntimeError(QUOTA_PER_MINUTE), "transient"),
        (RuntimeError(FREE_TIER_PER_MINUTE), "transient"),
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
def test_probe_checks_the_same_billing_account_qc_will_use():
    """Yoklama QC'nin anahtariyla yapilmali; yoksa baska hesabi yoklar, QC yine 402 yer."""
    seen: list[str] = []
    fake = _FakeGemini({critic.QC_MODEL: ["OK"]})
    fake.genai.Client = lambda **kwargs: (
        seen.append(kwargs.get("api_key")) or SimpleNamespace(models=_ModelsOK())
    )
    env = {
        "GEMINI_API_KEY_QC_GEMINI_ODEME_FIXTURE": "seri-qc-anahtari",
        "GEMINI_API_KEY_QC": "filo-qc-anahtari",
    }
    with ExitStack() as stack:
        stack.enter_context(mock.patch.dict(sys.modules, fake.modules()))
        stack.enter_context(mock.patch.object(critic, "GEMINI_API_KEY", "uretim-anahtari"))
        stack.enter_context(mock.patch.dict("os.environ", env, clear=False))
        status, _ = critic.probe_qc_access(_FIXTURE_SLUG)
    assert status == "ok"
    assert seen == ["seri-qc-anahtari"]


class _ModelsOK:
    def generate_content(self, **_kwargs):
        return SimpleNamespace(text="")


def test_free_tier_per_minute_limit_is_not_a_daily_limit():
    """Ucretsiz katmana donuste (28 Eyl) bu ayrim canli: dakikalik takilma beklenir."""
    assert critic._is_daily_quota_error(RuntimeError(QUOTA_DAILY)) is True
    assert critic._is_daily_quota_error(RuntimeError(FREE_TIER_PER_MINUTE)) is False


@pytest.mark.gercek_gemini_yoklamasi
def test_probe_falls_back_when_only_the_primary_models_day_is_used_up():
    """Ucretsiz katmanda kota model basina: QC yedek modelle gecer, gun kararmamali."""
    fake = _FakeGemini({
        critic.QC_MODEL: [RuntimeError(QUOTA_DAILY)],
        critic.QC_MODEL_FALLBACK: ["OK"],
    })
    with ExitStack() as stack:
        _gemini_context(stack, fake)
        status, _ = critic.probe_qc_access(_FIXTURE_SLUG)
    assert status == "ok"
    assert fake.calls == [critic.QC_MODEL, critic.QC_MODEL_FALLBACK]


@pytest.mark.gercek_gemini_yoklamasi
def test_probe_blocks_only_when_both_models_are_out_for_the_day():
    fake = _FakeGemini({
        critic.QC_MODEL: [RuntimeError(QUOTA_DAILY)],
        critic.QC_MODEL_FALLBACK: [RuntimeError(QUOTA_DAILY)],
    })
    with ExitStack() as stack:
        _gemini_context(stack, fake)
        status, _ = critic.probe_qc_access(_FIXTURE_SLUG)
    assert status == "daily_quota"


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
    # Denenmeyen gun altyapi yas saatine yazilmaz; odeme engeli gorulduyse bir
    # sonraki yoklama iki asamali olsun diye isaretlenir. Baska HICBIR alan degismez.
    after = dict(meta.get_part(1))
    seen = after.pop("billing_seen_at", None)
    expected = {k: v for k, v in before.items() if k != "first_infra_held_at"}
    assert after == expected, "yoklama bolum durumunu degistirdi"
    assert (seen is not None) == (status == "billing")
    assert meta.next_part == 1
    assert len(alerts) == 1 and "harcanmadı" in alerts[0]
    probe.assert_called_once_with(slug, confirm_after_s=0.0)


def test_fail_open_series_without_gates_is_not_blocked_by_the_probe(tmp_path):
    """P9: zorunlu kapisiz + api_fail_open seri Gemini yokken QC'siz yayini SECMISTIR."""
    slug = "probe-fail-open"
    meta = _runner_meta(slug, version_parts=3, parts={"1": {}})
    bible = _qc_bible(slug)
    bible.data["series"]["qc"] = {"enabled": True, "api_fail_open": True}
    plan_path = tmp_path / "part01.json"
    plan_path.write_text("{}", encoding="utf-8")
    video = tmp_path / "episode.mp4"
    producer = mock.Mock(return_value=ProduceResult("ok", video))
    with _runner_stack(meta, bible, plan_path, _plan(), producer) as stack:
        stack.enter_context(mock.patch.object(
            critic, "probe_qc_access", return_value=("billing", BILLING_402),
        ))
        stack.enter_context(mock.patch.object(series_runner, "_series_alert"))
        assert series_runner.run_next(slug, publish=True, force=True) is True
    producer.assert_called_once()


def test_spend_cap_probe_alert_says_cap_not_credits(tmp_path):
    slug = "probe-spend-cap"
    meta = _runner_meta(slug, version_parts=3, parts={"1": {}})
    bible = _qc_bible(slug)
    plan_path = tmp_path / "part01.json"
    plan_path.write_text("{}", encoding="utf-8")
    alerts: list[str] = []
    producer = mock.Mock(side_effect=AssertionError("ucretli uretim baslatildi"))
    with _runner_stack(meta, bible, plan_path, _plan(), producer) as stack:
        stack.enter_context(mock.patch.object(
            critic, "probe_qc_access", return_value=("billing", SPEND_CAP_ACCOUNT_429[:300]),
        ))
        stack.enter_context(mock.patch.object(
            series_runner, "_series_alert",
            side_effect=lambda _slug, text: alerts.append(text) or True,
        ))
        assert series_runner.run_next(slug, publish=True, force=True) is False
    producer.assert_not_called()
    assert "harcama tavanı DOLDU" in alerts[0]


@pytest.mark.gercek_gemini_yoklamasi
def test_confirmed_probe_catches_a_flickering_billing_window():
    """28 Eyl 18:45: bakiye sifirken tek yoklama gecti, 109 sn sonra QC 402 yedi.

    Iki asamali yoklamada ilk "ok" tek basina yetmez; ikinci cagri 402 ise
    sonuc billing olur ve aradaki bekleme gercekten uygulanir.
    """
    fake = _FakeGemini({critic.QC_MODEL: ["OK", RuntimeError(BILLING_402)]})
    with ExitStack() as stack:
        slept = _gemini_context(stack, fake)
        status, _ = critic.probe_qc_access(_FIXTURE_SLUG, confirm_after_s=75.0)
    assert status == "billing"
    assert fake.calls == [critic.QC_MODEL, critic.QC_MODEL]
    slept.assert_called_once_with(75.0)


@pytest.mark.gercek_gemini_yoklamasi
def test_normal_probe_is_a_single_call_without_waiting():
    fake = _FakeGemini({critic.QC_MODEL: ["OK"]})
    with ExitStack() as stack:
        slept = _gemini_context(stack, fake)
        status, _ = critic.probe_qc_access(_FIXTURE_SLUG)
    assert status == "ok"
    assert fake.calls == [critic.QC_MODEL]
    slept.assert_not_called()


@pytest.mark.parametrize("part", [
    {"status": "qc_retry", "billing_seen_at": "2026-09-28T18:47:34+00:00"},
    # cd617b5 oncesi kod billing_seen_at yazmiyordu (still-home Part 9 kaydi).
    {"status": "qc_retry", "last_reason_code": "BILLING", "hold_reason": "billing"},
])
def test_part_that_saw_billing_gets_the_two_step_probe(tmp_path, part):
    slug = "probe-two-step"
    video = tmp_path / "episode.mp4"
    producer = mock.Mock(return_value=ProduceResult("ok", video))
    _ok, _meta, _alerts, probe, _ = _run_with_probe(
        tmp_path, "ok", producer, slug=slug, part=part,
    )
    probe.assert_called_once_with(
        slug, confirm_after_s=series_runner._BILLING_CONFIRM_SECONDS,
    )
    assert series_runner._BILLING_CONFIRM_SECONDS >= 60


def test_billing_hold_marks_the_part_for_the_two_step_probe():
    meta = _state_meta({"status": "qc_retry"})
    with mock.patch.object(meta, "save"), mock.patch.object(series_runner, "_series_alert"):
        series_runner._record_recoverable_failure(
            meta, 18, ProduceResult("qc_hold", reason="402", reason_code="BILLING"),
        )
    assert meta.get_part(18).get("billing_seen_at")


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


def test_after_a_billing_outage_one_ordinary_infra_error_does_not_drop_the_part():
    """Denetim bulgusu: odeme beklenen gunler 48 saatlik altyapi saatini doldurmamali.

    Gun 0 gercek altyapi arizasi (saat baslar), 3 gun 402, kredi yuklenir, ilk
    siradan 503: eski kodda bolum needs_human olup kuyruktan dusuyordu.
    """
    meta = _state_meta({
        "infra_retry_count": 1,
        "first_infra_held_at": "2026-09-20T00:00:00+00:00",
        "status": "qc_retry",
    })
    with mock.patch.object(meta, "save"), mock.patch.object(series_runner, "_series_alert"):
        series_runner._record_recoverable_failure(
            meta, 18, ProduceResult("qc_hold", reason="402", reason_code="BILLING"),
        )
        advanced = series_runner._record_recoverable_failure(
            meta, 18, ProduceResult("qc_hold", reason="503", reason_code="TRANSIENT_INFRA"),
        )
    part = meta.get_part(18)
    assert advanced is False, "kredi yuklendikten sonraki ilk 503 bolumu dusurdu"
    assert part["status"] == "qc_retry"
    assert part["infra_retry_count"] == 2
    assert meta.next_part == 18


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


def test_retry_delay_ignores_the_http_code_in_the_sdk_details_body():
    """Denetim bulgusu: gercek SDK hatasi error.details'e tum govdeyi koyar.

    Ilk ciplak sayi HTTP kodudur (429/503); onu saniye sanmak her gecici hatayi
    30 sn tavanina uyutuyordu. Gercek bir google.genai hatasiyla sinanir.
    """
    errors = pytest.importorskip("google.genai.errors")
    body_429 = {"error": {"code": 429, "message": "Quota exceeded", "status": "RESOURCE_EXHAUSTED",
                          "details": [{"@type": "type.googleapis.com/google.rpc.RetryInfo",
                                       "retryDelay": "9s"}]}}
    body_503 = {"error": {"code": 503, "message": "high demand", "status": "UNAVAILABLE"}}
    assert critic._retry_delay_from_error(errors.ClientError(429, body_429)) == pytest.approx(9.0)
    assert critic._retry_delay_from_error(errors.ServerError(503, body_503)) is None


def test_probe_blocking_set_is_exactly_the_non_waitable_failures():
    assert critic.PROBE_BLOCKING == {"billing", "auth", "daily_quota"}
    assert "billing" in critic.QC_HOLD_REASONS


def test_billing_hold_does_not_re_review_the_same_clip(tmp_path):
    """28 Eyl still-home: ayni klip odeme arizasinda uc kez denetlendi (3 x 402)."""
    bible = _qc_bible(_FIXTURE_SLUG)
    bible.data["series"]["qc"] = {"enabled": True, "qc_review_retries": 2}
    clip = tmp_path / "shot_01.mp4"
    clip.write_bytes(b"clip")
    with mock.patch.object(
        critic, "review_clip",
        side_effect=critic.QCApiExhausted("billing", BILLING_402),
    ) as review, mock.patch.object(critic, "_log_event"), \
            mock.patch.object(critic, "_notify"), \
            mock.patch.object(critic.time, "sleep"):
        _path, _credits, status = critic.qc_shot(
            bible, {"n": 1}, clip, "prompt", None, episode=9, budget={"left": 0},
        )
    assert status == "hold"
    assert review.call_count == 1, "odeme arizasinda ayni klip yeniden denetlendi"



# ---------------------------------------------------------------------------
# 7) Ucretsiz katman: dort modellik sira (28 Eyl 2026)
# ---------------------------------------------------------------------------

@pytest.mark.gercek_model_sirasi
def test_production_chain_has_four_distinct_models_and_skips_retired_2_5():
    """Yeni projede gemini-2.5-flash 404 ("no longer available to new users")."""
    assert len(critic.QC_MODELS) == 4
    assert len(set(critic.QC_MODELS)) == 4, "ayni model iki kez = ayni kota"
    assert "gemini-2.5-flash" not in critic.QC_MODELS
    assert critic.QC_MODEL == critic.QC_MODELS[0]


@pytest.mark.gercek_model_sirasi
def test_replenish_starts_on_models_qc_does_not_lead_with():
    """Bolum yazari QC'nin ilk iki modelinin gunluk hakkini yemesin."""
    assert replenish.REPLENISH_MODELS[0] not in critic.QC_MODELS[:2]
    assert replenish.REPLENISH_MODELS[1] not in critic.QC_MODELS[:2]
    assert "gemini-2.5-flash" not in replenish.REPLENISH_MODELS


def test_model_chain_can_be_changed_without_code(monkeypatch):
    from series.gemini_odeme import model_chain

    monkeypatch.setenv("GEMINI_QC_MODELS", " gemini-9-flash , gemini-8-flash ,")
    assert model_chain("GEMINI_QC_MODELS", ("x",)) == ("gemini-9-flash", "gemini-8-flash")
    monkeypatch.setenv("GEMINI_QC_MODELS", "  ")
    assert model_chain("GEMINI_QC_MODELS", ("x",)) == ("x",)


_CHAIN = ("m-a", "m-b", "m-c", "m-d")


@pytest.mark.gercek_model_sirasi
@pytest.mark.gercek_gemini_yoklamasi
def test_probe_walks_the_whole_chain_before_calling_a_day_lost(monkeypatch):
    monkeypatch.setattr(critic, "QC_MODELS", _CHAIN)
    fake = _FakeGemini({
        "m-a": [RuntimeError(QUOTA_DAILY)],
        "m-b": [RuntimeError(QUOTA_DAILY)],
        "m-c": [RuntimeError(QUOTA_DAILY)],
        "m-d": ["OK"],
    })
    with ExitStack() as stack:
        _gemini_context(stack, fake)
        status, _ = critic.probe_qc_access(_FIXTURE_SLUG)
    assert status == "ok"
    assert fake.calls == list(_CHAIN)


@pytest.mark.gercek_model_sirasi
@pytest.mark.gercek_gemini_yoklamasi
def test_probe_blocks_when_every_model_in_the_chain_is_out_for_the_day(monkeypatch):
    monkeypatch.setattr(critic, "QC_MODELS", _CHAIN)
    fake = _FakeGemini({m: [RuntimeError(QUOTA_DAILY)] for m in _CHAIN})
    with ExitStack() as stack:
        _gemini_context(stack, fake)
        status, _ = critic.probe_qc_access(_FIXTURE_SLUG)
    assert status == "daily_quota"
    assert fake.calls == list(_CHAIN)


@pytest.mark.gercek_model_sirasi
def test_visual_qc_survives_high_demand_on_the_first_two_models(tmp_path, monkeypatch):
    """28 Eyl canli olcum: 3.8 ve 3.7 "high demand" 503, 3.6 hemen cevap verdi."""
    monkeypatch.setattr(critic, "QC_MODELS", _CHAIN)
    frame = tmp_path / "frame.png"
    frame.write_bytes(b"png")
    fake = _FakeGemini({
        "m-a": [RuntimeError(SERVER_503)] * 3,
        "m-b": [RuntimeError(SERVER_503)] * 3,
        "m-c": ['{"artifact_score": 1, "issues": []}'],
    })
    with ExitStack() as stack:
        _gemini_context(stack, fake)
        review = critic._review_frames(
            [frame], None, "prompt", "notes",
            slug=_FIXTURE_SLUG, episode=18, shot=1,
        )
    assert review == {"artifact_score": 1, "issues": []}
    assert fake.calls[-1] == "m-c"
    assert "m-d" not in fake.calls
