#!/usr/bin/env python3
"""credits_ledger.json çakışma birleştirici (persist_state.sh çağırır).

İki hat aynı anda deftere satır eklediğinde (defter append-only) autostash
veya rebase çakışması çıkar; 2026-08-07 ve 2026-08-08'de bu yarış iki kez
yayın kaydı kaybettirdi ve kanala mükerrer video bastırdı. Birleşim
deterministiktir ve yönden bağımsızdır: base+ours+theirs girdilerinin
birebir-eşitlik dedup'lu birleşimi, ts'e göre kararlı sıralanır. Aynı
(series, part) için farklı ts'li tekrar denemeler bilerek KORUNUR (gerçek
harcamalardır). Şema beklenenden saparsa exit 1 = fail-closed, persist
eskisi gibi elle bakıma düşer.
"""
import json
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
        and set(doc) == {"entries"}
        and isinstance(doc["entries"], list)
    )


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

    merged, seen = [], set()
    for entry in base["entries"] + ours["entries"] + theirs["entries"]:
        key = json.dumps(entry, sort_keys=True, ensure_ascii=False)
        if key in seen:
            continue
        seen.add(key)
        merged.append(entry)
    merged.sort(key=lambda e: str(e.get("ts", "")) if isinstance(e, dict) else "")

    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps({"entries": merged}, ensure_ascii=False, indent=2) + "\n")
    print(
        f"{path}: defter birleşti ,  ours {len(ours['entries'])} + "
        f"theirs {len(theirs['entries'])} -> {len(merged)} girdi"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
