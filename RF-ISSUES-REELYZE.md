# RF-ISSUES-REELYZE , ertelenenler

Same Page Meeting'de bilincli olarak plandan CIKARILAN isler.
Cikarilmis olmalari onemsiz olduklari anlamina gelmez.

---

## I-1 , 1080p yetenegi ARASTIRMASI (r3'te ertelendi)

**r2'deki hatali surum duzeltildi.** Once "1080p imkansiz" yazmistim; yanlisti:
```
core/kie_api.py:483   model: str = "bytedance/seedance-2-fast"   <- FAST varyanti
core/kie_api.py:489   "duration 4-15s; resolution 480p/720p"     <- FAST icin gecerli
AImagine-Fear/tools/gunluk.py:30   MODEL = "bytedance/seedance-2" <- FAST DEGIL
```
`seedance-2` (fast olmayan) sinirlari depoda **hicbir yerde belgelenmemis.**
Ters ipucu: `sentinal_ihsan/KONSEPT_v3_TASLAK.md:365` bir Seedance varyantinda
"720p 20 sn ~1.260 kredi" diyor.

**Durum: BILINMIYOR.** 1080p mumkun mu, kac krediye mal olur, bilmiyoruz.

Kanarya calistirilirsa sartlari (r3):
- Somut, `build.py --check`'ten gecmis bir rota slug'i
- **Model ACIKCA yazilmali:** `--model bytedance/seedance-2`.
  `kie_uret.py:112-113` varsayilanlari `sora-2-pro-storyboard` ve `25` saniye,
  yani belirtilmezse YANLIS modeli YANLIS surede calistirir ve krediyi bosa harcar.
- `--n-frames 15`, ses ayari acik, benzersiz cikti etiketi
- **`concurrency: group: kie-uretim` kilidi ICINDE** calismali, yoksa bakiye farki
  diger kanallarin harcamasini da icerir ve olcum anlamsizlasir
- Gonderimden ONCE harcama onayi ve butce
- Basari, red ve zaman asimi hallerinin UCUNDE de bakiye ve gorev sonucu kaydedilir
- Istek/yanit/probe kaniti saklanir

**Karar Ihsan'in** (kredi harcanacak, cuzdan dort kanalla ortak).
Bu plan bu karari BEKLEMIYOR: sozlesme olculen gercegi (720x1280, 24 fps) kaydeder.

## I-2 , fps 30 (model kisiti)

`tools/kie_uret.py:135-141` yukunde fps alani YOK. Her cikti 24 fps.
24'ten 30'a yeniden kodlama sahte kare uretir, kalite katmaz.
`canon/MASTER-BLOCK.md:12`'deki "1080x1920, 30 frames per second" ifadesi bugun
gerceklige uymuyor. Metni duzeltmek I-1 karariyla birlikte ele alinmali;
sozlesme bu arada olculen gercegi (24 fps) kaydeder.

## I-3 , Yaratici vekil olcumler (kalibrasyon gerekiyor)

Ilk taslaktaki 8 maddelik skor kartindan CIKARILANLAR:

| Olcum | Neden |
|---|---|
| Ilk yarim saniyede hareket | kare farki niyeti kanitlamaz |
| Kesme temposu / en uzun plan | sabit `scene=0.3` esigi su spreyini ve hizli kamera hareketini kesme saniyor; AImagine-Fear icerigi tam olarak bu |
| OCR ile ekran yazisi | metin politikasi kanala gore degisir (Fear'de YASAK, shadowedhistory'de ZORUNLU); OCR yoksa "bilinmeyen" olmali |
| Dongu suruskligi | ilk/son kare benzerligi donguyu kanitlamaz |
| Konusma var mi | EBU R128 + ses akisi konusmayi KANITLAMAZ; gercek VAD/ASR gerekir |

Geri gelecekse once **etiketlenmis gercek video kumesinde** yanlis-pozitif ve
yanlis-negatif oranlari olculmeli, kanal bazinda kalibre edilmeli.

## I-4 , Trend hasati ve kanca uretimi (KILL, r1)

Plan "erisimi cozmez" deyip erisim rock'u iceriyordu. Celiski.
Kaynaklar duruyor: `GET /discover/trending/{slug}` (kimlik dogrulamasi YOK),
`POST /v1/generate` (ucretsiz, **gunde 5 cagri**), indirme/desifre icin `yt-dlp` yeterli.

## I-5 , Kesme (continuity) kapisi

Kanal bazinda kalibre edilmeden kapi olamaz. `sentinal_ihsan` en uzun plani
17,85 saniye olmasina ragmen filonun en iyisi; kor bir "4 saniye tavani" onu reddederdi.

## I-6 , 271 videoluk gecmis tarama (shadowedhistory)

Sadece son 15 video olculdu. Iki aykiri var (1.179 ve 509).
Tum gecmisi tarayip aykirilarin ortak ozelligini cikarmak degerli ama Core Focus'ta degil.

## I-7 , Kredi rezervasyonu (KILL, r2)

Cuzdan zaten `concurrency: group: kie-uretim` ile serilestirilmis
(`calibrate.yml`, `event-horizon.yml`, `fear-slide.yml`). `KIE_BALANCE_FLOOR`
workflowlarda set edilmiyor; gitignore edilmis yerel defter izole kosucularda
koordinasyon saglayamaz; 900 sn TTL, Fear'in 1500 sn zaman asimindan kisa.
Basit olan zaten var.

## I-8 , Rota suresi ve karantina (r3'te ertelendi)

`tools/gunluk.py:31` `SURE = 15` sabit; `routes/toronto-cn-red-dusk.md:6` `DURATION: 20`,
`routes/vegas-strat-blue-rain-25.md:6` `DURATION: 25` okunmuyor.

**Neden ertelendi:** modelin gercek sure sozlesmesi bilinmiyor (bkz. I-1).
Tek bir 1080p kanaryasi SURE sinirlarini kanitlamaz. Bilmeden "20 saniye uyumsuz"
demek saglayici sinirini uydurmak olur. Sirket politikasi olarak sinirlamak baska,
saglayici sinirini iddia etmek baska.

**Geri gelirse ZORUNLU parca , karantina.** `tools/gunluk.py:76-86` `sirdaki()`:
```python
for s in SIRA:
    if s not in kullanilmis:   # gecmis = yayin kaydi
        return s
...
return min(SIRA, key=lambda s: son.get(s, -1))   # gecmiste yoksa -1, HEP kazanir
```
Bir rota yayinlanmazsa yayin kaydina hic girmez, "kullanilmamis" kalir ve
**ertesi gun yine secilir. Kalici kilitlenme, kanal yayin yapmayi tamamen durdurur.**
Ikinci dalda `son.get(s, -1)` yuzunden ayni sonuc.

Yani "harcamadan once reddet" davranisi karantina OLMADAN eklenirse kanali oldurur.
Karantina sartlari: her iki secim dalinda da filtrele, elle `--sehir` secimini de
reddet, bos havuz halini test et, ve kayitlari `yayin.jsonl`e YAZMA (okuyucular
oradaki satirlari yayin gecmisi sayiyor, rotasyon ve gun kilidi bozulur).

## I-9 , next-stop (duraklatilmis)

`aimagine/next-stop/series.json` -> `status: paused`.
Duraklatilmis seri uretim yapamaz, dogrulama ciktisi da veremez.
`master_lufs` eklenecekse seri yeniden aktiflestirildiginde ele alinmali.
Olculen durumu kayda gecsin: -16,1 / -17,1 LUFS, **true peak +0,2 ve +0,7 dBFS**
(yani dijital kirpma). Seri geri acilirsa bu ilk duzeltilecek sey.
