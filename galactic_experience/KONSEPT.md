# GALACTIC EXPERIMENTS, KANAL KONSEPT DOKTRİNİ v1.3
**Tarih:** 2026-07-29 · **Karar sahibi:** İhsan · **Statü:** TASLAK (İhsan onayı bekliyor)
**v1.1 (aynı gün, Codex Same Page turu 1):** hook_teaser kapatıldı (loop bütünlüğü); planetfall
emekliliği paused + replenish-kapalı olarak düzeltildi (completed diriltilir, motor gerçeği);
konu havuzu kuralı eklendi; ölçüm tablosu ölçülebilirlik etiketleri aldı; 6 tohum fakt
kaynaklara göre düzeltildi.
**v1.2 (aynı gün, turu 2):** seed_id kod tarafı doğrulaması; kanonik aile enum'u + ardışıklık
RED; #15 kartı kuralı netleşti (elle havuza eklenir); güvenlik maddesi; music_style sabitlendi;
doctrine_sha256 pin'i; hat açma ön koşulu havuz ≥25; 2 tohum netleştirildi.
**v1.3 (aynı gün, turu 3):** havuzun teknik tek kaynağı series.json `topic_pool` oldu
(id+topic+family; prompt'a runtime enjekte edilir); plan damgası eklendi (doktrin revizyonu
bekleyen planları geçersizleştirir); #15 kartı prosedürü: önce doktrin listesi, sonra
topic_pool + pin.
**Kanal:** `UCVCRWrQYrIHW6csOsw9bDNw` · @galacticexperiment-x6l · upload_profile: `galacticexperimet`
(profil adındaki yazım Upload-Post kaydının kendisidir, DÜZELTME) · narration register:
`galactic_experiment` · repo klasörü: `galactic_experience/`

> S4 kararı (2026-07-27): 12-24 sn uzay-faktı formatına dönüş + #15 Konu Kaşifi kartlarının
> konu kaynağı olması. Bu doküman o kararın uygulanabilir doktrinidir. Bu kanala persona/prompt
> yazan HER otomasyon bu dosyayı referans alır; doktrin TEK KAYNAKTIR, metni başka kanala
> kopyalanmaz (çapraz bulaşma kuralı, KANAL_ENTEGRASYON_PLANI_v2 FAZ 3). Üretim koşuları bu
> dosyanın SHA-256'sını loglar.

---

## 1. Teşhis: gerçek evren kazandı, kurgu evren kaybetti

Ölçüm (FAZ 0 röntgeni 2026-07-27 + canlı FAZ 2 snapshot 2026-07-29): 172 video, 57.653
izlenme, 121 abone, 30 günlük medyan 72.

1. **Mart 12-24 sn GERÇEK uzay-faktı dönemi kazandı:** medyan 1.085 (yalnız 9 videoyla, dört
   kanalın en yüksek format medyanı). Canlı snapshot doğruluyor: "Mars' Sleeping Giant: Olympus
   Mons" 4.777, "Earth's Fiery End" 1.708, "The Universe is Tearing Itself Apart!" 1.672,
   "The Boötes Void" 1.557, "Neptune: Diamond Rain" 1.389.
2. **Mayıs ALL-CAPS "What If" 32 sn formatı kaybetti:** medyan 24x düştü (tek tük vuruş var,
   medyan çökük: bağıran başlık + uzun süre = yanlış ikili).
3. **planetfall/AVA kurgu-evren bölümleri 0 izlenme sırasında.** Canlı raporda son planetfall
   bölümleri 0-77 bandı (676'lık LUMINOS aykırı değer). Kurgu gezegen ismi ilk karede hiçbir
   şey vaat etmiyor; gerçek isimler (Mars, Neptün, Güneş) kendi merakını taşıyor.
4. **#15 Konu Kaşifi CANLI ve kart üretiyor ama kartlar hiçbir yere akmıyor.** Tek dış-sinyal
   kaynağımız boşa çalışıyor.

## 2. Aktarılan meta dersleri (Sentinal araştırması 2026-07-24; dört kanalda geçerli)

- **İlk kare = thumbnail:** gerçek gök cismi + uç iddia ilk karede okunmalı.
- **Loop en güçlü sinyal:** kapanış jesti/kartı yasak; son kompozisyon başa rimlenir.
- **Taze yükleme kayırılıyor:** düzenli üretim şart; 25 bölüm sabır penceresi.
- **Politika:** onay modu + gerçek varyasyon + AI disclosure; kürasyonlu günde 1 tavan.
- **Ses ürünün yarısı:** huşu tonu kanalın kimliği; ama 18 sn'de tempo sarkamaz.

## 3. KONSEPT: "EVENT HORIZON", gerçek evrenin en uç 18 saniyesi

**Konumlandırma:** Her bölüm, GERÇEK astronomiden tek zihin-büken ve doğrulanabilir faktı
12-24 saniyede gösterir: gerçek gök cismi, gerçek sayı, uç görsel. Kanal vaadi:
**"Evren kurgudan daha tuhaf; her gün tek kanıtlı şok."**

**Formül:** gerçek fakt + ilk karede gök cismi ve iddia + üç çekim + huşu anlatımı + loop.

### 3.1 İmza format, ÜÇ ÇEKİM (3 × 6 sn = ~18 sn)

| Çekim | Adı | Kural |
|-------|-----|-------|
| 1 | **ŞOK** | Soğuk açılış: gök cismi en dramatik halinde, iddia anlatımın ilk cümlesinde. Yıldız alanında yavaş süzülme, logo, "welcome to space" kurulumu YASAK. |
| 2 | **ÖLÇEK** | Faktı hissettiren karşılaştırma/yakınlaşma: Dünya yanına konur, sayı görselleşir, kamera imkânsız mesafeyi kat eder. Bölümün en paylaşılabilir karesi genelde budur (hook_shot). |
| 3 | **UÇURUM** | Faktın sonucu/uç noktası; kompozisyon çekim 1'e rimlenerek döner, hareket sürerken biter (loop dikişi). Kapanış kartı YASAK. |

`hook_teaser` KAPALI: 1,2 sn'lik teaser videonun gerçek ilk karesini işgal eder ve çekim 3'ün
çekim 1'e rimlenen loop dikişini bozar (Codex bulgusu, turu 1). Soğuk açılış zaten kancadır.

### 3.2 Fakt ailesi rotasyonu (top-12 kanıtından; aynı aile üst üste iki bölümde kullanılmaz)

1. **Güneş sistemi uçları**, komşu gezegenlerin absürt gerçekleri ("Olympus Mons" 4.777,
   "Neptune: Diamond Rain" 1.389).
2. **Kozmik kader**, evrenin ve Dünya'nın sonu ("Earth's Fiery End" 1.708, "The Universe is
   Tearing Itself Apart!" 1.672).
3. **Derin uzay canavarları**, kara delikler, boşluklar, aşırı cisimler ("Boötes Void" 1.557).
4. **Cehennem gezegenler**, gerçek ötegezegen uçları ("KELT-9b's INFERNO" 1.384).
5. **Ölçek şoku**, kavranamaz büyüklük/zaman kıyasları ("13.8 Billion Years in 60 Seconds" 1.713).
6. **Bilim temelli what-if**, gerçek fizikten türetilmiş tek senaryo ("What if Earth Had
   Rings?" 1.505). KURAL: ölçülü ton; Mayıs'ın ALL-CAPS bağıran başlık + 30 sn+ süre ikilisi
   YASAK (medyanı 24x düşüren oydu). Ayda en fazla 6-7 bölüm bu aileden.

**Doğruluk kuralı (pazarlıksız):** fakt gerçek astronomi/astrofizikten, yaygın kaynakla
doğrulanabilir; sayılar brief'ten/karttan kopyalanır, UYDURULMAZ. What-if ailesinde bile
fizik gerçek kalır (senaryo spekülatif, mekanik değil).
**Konu havuzu kuralı:** bölüm konuları YALNIZ doğrulanmış tohum havuzundan seçilir. Havuzun
NORMATİF kaynağı §7 listesi, TEKNİK tek kaynağı series.json `topic_pool` alanıdır (id +
topic + family; prompt'a runtime enjekte edilir, brief'e kopyalanmaz). Doğrulayıcı KOD
tarafında: bilinmeyen/kullanılmış seed_id RED, aile-tohum eşleşmezliği RED, havuz tükenince
üretim Gemini'ye gitmeden DURUR (fail-closed). İhsan'ın onayladığı #15 kartları havuza ELLE
eklenir; prosedür: kart ÖNCE §7 listesine girer, SONRA topic_pool + doctrine_sha256 pin
birlikte güncellenir (otomatik kart akışı FAZ 4'te). Gemini'nin kendi fakt icat etmesi
yasaktır; Telegram onayı ikinci kalkan olarak kalır.

### 3.3 Konu kaynağı: #15 Konu Kaşifi köprüsü

- Hedef akış (FAZ 4'te otomatikleşir): #15 kartı → İhsan onayı (kaynak linki ZORUNLU) →
  calibrate köprüsü → replenish brief'ine yapılandırılmış konu (title/core/beats).
- Köprü kurulana kadar: brief'teki tohum listesi + elle eklenen kart konuları. Kart konusu
  her zaman tohum listeden ÖNCELİKLİDİR (dış sinyal > iç varsayım).

### 3.4 Yorum-yemi mühendisliği

- **Uzman tuzağı:** bölümde bilerek TEK hafif eksik bırakılan nüans (ör. "Saturn yüzer" faktında
  "hangi okyanusa sığar" sorusunu açık bırakmak); astronomi meraklısı düzeltmeden duramaz.
- **Ölçek tartışması:** "bunu kavrayabilen var mı?" hissi; bölüm başına en fazla bir yarım-soru.
- Dini/komplocu tartışma kışkırtması YASAK (düz astronomi kanalı; #34 itibar radarı izliyor).

### 3.5 Ses

- Register `galactic_experiment` (Charon) kalır; talimat 18 sn temposuna güncellenir: huşu ve
  sıcaklık kalır, "dramatic pauses" tek kısa duraklamaya iner (çekim 2'deki ölçek anı).
- Metin 30-44 kelime; ilk cümle = iddia; son cümle yarım bırakılıp başa bağlanır (loop'un ses
  ayağı). Selamlama, CTA, "did you know" YASAK.

### 3.6 Paketleme

- **Başlık kalıpları (4 sabit, top-12'den):**
  1. `<Subject>: <striking epithet>` (ör. "Mars' Sleeping Giant: Olympus Mons")
  2. `The Universe's <superlative>: <X>`
  3. `<Subject>: <impossible fact stated flat>`
  4. `What If <X>? <consequence>` (yalnız what-if ailesi; ALL-CAPS kelime EN FAZLA bir tane)
- **Hashtag 4 tane:** `#shorts #space #astronomy #universe`
- AI disclosure HER videoda açık. Watermark'sız tek master, Upload-Post ile üç platforma.
- **Güvenlik:** korku estetiği ve epilepsi riski yaratan hızlı flaş dizileri YOK; ton huşu,
  dehşet pornosu değil; "hepimiz öleceğiz" çerçevesi yerine "evren bundan büyük" çerçevesi.

## 4. Tempo, platform, kredi

- **YouTube günde 1 (kürasyonlu, approval modu).** TikTok + IG Reels aynı master.
- 3 çekim × 6 sn + QC ≈ tahmini **300-450 kredi/bölüm** (İLK gerçek koşu logundan doğrulanır).
  ⚠️ KIE_API_KEY ortak havuz; hat açma kararı S8 bütçesine bağlı.

## 5. Ölçüm ve gate'ler (analytics_data verisiyle, haftalık)

| Metrik | Sağlıklı | Alarm | Ölçüm kaynağı |
|--------|----------|-------|---------------|
| İlk ≥48 saat snapshot izlenmesi (bölüm başına; yayının 48. saatinden SONRAKİ ilk günlük snapshot) | Mart bandına tırmanış (600+) | <100 kalıcı → ilk kare/iddia zayıf | analytics_data/daily (seri-bazlı medyan FAZ 4'e kadar MANUEL, published.json eşlemesiyle) |
| Ortalama izlenme yüzdesi (APV) | ≥%85 (18 sn'de) | <%65 → ölçek çekimi sarkıyor | ÖLÇÜLEMEZ API katmanında; YouTube Studio'dan haftalık MANUEL bakış |
| APV >%100 (loop/rewatch VEKİLİ; doğrudan loop ölçümü değildir) | >%100 hedef | kapanış kartı sızmış mı denetle | ÖLÇÜLEMEZ; Studio'dan MANUEL |

- **Kill gate:** 25 bölüm sonunda medyan <400 VE tavan <4K → aile ağırlıkları değişir (kanal
  ve format iskeleti KALIR; 1.085'lik Mart medyanı hedeftir). Seri-bazlı medyan published.json
  eşlemesiyle hesaplanır (FAZ 4'te otomatikleşir, o güne dek manuel).
- **Double-down:** video >5K → aynı aileden 3 varyant öne; >50K → o aile haftada 3-4 bölüm
  (aile etiketi plan `family` alanından; FAZ 4 köprüsüne kadar manuel değerlendirme).
- Göreli eşikler FAZ 4 calibration.json'a bağlanır; 48h metrikleri ~14 gün ısınmada.

## 6. planetfall kill-gate ÖNERİSİ (İhsan kararı)

planetfall 25 bölüm penceresini fiilen doldurdu (24-25 yayın) ve son bölümler 0-77 bandında:
kill-gate koşulu sağlandı. **Öneri: planetfall EMEKLİ: `status: paused` + `auto_replenish.enabled:
false` (dosyalar git'te kalır). DİKKAT motor gerçeği: completed + replenish-açık seri bir
sonraki koşuda kendiliğinden DİRİLTİLİR; emeklilik bu yüzden paused + kapalı replenish ile
yazılır (Codex bulgusu, turu 1). ava-voyage zaten completed ve replenish'siz.** Kurgu-evren
mekaniği bu kanalda kanıt karşıtı;
"kanalı değil mekaniği değiştir" ilkesi uygulanır. Her iki seri klasörü `series_data/`'dan
`galactic_experience/` altına `git mv` ile taşınır (KANAL_KLASORLERI.md'deki bekleyen iş;
motor iki konumu da tanıdığı için kod değişikliği gerekmez).

## 7. Tohum bölüm fikirleri (doğrulanmış faktlar, İngilizce)

1. A day on Venus is longer than its year. (güneş sistemi uçları)
2. A sugar-cube of neutron star matter would weigh about as much as Mount Everest. (derin uzay canavarları)
3. Saturn is less dense than water; given a big enough ocean, it would float. (güneş sistemi uçları)
4. The Sun is about 400 times wider than the Moon and about 400 times farther away: the eclipse coincidence. (ölçek şoku)
5. TON 618: a black hole weighing tens of billions of Suns, recent estimates near 40 billion. (derin uzay canavarları)
6. Jupiter's Great Red Spot, a storm bigger than Earth, has been shrinking for 150 years. (güneş sistemi uçları)
7. There are more trees on Earth than stars in the Milky Way. (ölçek şoku)
8. NASA detected pressure waves from a black hole and sonified them: B-flat, 57 octaves below middle C. (derin uzay canavarları)
9. On average, Mercury is the closest planet to every other planet. (ölçek şoku)
10. The light of the galactic center you see tonight left during the last Ice Age. (ölçek şoku)
11. HD 189733 b: a deep-blue world where winds hit 8,700 km/h and it likely rains molten glass sideways. (cehennem gezegenler)
12. What if the Moon vanished tonight? Lunar tides disappear, weaker solar tides remain, and Earth's tilt slowly destabilizes. (bilim temelli what-if)

## 8. UYGULAMA (İhsan onayı sonrası)

**Yeni seri:** `galactic_experience/event-horizon/`
- series.json: `slug: event-horizon`, `base_title: Galactic Experiments`, `standalone: true`,
  `upload_profile: galacticexperimet`, `publish_mode: approval`, `status: active`,
  `priority: 999`, `total_parts: 0`, `next_part: 1` (ilk replenish part 1'den başlasın),
  platformlar youtube+instagram+tiktok, hashtag §3.6.
- auto_replenish: `{enabled: true, batch: 5, min_queue: 2, shots: 3, shot_seconds: "6",
  music_prompt: true, narration: {min_words: 30, max_words: 44}}` (bütçe doğrulayıcıda
  BİREBİR uygulanır)
  + `families`: ["güneş sistemi uçları", "kozmik kader", "derin uzay canavarları",
  "cehennem gezegenler", "ölçek şoku", "bilim temelli what-if"] (kanonik enum; doğrulayıcı
  dışını RED eder, ardışık aynı aile RED)
  + `music_style` (AYNEN bu İngilizce string): "Awe-driven cosmic underscore with a steady
  forward pulse; one brief swell at the scale moment; no glacial ambient intro, no gentle
  outro; end mid-phrase so the loop is seamless."
  + `topic_pool`: §7'deki 12 tohum `{id, topic, family}` yapısında (id = liste numarası;
  konular prompt'a runtime enjekte edilir, brief'e kopyalanmaz)
  + §3 kurallarını anlatan Türkçe brief (çıktı dili İngilizce; her partta `family` ve
  `seed_id` zorunlu; konu yalnız enjekte edilen havuzdan) + §3.6 title_style.
- series.json'a `doctrine_sha256` pin'i yazılır (bu dosyanın SHA-256'sı; doktrin revize
  edilince topic_pool ve brief'le birlikte güncellenir, eşleşmezse üretim fail-closed
  durur). Replenish her plan part'ına aynı hash'i damgalar; doktrin değişirse eski damgalı
  bekleyen planlar produce'da durur ve yeniden üretilir.
- bible.json: art_style = fotoreal astronomi sineması (gerçek gök cisimleri, NASA-görsel
  gerçekçiliği, 9:16); series bloğunda `hook_teaser: {enabled: false}` (§3.1); qc notu =
  gerçek cisim adı + tek fakt + kapanış kartı yasağı; `narration.channel: galactic_experiment`.
- `core/narration.py` galactic_experiment talimatı §3.5'e göre güncellenir (ses Charon kalır).
- **planetfall:** `status: paused` + `auto_replenish.enabled: false` + `doctrine:
  "galactic_experience/KONSEPT.md"` alanı; **ava-voyage:** `doctrine:
  "galactic_experience/KONSEPT.md"` alanı (üretim/legacy koşular doktrin kapısından geçebilsin).
- **git mv:** planetfall + ava-voyage → `galactic_experience/` (§6; İhsan'ın 2026-07-18 kararı).

**Cron AÇILMAZ:** hat açma ayrı İhsan kararı (S8 bütçe + 4 kayıt kuralı).

**Hat açma ön koşulu:** konu havuzu ≥25 doğrulanmış konuya çıkarılır (12 tohum 25 bölüm
penceresini dolduramaz; onay sonrası ek tohum turu + onaylı #15 kartları havuza eklenir).

**İhsan kararları:** (1) bu doktrinin onayı, (2) planetfall emekliliği (§6), (3) hattı açma +
kredi bütçesi payı.
