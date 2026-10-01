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
from series.replenish import (
    creature_name,
    lookalike_group,
    strict_plan_validation_enabled,
    used_lookalike_groups,
    validate_plan_against_config,
)
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


def _lookalike_warnings(series_dir: pathlib.Path, cfg: dict, plan: dict,
                        number: int) -> list[str]:
    """Kuyruktaki planın hayvanı, ÖNCEKİ bir planın benzer-hayvan grubunda mı.

    Uyarıdır, hata değil: üretim kapısı bunu denetlemez (yazar kapısı denetler),
    lint hatası ise "üretim reddeder" anlamına gelir."""
    history = []
    for path in (series_dir / "plans").glob("part*.json"):
        match = PART_NAME.fullmatch(path.name)
        if not match or int(match.group(1)) >= number:
            continue
        try:
            earlier = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        title = str((earlier.get("episode") or {}).get("title") or "")
        history.append({"n": int(match.group(1)), "title": title,
                        "creature": creature_name(earlier, title)})
    history.sort(key=lambda item: item["n"])
    used = used_lookalike_groups(history, cfg)
    title = str((plan.get("episode") or {}).get("title") or "")
    creature = creature_name(plan, title)
    group = lookalike_group(creature, cfg)
    if group and group in used:
        first, name = used[group]
        return [f"benzer hayvan tekrarı: {creature!r} {group!r} grubunda, "
                f"o grup part {first} ({name!r}) ile kullanıldı"]
    return []


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
            errors = list(result.get("errors", []))
            warnings = list(result.get("warnings", []))
            # Denetci URETIM KAPISININ AYNISINI kosar. Oncesinde yalniz
            # validate_plan cagriliyordu, yani produce.py'nin kredi harcamadan
            # once kostugu plan/cfg kapisi buradan GORUNMUYORDU: kuyruk "TEMIZ"
            # raporlanirken bulutta ayni plan reddedilebiliyordu.
            cfg = meta.get("auto_replenish") or {}
            if strict_plan_validation_enabled(cfg):
                errors += validate_plan_against_config(plan, cfg, engine=bible.engine)
            match = PART_NAME.fullmatch(path.name)
            if match:
                warnings += _lookalike_warnings(series_dir, cfg, plan, int(match.group(1)))
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
