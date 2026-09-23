"""Kanalin kendi ilk yorumu (Upload-Post first_comment) ve caption sorusu.

Neden: videolar izleniyor ama yorumu baslatan yok. Her yayinda kanal kendi
adiyla bir soru yorumu atar ve caption etiketlerin ustunde bir soruyla biter.
Sabitleme API'si YOK (ne YouTube ne Instagram); bu kapi yalniz yorumun ve
sorunun payload'a dogru girdigini denetler. Yorumun gercekten dustugunu ancak
canli gonderi soyler.

Instagram'in 5 etiket tavani caption ile yorumlari BIRLIKTE sayar, bu yuzden
yorumda '#' varsa yorum hic gonderilmez.
"""
import json
from pathlib import Path
from unittest import mock

import pytest

from core import uploader
from series import engagement
from series.engagement import (
    insert_caption_question,
    pick_caption_question,
    pick_first_comment,
    valid_engagement_question,
)

KOK = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------- temizleyici
@pytest.mark.parametrize("girdi", ["", "   ", None, "\n\t"])
def test_bos_yorum_bos_doner(girdi):
    assert uploader.clean_first_comment(girdi) == ""


def test_etiketli_yorum_atlanir():
    assert uploader.clean_first_comment("Which city next? #travel") == ""


@pytest.mark.parametrize("link", ["see https://x.co ?", "go to www.site.com?", "HTTP://A.B?"])
def test_linkli_yorum_atlanir(link):
    assert uploader.clean_first_comment(link) == ""


def test_satir_sonlari_tek_bosluga_iner():
    assert uploader.clean_first_comment("Which one?\r\n\n  Tell us") == "Which one? Tell us"


def test_300_karakter_kelime_sinirinda_kesilir():
    metin = ("word " * 100).strip() + "?"
    temiz = uploader.clean_first_comment(metin)
    assert len(temiz) <= 300
    assert not temiz.endswith(" ")
    assert temiz.split(" ")[-1] == "word"


def test_bosluksuz_uzun_metin_300de_kesilir():
    assert len(uploader.clean_first_comment("a" * 400)) == 300


def test_emoji_ve_turkce_harf_korunur():
    metin = "Sence Zehra doğruyu mu söylüyor? 👇"
    assert uploader.clean_first_comment(metin) == metin


# ------------------------------------------------------------ payload kapisi
def _yukle(tmp_path, platform, first_comment="", yanit=None):
    video = tmp_path / "v.mp4"
    video.write_bytes(b"0")
    yakalanan = {}
    govde = yanit or {"success": True, "results": {platform: {"success": True}}}

    class _Yanit:
        status_code = 200
        content = b"{}"

        def json(self):
            return govde

    def _post(url, headers=None, data=None, files=None, timeout=None):
        yakalanan.update(data or {})
        return _Yanit()

    with mock.patch.object(uploader, "UPLOAD_POST_API_KEY", "x"), \
         mock.patch.object(uploader, "_delivery_copy", lambda p: Path(p)), \
         mock.patch.object(uploader, "channel_recent_titles", lambda u: set()), \
         mock.patch.object(uploader.requests, "post", _post):
        sonuc = uploader.upload_to_platform(
            video_path=video, title="Baslik", description="Aciklama",
            user="Youtube", platform=platform, social_caption="Caption",
            first_comment=first_comment,
        )
    return yakalanan, sonuc


@pytest.mark.parametrize("platform", ["youtube", "instagram", "tiktok"])
def test_ilk_yorum_her_platformda_gider(tmp_path, platform):
    data, _ = _yukle(tmp_path, platform, "Which city next? 🌍")
    assert data["first_comment"] == "Which city next? 🌍"


@pytest.mark.parametrize("platform", ["youtube", "instagram", "tiktok"])
def test_yorum_yoksa_alan_hic_gonderilmez(tmp_path, platform):
    data, _ = _yukle(tmp_path, platform, "")
    assert "first_comment" not in data


def test_etiketli_yorum_payloada_girmez(tmp_path):
    data, _ = _yukle(tmp_path, "instagram", "Which one? #fyp")
    assert "first_comment" not in data


def test_uyarilar_loglanir_sonuc_degismez(tmp_path):
    govde = {"success": True, "results": {"youtube": {"success": True}},
             "warnings": ["first_comment failed: comments disabled"]}
    with mock.patch.object(uploader.logger, "warning") as uyari:
        _, sonuc = _yukle(tmp_path, "youtube", "Which one?", yanit=govde)
    assert sonuc == govde
    assert any("comments disabled" in str(c) for c in uyari.call_args_list)


# ------------------------------------------------------------- secim kurali
SERI = {"engagement": {
    "first_comment_pool": ["One pool question?", "Two pool question?", "no question here"],
    "caption_question_pool": ["Caption question one?", "Caption question two?"],
}}


def test_plan_yorumu_havuzu_yener():
    assert pick_first_comment({"first_comment": " Plan question here? "}, SERI, 1) == "Plan question here?"


@pytest.mark.parametrize("kotu", ["", "no mark here", "Bad? #tag", "Link? http://a.b", 42, None, "Hi?"])
def test_gecersiz_plan_yorumu_havuza_duser(kotu):
    assert pick_first_comment({"first_comment": kotu}, SERI, 1) == "One pool question?"


def test_havuz_part_numarasiyla_doner():
    assert pick_first_comment({}, SERI, 2) == "Two pool question?"
    assert pick_first_comment({}, SERI, 4) == "One pool question?"
    assert pick_first_comment({}, SERI, 3001) == pick_first_comment({}, SERI, 1)


def test_havuzdaki_gecersiz_satir_bos_doner():
    assert pick_first_comment({}, SERI, 3) == ""


@pytest.mark.parametrize("cfg", [{}, {"engagement": {}}, {"engagement": {"first_comment_pool": []}},
                                 {"engagement": {"first_comment_pool": "tek metin?"}}, None])
def test_etkilesim_yoksa_bos(cfg):
    assert pick_first_comment({}, cfg, 1) == ""
    assert pick_caption_question(cfg, 1) == ""


def test_bozuk_part_numarasi_bos():
    assert pick_caption_question(SERI, "abc") == ""


# --------------------------------------------------------- caption sorusu
def test_sorulu_caption_bayt_bayt_ayni():
    cap = "Body with a question?\n\n#a #b"
    assert insert_caption_question(cap, "Extra question?") == cap


def test_soru_etiketlerin_ustune_girer():
    cap = "Body text.\n\n#a #b #c"
    assert insert_caption_question(cap, "Which one?") == "Body text.\n\nWhich one?\n\n#a #b #c"


def test_cok_satirli_etiket_blogu_bolunmez():
    cap = "Body text.\n\n#a #b\n#c #d"
    assert insert_caption_question(cap, "Which one?") == "Body text.\n\nWhich one?\n\n#a #b\n#c #d"


def test_etiket_sayisi_degismez():
    cap = "Body text.\n\n#a #b #c #d #e"
    yeni = insert_caption_question(cap, "Which one?")
    assert yeni.count("#") == cap.count("#")


def test_etiketsiz_caption_sona_soru_alir():
    assert insert_caption_question("Body.", "Which one?") == "Body.\n\nWhich one?"


def test_yalniz_etiket_satiri():
    assert insert_caption_question("#a #b", "Which one?") == "Which one?\n\n#a #b"


def test_ikinci_ekleme_etkisiz():
    bir = insert_caption_question("Body.\n\n#a", "Which one?")
    assert insert_caption_question(bir, "Another one?") == bir


def test_gecersiz_soru_eklenmez():
    assert insert_caption_question("Body.\n\n#a", "no mark") == "Body.\n\n#a"


# --------------------------------------------------- series_runner yayini
def _yayin(tmp_path, caption, soru, yorum="Pool question?"):
    from series import series_runner

    meta = mock.MagicMock()
    meta.title_for.return_value = "Title #shorts"
    meta.description_for.return_value = "Logline.\n\n#shorts #vfx"
    meta.hashtags = "#shorts #vfx"
    meta.upload_profile = "profil"
    meta.slug = "test-slug"
    meta.platforms = ["youtube", "instagram"]
    meta.data = {}
    video = tmp_path / "v.mp4"
    video.write_bytes(b"0")
    cagrilar = []

    def _up(src, title, desc, **kw):
        cagrilar.append({"title": title, "desc": desc, **kw})
        return {"success": True}

    with mock.patch.object(series_runner, "upload_to_platform", _up), \
         mock.patch("series.bible.episode_dir", lambda s, n: tmp_path / "yok"):
        try:
            series_runner._publish_part(meta, 3, video, "", caption=caption,
                                        first_comment=yorum, caption_question=soru)
        except Exception:
            pass  # yayin sonrasi kayit adimlari bu testin konusu degil
    return cagrilar


def test_captionsiz_plan_ig_icin_sorulu_caption_uretir(tmp_path):
    cagrilar = _yayin(tmp_path, "", "Would you volunteer?")
    assert cagrilar, "upload_to_platform hic cagrilmadi"
    for c in cagrilar:
        # Etiket EKLENMEZ: IG/TikTok eskiden yalniz basligi aliyordu.
        assert c["social_caption"] == "Title #shorts\n\nWould you volunteer?"
        assert c["social_caption"].count("#") == c["title"].count("#")
        assert "Would you volunteer?" in c["desc"]
        assert c["first_comment"] == "Pool question?"


def test_sorulu_caption_yayinda_degismez(tmp_path):
    cap = "Story body. What would you do?\n\n#a #b"
    cagrilar = _yayin(tmp_path, cap, "Would you volunteer?")
    assert cagrilar
    for c in cagrilar:
        assert c["social_caption"] == cap
        assert c["desc"] == cap


def test_soru_yoksa_eski_davranis(tmp_path):
    cagrilar = _yayin(tmp_path, "", "", yorum="")
    assert cagrilar
    for c in cagrilar:
        assert c["social_caption"] == ""
        assert c["first_comment"] == ""


# ------------------------------------------------------- ikmal (replenish)
def test_ikmal_istemi_ilk_yorumu_istiyor():
    kaynak = (KOK / "series" / "replenish.py").read_text(encoding="utf-8")
    assert '"first_comment"' in kaynak
    assert "valid_engagement_question" in kaynak


# ------------------------------------------------ canli seri havuzlari
SERILER = [
    "sentinal_ihsan/wild-encounter",
    "shadowedhistory/still-home",
    "galactic_experience/one-variable",
    "galactic_experience/flythrough",
]
YASAK = ("like and subscribe", "subscribe", "follow for", "real footage", "this is real")


@pytest.mark.parametrize("seri", SERILER)
def test_canli_seri_havuzu_gecerli(seri):
    cfg = json.loads((KOK / seri / "series.json").read_text(encoding="utf-8"))
    havuz = cfg["engagement"]["first_comment_pool"]
    assert len(havuz) >= 6
    for satir in havuz + cfg["engagement"].get("caption_question_pool", []):
        assert valid_engagement_question(satir), satir
        assert len(satir) <= 120, satir
        assert not any(y in satir.lower() for y in YASAK), satir
        assert uploader.clean_first_comment(satir) == satir, satir


def test_wild_encounter_caption_sorusu_var():
    cfg = json.loads((KOK / "sentinal_ihsan/wild-encounter/series.json").read_text(encoding="utf-8"))
    assert pick_caption_question(cfg, 15)


# ------------------------------------------ ikmal dogrulayicisi (gercek yol)
@pytest.mark.parametrize("case_name", ["plato_3x8", "tek_obje_4x6", "formatless_multishot"])
@pytest.mark.parametrize("yorum,kalir", [
    ("Which animal should the crew build next?", True),
    ("Bad one #fyp?", False),
    ("no question mark here", False),
    (12345, False),
    (None, False),
])
def test_ikmal_gecersiz_yorumu_duser_plani_korur(case_name, yorum, kalir):
    import copy
    from series import replenish
    from tests import test_rf_tekplan_golden as g

    meta, bible, cfg, episodes = g.CASES[case_name]()
    temel = copy.deepcopy(episodes)
    temel_hatalar = replenish._validate_batch(temel, bible, 8, 1, set(), cfg, history=[])

    denenen = copy.deepcopy(episodes)
    if yorum is not None:
        denenen[0]["first_comment"] = yorum
    hatalar = replenish._validate_batch(denenen, bible, 8, 1, set(), cfg, history=[])

    # Yorum ASLA yeni bir hata uretmez, plani dusurmez.
    assert hatalar == temel_hatalar
    assert ("first_comment" in denenen[0]) is kalir
    if kalir:
        assert denenen[0]["first_comment"] == yorum


# ------------------------------------------- taze goz bulgulari (23 Eyl 2026)
def test_soru_basliktaysa_iki_platform_da_soru_almaz(tmp_path):
    from series import series_runner

    meta = mock.MagicMock()
    meta.title_for.return_value = "Would you survive this?"
    meta.description_for.return_value = "Would you survive this?\n\nLogline.\n\n#shorts"
    meta.hashtags = "#shorts"
    meta.upload_profile = "p"
    meta.slug = "s"
    meta.platforms = ["youtube", "instagram"]
    video = tmp_path / "v.mp4"
    video.write_bytes(b"0")
    cagrilar = []

    def _up(src, title, desc, **kw):
        cagrilar.append({"desc": desc, **kw})
        return {"success": True}

    with mock.patch.object(series_runner, "upload_to_platform", _up), \
         mock.patch("series.bible.episode_dir", lambda s, n: tmp_path / "yok"):
        try:
            series_runner._publish_part(meta, 1, video, "", caption="",
                                        first_comment="", caption_question="Extra question?")
        except Exception:
            pass
    assert cagrilar
    for c in cagrilar:
        assert "Extra question?" not in c["desc"]
        assert c["social_caption"] == ""


@pytest.mark.parametrize("bozuk", [True, "evet", ["a?"], 5, None])
def test_bozuk_engagement_kosuyu_durdurmaz(bozuk):
    cfg = {"engagement": bozuk}
    assert pick_first_comment({"first_comment": "Plan question here?"}, cfg, 1) == ""
    assert pick_caption_question(cfg, 1) == ""
    assert engagement.engagement_block(cfg) == {}


def test_engagementsiz_seride_plan_yorumu_gonderilmez():
    assert pick_first_comment({"first_comment": "Plan question here?"}, {}, 1) == ""


def test_4xx_reddinde_video_yorumsuz_bir_kez_daha_gider(tmp_path):
    video = tmp_path / "v.mp4"
    video.write_bytes(b"0")
    gonderilen = []

    class _Yanit:
        def __init__(self, kod, govde):
            self.status_code, self._g = kod, govde
            self.content = b"{}"

        def json(self):
            return self._g

    def _post(url, headers=None, data=None, files=None, timeout=None):
        gonderilen.append(dict(data))
        if "first_comment" in data:
            return _Yanit(400, {"success": False, "error": "first_comment not allowed"})
        return _Yanit(200, {"success": True, "results": {"youtube": {"success": True}}})

    with mock.patch.object(uploader, "UPLOAD_POST_API_KEY", "x"), \
         mock.patch.object(uploader, "_delivery_copy", lambda p: Path(p)), \
         mock.patch.object(uploader, "channel_recent_titles", lambda u: set()), \
         mock.patch.object(uploader.requests, "post", _post):
        sonuc = uploader.upload_to_platform(
            video_path=video, title="B", description="A", user="u",
            platform="youtube", first_comment="Which one?",
        )
    assert sonuc and sonuc["success"] is True
    assert len(gonderilen) == 2
    assert "first_comment" in gonderilen[0] and "first_comment" not in gonderilen[1]


def test_yorumsuz_4xx_eskisi_gibi_tekrar_denenmez(tmp_path):
    video = tmp_path / "v.mp4"
    video.write_bytes(b"0")
    sayac = []

    class _Yanit:
        status_code = 400
        content = b"{}"

        def json(self):
            return {"success": False, "error": "bad"}

    def _post(url, headers=None, data=None, files=None, timeout=None):
        sayac.append(1)
        return _Yanit()

    with mock.patch.object(uploader, "UPLOAD_POST_API_KEY", "x"), \
         mock.patch.object(uploader, "_delivery_copy", lambda p: Path(p)), \
         mock.patch.object(uploader, "channel_recent_titles", lambda u: set()), \
         mock.patch.object(uploader.requests, "post", _post):
        assert uploader.upload_to_platform(
            video_path=video, title="B", description="A", user="u", platform="youtube",
        ) is None
    assert len(sayac) == 1
