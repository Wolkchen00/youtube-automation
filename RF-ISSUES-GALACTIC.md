# RF-ISSUES: galactic_experience turundan ertelenenler

Tarih: 10 Eylul 2026 (Los Angeles)
Kaynak: `RF-PLAN-GALACTIC-SES-KUNYE.md` ve bes turluk Same Page Meeting.
Bu turda BILEREK yapilmadi. Her biri gerekcesiyle burada duruyor.

## Ortak motorda duran gercek kusurlar

- **`_budget_failure` muhasebe okunamadiginda da "butce bitti" diyor.** (yuksek)
  `series/series_runner.py:574-588`: `produce.episode_spent` veya
  `minimum_remaining_completion_cost` None dondugunde sonuc `BUDGET_EXHAUSTED` olur,
  part TERMINAL yapilir ve kuyruk ilerletilir. Yani bozuk bir maliyet kaydi sessizce
  bolum yakar. Kapi `state_machine_version >= 2` olan her seride aciktir, yani
  `unnatural-lab` ve artik `event-horizon`.
  event-horizon icin bugun tetiklenmiyor, olculdu: asgari 300, kalan 900, tavan 900.
  Duzeltme yonu: muhasebe YOKLUGU ile kanitlanmis tukenmisligi ayirmak; yoklugu
  `TRANSIENT_INFRA` gibi sonlu ve yeniden denenebilir bir sinifa koymak.

- **`migrate_malformed_approval_holds` isaretciyi ilerletmeyebilir.** (orta)
  `series/series_runner.py:444-480`: bir kaydi `needs_human` yaptiginda `next_part`
  ilerlemez; sonraki her kosu satir 659'daki erken donusle "atlandi" deyip True doner.
  event-horizon kayitlarinda su an boyle bir kayit YOK (test bunu dogruluyor).

- **`ebur128` true-peak'i 0,1 dB cozunurlukte raporluyor.** (orta)
  `core/ffmpeg_tools.py:171-200`: -1,04 dBTP "-1,0" olarak okunabilir, yani sozlesme
  ihlali "gecti" diye damgalanabilir. ROCK 1'in payi bu marji pratikte kapatiyor ama
  olcumun kendisi hala kaba. Yuksek cozunurluklu dogrulama ayri bir is.

## Bu kanalda yapilmayanlar

- **`fact_captions` katmani.** Alt ucte senkron bilgi yazisi. Motor hazir
  (`core/ffmpeg_tools.py:1445`), plan `shot['fact']` alani istiyor. Ayri kanit gerekir.
- **`title_patterns` regex zorlamasi.** Alti aile uzerinde fullmatch genis bir yuzey.
  Once yeni baslik kalibinin ise yarayip yaramadigi olculmeli.
- **Cekim basina 4 saniye tavani / 5-7 saniyede pattern interrupt.**
  `shot_seconds` 6'dan 4'e inmek cekim sayisini ve kredi maliyetini artirir; ayri bir
  maliyet karari.
- **part 31'in son cekiminin 8,48 saniye surmesi.** Anlatim uzunlugu son cekimi geriyor.
  Olculdu (kesmeler 5,57 / 11,17; toplam 19,65) ama bu turda dokunulmadi.

## Diger kanallar (baska ajanlarin alani)

- **`shadowedhistory` ve `aimagine`'de `master_lufs` yok.** Olculen: flashpoints
  -20,5 / -25,1; next-stop -16,1 / -17,1 ve true peak +0,7 ile KIRPIYOR.
  ROCK 1'in limiter payi onlarin da yolunu acar ama bayragi biz ACMIYORUZ.
- **`sentinal_ihsan/unnatural-lab` part 33 su an `AUDIO_MASTER` hatasiyla `qc_retry`.**
  Hata imzasi bizim buldugumuzla ayni. `master_true_peak_margin_db: 0.2` eklemek
  muhtemelen serbest birakir, ama o kanal bizim alanimiz degil.
- **Diger uc seri hala `state_machine_version` 1'de.** Ayni sessiz-susma riski
  (bir `qc_hold` -> `awaiting_approval` -> her kosu yesil) onlarda da var.

## Olculemeyenler

- Retention egrileri ve impressions/CTR: YouTube Studio erisimi gerekiyor.
- 140 abone ile 88 medyan izlenme arasindaki fark: aboneler gormuyor mu, goruyor da
  tiklamiyor mu? Veri olmadan ayirt edilemez.

---

## 10 Eylul aksami , Codex tarama testi sonrasi durum

Part 33 elle tetiklendi ve 3/3 platforma cikti. Yayinlanmis dosya indirilip
olculdu: -14,1 LUFS, true peak -1,0 dBTP, 19,83 sn, kunye ekranda.

### DUZELTILDI

- **Kirpilan anlatim sessiz kaliyordu.** `mix_voiceover` anlatimi kesip yalnizca
  log'a yaziyordu; `coherence.narration_delivered` yine de `true` oluyordu ve
  bolum sonu kesik anlatimla yayinlanabiliyordu. Opsiyonel `report` sozlugu
  eklendi, kirpma artik butunluk kapisina ve Telegram'a dusuyor.
- **Rejim damgasi olcum aninda okunuyordu.** Artik motorun uretim aninda yazdigi
  `stack_sha256` kullaniliyor (video_id -> published.json -> part).
- **Kusur defteri yalnizca anlik goruntuydu.** Motor artik her tutulma yolunda
  olay ANINDA `hold_log.jsonl` yaziyor; iki kosu arasinda dogup olen hata da iz
  birakiyor.
- **Yayinlanmayan bolum "uretildi" diye sunuluyordu.** `budget_exhausted`,
  `skipped` ve `rejected` bolumlerde ucretli is hic baslamiyor; artik ayri
  sayiliyorlar.

### YANLIS CIKAN BULGU

- Codex "dusen cekim yeniden denemede krediyi tekrar yakar" dedi. Kabul edilen
  cekimler diske onbellekleniyor ve `_revalidate_cached_shot` ile dogrulanip
  tekrar kullaniliyor (`produce.py:1583`). Onerilen duzeltme zaten kurulu.

### HALA ERTELENMIS

- **TTS hatasi ucretli cekimlerden SONRA bolumu tutuyor.** Codex anlatimin
  cekimlerden once uretilmesini onerdi. Siddeti dusuk: cekimler onbellekte
  oldugu icin yeniden deneme kredi yakmaz, maliyet bir gunluk gecikmedir.
  Boru hattini yeniden siralamak kendi riskini getirir.
- **`flashpoints` hala `state_machine_version` 1.** Payi (0.2) kendileri aldi ve
  takili part 31'i serbest biraktilar, yani aktif sorun yok; ama bir `qc_hold`
  yine `awaiting_approval` yapip kanali sessizce susturabilir. O kanal baska bir
  ajanin alani.
- **`beyin.py` artik `## 6. BASLIK OZNESI` bolumu uretiyor.** Bes basliklik
  sozlesme testi yalniz o besinin VARLIGINI dogruluyor, fazlasini yasaklamiyor.
  Bolum baska bir ajanin isi; sozlesmenin "tam bes" mi yoksa "en az bes" mi
  oldugu onlarin karari.
