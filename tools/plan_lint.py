"""Kuyruktaki seri planlarını ücretli çağrı yapmadan doğrula.

Kullanım:
    py -X utf8 tools/plan_lint.py --series unnatural-lab

Çıkış kodu:
    0  denetlenen planların hiçbirinde hata yok
    1  en az bir planda hata var
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from series.bible import Bible
from series.shots import validate_plan


REPO = pathlib.Path(__file__).resolve().parents[1]
PART_NAME = re.compile(r"part(\d+)\.json$")


def _series_path(series: str, repo: pathlib.Path = REPO) -> pathlib.Path:
    matches = [
        path
        for path in repo.glob(f"*/{series}/series.json")
        if "output" not in path.parts and "_archive" not in path.parts
    ]
    if not matches:
        raise SystemExit(f"seri bulunamadı: {series}")
    return matches[0]


def _queued_plans(series_dir: pathlib.Path, meta: dict) -> list[pathlib.Path]:
    """Motor kuyruğundaki next_part..total_parts planlarını sıra ile döndür."""
    next_part = int(meta.get("next_part", 1))
    total_parts = int(meta.get("total_parts", 0))
    queued: list[tuple[int, pathlib.Path]] = []
    for path in (series_dir / "plans").glob("part*.json"):
        match = PART_NAME.fullmatch(path.name)
        if match:
            number = int(match.group(1))
            if next_part <= number <= total_parts:
                queued.append((number, path))
    return [path for _, path in sorted(queued)]


def lint_series(series: str, repo: pathlib.Path = REPO) -> int:
    meta_path = _series_path(series, repo)
    series_dir = meta_path.parent
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    bible = Bible(json.loads((series_dir / "bible.json").read_text(encoding="utf-8")))
    plan_paths = _queued_plans(series_dir, meta)

    clean = 0
    failed = 0
    for path in plan_paths:
        print(f"{path.name}:")
        try:
            plan = json.loads(path.read_text(encoding="utf-8"))
            result = validate_plan(plan, bible)
            errors = result.get("errors", [])
            warnings = result.get("warnings", [])
        except (OSError, json.JSONDecodeError) as error:
            errors = [f"plan okunamadı: {error}"]
            warnings = []

        for error in errors:
            print(f"  HATA: {error}")
        for warning in warnings:
            print(f"  UYARI: {warning}")
        if errors:
            failed += 1
        else:
            clean += 1
            print("  TEMİZ")

    names = ", ".join(path.name for path in plan_paths) or "yok"
    print(
        f"ÖZET: denetlenen planlar: {names}; {len(plan_paths)} plan denetlendi; "
        f"{clean} temiz, {failed} hatalı."
    )
    return 1 if failed else 0


def main(argv: list[str] | None = None, *, repo: pathlib.Path = REPO) -> int:
    parser = argparse.ArgumentParser(description="Kuyruktaki planları yerel olarak doğrula")
    parser.add_argument("--series", required=True)
    args = parser.parse_args(argv)
    return lint_series(args.series, repo)


if __name__ == "__main__":
    raise SystemExit(main())
