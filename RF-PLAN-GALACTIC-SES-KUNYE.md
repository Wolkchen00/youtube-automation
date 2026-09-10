# RF-PLAN: galactic_experience kanal duzeltmesi (ses + kunye + yayin kapisi + baslik)

Tarih: 10 Eylul 2026 (Los Angeles)
Kaynak analiz: `galactic_experience/REELYZE-RAPOR.md`
Seri: `event-horizon` (kanal: galactic_experience / galacticexperimet)
Temel: `git HEAD 9eec629`, `python -m pytest tests/ -q` => 801 passed, 2 skipped, 188 subtests

## Core Focus

event-horizon bolumleri telefon hoparlorunde DUYULSUN, sessiz izleyicide bir sey OKUNSUN,
ve kusurlu bolum yayina CIKMASIN. Tek kanal, dort dosya grubu, olculebilir kanit.

## Kapsam karari (Ihsan, 10 Eylul)

1. Ses duzeltmesi YALNIZ galactic_experience'a girer. shadowedhistory ve aimagine ile
   baska ajanlar ilgileniyor; onlarin `bible.json` / `series.json` dosyalarina DOKUNULMAZ.
2. Ekran kunyesi icin ortak motora (`series/replenish.py`) dar, additif muafiyet yazilir.
3. Kusurlu (degraded) bolum yayini YALNIZ event-horizon'da durdurulur; diger uc serinin
   davranisi bit bit ayni kalir.
4. Baslik kalibi degisir VE kuyruktaki hazir planlar (part 32-35) yeni kaliba cevrilir.

## Olculmus baslangic durumu (bu plan tahmine degil olcume dayanir)

Iki yayinlanmis video yt-dlp ile indirildi, ffmpeg EBU R128 ve sahne taramasiyla olculdu:

| Bolum | Integrated LUFS | True peak | Sure | Gercek kesme |
|---|---|---|---|---|
| part 24 Neptune (`TVXhCHS5vUg`) | -24,7 | -10,7 dBFS | 10,95 sn | 1 (5,57 sn) |
| part 31 Earth Rings (`Enq3rtRayIg`) | -21,9 | -8,6 dBFS | 19,65 sn | 2 (5,57 / 11,17 sn) |

Hedef: -14 LUFS, TP -1,0. Fark: 8-11 dB.

### Rapordaki iki duzeltme

- Rapor "Neptune'de 0 kesme" diyor. Bu bir OLCUM YANILGISI: ffmpeg sahne dedektori
  varsayilan esikte karanlik uzay goruntusundeki kesmeyi kaciriyor. Esik 0,04'e
  indirilince kesme 5,57 sn'de goruluyor ve kontakt sayfasi iki ayri cekimi
  (Neptune uzaklasiyor -> gunes yorunge diyagrami) gosteriyor. Gercek sorun kesme
  yoklugu DEGIL, planlanan 3 cekimin 2'siyle yayinlanmis olmasi.
- Rapor daha buyuk bir sorunu atlamis: part 29 (Olympus Mons) `dropped_shots: [3]`,
  `loop_closed: false`, `narration_delivered: false`, `degraded: true` ile YAYINLANMIS.
  Motor kusuru olcuyor, Telegram'a uyari atiyor, yayini durdurmuyor.

### Kok neden (kod okumasiyla teyitli)

`series/produce.py:2147-2148`: `bible.master_lufs is None` ise `master_audio` HIC
cagrilmiyor, ham miks yayinlaniyor. `series/bible.py:281-284`: alan yoksa None doner.
`galactic_experience/event-horizon/bible.json` icinde `master_lufs` yok;
`sentinal_ihsan/unnatural-lab/bible.json:11` icinde var (-14) ve o kanal -14,3 olcuyor.

---

## ROCK 1: Ses masteri acilir

**Neden birinci**: 8-11 dB eksik ses, anlatim tabanli bir kanalda icerigin kendisini
yok ediyor. YouTube sessiz videoyu YUKSELTMEZ (sadece yuksek olani kisar), yani bu
fark izleyiciye oldugu gibi gidiyor.

**Dosya**: `galactic_experience/event-horizon/bible.json`

`series` blogunun icine tek alan:
```json
"master_lufs": -14
```

**Done looks like**: `Bible(event-horizon).master_lufs == -14.0`; produce artik
`ffmpeg_tools.master_audio(target_i=-14, target_tp=-1.0, target_lra=11.0)` yolundan
geciyor; `flashpoints` ve `next-stop` bibl'lari BIT BIT degismemis.

**Kabul edilen risk**: master yolu acilinca mastering hatasi `_audio_master_hold`
dondurur ve o bolum yayinlanmaz. Bu yol `unnatural-lab`'da her gun calisiyor, kanit
edilmis. Riski kabul ediyoruz.

**PROOF**:
```
python -m pytest tests/ -q
```
801+ passed olmali (yeni testler haric dusen olmayacak). Ayrica yeni test dosyasi
`tests/test_galactic_master_lufs.py`:
- `event-horizon` bible'inda `master_lufs == -14.0`.
- `flashpoints` ve `next-stop` bible'larinda hala `None` (kapsam disi kanallara
  sizmadigimizin nobetcisi).
- ffmpeg ile uretilen -25 LUFS'luk sentetik sinyal `master_audio(target_i=-14)`'ten
  gecince olculen integrated -14 +/- 0,5 LUFS ve true peak <= -1,0 dBTP olmali
  (ffmpeg yoksa test skip eder, hata vermez).

---

## ROCK 2: Ekran kunyesi acilir (ortak motorda dar muafiyet)

**Neden ikinci**: Bu seride hicbir ekran yazisi yok. Sessiz izleyici hicbir sey
okuyamiyor. Motorda `title_card_overlay` (`core/ffmpeg_tools.py:1362`) HAZIR ve
`shadowedhistory` kullaniyor.

**Tuzak**: `series/replenish.py:1372-1384` her seride kunyeye 4 haneli YIL sart
kosuyor (tarih kanallari icin yazilmis; `flashpoints` icin cag capasi istisnasi var).
Uzay kanalinda "Olympus Mons, 1971" sacma olurdu ve yil sarti kuyruktaki her plani
reddederdi. Muafiyet SART.

**Dosyalar ve degisiklikler**:

1. `series/replenish.py`
   - Yeni opsiyonel cfg alani: `title_card_year_required` (bool, **varsayilan True**).
     Varsayilan True olmasi, dokunulmayan uc serinin davranisini bit bit korur.
   - Alan, cfg anahtar beyaz listesine eklenir (satir ~145 ve ~216'daki iki listeye);
     aksi halde bilinmeyen anahtar dogrulamayi patlatir.
   - `want_tc` dogrulamasinda: `title_card_year_required` False ise yil kontrolu
     ATLANIR; title/subtitle zorunlulugu ve 60 karakter siniri AYNEN kalir.
   - `tc_shape` prompt metni (satir ~652) kosullu olur: yil gerekmiyorsa modelden
     yil degil, `title` = gok cisminin adi (max 40 karakter),
     `subtitle` = anomalinin kendisi (max 6 kelime) istenir.
2. `galactic_experience/event-horizon/bible.json`
   - `series` blogu: `"title_card": {"enabled": true, "duration": 2.0}`
3. `galactic_experience/event-horizon/series.json`
   - `auto_replenish`: `"title_card": true`, `"title_card_year_required": false`
   - `brief` icine kunye kurali eklenir (Ingilizce cikti, 3-7 kelime, ust ucte bir).

**Done looks like**: event-horizon plani yilsiz kunyeyle dogrulamadan GECER;
`flashpoints` plani yilsiz kunyeyle hala REDDEDILIR; kunye final videoya biniyor.

**NON-GOAL**: `fact_captions` bu rock'ta acilmaz (ayri bir katman, ayri kanit gerekir).

**PROOF**:
```
python -m pytest tests/ -q
```
Yeni test dosyasi `tests/test_title_card_year_exemption.py`:
- `title_card_year_required: false` cfg'sinde yilsiz kunye KABUL edilir.
- Ayni cfg'de bos subtitle REDDEDILIR, 61 karakterlik title REDDEDILIR.
- `title_card_year_required` HIC verilmemis cfg'de yilsiz kunye REDDEDILIR
  (geriye donuk uyum nobetcisi).
- `flashpoints` slug'inda cag capasi istisnasi hala calisir.

---

## ROCK 3: Kusurlu bolum yayini durur (yalniz event-horizon)

**Neden ucuncu**: part 29 anlatimsiz ve eksik cekimle yayinlandi (131 izlenme).
part 24 planlanan 3 cekimin 2'siyle, 10,95 saniye yayinlandi. Motor ikisini de
"degraded" olarak OLCTU ama yayini durdurmadi.

**Dosyalar ve degisiklikler**:

1. `series/bible.py`
   - Yeni property `block_degraded_publish` -> `bool(series.get("block_degraded_publish", False))`.
     Varsayilan False: dokunulmayan uc serinin davranisi bit bit ayni kalir.
2. `series/series_runner.py`
   - `_publish_part` cagrisindan ONCE: bible bayragi True ve `result.coherence["degraded"]`
     True ise bolum YAYINLANMAZ. Mevcut `_record_recoverable_failure` yoluna
     `reason_code="EPISODE_DEGRADED"` ile girer; boylece icerik retry sayaci calisir
     (3 deneme, sonra `needs_human`) ve kuyruk sessizce kilitlenmez.
   - `EPISODE_DEGRADED` `_NON_RETRYABLE_REASON_CODES` ve `_INFRA_REASON_CODES`
     kumelerine EKLENMEZ (icerik sinifi olmali).
   - Telegram uyarisi neyin eksik oldugunu yazar (loop, anlatim, sure, dusen roller).
3. `galactic_experience/event-horizon/bible.json`
   - `series` blogu: `"block_degraded_publish": true`
   - `series` blogu: `"duration_band": [14, 26]`
     Gerekce: saglikli bolumler 16,6 ve 19,65 sn olctu; basarisiz olanlar 10,95 ve
     11,1 sn. 14 alt siniri basarisizlari yakalar, saglikliyi yakalamaz.
     `duration_band` olmadan `duration_in_band` hep None kalir ve sure hic denetlenmez.

**Kabul edilen maliyet**: son 10 bolumun 3'unde cekim dustu. Bu kapi acikken o bolumler
yayinlanmak yerine yeniden uretilir (3 denemeye kadar), yani kredi harcamasi artabilir
ve yayin temposu duser. Ihsan bunu bilerek secti: az ama saglam video.

**NON-GOAL**: `qc.min_shots` / `require_all_shots` bu rock'ta EKLENMEZ. Dusen cekim
zaten `arc_roles_missing` uzerinden `degraded` yapiyor; ikinci bir kapi ayni isi
uretim ortasinda, daha kor bir sekilde yapardi.

**PROOF**:
```
python -m pytest tests/ -q
```
Yeni test dosyasi `tests/test_degraded_publish_gate.py`:
- Bayrak True + degraded coherence -> `_publish_part` HIC cagrilmaz, part `qc_retry`
  olur, `retry_count` artar.
- Bayrak True + saglikli coherence -> yayin normal ilerler.
- Bayrak YOK (varsayilan) + degraded coherence -> yayin ESKISI GIBI ilerler
  (uc kanali koruyan nobetci).
- Uc basarisiz denemeden sonra `needs_human` ve kuyruk ilerler.

---

## ROCK 4: Baslik kalibi anomali vaat eder + kuyruk yenilenir

**Neden dorduncu**: Basliklar konu bildiriyor, merak yaratmiyor. "Olympus Mons:
Towers Over Everest" bir ansiklopedi satiri. Filodaki tek basarili kanal
(`sentinal_ihsan`, 1.292 medyan) "This X Is NOT Supposed To Y" kalibini kullaniyor:
konu degil ANOMALI vaat ediyor.

**Dosyalar ve degisiklikler**:

1. `galactic_experience/event-horizon/series.json`
   - `auto_replenish.title_style`: mevcut dort kalibin yanina anomali-once kaliplari
     eklenir; ornegin `"<Subject> Should Not <verb>. It Does."` ve
     `"<Subject> Breaks <rule>"`. En fazla bir ALL-CAPS kelime kurali, emoji ve
     hashtag yasagi AYNEN korunur.
   - `brief` (5) SES maddesine dokunulmaz; baslik maddesi guncellenir.
2. `galactic_experience/event-horizon/plans/part32.json` ... `part35.json`
   - `episode.title` yeni kaliba cevrilir (Ingilizce, gercek astronomi, uydurma yok;
     konu ve fakt DEGISMEZ, sadece basligin sozdizimi degisir).
   - Her plana ROCK 2'nin sekliyle `title_card` alani eklenir.
   - `doctrine_sha256` alanina DOKUNULMAZ (doktrin metni degismiyor).

**Done looks like**: dort kuyruk plani yeni kaliba uyar, kunye alanini tasir ve
`preflight` dogrulamasindan gecer.

**NON-GOAL**: `title_patterns` regex zorlamasi bu turda EKLENMEZ. Alti aile uzerinde
fullmatch regex genis bir yuzey; once kalibin ise yarayip yaramadigini olcelim.
Issues listesine gider.

**PROOF**:
```
python -m pytest tests/ -q
python -c "import json,glob; [json.load(open(p,encoding='utf-8')) for p in glob.glob('galactic_experience/event-horizon/plans/part3[2-5].json')]"
```
Yeni test dosyasi `tests/test_galactic_queue_titles.py`:
- part 32-35 planlarinin her birinde `title_card.title` ve `.subtitle` dolu ve
  <= 60 karakter.
- Her birinde `episode.title` bos degil, emoji ve hashtag icermiyor, en fazla bir
  ALL-CAPS kelime tasiyor.
- Her birinde `doctrine_sha256` korunmus.

---

## Bagimlilik sirasi

ROCK 1 -> ROCK 2 -> ROCK 3 -> ROCK 4.
ROCK 4, ROCK 2'nin kunye seklini kullandigi icin ondan sonra gelir. ROCK 1 ve 3
birbirinden bagimsiz ama ROCK 1 once cunku tek basina en buyuk etkiye sahip.

## DOKUNMA listesi

- `shadowedhistory/**`, `aimagine/**`, `AImagine-Fear/**`, `sentinal_ihsan/**`:
  baska ajanlarin alani. Tek satir bile degismez.
- `core/ffmpeg_tools.py`: master_audio, title_card_overlay ve fact_captions_overlay
  calisiyor. Davranis degisikligi YOK.
- `galactic_experience/event-horizon/published.json`, `series_log.*`, `qc_log.jsonl`:
  gecmis kayit, dokunulmaz.
- `galactic_experience/planetfall`, `ava-voyage`: duraklatilmis, oyle kalsin.
- Cozunurluk 1080x1920 ve fps 30 dogru, dokunulmaz.
- `doctrine_sha256` pinleri: doktrin metni bu planda degismiyor, pin de degismez.

## Bu turda YAPILMAYANLAR (Issues listesine)

- `fact_captions` katmani (alt ucte senkron bilgi yazisi).
- `title_patterns` regex zorlamasi.
- Cekim basina 4 saniye tavani / 5-7 saniyede pattern interrupt: `shot_seconds` 6'dan
  4'e inmek cekim sayisini ve kredi maliyetini artirir, ayri bir maliyet karari.
- part 31'in son cekiminin 8,48 saniye surmesi (anlatim uzunlugu cekimi geriyor).
- Diger uc kanalin `master_lufs` eksigi (baska ajanlarin alani).
- Retention ve CTR verisi: YouTube Studio gerekiyor, olculemedi.
