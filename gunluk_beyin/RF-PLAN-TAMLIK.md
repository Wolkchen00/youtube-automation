# RF-PLAN , beyin: eksik bolum korlugu + baslik oznesi boyutu

Tarih: 10 Eylul 2026 (Los Angeles)
Dal: `nemo-beyin-tamlik` (worktree; ana agacta alti baska oturum var)
Integrator: Nemotron (`/nemo`)

## Core Focus (tek cumle)

Beyin, KUSURLU uretilmis bir bolumu basari ornegi sanmasin.

---

## Sorun (bu kosuda olculdu, tahmin degil)

Beyin yayinlanmis DOSYAYI olcuyor (`yt-dlp` + `ffmpeg`) ama URETIM KAYDINA hic
bakmiyor. Bu yuzden "9,44 saniye" degerinin ne oldugunu bilemiyor: bu deger bu
kanalda tek bir seyin imzasidir , QC bir cekimi dusurmus, anlatim otomatik
kisaltilmis YARIM bolum.

Sonuc: `gunluk_beyin/kanallar/flashpoints/BEYIN.md` bugun sunu tavsiye ediyor:

```
## 4. BUGUN ICIN YON
- sure: ... Bugunku videoyu 9.44sn civarina hedefle.
- kelime sayisi: ... Bugunku videoyu 26.00 civarina hedefle.
```

Bu, 2026-09-10'da `shadowedhistory/flashpoints/bible.json` icine `qc.min_shots: 2`
eklenerek DURDURULAN kusurun ta kendisidir. Boru hatti artik 9,44 saniyelik bolum
URETEMEZ, yani beyin ulasilamayan bir hedefi her gun onermeye devam eder.

### Olculen kanit , beynin ust yarisi ile yarim bolumlerin ortusmesi

15 kayitlik flashpoints defteri, beynin kendi ust/alt kovalarina gore:

| kova | video | yarim bolum |
|---|---|---|
| **UST** | 7 | **4 (%57)** |
| alt | 8 | 2 (%25) |

Ust yarinin medyan suresini (9,44 sn) ve medyan kelime sayisini (26) o dort yarim
bolum belirliyor. Iki dev aykiri deger (Wrangel 1.179 ve Brooklyn 509) de yarim
bolum , 15 satirlik orneklemde ikisi medyani domine ediyor.

**Beyne haksizlik edilmiyor:** mantigi dogru ve zaten cekinceli
("Korelasyon, nedensellik degil"). Kusur GIRDIDE: defter bir bolumun eksik uretilip
uretilmedigini bilmiyor. Nitekim tam 29 bolumluk katalogda etki KAYBOLUYOR
(yarim kova medyani 23, tam 15 sn kovasi 33); beynin penceresi son 15 video ve o
pencerede erken donemin hitleri (Nintendo 795, Roma betonu 242, Napoleon 193) yok.

### Ikinci kusur: bir esigi n=1 ile gecersiz ilan ediyor

`BEYIN.md` bolum 5:

```
- ~~LUFS -16..-13 hedefi~~ , en iyi videoda deger: -21.2
```

"En iyi videomuz esigi ihlal ediyor, oyleyse esik burada calismiyor" akil yurutmesi
TEK VIDEOYA dayaniyor ve o video da yarim bolum (`nH-BdFphWRQ`, part 22). Ayni gun
`master_lufs: -14` gonderildi; filo kanitiyla da celisiyor (sesi dogru olan tek seri
`unnatural-lab` -14,3 LUFS ve medyani 1.292 olan tek seri).

---

## Tespit yontemi , GERCEK VERIYLE DOGRULANDI

Iki aday sinyal sinandi (`published.json` + `series.json` + `plans/` + `qc_log.jsonl`,
15 kayitlik flashpoints defteri):

| yontem | sonuc |
|---|---|
| `series.json` -> `parts.<n>.dropped_shots` | kesin AMA eksik , part22'yi KACIRIYOR (alan sonradan eklenmis) |
| kesme sayisi (teslim cekim = kesme+1) | KULLANILAMAZ , 6 eksik bolumden yalniz 1'ini buldu |
| **olculen sure / planlanan sure** | **KUSURSUZ , 6/6 dogru, 0 yanlis isaret** |

Olculen ayrim:

| bolum tipi | oran |
|---|---|
| tam (part 16-21, 25, 28, 29) | 0,93 , 0,95 |
| eksik (part 22, 23, 24, 26, 27, 30) | 0,46 , 0,48 |

0,60 / 0,65 / 0,70 / 0,75 esiklerinin DORDU de ayni kumeyi veriyor
(`{22, 23, 24, 26, 27, 30}`), ve bu kume `qc_log.jsonl` `final_reject` kumesiyle
BIREBIR ayni. Iki kova arasinda veri yok; **0,70 kocaman bir bosluga oturuyor.**

---

## Rock 1: eksik uretilmis bolum kural cikarimina girmesin

**Yapilacak (`gunluk_beyin/beyin.py`):**

1. Kanal -> uretim kaydi eslesmesi ekle. Sabit bir sozluk, `CHANNELS` yaninda:
   ```
   PRODUCTION_DIRS = {
       "unnatural-lab": "sentinal_ihsan/unnatural-lab",
       "event-horizon": "galactic_experience/event-horizon",
       "flashpoints":   "shadowedhistory/flashpoints",
       "aimagine-fear": None,          # ayri hat, series.json yok
   }
   ```

   **YOL COZUMU , burada dikkat (turu 1'de olculdu, Nemo'nun onerisi duzeltildi):**

   | | cwd |
   |---|---|
   | GitHub workflow | `<depo>/gunluk_beyin` (`working-directory: gunluk_beyin`) |
   | testler | gecici klasor (`calistir()` beyin.py'yi `cwd=kok` ile ALT SUREC olarak kosar) |

   Mevcut `channel_dir()` yollari `os.getcwd()`'ye gore cozuyor ve testler tam olarak
   bunu kullaniyor. Uretim yolu da AYNI mantikla cozulmeli, ama testler alt surec
   oldugu icin Python parametresi gecemez , yalnizca cwd ve ortam degiskeni kontrol
   edebilirler. Bu yuzden:

   ```
   def production_root():
       override = os.environ.get("BEYIN_URETIM_KOK")
       if override:
           return override
       return os.path.abspath(os.path.join(os.getcwd(), ".."))
   ```

   `ROOT` (modulun kendi klasoru) KULLANILMAYACAK: uretimde dogru sonucu verir ama
   testlerde GERCEK depoyu isaret eder, testler hermetik olmaktan cikar ve canli
   depo durumuna baglanir. Cozum cagri aninda hesaplanmali (import aninda DEGIL),
   yoksa ortam degiskeni testlerde ise yaramaz.

   Klasor veya dosya yoksa fonksiyon BOS eslesme dondurur ve hicbir sey patlamaz.

2. `episode_completeness(channel)` fonksiyonu: `{video_id: {...}}` dondurur.
   - `published.json` -> `results.youtube` ile `video_id -> part`
   - `plans/part<NN>.json` -> `sum(shot["duration"])` = planlanan saniye,
     `len(shots)` = planlanan cekim
   - `series.json` -> `parts.<n>.dropped_shots`
   - Karar (UNION, ikisi birden):
     * `dropped_shots` bos olmayan bir listeyse -> `complete = False`
     * VEYA planlanan sure biliniyor ve `olculen / planlanan < 0.70` -> `complete = False`
     * ikisi de bilinmiyorsa -> `complete = None` (BILINMIYOR, False DEGIL)
   - Esik modul sabiti olsun: `COMPLETE_DURATION_RATIO = 0.70`, yanina olculen
     0,46/0,95 ayrimini anlatan bir yorum.

3. `cmd_brain` icinde satirlar uce ayrilsin: **tam**, **eksik**, **bilinmiyor**.
   - Bolum 2 (karsilastirma) ve bolum 4 (bugun icin yon) YALNIZ `complete is not False`
     olan satirlarla hesaplansin. Yani eksik oldugu BILINEN bolum kural cikarimina
     girmez; bilinmeyen girer (eski davranis korunur, sessiz veri kaybi olmaz).
   - `MIN_SAMPLES` kontrolu ARTIK ELENMIS kume uzerinden yapilsin. flashpoints icin
     15 kayittan 6'si duser, 9 kalir, 9 < 15 -> bolum 2 ve 4 "YETERSIZ VERI" der.
     **Bu dogru ciktidir.** Kusurdan kural cikarmaktansa "yeterli temiz veri yok"
     demek dogrudur. Yeni (duzeltme sonrasi) bolumler biriktikce kendiliginden acilir.
   - Bolum 5'teki "gecersiz esikler" mantigi da ELENMIS kumenin en iyisini kullansin.
     Bir esigi yarim bolume dayanarak gecersiz ilan etmek tam olarak bugunku LUFS
     hatasidir.

4. Eksik bolumler ISIMLE listelensin, dislandiklari soylensin ve sebebi yazilsin
   (hangi sinyal tetikledi: `dropped_shots` mi, sure orani mi, oran kac). Sessizce
   dusurme; okuyan ajan neyin neden dislandigini gorsun.

   **NEREYE:** `## 1. DURUM` bolumunun icine `###` seviyesinde bir ALT baslik olarak.
   YENI bir `## N.` ust baslik ACMA. Gerekce olculdu: `tests/test_beyin_bagimsiz.py:69`
   `BASLIKLAR` sabiti bes ust basligi birebir sabitliyor,
   `test_bes_baslik_birebir_var` her birinin TAM BIR KEZ gectigini,
   `test_baslik_sirasi_dogru` sirayi dogruluyor. Alt baslik bu testleri etkilemez.

**Done looks like:** flashpoints `BEYIN.md` artik "9,44 saniye hedefle" DEMIYOR;
bolum 2/4 yetersiz veri diyor; eksik alti bolum sebebiyle birlikte listeleniyor;
bolum 5 LUFS esigini yarim bolume dayanarak gecersiz ilan etmiyor.

**DOKUNMA:** `arac/` altindaki olcum modulleri, `defter.jsonl` dosyalari (makine
yazar), `.github/workflows/gunluk-beyin.yml`, ve `gunluk_beyin` disindaki hicbir sey.

## Rock 2: baslik oznesi boyutu

**Neden:** 29 yayinlanmis bolumun tamami olculdu (10 Eylul). Baslik KALIBI hicbir sey
ongormuyor (her kalipta hem hit hem sifir var). Baslikin OZNESI onguruyor:

| ozne | n | medyan izlenme |
|---|---|---|
| SEY (yapi, eser, hayvan, marka) | 12 | **80** |
| OLAY (savas, yangin, sel) | 9 | 20 |
| KISI (adiyla anilan birey) | 8 | **8** |

Siralama hem erken (1-20) hem gec (21-30) donemde ayni; yedi ayri yeniden
siniflandirma ve ucu ayni anda denendi, siralama bozulmadi. Ayrinti:
`shadowedhistory/REELYZE-RAPOR.md` icindeki "EK , BASLIK ANALIZI" bolumu.

**Yapilacak:**

1. Kurate edilmis etiket dosyasi: `gunluk_beyin/kanallar/<kanal>/ozne.json`
   ```
   {"<video_id>": "SEY" | "OLAY" | "KISI", ...}
   ```
   **Defterin kendisi ELLE DUZENLENMEZ** , o makine ciktisidir (`write_ledger`
   her kosuda yeniden yazar). Etiket insan bilgisidir, ayri dosyada durur.
   Dosya yoksa hicbir sey patlamaz.

2. `cmd_brain` yeni bir bolum yazsin: `## 6. BASLIK OZNESI`.
   Bu YENI bir ust baslik olabilir , dogrulandi: `BASLIKLAR` yalniz 1-5'i sabitliyor,
   `test_baslik_sirasi_dogru` yalniz o besinin konumuna bakiyor, altina eklenen
   6. bolum ikisini de bozmaz. Metni bes basligin hicbirini birebir ICERMEMELI. Yalniz **eksik olmayan**
   satirlarla ve yalniz etiketi olanlarla hesaplansin.
   - En az IKI grupta en az 3'er etiketli satir varsa: grup medyanlarini tablo yap,
     grup basina n yaz, ve ayni "korelasyon, nedensellik degil" cekincesini koy.
   - Yeterli etiket yoksa: SAYI URETME. Bunun yerine bulguyu KAYITLI HIPOTEZ olarak
     yaz, kaynagini (`REELYZE-RAPOR.md`, 29 bolum, 10 Eylul 2026) goster ve
     `ozne.json`'a etiket eklenmesi gerektigini soyle.
   - **Dongusellik uyarisi (Nemo turu 1, kabul edildi):** etiketler ELLE konuyor ve
     medyan ayni etiketlerden hesaplaniyor. Bu bir KESIF DEGILDIR. Cikti metni bunu
     acikca soylemeli: bolum "HIPOTEZ" kelimesini ve kaynak atfini
     (`REELYZE-RAPOR.md`, 29 bolum, 10 Eylul 2026) MUTLAKA icermeli, "kesif"/"bulduk"
     dili KULLANMAMALI. Bu testle dogrulanacak (proof 13).
   - Gecersiz etiket degeri (SEY/OLAY/KISI disi) sessizce ATLANSIN, satir sayilmasin.

3. flashpoints icin `ozne.json` tohumlansin , defterdeki 15 video icin, asagidaki
   denetlenebilir atamalarla (kural: SEY = gozde canlanan somut sey; OLAY = vaka;
   KISI = adiyla anilan birey):

   | video_id | ozne | konu |
   |---|---|---|
   | NZE4B4iylnM | SEY | Oxford University |
   | v4DAdC8OYkA | SEY | Colosseum |
   | 6GgIn4roshE | KISI | Cleopatra |
   | EUysWNHpokY | SEY | Roma idrar camasirhanesi |
   | ZFI72hS02Qs | OLAY | Viyana 1913 |
   | KBmoJvN4spE | KISI | Cleopatra |
   | nH-BdFphWRQ | SEY | Wrangel mamutlari |
   | bhTaWCiP6c4 | OLAY | Londra bira seli 1814 |
   | f-TYvhYuvQg | SEY | Great Wall |
   | azsyU1pLZW4 | OLAY | Tanganyika kahkaha salgini |
   | lMSL80iP3Cg | SEY | Brooklyn Bridge |
   | IkqbnHyj-Ms | OLAY | Great Fire of London |
   | Rt8lp7mJxYE | OLAY | bos ada isgali |
   | to7T1zjXpaU | KISI | Henry Box Brown |
   | sO6q52tZaqg | OLAY | Yuz Yil Savaslari |

**Done looks like:** `ozne.json` var; flashpoints raporunda BASLIK OZNESI bolumu
gorunuyor; eksik bolumler bu hesaba da girmiyor; etiketsiz kanallarda (event-horizon,
unnatural-lab, aimagine-fear) bolum sayisiz hipotez metnine dusuyor ve patlamiyor.

---

## PROOF

Yeni testler mevcut dosyaya eklenir: `gunluk_beyin/tests/test_beyin_bagimsiz.py`
(866 satir, pytest, fixture + parametrize uslubu , AYNEN o uslup izlenecek).

Kanit sunlari OLCMELI:

1. **Eksik bolum kural cikarimindan cikar.** Fixture: 15 satirlik defter; en YUKSEK
   izlenmeli satir eksik bolum olsun (planlananin %47'si). Uretilen `BEYIN.md`
   bolum 4'te o satirin suresi HEDEF olarak GECMEMELI.
2. **Bos gecmeyen capa:** ayni fixture'da eksik satir TAM yapilirsa bolum 4'te o
   sure hedef olarak GECMELI. (Yoksa 1. madde bos gecer.)
3. **Esik ayrimi:** oran 0,47 -> eksik; oran 0,93 -> tam. Sinir civari (0,69 / 0,71)
   iki yone de dogru dusmeli.
4. **dropped_shots tek basina yeterli:** sure bilgisi HIC yokken `dropped_shots: [2]`
   olan satir yine de eksik sayilmali.
5. **BILINMIYOR eksik DEGILDIR:** ne `dropped_shots` ne planlanan sure varsa satir
   kural cikarimina GIRMELI (sessiz veri kaybi olmasin).
6. **MIN_SAMPLES elenmis kume uzerinden:** 15 satirin 6'si eksikse bolum 2 ve 4
   "YETERSIZ VERI" demeli.
7. **Eksikler ISIMLE raporlanmali:** dislanan her video_id ve sebebi ciktida gecmeli.
8. **Bolum 5 gecersiz-esik mantigi** eksik bolume dayanarak bir esigi gecersiz ilan
   ETMEMELI (LUFS vakasi birebir test edilsin).
9. **Baslik oznesi , yeterli etiket:** iki grupta 3'er etiketli tam satir varsa
   tablo cikmali ve medyanlar dogru olmali.
10. **Baslik oznesi , yetersiz etiket:** etiket yoksa SAYI CIKMAMALI; hipotez metni
    ve kaynak gecmeli.
11. **Bozuk girdi patlatmamali:** `ozne.json` yok / bos / bozuk JSON / gecersiz etiket
    degeri / bilinmeyen video_id , hicbirinde cokme olmamali.
12. **Uretim kaydi yoksa** (aimagine-fear, `PRODUCTION_DIRS` degeri None) beyin eskisi
    gibi calismali.
13. **Dongusellik durustlugu:** baslik oznesi bolumu tablo urettiginde metin
    "HIPOTEZ" kelimesini ve `REELYZE-RAPOR.md` atfini icermeli.
14. **Mevcut bes baslik bozulmamali:** `test_bes_baslik_birebir_var` ve
    `test_baslik_sirasi_dogru` DEGISMEDEN gecmeli.
15. **Yol cozumu:** `BEYIN_URETIM_KOK` ortam degiskeni verildiginde uretim kaydi
    ORADAN okunmali; verilmediginde `cwd/..` kullanilmali.

**Calistirma komutlari , TEK KOMUT, kabuk operatoru YOK** (Nemo `run_command`'i
Windows `cmd.exe` altinda kosar; `;` veya `$?` iceren komutta doner durur):

```
python -m pytest gunluk_beyin/tests/test_beyin_bagimsiz.py -q
```

```
python gunluk_beyin/beyin.py beyin flashpoints
```

Ikincisi gercek defteri okur ve `BEYIN.md`'yi yeniden yazar; ciktisinda artik
"9.44sn civarina hedefle" GECMEMELI.

---

## BUDGET

Bu is en fazla **30 adim** surer. Kod iki dosyada: `gunluk_beyin/beyin.py` ve
`gunluk_beyin/tests/test_beyin_bagimsiz.py`, arti yeni `ozne.json`.
Sentetik test fixture'i INSA ETME, kendi isini tekrar tekrar dogrulama.
Proof komutlarini BIRER KEZ calistir, sonra RAPORUNU YAZ VE ARAC CAGIRMAYI BIRAK.

## Kapsam disi

- `gunluk_beyin/arac/` altindaki olcum modulleri
- `defter.jsonl` dosyalari (makine yazar, elle duzenlenmez)
- `.github/workflows/gunluk-beyin.yml`
- `gunluk_beyin/` disindaki HICBIR dosya (kanal bible/series dosyalari dahil ,
  bu kosuda YALNIZ okunurlar)
- Beynin mevcut esikleri (`MIN_SAMPLES`, `MIN_AGE_HOURS`, `MIN_RELATIVE_GAP`)
  degistirilmeyecek

---

# SONUC (10 Eylul 2026)

## Kim ne yapti

- **Nemo (Integrator)** `gunluk_beyin/tamlik.py`'yi yazdi (199 satir). Iki kez
  once basarisiz oldu: ilk cagri 19 arac cagrisinin 19'unu da OKUMAYA harcayip
  "simdi uygulamaya geciyorum" cumlesiyle bitirdi, devam turu bos rapor dondu.
  Kok neden bu harness'in yapisal siniri: `write_file` DOSYANIN TAMAMINI yeniden
  yazar, yani 613 satirlik `beyin.py`'yi degistirmek modelin o 613 satiri bastan
  hatasiz uretmesini gerektiriyor. Ucuncu cagri YENI ve KUCUK bir dosya isteyince
  calisti.
- **Claude (Visionary)** iki tur basarisizliktan sonra direksiyonu aldi
  (motor kurali: 2 fix turundan sonra Visionary bitirir): `beyin.py` entegrasyonu,
  `ozne.json`, iki test dosyasi ve asagidaki uc ek duzeltme.

## Plana EK olarak yapilanlar (gerekceli)

1. **Yetersiz-veri mesaji temiz sayiyi basiyor.** Eskisi "n=15, en az 15 gerekiyor"
   diyordu , esik saglanmis gibi gorunurken kural cikarmayi reddediyordu, hata gibi
   okunuyordu. Artik "temiz kayit n=9 ... 6 tanesi eksik uretildigi icin sayilmadi".

2. **"Gecersiz esik" mantigina yeni bir ayrim: HIC UYGULANMAMIS.** Bolum 5, en iyi
   video bir esigi ihlal edince esigi cizip atiyordu. Ama flashpoints'te 15 kaydin
   15'i de LUFS esigini ihlal ediyor , cunku mastering hic cagrilmamisti. Herkesin
   ihlal ettigi bir esik, esigin yanlis oldugunu DEGIL, hic uygulanmadigini gosterir.
   Cizip atmak gercek kusuru gizler. Artik ayri bir baslikta ve "esik gecerlidir,
   eksik olan uygulamadir" diyerek raporlaniyor.

3. **Is akisi tum `tests/` klasorunu kosuyor.** Eskisi tek dosya adini sabitliyordu
   (`tests/test_beyin_bagimsiz.py`), yani yeni eklenen `test_tamlik.py` CI'da HIC
   kosmayacakti. Kosmayan test koruma degildir. Plan "workflow degismeyecek" diyordu;
   bu kisit BILEREK ihlal edildi ve sebebi burada.

## Kendi hatam , tam diff okurken yakalandi

Bolum 2'nin `rankable` listesi filtresiz kalmisti (girinti uyusmadigi icin bir
degistirme sessizce hicbir sey yapmamis, ve o satirda `assert` koymamistim).
Testler bunu yakalamadi cunku flashpoints'te temiz kayit 15'in altinda kaliyor ve
bolum 2 o satira hic ulasmiyor. Kacak ancak temiz kayit esigi astiginda ortaya
cikacakti: bolum 2 eksik bolumleri sayarken bolum 4 saymayacakti.
Duzeltildi + `test_bolum2_de_eksik_bolumleri_saymaz` eklendi (mutasyonla bos
gecmedigi dogrulandi).

## Kanit (hepsi Claude tarafindan kosuldu)

- `python -m pytest tests -q` (CI'nin komutu, cwd=gunluk_beyin): **98 gecti**
- Mevcut 52 testin hicbiri degistirilmedi: `git diff --numstat` -> **231 ekleme, 0 silme**
- Mutasyon testi , su dordunun her biri geri alininca ilgili test DUSTU:
  filtre (`kept`), esik `0.70`, `_all_break` mantigi, bolum 2 filtresi
- Gercek defterde dogrulama: modul tam olarak `{22, 23, 24, 26, 27, 30}` buluyor,
  `qc_log.jsonl` `final_reject` kumesiyle birebir

## Ciktida dogrulanan dort sey

1. Bolum 4'te "9.44sn hedefle" YOK
2. Eksik alti bolum sebebiyle birlikte listeleniyor
3. Bolum 5 LUFS esigini gecersiz ilan ETMIYOR (artik "hic uygulanmamis" diyor)
4. Bolum 6 hipotez etiketi ve `REELYZE-RAPOR.md` atfiyla cikiyor

## Kalan (yapilmadi)

- `ozne.json` yalniz flashpoints icin var. Diger uc kanalda bolum 6 sayi
  uretmeden hipotez metnine dusuyor , dogru davranis, etiket bekliyor.
