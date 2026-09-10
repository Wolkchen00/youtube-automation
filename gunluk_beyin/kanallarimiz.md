# Kendi kanallarimiz , harita ve olculmus durum

Olcum tarihi: 10 Eylul 2026. Depo: `Desktop/Antigravity/Projeler/Youtube`

## Kritik ayrim: BES icerik hatti, DORT YouTube kanali

| Icerik hatti | Klasor | YouTube kanali | Kanal ID | Durum |
|---|---|---|---|---|
| unnatural-lab | `sentinal_ihsan/unnatural-lab` | sentinal_ihsan | `UC-Aht8VqAUMTUKYRQA3agYQ` | aktif, **referans** |
| event-horizon | `galactic_experience/event-horizon` | galactic_experiment | `UCVCRWrQYrIHW6csOsw9bDNw` | aktif |
| flashpoints | `shadowedhistory/flashpoints` | shadowedhistory | `UCUdp0KLBh4EeeSgVbwS_DhA` | aktif |
| AImagine-Fear | `AImagine-Fear/` | **aimagine** | `UCCgbHTzYKYawUT6zEo0nlDg` | aktif, bagimsiz hat |
| next-stop | `aimagine/next-stop` | **aimagine** | (ayni) | **paused** |

Fear ile next-stop AYNI YouTube kanalina basiyor. `core/config.py:35` dort kanal
tanimliyor cunku YouTube hesabi dort.

Sosyal hesaplar: `@aimagine_._` (IG, 4.494 takipci / 183 gonderi),
`@sentinal.ihsan.daily`, `@shad0wedhistory` (TikTok).

## Iki ayri mimari

**Ortak motor** (`core/` + `series/`) , dort seri kanalini besler.
Kanal-ozel Python kodu YOK, fark sadece `bible.json` + `series.json` verisi.
Cikti 1080x1920, 30 fps.

**AImagine-Fear** , tamamen bagimsiz hat (`AImagine-Fear/build.py`, `tools/`).
Cikti 720x1280, 24 fps. Ortak motordan sadece `core/uploader.upload_to_platform` kullanir.

Yayin siniri HEPSI icin ayni: `core.uploader.upload_to_platform()`.

## Olculmus performans (10 Eylul 2026)

| Kanal | Abone | Video | 30g medyan izlenme |
|---|---|---|---|
| sentinal_ihsan | 125 | 169 | **1.292** |
| galactic_experiment | 140 | 199 | 88,5 |
| shadowedhistory | 127 | 271 | 27 |
| aimagine | 98 | 250 | 4 |

## Olculmus ses durumu , en onemli tablo

| Seri | `master_lufs` | Olculen LUFS | True peak |
|---|---|---|---|
| unnatural-lab | **-14** | **-14,3 / -14,8** | -1,1 / -1,4 |
| event-horizon | YOK | -21,9 / -24,7 | -6,2 / -10,7 |
| flashpoints | YOK | -20,5 / -25,1 | -6,9 / -10,1 |
| next-stop | YOK | -16,1 / -17,1 | **+0,2 / +0,7 KIRPIYOR** |
| AImagine-Fear | (bagimsiz hat, yok) | -15,4 / -16,5 | -1,5 / -4,0 |

Kok neden: `series/produce.py:2148` `if master_lufs is None:` -> mastering ADIMI
TAMAMEN ATLANIYOR. Alan filoda sadece `unnatural-lab/bible.json:11`'de var.

### UYARI: `master_lufs` eklemek tek satirlik ve masum DEGIL

Uc davranisi birden ceviriyor:
```
produce.py:604   amix_normalize = master_lufs is None      -> KAPANIR
produce.py:656   music_volume = 0.50 if ... else 0.28       -> neredeyse IKI KAT
produce.py:659   limit_mix_peak = master_lufs is not None   -> ACILIR
```
Ustelik `unnatural-lab` `narration.native_mix_level: 0.5` tasiyor, digerleri TASIMIYOR
(`series/bible.py:269`: "Alan yoksa native ses tamamen kapalidir (0.0)").
Yani 0,50 muzik kalibrasyonu dogal sesin de bulundugu bir mikste yapildi; hedef
serilerde miks sadece anlatim + muzik, muzik orantili olarak DAHA YUKSEK olur.

`event-horizon` (126-156 WPM) ve `flashpoints` (70-119 WPM) yogun TTS anlatimli.
Ekle, **yayinlamadan** kos, ses seviyesinin yaninda anlatim/muzik dengesini de olc.
Mevcut arac: `tools/audio_master_check.py` (pencereli RMS, 1,5 dB esigi kullaniyor).
Mevcut test `tests/test_rocka_audio_master.py:117` alan eklenince KIRILIR, silme, guncelle.

## AImagine-Fear ozel durumu , calisan sey teknik degil

Ayni dosya, ayni gun, uc platform (Burj Khalifa, 6 Eylul):

| Platform | Sonuc |
|---|---|
| **Instagram** | **371.000 begeni, 1.098 yorum** (~6,5-9M izlenme TAHMINI) |
| YouTube | 1.995 izlenme |
| TikTok | 685 izlenme |

Teknik olarak en kotu ayarli kanal (720p, ses normalizasyonu yok, ekran yazisi yok)
Instagram'da patladi. **Teknik duzeltme hit uretmez.**

Ayni format, farkli sonuc (hepsi 720x1280, 24 fps, 15,1 sn, 0 kesme, benzer LUFS,
ayni metadata, kodda degisiklik yok):
- Burj Khalifa 6 Eyl: sicak altin/amber, gercek cekim gibi -> patladi
- Empire State 5 Eyl: doygun macenta neon, AI ciktisi gibi -> 13 izlenme

Hipotez: **doygun neon palet fotogercekcigi bozuyor.** Kanonun kendi hedefi
"Photorealistic live-action action-camera footage, not animation, not a render".
Test edilebilir: sonraki rotalarin yarisi sicak dogal isik, yarisi neon, IG'de karsilastir.

`canon/NEGATIVES.md:15` ekran yazisini YASAKLIYOR. Reelyze "ekle" diyor ama
371.000 begeni metinsiz geldi. Degistirmek ayri bir karar, ayri bir test.

## Bilinen acik hatalar (2026-09-10 itibariyle)

1. **`_delivery_copy()` cache hatasi** , `core/uploader.py:109`
   ```python
   delivery = video_path.parent / f"{video_path.stem}_delivery.mp4"
   if delivery.exists() and delivery.stat().st_size > 0:
       return delivery
   ```
   Cache anahtari dosya ADI, icerigi degil. Kaynak yeniden uretilirse ONCEKI
   icerigin kopyasi yuklenir. **Yanlis video yayinlanabilir.**
2. **Fear `sha()` kirpiyor** , `AImagine-Fear/tools/yayinla.py:46`
   `return h.hexdigest()[:16]`. Kanit icin tam 64 hane gerekiyorsa yetersiz.
3. **`sirdaki()` kilitlenme riski** , `AImagine-Fear/tools/gunluk.py:76-86`.
   Yayinlanmayan rota yayin kaydina girmez, "kullanilmamis" kalir, ertesi gun
   yine secilir. "Harcamadan once reddet" davranisi karantina olmadan eklenirse
   kanal yayin yapmayi tamamen durdurur.
4. **`approver._publish_approved()`** basarisizlikta `approved=True` birakiyor
   (`series/approver.py:78-79`), deterministik red sonsuza kadar yeniden denenir.

## Ilgili dokumanlar
- `Projeler/Reelyze_Arastirma/REELYZE-DOSYASI.md` , tam metodoloji dosyasi
- `Projeler/Reelyze_Arastirma/codex-toplanti/` , plan, ertelenenler, 5 turluk inceleme
- Her kanal klasorunde `REELYZE-RAPOR.md` , kanal bazli analiz
