# RF-PLAN: Kanca kapıları ve yayın hattı onarımı (unnatural-lab)

Tarih: 2026-09-10 (Los Angeles)
Kaynak analiz: `sentinal_ihsan/REELYZE-RAPOR.md`
Kanal: `sentinal_ihsan` / seri `unnatural-lab` (filonun en iyi kanalı, 30 günlük medyan 1.292)

## CORE FOCUS

Çalışan formülü bozmadan iki şeyi garanti altına al: ölçülmüş biçimde ölü olan
bölüm fikirleri para harcanmadan ÖNCE reddedilsin, ve üretilmiş bölümler
yayına çıkmadan yolda ölmesin.

---

## 0. Ölçüm tabanı (bu planın dayandığı veri)

### 0.1 Aile başına performans (`sentinal_ihsan/unnatural-lab/calibration.json`, 2026-09-06 anlık görüntüsü)

| Aile | n | Medyan |
|---|---|---|
| impossible-state-change | 3 | 1295 |
| impossible-interior | 2 | 1196 |
| impossible-material | 2 | 1161 |
| impossible-behaviour | 3 | 1136 |
| reversed-physics | 1 | 616 |
| slightly-uncanny | 1 | 495 |
| **impossible-continuity** | **2** | **79 ve 146** |

`impossible-continuity` ailesinin iki bölümü de öldü. Diğer her ailenin
her bölümü en az 495 aldı. Örneklem küçük (n=2) ama mekanizma açıklanabilir:
bu ailenin anomalisi (çoğalma, bitmeme, kendini yenileme) TEK KAREDE
okunamaz, izleyicinin zaman geçirmesini ister.

### 0.2 Raporun bir teşhisi YANLIŞ, düzeltiliyor

REELYZE raporu part 19'u (`I Found UNNATURAL PAGES... And They STARTED To REPLICATE!`, 82 izlenme)
"I Found... kalıbı izleyiciden sabır istiyor" diye açıklıyor. Ölçüm bunu ÇÜRÜTÜYOR:
aynı kalıbı kullanan 7 bölüm var ve metrikleri 801 / 74 / **2554** / 1285 / 1127 / 1202 / 79.
Kalıbın kendisi nötr. Part 19'u öldüren şey başlık kalıbı değil, `impossible-continuity`
ailesidir. Aynı şey part 32 (`This NAPKIN Never ENDS!`, 146) için de geçerli:
o başlık mevcut kalıp 2'ye UYUYOR, yani kalıp denetimi onu yakalayamazdı.

**Sonuç: kapı başlık BİÇİMİNE değil, anomalinin ZAMANA BAĞLI olup olmadığına kurulmalı.**
Başlık biçimi kapısı ayrı ve daha ucuz bir iş, o da kurulacak ama ikisi farklı şeyi yakalar.

### 0.3 Motorda zaten var olan ama bu kanalda TAKILI OLMAYAN parçalar

- `series/replenish.py::_compiled_title_patterns` + `validate_plan_against_config`:
  `title_patterns` (regex + izinli aile listesi) tam bir başlık kapısı sunuyor,
  test edilmiş durumda. `sentinal_ihsan/unnatural-lab/series.json` içindeki
  `auto_replenish` bloğunda bu anahtar YOK; kanal yalnız serbest metin `title_style`
  talimatına güveniyor.
- `series/shots.py::TEMPORAL_OVERREACH`: `never|always|forever|eventually` regex'i var,
  ama YALNIZ `shot.violation_observation` alanına uygulanıyor (shots.py:150).
  `episode.title` ve `object_card.anomaly_descriptor` hiç taranmıyor.
  Part 32'nin başlığında geçen "Never" kelimesini mevcut regex ZATEN yakalardı,
  ama başlık o regex'ten geçmiyor.

### 0.4 Yayın hattı gerçeği (`series.json` parts durumları)

33 bölümün 10'u YouTube'a hiç çıkmadı:

| Part | Durum | Sebep |
|---|---|---|
| 25 | budget_exhausted | kalan=364, asgari=400, tavan=800 |
| 26 | budget_exhausted | kalan=68, asgari=400, tavan=1000 |
| 28 | budget_exhausted | kalan=320, asgari=400, tavan=1000 |
| 30 | needs_human | reason_code=UNKNOWN, "üretim nedeni bilinmiyor" |
| 23, 24 | skipped | |
| 33 | qc_retry, ŞU AN TIKALI | master true-peak -0,9 dBTP > -1,0, 3 denemede tutturamadı |

`last_run.json`: 2026-09-09 koşusu `failure`. Son 11 bölümün 6'sı yayına çıkmadı.
Bütçe ile ölen üç bölümde kredi HARCANDI ve karşılığında video ALINMADI
(part 26: 1000 kredinin 932'si yanmış, çıktı yok).

---

## 1. Rock listesi

Beş rock, bağımlılık sırasında. Her rock'ın kanıtı `python -m pytest tests/ -q`
(taban: 803 passed, 188 subtests, ~35 sn) ARTI o rock'a ait yeni test dosyası.

Kanıt komutunda kullanılacak yorumlayıcı: `python` (PATH'teki Python 3.12, pytest 9.1.1).
Depo kökündeki `.venv` içinde pytest YOK, onu kullanma.

---

### ROCK 3 (İLK SIRADA, kanal şu an bunda tıkalı) , master true-peak yakınsaması

**Kusur.** `core/ffmpeg_tools.py::master_audio`, teslimi 3 denemede -1,0 dBTP altına
indirmeye çalışıyor. Her başarısız denemeden sonra limiter tavanını TAM AŞIM KADAR
geri çekiyor:

```
limiter_db -= overshoot
```

Marj yok. Limiter AAC kodlamasından ÖNCE uygulanıyor, ölçüm ise kodlanmış teslimden
alınıyor; AAC kendi kare-arası tepe noktalarını ekliyor. Tavanı tam aşım kadar geri
çekmek hedefi sınırın TAM ÜSTÜNE nişanlıyor, sonraki deneme yine kıl payı yukarıda
kapanıyor ve döngü üç denemede yakınsamıyor. Part 33 kanıtı: -0,9 dBTP, yani sınırın
0,1 dB üstünde takılı kalmış.

**Yapılacak.** Geri çekmeye emniyet marjı ekle: `limiter_db -= (overshoot + margin)`,
`margin >= 0.2` dB, ve deneme başına asgari adım 0,3 dB olsun ki sıfıra yakın aşımlarda
döngü yerinde saymasın. Kümülatif geri çekme için tavan koy (LUFS kapısı zaten
`abs(delivered - target_i) <= 1.0` diye koruyor; marj bunu bozmamalı).

**DEĞİŞMEYECEK.** Sözleşme hedefleri aynen kalır: `target_i=-14.0`, `target_tp=-1.0`.
Bu, REELYZE raporunun "ses ayarlarına dokunma" kuralına uyuyor: hedef değil,
hedefe VARMA yöntemi düzeltiliyor. `series/produce.py::_verify_audio_master`
içindeki `true_peak <= -1.0` kapısı da aynen kalır, fail-closed kalmaya devam eder.

**Done looks like.** 0,1 dB aşımla açılan bir teslim, üç denemenin içinde
-1,0 dBTP'nin ALTINDA kapanır ve entegre loudness -14 ± 1,0 LUFS içinde kalır.

**Proof.** `python -m pytest tests/test_master_true_peak.py tests/test_master_true_peak_adversarial.py tests/test_rocka_audio_master.py -q`
artı yeni `tests/test_master_true_peak_convergence.py`: sahte ölçüm dizisiyle
(deneme 1: -0,9 dBTP) döngünün ikinci denemede -1,0 altına indiğini ve
`RuntimeError` YÜKSELTMEDİĞİNİ doğrular. Sonra tam takım: `python -m pytest tests/ -q`.

---

### ROCK 1 , ilk-karede-okunur anomali kapısı (harcamadan ÖNCE)

**Kusur.** Zamana yayılan anomali (bitmeyen peçete, çoğalan sayfalar) plan
aşamasında hiçbir kapıdan geçmiyor; kredi harcandıktan ve video yayınlandıktan
SONRA ölçümle anlaşılıyor. Mevcut `require_first_frame` QC kapısı üretim
sonrasında çalışıyor, yani para çoktan yanmış oluyor.

**Yapılacak.** `series/shots.py` içinde:

1. `TEMPORAL_OVERREACH` sözlüğünü ölçülmüş katillerle genişlet. En az şunlar
   yakalanmalı: `endless`, `endlessly`, `never-ending`, `neverending`, `unending`,
   `infinite`, `infinitely`, `never runs out`, `never ends`, `replicate` (ve çekimleri),
   `duplicate` (ve çekimleri), `multiply` / `multiplying`, `refills itself`,
   `over and over`, `again and again`, `more and more`, `one after another`,
   `indefinitely`, `continuously`.
2. Bu kapıyı `format_plan_errors` içinde İKİ YENİ ALANA uygula:
   - `plan["episode"]["title"]`
   - `plan["object_card"]["anomaly_descriptor"]`
   Her ihlal, hangi alanda hangi ifadenin yakalandığını söyleyen açık bir
   hata satırı üretir.
3. Mevcut `violation_observation` uygulaması AYNEN kalır.

**Yanlış pozitif sınırı (Codex bunu ciddiye alsın).** Kapı YALNIZ başlık ve
`anomaly_descriptor` alanlarına uygulanır, çekim prompt'larına UYGULANMAZ.
Çekim prompt'unda "continues to pull" gibi ifadeler meşrudur ve
`shot 2 PROBE / shot 3 ESCALATION` akışının parçasıdır. Genişletilmiş
sözlüğün mevcut 803 testin hiçbirini kırmaması ve parts 22-31, 33-37 plan
dosyalarının HEPSİNİN kapıdan geçmesi zorunludur.

**impossible-continuity kararı (İhsan, 2026-09-10): KARANTİNA, idam DEĞİL.**
Aile `families` listesinde KALIR. Aileye özel kod YAZILMAZ. Kapı her aileye
eşit uygulanır; zamana bağlı fikir üreten continuity bölümleri doğal olarak
kapıdan geçemez, tek karede okunabilen bir continuity fikri geçebilir.
Gerekçe: n=2 ile aileyi kalıcı silmek erken, ve havuz daralması ikmali
çözülemez hale getirme riski taşıyor (bkz. bilinen risk: family kilidi).

**Sessiz kuyruk boşalmasına karşı (ZORUNLU).** Kapı bir toplu ikmal partisini
`min_queue` altına düşürürse koşu SESSİZ YEŞİL DÖNMEZ. `series/replenish.py`
içindeki mevcut alarm yolu (`_alert`) tetiklenir ve mesaj kaç bölümün hangi
kapıdan düştüğünü söyler. Bu kuralın testi yazılmadan rock bitmiş sayılmaz.

**Done looks like.** Part 32'nin gerçek plan JSON'u (`sentinal_ihsan/unnatural-lab/plans/part32.json`)
kapıdan GEÇEMEZ; part 31 ve part 27 GEÇER; mevcut takım yeşil kalır.

**Proof.** Yeni `tests/test_first_frame_readable_gate.py`:
gerçek part32.json'u yükleyip en az bir hata satırı bekler (hem başlıktan hem
`anomaly_descriptor`'dan), part31.json ve part27.json'un sıfır hata verdiğini
doğrular, ve genişletilmiş sözlüğün çekim prompt'larına uygulanmadığını gösterir.
Artı kuyruk-boşalma alarmı testi. Sonra `python -m pytest tests/ -q`.

---

### ROCK 2 , title_patterns'ı bu kanala tak

**Kusur.** Başlık kalıbı bu kanalda yalnız serbest metin talimatı
(`auto_replenish.title_style`) ile tarif edilmiş. Motor bunu zorlayamıyor;
üretici modelin kalıba uyup uymadığı ölçülmüyor. Kalıp dışına çıkan başlık
part 19'da yayına çıktı.

**Yapılacak.** `sentinal_ihsan/unnatural-lab/series.json` içindeki `auto_replenish`
bloğuna `title_patterns` ekle. Kullanılan üç kalıbın regex karşılığı yazılır,
her biri kanonik `families` listesinden izin verilen ailelerle eşlenir.
`title_style` serbest metni SİLİNMEZ, üretici için yönlendirme olarak kalır;
`title_patterns` onun makine tarafından zorlanan karşılığıdır.

Regex'ler `re.fullmatch` ile çalışır (motorun mevcut davranışı) ve 75 karakter
üst sınırıyla tutarlı olmalıdır.

**Bu rock'ın SINIRI, açıkça yazıyorum.** `title_patterns` part 32'yi
YAKALAYAMAZ; `This NAPKIN Never ENDS!` kalıp 2'ye biçimsel olarak uyar.
Onu ROCK 1 yakalar. Bu rock yalnız BİÇİM kaçağını kapatır, ANLAM kaçağını değil.
İkisini birbirinin yerine sayma.

**Done looks like.** Part 22'den 37'ye kadar üretilmiş her başlık kapıdan geçer;
part 19'un başlığı ve uydurulmuş kalıp dışı başlıklar reddedilir;
`validate_replenish_config` yeni config için sıfır hata döner.

**Proof.** Yeni `tests/test_unnatural_lab_title_patterns.py`: gerçek `series.json`
config'ini okur, `validate_replenish_config` temiz döner, parts 22-37 plan
dosyalarındaki başlıkların hepsi fullmatch sağlar, part 19 başlığı ve en az üç
uydurma kalıp dışı başlık reddedilir. Sonra `python -m pytest tests/ -q`.

---

### ROCK 5 , UNKNOWN başarısızlığın kanıtını kaybetme

**Kusur.** `series/series_runner.py` sınıflandıramadığı başarısızlığa güvenli
varsayılan olarak `UNKNOWN` veriyor ve part kaydına "üretim nedeni bilinmiyor"
yazıyor (part 30 böyle öldü). Operatöre hiçbir iz kalmıyor; bölüm ölü,
teşhis imkânsız.

**Yapılacak.** Sınıflandırma başarısız olduğunda kanıt KAYBEDİLMEZ:
ham başarısızlık ayrıntısı (istisna tipi ve mesajı, son boru hattı aşaması,
varsa alt süreç çıkış kodu) part kaydına ve alarm mesajına yazılır.
`UNKNOWN` kodu KALIR (yeniden denenebilirlik davranışı değişmez);
değişen tek şey, yanına iz düşülmesidir.

**Sınır.** Yeni bir sınıflandırma motoru YAZILMAZ. Sebep kodu kümesi
(`CONTENT_REJECT`, `BUDGET_EXHAUSTED`, `TRANSIENT_INFRA`, `UNKNOWN`) genişletilmez.
Kişisel veri ya da API anahtarı loglanmaz; mesaj kırpılır (üst sınır belirle,
örneğin 500 karakter).

**Done looks like.** Sınıflandırılamayan bir başarısızlık, part kaydında
okunabilir bir `failure_detail` bırakır ve alarm mesajı bu ayrıntıyı içerir.

**Proof.** Yeni `tests/test_unknown_failure_evidence.py`: sınıflandırılamayan
sahte bir başarısızlık üretir, part kaydında ayrıntının durduğunu ve alarma
düştüğünü, kırpma sınırının uygulandığını doğrular. Sonra `python -m pytest tests/ -q`.

---

### ROCK 4 (EN SON, en riskli) , bütçe tabanı rezervasyonu

**Kusur.** Bölüm bütçesi tek bir havuz. Başarısız denemeler bu havuzdan
harcıyor; kalan miktar tamamlanma tabanının (400 kredi) altına düşünce kapı
bölümü terk ediyor. Sonuç: kredi harcanmış, video yok. Üç bölüm böyle öldü
(25, 26, 28), part 26'da 1000 kredinin 932'si karşılıksız yandı.

**Yapılacak.** Tamamlanma tabanını bölümün İLK harcamasından önce REZERVE et.
Denemeler yalnız isteğe bağlı kalandan (tavan eksi taban) harcayabilir.
İsteğe bağlı kısım tükendiğinde koşu, tabanı YAKMADAN önce durur; rezerve
edilmiş taban bölümün teslimine ayrılmış kalır.

**Sert sınırlar (Codex bunları aşarsa rock reddedilir).**
- `credits_ledger.json` şeması ve durable defter davranışı DEĞİŞMEZ.
  Gerçek harcama kaydı olduğu gibi korunur.
- `kie_reservations.json` / `balance_floor` mekanizmasının koşular arası
  paylaşım sorunu BU ROCK'IN KAPSAMINDA DEĞİLDİR (bilinen açık madde,
  `ISSUES.md` içinde duruyor). Rezervasyon tek bölümün bütçe zarfı içinde kalır.
- Kredi tavanı değerlerine (`credit_hard_cap_value`, `credit_monthly_cap_value`)
  DOKUNULMAZ. Bunlar İhsan'ın kararı.
- Kapı fail-closed kalır: rezervasyon mekanizması belirsizse harcamaya İZİN VERMEZ.

**Done looks like.** Denemeleri tavanın isteğe bağlı kısmını tüketen bir bölüm,
tamamlanma tabanı hâlâ elindeyken durur; "kalan < asgari" durumu artık
harcama SONRASI keşfedilen bir sürpriz değil, harcama ÖNCESİ uygulanan bir kural olur.

**Proof.** Yeni `tests/test_budget_floor_reservation.py`: bir bölümün
denemelerinin isteğe bağlı kısmı tükettiği senaryoyu kurar, tabanın
harcanmadığını ve bölümün `budget_exhausted` ile TERK EDİLMEDİĞİNİ doğrular.
Mevcut `tests/test_credit_gate.py` ve `tests/test_rock1_budget_and_qcskip.py`
yeşil kalmalı. Sonra `python -m pytest tests/ -q`.

---

## 2. Bu planın DOKUNMADIĞI şeyler

REELYZE raporunun "neye dokunma" listesi aynen geçerli:

- Ses hedefleri: -14 LUFS, -1,0 dBTP. ROCK 3 hedefe VARMA yöntemini düzeltir,
  hedefi değil.
- `bible.json` içindeki formül, QC talimatı, art_style, karakter, ortamlar.
- `auto_replenish.brief` metni. Kapılar brief'i değiştirerek değil, üretilen
  planı doğrulayarak çalışır.
- Ortak motorun diğer kanallara bakan davranışı. ROCK 1, 3, 4, 5 paylaşılan
  kodda; hiçbiri diğer üç kanalın mevcut davranışını değiştirmemeli
  (803 testin yeşil kalması bunun kanıtıdır).
- Kesme sayısı ve plan süresi. Rapor "A/B testi yapmadan kesme ekleme" diyor;
  bu planda kesme ile ilgili hiçbir değişiklik YOK.
- Yayınlanmış bölümlerin durum dosyaları. Part 33'ün `qc_retry` kaydına
  elle dokunulmaz; ROCK 3 düzelttikten sonra sıradaki koşu onu kendi
  yeniden dener.

## 3. Ertelenenler (ISSUES listesine)

- 16 sn mi 22 sn mi sorusu: kasıtlı süre A/B testi ister, bu çevrimde yok.
- Diğer üç kanala ses ayarı yayılması: rapor öneriyor, ayrı iş.
- `reversed-physics` (616) ve `slightly-uncanny` (495) ailelerinin düşük
  medyanları: n=1, karar için yetersiz. Calibration'ın boost/explore
  mekanizması zaten çalışıyor.
- Parts 23 ve 24'ün neden `skipped` olduğu: iz yok, ROCK 5 bundan sonrası
  için iz bırakacak.
