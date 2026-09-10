"""Rakip/trend taramasi. Reelyze'in KIMLIK DOGRULAMASIZ uc noktalari.

Bu uc nokta anahtar istemiyor ve kota harcamiyor:
    GET /discover/trending           52 nis indeksi
    GET /discover/trending/{slug}    nis basina 24 aykiri video
    GET /retention-report/stats      toplu retention istatistigi

Kullanim:
    python trend.py --nisler
    python trend.py --nis ai-tools
    python trend.py --hepsi --cikti trend.json
    python trend.py --istatistik
"""
import argparse, json, statistics as st, time, urllib.request

BASE = "https://api.getreelyze.com"
UA = {"User-Agent": "Mozilla/5.0"}


def al(yol, timeout=45):
    return json.load(urllib.request.urlopen(
        urllib.request.Request(BASE + yol, headers=UA), timeout=timeout))


def nisler():
    return al("/discover/trending").get("niches", [])


def nis(slug):
    return al("/discover/trending/" + slug).get("videos", [])


def normalize(satirlar):
    """Her nisi KENDI medyanina normalize et.

    Nisler arasi ham karsilastirma Simpson paradoksu uretir: dusuk medyanli
    niste az izlenme bile yuksek gorunur. `outlier_score` da mutlak deger degil
    (formulu tersine cozulemedi), sadece siralama sinyali.
    """
    nis_bazli = {}
    for r in satirlar:
        nis_bazli.setdefault(r.get("nis"), []).append(r)
    for _, vs in nis_bazli.items():
        izl = [v["views"] for v in vs if isinstance(v.get("views"), (int, float))]
        if len(izl) < 5:
            continue
        med = st.median(izl)
        for v in vs:
            if isinstance(v.get("views"), (int, float)) and med:
                v["nis_medyanina_kat"] = round(v["views"] / med, 2)
    return satirlar


def main():
    ap = argparse.ArgumentParser(description="Reelyze ucretsiz trend akisi")
    ap.add_argument("--nisler", action="store_true", help="nis indeksini listele")
    ap.add_argument("--nis", help="tek nisin videolarini cek")
    ap.add_argument("--hepsi", action="store_true", help="butun nisleri cek")
    ap.add_argument("--istatistik", action="store_true", help="toplu retention istatistigi")
    ap.add_argument("--cikti", help="JSON cikti dosyasi")
    a = ap.parse_args()

    if a.istatistik:
        d = al("/retention-report/stats")
        print("=== Reelyze toplu retention istatistigi ===")
        for k, v in d.items():
            print("  %-26s %s" % (k, v))
        print("\n  Not: bu Reelyze'in KENDI analiz havuzu, bizim kanallarimiz degil.")
        return

    if a.nisler:
        ns = nisler()
        print("=== %d nis ===" % len(ns))
        for n in ns:
            print("  %-30s %-30s %s video" % (n["query"], n["slug"], n["count"]))
        return

    satirlar = []
    if a.nis:
        vs = nis(a.nis)
        for v in vs:
            v["nis"] = a.nis
        satirlar = vs
    elif a.hepsi:
        for n in nisler():
            try:
                vs = nis(n["slug"])
            except Exception as e:
                print("ATLANDI %s: %s" % (n["slug"], e))
                continue
            for v in vs:
                v["nis"] = n["slug"]
            satirlar.extend(vs)
            print("  %-28s %3d video" % (n["slug"], len(vs)))
            time.sleep(0.15)
    else:
        ap.error("--nisler, --nis, --hepsi veya --istatistik gerekli")

    benzersiz = list({r["url"]: r for r in satirlar}.values())
    benzersiz = normalize(benzersiz)

    if not benzersiz:
        print()
        print("SONUC YOK: 0 video dondu.")
        if a.nis:
            print("  '%s' gecerli bir slug mi? Listeyi gormek icin:" % a.nis)
            print("    python trend.py --nisler")
        return

    print()
    print("=== %d benzersiz video ===" % len(benzersiz))
    ust = sorted(benzersiz, key=lambda r: -(r.get("outlier_score") or 0))[:15]
    print("  %9s %7s %12s  %-20s %s" % ("skor", "sure", "izlenme", "yazar", "baslik"))
    for r in ust:
        print("  %9.1f %6.1fs %12s  %-20s %s" % (
            r.get("outlier_score") or 0, r.get("duration_seconds") or 0,
            "{:,}".format(int(r.get("views") or 0)),
            (r.get("author_handle") or "")[:20],
            (r.get("title") or "")[:44].replace("\n", " ")))

    print()
    print("  Not: outlier_score MUTLAK deger degil, siralama sinyali. Sure/performans")
    print("  sorusu icin 'nis_medyanina_kat' alanini kullan, ham skoru degil.")

    if a.cikti:
        json.dump(benzersiz, open(a.cikti, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print("\nyazildi: %s (%d kayit)" % (a.cikti, len(benzersiz)))


if __name__ == "__main__":
    main()
