# RF-PLAN-FEAR-DUZELT , AImagine-Fear kanalini duzelt

Tarih: 10 Eylul 2026 (Los Angeles)
Dal: `codex-fear-duzelt` (worktree; ana agacta baska oturumlarin islenmemis isi var)
Kaynak analiz: `AImagine-Fear/REELYZE-RAPOR.md`
Taban: 9eec629, `python -m pytest AImagine-Fear/tests -q` = 28 passed (olculdu 07:50 PDT)
Revizyon: **r3** (Codex round 1 + round 2, 43 bulgu islendi , `RF-SAME-PAGE-LOG-FEAR-DUZELT.md`)

## Core Focus (tek cumle)

AImagine-Fear'in urettigi video kanonun soyledigi seyle birebir ayni olsun, YouTube'a
kancasiyla ve etiketiyle ulassin, ve hangi paletle uretildigi olculebilir kalsin.

## Ihsan'in verdigi uc karar

1. Kapsam: hem uretim hatti hem dagitim.
2. Cozunurluk varsayilani SIMDI 1080p olacak. Kredi maliyeti olculmedi, bilerek kabul edildi.
3. Palet testi: kod tarafi kurulur, gercek video uretimini Ihsan tetikler.
   **Hicbir rock para harcayan bir uretim cagrisi calistirmaz.**

---

## Planin dayandigi UC TEHLIKE (uctu de bu depoda dogrulandi)

**A. ffprobe duz sozluge cevrilince ses akisi videonun fps'ini eziyor.**
Canli olcum, gercek bir yayinlanmis video:
```
codec_type=video   r_frame_rate=24/1
codec_type=audio   r_frame_rate=0/0
```
`denetle()` su an `dict(re.findall(...))` yapiyor, sonraki akis oncekini eziyor.
Naif bir fps kapisi HER videoda yanlis kalirdi.

**B. `bytedance/seedance-2`'nin sure ve cozunurluk sinirlari BILINMIYOR.**
```
core/kie_api.py:481   resolution: str = "720p"
core/kie_api.py:483   model: str = "bytedance/seedance-2-fast"     <- FAST varyanti
core/kie_api.py:489   "Seedance duration is an integer 4-15s; resolution 480p/720p"
AImagine-Fear/tools/gunluk.py:30   MODEL = "bytedance/seedance-2"  <- FAST DEGIL
```
"4-15s" ve "480p/720p" **`seedance-2-fast`'i** belgeliyor. Bu kanal fast OLMAYAN modeli
cagiriyor ve onun sinirlari depoda hicbir yerde yazili degil.
`routes/vegas-strat-blue-rain-15.md:10`'daki "tavani 15 saniye" notu da ayni karisikligin
urunu; **guvenilmez**. Bugune kadar KANITLANMIS tek kombinasyon:
`(seedance-2, 15 sn, 720p)` , cunku yayinlanan her video bu.
`(seedance-2, 15 sn, 1080p)` **kanitlanmadi** ve bu kosuda varsayilan yapiliyor.

**C. Zamanlanmis kosu insan olmadan yayinliyor.**
`.github/workflows/fear-slide.yml`: `cron: '20 13 * * *'` (06:20 Los Angeles) ->
`python AImagine-Fear/tools/gunluk.py` -> uret, denetle, YAYINLA.
Yani 1080p varsayilani main'e girerse **ertesi sabah kimse bakmadan dogrulanmamis bir
profille yayin yapilir.** Bu yuzden "ilk kosuyu elle yap" bir prosedur notu olarak
YETMEZ; kodda kalici bir onay durumu olmali.

---

## Dogrulanmis durum (her iddia dosya:satir)

| Iddia | Kanit |
|---|---|
| Prompt 1080x1920 30fps istiyor | `canon/MASTER-BLOCK.md` FORMAT |
| API'ye 720p gidiyor | `tools/gunluk.py:32`, `:148` |
| Kapi 720x1280 BEKLIYOR, fps'e bakmiyor | `tools/gunluk.py:94-108` |
| Rota suresi okunmuyor | `tools/gunluk.py:31`; `routes/toronto-cn-red-dusk.md:6` `DURATION: 20` |
| Seedance suresi tamsayiya cevriliyor | `tools/kie_uret.py` `"duration": int(args.n_frames)` |
| Ses normalizasyonu yok | AImagine-Fear altinda hicbir .py'de `loudnorm` yok |
| Hazir cozum + sidecar | `core/ffmpeg_tools.py:234` `master_audio`, `.audio_master.json` |
| 80 MB ustu denetimsiz transcode | `core/uploader.py:36` `MAX_UPLOAD_MB = 80`, `:101`, `:491` |
| Etiket gonderilmiyor | `core/uploader.py:453` `tags` VAR, `tools/yayinla.py` gecmiyor |
| Mukerrer baslik YouTube'u atliyor | `core/uploader.py:475-488` |
| Baslik karsilastirmasi noktalama/emoji/buyuk-kucuk ATIYOR | `core/utils.py:119` `normalize_title` = `re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()` |
| Rota alanlari bolumlerden ONCE | `build.py` `load_route`; `parse_sections` alanlari GOREMEZ |
| Yeni rota ureticisi var | `tools/sehir_ekle.py:85-89` |
| Zamanlanmis yayin var | `.github/workflows/fear-slide.yml` cron 13:20 UTC |
| Kategori degistirilemez | `core/uploader.py`'de `category` YOK -> issue |

---

## Butun rocklar icin gecerli kurallar

- **Semaya alan/bolum ekleyen her rock TEK commit'te tam goc yapar:** once butun veri
  (9 rota + `routes/_TEMPLATE.md` + `tools/sehir_ekle.py` sablonu + test fixture'lari
  + README), sonra `build.py` dogrulamasi. Ara adimda `build.py --check` KIRMIZI kalmaz.
- **Saf fonksiyon testi tek basina kanit degildir.** Her rock ayrica *baglanti* testi
  ister: `subprocess` / `upload_to_platform` mock'lanir ve gercek sarmalayicinin
  urettigi TAM argv ya da TAM cagri argumani dogrulanir.
- **Bos gecen test kanit degildir.** Bir kume uzerinde donen her iddia once kumenin
  BOS OLMADIGINI dogrular (bkz. Rock 4 `SIRA` testi).
- **ffmpeg gerektiren test `skip` ile yesil sayilmaz.** Kapanis kanitini calistiran BEN
  once `ffmpeg -version` dogrularim ve `pytest` ciktisinda sifir `skipped` ararim.
- **Kredi harcayan cagridan ONCE butun onkontroller biter:** profil onayi, sure izni,
  TITLE havuzu, etiket turetimi, caption/TITLE varligi. Onkontrol hatasi asla
  uretimden SONRA patlamaz.
- `core/` altindaki hicbir dosya DEGISTIRILMEZ, yalnizca cagrilir ve okunur.

---

## Rock 1: Uretim profili tek gercek kaynak (prompt + API + kapi)

**Sorun.** Prompt bir sey, API baska sey, kapi ucuncu bir sey soyluyor. Kapi kendi
sabitini dogruladigi icin sapmayi goremez.

**Done looks like.**
- Yeni paylasilan modul `AImagine-Fear/profil.py`:
  `PROFILLER = {"1080p": {...}, "720p": {...}}`, her biri
  `{"cozunurluk", "genislik", "yukseklik", "fps", "fps_tolerans", "sure_tolerans",
    "min_bayt"}`. Varsayilan `1080p`.
- **Kanon da bu modulden besleniyor.** `canon/MASTER-BLOCK.md` FORMAT bolumundeki sabit
  "1080x1920, 30 frames per second" metni `<<COZUNURLUK>>` ve `<<FPS>>` token'lariyla
  degistirilir; `build.py` bunlari aktif profilden doldurur (mevcut `TOKEN_FIELDS`
  mekanizmasinin yanina profil token'lari eklenir). Boylece profil degistiginde
  **prompt da degisir** ve "kanona aykiri video uretme" kacisi kapanir.
- `tools/gunluk.py` API cagrisini ve kapiyi AYNI profilden besler.
  `--profil {1080p,720p}` bayragi ucunu birden (prompt, API, kapi) birlikte cevirir.
- **ffprobe JSON** okunur (`-print_format json -show_streams -show_format`) ve **video
  akisi acikca secilir** (`codec_type == "video"`). Duz sozluge cevirme YOK. Ses
  akisinin varligi ayrica kontrol edilir.
- fps `r_frame_rate` kesrinden hesaplanir; `30/1` ve `30000/1001` ikisi de 30.
- **Sessiz dusurme ayri bir hata:** 1080p istenip 720x1280 dondugunde mesaj
  `istendi 1080p, geldi 720x1280 , model sessizce dusurdu` der; genel "cozunurluk
  yanlis" demez.
- Saf fonksiyonlar: `uretim_komutu(slug, sure, profil) -> list[str]` ve
  `denetle_akislar(probe_json, dosya_boyutu, beklenen_sure, istenen_profil) -> list[str]`.

**Non-goal.** Video uretmek. `kie_uret.py` varsayilanlarini degistirmek (dort kanalla
ortak). Goruntunun kanona ICERIK olarak uydugunu dogrulamak.

**Proof.** `pytest AImagine-Fear/tests -q -k "profil or kapi or fps"`
- `uretim_komutu` -> `--resolution 1080p` (saf) VE `subprocess` mock'lu `main()` yolunda AYNI argv (baglanti)
- ffprobe JSON fixture (video 1080x1920 `30/1` + audio `0/0`) -> BOS liste
- ayni fixture video `24/1` -> fps sorunu (**ses akisinin `0/0`'i ezmedigi kanit**)
- `30000/1001` -> sorun YOK
- 1080p istenip 720x1280 -> mesajda "sessizce dusurdu" gecer
- `--profil 720p` -> argv `--resolution 720p` VE kapi 720x1280 bekler VE uretilen
  PROMPT.txt icinde `720x1920`... yani profilin cozunurlugu gecer (uc kaynak birlikte doner)
- `canon/MASTER-BLOCK.md` icinde artik sabit `1080x1920` YOK, `<<COZUNURLUK>>` var
- ses akisi yok -> sorun

---

## Rock 1b: Yetenek matrisi ve kalici yayin onayi

**Sorun.** (B) modelin sinirlari bilinmiyor, (C) cron kimse bakmadan yayinliyor.
"Ilk kosuyu elle yap" bir prosedur notu; kod bunu zorlamiyor.

**Done looks like.**
- `AImagine-Fear/profil.py` icinde **yetenek matrisi**, anahtar
  `(model, sure, cozunurluk)`, deger `"dogrulandi"` ya da `"kanarya"`:
  ```
  ("bytedance/seedance-2", 15, "720p")  : "dogrulandi"   # yayinlanan her video bu
  ("bytedance/seedance-2", 15, "1080p") : "kanarya"      # DOGRULANMADI
  ```
  Yaninda acik yorum: *`core/kie_api.py:489`'daki "4-15s / 480p-720p" notu
  `seedance-2-fast`'e ait, bu modele DEGIL.*
- **`"kanarya"` bir kombinasyon YAYINLANAMAZ.** `gunluk.py` uretimden ve krediden ONCE
  bakar; kanarya ise ya `--yayinlama` ister ya da durur. Cron da bu yola girer, yani
  main'e 1080p girse bile ertesi sabah **sessiz yayin olmaz**, kosu acik mesajla durur.
- Onay kalici ve versiyonlu: `AImagine-Fear/profil_onay.json`, iceriginde onaylanan
  kombinasyon ve onaylanan master'in sha'si. Ihsan kanaryayi gozle gordukten sonra
  bu dosyayi yazar (tek komut: `--onayla <master>`), kombinasyon `"dogrulandi"` olur.
- `tools/gunluk.py --yayinlama`: uretir, **master'lar, denetler**, `kontrol.py`
  kontakt sayfasini `out/<slug>/` altina yazar, YAYINLAMAZ, yollari basar.
  **Kontakt sayfasinin gercekten olustugu ve boyutunun > 0 oldugu dogrulanir**
  (`kontrol.py` ffmpeg cikis kodunu yok sayip var olmayan bir yol dondurebiliyor);
  olusmadiysa kosu BASARISIZ.
- `tools/gunluk.py --yayinla-mevcut <master>`: onaylanmis bir master'i uretim yapmadan
  yayinlar. Boylece kanarya videosu cope gitmez ve "onayladigim video degil, ertesi
  gun uretilen baska video yayinlandi" tuzagi kapanir. Sha, `profil_onay.json`'daki
  onayla eslesmezse durur.
- `tools/gunluk.py --dry` **cevrimdisi ve belirlenimci**: ag cagrisi yok, kredi okumasi
  yok, ayni-gun kapisindan ONCE calisir, slug + sure + profil + matris durumu basar.

**Sira notu.** Rock 1b'nin `--dry` ciktisinda palet YOKTUR; palet Rock 4'te eklenir ve
kendi testiyle gelir.

**Non-goal.** Otomatik goruntu siniflandirmasi, OCR, sahne tespiti -> issue.

**Proof.** `pytest AImagine-Fear/tests -q -k "matris or onay or dry or yayinlama"`
- kanarya kombinasyonu + yayin yolu -> DURUR, `upload_to_platform` HIC cagrilmaz (mock)
- kanarya kombinasyonu + `--yayinlama` -> uretim yolu calisir, yayin cagrilmaz
- `profil_onay.json` dogru kombinasyonu tasiyorsa yayin yolu ACILIR
- `--yayinla-mevcut` sha uyusmazsa DURUR
- kontakt sayfasi olusmazsa `--yayinlama` BASARISIZ doner (ffmpeg sahte basarisizligi)
- `--dry` bugun yayin VARKEN bile alanlari basar, 0 doner, `requests` HIC cagrilmaz

---

## Rock 2: Rota suresi okunur, matrisle dogrulanir

**Sorun.** `SURE = 15` sabit; 20/25 saniyelik rotalar sessizce kirpiliyor. Ama sureyi
okuyup oldugu gibi gondermek de yanlis: modelin sinirlari bilinmiyor (B) ve
`kie_uret.py` sureyi `int()` ile ceviriyor.

**Done looks like.**
- Sure `routes/<slug>.md`'den **`build.load_route()` ile** okunur (`parse_sections`
  DEGIL: alanlar ilk `## `'den once geliyor). Import icin `KOK` `sys.path`'e eklenir;
  betik calistirildiginda `sys.path`'e `tools/` giriyor, `AImagine-Fear/` girmiyor.
- Kesirli, sifir, negatif sure ve matriste karsiligi olmayan `(model, sure, cozunurluk)`
  **kredi harcanmadan ONCE** durur.
- `SIRA` yalniz matriste `"dogrulandi"` ya da `"kanarya"` karsiligi olan sureli
  rotalari icerir. `toronto-cn-red-dusk` (20), `vegas-strat-blue-rain` (20),
  `vegas-strat-blue-rain-25` (25) havuz DISINDA. Sebep kod icinde tek satir:
  *tavan degil, DOGRULANMAMIS.* Rota dosyalari SILINMEZ; kanarya sonrasi matrise tek
  satir eklenince geri gelirler.
- Sabit `SURE = 15` silinir.

**Proof.** `pytest AImagine-Fear/tests -q -k "sure or duration or model or sira"`
- `dubai-burj-altin` -> 15; `toronto-cn-red-dusk` -> 20 okunur AMA `SIRA`'da YOK
- matris disi sure -> sifir API cagrisi (subprocess mock, cagrilirsa KALIR)
- `DURATION` yok / `abc` / `0` / `-5` / `12.5` -> hata, sifir API cagrisi
- **`SIRA` bos DEGIL, tekrar ICERMEZ ve acikca tanimlanan aktif rota kumesine TAM ESIT**
  (yalniz "listedekiler izinli" demek bos listeyle de gecerdi)
- `gunluk.py` deponun kokunden VE alakasiz bir cwd'den calistirildiginda import calisir

---

## Rock 3: Ses normalizasyonu, ve kapi son dosyayi olcer

**Sorun.** Olculen -15,4 ve -16,5 LUFS; hedef -14 / -1 dBTP. Depoda hazir loudnorm var,
bu kanal cagirmiyor.

**Done looks like.**
- **Tek dogru sira: uret -> master'la -> denetle -> yayinla.** Denetlenen dosya ile
  yayinlanan dosya AYNI dosya olur ve `yayinla.py`'nin sha'si o dosyanin sha'sidir.
  (Rock 1b'nin `--yayinlama` modu da bu siraya uyar.)
- Master `out/<slug>/master/` altina yazilir. Ham video glob'u (`*_gunluk_*.mp4`) bu
  klasoru GORMEZ, yoksa master ertesi kosuda ham video sanilip tekrar normalize edilir.
- `core.ffmpeg_tools.master_audio(ham, master, target_i=-14.0, target_tp=-1.0)`.
- Teslim degerleri **yeniden olculmez**: `master_audio` olcup zorluyor ve
  `<master>.audio_master.json` yaziyor. Defter o sidecar'in son denemesinden okur.
- Sidecar okunamazsa ya da I = -14 +/- 1,0 / TP <= -1,0 disindaysa **YAYIN DURUR**.
- **Boyut kapisi esigi sabitlenmez:** `core.uploader.MAX_UPLOAD_MB` **oradan okunur** ve
  ayni bayt hesabi (`st_size / (1024*1024)`) kullanilir. Asilirsa dur; yoksa
  `core/uploader.py:491` `_delivery_copy` denetlenmemis ucuncu bir transcode uretir.

**Proof.** `pytest AImagine-Fear/tests -q -k "ses or loudnorm or master or boyut"`
- ffmpeg ile 2 sn'lik klip (`testsrc2` + `sine`) master'lanir, sidecar'dan okunan I -14 +/- 1,0
- sahte sidecar -30 LUFS -> KALIR; sidecar YOK -> KALIR (sessizce gecmez)
- master yolu `*_gunluk_*.mp4` glob'una YAKALANMAZ
- `MAX_UPLOAD_MB` monkeypatch ile 1'e cekilince kucuk dosya bile KALIR (esigin
  gercekten core'dan okundugunun kaniti, sabit 80 olsaydi gecerdi)
- **cagri sirasi baglanti testi:** `master_audio` -> `denetle` -> `upload_to_platform`
  tam bu sirada cagrilir

---

## Rock 4: Palet damgasi ve defter semasi

**Sorun.** Patlayan video sicak altin/amber; olen video doygun macenta neon; ikisi
teknik olarak birebir ayni. Palet hicbir yerde kayitli degil, hipotez OLCULEMEZ.
Ayrica `sirdaki()` yalniz `slug` VARLIGINA bakiyor ve `yayinla.py` **basarisiz donmeden
ONCE deftere yaziyor**, yani tam basarisiz yayin bile donusumu ilerletir.

**Done looks like.**
- Rotalara `PALET: sicak|neon` alani, `build.py` zorunlu kilar ve yalniz bu ikisini kabul eder.
- Dokuz rota etiketlenir: `dubai-burj-altin` ve `toronto-cn-red-dusk` **sicak**, kalan
  yedi **neon**.
- Defter kaydi (`yayin.jsonl`) su alanlari **denetlenen master'dan olculen gercek
  degerlerle** tasir: `slug`, `palet`, `rota_suresi`, `cozunurluk`, `fps`, `lufs`,
  `true_peak`, `kullanildi`.
- **`kullanildi` yalnizca DOGRULANMIS YouTube yayinindan turetilir:** yanit truthy
  olmasi YETMEZ, icinden bir `post_id` / `publication_id` / video kimligi cikarilabilmeli.
  Cikarilamazsa `kullanildi=false`.
- `sirdaki()` ve **ayni-gun kapisi** artik `kullanildi=true` satirlara bakar, satirin
  varligina degil. Boylece basarisiz bir yayin ne donusumu ilerletir ne de ayni gun
  guvenli tekrari engeller.
- `yayinla.py`'nin **cikis kodu** dogrulanmis YouTube yayinina baglanir (su an herhangi
  bir platform basarisi 0 dondurüyor; YouTube dusup IG gecince workflow "basarili"
  gorunuyor ve Core Focus ihlali alarm uretmiyor).
- **Geriye uyumlu okuma:** eski `yayin.jsonl` satirlarinda `kullanildi` YOK. Alan
  yoksa `results.youtube` icinden dogrulanmis basari cikarilir. Geriye donuk dosya
  yazimi YOK, yalnizca okuma uyumu.
- `--dry` ciktisina palet eklenir.

**Non-goal.** Yeni sehir ya da yeniden boyanmis rota UYDURMAK (ucuncu sicak rota
Ihsan'in isi -> issue). Mevcut `yayin.jsonl` satirlarini yeniden yazmak. Platform
basina yeniden deneme (-> issue).

**Palet dagilimi hakkinda durust not.** Rock 2 sonrasi aktif `SIRA`'da **tek** sicak
rota kaliyor (`dubai-burj-altin`; `toronto` 20 saniyelik oldugu icin havuz disi).
Bu yuzden bu rock **hicbir donusum aralik iddiasinda BULUNMAZ** , oyle bir test
bos gecerdi. Rock yalnizca dogru etiketleme ve telemetridir. Gercek A/B, ikinci bir
desteklenen sicak rota yazildiginda baslar (issue #7).

**Proof.** `pytest AImagine-Fear/tests -q -k "palet or defter or kullanildi"`
- `PALET` yok -> `build.py --check` KALIR; `PALET: mor` -> KALIR
- **dokuz slug -> PALET eslemesi birebir dogrulanir** (yalniz "hepsi geciyor" demek yetmez)
- defter kaydi butun alanlari tasir ve degerler **sahte olculumlerle birebir eslesir**
  (sabit/eksik kalirsa KALIR)
- YouTube yaniti truthy ama kimliksiz -> `kullanildi=false`
- YouTube `None` + IG basarili -> `kullanildi=false` VE `yayinla.py` sifir DISI doner
- `kullanildi=false` satir varken ayni-gun kapisi yayini ENGELLEMEZ
- eski satir (`kullanildi` alani yok, `results.youtube` dolu) -> dogrulanmis sayilir

---

## Rock 5: YouTube kancasi, etiketleri ve #shorts

**Sorun.** Etiketler YouTube'un otomatik copu; sekiz videodan birinde `#shorts` var;
basliklar 98-99 karakter, cumle ortasinda kesiliyor. `core/uploader.py:453` etiket
parametresini KABUL EDIYOR, `yayinla.py` gecmiyor.

**Done looks like.**
- **Rotalara `TITLE_KEYWORD` alani ve `TITLE` bolumu.**
  `TITLE_KEYWORD` kancada gecmesi zorunlu kelimedir ve rota yazari secer
  (`Burj Khalifa` -> `Burj`, `Empire State Building` -> `Empire`). Otomatik "en uzun
  buyuk harfli kelime" kurali KULLANILMAZ , Burj Khalifa icin `Khalifa`, Empire State
  Building icin `Building` secerdi.
- `TITLE` bolumu 2-5 satir, her satir bir varyant. Belirlenimci dogrulama:
  1. `#shorts` ile biter,
  2. `#shorts` dahil toplam <= 70 karakter,
  3. ilk 40 karakter icinde `TITLE_KEYWORD` gecer,
  4. 40. karakter kelime ortasina denk gelmez (40. ve 41. karakterden en az biri bosluk),
  5. **varyantlar `core.utils.normalize_title` ile karsilastirildiginda farkli olmali**
     , birebir esitlik YETMEZ, cunku uploader noktalama, emoji ve buyuk-kucuk harfi
     atiyor (`core/utils.py:119`) ve normalize-esit iki varyant kapida carpisir.
- `build.py` `out/<slug>/TITLE.txt` yazar.
- **Varyant secimi.** `gunluk.py` `yayin.jsonl`'de (`kullanildi=true` satirlarda)
  **normalize edilmis** haliyle kullanilmamis varyanti secer. Havuz tukendiyse
  **YAYIN DURUR** ve "bu rotaya yeni TITLE varyanti yaz" der. `allow_duplicate_title`
  HIC kullanilmaz.
- **Havuz tukenmesi ve butun metadata onkontrolu KREDI HARCAMADAN ONCE calisir.**
  Yoksa her gun once uretilir, para gider, sonra baslik yuzunden durulur.
- **Etiketler.** `tools/yayinla.py` `--tags` alir ve `upload_to_platform(..., tags=...)`
  olarak GECIRIR. Etiketler caption'daki `#` etiketlerinden turetilir , kanon tek kaynak.
- `gunluk.py` basligi `TITLE.txt`'ten alir ve `--tags` gecirir.

**Non-goal.** `canon/CAPTION.md` etiket havuzu. `canon/NEGATIVES.md` ekran yazisi
yasagi. Kategori. `core/` altinda hicbir sey.

**Proof.** `pytest AImagine-Fear/tests -q -k "title or baslik or etiket or tags"`
- 70 karakter GECER, 71 KALIR (sinir, iki yonlu)
- `#shorts` ile bitmeyen KALIR
- ilk 40'ta `TITLE_KEYWORD` yoksa KALIR, varsa gecer (iki yonlu)
- 40. karakter kelime ortasinda -> KALIR
- tek varyant KALIR
- **`"STRAT Tower Drop! #shorts"` ve `"strat tower drop #shorts"` -> normalize esit,
  KALIR** (birebir farkli olduklari halde)
- havuz tukenmis -> DURUR **ve `subprocess` uretim cagrisi HIC yapilmaz** (onkontrol kaniti)
- dokuz rotanin `TITLE_KEYWORD`'u kendi TITLE varyantlarinin ilk 40 karakterinde gecer
- `upload_to_platform` mock'lanir, YouTube cagrisindaki `tags` argumani TAM OLARAK
  `"MegaSlideFear,CNTower,WaterSlide,POVReels,CGIAdventure,ViralReels"`
- `build.py --check` YESIL

---

## Kapanis kapisi (BEN calistiririm)

```
ffmpeg -version                               # yoksa ses testleri skip olur, kanit sayilmaz
python -m pytest AImagine-Fear/tests -q       # 28 taban + yeni; SIFIR skipped
python AImagine-Fear/build.py --check         # 9 rota temiz
python AImagine-Fear/tools/gunluk.py --dry    # cevrimdisi; slug, sure, palet, profil, matris
```

## Sira ve bagimliliklar

```
Rock 1 -> Rock 1b -> Rock 2 -> Rock 3 -> Rock 4 -> Rock 5
```
Hepsi `gunluk.py`'yi degistiriyor; sira sart.
Rock 4, Rock 5'ten ONCE cunku TITLE varyant secimi `kullanildi` semantigine dayaniyor.

**AYNI COMMIT'TE gitmesi gerekenler:**
1. Rock 1: profil + kanon token'lari + kapi. Ayrilirsa prompt ile uretim ayrisir ya da yayin durur.
2. Rock 1b: yetenek matrisi + yayin yolu kapisi. Ayrilirsa cron dogrulanmamis profille yayinlar.
3. Rock 3: master'lama + denetimin/sha'nin son dosyaya bakmasi.
4. Rock 4 ve 5: sema gocu (veri + `_TEMPLATE.md` + `sehir_ekle.py` + fixture'lar) + `build.py` dogrulamasi.

## Dokunulmayacaklar

- `core/` altindaki her sey. Yalnizca cagrilir ve okunur.
- `canon/NEGATIVES.md:15` ekran yazisi yasagi. 371.000 begeni metinsiz geldi.
- `canon/CAPTION.md` sabit etiket havuzu.
- `tools/kie_uret.py` cuzdan mantigi ve `MIN_KREDI = 700`. Cuzdan dort kanalla ORTAK.
- `yayin.jsonl` mevcut satirlari (yalniz okuma uyumu, yazma yok).
- Diger kanallar: `aimagine/`, `sentinal_ihsan/`, `galactic_experience/`,
  `shadowedhistory/`, `series/`, `AImagine-Train/`.
- `.github/workflows/fear-slide.yml` , kod degismeden davranisi degisiyor (kanarya
  kapisi). Yorumundaki "720p" satiri Rock 1'de guncellenir, mantigi degismez.
