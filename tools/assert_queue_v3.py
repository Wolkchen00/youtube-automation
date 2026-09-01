"""Kuyruk butunlugu: yayinlanmamis her plan canon v3.1 sozlesmesine uyuyor mu?

Kullanim:
    python -X utf8 tools/assert_queue_v3.py

Ilk yayinlanmamis part numarasi series.json'dan KESFEDILIR (part04 gibi sabit isim yok;
CI arada bir bolum yayinlamis olabilir).

KRITIK (Same Page turu 3): replenish.py yalnizca prompt'un onekle BASLADIGINI dogruluyor
(satir ~243-245), asgari govde uzunlugu ya da icerik denetimi YOK. Yani onek + yanki'dan
ibaret, govdesiz bir prompt bugun tum yapilandirma kapilarindan gecer. Bu yuzden burada
onek VE yanki soyulup arada gercek vista icerigi kaldigi dogrulanir.
"""
import io
import json
import re
import sys
from pathlib import Path

DATA = Path("aimagine/next-stop")
PLANS = DATA / "plans"
MIN_BODY = 400

COVER_TIMES = {
    1: ["2.5", "5.0", "7.5"],
    2: ["1.0", "4.0", "7.0"],
    3: ["1.0", "4.0", "7.0"],
    4: ["1.0", "4.0", "7.0"],
    5: ["1.0", "4.0", "7.0"],
    6: ["1.0", "3.6", "6.8"],
}


def main():
    try:
        s = json.loads(io.open(DATA / "series.json", encoding="utf-8").read())
    except Exception as exc:
        print("HATA: series.json okunamadi: %s" % exc)
        return 1

    ar = s.get("auto_replenish") or {}
    sp = ar.get("shot_plan") or []
    if len(sp) != 6:
        print("HATA: shot_plan 6 degil (%d)" % len(sp))
        return 1
    echo = sp[0][sp[0].rindex("Remember the canon:"):]

    parts = s.get("parts") or {}
    total = int(s.get("total_parts") or 0)
    published = {int(n) for n, p in parts.items() if str(p.get("status")) == "published"}
    first_unpub = 1
    while first_unpub in published:
        first_unpub += 1

    fails = []

    # 1) total_parts USTUNDE dosya kalmamali (_adopt_orphans ardisiklik tuzagi)
    for f in sorted(PLANS.glob("part*.json")):
        m = re.search(r"part0*(\d+)\.json$", f.name)
        if m and int(m.group(1)) > total:
            fails.append("total_parts=%d ustunde plan dosyasi var: %s" % (total, f.name))

    checked = 0
    for n in range(first_unpub, total + 1):
        path = PLANS / ("part%02d.json" % n)
        if not path.is_file():
            fails.append("part%02d.json yok (first_unpub=%d, total=%d)" % (n, first_unpub, total))
            continue
        try:
            plan = json.loads(io.open(path, encoding="utf-8").read())
        except Exception as exc:
            fails.append("part%02d okunamadi: %s" % (n, exc))
            continue
        checked += 1
        tag = "part%02d" % n

        shots = plan.get("shots") or []
        if len(shots) != 6:
            fails.append("%s: cekim sayisi %d, 6 olmali" % (tag, len(shots)))
            continue
        if [int(x.get("n", 0)) for x in shots] != [1, 2, 3, 4, 5, 6]:
            fails.append("%s: cekim numaralari 1..6 degil" % tag)
        if int(plan.get("hook_shot") or 0) != 6:
            fails.append("%s: hook_shot 6 olmali" % tag)

        title = str((plan.get("episode") or {}).get("title") or "")
        fam = str(plan.get("family") or "").strip()
        pats = ar.get("title_patterns") or []
        matched = [p for p in pats if re.fullmatch(p.get("regex", ""), title)]
        if not matched:
            fails.append("%s: baslik title_patterns fullmatch saglamiyor: %r" % (tag, title))
        elif not any(fam in (p.get("families") or []) for p in matched):
            fails.append("%s: baslik kalibi family=%r kabul etmiyor" % (tag, fam))

        for sh in shots:
            i = int(sh.get("n", 0))
            if str(sh.get("duration")) not in ("4", "6", "8", "10"):
                fails.append("%s cekim %d: sure %r gecersiz" % (tag, i, sh.get("duration")))
            prompt = str(sh.get("prompt") or "")
            prefix = sp[i - 1].strip() + "\n\n"
            if not prompt.startswith(prefix):
                fails.append("%s cekim %d: prompt shot_plan onekiyle baslamiyor" % (tag, i))
                continue
            if not prompt.endswith(echo):
                fails.append("%s cekim %d: prompt canon yankisi ile BITMIYOR" % (tag, i))
                continue
            body = prompt[len(prefix):-len(echo)].strip()
            if len(body) < MIN_BODY:
                fails.append("%s cekim %d: govde %d karakter, en az %d olmali "
                             "(onek+yanki disinda gercek icerik yok)" % (tag, i, len(body), MIN_BODY))
            hits = sum(1 for t in COVER_TIMES.get(i, []) if t in body)
            if hits < 2:
                fails.append("%s cekim %d: govde kendi ortme saatlerinden en az 2'sini "
                             "icermeli (bulunan %d)" % (tag, i, hits))

    print("ilk yayinlanmamis part: %d | total_parts: %d | denetlenen plan: %d"
          % (first_unpub, total, checked))
    if fails:
        print("\nBASARISIZ (%d):" % len(fails))
        for f in fails[:40]:
            print("  - %s" % f)
        if len(fails) > 40:
            print("  ... +%d tane daha" % (len(fails) - 40))
        return 1
    if checked == 0:
        print("\nUYARI: denetlenecek yayinlanmamis plan yok.")
        return 1
    print("\nQUEUE V3 OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
