# RF-PLAN-WILD-ENCOUNTER (Clarity Break, 2026-09-11)

Kanal: sentinal_ihsan. Seri: `sentinal_ihsan/wild-encounter` (format `plato-3x8`,
sahte kamera arkasi). Bu plan Ihsan'in 11 Eylul'de sectigi dort isi kapsar.

## Core Focus

wild-encounter'in her bolumu, muziksiz diegetik sesle -14 LUFS'te, formatla
celismeyen prompt ve QC metinleriyle, bolum ici tutarli yaratik ve setle
uretilebilsin; test takimi bunu yesil kanitlasin.

## Durum (olculdu, tahmin degil)

- ep05 "This GIANT OCTOPUS Is NOT Real" 11 Eylul 02:52 PDT'de YT/IG/TikTok'ta
  yayinda. 7. saatte YT 1.384 izlenme (eski konseptin tavani ~1,5K), TikTok 94.
- Ihsan kararlari: (a) muzik yatagi KALKAR, diegetik ortam sesi KALIR ve
  kisilmez (ep06'dan itibaren); (b) giris AGIZDAN, cikis ekibin elleriyle
  (part06); (c) yaratik tutarliligi karakter kaydiyla.
- Test takimi bu worktree'de (HEAD e004e2e): 49 failed + 11 error, 1357 passed.
  60'inin HEPSI 10 Eylul arsivlemesinden: testler canli
  `sentinal_ihsan/unnatural-lab/*`, `series_data/unnatural-lab/*`,
  `sentinal_ihsan/KONSEPT.md` okuyor ya da "en az 8 kurulu seri" bekliyor.
  Arsiv oncesi agac: commit `4c3f392`.
- `bible.art_style` HER cekim promptunun basina ekleniyor (`series/shots.py:369`
  omni, `:409` diger motorlar) ve hala "real outdoor location, handheld,
  hybrid creature" diyor. Format ise stüdyo seti, sabit kamera, prop.
- `bible.series.qc.notes` cekim vuruslarini tarif ediyor ve 3. vurusu
  "govdedeki KAPAK acilir" diye yaziyor; part06 agizdan cikis kullaniyor.
  11 Eylul'de ayni sinif hata (kural degisti, QC notu bayat kaldi) uc kez
  dogru videoyu reddetti, 483 kredi.
- `produce.py:640` muzigi `bible.music` ile aciyor; `produce.py:2186-2231`
  mastering'i `master_lufs` ile, muzikten BAGIMSIZ calistiriyor. Yani
  `music: false` + `master_lufs: -14` = muziksiz govde -14'e masterlanir.
  ep05 muziksiz govde `ep05.mp4` -17,6 LUFS olculdu.
- `ensure_episode_refs` (`produce.py:1077`) yalniz `tek-obje-4x6` icin obje +
  ortam referansi uretiyor (kredi kapisi, hash ile bayatlik, atomik yazim var).
  Omni payload'u ortam referansini (`role: environment`) ve `prop_ref_urls`'u
  (`role: object`) zaten kullaniyor (`shots.py:260-320`).
  `ensure_character_registration` (`produce.py:1252`) `character_id` varsa hic
  dokunmuyor; Ihsan'in yuz capasi `92369a8131e7497abf00c3b5ba1c92c9`.

## Rocks (bagimlilik sirasinda)

### ROCK 1: Test takimini arsivden kurtar

Yapilacak: arsivleme yuzunden kirilan 60 testi, canli kanal yapilandirmasi
yerine DONDURULMUS fixture'dan okuyacak hale getir.

- Fixture kaynagi: `git show 4c3f392:<yol>` ile bayt-bayt ayni kopya, hedef
  `tests/fixtures/archived/<orijinal goreli yol>` (or.
  `tests/fixtures/archived/sentinal_ihsan/unnatural-lab/bible.json`).
  Yalniz testlerin gercekten okudugu dosyalar kopyalanir.
- Testler tek bir yardimci uzerinden fixture kokunu bulur
  (or. `tests/_archived_fixture.py`). `series_data/<slug>` ya da `Bible.load`
  yoluyla okuyan testler icin mevcut bir enjeksiyon noktasi (monkeypatch ile
  kok dizin) kullanilir.
- IKI SINIF TEST VAR, ayri ele alinir (SPM tur 1):
  (a) BELIRLI bir arsiv serisini sabitleyen testler (unnatural-lab
      config/plan/doktrin, KONSEPT.md): dondurulmus fixture'a gecer.
  (b) FILO testleri (kurulu TUM serileri tarayip izolasyon / salt-okunur /
      "baska seri X kazanmadi" gibi degismezleri denetleyenler): CANLI serileri
      taramaya DEVAM eder. Yalniz arsivin kirdigi sey duzeltilir (sabit slug
      listesi, sabit sayi esigi). Fixture'a cevirmek canli filodaki gelecek
      bozulmayi gizler, yasak.
- Sayi esigi ("kurulu seri >= 8"): sabit sayi yerine, yardimcinin buldugu
  liste ile BAGIMSIZ bir dosya sistemi taramasinin (series.json tasiyan canli
  seri dizinleri) ESITLIGI assert edilir, arti bos-olmama korumasi. Bu
  eskisinden guclu; gerekceyi raporla.
- Hicbir assert gevsetilmez, test mantigi degismez; degisen yalniz verinin
  kaynagi.
- ROCK 1 uretim koduna (`series/`, `core/`) DOKUNMAZ. Enjeksiyon noktasi yoksa
  ve uretim kodu degismeden olmuyorsa: `BLOCKED: <fonksiyon ve sebep>`.
- Test kirliligi: tam takim kosusu git'te izlenen
  `series_data/advers/hold_log.jsonl` dosyasina 8 satir ekliyor (olculdu,
  bu worktree'de). Testler izlenen hicbir dosyaya yazmamali: test altyapisinda
  (or. conftest autouse fixture ile yolu tmp'ye yonlendirerek) duzelt; uretim
  koduna dokunmadan olmuyorsa BLOCKED.
- Done: tam takim yesil ve kosu agaci kirletmiyor.
- PROOF: `python -m pytest -q -p no:cacheprovider` -> `0 failed`, `0 error`;
  kosudan SONRA `git status --porcelain` yalniz senin bu rockta ekledigin /
  degistirdigin dosyalari gosterir (izlenen baska dosya degismez);
  ve `git diff --stat -- series core` bos.

### ROCK 2: Muzik yatagi kapali, muziksiz govde masterlanir

- `sentinal_ihsan/wild-encounter/bible.json`: `"music": false`.
- `sentinal_ihsan/wild-encounter/series.json`: `auto_replenish.music_prompt`
  -> `false`; `music_style` anahtari kaldirilir.
- `sentinal_ihsan/wild-encounter/plans/part06.json`: `"music"` alani kaldirilir.
- Dogrula: `validate_replenish_config(cfg)` bu degisiklikle `[]` donuyor; muzik
  alani olmayan plan `validate_plan_against_config`'ten geciyor.
- Motor davranisini sabitleyen GENEL regresyon testi (canli config OKUMAZ,
  sentetik bible ile): `music` False ve `master_lufs` = -14 iken
  (a) `generate_background_music` hic cagrilmaz, (b) `master_audio` muziksiz
  govde yoluyla cagrilir, (c) `"music"` `required_layers` icinde degilse bolum
  muzik yok diye dusmez. En kucuk dikisi (seam) sen sec, sebebini yaz.
- Modelin KENDI urettigi muzik (SPM tur 1, Q1/Q2): `native_audio_review`
  `unwanted_music=true` gorunce cekimi reddediyor. Bunu kilitleyen mevcut testi
  bul ve adini raporla; yoksa sentetik config'le motor duzeyi bir test ekle
  (canli config okuyan test YAZILMAZ).
- Done: ep06 muziksiz, mastering'li cikacak sekilde yapilandirildi ve test
  bunu kilitliyor.
- PROOF: `python -m pytest -q -p no:cacheprovider` -> 0 failed / 0 error; ve
  yeni test dosyasi tek basina yesil.
- Visionary kaniti (Codex degil, ben kosarim; ep05.mp4 worktree disinda):
  ana agactaki `output/series/wild-encounter/episodes/ep05/ep05.mp4` uzerinde
  `ffmpeg_tools.master_audio(..., target_i=-14, target_tp=-1.0, target_lra=11,
  true_peak_margin_db=<bible degeri>)` -> `ep05_ambient_mastered.mp4`;
  olcum -14 +/- 1 LU ve true peak <= -1,0 dBTP; `_verify_audio_master` True.

### ROCK 3: Format hijyeni, modelin ve QC'nin okudugu her metin ayni formati anlatir

Tek kaynak ilkesi (SPM tur 1 ile daraltildi): QC'nin olcut aldigi vurus
TANIMI yalniz `series.json auto_replenish.shot_plan`'dadir. Her cekim promptu
o metinle baslar (`validate_plan_against_config` zorluyor); QC'ye giden
birlesik prompt `art_style` ile basladigi icin QC notu "SHOT N, ile baslayan
paragrafa" bakar, "ilk paragraf" demez. logline, synopsis ve cekim govdesi
vurusu anlatabilir; ama QC notu ve art_style giris/cikis MEKANIZMASI (kapak,
agiz vb.) tasimaz. Boylece mekanizma degisince QC notu bayat kalamaz.

Degisecek alanlar, hedef metinler EK A'da harfi harfine:

1. `bible.json` `art_style` -> EK A.1.
2. `bible.json` `series.qc.notes` -> EK A.2.
3. `series.json` `auto_replenish.shot_plan` -> EK A.3 (uc satir).
4. `part06.json` her cekim promptunun ILK paragrafi (ilk `\n\n`'e kadar) EK A.3
   ile degistirilir; govde metni aynen kalir.
5. `series.json`: `logline`, `hashtags`, `title_patterns`, `title_style`,
   `brief` -> EK A.4. `families` DEGISMEZ.
6. `bible.json` `series` altindaki bayat notlar: `format_note`, `chain_note`,
   `object_match_note`, `first_frame_note`, `continuity_note` -> EK A.5.
   `duration_note` ve `credit_cap_note` aynen kalir.
7. `bible.json` `characters[ihsan_field].bio` -> EK A.6.
   `appearance`, `ref_image_url`, `character_id`, `voice` DOKUNULMAZ
   (yuz capasi; Ihsan "yuz cok iyi" dedi).
8. `DOKTRIN.md`: baslik blogundan hemen sonra EK A.7'deki "GUNCEL FORMAT"
   bolumu eklenir. Eski "Tek cumle", "Degismez kurallar", "Neye DOKUNMA"
   bolum basliklarinin sonuna " (ESKI FORMAT, 10 Eylul, artik gecerli degil)"
   eklenir; iceriklerine ve olculmus ders bolumlerine dokunulmaz.
- Dogrula: `plans/` altindaki eski planlari (part02-05) toplu dogrulayan bir
  surec var mi? Varsa yeni shot_plan onlari kirar mi? Rapor et.
- Done: part06 yeni config'e karsi hatasiz dogrulaniyor; canli config'te bayat
  ifade kalmadi; dry-run cekim 1 promptu yeni art_style ile basliyor.
- PROOF:
  1. `python -m series.cli produce wild-encounter sentinal_ihsan/wild-encounter/plans/part06.json --dry-run`
     cikti: dogrulama hatasi yok, uc cekim, cekim 1 prompt'u EK A.1 ile basliyor.
     (Dry-run post-process'e ulasmaz; muzik/master kaniti ROCK 2'dedir.)
  2. `python -c` betigi: `validate_replenish_config(cfg) == []` ve
     `validate_plan_against_config(part06, cfg) == []`.
  3. Bayatlik taramasi, yalniz `bible.json` + `series.json` + `part06.json`:
     `kisik muzik`, `music bed`, `real outdoor location`, `hatch`, `both shots`,
     `hybrid`, `16 saniye`, `2 x 8` -> sifir eslesme (buyuk/kucuk harf duyarsiz).
  4. Tam takim: 0 failed / 0 error.

### ROCK 4: Yaratik ve set capasi, yalniz referans gorselle (plato-3x8, opt-in)

Amac: her bolumun yaratigi uc cekim boyunca AYNI kalsin, set zengin ve sabit
olsun. SPM tur 1 karari: karakter KAYDI (register_character) bu tur uretime
BAGLANMAZ. Kie'nin insan olmayan ozneyi kabul ettigi kanitlanmadi, ucreti
bilinmiyor, idempotency yok. Tek-obje formatinda calisan, testli referans
gorsel yolu kullanilir; kayit olculmus bir deneye ertelendi (RF-ISSUES).

- Opt-in bayrak: `bible.series.episode_anchors: true`. Yalniz wild-encounter
  acar. Bayrak kapaliyken her format icin davranis birebir eskisi
  (`tek-obje-4x6` yolu dahil, payload baytlari degismez).
- Bayrak acik ve `plan.format_version == "plato-3x8"` iken, mevcut
  `ensure_episode_refs` cagri noktasinda (ya da yanindaki kardes fonksiyonda):
  1. ORTAM: `environments[object_card.environment].ref_image_url` yoksa film
     seti prompt'uyla (EK B.1) uret, yukle, yuklemeden HEMEN SONRA
     `bible.json`'a atomik yaz. `tek-obje` yolundaki "room and surface ...
     plain wall ... daylight" prompt'u bu formatta KULLANILMAZ.
  2. YARATIK: `object_card.name` + `descriptor` + ortam tarifinden (EK B.2;
     `anomaly_descriptor` KULLANILMAZ, yaratik referansta canli gorunmeli)
     uret, yukle, yuklemeden HEMEN SONRA plana atomik yaz:
     `plan["prop_ref_urls"] = [url]` (TEK kanonik alan; mevcut `role: object`
     baglamasi bunu okur) ve `plan["ref_prompt_sha256"]`. Hash, plato
     sablonunun kendi surum etiketiyle hesaplanir; ad/descriptor/ortam tarifi
     ya da sablon degisirse yeniden uretilir.
  3. PAYLOAD degismez: mevcut `resolve_shot` sirasi chain / object /
     environment, Ihsan `character_ids` icinde. Omni referans birim siniri (7)
     preflight'ta zaten denetleniyor; part06 icin sinirin altinda kaldigini
     test et.
- Para kurallari (hepsi zorunlu):
  - Her ucretli cagridan ONCE `hard_cap.authorize`, SONRA
    `_record_episode_cost`; mevcut `_generate_uploaded_reference` yeniden
    kullanilir.
  - Gorsel uretimi basarisizsa fonksiyon False doner, bolum video kredisi
    harcamadan durur (mevcut davranis). Otomatik yeniden deneme yok.
  - Tekrar kosu sifir ucretli cagri yapar (idempotent).
- `object_card.anomaly_descriptor` ROCK B anomaly_match metrigini ister ama
  kapi yalniz `qc.enforce.anomaly_match` ile acilir (SPM tur 1, Q3);
  wild-encounter'da `enforce` yok. Bu durumun degismedigini test et.
- `require_object_match` KAPALI kalir (ep06 olculmeden yeni QC kapisi yok).
- DOKTRIN.md GUNCEL FORMAT kurallarina 12. madde eklenir (EK A.7 sonu).
- Done: ep06 dry-run'i capalarin hazirlanacagini gosteriyor; payload rol
  sirasi dogru; para yollari testli.
- PROOF:
  1. Yeni test dosyasi (Kie tamamen mock'lu, SIFIR ag): bayrak kapali ->
     cagri yok ve payload baytlari degismez (tek-obje ve plato); bayrak acik +
     bos durum -> tam bir ortam gorseli ve bir yaratik gorseli, her biri
     yuklemeden hemen sonra diske yazilmis; ikinci kosu -> sifir cagri;
     descriptor degisti -> yalniz yaratik yeniden uretilir; ortam gorseli
     yazildiktan sonra yaratik uretimi coker -> tekrar kosu ortami YENIDEN
     URETMEZ; gorsel hatasi -> False; kredi kapisi reddeder -> ucretli cagri
     yok; `resolve_shot` part06 cekim 1 icin roller object/environment ve
     cekim 2 icin chain/object/environment, Ihsan'in kimligi `character_ids`
     icinde.
  2. `python -m series.cli produce wild-encounter sentinal_ihsan/wild-encounter/plans/part06.json --dry-run`
     capalarin hazirlanacagini soyler, ucretli cagri yapmaz.
  3. Tam takim: 0 failed / 0 error.

### ROCK 5: wild-encounter gunluk otomasyona baglanir (Ihsan istegi, 11 Eylul ~11:50 PDT)

Ihsan: "sonraki videolar bu otomasyonda oldugundan emin ol"; karar: GUNLUK,
OTOMATIK YAYIN. Visionary insa etti (Codex kotada), Codex 2:35 PM'de inceler.

Olculen engeller (canli yapilandirmayla ikmal probu, 11 Eylul 11:54 PDT):
- 6 Gemini denemesinin 6'si da reddedildi: `_validate_batch` formatli her seride
  sureyi sabit "6" bekliyordu (tek-obje kalintisi), plato 8 sn.
- Baslik kalibi iki buyuk harfli kelimeyle sinirliydi ("GIANT PRAYING MANTIS" dustu).
- Formatli seriler icin yazilan obje kurali "anomaliyi her cekime kopyala, cekim 1'de
  en uc haliyle goster" diyordu: plato'da ifsa cekim 1'de harcanirdi.
- Aileler melez donemin adlariydi (wrong-skin, wrong-head): Gemini "tuylu yilan" yazdi.
- Yuz capasi (ihsan_field) planlara garanti girmiyordu.
- Seri draft, parts bos, next_part 1: ep05/ep06 kayit disiydi (mukerrer riski).

Yapilanlar:
- replenish.py: sure kontrolu cfg.shot_seconds'tan (tek-obje'de config zaten 6'ya
  kilitli, mesaj bayt bayt ayni); `PLATO_OBJECT_RULE` (yalniz plato-3x8): tek gercek
  hayvan, dogal anatomi, habitata uyan set, ifsa yalniz cekim 3, olumsuz kelime yasagi;
  opt-in `required_characters` her cekime mekanik eklenir, bible'da yoksa cfg hatasi;
  modelin kismen kopyaladigi SHOT satiri atilir, kanonik satir bir kez kalir.
- shots.py: `PLATO_FORMAT` sabiti (produce ve replenish buradan alir).
- series.json: status active, publish_mode auto, enabled true, required_characters,
  baslik kalibi {0,2}, aileler hayvan turu (reptile, sea-giant, insect-giant,
  mammal-giant, bird-giant), parts 5 ve 6 published, next_part 7.
- published.json: ep05 ve ep06 kimlik ve linkleriyle.
- bible.json: yalniz kurulmus setler (jungle_set, ocean_tank_set, desert_ruins_set);
  dis mekanlar ve ciplak soundstage cikti.
- .github/workflows/wild-encounter.yml: 18:30 UTC gunluk; unnatural-lab.yml'e
  dokunulmadi (bir test onu okuyor). series.yml (run_all) zamanlamasi kapali, cift
  uretim yok.
- PROOF: tests/test_replenish_plato.py (13 test, 5 mutasyonun 5'i yakalandi);
  gercek ikmal kosusu part07-11'i ILK denemede yazdi, hepsi dogrulayicidan temiz,
  tekrar yok, olumsuz kelime yok, her cekimde yuz kimligi; part07 dry-run temiz.

## Rocklardan sonra (Visionary, Codex degil)

1. Level 10 inceleme her rock icin: tam diff, kanit kendi kosumum, kendi
   adversaryal testim.
2. Dal ana agaca birlesir (teardown sirasi: once birlestir, sonra worktree sil).
3. ep06 uretimi (Ihsan onayladi, ~315 kredi): ana agacta
   `python -m series.cli produce wild-encounter sentinal_ihsan/wild-encounter/plans/part06.json`.
   Once/sonra Kie bakiyesi olculur (kayit maliyeti bilinmiyor).
   Kare kare izlerim, sesi olcerim, konumu Ihsan'a veririm; yayin Ihsan onayiyla.

## Non-goals

- Diger kanallar, diger seriler, gunluk beyin, dashboard.
- `require_continuity` / `require_object_match` / `require_first_frame`
  kapilarini acmak (ep06 olculmeden).
- `families` listesini yeniden tasarlamak.
- auto_replenish'i acmak.
- Yayin, push.

## EK A: hedef metinler (harfi harfine)

### A.1 `art_style`

```
Vertical 9:16 photoreal behind-the-scenes footage of a real film shoot on a studio stage. One giant, lifelike creature built as a practical effect stands on a dressed set of real materials, with practical haze, overhead studio lighting, crew in black, camera rigs and a green screen wall making the production obvious. Natural colour, true skin tones and real depth of field; everything else obeys ordinary physics.
```

### A.2 `series.qc.notes` (paragraflar arasi tek bos satir, JSON'da `\n\n`)

```
SERIES EXEMPTION, READ THIS FIRST: this series is a FAKE BEHIND-THE-SCENES of a film shoot. A giant, lifelike creature stands on a built film set and is revealed at the end to be a practical prop. Ignore the words "impossible anatomy" and "chimera" in your artifact_score definition FOR THAT CREATURE: it is the subject of the clip, not a defect, and it must NEVER raise artifact_score. Reserve the numeric artifact_score for UNINTENDED generation defects only: the man, his hands, his face, the crew, the floor or the set structure melting, duplicating, breaking or glitching.

THE BEAT OF EACH SHOT IS WRITTEN IN ITS OWN PROMPT. Each shot prompt contains a paragraph that begins "SHOT 1,", "SHOT 2," or "SHOT 3," followed by the beat name. That paragraph is the required story beat for that shot and it is authoritative: pass the shot only if the clip performs that beat, and judge the beat against no other description. The three beats are one continuous scene on one set and their order never changes: the threat, the man taken completely out of sight, and the reveal that the creature is a prop with the man unharmed.

THE PRODUCTION MUST BE VISIBLE IN EVERY SHOT. At least one clear production element, such as the green screen wall, crew, camera operators, rigs or studio lights, must be visible in the sampled frames of every shot. Dressed set materials such as foliage, rock, water and haze are EXPECTED. A shot in which no production element is visible, so that it reads as location footage, is a FAIL: the whole format depends on the viewer seeing that this is a film shoot.

SCALE CARRIES THIS FORMAT. The creature must be LARGE and CLOSE, filling much of the frame. A small or distant creature is a FAIL.

THERE IS NO TRANSFORMATION IN THIS SERIES. Nothing morphs, nothing fuses. A creature that changes shape or species is a FAIL. This was measured: the model cannot fuse two bodies, and that failure is why this format was chosen.

ONE MAN ONLY, in all three shots. One face, two hands, five fingers each. A second copy of him anywhere is an automatic fail. His face must match the reference: Turkish man, warm olive skin, full neatly groomed black beard, thick dark eyebrows, short dark hair. A different face is an automatic fail; this is the single most important check. Crew members are expected and are NOT copies of him.

He NEVER speaks and never moves his mouth as if talking; there is no narration. A posed look into the lens is a fail; watching the creature or the crew is correct.

Studio equipment, rigging, cables, monitors and camera bodies in frame are EXPECTED and are not defects. Only subtitle bars, captions or watermark-style graphics laid over the footage count as unwanted text. Water spray, haze and lens flare are INTENDED realism.

THE SOUND IS THE SET'S OWN SOUND: ambience, water, the creature rig moving, crew movement and applause.

All three shots are the SAME set and the SAME light. A drifting viewpoint inside a shot is a continuity observation, not a defect score; record it under issues in plain words.
```

### A.3 `auto_replenish.shot_plan`

```
SHOT 1, THE THREAT ON SET. A built film set reads immediately: dressed practical set pieces and haze around the frame, a green screen wall visible beyond them, and the backs of camera operators with their rigs in the foreground. One giant creature faces exactly one man, who stands his ground and watches its jaws begin to part.
```
```
SHOT 2, TAKEN INSIDE. The creature's jaws open wide and close over exactly one man until he is completely out of sight inside its mouth, and the creature settles with the man nowhere in frame. The crew keep filming.
```
```
SHOT 3, THE PRACTICAL REVEAL. Crew members put their hands on the creature and push its jaws open, and the same one man climbs out of the mouth onto the set floor unharmed, showing that the creature is a built practical prop rather than a living animal.
```

### A.4 `series.json` alanlari

- `logline`: `On a film set, a giant lifelike creature takes the performer into its mouth. Then the crew push its jaws open and he climbs out.`
- `hashtags`: `#shorts #vfx #behindthescenes #ai`
- `title_patterns`: yalniz bir kalip kalir:
  `{"regex": "This [A-Z][A-Z]+(?: [A-Z]+)? Is NOT Real", "families": <mevcut alti aile>}`
- `title_style`: `a punchy English Shorts title in exactly this pattern: 'This <ANIMAL> Is NOT Real' or 'This GIANT <ANIMAL> Is NOT Real', for example 'This GIANT CROCODILE Is NOT Real'. Every word before 'Is' is in CAPS. Max 60 characters, the validator rejects 61 and above. No hashtags, no surrounding quotes, no emoji in the title field.`
- `brief`:

```
SERI: bir film setinde dev, gercekci bir yaratik performans sanatcisini (Ihsan) agzina alir; ekip cenesini elleriyle acar ve Ihsan yara almadan cikar. Yaratigin pratik efekt oldugu son vurusta anlasilir. Kaynak: sentinal_ihsan/wild-encounter/DOKTRIN.md, GUNCEL FORMAT bolumu. >>> CIKTI DILI: bu brief TURKCEDIR ama URETTIGIN HER SEY INGILIZCEDIR: baslik, sinopsis ve TUM cekim promptlari Ingilizce yazilir. <<< DEGISMEZ KURALLAR: (1) ANLATIM VE MUZIK YOKTUR. Voiceover yok, konusma yok, muzik yok. Ses setin kendi sesidir. Cekim promptlarinda 'speaking', 'talking', 'explaining', 'narrating' GECMEZ. Her cekim promptu olumlu bir ses cumlesiyle biter, ornek: 'Ambient sound only: dripping water, studio air handling and distant crew movement.' (2) TEK DEV YARATIK, GERCEKCI, pratik efekt. Donusum yok, birlesme yok, iki hayvan yok. Izleyicinin tanidigi bir hayvan secilir ve cenesi bir insani alacak kadar buyuk olur. (3) UC VURUS, SIRASI DEGISMEZ, TEK SET: her cekim promptu shot_plan'daki metinle HARFI HARFINE baslar, ardindan bos satir ve o bolumun ayrintisi gelir. (4) IHSAN SAHNENIN ICINDE: yuzu ve govdesi net, KAMERAYA BAKMAZ, yaratiga ya da ekibe bakar. Kadrajda TEK Ihsan olur. (5) KIYAFET SETE GORE degisir (orman setinde saha gomlegi, su tankinda dalgic ustu); degismeyen sey adamin kendisidir. (6) OLCEK: yaratik buyuk ve yakin, kadrajin buyuk kismini doldurur. (7) SET: ciplak yesil perde DEGIL, kurulmus dekor: on planda gercek set malzemesi (yaprak, sarmasik, kaya, su, sis), arkada yesil perde, kenarda siyahli ekip, en onde kamera operatorlerinin sirti. Isik tepedeki studyo izgarasindan gelir. (8) SURE: uc cekim, her biri 8 saniye. (9) EKRANA YAZI YOK. (10) GUVENLIK: kan, yaralanma, hayvana eziyet yok; gerilim olcekten ve yutulma anindan gelir. (11) AILE: her bolum 'family' alanindaki kanonik listeden BIR aile secer ve ardisik iki bolum ayni aileyi KULLANAMAZ.
```

### A.5 `bible.series` notlari

- `format_note`: `2026-09-11, plato-3x8. Sahte kamera arkasi: uc cekim x 8 sn, tek set, tek sahne. Vuruslar: tehdit, yaratigin agzina alinma, ekibin ceneyi elle acmasi ve cikis. Olcum dayanagi: DckORL2B8gx (15,2 sn, 0 kesme, 4,4M) ve DdEArj4BMrV (15,18 sn, 0 kesme, kurulmus dekor). ep05 22,7 sn, 2 kesme. Vurus metninin TEK kaynagi series.json auto_replenish.shot_plan; QC notu vurus tarif etmez, prompttaki SHOT paragrafina bakar.`
- `chain_note`: `2026-09-11 ACIK. Tek set, tek sahne: cekim 2 ve 3 onceki cekimin son karesinden baslar, set ve isik bolum icinde sabit kalir.`
- `object_match_note`: `2026-09-11 KAPALI. plato-3x8 icin yaratik referansi RF-PLAN-WILD-ENCOUNTER Rock 4 ile uretiliyor. Kapi ep06 olculmeden ACILMAZ: yeni bir QC kapisi yanlis retle kredi yakar.`
- `first_frame_note`: `2026-09-11 KAPALI. require_first_frame acilis karesinde imkansiz ozellik arar; bu formatta imkansiz ozellik yok, yaratik bir prop ve ifsa cekim 3'te. Acik olsa her bolumu yanlis sebeple reddeder.`
- `continuity_note`: `2026-09-11 KAPALI, ep06 olculene kadar. Eski gerekce cekimlerin farkli mekanlarda gecmesiydi; plato-3x8'de tek set var. chain_frames ve ortam referansi sureklilik sagliyor; kapiyi olcmeden acmak yanlis retle kredi yakma riskidir.`

### A.6 `characters[ihsan_field].bio`

```
Kanalin yuzu, Ihsan'in kendi figuru. Her bolumde bir film setinde dev, gercekci bir yaratikla sahneye cikar; yaratik onu agzina alir, ekip cenesini acar, o yara almadan cikar. Kamerada ASLA konusmaz ve agzini konusur gibi oynatmaz; bu seride anlatim ve muzik YOKTUR, ses setin kendi sesidir. Yuzu ve govdesi kadrajda NET gorunur, kameraya degil yaratiga ya da ekibe bakar. Kiyafeti bolumden bolume SETE GORE degisir; degismeyen sey adamin KENDISIDIR.
```

### A.7 DOKTRIN.md "GUNCEL FORMAT" bolumu

```
## GUNCEL FORMAT (11 Eylul 2026'dan itibaren gecerli)

Bu bolum asagidaki "Tek cumle", "Degismez kurallar" ve "Neye DOKUNMA"
bolumlerinin YERINE gecer. Onlar 10 Eylul'un dis mekan / melez yaratik
formatini anlatir; o format olculerek terk edildi (asagidaki basarisizlik
kayitlari). Kayitlar ders olarak duruyor.

### Tek cumle

Bir film setinde dev, gercekci bir yaratik Ihsan'i agzina alir; ekip
cenesini elleriyle acar ve Ihsan yara almadan cikar. Yaratigin bir prop
oldugu son vurusta anlasilir.

### Kurallar

1. ANLATIM YOK, MUZIK YOK. Ses setin kendi sesidir: ortam, su, yaratik
   mekanizmasi, ekip hareketi, alkis. Diegetik ses kisilmez. Mastering
   muziksiz govde uzerinde -14 LUFS / -1 dBTP'ye yapilir. (11 Eylul, ep05
   sonrasi Ihsan karari.)
2. UC VURUS, SIRASI DEGISMEZ, TEK SET: tehdit, agza alinma, ekibin ceneyi
   acmasi ve cikis. Vurus metninin TEK KAYNAGI
   series.json auto_replenish.shot_plan; her cekim promptu o metinle baslar.
3. QC NOTU VURUS TARIF ETMEZ, prompttaki "SHOT N," paragrafina bakar.
   Sebep: kural degisip QC notu bayat kalinca dogru video yanlis sebeple
   reddedildi; 11 Eylul'de uc kez, 483 kredi.
4. art_style HER cekim promptunun basina eklenir (series/shots.py). Formati
   degistiren her karar art_style'i ayni anda degistirir.
5. KURULMUS DEKOR, CIPLAK YESIL PERDE DEGIL. On planda gercek set malzemesi
   (yaprak, kaya, su, sis), arkada yesil perde, kenarda ekip, en onde kamera
   operatorlerinin sirti. (DdEArj4BMrV dersi.)
6. GIRIS AGIZDAN, CIKIS EKIBIN ELLERIYLE. Prop oldugunu kanitlayan sey alkis
   degil, ellerin dekorun uzerinde olmasi.
7. TEK YARATIK, DONUSUM YOK. Iki govde birlestirilemiyor (olculdu).
8. OLCEK: yaratik buyuk ve yakin, kadrajin buyuk kismini doldurur.
9. TEK IHSAN, konusmaz, kameraya bakmaz. Yuz capasi character_id; kiyafet
   sete gore degisir.
10. SURE: 3 x 8 sn, duration_band [12, 26]. ep05 22,7 sn cikti.
11. EKRANA YAZI YOK. GUVENLIK: kan ve yaralanma yok.
```

ROCK 4 bittiginde eklenecek 12. madde:

```
12. Her bolumun yaratigi bir referans gorselle (plan.prop_ref_urls), seti
    ortam referansiyla capalanir (bible.series.episode_anchors); bolum icinde
    cekim zinciri de surekliligi tasir. Yaratigi Kie'de KARAKTER olarak kaydetmek
    olculmus bir denemeden once uretime baglanmaz (insan olmayan ozne ve ucret
    dogrulanmadi).
```

## EK B: capa prompt'lari (ROCK 4)

### B.1 ortam referansi

```
Reference plate of a built film set for a vertical 9:16 video series: {env_desc}. One wide, locked-off composition shows the whole dressed set, the green screen wall beyond it, the overhead studio lighting grid and practical haze, in natural colour with real depth of field. The set stands empty and ready before the take, with the floor clear.
```

### B.2 yaratik referansi

```
Hero reference image of one {name} standing on a built film set: {env_desc}. Exact identity: {descriptor}. The whole creature is visible at realistic scale under overhead studio light, its colour, skin texture, eyes and teeth sharply readable, and the set around it stands empty and ready before the take.
```
