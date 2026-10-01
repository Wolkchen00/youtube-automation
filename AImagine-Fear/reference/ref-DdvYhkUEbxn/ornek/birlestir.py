"""B30: iki 15 sn uretimi tek videoya birlestirir.

Ikinci uretim birincinin son karesinden basladigi icin ikisi de ek yerinde koyu gri
bulutun icinde. Birinci uretimin sonundaki bulut ~4 sn surup olu bekleme yapiyordu
(olculdu: 10,75-15,0 sn ust bolge std 21-27, yani duz gri). O yuzden birinci
--bir-son'da kesilir ve ikinciye bulutun icinde kisa capraz gecisle baglanir; duz gri
karede gecis gorunmez. Ses ayni noktada capraz gecer, sonra -14 LUFS'e cekilir.
Kullanim:
  python birlestir.py bir.mp4 iki.mp4 cikti.mp4 [--bir-son 12.0] [--iki-son 14.5] [--gecis 0.3]
"""
import argparse
import subprocess

ap = argparse.ArgumentParser()
ap.add_argument("bir")
ap.add_argument("iki")
ap.add_argument("cikti")
ap.add_argument("--bir-son", type=float, default=12.0, help="birinci uretim bu saniyede biter")
ap.add_argument("--iki-son", type=float, default=14.5, help="ikinci uretim bu saniyede biter")
ap.add_argument("--gecis", type=float, default=0.3, help="ek yerindeki capraz gecis, sn")
a = ap.parse_args()

ofset = a.bir_son - a.gecis
filtre = (
    "[0:v]trim=end={b},setpts=PTS-STARTPTS,fps=24,format=yuv420p[v0];"
    "[1:v]trim=end={i},setpts=PTS-STARTPTS,fps=24,format=yuv420p[v1];"
    # xfade cikisi yuv444p'ye kayiyor; Windows oynaticilari 4:4:4 h264'u acmiyor.
    "[v0][v1]xfade=transition=fade:duration={g}:offset={o},format=yuv420p[v];"
    "[0:a]atrim=end={b},asetpts=PTS-STARTPTS[a0];"
    "[1:a]atrim=end={i},asetpts=PTS-STARTPTS[a1];"
    "[a0][a1]acrossfade=d={g}[ax];"
    "[ax]loudnorm=I=-14:TP=-1.5:LRA=11[a]"
).format(b=a.bir_son, i=a.iki_son, g=a.gecis, o=ofset)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.bir, "-i", a.iki,
                "-filter_complex", filtre, "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-crf", "17", "-preset", "medium",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", a.cikti], check=True)
print("yazildi:", a.cikti)
