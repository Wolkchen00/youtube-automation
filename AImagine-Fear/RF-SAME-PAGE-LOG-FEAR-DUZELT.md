# RF-SAME-PAGE-LOG-FEAR-DUZELT

Plan: `RF-PLAN-FEAR-DUZELT.md` | Dal: `codex-fear-duzelt` | Codex modeli: gpt-5.6-sol (effort: high)
Thread: 01a08bd3-896b-73f2-ae38-7bd6c3e26c18

## Round 1

### Integrator bulgulari (Codex, AYNEN)

```
- [FIX] Metadata gates can pass an unrelated 1080x1920/30fps clip with audio, so the plan never proves the generated video matches the visual or temporal canon -> Add a semantic frame/audio acceptance gate or make the first live generation stop for human approval before publishing.
- [FIX] `PROFIL` is not actually single-source while `canon/MASTER-BLOCK.md` still hardcodes 1080x1920/30fps and `kie_uret.py` defaults to 720p -> Render prompt, API arguments, and audit expectations from one machine-readable profile or enforce an explicit consistency test across all three.
- [FIX] Flattening ffprobe output into one dictionary can let the audio stream’s `r_frame_rate=0/0` overwrite the video rate and cannot reliably represent multiple streams -> Request ffprobe JSON, select the video stream explicitly, and check that any audio stream exists.
- [FIX] The proposed pure-function proofs can pass even if `main()` retains its old inline command or `denetle()` never calls `denetle_alanlar()` correctly -> Add wiring tests that mock subprocess execution and assert the exact production command and parsed probe structure passed by the real wrappers.
- [FIX] A plain `import build` from `tools/gunluk.py` is not portable because script execution puts `AImagine-Fear/tools`, not `AImagine-Fear`, on `sys.path` -> Insert resolved `KOK` before import and test invocation from repo root and an unrelated cwd on Windows and CI; there is no inherent import cycle.
- [FIX] `parse_sections()` cannot read `DURATION` because route fields occur before the first section -> Use `load_route()` with absolute paths or extract one shared field parser instead of duplicating the format.
- [CLARIFY] Rock 2 and Rock 5 intend to run 20/25-second routes through `bytedance/seedance-2` despite `vegas-strat-blue-rain-15.md` documenting a 15-second model ceiling -> Has that model’s acceptance of 20 and 25 seconds been verified, and if not should unsupported routes remain outside `SIRA`?
- [FIX] Positive fractional durations pass the proposed validation but `kie_uret.py` converts Seedance duration with `int(args.n_frames)`, causing generation and audit expectations to disagree -> Restrict each model to a positive integer duration allowlist before spending credits.
- [FIX] Mastering after the structural gate does not inherently disable SHA because `yayinla.py` hashes the master, but it makes the audited and published artifacts different and `core/uploader.py` may create a third unaudited delivery transcode above 80 MB -> Produce the final delivery first, prevent or anticipate `_delivery_copy`, then run every gate and SHA against the exact upload artifact.
- [CLARIFY] `master_yolu` is unspecified, so a name matching `*_gunluk_*.mp4` could be selected later as raw generation and normalized repeatedly -> Will masters live in a separate directory or use a pattern excluded from raw-video discovery?
- [FIX] Rock 3’s required ffmpeg test may be skipped and still return a green pytest result -> Make ffmpeg mandatory in the CI proof and add non-ffmpeg failure/wiring tests so local skips cannot constitute acceptance.
- [FIX] Rock 3 performs another full loudness analysis even though `master_audio()` already measures, enforces, and writes the delivered values to `.audio_master.json` -> Read the final recorded attempt from that sidecar for the ledger instead of running a redundant measurement.
- [FIX] After every TITLE variant is used, selecting the oldest one still triggers `upload_to_platform()`’s duplicate-title return at lines 475-488, so YouTube is skipped -> Pass an explicit intentional-reuse flag only for exhausted pools or generate a genuinely unique title, and test the actual uploader call.
- [FIX] `yayinla.py` treats any one platform success as overall success, while its SHA/day guards block whole-run retries, so YouTube-success/Instagram-failure and the reverse both leave unrecoverable or duplicate platform state -> Record success per platform, retry only missing platforms, and define rotation/title use from successful YouTube publication rather than aggregate exit status.
- [FIX] Moving `slug` directly into every `yayinla.py` record makes a completely failed attempt advance `sirdaki()` because `yayinla.py` writes the ledger before returning failure and `sirdaki()` checks only slug presence -> Ship the writer change with success-aware rotation and same-day guards.
- [FIX] The TITLE “meaningful first 40 characters” rule has no defined landmark normalization or emotion vocabulary, and its proof omits both positive and negative hook cases -> Replace it with a deterministic hook grammar and test boundary, missing-hook, and word-split cases.
- [FIX] Seeing tags in `yayinla.py --dry` proves only logging, not that YouTube receives them -> Mock `upload_to_platform()` and assert the exact comma-separated `tags` value on the YouTube call.
- [FIX] The required TITLE/PALET schema bullets precede migration and omit `_TEMPLATE.md`, `tools/sehir_ekle.py`, README instructions, and test fixtures, leaving `build.py --check` red midway and future generated routes invalid -> Add new data to all routes and producers first, then activate validation/output, or ship the complete migration atomically.
- [KILL] Rock 5’s palette labeling, extra recolored route, and A/B rotation are a confounded growth experiment rather than work required for canon fidelity or YouTube hook/tag/#shorts delivery -> Remove Rock 5 from this plan and track the experiment separately with a sidecar manifest if it is pursued later.
- [FIX] Rock 5’s linear “no three equal palettes” proof can pass while cyclic `SIRA` crosses its end/start boundary with three neon routes, and a 7-neon/3-warm cycle cannot satisfy that constraint everywhere -> If retained elsewhere, test cyclic adjacency and rebalance the sample counts instead of claiming alternation.
- [FIX] The closing `gunluk.py --dry` command can exit zero at the same-day guard before printing duration/profile/palette, so its stated proof can pass while planning output is absent -> Make dry mode deterministic and offline after build validation, and assert its required fields in a test.
- [FIX] The atomicity statement is incomplete because post-master transform plus final-artifact audit/SHA and platform-aware TITLE selection plus retry ledger semantics also require safe ordering, while schema migrations require data-first ordering or one atomic change -> Add these deployment dependencies explicitly beside the Rock 1 resolution/gate constraint.
VERDICT: NOT YET```

### Visionary yaniti (Claude)

Bagimsiz dogrulama: `git status --porcelain` bos , read-only tur hicbir dosyaya dokunmadi.

**Bu depoda ELLE DOGRULADIGIM uc bulgu (kabul, plani maddi olarak degistirdi):**

- ACCEPTED , ffprobe duz sozluk, ses akisi fps'i eziyor -> Canli `ffprobe` kosusuyla
  dogrulandi: gercek bir yayinlanmis videoda `video r_frame_rate=24/1` sonrasinda
  `audio r_frame_rate=0/0` geliyor ve `dict(re.findall(...))` ikincisini aliyor.
  Yazilacak fps kapisi HER videoda yanlis kalirdi. Rock 1 artik ffprobe JSON okuyup
  video akisini acikca seciyor; fixture testi bu ezmeyi yakaliyor.
- ACCEPTED (ama gerekcesi DUZELTILDI) , Codex'in CLARIFY'i "20/25 saniye bu modelde
  dogrulandi mi?" diye sordu. Ilk yanitim YANLISTI: `routes/vegas-strat-blue-rain-15.md:10`
  "bytedance/seedance-2 tavani 15 saniye" diyor diye "evet, tavan 15" dedim.
  **O not guvenilmez.** Dogrulama:
  ```
  core/kie_api.py:481   resolution: str = "720p"
  core/kie_api.py:483   model: str = "bytedance/seedance-2-fast"    <- FAST
  core/kie_api.py:489   "Seedance duration is an integer 4-15s; resolution 480p/720p"
  AImagine-Fear/tools/gunluk.py:30   MODEL = "bytedance/seedance-2" <- FAST DEGIL
  ```
  Yani o sinirlar `seedance-2-fast`'e ait; bu kanalin cagirdigi modelin sinirlari
  depoda hicbir yerde YAZILI DEGIL. Codex'in sorusu hakliymis, benim cevabim yanlisti.
  Rock 2 buna gore yeniden yazildi: izin listesi `{15}` ve yaninda "DOGRULANMADI"
  yorumu; 20/25 saniyelik uc rota havuzdan cikiyor ama sebep "tavan" degil
  "dogrulanmamis". Rota dosyalari silinmez, kanarya sonrasi kume tek satirla genisler.
  Ayni belirsizlik cozunurluk icin de gecerli oldugundan Rock 1'e `--profil` bayragi ve
  "sessiz dusurme" tespiti eklendi.
- ACCEPTED , `yayinla.py` basarisiz donmeden once deftere yaziyor -> Kod okundu,
  dogru. `slug`'i o kayda tasimak tam basarisiz yayinda bile donusumu ilerletirdi.
  Rock 4/5 artik "kullanildi" bayragini cikis kodundan degil YouTube sonucundan
  turetiyor.

**Kabul edilen digerleri:**

- ACCEPTED , `parse_sections` DURATION'i goremez (alanlar ilk `## `'den once) ->
  Rock 2 acikca `build.load_route()` kullaniyor.
- ACCEPTED , `import build` tasinabilir degil (betik `tools/`'u sys.path'e koyuyor) ->
  Rock 2'ye `KOK` ekleme + iki farkli cwd'den import testi.
- ACCEPTED , kesirli sure `int()` ile bozuluyor (`kie_uret.py`) -> tamsayi izin listesi.
- ACCEPTED , saf fonksiyon testi `main()` eski satiri saklarsa gecer -> her rock icin
  zorunlu *baglanti testi* (subprocess/uploader mock, TAM argv dogrulanir) genel kural
  olarak plana girdi.
- ACCEPTED , master'lama kapidan sonra gelirse denetlenen dosya yayinlanan dosya degil,
  ustelik 80 MB ustu `_delivery_copy` ucuncu bir transcode uretiyor -> sira
  "uret -> master'la -> denetle -> yayinla" olarak degisti; 80 MB kapisi eklendi
  (`core/uploader.py:36` `MAX_UPLOAD_MB = 80` dogrulandi).
- ACCEPTED , master `*_gunluk_*.mp4` glob'una yakalanip tekrar tekrar normalize
  edilebilir -> master `out/<slug>/master/` altina, glob disina.
- ACCEPTED , `master_audio` zaten olcuyor ve `.audio_master.json` yaziyor, ikinci olcum
  gereksiz -> defter sidecar'dan okuyor.
- ACCEPTED , ffmpeg testi `skip` olup yesil gorunebilir -> kapanis kaniti once
  `ffmpeg -version` dogruluyor, `skip` kanit sayilmiyor.
- ACCEPTED , TITLE havuzu tukendiginde eskiyi secmek yine mukerrer baslik kapisina
  carpiyor -> havuz tukenince YAYIN DURUYOR; `allow_duplicate_title` hic kullanilmiyor.
- ACCEPTED , "anlamli ilk 40 karakter" yoruma acik -> belirlenimci dilbilgisi
  (landmark ayirt edici kelimesi + kelime ortasinda kesilmeme) ve iki yonlu testler.
- ACCEPTED , `--dry` ciktisi etiketleri gordu diye YouTube aldi demek degil ->
  `upload_to_platform` mock'lanip TAM `tags` dizesi dogrulaniyor.
- ACCEPTED , sema gocu once dogrulamayi acarsa `build.py --check` arada kirmizi kalir;
  `_TEMPLATE.md`, `tools/sehir_ekle.py`, fixture'lar unutulmus -> "tek commit'te tam
  goc" genel kural oldu; `sehir_ekle.py:85-89` sablonu goce dahil.
- ACCEPTED , teknik kapi kanona ICERIK uyumunu kanitlamaz -> Rock 1b eklendi:
  `--yayinlama` (uret + denetle + kontakt sayfasi, yayinlama) ve `--dry` cevrimdisi
  ve belirlenimci hale geldi. Otomatik goruntu siniflandirmasi issue'ya dustu.
- ACCEPTED , `--dry` ayni-gun kapisinda erken 0 ile cikabiliyor -> `--dry` artik o
  kapidan once calisiyor ve alanlari her zaman basiyor.
- ACCEPTED , atomiklik ifadesi eksik -> "ayni commit'te gitmesi gerekenler" uc cift
  olarak yazildi (cozunurluk/kapi, master/denetim, sema/dogrulama).
- ACCEPTED , `PROFIL` tek kaynak degil cunku `canon/MASTER-BLOCK.md` sayilari sabit
  yaziyor -> kanon tutarlilik testi eklendi. `kie_uret.py` varsayilani DEGISMIYOR
  (dort kanalla ortak); bunun yerine `gunluk.py`'nin `--resolution`'i her zaman acikca
  gecirdigi test ediliyor.

**Kismen kabul:**

- PARTIAL , platform basina basari/yeniden deneme semantigi bozuk -> Donusumun yalniz
  YouTube basarisinda ilerlemesi KABUL ve Rock 4'te. Eksik platformlari tek tek yeniden
  deneme mekanizmasi bu kosugun kapsami disinda, `RF-ISSUES-FEAR-DUZELT.md`'ye dustu:
  gercek bir davranis degisikligi ve dort kanalin ortak yukleyicisine yakin.

**Reddedilen:**

- REJECTED , [KILL] Rock 5 (palet) Core Focus'a girmiyor -> Ihsan bu kosuda acikca
  istedi ("kod tarafini kur, uretimi ben tetiklerim"), yani bu Visionary'nin degil
  Owner'in karari. Core Focus paletin OLCULEBILIR kalmasini icerecek sekilde
  genisletildi. Codex'in teknik itirazlari yine de kabul edildi: yeni rota UYDURULMUYOR
  ve yanlis donusum iddiasi birakildi (asagi).
- ACCEPTED (ayni bulgunun teknik yarisi) , "ust uste uc ayni palet yok" iddiasi
  2 sicak / 7 neon ile dairesel olarak SAGLANAMAZ -> iddia plandan cikarildi, yerine
  gercekten dogru olan sey test ediliyor: sicak rotalar arasindaki neon dizisi
  uzunluklari en fazla 1 farkli. Ucuncu sicak rota (yeniden boyanmis Sanghay) plandan
  CIKARILDI ve issue'ya dustu , Codex hakli, kanon metnini toplu renk degistirerek
  yeniden yazmak Codex'in isi degil.

**Cevaplanan CLARIFY'lar:**

- Seedance 20/25 sn destegi dogrulandi mi? -> HAYIR, tavan 15 ve depoda yazili. Rotalar
  havuzdan cikti.
- `master_yolu` neresi? -> `out/<slug>/master/`, ham video glob'unun disinda.
