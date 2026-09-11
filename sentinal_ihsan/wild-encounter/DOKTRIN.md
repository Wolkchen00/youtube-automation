# Wild Encounter , seri doktrini

Kurulus: 10 Eylul 2026. Kanal sifirdan yazildi, onceki sekiz seri arsivde
(`Antigravity/_arsiv/sentinal_ihsan_2026-09-10`).

Bu belgedeki her sayi OLCULMUSTUR. Kaynak: `sentinal_ihsan/TERSINE-MUHENDISLIK.md`.
Izlenme sayilari Ihsan'in IG Insights'indan, teknik olcumler bizim (yt-dlp + ffmpeg).

## GUNCEL FORMAT (12 Eylul 2026'dan itibaren gecerli)

Bu bolum asagidaki "Tek cumle", "Degismez kurallar" ve "Neye DOKUNMA"
bolumlerinin YERINE gecer. Onlar 10 Eylul'un dis mekan / melez yaratik
formatini anlatir; o format olculerek terk edildi (asagidaki basarisizlik
kayitlari). Kayitlar ders olarak duruyor.

### Tek cumle

Bir film setinde dev, gercekci bir yaratik Ihsan'i agzina alir; ekip
cenesini elleriyle acar ve Ihsan yara almadan cikar. Yaratigin bir prop
oldugu son vurusta anlasilir.

### Kurallar

1. ANLATIM YOK, MUZIK YOK. Ses setin kendi sesidir: ortam, su, yaratik
   mekanizmasi, ekip hareketi, alkis. Diegetik ses kisilmez. Mastering
   muziksiz govde uzerinde -14 LUFS / -1 dBTP'ye yapilir. (11 Eylul, ep05
   sonrasi Ihsan karari.)
2. UC VURUS, SIRASI DEGISMEZ, TEK SET: tehdit, agza alinma, ekibin ceneyi
   acmasi ve cikis. Vurus metninin TEK KAYNAGI
   series.json auto_replenish.shot_plan; her cekim promptu o metinle baslar.
3. QC NOTU VURUS TARIF ETMEZ, prompttaki "SHOT N," paragrafina bakar.
   Sebep: kural degisip QC notu bayat kalinca dogru video yanlis sebeple
   reddedildi; 11 Eylul'de uc kez, 483 kredi.
4. art_style HER cekim promptunun basina eklenir (series/shots.py). Formati
   degistiren her karar art_style'i ayni anda degistirir.
5. KURULMUS DEKOR, CIPLAK YESIL PERDE DEGIL. On planda gercek set malzemesi
   (yaprak, kaya, su, sis), arkada yesil perde, kenarda ekip, en onde kamera
   operatorlerinin sirti. (DdEArj4BMrV dersi.)
6. GIRIS AGIZDAN, CIKIS EKIBIN ELLERIYLE. Prop oldugunu kanitlayan sey alkis
   degil, ellerin dekorun uzerinde olmasi.
7. TEK YARATIK, DONUSUM YOK. Iki govde birlestirilemiyor (olculdu).
8. OLCEK: yaratik buyuk ve yakin, kadrajin buyuk kismini doldurur.
9. TEK IHSAN, konusmaz, kameraya bakmaz. Yuz capasi character_id; kiyafet
   sete gore degisir.
10. SURE: 3 x 8 sn, duration_band [12, 26]. ep05 22,7 sn cikti.
11. EKRANA YAZI YOK. GUVENLIK: kan ve yaralanma yok.

## Tek cumle (ESKI FORMAT, 10 Eylul, artik gecerli degil)

Bir adam gercek bir dogal mekanda, iki gercek hayvanin imkansiz birlesimi olan
TEK bir yaratikla karsilasir, ve zar zor kurtulur. Hicbir sey aciklanmaz.

## Neden bu format

Referans olcumu (dort video):

| Video | Izlenme | Sure | Kesme | Konusma | LUFS |
|---|---|---|---|---|---|
| DaP6llKhER_ | 11,9M | 18,9 sn | 1 | 0 kelime | -14,1 |
| DckORL2B8gx | 4,4M | 15,2 sn | 0 | 0 kelime | -14,5 |
| DcPo5RSBCzW | 734K | 59,0 sn | 15 | 0 kelime | -14,1 |
| Dcgzp2Oz4GG | 290K | 10,1 sn | 1 | 0 kelime | -14,1 |

Ucu birden ayri bir parcayi kanitliyor:
- 11,9M : YARATIK tek basina tasiyabiliyor
- 290K  : SABIT ERKEK KARAKTER tanik olarak ise yariyor
- 734K  : YARATIK ve INSAN AYNI SAHNEDE, kovalama ile

Bizim formatimiz ucunun birlesimidir.

## Degismez kurallar (ESKI FORMAT, 10 Eylul, artik gecerli degil)

1. **ANLATIM YOKTUR.** Dort referansin DORDUNDE de desifre sifir kelime.
   Voiceover yok, konusma yok, karakter agzini konusur gibi oynatmaz.
   Ses yalniz ortam sesi ve kisik muzik yatagidir.

2. **TEK YARATIK, IKI TANIDIK HAYVANIN BIRLESIMI.** Izleyicinin tanidigi iki
   hayvan. Egzotik ve bilinmeyen tur secilmez, cunku ilk karede okunmaz.
   Yaratik gercek bir hayvan gibi davranir, fantastik yaratik gibi degil.

3. **UC ASAMALI ARK, SIRASI DEGISMEZ.**
   - GIZEM : yaratik kadrajda ama KISMEN GIZLI. Izleyici bir terslik oldugunu
     anlar, ne oldugunu anlamaz.
   - IFSA  : yaratik tamamen gorunur olur.
   - ODUL  : bir eylem olur (hucum, kovalama, agzinda av).
   Shot 1 yaratigin tamamini GOSTEREMEZ. Gosterirse ifsa erken harcanir.

4. **ADAM SAHNENIN ICINDE, TANIK ROLUNDE.** Yuzu ve govdesi net gorunur,
   kameraya degil yaratiga bakar. Tepkisi fizikseldir. Kadrajda TEK bir adam
   olur; ikinci kopya hatadir.

5. **KIYAFET MEKANA GORE DEGISIR, ADAM DEGISMEZ.** Kiyafet degisimi hata
   DEGILDIR ve QC'de hata sayilmaz. Degismeyen sey yuz, sakal, sac ve govdedir.
   Kimlik capasi: `character_id` ve referans gorsel.

6. **SURE TAVANI SERT: 16 saniye (2 x 8 sn), 1 kesme.**
   Olculdu: bu hesabin isabetleri 15-19 saniye ve 0-1 kesme. Ayni hesabin
   DUSEN videolari 24-32 saniyeye ve 17 kesmeye cikmisti, medyani 2.161'den
   325 begeniye dustu. Uzatmak olcumle iliskilendirilmis tek gerileme desenidir.

7. **OLCEK KONTRASTI isi yapan seydir.** Ya yaratik adama gore devasa olur,
   ya tanidik bir hayvan tanimadigin bir dokuya sahip olur.

8. **MEKAN GERCEK ve DOGAL.** Sahil, orman nehri, col, kayalik kiyi.
   Dogal gun isigi, elde cekim hissi. Stilize renk derecelendirmesi yok.

9. **EKRANA YAZI YOK.** Cekim promptu altyazi, baslik ya da grafik tarif etmez.

10. **GUVENLIK.** Kan, yaralanma, hayvana eziyet, insan olumu yok.
    Gerilim kovalamacadan gelir, siddetten degil.

## Neye DOKUNMA (ESKI FORMAT, 10 Eylul, artik gecerli degil)

- Ses hedefi -14 LUFS. Referanslar -14,1 ila -14,5 olculdu, motorumuz zaten
  ayni hedefte. Degistirme.
- 2 x 8 saniye yapisi. Referansin 18,9 sn / 1 kesme yapisinin motordaki tam
  karsiligi budur.
- `duration_band` tavani 20 saniye. Kural 6'nin makinedeki karsiligi.

## Bilinen acik maddeler

- `environments` icinde referans gorsel YOK (`ref_image_url: null`).
  Bolumler arasi mekan tutarliligi bundan zayif kalir; ilk bolumlerden sonra
  referans gorsel uretilip baglanmali.
- Bu format YouTube'da KANITLANMADI. Iki referans hesabin da YouTube kanali
  olu (92 ve 29 abone, medyan 49 ve 422). Format Instagram'da tuttu.
  Ana hedef YouTube oldugu icin bu bir risktir ve ilk bolumlerle olculecektir.
- Retention olculemedi (hesaplar bizim degil).

## Bolum 1 uretiminden ogrenilen , 315 kredi odendi

Ilk uretim denemesi QC'den UC KEZ dondu. Red sebepleri kayda deger:

1. "ham native seste istenmeyen konusma var"
2. "izleyici acilis karesinde imkansiz ozelligi okuyamiyor"
3. ayni (2)

### Ders 1: KIMLIGI gizle, ANOMALIYI DEGIL

Ilk cekim 1 promptum yaratigi fazla saklamisti: "sadece kabuk ve kiskac
kopukten cikiyor". O kadraj sadece bir YENGEC gibi okunuyor, ortada hicbir
tuhaflik yok, dolayisiyla imkansiz ozellik acilis karesinde OKUNMUYOR.

Referansa donup bakildiginda hata gorundu: 11,9M'lik videonun ilk karesinde
ASLAN YELESI ve BALONBALIGI DIKENLERI BIRLIKTE gorunuyor. Yani anomali
ilk kareden itibaren okunuyor; gizlenen sey yaratigin KIMLIGI ve YUZU.

Kural: cekim 1'de melezin IKI YARISI da ayni govdede gorunur olmali
(kurk + kabuk), gizlenen tek sey yuz ve tam siluettir.

Bu ayni zamanda bible'daki iki kuralin celiskisini cozer:
`require_first_frame: true` ile "cekim 1 gizem olmali" kurali ancak boyle
birlikte var olabilir.

### Ders 2: sesi OLUMLU cumleyle tarif et

"Konusma yok" demek difuzyon modellerinde tersine calisabiliyor
(bkz. bilinen tuzak: olumsuz cumle nesneyi cizdirir). Bunun yerine promptun
sonuna ne OLDUGU yazilir: "Ambient sound only: waves, wind and running water."

### Maliyet notu

Cekim basina deneme 105 kredi (~0,53 dolar). Uc deneme = 315 kredi.
Bu, tahmin ettigim bolum basi ~600 kredinin cok altinda; QC erken durdurdugu
icin tam bolum maliyeti olusmadi.

## OLCULEN BASARISIZLIK: iki govde birlestirilemiyor (2026-09-11)

Iki bagimsiz uretim denemesi, giderek daha acik promptlarla:

1. "iki hayvan kadrajda, birlesirler, tek hayvan ortaya cikar"
   -> timsah filin altinda kayboldu, toz dagilinca SADE BIR FIL kaldi.
2. Bitis durumu ACIKCA tarif edildi (fil basi + timsah plakalari + timsah
   kuyrugu, ayni govdede, son anda birlikte gorunur)
   -> yine olmadi: fil timsahin uzerinden gecti, sonda iki AYRI hayvan kaldi.

Zincir karesi denetcisi ikisini de dogru yakaladi ve metin-tek uretime
dusmeyi REDDETTI. Kapi calisti, para korundu (toplam 168 kredi).

SONUC: bu model iki ayri hayvani TEK GOVDEDE birlestirmiyor. Onlari iki ayri
hayvan olarak canlandiriyor, cunku promptta iki ayri hayvan var.

## REFERANSIN GERCEKTE YAPTIGI SEY (2 fps, 118 kare incelendi)

Acilis segmentinde EKRANDA TEK HAYVAN VAR: deve. Cingirakli yilan AYRI BIR
HAYVAN OLARAK HIC GOSTERILMIYOR; adi yalniz altyazida geciyor. Deve kivrilip
DONUSUYOR ve yilan derisini KAZANIYOR.

Yani mekanizma "iki govdenin birlesmesi" DEGIL, "tek oznenin donusumu".
Tek ozneli donusum difuzyon icin cok daha kolaydir: doku ve siluet degisimi,
govde kaynastirma degil.

BENIM HATAM: iki hayvani kadraja koyup birlestirmelerini istedim. Model de
onlari iki ayri hayvan gibi davrandirdi, cunku oyleler.

DOGRU KURULUM: kadrajda TEK hayvan olur; o hayvan, ikinci hayvanin dokusunu,
zirhini ya da uzvunu KAZANARAK donusur. Ikinci hayvan yalnizca BASLIKTA ve
kazanilan ozellikte vardir.

## A TESTININ SONUCU: tek ozneli donusum CALISIYOR (2026-09-11, part03)

Kadrajda TEK fil, timsah yalniz baslikta ve kazanilan zirhta.
Sonuc kareleri: 0-1,5 sn sade fil, 2-2,5 sn toz patlamasi, 3 sn sonrasi
filin SIRTINDA timsah plakalari ve ARKASINDA timsah kuyrugu.

KANIT: donusum gerceklesti. Iki govdeyi birlestirmek IMKANSIZ, tek ozneyi
donusturmek MUMKUN. Fark, promptta kac hayvan oldugudur.

IKI CEKINCE, ikisi de dogru:

1. QC bunu YANLIS SEBEPLE reddetti: bible'daki QC notu hala "cekim 1 IKI
   hayvanla baslar" diyordu. Promptu tek ozneye cevirdim ama kurali
   guncellemedim. Kapi dogru calisti, TALIMAT bayatti. Kural degistirilirken
   QC notu AYNI ANDA guncellenmeli; bu oturumda ayni hata uc kez tekrarlandi
   (require_first_frame, require_continuity, ve simdi iki-hayvan kurali).

2. Etki REFERANSA GORE ZAYIF. Referansta deve bastan asagi yilan derisine
   burunuyor; bizde zirh yalniz sirtta ve kuyrukta okunuyor. Donusum olmasi
   ile ETKILEYICI olmasi ayri seyler. Daha sert prompt gerekir: govdenin
   TAMAMINI kaplayan doku, ve zirhin kadrajin buyuk kismini doldurmasi.

## UCUNCU REFERANS: DdEArj4BMrV , ORTAM DERSI (2026-09-11)

Olcum: 720x1280, 15,18 sn, SIFIR kesme, -15,2 LUFS, 0 kelime. 30 kare, 2 fps.

Yapi, Ihsan'in tarif ettiginin birebir kaniti:
  tehdit -> IceRI ALINMA -> ifsa
  Dev timsah kafasi arkada, kadin onde; agiz aciliyor; KADIN AGZIN ICINDE;
  yakin plan; EKIP KAFAYI ELLERIYLE ITIYOR; kadin agizdan cikiyor.

ORTAM FARKI, Ihsan'in ovdugu sey ve bizim ep04'te eksik olani:

| | Referans | Bizim ep04 |
|---|---|---|
| Set | KURULMUS ORMAN DEKORU: yapraklar, sarmasik, sis | Ciplak yesil perde |
| Isik | Tepedeki studyo lambalari yapraklar arasindan, atmosferik | Duz uc nokta |
| Giris yolu | Yaratigin AGZI | Govdedeki kapak |
| Ekip | Dekora ELLERIYLE DOKUNUYOR | Yalnizca alkisliyor |

UC DERS:
1. Ciplak yesil perde yerine KURULMUS DEKOR kullan. Yesil perde arkada
   gorunebilir ama on planda gercek set malzemesi (yaprak, sarmasik, kaya,
   sis) olmali. Ortam zenginligi izleyiciyi tutan sey.
2. Iceri giris KAPAKTAN degil AGIZDAN olmali. Cok daha icgudusel ve
   "yiyormus gibi" okunuyor, ki Ihsan'in istedigi tam buydu.
3. Ekip dekora FIZIKSEL OLARAK DOKUNMALI. Prop oldugunu kanitlayan sey
   alkis degil, ellerin dekorun uzerinde olmasi.

NOT: referansin true peak degeri +0,6 dBFS, yani KIRPIYOR. Bizim -1,0
hedefimiz daha dogru; bu kalemde onlari taklit etme.

## SES KARARI, 11 Eylul 2026 (ep06'dan itibaren)

Ihsan ep05'i izledi. Goruntu onaylandi, **ses reddedildi**.

Karar: **arka plan muzigi kalkiyor.** Yerine sahnenin kendi sesi: plato
ambiyansi, su, ahtapotun saldiri sesi, ekip hareketi. Onun sozleriyle
"ortam seslerini yok etmeyelim" , diegetik ses kisilmeyecek, sadece muzik
yatagi cikacak.

Olculen gerekce, tahmin degil:
- ep05 muzikli master: -14,0 LUFS / -1,7 dBTP, LRA 8,9
- ep05 muziksiz gövde (`ep05.mp4`): **-17,6 LUFS**, LRA 6,3

Yani muziksiz dosyayi oldugu gibi yayinlamak platform hedefinin 3,6 LU altinda
kalir ve video sessiz duyulur. **Dosya takasi bir cozum DEGILDIR.** Dogru yol:
muzik adimini atla, mastering'i muziksiz gövde uzerinde kostur.

Referans dayanagi: raselranaai ve motionsbysubh.ai'nin olctugumuz tutan
videolarinin hicbirinde muzik yatagi yok. Sahte-kamera-arkasi formatinda muzik
"gercek cekim" hissini oldurup videoyu reklama benzetiyor.

ep05 muzikli haliyle yayinlandi, cunku etkilesim testi bekletilmedi.
