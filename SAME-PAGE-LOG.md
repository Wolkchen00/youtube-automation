# SAME PAGE LOG, AIMAGINE sabit-kare pivotu (cairo_ia)

Toplantı: Fable 5 (Visionary) ↔ Codex gpt-5.6-sol (Integrator, salt-okunur).
Plan dosyası: PLAN.md · Doktrin: aimagine/KONSEPT.md v2.0 · Tavan: 5 tur.

## Round 1

### Integrator findings (Codex, verbatim)

- [FIX] Deleting part06–10 while leaving `total_parts=10` makes replenish see five pending parts and perform a no-op -> Temporarily set `total_parts=5` before replenish or add an explicit missing-plan regeneration path, then finish at 10.
- [FIX] `produce_episode` succeeds with any non-empty `shot_files`, and QC explicitly drops rejected shots, so an incomplete episode can be auto-published -> Require all six numbered shots to pass QC before assembly or publication.
- [FIX] A last-frame extraction or ImgBB upload failure leaves the older `chain_url` active, allowing shot 5 to chain from exterior shot 3 after shot 4 -> Clear chain state at every break and fail closed whenever the next chained shot lacks its immediate predecessor's frame.
- [FIX] Unconditional frame uploads after shots 3 and 6 add needless ImgBB dependencies even though the following shot breaks or does not exist -> Use one-shot lookahead and upload only after shots 1, 2, 4, and 5.
- [FIX] Producer-side validation is unaware of `chain_breaks`, configured duration, shot count, and configured hook, so a manually edited or malformed stamped plan can bypass replenish validation -> Add cfg-aware fatal validation in `produce_episode` before any Kie spend.
- [FIX] `_validate_batch` currently accepts any 2–6 shots and any valid Omni duration, so six mixed-duration shots can pass despite the required 6×10 format -> Under this opt-in format require exactly six shots and every duration exactly `"10"`.
- [FIX] `shot_plan` is only prompt advice plus a length check, so Gemini can ignore the exterior/interior phases while every proposed proof passes -> Deterministically prefix each normalized shot prompt with its canonical per-shot rule.
- [FIX] "Validate `shot_plan` at cfg-load time" assumes a validation layer that `SeriesMeta.auto_replenish` does not have -> Add one shared config validator checking non-empty strings, exact length, boolean chain fields, unique in-range breaks, and an in-range hook.
- [FIX] Removing the from-scratch slug fallback changes legacy prompt behavior when `hook_shot` is absent, violating the stated bit-identical opt-in contract -> Preserve the exact old slug branch when the key is absent and use the cfg value only when explicitly present.
- [FIX] `validate_plan` counts reference units before `produce_episode` prepends the chain image, so a seven-unit shot becomes an eight-unit Kie request only at execution -> Validate the final assembled Omni kwargs after the per-shot chain decision.
- [FIX] Default `chain_scope="series"` needlessly reads, logs, stores, and uploads a cross-episode frame that shot 1 is supposed to reject -> Set from-scratch explicitly to `chain_scope: "episode"`, the materially simpler isolation mechanism.
- [CLARIFY] Shot 4 deliberately breaks the only mechanical visual link between the finished exterior and its interior, leaving "the same structure" and USTA identity prompt-only -> Is two mechanically independent segments acceptable, or must a shared design reference bridge shots 3 and 4?
- [FIX] `python -m series.produce` has no CLI, while `series_runner --dry-run` returns success even when `produce_episode` fails or returns `None` -> Define one real proof command whose nonzero exit reflects doctrine, plan, and chain-trace failure.
- [FIX] Dry-run never synthesizes an uploaded last frame, so it cannot demonstrate the claimed `false,true,true,false,true,true` chain sequence -> Expose a pure chain-decision trace and test it through normal, idempotent-skip, and cross-episode-start branches.
- [FIX] The Rock 2 data migration makes existing installed-series assertions expecting from-scratch 4×8 and five families fail, although tests are omitted from Rock 2's file list -> Update those fixtures and run every direct test, not only the proposed three commands.
- [FIX] A golden generated from post-change code can pass while other channels' prompts drift -> Freeze pre-change `_build_prompt` outputs and normalized plans for every installed series lacking the new keys, and assert the new fields remain absent.
- [FIX] The pin instruction says "actual SHA-256," but runtime hashes LF-normalized text and the repository has no line-ending policy, so a raw Windows hash can fail on Linux CI -> Compute pins only with `series.bible.doctrine_sha256` and add an LF-versus-CRLF equivalence test.
- [FIX] `EPISODE_CREDIT_CAP=900` is below the doctrine's own 1,150-credit estimate and only limits reservation/QC rather than base-shot spending -> Give this workflow a conservative measured cap and enforce remaining budget before every paid generation or regeneration.
- [CLARIFY] Rock 3 spends no Kie credit, yet merge immediately sends the first unobserved pivot episode through `publish_mode=auto` -> Has Ihsan explicitly accepted skipping a non-publishing part-6 canary, or should auto resume only after that review?

VERDICT: NOT YET

### Visionary response (Fable)

- ACCEPTED (1, total_parts no-op): PLAN Rock 2.3 + KONSEPT §7: plans sil + total_parts 5;
  replenish 6-10 üretip 10'a taşır.
- ACCEPTED (2, eksik çekim yayını): opt-in `qc.require_all_shots: true`; PLAN Rock 1.3 + veri.
- ACCEPTED (3, bayat zincir sızıntısı): chain=false önce durumu sıfırlar; chain=true önceki
  kare yoksa FAIL-CLOSED; PLAN Rock 1.1.
- ACCEPTED (4, gereksiz upload): lookahead; yalnız sonraki çekim zincirliyse yükle; Rock 1.1.
- ACCEPTED (5, produce-tarafı doğrulama): kredi öncesi cfg-uyum doğrulaması; Rock 1.4.
- ACCEPTED (6, katı 6×10): chain_breaks'li cfg'de çekim sayısı ve süre TAM eşitlik; Rock 1.5.
- ACCEPTED (7, shot_plan zorlaması): normalize sırasında deterministik per-shot önek; Rock 1.5.
- ACCEPTED (8, cfg-yükleme doğrulayıcısı yok): paylaşılan config doğrulayıcı eklenir; Rock 1.5.
- ACCEPTED (9, slug fallback bit-değişmezliği): cfg yokken eski slug dalı AYNEN kalır; Rock 1.5.
- ACCEPTED (10, 7-birim kotası zincir sonrası): nihai kwargs üzerinde doğrulama; Rock 1.4.
- ACCEPTED (11, chain_scope): `chain_scope: "episode"` opt-in anahtarı; şot-1 chain=false
  ikinci emniyet olarak kalır; Rock 1.2 + veri.
- ANSWERED (12, şot 3→4 köprüsü): İKİ BAĞIMSIZ SEGMENT TASARIMDIR (cairo da içe kesiyor);
  köprüyü şot-4 kural öneki (dış malzeme/stil dili içeride sürer) + QC rubrik taşır;
  referans-görsel köprüsü ISSUES'a deney olarak eklendi.
- ACCEPTED (13, gerçek proof komutu): `chain_trace` CLI (ihlalde sıfır-dışı) + produce_episode
  doğrudan çağrı; runner exit-code'una güvenilmez; Rock 1.6 + Rock 3.
- ACCEPTED (14, dry-run zincir kanıtı): saf zincir-karar fonksiyonu + üç dal birim testi; Rock 1.7.
- ACCEPTED (15, mevcut fixture kırılması): Rock 2.6 fixture güncelleme + TÜM testler proof'ta.
- ACCEPTED (16, golden pre-change): golden'lar kod değişmeden ÖNCE dondurulur; Rock 1.0.
- ACCEPTED (17, SHA CRLF/LF): pin yalnız motorun hash fonksiyonuyla; eşdeğerlik testi; Rock 2.4.
- ACCEPTED (18, kredi tavanı): from-scratch koşusunda 1.400 (KONSEPT §4); diğer kanallar eski.
- ANSWERED (19, canary): İhsan'ın onay-dondurma kararı (2026-07-30, publish_mode=auto) sürer;
  merge+push zaten İhsan kapısı; push öncesi approval'a çevirme seçeneği final raporda
  açıkça sunulacak. Kayıt: USER GATE at push.

## Round 2

### Integrator findings (Codex, verbatim)

- [FIX] `chain_scope` is planned in root `series.json`, but current runner and producer read `bible.json["series"]["chain_scope"]` -> Put it in `bible.json.series` or explicitly update both consumers and include `series_runner.py` in Rock 1.
- [FIX] `require_all_shots` cannot distinguish QC pass from QC skip because `qc_shot` returns the clip for both, so failed Gemini/frame review can still auto-publish -> For this opt-in mode treat `skip` as failure and return an explicit QC status from `critic.py`.
- [FIX] The claimed shot-3→4 QC bridge is ineffective because critic reviews one clip at a time without the preceding boundary frame -> Add cross-shot boundary review or state clearly that continuity across the break is prompt-only.
- [FIX] Raising `EPISODE_CREDIT_CAP` to 1,400 still does not create a hard cap because base shots ignore it and regen checks current spend rather than projected spend -> Check remaining budget before every paid shot and regen, including the next call's estimated cost.
- [FIX] Rock 3 still lacks a machine-verifiable produce dry-run because successful and failed `produce_episode(..., dry_run=True)` calls both return `None` -> Add a real validation CLI or structured dry-run result with a nonzero failure exit.
- [FIX] "Shot count equals six" does not reject duplicate, missing, or out-of-order `n` values, which can reuse the same cached filename and repeat a clip while `require_all_shots` passes -> Require shot numbers to equal `[1,2,3,4,5,6]` exactly before spending.
- [FIX] The five canonical title patterns are checked only once in Rock 3, so later automatic replenish batches can violate 3.5 and still publish -> Add from-scratch opt-in title-pattern validation to `_validate_batch`.

VERDICT: NOT YET

### Visionary response (Fable)

- ACCEPTED (1, chain_scope yeri): anahtar bible.json `series` bloğuna taşındı (chain_frames'in
  yanı); `series_runner.py` Rock 1 dosya listesine eklendi. KONSEPT 7 + PLAN Rock 1.2/2.2.
- ACCEPTED (2, QC skip = pass): bu opt-in modda skip BAŞARISIZ sayılır; `critic.py` pass/skip/
  fail'i ayırt eden açık durum döndürür; diğer seriler etkilenmez. PLAN Rock 1.3.
- ACCEPTED (3, sınır köprüsü etkisiz): doktrin artık AÇIKÇA yazıyor: 3→4 sınırında süreklilik
  SALT-PROMPT'tur (şot-4 kural öneki taşır); cross-shot QC ISSUES'a eklendi.
- ACCEPTED (4, sert kredi tavanı): `credit_hard_cap: true` opt-in; her ücretli çağrıdan önce
  kalan bütçe SIRADAKİ çağrının tahmini maliyetiyle denetlenir; aşım = fail-closed. Rock 1.5.
- ACCEPTED (5, makine-doğrulanabilir kanıt): zincir izi CLI'ı tam PREFLIGHT aracına genişledi
  (SHA kapısı + cfg uyumu + zincir izi, ihlalde sıfır-dışı). Rock 1.7 + Rock 3.4.
- ACCEPTED (6, çekim numaraları): numaralar TAM [1..shots], tekrar/eksik/sıra bozukluğu RED;
  hem replenish doğrulayıcısında hem kredi-öncesi produce doğrulamasında. Rock 1.4/1.6.
- ACCEPTED (7, başlık kalıpları her koşuda): `title_patterns` opt-in regex listesi
  `_validate_batch`'e girer; uymayan batch fix-turuna reddedilir. Rock 1.6 + veri Rock 2.1.

## Round 3

### Integrator findings (Codex, verbatim)

Round-2'den chain-scope yerleşimi, QC skip davranışı, cross-shot kapsam kararı, preflight, kesin çekim numaraları ve sürekli başlık doğrulaması yeterince ele alınmış.

- [FIX] `credit_hard_cap` için 10 saniyelik Omni çağrısının tahmini maliyet kaynağı tanımlı değil ve ücretli Kie Suno çağrısı kredi döndürülmeden/loglanmadan bütçe dışında kalıyor -> Motor/süre bazlı muhafazakâr maliyet tablosu tanımla, bilinmeyen maliyette fail-closed davran ve Suno'yu da rezervasyon/harcama hesabına kat.
- [FIX] Rock 2 proof'u `credit_hard_cap=true` değerini kontrol ediyor fakat workflow'daki gerçek `EPISODE_CREDIT_CAP=1400` değerini doğrulamıyor -> Proof'a from-scratch workflow env değerinin tam 1400 olduğunu makineyle denetleyen assertion ekle.
- [FIX] Düz bir `title_patterns` regex listesi §3.5'in aile kısıtlarını uygulayamaz ve kısmi eşleşme fazladan metni kabul edebilir -> Kuralları `regex + allowed_families` olarak yapılandır, cfg yüklenirken derle ve başlıkları `fullmatch` ile doğrula.
- [FIX] Zorunlu teaser ve müzik katmanları hâlâ best-effort olduğu için tüm altı çekim geçse bile günlük koşu kancasız veya müziksiz videoyu otomatik yayınlayabilir -> From-scratch için zorunlu post-process katmanlarını fail-closed yapan opt-in bir teslimat kapısı ekle ve teaser/müzik hata testlerini proof'a kat.

VERDICT: NOT YET

### Visionary response (Fable)

- ACCEPTED (1, maliyet tahmini kaynağı): KONSEPT §7 artık tek yerde tanımlı, motor+süre bazlı
  MUHAFAZAKÂR maliyet tablosunu şart koşuyor; tabloda olmayan çağrı türü = fail-closed;
  ücretli müzik (Suno/Kie) muhasebeye dahil, kredi dönmese bile tahmin harcanmış sayılır.
  PLAN Rock 1.5 + test (bilinmeyen maliyet + müzik muhasebesi).
- ACCEPTED (2, workflow env doğrulaması): Rock 2 PROOF'una from-scratch.yml içindeki
  EPISODE_CREDIT_CAP değerinin TAM "1400" olduğunu denetleyen assertion eklendi.
- ACCEPTED (3, title_patterns yapısı): düz regex listesi bırakıldı; kurallar
  `{regex, families}`, cfg yüklenirken DERLENİR, başlık FULLMATCH eder ve bölümün family'si
  kuralın izinli ailelerinde olmalı (kalıp 3 yalnız dönüşüm; kalıp 4 dönüşüm + geri dönüşüm).
  KONSEPT §7 (e/f) + PLAN Rock 1.7 / 2.1.
- ACCEPTED (4, teslimat kapısı): bible series bloğuna `required_layers:
  ["hook_teaser","music"]` (opt-in); katman üretilemezse bölüm fail-closed durur ve
  yayınlanmaz. Bugünkü davranış (`produce.py` kancayı yutup "video kancasız yayınlanır")
  bu kanalda kusurlu teslimat sayılıyor. PLAN Rock 1.6 + test.

## Round 4

### Integrator findings (Codex, verbatim)

Round-3'teki dört bulgu tasarım düzeyinde ele alınmış.

- [FIX] Rock 2 yalnız `required_layers` alanının okunabildiğini, Rock 1 ise yalnız teaser hata yolunu kanıtlıyor; dolayısıyla `music` kapısı eksik veya yanlış bağlanmışken tüm proof'lar geçebilir -> Listeyi tam olarak `["hook_teaser","music"]` diye assert et ve her katmanın başarısızlığını ayrı testte yayın-engelleyici olarak doğrula.
- [FIX] Kredi proof'u bilinmeyen maliyet ve müzik muhasebesini söylüyor fakat ana Omni çekimi ile QC regen çağrılarının sert tavana gerçekten bağlandığını ayrı ayrı kanıtlamıyor -> Ana çekim, regen ve Suno yollarının her biri için sınır-altı/sınır-aşımı testleri ekle.
- [FIX] Prompt golden'ları yeni çalışma-zamanı kapılarının anahtarsız serilerde davranış-nötr kaldığını kanıtlamaz -> `credit_hard_cap` ve `required_layers` yokken eski fail-open kredi/post-process davranışının korunduğunu doğrudan regresyon testleriyle göster.

VERDICT: NOT YET

### Visionary response (Fable)

- ACCEPTED (1, katman katman kanıt): Rock 2 PROOF artık `required_layers` için VARLIK değil
  TAM EŞİTLİK (`["hook_teaser","music"]`) assert ediyor; Rock 1.9 kanıt matrisinde teaser ve
  music için AYRI yayın-engelleme testleri var.
- ACCEPTED (2, kredi yolları ayrı ayrı): kanıt matrisi (a) ana Omni çekimi, (b) QC regen,
  (c) ücretli müzik için sınır-altı GEÇER + sınır-aşımı ENGELLER testlerini ayrı ayrı şart
  koşuyor; tabloda olmayan çağrı türü = fail-closed testi ayrıca duruyor.
- ACCEPTED (3, çalışma-zamanı davranış nötrlüğü): golden'a ek olarak doğrudan regresyon
  testleri: `credit_hard_cap` yokken eski fail-open kredi davranışı, `required_layers` yokken
  teaser/müzik hatasına rağmen yayın (bugünkü davranış) korunur.

## Round 5 (final)

### Integrator findings (Codex, verbatim)

Round-4 bulgularının tamamı kapatılmış. Kayalar uygulanabilir, proof matrisi yanlış pozitif boşlukları kapatıyor ve anahtarsız serilerin davranış-nötrlüğü doğrudan test ediliyor. Yeni blocker yok.

VERDICT: SAME PAGE

### Visionary response (Fable)

Toplantı kapandı. Bulgu seyri: 19 → 7 → 4 → 3 → 0. Hiçbir bulgu sessizce düşürülmedi;
iki CLARIFY yanıtlandı (3→4 sınırı salt-prompt kabul; canary yerine push kapısı), gerisi
KABUL edilip PLAN rev.4 + KONSEPT v2.0 §7'ye yazıldı. İnşaat Rock 1'den başlar.
