"""Kanal performansi: YouTube (RSS + canli sayfa), Instagram, TikTok.

RSS sayilari BAYAT olabilir, bu yuzden canli sayfayla karsilastirilir.
Instagram giris duvari veriyor ama og:description begeni/yorum siziyor.

Kullanim:
    python kanal.py --youtube UCxxxxxxxx
    python kanal.py --youtube UCxxxx --limit 8
    python kanal.py --ig-reel https://www.instagram.com/reel/XXXX/
    python kanal.py --tiktok https://www.tiktok.com/@kullanici/video/123
    python kanal.py --youtube UCxxxx --cikti kanal.json
"""
import argparse, html, json, re, time, urllib.request

UA = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/122.0 Safari/537.36"),
    "Accept-Language": "en-US,en;q=0.9",
}


def getir(url, timeout=45):
    try:
        return urllib.request.urlopen(
            urllib.request.Request(url, headers=UA), timeout=timeout
        ).read().decode("utf-8", "replace")
    except Exception as e:
        return "HATA:%s" % e


def sayi(s):
    s = s.replace(",", "").strip()
    m = re.match(r"^([\d.]+)([KMB]?)$", s)
    if not m:
        return None
    return int(float(m.group(1)) * {"": 1, "K": 1e3, "M": 1e6, "B": 1e9}[m.group(2)])


def arasi(h, bas, son='"'):
    i = h.find(bas)
    if i < 0:
        return None
    i += len(bas)
    j = h.find(son, i)
    return h[i:j] if j > i else None


def youtube_rss_ex(kanal_id, limit, deneme=3):
    """(satirlar, hata) dondurur. hata None ise besleme GERCEKTEN okundu.

    `youtube_rss` ag coktugunde de bos liste donduruyordu; cagiran taraf bunu
    "yeni video yok" saniyor ve exit 0 veriyordu. Yani ag tamamen kopukken
    gunluk kosu YESIL gorunuyordu. Hatayi ayirt edebilmek icin bu surum var.

    YENIDEN DENEME SART. Olculdu 2026-09-10: ayni kanala arka arkaya bes cagri
    yapildiginda ILKI 500 dondu, kalan dordu gecti. Tek denemede hatayi kirmizi
    saymak kosuyu neredeyse her gun gurultulu kirmizi yapardi; insan da kirmiziyi
    gormezden gelmeye baslardi, ki bu sessiz yesilden daha kotudur.
    """
    son_hata = None
    for i in range(max(1, deneme)):
        if i:
            time.sleep(1 + 2 * i)          # 1 sn, 3 sn
        xml = getir("https://www.youtube.com/feeds/videos.xml?channel_id=" + kanal_id)
        if xml.startswith("HATA:"):
            son_hata = xml[5:]
            continue
        if "<entry>" not in xml and "<feed" not in xml:
            # Sayfa geldi ama RSS degil (engel sayfasi, captcha, sema degisikligi).
            son_hata = "beslemenin sekli beklenmedik (%d bayt)" % len(xml)
            continue
        return _rss_ayristir(xml, limit), None
    return [], "%d denemede basarisiz , son hata: %s" % (deneme, son_hata)


def youtube_rss(kanal_id, limit):
    """Geriye uyum: sadece satirlari dondurur. Yeni kod `_ex` kullanmali."""
    return youtube_rss_ex(kanal_id, limit)[0]


def _rss_ayristir(xml, limit):
    satirlar = []
    for e in re.findall(r"<entry>(.*?)</entry>", xml, re.S)[:limit]:
        vid = re.search(r"<yt:videoId>([^<]+)</yt:videoId>", e)
        baslik = re.search(r"<title>(.*?)</title>", e, re.S)
        tarih = re.search(r"<published>([^<]+)</published>", e)
        izl = re.search(r'views="(\d+)"', e)
        if vid:
            ham_tarih = tarih.group(1) if tarih else ""
            satirlar.append({
                "video_id": vid.group(1),
                "baslik": html.unescape((baslik.group(1) if baslik else "").strip()),
                "tarih": ham_tarih[:10],
                # TAM zaman damgasi. Yas hesabi bunun uzerinden yapilmali:
                # sadece gun kullanilirsa gece 23:00'te yayinlanan video
                # 23 saat daha yasli sanilir ve 24 saat kapisi yanlis acilir.
                "yayin_ts": ham_tarih,
                "rss_izlenme": int(izl.group(1)) if izl else None,
            })
    return satirlar


def youtube_canli(vid):
    """RSS bayat olabilir, canli sayfadan gercek sayilari cek."""
    for u in ("https://www.youtube.com/shorts/" + vid,
              "https://www.youtube.com/watch?v=" + vid):
        h = getir(u)
        if h.startswith("HATA:"):
            continue
        m = re.search(r'"viewCount":"(\d+)"', h)
        if m:
            begeni = re.search(r'"likeCount":"(\d+)"', h)
            sure = re.search(r'"lengthSeconds":"(\d+)"', h)
            return {
                "izlenme": int(m.group(1)),
                "begeni": int(begeni.group(1)) if begeni else None,
                "sure_sn": int(sure.group(1)) if sure else None,
                "baslik": arasi(h, '<meta name="title" content="'),
                "etiketler": arasi(h, '<meta name="keywords" content="'),
            }
    return {}


def instagram(url, deneme=3):
    """Giris duvari var ama og:description begeni ve yorum siziyor.
    DIKKAT: begeni izlenme DEGIL. Hiz siniri var, aralarla cagir."""
    for i in range(deneme):
        h = getir(url)
        m = re.search(r'og:description" content="([^"]{0,300})', h or "")
        if m:
            d = html.unescape(m.group(1))
            out = {"ham": d[:140]}
            b = re.search(r"([\d.,]+[KMB]?)\s+likes", d)
            y = re.search(r"([\d.,]+[KMB]?)\s+comments", d)
            if b:
                out["begeni"] = sayi(b.group(1))
            if y:
                out["yorum"] = sayi(y.group(1))
            out["not"] = ("begeni izlenme DEGIL; olculen begeni orani izlenmenin "
                          "%4-5,8'i, tahmin icin kullan ve TAHMIN diye etiketle")
            return out
        time.sleep(6 + i * 6)
    return {"hata": "og:description alinamadi (hiz siniri veya giris duvari)"}


def tiktok(url):
    h = getir(url)
    if h.startswith("HATA:"):
        return {"hata": h[:90]}
    out = {}
    for ad, desenler in {
        "izlenme": [r'"playCount":(\d+)', r'"play_count":(\d+)'],
        "begeni": [r'"diggCount":(\d+)', r'"digg_count":(\d+)'],
        "yorum": [r'"commentCount":(\d+)', r'"comment_count":(\d+)'],
        "paylasim": [r'"shareCount":(\d+)', r'"share_count":(\d+)'],
    }.items():
        for p in desenler:
            m = re.search(p, h)
            if m:
                out[ad] = int(m.group(1))
                break
    return out or {"hata": "sayac bulunamadi"}


def main():
    ap = argparse.ArgumentParser(description="Kanal ve video performansi")
    ap.add_argument("--youtube", help="YouTube kanal ID (UC...)")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--ig-reel", action="append", default=[], help="IG reel URL")
    ap.add_argument("--tiktok", action="append", default=[], help="TikTok video URL")
    ap.add_argument("--cikti", help="JSON cikti dosyasi")
    a = ap.parse_args()

    sonuc = {}

    if a.youtube:
        satirlar = youtube_rss(a.youtube, a.limit)
        print("=" * 84)
        print("YouTube %s  (%d video)" % (a.youtube, len(satirlar)))
        print("  %-13s %10s %10s %8s %5s  %s" % (
            "video_id", "RSS", "CANLI", "begeni", "sn", "baslik"))
        for r in satirlar:
            c = youtube_canli(r["video_id"])
            r.update({"canli_" + k: v for k, v in c.items()})
            fark = ""
            if c.get("izlenme") and r.get("rss_izlenme"):
                kat = c["izlenme"] / max(r["rss_izlenme"], 1)
                if kat >= 2:
                    fark = "  <-- RSS %.0fx dusuk" % kat
            print("  %-13s %10s %10s %8s %5s  %s%s" % (
                r["video_id"],
                "{:,}".format(r["rss_izlenme"]) if r.get("rss_izlenme") else "-",
                "{:,}".format(c["izlenme"]) if c.get("izlenme") else "?",
                "{:,}".format(c["begeni"]) if c.get("begeni") else "-",
                c.get("sure_sn") or "-", r["baslik"][:38], fark))
        sonuc["youtube"] = satirlar

    if a.ig_reel:
        print("=" * 84)
        print("Instagram")
        sonuc["instagram"] = []
        for u in a.ig_reel:
            s = instagram(u)
            s["url"] = u
            sonuc["instagram"].append(s)
            print("  %-52s begeni=%s yorum=%s %s" % (
                u[-52:], s.get("begeni", "?"), s.get("yorum", "?"),
                s.get("hata", "")))
            time.sleep(5)

    if a.tiktok:
        print("=" * 84)
        print("TikTok")
        sonuc["tiktok"] = []
        for u in a.tiktok:
            s = tiktok(u)
            s["url"] = u
            sonuc["tiktok"].append(s)
            print("  %-52s izlenme=%s begeni=%s %s" % (
                u[-52:], s.get("izlenme", "?"), s.get("begeni", "?"),
                s.get("hata", "")))

    if a.cikti:
        json.dump(sonuc, open(a.cikti, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print("\nyazildi: %s" % a.cikti)


if __name__ == "__main__":
    main()
