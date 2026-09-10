# RF-PLAN-REELYZE , plan (r4 revizyonu)

Tarih: 10 Eylul 2026 (Los Angeles) | Dal: `codex-reelyze`
Kayit: `RF-SAME-PAGE-LOG-REELYZE.md` | Ertelenenler: `RF-ISSUES-REELYZE.md`

## Core Focus

Yayin sinirinda, yuklenen HER dosya icin, medya sozlesmesi deterministik olarak
dogrulansin ve ihlalde yayin dursun.

## r3'un kapsam karari (kabul edildi)

Codex: *"Make Rock 6 the primary delivery with Rock 5 as its implementation dependency,
retain necessary active-channel audio remediation, and defer the 1080p experiment and
paused Next Stop rollout."*

**Alti rock -> dort rock.** Cikarilanlar ve gerekceleri `RF-ISSUES-REELYZE.md`'de.

### Cikarilanlar
- **1080p kanaryasi** (I-1) , kapiyi teslim etmek icin gerekli degil. Sozlesme
  OLCULEN gercegi kaydeder (720x1280, 24 fps), bir hedefi degil. Bu, r3'un
  "Ihsan reddederse plan tamamlanamaz" CLARIFY'ini de cozer: **karar beklemiyoruz.**
- **Rota suresi / karantina** (I-8) , modelin gercek sure sozlesmesi bilinmiyor.
  Tek bir 1080p kanaryasi sure sinirlarini KANITLAMAZ. Sozlesme bilinmeden
  "20 saniye uyumsuz" demek saglayici sinirini uydurmak olur.
- **next-stop** (I-9) , `aimagine/next-stop/series.json` -> `status: paused`.
  Duraklatilmis seri uretim yapamaz, dolayisiyla dogrulama ciktisi da veremez.

---

# FAZ 1 , Aktif kanallarin sesi

## Rock 1: `master_lufs`, iki AKTIF anlatimli seriye

**Kapsam:** `galactic_experience/event-horizon` ve `shadowedhistory/flashpoints`.
Ikisi de `status: active`. `unnatural-lab` DEGISMEZ (referans, zaten -14).
`next-stop` KAPSAM DISI (paused).

**r3 duzeltmesi , ses yollari:** ikisi de anlatim + muzik kullaniyor, dogal ses
varsayilan olarak kisik. Yani "uc farkli ses yolu" varsayimim yanlisti; iki seri de
AYNI yoldan gecer. Kontrol buna gore tanimlanir; olmayan stem "uygulanamaz" isaretlenir.

**Done looks like:**
1. Alan eklendi (`series` blogu, `"master_lufs": -14`).
2. **Izole render kosumu:** sabit bolum girdileriyle, canli seri durumuna ve yayin
   kaydina DOKUNMADAN. (`run_next(..., publish=False)` KULLANILMAZ: fonksiyonun
   kendi dokumantasyonu "uret + yayinla + durumu ilerlet" diyor, yani bolumu ilerletir.)
3. Her seri icin taban (alansiz) ve aday (alanli) cikti AYNI girdilerden uretildi.
4. Karsilastirma **islenmis** dosyalar uzerinde, hizalanmis araliklarda:
   - `{stem}_narrated.mp4` (produce.py:592) ve `{stem}_music.mp4` (produce.py:651)
   - taban ile aday arasindaki denge degisimi kayitli
   - kabul araligi: anlatim aralik(lar)inda muzigin taban-goreli artisi belirtilen
     esigi asmiyor. Ham `narration.wav` / `bg_music.mp3` seviyeleri KANIT SAYILMAZ
     (zamanlama, mix, limit ve mastering sonrasi katkiyi temsil etmezler).
5. Final: integrated loudness -15,0..-13,0; true peak <= -1,0 dBTP.
6. **Kayitli dinleme degerlendirmesi:** anlatim anlasilirligi bozulmamis.
   (Kisa muzik tepeleri "muzik anlatimi asmiyor" testini gecip yine de kelimeleri
   maskeleyebilir; sayisal esik tek basina yetmez.)
7. `tests/test_rocka_audio_master.py:117` `test_only_unnatural_lab_has_master_lufs`
   SILINMEZ, uc aktif seriyi dogrulayacak sekilde guncellenir; alansiz seri
   davranisinin kapsami ayri testte korunur.

**Proof:** `python -m pytest tests/test_rocka_audio_master.py tests/test_master_true_peak.py -q`
**ARTI** iki seri icin saklanmis taban/aday kanit dosyalari.
**Atlanan zorunlu medya testi = EKSIK sayilir**, gecmis sayilmaz (mevcut takimlar
ffmpeg veya fixture yoksa atliyor; sifir olmayan toplama tek basina yetersiz).
**ARTI** canli seri durumu ve yayin kaydi degismemis (assert edilir).

## Rock 2: AImagine-Fear ses masterlama, dogru sirada

**Done looks like:**
```
uret -> master_audio (AYRI dosya) -> TAM sozlesme kapisi MASTERLENMIS dosyada -> yayinla
```
`core.ffmpeg_tools.master_audio`, hedef I=-14, TP=-1,0, LRA=11.
`sys.path` bootstrap `tools/yayinla.py` ile birebir ayni.
Yayinlanan dosyanin masterlenmis dosya oldugu **sha256** ile dogrulanir.

Olculen mevcut durum: -15,4 / -16,5 / -16,1 / -15,5 LUFS (hedefin altinda).
Cozunurluk/fps DEGISMIYOR (720x1280, 24 fps olculen gercek, sozlesmeye oyle yazilir).

**Proof:** `AImagine-Fear/tests/test_master_sira.py` (yeni, bu rock'in teslimati).
Temiz surecte `import core.ffmpeg_tools` calisir; masterlenmis dosya -15,0..-13,0
ve TP <= -1,0; yayinlanan yolun hash'i masterlenmis dosyanin hash'i.

---

# FAZ 2 , Sinir kapisi (ASIL TESLIMAT)

## Rock 3: `core/medya_sozlesmesi.py` (Rock 4'un bagimliligi)

Sadece deterministik olcumler. Vekil YOK. Tamsayi puan YOK. Boyut vekili YOK.

| Olcum | Yontem |
|---|---|
| Cozulebilirlik | tam decode, **`-xerror`**, sifir olmayan cikis = RED |
| Akislar | `-select_streams v:0` / `a:0`, acikca |
| Geometri | genislik x yukseklik, **teslimat profiline gore** |
| fps | rasyonel ayristirma **+ CFR kaniti** (ortalama hiz/zaman damgasi) |
| Sure | tolerans sozlesmede |
| Integrated loudness / true peak | EBU R128 |

**Teslimat profilleri (r3):** tek geometri sozlesmesi hem 4K master'i hem 1080p
teslimat kopyasini dogrulayamaz. Sozlesme profil bazlidir; profil `_try()` icinde
`src` ile BIRLIKTE secilir.

**Cikti:** `dogrula(video, sozlesme) -> {gecti, olcumler, ihlaller, bilinmeyen, sozlesme_surumu}`
Olculemeyen "bilinmeyen"dir ve **fail-closed** sayilir.

**Proof:** `tests/test_medya_sozlesmesi.py` (yeni teslimat). Vakalar: gecerli dosya gecer;
**kismen bozulmus fixture** `-xerror` ile kalir; sessiz dosya "bilinmeyen" doner ve GECMEZ;
`30000/1001` dogru okunur; VFR dosya CFR kanitini gecemez; 4K profil ile 1080p profil
ayni dosyaya farkli karar verir.

## Rock 4: Sinira bagla, HER yuklenen dosya icin

**Dikis yeri dogrulandi:** `series/series_runner.py:329` `def _try(plat)`.

**Done looks like:**
1. Sozlesme `_try()` icine, **`src` secildikten SONRA**, profiliyle birlikte gecer.
   Sozlesme yoksa **fail-closed** durur.
2. **Tum cagiricilar atomik gucer:** `run_next()`, `approver._publish_approved()`,
   Fear'in altsurec argumanlari, ve hazir-video workflow'u. Sozlesme onay/indirme
   yollarinda da tasinir. Zorunlu kilinmadan ONCE hepsi gucmus olur.
3. **Dogrulama reddi, siradan yukleme hatasindan AYRI temsil edilir.** Aksi halde
   deterministik red mevcut 90 saniyelik yeniden deneme yoluna duser ve sonsuza
   kadar tekrar denenir. Red yeniden denenmez, tanisi saklanir.
4. Kanit **ilk yuklemeden ONCE** kalici yazilir, her ayri dosya icin ayri sha256.
5. Kanit `yayin.jsonl`e YAZILMAZ. Mevcut okuyucular oradaki satirlari yayin gecmisi
   sayiyor; reddedilen deneme rotasyonu ve ayni-gun kilidini tuketmemeli.
   Ayri kayit, ayri dosya.
6. `.github/workflows/fear-slide-hazir.yml` **ffmpeg kurar** (su an sadece
   `actions/setup-python@v5`; ffprobe olmadan kapi calisamaz).
7. Yeni test dosyalari CI kapsamina eklenir.

**Aktivasyon bagimliligi:** Rock 4'un ses zorlamasi, Rock 1 ve Rock 2 uyumlu cikti
uretene KADAR acilmaz. Once uretici-den-sinira tam yol test edilir, sonra zorlama acilir.

**Proof:** `tests/test_yayin_siniri.py` (yeni). Vakalar:
- **POZITIF:** her cagirici uzerinden gecerli dosya BASARIYLA yuklenir
  (r3: aksi halde her yuklemeyi engelleyen bir uygulama da testi gecerdi)
- gecerli sozlesme + bozuk dosya: secilen kotu dosya yukleyiciye HIC ulasmaz
- uretici atlanarak dogrudan `yayinla.py`: sozlesmesiz dosya YUKLENMEZ
- sozlesme parametresi yok: durur
- iki farkli platform dosyasi: iki ayri kanit, iki ayri hash
- dogrulama reddi 90 sn yeniden deneme yoluna DUSMEZ
- reddedilen deneme rotasyonu ve gunluk slotu tuketmez
- `fear-slide-hazir.yml` ffprobe bulur

---

## Sira

```
Rock 1  (bagimsiz)
Rock 2  (bagimsiz)
Rock 3  ->  Rock 4   (zorlama Rock 1+2 bittikten sonra acilir)
```

## Dokunulmayacaklar
- `sentinal_ihsan/unnatural-lab` , dogru calisan tek seri, referans.
- `canon/NEGATIVES.md:15` ekran yazisi yasagi.
- `MIN_KREDI = 700` , fiyatlanan istek yapilandirmasi (model, cozunurluk, sure)
  degismedigi surece gecerli. Bu plan hicbirini degistirmiyor.
- `yayin.jsonl` gecmisi ve onu okuyan rotasyon/gun kilidi mantigi.
- `concurrency: group: kie-uretim`.
- `aimagine/next-stop` , duraklatilmis, oyle kalir.
