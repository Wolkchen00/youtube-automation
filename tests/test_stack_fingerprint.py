"""Donmus uretim stack'i parmak izinin determinism ve kayit guvenceleri."""

import json
from unittest import mock

from core import stack_fingerprint
from series.series_meta import SeriesMeta


def _fixture(tmp_path, monkeypatch):
    project = tmp_path / "repo"
    series_dir = project / "sentinal_ihsan" / "test-series"
    series_dir.mkdir(parents=True)
    for index, relative in enumerate(stack_fingerprint.STACK_SOURCES):
        path = project / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(f"# source {index}\nvalue = {index}\n".encode("utf-8"))

    bible = {
        "slug": "test-series",
        "series": {"master_lufs": -14, "description": "stable"},
        "art_style": "natural",
        "style_ref_url": None,
        "characters": [{
            "name": "Ihsan",
            "description": "black shirt",
            "metadata": {"kind": "character"},
        }],
        "environments": [{"id": "kitchen", "description": "worn counter"}],
    }
    series = {
        "base_title": "Test",
        "logline": "A test series",
        "hashtags": "#test",
        "families": ["alpha", "beta"],
        "music_style": "dry taps",
        "total_parts": 20,
        "auto_replenish": {"batch": 5, "brief": "stable brief"},
        "parts": {},
        "next_part": 1,
        "last_run": {"at": "today"},
    }
    bible_path = series_dir / "bible.json"
    series_path = series_dir / "series.json"
    doctrine_path = series_dir.parent / "KONSEPT.md"
    bible_path.write_bytes(json.dumps(bible, ensure_ascii=False).encode("utf-8"))
    series_path.write_bytes(json.dumps(series, ensure_ascii=False).encode("utf-8"))
    doctrine_path.write_bytes(b"Frozen doctrine\n")

    monkeypatch.setattr(stack_fingerprint, "PROJECT_ROOT", project)
    monkeypatch.setattr(stack_fingerprint, "data_dir", lambda slug: series_dir)
    monkeypatch.setattr(
        stack_fingerprint,
        "doctrine_path",
        lambda slug: doctrine_path if doctrine_path.exists() else None,
    )
    return {
        "project": project,
        "series_dir": series_dir,
        "bible_path": bible_path,
        "series_path": series_path,
        "doctrine_path": doctrine_path,
        "bible": bible,
        "series": series,
    }


def _write_json(path, value, *, indent=None, sort_keys=False):
    path.write_bytes(json.dumps(
        value,
        ensure_ascii=False,
        indent=indent,
        sort_keys=sort_keys,
    ).encode("utf-8"))


def test_crlf_and_lf_source_versions_have_the_same_fingerprint(tmp_path, monkeypatch):
    fixture = _fixture(tmp_path, monkeypatch)
    source = fixture["project"] / stack_fingerprint.STACK_SOURCES[0]
    source.write_bytes(b"first line\nsecond line\n")
    lf_hash = stack_fingerprint.fingerprint("test-series")
    source.write_bytes(b"first line\r\nsecond line\r\n")
    assert stack_fingerprint.fingerprint("test-series") == lf_hash


def test_json_key_order_and_indentation_do_not_change_fingerprint(tmp_path, monkeypatch):
    fixture = _fixture(tmp_path, monkeypatch)
    before = stack_fingerprint.fingerprint("test-series")
    _write_json(fixture["bible_path"], fixture["bible"], indent=4, sort_keys=True)
    _write_json(fixture["series_path"], fixture["series"], indent=2, sort_keys=True)
    assert stack_fingerprint.fingerprint("test-series") == before


def test_adding_nested_ref_url_does_not_change_fingerprint(tmp_path, monkeypatch):
    fixture = _fixture(tmp_path, monkeypatch)
    before = stack_fingerprint.fingerprint("test-series")
    fixture["bible"]["environments"][0]["ref_url"] = "https://cache.test/ref.png"
    fixture["bible"]["characters"][0]["metadata"].update({
        "_runtime": "ignored",
    })
    _write_json(fixture["bible_path"], fixture["bible"])
    assert stack_fingerprint.fingerprint("test-series") == before


def test_style_ref_url_change_changes_fingerprint(tmp_path, monkeypatch):
    fixture = _fixture(tmp_path, monkeypatch)
    before = stack_fingerprint.fingerprint("test-series")
    fixture["bible"]["style_ref_url"] = "https://operator.test/style.png"
    _write_json(fixture["bible_path"], fixture["bible"])
    assert stack_fingerprint.fingerprint("test-series") != before


def test_daily_series_ledger_fields_do_not_change_fingerprint(tmp_path, monkeypatch):
    fixture = _fixture(tmp_path, monkeypatch)
    before = stack_fingerprint.fingerprint("test-series")
    fixture["series"].update({
        "parts": {"1": {"status": "published"}},
        "next_part": 17,
        "last_run": {"at": "tomorrow", "parts": "12-16"},
    })
    _write_json(fixture["series_path"], fixture["series"])
    assert stack_fingerprint.fingerprint("test-series") == before


def test_bible_master_lufs_change_changes_fingerprint(tmp_path, monkeypatch):
    fixture = _fixture(tmp_path, monkeypatch)
    before = stack_fingerprint.fingerprint("test-series")
    fixture["bible"]["series"]["master_lufs"] = -16
    _write_json(fixture["bible_path"], fixture["bible"])
    assert stack_fingerprint.fingerprint("test-series") != before


def test_stack_source_content_change_changes_fingerprint(tmp_path, monkeypatch):
    fixture = _fixture(tmp_path, monkeypatch)
    before = stack_fingerprint.fingerprint("test-series")
    source = fixture["project"] / stack_fingerprint.STACK_SOURCES[-1]
    source.write_bytes(source.read_bytes() + b"changed = True\n")
    assert stack_fingerprint.fingerprint("test-series") != before


def test_removing_a_stack_source_from_the_list_changes_fingerprint(tmp_path, monkeypatch):
    _fixture(tmp_path, monkeypatch)
    before = stack_fingerprint.fingerprint("test-series")
    monkeypatch.setattr(
        stack_fingerprint,
        "STACK_SOURCES",
        stack_fingerprint.STACK_SOURCES[:-1],
    )
    assert stack_fingerprint.fingerprint("test-series") != before


def test_stack_version_change_changes_fingerprint(tmp_path, monkeypatch):
    _fixture(tmp_path, monkeypatch)
    before = stack_fingerprint.fingerprint("test-series")
    # Sabit bir surum dizesi PINLEME: sf1 -> sf2 yukseltmesinde bu test sessizce
    # kendiliginden gecer hale gelmisti. Iddia edilen sey degismezdir: surum
    # DEGISIRSE parmak izi degisir.
    monkeypatch.setattr(
        stack_fingerprint, "STACK_VERSION",
        stack_fingerprint.STACK_VERSION + "-baska",
    )
    assert stack_fingerprint.fingerprint("test-series") != before


def test_doctrine_content_change_changes_fingerprint(tmp_path, monkeypatch):
    fixture = _fixture(tmp_path, monkeypatch)
    before = stack_fingerprint.fingerprint("test-series")
    fixture["doctrine_path"].write_bytes(b"Changed frozen doctrine\n")
    assert stack_fingerprint.fingerprint("test-series") != before


def test_mark_produced_is_fail_open_when_fingerprint_fails():
    meta = SeriesMeta({"slug": "test-series", "parts": {}})
    with mock.patch(
        "series.series_meta.fingerprint",
        side_effect=PermissionError("okuma reddedildi"),
    ), mock.patch("series.series_meta.logger.warning") as warning:
        meta.mark_produced(1, "episode.mp4", "Episode")
    part = meta.get_part(1)
    assert part["status"] == "produced"
    assert part["video"] == "episode.mp4"
    assert part["subtitle"] == "Episode"
    assert part["stack_sha256"] is None
    assert part["stack_version"] is None
    warning.assert_called_once()


def test_mark_produced_records_hash_and_version():
    meta = SeriesMeta({"slug": "test-series", "parts": {}})
    with mock.patch(
        "series.series_meta.fingerprint",
        return_value="d" * 64,
    ):
        meta.mark_produced(1, "episode.mp4")
    part = meta.get_part(1)
    assert part["stack_sha256"] == "d" * 64
    assert part["stack_version"] == stack_fingerprint.STACK_VERSION
