from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from tools import qc_call_census as census


NOW = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)


def _journal(root: Path, channel: str = "kanal", series: str = "seri") -> Path:
    path = root / channel / series / "qc_log.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _write(path: Path, *events: dict | str) -> None:
    lines = [event if isinstance(event, str) else json.dumps(event) for event in events]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def _attempt(attempt_id: str, ts: datetime = NOW, **extra: object) -> dict:
    return {
        "ts": ts.isoformat().replace("+00:00", "Z"),
        "event": "qc_api_attempt",
        "attempt_id": attempt_id,
        "task_type": "visual_review",
        "model": "gemini-test",
        "is_fallback": False,
        "episode": 1,
        "shot": 1,
        **extra,
    }


def _result(attempt_id: str, outcome: str, ts: datetime = NOW) -> dict:
    return {
        "ts": ts.isoformat().replace("+00:00", "Z"),
        "event": "qc_api_result",
        "attempt_id": attempt_id,
        "outcome": outcome,
    }


def test_attempt_result_id_eslesir_ve_yinelenen_attempt_sayilmaz(tmp_path: Path) -> None:
    path = _journal(tmp_path)
    _write(
        path,
        _attempt("a1"),
        _attempt("a1"),
        _result("a1", "ok"),
        _attempt("a2"),
        _result("a2", "429"),
    )

    report = census.build_report(tmp_path, now=NOW)

    assert report["q1"]["toplam_cagri"] == 2
    assert report["q2"]["adet"] == {
        "ok": 1,
        "429": 1,
        "diger_hata": 0,
        "sonucsuz": 0,
    }
    assert report["meta"]["yinelenen_attempt_kaydi"] == 1


def test_sonucsuz_attempt_hem_raporda_hem_tabloda_gorunur(tmp_path: Path) -> None:
    _write(_journal(tmp_path), _attempt("kayip"))

    report = census.build_report(tmp_path, now=NOW)
    table = census.render_table(report)

    assert report["q2"]["adet"]["sonucsuz"] == 1
    assert "sonuçsuz" in table and "|    1 | 100.0%" in table


def test_bozuk_json_sayilir_ve_main_sifirla_cikar(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _write(_journal(tmp_path), "{bu json degil", _attempt("a1"), _result("a1", "ok"))

    exit_code = census.main([], project_root=tmp_path, now=NOW)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Bozuk JSON satırı: 1" in output
    assert "TOPLAM" in output


def test_days_siniri_dahil_olacak_sekilde_ts_ile_filtreler(tmp_path: Path) -> None:
    cutoff = NOW - timedelta(days=2)
    _write(
        _journal(tmp_path),
        _attempt("sinir", cutoff),
        _result("sinir", "ok", cutoff),
        _attempt("eski", cutoff - timedelta(microseconds=1)),
        _result("eski", "429", cutoff - timedelta(microseconds=1)),
    )

    report = census.build_report(tmp_path, days=2, now=NOW)

    assert report["q1"]["toplam_cagri"] == 1
    assert report["q2"]["adet"]["ok"] == 1
    assert report["q2"]["adet"]["429"] == 0


@pytest.mark.parametrize("empty_file", [False, True])
def test_bos_veya_eksik_journal_veri_yok_der(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    empty_file: bool,
) -> None:
    if empty_file:
        _write(_journal(tmp_path))

    exit_code = census.main([], project_root=tmp_path, now=NOW)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "veri yok" in output
    assert "Traceback" not in output


def test_json_ile_tablo_ayni_toplamlari_tasir(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _write(
        _journal(tmp_path),
        _attempt("a1"),
        _result("a1", "ok"),
        _attempt("a2"),
        _result("a2", "error"),
    )

    assert census.main(["--json"], project_root=tmp_path, now=NOW) == 0
    json_report = json.loads(capsys.readouterr().out)
    assert census.main([], project_root=tmp_path, now=NOW) == 0
    table = capsys.readouterr().out

    assert json_report["q1"]["toplam_cagri"] == 2
    assert json_report["q2"]["adet"]["ok"] == 1
    assert json_report["q2"]["adet"]["diger_hata"] == 1
    assert "TOPLAM" in table and "|     2" in table
    assert "diğer hata" in table and "|    1 |  50.0%" in table


def test_q3_gozlenen_bolumleri_sayar_ama_tamligi_tahmin_etmez(tmp_path: Path) -> None:
    path = _journal(tmp_path, "sentinal_ihsan", "unnatural-lab")
    _write(
        path,
        _attempt("e1-s1", episode=1, shot=1),
        _result("e1-s1", "ok"),
        _attempt("e1-s2", episode=1, shot=2),
        _result("e1-s2", "ok"),
        _attempt("e2-s1", episode=2, shot=1),
        _result("e2-s1", "ok"),
        _attempt("e2-s2a", episode=2, shot=2),
        _result("e2-s2a", "429"),
        _attempt("e2-s2b", episode=2, shot=2),
        _result("e2-s2b", "ok"),
        _attempt("e2-s3", episode=2, shot=3),
        _result("e2-s3", "ok"),
    )

    q3 = census.build_report(tmp_path, now=NOW)["q3"]

    assert [row["cagri"] for row in q3["bolumler"]] == [2, 4]
    assert q3["gozlenen_bolum_medyani"] == 3
    assert q3["gozlenen_bolum_maksimumu"] == 4
    assert q3["tam_bolum_cagri_ihtiyaci"] is None
    assert "belirlenemiyor" in q3["tamamlanma_notu"]
