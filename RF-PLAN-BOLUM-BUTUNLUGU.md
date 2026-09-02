# RF-PLAN: Sentinal bolum butunlugu denetimi + senaryo gercekciligi

## Core Focus (tek cumle)

unnatural-lab motoru, bolum birlestikten SONRA kendi ciktisina bakip "bu bolum
formatin sozunu tutuyor mu?" sorusunu kendisi yanitlasin; bugun sessizce gecen
kusurlar bir daha sessiz gecmesin.

## Neden simdi (2026-09-02 kaniti)

Part 27 bugun uc platforma da yayinlandi ama IKI kusuru vardi ve ikisini de
motor degil, ben elle indirip izleyerek buldum:

1. **Loop kapanmadi.** Cekim 4 QC'den gecemeyip dustu; o cekim formatin kapanis
   halkasiydi (acilis kadrajina donup dongulu bitirecekti). Video kasik havada,
   farkli kadrajda aniden bitiyor. Part kaydinda yalnizca
   `dropped_shots: [4], dropped_shot_roles: {"4": "loop_seam"}` var; hicbir yerde
   "bu bolumun LOOP'U YOK" yazmiyor.
2. **Anlatim hic cikmadi.** `shorten_narration_for_duration` emekli modele
   (`gemini-2.0-flash`) 404 verdi, bolum muzik-only yayinlandi. Telegram alarmi
   dustu ama PART KAYDINDA iz yok: `series.json` part 27 kaydinda anlatimin
   eksik oldugunu soyleyen tek bir alan bile yok. Yarin bakan biri bunu goremez.

Yani: cekim-basi QC saglam, ama BOLUM SEVIYESINDE denetim YOK. Bugun var olan
bolum-sonrasi adimlar yalniz teslimat sesine bakiyor
(`_verify_native_audio_delivery` -> `critic.qc_audio`) ve master seviyesine
(`_verify_audio_master`). Ikisi de "bolum formatin sozunu tutuyor mu" sorusunu
sormuyor.

## Devralinan ders: Shorts_Dizi_Fabrikasi `brain/coherence_qc.py`

Mini dizi motoru tam bu sorunu cozmus: bolum birlestikten sonra kendi ciktisini
dinleyip yapisini inceleyen bir SELF-REVIEW. Oradaki alti denetimin dogrudan
karsiligi:

| coherence_qc kontrolu | unnatural-lab karsiligi |
|---|---|
| 1. Konusma tam bitiyor mu | **BIZDE YOK** -> ROCK 1 |
| 2. Replik dusurulmus mu | kismen var (`dropped_shots`) |
| 3. Sahneler baglaniyor mu | var (ortam id + sureklilik kapisi) |
| 4. Beklenmeyen konusma | var (`native_audio_review.unwanted_speech`) |
| 5. Sureklilik metni dogru mu | var ve DAHA GUCLU (`state_carry` birebir linter) |
| 6. Kadro eksik mi | yok, bu seride kadro yok (yalniz eller) |

Ve en onemli tasarim ilkesi: **BLOKLAMAZ, rapor uretir.** Kanal nefes almaya
devam eder, kusur gorunur olur. Bu plan o ilkeyi aynen aliyor.

## Higgsfield incelemesi: cogu UYGULANMAZ, ikisi ogretici

`presets_show` ile gercek preset aciklamalari okundu (web sayfasi yalniz isim
veriyor). Sonuc durustce: **viral presetlerin neredeyse tamami bu formata TERS.**
ORBIT 360, EARTH ZOOM, SELFIE TWIN, ACTION FIGURE, RED CARPET, paparazzi, K-pop
sahneleri: hepsi (a) bir INSAN/karakter etrafinda kurulu, (b) agir KAMERA
HAREKETI iceriyor. unnatural-lab ise olculmus kararlarla yuzu kadraj disinda
tutuyor (`require_no_face: true`), kadraji kilitliyor, ve ekipman kelimeleri
serinin EN BUYUK tek red sebebi. Bu presetleri uygulamak kazanan formati bozardi.

Ogretici olan ikisi, preset olarak DEGIL gramer olarak:

- **ICE STATUE**: "kristal kiragi seni buz heykeline cevirir, KIYAFETIN gercek
  kumas kalir." Tek malzeme donusumu + neyin gercek kaldiginin acikca yazilmasi.
- **CLAY FIGURINE**: "eller seni hamur gibi sikar, HER GOCUK YERINDE KALIR."
  Kalici iz = bizim `state_carry` kuralimizin ta kendisi.

Ikisi de serinin ZATEN uyguladigi grameri dogruluyor. Yeni kural gerekmiyor,
ve dogrulama bunu tesyid etti: ROCK 3 bu yuzden KILL edildi (asagida).

## Non-goals

- Higgsfield viral presetlerini seriye sokmak. Format kilitli kadraj ve yuzsuz;
  presetler karakter ve kamera hareketi uzerine kurulu.
- Kadraj/kamera kurallarini gevsetmek.
- Bolumu BLOKLAMAK. Denetim rapor uretir, yayini durdurmaz (kanal 5 gun
  karanlik kaldi; sessiz kusur kotu, kapali kanal daha kotu).
- Diger uc kanalin davranisini degistirmek. Her sey opt-in.
- Paylasilan planner prompt'unu degistirmek (golden testler bayt-sabit tutuyor).

## Kisitlar

- Python 3.11, mevcut bagimliliklar. Yeni paket yok.
- Denetim UCRETSIZ olmali: ffmpeg + yerel hesap. Ek Gemini cagrisi YOK
  (kota zaten bu kanalin dar bogazi).
- Turkce log/alarm metni, mevcut usluba uygun.
- Em dash kullanilmayacak.
- Degisebilecek dosyalar: `series/produce.py`, `series/critic.py`,
  `series/series_meta.py`, `series/series_runner.py`, `tests/`,
  `sentinal_ihsan/unnatural-lab/bible.json`.

---

## ROCK 1: Bolum butunlugu raporu (deterministik, ucretsiz)

**Done looks like:** bolum birlestikten ve post-process bittikten SONRA, yayindan
ONCE, deterministik bir rapor uretilir ve part kaydina yazilir. Alanlar:

- `loop_closed` (bool): planin SON cekimi bolumde var mi. Dustuyse false.
- `narration_delivered` (bool | null): seri anlatim bekliyorsa, final master'da
  anlatim gercekten var mi. Beklemiyorsa null.
- `arc_roles_missing` (list): dusen cekimlerin rolleri (cold_open, probe,
  escalation, loop_seam).
- `duration_s` (float) ve `duration_in_band` (bool): olculmus kazanan bant
  14-41 sn (workflow basligindaki canli YouTube olcumu, n=148).
- `degraded` (bool): yukaridakilerden herhangi biri kusurluysa true.

**Neden deterministik:** hepsi zaten elimizde olan veriden hesaplanir
(`dropped_shots`, `narration_ok`, `ffprobe` suresi). Tek bir API cagrisi
gerekmez, dolayisiyla Gemini kotasini yakmaz.

**BLOKLAMAZ.** `degraded=true` bolumu durdurmaz; part kaydina yazilir ve
BASARILI yayindan sonra tek bir Telegram alarmi neyin eksik oldugunu soyler.

**Dikkat:** `narration_ok` bilgisi bugun `_post_process` icinde yerel; disari
cikarilmali. `ProduceResult` uzerinde tasinip runner'da kaydedilmeli (bugun
`dropped_shots` icin kurulan yol ayni yol).

**Proof:** `python -m pytest tests/test_episode_coherence.py -q` (yeni). Vakalar:
(a) dort cekim tam + anlatim var -> `degraded=false`, `loop_closed=true`;
(b) cekim 4 dusmus -> `loop_closed=false`, `arc_roles_missing` icinde
`loop_seam`, `degraded=true`; (c) cekim 1 dusmus -> `cold_open` eksik;
(d) anlatim beklenip uretilememis -> `narration_delivered=false`;
(e) anlatimsiz seri -> `narration_delivered` null, `degraded` bundan etkilenmez;
(f) sure banttan tasmis -> `duration_in_band=false`;
(g) part kaydina yazilan alanlar BASARILI yayin sonrasi olusur, basarisiz
yayinda part `published` olmaz.

---

## ROCK 2: KILL , loop kapanisi kare benzerligiyle OLCULEMEZ

Bu rock "ilk kare ile son kareyi karsilastir, benzerlik esigin altindaysa loop
kirik say" diyordu. Plan esigi uydurmayi yasaklayip CANLI VERIYLE kalibre
edilmesini sart kosuyordu. Kalibrasyon yapildi ve HIPOTEZI CURUTTU.

Olcum (yayinlanmis videolar YouTube'dan indirildi, 64x114 gri tonlama, ilk kare
ile son karenin ortalama mutlak farki; 0 = ayni, 255 = zit):

| Bolum | Loop durumu | Ilk-son fark |
|---|---|---|
| part 22 (vKus2kyMIN0) | SAGLAM, dort cekim tam | **65.66** |
| part 27 (dnsKT8eTWMo) | KIRIK, cekim 4 dustu | **21.29** |

Loop'u KIRIK olan bolum, saglam olandan DAHA BENZER cikti. Onerilen olcut iki
bolumu TERS siniflandirirdi.

Sebep, formatin kendi kuralinda: kadraj butun bolum boyunca KILITLI. Dolayisiyla
ilk-son piksel farki loop kapanisini degil, OBJENIN NE KADAR DEGISTIGINI olcer.
part 22'de limon dramatik bicimde donustugu icin fark buyuk; part 27 cekim 3'te
bittigi ve o kare acilisa benzedigi icin fark kucuk. Kilitli kadrajli bir
formatta ham piksel farki yanlis alettir.

Anlamli bir "loop gercekten kapandi mi" olcumu ancak GORME denetimi ister; o da
Gemini kotasi harcar ve kota bu kanalin bilinen dar bogazidir (plan non-goal'u).

**Karar: KILL.** Loop icin guvenilir ve ucretsiz sinyal, ROCK 1'in deterministik
"planin son cekimi bolumde var mi" kontrolüdur. Kanit burada birakiliyor ki ayni
fikir yeniden onerilmesin.

---

## ROCK 3: KILL , senaryo gercekciligi kurallari ZATEN zorunlu

Bu rock, higgsfield gramerini (adlandirilmis tek donusum + neyin gercek kaldigi
+ kalici iz) senaryo olcutu olarak eklemeyi oneriyordu ve "yeni kural icat etme,
once linterin neyi kapsadigini DOGRULA" diyordu. Dogrulama yapildi: ucu de
zaten zorunlu.

| Higgsfield grameri | unnatural-lab'da nerede zorunlu |
|---|---|
| Adlandirilmis tek donusum (ICE STATUE) | `object_card.anomaly_descriptor` en az 10 kelime VE her cekim prompt'unda birebir gecmeli (`shots.py`) |
| Neyin gercek kaldigi yazili | `descriptor` her cekimde birebir; ayrica `shots.py:182` dort cekimin de `environment` degerini `object_card.environment`'a esitler |
| Kalici iz (CLAY FIGURINE) | `state_carry` cekim 1-3'te zorunlu, bir sonraki cekimin prompt'unda BIREBIR gecmeli, son cekimde YASAK |

Eklenecek tek parca sandigim "dort cekim ayni ortami kullanmali" kurali
`series/shots.py:182`'de zaten var:

    if env_id and shot.get("environment") != env_id:
        errors.append(f"cekim {number} environment tam {env_id!r} olmali")

**Karar: KILL.** Senaryo gercekciliginin KURAL tarafi kapali. Gercek eksik
kurallarda degil, modelin urettigi ICERIKTE: ikmal Gemini'si bu kurallari
saglayan metin yazmakta zorlaniyor. O sorun ayri bir madde olarak
`ISSUES.md`'de zaten kayitli (kismi kabul + alan onarimi ile hafifletildi, kok
neden cekim 1'in "anomali zaten suruyor" kuralinin modeli olumsuz kurmaya
itmesi). Ayni isi ikinci kez yazmak deger uretmez.

## Kabul kaniti (unit testler YETMEZ)

1. `python -m pytest tests/ -q` -> 0 failed.
2. Canli veriyle geriye donuk kontrol: part 22 (loop saglam, anlatimli) ve
   part 27 (loop kirik, anlatimsiz) uzerinde denetim CALISTIRILIR ve
   part 27 icin `degraded=true`, `loop_closed=false`,
   `narration_delivered=false` uretmelidir. Denetim gecmisi dogru okumuyorsa
   gelecegi de okumaz.
3. Bir sonraki gercek kosuda part kaydinda yeni alanlar gorunur.
