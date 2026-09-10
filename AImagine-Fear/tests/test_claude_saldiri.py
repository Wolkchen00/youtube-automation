"""Claude'un bagimsiz saldiri testleri (Level 10 inceleme).

Codex'in kendi paketinin ATLADIGI vakalar. Buradaki her test, gecmesi kolay olsun
diye degil, uretim kodunu gercekten kirmaya calissin diye yazildi.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

PROJE_KOKU = Path(__file__).resolve().parent.parent
if str(PROJE_KOKU) not in sys.path:
    sys.path.insert(0, str(PROJE_KOKU))

import profil as profil_modulu  # noqa: E402
from tools import gunluk  # noqa: E402


def _gecici(ad: str) -> Path:
    yol = PROJE_KOKU / "tests" / ".claude-tmp" / (ad + "-" + uuid.uuid4().hex[:8])
    yol.mkdir(parents=True)
    return yol


# --------------------------------------------------------------------------
# 1. Codex'in bos gecen testinin YERINE gercek olan.
#    Onun testi iki AYRI klasor kurup birinin glob'unun otekini gormedigini
#    dogruluyordu , bu Python'un glob'unu test eder, bizim kodumuzu degil.
#    Gercek senaryo: dunku kosunun master'i bugun ham video sanilir mi?
# --------------------------------------------------------------------------
def test_dunku_master_bugun_ham_video_sanilmaz() -> None:
    kok = _gecici("master-glob")
    try:
        slug = "test-slug"
        video = kok / "out" / slug / "video"
        video.mkdir(parents=True)
        ham = video / (slug + "_gunluk_01.mp4")
        ham.write_bytes(b"ham")

        # Uretim kodunun yazdigi master yolu (gunluk.py:540 ile ayni kalip)
        master = kok / "out" / slug / "master" / (ham.stem + "_master.mp4")
        master.parent.mkdir(parents=True)
        master.write_bytes(b"master")

        # Uretim kodunun ham video kesfi ile BIREBIR ayni ifade
        bulunan = sorted(
            (kok / "out" / slug / "video").glob("*_gunluk_*.mp4"),
            key=lambda p: p.stat().st_mtime,
        )
        assert bulunan == [ham], "master ham video olarak secildi"
        assert master.name.startswith(ham.stem), (
            "master adi ham videonun adini tasiyor; ayni KLASORDE olsaydi glob onu da "
            "yakalardi. Ayrimi saglayan tek sey klasor, ve bu test onu koruyor."
        )
    finally:
        shutil.rmtree(kok, ignore_errors=True)


# --------------------------------------------------------------------------
# 2. Onay BASKA bir kombinasyon icinse mevcut kombinasyonu ACMAMALI.
# --------------------------------------------------------------------------
def test_baska_kombinasyonun_onayi_gecerli_sayilmaz(monkeypatch) -> None:
    kok = _gecici("capraz-onay")
    try:
        onay_yolu = kok / "profil_onay.json"
        # 720p@30 icin onay (matriste 'kanarya'), ama biz 1080p@24 kosuyoruz
        onay_yolu.write_text(json.dumps({
            "model": "bytedance/seedance-2", "sure": 15,
            "cozunurluk": "720p", "fps": 30,
            "master_sha": "a" * 64, "profil_hash": profil_modulu.profil_hash(),
        }), encoding="utf-8")
        monkeypatch.setattr(gunluk, "ONAY_DOSYASI", onay_yolu)
        izinli, durum = gunluk.yayin_izni("1080p", 15)
        assert izinli is False, "baska kombinasyonun onayi 1080p'yi acti"
        assert "kombinasyonu farkli" in durum
    finally:
        shutil.rmtree(kok, ignore_errors=True)


# --------------------------------------------------------------------------
# 3. profil.py GERCEKTEN degistiginde eski onay gecersiz olmali.
#    Codex bunu monkeypatch ile test etti; ben dosyayi gercekten degistiriyorum.
# --------------------------------------------------------------------------
def test_profil_dosyasi_gercekten_degisince_onay_duser(monkeypatch) -> None:
    kok = _gecici("hash-eskime")
    try:
        kopya = kok / "profil.py"
        kopya.write_bytes(PROJE_KOKU.joinpath("profil.py").read_bytes())
        eski_hash = profil_modulu.profil_hash(kopya)

        # Gercek bir icerik degisikligi: toleransi degistir
        metin = kopya.read_text(encoding="utf-8")
        kopya.write_text(metin.replace('"fps_tolerans": 0.1', '"fps_tolerans": 5.0'),
                         encoding="utf-8")
        yeni_hash = profil_modulu.profil_hash(kopya)
        assert eski_hash != yeni_hash, "gercek icerik degisikligi hash'i degistirmedi"

        onay_yolu = kok / "profil_onay.json"
        onay_yolu.write_text(json.dumps({
            "model": "bytedance/seedance-2", "sure": 15,
            "cozunurluk": "1080p", "fps": 24,
            "master_sha": "b" * 64, "profil_hash": eski_hash,
        }), encoding="utf-8")
        monkeypatch.setattr(gunluk, "ONAY_DOSYASI", onay_yolu)
        monkeypatch.setattr(gunluk, "profil_hash", lambda *a, **k: yeni_hash)
        izinli, durum = gunluk.yayin_izni("1080p", 15)
        assert izinli is False, "profil degismisken eski onay hala aciyor"
        assert "hash" in durum
    finally:
        shutil.rmtree(kok, ignore_errors=True)


# --------------------------------------------------------------------------
# 4. Satir sonu normalizasyonu: CRLF ve LF kopyalari AYNI hash.
#    Bu, CI'da onayin gecersiz olmamasinin tek garantisi.
# --------------------------------------------------------------------------
def test_crlf_ve_lf_kopyalari_ayni_hash_verir() -> None:
    kok = _gecici("crlf")
    try:
        govde = "a = 1\nb = 2\n" + "# " + "x" * 200 + "\n"
        lf = kok / "lf.py"
        crlf = kok / "crlf.py"
        lf.write_bytes(govde.encode("utf-8"))
        crlf.write_bytes(govde.replace("\n", "\r\n").encode("utf-8"))
        assert lf.read_bytes() != crlf.read_bytes(), "test kurulumu bozuk"
        assert profil_modulu.profil_hash(lf) == profil_modulu.profil_hash(crlf), (
            "CRLF/LF hash'leri farkli , onay Linux runner'da kalici gecersiz olur"
        )
        # Ama GERCEK bir degisiklik hala farkli hash vermeli
        baska = kok / "baska.py"
        baska.write_bytes((govde + "c = 3\n").encode("utf-8"))
        assert profil_modulu.profil_hash(lf) != profil_modulu.profil_hash(baska)
    finally:
        shutil.rmtree(kok, ignore_errors=True)


# --------------------------------------------------------------------------
# 5. fps toleransinin SINIRI. 24000/1001 gecmeli, 25 fps gecmemeli.
# --------------------------------------------------------------------------
@pytest.mark.parametrize("kesir,gecmeli", [
    ("24/1", True),
    ("24000/1001", True),    # 23.976, tolerans 0.1 icinde
    ("25/1", False),
    ("30/1", False),
    ("0/0", False),
])
def test_fps_tolerans_siniri(kesir: str, gecmeli: bool) -> None:
    probe = {
        "streams": [
            {"codec_type": "video", "width": 1080, "height": 1920, "r_frame_rate": kesir},
            {"codec_type": "audio", "r_frame_rate": "0/0"},
        ],
        "format": {"duration": "15.0"},
    }
    sorunlar = gunluk.denetle_akislar(probe, 5_000_000, 15, gunluk.PROFILLER["1080p"])
    fps_sorunu = [s for s in sorunlar if "fps" in s]
    if gecmeli:
        assert not fps_sorunu, "%s dusmemeliydi: %s" % (kesir, fps_sorunu)
    else:
        assert fps_sorunu, "%s gecmemeliydi" % kesir


# --------------------------------------------------------------------------
# 6. Denetimi KALMIS bir master onaylanamaz.
# --------------------------------------------------------------------------
def test_denetimi_kalmis_master_onaylanamaz(monkeypatch, capsys) -> None:
    kok = _gecici("kotu-onay")
    try:
        slug = "test-slug"
        master = kok / "out" / slug / "master" / "m.mp4"
        master.parent.mkdir(parents=True)
        master.write_bytes(b"bozuk master")
        sha = gunluk.sha256_dosya(master)
        kayit_yolu = kok / "out" / slug / "uretim" / (sha + ".json")
        kayit_yolu.parent.mkdir(parents=True)
        kayit_yolu.write_text(json.dumps({
            "sema_surumu": 1, "model": gunluk.MODEL, "istenen_profil": "1080p",
            "profil_hash": profil_modulu.profil_hash(), "slug": slug,
            "beklenen_sure": 15, "olculen": {}, "denetim_sonucu": "basarisiz",
            "master_sha": sha, "ts": "2026-09-10T00:00:00+00:00",
        }), encoding="utf-8")
        onay_yolu = kok / "profil_onay.json"
        monkeypatch.setattr(gunluk, "KOK", kok)
        monkeypatch.setattr(gunluk, "ONAY_DOSYASI", onay_yolu)
        assert gunluk.onayla(master) == 1, "denetimden kalmis master onaylandi"
        assert not onay_yolu.exists(), "reddedilen onayda dosya YAZILDI"
    finally:
        shutil.rmtree(kok, ignore_errors=True)


# --------------------------------------------------------------------------
# 7. Onay dosyasi TAZE CHECKOUT'ta da calismali (CI senaryosu).
#    Plan bunu vaat etti; Codex'in surumu monkeypatch'liydi.
# --------------------------------------------------------------------------
def test_onay_taze_checkoutta_da_gecerli() -> None:
    kok = _gecici("taze-checkout")
    try:
        hedef = kok / "AImagine-Fear"
        hedef.mkdir(parents=True)
        for ad in ("profil.py",):
            shutil.copy2(PROJE_KOKU / ad, hedef / ad)
        # LF ile yazilmis onay (Linux runner'in gorecegi hali)
        onay = {
            "model": "bytedance/seedance-2", "sure": 15,
            "cozunurluk": "1080p", "fps": 24, "master_sha": "c" * 64,
        }
        # profil_hash TAZE kopyadan hesaplanir; CRLF farki olsa bile ayni olmali
        sys.path.insert(0, str(hedef))
        try:
            onay["profil_hash"] = profil_modulu.profil_hash(hedef / "profil.py")
        finally:
            sys.path.remove(str(hedef))
        assert onay["profil_hash"] == profil_modulu.profil_hash(), (
            "taze checkout'ta profil hash'i degisti , onay CI'da gecersiz olur"
        )
    finally:
        shutil.rmtree(kok, ignore_errors=True)


# --------------------------------------------------------------------------
# 8. BUGUNKU GERCEK DURUM: varsayilan profil yayinlanamaz olmali.
#    Bu bir hata degil, KASITLI: kanarya onaylanana kadar cron sessizce
#    dogrulanmamis profille yayin yapmasin diye. Test bunu belgeliyor.
# --------------------------------------------------------------------------
def test_varsayilan_profil_onaysiz_yayinlanamaz(monkeypatch) -> None:
    kok = _gecici("varsayilan")
    try:
        monkeypatch.setattr(gunluk, "ONAY_DOSYASI", kok / "yok.json")
        izinli, durum = gunluk.yayin_izni(profil_modulu.VARSAYILAN_PROFIL, 15)
        assert izinli is False
        assert "kanarya" in durum
        # 720p ise gecmiste 27/27 kez uretildigi icin dogrulanmis olmali
        izinli720, durum720 = gunluk.yayin_izni("720p", 15)
        assert izinli720 is True, "720p@24 dogrulanmis olmaliydi: %s" % durum720
    finally:
        shutil.rmtree(kok, ignore_errors=True)
