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
