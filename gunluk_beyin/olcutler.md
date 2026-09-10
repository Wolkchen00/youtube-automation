# Olcutler, esikler ve kiyas degerleri

Kaynak: getreelyze.com metodolojisi + 1.204 aykiri videonun kendi olcumumuz
(10 Eylul 2026). Tam dosya: `Projeler/Reelyze_Arastirma/REELYZE-DOSYASI.md`

---

## 1. Sert teknik esikler (dogrudan uygulanabilir)

| Olcum | Hedef | Not |
|---|---|---|
| Integrated loudness | **-16 ila -13 LUFS** | sosyal medya hedefi |
| True peak | **<= -1,0 dBTP** | ustu platform yeniden kodlamasinda bozulma yapar |
| LRA | 4 civari | ses agirlikli kisa video icin normal |
| En uzun tek plan | **<= 4 sn** | asiyorsa kesme, zoom veya yazi gerekiyor |
| Kesme araligi | 1,5-3 sn | konusan kafa icin |
| Pattern interrupt | her 5-7 sn | ve her dusus ucurumundan 1-2 sn once |
| Kesme tabani | saniyede birden hizli olmasin | kafa karistiriyor |
| Jump cut | 0,3 sn'den uzun duraklamalari sil | |

**Uyari:** kesme sayisi `scene=0.3` esigiyle olculuyor ve su spreyi, flash, hizli
kamera hareketi kesme sanilabiliyor. Su/hiz iceren icerikte kareleri gozle dogrula.

**Uyari 2:** kor "4 saniye tavani" kurali her kanala uymaz. Olctugumuz en iyi kanalin
(`sentinal_ihsan`) en uzun plani 17,85 saniye ve filonun en iyisi. Anomalinin kendisi
pattern interrupt gorevi goruyorsa kesme gerekmez.

## 2. Ilk 3 saniye, kare kare

- **0,0 sn:** ilk karede hareket veya bir yuz. Statik acilis en yaygin kaydirma tetigi.
  Ekran yazisi HEMEN gorunmeli, fade-in yok.
- **1,0 sn:** odul/payoff ifadesi ekranda yazili olmali (sessiz izleyici icin).
- **3,0 sn:** izleyici kalma karari verir. Burada olculen skip rate en agirlikli sinyal.

Ekran yazisi: **3-7 kelime** (bazi kaynakta 5-9), tek satir, buyuk, yuksek kontrast,
arkasinda opak bar veya kalin stroke. Yerlesim **ust-orta ucte bir**.
**Dip %15 kullanilamaz** (kullanici adi, aciklama, UI dugmeleri).
Ses ve yazi ayni seyi FARKLI kelimelerle soylemeli, birebir kopya olmamali.

## 3. Sinyal siralamasi (kanonik)

```
skip rate (ilk 3 sn)  >  shares  >  likes  >  saves  >  reposts  >  comments
```
Yukaridan asagi optimize et. "Shares are downstream of retention: ilk 3 saniyede
%70 kaydiriyorsa paylasim sayin kalan %30 ile sinirli."

**AMA kendi olcumumuz sunu ekliyor:** begeni orani ayirt etmiyor (skor dilimleri
arasinda sabit %5,4-5,8), **yorum orani ayirt ediyor** (%0,038 -> %0,058, %53 artis).
Kendi olcumunde begeniyi degil yorumu izle.

## 4. Retention egrisi, dort sekil

| Sekil | Gorunum | Sebep | Cozum |
|---|---|---|---|
| **Cliff** | ilk 1-3 sn dik dusus | zayif kanca | ilk cumleyi ve ilk kareyi degistir |
| **Slide** | bastan sona duz inis | duz tempo, artmayan odul | tempoyu hizlandir, odulu yukselt |
| **Mid-clip cliff** | tutuyor sonra belirli noktada cakiliyor | olu an, gecikmis odul, konu sapmasi | o zaman damgasini kes |
| **Flat tail / uptick** | sonda duzlesiyor veya yukseliyor | dongu / tekrar izleme | **iyi**, koru |

## 5. Tamamlanma orani

`completion rate = ortalama izlenme suresi / video uzunlugu`

| Uzunluk | Beklenti |
|---|---|
| < 7 sn | cogu izleyici sona ulasmali |
| 7-15 sn | buyuk kismi bitirmeli |
| 15-30 sn | daha kucuk bir kisim |
| 30-60 sn | daha az, ortalama izlenme suresi daha faydali |
| 60-90 sn | sadece azinlik bitirir, normal |

**%100 ustu = dongu/tekrar izleme, en guclu sinyallerden biri.**
15 sn altinda kusursuz dongu efektif izlenme suresini ikiye katlayabilir.

Teshis: yuksek watch time + dusuk completion = cok uzun.
Dusuk watch time + yuksek completion = iyi ama cok kisa, uzatilabilir.

## 6. Sure , DIKKATLI OKU

Reelyze rehberleri "7-21 saniye tatli nokta" diyor.
1.204 aykiri videoyu **nis medyanina normalize ederek** olctuk:

| Kova | Nis medyanina gore medyan kat |
|---|---|
| 0-7 sn | **1,69** |
| 7-15 sn | 1,34 |
| 15-21 sn | 1,36 |
| 21-30 sn | 1,02 |
| 30-45 sn | 0,85 |
| 45-60 sn | 0,89 |
| 60-90 sn | 0,94 |
| 90-180 sn | **0,65** |

Nis ici sure/izlenme sira korelasyonu: **medyan -0,216**, 51 nisin 37'si negatif.
**Kisa kazaniyor.**

> Normalize etmeden bakarsan TERS sonuc cikiyor (uzun video daha iyi gorunuyor).
> Simpson paradoksu: dusuk medyanli niste az izlenme bile yuksek skor uretiyor.
> Nis ici normalize etmeden sure yorumu YAPMA.

Icerik tipine gore onerilen: kanca odakli/trend 7-15 sn, ipucu/liste 15-30 sn,
hikaye/vaka 21-34 sn, derin ogretici 34-60 sn, konusan kafa 12-25 sn.

## 7. Senaryo iskeleti

```
HOOK      0-3 sn     tek satir + ekran yazisi, 8 kelimeden az
PROMISE   3-6 sn     "Here are [sayi] [sey] that [sonuc]"
VALUE     6-25 sn    2-4 siki vurus, her birinde yeni gorsel
LOOP      son 2-3 sn kancayi cozer veya videoyu bastan baslatir
```
20-40 sn video icin **55-90 konusulan kelime**. 6. sinif okuma seviyesi.
Ortada bir re-hook. Odulu one al. Icinde tek bir acikca paylasilabilir cumle olsun.

## 8. Kanca kaliplari (yedi tane)

1. Aykiri iddia  2. Once sonuc  3. Dogrudan hedefleme  4. Acik dongu
5. Gorsel kanit (ilk karede)  6. Aksiyonun ortasindan basla  7. Negatif kanca

**Kural: kanca KATEGORI degil PROBLEM adlandirmali.**
"the algorithm" / "5 SEO tips" = kotu. "why your Reels die at 3 seconds" = iyi.

Ek gozlem (kendi olcumumuz): **taninabilirlik onemli.** `shadowedhistory` kanalinda
Brooklyn Bridge (509) ve mamut (1.179) tuttu; Tanganyika ve Cleopatra-ceviri (6-22)
tutmadi. Izleyici ismi bilmiyorsa ilk 3 saniyede "bu benim icin mi" sorusuna cevap yok.

## 9. Paylasim

Kiyas: cogu video izleyicinin **%0,5-1**'i paylasir. Iyi **%2-3**. Viral **%4+**.

Bes tetik: Kimlik, Fayda, Duygu, Statu, Sohbet.

## 10. Yayin sikligi

Buyume modu haftada 5-7. Koruma modu 3-5. Yeni hesap (1000 alti) 4-6.
Genel optimum 4-7. Gunde birden fazla cezalandirilmiyor ama nadiren fayda veriyor.

## 11. Kiyas degerleri (9.770 Instagram gonderisi / 222 hesap)

| Takipci bandi | Medyan izlenme | Iyi (p75) | Ust %10 | Medyan kat |
|---|---|---|---|---|
| < 1.000 | 478 | 1.573 | 3.331 | **2,26x** |
| 1.000-10.000 | 2.036 | 4.651 | 13.996 | 0,61x |
| 10.000-100.000 | 6.419 | 25.564 | 131.563 | 0,29x |
| 100.000+ | 141.075 | 329.138 | 936.370 | 0,33x |

Kac video takipci sayisinin kac katina ulasiyor:
1x+ %38,7 | 2x+ %25,5 | 3x+ %19,7 | 5x+ %13,2 | **10x+ %7,7 (viral tanimi)** | 20x+ %4,9

**Reels'lerin sadece %38,7'si kendi takipci sayisi kadar bile izlenme aliyor.**

Seed havuzu: Instagram yeni videoyu 200-500 hesaba test ediyor. Karar genelde
ilk 30-60 dakikada. Basarisiz demeden once 24-48 saat bekle.

## 12. Yayin oncesi 8 maddelik skor karti (her madde 1 puan)

1. **Ilk kare:** ilk yarim saniyede hareket, yuz veya pattern interrupt? Statik = 0
2. **Acilis cumlesi:** izleyicinin PROBLEMINI mi adlandiriyor (1), KONUYU mu (0)
3. **Ekran yazisi:** 7 kelimenin altinda okunakli kanca, 1. saniyeden once ekranda
4. **Vaat:** 3. saniyede izleyici kalirsa ne alacagini biliyor mu? Tek cumleyle diyemiyorsan 0
5. **Tempo:** ilk 10 saniyede kesme sayisi. Konusan kafada 2'den az = 0
6. **Ses:** konusma muzigin uzerinde net VE ilk cumle hemen basliyor? Ikisi de = 1
7. **Aciklama metni:** videoda olmayan bir sey katiyor VE tek net eylemle bitiyor?
8. **Odul:** videoyu sonuna kadar kendin izle. Kaydirmak istedigin an = retention tavanin

**6+ = yayinla. 4-5 = en dusuk maddeyi duzelt. 3 ve alti = kancayi bastan yaz.**

Dusuk skorda duzeltme sirasi: kancayi problem adlandiracak sekilde yaz > ilk saniyeyi
tamamen kes > kanca satirini ilk kareye yazi olarak koy > ilk kesmeyi one al >
odulu one tasi > yeniden puanla. Hala 5 altiysa sorun kurgu degil **fikir**.

**Not:** 1, 3, 5, 8 maddeleri makinece guvenilir olculemiyor (kare farki niyeti
kanitlamaz; OCR yoksa bilinmez; sahne esigi yaniltir). Bunlari insan yargisi olarak
isle, sayisal puana cevirme.
