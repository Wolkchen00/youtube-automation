# RF-PLAN-FEAR-DUZELT , AImagine-Fear kanalini duzelt

Tarih: 10 Eylul 2026 (Los Angeles)
Dal: `codex-fear-duzelt` (worktree; ana agacta baska oturumlarin islenmemis isi var)
Kaynak analiz: `AImagine-Fear/REELYZE-RAPOR.md`
Taban: 9eec629, `python -m pytest AImagine-Fear/tests -q` = 28 passed (olculdu, 2026-09-10 07:50 PDT)
Revizyon: r2 (Codex round 1'in 22 bulgusu islendi, `RF-SAME-PAGE-LOG-FEAR-DUZELT.md`)

## Core Focus (tek cumle)

AImagine-Fear'in urettigi video kanonun soyledigi seyle birebir ayni olsun, YouTube'a
kancasiyla ve etiketiyle ulassin, ve hangi paletle uretildigi olculebilir kalsin.

## Ihsan'in verdigi uc karar (bu plan bunlara uyar, tartisilmaz)

1. Kapsam: hem uretim hatti hem dagitim.
2. Cozunurluk varsayilani SIMDI 1080p olacak. Kredi maliyeti olculmedi, bilerek kabul edildi.
3. Palet testi: kod tarafi kurulur, gercek video uretimini Ihsan tetikler.
   **Hicbir rock para harcayan bir uretim cagrisi calistirmaz.**

## Round 1'de ORTAYA CIKAN ve plani degistiren uc gercek

Bunlar ilk planda YOKTU. Ucu de bu depoda dogrulandi.

**A. ffprobe duz sozluge cevrilince ses akisi videonun fps'ini eziyor.**
Canli olcum (`out/*/video/*.mp4`):
```
codec_type=video   r_frame_rate=24/1
codec_type=audio   r_frame_rate=0/0
```
`denetle()` su an `dict(re.findall(r"^(\w+)=(.+)$", ...))` yapiyor; sonraki akis
oncekini eziyor. fps kapisi bu haliyle yazilsaydi HER videoda yanlis kalirdi.

**B. `bytedance/seedance-2`'nin sure ve cozunurluk sinirlari BILINMIYOR.**
Once `routes/vegas-strat-blue-rain-15.md:10`'daki *"bytedance/seedance-2 tavani 15
saniye"* notuna guvendim. **Bu not guvenilmez.** Dogrulama:
```
core/kie_api.py:481   resolution: str = "720p"
core/kie_api.py:483   model: str = "bytedance/seedance-2-fast"     <- FAST varyanti
core/kie_api.py:489   "Seedance duration is an integer 4-15s; resolution 480p/720p"
AImagine-Fear/tools/gunluk.py:30   MODEL = "bytedance/seedance-2"  <- FAST DEGIL
```
"4-15 saniye" ve "480p/720p" sinirlari **`seedance-2-fast`'i** belgeliyor. Bu kanal
fast OLMAYAN modeli cagiriyor ve onun gercek sinirlari depoda HICBIR YERDE yazili
degil. Ters yonde ipucu da var: `sentinal_ihsan/KONSEPT_v3_TASLAK.md:365` bir Seedance
varyantinda 20 saniyeden soz ediyor.

Sonuc: REELYZE raporunun 5. maddesi ("rota DURATION alanini oku") **oldugu gibi
uygulanamaz**, ama sebebi "tavan 15" degil, **sinirlari bilmiyor olmamiz**. Plan bu
belirsizligi kodda ACIKCA tasiyor: izin listesi var, "DOGRULANMADI" diye isaretli, ve
yalniz gercekten uretip yayinladigimiz sureyi (15) iceriyor.

**C. `yayinla.py` basarisiz donmeden ONCE deftere yaziyor.**
`tools/yayinla.py` kaydi `DEFTER`'e ekliyor, sonra `return 0 if basarili else 1`.
`sirdaki()` ise yalniz `slug` alaninin VARLIGINA bakiyor. Bu yuzden `slug`'i dogrudan
bu kayda tasimak, tamamen basarisiz bir yayinda bile donusumu ilerletir.

## Dogrulanmis durum (her iddia dosya:satir, bu depoda okundu)

| Iddia | Kanit |
|---|---|
| Prompt 1080x1920 30fps istiyor | `canon/MASTER-BLOCK.md` FORMAT bolumu |
| API'ye 720p gidiyor | `tools/gunluk.py:32`, `:148` |
| Kapi 720x1280 BEKLIYOR | `tools/gunluk.py:99` |
| Kapi fps'e bakmiyor | `tools/gunluk.py:94-108` |
| Rota suresi okunmuyor | `tools/gunluk.py:31` `SURE = 15`; `routes/toronto-cn-red-dusk.md:6` `DURATION: 20` |
| Model tavani 15 sn | `routes/vegas-strat-blue-rain-15.md:10` |
| Seedance suresi tamsayiya cevriliyor | `tools/kie_uret.py` `"duration": int(args.n_frames)` |
| Ses normalizasyonu yok | AImagine-Fear altinda hicbir .py'de `loudnorm` yok |
| Hazir cozum var | `core/ffmpeg_tools.py:234` `master_audio`, sidecar `.audio_master.json` yaziyor |
| 80 MB ustu ucuncu transcode | `core/uploader.py:36` `MAX_UPLOAD_MB = 80`, `:101` `_delivery_copy`, `:491` cagriliyor |
| Etiket gonderilmiyor | `core/uploader.py:453` `tags` VAR, `tools/yayinla.py` HIC gecmiyor |
| Mukerrer baslik YouTube'u atliyor | `core/uploader.py:475-488` |
| Baslik kancasiz | `tools/gunluk.py:170` `caption...[0][:95]` |
| Rota alanlari bolumlerden ONCE | `build.py` `load_route` alanlari `## ` gormeden okur; `parse_sections` yalniz `## ` bolumlerini toplar, DURATION'i GOREMEZ |
| Yeni rota ureticisi var | `tools/sehir_ekle.py:85-89` sabit sablonla rota yaziyor |
| Kategori degistirilemez | `core/uploader.py` icinde `category`/`categoryId` HIC YOK -> `RF-ISSUES-FEAR-DUZELT.md` |

## Butun rocklar icin gecerli kurallar

- **Semaya alan/bolum ekleyen her rock TEK commit'te tam goc yapar:** once butun
  veriye (9 rota + `routes/_TEMPLATE.md` + `tools/sehir_ekle.py` sablonu + test
  fixture'lari + README), sonra `build.py` dogrulamasi. Ara adimda
  `build.py --check` KIRMIZI kalmaz.
- **Saf fonksiyon testi tek basina kanit degildir.** Her rock ayrica en az bir
  *baglanti* testi ister: `subprocess`/`upload_to_platform` mock'lanir ve gercek
  sarmalayicinin urettigi TAM argv ya da TAM cagri argumani dogrulanir. Boylece
  `main()` eski satiri saklarsa test kalir.
- **ffmpeg gerektiren test `skip` ile yesil sayilmaz.** Kapanis kanitini ben
  calistiriyorum ve once `ffmpeg -version` dogruluyorum.
- `core/` altindaki hicbir dosya DEGISTIRILMEZ, yalnizca cagrilir.

## Rocklar (bagimlilik sirasinda)

---

### Rock 1: Uretim profili tek yerde, kapi oradan okur (1080p + 30fps)

**Sorun.** Prompt bir sey, API baska sey, kapi ucuncu bir sey soyluyor. Kapi kendi
sabitini dogruladigi icin sapmayi goremez; 1080p'ye gecilirse dogru videoyu "sorunlu"
diye isaretleyip yayini durdurur.

**Done looks like.**
- `tools/gunluk.py` icinde tek `PROFIL` sozlugu:
  `{"cozunurluk": "1080p", "genislik": 1080, "yukseklik": 1920, "fps": 30,
    "fps_tolerans": 1.0, "sure_tolerans": 1.5, "min_bayt": 3_000_000}`.
- API cagrisi ve kapi AYNI sozlukten okur. Iki yerde ayri sayi kalmaz.
- **ffprobe JSON ile okunur** (`-print_format json -show_streams -show_format`) ve
  **video akisi acikca secilir** (`codec_type == "video"`). Duz sozluge cevirme YOK.
  Ses akisinin varligi ayrica kontrol edilir.
- fps `r_frame_rate` kesrinden hesaplanir; `30/1` ve `30000/1001` ikisi de 30 sayilir.
- Cozunurluk varsayilani `1080p`, kapinin bekledigi `1080x1920`. **Ayni commit'te.**
- **`seedance-2`'nin 1080p verip vermedigi BILINMIYOR** (bkz. yukarida B maddesi).
  Plan bu belirsizligi kodda tasiyor, varsayimla kapatmiyor:
  - `--profil 720p` / `--profil 1080p` bayragi: kanarya kotu cikarsa **kod
    degistirmeden** tek bayrakla geri donulur. Bayrak hem API'yi hem kapiyi birlikte
    cevirir, yani ikisi asla ayrisamaz.
  - **Sessiz dusurme yakalanir:** kapi "istenen" ile "gelen"i karsilastirir. 1080p
    istenip 720x1280 dondugunde hata metni bunu acikca soyler
    (`istendi 1080p, geldi 720x1280 , model sessizce dusurdu`), genel bir
    "cozunurluk yanlis" demez.
  - Profil degisikliginden sonraki ILK kosu Rock 1b'nin `--yayinlama` moduyla yapilir:
    uretir, denetler, YAYINLAMAZ. Kanarya bu, ve gunluk kosunun zaten harcayacagi
    krediden fazlasini harcamaz.
- Iki saf fonksiyon ayrilir:
  - `uretim_komutu(slug, sure, profil) -> list[str]` (argv kurar, calistirmaz)
  - `denetle_akislar(probe_json, dosya_boyutu, beklenen_sure, profil) -> list[str]`
  `denetle(video, beklenen_sure, profil)` ffprobe'u cagirip ikincisini sarar.
- **Kanon tutarlilik testi:** `canon/MASTER-BLOCK.md` FORMAT bolumundeki cozunurluk ve
  fps sayilari `PROFIL` ile ayni olmali; degilse test KALIR. (`kie_uret.py`'nin kendi
  varsayilani degismez cunku dort kanalla ortak; bunun yerine `gunluk.py`'nin
  `--resolution`'i HER ZAMAN acikca gecirdigi test edilir.)

**Non-goal.** Video uretmek. Kredi harcamak. `kie_uret.py` varsayilanlarini degistirmek.
Goruntunun kanona ICERIK olarak uydugunu dogrulamak (bkz. Rock 1b).

**Proof.** `python -m pytest AImagine-Fear/tests -q -k "profil or kapi or fps"`
- `uretim_komutu` ciktisinda `--resolution 1080p` VAR (saf test)
- `main()` yolunda `subprocess` mock'lanip AYNI argv gorulur (baglanti testi)
- gercek bir ffprobe JSON fixture'i (video 1080x1920 30/1 + audio 0/0) -> BOS liste
- ayni fixture ama video `24/1` -> fps sorunu (ses akisinin `0/0`'i ezmedigi kanit)
- `30000/1001` -> sorun YOK
- 720x1280 -> cozunurluk sorunu (eski davranis artik HATA)
- 1080p istenip 720x1280 gelince hata metni "sessizce dusurdu" der (sessiz dusurme testi)
- `--profil 720p` verilince HEM argv `--resolution 720p` olur HEM kapi 720x1280 bekler
  (tek bayrak ikisini birden cevirir; ayrisirlarsa test KALIR)
- ses akisi yok -> sorun
- `canon/MASTER-BLOCK.md` ile `PROFIL` uyusmazsa -> test KALIR

---

### Rock 1b: Ilk kosuyu insan onayina bagla

**Sorun.** Teknik kapi 1080x1920/30fps/sesli HERHANGI bir klibi gecirir. Kanona
goruntu olarak uydugunu kanitlamaz. Profil degistigi ilk kosu goz denetimi olmadan
yayinlanmamali. ("Pipeline basarili dedi" kalite kaniti degildir.)

**Done looks like.**
- `tools/gunluk.py --yayinlama`: uretir, denetler, ses master'lar, `kontrol.py`'nin
  kontakt sayfasini `out/<slug>/` altina yazar, **yayinlamaz**, 0 ile ciker ve dosya
  yollarini basar.
- `tools/gunluk.py --dry` **cevrimdisi ve belirlenimci** olur: ag cagrisi yok, kredi
  okumasi yok, ayni-gun kapisindan ONCE calisir. Sirdaki slug, okunan sure, palet ve
  profil satirlarini HER ZAMAN basar. (Su an ayni-gun kapisi `--dry`'dan once
  donuyor ve `--dry` sessizce 0 ile cikabiliyor.)

**Non-goal.** Otomatik goruntu siniflandirmasi, OCR, sahne analizi. Bunlar
`RF-ISSUES-FEAR-DUZELT.md`'de.

**Proof.** `python -m pytest AImagine-Fear/tests -q -k "dry or onay or yayinlama"`
- `--dry` bugun yayin VARKEN bile sure/palet/profil satirlarini basar ve 0 doner
- `--dry` hicbir ag cagrisi yapmaz (`requests` mock'lu, cagrilirsa test KALIR)
- `--yayinlama` `yayinla.py`'yi HIC cagirmaz (mock, cagrilirsa test KALIR)

---

### Rock 2: Rota suresi okunur, model tavaniyla dogrulanir

**Sorun.** `SURE = 15` sabit; 20 ve 25 saniyelik rotalar sessizce kirpiliyor. AMA
sureyi okuyup oldugu gibi gondermek de yanlis: `bytedance/seedance-2` tavani 15 saniye
(`routes/vegas-strat-blue-rain-15.md:10`) ve `kie_uret.py` sureyi `int()` ile ceviriyor.

**Done looks like.**
- Sure `routes/<slug>.md`'den **`build.load_route()` ile** okunur (`parse_sections`
  DEGIL: alanlar ilk `## ` bolumunden once geliyor, `parse_sections` onlari gormez).
  Import icin `KOK` (`AImagine-Fear/`) `sys.path`'e eklenir; betik calistirildiginda
  `sys.path`'e `tools/` giriyor, `AImagine-Fear/` girmiyor.
- **Model sure izin listesi:** `MODEL_SURELERI = {"bytedance/seedance-2": {15}}` ve
  yaninda acik yorum: *bu kume DOGRULANMADI; yalnizca gercekten uretip yayinladigimiz
  sureyi iceriyor. `core/kie_api.py:489`'daki "4-15s" notu `seedance-2-fast`'e ait,
  bu modele DEGIL.* Kesirli, sifir, negatif ve listede olmayan sure **kredi
  harcanmadan ONCE** durur.
- `SIRA` yalniz izin listesindeki sureli rotalari icerir. `toronto-cn-red-dusk` (20),
  `vegas-strat-blue-rain` (20), `vegas-strat-blue-rain-25` (25) donusum havuzundan
  CIKAR. Sebep kod icinde tek satirla yazili: *tavan degil, DOGRULANMAMIS*. Rota
  dosyalari SILINMEZ. Ihsan bir kanarya kosusuyla 20 saniyeyi dogrularsa kume tek
  satirla genisler.
- Okunan sure hem `--n-frames` olur hem kapinin bekledigi sure olur. Sabit `SURE = 15`
  silinir.

**Non-goal.** Rota dosyalarindaki DURATION degerlerini degistirmek. `build.py`'nin
mevcut DURATION dogrulamasina dokunmak. Yeni model eklemek.

**Proof.** `python -m pytest AImagine-Fear/tests -q -k "sure or duration or model"`
- `dubai-burj-altin` -> 15
- `toronto-cn-red-dusk` -> 20 okunur AMA `SIRA`'da YOK
- izin listesi disi sure ile calistirinca sifir API cagrisi (subprocess mock, cagrilirsa KALIR)
- `DURATION` yok / `abc` / `0` / `-5` / `12.5` -> hata, sifir API cagrisi
- `SIRA`'daki HER slug icin okunan sure izin listesinde (donusum havuzu butunlugu)
- `gunluk.py` deponun kokunden VE alakasiz bir cwd'den calistirildiginda import calisir

---

### Rock 3: Yayindan once ses normalizasyonu, ve kapi son dosyayi olcer

**Sorun.** Olculen: Burj Khalifa -15,4 LUFS, Sanghay -16,5 LUFS, TP -3,8/-3,5. Hedef
-14 LUFS / -1 dBTP. Depoda iki gecisli loudnorm hazir ve bu kanal cagirmiyor.

**Done looks like.**
- Sira: **uret -> master'la -> denetle -> yayinla.** Master'lama kapidan SONRA degil
  ONCE gelir, boylece denetlenen dosya ile yayinlanan dosya AYNI dosyadir ve
  `yayinla.py`'nin sha'si o dosyanin sha'sidir.
- Master `out/<slug>/master/` altina yazilir. Ham video kesfi (`*_gunluk_*.mp4` glob'u)
  bu klasoru GORMEZ, yoksa master bir sonraki kosuda ham video sanilip tekrar tekrar
  normalize edilir.
- `core.ffmpeg_tools.master_audio(ham, master, target_i=-14.0, target_tp=-1.0)` cagrilir.
- Teslim edilen degerler **yeniden olculmez**: `master_audio` zaten olcup zorluyor ve
  `<master>.audio_master.json` sidecar'ina yaziyor. Defter o sidecar'in son denemesinden
  okur.
- Sidecar okunamazsa ya da I = -14 +/- 1,0 / TP <= -1,0 disindaysa **YAYIN DURUR**.
- **80 MB kapisi:** master `MAX_UPLOAD_MB` (80) ustundeyse dur ve soyle. Yoksa
  `core/uploader.py:491` `_delivery_copy` denetlenmemis ucuncu bir transcode uretir ve
  yayinlanan dosya denetlenen dosya olmaz.

**Non-goal.** `core/ffmpeg_tools.py`'yi degistirmek. Videoyu yeniden kodlamak
(`master_audio` `-c:v copy` yapiyor, oyle kalsin). `_delivery_copy`'yi degistirmek.

**Proof.** `python -m pytest AImagine-Fear/tests -q -k "ses or loudnorm or master"`
- ffmpeg ile uretilen 2 sn'lik klip (`testsrc2` + `sine`) master'lanir, sidecar'dan
  okunan I -14 +/- 1,0 icinde
- sahte sidecar -30 LUFS -> kapi KALIR
- sidecar dosyasi yok -> kapi KALIR (sessizce gecmez)
- master yolu `*_gunluk_*.mp4` glob'una YAKALANMAZ (klasor ayrimi testi)
- 81 MB'lik sahte master -> kapi KALIR
- ffmpeg yoksa test `skip` olur; kapanis kanitini calistiran BEN once
  `ffmpeg -version` dogrularim, `skip` yesil sayilmaz

---

### Rock 4: YouTube kancasi, etiketleri ve #shorts

**Sorun.** Etiketler YouTube'un otomatik copu; sekiz videodan birinde `#shorts` var;
basliklar 98-99 karakter ve cumlenin ortasinda kesiliyor. `core/uploader.py:453`
etiket parametresini KABUL EDIYOR, `yayinla.py` gecmiyor.

**Done looks like.**
- **Rotalara `TITLE` bolumu.** 2-5 satir, her satir bir baslik varyanti.
  Dogrulama **belirlenimci dilbilgisi**, "anlamli" gibi yoruma acik kural YOK:
  1. satir `#shorts` ile biter,
  2. `#shorts` dahil toplam <= 70 karakter,
  3. `#shorts` ve noktalama atildiktan sonra ilk 40 karakter icinde `LANDMARK`
     alanindaki *ayirt edici kelime* (bas harfleri buyuk yazilmis kelimelerden en
     uzunu, orn. "Burj", "Skytree", "Empire") gecer,
  4. 40. karakter bir kelimenin ortasina denk gelmez (40. ve 41. karakterden en az
     biri bosluk ya da satir sonu),
  5. ayni rotada iki varyant birebir ayni olamaz.
- `build.py` `out/<slug>/TITLE.txt` yazar (mevcut `CAPTION.txt` kalibinda).
- **Varyant secimi ve mukerrer baslik tuzagi.** `core/uploader.py:475-488` ayni basligi
  ikinci kez gorurse YouTube'u ATLIYOR ve `None` donuyor. `gunluk.py` `yayin.jsonl`'de
  kullanilmamis varyanti secer. **Havuz tukendiyse yayin DURUR** ve "bu rotaya yeni
  TITLE varyanti yaz" der. Sessizce eskisini yeniden gondermek yok; `allow_duplicate_title`
  bu rock'ta HIC kullanilmaz (mukerrer korumasi kasitli).
- **Etiketler.** `tools/yayinla.py` `--tags` alir ve `upload_to_platform(..., tags=...)`
  olarak GECIRIR. Etiketler caption'daki `#` etiketlerinden turetilir (`#` atilir,
  virgulle birlesir) , kanon tek kaynak kalir.
- `gunluk.py` basligi `TITLE.txt`'ten alir ve `--tags` gecirir.
- **Donusum yalniz YouTube basarisinda ilerler.** `sonuclar["youtube"]` bos/`None`/hatali
  ise defter kaydi `slug`'i "kullanildi" olarak isaretlemez ve `sirdaki()` ayni rotada
  kalir. (`yayinla.py` basarisiz donmeden ONCE deftere yaziyor; bu yuzden "kullanildi"
  bayragi cikis kodundan degil YouTube sonucundan turetilir.)

**Non-goal.** `canon/CAPTION.md` etiket havuzu (kaynak kanalla ayni kumede kalmak
KASITLI). `canon/NEGATIVES.md` ekran yazisi yasagi. Kategori. `core/uploader.py`.
Basarisiz platformlari tek tek yeniden deneme (-> `RF-ISSUES-FEAR-DUZELT.md`).

**Proof.** `python -m pytest AImagine-Fear/tests -q -k "title or baslik or etiket or tags"`
- 70 karakteri asan satir KALIR; 70 tam GECER (sinir vakasi)
- `#shorts` ile bitmeyen KALIR
- ilk 40 karakterde landmark kelimesi YOKSA KALIR; VARSA gecer (iki yonlu)
- 40. karakter kelime ortasinda -> KALIR
- tek varyant KALIR; iki ayni varyant KALIR
- gecerli rota `out/<slug>/TITLE.txt` uretir
- varyant secici: defter bos -> 1. varyant; 1. kullanilmis -> 2.; hepsi kullanilmis -> DURUR
- `upload_to_platform` mock'lanir, YouTube cagrisindaki `tags` argumani
  TAM OLARAK `"MegaSlideFear,CNTower,WaterSlide,POVReels,CGIAdventure,ViralReels"`
- YouTube `None` donerken IG basarili -> slug "kullanildi" olmaz
- `python AImagine-Fear/build.py --check` YESIL kalir

---

### Rock 5: Palet damgasi (olcum altyapisi)

**Sorun.** Patlayan video (371.000 begeni) sicak altin/amber; olen video (13 izlenme)
doygun macenta neon. Ikisi teknik olarak birebir ayni. Palet hicbir yerde kayitli
degil, yani hipotez OLCULEMEZ.

**Codex bu rock'un KILL edilmesini istedi** (Core Focus'a girmiyor gerekcesiyle).
Reddedildi: Ihsan bu kosuda acikca istedi ve Core Focus buna gore genisletildi.
Ama Codex'in iki teknik itirazi kabul edildi ve rock daralttildi:
donusum "sicak/neon dogru siralanir" iddiasini BIRAKIYOR (3 sicak / 7 neon ile
dairesel olarak saglanamaz) ve yeni rota UYDURMUYOR.

**Done looks like.**
- Rotalara `PALET: sicak` ya da `PALET: neon` alani. `build.py` zorunlu alan yapar ve
  yalniz bu iki degeri kabul eder.
- Dokuz rota etiketlenir. Olculen dagilim: `dubai-burj-altin` (warm gold-amber) ve
  `toronto-cn-red-dusk` (hot red-orange) **sicak**; kalan yedi **neon**.
- `yayin.jsonl` kaydina her yayinda `slug`, `palet`, `rota_suresi`, `cozunurluk`,
  `fps`, `lufs`, `true_peak`, `kullanildi` yazilir. Boylece A/B sonradan olculebilir.
- `SIRA` sicak rotalari mumkun oldugunca esit araliga dagitir. Test **dairesel**
  bakar ve dogruyu iddia eder: iki sicak rota arasindaki neon dizisi uzunluklari
  birbirinden en fazla 1 farkli. ("Ust uste uc ayni palet yok" iddiasi YANLIS ve
  yazilmiyor: 2 sicak / 7 neon ile imkansiz.)

**Non-goal.** Gercek video uretmek ya da Kie'ye tek istek atmak. Mevcut `yayin.jsonl`
satirlarini geriye donuk doldurmak. Yeni sehir ya da yeniden boyanmis rota UYDURMAK
(ucuncu sicak rota Ihsan'in yazacagi ayri bir is -> `RF-ISSUES-FEAR-DUZELT.md`).

**Proof.** `python -m pytest AImagine-Fear/tests -q -k "palet"`
- `PALET` alani olmayan rota `build.py --check`'te KALIR
- `PALET: mor` KALIR
- dokuz rotanin hepsi gecer
- `SIRA` dairesel aralik testi gecer
- defter yazicisi `palet` ve `kullanildi` alanlarini iceren sozluk uretir

---

## Kapanis kapisi (butun rocklar bittikten sonra, BEN calistiririm)

```
ffmpeg -version                               # once bu; yoksa ses testleri skip olur ve kanit sayilmaz
python -m pytest AImagine-Fear/tests -q       # 28 taban + yeni testler, sifir skip
python AImagine-Fear/build.py --check         # 9 rota, temiz
python AImagine-Fear/tools/gunluk.py --dry    # cevrimdisi; slug, sure, palet, profil basar
```

## Sira ve bagimliliklar

```
Rock 1 -> Rock 1b -> Rock 2 -> Rock 3 -> Rock 4 -> Rock 5
```
Hepsi `gunluk.py`'yi degistiriyor; sira sart.

**AYNI COMMIT'TE gitmesi gerekenler (uc cift, biri ilk planda eksikti):**
1. Rock 1: cozunurluk 1080p + kapinin bekledigi 1080x1920. Ayrilirsa yayin durur.
2. Rock 3: master'lama adimi + denetimin/sha'nin son dosyaya bakmasi. Ayrilirsa
   denetlenen dosya ile yayinlanan dosya farkli olur.
3. Rock 4/5: sema gocu (veri + `_TEMPLATE.md` + `sehir_ekle.py` + fixture'lar) +
   `build.py` dogrulamasi. Ayrilirsa `build.py --check` arada kirmizi kalir.

## Dokunulmayacaklar

- `core/` altindaki her sey. Rock 3 ve 4 yalnizca CAGIRIR.
- `canon/NEGATIVES.md:15` ekran yazisi yasagi. 371.000 begeni metinsiz geldi.
- `canon/CAPTION.md` sabit etiket havuzu.
- `tools/kie_uret.py` cuzdan mantigi ve `MIN_KREDI = 700`. Cuzdan dort kanalla ORTAK.
- `yayin.jsonl` mevcut satirlari.
- Diger kanallar: `aimagine/`, `sentinal_ihsan/`, `galactic_experience/`,
  `shadowedhistory/`, `series/`, `AImagine-Train/`.
