# RF-PLAN , flashpoints: brief celiskisini bitir + kunye kuralini kanal ayarina bagla

Tarih: 10 Eylul 2026 (Los Angeles)
Dal: `codex-brief-v18` (worktree; ana agacta bes baska oturum var)
Integrator: Codex
Revizyon: r2 (Codex turu 1 sonrasi , iki temel varsayim duzeltildi)

## Core Focus (tek cumle)

Uretici model tek bir kural kumesi okusun: sayilar tek kaynaktan gelsin ve kunye
taninir bir sey adlandirsin.

---

## Prompt'un yapisi (turu 1'de dogrulandi, plan bunun uzerine kuruluyor)

`series/replenish.py:617` `_build_prompt(...) -> tuple[str, str]` ve docstring'i
`"(contents, system_instruction) döndür"` diyor. Yani modele IKI AYRI kanal gidiyor:

| Kanal | Icerigi | Oncelik |
|---|---|---|
| `system_instruction` | JSON semasi, TITLE_CARD kurali (`:748`), sema yer tutucusu (`:701`), NARRATION kurali `{wmin}-{wmax}` (`:740`), tempo/tam-cumle kurallari (`:732-739`) | YUKSEK |
| `contents` | SERIES/ART STYLE, **CREATIVE BRIEF** (`:1021-1023`), calibration, topic pool, history | kullanici seviyesi |

Bu, planin ilk surumundeki iki varsayimi curutuyor:

**DUZELTME 1 (Codex turu 1, hakliydi):** "v1.8 modele hic ulasmadi" iddiam YANLISTI.
Sistem prompt'u v1.8'i zaten basiyor , `:740` kelime butcesini yapisal config'ten
(`{wmin}-{wmax}` = 26-36) uretiyor, `:732-739` ise "measured documentary pace of
~2 words per second", konusma penceresi ve "must end with a complete sentence"
kurallarini basiyor (`voiceover_continuity` acik oldugu icin). Gercek kusur
EKSIKLIK degil, **CELISKI**: brief ayni sayilari farkli soyluyor.

**DUZELTME 2 (Codex turu 1, hakliydi):** kullanici seviyesindeki brief, sistem
seviyesindeki sabit kurali guvenilir bicimde EZEMEZ. Rock 2'nin ilk surumu bu
yuzden saglam degildi ve degistirildi.

---

## Kusur A: brief, sistem talimatiyla CELISIYOR

`auto_replenish.brief` metnindeki uc ifade:

| brief (contents) | sistem talimati / yapisal config |
|---|---|
| "dayanak: KONSEPT.md **v1.6**, 2026-07-29" | doktrin **v1.8** (2026-09-01) |
| "Iki cekim vardir, toplam yaklasik **12 sn**" | `shots: 2` x `shot_seconds: "10"` |
| "Narration **26-38** kelimedir" | `:740` prompt'a **26-36** basiyor |

Model ayni prompt icinde hem 26-36 hem 26-38 goruyor. Bu, en iyi ihtimalle
gurultudur; kotu ihtimalle kullanici metni sistem kuralini gevsetir.

## Kusur B: kunye kurali "ozne adini yaz" diyor

Iki yerde birden, ikisi de `system_instruction` icinde:

- `:748` `'- TITLE_CARD: "title" = the subject/site name (max 40 chars)'`
- `:701` sema yer tutucusu: `"title": "<subject name, max 40 chars>"`

Konu bilinmeyen bir kisi veya yer oldugunda bu, kunyeye TANINMAYAN bir ozel isim
yazdirir. Son 1 haftanin olcumu (7 bolum, yt-dlp + ffmpeg, kareler goz ile
incelendi):

| Kunyede yazan | Izlenme |
|---|---|
| BROOKLYN BRIDGE / New York City, 1883 | **511** |
| HUNDRED YEARS' WAR / Europe, 1337-1453 | **107** |
| THE GREAT WALL | 25 |
| GREAT FIRE OF LONDON | 23 |
| KISKA INVASION / Aleutian Islands, 1943 | 19 |
| HENRY "BOX" BROWN / Richmond, 1849 | 5 |

Belirleyici kanit Kiska: ilk karesi haftanin **en parlagi** (132/255) ve
kompozisyonu en iyisi , teknik olarak kusursuz, YouTube basligi da iyi
("The Real Reason America Invaded An Empty Island!"). Kunyedeki taninmayan ozel
isim tek basina harcadi.

Tam katalog (29 bolum): baslik KALIBI hicbir sey ongormuyor (her kalipta hem hit
hem sifir var), baslikin OZNESI onguruyor , SEY medyan 80, OLAY 20, KISI 8.
Ayrinti: `shadowedhistory/REELYZE-RAPOR.md` "EK , BASLIK ANALIZI".

---

## Rock 1: brief'ten cakisan SAYILARI cikar (yeniden yazmak degil, CIKARMAK)

**Yapilacak:** `shadowedhistory/flashpoints/series.json` -> `auto_replenish.brief`:

1. `dayanak: ... KONSEPT.md v1.6, 2026-07-29` -> `v1.8, 2026-09-01`
2. `(1) IMZA FORMAT` icindeki **"toplam yaklasik 12 sn"** ifadesi SILINIR.
   Yerine baska bir sure YAZILMAZ. Cumlenin geri kalani (iki cekim, shot 1
   CARPMA / shot 2 KANIT-BUKUM tarifi) aynen kalir.
3. `(5) SES` icindeki **"26-38 kelimedir"** ifadesi SILINIR. Yerine baska bir
   sayi YAZILMAZ; cumle "Narration uzunlugu ve temposu sistem talimatindaki
   NARRATION kuralina tabidir" gibi bir yonlendirmeye cevrilir.

**Neden yeniden yazmak degil silmek:** sayiyi brief'te de tekrarlamak, bugunku
kaymanin ta kendisini uretti , config degisti, prose degismedi. Codex turu 1
ayrica "~19 sn yazmak da sistem prompt'undaki ham sure ifadesiyle catisir" dedi.
Tek kaynak yapisal config olsun; brief SAYI TASIMASIN.

**DOKUNMA:** `narration.min_words/max_words`, `shots`, `shot_seconds` , ucu de
dogru, yapisal config degismiyor.

## Rock 2: kunye kuralini kanal ayarina bagla (`title_style` emsaliyle)

**Neden brief yetmiyor:** kural `system_instruction` icinde; brief `contents`
icinde. Kullanici metni sistem kuralini guvenilir bicimde ezemez.

**Emsal:** ayni dosyada `:729` `title_rule = title_style or (varsayilan)`.
YouTube BASLIK kurali zaten kanal ayariyla eziliyor. Kunye kurali icin AYNI
kalip kullanilacak , yeni bir mimari degil, mevcut kalibin ikinci kullanimi.

**Yapilacak:**

1. `series/replenish.py`, `_build_prompt` icinde `title_card_style` oku
   (`cfg.get("title_card_style")`), ve **IKI yeri birden** ezsin:
   - `:748` `tc_rule` , ayar varsa onun metni kullanilir
   - `:701` `tc_shape` yer tutucusu , ayar varsa `"<subject name, max 40 chars>"`
     yerine ayarin belirttigi tarif yazilir
   Ayar YOKSA her iki yer de BUGUNKU metni aynen uretir. Diger uc kanalda bu
   anahtar olmadigi icin ciktilari BIT BIT AYNI kalir.
2. `shadowedhistory/flashpoints/series.json` -> `auto_replenish.title_card_style`
   eklenir. Metnin soylemesi gerekenler:
   - `title`, ORTALAMA IZLEYICININ TANIDIGI bir seyi adlandirir.
   - Konu bilinmeyen bir kisi veya yer ise o isim kunyeye YAZILMAZ; hikayedeki
     taninir sey (yapi, nesne, olay tipi, kavram) yazilir. Konu ELENMEZ, yalnizca
     kunyenin OZNESI degisir.
   - Taninir bir ozel isim varsa dogrudan o yazilir.
   - `subtitle` yer + yil tasir; yer TANINIR olani olmali (bilinmeyen bolge adi
     tek basina yazilmaz).
   - Olculmus ornekler: iyi -> `BROOKLYN BRIDGE / New York City, 1883`;
     kotu -> `KISKA INVASION / Aleutian Islands, 1943`, duzeltilmisi ->
     `EMPTY ISLAND INVASION / Alaska, 1943`.
   - Uzunluk sinirlari korunur (title <=40, subtitle <=48 veya yil_gerekli
     modunda <=60/<=60; mevcut `validate_title_card` kurallari degismez).

**DOKUNMA:** `tc_rule`'un `tc_year_required is False` kolu (`:745-746`, celestial
metni , event-horizon'a ait), `validate_title_card`, `title_style`.

---

## PROOF

Yeni dosya: `tests/test_flashpoints_brief_sozlesmesi.py`

Test METNI degil MODELE GIDEN IKI KANALI denetler ve ikisini AYRI AYRI ele alir
(Codex turu 1: tek siralanmis prompt gibi davranmak yanlis).

`_build_prompt` cagrilabilirligi turu 1'de dogrulandi: ag, API anahtari,
calibration veya dolu history gerekmiyor; `series.replenish` import'u
`python-dotenv` + `requests` istiyor ve import aninda `logs/` ile cikti
klasorlerini olusturuyor , test depo kokunden calistirilir.

1. **Iki kanal ayri ayri alinir.** `contents, system_instruction = _build_prompt(...)`
   flashpoints'in GERCEK `SeriesMeta`, `Bible` ve `auto_replenish` degerleriyle.
2. **Brief `contents` icinde, kural `system_instruction` icinde** , test bu
   ayrimi acikca dogrular (yer degistirirlerse test duser).
3. **Brief SAYI TASIMIYOR:** `contents` icindeki CREATIVE BRIEF BOLUMU IZOLE
   EDILIR (baslik satirindan bir sonraki bolum basligina kadar) ve o blokta
   `\d+\s*-\s*\d+\s*kelime` ile `\d+\s*sn` kaliplarinin HICBIRI eslesmez.
   Codex turu 1: yalniz "12 sn" ve "26-38" dislamak zayif , baska yanlis bir
   sayi da gecerdi.
4. **Sistem talimati sayiyi yapisal config'ten basiyor:** `system_instruction`
   icindeki NARRATION satirindaki aralik, `auto_replenish.narration` degerleriyle
   AYNI (test iki kaynagi karsilastirir, sabit yazmaz).
5. **Dayanak guncel:** brief blogu "v1.8" gecer, "v1.6" GECMEZ.
6. **Kunye kurali sistem talimatinda:** `system_instruction` taninirlik
   KURALININ KENDISINI tasir , yalnizca ornekler degil. En az su uc sey ayri ayri
   aranir: (a) bilinmeyen ismin yazilmayacagi YASAGI, (b) yerine taninir seyin
   yazilacagi TALIMATI, (c) `EMPTY ISLAND INVASION` duzeltilmis ornegi.
   Codex turu 1: parcalara bakmak, tersine cevrilmis veya disi sokulmus bir
   kurali da gecirirdi.
7. **Sema yer tutucusu da degismis:** `system_instruction` icindeki JSON
   semasinda `"<subject name, max 40 chars>"` GECMEZ.
8. **Bos gecmeyen capa (Codex turu 1 [KILL] sonrasi yeniden yazildi):**
   `title_card_style` ve `brief` BOSALTILMIS bir cfg kopyasiyla ayni cagri
   yapilir ve YALNIZCA brief'e/ayara AIT isaretler kaybolur:
   - kaybolmali: taninirlik kurali, `EMPTY ISLAND INVASION`, CREATIVE BRIEF blogu
   - KAYBOLMAMALI: `{wmin}-{wmax}` araligi, tempo/tam-cumle kurallari, JSON
     semasi , bunlar yapisal config'ten gelir ve brief bosken de durmalidir.
   Eski surum "her sey kaybolsun" diyordu ve imkansizdi.
9. **Diger kanallar bit bit ayni:** `title_card_style` TASIMAYAN bir kanal
   (`event-horizon`) icin uretilen `system_instruction`, bu kosudan ONCEKI kodla
   uretilen metinle AYNI olmali. Pratik test: ayar yokken `tc_rule` ve `tc_shape`
   bugunku sabit metinleri birebir uretir.
10. **JSON butunlugu:** `series.json` gecerli JSON; `topic_pool` girdi sayisi,
    `next_part`, `parts` ve `title_style` degismemis.

**Calistirma:**

```
python -m pytest tests/test_flashpoints_brief_sozlesmesi.py -q
```

**Regresyon kapisi:**

```
python -m pytest tests/test_doctrine_gate.py tests/test_flashpoints_kanal_sozlesmesi.py -q
```

---

## Kapsam disi , Codex turu 1'de bulundu, GERCEK, ama bu kosuda YOK

- **`gentle, loopable resolve` celiskisi:** sabit bolum-yayi metni, flashpoints'in
  "daha yakin ve sert, eylem surerken biten" ikinci cekimiyle catisiyor.
  Ayri rock; bolum yayi metnini kanal ayarina baglamak gerekir.
- **`topic_pool` tam sayi tohum varsayimi:** motor `n15-...` bicimli string ID'li
  calibration kart konulari enjekte edebiliyor ve onlari once istiyor; brief
  "tam sayi seed_id zorunlu" diyor. Bugun `extra_topics` bos oldugu icin
  patlamiyor , sessiz bir mayin.
- **Aile tekrari istisnasi:** brief "ayni aile ust uste kullanilamaz" diyor,
  motor ise baska aile kalmadiginda ilk bolumde tekrara IZIN veriyor.
- **Hicbir dogrulayici taninirligi ZORLAMIYOR:** `_validate_batch` uzunluk ve yil
  disinda kunyeye bakmiyor. Yani bu kosu prompt'u duzeltir, CIKTIYI garanti
  ETMEZ. Garanti istenirse tohum basina deterministik kunye etiketi veya kanal
  kapsamli bir dogrulama sozlesmesi gerekir.
- `auto_replenish.title_style` , "Fact Or Ancient Propaganda?" kalibi olculdu
  (4 kullanim, medyan 24 = kanal medyani) ama n=4 ve icinde 143 izlenmeli
  Colosseum var; kalip kaldirmak icin kanit yetersiz.
- `KONSEPT.md`, `calibration.json`, `topic_pool` icerigi, kuyruktaki planlar.
