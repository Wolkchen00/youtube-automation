# Tersine muhendislik , milyonluk videolar

Tarih: 10 Eylul 2026. Kaynak: Ihsan'in verdigi dort referans video.
Izlenme sayilari Ihsan'dan (IG Insights), olcum bizim (ffmpeg + goz).

## 0. Onemli duzeltme: begeniden izlenme tahmin EDILEMEZ

Ben "en cok begenilen = en cok izlenen" diye tahmin etmistim. Gercek sayilar
bunu curuttu:

| Video | Begeni | Gercek izlenme | Begeni orani |
|---|---|---|---|
| DaP6llKhER_ | 65.000 | **11,9M** | %0,55 |
| DckORL2B8gx | 66.400 | **4,4M** | %1,51 |
| DcPo5RSBCzW | 26.900 | **734K** | %3,66 |
| Dcgzp2Oz4GG | 1.595 | **290K** | %0,55 |

En cok begenilen video 4,4M; 11,9M olan daha AZ begeni almis. Begeni orani
%0,55 ile %3,66 arasinda, 6,6 kat oynuyor. Bu kanalda begeniden izlenme
turetmek gecersizdir. Bundan sonra izlenme sayisi Ihsan'dan alinacak.

## 1. Olculen teknik yapi

| Video | Izlenme | Cozunurluk | Sure | Kesme | En uzun plan | LUFS | Kelime |
|---|---|---|---|---|---|---|---|
| DaP6llKhER_ | 11,9M | 720x1280 | 18,9 sn | 1 | 11,2 sn | -14,1 | 0 |
| DckORL2B8gx | 4,4M | 720x1280 | 15,2 sn | 0 | 15,2 sn | -14,5 | 0 |
| Dcgzp2Oz4GG | 290K | 720x1280 | 10,1 sn | 1 | 9,8 sn | -14,1 | 0 |
| DcPo5RSBCzW | 734K | **1280x720 YATAY** | **59,0 sn** | **15** | 10,2 sn | -14,1 | 0 |

Milyonluk ikisi: DIKEY, 15-19 saniye, 0-1 kesme, tek kamera pozisyonu.
734K olan bicimsel olarak farkli: yatay, 59 saniye, 15 kesme.

DUZELTME (Ihsan, 10 Eylul): bu videoyu "derleme, sablon degil" diye elemistim.
YANLISTI. Olcup IZLEMEDEN eledim; kareler cikarilinca gorundu. Onemi bicimde
degil, ICERIKTE: numarali melez listesi ("1. Camel X Rattle Snake",
"Lion X Octopus"...) ve DORUK NOKTASINDA INSAN SAHNEYE GIRIYOR , dev bir
balina-aslan melezi sudan cikip bir kadini kovaliyor, kadin on planda kaciyor.

Bu, elimizdeki TEK referans ki yaratik ile insani AYNI sahnede birlestiriyor.
Ihsan'in okumasi: yapimci kendini de sahneye koymus, karma bir video yaratmis,
tutmus, ve en cok izlenen videoya yol gostermis. Bizim aradigimiz birlesim bu.

Dordunde de SIFIR konusma. Ses -14,1 ila -14,5 LUFS.
NOT: bu bizim mevcut motor hedefimizle (-14 LUFS) AYNI. Ses tarafinda
degisiklik gerekmiyor.

Cozunurluk 720x1280, bizim 1080x1920'den DUSUK. Yani 4K ya da yuksek
cozunurluk bu isin sarti degil.

## 2. Anlati arki , IKI KANALDA DA AYNI

Uc asama, istisnasiz:

  1. GIZEM   : ozne kadrajda ama KIMLIGI GIZLI (basi onde, sadece bir uzvu
               gorunuyor, ya da siluet). Izleyici "bu ne?" diye sorar.
  2. IFSA    : ozne kendini acar. Tam gorunur olur.
  3. ODUL    : bir eylem olur (agzinda av, yurume, kameraya yaklasma).

DaP6llKhER_ (11,9M), kare kare:
  0-3 sn   : yaratik sahilde comelmis, BASI ONDE, sadece dikenli sirti gorunur
  6-9 sn   : basini kaldirir , aslan yuzu, yelesi tamamen balonbaligi dikeni
  15-19 sn : agzinda muren baligiyla kameraya dogru yurur

Dcgzp2Oz4GG (290K), kare kare:
  0-2,5 sn : adam helikopter kapisinda, sok ifadesi, disarida sadece dev bir BACAK
  5-7,5 sn : dev insansi tamamen gorunur, ormanda yuruyor, adam on planda izler

## 3. Iki ayri format, ayni ark

**A) YARATIK FORMATI** (motionsbysubh, 11,9M)
Insan YOK. Ozne melez bir hayvan. Iki gercek hayvanin imkansiz birlesimi
(aslan + balonbaligi dikeni; hyena + kaplumbaga kabugu; ahtapot + sempanze).
Gercekci fotograf dili, dogal gun isigi, gercek mekan (sahil, orman).

**B) TANIK FORMATI** (raselranaai, 290K) , IHSAN ICIN DOGRU SABLON
Sabit bir ERKEK karakter on planda, olayi YASAYAN taniktir.
Bir arac ya da bakis noktasindan cekilmis (helikopter kapisi), bu hem
kadraj cercevesi verir hem olcegi belli eder.
Arkada imkansiz olcekte bir sey. Karakterin SOK TEPKISI kadrajda gorunur.
Karakter KONUSMAZ.

Ihsan'in secimi: erkek karakter, kendi benzeri. Sablon B.

## 4. Olcek kontrasti , ortak motor

Her iki formatta da isi yapan sey OLCEK KONTRASTI:
- yaratik: bilinen bir hayvan, bilinmeyen bir doku/uzuvla
- tanik  : normal boyutta insan, agac boyunda bir varlik

Kontrast ILK KAREDE kismi, UCUNCU saniyede tam okunur.

## 5. Prompt iskeleti (turetildi, kopyalanmadi)

Bu promptlar yayinlanmadigi icin birebir alinamaz. Asagidaki iskelet
olcumden ve karelerden TURETILMISTIR.

Tanik formati icin, tek cekim, 15-19 saniye hedefi:

  KARAKTER  : <sabit karakter tarifi, referans gorselden>, kiyafet ORTAMA UYGUN
  KONUM     : <arac ya da bakis noktasi> icinde, kadrajin on planinda,
              govdesi ve yuzu gorunur, KAMERAYA BAKMAZ, disariya bakar
  TEPKI     : sok ve inanamama, agiz hafif acik, gozler buyumus
  ARKA PLAN : <gercek mekan>, dogal gun isigi, fotograf gercekciligi
  ANOMALI   : <imkansiz varlik>, <agac/bina> boyunda, ILK ANDA yalniz
              <tek bir uzvu> gorunur, sonra TAMAMI kadraja girer
  KAMERA    : tek sabit pozisyon, kesme YOK, hafif el titremesi
  SES       : konusma YOK, yalnız ortam sesi ve kisik gerilim muzigi

## 6. Bu kanalin KENDI dususu , tekrarlanmayacak hatalar

motionsbysubh son 20 gonderi medyani 325 begeni, en eski 40'in medyani 2.161.
6,6 kat dusus. Olculen farklar:

| | Isabetler | Yeni dusukler |
|---|---|---|
| sure | 15-19 sn | 24-32 sn |
| kesme | 0-1 | 1 ve 17 |

Uzayan sure ve montaja donus dususle ORTUSUYOR. Nedensellik kaniti degil,
ama iki uctaki fark net ve tek yonlu.

Gorsel fark (kareler): 4,4M'lik videoda yesil perde, ekip ve ON PLANDA
kamera monitorleri var, "bu sahte, iste nasil yapildi" ilk karede okunuyor.
Yeni dusuk videoda yesil perde ve monitor YOK, ekip arka planda puslu;
bir film karesi gibi duruyor, kamera arkasi gibi degil. Ifsa ilk karede
okunmuyor.

KURAL: odul ilk karede okunmali. Bu, eski unnatural-lab dersinin AYNISI.

## 7. Olculemedi

- Gercek retention ve izlenme suresi (hesaplar bizim degil, IG Insights yok)
- Bu videolarin hangi modelle uretildigi (filigran SYNTX.AI ve MOTIONSBYSUBH.AI,
  model adi yok)
- Birebir promptlar (yayinlanmamis)
- YouTube hesaplarinin ayni kisilere ait oldugu (isim benzerligi, dogrulanmadi)

## 8. UC REFERANSIN BIRLESIMI , bizim formatimiz

Uc video uc parcayi ayri ayri kanitliyor:

| Video | Izlenme | Ne kanitliyor |
|---|---|---|
| DaP6llKhER_ | 11,9M | YARATIK tek basina tasiyabiliyor; gizem->ifsa->odul arki |
| Dcgzp2Oz4GG | 290K | SABIT ERKEK KARAKTER tanik olarak ise yariyor |
| DcPo5RSBCzW | 734K | YARATIK + INSAN AYNI SAHNEDE, kovalama ile |

Bizim formatimiz ucunun birlesimi:
  - ozne: melez yaratik (olcek kontrasti, ilk karede kismi gorunur)
  - insan: Ihsan'in sabit karakteri, SAHNENIN ICINDE, tanik ya da kacan
  - ark : gizem -> ifsa -> odul (kovalama, yaklasma, av)
  - bicim: DIKEY 9:16, 15-19 saniye, 0-1 kesme, konusma YOK, -14 LUFS

Bicim milyonluk ikisinden alinir (dikey, kisa, tek plan), icerik ise
734K'lik videonun birlesiminden.
