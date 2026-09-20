"""wild-encounter: vurus teslim edilmeden klip yayina cikamaz.

Neden bu dosya var, olcumle:

18 Eylul 2026'da yayindaki uc bolum indirilip kare kare incelendi.

  ep09 `wuuu02K2hPc` kutup ayisi, 36.070 izlenme (kanal rekoru)
      Vurus TAM teslim edildi: adam yaklasir, ayinin agzi uzerine kapanir,
      adam gozden kaybolur, ekip kosup ceneyi iki eliyle acar, ayni adam
      disari cikip kameraya dogru yurur.

  ep11 `4cdvxPh_mE8` dev kalamar
      Vurusun HICBIR parcasi teslim edilmedi. Adam yaratiga dogru yurur,
      YANINDAN gecer, kadrajdan kaybolur. Temas yok. Ekip bos yaratigi iter.
      Kimse disari cikmaz. Yaratik bastan sona neredeyse hareketsiz bir prop.

Ikisi de QC'den `pass, artifact_score 0/10` ile gecti. Sebebi basit ve
yapisaldi: bu seride `violation_observation` HIC yazilmiyordu (replenish o alani
yalniz `fixed_object_prompt` dalinda isterdi, wild-encounter ise `plato +
single_shot` dalinda), dolayisiyla `_rb_requested` bostu ve `qc.enforce` null
idi. Yani vurusu denetleyen bir KARAR ALANI yoktu. `qc.notes` doktrini yaziyordu
ama notlar karara girmez.

Kapi vurusun VARLIGINI denetler, uslubunu degil. Uslup inceligi (adam ALINIYOR
mu, yoksa kendi mi tirmaniyor) bilerek disarida birakildi: belirsiz kriter
yanlis retle Kie kredisi yakar.
"""

from __future__ import annotations

import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from series import critic  # noqa: E402
from series.replenish import PLATO_SINGLE_SHOT_OBSERVATION  # noqa: E402
from series.shots import NEGATIVE_VIDEO_LANGUAGE, TEMPORAL_OVERREACH  # noqa: E402


WE = pathlib.Path(__file__).resolve().parents[1] / "sentinal_ihsan" / "wild-encounter"


def rb(value, visible=True, confidence=0.9):
    return {"value": value, "visible": visible, "confidence": confidence}


def decide(review_extra, *, enforce=True):
    review = {"artifact_score": 0, **review_extra}
    qc = {
        "artifact_threshold": 7,
        "_rb_requested": ("violation_reads",),
    }
    if enforce:
        qc["enforce"] = {"violation_reads": True}
    return critic._decide(review, qc, False, 1)


# ------------------------------------------------- the gate, both directions

def test_ep11_shaped_clip_is_rejected():
    """Vurus teslim edilmemis: klip REDDEDILIR, yayina cikamaz."""
    verdict, reasons = decide({"violation_reads": rb(False)})
    assert verdict == "fail", "vurusu teslim etmeyen klip yayina cikamaz"
    assert reasons, "ret sebepsiz olamaz"


def test_ep09_shaped_clip_passes():
    """Vurus teslim edilmis: klip GECER. Kapi calisan uretimi engellememeli."""
    verdict, reasons = decide({"violation_reads": rb(True)})
    assert verdict == "pass", f"teslim edilmis vurus reddedildi: {reasons}"
    assert reasons == []


# ---------------------------------------------- kapi yalnizca ACIK oldugunda

def test_without_the_enforce_flag_the_field_is_measured_not_gated():
    """P7: once olcum, sonra kapi. Terfi etmemis alan REDDETMEZ.

    Bu, kapiyi acmayan oteki serilerin davranisinin degismedigini kanitlar.
    """
    verdict, _ = decide({"violation_reads": rb(False)}, enforce=False)
    assert verdict == "pass"


# ----------------------------------------------- belirsizlik sessizce gecmez

def test_low_confidence_holds_instead_of_passing():
    """Model emin degilse klip SESSIZCE gecmez, hold'a duser."""
    verdict, reasons = decide({"violation_reads": rb(False, confidence=0.3)})
    assert verdict == "hold"
    assert any("güven" in r for r in reasons)


def test_unreadable_region_holds_instead_of_passing():
    """Bolge okunamiyorsa karar verilmemistir; pass sayilamaz."""
    verdict, _ = decide({"violation_reads": rb(None, visible=True, confidence=0.9)})
    assert verdict == "hold"


def test_a_missing_field_holds_instead_of_passing():
    """Alan hic gelmezse fail-closed: eksik olcum basari degildir."""
    verdict, reasons = decide({})
    assert verdict == "hold"
    assert reasons


def test_off_schema_field_holds():
    verdict, _ = decide({"violation_reads": {"value": False}})
    assert verdict == "hold"


# ------------------------------------------------------------ canli kosullar

def test_the_series_actually_has_the_gate_open():
    """Kapi kodda var olsa da bible'da acilmadikca hicbir sey degismez."""
    bible = json.loads((WE / "bible.json").read_text(encoding="utf-8"))
    assert bible["series"]["qc"].get("enforce", {}).get("violation_reads") is True


def test_every_queued_plan_carries_an_observation_naming_its_creature():
    """Gozlem olmadan alan istenmez, alan istenmezse kapi hic calismaz.

    Yalniz HENUZ URETILMEMIS planlara bakilir. Yayinlanmis eski bolumler
    (ornegin part02, farkli bir konsept doneminden) baska bicimde yazilmis
    gozlemler tasir; onlari geriye donuk duzeltmek kapiyi guclendirmez.
    """
    series = json.loads((WE / "series.json").read_text(encoding="utf-8"))
    next_part = int(series["next_part"])
    checked = 0
    for path in sorted(WE.glob("plans/part*.json")):
        if path.suffix != ".json":
            continue
        digits = "".join(ch for ch in path.stem if ch.isdigit())
        if not digits or int(digits) < next_part:
            continue
        plan = json.loads(path.read_text(encoding="utf-8"))
        name = str((plan.get("object_card") or {}).get("name") or "").strip()
        assert name, f"{path.name}: object_card.name yok"
        for shot in plan.get("shots") or []:
            observation = shot.get("violation_observation")
            assert observation, (
                f"{path.name}: gozlem YOK, bu plan uretilirse vurus denetlenmez"
            )
            checked += 1
            assert name in observation, (
                f"{path.name}: gozlem yaratigi adlandirmiyor, kapi neyi arayacagini bilemez"
            )
    if not checked:
        # Son bolum yayinlandiktan sonra, bir sonraki ikmale kadar kuyruk
        # mesru olarak BOSTUR. Bunu kirmiziya cevirmek gercek arizalari
        # golgeleyen gunluk bir yanlis alarm uretiyordu.
        pytest.skip("kuyruk su an bos (son bolum yayinlandi, ikmal bekleniyor)")


@pytest.mark.parametrize("creature", [
    "giant polar bear", "giant komodo dragon", "giant rhinoceros beetle",
])
def test_the_generated_observation_survives_every_validator(creature):
    """Gozlem uretiliyor ama dogrulayicilar reddediyorsa plan hic yazilamaz."""
    observation = PLATO_SINGLE_SHOT_OBSERVATION.format(creature=creature)
    assert len(observation.split()) >= 4
    assert observation == observation.strip()
    assert not NEGATIVE_VIDEO_LANGUAGE.search(observation), (
        "olumsuz dil: difuzyon olumsuzu cizer ve dogrulayici reddeder"
    )
    assert not TEMPORAL_OVERREACH.search(observation)
    assert creature in observation


def test_the_observation_covers_both_halves_of_the_beat():
    """Yutulma VE cikis. Birini atlarsa kapi yarim vurusu gecirir.

    ep11 ikisini de atladi; ep10 baykus cikisi verdi ama alinmayi vermedi.
    Tek yarim yeterli sayilirsa kapi asil arizayi yakalamaz.
    """
    observation = PLATO_SINGLE_SHOT_OBSERVATION.format(creature="giant owl").lower()
    assert "closes over" in observation and "hidden inside" in observation, (
        "yutulma yarisi eksik"
    )
    assert "climbs out" in observation, "cikis yarisi eksik"
