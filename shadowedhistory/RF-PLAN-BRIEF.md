# RF-PLAN , flashpoints uretim brief'ini gercege dondur

Tarih: 10 Eylul 2026 (Los Angeles)
Dal: `codex-brief-v18` (worktree; ana agacta bes baska oturum var)
Integrator: Codex

## Core Focus (tek cumle)

Uretici modelin OKUDUGU metin, kanalin bugun gecerli kurallariyla ayni seyi
soylesin , ve kunye taninir bir sey adlandirsin.

---

## Sorun , ikisi de olculdu

### Kusur A: brief v1.6'da kalmis, yapilandirma v1.8'e gecmis

`series.json` -> `auto_replenish.brief` metni prompt'a "CREATIVE BRIEF for new
episodes" olarak enjekte ediliyor (`series/replenish.py:1021-1023`) ve prompt
modele *"follow the CREATIVE BRIEF strictly"* diyor (`:741`). Yani model icin
KAYNAK metin budur.

Ama metin hala v1.6 kurallarini tasiyor:

| brief ne diyor | v1.8 ve yapisal config ne diyor |
|---|---|
| "dayanak: KONSEPT.md **v1.6**, 2026-07-29" | doktrin **v1.8** (2026-09-01) |
| "Iki cekim vardir, toplam yaklasik **12 sn**" | `shots: 2` x `shot_seconds: "10"` = **~19 sn** |
| "Narration **26-38** kelimedir" | `narration: {min_words: 26, max_words: 36}` |

Yani model her bolumde "12 saniyelik iki cekim, 26-38 kelime" hedefiyle yaziyor,
boru hatti ise 2x10 sn uretip 26-36 kelime dogruluyor. `KONSEPT.md:29-42` v1.8'i
Ihsan'in 2026-09-01 karari olarak kaydediyor; gerekcesi izleyici geri bildirimi
(*"konusmaci cok hizli konusuyor ve cumlesini bitiremeden video bitiyor"*).
Brief guncellenmedigi icin o karar modele HIC ULASMADI.

### Kusur B: kunye kurali yok, ve olculen fark tam orada

Motorun sabit kurali (`series/replenish.py:748`):
`'- TITLE_CARD: "title" = the subject/site name (max 40 chars)'`

"Ozne adi" demek, konu bilinmeyen bir kisi veya yer oldugunda kunyeye TANINMAYAN
bir ozel isim yazilmasi demek. Son 1 haftanin olcumu (7 bolum, yt-dlp + ffmpeg,
kareler goz ile incelendi):

| Kunyede yazan | Izlenme |
|---|---|
| BROOKLYN BRIDGE / New York City, 1883 | **511** |
| HUNDRED YEARS' WAR / Europe, 1337-1453 | **107** |
| THE GREAT WALL | 25 |
| GREAT FIRE OF LONDON | 23 |
| KISKA INVASION / Aleutian Islands, 1943 | 19 |
| HENRY "BOX" BROWN / Richmond, 1849 | 5 |

Belirleyici kanit Kiska: ilk karesi haftanin **en parlagi** (132/255) ve
kompozisyonu en iyisi (asker cikarmasi, derinlik, net ozne) , teknik olarak
kusursuz. YouTube basligi da iyiydi ("The Real Reason America Invaded An Empty
Island!"). Kunyedeki taninmayan ozel isim tek basina harcadi.

Henry Box Brown'da iki kaldirac birden yanlis: bilinmeyen kisi adi ARTI haftanin
en karanlik karesi (36/255, tahta sandik ici, taninir hicbir sey yok).

Tam katalog (29 bolum) ayni yone isaret ediyor: baslik KALIBI hicbir sey
ongormuyor (her kalipta hem hit hem sifir var), baslikin OZNESI onguruyor ,
SEY medyan 80, OLAY 20, KISI 8. Ayrinti: `shadowedhistory/REELYZE-RAPOR.md`
"EK , BASLIK ANALIZI".

---

## Rock 1: brief'i v1.8 ile hizala

**Yapilacak:** `shadowedhistory/flashpoints/series.json` ->
`auto_replenish.brief` metni icinde UC ifade duzeltilir:

1. `dayanak: shadowedhistory/KONSEPT.md v1.6, 2026-07-29`
   -> `dayanak: shadowedhistory/KONSEPT.md v1.8, 2026-09-01`
2. `(1) IMZA FORMAT: Iki cekim vardir, toplam yaklasik 12 sn.`
   -> sure ~19 sn olacak sekilde (iki cekim x 10 sn). Metnin geri kalani
      (shot 1 CARPMA / shot 2 KANIT-BUKUM tarifi) AYNEN kalir.
3. `(5) SES: Narration 26-38 kelimedir`
   -> `26-36`. Ayrica v1.8(c) ve v1.8(d) kurallari eklenir: anlatim DAIMA tam
      cumleyle biter, register olculu ve acele etmeyen belgesel anlatimidir.
      (Su an brief bunlari hic soylemiyor; v1.8 ikisini de acikca karara bagladi.)

**DOKUNMA:** `narration.min_words/max_words` (zaten 26-36, dogru),
`shots`, `shot_seconds` (zaten 2 ve "10", dogru). Yapisal config DOGRU;
duzeltilecek olan yalniz METIN.

## Rock 2: kunye kurali brief'e girsin

**Yapilacak:** ayni `brief` metnine YENI bir numarali kural eklenir (mevcut
kurallarin numaralandirmasi bozulmadan, sona (9) olarak):

Kuralin soylemesi gerekenler:
- Kunyenin `title` alani, ORTALAMA IZLEYICININ TANIDIGI bir seyi adlandirmali.
- Konu bilinmeyen bir kisi veya yer ise, kunye O ISMI YAZMAZ , hikayedeki
  taninir seyi (yapi, nesne, olay tipi, kavram) yazar. Konu ELENMEZ, yalnizca
  kunyenin OZNESI degisir.
- Taninir bir ozel isim varsa (Brooklyn Bridge, Colosseum, Eiffel Tower,
  Hundred Years' War) dogrudan o yazilir.
- `subtitle` yer + yil tasimaya devam eder, ama yer TANINIR olani olmali
  (ornek: "Nubia, Egypt" yerine "Abu Simbel, Egypt"; bilinmeyen bolge adi tek
  basina yazilmaz).
- Olculen ornekler kurala EK olarak yazilir ki model neyi kastettigimizi gorsun:
  iyi -> BROOKLYN BRIDGE / New York City, 1883 ; kotu -> KISKA INVASION /
  Aleutian Islands, 1943.

Metin brief'in geri kalaniyla ayni dilde (Turkce) ve ayni uslupta yazilir.

**DOKUNMA:** `series/replenish.py` icindeki sabit `TITLE_CARD` kurali. Motor
dort kanali besliyor ve bu bulgu YALNIZ flashpoints'te olculdu; kanal kapsamli
kural kanal dosyasina yazilir. Prompt zaten "follow the CREATIVE BRIEF strictly"
diyor, yani brief motor metnini daraltabilir.

---

## PROOF

Yeni dosya: `tests/test_flashpoints_brief_sozlesmesi.py`

Bu test METNI degil, MODELE GIDEN PROMPT'U denetler. Gerekcesi: brief'i
duzeltmek ancak prompt'a girdigi olculde bir sey degistirir; config'e dogru
cumleyi yazip prompt'un onu tasidigini varsaymak bos bir kanittir.

Testin olcmesi gerekenler:

1. **Prompt gercekten kuruluyor.** Kurucu fonksiyon
   `series.replenish._build_prompt(meta, bible, cfg, start, batch, history,
   fix_errors=None, calibration=None)` (satir 617) flashpoints'in GERCEK
   `SeriesMeta` + `Bible` + `auto_replenish` degerleriyle cagrilir; iki elemanli
   bir demet doner, prompt metni o demettedir. Ciktida `CREATIVE BRIEF for new
   episodes:` basligi ve brief metni GECER.
2. **Sure celiskisi bitti:** uretilen prompt'ta "12 sn" IFADESI GECMEZ.
3. **Kelime butcesi celiskisi bitti:** prompt'ta "26-38" GECMEZ, "26-36" GECER,
   ve bu deger `auto_replenish.narration` ile AYNIDIR (test iki kaynagi
   karsilastirir, sabit yazmaz).
4. **Dayanak guncel:** brief metni "v1.8" gecer, "v1.6" GECMEZ.
5. **Kunye kurali prompt'ta:** uretilen prompt taninirlik kuralini tasir
   (anahtar ifadeler test icinde tanimlanir, brief metninden kopyalanmaz ki
   test metne degil ANLAMA baglansin , en az: "tanin" kokunu iceren kural
   satiri ve "Brooklyn Bridge" ile "Kiska" ornekleri).
6. **v1.8 anlatim kurallari prompt'ta:** "tam cumle" ve "belgesel" kurallari
   gecer.
7. **Bos gecmeyen capa:** brief alani gecici olarak BOSALTILMIS bir cfg kopyasi
   ile ayni prompt kurulur ve yukaridaki ifadelerin HICBIRI gecmez. Bu, 1-6'nin
   bos yere gecmedigini olcer.
8. **Kapsam:** `series/replenish.py` ve `series/produce.py` bu kosuda
   DEGISMEMIS olmali (test degil, Level 10 diff incelemesiyle dogrulanir).
9. **JSON butunlugu:** `series.json` hala gecerli JSON, `topic_pool` girdi
   sayisi degismemis, `next_part`/`parts` bloklari korunmus.

**Calistirma:**

```
python -m pytest tests/test_flashpoints_brief_sozlesmesi.py -q
```

**Regresyon kapisi:**

```
python -m pytest tests/test_doctrine_gate.py tests/test_flashpoints_kanal_sozlesmesi.py -q
```

`test_doctrine_gate.py` flashpoints icin `shot_seconds == "10"`, `shots == 2` ve
`narration (26, 36)` bekliyor , DEGISMEDEN gecmeli. Gecmiyorsa yapisal config'e
dokunulmustur, geri al.

---

## Kapsam disi

- `series/` ve `core/` altindaki hicbir `.py`
- `shadowedhistory/KONSEPT.md` , doktrin dogru, eksik olan brief metniydi;
  doktrine dokunmak `doctrine_sha256` pinini kirar ve ikmali durdurur
- `auto_replenish.title_style` , YouTube BASLIK kaliplarini tutuyor.
  "Fact Or Ancient Propaganda?" kalibi olculdu (4 kullanim, medyan 24, kanal
  medyani da 24) ama n=4 ve icinde 143 izlenmeli Colosseum var; kalip
  kaldirmak icin kanit YETERSIZ. `RF-ISSUES.md`'ye olcum maddesi olarak gider.
- `topic_pool` icerigi
- Kuyruktaki `plans/part31-35.json` , part32 ve part33'un kunyeleri bugun
  ELLE duzeltildi (5d14976); bu kosu onlara dokunmaz
- `calibration.json` , makine uretimi (`series/calibrate.py`), elle duzenlenmez
