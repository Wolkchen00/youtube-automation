# idesignmedia.ai "Hollow Earth" kaydiragi, tersine muhendislik

Tarih: 2026-10-01. Kaynak: https://www.instagram.com/p/DdvYhkUEbxn/ (yayin 2026-09-26).
Indirilen dosya: `ref.mp4` (1080x1920, en yuksek dikey rendition). Olcum: `olcum.json`.
Kontakt sayfalari: `kontakt_1.jpg` (0-14,5 sn), `kontakt_2.jpg` (15-29 sn),
ek yeri yakin plan: `seam_bulut.jpg` (1,75-5,75 sn), `seam_magara.jpg` (14,5-21,5 sn).
Kiyas icin bizim 1 Ekim videomuz: `biz_eyfel.mp4`, `biz_kontakt.jpg`.

## Olculen teknik kimlik

| | Referans | Bizim Eyfel (1 Ekim) |
|---|---|---|
| Cozunurluk | 1080x1920 | 720x1280 |
| fps | 24 | 24 |
| Sure | 29,38 sn | 15,1 sn |
| Sert kesme (scene=0,3) | 0 | 0 |
| LUFS / true peak / LRA | -14,3 / -0,3 / 7,3 | -13,9 / -1,2 / 6,2 |
| Konusma | yok (whisper: tek yanlis "You", no_speech 0,86) | kadin sesi, 5 replik |
| Ilk 1 sn hareket (kareler arasi fark) | 10,1 | 0,9 |
| Ilk 3 sn ortalama hareket | 12,2 | 2,1 |

Begeni 118.573, yorum 558 (yorum/begeni %0,47). Izlenme olculmedi; begeniden
tahmin (%4-5,8 kurali, bu kanala uyup uymadigi bilinmiyor) ~2-3M, TAHMINDIR.

## Hangi model

Aciklamadaki kendi etiketi `#Seedance`. 1080p ve 24 fps Seedance 2.0 ciktisiyla uyumlu.
Seedance 2.0 tek uretimde en fazla 15 sn verir, video 29,38 sn. Yani **en az iki uretim
birlestirilmis**. Bu kesin (sure + model siniri). Ek yerinin TAM yeri kanitlanamadi, cunku
sert kesme yok; asagida aday yerler var.

## Zaman cizelgesi (2 kare/sn kontaktan)

| sn | Ne oluyor | Parlaklik / kontrast |
|---|---|---|
| 0,0-2,4 | Ilk karede ZATEN hareket var: bacaklar, seffaf kaydirak, gun batimi, bulut denizine dik inis | lum 115-130, std 47 |
| 2,4-5,2 | Bulutun ICI: neredeyse duz gri ekran, yalniz bacak golgesi | std 16 (kare neredeyse tek renk) |
| 5,2-8,5 | Bulutun altindan cikis: tavaninda gunes deligi olan dev magara, isik huzmeleri, karst tepeler, nehir | lum 70-79, hareket 3-6 (yavas acilis) |
| 8,5-11,5 | Brakiyozor kaydiragin ustunden boynunu uzatiyor, triseratops surusu yanda kosuyor | hareket 13-16 |
| 11,5-13 | Kaydirak selalenin kenarindan dusuyor | 12,0 sn ses tepe noktasi |
| 13-15 | Pterodaktil kameranin ustunden dalis, raptorler cikiyor | |
| 15-16 | Raptor kameraya atliyor, ekrani dolduruyor, hizli savrulma | hareket 22 (en yuksek) |
| 16-19,5 | Karanlik kristal magara, turkuaz parlayan kristaller, T-rex isik huzmesinde, kafasi kameranin yanindan geciyor | lum 27-38 |
| 19,5-20,5 | Parlak tunel agzi, isik objektifi dolduruyor | lum 33 -> 77 |
| 20,5-24 | Genis vadi: duman tuten yanardag, turkuaz nehir, sularda sauropod surusu, selaleler | hareket 6 (genis acilis) |
| 24-27 | Hiz artiyor, orman hareket bulanikligi | hareket 17-19 |
| 27-29 | T-rex agaclarin arasindan firliyor, agzi acik kameraya kosuyor, kamera AGZIN ICINE giriyor | ses en yuksek (-5,8 dB) |
| 29-29,4 | Siyah | |

**Ritim:** her 3-5 saniyede yeni bir sey. Sayilinca 9 ayri "acilis" var
(bulut, magara, brakiyozor, triseratops, selale, raptor, kristal magara, vadi, T-rex).
Bizim Eyfel'de 1 acilis var (sehir), sonra ayni sehir doner durur.

## Ek yeri adaylari (ek yeri = iki uretimin birlestigi an)

Uc "maske" bolgesi var. Hepsinde kare ya tek renk ya cok karanlik ya da cok parlak,
yani iki uretimin bitis ve baslangic karesi birbirine kolayca uyar:

1. **Bulut, 2,4-5,2 sn.** Kontrast std 16'ya dusuyor, ekran neredeyse duz gri.
   Icinde 3,46 sn ve 3,75 sn'de ani parlaklik siciramasi var (81->109, 75->104),
   ciplak gozle sicak bir isik parlamasi. Ihsan'in "bulutta ikinci videoya geciyor"
   gozlemiyle uyumlu. EN GUCLU ADAY.
2. **Raptor atlayisi, 15-16 sn.** Hayvan ekrani dolduruyor + savrulma. 15 sn sinirina denk.
3. **Karanlik magara ve parlak tunel, 16-20,5 sn.**

Olasi kurgu: 3 uretim (ornek: ~4 + ~15 + ~10 sn) ya da 2 uretim (15 + 14,4).
Hangisi oldugu olculemedi.

## Tutarliligi neden hic bozulmuyor (gozlem + olcum)

1. **Kamera hic degismiyor.** Butun video ayni POV: gogus hizasindan asagi, iki bacak
   kadrajin alt ucte birinde, kaydirak raylari ayni yerde. Uretim degisse de "kimlik"
   ayni kaliyor cunku tasinan tek sey bacak + ray.
2. **Yuz yok.** Kayacak kimlik yok. Bacaklar genel, ayirt edici isaret yok.
3. **Ek yerleri maskede.** Duz gri bulut, karanlik, parlak isik: iki uretimin
   uc uca gelmesi icin en kolay kareler.
4. **Ikinci uretim muhtemelen birincinin son karesinden baslatilmis** (ilk kare
   kilidi). Bu olculemedi ama Seedance'ta tutarli devam etmenin bilinen tek yolu bu.
   Bizde de var: `first_frame_url` (series/produce.py:509).

## Ses

Konusma yok. Ses efekt agirlikli: ruzgar, su, darbeler, kukremeler. Bas agirlikli
vuruslar olaylara oturuyor: 2,5 sn (buluta giris), 5,0 (cikis), 9,0 (brakiyozor),
12,0 (selale dususu), 15,0 (raptor), 18,5-19,0 (magarada T-rex), 21,0 (vadi),
27-28,5 (T-rex, en yuksek). Muzik var mi yok mu ses analiziyle ayirt edilemedi.

## Caption

> POV: the waterslide drops through the clouds and straight into a prehistoric Hollow
> Earth. 🌴🦖 Ancient jungles, massive waterfalls, dinosaurs trying to take you out at every
> turn, and the ride keeps accelerating until there is nowhere left to go except directly
> into a T. rex. Would you ride this?

Bitis sorusu "Would you ride this?" yorum istiyor. Bizim caption'lar duz cumle, soru yok.

## Tersine prompt (yeniden kurulmus, iki uretim varsayimiyla)

Bu metin ORIJINAL prompt degil; videodan geriye dogru kurulmus, ayni sonucu
uretmesi beklenen prompt. Seedance 2.0 icin zaman damgali.

### Uretim 1 (15 sn)

```
First-person POV on a transparent glass water slide, camera at chest height looking
straight down along the rider's two bare legs, which stay locked in the lower third of
the frame for the entire shot. Golden-hour sun, a sea of white cumulus far below.
One continuous shot, no cuts.

[0-2.5s] Already moving fast from the first frame. The slide plunges steeply downward
into the cloud sea, white mist bursting around the legs, the two metal rails converging
to a point inside the clouds.
[2.5-5s] Total immersion inside the cloud: flat grey-white murk, only the legs and the
faint rails readable. A warm glow grows somewhere below.
[5-8s] The slide punches out of the underside of the cloud into a colossal hollow-earth
cavern. A sunlit opening in the cavern ceiling pours god rays onto a prehistoric jungle
of karst peaks and a winding river. The slide keeps descending into it. Slow, wide reveal.
[8-11s] A Brachiosaurus rises beside the slide, its neck passing over the camera. A herd
of Triceratops runs alongside the slide.
[11-13s] The slide drops off the lip of a huge waterfall, spray across the lens.
[13-15s] A Pteranodon swoops low over the camera. Velociraptors burst from the ferns and
one lunges at the lens, jaws open, filling the frame as the slide whips past.

Audio: no voice. Wind, rushing water, splashes, deep impacts on every reveal,
dinosaur calls and roars.
```

### Uretim 2 (14,4 sn, ilk kare = uretim 1'in son karesi)

```
Same POV, same bare legs locked in the lower third, same transparent slide, one
continuous shot, no cuts.

[0-4s] The slide dives into a dark cave lit by glowing teal crystals and
bioluminescent mushrooms. A T-rex stands in a shaft of light ahead; its head swings past
the camera.
[4-5.5s] The slide climbs toward a bright tunnel mouth; light floods the lens.
[5.5-9s] Burst out high above a vast valley: a smoking volcano, a braided turquoise
river, herds of sauropods wading, waterfalls. Wide and slow.
[9-12s] Speed builds; jungle trees streak past in heavy motion blur.
[12-14.4s] A T-rex smashes through the trees ahead, charges straight at the camera with
its jaws wide open, and the camera goes directly into its mouth. Cut to black.

Audio: no voice. Rising speed wind, crashing trees, the loudest roar at the very end.
```

## Bizden farki, tek tabloda

| | Referans | Bizim kalip (son 16 video) |
|---|---|---|
| Baslangic | ilk karede dusus | 3,5 sn ayakta durma |
| Bulut | baska DUNYAYA kapi | ayni sehrin ustunde ortu |
| Acilis sayisi | 9 | 1 |
| Tehdit | canlilar kameraya saldiriyor | yalniz yukseklik |
| Bitis | T-rex yutuyor, siyah | havuza dusus, kahkaha |
| Ses | yalniz efekt | kadin sesi replikleri |
| Caption | soruyla bitiyor | duz cumle |
| Basliklar | , | son 16 basligin 10'u "..., into the cloud/fog/mist" kalibinda (yayin.jsonl) |
