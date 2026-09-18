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

---

# EK 4: raselranaai ve motionsbysubh.ai , 10 Eylul 2026

Ihsan'in verdigi iki IG hesabi. Olcum: ig_kaz DOM kazima (189+189 reel),
shortcode->pk cozumu ile GERCEK kronoloji, secilen reel'ler indirilip ffmpeg.

## 1. TUZAK: izgara sirasi kronoloji DEGIL

motionsbysubh.ai'de en cok begenilen 3 gonderi izgarada 1, 2, 3. siradaydi.
Shortcode'lar pk'ya cozulunce ortaya cikti: izgara sirasi [4,6,7,5,8], yani
ilk uc SABITLENMIS gonderi. "Son paylasimlar" penceresi onlarla kirleniyordu.
Ilk okumam yanlisti, kronoloji cozulerek duzeltildi.

## 2. Iki hesabin durumu (BEGENI, izlenme degil , 11. tuzak)

| | motionsbysubh.ai | raselranaai |
|---|---|---|
| reel | 189 | 189 |
| medyan begeni | 482 | 14 |
| en iyi | 66.400 | 1.595 |
| GERCEKTEN en yeni 20, medyan | 325 | 7 |
| en eski 40, medyan | 2.161 | 9 |

motionsbysubh.ai 6,6 KAT DUSMUS. Ihsan'in gozlemi dogru.
raselranaai hic tutmamis: 189 reel, medyan 14 begeni.

## 3. YouTube hesaplari , IKISI DE OLU

| Kanal | Abone | Medyan | En iyi | Son paylasimlar |
|---|---|---|---|---|
| MOTIONSBYSUBH AI | 92 | 49 | 88.000 | 4-36 |
| Rasel Rana AI | 29 | 422 | 1.800 | 1-13 |

Bu ONEMLI: format YouTube'a TASINMAMIS. IG'de calisan sey orada calismamis.
Biz YouTube kanali kuruyorsak bu bir uyaridir, kanit degil ama uyari.

## 4. Zirve ile dip karsilastirmasi (ffmpeg)

| | Zirve 66.400 | Eski hit 65.000 | Yeni dip 20 | Yeni dip 79 |
|---|---|---|---|---|
| cozunurluk | 720x1280 | 720x1280 | 720x1280 | 720x1280 |
| sure | 15,2 sn | 18,9 sn | 24,5 sn | 32,1 sn |
| kesme | 0 | 1 | 17 | 1 |
| en uzun plan | 15,2 | 11,2 | 5,5 | 22,4 |
| LUFS | -14,5 | -14,1 | -14,1 | -14,4 |
| konusma | yok | yok | yok | yok |

Isabetler KISA ve TEK PLAN. Yeni dusukler UZAMIS (24,5 ve 32,1 sn),
biri 17 kesmelik montaja donmus. Ses dordunde ayni, ayirt edici DEGIL.
Cozunurluk dordunde de 720x1280, bizim 1080x1920'den DUSUK.

## 5. Tur ve gorsel ayrim (kareler cikarildi, goz ile bakildi)

Tur: imkansiz bir film sahnesinin SAHTE KAMERA ARKASI.

Zirve: yesil perde duvari, ekip uyeleri net, ON PLANDA iki kamera monitoru
cekimi gosteriyor, tripodlar. "Bu sahte, iste nasil yapildi" ILK KAREDE okunuyor.

Dip: ayni tur, benzer kalite, ama sahne dunyanin icinde. Yesil perde yok,
monitor yok, ekip arka planda puslu. Bir FILM KARESI gibi duruyor.
Ifsa ilk karede OKUNMUYOR.

Bu, eski unnatural-lab dersiyle AYNI kural: odul ilk karede okunmali.

Zirve videoda sol ustte SYNTX.AI filigrani var (sponsor/arac markasi).

## 6. 11,9M iddiasi

Ihsan "instagramda 11.9M izlenen shortsu var" dedi. Begeniye gore zirve
DckORL2B8gx (66.400 begeni). 66.400/11.900.000 = %0,56 begeni orani,
Reels icin makul. TAHMINDIR; kesin oynatma IG Insights'ta ya da
media info API'de (su an 429 veriyor).

## 7. Kopyalanabilecekler ve KACINILACAKLAR

Kopyalanabilir (olculdu):
- 15-19 saniye, TEK PLAN, 0-1 kesme
- ifsanin ilk karede okunmasi (yesil perde + ekip + monitor)
- konusma yok, muzik/ambiyans surukluyor
- sabit karakter, ortama uygun kiyafet

Kacinilacak (olculdu, bu hesabin kendi dususu):
- videoyu 24-32 saniyeye uzatmak
- 17 kesmelik montaja donmek
- ifsayi kadrajdan cikarip film karesi gibi cekmek

## 8. Olculemedi

- Gercek oynatma sayilari (IG media info API 429 verdi, tekrar denenmeli)
- retention / izlenme suresi (IG Insights gerekir, hesap bizim degil)
- raselranaai'nin video icerigi (indirilmedi, sadece sayac olculdu)
- YouTube hesaplarinin gercekten ayni kisilere ait oldugu DOGRULANMADI;
  isim benzerligine dayaniyor.

---

# 12 Eylul 2026 , 2M begenili referansin olcumu (Db6U9BbBa1k)

Istek: Ihsan bu videoyu verdi, "cok kaliteli, 2M like almis, sentinalihsan
icin uygulanabilir mi" dedi.
Yontem: giris yapmis IG oturum cerezi ile yt-dlp, ffmpeg/ffprobe, EBU R128,
faster-whisper (VAD), kare kare goz.

## 1. BULGU 1: bu video doktrinimizin ucuncu referansinin AYNISI DEGIL, RAKIBI

Ayni sahne, ayni format, iki ayri video. Ikisini de indirip olctum.

| | **Db6U9BbBa1k** (Ihsan'in verdigi) | **DdEArj4BMrV** (doktrin referans 3) |
|---|---|---|
| Hesap | @drkelsofficial | @motionsbysubh.ai |
| Tarih | 11 Agustos 2026 | 10 Eylul 2026 |
| **Begeni** | **2.035.670** | **78** |
| Yorum | 13.854 | 5 |
| Uretim | beyan yok, `#animatronic` | caption'da yazili: **Seedance 2.5 / Syntx AI** |
| Cozunurluk | 720x1280, 24 fps | 1080x1920, 30 fps |
| Sure | 15,05 sn | 15,10 sn |
| Kesme (esik 0,30) | 0 | 0 |
| Kesme (esik 0,20) | **0** | 1 |
| Kesme (esik 0,10) | **0** | **25** |
| LUFS | -15,1 | -15,2 |
| True peak | -0,1 dBTP | +0,6 dBTP (kirpiyor) |
| **LRA** | **16,0** | 10,3 |
| Konusma | 1 seslenme (asagida) | 0 kelime |
| Filigran | yok | her karede SYNTX.AI |

Ayni sahneyi, ayni sureyi, daha yuksek cozunurlukle kopyalayan AI versiyonu
**78 begeni** aldi. 2 milyonluk olan teknik olarak daha DUSUK: 720p, 24 fps.

Bu, filonun AImagine-Fear dersinin ikinci bagimsiz kaniti:
**teknik duzeltme hit uretmez.**

### Doktrine duzeltme

`DOKTRIN.md` ve `bible.json:format_note`, DdEArj4BMrV'yi "720x1280, 15,18 sn"
diye kaydediyor. **Yanlis.** O olcum anonim yt-dlp'nin verdigi dusuk rendition'di.
Giris yapmis cerezle gercek rendition **1080x1920, 30 fps** cikiyor.
Ayni sebeple "0 kesme" de yanlis: 0,10 esiginde 25 kesme adayi var, yani o video
zincirlenmis. Hedef video ise 0,10 esiginde bile **0** veriyor, gercekten tek plan.

## 2. Vurus zaman cizelgesi (kare + RMS olcumu)

| Zaman | Vurus | Ses (RMS) |
|---|---|---|
| 0,0-0,6 sn | Sessizlige yakin acilis, **set seslenmesi** | -48 dB -> -29 dB |
| 0,6-4,5 sn | Tehdit: kafa arkada yukselir, cene acilir, kadin donuk, yuzu KAMERAYA DONUK | ~-24 dB |
| 4,5-6,0 sn | Yutulma: cene kapanir, kafa kameranin onunden gecer | **-9,2 dB tepe** |
| 6,0-10,5 sn | **OLU VURUS: yaratik durur, kadin kadrajda YOK, ekip bakar** | **-29 ila -35 dB** |
| 10,5-15,0 sn | Ifsa: ekip kafanin tabanindaki **DIKDORTGEN KAPAGI** acar, kadini cikarir | -22 ila -28 dB |

Toplam ses salinimi ~26 dB. Bizim ep06'mizin LRA'si 9,1, bu videonunki 16,0.

**Konusma:** 0,00-0,56 sn arasi tek seslenme var. Whisper "Action!" okuyor.
Ham dosyada kelime guveni 0,44; ilk 1,2 saniyeyi +12 dB yukseltip tekrar
kosunca no_speech 0,06'ya dustu, kelime guveni 0,59'a cikti. Yani **seslenme
kesin var**, metnin "Action" oldugu yuksek olasilikli ama kesin degil.
Bu anlatim DEGIL, setin kendi sesi. Kural 1'i ihlal etmez.

## 3. Bizim ep06 ile yan yana

| Olcum | 2M referans | ep06 (bizim) | ref3 (78 begeni) |
|---|---|---|---|
| Sure | **15,05 sn** | 22,87 sn | 15,10 sn |
| Kesme | 0 (0,10 esiginde de) | 1 | 25 (0,10 esiginde) |
| Cozunurluk | 720x1280 / 24 fps | 1080x1920 / 30 fps | 1080x1920 / 30 fps |
| LUFS | -15,1 | -14,5 | -15,2 |
| True peak | -0,1 | **-1,3 (en iyisi bizde)** | +0,6 |
| **LRA** | **16,0** | 9,1 | 10,3 |
| Acilis yuzu | kameraya donuk, korku okunur | **PROFILDEN**, ekip siluetleri onde | kameraya donuk |
| Fon | siyah duvak + beyaz yansitici | **parlak yesil perde** | orman dekoru + yesil |
| Kiyafet | sade siyah tisort, gri esofman, sirilsiklam | haki macera gomlegi | Lara Croft tarzi kostum |
| Cikis yolu | **kafa tabaninda kapak** | agizdan | agizdan |
| Bitis duygusu | **sarsilmis, nefes nefese, ekip kollarindan tutuyor** | alkis + gulumseme | alkis + cakistirma |

## 4. Sekiz maddelik skor karti , 2M referans

Madde 1, 3, 5, 8 insan yargisi (olcutler.md notu).

1. Ilk kare: yuz + hareket + arkada yaratik, ucu birden. **1**
2. Acilis "problemi" adlandiriyor mu: gorsel olarak evet, "bu kadin yutulacak". **1**
3. Ekran yazisi: **YOK. 0**
4. Vaat: 3. saniyede ne alacagini biliyorsun (yutulacak, sonra ifsa). **1**
5. Tempo: 0 kesme ama olay surekli ilerliyor, anomali pattern interrupt goruyor. **1**
6. Ses: muzik yok, ilk seslenme 0,3 sn'de, diegetik ses tam dinamikte. **1**
7. Aciklama metni: "shout out to our super stars" , videoda olmayan bir sey
   katiyor (ekibi ovuyor) ama net eylem yok. **0**
8. Odul: 15 saniye boyunca kaydirmak istemedim; olu vurus merak uretiyor. **1**

**6/8. Yayinlanabilir uste.** Kaybettigi iki madde ekran yazisi ve CTA.
Bizim doktrinimiz zaten ekran yazisini yasakliyor (kural 11), yani o madde
bilincli bir kayip. 371.000 begenili Burj Khalifa da yazisiz gelmisti.

## 5. UYGULANABILIR , en degerliden en ucuza

Her madde icin: ne olculdu, motorda nereye dokunur, ne kadar kesin.

### A. OLU VURUS'a zaman ve SESSIZLIK ver (en buyuk eksik, en ucuz)

Olculen: 6,0-10,5 sn arasi 4,5 saniye boyunca yaratik durur, kadin kadrajda
yoktur, ses 25 dB DUSER. Merak tam burada uretiliyor.
Bizim `shot_plan` 2. maddesi bunu zaten yaziyor ("the creature settles with the
man nowhere in frame") ama sure vermiyor ve mastering sessizligi duzlestiriyor.
Dokunulacak yer: `series.json auto_replenish.shot_plan[2]` + mastering zinciri.
Kesinlik: yapisal olarak olculdu, etkisi test edilmedi.

### B. Ses dinamigini KORU (LRA 16,0 vs 9,1)

Olculen: referansin salinimi 26 dB, bizimki dar. -14 LUFS hedefi dogru, sorun
hedef degil, sessiz bolumun sikistirilmasi.
Dokunulacak yer: `master_audio` limiter/kompresor ayari. Bunu kod tarafinda
DOGRULAMADIM, sadece ciktinin LRA'sini olctum. Once olcum, sonra degisiklik.

### C. Acilisa diegetik set seslenmesi

Olculen: 0,0-0,56 sn, sessizlige yakin kare uzerine tek seslenme.
"Bu gercek bir cekim" sinyalini bedavaya veriyor.
UYARI: QC'de `native_audio_review` acik ve ep01'de tam da "ham native seste
istenmeyen konusma var" diye RED verdi. Bu maddeyi eklersen QC notunu AYNI ANDA
guncellemen sart. Doktrinin kendi 3. dersi bu.

### D. Yuzu KAMERAYA DONDUR (bakis degil, yon)

Olculen: referansta ilk karede yuz kameraya donuk ve korku okunuyor.
ep06'da Ihsan profilden ve ekip siluetlerinin arkasinda.
`characters[0].bio` "kameraya degil yaratiga ya da ekibe bakar" diyor. Bu kalsin.
Eklenecek: **govde ve yuz kadraja donuk olsun, goz merceye bakmasin.**
Kesinlik: iki referansin ikisinde de var (2M ve 78'lik), yani format kurali,
performans ayirt edicisi degil. Yine de bizde EKSIK.

### E. Sure ve cekim sayisi , KARAR SENIN

Olculen: tutan uc referansin ucu de 15,0-15,2 sn. Bizim ep06 22,87 sn.
`bible.json:duration_note` senin 26 sn kararini kaydediyor, gerekce "uc vurus
24 saniye gerektiriyor".
**Bu gerekce olcumle curudu:** 2M referans DORT vurusu (tehdit, yutulma,
olu vurus, ifsa) 15,05 saniyede yapiyor. Yani uc vurus 24 saniye gerektirmiyor.
Onerim 2x8 = ~15-16 sn. Ama bu senin verdigin karardi, degistirmeden sormam gerek.

### F. A/B testine ACIK, kural yapma (n cok kucuk)

Bu uclu 2M ile 78 arasinda ayrisiyor ama tek ornek cifti. Kural yazma, test et:

- **Siyah duvak vs yesil perde.** 2M'de fon siyah duvak + beyaz yansitici.
  Ama 4,4M'lik DckORL2B8gx'te yesil perde VAR (TERSINE-MUHENDISLIK bolum 6).
  Yani yesil perde diskalifiye degil. Degisken olarak isaretle.
- **Sade kiyafet vs kostum.** 2M'de islak sade tisort + esofman. 78'lik ve
  bizim ep06'da kostum. Hipotez: kostum kurguya benziyor, sade kiyafet belgeye.
- **Sarsilmis bitis vs alkisli bitis.** 2M'de kadin nefes nefese, ekip kollarindan
  tutuyor, gulumseme YOK. 78'lik ve bizim ep06'da alkis ve cakistirma var.
- **Kapaktan cikis vs agizdan cikis.** 2M'de ekip kafanin tabanindaki dikdortgen
  kapagi aciyor. Doktrin kural 6 "cikis agizdan" diyor ve bu kural **78 begenili
  videodan** turetildi. Giris agizdan kalmali, cikis tartismali.

### G. Cozunurluge para harcama (teyit)

2M'lik video 720x1280 / 24 fps. Bizimki 1080x1920 / 30 fps. Ayrica bizim true
peak'imiz (-1,3) ucunun de en iyisi. Teknik kalemde onlerindeyiz ve fark bu degil.

## 6. Olculemedi

- **Izlenme sayisi.** Sadece begeni ve yorum geldi. TERSINE-MUHENDISLIK bolum 0
  bu hesaplarda begeniden izlenme turetmenin gecersiz oldugunu olctu (%0,55 ile
  %3,66 arasi, 6,6 kat oynuyor). **Tahmin yazmadim.**
- **Videonun AI mi gercek mi oldugu.** Caption `#animatronic` diyor ve ekibi
  ovuyor. 15,05 saniyelik, 0,10 esiginde bile kesmesiz tek plan, tutarli su
  fizigi ve mekanik olarak makul bir kapak var. Degerlendirmem (olcum degil):
  bugunku video modelleri icin bu zor, gercek set kaydi olma ihtimali yuksek.
  **Dogrulayamadim.** Onemi su: gercekse dokusunun bir kismi kopyalanamaz.
- **@drkelsofficial'in diger gonderileri.** yt-dlp profil listelemesi hata verdi,
  hesabin tek isabet mi yoksa surekli mi ustledigi bilinmiyor.
- **Retention.** Hesap bizim degil.

## 7. BUGUNE DAIR OPERASYON UYARISI

Bu rapor 12 Eylul 10:22 PDT'de yazildi. `wild-encounter.yml` bugun 11:30 PDT'de
ep07'yi otomatik yayinlayacak.

**DOKTRIN.md'ye bugun kosudan ONCE dokunma.** Doktrin damgasi degisince kuyruktaki
part07-11 bayatlar ve uretim "legacy plan doktrin damgasi guncel doktrinle
eslesmiyor" diyerek fail-closed durur. Bugun yayin cikmaz.

Dogru sira: ep07 ciksin, olculsun, sonra degisiklik, sonra
`python -m series.replenish --series wild-encounter` ile kuyruk yeniden yazilsin.

---

# 12 Eylul 2026, ikinci ekleme , UCUNCU ORNEK ANALIZI DEGISTIRDI (DcFKOMIql0L)

Ihsan ikinci bir ornek verdi. Olctum ve **yukaridaki 5. bolumun oncelik siralamasi
gecersiz kaldi.** Uc ornek yan yana gelince hangi degiskenin ayirt ettigi degisti.

## 1. Uc referans, tek tablo

| | **Db6U9BbBa1k** | **DcFKOMIql0L** | **DdEArj4BMrV** |
|---|---|---|---|
| Hesap | @drkelsofficial | @dreamina_lumi1 | @motionsbysubh.ai |
| Yayin | 11 Agu 2026 | 16 Agu 2026 | 10 Eyl 2026 |
| **Begeni** | **2.035.670** | **23.167** | **78** |
| Yorum | 13.854 | 303 | 5 |
| Yas (olcum ani) | ~32 gun | ~27 gun | **~2 gun** |
| Uretim | beyan yok, `#animatronic` | **Dreamina Seedance 2.5** (beyan) | Seedance 2.5 / Syntx AI (beyan) |
| Cozunurluk | 720x1280 / 24 fps | 1080x1920 / 30 fps | 1080x1920 / 30 fps |
| Sure | 15,05 sn | 10,05 sn | 15,10 sn |
| **Kesme (esik 0,10)** | **0** | **0** | **25** |
| LUFS | -15,1 | -14,7 | -15,2 |
| True peak | -0,1 | +0,2 | +0,6 |
| LRA | 16,0 | 8,5 | 10,3 |
| **Set seslenmesi** | **"Action!" 0,00-0,56** | **"Action!" 0,00-0,58 + "Cut!" 8,08-8,59** | **YOK** |
| Fon | siyah duvak | **cıplak MAVI perde** | kurulmus orman dekoru + sis |
| Set malzemesi | su tanki | kum serit + tahta iskele + can simidi | yaprak, sarmasik, sis, tepe isigi |
| Ifsa vurusu | kapaktan cikis | **YOK** | agizdan cikis |
| Yuz | kameraya donuk | **yuzukoyun, yuz gorunmuyor** | kameraya donuk |
| Filigran | yok | Dreamina reklam bindirmesi | SYNTX.AI |

## 2. AYIRT EDEN UC DEGISKEN

Iki kazanan ile kaybedeni ayiran, uc ornekte de tutarli olan UC sey var.

### 1. Gercekten tek plan (kesintisiz)

0,10 esiginde: 2M -> 0 kesme adayi, 23K -> 0, 78 -> **25**.
Iki kazanan tek cekimde uretilmis. Kaybeden zincirlenmis ve yumusak birlestirilmis.
23K'lik video 10,05 sn, yani tek Seedance uretimi. Yani **AI ile tek plan MUMKUN**,
sure tek uretimi asmayinca.

### 2. Diegetik set seslenmesi

2M: "Action!" 0,00-0,56 sn. 23K: "Action!" 0,00-0,58 **ve "Cut!" 8,08-8,59**.
78: sifir kelime.
Ikisi de sessizlige yakin bir kareden aciliyor, uzerine tek seslenme biniyor
(2M'de -48 dB -> -29 dB, 23K'de -43 dB -> -24 dB).

Bu videonun kancasi. Ilk yarim saniyede "bu gercek bir cekim, kayit basliyor"
diyor. Anlatim degil, setin kendi sesi. Doktrin kural 1'i ihlal etmez.
**En ucuz ve en tekrarlanabilir madde bu.**

### 3. CIPLAK CALISAN DUZENEK, atmosferik dekor DEGIL

- 2M: siyah duvak, su tanki, beyaz yansitici. Dekor yok.
- 23K: cıplak mavi perde, kum serit, bir tahta, bir can simidi. Dekor yok.
- 78: sarmasik, yaprak, sis, tepeden atmosferik isik. **Dekor dolu.**

Perdenin RENGI onemsiz: kazananlarda siyah ve mavi, TERSINE-MUHENDISLIK'teki
4,4M'lik DckORL2B8gx'te yesil. Onemli olan **sis ve dekor giydirmesinin YOKLUGU**.

Bu maddenin ikinci, bagimsiz destegi TERSINE-MUHENDISLIK bolum 6'da zaten var:
motionsbysubh'un dusen videolarinda "yesil perde ve monitor YOK, ekip arka planda
puslu; bir film karesi gibi duruyor" ve medyan 2.161'den 325'e dusmustu.
Yani ayni desen hem hesaplar arasi hem hesap ici olculdu.

**DOKTRIN KURAL 5 BU BULGUYLA TERS.** Kural su an "KURULMUS DEKOR, CIPLAK YESIL
PERDE DEGIL. On planda gercek set malzemesi (yaprak, kaya, su, sis)" diyor ve
kaynak olarak **78 begenili videoyu** gosteriyor. `art_style` de "practical haze"
yani sis istiyor. Iki kazananda da sis ve dekor YOK.

Ayrim sanirim su: **islevsel set malzemesi** (su tanki, kum, tahta) kaliyor,
**atmosferik giydirme** (sarmasik, yaprak doseme, sis, kanopi isigi) gidiyor.

## 3. AYIRT ETMEYEN degiskenler , yukaridaki 5. bolumu duzeltiyor

Uc ornek gelince su maddeler ayirt edici OLMAKTAN CIKTI. Onceki bolumde
fazla one koymustum.

| Degisken | 2M | 23K | 78 | Ayirt ediyor mu |
|---|---|---|---|---|
| LRA (ses salinimi) | 16,0 | **8,5** | 10,3 | **HAYIR.** 23K bizim ep06'dan (9,1) bile dar |
| True peak | -0,1 | +0,2 | +0,6 | HAYIR. Bizim -1,3 ucunun de en iyisi |
| Cozunurluk | 720p | 1080p | 1080p | HAYIR |
| Sure | 15,05 | 10,05 | 15,10 | HAYIR. 78'lik de 15 saniye |
| Ifsa vurusu | var | **YOK** | var | HAYIR. 23K ifsasiz 23 bin aldi |
| Yuz kameraya donuk | evet | **hayir** | evet | HAYIR. 23K'de kadin yuzukoyun |
| Olu vurus | 4,5 sn | ~1,5 sn | yok | Zayif sinyal, sadece en buyukte belirgin |

Yani onceki eklemedeki **B (ses dinamigi) ve D (yuz yonu) maddelerini geri
aliyorum.** Olcum onlari desteklemiyor. A (olu vurus) sadece en buyuk ornekte
belirgin, hipotez olarak kalsin, oncelik degil.

## 4. ONEMLI CEKINCE: yas esit degil

78 begenili video olcum aninda **~2 gunluk**, digerleri ~1 aylik.
`olcutler.md` bolum 11 "karar genelde ilk 30-60 dakikada, basarisiz demeden once
24-48 saat bekle" diyor; 48 saat sinirdayiz. Ayrica AImagine-Fear'da olculmus bir
**gec atesleme** vakasi var (Burj Khalifa 21. saatte 1 izlenme, 44. saatte 1.568).

78 ile 23.167 arasindaki fark yasla kapanacak kadar kucuk degil, ama sayiyi
kesin hukum gibi kullanma. **Uc gun sonra DdEArj4BMrV'yi tekrar olc.**

## 5. GUNCELLENMIS UYGULAMA SIRASI

Once yapilacaklar (uc ornekte de tutarli, ucu de ucuz):

1. **Acilisa "Action!" set seslenmesi.** Sessizlige yakin ilk kare, uzerine tek
   seslenme. Istersen sona "Cut!" de eklenebilir (23K'de var).
   UYARI: QC'de `native_audio_review` acik, ep01'de tam da bu sebeple RED verdi.
   Kural degisirse QC notu AYNI ANDA degisecek. Doktrinin kendi 3. dersi.
2. **Sis ve dekor giydirmesini kaldir.** `art_style` icindeki "practical haze"
   ve `environments.jungle_set` icindeki "hanging vines, wet leaf litter,
   low drifting haze" iki kazananda da yok. Islevsel malzeme kalsin
   (su, kum, tahta, kaya), atmosferik giydirme ciksin.
   Bu **DOKTRIN kural 5'i tersine cevirmek** demek, karar senin.
3. **Cekim sayisini dusur, tek plan hissini koru.** Iki kazanan da 0,10 esiginde
   0 kesme veriyor. Bizim ep06 22,87 sn ve 1 kesme. 23K'lik ornek tek uretimin
   suresinde kalarak (10 sn) bunu bedavaya aliyor.

Test edilecekler (tek ornek cifti, kural yapma):

4. Sade kiyafet vs kostum (2M sade tisort+esofman, 23K mayo, 78 macera kostumu).
5. Kapaktan cikis vs agizdan cikis (2M kapak, 78 agiz).
6. Olu vurusa sure vermek (sadece 2M'de belirgin).

Yapma:

7. Cozunurluk, LUFS, true peak tarafina para ve zaman harcama. Uc olcumde de
   performansla iliskisi yok ve bizim degerlerimiz zaten en iyisi.

## 6. Ek gozlem: baslik kalibimiz zaten dogru tarafta

23K'lik videonun basligi: "This Beach Shark Scene Looks Way Too Real".
Bizim `title_style`: "This GIANT <ANIMAL> Is NOT Real".
Ayni kalip, ters kutup. Degistirmeye gerek yok, ama "Looks Way Too Real"
yonu de test edilebilir.

## 7. Bu eklemede olculemedi

- Uc hesabin izlenme sayilari (yalniz begeni ve yorum geldi; begeniden izlenme
  turetmek TERSINE-MUHENDISLIK bolum 0'da gecersiz olctuldu).
- DcFKOMIql0L'nin ifsasiz bitisinin retention'a etkisi.
- Hesap boyutlari ve takipci sayilari (karsilastirma hesap olcegine gore
  normalize EDILMEDI, bu tablonun en buyuk zayifligi).

---

# 15 Eylul 2026 , ep09 (dev kutup ayisi) olcumu + otomasyon denetimi

Istek: "son video YouTube'da cok iyi izlendi, /reel-analiz DdSKzasgRsV, video
hatali ama neyi dogru yaptik, otomasyon calisacak mi, kac gun konsept var".
Yontem: yt-dlp ile IG kopyasi indirildi, ffprobe/ffmpeg + EBU R128 ile olculdu,
7 ek kare (t=4,0 / 5,0 / 6,0 / 7,0 / 8,0 / 9,0 / 9,8) goz ile incelendi,
izlenmeler canli watch sayfasindan cekildi, kosu loglari `gh run view` ile okundu.

## 1. Kanal olcumu (15 Eylul, canli sayaclar)

| Video | Format | sn | Izlenme | Begeni |
|---|---|---|---|---|
| `wuuu02K2hPc` GIANT POLAR BEAR | tek plan | 10 | **26.456** | 131 |
| `mYUqbRjJoVs` GIANT ANACONDA | tek plan | 10 | **6.820** | 52 |
| `TiJ8Uv7vhzs` GIANT CROCODILE | 3x8 | 23 | 3.857 | 29 |
| `TO_SK8dIyLQ` GIANT OCTOPUS | 3x8 | 23 | 2.870 | 16 |
| `Cs6gHuxf7A4` GIANT PRAYING MANTIS | 3x8 (kesik) | 23 | 296 | 4 |
| `XNEw5jkObdw` LEMON BOUNCES | unnatural-lab | 17 | 1.541 | 17 |
| `XzABOqtimVE` SOAP | unnatural-lab | 17 | 1.509 | 5 |
| `3k7qal307DQ` PLASTIC BOTTLE | unnatural-lab | 22 | 1.164 | 9 |
| `2scmbwTq4sQ` Burning Forest | , | 29 | 736 | 5 |
| `bGN9DDrPUeQ` NAPKIN | unnatural-lab | 22 | 172 | 2 |

- 10 sn TEK PLAN medyani: **16.638**. 23 sn 3x8 medyani: **2.870**. Oran **5,8 kat**.
- ep09, kanalin tum zamanlarinin en iyisi ve daha ~1 gunluk.
- TikTok'ta ayni video: **499 izlenme / 3 begeni**. Instagram olculemedi (hiz siniri).
  Yani patlama YouTube'a ozel; tek platformdan kanal karari verme.
- Orneklem tek plan tarafinda n=2. Yon guclu, kural degil.

## 2. ep09 teknik olcumu (IG kopyasi `DdSKzasgRsV`)

| Olcum | Deger | Esik | Sonuc |
|---|---|---|---|
| Cozunurluk | 1080x1920 | 1080x1920 | OK |
| Sure | 10,01 sn | referans 11/11 = 10,01 | OK, birebir |
| Sahne kesmesi | **0**, tek plan 10,01 sn | 0 | OK |
| Integrated loudness | **-14,1 LUFS** | -16 ... -13 | OK |
| True peak | **-2,0 dBTP** | <= -1,0 | OK |
| LRA | 6,6 | ~4 | kabul |
| Konusma | 0 kelime | anlatim yok | OK |
| Kare hizi | **30 fps** | referans 24 | KUSUR, bkz 5.4 |

## 3. NEYI DOGRU YAPTIK , kare kare dogrulandi

REFERANS-AYUSH-ANALIZ.md'nin olctugu dort ayirt edici ozellikten ucu tam,
biri yarim tuttu:

- **(a) SIS YOK.** Yedi karenin yedisinde hava temiz, duman/pus yok. Kaybeden
  referans videolarin ortak ozelligi olan sis bizde hic yok.
- **(c) IFSA VAR VE GUCLU.** t=7,0'da ekip kosarak geliyor, t=9,0'da elleriyle
  ceneyi aciyor, t=9,8'de Ihsan sag salim disarda. Referansin 675K'lik videosunu
  kazandiran vurus bizde de videonun icinde veriliyor.
- **(d) TANIDIK GERCEK HAYVAN.** Kutup ayisi. Uydurma yaratik degil.
- **(b) TEMAS , YARIM.** Asagida 4. bolum.

Gorsel gramerin tamami tuttu: mavi perde + acik mavi arti marker'lari, gorunur
studyo betonu, sig kum adasi + birkac kaya + kutuk + seyrek ot, tavanda beyaz
difuzyon izgarasi, koyu kiyafetli ekip ve on planda kamera operatorlerinin sirti,
genis kadrajdan yakina yavas push-in, ekranda yazi yok, muzik yok, anlatim yok.
Ses -14,1 LUFS ile filonun hedefinde.

**Tek cumleyle: 10 saniye + tek plan + sifir kesme + temiz hava + tanidik hayvan +
sondaki kurtarma karari dogru cikti. 3x8 formatindan tek plana gecis olculdu ve tuttu.**

## 4. KUSURLAR , goz ile gorulen (kare kanit, olcum degil)

1. **Yutulma vurusu eksik teslim edildi.** t=5,0'da Ihsan ayakta duruyor, sadece
   bas/ust govde agizda; bacaklari ve govdesinin buyuk kismi kadrajda. Doktrin ve
   QC notu "the man taken completely out of sight inside the mouth" diyor.
   Referansin kazanan videolarinda kisi TAMAMEN kayboluyor. En pahali kusur bu.
2. **Cikis suregi kopuk.** t=9,0'da ekip hala ceneyi acmaya calisirken Ihsan zaten
   agzin onunde ayakta. "Icinden cikti" hareketi gosterilmiyor; adam sahnede yer
   degistiriyor.
3. **Anatomi kusurlari.** t=9,0'da cenenin etrafinda fazladan el/kol var, soldaki
   ekip uyesinin kolu bozuk. QC bunu gormedi (`artifact_score` 0, `issues` bos).
4. **Merceğe bakis.** t=9,8'de Ihsan gulumseyerek kameraya dogru yuruyor ve merceğe
   cok yakin bakiyor. Doktrin kural 4 ve QC notu bunu acikca yasakliyor.
5. **Yaratik canli okunuyor.** Ayi yuruyor, kukruyor, goz kirpiyor. Ifsayi yalniz
   ekibin mudahalesi tasiyor. (Referansin kazananlarinda da boyle, bu yuzden
   listenin en altinda.)

## 5. OTOMASYON DENETIMI

### 5.1 Bugunku kosu BASARISIZ , part 10 uretilemedi

`gh run 35026600878`, 15 Eylul 21:36 UTC, 6 dk 2 sn, sonuc **failure**.

- Konu: Part 10/13, "This GIANT OWL Is NOT Real".
- Iki referans gorseli uretildi (jungle_set + dev baykus), 16 kredi harcandi.
- Sonra Kie Omni **5 denemenin 5'inde** `Internal Error, Please try again later.`
  dondu, her biri gorev olusturulduktan ~30 sn sonra.
- `En az cekim kapisi artik karsilanamaz: kabul=0, kalan=0, gerekli=1`
- Part 10 `qc_retry (1/3, neden=UNKNOWN)`.

**Kie coktu mu? Hayir.** Ayni gun `Galactic Daily` 19:45 UTC'de **ayni Omni
motorunu** basariyla kullandi (8 sn, 105 kredi). Fear Slide 17:41'de Seedance ile
gecti. Yani ariza Kie geneli degil; bu istege ozel ya da o bes dakikalik pencereye ait.

**Para yanmadi:** kosu icinde okunan bakiye 5.474, simdi olculen bakiye de **5.474**.
Basarisiz Omni denemeleri faturalanmamis. Defterde `wild-encounter:10 , 16.0` yaziyor
ve dogru.

### 5.2 Yarin ne olacak , sayilarla

Cron degismedi: `.github/workflows/wild-encounter.yml`, **18:30 UTC her gun**.

- 16 Eylul: part 10 yeniden uretilir. Tutarsa ep10 uc platforma cikar.
- Tutmazsa `retry_count` 2/3 olur, 17 Eylul'de 3/3 olur ve part 10 `needs_human`a
  dusup **kuyruk part 11'e ilerler** (`series/series_runner.py:877`).
- En kotu senaryo: **ilk yayin 18 Eylul**, uc gun yayinsiz.
- Sonsuz dongu riski yok, sayac sinirli.

**Zayiflik:** Kie'nin "Internal Error"u `UNKNOWN` olarak siniflandiriliyor ve ICERIK
sayacini (3 hak) yakiyor. Altyapi sayaci (`TRANSIENT_INFRA`, 6 hak + 48 saat)
devreye girmiyor. Motor tarafli bir ariza bolumu "insan baksin"a dusurebiliyor.

### 5.3 QC'de gercek bosluk , kusur 1, 2 ve 4 kapiya takilamaz

`bible.series.qc.notes` yutulma vurusunu ve "merceğe bakis fail" kuralini yaziyor.
Ama `series/critic.py:_decide` **yalniz su alanlara bakiyor**: `anatomy_ok`,
`face_match`, `wardrobe_ok`, `era_ok`, `unwanted_text`, `forbidden_elements`,
`artifact_score` ve terfi edilmis ROCK-B alanlari. Vurus teslimi icin **karar alani
yok**; `issues` listesi karara girmiyor.

Bu seride terfi etmis tek ROCK-B alani `anomaly_match` ve o da
`object_card.anomaly_descriptor`i, yani **ekibin ceneyi acmasini** denetliyor.
Yutulma vurusu denetimsiz. Nitekim ep09 QC kaydi: `verdict: pass`,
`artifact_score: 0`, `issues: []`, `anomaly_match: true/visible/1.0`.

Ayrica ep09 kosusunda **yuz denetimi hic yapilmadi**: `QC: referans yuz indirilemedi
(i.ibb.co read timeout) , face_match denetimsiz`. Kapinin sessizce dusmesi kosuyu
durdurmuyor, yalniz WARNING basiyor. Doktrinin "en onemli denetim" dedigi kapi o gun
kapaliydi.

### 5.4 UYGULANAN DUZELTME , teslim 24 fps'e cekildi

Olcum: yayindaki ep09 **300 kare / 10,01 sn**; `mpdecimate` **242 benzersiz kare**
birakiyor. Yani **58 kare (%19,3) KOPYA**. Kie kaynagi 24 fps uretiyor, boru hatti
30'a cikariyor ve hareket titriyor. `series/bible.py:323` bunu zaten yaziyor ve
`still-home` icin duzeltilmisti; **wild-encounter'a uygulanmamisti**.

`sentinal_ihsan/wild-encounter/bible.json` -> `series.fps = 24` eklendi (+ gerekce
`fps_note`). `final_export` artik `-r 24` ile cagrilacak.
Testler: `tests/test_wild_encounter_contract.py` 11/11, fps/bible/export secimi 19/19.

### 5.5 Denetlenmeyen kalan

**Gunluk beyin wild-encounter'i olcmuyor.** `Gunluk Beyin` is akisi 14 ve 15 Eylul'de
ust uste basarisiz (`event-horizon:olc`, `flashpoints:olc`, `flashpoints:topla`,
`aimagine-fear:olc`) ve listesindeki kanallar arasinda wild-encounter YOK. Filonun
en iyi seridi gunluk ogrenen deftere girmiyor.

## 6. KAC GUN KONSEPT VAR

Kuyrukta **dort yazili plan** var (`plans/part10..13.json`):

| Part | Baslik | Aile | Set |
|---|---|---|---|
| 10 | This GIANT OWL Is NOT Real | bird-giant | jungle_set (tutuldu) |
| 11 | This GIANT SQUID Is NOT Real | sea-giant | ocean_tank_set |
| 12 | This GIANT RHINOCEROS BEETLE Is NOT Real | insect-giant | desert_ruins_set |
| 13 | This GIANT KOMODO DRAGON Is NOT Real | reptile | jungle_set |

**Ama dogru cevap "4 gun" degil: kuyruk kendi kendini dolduruyor.**
`auto_replenish`: `min_queue: 2`, `batch: 5`. Bekleyen plan 2'nin altina inince
Gemini bes yeni bolum yaziyor ve bu **Kie kredisi harcamiyor**. Bu seride
`topic_pool` yok ve kalibrasyon karti yok, yani **sonlu bir konu havuzu yok**.

Pratikte siniri koyan uc sey:
1. **Tanidik, cenesi bir insani alacak kadar buyutulebilir gercek hayvan sayisi.**
   Su ana kadar 9 tane kullanildi. Gercekci havuz 30-50 bandinda, yani **~1 ay bu
   kalipla**; sonra kalip ya da hayvan tanimi genisletilmeli.
2. **Baslik benzersizligi.** Dogrulayici her yeni basligi TUM plan gecmisine karsi
   benzersiz istiyor (`series/replenish.py:1179`). Havuz daralinca ikmal reddedilir.
3. **Kredi.** ep08 ve ep09 defterde **142'ser kredi**. Bakiye 5.474 = **~38 bolum**.
   Aylik tavan 14.000 = ~98 bolum, bagli degil.

**Kisa cevap: makine tarafindan sinirsiz, konsept tarafindan yaklasik bir ay.**

## 7. Bu incelemede olculemedi

- Instagram izlenme ve begeni (hiz siniri / giris duvari). Uc platform
  karsilastirmasi eksik kaldi.
- Retention egrisi ve tamamlanma orani (YouTube Studio verisi gerekiyor; 26.456
  izlenmenin ne kadari dongu bilinmiyor).
- ep09'un neden ep08'in 3,9 kati aldigi. Iki bolum arasinda format ayni; degisen
  sey hayvan (anakonda -> kutup ayisi). **Tek cift, kural cikarma.**
- Kie "Internal Error"unun sebebi. Istek govdesi loglanmiyor; ayni istek yeniden
  gonderilmeden ayirt edilemez.

---

# EK , 18 Eylul 2026: dis video analizi (8,1M motosiklet POV) + Ihsan direktifi

Hedef: `https://www.youtube.com/shorts/daOYkiaV5rQ`
Yontem: yt-dlp ile indirildi, ffmpeg/ffprobe + EBU R128 ile olculdu, kare farki
ve bas bandi enerjisi ayrica hesaplandi, kareler goz ile incelendi.
Kiyas olarak kendi rekorumuz `wuuu02K2hPc` (wild-encounter ep09) ayni yontemle olculdu.

## 1. Hedef video , olculen degerler

| | Deger |
|---|---|
| Kanal | `@Mafiajeon1`, **7.490 abone**, 353 video |
| Yuklenme | 8 Eylul 2026 (olcum gunu ile arasi **10 gun**) |
| Izlenme | **8.111.300** |
| Begeni | 131.431 (**%1,62**) |
| Yorum | 971 (**%0,0120**) |
| Kanal medyani | **7.900 izlenme** (353 video) |
| **Medyan kati** | **1.025x** |
| Abone kati | 1.083x |
| Cozunurluk | 720x1280 (YouTube'un sundugu en yuksek dikey de bu) |
| fps / sure | 29,88 / **15,78 sn** |
| Kesme | **0** |
| LUFS / true peak / LRA | **-14,7** / -5,1 dBFS / **1,1** |
| Desifre | konusma YOK, 0 kelime |

**Kesme sayisi dogrulandi.** `scene` esigi 0,05'e kadar dusuruldu, hicbir kesme
vermedi. Ayrica kare kare fark hesaplandi: en buyuk iki fark **17,3 ve 16,6** (0-255).
Gercek bir kesme 40-80 bandinda olur. Yani video **tek, kesintisiz cekim**.
t=1,87 ve t=6,46'daki tepeler kesme degil, kameranin savrulmasi.

### Yerlesim , piksel piksel olculdu (720x1280 kare uzerinde)

| Bolge | Piksel | Oran |
|---|---|---|
| Ust siyah serit | 0-174 | %13,7 |
| **Beyaz metin banti** | **176-315** | **%11,0** |
| Goruntu alani | 316-1158 (**720x843**) | %65,9 |
| Alt siyah serit | 1159-1279 | %9,5 |

Uc sey buradan cikiyor:

1. **Goruntu karenin sadece %65,9'u.** Altta yatan AI klip neredeyse kare
   (720x843, 1:1,17). 9:16'ya doldurulmamis, **ortaya oturtulmus**.
2. **Metin banti ust ucte bir'de.** `references/olcutler.md` bolum 2'nin
   soyledigi yer tam olarak burasi.
3. **Alt %9,5 siyah.** YouTube'un kullanici adi ve dugmeleri goruntunun uzerine
   degil, siyahin uzerine biniyor. Kadrajin hicbir yeri UI'ya feda edilmemis.

### Ekrandaki metin

```
SOMEONE : OK BYE, SEE YOU TOMORROW!!
("Sometimes, Tomorrow Never Comes...!!")
```

Ust satir **6 kelime** (esik 7'nin altinda), alt satir parantez icinde 5 kelime.
Metin 0. kareden son kareye kadar **hic degismeden** duruyor. Fade yok.
Ust satir kurulum, alt satir vurus. Yani **hikayeyi metin anlatiyor, video kanit.**

## 2. Zaman cizelgesi , goruntu ve bas bandi yan yana

Genel ses seviyesi bastan sona **duz**: 0,1 sn'den sonra hep -13 ile -23 dBFS
arasinda. LRA 1,1 bunu dogruluyor. Ama bu, muzigin duz oldugu anlamina GELMIYOR.
Dinamik **bas bandinda (40-160 Hz)**. Ortalamaya gore normalize edilmis hali:

| t (sn) | Goruntude ne var | Bas |
|---|---|---|
| 0,0 | POV baslar, islak yol, onde beyaz kamyon, gosterge 90 | 0,24 |
| 0,5-3,0 | Sollama, hiz, karsi seride gecis | 1,31 -> **2,08** |
| 3,0-5,0 | **Mavi kamyon karsidan, kare doluyor** | 0,85 -> **0,13** |
| 5,0-6,2 | Mavi kamyon ile beyaz kamyonet arasinda sikisma | 1,11 -> 1,68 |
| **6,3-6,5** | **Carpma. Kamera savruluyor** (en buyuk kare farki) | 1,63 |
| 7,0 | Yerde. Yol kenarinda bir geyik duruyor | **0,13** |
| 7,5-10,0 | Kamyon izgarasi tepede, kask ve parcalar asfaltta | 1,08 -> **1,79** |
| 10,5-12,5 | **Kamera bedeni terk ediyor**, ucuncu sahis, beden motorun uzerinde | 0,30 -> **0,11** |
| 13,0-13,5 | Genis plan, beden ve motor yolda | **2,11 (parcanin en yuksegi)** |
| 14,0 | Kamera asfalta duser | 0,20 |
| 14,5-15,8 | **Seffaf beyaz figur, eller havada. Ruh.** | 0,92 -> 1,39 |

Onset olcumu: 49 vurus, medyan aralik 0,224 sn, yani **~134 BPM**.
Bas bandi araligi: **19,2 kat**. 31 yarim saniyelik kovanin **11'inde** bas
neredeyse yok.

**Olculen sonuc: muzigin dort sessizlesme ve yukselme ani, anlatinin dort
donum noktasina oturuyor.** Kamyon karsidayken bas cekiliyor, carpmada geri
geliyor, beden yerdeyken tamamen bosaliyor, ruh belirmeden hemen once en yuksek
noktasina cikiyor.

**Ama nedensellik iddia etmiyorum.** Olculen sey hizalanma. 134 BPM'lik bir
parcada 15,8 saniye yaklasik 4 olcu eder; rastgele bir baslangic noktasi da
bir miktar ortusme uretir. Dort olayin dordunun birden tutmasi tesadufe gore
zayif bir ihtimal, ama tek ornekle kanit olmaz.

## 3. Ihsan'in iddiasi test edildi

> "muzik cok mukemmel oturmus bu yuzden youtubeda 8.1M izlenmeye ulasmis"

**Hizalanma dogru cikti** (yukaridaki tablo). **Tek basina sebep oldugu olcumle
celisiyor.** Uc kanit:

**1. Kendi rekorumuzun ses dinamigi daha genis, ustelik muziksiz.**

| | 8,1M motor | Bizim ep09 (kutup ayisi) |
|---|---|---|
| Izlenme | 8.111.300 | 36.070 |
| Cozunurluk | 720x1280 | **1080x1920** |
| Sure / kesme | 15,78 sn / 0 | 10,02 sn / 0 |
| LUFS | -14,7 | -14,8 |
| True peak | -5,1 | **-3,0** |
| LRA | 1,1 | **6,6** |
| Bas bandi araligi | 19,2 kat | **28,8 kat** |
| Muzik | var | **YOK** (`bible.json` `"music": false`) |

Bizim video **her teknik eksende esit ya da daha iyi**. Aradaki fark 225 kat.
Teknik ayar bu farki aciklamiyor.

**2. Ayni kanalin 2. ve 3. videosu teknik olarak BOZUK, yine de patlamis.**

| Video | Izlenme | Sure | Kesme | LUFS | True peak |
|---|---|---|---|---|---|
| `-XQ5KiWvW7k` (tisort sakasi, gercek cekim) | 788.000 | 5,28 sn | 1 | -9,6 | **+0,7 KIRPIYOR** |
| `umOCuQNjDSI` | 225.000 | 5,8 sn | 6 | -8,0 | **+1,1 KIRPIYOR** |

Ikisi de esigin cok disinda ve kirpiyor. Bu kanalda teknik kalite kapi degil.

**3. Kanalin kendisi bunu tekrarlayamiyor.** 353 videoda medyan 7.900.
Bu video medyanin **1.025 kati**. Ayni kisi, ayni sablon, ayni muzik pratigi,
353 deneme, bir tane patlama. Formul olsaydi ikinci bir tane olurdu.

### Peki muzik onemsiz mi? Hayir, ve burada gercek bir acik var

Filonun **gunluk yayin yapan iki hattinda da muzik KAPALI**:

- `sentinal_ihsan/wild-encounter/bible.json` -> `"music": false`
- `AImagine-Fear` -> `build.py` icinde ses adimi yok; ustelik `LIST_B_PHRASES`
  listesinde `"background music"` ve `"soundtrack"` **yasakli ifade** olarak
  duruyor (`AImagine-Fear/build.py:148`)

Yani muzik, filonun bilerek kapattigi bir kol. Ihsan'in isaret ettigi sey
**patlamanin sebebi degil ama denenmemis bir degisken.** Ucuz test var,
bolum 6'da.

## 4. Gercekten ayiran sey , olculen ve varsayilan

**Olculen (kanit var):**

- **Begeni orani 3,7 kat yuksek.** %1,62'ye karsi bizim %0,44. Bu dagitim
  farki degil, izleyen kisi basina duygusal tepki farki. Video izletmekle
  kalmiyor, parmak hareket ettiriyor.
- **Yorum orani cok dusuk: %0,0120.** `references/olcutler.md` bolum 3'un
  olctugu ayirt edici bant %0,038-0,058. Bu video onun ucte biri.
  Yani video **tartisilmiyor, sessizce tuketiliyor ve paylasiliyor.**
- **Metin hikayenin kendisi.** Video tek basina bir kaza klibi. Bant onu
  "veda etmek" hakkinda bir cumleye ceviriyor. Paylasilabilir cumle metinde,
  goruntude degil.
- **Kesme yok, konusma yok, dil yok.** Hicbir dile bagli degil. 15,78 saniye
  boyunca tek cekim. Kuresel dagitima uygun.

**Varsayim (kanit yok, boyle isaretliyorum):**

- Konu **birinci sahis olum**. Izleyici kaza izlemiyor, kazayi YASIYOR ve
  sonunda kendi bedenine yukaridan bakiyor. Bu, kaydirilmasi zor bir sey.
- Ilk karede hareket var, gosterge yaniyor, yol islak. `olcutler.md` bolum
  12'nin 1. maddesi.

## 5. IHSAN DIREKTIFI: "motorda olan kisi ben olmaliyim, videoda acikca belli olsun"

### Once teknik gercek: bu formatta yuz gosterilecek TEK bir yer var

POV formatinin gucu, izleyicinin surucu OLMASI. Yuz gosterirsen POV biter.
Ama bu video POV'da kalmiyor. Olculen zaman cizelgesi:

- **0,0-10,0 sn (%63):** birinci sahis. Yuz yok, olamaz da.
- **10,5-14,5 sn (4 saniye):** kamera bedeni terk ediyor, **ucuncu sahis**.
  Surucu kadrajda, motorun uzerinde, yandan gorunuyor.
- **14,5-15,8 sn:** seffaf ruh figuru, eller havada.

**Orijinal video bu 4 saniyeyi harciyor: surucunun kafasinda bastan sona
kapali siyah kask var.** Kim oldugu hicbir karede belli degil.

**Ihsan'in istedigi sey tam olarak o bos slotu doldurmak.** Format zaten bir
kimlik penceresi aciyor, orijinal onu kullanmamis.

### Uretim sartnamesi

| Blok | Sure | Ne olacak |
|---|---|---|
| POV | 0-10 sn | Yuz YOK. Sadece gidon, kol, gosterge, yol. Kimlik ipucu kol ve ceket. |
| **Kimlik penceresi** | **10,5-14,5 sn** | Kamera bedeni terk eder. **Kask yok ya da vizor acik. Ihsan'in yuzu net.** |
| Kapanis | 14,5-15,8 sn | Kapanis plani **ayni yuzu tasir**. Kimlik iki kez dogrulanir. |

Uc sert kural:

1. **Yuz 4 saniyede ve kucuk ekranda okunmali.** Tek kare degil, en az 2,5
   saniye kesintisiz. Profil degil, dortte uc aci.
2. **Kol ve ceket 0. saniyeden itibaren ayni.** POV'da gordugu kol ile 10,5'te
   gordugu adam ayni kisi olmali, yoksa kimlik penceresi ise yaramaz.
3. **Yuz baglama yolu: `character_id` DEGIL `ref_image_url`.** Kie'nin
   `character_ids` alani bu hesapta bozuk, 15 Eylul'de izole edildi
   (`wild-encounter/bible.json:85`). Calisan yol `character_id: null` +
   `ref_image_url`, `series/shots.py:305` onu gorsel referans olarak kullaniyor.
   Ihsan'in mevcut referansi: `https://i.ibb.co/PGFFjg1m/Karakter-Referans.jpg`.
   **Bu URL `face_match` QC'sinde ep09'da timeout verdi**, yani kimlik
   dogrulamasi o kosuda hic calismadi. Kimligin urunun kendisi oldugu bir
   bolumde bu kabul edilemez, referans once kendi barindirdigimiz bir yere tasinmali.

### Iki gercek sorun, karar Ihsan'in

**1. Bu, Ihsan'in kendi olumunu gosteren bir video.** Yuz acikca taninirsa,
tanidiklari baglamsiz gorur ve yuzu kalici olarak bir olum goruntusune baglanir.
Bunu soylemek benim isim, karar Ihsan'in.

**2. Kurulu karakter sozlesmesiyle celisiyor.** `wild-encounter/bible.json`
karakter bio'su aynen soyle diyor: "yaratik onu agzina alir, ekip cenesini acar,
**o yara almadan cikar**". Kanalin 36.000'lik rekoru bu sozlesmeyle geldi.
Olum bolumu onu bozar.

**Onerim (ikisini de coz):** kaza **kil payi atlatilan** bir an olsun, olum degil.
Kimlik penceresi aynen kalir, ruh planinin yerine **surucu yerde, kaskini
cikariyor, kamyon yanindan geciyor** gelir. Metin banti ayni gerilimi tasir:
`"SOMEONE : OK BYE, SEE YOU TOMORROW!!"` -> `("Almost Didn't...!!")`.
Format, sure, kimlik penceresi, muzik yayi degismez. Degisen tek sey son 1,3 saniye.
Bu hem `wild-encounter`in "yara almadan cikar" sozlesmesini korur hem de
1. maddeyi ortadan kaldirir. Ihsan olum versiyonunu isterse yapilir, ama
o zaman ayri bir seride yapilmali, bu kanalda degil.

## 6. Filoda ne degismeli , somut

**A. Metin banti.** Motor zaten metin basabiliyor: `core/ffmpeg_tools.py:1498`
`title_card_overlay(title, subtitle, duration, box=True)`. Iki satir ve kutu
yapisi birebir tutuyor. Iki eksik var:
- `duration` bittiginde son 0,5 sn'de **fade out** yapiyor. Viral videoda bant
  **hic kaybolmuyor**. Fade'siz secenek ya da sure > klip uzunlugu gerekiyor.
- Bant goruntunun **uzerine** basiliyor. Viral videoda goruntu %65,9'a kucultulup
  bant **ustune, bos serite** oturtulmus. Bu yeni bir geometri, `pad` ile eklenir.

**B. `AImagine-Fear` kanonu bu formatla dogrudan celisiyor.** `canon/NEGATIVES.md`
sunlari yasakliyor: `NO on-screen text`, `NO third-person view`, `NO face. NO head.`
Yani Fear hatti **yapisal olarak Ihsan'i gosteremez.** Bu isin evi Fear degil,
`sentinal_ihsan`. Fear kanonuna dokunmak ayri bir karar, 371.000 begeni o kanonla
geldi.

**C. Muzik testi (ucuz, tek degisken).** `wild-encounter/bible.json` `"music": false`.
Bir sonraki iki bolumun **birine** muzik ac, digerini aynen birak. Ayni hafta,
ayni saat, benzer hayvan. Muzik acilinca `produce.py:604, 656, 659` uc davranis
birden degisiyor (`amix_normalize` kapanir, `music_volume` 0,28'den 0,50'ye cikar,
`limit_mix_peak` acilir), yani **yayinlamadan once `tools/audio_master_check.py`
kosulmali.** Bu seride anlatim yok, sadece dogal ses ve muzik olacak.

**D. Kimlik referansini kendi barindirmamiza tasi.** `i.ibb.co` ep09'da timeout
verdi ve QC'yi sessizce atlatti.

## 7. Bu incelemede olculemedi

- **Retention egrisi ve tamamlanma orani.** Baskasinin videosu, Studio verisi yok.
  15,78 sn'nin ne kadarinin izlendigi, dongu olup olmadigi bilinmiyor.
- **Paylasim sayisi.** YouTube disaridan vermiyor. `olcutler.md` bolum 3 paylasimi
  begeninin ustune koyuyor, o sinyal bu raporda YOK.
- **Muzigin kimligi.** Parca tanimlanamadi; aciklama alanindaki etiketler spam
  (kpop ve BTS etiketleri icerige ait degil). Tempo (~134 BPM) ve yapi olculdu,
  eser adi olculmedi.
- **Hizalamanin kasitli olup olmadigi.** Kurgucunun muzigi videoya mi, videoyu
  muzige mi oturttugu disaridan ayirt edilemez.
- **8,1M'in ne kadarinin YouTube disi trafikten geldigi.** Kanal aciklamasi
  klip ve sesin kendisine ait olmadigini soyluyor; kaynak video baska yerde
  viral olmus olabilir.

## 8. Karar ve yapilan is , 18 Eylul 2026

**Ihsan karari (ayni gun, iki asamada):**

1. Kil payi versiyonu secildi. Olum plani yok: Ihsan yerde, kaskini cikariyor,
   kamyon yanindan geciyor. Bolum 5'teki iki gerekce de bu kararla kapandi.
2. **"Sadece bir video uretecegiz, otomasyona baglamiyoruz."** Yeni seri,
   `auto_replenish`, aile havuzu, cron ve yayin akisi KURULMADI. Uretilen sey
   tek bir dosya.

### Motor kisiti , once bu olculdu, format onu takip etti

| Motor | Sure | Yuz referansi |
|---|---|---|
| **Omni** | **en fazla 10 sn** (`OMNI_VALID_DURATIONS` = 4/6/8/10) | `image_urls` ile CALISIR |
| Seedance | 4-15 sn | yalniz `first_frame_url`, karakter referansi YOK |

Referans video 15,78 saniye. Ama yuzun baglanabildigi tek motor 10 saniyede
duruyor, Seedance ise sadece ilk kareyi aliyor ve POV acilisinda kadrajda yuz
olmadigi icin kimligi tasiyamaz. **Yuz urunun kendisi oldugu icin 10 saniye
secildi.** Kayip degil: kanalin rekoru (ep09, 36.000) zaten 10 sn tek plan.

Bloklarin 15,78 sn'den 10 sn'ye tasinmasi:

| Blok | Referans | Bizim |
|---|---|---|
| POV, yuz yok | 0-10,0 sn | 0-4,0 sn |
| Carpma / kacinma | 6,3-6,5 sn | 4,0-5,5 sn |
| **Kimlik penceresi, yuz net** | 10,5-14,5 sn | **5,5-10,0 sn (4,5 sn)** |

Kimlik penceresi ORANSAL OLARAK BUYUDU (%25 -> %45). Referansta o pencere
kapali kaskla harcanmisti; burada islevi kimligin kendisi.

### Motordaki eksik kapandi (bolum 6A)

`core/ffmpeg_tools.py` icine **`caption_banner_overlay()`** eklendi.
`title_card_overlay`'den uc farki var ve ucu de olcumden geliyor:
bant erimez, goruntunun ustune degil disina basilir, metin hikayeyi anlatir.

Dogrulandi:

- **Geometri referansla birebir**: ust serit %13,7 / bant %11,0 / goruntu %65,9 /
  alt serit %9,5. Gercek dosyada olculdu, tahmin degil.
- **Cikti cozunurlugu korunuyor.** Ilk surum oransal `pad` kullaniyordu ve
  yuvarlama kaymasi 1920'yi **1918'e** dusuruyordu. Mutlak piksele cevrildi.
- Uzun baslik banda sigmazsa font kucultulur, bant TASMAZ ve goruntunun yeri
  kaymaz.
- Kesme isareti iceren altyazi (`("I Almost Didn't...!!")`) drawtext'i kirmiyor.

Baglanti: `series/bible.py` icinde `caption_banner` opt-in alani,
`series/produce.py` icinde kunyeden SONRA / fact-caption'lardan ONCE uygulanan
blok, ve `caption_banner` artik taninan bir zorunlu teslimat katmani.

**Mevcut seriler etkilenmiyor.** Alan yazilmamis her bible icin deger `{}`,
yani blok hic calismiyor. `tests/test_caption_banner.py` bunu kilitliyor:
dort canli hattin bible'larinda alanin BULUNMADIGI ayrica test ediliyor.
6 test gecti. Depo genelinde 1140 test gecti, 5 test kirik , o 5 test
degisiklikler geri alinmis halde de kirik, yani bu isle ilgisiz
(`test_experiment_runner` 4 + `test_rock5_containment` 1).

### Bant metni

```
SOMEONE : OK BYE, SEE YOU TOMORROW!!
("I Almost Didn't...!!")
```

Referansin kurulum/vurus kalibi korundu, sonuc olumden kurtulusa cevrildi.
Alt satir BIRINCI SAHIS: kimligi metin de tasiyor, sadece yuz degil.

### Bu videodan kural cikarilamaz

Tek dosya uretildi ve ayni anda uc sey birden degisti: konsept, ekran yazisi ve
muzik. Tuttugunda ya da tutmadiginda **hangisinin yaptigi ayristirilamaz.**
Muzigi tek degisken olarak olcmek hala bolum 6C'deki `wild-encounter` A/B
testini gerektiriyor; bu video onun yerine GECMEZ.

## 9. Uretim , 18 Eylul 2026, iki surum teslim edildi

Klasor: `output/tek_seferlik/motor_kilpayi/`

| Dosya | Nedir |
|---|---|
| `05_SURUM_A_motor_sesli.mp4` | motor sesi + muzik birlikte |
| `05_SURUM_B_muzik_tek.mp4` | **muzik tek ses** (referans videonun yaptigi sey) |
| `00_ilk_kare.jpg` / `00_son_kare.jpg` | kilitlenen iki kare |
| `01_ham.mp4` / `02_muzik.mp3` | ham klip ve Suno parcasi |

### Olculen sonuc

| | Bizim video | Referans (8,1M) |
|---|---|---|
| Cozunurluk | 720x1280 | 720x1280 |
| Sure | 10,1 sn | 15,78 sn |
| **Kesme** | **0** | **0** |
| LUFS (A / B) | -14,1 / -14,9 | -14,7 |
| True peak (A / B) | -2,7 / -1,3 | -5,1 |
| Kredi | 248 (video) + gorseller | , |

Yerlesim referansla ayni: ust serit %13,7 / bant %11,0 / goruntu %65,9 /
alt serit %9,5. Bant 0. kareden son kareye kadar degismiyor.

Zaman cizelgesi kare olcumuyle dogrulandi: 0-2 POV ve kamyon yaklasiyor,
3 kamyon kadraji dolduruyor, 4 kacinma ve kamyon siyiriyor, 5-6 kamera yerde
ve geri cekiliyor, **7-10 Ihsan'in yuzu net**. Kimlik penceresi 3,5 saniye,
2,5 sn tabanini gecti.

### Uretim yolu , iki motor dustugu icin ucuncu yol kullanildi

Planlanan yol Omni idi (yuzu `ref_image_url` ile baglar). Kosmadi:

| Deneme | Sonuc |
|---|---|
| Omni, tam prompt + yuz referansi | 5/5 "Internal Error" |
| **Omni, zararsiz 4 sn prompt, GORSEL YOK** | **basarisiz , arizanin promptla ilgisi yok** |
| Veo `REFERENCE_2_VIDEO` + yuz referansi | 2/2 "Internal Error" |
| Seedance, yalniz son kare | HTTP 422 "Not supporting only transmitting the last frame" |
| **Seedance, ilk kare + son kare** | **basarili, 248 kredi** |
| Kredi bakiyesi | 9.997, sorun bakiye degil |

Calisan yol: kimlik penceresi videonun SONUNDA oldugu icin yuzu **son kare**
kilitliyor. Son kare `generate_image` ile Ihsan'in referansindan uretildi ve
**goz ile onaylandiktan sonra** video kredisi harcandi. Ilk kare de POV
acilisini kilitliyor; ikisi arasindaki kaza Seedance tarafindan uretiliyor.
Bu, referans gorsel kabul eden motorlar dustugunde kimligi tasimanin
calisan yolu olarak duruyor.

### ⛔ CANLI ARIZA , bu videoyla ilgili degil, filoyu ilgilendiriyor

Kie'nin **Omni ucu dusmus.** Arizanin baslangici 18 Eylul 17:45 ile 18:18 UTC
arasi. Kanit tek makineden degil, bulut kosularindan:

- `Wild Encounter Daily` 17:45 UTC **basarili** (arizadan once)
- `Still Home Daily` 18:18 UTC **basarisiz**: Omni "Internal Error", 5/5 deneme,
  "En az cekim kapisi artik karsilanamaz: kabul=0"
- Bizim denemeler 18:24 UTC sonrasi, ayni hata

**Omni'de kosan hatlar:** `wild-encounter`, `one-variable`, `still-home`.
`flythrough` Seedance kullaniyor, etkilenmiyor. Ariza surerse yarinki
kosularda bu uc hat da duser.

### Olculen ders: motor sesi ile muzigin yayı ayni anda olmuyor

Ihsan'in isaret ettigi sey muzigin yayiydi. Suno istenen yapiyi gercekten
uretti: ham parcada bas bandi araligi **43,8 kat** (referans videoda 19,2 kat),
2,5-3,5 sn arasinda bas tamamen cekiliyor ve 4,0'da geri carpiyor.

Ama miksten sonra yay kayboldu. Olculdu:

| Miks | Bas bandi araligi |
|---|---|
| Muzik 0,45, motor sesi acik | **2,9 kat** |
| Muzik 0,85, motor sesi acik | **3,0 kat** |
| **Muzik tek ses** | **43,7 kat** |

**Muzigi yukseltmek ise yaramiyor.** Basi dolduran sey motor ve lastik sesi;
surekli ve genis bantli oldugu icin muzigin sustugu anlari kapatiyor, sonra
loudnorm hepsini yeniden normalize ediyor. Yay ancak dogal ses TAMAMEN
cikarilinca yasiyor.

Referans video da zaten muzik-tek ses: LRA 1,1, dogal ses yok. Yani
8,1M'lik video bu tercihi yapmis. **Surum B o tercihi kopyaliyor, surum A
gercekcilik icin motor sesini koruyor ve bunun bedeli olculmus haliyle
yayin %93'u.**

### Bu videodan hala kural cikarilamaz

Bolum 8'in sonundaki uyari gecerli: konsept, ekran yazisi ve muzik ayni anda
degisti. Ayrica surum A ile B arasindaki fark da ayri bir degisken. Tuttugunda
hangisinin yaptigi ayristirilamaz.
