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
