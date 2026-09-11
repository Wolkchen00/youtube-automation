# BEYIN , aimagine-fear

Uretim: 2026-09-11T04:08:38.470848+00:00
Kaynak: `/home/runner/work/youtube-automation/youtube-automation/gunluk_beyin/kanallar/aimagine-fear/defter.jsonl` (15 kayit)

Bu dosya HER GUN yeniden yazilir. Sabit fikir havuzu yoktur.
Sadece **24 saatten eski** videolar olculur, boylece izlenmenin
nerede oturdugu gorulur.

---

## 1. DURUM

- Olculen video: **15**
- Siralama olcusu: guncel izlenme , _24. saat olcumu henuz 2/15 kayitta var, yaslar farkli oldugu icin siralamayi dikkatli oku_
- Medyan izlenme: **17**
- Aralik: 1 ile 3,216 arasi

| | izlenme | tarih | baslik |
|---|---|---|---|
| EN IYI | 3,216 | 2026-09-06 | You're falling past the Burj Khalifa on a transp |
| EN KOTU | 1 | 2026-09-01 | Next Stop: Xibalba 🏞️💀 |

Son yayinlar (tekrar etme):
- 2026-09-10 , You're falling through glowing neon around the STRAT Tower. 
- 2026-09-09 , You're sliding down past the Oriental Pearl Tower on a trans
- 2026-09-08 , You're dropping past the Eiffel Tower on a transparent slide
- 2026-09-07 , You're sliding around the CN Tower on a transparent water sl
- 2026-09-06 , You're falling past the Burj Khalifa on a transparent slide 

### Yayinlanmayanlar

- Bu kanal icin seri kaydi okunamadi (ayri boru hatti ya da dosya yok). Yayinlanmayan bolumler GORUNTULENEMIYOR; bu 'hata yok' demek DEGILDIR.

## 2. BU KANALDA NE ISE YARIYOR

Videolar izlenmeye gore siralandi, ust yari ile alt yarinin
medyanlari karsilastirildi.

| olcum | ust yari | alt yari | yon | n |
|---|---|---|---|---|
| sure | 15.10sn | 56.22sn | ust yari DAHA DUSUK | n=7/7 |
| kesme / 10 sn | 0.00 | 0.53 | ust yari DAHA DUSUK | n=7/7 |
| en uzun plan | 15.08sn | 15.34sn | **anlamli fark yok** | n=7/7 |
| ses seviyesi (LUFS) | -15.50 | -16.10 | **anlamli fark yok** | n=7/7 |
| kelime sayisi | 0.00 | 0.00 | **anlamli fark yok** | n=7/7 |

> **Korelasyon, nedensellik degil.** Bunlar yon gosterir,
> kanun degildir. Tek dogru sanma, hipotez olarak kullan.

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

2. bolumdeki farklardan cikan somut hedefler:

- **sure**: ust yarinin medyani 15.10sn (alt yari 56.22sn). Bugunku videoyu 15.10sn civarina hedefle.
- **kesme / 10 sn**: ust yari 0.00, alt yari 0.53. Fark var ama hedef olarak VERILMIYOR (sifira yakin kesme onerisi zararli olur). Bu, format farkinin yan urunu olabilir.

## 5. KACIN

### Bu kanalda HIC UYGULANMAMIS esikler

Asagidaki esigi olculen videolarin **TAMAMI** ihlal ediyor.
Bu, esigin burada calismadigini GOSTERMEZ , boru hattinin o
esigi hic uygulamadigini gosterir. Esik gecerlidir; eksik olan
uygulamadir. Duzeltilene kadar bu boyutta karsilastirma yapma.

- **en uzun plan 4 sn tavani** , en iyi tam videoda deger: **15.1** (tum kayitlar ihlalde)

- **Ses seviyesi hedef disi**: `MUtJyJ-jOKg` -16.5 LUFS (hedef -16..-13)
- **Ses seviyesi hedef disi**: `w3KuWLDTCpQ` -16.5 LUFS (hedef -16..-13)
- **Ses seviyesi hedef disi**: `ttNzWAv2Pnw` -16.1 LUFS (hedef -16..-13)
- **Ses kirpiyor**: `GHTTxuOYSZ0` true peak 0.7 dBFS (tavan -1,0)
- **Ses kirpiyor**: `h-i3gAZ4GUs` true peak 0.7 dBFS (tavan -1,0)
- **Ses kirpiyor**: `SsmjEAKli6M` true peak 0.2 dBFS (tavan -1,0)
- _Ses kirpiyor: toplam 6 kayitta var, ilk 3 gosterildi._
- _Ses seviyesi hedef disi: toplam 7 kayitta var, ilk 3 gosterildi._

## 6. BASLIK OZNESI

**HIPOTEZ** , baslikin KALIBI degil, OZNESI ayirt ediyor gorunuyor:
gozde canlanan bir SEY (yapi, eser, hayvan, marka) > OLAY > adiyla
anilan KISI. Kaynak: `shadowedhistory/REELYZE-RAPOR.md` , 29 bolumun tamami olculdu, 10 Eylul 2026.

Bu defterde HENUZ yeterli etiket yok (en az iki grupta 3'er
tam bolum gerekiyor), bu yuzden **sayi uretilmedi**.
Etiket eklemek icin: `kanallar/aimagine-fear/ozne.json`
(`{"<video_id>": "SEY" | "OLAY" | "KISI"}`).

Uygulama notu: kisi konusu ELENMEZ, basligin OZNESI degistirilir.
Ornek: "John Snow: The Father Of Epidemiology" yerine
"The Water Pump That Ended London's Cholera Outbreak".
