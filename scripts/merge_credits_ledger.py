#!/usr/bin/env python3
"""credits_ledger.json çakışma birleştirici (persist_state.sh çağırır).

İki hat aynı anda deftere satır eklediğinde (defter append-only) autostash
veya rebase çakışması çıkar; 2026-08-07 ve 2026-08-08'de bu yarış iki kez
yayın kaydı kaybettirdi ve kanala mükerrer video bastırdı. Birleşim
deterministiktir ve yönden bağımsızdır: base+ours+theirs girdilerinin
birebir-eşitlik dedup'lu birleşimi, ts'e göre kararlı sıralanır. Aynı
(series, part) için farklı ts'li tekrar denemeler bilerek KORUNUR (gerçek
harcamalardır). Bilinen alanlar üç yönlü birleştirilir; bilinmeyen alanlar
çakışmıyorsa korunur. Güvenli biçimde birleştirilemeyen veri exit 1 ile
fail-closed kalır ve persist eskisi gibi elle bakıma düşer.
"""
import json
import math
import subprocess
import sys

# Windows cp1252 konsolunda Türkçe mesajlar UnicodeEncodeError verir (bilinen
# Py3.12 tuzağı); çıktı akışları UTF-8'e sabitlenir.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


def read_stage(stage: int, path: str):
    proc = subprocess.run(
        ["git", "show", f":{stage}:{path}"], capture_output=True
    )
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout.decode("utf-8"))
    except ValueError:
        return None


def is_ledger(doc) -> bool:
    return (
        isinstance(doc, dict)
        and "entries" in doc
        and isinstance(doc["entries"], list)
        and (
            "episode_spend" not in doc
            or isinstance(doc["episode_spend"], dict)
        )
    )


def merge_entries(base: dict, ours: dict, theirs: dict) -> list:
    merged, seen = [], set()
    for entry in base["entries"] + ours["entries"] + theirs["entries"]:
        key = json.dumps(entry, sort_keys=True, ensure_ascii=False)
        if key in seen:
            continue
        seen.add(key)
        merged.append(entry)
    merged.sort(key=lambda e: str(e.get("ts", "")) if isinstance(e, dict) else "")
    return merged


def validate_episode_spend(doc: dict, side: str) -> None:
    for key, value in doc.get("episode_spend", {}).items():
        # bool, Python'da int alt sınıfıdır; kredi miktarı olarak kabul edilmez.
        numeric = isinstance(value, (int, float)) and not isinstance(value, bool)
        finite = not isinstance(value, float) or math.isfinite(value)
        if not numeric or not finite or value < 0:
            raise ValueError(
                f"{side} episode_spend[{key!r}] sayısal ve negatif olmayan "
                "bir değer değil"
            )


def merge_episode_spend(base: dict, ours: dict, theirs: dict) -> dict:
    for side, doc in (("base", base), ("ours", ours), ("theirs", theirs)):
        validate_episode_spend(doc, side)

    base_spend = base.get("episode_spend", {})
    ours_spend = ours.get("episode_spend", {})
    theirs_spend = theirs.get("episode_spend", {})
    keys = sorted(set(base_spend) | set(ours_spend) | set(theirs_spend))
    merged = {}
    for key in keys:
        base_value = base_spend.get(key, 0)
        ours_value = ours_spend.get(key, base_value)
        theirs_value = theirs_spend.get(key, base_value)
        reconciled = ours_value + theirs_value - base_value
        # Eksik taraf burada özellikle 0 sayılır; eksik sayım güvenlik tavanını
        # zayıflatacağı için gerekirse fazla sayım yönüne sıkıştırılır.
        safe_floor = max(ours_spend.get(key, 0), theirs_spend.get(key, 0))
        merged[key] = max(reconciled, safe_floor)
    return merged


def merge_unknown_keys(base: dict, ours: dict, theirs: dict) -> dict:
    known = {"entries", "episode_spend"}
    keys = sorted((set(base) | set(ours) | set(theirs)) - known)
    merged = {}
    for key in keys:
        ours_has = key in ours
        theirs_has = key in theirs
        if ours_has and theirs_has:
            if ours[key] != theirs[key]:
                raise ValueError(
                    f"bilinmeyen üst düzey anahtar birleştirilemedi: {key}"
                )
            merged[key] = ours[key]
        elif ours_has:
            merged[key] = ours[key]
        elif theirs_has:
            merged[key] = theirs[key]
        else:
            merged[key] = base[key]
    return merged


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("kullanım: merge_credits_ledger.py <defter-yolu>", file=sys.stderr)
        return 1
    path = argv[1]

    ours = read_stage(2, path)
    theirs = read_stage(3, path)
    if ours is None or theirs is None:
        print(f"{path}: ours/theirs aşaması okunamadı ,  elle bak", file=sys.stderr)
        return 1
    base = read_stage(1, path)
    if base is None:
        base = {"entries": []}

    for doc in (base, ours, theirs):
        if not is_ledger(doc):
            print(f"{path}: beklenmeyen defter şeması ,  elle bak", file=sys.stderr)
            return 1

    try:
        merged_entries = merge_entries(base, ours, theirs)
        merged_spend = merge_episode_spend(base, ours, theirs)
        unknown = merge_unknown_keys(base, ours, theirs)
    except ValueError as exc:
        print(f"{path}: {exc} ,  elle bak", file=sys.stderr)
        return 1

    merged_doc = {"entries": merged_entries}
    if any("episode_spend" in doc for doc in (base, ours, theirs)):
        merged_doc["episode_spend"] = merged_spend
    for key in sorted(unknown):
        merged_doc[key] = unknown[key]
        print(
            f"{path}: uyarı: bilinmeyen üst düzey anahtar korundu: {key}",
            file=sys.stderr,
        )

    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(merged_doc, ensure_ascii=False, indent=2) + "\n")
    print(
        f"{path}: defter birleşti ,  ours {len(ours['entries'])} + "
        f"theirs {len(theirs['entries'])} -> {len(merged_entries)} girdi"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
