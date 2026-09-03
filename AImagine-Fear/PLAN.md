# AImagine Fear Slide, uretim plani

## Core Focus (tek cumle)

Tek bir rota dosyasindan, tek promptla tek video ureten, yapistirmaya hazir bir korku
kaydiragi promptu uret; oyle ki her rota ayni kamera, ayni beden, ayni kaydirak ve ayni
ses yasasini harfi harfine tasisin ve sadece sehir, landmark, renk ve hava degissin.

## Ne yapmiyoruz

- Klip zinciri YOK. Kaynak kanal 20 saniyeyi tek kesintisiz cekimde uretiyor
  (olculdu: `reference/TERSINE-MUHENDISLIK.md`). Bizde de bir rota = bir prompt = bir video.
- OPENING STATE / END STATE kaynastirma (weld) mantigi YOK. Tek klip oldugu icin gerekmiyor.
  Iki alan promptta yine yaziliyor cunku modele ilk kareyi ve son kareyi kilitliyorlar,
  ama bir sonraki klibe kopyalanmiyorlar.
- Video uretimi, indirme, yayinlama YOK. Bu depo sadece metin uretir.

## Mimari

```
canon/MASTER-BLOCK.md    her promptta AYNEN tekrarlanan sekiz bolum
canon/NEGATIVES.md       her promptun sonuna eklenen NEGATIVE blogu
canon/CAPTION.md         aciklama metni kalibi ve sabit etiketler (dogrulama icin)
routes/<slug>.md         rotaya ozel: baslik alanlari + OPENING STATE + BEATS + END STATE + VOICE + CAPTION
build.py                 uretici ve dogrulayici
out/<slug>/PROMPT.txt    yapistirmaya hazir tek prompt
out/<slug>/CAPTION.txt   yapistirmaya hazir aciklama + etiketler
out/<slug>/VOICE.txt     ses/replik zaman cizelgesi (referans, prompta gomulu de gelir)
tests/                   pytest
```

## ROCK: build.py

### Girdi ayristirma

`canon/MASTER-BLOCK.md` ve `canon/NEGATIVES.md` dosyalarindan `## BASLIK` seviyesindeki
bolumler okunur. Master bloktan alinacak bolumler, tam bu sirayla:

`FORMAT`, `INDEPENDENCE NOTE`, `CAMERA`, `RIDER`, `SLIDE`, `MOTION AND GRAVITY`,
`WORLD`, `AUDIO`

`canon/NEGATIVES.md` dosyasindan `NEGATIVE` bolumu alinir.

`routes/` altindaki, adi alt cizgi ile BASLAMAYAN her `.md` dosyasi bir rotadir.
Rota dosyasinin ust kisminda `ANAHTAR: deger` satirlari bulunur. Zorunlu anahtarlar:

`SLUG`, `DESTINATION`, `LANDMARK`, `DURATION`, `NEON`, `LEGWEAR`, `WEATHER`, `SOURCE`

Rota dosyasinin `## BASLIK` bolumleri, hepsi zorunlu:

`OPENING STATE`, `BEATS`, `END STATE`, `VOICE`, `CAPTION`

### Token yerlestirme

Master blok icindeki su tokenlar rota basliklarindan doldurulur:

| Token | Kaynak |
|---|---|
| `<<DURATION>>` | DURATION |
| `<<NEON>>` | NEON |
| `<<LEGWEAR>>` | LEGWEAR |
| `<<WEATHER>>` | WEATHER |
| `<<CITY>>` | DESTINATION |
| `<<LANDMARK>>` | LANDMARK |

Uretilen ciktida `<<` ya da `>>` kalirsa bu bir HATADIR.

### Cikti bicimi

`out/<slug>/PROMPT.txt` su sirayla, bolumler arasinda bos satir:

```
FORMAT
<metin>

INDEPENDENCE NOTE
<metin>

CAMERA
<metin>

RIDER
<metin>

SLIDE
<metin>

MOTION AND GRAVITY
<metin>

WORLD
<metin>

AUDIO
<metin>

OPENING STATE
At frame one: <rota OPENING STATE metni>

TIMELINE
<rota BEATS metni, satir satir aynen>

VOICE
<rota VOICE metni, satir satir aynen>

END STATE
At the final frame: <rota END STATE metni>

NEGATIVE
<negatif blok>
```

`out/<slug>/CAPTION.txt` rota CAPTION bolumunun aynisi.
`out/<slug>/VOICE.txt` rota VOICE bolumunun aynisi.

### Dogrulama (`python build.py --check`)

Herhangi biri patlarsa dosya adi, rota ve sebep yazilir ve cikis kodu 1 olur.

1. **Zaman butunlugu.** BEATS satirlari `[a-b] metin` bicimindedir. Ilk aralik `0.0`
   ile baslar, son aralik `DURATION` ile biter, her araligin bitisi bir sonrakinin
   baslangicina esittir. Bosluk ve cakisma HATADIR. En az 5 aralik olmalidir.
2. **Ses zamanlari.** VOICE satirlari `[a-b] ...` bicimindedir ve her ikisi de
   `0.0` ile `DURATION` arasinda olmalidir. VOICE araliklari birbiriyle cakisabilir
   (ciglik ve kahkaha ust uste binebilir), bu hata degildir.
3. **Token kalintisi.** Ciktida `<<` veya `>>` yoksa gecer.
4. **Yasakli ifadeler.** Iki ayri liste var, iki ayri kapsamda. Ikisi de buyuk kucuk
   harf duyarsizdir ve ihlalde rota adi, bolum adi ve satir yazilir.

   **Liste A, boru hatti sizintisi.** Kapsam: uretilen `PROMPT.txt` metninin TAMAMI,
   `NEGATIVE` blogu dahil, hicbir istisna yok. Bu ifadeler promptta hicbir bicimde,
   olumlu ya da olumsuz, gecmemelidir; cunku hepsi modele "bu bir dizinin parcasi"
   dedirtir ve tek cekim kuralini bozar:
   `clip 1`, `clip 2`, `next clip`, `previous clip`, `part 1`, `part 2`,
   `part one`, `part two`, `first clip`, `second clip`

   **Liste B, bicim celiskisi.** Kapsam: SADECE rotanin yazdigi bolumler, yani
   `OPENING STATE`, `TIMELINE`, `VOICE`, `END STATE` ve `CAPTION.txt`. Kanon
   bolumleri (FORMAT, INDEPENDENCE NOTE, CAMERA, RIDER, SLIDE, MOTION AND GRAVITY,
   WORLD, AUDIO) ve `NEGATIVE` blogu bu listeden MUAFTIR, cunku onlar bu terimleri
   bilerek yasak olarak yaziyor:
   `cut to`, `slow motion`, `slow-motion`, `time lapse`, `timelapse`, `drone shot`,
   `selfie`, `voiceover`, `voice-over`, `background music`, `soundtrack`,
   `third person`, `third-person`

   Gerekce: Liste B'nin isi, yeni bir sehir yazan kisinin kanonla kavga eden bir
   cumle yazmasini engellemek. Kanonun kendi metni zaten elle bir kez incelendi ve
   sabit; onu taramak sadece yanlis alarm uretir.
5. **Durum metinleri.** Rota `OPENING STATE` ve `END STATE` metinleri
   `frame one`, `first frame`, `last frame`, `final frame` ifadelerini ICERMEMELIDIR;
   cerceveyi uretici ekler.
6. **Uzunluk.** Iki ayri olcum, ikisi de bosluga gore kelime sayar:

   - `PROMPT.txt` toplami **1800 ile 2800** kelime arasinda olmalidir.
   - Rotanin kendi yazdigi bolumlerin toplami, yani
     `OPENING STATE` + `TIMELINE` + `VOICE` + `END STATE`, **600 ile 1000** kelime
     arasinda olmalidir.

   Gerekce: kanon 1190 kelime ve negatif blok 245 kelime, ikisi de sabit. Yani toplam
   bandi asil belirleyen sey rotanin uzunlugu. Ikinci olcum, asil kayma riskini
   dogrudan yakalar: yeni bir sehir yazan kisinin 200 kelimelik ici bos ya da 2000
   kelimelik dagilmis bir rota yazmasini engeller. Iki mevcut rota 855 ve 813
   kelimedir, yani bandin ortasindadir.

   UYARI: bu bant sistemin urettigi seye gore konuldu, modelde OLCULMEDI. 2300
   kelimelik bir promptun Veo/Sora uzerinde seyrelme yapip yapmadigi ayri bir A/B
   testinin isidir ve bu rockun kapsaminda degildir.
7. **Aciklama.** CAPTION bolumu tam 6 etiket icermeli, sonuncu bes tanesi sirasiyla
   `#WaterSlide #POVReels #CGIAdventure #ViralReels` ile bitmeli ve ilki `#MegaSlideFear`
   olmalidir. Ilk satir `You're` ile baslamalidir.
8. **Zorunlu alanlar.** Eksik baslik anahtari ya da eksik/bos bolum HATADIR.
9. **Belirlenimcilik.** Ayni girdi iki kez calistirildiginda byte olarak ayni cikti
   uretilmelidir.

10. **Slug bicimi.** `SLUG` yalnizca kucuk harf, rakam ve tire icerebilir, yani
    `^[a-z0-9]+(-[a-z0-9]+)*$`. Nokta, bosluk, egik cizgi, ters egik cizgi ve `..`
    HATADIR. Gerekce: `SLUG` dogrudan cikti dizini adi oluyor; `../..` iceren bir slug
    `out/` disina yaziyor. Bu bir varsayim degil, olculdu.

11. **Slug tekilligi.** Iki rota dosyasi ayni `SLUG` degerini kullanamaz. Gerekce: cikti
    yolu slug'dan turedigi icin ikinci rota birincinin ciktisini SESSIZCE eziyor. Bir
    rota dosyasini kopyalayip slug'i degistirmeyi unutmak, bu sistemde en olasi hata.

12. **Bos rota dizini.** `routes/` icinde islenebilir hicbir rota bulunamazsa bu bir
    HATADIR. "0 rota dogrulandi" diyip sifir kodla cikmak yanlis guven verir.

### Kabul kaniti (PROOF)

```
python build.py --check && python -m pytest -q
```

Ikisi de sifir kodla donmeli. `--check` iki rotayi da uretip dogrulamali.

### Testler (`tests/test_build.py`)

En az sunlari kapsamali, her biri gecici dizinde sentetik rota ile:

- saglam rota gecer
- BEATS icinde bosluk birakan rota patlar
- BEATS icinde cakisma olan rota patlar
- son aralik DURATION ile bitmeyen rota patlar
- eksik baslik anahtari patlar
- eksik bolum patlar
- BEATS icinde Liste B ifadesi (`slow motion`) gecen rota patlar
- ayni Liste B ifadesi sadece kanon ya da NEGATIVE bloglarinda geciyorsa rota GECER
- Liste A ifadesi (`next clip`) BEATS icinde gecerse patlar
- Liste A ifadesi NEGATIVE blogunda gecerse de patlar (Liste A istisnasizdir)
- OPENING STATE icinde `final frame` gecen rota patlar
- VOICE zamani DURATION disina tasan rota patlar
- CAPTION etiketleri eksik ya da yanlis sirada olan rota patlar
- rota bolumleri 600 kelimenin altinda kalan rota patlar
- rota bolumleri 1000 kelimeyi asan rota patlar
- ayni girdi iki kez uretildiginde ayni cikti
- alt cizgi ile baslayan `routes/_TEMPLATE.md` rota olarak islenmez
- iki rota ayni SLUG'i kullanirsa patlar (cikti sessizce ezilmez)
- SLUG icinde `../` gecen rota patlar VE `out/` disina hicbir sey yazilmaz
- SLUG icinde bosluk ya da buyuk harf gecen rota patlar
- `routes/` bos oldugunda patlar
- CRLF satir sonlu rota dosyasi sorunsuz islenir ve cikti LF kalir
- son beat DURATION'i asarsa patlar
- son beat `[17.5-20.00]` yazimi `DURATION: 20` ile esit sayilir ve gecer
- gercek iki rota (vegas, toronto) uretilir ve dogrulamadan gecer

## Kisitlar

- Python 3.12, sadece standart kutuphane. Yeni bagimlilik YOK. pytest zaten kurulu.
- Butun dosya okuma ve yazma islemleri UTF-8, `newline="\n"`.
- `canon/`, `routes/`, `reference/` iceriklerini DEGISTIRME. Sadece `build.py`,
  `tests/`, `out/` ve gerekiyorsa `README.md` yazilir.
- Metinlerde uzun tire kullanma.
