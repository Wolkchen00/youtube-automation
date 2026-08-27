# SAME PAGE MEETING — PLAN_PILOT_SONRASI_v1

Kanonik plan: `sentinal_ihsan/PLAN_PILOT_SONRASI_v1.md` · Integrator: Codex CLI 0.145.0 (gpt-5.6-sol, xhigh)
Visionary: Claude Opus 5 · Tur tavani: 5

## Round 1

### Integrator findings (Codex, verbatim)

- [FIX] B1 is only partly verified: `mix_voiceover` omits `normalize=0` and no final-master loudnorm exists, but the repo retains no evidence for −24.5 LUFS or the claimed 6.1 LU experiment -> Commit the ebur128/loudnorm outputs, exact inputs, command, and ffmpeg version.
- [FIX] B1 overstates music-only immunity because `replace_original=True` avoids the faulty voice amix but does not protect source-dependent music output from the missing master stage -> Describe music-only as unaffected only by the amix defect and measure it separately before rollout.
- [FIX] Adding both `normalize=0` and master loudnorm changes narration-to-music balance because the current voice mix is attenuated before the later normalized music-bed mix -> Apply final loudnorm alone first, then enable `normalize=0` only after retuning and comparing program/music ratios.
- [FIX] ROCK A’s default −14 LUFS changes all 19 series at once and can amplify noise or expose clipping in previously quiet masters -> Make mastering opt-in for Unnatural Lab, shadow-measure representative narrated and music-only outputs, then canary the remaining fleet.
- [FIX] ROCK A does not identify a truly final master point because teaser/overlays/upscale follow `_post_process`, while `_upscale_master` creates `delivery_1080.mp4` before returning the 4K path -> Master after all editorial transforms and ensure both 1080p and 4K deliveries are derived from or independently verified against that master.
- [FIX] ROCK A’s native-foley correlation proof can pass with practically inaudible foley because correlation is invariant to gain -> Add speech-free-window level delta or foley-to-bed ratio limits alongside correlation.
- [FIX] `narration.master_lufs` versus `series.master_lufs` is an unresolved schema choice whose proposed −14 default silently migrates every bible -> Choose one canonical opt-in field with explicit disabled/legacy behavior and validation.
- [FIX] B6’s non-fit conclusion is correct, but 4,484 omits the unused 300-credit preflight stage and treats stage caps as planned spend -> Show the full 4,784-credit worst case and explicitly reallocate stage caps under the unchanged 4,000 total.
- [FIX] ROCK E cannot run as proved because the ledger has spent 1,584 of the 1,700 `pilot` stage cap, leaving only 116 while its command again uses `--stage pilot` -> Add an authorized `pilot2` stage or durably reallocate caps before any paid call.
- [CLARIFY] The claimed current Kie balance of roughly 8,165 is not present in repository evidence although it drives K1-B -> What timestamped balance source establishes that value?
- [FIX] B7 is factually wrong: experiment-tagged ep22 logs contain 18 visual reviews and 18 native-audio reviews, while all 15 `scene_cut_scan` events are local ffmpeg work and the claimed 20 reviews include two unrelated August 24 events -> Instrument every actual Gemini `generate_content` attempt and report retries, fallbacks, task type, experiment ID, and quota response separately.
- [FIX] ROCK B’s `violation_reads` cannot reliably prove temporal or negative claims such as “never reaches the counter” from one frame -> Restrict statements to frame-observable outcomes or evaluate an ordered clip interval with an explicit unobservable/null result.
- [FIX] ROCK B’s `anomaly_match` is not reliably boolean when the interior is occluded, too small, wet, or viewed from another angle -> Require visibility/coverage and confidence fields, returning null unless material and topology are actually observable.
- [FIX] ROCK B adds `anomaly_descriptor` without specifying that `ensure_episode_refs` must include it, hash it, and invalidate stale `prop_ref_urls` -> Generate the NB2 hero from both descriptors and persist a descriptor-to-reference hash with regeneration tests.
- [FIX] ROCK B’s fixture proof can pass through hardcoded ep22 expectations while production fails to pass the new fields into the real review request -> Add an end-to-end plan-to-reference-to-Gemini-payload-to-qc_log test using a held-out fixture.
- [FIX] P7 has no fixture size, held-out split, human-label protocol, or promotion thresholds, so a poor report still satisfies ROCK B Done -> Predeclare minimum coverage and maximum false-pass/false-reject rates plus an explicit log-only-to-gated promotion decision.
- [FIX] ROCK C folds `state_carry` into the already fail-closed `continuity_ok`, contradicting its own log-only promise and P7 -> Introduce a separate nullable `state_carry_ok` measurement and leave `continuity_ok` enforcement unchanged until calibration passes.
- [FIX] ROCK C’s framing method cannot work as described because existing first-frame infrastructure measures only luma contrast and sharpness, not hero-object bounds or center -> Use background feature registration for camera drift or add a validated detector/segmentation fixture before reporting object geometry.
- [FIX] ROCK C’s proof would pass whenever a script emits numbers even if it tracked the wrong bright region rather than the hero object -> Require human-labeled bounding boxes or known synthetic transforms with quantified localization error.
- [FIX] P8 conflicts with P7 as written because the proposed cap of 60 is anchored to the false B7 count and may halt calibration during hidden retries or fallback-model attempts -> First log actual API attempts, then set a measured cap with retry headroom while piggybacked fields remain log-only.
- [FIX] A per-process QC counter can reset across reruns and miss the calls hidden inside model/retry loops -> Increment a durable episode-attempt counter immediately before every visual and audio `generate_content` call, including fallbacks.
- [CLARIFY] ROCK D assumes selecting another visible model provides a separate quota pool, but no quota-boundary evidence or billing decision is specified -> Which project, billing tier, and documented quota boundary makes the selected model operationally independent?
- [DEFER] ROCK C is measurement-only and cannot improve Pilot 2 while occupying the sequential path back to publication -> Collect framing/state telemetry during Pilot 2 and early kill-gate episodes without making ROCK C a K8 prerequisite.
- [FIX] The ordering does not demonstrate compliance with K8’s September 16 deadline because B-D have no timeboxes and both ROCK D and E await owner decisions -> Set dated stop-loss milestones, default to K1-B(b), enable Unnatural Lab-only audio mastering, and begin K8 no later than a fixed first-week date.
VERDICT: NOT YET
### Visionary response (Claude, tur 1)

Doğrulama notu: Codex'in en sert üç iddiası bağımsız olarak kontrol edildi. **B7 düzeltmesi doğru**
(qc_log: 08-26'da 18 review + 18 native_audio; 15 scene_cut_scan kaydı yerel ffmpeg alanları taşıyor;
3 kayıt 08-24 tarihli). **Teslim zinciri iddiası doğru** (produce.py 1613→1638→1665→1703→1713;
`_upscale_master` delivery_1080.mp4'ü satır 504'te üretiyor). **first_frame altyapısı iddiası doğru**
(`first_frame_ok` bir vision-LLM alanı; yerel ölçüm yalnız `luma_contrast_proxy` + `sharpness_proxy`,
core/ffmpeg_tools.py:95 ,  kahraman obje sınırı üretmiyor).

- ACCEPTED: B1 kanıtı repoda yok -> `sentinal_ihsan/measurements/pilot1_audio.md` eklendi (komutlar,
  ham ebur128 çıktısı, kontrollü amix deneyi, sürümler, zarf ölçümleri).
- ACCEPTED: müzik-only bağışıklığı abartılı -> B1 ikiye ayrıldı: amix kusuru yalnız anlatımlı serileri,
  master aşamasının yokluğu 19 serinin tamamını vuruyor.
- ACCEPTED (uyarlanarak): `normalize=0` + loudnorm birlikte anlatım/müzik oranını kaydırır -> ikisi
  birlikte uygulanıyor AMA ROCK A.5 oran ölçümü zorunlu kılıyor (konuşma penceresi program ↔ yatak
  farkı ±1,5 dB dışına çıkarsa `music_volume` ölçümle yeniden ayarlanır). İki ayrı sürüme bölmek
  yerine tek sürüm + P9 (yalnız yayını duran seride açılır) tercih edildi: filo riski zaten sıfır,
  iki üretim çevrimi beklemek K8 penceresini yiyor.
- ACCEPTED: -14 varsayılanı 19 seriyi birden değiştirir -> tek kanonik alan `series.master_lufs`,
  alan yoksa davranış bit-değişmez; bu çevrimde yalnız unnatural-lab'e yazılıyor; filoya yayılım
  ayrı karar (K-FILO) + gölge ölçüm + kanarya.
- ACCEPTED: gerçek master noktası yanlıştı -> ROCK A.2 zinciri ölçülen sırayla yazdı; master
  `_upscale_master` öncesine kondu, overlay/upscale adımlarının sesi kopyaladığı testle doğrulanacak,
  delivery_1080 ve 4K aynı master'dan türeyecek.
- ACCEPTED: korelasyon kazançtan bağımsız -> ROCK A.6 mutlak seviye + foley/yatak oranı eşikleri ekledi;
  ölçüm dosyasına da uyarı düşüldü.
- ACCEPTED: şema seçimi belirsiz -> `series.master_lufs` tek kanonik alan, yokluğu = legacy (kapalı).
- ACCEPTED: B6 aritmetiği eksik -> preflight 300 dahil en kötü 4.784 yazıldı; aşama tavanlarının
  "planlanan harcama değil üst sınır" olduğu açıkça belirtildi.
- ACCEPTED: ROCK E `pilot` aşamasında koşamaz (kalan 116 kr) -> ROCK D artık `pilot2` aşaması açmayı
  (veya kalıcı yeniden pay) şart koşuyor ve K1-B'ye bağlandı.
- ACCEPTED (CLARIFY yanıtlandı): Kie bakiyesi kanıtsızdı -> canlı ölçüldü: **5.999 kr**
  (2026-08-27 08:50, `kie_api.check_credit()`). Hafızadaki 8.165 bayatmış. Bu, yeni **B8** bulgusu ve
  yeni **K-KREDI** acil karar maddesi oldu; filo ömrü ~4 gün.
- ACCEPTED: B7 sayımı yanlış -> düzeltildi (36 loglanan çağrı) ve asıl mesele yeniden yazıldı:
  yeniden deneme/yedek model/429 loglanmadığı için gerçek çağrı sayısı ölçülemiyor.
- ACCEPTED (kısmi düzeltmeyle): `violation_reads` tek kareden zamansal/olumsuz iddiayı kanıtlayamaz ->
  kabul; ancak review çağrısı zaten **12 sıralı kare** görüyor (`bible.qc.frames = 12`), yani sıralı
  değerlendirme mevcut. Kural: cümle bu 12 karelik örneklemde gözlemlenebilir olmak zorunda,
  olumsuz/zaman-ötesi ifade yasak, `null` serbest.
- ACCEPTED: `anomaly_match` her durumda boolean olamaz -> üç yeni alan da
  `{value: bool|null, visible: bool, confidence}` biçimine geçti; görünmüyorsa `null`.
- ACCEPTED: `anomaly_descriptor` referans zincirine bağlanmamıştı -> `ensure_episode_refs` iki
  descriptor'ü birlikte kullanacak, `ref_prompt_sha256` yazılacak, descriptor değişince kayıtlı
  `prop_ref_urls` geçersiz sayılıp yeniden üretilecek (+ testler).
- ACCEPTED: fixture kanıtı üretim yolunu atlayabilir -> ROCK B proof'una uçtan uca zincir testi eklendi
  (plan → ensure_episode_refs → Gemini istek gövdesi → qc_log), tutulan fixture ile.
- ACCEPTED: P7 protokolsüzdü -> P7 artık sayı veriyor: alan başına ≥24 etiketli kare (≥8 negatif),
  en az yarısı held-out, insan etiketi, terfi eşiği yanlış-geçiş ≤%10 / yanlış-red ≤%20.
- ACCEPTED: `state_carry`'yi fail-closed `continuity_ok` içine katmak P7 ile çelişiyordu ->
  ayrı, nullable, log-only `state_carry_ok` alanı; `continuity_ok` davranışı değişmiyor.
- ACCEPTED: ROCK C'nin kadraj ölçüm yöntemi mevcut altyapıyla imkânsız -> ölçüm ERTELENENLER'e
  taşındı; pilot-2 ve kill-gate bölümlerinde telemetri olarak toplanacak, K8 ön koşulu değil.
- ACCEPTED: o rock'ın proof'u herhangi bir sayıyla geçerdi -> madde ertelendiği için düştü;
  geri geldiğinde insan etiketli kutu veya bilinen sentetik dönüşüm şartı yazıldı.
- ACCEPTED: P8'in 60 tavanı yanlış sayıya çapalıydı -> P8 yeniden yazıldı: önce ölçümleme,
  sayısal tavan pilot-2 verisinden sonra.
- ACCEPTED: süreç-içi sayaç yeniden başlatmada sıfırlanır -> ROCK C.1 kalıcı, çağrı öncesi artan,
  görev tipi/model/deney kimliği/yanıt sınıfı kıran sayaç şart koşuyor.
- ACCEPTED (CLARIFY yanıtlandı): başka model = ayrı kota havuzu varsayımı kanıtsız -> ROCK C.4 artık
  açıkça "model değiştirmek kota stratejisi değildir" diyor; gerçek çözüm ayrı proje/anahtar veya
  ödemeli katman (K-G).
- ACCEPTED (DEFER): ROCK C yalnız ölçümdü ve yayın yolunu tıkıyordu -> ertelendi (yukarıda).
- ACCEPTED: K8 uyumu gösterilmiyordu -> tarihli tablo eklendi (ROCK A 08-28 → kill-gate en geç 09-08),
  K1-B için 08-30 varsayılan kararı, ve stop-loss: 09-08'e kadar kill-gate başlamazsa kalan rock'lar
  ertelenir, kanal A+B stack'iyle yayına döner.

Visionary'nin kendi ek bulgusu (Codex yakalamadı): **B9** ,  `bible.json > qc.notes` hâlâ
"the bench / the tools / resets the background, the bench or the light" diliyle yazılı; seri
2026-08-26'da 4 ev ortamına geçti. QC'ye giden metin ortamla çelişiyor; ROCK B.7'de onarılacak.

REJECTED: yok. Tur 1'in 24 bulgusunun tamamı kabul edildi (biri düzeltmeyle, biri uyarlanarak).

## Round 2

### Integrator findings (Codex, verbatim)

- [FIX] ROCK A still violates P9 because the unconditional `mix_voiceover normalize=0` change affects every narrated series even when `series.master_lufs` is absent, making the promised 18-series bit-identical proof impossible -> Gate amix normalization behind an opt-in parameter enabled only for Unnatural Lab or defer it to K-FILO.
- [FIX] ROCK A specifies offline proof but not fail-closed production behavior when two-pass mastering fails, so a copied-through −24.5 LUFS file could still publish -> When `master_lufs` is configured, require successful final LUFS/true-peak verification or return `qc_hold`.
- [FIX] ROCK A’s foley and program/music acceptance criteria remain non-executable because the absolute-level and foley-to-bed thresholds are unspecified and the proof command accepts no music/program reference -> Declare numeric thresholds, reference inputs, window-selection rules, and one reproducible comparison command.
- [FIX] ROCK A assumes Topaz preserves mastered audio even though the external upscale response is not governed by the local `-c:a copy` flags -> Remux the pre-upscale mastered audio into the returned 4K video and verify both 1080p and 4K deliverables.
- [FIX] B9’s repair is incomplete because `series/critic.py` and `series/produce.py` also hardcode “workbench” in continuity, regeneration, environment-reference, and object-reference prompts -> Make every shared prompt surface environment-neutral, not only `bible.json > qc.notes`.
- [FIX] ROCK B does not explicitly update the existing schema whitelists, so `OBJECT_CARD_FIELDS` and `_validate_batch` normalization can discard `anomaly_descriptor`, `violation_statement`, and `state_carry` before production -> Name every whitelist/normalizer change and migrate part23 before its proof command runs.
- [FIX] `violation_statement` still uses a negative example (“tezgâhta birikinti oluşmuyor”) and has no applicable-shot binding, so non-violation shots cannot return a meaningful gate value -> Store a positive observable checkpoint on the relevant shot, such as `shot.violation_observation`, and mark other shots N/A.
- [FIX] `state_carry` does not identify which shot creates the state or which subsequent shot must retain it -> Define it on the source shot, evaluate it only against the next shot, and log N/A where no successor exists.
- [FIX] P7 labels standalone frames while `violation_reads` and `state_carry_ok` judge ordered multi-frame or cross-shot evidence -> Build fixtures from the same ordered image groups and previous-frame context used by production.
- [FIX] P7 can promote an abstaining model because null coverage is unconstrained and held-out positive/negative composition is not guaranteed -> Require class-stratified held-out examples and a minimum observable coverage, counting unjustified nulls as errors.
- [FIX] ROCK C says every 429 becomes `qc_hold`, which conflicts with its retained retry and fallback behavior when a later attempt succeeds -> Log intermediate 429s but emit `qc_hold(reason="quota")` only after the configured attempt policy is exhausted.
- [FIX] ROCK C’s unspecified persistent counter file leaves durability, concurrency, and crash recovery open while the existing durable QC journal already solves the problem more simply -> Append uniquely identified `qc_api_attempt` and `qc_api_result` events to `qc_log.jsonl`, with an unmatched attempt representing a crash or unknown result.
- [FIX] ROCK D still offers two incompatible budget mechanisms while its proof assumes a `pilot2` stage exists -> Choose `pilot2` now, assign its exact cap of at most 800, and state the resulting stage-cap map under the unchanged 4,000 total.
- [FIX] K-KREDI has no decision deadline, no live preflight, and no protected kill-gate reserve, while 5,999 credits at 1,550 per day cannot support the September 8 schedule -> Set a dated decision and mechanically reserve enough for intervening fleet consumption, Pilot 2, and the first kill-gate publications before authorizing Pilot 2.
- [FIX] The schedule unnecessarily marks all of ROCK C as blocked on K-G even though attempt logging and terminal-quota classification require no owner choice -> Implement the unblocked instrumentation immediately and make only QC-key provisioning decision-dependent with a dated fallback.
- [DEFER] Promoting all three new gates by September 4 is not required to begin a safe measured K8 and expands the critical path while Pilot 2 remains credit-blocked -> Keep them log-only unless P7 evidence is ready, and require human approval for their checks until each field is promoted.
- [FIX] The September 8 stop-loss can enter auto publication with the three new quality failures still log-only and without defaults for K-G or K8 approval mode -> Default to full human approval and a working dedicated QC key until the new gates are calibrated and explicitly promoted.
VERDICT: NOT YET
### Visionary response (Claude, tur 2)

Doğrulama notu: iki iddia bağımsız kontrol edildi, ikisi de doğru çıktı. **workbench sızıntısı**
gerçekten `bible.json` dışında da var (`series/critic.py:153, 437, 441, 1141, 1145`;
`series/produce.py:851, 878`). **Şema beyaz listesi** gerçekten yeni alanları düşürür
(`series/shots.py: OBJECT_CARD_FIELDS` → `series/replenish.py` normalizasyonu ~1003/~1151).
Ayrıca K-KREDI için gerçek tüketim `credits_ledger.json`'dan ölçüldü: **son 7 gün ortalaması
1.390 kr/gün** (tam günde 1.600-2.000).

- ACCEPTED: koşulsuz `normalize=0` P9'u çiğniyordu ve bit-değişmezlik iddiasını imkânsız kılıyordu ->
  ROCK A.1: **tek opt-in anahtar `series.master_lufs`**; alan yoksa amix davranışı dahil ses yolu
  bugünküyle birebir aynı; yeni yol yalnız unnatural-lab'de açık.
- ACCEPTED: mastering başarısızlığında üretim davranışı tanımsızdı -> ROCK A.6: `master_lufs`
  tanımlıyken mastering/doğrulama başarısızsa **`qc_hold`**; normalize edilmemiş dosya yayına gidemez.
- ACCEPTED: foley/oran eşikleri sayısızdı -> ROCK A.7 sayılarla yazıldı: master −14 ±1 LUFS,
  TP ≤ −1,0 dBTP; pencere tanımı (100 ms, TTS zarfı tepenin %8'i altı); foley konuşmasız pencerede
  program ≥ −30 dBFS ve yalnız-müzik referansının ≥ 6 dB üstü; anlatım/yatak farkı ±1,5 dB bandı;
  tek komutla ölçülür (`--ref-raw --ref-tts --ref-bed`).
- ACCEPTED: Topaz dış servis, yerel `-c:a copy` garanti etmez -> ROCK A.5: master'lanmış ses dönen
  4K'ya **remux** edilir, 1080p ve 4K ayrı ayrı doğrulanır.
- ACCEPTED: B9 eksikti -> ROCK B.8 artık altı kod yüzeyini de kapsıyor, metinler
  `object_card.environment`'tan besleniyor, diğer seriler için fallback korunuyor.
- ACCEPTED: şema beyaz listeleri isimlendirilmemişti -> ROCK B.2 dört yüzeyi de adıyla sayıyor ve
  `part23.json`'un proof'tan ÖNCE migrate edilmesini şart koşuyor.
- ACCEPTED: `violation_statement` olumsuz ve çekime bağsızdı -> çekim bazlı, OLUMLU
  `shot.violation_observation`; ihlal taşımayan çekimlerde N/A.
- ACCEPTED: `state_carry` kaynak/ardıl belirsizdi -> kaynak çekimde tanımlanır, yalnız bir sonraki
  çekime karşı değerlendirilir, ardılı yoksa N/A.
- ACCEPTED: P7 fixture'ları üretim bağlamını taklit etmiyordu -> fixture'lar üretimin gördüğü sıralı
  12 karelik grup + önceki çekimin son karesi bağlamıyla hazırlanır.
- ACCEPTED: P7 null kapsamı sınırsızdı -> sınıf-katmanlı held-out zorunlu; gözlemlenebilir vakalarda
  null oranı ≤ %30, gerekçesiz null hata sayılır.
- ACCEPTED: her 429'u `qc_hold` yapmak retry/fallback ile çelişiyordu -> ara 429'lar loglanır,
  `qc_hold(quota)` yalnız deneme politikası tükendiğinde.
- ACCEPTED (basitleştirme kabul): yeni kalıcı sayaç dosyası gereksizdi -> mevcut `qc_log.jsonl`
  defterine `qc_api_attempt` / `qc_api_result` olayları; eşleşmemiş attempt = çökme/bilinmeyen.
- ACCEPTED: ROCK D iki uyumsuz bütçe mekanizması sunuyordu -> tek seçenek: **`pilot2` aşaması,
  tavan tam 800**; aşama haritası yazıldı (pilot 1.700 dondu / pilot2 800 / preflight-bakeoff-holdout 0;
  tahsis edilmemiş 1.500 yalnız K1-B ile açılır).
- ACCEPTED: K-KREDI tarihsiz ve rezervsizdi -> karar tarihi **2026-08-28**; ölçülen tüketim
  (1.390 kr/gün) ve kill-gate ihtiyacı (~16.500 kr) yazıldı; pilot-2 öncesi mekanik rezerv şartı
  ROCK D'ye kondu. Ayrıca ölçüm şunu gösterdi: **mevcut bakiyeyle kill-gate imkânsız** ,  bu, planın
  en sert gerçeği olarak K-KREDI'ye taşındı.
- ACCEPTED: ROCK C'nin tamamı K-G'ye bağlıydı -> C1 (ölçümleme + kota sınıflandırma) karar beklemez,
  08-29'da yapılır; yalnız C2 (anahtar) karara bağlı ve 08-31 tarihli varsayılanı var.
- ACCEPTED (DEFER): üç kapının 09-04'te terfi etmesi zorunlu değil -> terfi ZORUNLU DEĞİL;
  eşiği tutmayan alan log-only kalır ve bu başarısızlık sayılmaz.
- ACCEPTED: stop-loss log-only kapılarla otomatik yayına girebilirdi -> stop-loss artık açıkça
  diyor ki: alanlar log-only ise yayın modu **K8-b (tam insan onayı)**, otomatik yayın yok.

REJECTED: yok. Tur 2'nin 17 bulgusunun tamamı kabul edildi.

## Round 3

### Integrator findings (Codex, verbatim)

- [FIX] ROCK A’s audio criteria still omit reference gain/fade/alignment and aggregation rules, while the proof command has no pre-change master from which to verify the ±1.5 dB balance claim -> Add `--baseline-final`, define exact reference preprocessing, and specify percentile/proportion thresholds across the selected 100 ms windows.
- [FIX] ROCK A requires separate 1080p and 4K verification but its proof accepts only one `<final.mp4>`, so broken Topaz audio remux can pass -> Run the checker explicitly against both deliverables and add a test where corrupted 4K audio causes `qc_hold`.
- [FIX] ROCK A’s Done requires all 18 non-opted-in series to remain bit-identical while its proof checks only one unspecified series -> Cover at least narrated and `replace_original=True` fixtures and assert every non-Unnatural bible lacks the opt-in.
- [FIX] P7’s report can run on an undersized or in-sample fixture set because no label-manifest format or minimum-count assertion is specified -> Define an immutable train/held-out manifest and make the reporter refuse promotion unless every field satisfies the declared sample, class, and split counts.
- [FIX] ROCK B does not define `visible` independently of expected-feature presence, allowing a missing violation or carried state to evade failure as `visible=false,value=null` -> Define visibility as observability of the relevant region/action and test visible-but-absent cases as `visible=true,value=false`.
- [FIX] ROCK B says fields become fail-closed without defining a promotion switch or the runtime treatment of false, null, invisible, and low-confidence results -> Add per-field enforcement configuration, an exact verdict table, and tests proving a promoted false or unjustified null blocks delivery.
- [FIX] `ref_prompt_sha256` invalidation is tied only to descriptor changes even though name, environment description, prompt template, and anomaly descriptor also affect the generated reference -> Hash the canonical complete prompt plus a template version and regenerate on any hash mismatch.
- [FIX] ROCK B’s environment-language proof can pass without exercising regeneration helpers, and the current code also emits “bench” from `critic.py:450`, which is absent from the enumerated locations -> Test every actual QC/reference/regeneration prompt with a bathroom fixture and assert environment-derived language with no workbench fallback leakage.
- [FIX] ROCK C1 cannot guarantee durable attempt accounting while the existing `_log_event` deliberately swallows write failures and still permits the paid call -> Use a strict append-and-flush path for `qc_api_attempt` and do not call Gemini unless that attempt is durably recorded.
- [FIX] ROCK C1’s result class `fallback-model` conflates which model was attempted with whether that attempt succeeded, rate-limited, or failed -> Keep outcome strictly `ok|429|error` and record fallback status or parent attempt separately on the attempt event.
- [FIX] ROCK C1 holds only terminal quota exhaustion, so exhausted authentication, 5xx, parsing, or logging failures can still reach the existing unreviewed-accept path -> Make exhaustion of any QC attempt policy produce `qc_hold`, with quota and non-quota reasons alerted separately.
- [FIX] ROCK D’s reserve formula omits the roughly 1,390-credit daily fleet burn during the ten kill-gate days, making the claim that a 15,000-credit top-up secures the dated schedule false -> Recompute the live requirement through the tenth publication, including pre-start fleet burn, Pilot 2, and concurrent fleet-plus-Unnatural burn.
- [FIX] ROCK D says credits are “mechanically reserved” without naming an enforceable shared-balance mechanism, while current episode and experiment ledgers cannot stop other workflows consuming that balance -> Add a global balance floor honored atomically by every paid workflow or obtain approval to pause the other fleet until the kill-gate finishes.
VERDICT: NOT YET
### Visionary response (Claude, tur 3)

Doğrulama notu: `series/critic.py:450`'nin de "bench" ürettiği doğrulandı (regen düzeltme metni) , 
tur 2'de ne Codex ne ben yakalamıştık, B9 listesine eklendi. Kredi aritmetiği yeniden hesaplandı ve
**Codex haklı çıktı**: yazdığım "15.000 kr yeterli" iddiası yanlıştı.

- ACCEPTED: ses ölçüm sözleşmesi eksikti (referans işleme, hizalama, toplama kuralı, baseline yok) ->
  ROCK A.7 yeniden yazıldı: mono 8 kHz indirgeme, ham dosya (fade/kırpma yok), 100 ms pencere,
  konuşmasız pencere tanımı, **medyan** toplama + ihlal eden pencere oranı, ve `--baseline-final`
  parametresi (±1,5 dB iddiası artık ölçülebilir).
- ACCEPTED: proof tek dosya alıyordu, bozuk Topaz remux'ı geçebilirdi -> checker **iki teslimatta
  ayrı ayrı** koşuyor; bozuk 4K sesi → `qc_hold` testi eklendi.
- ACCEPTED: bit-değişmezlik iddiası tek belirsiz seriyle kanıtlanamaz -> iki fixture (bir anlatımlı,
  bir `replace_original=True` müzik-only) + "unnatural-lab dışında hiçbir bible'da `master_lufs` yok"
  assert'i.
- ACCEPTED: P7 raporu küçük/örneklem-içi sette koşabilirdi -> **etiket manifesti** (immutable,
  sınıf ve split alanlarıyla) tanımlandı; raporlayıcı manifest sayıları tutmazsa terfi önermez, exit 1.
- ACCEPTED (en değerli bulgu): `visible` tanımı beklenen özelliğin varlığına kayıyordu, yani eksik
  ihlal `visible=false, value=null` ile kapıdan kaçabilirdi -> `visible` artık **bölge/eylem
  gözlemlenebilirliği** olarak tanımlı; görünür-ama-yok vakası **`visible=true, value=false`** ve
  fixture'da ayrı test sınıfı.
- ACCEPTED: terfi anahtarı ve çalışma zamanı davranışı tanımsızdı -> `qc.enforce.<field>` konfigürasyonu
  + tam karar tablosu (true / false+visible / null+invisible / gerekçesiz null / düşük güven) +
  terfi etmiş alanın teslimatı bloke ettiğini kanıtlayan testler.
- ACCEPTED: referans hash'i yalnız descriptor'e bağlıydı -> hash artık **kanonik tam prompt +
  şablon sürümü** üzerinden; herhangi bir bileşen değişirse referans geçersiz.
- ACCEPTED: ortam dili proof'u regen yardımcılarını dolaşmıyordu ve `critic.py:450` listede yoktu ->
  450 eklendi; proof **banyo fixture'ıyla** tüm QC/referans/regen prompt'larını sınıyor ve
  ortam alanı olan seride fallback'e düşülmediğini assert ediyor.
- ACCEPTED (kritik): `_log_event` yazma hatasını yutuyor, sayaç dayanıklı olmazdı -> ROCK C1:
  `qc_api_attempt` **katı append+flush**; attempt kalıcı yazılamadıysa **çağrı yapılmaz**.
- ACCEPTED: sonuç sınıfı fallback bilgisini karıştırıyordu -> sonuç yalnız `ok | 429 | error`;
  `is_fallback` ve model bilgisi attempt olayında.
- ACCEPTED: yalnız kota tükenmesi hold üretiyordu -> **her tükenme sınıfı** (`quota/auth/server/
  parse/logging`) `qc_hold` üretir; kota ve kota-dışı ayrı alarmlanır; "incelenmemiş kabul" yolu kapanır.
- ACCEPTED: kredi rezerv formülü kill-gate günlerindeki filo tüketimini atlıyordu -> yeniden hesaplandı:
  08-27→09-08 filo 16.680 + pilot-2 800 + kill-gate 10 gün 18.400 = **35.880 kr ≈ $179**;
  yükleme **≈ 29.900 kr ≈ $149**. Önceki "$75" rakamı yanlıştı, K-KREDI seçenekleri yeniden yazıldı.
- ACCEPTED: "mekanik rezerv" uygulanabilir bir mekanizmaya bağlı değildi -> yeni **ROCK D0:
  küresel `KIE_BALANCE_FLOOR`** ,  ücretli çağrı yapan tüm yollar canlı bakiyeyi okur, taban altında
  reddeder; kill-gate rezervi bununla korunur.

REJECTED: yok. Tur 3'ün 13 bulgusunun tamamı kabul edildi.

## Round 4

### Integrator findings (Codex, verbatim)

- [FIX] ROCK A downsamples finals to mono 8 kHz before all measurements, so native-rate stereo clipping or true-peak overs can pass -> Measure LUFS and dBTP on each encoded delivery at its native channel layout and sample rate; use mono 8 kHz only for envelope comparisons.
- [FIX] ROCK A aligns pre-teaser raw stems from the first sample and compares against an unprocessed music file even though production prepends a teaser and applies looping, gain, and fades -> Export aligned stems at the final master point or reproduce the exact production edit and bed filter graph before window comparisons.
- [FIX] P7 defines train/held-out splits without stating that promotion thresholds are calculated exclusively from held-out results, allowing strong train results to conceal broken held-out performance -> Calculate promotion metrics only on the held-out split and report train results separately.
- [FIX] D0 checks only whether cached pre-call balance exceeds the floor, so one large call or concurrent workflows can cross the reserve while its proof still passes -> Under a cross-workflow lock, authorize only when fresh balance minus the current estimate and all outstanding reservations remains at or above the floor, and test concurrent authorization.
- [FIX] D0 does not define how kill-gate jobs consume the balance protected by their own floor, so a static floor either blocks the kill-gate or must be lowered and cease protecting it -> Give the kill-gate an owner-tagged reservation that is transactionally drawn down and reconciled while unrelated workflows remain subject to the residual floor.
VERDICT: NOT YET
### Visionary response (Claude, tur 4)

Beş bulgunun beşi de "kanıt bozukken de geçer" sınıfında; hepsi kabul edildi.

- ACCEPTED: LUFS/true-peak'i mono 8 kHz'e indirgenmiş sinyalde ölçmek geçersizdi (stereo kırpma ve
  true-peak aşımı görünmez kalır) -> ölçüm sözleşmesi ayrıldı: **loudness ve TP teslim dosyasının
  kendi kanal düzeni ve örnekleme hızında** (`ebur128=peak=true`, downmix/resample yok);
  mono 8 kHz yalnız zarf karşılaştırması için.
- ACCEPTED: zarf hizalaması üretimin gerçek kurgusunu yok sayıyordu -> hizalama final master'ın zaman
  eksenine yapılır (teaser kayması `teaser_len` düşülür), **müzik yatağı referansı üretimin filtre
  grafiğiyle (loop + volume + afade) yeniden üretilir**, ham `bg_music.mp3` kullanılmaz; native
  referans master noktasındaki stem'den alınır.
- ACCEPTED: P7 terfi metriklerinin hangi split'ten hesaplandığı yazılmamıştı -> **terfi metrikleri
  yalnız held-out'tan**; train ayrı raporlanır ve karara girmez.
- ACCEPTED: D0 önbellekli bakiyeyle ve tek çağrı varsayımıyla çalışıyordu -> kural sertleşti:
  **taze bakiye − bu çağrının tahmini − açık rezervasyonlar ≥ taban**, kontrol+rezervasyon
  **workflow'lar arası kilit** altında atomik; eşzamanlılık testi ve "açık rezervasyonlar hesaba
  katılmazsa test KIRMIZI" kanıtı eklendi.
- ACCEPTED: statik taban kill-gate'i ya bloke eder ya da korumasını kaybederdi -> kill-gate
  **sahip etiketli rezervasyondan** (owner="killgate") işlemsel olarak düşülür ve mutabakat yapılır;
  taban yalnız bu rezervasyonun dışındaki bakiyeyi korur.

REJECTED: yok.

## Round 5

### Integrator findings (Codex, verbatim)

The plan is executable. The r5 changes close the remaining behavioral, proof, fleet-safety, credit, and K8-window blockers.

VERDICT: SAME PAGE
### Visionary response (Claude, tur 5)

Anlasma saglandi. Kanonik plan r5 donduruldu; build asamasi ROCK A ile baslar.
Toplam: 5 tur, 59 bulgu, 59 kabul, 0 red. Codex CLI 0.145.0 / gpt-5.6-sol / xhigh.
