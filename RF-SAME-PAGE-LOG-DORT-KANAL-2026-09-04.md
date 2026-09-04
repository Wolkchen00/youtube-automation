# Same Page Log , dort kanal yayin hatti (2026-09-04)

Plan dosyasi: `RF-PLAN-DORT-KANAL-2026-09-04.md`
Core Focus: Dort kanal da her gun otomatik yayin yapsin; yayin durursa sistem YESIL
gostermesin ve durus 24 saat icinde gorunur olsun.

## Round 1

### Integrator findings (Codex, verbatim)

- [FIX] The claimed root cause is wrong: Event Horizon still has unused numeric `topic_pool` IDs 14 and 24, while `extra_topics` is only the Notion extension -> Treat the failure as Gemini contract noncompliance and assign valid `seed_id`/family mechanically before generation.
- [FIX] Flashpoints likewise has unused numeric IDs 12 and 16, so `extra_topics: []` does not mean its usable topic pool is empty -> Count both unused `topic_pool` entries and valid unused `extra_topics`.
- [FIX] The citation to `calibrate.py:646-648` is inaccurate because those lines only resolve schema option names; approved cards are queried at lines 762-764 -> Correct the evidence citation even though the Event Horizon-only slug gate at line 703 is real.
- [FIX] ROCK 2 would not catch the live Galactic failure because `SeriesMeta.advance()` automatically changed Event Horizon to `status=completed`, so the proposed `status != active` success branch still returns green -> Distinguish intentional completion from exhausted `auto_replenish.enabled` series using an explicit terminal reason/outcome.
- [FIX] Series `status` alone is insufficient because current-part `awaiting_approval` and `needs_human` return `True`, `budget_exhausted` may advance into `completed`, and `qc_retry` follows another path -> Introduce typed outcomes such as `published`, `already_published_today`, `intentionally_paused`, `blocked_human`, and `exhausted`.
- [FIX] ROCK 2 omits its real blast radius: 12 workflows invoke the CLI, only five write `last_run.json`, and existing tests deliberately expect successful no-ops for hold states -> Define and test a per-caller migration matrix before changing the shared return contract.
- [FIX] The plan promises an explicit no-work value in `last_run.json`, but `series_runner` never writes that file and the five workflow writers reduce everything to the step's raw success/failure -> Add a machine-readable runner result and make every active workflow persist it without overwriting its semantic outcome.
- [FIX] The immediate Event Horizon green lie has a materially simpler cause: its failing `replenish | tee` step lacks pipefail, so exit 1 is masked before `run_next()` returns the completed-series no-op -> Add explicit Bash/pipefail to active replenish steps before altering the fleet-wide runner contract.
- [FIX] ROCK 2's proof can pass without exercising the new Turkish-named test because its `-k "runner or exhaust or replenish or hold"` filter need not match `test_tukenmis_seri_yesil_degil.py` -> Invoke that file explicitly and assert CLI exit code, Telegram/outbox behavior, and persisted outcome.
- [KILL] ROCK 3 duplicates the existing `replenish` failure alarm and durable notifier outbox, already covered by `test_alert_delivery_coverage.py` -> Extend that path to alert on the direct empty-pool return and add pipefail instead of building a second alarm CLI.
- [FIX] ROCK 3 resurrects a known-bad runway formula because `replenish.py:1627-1639` explicitly documents that `total_parts-next_part+1` can claim runway where plan files are missing -> Measure contiguous plan files starting at `next_part`, reusing the existing replenish calculation.
- [FIX] ROCK 3's expected Unnatural Lab result contradicts its own formula because `32-28+1` is five, not four -> Define whether the blocked current episode counts and make implementation, message, and test agree.
- [FIX] ROCK 3's proof can pass while production remains unwatched because a unit test and manual CLI run do not prove scheduling, Telegram delivery, outbox persistence, or execution within 24 hours -> Prove the installed workflow invocation and a failing delivery/outbox integration path.
- [FIX] No repo mechanism currently enforces the Core Focus's 24-hour publication SLA: daily analytics fetches actual YouTube uploads but performs no freshness check, and the disabled cleanup monitor is unrelated -> Add an independent scheduled freshness gate over the four YouTube channels that alerts and fails when the latest real upload exceeds 24 hours or a channel cannot be measured.
- [FIX] ROCK 4's synthetic proof can pass with the bug intact because the existing synthetic-sine test already calls `master_audio`, measures true peak, and passes while the real Part 28 reports +0.1 dBTP -> Require a deterministic fixture that fails on the current implementation and reproduces the codec/downsampling overshoot before accepting a fix.
- [FIX] ROCK 4's three-other-series blast premise is overstated in this checkout because only `unnatural-lab/bible.json` opts into `master_lufs` and an existing test enforces that fact -> Preserve legacy byte-identity tests, then regression-test both a previously passing Unnatural input and the newly failing reproduction.
- [FIX] Lowering ROCK 4's limiter can solve true peak while pushing integrated loudness outside the ±1 LUFS gate -> Require both LUFS and decoded AAC true-peak assertions across representative passing and overshoot inputs.
- [FIX] ROCK 1's proof can pass before the workflow is fixed whenever pytest is already installed locally, so it does not prove a clean GitHub runner can reach production -> Test dependency installation in an isolated environment and statically assert that the workflow installs pytest before invoking it.
- [FIX] Fear Slide can still report success with no YouTube publication because `yayinla.py` returns zero when any one platform succeeds and records the day regardless of which platform succeeded -> Make YouTube a required platform and fail the workflow unless its upload is positively confirmed.
- [FIX] After all four rocks, Galactic still has the same nondeterministic replenishment failure and Shadowed History has only one queued episode plus two unused seeds, so four channels are not guaranteed to publish daily -> Add a publication-restoration rock covering deterministic replenishment and a sustainable approved-topic supply, or narrow the Core Focus explicitly.

VERDICT: NOT YET

### Visionary response (Claude)

- **ACCEPTED (en degerli bulgu)**: "claimed root cause is wrong ... unused topic_pool IDs 14 and 24".
  Bagimsiz olctum, DOGRU: `_topic_pool` `id` anahtarini okuyor, kullanim `plans/partNN.json`
  `seed_id`'sinden geliyor; event-horizon kullanilmayan {14,24}, flashpoints {12,16}.
  r1'in kok nedeni ("havuz bos") YANLISTI. -> Plan r2'de bolum 1 "r1'IN HATASI" olarak
  acikca yazildi ve kok neden bolum 2'de degistirildi.
  DUZELTME UZERINE EK: Codex "Gemini contract noncompliance" diyor; bu da eksik.
  Paralel dogrulama filosu bir kademe daha derine indi: kalan iki tohumun family'si
  yasak family ile AYNI, yani aday listesi BOS sunuluyor. Gemini uyumsuz degil,
  gorev COZULEMEZ. -> ROCK 1 (veri) + ROCK 2 (kural cikisi) buna gore yazildi.
- **ACCEPTED**: flashpoints ayni durumda. -> ROCK 1 iki seriyi birden kapsiyor;
  flashpoints'in bu geceki slotu zaman kritigi olarak plana yazildi.
- **ACCEPTED**: `calibrate.py:646-648` atifi yanlis. -> Notion bolumu kok nedenden
  cikarildi (zaten r1 hatasiydi), NON-GOALS'a tasindi.
- **ACCEPTED (kritik)**: `SeriesMeta.advance()` event-horizon'u `completed` yapti,
  bu yuzden r1'in `status != active` dali yine yesil donerdi. -> r2 ROCK 3a
  `strict_empty` bayragina cevrildi: ayrim `status` degil, "acikca istenen slug icin
  uretilecek bolum var mi" sorusu.
- **ACCEPTED**: `awaiting_approval` / `needs_human` / `budget_exhausted` / `qc_retry`
  durumlari `status` ile ayrilamaz. -> ROCK 3a kisiti: bu durumlar ESKISI GIBI
  davranacak, degisiklik opt-in `strict_empty` ile sinirli.
- **ACCEPTED**: patlama yaricapi (12 workflow, 5'i last_run.json yazar, mevcut testler
  hold'da basarili no-op bekler). -> ROCK 3a varsayilani DEGISTIRMIYOR; opt-in bayrak.
- **ACCEPTED**: `series_runner` `last_run.json` yazmiyor. -> ROCK 3c isaret dosyasi
  (`logs/published_part.txt`) yaklasimiyla yeniden yazildi.
- **ACCEPTED (bagimsiz olarak dogrulama filosu da buldu)**: pipefail eksik. ->
  ROCK 3b oldu, bes workflow adiyla listelendi. Codex'in "before altering the runner
  contract" onceligi kabul: ROCK 3b, 3a'dan bagimsiz ve tek basina degerli.
- **ACCEPTED**: `-k` filtresi yeni testi kacirabilir. -> Tum PROOF komutlari dosya
  adiyla acik cagriya cevrildi.
- **ACCEPTED (KILL)**: ROCK 3 (eski "pist alarmi") mevcut alarm yolunu ve
  `test_alert_delivery_coverage.py` kapsamini tekrarliyor. -> Eski ROCK 3 KALDIRILDI.
  Yerine ROCK 2 (family kilidi cikisi) mevcut uyari/alarm yolunu KULLANIYOR,
  yeni CLI kurmuyor.
- **ACCEPTED**: `total_parts-next_part+1` bilinen bozuk formul; ayrica 32-28+1=5,
  benim yazdigim 4 yanlisti. -> Formul plandan tamamen cikti (rock kaldirildi).
- **ACCEPTED**: 24 saatlik SLA'yi zorlayan bir mekanizma repoda yok. -> Bu GERCEK bir
  bosluk ama bu cevrimin dort rock'ina sigmiyor ve ayri repodaki nobetciyle
  (`Akilli_Watchdog`) kesisiyor. ISSUES'a yazildi, Ihsan'a ayri cevrim olarak sunulacak.
  Core Focus daraltilmadi: bu cevrim "yayin geri gelsin + yesil yalan bitsin"i teslim eder.
- **ACCEPTED (kritik)**: ROCK 4'un ispati mevcut sinus testi gibi gecerken hatayi
  kacirabilir. -> ROCK 4 PROOF'u "fikstur duzeltmeden ONCE kirmizi olmali" kuralina
  baglandi. Ayni kural bolum 8'de tum rock'lara genellestirildi.
- **ACCEPTED**: `master_lufs` yalniz unnatural-lab bible'inda. -> ROCK 4 kisitlarina
  yazildi; bayt-esdegerlik testlerinin yesil kalmasi sart kosuldu.
- **ACCEPTED**: limiter'i dusurmek LUFS kapisini bozabilir. -> ROCK 4 done-looks-like
  her iki yarimi da (TP <= -1.0 VE |I+14| <= 1.0) dogrulamak zorunda.
- **ACCEPTED**: ROCK 1'in ispati yerelde pytest kuruluysa bos gecer. -> PROOF'a
  "workflow'un pytest kurdugunu STATIK olarak dogrula" maddesi eklendi.
- **DEFERRED**: `yayinla.py` tek platform basarisinda 0 donuyor, YouTube garanti degil.
  Gercek ve onemli, ama Fear Slide'in bugunku olumu test kapisinda; bu ayri bir kusur.
  -> ISSUES'a.
- **ACCEPTED (kismen)**: "dort rock sonrasi dort kanal garanti degil". Dogru.
  ROCK 1 iki kanali BUGUN geri getirir, ROCK 4 Sentinal'i, ROCK 1(pytest) AImagine'i.
  Surdurulebilir konu tedariki (Notion koprusu / havuz besleme) bu cevrimin disinda
  ve Ihsan'in icerik karari. -> NON-GOALS'da acikca yazildi, ISSUES'a tasindi.
- **REJECTED**: yok. Tur-1'de reddedilen bulgu yoktur.

## Round 2
### Integrator findings (Codex, verbatim)

Round‑1 audit:

- Fully addressed: wrong empty-pool diagnosis, Flashpoints’ equivalent state, bad `calibrate.py` citation, removal of the duplicate runway alarm and broken runway formula, explicit ROCK 3 test invocation, pre-fix-red audio fixture requirement, dual LUFS/TP assertion, pipefail scope, and acknowledgment that only Unnatural Lab opts into mastering.
- Partially addressed: completed-series handling, shared-runner blast radius, and truthful `last_run.json`; the new designs still have gaps below.
- I disagree with three dispositions: the 24-hour SLA, YouTube-required success, and sustainable topic supply cannot be deferred while the Core Focus remains unchanged.
- I also disagree that the pytest finding was addressed: r2 diagnoses Fear Slide’s missing pytest but contains no rock that installs it. The response’s reference to “ROCK 1(pytest)” no longer matches the plan.

New/open findings:

- [FIX] ROCK 1’s minimum usable entry is `{"id": <JSON integer>, "topic": <non-empty string>, "family": <canonical family>}`, with an ID unused both in the pool and plan history -> Add an explicit pool-schema validator because `_topic_pool` silently ignores non-integer IDs and silently overwrites duplicate IDs.
- [FIX] Pool-entry family validity is not checked by `validate_replenish_config`; a noncanonical family survives `_unused_topics` but makes every generated plan impossible because lines 1017-1019 reject it or lines 1063-1065 reject the seed/family mismatch -> Validate every entry’s ID, topic, canonical family, and uniqueness before calling Gemini.
- [FIX] Topic text has no pool-entry-level non-empty, uniqueness, language, source, or factuality gate -> Require non-empty distinct English topics and human-verifiable sourcing in the data review, while recognizing that downstream validation checks the generated plan rather than the source fact itself.
- [FIX] A hand-written Flashpoints topic must support the downstream title-card time-anchor gate at lines 1264-1289, while both series must still produce unique titles, valid narration, shots, durations, and generic `validate_plan` output -> Include a concrete year/era in each Flashpoints fact and test a generated-plan-shaped fixture for every new seed.
- [FIX] Adding entries will break the existing full suite because `tests/test_doctrine_gate.py:448-460` hard-codes both pools at exactly 27 entries -> Update that regression expectation or replace the brittle count with schema and minimum-size assertions in ROCK 1.
- [FIX] ROCK 1’s proposed feasibility test has inverted scope: Event Horizon is `completed` and would be skipped by “every ACTIVE series,” while active Unnatural Lab has no `topic_pool` and would fail unless silently excluded -> Explicitly test Event Horizon and Flashpoints, or select all `auto_replenish.enabled` series with a configured integer pool.
- [FIX] ROCK 1’s proof only requires one alternative-family seed although the data contract requires at least three mutually distinct families and a feasible five-item batch -> Assert unique IDs, canonical families, the three-new-family rule, and existence of a complete valid ordering for the effective batch.
- [FIX] ROCK 2 is applied at the wrong end: changing lines 900-910 only exposes the seeds, while lines 799-804 still prohibit the family, lines 824-828 still restrict the first seed pool, and lines 1020-1023 unconditionally reject the result -> Compute one shared “relax first family” decision and apply it consistently to all prompt rules and the validator’s first item only.
- [FIX] ROCK 2’s proof can pass while the real defect survives if it checks only prompt contents or mocks validation -> Assert that `_validate_batch` accepts the first unavoidable repeat, still rejects a second consecutive repeat inside the batch, and that unrelaxed alternatives remain preferred.
- [FIX] ROCK 2 promises a persistent counter/alarm but specifies neither storage nor proof of delivery -> Define the persisted field/outbox event and assert it, rather than proving only a warning log.
- [FIX] `main()` currently distinguishes `--series` only through a truthy following token; a missing value falls through to `run_all` and can produce an unrelated paid episode -> Replace the ad-hoc parser with `argparse` and reject missing/empty slug values before deriving `strict_empty`.
- [FIX] ROCK 3a’s rules are internally ambiguous because `completed` satisfies both “status != active succeeds” and “explicit slug with nothing producible fails” -> Define precedence explicitly: deliberate `paused`/`draft` succeeds, while explicitly scheduled exhausted auto-replenishing series fails.
- [FIX] Passing `strict_empty=True` during `--dry-run` could emit a real Telegram alarm even though `main()` suppresses the nonzero exit -> Suppress external alerts in dry-run or pass strict mode only for live execution.
- [FIX] ROCK 3c’s Python test can pass while the YAML shell writer remains broken because `last_run.json` is produced by workflow code, not `series_runner` -> Move result-file construction into a tested repository script and have all five workflows call that script.
- [FIX] A publication marker still does not prove YouTube publication: Event Horizon and Flashpoints have empty `required_platforms`, and Fear Slide succeeds when any platform succeeds -> Require confirmed YouTube success before writing `published_part.txt` or a success outcome.
- [FIX] ROCK 4a identifies only the first two-input mix at `mix_voiceover`, but music is added afterward by a second uncapped `normalize=0` amix at `ffmpeg_tools.py:1088` -> Cap both lossy mix stages or perform the final three-layer sum and limiting once before AAC.
- [FIX] Capping `mix_voiceover` is isolated to Unnatural Lab only if the limiter is explicitly gated on `amix_normalize=False`; an unconditional limiter changes every narrated series -> Make the limiter opt-in and pass that opt-in only when `master_lufs` is configured.
- [FIX] Correctly capping the later `mix_background_music` path would otherwise affect every narrated music series because that helper always uses `normalize=0` when preserving program audio -> Add a separate opt-in parameter instead of changing its default output.
- [FIX] ROCK 4b does not say whether retries re-render from the original premaster; feeding AAC output back into the next pass causes cumulative lossy encoding and measurement drift -> Re-render every attempt from the unchanged premaster with an adjusted limiter target and fail closed after three attempts.
- [FIX] The claimed ep01-ep27 byte-equivalence coverage is overstated: existing byte-identity tests protect non-opted-in legacy series, not an Unnatural Lab episode corpus -> Keep those tests and add an explicit previously-passing Unnatural fixture.
- [KILL] Deferring Fear Slide’s pytest installation leaves AImagine’s only automatic line guaranteed to fail before production -> Restore the clean-runner pytest-install rock and place it before the next 13:20 UTC cron.
- [FIX] Deferring the actual YouTube success requirement preserves the exact “green without channel publication” failure prohibited by the Core Focus -> Include required-YouTube semantics for Fear Slide and the two series pipelines in this cycle.
- [FIX] Deferring the 24-hour freshness gate means neither `last_run.json` nor `Akilli_Watchdog` currently observes the right AImagine file, so the SLA remains unimplemented -> Extend the existing daily YouTube analytics job with a four-channel freshness failure/alarm or include the external watchdog configuration as a required coordinated deliverable.
- [FIX] Three new topics produce roughly one five-episode batch and ROCK 2 only relaxes family rotation; neither supplies future topics after exhaustion -> Add an ongoing approved-topic source or explicitly change the Core Focus from continuous daily publication to a five-day recovery window.
- [CLARIFY] The plan says Flashpoints must be saved tonight but also forbids commit/push, so none of the data changes can reach the live cron -> State who deploys the changes and the deadline before 20:30 UTC.

Ordering is conditionally correct for Flashpoints: ROCK 1 and the validator-side ROCK 2 must precede ROCK 3b, because enabling pipefail first would make replenishment red and skip tonight’s still-valid Part 25. If Unnatural Lab’s 18:30 UTC slot has not fired, ROCK 4 should move to the front to prevent another paid failure; otherwise keep ROCK 1 first for the 20:30 deadline. The missing Fear Slide dependency fix must land before its next 13:20 run.

VERDICT: NOT YET
### Visionary response (Claude)
- ACCEPTED (KILL, en onemli): r2'de pytest rock'ini dusurmusum. Kendi hatam.
  -> r3'te ROCK B olarak geri kondu.
- ACCEPTED: test_doctrine_gate.py:448-460 iki havuzu 27'ye sabitliyor (dogruladim).
  -> ROCK C bu beklentiyi guncelleyecek.
- ACCEPTED: --series ad-hoc ayristirici; bos deger run_all'a dusup PARASI ODENMIS
  alakasiz bolum uretebiliyor (series_runner.py:963 dogrulandi). -> ROCK E1, argparse.
- ACCEPTED: ROCK D yanlis uctan uygulaniyordu; site listesi genisletildi.
- ACCEPTED: ikinci tavansiz amix (ffmpeg_tools.py:1088) ve opt-in gating sarti.
- ACCEPTED: her deneme premaster'dan yeniden uretilecek (kumulatif AAC kaybi).
- ACCEPTED: fizibilite testi kapsami ters; auto_replenish.enabled + integer havuz.
- ACCEPTED (CLARIFY): dagitim sahipligi. Ihsan push'u onayladi; Visionary diff'i
  okuyup proof'u kosar, sonra push eder.
- REJECTED (gerekce ile): 24 saatlik tazelik kapisi, tam YouTube-zorunlu semantigi,
  surdurulebilir konu tedariki. Gerekce: ayri repoya (Akilli_Watchdog) uzaniyor veya
  Ihsan'in icerik karari; dort kanali BUGUN yayina dondurme isini geciktirir.
  ROCK E4 YouTube noktasinin DAR halini aliyor. Ucu de ISSUES'a.

## Round 3
### Integrator findings (Codex, verbatim)

r3 is materially improved, but not buildable as written. ROCK A/B, argparse isolation, deployment ownership, and the three stated deferrals are addressed; I do not reopen those deferrals.

Verified details: the pool validator belongs in `validate_replenish_config()` at `replenish.py:125`, reached at `1610-1613`, before Gemini at `1670`. Malformed entries must make `replenish()` return `False`, produce exit 1 for an explicit live invocation, perform no mutation, and make zero `_gen_json` calls. Each entry needs a non-boolean integer ID unique within the pool, a nonempty topic, and a canonical family; a newly added ID must also be absent from history or `_unused_topics()` will discard it. No positivity rule exists. Flashpoints’ generated output still faces the title-card date gate.

ROCK A’s proposed gating affects no other live series: only `unnatural-lab/bible.json` defines `master_lufs`. This remains true only if the new `mix_background_music` option defaults off and is passed from `produce.py` solely when `master_lufs is not None`.

At `1020-1023`, first-item-only relaxation is implementable safely: exempt only `i == 0` from the history comparison, then update `previous_family` normally so every later batch adjacency remains enforced.

The five series workflows are `event-horizon.yml`, `flashpoints.yml`, `unnatural-lab.yml`, `from-scratch.yml`, and `next-stop.yml`; `fear-slide.yml` is the sixth current writer.

- [FIX] BLOCKING: ROCK C’s proof can pass when schema validation is tested directly or wired only at `_validate_batch:959`, after credits were already spent -> Test through `replenish()` with malformed configuration, mock `_gen_json`, and assert `False`, zero Gemini calls, and no state mutation.

- [FIX] BLOCKING: ROCK D misses the contradictory fifth constraint at `replenish.py:793-797`, which still tells Gemini that consecutive episodes must never share a family even when the first repetition is unavoidable -> Gate that sentence with the shared relaxation decision and add a proof asserting the complete generated prompt permits only the first repetition.

- [FIX] ROCK D’s four listed sites contain the only executable adjacency rejection, but `1588-1591` would still falsely label the family “forbidden” after relaxation -> Condition that terminal diagnostic on the same shared decision.

- [FIX] ROCK E2’s precedence is incomplete: real/code-supported states `planned`, `produced`, `published`, `rejected`, and `skipped`, plus finite non-auto `completed`, are not classified -> Explicitly preserve `planned`/`produced` recovery and finite completion, while failing closed if a terminal `published`/`rejected`/`skipped` part is unexpectedly at `next_part`.

- [FIX] BLOCKING: ROCK E4 updates five writers but omits active channel workflow `fear-slide.yml`, which can still exit successfully after Instagram-only publication and write a green `last_run.json` -> Make all six workflows call the result writer, including Fear Slide using `yayin.jsonl.results.youtube` as evidence.

- [FIX] BLOCKING: ROCK E4’s proof can pass using stale historical YouTube evidence or without proving each workflow invokes the script -> Bind evidence to the current run and add a static six-workflow wiring test plus a stale-evidence negative test.

- [FIX] ROCK B’s factual count is wrong because 18 workflows, not 17, currently install `requirements.txt` -> Correct the count; the decision to install pytest only in `fear-slide.yml` remains sound.

- [FIX] ROCK B has no remaining publication slot today while Flashpoints does, so placing it between A and C spends deadline time without helping tonight -> Execute A first as approved, then C and D’s validator side before E3; move B after that critical path.

VERDICT: NOT YET
### Visionary response (Claude)
- ACCEPTED: dort BLOCKING bulgunun DORDU de. Ayrica Codex'in verdigi kesin
  uygulama adresleri plana islendi (validate_replenish_config replenish.py:125,
  i==0 muafiyeti, 793-797 prompt cumlesi, 1588-1591 tani, fear-slide altinci yazar).
- ACCEPTED: ROCK B 18 workflow (17 degil) ve kritik yolun sonuna alindi.
- REJECTED: yok.

## Round 4
### Integrator findings (Codex, verbatim)

Yes. r4 is buildable. All four round-3 blockers are substantively cleared, and no plan-level blocker remains.

The remaining items belong in the build-review contract:

- [FIX] NON-BLOCKING: E2 leaves `budget_exhausted` under “old behavior” even though it is terminal and should never remain at `next_part` -> Treat `budget_exhausted` at the current pointer as inconsistent state and fail closed before any paid call.

- [FIX] NON-BLOCKING: ROCK D’s shared decision may be evaluated repeatedly during six Gemini attempts, risking duplicate alerts -> Keep the decision helper pure and emit/persist the relaxation event once per replenish run.

- [FIX] NON-BLOCKING: ROCK B says no other `fear-slide.yml` line may change while E4 necessarily changes that workflow’s result-writing step -> Qualify this as “no other line within ROCK B.”

- [FIX] NON-BLOCKING: The document header and revision field still say r3 although the body contains r4 -> Update both labels to r4.

VERDICT: SAME PAGE
### Visionary response (Claude)
- VERDICT: SAME PAGE alindi (tur 4/5). Dort NON-BLOCKING madde build sozlesmesine
  tasindi: budget_exhausted fail-closed, gevseme olayinin kosu basina TEK kez
  yayinlanmasi, ROCK B kisitinin kosullandirilmasi, r4 etiketi.
- Etiket ve ROCK B kisiti plana hemen islendi.
