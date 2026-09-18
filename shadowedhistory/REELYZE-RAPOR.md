# shadowedhistory , video analiz raporu

Tarih: 10 Eylul 2026 (Los Angeles)
Yontem: yt-dlp ile indirildi, ffmpeg/ffprobe + EBU R128 ile olculdu, kareler goz ile incelendi.
Metodoloji ve esikler: `Projeler/Reelyze_Arastirma/REELYZE-DOSYASI.md`

---

## 1. Kanal durumu

| | |
|---|---|
| Abone | 127 |
| Toplam video | 271 (filoda en cok video) |
| Toplam izlenme | 109.787 |
| **30 gunluk medyan izlenme** | **27** |

Karsilastirma: `sentinal_ihsan` 1.292 , `galactic_experiment` 88,5 , `shadowedhistory` 27 , `aimagine` 4.
En cok video ureten kanal, ama medyan 27. **Uretim yuksek, verim dusuk.**

### Son yayinlar , asiri degisken
| Video | Tarih | Izlenme |
|---|---|---|
| The Real Reason The Hundred Years' War Lasted 116 Years | 9 Eyl | 52 |
| Henry "Box" Brown: The Unbreakable Man | 8 Eyl | **5** |
| The Real Reason America Invaded An Empty Island! | 7 Eyl | 19 |
| The Great Fire Of London: Fact Or Ancient Propaganda? | 6 Eyl | 23 |
| **How Brooklyn Bridge Spanned The East River In 1883!** | 5 Eyl | **509** |
| How Laughter Paralyzed Tanganyika In 1962! | 4 Eyl | 22 |
| Wrangel Mammoths: The Last Survivors | 1 Eyl | **1.179** |
| The Real Reason Cleopatra Ruled Without Translators | 31 Agu | 6 |

5 izlenme ile 1.179 izlenme arasinda saliniyor. Iki aykiri var (Wrangel Mammoths 1.179,
Brooklyn Bridge 509), geri kalan 5-52 bandinda. **Aykirilarin ne yaptigini bulmak
bu kanalin tek meselesi.**

---

## 2. Olculen teknik durum

| Video | Izlenme | Cozunurluk | fps | Sure | Kesme | En uzun plan | LUFS | True peak | WPM |
|---|---|---|---|---|---|---|---|---|---|
| Brooklyn Bridge (HIT) | 509 | 1080x1920 | 30 | 9,4 sn | **0** | 9,44 sn | **-23,6** | -9,7 | 76 |
| Hundred Years (son) | 52 | 1080x1920 | 30 | 9,4 sn | 1 | 8,33 sn | **-25,1** | -10,1 | 70 |
| Henry Box Brown (olu) | 5 | 1080x1920 | 30 | 19,1 sn | 1 | 9,57 sn | **-20,5** | -6,9 | 119 |

Hedef: **-16 ila -13 LUFS**. Olculen: **-20,5 ile -25,1**.

### Bulgu A: Filodaki EN SESSIZ kanal
-25,1 LUFS, hedefin **12 dB** altinda. `sentinal_ihsan` -14,3 olcuyor ve 1.292 medyan aliyor.
12 dB pratikte "sesi dort kat kisik" demektir. Anlatim tabanli tarih icerigi icin
bu oldurucudur: telefonda, disarida, ya da ses kisikken video sessiz gibi.

Ortak motorda hazir cozum var (`core/ffmpeg_tools.py:234-372`, hedef I=-14, TP=-1,0),
ciktida uygulanmamis. **Bu kanalin bir numarali isi budur.**

### Bulgu B: Kanalin en iyi videosunda EKRAN YAZISI VAR
Brooklyn Bridge (509 izlenme) ilk karesine baktim: kopru insaatinin donem gorseli
uzerine, **ust-orta ucte bir**, yuksek kontrastli beyaz kalin harflerle:

```
BROOKLYN BRIDGE
New York City, 1883
```

Bu tam olarak Reelyze'in yayin oncesi kontrol listesindeki 3. madde: *"okunakli kanca
satiri, 7 kelimenin altinda, 1. saniyeden once ekranda, ust-orta ucte bir, dip %15 yasak
bolgeden uzak."* Kanalin en iyi ikinci videosu bunu tutturmus.

Motorda `title_card_overlay` (`core/ffmpeg_tools.py:1362`) ve `fact_captions_overlay`
(`:1445`) var ve bu kanal cagiriyor (`series/produce.py:2095-2107`).
**Kontrol edilmesi gereken: her videoda basiliyor mu, yoksa bazilarinda atlaniyor mu?**

### Bulgu C: 9,4 saniye cok kisa olabilir
Uc videodan ikisi 9,4 saniye. Kendi olctugumuz aykiri veri 0-7 saniye kovasini en iyi
(nis medyanina gore 1,69 kat) gosteriyor, yani kisa kotu degil. Ama 9,4 saniyede
70-76 WPM ile ancak 11-12 kelime soylenebiliyor. Bir tarih anlatisi icin bu cok az.
**Kisa olmasi sorun degil, kisa olup da hicbir sey soylememesi sorun.**

En dusuk performansli video (Henry Box Brown, 5 izlenme) tam tersine 19,1 saniye ve
119 WPM, yani 38 kelime. Iki uc da calismamis.

### Bulgu D: Sifir kesme
Brooklyn Bridge'de 0 kesme, tek plan 9,44 saniye. Tavan 4 saniye.
Bu videonun kazanmasinin sebebi kesme degil, baslik karti ve konunun taninirligi.

---

## 3. Iki aykiri ne yapmis

| | Wrangel Mammoths (1.179) | Brooklyn Bridge (509) | Digerleri (5-52) |
|---|---|---|---|
| Konu | mamutlar, Misir piramitlerinden sonra yasadilar | dunyaca unlu yapi | niche tarih olaylari |
| Taninirlik | yuksek (mamut) | **cok yuksek** | dusuk (Tanganyika, Cleopatra ceviri) |

**Hipotez: taninabilirlik.** Brooklyn Bridge ve mamut herkesin bildigi seyler.
"How Laughter Paralyzed Tanganyika In 1962" ilgi cekici ama izleyici Tanganyika'nin
ne oldugunu bilmiyor, yani ilk 3 saniyede "bu benim icin mi" sorusuna cevap yok.

Reelyze'in kurali birebir bunu soyluyor: *"kanca KATEGORI degil PROBLEM adlandirmali...
bir kanca izleyicinin bildigi bir seyle acilmali."* Bilinmeyen bir yer adiyla acilan
video izleyiciden is istiyor.

Bu test edilebilir: sonraki 8 videonun 4'unu dunyaca unlu bir konuyla, 4'unu niche
konuyla uret, karsilastir.

---

## 4. Ne yapilmali (etki sirasina gore)

1. **SES SEVIYESI. Filodaki en kotu, en acil is.** -25 LUFS'tan -14 LUFS'a.
   `core/ffmpeg_tools.master_audio` zaten var, cagrilmasi yeterli.
2. **Baslik kartinin HER videoda basildigini dogrula.** Kanalin en iyi videosunda var.
   Basilmayan varsa sebebini bul.
3. **Konu havuzunu taninabilirlige gore ele.** Konu secerken tek soru:
   *"Ortalama bir izleyici bu ismi daha once duydu mu?"* Duymadiysa ilk 3 saniyede
   taninan bir seye baglamak zorunda.
4. **Sifir kesmeli video birakma.** Tavan 4 saniye.
5. **Sureyi 12-18 saniyeye cek.** 9,4 saniye ile anlati kurulamiyor, 19,1 saniye ile
   izleyici birakiyor. Arasi denenmemis.

## 5. Neye DOKUNMA

- Cozunurluk 1080x1920 ve fps 30 dogru.
- Ortak motor (`core/`, `series/`) , dort kanali birden besliyor. Ses duzeltmesi
  buraya girecekse `sentinal_ihsan`'i bozmamali (o zaten dogru: -14,3).
- `flashpoints/bible.json` ve `series.json` , kanal kimligi.
- `footnotes` duraklatilmis, oyle kalsin.

## 6. Acik sorular (olculemedi)

- Retention egrileri (YouTube Studio gerekiyor)
- Ses neden -25 cikiyor: loudnorm cagriliyor mu, cagriliyorsa neden tutmuyor?
  Kod okumasi netlestirmedi, calisma zamaninda olculmeli.
- Taninabilirlik hipotezi 2 ornege dayaniyor, kanit degil. Kasitli test gerekiyor.
- 271 videonun tamaminin dagilimi (sadece son 15'i olculdu). Tum gecmisi tarayip
  aykirilari cikarmak bu kanal icin cok degerli olur.


---

## EK , KOK NEDEN BULUNDU (10 Eylul, uc bagimsiz yoldan dogrulandi)

Ses seviyesi sorununun sebebi tek bir eksik alan:

```
series/bible.py:284      series["master_lufs"] okunuyor
series/produce.py:2147   master_lufs = bible.master_lufs
series/produce.py:2148   if master_lufs is None:   ->  MASTERING TAMAMEN ATLANIYOR
series/produce.py:2161   target_i=master_lufs, target_tp=-1.0, target_lra=11.0
```

Tum aktif serilerde `series.master_lufs` alani tarandi:

| Seri | Kanal | master_lufs | Olculen LUFS | 30g medyan izlenme |
|---|---|---|---|---|
| `unnatural-lab` | sentinal_ihsan | **-14** | **-14,3 / -14,8** | **1.292** |
| `event-horizon` | galactic_experience | YOK | -21,9 / -24,7 | 88,5 |
| `flashpoints` | shadowedhistory | YOK | -20,5 / -25,1 | 27 |
| `next-stop` | aimagine | YOK | -16,1 / -17,1 (peak +0,7 KIRPIYOR) | 4 |

**Filoda `master_lufs` tanimli TEK seri `unnatural-lab` ve o da tek iyi performans
goesteren seri.** Diger her seride alan yok, bu yuzden `produce.py` mastering adimini
tamamen atliyor ve ham miks ne cikiyorsa o yayinlaniyor.

### Duzeltme (tek satir)
Ilgili `bible.json` dosyasinda `series` blogunun icine:
```json
"master_lufs": -14
```
Referans: `sentinal_ihsan/unnatural-lab/bible.json:11`.

### Dogrulama yontemi
1. ffmpeg EBU R128 ile yayinlanmis videolar olculdu (yt-dlp ile indirildi)
2. Codex kod incelemesi bagimsiz olarak ayni yeri isaret etti
3. Tum `bible.json` dosyalari tarandi, alan sadece bir yerde bulundu

Ucunun de ayni sonuca varmasi bunu tahmin degil TESPIT yapiyor.

### Uyari
Bu tek satir sesi duzeltir, **erisimi duzeltmez**. `unnatural-lab` sadece sesi dogru
oldugu icin 1.292 almiyor; format kalibi da dogru (bkz. `sentinal_ihsan/REELYZE-RAPOR.md`).
Ses duzeltmesi bir on kosul, tek basina yeterli degil.

---

## !!! UYARI , `master_lufs` TEK SATIRLIK DEGIL (10 Eylul, r2 incelemesi)

Yukarida "duzeltme tek satir" yazdim. **Bu eksik bilgiydi.** `master_lufs` alani
sadece mastering acmiyor, `produce.py` icinde UC davranisi birden ceviriyor:

```
series/produce.py:604   amix_normalize = bible.master_lufs is None
                        -> alan eklenince amix normalizasyonu KAPANIR
series/produce.py:656   music_volume = 0.50 if bible.master_lufs is not None else 0.28
                        -> muzik seviyesi 0,28 den 0,50 ye cikar (neredeyse iki kat)
series/produce.py:659   limit_mix_peak = bible.master_lufs is not None
                        -> tepe limitleyici ACILIR
```

Koddaki kendi yorumu bunun kasitli oldugunu soyluyor:

> normalize=0 programi legacy mikse gore 6,1 LU yukselttigi icin opt-in yatak
> 0.50 ye eslendi (foley/yatak +6,19 dB; anlatim/yatak degisimi +0,42 dB).
> Legacy yol 0.28 kalir.

Yani 0,50 degeri `normalize=0` ile BIRLIKTE calismak uzere kalibre edilmis, tutarli
bir tasarim. **Ama kalibrasyon `unnatural-lab` in ses profiline gore yapilmis.**

### Risk

`unnatural-lab` dogal ses agirlikli. `event-horizon` (126-156 WPM) ve `flashpoints`
(70-119 WPM) ise **yogun TTS anlatimi** iceriyor. Muzigin 0,28 den 0,50 ye cikmasi
bu iki kanalda anlatimi bogabilir.

### Dogru yaklasim

Alani ekleyip dogrudan yayinlamayin. Sirasiyla:

1. Alani ekle
2. **Yayinlamadan** bir uretim kosusu yap (her seri icin AYRI, uc ses yolu farkli)
3. Cikan dosyada su ucunu birden olc:
   - integrated loudness (hedef -15,0 ile -13,0)
   - true peak (<= -1,0 dBTP)
   - **anlatim/muzik dengesi** , kulakla dinle, muzik anlatimin onune gecmis mi
4. Denge bozuksa `native_mix_level` veya muzik seviyesi ayrica ayarlanmali

### Ayrica: mevcut bir test kirilacak

`tests/test_rocka_audio_master.py:117` , `test_only_unnatural_lab_has_master_lufs`

Bu test tam olarak "sadece unnatural-lab da olsun" diye yazilmis. Alan eklenince
KIRILACAK. Testi silmeyin, **yeni dogru yapilandirmayi dogrulayacak sekilde
guncelleyin** ve alansiz seri davranisinin kapsamini ayrica koruyun.

---

## EK , BASLIK ANALIZI (10 Eylul 2026, 29 yayinlanmis bolumun tamami)

Yontem: `published.json` -> yt-dlp ile her bolumun canli izlenme, begeni ve sure verisi.
Ayrica katalogdaki her baslik elle siniflandirildi (atamalarin tamami asagida, denetlenebilsin diye).

**Olculemedi:** yorum sayisi. yt-dlp 29 videonun 29'unda da `NA` dondu (kanalda yorumlar
kapali ya da disari verilmiyor). Reelyze olcutlerinde ayirt edici sinyal olarak yorum orani
gecer; bu kanalda o sinyal KULLANILAMADI. Yerine begeni orani konmadi, cunku ayni olcutler
begeni oranini ayirt etmez sayiyor. Bu bir bosluktur, tahminle doldurulmadi.

### Bulgu 1: baslik KALIBI hicbir sey ongormuyor

Dort kalip ayristirildi ve izlenmeye karsi cizildi:

| Kalip | n | medyan | en dusuk | en yuksek |
|---|---|---|---|---|
| The Real Reason X | 11 | 51 | 0 | 795 |
| How X ... In YYYY! | 6 | 24 | 17 | 509 |
| X: Fact Or Ancient Propaganda? | 4 | 24 | 0 | 143 |
| Isim: Nitelemesi | 8 | 24 | 5 | 1179 |
| **kanal geneli** | **29** | **24** | | |

"The Real Reason X" ilk bakista iki kat iyi gorunuyor (51 vs 24). Ama donemlere bolununce
cokuyor: erken donemde (part 1-20) medyani 78, gec donemde (part 21-30) **19**. Kalibin
avantaji zamanla ilgili, kalipla degil , 11 kullaniminin 8'i erken donemde.

Asil kanit su: **her kalipta hem bir hit hem bir sifir var.** A'da 795 ve 0, D'de 1179 ve 5,
C'de 143 ve 0, B'de 509 ve 17. Baslik kalibi ayirt etmiyor.

### Bulgu 2: baslikin OZNESI ongoruyor , ve bu bulgu doneme dayaniyor

Her baslik oznesine gore uce ayrildi:
- **SEY** = yapi, eser, malzeme, hayvan, kurum, marka (gozde canlanan somut bir sey)
- **OLAY** = savas, yangin, sel, hadise
- **KISI** = adiyla anilan bir birey

| Ozne | n | medyan | ortalama | en dusuk | en yuksek |
|---|---|---|---|---|---|
| **SEY** | 12 | **80** | 264 | 2 | 1.179 |
| OLAY | 9 | 20 | 27 | 9 | 90 |
| **KISI** | 8 | **8** | 46 | 0 | 193 |

SEY / KISI orani **10 kat.** Ve kritik test olan donem bolunmesinden sag cikiyor:

| Donem | SEY | OLAY | KISI |
|---|---|---|---|
| erken (1-20), donem medyani 29 | 54 (n=9) | 19 (n=4) | 12 (n=6) |
| gec (21-30), donem medyani 24 | 509 (n=3) | 23 (n=5) | 6 (n=2) |

Siralama (SEY > OLAY > KISI) HER IKI donemde de ayni. Baslik kalibi bulgusu donem
bolununce ters donuyordu; bu donmuyor.

**Ucta ne var:**

100 izlenmeyi gecen 8 bolumun 6'si SEY (mamut, Nintendo, Brooklyn Koprusu, Roma betonu,
Kolezyum, Roma idrar camasirhanesi). Iki istisna KISI: Napoleon (193) ve Hiroo Onoda (142).

10 izlenmenin altindaki 7 bolumun 5'i KISI: Gladiators (0), Cleopatra x2 (0 ve 6),
Henry Box Brown (5), Tsutomu Yamaguchi (9).

### Bu bulgu, raporun "taninabilirlik" hipotezini CURUTUYOR

Bu dosyanin ust kismindaki hipotez "izleyicinin bildigi konu kazanir" diyordu ve iki ornege
dayaniyordu. 29 bolumluk veri bunu tutmuyor:

- **Cleopatra** dunyanin en taninan tarihi figurlerinden biri. Iki bolum: **0 ve 6 izlenme.**
- **Gladiators** herkesin bildigi bir kavram. **0 izlenme.**
- Buna karsilik **Wrangel mamutlari** (1.179) ve **Nintendo oyun kagitlari** (795) taninan
  degil, BEKLENMEDIK konular.

Ayirt eden sey konunun taninmasi degil, oznenin **gozde canlanan bir SEY** olup olmadigi.
Kolezyum 143 alirken Gladiators 0 aliyor , ayni kalip, ayni cag, ayni taninirlik.
Fark: Kolezyum bir yapi, Gladiators bir insan sinifi.

### Duyarlilik testi (siniflandirma benim yargim, olcum degil)

Tartismali yedi atama tek tek degistirildi ve ucu ayni anda degistirildi:

| Degisiklik | SEY | OLAY | KISI | siralama |
|---|---|---|---|---|
| temel | 80 | 20 | 8 | korundu |
| Gladiators KISI -> SEY | 54 | 20 | 9 | korundu |
| Gladiators KISI -> OLAY | 80 | 20 | 9 | korundu |
| tomato pills SEY -> OLAY | 105 | 20 | 8 | korundu |
| Roma idrar SEY -> OLAY | 54 | 22 | 8 | korundu |
| Napoleon KISI -> OLAY | 80 | 22 | 6 | korundu |
| Onoda KISI -> SEY | 105 | 20 | 6 | korundu |
| tree rings SEY -> OLAY | 105 | 22 | 8 | korundu |
| **uc degisiklik ayni anda** | **54** | **20** | **9** | **korundu** |

Siralama hicbirinde bozulmadi.

### Ne yapilmali , ve ne YAPILMAMALI

**YAPILMAMALI: `unutulmus kisi` ailesini havuzdan atmak.** Aile listesi doktrin v1.2'de
kanonik enum yapildi ve ardisiklik ihlali RED aliyor. Bir aileyi bosaltmak ikmali
cozulemez hale getirir ve kosu yine yesil doner. Aileye dokunma.

**YAPILMALI: kisi konularinda basligi kisiden degil, hikayedeki SEY'den kurmak.**
Bulgu konunun kendisiyle degil BASLIGIN OZNESIYLE ilgili. Ayni kisi konusu, oznesi
degistirilerek yazilabilir:

| Havuzdaki konu | Bugunku kalip (KISI) | Onerilen (SEY) |
|---|---|---|
| id 44, John Snow kolerayi tek bir su pompasina baglar | "John Snow: The Father Of Epidemiology" | "The Water Pump That Ended London's Cholera Outbreak" |
| id 41, Witold Pilecki Auschwitz'e bilerek girer | "Witold Pilecki: The Volunteer" | "The Auschwitz Report Nobody Believed" |
| id 43, Mary Seacole Kirim'a kendi parasiyla gider | "Mary Seacole: The Rejected Nurse" | "The Hotel A Rejected Nurse Built On The Crimean Front" |

Kanalin kendi verisi bunu destekliyor: KISI kovasindaki iki basarili bolum de oznesini
bir KAVRAMA baglamis ("Hiroo Onoda: **The Last Samurai**", 142) ya da zaten kuresel olarak
taninan bir isim tasiyor (Napoleon, 193). Bilinmeyen isimle acilan her bolum dipte:
Zheng Yi Sao 16, Tsutomu Yamaguchi 9, Henry Box Brown 5.

**Havuzda hazir bekleyen SEY konulari (oncelik verilmeli):** id 36 Pisa Kulesi,
id 37 Panama Kanali, id 38 Londra kanalizasyonu, id 39 Sydney Limani Koprusu,
id 49 Viking boynuzlu miğfer yanilgisi. Dordu de unlu yapi , kanalin en iyi kovasi.
Havuzda 19 konu kalmis, `next_part` 31 / `total_parts` 35.

### Durust sinirlar

- Gec donemde kova basina n kucuk (SEY n=3, KISI n=2). Siralama tutuyor ama gec donem
  tek basina kanit degil.
- Siniflandirma bir olcum degil, benim yargim. Bu yuzden 29 atamanin tamami ve duyarlilik
  testi yukarida acikta.
- Bu bir KORELASYON. Baslik oznesinin izlenmeyi NEDEN etkiledigi olculmedi; muhtemel
  mekanizma (kapak karesi + baslik birlikte "bu ne" sorusuna ilk saniyede cevap veriyor)
  test edilmedi.
- Retention egrileri hala yok (YouTube Studio gerekiyor). Baslik tiklanmayi etkiler,
  izlenmeyi tutan sey ayri bir mesele.

**Onerilen test:** sonraki 8 bolumun 4'unu SEY oznesiyle, 4'unu KISI oznesiyle uret
(konu havuzundan ayni aile karisimini koruyarak) ve karsilastir. Bu, hipotezi 8 bolumde
kesin olarak dogrular ya da curutur.

---

# EK , @one__create referans analizi (13 Eylul 2026)

Ihsan kanali gelecek temali, ANLATIMSIZ bir konsepte cevirme karari verdi ve
kopyalanacak referans olarak `instagram.com/one__create` hesabindan 5 video verdi.

Yontem: 5 video `yt-dlp` ile en yuksek dikey rendition'da indirildi,
`ffmpeg`/`ffprobe` + EBU R128 ile olculdu, kontakt sayfalari goz ile incelendi.
Etkilesim sayilari IG meta verisinden alindi. Dosyalar oturum scratchpad'inde.

## 1. Olculen bicim , 5/5 videoda ayni

| Olcu | Deger | Not |
|---|---|---|
| Cozunurluk | 1080x1920 (4/5), 1440x2560 (1/5) | dikey |
| fps | 24 (4/5), 30 (1/5) | sinema hissi |
| Sure | 5,5 / 6,9 / 7,1 / 8,1 / **10,1** sn | cok kisa |
| Kesme | 1 (4/5), 2 (1/5) | yani **2 cekim** |
| LUFS | **-14,0 .. -14,1** | bes videonun besi de |
| True peak | -1,6 .. -2,7 dBFS | ,  |
| LRA | **1,0 .. 1,5** | neredeyse sifir dinamik |
| Desifre | **0 kelime** | anlatim YOK, dogrulandi |

## 2. "Derin ses" olculdu , alcak geciren drone

Bant enerjisi (mean_volume, dB):

| video | 20-80Hz | 80-250 | 250-2k | 2k-8k | 8k-16k |
|---|---|---|---|---|---|
| TOKYO 2247 | -21,6 | -22,4 | -21,5 | -47,9 | -62,4 |
| monsun | -21,9 | -22,4 | -21,4 | -50,4 | -90,3 |
| buz kubbe | -22,0 | -22,0 | -21,8 | -51,0 | -81,9 |
| col kubbe | -22,1 | -22,0 | -21,9 | -51,1 | -90,3 |
| duvar carsi | -22,9 | -21,9 | -21,6 | -51,0 | -76,5 |

Okuma: 20 Hz , 2 kHz arasi **duz ve guclu** (-21..-22 dB), 2-8 kHz **29 dB asagida**,
8 kHz ustu pratikte **yok**. Bu bir muzik parcasi degil: ~2 kHz'de tavanlanmis,
LRA 1,0-1,5 ile neredeyse hic dalgalanmayan **sabit derin ugultu**. Tiz yok,
vurus yok, konusma yok. Ihsan'in "hepsinde derin bir ses var" gozlemi bu.

## 3. Baslik karti , DAKTILO efekti

4 fps kontakt sayfasiyla kare kare izlendi:

- t=0,00 `TO` , t=0,25 `TOKYO 22` , t=0,50 `TOKYO 2247` (tamam)
- Ikinci videoda ayni: `EAR` , `EARTH 224` , `EARTH 2247`

Yani basliktaki harfler **tek tek yaziliyor, ~0,5 sn'de bitiyor**. Sonra ilk cekim
boyunca duruyor ve **kesmede ~0,4 sn icinde soluyor**; ikinci cekimde baslik YOK.

Yerlesim: sol ust, ~%6 sol kenar bosluğu, ~%20 ustten. Tamami buyuk harf,
kalin sikisik grotesk. **Yazi tipi tam teshis edilemedi**; Anton / Archivo Black
ailesine benziyor, kesin ad iddia etmiyorum.

Renk kontrasta gore secilmis: acik gokyuzu zeminde SIYAH (4/5), yogun koyu
sehir zemininde BEYAZ (1/5).

## 4. Etkilesim , ve kazanani ayiran sey

| video | begeni | yorum | yorum/begeni |
|---|---|---|---|
| **TOKYO 2247** | **46.042** | **848** | %1,84 |
| monsun / ikinci zemin | 2.597 | 36 | %1,39 |
| col kubbe | 328 | 1 | %0,30 |
| buz kubbe | 307 | 1 | %0,33 |
| duvar ici carsi | 124 | 2 | %1,61 |

Ihsan TOKYO videosunun **5,6M izlendigini** soyledi. IG oynatma sayisi meta veriden
CEKILEMEDI (yalniz begeni geliyor, 3. ve 11. tuzak), yani 5,6M Ihsan'in beyani
olarak duruyor, bizim olcumumuz degil. Begeni/izlenme = 46.042/5,6M = **%0,82**,
bu 11. maddedeki %0,8-4,6 bandina oturuyor, %4-5,8 formulune DEGIL.

**Kritik: ayni kanal, ayni format, ayni ses, ayni baslik , ama 46.042 ile 124 arasinda
371 kat fark var.** Bu iki tepeli dagilim, bizim aimagine olcumumuzun birebir aynisi
(gecti/kaldi kapisi, kanal cezasi degil).

Ayiran degisken, kareler karsilastirildiginda: **tanınır gercek yer.**

| video | yer | acilis kadraji | sonuc |
|---|---|---|---|
| TOKYO 2247 | Tokyo , Tokyo Kulesi + Skytree kadrajda | tanri-gozu genis, yapinin TAMAMI tek karede | 46.042 |
| monsun | tanınır kiyi megakenti | genis kurulus | 2.597 |
| buz kubbe | isimsiz donmus ova | genis ama jenerik | 307 |
| col kubbe | isimsiz col | orta plan, tek kubbe | 328 |
| duvar carsi | isimsiz ic mekan | **zaten ICERIDE basliyor** | 124 |

Iki kural birlikte calisiyor gorunuyor:
1. **Tanınır yer** , izleyicinin bildigi bir sehir/ikon kadrajda olacak
2. **Acilista tanri-gozu genis plan** , imkansiz yapi TEK karede okunacak

**Dikkat:** bu n=5. Iki kural da korelasyon, kanit degil. Ama 1. kural bizim
aimagine olcumumuzle (ikonlar 4/4 tuttu, tekrarlanan jenerik 3/3 kaybetti)
BAGIMSIZ olarak ortusuyor , iki ayri kanalda ayni yone isaret ediyor.

## 5. Kurgu grameri

Kesme anlari: 5,04 / 1,73+5,77 / 2,08 / 1,88 / 2,50 sn.

Kazanan (10,1 sn) **2 x 5 sn esit blok**. Kesme SERT ve eslesen-hareket DEGIL:
ayni yerin cok farkli iki bakis acisi. Cekim 1 tepeden, yapinin tamamini gosteriyor;
cekim 2 alcaktan, insan olcegine yakin, ayni yeri "gercek" gibi satiyor.

Kalan 4 videoda ilk cekim 1,7-2,5 sn ile cok kisa , ve hepsi dusuk performansli.
**Hipotez:** kazanan formul 2 x 5 sn, kaybedenler ilk cekime yeterli zaman vermiyor.
n=5'te ayirt edilemez, test edilmeli.

## 6. Caption

Ingilizce + Japonca cift dil, kisa satirlar. "A fictional future world created with AI"
ibaresi aciklamada acikca geciyor. Hashtag'te yil marka olarak kullaniliyor (#EARTH2247).

## 7. Kopyalanacak sozlesme , olculen degerler

- Sure **8-10 sn**, 2 cekim, ilk cekim ~5 sn
- **Anlatim YOK.** Tek ses: ~2 kHz'de kesilmis derin drone, **-14 LUFS**, LRA < 2
- Baslik sol ustte, daktilo ile ~0,5 sn'de yazilir, kesmede soluar
- Acilis kadraji tanri-gozu genis, imkansiz yapi tek karede okunur
- **Tanınır gercek sehir/ikon zorunlu** , isimsiz kubbe/col/ova YASAK
- 1080x1920, 24 fps

## 8. Olculemeyenler

- IG oynatma sayilari (giris duvari). Yalniz begeni alinabildi.
- Retention egrileri , yok.
- Yazi tipinin kesin adi , teshis edilemedi.
- Kanalin toplam video sayisi ve takipci sayisi , bu kosuda cekilmedi.
- Hangi AI modeliyle uretildigi , bilinmiyor.

---

# EK , PART 2 KANCA ANALIZI ve v2.0 KARARI (15 Eylul 2026)

Istek (Ihsan, iki direktif ayni oturumda):
1. "daha hizli gecisler lazim tek videoda 3 sahne gecisi istiyorum"
2. "ortamlari daha futuristik yapmani istiyorum robotik gelecek gibi olsun,
   videolar hep bi yikimdan sonrasini gosteriyor gibi olmus, onun yerine
   teknolojinin nasil gelistigini anlatan bir video olsun"

Analiz edilen video: `instagram.com/reel/DdST1bqDJzG` = **part 2, NEW YORK 2512**
(YouTube `ZDRrC5r7Vek`, TikTok `7685536040630766862`).

## 1. Olculen degerler

Arac: `yt-dlp` + `ffmpeg` (reel-analiz skill'i, `scripts/olc.py`).

| Olcu | Deger | Hedef / yorum |
|---|---|---|
| Cozunurluk | 1080x1920 | tamam |
| fps | 24,0 | tamam, doktrin 24 |
| Sure | 8,04 sn | doktrin bandi 7-9, tamam |
| Kesme sayisi | **1** (t=4,04) | SORUN , direktifin konusu |
| Plan uzunluklari | 4,04 + 4,00 sn | SORUN |
| Kesme / 10 sn | **1,24** | SORUN |
| LUFS | -14,1 | tamam, referans -14,0..-14,1 |
| True peak | -1,5 dBFS | tamam, kirpma yok |
| LRA | 2,0 | doktrin hedefi < 2, sinirda |
| Desifre | 0 kelime | tamam, anlatimsiz |

Ses zarfi (ceyrek saniyelik RMS): -19,4 ile -11,4 dBFS arasi, **duz**. Tek
belirgin hareket t=3,75-4,00'da (-11,4 dB) , drone kesmeye dogru hafifce
yukseliyor. Bu iyi ve **korunmali**.

## 2. Kanca teshisi , kesme sayisi asil sorun DEGIL

2 fps'lik kontakt sayfasi (16 kare / 8 sn) cikarildi ve goz ile bakildi.
Bulgu, kesme sayisindan daha sert:

**Cekim 1'in sekiz karesi pratik olarak AYNI. Cekim 2'nin sekiz karesi de
pratik olarak AYNI.** Kamera "yavas, tek yonlu hareket" kuralina uyuyor ama
hareket ekranda okunmuyor. Video, iki fotografin 4'er saniye tutulmasi gibi
izleniyor.

Ilk saniyede degisen tek sey, daktilo kunyesinin harfleriydi:

- t=0,00 kadrajda "N"
- t=0,25 "NEW YO"
- t=0,50 "NEW YORK 2512" tamamlandi
- t=0,50 , 3,50 arasi **hicbir sey degismiyor**
- t=4,04 tek kesme

Yani izleyicinin karar penceresinde (0-1,5 sn) videonun sundugu tek devinim
yazi animasyonuydu.

**Iyi olan:** t=0,00 karesi vaadi ZATEN tasiyor , Empire State + Chrysler
silueti + yukseltilmis platformlar + su ayni karede. Kanca KOMPOZISYON olarak
dogru kurulmus. Sorun kompozisyonda degil, **ritimde**.

**Ikinci sorun , odul cok gec:** videonun duygusal karsiligi (platformun
altindaki tekne mahallesi, camasirlar, isikli pencereler, insanlar) t=4,04'te
basliyor. Kanalin en iyi karesi, izleyicilerin cogunun coktan kaydirdigi
yerde duruyor.

## 3. Ikinci direktifin olculebilir dayanagi

Ihsan "yikimdan sonrasi gibi" dedi. Kadrajda gorunen: gri beton platformlar,
yukselmis deniz, bugunku bina stoku. **Gorunur tek bir calisan teknoloji yok.**

Konfigurasyon tarafinda sebep net: v1.0'in alti ailesinin ALTISI da bir
tehdide verilen cevapti (`su yukseldi`, `cole donustu`, `ortu altinda`,
`asagi indi`, `yukari buyudu`, `yesile donustu`) ve 36 konunun 36'si
"sehir bir seye karsi siginmis" diye yazilmisti. Ekrandaki his tesaduf degil,
doktrinin dogrudan ciktisiydi.

## 4. Kiyas tabani (v2.0 bunun uzerine olculecek)

| Bolum | YouTube | TikTok | IG |
|---|---|---|---|
| P1 ISTANBUL (13 Eyl) | 643 izlenme / 4 begeni | , | giris duvari |
| P2 NEW YORK (14 Eyl) | 716 izlenme / 7 begeni | **5.400 izlenme / 15 begeni** | giris duvari |

Not: TikTok YouTube'un ~7,5 kati getiriyor. Bu **olculdu ama aciklanmadi**,
n=1. IG oynatma sayisi yine cekilemedi (og:description hiz siniri, tuzak 3).
Eski kanal medyani 27 izlenmeydi, yani v1.0 zaten ~24 kat yukarida.

## 5. Yapilan degisiklik , v2.0

### 5.1 Ritim

Motorun alt siniri 4 saniye oldugu icin "4 cekim x 2,5 sn" DOGRUDAN
uretilemez. Iki adimda cozuldu:

1. 4 cekim x **4 sn** uretilir (Omni enum'u 4/6/8/10).
2. `micro_trim: 0.75` her klibin iki ucundan keser -> cekim basina **2,5 sn**.

Gercek uretim fonksiyonu (`core.ffmpeg_tools.trim_head_tail`) ile dogrulandi:
4 x 4,00 sn -> 4 x 2,50 sn -> birlesik **10,00 sn**, kesmeler 2,5 / 5,0 / 7,5.

| | v1.0 | v2.0 |
|---|---|---|
| Cekim | 2 | **4** |
| Kesme | 1 | **3** |
| Kesme / 10 sn | 1,24 | **3,0** |
| Sure | 8,04 sn | **10,0 sn** |
| Odul (insanlar) | 4,04 sn'de | **2,5 sn'de** |

10,0 sn ayni zamanda olculen referans kazananinin (10,1 sn) uzerine oturuyor;
v1.0'in 8 sn'si o kazananin kisaltilmis haliydi.

`trim_head_tail` kalan sure 2,0 sn'nin altina duserse kirpmayi reddedip klibi
oldugu gibi kopyalar, yani 4 sn'lik klipte `micro_trim` **en fazla 1,0**
olabilir. 0,75 guvenli payla secildi.

Ayrica cekim 1 artik **kameradan bagimsiz hareket** tasimak zorunda (gecen
kapsul, akan drone, yuruyen isik). Donuk ilk saniye artik sablon tarafindan
engelleniyor.

### 5.2 Yon

Alti aile de teknoloji alani oldu: `havada ulasim`, `robotik insaat`,
`enerji mimarisi`, `yasayan malzeme`, `otomatik uretim`, `yorunge baglantisi`.
36 konunun 36'si yeniden yazildi. `art_style` ve `qc.notes` artik felaket
estetigini (moloz, catlak, branda, sel, kum firtinasi, duman, terk edilmislik)
**otomatik fail** sayiyor, ayrica "gorunur calisan teknoloji yoksa fail" kurali
eklendi.

Havuzdan **Phoenix ve Cusco cikarildi** (dunyaca taninan silueti yok, kanalin
olculen tek kazanma sarti ise taninirlik , 371 kat). Yerlerine Chicago ve
Machu Picchu geldi. Ikisi de kullanilmamisti.

`id -> sehir` eslesmesi korundu: `_unused_topics` yayinlanmis bolumleri plan
dosyalarindaki `seed_id` ile izliyor, eslesme bozulsa Istanbul ve New York
havuza geri donerdi.

### 5.3 Risk dagilimi

Dort cekim yuzeysel olarak "dort kat fail sansi" gibi gorunur. Gercekte
anatomi riski tasiyan cekim **yalniz birdir** (cekim 2). Cekim 1 havadan ve
insansiz, cekim 3 makine olcegi, cekim 4 nesne ayrintisi. v1.0'da iki cekimin
biri riskliydi, yani risk orani 1/2'den **1/4'e dustu**.

Ayrica `qc.max_regens_per_episode: 8` eklendi. Adil pay `total // shot_count`
oldugu icin alan yazilmadiginda 4 cekim yine cekim basina 1 regen alirdi ,
part 3'u 15 Eylul'de dusuren tam olarak buydu ("cekim adil payi doldu").
8 // 4 = 2, yani her cekim `max_regens_per_shot` kadar hak aliyor.
`EPISODE_CREDIT_CAP` 900'den 1200'e cikti (4 x 80 + muzik 80 + en kotu
8 x 80 = 1040).

## 6. Yol boyunca bulunan IKI GERCEK ARIZA

### 6.1 Kunye kapisi TERS calisiyordu (kod hatasi, bugune kadar gizliydi)

`_validate_batch` icinde iki ayri kunye dali vardi. `year_required: true` olan
dal alt yaziyi **kosulsuz** zorunlu tutuyordu ve `subtitle_required: false`
alanini hic okumuyordu. Sonuc:

- Kanalin **dogru** kunyesi `{"title": "PARIS 2512", "subtitle": ""}` ->
  **REDDEDILIYORDU**
- **Yanlis** kunye `{"title": "Eiffel Tower: Energy Spine",
  "subtitle": "Paris, France 2512"}` -> **KABUL EDILIYORDU** (yil kontrolu alt
  yazidan geciyordu)

Bugune kadar gorulmemesinin sebebi: kurulustaki bes plan (911855c) ELLE
yazilmisti. 15 Eylul, ikmalin still-home icin plan yazdigi **ilk gundu** ve
bes planin BESI de bozuk kunye uretti. Yani bu hata benim degisikligimden
bagimsiz olarak ilk otomatik ikmalde patlayacakti.

Duzeltme: iki dal birlestirildi, tek kapi `validate_title_card`. Ustune
opt-in **bicim kapisi** eklendi (`title_card.title_pattern` /
`subtitle_pattern`); still-home icin `[A-Z][A-Z0-9' .-]{1,28} 2512` ve alt
yazi bos. Kanit: yeniden uretimde Gemini'nin 1. denemesi dort bozuk kunyeyle
**reddedildi**, 2. denemesi temiz gecti.

### 6.2 Muzik prompt'u doktrinden kaciyordu

Yeni uretilen bes planin besinde de piyano, yayli, kreskendo, akor cozumu ve
"rising harmonic progression" belirdi , doktrin ise tek, sabit, vurussuz,
melodisiz derin drone istiyor. Yayinlanmis iki bolumun prompt'u ise harfi
harfine AYNIYDI.

Degismeyen bir alani modele yazdirmak sadece sapma riski uretir. Yeni
`bible.series.music_fixed` alani eklendi: doluysa ikmal modelden muzik
istemez, kanonik metni aynen kullanir. still-home'a part 1/2'nin olculmus
(-14,1 LUFS, LRA 2,0) metni pinlendi.

## 7. Yeniden uretilen kuyruk (dogrulandi)

| Part | Baslik | Kunye | Aile |
|---|---|---|---|
| 3 | Paris Powers Its Own Tower | PARIS 2512 | enerji mimarisi |
| 4 | Dubai Grows Its Own Skin | DUBAI 2512 | yasayan malzeme |
| 5 | Tokyo Feeds Itself From Below | TOKYO 2512 | otomatik uretim |
| 6 | London Connects Earth To Orbit | LONDON 2512 | yorunge baglantisi |
| 7 | Cairo Moves Its People By Air | CAIRO 2512 | havada ulasim |

Besi de: 4 cekim x 4 sn, kanonik drone, tek satirlik dogru kunye. Part 3'un
dort prompt'unda yazi-riski kelimesi ve olumsuz dil **yok**; icerik olarak
isildayan enerji omurgasi, akan isik hatlari, otonom temizlik dronlari ve
otomatik cam temizleyici var , istenen robotik/ileri teknoloji yonu.

Kucuk sapma: part 3 cekim 4 "slowly pans across the balcony" diyor, doktrin
pan'i yasakliyor. Tek yonlu yavas hareket olarak zararsiz kabul edildi,
yeniden uretim tetiklenmedi.

## 8. OLCULMEMIS , iddia edilmiyor

- **v2.0 olculmedi.** "Uc gecis tek gecisten iyi tutar" ve "ileri teknoloji
  yonu felaket yonunden iyi tutar" IKI AYRI hipotez ve ayni bolumde birlikte
  degistiler. Part 3 ve sonrasi bunlari **birbirinden ayiramaz**. Ayirmak
  isteniyorsa ayri bir test kurulmalidir.
- Kontakt sayfasindaki "hareket yok" bulgusu GOZLE tespit edildi; hareket
  miktari (ornegin kare-farki enerjisi) sayisal olarak olculmedi.
- TikTok'un YouTube'un 7,5 kati getirmesi n=1'dir, aciklanmadi.
- Kesme sayaci sentetik dogrulama klibinde 3 kesmeden 2'sini gordu (duz renk
  alanlarinda `scene=0.3` esigi yetersiz kaliyor, tuzak 9). Uc kesmenin de
  yerinde oldugu kare renkleri orneklenerek ayrica dogrulandi.
- v2.0 ile uretilmis GERCEK bir bolum henuz yok. Yukaridaki 10,0 sn ve 3 kesme
  sentetik klip uzerinde, gercek uretim fonksiyonuyla dogrulandi.

---

# EK , v2.0'in ilk gercek bolumu olculdu (18 Eylul 2026)

Istek (Ihsan): "shadowedhistory kanali gunlerdir video paylasmiyor sebebini
ogren ve ayrica videolar viral olmuyor izlenmiyor izleyenleri ilk 3 saniye
ekrana kitlememiz lazim sahne gecisi bu arada olsun".

Olculen dosya: YouTube `Y-GE8XB8JJY` = **part 3, PARIS 2512**, v2.0 ile
uretilen ILK otomatik bolum (16 Eylul 23:28 UTC). Arac: `yt-dlp` + `ffmpeg`.

## 1. Bicim , v2.0 SOZU TUTTU

| Olcu | v1.0 (P2) | **v2.0 (P3)** | Doktrin |
|---|---|---|---|
| Sure | 8,04 sn | **10,17 sn** | 9-11 tamam |
| Kesme sayisi | 1 | **3** | tamam |
| Kesme anlari | 4,04 | **2,54 / 5,04 / 7,54** | 2,5 aralikli, tamam |
| fps | 24 | **24** | tamam |
| LUFS | -14,1 | **-14,0** | tamam |
| True peak | -1,5 dBFS | **-1,0 dBFS** | tamam |

**Ihsan'in "3 sahne gecisi" direktifi CANLI ve dogrulandi.** Bu maddede
yapilacak bir sey yok, v3.0 buna DOKUNMADI.

## 2. Sonuc , format duzeldi, izlenme cokdu

| Bolum | Bicim | YouTube izlenme | Begeni |
|---|---|---|---|
| P1 ISTANBUL (13 Eyl) | v1.0, 2 cekim | 648 | 4 |
| P2 NEW YORK (14 Eyl) | v1.0, 2 cekim | 875 | 7 |
| **P3 PARIS (16 Eyl)** | **v2.0, 4 cekim** | **21** | 0 |

P3 42. saatinde olculdu. Kanalin kendi "44 saat dolmadan olu ilan etme"
kurali geregi bu sayi HENUZ nihai degildir, ama P1 ve P2'nin ayni yastaki
degerlerinin iki kat buyuklugunde altinda.

## 3. Kanca teshisi , ilk kare BUGUNU gosteriyor

Cekim 1'in ilk 2,5 saniyesi 6 kareye bolundu ve goz ile incelendi:

| t | kadrajda ne var |
|---|---|
| **0,00** | Eyfel Kulesi KOYU demir renginde, caddeler sonuk, gokyuzu soluk mavi. **Kare, bugunun Paris'inden cekilmis bir drone fotografindan ayirt edilemiyor.** |
| 0,25 | kulede ilk isik izi |
| 0,50 | caddelerde isik seritleri belirmeye basliyor |
| 0,75 | kule beyaz isiyor, seritler net |
| 1,25 | vaat nihayet tam |

Destekleyici olcum: kadrajin orta ucte birinin ortalama parlakligi
t=0,00'da 109,6 iken t=0,75'te 127,8'e cikiyor (+%16,6), sonra 2,38'de
106,6'ya dusuyor. Yani sahnenin en aydinlik ani ilk kare DEGIL.

Bolumun tek "2512" kaniti, izleyicinin karar penceresi kapandiktan SONRA
ekrana geliyor. Doktrin "gecikmeli ortaya cikis yasaktir" diyordu; motor tam
olarak gecikmeli ortaya cikis uretti.

**Kok sebep, ve bu bir prompt kazasi DEGIL:** bolumun teknolojisi bir ISIKTI.
Isigin kapali hali vardir ve video modeli kapali-acik gecisini animasyon
firsati sayar. "Eyfel enerji omurgasi oldu" diye yazilan bir konu, modele
once bugunun kulesini kurdurur sonra yaktirir. Konunun CINSI ilk kareyi
belirliyor.

## 4. Ikinci bulgu , kapinin kendisi tutmuyordu

`qc.require_first_frame` bu seride ACIKTI. Ama kapiya giden metin
`series/critic.py` icinde unnatural-lab kanali icin yazilmisti:

> "The episode's **impossible property** must already be active and readable
> in this exact frame, and the **object** must fill a large share of the frame."

Sehir olcegindeki bir hava cekiminde "obje" diye bir sey yoktur, "imkansiz
ozellik" sorusu da bosa duser. Sonuc `qc_log.jsonl`'de duruyor: **P3'un
bugunku Paris'i gosteren acilis karesi bu kapidan IKI KEZ
`first_frame_ok=true` alarak gecti.**

Kapi acikti, calisiyor gorunuyordu, ve hicbir seyi tutmuyordu.

## 5. Ucuncu bulgu , cekim 2 olu bolge

Kare-farki ile hareket olculdu (Y kanali, ardisik kare mutlak farki):

| Cekim | Aralik | Hareket |
|---|---|---|
| 1 havadan | 0,0-2,5 sn | 9 |
| **2 yer seviyesi** | **2,5-5,0 sn** | **5** |
| 3 makine olcegi | 5,0-7,5 sn | 15 |
| 4 sicak ayrinti | 7,5-10,0 sn | 10 |

Cekim 2 videonun en donuk yeridir: mermer bir meydanda elinde tablet tutan,
DURAN insanlar. Sablon "sabit yukseklikte tek yonlu yavas hareket" istiyordu,
model bunu "hicbir sey olmuyor" diye okudu.

## 6. Yayin durusu , kanca ile ILGISIZ, iki ayri sebep

| Gun | Sonuc | Sebep |
|---|---|---|
| 14 Eyl | yayin | , |
| **15 Eyl** | **yayin YOK** | QC: cekim 2 iki denemede de kaldi (gomulu yazi, sonra bozuk anatomi), `min_shots=4` karsilanamadi |
| 16 Eyl | yayin (P3) | , |
| **17 Eyl** | **yayin YOK** | Kredi baslangic kapisi: `bakiye=1632 < esik=1800` |
| **18 Eyl** | **yayin YOK (beklenen)** | ayni kapi: bakiye 1017 |

Kredi kapisinin kok sebebi asimetriydi. Kapi bakiyeden `1,5 x EPISODE_CREDIT_CAP`
ister. still-home'un cap'i 1200'du, yani **esik 1800 ile filonun EN YUKSEGI**
(digerleri 900 -> 1350). Ama bu seri filonun en UCUZ islerinden birini yapiyor:

| Bolum | Rezerve | **Gercek harcama** |
|---|---|---|
| P2 | 900 | **206** |
| P3 | 1200 | **189** |

189 kredilik bir is icin kasada 1800 bekleniyordu. Ustelik hat gecenin EN
SONUNDA kosuyor (17 Eyl: galactic 19:46, wild-encounter 21:35, still-home
22:58), yani onundeki hatlar harcadiktan sonra artakalani buluyor. Cift ceza.

**Havuz seviyesinde ayri bir bulgu:** `fear-slide` (aimagine) ayni Kie
anahtarini kullanir, seedance ile 15 sn'lik cekim uretir (olculen 372 kredi)
ve **hicbir kredi kapisi ya da bolum tavani yoktur**. Kapili hatlar, kapisiz
hattin arkasindan geliyor. Bu karar Ihsan'a aittir, bu turda degistirilmedi.

## 7. Yapilan degisiklik , v3.0

1. **SILUET KURALI.** Teknoloji artik sehrin siluetini degistiren FIZIKSEL
   bir yapidir ve ilk karede tamamlanmis, tam calisir halde durur. Siluet
   geometridir, geometrinin kapali hali yoktur. Isik yapinin uzerine binen
   sustur, "2512" diyen TEK sey olamaz. Sinav: ilk kareyi simsiyah siluete
   indirgersen yeni yapi hala okunuyor mu?
2. **Isik surucu iki aile GECE gecer** (`enerji mimarisi`, `yasayan malzeme`).
   Ogle vaktinde soluk gokyuzu altinda isima gorunmez, P3 bunun kanitidir.
3. **36 konunun 18'i yeniden yazildi**: isik surucu 12 konu + siluet gucu
   zayif 6 `otomatik uretim` konusu ("halls" alcaktir, "towers" siluet yapar).
4. **Cekim 1'de hareket = YER DEGISTIRME.** "Bir yapinin boyunca yuruyen isik"
   ornegi sablondan cikarildi: modeli tam da yasakladigimiz rampaya itiyordu.
5. **Cekim 2'ye gecis (traversal) zorunlulugu** geldi; duran kalabalik
   basarisiz cekimdir.
6. **Ilk-kare QC kapisi seri-farkindali yapildi.** `series/critic.py` artik
   `bible.series.qc.first_frame_rule` yazan serinin kendi kuralini varsayilanin
   YERINE koyar. still-home'un kurali siluet testini ve karanlik-teknoloji
   yasagini dogrudan sorar.
7. **Kredi cap'i 1200 -> 900**, esik 1800 -> 1350, filonun geri kalaniyla ayni.
8. **`tools/siluet_denetim.py`** eklendi: kuyruktaki planlari ucretli cagri
   YAPMADAN denetler (durum-gecisi dili, zayiflik dili, isik ailelerinde gece,
   doktrin damgasi). Arsivlenen eski part 4 (DUBAI, "glows softly") bu araca
   verildiginde 4 bulgu uretti, yani arac gercek kazayi yakaliyor.

## 8. OLCULMEMIS , iddia edilmiyor

- **P3'un 21 izlenmesi NIHAI DEGIL** (42. saat). Kanalin kendi kurali 44
  saattir. Sayi yukselebilir.
- **v2.0'in iki hipotezi hala ayrisamiyor** (uc gecis vs ileri teknoloji
  yonu). v3.0 ustune UCUNCU bir degisken ekliyor (siluet + gece). P4 ve
  sonrasi bu ucunu de birbirinden ayiramaz. Ayirmak isteniyorsa ayri test.
- Siluet kuralinin izlenmeyi yukseltecegi **kanitlanmadi**. Dayanagi iki
  bagimsiz korelasyon: referansta taninir/imkansiz yapi 46.042 vs 124, ve
  bizim aimagine olcumumuz (landmark 4/4, jenerik tekrar 3/3 kayip).
- Parlaklik olcumu kamera hareketinden de etkilenir; ilk karedeki gecikmenin
  BIRINCIL kaniti kontakt sayfasidir, parlaklik yalniz destekleyicidir.
- Cekim 2'nin olu olmasinin izlenmeye etkisi olculmedi, yalniz kare-farki
  olculdu.

