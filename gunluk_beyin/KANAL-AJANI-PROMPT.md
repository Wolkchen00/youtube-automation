# Kanal ajani promptu , gunluk beyne baglanma

Bu metni her kanal ajaninin talimatlarina ekle (CLAUDE.md, sistem promptu, veya
kosunun basinda yapistir). `<KANAL>` yerine kanalin slug'ini yaz:
`unnatural-lab`, `event-horizon`, `flashpoints`, `aimagine-fear`.

---

## YAPISTIRILACAK METIN (asagisi)

### Bugunun fikrini uretmeden ONCE

Su dosyayi oku:

```
C:\Users\ihsan\Desktop\Antigravity\Projeler\Youtube\gunluk_beyin\kanallar\<KANAL>\BEYIN.md
```

Bu dosya HER GUN yeniden yaziliyor ve bu kanalin **kendi olculmus sonuclarindan**
turetiliyor. Sabit bir fikir havuzundan cekme. Fikri buradan cikan yone gore uret.

Dosyanin bes bolumu var, sunlari yap:

1. **DURUM** , kanalin nerede oldugunu gor. Medyan izlenme, en iyi ve en kotu video.
2. **BU KANALDA NE ISE YARIYOR** , bugunun fikrini sekillendiren asil bolum.
3. **GENEL ESIKLER** , kanala ozel veri yetersizse burasi gecerli.
4. **BUGUN ICIN YON** , somut oneriler. Fikrini bunlardan biriyle hizala.
5. **KACIN** , olculmus olarak kotu giden seyler. Bunlari YAPMA.

### Uc kural

**Kural 1 , "YETERSIZ VERI" yaziyorsa ona uy.**
2. ve 4. bolumlerde `YETERSIZ VERI (n=...)` yaziyorsa, o kanalda henuz kural
cikaracak kadar olcum yok demektir. O zaman 3. bolumdeki **genel esikleri** kullan.
Az veriden kural uydurma, beyin de uydurmuyor.

**Kural 2 , korelasyonu emir sayma.**
2. bolumdeki karsilastirmalarin yaninda `n=` ve "korelasyon, nedensellik degil"
notu var. Bunlar yon gosterir, kanun degildir. Beyin "kisa videolar daha iyi gitmis"
diyorsa bu bir hipotez; fikrini ona gore kur ama tek dogru sanma.

**Kural 3 , beyne rapor gondermene GEREK YOK.**
Yayinladiktan sonra hicbir sey yazma, hicbir yere kayit dusme. Beyin yayinlanan
videolari YouTube RSS'ten kendisi buluyor, olcuyor ve deftere ekliyor.
Tek yonlu bagimlilik, bozulacak el sikismasi yok.

### Fikri uretirken

- **Yeni fikir uret.** Stok listeden secme. Beyin bugun ne diyorsa ona gore kur.
- **Tekrar etme.** DURUM bolumundeki son videolarin basliklarina bak, ayni seyi yapma.
- **Olculebilir hedef koy.** "Daha iyi olsun" degil: "en uzun plan 4 saniyenin altinda",
  "ilk 1,5 saniyede ekran yazisi", "sure 15-21 saniye" gibi.
- Uretim boru hattinin kendi kurallari (kanon, negatifler, bible) HER ZAMAN oncelikli.
  Beyin onlarla celisirse boru hatti kazanir, celiskiyi de bir yere not et.

### BEYIN.md yoksa veya eskiyse

Dosya yoksa ya da tarihi bugunden eskiyse su komutu calistir:

```
cd C:\Users\ihsan\Desktop\Antigravity\Projeler\Youtube\gunluk_beyin
python beyin.py olc <KANAL>
python beyin.py topla <KANAL>
python beyin.py beyin <KANAL>
```

Ilki yeni yayinlari olcer, ikincisi izlenme sayilarini tazeler, ucuncusu beyni yazar.

---

## PROMPT METNI BITTI

## Sistemin nasil calistigi (ajanin bilmesine gerek yok, senin icin)

```
kanal ajani  ->  video yayinlar  ->  YouTube
                                        |
                                        v  (RSS, gunluk)
                    beyin.py olc  <-----+
                          |
                          v
                    defter.jsonl  (olcum + zaman serisi halinde sonuc)
                          |
                          v
                    beyin.py beyin
                          |
                          v
                      BEYIN.md  ---->  kanal ajani (ertesi gun)
```

Dongu tek yonlu. Kanal ajani beyni beslemiyor, beyin kendi topluyor.
Ajan bozulursa beyin yine calisir; beyin bozulursa ajan genel esiklerle devam eder.

## Kanal sluglari ve ID leri

| Slug | YouTube kanal ID | Klasor |
|---|---|---|
| `unnatural-lab` | `UC-Aht8VqAUMTUKYRQA3agYQ` | `sentinal_ihsan/unnatural-lab` |
| `event-horizon` | `UCVCRWrQYrIHW6csOsw9bDNw` | `galactic_experience/event-horizon` |
| `flashpoints` | `UCUdp0KLBh4EeeSgVbwS_DhA` | `shadowedhistory/flashpoints` |
| `aimagine-fear` | `UCCgbHTzYKYawUT6zEo0nlDg` | `AImagine-Fear` |

Not: `aimagine-fear` ile `next-stop` ayni YouTube kanalina basiyor.
`next-stop` su an `status: paused`. RSS ikisini birden dondurur, beyin ayirt
edemez; Fear icin olcum yaparken bunu akilda tut.
