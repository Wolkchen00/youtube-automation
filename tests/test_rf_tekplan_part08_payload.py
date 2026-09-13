"""RF-PLAN-TEKPLAN10 Rock 4(f): GERCEK part08'in urettigi Omni yukunu dogrular.

Neden CLI cikis kodu kanit degil: series/produce.py:2175-2177 None donse de
series/cli.py:101-103 basari donduruyor. Bu test ucretli fonksiyona hic
dokunmadan, plandan cikan SOMUT parametreleri dogrular.

Neden gercek dosyanin KOPYASI uzerinde calisir: capa hazirligi plan dosyasina
geri yaziyor (produce.py:1643-1646 -> 1373-1375 atomic_write_json). Bu test
capa katmanini cagirmiyor, ama izlenen dosyalarin baytlarini yine de
degismezlik icin dogruluyor.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest

from series.bible import Bible, doctrine_sha256
from series.shots import load_plan, resolve_shot, validate_plan


SERI = Path(__file__).resolve().parents[1] / "sentinal_ihsan" / "wild-encounter"
PART08 = SERI / "plans" / "part08.json"
BIBLE = SERI / "bible.json"
IHSAN_CID = "92369a8131e7497abf00c3b5ba1c92c9"


def _ozet(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


@pytest.fixture
def calisma(tmp_path):
    """Gercek part08'i gecici bir yola kopyalar ve dosya baytlarini pinler."""
    once = {"part08": _ozet(PART08), "bible": _ozet(BIBLE)}
    kopya = tmp_path / "part08.json"
    shutil.copy2(PART08, kopya)
    yield kopya
    # Izlenen dosyalar bu testten degismeden cikmali.
    assert _ozet(PART08) == once["part08"], "part08.json test sirasinda degisti"
    assert _ozet(BIBLE) == once["bible"], "bible.json test sirasinda degisti"


def _bible() -> Bible:
    return Bible(json.loads(BIBLE.read_text(encoding="utf-8")))


def test_part08_tek_cekim_ve_on_saniye(calisma):
    plan = load_plan(calisma)
    assert len(plan["shots"]) == 1, "tek plan formati: tam bir cekim"
    assert str(plan["shots"][0]["duration"]) == "10"


def test_part08_plan_dogrulamasindan_gecer(calisma):
    plan = load_plan(calisma)
    validate_plan(plan, _bible())  # hata varsa yukselir


def test_part08_doktrin_damgasi_guncel(calisma):
    plan = load_plan(calisma)
    assert plan["doctrine_sha256"] == doctrine_sha256(SERI / "DOKTRIN.md"), (
        "bayat damga: produce.py:1560-1569 uretimi durdurur"
    )


def test_part08_object_card_tam(calisma):
    """produce.py:1278-1281 object_card'siz Plato planini reddeder."""
    card = load_plan(calisma).get("object_card")
    assert isinstance(card, dict)
    for alan in ("name", "descriptor", "environment", "framing", "anomaly_descriptor"):
        assert str(card.get(alan) or "").strip(), f"object_card.{alan} bos"
    # Yaratik TANIDIK GERCEK bir hayvan olmali, kukla dili kimlikte gecmemeli.
    kimlik = f"{card['name']} {card['descriptor']}".lower()
    for kukla in ("prop", "animatronic", "puppet", "fibreglass", "silicone", "armature"):
        assert kukla not in kimlik, f"kimlik alaninda yapim dili: {kukla}"


def test_part08_omni_yuku_dogru(calisma):
    """Ucretli cagriya gidecek SOMUT parametreler."""
    plan = load_plan(calisma)
    cozum = resolve_shot(_bible(), plan["shots"][0], plan=plan)
    kw = cozum["kwargs"]

    assert kw["duration"] == "10", f"sure {kw['duration']!r}, motora 10 gitmeli"
    assert kw["aspect_ratio"] == "9:16"
    assert IHSAN_CID in (kw["character_ids"] or []), "Ihsan'in yuzu yuke baglanmamis"

    prompt = kw["prompt"]
    dusuk = prompt.lower()
    # art_style her cekim promptunun basina eklenir (series/shots.py).
    assert "one continuous uncut shot" in dusuk
    assert "blue screen" in dusuk
    assert "pushes in slowly" in dusuk
    assert "the air is clear" in dusuk
    # Vuruslar ayni cekimde, sirasiyla.
    for vurus in ("out of sight", "jaws open", "climbs out"):
        assert vurus in dusuk, f"vurus eksik: {vurus}"
    # Anlatim ve muzik yok; ses setin kendi sesi.
    assert "ambient sound only" in dusuk
    for yasak in ("narration", "voice-over", "voiceover", "speaking", "musical score"):
        assert yasak not in dusuk, f"prompt anlatim/muzik vaat ediyor: {yasak}"
    # Olculmus bulgu: sis kaybedenlerde var, kazananlarda yok.
    for yasak in ("haze", "fog", "green screen"):
        assert yasak not in dusuk, f"prompt yasak set dili tasiyor: {yasak}"


def test_part08_omni_yuku_yalniz_beklenen_uyariyi_verir(calisma):
    """Tek beklenen uyari: ortam referans gorseli henuz yok.

    Bu KASITLI: 13 Eylul'de set tarifi mavi perdeye ve sissiz minimal sete
    cevrildi, bu yuzden environments[].ref_image_url alanlari bosaltildi
    (eski sisli/yesil gorsel yeni prompta sizmasin). Uretim capa asamasinda
    (bible.series.episode_anchors) yeni tarife gore yeniden uretir.
    Baska bir uyari cikarsa yuk bozulmus demektir.
    """
    plan = load_plan(calisma)
    cozum = resolve_shot(_bible(), plan["shots"][0], plan=plan)
    beklenen = "Ortam 'desert_ruins_set' referans görseli yok"
    assert cozum["warnings"] == [beklenen], cozum["warnings"]
    assert cozum["units"] <= 7, "7-birim referans kotasi asildi"
