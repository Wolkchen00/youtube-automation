# galactic_experience , video analiz raporu

Tarih: 10 Eylul 2026 (Los Angeles)
Yontem: yt-dlp ile indirildi, ffmpeg/ffprobe + EBU R128 ile olculdu, kareler goz ile incelendi.
Metodoloji ve esikler: `Projeler/Reelyze_Arastirma/REELYZE-DOSYASI.md`

---

## 1. Kanal durumu

| | |
|---|---|
| Abone | 140 (filoda en cok abone) |
| Toplam video | 199 |
| Toplam izlenme | 64.098 |
| **30 gunluk medyan izlenme** | **88,5** |

Karsilastirma: `sentinal_ihsan` 1.292 , `galactic_experiment` 88,5 , `shadowedhistory` 27 , `aimagine` 4.
Filoda ikinci sirada. En cok abonesi olan kanal ama izlenme abone sayisiyla orantili degil.

### Son yayinlar
| Video | Tarih | Izlenme |
|---|---|---|
| What If Earth Had Rings? Sky BLADES | 9 Eyl | 296 |
| Flying to Alpha Centauri: A 5 MILLION Year Trip | 8 Eyl | 336 |
| Olympus Mons: Towers Over Everest | 7 Eyl | 131 |
| KELT-9b: Hotter Than MOST Stars | 6 Eyl | 222 |
| The Universe's SLOWEST Particle | 5 Eyl | 393 |
| Neptune: Its Year is LONGER Than a LIFETIME | 30 Agu | 60 |

Bant dar: 60-393. Ne patlayan var ne tamamen olen. **Kanal duz gidiyor.**

---

## 2. Olculen teknik durum , EN BUYUK SORUN SES SEVIYESI

| Video | Izlenme | Cozunurluk | fps | Sure | Kesme | En uzun plan | LUFS | True peak | LRA | WPM |
|---|---|---|---|---|---|---|---|---|---|---|
| Earth Rings | 296 | 1080x1920 | 30 | 19,6 sn | 2 | 8,47 sn | **-21,9** | -8,6 | 1,6 | 156 |
| Alpha Centauri | 336 | 1080x1920 | 30 | 16,6 sn | 2 | 5,6 sn | **-22,1** | -6,2 | 3,0 | 126 |
| Neptune (zayif) | 60 | 1080x1920 | 30 | 10,9 sn | **0** | 10,94 sn | **-24,7** | -10,7 | 2,0 | 154 |

Hedef: **-16 ila -13 LUFS**. Olculen: **-21,9 ile -24,7**.

### Bulgu A: Videolar 6 ile 11 dB FAZLA SESSIZ
Bu kanalin sesi hedefin cok altinda. Karsilastirma icin ayni filodaki `sentinal_ihsan`
**-14,3 ile -14,8** olcuyor ve 30 gunluk medyani 1.292.

6-11 dB kucuk bir fark degil. Telefon hoparlorunde, gurultulu ortamda, ya da kullanici
sesi kisik tutuyorsa bu video **duyulmuyor**. Anlatim tabanli bir kanalda
(126-156 WPM, yani yogun konusma) ses duyulmuyorsa icerik yok demektir.

Ortak motorda hazir cozum VAR: `core/ffmpeg_tools.py:234-372` (`master_audio`,
iki gecisli loudnorm, hedef I=-14, TP=-1,0). Ciktida uygulanmamis ya da
sonraki asamada bozulmus. **Bu kanalin bir numarali isi budur.**

### Bulgu B: En dusuk performansli videoda SIFIR kesme
Neptune (60 izlenme): 10,9 saniye, **0 kesme**, tek plan 10,94 saniye.
Digerlerinde 2 kesme var ve 4-6 kat daha fazla izlenme almislar.
Kisa video kurallarina gore tavan 4 saniye, pattern interrupt her 5-7 saniyede.

### Bulgu C: Konusma hizi yuksek
126-156 WPM. Reelyze yogun bilgi icin 254 WPM'i "olcumlenebilir sekilde hizli" sayiyor,
yani bu aralik teknik olarak sorunlu degil. Ama astrofizik terimleri yogun bir icerikte
156 WPM + dusuk ses birlesince anlasilirlik dusuyor. Once sesi duzelt, sonra hizi olc.

### Bulgu D: Ekran yazisi yok
Bu seride ekran yazisi/altyazi basilmiyor. Ortak motorda `title_card_overlay` ve
`fact_captions_overlay` hazir (`core/ffmpeg_tools.py:1362` ve `:1445`), bu seri cagirmiyor.
`shadowedhistory` cagiriyor ve kanalin en iyi videosu tam da baslik kartli olan.
Sessiz izleyici bu kanalda hicbir sey goeremiyor.

---

## 3. Ne yapilmali (etki sirasina gore)

1. **SES SEVIYESI. Tek basina en onemli is.** -22 LUFS'tan -14 LUFS'a cikar.
   `core/ffmpeg_tools.master_audio` zaten var, cagrilmasi yeterli.
   Hedef: I=-14, TP=-1,0, LRA=11.
2. **Ekran yazisi ekle.** En azindan baslik karti (ilk 1,5 saniye, ust-orta ucte bir,
   3-7 kelime). `shadowedhistory` bunu yapiyor, ornek al.
3. **Sifir kesmeli video birakma.** Tek plan tavani 4 saniye, pattern interrupt 5-7 saniyede.
4. **Kanca testi.** Basliklar bilgi veriyor ama merak yaratmiyor:
   *"Neptune: Its Year is LONGER Than a LIFETIME"* iyi (60 izlenme aldi ama kalip dogru),
   *"Olympus Mons: Towers Over Everest"* daha zayif. `sentinal_ihsan`'in
   "This X Is NOT Supposed To Y" kalibi bu kanala uyarlanabilir:
   konu degil, **anomali** vaat et.

## 4. Neye DOKUNMA

- Cozunurluk 1080x1920 ve fps 30 dogru, dokunma.
- Ortak motor (`core/`, `series/`) , dort kanali birden besliyor.
  Ses duzeltmesi buraya girecekse `sentinal_ihsan`'i bozmamali (o zaten dogru).
- `event-horizon/bible.json` ve `series.json` , kanal kimligi.
- `planetfall` duraklatilmis ve replenish kapali, oyle kalsin.

## 5. Acik sorular (olculemedi)

- Retention egrileri (YouTube Studio gerekiyor)
- Ses neden -22 cikiyor: loudnorm hic cagrilmiyor mu, yoksa cagriliyor ama sonraki
  bir mikslemede mi bozuluyor? Kod okumasi bunu netlestirmedi, calisma zamaninda olculmeli.
- 140 abone ile 88 medyan izlenme: aboneler videolari goermuyor mu, yoksa goeruyor da
  tiklamiyor mu? (Impressions/CTR verisi gerekiyor.)


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
