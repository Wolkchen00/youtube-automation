"""RF-PLAN-TEKPLAN10: BAGIMSIZ advers testler (Visionary Level 10 denetimi).

Codex'in kendi test paketinin kacirdigi sinir durumlarini kilitler:
- tek cekimde object_card KIMLIK alanlarinda yapim dili hala yasak mi
- alt sinirin 2'den 1'e inmesi 2/6 sinirlarini bozdu mu, 0 ve 7 hala reddediliyor mu
- tek cekim nihai sistem promptunda sis ve sabit kamera dili GERCEKTEN yok mu
- tek cekimde cekim promptunda yapim dili serbest (kasitli davranis, kilitlenir)
- uc cekimli Plato'nun erken-ifsa korumasi bozulmadi mi
"""

from __future__ import annotations

import re

import pytest

from tests.test_rf_tekplan_single_shot import (
    _bible, _cfg, _episode, _meta, _system,
)
from series import replenish


def _dogrula(episodes, cfg, batch=1):
    return replenish._validate_batch(
        episodes, _bible(), 8, batch, set(), cfg, history=[]
    )


# ---------------------------------------------------------------- kimlik alanlari

@pytest.mark.parametrize("kirli_ad", [
    "animatronic lion",
    "giant lion puppet",
    "fibreglass lion",
])
def test_tek_cekimde_object_card_adinda_yapim_dili_hala_reddedilir(kirli_ad):
    """Tek cekimde cekim-promptu kontrolu kapatildi; KIMLIK alanlari kapali kalmali.

    Plan sarti: 'Yapim dili yaratik kimlik alanlarinda yasak kalir.'
    Bu kapi duserse Gemini 'animatronic lion' yazar, referans gorsel bir kukla
    uretir ve ifsa daha ilk karede harcanir.
    """
    bolum = _episode()
    bolum["object_card"]["name"] = kirli_ad
    hatalar = _dogrula([bolum], _cfg())
    assert any("object_card canli hayvani tarif etmeli" in h for h in hatalar), (
        f"{kirli_ad!r} kimlik alaninda gecti, hatalar: {hatalar}"
    )


def test_tek_cekimde_object_card_descriptorunda_yapim_dili_hala_reddedilir():
    bolum = _episode()
    bolum["object_card"]["descriptor"] = (
        "a colossal tawny lion four metres tall built over a steel armature with "
        "silicone skin amber eyes and ivory teeth"
    )
    hatalar = _dogrula([bolum], _cfg())
    assert any("object_card canli hayvani tarif etmeli" in h for h in hatalar), hatalar


def test_tek_cekimde_cekim_promptunda_yapim_dili_SERBEST():
    """Kasitli davranis kilidi: ifsa ayni cekimde oldugu icin prop dili gerekli.

    Bu test, birinin 'tutarlilik olsun' diye kapiyi tek cekime de geri
    acmasini engeller: acilirsa tek cekim formati uretilemez hale gelir.
    """
    bolum = _episode()
    assert "practical hinged jaws" in bolum["shots"][0]["prompt"]
    assert _dogrula([bolum], _cfg()) == []


# ---------------------------------------------------------------- cekim sayisi sinirlari

def test_iki_cekim_hala_kabul_edilir():
    """Alt sinir 2'den 1'e indi; 2 bozulmamis olmali."""
    cfg = _cfg(shots=2, shot_plan=["BEAT ONE.", "BEAT TWO."])
    bolum = _episode()
    ikinci = dict(bolum["shots"][0])
    ikinci["n"] = 2
    bolum["shots"] = [bolum["shots"][0], ikinci]
    hatalar = _dogrula([bolum], cfg)
    assert not any("çekim sayısı 1-6 olmalı" in h for h in hatalar), hatalar


@pytest.mark.parametrize("adet", [0, 7])
def test_sifir_ve_yedi_cekim_hala_reddedilir(adet):
    """Alt siniri 1'e indirmek 0'i ve ust siniri serbest birakmamali."""
    cfg = _cfg(shots=adet or 1, shot_plan=["BEAT."] * max(adet, 1))
    bolum = _episode()
    tek = bolum["shots"][0]
    bolum["shots"] = [dict(tek, n=i + 1) for i in range(adet)]
    hatalar = _dogrula([bolum], cfg)
    # Iki ayri kapi reddedebilir: batch dogrulayici ("cekim sayisi 1-6") ya da
    # cfg dogrulayici ("shots 1..6"). Ikisi de kabul; onemli olan GECMEMESI.
    assert any(("çekim sayısı 1-6 olmalı" in h) or ("shots 1..6" in h)
               for h in hatalar), f"{adet} cekim gecti, hatalar: {hatalar}"


# ---------------------------------------------------------------- nihai prompt hijyeni

YASAK_DESENLER = [
    r"\bhaze\b",
    r"\bfog\b",
    r"locked-off",
    r"no withheld reveal",
    r"no closing gesture",
    r"voice is added later as narration",
    r"the score is the only voice",
    r"green screen",
]


@pytest.mark.parametrize("desen", YASAK_DESENLER)
def test_tek_cekim_sistem_promptunda_yasak_dil_yok(desen):
    """Olculmus bulgu: sis kaybedenlerde var, kazananlarda yok.

    Bu desenlerin herhangi biri nihai prompta sizarsa Gemini sisli / sabit
    kameral / anlatim vaatli bir bolum yazar.
    """
    system = _system()
    bulunan = re.findall(desen, system, re.I)
    assert not bulunan, f"{desen!r} nihai promptta bulundu: {bulunan}"


@pytest.mark.parametrize("zorunlu", ["blue screen", "push-in"])
def test_tek_cekim_sistem_promptunda_zorunlu_dil_var(zorunlu):
    assert zorunlu.lower() in _system().lower(), f"{zorunlu!r} nihai promptta yok"


# ---------------------------------------------------------------- cok cekim regresyonu

def test_uc_cekimli_plato_erken_ifsa_korumasi_bozulmadi():
    """Tek cekim istisnasi, uc cekimli formatin korumasini delmemeli."""
    cfg = _cfg(shots=3, shot_plan=["SHOT 1, THREAT.", "SHOT 2, TAKEN.", "SHOT 3, REVEAL."])
    bolum = _episode()
    tek = bolum["shots"][0]
    bolum["shots"] = [
        dict(tek, n=1, prompt="A colossal tawny lion made of fibreglass roars at Ihsan. "
                              "Ambient sound only: studio air handling."),
        dict(tek, n=2, prompt="The lion takes Ihsan into its mouth. "
                              "Ambient sound only: studio air handling."),
        dict(tek, n=3, prompt="Crew open the practical jaws and Ihsan steps out. "
                              "Ambient sound only: studio air handling."),
    ]
    hatalar = _dogrula([bolum], cfg)
    assert any("yapım dili ifşayı erken" in h for h in hatalar), (
        f"uc cekimde cekim 1'deki 'fibreglass' yakalanmadi: {hatalar}"
    )


def test_uc_cekimli_plato_sis_dilini_hala_kabul_eder():
    """Uc cekimli metin BIT-BIT korunmali: eski kural sis'i hos karsiliyordu.

    Bu test, tek cekim temizligini yanlislikla uc cekime uygulayan bir
    degisikligi yakalar (altin kopyalarin yedegi).
    """
    cfg = _cfg(shots=3, shot_plan=["SHOT 1.", "SHOT 2.", "SHOT 3."])
    _contents, system = replenish._build_prompt(
        _meta(cfg), _bible(), cfg, start=8, batch=1, history=[]
    )
    assert "haze" in system.lower(), "uc cekimli Plato metni degismis (regresyon)"
