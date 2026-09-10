# RF-PLAN-REELYZE , plan (r5 revizyonu)

Tarih: 10 Eylul 2026 (Los Angeles) | Dal: `codex-reelyze`
Kayit: `RF-SAME-PAGE-LOG-REELYZE.md` | Ertelenenler: `RF-ISSUES-REELYZE.md`

## Core Focus

Yayin sinirinda, **gercekten yuklenen baytlar** icin, medya sozlesmesi deterministik
olarak dogrulansin ve ihlalde yayin dursun.

## r4 CLARIFY cevabi , kac kanal

Ayrim su: **bes icerik hatti, dort YouTube kanali.**

| Icerik hatti | YouTube kanali | Durum |
|---|---|---|
| `sentinal_ihsan/unnatural-lab` | sentinal_ihsan | aktif, **referans** (dogru ses) |
| `galactic_experience/event-horizon` | galactic_experiment | aktif |
| `shadowedhistory/flashpoints` | shadowedhistory | aktif |
| `AImagine-Fear` | **aimagine** | aktif, bagimsiz hat |
| `aimagine/next-stop` | **aimagine** | **paused** (I-9) |

`core/config.py:35` dort kanal tanimliyor cunku YouTube hesabi dort. Fear ile next-stop
ayni kanala basiyor. Plan **dort canli hatti** kapsar; next-stop duraklatilmis.
Yayin siniri hepsi icin AYNI cagri: `core.uploader.upload_to_platform()`.

---

## r4'un getirdigi tasarim degisikligi , kapinin yeri

Onceki surumde kapi `_try()` (series_runner.py:329) ve `yayinla.py`'ye ayri ayri
konuyordu. **Yanlis.** `core/uploader.py:491`:
```python
video_path = _delivery_copy(Path(video_path))   # gerekirse SIKISTIRILMIS kopya
```
`_delivery_copy()` yeniden kodlayabilir, yani `_try()` icinde dogrulanan dosya
yuklenen dosya OLMAYABILIR. Ayrica `core/uploader.py:611` (yeniden yukleme yolu)
`_try()`'i ve `yayinla.py`'yi tamamen atlar.

Deponun KENDI ilkesi, `core/uploader.py:44-45`, birebir:
> *"Kapi upload_to_platform icindedir cunku olculen TEK tikanma noktasi orasi
> (cagiranlar: publish_video, series_runner:336)."*

Orada zaten ayni siniftan bir kapi var (mukerrer baslik, 2026-09-02, sebebi de ayni:
ureticiye konan kapiyi elle yayin atliyordu). **Ayni kaliba uyuyoruz.**

---

# FAZ 1 , Aktivasyon on kosullari

## Rock 1: `master_lufs`, iki aktif anlatimli seriye

**Kapsam:** `event-horizon`, `flashpoints`. `unnatural-lab` DEGISMEZ. `next-stop` disarida.

**r4 duzeltmesi , A/B icin mevcut duzenek YETMIYOR.**
`series/experiment.py` izole, yayinlanmayan uretim sunuyor (satir 475, CLI `run`) ve
canli durumu korur. **Ama** `produce_episode()` bible'i canli slug'dan yeniden yukler
ve her kosuda medyayi yeniden uretir. Ayni kaynaklarla alansiz/alanli A/B YAPILAMAZ.

**Teslimat:** acik bible override + **replay harness** , ayni ham video, ayni TTS
dosyasi, ayni muzik dosyasi yeniden kullanilir, sadece `master_lufs` degisir.

**r4 duzeltmesi , olcum yontemi.**
`_music.mp4` muzik-only stem DEGIL, `_narrated.mp4` + muzik karisimidir. Ikisinin
integrated loudness farki dengeyi DOGRUDAN olcmez. (Bu benim r3'teki hatamdi.)
Dogru arac depoda var: **`tools/audio_master_check.py`** , `_window_rms`,
`_median_db`, `_production_bed_pcm`, `_measure_native` ile pencereli RMS analizi.
TTS-etkin pencere yaklasimi **native-sessiz anlatim profiline genisletilir**.

> Neden native-sessiz: `series/bible.py:269` , *"Alan yoksa native ses tamamen
> kapalidir (0.0)."* `unnatural-lab` `narration.native_mix_level: 0.5` tasiyor,
> hedef iki seri TASIMIYOR. `music_volume = 0.50` kalibrasyonu dogal sesin de
> bulundugu bir mikste yapildi; hedef seride miks sadece anlatim + muzik, yani
> ayni 0,50 anlatima karsi ORANTILI OLARAK DAHA YUKSEK.

**Sabit esik (r5 duzeltmesi , mevcut araca hizalandi):**
Onceki taslakta uydurdugum `+3,0 dB` kalibrasyonsuzdu ve `tools/audio_master_check.py`
zaten **1,5 dB** kullaniyor. Ayrica tek basina medyan, kisa sureli kelime maskelemesini
gizler. Iki olcut birden:

| Olcut | Sinir |
|---|---|
| TTS-etkin pencerelerde muzik yataginin **medyan** artisi (tabana gore) | <= **1,5 dB** |
| Ayni pencerelerde **p95** artisi | <= **3,0 dB** |
| Esigi asan pencere **orani** | <= **%5** |

Herhangi biri asilirsa Rock 1 KALIR; `music_volume` veya `native_mix_level` ayrica
ayarlanir. Esikler etiketlenmis dinleme ornekleriyle kalibre edilir ve kalibrasyon
kaniti manifest'e yazilir.

**Done looks like:**
1. Alan eklendi (`series` blogu, `"master_lufs": -14`).
2. Replay harness ile her seri icin taban ve aday, AYNI kaynaklardan.
3. TTS-etkin pencere karsilastirmasi yapildi, +3,0 dB esigi asilmadi.
4. Final: integrated loudness -15,0..-13,0; true peak <= -1,0 dBTP.
5. Kayitli dinleme karari (anlatim anlasilirligi bozulmamis).
6. **Manifest** yazildi: kaynak hash'leri, final hash'leri, olcumler, dinleme karari,
   ve **degismedigi kanitlanan** canli durum hash'leri (series.json, published.json,
   yayin kaydi).
7. `tests/test_rocka_audio_master.py:117` guncellendi (silinmedi), alansiz seri
   davranisinin kapsami ayri testte korundu.

**Proof:** `python -m pytest tests/test_rocka_audio_master.py tests/test_master_true_peak.py tests/test_manifest_ab.py -q`
Manifest testi yukaridaki alanlarin HEPSINI dogrular. **Atlanan zorunlu medya testi
EKSIK sayilir**, gecmis sayilmaz.

## Rock 2: AImagine-Fear masterlenmis artefakt uretimi

**r4 duzeltmesi:** Rock 2 "bagimsiz" degildi, Rock 3/4'un henuz olmayan kapisini
calistiriyordu. **Kapsam daraltildi: sadece ayri masterlenmis dosya uret.**
Tam dogrulama TEK yerde, Rock 4 sinirinda yapilir.

**Done looks like:** `core.ffmpeg_tools.master_audio` cagrilir (I=-14, TP=-1,0, LRA=11),
cikti AYRI dosyaya yazilir, yayina giden yol o dosyayi gosterir.
`sys.path` bootstrap `tools/yayinla.py` ile birebir ayni.
Cozunurluk/fps DEGISMEZ (720x1280, 24 fps olculen gercek).

**Proof:** `AImagine-Fear/tests/test_master_sira.py` (yeni teslimat).
**Girdi BILEREK uyumsuz secilir** (or. -20 LUFS). Assert edilir:
girdi sozlesmeden KALIR; cikti byte/hash olarak girdiden FARKLIDIR; sadece cikti gecer.
(r4: girdi bastan uyumluysa `master_audio` no-op olsa bile test gecerdi.)

---

# FAZ 2 , Sinir kapisi , TEK ATOMIK KABUL BIRIMI

r4: *"Rock 3 ve Rock 4'u tek atomik kabul birimi yap."* Kabul.
Ikisi ayri kabul edilirse Core Focus saglamayan kismi teslimat mumkun olur.

## Rock 3+4 (atomik): sozlesme dogrulayici + yayin sinirina yerlestirme

### 3a , `core/medya_sozlesmesi.py`

| Olcum | Yontem |
|---|---|
| Cozulebilirlik | tam decode, `-xerror`, sifir olmayan cikis = RED |
| Akislar | `-select_streams v:0` / `a:0` |
| Geometri | teslimat profiline gore |
| fps | rasyonel ayristirma + CFR kaniti (ortalama hiz/zaman damgasi) |
| Sure | tolerans sozlesmede |
| Integrated loudness / true peak | EBU R128 |

`dogrula(video, sozlesme) -> {gecti, olcumler, ihlaller, bilinmeyen, sozlesme_surumu}`
Olculemeyen "bilinmeyen"dir ve **fail-closed**. Tamsayi puan yok, boyut vekili yok.

### 3b , Sozlesme kaynaklari (r4)

**Artefakt olcumunden sozlesme TURETMEK YASAK.** Her aktif hat ve teslimat profili
icin depoya kayitli, surumlu sozlesme matrisi. **Sure ve tolerans ACIKCA yazilir**
(r5: validator bunlari zorunlu sayiyordu ama matris gostermiyordu):

| Hat / profil | Geometri | fps | Sure | Tolerans | I | TP |
|---|---|---|---|---|---|---|
| `unnatural-lab` | 1080x1920 | 30 | `duration_band` (bible'da VAR) | +/-1,5 sn | -14 +/-1 | <= -1 |
| `event-horizon` | 1080x1920 | 30 | **plan/politika tabanli** (bible'da YOK) | +/-1,5 sn | -14 +/-1 | <= -1 |
| `flashpoints` | 1080x1920 | 30 | **plan/politika tabanli** (bible'da YOK) | +/-1,5 sn | -14 +/-1 | <= -1 |
| `AImagine-Fear` | 720x1280 | 24 | **sabit 15 sn** | +/-1,5 sn | -14 +/-1 | <= -1 |
| 4K master profili (varsa) | ayri satir | | | | | |

`duration_band` alani sadece `unnatural-lab/bible.json`'da var; diger ikisinde YOK.
Bu yuzden sure kurali onlar icin **artefakttan degil, matristen** gelir.

Factory testi: her hat/profil icin sozlesme uretilebiliyor, alanlari tam, ve
artefakt olcumunden turetilmedigi assert ediliyor.

### 3c , Kapinin yeri

**`core/uploader.py` `upload_to_platform()` icinde, `_delivery_copy()` SONRASI**
(satir 491'den hemen sonra). Mevcut mukerrer-baslik kapisiyla ayni kalip.
Bu tek yerlesim su cagiranlarin HEPSINI kapsar:
`AImagine-Fear/tools/yayinla.py:119`, `series_runner:336` (`_try`), `core/uploader.py:611`.

**r5 duzeltmesi , cagirici gocu TAMAMEN kalkmiyor.** "Tek yerlesim her seyi cozer"
demistim, fazla iddialiydi: cagiricilar hala sozlesmeyi TASIMAK zorunda.
Ama is kuculuyor: cagirici **sadece guvenilir bir sozlesme kimligi/profili** verir
(`contract_id`), matrisi `upload_to_platform` kendi icinde yukler. Boylece cagirici
tarafinda tasinan sey tek bir string.

Atomik gecirilecek cagirilar (dogrudan ve gecisli):
`AImagine-Fear/tools/yayinla.py:119`, `series_runner:336` (`_try`),
`core/uploader.py:611` (yeniden yukleme), ve `publish_video`.
Sozlesme kimligi yoksa **fail-closed durur.**

### 3c-ek , teslimat anlik goruntusu (r5)

**Mevcut hata:** `core/uploader.py:109-111`
```python
delivery = video_path.parent / f"{video_path.stem}_delivery.mp4"
if delivery.exists() and delivery.stat().st_size > 0:
    return delivery
```
Cache anahtari kaynak dosyanin ADI, icerigi degil. Ayni yoldaki kaynak yeniden
uretilirse ONCEKI icerigin delivery kopyasi donuyor ve **yanlis video yukleniyor.**
Bu plandan bagimsiz, canli bir hata.

**Duzeltme:** delivery cache'i **tam kaynak hash'i** ile anahtarlanir.
Dogrulama ve hash'ten sonra **icerik-adresli, degismez bir anlik goruntu** uretilir;
butun POST denemeleri YALNIZ o anlik goruntuyu acar (r5: dosya her retry'da yeniden
aciliyordu, arada kaynak degisirse kanitlanandan farkli baytlar yuklenebilirdi).

Testler: ayni yoldaki kaynak degisince yeniden kodlandigi; dogrulama ile POST
arasinda kaynak mutasyonu olsa bile yuklenen baytlarin anlik goruntu oldugu.

### 3d , Red, siradan hatadan AYRI

**r5 duzeltmesi , tipli sonuc her katmanda tasinmali.** Mevcut kod `if res` ve
`bool(res)` ile basari testi yapiyor; `_publish_part()` `list[str]` donduruyor.
Tipli red bu kontrollerde **basari sayilabilir veya tamamen kaybolabilir.**
Ayristirilmis sonuc tipi butun katmanlara tasinir ve reddin ASLA basari sayilmadigi
uc yerde ayri ayri test edilir: `series`, `Fear` (basari sayaci dahil), `video_monitor`.

Dogrulama reddi tipli `validation_rejected` sonucu dondurur:
- 90 saniyelik ic yeniden deneme yoluna DUSMEZ
- `series/approver.py` `_publish_approved()` (satir 78-79, dokumantasyonu birebir
  *"Basarisizsa part['approved']=True"*) bunu **non-retry hold** olarak isaretler.
  Aksi halde satir 122-124 her workflow kosusunda sonsuza kadar yeniden dener.
- Tanisi saklanir

### 3e , Kanit defteri

- Kesin yol: `analytics_data/sozlesme_kaniti.jsonl` (yeni, `yayin.jsonl`den AYRI)
- `yayin.jsonl`e YAZILMAZ: okuyucular oradaki satirlari yayin gecmisi sayiyor,
  reddedilen deneme rotasyonu ve ayni-gun kilidini tuketmemeli
- **Yazma hatasi yayin-engelleyicidir** (sessizce yutulmaz)
- Ilk yuklemeden ONCE yazilir
- **r5 duzeltmesi , "kalici" iddiasi indirildi.** Yerel JSONL yuklemeden once
  yazilabilir, ama workflow sonundaki git persist basarisiz olursa yayin gerceklesmis
  olur ve kanit kaybolur. Ikisinden biri:
  (a) yuklemeden once basariyla onaylanan dayanikli depoya yaz, ya da
  (b) "kalici" iddiasini kaldir ve **persist basarisizligini AYRI bir kritik ihlal**
  olarak raporla. Bu planda (b) secilir; (a) icin altyapi yok.
- **Tam 64 haneli kucuk-hex sha256.** Fear'in `yayinla.py:46` `sha()` fonksiyonu
  `hexdigest()[:16]` ile kirpiyor; kanitta kirpilmis digest KULLANILMAZ.
  Yuklenen gercek dosyayla birebir eslesme sarti.
- Iki Fear workflow'u ve seri workflow'lari bu dosyayi persist eder

### 3f , Rollout

**Tek atomik rollout, production'da default-ON.** Prose sirasi yeterli degil (r4:
kapi sozlesmeler hazir olmadan canliyi durdurabilir ya da testler gectikten sonra
suresiz kapali kalabilir). Aktivasyon Rock 1 ve Rock 2 bittikten SONRA, tek adimda.

### 3g , `.github/workflows/fear-slide-hazir.yml` ffmpeg kurar
Su an sadece `actions/setup-python@v5`; ffprobe olmadan kapi calisamaz.

### 3h , Mevcut testler ve CI (r5)

Kapi `upload_to_platform` icine girdigi icin **sozlesmesiz uploader cagrisi yapan
mevcut testler kirilir.** En az ikisi: `tests/test_async_upload_confirmation.py` ve
`tests/test_publish_duplicate_gate.py`. Bunlar sozlesmeli fixture'lara gecirilir.

Ayrica r5 taslaginda "kok testleri CI'a ekle" sartini dusurmusum. Geri konuyor:
**adlandirilmis bir CI adimi** kok sozlesme testlerini calistirir
(su an sadece `AImagine-Fear/tests` kosuyor).

**Kabul:** tam test paketi yesil, sadece yeni dosyalar degil.

**Proof:** `tests/test_medya_sozlesmesi.py` + `tests/test_yayin_siniri.py` (ikisi de yeni).

Sozlesme testleri: gecerli dosya gecer; kismen bozulmus fixture `-xerror` ile kalir;
sessiz dosya "bilinmeyen" doner ve GECMEZ; `30000/1001` dogru okunur; VFR CFR kanitini
gecemez; iki profil ayni dosyaya farkli karar verir.

Sinir testleri:
- **POZITIF:** dort canli hattin HER BIRI uzerinden gecerli dosya BASARIYLA yuklenir
  (r4: aksi halde her yuklemeyi engelleyen uygulama da testi gecerdi)
- `_delivery_copy()` yeniden kodlarsa **kodlanmis dosya** dogrulanir, oncesi degil
- gecerli sozlesme + bozuk dosya: yukleyiciye HIC ulasmaz
- sozlesme parametresi yok: durur
- **sozlesmesiz `yayinla.py` negatif testi:** diger korumalar (API anahtari,
  ayni-gun kilidi) BASARIYA mock'lanir, `missing_contract` sonucu ve **sifir ag POST'u**
  assert edilir (r4: aksi halde erken cikis yuzunden kapiya hic ulasmadan gecerdi)
- `validation_rejected` 90 sn yeniden denemeye DUSMEZ; approver'da iki ardisik poll
  testi part'in tekrar denenmedigini dogrular
- reddedilen deneme rotasyonu ve gunluk slotu tuketmez
- kanit defteri yazma hatasi yayini ENGELLER
- kanitta 64 haneli digest var ve yuklenen dosyayla eslesir
- `fear-slide-hazir.yml` ffprobe bulur

---

## Sira

```
Rock 1  ┐
Rock 2  ┘ -> Rock 3+4 (atomik) aktivasyonu
```
Rock 3+4 yazilabilir ve test edilebilir; **zorlama** Rock 1 ve 2 bittikten sonra acilir.

## Dokunulmayacaklar
- `sentinal_ihsan/unnatural-lab` , referans.
- `canon/NEGATIVES.md:15` ekran yazisi yasagi.
- `MIN_KREDI = 700` , bu plan model/cozunurluk/sure hicbirini degistirmiyor.
- `yayin.jsonl` ve onu okuyan rotasyon/gun kilidi mantigi.
- `concurrency: group: kie-uretim`.
- `aimagine/next-stop` , duraklatilmis.
- Mevcut mukerrer-baslik kapisi (`core/uploader.py:44`) , yaninda duracagiz, uzerine degil.
