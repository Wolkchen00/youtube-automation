from pathlib import Path
from unittest import mock

import pytest

from core import uploader


STILL_HOME_CAPTION = (
    "Cairo rebuilt itself around a magnetic transit spine.\n\n"
    "Would you live in this future?\n\n"
    "#Cairo #MagneticTransit #FutureCity #Giza #SmartInfrastructure "
    "#Egypt #Cairo2050 #UrbanDesign #SustainableCity #FutureTransport "
    "#Architecture #SmartCity #CityOfTomorrow #StillHome"
)


def test_14_etiketli_still_home_ilk_5_etiketi_sirasiyla_tutar():
    assert uploader.cap_instagram_hashtags(STILL_HOME_CAPTION) == (
        "Cairo rebuilt itself around a magnetic transit spine.\n\n"
        "Would you live in this future?\n\n"
        "#Cairo #MagneticTransit #FutureCity #Giza #SmartInfrastructure"
    )


def test_tam_5_etiket_bayt_bayt_degismez():
    caption = "Body.\n\n#one #two #three #four #five  \n"
    assert uploader.cap_instagram_hashtags(caption) == caption


def test_etiketsiz_metin_bayt_bayt_degismez():
    caption = "Body with  two spaces.\n\nQuestion?  \n"
    assert uploader.cap_instagram_hashtags(caption) == caption


def test_mukerrer_etiket_ilkini_tutar_ve_bir_kez_sayar():
    caption = "#one #two #one #three #four #five #six #two"
    assert uploader.cap_instagram_hashtags(caption) == "#one #two #three #four #five"


def test_unicode_etiketler_sayilir_ve_korunur():
    caption = "#İstanbul #東京 #üç #四 #beş #altı"
    assert uploader.cap_instagram_hashtags(caption) == "#İstanbul #東京 #üç #四 #beş"


def test_url_parcasi_ve_yalniz_diyez_etiket_degil_inline_etiketler_sayilir():
    caption = (
        "See https://example.com/page#section and a lone #.\n"
        "Inline #one, #two, #three, #four, #five and #six."
    )
    assert uploader.cap_instagram_hashtags(caption) == (
        "See https://example.com/page#section and a lone #.\n"
        "Inline #one, #two, #three, #four, #five and."
    )


def test_silinen_etiket_satirlari_ve_artakalan_bosluklar_temizlenir():
    caption = (
        "Body line one.\nBody line two.\n\nQuestion?\n\n"
        "#one #two #three #four #five   \n"
        "#six #seven   \n"
    )
    assert uploader.cap_instagram_hashtags(caption) == (
        "Body line one.\nBody line two.\n\nQuestion?\n\n"
        "#one #two #three #four #five"
    )


def _gonderilen_data(tmp_path, platform, social_caption):
    video = tmp_path / "v.mp4"
    video.write_bytes(b"0")
    yakalanan = {}

    class _Yanit:
        status_code = 200
        content = b"{}"

        def json(self):
            return {"success": True, "results": {platform: {"success": True}}}

    def _post(url, headers=None, data=None, files=None, timeout=None):
        yakalanan.update(data or {})
        return _Yanit()

    with mock.patch.object(uploader, "UPLOAD_POST_API_KEY", "x"), \
         mock.patch.object(uploader, "_delivery_copy", lambda p: Path(p)), \
         mock.patch.object(uploader, "channel_recent_titles", lambda u: set()), \
         mock.patch.object(uploader.requests, "post", _post):
        uploader.upload_to_platform(
            video_path=video,
            title="Original title #shorts",
            description="YouTube description #one #two #three #four #five #six",
            user="Youtube",
            platform=platform,
            social_caption=social_caption,
        )
    return yakalanan


def test_instagram_iki_caption_alanina_da_5_etiketli_metin_yazar(tmp_path):
    data = _gonderilen_data(tmp_path, "instagram", STILL_HOME_CAPTION)
    expected = uploader.cap_instagram_hashtags(STILL_HOME_CAPTION)
    assert data["instagram_title"] == expected
    assert data["title"] == expected


def test_6_etiketli_caption_instagrama_ilk_5_etiketle_gider(tmp_path):
    caption = "Body.\n\n#one #two #three #four #five #six"
    data = _gonderilen_data(tmp_path, "instagram", caption)
    expected = "Body.\n\n#one #two #three #four #five"
    assert data["instagram_title"] == expected
    assert data["title"] == expected


@pytest.mark.parametrize("platform", ["youtube", "tiktok"])
def test_diger_platformlarin_metni_degismez(tmp_path, platform):
    data = _gonderilen_data(tmp_path, platform, STILL_HOME_CAPTION)
    assert data["title"] == "Original title #shorts"
    if platform == "youtube":
        assert data["description"] == "YouTube description #one #two #three #four #five #six"
        assert "instagram_title" not in data
    else:
        assert data["tiktok_title"] == STILL_HOME_CAPTION
        assert "instagram_title" not in data
