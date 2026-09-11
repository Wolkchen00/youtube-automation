"""Retirement guard: old-concept rows leave the comparison but keep their seat.

When a channel's concept is replaced rather than tuned, its previous
measurements describe a product that no longer exists. Pooling them means the
brain derives "what works on this channel" from a dead format.

Two failure modes this file exists to prevent, in order of damage:

1. Retired rows still shaping the report. That is the whole point.
2. Retirement behaving like deletion. If `olc` stops recognising those video
   ids it will re-download and re-measure every one of them on the next run,
   and they walk straight back into the ledger as fresh active rows. The
   retirement would appear to work, then silently undo itself overnight.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def run(cwd, *args):
    return subprocess.run(
        [sys.executable, "-X", "utf8", str(ROOT / "beyin.py"), *args],
        cwd=str(cwd), capture_output=True, text=True, encoding="utf-8",
        errors="replace")


def row(i, channel="unnatural-lab", duration=15.0, views=100, retired=None):
    record = {
        "video_id": "v%03d" % i,
        "kanal": channel,
        "tarih": "2026-08-%02d" % (i + 1),
        "yayin_ts": "2026-08-%02dT10:00:00+00:00" % (i + 1),
        "baslik": "video %d" % i,
        "olcum": {"sure": duration, "lufs": -14.0,
                  "kesme_per_10sn": 2.0, "en_uzun_plan": 3.0},
        "sonuc": {"izlenme": views, "gecmis": []},
    }
    if retired:
        record["emekli"] = retired
    return record


def seed(cwd, channel, rows):
    folder = cwd / "kanallar" / channel
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "defter.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
        encoding="utf-8")
    return folder


def read_ledger(cwd, channel):
    path = cwd / "kanallar" / channel / "defter.jsonl"
    return [json.loads(line) for line in
            path.read_text(encoding="utf-8").splitlines() if line.strip()]


def report(cwd, channel):
    return (cwd / "kanallar" / channel / "BEYIN.md").read_text(encoding="utf-8")


# ─── the ledger keeps everything ─────────────────────────────────────────────

def test_retiring_keeps_every_row(tmp_path):
    seed(tmp_path, "unnatural-lab", [row(i) for i in range(16)])
    proc = run(tmp_path, "emekli", "unnatural-lab", "--sebep", "konsept degisti")
    assert proc.returncode == 0, proc.stderr
    rows = read_ledger(tmp_path, "unnatural-lab")
    assert len(rows) == 16, "emeklilik SILME degildir"
    assert all(r.get("emekli") for r in rows)
    assert rows[0]["emekli"]["sebep"] == "konsept degisti"
    assert rows[0]["emekli"]["ts"], "damga zamansiz olmamali"


def test_retiring_preserves_the_measurements(tmp_path):
    seed(tmp_path, "unnatural-lab", [row(i, duration=12.5 + i) for i in range(16)])
    run(tmp_path, "emekli", "unnatural-lab")
    rows = read_ledger(tmp_path, "unnatural-lab")
    assert rows[3]["olcum"]["sure"] == 15.5
    assert rows[3]["sonuc"]["izlenme"] == 100


# ─── the report stops reasoning from them ────────────────────────────────────

def test_report_makes_no_channel_claim_after_retirement(tmp_path):
    """16 kayit normalde kanala ozel kural uretmeye YETER. Emeklilikten sonra
    uretmemeli, yoksa emeklilik hicbir ise yaramamis olur."""
    seed(tmp_path, "unnatural-lab", [row(i, duration=10.0 + i, views=50 * i)
                                     for i in range(16)])
    run(tmp_path, "beyin", "unnatural-lab")
    once = report(tmp_path, "unnatural-lab")
    assert "YETERSIZ VERI" not in once, "test kurulumu yanlis: 16 kayit yetmeliydi"

    run(tmp_path, "emekli", "unnatural-lab", "--sebep", "konsept bastan yazildi")
    run(tmp_path, "beyin", "unnatural-lab")
    sonra = report(tmp_path, "unnatural-lab")
    assert "YETERSIZ VERI" in sonra
    assert "EMEKLI" in sonra
    assert "konsept bastan yazildi" in sonra


def test_report_counts_only_active_rows(tmp_path):
    rows = [row(i, retired={"ts": "2026-09-11T00:00:00+00:00", "sebep": "eski"})
            for i in range(15)]
    rows += [row(100 + i) for i in range(2)]
    seed(tmp_path, "unnatural-lab", rows)
    run(tmp_path, "beyin", "unnatural-lab")
    metin = report(tmp_path, "unnatural-lab")
    assert "Olculen video: **2**" in metin, \
        "emekli kayitlar 'olculen video' sayisina karismamali"
    assert "15 kayit EMEKLI" in metin


def test_all_retired_says_so_instead_of_empty_ledger(tmp_path):
    """'Defter bos' yaniltici olurdu: defter dolu, sadece hepsi emekli."""
    seed(tmp_path, "unnatural-lab",
         [row(i, retired={"ts": "2026-09-11T00:00:00+00:00", "sebep": "eski"})
          for i in range(15)])
    run(tmp_path, "beyin", "unnatural-lab")
    metin = report(tmp_path, "unnatural-lab")
    assert "hepsi emekli" in metin
    assert "Defter bos. Once" not in metin


# ─── retirement must not turn into re-measurement ────────────────────────────

def test_measure_still_treats_retired_videos_as_known(tmp_path, monkeypatch):
    """EN ONEMLI VAKA. `olc` emekli video id'lerini bilinen saymazsa hepsini
    yeniden indirip olcer ve aktif kayit olarak geri koyar , emeklilik bir
    gecede kendini bozar."""
    sys.path.insert(0, str(ROOT))
    import beyin

    monkeypatch.chdir(tmp_path)
    rows = [row(i, retired={"ts": "2026-09-11T00:00:00+00:00", "sebep": "eski"})
            for i in range(15)]
    seed(tmp_path, "unnatural-lab", rows)

    import types
    feed = [{"video_id": "v%03d" % i, "baslik": "video %d" % i,
             "tarih": "2026-08-%02d" % (i + 1),
             "yayin_ts": "2026-08-%02dT10:00:00+00:00" % (i + 1),
             "rss_izlenme": None} for i in range(15)]
    fake_uploads = types.ModuleType("uploads")
    fake_uploads.list_uploads = lambda cid, limit: (feed, None, "api")
    olculenler = []
    fake_olc = types.ModuleType("olc")

    def _tek(url, workdir, flag):
        olculenler.append(url)
        return {"olcum": {"sure": 9.9}}

    fake_olc.tek = _tek
    monkeypatch.setitem(sys.modules, "uploads", fake_uploads)
    monkeypatch.setitem(sys.modules, "olc", fake_olc)

    beyin.cmd_measure("unnatural-lab", limit=15)
    assert olculenler == [], \
        "emekli videolar yeniden olculdu: %s" % olculenler[:3]
    assert len(read_ledger(tmp_path, "unnatural-lab")) == 15, \
        "defter sisti, emekli kayitlar mukerrer eklendi"


# ─── idempotence and edges ───────────────────────────────────────────────────

def test_retiring_twice_is_harmless(tmp_path):
    seed(tmp_path, "unnatural-lab", [row(i) for i in range(3)])
    run(tmp_path, "emekli", "unnatural-lab", "--sebep", "birinci")
    ilk = read_ledger(tmp_path, "unnatural-lab")[0]["emekli"]["ts"]
    proc = run(tmp_path, "emekli", "unnatural-lab", "--sebep", "ikinci")
    assert proc.returncode == 0
    assert "aktif kayit yok" in proc.stdout
    sonra = read_ledger(tmp_path, "unnatural-lab")[0]["emekli"]
    assert sonra["ts"] == ilk and sonra["sebep"] == "birinci", \
        "ikinci cagri ilk emeklilik damgasini ezdi"


def test_only_new_rows_retire_on_a_second_pass(tmp_path):
    rows = [row(i, retired={"ts": "2026-09-01T00:00:00+00:00", "sebep": "eski"})
            for i in range(3)]
    rows += [row(50 + i) for i in range(2)]
    seed(tmp_path, "unnatural-lab", rows)
    proc = run(tmp_path, "emekli", "unnatural-lab", "--sebep", "yeni")
    assert "2 kayit EMEKLIYE AYRILDI" in proc.stdout
    son = read_ledger(tmp_path, "unnatural-lab")
    assert son[0]["emekli"]["sebep"] == "eski", "onceki damga korunmali"
    assert son[-1]["emekli"]["sebep"] == "yeni"


def test_missing_ledger_fails_loudly(tmp_path):
    proc = run(tmp_path, "emekli", "flashpoints")
    assert proc.returncode != 0
    assert "Defter yok" in (proc.stdout + proc.stderr)


def test_retire_rejects_path_traversal(tmp_path):
    proc = run(tmp_path, "emekli", "unnatural-lab/../pwned")
    assert proc.returncode != 0
    assert not (tmp_path / "pwned").exists()


def test_retire_works_while_suspended(tmp_path):
    """Aski tam olarak bu gecis icin konuluyor; emeklilik ona takilmamali."""
    seed(tmp_path, "unnatural-lab", [row(i) for i in range(4)])
    run(tmp_path, "askiya-al", "unnatural-lab", "--kadar", "acik")
    proc = run(tmp_path, "emekli", "unnatural-lab", "--sebep", "gecis")
    assert proc.returncode == 0, proc.stderr
    assert "EMEKLIYE AYRILDI" in proc.stdout
    assert all(r.get("emekli") for r in read_ledger(tmp_path, "unnatural-lab"))


def test_other_channels_untouched(tmp_path):
    seed(tmp_path, "unnatural-lab", [row(i) for i in range(3)])
    seed(tmp_path, "flashpoints", [row(i, channel="flashpoints") for i in range(3)])
    run(tmp_path, "emekli", "unnatural-lab")
    assert not any(r.get("emekli")
                   for r in read_ledger(tmp_path, "flashpoints"))


# ─── selective retirement: a removed FORMAT, not the whole channel ───────────

def test_only_named_videos_are_retired(tmp_path):
    """Olculdu 2026-09-11: aimagine-fear defterinde 9 video 15,1 sn ve 6 video
    ~56 sn , ayni YouTube kanalina basan IKI AYRI URUN (Fear kaydiragi ve
    durdurulmus Next Stop). Beyin ikisini havuzlayip 'sure' bulgusunu bu format
    ayrimindan uyduruyordu."""
    rows = [row(i) for i in range(4)]
    seed(tmp_path, "unnatural-lab", rows)
    proc = run(tmp_path, "emekli", "unnatural-lab",
               "--video", "v001,v003", "--sebep", "eski format")
    assert proc.returncode == 0, proc.stderr
    assert "2 kayit EMEKLIYE AYRILDI" in proc.stdout
    kayitlar = {r["video_id"]: r for r in read_ledger(tmp_path, "unnatural-lab")}
    assert kayitlar["v001"].get("emekli") and kayitlar["v003"].get("emekli")
    assert not kayitlar["v000"].get("emekli")
    assert not kayitlar["v002"].get("emekli")


def test_unknown_video_id_fails_loudly(tmp_path):
    """Yazim hatasi SESSIZCE hicbir seyi emekliye ayirmamali , kullanici
    formati kaldirdigini sanip devam ederdi."""
    seed(tmp_path, "unnatural-lab", [row(i) for i in range(3)])
    proc = run(tmp_path, "emekli", "unnatural-lab", "--video", "v001,YOKBOYLE")
    assert proc.returncode != 0
    assert "YOKBOYLE" in (proc.stdout + proc.stderr)
    assert not any(r.get("emekli")
                   for r in read_ledger(tmp_path, "unnatural-lab")), \
        "hatali listede kismen emekliye ayirdi"


def test_selective_retirement_leaves_the_rest_comparable(tmp_path):
    """Geri kalan kayitlar 15'i buluyorsa kanal kurali URETMEYE DEVAM etmeli:
    emeklilik, kanali susturmak degil, karisimi ayirmak icin."""
    rows = [row(i, duration=15.0) for i in range(16)]
    rows += [row(100 + i, duration=56.0) for i in range(4)]
    seed(tmp_path, "unnatural-lab", rows)
    run(tmp_path, "emekli", "unnatural-lab",
        "--video", ",".join("v%03d" % (100 + i) for i in range(4)))
    run(tmp_path, "beyin", "unnatural-lab")
    metin = report(tmp_path, "unnatural-lab")
    assert "4 kayit EMEKLI" in metin
    assert "YETERSIZ VERI" not in metin, "16 aktif kayit kaldi, kural uretmeliydi"


def test_video_list_tolerates_spaces(tmp_path):
    seed(tmp_path, "unnatural-lab", [row(i) for i in range(3)])
    proc = run(tmp_path, "emekli", "unnatural-lab", "--video", " v000 , v002 ")
    assert proc.returncode == 0, proc.stderr
    kayitlar = {r["video_id"]: r for r in read_ledger(tmp_path, "unnatural-lab")}
    assert kayitlar["v000"].get("emekli") and kayitlar["v002"].get("emekli")
    assert not kayitlar["v001"].get("emekli")
