# -*- coding: utf-8 -*-
"""DUSMANCA dayaniklilik testleri (beyin.py).

Bu dosya implementasyon GORULMEDEN, sadece davranis sozlesmesine gore yazildi.
Amac kodu kirmak, hosgorulu olmak degil.

Kapsam:
  SOZLESME 1 - defter.jsonl yazimi atomik olmali, beyin komutu sadece okur.
  SOZLESME 2 - ag cokmusken olc/topla sessizce exit 0 vermemeli.
  EK        - kanal slug dogrulamasi, arguman hatalari, yol kacisi.

AG POLITIKASI: Hicbir test gercek ag cagrisi yapmaz. Her alt surec
(1) PYTHONPATH ile yuklenen bir sitecustomize.py icinde socket / urllib /
http.client katmanlari OSError firlatacak sekilde yamalanmis,
(2) HTTP_PROXY/HTTPS_PROXY/ALL_PROXY kapali bir porta (127.0.0.1:9)
yonlendirilmis, (3) no_proxy bosaltilmis olarak calisir.
test_ag_sondasi_kapali_dogrulamasi bu engelin gercekten etkin oldugunu
alt surecte OLCEREK kanitlar.
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

import pytest


# --------------------------------------------------------------------------
# Sabitler
# --------------------------------------------------------------------------

GECERLI_KANALLAR = ("unnatural-lab", "event-horizon", "flashpoints", "aimagine-fear")
KANAL = "unnatural-lab"
ZAMAN_ASIMI = 90  # saniye; asilirsa test FAIL olur (asili kalmak da bir hatadir)

KOPYALANACAK_EK_UZANTILAR = (".json", ".toml", ".yaml", ".yml", ".ini", ".cfg")
EK_DOSYA_BOYUT_SINIRI = 262144  # 256 KB

# Ag hatasinin kullaniciya ANLASILIR sekilde bildirildigini gosteren ipuclari.
AG_IPUCLARI = (
    "ag ", "ag'", "ag,", "ag.", "aga ", "agda", "agi ", "ağ", "network",
    "baglan", "bağlan", "baglant", "erisim", "erişim", "erisile", "erişile",
    "internet", "offline", "cevrimdisi", "çevrimdışı", "proxy", "dns",
    "ulasil", "ulaşıl", "timeout", "zaman asim", "zaman aşım", "socket",
    "connection", "unreachable", "resolve", "urlerror", "httperror",
    "api", "istek", "request",
)

TRACEBACK_IMZASI = "Traceback (most recent call last)"

# PYTHONPATH uzerinden yuklenip alt surecte tum ag katmanlarini kapatan yama.
SITECUSTOMIZE = '''# -*- coding: utf-8 -*-
"""Test kosumu icin dis ag erisimini tamamen kapatir."""
import socket

_MESAJ = "AG_KAPALI: test ortami dis ag erisimini engelliyor"


def _reddet(*args, **kwargs):
    raise OSError(_MESAJ)


try:
    socket.socket.connect = _reddet
    socket.socket.connect_ex = _reddet
    socket.socket.sendto = _reddet
except Exception:
    pass

try:
    socket.create_connection = _reddet
    socket.getaddrinfo = _reddet
    socket.gethostbyname = _reddet
    socket.gethostbyname_ex = _reddet
except Exception:
    pass

try:
    import urllib.request as _ur

    _ur.urlopen = _reddet
    _ur.OpenerDirector.open = _reddet
except Exception:
    pass

try:
    import http.client as _hc

    _hc.HTTPConnection.connect = _reddet
    _hc.HTTPSConnection.connect = _reddet
except Exception:
    pass
'''

SONDA = '''# -*- coding: utf-8 -*-
"""Ag engelinin gercekten etkin olup olmadigini olcer."""
import socket
import urllib.request

sonuc = []

try:
    urllib.request.urlopen("http://example.com", timeout=5)
    sonuc.append("URLOPEN=ACIK")
except Exception as hata:
    sonuc.append("URLOPEN=KAPALI:" + type(hata).__name__)

try:
    socket.create_connection(("93.184.216.34", 80), 3)
    sonuc.append("SOCKET=ACIK")
except Exception as hata:
    sonuc.append("SOCKET=KAPALI:" + type(hata).__name__)

try:
    socket.getaddrinfo("example.com", 80)
    sonuc.append("DNS=ACIK")
except Exception as hata:
    sonuc.append("DNS=KAPALI:" + type(hata).__name__)

print(" ".join(sonuc))
'''


# --------------------------------------------------------------------------
# beyin.py bulma
# --------------------------------------------------------------------------


def _aday_koklerde_ara(baslangic: pathlib.Path):
    for dizin in [baslangic, *baslangic.parents]:
        aday = dizin / "beyin.py"
        if aday.is_file():
            return aday.resolve()
    return None


def _beyin_py_bul():
    """BEYIN_PY ortam degiskeni -> cwd ve ust klasorler -> test dosyasi ve ustleri."""
    ham = os.environ.get("BEYIN_PY")
    if ham:
        yol = pathlib.Path(ham).expanduser()
        if yol.is_file():
            return yol.resolve()
        if yol.is_dir() and (yol / "beyin.py").is_file():
            return (yol / "beyin.py").resolve()
        return None

    bulunan = _aday_koklerde_ara(pathlib.Path.cwd().resolve())
    if bulunan is not None:
        return bulunan
    return _aday_koklerde_ara(pathlib.Path(__file__).resolve().parent)


@pytest.fixture(scope="session")
def kaynak_kok() -> pathlib.Path:
    yol = _beyin_py_bul()
    if yol is None:
        pytest.fail(
            "beyin.py BULUNAMADI. Aranan sira: BEYIN_PY ortam degiskeni, "
            "cwd ve ust klasorler, test dosyasinin klasoru ve ustleri. "
            "BEYIN_PY=<beyin.py yolu> vererek tekrar calistirin. "
            "(Sessiz skip bilerek yapilmiyor.)",
            pytrace=False,
        )
    return yol.parent


# --------------------------------------------------------------------------
# Izole proje / ag engeli kurulumu
# --------------------------------------------------------------------------


class Ortam:
    def __init__(self, proje, env, tmp_path, engel):
        self.proje = proje
        self.env = env
        self.tmp_path = tmp_path
        self.engel = engel


def _proje_kopyala(tmp_path: pathlib.Path, kaynak_kok: pathlib.Path) -> pathlib.Path:
    proje = tmp_path / "proje"
    proje.mkdir()
    for oge in kaynak_kok.iterdir():
        if oge.is_file() and oge.suffix == ".py":
            shutil.copy2(oge, proje / oge.name)
        elif (
            oge.is_file()
            and oge.suffix.lower() in KOPYALANACAK_EK_UZANTILAR
            and oge.stat().st_size <= EK_DOSYA_BOYUT_SINIRI
        ):
            shutil.copy2(oge, proje / oge.name)
        elif oge.is_dir() and oge.name == "arac":
            shutil.copytree(oge, proje / "arac")
    assert (proje / "beyin.py").is_file(), "beyin.py gecici projeye kopyalanamadi"
    return proje


def _ag_engeli_kur(tmp_path: pathlib.Path) -> pathlib.Path:
    engel = tmp_path / "_agengel"
    engel.mkdir()
    (engel / "sitecustomize.py").write_text(SITECUSTOMIZE, encoding="utf-8")
    (engel / "sonda.py").write_text(SONDA, encoding="utf-8")
    return engel


def _ortam_degiskenleri(engel: pathlib.Path) -> dict:
    env = dict(os.environ)
    env.pop("BEYIN_PY", None)

    onceki = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(engel) + ((os.pathsep + onceki) if onceki else "")

    for anahtar in (
        "HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
        "ALL_PROXY", "all_proxy", "FTP_PROXY", "ftp_proxy",
    ):
        env[anahtar] = "http://127.0.0.1:9"
    env["NO_PROXY"] = ""
    env["no_proxy"] = ""

    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["BEYIN_TEST_OFFLINE"] = "1"
    return env


@pytest.fixture()
def ortam(tmp_path: pathlib.Path, kaynak_kok: pathlib.Path) -> Ortam:
    proje = _proje_kopyala(tmp_path, kaynak_kok)
    engel = _ag_engeli_kur(tmp_path)
    return Ortam(proje=proje, env=_ortam_degiskenleri(engel), tmp_path=tmp_path, engel=engel)


# --------------------------------------------------------------------------
# Calistirma yardimcilari
# --------------------------------------------------------------------------


def _calistir(ortam: Ortam, *argumanlar, betik: str = "beyin.py", cwd=None):
    komut = [sys.executable, betik, *argumanlar]
    try:
        return subprocess.run(
            komut,
            cwd=str(cwd or ortam.proje),
            env=ortam.env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=ZAMAN_ASIMI,
        )
    except subprocess.TimeoutExpired:
        pytest.fail(
            "Komut {0} saniyede bitmedi: {1}. Ag cokmusken sonsuz yeniden deneme "
            "veya asili kalma da bir dayaniklilik hatasidir.".format(ZAMAN_ASIMI, komut),
            pytrace=False,
        )


def _cikti(surec) -> str:
    return (surec.stdout or "") + "\n" + (surec.stderr or "")


def _rapor(surec, baslik: str) -> str:
    return "{0}\n  exit={1}\n  stdout:\n{2}\n  stderr:\n{3}".format(
        baslik, surec.returncode, surec.stdout, surec.stderr
    )


# --------------------------------------------------------------------------
# Defter yardimcilari
# --------------------------------------------------------------------------


def _kanal_dizini(ortam: Ortam, kanal: str = KANAL) -> pathlib.Path:
    dizin = ortam.proje / "kanallar" / kanal
    dizin.mkdir(parents=True, exist_ok=True)
    return dizin


def _defter_yolu(ortam: Ortam, kanal: str = KANAL) -> pathlib.Path:
    return _kanal_dizini(ortam, kanal) / "defter.jsonl"


def _rapor_yolu(ortam: Ortam, kanal: str = KANAL) -> pathlib.Path:
    return _kanal_dizini(ortam, kanal) / "BEYIN.md"


def _kayit(sira: int, kanal: str = KANAL, video_id: str = None) -> dict:
    """Semayi bilmiyoruz; hem Turkce hem Ingilizce alan adlarini birlikte yaziyoruz."""
    vid = video_id or "vid{0:04d}".format(sira)
    tarih = "2026-08-{0:02d}T09:00:00Z".format((sira % 28) + 1)
    return {
        "video_id": vid,
        "id": vid,
        "videoId": vid,
        "kanal": kanal,
        "channel": kanal,
        "baslik": "Test videosu {0}".format(sira),
        "title": "Test videosu {0}".format(sira),
        "yayin_tarihi": tarih,
        "published_at": tarih,
        "publishedAt": tarih,
        "tarih": tarih,
        "olcum_zamani": tarih,
        "measured_at": tarih,
        "goruntuleme": 1000 + sira * 37,
        "izlenme": 1000 + sira * 37,
        "views": 1000 + sira * 37,
        "view_count": 1000 + sira * 37,
        "begeni": 10 + sira,
        "likes": 10 + sira,
        "like_count": 10 + sira,
        "yorum": sira,
        "comments": sira,
        "comment_count": sira,
        "sure_sn": 45,
        "duration": 45,
        "url": "https://example.invalid/watch?v=" + vid,
    }


def _defter_yaz(ortam: Ortam, adet: int = 6, kanal: str = KANAL, tekrarli: bool = False) -> pathlib.Path:
    yol = _defter_yolu(ortam, kanal)
    satirlar = [json.dumps(_kayit(i, kanal), ensure_ascii=False) for i in range(1, adet + 1)]
    if tekrarli:
        satirlar = satirlar + list(satirlar)  # her kayit iki kez
    yol.write_text("\n".join(satirlar) + "\n", encoding="utf-8")
    return yol


def _ham_defter_yaz(ortam: Ortam, metin: str, kanal: str = KANAL) -> pathlib.Path:
    yol = _defter_yolu(ortam, kanal)
    yol.write_text(metin, encoding="utf-8")
    return yol


def _tmp_artiklari_birak(ortam: Ortam, kanal: str = KANAL):
    """Yarida kesilmis bir yazimin birakabilecegi artiklari taklit eder."""
    dizin = _kanal_dizini(ortam, kanal)
    yarim = '{"video_id": "yarim-kayit-ASLA-SAYILMAMALI", "izlen'
    artiklar = [
        dizin / "defter.jsonl.tmp",
        dizin / ".defter.jsonl.tmp",
        dizin / "defter.jsonl.tmp.98765",
        dizin / "defter.jsonl.partial",
        dizin / "tmp0abcdef.defter",
    ]
    for artik in artiklar:
        artik.write_text(yarim, encoding="utf-8")
    return artiklar


def _satirlari_coz(yol: pathlib.Path):
    """Her satiri ayri ayri json.loads eder. (nesneler, bozuk_satirlar) dondurur."""
    assert yol.is_file(), "defter.jsonl kayboldu: {0}".format(yol)
    metin = yol.read_bytes().decode("utf-8")
    parcalar = metin.split("\n")
    if parcalar and parcalar[-1] == "":
        parcalar = parcalar[:-1]

    nesneler, bozuklar = [], []
    for sira, satir in enumerate(parcalar, 1):
        if satir.strip() == "":
            bozuklar.append((sira, "BOS SATIR"))
            continue
        try:
            nesneler.append(json.loads(satir))
        except Exception as hata:
            bozuklar.append((sira, "{0}: {1}".format(type(hata).__name__, satir[:120])))
    return nesneler, bozuklar


def _gecerli_jsonl_dogrula(yol: pathlib.Path, baglam: str = ""):
    nesneler, bozuklar = _satirlari_coz(yol)
    assert not bozuklar, (
        "defter.jsonl gecerli JSONL degil {0}. Bozuk satirlar: {1}".format(baglam, bozuklar)
    )
    assert nesneler, "defter.jsonl bosaldi {0}".format(baglam)
    return nesneler


def _kimlikler(nesneler):
    bulunan = set()
    for nesne in nesneler:
        if not isinstance(nesne, dict):
            continue
        for anahtar in ("video_id", "videoId", "id"):
            if anahtar in nesne:
                bulunan.add(str(nesne[anahtar]))
                break
    return bulunan


# ==========================================================================
# SOZLESME 0 - ortam dogrulamasi
# ==========================================================================


def test_beyin_py_bulunabilmeli():
    """beyin.py bulunamazsa test ACIKCA fail olur; sessiz skip yok."""
    yol = _beyin_py_bul()
    assert yol is not None and yol.is_file(), (
        "beyin.py bulunamadi. BEYIN_PY ortam degiskeni ile yolunu verin ya da "
        "testi projenin icinden calistirin."
    )


def test_ag_sondasi_kapali_dogrulamasi(ortam: Ortam):
    """Testlerin GERCEKTEN dis aga cikmadigini alt surecte olcerek kanitlar."""
    surec = _calistir(ortam, betik=str(ortam.engel / "sonda.py"))
    cikti = _cikti(surec)
    assert "URLOPEN=ACIK" not in cikti, "urlopen hala calisiyor, ag engeli etkin degil:\n" + cikti
    assert "SOCKET=ACIK" not in cikti, "ham socket hala calisiyor, ag engeli etkin degil:\n" + cikti
    assert "DNS=ACIK" not in cikti, "DNS hala cozuluyor, ag engeli etkin degil:\n" + cikti
    assert "URLOPEN=KAPALI" in cikti and "SOCKET=KAPALI" in cikti, (
        "Ag engeli sondasi beklenen ciktiyi vermedi:\n" + cikti
    )


# ==========================================================================
# SOZLESME 1 - defter yazimi atomik olmali
# ==========================================================================


def test_beyin_defteri_bayt_bayt_degistirmemeli(ortam: Ortam):
    """beyin komutu sadece OKUR: defter.jsonl bayt bayt ayni kalmali."""
    defter = _defter_yaz(ortam, adet=8)
    once = defter.read_bytes()

    surec = _calistir(ortam, "beyin", KANAL)

    sonra = defter.read_bytes()
    assert sonra == once, _rapor(
        surec,
        "beyin komutu defter.jsonl dosyasini DEGISTIRDI (sadece okumali). "
        "once={0} bayt, sonra={1} bayt".format(len(once), len(sonra)),
    )


def test_bozuk_satir_raporda_belirtilmeli(ortam: Ortam):
    """Parse edilemeyen satir BEYIN.md icinde 'bozuk' olarak gecmeli."""
    saglam = [json.dumps(_kayit(i), ensure_ascii=False) for i in range(1, 6)]
    metin = "\n".join(saglam[:2] + ['{"video_id": "bozuk-1", "izlenme": '] + saglam[2:]) + "\n"
    _ham_defter_yaz(ortam, metin)

    surec = _calistir(ortam, "beyin", KANAL)
    rapor = _rapor_yolu(ortam)

    assert rapor.is_file(), _rapor(surec, "BEYIN.md uretilmedi (bozuk satirli defter)")
    icerik = rapor.read_text(encoding="utf-8", errors="replace").lower()
    assert "bozuk" in icerik, _rapor(
        surec,
        "BEYIN.md icinde 'bozuk' gecmiyor; bozuk satir sessizce yutulmus. "
        "Rapor ilk 800 karakter:\n" + icerik[:800],
    )


def test_bozuk_satir_kalici_silinmemeli(ortam: Ortam):
    """beyin calistiktan sonra defter.jsonl BAYT BAYT AYNI kalmali (bozuk satir dahil)."""
    saglam = [json.dumps(_kayit(i), ensure_ascii=False) for i in range(1, 6)]
    bozuk_satir = '{"video_id": "bozuk-2", "izlenme": '
    metin = "\n".join(saglam[:3] + [bozuk_satir] + saglam[3:]) + "\n"
    defter = _ham_defter_yaz(ortam, metin)
    once = defter.read_bytes()

    surec = _calistir(ortam, "beyin", KANAL)

    sonra = defter.read_bytes()
    assert sonra == once, _rapor(
        surec, "beyin, bozuk satiri iceren defteri DEGISTIRDI (kalici silme/temizleme yasak)"
    )
    assert bozuk_satir in sonra.decode("utf-8"), _rapor(
        surec, "Bozuk satir defterden KALICI olarak silinmis"
    )


def test_yarim_tmp_artigi_defteri_bozmamali(ortam: Ortam):
    """Yarida kesilmis yazimin .tmp artiklari eski defteri BOZMAMALI."""
    defter = _defter_yaz(ortam, adet=9)
    once_nesneler = _gecerli_jsonl_dogrula(defter, "(baslangic)")
    once_kimlikler = _kimlikler(once_nesneler)
    _tmp_artiklari_birak(ortam)

    surecler = {
        "beyin": _calistir(ortam, "beyin", KANAL),
        "olc": _calistir(ortam, "olc", KANAL),
        "topla": _calistir(ortam, "topla", KANAL),
    }

    sonra_nesneler = _gecerli_jsonl_dogrula(defter, "(tmp artiklarindan sonra)")
    sonra_kimlikler = _kimlikler(sonra_nesneler)
    eksik = once_kimlikler - sonra_kimlikler
    assert not eksik, "tmp artigi yuzunden defterden kayit kayboldu: {0}\n{1}".format(
        sorted(eksik),
        "\n".join(_rapor(s, ad) for ad, s in surecler.items()),
    )


def test_tmp_artigi_icerigi_deftere_sizmamali(ortam: Ortam):
    """Yarim .tmp icerigi hicbir sekilde defter.jsonl'e karismamali."""
    defter = _defter_yaz(ortam, adet=5)
    _tmp_artiklari_birak(ortam)

    for komut in ("beyin", "olc", "topla"):
        _calistir(ortam, komut, KANAL)

    icerik = defter.read_text(encoding="utf-8", errors="replace")
    assert "yarim-kayit-ASLA-SAYILMAMALI" not in icerik, (
        "Yarim .tmp artiginin icerigi defter.jsonl icine sizmis"
    )
    _gecerli_jsonl_dogrula(defter, "(tmp sizintisi kontrolu)")


@pytest.mark.parametrize("komut", ["beyin", "olc", "topla"])
def test_defter_her_komuttan_sonra_gecerli_jsonl(ortam: Ortam, komut: str):
    """Her komuttan sonra: her satir ayri json.loads olur, yarim son satir kalmaz."""
    defter = _defter_yaz(ortam, adet=7)
    surec = _calistir(ortam, komut, KANAL)

    ham = defter.read_bytes()
    assert ham, _rapor(surec, "{0} sonrasi defter.jsonl BOSALDI".format(komut))

    nesneler, bozuklar = _satirlari_coz(defter)
    assert not bozuklar, _rapor(
        surec,
        "{0} sonrasi defter.jsonl gecerli JSONL degil. Bozuk satirlar: {1}".format(komut, bozuklar),
    )
    assert nesneler, _rapor(surec, "{0} sonrasi defterde hic kayit kalmadi".format(komut))
    metin = ham.decode("utf-8")
    assert metin.endswith("\n") or not metin.split("\n")[-1].strip() == "", (
        "{0} sonrasi dosya sonunda yarim/tuhaf satir var".format(komut)
    )


def test_duplicate_video_id_sayimi_sismemeli(ortam: Ortam):
    """15 benzersiz video iki kez yazildiginda rapor 30 dememeli (ya da acikca uyarmali)."""
    defter = _defter_yaz(ortam, adet=15, tekrarli=True)
    nesneler, bozuklar = _satirlari_coz(defter)
    assert not bozuklar and len(nesneler) == 30
    assert len(_kimlikler(nesneler)) == 15

    surec = _calistir(ortam, "beyin", KANAL)
    rapor = _rapor_yolu(ortam)
    assert rapor.is_file(), _rapor(surec, "BEYIN.md uretilmedi (duplicate testi)")

    metin = rapor.read_text(encoding="utf-8", errors="replace")
    dusuk = metin.lower()

    uyarildi = any(
        ipucu in dusuk
        for ipucu in (
            "mukerrer", "mükerrer", "tekrar eden", "tekrarli", "tekrarlı",
            "duplicate", "yinelen", "cift kayit", "çift kayıt", "benzersiz", "unique",
        )
    )
    if uyarildi:
        return

    # Uyari yoksa: video sayisi 30 olarak raporlanmamali.
    # "son 30 gun" gibi zaman ifadeleri hariç tutulur.
    kotu_satirlar = []
    desen = re.compile(r"(?<![0-9])30(?![0-9])(?!\s*(gun|gün|g\b|saat|sa\b|dk|dakika|hafta|ay\b|sn|saniye|%))")
    for satir in metin.splitlines():
        alcak = satir.lower()
        if not any(k in alcak for k in ("video", "kayit", "kayıt", "toplam", "adet", "bolum", "bölüm")):
            continue
        if desen.search(alcak):
            kotu_satirlar.append(satir.strip())

    assert not kotu_satirlar, (
        "Duplicate kayitlar sayimi sisirmis: 15 benzersiz video 30 gibi raporlanmis ve "
        "hicbir mukerrer uyarisi yok. Suclu satirlar: {0}".format(kotu_satirlar)
    )


@pytest.mark.parametrize("komut", ["olc", "topla"])
def test_ag_cokmusken_yazan_komut_defteri_bozmamali(ortam: Ortam, komut: str):
    """olc/topla ag cokmusken basarisiz olsa bile eski defter BOZULMADAN kalmali."""
    defter = _defter_yaz(ortam, adet=12)
    once_kimlikler = _kimlikler(_gecerli_jsonl_dogrula(defter, "(baslangic)"))

    surec = _calistir(ortam, komut, KANAL)

    sonra_nesneler = _gecerli_jsonl_dogrula(defter, "({0} basarisiz olduktan sonra)".format(komut))
    eksik = once_kimlikler - _kimlikler(sonra_nesneler)
    assert not eksik, _rapor(
        surec,
        "{0} ag cokmusken defteri bozdu / kayit kaybetti: {1}".format(komut, sorted(eksik)),
    )


def test_olc_yarim_tmp_dosyasi_birakmamali_eger_defter_bozulacaksa(ortam: Ortam):
    """Cokmeden sonra kalan gecici dosya bir dahaki okumayi bozmamali."""
    defter = _defter_yaz(ortam, adet=6)
    _calistir(ortam, "olc", KANAL)  # ag yok, basarisiz olmasi beklenir

    # Cokme sonrasi kalan artiklarla birlikte beyin yine dogru calismali.
    surec = _calistir(ortam, "beyin", KANAL)
    _gecerli_jsonl_dogrula(defter, "(olc cokusu sonrasi)")
    assert surec.returncode == 0, _rapor(
        surec, "olc cokusundan kalan artiklar beyin komutunu kirdi (beyin ag kullanmaz, exit 0 olmali)"
    )


# ==========================================================================
# SOZLESME 2 - ag cokunce sessiz yesil olmamali
# ==========================================================================


def test_olc_ag_yokken_exit_0_vermemeli(ortam: Ortam):
    _defter_yaz(ortam, adet=4)
    surec = _calistir(ortam, "olc", KANAL)
    assert surec.returncode != 0, _rapor(
        surec,
        "SESSIZ YESIL: ag tamamen erisilemezken 'olc' exit 0 verdi. "
        "Ag cokmesi basari olarak raporlanamaz.",
    )


def test_topla_ag_yokken_exit_0_vermemeli(ortam: Ortam):
    _defter_yaz(ortam, adet=4)
    surec = _calistir(ortam, "topla", KANAL)
    assert surec.returncode != 0, _rapor(
        surec,
        "SESSIZ YESIL: ag tamamen erisilemezken 'topla' exit 0 verdi.",
    )


def test_bos_defter_ve_ag_cokmus_iken_olc_exit_0_vermemeli(ortam: Ortam):
    """Defter BOS + ag COKMUS: 'yeni video yok' deyip yesil donmek YASAK."""
    defter = _defter_yolu(ortam)
    defter.write_text("", encoding="utf-8")

    surec = _calistir(ortam, "olc", KANAL)
    cikti = _cikti(surec).lower()

    assert surec.returncode != 0, _rapor(
        surec,
        "SESSIZ YESIL: bos defter + cokmus ag durumunda 'olc' exit 0 verdi. "
        "Bu tam olarak yasaklanan 'yeni video yok' yalanidir.",
    )
    assert "yeni video yok" not in cikti or surec.returncode != 0


@pytest.mark.parametrize("komut", ["olc", "topla"])
def test_ag_hatasi_anlasilir_mesaj_vermeli_traceback_dokmemeli(ortam: Ortam, komut: str):
    """Cikti ag/erisim sorununu ANLATMALI; cipllak traceback kabul edilmez."""
    _defter_yaz(ortam, adet=4)
    surec = _calistir(ortam, komut, KANAL)
    cikti = _cikti(surec)
    dusuk = cikti.lower()

    assert TRACEBACK_IMZASI not in cikti, _rapor(
        surec, "{0} ag hatasinda ham traceback dokuyor; anlasilir mesaj gerekli".format(komut)
    )
    assert any(ipucu in dusuk for ipucu in AG_IPUCLARI), _rapor(
        surec,
        "{0} ciktisinda ag/erisim sorunu oldugu ANLASILMIYOR. "
        "Beklenen ipuclarindan hicbiri yok.".format(komut),
    )
    assert cikti.strip(), _rapor(surec, "{0} hicbir sey yazmadan basarisiz oldu".format(komut))


def test_beyin_ag_yokken_exit_0_vermeli(ortam: Ortam):
    """beyin ag kullanmaz: ag cokmusken bile defterden okuyup exit 0 vermeli."""
    _defter_yaz(ortam, adet=10)
    surec = _calistir(ortam, "beyin", KANAL)
    assert surec.returncode == 0, _rapor(
        surec,
        "beyin komutu ag kullanmiyor olmasina ragmen ag cokmusken basarisiz oldu. "
        "Ag bagimliligi sizmis olabilir.",
    )
    assert TRACEBACK_IMZASI not in _cikti(surec), _rapor(surec, "beyin traceback dokuyor")


def test_beyin_raporu_dogru_yola_yazmali(ortam: Ortam):
    """Rapor kanallar/<kanal>/BEYIN.md olmali ve bos olmamali."""
    _defter_yaz(ortam, adet=10)
    surec = _calistir(ortam, "beyin", KANAL)
    rapor = _rapor_yolu(ortam)

    assert rapor.is_file(), _rapor(surec, "kanallar/{0}/BEYIN.md uretilmedi".format(KANAL))
    icerik = rapor.read_text(encoding="utf-8", errors="replace").strip()
    assert len(icerik) > 20, _rapor(surec, "BEYIN.md pratikte bos: {0!r}".format(icerik[:120]))


def test_ag_calisirken_yeni_video_yok_vakasi():
    """ACIK BILDIRIM: 'ag calisiyor ama yeni video yok -> exit 0' vakasi TEST EDILMEDI.

    Gerceklestirmek icin kanalin uzak API'sinin sema ve uc noktasi bilinmeli ve
    sahte bir HTTP sunucusu ayaga kaldirilmali. Sozlesme implementasyonu
    gostermedigi icin bu vaka SOZLESME GEREGI atlanmistir; sessizce gecirilmiyor,
    burada acikca isaretleniyor.
    """
    pytest.skip(
        "ATLANDI (acik bildirim): 'ag calisiyor + yeni video yok -> exit 0' vakasi, "
        "uzak API semasi bilinmeden sahte sunucu ile simule edilemedi. "
        "Testin geri kalani ag COKMUS senaryosunu kapsar."
    )


# ==========================================================================
# EK - kanal slug dogrulamasi ve arguman dayanikliligi
# ==========================================================================


@pytest.mark.parametrize(
    "kotu_slug",
    [
        "unnatural_lab",
        "Unnatural-Lab",
        "flashpoint",
        "eventhorizon",
        "aimagine_fear",
        "kanal1",
        "",
        " ",
        "unnatural-lab ",
        "unnatural-lab;rm",
    ],
)
@pytest.mark.parametrize("komut", ["olc", "topla", "beyin"])
def test_gecersiz_kanal_bilinmeyen_kanal_ve_exit_1(ortam: Ortam, komut: str, kotu_slug: str):
    """Gecersiz slug -> 'Bilinmeyen kanal' mesaji ve exit 1."""
    surec = _calistir(ortam, komut, kotu_slug)
    cikti = _cikti(surec)

    assert surec.returncode == 1, _rapor(
        surec, "{0} {1!r}: gecersiz slug icin exit 1 beklendi".format(komut, kotu_slug)
    )
    assert "Bilinmeyen kanal" in cikti, _rapor(
        surec, "{0} {1!r}: 'Bilinmeyen kanal' mesaji yok".format(komut, kotu_slug)
    )
    assert TRACEBACK_IMZASI not in cikti, _rapor(
        surec, "{0} {1!r}: gecersiz slug traceback dokturuyor".format(komut, kotu_slug)
    )


@pytest.mark.parametrize("kanal", list(GECERLI_KANALLAR))
def test_gecerli_sluglar_bilinmeyen_kanal_dememeli(ortam: Ortam, kanal: str):
    """Dort gecerli slug da taninmali; beyin komutu bunlarda exit 0 vermeli."""
    _defter_yaz(ortam, adet=5, kanal=kanal)
    surec = _calistir(ortam, "beyin", kanal)
    cikti = _cikti(surec)

    assert "Bilinmeyen kanal" not in cikti, _rapor(
        surec, "Gecerli slug {0!r} reddedildi".format(kanal)
    )
    assert surec.returncode == 0, _rapor(
        surec, "Gecerli slug {0!r} icin beyin exit 0 vermedi".format(kanal)
    )


@pytest.mark.parametrize(
    "kacis",
    ["../../../pwned", "..\\..\\pwned", "kanallar/../../pwned", "/pwned", "unnatural-lab/../pwned"],
)
def test_kanal_slugu_yol_kacisina_izin_vermemeli(ortam: Ortam, kacis: str):
    """Yol kacisi denemeleri reddedilmeli ve proje disina hicbir sey yazilmamali."""
    surec = _calistir(ortam, "beyin", kacis)

    assert surec.returncode != 0, _rapor(
        surec, "Yol kacisi {0!r} kabul edildi (exit 0)".format(kacis)
    )
    sizanlar = [str(p) for p in ortam.tmp_path.rglob("*pwned*")]
    assert not sizanlar, "Yol kacisi {0!r} dosya sistemine sizdi: {1}".format(kacis, sizanlar)


def test_eksik_veya_hatali_argumanlar_sessiz_basari_vermemeli(ortam: Ortam):
    """Arguman yok / bilinmeyen komut / kanal eksik: sessizce yesil donulmemeli."""
    _defter_yaz(ortam, adet=3)

    # 1) Hicbir arguman yok: ya hata kodu, ya da acikca yardim metni.
    bos = _calistir(ortam)
    bos_cikti = _cikti(bos).lower()
    if bos.returncode == 0:
        assert any(k in bos_cikti for k in ("kullanim", "kullanım", "usage", "komut", "olc", "topla", "beyin")), (
            _rapor(bos, "Argumansiz calistirma exit 0 verdi ama yardim/kullanim metni de yazmadi")
        )
    assert TRACEBACK_IMZASI not in _cikti(bos), _rapor(bos, "Argumansiz calistirma traceback dokuyor")

    # 2) Bilinmeyen komut.
    bilinmeyen = _calistir(ortam, "zipzip", KANAL)
    assert bilinmeyen.returncode != 0, _rapor(bilinmeyen, "Bilinmeyen komut exit 0 verdi")
    assert TRACEBACK_IMZASI not in _cikti(bilinmeyen), _rapor(
        bilinmeyen, "Bilinmeyen komut traceback dokuyor"
    )

    # 3) Kanal argumani eksik.
    for komut in ("olc", "topla", "beyin"):
        eksik = _calistir(ortam, komut)
        assert eksik.returncode != 0, _rapor(
            eksik, "{0} kanal argumani olmadan exit 0 verdi".format(komut)
        )
        assert TRACEBACK_IMZASI not in _cikti(eksik), _rapor(
            eksik, "{0} eksik arguman icin traceback dokuyor".format(komut)
        )
