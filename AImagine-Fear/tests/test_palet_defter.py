"""Rock 4: palet damgasi ve defter semantigi.

Merkezdeki iddia: bir defter satirinin VARLIGI yayin kaniti degildir. Kanit,
YouTube yanitindan cikarilabilen bir yayin kimligidir.
"""
from __future__ import annotations

import json
import shutil
import sys
import uuid
from pathlib import Path

import pytest

PROJE_KOKU = Path(__file__).resolve().parent.parent
if str(PROJE_KOKU) not in sys.path:
    sys.path.insert(0, str(PROJE_KOKU))

import build  # noqa: E402
import defter as defter_modulu  # noqa: E402
from tools import gunluk  # noqa: E402


# ----------------------------------------------------------------------
# PALET alani: veri, dogrulama ve uretici birlikte gocmus olmali
# ----------------------------------------------------------------------
def test_dokuz_rotanin_palet_eslemesi_birebir() -> None:
    """Sadece "hepsi geciyor" demek yetmez; hangi rotanin hangi palette
    oldugu A/B'nin TEK olcum dayanagi."""
    beklenen = {
        "dubai-burj-altin": "sicak",
        "toronto-cn-red-dusk": "sicak",
        "newyork-empire-magenta-kar": "neon",
        "paris-eyfel-beyaz-cise": "neon",
        "sanghay-inci-yesil-sis": "neon",
        "tokyo-skytree-mor-yagmur": "neon",
        "vegas-strat-blue-rain": "neon",
        "vegas-strat-blue-rain-15": "neon",
        "vegas-strat-blue-rain-25": "neon",
        "istanbul-camlica-amber-sicak": "sicak",
    }
    gercek = {
        yol.stem: build.load_route(yol, PROJE_KOKU).fields["PALET"]
        for yol in sorted((PROJE_KOKU / "routes").glob("*.md"))
        if not yol.name.startswith("_")
    }
    assert gercek == beklenen


def test_palet_zorunlu_alan() -> None:
    assert "PALET" in build.ROUTE_FIELDS


@pytest.mark.parametrize("deger", ["", "mor", "warm", "Sicak", "sicak neon"])
def test_gecersiz_palet_build_check_te_kalir(deger: str, tmp_path: Path) -> None:
    kok = tmp_path / "proje"
    (kok / "routes").mkdir(parents=True)
    shutil.copytree(PROJE_KOKU / "canon", kok / "canon")
    ham = (PROJE_KOKU / "routes" / "dubai-burj-altin.md").read_text(encoding="utf-8")
    bozuk = "\n".join(
        ("PALET: " + deger) if s.startswith("PALET:") else s
        for s in ham.splitlines()
    )
    (kok / "routes" / "dubai-burj-altin.md").write_text(bozuk + "\n", encoding="utf-8")
    with pytest.raises(build.BuildError):
        build.build_project(kok, check=True)


def test_sablon_ve_uretici_de_gocmus() -> None:
    """Goc eksik kalirsa yeni uretilen rotalar dogdugu anda gecersiz olur."""
    sablon = (PROJE_KOKU / "routes" / "_TEMPLATE.md").read_text(encoding="utf-8")
    assert "PALET:" in sablon
    uretici = (PROJE_KOKU / "tools" / "sehir_ekle.py").read_text(encoding="utf-8")
    assert "PALET: {palet}" in uretici


# ----------------------------------------------------------------------
# yayin_kimligi: kimliksiz basari yayin sayilmaz
# ----------------------------------------------------------------------
def test_gercek_yanit_seklinden_kimlik_cikarilir() -> None:
    """yayin.jsonl'deki GERCEK ic ice yapiyla."""
    gercek = {
        "success": True,
        "results": {"youtube": {"success": True, "post_id": "qFYCRHr7604"}},
    }
    assert defter_modulu.yayin_kimligi(gercek) == "qFYCRHr7604"


@pytest.mark.parametrize("yanit", [
    None,
    {},
    {"success": True},                                   # kimliksiz 200
    {"success": True, "results": {"youtube": {"success": True}}},   # ic ice kimliksiz
    {"success": False, "results": {"youtube": {"post_id": "x"}}},   # basarisiz
    {"hata": "timeout"},
    {"success": True, "results": {"youtube": {"post_id": "   "}}},  # bos kimlik
])
def test_kimliksiz_yanit_yayin_sayilmaz(yanit) -> None:
    assert defter_modulu.yayin_kimligi(yanit) is None


# ----------------------------------------------------------------------
# kullanildi_mi: yeni alan + ESKI satirlar icin geriye uyum
# ----------------------------------------------------------------------
def test_yeni_satir_kullanildi_alanini_kullanir() -> None:
    assert defter_modulu.kullanildi_mi({"kullanildi": True}) is True
    assert defter_modulu.kullanildi_mi({"kullanildi": False}) is False


def test_eski_satir_youtube_sonucundan_cikarilir() -> None:
    """Geriye uyum olmasaydi butun gecmis 'basarisiz' sayilir, donusum
    sifirlanir ve eski basliklar yeniden secilirdi."""
    # GERCEK sekil: kayit["results"]["youtube"] = Upload-Post yanitinin tamami,
    # ve o yanitin kendi icinde results.youtube.post_id var.
    eski = {
        "slug": "dubai-burj-altin",
        "results": {
            "youtube": {
                "success": True,
                "results": {"youtube": {"success": True, "post_id": "abc123"}},
            }
        },
    }
    assert "kullanildi" not in eski
    assert defter_modulu.kullanildi_mi(eski) is True


def test_gercek_defterdeki_gecmis_kayboluyor_mu() -> None:
    """Depodaki gercek yayin.jsonl ile: sekiz kaydin hepsi dogrulanmis sayilmali."""
    ham = (PROJE_KOKU / "yayin.jsonl").read_text(encoding="utf-8")
    kayitlar = [json.loads(s) for s in ham.splitlines() if s.strip()]
    assert kayitlar, "yayin.jsonl bos"
    basarili = defter_modulu.basarili_kayitlar(kayitlar)
    assert len(basarili) == len(kayitlar), (
        "geriye uyum kirik: %d kaydin %d'i dogrulanmis sayildi"
        % (len(kayitlar), len(basarili))
    )


def test_basarisiz_satir_ne_donusumu_ne_gunu_kilitler() -> None:
    gecmis = [
        {"slug": "dubai-burj-altin", "ts": "2026-09-10 06:20 PDT",
         "kullanildi": False, "results": {"youtube": {"hata": "timeout"}}},
    ]
    # ayni-gun kapisi
    assert defter_modulu.bugunku_basarili(gecmis, "2026-09-10") == []
    # donusum: basarisiz slug "kullanilmis" sayilmamali
    assert gunluk.sirdaki(gecmis) == gunluk.SIRA[0]


def test_basarili_satir_donusumu_ilerletir() -> None:
    gecmis = [
        {"slug": gunluk.SIRA[0], "ts": "2026-09-10 06:20 PDT",
         "kullanildi": True, "youtube_id": "abc"},
    ]
    assert gunluk.sirdaki(gecmis) == gunluk.SIRA[1]
    assert len(defter_modulu.bugunku_basarili(gecmis, "2026-09-10")) == 1


# ----------------------------------------------------------------------
# Defter alanlarinin KAYNAKLARI ayri olmali
# ----------------------------------------------------------------------
def test_defter_alanlari_dogru_kaynaktan_gelir() -> None:
    kayit = {
        "slug": "dubai-burj-altin",
        "palet": "sicak",
        "beklenen_sure": 15,
        "istenen_profil": "1080p",
        "olculen": {"genislik": 1080, "yukseklik": 1920, "fps": 23.976, "sure": 15.04},
        "ses": {"lufs": -14.1, "true_peak": -1.3},
    }
    alanlar = gunluk.defter_alanlari("dubai-burj-altin", kayit)
    # uretim kaydindan
    assert alanlar["palet"] == "sicak"
    assert alanlar["rota_suresi"] == 15
    # probe olcumunden (SABIT DEGIL: gercek olculen deger)
    assert alanlar["fps"] == 23.976
    assert alanlar["sure"] == 15.04
    # sidecar'dan
    assert alanlar["lufs"] == -14.1
    assert alanlar["true_peak"] == -1.3
    # kullanildi BURADA yok: onu yayinla.py YouTube yanitindan turetir
    assert "kullanildi" not in alanlar


def test_uretim_kaydi_semasi_2_ve_palet_tasiyor() -> None:
    """Sema surumu bumplandi mi ve palet kayda giriyor mu."""
    kaynak = (PROJE_KOKU / "tools" / "gunluk.py").read_text(encoding="utf-8")
    assert '"sema_surumu": 2' in kaynak
    assert '"palet": palet' in kaynak


# ----------------------------------------------------------------------
# Palet A/B artik GERCEKTEN kosabilir: iki sicak rota aktif sirada.
# Bu test daha once BOS gecerdi (tek sicak rota vardi) ve o yuzden
# yazilmamisti. Artik gercek bir iddia.
# ----------------------------------------------------------------------
def test_sicak_rotalar_siraya_esit_dagilmis() -> None:
    paletler = [gunluk.rota_paleti(slug) for slug in gunluk.SIRA]
    sicak_indeksler = [i for i, p in enumerate(paletler) if p == "sicak"]
    assert len(sicak_indeksler) >= 2, (
        "A/B icin en az iki sicak rota gerekiyor, su an: %d" % len(sicak_indeksler)
    )
    n = len(gunluk.SIRA)
    # Dairesel araliklar: son sicaktan bassa donen mesafe de sayilir
    araliklar = [
        (sicak_indeksler[(k + 1) % len(sicak_indeksler)] - sicak_indeksler[k]) % n
        for k in range(len(sicak_indeksler))
    ]
    assert max(araliklar) - min(araliklar) <= 1, (
        "sicak rotalar esit dagilmamis, dairesel araliklar: %s" % araliklar
    )


def test_sira_hem_sicak_hem_neon_iceriyor() -> None:
    paletler = {gunluk.rota_paleti(slug) for slug in gunluk.SIRA}
    assert paletler == {"sicak", "neon"}, (
        "A/B icin sirada her iki palet de olmali, su an: %s" % paletler
    )
