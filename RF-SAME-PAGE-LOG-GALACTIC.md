# RF Same Page Log: galactic_experience ses/kunye/yayin kapisi/baslik

Plan: RF-PLAN-GALACTIC-SES-KUNYE.md
Codex: gpt-5.6-sol, effort=high, thread 01a08bd9-2f79-75e3-b3fe-e9374c42b952

## Round 1
### Integrator findings (Codex, verbatim)

- [KILL] Rock 4’s CTR-oriented `title_style` and episode-title rewrites do not serve the Core Focus, and its proof accepts titles matching none of the proposed patterns -> Cut the title initiative and move only the required part32–35 title-card backfill into Rock 2.
- [FIX] `event-horizon` remains on state-machine v1, so an `AUDIO_MASTER` hold becomes `awaiting_approval`, later runs skip it while returning success, and the channel stops indefinitely -> Add an event-horizon-only finite recovery migration and state explicitly that mastering can halt the whole channel; `unnatural-lab` part33 proves this failure is real.
- [FIX] Enabling `master_lufs` makes `tests/test_rocka_audio_master.py::test_only_unnatural_lab_has_master_lufs` fail because it asserts that Unnatural Lab is the sole configured series -> Update that existing fleet guard to expect exactly Unnatural Lab and Event Horizon without modifying either owned Sentinal file.
- [FIX] The proposed skippable synthetic-tone test can pass without ffmpeg and separately tests configuration and a utility without proving Event Horizon’s narration-plus-music delivery -> Add a non-skippable publishing-runner smoke test over the Event Horizon mix that measures the final artifact’s LUFS, true peak, and narration audibility.
- [FIX] Title-card rendering is fail-open twice—`title_card_overlay` copies the untouched input on ffmpeg failure and `produce.py` catches errors before publishing anyway—so every proposed proof can pass while the video contains no text -> Make `title_card` an event-horizon required delivery layer, fail closed on copy-through/render failure, and inspect pixels from the rendered upper-third in an integration test.
- [FIX] The alleged cfg allowlists at replenish lines 145 and 216 are actually fixed-frame and strict-validation trigger lists, while the plan misses the schema comment, exact boolean validation, and the contradictory year instruction in `tc_rule` around line 695 -> Prefer `"year_required": false` inside the existing `bible.series.title_card` object, or update every documented, prompt, validation, normalization, produce, and preflight consumer with default-true tests.
- [FIX] The new prompt promises title ≤40 characters, subtitle ≤6 words, and the brief says 3–7 words, while normalization and proof still accept 60 characters for both -> Define one readable event-horizon contract and enforce the same limits in generation, hand-plan validation, and tests without changing legacy-series limits.
- [FIX] Rock 4’s proof only parses JSON and current preflight never validates `title_card`, so malformed hand-edited cards can pass while production skips the overlay -> Run `series.preflight` for all four final files and make it call the same title-card validator used by replenishment and production.
- [CLARIFY] The plan supplies none of the actual part32–35 `title_card` strings, so their factual accuracy, word limits, and readability cannot be reviewed -> What exact title and subtitle will be written into each queued plan?
- [FIX] `EPISODE_DEGRADED` is rejected by `ProduceResult.__post_init__` and is absent from its Literal domain and migration registry, so the proposed typed failure cannot reach retry handling -> Add it to `series/produce.py`’s complete reason-code domain, runner migration registry, and exact-domain tests before constructing the failure.
- [FIX] A gate placed immediately before `_publish_part` occurs after the existing non-OK retry branch, `mark_produced`, approval handling, and `--no-publish`, so an OK result with degraded coherence does not naturally enter the claimed retry path -> Convert the result to a typed recoverable failure immediately after result normalization and before all produced/approval/publish branches.
- [FIX] With a configured duration band, an unreadable duration becomes `duration_in_band=None` and `degraded=False`, allowing an unmeasured artifact to publish -> For opted-in Event Horizon require a present coherence report and `duration_in_band is True`, treating missing measurement as a recoverable hold.
- [FIX] `[14,26]` does not reject recorded healthy parts 28, 30, and 31 at 16.62, 16.62, and 19.62 seconds, but the plan omits parts26–27 and offers no evidence for a 26-second upper limit on an 18-second format -> Cite all six coherence records, retain the supported lower cutoff, and derive or tighten the upper cutoff from measured maximum valid render extension.
- [FIX] `bool(series.get("block_degraded_publish", False))` treats malformed values such as `"false"` or `1` as enabled and can unexpectedly stop production -> Opt in only with JSON `true`, reject non-booleans during preflight, and test absent, false, and malformed values.

VERDICT: NOT YET
### Visionary response (Claude)

Her bulgu once bagimsiz olarak dogrulandi (kod okumasi + gercek veri), sonra karara baglandi.

- **REJECTED** [KILL] Rock 4 baslik girisimi -> Ihsan bu turda basligi VE kuyrugu
  yenilemeyi acikca secti (Owner's Box karari, 10 Eylul). Core Focus'a hizmet ettigi
  gerekce: kanalin sorunu sadece teslimat degil, tiklanma. Ancak proof elestirisi
  HAKLI ve kabul edildi: artik dort baslik plana tam metin olarak yazildi ve test
  birebir esitlik, ALL-CAPS sayimi ve emoji yoklugu ariyor.
- **ACCEPTED** [FIX] state machine v1 -> `series_runner.py:650,659,773` okundu.
  Dogrulandi: `state_machine_version` yok, varsayilan 1, `_record_recoverable_failure`
  hic cagrilmiyor, `qc_hold` -> `awaiting_approval` -> her kosu True donuyor.
  `unnatural-lab` part 33 kaniti da dogrulandi (`qc_retry`, `AUDIO_MASTER`,
  retry_count 1, "master teslim sozlesmesi 3 denemede tutulamadi"). Bu bulgu plani
  degistirdi: yeni **ROCK 0** eklendi ve ROCK 1'in onkosulu yapildi.
- **ACCEPTED** [FIX] `test_only_unnatural_lab_has_master_lufs` -> dosya okundu,
  satir 117-128'de `assertEqual(found, [(expected, -14)])`. Dogrulandi. ROCK 1'e
  zorunlu yan degisiklik olarak yazildi; `sentinal_ihsan/` altindaki dosyalara
  dokunulmuyor, degisen yalniz test dosyasi.
- **ACCEPTED** [FIX] atlanabilir sentetik ton testi -> proof yeniden yazildi:
  ffmpeg SKIP etmeyen, event-horizon karisimini taklit eden (anlatim + kisik muzik)
  bir miks uzerinde calisan, cikti LUFS/TP olcen ve anlatim bandinin en az 6 dB
  yukseldigini dogrulayan test.
- **ACCEPTED** [FIX] kunyede iki katli fail-open -> `core/ffmpeg_tools.py:1431-1436`
  okundu, ffmpeg hatasinda `shutil.copy2` ile girdi kopyalaniyor ve fonksiyon basarili
  donuyor; `produce.py:2107-2109` istisnayi yutuyor. Dogrulandi. Cozum mevcut
  `required_layers` sozlugune baglandi (`produce.py:1359`), yeni bir mekanizma
  uydurulmadi. Piksel kontrollu test proof'a girdi.
- **ACCEPTED** [FIX] replenish 145/216 yanlis tanimlanmisti -> okundu, ikisi de
  `fixedframe_keys` / `strict_plan_validation_enabled` tetikleyicisi. Plan yanlisti;
  oraya anahtar eklemek alakasiz dogrulamayi acardi. Codex'in onerisi alindi:
  alan `bible.series.title_card.year_required` oldu. `bible` degiskeninin dogrulama
  noktasinda kapsamda oldugu `if bible.slug == "flashpoints"` satiriyla teyit edildi.
- **ACCEPTED** [FIX] 40/48/60/3-7 kelime celiskisi -> `tc_shape` (652) ve `tc_rule`
  (695) okundu: title 40, subtitle 48 istiyor; normalizasyon 60 kabul ediyor; brief
  3-7 kelime diyordu. Tek sozlesme yazildi: `year_required` False olan seriler icin
  her yerde 40/48; eski seriler bugunku 60'ta birakildi.
- **ACCEPTED** [FIX] Rock 4 proof'u sadece JSON parse ediyordu -> proof `series.preflight`
  cagirmaya cevrildi ve preflight'a paylasilan kunye dogrulamasi eklendi.
- **ANSWERED** [CLARIFY] part32-35 kunye metinleri -> dort baslik ve dort kunye plana
  tam metin olarak yazildi (bkz. ROCK 4 tablosu). Fakt, synopsis, narration, family,
  seed_id ve doctrine_sha256 degismiyor.
- **ACCEPTED** [FIX] `EPISODE_DEGRADED` `ProduceResult` alanina girmiyor ->
  `produce.py:82-105` okundu, `__post_init__` kapali kume kontrolu yapiyor ve
  `ValueError` firlatiyor. Dogrulandi. Literal alani, `__post_init__` kumesi ve
  `series_runner.migrate_malformed_approval_holds` icindeki `valid_codes` kumesi
  plana yazildi.
- **ACCEPTED** [FIX] kapi yanlis yerde -> `series_runner.py:768-802` okundu; sira
  gercekten sonuc normalizasyonu -> v2 hata dali -> qc_hold -> `mark_produced` ->
  onay modu -> `--no-publish` -> `_publish_part`. Kapi sonuc normalizasyonunun hemen
  ardina alindi.
- **ACCEPTED** [FIX] olculemeyen sure kapidan gecer -> `episode_coherence.py` okundu,
  `duration_in_band` None iken `degraded` False kaliyor. Dogrulandi. event-horizon
  icin `duration_in_band is True` sarti eklendi.
- **ACCEPTED** [FIX] `[14,26]` ust siniri dayanaksiz -> `series.json` coherence
  kayitlari okundu: 26=11,02 / 27=11,03 / 28=16,62 / 29=11,10 / 30=16,62 / 31=19,62.
  Alt sinir 14 dogrulandi, ust sinir olculmus azami 19,62 uzerine 2,4 saniye payla
  **22**'ye cekildi. Alti kaydin tamami plana tablo olarak yazildi.
- **ACCEPTED** [FIX] `bool(...)` bozuk degeri aciyor -> `block_degraded_publish` ve
  `title_card.year_required` artik yalnizca JSON bool kabul ediyor, aksi halde
  `ValueError`.

## Turlar arasi: Visionary'nin kendi olcumu (10 Eylul, 08:29 PDT)

Codex kotasi doldugu icin tur 2 beklerken, ROCK 2'nin temel varsayimi gercek veriyle
sinandi: yayinlanmis part 24 videosu (-24,8 LUFS) motorun kendi
`core/ffmpeg_tools.master_audio(target_i=-14, target_tp=-1.0)` fonksiyonundan gecirildi.

Sonuc: `RuntimeError: master teslim sozlesmesi 3 denemede tutulamadi:
true-peak -0.9 dBTP > -1.0 dBTP`.

Yani `master_lufs` alanini eklemek tek basina kanali duzeltmezdi; her bolumu
`AUDIO_MASTER` hold'una dusururdu. Ne rapor ne Codex tur 1 bunu yakalamisti.

Kok neden tavan supurmesiyle olculdu: teslim true-peak, limiter tavaninin daima
~0,15 dB ustunde; dongu ise tavani tam olculen tasma kadar (0,1 dB, ffmpeg'in rapor
cozunurlugu) geri cekiyor, yani hicbir ilerleme kaydetmiyor. Uc deneme
-1,0 / -1,1 / -1,2'de bitiyor; gectigi yer -1,3.

Onerilen duzeltme ayni gercek ses uzerinde yan yana kosularak kanitlandi: geri cekmeye
0,2 dB pay eklenince ikinci denemede geciyor (-14,1 LUFS, -1,3 dBTP).

Plana yeni **ROCK 1** olarak eklendi, rock'lar 0..5 diye yeniden numaralandi ve
tur 2 prompt'una "en sert bunu incele" talimati konuldu.

## Round 2
### Integrator findings (Codex, verbatim)

Several round-1 findings are addressed: the owner-authorized title work stays; the reason-code additions and earlier degraded gate reach the finite content-retry branch; missing duration fails closed; and `bible` is available at replenish’s validation site. `[14,22]` correctly separates all six recorded episodes: 26/27/29 fail at 11.02/11.03/11.10 seconds; healthy 28/30/31 pass at 16.62/16.62/19.62.

The remaining issues are:

- [FIX] Rock 1 changes Unnatural Lab’s retry behavior despite the explicit other-series behavioral-isolation constraint, and first-attempt equality does not protect episodes that currently succeed on attempts two or three -> Make the revised retry policy an Event Horizon-only opt-in with existing defaults preserved, and reconcile the contradictory “master_audio behavior unchanged” section.

- [FIX] The sweep establishes a three-attempt failure on part24, not a constant 0.15 dB offset, perpetual nonconvergence, failure of every episode, or Unnatural Lab part33’s identical cause -> Narrow the diagnosis to the evidence and preserve a reproducible old-fails/new-passes fixture; the reported sample already passes with the margin and three attempts, so justify or remove the fourth attempt.

- [FIX] The `target_tp - 3.0` cutoff rejects a feasible solution in the existing adversarial test that compensates for 3.1 dB overshoot, while one clip’s LUFS at a −6 dB ceiling cannot establish a universal limit -> Test quiet and heavily limited content against both delivered constraints, preserve legacy behavior, and make any opted-in cutoff raise with cleanup rather than `break`, which bypasses the loop’s failure branch.

- [FIX] Rock 1 cannot leave both existing true-peak test files unchanged and green because they assert three attempts and include the now-rejected 3.1 dB compensation case -> Retain those tests against the legacy default and add separate tests for the Event Horizon retry policy.

- [FIX] The one-decimal `ebur128` summary can report −1.0 for a true peak slightly above −1.0, so the proposed measurement can certify a contract violation -> Use higher-precision decoded-delivery verification or conservative acceptance headroom for the opt-in path; neither sample-peak `astats` nor a pre-encode limiter certifies the final AAC true peak. [FFmpeg filter documentation](https://ffmpeg.org/ffmpeg-filters.html#alimiter)

- [FIX] Rock 0 also activates `_budget_failure`, which treats unknown spend or completion cost as `BUDGET_EXHAUSTED` and immediately advances the queue, potentially skipping multiple parts on a shared accounting-read failure -> Distinguish unavailable accounting from proven exhaustion through an additive opt-in path, and test that an accounting failure preserves the current part and partial work.

- [FIX] Migration can change a malformed approval hold into `needs_human` without advancing `next_part`, after which the existing early-return branch again reports success indefinitely -> Specify and test atomic migration/pointer handling, including exhausted holds and preserved partial artifacts; the current Event Horizon records contain no such hold, but the claimed migration guarantee remains false.

- [FIX] Adding `title_card` only to produce’s required-layer vocabulary leaves `series/preflight.py:122` rejecting every newly opted-in Event Horizon plan -> Update both vocabularies and test the actual four-plan preflight path with `required_layers=["title_card"]`.

- [FIX] Required-overlay exception handling does not cover disabled configuration, missing card fields, or the utility’s separate empty-rows copy-through path, and Rock 5 still omits production from shared card validation -> Validate required cards before spending and enforce them in production, including absent/blank/disabled cases that must never reach publish.

- [FIX] Defaulting `year_required` to true preserves existing replenish rules but does not preserve behavior if newly added preflight or production checks reject legacy plans that previously passed -> Scope new delivery validation to explicit opt-in, preserve Flashpoints’ boolean `title_card: true` shorthand, and compare legacy prompts and acceptance behavior for Flashpoints, Footnotes, and Drowned History.

- [FIX] Event Horizon’s changed brief and title-card prompt invalidate its existing prompt golden in `tests/test_fixedframe.py`, an additional suite migration absent from the plan -> Update only Event Horizon’s expected prompt and retain byte-identical expectations for every unaffected series.

- [FIX] Rock 2’s direct utility test bypasses Event Horizon’s actual narration/music mixing, and increased speech-band RMS can come entirely from music while narration remains inaudible -> Exercise the production-to-publish boundary with recognizable speech, measure the delivered artifact, verify narration independently, and include a phone-speaker listening check.

- [FIX] Rock 3’s upper-third brightness difference can pass with unreadable or incorrect text and does not prove production actually uses the required overlay -> Inspect expected text in the final production artifact at phone display size and test that renderer failure prevents the publisher from being called.

- [FIX] The four titles satisfy the stated character, capitalization, emoji, and family-rotation constraints, but none matches the proposed six-pattern vocabulary exactly -> Reconcile the owner-approved exact titles with the prompt templates; this requires consistent wording, not the deferred regex framework.

- [FIX] “Should Not Be Egg-Shaped” presents an expected tidal deformation as physically anomalous, while “the Sky Will Be EMPTY” erases the Local Group that part33’s own premise preserves -> Keep the title initiative but use an accurate anomaly for WASP-12b and explicitly qualify the disappearing distant galaxies. [NASA’s WASP-12b explanation](https://science.nasa.gov/universe/exoplanets/wasp-12b-an-egg-shaped-planet/)

- [FIX] Rock 5 specifies exact equality only for `episode.title`, despite the claimed byte-equality proof for all title-card strings -> Assert both card fields against the exact table values and pin unchanged-plan comparisons to an explicit baseline commit.

No files modified; the suite and reported media experiment were not rerun.

VERDICT: NOT YET
### Visionary response (Claude)

Kod iddialarinin tamami dosyadan dogrulandi; hicbiri sozune inanilarak kabul edilmedi.

- **ACCEPTED** ROCK 1 unnatural-lab'i etkiliyor -> Hakli. Duzeltme artik OPT-IN:
  `master_audio(..., true_peak_margin_db=0.0)` varsayilani bugunku aritmetigin birebir
  aynisi; pay yalnizca `bible.master_true_peak_margin_db` tanimlayan seride devreye
  girer. "Ilk deneme esitligi yetmez" itirazi da boylece kapaniyor: opt-in olmayan
  seride ikinci ve ucuncu deneme de degismiyor.
- **ACCEPTED** teshis fazla genis, dorduncu deneme dayanaksiz -> Iddia daraltildi.
  "Her bolum patlar" ve "part 33'un sebebi ayni" cikarildi; part 33 icin yalniz
  "ayni hata imzasi" deniyor, sesi olculmedi. Deneme sayisi 3'te BIRAKILDI.
  Teshis de inceltildi: sorun sabit tasma degil, ffmpeg'in 0,1 dB rapor cozunurlugunun
  gercek 0,15 dB araligi EKSIK olcmesi. Mevcut adversarial testin 3,1 dB'lik sabit
  tasmayla yakinsamasi bu teshisle celismiyor, onu tamamliyor.
- **ACCEPTED** `target_tp - 3.0` kesme siniri -> `tests/test_master_true_peak_adversarial.py`
  okundu: 3,1 dB tasmayi telafi eden cozumu GECERLI sayiyor, sinir onu reddederdi.
  Sinir PLANDAN CIKARILDI.
- **ACCEPTED** mevcut true-peak testleri degismeden kalamaz -> Artik kalabiliyor:
  varsayilan pay 0,0 oldugu icin iki test de tek satir degismeden yesil kalir; yeni
  davranis ayri bir test dosyasinda.
- **DEFERRED** ebur128 0,1 dB cozunurlugu -1,04'u "-1,0" diye gecirebilir -> Gercek
  ama ayri bir is; pay bunu pratikte kapatiyor. Issues listesine alindi.
- **ACCEPTED + DEFERRED** ROCK 0 `_budget_failure` kapisini da aciyor ->
  `series_runner.py:708` dogrulandi, kapi gercekten v2 ile aciliyor ve muhasebe
  okunamadiginda `BUDGET_EXHAUSTED` deyip kuyrugu ilerletiyor. Gercek event-horizon
  verisiyle OLCULDU: asgari 300, kalan 900, kapi tetiklenmiyor. Olculen degerler
  ROCK 0 proof'una cakildi; latent duzeltme Issues'a.
- **ACCEPTED (test)** migration `needs_human` yapip `next_part` ilerletmeyebilir ->
  Senaryo teste eklendi ve event-horizon kayitlarinda boyle bir kayit OLMADIGI
  dogrulaniyor. Duzeltme Issues'a.
- **ACCEPTED** `preflight.py:122` ayri bir katman sozlugu tutuyor -> Dogrulandi,
  `{"hook_teaser", "music", "native_audio"}`. Yalniz produce'u guncellemek her yeni
  event-horizon planini reddederdi. IKI sozluk de guncelleniyor ve dort planin
  gercek preflight yolu test ediliyor.
- **ACCEPTED** zorunlu katman bos/eksik kunyeyi yakalamiyor -> Ucretli isten ONCE
  preflight dogrulamasi eklendi (bos/eksik/kapali kunye kredi harcanmadan reddedilir).
- **ACCEPTED** flashpoints'in `"title_card": true` kisayolu -> Korunuyor ve test edildi.
  Ayrica uc eski serinin bugun gecen ornek planlarinin degisiklikten sonra da gectigi
  test ediliyor.
- **ACCEPTED** `tests/golden/fixedframe_prompts.json` -> `test_fixedframe.py:35`
  okundu, `event-horizon` golden listesinde. YALNIZ onun beklenen prompt'u guncellenir.
- **PARTIALLY ACCEPTED** ROCK 2 proof'u anlatimi kanitlamiyor -> Hakli kismi kabul:
  olculen sey artik seviye degil ANLATIM/MUZIK ORANI (master oncesi ve sonrasi 1 dB'den
  fazla degismemeli). "Telefon hoparlorunde dinleme kontrolu" bir CI testi olamaz;
  REDDEDILDI. Yerine: Level 10 incelemesinde master oncesi/sonrasi gercek ses ornekleri
  Ihsan'a gonderilir, kulak karari onun.
- **ACCEPTED** kunye piksel testi okunabilirligi kanitlamiyor -> Test farksal hale
  getirildi (bos baslikla ayni render belirgin daha az mürekkep uretmeli) ve Level 10'da
  kare gozle incelenir.
- **ACCEPTED** dort baslik ilan edilen kaliplara uymuyor -> Kalip (6) tekil/cogul ozne
  ve duz eylemi kapsayacak sekilde yeniden yazildi; dort baslik da ona uyduruldu.
- **ACCEPTED** iki baslik fakta aykiri -> Ikisi de degistirildi.
  part 32: yumurta sekli gelgitin BEKLENEN sonucu (NASA zaten "egg-shaped" diyor),
  anomali degil; baslik yildizin gezegeni yutmasina cevrildi.
  part 33: "sky will be EMPTY" bolumun kendi onermesiyle (Yerel Grup kalir) celisiyordu;
  baslik ve kunye "distant galaxies" diyerek duzeltildi.
- **ACCEPTED** ROCK 5 yalniz `episode.title` icin birebir esitlik ariyordu -> Her iki
  kunye alani da birebir esitlikle test ediliyor; degismeyen alanlarin karsilastirmasi
  **9eec629** temel commit'ine sabitlendi.

## Round 3
### Integrator findings (Codex, verbatim)

Verified: margin `0.0` preserves the existing three-attempt arithmetic; runtime has no `master_audio` caller outside `produce.py`—only tests do. The two identified sets are the only layer-name vocabularies. All four titles/cards match their source plans, family rotation, patterns, and limits. The degraded gate reaches finite content retry and does not conflict with today’s 300/900 budget result. No protected channel files are listed for modification.

- [FIX] The DOKUNMA section still says `master_audio` behavior does not change, directly contradicting Rock 1’s opt-in behavioral change and leaving implementation instructions ambiguous -> Say that default behavior is unchanged while Event Horizon explicitly opts into the new pullback arithmetic.

- [FIX] Rock 1 and Rock 2 test `master_audio` directly, so every stated test can pass if `produce.py` forgets to forward `bible.master_true_peak_margin_db`, and their constructed mix bypasses the actual `master_lufs` branches that change voice normalization and music gain from 0.28 to 0.50 -> Add one production-path test proving the 0.2 argument is forwarded and measuring the final narration/music ratio, LUFS, and true peak after the real Event Horizon mixing path.

- [FIX] Full preflight is not called by `series_runner.py`, while `produce.py` currently skips `title_card_overlay` when card fields are absent, so a required but missing card can still consume credits and publish without text -> Call the shared required-title-card validator from production before the budget/paid path, or explicitly fail production whenever `title_card` is required but disabled, missing, or blank.

- [FIX] The title-card proof only detects changed upper-third pixels, which can pass for incorrect or unreadable marks without proving the exact queued text reached the final episode -> Add a production-path assertion for the exact title/subtitle arguments and include an actual phone-scale final-frame review in the Level 10 owner evidence.

VERDICT: NOT YET

### Visionary response (Claude)

Codex bu turda bes dogrulama maddesini olumlu kapatti (pay 0,0 esitligi, master_audio'nun
produce disinda cagricisi olmadigi, iki katman sozlugunun tek oldugu, dort basligin
kaynak planlarla tutarli oldugu, korumali kanal dosyalarina dokunulmadigi). Kalan dort
bulgunun ikisi somut kod iddiasiydi ve ikisi de kaynaktan dogrulandi.

- **ACCEPTED** DOKUNMA listesi celiskisi -> "master_audio davranisi degismez" satiri
  duzeltildi: VARSAYILAN davranis degismez, event-horizon acikca opt-in olur.
- **ACCEPTED (buyuk)** `master_lufs` uc anahtari birden ceviriyor -> Kaynaktan
  dogrulandi: `produce.py:604` amix_normalize, `:656` music_volume 0.28 -> **0.50**,
  `:659` limit_mix_peak. Yani ses masteri acilinca MUZIK de neredeyse iki katina
  cikiyor. Anlatim tabanli bir kanalda bu, duzeltmeye calistigimiz seyi gomebilirdi
  ve benim kanitim (zaten miksLENMIS yayinlanmis videoyu master'lamak) bu yolu hic
  test etmemisti. Plana tablo olarak yazildi ve ROCK 2'nin proof'u gercek karisim
  yolunu olcen bir URETIM YOLU testiyle degistirildi: pay'in iletildigi, uc dalin
  secildigi ve anlatimin muzige gore en az 6 dB onde kaldigi olculur.
- **ACCEPTED** preflight uretim yolunda degil -> `series_runner.py:680` dogrulandi:
  yalnizca `validate_required_platforms` iceri aliniyor; `preflight.inspect/run` bir
  CLI aracidir. "Ucretli isten once reddet" garantim YANLISTI. Koruma `produce.py`nin
  zaten kosan `required_layers` blogona (satir 1345-1364) tasindi; preflight ayni
  fonksiyonu elle kontrol icin ayna olarak cagirir.
- **ACCEPTED** kunye piksel testi metni kanitlamiyor -> Test farksal hale getirildi
  (bos baslikla daha az murekkep) ve uzerine `title_card_overlay`'e gecilen `title` /
  `subtitle` argumanlarinin plandaki tam metinle birebir esitligini cakan bir uretim
  yolu testi eklendi. Telefon olceginde final kare Ihsan'a gonderilecek.

