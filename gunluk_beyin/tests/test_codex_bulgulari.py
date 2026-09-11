"""Regression guards for the defects Codex found on 2026-09-11.

Each test names the finding it locks down. They are gathered in one file on
purpose: if a later refactor reopens one of these holes, the failure message
should say which reviewed defect came back, not just which assertion broke.

The theme across all of them is the same and it is the reason they matter:
this code runs unattended. Every one of these failures produced a GREEN run
with wrong or missing data.
"""
import json
import os
import re
import subprocess
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT))


def run(cwd, *args):
    return subprocess.run(
        [sys.executable, "-X", "utf8", str(ROOT / "beyin.py"), *args],
        cwd=str(cwd), capture_output=True, text=True, encoding="utf-8",
        errors="replace")


def ledger_row(i, channel="flashpoints"):
    return {
        "video_id": "v%03d" % i, "kanal": channel,
        "tarih": "2026-08-%02d" % (i + 1),
        "yayin_ts": "2026-08-%02dT10:00:00+00:00" % (i + 1),
        "baslik": "video %d" % i,
        "olcum": {"sure": 15.0, "lufs": -14.0,
                  "kesme_per_10sn": 2.0, "en_uzun_plan": 3.0},
        "sonuc": {"izlenme": 100, "gecmis": []},
    }


def seed(cwd, channel, rows):
    folder = cwd / "kanallar" / channel
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "defter.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
        encoding="utf-8")
    return folder


# ─── Finding 2: every measurement failing still exited 0 ─────────────────────

def install_measure_fakes(monkeypatch, feed, measure):
    fake_uploads = types.ModuleType("uploads")
    fake_uploads.list_uploads = lambda cid, limit: (feed, None, "api")
    fake_olc = types.ModuleType("olc")
    fake_olc.tek = measure
    monkeypatch.setitem(sys.modules, "uploads", fake_uploads)
    monkeypatch.setitem(sys.modules, "olc", fake_olc)


def feed_row(i, ts="2026-08-01T10:00:00+00:00"):
    return {"video_id": "new%02d" % i, "baslik": "yeni %d" % i,
            "tarih": ts[:10], "yayin_ts": ts, "rss_izlenme": None}


def test_all_measurements_failing_stops_hard(monkeypatch, tmp_path):
    """BULGU 2. yt-dlp/ffmpeg tamamen coktugunde her video `continue` ile
    geciliyordu ve komut exit 0 verip 'defter: N kayit' basiyordu."""
    import beyin
    monkeypatch.chdir(tmp_path)
    seed(tmp_path, "flashpoints", [ledger_row(i) for i in range(3)])

    def hep_patla(url, workdir, flag):
        raise RuntimeError("ffmpeg yok")

    install_measure_fakes(monkeypatch, [feed_row(i) for i in range(4)], hep_patla)
    with pytest.raises(SystemExit) as exc:
        beyin.cmd_measure("flashpoints", limit=10)
    assert "HICBIRI olculemedi" in str(exc.value)


def test_partial_measurement_failure_is_reported_but_proceeds(monkeypatch,
                                                              tmp_path, capsys):
    import beyin
    monkeypatch.chdir(tmp_path)
    seed(tmp_path, "flashpoints", [ledger_row(i) for i in range(3)])

    def bazen(url, workdir, flag):
        if url.endswith("new00"):
            return {"olcum": {"sure": 9.0}}
        return {"hata": "indirilemedi"}

    install_measure_fakes(monkeypatch, [feed_row(i) for i in range(3)], bazen)
    beyin.cmd_measure("flashpoints", limit=10)
    cikti = capsys.readouterr().out
    assert "2 video olculemedi" in cikti, "kismi kayip sessizce gecilmemeli"


def test_measure_failure_is_stamped_into_the_report(monkeypatch, tmp_path):
    """BULGU 1. Olcum dustugunde rapor yine BUGUNUN tarihiyle yazilip
    eksiksiz gorunuyordu; okuyan ajan yeni videolarin hic olculmedigini
    bilemiyordu."""
    import beyin
    monkeypatch.chdir(tmp_path)
    seed(tmp_path, "flashpoints", [ledger_row(i) for i in range(16)])

    fake_uploads = types.ModuleType("uploads")
    fake_uploads.list_uploads = lambda cid, limit: ([], "API: 403 | RSS: 404", None)
    fake_olc = types.ModuleType("olc")
    fake_olc.tek = lambda url, w, f: {"olcum": {"sure": 9.0}}
    monkeypatch.setitem(sys.modules, "uploads", fake_uploads)
    monkeypatch.setitem(sys.modules, "olc", fake_olc)
    with pytest.raises(SystemExit) as exc:
        beyin.cmd_measure("flashpoints", limit=10)
    assert "yukleme listesi okunamadi" in str(exc.value),         "test kurulumu yanlis: baska bir yerden cikti"

    proc = run(tmp_path, "beyin", "flashpoints")
    assert proc.returncode == 0, proc.stderr
    metin = (tmp_path / "kanallar" / "flashpoints" / "BEYIN.md").read_text(
        encoding="utf-8")
    assert "son olcum adimi BASARISIZ" in metin
    assert "403" in metin


def test_successful_measure_clears_the_stamp(monkeypatch, tmp_path):
    import beyin
    monkeypatch.chdir(tmp_path)
    seed(tmp_path, "flashpoints", [ledger_row(i) for i in range(3)])
    beyin.note_measure_failure("flashpoints", "eski hata")
    assert beyin.read_measure_failure("flashpoints")

    install_measure_fakes(monkeypatch, [feed_row(0)],
                          lambda url, w, f: {"olcum": {"sure": 9.0}})
    beyin.cmd_measure("flashpoints", limit=10)
    assert beyin.read_measure_failure("flashpoints") is None, \
        "olcum duzeldi ama rapor hala 'basarisiz' diyecek"


# ─── Finding 7: backlog beyond the window vanished silently ──────────────────

def test_saturated_window_warns(monkeypatch, tmp_path, capsys):
    """BULGU 7. Pencere `limit` ile kirpilip ONDAN SONRA 'defterde yok'
    suzgeci calisiyordu: birikim limitten buyukse en eskiler bir daha ASLA
    olculmezdi ve kosu yesil donerdi."""
    import beyin
    monkeypatch.chdir(tmp_path)
    seed(tmp_path, "flashpoints", [])
    feed = [feed_row(i) for i in range(5)]
    install_measure_fakes(monkeypatch, feed,
                          lambda url, w, f: {"olcum": {"sure": 9.0}})
    beyin.cmd_measure("flashpoints", limit=5)
    cikti = capsys.readouterr().out
    assert "EN ESKI videosu da defterde yok" in cikti
    assert "--limit 15" in cikti


def test_unsaturated_window_stays_quiet(monkeypatch, tmp_path, capsys):
    import beyin
    monkeypatch.chdir(tmp_path)
    seed(tmp_path, "flashpoints", [])
    feed = [feed_row(i) for i in range(3)]
    install_measure_fakes(monkeypatch, feed,
                          lambda url, w, f: {"olcum": {"sure": 9.0}})
    beyin.cmd_measure("flashpoints", limit=10)
    assert "EN ESKI" not in capsys.readouterr().out, "gereksiz alarm"


# ─── Finding 11: a typo silently suspended a channel that does not exist ─────

def test_suspending_an_unknown_channel_fails(tmp_path):
    proc = run(tmp_path, "askiya-al", "flashpoint", "--gun", "2")
    assert proc.returncode != 0
    assert "Bilinmeyen kanal" in (proc.stdout + proc.stderr)
    assert not (tmp_path / "kanallar" / "flashpoint").exists(), \
        "yazim hatasi bos bir kanal klasoru actı"


def test_suspending_an_adhoc_channel_with_a_ledger_works(tmp_path):
    seed(tmp_path, "deneme-kanali", [ledger_row(0, "deneme-kanali")])
    proc = run(tmp_path, "askiya-al", "deneme-kanali", "--gun", "1")
    assert proc.returncode == 0, proc.stderr


# ─── Finding 10: notice/state ordering and silent resume failure ─────────────

def test_notice_is_written_before_the_state_file(tmp_path, monkeypatch):
    """BULGU 10. Once durum yazilip sonra bildirim yazilsaydi ve bildirim
    yazilamasaydi, kanal ASKIYA ALINMIS ama eski uygulanabilir raporu yerinde
    kalmis olurdu , gunlerce sessizce eski konsepti satardi."""
    import beyin
    import askida
    monkeypatch.chdir(tmp_path)
    folder = seed(tmp_path, "flashpoints", [ledger_row(0)])
    (folder / "BEYIN.md").write_text("# gercek rapor\nhedef 15 sn\n",
                                     encoding="utf-8")

    def patla(channel, channel_dir, record):
        raise OSError("disk dolu")

    monkeypatch.setattr(askida, "install_notice", patla)
    with pytest.raises(OSError):
        beyin.cmd_suspend("flashpoints", days=2)
    assert not (folder / askida.STATE_FILE).exists(), \
        "bildirim yazilamadi ama kanal yine de askiya alindi"


def test_resume_reports_a_failed_state_removal(tmp_path, monkeypatch):
    import beyin
    import askida
    monkeypatch.chdir(tmp_path)
    seed(tmp_path, "flashpoints", [ledger_row(0)])
    beyin.cmd_suspend("flashpoints", days=2)
    monkeypatch.setattr(askida, "clear_state", lambda folder: False)
    with pytest.raises(SystemExit) as exc:
        beyin.cmd_resume("flashpoints")
    assert "SILINEMEDI" in str(exc.value)


# ─── Finding 4: two writers shared one temp filename ─────────────────────────

def test_ledger_temp_name_is_process_specific(tmp_path, monkeypatch):
    import beyin
    monkeypatch.chdir(tmp_path)
    gorulen = []
    gercek_open = open

    def izle(path, *a, **k):
        if str(path).endswith(tuple(".tmp.%d" % os.getpid() for _ in [0])) or \
                ".tmp" in str(path):
            gorulen.append(str(path))
        return gercek_open(path, *a, **k)

    monkeypatch.setattr("builtins.open", izle)
    beyin.write_ledger("flashpoints", [ledger_row(0)])
    assert gorulen, "gecici dosya hic kullanilmadi"
    assert str(os.getpid()) in gorulen[0], \
        "iki surec ayni .tmp adini paylasiyor: %s" % gorulen[0]


# ─── Finding 8: the Actions summary contradicted the report ──────────────────

SUMMARY = REPO / ".github" / "workflows" / "gunluk-beyin.yml"


def test_summary_asks_about_suspension_before_data(tmp_path):
    """BULGU 8. Ozet once 'YETERSIZ VERI' ariyordu. Aski bildiriminde o ifade
    GECMEZ, 'YON YOKTUR' gecer , yani askidaki kanal ozette 'kanala ozel
    kural VAR' diye gorunuyordu, gercegin tam tersi."""
    metin = SUMMARY.read_text(encoding="utf-8")
    i_aski = metin.find('grep -q "ASKIDA"')
    i_veri = metin.find('grep -q "YETERSIZ VERI"')
    assert i_aski != -1, "ozet askiyi hic sormuyor"
    assert i_aski < i_veri, "aski kontrolu YETERSIZ VERI'den SONRA geliyor"


def test_summary_counts_active_rows_not_raw_lines():
    metin = SUMMARY.read_text(encoding="utf-8")
    assert 'grep -vc \'"emekli"\'' in metin, \
        "ozet ham satir sayiyor, emekli kayitlar n'e karisiyor"


def test_summary_surfaces_measure_failure():
    metin = SUMMARY.read_text(encoding="utf-8")
    assert "olcum-hatasi.json" in metin


# ─── Finding 3: partial refresh went green whatever the cause ────────────────

def install_collect_fakes(monkeypatch, batch, batch_error=None, page=None):
    fake_uploads = types.ModuleType("uploads")
    fake_uploads.stats_for = lambda ids: (batch, batch_error)
    fake_kanal = types.ModuleType("kanal")
    fake_kanal.youtube_canli = lambda vid: (page or {}).get(vid, {})
    monkeypatch.setitem(sys.modules, "uploads", fake_uploads)
    monkeypatch.setitem(sys.modules, "kanal", fake_kanal)


def read_rows(cwd, channel="flashpoints"):
    path = cwd / "kanallar" / channel / "defter.jsonl"
    return [json.loads(l) for l in
            path.read_text(encoding="utf-8").splitlines() if l.strip()]


def test_api_answered_so_a_missing_video_is_information_not_failure(
        monkeypatch, tmp_path, capsys):
    """BULGU 3a. API CEVAP VERDIYSE ve bir video listede yoksa o video gercekten
    silinmis/ozel. Bu bir ariza degil; kosu hakli olarak yesil kalmali ve kayit
    her gun yeniden alarm uretmemeli."""
    import beyin
    monkeypatch.chdir(tmp_path)
    seed(tmp_path, "flashpoints", [ledger_row(i) for i in range(4)])
    install_collect_fakes(monkeypatch, {
        "v000": {"izlenme": 10}, "v001": {"izlenme": 20},
        "v002": {"izlenme": 30},
    })
    beyin.cmd_collect("flashpoints")
    cikti = capsys.readouterr().out
    assert "gorunmuyor" in cikti and "ariza DEGIL" in cikti
    kayitlar = {r["video_id"]: r for r in read_rows(tmp_path)}
    assert kayitlar["v003"].get("gorunmez"), "gorunmez kaydi isaretlenmedi"
    assert not kayitlar["v000"].get("gorunmez")


def test_a_returning_video_loses_its_invisible_mark(monkeypatch, tmp_path):
    import beyin
    monkeypatch.chdir(tmp_path)
    rows = [ledger_row(i) for i in range(2)]
    rows[1]["gorunmez"] = {"ts": "2026-09-01T00:00:00+00:00", "sebep": "eski"}
    seed(tmp_path, "flashpoints", rows)
    install_collect_fakes(monkeypatch, {"v000": {"izlenme": 1},
                                        "v001": {"izlenme": 2}})
    beyin.cmd_collect("flashpoints")
    kayitlar = {r["video_id"]: r for r in read_rows(tmp_path)}
    assert not kayitlar["v001"].get("gorunmez"), \
        "video geri geldi ama hala gorunmez isaretli"


def test_api_down_and_most_rows_unreadable_stops_hard(monkeypatch, tmp_path):
    """BULGU 3b. API DUSTUYSE sayfa kazimaya guveniyoruz. Orada cogu kayit
    okunamiyorsa kalan sayilar BAYAT ve rapor onlari guncel saniyor , eskiden
    1/60 tazelenmesi bile kosuyu yesil birakiyordu."""
    import beyin
    monkeypatch.chdir(tmp_path)
    seed(tmp_path, "flashpoints", [ledger_row(i) for i in range(6)])
    install_collect_fakes(monkeypatch, {}, batch_error="HTTP 403 quotaExceeded",
                          page={"v000": {"izlenme": 5}})
    with pytest.raises(SystemExit) as exc:
        beyin.cmd_collect("flashpoints")
    mesaj = str(exc.value)
    assert "BAYAT" in mesaj and "5" in mesaj


def test_api_down_but_scraping_mostly_works_stays_green(monkeypatch, tmp_path,
                                                        capsys):
    """Esik yarisi: bir iki kayit kacmasi gurultudur, kirmizi yapmamali."""
    import beyin
    monkeypatch.chdir(tmp_path)
    seed(tmp_path, "flashpoints", [ledger_row(i) for i in range(6)])
    sayfa = {"v%03d" % i: {"izlenme": 10 + i} for i in range(5)}
    install_collect_fakes(monkeypatch, {}, batch_error="HTTP 500", page=sayfa)
    beyin.cmd_collect("flashpoints")
    cikti = capsys.readouterr().out
    assert "API dustu" in cikti, "API'nin dustugu sessizce gecilmemeli"


def test_invisible_rows_are_not_confused_with_api_failure(monkeypatch,
                                                          tmp_path, capsys):
    """API dustuyse okunamayan kayit 'gorunmez' diye ISARETLENMEMELI:
    silinmis olduklarina dair bir kanit yok, sadece ulasamadik."""
    import beyin
    monkeypatch.chdir(tmp_path)
    seed(tmp_path, "flashpoints", [ledger_row(i) for i in range(4)])
    install_collect_fakes(monkeypatch, {}, batch_error="HTTP 500",
                          page={"v000": {"izlenme": 1}, "v001": {"izlenme": 2},
                                "v002": {"izlenme": 3}})
    beyin.cmd_collect("flashpoints")
    kayitlar = {r["video_id"]: r for r in read_rows(tmp_path)}
    assert not kayitlar["v003"].get("gorunmez"), \
        "ulasilamayan kayit 'silinmis' diye damgalandi"
