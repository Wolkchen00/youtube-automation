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
