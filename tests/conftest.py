"""Test altyapisi: testler git'te izlenen series_data/ agacina YAZMAZ.

RF-PLAN-WILD-ENCOUNTER ROCK 1. Olculdu: tam takim kosusu izlenen
series_data/advers/hold_log.jsonl dosyasina 8 satir ekliyordu. Sebep:
`series.bible.data_dir(slug)`, kurulu olmayan bir slug icin eski series_data/
kokune duser; `series_data/advers/` dizini (yalniz o izlenen defter yuzunden)
var oldugu icin test_hold_recovery_adversarial'in sentetik "advers" serisi
`_append_hold_log` ile gercek deftere yaziyordu.
"""

import pytest


@pytest.fixture(autouse=True)
def _eski_series_data_kokunu_izole_et(tmp_path_factory, monkeypatch):
    """Eski series_data/ kokunde SERI OLMAYAN dizinleri ve yeni-slug dususunu tmp'ye cevir.

    - Seri OLMAYAN dizinler (series.json tasimayan, or. `advers`) icin arama
      listesinde gercek kokten ONCE bos bir golge dizin durur; `data_dir` onu
      bulur ve yazilar tmp'ye gider.
    - `SERIES_DATA_DIR` (hic bulunamayan slug'in dusus yolu) tmp'yi gosterir.
    - Gercek series.json tasiyan seriler etkilenmez: `data_dir` onlari ilk
      turda bulur ve `all_series_dirs()` uretimdeki listeyi aynen verir.
    Kendi kokunu yamalayan testler bunu kendi kapsamlarinda ezer.
    """
    from series import bible as bible_module

    real = bible_module.SERIES_DATA_DIR
    shadow = tmp_path_factory.mktemp("series_data")
    if real.is_dir():
        for entry in real.iterdir():
            if entry.is_dir() and not (entry / "series.json").exists():
                (shadow / entry.name).mkdir()
    roots = []
    for root in bible_module._SEARCH_ROOTS:
        if root == real:
            roots.append(shadow)
        roots.append(root)
    monkeypatch.setattr(bible_module, "_SEARCH_ROOTS", roots)
    monkeypatch.setattr(bible_module, "SERIES_DATA_DIR", shadow)
