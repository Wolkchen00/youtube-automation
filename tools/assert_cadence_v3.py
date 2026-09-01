"""Kadans v3.1 yapilandirma butunlugu kontrolu (series.json auto_replenish).

Kullanim:
    python -X utf8 tools/assert_cadence_v3.py [series.json yolu]

Kirmizi/yesil kaniti: aimagine/next-stop/series.json.v2bak -> CIKIS 1 olmak ZORUNDA.

replenish.py yalnizca prompt'un onekle BASLADIGINI dogruluyor; govdeyi hic denetlemiyor.
Bu script onekleri, ortak yanki son ekini ve brief maddelerini denetler.
"""
import io
import json
import re
import subprocess
import sys
from pathlib import Path

DEFAULT = Path("aimagine/next-stop/series.json")
EM_DASH, EN_DASH = chr(0x2014), chr(0x2013)   # formatter hook literal tireyi bozuyor

# cekim -> beklenen ortme saatleri (plan bolum 4.1)
COVER_TIMES = {
    1: ["2.5", "5.0", "7.5"],
    2: ["1.0", "4.0", "7.0"],
    3: ["1.0", "4.0", "7.0"],
    4: ["1.0", "4.0", "7.0"],
    5: ["1.0", "4.0", "7.0"],
    6: ["1.0", "3.6", "6.8"],
}

ECHO_MIN = 300
ECHO_PROBES = [
    ("sabit kamera",        ["never moves from its one fixed place"]),
    ("yana bakis",          ["sideways"]),
    ("kameraya dogru degil", ["never toward the camera"]),
    ("cam tavan",           ["glass roof"]),
    ("direkler",            ["gripping poles"]),
    ("opak ortam ortmesi",  ["opaque environmental cover"]),
    ("ceyrek saniye",       ["a fifth of a second", "fifth of a second"]),
    ("duran kare yok",      ["never a still frame", "is ever a still frame"]),
]

BRIEF_PROBES = [
    ("kadraj kilidi",        ["KADRAJ TUM BOLUM BOYUNCA KILITLIDIR"]),
    ("yana akis",            ["DUNYA YANA AKAR"]),
    ("kacis noktasi yok",    ["kacis noktasi olmaz"]),
    ("yolcular ayakta",      ["YOLCULAR AYAKTA DURUR VE TUTUNUR"]),
    ("direkler",             ["dikey direkleri ve tutamaklari"]),
    ("kenar isigi siluet",   ["kenar isigiyla cizilmis siluetler"]),
    ("kimlik secilmez",      ["HICBIR MESAFEDE secilmez"]),
    ("tepki asla eksik",     ["Tepki asla eksik"]),
    ("ortam maddesi ortme",  ["ORTAM MADDESIYLE"]),
    ("en fazla bir yapisal", ["EN FAZLA BIR yapisal"]),
    ("ortme suresi",         ["sekizde biri ile dortte biri"]),
    ("tunelde beklemez",     ["BEKLEMEZ"]),
    ("uzun karanlik yok",    ["uzun\nkaranlik gecis istisnasi YOKTUR", "karanlik gecis istisnasi YOKTUR"]),
    ("olu hava yok",         ["OLU HAVA YOK"]),
    ("cam tavan yukari",     ["YUKARI bakmalidir"]),
    ("dikkat beati",         ["BIR SEY TRENE DIKKAT EDER"]),
    ("beat sadece 4 veya 5", ["cekim 4 ya da cekim 5"]),
    ("zincir tekrari yasak", ["ZINCIR TEKRARI YASAK"]),
    ("karanlik 3-6",         ["Cekim 3, 4, 5 ve 6'nin govdesinde"]),
    ("canon yankisi",        ["CANON YANKISI"]),
]

FROZEN_KEYS = ["families", "title_style", "title_patterns", "batch", "min_queue",
               "shots", "shot_seconds", "hook_shot", "chain_breaks", "credit_hard_cap"]


def head_blob(path: Path):
    rel = path.as_posix()
    for suffix in (".v2bak", ".v3bak"):
        if rel.endswith(suffix):
            rel = rel[: -len(suffix)]
    try:
        out = subprocess.run(["git", "show", "HEAD:" + rel], capture_output=True, timeout=30)
        if out.returncode != 0:
            return None
        return json.loads(out.stdout.decode("utf-8"))
    except Exception:
        return None


def common_suffix(strings):
    if not strings:
        return ""
    ref = strings[0]
    n = 0
    while n < len(ref) and all(len(s) > n and s[-1 - n] == ref[-1 - n] for s in strings):
        n += 1
    return ref[len(ref) - n:] if n else ""


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    fails = []

    if not path.is_file():
        print("HATA: dosya yok: %s" % path)
        return 1
    try:
        data = json.loads(io.open(path, encoding="utf-8").read())
    except Exception as exc:
        print("HATA: JSON okunamadi: %s" % exc)
        return 1

    ar = data.get("auto_replenish") or {}
    sp = ar.get("shot_plan")
    brief = ar.get("brief") or ""

    if not isinstance(sp, list) or len(sp) != 6 or not all(
            isinstance(x, str) and x.strip() for x in sp):
        print("HATA: shot_plan tam 6 dolu string olmali (bulunan: %r)" %
              (len(sp) if isinstance(sp, list) else type(sp).__name__))
        return 1

    # 1) ortme saatleri
    for n, times in COVER_TIMES.items():
        body = sp[n - 1]
        for t in times:
            pat = r"(?<![\d.])~?" + re.escape(t) + r"(?![\d])"
            if not re.search(pat, body):
                fails.append("cekim %d onekinde ortme saati %s yok" % (n, t))

    # 2) ortak yanki son eki
    echo = common_suffix(sp)
    if len(echo) < ECHO_MIN:
        fails.append("ortak yanki son eki %d karakter, en az %d olmali" % (len(echo), ECHO_MIN))
    else:
        el = echo.lower()
        for label, needles in ECHO_PROBES:
            if not any(x in el for x in needles):
                fails.append("yanki maddesi EKSIK -> %s" % label)
    for i, p in enumerate(sp, 1):
        if echo and not p.endswith(echo):
            fails.append("cekim %d oneki ortak yanki ile bitmiyor" % i)

    # 3) brief maddeleri
    for label, needles in BRIEF_PROBES:
        if not any(x in brief for x in needles):
            fails.append("brief maddesi EKSIK -> %s" % label)

    # 4) tire
    blob = brief + "".join(sp)
    if EM_DASH in blob:
        fails.append("shot_plan/brief icinde em-dash var")
    if EN_DASH in blob:
        fails.append("shot_plan/brief icinde en-dash var")

    # 5) dondurulmus kardes anahtarlar HEAD ile ayni mi
    head = head_blob(path)
    if head is None:
        print("NOT: git HEAD surumu okunamadi, kardes-anahtar karsilastirmasi atlandi")
    else:
        har = head.get("auto_replenish") or {}
        for k in FROZEN_KEYS:
            if json.dumps(ar.get(k), sort_keys=True, ensure_ascii=False) != \
               json.dumps(har.get(k), sort_keys=True, ensure_ascii=False):
                fails.append("dondurulmus anahtar DEGISMIS: auto_replenish.%s" % k)

    print("dosya   : %s" % path)
    print("shot_plan: 6 onek, uzunluklar %s" % [len(x) for x in sp])
    print("yanki   : %d karakter" % len(echo))
    print("brief   : %d karakter" % len(brief))
    if fails:
        print("\nBASARISIZ (%d):" % len(fails))
        for f in fails:
            print("  - %s" % f)
        return 1
    print("\nCADENCE V3 OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
