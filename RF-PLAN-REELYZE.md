# RF-PLAN-REELYZE , uc fazli plan

Tarih: 10 Eylul 2026 (Los Angeles)
Dal: `codex-reelyze` (worktree, ana agac bozulmasin)
Kaynak arastirma: `Projeler/Reelyze_Arastirma/REELYZE-DOSYASI.md`

## Core Focus (tek cumle)

Yayinlanan her kisa videonun teknik kalitesini olculebilir hale getir ve yayindan
ONCE bir kapidan gecir, boylece bes kanalin hicbiri sessizce bozuk dosya yayinlamasin.

## Bu plan neyi COZMEZ (acikca kapsam disi)

Bu plan **erisim (reach) sorununu cozmez**. Olculen gercek soyle: AImagine-Fear
teknik olarak en kotu ayarlara sahip kanal (720p, ses normalizasyonu yok, ekran yazisi
yok) ve Instagram'da 371.000 begeni aldi; teknik olarak dogru kurulmus dort seri kanali
(1080x1920, loudnorm I=-14) 27 ile 1292 arasi medyan izlenmede. **Teknik duzeltme bir
hit uretmez.** Bu plan yalnizca "urettigimiz sey niyetimize uysun" sorununu cozer.
Erisim/format/kanal stratejisi AYRI bir istir ve bu plandan sonra gelir.

## Dogrulanmis durum (kanal boru hatti haritasi, 12 ajan, her iddia dosya:satir kanitli)

| Kanal | Cozunurluk | Ses norm. | Ekran yazisi | Kalite kapisi |
|---|---|---|---|---|
| aimagine / from-scratch | 1080x1920 | VAR (I=-14) | yok | critic.py QC |
| sentinal_ihsan | 1080x1920 | VAR | VAR | critic.py QC |
| galactic_experience | 1080x1920 | VAR | yok | critic.py QC |
| shadowedhistory | 1080x1920 | VAR (klip) | VAR | critic.py QC |
| **AImagine-Fear** | **720x1280, 24fps** | **YOK** | **yasak (kanon)** | 720x1280 sabit bekliyor |

Yani **kusur filo geneli degil, tek kanalda**. Dort seri kanali ortak motoru
(`core/` + `series/`) kullaniyor ve zaten dogru; AImagine-Fear tamamen bagimsiz bir
hat ve tek basina geride.

---

# FAZ 1 , AImagine-Fear uretim hattini niyetine uydur

## Rock 1: Cozunurluk ve fps

**Sorun (dogrulandi):** `canon/MASTER-BLOCK.md:12` modele "1080x1920, 30 frames per
second" diyor. `tools/gunluk.py:32` API'ye `COZUNURLUK = "720p"` gonderiyor.
Canli kanit `yayin.jsonl` -> `prevalidation_metadata: {width:720, height:1280, fps:24.0}`.
Taklit edilen kaynak `reference/TERSINE-MUHENDISLIK.md:21`'e gore 1080x1920 30 fps.

**Done looks like:** `tools/gunluk.py` 1080p uretir; prompt, API parametresi ve kalite
kapisi ayni degeri soyler; fps de denetlenir.

**Proof:**
`python -m pytest AImagine-Fear/tests -q -k "cozunurluk or fps"`
ve `python AImagine-Fear/tools/kie_uret.py <slug> --dry` ciktisinda `"resolution": "1080p"`.

## Rock 2: Rota suresi okunmuyor

**Sorun (dogrulandi):** `tools/gunluk.py:31` `SURE = 15` sabit; `:148` bunu
`--n-frames` olarak gonderiyor. `routes/toronto-cn-red-dusk.md:6` `DURATION: 20`,
`routes/vegas-strat-blue-rain-25.md:6` `DURATION: 25` diyor ve bu deger HIC OKUNMUYOR.
20 saniyelik rota secilirse promptun zaman cizelgesi [0.0-20.0] sayar, API'den 15 sn
istenir, cikan video kapiyi gecer (15 +/- 1.5) ve kaydiragin son ucte biri hic uretilmez.

**Done looks like:** sure rota dosyasindan okunur; kapi da ayni degeri kullanir;
rota suresi ile uretilen sure uyusmazsa yayin durur.

**Proof:** `python -m pytest AImagine-Fear/tests -q -k "sure or duration"`
(20 ve 25 saniyelik rotalar icin ayri vaka; okunamayan/eksik DURATION icin de vaka.)

## Rock 3: Ses seviyesi normalizasyonu

**Sorun (dogrulandi):** AImagine-Fear altinda hicbir `.py` dosyasinda
`loudnorm|dynaudnorm|LUFS|volume=|acompressor|alimiter` gecmiyor. Olculen sonuc:
Burj Khalifa **-15,4 LUFS**, Sanghay **-16,5 LUFS**; sosyal hedef -16 ila -13.
Depoda hazir cozum VAR ve bu kanal cagirmiyor: `core/ffmpeg_tools.py:234-372`
(`master_audio`, iki gecisli loudnorm, `target_i=-14.0, target_tp=-1.0, target_lra=11.0`).

**Done looks like:** `tools/gunluk.py` icinde `denetle()` ile `yayinla.py` arasinda
master_audio cagrilir; cikti -14 LUFS +/- 1, true peak <= -1 dBTP.

**Proof:** `python AImagine-Fear/tools/kontrol.py <video> --ses` cikisinda olculen
LUFS -15,0 ile -13,0 arasinda ve true peak <= -1,0 dBTP.

## Rock 4: Kalite kapisini sabitlerden kurtar

**Sorun (dogrulandi):** `tools/gunluk.py:99`
`if alanlar.get("width") != "720" or alanlar.get("height") != "1280":`
Kapi 720x1280'i DOGRU kabul ediyor. Rock 1 uygulanirsa bu kapi dogru 1080x1920 videoyu
"sorunlu" diye isaretler ve yayini durdurur. Kapi ayrica fps'e, ses seviyesine ve
kesme sayisina hic bakmiyor.

**Done looks like:** beklenen degerler tek bir yerde tanimli (sabit sozluk veya config),
kapi oradan okur, ve kapi fps + LUFS + true peak de dogrular.

**Proof:** `python -m pytest AImagine-Fear/tests -q -k "kapi or denetle"` , 1080x1920
gecer, 720x1280 kalir, yanlis fps kalir, -18 LUFS kalir.

---

# FAZ 2 , Yayin oncesi skor karti (filo geneli, paylasilan modul)

## Rock 5: `core/skor_karti.py` , olcen modul

Reelyze'in yayin oncesi 8 maddelik kontrol listesini KODA cevir. Sekiz maddenin
dokuzu insan yargisi gerektiriyor; makinece olculebilen alt kume su:

| # | Madde | Nasil olculur |
|---|---|---|
| 1 | Ilk karede hareket var mi | ilk 0,5 sn'de kare farki esigi (ffmpeg) |
| 3 | Ilk 1,5 sn'de ekran yazisi | kare cikar + OCR (opsiyonel bagimlilik) |
| 5 | Ilk 10 sn'deki kesme sayisi | sahne tespiti, `select='gt(scene,0.3)'` |
| 6 | Ses: konusma var mi, seviye dogru mu | ebur128 (LUFS/TP/LRA) + ses akisi |
| 8 | En uzun tek plan 4 sn'yi asiyor mu | plan uzunluklari |
| + | Sure/tamamlanma beklentisi | sure kovasi |
| + | Dongu uygunlugu (ilk/son kare benzerligi) | kare karsilastirma |

**Done looks like:** `skorla(video_yolu) -> {"puan": int, "maddeler": [...], "engel": [...]}`
Bagimsiz, saf fonksiyon; ffmpeg disinda zorunlu bagimlilik yok; OCR yoksa o madde
"olculemedi" doner, uydurulmaz.

**Proof:** `python -m pytest tests/test_skor_karti.py -q` , sentetik test videolariyla
(siyah kare, tek plan, sessiz, cok gurultulu) her maddenin hem gecer hem kalir vakasi.

## Rock 6: Skor kartini iki mimariye de bagla

Iki ayri kapi var, ikisi de skor kartini cagirmali:
- `AImagine-Fear/tools/gunluk.py` -> `denetle()`
- `series/critic.py` / `series/produce.py` -> QC akisi

**Done looks like:** her iki hat da yayindan once skor kartini calistirir, sonucu loga
ve yayin kaydina yazar. **Ilk surumde skor YAYINI ENGELLEMEZ, sadece raporlar** (esikler
gercek veriyle kalibre edilene kadar). Yalnizca sert teknik hatalar (cozunurluk, ses yok)
engeller, bunlar zaten mevcut kapida.

**Proof:** her iki hattin kuru kosusu skor kartini iceren bir rapor satiri uretir;
`python -m pytest tests -q -k "skor"` yesil.

---

# FAZ 3 , Bedava dis sinyal

## Rock 7: Trend hasati ve kanca uretici

Dogrulanmis bedava kaynaklar:
- `GET /discover/trending` ve `GET /discover/trending/{slug}` , **kimlik dogrulamasi
  YOK**, 52 nis x 24 video, `outlier_score` ile. Gunluk cekilebilir.
- `POST /v1/generate` (kanca/aciklama/hashtag) , ucretsiz ama **gunde 5 cagri**
  (blog dogru, SKILL.md'deki "50/gun" yanlis; canli test: `"Free tier limit reached
  (5 calls/day)"`).
- Indirme ve desifre icin Reelyze'a gerek YOK: `yt-dlp` + `ffmpeg` ayni isi kotasiz yapar.

**Done looks like:** `tools/trend_hasat.py` gunluk 52 nisi ceker, yeni girenleri
(`first_seen_at`) isaretler, kendi normalizasyonumuzu hesaplar (nis medyanina bolerek,
cunku `outlier_score`'un formulu cozulemedi) ve JSONL'e yazar. Kanca uretimi ayri bir
komut ve gunluk 5 cagriyi asmaz, asarsa duraklar.

**Proof:** `python tools/trend_hasat.py --dry` en az 1000 kayit ceker ve sema dogrular;
`python -m pytest tests/test_trend_hasat.py -q` , 429 ve bos yanit vakalari dahil.

---

## Sira ve bagimliliklar

```
Rock 1 -> Rock 4   (kapi, yeni cozunurlugu kabul etmeli, YOKSA yayin durur)
Rock 2, Rock 3     (bagimsiz, paralel)
Rock 5 -> Rock 6   (once modul, sonra baglama)
Rock 7             (bagimsiz)
```

**KRITIK:** Rock 1 ile Rock 4 AYNI commit'te gitmeli. Rock 1 tek basina yayini durdurur.

## Dokunulmayacaklar

- `core/` ve `series/` icindeki dort kanalin calisan akisi (Rock 6 disinda)
- Kie cuzdani mantigi: cuzdan dort kanalla ORTAK (`tools/kie_uret.py:6`), kredi tabani
  `MIN_KREDI = 700` degismeyecek
- `canon/NEGATIVES.md`'deki ekran yazisi yasagi , bu KASITLI bir estetik karar.
  Reelyze "ekran yazisi ekle" diyor ama bu kanalin kimligi metinsiz olmasi.
  Degistirilecekse Ihsan'in karari, bu planda DEGIL.
- `yayin.jsonl` gecmis kayitlari
