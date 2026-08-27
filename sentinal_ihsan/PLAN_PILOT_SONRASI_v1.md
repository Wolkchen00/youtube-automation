# PLAN_PILOT_SONRASI_v1 ,  sentinal.ihsan.daily / Unnatural Lab

Tarih: 2026-08-27 · Durum: TASLAK r1 (Same Page Meeting öncesi) · Sahibi: İhsan
Öncül: `PLAN_GERCEKCILIK_v1.md` (ROCK 1-5 ön işi push'lu; ENTEGRE PİLOT 1 üretildi).
Bu plan **PİLOT 1 SONRASI** çevrimi kapsar. Öncül planın CORE FOCUS'u, P1-P6 ilkeleri ve
kill-gate/K8 mimarisi aynen geçerlidir; burada yalnız pilotun ÖLÇÜLEN sonucundan doğan işler var.

## CORE FOCUS (değişmedi)

Bölüm başına ~$2-4 üretim bütçesi içinde (video + tüm keyframe/referans görselleri + upscale;
Suno ayrı aylık kalemde), Unnatural Lab bölümlerini obje/ortam tutarlılığı ve gerçekçilikte
izleyicinin 0,5 saniyede "AI" diye kaydırmayacağı, beğeni ve yorum üreten videolara dönüştürmek.

## 0. PİLOT-1 ÖLÇÜM RAPORU (part22 "Something Is WRONG With This LEMON")

Üretim: 2026-08-26, izole deney runner'ı, `exp-2026-08-gerceklik/pilot`, YAYINLANMADI.
Ölçümler 2026-08-27'de Visionary tarafından bağımsız koşuldu (üreten koşunun raporu kanıt sayılmadı).

**GEÇEN (yeni doktrin sahada çalışıyor):**
- 4/4 çekim QC'den geçti; `qc_log` ep22: 20 review, 18 native_audio_review, 15 scene_cut_scan,
  10 regen, 4 final_reject, 4 qc_pass, 1 qc_hold. Eksik çekim yok, süre 22,29 sn (4×6 − micro_trim).
- Yüz yok (4 çekimde de yalnız eller/gövde). İlk karede anomali okunuyor (limon + taş sarmal merdiven).
- Ortam gerçekçiliği: yaşanmış mutfak tezgâhı ,  çizikli granit, kırıntı, fayans, pencere ışığı,
  dolap altı sıcak ışık, kesme tahtası, bez. Öncül plandaki "atölye tezgâhı" sterilliği gitti.
- **Native foley mikste:** konuşmasız pencerelerde final ↔ ham (raw) zarf korelasyonu **0,709**
  (ROCK 1 `bg_duck 0.0 → native_mix_level 0.5` düzeltmesi sahada çalışıyor).
- **Anlatım mikste:** (final − müziksiz) zarfı ile TTS zarfı korelasyonu **0,630**; konuşma
  pencerelerinde ortalama fark −36,9 dB, konuşmasız pencerelerde −54,2 dB (**+17,2 dB**).
- **Müzik yatağı:** 219 pencerenin 196'sında final > anlatımlı-müziksiz sürüm.
- Maliyet: **1.584 kr** (pilot alt-tavanı 1.700; deney toplam tavanı 4.000).

**BULGULAR (hepsi ölçüldü; her biri bu planın bir rock'ına bağlanır):**

- **B1 ,  SES SEVİYESİ, FİLO GENELİ (kritik).** Master **−24,5 LUFS**; sosyal platform normu ~−14 LUFS.
  Kök 1: `core/ffmpeg_tools.mix_voiceover` içindeki `amix=inputs=2` **`normalize=0` taşımıyor** →
  ffmpeg her girdiyi 1/N'e böler. Sentetik ölçüm (aynı filtre, aynı seviyeler): varsayılan −26,5 LUFS
  vs `normalize=0` −20,4 LUFS = **6,1 LU sistematik kayıp**. Kök 2: final master'da loudnorm YOK
  (`concatenate_audio_smooth` içindeki `loudnorm=I=-18` klip-içi katmandır, master değil).
  Etki alanı: anlatımlı TÜM seriler. Müzik-only seriler `replace_original=True` yolundan gider
  (amix yok) → etkilenmez. Sessiz feed'de 10 LU düşük master = ses açıkken bile "cılız" video.
- **B2 ,  ANOMALİ KİMLİĞİ SÜRÜKLENİYOR.** `object_card.descriptor` limonu kilitliyor ama anomalinin
  İÇ YAPISI çekimden çekime değişiyor: çekim 1 sık dokulu yıkıntı, çekim 3 düz kabartma,
  çekim 4 kemerli + derinlikli sarmal. `object_match` bunu göremez (limon eşleşiyor, kapı geçiyor).
  Kanalın satması gereken şey tam da o iç yapı.
- **B3 ,  İHLAL FİZİĞİ PREMISE'İ ÇÜRÜTÜYOR.** Çekim 3'te su basamaklardan inip karanlığa akmak yerine
  limonun ALTINDAN sızıp tezgâhta birikiyor → "dipsiz boşluk" yerine "akıtan meyve". Hiçbir kapı
  "ihlal amaçlandığı gibi okunuyor mu"yu ölçmüyor; dört zorunlu alan da geçti.
- **B4 ,  ORTAM DURUM SÜREKLİLİĞİ.** Çekim 3'ün bıraktığı su birikintisi çekim 4'te yok;
  `continuity_ok` yine de geçti (kapı obje kimliğine bakıyor, sahne durumuna değil).
- **B5 ,  KADRAJ KİLİDİ YALNIZ ÇEKİM İÇİ.** Çekim 4 belirgin biçimde daha yakın ve alçak açı.
  "The frame remains completely locked" cümlesi çekimler ARASI ölçek/açıyı bağlamıyor; ölçen kapı yok.
- **B6 ,  BÜTÇE ARİTMETİĞİ ÇÖKTÜ.** Pilot-1: 1.584 kr. Kalan: 2.416 kr. Öncül planın kalan aşamaları
  bake-off 2.400 + holdout 500 = 2.900 → toplam **4.484 > 4.000 mekanik tavan**. Ayrıca bake-off'un
  ayrı ön koşulu (ortak havuz koruması: Kie bakiyesi ≥ 15.000 kr) bugün karşılanmıyor (~8.165).
- **B7 ,  QC KOTA TAVANI.** Tek bölüm **53 Gemini çağrısı** yaktı (20 review + 18 native_audio +
  15 scene_cut). Yerel anahtar ücretsiz katmanda; 2026-08-26'da ikmal + QC kotayı tüketti (429) ve
  pilot ikinci Google projesinin anahtarıyla sürdürüldü. Fail-closed kapılar kota bitince `qc_hold`
  üretir → yayın durur. Günlük 4 kanallık filo bu tavanı her gün zorlar. `QC_MODEL` hâlâ
  `gemini-2.5-flash` (sabit, `series/critic.py:43`).

## İLKELER (devralınan P1-P6 + yeni)

- **P7 ,  Ölçüm önce, kapı sonra.** Yeni her QC alanı önce salt-ölçüm (log-only) modunda koşar;
  fixture kalibrasyonu yapılıp **yanlış-geçiş ve yanlış-red oranları raporlanmadan** fail-closed'a alınmaz.
- **P8 ,  Kapı bütçesi.** Her yeni kapı Gemini çağrı maliyetiyle birlikte planlanır; bölüm başına
  toplam QC çağrısının mekanik üst sınırı vardır. Kapı eklemek bedava değildir.

---

## ROCK A ,  Ses master zinciri (0 kredi; filo geneli; B1)

**Ne:**
1. `core/ffmpeg_tools.mix_voiceover`: `amix` çağrısına **`normalize=0`** eklenir (niyet edilen gain
   staging'i geri getirir: native × `native_mix_level` + ses × `voice_volume`).
2. Teslim zincirinin EN SONUNA (müzik miksinden sonra, `series/produce.py` içindeki tek noktada)
   **iki geçişli loudnorm** eklenir: ölçüm geçişi → `measured_*` değerleriyle uygulama geçişi.
   Hedef: **I = −14 LUFS, TP = −1,0 dBTP, LRA = 11**.
3. Bible'a `narration.master_lufs` (veya `series.master_lufs`) alanı; yoksa varsayılan −14.
   Müzik-only seriler dahil TÜM final master'lar bu aşamadan geçer (tek çıkış noktası).
4. Native foley'in normalizasyonla ezilmediği ölçülür (zarf korelasyonu eşiği).

**Done:** yeni master **−14 ±1 LUFS**, true peak ≤ −1,0 dBTP, native foley zarf korelasyonu ≥ 0,60;
mevcut 276 test + 127 subtest yeşil kalır; müzik-only yol davranışı bozulmaz.

**Proof:** `py -X utf8 -m pytest tests/ -q` **ve** yeni `tools/audio_master_check.py <mp4> [--ref-raw <mp4>]`
(ebur128 entegre loudness + true peak + native korelasyon ölçer; eşik dışında exit 1) , 
pilot-1 master'ının yeniden mikslenmiş sürümü üzerinde koşturulur ve çıktısı rapora eklenir.

## ROCK B ,  Anomali kimlik çıpası + ihlal okunurluk kapısı (0 kredi; B2, B3)

**Ne:**
1. Plan şemasına **`object_card.anomaly_descriptor`** (≥10 kelime; iç yapının malzeme + geometri +
   ışık imzası, ör. "weathered grey stone steps with a low arched opening and a dark unlit shaft").
   4 çekimde birebir tekrar; `replenish._validate_batch` fail-closed doğrular (`tek-obje-4x6` formatı).
2. Plana **`violation_statement`** (tek cümle: ihlal izleyiciye NE göstermeli;
   ör. "the water disappears down the shaft and never reaches the counter").
3. QC'ye iki alan: **`anomaly_match: bool|null`** (bölümün NB2 hero referansına karşı iç yapı eşleşmesi)
   ve **`violation_reads: bool|null`** (`violation_statement`'a karşı gösterilen fizik).
4. P7: iki alan da önce log-only; fixture seti (ep22'nin gerçek kareleri dahil pozitif/negatif örnekler)
   ölçülür, alan başına doğruluk + **yanlış-geçiş oranı** raporlanır, ancak ondan sonra fail-closed.
5. P8: iki yeni alan ayrı çağrı AÇMAZ ,  mevcut `review` çağrısının şemasına eklenir (çağrı sayısı sabit kalır).

**Done:** fixture'da ep22 çekim 3 karesi `violation_reads=false`, ep22 çekim 1 ↔ çekim 4 karesi
`anomaly_match=false` olarak yakalanır; iki alanın yanlış-geçiş oranı raporlanır; testler yeşil.

**Proof:** `py -X utf8 -m pytest tests/ -q` + yeni `tools/qc_fixture_report.py --field anomaly_match
--field violation_reads` çıktısı (alan başına doğruluk/yanlış-geçiş tablosu).

## ROCK C ,  Sahne durumu + kadraj sürüklenmesi: ÖLÇÜM (0 kredi; B4, B5)

**Ne:**
1. Plana opsiyonel **`state_carry`** (tek cümle: bir çekimin bıraktığı kalıcı iz);
   `continuity_ok` review şemasına "bu iz sonraki çekimde var mı" sorusu eklenir (yeni çağrı açmadan).
2. **Kadraj sürüklenmesi LLM'siz, kodla ölçülür:** her çekimin ilk karesinde kahraman objenin kadraj
   alanı ve merkez koordinatı (mevcut `first_frame_ok` doluluk/kontrast altyapısı yeniden kullanılır);
   çekimler arası sapma **log-only** raporlanır (öneri bandı: alan ±%35, merkez ±%15).
3. Kapıya dönüştürme bu rock'ta YAPILMAZ (P7): kalibrasyon verisi toplanır.

**Done:** ep22 üzerinde çekim 4'ün ölçek sapması sayıyla raporlanır; `state_carry` alanının
review şemasına ulaştığı testle kanıtlanır.

**Proof:** `py -X utf8 -m pytest tests/ -q` + yeni `tools/framing_drift_report.py <bölüm-klasörü>` çıktısı.

## ROCK D ,  QC kota dayanıklılığı (0 kredi; B7; K-G kararına bağlı)

**Ne:**
1. `QC_MODEL` sabitleri gözden geçirilir: anahtarın gerçekten görebildiği modeller listelenir
   (ücretsiz API çağrısı), kota havuzu ayrı ve güncel bir model seçilir; seçim gerekçesiyle loglanır.
2. **Bölüm başına QC çağrı sayacı + mekanik üst sınır** (`qc_call_budget`, öneri 60): aşımda `qc_hold`
   (fail-closed korunur; sessiz geçiş asla).
3. **429/kota hatası ayrı sınıflandırılır:** `qc_hold` sebebi `quota` olarak loglanır ve Telegram'a
   AYRI ve açık mesaj gider (bugün genel hataya karışıyor, 3,8 günlük sessizlik dersinin aynısı).
4. `GEMINI_API_KEY_QC` varsa QC bu anahtarı kullanır (üretim/ikmal anahtarından ayrılır); yoksa
   mevcut davranış birebir korunur.

**Done:** sahte 429 senaryosunda koşu `qc_hold(quota)` verir, yayınlamaz, ayrı Telegram mesajı çıkar;
gerçek bir bölümün QC çağrı sayısı raporlanır.

**Proof:** `py -X utf8 -m pytest tests/ -q` (yeni kota testleri dahil) + çağrı sayısı raporu.

## ROCK E ,  ENTEGRE PİLOT 2 (yayınsız; ~450-800 kr; K1-B kararına bağlı)

**Ne:** A-D yürürlükteyken part23 (sabun → banyo lavabosu) izole deney runner'ında üretilir.
Ölçülenler: 4 zorunlu kapı + 2 yeni alan, master LUFS, anomali eşleşmesi, ihlal okunurluğu,
kadraj sapması, QC çağrı sayısı, toplam kredi.

**Done:** rapor + video; A-D'nin sahada çalıştığı ölçümle kanıtlanır (pilot-1'e göre fark tablosu).

**Proof:** `py -X utf8 -m series.experiment run unnatural-lab --plan sentinal_ihsan/unnatural-lab/plans/part23.json --experiment-id exp-2026-08-gerceklik --stage pilot` + `tools/audio_master_check.py` + fixture raporları.

---

## KARAR MADDELERİ (İhsan)

- **K1-B (deney bütçesi).** Pilot-1 1.584 kr yedi, kalan 2.416 kr; bake-off + holdout 2.900 kr sığmıyor.
  (a) Tavanı 4.000 → 6.000 kr ($30) çıkar, öncül plan aynen sürsün.
  (b) Tavan 4.000'de kalsın, **bake-off ERTELENSİN**; pilot-2 + kill-gate Omni ile koşsun, motor kararı
  sonraki çevrime kalsın. (c) Bake-off küçültülsün (4 kol → 2 kol: Omni kontrol + Veo FLF), holdout korunur.
  **Önerim: (b)** ,  B2 bake-off'un gerekçesini güçlendiriyor ama Kie bakiyesi (~8.165) zaten 15.000
  eşiğinin altında; önce 0 kredilik kazanımları (A-D) alıp kill-gate'i başlatmak, motor kararını
  bakiye ve kanıt olgunlaşınca vermek daha ucuz ve daha hızlı yayına döndürür.
- **K-G (QC anahtarı).** Ücretsiz katman filo için yetersiz (bölüm başı 53 çağrı).
  (a) Ödemeli katmana geç (aylık birkaç dolar), (b) QC'ye ayrı proje anahtarı ver, (c) kapı sayısını azalt.
  **Önerim: (a)+(b)**; ROCK D bunu mekanik hale getirir.
- **K-P (pilot-1 kalite kapısı).** P6 gereği pilot YAYINLANMAZ. Sorulan tek şey: ep22 kalitesi
  kill-gate'e girecek çıtayı karşılıyor mu ,  evet / hayır / "şu düzeltmeyle evet".

## ERTELENENLER (Issues)

Öncül planın Ertelenenler listesi aynen geçerli. Eklenenler: B5 kapıya dönüşmeden önce ölçüm (ROCK C);
sidechain ducking + LUFS ince ayarı; anomali referansının çekim başına yeniden basılması (maliyetli varyant);
`micro_trim` sonrası ilk-kare tazeleme.

## SIRA VE ZAMAN

1. **ROCK A** (yarım gün, filo geneli kazanım) → 2. **ROCK B** → 3. **ROCK C** (ölçüm) →
4. **ROCK D** (K-G kararıyla) → 5. **ROCK E / PİLOT 2** (K1-B kararıyla) → 6. K8 prosedürü + 10 bölümlük kill-gate.

**K8 penceresi işliyor:** seri part21'den beri yayınsız (workflow `unnatural-lab.yml` devre dışı,
2026-08-26). Öncül plandaki azami yayınsız süre 3 hafta; bu çevrim o pencereye sığmalıdır.
