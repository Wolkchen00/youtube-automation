# RF-PLAN , dort kanalin gunluk otomatik yayini geri gelsin (r4)

**Tarih:** 2026-09-04 · **Surucu:** Claude (Visionary) · **Inceleyen:** Codex (Integrator)
**Revizyon:** r4 , Codex VERDICT: SAME PAGE (tur 4/5). r1'in KOK NEDENI yanlisti (Codex tur-1 yakaladi, duzeltildi).
r2'de ROCK sirasini degistirirken **pytest rock'ini dusurdum** (Codex tur-2 KILL ile
yakaladi, r3'te geri kondu). Iki bagimsiz inceleme hatti (Codex + 14 ajanlik dogrulama
filosu) ayni uc kusuru birbirinden habersiz buldu.

**Ihsan kararlari (2026-09-04, alindi):**
1. Duzeltmeler canli repoya push EDILECEK. Push oncesi Visionary tam diff'i okur ve
   proof'u kendi kosar.
2. Ses duzeltmesi (ROCK A) sirada ONE alinir; Sentinal'in bu geceki kosusunda bir
   680 kredi (3,40 $) daha yanmasin.

## CORE FOCUS (tek cumle)

Dort kanal da her gun otomatik yayin yapsin; yayin durursa sistem YESIL
gostermesin ve durus 24 saat icinde gorunur olsun.

---

## 1. CANLI DURUM (2026-09-04 19:16 UTC olculdu)

| Kanal | Son yayin (RSS) | Sessizlik | Bu geceki slot |
|---|---|---|---|
| shad0wedhistory | 09-03T22:52Z | 0.8 gun | flashpoints 20:30 UTC , **son bolum (25/25)** |
| AImagine | 09-03T21:45Z (ELLE tetiklenmis) | 0.9 gun | fear-slide 13:20 , bugun pytest'te oldu |
| sentinal ihsan | 09-02T17:46Z | **2.0 gun** | unnatural-lab 18:30 , **henuz atesellenmedi** |
| Galactic Experiment | 08-31T21:52Z | **3.9 gun** | event-horizon 16:30 , **19:03'te kostu, YESIL, sifir video** |

Kosu 33909183769 (bugun 19:03, canli kanit):

    🔁 event-horizon: kuyruk 0 < 2 → Gemini part 26-27 yaziyor…
    ⚠️ Ikmal dogrulamasi gecmedi (4. deneme): ["part 26: ardisik iki part ayni family
       degerini kullanamaz (yasak family: 'olcek soku')", ...]
    ❌ event-horizon oto-ikmal basarisiz: ... ilk bolum 26 icin yasak family: 'olcek soku'
    ✅ 'event-horizon' tamamlandi (part 25/25).

Kosu exit 0. **Dorduncu ust uste yesil yalan.**

## 2. r1'IN HATASI

r1: *"konu havuzu bos (`extra_topics: []`)"*. **Yanlis.** `extra_topics` yalnizca Notion
UZANTISIDIR. Asil havuz `series.json -> auto_replenish.topic_pool` icindedir ve doludur:

    event-horizon : 27 konu, kullanilmayan = {14, 24}
    flashpoints   : 27 konu, kullanilmayan = {12, 16}

(`series/replenish.py:410-417` `_topic_pool(cfg)` anahtar olarak `id` okur; kullanim
`plans/partNN.json` icindeki `seed_id`'den olculur.)

## 3. GERCEK KOK NEDEN , family kilidi

`series/replenish.py:1020-1023`: ardisik iki part ayni `family`'yi kullanamaz.

    event-horizon: kalan tohum 14, 24 -> ikisi de family 'olcek soku'
                   part25 (seed_id=13) -> family 'olcek soku'
                   => ilk bolum icin aday listesi BOS
    flashpoints  : kalan tohum 12, 16 -> ikisi de family 'efsane vs kayit'
                   => AYNI TUZAK, bu gece son bolumunu uretip yarin olur

Gemini'ye bos liste sunuluyor; uydurma `seed_id` yaziyor (`999`, `1`, prompt yer
tutucusu `n15-32hex`, hatta uydurma `e26-...` formati), dogrulayici reddediyor,
6 deneme bitiyor. **Kisit matematiksel: Gemini ne kadar iyi olursa olsun cozulmez.**

Daha derin kok: ikmal havuzu YEREL (ikili) kisitla tuketiyor, KURESEL fizibilite
gozetmiyor. Cesitli family'ler erken harcaniyor, dibe ayni family'den tohum birikiyor.

## 4. YESIL YALAN (uc katman)

**(a)** `series/series_runner.py:605-607` `return True`; `main()` (:957-980)
`ok is not True` olmadigi icin exit 0. **Ayni dosyanin :976-978 yorumu "Video CIKMAYAN
her kosu KIRMIZI gorunsun" diyor** , bu dal kendi niyetini ihlal ediyor.

**(b)** `Oto-ikmal` adiminda `shell: bash` YOK -> pipefail yok -> `replenish.py:1734-1736`
`sys.exit(1)`'i `tee`'nin 0'i yutuyor. Kardes `Produce` adiminda VAR (yorumu:
*"tee'nin 0'i python'un exit kodunu maskeliyordu (ROCK 3)"*). Etkilenen bes workflow:
`event-horizon.yml`, `flashpoints.yml`, `unnatural-lab.yml`, `from-scratch.yml`, `next-stop.yml`.

**(c)** `last_run.json` sifir video uretilen kosuda `"outcome":"success"` yaziyor.
Panoyu ve nobetciyi besleyen dosya bu.

## 5. SENTINAL'IN SES KAPISI

Anlatim (TTS) yolu commit 2a83147 ile ILK KEZ calisir hale geldi; ep27 sessizce
ANLATIMSIZ yayinlanmisti, ep28 ilk kez uc katmanli. Uc katman `amix normalize=0`
ile TAVANSIZ toplaniyor. `core/ffmpeg_tools.py:257` sabit 2 dB teslim marji AAC 128k'nin
icerige bagli tepe asimindan (0.4-2.2+ dB) kucuk. Olculen: `I=-14.3 (gecer), TP=+0.1 (kalir)`.

**Part 28 KURTARILAMAZ**: `credits_ledger.json` `episode_spend["unnatural-lab:28"]=680.0`,
asgari tamamlanma 400 > kalan 320; cekimler `output/` gitignore'lu, diskte yok.
Birak `budget_exhausted` olsun. **Hedef: part 29 kapiyi GECSIN.**

---

## 6. ROCK'LAR

**UYGULAMA SIRASI (kritik yol, Codex tur-3):**

    A  ->  C  ->  D  ->  E  ->  B

- **A once** (Ihsan karari): unnatural-lab'in 18:30 slotu HENUZ atesellenmedi;
  duzeltmesiz kosarsa bir 680 kredi daha yanar.
- **C ve D, E3'ten (pipefail) ONCE**: aksi halde bu gece ikmal kirmiziya doner ve
  flashpoints'in HALA GECERLI part 25'i atlanir.
- **B en sona**: Fear Slide'in bugun kalan yayin slotu YOK (13:20 UTC gecti), bu
  yuzden kritik yolda yer kaplamamali. Yarin 13:20'den once yetismesi yeterli.


### ROCK A , master ses tavani gercekten tutsun (SENTINAL, bu gece)

**Neden:** Duzeltme olmazsa bu geceki kosuda part 29 ayni kapida oturur, 3,40 $ daha yanar.

**A1 , miks tarafi (kok).** IKI ayri tavansiz miks asamasi var, **ikisi de** kapatilacak:
- `series/produce.py:600-604` -> `mix_voiceover` (`amix_normalize=bible.master_lufs is None`)
- `core/ffmpeg_tools.py:1088` -> arka plan muzigi eklenirken IKINCI `normalize=0` amix
  (Codex tur-2 bulgusu: r2 yalniz birincisini gormustu)

**Kritik kisit:** Tavan **opt-in** olacak, `amix_normalize=False` / `master_lufs`
yapilandirilmis oldugunda gecilecek. Kosulsuz limiter ANLATIMLI HER SERIYI degistirir.
`mix_background_music` varsayilan ciktisi DEGISMEYECEK; ayri opt-in parametre eklenecek.

**Izolasyon sarti (Codex tur-3, dogrulandi):** Bu degisiklik baska HICBIR canli seriyi
etkilemez, cunku `master_lufs` yalniz `unnatural-lab/bible.json`'da tanimli. Ancak bu
**yalnizca su iki kosul saglanirsa** dogru kalir:
1. yeni `mix_background_music` secenegi **varsayilan olarak KAPALI** olacak;
2. `produce.py` bu secenegi **yalnizca `master_lufs is not None` iken** gecirecek.
Bu iki kosul testle kanitlanacak.

**A2 , teslim tarafi (kapanis).** `core/ffmpeg_tools.py:257` sabit marj yerine olcum
tabanli kendini duzelten dongu: master'la, `measure_audio_loudness` ile olc,
`true_peak > -1.0` ise asimi geri besleyip **DEGISMEMIS premaster'dan YENIDEN** master'la,
en fazla 3 tur, sonra fail-closed. **Her deneme premaster'dan yeniden uretilecek**;
AAC ciktisini geri beslemek kumulatif kayipli kodlama ve olcum kaymasi yaratir
(Codex tur-2). Tamami yerel ffmpeg, **0 kredi**.

**Kritik kisitlar:**
- Kapi (`series/produce.py:745 _verify_audio_master`) GEVSETILMEYECEK.
- Sozlesme sabit: `|I - (-14)| <= 1.0` VE `TP <= -1.0 dBTP`. Limiter'i dusurup
  LUFS'u kapinin disina itmek KABUL EDILMEZ (Codex tur-1).
- `master_lufs` yalniz `sentinal_ihsan/unnatural-lab/bible.json`'da; patlama yaricapi
  bu seriyle sinirli olmali ve bu KANITLANMALI.
- Part 28 kurtarilmayacak.

**PROOF:** yeni `tests/test_master_true_peak.py`, **duzeltmeden ONCE KIRMIZI olmali.**
Repoda zaten sinus tabanli bir test var ve o gecerken gercek hata hayatta kaldi
(Codex tur-1), o yuzden fikstur ffmpeg ile HF yogun / ornekler-arasi tepe ureten uc
katmanli malzeme kuracak. Test hem `TP <= -1.0` hem `|I+14| <= 1.0` iddia edecek.
Ayrica ONCEDEN GECEN bir Unnatural girdisi icin regresyon fikstru eklenecek.
Komut: `python -X utf8 -m pytest tests/test_master_true_peak.py -q`
artı `python -X utf8 -m pytest tests/ -q -k "audio or ses or master or rock1 or byte"`

### ROCK B , Fear Slide test kapisi acilsin (AIMAGINE)

**Neden:** Kanalin TEK otomatik hatti her kosuda ~1 dakikada oluyor. r2'de bu rock
yanlislikla dusmustu (Codex tur-2 KILL).

**Ne yapilacak:** `.github/workflows/fear-slide.yml` "Install dependencies" adimi:
`pip install -r requirements.txt` -> `pip install -r requirements.txt pytest`.
**ROCK B kapsaminda baska hicbir satira dokunma.** (ROCK E4 ayni dosyanin sonuc-yazma
adimini zaten degistirir; bu kisit yalnizca ROCK B icindir , Codex tur-4.)

**Neden `requirements.txt` DEGIL:** o dosyayi depodaki **18** workflow'un HEPSI kuruyor;
dort kanalin butun canli uretim hatlarinin calisma-zamani manifestosu. Sadece-test
bagimliligi oraya konmaz. `continue-on-error: true` de KOYULMAYACAK , test kapisi
kredi korumasidir, kaldirilmaz.

**PROOF:** (a) statik: `python -c` ile `fear-slide.yml` YAML'i parse edilip, pytest'i
CAGIRAN adimdan ONCE gelen bir adimin pytest'i KURDUGU dogrulanacak (yerelde pytest
zaten kurulu oldugu icin sadece pytest kosmak ispat DEGIL , Codex tur-1);
(b) `python -X utf8 AImagine-Fear/build.py --check && python -X utf8 -m pytest AImagine-Fear/tests -q`

### ROCK C , flashpoints bu gece olmesin + Galactic dirilsin (VERI + TEST)

**Neden:** Bolum 3. Iki seri de family kilidinde. flashpoints'in slotu bu gece.

**Ne yapilacak:** Iki `series.json`'da `auto_replenish.topic_pool`'a **en az ucer**
yeni konu. Her girdi TAM olarak: `{"id": <JSON integer>, "topic": <bos olmayan string>,
"family": <o serinin auto_replenish.families listesinden>}`.

Kisitlar (hepsi Codex tur-2'den, dogrulandi):
- `id` JSON integer olacak (`_topic_pool` integer olmayani SESSIZCE atlar, ayni id'yi
  SESSIZCE ezer), hem havuzda hem plan gecmisinde kullanilmamis olacak.
- `family` kanonik listede olacak. `validate_replenish_config` bunu KONTROL ETMIYOR;
  kanonik olmayan family `_unused_topics`'ten gecer ama `replenish.py:1017-1019` veya
  `1063-1065` her uretilen plani reddeder. **Bu yuzden bu rock havuz girdileri icin
  acik bir sema dogrulayicisi EKLEYECEK** (id non-boolean integer ve havuz icinde
  benzersiz, topic bos degil, family kanonik).
  **YERI (Codex tur-3, dogrulandi):** `validate_replenish_config()`,
  `replenish.py:125`; bu fonksiyona `1610-1613`'te ulasiliyor ve Gemini `1670`'te
  cagriliyor, yani dogrulayici kredi harcanmadan ONCE koser.
  **HATA DAVRANISI:** bozuk girdi -> `replenish()` `False` doner, acik canli cagride
  exit 1 olur, **hicbir mutasyon yapilmaz ve SIFIR `_gen_json` cagrisi olur.**
  Not: yeni eklenen id plan gecmisinde de bulunmamalidir, yoksa `_unused_topics()`
  onu eler. Havuzda pozitiflik kurali YOKTUR.
- Yeni konularin family'leri hem yasak family'den hem BIRBIRINDEN farkli olacak
  (yasak: event-horizon 'olcek soku', flashpoints 'efsane vs kayit').
- Konular Ingilizce, birbirinden farkli, dogrulanabilir olgu.
- **flashpoints konulari somut yil/donem icerecek** , `replenish.py:1264-1289`
  title-card zaman-capasi kapisi bunu ariyor (Codex tur-2).
- `total_parts` ve `status` bu rock'ta DEGISTIRILMEYECEK.

**Mevcut testi kirmayacak:** `tests/test_doctrine_gate.py:448-460` iki havuzu da tam
27 girdiye SABITLIYOR (`pool_size` alani). Bu beklenti guncellenecek; tercihen kirilgan
sayim yerine sema + asgari-boyut iddiasina cevrilecek.

**PROOF:** yeni `tests/test_havuz_fizibilite.py`. Kapsam secimi `status == "active"`
DEGIL (event-horizon `completed`, unnatural-lab'in havuzu YOK , Codex tur-2):
**`auto_replenish.enabled` VE integer `topic_pool` yapilandirilmis** seriler secilecek,
event-horizon ve flashpoints ACIKCA kapsanacak. Test sunlari iddia edecek: id'ler
benzersiz ve integer, family'ler kanonik, yasak family disinda en az bir aday var,
ve etkin batch icin gecerli bir TAM SIRALAMA mevcut (yalniz "bir alternatif var"
yeterli degil , Codex tur-2).

**BLOCKING kisit (Codex tur-3):** Sema dogrulamasi DOGRUDAN cagrilarak veya yalniz
`_validate_batch:959`'a baglanarak test EDILEMEZ , orada krediler zaten harcanmis olur.
Test **`replenish()` UZERINDEN** kosacak: bozuk yapilandirma verilecek, `_gen_json`
mock'lanacak, ve su uc sey iddia edilecek: donus `False`, **sifir Gemini cagrisi**,
**sifir durum mutasyonu**.
Komut: `python -X utf8 -m pytest tests/test_havuz_fizibilite.py tests/test_doctrine_gate.py -q`

### ROCK D , family kilidi bir daha kanal oldurmesin (KOD)

**Neden:** ROCK C veriyi tazeler ama kural durur; havuz her seride er ya da gec ayni
sekilde dibe vurur.

**Ne yapilacak:** TEK bir paylasilan "ilk family'yi gevset" karari hesaplanacak ve
**ALTI noktaya birden tutarli uygulanacak** (Codex tur-2: r2 yalniz 900-910'u
degistiriyordu, plan yine 1020-1023'te reddedilirdi. Codex tur-3: iki nokta daha
eksikti):
- `replenish.py:793-797` , **prompt CUMLESI** (Gemini'ye hala "ardisik bolumler asla
  ayni family'yi paylasamaz" diyor; gevseme aktifken bu cumle de kosullanacak) **[tur-3]**
- `replenish.py:799-804` , prompt kurallari
- `replenish.py:824-828` , ilk tohum havuzu kisiti
- `replenish.py:900-910` , aday filtresi
- `replenish.py:1020-1023` , dogrulayici. **Uygulama (Codex tur-3, dogrulandi):**
  yalnizca `i == 0` gecmis karsilastirmasindan muaf tutulacak, sonra `previous_family`
  NORMAL sekilde guncellenecek , boylece batch icindeki sonraki tum komsuluklar
  aynen zorunlu kalir.
- `replenish.py:1588-1591` , terminal tani mesaji; gevseme sonrasi family'yi hala
  "yasak" diye etiketlemesin, ayni paylasilan karara kosullanacak **[tur-3]**

Gevseme SADECE aday listesi baska turlu bos kaliyorsa devreye girer. Havuzda baska
family'den tohum varsa davranis AYNEN korunur.
Gevseme MEVCUT uyari/alarm yolu uzerinden gorunur olacak (yeni CLI kurulmayacak ,
Codex tur-1 KILL); kalici alani ve outbox olayi acikca tanimlanip test edilecek.

**PROOF:** yeni `tests/test_family_kilidi_cikisi.py`. Prompt icerigini kontrol etmek
veya dogrulamayi mock'lamak YETERLI DEGIL (Codex tur-2). Test sunu iddia edecek:
(a) `_validate_batch` kacinilmaz ILK tekrari KABUL eder;
(b) batch icindeki IKINCI ardisik tekrari HALA REDDEDER;
(c) alternatif family varken yasak family SECILMEZ;
(d) gevseme kalici alana yazilir ve outbox olayi uretilir;
(e) **uretilen TAM prompt metni yalnizca ILK tekrara izin verir** , 793-797 cumlesi
    gevseme aktifken celiskili kalmamalidir (Codex tur-3).
artı mevcut `tests/test_rock2_replenish_family.py` yesil kalir.

### ROCK E , yesil yalan bitsin (KOD + WORKFLOW)

**E1 , `--series` ayristiricisi (PARA HATASI, Codex tur-2).**
`series_runner.py:963` `if "--series" in argv:` ad-hoc. Degeri eksik/bos olan cagri
`run_all` yoluna dusuyor ve **alakasiz, parasi odenmis bir bolum uretebiliyor.**
`argparse`'a cevrilecek; eksik/bos slug REDDEDILECEK.

**E2 , `strict_empty` opt-in.** `run_next(..., strict_empty: bool = False)`.
`main()` yalnizca gecerli bir `--series <slug>` ile cagrildiginda `True` gecer.
Oncelik acikca tanimli (Codex tur-2, `completed` iki kurali birden sagliyordu):
- `status` `paused` / `draft` -> **BASARI** (Ihsan bilerek durdurdu, kirmizi yanmaz)
- acikca zamanlanmis, `auto_replenish.enabled`, kuyrugu tukenmis seri -> **BASARISIZLIK**
  + alarm (event-horizon'un tam durumu)
- `awaiting_approval` / `needs_human` / `budget_exhausted` / `qc_retry` -> **ESKISI GIBI**
- **[Codex tur-3, eksik kalan durumlar]** `planned` / `produced` -> kurtarma yolu
  AYNEN korunur (uretime devam edilir, basarisizlik sayilmaz).
  `auto_replenish` KAPALI, sonlu bir serinin `completed` olmasi -> **BASARI**
  (dogal bitis, Ihsan'in tasarimi).
  `next_part`'ta beklenmedik sekilde terminal bir part duruyorsa
  (`published` / `rejected` / `skipped`) -> **fail-closed**, kirmizi.
- `--dry-run` sirasinda strict modda **dis alarm GONDERILMEYECEK** (Codex tur-2)

Varsayilan davranis DEGISMEZ; 12 workflow'un cagirdigi paylasilan sozlesme korunur.

**E3 , pipefail.** Bes workflow'un `Oto-ikmal` adimina `shell: bash`.
Cron saatlerine ve cron yorumlarina DOKUNULMAYACAK.

**E4 , `last_run.json` dogruyu yazsin.** Sonuc dosyasini olusturma isi YAML shell'inden
alinip **test edilebilir bir repo betigine** tasinacak (`scripts/`), ve **ALTI workflow**
o betigi cagiracak (Codex tur-2: Python testi gecerken YAML yazici bozuk kalabilirdi):
`event-horizon.yml`, `flashpoints.yml`, `unnatural-lab.yml`, `from-scratch.yml`,
`next-stop.yml`, **`fear-slide.yml`**.

**BLOCKING (Codex tur-3):** `fear-slide.yml` bugun `last_run.json` yazan ALTINCI
kaynaktir ve **yalniz Instagram yayinlandiginda bile basariyla cikip yesil yaziyor.**
Fear Slide icin kanit alani `yayin.jsonl` -> `results.youtube` olacak.

Betik `outcome=success` yazmadan once **YouTube yayininin dogrulandigini** arayacak;
aksi halde `no_video` yazacak (Codex tur-2 #24/#31'in dar kabulu).
**Kanit BU KOSUYA bagli olacak** , eski/bayat YouTube kaydi basari sayilmayacak (tur-3).

**SIRA KISITI (Codex tur-2):** ROCK C ve ROCK D'nin dogrulayici tarafi, ROCK E3'ten
(pipefail) ONCE gelmelidir. Aksi halde bu gece ikmal kirmiziya doner ve flashpoints'in
HALA GECERLI part 25'i atlanir.

**PROOF:** yeni `tests/test_tukenmis_seri_yesil_degil.py`, **dosya adiyla acik cagri**
(`-k` filtresine guvenilmeyecek , Codex tur-1). CLI cikis kodunu, alarm cagrisini
(ve dry-run'da alarm GONDERILMEDIGINI), yazilan `last_run.json` icerigini,
ve argparse'in bos `--series` degerini reddettigini dogrulayacak.

**E4 icin ek BLOCKING ispat (Codex tur-3):**
(a) **statik baglanti testi:** ALTI workflow'un da sonuc betigini cagirdigi YAML'dan
    dogrulanacak (bir workflow atlanirsa test kirmizi olsun);
(b) **bayat kanit negatif testi:** onceki bir kosudan kalmis YouTube kaydiyla
    `outcome=success` YAZILMADIGI dogrulanacak.
Komut: `python -X utf8 -m pytest tests/test_tukenmis_seri_yesil_degil.py -q`
artı tam paket `python -X utf8 -m pytest tests/ -q`

---

## 7. NON-GOALS (bu cevrimde YAPILMAYACAK) ve REDDEDILEN BULGULAR

- **24 saatlik yayin tazelik kapisi.** Codex bunu ertelenemez sayiyor; Visionary
  KATILMIYOR ve gerekcesini yaziyor: bu kapi `Akilli_Watchdog` AYRI REPOSUNA uzaniyor
  (`work_evidence_checker.py`, `config.py`), koordineli bir teslim gerektirir ve bu
  cevrimin dort kanali BUGUN yayina dondurme isini geciktirir. ISSUES'a, ayri cevrim.
- **Tam "YouTube zorunlu platform" semantigi** (`yayinla.py` tek platform basarisinda
  0 donuyor; event-horizon/flashpoints `required_platforms` bos). ROCK E4 bunun DAR
  halini aliyor (sonuc dosyasi YouTube dogrulanmadan `success` yazmaz). Genis hali
  (uretim hattinin kendisinin kirmizi donmesi) ISSUES'a.
- **Surdurulebilir konu tedariki** (Notion koprusu / havuz besleme). ROCK C bes
  bolumluk pist acar; kalici tedarik Ihsan'in ICERIK karari. ISSUES'a.
- **`_bridge_notion`'i diger uc seriye acmak.** ISSUES'a.
- **Notion'daki 4 "Aday" konu kartini onaylamak.** Icerik karari.
- **`from-scratch` / `next-stop` serilerini geri acmak.** Ihsan bilerek durdurdu.
- **`Akilli_Watchdog` config'i** (`aimagine/from-scratch/last_run.json` yerine
  `AImagine-Fear/last_run.json` izlenmeli). AYRI REPO. ISSUES'a.
- **Pano (`Proje_Dashboard/run.py:727`) tazelik/renk duzeltmesi.** AYRI REPO,
  Visionary kendi yapacak.
- **Part 28'i kurtarmak.**
- **Bos `GEMINI_API_KEY_QC_UNNATURAL_LAB` secret'i.** ISSUES'a.

## 8. KISITLAR

- Bu depo CANLI uretim yapar ve gercek para harcar.
  **Hicbir rock uretim tetiklemez, `gh workflow run` cagirmaz, commit/push yapmaz.**
  Push'u Visionary yapar: tam diff okunur, proof kendi kosulur, sonra push.
- Calisma dizini izole bir git worktree'dir (ana agac baska oturumlarca kullaniliyor).
- Mevcut testler yesil kalmali: `python -X utf8 -m pytest tests/ -q`.
- `.github/workflows/` icindeki **cron saatleri ve cron yorumlari DEGISTIRILMEYECEK**.
- Turkce log/yorum uslubu korunacak; dosyalarda em-dash kullanilmayacak.
- **Her rock'in testi, duzeltmeden ONCE kirmizi olacak sekilde yazilacak.**
  "Gecerken hatayi kaciran test" bu cevrimde uc kez yakalandi; bu kural pazarlik disi.
