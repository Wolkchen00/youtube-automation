# SENTINAL IHSAN DAILY ,  KANAL KONSEPT DOKTRİNİ v2.1
**Tarih:** 2026-07-24 · **Karar sahibi:** İhsan · **Statü:** UYGULAMAYA HAZIR (push bekliyor)
**v2.1 (aynı gün, İhsan yönergesi):** sessiz format → GÜNDELİK VLOG VOICEOVER. Gerekçe: steril
sessizlik "AI hissi" veriyor, izleyici mesafeleniyor; gerçek video hissi = akıcı doğal konuşma.

---

## ⚡ v3 FAZ-1 YÜRÜRLÜKTE (2026-08-09, İhsan onayı) ,  aşağıdaki v2.1 metnini EZER

Referans kanal @silent_builder_official ölçüldü; tam analiz ve fazlı plan: `KONSEPT_v3_TASLAK.md`
(o dosya taslaktır, YALNIZ aşağıdaki maddeler uygulandı). Bu bölüm v2.1 ile çeliştiği her yerde
kazanır; çelişmediği her v2.1 kuralı aynen yürürlüktedir.

1. **ÖN KAMERA POV İPTAL.** "%90 gerçek telefon görüntüsü", "iPhone'la kol mesafesinden",
   "front-camera POV" ifadelerinin tamamı doktrinden düştü. Ölçüm: `qc_log.jsonl`'daki 51 red
   gerekçesinin 23'ü "prompt'un yasakladığı öğe görünüyor" ve issue metinleri birebir
   "Phone visible in frame" diyor ,  prompt modele telefon çizdiriyordu.
2. **BAKIŞ AÇISI KİLİTLİ.** Bakış çekim boyunca tek ve değişmez konum/açıda kalır; kadrajda
   hareket eden tek şey eller ve objedir. Dört çekimin dördü de AYNI mekân, AYNI yüzey, AYNI ışık.
3. **PROMPT'A EKİPMAN ADI YAZILMAZ.** `tripod`, `camera`, `static shot`, `locked camera`,
   `camera A`, `slate`, `phone`, `iPhone`, `selfie`, `front-camera` sahneye nesne ya da yazı
   olarak sızıyor. Kamera davranışla tarif edilir. (AImagine'de aynı ders KN-5 olarak alındı.)
4. **YASAK BÖLGE yeniden yazıldı.** Dönüşümün hedefi serbest; onu mümkün kılan MEKANİZMA gerçek
   bir teknik olamaz. İkinci turnusol eklendi: "bunu ben de yapabilir miyim?" cevabı EVET ise ÇÖP.
   Bu kural brief'e aittir, çekim prompt'una yasak listesi olarak YAZILMAZ.
5. **Anlatım bütçesi 32-45 → 20-28 kelime.** Sessizlik formatın parçası.
6. **QC:** `frames` 8→12, `artifact_threshold` 6→7, `max_regens_per_episode` 6.
   `qc.notes` baştan yazıldı ve en başına SERIES EXEMPTION eklendi: tek senaryolu fizik ihlali
   ve malzemenin ona bağlı biçim değiştirmesi `artifact_score`'u ASLA yükseltmez.
7. **`hook_teaser` kapatıldı.** `art_style` telefon kurgusundan arındırıldı.
8. **`families` ve `music_style` motora verildi;** aile rotasyonu artık ölçülebilir.
9. **DEĞİŞMEYENLER:** dört çekim ANOMALİ→PROBE→ESCALATION→LOOP, loop dikişi ve kapanış jesti
   yasağı, tek imkânsızlık kuralı, karakter ve siyah tişört, uzman tuzağı, `publish_mode: auto`,
   günde 1 bölüm. **3 çekim x 8 sn, zincirli geçiş ve REVEAL finali FAZ-2'dir, HENÜZ UYGULANMADI.**

**Bu kanala persona/prompt/yorum yazan otomasyonlar (#6, #15, #16, #34) bu bölümü de okumalıdır.**

---

> SEÇENEK A (absürt obje/deney, İhsan kararı 2026-07-20) temel alınır; bu doküman o kararın
> "milyon izlenme sınıfına" yükseltilmiş halidir. Bu kanala persona/doktrin yazan HER otomasyon
> (#6 yorum cevabı, #15 script, #16 tartışma yorumu, #34 itibar) bu dosyayı referans alır.

---

## 1. Neden 146 video başarısız oldu (teşhis)

Kanal ölçümü (YouTube API, 2026-07-18): 146 video · 99.227 izlenme · 113 abone · 53 yorum.

1. **Ödül sonda.** Hayatta-kalma formatı (47-53 sn, anlatımlı) izleyiciden 50 saniyelik yatırım
   istedi → 4-71 izlenme, ~100x çöküş. Shorts feed'inde tıklama kararı yok; ilk 1 saniye
   thumbnail'in kendisidir.
2. **Absürtlük eşiği çok düşük.** Eski absürt-obje formatı (medyan 788, tavan 3.355) %100
   MAKUL işlemler gösterdi: köpük kaplama, boya daldırma, kendini temizleyen şişe. Bunlar
   "ilginç DIY"dır, "gerçeklik kırılması" değildir. 2026 metasında kazanan klip = **%90 gerçek
   görüntü + TEK imkânsız öğe** (cam çilek, olimpik atlayan kedi). Tamamen makul de, tamamen
   çizgi-film de kaybediyor; kazanan bu ikisinin arasındaki dar bant.
3. **Loop, ses ve yorum motoru yok.** Mart 2025'ten beri her loop yeni izlenme sayılıyor ve
   %100+ retention en güçlü sinyal; eski videolarda "sunum jesti + kapanış" loop'u öldürüyordu.
   Ses ürünün yarısı (Veo-3 senkron sesi glass-fruit patlamasını başlattı); bizim hat müzik-only.
   Yorum tetiği tasarlanmamıştı → 146 videoda 53 yorum.

## 2. Araştırma özeti (2026-07-24, üç paralel ajan)

- **Algoritma:** Her Short kanal geçmişinden bağımsız kendi seed testini alır (YouTube + TikTok
  resmi). 146 videoluk zayıf geçmiş yeni videoları CEZALANDIRMAZ; pivot yerinde yapılabilir.
  Eşikler (pratisyen tahminleri): viewed-vs-swiped ≥%70 viral bölge, ilk 3 sn'de %80+ tutma,
  loop >%100 en güçlü sinyal. Eylül 2025'ten beri ~30 günden taze yüklemeler kayırılıyor →
  günlük üretim şart. IG tarafında sıralama: watch time + **sends** (DM paylaşımı); Trial Reels
  ile takipçi yakmadan format testi yapılabilir. Thumbnail feed'de yok; **ilk kare = thumbnail**.
- **Meta:** 2025-26'nın patlayan AI formatlarının ortak formülü: (a) yeni model yeteneğine ilk
  binen kazanır (pencere 4-8 hafta), (b) **karakter/evren sahibi hesap, anonim klip çöplüğünü
  yener** (Bigfoot vlog: 0→330K takipçi/1 ay; brainrot karakter roster'ları), (c) kırılma tipik
  olarak ilk 20-25 videoda gelir ya da o mekanikte hiç gelmez → **kanalı değil mekaniği değiştir**,
  (d) ses tasarımı ve retention mimarisi üretim kalitesinden önemli.
- **Politika (kritik):** Temmuz 2025 "inauthentic content" YPP kuralı + Ocak 2026 slop temizliği
  (4.2M abonelik Super Cat League dahil 16 kanal silindi). Tam-otomatik üret→yükle hattı en
  riskli arketip. Bizi koruyan: onay modu (insan kürasyonu), tek tanınabilir karakter (Ihsan),
  bölümler arası gerçek varyasyon, AI disclosure etiketi. YouTube'da 1/gün kürasyonlu tavan;
  hacim artışı TikTok/Reels tarafında yapılır.
- **Beklenti matematiği (dürüst):** ~1M izlenme ≈ 500-5.000 abone; yani "binlerce abone" ve
  "milyonlarca izlenme" AYNI olayın iki yüzü = en az 1-2 gerçek viral hit. Medyan senaryo
  (günde 1-3 video, 4-6 hafta): on binlerce izlenme. Bu doktrin garantiyi değil, şans yüzeyini
  büyütür: doğru ilk kare × loop × tırmanış × hacim × 25-video sabır penceresi × mekanik rotasyonu.

## 3. KONSEPT: "UNNATURAL" ,  gerçekliği kıran sakin adam

**Konumlandırma:** Ihsan (27), telefon kamerasıyla çekilmiş gibi görünen mutfak/garaj/atölye
görüntülerinde, fizik kurallarına uymayan SIRADAN objeler bulur ve onları sakin, meraklı,
hiç şaşırmayan bir yüzle "test eder". Kamerada dudakları hiç kıpırdamaz; sesi görüntünün
üzerinde arkadaşına anlatır gibi konuşur ve imkânsızlığı ASLA açıklamaz. Kanal vaadi:
**"Her gün, gerçekliğin çatladığı 24 saniye."**

**Formül:** %90 gerçek telefon görüntüsü + TEK imkânsız özellik + bölüm içi tırmanış + görünmez loop dikişi.

Karakter kalır (politika kalkanı + abone kancası + slop'tan farklılaşma). Seri slug'ı
`unnatural-lab` kalır; başlık "Unnatural Lab" kalır.

### 3.1 İmza format ,  DÖRT ÇEKİM v2 (SETUP→REVEAL öldü, yaşasın ANOMALİ-ÖNCE)

| Çekim | Adı | Kural |
|-------|-----|-------|
| 1 | **ANOMALİ** | Soğuk açılış, eylem ORTASINDAN. İmkânsız obje daha ilk karede tam ışıkta, makro, el temas halinde ve tuhaflık ÇALIŞIR durumda. Hazırlık, malzeme toplama, establishing shot YASAK. İzleyici 0,5 sn'de hem objeyi hem imkânsızlığı okuyabilmeli. |
| 2 | **MÜDAHALE** | Ihsan anomaliyi kışkırtır: keser, sıkar, düşürür, döker, ters çevirir. Anomali doğrulayarak ve büyüyerek cevap verir. Eller net. |
| 3 | **TIRMANIŞ** | İkinci twist ,  çekim 1'den DAHA imkânsız (yayılır, ölçek değiştirir, kendi kendine devam eder). Genellikle hook_shot budur. |
| 4 | **LOOP DİKİŞİ** | Kompozisyon çekim 1'in ilk karesine görsel olarak rimlenerek döner; eylem DEVAM EDERKEN biter. Sunum jesti, işaret etme, kameraya bakıp onay, kapanış beat'i YASAK ,  video hiç bitmiyormuş gibi loop'lanmalı. |

Süre 4×6 sn = ~24 sn sabit (kanal verisi: 14-41 sn bandı kazanıyor; 24 sn loop + monetizasyon dengesi).
`hook_teaser` (1,2 sn doruk önizleme) açık kalır.

### 3.2 Mekanik rotasyonu (eski "malzeme listesi" yerine "imkânsızlık aileleri")

Her bölüm BİR aileden BİR imkânsızlık seçer; aynı aile üst üste iki bölümde kullanılmaz:

1. **İmkânsız malzeme** ,  obje yanlış maddeden (kumaş gibi katlanan tuğla, cam gibi kırılan ekmek)
2. **İmkânsız davranış** ,  obje kendi başına hareket eder (kartondaki yumurtalar top gibi sekmeye başlar)
3. **İmkânsız iç yapı** ,  kesilince yanlış şey çıkar (elmanın içi minik elmalarla dolu)
4. **Ters fizik** ,  yerçekimi/zaman tersine (kalemtıraş talaşları geri sarılıp kalem olur, kahve fincandan yukarı spiral çizer)
5. **İmkânsız hâl değişimi** ,  buz yakar, su ahşap gibi çivi tutar, ekmek sıvı gibi akar sonra tekrar somun olur
6. **İmkânsız süreklilik/ölçek** ,  hiç bitmeyen dökme, katlandıkça büyüyen kağıt
7. **Hafif tekinsiz** ,  gölge objeden ayrı kalır, ayna 3 saniye geç gösterir (gündüz, aydınlık, MERAK tonu; asla korku estetiği)

YASAK bölge: gerçek hayatta mümkün her işlem (köpük genleşmesi, boya/reçine daldırma, beton döküm,
hidrolik pres, mıknatıs sıvısı). Turnusol testi: izleyici "bunu hangi dükkândan almış?" diye
soruyorsa ÇÖP; "fizik buna izin vermez, nasıl yaptı?" diye soruyorsa DOĞRU.

### 3.3 Yorum-yemi mühendisliği (izlenmenin ikinci motoru)

- **Uzman tuzağı (her bölümde 1 adet):** fiziği bilerek HAFİF yanlış bir detay ,  yanlış kırılma
  deseni, imkânsız ölçek oranı, ters yöne damlayan sıvı. Mühendis/kimyacı/fizikçi düzeltmeden
  duramaz ("as an engineer, this is wrong because..."). #16 Reels_Tartisma_Yorumu doktrini
  (meslek ekseni) zaten buna kurulu ,  tohum yorumlar bu tuzağı işaret eder.
- **"Gerçek mi AI mı?" belirsizliği:** görüntü gerçeklik eşiğinde tutulur; yorum bölümünün
  "obviously AI" vs "no way" diye ikiye bölünmesi hedeflenen sonuçtur. Her cevap zinciri sinyaldir.
- **Sayma/bulma oyunu (ara sıra):** sabitlenmiş yorumdan "kaç yumurta gerçekti?" ,  tam yeniden
  izleme + yorum aynı anda.
- Rage-bait YOK (platformlar aktif bastırıyor); belirsizlik ve uzman tuzağı daha uzun ömürlü.

### 3.4 Ses v2.1 ,  GÜNDELİK VLOG VOICEOVER (İhsan yönergesi, 2026-07-24)

Steril sessizlik "AI hissi" verir ve izleyiciyi mesafelendirir; 2025'in en hızlı patlaması
(Bigfoot vlog'ları) akıcı KONUŞAN selfie-vlog'lardı. Ama kötü dudak senkronu "bu AI" hissini
en hızlı veren şeydir. Çözüm ikisini birden alır:

- **Kamerada dudak KAPALI** (lip-sync riski sıfır, QC kuralı aynen duruyor) + **üstüne Ihsan'ın
  kendi sesiyle birinci-şahıs gündelik voiceover** ,  TikTok/vlog'un en doğal konvansiyonu.
- **Ses = Algieba** (marka sesi tek; influencer personasıyla aynı), yeni register:
  `sentinal_vlog` (core/narration.py) ,  "arkadaşına anlatan adam": rahat, akıcı, hafif
  eğlenmiş; ufak duraksamalar, yarım gülme, 'okay so...' doğallığı. Sunucu/belgesel/ASMR
  tonu ve fısıltı YASAK.
- **Metin kuralları (brief'te):** 32-45 kelime (24 sn'de rahat konuşma temposu); imkânsızlığı
  asla açıklamaz/adlandırmaz, ekranda görüneni betimlemez ,  bağlam ve tepki verir ("üç gündür
  böyle", "ev sahibi görse öldürür"); selamlama ve CTA yasak; cümle ortasından başlar, sonu
  başa bağlanır (loop'un ses ayağı); bölüm başına en fazla bir yarım-soru yorum-yemi.
- **Ekran-ses uyumu (3 katman):** (1) İçerik: anlatım çekimlerle AYNI Gemini planında tek
  seferde yazılır ve vuruş sırası çekim sırasını izler ,  ilk cümle anomaliye (shot 1-2), orta
  vuruş tırmanışa (shot 3), kapanış yarım cümlesi loop anına (shot 4); ekranda henüz olmamış
  şeye atıf yasak. (2) Süre: mikser (`ffmpeg_tools.mix_voiceover`) TTS videodan uzunsa
  otomatik hızlandırıp sığdırır (tavan 1.15x; üstünde log uyarısı). (3) İnsan kapısı: Telegram
  onay önizlemesi sesli izlenir ,  uyumsuz bölüm reddedilir, yerine yenisi yazılır.
- **Müzik alt yatağa iner:** anlatımın altında kısık ve perküsif, konuşmayı bastırmaz;
  yavaş/ethereal açılış yine yasak.

Faz-2 motor yükseltmesi olarak sırada: **diegetik/dokunsal foley** (temas, çatlama, akma
sesleri) ,  voiceover'ın altına gerçek dünya sesi eklemek türün dopaminini tamamlar.

### 3.5 Paketleme

- **Başlık kalıpları (3 sabit):**
  1. `I Found UNNATURAL <objects>... And They STARTED To <action>!`
  2. `This <object> Is NOT Supposed To <action>?!`
  3. `Can I Turn A <object> Into A <impossible thing>?!`
- **Hashtag 4 taneye iner:** `#shorts #oddlysatisfying #experiment #isitreal` (hashtag sınıflandırma
  içindir, viral etkisi minör; 3-5 üstü zarar).
- **AI disclosure etiketi HER videoda açık** (YouTube Studio kanal varsayılanını kontrol et , 
  DEVAM-NOTU'nda zaten manuel iş olarak kayıtlı). Gizlemek bağımsız ihlaldir.
- Watermark'sız tek temiz master → Upload-Post ile üç platforma native (mevcut akış doğru).

## 4. Tempo, platform, kredi

- **YouTube: günde 1** (kürasyonlu; 3+/gün aynı-şablon YT'de artık başlı başına demonetizasyon
  deseni). **TikTok + IG Reels: aynı master'la başla; sinyal gelirse ayrı kısa kesimlerle 2-3/güne
  çık** (hacim artışı bu iki platformda güvenli). IG'de 1.000+ takipçi olunca **Trial Reels** aç.
- Kırılma penceresi: **25 bölüm** (~3,5 hafta). Bu süre dolmadan format hakkında hüküm verme.
- Kredi: room-408 6×8 sn ≈ 670-900 kredi/bölümdü; unnatural-lab 4×6 sn + QC tahminen
  ~400-600 kredi/bölüm (İLK gerçek koşunun logundan doğrula: Actions artifact
  `unnatural-lab-logs-*` ya da `python -m series.cli credit`). Günde 1 bölüm ≈ ayda
  ~15-18K kredi ,  bakiye planı buna göre. ⚠️ KIE_API_KEY 5 projeyle ORTAK havuz.

## 5. Ölçüm ve gate'ler (ölç-ele protokolü)

Haftalık (pazartesi, `analytics.yml` verisiyle):

| Metrik | Sağlıklı | Alarm |
|--------|----------|-------|
| YT viewed-vs-swiped | ≥%70 | <%50 → ilk kare zayıf, ANOMALİ kuralını denetle |
| Ortalama izlenme yüzdesi | ≥%90 (24 sn'de) | <%70 → orta bölüm sarkıyor, TIRMANIŞ zayıf |
| Loop oranı | >%100 hedef | sunum jesti sızmış mı kontrol et |
| İlk 48 saat izlenme | kanal bazlı takip | medyan trendine bak, tekil videoya değil |

- **Kill gate:** 25 bölüm sonunda medyan <2K VE tavan <20K → mekanik ailesi ağırlıklarını değiştir
  (kanal ve karakter KALIR). 
- **Double-down protokolü:** herhangi bir video >100K → aynı imkânsızlık ailesinden 3 varyantı
  öne çek; >1M → o aile haftada 3-4 bölüme çıkar.
- **Eski videolar:** 12 hayatta-kalma/tarihsel video için öneri = UNLIST (temiz pivot; framework
  önerisi). Eski absürt videolar kalabilir. → İhsan kararı, geri alınabilir.
- `publish_mode: approval` format kanıtlanana kadar kalır (politika kalkanı); sonra `auto`.

## 6. Referans hesap anatomisi (ferdolans / mrberk0)

> Ajan raporu beklemede ,  rapor gelince bu bölüm doldurulacak. Ana strateji yukarıdaki
> bulgulara dayanır ve bu bölümden bağımsız uygulanabilir.

## 7. Tohum bölüm fikirleri (doğru kalibrasyon örnekleri, İngilizce)

1. Eggs in a carton start bouncing like superballs ,  each bounce higher than the last.
2. A loaf of bread pours like thick liquid when tilted, then sets back into a loaf.
3. An ice cube lights a match on contact, steaming cold the whole time.
4. A rock cracked open leaks golden liquid that flows UP the hammer handle.
5. A banana unzips like a jacket zipper, perfectly clean inside.
6. A newspaper folded once knocks like solid oak; folded again, it's a plank.
7. Honey poured on a plate assembles itself into a perfect honeycomb.
8. Nails hammered into a bowl of water stand fixed in the surface like it's wood.
9. A soccer ball deflates into silk; he folds it like a shirt and pockets it.
10. Pencil shavings spiral backwards and reassemble into a sharpened pencil.
11. Tomatoes rolled across the counter sort themselves by size, largest first.
12. An apple bitten open is full of dozens of tiny perfect apples.
13. A rubber band stretched keeps growing into a rope, then coils itself neatly.
14. Coffee spirals up out of the cup, back into the pot, cup dries itself.
15. A brick floats in a bucket of water while the sponge next to it sinks.
16. He peels the shadow off a chair and folds it; the chair stands shadowless.
17. A mirror shows the room three seconds late ,  he waves, waits, the reflection waves.
18. A puddle has a zipper; unzipped, the ground underneath is dry carpet.
19. A candle burns steadily at the bottom of a full fish tank.
20. Folding a paper napkin makes it larger each fold until it covers the table.

## 8. UYGULAMA DURUMU

**Bu oturumda yapıldı (lokal, push bekliyor):**
- `unnatural-lab/series.json`: brief v2 (ANOMALİ-önce akış + imkânsızlık aileleri + uzman tuzağı
  + loop dikişi + müzik kuralı), title_style v2, hashtags v2, `total_parts: 1` (eski 5 plan
  emekli edildi → bir sonraki cron'da Gemini yeni brief'le kredisiz taze plan yazar)
- `unnatural-lab/plans/part02..05.json` silindi (git geçmişinde duruyor, geri alınabilir)
- `unnatural-lab/bible.json`: art_style'a tek-imkânsızlık kuralı, qc notlarına loop-dikişi denetimi
- **v2.1 ses katmanı:** `core/narration.py`'ye `sentinal_vlog` ses profili (Algieba, gündelik
  vlog registeri); `bible.json` → `narration.channel: sentinal_vlog`; `series.json` →
  `narration: {min_words: 35, max_words: 50}` + brief kural (1) vlog-voiceover, kural (11)
  müzik alt-yatak

**İhsan'ın kararları / işleri:**
1. **Push onayı** ,  bu değişiklikler push edilmeden cron eski brief'le devam eder. (Üretim şu an
   zaten ep01 onayına kilitli, acele kredi riski yok.)
2. **Telegram #290 (ep01 "UNNATURAL FOAM"):** eski kalibrasyonla üretildi (%100 makul köpük =
   yasak bölge). Öneri: REDDET, kanal yeni doktrinle açılsın; kredisi zaten harcandı (sunk cost).
   İzleyip görsel olarak çok güçlü buluyorsan yayınla ,  algoritmik zararı yok, sadece veri noktası.
3. 12 hayatta-kalma/tarihsel videoyu unlist etme kararı.
4. YouTube Studio AI disclosure kanal varsayılanı kontrolü.
5. Kie kredi bütçesi: günde 1 bölüm ≈ ayda ~15-18K kredi tahmini ,  bakiyeyi planla.
