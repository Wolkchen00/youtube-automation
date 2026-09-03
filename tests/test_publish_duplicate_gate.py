"""Mukerrer-baslik yayin kapisi muhafizi.

2026-09-02'de AImagine kanalinda "Next Stop: The Deep" 3 kez, "Next Stop: Hell"
5 kez birikmisti. Sebep: hicbir yol yuklemeden once kanala bakmiyordu.
- Gunluk boru hatti series_runner:336'dan dogrudan upload_to_platform cagiriyor
  (publish_video'yu HIC kullanmiyor), yani kapiyi publish_video'ya koymak
  bosunaydi.
- Pilot kosulari (output/experiments) ve elle yayinlar da ayni yerden geciyor.
upload_to_platform olculen TEK tikanma noktasi; kapi orada.

Kapi bilerek FAIL-OPEN: kanal dogrulanamazsa yayin SURER. Gunluk kanali gecici
bir ag hatasi yuzunden karartmak, bir mukerrer videodan daha pahalidir.
"""
import json
from pathlib import Path

import pytest

from core import uploader
from core.utils import normalize_title

KOK = Path(__file__).resolve().parents[1]
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "rss_ornek.xml"


@pytest.fixture(autouse=True)
def _onbellek_temizle():
    """Her test kendi kanal onbellegiyle basiasin."""
    uploader._channel_titles_cache.clear()
    yield
    uploader._channel_titles_cache.clear()


# ─── normalize_title ──────────────────────────────────────────────────────────

def test_normalize_emoji_ve_noktalamayi_atiyor():
    assert (normalize_title("Next Stop: The Deep \U0001F686\U0001F30A")
            == normalize_title("next stop the deep"))


def test_normalize_farkli_duraklari_ayirt_ediyor():
    assert normalize_title("Next Stop: The Deep \U0001F686") != \
        normalize_title("Next Stop: Kepler-186f \U0001FA90")


def test_replenish_ayni_normalizasyonu_kullaniyor():
    """Ayrisirlarsa baslik replenish'ten gecip kapida takilir , sessiz ariza."""
    from series.replenish import _norm_title
    for ornek in ["Next Stop: The Deep \U0001F686\U0001F30A", "  MIXED Case: Test!! ",
                  "", "Next Stop: Kepler-186f \U0001FA90✨"]:
        assert _norm_title(ornek) == normalize_title(ornek), ornek


# ─── kanal akisi ayristirma (AG CAGRISI YOK) ──────────────────────────────────

class _SahteYanit:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code


def test_gercek_rss_ayristiriliyor(monkeypatch):
    """Mock'lanmis kume degil, GERCEK yakalanmis YouTube XML'i ayristirilir."""
    xml = FIXTURE.read_text(encoding="utf-8")
    monkeypatch.setattr(uploader, "_channel_id_for_user", lambda u: "UC_TEST")
    monkeypatch.setattr(uploader.requests, "get", lambda *a, **k: _SahteYanit(xml))
    basliklar = uploader.channel_recent_titles("Youtube")
    assert basliklar is not None
    assert normalize_title("Next Stop: Kepler-186f") in basliklar
    assert normalize_title("Next Stop: The Deep") in basliklar


def test_onbellek_tek_istek_atiyor(monkeypatch):
    """Bir bolumun 3 platform cagrisi 1 RSS istegine inmeli."""
    xml = FIXTURE.read_text(encoding="utf-8")
    sayac = {"n": 0}

    def _get(*a, **k):
        sayac["n"] += 1
        return _SahteYanit(xml)

    monkeypatch.setattr(uploader, "_channel_id_for_user", lambda u: "UC_TEST")
    monkeypatch.setattr(uploader.requests, "get", _get)
    uploader.channel_recent_titles("Youtube")
    uploader.channel_recent_titles("Youtube")
    uploader.channel_recent_titles("Youtube")
    assert sayac["n"] == 1, f"beklenen 1 istek, atilan {sayac['n']}"


@pytest.mark.parametrize("senaryo", ["http_hata", "bozuk_xml", "istisna", "kanal_yok"])
def test_dogrulanamayan_her_durum_none_donuyor(monkeypatch, senaryo):
    """Bilinmeyen her sey 'dogrulanamadi' kovasina duser."""
    monkeypatch.setattr(uploader, "_channel_id_for_user",
                        lambda u: None if senaryo == "kanal_yok" else "UC_TEST")
    if senaryo == "http_hata":
        monkeypatch.setattr(uploader.requests, "get",
                            lambda *a, **k: _SahteYanit("", status_code=503))
    elif senaryo == "bozuk_xml":
        monkeypatch.setattr(uploader.requests, "get",
                            lambda *a, **k: _SahteYanit("<html>not a feed"))
    elif senaryo == "istisna":
        def _patla(*a, **k):
            raise OSError("ag koptu")
        monkeypatch.setattr(uploader.requests, "get", _patla)
    assert uploader.channel_recent_titles("Youtube") is None


# ─── kapinin kendisi ──────────────────────────────────────────────────────────

@pytest.fixture
def _yukleme_izleyici(monkeypatch, tmp_path):
    """upload_to_platform'un gercek HTTP'ye gitmesini engelle, cagriyi say."""
    video = tmp_path / "ep.mp4"
    video.write_bytes(b"x")
    cagrilar = []

    def _post(*a, **k):
        cagrilar.append(k)
        return _SahteYanit(json.dumps({"success": True}))

    monkeypatch.setattr(uploader, "UPLOAD_POST_API_KEY", "test-key")
    monkeypatch.setattr(uploader, "_delivery_copy", lambda p: p)
    monkeypatch.setattr(uploader.requests, "post", _post)
    return video, cagrilar


def test_kanalda_varsa_youtube_yuklenmiyor(monkeypatch, _yukleme_izleyici):
    video, cagrilar = _yukleme_izleyici
    monkeypatch.setattr(uploader, "channel_recent_titles",
                        lambda u: {normalize_title("Next Stop: The Deep")})
    sonuc = uploader.upload_to_platform(
        video, "Next Stop: The Deep \U0001F686\U0001F30A", "d",
        user="Youtube", platform="youtube")
    assert sonuc is None
    assert cagrilar == [], "mukerrer basliga ragmen yukleme yapildi"


def test_kapi_instagram_a_dokunmuyor(monkeypatch, _yukleme_izleyici):
    video, cagrilar = _yukleme_izleyici
    monkeypatch.setattr(uploader, "channel_recent_titles",
                        lambda u: {normalize_title("Next Stop: The Deep")})
    uploader.upload_to_platform(
        video, "Next Stop: The Deep \U0001F686\U0001F30A", "d",
        user="Youtube", platform="instagram")
    assert len(cagrilar) == 1, "instagram kapiya takildi, takilmamaliydi"


def test_dogrulanamayinca_yayin_suruyor(monkeypatch, _yukleme_izleyici):
    """FAIL-OPEN: ag hatasi gunluk kanali karartmamali."""
    video, cagrilar = _yukleme_izleyici
    monkeypatch.setattr(uploader, "channel_recent_titles", lambda u: None)
    uploader.upload_to_platform(
        video, "Next Stop: The Deep \U0001F686", "d",
        user="Youtube", platform="youtube")
    assert len(cagrilar) == 1, "kanal dogrulanamayinca yayin durduruldu"


def test_bayrak_kapiyi_atliyor(monkeypatch, _yukleme_izleyici):
    video, cagrilar = _yukleme_izleyici
    monkeypatch.setattr(uploader, "channel_recent_titles",
                        lambda u: {normalize_title("Next Stop: The Deep")})
    uploader.upload_to_platform(
        video, "Next Stop: The Deep \U0001F686", "d",
        user="Youtube", platform="youtube", allow_duplicate_title=True)
    assert len(cagrilar) == 1, "allow_duplicate_title kapiyi atlamadi"


def test_yeni_baslik_engellenmiyor(monkeypatch, _yukleme_izleyici):
    video, cagrilar = _yukleme_izleyici
    monkeypatch.setattr(uploader, "channel_recent_titles",
                        lambda u: {normalize_title("Next Stop: The Deep")})
    uploader.upload_to_platform(
        video, "Next Stop: Bifrost \U0001F308", "d",
        user="Youtube", platform="youtube")
    assert len(cagrilar) == 1, "yeni baslik yanlislikla engellendi"


# ─── gunluk farkli durak guvencesi ────────────────────────────────────────────

def test_next_stop_kuyrugunda_baslik_tekrari_yok():
    """Her gun FARKLI bir durak: kuyruktaki tum planlar benzersiz olmali."""
    pdir = KOK / "aimagine" / "next-stop" / "plans"
    basliklar = []
    for yol in sorted(pdir.glob("part*.json")):
        plan = json.loads(yol.read_text(encoding="utf-8"))
        b = str((plan.get("episode") or {}).get("title") or "").strip()
        if b:
            basliklar.append(normalize_title(b))
    assert basliklar, "next-stop plani bulunamadi"
    tekrar = {b for b in basliklar if basliklar.count(b) > 1}
    assert not tekrar, f"kuyrukta tekrar eden durak var: {tekrar}"


def test_next_stop_duraklatildi_gunluk_yayin_kosmuyor():
    """DURAKLATILDI 2026-09-03: kanal korku kaydiragi formatina gecti.

    Bu test eskiden seridin gunluk yayina ACIK olmasini sart kosuyordu.
    Karar tersine dondu: ne 'active' status ne de aktif cron olmali. Mukerrer
    yayin kapisinin KENDI testleri (bu dosyadaki digerleri) aynen duruyor,
    cunku kapi seri geri acilirsa yine gerekli ve published.json korundu.
    """
    seri = json.loads(
        (KOK / "aimagine" / "next-stop" / "series.json").read_text(encoding="utf-8"))
    assert seri["status"] == "paused", (
        f"next-stop duraklatildi, 'paused' olmali. Bulunan: {seri['status']!r}"
    )
    wf = (KOK / ".github" / "workflows" / "next-stop.yml").read_text(encoding="utf-8")
    aktif_cron = [s for s in wf.splitlines()
                  if "cron:" in s and not s.lstrip().startswith("#")]
    assert not aktif_cron, f"next-stop cron'u kapali olmali, bulunan: {aktif_cron}"
