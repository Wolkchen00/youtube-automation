"""routes/ altindaki her rotayi uretime girmeden once denetler.

Bu dosya olmadan rota kurallari yalniz _TEMPLATE.md yorumunda yaziyordu ve
kimse zorlamiyordu. Sessiz uyusmazlik gecmisi var: rota DURATION alani bir
sure hic okunmadi, 20 ve 25 saniyelik rotalar kirpildi.

Denetlenen kurallar:
  1. build.py'nin istedigi butun alanlar ve bolumler var
  2. SLUG dosya adiyla ayni ve build.py'nin SLUG_RE kalibina uyuyor
  3. DURATION tam sayi ve 15 (seedance-2 icin dogrulanmis tek sure)
  4. BEATS 0.0'dan DURATION'a bosluksuz, cakismasiz, en az 5 aralik
  5. NEON butun rotalarda BENZERSIZ
  6. LEGWEAR kanon metniyle birebir ayni (2026-09-14 Ihsan karari)
  7. OPENING/END STATE icinde "frame one" veya "final frame" yok
  8. CAPTION kazanan kalibi tutuyor ve etiketleri tam
  9. TITLE en az bir satir ve "#shorts" ile bitiyor
 10. VOICE zaman damgalari DURATION icinde kaliyor

Kullanim:
    python tools/rota_denetim.py            # hepsi
    python tools/rota_denetim.py <slug>     # tek rota
Cikis 0 temiz, 1 en az bir kural kirik.
"""

import io
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import build

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROUTES = os.path.join(KOK, "routes")
GUNLUK = os.path.join(KOK, "tools", "gunluk.py")

ALANLAR = ("SLUG", "DESTINATION", "LANDMARK", "DURATION", "NEON", "PALET",
           "TITLE_KEYWORD", "SEHIR_ISIGI", "LEGWEAR", "WEATHER", "SOURCE")
BOLUMLER = ("OPENING STATE", "BEATS", "END STATE", "VOICE", "CAPTION", "TITLE")

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ARALIK_RE = re.compile(r"^\[(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\]")

# 2026-09-14 Ihsan karari. Degistirilmez.
KANON_LEGWEAR = "a black high-cut one-piece swimsuit, legs bare from the hip down"
GEREKLI_ETIKETLER = ("#MegaSlideFear", "#WaterSlide", "#POVReels",
                     "#CGIAdventure")
GECERLI_SURE = 15

HATA = []
UYARI = []


def sira_oku():
    """gunluk.py'deki SIRA listesini oku.

    Uretime giren rotalar bunlar. Uretime hic girmeyen bir rotanin bulgusu
    cikis kodunu bozmamali: hep kirmizi yanan denetim gormezden gelinir ve
    o zaman gercek bir ariza da gozden kacar.
    """
    try:
        metin = io.open(GUNLUK, encoding="utf-8").read()
    except IOError:
        return None
    m = re.search(r"^SIRA = \[(.*?)^\]", metin, re.S | re.M)
    if not m:
        return None
    # Liste, kume DEGIL: "yan yana iki rota ayni rengi alamaz" kurali siraya
    # bakar. `slug in SIRA` uyelik testi listede de calisir.
    return re.findall(r'"([^"]+)"', m.group(1))


SIRA = sira_oku()


def hata(slug, mesaj):
    """SIRA'daki rotada BULGU, disindakinde UYARI."""
    satir = "%s , %s" % (slug, mesaj)
    if SIRA is None or slug in SIRA:
        HATA.append(satir)
    else:
        UYARI.append(satir)


def alanlari_oku(metin):
    alan = {}
    for satir in metin.split("\n"):
        if satir.startswith("## "):
            break
        m = re.match(r"^([A-Z][A-Z_]*):\s*(.*)$", satir)
        if m:
            alan[m.group(1)] = m.group(2).strip()
    return alan


def bolumleri_oku(metin):
    bolum = {}
    ad = None
    birikim = []
    for satir in metin.split("\n"):
        if satir.startswith("## "):
            if ad:
                bolum[ad] = "\n".join(birikim).strip()
            ad = satir[3:].strip()
            birikim = []
        elif ad:
            birikim.append(satir)
    if ad:
        bolum[ad] = "\n".join(birikim).strip()
    return bolum


def beats_dogrula(slug, govde, sure):
    araliklar = []
    for satir in govde.split("\n"):
        satir = satir.strip()
        if not satir:
            continue
        m = ARALIK_RE.match(satir)
        if m:
            araliklar.append((float(m.group(1)), float(m.group(2))))
        elif satir.startswith("["):
            hata(slug, "BEATS satiri okunamadi: %s" % satir[:40])

    if len(araliklar) < 5:
        hata(slug, "BEATS %d aralik, en az 5 olmali" % len(araliklar))
        return

    if abs(araliklar[0][0]) > 0.001:
        hata(slug, "BEATS %.1f'den basliyor, 0.0 olmali" % araliklar[0][0])
    if abs(araliklar[-1][1] - sure) > 0.001:
        hata(slug, "BEATS %.1f'de bitiyor, DURATION %d olmali"
             % (araliklar[-1][1], sure))

    for i in range(len(araliklar) - 1):
        bit = araliklar[i][1]
        bas = araliklar[i + 1][0]
        if abs(bit - bas) > 0.001:
            hata(slug, "BEATS %d ile %d arasinda kopukluk: %.1f -> %.1f"
                 % (i + 1, i + 2, bit, bas))

    for bas, bit in araliklar:
        if bit <= bas:
            hata(slug, "BEATS ters veya sifir aralik: [%.1f-%.1f]" % (bas, bit))


def voice_dogrula(slug, govde, sure):
    for satir in govde.split("\n"):
        satir = satir.strip()
        if not satir:
            continue
        m = ARALIK_RE.match(satir)
        if not m:
            if satir.startswith("["):
                hata(slug, "VOICE satiri okunamadi: %s" % satir[:40])
            continue
        bas, bit = float(m.group(1)), float(m.group(2))
        if bit > sure + 0.001:
            hata(slug, "VOICE %.1f'de bitiyor, DURATION %d'i asiyor" % (bit, sure))
        if bas < -0.001:
            hata(slug, "VOICE negatif zamanda basliyor: %.1f" % bas)


def rota_denetle(yol, neon_sahipleri):
    dosya = os.path.basename(yol)
    slug_dosya = dosya[:-3]
    metin = io.open(yol, encoding="utf-8").read()
    alan = alanlari_oku(metin)
    bolum = bolumleri_oku(metin)

    for a in ALANLAR:
        if a not in alan or not alan[a]:
            hata(slug_dosya, "eksik alan: %s" % a)
    for b in BOLUMLER:
        if b not in bolum or not bolum[b]:
            hata(slug_dosya, "eksik bolum: %s" % b)
    if HATA and any(h.startswith(slug_dosya + " , eksik") for h in HATA):
        return

    slug = alan["SLUG"]
    if slug != slug_dosya:
        hata(slug_dosya, "SLUG '%s' dosya adiyla ayni degil" % slug)
    if not SLUG_RE.fullmatch(slug):
        hata(slug, "SLUG kalibi bozuk, beklenen ^[a-z0-9]+(-[a-z0-9]+)*$")

    try:
        sure = int(alan["DURATION"])
    except ValueError:
        hata(slug, "DURATION tam sayi degil: %r" % alan["DURATION"])
        return
    if sure != GECERLI_SURE:
        hata(slug, "DURATION %d, uretime giren tek sure %d (seedance-2)"
             % (sure, GECERLI_SURE))

    neon = alan["NEON"].lower()
    if neon in neon_sahipleri:
        hata(slug, "NEON '%s' zaten %s rotasinda kullanilmis"
             % (neon, neon_sahipleri[neon]))
    else:
        neon_sahipleri[neon] = slug

    if alan["LEGWEAR"] != KANON_LEGWEAR:
        hata(slug, "LEGWEAR kanondan farkli (2026-09-14 karari degistirilemez)")

    for b in ("OPENING STATE", "END STATE"):
        dusuk = bolum[b].lower()
        for yasak in ("frame one", "final frame"):
            if yasak in dusuk:
                hata(slug, "%s icinde yasak ifade: '%s'" % (b, yasak))

    beats_dogrula(slug, bolum["BEATS"], sure)
    voice_dogrula(slug, bolum["VOICE"], sure)

    cap = bolum["CAPTION"]
    if not cap.lower().startswith("you're"):
        hata(slug, "CAPTION \"You're\" ile baslamiyor, kazanan kalip bu")
    for et in GEREKLI_ETIKETLER:
        if et not in cap:
            hata(slug, "CAPTION'da eksik etiket: %s" % et)
    dest = alan["DESTINATION"]
    if dest.lower() not in cap.lower():
        hata(slug, "CAPTION sehir adini (%s) gecmiyor" % dest)

    basliklar = [s for s in bolum["TITLE"].split("\n") if s.strip()]
    if not basliklar:
        hata(slug, "TITLE bos")
    for b in basliklar:
        if not b.strip().endswith("#shorts"):
            hata(slug, "TITLE satiri '#shorts' ile bitmiyor: %s" % b.strip()[:40])
    kw = alan["TITLE_KEYWORD"]
    if basliklar and not any(kw.lower() in b.lower() for b in basliklar):
        hata(slug, "hicbir TITLE satiri TITLE_KEYWORD '%s' icermiyor" % kw)


def uretim_kapilari():
    """Uretim is akisinin kendi kapilarini burada da kostur.

    2026-09-15'te sekiz rota bu betikle dogrulandi, betik TEMIZ dedi ve
    rotalar push edildi. Ama uretim is akisi baska iki kapi kosuyor,
    `build.py --check` ve `pytest AImagine-Fear/tests`, ve ikisi de
    KIRMIZIYDI. Kanal 16 ve 17 Eylul'de hic video cikaramadi.

    Bu betigin yesil yanip uretimin kirmizi yanmasi bir daha olmasin diye
    ayni iki kapi buradan da cagriliyor. build.py --check out/ altini
    yeniden URETIR (deterministik), yani bu betik artik salt okunur degil.
    """
    sorun = []
    for ad, komut in (
        ("build.py --check", [sys.executable, "-X", "utf8",
                              os.path.join(KOK, "build.py"), "--check"]),
        ("pytest tests", [sys.executable, "-X", "utf8", "-m", "pytest",
                          os.path.join(KOK, "tests"), "-q"]),
    ):
        try:
            sonuc = subprocess.run(komut, cwd=KOK, capture_output=True, text=True)
        except OSError as hata_:
            sorun.append("%s kosturulamadi: %s" % (ad, hata_))
            continue
        if sonuc.returncode != 0:
            govde = (sonuc.stdout or "") + (sonuc.stderr or "")
            satirlar = [s for s in govde.splitlines() if s.strip()][-12:]
            girinti = "\n    "
            sorun.append("%s KIRMIZI (cikis %d):%s%s"
                         % (ad, sonuc.returncode, girinti,
                            girinti.join(satirlar)))
    return sorun


def renk_ardisikligi_denetle():
    """SIRA'da yan yana iki rota ayni sehir-isigi AILESINI alamaz.

    Ihsan'in sikayeti "kanal hep ayni renkler oluyor" idi ve 2026-09-17
    olcumu dogruladi: yayinlanan alti videonun dordunde baskin ton amberdi.
    Sebep kanonda sabit yazan "warm amber" sehir isigiydi; POV asagi baktigi
    icin kareyi sehir dolduruyor, ince neon serit degil.

    Renk artik rota basina secilebiliyor, ama secilebilir olmasi yetmez:
    arka arkaya iki amber rota yazilirsa izleyici yine ayni kanali gorur.
    Kural siraya bakar, tek tek rotaya degil, o yuzden burada denetlenir.
    Liste dairesel: son rotadan basa donen komsuluk da sayilir.
    """
    if not SIRA:
        return
    aile = {}
    for slug in SIRA:
        yol = os.path.join(ROUTES, slug + ".md")
        try:
            alan = alanlari_oku(io.open(yol, encoding="utf-8").read())
        except IOError:
            continue
        aile[slug] = build.sehir_isigi_ailesi(alan.get("SEHIR_ISIGI", ""))
    sirali = [s for s in SIRA if s in aile]
    for i, slug in enumerate(sirali):
        sonraki = sirali[(i + 1) % len(sirali)]
        if aile[slug] and aile[slug] == aile[sonraki]:
            hata(slug, "SIRA'da bir sonraki rota (%s) ayni renk ailesini "
                       "kullaniyor: %s , yan yana iki video ayni renkte cikar"
                       % (sonraki, aile[slug]))


def main():
    hedef = sys.argv[1] if len(sys.argv) > 1 else None
    yollar = sorted(
        os.path.join(ROUTES, f) for f in os.listdir(ROUTES)
        if f.endswith(".md") and not f.startswith("_"))
    if hedef:
        yollar = [y for y in yollar if os.path.basename(y)[:-3] == hedef]
        if not yollar:
            print("rota bulunamadi: %s" % hedef)
            return 1

    neon_sahipleri = {}
    for y in yollar:
        rota_denetle(y, neon_sahipleri)

    # Tek rota denetlenirken de kosar: renk ardisikligi rotanin kendi ici
    # degil, SIRA'nin ozelligidir ve tek rota degistirmek onu bozabilir.
    renk_ardisikligi_denetle()

    print("denetlenen rota: %d" % len(yollar))
    print("benzersiz NEON: %d" % len(neon_sahipleri))
    if SIRA is None:
        print("UYARI: gunluk.py SIRA listesi okunamadi, hepsi uretimde sayildi")
    else:
        print("SIRA'da (uretime giren): %d" % len(SIRA))

    if UYARI:
        print("-" * 58)
        print("UYARI: %d bulgu, SIRA DISI rotalarda. Uretimi etkilemez." % len(UYARI))
        for u in UYARI:
            print("  ~ %s" % u)

    # Tek rota denetlenirken de tam kapi kosar: kelime tavani ve baslik
    # kesme kurallari rotalar arasi degil, dosya ici kurallardir ve asil
    # uretimi durduran da bunlardi.
    kapi_sorunlari = uretim_kapilari()

    print("=" * 58)
    if HATA or kapi_sorunlari:
        if HATA:
            print("SONUC: %d BULGU, uretime giren rotalarda" % len(HATA))
            for h in HATA:
                print("  - %s" % h)
        for k in kapi_sorunlari:
            print("  - %s" % k)
        return 1
    print("SONUC: TEMIZ. Rota kurallari ve uretim kapilari (build --check,")
    print("       pytest) birlikte gecti.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
