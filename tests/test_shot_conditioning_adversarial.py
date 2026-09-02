"""ROCK 4b düşman testleri , Visionary incelemesi.

Bu rock `series/produce.py`'ye ağır dokunuyor ve o motoru ON İKİ hat çağırıyor.
En büyük risk yeni özelliğin bozuk olması DEĞİL, kapalıyken diğer 11 hattı
bozmasıdır. Testlerin ağırlığı oraya veriliyor. Ayrıca üç kusurun her birinin
GERÇEKTEN kapandığı, eski kodda düşecek iddialarla sınanıyor.
"""
from __future__ import annotations

import json
import pathlib
import re

import pytest

from series.bible import Bible

REPO = pathlib.Path(__file__).resolve().parents[1]


def _bible(**series):
    base = {"slug": "t", "title": "t", "engine": "omni"}
    base.update(series)
    return Bible({"series": base, "characters": [], "environments": [], "props": []})


# --- 1. FILO GUVENLIGI: zincir KAPALIYKEN hicbir sey degismemeli -----------

def test_eleven_other_lines_are_untouched_chain_off_is_the_default():
    """Sentinal disindaki her seri chain_frames'siz calisiyor; oyle kalmali."""
    others = []
    for p in sorted(REPO.glob("*/*/bible.json")):
        if "unnatural-lab" in str(p).replace("\\", "/"):
            continue
        s = json.loads(p.read_text(encoding="utf-8")).get("series", {})
        others.append((p.name, s.get("chain_frames"), s.get("allow_cross_episode_chaining")))
    for name, cf, opt in others:
        assert opt is None, f"{name}: capraz-bolum opt-in bu rock'ta EKLENMEMELIYDI"
    # en az birkac seri gercekten var ki test anlamli olsun
    assert len(others) >= 5


def test_unnatural_lab_got_scope_but_NOT_chaining():
    """4b kosullandirmayi ACMAZ , acma karari 4a pilotunun isi."""
    s = json.loads((REPO / "sentinal_ihsan" / "unnatural-lab" / "bible.json")
                   .read_text(encoding="utf-8"))["series"]
    assert s.get("chain_scope") == "episode", "chain_scope episode olarak yazilmamis"
    assert s.get("chain_frames") in (False, None), \
        "chain_frames ACILMIS , bu rock onu acmamaliydi (4a pilotunun isi)"
    assert s.get("allow_cross_episode_chaining") is not True


def test_chain_off_bible_needs_no_new_fields():
    """Zincir kapaliyken yeni alanlarin YOKLUGU hicbir hata uretmemeli."""
    b = _bible()  # hicbir zincir alani yok , eski seri gibi
    assert b.chain_frames in (False, None)
    # scope okunabilmeli ve eski varsayilani korumali
    assert b.chain_scope in ("series", "episode")


# --- 2. KUSUR 1: chain_scope tuzagi ---------------------------------------

def test_cross_episode_requires_explicit_third_flag_not_just_scope():
    """`chain_scope: series` TEK BASINA onay sayilmamali , tuzak tam buydu.

    Alan zaten "series"e dusuyor; onu riza kabul etmek, yazmayi unutan her
    seriyi sessizce bolumler arasi zincire sokardi.
    """
    unsafe = _bible(chain_frames=True, chain_scope="series")
    consent = _bible(chain_frames=True, chain_scope="series",
                     allow_cross_episode_chaining=True)
    assert unsafe.allow_cross_episode_chaining is False,         "scope tek basina onay sayildi , tuzak duruyor"
    assert consent.allow_cross_episode_chaining is True


@pytest.mark.parametrize("bad", [None, False, "true", "True", "series", 1, 0, [], {}])
def test_opt_in_only_accepts_a_real_json_true(bad):
    """String "true" ya da 1 gibi degerler onay SAYILMAMALI (fail-closed).

    JSON'a elle "true" yazmak cok kolay bir hata; `is True` kontrolu bunu eler.
    """
    b = _bible(chain_frames=True, chain_scope="series",
               allow_cross_episode_chaining=bad)
    assert b.allow_cross_episode_chaining is False, f"{bad!r} yanlislikla onay sayildi"


def test_unsafe_config_fails_closed_with_an_actionable_message():
    """chain_frames=True + scope=series + opt-in YOK -> uretim REDDEDILMELI.

    Metin taramasi degil, gercek fonksiyonun davranisi.
    """
    from series.produce import chain_configuration_error
    unsafe = _bible(chain_frames=True, chain_scope="series")
    err = chain_configuration_error(unsafe)
    assert err, "guvensiz yapilandirma kabul edildi , bolumler arasi kare tasinir"
    assert "allow_cross_episode_chaining=true" in err,         "hata mesaji operatore cozumu soylemiyor"
    # bilincli kullanim serbest
    assert chain_configuration_error(
        _bible(chain_frames=True, chain_scope="series",
               allow_cross_episode_chaining=True)) is None
    # episode kapsami ve zincir kapali hallerinde engel YOK
    assert chain_configuration_error(_bible(chain_frames=True, chain_scope="episode")) is None
    assert chain_configuration_error(_bible()) is None


def test_episode_scope_never_reads_previous_episode_frame():
    """Kusur 1'in ASIL zarari: bolum 27, bolum 26'nin son karesinden baslamasin."""
    from series import series_runner

    class _M:
        data = {"last_frame_url": "https://ornek/onceki-bolum-son-kare.png"}

    # episode kapsami -> ASLA okunmaz
    assert series_runner._episode_chain_start(
        _bible(chain_frames=True, chain_scope="episode"), _M()) is None
    # series kapsami ama opt-in YOK -> yine okunmaz (fail-closed)
    assert series_runner._episode_chain_start(
        _bible(chain_frames=True, chain_scope="series"), _M()) is None
    # zincir kapali -> okunmaz
    assert series_runner._episode_chain_start(_bible(), _M()) is None
    # yalniz acik izinle okunur
    assert series_runner._episode_chain_start(
        _bible(chain_frames=True, chain_scope="series",
               allow_cross_episode_chaining=True), _M()) == _M.data["last_frame_url"]


def test_supplied_sidecar_is_ignored_for_episode_scoped_series():
    """Disaridan sidecar URL'i gelse bile bolum kapsaminda YOK SAYILMALI."""
    from series.produce import _initial_chain_url
    url = "https://ornek/bayat.png"
    assert _initial_chain_url(_bible(chain_frames=True, chain_scope="episode"), url) is None
    assert _initial_chain_url(_bible(), url) is None
    assert _initial_chain_url(
        _bible(chain_frames=True, chain_scope="series"), url) == url


# --- 3. KUSUR 2: baglama sirasi -------------------------------------------

def test_binding_labels_are_derived_from_the_final_ordered_list():
    """Eski kod `resolve_shot` SONRASI zincir karesini basa ekliyordu; etiketler
    kayiyordu. Duzeltmeden sonra prompt'taki numaralar listeyle AYNI kaynaktan
    turemeli , yani produce.py'de 'once resolve, sonra prepend' kalibi KALMAMALI.
    """
    src = (REPO / "series" / "produce.py").read_text(encoding="utf-8")
    assert not re.search(r'kwargs\["image_urls"\]\s*=\s*\[chain_url\]\s*\+', src), \
        "resolve_shot sonrasi prepend hala duruyor , etiketler kayar"


def test_shots_module_asserts_url_label_correspondence():
    """Karsiligin bir daha kaymamasi icin shots.py'de acik bir dogrulama olmali."""
    src = (REPO / "series" / "shots.py").read_text(encoding="utf-8")
    assert "image_urls" in src
    has_check = any(k in src for k in ("assert", "raise ValueError", "uyusmuyor",
                                       "correspond", "karsilik", "eslesmiyor"))
    assert has_check, "URL/etiket karsiligi icin dogrulama yok"


# --- 4. KUSUR 3: bayat kare tasinmasi -------------------------------------

def test_no_else_less_chain_url_assignment_survives():
    """Eski kalip: `if up: chain_url = up` , else YOK, onceki kare KALIRDI.

    Duzeltmeden sonra kabul edilen bir cekimin kare/yukleme basarisizliginda
    zincir referansi ya sifirlanmali ya fail etmeli; sessizce eski karede
    kalmamali. Kodda cikplak atama kalmamis olmali.
    """
    src = (REPO / "series" / "produce.py").read_text(encoding="utf-8")
    bare = re.findall(r'\n\s+if up:\n\s+chain_url = up\n(?!\s*else)', src)
    assert not bare, (
        f"{len(bare)} adet else'siz `if up: chain_url = up` kalmis , "
        "kabul edilen cekimde yukleme patlarsa BAYAT kare tasinir"
    )


def test_stale_frame_reset_is_logged_not_silent():
    """Sessiz geri dusme bu hatanin en kotu yani idi; log satiri sart."""
    src = (REPO / "series" / "produce.py").read_text(encoding="utf-8")
    idx = [m.start() for m in re.finditer(r"chain_url", src)]
    assert idx, "chain_url hic gecmiyor?"
    window = src[max(0, idx[0] - 2000): idx[-1] + 2000]
    assert any(k in window for k in ("logger.warning", "logger.info", "logger.error")), \
        "zincir referansi yollarinda hicbir log yok , sessiz geri dusme riski"
