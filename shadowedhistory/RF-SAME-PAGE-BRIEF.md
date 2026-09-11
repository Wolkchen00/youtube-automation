# RF-SAME-PAGE-LOG , flashpoints brief + kunye kurali

Codex CLI 0.154.0 · model `gpt-5.6-sol` · effort high
Thread: 01a08e5b-d5b2-7f11-924f-ab7ede1c9285

## Round 1

### Integrator findings (Codex, verbatim)

```
- [CLARIFY] The brief is injected into `contents` after SERIES/ART STYLE and before calibration, topic pools, history, and repair errors, while TITLE_CARD lives in the separate higher-priority `system_instruction`; “follow the CREATIVE BRIEF strictly” is also in that system instruction -> Test and describe `contents` and `system_instruction` separately, not as one ordered prompt.
- [FIX] The proposed recognizability rule conflicts with both `<subject name, max 40 chars>` and `"title" = the subject/site name`, and a user-level brief cannot reliably override either system-level instruction -> Add an opt-in flashpoints title-card rule in config and make `_build_prompt` use it for both the schema placeholder and TITLE_CARD rule while preserving the existing default for other channels.
- [FIX] The exact stale strings are `v1.6, 2026-07-29`, `İki çekim vardır, toplam yaklaşık 12 sn.`, and `Narration 26-38 kelimedir`, versus doctrine v1.8, `shots: 2` × `shot_seconds: "10"`, and narration 26–36 -> Update all three, but describe duration unambiguously as “two 10-second source shots, approximately 19 seconds after trimming.”
- [FIX] Replacing “12 sn” with merely “~19 sn” still leaves the model reading both `~20-second piece` in the system prompt and `~19 sn` in the brief -> Explain raw versus edited duration in the brief or render the finished duration consistently from `shots`, `shot_seconds`, and `micro_trim`.
- [CLARIFY] The plan’s claim that v1.8 “never reached the model” is false because the system prompt already renders 2×10 seconds, 26–36 words, measured documentary pace, an 18.3-second speaking window, complete-sentence endings, and same-scene continuity -> Reframe the defect as conflicting duplicate instructions, not missing delivery.
- [FIX] The hardcoded `gentle, loopable resolve` conflicts with flashpoints’ “closer and harder” second shot that ends during continuing action -> Make the episode-arc wording channel-configurable or remove “gentle resolve” when `voiceover_continuity` is enabled.
- [FIX] The brief unconditionally requires integer `topic_pool` seeds, but the engine can inject calibration card topics with `n15-…` string IDs and requires those first -> Update the brief for both seed classes or explicitly prove card topics are permanently disabled; `extra_topics` is only empty today.
- [FIX] The brief says consecutive families can never repeat, while the engine deliberately permits a first-episode repeat when no alternative family remains -> State the same exhaustion exception in the brief or remove that engine relaxation.
- [FIX] Proof item 3 can pass during a new drift because 26–36 is always rendered from structured config even if the brief changes to another wrong range; today the prompt contains both config-derived 26–36 and brief-derived 26–38 -> Isolate the CREATIVE BRIEF section, parse its numeric range, and compare it directly with `narration.min_words/max_words`.
- [FIX] Proof item 2 only excludes “12 sn,” so any other incorrect duration would pass -> Parse the brief’s duration statement and compare it with the configured raw and trimmed durations.
- [KILL] Proof item 7 is impossible as written because blanking the brief leaves “12 sn absent,” config-derived 26–36, documentary pacing, and complete-sentence rules true -> Require only brief-owned markers to disappear and separately require structured/system invariants to remain.
- [FIX] Proof item 5 checks fragments and examples rather than the operative prohibition, so an inverted or toothless recognizability rule could pass -> Assert the complete unknown-name prohibition, replacement behavior, and a corrected Kiska output example such as `EMPTY ISLAND INVASION / Alaska, 1943`.
- [FIX] No validator enforces recognizability: `_validate_batch` accepts any nonempty title card satisfying length and year checks -> Add deterministic per-seed title-card labels or a channel-scoped validation contract if recognizable output—not merely prompt wording—is required.
- [CLARIFY] `_build_prompt` itself needs no network, API key, calibration, or nonempty history, and blank brief is callable; however importing `series.replenish` requires `python-dotenv` and `requests` and import-time config opens `logs/youtube.log` and creates output directories, while real `SeriesMeta.load`/`Bible.load` require their JSON files -> Keep the test repository-rooted and ensure its environment permits those import side effects, or refactor imports to be hermetic.
- [CLARIFY] Editing only `shadowedhistory/flashpoints/series.json:auto_replenish.brief` and adding a test does not change other channels, but changing the shared TITLE_CARD default would -> Use an opt-in flashpoints config override rather than replacing the shared default globally.
VERDICT: NOT YET```

### Visionary response (Claude)

Codex bu turda planin IKI TEMEL VARSAYIMINI curuttu. Ikisini de bagimsiz olarak
dogruladim ve plan yeniden yazildi.

- **ACCEPTED (varsayimim YANLISTI)** , "v1.8 modele hic ulasmadi"
  -> `series/replenish.py:740` kelime butcesini yapisal config'ten basiyor
  (`{wmin}-{wmax}` = 26-36) ve `:732-739` tempo + "must end with a complete
  sentence" kurallarini basiyor (`voiceover_continuity` acik). Yani v1.8 sistem
  prompt'unda ZATEN var. Gercek kusur EKSIKLIK degil CELISKI: brief ayni sayilari
  farkli soyluyor. Plan bu cerceveyle yeniden yazildi.

- **ACCEPTED (Rock 2 degistirildi)** , kullanici brief'i sistem kuralini ezemez
  -> `_build_prompt` docstring'i dogruladi: `(contents, system_instruction)`.
  TITLE_CARD kurali (`:748`) ve sema yer tutucusu (`:701`) `system_instruction`
  icinde; brief `contents` icinde. Kullanici metniyle sistem kuralini ezmeye
  calismak ongorulemez davranis uretir.
  -> Codex'in onerdigi yol alindi: opt-in kanal ayari + `_build_prompt` icinde
  ezme. Emsal ZATEN VAR: `:729` `title_rule = title_style or (varsayilan)`.
  Yani yeni mimari degil, mevcut kalibin ikinci kullanimi. Ayar yokken diger uc
  kanal bit bit ayni cikti uretir ve proof bunu olcuyor (madde 9).

- **ACCEPTED** , ezme IKI yeri birden kapsamali
  -> `:701` sema yer tutucusu da `"<subject name, max 40 chars>"` diyor. Yalniz
  kurali degistirip semayi birakmak celiskiyi surdururdu. Proof madde 7 bunu
  ayrica denetliyor.

- **ACCEPTED (Rock 1'in yonu degisti)** , "~19 sn yaz" yerine "sayiyi CIKAR"
  -> Codex "~19 sn de sistem prompt'undaki ham sure ifadesiyle catisir" dedi.
  Dogru. Bugunku kaymanin sebebi zaten sayinin IKI yerde tutulmasiydi: config
  degisti, prose degismedi. Yeni karar: brief hicbir sayi tasimasin, tek kaynak
  yapisal config olsun.

- **ACCEPTED** , proof 7 [KILL]
  -> Hakli: brief bosaltilinca "12 sn yok", config-turevi 26-36, tempo ve tam
  cumle kurallari HALA dogru kalir; "hepsi kaybolsun" imkansiz bir iddiaydi.
  Capa yeniden yazildi: yalniz brief'e/ayara AIT isaretler kaybolmali, yapisal
  config'ten gelenler KALMALI (madde 8).

- **ACCEPTED** , proof 2 ve 3 zayifti
  -> "12 sn" ve "26-38" ifadelerini dislamak, BASKA yanlis bir sayiyi gecirirdi.
  Yeni proof brief blogunu IZOLE EDIP icinde herhangi bir sure/kelime sayisi
  kalibi aramiyor (madde 3), ve sistem talimatindaki araligi yapisal config ile
  KARSILASTIRIYOR (madde 4).

- **ACCEPTED** , proof 5 parcalara bakiyordu
  -> Tersine cevrilmis veya disi sokulmus bir kural da gecerdi. Madde 6 artik
  yasagi, yerine koyma talimatini ve duzeltilmis Kiska ornegini AYRI AYRI ariyor.

- **ACCEPTED (sinir olarak yazildi)** , hicbir dogrulayici taninirligi zorlamiyor
  -> `_validate_batch` uzunluk ve yil disinda kunyeye bakmiyor. Bu kosu PROMPT'u
  duzeltir, CIKTIYI garanti etmez. Kapsam disi bolumune acikca yazildi.

- **DEFERRED** , `gentle, loopable resolve` celiskisi; `topic_pool` string ID'li
  calibration konulari; aile tekrari istisnasi
  -> Ucu de gercek ve ucu de dogrulandi. Ucu de bu kosunun kapsami disinda,
  "Kapsam disi" bolumunde gerekceleriyle duruyor. Ozellikle string ID'li konular
  sessiz bir mayin: bugun `extra_topics` bos oldugu icin patlamiyor.

- **NOT** , kapsam GENISLEDI: plan artik `series/replenish.py`'ye TEK SATIRLIK
  bir ezme ekliyor. Ilk surum "motor degismeyecek" diyordu. Degisiklik mevcut
  `title_style` kalibinin aynisi ve opt-in; ama kapsam degisikligi oldugu icin
  burada acikca kayda geciyor.
