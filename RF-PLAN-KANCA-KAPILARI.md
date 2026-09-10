# RF-PLAN: Kanca kapıları ve yayın hattı onarımı (unnatural-lab)

Tarih: 2026-09-10 (Los Angeles)
Kaynak analiz: `sentinal_ihsan/REELYZE-RAPOR.md`
Kanal: `sentinal_ihsan` / seri `unnatural-lab`
Revizyon: v3, Same Page turu 2 sonrası (Codex turu 1: 23 bulgu, turu 2: 20 bulgu)

## CORE FOCUS

Çalışan formülü bozmadan iki şeyi garanti altına al: ilk karede okunamayacağı
YAPISAL olarak belli olan bölüm fikirleri para harcanmadan ÖNCE reddedilsin,
ve üretilmiş bölümler yayına çıkmadan yolda ölmesin.

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
| impossible-continuity | 1 | 79 |

Bu anlık görüntüde continuity ailesinde yalnız part 19 var (n=1). İkinci
continuity bölümü part 32 (`This NAPKIN Never ENDS!`, 146 izlenme) anlık
görüntüden sonra yayınlandı ve sayısı REELYZE raporundan geliyor.

### 0.2 Rapora itiraz, sınırlandırılmış hâliyle

Rapor part 19'u (82) "I Found... kalıbı sabır istiyor" diye açıklıyor.
Aynı kalıbı kullanan 7 bölümün metrikleri: 801 / 74 / 2554 / 1285 / 1127 / 1202 / 79.
Bu veri başlık kalıbını TEK açıklama olmaktan çıkarır; başlık biçiminin nötr
olduğunu ya da continuity ailesinin tek sebep olduğunu KANITLAMAZ.
Yedi sonucun hepsi karıştırıcı değişken taşıyor.

### 0.3 Kapı kuralının kanıt durumu, DÜRÜST HÂLİYLE

v2'de "25 plan üzerinde ölçüldü, sıfır yanlış pozitif" yazmıştım. Codex turu 2
bunu üç ayrı yerden çürüttü ve üçü de doğrulandı:

**(a) Kapı eski format bölümlerine hiç ulaşmıyor.** Parts 1-21 arasında
`format_version` yok, `object_card` yok, `violation_observation` yok
(doğrulandı: part 10, 19, 20 için `format_version: None`).
`series/shots.py::format_plan_errors` bu planlarda ilk satırda boş dönüyor.
Yani kapının GERÇEK kapsamı part 22 ve sonrasıdır. O kapsamda kapının
reddettiği ölçülmüş ölü bölüm sayısı **BİRDİR** (part 32, 146 izlenme).
Part 19 kapsam dışıdır; onun regex'e takılması üretim davranışı değildir.

**(b) Kelime listesinin 2.158 izlenmelik karşı örneği var.** Part 10
(`Can I Turn A BOTTLE Into A NEVER-ENDING FOUNTAIN?!`) kanalın en iyi ikinci
bölümü ve başlığında `NEVER-ENDING` geçiyor (calibration metriği 2158,
yaş 664 saat). Eski formatta olduğu için kapı ona dokunmazdı, ama
"bitmeyen anomali ölüdür" tezini ölçüm DESTEKLEMİYOR.

**(c) Kural boş alanla atlatılabiliyor.** `series/shots.py:142` şu an
`if observation is not None:` diyor; `violation_observation` tamamen opsiyonel.
Üreteç alanın red ürettiğini öğrenirse alanı yazmamayı öğrenir.

**Sonuç ve İHSAN KARARI (2026-09-10): sert red YALNIZ YAPISAL kurala uygulanır.**
- `violation_observation` bu formatta ZORUNLU hâle gelir; atlatma yolu kapanır.
- Reddeden tek kural, shot 1 gözleminin ÖNCEKİ BİR OLAYA bağlı olmasıdır.
  Bu bir zevk yargısı değil, ilk-kare okunurluğu hakkında yapısal bir olgudur:
  gözlem "After being rolled, the dice land..." diyorsa ilk kare o iddiayı
  gösteremez, çünkü iddia kendinden önceki bir olaya atıf yapıyor.
  Bu kuralın bütün derlemede karşı örneği YOKTUR.
- Sınırsız-nicelik kelime listesi REDDETMEZ, BAYRAK TAKAR: kaydedilir ve
  alarma düşer. Gerekçe: part 10 karşı örneği. Bayrak, 20 bölüm sonra
  "bayraklılar gerçekten düşük mü performe ediyor" sorusunu ölçülebilir kılar.

### 0.4 Kapının gerçek kapsamı ve çağrı yolları

Codex turu 2, bulgu 4 doğrulandı: `validate_plan_against_config`
`format_plan_errors`'ı HİÇ çağırmıyor. Kapı yalnız `validate_plan`
(`shots.py:432`, `shots.py:447`) üzerinden şu dört yerden görülür:

| Çağrı yeri | Görür mü |
|---|---|
| `series/replenish.py:1417` (`_validate_batch`) | EVET |
| `series/preflight.py:125` | EVET |
| `series/produce.py:1398` | EVET |
| `series/produce.py:1461` (referans sonrası) | EVET |
| `validate_plan_against_config` (doğrudan config doğrulama) | HAYIR |

Testler regex'i değil, BU ÇAĞRI YOLLARINI kanıtlamak zorundadır.

### 0.5 Yayın hattı gerçeği, tam sayım

Kaynak: `series.json` parts sözlüğü, `published.json`.

| Part | Durum | Sebep |
|---|---|---|
| 1, 2 | rejected | |
| 5 | `series.json` published, `published.json` youtube id NULL | iki kaynak çelişiyor |
| 23, 24 | skipped | iz yok |
| 25 | budget_exhausted | kalan=364, asgari=400 |
| 26 | budget_exhausted | kalan=68, asgari=400 |
| 28 | budget_exhausted | kalan=320, asgari=400 |
| 30 | needs_human | reason_code=UNKNOWN, "üretim nedeni bilinmiyor" |
| 33 | qc_retry, ŞU AN TIKALI | master true-peak -0,9 dBTP > -1,0 |

33 bölümün 23'ü YouTube'a ulaştı. `last_run.json`: 2026-09-09 koşusu `failure`.

**Karşılıksız yanan kredi** (`credits_ledger.json`, `episode_spend`):
part 25 = 436, part 26 = 932, part 28 = 680, part 30 = 848.
Toplam **2.896 kredi, yaklaşık 14,50 dolar, çıktı sıfır.**
Part 33'te 596 harcanmış, tavana 404 kalmış.

Bu tarafın kanıtı mekanik ve tartışmasızdır; içerik kapısının kanıtından
belirgin biçimde güçlüdür. Plan bu asimetriyi gizlemez.

---

## 1. Rock listesi

Beş rock. **Sıra: A, D, B, C, E.** (Codex turu 2, bulgu 7: D, B'nin sert
ön koşuludur, bu yüzden B'den önce gelir.) Ortak kanıt:
`python -m pytest tests/ -q` (taban: 803 passed + 188 subtest, ~35 sn),
PATH'teki Python 3.12 ile. Depo kökündeki `.venv` içinde pytest YOKTUR.

---

### ROCK A , master true-peak yakınsaması

**Kusur.** `core/ffmpeg_tools.py::master_audio` her başarısız denemede limiter
tavanını tam aşım kadar geri çekiyor (`limiter_db -= overshoot`), marj yok,
yani hedefi sınırın tam üstüne nişanlıyor.

**Kanıt durumu, dürüstçe.** Elimizdeki tek gözlem part 33'ün yuvarlanmış
son sonucu: -0,9 dBTP. Deneme düzeyi telemetri başarısızlıkta siliniyor.
"AAC kare-arası tepe ekliyor" bir ÇIKARIM, ölçüm değil.

**Yapılacak, sırayla:**
1. **Önce kanıtı koru.** Her denemenin limiter tavanı, ölçülen true-peak ve
   LUFS değeri `RuntimeError` yükselmeden önce KALICI bir yere yazılsın.
   Codex turu 2, bulgu 12: bugünkü geçici bölüm çıktısı klasörü YETMEZ,
   iş akışı yalnız logları ve stem'leri yüklüyor. Telemetri, başarısızlıktan
   sonra da okunabilen bir yere gitmeli ve bu test edilmeli.
2. Geri çekmeye emniyet marjı: `limiter_db -= (overshoot + margin)`,
   `margin >= 0.2` dB, deneme başına asgari hareket 0,3 dB.
3. **Kümülatif geri çekme sınırı AÇIKÇA tanımlanır** (turu 1 bulgu 15,
   turu 2 bulgu 13). Hem true-peak hem LUFS kapısını aynı anda sağlayan
   hiçbir limiter ayarının olmadığı malzeme MÜMKÜNDÜR. O durumda davranış
   "başarılı gibi yapmak" değil, TEŞHİS ÜRETEREK fail-closed durmaktır.
   Plan artık sınır-LUFS malzemesinde başarı VAAT ETMİYOR.

**DEĞİŞMEZ.** `target_i=-14.0`, `target_tp=-1.0` ve
`produce.py::_verify_audio_master` içindeki `true_peak <= -1.0` fail-closed
kapısı aynen kalır. REELYZE'nin "ses ayarlarına dokunma" kuralı korunuyor.

**Part 33'ü tek başına kurtarmaz.** Üretilmiş medyası kalıcı değil, defterde
596/1000 yanmış, 404 kalmış, taze koşu ~400 istiyor.

**Proof.** Yeni `tests/test_master_true_peak_convergence.py`:
(a) limiter tavanının denemeler arasında en az 0,3 dB HAREKET ETTİĞİ,
    doğrudan üretilen filtre dizesinden okunarak (turu 2 bulgu... mock
    ikinci ölçümü limiter'dan bağımsız verirse düzeltilmemiş kod da geçer);
(b) gerçek AAC ile üretilmiş, 0,1 dB aşımla açılan malzemede döngünün üç
    denemede -1,0 dBTP altında kapandığı;
(c) hiçbir ayarın iki kapıyı birden sağlamadığı malzemede fail-closed
    durulduğu ve teşhis çıktısının üretildiği;
(d) kümülatif sınıra çarpınca davranışın tanımlı olduğu;
(e) başarısızlık telemetrisinin kalıcı konumda HAYATTA KALDIĞI.
Mevcut `test_master_true_peak.py`, `test_master_true_peak_adversarial.py`,
`test_rocka_audio_master.py` yeşil kalır. Sonra tam takım.

---

### ROCK D , kapıdan düşen planın tipli reddi (ROCK B'nin ön koşulu)

**Kusur, kanıtlanmış hâliyle.** Codex turu 2, bulgu 8 haklı: part 30'un
`UNKNOWN` ile ölmesini plan reddine bağlamak KANITSIZDI ve "sonsuz döngü"
demem de yanlıştı; mevcut yaşam döngüsü üç denemeyle SINIRLI. Kanıtlanmış
olan tek şey şudur: sınıflandırılamayan başarısızlıkta hata ayrıntısı
KAYBOLUYOR ("üretim nedeni bilinmiyor") ve bölüm üç ÜCRETLİ üretim denemesi
tüketerek ölüyor (part 30 defterde 848 kredi).

**Yapılacak.** İçerik kapısından düşen bir plan `CONTENT_REJECT` sebep koduyla
ANINDA reddedilir; üç üretim denemesini TÜKETMEZ. Kayıt, hangi kuralın hangi
alanda hangi ifadeden düştüğünü söyler.

**Geçiş kararı (Codex turu 2, bulgu 9).** "İlerle ya da değiştir" belirsiz
bırakılmaz: mevcut atomik `terminalize-and-advance` yolu kullanılır ve alarm
üretilir. Kanıt, SONRAKİ geçerli bölümün hâlâ koşulabilir olduğunu doğrular;
bölümü belirsiz süre park etmek testi geçmiş sayılmaz.

**Sızıntı koruması.** Ham istisna metni 500 karaktere kırpmak API anahtarı,
imzalı URL ya da kişisel veri sızmasını ENGELLEMEZ. Kaydedilen şey izin
listeli, YAPILANDIRILMIŞ bir kayıttır: kural adı, alan adı, yakalanan ifade.
Serbest metin değil.

**Kapsam DIŞI, ISSUES'a.** `series/produce.py` içindeki birçok dal hatayı
yutup `None` döndürüyor; genel tipli hata kanıtı altyapısı bu çevrimde
YAPILMIYOR. Bu rock yalnız içerik reddi yolunu tipler.

**Proof.** Yeni `tests/test_content_reject_lifecycle.py`: kapıdan düşen plan
`CONTENT_REJECT` üretir; ÜÇ ÜRETİM DENEMESİ TÜKETİLMEZ; alarma düşer;
kayıt yapılandırılmıştır ve ham istisna metni içermez; sonraki geçerli bölüm
koşulabilir kalır. Sonra tam takım.

---

### ROCK B , ilk-karede-okunur anomali kapısı (harcamadan ÖNCE)

**Kural, İhsan kararıyla ikiye ayrıldı.**

**B1, REDDEDER , yapısal: shot 1 gözlemi önceki bir olaya bağlı olamaz.**
Uygulanır: YALNIZ `shots[0].violation_observation`, YALNIZ `tek-obje-4x6`.
Yakalanan yapılar: `after being|it|the|each|every`, satır başında `after`,
`once it|the|they`, `having been`, `each time`, `every time`,
`regardless of`, `keeps <fiil>ing`.
Ölçülen etki: part 36 reddedilir (`After being rolled, both dice visibly land...`).
Derlemede karşı örneği yoktur.

**B2, ZORUNLU ALAN: `violation_observation` bu formatta artık opsiyonel değil.**
Bugün `shots.py:142` `if observation is not None:` diyor; alan yazılmazsa
kuralın tamamı atlanıyor. Shot 1 için alan ZORUNLU hâle gelir.
Göç maliyeti sıfır: parts 22-37'nin hepsinde alan zaten dolu (doğrulandı).

**B3, BAYRAK TAKAR, REDDETMEZ , sınırsız nicelik sözlüğü.**
`never`, `always`, `forever`, `eventually`, `endless`, `endlessly`,
`never-ending`, `neverending`, `unending`, `unbounded`, `over and over`,
`again and again`, `more and more`, `one after another`, `replicat*`,
`duplicat*`, `multiplies`, `multiplying`, `refills itself`, `indefinitely`.
Uygulanır: `episode.title`, `object_card.anomaly_descriptor`,
`shots[0].violation_observation`. Sonuç RED DEĞİL, kayıt ve alarmdır.
Gerekçe: part 10 (2158 izlenme, `NEVER-ENDING` başlıklı) karşı örneği.
`infinite`/`infinitely` listeye ALINMAZ (part 37 kanıtı: uzamsal kullanım
meşru, o aile 1196 medyanlı).

**Paylaşılan sabit değişmez.** `TEMPORAL_OVERREACH` DEĞİŞTİRİLMEZ; onu
genişletmek dört kanalda `violation_observation` davranışını sessizce
değiştirir. Yeni kurallar `tek-obje-4x6` formatına ait AYRI, opt-in
sabitler olarak eklenir ve YALNIZ shot 1'e uygulanır
(Codex turu 2, bulgu 5: sonraki çekimleri de etkilemek yeni bir kusurdur).

**Onarım yolu (Codex turu 2, bulgu 5 ve 6).** İki ayrı iş:
(a) `_OBSERVATION_RULE` talimat metni ile doğrulayıcının sözlüğü tek kaynaktan
    türetilir, ama YALNIZ ilgili format ve shot 1 için; genel talimatı
    değiştirmek diğer formatları etkiler.
(b) B1 ihlali ONARILABİLİR SAYILMAZ. Gözlem cümlesini kozmetik olarak yeniden
    yazmak, altındaki fikri değiştirmez ve reddin amacını boşa çıkarır.
    B1'e takılan plan YENİ FİKİR ister, metin onarımı değil.
    Bu, `_repair_episode_fields` yolunun dışında tutularak sağlanır.

**impossible-continuity: KARANTİNA, idam değil.** Aile listede kalır,
aileye özel kod yazılmaz.

**ROCK D olmadan devreye alınmaz.**

**Proof.** Yeni `tests/test_first_frame_readable_gate.py`. Regex birim testi
YETMEZ; kanıt bölüm 0.4'teki ÇAĞRI YOLLARINI kullanır:
- `replenish.py:1417`, `preflight.py:125`, `produce.py:1398` ve `1461`
  yollarının hepsi B1'i görür; `validate_plan_against_config` doğrudan
  çağrısı görmez (bu ayrım açıkça test edilir);
- part 36 reddedilir, düşüren ALAN ve İFADE adıyla doğrulanır;
- parts 22-35 ve 37 GEÇER;
- `violation_observation` OLMAYAN bir plan reddedilir (B2), ve alanı silerek
  kaçma denemesinin işe yaramadığı gösterilir;
- aynı olay-bağımlılığını farklı kelimelerle söyleyen bir başka ifade
  denenir ve kuralın sınırı dürüstçe kaydedilir;
- B3 sözlüğüne takılan bir plan REDDEDİLMEZ, yalnız bayrak ve alarm üretir;
- `TEMPORAL_OVERREACH` sabitinin metni DEĞİŞMEMİŞTİR;
- `tek-obje-4x6` olmayan bir plan ve shot 2/3/4 etkilenmez;
- B1 ihlali `_repair_episode_fields` tarafından onarılmaya ÇALIŞILMAZ.
- Tarihsel fixture'lar (parts 1-21) DEĞİŞTİRİLMEZ; part 19 için
  "biçimlendirilmiş eşdeğer" ayrı bir fixture olarak yazılır
  (Codex turu 2, bulgu 1).
- Fixture manifestosu test dosyasında AÇIKÇA listelenir (turu 2, bulgu 2).
Sonra tam takım.

---

### ROCK C , title_patterns'ı bu kanala tak

**Kusur.** Başlık kalıbı yalnız serbest metin talimatıyla tarif edilmiş.

**Yapılacak.** `sentinal_ihsan/unnatural-lab/series.json` içindeki
`auto_replenish` bloğuna `title_patterns` ekle. Üç kalıp, `re.fullmatch`.
Kalıp 3 tekil ve ÇOĞUL özneyi kabul etmeli (part 36:
`Why Won't These DICE Change Their Number?`).

**Aile eşlemesi (Codex turu 2, bulgu 10).** Başlık biçimi anlamlı bir aile
kısıtı DAYATMIYOR. Bu yüzden test geçirmek için uydurma dışlama YAZILMAZ:
her kalıp kanonik `families` listesinin tamamına eşlenir ve bu tercih
gerekçesiyle plana yazılır. Kanıt, eşlemenin BİLEREK geniş olduğunu
doğrular, geniş olduğunu gizlemez.

**Karakter üst sınırı 60'a hizalanır.** `replenish.py:1093` şu an
`len(title) > 60` uyguluyor, `auto_replenish.title_style` metni ise
"Max 75 characters" diyor. Sözleşme 60'ta birleşir, brief metnindeki 75
sayısı 60 yapılır. Brief'e dokunulan TEK yer budur.

**Mevcut test fixture'ları göç eder (Codex turu 2, bulgu 11).**
`tests/test_replenish_partial_batch.py` canlı config ile
`"Partial Proof A"` / `"Clean Batch A"` gibi başlıklar kullanıyor
(doğrulandı). Bunlar geçerli başlıklara taşınır ve testlerin ÖNEK, ONARIM
ve RED iddiaları aynen korunur.

**SINIR.** `title_patterns` part 32'yi yakalayamaz; o başlık kalıp 2'ye
biçimsel olarak uyar. Bu rock yalnız BİÇİM kaçağını kapatır ve ondan
performans iddiası TÜRETİLMEZ.

**Proof.** Yeni `tests/test_unnatural_lab_title_patterns.py`:
`validate_replenish_config` sıfır hata; parts 22-37 başlıklarının hepsi
fullmatch; part 19 başlığı reddedilir; her kalıbın pozitif sınırı ve
yakın-eşleşen bozuk varyantları ayrı ayrı; 60 ve 61 karakter sınırı;
göç eden fixture'ların eski iddiaları hâlâ geçer. Sonra tam takım.

---

### ROCK E , koşu sınırında kaybolan üretim

**ROCK 4 (bütçe tabanı rezervasyonu) v2'de KALDIRILDI.**
`series/critic.py::CapAwareRegenAllocator` (satır 1085) zaten "her
henüz-yetkilendirilmemiş ana çekimi" koruyor; önerdiğim rezervasyon onun
kopyasıydı ve gerçek kaybı ıskalıyordu.

**Gerçek kusur.** Koruma TEK KOŞU içinde çalışıyor. Kabul edilmiş çekimler
koşu sınırını geçmiyor; koşu ölünce her şey kayboluyor, sonraki koşu sıfırdan
üretiyor, ama kalıcı defter aynı bölüm için saymaya devam ediyor. Ölçülen
sonuç: 2.896 kredi, sıfır video.

**Kapsam, Codex turu 2 bulgularıyla sıkılaştırıldı.**
- Sahiplik: yalnız SERİLEŞTİRİLMİŞ unnatural-lab koşuları. Eşzamanlı koşu
  sahipliği bu rock'ın kapsamı dışıdır (bulgu 14).
- Eserler DEĞİŞMEZ (immutable) kontrol noktalarıdır ve ATOMİK bir manifest
  ile kaydedilir.
- **Bayat eser koruması (bulgu 15).** `seri:bölüm` anahtarı ve bayt
  bütünlüğü YETMEZ: plan, referans ya da QC değiştiyse eski çekim geçersizdir.
  Eserler plan kimliğine ve referans kimliğine BAĞLANIR; planda zaten duran
  `doctrine_sha256` ve `ref_prompt_sha256` alanları bu bağın taşıyıcısıdır.
  Geçersizleme ve zincir bağımlılığı test edilir.
- **Geri yükleme yeri (bulgu 16).** Üretimin İÇİNDE geri yüklemek GEÇ KALIR:
  `run_next` önce `_budget_failure` çalıştırıyor, ve tamamlanmış bir master
  bile üretim kredi kapılarına takılabiliyor. Geri yükleme ve doğrulama,
  tamamlanma maliyeti hesabından ÖNCE yapılır; doğrulanmış bir master
  üretim rezervasyonlarına girmeden doğrudan yayına yönlendirilir.
- **Depolama kesintisi ile bozulma AYRILIR (bulgu 17).** "Bütünlük
  doğrulanamazsa yeniden üret" kuralı geçici bir depolama arızasını taze
  kredi harcamasına çevirir. Erişilemeyen depolama ile DOĞRULANMIŞ bozulma
  ayrı ele alınır; kurtarma belirsizse koşu durur ve eyleme dönük alarm üretir.

**Sert sınırlar.** `credits_ledger.json` şeması ve durable defter davranışı
DEĞİŞMEZ; harcama muhasebesi korunur. Kredi tavanı değerlerine dokunulmaz.
`balance_floor` / `kie_reservations.json` koşular arası paylaşımı kapsam dışı.

**Proof (Codex turu 2, bulgu 19).** İki koşuluk kanıt, hayatta kalan yerel
dosyalar ya da mock'lanmış önbellek kabulüyle SAHTE GEÇEBİLİR. Bu yüzden
`tests/test_durable_episode_recovery.py`:
birinci koşunun çalışma dosyaları SİLİNİR; yalnız kalıcı eserler geri
yüklenir; gerçek defter ve gerçek QC kontrolleri korunur; ikinci koşunun
kabul edilmiş çekimleri SIFIR kez yeniden ürettiği ve tavanı aşmadan
tamamladığı doğrulanır; plan/referans değişince eserin geçersizlendiği
doğrulanır; depolama erişilemezken TAZE HARCAMA YAPILMADIĞI doğrulanır.
Mevcut `test_credit_gate.py`, `test_rock1_budget_and_qcskip.py`,
`test_hold_recovery.py` yeşil kalır. Sonra tam takım.

---

## 2. Bu planın DOKUNMADIĞI şeyler

- Ses hedefleri: -14 LUFS, -1,0 dBTP. ROCK A hedefe varma yöntemini düzeltir.
- `bible.json`: formül, QC talimatı, art_style, karakter, ortamlar.
- `auto_replenish.brief` metni. TEK istisna: ROCK C içindeki 75 -> 60 düzeltmesi.
- Kesme sayısı ve plan süresi.
- Yayınlanmış bölümlerin durum dosyaları; part 33'ün `qc_retry` kaydına
  elle dokunulmaz.
- Tarihsel plan fixture'ları (parts 1-21) değiştirilmez.
- Diğer üç kanalın davranışı; 803 testin yeşil kalması bunun kanıtıdır.

## 3. DAĞITIM ÖNCESİ İHSAN KARARI (Codex turu 2, bulgu 20)

**Part 33 politikası, YAPIM'ı değil DAĞITIM'ı bloke eder.** Kod offline
yazılabilir, ama ROCK A dağıtıldığı anda zamanlanmış koşu part 33'ün kalan
404 kredisini kendi başına harcamakta serbest kalır. Bu yüzden dağıtımdan
önce şu seçilmeli: bölümü TUT (hold), YENİDEN DENE, ya da TERK ET.
Bu yapım hiçbir ücretli kabul koşusunu yetkilendirmez.

## 4. ISSUES listesine ertelenenler

- **Yayın kurtarma (Codex turu 1 bulgu 23, turu 2 bulgu 18).** Mevcut
  mükerrer-başlık kapısı yayın kurtarma DEĞİLDİR: arama hatasında fail-open
  davranıyor, yalnız YouTube'u kapsıyor, kaybolan yükleme onaylarını
  ele almıyor. Doğru iş: platform başına tamamlanma ve bekleyen istek
  kimliklerini kalıcılaştırmak, yeniden göndermeden önce mutabakat yapmak,
  ve "uzak başarılı, yerel çöktü" senaryosunu test etmek. Bu çevrimde
  YAPILMIYOR; ölçülen kaybı tek bölüm (part 5), ROCK E'nin ölçülen kaybı
  ise 2.896 kredi.
- `series/produce.py` genelinde tipli hata kanıtı: birçok dal hatayı yutup
  `None` döndürüyor.
- Part 5'in iki kaynak arasındaki çelişkisi, parts 23-24'ün izsiz `skipped` durumu.
- `balance_floor` / `kie_reservations.json` koşular arası paylaşımı.
- Eşzamanlı koşu sahipliği (ROCK E kapsam dışı bırakıldı).
- B3 bayraklarının 20 bölüm sonra ölçülmesi: bayraklı bölümler gerçekten
  düşük mü performe ediyor? Bu, sert redde geçilip geçilmeyeceğinin kararıdır.
- 16 sn mi 22 sn mi süre A/B testi; diğer üç kanala ses ayarı yayılması.
- Part 20 (`This BRUSH...HUM?!`, 498) ses-anomalisi vakası: brief yalnız-sesle
  anlaşılan ihlali yasaklıyor ama kapı yok.
