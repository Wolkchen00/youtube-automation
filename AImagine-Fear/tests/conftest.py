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
def _durum_dosyalarini_izole_et(tmp_path_factory, monkeypatch):
    """Hicbir test gunluk.py'nin YAZDIGI durum dosyalarina dokunamasin.

    Bu koruma iki kez kaza sonucu ogrenildi. Testler KOK'u izole ediyordu ama
    bu yollar modul seviyesinde sabit oldugu icin gercek depoya yaziliyordu:

      profil_onay.json      -> commit'lenseydi cron 1080p'yi hic olculmemisken
                               "dogrulandi" sayardi.
      kanarya_basarisiz.json -> commit'lenseydi cron kanaryayi HIC calistiramaz,
                               kanal sessizce dururdu.
      kredi_bekliyor.json    -> commit'lenseydi telafi cron'u sahte bir kredi
                               durusu icin para harcayabilirdi.

    Yeni bir durum dosyasi eklenirse BURAYA da eklenmeli.
    """
    from tools import gunluk

    kok = tmp_path_factory.mktemp("durum")
    for ad in ("ONAY_DOSYASI", "KANARYA_KILIDI", "KREDI_BEKLIYOR"):
        monkeypatch.setattr(gunluk, ad, kok / getattr(gunluk, ad).name)
