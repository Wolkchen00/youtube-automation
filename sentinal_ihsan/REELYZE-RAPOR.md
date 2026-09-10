# sentinal_ihsan , video analiz raporu

Tarih: 10 Eylul 2026 (Los Angeles)
Yontem: yt-dlp ile indirildi, ffmpeg/ffprobe + EBU R128 ile olculdu, kareler goz ile incelendi.
Metodoloji ve esikler: `Projeler/Reelyze_Arastirma/REELYZE-DOSYASI.md`

---

## 1. Kanal durumu , FILONUN EN IYISI

| | |
|---|---|
| Abone | 125 |
| Toplam video | 169 |
| Toplam izlenme | 121.729 |
| **30 gunluk medyan izlenme** | **1.292** |

Karsilastirma: `galactic_experiment` 88,5 , `shadowedhistory` 27 , `aimagine` 4.
**Bu kanal digerlerinden 15 ile 300 kat daha iyi.**

### Son yayinlar
| Video | Tarih | Izlenme |
|---|---|---|
| This NAPKIN Never ENDS! | 8 Eyl | **146** |
| This PLASTIC Bottle Turns To STONE! | 7 Eyl | 1.155 |
| Something Is WRONG With This SOAP | 4 Eyl | 1.499 |
| Something Is WRONG With This ICE CUBE | 2 Eyl | 1.306 |
| Something Is WRONG With This LEMON | 28 Agu | 1.406 |
| This SPONGE Is NOT Supposed To REPEL WATER?! | 23 Agu | 1.409 |
| This BRUSH Is NOT Supposed To HUM?! | 22 Agu | 498 |
| I Found UNNATURAL PAGES... And They STARTED To REPLICATE | 21 Agu | **82** |

Kalip cok net: **"This X Is NOT Supposed To Y" / "Something Is WRONG With This X"**
kalibi 1.100-1.500 aliyor. Kalip disina cikan iki video (`UNNATURAL PAGES` 82,
`NAPKIN Never ENDS` 146) cakiliyor.

---

## 2. Olculen teknik durum , FILODA TEK DOGRU AYARLI KANAL

| Video | Izlenme | Cozunurluk | fps | Sure | Kesme | En uzun plan | LUFS | True peak | WPM |
|---|---|---|---|---|---|---|---|---|---|
| Plastic Bottle (HIT) | 1.155 | 1080x1920 | 30 | 22,2 sn | 1 | 17,85 sn | **-14,4** | **-1,1** | 86 |
| Napkin (DUSEN) | 146 | 1080x1920 | 30 | 22,2 sn | 2 | 11,2 sn | **-14,3** | **-1,4** | 76 |
| Soap (HIT) | 1.499 | 1080x1920 | 30 | 16,6 sn | 1 | 11,01 sn | **-14,8** | **-1,4** | 62 |

Hedefler: LUFS -16 ila -13, true peak <= -1 dBTP.

**Ses seviyesi hedefin tam ortasinda ve true peak guvenli.** Filoda bunu tutturan
tek kanal bu. Ve filonun en iyi performans goesteren kanali da bu.

> Bu bir korelasyon, nedensellik kaniti degil. Ama olculmus bir ortuşme:
> ses seviyesi dogru olan tek kanal, performansi dogru olan tek kanal.
> Diger kanallarin ses duzeltmesi yapildiktan sonra bu tekrar olculmeli.

---

## 3. Neden calisiyor , korunmasi gereken formul

Kareye baktim (Plastic Bottle, ilk kare): bir el, mavi bir pet sise, sise tastan
bir dokuya donusuyor. Sade, aydinlik, gundelik ic mekan. **Tek net ozne, ilk karede
anomali gorunur durumda.**

Formul su:
1. **Gundelik nesne** (sise, sabun, buz kupu, limon, sunger, kalem, anahtar)
2. **Nesneye ait olmayan bir ozellik** (tasa donusuyor, suyu itiyor, dumanlaniyor)
3. **Anomali ILK KAREDE gorunuyor**, aciklamayi beklemiyor
4. Baslik anomaliyi dogrudan soyluyor, buyuk harfle nesneyi vurguluyor
5. 16-22 saniye
6. 62-86 WPM , yavas, net konusma
7. Ses -14 LUFS

Reelyze'in kanonik sinyal siralamasina gore bu tam isabet:
kanca ilk 3 saniyede kazaniliyor, cunku anomali ilk karede.

### Iki basarisiz video neden basarisiz
- `I Found UNNATURAL PAGES... And They STARTED To REPLICATE` (82): baslik anomaliyi
  degil bir HIKAYE ANLATIMINI vaat ediyor. "I Found..." kalibi izleyiciden sabir istiyor.
- `This NAPKIN Never ENDS!` (146): "never ends" gorsel bir anomali degil, soyut bir iddia.
  Sise tasa donusurken gozle gorulur; pecetenin bitmemesi ilk karede gosterilemez.

**Kural: anomali ILK KAREDE GORULEBILIR olmali.** Gorulemeyen anomali kalibi kiriyor.

---

## 4. Ne yapilmali

1. **Formulu bozma.** Bu kanalda yapilacak en degerli sey hicbir sey yapmamak.
   "This X Is NOT Supposed To Y" kalibina sadik kal.
2. **Konu havuzunu gorsel anomali filtresinden gecir.** Yeni konu eklerken tek soru:
   *"Bu anomali ilk karede gozle gorulur mu?"* Hayirsa havuza alma.
   (Ilgili risk: `family kilidi kanal olduruyor` , konu havuzu tukenirse kalip bozulur.)
3. **Diger kanallar bu kanali ornek alsin.** Ozellikle ses ayari ve "anomali ilk karede"
   kurali `galactic_experience` ve `shadowedhistory` icin dogrudan uygulanabilir.
4. **En uzun plan 17,85 saniye.** Kisa video kurallarina gore tavan 4 saniye.
   Bu kanal buna ragmen kazaniyor, cunku anomalinin kendisi pattern interrupt gorevi
   goeruyor. **Once A/B testi yapmadan kesme eklemeyin**, calisan seyi bozabilirsiniz.

## 5. Neye DOKUNMA

- Ses ayarlari. Filoda tek dogru olan bu, referans olarak kalsin.
- `could-you-survive/bible.json` ve `series.json` , kanal kimligini bunlar tutuyor.
- Ortak motor (`core/`, `series/`) , dort kanali birden besliyor.

## 6. Acik sorular (olculemedi)

- Retention egrileri (YouTube Studio gerekiyor)
- Bu kanalin TikTok/IG sayilari (olculmedi)
- 22 saniye mi 16 saniye mi daha iyi: Soap (16,6 sn) 1.499, Plastic Bottle (22,2 sn) 1.155.
  Tek ornek, sonuc cikarmak icin yetersiz. Kasitli bir sure A/B testi degerli olur.
