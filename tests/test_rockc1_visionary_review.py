"""ROCK C1 Seviye-10 incelemesi (Visionary): fail-open muafiyetinin SINIRLARI.

Codex'in kendi paketi fail-closed yolu kanitliyor. Bu dosya incelemede acilan
ucuncu yolu kanitlar: canli ama zorunlu kapisi olmayan seriler acik muafiyetle
yayinda kalir, muafiyet ilan edilmis bir kapiyi delemez, ve ucretli cagri asla
kalici kayit yazilmadan yapilmaz.
"""

import json
import pathlib
import sys
import unittest
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from series import critic
from test_rockc1_qc_instrumentation import EpisodeHarness, FakeGemini


QUOTA = "429 RESOURCE_EXHAUSTED"


class FailOpenScopeTests(EpisodeHarness):
    """Muafiyet dogru yerde calisiyor, yanlis yerde calismiyor."""

    def _set_qc(self, **extra):
        path = self.folder / "bible.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["series"]["qc"].update(extra)
        path.write_text(json.dumps(data), encoding="utf-8")

    def test_explicit_exemption_keeps_episode_alive_but_never_silent(self):
        self._set_qc(api_fail_open=True)
        fake = FakeGemini([RuntimeError(QUOTA)] * 6)
        with self.run_context(fake), mock.patch.object(critic, "_notify") as notify:
            result = self.produce(fake)

        self.assertNotEqual(result.status, "qc_hold")
        events = [event.get("event") for event in self.journal()]
        self.assertIn("qc_api_exhausted_open", events)
        self.assertIn("qc_api_attempt", events)
        self.assertTrue(notify.called, "muafiyet sessiz gecise donusemez")
        alerts = [call.args[0] for call in notify.call_args_list]
        quota_alerts = [text for text in alerts if "QC KOTA" in text]
        self.assertTrue(quota_alerts, f"kota alarmi gonderilmedi: {alerts}")
        # Muafiyetli seride mesaj "yayinlanmayacak" DEMEMELI: bolum yayina gidiyor.
        self.assertNotIn("yayınlanmayacak", quota_alerts[0])
        self.assertIn("QC'SIZ devam ediyor", quota_alerts[0].replace("İ", "I"))
        # Operator, kabul edilen klibin sebebini de gormeli.
        self.assertTrue(any("quota" in text for text in alerts))

    def test_declared_gate_cannot_buy_an_exemption(self):
        self._set_qc(api_fail_open=True, require_no_face=True)
        fake = FakeGemini([RuntimeError(QUOTA)] * 6)
        with self.run_context(fake), mock.patch.object(critic, "_notify"):
            result = self.produce(fake)

        self.assertEqual((result.status, result.reason), ("qc_hold", "quota"))

    def test_default_without_flag_stays_fail_closed(self):
        fake = FakeGemini([RuntimeError(QUOTA)] * 6)
        with self.run_context(fake), mock.patch.object(critic, "_notify"):
            result = self.produce(fake)

        self.assertEqual((result.status, result.reason), ("qc_hold", "quota"))


class AttemptOrderingTests(unittest.TestCase):
    """Kalici kayit yazilamiyorsa kotali cagri HIC yapilmaz."""

    def test_no_api_call_when_attempt_cannot_be_recorded(self):
        calls = []

        class Models:
            def generate_content(self, **kwargs):
                calls.append(kwargs)
                return SimpleNamespace(text="{}")

        client = SimpleNamespace(models=Models())
        with mock.patch.object(critic, "_strict_log_event", side_effect=OSError("disk dolu")):
            with self.assertRaises(critic.QCApiExhausted) as ctx:
                critic._generate_content_recorded(
                    client, model="m", contents=[], config=None,
                    slug="s", episode=1, shot=1,
                    task_type="visual_review", is_fallback=False,
                )
        self.assertEqual(ctx.exception.reason, "logging")
        self.assertEqual(calls, [], "kayit yazilamadan cagri yapildi")


class FleetExemptionInvariantTests(unittest.TestCase):
    """Degismez: muafiyet yalnizca zorunlu kapisi OLMAYAN seride bulunabilir."""

    def test_exemption_only_where_no_mandatory_gate_is_declared(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        checked = 0
        for path in root.glob("*/*/bible.json"):
            if "output" in path.parts or "_archive" in path.parts:
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            qc = (data.get("series") or {}).get("qc") or {}
            if not qc.get("api_fail_open"):
                continue
            checked += 1
            self.assertFalse(
                critic._has_mandatory_gate(qc),
                f"{path}: acik muafiyet ile zorunlu kapi bir arada olamaz",
            )
        self.assertGreater(checked, 0, "muafiyetli seri kalmadiysa bu test guncellenmeli")


if __name__ == "__main__":
    unittest.main()
