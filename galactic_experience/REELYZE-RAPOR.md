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
