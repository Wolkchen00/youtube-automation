# RF-PLAN , Sentinal Ihsan kanalinin dirilisi + "yapmacik" sorununun kokunden cozumu

**Tarih:** 2026-09-01 · **Surucu:** Claude (Visionary) · **Inceleyen:** Codex (Integrator)
**Revizyon:** r6 (Codex tur 1-4: 71 bulgu · bagimsiz panel: 5 blocking · ROCK 0 canli sonucu)
**Not:** r6'da tum duzeltmeler rock GOVDELERINE islendi; r5'in EK bolumu kaldirildi,
kanitlar §8 defterine tasindi (Codex tur-4 yapisal bulgusu).
**Kapsam:** `sentinal_ihsan/unnatural-lab` hatti (kanal: @sentinalihsandaily,
`UC-Aht8VqAUMTUKYRQA3agYQ`). ROCK 2 ve ROCK 3 ortak motoru degistirir , patlama yaricapi
**12 workflow** `series_runner`'i cagiriyor, **5 workflow** `last_run.json` semasini yaziyor
(event-horizon, flashpoints, from-scratch, next-stop, unnatural-lab). Olculdu.

## CORE FOCUS (tek cumle)

Sentinal Ihsan her gun 1 video yayinlasin, videolar **izleyicinin tepki verdigi** kalitede
olsun (L/1k >= 30), ve yayin durursa Ihsan **24 saat icinde** haberdar olsun.

---

## 1. TESHIS , kanit zinciri (hepsi bu makinede, bugun olculdu)

### Olgu 0 , kanalin gercek durumu (YouTube'un kendi RSS'i, pipeline degil)
Son yukleme: **2026-08-28T21:05:46Z** , "Something Is WRONG With This LEMON" (part 22).
Bugun 2026-09-01 ~13:00 UTC -> **~3,8 gun / 91 saat sessiz.**
Ayni beslemede ikinci bir bosluk: 2026-08-23 -> 2026-08-28 arasi 5 gun.
Yani bu 10 gunde **ikinci** kesinti.

### Olgu 1 , tetikleyici: imgbb 4 dakika dustu (30 Agustos)
Kosu 33336374003 (`gh run view --log`), birebir:

    21:26:03 WARNING  QC: obje referansi indirilemedi (1/3, 503 Server Error:
             Service Temporarily Unavailable for url: https://i.ibb.co/SXPpVG4t/ep23-bar-of-soap.png)
    21:28:18 WARNING  QC: obje referansi indirilemedi (2/3, ... Read timed out.)
    21:29:04 WARNING  QC: obje referansi indirilemedi (3/3, ... Read timed out. (read timeout=30))
    21:29:04 ERROR    QC HOLD: [REFERENCE OBJECT] indirilemedi
    21:29:04 ERROR    Part 23 QC HOLD , durum awaiting_approval; yayin bloke edildi.

**Bugun ayni URL: HTTP 200, 1.858.201 bayt, 3/3 basarili.** Kanali 4 gundur durduran sey
**4 dakikalik gecici bir CDN kesintisi**. Kod: `series/critic.py:336-359`
(3 deneme, 0.25s+0.5s = ~1 sn toplam geri cekilme) -> `series/produce.py:1260-1263`.

### Olgu 2 , asil kusur: hold durumu CIKISI OLMAYAN bir kuyu
`series.json` part 23: `{"status": "awaiting_approval",
"hold_reason": "reference object could not be downloaded"}` , `video`, `release_tag`,
`approval_msg_id` **ucu de yok**. `series_runner.py:393` sonraki kosuda uretmeden cikar;
`approver.py:122` bos tag ile karti yenileyemez. **Insan elle JSON'a dokunmadan cikis yok.**

### Olgu 3 , tek alarm yine Telegram'da patladi
`series_runner.py:492-500` alarmi `_alert(f"⏸️ *{meta.base_title}* Part {n} ... Durum
awaiting_approval; ...")` , `notifier.py:51` kosulsuz `parse_mode="Markdown"`.
Sonuc: `can't parse entities: ... byte offset 89`. **Dun flashpoints'te teshis edilen
kusurun birebir aynisi** (orada byte 92).

### Olgu 4 , yesil isik yalan soyledi (kodda dogrulandi)
`series_runner.py:491-501`: `qc_hold` dalinin sonu **`return True`**. Workflow adimi
`steps.produce.outcome`'u yazdigi icin `last_run.json` =
`{"ts":"2026-08-30T21:29:04Z","outcome":"success",...}`. Nobetci bu dosyaya bakiyor.

### Olgu 5 , OLDURUCU DARBE: workflow GitHub'da KAPALI
`gh workflow list --all` -> `Unnatural Lab Daily   disabled_manually   316866393`
(diger 15 workflow `active`). `gh run list --workflow=unnatural-lab.yml` en yeni kosu
**2026-08-30T21:25:04Z**; 31 Ag ve 1 Eyl'de **hicbir kosu olusmadi**. Ayni gunlerde
next-stop, from-scratch, event-horizon, flashpoints kostu.
**Otomasyon yapmadi:** `Akilli_Watchdog/config.py:246-275` `QUOTA_SHED_LIST` = 4 proje,
`youtube-automation` yok; `QUOTA_SHED_APPROVED` varsayilani `"0"`.
**[Codex tur-1 kabul edildi]** Repo icinden kimin kapattigi **kanitlanamaz**; bu bir
CLARIFY'dir, ROCK 0 Ihsan'in onayina baglidir (Bolum 5, soru 1).

### Olgu 6 , DUNKU PLANIN ROCK 1/2/3'U HIC INSA EDILMEDI
`RF-PLAN-YAYIN-DURDU.md` tam bu olum durumunu tarif etti. Bugun olctum, yalniz ROCK 0 yapildi:

| dun soz verilen | bugunku gercek |
|---|---|
| `qc_retry`/`needs_human`/`first_held_at`/`retry_spent` | `series/`+`core/` icinde **sifir esleme** |
| notifier Markdown kacisi + fallback + outbox | `notifier.py:51,69,98,151` hala kosulsuz Markdown |
| `RunResult` + `last_youtube_publish_at` | **sifir esleme** |
| 3 yeni test dosyasi | ucu de **yok** |

**Bu planin en onemli bulgusu:** teshis dogruydu, kalici cozum insa edilmedigi icin ertesi
gun ayni sinif hata ikinci kanali oldurdu. ROCK 0'i tek basina yapmak yarin ucuncu kanali
oldurur. **[Codex FIX kabul]** Bu cevrim, ROCK 1-3 birlesmis kod + kanit olmadan
"bitti" ilan EDILEMEZ.

### Olgu 7 , part 23'un iki ayri dusme sebebi var
Kosu 33275135503 (29 Ag, **failure**): `QC: cekim 3 esigi gecemedi (dinamik kredi payi
doldu) , cekim bolumden dusuruldu` + `Part 23 uretilemedi`. `qc_log.jsonl`: cekim 3 iki
denemede de `continuity_ok:false` / `state_carry_ok:false`.
Sonra 30 Ag altyapi arizasi (Olgu 1). **Kredi , DUZELTILDI [Codex FIX kabul]:**
bolum tavani env'deki 900 **degil**, `bible.json > series.credit_hard_cap_value = **800**`
(`credit_gate.py:234` bible degerini env'in onune geciriyor). Yanan 436 -> **kalan 364**,
464 degil. 364, dort taze cekime buyuk olasilikla **yetmez**.

### Ozet nedensellik
29 Ag icerik reddi (436 kredi yandi) -> 30 Ag imgbb 4 dk dustu -> kurtarilamaz hold yazildi
(kusur A) -> alarm Markdown hatasindan gitmedi (kusur B) -> kosu yesil raporladi (kusur C)
-> 31 Ag workflow kapatildi, kosu hic olusmadi (kusur D) -> 4 gun sessizlik.

---

## 2. "YAPMACIK" SORUNU , olculdu VE gozle denetlendi

### 2.1 Izleniyor ama tepki gelmiyor
`analytics_data/daily/2026-09-01.json`, son 16 video:

| olcut | deger | kill-gate hedefi | durum |
|---|---|---|---|
| toplam izlenme | 20.550 | , | , |
| **L/1k** | **7,54** | **>= 30** | **4x altinda** |
| **C/1k** | **0,24** | **>= 1,0** | **4x altinda** |
| medyan izlenme | ~1.205 | , | iyi |
| 16 videoda toplam yorum | **5** | , | , |
| abone (27 Tem -> bugun) | 113 -> **125** | , | 5 haftada +12 |

**[Codex FIX kabul]** Bu tek basina "izleyici AI oldugunu anladi"nin KANITI degildir;
konu, kanca ve hedef kitle uyumsuzlugu da aciklayabilir. Bu bir **hipotez**dir ve
ROCK 4 onu sabit-yasta olcumle sinar.

### 2.2 Claude'un elle video denetimi (2026-09-01, gercek yayinlanmis dosyalar)
`yt-dlp` ile indirildi, `ffmpeg` ile 20 karelik kontakt sayfasi cikarildi, gozle bakildi.
**Bu, plandaki en degerli yeni kanittir ve 10 bolumluk bir olcum programina gerek
kalmadan bugun elde edildi , Codex'in ROCK 4 KILL gerekcesi hakliydi.**

**part 22 , "Something Is WRONG With This LEMON"** (`vKus2kyMIN0`, 1.392 izlenme, 7 begeni):
- Cekim 1-2: koyu benekli tezgah, sicak tungsten isik, kamera alcak ve yakin.
- Cekim 3-4: **belirgin sekilde BASKA bir tezgah** (acik renkli, farkli benek deseni,
  cizikler), **soguk gun isigi**, kamera cok daha geride, obje kadrajda baska konumda.
- Dort cekimin dordu de planda `environment: kitchen_counter` olarak **ayni** yazili.
- Anomali (limonun icindeki metal kilit) kucuk ve **statik**; 22 saniye boyunca hicbir sey
  yapmiyor. Kucuk ekranda (Shorts) ne oldugu okunmuyor.
- El anatomisi bu videoda **iyi**. Sorun anatomi degil.

**part 21 , "This SPONGE Is NOT Supposed To REPEL WATER?!"** (`5PG5IbbivE0`, 1.407 izlenme,
10 begeni):
- Anomali NET okunuyor, escalation gercek (masa -> su birikintisi -> kase -> muslugun
  altinda su sungerden akiyor). **Formatin dogru calistigi hali budur.**
- Ama: **cekim 1 rustik ahsap masa, cekim 2 baska bir mutfak masasi (ocak arka planda),
  cekim 3 baska bir tezgah + cam kase, cekim 4 evye.** Dort ayri mekan.
- **Yuz 4 cekimin 3'unde acikca gorunuyor** ve bir karede adam **agzi acik "vay be"
  tepkisi** veriyor , tam olarak kullanicinin "yapmacik" dedigi sey.
  (part 21 ESKI semayla planlanmis: `face_visible=None`, cekimlerde `environment` yok.
  part 22'de `face_visible=False` ve yuz gercekten yok , **yuz duzeltmesi tuttu.**)

### 2.3 MEKANIK KOK NEDEN , hipotez, kanitlanmis tek sebep DEGIL
`bible.json > series.chain_frames = **False**` (Codex tur-2 bagimsiz dogruladi:
`produce.py` ne onceki son kareyi yakaliyor ne de sonraki Omni payload'ina ekliyor).
Dort cekim birbirinden bagimsiz uretiliyor; cekimler arasi tek sureklilik mekanizmasi
**metin**. Metin bir kamera konumunu, bir yuzeyi ya da bir isigi sabitleyemez.

Ikinci kanit: `series/shots.py:156-177` `state_carry` icin **zaten mekanik lint var**
(ardil cekimin prompt'unda izin birebir gecmesini kontrol ediyor). Bu lint part 23'u
gecirdi, video yine surekliligi kirdi. **[Codex KILL kabul]** "state_carry lint'i
ekleyelim" olu oneriydi.

**[Codex tur-2 FIX kabul , kanit geri cekildi]** Onceki revizyonda 29 Ag'daki
`⚠️ Ortam referans gorseli yok` uyarisini nedensel kanit gostermistim. **Yaniltici:**
`ensure_episode_refs` ucretli cekimlerden ONCE `bathroom_sink` referansini uretip
kaliciliyor , tipki part 22 icin `kitchen_counter`'i urettigi gibi. Bu satir kanit
listesinden **cikarildi**; yerine gercek son payload'lar test edilecek (ROCK 4).

**[Codex tur-2 FIX kabul]** `chain_frames=False` **makul bir katki**dir, kanitlanmis tek
kok neden degil , part 22 zaten uretilmis ortam referansini almisti ve yine kaydi.
Bu yuzden ROCK 4 dogrudan 10 bolumluk deneye girmez; once **yayinlanmayan esli
kosullandirma pilotu** calisir.

### 2.4 Format karari dogruydu, sorun format degil
`ENTEGRASYON_ANALIZ_2026-07.md` 1.1: Temmuz'da uzun anlatili seri medyani **15** izlenme.
Absurd-obje formatina donus medyani **~1.205**'e cikardi , **80x**. Format pivotu isini
yapti. Kalan problem **sahne butunlugu / inandiricilik**.

---

## 3. ELDEKI OTOMASYONLAR (envanter, olculdu)

`Projeler/KURULUM_TAKIP.md`: **36 proje , 17 canli, 18 dondurulmus, 1 kismi.**
Kullanicinin "Make icindeki projeler klasoru" dedigi budur; fiili kosum yeri Make degil
**GitHub Actions / Railway / Coolify / lokal** (tablonun "host" sutunu).

| # | proje | durum | Sentinal'e katkisi |
|---|---|---|---|
| **6** | YouTube_Yorum_Otomasyonu | canli | **Zaten TAM BU KANALA bagli** (`UC-Aht8VqAUMTUKYRQA3agYQ`). C/1k 0,24 , cevaplanacak yorum yok. Kanal dirilmeden issiz. |
| **13** | YT_Aciklama_Otomasyonu | canli | aciklama/etiket , kesif |
| **8/9** | Notion_Video_Link/Performans_Doldurucu | canli | performansi Notion'a tasiyor, **brief'e geri akmiyor** (acik halka) |
| **15** | Reels_Script_Pipeline | canli | obje/kanca havuzu beslenebilir |
| **33** | TikTok_Video_Boost | kismi | ikinci dagitim kanali (bu cevrim disi) |
| **34** | Itibar_Radari | canli | disaridan tepki olcumu |
| **35** | Akilli_Watchdog | canli | **Sentinal'i izliyor ama yanlis olcutle** (Olgu 4) |

**MCP ile erisilebilir ama repoda kullanilmayanlar:** `higgsfield.video_analysis_create`
(elle denetimi otomatige cevirir , SONRAKI cevrim), `higgsfield.upscale_video`,
`apify.scraptik--tiktok-api` (havuzu olcuye baglar). `higgsfield.virality_predictor`
**[Codex KILL kabul]** yayin bloke eden kapi olarak KULLANILMAZ (kalibre degil, gunluk
yayini durdurabilir).
**Not:** `fal-ai` MCP bu oturumda **401** ile baglanamadi. Higgsfield ve Apify calisiyor.

---

## 4. ROCK'LAR

**[Codex tur-4 FIX kabul , YAPISAL]** r5'te zorunlu duzeltmeler bir EK'te duruyordu, rock
govdeleri onlarla celisiyordu , bir gelistirici ROCK 3'u okuyup yanlis seyi insa ederdi.
r6'da tum duzeltmeler **rock govdelerinin ve proof'larinin ICINE** islendi; ek kaldirildi,
yerine §8 kanit defteri kondu.

**Sira:** ROCK 0 (KAPANDI) -> **ROCK 1a defter** -> **ROCK 1b QC kapasitesi** ->
ROCK 1c durum makinesi (Sentinal canary) -> ROCK 2 alarm -> ROCK 3 repo ici olcum ->
ROCK 3d nobetci (ayri repo) -> ROCK 4a pilot -> 4b kosullandirma -> 4c pencere.

---

### ROCK 0 , KAPANDI: uygulandi, BASARISIZ  [Codex tur-4 KILL kabul]

1 Eylul'de uygulandi: workflow `active` yapildi, part 23/24 `skipped`, part 25 kuyudan
kurtarildi, part 24/25/26 cekim 1 promptlari duzeltildi. **Uc kosu, sifir yayin.**
Ayrintili kanit: §8.

**Durum: EXECUTED-BUT-UNSUCCESSFUL.**
**[Codex tur-4 KILL kabul] YASAK:** ROCK 1a, 1b, 2 ve 3'un Done kapilari gecmeden
**hicbir uretim retry'i tetiklenmeyecek**. Her deneme kalici bolum butcesinden yiyor ve
bugun yayin uretmeden ~1300 kredi yakildi.

**Kalici kazanim (yok sayilmamali):** cekim 1 "kurulmus durum" duzeltmesi tuttu ,
part 24'te regen 1 sonrasi, part 25'te **ilk denemede** gecti. Ilk-kare kusuru cozulmustur.

---

### ROCK 1a , Defter catisma kurtarma  [ROCK 1c'nin ON KOSULU]

**Neden once bu:** `scripts/merge_credits_ledger.py:36-41` korumasi `set(doc) == {"entries"}`;
canli defterde `{'entries','episode_spend'}` var (`episode_spend` 2026-08-28'de eklendi,
script 2026-08-13'te yazildi). Bu makinede calistirdim: `is_ledger(canli) = False`.
Sonuc: es zamanli kosuda defter catisirsa `persist_state.sh` fail-closed dala girer ve
**durum commit'inin TAMAMI duser** , `series.json` ilerlemesi, `published.json`,
`last_run.json` ve ROCK 2'nin alarm outbox'i repoya hic ulasmaz.
Ayrica satir 74 dosyayi `{"entries": merged}` olarak yeniden yazar , **`episode_spend`'i
SILER**, yani `credit_gate`'in dayandigi bolum muhasebesi ucar.
**[Codex tur-4 FIX kabul]** ROCK 1c'nin "tek yetkili sayac" iddiasi ve ROCK 2'nin outbox'i
ikisi de bu kirik yolun uzerinde duruyor , ayri rock degil, ON KOSUL.

**Ne:** sema-koruyan uc-yollu defter catisma cozumu. `episode_spend` dahil bilinen tum
ust seviye anahtarlar korunur; bilinmeyen anahtar gorulurse fail-closed.
**Done:** es zamanli iki kosunun defter catismasi veri kaybetmeden birlesir.
**Proof:** `python -m pytest tests/test_ledger_merge.py -q` , (a) ayrik anahtarlar
birlesir, (b) **ayni anahtarda ayrisan degerler** icin tanimli ve test edilmis kural,
(c) `episode_spend` her senaryoda korunur, (d) bilinmeyen sema -> fail-closed,
(e) **uctan uca:** yapay catisma kurulur, `persist_state.sh` kosar, `series.json` +
`published.json` + `last_run.json` + outbox'in HEPSI commit'te bulunur.

---

### ROCK 1b , QC kapasitesi: kota bir "retry" degil, bir KAPASITE sorunu  [ON KOSUL]

**[Codex tur-4 FIX kabul]** r5'te `QUOTA` yalnizca "retryable" bir neden koduydu. EK-7
bunu curuttu: 1 Eylul 19:25-19:29'da birincil `gemini-2.5-flash` **429 RESOURCE_EXHAUSTED**,
yedek `gemini-flash-latest` **503 UNAVAILABLE** verdi ve bolum yayinlanamadi. Filo ortak
kota Sentinal'in gunluk slotuna sira gelmeden tukeniyor (dunku flashpoints planinin
Olgu 8'i, ayni sinif). Retry mantigi bunu **cozmez**: ertesi gun ayni saatte kota yine bos olur.

**Ne:** canary, **bir tam gunluk bolume yetecek AYRILMIS ya da IZOLE QC kapasitesi**
uzerine kurulur. Secenekler (Ihsan karari, §5 soru 2): ayri proje+anahtar, faturalandirma
+ harcama tavani, hat basina QC butcesi, ya da sira adaleti.
**Done:** Sentinal'in gunluk slotunda bir bolumun TUM QC cagrilarini yapabilecek kapasite
olculebilir sekilde ayrilmis.
**Proof:** `python tools/qc_call_census.py --days 7` ile gun x hat x model x sonuc tablosu
**artı** ayrilmis kapasiteyle kosan **gercek bir ZAMANLANMIS kosu** (elle tetikleme degil)
QC'yi 429/503 almadan bastan sona tamamlar.

---

### ROCK 1c , Gecici ariza kalici olum olmasin  [Sentinal canary]

0. **Canary'nin on kosulu:** ortak runner'da "yalniz Sentinal'de dene" imkansiz ,
   `series_runner`'i degistirmek 12 workflow'u aninda etkiler. Bu yuzden seri-basi
   `bible.json > series.state_machine_version` bayragi, **varsayilan eski davranis**.
   Bayrak kapaliyken davranisin BIREBIR eskisi oldugu test edilir; migrasyon yalniz
   `unnatural-lab`'a uygulanir.
1. **Tek dayanikli referans stratejisi:** obje referansi, ortam referansi ve zincir karesi
   ucu birden ayni kalici kaynaktan. Uretim motoru public URL istedigi icin strateji
   "kalici depo + deterministik public URL" olarak TEK yerde tanimlanir.
2. **Geri cekilme sabit:** 5 deneme, 2/5/10/20 sn + ±%20 jitter, **toplam son tarih 90 sn**;
   en kotu durum aritmetigi testte assert edilir.
3. **Tipli neden kodu:** `QUOTA`, `REF_DOWNLOAD`, `FRAME_EXTRACT`, `AUDIO_MASTER`,
   `CONTENT_REJECT`, `BUDGET_EXHAUSTED`, `UNKNOWN`. Varsayilan retryable; istisnalar acik listede.
4. Tek sinirli deneme politikasi `generation_fail` ve icerik reddi dahil **her**
   terminal-olmayan uretim sonucuna uygulanir.
5. **Kontrol noktalari ayrilir:** uretim / Release / onay karti / platform yuklemesi.
   Telegram ya da Release patladiginda video **yeniden URETILMEZ**.
6. `retry_spent` EKLENMEZ; `credits_ledger.json` tek yetkili sayac (ROCK 1a onu onarir).
7. 3 denemeden sonra olu-mektup: `needs_human` + kanaldan dusurulur, `run_next` sonraki
   uygun bolume gecer, escalation surer. Olu-mektup **terminallestirilir** ve `next_part`
   secilen bolum URETILMEDEN ONCE atomik ilerletilir.
8. **Gecis:** diskteki bozuk `awaiting_approval` kayitlari idempotent migrasyonla
   siniflandirilir , yeni runner calismadan ONCE.
9. `awaiting_approval` yalniz `video` + `release_tag` + `approval_msg_id` ucu doluyken yazilir.
10. **[Codex tur-4 FIX kabul , YENI] Butce tukenmesi normatif gecistir.** r5'te yalnizca
    "kredi butcesi asilirsa retry durur" yaziyordu; bu, bolumu **secili ama bitirilemez**
    birakiyordu (part 24 bugun tam bunu yasadi: 512/800, kalan 288, dort ana cekim icin
    muhafazakar taban 400). Kural: **her ucretli cagridan ONCE** kalan kredi ile
    *muhafazakar asgari tamamlama maliyeti* karsilastirilir; yetmiyorsa bolum atomik olarak
    `budget_exhausted` diye **terminallestirilir**, alarm gider, `next_part` ilerler.
**Done:** imgbb/kota dususe bile hat kendiliginden toparlanir; tek kotu bolum kanali durdurmaz.
**Proof:** `python -m pytest tests/test_hold_recovery.py -q` , hold->retry->yayin;
`REF_DOWNLOAD` retryable; 3 denemeden sonra olu-mektup + **sonraki bolum uretilir ve
isaretci once ilerler**; her eksik-artefakt vakasi `awaiting_approval` YAZMAZ; migrasyon
idempotent; **iki ardisik temiz checkout kosusu disaridaki imgbb kapaliyken gecer**;
geri cekilme en kotu suresi 90 sn'yi asmaz; **butce yetmeyen bolumde EK HARCAMA SIFIR
oldugu assert edilir** ve durum `budget_exhausted` olur.

---

### ROCK 2 , Alarm kirilmasin

1. Kritik alarmlar **`parse_mode` olmadan** gonderilir (kacis+fallback yerine, daha basit).
2. `send_message` yapisal sonuc doner; `last_run.json`'a dokunmaz.
3. **Outbox:** teslim edilemeyen kritik alarm dosyaya yazilir, durum commit'iyle kalici olur,
   sonraki kosuda yeniden denenir; teslim edilene kadar `outcome=failure`.
4. **Sira baglayici:** outbox bosaltimi **son `if: always()` persist adimindan ONCE**.
5. Checkout patlarsa repodaki alarm kodu YOKTUR -> ayri, **checkout'tan bagimsiz** dogrudan
   bildirim adimi; checkout/pip/import patlamalari workflow duzeyi proof'a dahil.
**Done:** icinde `_`, `*`, `[` gecen alarm her zaman ulasir; ulasmazsa hat kirmizi olur.
**Proof:** `python -m pytest tests/test_notifier_entity_fallback.py -q` + `_alert` dahil TUM
kritik cagri yollari (runner cikis kodu + outbox olusumu + sonraki kosuda teslim) +
checkout-basarisiz workflow testi
**+ [Codex tur-4 FIX kabul] uctan uca:** ROCK 1a'nin catisma senaryosu altinda outbox
kaydinin commit'te HAYATTA KALDIGI gosterilir , aksi halde alarm testi gecerken gercek
alarm sessizce kaybolur.

---

### ROCK 3 , Yesil isik gercek yayini olcsun  [repo ici]

1. Tipli `RunResult` + tek atomik yazici.
2. `last_run.json` semasi korunur; `action` ve `last_youtube_publish_at` eklenir. Damga
   `published.json`'daki son dogrulanmis yayindan tohumlanir; yayin olmayan her sonuc onu
   **degistirmeden birakir**.
3. `action=published` icin 11 karakterlik bicim yeterli degil , kimlik YouTube RSS/API ile
   dogrulanir. **Cifte yukleme korumasi:** `uploaded_pending_verification` kontrol noktasi;
   mevcut yukleyici HTTP 200 donen ama **kimlik icermeyen** cevaplari kabul ettigi icin
   (`core/uploader.py` kimlik cikarma yollari `None` donebiliyor; `published.json`'da
   `instagram`/`tiktok` `null`) ya **dayanikli idempotency anahtari** (yukleme oncesi
   uretilen, kanalda aranabilen isaret) ya da **test edilmis kimliksiz kurtarma yolu**
   tanimlanir: ne yeniden POST eder, ne sonsuza kadar bekler (sinirli yoklama ->
   `needs_human` + alarm).
4. Runner hic olusmadan patlayan durumlar icin workflow'a ait ayri hata zarfi.
5. Nobet esigi 12 saat DEGIL , **beklenen-slot son tarihi + tolerans**. Tolerans, olculen
   kuyruk gecikmeleriyle (+119..+397 dk) celismeyecek sekilde secilir ve
   **kuyrukta/kosuyor/patladi** durumlari ayirt edilir (GitHub run state).
**Done:** held/failed kosu asla `success` yazmaz; yalniz dogrulanmis YouTube yayini
`published` sayilir.
**Proof:** `python -m pytest tests/test_last_run_contract.py -q` (held kosu success yazmaz;
IG-only `failed`; no-op damgayi ilerletmez; dis dogrulama belirsizken cifte yukleme YOK)
+ **calistirilabilir workflow sozlesme kontrolu** bes sema yazicisi icin ve duman testi
12 runner cagiricisi icin (gecis matrisi tek basina YETMEZ).

---

### ROCK 3d , NOBETCI: kontrol eksik degil, NOBETCININ KENDISI OLU  [ayri repo]

**[Codex tur-4 FIX kabul , r5'in ROCK 3.5-3.6'si YANLISTI ve kaldirildi]** "state kontrolu
ekleyelim" onerisi olu dogmustu: `actions_checker.py:371-388` **zaten** `state != "active"`
icin `logger.critical` uretiyor, `disabled_manually`'yi adiyla aniyor ve `config.py:138`
`youtube-automation`'i **zaten** hedefliyor. Eksik olan kontrol degil, **calisma yolu**.

Olculen kok neden: `akilli-watchdog` workflow'unda `Nobet` adiminin `if:` korumasi YOK ve
onunde kosulsuz bir unittest adimi var. `tests/test_kurulum.py:391`
`assertTrue(check_actions_quota(100)["healthy"])` iddia ediyor ama fonksiyon **ay sonu
projeksiyonu** yapiyor. Yerelde birebir urettim: ayin 1'inde 100 dk -> projeksiyon **3000**
-> `healthy=False` -> test patlar -> job exit 1 -> **nobet hic kosmaz**.
Kanit: kosu 33493291124 (2026-09-01 09:38) `FAILED (failures=1)`, logda CANLI saglik
kontrolu ciktisi YOK. 2026-08-31 11:12 kosusu ise DOGRU davranmisti.

**Ne:**
1. **Nobeti kendi testinden ayir:** patrol ayri, **bagimsiz zamanlanmis job**.
   **[Codex tur-4 FIX kabul]** Yalnizca `Nobet` adimina `if: always()` koymak YETMEZ ,
   workflow'un kendisi devre disi kalirsa ya da calismadan patlarsa yine sessizdir.
2. **Olu-adam (dead-man) kalp atisi:** nobetci kosmadiginda BAGIMSIZ bir kanal bagirir.
3. Tarih bagimli kota testi **enjekte edilen tarihle deterministik** hale getirilir.
4. `FLEET_PAT` yoklugu **fail-closed** dogrulanir (bugun yokken Actions nobeti sessizce kor).
**Done:** nobetci kosmadigi ya da workflow'u kapatildigi zaman 24 saatin altinda haber gelir.
**Proof:** ayin 1'i enjekte edilmis kota testi gecer; PAT'siz kosu KIRMIZI biter; patrol
job'u kasten oldurulur ve **dead-man kanali bagirir**; **[Codex tur-4 CLARIFY]** bu repo
buradan okunamadigi icin kanit o repodan disariya alinir (kosu kimligi + log alintisi).

---

### ROCK 4a , YAYINLANMAYAN ESLI PILOT  [4b/4c'nin kapisi]

Cekim 2 surekliligi **4 bagimsiz uretimde, 2 obje ve 2 ortamda** reddedildi (§8).
**[Codex tur-4 kabul]** Bu, surekliligin **sistematik bir sorun oldugunu kanitlar**;
`chain_frames=True`'nun **cozum oldugunu kanitlamaz**. Pilot bu yuzden zorunlu kalir.

**Ne:** ayni plandan iki kol , biri bugunku ayar, biri gorsel kosullandirma acik.
Ikisi de yayinlanmaz. Planlarda `"seed": null` oldugu icin kol basina tek uretim salt
model rastgeleligini olcer: **acik ve kollar arasi AYNI seed'ler**, **en az 3 esli tekrar**
(3 farkli obje/ortam), **onceden yazilmis sahne-sureklilik rubrigi** (ayni yuzey / ayni
isik / ayni kamera konumu / obje konum tutarliligi , her biri gec-kal), **kor puanlama**.
**Done:** pilot fark uretirse 4b'ye gecilir; uretmezse hipotez REDDEDILIR ve ROCK 4 durur.
**Proof , [Codex tur-4 FIX kabul] "iki kontakt sayfasi" YETMEZ:** **alti kolun artefaktinin
tamami**, kaydedilmis seed'ler, kor puanlar, rubrik sonuclari ve **onceden yazilmis
dur/devam hesabi** teslim edilir.

---

### ROCK 4b , Kosullandirmayi acmadan ONCE kapatilacak kusurlar

Ucu de kodda dogrulandi; acilirsa uretimi BOZAR:
1. **`chain_scope` varsayilani `"series"`** (`series/bible.py:209`) , `chain_frames` acilip
   `chain_scope="episode"` yazilmazsa bolum 24, bolum 23'un son karesinden baslar.
2. **Baglama sirasi bozuk** (`series/produce.py:1337-1341`): `resolve_shot` numarali gorsel
   baglamalari kurduktan SONRA zincir karesi `image_urls`'in basina ekleniyor; prompt
   "gorsel 1 = obje" derken 1. sira artik onceki kare. Tam sirali referans listesi **once**
   kurulur, etiketler ondan turetilir, URL-etiket karsiligi assert edilir.
3. **[Codex tur-4 FIX kabul , r5 bunu EKSIK tarif ediyordu] Bayat kare tasinmasi.**
   r5 "kosullandirmasiz sessizce devam eder" diyordu; kod daha kotu:
   `produce.py:1501-1510` ve `1647-1656`'da `if up: chain_url = up` dallarinin **else'i yok**.
   Cekim KABUL edildiginde ama kare cikarma/yukleme None donduğunde `chain_url` **onceki
   cekimin karesinde KALIR** (sifirlama yalnizca `previous_shot_dropped` yolunda) , yani
   cekim 4, cekim 2'nin karesiyle kosullandirilabilir ve bu yolda **tek log satiri yok**.
   Duzeltme: her cekim icin **taze bir degiskenden** kurulan sonraki-kare referansi; her
   basarisizlikta ya fail ya **acik sifirlama**.
4. Son-kare zinciri kabul edilmis bir artefakti sonraki tum cekimlere tasiyabilir , zincir
   karesi **uygunluk QC'si** + metin-uretimine sessizce donmeyen **kanonik sahneye sifirlama**.
**Proof:** `python -m pytest tests/test_shot_conditioning.py -q` , `chain_scope="episode"`
zorunlu; URL-etiket karsiligi assert; zincir yuklemesi patarsa uretim baslamaz (dusman testi);
**cekim N+1'in YALNIZ kabul edilmis cekim N'in provenansiyla kosullandirildigi assert edilir**
(bayat kare tasinmasi yakalanir); bolumler arasi tasima YOK.

---

### ROCK 4c , 10 bolumluk pencere  [YENIDEN TASARLANDI]

**[Codex tur-4 FIX kabul , r5'in tasarimi MIMARI OLARAK IMKANSIZDI]** r5 "yayin oncesi
gozle kabul + 12 saat SLA + 1 bolum tampon" diyordu. Mevcut kodda kurulamaz:
onay adimi (`unnatural-lab.yml:74-78`) ve uretim adimi (:83-89) **ayni gunluk job'da**;
`series-approve.yml` cron'u YORUMDA; `approver.py:102-106` yalnizca `next_part`'a bakiyor;
`series_runner.py:393-395` `awaiting_approval` gorunce uretimi blokluyor ve `:403-407`
o gun kanala yayin yapilmissa yine uretmiyor. Sonuc: kadans **iki gunde bire** duser ve
tampon hicbir zaman olusamaz , CORE FOCUS'un "her gun 1 video" ayagi ihlal edilir.

**Ne:** uretim, inceleme ve zamanlanmis yayin **birbirinden ayrilir** ve aralarinda
**dayanikli bir artefakt kuyrugu** durur. Uretim kuyruga yazar; inceleme kuyruktan alir;
yayin kuyrugun onaylanmis basindan gunluk cikar. Uretim, inceleme bekleyen bir bolum
yuzunden durmaz.
**Tek degisken kilidi:** obje havuzu, baslik kaliplari, anlatim, sure, yuz kurali degismez.
**Olcum:** taban **sabit 72 saat yasta** yeniden kurulur (bugunku 7,54 karisik yasta
olculdu); karar bantlari ve istatistik **onceden** yazilir. **Kalite hedefi acik kalir:**
L/1k 30'a ulasmadan bu is "baska deney secerek" Done ilan EDILEMEZ; 7,54'un altina duserse
mudahale geri alinir.
**Kill-gate:** stack parmak izi degisecegi icin yeni pencere acilir ve kayda gecer.
**Done + Proof , [Codex tur-4 FIX kabul]:** **10 ARDISIK GUNLUK yayin** kanitlanir ve
**tamponun hicbir gun sessizce sifira dusmedigi** gosterilir; 10 bolumun her biri icin
yayin oncesi gorsel kabul kaydi; sabit-72-saat taban raporu ve onceden yazilmis karar bandi.

---

## 5. IHSAN'IN KARAR VERMESI GEREKENLER

1. **`Unnatural Lab Daily` workflow'unu kim/neden kapatti?** (30 Ag 21:29 , 31 Ag 18:30
   arasi). 31 Ag 11:12'de nobetci onu hala `active` gormustu. Repodan kanitlanamiyor.
2. **QC kapasitesi (ROCK 1b, artik ON KOSUL):** (a) ayri proje+anahtar, (b) faturalandirma
   + harcama tavani, (c) hat basina QC butcesi, (d) sira adaleti , ya da bilesimi?
   Bugun filo ortak kota Sentinal'i kuru birakti ve bolum yayinlanamadi.
3. **ROCK 1c yayilimi:** 12 workflow / 5 sema yazicisi ortak motoru kullaniyor. Tavsiyem:
   surum bayragiyla once yalniz Sentinal canary, sonra filo. Onayliyor musun?
4. **[UC turdur acik, ROCK 2'nin Done sarti]** Basarisiz GitHub job bildirimlerini
   **gercekten aliyor musun** (mail/mobil), 24 saat icinde? Kanit gelene kadar 24 saat sozu
   tek kanala dayanir sayilacak.
5. **ROCK 3d ayri repoda** (`akilli-watchdog`). Orada calismami istiyor musun? Nobetci su an
   OLU ve her ay basinda yeniden olecek.

## 6. KAPSAM DISI

- Kalite kapisini gevsetmek. Fail-closed dogru; sorun cikis yolunun olmamasi.
- QC modelini degistirmek (`ISSUES.md` C2 yalnizca envanterdir; r4'te bunu yanlis
  alintiladigim engel kaldirildi).
- `virality_predictor`'i yayin bloke eden kapi yapmak (kalibre degil).
- Duraklatilmis 6 Sentinal serisini diriltmek.
- `kie-uretim` concurrency kuyrugunun yeniden tasarimi -> `ISSUES.md` (ROCK 3.5'in
  tolerans secimi bu olcume BAGIMLI kalir).
- **[Codex tur-4 DEFER kabul]** `SHOT1_ONSET_LANGUAGE`'a daha fazla tetikleyici fiil
  eklemek , sinirsiz bir regex yamasi olur ve etkilenen planlar duzeltildikten sonra
  asil engel degil. Yerine "yapisal kurulmus-ilk-kare dogrulamasi" `ISSUES.md`'ye yazildi.
- TikTok boost (#33), upscale, Apify havuz beslemesi, `video_analysis_create`.

## 7. RISKLER

- ROCK 1a/1b on kosul; atlanirsa ROCK 1c ve ROCK 2 kagit uzerinde gecer, gercekte kaybolur.
- ROCK 1c 12 workflow'un cagirdigi motoru degistirir , surum bayragi + canary sart.
- ROCK 3d ayri repoda ve nobetci su an olu; yapilmazsa 24 saat sozu tutulmaz.
- ROCK 4b acilmadan kosullandirma acilirsa uretim BOZULUR (uc kusur da kodda dogrulandi).
- ROCK 4a pilotu hipotezi curutebilir , o zaman ROCK 4 durur, bu kabul edilen bir sonuctur.
- ROCK 4c yeniden tasarimi uretim/yayin ayrimini degistirir; kadans regresyon riski var,
  bu yuzden proof 10 ardisik GUNLUK yayin istiyor.

## 8. KANIT DEFTERI , 1 Eylul 2026 (ROCK 0 uygulamasi)

| kosu | ne oldu | sonuc |
|---|---|---|
| 33533304587 16:41 | part24 cekim 1 iki kez red (acilis karesi okunmuyor) | failure |
| 33534926748 16:57 | cekim 1 **GECTI** (duzeltme tuttu); cekim 2 surekliligi 2 kez red | failure |
| 33547942009 19:10 | part25 cekim 1 **ILK denemede GECTI**; cekim 2 surekliligi 2 kez red; sonra QC kotasi | **"success" ama YAYIN YOK** |

Son kosunun tam olum zinciri (birebir log):

    19:25:55 Ham ses QC gemini-2.5-flash geçici hata (429 RESOURCE_EXHAUSTED) ,  5s sonra tekrar
    19:26:10 Ham ses QC gemini-2.5-flash başarısız: 429 RESOURCE_EXHAUSTED
    19:27:44 Ham ses QC gemini-flash-latest geçici hata (503 UNAVAILABLE)
    19:29:14 Ham ses QC yapılamadı (503 UNAVAILABLE)
    19:29:15 QC HOLD: çekim 2 zorunlu kapıda değerlendirilemedi
    19:29:15 Part 25 QC HOLD ,  durum awaiting_approval; yayın bloke edildi.
    19:29:15 Telegram sendMessage hata: can't parse entities ... byte offset 89
    kosu sonucu: success ; uzaktaki last_run.json = {"outcome":"success"}

Dort kusur ayni anda: kurtarilamaz hold + olu alarm + yalanci yesil + tukenmis ortak kota.

**Kredi (tavan 800/bolum):** 23 -> 436, 24 -> 512, 25 -> 352. Bir gunde ~1300 kredi,
sifir yayin.

**Elle mudahaleler (hepsi kayitli, geri alinabilir):** part23 `skipped` (0b2c579),
part24 `skipped`, part25 hold'dan kurtarildi -> `planned` (49f7300), part24/25/26 cekim 1
promptlari duzeltildi (5ab27cd, 207986e, 16bccd2), workflow `active`.

**Kontakt sayfalari:** `sentinal_ihsan/measurements/contact_sheets_2026-09-01/`
(video kimlikleri, yayin tarihleri, olcumler, yeniden uretim komutlari, SHA256).

**Bagimsiz panel:** 29 ajan, 5 mercek, her bulgu 2 celiskici dogrulayici; 25 ham bulgu ->
12 dogrulandi -> 5 blocking onaylandi. 13 dusuk siddetli bulgu DOGRULANMADI (kapsam disi).
