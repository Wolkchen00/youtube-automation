# Kontakt sayfalari , elle gerceklik denetimi (2026-09-01)

Uretildigi yontem (yeniden uretilebilir):

    python -m yt_dlp -f "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b" -o "<id>.%(ext)s" \
      "https://www.youtube.com/watch?v=<id>"
    ffmpeg -i "<id>.mp4" -vf "fps=20/<sure>,scale=300:-1,tile=5x4" -frames:v 1 "<id>_sheet.jpg"

| dosya | video id | bolum | yayin (UTC) | izlenme | begeni | sure |
|---|---|---|---|---|---|---|
| vKus2kyMIN0_sheet.jpg | vKus2kyMIN0 | part 22 "Something Is WRONG With This LEMON" | 2026-08-28T21:05:46Z | 1392 | 7 | 22,27 sn |
| 5PG5IbbivE0_sheet.jpg | 5PG5IbbivE0 | part 21 "This SPONGE Is NOT Supposed To REPEL WATER?!" | 2026-08-23T19:12:45Z | 1407 | 10 | 22,27 sn |

Her sayfa 5x4 = 20 kare, video boyunca esit araliklarla.

## Gozlem (RF-PLAN-SENTINAL-DIRILIS.md bolum 2.2)

- **part 22:** cekim 1-2 koyu benekli tezgah + sicak tungsten isik; cekim 3-4 acik renkli
  BASKA bir tezgah + soguk gun isigi, kamera belirgin geride. Planda dort cekimin dordu de
  `environment: kitchen_counter`. El anatomisi iyi , sorun anatomi degil, sahne butunlugu.
- **part 21:** anomali net okunuyor ve escalation gercek (formatin dogru hali). Ama dort
  cekim dort ayri mekanda geciyor; yuz 4 cekimin 3'unde gorunuyor ve bir karede agiz acik
  "vay be" tepkisi var. (part 21 ESKI semayla planlandi: `face_visible=None`, cekimlerde
  `environment` alani yok. part 22'de yuz kurali tuttu.)

Kaynak videolar repoya konmadi (boyut); yukaridaki komutlarla kimlikten yeniden indirilebilir.
