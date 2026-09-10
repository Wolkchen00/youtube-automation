"""Gunluk ogrenen beyin.

Kanal basina yayinlanan videolarin OLCUMLERINI ve SONUCLARINI bir deftere
biriktirir, sonra o defteri okuyup kanala ozel bir BEYIN.md yazar.
Kanal ajani her gun bu dosyayi okuyup yeni fikir uretir.

Sabit fikir havuzu YOK. Beyin her gun OLCULMUS sonuclardan yeniden yazilir.

    python beyin.py olc   <kanal>   yeni yayinlari olc, deftere ekle
    python beyin.py topla <kanal>   izlenme sayilarini tazele (zaman serisi)
    python beyin.py beyin <kanal>   defteri oku, BEYIN.md yaz

Kanal sluglari: unnatural-lab, event-horizon, flashpoints, aimagine-fear
"""
import argparse
import json
import os
import statistics as st
import sys
import tempfile
from datetime import datetime, timezone

KOK = os.path.dirname(os.path.abspath(__file__))
ARAC = os.path.join(KOK, "arac")

# Kanal ID leri. kanallarimiz.md ile ayni tutulmali.
KANALLAR = {
    "unnatural-lab": "UC-Aht8VqAUMTUKYRQA3agYQ",
    "event-horizon": "UCVCRWrQYrIHW6csOsw9bDNw",
    "flashpoints": "UCUdp0KLBh4EeeSgVbwS_DhA",
    "aimagine-fear": "UCCgbHTzYKYawUT6zEo0nlDg",
}

# Kanala ozel kural cikarmak icin gereken en az video sayisi.
# Altinda kalirsak HICBIR SEY iddia etmeyiz, genel esiklere duseriz.
ASGARI_N = 15

# Karsilastirilacak olcum alanlari: (defterdeki yol, gosterim adi, birim)
ALANLAR = [
    ("sure", "sure", "sn"),
    ("kesme_per_10sn", "kesme / 10 sn", ""),
    ("en_uzun_plan", "en uzun plan", "sn"),
    ("lufs", "ses seviyesi (LUFS)", ""),
]
UST_ALANLAR = [("wpm", "konusma hizi (WPM)", ""), ("kelime", "kelime sayisi", "")]

GENEL_ESIKLER = """- Integrated loudness hedefi: **-16 ila -13 LUFS**
- True peak tavani: **-1,0 dBTP** (ustu platform yeniden kodlamasinda bozulur)
- En uzun tek plan: **4 saniyeyi asmasin**
- Kesme araligi: **1,5-3 saniye**, pattern interrupt her 5-7 saniyede
- Ilk 1,5 saniyede ekran yazisi: **3-7 kelime**, ust-orta ucte bir, dip %15 yasak
- Sure: nis ici olcumde **kisa kazaniyor** (0-7 sn en iyi 1,69x; 90+ sn en kotu 0,65x)
- Sinyal sirasi: skip rate (ilk 3 sn) > shares > likes > saves > reposts > comments
- **Yorum orani begeni oranindan daha ayirt edici** (begeni skor dilimleri arasi sabit)"""


def simdi():
    return datetime.now(timezone.utc).isoformat()


def kanal_kok(kanal, kok=None):
    return os.path.join(kok or os.getcwd(), "kanallar", kanal)


def defter_yolu(kanal, kok=None):
    return os.path.join(kanal_kok(kanal, kok), "defter.jsonl")


def defter_oku(kanal, kok=None):
    """Bozuk satirlari ATLAR, cokmez. Atlanan sayisini da dondurur."""
    p = defter_yolu(kanal, kok)
    satirlar, bozuk = [], 0
    if not os.path.exists(p):
        return satirlar, bozuk
    with open(p, encoding="utf-8", errors="replace") as f:
        for ham in f:
            ham = ham.strip()
            if not ham:
                continue
            try:
                d = json.loads(ham)
            except Exception:
                bozuk += 1
                continue
            if isinstance(d, dict) and d.get("video_id"):
                satirlar.append(d)
            else:
                bozuk += 1
    return satirlar, bozuk


def defter_yaz(kanal, satirlar, kok=None):
    p = defter_yolu(kanal, kok)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        for d in satirlar:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")


def sayi(x):
    """Sadece gercek sayilari dondurur. None, bool ve metin ELENIR."""
    if isinstance(x, bool) or x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    return None


def alan(kayit, ad):
    """Once olcum icinde, sonra kok seviyesinde ara."""
    o = kayit.get("olcum")
    if isinstance(o, dict) and ad in o:
        return sayi(o.get(ad))
    return sayi(kayit.get(ad))


def izlenme(kayit):
    s = kayit.get("sonuc")
    if isinstance(s, dict):
        v = sayi(s.get("izlenme"))
        if v is not None:
            return v
    return sayi(kayit.get("rss_izlenme"))


# ---------------------------------------------------------------- olc

def komut_olc(kanal, limit=15):
    if kanal not in KANALLAR:
        sys.exit("Bilinmeyen kanal: %s\n  Gecerli: %s"
                 % (kanal, ", ".join(sorted(KANALLAR))))
    sys.path.insert(0, ARAC)
    try:
        from kanal import youtube_rss
        from olc import tek
    except Exception as e:
        sys.exit("arac/ modulleri yuklenemedi: %s" % e)

    mevcut, _ = defter_oku(kanal)
    bilinen = {d["video_id"] for d in mevcut}
    videolar = youtube_rss(KANALLAR[kanal], limit)
    yeni = [v for v in videolar if v["video_id"] not in bilinen]

    print("kanal: %s  |  RSS: %d video  |  yeni: %d"
          % (kanal, len(videolar), len(yeni)))
    if not yeni:
        print("olculecek yeni video yok.")
        return

    gecici = os.path.join(tempfile.gettempdir(), "gunluk-beyin")
    os.makedirs(gecici, exist_ok=True)

    for v in yeni:
        vid = v["video_id"]
        print("  olculuyor: %s  %s" % (vid, (v.get("baslik") or "")[:44]))
        try:
            r = tek("https://www.youtube.com/shorts/" + vid, gecici, False)
        except Exception as e:
            print("    HATA: %s" % e)
            continue
        if r.get("hata"):
            print("    ATLANDI: %s" % r["hata"])
            continue
        mevcut.append({
            "video_id": vid,
            "kanal": kanal,
            "tarih": v.get("tarih"),
            "baslik": v.get("baslik"),
            "olcum": r.get("olcum") or {},
            "kelime": r.get("kelime"),
            "wpm": r.get("wpm"),
            "sonuc": {"izlenme": v.get("rss_izlenme"), "begeni": None, "gecmis": []},
            "olculdu_ts": simdi(),
        })
        defter_yaz(kanal, mevcut)
    print("defter: %d kayit -> %s" % (len(mevcut), defter_yolu(kanal)))


# -------------------------------------------------------------- topla

def komut_topla(kanal):
    if kanal not in KANALLAR:
        sys.exit("Bilinmeyen kanal: %s" % kanal)
    sys.path.insert(0, ARAC)
    try:
        from kanal import youtube_canli
    except Exception as e:
        sys.exit("arac/kanal.py yuklenemedi: %s" % e)

    satirlar, bozuk = defter_oku(kanal)
    if not satirlar:
        print("defter bos, once 'olc' calistir.")
        return
    if bozuk:
        print("UYARI: %d bozuk satir atlandi." % bozuk)

    guncel = 0
    for d in satirlar:
        c = youtube_canli(d["video_id"]) or {}
        if not c.get("izlenme"):
            continue
        s = d.get("sonuc")
        if not isinstance(s, dict):
            s = {"gecmis": []}
            d["sonuc"] = s
        s.setdefault("gecmis", [])
        yas = None
        try:
            t0 = datetime.fromisoformat(str(d.get("tarih")) + "T00:00:00+00:00")
            yas = round((datetime.now(timezone.utc) - t0).total_seconds() / 3600, 1)
        except Exception:
            pass
        # Gecmisi EZME, ustune ekle. Zaman serisi boylece birikir.
        s["gecmis"].append({"ts": simdi(), "izlenme": c["izlenme"], "yas_saat": yas})
        s["izlenme"] = c["izlenme"]
        if c.get("begeni") is not None:
            s["begeni"] = c["begeni"]
        guncel += 1

    defter_yaz(kanal, satirlar)
    print("%d/%d kayit guncellendi -> %s" % (guncel, len(satirlar), defter_yolu(kanal)))


# --------------------------------------------------------------- beyin

def _karsilastir(ust, alt, ad, gosterim, birim):
    """Iki yarinin medyanini karsilastir. Veri yoksa None doner."""
    a = [alan(k, ad) for k in ust]
    b = [alan(k, ad) for k in alt]
    a = [x for x in a if x is not None]
    b = [x for x in b if x is not None]
    if len(a) < 3 or len(b) < 3:
        return None
    ma, mb = st.median(a), st.median(b)
    fark = ma - mb
    if abs(fark) < 1e-9:
        yon = "fark yok"
    elif fark > 0:
        yon = "ust yari DAHA YUKSEK"
    else:
        yon = "ust yari DAHA DUSUK"
    return ("| %s | %.2f%s | %.2f%s | %s | n=%d/%d |"
            % (gosterim, ma, birim, mb, birim, yon, len(a), len(b)))


def komut_beyin(kanal):
    satirlar, bozuk = defter_oku(kanal)
    n = len(satirlar)
    yeterli = n >= ASGARI_N

    yetersiz_cumle = (
        "**YETERSIZ VERI** (n=%d, en az %d gerekiyor). Bu kanala ozel kural "
        "cikarilamaz, asagidaki genel esikler kullanilmali." % (n, ASGARI_N)
    )

    L = []
    L.append("# BEYIN , %s" % kanal)
    L.append("")
    L.append("Uretim: %s" % simdi())
    L.append("Kaynak: `%s` (%d kayit)" % (defter_yolu(kanal), n))
    if bozuk:
        L.append("")
        L.append("> UYARI: defterde %d bozuk satir atlandi." % bozuk)
    L.append("")
    L.append("Bu dosya HER GUN yeniden yazilir. Sabit fikir havuzu yoktur.")
    L.append("")
    L.append("---")
    L.append("")

    # ---- 1. DURUM
    L.append("## 1. DURUM")
    L.append("")
    if n == 0:
        L.append("Defter bos. Once `python beyin.py olc %s` calistir." % kanal)
    else:
        izl = [izlenme(k) for k in satirlar]
        izl_v = [x for x in izl if x is not None]
        L.append("- Olculen video: **%d**" % n)
        if izl_v:
            L.append("- Medyan izlenme: **%s**" % "{:,.0f}".format(st.median(izl_v)))
            L.append("- Aralik: %s ile %s arasi"
                     % ("{:,.0f}".format(min(izl_v)), "{:,.0f}".format(max(izl_v))))
            sirali = sorted([k for k in satirlar if izlenme(k) is not None],
                            key=lambda k: -izlenme(k))
            L.append("")
            L.append("| | izlenme | tarih | baslik |")
            L.append("|---|---|---|---|")
            for etiket, k in (("EN IYI", sirali[0]), ("EN KOTU", sirali[-1])):
                L.append("| %s | %s | %s | %s |"
                         % (etiket, "{:,.0f}".format(izlenme(k)),
                            k.get("tarih") or "?", (k.get("baslik") or "?")[:48]))
            L.append("")
            L.append("Son yayinlar (tekrar etme):")
            for k in sorted(satirlar, key=lambda k: str(k.get("tarih") or ""),
                            reverse=True)[:5]:
                L.append("- %s , %s" % (k.get("tarih") or "?",
                                        (k.get("baslik") or "?")[:60]))
        else:
            L.append("- Izlenme verisi yok. `python beyin.py topla %s` calistir." % kanal)
    L.append("")

    # ---- 2. BU KANALDA NE ISE YARIYOR
    L.append("## 2. BU KANALDA NE ISE YARIYOR")
    L.append("")
    satir_karsilastirmalari = []
    if not yeterli:
        L.append(yetersiz_cumle)
    else:
        olculebilir = [k for k in satirlar if izlenme(k) is not None]
        if len(olculebilir) < ASGARI_N:
            L.append("**YETERSIZ VERI** (izlenmesi bilinen kayit n=%d, en az %d "
                     "gerekiyor). `topla` komutunu calistir." % (len(olculebilir), ASGARI_N))
        else:
            sirali = sorted(olculebilir, key=lambda k: -izlenme(k))
            orta = len(sirali) // 2
            ust, alt = sirali[:orta], sirali[-orta:]
            for ad, gosterim, birim in ALANLAR + UST_ALANLAR:
                s = _karsilastir(ust, alt, ad, gosterim, birim)
                if s:
                    satir_karsilastirmalari.append(s)
            if satir_karsilastirmalari:
                L.append("Videolar izlenmeye gore siralandi, ust yari ile alt yarinin")
                L.append("medyanlari karsilastirildi.")
                L.append("")
                L.append("| olcum | ust yari | alt yari | yon | n |")
                L.append("|---|---|---|---|---|")
                L.extend(satir_karsilastirmalari)
                L.append("")
                L.append("> **Korelasyon, nedensellik degil.** Bunlar yon gosterir,")
                L.append("> kanun degildir. Tek dogru sanma, hipotez olarak kullan.")
            else:
                L.append("Karsilastirilabilir olcum alani bulunamadi "
                         "(her alanda en az 3+3 gecerli deger gerekiyor).")
    L.append("")

    # ---- 3. GENEL ESIKLER
    L.append("## 3. GENEL ESIKLER")
    L.append("")
    L.append("Kanala ozel veri yetersizse veya celiskiliyse bunlar gecerli.")
    L.append("")
    L.append(GENEL_ESIKLER)
    L.append("")

    # ---- 4. BUGUN ICIN YON
    L.append("## 4. BUGUN ICIN YON")
    L.append("")
    if not yeterli or not satir_karsilastirmalari:
        L.append(yetersiz_cumle)
    else:
        L.append("2. bolumdeki farklardan cikan somut hedefler:")
        L.append("")
        oneri = []
        sirali = sorted([k for k in satirlar if izlenme(k) is not None],
                        key=lambda k: -izlenme(k))
        orta = len(sirali) // 2
        ust, alt = sirali[:orta], sirali[-orta:]
        for ad, gosterim, birim in ALANLAR + UST_ALANLAR:
            a = [alan(k, ad) for k in ust]
            a = [x for x in a if x is not None]
            b = [alan(k, ad) for k in alt]
            b = [x for x in b if x is not None]
            if len(a) < 3 or len(b) < 3:
                continue
            ma, mb = st.median(a), st.median(b)
            if abs(ma - mb) < 1e-9:
                continue
            oneri.append("- **%s**: ust yarinin medyani %.2f%s (alt yari %.2f%s). "
                         "Bugunku videoyu %.2f%s civarina hedefle."
                         % (gosterim, ma, birim, mb, birim, ma, birim))
        L.extend(oneri if oneri else ["- Anlamli fark bulunamadi."])
    L.append("")

    # ---- 5. KACIN
    L.append("## 5. KACIN")
    L.append("")
    # Kanalin EN IYI videosu bir esigi ihlal ediyorsa, o esik bu kanalda
    # gecersizdir. Kor uygulamak calisani bozar: olculmus ornek, filonun en iyi
    # kanalinin en uzun plani 17,85 sn olmasina ragmen en iyi olmasi.
    en_iyi = None
    _izl = [k for k in satirlar if izlenme(k) is not None]
    if _izl:
        en_iyi = max(_izl, key=izlenme)

    def _en_iyi_de_ihlal(ad, kosul):
        if not en_iyi:
            return False
        v = sayi((en_iyi.get("olcum") or {}).get(ad))
        return v is not None and kosul(v)

    celisen = []
    if _en_iyi_de_ihlal("en_uzun_plan", lambda v: v > 4.0):
        celisen.append(("Uzun statik plan",
                        "en uzun plan 4 sn tavani",
                        sayi((en_iyi.get("olcum") or {}).get("en_uzun_plan"))))
    if _en_iyi_de_ihlal("lufs", lambda v: not (-16.0 <= v <= -13.0)):
        celisen.append(("Ses seviyesi hedef disi", "LUFS -16..-13 hedefi",
                        sayi((en_iyi.get("olcum") or {}).get("lufs"))))
    celisen_turler = {t for t, _, _ in celisen}

    kacin = []
    for k in satirlar:
        o = k.get("olcum") or {}
        tp = sayi(o.get("true_peak"))
        lu = sayi(o.get("lufs"))
        ep = sayi(o.get("en_uzun_plan"))
        if tp is not None and tp > -1.0:
            kacin.append(("Ses kirpiyor",
                          "- **Ses kirpiyor**: `%s` true peak %.1f dBFS (tavan -1,0)"
                          % (k.get("video_id"), tp)))
        if lu is not None and not (-16.0 <= lu <= -13.0):
            kacin.append(("Ses seviyesi hedef disi",
                          "- **Ses seviyesi hedef disi**: `%s` %.1f LUFS (hedef -16..-13)"
                          % (k.get("video_id"), lu)))
        if ep is not None and ep > 4.0:
            kacin.append(("Uzun statik plan",
                          "- **Uzun statik plan**: `%s` en uzun plan %.1f sn (tavan 4,0)"
                          % (k.get("video_id"), ep)))
    # Kanalin kendi verisiyle celisen esikleri kusur olarak SUNMA.
    kacin = [(t, m) for t, m in kacin if t not in celisen_turler]

    if celisen:
        L.append("### Bu kanalda GECERSIZ esikler")
        L.append("")
        L.append("Asagidaki genel esikleri kanalin **en iyi videosu** de ihlal ediyor")
        L.append("(`%s`, %s izlenme). Yani bu kanalda o esik calismiyor."
                 % (en_iyi.get("video_id"),
                    "{:,.0f}".format(izlenme(en_iyi) or 0)))
        L.append("**Kor uygulama, calisan seyi bozarsin.**")
        L.append("")
        for _, ad, deger in celisen:
            L.append("- ~~%s~~ , en iyi videoda deger: **%.1f**" % (ad, deger))
        L.append("")

    if kacin:
        # Ayni kusurdan en fazla 3 ornek, rapor sismesin.
        gorulen = {}
        kirpilmis = []
        for tur, metin in kacin:
            gorulen[tur] = gorulen.get(tur, 0) + 1
            if gorulen[tur] <= 3:
                kirpilmis.append(metin)
        L.extend(kirpilmis)
        for tur, adet in sorted(gorulen.items()):
            if adet > 3:
                L.append("- _%s: toplam %d kayitta var, ilk 3 gosterildi._"
                         % (tur, adet))
    elif celisen:
        L.append("Kalan teknik esik ihlali yok.")
    elif n == 0:
        L.append("Veri yetersiz.")
    else:
        L.append("Olculen kayitlarda teknik esik ihlali yok.")
    L.append("")

    hedef = os.path.join(kanal_kok(kanal), "BEYIN.md")
    os.makedirs(os.path.dirname(hedef), exist_ok=True)
    with open(hedef, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print("yazildi: %s  (n=%d, %s)"
          % (hedef, n, "kanala ozel kural VAR" if yeterli else "YETERSIZ VERI"))


def main():
    ap = argparse.ArgumentParser(description="Gunluk ogrenen beyin")
    ap.add_argument("komut", choices=["olc", "topla", "beyin"])
    ap.add_argument("kanal")
    ap.add_argument("--limit", type=int, default=15,
                    help="olc: RSS'ten kac video taransin")
    a = ap.parse_args()

    if a.komut == "olc":
        komut_olc(a.kanal, a.limit)
    elif a.komut == "topla":
        komut_topla(a.kanal)
    else:
        komut_beyin(a.kanal)


if __name__ == "__main__":
    main()
