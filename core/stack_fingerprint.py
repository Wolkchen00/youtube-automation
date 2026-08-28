"""Uretim stack'inin denetlenebilir, seri-bazli parmak izi.

Bu liste yalniz video ciktisini sekillendiren kaynak yuzeyidir. experiment.py,
balance_floor.py, credit_gate.py, killgate.py, analytics.py, approver.py, tools/ ve
tests/ bilerek disaridadir; onlar degisince donmus uretim stack'i bozulmus sayilmaz.
Listenin kendisi de hash'e girer, dolayisiyla kapsami daraltmak sessiz kalamaz.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from core.config import PROJECT_ROOT
from series.bible import data_dir, doctrine_path

STACK_VERSION = "sf1"

STACK_SOURCES = (
    "series/produce.py",
    "series/shots.py",
    "series/critic.py",
    "series/bible.py",
    "series/replenish.py",
    "series/series_runner.py",
    "series/omni_api.py",
    "core/ffmpeg_tools.py",
    "core/kie_api.py",
)

_BIBLE_VOLATILE_KEYS = {
    "ref_url",
    "voice_id",
    "character_id",
    "registered",
    "prop_ref_urls",
}

_SERIES_OUTPUT_KEYS = (
    "auto_replenish",
    "base_title",
    "logline",
    "hashtags",
    "families",
    "music_style",
    "total_parts",
)


def _normalized_bytes(path: Path) -> bytes:
    """Kaynak metnini platformdan bagimsiz UTF-8/LF baytlarina cevir."""
    return path.read_bytes().decode("utf-8").replace("\r\n", "\n").encode("utf-8")


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")


def _stable_bible(value: object) -> object:
    """Uretim sirasinda yazilan kimlik/cache alanlarini her derinlikte ayikla."""
    if isinstance(value, dict):
        return {
            key: _stable_bible(item)
            for key, item in value.items()
            if not key.startswith("_") and key not in _BIBLE_VOLATILE_KEYS
        }
    if isinstance(value, list):
        return [_stable_bible(item) for item in value]
    return value


def _add_input(digest, name: str, content: bytes) -> None:
    """Ad ve uzunluk cercevesi, komsu girdilerin birbirine karismasini onler."""
    encoded_name = name.encode("utf-8")
    digest.update(len(encoded_name).to_bytes(8, "big"))
    digest.update(encoded_name)
    digest.update(b"\0")
    digest.update(len(content).to_bytes(8, "big"))
    digest.update(content)
    digest.update(b"\0")


def fingerprint(slug: str) -> str:
    """Bir serinin mevcut uretim stack'i icin deterministik SHA-256 uret."""
    digest = hashlib.sha256()
    _add_input(digest, "stack_version", STACK_VERSION.encode("utf-8"))
    _add_input(digest, "stack_sources", _canonical_json(STACK_SOURCES))

    for relative in STACK_SOURCES:
        _add_input(
            digest,
            f"source:{relative}",
            _normalized_bytes(PROJECT_ROOT / relative),
        )

    folder = data_dir(slug)
    bible = json.loads((folder / "bible.json").read_text(encoding="utf-8"))
    _add_input(digest, "bible.json", _canonical_json(_stable_bible(bible)))

    series = json.loads((folder / "series.json").read_text(encoding="utf-8"))
    stable_series = {key: series[key] for key in _SERIES_OUTPUT_KEYS if key in series}
    _add_input(digest, "series.json", _canonical_json(stable_series))

    doctrine = doctrine_path(slug)
    if doctrine is None:
        _add_input(digest, "doctrine", b"<yok>")
    else:
        _add_input(digest, "doctrine", _normalized_bytes(doctrine))
    return digest.hexdigest()
