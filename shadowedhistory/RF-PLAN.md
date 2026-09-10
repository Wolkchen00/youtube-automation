# RF-PLAN , shadowedhistory / flashpoints kanal duzeltmesi

Tarih: 10 Eylul 2026 (Los Angeles)
Dal: `codex-shadow-kanal` (worktree; ana agacta bes baska oturum calisiyor)
Kaynak: `shadowedhistory/REELYZE-RAPOR.md` + bu kosuda yapilan olcum

## Core Focus (tek cumle)

flashpoints'in yayinladigi her bolum, kanalin kendi olculmus en iyi bicimine uysun:
15 saniye, iki cekim, duyulabilir ses, ekranda okunur bilgi , ve yarim bolum asla
yayinlanmasin.

## Bu plan neyi COZMEZ

Erisim sorununu cozmez. Kanalin iki hitini (1.179 ve 509 izlenme) ne ses ne sure
acikladi; ikisi de konu tanınırligiyla one cikti ve bu hipotez 29 bolumluk veride
zayif ciktı (asagida). Bu plan "urettigimiz sey niyetimize uysun" sorununu cozer.
Konu secimi ayri bir is olarak `RF-ISSUES.md`'ye tasindi.

---

## Olculen durum (bu kosuda dogrulandi, hepsi dosya:satir veya canli olcum)

### Kanit 1: mastering hic calismiyor

```
series/produce.py:2147   master_lufs = bible.master_lufs
series/produce.py:2148   if master_lufs is None:  ->  master_audio() HIC CAGRILMIYOR
```

`shadowedhistory/flashpoints/bible.json` `series` blogunda `master_lufs` alani YOK.
Filoda alani tanimli tek seri `sentinal_ihsan/unnatural-lab/bible.json:11` (`-14`) ve
olculen ciktisi -14,3 LUFS. flashpoints olculen: -20,5 ile -25,1 LUFS. Hedef -16..-13.

### Kanit 2: 29 bolumun 9'u YARIM yayinlandi

```
series/produce.py:126-130  _required_shot_count():
    bible.min_shots None ve require_all_shots False  ->  return 1
```

`flashpoints/bible.json` `qc` blogunda `min_shots` yok, `require_all_shots` yok.
Yani iki cekimlik bir plan TEK cekimle yayina cikabiliyor. Olculen sonuc:

`qc_log.jsonl` -> `final_reject` olayi 8 bolumde (4, 9, 22, 23, 24, 26, 27, 30).
Yayinlanan sure dagilimina gore toplam 9 bolum tek cekimle cikmis (part 6 QC disi
bir yoldan cekim kaybetmis).

Cekim dustugunde `produce.py:570-583` anlatimi otomatik kisaltiyor
(`shorten_narration_for_duration`). Plandaki 33-42 kelimelik anlatim ~12 kelimeye
iniyor. Yani bolum yayinlaniyor ama **anlattigi bilgiyi bitirmiyor.**

### Kanit 3: 15 saniye kanalin en iyi teslim suresi

29 yayinlanmis bolumun tamami yt-dlp ile cekildi (izlenme + sure, 10 Eylul):

| Teslim suresi | Bolum sayisi | Medyan izlenme | En yuksek |
|---|---|---|---|
| **15 sn (iki cekim x 8 sn)** | **17** | **33** | 795 |
| 9-10 sn (tek cekim, 20 sn plandan) | 5 | 23 | 509 |
| 7 sn (tek cekim, 16 sn plandan) | 4 | 19,5 | 1.179 |
| 19 sn (iki cekim x 10 sn) | 3 | **19** | 22 |

`series.json` `auto_replenish.shot_seconds` 22. bolumden sonra `"8"` -> `"10"` olmus.
Plan suresi 16 sn -> 20 sn. O tarihten beri **tek bolum bile 100 izlenmeyi gecmedi**
(hitler haric, ki ikisi de tek cekimli kazalar). 19 saniyelik uc bolum: 22, 19, 5.

Rapor "12-18 saniyeye cek" diyordu. Kanalin verisi tam olarak 15 saniyeyi isaret ediyor
ve bu deger kanalda zaten 17 kez calismis. Bu bir deney degil, geri alma.

### Kanit 4: fact_captions kapali, kardes serilerde acik

35 planin **hicbirinde** bir cekimde bile `fact` alani yok. `flashpoints/bible.json`
`fact_captions` icermiyor; `series.json` `auto_replenish.fact_captions` bayragi yok.

Ayni kanalin diger iki serisi acik:
`shadowedhistory/drowned-history/bible.json` -> `{"enabled": true, "hold": 2.6}`
`shadowedhistory/footnotes/bible.json` -> `{"enabled": true, "hold": 2.8}`

Motorun kendi belgesi (`series/bible.py:366-372`): *"Faceless tarih Shorts'larinda
izlenme/paylasimi en cok artiran kaldirac."* Aktif yayinlanan seri bunu kullanmiyor.

### Kanit 5 (rapordaki iddia CURUDU): kunye zaten her planda var

Rapor "baslik kartinin her videoda basildigini dogrula" diyordu. 35 planin **35'inde**
de `title_card.title` dolu, `bible.json` `title_card: true`
(`series/bible.py:360-363` bool degeri `{"enabled": True}`'ya ceviriyor).
Yapilacak is yok. Bu madde plandan dusuruldu.

---

## Rock 1: Ses , mastering'i devreye al

**Sorun:** `bible.json` `series` blogunda `master_lufs` yok, mastering atlaniyor.

**Yapilacak:** `shadowedhistory/flashpoints/bible.json` -> `series` blogunun icine
`"master_lufs": -14`. Referans bicim: `sentinal_ihsan/unnatural-lab/bible.json:11`.

**Done looks like:** `Bible(...).master_lufs == -14.0`, `produce.py:2148` dali artik
`master_audio()` cagiran kola giriyor.

**DOKUNMA:** `core/ffmpeg_tools.py`, `series/produce.py`, `series/bible.py`. Motor
dogru; eksik olan yalniz kanal konfigurasyonu. Baska kanalin bible dosyasina dokunma.

## Rock 2: Yarim bolum yayinlanmasin

**Sorun:** `min_shots` tanimsiz, esik 1'e dusuyor, iki cekimlik plan tek cekimle cikiyor.

**Yapilacak:** `bible.json` -> `qc` blogunun icine `"min_shots": 2`.

**Done looks like:** `_required_shot_count(bible, 2) == 2`. Bir cekim final_reject
alirsa bolum yayinlanmaz (kredi zaten harcanmis olur, ama yarim bolum kanala girmez).
`validate_min_shots` hata vermez (deger plan cekim sayisini asmaz).

**Bilinen bedel , acikca kabul ediliyor:** bu kural gecmiste uygulansaydi kanalin iki
hiti (part 22 = 1.179, part 26 = 509) yayinlanmazdi. Yine de dogru karar: tek cekimli
kova medyani 23, iki cekimli 15 sn kovasi medyani 33. Iki hit, tek cekimin ustunlugunu
gostermiyor; 9 bolumluk kovada geri kalan 7'si 2-64 arasi. Bedeli plana yaziyoruz ki
sonradan surpriz olmasin.

## Rock 3: Sureyi 15 saniyeye geri al

**Sorun:** `auto_replenish.shot_seconds` `"10"`; teslim 19 sn; o kovanin medyani 19.

**Yapilacak:**
1. `shadowedhistory/flashpoints/series.json` -> `auto_replenish.shot_seconds`: `"8"`
2. Uretilmemis kuyruk planlari `plans/part31.json` .. `plans/part35.json` icindeki her
   cekimin `duration` alani `"10"` -> `"8"` (`series.json.next_part` = 31, yani 31-35
   henuz uretilmedi; 1-30 gecmistir, dokunma)

**Done looks like:** `series.json` `shot_seconds == "8"`; part31-35 plan toplam suresi
16 sn; part01-30 dosyalari degismemis.

**DOKUNMA:** `series/replenish.py`. Sabit kodlu bir sure yok, deger konfigurasyondan
okunuyor (`replenish.py` `cfg` uzerinden).

## Rock 4: fact_captions'i ac

**Sorun:** kanalin en guclu ekran-ici kaldiraci kapali; kardes iki seride acik.

**Yapilacak:**
1. `bible.json` -> `series` blogunun icine `"fact_captions": {"enabled": true, "hold": 2.6}`
2. `series.json` -> `auto_replenish` icine `"fact_captions": true` (yeni uretilen
   planlar `fact` alani tasisin; `replenish.py:1288` en az iki cekimde zorunlu kilar)

**Done looks like:** `Bible(...).fact_captions == {"enabled": True, "hold": 2.6}`.
Kuyruktaki 31-35 planlari `fact` tasimadigi icin onlarda hicbir sey cizilmez
(`produce.py` yorumu: *"shot['fact'] yoksa hicbir sey cizilmez"*) , yani bu degisiklik
kuyrugu bozmaz, 36. bolumden itibaren devreye girer.

**DOKUNMA:** `plans/part01.json` .. `plans/part35.json` icine elle `fact` yazma.
Kuyruk planlari uretim bicimini degistirmeden gecmeli.

---

## PROOF (tek komut, hepsini kapsar)

Yeni dosya: `tests/test_flashpoints_kanal_sozlesmesi.py`

Bu dosya bir konfigurasyon sozlesme testidir. Gerekcesi: bu depoda CI durum
dosyalarini geri yaziyor (`chore: flashpoints durumunu ilerlet [skip ci]`), yani
`bible.json` ve `series.json` otomatik islemlerin dokundugu dosyalar. Testsiz bir
konfigurasyon duzeltmesi sessizce geri alinabilir.

Test sunlari dogrulamali (motoru mocklamadan, gercek dosyalari okuyarak):

1. `Bible` flashpoints bible'ini yukler ve `master_lufs == -14.0` doner
2. `series.produce._required_shot_count(bible, 2) == 2`
3. `series.preflight.validate_min_shots(bible, plan)` part31 plani icin bos liste doner
4. `Bible(...).fact_captions == {"enabled": True, "hold": 2.6}`
5. `series.json` `auto_replenish.shot_seconds == "8"` ve `fact_captions is True`
6. `plans/part31.json` .. `part35.json`: her cekimin `duration` degeri `"8"`,
   plan basina cekim sayisi 2, toplam 16 sn
7. `plans/part01.json` .. `part30.json` dosyalarinda cekim sureleri DEGISMEMIS
   (1-22 icin `"8"`, 23-30 icin `"10"` , gecmis kayittir, duzeltilmez)
8. Regresyon capasi: `sentinal_ihsan/unnatural-lab/bible.json` `master_lufs` hala -14
   (bu kosu baska kanala dokunmadi)

**Calistirma:**

```
python -m pytest tests/test_flashpoints_kanal_sozlesmesi.py -q
```

**Regresyon kapisi (mevcut takim bozulmadi):**

```
python -m pytest tests/test_min_shots.py tests/test_rocka_audio_master.py tests/test_master_true_peak.py -q
```

Iki komut da yesil olmadan rock kapanmaz.

---

## Kapsam disi (bu kosuda ASLA dokunulmayacak)

- `core/` ve `series/` altindaki hicbir `.py` , motor dogru, dort kanali birden besliyor
  ve su anda bes ayri oturum ayni depoda calisiyor
- `sentinal_ihsan/`, `galactic_experience/`, `aimagine/`, `AImagine-Fear/` , baska
  oturumlarin sahasi
- `shadowedhistory/drowned-history/`, `footnotes/`, `secrets-anatolia/` , footnotes
  duraklatilmis, oyle kalsin
- `published.json`, `qc_log.jsonl`, `series_log.csv`, `calibration.json` , calisma
  zamani durumu, elle duzenlenmez
- Cozunurluk (1080x1920) ve fps (30) , dogru
- Konu havuzu icerigi , `RF-ISSUES.md`
