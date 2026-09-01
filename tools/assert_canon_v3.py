"""Canon v3.1 yapilandirma butunlugu kontrolu (bible.json art_style).

Kullanim:
    python -X utf8 tools/assert_canon_v3.py [bible.json yolu]

Varsayilan yol aimagine/next-stop/bible.json. Kirmizi/yesil kaniti icin
aimagine/next-stop/bible.json.v2bak verilebilir: o dosyada CIKIS 1 olmak ZORUNDA.

Bu script yalnizca YAPILANDIRMA butunlugunu olcer. Anlamsal kapi (kadans, yuz, opaklik,
kadraj kilidi) uretilmis videoda tools/measure_pilot.py ve kare kare insan incelemesidir.
"""
import io
import json
import re
import subprocess
import sys
from pathlib import Path

DEFAULT = Path("aimagine/next-stop/bible.json")
MIN_LEN, MAX_LEN = 5300, 6500
EM_DASH, EN_DASH = chr(0x2014), chr(0x2013)   # formatter hook literal tireyi bozuyor

# (etiket, en az biri bulunmasi gereken kucuk-harf ifadeler)
PROBES = [
    ("1  ham telefon goruntusu",      ["raw photorealistic amateur smartphone footage"]),
    ("1b kusurlar sahne degistirmez", ["never hide the world outside and never change the scene"]),
    ("2  cam gozlem vagonu",          ["glass observation car"]),
    ("2b cam tavan",                  ["into a glass roof"]),
    ("2c tavan kaburgalari",          ["ribs arching overhead", "dark ribs arching"]),
    ("3  KADRAJ KILIDI",              ["the framing is locked"]),
    ("3b aynalanma yasagi",           ["never mirrors"]),
    ("3c yeniden sahneleme yasagi",   ["never re-stages"]),
    ("3d tek kamera konumu",          ["one fixed position, height, angle and lens"]),
    ("4  YANA AKIS",                  ["the world moves sideways"]),
    ("4b kameraya dogru gelmez",      ["never toward the camera"]),
    ("4c kacis noktasi yok",          ["no vanishing point in the middle of the window"]),
    ("4d hat boyunca bakma yasagi",   ["never look along the track"]),
    ("5  yolcular AYAKTA",            ["passengers stand and hold on"]),
    ("5b direkler",                   ["floor-to-ceiling vertical poles"]),
    ("5c kenar isigi siluet",         ["rim-lit silhouettes", "rim-lit outlines"]),
    ("5d kimlik secilmez",            ["never discernible at any distance"]),
    ("5e kiyafet/yer surekli",        ["keep their positions and their clothing"]),
    ("5f camin otesinde insan yok",   ["no human reflection ever appears"]),
    ("6  SISMOGRAF",                  ["the passengers are the seismograph"]),
    ("6b tepki asla eksik olmaz",     ["reaction is never absent"]),
    ("7  hiz",                        ["never stops, never slows and never arrives"]),
    ("8  iki-uc saniyede degisir",    ["the view changes every two or three seconds"]),
    ("9  ortmeyi dunya yapar",        ["the world itself does the covering"]),
    ("9b kadans ortmesi ortamdir",    ["every reset that sets the pace is environmental"]),
    ("9c en fazla bir yapisal",       ["at most one structural cover"]),
    ("10 ortme suresi",               ["one eighth and one quarter of a second"]),
    ("10b tunelde beklemez",          ["never dwells in a tunnel", "never dwells inside a tunnel"]),
    ("10c tam opaklik",               ["complete opacity"]),
    ("10d yari saydam sifirlamaz",    ["translucent or partial cover never permits a reset"]),
    ("11 her ortme bir darbedir",     ["every cover is an impact"]),
    ("12 OLU HAVA YOK",               ["no dead air"]),
    ("12b ortucu cikmaz, doldurur",   ["it fills the frame and becomes the cover"]),
    ("13 dikis kurali",               ["seam rule"]),
    ("13b onek saatleri baglayici",   ["are binding and nothing later may override them"]),
    ("13c son saniye temiz",          ["last second"]),
    ("14 gecis fizigi",               ["transit physics"]),
    ("15 kontrast tirmanir",          ["contrast climbs and never washes out"]),
    ("15b gok en karanlik",           ["darkest region of the landscape"]),
    ("16 yazi yok",                   ["no text anywhere"]),
    ("17 diegetic ses",               ["diegetic audio only"]),
    ("18 guvenlik",                   ["no gore, no graphic injury"]),
]

# ortme suresi kare cinsinden YAZILMAMALI (24 fps'te ceyrek saniye ~6 karedir)
FRAME_PHRASES = [
    r"one or two frames", r"1\s*-\s*2\s*frames", r"a frame or two",
    r"single frame of", r"two frames of",
]


def head_blob(path: Path):
    """git HEAD surumunu getir; yoksa None."""
    rel = path.as_posix()
    for suffix in (".v2bak", ".v3bak"):
        if rel.endswith(suffix):
            rel = rel[: -len(suffix)]
    try:
        out = subprocess.run(["git", "show", "HEAD:" + rel],
                             capture_output=True, timeout=30)
        if out.returncode != 0:
            return None
        return json.loads(out.stdout.decode("utf-8"))
    except Exception:
        return None


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

    art = data.get("art_style")
    if not isinstance(art, str) or not art.strip():
        print("HATA: art_style yok ya da string degil")
        return 1

    low = art.lower()

    if not (MIN_LEN <= len(art) <= MAX_LEN):
        fails.append("uzunluk %d, %d-%d araliginda olmali" % (len(art), MIN_LEN, MAX_LEN))

    for label, needles in PROBES:
        if not any(n in low for n in needles):
            fails.append("canon maddesi EKSIK -> %s (aranan: %r)" % (label, needles[0]))

    if EM_DASH in art:
        fails.append("em-dash (U+2014) var; formatter hook bunu bozuyor")
    if EN_DASH in art:
        fails.append("en-dash (U+2013) var")

    for pat in FRAME_PHRASES:
        if re.search(pat, low):
            fails.append("ortme suresi KARE cinsinden yazilmis (%r); saniye kullanilmali" % pat)

    head = head_blob(path)
    if head is None:
        print("NOT: git HEAD surumu okunamadi, diger-anahtar karsilastirmasi atlandi")
    else:
        # series.title_card BILEREK eklendi (kullanici istegi: ekranda "NEXT STOP: X"
        # kancasi). O anahtar asagida ayrica dogrulanir; geri kalan HEAD ile ayni olmali.
        def strip(d):
            out = {k: v for k, v in d.items() if k != "art_style"}
            if isinstance(out.get("series"), dict):
                out["series"] = {k: v for k, v in out["series"].items() if k != "title_card"}
            return out

        a, b = strip(data), strip(head)
        if json.dumps(a, sort_keys=True, ensure_ascii=False) != \
           json.dumps(b, sort_keys=True, ensure_ascii=False):
            diff = [k for k in sorted(set(a) | set(b)) if a.get(k) != b.get(k)]
            fails.append("art_style/title_card DISINDA anahtar degismis: %s" % diff)

        tc = (data.get("series") or {}).get("title_card") or {}
        if not (tc.get("enabled") and tc.get("from_episode_title")):
            fails.append("series.title_card acik ve from_episode_title=true olmali: %r" % tc)
        elif not (3.0 <= float(tc.get("duration", 0)) <= 6.0):
            fails.append("title_card suresi %s, 3-6 saniye araliginda olmali" % tc.get("duration"))

    print("dosya      : %s" % path)
    print("art_style  : %d karakter (sinir %d-%d)" % (len(art), MIN_LEN, MAX_LEN))
    print("canon maddesi: %d/%d bulundu" % (len(PROBES) - sum(
        1 for lbl, n in PROBES if not any(x in low for x in n)), len(PROBES)))
    if fails:
        print("\nBASARISIZ (%d):" % len(fails))
        for f in fails:
            print("  - %s" % f)
        return 1
    print("\nCANON V3 OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
