"""Kisa video olcumu. yt-dlp ile indirir, ffmpeg/ffprobe ile olcer.

Reelyze'in ucretli kare-kare analizinin OLCULEBILIR kismini bedava uretir.

Kullanim:
    python olc.py https://www.youtube.com/shorts/XXXX
    python olc.py video.mp4 --kare
    python olc.py --liste ids.txt --cikti olcumler.json
"""
import argparse, json, os, re, subprocess, sys, tempfile

SAHNE_ESIGI = 0.30
KARE_ZAMANLARI = (0.0, 0.5, 1.0, 1.5, 3.0)


def sh(args, timeout=600):
    return subprocess.run(args, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)


def indir(url, klasor):
    """yt-dlp ile en yuksek kalitede indir, otomatik altyaziyi da al."""
    vid = re.sub(r"[^A-Za-z0-9_-]", "_", url)[-40:]
    mp4 = os.path.join(klasor, vid + ".mp4")
    if os.path.exists(mp4) and os.path.getsize(mp4) > 10000:
        return mp4, vid
    sh([sys.executable, "-m", "yt_dlp", "-f", "bv*+ba/b",
        "--merge-output-format", "mp4", "--write-auto-sub", "--sub-lang", "en",
        "--sub-format", "vtt", "--no-warnings",
        "-o", os.path.join(klasor, vid + ".%(ext)s"), url], timeout=900)
    if not os.path.exists(mp4):
        for uzanti in (".mkv", ".webm"):
            alt = os.path.join(klasor, vid + uzanti)
            if os.path.exists(alt):
                sh(["ffmpeg", "-y", "-i", alt, "-c", "copy", mp4])
                break
    return (mp4 if os.path.exists(mp4) else None), vid


def en_yuksek_rendition(url):
    """YouTube'un sundugu en yuksek DIKEY rendition. Gercek yayin kalitesi ipucu."""
    r = sh([sys.executable, "-m", "yt_dlp", "-F", "--no-warnings", url], timeout=240)
    en = (0, 0)
    for m in re.finditer(r"(\d{2,4})x(\d{2,4})", r.stdout or ""):
        g, y = int(m.group(1)), int(m.group(2))
        if y > g and y > en[1]:
            en = (g, y)
    return "%dx%d" % en if en[1] else None


def altyazi(klasor, vid):
    for f in os.listdir(klasor):
        if f.startswith(vid) and f.endswith(".vtt"):
            t = open(os.path.join(klasor, f), encoding="utf-8", errors="replace").read()
            t = re.sub(r"WEBVTT.*?\n\n", "", t, flags=re.S)
            t = re.sub(r"<[^>]+>", "", t)
            t = re.sub(r"^\d+\s*$", "", t, flags=re.M)
            t = re.sub(r"^[\d:.]+ --> .*$", "", t, flags=re.M)
            gorulen, satirlar = set(), []
            for L in t.split("\n"):
                L = L.strip()
                if L and L not in gorulen:
                    gorulen.add(L)
                    satirlar.append(L)
            return " ".join(satirlar)
    return None


def olc(mp4):
    o = {}
    r = sh(["ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate,codec_name",
            "-show_entries", "format=duration,size,bit_rate",
            "-of", "default=noprint_wrappers=1", mp4])
    f = dict(re.findall(r"^(\w+)=(.+)$", r.stdout, re.M))
    o["genislik"] = int(f["width"]) if f.get("width", "").isdigit() else None
    o["yukseklik"] = int(f["height"]) if f.get("height", "").isdigit() else None
    o["cozunurluk"] = "%sx%s" % (o["genislik"], o["yukseklik"])
    fr = f.get("r_frame_rate", "0/1")
    try:
        pay, payda = fr.split("/")
        o["fps"] = round(int(pay) / int(payda), 2) if int(payda) else None
    except Exception:
        o["fps"] = None
    o["kodek"] = f.get("codec_name")
    o["sure"] = round(float(f.get("duration", 0) or 0), 2)
    o["boyut_mb"] = round(int(f.get("size", 0) or 0) / 1e6, 2)

    ra = sh(["ffprobe", "-v", "error", "-select_streams", "a:0",
             "-show_entries", "stream=codec_name,channels,sample_rate",
             "-of", "default=noprint_wrappers=1", mp4])
    fa = dict(re.findall(r"^(\w+)=(.+)$", ra.stdout, re.M))
    if ra.returncode != 0:
        # ffprobe dustuyse "ses yok" SONUCU CIKARMA: ses olabilir de olmayabilir
        # de, bilmiyoruz. False demek, sessiz bir videoyu dogrulanmis gibi
        # gosterirdi ve LUFS'un neden olculmedigini yanlis acikardi.
        o["ses_var"] = None
        o.setdefault("hatalar", []).append(
            "ses akisi sorgulanamadi (ffprobe %d)" % ra.returncode)
    else:
        o["ses_var"] = bool(fa.get("codec_name"))
    o["ses_kanal"] = fa.get("channels")

    if o["ses_var"]:
        rl = sh(["ffmpeg", "-nostats", "-i", mp4, "-filter_complex",
                 "ebur128=peak=true", "-f", "null", "-"])
        tx = rl.stderr or ""

        def son(desen):
            m = re.findall(desen, tx)
            return float(m[-1]) if m else None
        o["lufs"] = son(r"I:\s*(-?\d+\.\d+)\s*LUFS")
        o["lra"] = son(r"LRA:\s*(-?\d+\.\d+)\s*LU")
        o["true_peak"] = son(r"Peak:\s*(-?\d+\.\d+)\s*dBFS")
        if rl.returncode != 0 and o["lufs"] is None:
            o.setdefault("hatalar", []).append(
                "ses seviyesi olculemedi (ffmpeg %d)" % rl.returncode)
    else:
        o["lufs"] = o["lra"] = o["true_peak"] = None

    rs = sh(["ffmpeg", "-nostats", "-i", mp4, "-filter_complex",
             "select='gt(scene,%s)',metadata=print:file=-" % SAHNE_ESIGI,
             "-an", "-f", "null", "-"])
    if rs.returncode != 0:
        # EN TEHLIKELI SESSIZ HATA. ffmpeg patlayinca `zamanlar` bos kaliyordu
        # ve "0 kesme" diye deftere giriyordu: makul gorunen, uygulanabilir,
        # UYDURMA bir deger. Olculemeyen sey olculemedi diye gecmeli.
        o["kesme_sayisi"] = o["kesme_per_10sn"] = None
        o["kesme_zamanlari"] = None
        o["en_uzun_plan"] = o["ort_plan"] = None
        o.setdefault("hatalar", []).append(
            "sahne tespiti basarisiz (ffmpeg %d): %s"
            % (rs.returncode, (rs.stderr or "")[-160:]))
        return o
    zamanlar = [round(float(x), 2)
                for x in re.findall(r"pts_time:(\d+\.?\d*)", rs.stdout or "")]
    o["kesme_sayisi"] = len(zamanlar)
    o["kesme_zamanlari"] = zamanlar
    o["kesme_per_10sn"] = round(len(zamanlar) / o["sure"] * 10, 2) if o["sure"] else None
    sinirlar = [0.0] + zamanlar + [o["sure"]]
    planlar = [round(sinirlar[i + 1] - sinirlar[i], 2) for i in range(len(sinirlar) - 1)]
    planlar = [p for p in planlar if p > 0]
    o["plan_uzunluklari"] = planlar
    o["en_uzun_plan"] = max(planlar) if planlar else None
    o["en_kisa_plan"] = min(planlar) if planlar else None
    o["ort_plan"] = round(sum(planlar) / len(planlar), 2) if planlar else None
    o["kesme_notu"] = ("scene=%s esigi su spreyini/flash'i kesme sanabilir, "
                       "su veya hizli hareket iceren videoda kareleri gozle dogrula"
                       % SAHNE_ESIGI)
    return o


def kareler(mp4, klasor, vid):
    yollar = []
    kok = os.path.join(klasor, "kareler")
    os.makedirs(kok, exist_ok=True)
    for t in KARE_ZAMANLARI:
        p = os.path.join(kok, "%s_t%s.jpg" % (vid, str(t).replace(".", "_")))
        sh(["ffmpeg", "-y", "-ss", str(t), "-i", mp4, "-frames:v", "1",
            "-q:v", "3", "-vf", "scale=430:-1", p], timeout=180)
        if os.path.exists(p) and os.path.getsize(p) > 500:
            yollar.append(p)
    return yollar


def tek(hedef, klasor, kare_iste):
    kayit = {"hedef": hedef}
    if re.match(r"^https?://", hedef):
        mp4, vid = indir(hedef, klasor)
        if not mp4:
            kayit["hata"] = "indirilemedi"
            return kayit
        kayit["en_yuksek_rendition"] = en_yuksek_rendition(hedef)
        kayit["desifre"] = altyazi(klasor, vid)
    else:
        mp4, vid = hedef, os.path.splitext(os.path.basename(hedef))[0]
        if not os.path.exists(mp4):
            kayit["hata"] = "dosya yok"
            return kayit
    kayit["olcum"] = olc(mp4)
    n = len((kayit.get("desifre") or "").split())
    kayit["kelime"] = n
    s = kayit["olcum"]["sure"]
    kayit["wpm"] = round(n / s * 60) if s and n else None
    if kare_iste:
        kayit["kareler"] = kareler(mp4, klasor, vid)
    return kayit


def yaz(k):
    if k.get("hata"):
        print("  HATA: %s" % k["hata"])
        return
    o = k["olcum"]
    print("  cozunurluk : %s   (YouTube max dikey: %s)" % (
        o["cozunurluk"], k.get("en_yuksek_rendition") or "?"))
    print("  fps        : %s        sure: %s sn" % (o["fps"], o["sure"]))
    print("  kesme      : %s  (%s/10sn)   en uzun plan: %s sn" % (
        o["kesme_sayisi"], o["kesme_per_10sn"], o["en_uzun_plan"]))
    if o["ses_var"]:
        print("  LUFS       : %s   true peak: %s dBFS   LRA: %s" % (
            o["lufs"], o["true_peak"], o["lra"]))
    else:
        print("  SES AKISI YOK")
    print("  desifre    : %s kelime, %s WPM" % (k.get("kelime"), k.get("wpm")))
    if k.get("kareler"):
        print("  kare       : %d adet -> %s" % (
            len(k["kareler"]), os.path.dirname(k["kareler"][0])))
    uyari = []
    if o["lufs"] is not None and not (-16.0 <= o["lufs"] <= -13.0):
        uyari.append("LUFS hedef disinda (-16..-13)")
    if o["true_peak"] is not None and o["true_peak"] > -1.0:
        uyari.append("true peak > -1 dBTP, KIRPMA RISKI")
    if o["en_uzun_plan"] and o["en_uzun_plan"] > 4.0:
        uyari.append("en uzun plan 4 sn tavanini asiyor")
    if uyari:
        print("  UYARI      : " + " | ".join(uyari))


def main():
    ap = argparse.ArgumentParser(description="Kisa video olcumu (yt-dlp + ffmpeg)")
    ap.add_argument("hedef", nargs="?", help="video URL veya yerel dosya")
    ap.add_argument("--liste", help="her satirda bir URL/dosya olan metin dosyasi")
    ap.add_argument("--kare", action="store_true", help="ilk kareleri cikar")
    ap.add_argument("--cikti", help="sonuclari bu JSON dosyasina yaz")
    ap.add_argument("--klasor", help="indirme klasoru (varsayilan: gecici)")
    a = ap.parse_args()

    hedefler = []
    if a.liste:
        hedefler = [L.strip() for L in open(a.liste, encoding="utf-8") if L.strip()]
    elif a.hedef:
        hedefler = [a.hedef]
    else:
        ap.error("hedef veya --liste gerekli")

    klasor = a.klasor or os.path.join(tempfile.gettempdir(), "reel-analiz")
    os.makedirs(klasor, exist_ok=True)

    sonuc = []
    for h in hedefler:
        print("=" * 70)
        print(h)
        k = tek(h, klasor, a.kare)
        yaz(k)
        sonuc.append(k)

    if a.cikti:
        json.dump(sonuc, open(a.cikti, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print("\nyazildi: %s" % a.cikti)


if __name__ == "__main__":
    main()
