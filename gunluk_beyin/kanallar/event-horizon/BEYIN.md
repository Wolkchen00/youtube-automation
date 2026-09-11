# BEYIN , event-horizon

Uretim: 2026-09-11T07:41:12.796284+00:00
Kaynak: `/home/runner/work/youtube-automation/youtube-automation/gunluk_beyin/kanallar/event-horizon/defter.jsonl` (15 kayit)

Bu dosya HER GUN yeniden yazilir. Sabit fikir havuzu yoktur.
Sadece **24 saatten eski** videolar olculur, boylece izlenmenin
nerede oturdugu gorulur.

---

## 1. DURUM

- Olculen video: **15**
- Siralama olcusu: guncel izlenme , _24. saat olcumu henuz 2/15 kayitta var, yaslar farkli oldugu icin siralamayi dikkatli oku_
- Medyan izlenme: **104**
- Aralik: 23 ile 393 arasi

| | izlenme | tarih | baslik |
|---|---|---|---|
| EN IYI | 393 | 2026-09-05 | The Universe's SLOWEST Particle: Photon's Journe |
| EN KOTU | 23 | 2026-09-10 | WASP-12b: Planet Being DEVOURED |

Son yayinlar (tekrar etme):
- 2026-09-10 , WASP-12b: Planet Being DEVOURED
- 2026-09-09 , What If Earth Had Rings? Sky BLADES
- 2026-09-08 , Flying to Alpha Centauri: A 5 MILLION Year Trip
- 2026-09-07 , Olympus Mons: Towers Over Everest
- 2026-09-06 , KELT-9b: Hotter Than MOST Stars

### Teslim rejimi

- Guncel rejim: `c623ea0f`
- Rejim takibi bugun basladi; defterdeki 15 kaydin hicbirinde damga yok, hepsi birlikte sayiliyor.

### Yayinlanmayanlar

- Su anda tutulan bolum yok.

### Kural cikarimina GIRMEYEN bolumler

Bu bolumler EKSIK uretilmis (bir cekim dusmus). Yayinlanan
dosya kisa ve anlatimi otomatik kisaltilmis oldugu icin
olcumleri bir basari ornegi DEGILDIR; 2., 4. ve 5. bolumlerin
hicbirine girmiyorlar.

| video | bolum | sebep |
|---|---|---|
| `2Cs_MsKcImA` | 29 | dropped_shots=[3] |
| `VS8yd--FZsg` | 27 | dropped_shots=[3] |
| `DFIc-OD3ASw` | 26 | dropped_shots=[2] |
| `TVXhCHS5vUg` | 24 | sure orani 0.61 < 0.7 |

Kalan tam kayit: **11** (esik 15).

## 2. BU KANALDA NE ISE YARIYOR

**YETERSIZ VERI** (n=11, en az 15 gerekiyor; defterdeki 15 kaydin 4 tanesi eksik uretildigi icin sayilmadi). Bu kanala ozel kural cikarilamaz, asagidaki genel esikler kullanilmali.

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

**YETERSIZ VERI** (n=11, en az 15 gerekiyor; defterdeki 15 kaydin 4 tanesi eksik uretildigi icin sayilmadi). Bu kanala ozel kural cikarilamaz, asagidaki genel esikler kullanilmali.

## 5. KACIN

### Bu kanalda HIC UYGULANMAMIS esikler

Asagidaki esigi olculen videolarin **TAMAMI** ihlal ediyor.
Bu, esigin burada calismadigini GOSTERMEZ , boru hattinin o
esigi hic uygulamadigini gosterir. Esik gecerlidir; eksik olan
uygulamadir. Duzeltilene kadar bu boyutta karsilastirma yapma.

- **en uzun plan 4 sn tavani** , en iyi tam videoda deger: **5.6** (tum kayitlar ihlalde)
- **LUFS -16..-13 hedefi** , en iyi tam videoda deger: **-22.1** (tum kayitlar ihlalde)

Olculen kayitlarda teknik esik ihlali yok.

## 6. BASLIK OZNESI

**HIPOTEZ** , baslikin KALIBI degil, OZNESI ayirt ediyor gorunuyor:
gozde canlanan bir SEY (yapi, eser, hayvan, marka) > OLAY > adiyla
anilan KISI. Kaynak: `shadowedhistory/REELYZE-RAPOR.md` , 29 bolumun tamami olculdu, 10 Eylul 2026.

Bu defterde HENUZ yeterli etiket yok (en az iki grupta 3'er
tam bolum gerekiyor), bu yuzden **sayi uretilmedi**.
Etiket eklemek icin: `kanallar/event-horizon/ozne.json`
(`{"<video_id>": "SEY" | "OLAY" | "KISI"}`).

Uygulama notu: kisi konusu ELENMEZ, basligin OZNESI degistirilir.
Ornek: "John Snow: The Father Of Epidemiology" yerine
"The Water Pump That Ended London's Cholera Outbreak".
