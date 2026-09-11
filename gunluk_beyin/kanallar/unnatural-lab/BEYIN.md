# BEYIN , unnatural-lab

Uretim: 2026-09-11T03:52:25.795247+00:00
Kaynak: `/home/runner/work/youtube-automation/youtube-automation/gunluk_beyin/kanallar/unnatural-lab/defter.jsonl` (15 kayit)

Bu dosya HER GUN yeniden yazilir. Sabit fikir havuzu yoktur.
Sadece **24 saatten eski** videolar olculur, boylece izlenmenin
nerede oturdugu gorulur.

---

## 1. DURUM

- Olculen video: **15**
- Siralama olcusu: guncel izlenme , _24. saat olcumu henuz 0/15 kayitta var, yaslar farkli oldugu icin siralamayi dikkatli oku_
- Medyan izlenme: **1,157**
- Aralik: 82 ile 1,499 arasi

| | izlenme | tarih | baslik |
|---|---|---|---|
| EN IYI | 1,499 | 2026-09-04 | Something Is WRONG With This SOAP |
| EN KOTU | 82 | 2026-08-21 | I Found UNNATURAL PAGES... And They STARTED To R |

Son yayinlar (tekrar etme):
- 2026-09-08 , This NAPKIN Never ENDS!
- 2026-09-07 , This PLASTIC Bottle Turns To STONE!
- 2026-09-04 , Something Is WRONG With This SOAP
- 2026-09-02 , Something Is WRONG With This ICE CUBE
- 2026-08-28 , Something Is WRONG With This LEMON

### Teslim rejimi

- Guncel rejim: `21de6eb7`
- Rejim takibi bugun basladi; defterdeki 15 kaydin hicbirinde damga yok, hepsi birlikte sayiliyor.

### Yayinlanmayanlar

- **8 bolum YAYINLANMADI.** Bunlar YouTube'a cikmadigi icin yukaridaki olcumlere HIC girmiyor.
  - 1 tanesi URETILDI ama yayina giremedi; en cok ogrenilecek hatalar bunlardir.
  - 7 tanesi HIC URETILMEDI (butce kapisi, atlandi ya da reddedildi); kredi harcanmadi.

| part | uretim | durum | kod | eksik | deneme |
|---|---|---|---|---|---|
| 1 | uretilmedi | rejected | - | - | - |
| 2 | uretilmedi | rejected | - | - | - |
| 23 | uretilmedi | skipped | - | - | - |
| 24 | uretilmedi | skipped | - | - | - |
| 25 | uretilmedi | budget_exhausted | BUDGET_EXHAUSTED | kalan bölüm kredisi tamamlanma tabanına yetm | 0 |
| 26 | uretilmedi | budget_exhausted | BUDGET_EXHAUSTED | kalan bölüm kredisi tamamlanma tabanına yetm | 0 |
| 28 | uretilmedi | budget_exhausted | BUDGET_EXHAUSTED | kalan bölüm kredisi tamamlanma tabanına yetm | 1 |
| 30 | uretildi | needs_human | UNKNOWN | üretim nedeni bilinmiyor | 3 |

### Kural cikarimina GIRMEYEN bolumler

Bu bolumler EKSIK uretilmis (bir cekim dusmus). Yayinlanan
dosya kisa ve anlatimi otomatik kisaltilmis oldugu icin
olcumleri bir basari ornegi DEGILDIR; 2., 4. ve 5. bolumlerin
hicbirine girmiyorlar.

| video | bolum | sebep |
|---|---|---|
| `XzABOqtimVE` | 29 | dropped_shots=[1] |
| `dnsKT8eTWMo` | 27 | dropped_shots=[4] |
| `FuoWvZCKvf4` | 19 | sure orani 0.69 < 0.7 |

Kalan tam kayit: **12** (esik 15).

## 2. BU KANALDA NE ISE YARIYOR

**YETERSIZ VERI** (n=12, en az 15 gerekiyor; defterdeki 15 kaydin 3 tanesi eksik uretildigi icin sayilmadi). Bu kanala ozel kural cikarilamaz, asagidaki genel esikler kullanilmali.

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

**YETERSIZ VERI** (n=12, en az 15 gerekiyor; defterdeki 15 kaydin 3 tanesi eksik uretildigi icin sayilmadi). Bu kanala ozel kural cikarilamaz, asagidaki genel esikler kullanilmali.

## 5. KACIN

### Bu kanalda HIC UYGULANMAMIS esikler

Asagidaki esigi olculen videolarin **TAMAMI** ihlal ediyor.
Bu, esigin burada calismadigini GOSTERMEZ , boru hattinin o
esigi hic uygulamadigini gosterir. Esik gecerlidir; eksik olan
uygulamadir. Duzeltilene kadar bu boyutta karsilastirma yapma.

- **en uzun plan 4 sn tavani** , en iyi tam videoda deger: **5.6** (tum kayitlar ihlalde)

- **Ses seviyesi hedef disi**: `5PG5IbbivE0` -24.3 LUFS (hedef -16..-13)
- **Ses seviyesi hedef disi**: `HeP0V84NXfw` -23.2 LUFS (hedef -16..-13)
- **Ses seviyesi hedef disi**: `FuoWvZCKvf4` -22.3 LUFS (hedef -16..-13)
- _Ses seviyesi hedef disi: toplam 10 kayitta var, ilk 3 gosterildi._

## 6. BASLIK OZNESI

**HIPOTEZ** , baslikin KALIBI degil, OZNESI ayirt ediyor gorunuyor:
gozde canlanan bir SEY (yapi, eser, hayvan, marka) > OLAY > adiyla
anilan KISI. Kaynak: `shadowedhistory/REELYZE-RAPOR.md` , 29 bolumun tamami olculdu, 10 Eylul 2026.

Bu defterde HENUZ yeterli etiket yok (en az iki grupta 3'er
tam bolum gerekiyor), bu yuzden **sayi uretilmedi**.
Etiket eklemek icin: `kanallar/unnatural-lab/ozne.json`
(`{"<video_id>": "SEY" | "OLAY" | "KISI"}`).

Uygulama notu: kisi konusu ELENMEZ, basligin OZNESI degistirilir.
Ornek: "John Snow: The Father Of Epidemiology" yerine
"The Water Pump That Ended London's Cholera Outbreak".
