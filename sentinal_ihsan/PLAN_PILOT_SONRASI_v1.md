# PLAN_PILOT_SONRASI_v1 ,  sentinal.ihsan.daily / Unnatural Lab

Tarih: 2026-08-27 · Durum: TASLAK r4 (Same Page Meeting tur 1-3 bulguları işlendi) · Sahibi: İhsan
Öncül: `PLAN_GERCEKCILIK_v1.md` (ROCK 1-5 ön işi push'lu; ENTEGRE PİLOT 1 üretildi).
Ölçüm kanıtları: `sentinal_ihsan/measurements/pilot1_audio.md` · Müzakere: `PLAN_PILOT_SONRASI_SPM_LOG.md`

## CORE FOCUS (değişmedi)

Bölüm başına ~$2-4 üretim bütçesi içinde (video + tüm keyframe/referans görselleri + upscale;
Suno ayrı aylık kalemde), Unnatural Lab bölümlerini obje/ortam tutarlılığı ve gerçekçilikte
izleyicinin 0,5 saniyede "AI" diye kaydırmayacağı, beğeni ve yorum üreten videolara dönüştürmek.

## 0. PİLOT-1 ÖLÇÜM RAPORU (part22 "Something Is WRONG With This LEMON")

Üretim: 2026-08-26, izole deney runner'ı, `exp-2026-08-gerceklik/pilot`, YAYINLANMADI.
Ölçümler 2026-08-27'de Visionary tarafından bağımsız koşuldu.

**GEÇEN:** 4/4 çekim QC'den geçti; eksik çekim yok; 22,29 sn. Yüz yok; ilk karede anomali okunuyor;
ortam yaşanmış mutfak. Native foley mikste (konuşmasız pencerelerde final↔ham korelasyonu **0,709**);
anlatım mikste (**+17,2 dB**); müzik yatağı 219 pencerenin 196'sında. Maliyet **1.584 kr**.

**BULGULAR:**

- **B1 ,  SES SEVİYESİ (kritik).** Master **−24,5 LUFS** (norm ~−14). İki kök: (i) `mix_voiceover`
  içindeki `amix` **`normalize=0` taşımıyor** → kontrollü ölçümde **6,1 LU kayıp** (yalnız anlatımlı
  seriler); (ii) teslim zincirinde **master normalizasyonu yok** (19 serinin tamamı).
- **B2 ,  ANOMALİ KİMLİĞİ SÜRÜKLENİYOR.** Anomalinin iç yapısı çekim 1/3/4'te farklı; `object_match` görmüyor.
- **B3 ,  İHLAL FİZİĞİ PREMISE'İ ÇÜRÜTÜYOR.** Çekim 3'te su limonun altından sızıp tezgâhta birikiyor.
- **B4 ,  ORTAM DURUM SÜREKLİLİĞİ.** Birikinti çekim 4'te yok; `continuity_ok` geçti.
- **B5 ,  KADRAJ KİLİDİ YALNIZ ÇEKİM İÇİ.** Ölçüm altyapısı yok (`ffmpeg_tools.py:95` yalnız luma/keskinlik
  vekilleri) → ERTELENENLER (telemetri).
- **B6 ,  BÜTÇE ARİTMETİĞİ.** Harcanan 1.584; kalan aşama tavanları 3.200 → en kötü 4.784 > 4.000.
  `pilot` aşamasında kalan **116 kr**.
- **B7 ,  QC ÇAĞRI HACMİ.** Loglanan **36** Gemini çağrısı (18 review + 18 native_audio); 15 scene_cut
  yerel ffmpeg. **Asıl sorun:** retry / yedek model / 429 loglanmıyor → gerçek deneme sayısı ölçülemiyor.
- **B8 ,  KREDİ ÖMRÜ (ACİL, ÖLÇÜLDÜ).** Bakiye **5.999 kr (~$30)**; `credits_ledger.json` son 7 gün
  ortalaması **1.390 kr/gün**; Ağustos gerçekleşen **37.594 kr ≈ $188/ay**. → **~4 günlük ömür.**
  Kill-gate sonuna kadar (bugünden ~22 gün) toplam ihtiyaç **~35.900 kr ≈ $179**; eldeki düşülünce
  **~30.000 kr ≈ $149 yükleme**. Mevcut bakiyeyle kill-gate mekanik olarak imkânsızdır.
- **B9 ,  ORTAM DİLİ KODDA ESKİ.** "workbench/bench" `bible.json > qc.notes` dışında da sabit:
  `series/critic.py:153, 437, 441, **450**, 1141, 1145` ve `series/produce.py:851, 878`.

## İLKELER (devralınan P1-P6 + yeni)

- **P7 ,  Ölçüm önce, kapı sonra; manifestli protokolle.** Yeni her QC alanı log-only başlar.
  **Etiket manifesti** (`tests/fixtures/qc_calibration/manifest.json`) alan başına örnekleri,
  sınıfını (pozitif/negatif), split'ini (train/held-out) ve insan etiketini taşır; manifest
  değişmez (immutable) kabul edilir ve raporlayıcı **manifest sayıları tutmuyorsa terfi ÖNERİSİ
  üretmez, hata verir**. Asgari: alan başına **≥24 örnek**, **≥8 negatif**, **≥%50 held-out**,
  sınıf-katmanlı. Fixture'lar üretimin gördüğü biçimde (sıralı 12 karelik grup + önceki çekimin son
  karesi) hazırlanır. Terfi eşiği: **yanlış-geçiş ≤ %10, yanlış-red ≤ %20, gözlemlenebilir vakalarda
  null ≤ %30**; gerekçesiz null hata sayılır. **Terfi metrikleri YALNIZ held-out split'ten hesaplanır;**
  train sonuçları ayrı raporlanır ve terfi kararına girmez. Eşik tutmazsa alan log-only kalır
  (başarısızlık değil).
- **P8 ,  Kapı bütçesi ölçümle konur.** Önce gerçek `generate_content` denemeleri kaydedilir; sayısal
  tavan pilot-2 verisinden sonra konur.
- **P9 ,  Filo riski tek serinin işine feda edilmez.** Teslim zincirine dokunan değişiklik **tek bir
  opt-in alanın** arkasındadır; alan yoksa çıktı bit-değişmez. Yayılım ayrı, kanaryalı adım (K-FILO).

---

## ROCK A ,  Ses master zinciri (0 kredi; yalnız Unnatural Lab; B1)

**Ne:**
1. **Tek opt-in anahtar `series.master_lufs`.** Alan yoksa ses yolu (amix davranışı dahil)
   bugünküyle birebir aynıdır. Bu çevrimde yalnız `unnatural-lab/bible.json` `-14` alır.
2. Yeni yolda `mix_voiceover` **`normalize=0`** ile çağrılır (parametre; varsayılan legacy).
3. **Master noktası:** ölçülen zincir `_post_process` (1613) → `hook_teaser` (1638) →
   `title_card_overlay` (1665) → `fact_captions_overlay` (1703) → `_upscale_master` (1713).
   Mastering **`_upscale_master`'dan hemen önce** uygulanır.
4. **İki geçişli loudnorm**: hedef **I = −14 LUFS, TP = −1,0 dBTP, LRA = 11**.
5. **Upscale dış servistir (Topaz):** master'lanmış ses dönen 4K'ya **remux** edilir; `delivery_1080.mp4`
   ve 4K **ayrı ayrı** doğrulanır.
6. **Fail-closed:** `master_lufs` tanımlıyken mastering veya iki teslimattan HERHANGİ birinin
   doğrulaması başarısızsa bölüm **`qc_hold`**.
7. **Ölçüm sözleşmesi (belirsizlik bırakmaz):**
   - **Loudness ve true-peak, teslim dosyasının KENDİ kanal düzeni ve örnekleme hızında ölçülür**
     (`ebur128=peak=true`; downmix ya da yeniden örnekleme YOK). Mono 8 kHz indirgeme YALNIZ zarf
     karşılaştırmaları içindir ,  aksi hâlde stereo kırpma ve true-peak aşımı görünmez kalır.
   - Zarf karşılaştırması final master'ın zaman eksenine hizalanır: teaser eklendiyse gövde kayması
     (`teaser_len`) düşülür; **müzik yatağı referansı üretimin filtre grafiğiyle yeniden üretilir**
     (loop + `volume` + `afade`), ham `bg_music.mp3` ile karşılaştırma YAPILMAZ; native referans
     master noktasındaki stem'den alınır. Pencere 100 ms.
   - "Konuşmasız pencere" = TTS zarfı kendi tepesinin **%8**'inin altında olan pencere.
   - **Aggregation: seçilen pencerelerin MEDYANI** kullanılır (tek uç pencere kararı çevirmesin);
     eşiği ihlal eden pencere oranı da raporlanır.
   - Eşikler: master **−14 ±1 LUFS**, **TP ≤ −1,0 dBTP** (her iki teslimat);
     foley: konuşmasız pencerelerde program medyanı **≥ −30 dBFS** VE yalnız-müzik referansının
     medyanının **≥ 6 dB** üstünde; anlatım/yatak dengesi: `--baseline-final` ile verilen
     değişiklik-öncesi master'a göre fark **±1,5 dB** bandında (bant dışındaysa `music_volume`
     ölçümle yeniden ayarlanır).
8. Filoya yayılım bu rock'ta YAPILMAZ (K-FILO).

**Done:** her iki teslimat da dört eşiği geçer; `master_lufs` alanı olmayan seriler için çıktı
bit-değişmez; mastering/doğrulama hatası `qc_hold` üretir; 276 + 127 subtest yeşil.

**Proof:**
```
py -X utf8 -m pytest tests/ -q
py -X utf8 tools/audio_master_check.py <delivery_1080.mp4> --ref-raw <ep_raw.mp4> --ref-tts <narration.wav> --ref-bed <bg_music.mp3> --baseline-final <pilot1_master.mp4>
py -X utf8 tools/audio_master_check.py <delivery_4k.mp4>   --ref-raw <ep_raw.mp4> --ref-tts <narration.wav> --ref-bed <bg_music.mp3>
```
Testler: (a) **iki** bit-değişmezlik fixture'ı ,  bir anlatımlı seri ve bir `replace_original=True`
müzik-only seri ,  artı "unnatural-lab dışında hiçbir bible'da `master_lufs` yok" assert'i;
(b) bozuk 4K sesi → `qc_hold` testi; (c) mastering başarısızlığı → `qc_hold` testi.

## ROCK B ,  Anomali kimliği + ihlal okunurluğu + sahne durumu (0 kredi; B2, B3, B4, B9)

**Ne:**
1. **`object_card.anomaly_descriptor`** (≥10 kelime; iç yapının malzeme + geometri + ışık imzası),
   4 çekimde birebir; `tek-obje-4x6` formatında fail-closed doğrulanır.
2. **Şema beyaz listeleri açıkça güncellenir:** `series/shots.py: OBJECT_CARD_FIELDS`,
   `TEK_OBJE_FORMAT`, `validate_plan` ve `series/replenish.py` normalizasyonu (~1003, ~1151).
   `part23.json` proof'tan ÖNCE yeni şemaya migrate edilir.
3. **İhlal çekim bazında ve OLUMLU:** ilgili çekime `shot.violation_observation` ,  12 karelik sıralı
   örneklemde gözlemlenebilir olumlu kontrol noktası. Olumsuz/zaman-ötesi ifade yasak; ihlal
   taşımayan çekimlerde **N/A**.
4. **`state_carry` kaynak çekimde** tanımlanır, **yalnız bir sonraki çekime karşı** değerlendirilir;
   ardıl yoksa N/A.
5. **Üç nullable alan** review şemasına (yeni çağrı açmadan): `anomaly_match`, `violation_reads`,
   `state_carry_ok`; biçim `{value: bool|null, visible: bool, confidence: 0-1}`.
   **`visible` tanımı bağımsızdır:** ilgili BÖLGE/EYLEM kadrajda ve okunabilir mi (beklenen özelliğin
   VAR olup olmaması değil). Yani anomali bölgesi görünüyor ama beklenen yapı yoksa doğru cevap
   **`visible=true, value=false`**'tur; `visible=false` yalnız bölge kapalı/çok küçük/karanlıksa geçerlidir.
   Bu ayrım fixture'da ayrı test sınıfı olarak ölçülür (görünür-ama-yok vakaları).
6. **Terfi anahtarı ve karar tablosu:** her alan için `qc.enforce.<field>: false|true` konfigürasyonu.
   `false` (log-only): hiçbir sonuç bölümü durdurmaz. `true` (terfi etmiş):
   | sonuç | davranış |
   |---|---|
   | `value=true` | geç |
   | `value=false`, `visible=true` | **fail → regen hakkı** |
   | `value=null`, `visible=false` | geç, `qc_log`'a not (gözlemlenemedi) |
   | `value=null`, `visible=true` (gerekçesiz null) | **fail-closed → `qc_hold`** |
   | `confidence < 0.5` | `value` yok sayılır, gerekçesiz null gibi işlenir |
   Terfi etmiş bir alanın `false` ve gerekçesiz `null` sonucunun teslimatı BLOKE ettiği testle kanıtlanır.
7. **Referans zinciri:** `ensure_episode_refs` hero referansını `descriptor` + `anomaly_descriptor` +
   `object_card.name` + ortam tarifi + **prompt şablon sürümü** ile üretir; plana bunların
   **kanonik tam prompt'unun** `ref_prompt_sha256`'sı yazılır. Hash uyuşmazlığının HERHANGİ bir
   nedeni (herhangi bir alan ya da şablon sürümü değişikliği) referansı geçersiz kılar ve yeniden ürettirir.
8. **B9 onarımı ,  ortam-nötr dil, TÜM yüzeylerde:** `bible.json > qc.notes` +
   `series/critic.py:153, 437, 441, **450**, 1141, 1145` + `series/produce.py:851, 878`.
   Metinler `object_card.environment`'tan beslenir; "workbench/bench" sabitleri kaldırılır;
   ortam alanı olmayan seriler için mevcut metin fallback'i korunur ama **ortam alanı olan seride
   fallback'e düşülmediği** testle kanıtlanır.
9. Üç alan da log-only başlar; P7 manifest protokolüyle kalibre edilir. `continuity_ok`'un bugünkü
   fail-closed davranışı DEĞİŞMEZ.

**Done:** fixture'da ep22 çekim 3 `violation_reads` = görünür-ama-yok (false), çekim 1 ↔ 4
`anomaly_match=false`; üç alanın yanlış-geçiş/yanlış-red/null oranı manifest sayılarıyla raporlanır;
bayat referans ve hash testleri geçer; **banyo fixture'ıyla** üretilen tüm QC/referans/regen
prompt'larında workbench dili yok; testler yeşil.

**Proof:** `py -X utf8 -m pytest tests/ -q` ,  uçtan uca zincir testi dahil (plan → normalizasyon →
`ensure_episode_refs` → Gemini istek gövdesi → `qc_log`), artı terfi karar tablosu testleri ve
banyo-ortamı prompt testleri ,  + `py -X utf8 tools/qc_fixture_report.py --field anomaly_match
--field violation_reads --field state_carry_ok` (manifest sayıları tutmazsa exit 1).

## ROCK C ,  QC ölçümleme + kota dayanıklılığı (0 kredi; B7)

**C1 ,  karar beklemez (2026-08-29):**
1. **Dayanıklı deneme kaydı:** her `generate_content` çağrısından ÖNCE `qc_log.jsonl`'a
   `qc_api_attempt` (benzersiz `attempt_id`, görev tipi, model, `is_fallback`, deney kimliği)
   **katı append+flush** yoluyla yazılır. Mevcut `_log_event` yazma hatasını sessizce yutuyor;
   yeni yol için bu YASAK: **attempt kalıcı olarak yazılamadıysa ücretli/kotalı çağrı YAPILMAZ.**
   Yanıt dönünce `qc_api_result` yazılır; sonuç sınıfı **yalnız `ok | 429 | error`**
   (hangi modelin denendiği ve fallback olup olmadığı attempt olayında durur).
   Eşleşmemiş attempt = çökme/bilinmeyen sonuç.
2. **Tükenme politikası:** ara 429'lar loglanır, tek başına bölümü düşürmez. **Deneme politikası
   HANGİ nedenle tükenirse tükensin** (kota, kimlik doğrulama, 5xx, ayrıştırma hatası, log yazma
   hatası) sonuç **`qc_hold`**'dur ,  "incelenmemiş kabul" yoluna düşülmez. `reason` alanı
   `quota` / `auth` / `server` / `parse` / `logging` olarak ayrışır ve Telegram'da kota ile
   kota-dışı ayrı mesajlanır.
3. Çağrı tavanı bu rock'ta KONMAZ (P8).

**C2 ,  K-G kararına bağlı (varsayılan tarihli, 2026-08-31):** `GEMINI_API_KEY_QC` desteği; yoksa
mevcut davranış korunur. Yanıt gelmezse İhsan'ın ikinci Google projesi anahtarı QC'ye atanır.
`QC_MODEL` seçimi kanıtla yapılır; **model değiştirmek kota stratejisi değildir** (aynı proje = aynı havuz).

**Done:** bir bölümün gerçek API denemesi `qc_log`'dan sayılabiliyor; log yazılamıyorsa çağrı
yapılmıyor; her tükenme sınıfı `qc_hold` üretiyor; kota ve kota-dışı ayrı alarm.

**Proof:** `py -X utf8 -m pytest tests/ -q` (attempt/result eşleşmesi, log-yazma-hatası → çağrı yok,
beş tükenme sınıfı → `qc_hold`, tek 429'da düşmeme) + pilot-2 deneme sayısı raporu.

## ROCK D ,  Kredi tabanı + ENTEGRE PİLOT 2 (K-KREDI + K1-B kararına bağlı)

**D0 ,  Küresel kredi tabanı (0 kredi, kod işi; ön koşul).** Bugün ne bölüm defteri ne deney defteri
başka workflow'ların ortak bakiyeyi tüketmesini durduramıyor. Ücretli çağrı yapan **tüm** yollara
ortak kapı: **`KIE_BALANCE_FLOOR`**. Yetkilendirme kuralı: **taze bakiye (önbelleksiz) − bu çağrının
tahmini − açık (settle edilmemiş) rezervasyonların toplamı ≥ taban** ise geçer, değilse reddedilir ve
alarm gider. Kontrol + rezervasyon yazımı **workflow'lar arası kilit** altında atomik yapılır (yarış
hâlinde iki koşu aynı krediyi harcayamaz).
**Kill-gate tabanla çelişmez:** kill-gate yayınları kendi **sahip etiketli rezervasyonundan**
(ör. `owner="killgate"`, 10 bölüm × tahmin) işlemsel olarak düşülür ve koşu sonunda gerçekleşenle
mutabakat yapılır; taban yalnız bu rezervasyonun DIŞINDAKİ bakiyeyi korur, dolayısıyla ne kill-gate'i
bloke eder ne de sıfırlanmak zorunda kalır.
*Proof:* taban altında çağrı reddedilir; eşzamanlı iki yetkilendirme testinde yalnız biri geçer;
açık rezervasyonlar hesaba katılmazsa testin KIRMIZI olduğu gösterilir; kill-gate rezervasyonu
düşülürken filo çağrıları taban tarafından durdurulur.

**D1 ,  Bütçe mekaniği (tek seçenek):** defterde **`pilot2` aşaması, tavanı tam 800 kr**.
4.000 toplam altında harita: `pilot 1.700` (1.584 harcandı, donduruldu) · **`pilot2` 800** ·
`preflight 0` · `bakeoff 0` · `holdout 0` → tahsis 2.500; tahsis edilmemiş 1.500 yalnız K1-B ile açılır.

**D2 ,  Pilot 2:** A-C yürürlükteyken part23 (sabun → banyo lavabosu) izole runner'da üretilir.
Ölçülenler: 4 zorunlu kapı + 3 yeni alan, master LUFS (1080p ve 4K), foley eşikleri, anomali
eşleşmesi, ihlal okunurluğu, gerçek QC API denemesi, toplam kredi; pilot-1'e göre fark tablosu.
**Başlama ön koşulu:** `KIE_BALANCE_FLOOR` kill-gate rezervini koruyacak şekilde ayarlanmış olmalı
ve canlı bakiye pilot-2 + taban toplamını karşılamalı.

**Proof:** `py -X utf8 -m series.experiment run unnatural-lab --plan sentinal_ihsan/unnatural-lab/plans/part23.json --experiment-id exp-2026-08-gerceklik --stage pilot2` + iki teslimat için
`tools/audio_master_check.py` + fixture raporları.

---

## KARAR MADDELERİ (İhsan)

- **K-KREDI (ACİL ,  karar tarihi 2026-08-28).** Bakiye **5.999 kr (~$30)**; ölçülen tüketim
  **1.390 kr/gün**; Ağustos gerçekleşen **$188**. Hesap: 08-27→09-08 filo **16.680 kr** + pilot-2
  **800** + kill-gate 10 gün (filo 1.390 + unnatural 450 = 1.840/gün) **18.400** = **35.880 kr ≈ $179**;
  eldeki düşülünce **yükleme ≈ 29.900 kr ≈ $149**.
  (a) **~30.000 kr (~$150)** ,  pilot-2 + kill-gate + filo sonuna kadar güvence. **Önerim.**
  (b) ~12.000 kr (~$60) ,  filo 09-08'e kadar + pilot-2; kill-gate için ikinci yükleme şart.
  (c) ~7.000 kr (~$35) ,  yalnız filo birkaç gün daha; deneyler durur.
  (d) yükleme yok ,  **~4 gün içinde tüm filo durur.**
  Not: kill-gate 10 ARDIŞIK yayın ölçer; ortasında kredi bitmesi ölçümü çöpe atar → (b) seçilirse
  kill-gate başlangıcı ikinci yüklemeye bağlanır ve takvim kayar.
- **K1-B (deney bütçesi).** (a) tavan 6.000; (b) tavan 4.000 kalsın, **bake-off ERTELENSİN**;
  (c) bake-off 2 kola insin. **Önerim: (b)**. Yanıt gelmezse **2026-08-30'da (b)** varsayılan.
- **K-G (QC anahtarı).** (a) ödemeli katman, (b) ayrı proje anahtarı, (c) kapı sayısını azalt.
  **Önerim: (a)+(b)**. Yanıt gelmezse 2026-08-31'de ikinci proje anahtarı QC'ye atanır.
- **K-FILO (mastering yayılımı).** Pilot-2 raporundan sonra 18 seriye kanarya ile yayılsın mı?
  **Önerim: EVET**, bir anlatımlı + bir müzik-only seride gölge ölçümden sonra.
- **K8 (yayına dönüş modu).** Üç yeni alan kill-gate başında hâlâ log-only olabilir → o durumda
  **varsayılan (b): 10 bölümün tamamı insan onaylı**; alanlar terfi etmişse (a) 3 onay + 7 auto.
- **K-P (pilot-1 kalite kapısı).** Pilot YAYINLANMAZ (P6). Tek soru: ep22 kalitesi kill-gate çıtasını
  karşılıyor mu ,  evet / hayır / "şu düzeltmeyle evet".

## ERTELENENLER (Issues)

Öncül planın listesi geçerli. Eklenenler: **B5 kadraj sürüklenmesi ölçümü** (insan etiketli kutu ya da
bilinen sentetik dönüşüm ister → pilot-2 ve kill-gate telemetrisi, K8 ön koşulu DEĞİL);
sidechain ducking + LUFS ince ayarı; anomali referansının çekim başına yeniden basılması;
`micro_trim` sonrası ilk-kare tazeleme; mastering'in 18 seriye yayılımı (K-FILO);
QC çağrı tavanının sayısal değeri (pilot-2 sonrası).

## SIRA VE ZAMAN (K8 penceresi: son tarih 2026-09-16)

| # | İş | Tarih hedefi | Bağlı karar |
|---|---|---|---|
| 1 | ROCK A (ses master, yalnız unnatural-lab) | 2026-08-28 | ,  |
| 2 | ROCK C1 (QC ölçümleme + tükenme politikası) | 2026-08-29 | ,  |
| 3 | ROCK D0 (küresel kredi tabanı) | 2026-08-29 | ,  |
| 4 | ROCK B (anomali + ihlal + durum + ortam dili, log-only) | 2026-08-31 | ,  |
| 5 | ROCK C2 (QC anahtarı) | 2026-08-31 | K-G (tarihli varsayılan) |
| 6 | ROCK D1-D2 / PİLOT 2 | 2026-09-02 | **K-KREDI (08-28)** + K1-B (08-30) |
| 7 | P7 kalibrasyon raporu → terfi (ZORUNLU DEĞİL) | 2026-09-04 | ,  |
| 8 | K8 prosedürü + kill-gate başlangıcı | **en geç 2026-09-08** | K8 + K-KREDI |

**Stop-loss:** 2026-09-08'e kadar kill-gate başlamazsa kalan rock'lar ERTELENENLER'e taşınır ve kanal
mevcut (A+B uygulanmış) stack'le yayına döner ,  **yeni alanlar log-only ise yayın modu insan onaylıdır
(K8-b)**, otomatik yayına geçilmez. Yayınsız geçiş 3 haftayı AŞMAZ. Seri part21'den beri yayınsız.
