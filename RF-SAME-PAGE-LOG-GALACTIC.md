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

