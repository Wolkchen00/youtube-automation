# AImagine-Fear , video analiz raporu

Tarih: 10 Eylul 2026 (Los Angeles)
Yontem: yt-dlp ile indirildi, ffmpeg/ffprobe + EBU R128 ile olculdu, kareler goz ile incelendi.
Bir video (Sanghay) Reelyze'in ucretsiz kare-kare analizinden gecti: `Reelyze_Arastirma/RAPOR-sanghay-w3KuWLDTCpQ.md`
Metodoloji ve esikler: `Projeler/Reelyze_Arastirma/REELYZE-DOSYASI.md`

---

## 1. Bu kanal aslinda KAZANIYOR, ama YouTube'da degil

Ayni dosya, ayni gun, uc platform:

| Video | Tarih | Instagram | YouTube | TikTok |
|---|---|---|---|---|
| **Burj Khalifa / Dubai** | 6 Eyl | **371.000 begeni, 1.098 yorum** | 1.995 | 685 |
| Sanghay | 9 Eyl | 299 begeni | 1.914 | 419 |
| Eyfel | 8 Eyl | olculemedi | 1.497 | 430 |
| CN Tower | 7 Eyl | olculemedi | 1.403 | 404 |
| Empire State | 5 Eyl | olculemedi | **13** | 376 |
| Tokyo | 4 Eyl | olculemedi | 39 | 362 |
| Vegas STRAT | 3 Eyl | olculemedi | 49 | 318 |

Instagram hesabi `@aimagine_._`: 4.494 takipci, 183 gonderi.
371.000 begeni, kendi olctugumuz begeni orani (izlenmenin %4-5,8'i) uzerinden kabaca
**6,5-9 milyon izlenmeye** denk gelir. Kesin rakam IG Insights'ta.

**Sonuc: icerik fikri calisiyor. Sorun YouTube dagitiminda.**

---

## 2. Olculen teknik durum

| Video | Cozunurluk | fps | Sure | Kesme | En uzun plan | LUFS | True peak |
|---|---|---|---|---|---|---|---|
| Burj Khalifa (HIT) | **720x1280** | **24** | 15,1 sn | **0** | 15,08 sn | -15,4 | -3,8 |
| Sanghay | **720x1280** | **24** | 15,1 sn | **0** | 15,13 sn | -16,5 | -3,5 |
| Empire State (olu) | **720x1280** | **24** | 15,1 sn | **0** | 15,08 sn | -16,1 | -4,0 |
| Vegas STRAT (olu) | **720x1280** | **24** | 15,1 sn | **0** | 15,08 sn | -15,5 | -1,5 |

Hedefler: cozunurluk 1080x1920, fps 30, LUFS -16 ila -13, true peak <= -1 dBTP.

**Cozunurluk kesin dogrulandi.** yt-dlp'ye gore YouTube'un sundugu en yuksek dikey
rendition 720x1280. YouTube kaynaktan yukariya olceklemez, yani **gercekten 720p yayinladik**.

### Uc yonlu celiski (kod okundu, satir satir)
```
canon/MASTER-BLOCK.md:12   modele "1080x1920, 30 frames per second" diyor
tools/gunluk.py:32         COZUNURLUK = "720p"          <- API'ye giden bu
tools/gunluk.py:99         kalite kapisi 720x1280 BEKLIYOR, farkliysa HATA sayar
reference/TERSINE-MUHENDISLIK.md:21  taklit edilen kaynak 1080x1920, 30 fps
```
Prompt'taki 1080x1920 olu metin. Kapi 720x1280'i dogru kabul ettigi icin bu sorunu
asla yakalayamaz; **dogru bir 1080x1920 videoyu "sorunlu" diye isaretler ve yayini durdurur.**

### Ikinci hata: rota suresi okunmuyor
```
tools/gunluk.py:31    SURE = 15        (sabit)
tools/gunluk.py:148   --n-frames olarak bu gonderiliyor
routes/toronto-cn-red-dusk.md:6      DURATION: 20     <- OKUNMUYOR
routes/vegas-strat-blue-rain-25.md:6 DURATION: 25     <- OKUNMUYOR
```
20 saniyelik bir rota secilirse promptun zaman cizelgesi [0.0-20.0] boyunca beat sayar,
API'den 15 saniye istenir, cikan video kapiyi GECER (15 +/- 1,5) ve **kaydiragin son ucte
biri hic uretilmez**. Kapi promptu degil kendi sabitini dogruluyor.

### Ucuncu hata: ses seviyesi normalizasyonu yok
`AImagine-Fear/` altindaki hicbir `.py` dosyasinda `loudnorm|dynaudnorm|LUFS|volume=`
gecmiyor. Depoda hazir cozum VAR ve bu kanal cagirmiyor:
`core/ffmpeg_tools.py:234-372` (`master_audio`, iki gecisli loudnorm, hedef I=-14, TP=-1,0).
Olculen sonuc: -15,4 ile -16,5 arasi, yani hedefin altinda.

---

## 3. HIT ile OLU arasindaki gercek fark: GORUNTU, teknik degil

Teknik olarak dort video da BIREBIR AYNI: 720x1280, 24 fps, 15,1 sn, 0 kesme, benzer LUFS.
Metadata da ayni (baslik kalibi, etiketler, kategori). Kodda 5-6 Eylul arasi
**hicbir degisiklik yok**, sadece durum commitleri. Yani fark uretim ayarlarinda degil.

Kareleri karsilastirdim:

**Burj Khalifa (HIT):** sicak altin/amber tonlar, gece Dubai'nin gercek sehir izgarasi
ta asagida, cam zeminde yansimalar, ciplak ayaklar. **Gercek cekim gibi duruyor.**
Yukseklik ilk karede aninda okunuyor.

**Empire State (OLU, 13 izlenme):** her yerde parlak macenta/pembe neon seritler, kar,
desenli siyah tayt. **Yapay zeka cikti gibi duruyor.** Ustteki pembe neon seritler
CGI olarak okunuyor, mekan gercekligi kayboluyor.

Kanonun kendi hedefi: *"Photorealistic live-action action-camera footage, not animation,
not a render, not a game"* (`canon/MASTER-BLOCK.md:12`).
**Patlayan video bu hedefi tutturmus, olen video tutturamamis.**

En guclu hipotez: **doygun neon palet fotogercekcigi bozuyor.** Sicak/dogal isikli
gece sahneleri gercek duruyor; macenta/siklamen neon serit ekleyen rotalar yapay duruyor.
Bu test edilebilir: sonraki 6 rotanin yarisini sicak dogal isikla, yarisini neonla uret,
IG'de karsilastir.

---

## 4. YouTube neden yemiyor

Olculebilir olanlar:

1. **Kanal gecmisi zehirli.** `aimagine` YouTube kanali: 98 abone, 250 video,
   30 gunluk medyan izlenme **4**. Ayni kanalda 56 saniyelik "Next Stop" serisi
   (3-17 izlenme) ile 15 saniyelik POV kaydiragi yan yana duruyor. Algoritma bu kanaldan
   ne bekleyecegini bilmiyor. Instagram hesabi ise SADECE bu icerigi yayinliyor ve
   4.494 takipcisi var.
2. **Etiket yok.** Alti videonun da etiketleri YouTube'un otomatik copu:
   `video, sharing, camera phone, video phone, free, upload`. Gercek etiket set edilmemis.
3. **#shorts yok.** Sekiz videodan sadece birinde (`Lmf0kyxhxhg`) basliğinda `#shorts` var.
4. **Baslik kancasiz.** Basliklar 98-99 karakter, YouTube'un 100 karakter sinirinda
   kesiliyor: *"You're sliding down past the Oriental Pearl Tower on a transparent slide
   above Shanghai. Every"* , cumle yarida bitiyor, kanca yok.
5. **Kategori "People & Blogs"**, icerik seyahat/thrill.

DIKKAT: bunlarin hicbiri HIT ile OLU'yu ayirmiyor (ikisinde de ayni). Yani bunlar
**tavani** aciklar, gunler arasi farki degil. YouTube'da 13'ten 1.995'e sicrama
6 Eylul'de oldu ve bu tam da IG'de patlayan gun. Muhtemel: IG virali capraz trafik surukledi.

---

## 5. Ne yapilmali (etki sirasina gore)

1. **Palet testi (en yuksek etki, kod degisikligi yok).** Sonraki 6 rotayi ikiye bol:
   3'u sicak/dogal gece isigi, 3'u doygun neon. IG begeni sayilarini karsilastir.
   Hipotez: sicak olanlar kazanir. Bu tek deney kanalin gelecegini belirler.
2. **Cozunurluk 1080p + kapiyi ayni anda duzelt.** IKISI AYNI COMMIT'TE gitmeli,
   yoksa yayin durur. (`RF-PLAN-REELYZE.md` Rock 1 + Rock 4)
3. **fps 30.** Kanon 30 istiyor, 24 uretiliyor, kapi fps'e hic bakmiyor.
4. **Ses normalizasyonu.** `core/ffmpeg_tools.master_audio` cagir, hedef -14 LUFS.
5. **Rota DURATION alanini oku.** 20 ve 25 saniyelik rotalar su an sessizce kirpiliyor.
6. **YouTube metadata:** gercek etiketler, basliga kanca (ilk 40 karaktere sigsin),
   `#shorts`, kategori "Travel & Events" veya "Entertainment".
7. **Next Stop'u bu kanaldan ayir.** Iki farkli format tek kanalda algoritmayi bolüyor.

## 6. Neye DOKUNMA

- `canon/NEGATIVES.md:15` ekran yazisi yasagi (*"NO on-screen text. NO caption..."*).
  Reelyze "ekran yazisi ekle" diyor ama bu kanalin kimligi metinsiz olmasi ve
  **371.000 begeni metinsiz geldi.** Degistirilecekse ayri bir karar, ayri bir test.
- Kie cuzdani mantigi. Cuzdan dort kanalla ORTAK (`tools/kie_uret.py:6`).
  720p'den 1080p'ye cikmak kredi maliyetini artirabilir; once tarifeyi olc.
- `yayin.jsonl` gecmis kayitlari.

## 7. Acik sorular (olculemedi)

- IG gercek izlenme sayilari (Insights gerekiyor; begeniden tahmin ettim)
- Retention egrileri (YouTube Studio / IG Insights gerekiyor)
- 1080p'nin Kie kredi maliyeti (olculmedi, tarifeye yazilmadan test edilmeli)
