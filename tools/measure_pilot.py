"""Uretilmis bir bolumu OLC: ortme olaylari, sifirlama araliklari, donmus vista, sure.

Kullanim:
    python -X utf8 tools/measure_pilot.py <bolum.mp4> [--fps 12] [--json cikti.json]

Numpy/opencv YOK: ffmpeg ham gri kareleri stdout'a verir, piksel matematigi saf Python.

NEDEN HAM KARE FARKI YETMEZ (Same Page turu 1, Codex bulgusu): el titremesi, parcaciklar ve
pozlama gurultusu pikselleri surekli oynatir, bu yuzden donmus bir vista ham farkla "hareketli"
gorunur. Cozum: kaba orneklem (32x56) + kare basina ortalama/kontrast normalizasyonu; boylece
parlaklik pompalamasi ve titresim degil, SAHNE ICERIGI olculur.

BILINEN SINIR (ep90/ep91 karsilastirmasinda olculdu): bu detektor "DUZ ve opak" ortmeyi
guvenilir bulur, ama DOKULU ama yine de her seyi gizleyen ortmeyi (kopuren su, kaynayan kabarcik,
yogun kar) KACIRIR, cunku o kareler yuksek uzamsal detay tasir. Yani rapor edilen ortme sayisi
bir ALT SINIRDIR, gercek sayi degildir. Bu yuzden sayiyi tek basina kanit sayma.

Bu script olcebildigini olcer. Anlamsal olcutler (ortucu ortam maddesi mi, kadraj kaydi mi,
yolcu tepki verdi mi) kontakt sayfasindan INSAN incelemesidir; plan bolum 5 boyle diyor.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

W, H = 32, 56           # kaba orneklem (9:16)
N = W * H
GAP_LIMIT = 3.2         # saniye: sifirlamalar arasi en buyuk izinli aralik
COVER_MAX = 0.45        # saniye: bir ortme en fazla bu kadar surebilir
FROZEN_LIMIT = 3.2      # saniye: anlamli icerik en fazla bu kadar sabit kalabilir

# ORTME TANIMI (klibe gore olcekli, sabit sayi degil):
# bir ortme, camin ICERIGINI kaybettigi karedir. Bunu iki kosulla olcuyoruz:
#   (a) uzamsal detay (std sapma) klibin MEDYANININ %60'inin altinda  -> sahne dokusu gitti
#   (b) ve ayrica mutlak bir tavanin altinda                          -> gercekten duz
# Boylece karanlik bir su altinda da, parlak bir firinda da ayni tanim calisir.
FLAT_REL = 0.60              # medyan sd'ye orani
FLAT_ABS = 32.0              # mutlak sd tavani
FROZEN_EPS = 0.055           # normalize edilmis kareler arasi ortalama fark esigi


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", str(path)],
                         capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except Exception:
        return 0.0


def frames(path, fps):
    """(ortalama, stdsapma, normalize_kare) listesi dondur."""
    cmd = ["ffmpeg", "-v", "error", "-i", str(path),
           "-vf", "fps=%s,scale=%d:%d,format=gray" % (fps, W, H),
           "-f", "rawvideo", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    out = []
    for i in range(len(raw) // N):
        buf = raw[i * N:(i + 1) * N]
        m = sum(buf) / N
        var = sum((b - m) ** 2 for b in buf) / N
        sd = var ** 0.5
        # normalize: ortalama ve kontrast cikarilir -> titresim/pozlama degil icerik kalir
        d = sd if sd > 1e-6 else 1.0
        norm = [(b - m) / d for b in buf]
        out.append((m, sd, norm))
    return out


def ndiff(a, b):
    return sum(abs(x - y) for x, y in zip(a, b)) / N


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--fps", type=float, default=12.0)
    ap.add_argument("--json", dest="js")
    a = ap.parse_args()

    path = Path(a.video)
    if not path.is_file():
        print("HATA: dosya yok: %s" % path)
        return 1

    dur = duration(path)
    fr = frames(path, a.fps)
    if len(fr) < 10:
        print("HATA: kare cikarilamadi (%d kare). Dosya bozuk olabilir." % len(fr))
        return 1
    step = 1.0 / a.fps

    # --- ortme olaylari: klibe gore "duz" ardisik kare bloklari
    sds = sorted(sd for _, sd, _ in fr)
    med_sd = sds[len(sds) // 2]
    thr = min(FLAT_ABS, med_sd * FLAT_REL)
    flags = [(sd < thr) for _, sd, _ in fr]
    covers, i = [], 0
    while i < len(flags):
        if flags[i]:
            j = i
            while j + 1 < len(flags) and flags[j + 1]:
                j += 1
            mid = fr[(i + j) // 2][0]
            covers.append((i * step, (j + 1) * step,
                           "KARANLIK" if mid < 90 else ("PARLAK" if mid > 150 else "DUZ")))
            i = j + 1
        else:
            i += 1

    # --- sifirlama araliklari (bas ve son sinir dahil)
    marks = [0.0] + [(s + e) / 2 for s, e, _ in covers] + [dur]
    gaps = [(marks[k], marks[k + 1], marks[k + 1] - marks[k]) for k in range(len(marks) - 1)]

    # --- donmus vista: normalize kareler arasi fark esigin altinda kalan en uzun blok
    diffs = [ndiff(fr[k][2], fr[k - 1][2]) for k in range(1, len(fr))]
    best, run, start = (0.0, 0.0, 0.0), 0, 0
    for k, d in enumerate(diffs):
        covered = any(s <= (k + 1) * step <= e for s, e, _ in covers)
        if d < FROZEN_EPS and not covered:
            if run == 0:
                start = k
            run += 1
            if run * step > best[0]:
                best = (run * step, start * step, (k + 1) * step)
        else:
            run = 0

    print("dosya            : %s" % path)
    print("sure             : %.2f s   (%d kare @ %.0f fps)" % (dur, len(fr), a.fps))
    print("detay (sd)       : min %.1f  medyan %.1f  -> ortme esigi %.1f" % (sds[0], med_sd, thr))
    print("ortme olayi      : %d" % len(covers))
    for s, e, kind in covers:
        print("   %6.2f-%6.2f s  %5.2f s  %s" % (s, e, e - s, kind))
    print("sifirlama araligi: en buyuk %.2f s (sinir %.1f)" %
          (max(g[2] for g in gaps) if gaps else 0.0, GAP_LIMIT))
    for s, e, g in gaps:
        if g > GAP_LIMIT:
            print("   ASIM %6.2f-%6.2f s -> %.2f s" % (s, e, g))
    print("donmus vista     : en uzun %.2f s (%.2f-%.2f s, sinir %.1f)" %
          (best[0], best[1], best[2], FROZEN_LIMIT))

    fails = []
    for s, e, g in gaps:
        if g > GAP_LIMIT:
            fails.append("sifirlama araligi %.2f s (%.2f-%.2f), sinir %.1f" % (g, s, e, GAP_LIMIT))
    for s, e, _ in covers:
        if e - s > COVER_MAX:
            fails.append("ortme %.2f s surdu (%.2f-%.2f), sinir %.2f" % (e - s, s, e, COVER_MAX))
    if best[0] > FROZEN_LIMIT:
        fails.append("donmus vista %.2f s (%.2f-%.2f), sinir %.1f" %
                     (best[0], best[1], best[2], FROZEN_LIMIT))
    if not covers:
        fails.append("hic ortme olayi bulunamadi")

    print()
    if fails:
        print("SONUC: BASARISIZ (%d)" % len(fails))
        for f in fails:
            print("  - %s" % f)
    else:
        print("SONUC: PILOT OLCUM OK")
    print("\nNOT: ortucunun ortam maddesi olup olmadigi, kadrajin kayip kaymadigi ve yolcularin"
          "\n     tepki verip vermedigi BU SCRIPT'LE OLCULEMEZ; kontakt sayfasindan gozle"
          "\n     dogrulanmasi zorunludur (plan bolum 5).")

    if a.js:
        Path(a.js).write_text(json.dumps({
            "duration": dur, "covers": [[s, e, k] for s, e, k in covers],
            "gaps": [[s, e, g] for s, e, g in gaps],
            "frozen": {"len": best[0], "start": best[1], "end": best[2]},
            "fails": fails}, ensure_ascii=False, indent=2), encoding="utf-8")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
