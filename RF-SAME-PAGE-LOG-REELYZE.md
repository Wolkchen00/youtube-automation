# RF-SAME-PAGE-LOG-REELYZE

Plan dosyasi: `RF-PLAN-REELYZE.md`
Ertelenenler: `RF-ISSUES-REELYZE.md`
Codex oturumu: `01a08bb3-0c37-7611-93a9-c54d12324c55`
Model: `gpt-5.6-sol`, reasoning effort `high`

## Round 1

### Integrator bulgulari (Codex, birebir)

```
- [FIX] Rock 1 and Rock 4 remain separately provable despite the prose-only same-commit warning, so partial delivery can stop publishing -> Merge them into one atomic rock with one end-to-end test that reaches the publisher.
- [FIX] Rock 1 cannot control 30 fps because the Kie payload exposes resolution but no fps field, while every recorded output is 24 fps -> Require a paid 1080p pilot and gate its actual fps, or explicitly normalize and revalidate the final artifact.
- [FIX] Rock 1's dry-run proof only echoes requested JSON and can pass even if Kie rejects 1080p or returns another geometry -> Probe a real downloaded canary and assert 1080x1920 plus the agreed fps before rollout.
- [FIX] Rock 1's dry-run proof is not runnable from a clean checkout because `out/<slug>/PROMPT.txt` is ignored and `<slug>` is only a placeholder -> Prepend `build.py --check`, use a concrete slug, and include output probing in the proof.
- [FIX] Rock 2 sends route durations of 20 and 25 seconds to a model whose documented contract is 4–15 seconds, so Toronto will fail after spending-path entry rather than become correct -> Validate model-duration compatibility before the credit call and shorten those routes or select an explicitly costed compatible model ([Kie contract](https://kie.ai/seedance-2-0)).
- [FIX] Rock 2's `-k "sure or duration"` proof already selects unrelated `build.py` timeline tests and can pass while `gunluk.py` still uses `SURE = 15` -> Add tests asserting the exact duration passed to Kie and reused by the final gate.
- [FIX] Rock 2 proposes new route parsing although `build.load_route()` already owns the validated DURATION field -> Reuse that parser as the single source instead of adding a second Markdown parser.
- [CLARIFY] The repository has no resolution-specific price for `bytedance/seedance-2`; its “720p and 1080p cost the same” note applies only to Omni -> What measured Kie balance delta will be accepted for identical 15-second 720p and 1080p canaries?
- [FIX] `MIN_KREDI = 700` is based on a 615-credit 720p/15-second run and is unchanged despite resolution and duration changes -> Derive the floor from model, duration, resolution, audio, and a protected reserve after measuring the new charge.
- [FIX] A balance check is not a reservation, so another live channel can spend the shared wallet during Fear's long generation -> Join the existing durable credit-reservation mechanism or serialize shared-wallet paid calls.
- [FIX] Importing `core.ffmpeg_tools` has no circular dependency and CI installs `python-dotenv`, but `python AImagine-Fear/tools/gunluk.py` does not put the repo root on `sys.path` -> Bootstrap `YT_KOK` exactly as `yayinla.py` does and add a clean-process CI import test.
- [FIX] Rock 3 masters audio after `denetle()`, meaning the artifact actually published has never passed resolution, duration, audio, or decode validation -> Produce a distinct mastered file, then run the complete gate on that exact file before publishing it.
- [FIX] Rock 3's proof calls nonexistent `kontrol.py --ses`, and `kontrol.py` contains no LUFS or true-peak measurement -> Add the CLI contract or use `measure_audio_loudness`, with a nonzero exit on missing or off-target measurements.
- [FIX] Rock 4 still relies on an untyped flattened ffprobe parse and a fixed 3 MB heuristic, which can pass a corrupt large file or reject a valid efficient one -> Select streams explicitly, parse rational fps, remove the size proxy, and perform a fail-closed full decode check.
- [FIX] Rock 4 promises cut validation in its problem statement but omits cuts from Done and Proof -> Either add a calibrated channel-specific continuity gate or remove that promise.
- [FIX] The fleet map overstates existing protection because `critic.py` is opt-in per-clip semantic QC, some active configurations fail open, and only Unnatural Lab has `master_lufs = -14` -> Audit the four active series against their final published artifact and add the common deterministic technical gate there.
- [FIX] Rock 6 attaches checks to producers rather than publication boundaries, so `fear-slide-hazir.yml`, manual `yayinla.py`, cached series artifacts, or future callers can bypass them -> Enforce the gate in `yayinla.py` and `_publish_part()` immediately before upload.
- [FIX] Rock 6 says scorecard data enters publication records without defining how `gunluk.py` passes it into `yayinla.py` or how series metadata stores it -> Define and test a versioned record schema tied to the published file hash.
- [FIX] Rock 6 leaves every new score nonblocking and therefore ends without delivering the Core Focus's pre-publication gate -> Block immediately on deterministic media-contract failures and keep only calibrated creative proxies report-only.
- [DEFER] First-half-second motion, cut cadence, longest-shot length, OCR presence, and loop similarity are creative-format proxies rather than reliable fleet-wide technical checks -> Move them to calibration work and ship the simpler decode/streams/geometry/fps/duration/LUFS/true-peak gate first.
- [FIX] EBU R128 plus audio-stream presence cannot establish that speech exists, so Rock 5 would report false confidence -> Return speech as unknown unless a tested VAD/ASR classifier actually measures it.
- [FIX] Scene detection at one fixed `scene=0.3` threshold confuses water spray, flashes, and rapid camera motion with edits, and longest-shot measurement inherits the same errors -> Calibrate per channel on labeled real videos and retain raw timestamps and confidence.
- [FIX] First/last-frame similarity does not prove a seamless loop, and first-0.5-second frame difference does not prove intentional motion -> Label both as proxies, exclude them from aggregate scoring, and validate them against a labeled corpus.
- [FIX] A universal “opening text present” score contradicts AImagine-Fear's explicit no-text canon and channels with post-render title cards have different expectations -> Make text policy channel-specific as required, forbidden, or not applicable, with missing OCR always unknown.
- [FIX] Returning one integer score while optional metrics are unmeasured makes scores incomparable across machines and hides missing evidence -> Record policy version, measured denominator, per-metric evidence, and unknown states before introducing an aggregate score.
- [FIX] The synthetic Rock 5 tests can pass while real scene, motion, OCR, and loop measurements are unusably noisy -> Add labeled real-video false-positive and false-negative acceptance limits.
- [FIX] `tests/test_skor_karti.py`, `tests/test_trend_hasat.py`, `core/skor_karti.py`, and `tools/trend_hasat.py` do not exist, and current workflows execute only `AImagine-Fear/tests` -> Make their creation and relevant workflow wiring explicit acceptance work rather than citing absent proofs.
- [FIX] Rock 6's dry runs cannot prove scoring of a final artifact because dry production creates no video to inspect -> Use committed/generated fixtures and assert that the exact hashed upload path receives and persists its scorecard.
- [KILL] Rock 7 is reach, trend, and hook work that the plan itself declares outside the Core Focus -> Remove Rock 7 from this plan entirely.

VERDICT: NOT YET```

### Visionary yaniti (Claude)

29 bulgunun tamami islendi. Hicbiri sessizce dusurulmedi.

**Once bagimsiz dogrulama.** Codex'in dogrulanabilir iddialarini kendim kontrol ettim:

| Iddia | Dogrulama | Sonuc |
|---|---|---|
| `build.load_route()` zaten DURATION ayristiriyor | `build.py:246`, dogrulama `:333-349`, `:444` | DOGRU |
| `measure_audio_loudness` var | `core/ffmpeg_tools.py:171` | DOGRU |
| `kontrol.py --ses` yok | `kontrol.py:69-71` sadece video/--threshold/--no-transcript | DOGRU, kanit uydurmusum |
| `_publish_part` var | `series/series_runner.py:308` | DOGRU |
| Rezervasyon mekanizmasi var, Fear kullanmiyor | `series/balance_floor.py:32` sahibi, Fear'de import yok | DOGRU |
| Sadece unnatural-lab'da `master_lufs` var | tum `bible.json` tarandi, tek eslesme `sentinal_ihsan/unnatural-lab/bible.json:11` | DOGRU |
| Seedance sure sozlesmesi | `core/kie_api.py:489` "integer 4-15s" | DOGRU, ve ayrica **480p/720p**, yani 1080p YOK |

Son satir planin merkezini yikti: **1080p bu modelde mumkun degil.**
Codex bunu maliyet sorusu olarak sormustu; kendi depomuz duz metin olarak yaziyor.

**KABUL EDILENLER (plana islendi):**
- Rock 1 + Rock 4 ayri teslim edilirse yayin durur -> tek atomik rock oldu (yeni Rock 3)
- fps hedeflenemez, Kie yukunde alan yok -> hedef kaldirildi, kanon metni duzeltiliyor, I-2
- Kuru kosu proof'u sahte -> gercek dosya olcumu sart kosuldu
- Proof temiz checkout'tan calismiyor -> somut slug + `build.py --check` on kosulu
- 20/25 sn rotalar duzelmez, patlar (sozlesme 4-15 sn) -> harcamadan ONCE reddet
- `-k "sure or duration"` alakasiz testleri seciyor -> Kie'ye giden degeri dogrulayan test
- Ikinci ayristirici gereksiz -> `build.load_route()` tek kaynak
- 1080p fiyati bilinmiyor -> I-1, Ihsan'in karari, kanarya olcumu sart
- `MIN_KREDI` turetilmeli -> model degismedikce gecerli, degisirse I-1 ile
- Bakiye kontrolu rezervasyon degil -> `balance_floor.py` mekanizmasina katil (Rock 5)
- `sys.path` bootstrap eksik -> `yayinla.py` ile birebir ayni (Rock 5)
- Masterlama `denetle()`'den sonra, yayinlanan dosya kapidan gecmemis -> sira duzeltildi:
  master -> TAM kapi -> yayin, hash ile dogrulanacak (Rock 5)
- `kontrol.py --ses` yok -> `measure_audio_loudness` kullanilacak
- ffprobe duz ayristirma, 3 MB vekili -> acik akis secimi, rasyonel fps, boyut vekili KALDIRILDI
- Kesme vaadi Done/Proof'ta yok -> vaat kaldirildi, I-5
- Filo haritasi korumayi abartti, sadece unnatural-lab'da master_lufs -> **yeni Rock 1 oldu**,
  planin en yuksek getirili maddesi. Bagimsiz olcumum ayni sonucu vermisti.
- Kapilar ureticide, yayin sinirinda degil -> Rock 2 ve Rock 7 sinira tasindi
- Kayit semasi tanimsiz -> surumlu sema + sha256 baglama (Rock 7)
- Her sey report-only kalirsa Core Focus teslim edilmez -> deterministik ihlaller BLOKLAR
- Yaratici vekiller guvenilir degil -> I-3'e tasindi, kapsamdan cikti
- EBU R128 konusmayi kanitlamaz -> konusma tespiti tamamen cikarildi
- Sabit `scene=0.3` esigi su spreyini kesme saniyor -> cikarildi, I-3
  (bu kanalin icerigi tam olarak su ve hizli hareket, esik burada ozellikle guvenilmez)
- Ilk/son kare benzerligi dongu kanitlamaz -> cikarildi
- Metin politikasi kanala gore degisir -> tek tip "metin var mi" puani KALDIRILDI
- Tek tamsayi puan makineler arasi kiyaslanamaz -> puan kaldirildi, olcum + ihlal +
  bilinmeyen + sozlesme surumu donduruluyor
- Sentetik testler gercek gurultuyu yakalamaz -> I-3'te etiketlenmis kume sarti
- Olmayan test dosyalari kanit gosterilmis -> bu dosyalarin YAZILMASI teslimatin parcasi
- Kuru kosu video uretmiyor, skorlanamaz -> hash'lenmis gercek dosya sarti

**KABUL, KILL:**
- Rock 7 (trend/kanca) kapsam disi -> silindi, I-4. Plan "erisimi cozmez" deyip
  erisim rock'u iceriyordu; celiski Codex'in tespiti, haklı.

**REDDEDILEN:** yok.

**Planin yapisal degisimi:** 3 faz / 7 rock korundu ama icerik degisti.
Eski Rock 1 (1080p) OLDU. Yerine `master_lufs` geldi ve plan artik ses ile basliyor,
cunku olculmus etkisi en yuksek ve riski en dusuk olan o.
