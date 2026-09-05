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


class PipefailTests(unittest.TestCase):
    """`| tee` ile borulanan her adim pipefail ISTEMELIDIR.

    GitHub Actions varsayilan kabugu `bash -e` (pipefail YOK). `python ... | tee`
    kurulumunda boru hattinin cikis kodu `tee`'nin 0'i olur ve python'un exit 1'i
    SESSIZCE yutulur. 2026-09-01..04 arasinda Galactic'in oto-ikmali dort gun
    ust uste basarisiz oldu ama adim hep yesil kaldi; ariza ancak YouTube RSS
    okunarak gorulebildi. `shell: bash` bu maskeyi kaldirir.
    """

    # HENUZ DUZELTILMEMIS adimlar. Sessizce atlanmiyorlar: burada ADIYLA
    # duruyorlar ki gorunur kalsinlar ve liste BUYUYEMESIN (yeni bir ihlal
    # eklenirse test kirmizi olur). Bunlar kanal yayin hattinda DEGIL; pipefail
    # eklemek kosuyu o adimda durdurabilecegi icin ayri bir cevrimde,
    # devaminda ne oldugu incelenerek yapilacak. RF-ISSUES'a yazildi.
    BILINEN_ACIKLAR = {
        ("analytics.yml", "Take daily snapshot"),
        ("analytics.yml", "Generate weekly report"),
        ("calibrate.yml", "Measure and calibrate"),
        ("cleanup.yml", "Run cleanup monitor"),
        ("series-approve.yml", "Check approvals + publish"),
    }

    def test_tee_ile_borulanan_adimlar_pipefail_istiyor(self):
        eksik = []
        incelenen = 0
        for path in sorted(WORKFLOW_DIR.glob("*.yml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                continue
            for step in _steps(data):
                run = _run_text(step)
                if "| tee" not in run:
                    continue
                incelenen += 1
                kabuk = str(step.get("shell") or "")
                if "bash" in kabuk:
                    continue
                anahtar = (path.name, str(step.get("name") or ""))
                if anahtar in self.BILINEN_ACIKLAR:
                    continue
                eksik.append(f"{path.name}: {step.get('name') or run[:50]!r}")
        self.assertFalse(
            eksik,
            "su adimlar `| tee` kullaniyor ama `shell: bash` (pipefail) yok, "
            "yani python'un exit kodu yutulur: " + "; ".join(eksik),
        )
        self.assertGreater(incelenen, 0, "hic tee'li adim bulunamadi , test kendini kandiriyor")

    def test_bilinen_aciklar_hala_gercek(self):
        """Liste curumesin: duzeltilen bir adim burada kalmamali."""
        mevcut = set()
        for path in sorted(WORKFLOW_DIR.glob("*.yml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                continue
            for step in _steps(data):
                if "| tee" not in _run_text(step):
                    continue
                if "bash" in str(step.get("shell") or ""):
                    continue
                mevcut.add((path.name, str(step.get("name") or "")))
        cozulmus = self.BILINEN_ACIKLAR - mevcut
        self.assertFalse(
            cozulmus,
            f"bu adimlar artik duzelmis, BILINEN_ACIKLAR listesinden cikarilmali: {cozulmus}",
        )


class KanalAlarmiTests(unittest.TestCase):
    """Her KANAL hatti patlayinca Telegram'a haber vermeli.

    2026-09-04 denetimi: dort kanal workflow'undan yalniz unnatural-lab
    bildirim gonderiyordu. Digerleri sessizdi, yani Galactic / Shadowed History /
    AImagine kirilirsa Ihsan HIC ogrenmezdi , Galactic'i dort gun sessizce
    olduren korlugun ta kendisi. Uzaktayken tek gorunurluk Telegram'dir.
    """

    KANAL_HATLARI = {
        "event-horizon.yml", "flashpoints.yml",
        "unnatural-lab.yml", "fear-slide.yml",
    }

    def test_her_kanal_hatti_basarisizlikta_telegrama_haber_veriyor(self):
        eksik = []
        for ad in sorted(self.KANAL_HATLARI):
            data = yaml.safe_load((WORKFLOW_DIR / ad).read_text(encoding="utf-8"))
            adimlar = _steps(data)
            tg = [s for s in adimlar if "api.telegram.org" in _run_text(s)]
            if not tg:
                eksik.append(f"{ad}: hic Telegram bildirimi yok")
                continue
            if not any("failure()" in str(s.get("if") or "") for s in tg):
                eksik.append(f"{ad}: bildirim var ama 'if: failure()' degil")
        self.assertFalse(
            eksik,
            "bu kanal hatlari sessizce olebilir: " + "; ".join(eksik),
        )

    def test_bildirim_kosunun_sonucunu_degistirmiyor(self):
        """Telegram ulasilamazsa kosu KIRMIZI olmamali (yanlis alarm uretmesin)."""
        for ad in sorted(self.KANAL_HATLARI):
            data = yaml.safe_load((WORKFLOW_DIR / ad).read_text(encoding="utf-8"))
            for s in _steps(data):
                if "api.telegram.org" in _run_text(s):
                    self.assertTrue(
                        s.get("continue-on-error"),
                        f"{ad}: Telegram adimi continue-on-error tasimiyor",
                    )


if __name__ == "__main__":
    unittest.main()
