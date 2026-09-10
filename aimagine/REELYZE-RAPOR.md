# aimagine , video analiz raporu

Tarih: 10 Eylul 2026 (Los Angeles)
Yontem: yt-dlp ile indirildi, ffmpeg/ffprobe + EBU R128 ile olculdu, kareler goz ile incelendi.
Metodoloji ve esikler: `Projeler/Reelyze_Arastirma/REELYZE-DOSYASI.md`

---

## 1. Kanal durumu

| | |
|---|---|
| Abone | 98 |
| Toplam video | 250 |
| Toplam izlenme | 141.335 |
| **30 gunluk medyan izlenme** | **4** |

**Filonun en kotu performans goesteren kanali.** Omur boyu video basi ortalama ~565
izlenme, ama son 30 gunun medyani 4. Yani kanal eskiden calisiyordu, artik calismiyor.

### Kritik yapisal sorun: tek kanalda iki ayri format

Bu YouTube kanalina IKI ayri uretim hatti basiyor:
- **Next Stop** serisi (`aimagine/next-stop/`, ortak motor) , 56 saniyelik videolar, 3-17 izlenme
- **AImagine-Fear** (`AImagine-Fear/`, bagimsiz hat) , 15 saniyelik POV kaydiragi, 13-1.995 izlenme

Ayni kanalda 56 saniyelik anlatimli tren yolculugu ile 15 saniyelik sessiz korku kaydiragi
yan yana duruyor. Algoritma bu kanaldan ne bekleyecegini bilemiyor.
**AImagine-Fear ayni icerigi Instagram'da 371.000 begeniye tasidi** (bkz.
`AImagine-Fear/REELYZE-RAPOR.md`), cunku orada hesap SADECE o icerigi yayinliyor.

Bu raporun geri kalani **Next Stop** hattini inceliyor.

---

## 2. Olculen teknik durum , Next Stop

| Video | Izlenme | Cozunurluk | fps | Sure | Kesme | En uzun plan | LUFS | True peak |
|---|---|---|---|---|---|---|---|---|
| The Deep | 17 | 1080x1920 | 30 | **56,2 sn** | 3 (0,5/10sn) | **36,54 sn** | -17,1 | **+0,2** |
| Bifrost | 9 | 1080x1920 | 30 | **56,2 sn** | 11 (2,0/10sn) | 15,34 sn | -16,1 | **+0,7** |

Hedefler: LUFS -16 ila -13, true peak <= -1 dBTP, tek plan <= 4 sn.

### Bulgu A: SES KIRPIYOR , en acil teknik hata
True peak **+0,2 ve +0,7 dBFS**. Bu 0'in USTUNDE, yani dijital kirpma var.
Guvenli tavan -1 dBTP. Platform yeniden kodlamasi bunu duyulur bozulmaya cevirir,
ozellikle telefon hoparlorunde. Filodaki tek kirpan kanal bu.

Not: ortak motorda hazir cozum var (`core/ffmpeg_tools.py:234-372`, hedef I=-14, TP=-1,0),
ama bu ciktida uygulanmamis ya da sonraki bir asamada bozulmus.

### Bulgu B: 36,5 saniyelik tek plan
"The Deep" videosunda 56,2 saniyenin 36,54'u **tek kesintisiz plan**. Kisa video
kurallarina gore tavan 4 saniye. Bu videonun 3 kesmesi var, yani 10 saniyede 0,5 kesme.
Bifrost'ta 11 kesme var (2,0/10sn) ve iki katı izlenme almis, ama ikisi de cok dusuk.

### Bulgu C: 56 saniye, formata gore cok uzun
Kendi olctugumuz 1.204 aykiri video verisinde, nis medyanina gore normalize edilmis
performans sure ile ters orantili:

| Kova | Nis medyanina gore kat |
|---|---|
| 0-7 sn | 1,69 |
| 7-15 sn | 1,34 |
| 21-30 sn | 1,02 |
| 45-60 sn | 0,89 |

56 saniyelik video en kotu kovada. Ayni kanaldaki 15 saniyelik POV kaydiragi
100-150 kat daha fazla izleniyor.

### Bulgu D: Konusma yok, altyazi yok
Iki videonun da otomatik altyazisi bos dondu (0 kelime). Yani ya konusma yok
ya da YouTube konusmayi tanimiyor. 56 saniye boyunca sessiz izleyiciye hicbir metin yok.

---

## 3. Ne yapilmali (etki sirasina gore)

1. **Iki formati ayir.** Next Stop ile AImagine-Fear ayni kanalda olmamali.
   Ya Next Stop'u durdur, ya ayri bir kanala tasi. Bu tek karar kanalin kaderini belirler.
2. **Ses kirpmasini durdur.** True peak <= -1 dBTP zorunlu. Yayin oncesi kapiya
   true peak kontrolu ekle (`RF-PLAN-REELYZE.md` Rock 5).
3. **Sureyi 56 saniyeden asagi cek.** Hedef 15-25 saniye. Ayni hikayeyi kisalt.
4. **Tek plan tavani koy.** 36,5 saniyelik plan kabul edilemez, 4 saniye tavani uygula.
5. **Ekran yazisi ekle.** Sessiz izleyicinin 56 saniye boyunca tutunacagi hicbir sey yok.
   Ortak motorda `core/ffmpeg_tools.py:1362 title_card_overlay` hazir duruyor,
   bu seri cagirmiyor. `shadowedhistory` cagiriyor ve kanalin en iyi videosu o.

## 4. Neye DOKUNMA

- Ortak motor (`core/`, `series/`) dort kanali birden besliyor. Buradaki her degisiklik
  `sentinal_ihsan`, `galactic_experience` ve `shadowedhistory`'yi de etkiler.
- `next-stop/bible.json` ve `series.json` , kanal kimligini bunlar tutuyor.
  Depoda `.v2bak` ve `.v3bak` yedekleri var, bunlar izlenmiyor (untracked), silme.

## 5. Acik sorular (olculemedi)

- Retention egrileri (YouTube Studio gerekiyor). 56 saniyede izleyici tam olarak nerede birakiyor?
- Ses kirpmasi ne zaman basladi? Eski videolarda da var mi, yoksa yeni bir regresyon mu?
- Next Stop icin IG/TikTok sayilari (bu hat oralara basiyor mu, olculmedi)


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
