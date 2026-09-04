"""Bir workflow pytest CAGIRIYORSA, ondan ONCE pytest KURMALIDIR.

Neden statik: yerel makinede pytest zaten kurulu oldugu icin "pytest kostu ve
gecti" temiz bir GitHub runner'i hakkinda hicbir sey KANITLAMAZ. 2026-09-04'te
tam bu bosluk yuzunden aimagine kanalinin TEK gunluk seridi (Fear Slide Daily,
kosu 33897545943) uretime hic baslamadan "No module named pytest" ile oldu:
fear-slide.yml:80 pytest cagiriyordu, requirements.txt icinde pytest yoktu ve
depoda hicbir bagimlilik dosyasinda da yoktu.

Bu test o sinifi kapatir: is akisi dosyalarini okur, pytest cagiran her adim
icin ondan ONCE gelen bir adimin pytest kurdugunu dogrular.
"""
from __future__ import annotations

import pathlib
import unittest

import yaml

WORKFLOW_DIR = pathlib.Path(__file__).resolve().parents[1] / ".github" / "workflows"


def _steps(workflow: dict) -> list[dict]:
    adimlar: list[dict] = []
    for job in (workflow.get("jobs") or {}).values():
        if isinstance(job, dict):
            for step in job.get("steps") or []:
                if isinstance(step, dict):
                    adimlar.append(step)
    return adimlar


def _run_text(step: dict) -> str:
    run = step.get("run")
    return run if isinstance(run, str) else ""


def _cagiriyor_mu(text: str) -> bool:
    """Adim pytest CALISTIRIYOR mu (kurmuyor)."""
    for satir in text.splitlines():
        s = satir.strip()
        if "pytest" not in s:
            continue
        if "pip install" in s or "pip3 install" in s:
            continue
        if "-m pytest" in s or s.startswith("pytest") or " pytest " in f" {s} ":
            return True
    return False


def _kuruyor_mu(text: str) -> bool:
    for satir in text.splitlines():
        s = satir.strip()
        if ("pip install" in s or "pip3 install" in s) and "pytest" in s:
            return True
    return False


class WorkflowTestBagimliligiTests(unittest.TestCase):

    def test_pytest_cagiran_her_workflow_onceden_pytest_kuruyor(self):
        incelenen = 0
        for path in sorted(WORKFLOW_DIR.glob("*.yml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                continue
            adimlar = _steps(data)
            metinler = [_run_text(a) for a in adimlar]
            for i, metin in enumerate(metinler):
                if not _cagiriyor_mu(metin):
                    continue
                incelenen += 1
                onceki_kurulum = any(_kuruyor_mu(m) for m in metinler[:i])
                self.assertTrue(
                    onceki_kurulum,
                    f"{path.name}: {i + 1}. adim pytest cagiriyor ama ondan once "
                    f"pytest kuran bir adim YOK. Temiz bir runner'da "
                    f"'No module named pytest' ile exit 1 verir.",
                )
        self.assertGreater(
            incelenen, 0,
            "hicbir workflow'da pytest cagrisi bulunamadi , test kendini kandiriyor",
        )

    def test_fear_slide_ozellikle_korunuyor(self):
        """Regresyon capasi: aimagine kanalini olduren birebir dosya."""
        path = WORKFLOW_DIR / "fear-slide.yml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        metinler = [_run_text(a) for a in _steps(data)]
        cagri = [i for i, m in enumerate(metinler) if _cagiriyor_mu(m)]
        self.assertTrue(cagri, "fear-slide.yml artik pytest cagirmiyor")
        kurulum = [i for i, m in enumerate(metinler) if _kuruyor_mu(m)]
        self.assertTrue(kurulum, "fear-slide.yml pytest kurmuyor")
        self.assertLess(
            min(kurulum), min(cagri),
            "fear-slide.yml pytest'i cagirdiktan SONRA kuruyor",
        )


if __name__ == "__main__":
    unittest.main()
