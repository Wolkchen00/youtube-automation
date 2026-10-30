"""Kaziyi isim listesi kaybolunca ayni listeyi parlak yazi olarak 3. saniyeye kadar tutar.

Kullanim: python isim_bindir.py <master.mp4> <cikti.mp4> <y_merkez_orani> Ad1,Ad2,...
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

giris, cikis, y_oran, isimler = Path(sys.argv[1]), Path(sys.argv[2]), float(sys.argv[3]), sys.argv[4].split(",")
G, Y = 720, 1280
FONT = "C:/Windows/Fonts/arialbd.ttf"
baslik_f = ImageFont.truetype(FONT, 42)
ad_f = ImageFont.truetype(FONT, 36)

yazi = Image.new("L", (G, Y), 0)
d = ImageDraw.Draw(yazi)
yarim = (len(isimler) + 1) // 2
satir = 42
blok_h = 60 + satir * yarim
ust = int(Y * y_oran - blok_h / 2)
d.text((G / 2, ust), "NEW FOLLOWERS", font=baslik_f, fill=255, anchor="mt")
for i, ad in enumerate(isimler):
    sutun_x = G / 2 - 120 if i < yarim else G / 2 + 120
    d.text((sutun_x, ust + 56 + satir * (i % yarim)), ad, font=ad_f, fill=255, anchor="mt")

# Gorsel kaziya benzesin: beyaz yazi, yumusak beyaz isik, altinda okunurluk icin hafif golge.
golge = yazi.filter(ImageFilter.GaussianBlur(5)).point(lambda v: min(255, int(v * 1.4)))
isik = yazi.filter(ImageFilter.GaussianBlur(10))
katman = Image.new("RGBA", (G, Y), (0, 0, 0, 0))
katman.paste((0, 0, 0, 255), mask=golge.point(lambda v: int(v * 0.55)))
isik_k = Image.new("RGBA", (G, Y), (255, 255, 255, 0))
isik_k.putalpha(isik.point(lambda v: int(v * 0.8)))
katman = Image.alpha_composite(katman, isik_k)
beyaz = Image.new("RGBA", (G, Y), (255, 255, 255, 0))
beyaz.putalpha(yazi)
katman = Image.alpha_composite(katman, beyaz)
png = cikis.with_suffix(".katman.png")
katman.save(png)

# 0,83 sn (24 fps 20. kare): Seedance kazili listeyi birakiyor (y merkezi ~0,72). Liste ayni yerde
# devralinir, 0,45 sn'de y_oran'a suzulur, 3. saniyenin sonunda soner.
BAS, SUZ, KAYMA = 0.82, 0.45, int((0.73 - y_oran) * Y)
filtre = (
    "[1:v]format=rgba,fade=t=out:st=2.85:d=0.35:alpha=1[k];"
    "[0:v][k]overlay=x=0:y='if(lt(t,%.2f),%d,if(lt(t,%.2f),%d*(1-(t-%.2f)/%.2f),0))'"
    ":enable='between(t,%.2f,3.25)':shortest=1,format=yuv420p[v]"
    % (BAS, KAYMA, BAS + SUZ, KAYMA, BAS, SUZ, BAS)
)
subprocess.run([
    "ffmpeg", "-v", "error", "-y", "-i", str(giris), "-loop", "1", "-framerate", "24", "-i", str(png),
    "-filter_complex", filtre, "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-preset", "slow",
    "-crf", "17", "-r", "24", "-c:a", "copy", "-movflags", "+faststart", str(cikis),
], check=True)
print("tamam", cikis)
