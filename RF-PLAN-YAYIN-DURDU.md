# RF-PLAN , Shadowed History 4 gundur neden yayinlamiyor + kalici cozum

**Tarih:** 2026-08-31 · **Surucu:** Claude (Visionary) · **Inceleyen:** Codex (Integrator)
**Revizyon:** r3 (Codex tur-1 ve tur-2 bulgulari islendi)
**Kapsam:** shadowedhistory/flashpoints hatti (kanal: @shad0wedhistory357). unnatural-lab
ayni tuzakta ama bu cevrimin kapsaminda degil (bkz. Bolum 5).

## CORE FOCUS (tek cumle)

Shadowed History her gun 1 video yayinlasin; yayin durursa **24 saat icinde** Ihsan bunu
Telegram'dan ogrensin , "kosu yesil" degil "YouTube'a video cikti" olcusuyle.

---

## 1. Teshis , kanit zinciri (hepsi bu makinede olculdu)

### Olgu 0 , son gercek yayin
`shadowedhistory/flashpoints/series.json` part 20: `published_at 2026-08-27T00:12:08Z`.
Part 21: `{"status": "awaiting_approval", "hold_reason": "quota"}` , video yok, release yok,
subtitle yok. `published.json` son kaydi da part 20. Kanal 4 gundur sessiz.

### Olgu 1 , tetikleyici: Gemini QC kotasi tukendi (2026-08-29 03:03 UTC)
Kosu 33229978336: cekim 1 QC GECTI, cekim 2 icin
`429 RESOURCE_EXHAUSTED ... limit: 20, model: gemini-3.7-flash`
(quotaId `GenerateRequestsPerDayPerProjectPerModel-FreeTier`). Birincil `gemini-2.5-flash`
ve yedek `gemini-flash-latest` (= gemini-3.7-flash) ikisi de 429; iki review retry de 429.
QC zorunlu kapi oldugu icin fail-closed durdu , **dogru karar, hata degil.**
`qc_log.jsonl` son satiri: `{"event":"qc_hold","episode":21,"shot":2,"reason":"quota"}`.

### Olgu 2 , asil kusur: hold durumu CIKISI OLMAYAN bir kuyu
`series/series_runner.py:492-499` , `qc_hold` gelince part `awaiting_approval` +
`hold_reason` yaziliyor. Bu part'in `release_tag`, `video`, `approval_msg_id` alanlari YOK ,
cunku bolum hic tamamlanmadi. Sonuc:
- `series_runner.py:393` her sonraki kosuda `awaiting_approval` gorup **uretmeden** cikiyor:
  `"Part 21 zorunlu QC/onay bekliyor , uretim ve yayin atlandi."`
- `series/approver.py:122` kart yenilemeye calisiyor; `_download_release(None)` bos tag'de
  aninda `None` donuyor -> `"Part 21: release indirilemedi, kart yenilenemedi."`
- Onaylanacak video olmadigi icin Ihsan onay verse bile yayin olamaz.

**Bu bir kilit degil, kalici olum durumu: insan elle JSON'a dokunmadan cikis yok.**

**Ayni olum durumunun ikinci kapisi:** `series_runner.py:526-533` onay modunda
`release_tag`/`approval_msg_id` `None` olsa bile `awaiting_approval` yaziyor , Telegram
kapali/arizali oldugu bir gunde ayni kuyu QC'den bagimsiz olarak da kazilabilir.

### Olgu 3 , tek uyari mesaji Telegram'da patladi
Ayni kosu, 03:04:26:
`Telegram sendMessage hata: Bad Request: can't parse entities: Can't find end of the entity starting at byte offset 92`

Kanit (kendi olctum): `series_runner.py:497-500` alarm metninin 92. bayti,
`Durum awaiting_approval` icindeki **alt cizgi**. `notifier.send_message`
`parse_mode="Markdown"` ile gonderiyor (`series/notifier.py:51`); Telegram kapanmamis
italik entity sanip **tum mesaji rediyor**. "Kanal durdu" alarmi, kendi metnindeki
formatlama hatasi yuzunden hic gitmedi. Hata yalniz log'a ERROR yazildi, kosu 0 ile bitti.

### Olgu 4 , yesil isik yalan soyluyor
`.github/workflows/flashpoints.yml` "Uretim sonucunu kaydet" adimi `steps.produce.outcome`'u
yaziyor. Atlama yolu `return True` oldugu icin outcome=success:
`last_run.json = {"ts":"2026-08-30T22:52:56Z","outcome":"success",...}`.
Akilli_Watchdog `config.py:191-197` tam da bu dosyaya bakiyor (`timestamp_field: ts`,
`outcome_field_required: true`, `window_hours: 26`) , nobetci "kosu oldu mu"yu olcup
"video cikti mi" saniyor. Watchdog'un kendi yorumu (config.py:173-175) bunu yasakliyor:
*"Workflow sonucu veya dosya mtime'i kanit sayilmaz"* , uygulama ilkeyi ihlal ediyor.
53 saniyelik "basarili" kosular (30 Ag 22:52, 29 Ag 22:42) tam olarak budur.
**Ek olcum:** watchdog cron'u gunde TEK kosu (`0 5 * * *`).

### Olgu 5 , tekil kaza degil, sinif
`sentinal_ihsan/unnatural-lab` part 23: `{"status":"awaiting_approval",
"hold_reason":"reference object could not be downloaded"}` , ayni tuzak, farkli altyapi
arizasi (`produce.py:1262`). O kanal da 28 Agustos 21:06Z'den beri sessiz.

### Olgu 6 , `hold_reason` siniflandirici olarak yetersiz (Codex tur-2 duzeltmesi kabul)
Onceki revizyonda "reason None gelebilir" yazmistim , **yanlis**: `produce.py:1471-1474`
ve `1618-1621` bos reason'i `f"mandatory QC unavailable for shot {n}"` ile dolduruyor,
digerleri (514 ses masteri, 1262 referans, 1864 hata) zaten reason tasiyor. Yani alan hep
dolu ama **serbest metin** ve genel yedek metin nedeni siliyor. Ayrica "icerik kotu" diye
ayri bir `qc_hold` dali YOK , kotu icerik regen/fail yoluna gidiyor. Sonuc: siniflandirma
metne degil **tipli neden koduna** dayanmali.

### Olgu 7 , odenmis klip hala canli
`series_log.csv` ep21 cekim-1 satirindaki Kie temp URL'i bugun hala **HTTP 200, 5.8 MB**
(Last-Modified 29 Ag 02:59). 105 kredilik cekim teknik olarak kurtarilabilir; cekim 2
tutuldugu icin CSV'ye hic yazilmadi. Bugunku kodda "kayitli URL'den devam et" yolu yok.

### Olgu 8 , asil yapisal sorun: QC kotasi FILO ORTAK, flashpoints kuyrukta EN SON
`qc_log.jsonl` defterlerinden cikardigim gun x model x sonuc sayimi:

| gun | model | ok | 429 | error |
|---|---|---|---|---|
| 2026-08-28 | gemini-2.5-flash | 29 | **26** | 5 |
| 2026-08-28 | gemini-flash-latest | 6 | 0 | 7 |
| 2026-08-29 | gemini-2.5-flash | 11 | **22** | 3 |
| 2026-08-29 | gemini-flash-latest | 2 | **9** | 9 |

Hat bazinda gunluk cagri: 28 Ag'da unnatural-lab tek basina 122, 29 Ag'da event-horizon 52 +
flashpoints 40. **Yani kota flashpoints'e sira gelmeden tukeniyor.**
Cron sirasi: next-stop 13:20 -> from-scratch 14:30 -> event-horizon 16:30 -> unnatural-lab
18:30 -> **flashpoints 20:30 UTC**. Shadowed History her gun kuyrugun sonunda; ortak kota
tukendiginde **yapisal olarak ilk kurban o**. Ayrica Gemini gunluk kotasi UTC'de degil
**Pasifik gece yarisinda** sifirlaniyor (Codex tur-2, resmi rate-limit dokumani) , 20:30 UTC
kosusu Pasifik gununun sonuna denk geliyor, yani tankin en bos ani.

**Bugunku canli olcum (2026-08-31 ~13:05 PT):** QC anahtariyla `gemini-2.5-flash`
`generateContent` cagrisi **200 OK** dondu , birincil modelde su an kota var.
`gemini-flash-latest` probe'u iki denemede de baglanti kuramadi (HTTP 000, sonucsuz).

### Ozet nedensellik
Filo ortak QC kotasini gun icinde tuketti (28-29 Ag) -> kuyrugun sonundaki flashpoints
429 yedi -> zorunlu QC fail-closed durdu (dogru) -> hold durumu kurtarilamaz yazildi
(kusur A) -> tek alarm Markdown hatasindan gitmedi (kusur B) -> kosu yesil raporladi,
gunde-bir bakan nobetci yesil gordu (kusur C) -> 4 gun sessizlik.

---

## 2. 24 saat garantisi nasil kuruluyor (mimari karar)

Ucu birden sart, cunku her biri tek basina delik:
1. **Birincil , hattin kendi alarmi (aninda).** `held`/`failed` sonucu Telegram'a ULASAN
   mesaj (ROCK 2 teslimati garantiler). Gecikme: dakikalar.
2. **Ikincil , kosu hic baslamazsa.** `series_runner`'dan ONCEKI adimlar (checkout, pip,
   ikmal) patlarsa birinci katman hic calismaz. Workflow'a `if: always()` calisan bagimsiz
   bir "kosu basarisiz" alarm adimi eklenir; alarm da gidemezse job KIRMIZI biter ve
   GitHub'in kendi bildirimi ikinci kanal olur.
3. **Yedek , nobetci.** Watchdog gunde 1 kez baktigi icin 20 saatlik esikle bile en kotu
   durumda ~44 saat sonra bagirir , 24 saat sozunu tutmaz. Bu yuzden bu cevrimde nobetci
   frekansi da artar: **esik + azami yoklama araligi <= 24 saat** (or. 12 saatlik esik +
   6 saatte bir yoklama).

---

## 3. Rock'lar (bagimlilik sirasi)

### ROCK 0 , Acil kurtarma: bugun video ciksin  [elle, ~30 dk]
**Ne:** flashpoints part 21 durumunu `planned`'a dondur (`hold_reason` sil), sonra
`workflow_dispatch` ile hatti tetikle. `plans/part21.json` mevcut.
**Zamanlama:** birincil QC modeli su an cevap veriyor (Olgu 8), yani beklemeye gerek yok;
bugunun filo kosulari (13:20-18:30 UTC) bittigi icin kota en rahat halinde. Ilk deneme
429 alirsa Pasifik gece yarisi sonrasina birakilir.
**Maliyet (bilerek kabul):** ~210 Kie kredisi yeniden harcanir; cekim 1 kurtarilabilirdi
ama o yol kodda yok (Olgu 7). flashpoints'in `bible.json`'inda seri tavani YOK ve
`credits_ledger.episode_spend`'de kaydi YOK , yani her deneme taze 900 rezervasyon alir,
kalici bir bolum tavani retry'i sinirlamiyor (ROCK 1 bunu bagliyor).
**Done:** part 21 `platforms_ok` icinde `youtube`, `published.json` son kaydinda
`results.youtube` gecerli bir 11 karakterlik YouTube kimligi ve o video
`UCUdp0KLBh4EeeSgVbwS_DhA` kanalinda gorunuyor.
**Proof (yayin kaniti, kosu yesili degil):**

    python -c "import json,re;d=json.load(open('shadowedhistory/flashpoints/published.json',encoding='utf-8'));r=d[-1];v=r['results']['youtube'];print(r['part'], v, bool(re.fullmatch(r'[A-Za-z0-9_-]{11}', v or '')))"
    # 21 <id> True  ,  ardindan video https://youtu.be/<id> ile kanalda dogrulanir

### ROCK 1 , Altyapi arizasi != icerik reddi: kurtarilabilir hold
**Ne:**
1. `ProduceResult` hold'lari **tipli neden koduyla** doner (`QUOTA`, `REF_DOWNLOAD`,
   `FRAME_EXTRACT`, `AUDIO_MASTER`, `UNKNOWN`) , serbest metne bakan siniflandirma YOK
   (Olgu 6). Varsayilan **retryable**; retry edilmeyecekler acik listede.
2. Retryable hold -> part `status="qc_retry"`, `retry_count`, `first_held_at`,
   `retry_spent`. Sonraki kosu bu durumu gorunce **yeniden uretir**. Ust sinir 3 deneme
   VE kalici bir part-basi kredi butcesi (denemeler arasi toplam; flashpoints'te bugun
   boyle bir tavan olmadigi icin bu rock onu getiriyor).
3. 3. denemeden sonra `status="needs_human"`; `run_next` bu durumu da **acikca bloke eder**
   (bugun yalniz `awaiting_approval` bloke ediyor) ve ROCK 2 alarmi gider.
4. **Sinir:** `awaiting_approval` bundan boyle YALNIZ `video` + `release_tag` +
   `approval_msg_id` UCU de doluyken yazilir; biri eksikse retryable failure
   (Olgu 2'nin ikinci kapisi kapanir).
**Done:** kota 429'u alan hat ertesi gun kendiliginden toparlanir, insan gerekmez.
**Proof:** `python -m pytest tests/test_hold_recovery.py -q` , durum makinesi testi:
hold -> retry -> yayin; yayin ancak `platforms_ok` icinde `youtube` VE gecerli YouTube
kimligi varken "published" sayilir; uretici/yukleyici cagri sayaci dogrulanir; 3 denemeden
sonra `needs_human`; 4. kosu ne uretir ne yukler; kredi butcesi asilirsa retry durur;
video/release/kart eksikliklerinin her biri icin ayri vaka `awaiting_approval` YAZMAZ.

### ROCK 2 , Alarm kirilmasin (teslimat garantisi)
**Ne:** `series/notifier.py` + kosu iskeleti:
1. Dinamik metinde Markdown kacisi (kritik alarmlarda parse_mode kullanmamak da kabul).
2. `can't parse entities` gelirse **tek** yeniden deneme parse_mode'suz.
3. `send_message` yapisal sonuc doner (`delivered`, `error`). Notifier `last_run.json`'a
   DOKUNMAZ.
4. **Alarm kutusu (outbox):** teslim edilemeyen KRITIK alarm dosyaya yazilir, durum
   commit'iyle kalici olur ve sonraki kosuda yeniden denenir; teslim edilene kadar kosu
   `outcome=failure` raporlar ve job kirmizi biter (GitHub bildirimi = ikinci kanal).
5. `if: always()` calisan bagimsiz "kosu basarisiz" adimi , `series_runner` hic
   calismadiginda da haber gider (Bolum 2, katman 2).
**Done:** icinde `_`, `*`, `[` gecen alarm her zaman ulasir; ulasmazsa hat kirmizi olur ve
alarm kuyrukta bekler.
**Proof:** `python -m pytest tests/test_notifier_entity_fallback.py -q` , sahte 400
"can't parse entities" -> ikinci cagri parse_mode'suz, `delivered=True`; ag hatasinda
`delivered=False`, outbox'a yazilir, sonraki kosuda yeniden denenir, kosu failure raporlar.

### ROCK 3 , Yesil isik gercek yayini olcsun  [once YALNIZ flashpoints]
**Ne:**
1. `run_next` bugun yalniz `bool` donuyor; workflow sonucu log'dan cikaramaz. Bu yuzden
   **tipli `RunResult`** (`action`, `part`, `platforms_ok`, `youtube_id`, `alert_delivered`)
   ve **tek atomik yazici** eklenir; workflow adimi log ayristirmaz.
2. `last_run.json` semasi korunur (`ts`, `outcome`, `raw_outcome`, `run_id`), uzerine
   geriye uyumlu alanlar eklenir: `action` (`published|noop|held|failed`),
   `last_youtube_publish_at`.
3. `action=published` **YouTube dogrulanmis** demektir (gecerli kimlik + `platforms_ok`
   icinde `youtube`). Yalniz Instagram/TikTok basarisi `failed` sayilir ve alarm gider ,
   ilerletme davranisi degismez, yalniz olcum ve alarm YouTube'a baglanir.
4. `noop` (seri tamamlandi / gunde-1 kilidi) ancak o gun KANAL duzeyinde YouTube yayini
   varsa `success` sayilir; yoksa alarm gider. No-op asla `last_youtube_publish_at`'i
   tazelemez.
5. Akilli_Watchdog: flashpoints hedefi `last_youtube_publish_at`'e bakar; **esik 12 saat,
   yoklama 6 saatte bir** (esik + yoklama <= 24 saat).
**Done:** bugunku senaryo tekrarlansa hat kirmizi olur, alarm gider, nobetci de 24 saatin
altinda gorur.
**Proof:** `python -m pytest tests/test_last_run_contract.py -q` , held kosu success
yazmaz; IG-only yayin `failed` olur; no-op kanal kaniti yoksa alarm uretir ve
`last_youtube_publish_at`'i ilerletmez. Watchdog tarafinda en kotu alarm suresi testi.

### ROCK 4 , QC kota tavani  [IHSAN KARARI GEREKIR , para]
**Ne:** Olcum zaten var (Olgu 8) ve tek satirlik gercek su: **filo gunde 100-150 QC cagrisi
yapiyor, yedek modelin ucretsiz gunluk tavani 20.** Secenekler:
- (a) QC projesinde faturalandirmayi ac. Tavanlar model/proje/katman bazli kalkmaz ama
  ucretli katmanda cok daha yuksektir; yaninda **harcama tavani** konur.
- (b) Cagri sayisini dusur: unnatural-lab'in 122 cagrilik retry firtinasi tek basina bir
  gunu yakti , retry politikasi ve audio QC ornekleme gozden gecirilir.
- (c) **Ayri PROJE + ayri anahtar** (ayni projede ikinci anahtar kotayi ARTIRMAZ; kota
  proje+model bazlidir).
- (d) Sira adaleti: flashpoints her gun kuyrugun sonunda; sira dondurulur ya da QC butcesi
  hat basina paylastirilir.
**Done:** gunluk talep, tavan ve secenek maliyeti masada; Ihsan secer.
**Proof:** `python tools/qc_call_census.py --days 7` , gun x hat x model x sonuc tablosu
(attempt_id ile eslesmis benzersiz denemeler; Olgu 8 tablosunu uretir).

---

## 4. Kapsam disi (bu cevrimde yapilmayacak)

- QC modelini degistirmek (ISSUES.md ROCK C2 karari: olcumsuz model degisimi yasak).
- 5 workflow icin sema migrasyonu , flashpoints kanitlandiktan sonra.
- Kalite kapisini gevsetmek. Fail-closed dogru davranis; sorun cikis yolunun olmamasi.
- `kie-uretim` concurrency / cron kaymasinin yeniden tasarimi.
- "Kayitli klip URL'inden devam et" optimizasyonu (Olgu 7).
- Yayin ILERLETME kuralini degistirmek (bugun herhangi bir platform yeter).

## 5. Ihsan'in karar vermesi gerekenler

1. **unnatural-lab part 23 de ayni sekilde cakili** (28 Ag'dan beri sessiz). Kurtarma
   flashpoints'ten sonra mi? Ek detay: o serinin `bible.json`'inda bolum tavani **800**
   ve defterde `unnatural-lab:23 = 436` yanmis gorunuyor, kalan 364 , 4 taze cekime
   yetmeyebilir; defter sifirlansin mi?
2. **ROCK 4 secimi:** (a) faturalandirma, (b) cagri azaltma, (c) ayri proje+anahtar,
   (d) sira adaleti , ya da bunlarin bilesimi.
3. ROCK 0 bugun mu tetiklensin? (Birincil QC modeli su an cevap veriyor.)

## 6. Riskler

- ROCK 1 yeniden uretim kredi harcar; 3 deneme + part-basi kalici kredi butcesi bagliyor.
  Bu butce bugun flashpoints'te YOK, rock onu getiriyor.
- ROCK 3 alan EKLER, alan degistirmez; watchdog eski `outcome`'u okumaya devam edebilir.
  Watchdog frekans degisikligi ikinci repoda, ayni cevrimde yapilmali.
- ROCK 0 bugun tetiklenirse gunde-1 kilidi baska bir hattin uretimini yarina itebilir.
- Alarm outbox'i durum commit'ine baglidir; persist adimi patlarsa alarm kuyrukta kalir ,
  bu yuzden teslim edilmemis alarm kosuyu KIRMIZI yapar (GitHub bildirimi yedek kanal).
