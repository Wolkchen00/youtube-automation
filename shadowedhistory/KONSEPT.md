# SHAD0WED HISTORY, KANAL KONSEPT DOKTRİNİ v1.6
**Tarih:** 2026-07-29 · **Karar sahibi:** İhsan · **Statü:** TASLAK (İhsan onayı bekliyor)
**v1.1 (aynı gün, Codex Same Page turu 1):** zaman çıpası BCE/çağ biçimlerini kapsar; caption
ve fact_captions kaldırıldı (motor gerçeği); kelime bütçesi doğrulayıcıda birebir uygulanır;
konu havuzu kuralı eklendi; ölçüm tablosu ölçülebilirlik etiketleri aldı; 4 tohum fakt
kaynaklara göre düzeltildi.
**v1.2 (aynı gün, turu 2):** konu havuzu seed_id ile KOD tarafında doğrulanır; aile listesi
kanonik enum oldu ve ardışıklık ihlali RED; güvenlik maddesi eklendi; music_style sabitlendi;
doctrine_sha256 pin'i; hat açma ön koşulu havuz ≥25.
**v1.3 (aynı gün, turu 3):** havuzun teknik tek kaynağı series.json `topic_pool` oldu
(id+topic+family; brief'e kopyalanmaz, prompt'a runtime enjekte edilir); plan damgası eklendi
(doktrin revizyonu bekleyen planları geçersizleştirir); havuz genişletme prosedürü netleşti.
**v1.4 (aynı gün, Level 10):** çekim süresi 7 sn → 6 sn (Kie gemini-omni-video resmi şeması
duration'ı 4/6/8/10 enum'una kilitliyor, 7 YOK; bölüm ~12 sn oldu); anlatım bütçesi 20-30
kelimeye indi.
**v1.5 (aynı gün, canlı replenish kanıtı):** çağ çıpası BCE/CE biçimlerini de kapsar (Gemini
doğal olarak "69 BCE" yazar; canlı koşu BC/AD-tek regex'inde fail-closed düştü, doğrulayıcı
genişletildi).
**v1.6 (aynı gün, canlı replenish kanıtı 2):** bölüm 2 x 8 sn = ~16 sn oldu (kanıt bandı
10-16'nın üst ucu) ve anlatım bütçesi 26-38 kelimeye çıktı: Gemini tarih faktı anlatımını
doğal olarak söylenen aralığın %10-20 üstünde yazıyor ve hedefi kovalamak çözüm değil. Nihai
kural: hedef aralık prompt'ta aynen; doğrulayıcı MİKSÖR PAYIYLA kabul eder (min×0.85 ..
max×1.15; TTS miksörü 1.15x hızlandırmayı zaten karşılar, ölçüsüz eski 0.7-1.35 toleransı
geri gelmedi).
**Kanal:** `UCUdp0KLBh4EeeSgVbwS_DhA` · @shad0wedhistory357 · upload_profile: `shad0wedhistory` · narration register: `shadowedhistory`

> S4 kararı (2026-07-27): 10-16 sn tekil tarih-faktı formatına dönüş. Bu doküman o kararın
> uygulanabilir doktrinidir. Bu kanala persona/prompt yazan HER otomasyon bu dosyayı referans
> alır; doktrin TEK KAYNAKTIR, metni başka kanala kopyalanmaz (çapraz bulaşma kuralı,
> KANAL_ENTEGRASYON_PLANI_v2 FAZ 3). Üretim koşuları bu dosyanın SHA-256'sını loglar.

---

## 1. Teşhis: kanal kendi A/B testini yaptı, kazanan belli

Ölçüm (FAZ 0 röntgeni 2026-07-27 + canlı FAZ 2 snapshot 2026-07-29): 245 video, 107.277
izlenme, 123 abone, 30 günlük medyan 77,5.

1. **Ocak-Mart 10-16 sn TEKİL FAKT dönemi kazandı:** medyan 706-866; kanalın en iyi 10
   videosunun 6'sı bu dönemden. Canlı snapshot doğruluyor: "How Ships Crossed Land in 1453!"
   1.666, "Forging a Samurai Katana!" 1.652, "The Real Reason Pirates Wore Eye Patches" 1.493,
   "Persian Immortals: Army of Illusion?" 1.413, "Hanging Gardens: Fact or Ancient Propaganda?"
   1.300.
2. **Nisan'daki 30 sn+ anlatılı seriye kayış kaybetti:** hacim 2x artarken medyan 5x düştü.
3. **Temmuz footnotes/drowned bölümleri 0 izlenme sırasında.** Canlı raporda son bölümler
   27-79 bandında. Tek istisna 755 izlenmeli "Western Front, 1914" (Noel ateşkesi = herkesin
   bildiği hikaye; formatı değil konuyu ödüllendiren aykırı değer).
4. Ders Sentinal teşhisiyle aynı: ödül sonda olamaz; 33-47 sn'lik sessiz sinema izleyiciden
   yarım dakikalık yatırım istiyor, Shorts feed'i bunu vermiyor.

## 2. Aktarılan meta dersleri (Sentinal araştırması 2026-07-24; dört kanalda geçerli)

- **İlk kare = thumbnail.** Feed'de tıklama kararı yok; izleyici 0,5 sn'de konuyu okumalı.
- **Loop en güçlü sinyal.** Video biterken kapanış jesti yasak; sonu başa bağlanır.
- **Taze yükleme kayırılıyor** (~30 gün penceresi): düzenli üretim şart.
- **Politika:** tam-otomatik üret-yükle en riskli arketip; onay modu + gerçek varyasyon +
  AI disclosure bizi korur. YouTube'da kürasyonlu günde 1 tavan.
- **Beklenti matematiği:** kırılma tipik ilk 20-25 videoda gelir ya da o mekanikte hiç gelmez;
  25 bölüm dolmadan format hakkında hüküm verilmez.

## 3. KONSEPT: "FLASHPOINTS", 16 saniyede bir tarih çarpması

**Konumlandırma:** Her bölüm, izleyicinin bildiğini sandığı tarihten TEK çarpıcı ve
DOĞRULANABİLİR faktı ~16 saniyede patlatır (kanıt bandı 10-16 sn'nin üst ucu). İddia daha ilk
cümlede ve ilk karede; kanıt/büküm ikinci çekimde. Kanal vaadi: **"Tarih kitabının dipnotu,
feed'in en sert 16 saniyesi."**

**Formül:** gerçek fakt + ilk karede iddia + iki çekim + tek nefes anlatım + loop dikişi.

### 3.1 İmza format, İKİ ÇEKİM (2 × 8 sn = ~16 sn; motor gerçeği: Kie Omni süresi 4/6/8/10
enum'udur, ara değer yoktur)

| Çekim | Adı | Kural |
|-------|-----|-------|
| 1 | **ÇARPMA** | Soğuk açılış, faktın EN görsel anının ortasından. İlk kare tek başına konuyu ve tuhaflığı okutur; establishing shot, harita üzerinde yavaş zoom, atmosfer kurulumu YASAK. Anlatımın ilk cümlesi = başlıktaki iddianın kendisi. |
| 2 | **KANIT/BÜKÜM** | Faktın en tuhaf detayı ya da sonucu; görsel olarak çekim 1'den daha yakın/daha sert. Kompozisyon çekim 1'in ilk karesine rimlenerek döner, eylem sürerken biter (loop dikişi). Kapanış karti, "follow for more" jesti YASAK. |

`hook_teaser` kapalı kalabilir (video zaten 14 sn; teaser toplam süreyi yer).

### 3.2 Fakt ailesi rotasyonu (top-10 kanıtından türetildi; aynı aile üst üste iki bölümde kullanılmaz)

1. **Yanılgı kırıcı**, herkesin bildiği "gerçek" yanlış ("The Real Reason Pirates Wore Eye
   Patches" 1.493). En güçlü yorum motoru.
2. **İmkânsız mühendislik**, "bunu o çağda nasıl yaptılar" ("How Ships Crossed Land in 1453!"
   1.666; "Forging a Samurai Katana!" 1.652).
3. **Tuhaf savaş**, savaşın absürt/ürkütücü detayı ("Assyrian Siege Drum Terror" 1.384;
   "Great Emu War" sınıfı).
4. **Unutulmuş kişi**, tarihin sildiği tek insan ("Ignaz Semmelweis" 1.397).
5. **Efsane vs kayıt**, mit ile belge çatışması ("Hanging Gardens: Fact or Ancient
   Propaganda?" 1.300).
6. **Zaman çarpması**, imkânsız görünen kronoloji (Kleopatra Ay'a piramitten yakın; mamutlar
   piramitlerle aynı çağda). Viral tarih türünün kanıtlanmış ailesi.

**Doğruluk kuralı (pazarlıksız):** her fakt gerçek ve yaygın kaynaklarla doğrulanabilir olmalı;
her bölümde ZAMAN ÇIPASI bulunur: 4 haneli yıl, onlu yıl biçimi ("the 1830s"), çağ biçimi
(BC, BCE, AD ya da CE) ya da yüzyıl (antik konular dışlanmaz). Sayı UYDURULMAZ; brief'te/kartta olmayan sayı prompt'a giremez.
**Konu havuzu kuralı:** bölüm konuları YALNIZ doğrulanmış tohum havuzundan seçilir. Havuzun
NORMATİF kaynağı bu doktrinin §6 listesi, TEKNİK tek kaynağı series.json `topic_pool` alanıdır
(id + topic + family; brief'e kopyalanmaz, prompt'a runtime enjekte edilir). Doğrulayıcı KOD
tarafında çalışır: bilinmeyen/kullanılmış seed_id RED, aile-tohum eşleşmezliği RED, havuz
tükenince üretim Gemini'ye gitmeden DURUR (fail-closed). Havuz genişletme prosedürü: yeni konu
ÖNCE bu doktrinin §6 listesine girer, SONRA topic_pool + doctrine_sha256 pin birlikte
güncellenir. Gemini'nin kendi fakt icat etmesi yasaktır (#15 benzeri kaynaklı konu akışı FAZ
4'te bağlanana kadar bu kural kanalın fakt kalkanıdır; Telegram onayı ikinci kalkan).

### 3.3 Yorum-yemi mühendisliği

- Yanılgı-kırıcı aile doğal "aslında..." düzeltme yorumu tetikler; bu kanalın uzman tuzağıdır.
- Bölüm başına EN FAZLA bir yarım-soru ("and that's not even the strange part, because").
- Rage-bait ve milliyetçi kışkırtma YASAK (tarih kanalında en riskli tuzak; platformlar
  bastırıyor, itibar radarı #34 alarm üretir).

### 3.4 Ses

- Register `shadowedhistory` (Charon) kalır; talimat 16 sn temposuna güncellenir: belgesel
  ağırlığı yerine **sert, kendinden emin, hızlı fakt anlatımı**; "dramatic pause" 16 sn'de
  lüks, tek kısa duraklama büküm öncesinde.
- Metin 26-38 kelime (Gemini'nin doğal fakt-anlatım uzunluğu; 16 sn'de rahat tempo); ilk
  cümle iddia (5-9 kelime), son cümle yarım bırakılıp başa bağlanır.
- Selamlama, CTA, "did you know" kalıbı YASAK (ilk kelime doğrudan faktır).

### 3.5 Paketleme

- **Başlık kalıpları (4 sabit, top-10'dan):**
  1. `The Real Reason <subject> <did X>`
  2. `How <subject> <impossible feat> In <YEAR>!`
  3. `<Subject>: Fact Or Ancient Propaganda?`
  4. `<Subject>: The <striking epithet>`
- **Hashtag 4 tane:** `#shorts #history #historyfacts #didyouknow`
- `title_card` AÇIK (zaman çıpası ekranda; footnotes'tan kanıtlanmış motor özelliği).
  `fact_captions` ve `caption` KULLANILMAZ (motor gerçeği: 2 çekimli formatta çift fakt
  overlay kuralı imkânsız; approval yayın yolu caption'ı zaten yok sayıyor). Fakt yükünü
  anlatım + başlık taşır. AI disclosure HER videoda açık.
- **Güvenlik:** kan, ceset, işkence, infaz görseli YOK; savaş/felaket konuları grafik şiddet
  göstermeden anlatılır (feed-güvenli tarih; merak dehşetten gelmez).
- Watermark'sız tek master, Upload-Post ile üç platforma native.

## 4. Tempo, platform, kredi

- **YouTube günde 1 (kürasyonlu, approval modu).** TikTok + IG Reels aynı master.
- 2 çekim × 7 sn + QC ≈ tahmini **200-350 kredi/bölüm** (unnatural-lab 4×6 ≈ 400-600
  referansından ölçekli; İLK gerçek koşunun logundan doğrulanır). ⚠️ KIE_API_KEY ortak havuz;
  hat açma kararı S8 bütçesine bağlı.

## 5. Ölçüm ve gate'ler (analytics_data verisiyle, haftalık)

| Metrik | Sağlıklı | Alarm | Ölçüm kaynağı |
|--------|----------|-------|---------------|
| İlk ≥48 saat snapshot izlenmesi (bölüm başına; "48h" tam 48 saat değil, yayının 48. saatinden SONRAKİ ilk günlük snapshot'tır) | Ocak-Mart bandına tırmanış (400+) | <100 kalıcı → ilk kare/iddia zayıf | analytics_data/daily (seri-bazlı medyan FAZ 4'e kadar MANUEL: published.json eşlemesiyle elle bakılır) |
| Ortalama izlenme yüzdesi (APV) | ≥%90 (16 sn'de) | <%70 → büküm geç geliyor | ÖLÇÜLEMEZ API katmanında; YouTube Studio'dan haftalık MANUEL bakış |
| APV >%100 (loop/rewatch VEKİLİ; doğrudan loop ölçümü değildir) | >%100 hedef | kapanış jesti sızmış mı denetle | ÖLÇÜLEMEZ; Studio'dan MANUEL |

- **Kill gate:** 25 bölüm sonunda medyan <350 VE tavan <3K → aile ağırlıkları değişir
  (kanal ve format iskeleti KALIR; 706-866'lık kanıt bandı hedeftir). Seri-bazlı medyan,
  published.json video eşlemesiyle hesaplanır (FAZ 4'te otomatikleşir, o güne dek manuel).
- **Double-down:** video >5K → aynı aileden 3 varyant öne; >50K → o aile haftada 3-4 bölüm
  (aile etiketi plan `family` alanından; FAZ 4 köprüsüne kadar manuel değerlendirme).
- Göreli eşikler FAZ 4 calibration.json katmanına bağlanır; 48h metrikleri ~14 gün ısınmada.
- **footnotes + drowned-history PAUSED kalır** (dirilmez; yeni format 25 bölüm penceresini
  tamamlamadan eski seriye dönüş yok). secrets-anatolia completed, dokunulmaz.

## 6. Tohum bölüm fikirleri (doğrulanmış faktlar, İngilizce)

1. The Anglo-Zanzibar War of 1896 lasted roughly 38 to 45 minutes, history's shortest war. (tuhaf savaş)
2. Oxford University is older than the Aztec Empire, teaching since ~1096. (zaman çarpması)
3. Cleopatra lived closer in time to the Moon landing than to the Great Pyramid. (zaman çarpması)
4. Woolly mammoths were still alive on Wrangel Island while the pyramids were built. (zaman çarpması)
5. Roman concrete heals its own cracks with lime clasts, confirmed by MIT in 2023. (imkânsız mühendislik)
6. The Eiffel Tower had a 20-year permit; a radio antenna saved it in 1909. (efsane vs kayıt)
7. Hiroo Onoda kept fighting World War 2 in the Philippines until 1974. (unutulmuş kişi)
8. Tree rings from a solar storm date the Viking camp in Newfoundland to exactly 1021. (imkânsız mühendislik)
9. In the 1830s, American quacks marketed tomato extract as medicine, even as tomato pills. (yanılgı kırıcı)
10. In 1932, Australia deployed soldiers with Lewis machine guns against emus; the cull failed and the birds stayed. (tuhaf savaş)
11. Napoleon was average height for his era; "tiny Napoleon" was British propaganda. (yanılgı kırıcı)
12. The Great Fire of London in 1666 destroyed 13,200 houses; traditional accounts name only six victims, though the true toll was likely higher. (efsane vs kayıt)

## 7. UYGULAMA (İhsan onayı sonrası)

**Yeni seri:** `shadowedhistory/flashpoints/`
- series.json: `slug: flashpoints`, `base_title: Shadowed History`, `standalone: true`,
  `upload_profile: shad0wedhistory`, `publish_mode: approval`, `status: active`,
  `priority: 999`, `total_parts: 0`, `next_part: 1` (ilk replenish part 1'den başlasın),
  platformlar youtube+instagram+tiktok, hashtag §3.5.
- auto_replenish: `{enabled: true, batch: 5, min_queue: 2, shots: 2, shot_seconds: "8",
  title_card: true, music_prompt: true, humans: historical,
  narration: {min_words: 26, max_words: 38}}` (hedef aralık prompt'ta; doğrulayıcı miksör
  payıyla kabul eder: 22-44; caption/fact_captions YOK; süre Kie enum gerçeği gereği 8 sn,
  bölüm ~16 sn)
  + `families`: ["yanılgı kırıcı", "imkânsız mühendislik", "tuhaf savaş", "unutulmuş kişi",
  "efsane vs kayıt", "zaman çarpması"] (kanonik enum; doğrulayıcı bunun dışını RED eder,
  ardışık aynı aile RED)
  + `music_style` (AYNEN bu İngilizce string): "Fast, tense, percussive underscore that hits
  with the opening claim and drives without pause; no slow or ethereal intro, no gentle
  outro; end mid-groove so the loop is seamless."
  + `topic_pool`: §6'daki 12 tohum `{id, topic, family}` yapısında (id = liste numarası;
  konular prompt'a runtime enjekte edilir, brief'e kopyalanmaz)
  + §3 kurallarını anlatan Türkçe brief (çıktı dili İngilizce; her partta `family` ve
  `seed_id` zorunlu; konu yalnız enjekte edilen havuzdan) + §3.5 title_style.
- series.json'a `doctrine_sha256` pin'i yazılır (bu dosyanın SHA-256'sı; doktrin her revize
  edildiğinde topic_pool ve brief'le birlikte güncellenir, eşleşmezse üretim fail-closed
  durur). Replenish her plan part'ına aynı hash'i damgalar; doktrin değişirse eski damgalı
  bekleyen planlar produce'da durur ve yeniden üretilir.
- bible.json: art_style = dönem gerçekçiliği (fotoreal sinematik, 9:16); series bloğunda
  `title_card: true` + `hook_teaser: {enabled: false}`; qc notu = tek fakt kuralı + kapanış
  jesti yasağı + okunur çakma-yazı yasağı; `narration.channel: shadowedhistory`.
- `core/narration.py` shadowedhistory talimatı §3.4'e göre güncellenir (ses Charon kalır).

**Cron AÇILMAZ:** hattın açılması ayrı İhsan kararı (S8 bütçe + 4 kayıt kuralı:
KURULUM_TAKIP + projects.yaml + routines.json + ACTIONS_TARGETS).

**Hat açma ön koşulu:** konu havuzu ≥25 doğrulanmış konuya çıkarılır (12 tohum 25 bölüm
penceresini dolduramaz; onay sonrası ek doğrulanmış tohum turu yapılır, her tohum kaynak
kontrolünden geçer).

**İhsan kararları:** (1) bu doktrinin onayı, (2) hattı açma + kredi bütçesi payı,
(3) footnotes/drowned-history kalıcı durumu (öneri: paused kalsın, 25 bölüm sonrası bakılır).
