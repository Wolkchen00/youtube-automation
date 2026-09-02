"""Next Stop zincir yedegi muhafizi.

2026-09-02'de bolum 5, cekim 1'in son karesi QC'den "anatomi bozuk" diye donunce
BUTUN bolum oldu: bir sonraki cekim icin kanonik gorsel yoktu, motor fail-closed
oldu (qc_log.jsonl, event=chain_frame_failure, canonical_source=null).

Kok neden: bible'da environments/props/characters bostu ve plan cekimleri
"environment" alani tasimiyordu, bu yuzden resolve_shot image_urls'i HER ZAMAN
bos donuyor, _canonical_scene_source HER ZAMAN None oluyordu. Yani bolumdeki 5
zincir sicramasinin her biri tek basina bolumu oldurebilen bir tekil ariza
noktasiydi.

Bu testler o onarimin sessizce geri alinmasini engeller.
"""
import json
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parents[1]
SERI_DIZIN = KOK / "aimagine" / "next-stop"
ENV_ID = "carriage"


def _json(yol: Path) -> dict:
    return json.loads(yol.read_text(encoding="utf-8"))


def _aktif_planlar() -> list[tuple[str, dict]]:
    """Henuz yayinlanmamis (next_part ve sonrasi) plan dosyalari."""
    seri = _json(SERI_DIZIN / "series.json")
    ilk = int(seri["next_part"])
    cikti = []
    for yol in sorted((SERI_DIZIN / "plans").glob("part*.json")):
        plan = _json(yol)
        if int(plan.get("episode", {}).get("number") or 0) >= ilk:
            cikti.append((yol.name, plan))
    return cikti


def test_bible_kanonik_vagon_referansi_tasiyor():
    """(a) Yedek gorselin kendisi duruyor mu."""
    bible = _json(SERI_DIZIN / "bible.json")
    ortamlar = {o.get("id"): o for o in (bible.get("environments") or [])}
    assert ENV_ID in ortamlar, (
        f"bible.environments icinde '{ENV_ID}' yok. Yedek gorsel kalkarsa tek bir "
        "kotu zincir karesi butun bolumu yeniden oldurur."
    )
    url = ortamlar[ENV_ID].get("ref_image_url")
    assert url and str(url).startswith("http"), (
        f"'{ENV_ID}' ortaminin ref_image_url'i bos ya da gecersiz: {url!r}"
    )


def test_aktif_planlarin_her_cekimi_ortam_alani_tasiyor():
    """(b) Alan gercekten planlarda mi."""
    planlar = _aktif_planlar()
    assert planlar, "denetlenecek aktif plan bulunamadi"
    for ad, plan in planlar:
        cekimler = plan.get("shots") or []
        assert cekimler, f"{ad}: cekim yok"
        for cekim in cekimler:
            assert cekim.get("environment") == ENV_ID, (
                f"{ad} cekim {cekim.get('n')}: environment '{ENV_ID}' degil "
                f"({cekim.get('environment')!r}). Bu cekim zincir yedeksiz kalir."
            )


def test_gercek_kod_yolu_kanonik_kaynak_donduruyor():
    """(c) Asil sart: alan varligi degil, motorun kendi kararı.

    Alan var ama bible'da o id yoksa resolve_shot yine bos doner; bu yuzden
    alana bakip gecmek yeterli degil, gercek fonksiyon cagrilir.
    """
    from series.bible import Bible
    from series.produce import _canonical_scene_source

    bible = Bible.load("next-stop")
    assert bible is not None, "next-stop bible yuklenemedi"
    for ad, plan in _aktif_planlar():
        for cekim in plan.get("shots") or []:
            kaynak = _canonical_scene_source(bible, cekim, plan, "omni")
            assert kaynak is not None, (
                f"{ad} cekim {cekim.get('n')}: kanonik kaynak None. Zincir karesi "
                "reddedilirse motor fail-closed olur ve bolum olur."
            )


def test_replenish_konfigi_gelecek_bolumlere_de_alani_yazdiriyor():
    """(d) part10+ boslugu: yeni uretilen planlar da alani tasimali.

    replenish.py:550 shot_refs bayragina bakiyor; kapaliysa uretilen cekimlerde
    "environment" alani hic olmaz ve ariza part10'da geri doner.
    """
    seri = _json(SERI_DIZIN / "series.json")
    ar = seri.get("auto_replenish") or {}
    assert ar.get("shot_refs") is True, (
        "auto_replenish.shot_refs True degil. Bu bayrak olmadan replenish yeni "
        "planlara 'environment' alanini hic yazmaz ve part10'dan sonra tekil "
        "ariza noktasi geri gelir."
    )
    assert "\"environment\": \"carriage\"" in ar.get("brief", ""), (
        "brief icinde ortam alanini ZORUNLU kilan kural yok. replenish sablonu "
        "alani 'optional' diye tanitiyor, yani model atlayabilir."
    )


def test_next_stop_hala_aktif_ve_kanal_tek_seride_bagli():
    """Onarim, seridin kendisi kapaliysa anlamsiz."""
    seri = _json(SERI_DIZIN / "series.json")
    assert seri["status"] == "active", (
        f"next-stop 'active' olmali, kanalin tek uretim seridi o. "
        f"Bulunan: {seri['status']!r}"
    )


@pytest.mark.parametrize("alan,beklenen", [("chain_scope", "episode"), ("chain_frames", True)])
def test_zincir_ayarlari_degismedi(alan, beklenen):
    """Yedek eklemek zincirin KENDISINI kapatmak degildir.

    Biri 'sorunu' zinciri kapatarak cozmeye kalkarsa serinin imza formati
    (tek kesintisiz yolculuk) bozulur; bu test onu yakalar.
    """
    bible = _json(SERI_DIZIN / "bible.json")
    assert bible["series"][alan] == beklenen, (
        f"bible.series.{alan} {beklenen!r} olmali, bulunan "
        f"{bible['series'][alan]!r}. Zincir kapatilarak 'onarim' yapilmis olabilir."
    )
