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

Ikisi de serinin ZATEN uyguladigi grameri dogruluyor. Yeni kural gerekmiyor;
ROCK 3 bunu senaryo denetimine olcut olarak yaziyor.

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

## ROCK 2: Loop kapanisi OLCULUR (kare benzerligi)

**Done looks like:** son cekim yerindeyse, bolumun ILK karesi ile SON karesi
ffmpeg ile cikarilip yapisal olarak karsilastirilir; benzerlik esigin altindaysa
`loop_closed=false` yazilir. Boylece "cekim 4 uretildi ama acilis kadrajina
donmedi" durumu da yakalanir, sadece "cekim dustu" degil.

**Neden ayri rock:** ROCK 1 cekimin VARLIGINA bakar, bu rock KALITESINE bakar.
Part 27'de cekim dustugu icin ROCK 1 yeterdi; ama cekim uretilip loop'u yine de
kapatmadigi durum daha sinsi ve olculmeden gorulmez.

**Yontem:** ffmpeg ile iki kare PNG'ye alinir, kucultulup gri tonlamaya
indirilir ve ortalama mutlak fark hesaplanir. Esik CANLI VERIYLE kalibre
edilir: yayinlanmis bir bolumun (part 22, loop'u saglam) ve part 27'nin
(loop'u kirik) degerleri olculup esik ikisinin arasina konur. Esik uydurulmaz.

**Dikkat:** hook_teaser acikken bolumun basina ayri bir kesit ekleniyor ve ILK
KARE degisiyor. unnatural-lab'da `hook_teaser.enabled=false`, ama olcum
teaser'dan ONCEKI gövde uzerinden yapilmali ki teaser acilirsa olcum bozulmasin.

**Proof:** `python -m pytest tests/test_loop_seam.py -q` (yeni). Vakalar:
(a) ayni kare iki kez -> benzerlik tam, `loop_closed=true`;
(b) tamamen farkli iki kare -> `loop_closed=false`;
(c) esik, canli olculmus part 22 ve part 27 degerlerinin ARASINDA;
(d) kare cikarilamazsa denetim `null` doner ve bolumu DUSURMEZ (fail-open,
    cunku bu bir kalite raporu, teslimat kapisi degil).

---

## ROCK 3: Senaryo gercekciligi olcutu (ikmal denetimine ek)

**Done looks like:** ikmalin urettigi plan, mevcut sert dogrulamaya EK OLARAK
uc gercekcilik olcutunden gecer. Ucu de deterministik, LLM cagrisi yok:

1. **Tek donusum yazili mi:** `object_card.anomaly_descriptor` var ve en az 10
   kelime (bugunku kural) VE cekim promptlarinda birebir geciyor (bugunku
   kural). Bu ICE STATUE grameridir: donusum ADLANDIRILMIS olmali.
2. **Neyin gercek kaldigi yazili mi:** her cekim prompt'unda objenin kimligini
   koruyan `descriptor` birebir geciyor (bugunku kural) VE ortam tarifi
   degismiyor: dort cekimin `environment` degeri AYNI id.
3. **Kalici iz zinciri:** cekim 1-3'te `state_carry` var ve bir sonraki cekimde
   birebir geciyor (bugunku kural), son cekimde YOK (bugunku kural). Bu
   CLAY FIGURINE grameridir: her gocuk yerinde kalir.

**Dikkat:** uc olcutun de buyuk kismi ZATEN `series/shots.py` icinde var. Bu
rock yeni kural icat ETMEZ; eksik olan tek parcayi (dort cekimin ayni
`environment` id'sini kullanmasi) ekler ve ucunu tek bir "gercekcilik" raporu
altinda gorunur kilar. Yeni kural eklemeden once mevcut linterin neyi zaten
kapsadigi dosyadan DOGRULANIR; tekrar eden kural yazilmaz.

**Proof:** `python -m pytest tests/test_scenario_realism.py -q` (yeni). Vakalar:
(a) dort cekim ayni ortam -> gecer; (b) cekim 3 baska ortam -> REDDEDILIR;
(c) mevcut canli planlar (part 27, 28) bu olcutten TEMIZ gecer (regresyon).

---

## Kabul kaniti (unit testler YETMEZ)

1. `python -m pytest tests/ -q` -> 0 failed.
2. Canli veriyle geriye donuk kontrol: part 22 (loop saglam, anlatimli) ve
   part 27 (loop kirik, anlatimsiz) uzerinde denetim CALISTIRILIR ve
   part 27 icin `degraded=true`, `loop_closed=false`,
   `narration_delivered=false` uretmelidir. Denetim gecmisi dogru okumuyorsa
   gelecegi de okumaz.
3. Bir sonraki gercek kosuda part kaydinda yeni alanlar gorunur.
