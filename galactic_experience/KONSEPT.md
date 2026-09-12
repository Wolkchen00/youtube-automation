# GALACTIC EXPERIMENT, KANAL KONSEPT DOKTRİNİ v2.0

**Tarih:** 2026-09-12 · **Karar sahibi:** İhsan · **Statü:** TASLAK (İhsan onayı bekliyor)
**Önceki sürüm:** v1.5 "EVENT HORIZON" (29 Temmuz 2026). 12 Eylül 2026'da İhsan kararıyla
RAFA KALDIRILDI, tam arşivi `_surumler/2026-09-12_event-horizon-rafta/` içinde.

**Kanal:** `UCVCRWrQYrIHW6csOsw9bDNw` · @galacticexperiment-x6l · upload_profile:
`galacticexperimet` (profil adındaki yazım Upload-Post kaydının kendisidir, DÜZELTME) ·
repo klasörü: `galactic_experience/` · seri slug: `one-variable`

**Kanal kimliği DEĞİŞMİYOR** (İhsan kararı, 12 Eylül): ad, avatar, handle aynı kalır.
**Eski 199 video DURUYOR**, silinmez, gizlenmez.

> Bu doküman bu kanala prompt yazan HER otomasyonun tek kaynağıdır. Üretim koşuları
> bu dosyanın SHA-256'sını loglar; `series.json` içindeki `doctrine_sha256` pin'i
> tutmuyorsa koşu fail-closed durur. Metni başka kanala kopyalanmaz.

---

## 1. Teşhis: kanal ölmedi, format öldü

12 Eylül 2026 ölçümü (tam rapor: `REELYZE-RAPOR.md` EK 2 ve EK 3).

| | Biz | Aynı nişte AstroX | Aynı nişte Dark Narr |
|---|---:|---:|---:|
| Abone | 141 | 15.400 | 30.700 (10 aylık kanal) |
| Son 50 videonun medyanı | **127** | 42.320 | 57.050 |

Niş küçük kanala izlenme veriyor. Sorun konu seçimi değil.

Üç ölçülmüş sebep:

1. **Ses 6-11 dB fazla sessizdi.** Bizde -21,9 / -24,7 LUFS. Kazananların hepsi
   -14,0 ile -15,4 arasında. Telefon hoparlöründe bizim video duyulmuyordu.
2. **Kanca sözeldi, görsel değildi.** İlk karemiz bir uzay fotoğrafıydı, vaadi
   anlatım taşıyordu. Kazananlarda ilk kare tek başına imkânsız bir şey gösteriyor.
3. **Yorum oranı 1000 izlenmede 0,00.** Nişte 0,11-0,72. Kimse takılmıyordu.

### 1.1 Kök neden: ortam sesini kendi kodumuzla siliyorduk

```
series/bible.py:326    native_audio varsayılanı True   -> klipler SESLİ üretiliyor
series/bible.py:271    native_mix_level varsayılanı 0.0
series/produce.py:608  mix_voiceover(..., bg_duck=bible.native_mix_level)
```

`event-horizon/bible.json` içinde `native_mix_level` yoktu, yani 0,0; `narration.channel`
ise doluydu. **Motor 33 bölümün hepsinde gerçek ortam sesini üretti, sıfırla çarpıp attı,
yerine TTS anlatım koydu.** `master_lufs` alanı da 11 Eylül'e kadar yoktu, mastering hiç
çalışmadı. Bu doktrin o iki hatayı yapısal olarak imkânsız kılar.

### 1.2 Ölçülen kazanan anatomi (n=5, @earthimpacts25)

| Süre | Kesme | Beğeni |
|---:|---:|---:|
| **8,01 sn** | **0** | **500.229** |
| **8,01 sn** | **0** | **401.000** |
| **8,01 sn** | **0** | 42.195 |
| 24,0 sn | 3 | 8.618 |
| 48,02 sn | 5 | **306** |

Sıralama kusursuz monoton: **video uzadıkça ve kesme arttıkça performans düşüyor.**
"En uzun plan" beşinde de 8,00-8,02 saniye, yani AI motorunun tek üretim birimi.
n=5, kanıt değil, ama kanal düzeyi veriyle de uyuşuyor (VoidNubis 11 sn, space_art.ai 7,15 sn).

---

## 2. KONSEPT: "ONE VARIABLE", tek değişken deneyi

**Konumlandırma:** Her bölüm, gerçek ve tanınabilir bir yerde **tek bir değişkeni**
değiştirir ve sonucu **tek kesintisiz 8 saniyelik planda**, yukarıdan gösterir.
Ses yok denecek kadar sade: sadece o şeyin gerçekten çıkaracağı ses.

Kanal vaadi: *"Deneyi çalıştırdık. Sonuç bu."*

Kanal adı ilk kez içerikle örtüşüyor. Galactic Experiment artık gerçekten bir deney.

**Neden earthimpacts25'in kopyası değil:** onlarda çerçeve yok, sadece felaket var.
Bizde her bölüm bir deney, yani (a) tekrarlanabilir bir başlık kalıbı, (b) simülasyon
olduğunun doğal ve dürüst beyanı, (c) sonsuz konu alanı verir.

**Dürüstlük kuralı (tartışmaya kapalı):** bu videolar gerçek görüntü DEĞİL, hiçbir
yerde gerçek çekim gibi sunulmaz. "Deney" çerçevesi bunu zaten söyler; caption ayrıca
simülasyon olduğunu yazar. "Bunu ben çektim" tipi birinci şahıs iddia YASAK.

---

## 3. FORMAT, sayıyla

Bunlar ölçümden gelir, yaratıcı tercih değildir.

| Alan | Değer | Gerekçe |
|---|---|---|
| Çekim sayısı | **1** | 8 sn tek plan üç kazananın üçünde de var; kesme arttıkça düşüyor |
| Süre | **8 saniye** | motorun tek üretim birimi; bölme yok, ekleme yok |
| Kesme | **0** | monoton örüntünün tepesi |
| En | 1080x1920, 9:16 | mevcut standart, değişmiyor |
| Anlatım | **YOK** | beş kazananın beşinde de 0 kelime |
| Ses | motorun native sesi, **TEK ses** | bkz. bölüm 4 |
| Integrated loudness | **-14 LUFS** | kazananlar -14,0 / -15,4; biz -22 idi |
| True peak | **-1,0 dBTP** | üstü platform yeniden kodlamasında bozulur |
| Ekran yazısı | **YOK** | künye yok, altyazı yok, imza yok, kapanış kartı yok |
| Kamera | **KİLİTLİ** | olay kadraja girer, kamera peşinden gitmez |
| Bakış | yörüngeden ya da yüksek hava | ölçek referansı için gerçek coğrafya |

### 3.1 İlk kare kuralı

**İlk kare tek başına durmalı.** Ses kapalı, başlık okunmamış, hiçbir bağlam yokken
bile o kare "bu ne" dedirtmeli. Merak vaat etmek yetmez, GÖRÜNTÜ vaat edilecek.

İlk karede hem tanıdık şey hem müdahale aynı anda okunacak. Yavaş açılış, bekletme,
"birazdan göreceksiniz" kurulumu YASAK. 8 saniyede kurulum lüksü yok.

### 3.2 Sekiz saniyenin iç yapısı

```
0,0 - 1,5 sn   tanıdık yer + müdahale ilk karede okunur
1,5 - 5,0 sn   müdahale gelişir, kamera kilitli
5,0 - 8,0 sn   sonuç gerçekleşir, ödeme yapılır
```

Son kare bir kapanış değil, bir durum olmalı: döngüde tekrar izlendiğinde ilk kareyle
çelişmemeli. Kapanış jesti, kutlama, kameraya bakış, ta-da anı YASAK.

---

## 4. SES DOKTRİNİ, bu kanalın bir numaralı işi

Eski format tam burada öldü. Bu bölüm yapılandırmaya birebir yansır.

1. **Motorun native sesi KORUNUR ve tek ses odur.** `bible.series.native_audio: true`,
   `narration` alanı YOK, `music: false`. Anlatım olmadığı için `native_mix_level`
   çarpanı hiç devreye girmez, ses olduğu gibi geçer.
2. **`required_layers` içinde `native_audio` bulunur.** `produce.py:706`
   `_verify_native_audio_delivery` fail-closed doğrular: ses teslim edilmediyse
   bölüm yayına ÇIKMAZ. Sessiz başarısızlık bu kanalda bir daha olmaz.
3. **`master_lufs: -14`, `master_true_peak_margin_db: 0.2`.** Mastering atlanamaz.
4. **Sessizlik bir araçtır.** Ölçülen en iyi ses tasarımı (dev dalga videosu) şuydu:
   `0-1 sn -16,0 dB` → `4-5 sn -24,8 dB (en sessiz an)` → `7-8 sn -8,5 dB (çarpma)`.
   16 dB'lik iniş çıkış. Prompt bu şekli ister: **çarpmadan hemen önce bir sessizlik anı.**
5. **Dinamik aralık hedef DEĞİL, sonuçtur.** Ölçüm LRA'nın kazananlarda 0,9 ile 8,6
   arasında savrulduğunu gösterdi, yani LRA tek başına ayırt etmiyor. Kovalanacak
   sayı LRA değil, **-14 LUFS**.

### 4.1 Müzik (AÇIK KONU)

Şu an `music: false`. Ayrı bir hesap ailesinde (@nebula.galaxies) müziğin yükseldiği
anda kesme yapıldığı gözlemlendi ve bu ölçüm **12 Eylül itibarıyla devam ediyor**.
Ölçüm sonuçlanmadan müzik açılmaz. Açılırsa bu bölüm revize edilir ve pin yenilenir.

---

## 5. KANCA, BAŞLIK VE CAPTION

### 5.1 Başlık

Başlık deneyin kendisidir, düz cümleyle. Tıklama tuzağı noktalama yok, hashtag yok.

Kalıp: **`<tanıdık şey> + <tek değişken>`**, maksimum 70 karakter.

- İYİ: "Saturn's Rings Around Earth"
- İYİ: "The Pacific Ocean, Drained"
- İYİ: "The Moon at Space Station Altitude"
- KÖTÜ: "You Won't Believe What Happens Next"
- KÖTÜ: "Olympus Mons: Towers Over Everest" (ansiklopedi maddesi, eski formatın hatası)

Başlığın ÖZNESİ gözde canlanan bir ŞEY olmalı. Bu, `gunluk_beyin` defterindeki
"başlık öznesi" hipotezinin bu kanala uygulanmasıdır.

### 5.2 Caption

Hikâye videoda değil caption'da. 70-140 kelime, akıcı İngilizce.

Sırası: deneyin tek cümlelik tanımı → değiştirilen tek değişken → gerçek fiziğin ne
dediği → gerçekte neden olamayacağı → izleyiciye tek soru.

**Caption şunu açıkça yazar: bu bir simülasyondur.** Gerçek sayı verilecekse doğru
olacak; emin olunmayan sayı hiç yazılmaz.

Hashtag: 6-9 adet, konuyu ve nişi anlatan.

---

## 6. KONU HAVUZU VE AİLELER

Kanonik aile listesi (`auto_replenish.families` ile birebir aynı olmak zorunda):

1. `yörünge deneyi` , gök cisimlerinin yerini veya yörüngesini değiştirmek
2. `ölçek deneyi` , bir şeyi tanıdık bir yerin yanına gerçek ölçeğiyle koymak
3. `su deneyi` , okyanus, buz, nehir kütlesini taşımak veya kaldırmak
4. `atmosfer deneyi` , havanın bileşimini, yoğunluğunu veya davranışını değiştirmek
5. `yerçekimi deneyi` , yerçekimini artırmak, azaltmak veya yönünü değiştirmek
6. `ışık ve zaman deneyi` , güneş ışığı, gölge, dönme hızı, gün uzunluğu

**Ardışık iki bölüm aynı aileden olamaz.** Motor bunu mekanik olarak reddeder.

Her bölüm **gerçek ve tanınabilir bir yere** demirlenir (gerçek kıyı, gerçek dağ,
gerçek şehir silueti, gerçek gezegen). Ölçek referansı buradan gelir. Uydurma yer adı
kullanılmaz; eski `planetfall` serisinin kurgu gezegen isimleriyle 0 izlenme alması
bu dersin kaynağıdır.

---

## 7. YASAKLAR

- **Anlatım, konuşma, dudak senkronu, TTS.** Hiçbir koşulda.
- **Ekran yazısı, künye, altyazı, logo, filigran, kapanış kartı.**
- **Birinci şahıs gerçeklik iddiası** ("bunu ben çektim", "teleskobumla yakaladım").
- **Gerçek adlı şehirde gerçekçi can kaybı sahnesi.** Deney fizik gösterir, felaket
  pornosu yapmaz. İnsan figürü, ceset, panik kalabalığı, yıkılan meskûn bina yakın
  planı yok. Ölçek ve fizik yeterince etkileyici.
- **Kurgu yer adı.**
- **Birden fazla çekim.** Bölüm tek plandır. İki plana ihtiyaç duyuluyorsa fikir
  yanlıştır, bölüm reddedilir.
- **İkinci bir değişken.** Adı üstünde: tek değişken.

---

## 8. ÖLÇÜM VE KARAR KURALLARI

- Ana sinyal **yorum oranı** (1000 izlenmede). Eski formatta 0,00 idi, nişte 0,11-0,72.
  Beğeni oranı ayırt etmiyor, ona bakılmaz.
- Değerlendirme penceresi **44 saat**. Daha erken "tutmadı" denmez; `aimagine` ölçümünde
  21. saatte 1 izlenmede olan video 44. saatte 1.568'e çıkmıştı.
- Sabır penceresi **25 bölüm**. Format bundan önce değiştirilmez.
- Her bölümün teslim edilen LUFS'u ölçülür ve deftere yazılır. -16 ile -13 dışına
  çıkan bölüm kusurlu sayılır.
- Günlük 1 video tavanı geçerli (filo kuralı, kanal başına).

---

## 9. AÇIK SORULAR (ölçülmedi, karar verilmedi)

- **Müzik açılacak mı, açılırsa kesme senkronu nasıl?** Ölçüm sürüyor (bölüm 4.1).
- **24 fps mi 30 fps mi?** Ölçülen beş kazananın beşi de 24 fps, bizim çıktımız 30.
  Nedensellik kanıtlanmadı, motor değişikliği ayrıca değerlendirilecek.
- **Çözünürlük gerçekten önemli mi?** 500 bin ve 401 bin beğenili iki video 720x1280
  çıkmış. Yani 1080p bir kazanma sebebi değil. Maliyet tartışmasında bu bilinmeli.
- **8 saniye mi 7 mi 10 mu?** space_art.ai 7,15 sn, earthimpacts25 8,01 sn,
  VoidNubis 11 sn. Bant dar ama optimum ölçülmedi.
- Retention eğrileri (YouTube Studio gerekiyor).
