# Same Page Log — Next Stop v2 (RF-PLAN-NEXTSTOP-V2.md)

Model: gpt-5.6-sol (reasoning=high). Round 1 ilk denemesi 10 dk zaman aşımı (kapsam geniş); daraltılmış promptla taze oturum başarılı. Thread: 01a05973-9ff4-71f0-b525-9e2fb6dfa73f

## Round 1
### Integrator findings (Codex, verbatim)
```
- [KILL] The plan assumes prompt changes alone can reproduce Seedance/Higgsfield-style multi-scene behavior in Omni, while its own risk section accepts failure as success -> Gate rollout on one real 10-second Omni pilot showing three distinct vistas, two fully masked transitions, and synchronized visible passenger reactions.
- [KILL] Accepting only two vistas contradicts the core 2.5–3.5-second cadence and makes the stated success criterion unfalsifiable -> Treat fewer than three vistas per 10-second clip as a failed pilot, not an acceptable improvement.
- [FIX] “Three vistas,” “three masked vistas,” and a view changing every 2–3 or 2.5–3.5 seconds describe different numbers and timings of transitions -> Specify exactly three vistas separated by exactly two full-window masks, preferably near 3.1 and 6.3 seconds, with an explicit shot-6 exception.
- [FIX] Shot 1’s first mask at about 4 seconds violates both the 2.5–3.5-second cadence and art_style’s stricter “every two to three seconds” rule -> Move its masks to roughly 3.1 and 6.3 seconds and align art_style to the same range.
- [FIX] Chained shots are seeded by a clear prior last frame yet are told to open after a mask has already happened, so the requested new vista conflicts with the actual seed -> Start shots 2–6 in the inherited vista and place the first complete mask after the clip begins.
- [FIX] The 0.45-second head trim can remove the seam mask, impact peak, and initial passenger reaction on every chained shot -> Make the opening event begin before 0.45 seconds but keep the full mask and reaction peak visible around 0.55–0.9 seconds.
- [FIX] The final “Next stop-” is placed at the raw clip ending where the 0.45-second tail trim can delete it -> Finish the audible cutoff before roughly 9.5 seconds, with the arrival line and chime moved earlier.
- [FIX] Passengers are allowed to occlude the bottom third of the window but are simultaneously forbidden from appearing anywhere inside the window rectangle -> Forbid people only beyond or reflected in the glass, while explicitly permitting near-side silhouettes to overlap a tightly limited edge area.
- [FIX] A window occupying 75% of frame can expose only 50% of frame after one-third occlusion, below the reference’s stated 60–90% visible-window range -> Cap total silhouette occlusion to about 10–15% of the window and keep reacting head-and-shoulder outlines visibly in frame.
- [FIX] “Masked cuts” and “the journey is cut” invite editing despite the unbroken-take rule, while smoke, spray, or embers may not fully conceal a morph -> Call them continuous occlusion transitions and permit a vista reset only during demonstrably opaque blackout or full overexposure.
- [FIX] Subsecond masks cannot physically advance the train between distant districts while the brief also says masks never skip the journey -> Require adjacent track-connected vistas and let the mask hide only a short continuous interval, not unexplained geographic displacement.
- [FIX] A camera looking exactly 90 degrees sideways cannot repeatedly observe landmarks “far ahead” growing toward it -> Describe landmarks entering from the leading edge of the side window, crossing laterally, and exiting the trailing edge.
- [FIX] “The outside is always brighter than the interior” contradicts “the sky is the darkest part of the frame” -> Make the sky the darkest exterior region while keeping the carriage darker still.
- [FIX] The new prefixes are mechanically valid because validation requires the exact prefix plus two newlines and a 30-character body, but their long fixed timelines can conflict with destination-specific timestamps added by Gemini -> Shorten each prefix to invariant beat constraints and require the body to supply one authoritative time-coded vista sequence.
- [FIX] Rock 3’s delete-then-reset logic is sound only if every part04–08 file is absent; any surviving consecutive file will be re-adopted and alter the queue calculation -> After the current run finishes and pull completes, assert part04–08 are all absent, verify next_part is 4, set total_parts to 3, then replenish.
- [FIX] Rock 3 omits committing and pushing the canon, config, counter, deletions, and regenerated plans, so tomorrow’s runner can still consume the old repository state -> Complete and push one coherent commit before 13:20 UTC and verify no workflow is running during the reset.
- [KILL] Rock 4 proves JSON generation and dry-run assembly but cannot prove Omni produced masked transitions or passenger physics -> Add a real pilot clip and inspect the complete video timeline before allowing automated production.
- [FIX] QC can pass while broken because it samples frames, can miss fraction-second masks, and compares against the raw shot prompt without art_style requirements -> Add time-targeted checks around each commanded mask and reaction, using the assembled final prompt or repeating every critical canon requirement in each shot.
- [FIX] Manually reading only part04 leaves 24 prompts in part05–08 unverified, and exact-prefix validation does not validate cadence semantics -> Run a deterministic audit over all 30 prompts for two masks, three vistas, timestamps, passenger reactions, direction continuity, and exact prefixes.
- [FIX] Shot 6 does not protect the 4.5–5.9-second teaser interval from landing on blackout or shake, so the prepended hook may be visually empty -> Reserve that interval for a clear spectacular vista and place shot-6 masks outside it.
VERDICT: NOT YET```
### Visionary response (Fable)
- ACCEPTED (KILL#1 + KILL#17, pilot): gerçek üretim kanıtı şart -> yeni ROCK 3: 2 çekimlik gerçek Omni pilotu (~252 kredi), Fable kare kare doğrular; pilot geçmeden kuyruk yenilenmez.
- ACCEPTED (KILL#2): "2 vista da olur" esnekliği kaldırıldı -> pilot ölçütü tam 3 vista + 2 tam maske; düşüş = başarısız pilot, revizyon.
- ACCEPTED (FIX cadence tutarsızlığı): tek sözleşme -> 3 vista / 2 tam maske, maskeler ~3.0 ve ~6.5; çekim 1 istisnası (~4/~7) ve çekim 6 istisnası (tek maske ~3) brief'te açık.
- ACCEPTED (FIX chain-seed çelişkisi): çekim 2-6 önceki vistanın İÇİNDE açılır, ilk tam maske ~1.0 sn'de -> shot_plan ve SEAM RULE yeniden yazıldı.
- ACCEPTED (FIX micro_trim baş): kritik olay ilk 0.5 sn'e yazılmaz; açılış darbesi ~1.0 sn (trim sonrası ~0.55) -> zamanlama sözleşmesi bölümü eklendi.
- ACCEPTED (FIX micro_trim son / "Next stop-"): varış anonsu ~8.0, kesilme ≤9.3 -> çekim 6 öneki ve brief kural 6.
- ACCEPTED (FIX pencere içi yolcu çelişkisi): yasak cam-ötesi + yansımaya daraltıldı; siluetler pencerenin en alt altıda birini örtebilir -> canon yeniden yazıldı.
- ACCEPTED (FIX %75 pencere vs 1/3 örtme): örtme sınırı alt 1/6.
- ACCEPTED (FIX "masked cuts" kurgu çağrışımı + yarı saydam maske morph riski): "occlusion transitions" adı; sahne sıfırlama YALNIZ tam karartma/tam patlama; yeşillik-duman-kıvılcım kısmi maske=doku.
- PARTIAL (FIX coğrafi sıçrama): WWII tarzı serbest ışınlanma REDDEDİLDİ (serinin fizik kimliği Core Focus'un parçası); kabul edilen biçim: yeni vista aynı hattın ilerisi, maske kısa aralığı sıkıştırır -> canon + brief kural 4.
- ACCEPTED (FIX 90° yan bakış vs "far ahead"): leading edge -> trailing edge geometrisi canon'a yazıldı.
- ACCEPTED (FIX parlaklık çelişkisi): gök MANZARANIN en karanlık bölgesi, vagon içi ondan karanlık.
- PARTIAL (FIX önek saatleri vs Gemini gövde saatleri): önekler kısaltılMADI (kadans determinizmi bu işin özü); çözüm brief kural 6: gövde önekle çelişen saat yazamaz, önek saatlerine vista içeriği doldurur.
- ACCEPTED (FIX Rock 3 assert): silme sonrası ardışık artık kontrolü + next_part==4 doğrulaması -> Rock 4 adım 1-2.
- ACCEPTED (FIX commit/push): Rock 5'e push-before-13:20-UTC + workflow-not-running koşulu eklendi.
- PARTIAL (FIX QC kör noktası): QC kod değişikliği non-goal; kritik dil ham çekim promptunda taşındığı için QC görür; zaman-hedefli maske denetimi ISSUES'a DEFER.
- ACCEPTED (FIX 30 prompt denetimi): deterministik denetim betiği (Rock 4.5) tüm 5x6 promptu tarar.
- ACCEPTED (FIX teaser penceresi): çekim 6'da 4-7 sn temiz spektakl; maske ~3'te.

## Ara not: koltuk devri (2026-08-31 ~15:15 yerel)
Codex ChatGPT kullanım limitine takıldı (15:53'e kadar kapalı; round 2 iki denemede de
"usage limit" hatası). Boş beklememek için Visionary, Rock 1-2 düzenlemelerini (bible
art_style v2 + series.json shot_plan/brief v2) PILOT ÖN KOŞULU olarak kendisi uyguladı
ve Rock 3 pilotunu başlattı (deney: nextstop-v2-pilot, 6 çekim tam bölüm — 2 çekimlik
pilot, produce'un 6-çekim/hook_shot=6/başlık-deseni katı doğrulamasına takıldı; pilot
aşama kapağı 800 kredi, tam bölüm ~756 kredi sığıyor). Ayrıca 4-mercekli bağımsız
adversarial stres-testi (workflow) koşuldu. Codex dönünce: round 2 plan doğrulaması +
Rock 1-2 diff incelemesi + Rock 4-5 build Codex koltuğunda.
