# Referans hesap analizi ,  @ayush_0_ai

Ölçüm tarihi: 13 Eylül 2026. Yöntem: 11 reel yt-dlp ile indirildi, ffprobe/ffmpeg ile
ölçüldü, 2 fps kare çıkarımı (video başına 20 kare) ile gözle incelendi.
Ham dosyalar ve kontakt sayfaları scratchpad'de, ölçüm tablosu `olcum.json`.

Hedef video: https://www.instagram.com/reel/DctJSa2hYPJ/ (shoebill kuşu)

---

## 1. Üretim imzası ,  11 videonun 11'i birebir aynı

| Ölçüt | Değer | Kaç videoda |
|---|---|---|
| Süre | **10,01 sn** | 11/11 |
| Kare hızı | **24 fps** | 11/11 |
| Çözünürlük | **1080×1920** (9:16) | 11/11 |
| Kare sayısı | **240** | 11/11 |
| Sahne kesmesi | **0 ,  tek plan** | 11/11 |
| Ses | var, ortam sesi | 11/11 |
| LUFS | −14,0 ile −16,8 arası | 11/11 |

Bu bir tercih değil, bir **motor imzası**: tek çağrı, 10 saniye, 1080p dikey, 24 fps.

**Watermark doğrulandı:** kadrajın sağ-altında dört köşeli parıltı (✦) ,  Google Veo
(Gemini) işareti. Kullanıcının tespiti doğru. Kare: `wm_zoom.jpg`.

---

## 2. Performans ,  kanal aslında ölü, 3 video patlamış

İzlenme değil **beğeni** sayıları (IG ızgara rozeti + info.json).

### Patlayanlar (sabitlenmiş ilk 3 + 1)

| Video | Konu | Beğeni | Yorum |
|---|---|---|---|
| DcgHdIIMGJf | Dev **anakonda**, kadını yutar, ekip yılanı açar | **675.316** | 2.164 |
| DctJSa2hYPJ | Dev **shoebill kuşu**, adamı ağzına alır | **~148.000** | ,  |
| Dcfjx3DhGMD | **Minyatür dağ maketi** + gerçek boy SUV | **16.691** | 8 |
| DdFs7RWB534 | Dev **kaplan**, adamı devirir, ekip çıkarır | **6.076** | 13 |

### Ölüler (son yüklenenler)

| Video | Konu | Beğeni |
|---|---|---|
| DdIYvbhhU26 | Dev **zürafa** ,  sadece yürüyor | 135 |
| DdK6e4zhKEm | Dev **kobra** ,  kükrer | 134 |
| DdG2oFHMWFk | **Kurt/canavar** | 130 |
| DdL-4URBXSb | **T-Rex** | 126 |
| DdNaFkaBOv3 | Dev **örümcek** | 72 |
| DdJVfgehirp | Dev **ahtapot**, su tankı | 64 |
| DdOmEy4SVtd | **Ejderha** + kale seti | 42 |

**Bu tablo işin en önemli kısmı.** "Bu adam 10M izleniyor" doğru değil: aynı format,
aynı motor, aynı caption ile 675.316 ile 42 arasında salınıyor. Yani formatı
kopyalamak tek başına yetmez ,  **ayırt edici, formatın içindeki seçimler.**

---

## 3. Caption ayırt edici DEĞİL

Hepsinde aynı kalıp:

> "Ever wonder how [X]? Here is a behind-the-scenes look at [Y].
> What is your favorite [Z]? #BehindTheScenes #VFX #filmmaking"

675.316 beğenili videoda da, 42 beğenili videoda da aynı. **Fark caption'da değil,
görüntüde.**

---

## 4. Kazananı kaybedenden ayıran dört şey (ölçülmüş)

### (a) SİS ,  ölülerde var, kazananlarda yok
Örümcek (72), T-Rex (126), kobra (134), kurt (130): kadrajda belirgin duman/sis.
Anakonda (675K), shoebill (148K), kaplan (6K): **sis yok, hava temiz**.

> Bu bizim `DOKTRIN` kural 5'teki "çıplak düzenek" bulgusunu bağımsız olarak doğruluyor.
> Ama bizim `art_style` şu an tam tersini yazıyor: `with practical haze`.

### (b) TEMAS ,  yaratık insanı fiziksel olarak ALMALI
- Kazananlar: yılan kadını **yutar**, kuş adamı **gagasına alır**, kaplan adamı **devirir**.
- Ölüler: zürafa yürür, kobra kükrer, örümcek durur, T-Rex kükrer. **Temas yok.**

Zürafa kritik kanıt: gerçek hayvan, devasa ölçek, temiz set ,  ama **temas olmadığı için 135**.
Yani "gerçek hayvan" tek başına yetmiyor; tutan şey **yakalanma anı**.

### (c) İFŞA ,  sonda ekip yaratığı açıp insanı çıkarır
675.316'lık videoda final: yılanın yan gövdesi **kapak gibi açılıyor**, kadın içinden
çıkıyor. "Bu dev yaratık aslında içinde insan olan bir kukla" cevabı **videonun içinde**
veriliyor. Shoebill'de de ekip koşup adamı çıkarıyor.
Ölülerde bu vuruş ya yok ya da zayıf.

### (d) TANIDIK GERÇEK HAYVAN > uydurma yaratık
Kazananlar: anakonda, shoebill, kaplan ,  izleyicinin **tanıdığı** hayvanlar, devleştirilmiş.
Ölüler: ejderha (42), kurt-canavar (130), dev örümcek (72) ,  uydurma ya da jenerik korku.

---

## 5. Görsel gramer (prompt'a girecek olan)

Kontakt sayfalarından ölçülen, 11/11 tutarlı:

- **Perde: MAVİ**, üzerinde açık mavi artı/yıldız tracking marker'ları. Yeşil değil.
- **Zemin: stüdyo betonu görünür**, üzerine serilmiş kum/toprak "adası". Setin kenarı
  betona bitiyor ,  yapımın sahte olduğu bu sınırdan anlaşılıyor.
- **Set dekoru minimal**: kum + birkaç kaya + seyrek ot/kütük. Yoğun bitki örtüsü yok.
- **Işık**: tavanda büyük beyaz difüzyon ızgarası / softbox dizisi, her karede görünür.
- **Ekip**: 4–10 kişi, koyu/siyah kıyafet, kamera operatörleri, dolly rayı, boom mikrofon,
  monitörler, yerde kablolar ve renkli işaret bantları.
- **Kamera hareketi**: tek plan içinde **yavaş push-in** ,  geniş kuruluş kadrajından
  yakın plana doğru sürekli ilerleme. Sabit tripod değil, elde/gimbal hissi.
  (Kare karşılaştırması: `kamera_hareket.jpg`)
- **Ekranda yazı yok. Müzik yok. Anlatım yok.** Sadece ortam sesi.

---

## 6. Bizim wild-encounter ile fark tablosu

| | Referans (kazananlar) | Bizim mevcut format |
|---|---|---|
| Çekim | **1 çekim** | 3 çekim (`shots: 3`) |
| Süre | **10 sn** | 8+8+8 = 24 sn (`duration_band: 12–26`) |
| Kesme | **0** | 2 (zincirleme) |
| Sis | **yok** | `practical haze` + `low drifting haze` |
| Perde | **mavi** | `green screen wall` |
| Set dekoru | minimal kum/kaya | yoğun orman, sarmaşık, yaprak |
| Yaratık ailesi | gerçek tanıdık hayvan | `insect-giant` dahil (örümcek = 72) |
| Kredi/bölüm | 1×10 sn = **100** | 3×8 sn = **240** |

Not: `bible.json` içindeki `duration_note` zaten şunu kaydetmiş , 
*"referans hesabin videolari 24-32 saniyeye cikinca medyani 2.161'den 325 begeniye
dusmustu"*. Bu yeni ölçüm aynı yöne işaret ediyor: **10 saniye.**

Ayrıca ep07'nin kesik çıkma arızası doğrudan 3-çekim zincirlemesinden geliyordu.
Tek plana geçmek o arıza sınıfını tamamen ortadan kaldırır.

---

## 7. Tersine mühendislikle çıkarılan prompt iskeleti

Referansın tek çağrılık prompt'u şu bileşenlerden oluşuyor:

```
Vertical 9:16 photoreal behind-the-scenes footage of a real film shoot,
filmed as ONE CONTINUOUS UNCUT SHOT, 10 seconds, no cuts.

SET: a film studio soundstage. A large BLUE screen wall with pale blue cross
tracking markers fills the background. The bare studio concrete floor is visible
at the edges of frame; a shallow island of dry sand and earth is dressed over it,
with a few scattered rocks, a bare log and sparse dry grass. No fog, no haze,
no smoke, clear air.

LIGHT: a wide overhead grid of large white diffusion softboxes, visible at the
top of frame, casting even soft daylight.

PRODUCTION: [4-10] crew in dark clothing, camera operators with cinema cameras on
a dolly track, a boom microphone, monitors and cables on the floor.

SUBJECT: one enormous, photoreal [REAL ANIMAL] standing on the set, scaled so its
[jaws/beak] are large enough to take a whole human. It is a practical animatronic
prop, not a living animal.

ACTION (one continuous 10s beat): the creature [takes the person into its mouth /
knocks them down], the person disappears from view, the crew rush in, force the
creature open and the person climbs out unharmed.

CAMERA: one unbroken handheld shot that pushes slowly in from a wide establishing
frame to a close frame. No cuts, no edits.

AUDIO: ambient sound only ,  crew movement, studio air handling, footsteps on sand.
No music, no narration, no speech.

No on-screen text.
```

---

## 8. Hâlâ ölçülmemiş olanlar

- **Gerçek oynatma sayısı.** Elimizdeki beğeni; IG media-info API 429 verdi
  (bilinen tuzak). Göreli sıralama güvenilir, mutlak izlenme değil.
- **Kanalın ilk 3 videosunun ne zaman patladığı.** Geç ateşleme ihtimali ölçülmedi
  (bizim `aimagine-kanal-bulgulari` dersi: 44 saat dolmadan ölü sayma).
- **Motorun tam sürümü.** Watermark Veo diyor; hangi Veo sürümü olduğu kareden
  çıkarılamıyor.
- Örneklem 11 video. "Sis kötü" ve "temas şart" hipotezleri **güçlü ama tek hesaptan**;
  kendi kanalımızda A/B ile doğrulanmalı.
