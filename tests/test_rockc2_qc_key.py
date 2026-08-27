"""ROCK C2: QC anahtarinin uretim/ikmal anahtarindan ayrilabilmesi.

Kota tukenmesi 2026-08-26'da tum QC'yi durdurdu cunku ikmal ve QC AYNI anahtari
paylasiyordu. Bu paket ayrimin calistigini, tanimsizken davranisin degismedigini ve
anahtarin ASLA loglanmadigini kanitlar.
"""

import json
import logging
import pathlib
import sys
import types
import unittest
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from series import critic


class KeyResolutionTests(unittest.TestCase):
    def setUp(self):
        critic._QC_KEY_SOURCE_LOGGED = False

    def test_separate_key_is_preferred_when_present(self):
        with mock.patch.dict("os.environ", {"GEMINI_API_KEY_QC": "qc-key"}), \
                mock.patch.object(critic, "GEMINI_API_KEY", "uretim-key"):
            key, source = critic._qc_api_key()
        self.assertEqual((key, source), ("qc-key", "GEMINI_API_KEY_QC"))

    def test_falls_back_to_the_production_key(self):
        with mock.patch.dict("os.environ", {}, clear=False), \
                mock.patch.object(critic, "GEMINI_API_KEY", "uretim-key"):
            import os
            os.environ.pop("GEMINI_API_KEY_QC", None)
            key, source = critic._qc_api_key()
        self.assertEqual((key, source), ("uretim-key", "GEMINI_API_KEY"))

    def test_blank_separate_key_is_ignored(self):
        with mock.patch.dict("os.environ", {"GEMINI_API_KEY_QC": "   "}), \
                mock.patch.object(critic, "GEMINI_API_KEY", "uretim-key"):
            key, source = critic._qc_api_key()
        self.assertEqual((key, source), ("uretim-key", "GEMINI_API_KEY"))

    def test_key_value_is_never_logged_only_its_source(self):
        with self.assertLogs("youtube", level=logging.INFO) as captured:
            with mock.patch.dict("os.environ", {"GEMINI_API_KEY_QC": "gizli-anahtar-123"}), \
                    mock.patch.object(critic, "GEMINI_API_KEY", "uretim-key"):
                critic._qc_api_key()
        joined = "\n".join(captured.output)
        self.assertIn("GEMINI_API_KEY_QC", joined)
        self.assertNotIn("gizli-anahtar-123", joined)
        self.assertNotIn("uretim-key", joined)

    def test_source_is_logged_once_per_process(self):
        with self.assertLogs("youtube", level=logging.INFO) as captured:
            with mock.patch.dict("os.environ", {"GEMINI_API_KEY_QC": "qc-key"}):
                critic._qc_api_key()
                critic._qc_api_key()
                critic._qc_api_key()
        source_lines = [line for line in captured.output if "QC anahtar kaynagi" in line]
        self.assertEqual(len(source_lines), 1)


class ClientWiringTests(unittest.TestCase):
    """Cozulen anahtar gercekten Gemini istemcisine gidiyor mu?"""

    def setUp(self):
        critic._QC_KEY_SOURCE_LOGGED = False

    @staticmethod
    def _fake_genai(seen):
        part = types.ModuleType("google.genai.types")

        class Part:
            @staticmethod
            def from_text(*, text):
                return {"text": text}

            @staticmethod
            def from_bytes(*, data, mime_type):
                return {"data": data}

        class Config:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

        part.Part = Part
        part.GenerateContentConfig = Config

        class Models:
            def generate_content(self, **_kwargs):
                return SimpleNamespace(text=json.dumps({"artifact_score": 0}))

        genai = types.ModuleType("google.genai")
        genai.types = part

        def client(**kwargs):
            seen.append(kwargs.get("api_key"))
            return SimpleNamespace(models=Models())

        genai.Client = client
        google = types.ModuleType("google")
        google.genai = genai
        return {"google": google, "google.genai": genai, "google.genai.types": part}

    def _review(self, env, tmp):
        seen = []
        with mock.patch.dict("sys.modules", self._fake_genai(seen)), \
                mock.patch.dict("os.environ", env), \
                mock.patch.object(critic, "GEMINI_API_KEY", "uretim-key"), \
                mock.patch.object(critic, "data_dir", return_value=tmp):
            critic._review_frames(
                [], None, "prompt", "notes",
                slug="c2-test", episode=1, shot=1,
            )
        return seen

    def test_review_uses_the_separate_key_when_set(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            seen = self._review({"GEMINI_API_KEY_QC": "qc-key"}, pathlib.Path(td))
        self.assertEqual(seen, ["qc-key"])

    def test_review_falls_back_without_the_separate_key(self):
        import os
        import tempfile
        env = {k: v for k, v in os.environ.items() if k != "GEMINI_API_KEY_QC"}
        with tempfile.TemporaryDirectory() as td:
            with mock.patch.dict("os.environ", env, clear=True):
                seen = self._review({}, pathlib.Path(td))
        self.assertEqual(seen, ["uretim-key"])

    def test_missing_both_keys_is_an_auth_exhaustion(self):
        with mock.patch.object(critic, "GEMINI_API_KEY", ""), \
                mock.patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(critic.QCApiExhausted) as ctx:
                critic._review_frames(
                    [], None, "prompt", "notes", slug="c2", episode=1, shot=1,
                )
        self.assertEqual(ctx.exception.reason, "auth")


if __name__ == "__main__":
    unittest.main()
