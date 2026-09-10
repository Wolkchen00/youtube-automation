# RF-ISSUES-REELYZE , ertelenenler

r1 Same Page Meeting'inde bilincli olarak plandan CIKARILAN isler.
Cikarilmis olmalari onemsiz olduklari anlamina gelmez; kalibrasyon veya Ihsan'in
karari gerektirdikleri icin bu cevrimde YOK.

---

## I-1 , 1080p icin model degisikligi (Ihsan'in karari)

`core/kie_api.py:489`: *"Seedance duration is an integer 4-15s; resolution 480p/720p."*
AImagine-Fear 1080p uretemez cunku secilen model veremiyor.

1080p istiyorsak model degismeli. Bu su uc seyi birden degistirir:
- **Maliyet.** Su anki kosu 615 kredi = $3,08 (`MIN_KREDI = 700` buna dayali).
  Yeni modelin fiyati OLCULMEDEN tarifeye yazilmamali.
- **Gorunum.** Instagram'da 371.000 begeni alan estetik bu modelin ciktisi.
  Model degisikligi calisan seyi bozabilir.
- **Kredi tabani.** `MIN_KREDI` yeniden turetilmeli.

**Karar Ihsan'in.** Once tek bir kanarya uretimiyle gercek fiyat olculmeli.

## I-2 , fps 30 hedefi (model kisiti)

Kie yuku fps alani icermiyor (`tools/kie_uret.py:135-141`). Her cikti 24 fps.
24'ten 30'a yeniden kodlama sahte kare uretir, kalite katmaz.
`canon/MASTER-BLOCK.md:12`'deki "30 frames per second" ifadesi Rock 3'te kaldiriliyor.
Gercek 30 fps isteniyorsa I-1 ile birlikte degerlendirilmeli.

## I-3 , Yaratici vekil olcumler (kalibrasyon gerekiyor)

Planin ilk taslagindaki 8 maddelik skor kartinin su maddeleri CIKARILDI:

| Olcum | Neden cikarildi |
|---|---|
| Ilk yarim saniyede hareket | kare farki niyeti kanitlamaz, sadece degisimi olcer |
| Kesme temposu / en uzun plan | sabit `scene=0.3` esigi su spreyini, flash'i ve hizli kamera hareketini kesme saniyor. AImagine-Fear icerigi tam olarak su ve hizli hareket iceriyor. |
| OCR ile ekran yazisi | OCR yoksa "bilinmeyen" olmali; ayrica metin politikasi kanala gore degisir (AImagine-Fear'de YASAK, shadowedhistory'de ZORUNLU) |
| Dongu suruskligi | ilk/son kare benzerligi kusursuz donguyu kanitlamaz |
| Konusma var mi | EBU R128 + ses akisi varligi konusmayi KANITLAMAZ. Gercek VAD/ASR gerekir. |

Bunlar geri gelecekse once **etiketlenmis gercek video kumesi** uzerinde yanlis-pozitif
ve yanlis-negatif oranlari olculmeli, ve kanal bazinda kalibre edilmeli.
Kalibre edilmemis vekil olcum yanlis guven uretir, hicbir olcumden daha kotudur.

## I-4 , Trend hasati ve kanca uretimi (KILL, kapsam disi)

Ilk taslakta Rock 7'ydi. Planin kendisi "bu plan erisimi cozmez" diyor, sonra bir
erisim rock'u iceriyordu. Celiski. Codex KILL onerdi, kabul edildi.

Kaynaklar duruyor ve degerli, ama AYRI bir planin isi:
- `GET /discover/trending/{slug}` , kimlik dogrulamasi YOK, 52 nis x 24 video
- `POST /v1/generate` , kanca/aciklama/hashtag, ucretsiz ama **gunde 5 cagri**
- Indirme/desifre icin `yt-dlp` + `ffmpeg` yeterli, Reelyze gerekmiyor

## I-5 , Kesme (continuity) kapisi

Ilk taslakta Rock 4 "kesme dogrulamasi" vaat edip Done ve Proof'a koymamisti.
Kesme sayisi kanal bazinda kalibre edilmeden kapi olamaz (bkz. I-3).
`sentinal_ihsan` en uzun plani 17,85 saniye olmasina ragmen filonun en iyisi;
kor bir "4 saniye tavani" kurali onu reddederdi.

## I-6 , 271 videoluk gecmis tarama (shadowedhistory)

Sadece son 15 video olculdu. `shadowedhistory` 271 video uretmis ve iki aykirisi var
(1.179 ve 509). Tum gecmisi tarayip aykirilarin ortak ozelligini cikarmak bu kanal
icin cok degerli olur ama bu planin Core Focus'unda degil.
