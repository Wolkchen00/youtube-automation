"""Teslim rejimi damgasi ve kusur defteri.

Iki kor nokta kapatiliyor:

  1. REJIM. Defter yalniz YouTube'a cikani olcer. Ayarlar degisince (ornek:
     event-horizon 10 Eylul'de -22 LUFS ve yazisizken -14 LUFS ve kunyeli
     oldu) eski ve yeni kayitlar ayni urunun iki ornegi DEGILDIR. Havuzlanirsa
     beyin izlenme farkini yanlis sebebe baglar.

  2. KUSUR. Uretilip yayinlanmayan bolum deftere hic girmez, yani en cok
     ogrenilecek hatalar gorunmez. Ustelik series.json yalnizca ANLIK durumu
     tutar: iki kosu arasinda kendini toparlayan bir hata (olculdu:
     unnatural-lab part 33, AUDIO_MASTER, yeniden denemede yayinlandi) hicbir
     iz birakmazdi.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ZAMAN_ASIMI = 180

BEYIN_PY = None
_burada = Path(__file__).resolve()
for _klasor in [_burada.parent, *_burada.parents]:
    _aday = _klasor / "beyin.py"
    if _aday.is_file():
        BEYIN_PY = _aday.resolve()
        break

pytestmark = pytest.mark.skipif(BEYIN_PY is None, reason="beyin.py bulunamadi")


def _modul():
    """beyin.py'yi modul olarak yukle (saf fonksiyonlari dogrudan test etmek icin)."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("beyin_modulu", BEYIN_PY)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


# ----------------------------------------------------------------- kurulum


def _sahte_seri(kok: Path, rel: str, bible: dict, series: dict | None = None) -> Path:
    """Gecici depoda sahte bir seri klasoru kurar."""
    klasor = kok / rel
    klasor.mkdir(parents=True, exist_ok=True)
    (klasor / "bible.json").write_text(
        json.dumps(bible, ensure_ascii=False), encoding="utf-8")
    if series is not None:
        (klasor / "series.json").write_text(
            json.dumps(series, ensure_ascii=False), encoding="utf-8")
    return klasor


def _bible(**seri_ustu) -> dict:
    seri = {"slug": "unnatural-lab", "resolution": "1080p", "aspect_ratio": "9:16",
            "micro_trim": 0.25, "audio_smooth": True}
    seri.update(seri_ustu)
    return {"series": seri, "music": True, "art_style": "x"}


def _beyin_kok(tmp_path: Path) -> Path:
    """gunluk_beyin/ karsiligi bir alt klasor; seri dosyalari BIR UST dizinde."""
    kok = tmp_path / "gunluk_beyin"
    kok.mkdir(parents=True, exist_ok=True)
    return kok


# -------------------------------------------------------------- rejim: saf


def test_kaynak_yoksa_rejim_none_dondurur_patlamaz(tmp_path):
    """Sandbox'ta ve aimagine-fear'de seri dosyasi YOK. Bu hata degildir."""
    m = _modul()
    kok = _beyin_kok(tmp_path)
    assert m.delivery_regime("unnatural-lab", root=str(kok)) is None
    assert m.delivery_regime("bilinmeyen-kanal", root=str(kok)) is None
    assert m.held_episodes("unnatural-lab", root=str(kok)) is None


def test_teslimi_degistiren_alan_rejimi_degistirir(tmp_path):
    m = _modul()
    kok = _beyin_kok(tmp_path)
    rel = os.path.join("sentinal_ihsan", "unnatural-lab")

    _sahte_seri(tmp_path, rel, _bible(master_lufs=None))
    once = m.delivery_regime("unnatural-lab", root=str(kok))
    assert once is not None

    _sahte_seri(tmp_path, rel, _bible(master_lufs=-14))
    sonra = m.delivery_regime("unnatural-lab", root=str(kok))
    assert sonra["id"] != once["id"], "master_lufs degisti, rejim ayni kaldi"

    degisenler = m.regime_diff(once["alanlar"], sonra["alanlar"])
    assert any("master_lufs" in satir for satir in degisenler)


def test_teslimi_degistirmeyen_alan_rejimi_degistirmez(tmp_path):
    """art_style bir metin tarifi; teslim edilen dosyayi olculebilir sekilde
    degistirmez. Her kucuk duzenleme rejim kirarsa damga ise yaramaz."""
    m = _modul()
    kok = _beyin_kok(tmp_path)
    rel = os.path.join("sentinal_ihsan", "unnatural-lab")

    _sahte_seri(tmp_path, rel, _bible(master_lufs=-14))
    once = m.delivery_regime("unnatural-lab", root=str(kok))

    bible = _bible(master_lufs=-14)
    bible["art_style"] = "bambaska bir tarif"
    _sahte_seri(tmp_path, rel, bible)
    sonra = m.delivery_regime("unnatural-lab", root=str(kok))
    assert sonra["id"] == once["id"]


def test_kunye_ve_baslik_kalibi_rejime_dahil(tmp_path):
    """Ekran yazisi ve baslik kalibi izlenmeyi dogrudan etkiler; rejime girmeli."""
    m = _modul()
    kok = _beyin_kok(tmp_path)
    rel = os.path.join("sentinal_ihsan", "unnatural-lab")

    _sahte_seri(tmp_path, rel, _bible(), {"auto_replenish": {"title_style": "eski"}})
    once = m.delivery_regime("unnatural-lab", root=str(kok))
    _sahte_seri(tmp_path, rel, _bible(), {"auto_replenish": {"title_style": "yeni"}})
    assert m.delivery_regime("unnatural-lab", root=str(kok))["id"] != once["id"]

    _sahte_seri(tmp_path, rel, _bible(title_card={"enabled": True}))
    kunyeli = m.delivery_regime("unnatural-lab", root=str(kok))
    _sahte_seri(tmp_path, rel, _bible())
    assert m.delivery_regime("unnatural-lab", root=str(kok))["id"] != kunyeli["id"]


def test_rejim_kaydi_bir_kez_yazilir(tmp_path):
    m = _modul()
    kok = _beyin_kok(tmp_path)
    _sahte_seri(tmp_path, os.path.join("sentinal_ihsan", "unnatural-lab"),
                _bible(master_lufs=-14))
    rejim = m.delivery_regime("unnatural-lab", root=str(kok))

    m.remember_regime("unnatural-lab", rejim, root=str(kok))
    ilk = m.read_regimes("unnatural-lab", root=str(kok))
    assert list(ilk) == [rejim["id"]]
    damga = ilk[rejim["id"]]["ilk_gorulme"]

    m.remember_regime("unnatural-lab", rejim, root=str(kok))
    ikinci = m.read_regimes("unnatural-lab", root=str(kok))
    assert list(ikinci) == [rejim["id"]]
    assert ikinci[rejim["id"]]["ilk_gorulme"] == damga, "ilk gorulme ezildi"

    m.remember_regime("unnatural-lab", None, root=str(kok))
    assert list(m.read_regimes("unnatural-lab", root=str(kok))) == [rejim["id"]]


# -------------------------------------------------------------- kusur: saf


def _series_parts(parts: dict) -> dict:
    return {"slug": "unnatural-lab", "parts": parts}


def test_yayinlanmis_ve_kuyruktaki_bolumler_kusur_sayilmaz(tmp_path):
    m = _modul()
    kok = _beyin_kok(tmp_path)
    _sahte_seri(tmp_path, os.path.join("sentinal_ihsan", "unnatural-lab"), _bible(),
                _series_parts({
                    "1": {"status": "published", "subtitle": "cikti"},
                    "2": {"status": "queued"},
                    "3": {"status": ""},
                }))
    assert m.held_episodes("unnatural-lab", root=str(kok)) == []


def test_tutulan_bolum_gerekcesiyle_dondurulur(tmp_path):
    m = _modul()
    kok = _beyin_kok(tmp_path)
    _sahte_seri(tmp_path, os.path.join("sentinal_ihsan", "unnatural-lab"), _bible(),
                _series_parts({
                    "4": {"status": "published"},
                    "5": {
                        "status": "qc_retry",
                        "last_reason_code": "EPISODE_DEGRADED",
                        "hold_reason": "bolum butunlugu yayin kapisinda reddedildi",
                        "retry_count": 2,
                        "subtitle": "Yarim Bolum",
                        "coherence": {"arc_roles_missing": ["loop_seam"],
                                      "narration_delivered": False,
                                      "duration_s": 11.1},
                    },
                }))
    tutulan = m.held_episodes("unnatural-lab", root=str(kok))
    assert len(tutulan) == 1
    kayit = tutulan[0]
    assert kayit["part"] == "5"
    assert kayit["durum"] == "qc_retry"
    assert kayit["kod"] == "EPISODE_DEGRADED"
    assert kayit["deneme"] == 2
    assert kayit["dusen_roller"] == ["loop_seam"]
    assert kayit["anlatim"] is False
    assert kayit["sure"] == 11.1


def test_kusur_defteri_tekrar_etmez_ve_kendini_toparlayani_saklar(tmp_path):
    """En onemli davranis: hata duzelse bile IZ kalir."""
    m = _modul()
    kok = _beyin_kok(tmp_path)
    rel = os.path.join("sentinal_ihsan", "unnatural-lab")
    tutuklu = _series_parts({
        "33": {"status": "qc_retry", "last_reason_code": "AUDIO_MASTER",
               "hold_reason": "mastering basarisiz", "retry_count": 1},
    })
    _sahte_seri(tmp_path, rel, _bible(), tutuklu)

    toplam, yeni = m.record_faults("unnatural-lab", root=str(kok))
    assert (toplam, yeni) == (1, 1)

    toplam, yeni = m.record_faults("unnatural-lab", root=str(kok))
    assert (toplam, yeni) == (1, 0), "ayni olay ikinci kez eklendi"

    # Bolum kendini toparladi: series.json artik onu published gosteriyor.
    _sahte_seri(tmp_path, rel, _bible(),
                _series_parts({"33": {"status": "published"}}))
    assert m.held_episodes("unnatural-lab", root=str(kok)) == []
    toplam, yeni = m.record_faults("unnatural-lab", root=str(kok))
    assert toplam == 1, "toparlanan hata kusur defterinden silindi"
    kayitlar = m.read_faults("unnatural-lab", root=str(kok))
    assert kayitlar[0]["kod"] == "AUDIO_MASTER"


def test_kaynak_yoksa_kusur_kaydi_dosya_yaratmaz(tmp_path):
    m = _modul()
    kok = _beyin_kok(tmp_path)
    assert m.record_faults("unnatural-lab", root=str(kok)) is None
    assert not (kok / "kanallar" / "unnatural-lab" / "kusur.jsonl").exists()


# ------------------------------------------------------------ beyin ciktisi


def _kayitlar(n: int, rejim=None) -> list:
    satirlar = []
    for i in range(n):
        satir = {
            "video_id": "vid%03d" % i,
            "kanal": "unnatural-lab",
            "tarih": "2026-09-%02d" % ((i % 28) + 1),
            "baslik": "Baslik %d" % i,
            "olcum": {"sure": 15.0 + i, "lufs": -14.0 - (i % 4),
                      "kesme_per_10sn": 1.0 + (i % 3) * 0.5,
                      "en_uzun_plan": 5.0 + (i % 4)},
            "kelime": 30 + i,
            "wpm": 80 + i,
            "sonuc": {"izlenme": 100 + i * 90, "begeni": 3, "gecmis": []},
            "olculdu_ts": "2026-09-10T12:00:00Z",
        }
        if rejim is not None:
            satir["rejim"] = rejim
        satirlar.append(satir)
    return satirlar


def _calistir(kok: Path, kanal: str, komut: str = "beyin"):
    shutil.copy2(BEYIN_PY, kok / "beyin.py")
    for komsu in BEYIN_PY.parent.glob("*.py"):
        if komsu.name != "beyin.py" and not komsu.name.startswith("test_"):
            try:
                shutil.copy2(komsu, kok / komsu.name)
            except OSError:
                pass
    ortam = dict(os.environ)
    ortam["PYTHONDONTWRITEBYTECODE"] = "1"
    for anahtar in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        ortam[anahtar] = "http://127.0.0.1:9"
    return subprocess.run([sys.executable, "beyin.py", komut, kanal],
                          cwd=str(kok), env=ortam, capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          timeout=ZAMAN_ASIMI)


def _defter_yaz(kok: Path, kanal: str, satirlar: list) -> None:
    klasor = kok / "kanallar" / kanal
    klasor.mkdir(parents=True, exist_ok=True)
    with open(klasor / "defter.jsonl", "w", encoding="utf-8") as fh:
        for satir in satirlar:
            fh.write(json.dumps(satir, ensure_ascii=False) + "\n")


def _beyin_metni(kok: Path, kanal: str) -> str:
    return (kok / "kanallar" / kanal / "BEYIN.md").read_text(encoding="utf-8")


def test_damgasiz_defter_havuzlanir_ama_takibin_yeni_oldugu_soylenir(tmp_path):
    kok = _beyin_kok(tmp_path)
    _sahte_seri(tmp_path, os.path.join("sentinal_ihsan", "unnatural-lab"),
                _bible(master_lufs=-14), _series_parts({}))
    _defter_yaz(kok, "unnatural-lab", _kayitlar(16))
    sonuc = _calistir(kok, "unnatural-lab")
    assert sonuc.returncode == 0, sonuc.stderr
    metin = _beyin_metni(kok, "unnatural-lab")
    assert "Teslim rejimi" in metin
    assert "Rejim takibi bugun basladi" in metin
    assert "YETERSIZ VERI" not in metin, "damgasiz defter beyni kor etti"


def test_karma_orneklem_yuksek_sesle_uyarir(tmp_path):
    """Damga VAR ama guncel rejimde az kayit varsa: havuzla, ama SOYLE."""
    kok = _beyin_kok(tmp_path)
    _sahte_seri(tmp_path, os.path.join("sentinal_ihsan", "unnatural-lab"),
                _bible(master_lufs=-14), _series_parts({}))
    m = _modul()
    guncel = m.delivery_regime("unnatural-lab", root=str(kok))["id"]
    satirlar = _kayitlar(14, rejim="eskirejim") + _kayitlar(2, rejim=guncel)
    for i, satir in enumerate(satirlar):
        satir["video_id"] = "v%03d" % i
    _defter_yaz(kok, "unnatural-lab", satirlar)

    sonuc = _calistir(kok, "unnatural-lab")
    assert sonuc.returncode == 0, sonuc.stderr
    metin = _beyin_metni(kok, "unnatural-lab")
    assert "DIKKAT: karma orneklem" in metin
    assert "Onceki rejime gore degisenler" in metin or "dagilim" in metin


def test_guncel_rejim_yeterliyse_yalniz_o_kullanilir(tmp_path):
    kok = _beyin_kok(tmp_path)
    _sahte_seri(tmp_path, os.path.join("sentinal_ihsan", "unnatural-lab"),
                _bible(master_lufs=-14), _series_parts({}))
    m = _modul()
    guncel = m.delivery_regime("unnatural-lab", root=str(kok))["id"]
    satirlar = _kayitlar(16, rejim=guncel) + _kayitlar(4, rejim="eskirejim")
    for i, satir in enumerate(satirlar):
        satir["video_id"] = "v%03d" % i
    _defter_yaz(kok, "unnatural-lab", satirlar)

    sonuc = _calistir(kok, "unnatural-lab")
    assert sonuc.returncode == 0, sonuc.stderr
    metin = _beyin_metni(kok, "unnatural-lab")
    assert "YALNIZ guncel rejimin 16 kaydiyla" in metin


def test_tutulan_bolumler_beyinde_gorunur(tmp_path):
    kok = _beyin_kok(tmp_path)
    _sahte_seri(tmp_path, os.path.join("sentinal_ihsan", "unnatural-lab"), _bible(),
                _series_parts({
                    "9": {"status": "needs_human", "last_reason_code": "CONTENT_REJECT",
                          "hold_reason": "icerik reddedildi", "retry_count": 3},
                }))
    _defter_yaz(kok, "unnatural-lab", _kayitlar(16))
    sonuc = _calistir(kok, "unnatural-lab")
    assert sonuc.returncode == 0, sonuc.stderr
    metin = _beyin_metni(kok, "unnatural-lab")
    assert "Yayinlanmayanlar" in metin
    assert "YAYINLANMADI" in metin
    assert "CONTENT_REJECT" in metin
    assert (kok / "kanallar" / "unnatural-lab" / "kusur.jsonl").exists()


def test_kaynak_okunamayinca_beyin_hata_yok_demez(tmp_path):
    """En sinsi hata: sessizlik 'temiz' diye okunur."""
    kok = _beyin_kok(tmp_path)
    _defter_yaz(kok, "aimagine-fear", _kayitlar(16))
    sonuc = _calistir(kok, "aimagine-fear")
    assert sonuc.returncode == 0, sonuc.stderr
    metin = _beyin_metni(kok, "aimagine-fear")
    assert "GORUNTULENEMIYOR" in metin
    assert "hata yok" in metin.lower()

def test_uretilmeyen_bolum_uretildi_diye_sunulmaz(tmp_path):
    """budget_exhausted/skipped/rejected bolumler ucretli ise HIC baslamadi.
    Bunlari "uretildi ama yayinlanmadi" diye sunmak BEYIN.md'yi yalanci yapar."""
    m = _modul()
    kok = _beyin_kok(tmp_path)
    _sahte_seri(tmp_path, os.path.join("sentinal_ihsan", "unnatural-lab"), _bible(),
                _series_parts({
                    "5": {"status": "budget_exhausted",
                          "last_reason_code": "BUDGET_EXHAUSTED"},
                    "6": {"status": "skipped"},
                    "7": {"status": "rejected"},
                    "8": {"status": "qc_retry", "last_reason_code": "EPISODE_DEGRADED",
                          "retry_count": 1},
                }))
    tutulan = {h["part"]: h["uretildi"] for h in m.held_episodes("unnatural-lab",
                                                                root=str(kok))}
    assert tutulan == {"5": False, "6": False, "7": False, "8": True}


def test_beyin_uretilen_ve_uretilmeyeni_ayri_sayar(tmp_path):
    kok = _beyin_kok(tmp_path)
    _sahte_seri(tmp_path, os.path.join("sentinal_ihsan", "unnatural-lab"), _bible(),
                _series_parts({
                    "5": {"status": "budget_exhausted",
                          "last_reason_code": "BUDGET_EXHAUSTED"},
                    "8": {"status": "needs_human", "last_reason_code": "CONTENT_REJECT",
                          "retry_count": 3},
                }))
    _defter_yaz(kok, "unnatural-lab", _kayitlar(16))
    sonuc = _calistir(kok, "unnatural-lab")
    assert sonuc.returncode == 0, sonuc.stderr
    metin = _beyin_metni(kok, "unnatural-lab")
    assert "2 bolum YAYINLANMADI" in metin
    assert "1 tanesi URETILDI" in metin
    assert "1 tanesi HIC URETILMEDI" in metin
    assert "uretildi ama YAYINLANMADI" not in metin

# ------------------------------------------------- rejim: URETIM ANI (dogru olan)


def _yayin_kur(tmp_path, parts: dict, published: list):
    rel = os.path.join("sentinal_ihsan", "unnatural-lab")
    klasor = _sahte_seri(tmp_path, rel, _bible(), _series_parts(parts))
    (klasor / "published.json").write_text(json.dumps(published, ensure_ascii=False),
                                           encoding="utf-8")
    return _beyin_kok(tmp_path)


def test_rejim_olcum_aninda_degil_uretim_aninda_okunur(tmp_path):
    """24 saat kapisi yuzunden olcum HEP bir gun sonra yapilir. O sirada ayarlar
    degismis olabilir; dunku videoyu bugunku ayarla damgalamak yanlistir.
    Motor zaten her bolume stack_sha256 yaziyor, dogru kaynak odur."""
    m = _modul()
    kok = _yayin_kur(
        tmp_path,
        parts={
            "31": {"status": "published", "stack_sha256": "6d8fa04a" + "0" * 56},
            "33": {"status": "published", "stack_sha256": "c623ea0f" + "0" * 56},
        },
        published=[
            {"part": 31, "results": {"youtube": "ESKIVIDEO"}},
            {"part": 33, "results": {"youtube": "YENIVIDEO"}},
        ],
    )
    assert m.part_regime("unnatural-lab", 31, root=str(kok)) == "6d8fa04a"
    assert m.part_regime("unnatural-lab", 33, root=str(kok)) == "c623ea0f"
    assert m.published_regime("unnatural-lab", "ESKIVIDEO", root=str(kok)) == "6d8fa04a"
    assert m.published_regime("unnatural-lab", "YENIVIDEO", root=str(kok)) == "c623ea0f"
    assert m.published_regime("unnatural-lab", "YOKBOYLE", root=str(kok)) is None


def test_guncel_rejim_en_son_YAYINLANAN_bolumden_gelir(tmp_path):
    """Tutulan bir bolum rejimi belirlemez: o video kimseye ulasmadi."""
    m = _modul()
    kok = _yayin_kur(
        tmp_path,
        parts={
            "33": {"status": "published", "stack_sha256": "c623ea0f" + "0" * 56},
            "34": {"status": "qc_retry", "stack_sha256": "deadbeef" + "0" * 56},
        },
        published=[{"part": 33, "results": {"youtube": "YENIVIDEO"}}],
    )
    assert m.latest_regime("unnatural-lab", root=str(kok)) == "c623ea0f"


def test_motor_damgasi_yoksa_yapilandirmaya_dusulur(tmp_path):
    m = _modul()
    kok = _yayin_kur(tmp_path, parts={"1": {"status": "published"}}, published=[])
    assert m.latest_regime("unnatural-lab", root=str(kok)) is None
    assert m.delivery_regime("unnatural-lab", root=str(kok)) is not None
