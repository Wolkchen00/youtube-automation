# RF-PLAN: Kanca kapıları ve yayın hattı onarımı (unnatural-lab)

Tarih: 2026-09-10 (Los Angeles)
Kaynak analiz: `sentinal_ihsan/REELYZE-RAPOR.md`
Kanal: `sentinal_ihsan` / seri `unnatural-lab`
Revizyon: v5, Same Page turu 4 sonrasi (Codex tur 1-3: 23+20+11 = 54 bulgu;
Nemotron tur 4, TAZE OTURUM: 8 bulgu). Integrator turu 4'te Codex'ten
Nemotron'a gecti; kota duvari nedeniyle oturum surekliligi KIRILDI ve
taze model kendi onceki bulgularini dogrulayamaz.

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

İkinci continuity bölümü part 32 (146 izlenme) anlık görüntüden sonra
yayınlandı; sayısı REELYZE raporundan geliyor.

### 0.2 Rapora itiraz, sınırlandırılmış hâliyle

Rapor part 19'u (82) "I Found... kalıbı sabır istiyor" diye açıklıyor.
Aynı kalıbı kullanan 7 bölümün metrikleri: 801 / 74 / 2554 / 1285 / 1127 / 1202 / 79.
Bu veri başlık kalıbını TEK açıklama olmaktan çıkarır; başlık biçiminin nötr
olduğunu ya da continuity ailesinin tek sebep olduğunu KANITLAMAZ.

### 0.3 Kapı kuralının kanıt durumu, dürüst hâliyle

**(a) Kapı eski format bölümlerine ulaşmıyor.** Parts 1-21'de `format_version`
yok (doğrulandı: part 10, 19, 20 için `None`); `format_plan_errors` ilk satırda
boş dönüyor. Kapının GERÇEK kapsamı part 22 ve sonrasıdır ve o kapsamda
reddedilen ölçülmüş ölü bölüm sayısı **BİRDİR** (part 32, 146 izlenme).

**(b) Kelime listesinin 2.158 izlenmelik karşı örneği var.** Part 10
(`Can I Turn A BOTTLE Into A NEVER-ENDING FOUNTAIN?!`, metrik 2158) kanalın
en iyi ikinci bölümü ve başlığında `NEVER-ENDING` geçiyor.

**(c) Kural boş alanla atlatılabiliyordu.** `series/shots.py:142`
`if observation is not None:` diyor; alan opsiyonel.

**İHSAN KARARI (2026-09-10): sert red YALNIZ yapısal kurala.**
Kelime listesi bayrak takar, reddetmez. Alan zorunlu hâle gelir.

### 0.4 Kapının çağrı yolları

`validate_plan_against_config` `format_plan_errors`'ı HİÇ çağırmıyor.
Kapı yalnız `validate_plan` (`shots.py:432`, `447`) üzerinden görülür:

| Çağrı yeri | B1/B2 görür mü |
|---|---|
| `series/replenish.py:1417` (`_validate_batch`) | EVET |
| `series/preflight.py:125` | EVET |
| `series/produce.py:1398` | EVET |
| `series/produce.py:1461` (referans sonrası) | EVET |
| Doğrudan config çağrıları (`replenish.py:1411`, `preflight.py:119`, `produce.py:1388`) | HAYIR |

Testler regex'i değil BU YOLLARI kanıtlar.

### 0.5 Yayın hattı gerçeği

| Part | Durum | Sebep |
|---|---|---|
| 1, 2 | rejected | |
| 5 | `series.json` published, `published.json` youtube id NULL | çelişki |
| 23, 24 | skipped | iz yok |
| 25 | budget_exhausted | kalan=364, asgari=400 |
| 26 | budget_exhausted | kalan=68, asgari=400 |
| 28 | budget_exhausted | kalan=320, asgari=400 |
| 30 | needs_human | UNKNOWN, "üretim nedeni bilinmiyor" |
| 33 | qc_retry, ŞU AN TIKALI | true-peak -0,9 dBTP > -1,0 |

33 bölümün 23'ü YouTube'a ulaştı. **Karşılıksız yanan kredi**
(`credits_ledger.json`): 25 = 436, 26 = 932, 28 = 680, 30 = 848.
Toplam **2.896 kredi, ~14,50 dolar, çıktı sıfır.** Part 33'te 596 harcanmış,
404 kalmış.

---

## 1. Rock listesi

Beş rock. **Sıra: A, D, B, C, E.** Ortak kanıt: `python -m pytest tests/ -q`
(taban: 803 passed + 188 subtest, ~35 sn), PATH'teki Python 3.12 ile.
Depo kökündeki `.venv` içinde pytest YOKTUR.

---

### ROCK A , master true-peak yakınsaması

**Kusur 1.** `core/ffmpeg_tools.py::master_audio` her başarısız denemede
`limiter_db -= overshoot` yapıyor; marj yok, hedef sınırın tam üstüne nişanlı.

**Kusur 2, YENİ (Nemotron turu 4, kodda doğrulandı).** Döngü durumu YALNIZ
true-peak başarısız olunca değiştiriyor:

```python
if not true_peak_ok:
    limiter_db -= overshoot      # durum değişir
if not loudness_ok:
    logger.warning(...)          # HİÇBİR DURUM DEĞİŞMEZ
```

True-peak geçip LUFS penceresi dışında kalırsa `limiter_db` aynı kalır.
Filtre dizesi aynı, girdi aynı değişmemiş premaster, dolayısıyla çıktı
BİREBİR AYNI ve ölçüm de aynı. 2. ve 3. denemeler 1. denemenin kopyasıdır:
üç ffmpeg koşusu boşa gider ve başarısızlık garantidir. Bu kusuru ilk üç
inceleme turu da kaçırdı.

**Kanıt durumu.** Elimizdeki tek gözlem part 33'ün yuvarlanmış -0,9 dBTP
sonucu. Deneme telemetrisi siliniyor. "AAC kare-arası tepe ekliyor" bir çıkarım.

**Yapılacak, sırayla:**

1. **Önce kanıtı koru.** Her denemenin limiter tavanı, ölçülen true-peak ve
   LUFS değeri `RuntimeError` yükselmeden ÖNCE **`logs/` altına** yazılır.
   Gerekçe (Codex turu 3, CLARIFY): `.github/workflows/unnatural-lab.yml:131-137`
   `logs/` klasörünü `always()` koşuluyla yüklüyor (7 gün saklama);
   bölüm çıktı klasörü YÜKLENMİYOR. Telemetrinin başarısızlıktan sonra
   okunabildiği test edilir.
2. Geri çekmeye emniyet marjı: `limiter_db -= (overshoot + margin)`,
   `margin = 0.2` dB, deneme başına asgari hareket 0,3 dB.
3. **Kümülatif sınır SAYIYLA: başlangıç `target_tp` değerinden en fazla
   3,0 dB toplam indirim.** Yani -1,0 hedefinde limiter tavanı en fazla
   -4,0 dBTP'ye çekilir. Bu sınıra çarpıldığında davranış "başarılı gibi
   yapmak" DEĞİL, teşhis üreterek fail-closed durmaktır: son denemenin
   limiter tavanı, ölçülen TP ve LUFS değerleri hata mesajına ve `logs/`
   telemetrisine yazılır. Plan, hem TP hem LUFS kapısını sağlayan hiçbir
   ayarın bulunmadığı malzemede BAŞARI VAAT ETMİYOR.
4. **Kusur 2'nin onarımı.** LUFS-tek-başına başarısızlığında ya durumu
   DEĞİŞTİREN bir düzeltme adımı uygulanır, ya da döngü DERHAL fail-closed
   durur ve teşhis üretir. Aynı limiter ayarıyla ikinci bir deneme koşmak
   YASAKTIR: özdeş girdi ve özdeş filtre özdeş çıktı verir.

**DEĞİŞMEZ.** `target_i=-14.0`, `target_tp=-1.0`, ve
`produce.py::_verify_audio_master` içindeki `true_peak <= -1.0` fail-closed
kapısı aynen kalır.

**Part 33'ü tek başına kurtarmaz.** Medyası kalıcı değil, defterde 596/1000.

**Proof.** Yeni `tests/test_master_true_peak_convergence.py`:
(a) limiter tavanının denemeler arasında en az 0,3 dB HAREKET ETTİĞİ,
    üretilen ffmpeg filtre dizesinden OKUNARAK doğrulanır. Yalnız ölçüm
    mock'lamak yetmez: ikinci ölçümü limiter'dan bağımsız veren bir mock
    düzeltilmemiş kodu da yeşil gösterir;
(b) gerçek AAC ile üretilmiş, 0,1 dB aşımla açılan malzemede döngünün üç
    denemede -1,0 dBTP altında kapandığı;
(b2) ARTAN aşımlı malzemede (Nemotron turu 4): üç denemenin ÜÇÜNÜ de
    gerektiren bir senaryoda son çıktının HEM true-peak HEM LUFS kapısını
    sağladığı. Tek bir 0,1 dB vakası yeterli kanıt değildir;
(b3) LUFS-tek-başına başarısızlığında iki ÖZDEŞ denemenin koşulmadığı:
    ya durum değişir ya derhal fail-closed durulur;
(c) 3,0 dB kümülatif sınıra çarpan malzemede fail-closed durulduğu ve
    teşhisin üretildiği;
(d) sınır-LUFS malzemesinde iki kapının çelişmesi hâlinde de fail-closed;
(e) telemetrinin `logs/` altında hayatta kaldığı.
Mevcut `test_master_true_peak.py`, `test_master_true_peak_adversarial.py`,
`test_rocka_audio_master.py` yeşil kalır. Sonra tam takım.

---

### ROCK D , kapıdan düşen planın tipli reddi (ROCK B'nin ön koşulu)

**Kusur, kanıtlanmış hâliyle.** Part 30'un `UNKNOWN` ile ölmesini plan reddine
bağlamak kanıtsızdı; mevcut yaşam döngüsü üç denemeyle SINIRLI, "sonsuz" demem
yanlıştı. Kanıtlanmış olan: sınıflandırılamayan başarısızlıkta hata ayrıntısı
KAYBOLUYOR ve bölüm üç ÜCRETLİ üretim denemesi tüketerek ölüyor
(part 30 defterde 848 kredi).

**Yapılacak.** İçerik kapısından düşen plan `CONTENT_REJECT` koduyla ANINDA
reddedilir, üç üretim denemesini TÜKETMEZ. Kayıt hangi kuralın hangi alanda
hangi ifadeden düştüğünü söyler.

**Geçiş kararı.** Mevcut atomik `terminalize-and-advance` yolu kullanılır ve
alarm üretilir. Kanıt, SONRAKİ geçerli bölümün koşulabilir kaldığını doğrular;
bölümü belirsiz süre park etmek geçmiş sayılmaz.

**Sızıntı koruması.** Ham istisna metnini kırpmak API anahtarı, imzalı URL ya
da kişisel veri sızmasını engellemez. Kaydedilen şey izin listeli
YAPILANDIRILMIŞ bir kayıttır: kural adı, alan adı, yakalanan ifade.

**Kapsam DIŞI, ISSUES'a.** `produce.py` genelindeki `None` dönen dallar için
genel tipli hata altyapısı bu çevrimde yapılmıyor.

**Proof.** Yeni `tests/test_content_reject_lifecycle.py`: kapıdan düşen plan
`CONTENT_REJECT` üretir; ÜÇ ÜRETİM DENEMESİ TÜKETİLMEZ; alarma düşer; kayıt
yapılandırılmıştır ve ham istisna metni içermez; sonraki geçerli bölüm
koşulabilir kalır. Sonra tam takım.

---

### ROCK B , ilk-karede-okunur anomali kapısı

**B1, REDDEDER , YALNIZ tamamlanmış-olay bağımlılığı.**
Uygulanır: yalnız `shots[0].violation_observation`, yalnız `tek-obje-4x6`.

Codex turu 3, bulgu 2 kabul edildi: `regardless of` ve `keeps <fiil>ing`
DEĞİŞMEZLİK ya da SÜREGELEN DURUM anlatabilir ve bunlar ilk karede okunabilir
("Regardless of angle, the blue core is visible"). Bunlar B1'den ÇIKARILDI.
Çıplak `^after` de çıkarıldı.

**B1 literal regex** (ROCK C gibi ölçülerek yazıldı, yapımda yorum payı yok):

```
\b(?:after being \w+ed
   |having been \w+ed
   |after (?:the |a |an |it |they |each |every )?(?:\w+ )?(?:is|are|was|were) \w+ed
   |after (?:it|the|they|each|every) \w+ed
   |once (?:it|the|they|the \w+) (?:is|are|was|were|has|have) (?:been )?\w+ed)\b
```

**Ölçüm.** 16 `tek-obje-4x6` planının tam olarak BİRİ reddediliyor: part 36
(`After being rolled, both dice visibly land...`). Parts 22-35 ve 37 geçer.
Eski format planlarının hiçbirinde shot 1 gözlemi yok, yani kapsam dışılar.

Saldırgan küme, 8/8 doğru:

| İfade | Beklenen | Sonuç |
|---|---|---|
| `Regardless of angle, the blue core is visible.` | geç | geç |
| `The surface keeps glowing while the hand rests on it.` | geç | geç |
| `The stone is embedded in the soap and water runs around it.` | geç | geç |
| `Water flows upward from the bottle mouth in a steady column.` | geç | geç |
| `After being rolled, both dice visibly land on their faces.` | RED | RED |
| `After being rolled, the dice always land alike.` | RED | RED |
| `After the lid is removed the glow persists.` | RED | RED |
| `Once the jar is opened the light stays trapped.` | RED | RED |

**Kaydedilen sınır, dürüstçe.** Bu bir YAPI SAYIMIDIR, semantik bir çözümleyici
değildir. İlk daraltılmış taslak `After the lid is removed...` ifadesini
KAÇIRIYORDU; ölçüm sırasında yakalandı ve regex genişletildi. Aynı türden
başka bir kaçak kalmış olabilir. Bu yüzden B1 tek savunma hattı sayılmaz;
üretim sonrası `require_first_frame` QC kapısı yerinde kalır.

**B2, ZORUNLU ALAN.** `violation_observation` bu formatta shot 1 için zorunlu
olur; `if observation is not None:` kaçışı kapanır.

**B2 göç maliyeti SIFIR DEĞİL (Codex turu 3, bulgu 1, doğrulandı).**
Kuyruktaki planlar ve prompt sözleşmesi uyumlu, ama iki test kurucusu shot 1
gözlemini yazmıyor ve kırılacak:
- `tests/test_gercekcilik_rock2.py::raw_plan`
- `tests/test_shot1_onset.py::plan_with_actions`
İkisine de geçerli bir shot 1 gözlemi eklenir. Golden dosya YALNIZ prompt
metni değişirse güncellenir.

**B3, BAYRAK TAKAR, REDDETMEZ , sınırsız nicelik sözlüğü.**
`endless`, `endlessly`, `never-ending`, `neverending`, `unending`, `unbounded`,
`over and over`, `again and again`, `more and more`, `one after another`,
`replicat*`, `duplicat*`, `multiplies`, `multiplying`, `refills itself`,
`indefinitely`, ve mevcut kapıların zaten reddetmediği yerlerde
`never`, `always`, `forever`, `eventually`.
`infinite`/`infinitely` listeye ALINMAZ (part 37 kanıtı).

**B3 ÖNCELİK KURALI (Codex turu 3, bulgu 3, doğrulandı).**
B3 mevcut hiçbir sert kapıyı ZAYIFLATMAZ ve hiçbir yeni red EKLEMEZ.
Doğrulanan çakışmalar:
- `NEGATIVE_VIDEO_LANGUAGE` zaten `never` kelimesini yakalıyor;
- `TEMPORAL_OVERREACH` zaten `never|always|forever|eventually` kelimelerini
  `violation_observation` alanında reddediyor;
- `object_card.anomaly_descriptor` çekim prompt'una BİREBİR kopyalanıyor
  (`shots.py:137`) ve prompt de sert lint'ten geçiyor.
Yani bu kelimeler o alanlarda BUGÜN DE reddediliyor ve reddedilmeye devam eder.
B3'ün bayrağı yalnız mevcut sert kapının ateşlemediği yerlerde anlamlıdır
(başlıca `episode.title`). Bu öncelik açıkça test edilir; B3 hiçbir mevcut
reddi muaf tutmaz.

**B3 MEKANİZMASI (Codex turu 3, bulgu 4).** B3, `format_plan_errors` içine
KONULMAZ: o fonksiyon yalnız hata listesi döndürür ve çağrı yollarında
TEKRAR TEKRAR çağrılır, yani orada kayıt ya da alarm üretmek mükerrer olur.
Bunun yerine saf, yan etkisiz bir TARAYICI yazılır (yapılandırılmış bulgu
döndürür); redler doğrulamada tüketilir; B3 bulguları yaşam döngüsünde
TEK BİR tekilleştirilmiş noktada kaydedilir ve alarma düşer.

**B1 ONARILAMAZ, ve tüm alan onarımını KISA DEVRE YAPAR
(Codex turu 3, bulgu 5).** B1'i yalnız `_repair_episode_fields` dışında
tutmak YETMEZ: hem B1'e hem mevcut onarılabilir bir kurala takılan bir gözlem
tüm-alan onarımına girip B1'i kozmetik olarak sildirebilir. Bu yüzden B1
taşıyan bölümde ALAN ONARIMININ TAMAMI kısa devre yapar. Test edilecek karışık
ifade: `After being rolled, the dice always land alike.`

**Paylaşılan sabit değişmez.** `TEMPORAL_OVERREACH` metni DEĞİŞTİRİLMEZ.
Yeni kurallar format-kapsamlı, opt-in sabitlerdir ve YALNIZ shot 1'e uygulanır.
`_OBSERVATION_RULE` talimatı ile doğrulayıcı sözlüğü tek kaynaktan türetilir,
ama yalnız ilgili format ve shot 1 için.

**impossible-continuity: KARANTİNA, idam değil.** Aileye özel kod yazılmaz.

**ROCK D olmadan devreye alınmaz.**

**Proof.** Yeni `tests/test_first_frame_readable_gate.py`. Regex birim testi
YETMEZ:
- bölüm 0.4'teki dört yol B1/B2'yi görür, doğrudan config çağrıları görmez;
- part 36 reddedilir, düşüren alan ve ifade adıyla doğrulanır;
- parts 22-35 ve 37 geçer; fixture manifestosu test dosyasında açıkça listelenir;
- `regardless of` ve `keeps <fiil>ing` içeren OKUNABİLİR bir gözlem
  REDDEDİLMEZ (turu 3 bulgu 2 regresyon testi);
- `violation_observation` olmayan plan reddedilir; alanı silerek kaçma çalışmaz;
- B3 sözlüğüne takılan plan REDDEDİLMEZ, bayrak üretir, ve mevcut sert
  kapıların ateşlediği alanlarda red DEVAM EDER (öncelik testi);
- B3 kaydı/alarmı bir yaşam döngüsünde TEK KEZ düşer (mükerrerlik testi);
- karışık ifade `After being rolled, the dice always land alike.` ile
  alan onarımının tamamen kısa devre yaptığı;
- `TEMPORAL_OVERREACH` metni değişmemiştir; `tek-obje-4x6` olmayan plan ve
  shot 2/3/4 etkilenmez;
- tarihsel fixture'lar (parts 1-21) DEĞİŞTİRİLMEZ; part 19 için ayrı
  "biçimlendirilmiş eşdeğer" fixture yazılır.
- **ÜRETKEN SALDIRGAN TEST (Nemotron turu 4).** Sabit manifest yeterli kanıt
  değildir: 8 bilinen vakanın dışında bir dilbilgisi yapısı kullanan yeni bir
  plan testleri geçip üretimde patlar. `violation_observation` ifadeleri
  programatik olarak MUTASYONA uğratılır (zaman kipi, edilgen/etken, araya
  giren sözcük) ve B1'in davranışı bu üretilmiş küme üzerinde raporlanır.
  Amaç mükemmel kapsama değil, KAPSAMIN ÖLÇÜLMESİ ve sınırın kayda geçmesidir.

**GERÇEK İKMAL DÖNGÜSÜ TESTİ (Codex turu 3, bulgu 6).** Yukarıdakiler kapıyı
kanıtlar ama döngüyü kanıtlamaz. `generate_plans` / `replenish` üzerinden iki
entegrasyon testi eklenir:
- BİRİNCİ sıradaki bölüm onarılamaz kurala takarsa: yeni üretim denemeleri ve
  ardından GÜRÜLTÜLÜ istisna; sessiz yeşil dönüş YOK;
- SONRAKİ sıradaki bölüm takarsa: en uzun geçerli önek artı alarm;
- her iki durumda da boş sonuç ASLA yeşil dönmez.
Sonra tam takım.

---

### ROCK C , title_patterns'ı bu kanala tak

**Literal regexler (Codex üç turdur istedi, ölçülerek yazıldı).**
`re.fullmatch` ile çalışır.

```
P1  Something Is WRONG With (?:This|These) [A-Z][A-Z0-9]*(?: [A-Z][A-Z0-9]*){0,2}
P2  This [A-Z][A-Za-z0-9]*(?: [A-Za-z0-9]+){0,2} [A-Za-z][A-Za-z0-9 ']{2,40}[!?]{1,2}
P3  Why Won't (?:This|These) [A-Z][A-Z0-9]*(?: [A-Z][A-Z0-9]*){0,2} [A-Za-z][A-Za-z0-9 ']{2,40}\?
```

**Ölçüldü.** Parts 22-37'nin 16 başlığının HEPSİ kabul ediliyor ve her biri
TAM BİR kalıba düşüyor (P1: 22, 25, 27, 29, 35, 37 , P2: 24, 26, 28, 30, 31,
32, 33 , P3: 23, 34, 36). Reddedilenler: `I Found UNNATURAL PAGES... And They
STARTED To REPLICATE!`, `Can I Turn A BOTTLE Into A NEVER-ENDING FOUNTAIN?!`,
küçük harfli varyant, eksik obje (`Something Is WRONG With This`), `This`,
`This LEMON`, `Watch This LEMON BOUNCE!`, kesme işaretsiz `Why Wont This SOAP
Melt?`, ve aşırı uzun kuyruklu varyant.

**Aile eşlemesi ve dürüst sınırı (Codex turu 3, bulgu 7).**
Başlık biçimi anlamlı bir aile kısıtı DAYATMIYOR, bu yüzden her kalıp kanonik
`families` listesinin tamamına eşlenir. Bunun sonucu açıkça kabul ediliyor:
config'in aile yarısı bu seride TOTOLOJİKTİR ve hiçbir şey zorlamaz.
Test geçirmek için uydurma dışlama YAZILMAZ. Kanıt, eşlemenin bilerek geniş
olduğunu doğrular; zorlayıcı olduğunu iddia ETMEZ.

**Karakter üst sınırı 60'a hizalanır.** `replenish.py:1093` `len(title) > 60`
uyguluyor, `title_style` metni "Max 75 characters" diyor. Sözleşme 60'ta
birleşir, brief metnindeki 75 sayısı 60 yapılır. Brief'e dokunulan tek yer.

**Mevcut fixture'lar göç eder.** `tests/test_replenish_partial_batch.py`
canlı config ile `"Partial Proof A"` / `"Clean Batch A"` başlıkları kullanıyor
(doğrulandı). Geçerli başlıklara taşınır; önek, onarım ve red iddiaları
aynen korunur.

**SINIR.** `title_patterns` part 32'yi yakalayamaz (kalıp 2'ye biçimsel olarak
uyar). Bu rock yalnız biçim kaçağını kapatır ve ondan performans iddiası
türetilmez.

**Proof.** Yeni `tests/test_unnatural_lab_title_patterns.py`:
`validate_replenish_config` sıfır hata; yukarıdaki 16 kabul ve 9 red vakası
birebir; 60 ve 61 karakter sınırı; aile eşlemesinin totolojik olduğu açıkça
belgelenir; göç eden fixture'ların eski iddiaları hâlâ geçer. Sonra tam takım.

---

### ROCK E , koşu sınırında kaybolan üretim ve yayın

**Gerçek kusur.** `CapAwareRegenAllocator` (critic.py:1085) korumayı TEK KOŞU
içinde yapıyor. Kabul edilmiş çekimler koşu sınırını geçmiyor; koşu ölünce
her şey kayboluyor, sonraki koşu sıfırdan üretiyor, kalıcı defter saymaya
devam ediyor. Ölçülen sonuç: 2.896 kredi, sıfır video.

**DEPOLAMA BACKEND'İ, adıyla.** Yeni depo icat EDİLMEZ. Mevcut GitHub Release
yolu genişletilir: `series/approver.py` içinde `_download_release(tag)` ve
`_cleanup_release(tag)` var, `series_runner.py:147` `gh release create` ile
videoyu yüklüyor, `:820` bölüm kaydına `release_tag` yazıyor, `:441`
tamamlanmayı `("video", "release_tag", "approval_msg_id")` üçlüsüyle ölçüyor.

**KÖK SEBEP, satır numarasıyla (Nemotron turu 4, doğrulandı).**
`_persist_release(slug, n, video)` YALNIZ `if mode == "approval":` bloğunun
içinden çağrılıyor (`series_runner.py:806`). unnatural-lab'in `publish_mode`
değeri **`auto`**. Yani bu seride kalıcı Release HİÇ OLUŞTURULMUYOR ve
üretilen hiçbir şey koşu sınırını geçmiyor. 2.896 kredilik kaybın mekanizması
budur; artık çıkarım değil, tek satırlık bir koşul.

**Bu yüzden ROCK E üç parçadır:**
1. ÜRETİM ANINDA yükleme: tamamlanan eser, `approval` moduna bağlı olmadan
   kalıcılaştırılır. Mevcut `_persist_release` yeniden kullanılır, yeniden yazılmaz.
2. KOŞU BAŞINDA kurtarma: var olan eser indirilir ve doğrulanır.
3. ÜRETİMİ ATLAMA: doğrulanmış eser varsa o çekim/master yeniden üretilmez.

**KİMLİK, düzeltilmiş hâliyle (Codex turu 3, bulgu 10).**
`doctrine_sha256` ve `ref_prompt_sha256` YETMEZ: birincisi planlar arasında
PAYLAŞILIYOR, ikincisi çekim prompt'larını ve gerçek referans baytlarını
dışarıda bırakıyor. Ayrıca geri yüklenen çekimler, `qc_log.jsonl` kanıtı
olmadan `_revalidate_cached_shot` kapısından geçemez. Kontrol noktaları şunlara
bağlanır: normalize edilmiş TAM PLAN özeti, REFERANS İÇERİK özeti,
QC POLİTİKA parmak izi, ve KALICILAŞTIRILMIŞ QC-geçiş kanıtı.
Geçersizleme ve zincir bağımlılığı test edilir.

**GERİ YÜKLEME YERİ.** Üretimin içinde geri yüklemek geç kalır: `run_next`
önce `_budget_failure` çalıştırıyor ve tamamlanmış bir master bile üretim
kredi kapılarına takılabiliyor. Geri yükleme ve doğrulama, tamamlanma maliyeti
hesabından ÖNCE yapılır; doğrulanmış master üretim rezervasyonlarına girmeden
doğrudan yayına yönlendirilir.

**DEPOLAMA KESİNTİSİ ile BOZULMA AYRILIR.** "Doğrulanamazsa yeniden üret"
kuralı geçici bir arızayı taze kredi harcamasına çevirir. Erişilemeyen depolama
ile doğrulanmış bozulma ayrı ele alınır; kurtarma belirsizse koşu durur ve
eyleme dönük alarm üretir.

**YAYIN KURTARMA ARTIK KAPSAM İÇİNDE (Codex turu 3, bulgu 11).**
v3'te ertelenmişti; Codex haklı olarak bunun YENİ BİR TUZAK yarattığını
gösterdi: ROCK E eserleri kalıcılaştırınca, kısmi başarı durumunda
Instagram ve TikTok'a BAŞARIYLA atılmış gönderiler yeniden atılır, ve
kaybolan bir YouTube onayı mükerrer-başlık kapısını sonsuza kadar tetikleyip
yerel durumu hiç ilerletmez. Asgari kapsam: platform başına tamamlanma ve
BEKLEYEN İSTEK kimlikleri kalıcılaştırılır, yeniden göndermeden önce mutabakat
yapılır, ve zaten başarılı olan platform ATLANIR.

**Sert sınırlar.** `credits_ledger.json` şeması ve durable defter davranışı
DEĞİŞMEZ; harcama muhasebesi korunur. Kredi tavanlarına dokunulmaz.
`balance_floor` / `kie_reservations.json` koşular arası paylaşımı ve eşzamanlı
koşu sahipliği kapsam dışıdır; bu rock yalnız SERİLEŞTİRİLMİŞ unnatural-lab
koşularını hedefler.

**Proof.** `tests/test_durable_episode_recovery.py`. İki koşuluk kanıt hayatta
kalan yerel dosyalarla ya da mock'lanmış önbellek kabulüyle SAHTE GEÇEBİLİR,
bu yüzden:
- birinci koşunun çalışma dosyaları SİLİNİR, yalnız kalıcı eserler geri yüklenir;
- gerçek defter ve gerçek QC kontrolleri korunur;
- ikinci koşu kabul edilmiş çekimleri SIFIR kez yeniden üretir ve tavanı
  aşmadan tamamlar;
- plan ya da referans değişince eser GEÇERSİZ sayılır;
- QC kanıtı olmadan geri yüklenen çekim kabul EDİLMEZ;
- depolama erişilemezken TAZE HARCAMA YAPILMAZ, koşu alarm üreterek durur;
- "uzak başarılı, yerel çöktü" senaryosunda zaten yayınlanmış platform
  ATLANIR ve mükerrer gönderi olmaz.
Mevcut `test_credit_gate.py`, `test_rock1_budget_and_qcskip.py`,
`test_hold_recovery.py`, `test_publish_duplicate_gate.py`,
`test_async_upload_confirmation.py` yeşil kalır. Sonra tam takım.

---

## 2. Bu planın DOKUNMADIĞI şeyler

- Ses hedefleri: -14 LUFS, -1,0 dBTP.
- `bible.json`: formül, QC talimatı, art_style, karakter, ortamlar.
- `auto_replenish.brief` metni. TEK istisna: ROCK C'deki 75 -> 60 düzeltmesi.
- Kesme sayısı ve plan süresi.
- Part 33'ün `qc_retry` kaydına elle dokunulmaz.
- Tarihsel plan fixture'ları (parts 1-21).
- `TEMPORAL_OVERREACH` sabitinin metni.
- Diğer üç kanalın davranışı; 803 testin yeşil kalması bunun kanıtıdır.

## 3. DAĞITIM ÖNCESİ İHSAN KARARI

**Part 33 politikası YAPIM'ı değil DAĞITIM'ı bloke eder.** Kod offline
yazılabilir, ama ROCK A dağıtıldığı anda zamanlanmış koşu part 33'ün kalan
404 kredisini kendi başına harcamakta serbest kalır. Dağıtımdan önce seçilmeli:
TUT (hold), YENİDEN DENE, ya da TERK ET. Bu yapım hiçbir ücretli kabul
koşusunu yetkilendirmez.

## 4. ISSUES listesine ertelenenler

- **`target_lra` teslimde hiç doğrulanmıyor (Nemotron turu 4).**
  `master_audio` LRA hedefini loudnorm'a veriyor ama teslim ölçümünde yalnız
  true-peak ve LUFS kontrol ediliyor. Bu çevrimde YAPILMIYOR, çünkü LRA kapısı
  eklemek YENİ bir red kriteridir ve bugün geçen bölümleri düşürmeye başlayabilir;
  bu planın kuralı "ses kapılarını değiştirme, yalnız yakınsamayı düzelt".
  Ölçülüp ayrıca karar verilmeli.
- Rock sırası A-D-B-C-E entegrasyonu (Nemotron turu 4): E'nin dayanıklılık
  testleri fixture üzerinde geçip gerçek koşuda düşebilir; E'den önce
  A/B/C/D'nin gerçek koşuda regresyon üretmediği doğrulanmalı.
- `series/produce.py` genelinde tipli hata kanıtı: birçok dal hatayı yutup
  `None` döndürüyor.
- Part 5'in iki kaynak arasındaki çelişkisi; parts 23-24'ün izsiz `skipped` durumu.
- `balance_floor` / `kie_reservations.json` koşular arası paylaşımı.
- Eşzamanlı koşu sahipliği (ROCK E serileştirilmiş koşularla sınırlı).
- B3 bayraklarının 20 bölüm sonra ölçülmesi: bayraklı bölümler gerçekten düşük
  mü performe ediyor? Sert redde geçilip geçilmeyeceğinin kararı budur.
- ROCK C aile eşlemesinin totolojik olması: aile kısıtı gerçekten anlamlı hâle
  getirilecekse ayrı bir ölçüm işi ister.
- 16 sn mi 22 sn mi süre A/B testi; diğer üç kanala ses ayarı yayılması.
- Part 20 (`This BRUSH...HUM?!`, 498) ses-anomalisi vakası.
