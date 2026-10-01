"""DARK FACT (shadowedhistory, 1 Ekim 2026) kurulum kilitleri.

Doktrin: shadowedhistory/DARK-FACT.md. Iki surum gun asiri cikar; tek degisken
kesme sayisidir. Bu testler surumleri birbirinden ayiran ve ayni tutan seyleri
kilitler, ayrica canli kuyrugun kredi harcamadan uretime girebilecegini dogrular.
"""
import json
import subprocess
from pathlib import Path

import pytest
import yaml

from series import omni_api
from series.bible import Bible
from series.replenish import (
    validate_plan_against_config,
    validate_replenish_config,
    validate_title_card,
)

REPO = Path(__file__).resolve().parents[1]
SERILER = ("dark-fact-a", "dark-fact-b")


@pytest.fixture(autouse=True)
def _eski_series_data_kokunu_izole_et():
    """Yalniz izlenen kurulum dosyalarini okur, hicbir yere yazmaz."""


def _meta(slug):
    return json.loads((REPO / "shadowedhistory" / slug / "series.json").read_text(encoding="utf-8"))


def _bible(slug):
    return Bible(json.loads((REPO / "shadowedhistory" / slug / "bible.json").read_text(encoding="utf-8")))


def _planlar(slug):
    return sorted((REPO / "shadowedhistory" / slug / "plans").glob("part*.json"))


@pytest.mark.parametrize("slug", SERILER)
def test_ikmal_ayari_ve_bekleyen_planlar_gecerli(slug):
    meta, bible = _meta(slug), _bible(slug)
    cfg = meta["auto_replenish"]
    assert validate_replenish_config(cfg, engine=bible.engine) == []
    planlar = _planlar(slug)
    assert planlar, "kuyruk bos"
    for yol in planlar:
        plan = json.loads(yol.read_text(encoding="utf-8"))
        assert validate_plan_against_config(plan, cfg, engine=bible.engine) == [], yol.name
        assert validate_title_card(bible, plan, required=True) == [], yol.name
        assert len(plan["hashtags"].split()) <= 5, yol.name   # IG etiket tavani


@pytest.mark.parametrize("slug", SERILER)
def test_yazi_video_boyunca_ekranda_kalir(slug):
    bible = _bible(slug)
    tc = bible.title_card
    band = bible.data["series"]["duration_band"]
    # title_card_overlay suresi dolunca yaziyi eritir; video bandinin ustunde
    # bir sure yazinin hic solmamasi demektir (doktrin kural 1).
    assert float(tc["duration"]) > max(band) + 1
    assert tc["preserve_case"] is True and tc["year_required"] is False


def test_iki_surum_yalniz_kesme_sayisinda_ayrisir():
    a, b = _bible("dark-fact-a").data, _bible("dark-fact-b").data
    assert a["art_style"] == b["art_style"]
    assert a["series"]["music_fixed"] == b["series"]["music_fixed"]
    assert a["series"]["title_card"] == b["series"]["title_card"]
    ma, mb = _meta("dark-fact-a")["auto_replenish"], _meta("dark-fact-b")["auto_replenish"]
    assert (ma["shots"], ma["shot_seconds"], a["series"]["micro_trim"]) == (1, "10", 0)
    assert (mb["shots"], mb["shot_seconds"], b["series"]["micro_trim"]) == (4, "4", 0.75)
    for meta, bible in ((ma, a), (mb, b)):
        assert bible["series"]["qc"]["min_shots"] == meta["shots"]


def test_konu_havuzlari_ayrik_ve_kisi_aniti_yok():
    ida = {t["id"] for t in _meta("dark-fact-a")["auto_replenish"]["topic_pool"]}
    idb = {t["id"] for t in _meta("dark-fact-b")["auto_replenish"]["topic_pool"]}
    assert ida and idb and not (ida & idb), "ayni bilgi iki kez yayinlanir"
    for slug in SERILER:
        metinler = [t["topic"] for t in _meta(slug)["auto_replenish"]["topic_pool"]]
        metinler += [p.read_text(encoding="utf-8") for p in _planlar(slug)]
        for metin in metinler:
            dusuk = metin.lower()
            for ad in omni_api.PUBLIC_FIGURE_SUBJECTS:
                assert ad not in dusuk, (slug, ad)


def test_iki_seri_ayni_kanala_ve_ayni_doktrine_baglidir():
    for slug in SERILER:
        meta = _meta(slug)
        assert meta["upload_profile"] == "shad0wedhistory"   # gunde-1 kilidi ikisini birlikte sayar
        assert meta["doctrine"] == "shadowedhistory/DARK-FACT.md"
        assert (REPO / meta["doctrine"]).is_file()
    assert all(_meta(slug)["status"] == "active" for slug in SERILER)
    still = json.loads((REPO / "shadowedhistory" / "still-home" / "series.json").read_text(encoding="utf-8"))
    assert still["status"] == "paused"


def _secim_betigi():
    wf = yaml.safe_load((REPO / ".github" / "workflows" / "dark-fact.yml").read_text(encoding="utf-8"))
    adim = next(s for s in wf["jobs"]["produce-and-publish"]["steps"] if s["name"].startswith("Seriyi sec"))
    return adim["run"]


@pytest.mark.parametrize("gun,beklenen", [("001", "dark-fact-a"), ("274", "dark-fact-b"),
                                          ("275", "dark-fact-a"), ("008", "dark-fact-b"),
                                          ("009", "dark-fact-a")])
def test_gun_paritesi_seri_secer(tmp_path, gun, beklenen):
    """Yilin gunu sifirla baslar ('008'); 10# olmadan bash onu sekizli sanip patlar."""
    betik = _secim_betigi().replace('${{ github.event.inputs.seri }}', "")
    betik = betik.replace("$(date -u +%j)", gun)
    env_dosyasi = tmp_path / "env"
    try:
        sonuc = subprocess.run(["bash", "-c", betik], capture_output=True, text=True,
                               env={"GITHUB_ENV": str(env_dosyasi), "PATH": "/usr/bin:/bin"})
    except FileNotFoundError:
        pytest.skip("bash yok")
    assert sonuc.returncode == 0, sonuc.stderr
    assert env_dosyasi.read_text().strip() == f"SERI={beklenen}"


def test_elle_secim_gecersiz_seriyi_reddeder(tmp_path):
    betik = _secim_betigi().replace('${{ github.event.inputs.seri }}', "still-home")
    try:
        sonuc = subprocess.run(["bash", "-c", betik], capture_output=True, text=True,
                               env={"GITHUB_ENV": str(tmp_path / "env"), "PATH": "/usr/bin:/bin"})
    except FileNotFoundError:
        pytest.skip("bash yok")
    assert sonuc.returncode != 0
