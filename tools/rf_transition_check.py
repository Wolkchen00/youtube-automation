#!/usr/bin/env python3
"""FROM SCRATCH plan gecisinin korunan verilerini denetler."""

import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from series import preflight
from series.bible import data_dir, doctrine_path, doctrine_sha256


SIDECAR_NAME = ".rf_transition.json"
REQUIRED_PARTS = range(6, 11)
_PLAN_RE = re.compile(r"^part(\d+)\.json$")


def _sha256(data):
    """Baytlarin SHA-256 ozetini dondurur."""
    return hashlib.sha256(data).hexdigest()


def canonical_parts_sha256(parts):
    """Parts alt agacini kanonik JSON olarak ozetler."""
    payload = json.dumps(
        parts,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return _sha256(payload)


def _read_json(path):
    """JSON dosyasini nesne olarak okur."""
    return json.loads(path.read_text(encoding="utf-8"))


def _current_doctrine(slug, series):
    """Guncel doktrin ozetini ve varsa hatayi dondurur."""
    path = doctrine_path(slug)
    if path is None:
        return None, "doktrin dosyasi bulunamadi"
    try:
        text = path.read_bytes().decode("utf-8").replace("\r\n", "\n")
    except (OSError, UnicodeError) as error:
        return None, f"doktrin okunamadi: {error}"
    if not text.strip():
        return None, "doktrin dosyasi bos"
    digest = doctrine_sha256(path)
    pinned = str(series.get("doctrine_sha256") or "").strip().lower()
    if pinned != digest:
        return None, "series doctrine_sha256 pin'i guncel doktrinle eslesmiyor"
    return digest, None


def _checkpoint_sha():
    """Calisma agacinin guncel commit kimligini okur."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def _load_context(series_dir):
    """Seri kokunu ve temel dosyalari yukler."""
    root = pathlib.Path(series_dir)
    series = _read_json(root / "series.json")
    slug = str(series.get("slug") or root.name).strip()
    expected = data_dir(slug).resolve()
    if root.resolve() != expected:
        raise ValueError(f"seri yolu kayitli veri yoluyla eslesmiyor: {expected}")
    published = (root / "published.json").read_bytes()
    return root, slug, series, published


def snapshot(series_dir):
    """Korunan durumun gecis oncesi fotografini yazar."""
    try:
        root, slug, series, published = _load_context(series_dir)
        digest, doctrine_error = _current_doctrine(slug, series)
        if doctrine_error:
            raise ValueError(doctrine_error)
        sidecar = root / SIDECAR_NAME
        previous = _read_json(sidecar) if sidecar.exists() else None
        record = {
            "checkpoint_sha": _checkpoint_sha(),
            "doctrine_sha256": digest,
            "next_part": series.get("next_part"),
            "parts_sha256": canonical_parts_sha256(series.get("parts")),
            "published_sha256": _sha256(published),
            "total_parts": series.get("total_parts"),
        }
        if previous is not None:
            record["previous"] = previous
        sidecar.write_text(
            json.dumps(record, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except (OSError, ValueError, json.JSONDecodeError, subprocess.SubprocessError) as error:
        print(f"HATA: snapshot olusturulamadi: {error}", file=sys.stderr)
        return 1

    print(f"RF gecis snapshot'i: {root}")
    print(f"checkpoint_sha={record['checkpoint_sha']}")
    print(f"doctrine_sha256={record['doctrine_sha256']}")
    print(f"parts_sha256={record['parts_sha256']}")
    print(f"published_sha256={record['published_sha256']}")
    print(f"total_parts={record['total_parts']} next_part={record['next_part']}")
    print("SNAPSHOT OK")
    return 0


def _plan_numbers(plans_dir):
    """Plans klasorundeki numarali JSON dosyalarini bulur."""
    numbered = {}
    for path in plans_dir.glob("part*.json"):
        match = _PLAN_RE.fullmatch(path.name)
        if match:
            numbered[int(match.group(1))] = path
    return numbered


def verify(series_dir):
    """Yenilenen planlari ve korunan durumu snapshot ile dogrular."""
    errors = []
    try:
        root, slug, series, published = _load_context(series_dir)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"HATA: seri verisi okunamadi: {error}", file=sys.stderr)
        return 1

    sidecar_path = root / SIDECAR_NAME
    try:
        sidecar = _read_json(sidecar_path)
    except FileNotFoundError:
        print(f"HATA: snapshot sidecar'i yok: {sidecar_path}", file=sys.stderr)
        return 1
    except (OSError, json.JSONDecodeError) as error:
        print(f"HATA: snapshot sidecar'i okunamadi: {error}", file=sys.stderr)
        return 1

    digest, doctrine_error = _current_doctrine(slug, series)
    if doctrine_error:
        errors.append(doctrine_error)
    elif str(sidecar.get("doctrine_sha256") or "").lower() != digest:
        errors.append("snapshot doctrine_sha256 alani guncel doktrinle eslesmiyor")

    current_parts = canonical_parts_sha256(series.get("parts"))
    if sidecar.get("parts_sha256") != current_parts:
        errors.append("series.json parts alt agaci snapshot'tan farkli")
    current_published = _sha256(published)
    if sidecar.get("published_sha256") != current_published:
        errors.append("published.json ham baytlari snapshot'tan farkli")
    if series.get("total_parts") != 10:
        errors.append(f"total_parts 10 olmali, gelen: {series.get('total_parts')!r}")
    if series.get("next_part") != 6:
        errors.append(f"next_part 6 olmali, gelen: {series.get('next_part')!r}")

    numbered = _plan_numbers(root / "plans")
    overflow = sorted(number for number in numbered if number > 10)
    if overflow:
        errors.append(f"10'dan buyuk plan numaralari var: {overflow}")

    for number in REQUIRED_PARTS:
        path = root / "plans" / f"part{number:02d}.json"
        if not path.is_file():
            errors.append(f"gerekli plan yok: {path.name}")
            continue
        try:
            plan = _read_json(path)
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"{path.name} okunamadi: {error}")
        else:
            plan_digest = str(plan.get("doctrine_sha256") or "").strip().lower()
            if digest is not None and plan_digest != digest:
                errors.append(f"{path.name} doctrine_sha256 damgasi guncel degil")
        try:
            result = preflight.run(slug, path)
        except Exception as error:
            errors.append(f"{path.name} preflight calismadi: {error}")
        else:
            if result != 0:
                errors.append(f"{path.name} preflight basarisiz, cikis: {result}")

    print(f"RF gecis dogrulamasi: {root}")
    if errors:
        for error in errors:
            print(f"HATA: {error}")
        print(f"RF TRANSITION FAIL ({len(errors)} ihlal)")
        return 1
    print("Korunan parts ve published.json degismedi.")
    print("part06..part10 guncel doktrinle ve preflight ile dogrulandi.")
    print("RF TRANSITION OK")
    return 0


def main(argv=None):
    """Komut satiri girisini calistirir."""
    parser = argparse.ArgumentParser(
        description="FROM SCRATCH plan gecisini snapshot ve preflight ile denetler."
    )
    parser.add_argument("series_dir", type=pathlib.Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--snapshot", action="store_true")
    mode.add_argument("--verify", action="store_true")
    args = parser.parse_args(argv)
    return snapshot(args.series_dir) if args.snapshot else verify(args.series_dir)


if __name__ == "__main__":
    raise SystemExit(main())
