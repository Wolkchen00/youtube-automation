# RF-PLAN-REELYZE , uc fazli plan (r2 revizyonu)

Tarih: 10 Eylul 2026 (Los Angeles)
Dal: `codex-reelyze` (worktree)
Kaynak arastirma: `Projeler/Reelyze_Arastirma/REELYZE-DOSYASI.md`
Inceleme kaydi: `RF-SAME-PAGE-LOG-REELYZE.md`

## Core Focus (tek cumle)

Yayinlanan her kisa videonun **medya sozlesmesi** (cozunurluk, fps, sure, ses seviyesi,
tepe seviye, cozulebilirlik) yayin sinirinda deterministik olarak dogrulansin, boylece
bes kanalin hicbiri sessizce sozlesmeye uymayan dosya yayinlamasin.

## Bu plan neyi COZMEZ

**Erisim (reach) sorununu cozmez.** Olculen gercek: AImagine-Fear teknik olarak en kotu
ayarlara sahip kanal ve Instagram'da 371.000 begeni aldi. Teknik duzeltme hit uretmez.
Erisim/format/kanal stratejisi AYRI bir is ve bu planda YOK.

Yaratici olcumler (ilk kare hareketi, kesme temposu, OCR ile ekran yazisi, dongu,
konusma tespiti) bu plandan CIKARILDI. Bunlar kalibrasyon gerektiren vekil olcumlerdir
ve kalibre edilmeden yanlis guven uretirler. `RF-ISSUES-REELYZE.md`'ye tasindi.

---

## r1 incelemesinin degistirdigi iki temel varsayim

### 1. 1080p bu modelde YOK
`core/kie_api.py:489` birebir: *"Seedance duration is an integer 4-15s; resolution 480p/720p."*

Yani AImagine-Fear'in 720p uretmesi bir **yanlis ayar degil, modelin tavani**.
Asil kusur su: `canon/MASTER-BLOCK.md:12` modele *"1080x1920, 30 frames per second"*
diyor ve model bunu **veremez**. Belge gerceklige yalan soyluyor.

Ayrica Kie yuku fps alani ICERMIYOR (`tools/kie_uret.py:135-141`: prompt, duration,
aspect_ratio, resolution, generate_audio). Her cikti 24 fps. **fps hedeflenemez.**

Karar: kanonu ve kapiyi gerceklige hizala. 1080p istiyorsak MODEL DEGISIKLIGI gerekir;
bu maliyeti, gorunumu ve kredi tabanini degistirir, dolayisiyla **Ihsan'in karari** ve
bu planda DEGIL (`RF-ISSUES-REELYZE.md` I-1).

### 2. En yuksek getirili duzeltme planda hic yoktu
`series/produce.py:2148` `if master_lufs is None:` ise mastering ADIMI TAMAMEN ATLANIYOR.
`master_lufs` alani filoda **tek bir seride** tanimli.

| Seri | Kanal | master_lufs | Olculen LUFS | 30g medyan izlenme |
|---|---|---|---|---|
| `unnatural-lab` | sentinal_ihsan | **-14** | **-14,3 / -14,8** | **1.292** |
| `event-horizon` | galactic_experience | YOK | -21,9 / -24,7 | 88,5 |
| `flashpoints` | shadowedhistory | YOK | -20,5 / -25,1 | 27 |
| `next-stop` | aimagine | YOK | -16,1 / -17,1, tepe **+0,7 KIRPIYOR** | 4 |

Uc bagimsiz yontem ayni yeri gosterdi: ffmpeg EBU R128 olcumu, Codex kod incelemesi,
tum `bible.json` taramasi. Duzeltme: uc dosyaya birer satir.

---

# FAZ 1 , Ses (filo geneli, en yuksek getiri, en dusuk risk)

## Rock 1: `master_lufs` uc seriye ekle ve OLCEREK dogrula

**Done looks like:** `event-horizon`, `flashpoints`, `next-stop` bible.json'larinin
`series` blogunda `"master_lufs": -14` var. Bir sonraki uretim ciktisi olculdugunde
integrated loudness -15,0 ile -13,0 arasinda ve true peak <= -1,0 dBTP.

**Neden guvenli:** `unnatural-lab` ayni degerle 2026-08'den beri uretiyor, regresyon
riski yok. `sentinal_ihsan`'a DOKUNULMUYOR.

**Proof:**
```
python -m pytest tests -q -k "master_lufs or bible"
python -c "import json;[print(p, json.load(open(p,encoding='utf-8'))['series'].get('master_lufs')) for p in ['galactic_experience/event-horizon/bible.json','shadowedhistory/flashpoints/bible.json','aimagine/next-stop/bible.json','sentinal_ihsan/unnatural-lab/bible.json']]"
```
uc dosyada da `-14` yazmali. ARTI: bir kuru uretim kosusundan cikan gercek dosyada
`core.ffmpeg_tools.measure_audio_loudness` ile olculen I ve TP kabul araligi icinde.

> Kanit kurali: `bible.json`'da alanin yazmasi kanit DEGILDIR. Kanit, uretilen
> GERCEK dosyanin olculmus degeridir.

## Rock 2: Yayin sinirinda ses sozlesmesi kapisi (fail-closed)

**Sorun:** kapilar ureticilere bagli, yayin sinirina degil. `fear-slide-hazir.yml`
onceden uretilmis mp4'u dogrudan `yayinla.py`'ye veriyor ve denetimi TAMAMEN atliyor.
Elle `yayinla.py` cagrisi da atliyor.

**Done looks like:** `AImagine-Fear/tools/yayinla.py` ve
`series/series_runner.py:_publish_part` yuklemeden HEMEN ONCE ayni ses sozlesmesini
dogrular: integrated loudness hedef +/- 1,5 LU, true peak <= -1,0 dBTP, ses akisi var.
Olculemezse veya disaridaysa **YAYIN DURUR** (fail-closed), sessizce gecmez.

**Proof:** `python -m pytest tests -q -k "yayin_kapisi"` , hedefte olan dosya gecer;
-22 LUFS gecmez; +0,7 dBTP gecmez; sessiz dosya gecmez; olculemeyen dosya gecmez
(bu son vaka fail-closed'i kanitlar).

---

# FAZ 2 , AImagine-Fear'i gerceklige hizala

## Rock 3: Kanon, kod ve kapi ayni seyi soylesin (ATOMIK)

**Sorun:** uc kaynak uc farkli sey soyluyor:
```
canon/MASTER-BLOCK.md:12   "1080x1920, 30 frames per second"   <- MODEL VEREMEZ
tools/gunluk.py:32         COZUNURLUK = "720p"                 <- gercek
tools/gunluk.py:99         kapi 720x1280 bekliyor              <- gercek ama sabit
core/kie_api.py:489        "resolution 480p/720p"              <- tavan
```

**Done looks like:** beklenen medya sozlesmesi TEK yerde tanimli (`AImagine-Fear`
icinde bir sabit sozluk): `{width:720, height:1280, fps:24, duration_s:15}`.
Kanon metni bu degerleri soyler (yalan iddia kaldirilir). Kapi sozlukten okur.
fps de dogrulanir. Uc kaynak birbirine referans verir, kopyalanmaz.

**Neden atomik:** cozunurluk beklentisi ile kapi AYRI commit'lerde giderse yayin durur.
Tek rock, tek commit.

**Proof:** `python -m pytest AImagine-Fear/tests -q -k "sozlesme"` , sozluk degeri
degistirilirse kapi otomatik takip eder (test bunu dogrular); 1080x1920 girdi
mevcut sozlesmeye gore REDDEDILIR (cunku model veremez, gelirse bir sey yanlis demektir);
24 disi fps reddedilir. ARTI: `git grep -n "1080x1920" AImagine-Fear/canon/` bos doner.

## Rock 4: Rota suresini MODEL SOZLESMESINE karsi dogrula

**Sorun:** `tools/gunluk.py:31` `SURE = 15` sabit; rota dosyalari `DURATION: 20` ve
`DURATION: 25` iceriyor (`routes/toronto-cn-red-dusk.md:6`,
`routes/vegas-strat-blue-rain-25.md:6`) ve bu deger hic okunmuyor.

**r1 incelemesinin duzelttigi nokta:** bu degerleri okuyup API'ye gondermek DUZELTME
DEGIL. `core/kie_api.py:489` sureyi 4-15 saniyeyle sinirliyor. 20 gonderirsek
kredi harcanir ve istek reddedilir. Dogru davranis: **harcama yolundan ONCE reddet.**

**Done looks like:** sure `build.load_route()` ile okunur (ikinci ayristirici YAZILMAZ,
`build.py:246` zaten var ve `:333-349` dogruluyor). Model sozlesmesine (4-15 sn) karsi
kontrol edilir. Disardaysa kredi cagrisindan ONCE net hatayla durur. Uyumsuz rotalar
(`toronto` 20 sn, `vegas-...-25` 25 sn) ya kisaltilir ya "bu modelle uyumsuz" diye
isaretlenir. Kapi da ayni okunan degeri kullanir, kendi sabitini degil.

**Proof:** `python -m pytest AImagine-Fear/tests -q -k "rota_sure"` , 15 sn gecer;
20 sn kredi cagrisi YAPILMADAN durur (mock ile cagrilmadigi dogrulanir); DURATION
eksik/bozuk olan rota durur.

## Rock 5: Ses masterlama, DOGRU SIRADA, cuzdan rezervasyonuyla

**r1 incelemesinin duzelttigi nokta:** ilk taslak sesi `denetle()`'den SONRA
masterliyordu, yani yayinlanan dosya hic kapidan gecmemis oluyordu.

**Done looks like:**
```
uret -> master_audio (ayri dosya uret) -> TAM KAPIYI MASTERLENMIS DOSYADA calistir -> yayinla
```
`core.ffmpeg_tools.master_audio` cagrilir (hedef I=-14, TP=-1,0, LRA=11).
`sys.path` bootstrap `tools/yayinla.py`'deki ile BIREBIR ayni sekilde yapilir.
ARTI: `series/balance_floor.py`'nin rezervasyon mekanizmasina katilinir , cuzdan
dort canli kanalla ORTAK (`tools/kie_uret.py:6`) ve bakiye kontrolu rezervasyon degildir.

**Proof:** `python -m pytest AImagine-Fear/tests -q -k "master veya rezerv"` , temiz
surecte `import core.ffmpeg_tools` calisir; masterlenmis dosya `measure_audio_loudness`
ile -15,0..-13,0 ve TP <= -1,0 olcer; yayinlanan dosya yolunun masterlenmis dosya
oldugu dogrulanir (hash karsilastirmasi); es zamanli iki kosu ayni krediyi rezerve edemez.

---

# FAZ 3 , Ortak deterministik medya sozlesmesi

## Rock 6: `core/medya_sozlesmesi.py`

**Kapsam bilerek DAR.** Sadece deterministik, makinece kesin olculebilen seyler:

| Olcum | Yontem | Bilinmezlik |
|---|---|---|
| Cozulebilirlik | tam decode, sifir olmayan cikis kodu = RED | yok |
| Akislar | `-select_streams v:0` / `a:0`, acikca | yok |
| Geometri | genislik x yukseklik | yok |
| fps | rasyonel ayristirma (`30000/1001` dogru okunur) | yok |
| Sure | format suresi | yok |
| Integrated loudness | EBU R128 | ses yoksa "olculemedi" |
| True peak | EBU R128 peak=true | ses yoksa "olculemedi" |

**Done looks like:** `dogrula(video, sozlesme) -> {"gecti": bool, "olcumler": {...},
"ihlaller": [...], "bilinmeyen": [...], "sozlesme_surumu": "1"}`
Tek bir tamsayi puan DONDURMEZ (r1: farkli makinelerde kiyaslanamaz ve eksik kaniti gizler).
Olculemeyen sey "bilinmeyen" olarak isaretlenir, asla varsayilmaz.
Dosya boyutu vekili YOK (3 MB esigi kaldirilir: bozuk buyuk dosya gecer, verimli
kucuk dosya reddedilir).

**Proof:** `python -m pytest tests/test_medya_sozlesmesi.py -q` (bu dosya bu rock'in
teslimatidir, mevcut degil). Vakalar: gecerli dosya gecer; bozuk dosya decode'da kalir;
sessiz dosya "bilinmeyen" doner ve GECMEZ; `30000/1001` fps dogru okunur;
ses akisi olmayan dosya loudness'i "bilinmeyen" doner.

## Rock 7: Sozlesmeyi YAYIN SINIRINA bagla

**Done looks like:** `AImagine-Fear/tools/yayinla.py` ve
`series/series_runner.py:_publish_part` (satir 308) yuklemeden hemen once
`medya_sozlesmesi.dogrula()` cagirir. Deterministik ihlal = YAYIN DURUR.
Sonuc, yayinlanan dosyanin **sha256'siyla baglanmis surumlu bir kayit semasi** olarak
`yayin.jsonl` ve seri metadata'sina yazilir.

**Neden ureticilere degil sinira:** `fear-slide-hazir.yml`, elle `yayinla.py`,
onbelleklenmis seri ciktilari ve gelecekteki cagiricilar uretici kapisini atlar.
Sinir tek gecistir.

**Proof:** `python -m pytest tests -q -k "sinir_kapisi"` , dogrudan `yayinla.py`
cagrisi (uretici atlanarak) sozlesmesiz dosyayi YUKLEMEZ; `_publish_part` ayni sekilde;
yayin kaydinda dosya hash'i ve sozlesme surumu bulunur.

---

## Sira ve bagimliliklar

```
Rock 1 (bagimsiz, hemen)  ->  Rock 2 (Rock 1'in sonucunu korur)
Rock 3 (atomik, tek commit)
Rock 4 (bagimsiz)
Rock 5 (Rock 3'ten sonra: kapi dogru degerleri bilmeli)
Rock 6  ->  Rock 7
```

## Dokunulmayacaklar

- `sentinal_ihsan/unnatural-lab` , filoda dogru calisan tek seri, referans.
- `canon/NEGATIVES.md:15` ekran yazisi yasagi , kasitli estetik karar,
  371.000 begeni metinsiz geldi. Degistirilecekse Ihsan'in karari.
- `MIN_KREDI = 700` , 615 kredilik 720p/15sn kosusuna dayali. Model degismedigi
  surece gecerli. Model degisirse yeniden turetilmeli (`RF-ISSUES-REELYZE.md` I-1).
- `yayin.jsonl` gecmis kayitlari.
- Ortak motorun dort kanali besleyen calisan akisi (Rock 1, 2, 7 disinda).
