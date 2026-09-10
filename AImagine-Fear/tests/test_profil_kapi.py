from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

import build
import profil
from tools import gunluk


def _probe(width=1080, height=1920, fps="24/1", audio=True, duration="15.0"):
    streams = [
        {
            "codec_type": "video",
            "width": width,
            "height": height,
            "r_frame_rate": fps,
        }
    ]
    if audio:
        streams.append({"codec_type": "audio", "r_frame_rate": "0/0"})
    return {"streams": streams, "format": {"duration": duration}}


def _tamam(stdout=""):
    return subprocess.CompletedProcess([], 0, stdout=stdout, stderr="")


def _approval(profile_name="1080p", master_sha="abc"):
    p = profil.PROFILLER[profile_name]
    return {
        "model": gunluk.MODEL,
        "sure": 15,
        "cozunurluk": p["cozunurluk"],
        "fps": p["beklenen_fps"],
        "master_sha": master_sha,
        "profil_hash": gunluk.profil_hash(),
    }


def test_profil_tek_kaynak_prompt_api_ve_kapi(tmp_path: Path) -> None:
    command = gunluk.uretim_komutu("slug", 15, profil.PROFILLER["1080p"])
    assert command == [
        gunluk.PY,
        "tools/kie_uret.py",
        "slug",
        "--model",
        gunluk.MODEL,
        "--n-frames",
        "15",
        "--resolution",
        "1080p",
        "--tag",
        "gunluk",
        "--max-wait",
        "1500",
    ]
    canon = build.load_canon(Path(build.__file__).resolve().parent)
    route = build.load_route(
        Path(build.__file__).resolve().parent / "routes" / "dubai-burj-altin.md",
        Path(build.__file__).resolve().parent,
    )
    prompt = build.render_route(canon, route, "1080p")["PROMPT.txt"]
    assert "1080x1920, 24 frames per second" in prompt
    assert gunluk.denetle_akislar(_probe(), 3_000_000, 15, profil.PROFILLER["1080p"]) == []


def test_720p_profile_turns_prompt_api_and_gate_together() -> None:
    command = gunluk.uretim_komutu("slug", 15, profil.PROFILLER["720p"])
    assert command[command.index("--resolution") + 1] == "720p"
    root = Path(build.__file__).resolve().parent
    canon = build.load_canon(root)
    route = build.load_route(root / "routes" / "dubai-burj-altin.md", root)
    prompt = build.render_route(canon, route, "720p")["PROMPT.txt"]
    assert "720x1280, 24 frames per second" in prompt
    assert gunluk.denetle_akislar(
        _probe(720, 1280), 3_000_000, 15, profil.PROFILLER["720p"]
    ) == []
    errors = gunluk.denetle_akislar(
        _probe(720, 1920), 3_000_000, 15, profil.PROFILLER["720p"]
    )
    assert any("beklenen 720x1280" in error for error in errors)


def test_ffprobe_video_stream_wins_over_audio_zero_rate() -> None:
    assert gunluk.denetle_akislar(
        _probe(), 3_000_000, 15, profil.PROFILLER["1080p"]
    ) == []
    errors = gunluk.denetle_akislar(
        _probe(fps="30/1"), 3_000_000, 15, profil.PROFILLER["1080p"]
    )
    assert errors == ["fps 30.000, beklenen ~24"]


def test_fractional_24000_1001_passes_and_missing_audio_fails() -> None:
    assert gunluk.denetle_akislar(
        _probe(fps="24000/1001"), 3_000_000, 15, profil.PROFILLER["1080p"]
    ) == []
    errors = gunluk.denetle_akislar(
        _probe(audio=False), 3_000_000, 15, profil.PROFILLER["1080p"]
    )
    assert errors == ["ses akisi YOK"]


def test_silent_resolution_drop_has_specific_message() -> None:
    errors = gunluk.denetle_akislar(
        _probe(720, 1280), 3_000_000, 15, profil.PROFILLER["1080p"]
    )
    assert errors == ["istendi 1080p, geldi 720x1280 - model sessizce dusurdu"]


def test_canon_contains_profile_tokens_not_stale_literals() -> None:
    text = (Path(build.__file__).resolve().parent / "canon" / "MASTER-BLOCK.md").read_text(
        encoding="utf-8"
    )
    assert "<<COZUNURLUK>>" in text
    assert "<<FPS>>" in text
    assert "1080x1920" not in text
    assert "30 frames" not in text


def test_profile_hash_normalizes_line_endings(tmp_path: Path) -> None:
    lf = tmp_path / "lf.py"
    crlf = tmp_path / "crlf.py"
    changed = tmp_path / "changed.py"
    lf.write_bytes(b"a = 1\nb = 2\n")
    crlf.write_bytes(b"a = 1\r\nb = 2\r\n")
    changed.write_bytes(b"a = 1\nb = 3\n")
    assert profil.profil_hash(lf) == profil.profil_hash(crlf)
    assert profil.profil_hash(lf) != profil.profil_hash(changed)


def test_matrix_key_includes_canonical_fps() -> None:
    key24 = profil.matris_anahtari(gunluk.MODEL, 15, "720p", 24)
    key30 = profil.matris_anahtari(gunluk.MODEL, 15, "720p", 30)
    assert profil.YETENEK_MATRISI[key24] == "dogrulandi"
    assert profil.YETENEK_MATRISI[key30] == "kanarya"
    assert key24 != key30


def test_canary_publish_stops_before_credit_or_subprocess(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(gunluk, "ONAY_DOSYASI", tmp_path / "missing.json")
    monkeypatch.setattr(gunluk, "defter", lambda: [])
    monkeypatch.setattr(gunluk, "kredi", lambda: (_ for _ in ()).throw(AssertionError("credit")))
    monkeypatch.setattr(gunluk, "kosa", lambda *a: (_ for _ in ()).throw(AssertionError("process")))
    assert gunluk.main([]) == 1


def test_bad_approval_cases_stay_closed(monkeypatch, tmp_path: Path) -> None:
    approval_path = tmp_path / "profil_onay.json"
    monkeypatch.setattr(gunluk, "ONAY_DOSYASI", approval_path)
    cases = [
        "{",
        json.dumps({**_approval(), "cozunurluk": "720p"}),
        json.dumps({**_approval(), "profil_hash": "old"}),
    ]
    for body in cases:
        approval_path.write_text(body, encoding="utf-8")
        allowed, _ = gunluk.yayin_izni("1080p", 15)
        assert not allowed


def test_valid_persistent_approval_opens_canary(monkeypatch, tmp_path: Path) -> None:
    approval_path = tmp_path / "profil_onay.json"
    approval_path.write_text(json.dumps(_approval()), encoding="utf-8")
    monkeypatch.setattr(gunluk, "ONAY_DOSYASI", approval_path)
    assert gunluk.yayin_izni("1080p", 15) == (True, "dogrulandi (kalici onay)")


def test_dry_is_before_same_day_and_never_reads_credit(monkeypatch, capsys) -> None:
    today = datetime.now(gunluk.LA).strftime("%Y-%m-%d")
    monkeypatch.setattr(gunluk, "defter", lambda: [{"slug": "x", "ts": today}])
    monkeypatch.setattr(gunluk, "kredi", lambda: (_ for _ in ()).throw(AssertionError("credit")))
    monkeypatch.setattr(gunluk, "kosa", lambda *a: (_ for _ in ()).throw(AssertionError("process")))
    assert gunluk.main(["--dry"]) == 0
    output = capsys.readouterr().out
    assert "sirdaki slug" in output
    assert "sure         : 15" in output
    assert "profil       : 1080p" in output
    assert "matris       : kanarya" in output


def test_yayinlama_runs_generation_without_publish_and_checks_contact(
    monkeypatch, tmp_path: Path
) -> None:
    slug = "test-slug"
    raw = tmp_path / "out" / slug / "video" / "test_gunluk_1.mp4"
    raw.parent.mkdir(parents=True)
    raw.write_bytes(b"raw")
    caption = tmp_path / "out" / slug / "CAPTION.txt"
    caption.write_text("Title\ncaption #MegaSlideFear #TestTower", encoding="utf-8")
    (tmp_path / "out" / slug / "TITLE.txt").write_text(
        "Test Tower glass drop #shorts\nI slid off the Test Tower #shorts",
        encoding="utf-8",
    )
    events = []

    monkeypatch.setattr(gunluk, "KOK", tmp_path)
    monkeypatch.setattr(gunluk, "DEFTER", tmp_path / "yayin.jsonl")
    monkeypatch.setattr(gunluk, "defter", lambda: [])
    monkeypatch.setattr(gunluk, "kredi", lambda: 1000)
    monkeypatch.setattr(gunluk, "rota_suresi", lambda slug, kok=None: 15)
    monkeypatch.setattr(gunluk, "rota_paleti", lambda slug, kok=None: "neon")

    def fake_run(command, cwd):
        if "kie_uret.py" in " ".join(command):
            events.append(("generate", command))
        return _tamam()

    monkeypatch.setattr(gunluk, "kosa", fake_run)
    import core.ffmpeg_tools

    def fake_master(source, destination, **kwargs):
        events.append(("master", source, destination, kwargs))
        destination.parent.mkdir(parents=True)
        destination.write_bytes(b"master")

    monkeypatch.setattr(core.ffmpeg_tools, "master_audio", fake_master)

    def fake_audit(master, duration, selected):
        events.append(("audit", master))
        return [], {"genislik": 1080, "yukseklik": 1920, "fps": 23.976, "sure": 15.0}

    monkeypatch.setattr(gunluk, "denetle", fake_audit)

    def fake_contact(master, master_sha, duration):
        events.append(("contact", master))
        target = tmp_path / "contact.png"
        target.write_bytes(b"png")
        return target

    monkeypatch.setattr(gunluk, "_kontakt_uret", fake_contact)
    monkeypatch.setattr(gunluk, "yayinla", lambda *a: (_ for _ in ()).throw(AssertionError("publish")))

    assert gunluk.main(["--yayinlama", "--sehir", slug]) == 0
    assert [event[0] for event in events] == ["generate", "master", "audit", "contact"]
    generation = events[0][1]
    assert generation[generation.index("--resolution") + 1] == "1080p"


def test_contact_stale_file_cannot_hide_new_failure(monkeypatch, tmp_path: Path) -> None:
    master = tmp_path / "out" / "slug" / "master" / "master.mp4"
    master.parent.mkdir(parents=True)
    master.write_bytes(b"master")
    stale = master.parent.parent / "kontakt" / "sha.png"
    stale.parent.mkdir(parents=True)
    stale.write_bytes(b"old")
    from tools import kontrol

    monkeypatch.setattr(kontrol, "contact_sheet", lambda *args: args[2])
    result = gunluk._kontakt_uret(master, "sha", 15.0)
    assert result == stale
    assert not result.exists()


def test_two_masters_same_slug_keep_two_immutable_records(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(gunluk, "KOK", tmp_path)
    for sha in ("a" * 64, "b" * 64):
        record = {"master_sha": sha, "slug": "same", "sema_surumu": 1}
        gunluk.uretim_kaydi_yaz("same", record)
    assert profil.uretim_kaydi_bul("a" * 64, tmp_path)["master_sha"] == "a" * 64
    assert profil.uretim_kaydi_bul("b" * 64, tmp_path)["master_sha"] == "b" * 64


def test_24000_1001_record_approves_with_canonical_24(monkeypatch, tmp_path: Path) -> None:
    master = tmp_path / "out" / "slug" / "master" / "m.mp4"
    master.parent.mkdir(parents=True)
    master.write_bytes(b"master")
    sha = gunluk.sha256_dosya(master)
    record = {
        "sema_surumu": 1,
        "model": gunluk.MODEL,
        "istenen_profil": "1080p",
        "profil_hash": gunluk.profil_hash(),
        "slug": "slug",
        "beklenen_sure": 15,
        "olculen": {"genislik": 1080, "yukseklik": 1920, "fps": 24000 / 1001, "sure": 15},
        "denetim_sonucu": "basarili",
        "master_sha": sha,
        "ts": "now",
    }
    record_path = tmp_path / "out" / "slug" / "uretim" / f"{sha}.json"
    record_path.parent.mkdir(parents=True)
    record_path.write_text(json.dumps(record), encoding="utf-8")
    monkeypatch.setattr(gunluk, "KOK", tmp_path)
    monkeypatch.setattr(gunluk, "ONAY_DOSYASI", tmp_path / "profil_onay.json")
    assert gunluk.onayla(master) == 0
    approval = json.loads(gunluk.ONAY_DOSYASI.read_text(encoding="utf-8"))
    assert approval["fps"] == 24


def test_yayinla_mevcut_uses_record_slug_and_no_generation(monkeypatch, tmp_path: Path) -> None:
    master = tmp_path / "master.mp4"
    master.write_bytes(b"master")
    sha = gunluk.sha256_dosya(master)
    record = {
        "master_sha": sha,
        "denetim_sonucu": "basarili",
        "istenen_profil": "1080p",
        "model": gunluk.MODEL,
        "beklenen_sure": 15,
        "slug": "record-slug",
        "sema_surumu": 1,
    }
    approval_path = tmp_path / "profil_onay.json"
    approval_path.write_text(json.dumps(_approval(master_sha=sha)), encoding="utf-8")
    monkeypatch.setattr(gunluk, "ONAY_DOSYASI", approval_path)
    monkeypatch.setattr(gunluk, "KOK", tmp_path)
    monkeypatch.setattr(gunluk, "defter", lambda: [])
    cikti = tmp_path / "out" / "record-slug"
    cikti.mkdir(parents=True)
    (cikti / "CAPTION.txt").write_text("caption #MegaSlideFear #TestTower", encoding="utf-8")
    (cikti / "TITLE.txt").write_text(
        "Record slug glass drop #shorts\nRecord slug, no floor #shorts",
        encoding="utf-8",
    )
    monkeypatch.setattr(gunluk, "uretim_kaydi_bul", lambda *args: record)
    called = []
    monkeypatch.setattr(
        gunluk, "yayinla",
        lambda path, slug, same, kayit=None, baslik="", tags="": called.append((path, slug)) or 0,
    )
    monkeypatch.setattr(gunluk, "uretim_komutu", lambda *a: (_ for _ in ()).throw(AssertionError("generate")))
    assert gunluk.yayinla_mevcut(master, False) == 0
    assert called == [(master, "record-slug")]


def test_yayinla_mevcut_rejects_sha_mismatch(monkeypatch, tmp_path: Path) -> None:
    master = tmp_path / "master.mp4"
    master.write_bytes(b"master")
    sha = gunluk.sha256_dosya(master)
    monkeypatch.setattr(
        gunluk,
        "uretim_kaydi_bul",
        lambda *args: {
            "master_sha": sha,
            "denetim_sonucu": "basarili",
            "istenen_profil": "1080p",
        },
    )
    approval_path = tmp_path / "profil_onay.json"
    approval_path.write_text(json.dumps(_approval(master_sha="other")), encoding="utf-8")
    monkeypatch.setattr(gunluk, "ONAY_DOSYASI", approval_path)
    monkeypatch.setattr(gunluk, "yayinla", lambda *a: (_ for _ in ()).throw(AssertionError("publish")))
    assert gunluk.yayinla_mevcut(master, False) == 1


def test_schema_one_has_only_frozen_first_commit_fields() -> None:
    forbidden = {"palet", "caption", "secilen_baslik", "etiketler"}
    record_fields = {
        "sema_surumu", "model", "istenen_profil", "profil_hash", "slug",
        "beklenen_sure", "olculen", "denetim_sonucu", "master_sha", "ts",
    }
    assert not (record_fields & forbidden)
