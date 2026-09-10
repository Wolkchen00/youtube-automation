# RF-PLAN-FEAR-DUZELT , AImagine-Fear kanalini duzelt

Tarih: 10 Eylul 2026 (Los Angeles)
Dal: `codex-fear-duzelt` (worktree; ana agacta baska oturumlarin islenmemis isi var)
Kaynak analiz: `AImagine-Fear/REELYZE-RAPOR.md`
Taban: 9eec629, `python -m pytest AImagine-Fear/tests -q` = 28 passed (olculdu 07:50 PDT)
Revizyon: **r6** (Codex round 1-5 TAMAMLANDI, 63 bulgunun hepsi islendi , `RF-SAME-PAGE-LOG-FEAR-DUZELT.md`)

## Core Focus (tek cumle)

AImagine-Fear'in urettigi video kanonun soyledigi seyle birebir ayni olsun, YouTube'a
kancasiyla ve etiketiyle ulassin, ve hangi paletle uretildigi olculebilir kalsin.

## Ihsan'in verdigi uc karar

1. Kapsam: hem uretim hatti hem dagitim.
2. Cozunurluk varsayilani SIMDI 1080p olacak. Kredi maliyeti olculmedi, bilerek kabul edildi.
3. Palet testi: kod tarafi kurulur, gercek video uretimini Ihsan tetikler.
   **Hicbir rock para harcayan bir uretim cagrisi calistirmaz.**

---

## Planin dayandigi DORT TEHLIKE (dordu de bu depoda dogrulandi)

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

**D. 30 fps ISTENEMIYOR. Parametre yok, ve model 27/27 kez 24 fps verdi.**
```
yayin.jsonl  -> "fps": 24.0   (27 kaydin 27'si; 30 fps HIC gorulmedi)
tools/kie_uret.py:135-140 seedance govdesi:
    prompt, duration, aspect_ratio, resolution, generate_audio
    ^ fps / frame rate parametresi YOK
```
`canon/MASTER-BLOCK.md` FORMAT bolumu "30 frames per second" diyor ama bu yalnizca
prompt metni; API'de fps kolu yok ve model metni dinlemiyor. Yani **fps istenen degil
GOZLENEN bir ozellik.**

Sonuc: REELYZE raporunun 3. maddesi ("fps 30") oldugu gibi uygulanamaz. Daha da
onemlisi, kapiyi 30'a kurmak **her videoyu dusurur ve kanali tamamen durdurur.**
Bu planda fps profilin GOZLENEN degeri (24) ile dogrulanir, kanon metni de ayni
degeri soyler. 30 fps'e cikmak prompt isi degil model degisikligi isidir -> issue.

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
| **fps istenemiyor** | `tools/kie_uret.py:135-140` seedance govdesinde fps parametresi YOK |
| **27/27 teslim 24 fps** | `yayin.jsonl` -> `"fps": 24.0`, 30 fps HIC yok |
| Onay dosyasi CI'ya tasinmali | `.github/workflows/fear-slide.yml` `persist_state.sh` yalniz `yayin.jsonl` + `last_run.json` tasiyor |
| sha kapisi kosulsuz | `tools/yayinla.py:80-87` basarisiz denemede yazilan sha'yi da blokluyor |
| **CRLF/LF hash tuzagi** | `core.autocrlf=true`, `.gitattributes` YOK; `gunluk.py` calisma agacinda 198 CRLF / 0 yalin LF |

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
  `{"cozunurluk", "genislik", "yukseklik", "beklenen_fps", "fps_tolerans",
    "sure_tolerans", "min_bayt"}`. Varsayilan `1080p`.
- **`beklenen_fps` = 24, 30 DEGIL.** fps istenen degil GOZLENEN bir ozellik (bkz. D):
  API'de fps kolu yok ve model 27/27 teslimde 24 verdi. Kapiyi 30'a kurmak kanali
  durdururdu. Deger degisirse (yeni model, yeni gozlem) profil guncellenir, kapi
  otomatik onu izler.
- **Kanon da bu modulden besleniyor.** `canon/MASTER-BLOCK.md` FORMAT bolumundeki sabit
  "1080x1920, 30 frames per second" metni `<<COZUNURLUK>>` ve `<<FPS>>` token'lariyla
  degistirilir; `build.py` bunlari aktif profilden doldurur (mevcut `TOKEN_FIELDS`
  mekanizmasinin yanina profil token'lari eklenir). Boylece profil degistiginde
  **prompt da degisir**, ve prompt artik hicbir zaman elde edemedigimiz bir fps'i
  ISTEMEZ , uc kaynak (prompt, kapi, gerceklik) ayni sayiyi soyler.
- `tools/gunluk.py` API cagrisini ve kapiyi AYNI profilden besler.
  `--profil {1080p,720p}` bayragi ucunu birden (prompt, API, kapi) birlikte cevirir.
- **ffprobe JSON** okunur (`-print_format json -show_streams -show_format`) ve **video
  akisi acikca secilir** (`codec_type == "video"`). Duz sozluge cevirme YOK. Ses
  akisinin varligi ayrica kontrol edilir.
- fps `r_frame_rate` kesrinden hesaplanir ve `beklenen_fps` ile karsilastirilir;
  `24/1` ve `24000/1001` ikisi de 24 sayilir.
- **Sessiz dusurme ayri bir hata:** 1080p istenip 720x1280 dondugunde mesaj
  `istendi 1080p, geldi 720x1280 , model sessizce dusurdu` der; genel "cozunurluk
  yanlis" demez.
- Saf fonksiyonlar: `uretim_komutu(slug, sure, profil) -> list[str]` ve
  `denetle_akislar(probe_json, dosya_boyutu, beklenen_sure, istenen_profil) -> list[str]`.

**Non-goal.** Video uretmek. `kie_uret.py` varsayilanlarini degistirmek (dort kanalla
ortak). Goruntunun kanona ICERIK olarak uydugunu dogrulamak.

**Proof.** `pytest AImagine-Fear/tests -q -k "profil or kapi or fps"`
- `uretim_komutu` -> `--resolution 1080p` (saf) VE `subprocess` mock'lu `main()` yolunda AYNI argv (baglanti)
- ffprobe JSON fixture (video 1080x1920 `24/1` + audio `0/0`) -> BOS liste
- ayni fixture video `30/1` -> fps sorunu (**ses akisinin `0/0`'i ezmedigi kanit**)
- `24000/1001` -> sorun YOK
- 1080p istenip 720x1280 -> mesajda "sessizce dusurdu" gecer
- `--profil 720p` -> argv `--resolution 720p` VE kapi TAM OLARAK `720x1280` bekler
  (`720x1920` DEGIL; en-boy orani 9:16 sabit) VE `gunluk.py`'nin gercek yolu build'e
  secili profili gecirir, uretilen PROMPT.txt icinde `720x1280` ve `24` gecer
  (uc kaynagin birlikte dondugunun kaniti)
- `canon/MASTER-BLOCK.md` icinde artik sabit `1080x1920` da `30 frames` de YOK,
  `<<COZUNURLUK>>` / `<<FPS>>` var
- ses akisi yok -> sorun

---

## Rock 1b: Yetenek matrisi ve kalici yayin onayi

**Sorun.** (B) modelin sinirlari bilinmiyor, (C) cron kimse bakmadan yayinliyor.
"Ilk kosuyu elle yap" bir prosedur notu; kod bunu zorlamiyor.

**Done looks like.**
- `AImagine-Fear/profil.py` icinde **yetenek matrisi**, anahtar
  `(model, sure, cozunurluk, fps)`, deger `"dogrulandi"` ya da `"kanarya"`.
  **fps anahtarin PARCASI** , 720p kombinasyonu yalniz 24 fps'te gozlendi, 30'da degil:
  ```
  ("bytedance/seedance-2", 15, "720p",  24) : "dogrulandi"  # 27/27 teslim boyle
  ("bytedance/seedance-2", 15, "720p",  30) : "kanarya"     # HIC gorulmedi
  ("bytedance/seedance-2", 15, "1080p", 24) : "kanarya"     # DOGRULANMADI
  ```
  Yaninda acik yorum: *`core/kie_api.py:489`'daki "4-15s / 480p-720p" notu
  `seedance-2-fast`'e ait, bu modele DEGIL.*
- **`"kanarya"` bir kombinasyon YAYINLANAMAZ.** `gunluk.py` uretimden ve krediden ONCE
  bakar; kanarya ise ya `--yayinlama` ister ya da durur. Cron da bu yola girer, yani
  main'e 1080p girse bile ertesi sabah **sessiz yayin olmaz**, kosu acik mesajla durur.
- **Tek ortak anahtar uretici:** `profil.matris_anahtari(model, sure, cozunurluk, fps)`.
  Matrise bakan HER yol (Rock 1b onayi, Rock 2 onkontrolu) bu fonksiyonu cagirir.
  Iki yerde elle demet kurulmaz; aksi halde biri uc elemanli biri dort elemanli anahtar
  uretir ve **butun kombinasyonlar reddedilir.**
- **fps anahtari OLCULEN kesirden degil profilin `beklenen_fps`'inden kurulur.**
  Kapi `24000/1001`'i (= 23,976) tolerans icinde 24 sayiyor; ama matris anahtarina
  olculen degeri koysaydik anahtar `23.976` olur, matriste `24` ararken TUTMAZDI ,
  yani kapi GECER, onay PATLARDI. Anahtar her zaman kanonik `beklenen_fps`.
- **Kayit sema surumu:** `sema_surumu` alani olmayan ya da 1 olan kayitlarda
  `palet`, `caption`, `secilen_baslik`, `etiketler` YOKTUR. Nihai kod bu alanlari
  **dogrudan okumaz**, `uretim_kaydi_bul()` uzerinden geri duser: `palet` rota
  dosyasindan, caption `out/<slug>/CAPTION.txt`'ten, baslik/etiket o anki kanondan
  turetilir (slug kayittan geldigi icin hepsi DOGRU rotaya aittir). Boylece ilk
  commit sirasinda uretilip onaylanmis bir master, Rock 5 kodu yerine gectikten
  sonra da yayinlanabilir.
- **Uretim kaydi**, her uretimde **master sha'si altinda DEGISMEZ** yazilir:
  `out/<slug>/uretim/<master_sha>.json`. Tek bir `uretim.json` OLMAZ , ayni slug icin
  B uretilince A'nin kaniti silinir ve A bir daha ne onaylanabilir ne yayinlanabilirdi.
  Icerik:
  `{sema_surumu, model, istenen_profil, profil_hash, slug, beklenen_sure,
    olculen: {genislik, yukseklik, fps, sure}, denetim_sonucu, master_sha, ts}`
  **`profil_hash` denetim ANINDAKI profildir.** `--onayla` bunun guncel hash ile
  eslesmesini sart kosar; yoksa profil degistikten sonra eski bir
  `denetim_sonucu=basarili` kaydi yeni ayarlari yetkilendirebilirdi.
  Onay ve `--yayinla-mevcut` **yalniz bu kayittan** beslenir.
- **Sema ROCK SINIRLARINDA buyur** (`sema_surumu` alani bunu tasir):
  | Rock | Eklenen alanlar | O asamada `--yayinla-mevcut` metadata kaynagi |
  |---|---|---|
  | 1+1b+3 (ilk commit) | yukaridaki temel alanlar | `out/<slug>/CAPTION.txt`, baslik = caption ilk satiri (BUGUNKU davranis) |
  | 4 | `palet` | ayni |
  | 5 | `caption`, `secilen_baslik`, `etiketler` | **kayittan** |
  Tuketici kendi asamasinda VAR OLAN alanlari okur; ilk commit'in testleri palet ya da
  TITLE istemez (o alanlar henuz yok). Her teslim sinirinda testler gercek rota
  dosyalariyla kosar.
- Onay kalici: `AImagine-Fear/profil_onay.json`. Icerigi: onaylanan
  `(model, sure, cozunurluk, fps)`, onaylanan master'in sha'si, **ve `profil.py`
  iceriginin hash'i.** Profil dosyasi degisirse onay otomatik GECERSIZ olur.
  **Hash satir sonu normalize edilerek hesaplanir** (`\r\n` -> `\n`, sonra sha256).
  Sart, tercih degil: bu depoda `core.autocrlf=true` ve `.gitattributes` YOK
  (`gunluk.py` calisma agacinda 198 CRLF, 0 yalin LF). Ham bayt hash'i Windows'ta
  bir, Linux runner'da baska cikar; onay CI'da **kalici olarak gecersiz** olur ve
  cron her sabah yayini reddeder.
  Ihsan kanaryayi gozle gordukten sonra `--onayla <master>` calistirir; komut once
  uretim kaydini dogrular (denetim GECMIS mi, model ayni mi, sha tutuyor mu),
  sonra kombinasyonu `"dogrulandi"` yapar.
- **Onay CI'ya nasil ulasiyor:** `profil_onay.json` depoya islenen bir dosyadir ve
  cron'un checkout ettigi dalda bulunmalidir. `--onayla` dosyayi yazdiktan sonra
  Ihsan'in commit'lemesi gerektigi acikca basilir. Ayrica
  `.github/workflows/fear-slide.yml`'deki `persist_state.sh` listesine eklenir ki
  kosu onu dusurmesin. (Su an liste yalniz `yayin.jsonl` ve `last_run.json` tasiyor.)
- `tools/gunluk.py --yayinlama`: uretir, **master'lar, denetler**, `kontrol.py`
  kontakt sayfasini **kosuya ozel yeni bir yola** yazar
  (`out/<slug>/kontakt/<master_sha>.png`), YAYINLAMAZ, yollari basar.
  Dosyanin gercekten olustugu ve boyutunun > 0 oldugu dogrulanir; olusmadiysa kosu
  BASARISIZ. Kosuya ozel yol sart: `kontrol.py` ffmpeg cikis kodunu yok sayiyor, ve
  sabit bir yolda onceki kosudan kalan dolu bir PNG yeni basarisizligi gizlerdi.
- `tools/gunluk.py --yayinla-mevcut <master>`: onaylanmis bir master'i uretim yapmadan
  yayinlar. **Slug `sirdaki()`'den DEGIL o master'in uretim kaydindan** gelir; yoksa
  siradaki rota degistiginde onaylanmis videoya baska rotanin metadata'si takilirdi.
  Caption/baslik/etiket kaynagi yukaridaki sema tablosuna gore: ilk commit'te
  `out/<slug>/CAPTION.txt` (slug kayittan geldigi icin yine DOGRU rota), Rock 5'ten
  sonra dogrudan kayittan. Sha `profil_onay.json` ile eslesmezse durur.

**REDDEDILEN (Codex round 3):** "her videonun kendi SHA onayi zorunlu olsun".
Bu, gunluk otomatik kanali bitirir , kanal bugune kadar zaten insansiz kosuyor ve
720p'de de oyleydi, yani bu degisiklik YENI bir risk getirmiyor. Ayirim su:
**profil onayi teknik bir izindir** (bu kombinasyon calisiyor mu), **video onayi ayri
bir urundur** (bu video iyi mi) ve o issue #6'da (anlamsal kapi). Per-video sha
baglamasi yalnizca `--yayinla-mevcut` yolunda zorunlu.
- `tools/gunluk.py --dry` **cevrimdisi ve belirlenimci**: ag cagrisi yok, kredi okumasi
  yok, ayni-gun kapisindan ONCE calisir, slug + sure + profil + matris durumu basar.

**Sira notu.** Rock 1b'nin `--dry` ciktisinda palet YOKTUR; palet Rock 4'te eklenir ve
kendi testiyle gelir.

**Non-goal.** Otomatik goruntu siniflandirmasi, OCR, sahne tespiti -> issue.

**Proof.** `pytest AImagine-Fear/tests -q -k "matris or onay or dry or yayinlama"`
- kanarya kombinasyonu + yayin yolu -> DURUR, `upload_to_platform` HIC cagrilmaz (mock)
- kanarya kombinasyonu + `--yayinlama` -> uretim yolu calisir, yayin cagrilmaz
- `profil_onay.json` dogru kombinasyonu tasiyorsa yayin yolu ACILIR
- **onay reddi vakalari, her birinde SIFIR uretim VE SIFIR yayin cagrisi:**
  dosya YOK / JSON BOZUK / kombinasyon YANLIS / `profil.py` hash'i ESKI /
  uretim kaydinda `denetim_sonucu` BASARISIZ / uretim kaydindaki model FARKLI
- `--yayinla-mevcut` sha uyusmazsa DURUR
- `--yayinla-mevcut` metadata'yi uretim kaydindan alir: `sirdaki()` BASKA bir slug
  donduruyorken bile dogru caption/TITLE/palet gider ve **uretim cagrisi yapilmaz**
- kontakt sayfasi olusmazsa `--yayinlama` BASARISIZ doner (ffmpeg sahte basarisizligi)
- **onceki kosudan kalan dolu bir kontakt PNG'si varken yeni ffmpeg basarisizligi
  yine yakalanir** (kosuya ozel yolun kaniti; sabit yol olsaydi test gecerdi)
- taze bir checkout'ta (gecici dizine kopyalanan depo) ayni `profil_onay.json` yuklenir
  ve yayin yolu acik kalir (CI kaniti)
- **`profil.py`'nin CRLF ve LF kopyalari AYNI hash'i verir; gercek bir icerik
  degisikligi FARKLI hash verir** (autocrlf tuzaginin kaniti)
- **ayni matris anahtari iki yerde elle kurulmaz:** Rock 2 onkontrolu ile Rock 1b
  onayi ayni `matris_anahtari()` ciktisini kullanir; ayni model/sure/cozunurlukte
  fps 24 GECER, fps 30 KALIR (gercek preflight yolundan)
- **ayni slug icin A sonra B uretilir; A'nin kaydi hala okunur ve A yayinlanabilir**
  (degismez kayit kaniti; tek `uretim.json` olsaydi test KALIRDI)
- uretim kaydindaki `profil_hash` guncel profille uyusmuyorsa `--onayla` REDDEDER
- **uctan uca `24000/1001` vakasi:** boyle bir video kapiyi GECER **ve** ayni kosuda
  `--onayla` BASARIR (anahtar kanonik 24'ten kuruldugunun kaniti; olculen kesirden
  kurulsaydi kapi gecer onay patlardi)
- **`sema_surumu: 1` kayit + nihai kod -> `--yayinla-mevcut` DOGRU metadata ile
  yayinlar** (palet rotadan, caption CAPTION.txt'ten); alan eksik diye patlamaz
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
- Kesirli, sifir, negatif sure ve matriste karsiligi olmayan kombinasyon **kredi
  harcanmadan ONCE** durur. Anahtar **`profil.matris_anahtari(...)` ile kurulur**,
  elle demet YAZILMAZ , Rock 1b ile ayni dort elemanli anahtar (fps DAHIL) kullanilir.
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
- Defter kaydi (`yayin.jsonl`) su alanlari tasir. **Her alanin kaynagi ayri ve
  acikca tanimli** , "hepsi master'dan olculur" demek yanlisti, cunku slug ve palet
  medya olcumu degil:

  | Alan | Kaynak |
  |---|---|
  | `slug`, `palet`, `rota_suresi` | uretim kaydi, **`uretim_kaydi_bul(master_sha)` ile** (`out/<slug>/uretim/<master_sha>.json`) |
  | `cozunurluk`, `fps`, `sure` | denetlenen master'in ffprobe olcumu |
  | `lufs`, `true_peak` | `<master>.audio_master.json` sidecar'i |
  | `kullanildi` | YouTube yanitindan cikarilan yayin kimligi |
- **`kullanildi` yalnizca DOGRULANMIS YouTube yayinindan turetilir:** yanit truthy
  olmasi YETMEZ, icinden bir `post_id` / `publication_id` / video kimligi cikarilabilmeli.
  Cikarilamazsa `kullanildi=false`.
- `sirdaki()` ve **ayni-gun kapisi** artik `kullanildi=true` satirlara bakar, satirin
  varligina degil. Boylece basarisiz bir yayin donusumu ilerletmez ve ayni-gun kapisini
  tetiklemez.
  **Sinirli iddia:** `yayinla.py`'nin sha kapisi (`tools/yayinla.py:80-87`) basarisiz
  denemede de yazilmis sha'yi KOSULSUZ engellemeye devam ediyor. Yani ayni dosyanin
  yeniden gonderimi hala bloke; duzelen yalnizca ayni-gun kapisi ve donusum. Tam
  platform-bazli tekrar issue #5'te ertelendi ve bu plan onu cozdugunu IDDIA ETMIYOR.
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
[Rock 1 + Rock 1b + Rock 3]  ->  Rock 2  ->  Rock 4  ->  Rock 5
        (TEK COMMIT)
```
Hepsi `gunluk.py`'yi degistiriyor; sira sart.
Rock 4, Rock 5'ten ONCE cunku TITLE varyant secimi `kullanildi` semantigine dayaniyor.

**AYNI COMMIT'TE gitmesi gerekenler:**
1. **Rock 1 + Rock 1b + Rock 3 birlikte.** Bu uclu ayrilamaz:
   - Rock 1 tek basina giderse 1080p varsayilani main'e duser ama kapi henuz yok ->
     **ara surumde cron acigi yeniden acilir** ve ertesi sabah dogrulanmamis profille
     yayin yapilir. (Codex round 3 bulgusu; onceki surumde bu ucu ayri commit'lerdi.)
   - Rock 1b'nin `--yayinlama` akisi master'lamaya, yani Rock 3'e muhtac.
   Bu yuzden profil + kanon token'lari + kapi + yetenek matrisi + onay + master'lama
   TEK commit.
2. Rock 4 ve 5: sema gocu (veri + `_TEMPLATE.md` + `sehir_ekle.py` + fixture'lar) +
   `build.py` dogrulamasi, her biri kendi icinde atomik.

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
