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

---

# EK 2 , YENİ KONSEPT ARAŞTIRMASI (12 Eylül 2026)

Bağlam: İhsan konsepti rafa kaldırdı, önce rakip araştırması istedi.
Kanal adı ve kimliği aynı kalıyor, eski 199 video duruyor.

Yöntem: YouTube Data API v3 ile 10 sorgu (45 gün, `videoDuration=short`,
`order=viewCount`) tarandı, 323 shorts bulundu. Aday kanalların **son 50
videosunun tamamı** ayrıca çekildi, yani aşağıdaki medyanlar sadece hitleri
değil o kanalın tam çıktısını ölçüyor.

## 1. Niş ölü değil, biz ölüyüz

Aynı nişteki kanalların son 50 videosunun medyanı:

| Kanal | Abone | Medyan izlenme | Medyan süre | İzlenme/abone |
|---|---:|---:|---:|---:|
| Astro Creo | 203.000 | 961.894 | 16 sn | 4,74 |
| Science Of Infinity | 1.470.000 | 570.054 | 28 sn | 0,39 |
| Cosmic Void | 95.200 | 450.884 | 59 sn | 4,74 |
| Jupiter TV | 143.000 | 219.890 | 36 sn | 1,54 |
| Dark Cosmic Explained | 53.200 | 83.586 | 30 sn | 1,57 |
| Astro Boom | 44.900 | 49.684 | 28 sn | 1,11 |
| **AstroX** | **15.400** | **42.320** | 24 sn | **2,75** |
| **BİZ (galactic_experiment)** | **141** | **127** | 17 sn | **0,90** |

AstroX bizim büyüklüğümüze en yakın kanal ve **333 kat** fazla izleniyor.
Üstelik Endonezce yayın yapıyor, yani dil avantajı bile bizde.

**Sonuç: konu seçimi sorun değil. Uzay nişi küçük kanala da izlenme veriyor.**

## 2. İhsan'ın bulduğu format , ölçüldü

`instagram.com/reel/DbXH3hTMQj9/` , @space_art.ai, "Infinite Neighborhood🌍"

| Ölçülen | Değer | Bizim son videolarımız |
|---|---|---|
| Süre | **7,15 sn** | 17 sn |
| Kesme sayısı | **0 (tek plan)** | 2 |
| Konuşma | **0 kelime, anlatım YOK** | 126-156 WPM yoğun anlatım |
| LUFS | **-14,1** | -21,9 / -24,7 |
| True peak | **-1,3 dBFS** | -6,2 / -10,7 |
| LRA | 0,9 (sabit, tek müzik yatağı) | 1,6-3,0 |
| Çözünürlük | 1088x1936, 20,27 fps | 1080x1920, 30 fps |
| Beğeni | 836.079 | , |
| Yorum | 4.463 | , |
| Yayın | 29 Temmuz 2026 | , |

Görsel: banliyö evleri ve bir yol, Dünya'nın üzerinde uzaya doğru giden dev bir
halkanın üstüne kurulmuş. Tek kare, neredeyse hareketsiz, çok yavaş bir sürüklenme.
Ekranda yazı yok, jenerik yok, kapanış kartı yok. Kavramın adı **caption'da**.

İzlenme ölçülemedi (IG giriş duvarı). Beğeni/izlenme oranı %4-5,8 formülüyle
836K beğeni ≈ 14-21M izlenme eder, İhsan'ın gördüğü ~15M ile tutarlı. **Tahmindir.**

⚠️ **n=1.** Hesabın diğer gönderileri IG giriş duvarı yüzünden listelenemedi,
yt-dlp ve WebFetch ikisi de bloklandı. Bu tek videonun ölçümüdür, hesabın
ortalaması DEĞİLDİR.

## 3. Aynı tür YouTube Shorts'ta da tutuyor

"İmkânsız mekân" türünü YouTube'da ayrıca ölçtüm (son 50 video, tamamı):

| Kanal | Abone | Kuruluş | Medyan izlenme | Medyan süre |
|---|---:|---|---:|---:|
| LimitNook | 16.100 | Haz 2024 | 155.756 | 49 sn |
| **Dark Narr** | **30.700** | **Kas 2025** | **57.050** | 44 sn |
| **VoidNubis** | **6.700** | Eki 2024 | **54.434** | **11 sn** |

Dark Narr **10 aylık** bir kanal ve 57 bin medyan yapıyor.
VoidNubis 6.700 abone ile 11 saniyelik videolarda 54 bin medyan yapıyor.

⚠️ **Seçim yanlılığı:** bu kanalları izlenmeye göre sıralanmış aramayla buldum,
yani kazananları görüyorum. Aynı türde batmış kanalları göremiyorum. Kanal
medyanları dürüst (50 videonun hepsi sayıldı) ama kanal KÜMESİ yanlı.

## 4. "Created with @openart_ai" , araştırıldı

OpenArt (openart.ai) bir model toplayıcı arayüz. Kendi modeli yok, altında
Seedance gibi motorları çalıştırıyor. Fiyat: 7-120 $/ay kredi paketleri,
video başına yaklaşık 0,45-0,70 $.

**Bizim bu araca ihtiyacımız yok. Aynı motor zaten depoda:**

```
core/kie_api.py:475   generate_seedance_video(..., model="bytedance/seedance-2-fast")
core/kie_api.py:508   first_frame_url  ->  görselden videoya (image-to-video)
```

Yani space_art.ai'nin reçetesinin tamamı elimizde:
görsel üret (`generate_image`) -> Seedance ile tek plana çevir -> Suno müziği
(`core/music_generator.py`) -> `core/ffmpeg_tools.master_audio` ile -14 LUFS.
OpenArt aboneliği bize yeni bir yetenek getirmez, sadece aynı işi arayüzle yapar.

**Araç fark değil. Fark KONSEPT ve PROMPT.**

## 5. Neden bizim video tutmadı , üç ölçülmüş sebep

1. **Ses 6-11 dB fazla sessiz.** Kazanan videonun -14,1 LUFS'una karşı bizde
   -21,9 ile -24,7. `master_lufs` alanı bible'a ancak 11 Eylül'de eklendi,
   yayınlanan 33 bölümün neredeyse hepsi sessiz çıktı.
2. **Kanca görsel değil, sözel.** Bizim ilk karemiz bir uzay fotoğrafı, vaadi
   anlatım taşıyor. Kazananlarda ilk kare TEK BAŞINA imkânsız bir şey gösteriyor
   ve ses kapalı da olsa izleten o.
3. **Başlıklar ansiklopedi maddesi.** "Olympus Mons: Towers Over Everest" bilgi
   veriyor ama merak yaratmıyor. Kazananlarda başlık ya birinci şahıs iddia
   ("I Captured Something Crossing The Moon") ya da kavram adı ("Infinite
   Neighborhood"). Bizim yorum oranımız **1000 izlenmede 0,00**, nişte 0,11-0,72.
   Kimse konuşmuyor, yani kimse takılmıyor.

## 6. Üç aday konsept

Hepsi "Galactic Experiment" adının altına oturur, kanal kimliği değişmez.

### A , İMKÂNSIZ UZAY MEKÂNLARI  (önerilen)
Her bölüm tek bir imkânsız yapı/mekân: uzaya uzanan banliyö, halka üstünde
otoyol, Satürn'ün halkasında tren istasyonu. Fotogerçekçi, tek plan, 8-10 sn,
anlatım yok, tek müzik. Başlık = mekânın adı.
- Kanıt: space_art.ai (ölçülen tek video 836K beğeni), VoidNubis 6,7K aboneyle
  54K medyan, Dark Narr 10 ayda 30,7K abone.
- Üretim: **şu ankinden UCUZ.** 3 çekim yerine 1, TTS yok, anlatım riski yok.
- Risk: tür hızlı doyuyor, görsel fikir kalitesi her şey. Fikir havuzu şart.

### B , ÖLÇEK KARŞILAŞTIRMASI
"Jupiter vs Black Hole vs Sun" kalıbı. 30 sn, ekran yazılı, artan gerilim.
- Kanıt: Dark Cosmic Explained 53,2K aboneyle 83,5K medyan.
- Üretim: mevcut motorla doğrudan yapılır, ekran yazısı katmanı zaten var.
- Risk: türde çok kalabalık, ayırt edicilik düşük.

### C , "BUNU YAKALADIM" TELESKOP POV'U
Astro Creo'nun kalıbı, 203K aboneyle 962K medyan. **Önermiyorum:** format
"bunu kendi teleskobumla çektim" iddiası üzerine kurulu. Bizim üretimimiz AI,
bu iddia yalan olur. Kanalı da riske atar.

## 7. Konsept ne olursa olsun değişmeyecek dört teknik kural

Bunlar ölçümle sabit, tartışma konusu değil:

1. `master_lufs: -14`, true peak -1,0 dBTP. Bible'da var, çıktıda DOĞRULANACAK.
2. İlk kare tek başına durmalı. Ses kapalıyken de izletmeli.
3. Kapanış kartı, jenerik, imza yok. Son kare başa rimlenir (loop).
4. Yorum oranı ana sinyal. Beğeni değil yorum ölçülecek (nişte 0,11-0,72 / 1000).

## 8. Ölçülemeyenler

- space_art.ai'nin gerçek izlenmesi ve hesap ortalaması (IG giriş duvarı).
- Retention eğrileri (YouTube Studio gerekiyor).
- Bizim 141 abonemiz videoları görüyor mu (impressions/CTR verisi yok).
- Rakip kanalların gerçek üretim maliyeti.

---

# EK 3 , @earthimpacts25 ANATOMİSİ (12 Eylül 2026)

İhsan'ın itirazı haklıydı: EK 2'deki YouTube kanalları gerçek çekim ve editle
çalışıyor, biz AI video üretiyoruz. Doğru karşılaştırma saf AI üreten hesaplar.
Bu bölüm `@earthimpacts25`'in anatomisidir. Format: gerçek felaketlerin
Dünya üstünden simülasyonu.

Yöntem: 5 reel yt-dlp ile indirildi, ffmpeg/EBU R128 ile ölçüldü, kareler
gözle incelendi. Hesabın 84 reel'i ayrıca izgara kaydırmasıyla çıkarıldı
(`ig_kaz.py dom`).

## 1. Ölçülen beş video

| Reel | Beğeni | Süre | Kesme | En uzun plan | LUFS | True peak | LRA | Çözünürlük |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `DPJSFp_Cqyj` düz dünya gün batımı | **500.229** | **8,01 sn** | **0** | 8,01 | -14,1 | -0,9 | 5,4 | 720x1280 |
| `DQfOoo4ChGR` | **401.000** | **8,01 sn** | **0** | 8,01 | -14,0 | -1,0 | 0,9 | 720x1280 |
| `DSAoo7MCnen` dev dalga | 42.195 | **8,01 sn** | **0** | 8,01 | -15,4 | -0,7 | 8,6 | 720x1280 |
| `Dcvgb0qqp1e` | 8.618 | 24,0 sn | 3 | 8,00 | -14,1 | -1,0 | 6,1 | 1080x1920 |
| `DcHQcd9RPnk` girdap | **306** | 48,02 sn | 5 | 8,02 | -14,1 | -1,0 | 5,9 | 1080x1920 |

### Bulgu A , süre ve kesme arttıkça performans DÜŞÜYOR, istisnasız

8 sn tek plan: 500K, 401K, 42K. 24 sn üç kesme: 8,6K. 48 sn beş kesme: 306.
Sıralama kusursuz monoton. **n=5, kanıt değil ama çok temiz bir örüntü**,
ve kanal düzeyi veriyle de uyuşuyor (VoidNubis 11 sn, space_art.ai 7,15 sn).

### Bulgu B , "en uzun plan" hepsinde 8,00-8,02 saniye

Bu tesadüf değil. **8 saniye AI video motorlarının tek üretim birimi.**
48 saniyelik video = 6 x 8 sn zincir. 24 saniyelik = 3 x 8 sn.
Yani hesap tek bir motor kullanıyor ve uzun videoyu klip ekleyerek yapıyor.
Daha çok klip = daha kötü sonuç.

### Bulgu C , beş videonun HEPSİNDE ortak olan üç şey

1. **Anlatım YOK.** Beşinde de 0 kelime. Konuşan yok, alt yazı yok.
2. **Ses seviyesi -14,0 ile -15,4 LUFS**, true peak -0,7 ile -1,0.
   Yani hepsi doğru seviyede. Bizim videolarımız -21,9 / -24,7.
3. **24 fps.** Bizimki 30.

### Bulgu D , LRA ayırt ETMİYOR, seviye ediyor

İhsan "ortam sesi olan videolar daha çok izleniyor" dedi. Ölçüm bunu
kısmen doğruluyor ama inceltiyor:

- Dinamik aralık (LRA) hitlerde **0,9 ile 8,6 arasında savruluyor**.
  401 bin beğenili video LRA 0,9 (düpedüz düz), 42 bin beğenili video LRA 8,6.
  **Yani "dinamik ses tasarımı" tek başına ayırt edici değil.**
- Ayırt eden şey **sesin VAR ve DOĞRU SEVİYEDE olması**. Beş videonun beşi de
  -14 LUFS bandında. Bizim hiçbirimiz değil.

Dev dalga videosunda (`DSAoo7MCnen`) ses tasarımı saniye saniye şöyle:

```
  0-1 sn   -16,0 dB   sakin
  3-4 sn   -21,7 dB   SESSIZLESIYOR
  4-5 sn   -24,8 dB   EN SESSIZ AN  <- dalga yaklasiyor
  6-7 sn    -9,6 dB   CARPMA
  7-8 sn    -8,5 dB   yikim
```

16 dB'lik bir iniş-çıkış. Sessizlik çarpmayı büyütüyor. Bizim videolarımızda
LRA 1,6-3,0, yani böyle bir an hiç yok. **Bu tekniği almalıyız ama "hit
garantisi" diye değil, kalite olarak.**

## 2. Hesabın gerçek gidişatı , parlak kısmı yanıltıcı

84 reel'in tamamı ölçüldü (izgara rozeti = **beğeni**, izlenme değil):

| | Değer |
|---|---:|
| Medyan beğeni | **804** |
| En düşük | 147 |
| En yüksek | 500.000 |

İzgaranın ilk üç sırası **sabitlenmiş gönderi** (500K / 401K / 64K).
Sabitlenmişler çıkarılınca son 9 gönderinin medyanı **923 beğeni**.

**Yani bu hesap istikrarlı bir güç değil.** İki büyük vuruşu var, gerisi
150-3.000 bandında. Dağılım iki tepeli: ya geçiyor ya kalıyor. Bu, aimagine
kanalında daha önce ölçtüğümüz "geçti/kaldı kapısı" örüntüsünün aynısı.

Yine de: medyan 923 beğeni, beğeni/izlenme %2-5 kabul edilirse **18.000-46.000
izlenme** eder. Bizim medyanımız 127 izlenme. Dip noktaları bile bizim
tavanımızın çok üstünde.

⚠️ İzlenme ÖLÇÜLEMEDİ. IG medya API'si 429 verdi (dört geri çekilme denemesi
de reddedildi), izgara yalnız beğeni gösteriyor. Yukarıdaki izlenme aralığı
**ÇEVİRİDİR, ölçüm değildir.**

## 3. Görsel anatomi

`DSAoo7MCnen` (dev dalga):
- **İlk kare tehdidi tamamen gösteriyor.** Kuş bakışı sahil kenti, sağda
  şehir boyunca uzanan devasa dalga duvarı. Merak yok, VAAT var.
- Kamera kilitli, hareket yok. Olay kadraja giriyor, kamera peşinden gitmiyor.
- 7,8. saniyede dalga şehri yutmuş. Ödeme yapıldı.
- Ekranda yazı yok. Hikâye caption'da, uzun ve duygusal bir metin.

`DPJSFp_Cqyj` (500K, düz dünya):
- Uzaydan Dünya, ama kenarı bir UÇURUM. Okyanus boşluğa dökülüyor.
- Tanıdık görüntü + imkânsız tek değişiklik. Kanca bu.
- Caption soru soruyor: "How would sunsets actually work on a flat earth?"

**Ortak kalıp: tanıdık bir yer + tek imkânsız/felaket müdahalesi + kuş bakışı
ölçek + tek plan + gerçek ortam sesi.**

## 4. BİZDE NEDEN OLMADI , kök neden bulundu

Ölçüm sırasında kendi kodumuzda şunu buldum:

```
series/bible.py:326    native_audio varsayilani True   -> klipler SESLI uretiliyor
series/bible.py:271    native_mix_level varsayilani 0.0
series/produce.py:608  mix_voiceover(..., bg_duck=bible.native_mix_level)
```

`event-horizon/bible.json` içinde `native_mix_level` alanı **yok**, yani 0,0.
`narration.channel` ise dolu.

**Sonuç: motor 33 bölümün hepsinde gerçek ortam sesini üretti, sonra onu
SIFIRLA çarpıp attı ve yerine TTS anlatım koydu.** Üstüne `master_lufs` alanı
11 Eylül'e kadar yoktu, yani mastering adımı da hiç çalışmadı ve miks -22 LUFS
çıktı.

İhsan'ın gözlemi doğru ve gözlemlediğinden daha iyi: **o ortam sesini zaten
üretiyorduk, kendi elimizle siliyorduk.**

## 5. Bunu üretebilir miyiz , EVET, yeni kod gerekmiyor

| Gereken | Bizde ne var |
|---|---|
| 8 sn tek plan, sesli | `core/kie_api.py:475` Seedance 2 (`sound=True`) / Veo (`veo3_fast`, 8 sn) |
| Görselden videoya | `first_frame_url` parametresi |
| Ortam sesini KORUMAK | `bible.native_mix_level` , şu an 0,0, yükseltilecek |
| Anlatımı kapatmak | `narration.channel` alanını kaldır |
| -14 LUFS mastering | `bible.master_lufs: -14` , event-horizon'da ARTIK VAR |
| True peak -1,0 | `core/ffmpeg_tools.master_audio` içinde hazır |
| Teslimat kapısı | `required_layers: ["native_audio"]` , `produce.py:706` fail-closed doğruluyor |

`from-scratch/bible.json` bu kombinasyonu (`required_layers: ["hook_teaser",
"native_audio"]`, `music: false`) zaten taşıyor. Yani şablon depoda mevcut.

## 6. Instagram ses kütüphanesi sorusu

İhsan `instagram.com/reels/audio/165083033044073/` bağlantısını sordu.

- **Otomatik hattımızda seçilemez.** Yayını `core/uploader.upload_to_platform`
  üzerinden Upload-Post API'siyle yapıyoruz; IG ses kütüphanesinden parça
  iliştirmek yalnız Instagram uygulamasının kendi arayüzünde mümkün.
- **Gerek de yok.** Dev dalga videosunun sesi 7. saniyedeki çarpmayla birebir
  senkron. Genel bir kütüphane parçası görüntüye böyle oturmaz. O ses videonun
  kendi sesi, sonradan seçilmiş bir şarkı değil.
- Sabit bir marka müziği istenirse `core/music_generator.py` (Suno) tek parça
  üretir ve her bölümde aynısı kullanılır.

⚠️ Ses sayfası açılamadı (WebFetch içerik döndürmedi), parçanın adı ve kaç
reel'de kullanıldığı **ölçülemedi**.

## 7. Ölçülemeyenler

- Gerçek izlenme sayıları (IG API 429).
- Hesabın videolarının hangi motorla üretildiği (8,01 sn + 24 fps + 720p
  Veo 3 imzasıyla uyumlu ama **doğrulanmadı**).
- Retention eğrileri.
- 84 reel'in tarihleri (izgara kaydırması tarih vermiyor), bu yüzden
  "hesap düşüşte mi" sorusu cevaplanamadı, yalnız izgara sırası biliniyor.

---

# EK 4 , A/B BAKE-OFF SONUCU (12 Eylül 2026)

İhsan direktifi: "iki konsept için de 1'er video üret böylelikle hangisini daha iyi
yarattığımızı görebiliriz."

İki varyant gerçekten üretildi. Yayına ÇIKMADI: `series.experiment run` izole çıktı
ağacına yazdı, kredi `experiments_ledger.json` içine işlendi.
Deney kimliği: `exp-2026-09-bakeoff-ses`, aşama `bakeoff`.

Konu ikisinde de aynı (Satürn'ün halkaları Dünya'da), prompt gövdeleri aynı coğrafi
çapaları kullanıyor, `master_lufs` ikisinde de -14. Yani ölçülen şey FORMAT.

## 1. Ölçülen sonuç

| | **A** tek plan + native ses | **B** 2 plan + kesme + müzik |
|---|---|---|
| Süre | 8,00 sn | 8,03 sn |
| Kesme | **0** | **1 adet, 4,03 sn** |
| Çözünürlük / fps | 1080x1920 / 30 | 1080x1920 / 30 |
| **Integrated LUFS** | **-27,3** ❌ | **-14,3** ✅ |
| True peak | -0,5 dBFS | -1,5 dBFS |
| LRA | 7,8 | 6,6 |
| **Mastering kapısı** | **BAŞARISIZ, yayın tutuldu** | **GEÇTİ** |
| Kredi | **105** | **189** |
| Üretim süresi | ~2 dakika | ~6 dakika |
| QC | çekim 1 ilk denemede geçti | çekim 1 RED (gömülü yazı) → regen → geçti |

## 2. A neden kapıya takıldı

Motorun verdiği native ses **-26,18 LUFS**. Eski event-horizon formatının öldüğü
yerin aynısı, hatta daha kötü (-21,9 idi).

Mastering üç kez denedi:

```
deneme 1: limiter -1,0 dB  ->  -15,9 LUFS, TP +1,1  (tepe taşıyor)
deneme 2: limiter -3,3 dB  ->  -16,7 LUFS, TP -0,6
deneme 3: limiter -3,9 dB  ->  -17,0 LUFS, TP -3,0  (pes etti)
```

Sebep `core/ffmpeg_tools.py` `master_audio`: zincir `loudnorm(linear=true) + alimiter`.
`linear=true` yalnız sabit kazanç uygular, sıkıştırma yapmaz. Yatak -25 dB'de
dururken tek bir tepe -0,5 dB'de olunca limiter o tepeyi ezmek için tavanı indiriyor,
tavan inince gürlük de düşüyor. Kendi kendini kovalıyor.

**Kapı doğru çalıştı.** Fail-closed olmasaydı bu video sessizce -17 LUFS yayına çıkardı.

### İstediğimiz darbe geldi, yatak gelmedi

A'nın ses eğrisi 0,5 saniyelik dilimlerde:

```
  0,0 - 6,0 sn   -23 ile -26 dB arası, DÜMDÜZ
  6,5 sn         -20,1 dB  (6,80-6,90 arasında tepe -0,5 dB'ye fırlıyor)
  7,0 - 7,5 sn   -27 dB
```

6,80-6,90 arası ses 50 milisaniyede -17 dB'den -0,5 dB'ye çıkıp sönüyor. Yani
prompt'ta "6-8. saniyede patlasın" dediğimiz darbe **tam yerinde geldi**. Sorun
darbe değil, yatağın 10 dB fazla sessiz olması.

### Zorla düzeltmek işe yaramıyor

Motoru değiştirmeden dinamik loudnorm denendi:

| | LUFS | LRA |
|---|---:|---:|
| Ham | -26,18 | **7,60** |
| Dinamik master | -15,35 | **1,20** |

Seviye düzeliyor ama dinamik aralık 7,6'dan 1,2'ye çöküyor, yani "sessizlik sonra
çarpma" şekli tamamen düzleşiyor. Kazandığımız şeyi kaybediyoruz.

## 3. B'de müzik gerçekten kesmeye oturdu

B'nin ses eğrisi:

```
  0,0 sn   -40,3 dB   <- FADE-IN, kusur
  1,5 sn   -22,0 dB
  3,0 sn   -16,3 dB
  3,5 sn   -15,9 dB
  4,0 sn   -13,3 dB   <- KESME 4,03 sn'de. Müzik tam buraya yükseldi.
  6,5 sn   -14,4 dB
  7,5 sn   -26,7 dB   <- FADE-OUT, kusur
```

Müzik kesmeye yükseliyor. Nebula'da ölçtüğümüz etki üretildi.

**İki kusur var ve ikisi de konseptten değil, mikserden geliyor:**

```
core/ffmpeg_tools.py:1191
  afade=t=in:st=0:d=1.0,afade=t=out:st={fade_out_st}:d=1.5
```

- **1 saniyelik fade-in** ilk kareyi sessiz bırakıyor. İlk saniye kancanın en
  önemli saniyesi; ölçtüğümüz rakiplerin hiçbirinde fade-in yok.
- **1,5 saniyelik fade-out** döngüyü kırıyor. Doktrin "son kare başa rimlenir"
  diyor, fade-out bunu imkânsız kılıyor.

Müzik prompt'una "ilk saniyeden itibaren tam atmosferle aç" ve "ortada bitir"
yazılmıştı; Suno'nun değil mikserin sorunu.

## 4. Görsel karşılaştırma (kareler gözle incelendi)

**A:**
- Model `art_style`'daki "spacecraft-window" ifadesini birebir almış ve ekrana
  **lomboz çerçevesi** çizmiş. Kadrajın yaklaşık beşte biri koyu çerçeve.
- **Kamera kilitli kalmamış.** İlk karede halkalar sağda ve altta kadrajı sarıyor;
  7,8. saniyede belirgin biçimde yakınlaşmış ve halkalar büyük ölçüde kadrajdan
  çıkmış. Yani bölümün vaadi sonunda zayıflıyor.
  (Not: kaba koyu-piksel ölçümü bunu ayırt edemedi çünkü lomboz vinyeti sabit ve
  baskın; tespit kareleri gözle karşılaştırmaya dayanıyor.)
- Coğrafya iyi: Japonya, Filipinler, Avustralya okunuyor.

**B:**
- Lomboz yok, kadraj tam dolu.
- **Halka gölgeleri Pasifik bulut örtüsüne düşüyor**, prompt'ta istenen tam bu.
- Kesme sonrası **ölçek sıçraması çalışıyor**: halka düzleminin içinde, ev
  büyüklüğünde buz ve kaya blokları kadrajı dolduruyor, Dünya'nın kenarı çok
  aşağıda. Nebula'nın kalıbı birebir üretildi.
- QC ilk denemede çekim 1'i gömülü yazı yüzünden reddetti, regen sonrası geçti.
  Yani QC katmanı çalışıyor.

## 5. Karar için okuma

Ölçüme göre **B önde**, üç ayrı sebeple:

1. Teslim edilebiliyor. A mastering kapısına takıldı, B geçti.
2. Görseli daha iyi. Lomboz yok, kadraj kilitli kalıyor, ölçek sıçraması vuruyor.
3. Aranan ses etkisi üretildi.

A'nın tek üstünlüğü **maliyet**: 105 krediye karşı 189 kredi, yani B yaklaşık
1,8 kat pahalı. Günlük 1 video için 189 kredi kabul edilebilir.

### B seçilirse kapatılması gereken üç kusur

1. **Müzik fade'lerini kaldır.** `ffmpeg_tools.py:1191`. Bu ortak motor kodu,
   `footnotes` ve `the-vast` gibi müzikli seriler de kullanıyor; değişiklik
   opt-in bayrakla yapılmalı, yoksa onların çıktısı da değişir.
2. **Kesme %50'de, olması gereken %37.** Motor süre enum'u 4/6/8/10 olduğu için
   2,93 sn üretilemiyor. Çözüm: 3+5 saniyelik iki çekim mümkün değil, ama 8 sn
   tek klip üretip post'ta 2,93'te kesmek mümkün. Motor işi.
3. **`art_style`'dan "spacecraft-window" ifadesini çıkar.** A'da lomboz çizdirdi.

## 6. Ölçülemeyenler

- İzleyici tepkisi. Bu bir üretim kalitesi karşılaştırmasıdır, performans ölçümü
  değildir. Hangi formatın daha çok izlendiğini ancak yayınlayıp 44 saat bekleyerek
  öğreniriz.
- n=1. Her varyanttan tek video üretildi. Motorun varyansı ölçülmedi.
- A'nın kamera kayması tek bölümde gözlendi, kaç bölümde tekrarlandığı bilinmiyor.
- Suno'nun vuruşunun kesmeye milisaniye hassasiyetinde oturup oturmadığı
  ölçülmedi; ölçülen şey 0,5 saniyelik dilimlerde yükselişin kesme dilimine
  denk geldiğidir.

---

# EK 5 , GİRDAP VİDEOSU ANATOMİSİ (12 Eylül 2026)

İhsan direktifi: "bu girdap videosunu detaylıca incele, tam promptunu çıkart, bir
sonraki hedef bu videonun aynısını çıkartabilmek olmalı."

Kaynak: `instagram.com/reel/DQfOoo4ChGR/` , @earthimpacts25, 31 Ekim 2025.
Hesabın **ikinci en büyük** videosu.

## 1. Ölçüm

| | Değer |
|---|---|
| Beğeni | **382.016** |
| Yorum | 2.873 |
| Süre | **8,01 sn** |
| Kesme | **0** |
| Çözünürlük / fps | 720x1280 / 24 |
| Integrated LUFS | **-14,0** |
| True peak | -1,0 dBFS |
| **LRA** | **0,9** |
| Konuşma | 0 kelime |

Yorum/beğeni oranı: 2.873 / 382.016 = **%0,75**. Tsunami videosunda %0,90.

## 2. EN ÖNEMLİ BULGU: kadraj bir UÇAK PENCERESİ

Bu videonun kancası girdap değil, **nereden bakıldığı.**

Ekranda görünen: yolcu uçağının oval kabin penceresi, yuvarlatılmış köşeleriyle
kadrajın alt ve sol kenarını sarıyor; sağ üstte kanat ve winglet; altta kıyı kasabası,
liman ve mendirek; denizde ortası simsiyah, kolları köpüklü dev bir girdap.

**Yani video "biri uçakta telefonuyla çekmiş" gibi duruyor.** İmkânsız şeyi gerçek
gösteren şey bu. Temiz bir sinematik havadan çekim olsaydı AI olduğu anında okunurdu.

### Bu, benim daha önceki kararımı TERSİNE ÇEVİRİYOR

Bake-off'ta A varyantında model `art_style`'daki "spacecraft-window" ifadesini
birebir alıp lomboz çerçevesi çizmişti ve ben bunu kusur sayıp ifadeyi kaldırdım
(doktrin v2.1, bölüm 7.1, kural 5).

**Yörünge çekimi için o karar doğruydu, ama bu format için yanlış olurdu.** Burada
çerçeve kusur değil, formatın kendisi. Doğru kural şu: *çerçeve BİLEREK istenirse
formatın parçasıdır; istenmeden gelirse kusurdur.* Yani nesne adı yasağı mutlak
değil, bakış modu bölüm bazında seçilmeli.

## 3. Ses: tsunami videosunun TAM TERSİ

```
  0,0 sn  -12,9 dB      4,0 sn  -14,5 dB
  1,5 sn  -16,0 dB      6,0 sn  -15,3 dB
  2,5 sn  -14,0 dB      7,5 sn  -13,9 dB
```

Sekiz saniye boyunca **-13 ile -16 dB arası, dümdüz**. LRA 0,9.

Sessizlik anı yok, çarpma yok, ark yok. Sadece sabit ve gür bir uçak kabini uğultusu
artı rüzgâr. Tsunami videosunda LRA 8,6 ve 16 dB'lik iniş çıkış vardı.

**Ders: ses arkı OLAYA bağlı, formata değil.** Çarpma olayı varsa sessizlik-sonra-darbe;
süregiden bir olay (girdap, dönme, akış) varsa sabit ve gür yatak. İkisi de -14 LUFS.

## 4. Hareket

Kamera pencereye sabit ama tam kilitli değil: sekiz saniyede hafif bir içeri itme var.
İlk ve son kare kompozisyon olarak neredeyse aynı; değişen şey girdabın açılması,
boğazının derinleşmesi ve köpük kollarının keskinleşmesi. Kesme yok.

## 5. Caption: AI olduğunu AÇIKÇA söylüyor

> Off the northeast coast of Britain, the sea moves in slow, endless motion , a vast
> whirlpool circling with calm precision, as if the ocean itself is breathing. From above...
>
> #earthimpacts #fblifestyle #unrealviews #oceandreams #aiartcommunity #visualexploration
>
> **This content isn't real , it's a simulated 'what if' scenario created by AI for
> visual exploration.**

382 bin beğenili video AI olduğunu açıkça yazıyor ve bu performansını düşürmemiş.
Bizim doktrinimizin dürüstlük kuralı bu ölçümle desteklenmiş oluyor.

Ayrıca yer BURADA adlandırılıyor ("northeast coast of Britain") , ama caption'da,
görüntüde değil. Bölüm 7.1 kural 1'le çelişmiyor: kural prompt'a yer adı yazmakla
ilgili, caption'la değil.

## 6. Üretim promptu (tersine çıkarıldı)

`tools/tersine_prompt.py` çıktısı, Gemini vision 8 kare üzerinden:

> The shot opens looking out of an airplane window, revealing a vast expanse of
> grey-blue ocean. The white wing of the aircraft is visible in the upper right,
> partially framing the view. Below, a colossal, swirling whirlpool dominates the
> water, its frothing white foam contrasting with the dark, deep center. Beyond the
> turbulent vortex, a sprawling coastal city with sandy beaches and a busy harbor
> stretches along the distant shoreline under an overcast sky. The camera gently
> pushes forward, subtly magnifying the intricate details of the whirlpool, before
> slowly pulling back to reveal the full panoramic view again. A steady, low hum of
> airplane engines fills the air, consistent and unwavering, with a subtle, constant
> whoosh of wind passing the fuselage. The sound remains at a stable, moderate level
> throughout the shot, creating a continuous ambient drone.

Aracın kendi risk listesi:
- Uçak penceresi ve kanadın çekim boyunca TUTARLI kalması
- Girdabın su dokusunun ve hareketinin gerçekçiliği
- Girdap ile uzaktaki şehir arasındaki ölçek dengesi

## 7. Kopyalamak için gereken, madde madde

1. **Bakış: yolcu uçağı penceresi.** Oval kabin çerçevesi alt ve sol kenarda, sağ
   üstte kanat ve winglet. Çerçeve BİLEREK istenir.
2. **Hava: kapalı.** Gri bulut örtüsü, gri-yeşil deniz. Güneşli değil. Bu, amatör
   çekim hissini güçlendiriyor.
3. **Kıyı uzakta.** Kasaba, liman, mendirek üst üçlükte ve KÜÇÜK. Girdap ana özne.
4. **Girdap: ortası SİMSİYAH açık boğaz**, çevresinde spiral köpük kolları.
5. **Hareket: çok hafif içeri itme.** Kilitli değil ama kamera hareketi de değil.
6. **Ses: sabit kabin uğultusu + rüzgâr, -14 LUFS, ark YOK.**
7. **Caption AI beyanını taşır.**

## 8. Doktrin için açık soru

Bizim doktrinimiz bakış açısını "yörüngeden ya da yüksek hava" diye tanımlıyor
(bölüm 3). Bu video **üçüncü bir mod** gösteriyor: yolcu POV'u. Hesabın ikinci en
büyük videosu bu modda.

Ek fayda: pencere çerçevesi modele güçlü bir kompozisyon çapası veriyor, bu da
bölüm 7.1 kural 4'teki "motor kilitli kamerayı tam tutmuyor" sorununu hafifletebilir.

**Karar İhsan'ın:** bu mod doktrine eklensin mi?

## 9. Ölçülemeyenler

- Gerçek izlenme sayısı (IG API 429; 26M rakamı İhsan'ın gördüğü sayıdır).
- Hangi motorla üretildiği.
- Pencere çerçevesinin performansa katkısı izole edilmedi; n=1, aynı hesapta
  çerçevesiz videolar da büyük vuruş yapmış (tsunami 42K, düz dünya 500K).

---

# EK 6 , @space_art.ai BES VIDEOLUK KARSILASTIRMA (13 Eylul 2026)

Ihsan bes link verdi: uc tanesi ilk turda (14,5M / 2,1M / 65K), iki tanesi ikinci
turda (268K / 78K). Hepsi TEK hesaptan, ayni format. Bu, hesabin kendi icinde
dogal bir deney demek: teknik degiskenler sabit, performans 223 kat degisiyor.

Izlenme sayilari Ihsan'in uygulamadan okudugu degerlerdir; **biz olcemedik**
(IG izlenmeyi disariya vermiyor). Geri kalan her sey 13 Eylul'de `yt-dlp` +
`ffmpeg` ile olculdu.

## 1. Olcum tablosu

| | A | B | D | E | C |
|---|---|---|---|---|---|
| reel | `DbXH3hTMQj9` | `DcXi8TRM9Q9` | `DbgKZG1M83B` | `DbqjAQSMEAk` | `DcEbu_hs_jE` |
| konu | banliyo halkasi, Dunya | sonsuz banliyo adasi | tek yelkenli, halka kanali | marina, halka kanali | banliyo halkasi, pembe gezegen |
| tarih | 29 Tem | 23 Agu | 1 Agu | 5 Agu | 15 Agu |
| **izlenme** | **14.500.000** | **2.100.000** | **268.000** | **78.000** | **65.000** |
| begeni | 841.865 | 172.188 | 16.808 | 2.810 | 5.337 |
| yorum | 4.480 | 843 | 142 | 33 | 23 |
| begeni/izlenme | %5,81 | %8,20 | %6,27 | %3,60 | %8,21 |
| yorum/1000 izlenme | 0,31 | 0,40 | 0,53 | 0,42 | 0,35 |
| sure | 7,15 sn | 7,52 sn | 8,10 sn | 8,15 sn | 7,41 sn |
| kesme | 0 | 0 | 0 | 0 | 0 |
| fps | 20,27 | 60 | 24 | 30 | 50 |
| LUFS | -14,1 | -14,0 | -14,0 | -14,1 | -14,1 |
| true peak | -1,3 | -1,2 | -1,1 | -5,1 | -2,7 |
| LRA | 0,9 | 0,9 | 2,1 | 0,8 | 1,4 |
| konusma | 0 | 0 | 0 | 0 | 0 |
| hashtag | yok | yok | yok | yok | yok |
| caption | Infinite Neighborhood🌍 | Infinite floating island♾️ | Maybe this is where dreams go✨ | The Ring Marina🪐⛵ | Infinite Neighborhood🩷 |

## 2. Teknik format performansi ACIKLAMIYOR

Bes videonun hepsi: 7-8 sn, tek plan, sifir kesme, sifir kelime, -14 LUFS, dikey.
En iyi ile en kotu arasinda 223 kat fark var ve teknik parmak izleri ayni.
**Teknik format giris bileti, ayirt edici degil.**

Izleyici basina etkilesim de neredeyse sabit: yorum/1000 izlenme 0,31 ile 0,53
arasinda ve siralamayla ILGISIZ (en yuksek yorum orani 268K'lik videoda).
Yani kotu performans "izleyici sevmedi" demek degil, **"video izleyiciye
ulasmadi"** demek. Ulasimi belirleyen sinyaller (ilk saniye tutma, paylasim,
kaydetme) IG'de disariya kapali, olcemedik.

## 3. En temiz ortusme: SES SONA DOGRU BUYUYOR MU

Her videonun ses zarfi olculdu (ilk ceyrek ortalamasi -> son ceyrek ortalamasi,
normalize RMS):

| video | izlenme | ses zarfi | yon |
|---|---|---|---|
| A | 14,5M | 0,61 -> 0,69 | **yukseliyor** |
| B | 2,1M | 0,60 -> 0,68 | **yukseliyor** |
| D | 268K | 0,30 -> 0,61 | **yukseliyor (en keskin)** |
| E | 78K | 0,70 -> 0,71 | duz |
| C | 65K | 0,58 -> 0,52 | dusuyor |

**Sesi yukselen uc video, en iyi uc video. Yukselmeyen iki video, en kotu iki
video.** n=5 ve tek hesap, yani kanit degil; ama bu kadar temiz bir ayrim
gorulduginde test edilmeye deger. Bizim kendi girdap videomuzda sabit gur bir
yatak vardi, yukselen bir kapanis YOKTU.

## 4. A ile B ayni muzigi kullaniyor, C, D, E farkli

Capraz korelasyon (1,0 = ayni kayit): **A-B 0,998.** Diger butun ciftler 0,05'in
altinda. Yani hesap 14,5M ve 2,1M'lik iki videosunda ayni parcayi, ayni
baslangic noktasindan kullanmis.

Kazanan parcanin olculen kimligi: si minor duragan pad (B3 247 Hz, G4 382 Hz,
B4 494 Hz), 8 kHz ustu enerji %0,7 (davul, vurmali, hi-hat YOK), enerjinin %85'i
200-2000 Hz, yaklasik 2,5 saniyede bir agir vurus (1,18 / 3,8 / 6,1 sn).

**Bunun bizim icin anlami:** ayni sesi bolumden bolume tekrar kullanmak
performansi dusurmemis. B, A'nin sesini aynen kullanip 2,1M almis. Yani tek marka
sesi tutarli bir secim; tekrar eden sey GORUNTU oldugunda is degisiyor (bkz. 5).

## 5. Iki kez tekrar eden oruntu: AYNI DUNYAYI IKINCI KEZ CEKMEK COKUYOR

Tarih sirasina dizince:

1. **A**, 29 Tem, banliyo halkasi + Dunya , **14,5M**
2. **D**, 1 Agu, halka kanalinda TEK yelkenli , **268K**
3. **E**, 5 Agu, ayni halka kanali ama MARINA (yuzlerce tekne) , **78K** , D'nin
   dunyasinin 4 gun sonraki tekrari, **3,4 kat dusus**
4. **C**, 15 Agu, A'nin kompozisyonu ama pembe uydurma gezegen, **ayni baslik** ,
   **65K** , A'nin 17 gun sonraki tekrari, **223 kat dusus**
5. **B**, 23 Agu, YENI dunya (sonsuz ada) + A'nin muzigi , **2,1M**

Ornek sayisi 2/2. Yeni dunya kurulunca buyuk, ayni dunya tekrarlaninca kucuk.
B bu oruntuyu ayirt etmeyi saglayan vaka: muzik tekrarlanmis ama gorsel dunya
yeni, sonuc 2,1M. **Tekrarlanmamasi gereken sey gorsel dunya.**

Bu bulgu bizim kendi `aimagine` olcumumuzle de ortusuyor: tekrarlanan landmark
uc denemede uc kez kaybetmisti.

## 6. D ile E arasindaki farki SAYIYLA bulamadim, bakarak buldum

Iki goruntu istatistigi denendi ve ikisi de siralamayi ACIKLAMADI:

| video | kenar yogunlugu (kalabalik olcusu) | en parlak %2'nin dagilimi (odak olcusu) |
|---|---|---|
| D 268K | 8,84 | 15/180 hucre |
| E 78K | 6,14 | 9/180 hucre |

Kalabalik gorunen marina daha DUSUK kenar yogunlugu verdi (tekneler koyu ve
dusuk kontrastli), odak olcusu de kaybedeni daha "odakli" gosterdi. Yani bu iki
metrik bu isi olcmuyor, boyle yaziyorum.

Gozle gorulen fark su: **D'de kadrajda tek bir tanimlanabilir ozne var** , dev
gezegenin yanindaki kucucuk bir yelkenli. Izleyici kendini o teknenin icine
koyabiliyor. **E'de yuzlerce tekne var ve hicbiri ozne degil**; ayni dunyanin
altyapisi gosteriliyor, insanin yerlesecegi bir nokta yok.

Caption da ayni yonde: D "Maybe this is where dreams go" (duygu), E "The Ring
Marina" (etiket).

## 7. Uretime giren kurallar

1. Ses klibin SONUNA dogru buyusun. Duz ya da dusen zarf iki kaybedende de var.
2. Tek marka sesi tekrar kullanilabilir; **gorsel dunya tekrar edilemez.**
3. Kadrajda bir tane tanimlanabilir, insan olcegine yakin ozne olsun.
4. Caption kisa kalsin (2-4 kelime + emoji) ve hashtag olmasin , bes videoda da
   boyle. **Duygu mu etiket mi sorusu CEVAPSIZ:** D duygu yazip 268K almis, E
   etiket yazip 78K, ama 14,5M'lik A da etiket yaziyor ("Infinite Neighborhood").
   Yani caption tonu bu veriyle ayirt edilmiyor, iddia etmiyorum.
5. Taninabilir gercek yer (Dunya) uydurma gezegeni yeniyor (EK 5 ve bu ekteki A-C
   karsilastirmasi).

## 8. Olcemediklerimiz

Izlenme (Ihsan'in okudugu deger), paylasim, kaydetme, tutma egrisi, muzigin adi,
IG ses sayfasindan gelen trafik, hangi motorla uretildigi.

---

# EK 7 , @synthhorizon.ai (KONSEPT 3 ADAYI), 13 Eylul 2026

Ihsan uc link verdi ve "en cok izlenen 752K'lik videoyu aynen kopyalayabiliriz"
dedi. Hesap `synthhorizon.ai` (goruntulenen ad "infinite loop"), space_art.ai'den
BASKA bir hesap ve BASKA bir formul: uzun, hizli, FPV ucus.

## 1. Olcum

| | **X , 752K** | **Y** | **Z** |
|---|---|---|---|
| post | `DcX3cXfoFP4` | `Dcc9KKDIXVA` | `DdJAIElo1A0` |
| konu | Saturn halkalarinin icinden ucus | Uranus halkalarina dalis | Yengec Bulutsusu suzulusu |
| tarih | 23 Agu | 25 Agu | 11 Eyl |
| izlenme | **752.000** (Ihsan) | olcemedik | olcemedik |
| begeni | 34.415 | **515** | 1.536 |
| yorum | 66 | 7 | 5 |
| sure | **15,21 sn** | 15,05 sn | **17,04 sn** |
| kesme | 1 (13,5 sn'de beyaz patlama) | 0 | 0 |
| fps | 23,86 | 24 | 24 |
| LUFS / TP / LRA | -15,0 / **-0,3** / **12,7** | -14,7 / **+0,1** / 11,2 | -14,3 / -0,9 / 5,4 |
| caption | uzun + CTA + 5 hashtag | uzun + 5 hashtag | kisa + 5 hashtag |

Not: bu hesapta true peak 0 dBTP'ye dayaniyor, yani **kirpma riski var** (bizim
kapimiz -1 dBTP). Kopyalarken bunu kopyalamayacagiz.

## 2. Formul , space_art.ai'nin TERSI

| | space_art.ai (EK 6) | synthhorizon.ai |
|---|---|---|
| sure | 7-8 sn | 15-17 sn |
| kamera | sabit, cok yavas ileri itme | FPV, hizli dalis, savrulma |
| ses | duragan pad, LRA 0,9 | ses tasarimi, LRA 12,7, 15 sert vurus |
| ses zarfi | dolu baslar, hafif buyur | **neredeyse sessiz baslar** (0,08), 14. sn'de patlar (0,97) |
| kanca | ilk karede imkansiz sey | ilk kare SIYAH, acilim fade ile |
| caption | 2-4 kelime, hashtag yok | uzun cumle + CTA + hashtag |

X'in anatomisi: 0-4 sn genis Saturn ve halka duzlemi (sakin) -> 4-6 sn halkaya
dalis, ilk buz parcalari -> 6-13 sn parcalarin arasindan hizli ucus, carpmalar,
hiz bulanikligi -> 13,3-13,6 sn beyaz patlama (tek kesme) -> 14-15 sn buz
kristallerinin icinde kapanis. Ses bu olaylarla BIREBIR senkron: vuruslar 6,3 /
9,6 / 10,5 / 13,3-13,6. Enerjinin %35'i 200 Hz altinda, yani derin ugultu.

## 3. Ayni tekrar oruntusu, ucuncu kez

X (Saturn halkasina dalis) 23 Agustos'ta 34.415 begeni aldi. Y (Uranus
halkasina dalis, ayni anatomi) **iki gun sonra** ciktu ve 515 begenide kaldi,
yani 67 kat dusus. Bu, ayni bulgunun ucuncu tekrari:
C-A'dan sonra, E-D'den sonra, simdi Y-X'ten sonra. **Ayni dunyayi iki kez
cekmek her uc vakada da cokme getirdi.**

## 4. Hangi AI , KANITLANAMADI, en guclu hipotez Seedance 2.0

Dosyada uretici bilgisi YOK: Instagram her seyi kendi VP9 kodlamasiyla
(`encoder=VPC Coding`) yeniden sikistiriyor. Caption'larda da arac adi gecmiyor
(space_art.ai "Created with @openart_ai" yaziyordu, bu hesap yazmiyor).

Ihsan'in tahmini (Seedance 2.0, 15 sn) olculebilir kanitlarla UYUMLU:
1. Iki videonun suresi 15,21 ve 15,05 sn , Seedance 2.0'in tek cekim tavani 4-15 sn.
2. Ses gorsel olaylarla birebir senkron ve muzikal degil, ses tasarimi.
   Seedance 2.0'in ayri bir ses dali var ve senkron efekt uretiyor.
3. Filigran yok (Sora uygulama ciktisi filigran tasir).
4. 24 fps.

Uyusmayan tek veri: ucuncu video 17,04 sn ve kesmesiz. Bu, 15 sn tavanini asiyor;
ya Seedance'in "extend" ozelligi kullanilmis (son kareden 4-15 sn uzatma, dikissiz)
ya da baska bir model. **Kanit degil, hipotez.**

Pratik sonuc: Seedance 2.0 zaten bizim depomuzda
(`core/kie_api.py:475 generate_seedance_video`, 4-15 sn, `sound=True`). Hipotezi
test etmenin yolu bir bolum uretip yan yana koymaktir; fiyati depoda yazili degil,
ilk kosuda API'nin bildirdigi `creditsConsumed` ile olculur.

## 5. Bu konsepti secersek ne degisir

- Sure 8 sn degil 15 sn , kredi maliyeti yaklasik iki kati.
- Motorun kendi sesi KULLANILIR (bizim mevcut iki konseptimizde ses ya atiliyor
  ya muzikle degistiriliyor). QC'nin `native_audio_review` kapisi acilmali.
- Ilk kare siyahtan aciliyor; bizim doktrinimiz "ilk karede imkansiz sey okunsun"
  diyor. Bu konsept o kurali BOZUYOR ve yine de 752K almis. Yani kural evrensel
  degil, formata bagli.
- Kirpma riski (TP 0 dBTP) kopyalanmaz, -1 dBTP kapimiz kalir.

---

# EK 8 , KENDI UC KONSEPTIMIZIN BAKE-OFF SONUCU (14 Eylul 2026)

Olcum: 14 Eylul 2026, YouTube Data API v3 (izlenme/begeni/yorum), TikTok `yt-dlp`,
IG `yt-dlp` (izlenme giris duvarinda, yalniz begeni geldi). Teknik olcumler
yayinlanan yerel master dosyalarindan, `ffmpeg`.

13 Eylul'de Ihsan karariyla uc konsept adayi ayni kanala basildi. Bu ek onlarin
uctan uca olcumudur. Yayin kayitlari `<seri>/published.json`.

## 1. Olcum tablosu

| | konsept | yayin (UTC) | yas | YouTube | YT izl/saat | TikTok | IG begeni |
|---|---|---|---|---:|---:|---:|---:|
| One Wave Along the Whole Coast (p92) | A one-variable | 12 Eyl 22:07 | 46,6 s | 1.060 | 22,7 | **9.545** | , |
| One Whirlpool That Never Closes (p93) | A one-variable | 13 Eyl 18:03 | 26,7 s | **1.676** | 62,8 | 367 | 2 |
| Infinite Neighborhood | B infinite-places | 13 Eyl 22:24 | 22,3 s | **77** | 3,5 | 306 | 5 |
| Through the Rings of Saturn | C flythrough | 14 Eyl 16:16 | 4,4 s | 431 | **98,0** | 170 | **30** |

Kiyas: rafa kaldirilan event-horizon formatinin 15 bolumluk medyani **104**
(`gunluk_beyin/kanallar/event-horizon/defter.jsonl`, 23 Agu , 10 Eyl).
Yorum sayisi dort videoda da 0-3, yani ana sinyal olarak kullanilamadi.

**Yas esit degil.** C olcum aninda 4,4 saatlikti, 44 saatlik pencere dolmadi.
C icin asagidaki hicbir sonuc kesin degildir.

## 2. Teknik olcum , dordu de

| | fps | sure | LUFS | true peak | LRA | kesme | ses zarfi ilk>son | ilk 1 sn parlaklik |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A p92 tsunami | 24 | 8,0 | -17,9 | -0,9 | 13,3 | 0 | **+17,0 dB** | 124,8 |
| A p93 girdap | 30 | 8,0 | -14,1 | -2,2 | 0,9 | 0 | +2,2 dB | 129,9 |
| B mahalle | 30 | 8,0 | -13,9 | -2,2 | 2,6 | 0 | +3,4 dB | 56,9 |
| C saturn | 30 | 15,1 | -13,6 | -3,7 | 12,1 | 0 | +6,2 dB | 53,0 |

`olc.py` C'de 3 kesme raporladi (12,43 / 13,27 / 14,10 sn). **Yanlis pozitif**,
gozle dogrulandi: o anlar buz alanindaki hiz bulaniklig, kamera kesintisiz.
Skill'in 9. tuzagi (`scene=0.3` hizli hareketi kesme sanar) burada gerceklesti.
C tek plan kuralini BOZMUYOR.

## 3. B'nin cokusunu ACIKLAMAYAN olculer

B en kotu video (YT 77, kanalin olu formatinin bile altinda). Su hipotezlerin
hepsi olculdu ve hepsi B'yi ayirmakta BASARISIZ:

1. **Ses seviyesi degil.** B -13,9 LUFS ile hedefin tam ortasinda. Kazanan tsunami
   -17,9 ile hedefin 4 dB disinda ve true peak'i kirpma sinirinda (-0,9).
2. **Ses zarfi degil.** B'de +3,4 dB, kazanan girdapta +2,2 dB. B kurali daha iyi sagliyor.
3. **Hareket miktari degil.** Kare farki ortalamasi B 0,0061, girdap 0,0070. Fark yok.
   Ayrica en az hareketli video (tsunami, 0,0022) TikTok'ta 9.545 aldi.
4. **Parlaklik degil.** B 56,9 ile karanlik, ama C 53,0 ile daha da karanlik ve tutuyor.
5. **Yayin saati degil.** Tsunami 22:07 UTC'de cikip 1.060 aldi, B 22:24'te cikip 77 aldi.
6. **Doktrin uyumu degil.** B kendi doktrinine harfiyen uyuyor: tek plan, 8 sn, yazi yok,
   anlatim yok, hashtag yok, -14 LUFS, zarf yukseliyor.

Teknik olcumlerde B, dordun en "ortalama" videosu. Cokus teknikte degil.

## 4. Geriye kalan tek fark: OZNENIN GERCEKLIGI

Kareler gozle incelendi (0 / 2 / 4 / 6 / 7,8 sn, C'de 0 / 3 / 6 / 9 / 14,9 sn).

| video | ozne | gercek mi | ilk karede olay var mi | 8 sn boyunca degisim |
|---|---|---|---|---|
| tsunami | dev dalga + sahil sehri | **gercek olay, gercek sehir** | evet, dalga sehre yikiliyor | dalga limani yutuyor |
| girdap | dev girdap + kiyi kasabasi | **gercek olay, gercek kiyi** | evet, girdap aciliyor | girdap buyuyor ve derinlesiyor |
| Saturn | Saturn halkalari | **gercek gok cismi** | hayir, sakin genis plan | dalis, hiz, doruk |
| mahalle | Dunya'yi saran ev halkasi | Dunya gercek, **halka uydurma** | hayir | **bes kare neredeyse ayni** |

Tutan uc videonun oznesi gercek: tsunami, girdap, Saturn. Tutmayanin oznesi uydurma
bir geometri. Bu, konsept B'nin KENDI doktrininin 8. maddesidir ("uydurma gezegen
olculen en buyuk kayip sebebi, 223 kat dusus", EK 5).

Ikinci gozlem, olculdu ama tek ornek: B'de 8 saniye boyunca hicbir sey olmuyor.
Bes ornek kare neredeyse ayni. Diger uc videoda her karede durum degisiyor.

**Bu tek bir B videosudur, tek ornekten kural cikmaz.** Ancak filoda ayni yonde
UC bagimsiz olcum var:
- `shadowedhistory/still-home`: taninan sehir 46.042 begeni, isimsiz kubbe 124 (371 kat)
- `AImagine-Fear`: ikonik landmark 4/4 tuttu, tekrarlanan uydurma rota 3/3 kayip
- bu ek: gercek ozne 3/3 tuttu, uydurma ozne 1/1 kaybetti

Dort kanalda ayni yon. Hipotez kanit degil, ama tesaduf olarak aciklamak zorlasti.

## 5. Platform ayrisiyor, konsept secimini tek platformdan yapma

Ayni konseptin iki bolumu iki ayri platformda patladi:
- tsunami TikTok'ta 9.545, YouTube'da 1.060
- girdap YouTube'da 1.676, TikTok'ta 367

C, IG'de 4,4 saatte 30 begeni aldi; diger ucu 2, 5 ve olculemedi. IG izlenmesi
giris duvarinda, bu yuzden C'nin IG ustunlugu **begeni uzerinden**, izlenme degil.

## 6. Karar icin ne eksik

- C'nin 44 saatlik olcumu (16 Eylul ~12:00 UTC'de tamamlanir).
- Uc videoda da yorum 0-3. Doktrinin ana sinyali yorum oraniydi, bu orneklemde CALISMADI.
- IG izlenme sayilari (giris yapmis oturum gerekiyor, `ig_medya_bilgi.py`).

## 7. Olcemediklerimiz

- Retention ve skip rate: platform paneli gerekiyor, disaridan olculemez.
- Kac izlenmenin onerilenden, kac tanesinin aramadan geldigi.
- B'nin cokusunun izleyici tarafindaki sebebi. Elimizdeki tek sey kare
  karsilastirmasi, bu bir yorumdur, olcum degil.
