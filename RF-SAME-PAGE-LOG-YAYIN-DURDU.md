# RF-SAME-PAGE-LOG , Shadowed History yayin durmasi (2026-08-31)

Plan dosyasi: `RF-PLAN-YAYIN-DURDU.md` · Codex: codex-cli 0.145.0, model `gpt-5.6-sol`,
reasoning effort `high` · Thread: `01a0595e-2570-7123-9288-2f1ac9f053be`

## Round 1

### Integrator findings (Codex, verbatim)

- [FIX] Two factual citations are wrong: `_download_release(...)` is at `approver.py:122`, not 130, and `parse_mode="Markdown"` is at `notifier.py:51`, not 52 -> Correct the citations before treating the plan as an implementation specification.
- [CLARIFY] The Akilli_Watchdog `config.py:192`, 26-hour window, and compatibility claims cannot be verified because that repository and commit are absent from this workspace -> Provide the exact watchdog checkout/commit and current contract tests.
- [FIX] ROCK0's "no artifact to lose" claim is overstated because QC logs record paid raw clips for both stuck parts, while only final videos/releases are absent -> Account for the lost clips and persist resumable media on future holds.
- [DEFER] Unnatural Lab recovery is outside the Shadowed History Core Focus and part 23 already has 436 of its 800-credit durable cap spent, leaving too little for four fresh Omni shots -> Restore Flashpoints first and move Unnatural Lab recovery to the Issues List.
- [FIX] ROCK0 proof can pass while YouTube remains silent because `series.json` state and a green `gh run list` are not publication evidence -> Require a non-empty YouTube video ID and verify it belongs to the target channel.
- [FIX] `qc_retry` will not duplicate uploads because `qc_hold` returns before `_publish_part`, but fresh Actions checkouts lose outputs and the held clip is renamed `_qchold`, so retries regenerate paid shots despite existing same-clip QC retries -> Persist and restore passed/held clips for QC-only retry, or budget and test every provider call across all attempts.
- [KILL] The proposed "content-originated `qc_hold`" branch does not exist: bad content becomes `fail`, while `qc_hold` represents unevaluable QC, reference, or mastering failures and always receives a reason -> Remove the string-presence classification and use typed retryable reason codes.
- [FIX] `needs_human` is not terminal in the current runner because only `awaiting_approval` blocks production, and ROCK1's proof stops immediately after the transition -> Add an explicit block and assert a fourth run calls neither production nor upload.
- [FIX] The approval branch currently writes `awaiting_approval` even when `release_tag` or `approval_msg_id` is missing, recreating the same dead state independently of QC -> Fall back to a retryable failure unless video, release, and approval card are all confirmed, with separate tests for each missing artifact.
- [FIX] ROCK1's proof only shows that production is attempted again and can pass even if no video is ever published -> Add a hold-to-retry-to-confirmed-YouTube state-machine test with provider and uploader call-count assertions.
- [FIX] ROCK2 gives generic `notifier.send_message` no series path for writing `alert_delivered:false`, and the later workflow step would overwrite that field anyway -> Return structured delivery status to one atomic result writer and add a live Telegram canary rather than letting the notifier mutate `last_run.json`.
- [FIX] Current code marks a part published and advances it when any platform succeeds, so Instagram-only success can make `published_at` green while YouTube is silent -> Require confirmed YouTube success for Shadowed History advancement and monitor the latest part containing `youtube` in `platforms_ok` plus its video ID.
- [FIX] Treating completed or other no-op runs as successful work evidence can refresh green state forever without a new video -> No-op runs must not refresh publication evidence; use the latest confirmed channel-level YouTube publication timestamp.
- [FIX] ROCK3's 30-hour evidence window directly violates the 24-hour notification requirement and polling delay can extend it further -> Set the threshold below 24 hours by at least one polling interval and test the worst-case alarm time.
- [DEFER] Migrating all five workflows and introducing a new cross-repo schema is unnecessary surface for this cycle -> Keep the existing `ts/outcome` contract, derive Flashpoints values from confirmed YouTube publication evidence, and defer fleet rollout until the Shadowed History repair is proven.
- [FIX] ROCK4 overstates that billing practically removes the cap because Gemini limits remain model-, project-, and tier-dependent and paid tiers only provide higher limits -> Measure the project's active AI Studio limits and seven-day demand, then set a spend ceiling before requesting a billing decision.

VERDICT: NOT YET

### Visionary response (Claude) , her bulgu bagimsiz dogrulandi

- ACCEPTED: satir numaralari -> `grep -n` ile dogrulandi (`approver.py:122`, `notifier.py:51`);
  plan duzeltildi.
- ACCEPTED (kanit eklendi): watchdog ikinci repoda, Codex goremez. Kendim okudum:
  `Akilli_Watchdog/config.py:191-197` flashpoints hedefi, `window_hours: 26`,
  `outcome_field_required: true`; cron `0 5 * * *` (GUNDE TEK KOSU). Bu olcum plana
  Olgu 4 + Bolum 2 olarak girdi ve mimariyi degistirdi: 24 saat garantisi nobetciden
  degil hattin kendi aninda alarmindan gelir.
- ACCEPTED, kismen duzeltildi: "kaybedilecek artefakt yok" ifadesi asiriydi. Ama Codex de
  eksik: ODENMIS KLIP HALA CANLI , `series_log.csv` ep21 cekim-1 URL'i bugun HTTP 200,
  5.8 MB (kendim curl ile olctum). Cekim 2 tutuldugu icin CSV'ye hic yazilmadi. Plana
  Olgu 7 olarak girdi; "kayitli URL'den devam et" optimizasyonu kapsam disina yazildi.
- ACCEPTED (rakam duzeltmesiyle): unnatural-lab bu cevrimden cikarildi, Ihsan karari
  olarak Bolum 5'e tasindi. Duzeltme: bolum tavani 800 degil **900**
  (`unnatural-lab.yml:67 EPISODE_CREDIT_CAP=900`); defterde `unnatural-lab:23 = 436.0`,
  kalan 464. Codex'in "yeterli olmayabilir" tespiti gecerli.
- ACCEPTED: ROCK 0 proof'u `published.json` son kaydinda `results.youtube` bos olmayacak
  sekilde YouTube video id'sine baglandi.
- ACCEPTED: retry'in yukleme cogaltmadigi dogrulandi (qc_hold `_publish_part`'tan once
  doner); kredi maliyeti plana acikca yazildi, klip kalicilastirma kapsam disi.
- KISMEN REDDEDILDI, fix KABUL: Codex'in gerekcesi hatali , `qc_hold` HER ZAMAN reason
  almiyor. `critic.py` "hold" verdictini 7+ yerde uretiyor (627/660/662/664/666/692/697/
  1361/1412/1481) ama `budget["hold_reason"]` yalniz API tukenmesinde (1496) yaziliyor;
  digerlerinde `reason=None` doner. Sonuc ayni: metin varligina bakan siniflandirma
  yanlis -> TIPLI neden kodu. Ayrica "icerik kaynakli qc_hold dali" gercekten yok,
  o dal plandan cikarildi (Olgu 6).
- ACCEPTED: `needs_human` icin `run_next`'e acik blok + 4. kosunun ne urettigini ne
  yukledigini dogrulayan test.
- ACCEPTED (bagimsiz dogrulandi): `series_runner.py:526-533` onay modunda `tag`/`msg_id`
  None olsa da `awaiting_approval` yaziyor. Plana Olgu 2'nin "ikinci kapisi" olarak
  girdi; ROCK 1 sinir kurali bunu kapatiyor.
- ACCEPTED: ROCK 1 proof'u hold -> retry -> yayin durum makinesi + cagri sayaci oldu.
- ACCEPTED: notifier `last_run.json`'a dokunmaz; yapisal teslim durumu doner, yazan tek
  bilesen kosu sonucunu yazandir. Telegram canary DEFER (ayri is).
- ACCEPTED (kanit tarafinda): `_publish_part` herhangi bir platform basarisinda
  `mark_published` + `advance` yapiyor , dogrulandi (series_runner.py:314-316, 274-276).
  KANIT alani YouTube'a ozgulestirildi. Ilerletme DAVRANISINI degistirmek ayri karar,
  kapsam disi.
- ACCEPTED: no-op kosular yayin kanitini tazelemez.
- ACCEPTED: 30 saat esigi Core Focus'un 24 saatiyle celisiyordu. Yeni mimari: aninda
  alarm birincil, nobetci 20 saat penceresiyle yedek; nobetci frekansi ayri iste artar.
- ACCEPTED: sema migrasyonu 5 workflow + ikinci repoya yayilmiyor. `ts/outcome` korunur,
  yalniz geriye uyumlu alan eklenir, once flashpoints kanitlanir.
- ACCEPTED: ROCK 4 "tavan kalkar" iddiasi cikarildi; once 7 gunluk olcum, sonra harcama
  tavaniyla karar.

## Round 2

### Integrator findings (Codex, verbatim)

- [FIX] Olgu 6 is still factually wrong: `critic` can produce an internal hold without `budget["hold_reason"]`, but `produce.py:1472-1475` and `1619-1622` replace it with `"mandatory QC unavailable for shot N"`, so `ProduceResult(reason=None)` does not reach the runner -> Correct the diagnosis while retaining typed reason codes because the current fallback loses cause specificity.
- [FIX] The Unnatural Lab cap correction is wrong: `produce.episode_credit_cap()` prefers `bible.json`’s `credit_hard_cap_value:800` over workflow `EPISODE_CREDIT_CAP=900`, and the existing test asserts 800 -> Record 436/800 spent and 364 remaining.
- [FIX] A 20-hour threshold with one daily watchdog poll can detect silence almost 44 hours late, and even two daily polls can take almost 32 hours -> Bring polling into this cycle and enforce `threshold + maximum poll interval <= 24h`.
- [FIX] The immediate pipeline alarm does not cover failures before `series_runner`, including checkout/install failures and the non-`continue-on-error` replenish step, so production can be skipped without any alert -> Add an independent `if: always()` failure-alert step and rely on the corrected watchdog for workflows that never start.
- [FIX] `delivered=false` plus a red workflow still does not notify Ihsan, and ROCK2 specifies no retry for network, token, chat, or permanent Telegram failures -> Persist an alert outbox and retry it independently within the 24-hour bound.
- [FIX] Current `run_next` exposes only a boolean and the CLI exposes only an exit code, so the workflow cannot reliably derive `published|noop|held|failed` or alert delivery without an undefined new contract -> Specify a typed `RunResult` and one atomic machine-readable result writer, with no log parsing.
- [FIX] ROCK3 still says `published -> success` while current publication means any platform succeeded, so an Instagram-only run can be green with no immediate Telegram alert and the stated proof can pass while YouTube is dark -> Define the monitoring action `published` as YouTube-confirmed, classify IG-only as failure for outcome/alert purposes, without changing advancement.
- [FIX] Completed-series and günde-1 no-ops are not legitimate successes unless the channel has a YouTube-confirmed publication for that day; otherwise the primary alarm stays silent -> Make no-op success conditional on channel-level YouTube evidence and alert immediately when none exists.
- [FIX] ROCK1’s hold-to-retry-to-“published” proof inherits the current any-platform meaning and can pass on Instagram-only success -> Require `platforms_ok` to contain YouTube, a strict YouTube identifier, `action=published`, and `outcome=success`.
- [FIX] ROCK0 waits for UTC rollover, but Gemini daily quotas reset at midnight Pacific according to the [official rate-limit documentation](https://ai.google.dev/gemini-api/docs/rate-limits) -> Wait for the provider’s reported reset time or midnight Pacific, not 00:00 UTC.
- [FIX] A non-empty `published.json.results.youtube` is not conclusive because `series_runner._publish_identifier()` recursively accepts a generic `id` from the full response -> Use the uploader’s stricter publication identifier and verify the ID through YouTube against the expected channel.
- [FIX] The risk section incorrectly says the episode cap bounds Flashpoints retries: Flashpoints has no series hard cap or durable episode spend, and every retry receives a fresh 900-credit reservation -> State the cumulative worst-case cost and add a durable per-part retry budget if three attempts are retained.
- [FIX] ROCK4 option (c) is still wrong because a second key in the same project does not double project-level quota, and a line-by-day census cannot evaluate per-model limits -> Make option (c) a second project plus key and report day × project × model using unique recorded attempts.
VERDICT: NOT YET

### Visionary response (Claude) , tur 2

**Onemli: tur 1'deki iki kendi duzeltmem tur 2'de curudu, kayit duzeltiliyor.**

- KABUL, kendi hatam duzeltildi: `qc_hold` reason'i runner'a asla None gelmiyor ,
  `produce.py:1471-1474` ve `1618-1621` bos reason'i
  `"mandatory QC unavailable for shot {n}"` ile dolduruyor. Tur 1'deki "reason=None doner"
  ifadem YANLIS. Tipli neden kodu fix'i gecerli kaliyor (genel yedek metin nedeni siliyor).
- KABUL, kendi hatam duzeltildi: unnatural-lab bolum tavani **800** , `episode_credit_cap()`
  `bible.json` -> `series.credit_hard_cap_value=800` degerini env'deki 900'un onune aliyor
  (`produce.py:161-170`). Tur 1'de "900" yazmistim, Codex hakli. 436 harcanmis, 364 kalmis.
- KABUL: nobetci matematigi , 20 saat esik + gunde tek yoklama = en kotu ~44 saat.
  Bu cevrimde yoklama frekansi da degisiyor: esik 12 saat + 6 saatte bir yoklama.
- KABUL: `series_runner` oncesi adimlar (checkout, pip, ikmal) patlarsa hicbir alarm
  gitmiyor -> `if: always()` bagimsiz alarm adimi + job kirmizi (GitHub bildirimi 2. kanal).
- KABUL: teslim edilemeyen alarm icin kalici outbox + sonraki kosuda yeniden deneme.
- KABUL: `run_next` yalniz bool donuyor -> tipli `RunResult` + tek atomik yazici, log
  ayristirma yok.
- KABUL: `action=published` YouTube dogrulanmis demek; IG-only yayin `failed` sayilir
  (ilerletme davranisi degismez).
- KABUL: no-op ancak o gun kanal duzeyinde YouTube yayini varsa success.
- KABUL: `_publish_identifier` genel `id` anahtarini kabul ediyor (series_runner.py:124-145)
  -> ROCK 0 proof'u 11 karakterlik gecerli YouTube kimligi + kanal dogrulamasi istiyor.
- KABUL: flashpoints'te seri tavani ve kalici `episode_spend` YOK , her deneme taze 900
  rezervasyon aliyor. ROCK 1 part-basi kalici retry butcesi getiriyor.
- KABUL: ROCK 4 (c) ayni projede ikinci anahtar degil, **ayri proje + anahtar**.
- YENI KANIT (r3, Codex gormedi): `qc_log.jsonl` filo sayimi , 28 Ag 2.5-flash 29 ok /
  26 429, 29 Ag 11 ok / 22 429 ve flash-latest 2 ok / 9 429. Hat basina: unnatural-lab tek
  gunde 122 cagri. Cron sirasi flashpoints'i her gun EN SONA koyuyor, kota Pasifik gece
  yarisinda sifirlaniyor. Kok neden filo duzeyinde kota rekabeti -> ROCK 4'e (d) sira
  adaleti secenegi eklendi.
- CANLI OLCUM: 2026-08-31 ~13:05 PT'de QC anahtariyla `gemini-2.5-flash` generateContent
  cagrisi 200 OK dondu , birincil modelde bugun kota var (ROCK 0 beklemek zorunda degil).
  `gemini-flash-latest` probe'u iki denemede de baglanamadi (HTTP 000, sonucsuz).

## Round 3 , CALISTIRILAMADI (DEGRADED)

Iki deneme de basarisiz. Stream hatasi (kelimesi kelimesine):
`"You've hit your usage limit. Upgrade to Pro ... or try again at 3:53 PM."`
Codex hesap duzeyinde kullanim limitine takildi; taze oturum da ayni limite carpar.
**Toplanti tur 2'de `VERDICT: NOT YET` ile durdu.** r3 revizyonu tur-2'nin 13 bulgusunun
tamamini isliyor ama Codex tarafindan DOGRULANMADI. Limit sifirlandiktan sonra
(15:53 PT) tur 3 ayni thread ile (`01a0595e-2570-7123-9288-2f1ac9f053be`) kosulmali.

## ROCK 0 , UYGULANDI ve DOGRULANDI (2026-08-31)

**Yapilanlar**
1. `gh workflow disable unnatural-lab.yml` , Ihsan karari: o hat simdilik donduruldu
   (part 23 oldugu gibi duruyor, gunluk kosu QC kotasi yakmiyor).
2. `shadowedhistory/flashpoints/series.json` part 21: `awaiting_approval` -> `planned`
   (commit 80d8293), push origin/main.
3. Tetiklemeden hemen once canli kota probe'u: `gemini-2.5-flash` generateContent HTTP 200.
4. `gh workflow run flashpoints.yml` -> run 33445384960 (workflow_dispatch, 22:15:46Z).

**Kosu ne yapti (log kaniti, ozet)**
- Cekim 1 ilk uretimde QC RED (yasakli oge) -> regen 1/1 -> QC GECTI (artifact 0/10).
- Cekim 2 QC GECTI (artifact 1/10). Merge + final export + anlatim (Charon) + Suno muzik
  + kunye "Cleopatra VII".
- Yayin: 3/3 platform OK (YouTube senkron, IG ve TikTok asenkron dogrulandi).

**Bagimsiz dogrulama (Codex'in tur-1/2'de istedigi siki kanit)**
- `series.json` part 21: `status=published`, `platforms_ok=[youtube,instagram,tiktok]`,
  `published_at=2026-08-31T22:29:24Z`; `next_part=22`.
- `published.json` son kayit: part 21, `results.youtube="KBmoJvN4spE"` , 11 karakter
  duzenli ifadeyi gecti.
- oEmbed: baslik "The Real Reason Cleopatra Ruled Without Translators",
  `author_url=https://www.youtube.com/@shad0wedhistory357`; watch sayfasinda kanal kimligi
  `UCUdp0KLBh4EeeSgVbwS_DhA` dogrulandi.
- Video indirildi ve izlendi (yt-dlp + ffmpeg): 1080x1920, 30 fps, 15,04 sn, opus stereo.
  EBU R128: I=-19,6 LUFS, TP=-6,5 dBFS, LRA=1,5 LU. flashpoints `bible.json`'da
  `master_lufs` YOK -> eski ses yolu, master kapisi bu seride zaten calismiyor (spec ihlali
  degil, ama K-FILO'da ele alinmali).
- Kontakt sayfasi: kunye "CLEOPATRA VII / Alexandria, 48 BC" ilk 3 saniyede okunuyor;
  cekim 1 sutunlu disari sahnesi, cekim 2 papirus/mürekkep yakin plani.

**QC'nin kacirdigi gozlem (Ihsan'a not)**
13-15. saniyedeki mesaleli tas ic mekanda arkadaki iki muhafizin zirh/mifer silueti
Ptolemaios donemi (MO 48) yerine gec antik/ortacag hissi veriyor; bible'in "kiyafet,
mimari, nesne ve teknoloji zaman capasiyla ortusmeli" kuralinin sinirinda. Agir alan
derinligi yuzunden bulanik, izleyicinin fark etme ihtimali dusuk , kanal doktrini acisindan
kayda gecirildi, yayin geri cekilmedi.

**Dogrulamadigim sey:** anlatimin sesli icerigini birebir dinleyip/transkript edip plandaki
metinle karsilastirmadim; anlatimin varligi kosu logu + ses karakteristigi ile teyitli.
Plandaki metin 37 kelime (hedef bant 26-38).
