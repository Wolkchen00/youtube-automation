"""Arsivlenmis serilerin DONDURULMUS kopyalari (RF-PLAN-WILD-ENCOUNTER, ROCK 1).

2026-09-10 arsivlemesi sentinal_ihsan altindaki eski serileri ve kanalin
KONSEPT.md dosyasini canli agactan kaldirdi. BELIRLI bir arsiv serisini
sabitleyen testler (unnatural-lab config/plan/doktrin, sentinal_ihsan/KONSEPT.md,
arsiv serilerinin golden prompt'lari) veriyi artik buradan okur:

    tests/fixtures/archived/<orijinal goreli yol>

Her dosya `git show 4c3f392:<orijinal goreli yol>` ciktisiyla bayt-bayt aynidir
(4c3f392 = arsivden hemen onceki agac). Yalniz testlerin gercekten okudugu
dosyalar kopyalanmistir.

Kurallar:
  - Fixture'lar DONDURULMUSTUR. Hicbir test bu dizine yazmaz; veriyi degistiren
    bir test once gecici bir kopya alir (copy_archived_series).
  - FILO testleri (kurulu TUM serileri tarayip bir degismezi denetleyenler) bu
    modulu KULLANMAZ. Onlar canli serileri taramaya devam eder; fixture'a
    cevirmek canli filodaki gelecekteki bir bozulmayi gizlerdi.
"""

from __future__ import annotations

import pathlib
import shutil
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
ARCHIVED_ROOT = REPO_ROOT / "tests" / "fixtures" / "archived"
SOURCE_COMMIT = "4c3f392"
ARCHIVED_CHANNEL = "sentinal_ihsan"


def archived_path(relative: str) -> pathlib.Path:
    """Orijinal goreli yolun (or. 'sentinal_ihsan/KONSEPT.md') dondurulmus kopyasi."""
    return ARCHIVED_ROOT / relative


def archived_search_roots(channel_root: pathlib.Path | None = None):
    """Seri arama koklerinin BASINA dondurulmus kanal kokunu koyan patch.

    Mevcut enjeksiyon noktasi kullanilir: `series.bible._SEARCH_ROOTS`
    (test_doctrine_gate, test_fixedframe, test_calibrate ayni noktayi yamalar).
    Boylece `Bible.load`, `SeriesMeta.load`, `data_dir` ve `doctrine_path`
    arsiv slug'larini dondurulmus kopyaya cozer. Canli seriler canli kalir,
    cunku fixture kokunde yalniz arsiv serileri vardir. Liste cagri aninda
    kurulur; `with`, `.start()` / `.stop()` ile kullanilir.
    """
    from series import bible as bible_module

    root = channel_root if channel_root is not None else ARCHIVED_ROOT / ARCHIVED_CHANNEL
    return mock.patch.object(
        bible_module, "_SEARCH_ROOTS", [root, *bible_module._SEARCH_ROOTS]
    )


def copy_archived_series(destination: pathlib.Path, slug: str) -> pathlib.Path:
    """Arsiv serisini ve kanal KONSEPT.md'sini gecici bir kanal kokune kopyala.

    Veriyi degistiren testler icindir; dondurulmus fixture'a yazilmaz. Donen
    kanal koku `archived_search_roots(channel_root=...)` ile kullanilir.
    """
    source_channel = ARCHIVED_ROOT / ARCHIVED_CHANNEL
    channel_root = pathlib.Path(destination) / ARCHIVED_CHANNEL
    shutil.copytree(source_channel / slug, channel_root / slug)
    shutil.copyfile(source_channel / "KONSEPT.md", channel_root / "KONSEPT.md")
    return channel_root
