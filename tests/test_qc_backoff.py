"""ROCK 3: altyapi arizasi icerik reddi degildir.

Kapsanan sozlesme:
  * sunucunun soyledigi retryDelay okunur, ama tek ve BOLUM GENELI tavanlarla
    sinirlanir (workflow 120 dakikayi asamaz);
  * GUNLUK kota sinyalinde bosuna uyunmaz, ama YEDEK MODEL yine denenir
    (ucretsiz katman kotasi model BASINA ayrilir, bkz. canli 429 govdesi:
    "GenerateRequestsPerDayPerProjectPerModel-FreeTier");
  * C1 hold siniflandirmasi DEGISMEZ: her 429 hala "quota"dir;
  * altyapi kaynakli hold ICERIK sayacini yakmaz, kendi SONLU butcesinden
    harcar ve butce dolunca yine insana devreder.
"""

from __future__ import annotations

import sys
import types as pytypes
from contextlib import ExitStack
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from series import critic, produce, series_runner  # noqa: E402
from series.produce import ProduceResult  # noqa: E402
from series.series_meta import SeriesMeta  # noqa: E402


QUOTA_DAILY = (
    "429 RESOURCE_EXHAUSTED. {'error': {'code': 429, 'message': 'You exceeded your "
    "current quota. Quota exceeded for metric: "
    "generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 20, "
    "model: gemini-3.7-flash', 'status': 'RESOURCE_EXHAUSTED', 'details': [{'@type': "
    "'type.googleapis.com/google.rpc.QuotaFailure', 'violations': [{'quotaId': "
    "'GenerateRequestsPerDayPerProjectPerModel-FreeTier'}]}, {'@type': "
    "'type.googleapis.com/google.rpc.RetryInfo', 'retryDelay': '9s'}]}}"
)
QUOTA_PER_MINUTE = (
    "429 RESOURCE_EXHAUSTED. {'error': {'code': 429, 'message': 'Quota exceeded for "
    "metric: generativelanguage.googleapis.com/generate_content_requests', "
    "'status': 'RESOURCE_EXHAUSTED', 'details': [{'@type': "
    "'type.googleapis.com/google.rpc.RetryInfo', 'retryDelay': '9s'}]}}"
)
SERVER_503 = (
    "503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently "
    "experiencing high demand.', 'status': 'UNAVAILABLE'}}"
)


# ---------------------------------------------------------------------------
# (a)(b)(h)(i)  sunucu gecikmesinin okunmasi ve sinirlanmasi
# ---------------------------------------------------------------------------

def test_server_retry_delay_is_read_from_the_error_body():
    """(a) Sunucu '9 saniye sonra dene' diyorsa merdiven 9'a uyar, 5'e degil."""
    assert critic._retry_delay_from_error(RuntimeError(QUOTA_DAILY)) == pytest.approx(9.0)


def test_retry_delay_falls_back_to_the_fixed_ladder_when_unparseable():
    """(b) Govdede okunabilir gecikme yoksa sabit merdiven kullanilir."""
    assert critic._retry_delay_from_error(RuntimeError(SERVER_503)) is None
    assert critic._retry_delay_from_error(RuntimeError("retryDelay: elma")) is None


def test_millisecond_and_structured_delays_are_understood():
    assert critic._retry_delay_from_error(
        RuntimeError("retryDelay: 1500ms")) == pytest.approx(1.5)
    assert critic._duration_seconds({"retryDelay": {"seconds": 4, "nanos": 500_000_000}}) \
        == pytest.approx(4.5)


def test_absurd_server_delay_cannot_hang_the_workflow():
    """(h) ADVERSARIAL: sunucu 'bir gun sonra dene' derse gun boyu uyunmaz."""
    budget = critic.QCWaitBudget()
    slept: list[float] = []
    with mock.patch.object(critic.time, "sleep", side_effect=slept.append):
        critic._wait_for_qc_retry(
            RuntimeError("503 UNAVAILABLE retryDelay: 86400s"), attempt=1, max_tries=3,
            response_received=False, wait_budget=budget, label="Gorsel QC", model="m",
        )
    assert slept and slept[0] <= critic.QC_MAX_SINGLE_DELAY
    assert budget.waited <= critic.QC_MAX_SINGLE_DELAY


def test_negative_and_zero_delays_never_become_negative_sleeps():
    """(i) ADVERSARIAL: bozuk/negatif gecikme negatif uykuya donusmemeli."""
    budget = critic.QCWaitBudget()
    assert budget.claim(-5.0) == 0.0
    assert budget.claim(0.0) == 0.0
    assert budget.waited == 0.0


# ---------------------------------------------------------------------------
# (c)(j)  tek ve BOLUM GENELI bekleme tavanlari
# ---------------------------------------------------------------------------

def test_single_delay_is_capped():
    """(c) Tek bekleme tavani asilamaz."""
    budget = critic.QCWaitBudget()
    assert budget.claim(10_000.0) == critic.QC_MAX_SINGLE_DELAY


def test_total_wait_budget_is_shared_across_calls_not_per_call():
    """(j) ADVERSARIAL: ROCK 3a'nin kalbi.

    Butce CAGRI BASINA olsaydi bir bolumdeki ~10 QC isiyle carpilir ve 120
    dakikalik workflow limitini asardi. Ayni butce nesnesi paylasildiginda
    toplam bekleme tavani ASLA asilmaz.
    """
    budget = critic.QCWaitBudget()
    for _ in range(50):
        budget.claim(critic.QC_MAX_SINGLE_DELAY)
    assert budget.waited == pytest.approx(critic.QC_MAX_EPISODE_WAIT)
    assert budget.claim(10.0) == 0.0  # tukendikten sonra tek saniye bile yok
    assert critic.QC_MAX_EPISODE_WAIT <= 1800, "bolum butcesi workflow'u yiyecek kadar buyuk"


def test_exhausted_episode_budget_stops_retrying_instead_of_sleeping():
    budget = critic.QCWaitBudget(waited=critic.QC_MAX_EPISODE_WAIT)
    with mock.patch.object(critic.time, "sleep") as slept:
        proceed = critic._wait_for_qc_retry(
            RuntimeError(SERVER_503), attempt=1, max_tries=3,
            response_received=False, wait_budget=budget, label="Gorsel QC", model="m",
        )
    assert proceed is False
    slept.assert_not_called()


# ---------------------------------------------------------------------------
# (d)(k)  gunluk kota: bosuna uyuma, ama yedek modeli birakma
# ---------------------------------------------------------------------------

def test_daily_quota_is_recognised_and_per_minute_quota_is_not():
    assert critic._is_daily_quota_error(RuntimeError(QUOTA_DAILY)) is True
    assert critic._is_daily_quota_error(RuntimeError(QUOTA_PER_MINUTE)) is False
    assert critic._is_daily_quota_error(RuntimeError(SERVER_503)) is False


def test_daily_quota_does_not_sleep():
    """(d) Gunluk tavan saniyeler icinde acilmaz; beklemek bos harcama."""
    with mock.patch.object(critic.time, "sleep") as slept:
        proceed = critic._wait_for_qc_retry(
            RuntimeError(QUOTA_DAILY), attempt=1, max_tries=3,
            response_received=False, wait_budget=critic.QCWaitBudget(),
            label="Ham ses QC", model=critic.QC_MODEL,
        )
    assert proceed is False
    slept.assert_not_called()


def test_per_minute_quota_still_retries_after_waiting():
    """Dakikalik 429 gecicidir; beklenerek asilir."""
    with mock.patch.object(critic.time, "sleep") as slept:
        proceed = critic._wait_for_qc_retry(
            RuntimeError(QUOTA_PER_MINUTE), attempt=1, max_tries=3,
            response_received=False, wait_budget=critic.QCWaitBudget(),
            label="Gorsel QC", model=critic.QC_MODEL,
        )
    assert proceed is True
    slept.assert_called_once()


def test_classification_contract_is_unchanged_every_429_is_quota():
    """(e) C1 tipli sozlesmesi korunur: 429 daima 'quota', 503 daima 'server'."""
    assert critic._classify_api_error(RuntimeError(QUOTA_DAILY)) == "quota"
    assert critic._classify_api_error(RuntimeError(QUOTA_PER_MINUTE)) == "quota"
    assert critic._classify_api_error(RuntimeError(SERVER_503)) == "server"


class _FakeGemini:
    """Model BASINA cagri sayan asgari genai taklidi."""

    def __init__(self, per_model: dict[str, list]):
        self.per_model = {k: list(v) for k, v in per_model.items()}
        self.calls: list[str] = []
        owner = self

        class Part:
            @staticmethod
            def from_text(*, text):
                return {"text": text}

            @staticmethod
            def from_bytes(*, data, mime_type):
                return {"data": data, "mime_type": mime_type}

        class Config:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

        class Models:
            def generate_content(self, *, model, **_kwargs):
                owner.calls.append(model)
                queue = owner.per_model.get(model) or []
                outcome = queue.pop(0) if queue else RuntimeError(SERVER_503)
                if isinstance(outcome, BaseException):
                    raise outcome
                return SimpleNamespace(text=outcome)

        self.types = pytypes.ModuleType("google.genai.types")
        self.types.Part = Part
        self.types.GenerateContentConfig = Config
        self.genai = pytypes.ModuleType("google.genai")
        self.genai.types = self.types
        self.genai.Client = lambda **_kwargs: SimpleNamespace(models=Models())
        self.google = pytypes.ModuleType("google")
        self.google.genai = self.genai

    def modules(self):
        return {
            "google": self.google,
            "google.genai": self.genai,
            "google.genai.types": self.types,
        }


def test_daily_quota_on_primary_model_still_tries_the_fallback_model(tmp_path):
    """(k) ADVERSARIAL, GERCEK REGRESYON.

    Ucretsiz katman gunluk kotasi MODEL BASINA ayrilir. Birincil model gunluk
    kotayi doldurdu diye yedek modeli hic denememek, tam da kota krizinde
    dayanikliligi DUSURUR. Bu test o yolu kilitler.
    """
    frame = tmp_path / "frame.png"
    frame.write_bytes(b"png")
    fake = _FakeGemini({
        critic.QC_MODEL: [RuntimeError(QUOTA_DAILY)],
        critic.QC_MODEL_FALLBACK: ['{"artifact_score": 2, "issues": []}'],
    })
    with ExitStack() as stack:
        stack.enter_context(mock.patch.dict(sys.modules, fake.modules()))
        stack.enter_context(mock.patch.object(critic, "GEMINI_API_KEY", "test-key"))
        stack.enter_context(mock.patch.object(critic, "_strict_log_event", lambda *a, **k: None))
        stack.enter_context(mock.patch.object(critic.time, "sleep"))
        review = critic._review_frames(
            [frame], None, "prompt", "notes",
            slug="unnatural-lab", episode=26, shot=1,
        )
    assert critic.QC_MODEL in fake.calls
    assert critic.QC_MODEL_FALLBACK in fake.calls, "yedek model HIC denenmedi"
    assert review == {"artifact_score": 2, "issues": []}


# ---------------------------------------------------------------------------
# (f)(g)(l)(m)  altyapi sayaci icerik sayacindan ayridir
# ---------------------------------------------------------------------------

def test_qc_api_reason_code_separates_quota_from_transient_infra():
    assert produce._qc_api_reason_code("quota") == "QUOTA"
    assert produce._qc_api_reason_code("server") == "TRANSIENT_INFRA"
    assert produce._qc_api_reason_code("auth") == "UNKNOWN"


# DIKKAT: gercek seri slug'i KULLANILMAZ. `terminalize_and_advance` iceride
# `save_atomic()` cagirir ve slug'dan turetilen GERCEK dosyaya yazar; canli
# unnatural-lab/series.json bu yuzden bir kez ezildi. Hem uydurma slug
# kullaniyoruz hem de iki yazma yolunu da kapatiyoruz.
_FIXTURE_SLUG = "qc-backoff-fixture"


def _meta(part: dict | None = None) -> SeriesMeta:
    return SeriesMeta({
        "slug": _FIXTURE_SLUG,
        "base_title": "QC Backoff Fixture",
        "total_parts": 30,
        "next_part": 26,
        "status": "active",
        "publish_mode": "auto",
        "upload_profile": "p",
        "platforms": ["youtube"],
        "parts": {"26": part if part is not None else {}},
    })


@pytest.fixture(autouse=True)
def _never_touch_real_series_state():
    """Hicbir test gercek seri durumunu diske yazamaz."""
    with mock.patch.object(SeriesMeta, "save"), \
            mock.patch.object(SeriesMeta, "save_atomic"):
        yield


@pytest.mark.parametrize("code", ["QUOTA", "TRANSIENT_INFRA"])
def test_infrastructure_hold_never_burns_the_content_retry_counter(code):
    """(f)(m) Kanal 5 gun karanlik kaldi cunku altyapi arizasi icerik reddi

    gibi sayildi. Icerik sayaci 2/3'te DURMALI, altyapi kendi butcesinden
    harcamali.
    """
    meta = _meta({"retry_count": 2, "status": "qc_retry"})
    result = ProduceResult("qc_hold", reason="kota", reason_code=code)
    with mock.patch.object(meta, "save"), \
            mock.patch.object(series_runner, "_series_alert", return_value=True):
        advanced = series_runner._record_recoverable_failure(meta, 26, result)
    part = meta.get_part(26)
    assert advanced is False, "altyapi arizasi bolumu kuyruktan dusurmemeli"
    assert part["retry_count"] == 2, "ICERIK sayaci altyapi yuzunden artti"
    assert part["infra_retry_count"] == 1
    assert part["status"] == "qc_retry"


def test_infrastructure_budget_is_finite_and_still_escalates_to_a_human():
    """(g) Kalici billing arizasinda sonsuz sessiz dongu OLMAMALI."""
    meta = _meta({"infra_retry_count": series_runner._INFRA_RETRY_LIMIT - 1})
    alerts: list[str] = []
    result = ProduceResult("qc_hold", reason="kota", reason_code="QUOTA")
    with mock.patch.object(meta, "save"), \
            mock.patch.object(meta, "save_atomic", create=True), \
            mock.patch.object(series_runner, "_series_alert",
                              side_effect=lambda slug, text: alerts.append(text) or True):
        advanced = series_runner._record_recoverable_failure(meta, 26, result)
    assert advanced is True
    assert meta.get_part(26)["status"] == "needs_human"
    assert alerts and "needs_human" in alerts[0]


def test_infrastructure_budget_also_expires_by_age(monkeypatch):
    """(l) ADVERSARIAL: sayac dolmasa bile gunlerce suren ariza insana gider."""
    old = "2026-08-25T00:00:00+00:00"
    part = {"infra_retry_count": 1, "first_infra_held_at": old}
    spent, why = series_runner._infra_budget_spent(part, 2)
    assert spent is True
    assert "saattir" in why


def test_fresh_infrastructure_failure_is_not_immediately_terminal():
    part = {"first_infra_held_at": series_runner.datetime.now(
        series_runner.timezone.utc).isoformat()}
    spent, _ = series_runner._infra_budget_spent(part, 1)
    assert spent is False


def test_content_failures_still_dead_letter_at_three():
    """Icerik yolu DEGISMEDI: ucuncu icerik hatasinda insana devredilir."""
    meta = _meta({"retry_count": 2})
    result = ProduceResult("qc_hold", reason="icerik", reason_code="UNKNOWN")
    with mock.patch.object(meta, "save"), \
            mock.patch.object(series_runner, "_series_alert", return_value=True):
        advanced = series_runner._record_recoverable_failure(meta, 26, result)
    assert advanced is True
    assert meta.get_part(26)["status"] == "needs_human"
