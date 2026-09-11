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

---

# EK: Konsept arastirmasi , 10 Eylul 2026

Sebep: Ihsan'in karari, "izlenmeler 1.5k gecmiyor, baska konsept bulmaliyiz".
Yontem: Reelyze bedava trend indeksi (1204 kayit), YouTube arama (10 sorgu),
yt-dlp ile kanal olcumu (16 aday), ffmpeg ile video olcumu (3 video, 2 kanal).

## 1. Reelyze nis indeksi bu soruyu CEVAPLAYAMIYOR

52 nisin tam listesi tarandi: oddly-satisfying, ASMR, bilim, merak, illuzyon,
deney ya da AI-gorsel diye bir nis YOK. Liste tamamen creator-economy, yemek,
fitness, guzellik, ev ve finans. Bu indeksten bizim alanimiz hakkinda sonuc
cikarilamaz. Cikarilirsa uydurma olur.

Nisten BAGIMSIZ gecerli tek bulgu: 1063 yazarin yalniz 26'si (%2,4) uc veya daha
fazla aykiri video cikarmis. Viral kisa videolarin %97,6'si TEK SEFERLIK.
Tekrarlayan yazarlarin yorum orani %0,058, tek seferliklerin %0,045.
Tekrarlanabilir format hem nadir hem daha baglayici.

## 2. Bizim yaptigimiz isi birebir yapan kanallar da olu

yt-dlp ile olculdu (abone = channel_follower_count, medyan = son 25 Shorts):

| Kanal | Abone | Medyan izlenme |
|---|---|---|
| Impossible Materials ASMR | 9 | 986 |
| MICOMIX | 9 | 1.200 |
| Yumeji Prismatica | 2 | 185 |
| **sentinal_ihsan (biz)** | **125** | **1.292** |

"AI ile imkansiz malzeme" alani kalabalik ve donusumsuz. Biz bu kumede en
iyisiyiz, ama kume olu.

## 3. Komsu alanda tavan 1,5k DEGIL

| Kanal | Abone | Medyan | En iyi |
|---|---|---|---|
| SatisVid | 256.000 | 63.000 | 287.000 |
| MessyLab | 35.000 | 55.000 | 243.000 |
| SatisfAI | 11.200 | 5.400 | 515.000 |

MessyLab ve SatisVid bizim medyanimizin 42-49 kati. Yani 1,5k nis tavani degil.

## 4. Kazananlarin yaptigi, bizim yapmadigimiz uc sey

Baslik ornekleri:
- MessyLab: "Choose your floating bed part2 | Which one would you dare to..."
  Seri halinde: 94k, 155k, 79k, 53k, 59k. Tutarli.
- SatisVid: "No Talking Just Slime ASMR", "Top 5 Neon Fruit Cuts AI ASMR"
- SatisfAI: "What's Hiding Inside These Fruits?!"

Bizim seviyemizdekiler: "Cutting a Pomegranate Reveals a Red Planet City",
"That Cut Was PERFECT". Tek seferlik merak, soru yok, seri yok, katilim yok.

Ayrim OZNE degil, KAP:
1. **Katilim.** Izleyiciye soru soruluyor, cevap yoruma yaziliyor.
2. **Acik serilestirme.** part2, part3 , devami geleceginin vaadi.
3. **Ses urunun kendisi.** Baslikta acikca "No Talking".

## 5. Teknik olcum , uc video, iki kanal

| Video | Izlenme | Cozunurluk | Sure | Kesme | LUFS | True peak | Kelime |
|---|---|---|---|---|---|---|---|
| MessyLab part2 | 155.000 | 2160x3840 | 22,8 | 0 | -21,4 | +0,6 | 0 |
| MessyLab part3 | 94.000 | 2160x3840 | 22,5 | 0 | -23,9 | 0,0 | 0 |
| SatisVid | 32.000 | 1080x1920 | 29,7 | 1 | -31,8 | -4,8 | 0 |
| **biz (Plastic Bottle)** | **1.155** | 1080x1920 | 22,2 | 1 | -14,4 | -1,1 | ~32 |

Ucunde de SIFIR anlatim.

**Bu "ses seviyesi onemsiz" DEMEK DEGILDIR.** Bunlar ASMR kanallari; sessiz
olmak o turun konvansiyonu, izleyici sesi kendi aciyor. Dogru okuma: biz
konusan-icerik standardina (-14 LUFS, voiceover onde) gore masterliyoruz ama
sessiz-samimi ses konvansiyonu olan bir turde yarisiyoruz.

Raporun 2. bolumundeki ses-performans ortusmesi "korelasyon, nedensellik degil"
diye dogru etiketlenmisti. Iste karsi ornegi: sesi bizim standardimiza gore
YANLIS olan (-21,4 LUFS, +0,6 dBTP kirpma) bir kanal 42 kat izlenme aliyor.

## 6. Motor fizibilitesi , anlatimsiz seri DESTEKLENIYOR

- `series/bible.py:323` `native_audio()` var, varsayilan True.
- `series/bible.py:480`: "anlatimsiz serilerde kullan (music:true + narration'siz bible)".
- `series/critic.py` ham native ses denetimi yapiyor (`native_audio_review`).
- unnatural-lab QC'si zaten `native_audio_review: true`.

4 cekim x 6 saniye yapisi "Choose your X" formatina neredeyse birebir oturuyor:
her cekim bir secenek.

## 7. Olculemeyenler

- Motorun urettigi native sesin ASMR kalitesi. OLCULMEDI ve en kritik bilinmeyen.
- 4K yolu: MessyLab 4K yayinliyor, bizde upscale kapali (ISSUES: Topaz kirilgan).
- Retention egrileri (YouTube Studio gerekiyor).
- 7 aday kanal cekilemedi (RandomAI, ZestLensASMR, JellyVerse AI, Dreamy ASMR,
  Velor AI Art, Which World?, Walter's Puppet Box).

---

# EK 2: AI KARAKTER turu , dogru referans sinifi bulundu

Ihsan'in tarifi: "urun tanitimi yapan ai videolar karakterler gibi veya
firtinada muz yemege calisan kadin ai karakterler".

## Referans kanal: The World According to AI

https://www.youtube.com/@AWorldAccordingToAI , 242.000 abone.
Son 29 Shorts: medyan 79.000, ortalama 217.513, en iyi 2.100.000, en dusuk 2.900.

Bizim medyanimiz 1.292. Yani 61 kat.

## Yapisal bulgu: TEKRAR EDEN KARAKTER motor, tek seferlik karakter oluyor

Bigfoot videolari (12 adet): 52k, 122k, 65k, 50k, 70k, 108k, 58k, 107k,
172k, 1.100.000, 439k, 114k. Medyan ~106k.

Tek seferlik karakterler:
- Triceratops: 2.900 (kanalin EN KOTUSU)
- Ape surfing: 34k

Baslik kalibi: "Bigfoot VLOG. Cooking burgers", "Bigfoot cooks steak on his
cooking show", "Bigfoot VLOG 1 / VLOG 2. Building a log cabin".
Karakter adi + sirradan eylem + "VLOG" + numara.

Abone olma sebebi bu: izleyici BIGFOOT'u takip etmek icin abone oluyor.
Bizim formatimizda takip edilecek bir sey yok, her bolum kendi kendine bitiyor.

## Teknik olcum (ffmpeg)

| Video | Izlenme | Cozunurluk | Sure | Kesme | En uzun plan | LUFS | Kelime | WPM |
|---|---|---|---|---|---|---|---|---|
| Bigfoot mantar | 1.100.000 | 1080x1920 | 8,0 | 0 | 8,0 | -26,3 | 14 | 105 |
| Bigfoot kulube | 439.000 | 1080x1920 | 20,3 | 2 | 8,0 | -26,0 | 49 | 145 |
| biz (Plastic Bottle) | 1.155 | 1080x1920 | 22,2 | 1 | 17,8 | -14,4 | ~32 | 86 |

Cozunurluk BIZIMLE AYNI. 4K gerekmiyor.
1,1 milyonluk video TEK 8 saniyelik cekim, sifir kesme, tek uretim.
Plan uzunlugu 8 sn: Veo'nun dogal klip boyu, bizim motorda da mevcut.

## Gorsel olcum (kare cikarildi, goz ile bakildi)

1,1 milyonluk videonun uretim ozellikleri:
- SELFIE/VLOG kadraji, karakter kamerayi kendi tutuyor, kol mesafesi
- Karakter KAMERAYA KONUSUYOR, dudak senkronlu
- GOMULU KARAOKE ALTYAZI, kelime kelime kirmizi vurgu
- Orman, dogal isik, tek plan

## Bu bizim doktrinimizin madde madde tersi

unnatural-lab `bible.json` briefi:
- "TELEFON POV, SELFIE ve KOL MESAFESI kavramlari IPTAL EDILMISTIR"
- "Karakter KAMERADA asla konusmaz, dudak oynatmaz, agzi kapalidir"
- "cekim prompt'u ekrana bindirilmis altyazi, baslik, grafik TARIF ETMEZ"

Referans video ucunu de yapiyor. Bu kurallar YANLIS DEGIL, el+obje formati
icin olcumle turetilmisti. Karakter formatina gecilirse ucu de dusmeli.

## Motor fizibilitesi , format destekleniyor

| Gereken | Durum |
|---|---|
| Sabit karakter kimligi | `bible.characters[0].character_id` ve `ref_image_url` KAYITLI |
| 8 sn tek cekim | `series/replenish.py` VALID_DURATIONS icinde "8" var |
| Kameraya konusma | `bible.py:323 native_audio()` |
| Gomulu altyazi | `core/ffmpeg_tools.py::fact_captions_overlay` |
| Yuz acik | `face_visible`, `omit_character_refs`, `qc.require_no_face` bayraklari |

Maliyet: 1,1 milyonluk video tek uretim. Bizim 4 cekimlik bolum ~615 kredi
(~3,08 dolar); tek 8 sn cekim bunun dortte biri.

## Kendi kanalimizin verisi (yt-dlp, 173 Shorts)

| | n | Medyan | En iyi |
|---|---|---|---|
| unnatural-lab (yuzsuz) | 23 | 1.100 | 2.600 |
| kanalin geri kalani | 150 | 745 | 3.300 |

Kanal 173 videoda hic 3.300'u gecmemis. Yuz-onde AI icerik ZATEN denenmis
(ornek: "I Tried to Carve a PERFECT Jell-O Cube", kare cikarildi, Ihsan'in
AI karakteri kadrajda) ve yuzsuz seriyi GECMEMIS.

Sonuc: sorun ne yuz ne konsept tek basina. Eksik olan TEKRAR EDEN KARAKTER
ve onun etrafinda kurulan seri vaadi.

## Olculemedi

- Instagram: og:description giris duvarina takildi, IG sayilari CIKARILAMADI.
  Hesaplar: zachking, ur_smartmaker, bluelightningtv.
- "Firtinada muz yiyen kadin" videosunun kendisi bulunamadi; tur dogru tespit
  edildi ama o spesifik video/kanal olculmedi.
- Motorun uretecegi karakterin dudak senkronu ve konusma kalitesi OLCULMEDI.

---

# EK 3: Codex arastirmasi ve DENETIMI , 10 Eylul 2026

Codex'e sistematik olcum harness'i yazdirildi (204 kanal, 933 Shorts).
Asagidakiler Codex'in raporundan DEGIL, dataset.json'in kendi denetimimden gelir.

## Codex'in ilk sonucu YANLISTI, sebebi olcum artefakti

Codex ilk turda "tekrar eden karakter hipotezi olcekte desteklenmedi,
23 kanalda medyan fark 0 puan" dedi. Denetim bunu curuttu:

- `recurring_character_name` ozelligi 897 videonun 51'inde atesliyordu (%5,7).
- 23 kanalin 20'sinde ozellik HEM isabet HEM iska kumesinde SIFIR kez atesledi.
  Bunlar "berabere" degil, OLCUM YOKLUGU. Kanit tabani n=23 degil n=3 idi
  (1 destekleyen, 1 curuten, 1 esit).
- Ayrica 23 kanalin medyanlarinin medyani 926 idi, yani bu kanalin 1.292
  medyaninin ALTINDA. 12'si bizden kotu. Batan kanallarin ic kiyasi
  kazandirani ogretmez.

Duzeltme turunda dedektor kanal-basi token frekansina cevrildi:
atesleme orani %5,7 -> %44,7. Yani sorun turde degil dedektorde idi.

## Duzeltilmis sonuc, kanal ICI test

| Grup | n | Destekleyen | Curuten | Medyan fark |
|---|---|---|---|---|
| Bilgi tasiyan tum kanallar | 12 | 6 | 4 | +7 puan |
| Kazananlar (medyan >=20k) | 6 | 3 | 1 | +17 puan |
| Taban (medyan <=2k) | 6 | 3 | 3 | +3 puan |

Zayif ama pozitif, ve kazananlarda daha guclu. Kesin degil.

## Hipotez YANLIS SEVIYEDE test edilmisti

`EverythingSquatch`: isabet 5/5, iska 5/5. Bigfoot'a adanmis bir kanalda
karakter adi her baslikta, dolayisiyla kanal ICI farki TANIM GEREGI aciklayamaz.
"Tekrar eden karakter" etkisi video seviyesinde degil KANAL seviyesinde calisir.

Kanal seviyesinde (n=29, en az 10 videolu kanallar):

| Karakter tutarliligi | n | Medyan izlenme |
|---|---|---|
| Yuksek (>=%60 baslikta ayni karakter) | 11 | 5.700 |
| Dusuk (<=%20) | 9 | 168 |

Temiz degil: `Super Ai hero` %100 tutarlilikla 40 izlenme, `Animal Rescue AI`
%0 karakterle 23.000.

## DAHA GUCLU DESEN: hayvan / yaratik oznesi

Mekanik olcum (kelime listesiyle, gozle degil):

| Grup | n | Medyan izlenme |
|---|---|---|
| Basliklarinin >=%50'si hayvan/yaratik | 8 | 25.500 |
| Hayvan/yaratik yok (<=%10) | 15 | 108 |

Hayvan grubu: The World According to AI 79.000, AI Pet Legends 70.500,
Bigfoot Adventures 53.000, EverythingSquatch 28.000, Animal Rescue AI 23.000,
Kim The Gorilla 5.700, Gorilla Vlogs AI 4.600, Surreal Ai Clips 168.

Hayvansiz grubun tepesi: Hero of SuperAI 102.500 (%0 hayvan), Tooniverse
41.000 (%2). Geri kalan 13 kanal 2.400 ve altinda.

En dipte insan vlogu ve urun reklami var: Daily vlogs sharma ji 11,
AI Product Commercials 24, Hasnain Daily Short Vlogs 29, @Hero of Super AI 2.

### Bu bulgunun SINIRLARI, abartilmamali

- SECIM YANLILIGI: 30 kesif sorgusunun 5'i dogrudan yaratik odakliydi
  (AI Bigfoot vlog, AI cryptid vlog, AI creature vlog, AI animal vlog).
  Yaratik kanallari orneklemeye SECILEREK girdi; farkin bir kismi bundan.
- Kanallar ARASI karsilastirma: uretim kalitesi, kanal yasi ve rekabet
  yogunlugu kontrol edilmiyor. Kanal ICI testten daha zayif kanit.
- n=29 kanal, gruplar 8 ve 15. Kucuk.
- Hayvan SART DEGIL: iki istisna 102.500 ve 41.000 aliyor.
- Kelime listesi benim kurgum, kanonik bir siniflandirma degil.

## Karar icin anlami

Ihsan 10 Eylul'de karakteri "kendi AI benzeri" olarak sectigi icin bu bulgu
o karara DOGRUDAN karsi kanit uretiyor: bu orneklemde insan ozneli AI kanallari
dipte kumelenirken (medyan 108) hayvan/yaratik ozneli kanallar tepede (25.500).
Hayvansiz iki kazanan da "siradan bir adam" degil, superkahraman ve cizgi film.

Karar Ihsan'in; bu not kanitin ne dedigini kayda gecirmek icindir.
