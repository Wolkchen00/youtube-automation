"""Instagram caption'inin GERCEKTEN inen alana yazildigini dogrular.

Neden bu test var: `instagram_title` parametresi c06c4dc'den beri
gonderiliyordu ve Upload-Post onu kabul edip yanitinda `post_title` olarak
geri veriyordu, yani her sey calisiyor gorunuyordu. Ama Instagram'a inen
metin `title` idi. 22 Eylul 2026'da reel Ddj2SZ9jPWj'nin og:description'i
olculdu: "Golden Gate Bridge, into the fog #shorts", yani gonderilen BASLIK.
Caption'in govdesi ve alti etiketinin hicbiri gonderide yoktu.

Bu test payload'i denetler. Payload dogru diye caption'in indigini KANITLAMAZ;
onu ancak canli gonderi soyler. Kapinin isi, duzeltmenin sessizce geri
alinmasini onlemek.
"""
from pathlib import Path
from unittest import mock

import pytest

from core import uploader


CAPTION = (
    "You're dropping through the fog off the Golden Gate Bridge.\n\n"
    "#MegaSlideFear #GoldenGateBridge #WaterSlide #POVReels #CGIAdventure #ViralReels"
)
BASLIK = "Golden Gate Bridge, into the fog #shorts"


def _gonderilen_data(tmp_path, platform, social_caption):
    """Payload'i yakalar. Mukerrer-baslik kapisi AGA cikar, o yuzden mock'lanir."""
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
         mock.patch.object(uploader, "channel_recent_titles", lambda u: set()),          mock.patch.object(uploader.requests, "post", _post):
        uploader.upload_to_platform(
            video_path=video, title=BASLIK, description=CAPTION,
            user="Youtube", platform=platform, social_caption=social_caption,
        )
    return yakalanan


def test_instagram_caption_inen_alana_da_yazilir(tmp_path):
    data = _gonderilen_data(tmp_path, "instagram", CAPTION)
    assert data["instagram_title"] == CAPTION
    # ASIL KAPI: Instagram'a inen alan `title`. Buraya baslik yazilirsa
    # caption ve etiketler gonderiye HIC ulasmaz.
    assert data["title"] == CAPTION, (
        "Instagram'a inen alan `title`. Caption oraya yazilmazsa "
        "gonderide YouTube basligi gorunur ve etiketler kaybolur."
    )
    assert BASLIK not in data["title"]


def test_caption_yoksa_eski_davranis_korunur(tmp_path):
    data = _gonderilen_data(tmp_path, "instagram", "")
    assert data["title"] == BASLIK
    assert "instagram_title" not in data


def test_youtube_basligi_bozulmaz(tmp_path):
    data = _gonderilen_data(tmp_path, "youtube", CAPTION)
    assert data["title"] == BASLIK[:uploader.TITLE_LIMIT]
    assert "instagram_title" not in data
