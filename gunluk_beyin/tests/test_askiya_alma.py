"""Suspension guard: a parked channel must go QUIET, not just skip its run.

Ihsan, 2026-09-11: sentinal_ihsan's concept is being rewritten from scratch.
Its ledger holds 15 videos made under the old concept. Until new-format videos
exist and are past the 24h gate, any channel-specific direction derived from
that ledger describes a product that no longer exists.

The trap this file exists to prevent: "suspended" meaning only "the run is
skipped". The channel agent reads `kanallar/<channel>/BEYIN.md` every morning
and cannot tell that the brain stopped. A stale report keeps selling the old
concept's advice for as long as the suspension lasts, which is the exact
outcome the suspension was asked for to avoid.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import askida  # noqa: E402


def run(cwd, *args):
    return subprocess.run(
        [sys.executable, "-X", "utf8", str(ROOT / "beyin.py"), *args],
        cwd=str(cwd), capture_output=True, text=True, encoding="utf-8",
        errors="replace")


def seed_report(cwd, channel, text="# gercek rapor\n\nsure hedefi 15 sn\n"):
    folder = cwd / "kanallar" / channel
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "BEYIN.md").write_text(text, encoding="utf-8")
    return folder


def seed_ledger(cwd, channel, n=16):
    folder = cwd / "kanallar" / channel
    folder.mkdir(parents=True, exist_ok=True)
    rows = []
    for i in range(n):
        rows.append(json.dumps({
            "video_id": "v%03d" % i,
            "kanal": channel,
            "tarih": "2026-08-%02d" % (i + 1),
            "yayin_ts": "2026-08-%02dT10:00:00+00:00" % (i + 1),
            "baslik": "eski konsept %d" % i,
            "olcum": {"sure": 15.0 + i * 0.1, "lufs": -14.0,
                      "kesme_per_10sn": 2.0, "en_uzun_plan": 3.0},
            "sonuc": {"izlenme": 100 + i * 10, "gecmis": []},
        }, ensure_ascii=False))
    (folder / "defter.jsonl").write_text("\n".join(rows) + "\n", encoding="utf-8")
    return folder


# ─── the core promise: the report stops talking ──────────────────────────────

def test_suspending_replaces_the_report(tmp_path):
    seed_report(tmp_path, "unnatural-lab")
    proc = run(tmp_path, "askiya-al", "unnatural-lab", "--gun", "2",
               "--sebep", "konsept bastan yaziliyor")
    assert proc.returncode == 0, proc.stderr
    metin = (tmp_path / "kanallar" / "unnatural-lab" / "BEYIN.md").read_text(
        encoding="utf-8")
    assert "ASKIDA" in metin
    assert "sure hedefi 15 sn" not in metin, \
        "eski tavsiye hala BEYIN.md'de duruyor"
    assert "konsept bastan yaziliyor" in metin


def test_previous_report_is_kept_not_destroyed(tmp_path):
    seed_report(tmp_path, "unnatural-lab")
    run(tmp_path, "askiya-al", "unnatural-lab", "--gun", "2")
    eski = tmp_path / "kanallar" / "unnatural-lab" / askida.ARCHIVED_REPORT
    assert eski.is_file()
    assert "sure hedefi 15 sn" in eski.read_text(encoding="utf-8")


def test_suspending_twice_does_not_overwrite_the_archive(tmp_path):
    """Ikinci askiya alma, arsivi ASKI BILDIRIMIYLE ezmemeli."""
    seed_report(tmp_path, "unnatural-lab")
    run(tmp_path, "askiya-al", "unnatural-lab", "--gun", "2")
    run(tmp_path, "askiya-al", "unnatural-lab", "--gun", "5")
    eski = (tmp_path / "kanallar" / "unnatural-lab"
            / askida.ARCHIVED_REPORT).read_text(encoding="utf-8")
    assert "sure hedefi 15 sn" in eski, "tek gercek rapor kaybedildi"
    assert "ASKIDA" not in eski


def test_notice_says_nothing_actionable(tmp_path):
    """Bildirim, kanal ajaninin uygulayabilecegi bir HEDEF icermemeli."""
    seed_report(tmp_path, "unnatural-lab")
    run(tmp_path, "askiya-al", "unnatural-lab", "--gun", "2")
    metin = (tmp_path / "kanallar" / "unnatural-lab" / "BEYIN.md").read_text(
        encoding="utf-8")
    assert "YON YOKTUR" in metin
    for yasak in ("BUGUN ICIN YON", "hedef olarak", "LUFS hedefi"):
        assert yasak not in metin, "aski bildiriminde uygulanabilir hedef var: %s" % yasak


# ─── the three commands actually stop ────────────────────────────────────────

@pytest.mark.parametrize("komut", ["olc", "topla", "beyin"])
def test_every_command_stops_while_suspended(tmp_path, komut):
    seed_ledger(tmp_path, "unnatural-lab")
    seed_report(tmp_path, "unnatural-lab")
    run(tmp_path, "askiya-al", "unnatural-lab", "--gun", "2")
    bildirim = (tmp_path / "kanallar" / "unnatural-lab" / "BEYIN.md").read_text(
        encoding="utf-8")

    proc = run(tmp_path, komut, "unnatural-lab")
    assert proc.returncode == 0, "aski bir HATA degil, kosuyu kirmizi yapmamali"
    assert "ASKIDA" in proc.stdout, "sessizce atlandi, log yok"
    sonra = (tmp_path / "kanallar" / "unnatural-lab" / "BEYIN.md").read_text(
        encoding="utf-8")
    assert sonra == bildirim, "%s aski bildirimini ezdi" % komut


def test_other_channels_are_untouched(tmp_path):
    seed_ledger(tmp_path, "unnatural-lab")
    seed_ledger(tmp_path, "flashpoints")
    run(tmp_path, "askiya-al", "unnatural-lab", "--gun", "2")
    proc = run(tmp_path, "beyin", "flashpoints")
    assert proc.returncode == 0, proc.stderr
    assert "ASKIDA" not in proc.stdout
    assert (tmp_path / "kanallar" / "flashpoints" / "BEYIN.md").is_file()


# ─── expiry: it must let go on its own ───────────────────────────────────────

def write_state_raw(cwd, channel, until, reason="test"):
    folder = cwd / "kanallar" / channel
    folder.mkdir(parents=True, exist_ok=True)
    (folder / askida.STATE_FILE).write_text(json.dumps({
        "askiya_alindi": "2026-09-11T00:00:00+00:00",
        "kadar": until,
        "sebep": reason,
    }), encoding="utf-8")
    return folder


def test_expired_suspension_runs_again(tmp_path):
    seed_ledger(tmp_path, "unnatural-lab")
    dun = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    write_state_raw(tmp_path, "unnatural-lab", dun)
    proc = run(tmp_path, "beyin", "unnatural-lab")
    assert proc.returncode == 0, proc.stderr
    assert "suresi dolmus" in proc.stdout
    metin = (tmp_path / "kanallar" / "unnatural-lab" / "BEYIN.md").read_text(
        encoding="utf-8")
    assert "ASKIDA" not in metin, "suresi dolan aski hala rapor uretmiyor"


def test_open_ended_suspension_never_expires_on_its_own(tmp_path):
    seed_ledger(tmp_path, "unnatural-lab")
    write_state_raw(tmp_path, "unnatural-lab", None)
    proc = run(tmp_path, "beyin", "unnatural-lab")
    assert "ASKIDA" in proc.stdout
    assert "acik uclu" in proc.stdout


def test_resume_lifts_it(tmp_path):
    seed_ledger(tmp_path, "unnatural-lab")
    run(tmp_path, "askiya-al", "unnatural-lab", "--kadar", "acik")
    assert run(tmp_path, "beyin", "unnatural-lab").stdout.count("ASKIDA")
    proc = run(tmp_path, "devam", "unnatural-lab")
    assert proc.returncode == 0
    proc = run(tmp_path, "beyin", "unnatural-lab")
    assert "ASKIDA" not in proc.stdout
    metin = (tmp_path / "kanallar" / "unnatural-lab" / "BEYIN.md").read_text(
        encoding="utf-8")
    assert "ASKIDA" not in metin, "devam sonrasi rapor yeniden yazilmali"


def test_resume_on_a_channel_that_was_not_suspended_is_harmless(tmp_path):
    seed_ledger(tmp_path, "flashpoints")
    proc = run(tmp_path, "devam", "flashpoints")
    assert proc.returncode == 0
    assert "zaten askida degil" in proc.stdout


# ─── failing safe ────────────────────────────────────────────────────────────

def test_unreadable_state_file_does_not_park_the_channel(tmp_path):
    """Bozuk aski dosyasi kanali SESSIZCE durdurmamali.

    Sessizce duran bir kanal, durdugu fark edilmeyen kanaldir. Bozuk dosyanin
    dogru cevabi 'askida degil' , yanlis bir ekstra kosu, fark edilmeyen bir
    sessizlikten ucuzdur.
    """
    seed_ledger(tmp_path, "unnatural-lab")
    folder = tmp_path / "kanallar" / "unnatural-lab"
    (folder / askida.STATE_FILE).write_text("{bozuk json", encoding="utf-8")
    proc = run(tmp_path, "beyin", "unnatural-lab")
    assert proc.returncode == 0, proc.stderr
    assert "ASKIDA" not in proc.stdout


def test_unparseable_deadline_keeps_it_suspended(tmp_path):
    """Tarih okunamiyorsa aski SURER. Ters yon, kanali sessizce acardi."""
    seed_ledger(tmp_path, "unnatural-lab")
    write_state_raw(tmp_path, "unnatural-lab", "her zaman")
    proc = run(tmp_path, "beyin", "unnatural-lab")
    assert "ASKIDA" in proc.stdout


@pytest.mark.parametrize("kotu", ["2026-13-01", "yarin", "20-09-2026", ""])
def test_bad_date_is_rejected_loudly(tmp_path, kotu):
    proc = run(tmp_path, "askiya-al", "unnatural-lab", "--kadar", kotu)
    assert proc.returncode != 0 or "ValueError" in proc.stderr, \
        "gecersiz tarih sessizce kabul edildi: %r" % kotu


def test_suspension_rejects_path_traversal(tmp_path):
    proc = run(tmp_path, "askiya-al", "unnatural-lab/../pwned", "--gun", "1")
    assert proc.returncode != 0
    assert not (tmp_path / "kanallar" / "pwned").exists()
    assert not (tmp_path / "pwned").exists()


def test_zero_or_negative_days_rejected(tmp_path):
    for gun in ("0", "-3"):
        proc = run(tmp_path, "askiya-al", "unnatural-lab", "--gun", gun)
        assert proc.returncode != 0 or "ValueError" in proc.stderr, gun


# ─── date handling ───────────────────────────────────────────────────────────

def test_until_a_date_includes_that_whole_day(tmp_path):
    """'--kadar 2026-09-20' 20'sinde hala askida olmali, 21'inde degil."""
    iso = askida.parse_until("2026-09-20")
    bitis = datetime.fromisoformat(iso)
    assert bitis.date().isoformat() == "2026-09-20"
    assert bitis.hour == 23, "gun basinda bitirmek 20'sini kapsam disi birakir"


def test_open_ended_parses_to_none():
    assert askida.parse_until("acik") is None
    assert askida.parse_until("ACIK") is None
