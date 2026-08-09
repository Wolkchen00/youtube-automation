# RF-SAME-PAGE-LOG-SES , AImagine ses + görünür işçilik

Plan dosyası: `RF-PLAN-SES.md` · Codex: `gpt-5.6-sol`, reasoning effort `high`
Thread: `019fe790-aa59-7070-894c-56137127c34a`

## Tur 1

### Integrator bulguları (Codex, aynen)

```
- [FIX] `from-scratch` uses the Omni branch, which never reads `bible.native_audio`; cited `produce.py:951/979` and `kie_api.py:396` belong to the non-Omni branch -> Use an Omni API option that explicitly requests native audio or first prove the current Omni model guarantees it.
- [FIX] ROCK 1’s audio proof deliberately passes a 440 Hz tone plus a silent clip, so it certifies a non-construction soundtrack with a large silent gap -> Require per-shot audio coverage and semantic no-music/construction-sound validation.
- [FIX] Per-clip `loudnorm` amplifies any nonzero hiss before the `-50 dB` aggregate gate, making weak noise look healthy -> Measure every source clip before normalization and reject silence, sparse transients, and noise-only audio.
- [FIX] The proposed audio gate runs inside `_post_process` before the hook and later transforms, despite claiming to inspect the final file -> Run the required-layer gate on the actual returned upload file after every transformation.
- [FIX] A final audio rejection leaves all shot files cached, so every retry skips generation and deterministically fails again -> Reject or quarantine audio-bad clips immediately after download so the next run can regenerate them.
- [FIX] `series/preflight.py:78` has its own `required_layers` whitelist and will reject `native_audio`, but R1-g changes only `produce.py` -> Add the opt-in layer to both whitelists and their tests.
- [KILL] R2-c intentionally records self-building only under `issues` and still permits publication, which directly violates the Core Focus -> Cut the observation-only grace period and make missing visible builder-caused change a fail-closed QC result now.
- [FIX] `require_all_shots` remains false, allowing a rejected construction phase to disappear and the structure to jump between surviving shots -> Require all six causal build phases or fail the episode.
- [FIX] Linter rule (f) can pass “the builder carries a hammer while the walls rise by themselves” because one builder verb and one noun can coexist with self-assembly prose -> Reject autonomous state-change clauses and require the builder to be the grammatical cause of each structural change.
- [FIX] Rule (f) requires builder action in both the fixed prefix and generated body while brief item (9) forbids repeating the prefix’s builder sentences -> Put the causal action in one structured surface and generate the final prompt from that single source.
- [FIX] Proposed shot 6 names neither a real tool nor its sound, while `trim` can satisfy the material-noun escape hatch -> Name the tool and audible action explicitly and lint tool, action, and sound separately.
- [FIX] R2-a replaces “exactly one” with semantically equivalent “single” and “alone,” so Gemini can still set `forbidden_elements` while rule (g) passes -> Remove exclusion semantics from the QC prompt or add an explicit opt-in QC field whose decision logic is controlled in code.
- [FIX] `_PENDING_PARTS` still includes part06, whose protected body lacks the new builder-action form, so the promised zero-violation lint and bit-identical part06 cannot both hold -> Derive lint scope from unpublished parts and scan only part07–10.
- [FIX] Updating `KONSEPT.md` changes the doctrine hash, while `rf_transition_check.py` requires part06’s embedded hash to match and the plan forbids changing part06 -> Grandfather published part06 and enforce the new doctrine hash only on regenerated part07–10.
- [FIX] `auto_replenish.batch` is 5, so lowering `total_parts` to 6 generates part07–11 rather than the promised part07–10 -> Use an explicit four-plan regeneration target or temporarily set and restore `batch: 4`.
- [FIX] Deleting plans and lowering `total_parts` before a network-dependent Gemini call creates a crash state where `next_part: 7 > total_parts: 6` silently disables production -> Generate and validate replacements in staging, then atomically swap plans and metadata.
- [FIX] `rf_transition_check.py` hard-codes `next_part == 6` although live state and the plan require 7, and it does not compare current `next_part` with the snapshot -> Validate `next_part` against the snapshot value and update the stale regression fixture.
- [FIX] The transition snapshot hashes only `series.json.parts` metadata and `published.json`, not `plans/part01..part06.json`, so its proof passes after protected plan files are modified -> Snapshot and verify raw hashes for every protected plan file.
- [FIX] The documented proof commands use invalid CLI shapes because both prompt-lint and transition-check require a positional series directory, while preflight requires a real plan path -> Use `rf_prompt_lint.py aimagine/from-scratch`, `rf_transition_check.py aimagine/from-scratch --verify`, and full `--plan` paths.
- [FIX] Existing tests not mentioned by the plan will fail: `test_fixedframe.py` expects required music and a music call, `test_rf_transition_check.py` expects `next_part: 6`, and prompt-lint tests include part06 -> Update these existing assertions alongside the new tests.
- [FIX] The budget analysis divides an asserted 1880 by observed 126-credit clips, but the workflow cap is 1900 and `HardCreditCap` authorizes 10-second Omni calls at 200 credits -> Recalculate first-run and resumed-run call capacity from the actual authorization algorithm.
- [FIX] Synthetic ffmpeg tests do not validate Omni audio behavior or visible construction before the next live auto-publish spends shared credits -> Run a paid isolated staging canary and manually inspect both soundtrack and builder causality before enabling the production configuration.
VERDICT: NOT YET```

### Visionary yanıtı (Claude) , 22 bulgunun her biri

Doğrulama yöntemi: her kod alıntısı elle okundu; ses iddiası canlı Kie URL'inden klip
indirilip ffprobe + Gemini ses denetimiyle ÖLÇÜLDÜ.

- **KABUL F-1** (Omni dalı `native_audio` okumaz) → Kod alıntım yanlıştı, `sound=` ucuz
  görsel motor dalı. AMA ölçtüm: Omni klibi `aac 48kHz stereo, mean -29.7 dB`, Gemini
  `has_music:false, construction_sounds:["thud","whirring"]`. Omni sesi bayraksız üretiyor.
  Plan §1.1'e ölçüm eklendi, yanlış alıntı KN-1'de düzeltildi, payload'a alan EKLENMİYOR.
- **KABUL F-2** (ton+sessizlik testi sahte kanıt) → Seviye kapısı tek başına yetmez;
  `critic.qc_audio` (Gemini ses denetimi) eklendi: `has_music`/`speech`/`construction_sounds`.
- **KABUL F-3** (loudnorm hışırtıyı yükseltir) → Aynı çözüm; anlamsal kapı seviye kapısının
  üstüne kondu.
- **KABUL F-4** (kapı final dosyada koşmalı) → R1-j: kapı `_post_process` içinde değil,
  hook teaser dahil TÜM dönüşümlerden sonra, döndürülen dosyada koşar.
- **KABUL F-5** (önbellekli klipler sonsuz aynı hata) → Otomatik silme YOK (6 klip ≈ 1200
  kredi, aynı sonuç beklenir); yerine Telegram uyarısı + "ELLE BAK". ISSUES I-I.
- **KABUL F-6** (`preflight.py:78` kendi beyaz listesi) → Doğrulandı. R1-i eklendi.
- **RED F-7** [KILL, kendi kendine inşa hemen fail-closed olsun] → Üç gerekçe:
  (1) `_QC_SYSTEM` `artifact_score`'u zaten "impossible physics" ile tanımlıyor, yoktan
  beliren nesne kısmen SKORLANIYOR (ep07'nin 7-9 skorları); (2) kredi tavanı bu kadar
  darken yeni sert red sınıfı "sıfır video" gününü garantiler , bir kusurlu video sıfır
  videodan iyidir; (3) satır `issues`'a yazıyor, terfi kararı VERİYLE alınacak (I-G tetiği).
- **RED F-8** (`require_all_shots` geri açılsın) → İhsan'ın 2026-08-08 açık kararını geri
  alır ve ep06'yı , tek yayınlanan bölümü , öldürürdü.
- **KABUL F-9** (kural (f) zayıf) → `AUTONOMOUS_CLAUSES` blokajı eklendi. Genel edilgen
  dedektörü YAZILMIYOR (meşru "the viewpoint is released" yanlış pozitif olurdu); liste
  ölçülmüş ihlallerden oluşuyor.
- **KABUL F-10** (kural (f) ile brief (9) çelişiyor) → brief (9) netleştirildi: önek
  kelime kelime tekrarlanmaz, ama ustanın özne olması ZORUNLU. Çelişkisizlik testle
  kanıtlanacak (PROOF 3).
- **KABUL F-11** (çekim 6'da alet/ses yok, "trim" kaçamak) → Çekim 6 yeniden yazıldı
  ("fastens the last trim with a whining screwdriver"); kural (f) MALZEME değil ALET adı
  istiyor.
- **KISMEN KABUL F-12** ("single/alone" hâlâ dışlama semantiği) → "exactly one" ve "alone"
  çıkarıldı, tarif cümlesine çevrildi. Tamamen atmak Kie'de kalabalığı geri getirir (v2.1
  ölçümü). Kalan risk plana yazıldı ve ölçülecek.
- **KABUL F-13** (`_PENDING_PARTS` part06'yı kapsıyor) → R4-a: kapsam `next_part`'tan
  türetilir.
- **KABUL F-14** (part06 eski doktrin damgasını taşır) → R4-d: `--verify` korunan planlarda
  damga eşitliği ARAMAZ.
- **KABUL F-15** (`batch: 5` → part11 üretir) → R4-f/4: geçici `batch: 4`.
- **KABUL F-16** (`next_part 7 > total_parts 6` çökme durumu) → R4-f: `finally` ile
  `series.json` geri yükleme + son koşul doğrulaması.
- **KABUL F-17** (`rf_transition_check` `next_part == 6` sabiti) → R4-b: snapshot'la
  karşılaştırılır. Bugün `--verify` zaten hatalı çalışıyordu.
- **KABUL F-18** (snapshot plan dosyalarını hash'lemiyor) → R4-c: ham SHA-256 eklendi.
- **KABUL F-19** (CLI şekilleri yanlış) → Doğrulandı, araçlar konumsal `series_dir` alıyor;
  bütün PROOF komutları düzeltildi.
- **KABUL F-20** (mevcut testler kırılacak) → R4-e: izin verilen TAM liste (4 yer). Başka
  test kırılırsa Codex `BLOCKED:` yazıp duracak.
- **KABUL F-21** (bütçe aritmetiği yanlış) → En değerli bulgu. Tavan 1900, omni 10 sn tahmini
  200, müzik 80. ep07'nin ölüm sebebi QC değil BÜTÇEYDİ. Yeni **ROCK 3** (zorunlu ana çekim
  rezervasyonu) buradan doğdu.
- **KABUL F-22** (sentetik test canlı davranışı kanıtlamaz) → §7: tek klip canary'si
  (~126 kredi), İhsan onayına bağlı.

**Plan r2 olarak yeniden yazıldı. Rock sayısı 3 → 4.**
