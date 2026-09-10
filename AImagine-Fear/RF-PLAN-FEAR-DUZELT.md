# RF-PLAN-FEAR-DUZELT , AImagine-Fear kanalini duzelt

Tarih: 10 Eylul 2026 (Los Angeles)
Dal: `codex-fear-duzelt` (worktree; ana agacta baska oturumlarin islenmemis isi var)
Kaynak analiz: `AImagine-Fear/REELYZE-RAPOR.md`
Taban: 9eec629, `python -m pytest AImagine-Fear/tests -q` = 28 passed (olculdu, 2026-09-10 07:50 PDT)

## Core Focus (tek cumle)

AImagine-Fear'in urettigi video kanonun soyledigi seyle birebir ayni olsun, ve
YouTube'a kancasiyla, etiketiyle ve #shorts damgasiyla ulassin.

## Bu planin bir onceki plandan farki

Baska bir oturum `codex-reelyze` dalinda `RF-PLAN-REELYZE.md` yazdi (hic insa edilmedi).
O plan filo geneli ve **erisim sorununu acikca kapsam disi biraktigini** yaziyor.
Bu plan tam tersi: yalnizca AImagine-Fear, ve erisim yarisi DAHIL.
O planin Faz 1'i (Rock 1-4) burada Rock 1-3 olarak devralindi; Faz 2 (filo skor karti)
ve Faz 3 (Reelyze trend hasati) bu kosuda YOK.

## Ihsan'in verdigi uc karar (bu plan bunlara uyar, tartisilmaz)

1. Kapsam: hem uretim hatti hem dagitim.
2. Cozunurluk varsayilani SIMDI 1080p olacak. Kredi maliyeti olculmedi ve bu bilerek
   kabul edildi.
3. Palet testi: kod tarafi kurulur, gercek video uretimini Ihsan tetikler.
   **Hicbir rock para harcayan bir uretim cagrisi calistirmaz.**

## Dogrulanmis durum (her iddia dosya:satir, bu depoda okundu)

| Iddia | Kanit |
|---|---|
| Prompt 1080x1920 30fps istiyor | `canon/MASTER-BLOCK.md` FORMAT bolumu |
| API'ye 720p gidiyor | `tools/gunluk.py:32` `COZUNURLUK = "720p"`, `:148` `--resolution` |
| Kapi 720x1280 BEKLIYOR | `tools/gunluk.py:99` `!= "720" or ... != "1280"` |
| Kapi fps'e bakmiyor | `tools/gunluk.py:94-108` `denetle()` icinde fps yok |
| Rota suresi okunmuyor | `tools/gunluk.py:31` `SURE = 15`, `routes/toronto-cn-red-dusk.md:6` `DURATION: 20`, `routes/vegas-strat-blue-rain-25.md:6` `DURATION: 25` |
| Ses normalizasyonu yok | AImagine-Fear altinda hicbir .py'de `loudnorm` yok |
| Hazir cozum var | `core/ffmpeg_tools.py:234` `master_audio(...)`, `measure_audio_loudness(path)` |
| Etiket gonderilmiyor | `core/uploader.py:453` `tags: str = ""` parametresi VAR, `tools/yayinla.py` HIC gecmiyor |
| Baslik kancasiz | `tools/gunluk.py:170` `caption...[0][:95]`, caption ilk cumlesi 98-99 karakter |
| Kategori degistirilemez | `core/uploader.py` icinde `category` / `categoryId` HIC YOK. Upload-Post'ta kategori alani bu kod yolundan erisilemiyor. Bu yuzden rock DEGIL, `RF-ISSUES-FEAR-DUZELT.md`'ye elle is olarak dustu. |

## Rocklar (bagimlilik sirasinda)

---

### Rock 1: Uretim profili tek yerde, kapi oradan okur (1080p + 30fps)

**Sorun.** Prompt bir sey, API baska sey, kapi ucuncu bir sey soyluyor. Kapi kendi
sabitini dogruladigi icin sapmayi asla goremez, ve 1080p'ye gecilirse dogru videoyu
"sorunlu" diye isaretleyip yayini durdurur.

**Done looks like.**
- `tools/gunluk.py` icinde tek bir `PROFIL` sozlugu: `{"cozunurluk": "1080p",
  "genislik": 1080, "yukseklik": 1920, "fps": 30, "fps_tolerans": 1.0,
  "sure_tolerans": 1.5}`.
- API cagrisi bu sozlukten beslenir; `denetle()` de AYNI sozlukten okur. Iki yerde
  ayri sayi kalmaz.
- Kapi artik fps'i de dogrular (`r_frame_rate` ayristirilarak, `30/1` ve `30000/1001`
  ikisi de 30 sayilir).
- Cozunurluk varsayilani `1080p`, kapinin bekledigi `1080x1920`. **Ayni commit'te.**
- Test edilebilirlik icin iki saf fonksiyon ayrilir:
  - `uretim_komutu(slug, sure, profil) -> list[str]` (argv'yi kurar, calistirmaz)
  - `denetle_alanlar(alanlar, dosya_boyutu, beklenen_sure, profil) -> list[str]`
    (ffprobe'un ayristirilmis alanlarini alir; ffmpeg CAGIRMAZ)
  `denetle(video, beklenen_sure)` bu ikinciyi sarar.

**Non-goal.** Video uretmek. Kredi harcamak. `kie_uret.py`'nin varsayilanlarini
degistirmek (o dort kanalla ortak, `--resolution` zaten disaridan geliyor).

**Proof.**
`python -m pytest AImagine-Fear/tests -q -k "profil or kapi or fps"`
En az su vakalar gecmeli:
- `uretim_komutu` ciktisinda `--resolution 1080p` VAR
- `denetle_alanlar` 1080x1920 30fps icin BOS liste dondurur
- 720x1280 icin cozunurluk sorunu dondurur (eski davranis artik HATA)
- `r_frame_rate=24/1` icin fps sorunu dondurur
- `r_frame_rate=30000/1001` icin sorun DONDURMEZ
- ses akisi yoksa sorun dondurur

---

### Rock 2: Rota suresi okunur, kapi onu dogrular

**Sorun.** `SURE = 15` sabit. 20 ve 25 saniyelik rotalar sessizce 15 saniyeye kirpiliyor;
promptun zaman cizelgesi [0.0-20.0] sayarken video 15 saniye geliyor ve kapi bunu
"dogru" sayiyor cunku kendi sabitine bakiyor. Kaydiragin son ucte biri hic uretilmiyor.

**Done looks like.**
- `tools/gunluk.py` sureyi `routes/<slug>.md` icindeki `DURATION` alanindan okur.
  Ayristirmayi kendi yazma: `build.py` zaten rota ayristiriyor, oradan yararlan
  (`load_route` / `parse_sections`) ya da ayni bicimi kullanan tek kucuk yardimci yaz.
- Bu deger hem `--n-frames` olarak API'ye gider hem de kapinin bekledigi sure olur.
- DURATION okunamaz, sayi degil, ya da <= 0 ise: **kredi harcanmadan ONCE** dur
  (`build --check` adiminin hemen yaninda), acik hata mesaji bas.
- Sabit `SURE = 15` silinir. Geride hicbir yerde kalmaz.

**Non-goal.** Rota dosyalarindaki DURATION degerlerini degistirmek. `build.py`'nin
mevcut DURATION dogrulamasina dokunmak.

**Proof.**
`python -m pytest AImagine-Fear/tests -q -k "sure or duration"`
En az su vakalar:
- `toronto-cn-red-dusk` icin okunan sure 20
- `vegas-strat-blue-rain-25` icin 25
- `dubai-burj-altin` icin 15
- DURATION alani olmayan sahte rota -> hata, sifir API cagrisi
- `DURATION: abc` -> hata
- `DURATION: 0` -> hata
- 20 saniyelik rotada 15 saniyelik video kapida KALIR

---

### Rock 3: Yayindan once ses normalizasyonu, ve kapi sesi olcer

**Sorun.** Olculen: Burj Khalifa -15,4 LUFS, Sanghay -16,5 LUFS, true peak -3,8 ve -3,5.
Sosyal hedef -14 LUFS / -1 dBTP. Depoda iki gecisli loudnorm hazir duruyor ve bu kanal
onu hic cagirmiyor.

**Done looks like.**
- `tools/gunluk.py`, denetim TEMIZ ciktiktan sonra ve yayindan ONCE
  `core.ffmpeg_tools.master_audio(video, master_yolu, target_i=-14.0, target_tp=-1.0)`
  cagirir. Yayina giden dosya master'lanmis olandir.
- Master sonrasi `measure_audio_loudness` ile olcum yapilir; sonuc
  I = -14 +/- 1,0 ve TP <= -1,0 disindaysa **YAYIN DURUR**.
- Olculen LUFS ve true peak `yayin.jsonl` kaydina yazilir.
- `core/` icindeki hicbir dosya DEGISTIRILMEZ, sadece cagrilir. Import yolu
  `yayinla.py`'deki mevcut kalibi izler (depo koku `sys.path`'e eklenir).

**Non-goal.** `core/ffmpeg_tools.py`'yi degistirmek. Video yeniden kodlamak
(`master_audio` zaten `-c:v copy` yapiyor, oyle kalsin).

**Proof.**
`python -m pytest AImagine-Fear/tests -q -k "ses or loudnorm"` , ffmpeg ile uretilen
kucuk bir test klibi (`sine` + `testsrc2`, 2 saniye) master'lanir ve
`measure_audio_loudness` ciktisi -14 +/- 1,0 icinde cikar; kasitli olarak -30 LUFS
birakilmis bir dosya kapida KALIR.
ffmpeg yoksa test `skip` olur, sessizce gecmez.

---

### Rock 4: YouTube kancasi, etiketleri ve #shorts

**Sorun.** Alti videonun etiketleri YouTube'un otomatik copu
(`video, sharing, camera phone, ...`). Sekiz videodan yalniz birinde `#shorts` var.
Basliklar 98-99 karakter ve cumlenin ortasinda kesiliyor, kanca yok.
`core/uploader.py:453` etiket parametresini KABUL EDIYOR, `yayinla.py` gecmiyor.

**Done looks like.**
- **Rota dosyalarina yeni bolum: `TITLE`.** En az 2, en fazla 5 satir; her satir bir
  baslik varyanti. `build.py` bunu zorunlu bolum yapar ve dogrular:
  - satir uzunlugu `#shorts` dahil <= 70 karakter
  - kanca ilk 40 karaktere sigar (yani ilk 40 karakter kendi basina anlamli bir
    cumle parcasi; somut kural: ilk 40 karakter icinde en az bir landmark ya da
    sayi/duygu kelimesi gecer ve kelime ortasinda kesilmez)
  - her satir `#shorts` ile biter
  - ayni rota icinde iki varyant birebir ayni olamaz
- `build.py` `out/<slug>/TITLE.txt` yazar (mevcut `CAPTION.txt` ile ayni kalipta).
- Dokuz mevcut rota dosyasinin hepsine TITLE bolumu eklenir.
- **Varyant secimi (mukerrer baslik tuzagi).** `core/uploader.py:475-488` YouTube'da
  ayni baslik ikinci kez gelirse yuklemeyi ATLIYOR. `sirdaki()` havuz bitince en eski
  slug'a donuyor, yani ayni rota ikinci kez yayinlanacak. Bu yuzden `gunluk.py`
  TITLE varyantlarindan `yayin.jsonl`'de HENUZ KULLANILMAMIS olani secer; hepsi
  kullanilmissa en eski kullanilani secer ve bunu loga acikca yazar.
- **Etiketler.** `tools/yayinla.py` yeni `--tags` argumani alir ve
  `upload_to_platform(..., tags=...)` olarak GECIRIR (su an dusuruluyor).
  Etiketler caption'daki `#` etiketlerinden turetilir (`#` atilir, virgulle birlesir),
  boylece kanon tek kaynak kalir ve ikinci bir liste tutulmaz.
- `gunluk.py` basligi artik `CAPTION.txt`'in ilk satirindan DEGIL `TITLE.txt`'ten alir
  ve `--tags` gecirir.

**Non-goal.** `canon/CAPTION.md` etiket havuzunu degistirmek (kaynak kanalla ayni
havuzda kalmak KASITLI). `canon/NEGATIVES.md`'deki ekran yazisi yasagi. Kategori
degistirmek (kod yolundan erisilemiyor, issue'ya dustu). `core/uploader.py`.

**Proof.**
`python -m pytest AImagine-Fear/tests -q -k "title or baslik or etiket or tags"`
En az su vakalar:
- 70 karakteri asan TITLE satiri `build.py --check`'te KALIR
- `#shorts` ile bitmeyen satir KALIR
- tek varyantli TITLE KALIR
- iki ayni varyant KALIR
- gecerli rota `out/<slug>/TITLE.txt` uretir
- varyant secici: `yayin.jsonl` bos -> ilk varyant; ilk varyant kullanilmis -> ikinci
- etiket turetici `#MegaSlideFear #CNTower` -> `MegaSlideFear,CNTower`
- `yayinla.py --dry` ciktisinda etiketler gorunur
Ayrica `python AImagine-Fear/build.py --check` YESIL kalir (9 rota).

---

### Rock 5: Palet damgasi ve sicak/neon donusumu

**Sorun.** Patlayan video (371.000 begeni) sicak altin/amber; olen video (13 izlenme)
doygun macenta neon. Ikisi teknik olarak birebir ayni. En guclu hipotez paletin
fotogercekcigi bozdugu. Su an palet hicbir yerde kayitli degil, yani sonuc olculemez.

**Done looks like.**
- Rota dosyalarina yeni ALAN: `PALET: sicak` ya da `PALET: neon`. `build.py` zorunlu
  alan yapar ve yalniz bu iki degeri kabul eder.
- Mevcut dokuz rota etiketlenir. Olculen gercek dagilim: `dubai-burj-altin` (warm
  gold-amber) ve `toronto-cn-red-dusk` (hot red-orange) sicak; kalan yedisi neon.
- **Ucuncu bir sicak rota:** `sanghay-inci-amber-sis.md`, mevcut
  `sanghay-inci-yesil-sis.md`'nin yalnizca RENK acisindan yeniden boyanmis kopyasi.
  `NEON: acid green` -> `NEON: warm amber-gold`, ve BEATS/OPENING/END icindeki yesil
  renk tarifleri amber'a cevrilir. **Zaman cizelgesi, beat sinirlari, VOICE zamanlari,
  kelime sayisi ve cumle yapisi AYNEN korunur.** Yeni SLUG, yeni CAPTION landmark
  etiketi ayni (`#OrientalPearlTower` kalibinda), TITLE varyantlari yazilir.
- `SIRA` listesi sicak/neon donusumlu olacak sekilde yeniden dizilir (uc sicak rota
  yedi neon rotanin arasina serpistirilir), boylece A/B kendiliginden yurur.
- `yayin.jsonl` kaydina her yayinda `slug`, `palet`, `rota_suresi`, `cozunurluk`,
  `fps`, `lufs`, `true_peak` yazilir. Su an `slug` yayindan SONRA son satira
  yamaniyor (`gunluk.py:180-186`); bu yamama kaldirilir ve alanlar `yayinla.py`
  kaydin icine dogrudan yazar.

**Non-goal.** Gercek video uretmek ya da Kie'ye tek bir istek bile atmak. Mevcut
`yayin.jsonl` satirlarini geriye donuk doldurmak. Yeni sehir icat etmek.

**Proof.**
`python -m pytest AImagine-Fear/tests -q -k "palet"`
- `PALET` alani olmayan rota `build.py --check`'te KALIR
- `PALET: mor` KALIR
- dokuz + bir = on rotanin hepsi gecer
- `SIRA` icinde ust uste uc ayni palet YOKTUR
- yayin kaydi yazicisi `palet` alanini iceren bir sozluk uretir
Ayrica `python AImagine-Fear/build.py --check` on rota icin YESIL,
ve `sanghay-inci-amber-sis` icin uretilen PROMPT.txt icinde `acid green` GECMEZ.

---

## Kapanis kapisi (butun rocklar bittikten sonra)

```
python -m pytest AImagine-Fear/tests -q      # 28 taban testi + yeni testler, hepsi yesil
python AImagine-Fear/build.py --check         # 10 rota, temiz
python AImagine-Fear/tools/gunluk.py --dry    # sirdaki sehir, sure, palet, profil basar
```
`--dry` hicbir sey uretmez ve hicbir kredi harcamaz. Kredi okumasi icin ag gerekir;
ag yoksa acik mesajla durur, sessizce gecmez.

## Sira ve bagimliliklar

```
Rock 1 -> Rock 2   (ikisi de denetle()/gunluk.py'yi degistiriyor, sira sart)
Rock 2 -> Rock 3   (kapi once dogru olsun, sonra ses adimi araya girsin)
Rock 3 -> Rock 4   (yayin cagrisinin imzasi Rock 4'te degisiyor)
Rock 4 -> Rock 5   (ikisi de build.py'ye rota alani/bolumu ekliyor)
```

**KRITIK:** Rock 1'in cozunurluk degisikligi ile kapi degisikligi AYNI commit'te.
Ayrilirsa yayin durur.

## Dokunulmayacaklar

- `core/` altindaki her sey. Rock 3 ve Rock 4 yalnizca CAGIRIR, degistirmez.
  Dort canli kanal ayni motoru kullaniyor.
- `canon/NEGATIVES.md:15` ekran yazisi yasagi. Reelyze "ekran yazisi ekle" diyor ama
  371.000 begeni metinsiz geldi. Degistirilecekse ayri karar, ayri test.
- `canon/CAPTION.md` sabit etiket havuzu (kaynak kanalla ayni kumede kalmak kasitli).
- `tools/kie_uret.py` icindeki cuzdan ve `MIN_KREDI = 700` tabani. Cuzdan dort kanalla
  ORTAK.
- `yayin.jsonl` icindeki mevcut satirlar. Yalniz yeni satirlar yeni alanlari tasir.
- Diger kanallarin klasorleri: `aimagine/`, `sentinal_ihsan/`, `galactic_experience/`,
  `shadowedhistory/`, `series/`, `AImagine-Train/`.

## Bu planda BILEREK olmayanlar

- Kategoriyi "Travel & Events" yapmak: `core/uploader.py` kategori alanini hic
  desteklemiyor, elle YouTube Studio isi. -> `RF-ISSUES-FEAR-DUZELT.md`
- "Next Stop" serisini kanaldan ayirmak: YouTube hesap islemi, kod degil.
  -> `RF-ISSUES-FEAR-DUZELT.md`
- 1080p'nin gercek kredi maliyeti: ilk gercek kosuda olculecek, tarifeye ONCEDEN
  yazilmayacak.
- Filo geneli skor karti ve Reelyze trend hasati: `RF-PLAN-REELYZE.md` Faz 2-3, ayri is.
