# RF-PLAN: Kanca kapıları ve yayın hattı onarımı (unnatural-lab)

Tarih: 2026-09-10 (Los Angeles)
Kaynak analiz: `sentinal_ihsan/REELYZE-RAPOR.md`
Kanal: `sentinal_ihsan` / seri `unnatural-lab`
Revizyon: v2, Same Page turu 1 sonrası (Codex 23 bulgu, verdict NOT YET)

## CORE FOCUS

Çalışan formülü bozmadan iki şeyi garanti altına al: ölçülmüş biçimde ölü olan
bölüm fikirleri para harcanmadan ÖNCE reddedilsin, ve üretilmiş bölümler
yayına çıkmadan yolda ölmesin.

---

## 0. Ölçüm tabanı

### 0.1 Aile başına performans

Kaynak: `sentinal_ihsan/unnatural-lab/calibration.json`, anlık görüntü 2026-09-06.

| Aile | n | Medyan |
|---|---|---|
| impossible-state-change | 3 | 1295 |
| impossible-interior | 2 | 1196 |
| impossible-material | 2 | 1161 |
| impossible-behaviour | 3 | 1136 |
| reversed-physics | 1 | 616 |
| slightly-uncanny | 1 | 495 |
| impossible-continuity | **1** | **79** |

**Alıntı düzeltmesi (Codex turu 1, bulgu 1).** Bu anlık görüntüde continuity
ailesinde YALNIZ part 19 var, n=1. İkinci continuity bölümü part 32
(`This NAPKIN Never ENDS!`, 8 Eylül'de yayınlandı, 146 izlenme) anlık görüntüden
SONRA yayınlandı ve sayısı REELYZE raporundan geliyor, calibration.json'dan değil.
Birleşik veri seti n=2'dir ve iki farklı kaynaktan derlenmiştir.

### 0.2 Rapora itiraz, sınırlandırılmış hâliyle

REELYZE raporu part 19'u (82 izlenme) "I Found... kalıbı sabır istiyor" diye
açıklıyor. Aynı kalıbı kullanan 7 bölümün metrikleri: 801 / 74 / 2554 / 1285 /
1127 / 1202 / 79.

**Bu veri şunu çürütür:** başlık kalıbı part 19'un TEK açıklaması olamaz.
**Bu veri şunu KANITLAMAZ** (Codex turu 1, bulgu 2): başlık biçiminin nötr
olduğunu, ya da continuity ailesinin tek sebep olduğunu. Yedi sonuç da
karıştırıcı değişkenlerle dolu (yaş, aile, obje, dönem).

Bu planın operasyonel sonucu bu yüzden şudur: kapı başlık BİÇİMİNE değil,
anomalinin tek karede okunup okunamadığına kurulur. Bu, iki hipotezden
hangisinin doğru olduğuna bağlı olmayan bir seçimdir, çünkü ikisi de aynı
yöne işaret ediyor. Başlık biçimi kapısı ayrıca kurulur (ROCK C) ama
ondan performans iddiası TÜRETİLMEZ.

### 0.3 Motorda var olan ama bu kanalda takılı olmayan parçalar

- `series/replenish.py::_compiled_title_patterns` + `validate_plan_against_config`:
  `title_patterns` (regex + izinli aile) tam bir başlık kapısı, test edilmiş.
  `unnatural-lab` config'inde bu anahtar YOK.
- `series/shots.py::TEMPORAL_OVERREACH`: `never|always|forever|eventually`,
  YALNIZ `shot.violation_observation` alanına uygulanıyor (shots.py:150).
  `episode.title` ve `object_card.anomaly_descriptor` hiç taranmıyor.

### 0.4 Yayın hattı gerçeği, TAM sayım

Kaynak: `series.json` parts sözlüğü, `published.json`. **Düzeltme (Codex bulgu 3):**
önceki sürüm 10 diyip 7 satır listelemişti. Tam liste:

| Part | Durum | Sebep |
|---|---|---|
| 1, 2 | rejected | |
| 5 | `series.json`'da published, ama `published.json`'da youtube id NULL | iki kaynak çelişiyor |
| 23, 24 | skipped | iz yok |
| 25 | budget_exhausted | kalan=364, asgari=400 |
| 26 | budget_exhausted | kalan=68, asgari=400 |
| 28 | budget_exhausted | kalan=320, asgari=400 |
| 30 | needs_human | reason_code=UNKNOWN, "üretim nedeni bilinmiyor" |
| 33 | qc_retry, ŞU AN TIKALI | master true-peak -0,9 dBTP > -1,0 |

33 bölümün 23'ü YouTube'a ulaştı. `last_run.json`: 2026-09-09 koşusu `failure`.

**Karşılıksız yanan kredi** (`credits_ledger.json`, `episode_spend`):
part 25 = 436, part 26 = 932, part 28 = 680, part 30 = 848. Toplam **2.896 kredi,
yaklaşık 14,50 dolar, çıktı sıfır.** Part 33'te 596 harcanmış, tavana 404 kalmış.

### 0.5 Aday kapı kuralının ölçümü (bu planın en önemli tek verisi)

Turu 1'de Codex, kelime kara listesinin ilk-kare okunurluğunu ölçmediğini
söyledi (bulgu 4) ve haklı çıktı. İlk taslaktaki liste part 37'yi
(`Something Is WRONG With This TEA BAG`, `impossible-interior`, medyan 1196)
"infinitely deep" yüzünden reddediyordu. Oradaki "infinitely" UZAMSAL,
zamansal değil; shot 1 gözlemi "kesilmiş poşetin içinde minik canlı bir manzara
görünüyor" diyor, yani anomali tek karede okunuyor. Kural çalışan bir bölümü
öldürecekti.

Kural yeniden tasarlandı ve 25 gerçek plan dosyası üzerinde ölçüldü:

| Bölüm | Sonuç | Yakalayan |
|---|---|---|
| part 19 (82 izlenme, ölü) | RED | başlık: `REPLICATE` |
| part 32 (146 izlenme, ölü) | RED | başlık: `Never`, anomali: `endless` |
| part 36 (kuyrukta, aynı kusur) | RED | anomali: `always`, shot1 gözlem: `After being` |
| part 37 ve diğer 21 bölüm | GEÇER | , |

Ölçülmüş iki ölünün ikisi de yakalanıyor, yanlış pozitif yok.
`infinite` ve `infinitely` kelimeleri listeden ÇIKARILDI (part 37 kanıtı).

---

## 1. Rock listesi

Beş rock, bağımlılık sırasında. Ortak kanıt: `python -m pytest tests/ -q`
(taban: 803 passed + 188 subtest, ~35 sn), PATH'teki Python 3.12 ile.
Depo kökündeki `.venv` içinde pytest YOKTUR, onu kullanma.

---

### ROCK A , master true-peak yakınsaması

**Kusur.** `core/ffmpeg_tools.py::master_audio` her başarısız denemede limiter
tavanını tam aşım kadar geri çekiyor (`limiter_db -= overshoot`). Marj yok,
yani hedef sınırın tam üstüne nişanlanıyor. Limiter AAC kodlamasından ÖNCE
uygulanıyor, ölçüm kodlanmış teslimden alınıyor.

**Kanıt durumu, dürüstçe (Codex bulgu 13).** Elimizdeki tek gözlem part 33'ün
YUVARLANMIŞ son sonucu: -0,9 dBTP. Deneme düzeyi telemetri başarısızlıkta
SİLİNİYOR, yani "AAC kare-arası tepe ekliyor" mekanizması şu an bir ÇIKARIM,
ölçülmüş bir gerçek değil. Bu rock önce kanıtı korur, sonra düzeltir.

**Yapılacak, sırayla:**
1. Başarısızlık yolunda deneme düzeyi meta veriyi KORU: her denemenin
   limiter tavanı, ölçülen true-peak ve LUFS değeri, `RuntimeError` yükselmeden
   önce diske yazılsın. Bu tek başına bir sonraki başarısızlığı teşhis edilebilir kılar.
2. Geri çekmeye emniyet marjı ekle: `limiter_db -= (overshoot + margin)`,
   `margin >= 0.2` dB, deneme başına ASGARİ hareket 0,3 dB.
3. Kümülatif geri çekme için AÇIK bir tavan tanımla (Codex bulgu 15).
   Malzeme zaten -15 LUFS civarındaysa fazla geri çekme entegre loudness
   kapısını (`abs(delivered - target_i) <= 1.0`) dışarı itebilir. Tavan
   belirlenecek ve sınır davranışı test edilecek.

**DEĞİŞMEZ.** `target_i=-14.0`, `target_tp=-1.0` ve
`series/produce.py::_verify_audio_master` içindeki `true_peak <= -1.0`
fail-closed kapısı aynen kalır. REELYZE raporunun "ses ayarlarına dokunma"
kuralı korunuyor: hedef değil, hedefe varma yöntemi düzeltiliyor.

**Bu rock part 33'ü TEK BAŞINA KURTARMAZ (Codex bulgu 16).** Part 33'ün
üretilmiş medyası kalıcı değil ve defterde 596/1000 kredisi yanmış, geriye
404 kalmış; taze bir koşunun dört ana çekimi yaklaşık 400 kredi istiyor.
Yani part 33'ün yeniden denenmesi ayrı bir BÜTÇE KARARI gerektirir.
Bu karar İhsan'a aittir ve bu rock'ın kapsamı DIŞINDADIR.

**Proof (Codex bulgu 14 sonrası sertleştirildi).** Sahte ölçüm dizisi TEK BAŞINA
yeterli DEĞİLDİR: ikinci ölçümü limiter ayarından bağımsız olarak geçiren bir
mock, DÜZELTİLMEMİŞ kodu da yeşil gösterir. Yeni
`tests/test_master_true_peak_convergence.py` şunları doğrular:
(a) limiter tavanının denemeler arasında en az 0,3 dB HAREKET ETTİĞİ,
   doğrudan filtre dizesinden okunarak;
(b) gerçek AAC ile üretilmiş, 0,1 dB aşımla açılan bir ses malzemesinde
   döngünün üç denemenin içinde -1,0 dBTP altında kapandığı;
(c) -15 LUFS sınır malzemesinde loudness kapısının dışarı itilmediği;
(d) tekrarlı aşımda kümülatif tavana çarpınca davranışın tanımlı olduğu.
Artı mevcut `tests/test_master_true_peak.py`,
`tests/test_master_true_peak_adversarial.py`, `tests/test_rocka_audio_master.py`
yeşil kalır. Sonra tam takım.

---

### ROCK B , ilk-karede-okunur anomali kapısı (harcamadan ÖNCE)

**Kusur.** Zamana ya da önceki bir olaya bağlı anomali plan aşamasında hiçbir
kapıdan geçmiyor; kredi harcanıp video yayınlandıktan SONRA ölçümle anlaşılıyor.
Mevcut `require_first_frame` QC kapısı üretim SONRASINDA çalışıyor.

**Kural, iki parça.** Bölüm 0.5'te 25 gerçek plan üzerinde ölçüldü.

1. **SINIRSIZ NİCELİK** (uygulanır: `episode.title`,
   `object_card.anomaly_descriptor`, `shots[0].violation_observation`):
   `never`, `always`, `forever`, `eventually`, `endless`, `endlessly`,
   `never-ending`, `neverending`, `unending`, `unbounded`, `over and over`,
   `again and again`, `more and more`, `one after another`, `replicat*`,
   `duplicat*`, `multiplies`, `multiplying`, `refills itself`, `indefinitely`.
2. **ÖNCEKİ OLAYA BAĞLILIK** (uygulanır: YALNIZ `shots[0].violation_observation`):
   `after being|it|the|each|every`, satır başında `after`, `once it|the|they`,
   `having been`, `each time`, `every time`, `regardless of`, `keeps <fiil>ing`.

**Listede OLMAYANLAR ve neden.** `infinite` / `infinitely`: part 37 kanıtı,
uzamsal kullanım meşru ve o aile 1196 medyanlı. `continuous` / `continuously`:
kesintisiz bir BİÇİMİ tarif edebilir, yanlış pozitif riski ölçülmedi.

**Uygulama sınırı, önemli (Codex bulgu 6).** Paylaşılan
`series/shots.py::TEMPORAL_OVERREACH` regex'i DEĞİŞTİRİLMEZ. Onu genişletmek
dört kanalın hepsinde `violation_observation` davranışını sessizce değiştirir.
Bunun yerine `tek-obje-4x6` formatına ait AYRI, opt-in bir regex çifti eklenir
ve yalnız `format_plan_errors` içinden, yalnız o format için çalışır.
Diğer serilerin bugünkü davranışı bit düzeyinde aynı kalır.

**Kapı çekim prompt'larına UYGULANMAZ.** Çekim prompt'unda "continues to pull"
gibi ifadeler meşrudur ve `shot 2 PROBE / shot 3 ESCALATION` akışının parçasıdır.

**Onarım talimatı tek kaynaktan türetilir (Codex bulgu 7).**
`series/replenish.py::_OBSERVATION_RULE` bugün yasak kelimeleri elle sayıyor
("never, always, forever, eventually", satır 1471-1475). Yeni sözlük eklenince
bu metin bayatlar ve onarım çağrısı yeni yasaklı kelimeyi üretip sınırlı onarım
bütçesini boşa harcar. Talimat metni doğrulayıcının sözlüğünden ÜRETİLİR,
elle yazılmaz.

**impossible-continuity kararı (İhsan, 2026-09-10): KARANTİNA, idam DEĞİL.**
Aile `families` listesinde KALIR, aileye özel kod YAZILMAZ. Kapı her aileye
eşit uygulanır. Ölçüm bunun neden doğru olduğunu gösteriyor: kapı part 36'yı
(`impossible-behaviour`, sağlıklı aile) yakalıyor ve part 37'yi
(`impossible-interior`) geçiriyor. Yani kusur ailede değil, fikrin
zaman bağımlılığında.

**Kuyruk yönetimi (Codex bulgu 8, ROCK D'ye bağımlı).** Kapı, ZATEN KUYRUKTA
olan part 36'yı reddedecek. Bugün üretim sırasında reddedilen bir plan
sınıflandırılmamış `UNKNOWN` başarısızlığa dönüşüp AYNI dosyayı yeniden
deniyor, yani sonsuz döngü. ROCK D bunu tipli `CONTENT_REJECT`'e çevirir.
ROCK B, ROCK D olmadan devreye ALINMAZ.

**Silent-shrink alt maddesi KALDIRILDI (Codex bulgu 9, KILL kabul edildi).**
Mevcut kısmi-parti alarm yolu ve sıfır-önek istisnası bu işi zaten yapıyor
(`tests/test_replenish_partial_batch.py`). Yeni mekanizma yazılmaz; var olan
alarmın yüküne kaç bölümün hangi kapıdan düştüğü EKLENİR, o kadar.

**Done looks like.** Bölüm 0.5 tablosu birebir çıkar: 19, 32, 36 reddedilir;
diğer 22 bölüm geçer; mevcut 803 test yeşil kalır; diğer üç kanalın plan
doğrulama davranışı değişmez.

**Proof.** Yeni `tests/test_first_frame_readable_gate.py`, gerçek plan
dosyalarıyla: part 19, 32, 36 için hangi ALANDA hangi ifadeden düştüğünü
alan adıyla doğrular; part 37 dahil diğer 22 bölümün sıfır hata verdiğini
doğrular; kapının çekim prompt'larına uygulanmadığını gösterir; paylaşılan
`TEMPORAL_OVERREACH` sabitinin DEĞİŞMEDİĞİNİ ve `tek-obje-4x6` olmayan bir
planın etkilenmediğini doğrular; onarım talimatının sözlükten türediğini
doğrular. Sonra tam takım.

---

### ROCK C , title_patterns'ı bu kanala tak

**Kusur.** Başlık kalıbı yalnız serbest metin talimatıyla tarif edilmiş,
motor zorlamıyor.

**Yapılacak.** `sentinal_ihsan/unnatural-lab/series.json` içindeki
`auto_replenish` bloğuna `title_patterns` ekle. Üç kalıp, `re.fullmatch` ile.
Kalıp 3 hem tekil hem çoğul özneyi kabul etmeli: part 36 başlığı
`Why Won't These DICE Change Their Number?` (Codex bulgu 10).

**Karakter üst sınırı 60'a hizalanır (Codex bulgu 11).** `replenish.py:1093`
şu an `len(title) > 60` uyguluyor, ama `auto_replenish.title_style` metni
"Max 75 characters" diyor. Bu mevcut ve sessiz bir çelişki; en uzun gerçek
başlık 41 karakter olduğu için bugüne kadar ısırmadı. Sözleşme 60'ta
birleştirilir ve `title_style` metnindeki 75 sayısı 60 yapılır.
Bu, brief'in TEK bir sayısına dokunmaktır, formüle dokunmak değildir;
bilerek ve açıkça yapılıyor.

**Bu rock'ın SINIRI.** `title_patterns` part 32'yi YAKALAYAMAZ;
`This NAPKIN Never ENDS!` kalıp 2'ye biçimsel olarak uyar. Onu ROCK B yakalar.
Bu rock yalnız BİÇİM kaçağını kapatır. Bu rock'tan performans iddiası
türetilmez (bölüm 0.2).

**Proof.** Yeni `tests/test_unnatural_lab_title_patterns.py`:
`validate_replenish_config` gerçek config için sıfır hata döner;
parts 22-37 başlıklarının hepsi fullmatch sağlar; part 19 başlığı reddedilir;
her kalıbın POZİTİF sınırı ve yakın-eşleşen bozuk varyantları ayrı ayrı
test edilir; her kalıbın izin verilmeyen aile eşleşmesi ayrı ayrı doğrulanır
(Codex bulgu 12: hepsine-izin-veren eşleme anlamsızdır); 60 ve 61 karakterlik
sınır başlıkları test edilir. Sonra tam takım.

---

### ROCK D , kapıdan düşen planın tipli reddi (ROCK B'nin ön koşulu)

**Kusur.** Üretim sırasında reddedilen bir plan bugün sınıflandırılmamış
`UNKNOWN` başarısızlığa düşüyor ve DEĞİŞMEMİŞ dosyayı yeniden deniyor.
Part 30 böyle öldü (defterde 848 kredi). ROCK B devreye girince part 36
aynı kuyuya düşer.

**Yapılacak, dar kapsam.** İçerik kapısından düşen bir plan
`CONTENT_REJECT` sebep koduyla, düşüren ALAN ve İFADE kaydedilerek reddedilir,
ve kuyruk aynı dosyayı sonsuza kadar yeniden denemek yerine tanımlı bir
şekilde ilerler ya da bölümü değiştirir. Alarm mesajı hangi bölümün hangi
kapıdan düştüğünü söyler.

**Sızıntı koruması (Codex bulgu 22).** Ham istisna metnini 500 karaktere
kırpmak API anahtarı, imzalı URL ya da kişisel veri sızmasını ENGELLEMEZ.
Kaydedilen şey izin listeli, YAPILANDIRILMIŞ bir kayıttır (alan adı,
yakalanan ifade, kural adı), serbest metin değil.

**Kapsam DIŞI, ISSUES'a gidiyor (Codex bulgu 21).** `series/produce.py`
içindeki birçok dal hatayı yutup `None` döndürüyor; genel tipli hata kanıtı
altyapısı bu çevrimde YAPILMIYOR. Bu rock yalnız İÇERİK REDDİ yolunu tipler.

**Proof.** Yeni `tests/test_content_reject_lifecycle.py`: ROCK B kapısından
düşen bir planın `CONTENT_REJECT` kodu ürettiğini, aynı dosyanın sonsuz
yeniden denenmediğini, alarma düştüğünü ve kaydın yapılandırılmış olup ham
istisna metni İÇERMEDİĞİNİ doğrular. Sonra tam takım.

---

### ROCK E (EN SON, EN RİSKLİ) , koşu sınırında kaybolan üretim

**ROCK 4 (bütçe tabanı rezervasyonu) KALDIRILDI.** Codex turu 1, bulgu 17
haklı ve doğrulandı: `series/critic.py::CapAwareRegenAllocator` (satır 1085)
zaten "her henüz-yetkilendirilmemiş ana çekimi koruyor". Benim önerdiğim
rezervasyon bu korumanın kopyasıydı ve gerçek kaybı ıskalıyordu.

**Gerçek kusur.** Koruma TEK KOŞU içinde çalışıyor. Kabul edilmiş çekimler
koşu sınırını GEÇMİYOR: koşu ölünce üretilmiş her şey kayboluyor, sonraki
koşu sıfırdan üretiyor, ama kalıcı defter (`credits_ledger.json`,
`episode_spend`) aynı bölüm için saymaya DEVAM ediyor. Bu yüzden bölüm
tavanı, hiç video çıkmadan doluyor. Ölçülen sonuç: part 26'da 932/1000,
part 30'da 848/1000, part 25'te 436, part 28'de 680. Toplam 2.896 kredi,
karşılığı sıfır.

Codex bulgu 23 aynı kökü yayın ucunda gösteriyor: başarısız bir yükleme
geçici bir yerel yol kaydedip false dönüyor, sonraki GitHub koşusu yeniden
ÜRETİYOR, yükleme yeniden DENENMİYOR. `core/video_vault.py` içinde
kalıcı bir kasa sınıfı var ama `series/` boru hattında HİÇ kullanılmıyor
(doğrulandı: seri kodunda tek bir referans yok).

**Yapılacak, asgari kapsam.** Kabul edilmiş bölüm eserleri (çekim çıktıları
ve doğrulanmış master) `seri:bölüm` anahtarıyla kalıcı hale getirilir;
yeniden deneme onları YENİDEN ÜRETMEK yerine KULLANIR. Yükleme başarısız
olduğunda bir sonraki koşu yalnız yüklemeyi tekrarlar, üretimi değil,
ve mükerrer yayın kapısı (`tests/test_publish_duplicate_gate.py`) korunur.

**Sert sınırlar.**
- `credits_ledger.json` şeması ve durable defter davranışı DEĞİŞMEZ.
- Kredi tavanı değerlerine (`credit_hard_cap_value`,
  `credit_monthly_cap_value`) DOKUNULMAZ, bunlar İhsan'ın kararı.
- `kie_reservations.json` / `balance_floor` koşular arası paylaşım sorunu
  bu rock'ın kapsamı DIŞINDADIR (`ISSUES.md` içinde duran açık madde).
- Kapı fail-closed kalır: kalıcı eserin bütünlüğü doğrulanamıyorsa
  yeniden kullanılmaz, üretilir.

**Proof (Codex bulgu 19 sonrası sertleştirildi).** "budget_exhausted almadı"
YETERLİ DEĞİLDİR; bölüm hiç video üretmeden ya da `qc_retry` döngüsünde
dönerek de o testi geçer. Yeni `tests/test_durable_episode_recovery.py`:
üretimi yarıda ölen bir bölümün, ikinci koşuda kabul edilmiş çekimleri
YENİDEN ÜRETMEDEN tamamladığını ve tavanı aşmadığını uçtan uca doğrular;
başarısız yüklemenin sonraki koşuda üretimi değil YALNIZ yüklemeyi
tekrarladığını doğrular; mükerrer yayın kapısının hâlâ tuttuğunu doğrular.
Mevcut `tests/test_credit_gate.py`, `tests/test_rock1_budget_and_qcskip.py`,
`tests/test_publish_duplicate_gate.py`, `tests/test_hold_recovery.py`
yeşil kalır. Sonra tam takım.

---

## 2. Bu planın DOKUNMADIĞI şeyler

- Ses hedefleri: -14 LUFS, -1,0 dBTP. ROCK A hedefe VARMA yöntemini düzeltir.
- `bible.json`: formül, QC talimatı, art_style, karakter, ortamlar.
- `auto_replenish.brief` metni. TEK istisna, açıkça: ROCK C içindeki
  75 -> 60 karakter sayı düzeltmesi.
- Kesme sayısı ve plan süresi. Rapor A/B testi olmadan kesme eklemeyin diyor;
  bu planda kesme ile ilgili hiçbir değişiklik yok.
- Yayınlanmış bölümlerin durum dosyaları. Part 33'ün `qc_retry` kaydına
  elle dokunulmaz.
- Diğer üç kanalın davranışı. ROCK B açıkça format-kapsamlı yazılıyor;
  803 testin yeşil kalması bunun kanıtıdır.

## 3. İHSAN KARARI BEKLEYEN (build sırasında sorulacak)

- **Part 33'ün bütçesi.** Defterde 596/1000 yanmış, 404 kalmış, taze koşu
  yaklaşık 400 istiyor. Yeniden denensin mi, tavanı bir kereliğine
  yükseltilsin mi, yoksa bölüm terk mi edilsin? ROCK A bunu kendi başına
  çözmez.

## 4. ISSUES listesine ertelenenler

- `series/produce.py` genelinde tipli hata kanıtı (Codex bulgu 21):
  birçok dal hatayı yutup `None` döndürüyor.
- Part 5'in iki kaynak arasındaki çelişkisi (`series.json` published,
  `published.json` youtube id null) ve parts 23-24'ün izsiz `skipped` durumu.
- `balance_floor` / `kie_reservations.json` koşular arası paylaşımı.
- 16 sn mi 22 sn mi: kasıtlı süre A/B testi ister.
- Diğer üç kanala ses ayarı yayılması.
- `reversed-physics` (616) ve `slightly-uncanny` (495) düşük medyanları:
  n=1, karar için yetersiz. Calibration boost/explore mekanizması çalışıyor.
- Part 20 (`This BRUSH Is NOT Supposed To HUM?!`, 498) ses-anomalisi vakası:
  brief zaten yalnız-sesle-anlaşılan ihlali yasaklıyor, ama kapı yok.
