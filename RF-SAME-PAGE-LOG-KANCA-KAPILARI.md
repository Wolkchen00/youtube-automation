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

## Round 2

### Integrator findings (Codex, verbatim)

Prior findings 1–3, 5–6, 9, 11, 13–14, 17–18, and 20–22 are addressed through corrections, removal, or explicit deferral. Findings 4, 7–8, 10, 12, 15–16, 19, and 23 remain partly addressed.

Read-only reproduction: vocabulary matching rejects exactly 19, 32, and 36 across parts 13–37. Applying the promised format scope rejects only 32 and 36. Removing `infinite`/`infinitely` creates **no additional false negative in the actual corpus**: those words occur only in 32 and 37, and 32 remains caught.

- [FIX] Section 0.5’s production claim fails on part 19 because its real JSON lacks `format_version`, making `format_plan_errors` return immediately -> distinguish the historical vocabulary test from format-scoped enforcement and test a properly formatted equivalent of part 19 without silently altering the historical fixture.
- [FIX] The claimed 25-file cohort is unspecified, and scanning all 37 files also matches parts 5 and 10, with part 10’s “NEVER-ENDING FOUNTAIN” recording 2,158 in calibration -> publish the fixture manifest and stop presenting temporal wording as sufficient evidence that an idea is measurably dead.
- [FIX] ROCK B still tests wording rather than first-frame readability, and optional `violation_observation` lets an event-dependent plan evade the second rule by omitting that field -> require a shot-1 observable-state claim and test omitted fields and equivalent paraphrases.
- [FIX] A regex-only test can pass while production bypasses the gate: `validate_plan_against_config` never calls `format_plan_errors` -> keep one rule implementation, but test `_validate_batch` at `replenish.py:1417`, preflight at `preflight.py:125`, and production at `produce.py:1398` and `1461`, which reach it through `validate_plan`; direct config validation does not.
- [FIX] Merely deriving `_OBSERVATION_RULE` from the new vocabulary leaves repair detection and acceptance checking the old regex, while globally changing its instructions affects other formats and later shots -> apply the new checks and instructions only to the relevant format and shot, and test the actual repair path.
- [FIX] Repair can remove an event-dependent phrase while leaving the underlying episode unchanged, defeating the intended idea rejection -> define semantic gate failures as requiring a new idea rather than cosmetic observation rewriting.
- [FIX] Section 1 calls A–B–C–D–E dependency order despite D being B’s hard prerequisite -> order it A–D–B–C–E or explicitly distinguish development order from atomic deployment.
- [FIX] ROCK D attributes part 30’s failure to plan rejection without evidence and calls a finite three-attempt retry lifecycle infinite; my earlier “infinite” wording was also incorrect -> describe the demonstrated loss of failure detail and test immediate typed rejection without consuming three production attempts.
- [CLARIFY] ROCK D still leaves “advance or replace” undecided, so its proof could pass by parking the episode indefinitely -> choose a concrete transition, preferably the existing atomic terminalize-and-advance path with an alert, and assert the next valid episode remains runnable.
- [CLARIFY] ROCK C still supplies neither literal regexes nor justified family mappings, although its proof demands disallowed-family cases -> specify the actual rules; allow every family where title form imposes no meaningful restriction rather than inventing exclusions to satisfy a test.
- [FIX] ROCK C will invalidate existing tests using live config with titles such as “Partial Proof A” and “Clean Batch A” -> migrate those fixtures to valid titles while preserving their prefix, repair, and rejection assertions.
- [FIX] ROCK A’s retained telemetry is written under ephemeral episode output, but the workflow uploads only logs and stems -> persist failed-attempt metadata in an uploaded location and test its survival after failure.
- [FIX] ROCK A still leaves the backoff bound unspecified and promises boundary-LUFS success even where no limiter setting satisfies both gates -> define the bound and require diagnostic fail-closed behavior for infeasible material, alongside feasible convergence tests.
- [FIX] ROCK E is implementable without changing the credit ledger or shared balance reservations, but its ownership and checkpoint contract is missing -> scope it to serialized Unnatural Lab runs, use immutable artifact checkpoints with an atomic manifest, and preserve existing spend accounting.
- [FIX] A `series:episode` key and byte integrity alone can reuse stale shots after plan, reference, or QC changes -> bind artifacts to plan/reference identity and matching QC evidence, and test invalidation and downstream chain dependencies.
- [FIX] Restoring artifacts inside production is too late because `run_next` performs `_budget_failure` first, while a complete master can still be blocked by production credit gates -> restore and validate before completion-cost calculation, and route a verified master directly to publication without production reservations.
- [FIX] ROCK E’s instruction to regenerate whenever integrity cannot be verified turns a temporary storage outage into fresh credit spending -> distinguish unavailable storage from confirmed corruption and stop with an actionable alert when recovery is uncertain.
- [FIX] Preserving the existing duplicate-title gate does not provide publication recovery because it returns failure for an existing YouTube title, fails open on lookup errors, and covers neither other platforms nor lost upload acknowledgements -> persist per-platform completion and pending request IDs, reconcile them before reposting, and test remote success followed by a local crash.
- [FIX] ROCK E’s two-run proof can pass using surviving local files or mocked cache acceptance while real GitHub recovery remains broken -> delete the first runner’s working files, restore only durable artifacts, retain the real ledger and QC checks, and assert completion plus zero regeneration of accepted shots.
- [CLARIFY] Part 33’s budget choice need not block offline implementation, but deploying A leaves the scheduled retry free to spend its remaining 404 credits before that choice is made -> settle the production hold, retry, or abandonment policy before deployment; no paid acceptance run is authorized by the build alone.

VERDICT: NOT YET
### Visionary response (Claude)

Turu 2'nin üç yapısal iddiası dosyaya karşı tek tek doğrulandı ve üçü de doğru
çıktı: (a) part 10/19/20 `format_version: None`, kapı onlara ulaşmıyor;
(b) part 10 calibration metriği 2158 ve başlığı `NEVER-ENDING` içeriyor;
(c) `shots.py:142` `if observation is not None:`, alan opsiyonel.
Bunlar ROCK B'nin kanıt temelini çökertti ve rock yeniden tasarlandı.

- ACCEPTED (1) part 19 `format_version` taşımıyor, üretim kapısı ona ulaşmıyor
  -> plan 0.3(a) yeniden yazıldı. Kapının gerçek kapsamı part 22+ ilan edildi,
  kapsam içi ölçülmüş ölü sayısı n=1 olarak dürüstçe yazıldı. Tarihsel fixture
  DEĞİŞTİRİLMEYECEK; part 19 için ayrı "biçimlendirilmiş eşdeğer" fixture yazılacak.
- ACCEPTED (2) fixture kohortu belirsiz, parts 5 ve 10 da eşleşiyor, part 10 = 2158
  -> DOĞRULANDI ve bu planın en önemli düzeltmesi oldu. Kelime listesinin sert red
  yetkisi ALINDI. Fixture manifestosu test dosyasında açıkça listelenecek.
- ACCEPTED (3) ROCK B kelime test ediyor, opsiyonel alan kaçış bırakıyor
  -> İhsan kararıyla rock ikiye ayrıldı: B1 yapısal kural REDDEDER,
  B3 kelime listesi yalnız BAYRAK takar. B2 alanı zorunlu yaparak kaçışı kapatır.
  Alan silerek kaçma denemesi ayrıca test edilecek.
- ACCEPTED (4) `validate_plan_against_config` `format_plan_errors`'ı çağırmıyor
  -> DOĞRULANDI (shots.py:432/447 üzerinden dört çağrı yeri). Plan 0.4'e çağrı
  yolu tablosu eklendi; kanıt regex birim testi değil, bu yolları kullanacak.
- ACCEPTED (5) talimatı global değiştirmek diğer formatları ve sonraki çekimleri
  etkiler -> yeni kurallar format-kapsamlı VE yalnız shot 1'e uygulanacak;
  gerçek onarım yolu test edilecek.
- ACCEPTED (6) onarım, olay-bağımlı ifadeyi silip fikri değiştirmeden bırakabilir
  -> B1 ihlali ONARILAMAZ ilan edildi; `_repair_episode_fields` yolunun dışında
  tutulacak ve bu test edilecek. Semantik red yeni fikir ister, metin rötuşu değil.
- ACCEPTED (7) sıralama D'yi B'den sonra gösteriyordu -> sıra A, D, B, C, E oldu.
- ACCEPTED (8) part 30'u plan reddine bağlamak kanıtsız, "sonsuz" da yanlıştı
  -> ROCK D yeniden yazıldı: yalnız KANITLANMIŞ olan iddia edildi (hata ayrıntısı
  kayboluyor, bölüm üç ücretli deneme tüketerek ölüyor, defterde 848 kredi).
  Kanıt artık "üç üretim denemesi tüketilmez" iddiasını test ediyor.
- ACCEPTED (9) "ilerle ya da değiştir" belirsiz -> mevcut atomik
  terminalize-and-advance yolu seçildi, alarm üretilecek, ve kanıt SONRAKİ geçerli
  bölümün koşulabilir kaldığını doğrulayacak. Belirsiz park etmek geçmiş sayılmaz.
- ACCEPTED (10) ROCK C aile eşlemesi gerekçesiz -> başlık biçimi anlamlı aile kısıtı
  dayatmadığı için her kalıp tüm kanonik ailelere eşlenecek, ve bu tercih
  gerekçesiyle plana yazıldı. Test geçirmek için uydurma dışlama YAZILMAYACAK.
- ACCEPTED (11) ROCK C mevcut fixture'ları kıracak -> DOĞRULANDI
  (`test_replenish_partial_batch.py` içinde "Partial Proof A", "Clean Batch A").
  Fixture'lar geçerli başlıklara taşınacak, önek/onarım/red iddiaları korunacak.
- ACCEPTED (12) ROCK A telemetrisi geçici çıktıya yazılıyor, iş akışı onu yüklemiyor
  -> telemetri kalıcı ve başarısızlıktan sonra okunabilir bir yere yazılacak,
  hayatta kalması ayrıca test edilecek.
- ACCEPTED (13) geri çekme sınırı tanımsız, sınır-LUFS başarı vaadi hatalı
  -> sınır tanımlanacak VE plan artık sınır malzemede başarı vaat ETMİYOR:
  iki kapıyı birden sağlayan ayar yoksa teşhis üreterek fail-closed durulacak.
- ACCEPTED (14) ROCK E sahiplik ve kontrol noktası sözleşmesi eksik
  -> serileştirilmiş unnatural-lab koşularına daraltıldı, değişmez eser
  kontrol noktaları ve atomik manifest yazıldı, harcama muhasebesi korunuyor.
  Eşzamanlı koşu sahipliği açıkça ISSUES'a düştü.
- ACCEPTED (15) `seri:bölüm` + bayt bütünlüğü bayat çekim kullandırabilir
  -> eserler plan ve referans kimliğine bağlanacak; planda zaten duran
  `doctrine_sha256` ve `ref_prompt_sha256` taşıyıcı olarak kullanılacak;
  geçersizleme ve zincir bağımlılığı test edilecek.
- ACCEPTED (16) üretim içinde geri yükleme geç kalıyor, `run_next` önce
  `_budget_failure` koşuyor -> geri yükleme ve doğrulama tamamlanma maliyeti
  hesabından ÖNCE yapılacak; doğrulanmış master üretim rezervasyonlarına
  girmeden doğrudan yayına yönlendirilecek.
- ACCEPTED (17) "doğrulanamazsa yeniden üret" depolama arızasını harcamaya çevirir
  -> erişilemeyen depolama ile doğrulanmış bozulma ayrıldı; kurtarma belirsizse
  koşu durur ve eyleme dönük alarm üretir.
- ACCEPTED-DEFERRED (18) mükerrer-başlık kapısı yayın kurtarma değil
  -> DOĞRU ve bu çevrimde YAPILMIYOR. ISSUES'a Codex'in özgül maddeleriyle
  birlikte düştü (fail-open arama hatası, tek platform kapsamı, kaybolan
  yükleme onayı, platform başına bekleyen istek kimliği, uzak-başarılı-yerel-çöktü
  senaryosu). Gerekçe: ölçülen kaybı tek bölüm (part 5); ROCK E'nin ölçülen
  kaybı 2.896 kredi. Öncelik ölçüme göre verildi.
- ACCEPTED (19) iki koşuluk kanıt hayatta kalan yerel dosyalarla sahte geçebilir
  -> kanıt sertleştirildi: birinci koşunun çalışma dosyaları silinecek, yalnız
  kalıcı eserler geri yüklenecek, gerçek defter ve gerçek QC korunacak,
  sıfır yeniden üretim iddiası doğrulanacak.
- ACCEPTED (20) part 33 kararı yapımı değil DAĞITIMI bloke eder
  -> plan bölüm 3 yeniden yazıldı: yapım offline ilerleyebilir, ama dağıtımdan
  önce tut/yeniden dene/terk et seçilmeli. Bu yapım hiçbir ücretli kabul
  koşusunu yetkilendirmiyor.

Özet: turu 2'nin 20 bulgusunun 19'u kabul edildi, 1'i kabul edilip ertelendi
(bulgu 18, yayın kurtarma, gerekçesi ölçülen kayıp büyüklüğü).
En önemli sonuç: ROCK B'nin sert red yetkisi kelime listesinden ALINIP
yalnız yapısal kurala verildi, ve `violation_observation` zorunlu yapılarak
kaçış yolu kapatıldı. Bu, İhsan'ın kararıdır (2026-09-10).

## Round 3

### Integrator findings (Codex, verbatim)

- [FIX] B2’s “zero migration” claim is false: queued plans and the prompt contract are compliant, but `tests/test_gercekcilik_rock2.py::raw_plan` and `tests/test_shot1_onset.py::plan_with_actions` omit shot-1 `violation_observation` and break clean-validation/plan-lint tests -> Add a valid shot-1 observation to both builders; update the golden only if prompt wording changes.
- [FIX] B1 reproduction matches only part 36 among parts 22–37 and no pre-format shot-1 prompt, but `^after`, `regardless of`, and `keeps <verb>ing` can reject readable states such as “Regardless of angle, the blue core is visible” -> Restrict hard rejection to explicit completed-event dependencies and make invariance/ongoing-state phrases observation-only.
- [FIX] B3’s never-reject contract conflicts with existing hard gates because `never` triggers `NEGATIVE_VIDEO_LANGUAGE`, `always/forever/eventually` trigger `TEMPORAL_OVERREACH`, and an anomaly descriptor is copied into prompts that are also hard-linted -> Define B3 precedence explicitly, exempt only its scoped fields/mechanically composed phrase from those old rejections, and test through actual `validate_plan`.
- [FIX] B1/B2 in `format_plan_errors` reach `_validate_batch:1417`, `preflight:125`, and `produce:1398/1461` but not direct config calls at `1411/119/1388`, while B3 cannot safely record or alert there because the function returns only errors and those paths invoke it repeatedly -> Add a pure structured-finding scanner, consume rejects in validation, and persist/alert B3 once at a deduplicated lifecycle seam.
- [FIX] Merely excluding B1 from `_repair_episode_fields` is insufficient because an observation matching both B1 and an existing repairable rule can enter whole-field repair and have B1 cosmetically erased -> Short-circuit all field repair for an episode carrying B1 and test a mixed phrase such as “After being rolled, the dice always land alike.”
- [FIX] ROCK B’s proof does not exercise the real replenish loop, where a first-position unrepairable failure causes six new-generation attempts then a loud exception, while a later failure yields the longest valid prefix plus an alert -> Add `generate_plans`/`replenish` integration tests for both positions and assert an empty result never returns green.
- [FIX] ROCK C’s all-family mapping still enforces title shape but makes its family branch tautological, and the plan still omits the literal three regexes, allowing implementation and proof to invent a permissive contract together -> Put the exact `re.fullmatch` patterns and boundary cases in the plan before build.
- [FIX] ROCK A says the cumulative limiter backoff limit is explicit but provides no numeric limit -> Specify the maximum cumulative dB reduction and exact fail-closed diagnostic at that boundary.
- [CLARIFY] ROCK A and ROCK E promise persistent or durable artifacts without naming the authoritative storage backend, retention, deterministic key, or clean-checkout discovery mechanism -> Will this extend the existing GitHub Release path, or use another explicitly named store with tested retention and atomic-manifest semantics?
- [FIX] ROCK E incorrectly treats `doctrine_sha256` and `ref_prompt_sha256` as sufficient identity because the former is shared across plans and the latter excludes shot prompts and actual reference bytes, while restored shots also fail `_revalidate_cached_shot` without restored `qc_log.jsonl` evidence -> Bind checkpoints to a normalized full-plan hash, reference-content hash, QC-policy fingerprint, and persisted QC-pass evidence before completion-cost calculation.
- [FIX] Deferring publication recovery violates the Core Focus because partial success causes successful Instagram/TikTok posts to be uploaded again, while a lost YouTube acknowledgement can trigger the duplicate-title gate forever without advancing local state -> Include minimal durable per-platform completion/request IDs, reconciliation, and already-successful-platform skipping in ROCK E.
VERDICT: NOT YET
### Visionary response (Claude)

Turu 3'ün doğrulanabilir iddialarının hepsi dosyaya karşı kontrol edildi:
`test_gercekcilik_rock2.py::raw_plan` ve `test_shot1_onset.py::plan_with_actions`
gerçekten shot 1 gözlemi yazmıyor (ikisinde de sayı sıfır);
`NEGATIVE_VIDEO_LANGUAGE` gerçekten `never` yakalıyor;
`series/approver.py::_download_release` ve `series_runner.py:820` `release_tag`
gerçekten var. Üçü de kabul edildi.

- ACCEPTED (1) B2'nin "sıfır göç" iddiası yanlış -> DOĞRULANDI. İki test
  kurucusu adıyla plana yazıldı; ikisine geçerli shot 1 gözlemi eklenecek,
  golden yalnız prompt metni değişirse güncellenecek.
- ACCEPTED (2) `regardless of` ve `keeps <fiil>ing` okunabilir DEĞİŞMEZLİK
  durumlarını reddedebilir -> B1'den ÇIKARILDI, çıplak `^after` de çıkarıldı.
  B1 artık yalnız TAMAMLANMIŞ OLAY bağımlılığını yakalıyor
  (`after being <fiil-mis>`, `after (it|the|they|each|every) <fiil-mis>`,
  `once (it|the|they) (is|are|was|were|has|have) <fiil-mis>`,
  `having been <fiil-mis>`). Part 36 hâlâ yakalanıyor ("After being rolled").
  Çıkarılan ifadeler B3 bayrağına indi ve okunabilir bir `regardless of`
  gözleminin REDDEDİLMEDİĞİ ayrı bir regresyon testi olarak yazıldı.
- ACCEPTED (3) B3'ün "asla reddetmez" sözleşmesi mevcut sert kapılarla çelişiyor
  -> DOĞRULANDI ve plana açık ÖNCELİK KURALI yazıldı: B3 hiçbir mevcut reddi
  zayıflatmaz ve hiçbir yeni red eklemez. Üç çakışma adıyla belgelendi
  (NEGATIVE_VIDEO_LANGUAGE'in `never`i, TEMPORAL_OVERREACH'in dört kelimesi,
  anomaly_descriptor'ın prompt'a birebir kopyalanması). Öncelik `validate_plan`
  üzerinden test edilecek.
- ACCEPTED (4) B3 `format_plan_errors` içinde kayıt/alarm üretemez, o fonksiyon
  yalnız hata döndürüyor ve tekrar tekrar çağrılıyor -> B3 saf, yan etkisiz bir
  TARAYICI olarak yazılacak; redler doğrulamada tüketilecek; bayraklar yaşam
  döngüsünde TEK tekilleştirilmiş noktada kaydedilecek. Mükerrerlik testi eklendi.
- ACCEPTED (5) B1'i yalnız `_repair_episode_fields` dışında tutmak yetmez
  -> B1 taşıyan bölümde ALAN ONARIMININ TAMAMI kısa devre yapacak. Codex'in
  verdiği karışık ifade (`After being rolled, the dice always land alike.`)
  birebir test vakası olarak plana yazıldı.
- ACCEPTED (6) kanıt gerçek ikmal döngüsünü çalıştırmıyor -> `generate_plans` /
  `replenish` üzerinden iki entegrasyon testi eklendi: birinci sıradaki
  onarılamaz başarısızlık (yeni üretim denemeleri, sonra gürültülü istisna) ve
  sonraki sıradaki başarısızlık (en uzun geçerli önek artı alarm). Her iki
  durumda boş sonucun asla yeşil dönmediği iddia ediliyor.
- ACCEPTED (7) ROCK C literal regexleri hâlâ yok, tüm-aile eşlemesi totolojik
  -> üç regex ÖLÇÜLEREK yazıldı ve plana literal olarak kondu: parts 22-37'nin
  16 başlığı kabul (her biri tam bir kalıba), 9 saldırgan varyant red.
  Tüm-aile eşlemesinin TOTOLOJİK olduğu gizlenmedi, açıkça kabul edildi ve
  ISSUES'a ayrı madde olarak düştü. Test geçirmek için uydurma dışlama yazılmayacak.
- ACCEPTED (8) ROCK A kümülatif sınır sayı vermiyordu -> sayı kondu:
  başlangıç `target_tp` değerinden en fazla 3,0 dB toplam indirim
  (-1,0 hedefinde tavan en fazla -4,0 dBTP). Sınırda fail-closed davranış ve
  teşhis çıktısı tanımlandı.
- ACCEPTED (CLARIFY) depolama backend'i adlandırılmamıştı -> mevcut GitHub
  Release yolu adıyla seçildi ve doğrulandı: `series/approver.py::_download_release`,
  `_cleanup_release`, `series_runner.py:820` `release_tag`, `series_runner.py:441`
  tamamlanma üçlüsü. Yeni depo icat edilmeyecek. ROCK A telemetrisi de
  adlandırıldı: `logs/` altına yazılacak, çünkü iş akışı
  (`.github/workflows/unnatural-lab.yml:131-137`) yalnız `logs/` ve stems
  klasörlerini `always()` ile yüklüyor; bölüm çıktı klasörü yüklenmiyor.
- ACCEPTED (10) `doctrine_sha256` planlar arasında paylaşılıyor,
  `ref_prompt_sha256` çekim prompt'larını ve referans baytlarını dışlıyor,
  geri yüklenen çekim `qc_log.jsonl` kanıtı olmadan `_revalidate_cached_shot`
  kapısından geçemez -> kimlik dörtlüsü yazıldı: normalize tam plan özeti,
  referans içerik özeti, QC politika parmak izi, kalıcılaştırılmış QC-geçiş kanıtı.
- ACCEPTED (11) yayın kurtarmayı ertelemek YENİ TUZAK yaratıyor
  -> v3'teki erteleme GERİ ALINDI. Codex haklı: eserler kalıcılaşınca kısmi
  başarıda IG/TikTok yeniden gönderilir ve kaybolan YouTube onayı mükerrer-başlık
  kapısını sonsuza kadar tetikler. Asgari yayın kurtarma ROCK E kapsamına alındı:
  platform başına tamamlanma ve bekleyen istek kimlikleri, yeniden göndermeden
  önce mutabakat, zaten başarılı platformun atlanması, ve
  "uzak başarılı, yerel çöktü" senaryosunun testi.

Özet: turu 3'ün 11 bulgusunun 11'i de kabul edildi, hiçbiri reddedilmedi.
En büyük iki değişiklik: B1'in kapsamı okunabilir değişmezlik ifadelerini
dışarıda bırakacak şekilde DARALTILDI, ve v3'te ertelenen yayın kurtarma
ROCK E'ye GERİ ALINDI.
