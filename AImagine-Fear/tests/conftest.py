"""build.py'yi proje kokunden ithal edilebilir yapar.

Bu olmadan `pytest AImagine-Fear/tests` depo kokunden calistirildiginda
"ModuleNotFoundError: No module named 'build'" veriyor; sadece AImagine-Fear
klasorunun icinden calisiyordu. CI kosusu depo kokunden calisiyor, o yuzden sart.
"""
import sys
from pathlib import Path

import pytest

PROJE_KOKU = Path(__file__).resolve().parent.parent
if str(PROJE_KOKU) not in sys.path:
    sys.path.insert(0, str(PROJE_KOKU))


@pytest.fixture(autouse=True)
def _onay_dosyasini_izole_et(tmp_path_factory, monkeypatch):
    """Hicbir test GERCEK profil_onay.json'a yazamasin.

    Bu koruma bir kazayla ogrenildi: --yayinlama testi KOK'u izole ediyordu ama
    ONAY_DOSYASI modul seviyesinde sabit oldugu icin otomatik onay depoya
    yazildi. O dosya commit'lense cron 1080p'yi hic olculmemisken "dogrulandi"
    sanacakti. Artik her test kendi gecici yoluna yaziyor.
    """
    from tools import gunluk

    monkeypatch.setattr(
        gunluk, "ONAY_DOSYASI",
        tmp_path_factory.mktemp("onay") / "profil_onay.json",
    )
