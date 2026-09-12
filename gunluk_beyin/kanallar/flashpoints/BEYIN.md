# BEYIN , flashpoints

Uretim: 2026-09-12T09:31:21.512705+00:00
Kaynak: `/home/runner/work/youtube-automation/youtube-automation/gunluk_beyin/kanallar/flashpoints/defter.jsonl` (15 kayit)

Bu dosya HER GUN yeniden yazilir. Sabit fikir havuzu yoktur.
Sadece **24 saatten eski** videolar olculur, boylece izlenmenin
nerede oturdugu gorulur.

---

## 1. DURUM

- Olculen video: **15**
- Siralama olcusu: guncel izlenme , _24. saat olcumu henuz 1/15 kayitta var, yaslar farkli oldugu icin siralamayi dikkatli oku_
- Medyan izlenme: **24**
- Aralik: 0 ile 1,179 arasi

| | izlenme | tarih | baslik |
|---|---|---|---|
| EN IYI | 1,179 | 2026-09-01 | Wrangel Mammoths: The Last Survivors |
| EN KOTU | 0 | 2026-08-24 | The Real Reason Cleopatra Was Closer To The Moon |

Son yayinlar (tekrar etme):
- 2026-09-09 , The Real Reason The Hundred Years' War Lasted 116 Years!
- 2026-09-08 , Henry "Box" Brown: The Unbreakable Man
- 2026-09-07 , The Real Reason America Invaded An Empty Island!
- 2026-09-06 , The Great Fire Of London: Fact Or Ancient Propaganda?
- 2026-09-05 , How Brooklyn Bridge Spanned The East River In 1883!

### Teslim rejimi

- Guncel rejim: `dbcdc34a`
- Rejim takibi bugun basladi; defterdeki 15 kaydin hicbirinde damga yok, hepsi birlikte sayiliyor.

### Yayinlanmayanlar

- Su anda tutulan bolum yok.
- Kusur defterinde gecmisten **1** olay kayitli (`kusur.jsonl`). series.json yalnizca ANLIK durumu tutar; kendini toparlayan hatalar orada iz birakmaz.

### Kural cikarimina GIRMEYEN bolumler

Bu bolumler EKSIK uretilmis (bir cekim dusmus). Yayinlanan
dosya kisa ve anlatimi otomatik kisaltilmis oldugu icin
olcumleri bir basari ornegi DEGILDIR; 2., 4. ve 5. bolumlerin
hicbirine girmiyorlar.

| video | bolum | sebep |
|---|---|---|
| `sO6q52tZaqg` | 30 | dropped_shots=[2] |
| `IkqbnHyj-Ms` | 27 | dropped_shots=[1] |
| `lMSL80iP3Cg` | 26 | dropped_shots=[2] |
| `f-TYvhYuvQg` | 24 | dropped_shots=[2] |
| `bhTaWCiP6c4` | 23 | dropped_shots=[1] |
| `nH-BdFphWRQ` | 22 | sure orani 0.46 < 0.7 |

Kalan tam kayit: **9** (esik 15).

## 2. BU KANALDA NE ISE YARIYOR

**YETERSIZ VERI** (n=9, en az 15 gerekiyor; defterdeki 15 kaydin 6 tanesi eksik uretildigi icin sayilmadi). Bu kanala ozel kural cikarilamaz, asagidaki genel esikler kullanilmali.

## 3. GENEL ESIKLER

Kanala ozel veri yetersizse veya celiskiliyse bunlar gecerli.

- Integrated loudness hedefi: **-16 ila -13 LUFS**
- True peak tavani: **-1,0 dBTP** (ustu platform yeniden kodlamasinda bozulur)
- En uzun tek plan: **4 saniyeyi asmasin**
- Kesme araligi: **1,5-3 saniye**, pattern interrupt her 5-7 saniyede
- Ilk 1,5 saniyede ekran yazisi: **3-7 kelime**, ust-orta ucte bir, dip %15 yasak
- Sure: nis ici olcumde **kisa kazaniyor** (0-7 sn en iyi 1,69x; 90+ sn en kotu 0,65x)
- Sinyal sirasi: skip rate (ilk 3 sn) > shares > likes > saves > reposts > comments
- **Yorum orani begeni oranindan daha ayirt edici** (begeni skor dilimleri arasi sabit)

## 4. BUGUN ICIN YON

**YETERSIZ VERI** (n=9, en az 15 gerekiyor; defterdeki 15 kaydin 6 tanesi eksik uretildigi icin sayilmadi). Bu kanala ozel kural cikarilamaz, asagidaki genel esikler kullanilmali.

## 5. KACIN

### Bu kanalda HIC UYGULANMAMIS esikler

Asagidaki esigi olculen videolarin **TAMAMI** ihlal ediyor.
Bu, esigin burada calismadigini GOSTERMEZ , boru hattinin o
esigi hic uygulamadigini gosterir. Esik gecerlidir; eksik olan
uygulamadir. Duzeltilene kadar bu boyutta karsilastirma yapma.

- **LUFS -16..-13 hedefi** , en iyi tam videoda deger: **-23.8** (tum kayitlar ihlalde)

- **Uzun statik plan**: `sO6q52tZaqg` en uzun plan 8.3 sn (tavan 4,0)
- **Uzun statik plan**: `to7T1zjXpaU` en uzun plan 9.6 sn (tavan 4,0)
- **Uzun statik plan**: `IkqbnHyj-Ms` en uzun plan 7.3 sn (tavan 4,0)
- _Uzun statik plan: toplam 8 kayitta var, ilk 3 gosterildi._

## 6. BASLIK OZNESI

**HIPOTEZ** , baslikin KALIBI degil, OZNESI ayirt ediyor gorunuyor:
gozde canlanan bir SEY (yapi, eser, hayvan, marka) > OLAY > adiyla
anilan KISI. Kaynak: `shadowedhistory/REELYZE-RAPOR.md` , 29 bolumun tamami olculdu, 10 Eylul 2026.

Bu defterdeki etiketli ve TAM bolumlerde:

| ozne | n | medyan izlenme |
|---|---|---|
| SEY | 3 | 105 |
| OLAY | 3 | 19 |
| KISI | 3 | 5 |

> Etiketler ELLE konuldu ve medyan ayni etiketlerden hesaplandi.
> Bu bir KESIF DEGIL, kayitli bir HIPOTEZIN bu defterdeki
> gorunumudur. Korelasyon, nedensellik degil.

Uygulama notu: kisi konusu ELENMEZ, basligin OZNESI degistirilir.
Ornek: "John Snow: The Father Of Epidemiology" yerine
"The Water Pump That Ended London's Cholera Outbreak".
