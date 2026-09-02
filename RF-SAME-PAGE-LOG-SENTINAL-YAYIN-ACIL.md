# Same Page Meeting , Sentinal yayin acil kurtarma (2026-09-02)

Plan: RF-PLAN-SENTINAL-YAYIN-ACIL.md
Codex modeli: gpt-5.6-sol, reasoning effort high
Thread: 01a062bb-319a-7073-8052-caec7fa2e16b

## Round 1
### Integrator bulgular (Codex, birebir)
```
- [FIX] ROCK 1 sonucu tedavi ediyor; canlı reset, çekim 3'ün kasıtlı terminal hâli `state_carry` yerine statik obje referansına göre değerlendirildiği için geçerli düz/uzamış çatalların “unsuitable” sayılmasından doğuyor -> Zincir karesi QC'sine kaynak çekimin `state_carry` beklentisini verin, muafiyeti yalnız gerçek çıkarma/yükleme/API ve doğrulanmış uygunsuzluk yedeği olarak bırakın
- [FIX] ROCK 1 yeni bookkeeping gerektirmiyor; `chain_reset_pending` zaten `canonical_reset` değerini tam sonraki iterasyona taşıyor ve 1480 civarında tüketiliyor -> QC öncesinde bu mevcut değerin yerel snapshot'ını alın, ikinci bir reset state'i yaratmayın
- [FIX] Muafiyet yalnız `continuity_ok=false` redini kaldırırsa eksik veya şema dışı `continuity_ok` hâlâ hold üretir ve aynı çekimin regenleri yeniden duvara çarpar -> Alanı istemeye ve loglamaya devam ederken o çekimin bütün review/regen döngüsünde continuity kaynaklı hem fail hem unevaluated sonucunu non-blocking yapın
- [FIX] ROCK 2 sonrası `previous_shot_dropped` zinciri sıfırlarken `previous_accepted_clip` daha eski klibi taşır ve sonraki çekim yeniden continuity reddine uğrayarak tek düşüşü domino düşüşe çevirebilir -> `chain_reset_pending OR previous_shot_dropped` durumunu tek çekimlik kırık-çapa sinyali yapıp sonraki başarılı çekimde temizleyin
- [FIX] Üç kapıda ayrı ayrı `min_shots` kontrolü yazmak erken aşamada 3/4 hâlâ mümkünken bölümü yanlış iptal edebilir -> Tek bir `required_shot_count` türetin ve erken çıkışı yalnız `accepted + remaining < required` olduğunda, son kapıyı da `accepted >= required` olarak uygulayın
- [FIX] `min_shots` için tip ve sınır sözleşmesi yok; `true`, sıfır, negatif veya plan çekim sayısından büyük değer kredi harcanmadan reddedilmezse davranış belirsizleşir -> Tam `int` olup bool olmadığını ve `1 <= min_shots <= len(plan["shots"])` koşulunu preflight'ta doğrulayın
- [FIX] ROCK 2'nin “sessiz seri” varsayımı yanlış; canlı bible anlatımı etkinleştiriyor, part 26 anlatım taşıyor ve sayısal `min_shots` çekim 1 düşerse cold-open'ı, çekim 4 düşerse loop seam'i bozuyor -> Dört olası düşüş konumunu ayrı test edin ve rol kaybını yayın alarmında açıkça kabul ettirin veya `required_shots` politikası tanımlayın
- [DEFER] `hook_shot` düşerse teaser üretilemez, fakat canlı `hook_teaser.enabled=false` ve diğer kanallar `min_shots` kullanmayacak -> Genel hook fallback'ini bu acil yamaya katmayın, Issues List'e taşıyın
- [FIX] “Yayın gerçekleştiğinde alarm ve part kaydı” yalnız `produce.py`/`critic.py` kapsamıyla doğru uygulanamaz; gerçek upload sonucunu ve part state'ini `series_runner.py` bilir -> `ProduceResult` ile `dropped_shots` taşıyıp runner'da başarılı upload sonrası tek alarm ve part kaydı yazın ya da bu vaadi acil turdan çıkarın
- [FIX] ROCK 3 tek merdiven varmış gibi yazılmış, fakat görsel, ham native ses ve teslimat sesi için üç kopya retry döngüsü bulunuyor ve canlı arızalar ham ses yolunda da oluştu -> Retry/backoff'u ortak yardımcıya merkezleyip üç çağrı yolunu da ayrı test edin
- [KILL] 503/server hold'unu `QUOTA` diye adlandırmak teşhisi bozar ve ileride kota politikasına bağlanan yanlış davranış üretir -> Server sınıfını QUOTA'ya çevirmeyin; gerekiyorsa tipli `SERVER`/`TRANSIENT_INFRA` kodu ekleyin
- [FIX] “Tükenen kota hold'u QUOTA üretir” proof'u yeni davranışı kanıtlamıyor çünkü `_qc_api_reason_code("quota")` bugün zaten QUOTA döndürüyor -> 429 ardından fallback 503 gibi canlı karışık hata zincirinin nihai nedenini ve runner sonucunu test edin
- [FIX] QUOTA `_NON_RETRYABLE_REASON_CODES` içinde değildir ama yine de `retry_count` artırır; mevcut runner testi üçüncü QUOTA'da `needs_human` yazıp işaretçiyi sonraki bölüme ilerlettiğini açıkça kanıtlıyor -> “QUOTA sayılmaz” iddiasını çıkarın veya runner'a ayrı, sonlu altyapı retry bütçesi ve süre sınırı ekleyin
- [FIX] QUOTA'yı tamamen sayaç dışı bırakmak kalıcı kota/billing arızasında insan eskalasyonu olmayan sonsuz günlük retry döngüsü yaratır -> İçerik ve altyapı sayaçlarını ayırın, altyapı için de sonlu deneme/yaş eşiği sonunda insan alarmını koruyun
- [FIX] Sunucu `retryDelay` okumasının kaynağı, parse hatası davranışı, tek bekleme ve toplam bekleme tavanı tanımlı değil; artırılmış denemeler 120 dakikalık workflow'u aşabilir -> SDK metadata ve metin fallback'ini test edin, `max(single_delay)` ile `max(total_qc_wait)` sınırlarını koyun ve günlük kota için boşuna uyumayı kesin
- [FIX] Part 26 sayacını “iki başarısızlık da altyapıydı” diye sıfırlama gerekçesi repo kanıtıyla çelişiyor; iki koşu da çekim 2/4 continuity `final_reject` ile bitti -> Reset'i yeni kısmi-yayın politikasına verilmiş açık operatör override'ı olarak kaydedin, altyapı düzeltmesi diye yeniden yazmayın
- [FIX] Yalnız `retry_count=0` yapmak eski `last_reason_code`, `hold_reason` ve `first_held_at` alanlarını başarılı yayın kaydında bırakır -> Alanları atomik biçimde temizleyin veya ayrı bir `retry_history` altında arşivleyin
- [FIX] Billing doğrulanmadan tetikleme hâlâ yüzlerce video kredisi yakıp üçüncü başarısızlıkta part 26'yı `needs_human` yapabilir -> Ücretli kota teyidini state reset ve workflow dispatch öncesi zorunlu go/no-go kapısı yapın
- [FIX] Planın tam test proof'u mevcut hâliyle geçemez çünkü `tests/test_gercekcilik_rock3.py` canlı 1000 kredi tavanına karşı hâlâ 800 bekliyor -> Geçici 1000 kararını ve 800'e dönüş koşulunu test sözleşmesine açıkça işleyin
- [FIX] Üç yeni unit test; canlı bible, part 26 state'i, post-process, runner ve upload yolunu kapsamadığı için yeşil olup kanal yine yayınsız kalabilir -> Kabul kanıtını tek koşuda `status=published`, `platforms_ok` içinde YouTube, `next_part=27`, final medya süre/ses doğrulaması ve düşen çekim kaydı şartlarına bağlayın

VERDICT: NOT YET```

### Visionary yaniti (Claude)

Once dogrulama: uc iddiayi kendim kontrol ettim, ucu de DOGRU cikti.
- Anlatim: `bible.narration` dolu ve part26 tam anlatim metni tasiyor. Workflow
  yorumundaki "SESSIZ" ifadesi bayat. Benim varsayimim yanlisti.
- Test takimi: `origin/main` uzerinde `pytest tests/ -q` -> 2 failed, 599 passed.
- `chain_reset_pending`: produce.py 1519/1707/1868'de yaziliyor, 1452'de
  okunuyor, 1480'de sifirlaniyor. Ikinci bir durum degiskeni gereksiz.
  Ek bulgum: part26 cekimlerinde `chain` alani olmadigi icin 1452 dali HIC
  calismiyor, reset bilgisi bugun tamamen kayboluyor.

- ACCEPTED: Kok neden zincir karesi QC'sinin `state_carry`'yi bilmemesi ->
  ROCK 1 ikiye bolundu: 1a kok duzeltme (state_carry + SERIES EXEMPTION zincir
  denetimine de uygulanir), 1b emniyet agi olarak muafiyet kaldi.
- ACCEPTED: Yeni bookkeeping yaratma, mevcut `chain_reset_pending` snapshot'ini
  al -> ROCK 1 "Bookkeeping" bolumune yazildi.
- ACCEPTED: Muafiyet eksik/sema disi `continuity_ok` durumunu da kapsamali ->
  ROCK 1b ve proof vakasi (d).
- ACCEPTED: `previous_shot_dropped` domino riski -> tek "kirik cipa" sinyali,
  ilk basarili zincirde temizlenir. Proof vakasi (f).
- ACCEPTED: Uc kapiya ayri min_shots kontrolu yanlis erken iptal uretir ->
  tek `required_shot_count`, erken cikis yalniz `accepted + remaining < required`.
- ACCEPTED: `min_shots` tip/sinir sozlesmesi -> preflight dogrulamasi, ucretli
  cagri oncesi. Proof vakasi (e).
- ACCEPTED: "Sessiz seri" varsayimi yanlis -> ROCK 2'ye anlatim/sure bolumu ve
  dort dusus konumunun ayri testi eklendi; rol kaybi alarmda acikca yazilacak.
- DEFERRED: `hook_shot` yedegi -> ISSUES. Canli `hook_teaser.enabled=false`
  oldugu dogrulandi, acil turda gerekmiyor.
- ACCEPTED: Alarm ve part kaydi `series_runner` katmaninda olmali ->
  `ProduceResult.dropped_shots` ile tasinip BASARILI upload sonrasi yazilacak.
  Kisit listesi `series/series_runner.py` kapsayacak sekilde genisletildi.
- ACCEPTED: Uc kopya retry merdiveni -> ROCK 3a ortak yardimciya toplaniyor,
  uc yol ayri test ediliyor.
- ACCEPTED (KILL): Sunucu hatasini `QUOTA` diye adlandirmak -> plandan cikarildi.
  Ayri tipli altyapi kodu (`TRANSIENT_INFRA`) eklenecek, `QUOTA` yalniz gercek
  kota icin kalacak.
- ACCEPTED: Eski QUOTA proof'u yeni davranisi kanitlamiyor -> proof vakasi (e)
  karisik 429 + 503 zincirinin nihai nedenini test ediyor.
- ACCEPTED: QUOTA yine `retry_count` artiriyor -> yanlis iddia plandan
  cikarildi, "Duzeltilen yanlis varsayimlar" bolumune yazildi.
- ACCEPTED: QUOTA'yi tamamen sayac disi birakmak sonsuz dongu uretir ->
  ROCK 3d: sayaclar ayrilir ama altyapinin da SONLU butcesi ve insan
  eskalasyonu olur. Proof vakasi (g).
- ACCEPTED: `retryDelay` kaynagi, parse hatasi, tek ve toplam bekleme tavani
  tanimsiz -> ROCK 3a'ya yazildi, proof vakalari (a)(b)(c)(d).
- ACCEPTED: Part 26 sayac sifirlama gerekcesi kanitla celisiyor -> kapanis
  adimi 2 yeniden yazildi, acik operator override olarak kaydedilecek.
- ACCEPTED: Yalniz `retry_count` temizlemek bayat alan birakir -> ayni adimda
  `last_reason_code`, `hold_reason`, `first_held_at` atomik temizlenir.
- ACCEPTED: Billing dogrulanmadan tetikleme kredi yakar -> kapanis adimi 1
  zorunlu go/no-go kapisi oldu.
- ACCEPTED: Bayat kirmizi testler -> ROCK 4 eklendi.
- ACCEPTED: Uc unit test yesil olup kanal yayinsiz kalabilir -> kapanis adimi 4
  kabul kanitini gercek kosuya bagladi (published + YouTube kimligi +
  next_part=27 + medya dogrulamasi), adim 5 videoyu elle izletiyor.

Reddedilen bulgu yok.

## Round 2
### Integrator bulgular (Codex, birebir)
```
- [KILL] ROCK 1a’daki “SERIES EXEMPTION bugün zincir denetimine uygulanmıyor” iddiası yanlış; `review_chain_frame()` zaten `qc.notes` değerini `_review_frames()` çağrısına geçiriyor -> Yeni wiring eklemeyin, mevcut aktarımı regression testiyle kilitleyin
- [FIX] Yalnız `state_carry_expected` eklemek canlı hatayı çözmez; `_decide()` hâlâ `require_object_match` üzerinden kasıtlı deformasyon için dönen `object_match=false` sonucunu sert red sayar -> Zincir denetimine state-carry deformasyonuna izin veren ayrı kimlik sözleşmesi ekleyin ve `object_match=false + state_carry_ok=true + chain_frame_suitable=true` canlı şeklinin geçtiğini test edin
- [FIX] ROCK 2’nin “ses video süresini aşmaz” proof’u, `mix_voiceover()` anlatımın sonunu kestikten sonra da yeşil geçebilir -> Part 26’nın 18 saniyelik varyantında anlatımın tamamının yerleştiğini, `NARRATION_MAX_EXTEND` tavanına çarpılmadığını ve truncation warning oluşmadığını doğrulayın
- [FIX] ROCK 3’te “toplam QC bekleme tavanı” ortak helper çağrısı başına uygulanırsa yaklaşık on QC işiyle katlanıp 120 dakikalık workflow’u yine aşabilir -> Tek episode-wide paylaşılan bekleme bütçesi tanımlayın ve video üretimi, post-process ile upload için açık zaman tamponu bırakın
- [FIX] Tek ucuz Gemini çağrısının başarılı olması ücretli katmanı kanıtlamaz; ücretsiz kotada kalan tek çağrı da aynı sonucu verir -> Go/no-go kontrolünde Cloud projesinin billing/tier ve free-tier quota metriğini doğrulayın, test çağrısını yalnız anahtar/auth kontrolü sayın
- [FIX] Runner bugün herhangi bir platform başarılıysa part’ı `published` yapıp `next_part` değerini ilerletiyor; Instagram/TikTok başarılı fakat YouTube başarısız olduğunda hedef kanal karanlık kalır ve 500 kredi harcanmış olur -> Unnatural Lab için opt-in zorunlu platform olarak YouTube’u tanımlayın ve yalnız YouTube doğrulanınca published/advance ile kısmi-yayın alarmını çalıştırın
- [FIX] Kabul adımındaki “YouTube video kimliği dolu” şartının kaynağı belirsiz; part kaydı kimlik tutmuyor ve best-effort `published.json.results.youtube` başarılı upload sonrası bile null kalabiliyor -> Runner sonucunda YouTube kimliğini part’a kalıcı yazın veya kabulü YouTube API/public URL ile doğrulanmış yayın olarak kesin biçimde tanımlayın

VERDICT: NOT YET```

### Visionary yaniti (Claude)

Yedi bulgunun ikisini kodda birebir dogruladim, ikisi de DOGRU cikti:
critic.py:610-615 `_decide()` `object_match=false` gelince sert red veriyor
ve `review_chain_frame` `require_object_match`'i true geciriyor; ve
series_runner.py:753 `if ok:` herhangi bir platform basarisini yayin sayip
`next_part` ilerletiyor.

- ACCEPTED (KILL): SERIES EXEMPTION zaten zincir denetimine geciriliyor ->
  yanlis iddia ROCK 1a'dan cikarildi, yerine regresyon testi (h) kondu.
- ACCEPTED: state_carry tek basina yetmez, object_match sert red veriyor ->
  ROCK 1a kimlik sozlesmesi olarak yeniden yazildi; canli sekil
  (object_match=false + state_carry_ok=true + chain_frame_suitable=true)
  proof vakasi (a) oldu, gercek kimlik kaymasi vakasi (c) ile korundu.
- ACCEPTED: anlatim proof'u kesilmis anlatimla da yesil gecerdi -> proof
  vakasi (f) truncation uyarisi ve MAX_EXTEND tavani sartlarina baglandi.
  Not: bu riski bagimsiz olarak ben de bulmustum; Codex olcutu keskinlestirdi.
- ACCEPTED: toplam QC bekleme tavani cagri basina olursa katlanir -> ROCK 3a
  bolum genelinde PAYLASILAN tek butceye cevrildi, upload icin tampon birakildi.
- ACCEPTED: tek ucuz cagri ucretli katmani kanitlamaz -> kapanis adimi 1
  billing/tier ve free-tier kota metrigi dogrulamasina baglandi.
- ACCEPTED: herhangi bir platform yayin sayiliyor -> ROCK 2'ye opt-in
  `required_platforms` eklendi, unnatural-lab icin ["youtube"].
  Proof vakalari (h) ve (i).
- ACCEPTED (keskinlestirilerek): kabul kaniti belirsizdi -> kapanis adimi 4
  kesin tanima cevrildi. Not: part kaydi `platforms_ok` TUTUYOR
  (series_meta.py:149) ve published.json `results.youtube` kimligi tutuyor
  (part 22'de vKus2kyMIN0), yani kaynak belirsiz degil; kabul her ikisine
  birden baglandi.

Reddedilen bulgu yok.

## Round 3
### Integrator bulgular (Codex, birebir)
```
Önceki yedi bulgunun tamamı karşılanmış; yeni bir KILL/DEFER/FIX/CLARIFY bulgusu yok. Plan, belirtilen billing ve state onarımı sırası korunarak builder’a verilecek kadar net ve güvenli.

VERDICT: SAME PAGE```

### Visionary yaniti (Claude)

Yeni bulgu yok, VERDICT: SAME PAGE. Toplanti kapandi, insaya geciliyor.
Uc turda 27 bulgu kabul edildi, sifir bulgu reddedildi.
Kabul edilen bulgulardan besi kanalin yayinlamasini dogrudan engelleyen,
ilk planin kacirdigi sorunlardi (kimlik sozlesmesi, anlatim, kirmizi test
takimi, anlatim kesilmesi, platform ayrimi yapmayan yayin kurali).

## Insa: Codex kotasi bitti, Visionary direksiyonu aldi

Codex insanin ORTASINDA kullanim limitine takildi ("You've hit your usage limit").
Birakigi kismi is: 8 dosya degismis, 2 test dosyasi yazilmis; ROCK 3'un yarisi,
ROCK 4 ve test_qc_backoff.py HIC yapilmamis, ve HICBIR test calistirilmamisti.

Ilk deneme ayrica bosa gitti: `--sandbox workspace-write` ile Codex Windows'ta
hicbir dosyaya yazamadi, `BLOCKED` deyip durdu. Ikinci kosu sandbox'siz ama
git worktree izolasyonunda yapildi; ana depo bastan sona dokunulmadan kaldi
(kosu oncesi ve sonrasi `git status` karsilastirildi, ayni).

### Codex'in kismi isinde bulunan ve duzeltilen HATALAR

Taban: `origin/main` uzerinde 599 gecti / 2 kaldi. Codex'in kismi isiyle
takim **9 kaldi** , yani 7 testi BOZMUSTU. Kanit kendi kosumdan:

1. **`_classify_api_error` tipli sozlesmeyi bozdu.** Duz `429`'u artik "quota"
   saymiyordu (yalniz gunluk isaretli olanlari). ROCK C1 sozlesmesi buna
   dayaniyor; 5 test kirildi. DUZELTME: siniflandirma eski haline dondu, gunluk
   kota ayrimi yalnizca BEKLEME kararina taşındı (`_is_daily_quota_error`).
2. **Yedek modeli atlayan `break` (GERCEK REGRESYON).** Codex model dongusune
   `if last_reason == "quota": break` koymustu. Ucretsiz katman kotasi MODEL
   BASINA ayrilir (canli 429 govdesi:
   `GenerateRequestsPerDayPerProjectPerModel-FreeTier`), yani birincil model
   kotayi doldurdu diye yedek modeli hic denememek tam da kota krizinde
   dayanikliligi DUSURURDU. Uc yerden kaldirildi. Mutasyon testiyle dogrulandi:
   `break` geri konunca test kirmizi, kaldirilinca yesil.
3. **ROCK 3c ve 3d hic yapilmamisti.** `TRANSIENT_INFRA` kodu eklendi;
   altyapi hold'u artik ICERIK `retry_count` sayacini yakmiyor, kendi SONLU
   butcesinden (6 deneme VEYA 48 saat) harciyor ve butce dolunca yine
   `needs_human` + alarm uretiyor.
4. **ROCK 4 hic yapilmamisti.** Iki bayat kirmizi test, KORUDUKLARI davranis
   zayiflatilmadan bugunku bilincli kararlara hizalandi (1000 tavan icin
   `credit_cap_note`'ta 800'e donus kosulu artik ZORUNLU; chain_frames testi
   kapsam korumasini , chain_scope=episode + capraz-bolum kapali , koruyor).
5. **Platform karsilastirmasi buyuk/kucuk harfe duyarliydi.** Yayinci
   "YouTube" dondurse zorunlu platform "dogrulanmadi" sayilip kanal gereksiz
   yere karanlikta kalirdi. Iki taraf da normalize edildi.

### Kendi testlerimde bulunan ve duzeltilen HATA (bende)

Yazdigim `test_qc_backoff.py` GERCEK `sentinal_ihsan/unnatural-lab/series.json`
dosyasini EZDI: `terminalize_and_advance()` iceride `save_atomic()` cagirip
slug'dan turetilen gercek dosyaya yaziyor, ben yalniz `save`'i mocklamistim.
327 satirlik canli yapilandirma (logline, hashtags, auto_replenish brief,
families, music_style) 21 satirlik fixture'a dondu ve `next_part` 27 oldu.
Dort planner/golden testinin aniden kirmizi olmasi bu yuzdendi.
Dosya git'ten geri alindi (327 satir, next_part 26, auto_replenish yerinde),
ANA DEPO hic etkilenmedi. Testler artik uydurma slug kullaniyor ve
`save` + `save_atomic` ikisi de autouse fixture ile kapatiliyor.

### Eklenen kanitlar

- `tests/test_qc_backoff.py` (20 test): ROCK 3'un (a)-(g) vakalari, arti kendi
  adversarial eklerim , absurt sunucu gecikmesi (86400s) workflow'u asamaz,
  negatif/sifir gecikme negatif uykuya donmez, bolum butcesi CAGRI BASINA
  degil PAYLASILAN olmalı, ve gunluk kotada yedek model YINE denenir.
- `tests/test_chain_exemption_plumbing.py` (4 test): Codex'in zincir testleri
  muafiyeti yalniz `_decide()` seviyesinde dogruluyordu, yani "bayrak verilirse
  dogru davranir" diyordu. Kanali olduren hata ise bayragin HIC VERILMEMESIYDI.
  Bu dosya canli ariza senaryosunu (3 -> 4 sifirlanmasi) uretim dongusunde
  tekrar oynatip bayragin `qc_shot`'a ULASTIGINI kanitliyor, muafiyetin
  sonraki cekime SIZMADIGINI da. Mutasyon testiyle dogrulandi.

### Sonuc

`python -m pytest tests/ -q` -> **648 gecti, 0 kaldi** (taban: 599 gecti, 2 kaldi).
Testler sirasinda hicbir canli durum dosyasi yazilmadi.
