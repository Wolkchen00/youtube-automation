# RF SAME PAGE LOG , kanca kapilari (unnatural-lab)

Plan dosyasi: RF-PLAN-KANCA-KAPILARI.md
Codex: codex-cli 0.152.1, model gpt-5.6-sol, reasoning effort high
Codex thread: 01a08bd6-70ef-7973-9cae-b442f2c7d1f0

## Round 1

### Integrator findings (Codex, verbatim)

- [FIX] Section 0.1 attributes two continuity samples to `calibration.json`, but that snapshot contains only part 19 and reports n=1 -> cite part 32’s later report separately and label the combined n=2 dataset honestly.
- [FIX] The data makes continuity a credible suspect and disproves title as the sole explanation, but seven confounded “I Found…” results do not prove that title form is neutral or that continuity is the sole cause -> present both as hypotheses rather than overruling the report categorically.
- [FIX] Section 0.4 says ten parts never reached YouTube but lists only seven, while part 5 is “published” in `series.json` yet has a null YouTube result in `published.json` -> reconcile the two truth sources and enumerate parts 1, 2, and 5 or narrow the claim.
- [FIX] ROCK 1’s lexical blacklist neither measures deadness nor reliably represents first-frame readability, since synonyms evade it while visible duplication and impossible interiors can be false positives -> use the simpler series-scoped continuity quarantine plus a structured shot-1 observable-state contract.
- [FIX] The proposed ROCK 1 gate immediately invalidates queued part 36 through existing “always” and part 37 through new “infinitely,” contrary to the claimed parts 33–37 compatibility -> deliberately reject and replace those plans or narrow the rule, with an explicit migration test.
- [FIX] Widening shared `TEMPORAL_OVERREACH` changes future `violation_observation` behavior fleet-wide even though no existing non-unnatural plan currently matches -> introduce a separate opt-in first-frame regex instead of modifying the shared observation regex.
- [FIX] `_OBSERVATION_RULE` still teaches only the old four forbidden terms, so repair calls can emit newly forbidden vocabulary and waste the bounded repair budget -> derive repair instructions and validation from one vocabulary source.
- [FIX] A plan rejected during production becomes an untyped `UNKNOWN` failure and retries the unchanged file rather than being replaced -> return typed `CONTENT_REJECT` evidence and define an alerting replacement/advance lifecycle before enabling the gate.
- [KILL] ROCK 1’s silent-shrink sub-rock fixes behavior already covered by partial-batch alerts and a zero-prefix exception that makes the replenish command red -> retain the existing path and only enrich its payload with exact rejection counts and reasons.
- [CLARIFY] ROCK 2 omits the literal regexes and family mappings, and its singular “This” specification conflicts with part 36’s required “These” match -> specify the exact reviewed configuration before implementation.
- [FIX] ROCK 2 promises a 75-character limit while `_validate_batch` rejects anything over 60, and all proposed fixtures are below 42 characters -> align the contract at 60 or change the validator deliberately and test the 60/61 boundary.
- [FIX] ROCK 2’s proof could pass with overbroad regexes or meaningless all-family mappings -> test each pattern’s positive boundary, malformed near-matches, and every intended disallowed-family pairing.
- [FIX] Part 33 proves only the final rounded -0.9 dBTP result because failed-attempt telemetry is deleted, so the asserted AAC mechanism remains an inference -> preserve attempt-level limiter, TP, and LUFS metadata on failure and validate against codec-real material.
- [FIX] ROCK 3’s proposed mocked sequence would pass the unchanged implementation because the mock supplies a passing second measurement independently of the limiter setting -> assert a minimum 0.3 dB limiter movement and add a real AAC convergence test.
- [FIX] ROCK 3 leaves the cumulative backoff cap unspecified and can push material already at -15 LUFS outside the integrated-loudness gate -> define the cap and test boundary LUFS, repeated overshoot, and no-feasible-intersection behavior.
- [FIX] ROCK 3 alone cannot rescue part 33 because its generated media was not persisted, its durable spend is already 596/1000, and a fresh runner needs roughly 400 credits for four main shots -> recover a durable artifact or obtain an explicit budget decision before allowing the retry.
- [KILL] ROCK 4 duplicates the existing `CapAwareRegenAllocator` protection for not-yet-authorized main shots while missing the actual cross-run loss of accepted shots -> replace it with durable partial-shot recovery and atomic episode ownership, which cannot remain out of scope.
- [FIX] ROCK 4’s 400-credit “completion floor” funds only one estimated main call per missing shot and cannot guarantee QC acceptance or survive a failed paid call -> define a recoverable completion artifact and retry budget rather than calling one-attempt funding a completion guarantee.
- [FIX] ROCK 4’s proof passes if the episode merely avoids `budget_exhausted` while producing no video or looping in `qc_retry` -> require an end-to-end restart test that yields a durable publishable video without exceeding the cap.
- [DEFER] ROCK 5 improves forensics but neither rejects dead ideas nor prevents a produced episode from dying before publication -> move it behind the missing durable publication-handoff rock.
- [FIX] When ROCK 5 resumes, `series_runner` cannot recover exception type, stage, or subprocess code from the many `produce.py` branches that swallow errors and return `None`, so its fake-failure proof can pass while real failures remain blank -> propagate typed failure evidence from each production boundary and test a real `None` path.
- [FIX] Truncating raw exception text to 500 characters does not prevent API-key, URL-token, or personal-data leakage -> store an allow-listed structured record and redact secrets before persistence or alerts.
- [FIX] No rock closes the core auto-mode produced-to-published gap: a failed upload stores an ephemeral local path, returns false, and the next GitHub runner regenerates instead of retrying publication -> reuse the Release persistence path before upload and add duplicate-safe publish-only recovery.

VERDICT: NOT YET
### Visionary response (Claude)

Doğrulama notu: aşağıdaki her kabul, Codex'in raporuna değil, dosyanın kendisine
bakılarak doğrulandı. Dört yapısal iddia tek tek koda karşı kontrol edildi ve
dördü de doğru çıktı.

- ACCEPTED (1) calibration.json continuity için n=1, part 32 anlık görüntüden sonra
  yayınlanmış -> plan 0.1 düzeltildi, part 32'nin 146 sayısı REELYZE raporundan
  geldiği açıkça yazıldı, birleşik n=2'nin iki kaynaktan derlendiği söylendi.
- ACCEPTED (2) yedi "I Found" sonucu karıştırıcı, başlık nötr diye kanıtlanamaz
  -> plan 0.2 yeniden yazıldı: veri başlığı TEK açıklama olmaktan çıkarır ama
  nötr olduğunu kanıtlamaz. Operasyonel sonuç iki hipotezden bağımsız olduğu için
  değişmedi, ama ROCK C'den performans iddiası türetilmeyeceği açıkça yazıldı.
- ACCEPTED (3) 10 dendi 7 listelendi, part 5 çelişkili -> plan 0.4 tam sayıma
  çevrildi: 33 bölümün 23'ü YouTube'a ulaştı, parts 1, 2, 5 dahil tam liste yazıldı.
  Part 5 çelişkisi ISSUES'a düştü.
- ACCEPTED (4) kelime kara listesi ilk-kare okunurluğunu ölçmüyor -> DOĞRULANDI VE
  ÖLÇÜLDÜ. İlk taslak part 37'yi ("infinitely deep", impossible-interior, aile
  medyanı 1196) yanlış reddediyordu; oradaki kullanım uzamsal ve shot 1 gözlemi
  anomaliyi tek karede gösteriyor. Kural yeniden tasarlandı: sınırsız-nicelik
  sözlüğü + shot 1'e özel önceki-olaya-bağlılık kuralı. 25 gerçek plan üzerinde
  ölçüldü, sonuç plan 0.5'te tablo halinde: part 19, 32, 36 red; diğer 22 geçer;
  yanlış pozitif yok. infinite/infinitely listeden çıkarıldı.
- ACCEPTED (5) kapı part 36 ve 37'yi geçersiz kılıyor -> DOĞRULANDI. Part 36
  gerçek pozitif (anomalide "always", shot 1'de "After being rolled"), part 37
  yanlış pozitifti ve kural değişikliğiyle artık geçiyor. Part 36'nın göç yolu
  ROCK D'ye bağlandı ve ROCK B'nin ön koşulu yapıldı.
- ACCEPTED (6) paylaşılan TEMPORAL_OVERREACH'i genişletmek filo geneli davranış
  değiştirir -> paylaşılan sabit DEĞİŞTİRİLMEYECEK. tek-obje-4x6 formatına ait
  ayrı, opt-in regex çifti eklenecek; diğer serilerin davranışının bit düzeyinde
  aynı kaldığı test edilecek.
- ACCEPTED (7) _OBSERVATION_RULE yasak kelimeleri elle sayıyor (satır 1471-1475,
  doğrulandı) -> onarım talimatı doğrulayıcının sözlüğünden türetilecek.
- ACCEPTED (8) kapıdan düşen plan UNKNOWN'a düşüp aynı dosyayı yeniden deniyor
  -> ROCK D olarak ayrı rock yapıldı ve ROCK B'nin ön koşulu ilan edildi.
- ACCEPTED-KILL (9) silent-shrink alt maddesi mevcut kısmi-parti alarmının kopyası
  -> alt madde KALDIRILDI. Yeni mekanizma yazılmayacak, var olan alarmın yüküne
  red sayısı ve sebebi eklenecek.
- ACCEPTED (10) ROCK C regexleri yazılmamış, part 36 "These" istiyor -> kalıp 3
  tekil ve çoğul özneyi kabul edecek; literal regexler bu turda yazılıyor.
- ACCEPTED (11) 75 vs 60 çelişkisi -> DOĞRULANDI (replenish.py:1093 `len(title) > 60`).
  Sözleşme 60'ta birleştirilecek, title_style metnindeki 75 sayısı 60 yapılacak,
  60/61 sınırı test edilecek. Brief'e dokunulan tek yer bu ve bilerek yapılıyor.
- ACCEPTED (12) ROCK C kanıtı aşırı geniş regexle de geçer -> her kalıbın pozitif
  sınırı, yakın-eşleşen bozuk varyantları ve izin verilmeyen aile eşleşmesi ayrı
  ayrı test edilecek.
- ACCEPTED (13) part 33 yalnız yuvarlanmış -0,9 sonucunu kanıtlıyor, AAC mekanizması
  çıkarım -> kabul edildi ve plana dürüstçe yazıldı. ROCK A artık ÖNCE deneme
  düzeyi telemetriyi koruyor, SONRA düzeltiyor.
- ACCEPTED (14) mock ikinci ölçümü limiter ayarından bağımsız verirse düzeltilmemiş
  kod da yeşil geçer -> kanıt sertleştirildi: limiter tavanının filtre dizesinden
  okunarak en az 0,3 dB hareket ettiği ayrıca doğrulanacak, artı gerçek AAC
  malzemesiyle yakınsama testi.
- ACCEPTED (15) kümülatif geri çekme tavanı tanımsız, -15 LUFS malzeme riski
  -> tavan açıkça tanımlanacak, sınır LUFS ve tekrarlı aşım test edilecek.
- ACCEPTED (16) ROCK A part 33'ü kurtarmaz, 596/1000 harcanmış -> DOĞRULANDI
  (credits_ledger.json episode_spend "unnatural-lab:33" = 596.0). Plan bölüm 3'e
  açık bir İHSAN KARARI maddesi eklendi.
- ACCEPTED-KILL (17) ROCK 4 CapAwareRegenAllocator'ın kopyası, gerçek kayıp koşu
  sınırında -> DOĞRULANDI (critic.py:1085, docstring birebir bu korumayı tarif
  ediyor; produce.py:1500 kullanıyor). ROCK 4 KALDIRILDI, yerine ROCK E kondu:
  koşu sınırında kaybolan üretim. core/video_vault.py var ama series/ boru hattında
  hiç kullanılmıyor, bu da doğrulandı.
- ACCEPTED (18) 400 kredilik taban tek deneme finanse eder -> ROCK 4 ile birlikte
  düştü, ROCK E kalıcı eser kurtarma üzerine kuruldu.
- ACCEPTED (19) ROCK 4 kanıtı video üretmeden de geçer -> ROCK E kanıtı uçtan uca
  yapıldı: kabul edilmiş çekimler yeniden üretilmeden tamamlanma, tavanı aşmama,
  ve mükerrer yayın kapısının tutması.
- PARTIALLY REJECTED (20) ROCK 5 ertelensin -> Core Focus'a doğrudan hizmet
  etmediği kabul edildi, ama bulgu 8 onu ROCK B'nin ÖN KOŞULU yapıyor. Bu yüzden
  silinmedi, DARALTILDI: yalnız içerik reddi yolu tipleniyor (ROCK D). Genel
  adli inceleme işi ISSUES'a düştü.
- ACCEPTED-DEFERRED (21) produce.py birçok dalda hatayı yutup None dönüyor
  -> genel tipli hata kanıtı altyapısı bu çevrimde YAPILMIYOR, ISSUES'a düştü.
  ROCK D kapsamı yalnız içerik reddi olarak yazıldı.
- ACCEPTED (22) 500 karaktere kırpmak sızıntıyı engellemez -> ham metin yerine
  izin listeli yapılandırılmış kayıt (alan adı, yakalanan ifade, kural adı).
- ACCEPTED (23) üretilmişten yayınlanmışa geçiş açığı hiçbir rock tarafından
  kapatılmıyor -> ROCK E kapsamına alındı: başarısız yükleme sonraki koşuda
  üretimi değil yalnız yüklemeyi tekrarlayacak.

Özet: 23 bulgunun 21'i kabul edildi, 2'si KILL olarak kabul edilip plandan
çıkarıldı (silent-shrink alt maddesi, ROCK 4), 1'i kısmen reddedildi
(ROCK 5 silinmedi ama daraltıldı ve ROCK B'nin ön koşulu yapıldı).
Rock sayısı 5 kaldı ama içerik değişti: ROCK 4 gitti, ROCK D ve ROCK E geldi.
