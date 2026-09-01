# RF-PLAN , Sentinal Ihsan kanalinin dirilisi + "yapmacik" sorununun kokunden cozumu

**Tarih:** 2026-09-01 · **Surucu:** Claude (Visionary) · **Inceleyen:** Codex (Integrator)
**Revizyon:** r5 (Codex tur 1-3: 60 bulgu · bagimsiz panel: 5 blocking · ROCK 0 canli sonucu)
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

**[Codex tur-3 FIX kabul , sira DUZELTILDI]** Tur-2'de onerdigim sira hatali idi: ROCK 4c'nin
10 bolumluk penceresi boyunca alarmlar kirik ve yesil isik yalanci kalirdi , yani kalite
deneyini tam da kanalin sessizce olebildigi kosullarda kosardim. Dogru sira:

**ROCK 0 (hemen) -> ROCK 1 (Sentinal canary) -> ROCK 2 + ROCK 3'un REPO ICI kismi
(guvenilirlik tabani, filoya yayilim BLOKE watchdog isinden bagimsiz) -> ROCK 4a pilot
-> ROCK 4b duzeltmeler -> ROCK 4c 10 bolumluk pencere.**

ROCK 3'un watchdog'a bagli 5-6. maddeleri ayri ve BLOKE kalir; repo ici kismi (RunResult,
dogrulanmis yayin damgasi, cifte yukleme korumasi) ROCK 4c'den ONCE biter.

### ROCK 0 , Acil dirilis: bugun video ciksin  [elle, ~30 dk]
1. **Ihsan onayi olmadan baslamaz** (Bolum 5, soru 1): workflow neden kapali?
   Onay gelirse `gh workflow enable .github/workflows/unnatural-lab.yml
   --repo Wolkchen00/youtube-automation`, sonra `gh workflow list` ile `active` dogrula.
2. **[Codex FIX kabul]** Kredi defteri **SIFIRLANMAZ** , 436 gercek harcamadir.
   Secenek: (i) part 23 `skipped` + part 24'ten devam, (ii) kayda gecen tek seferlik
   tavan istisnasi. Gercek tavan **800**, kalan **364** (Codex tur-2 kesinlestirdi:
   yol `produce.episode_credit_cap(bible)` -> `credit_gate.reserve`).
3. **[Codex FIX kabul]** Part 23 atlanacaksa `status="skipped"` + `skip_reason` yazilir,
   `next_part` **atomik** ilerletilir; nonterminal hold birakilmaz.
4. "state_carry zincirini duzelt" onerisi **dusuruldu** (2.3).
5. `workflow_dispatch` ile tetikle.

**Done:** kanalda **bugun tarihli, beklenen bolume ait** yeni video var.
**Proof , [Codex tur-2 FIX kabul] onceki surum BUGUN DE GECIYORDU** (bayat part-22 kimligi
hem `published.json`'da hem RSS'te ayni). Bu yuzden dort kosul birden aranir:

**[Codex tur-3 FIX kabul]** Bolum ve baslik kontrolu de duz yazi degil, **assert** olmali
(`EXPECTED_PART` kurtarma karari verilirken , Bolum 5 soru 2 , sabitlenir):

    EXPECTED_PART=24 python - <<'EOF'
    import json,re,os,unicodedata,urllib.request,datetime
    exp=int(os.environ['EXPECTED_PART'])
    d=json.load(open('sentinal_ihsan/unnatural-lab/published.json',encoding='utf-8'))[-1]
    vid=d['results']['youtube']; part=d['part']; sub=d['subtitle']
    x=urllib.request.urlopen(
      'https://www.youtube.com/feeds/videos.xml?channel_id=UC-Aht8VqAUMTUKYRQA3agYQ',
      timeout=30).read().decode()
    e=x[x.index('<entry>'):]
    top_id=re.search(r'<yt:videoId>([^<]+)</yt:videoId>',e).group(1)
    top_pub=re.search(r'<published>([^<]+)</published>',e).group(1)
    top_title=re.search(r'<title>([^<]*)</title>',e).group(1)
    norm=lambda s:unicodedata.normalize('NFKC',s).casefold().strip()
    today=datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    checks={'id eslesti':vid==top_id,'beklenen bolum':part==exp,
            'bugun yayinlandi':top_pub[:10]==today,'baslik eslesti':norm(sub)==norm(top_title)}
    for k,v in checks.items(): print(f'{k:20}: {v}')
    assert all(checks.values()), f'ROCK 0 BASARISIZ: {checks}'
    EOF

### ROCK 1 , Gecici altyapi arizasi kalici olum olmasin  [once YALNIZ Sentinal , canary]
0. **[Codex tur-3 FIX kabul , canary'nin ON KOSULU]** "Yalniz Sentinal'de dene" ortak
   runner'da **mumkun degil**: `series_runner`'i degistirmek 12 workflow'u aninda etkiler.
   Bu yuzden ilk is bir **seri-basi durum makinesi surum bayragi** (`bible.json >
   series.state_machine_version`, varsayilan = eski davranis). Yeni yol yalnizca bayrak
   aciksa calisir. Kanit sarti: **bayrak kapaliyken davranisin BIREBIR eskisi oldugu**
   test edilir (legacy-off testi), migrasyon yalnizca `unnatural-lab`'a uygulanir.
1. **[Codex tur-2 FIX kabul] TEK dayanikli referans stratejisi**, yalniz QC indirmesi
   degil: **obje referansi, ortam referansi ve zincir karesi** ucu birden ayni kalici
   kaynaktan gelir. Repoya gomulu hash'li dosya QC icin yeterli ama uretim motoru
   **public URL** istiyor , bu yuzden strateji "kalici depo + deterministik public URL"
   olarak tek yerde tanimlanir. Cozulmeden ROCK 4 baslamaz.
2. **[Codex tur-2 FIX kabul] Geri cekilme sayilari SIMDI sabitlenir**, implementasyona
   birakilmaz: 5 deneme, gecikmeler 2/5/10/20 sn + ±%20 jitter, **toplam son tarih 90 sn**.
   En kotu durum aritmetigi testte assert edilir.
3. **Tipli neden kodu:** `QUOTA`, `REF_DOWNLOAD`, `FRAME_EXTRACT`, `AUDIO_MASTER`,
   `CONTENT_REJECT`, `UNKNOWN`. Varsayilan retryable; istisnalar acik listede.
4. **[Codex FIX kabul]** Tek sinirli deneme politikasi `generation_fail` ve icerik reddi
   dahil **her** terminal-olmayan uretim sonucuna uygulanir.
5. **[Codex FIX kabul] Kontrol noktalari ayrilir:** uretim / Release / onay karti /
   platform yuklemesi. Telegram ya da Release patladiginda video **yeniden URETILMEZ**.
6. **[Codex FIX kabul]** `retry_spent` EKLENMEZ; `credits_ledger.json` tek yetkili sayac.
7. **[Codex FIX kabul]** 3 denemeden sonra bolum olu-mektup: `status="needs_human"` +
   kanaldan dusurulur, `run_next` sonraki uygun bolume gecer, escalation devam eder.
   **[Codex tur-2 FIX kabul]** Olu-mektup **terminallestirilir ve `next_part` isaretcisi
   secilen sonraki bolum URETILMEDEN ONCE atomik ilerletilir** , yoksa mevcut `advance()`
   semantigi part 24'u yayinlarken isaretciyi 24'te birakabilir.
8. **[Codex FIX kabul] Gecis:** diskteki bozuk `awaiting_approval` kayitlari (part 23 ve
   diger hatlar) idempotent migrasyonla siniflandirilir , yeni runner calismadan ONCE.
9. `awaiting_approval` yalniz `video` + `release_tag` + `approval_msg_id` ucu doluyken.

**Done:** imgbb dusse hat kendiliginden toparlanir; tek kotu bolum kanali durduramaz.
**Proof:** `python -m pytest tests/test_hold_recovery.py -q` , hold->retry->yayin;
`REF_DOWNLOAD` retryable; 3 denemeden sonra olu-mektup + **sonraki bolum uretilir ve
isaretci once ilerler**; kredi butcesi asilirsa retry durur; her eksik-artefakt vakasi
`awaiting_approval` YAZMAZ; migrasyon idempotent; **iki ardisik temiz checkout kosusu
disaridaki imgbb kapaliyken gecer**; geri cekilme en kotu suresi 90 sn'yi asmaz.

### ROCK 4 , Sahne butunlugu: ONCE PILOT, sonra dar mudahale  [ROCK 1'den sonra]
**[Codex KILL kabul]** Salt-olcum rock'i kapatilabilir ve izleyici sahte video izlemeye
devam eder. Elle denetim bugun yapildi (2.2, artefaktlar
`sentinal_ihsan/measurements/contact_sheets_2026-09-01/`).

**4a , YAYINLANMAYAN ESLI PILOT (once bu).** **[Codex tur-2 FIX kabul]** 10 bolumluk
deneye girmeden once, ayni plandan iki uretim: biri bugunku ayarla, biri gorsel
kosullandirma acikken. Ikisi de yayinlanmaz; kontakt sayfalari karsilastirilir.
Pilot sahne butunlugunde fark uretmezse ROCK 4 **durur** ve hipotez reddedilir.

**[Codex tur-3 FIX kabul , pilotun kendisi gecerli olmali]** Planlarda `"seed": null`
(bkz. `plans/part23.json`), yani kol basina TEK uretim salt model rastgeleligini olcer ve
kosullandirmayi yanlislikla dogrulayabilir ya da reddedebilir. Sart: **acik ve kollar
arasi AYNI seed'ler**, **birden fazla esli tekrar** (en az 3 cift, 3 farkli obje/ortam) ve
**onceden yazilmis sahne-sureklilik rubrigi** (ayni yuzey / ayni isik / ayni kamera konumu /
obje konum tutarliligi , her biri gec-kal ikili). Degerlendirme **kor**: sayfalar
etiketsiz karistirilarak puanlanir.

**4b , Kosullandirmayi acmadan once kapatilmasi ZORUNLU uc kusur** (ucu de Codex tur-2,
ucunu de kodda dogruladim , acilirsa uretimi BOZAR):
- **`chain_scope` varsayilani `"series"`** (`series/bible.py:209`). `chain_frames` acilip
  `chain_scope="episode"` acikca yazilmazsa **bolum 24, bolum 23'un son karesinden
  baslar**. ROCK 4 `chain_scope="episode"` yazar ve test eder.
- **Baglama sirasi bozuk** (`series/produce.py:1337-1341`): `resolve_shot` prompt'un
  numarali gorsel baglamalarini kurduktan SONRA zincir karesi `image_urls`'in **basina**
  ekleniyor. Prompt "gorsel 1 = obje, gorsel 2 = oda" derken 1. sira artik onceki karedir.
  Duzeltme: tam sirali referans listesi **once** kurulur, etiketler ondan turetilir ve
  URL-etiket karsiligi assert edilir.
- **Sessiz geri dusme:** zincir karesi cikarilip imgbb'ye yukleniyor; yukleme patlarsa
  kosullandirma olmadan **sessizce devam** ediyor. Payload testi mutlu yolda gecerken
  uretim bagimsiz cekimlere donuyor. Duzeltme: fail-closed ya da ROCK 1'in kalici referans
  servisi + **yukleme-patlamasi dusman testi**.
- **[Codex tur-2 FIX kabul] Yeni hata sinifi:** son-kare zinciri, kabul edilmis kucuk bir
  artefakti ya da kotu obje duruşunu sonraki tum cekimlere tasiyabilir. Zincir karesi
  **uygunluk QC'si** + metin-uretimine sessizce donmeyen **kanonik sahneye sifirlama** yolu.

**4c , 10 bolumluk pencere (yalniz 4a gecerse).**
- Tek degisken: gorsel sureklilik. Obje havuzu, baslik kaliplari, anlatim, sure, yuz kurali
  **degismez**.
- **[Codex tur-2 FIX kabul] Gozle kabul 3 degil 10 bolumun HEPSINDE**, ve **yayindan
  ONCE**: her bolumun son kontakt sayfasi bakilir, karar kayda gecer.
  **[Codex tur-3 FIX kabul , yoksa kalite kapisi gunluk yayini durdurur ve CORE FOCUS'u
  ihlal eder]** Bu inceleme havada kalmaz, **mevcut artefakt-tam onay kontrol noktasina**
  baglanir (`publish_mode="approval"` yolu; ROCK 1'in sarti geregi `video`+`release_tag`+
  `approval_msg_id` ucu de dolu, yani onay karti gercekten yenilenebilir). Iki kural:
  (i) inceleme **SLA'si 12 saat**, asilirsa alarm; (ii) pencere boyunca **en az 1 onaylanmis
  bolum onde tutulur** (tampon), boylece inceleme gecikse bile o gunun yayini cikar.
  Tampon biterse bu bir **alarm**dir, sessiz duraklama degil.
- **[Codex tur-2 FIX kabul] Taban yeniden kurulur:** bugunku 7,54 karisik yasta olculdu;
  karsilastirma icin **sabit 72 saat yasta** taban yeniden hesaplanir. Karar bantlari ve
  istatistik **onceden** yazilir.
- **[Codex tur-2 FIX kabul] Kalite hedefi acik kalir:** L/1k 30'a ulasmadan bu is "baska
  deney secerek" Done ilan EDILEMEZ. 30'a ulasilir ya da Ihsan acik bir pivot/kill karari
  verir. 7,54'un altina duserse mudahale geri alinir.
- **Kill-gate:** stack parmak izi degisecegi icin `K8_KILL_GATE_PENCERESI.md` geregi yeni
  pencere acilir, kayda gecer.

**Proof:**
1. `python -m pytest tests/test_shot_conditioning.py -q` , `chain_scope="episode"`
   zorunlu; URL-etiket karsiligi assert; **zincir yuklemesi patarsa uretim baslamaz**
   (dusman testi); bolumler arasi tasima YOK.
2. 4a pilotunun iki kontakt sayfasi ve karsilastirma notu.
3. 10 bolumun her biri icin yayin-oncesi gorsel kabul kaydi.
4. Sabit-72-saat taban ve onceden yazilmis karar bandi raporu.

### ROCK 2 , Alarm kirilmasin
1. **[Codex FIX kabul]** Kritik alarmlar **`parse_mode` olmadan** gonderilir (kacis+fallback
   yerine, daha basit). Markdown yalnizca sunum mesajlarinda.
2. `send_message` yapisal sonuc doner; `last_run.json`'a dokunmaz.
3. **Outbox:** teslim edilemeyen kritik alarm dosyaya yazilir, durum commit'iyle kalici
   olur, sonraki kosuda yeniden denenir; teslim edilene kadar `outcome=failure`.
4. **[Codex FIX kabul] Sira baglayici:** outbox bosaltimi **son `if: always()` persist
   adimindan ONCE**; gercek workflow sirasi test edilir.
5. **[Codex tur-2 FIX kabul] Checkout patlarsa repodaki alarm kodu YOKTUR.** Bu yuzden
   ayri, **checkout'tan bagimsiz** dogrudan bildirim adimi (inline curl + secret) eklenir
   ve checkout/pip/import patlamalari workflow duzeyi proof'a dahil edilir.

**Done:** icinde `_`, `*`, `[` gecen alarm her zaman ulasir; ulasmazsa hat kirmizi olur.
**Proof:** `python -m pytest tests/test_notifier_entity_fallback.py -q` **+ [Codex FIX
kabul]** `_alert` dahil TUM kritik cagri yollari runner cikis kodu + outbox olusumu +
sonraki kosuda teslim uzerinden; **+ checkout-basarisiz senaryosunun workflow testi**.

### ROCK 3 , Yesil isik gercek yayini olcsun + KAPALI WORKFLOW nobeti  [surum kapisi]
1. Tipli `RunResult` + tek atomik yazici.
2. `last_run.json` semasi korunur; `action` ve `last_youtube_publish_at` eklenir.
   **Gecis:** damga `published.json`'daki son dogrulanmis yayindan tohumlanir; yayin
   olmayan her sonuc onu **degistirmeden birakir**.
3. **[Codex FIX kabul]** `action=published` icin 11 karakterlik bicim yeterli degil ,
   kimlik YouTube RSS/API ile dogrulanir.
   **[Codex tur-2 FIX kabul , CIFTE YUKLEME RISKI]** RSS/API yayilimi gecikirse basarili
   bir yukleme "failed" sayilip retry'de **ikinci kez yuklenebilir**. Bu yuzden
   `uploaded_pending_verification` kontrol noktasi: mevcut kimlik yoklanir, dogrulama
   belirsizken **asla yeniden POST edilmez**.
   **[Codex tur-3 FIX kabul , bu kontrol noktasinin KENDI on kosulu var]** Mevcut yukleyici
   HTTP 200 donen ama **hicbir kimlik icermeyen** cevaplari kabul ediyor
   (`core/uploader.py` kimlik cikarma yollari `None` donebiliyor; `published.json`'da
   `instagram`/`tiktok` alanlari `null` ve `results_raw` yalnizca "Upload initiated
   successfully in background" diyor). Kimlik yoksa "bekliyor" durumu sonsuza kadar
   asili kalir. Sart: ya **dayanikli bir arama/idempotency anahtari** (yukleme oncesi
   uretilen, cevaptan bagimsiz, sonradan kanalda aranabilen bir isaret , or. baslik/
   aciklama icine gomulu bolum kimligi), ya da **kimliksiz kurtarma yolu** acikca
   tanimlanir ve test edilir: ne yeniden POST eder, ne sonsuza kadar bekler
   (sinirli yoklama -> `needs_human` + alarm).
4. **[Codex FIX kabul]** Runner hic olusmadan patlayan durumlar icin workflow'a ait ayri
   hata zarfi; runner ciktisi icin tek atomik yazici korunur.
5. **[Codex FIX kabul]** Nobet esigi 12 saat DEGIL (yayin slotu 18:30 UTC; 12 saatlik yas
   her sabah 09:00'da bagirirdi). **Beklenen-slot son tarihi + tolerans.**
   **[Codex tur-2 FIX kabul]** 3 saatlik tolerans planin KENDI olcumuyle celisiyor ,
   `kie-uretim` kuyruk gecikmeleri 30-31 Ag'da **+397 dakikaya** kadar cikti. Cozum:
   tolerans tek basina yetmez, **kuyrukta/kosuyor/patladi durumlari ayirt edilir**
   (GitHub run state) ve secilen tolerans 24 saat sozunun altinda kalir.
6. **YENI:** watchdog izlenen her hattin GitHub `state` alanini okur; `active` degilse
   KRITIK alarm. Bugunku arizayi mevcut nobetci hic goremez.
7. **[Codex CLARIFY kabul]** 5 ve 6 **ikinci repoda** (`akilli-watchdog`), buradan
   okunamiyor. Bu maddeler **BLOKE**; plandaki config alintilari **dogrulanmamis iddia**.
   ROCK 4 bu bloke isi beklemez.

**Done:** bugunku senaryo (hold + kapali workflow) tekrarlansa 24 saatin altinda alarm.
**Proof:** `python -m pytest tests/test_last_run_contract.py -q` (held kosu success yazmaz;
IG-only `failed`; no-op damgayi ilerletmez; dis dogrulama belirsizken cifte yukleme YOK)
**+ [Codex tur-2 FIX kabul] gecis matrisi tek basina yetmez:** bes sema yazicisinin
**calistirilabilir workflow sozlesme kontrolu** ve 12 runner cagiricisinin duman testi.

---

## 5. IHSAN'IN KARAR VERMESI GEREKENLER

1. **`Unnatural Lab Daily` workflow'unu kim/neden kapatti?** (30 Ag 21:29 , 31 Ag 18:30
   arasi, elle). Repodan kanitlanamiyor. Bilerek kapatildiysa ROCK 0 yanlis olur. Aciliyor mu?
2. **Kredi:** part 23'e 436 yanmis, gercek tavan **800**, kalan **364** , dort taze cekime
   muhtemelen yetmez. (i) part 23 `skipped` + part 24'ten devam mi, (ii) kayda gecen tek
   seferlik tavan istisnasi mi?
3. **ROCK 1-3 yayilimi:** motor ortak (12 workflow / 5 sema yazicisi). Codex'in onerisi ve
   benim tavsiyem: **once yalniz Sentinal'de canary, sonra filo.** Onayliyor musun?
4. **[Codex CLARIFY , UC turdur acik, artik ROCK 2'nin Done sartidir]** Kirmizi GitHub
   job'i ikinci bildirim kanali sayiliyor. **Basarisiz job bildirimlerini gercekten aliyor
   musun** (mail/mobil), 24 saat icinde? Almiyorsan ROCK 2'nin ikinci katmani YOKTUR ve
   24 saat sozu tek kanala dayanir.
   **Kural:** bu kanal **dogrulanana** (test bildirimi gonderilip alindigina dair kanit)
   kadar ROCK 2 "bitti" ilan EDILEMEZ; alternatifi bagimsiz dogrulanmis ikinci bir hedef
   (ayri Telegram sohbeti / e-posta) eklemektir.

**[Codex tur-2 KILL kabul]** Onceki revizyondaki 5. soru (gorme-analizi saglayicisi)
**kaldirildi** , revize ROCK 4 payload testleri ve elle kontakt sayfasi kullaniyor,
o saglayiciya ihtiyaci yok. (`higgsfield.video_analysis_create` sonraki cevrimin konusu.)

## 6. KAPSAM DISI (bu cevrimde yapilmayacak)

- Kalite kapisini gevsetmek. Fail-closed dogru; sorun cikis yolunun olmamasi.
- QC modelini degistirmek. **[Codex FIX kabul]** Onceki revizyon bunu `ISSUES.md` ROCK
  C2'ye dayandiriyordu , **yanlis alinti, kaldirildi**. C2 yalnizca QC model envanteridir.
- `virality_predictor`'i yayin bloke eden kapi yapmak (kalibre degil).
- Duraklatilmis 6 Sentinal serisini diriltmek.
- `kie-uretim` concurrency kuyrugu (olctum: gecikmeler 20-24 Ag'da +40 dk iken 30-31 Ag'da
  +119..+397 dk; 28 Ag'da eklenen next-stop 5. hat oldu) -> `ISSUES.md`.
  **Not:** ROCK 3'un tolerans secimi bu olcume bagimli , kuyruk yeniden tasarlanmasa da
  durum ayrimi ROCK 3 kapsamindadir.
- TikTok boost (#33), upscale, Apify havuz beslemesi, `video_analysis_create` -> sonraki cevrim.

## 7. RISKLER

- ROCK 0 kredi harcar; part 23'te 436 yanmis, kalan yalnizca 364.
- ROCK 1 durum makinesini degistirir ve **12 workflow** ayni motoru cagirir , bu yuzden
  once Sentinal canary, surum kapisiyla filoya yayilim.
- ROCK 3'un 5-6. maddeleri **ikinci repoya** bagimli ve acikca BLOKE; ayni cevrimde
  yapilmazsa 24 saat sozu tutulmaz.
- **ROCK 4 en riskli rock:** gorsel kosullandirmayi acmak uc bilinen kusuru (chain_scope
  varsayilani, baglama sirasi, sessiz geri dusme) tetikleyebilir ve son-kare zinciri yeni
  bir bulasici artefakt sinifi dogurabilir. Bu yuzden once yayinlanmayan esli pilot.
- ROCK 4 kill-gate penceresini sifirlar; olcum yeniden 10 bolum bekler.
- Alarm outbox'i durum commit'ine baglidir; persist adimi patlarsa alarm kuyrukta kalir.
- **Kanit sinirlari:** kontakt sayfalari iki bolume dayanir (n=2) ve
  `chain_frames=False` kanitlanmis tek kok neden degil, sinanacak hipotezdir.

---

# EK , TUR 3 SONRASI BULUNANLAR (2026-09-01, ROCK 0 uygulanirken + bagimsiz panel)

Bu bolum, plan r4 yazildiktan SONRA uretilen kanitlari tasir. Ucu de plani degistiriyor.
Bagimsiz panel: 29 ajan, 5 mercek, her bulgu 2 celiskici dogrulayiciyla sinandi
(25 ham -> 25 benzersiz -> ilk 12 dogrulandi -> 5 blocking onaylandi; 13 dusuk-siddetli
bulgu DOGRULANMADI, kapsam disi birakildi). Asagidakilerin hepsini KODDA kendim dogruladim.

## EK-1 , NOBETCI OLU: kendi testi onu her ay basi olduruyor  [YENI, EN KRITIK]

`akilli-watchdog` workflow'unda `Nobet` adiminin ONUNDE kosulsuz bir test adimi var ve
`Nobet`'in `if:` korumasi YOK:

    - name: Kurulum testleri (agsiz, anahtarsiz)
      run: python -m unittest discover -s tests -p "test_*.py" -v
    - name: Nobet          # <- if: yok, testler patlayinca ATLANIR

`tests/test_kurulum.py:391`: `self.assertTrue(ac.check_actions_quota(100)["healthy"])`.
`check_actions_quota` ay sonu PROJEKSIYONU yapiyor. Bu makinede birebir urettim:

    kullanilan  100 -> healthy=False  projeksiyon=3000     (ayin 1'i: 100 / (1/30))
    kullanilan 1650 -> healthy=False  projeksiyon=49500
    kullanilan 1900 -> healthy=False  projeksiyon=57000

Yani **ayin ilk gunlerinde 100 dakika bile "saglksiz" projekte ediliyor**, test patliyor,
job exit 1 veriyor ve **nobet adimi hic calismiyor**.
Kanit: kosu 33493291124 (2026-09-01 09:38) `FAILED (failures=1)` +
`##[error]Process completed with exit code 1`; log'da CANLI saglik kontrolu ciktisi YOK
(satir 1-221 yalniz runner kurulumu, 222+ unittest).

**Zaman cizelgesi , 24 saat sozunun nerede koptugu:**
| an | olay |
|---|---|
| 31 Ag 11:12 | Nobetci kostu, DOGRU davrandi: `unnatural-lab.yml -> success`, kanit taze (13,8 sa), `Sorun Sayisi: 0` |
| 31 Ag 11:12-18:30 | Workflow elle kapatildi (bu araliktan sonra) |
| 1 Eyl 09:38 | Nobetci **kendi testinde oldu**, nobet adimi atlandi -> kimse haber almadi |

**UYARI , yorumlamada duzeltme:** kosu logundaki `🚨 [Is kaniti] Hat: kanit 84.0 saatlik`
ve `[Kie kredi] bakiye 1200` gibi satirlar **birim test fixture'larilidir**, canli bulgu
DEGILDIR (ayni checker sirayla 1200/3000/3001/3002,5 yaziyor, Temmuz tarihleri kullaniyor).
Ilk okumamda bunlari canli sanmistim; duzeltildi.

**Plan etkisi:** ROCK 3'un 5-6. maddeleri **YENIDEN YAZILMALI**. `state != active` kritik
alarmi ZATEN VAR (`actions_checker.py:371-388`, `disabled_manually` acikca adlandirilmis)
ve `youtube-automation` ZATEN hedef listesinde (`config.py:138`). Eksik olan kontrol degil:
(a) nobetcinin kendisi ayin basinda oluyor, (b) `FLEET_PAT` olmadan Actions nobeti kor.
Yeni ROCK 3 maddesi: **nobetciyi kendi testinden ayir** (`Nobet` adimina `if: always()`
ya da testleri ayri job'a al) + tarih bagimli kota testini duzelt + PAT varligini
fail-closed dogrula.

## EK-2 , UCUNCU SESSIZ OLUM MEKANIZMASI: defter birlestirme olu  [YENI]

`scripts/merge_credits_ledger.py:36-41` korumasi `set(doc) == {"entries"}`. Canli defterde
`{'entries', 'episode_spend'}` var (`episode_spend` 2026-08-28'de eklendi, birlestirme
script'i 2026-08-13'te yazilmis). Bu makinede calistirdim:

    canli defter anahtarlari: {'entries', 'episode_spend'}
    is_ledger(canli defter) = False

Sonuc: es zamanli kosularda defter catismasi olursa birlestirme exit 1 verir,
`persist_state.sh` fail-closed dala girer ve **durum commit'inin TAMAMI dusar**
(series.json ilerlemesi, published.json, last_run.json repoya HIC ulasmaz).
Ustelik koruma gevsetilse bile satir 74 dosyayi `{"entries": merged}` olarak yeniden
yaziyor , **`episode_spend`'i SILERDI**, yani `credit_gate`'in dayandigi bolum butcesi
muhasebesi ucar.

**Plan etkisi:** ROCK 1.6 `credits_ledger.json`'i "tek yetkili sayac" ilan ediyor ve
ROCK 2.3 alarm outbox'ini "durum commit'ine" bagliyor , **ikisi de bu kirik yolun
uzerinde duruyor.** Bu, ROCK 1'in on kosulu olarak plana girer.

## EK-3 , ZINCIR KARESI SESSIZ GERI DUSMESI SANDIGIMDAN KOTU  [ROCK 4b duzeltmesi]

Plan 4b "yukleme patlarsa kosullandirmasiz sessizce devam eder" diyordu. Kod daha kotu:
`produce.py:1501-1510` (omni) ve `1647-1656` (visual): `if lf:` / `if up: chain_url = up`
dallarinin **else'i yok**. Cekim kabul edildiginde (`status == "ok"`) ama kare cikarma ya
da yukleme None donduğunde `chain_url` **onceki cekimin karesinde kaliyor** , sifirlama
yalnizca `previous_shot_dropped` (yani `status != "ok"`) durumunda tetikleniyor.
Yani cekim 4, cekim 2'nin son karesiyle kosullandirilabilir ve **bu yolda tek bir log
satiri bile yok**. Bagimlilik yine imgbb , kanali olduren CDN'in ta kendisi.

## EK-4 , ROCK 0 CANLI SONUCU: hipotez dogrulandi, part 24 terk edildi

- Kosu 33533304587: cekim 1 iki kez reddedildi ("acilis karesinde imkansiz ozellik
  okunmuyor"). Sebep plan metniydi (tetikleyici fiiller).
- Cekim 1 "kurulmus durum" olarak yeniden yazildi (commit 5ab27cd). Kosu 33534926748:
  **`QC GECTI: cekim 1, artifact 0/10 (regen 1 sonrasi)`** , duzeltme tuttu.
- Ayni kosu **cekim 2**'de dustu: *"cekimler arasi tezgah, isik veya obje-durumu
  surekliligi bozuk"*. **ROCK 4'un hipotezi icin canli kanit.**
- `episode_spend["unnatural-lab:24"] = 512/800`. Panel gercek `CapAwareRegenAllocator` ile
  simule etti: 4 ana cekim icin muhafazakar tahminle **400 kredi taban** gerekir, ONE regen
  icin 484; 288 kalan **aritmetik olarak yetersiz**. Part 24 `skipped`, part 25'e gecildi
  (Ihsan karari).
- **Plan etkisi , YENI KURAL:** ROCK 1'e "bolum butcesi tukenmis bolum" kurali eklenmeli.
  `credit_gate.reserve` `amount = tavan - harcanan <= 0` oldugunda `False` donuyor ve bolum
  **kalici olarak tavan-kilidinde** kaliyor , bu, planin kapatmadigi IKINCI olum kuyusudur.

## EK-5 , LINT BOSLUGU: tetikleyici fiil kalibi yakalanmiyor  [ROCK 5 adayi]

`series/shots.py:46-50` `SHOT1_ONSET_LANGUAGE` yalnizca `begins/starts to` ve
`begins/starts <fiil>ing` kaliplarini ariyor. Part 24 ("tilt the mug... streams out...
curving upward"), part 25 ("drop the ball... immediately crushes the can flat") ve
part 26 ("the tines slowly curl inward") **ucu de** `plan_lint`'ten TEMIZ geciyordu.
Part 24 ve 25 elle duzeltildi; **part 26 hala bu kusurda.**
Bu, Codex'in `state_carry` lint'i icin gosterdigi boslugun ucuncu ornegi: metin lint'i
geciyor, uretilen goruntu kaliyor.

## EK-6 , ROCK 4c'nin onay kapisi gunluk yayinla CELISIYOR  [panel, blocking]

`unnatural-lab.yml`de onay adimi (:74-78) ve uretim adimi (:83-89) **ayni gunluk job'da**;
`series-approve.yml` cron'u YORUMDA. `approver.py:102-106` yalnizca `next_part`'a bakiyor.
`series_runner.py:393-395` `awaiting_approval` gorunce uretimi sert blokluyor; `:403-407`
o gun kanala yayin yapilmissa yine uretmiyor. Sonuc: onay-kapili pencerede kadans
**iki gunde bire** duser ve planin "en az 1 onaylanmis bolum onde tampon" sarti
mimari olarak kurulamaz , CORE FOCUS'un "her gun 1 video" ayagi ihlal edilir.
**Plan etkisi:** ROCK 4c'nin gozle-kabul mekanizmasi yeniden tasarlanmali (or. yayin
oncesi kabul ayri bir kosuda ve uretimden bagimsiz kuyrukla).
