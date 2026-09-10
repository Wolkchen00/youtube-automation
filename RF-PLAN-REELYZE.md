# RF-PLAN-REELYZE , plan (r3 revizyonu)

Tarih: 10 Eylul 2026 (Los Angeles) | Dal: `codex-reelyze`
Inceleme kaydi: `RF-SAME-PAGE-LOG-REELYZE.md` | Ertelenenler: `RF-ISSUES-REELYZE.md`

## Core Focus

Yayinlanan her kisa videonun **medya sozlesmesi** (cozunurluk, fps, sure, ses seviyesi,
tepe seviye, cozulebilirlik) **yayin sinirinda**, yuklenen HER dosya icin, deterministik
olarak dogrulansin ve ihlalde yayin dursun.

## Kapsam disi
Erisim/format/kanal stratejisi. Yaratici vekil olcumler. Cuzdan yonetisimi.
Hepsi `RF-ISSUES-REELYZE.md`'de gerekcesiyle.

---

## r2 incelemesinin degistirdigi uc varsayim

### 1. Model sozlesmesi BILINMIYOR (r2 beni duzeltti)
r2'de "1080p imkansiz" demistim. Yanlisti:
```
core/kie_api.py:483   model: str = "bytedance/seedance-2-fast"   <- FAST varyanti belgeleniyor
core/kie_api.py:489   "duration 4-15s; resolution 480p/720p"     <- FAST icin
AImagine-Fear/tools/gunluk.py:30   MODEL = "bytedance/seedance-2" <- FAST DEGIL
```
`seedance-2` (fast olmayan) sinirlari depoda **hicbir yerde belgelenmemis**.
Ters ipucu: `sentinal_ihsan/KONSEPT_v3_TASLAK.md:365` bir Seedance varyantinda
"720p 20 sn ~1.260 kredi" diyor.
**Karar: olcmeden kanona dokunma.** Rock 2 bunu bir kanaryayla cozer.

### 2. `master_lufs` uc davranisi birden ceviriyor
```
produce.py:604   amix_normalize = master_lufs is None      -> KAPANIR
produce.py:656   music_volume = 0.50 if ... else 0.28       -> neredeyse IKI KAT
produce.py:659   limit_mix_peak = master_lufs is not None   -> ACILIR
```
Kalibrasyon `unnatural-lab`in ses profiline gore yapilmis (dogal ses agirlikli).
`event-horizon` (126-156 WPM) ve `flashpoints` (70-119 WPM) yogun TTS anlatimi.
**Muzik 0,50'ye cikinca anlatimi bogabilir.** LUFS/TP olcmek yetmez, denge de olculmeli.

### 3. Cuzdan zaten serilestirilmis
`.github/workflows/{calibrate,event-horizon,fear-slide,...}.yml` hepsinde
`concurrency: group: kie-uretim`. Rezervasyon eklemek gereksiz karmasa.
Rock olarak KILL, `RF-ISSUES-REELYZE.md` I-7.

---

# FAZ 1 , Ses

## Rock 1: `master_lufs` uc seriye, seri basina kanitla

**Kapsam:** `event-horizon`, `flashpoints`, `next-stop` bible.json `series` blogu.
`sentinal_ihsan/unnatural-lab` DEGISMEZ (referans).

**Done looks like:**
1. Alan eklendi.
2. Her seri icin AYRI, **yayinlanmayan** bir gercek uretim ciktisi uretildi ve saklandi
   (uc seri uc farkli ses yolundan gecer: anlatim+muzik, anlatim+dogal ses, saf gorsel).
3. Her cikti icin olculdu: integrated loudness -15,0..-13,0; true peak <= -1,0 dBTP.
4. **Denge kontrolu:** ayni cikti icin anlatim-only ve muzik-only stem seviyeleri
   karsilastirildi; muzik anlatimin uzerine cikmiyor. (`music_volume` 0,28 -> 0,50
   degisimi bu adimda yakalanir.)
5. `tests/test_rocka_audio_master.py:117` `test_only_unnatural_lab_has_master_lufs`
   **silinmez**, yeni dogru yapilandirmayi (dort seri) dogrulayacak sekilde guncellenir;
   alansiz seri davranisinin kapsami ayri bir testte korunur.

**Proof:**
```
python -m pytest tests/test_rocka_audio_master.py tests/test_master_true_peak.py -q
```
(sifir toplama = BASARISIZ sayilir) ARTI her uc cikti icin
`core.ffmpeg_tools.measure_audio_loudness` degerleri kabul araliginda,
ARTI denge karsilastirmasi kayitli.

> `--dry` KULLANILMAZ: `gunluk.py --dry` uretimden ONCE cikar, dosya uretmez.
> Kanit gercek dosyadir, yapilandirma satiri degil.

---

# FAZ 2 , AImagine-Fear

## Rock 2: Model sozlesmesini OLC, sonra kanonu hizala

**Sorun:** kanon (`MASTER-BLOCK.md:12`) "1080x1920, 30 fps" diyor; kod 720p gonderiyor;
kapi 720x1280 sabit bekliyor; modelin gercek tavani bilinmiyor.

**Done looks like:**
1. **Kanarya:** tek rota, `--resolution 1080p`, tek uretim. Sonuc uc halden biri:
   kabul+1080x1920 / red / kabul ama 720p (sessiz dusurme).
2. Kredi farki olculur (su anki taban: 615 kredi = $3,08).
3. **Ihsan karar verir** (kredi harcanacak, cuzdan dort kanalla ortak).
4. Karardan SONRA: medya sozlesmesi tek bir Python nesnesinde tanimlanir.
   `build.py` bu nesneden `MASTER-BLOCK.md`'ye **placeholder** doldurur
   (`<<WIDTH>>`, `<<HEIGHT>>`, `<<FPS>>`, `<<DURATION>>` gibi). Metin kopyalanmaz.
5. Kapi ayni nesneden okur. fps de dogrulanir.

**Proof:** `python -m pytest AImagine-Fear/tests/test_sozlesme.py -q` (yeni dosya,
bu rock'in teslimati). Vakalar: sozlesme nesnesi degistirilince **render edilmis
`PROMPT.txt`** degisir (bos grep sonucu kanit SAYILMAZ); kapi ayni nesneden okur;
sozlesme disi geometri/fps reddedilir.

## Rock 3: Sure , tek sozlesme nesnesi, uyumsuz rota karantinasi

**Sorun:** `gunluk.py:31` `SURE = 15` sabit; rotalarda `DURATION: 20` ve `25` var,
okunmuyor. r2 duzeltmesi: `build.load_route()` varligi dogruluyor ama sayisal/sonlu
dogrulamayi `_parse_duration()` yapiyor; ikisini karistirmayin.

**Done looks like:**
1. Tek **public** dogrulanmis-sure yardimcisi acilir (mevcut `_parse_duration()`
   uzerinden), ikinci ayristirici YAZILMAZ.
2. Sure, Rock 2'nin sozlesme nesnesine girer; **ayni nesne** hem uretime hem yayin
   dogrulamasina gider. (r2: Rock 3'te sabit 15, Rock 4'te dinamik demek iki rakip
   kaynak yaratiyordu. Tek nesne.)
3. Model sozlesmesi disindaki rotalar (`toronto` 20 sn, `vegas-...-25` 25 sn)
   **kalici olarak karantinaya alinir ve `sirdaki()` tarafindan ATLANIR.**
   Sadece "uyumsuz" isaretlemek yetmez: yayinlanmadigi icin en eski kalir ve
   sonsuza kadar tekrar secilir.
4. Harcama yolundan ONCE reddedilir.

**Proof:** `AImagine-Fear/tests/test_rota_sure.py` (yeni). Vakalar: uyumlu rota gecer;
uyumsuz rota **Kie cagrisi yapilmadan** durur (mock ile cagrilmadigi dogrulanir);
karantinaya alinan rota `sirdaki()` tarafindan bir daha secilmez (rotasyon ilerler);
`DURATION` eksik/bozuk rota durur.

## Rock 4: Ses masterlama, dogru sirada

**Done looks like:**
```
uret -> master_audio (AYRI dosya) -> TAM sozlesme kapisi MASTERLENMIS dosyada -> yayinla
```
`sys.path` bootstrap `tools/yayinla.py` ile birebir ayni. Yayinlanan dosyanin
masterlenmis dosya oldugu **sha256 ile** dogrulanir.

**Proof:** `AImagine-Fear/tests/test_master_sira.py` (yeni). Temiz surecte
`import core.ffmpeg_tools` calisir; masterlenmis dosya -15,0..-13,0 ve TP <= -1,0;
yayinlanan yolun hash'i masterlenmis dosyanin hash'i.

---

# FAZ 3 , Ortak sozlesme kapisi (Rock 2 r2'de buraya birlestirildi)

## Rock 5: `core/medya_sozlesmesi.py`

Sadece deterministik olcumler. Vekil YOK.

| Olcum | Yontem |
|---|---|
| Cozulebilirlik | tam decode, **`-xerror`**, sifir olmayan cikis = RED |
| Akislar | `-select_streams v:0` / `a:0`, acikca |
| Geometri | genislik x yukseklik |
| fps | rasyonel ayristirma **+ CFR kaniti** (ortalama hiz/zaman damgalari; nominal `r_frame_rate` VFR'yi gizleyebilir) |
| Sure | format suresi, tolerans sozlesmede |
| Integrated loudness / true peak | EBU R128 |

**Done looks like:** `dogrula(video, sozlesme) -> {gecti, olcumler, ihlaller,
bilinmeyen, sozlesme_surumu}`. Tamsayi puan YOK. Dosya boyutu vekili YOK.
Olculemeyen "bilinmeyen"dir ve **fail-closed** sayilir.

**Proof:** `tests/test_medya_sozlesmesi.py` (yeni teslimat). Vakalar: gecerli dosya;
**kismen bozulmus fixture** `-xerror` ile kalir; sessiz dosya "bilinmeyen" doner ve GECMEZ;
`30000/1001` dogru okunur; VFR dosya CFR kanitini gecemez.

## Rock 6: Sozlesmeyi yayin sinirina bagla, HER dosya icin

**Done looks like:**
1. `AImagine-Fear/tools/yayinla.py` ve `series/series_runner.py` `_publish_part()`
   sozlesmeyi **acikca parametre olarak alir**; yoksa **fail-closed** durur
   (r2: kapilar neyi zorlayacagini bilmiyordu).
2. `_publish_part()` platforma gore FARKLI dosya gonderebiliyor (YouTube'a 4K,
   IG/TikTok'a `delivery_1080.mp4`). Dogrulama **`_try()` icinde, platform kaynagi
   secildikten SONRA** yapilir; her ayri dosya icin ayri sha256 ve ayri kanit.
3. Kanit **ilk yuklemeden ONCE** kalici yazilir. (Seri yayin kutugu yazma hatalarini
   bastiriyor; kanit sessizce kaybolabilir.)
4. `.github/workflows/fear-slide-hazir.yml` **ffmpeg kurar** (su an sadece
   `actions/setup-python@v5` var; ffprobe olmadan kapi calisamaz).
5. Yeni test dosyalari CI kapsamina eklenir (su an sadece `AImagine-Fear/tests` kosuyor).

**Proof:** `tests/test_yayin_siniri.py` (yeni). Vakalar: uretici atlanarak dogrudan
`yayinla.py` cagrisi sozlesmesiz dosyayi YUKLEMEZ; sozlesme parametresi yoksa durur;
`_publish_part` iki farkli platform dosyasi icin iki ayri kanit yazar;
kutuk yazma hatasi yaymayi ENGELLER; `fear-slide-hazir.yml` ffprobe bulur.

---

## Sira

```
Rock 1 (bagimsiz, hemen baslayabilir)
Rock 2 (KANARYA -> Ihsan karari -> sonra kod)  ->  Rock 3, Rock 4
Rock 5  ->  Rock 6
```

## Dokunulmayacaklar
- `sentinal_ihsan/unnatural-lab` , dogru calisan tek seri, referans.
- `canon/NEGATIVES.md:15` ekran yazisi yasagi , 371.000 begeni metinsiz geldi.
- `MIN_KREDI = 700` , model degismedikce gecerli; degisirse yeniden turetilmeli.
- `yayin.jsonl` gecmisi.
- `concurrency: group: kie-uretim` , cuzdani zaten serilestiriyor, dokunma.
