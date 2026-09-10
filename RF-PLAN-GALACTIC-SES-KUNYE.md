# RF-PLAN: galactic_experience kanal duzeltmesi (ses + kunye + yayin kapisi + baslik)

Tarih: 10 Eylul 2026 (Los Angeles)
Kaynak analiz: `galactic_experience/REELYZE-RAPOR.md`
Seri: `event-horizon` (kanal: galactic_experience / galacticexperimet)
Temel: `git HEAD 9eec629`, `python -m pytest tests/ -q` => 801 passed, 2 skipped, 188 subtests
Revizyon: r4 (Codex tur 2 bulgulari uygulandi)

## Core Focus

event-horizon bolumleri telefon hoparlorunde DUYULSUN, sessiz izleyicide bir sey OKUNSUN,
ve kusurlu bolum yayina CIKMASIN. Tek kanal, dort dosya grubu, olculebilir kanit.

## Kapsam karari (Ihsan, 10 Eylul)

1. Ses duzeltmesi YALNIZ galactic_experience'a girer. shadowedhistory ve aimagine ile
   baska ajanlar ilgileniyor; onlarin `bible.json` / `series.json` dosyalarina DOKUNULMAZ.
2. Ekran kunyesi icin ortak motora dar, additif muafiyet yazilir.
3. Kusurlu (degraded) bolum yayini YALNIZ event-horizon'da durdurulur.
4. Baslik kalibi degisir VE kuyruktaki hazir planlar (part 32-35) yeni kaliba cevrilir.

## Olculmus baslangic durumu

Iki yayinlanmis video yt-dlp ile indirildi, ffmpeg EBU R128 ve sahne taramasiyla olculdu:

| Bolum | Integrated LUFS | True peak | Sure | Gercek kesme |
|---|---|---|---|---|
| part 24 Neptune (`TVXhCHS5vUg`) | -24,7 | -10,7 dBFS | 10,95 sn | 1 (5,57 sn) |
| part 31 Earth Rings (`Enq3rtRayIg`) | -21,9 | -8,6 dBFS | 19,65 sn | 2 (5,57 / 11,17 sn) |

Hedef: -14 LUFS, TP -1,0. Fark: 8-11 dB.

`series.json` icindeki coherence kayitlari (motorun kendi olcumu):

| part | sure (sn) | degraded | dusen rol | anlatim |
|---|---|---|---|---|
| 26 | 11,02 | evet | episode_body | var |
| 27 | 11,03 | evet | loop_seam | var |
| 28 | 16,62 | hayir | - | var |
| 29 | 11,10 | evet | loop_seam | **YOK** |
| 30 | 16,62 | hayir | - | var |
| 31 | 19,62 | hayir | - | var |

Saglikli bant 16,62-19,62; bozuk bolumler 11,02-11,10. Son alti bolumun **ucu** kusurlu
ve ucu de yayinlandi.

### Rapordaki iki duzeltme

- Rapor "Neptune'de 0 kesme" diyor. Bu bir OLCUM YANILGISI: ffmpeg sahne dedektori
  varsayilan esikte karanlik uzay goruntusundeki kesmeyi kaciriyor. Esik 0,04'e
  indirilince kesme 5,57 sn'de goruluyor. Gercek sorun kesme yoklugu DEGIL, planlanan
  3 cekimin 2'siyle yayinlanmis olmasi.
- Rapor daha buyugunu atlamis: part 29 anlatimsiz ve eksik cekimle YAYINLANMIS.

### Kok neden (kod okumasiyla teyitli)

`series/produce.py:2147-2148`: `bible.master_lufs is None` ise `master_audio` HIC
cagrilmiyor. `galactic_experience/event-horizon/bible.json` icinde alan yok;
`sentinal_ihsan/unnatural-lab/bible.json:11` icinde var (-14) ve o kanal -14,3 olcuyor.

---

## ROCK 0: event-horizon durum makinesi surum 2'ye alinir (ONKOSUL)

**Neden sifirinci ve neden zorunlu**: `event-horizon/bible.json` icinde
`state_machine_version` YOK, yani varsayilan 1. `series/series_runner.py:650`
`new_state_machine = False` uretir. Sonucu:

- `_record_recoverable_failure` event-horizon icin HIC cagrilmaz (satir 773 v2 sarti).
- Bir `qc_hold` (ornegin mastering hatasi) `status = "awaiting_approval"` yapar ve
  fonksiyon **True** doner, yani cron kosusu BASARILI gorunur.
- Sonraki her kosuda satir 659 `awaiting_approval` gorup "uretim ve yayin atlandi"
  deyip yine True doner. **Kanal susar ve her kosu yesil rapor verir.**

Bu tahmin degil: `sentinal_ihsan/unnatural-lab` part 33 SU AN
`status=qc_retry, last_reason_code=AUDIO_MASTER, retry_count=1`,
hold_reason: "mastering basarisiz: master teslim sozlesmesi 3 denemede tutulamadi:
true-peak...". Mastering gercekten patliyor. unnatural-lab v2 oldugu icin kendini
toparliyor; event-horizon v1'de ayni olay kanali susturur.

**Dosya**: `galactic_experience/event-horizon/bible.json`, `series` blogu:
```json
"state_machine_version": 2
```

**Done looks like**: event-horizon hatalari sonlu yeniden deneme yolundan geciyor
(3 icerik denemesi, sonra `needs_human` ve kuyruk ilerler); `awaiting_approval`
kalintilari `migrate_malformed_approval_holds` ile bir kez siniflandiriliyor.

**Surum 2'nin ACTIGI ikinci kapi (tur 2 bulgusu, olculdu)**: `series_runner.py:708`
`if new_state_machine and not dry_run:` ile `_budget_failure` devreye girer. Bu kapi
`episode_spent` veya `minimum_remaining_completion_cost` None dondugunde
`BUDGET_EXHAUSTED` uretir ve part'i TERMINAL yapip kuyrugu ilerletir, yani muhasebe
OKUNAMADIGINDA da "butce bitti" der. event-horizon'un bugunku gercek degerleri
olculdu ve kapi TETIKLENMIYOR:

```
minimum_remaining_completion_cost(part32) = 300.0
episode_spent(part32)                     = 0.0
episode_credit_cap                        = 900
-> kalan 900 >= asgari 300, BUDGET_EXHAUSTED yok
```

Latent risk (maliyet kaydi bozulursa sessizce part yakar) ortak motorda ve
`unnatural-lab`'i da ilgilendirir; Issues listesine alindi, bu turda duzeltilmiyor.

**PROOF**: `python -m pytest tests/ -q` yesil, arti yeni test
`tests/test_galactic_state_machine_v2.py`:
- `Bible("event-horizon").state_machine_version == 2`.
- v2 acikken `qc_hold` sonucu `_record_recoverable_failure` yoluna girer,
  `awaiting_approval` DEGIL `qc_retry` olur.
- `flashpoints` ve `next-stop` hala varsayilan surumde (kapsam nobetcisi).
- Gercek event-horizon verisiyle `_budget_failure` None doner (kapi tetiklenmez);
  test olculen 300/900 degerlerini cakar ki bu varsayim sessizce degisirse patlasin.
- `migrate_malformed_approval_holds` bir kaydi `needs_human` yaptiginda `next_part`
  ilerlemiyorsa kuyruk sonsuza kadar "atlandi" der: bu senaryo test edilir ve
  event-horizon kayitlarinda boyle bir kayit OLMADIGI dogrulanir.

---

## ROCK 1: master_audio true-peak dongusu bu icerikte yakinsamiyor (ORTAK MOTOR, OPT-IN)

**Bu bulgu Visionary'nin kendi olcumunden geldi, raporda ve Codex tur 1'de yoktu.**

Yayinlanmis part 24 videosu (-24,8 LUFS) motorun kendi
`core/ffmpeg_tools.master_audio(target_i=-14, target_tp=-1.0)` fonksiyonundan
gecirildi. Sonuc:

```
RuntimeError: master teslim sozlesmesi 3 denemede tutulamadi:
true-peak -0.9 dBTP > -1.0 dBTP
```

Yani `master_lufs` alanini eklemek TEK BASINA bu bolumu duzeltmezdi;
`AUDIO_MASTER` hold'una dusururdu.

### Kok neden (bu ornek uzerinde olculdu)

Tavan supurmesi (ayni gercek ses, ayni boru hatti, ayni kodlayici):

| limiter tavani | teslim true-peak (ebur128) | astats tepe |
|---|---|---|
| -1,0 dB | -0,9 | -0,973 |
| -1,1 dB | -0,9 | -1,043 |
| -1,2 dB | -0,9 | -1,086 |
| **-1,3 dB** | **-1,3** | -1,295 |
| -1,5 dB | -1,3 | -1,415 |

Dongu (`core/ffmpeg_tools.py:305-307`) tavani tam olculen tasma kadar geri cekiyor:

```python
overshoot = delivered["true_peak_dbtp"] - float(target_tp)   # 0.1
limiter_db -= overshoot
```

Mevcut `tests/test_master_true_peak_adversarial.py` SABIT bir codec tasmasinin
(3,1 dB) bu donguyle yakinsadigini gosteriyor ve bu DOGRU: tasma tam olculebiliyorsa
bir adimda kapanir. Bu ornekte kapanmamasinin sebebi baska ve daha ince:

**ffmpeg'in ebur128 ozeti true-peak'i 0,1 dB cozunurlukte raporluyor.** Gercek
tavan-teslim araligi bu olcekte 0,15 dB civari (astats: tavan -1,1 iken tepe -1,043).
Olculen tasma (0,1) gercek aralikdan KUCUK oldugu icin her duzeltme adimi eksik
kaliyor. Uc deneme -1,0 / -1,1 / -1,2'de bitiyor; gectigi yer -1,3.

**Iddianin siniri, durustce**: bu tek bolum uzerinde olculdu. "Her bolum patlar"
demiyorum. Diyorum ki: olculen tasma raporlama cozunurlugunden kucukse dongu
ilerlemez, ve elimizdeki tek gercek ornekte bu tam olarak gerceklesti.
`sentinal_ihsan/unnatural-lab` part 33'un hold mesaji ayni imzayi tasiyor
(`AUDIO_MASTER`, "3 denemede tutulamadi: true-peak"); ayni kok neden OLABILIR
ama o bolumun sesi olculmedi, bu yuzden ayni sebep oldugu IDDIA EDILMIYOR.

### Duzeltme: opt-in pay, varsayilan bugunku davranis

`core/ffmpeg_tools.master_audio` yeni bir anahtar kelime argumani alir:

```python
def master_audio(..., true_peak_margin_db: float = 0.0):
    ...
    limiter_db -= (overshoot + float(true_peak_margin_db))
```

- Varsayilan `0.0` bugunku aritmetigin BIREBIR aynisidir.
- Deneme sayisi 3'te KALIR (tur 2 hakli: dorduncu denemeyi gerektiren bir kanit yok;
  0,2 dB pay ile ornek ikinci denemede geciyor).
- `target_tp - 3.0` dB kesme siniri PLANDAN CIKARILDI: mevcut adversarial test 3,1 dB
  tasmayi telafi eden bir cozumu gecerli sayiyor, o sinir onu reddederdi.

`series/produce.py` bu payi bible'dan okur ve gecer; `series/bible.py` yeni property
`master_true_peak_margin_db` (float, varsayilan 0.0, sonlu olmali, negatif olamaz).
`galactic_experience/event-horizon/bible.json`: `"master_true_peak_margin_db": 0.2`.

**Baska serilerin davranisi**: HIC degismez. Pay alani yok, varsayilan 0,0, aritmetik
birebir ayni. `unnatural-lab`'in bugun 2. veya 3. denemede gecen bolumleri de
etkilenmez. Bu, tur 2'nin "ilk deneme esitligi yetmez" itirazinin karsiligidir:
opt-in olmayan hicbir seride tek bir carpma bile degismiyor.

**Ihsan'in dikkatine**: ayni hata `unnatural-lab` part 33'u takmis olabilir.
Duzeltme onlar icin de tek satirlik bir alan, ama o kanal baska bir ajanin alani
ve bayragi biz ACMIYORUZ.

**Done looks like**: gercek kanal sesi (part 24) uzerinde `master_audio`, pay 0,2 ile
sozlesmeyi ucuncu denemeye kalmadan tutturuyor; pay 0,0 ile bugunku hatayi aynen veriyor.

**PROOF**:
```
python -m pytest tests/ -q
```
Yeni test `tests/test_master_true_peak_margin.py` (ffmpeg gerektirir, SKIP ETMEZ):
- Enjekte edilmis olcumle, gercek tasma raporlama cozunurlugunden BUYUK oldugunda
  (gercek 0,15 / raporlanan 0,1) pay=0,0 dongusu uc denemede de kalir; pay=0,2
  dongusu ikinci denemede gecer. Iki yon de ayni testte kanitlanir.
- Pay=0,0 ile uygulanan limiter tavanlari, degisiklikten ONCEKI diziyle
  (-1,0 / -1,1 / -1,2) birebir ayni olur.
- Ilk denemede gecen bir sinyalde pay ne olursa olsun ayni tavan kullanilir
  (pay yalnizca BASARISIZ denemeden sonra devreye girer).
- `bible.master_true_peak_margin_db`: alan yoksa 0,0; negatif, sonsuz veya
  sayi olmayan deger `ValueError`.
- `tests/test_master_true_peak.py` ve `test_master_true_peak_adversarial.py`
  TEK SATIR degismeden yesil kalir (uc deneme ve 3,1 dB telafi varsayimlari korunur).

---

## ROCK 2: Ses masteri acilir (master_lufs)

**Neden**: 8-11 dB eksik ses, anlatim tabanli bir kanalda icerigin kendisini yok
ediyor. YouTube sessiz videoyu YUKSELTMEZ, sadece yuksek olani kisar.

**Dosya**: `galactic_experience/event-horizon/bible.json`, `series` blogu:
```json
"master_lufs": -14
```

**Zorunlu yan degisiklik**: `tests/test_rocka_audio_master.py::test_only_unnatural_lab_has_master_lufs`
su an filoda `master_lufs` tanimli TEK serinin `unnatural-lab` oldugunu iddia ediyor
ve bu degisiklikle KIRILIR. Test, tam olarak `unnatural-lab` ve `event-horizon`
beklemeye guncellenir. `sentinal_ihsan` altindaki hicbir dosyaya dokunulmaz.

**Risk (durustce)**: mastering hatasi gercek (unnatural-lab part 33 kaniti).
ROCK 0 olmadan bu risk "kanal susar"dir. ROCK 0 ile risk "o bolum 3 kez denenir,
sonra insana devredilir ve kuyruk ilerler" seviyesine iner. ROCK 2, ROCK 0 ve ROCK 1 olmadan ASLA yayina alinmaz: ROCK 1'in payi olmadan
olculen ornek mastering'i gecemiyor.

**PROOF**:
```
python -m pytest tests/ -q
```
Yeni test `tests/test_galactic_master_lufs.py` (ffmpeg gerektirir, SKIP ETMEZ):
- `event-horizon` bible'inda `master_lufs == -14.0`; `flashpoints` ve `next-stop`
  hala `None` (kapsam nobetcisi).
- event-horizon'un gercek teslimat karisimini taklit eden miks uretilir: ayirt
  edilebilir bir konusma sinyali (300-3400 Hz bandi) + altinda bilinen bir seviyede
  muzik yatagi, toplam yaklasik -24 LUFS. `produce` yolunun kullandigi
  `ffmpeg_tools.master_audio(target_i=-14, target_tp=-1.0, target_lra=11.0,
  true_peak_margin_db=0.2)` calistirilir ve CIKTI olculur:
  integrated -14 +/- 0,5 LUFS, true peak <= -1,0 dBTP.
- **Anlatim/muzik ORANI korunur**: master oncesi ve sonrasi, konusma bandi ile muzik
  bandinin RMS farki 1 dB'den fazla degismemeli. Tur 2 hakli olarak "konusma bandi
  RMS'i tek basina muzikten de yukselebilir" dedi; olculen sey artik seviye degil ORAN.
- Anlatim tek basina da yukselmis olmali: master sonrasi konusma bandi RMS'i master
  oncesine gore en az 6 dB yuksek.
- Bu test bir INSAN dinleme kontrolunun yerine gecmez. Level 10 incelemesinde
  yayinlanmis part 24'un master oncesi ve sonrasi ses ornekleri Ihsan'a gonderilir;
  kulakla onay ONUN.

---

## ROCK 3: Ekran kunyesi acilir (fail-closed)

**Neden**: Bu seride hicbir ekran yazisi yok; sessiz izleyici hicbir sey okuyamiyor.
`core/ffmpeg_tools.py:1362` `title_card_overlay` HAZIR ve `shadowedhistory` kullaniyor.

**Uc tuzak, ucu de kapatilacak**:

1. **Yil sarti**: `series/replenish.py:1372-1384` her seride kunyeye 4 haneli YIL sart
   kosuyor. Uzay kanalinda her plan reddedilirdi.
   Cozum: yeni alan **`bible.series.title_card.year_required`** (bool, varsayilan
   True). Cfg (`auto_replenish`) yerine bible'da, cunku `title_card` yapilandirmasi
   zaten orada ve `bible` degiskeni dogrulama noktasinda kapsamda
   (`if bible.slug == "flashpoints"` satiri onu kullaniyor). `auto_replenish` icine
   yeni anahtar EKLENMEZ: replenish satir 145 ve 216'daki listeler beyaz liste degil,
   **fixed-frame ve strict-validation tetikleyicileridir**; oraya anahtar eklemek
   alakasiz dogrulamayi tetikler.
2. **Prompt celiskisi**: `tc_shape` (satir ~652) ve `tc_rule` (satir ~695) modelden
   "place and year exactly as the CREATIVE BRIEF instructs" istiyor.
   `year_required` False iken ikisi de yilsiz varyanta gecer: `title` = gok cisminin
   adi, `subtitle` = anomalinin kendisi.
3. **Iki katli fail-open**: `title_card_overlay` ffmpeg hatasinda girdiyi KOPYALAYIP
   basarili donuyor (`core/ffmpeg_tools.py:1431-1436`), ustune `produce.py:2107-2109`
   istisnayi yutup yayina devam ediyor. Yani kunye hic cizilmeden "kunye eklendi"
   yolu tamamlanabilir.
   Cozum: `title_card` mevcut **`required_layers`** sozlugune eklenir. Sozluk IKI
   YERDE tanimli ve IKISI DE guncellenir:
   - `series/produce.py:1359` `{"hook_teaser", "music", "native_audio"}`
   - `series/preflight.py:122` ayni kume (tur 2 bulgusu: yalniz produce'u guncellemek,
     preflight'in her yeni event-horizon planini "bilinmeyen required_layers" diye
     reddetmesine yol acardi)

   event-horizon `"required_layers": ["title_card"]` alir. Zorunlu katman modunda:
   `title_card_overlay` kopyalama-yedegine DUSMEZ, hata firlatir; `produce.py`
   istisnayi yutmaz, `None` dondurup bolumu durdurur.
   Zorunlu degilken bugunku fail-open davranisi AYNEN korunur (uc seri korunuyor).
4. **Ucretli isten ONCE dogrulama**: `title_card` zorunlu katmansa ve plan'da
   `title_card.title` yok/bos ise, `preflight` bunu kredi harcanmadan reddeder.
   Bugun ne preflight ne produce bunu kontrol ediyor; zorunlu katman bayragi tek
   basina bos bir kunyeyi yakalamaz, sadece cizim hatasini yakalar.
5. **Kisayol korunur**: `flashpoints/bible.json` `"title_card": true` (bool kisayolu)
   kullaniyor. `bible.title_card` bunu `{"enabled": True}` yapiyor ve
   `.get("year_required", True)` dogru sonucu veriyor. Bu kisayol BOZULMAZ ve test edilir.

**Tek uzunluk sozlesmesi** (`year_required` False olan seriler icin):
`title` <= 40 karakter, `subtitle` <= 48 karakter. Bu, prompt'un zaten istedigi
olculerdir; uretim, elle-plan dogrulamasi ve testler AYNI siniri uygular.
Eski seriler (`year_required` varsayilan True) bugunku 60 karakter sinirinda kalir.

**Dosyalar**:
- `series/replenish.py`: yil kontrolu `bible.title_card.get("year_required", True)`
  ile kosullu; prompt sekli kosullu; normalizasyon 40/48 sinirini uygular.
- `series/bible.py`: `title_card` property'si `year_required` alanini gecirir;
  bool olmayan deger `ValueError`.
- `core/ffmpeg_tools.py`: `title_card_overlay(..., required: bool = False)`;
  True ise kopyalama yedegi yok, `RuntimeError`.
- `series/produce.py`: `required_layers` bilinen kume + zorunlu kunye fail-closed.
- `galactic_experience/event-horizon/bible.json`:
  `"title_card": {"enabled": true, "duration": 2.0, "year_required": false}`,
  `"required_layers": ["title_card"]`
- `galactic_experience/event-horizon/series.json`: `auto_replenish.title_card: true`,
  `brief` icine Ingilizce kunye kurali (title = gok cismi adi, subtitle = anomali).

**NON-GOAL**: `fact_captions` bu turda acilmaz.

**PROOF**:
```
python -m pytest tests/ -q
```
Yeni test `tests/test_title_card_year_exemption.py`:
- `year_required: false` bible'inda yilsiz kunye KABUL edilir.
- Ayni bible'da 41 karakterlik title ve 49 karakterlik subtitle REDDEDILIR;
  bos subtitle REDDEDILIR.
- `year_required` HIC verilmemis bible'da yilsiz kunye REDDEDILIR (geriye uyum nobetcisi).
- `flashpoints` cag capasi istisnasi hala calisir.
- `year_required: "false"` (string) `ValueError` verir.
- `flashpoints`'in `"title_card": true` bool kisayolu calismaya devam eder.
- `required_layers: ["title_card"]` olan event-horizon plani `preflight`'tan GECER
  (iki sozluk de guncellendigi icin); `title_card` alani bos olan plan preflight'ta
  kredi harcanmadan REDDEDILIR.
- `flashpoints`, `footnotes` ve `drowned-history` icin bugun gecen ornek planlar
  degisiklikten sonra da AYNEN gecer.

`tests/golden/fixedframe_prompts.json` icinde `event-horizon` icin bir prompt golden'i
var (`tests/test_fixedframe.py:35`). Brief ve kunye prompt'u degistigi icin YALNIZ
event-horizon'un beklenen prompt'u guncellenir; diger her serinin beklentisi bit bit
korunur ve test bunu dogrular.

Yeni test `tests/test_title_card_required_layer.py` (ffmpeg gerektirir, SKIP ETMEZ):
- Gercek bir kisa video uretilir, `title_card_overlay(required=True)` bozuk bir yazi
  tipi/parametreyle cagrilir: kopyalama yedegi DEVREYE GIRMEZ, istisna yukselir.
- Basarili cizimde cikti karesinin **ust ucte birinden** piksel ornegi alinir ve
  girdiye gore belirgin parlaklik farki oldugu dogrulanir (yazi gercekten cizildi).
- `required=False` cagrisinda bugunku fail-open kopyalama davranisi AYNEN korunur.

---

## ROCK 4: Kusurlu bolum yayini durur (yalniz event-horizon)

**Neden**: son alti bolumun ucu kusurlu ve ucu de yayinlandi. part 29 anlatimsiz cikti.

**Dosyalar ve degisiklikler**:

1. `series/produce.py`
   - `ProduceResult.reason_code` Literal alanina ve `__post_init__` kontrol kumesine
     `"EPISODE_DEGRADED"` eklenir. Bugun bu deger `ValueError` firlatiyor, yani
     tipli hata NESNESI hic kurulamiyor.
2. `series/series_runner.py`
   - `migrate_malformed_approval_holds` icindeki `valid_codes` kumesine
     `"EPISODE_DEGRADED"` eklenir.
   - Kapi, sonuc normalizasyonundan HEMEN SONRA (satir ~772, `new_state_machine`
     kontrolunden once) durur: bible bayragi True ve sonuc `ok` ama coherence
     `degraded` ise, sonuc tipli bir `qc_hold` / `EPISODE_DEGRADED` hatasina cevrilir.
     `_publish_part` oncesine koymak YETMEZ: orasi `mark_produced`, onay modu ve
     `--no-publish` dallarindan SONRA gelir.
   - `EPISODE_DEGRADED` `_NON_RETRYABLE_REASON_CODES` ve `_INFRA_REASON_CODES`
     kumelerine EKLENMEZ; icerik sinifinda kalir (3 deneme, sonra `needs_human`).
   - Telegram uyarisi neyin eksik oldugunu yazar (loop, anlatim, sure, dusen roller).
3. `series/bible.py`
   - Yeni property `block_degraded_publish`. **Sadece JSON `true` acar.**
     Alan yoksa False. Bool olmayan deger (`"false"`, `1`, `"true"`) `ValueError`
     firlatir; boylece yazim hatasi sessizce uretimi durdurmaz.
4. `galactic_experience/event-horizon/bible.json`
   - `"block_degraded_publish": true`
   - `"duration_band": [14, 22]`
     Gerekce: olculmus saglikli bant 16,62-19,62; bozuklar 11,02-11,10. Alt sinir 14
     bozuklari yakalar, saglikliyi yakalamaz. Ust sinir 22, olculmus azami 19,62'nin
     uzerinde 2,4 saniye pay birakir (3 cekim x 6 sn = 18 sn tabani, arti anlatimin
     son cekimi gerdigi olculmus 1,6 sn). 26 icin hicbir kanit yoktu, dusuruldu.
5. **Olculemeyen sure** de kapiya takilir: event-horizon icin `degraded` olmamasi
   YETMEZ, `duration_in_band is True` sarti aranir. `duration_in_band is None`
   (sure okunamadi) yeniden denenebilir hold sayilir; aksi halde olculmemis bir
   dosya kapidan gecerdi.

**Kabul edilen maliyet (acikca)**: son alti bolumun ucu bu kapiya takilirdi. Bu kapi
acikken o bolumler yayinlanmak yerine yeniden uretilir (3 denemeye kadar), yani kredi
harcamasi artar ve yayin temposu duser. Ihsan bunu bilerek secti: az ama saglam video.

**NON-GOAL**: `qc.min_shots` / `require_all_shots` EKLENMEZ; dusen cekim zaten
`arc_roles_missing` uzerinden `degraded` yapiyor.

**PROOF**:
```
python -m pytest tests/ -q
```
Yeni test `tests/test_degraded_publish_gate.py`:
- `ProduceResult("qc_hold", reason_code="EPISODE_DEGRADED")` kurulabiliyor
  (bugun `ValueError` veriyor) ve tam kod alani beklenen kumeyle esit.
- Bayrak True + degraded coherence -> `_publish_part` HIC cagrilmaz, part `qc_retry`,
  `retry_count` artar.
- Bayrak True + `duration_in_band is None` -> yine hold (olculmemis dosya gecmez).
- Bayrak True + saglikli coherence -> yayin normal ilerler.
- Bayrak YOK (varsayilan) + degraded coherence -> yayin ESKISI GIBI ilerler
  (uc kanali koruyan nobetci).
- Uc basarisiz denemeden sonra `needs_human` ve kuyruk ilerler.
- `block_degraded_publish: "true"` (string) `ValueError`.

---

## ROCK 5: Baslik kalibi anomali vaat eder + kuyruk yenilenir

**Neden**: basliklar konu bildiriyor, merak yaratmiyor. Filodaki tek basarili kanal
(`sentinal_ihsan`, 1.292 medyan) "This X Is NOT Supposed To Y" kalibini kullaniyor:
konu degil ANOMALI vaat ediyor. Bu, Ihsan'in acik karari.

**Dosyalar ve degisiklikler**:

1. `galactic_experience/event-horizon/series.json`
   - `auto_replenish.title_style`: mevcut dort kalibin yanina iki anomali kalibi:
     (5) `"This <Subject> Should Not <verb>. It Does."`
     (6) `"This|These <Subject> <verb> <consequence>"`
     Emoji ve hashtag yasagi, en fazla bir ALL-CAPS kelime kurali AYNEN korunur.
     Tur 2 hakli olarak asagidaki dort basligin ilan edilen kaliplara UYMADIGINI
     soyledi; kalip (6) bu yuzden hem tekil hem cogul ozneyi ve duz eylemi kapsayacak
     sekilde yazildi ve dort baslik da (6)'ya uyacak sekilde duzeltildi.
   - `brief` baslik maddesi guncellenir (fakt ve aile rotasyonu kurallari degismez).
2. `galactic_experience/event-horizon/plans/part32.json` ... `part35.json`
   Konu, fakt, synopsis, narration, cekim promptlari, `family`, `seed_id` ve
   `doctrine_sha256` DEGISMEZ. Sadece `episode.title` degisir ve `title_card` eklenir:

   | part | yeni `episode.title` | `title_card.title` | `title_card.subtitle` |
   |---|---|---|---|
   | 32 | `This Star Is EATING Its Own Planet` | `WASP-12b` | `Its star is devouring it` |
   | 33 | `These Galaxies Are Leaving Us Forever` | `Cosmic expansion` | `Distant galaxies leave our sky` |
   | 34 | `This Star Rips ATOMS Apart` | `Magnetar` | `It pulls atoms apart` |
   | 35 | `This Moon Leaks Its OCEAN Into Space` | `Enceladus` | `Its ocean escapes into space` |

   Hepsi <= 60 karakter baslik, <= 40 karakter kunye basligi, <= 48 karakter alt yazi,
   en fazla bir ALL-CAPS kelime, emoji ve hashtag yok.

   **Iki baslik tur 2'nin dogruluk itirazi uzerine degistirildi:**
   - part 32 onceki oneri "This Planet Should Not Be Egg-Shaped" idi. YANLIS: yumurta
     sekli gelgit kuvvetlerinin BEKLENEN sonucu, NASA bu gezegeni zaten "egg-shaped"
     diye tanitiyor. Gercek anomali yildizin gezegeni yutmasi; baslik ona cevrildi.
   - part 33 onceki oneri "One Day the Sky Will Be EMPTY" idi. ABARTILI: bolumun kendi
     onermesi Yerel Grup'un KALDIGI. Baslik ve kunye artik "distant galaxies" diyerek
     kendi faktiyla celismiyor.
3. `series/preflight.py`
   - Kunye dogrulamasi replenish'ten paylasilan bir fonksiyona cikarilir ve preflight
     de ayni fonksiyonu cagirir. Bugun preflight `title_card` alanini HIC dogrulamiyor;
     elle duzenlenmis bozuk bir kunye uretime kadar fark edilmezdi.

**NON-GOAL**: `title_patterns` regex zorlamasi EKLENMEZ (alti aile uzerinde fullmatch
genis bir yuzey). Issues listesine gider.

**PROOF**:
```
python -m pytest tests/ -q
python -c "from series.preflight import main" 
```
Yeni test `tests/test_galactic_queue_titles.py`:
- part 32-35 planlarinin her biri `series.preflight` dogrulamasindan GECER
  (sadece JSON parse etmek yetmez).
- Her plandaki `title_card.title` <= 40, `.subtitle` <= 48 karakter ve bos degil.
- Her `episode.title` VE her `title_card.title` / `title_card.subtitle` yukaridaki
  tablodaki tam metinle BIREBIR esit; emoji/hashtag icermez, baslik en fazla bir
  ALL-CAPS kelime tasir.
- Her baslik `title_style` kalip (5) veya (6) ile tutarli (dogal dil kontrolu degil:
  test "This" ya da "These" ile basladigini ve bir eylem tasidigini dogrular).
- Her planda `doctrine_sha256`, `family`, `seed_id`, `synopsis`, `narration` ve
  `shots` DEGISMEMIS: karsilastirma **9eec629 temel commit'ine** sabitlenir
  (`git show 9eec629:galactic_experience/event-horizon/plans/partNN.json`), belirsiz
  bir "onceki hal"e degil.

---

## Bagimlilik sirasi

ROCK 0 -> ROCK 1 -> ROCK 2 -> ROCK 3 -> ROCK 4 -> ROCK 5.
ROCK 0 bir onkosuldur: ROCK 2 ve ROCK 4 yeni hold yollari aciyor ve v1 durum
makinesinde her hold kanali susturur.

## DOKUNMA listesi

- `shadowedhistory/**`, `aimagine/**`, `AImagine-Fear/**`, `sentinal_ihsan/**`:
  baska ajanlarin alani. Tek satir bile degismez. (`tests/test_rocka_audio_master.py`
  bir TEST dosyasidir, `sentinal_ihsan/` altinda degildir; guncellenmesi serbesttir.)
- `core/ffmpeg_tools.py`: `master_audio` ve `fact_captions_overlay` davranisi degismez.
  `title_card_overlay` yalniz yeni `required` bayragiyla genisler; bayraksiz cagri
  bugunku davranisi bit bit korur.
- `galactic_experience/event-horizon/published.json`, `series_log.*`, `qc_log.jsonl`:
  gecmis kayit, dokunulmaz.
- `galactic_experience/planetfall`, `ava-voyage`: duraklatilmis, oyle kalsin.
- Cozunurluk 1080x1920 ve fps 30 dogru, dokunulmaz.
- `doctrine_sha256` pinleri degismez.

## Bu turda YAPILMAYANLAR (Issues listesine)

- `fact_captions` katmani.
- `title_patterns` regex zorlamasi.
- Cekim basina 4 saniye tavani / 5-7 saniyede pattern interrupt: `shot_seconds` 6'dan
  4'e inmek cekim sayisini ve kredi maliyetini artirir, ayri bir maliyet karari.
- part 31'in son cekiminin 8,48 saniye surmesi.
- Diger uc kanalin `master_lufs` eksigi (baska ajanlarin alani). ROCK 1'in
  limiter duzeltmesi onlarin yolunu da acar ama alanlarini biz ACMIYORUZ.
- Diger serilerin `state_machine_version` 1'de kalmasi: ayni sessiz-susma riski
  onlarda da var, ama kapsam disi.
- `_budget_failure` muhasebe OKUNAMADIGINDA da `BUDGET_EXHAUSTED` deyip part'i
  terminal yapiyor ve kuyrugu ilerletiyor (ortak motor, `unnatural-lab`'i da etkiler).
  event-horizon'da bugun tetiklenmiyor (300 asgari / 900 kalan olculdu).
- `migrate_malformed_approval_holds` bir kaydi `needs_human` yapip `next_part`
  ilerletmezse kuyruk sessizce durur; event-horizon'da su an boyle kayit yok.
- ffmpeg `ebur128` ozeti true-peak'i 0,1 dB cozunurlukte raporluyor; -1,04 dBTP
  "-1,0" olarak gecebilir. ROCK 1'in payi bu marji pratikte kapatiyor ama olcumun
  kendisi hala kaba; yuksek cozunurluklu dogrulama ayri bir is.
- Retention ve CTR verisi: YouTube Studio gerekiyor.
