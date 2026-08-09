# RF-PLAN-SES , AImagine: diegetik ses + görünür işçilik

**Tarih:** 2026-08-09 · **Sürücü:** Claude (Visionary) / Codex (Integrator) · **Kanal:** AImagine
`from-scratch` · **Dosya adı çakışma kuralı:** `PLAN.md`, `RF-PLAN.md` ve `RF-PLAN-PROMPT.md`
zaten var ve ilgisiz , bu koşunun kanonik plan dosyası **`RF-PLAN-SES.md`**, log dosyası
**`RF-SAME-PAGE-LOG-SES.md`**.

## CORE FOCUS (tek cümle)

AImagine bölümleri müziksiz çıksın , tek ses inşaatın kendi gerçekçi sesi olsun , ve yapı
kendi kendine belirmesin, ustanın gözle görülür el işçiliğiyle yükselsin.

## 0. İhsan'ın talebi (aynen)

1. "Arkada hâlâ Suno'nun yaptığı müzikler var; bunları AImagine kanalında istemiyoruz."
2. "İnşaatın kendi sesini istiyoruz ama çok gerçekçi olmalı: çekiç vuruyorsa çekiç sesi,
   tornavida kullanıyorsa tornavida sesi, matkap kullanıyorsa matkap sesi."
3. "Videoda aktif bir inşa etme süreci görünmüyor. Video kendi kendine ilerliyor, bir adam
   öylece duruyormuş gibi. Arada bir eline bir eşya alıyor ve inşaat kendi kendine oluyor."
4. "Ürünler gelecek, ürünler geldikten sonra inşaata başlayacağız. Ürünleri alıp kendiniz
   inşa edeceksiniz. Her şeyi kendinizin yaptığını videoda birebir görmek istiyoruz."
5. "Hangi otomasyonlara ihtiyacımız var, hangileri zaten entegre , kontrol et."

---

## 1. ÖLÇÜM , bugünkü gerçek durum (dünkü rapora göre DÜZELTME)

Kaynak: `aimagine/from-scratch/qc_log.jsonl` (yalnız `event="review"` sayıldı; `final_reject`
aynı sebepleri tekrarlar ve tabloyu şişirir) + Actions koşuları 31281224993, 31319930400.

| Bölüm | Koşu | İlk-deneme QC geçişi | Sonuç |
|---|---|---|---|
| ep06 | 2026-08-08 22:14 | 4/6 (çekim 6'nın ilk incelemesi Gemini API hatası, üretim kusuru değil → üretim kalitesi bazında 5/6) | ✅ **YAYINLANDI** |
| ep07 | 2026-08-09 15:00 | **0/5** | ❌ **"Part 7 üretilemedi"** |

**Dün "%83,3" dedim, o rakam yalnız ep06 içindi ve çekim 6'nın API hatasını saymıyordu.
Bugünkü ep07 koşusu 0/5 ile çöktü ve kanal bugün yayın yapmadı.** Yani ROCK 1-3 kazanımı tek
bölümde tuttu, ikinci bölümde tutmadı. Doğru okuma: iki bölüm birleşik **4-5/11**, ve
varyans çok yüksek.

ep07 bütçede öldü: klip başına 126 kredi, tavan 1880 → ~14 klip. 13 klip harcandı, çekim 6'ya
sıra gelmeden bölüm durdu.

### 1.1 Gemini'nin kendi cümleleri , İhsan'ın şikâyeti makine tarafından doğrulanmış

`issues` alanından, ep06-ep07:

- "Materials (wagon, wood, crystals) **appear abruptly without continuous movement or arrival**,
  breaking the satisfying build progression."
- "Furniture and decor **appear abruptly rather than being smoothly installed**."
- "**Lack of smooth, continuous build progression; stages appear to jump rather than flow.**"
- "The roof elements **appear and disappear non-linearly** during the build progression."
- "Abrupt, **non-timelapse-like transformation** of the ground from rubble to paved surface."

Bu, madde 3'ün birebir makine kaydıdır. Şikâyet öznel değil, ölçülü.

Yan bulgular (aynı log): kalıcı **ghosting/çift pozlama** (yeni baskın kusur), **birden fazla
usta** (3 kayıt), **kamera kayması**, ve `art_style`'ın "bright daylight" sabitiyle yazarın
neon gece sahnesi arasındaki **çelişki** ("The prompt has conflicting lighting descriptions").

---

## 2. KÖK NEDENLER (kod ve log ile, tahmin değil)

### KN-1 , Native inşaat sesi üretiliyor ve sonra SİLİNİYOR

- Kie klipleri sesli üretiliyor: `core/kie_api.py:396` → `"generate_audio": bool(sound)`;
  `produce.py:951,979` → `sound=bible.native_audio`; `bible.py:215` varsayılan **True**.
- AImagine'de anlatım yok → `produce.py:236` bloğu atlanır → `narration_ok=False`.
- `produce.py:292-295` bu durumda `mix_background_music(..., music_volume=0.9,
  **replace_original=True**)` çağırır.
- `ffmpeg_tools.py:748-750`: `replace_original=True` → filtre yalnız `[bed][aout]`, yani
  **videonun kendi ses kanalı tamamen düşürülür** ve Suno tek ses olur.

Yani çekiç sesi zaten üretiliyor; boru hattı onu atıp yerine müzik koyuyor.

**Bu tasarım kasıtlıydı** (`produce.py:219-227` yorumu): her AI klibinin native sesi kesişlerde
"pop"lar ve boşluk bırakır; sürekli müzik bedi bu dikişleri maskeler. Müziği kaldırırken bu
sorunu geri çağırıyoruz , ROCK 1 bunu ayrıca çözmek zorunda.

### KN-2 , Prompt'un altı çekiminde ustanın YAPTIĞI hiçbir iş yazmıyor

Yürürlükteki `shot_plan` (özneyi düşüren edilgen çatı):

- "An empty lot **is graded**, then road, fence and landscaping **are laid out**, then the
  foundation **is marked**."
- "Foundation, walls and roof frame **rise** inside that same composition."
- "Cladding, roof, paint, exterior lighting and landscaping **are finished**."
- "Furniture and decor **are installed**, the lighting **comes up**."

Altı çekimde ustanın özne olduğu tek cümle var: "The builder arrives with materials."
Model kendisine yazılanı üretiyor: kendi kendine kurulan bir yapı ve yanında duran bir adam.

### KN-3 , Doktrin ustaya iş yapmayı açıkça YASAKLIYOR

- `art_style`: "Photoreal construction **timelapse** realism" (timelapse = insan bulanıklaşır,
  yapı sıçrar).
- `brief` madde (3): "Ustaya el veya parmak yakın planı gerektiren ince motor iş verilmez;
  **yürür, taşır, işaret eder, gözlemler**."

Bu kural 2026-08-08'de anatomi redlerini azaltmak için bilinçli konmuştu. İhsan'ın bugün
reddettiği görüntü tam olarak budur.

### KN-4 , QC yüzeyinde iki tane kendi kendini vuran yasak KALDI

`critic.py:118` tanımı: `forbidden_elements` = *"the prompt explicitly forbids elements ... and
a frame clearly shows one."* Yani prompt yüzeyindeki HER yasak, sık görülen bir üretim
sonucunu sert redde çevirir. 2026-08-08'de kanıtlanan mekanizma budur; iki kaynak hâlâ açık:

1. `qc.notes`: "Celebration, presentation gestures, looking at camera and ta-da poses **are
   forbidden** in this channel."
   → Gemini logu: *"The builder's final pose in frame 8, standing back and observing the
   finished work, **could be interpreted as a forbidden presentation** or 'ta-da' gesture."*
   İnşaat bitince ustanın geri çekilip bakması bu türün en doğal karesidir.
2. `art_style`: "**Exactly one** silent builder is present."
   → Gemini logu (3 kez): *"Multiple builders appear in frames 6 and 7, **violating the
   'exactly one silent builder' rule**."*

Niyet doğru, yeri yanlış: ikisi de `issues` gözlemi olmalı, red sebebi değil.

### KN-5 , `art_style` ışığı sabitliyor, yazar sahneyi çelişkiye sokuyor

`art_style` "bright daylight" diyor; yazar meşru biçimde ıslak neon gece sahnesi yazıyor.
Kendi kendisiyle çelişen prompt artifact skorunu yükseltiyor ve bir regen yakıyor.

---

## 3. ROCK 1 , DİEGETİK SES (müzik kalkar, inşaat sesi kalır)

**Done looks like:** AImagine bölümünün tek sesi kliplerin kendi inşaat sesidir; Suno hiç
çağrılmaz; ses gerçekten var olduğu MAKİNEYLE doğrulanır ve yoksa bölüm fail-closed durur.

### Değişiklikler

**R1-a** `aimagine/from-scratch/bible.json` kök: `"music": false`.

**R1-b** `bible.json` → `series.required_layers`: `["hook_teaser", "native_audio"]`
(`music` çıkar, yerine ses-varlığı kapısı gelir). Müzik bir teslimat garantisiydi; yerine
boşluk bırakmıyoruz, ölçülen bir kapı koyuyoruz.

**R1-c** `bible.json` → `series.audio_fade: 0.06` (YENİ opt-in anahtar).
Gerekçe: `concatenate_audio_smooth` varsayılan `fade=0.25` her kesişte 0,25 sn iniş + 0,25 sn
çıkış üretir. Bu, müzik bedinin altında saklanmak üzere seçilmişti; bed kalkınca bölüm başına
beş kez duyulur bir çukur olur. 0,06 sn tıkırtıyı keser, delik açmaz.

**R1-d** `series/bible.py`: yeni `audio_fade` property. Varsayılan **0.25** (anahtarı
kullanmayan HER seri bit-değişmez), tip float, `0.0 <= v <= 1.0` dışında cfg hatası.

**R1-e** `series/produce.py:1054`: `concatenate_audio_smooth(..., fade=bible.audio_fade)`.

**R1-f** `core/ffmpeg_tools.py`: yeni `measure_mean_volume(path) -> float | None`.
`ffmpeg -i <p> -af volumedetect -f null -` çıktısından `mean_volume: -XX.X dB` ayrıştırır.
Ses akışı yoksa veya ayrıştırılamazsa `None`. ffmpeg yoksa/patlarsa `None` (çağıran karar verir).

**R1-g** `series/produce.py:674`: `unknown_layers` beyaz listesi
`{"hook_teaser", "music", "native_audio"}` olur. (`music` beyaz listede KALIR , başka seriler
kullanıyor.)

**R1-h** `series/produce.py` `_post_process`: `required_layers` içinde `native_audio` varsa,
tüm katmanlardan SONRA final dosya ölçülür. `None` (ses akışı yok) **veya**
`mean_volume < -50.0 dB` ise `logger.error` + `return None` (fail-closed, `music` kapısının
aynısı). Ölçülen değer her hâlükârda `logger.info` ile loga yazılır , sessiz teslimat bir daha
fark edilmeden geçmesin.

**R1-i** `aimagine/from-scratch/series.json`: `auto_replenish.music_prompt: false`,
`auto_replenish.music_style` anahtarı SİLİNİR. Yazar artık Suno prompt'u yazmaz.

**R1-j** Ses yönü PROMPT yüzeyine, OLUMLU cümleyle yazılır (olumsuzlama hem denetçi kuralı
(a)'yı ihlal eder hem `forbidden_elements`'i besler , KN-4):
`art_style` sonuna eklenen cümle:
`The soundtrack is the work itself, close and dry: tool impacts, motor whine, material scrape and open-air site ambience.`
ve her `shot_plan` satırı o fazın duyulan aletini adıyla taşır (ROCK 2, R2-b).

**R1-k** `brief` madde (5) yeniden yazılır:

```
(5) SES: Müzik yoktur ve müzik prompt'u yazılmaz. Bölümün tek sesi sahnenin kendi sesidir:
aletin darbesi, motorun uğultusu, malzemenin sürtünmesi, açık hava şantiye ortamı. Her çekim
prompt'unda EN AZ BİR duyulur alet eylemi bulunur (çekiç vuruşu, matkap uğultusu, testere
sesi, tornavida tıkırtısı gibi) ve bu eylem ustanın yaptığı işle aynı cümlededir.
```

### Riskler (açıkça)

- Doktrin §3.4 "müzik = hipnozun yarısı" diyordu ve müzik `required_layers` kapısıydı.
  Bu, İhsan'ın açık kararıyla iptal ediliyor; doktrin v2.3'te güncellenir.
- Dikiş sesi: R1-c azaltır, sıfırlamaz. Kesişte ton sıçraması kalırsa çare `acrossfade`
  değil (video ile senkron kayar) , ISSUES'a yazılır.
- Kie'nin native sesinin gerçekten alet sesi taşıdığı ilk canlı koşuda ÖLÇÜLECEK; R1-h
  yalnız "ses var mı" der, "çekiç sesi mi" demez.

### PROOF (Codex koşacak, ben tekrar koşacağım)

1. `python -m pytest tests/ -q` , tamamı yeşil.
2. `python tools/rf_prompt_lint.py --series aimagine/from-scratch` , 0 ihlal.
3. YENİ `tests/test_diegetic_audio.py`:
   - ffmpeg ile iki adet 2 sn'lik klip üretilir (biri 440 Hz ton, biri sessiz);
     `concatenate_audio_smooth(..., fade=0.06)` sonucu ses akışı taşır ve
     `measure_mean_volume` tonlu birleşimde > -50 dB, sessizde < -50 dB (veya None) döner.
   - ffmpeg yoksa test `skip` olur (CI'da ffmpeg var, yerelde olmayabilir).
   - `bible.audio_fade` varsayılanı 0.25; anahtar yokken `concatenate_audio_smooth`
     0.25 ile çağrılır (mevcut serilerin bit-değişmezliği).
   - `native_audio` zorunlu katmanken sessiz final → `_post_process` `None` döner.
4. Makine iddiası: `bible.music is False`, `"music" not in required_layers`,
   `"native_audio" in required_layers`, ve `aimagine/`, `sentinal_ihsan/`,
   `shadowedhistory/`, `galactic_experience/` altındaki DİĞER hiçbir bible'da `audio_fade`
   anahtarı yok.

---

## 4. ROCK 2 , GÖRÜNÜR İŞÇİLİK (yapı kendi kendine belirmez)

**Done looks like:** Altı çekimin altısında da ustanın özne olduğu, adı konmuş bir aletle
yapılan bir iş vardır; malzeme çekim 1'de sahneye TAŞINARAK girer; QC yüzeyinde red üreten
yasak cümlesi kalmaz; bu kural makineyle denetlenir.

### Değişiklikler

**R2-a** `bible.json` → `art_style` TAMAMEN şu metinle değişir (bu string HEM Kie'ye HEM
Gemini'ye gider , `shots.py:48,137` + `produce.py:897`):

```
Photoreal construction realism in vertical 9:16, natural light that matches the scene, saturated but believable color, tactile real materials with matte weathered surfaces, coherent site geography, and continuous hands-on build progression in briskly accelerated real time. The viewpoint stays fixed for the whole shot: one unchanging position and angle, with a slow zoom as its single movement. A single recurring builder does all the work alone at mid-distance in a dark cap, dark crew-neck and work gloves, framed from behind or in profile with the full body inside the frame. Every change in the structure comes from his visible action in the same shot: he carries each piece in, sets it in place and fastens it with a real tool before it becomes part of the build. The soundtrack is the work itself, close and dry: tool impacts, motor whine, material scrape and open-air site ambience.
```

Neyi neden değiştirdi:
- `timelapse` → `continuous hands-on build progression in briskly accelerated real time`
  (hız korunur, sıçrama gider , Gemini'nin "stages jump rather than flow" şikâyeti).
- `bright daylight` → `natural light that matches the scene` (KN-5 çelişkisi biter).
- `Exactly one silent builder is present` → `A single recurring builder does all the work
  alone` (aynı niyet, yasak cümlesi değil , KN-4/2).
- YENİ nedensellik cümlesi: değişimin sebebi ustanın görünür eylemidir (KN-2'nin panzehiri).
- YENİ ses cümlesi (R1-j).

**R2-b** `series.json` → `auto_replenish.shot_plan` altı satır, ETİKETSİZ JSON dizisi
(numaralandırma prompt'a yazı olarak sızıyor , v2.2 dersi). Hepsi etken çatı, ustanın öznesi,
adı konmuş alet ve duyulan ses; hepsi ≤45 kelime (denetçi kuralı c):

```json
[
  "A fresh exterior wide scene, position and angle fixed, slow zoom the only movement. A loaded trailer rolls in; the builder unloads timber, panels and sacks by hand, rakes the lot level, then drives marker stakes with a ringing mallet.",
  "The same fixed exterior view continues from the previous final frame, slow zoom the only movement. The builder pours and levels the footing, raises wall frames one by one, and nails the roof rafters with a hammer and a screaming circular saw.",
  "The same fixed exterior view continues from the previous final frame, slow zoom the only movement. The builder screws on cladding with a whining drill, lays roofing, rolls paint across the walls, mounts exterior lamps, then plants and waters the landscaping.",
  "A fresh interior wide scene, position and angle fixed, slow zoom the only movement. The builder carries in boards, screws up interior walls, snaps flooring together with a rubber mallet, and runs conduit and lighting cable, matching the exterior materials.",
  "The same fixed interior view continues from the previous final frame, slow zoom the only movement. The builder hauls furniture in, assembles it with a clicking screwdriver, hangs decor, fits the lamps, flips the switch, and wipes the surfaces clean.",
  "Continuing from the previous final frame, the viewpoint is released for one unbroken move that begins inside, passes through a door or window, and settles on a wide exterior of the finished structure while the builder keeps fastening the last trim."
]
```

Çekim 1 İhsan'ın madde 4'ünü birebir karşılar: yüklü römork gelir, usta malzemeyi ELLE indirir,
sonra inşaata başlar.

**R2-c** `bible.json` → `series.qc.notes` TAMAMEN şu metinle değişir:

```
This channel builds one structure and delivers one final reveal; record any second structure or second reveal under issues. A second figure in the frame, camera-lock drift across a chained shot, a change in the recurring builder's cap, crew-neck, gloves or established look, and a break in the structure's material or design language are continuity observations: record them under issues. A celebration pose, a presentation gesture or a look at camera is also a continuity observation for this channel: record it under issues. Reserve the numeric score for genuine generation defects as defined in your instructions. When the structure changes state with no visible action causing it, record that under issues as well. hook_shot is 6 and the hook teaser comes from near the end of shot 6 while the finished exterior is visible.
```

- "forbidden" kelimesi tamamen çıktı (KN-4/1).
- İkinci figür artık `issues` gözlemi (KN-4/2).
- "görünür eylem olmadan durum değişimi" `issues`'a KAYDEDİLİR ama **skora yazılmaz**.
  Gerekçe: bugün bütçe zaten dar (ep07 13 klipte öldü); yeni bir sert red kaynağı açmak
  "sıfır video" riskini büyütür. Birincil kaldıraç prompt'tur; bu satır ölçüm gözüdür.
  **Terfi tetiği:** ardışık iki bölümde hâlâ "appear abruptly / jump rather than flow"
  sınıfı kayıt varsa, bu satır skorlanır hâle getirilir (ayrı karar, ISSUES).
- `qc.notes` yalnız Gemini'ye gider, Kie'ye GİTMEZ; bu yüzden içindeki "camera" kelimesi
  yasaklı-nesne taramasına GİRMEZ. Denetçi kuralı (b) `qc.notes`'a uygulanmayacak.

**R2-d** `series.json` → `auto_replenish.brief`:
- Madde (3) sonu değişir: "Ustaya el veya parmak yakın planı gerektiren ince motor iş
  verilmez; yürür, taşır, işaret eder, gözlemler." **→**
  `Usta işi KENDİ ELİYLE yapar: malzemeyi indirir, taşır, yerine koyar, aletle sabitler.
  İş ORTA MESAFEDEN, tam vücut kadrajda görünür; el veya parmak makro yakın planı yoktur.`
- Madde (5) R1-k ile değişir.
- YENİ madde (10):
  `(10) ETKEN ÇATI: Her çekim prompt'unun gövdesinde usta ÖZNEDİR ve bir iş yapar
  ("the builder <fiil>"). Yapının kendi kendine değiştiğini anlatan öznesiz edilgen cümle
  ("is built", "are installed", "rise", "goes up") YAZILMAZ. Her gövdede en az bir alet veya
  malzeme adı geçer ve o aletin sesi duyulur.`

**R2-e** `tools/rf_prompt_lint.py` iki yeni kural:
- **Kural (f) ETKEN İNŞA:** `shot_plan` satırlarının HER BİRİ ve her plan çekim gövdesi
  (`plans/part*.json` → `shots[].prompt` gövdesi, önek ayrıldıktan sonra) şunları taşımalı:
  (1) `the builder` + (en fazla 2 sözcük ara) + `BUILD_VERBS` içinden bir fiil,
  (2) `TOOL_OR_MATERIAL_NOUNS` içinden en az bir ad.
  Bu POZİTİF gerekliliktir: karşılanması için ustanın özne olduğu bir yan cümle şarttır,
  dolayısıyla öznesiz edilgen çatı yapısal olarak dışlanır. Ayrı bir "edilgen dedektörü"
  YAZILMAZ (kırılgan olur, yanlış pozitif üretir).
  `BUILD_VERBS` ve `TOOL_OR_MATERIAL_NOUNS` modül başında sabit demet, `PROHIBITED_NOUNS`
  ile aynı stilde, `normalize()` üzerinden sözcük-sınırı eşleşmesiyle.
- **Kural (g) QC YÜZEYİNDE YASAK YOK:** `art_style` ve `qc.notes` içinde
  `forbidden`, `exactly one`, `must not`, `is not allowed`, `prohibited` kalıpları ihlaldir.
  Gerekçe kod: `critic.py:118`.

**R2-f** `aimagine/KONSEPT.md` → **v2.3**:
- Başlık bloğuna v2.3 satırı (ses pivotu + görünür işçilik + gerekçe ölçümü).
- §3.1 tablosu: her çekimin "Kural" hücresi ustanın yaptığı işle yeniden yazılır; çekim 1'e
  malzeme teslimatı girer.
- §3.1 USTA paragrafı: "ince motor iş verilmez" → "işi kendi eliyle yapar, orta mesafeden".
- §3.4 SES tamamen yeniden: müzik YOK, diegetik ses TEK ses; ISSUES'taki "diegetik foley"
  maddesi kapanır.
- §3.5 Güvenlik maddesine dokunulmaz; "Kutlama/ta-da YASAK" ifadesi QC notundan kalktığı için
  §3.1 tablosundaki karşılığı "sahne tasarımı kuralı" olarak yeniden ifade edilir.
- §7 veri bölümü R1/R2 anahtarlarıyla güncellenir (`music: false`, `required_layers`,
  `audio_fade`, `music_prompt: false`).
- `doctrine_sha256` **motorun kendi fonksiyonuyla** yeniden pinlenir
  (`series/bible.py:97` LF normalizasyonu). Elle `sha256sum` KULLANILMAZ.

### Riskler (açıkça)

- **Anatomi:** alet kullanan usta anatomi redini artırabilir. Karşı veri: iş yaptırmayan
  bugünkü prompt'la ep07'de zaten 3 anatomi redi var; 27 incelemelik eski ölçümde 9 anatomi
  redi vardı ve o da elsiz doktrindi. Panzehir orta mesafe + tam vücut kadraj.
  **Geri dönüş tetiği:** ardışık iki bölümde anatomi redi ≥5 ise R2-d madde (3) eski hâline
  döner (tek satır).
- **Ghosting:** ep07'nin baskın kusuru; kaynağı ölçülmedi. Etken-çatı yazımının sürekli
  hareket üretip morphing'i azaltması BEKLENTİDİR, iddia değil. Ayrı ISSUES maddesi.

### PROOF

1. `python -m pytest tests/ -q` , tamamı yeşil.
2. `python tools/rf_prompt_lint.py --series aimagine/from-scratch` , 0 ihlal
   (yeni (f) ve (g) kuralları AÇIKKEN).
3. Benim yazacağım `tests/test_rf_active_build_adversarial.py` (Codex'in suitine ek):
   edilgen satır reddedilir; "the builder" yalnız ÖNEKte geçip gövdede geçmiyorsa reddedilir;
   fiil eşleşmesi sözcük-sınırlı ("rebuilder" tetiklemez); boş/None/Türkçe girdi patlamaz;
   45/46 kelime sınırı; `qc.notes` içindeki "exactly one" yakalanır, "one final reveal"
   yakalanmaz.
4. `python tools/rf_transition_check.py --verify` , `parts` 1-6 ve `published.json`
   bit-değişmez.
5. Doktrin SHA: `series.json`'daki pin, `bible.py`'nin kendi fonksiyonunun çıktısına eşit.

---

## 5. ROCK 3 , PLAN YENİLEME + KANIT

**Done looks like:** Bekleyen part07-10 planları yeni doktrinle yeniden üretilmiş, denetçiden
ve preflight'tan geçmiş; yayınlanmış veriye dokunulmamış.

- **R3-a** `tools/rf_transition_check.py --snapshot` (korunan veri mühürlenir).
- **R3-b** `plans/part07.json` … `part10.json` SİLİNİR.
- **R3-c** `series.json` → `total_parts` GEÇİCİ olarak **6** yapılır. (Yoksa replenish dört
  "bekleyen" part görüp no-op kalır , `replenish.py:334` `_adopt_orphans` + `:1195`
  `total_parts` kendi kendini yazma davranışı.) `next_part: 7` DEĞİŞMEZ.
- **R3-d** Replenish koşar, 7-10 yeni doktrinle üretilir, `total_parts` 10'a döner.
- **R3-e** Her yeni plan için `python -m series.preflight --series from-scratch --plan partNN`
  exit 0.
- **R3-f** `rf_prompt_lint` yeni planlarda 0 ihlal (kural (f) plan gövdelerini de tarar).
- **R3-g** `rf_transition_check --verify` , parts 1-6 + `published.json` bit-değişmez.

### Canlı ölçüm kapısı (bir sonraki iki koşudan sonra, kod işi değil)

| Metrik | Hedef | Bugün |
|---|---|---|
| İlk-deneme QC geçişi (2 bölüm birleşik) | ≥ 8/12 | 4-5/11 |
| Yayınlanan bölüm | ≥ 1/2 | 1/2 |
| `issues`'ta "appear abruptly / jump rather than flow" sınıfı kayıt | 0 | 5 |
| Final videoda ölçülen `mean_volume` | > -50 dB | ölçülmüyor |

Hedef tutmazsa: R2-c'deki "görünür eylem" satırı skorlanır hâle getirilir + bölüm kredi
tavanı ayrı bir kararla ele alınır.

---

## 6. OTOMASYON DENETİMİ (İhsan'ın 5. maddesi , kod değil, rapor)

### 6.1 AImagine'e ZATEN entegre olanlar (doğrulandı)

| # | Proje | Bağ | Durum |
|---|---|---|---|
| , | **Motor** (`Projeler/Youtube`) | `.github/workflows/from-scratch.yml`, günlük cron | ✅ CANLI (bugün başarısız) |
| , | **Upload-Post** | motor içinden YouTube + Instagram + TikTok | ✅ CANLI (ep06 üçüne de gitti) |
| 6 | YouTube_Yorum_Otomasyonu | `.github/workflows/aimagine.yml`, `YOUTUBE_CHANNEL_ID: UCCgbHTzYKYawUT6zEo0nlDg`, cron `0 7 * * *`, `YT_PHASE: "1"` | ✅ CANLI (Faz-1 salt-rapor) |
| 35 | Akilli_Watchdog | `config.py` → `#19 YouTube Otomasyonu`, repo `youtube-automation` | ⚠️ İZLİYOR ama `cron_hint: []` |
| 36 | Proje_Dashboard | `config/projects.yaml` | ✅ CANLI |
| 13 | YT_Aciklama_Otomasyonu | AImagine kanalına kurulu | 🚫 EMEKLİ (cron YAML'da yorumlu) |
| 14 | Gizli_Video_Otomasyonu | `aimagine_oauth_kur.py`, kanal ID bağlı | 🚫 DURAKLATILDI (schedule yorumlu; kanal `publish_mode=auto` ile doğrudan public yayınlıyor, unlisted akışı kullanılmıyor) |

### 6.2 Bu talep için gereken yeni otomasyon: YOK

Ses ve işçilik sorunu motorun kendi prompt yüzeyinde ve `_post_process` zincirinde çözülür.
Yeni bir servis eklemek bu iki sorunun hiçbirine dokunmaz. ROCK 1-3 dışında bir şey kurmak,
bu talep için harcanmış boş efor olur.

### 6.3 Gerçek boşluk , nöbetçi bu kanalın başarısızlığını GÖREMİYOR

Bugün ep07 çöktü ama Actions "success" yazdı. Sebep bilinen ve hâlâ açık:
`from-scratch.yml` içinde `python ... | tee log` boru hattı `pipefail` olmadan koşuyor,
çıkış kodu maskeleniyor. Nöbetçi (#35) bu repoyu `cron_hint: []` ile izliyor, yani
"koşu başarısız mı" sinyaline bakıyor , ve o sinyal yalan. **Sonuç: 4 kanalın üretim
başarısızlığı nöbetçinin kör noktasında.** Bu, hafızadaki "3,8 günlük 4-kanal sessizliği"
olayının tam mekanizması.

Bu bir ROCK DEĞİL (Plan 1 ROCK 3 olarak zaten onaylı planda duruyor), ama bu koşunun
raporunda İhsan'a tekrar hatırlatılır ve ISSUES'ta en yüksek öncelikte kalır.

### 6.4 Eklemeye DEĞER (öneri, bu koşunun kapsamı dışında, ayrı karar)

| Öneri | Ne kazandırır | Maliyet/risk |
|---|---|---|
| **#9 Notion Performans'ı AImagine'e klonla** | Kanal artık yayınlıyor; KONSEPT §5 kill-gate'i (25 bölüm, medyan <500) 7-günlük olgun performans verisi olmadan ÇALIŞMAZ | 1 saat, reçete hazır (`KURULUM_TAKIP.md`) |
| **#34 İtibar Radarı'nı AImagine'e aç** (FAZ 6 kapısı) | "Bu adam hiçbir şey yapmıyor" tipi yorum, bu şikâyetin ERKEN uyarısıydı; bugün tek denetçi İhsan'ın gözü | 3-4 saat, şemaya `channel` kolonu |
| **Higgsfield MCP `video_analysis_create` / `virality_predictor`** (#27 eklentisi içinde zaten kurulu) | Yayınlanan bölümü makineye izletip "aktif inşa var mı / ses dolu mu" sorusunu ölçmek. Bugün bu ölçüm HİÇ yok | Kredi + oturum doğrulaması gerekir, doğrulanmadı |
| **Apify MCP `scraptik--tiktok-api`** | cairo_ia gibi referans hesapların gerçek viral verisini çekmek; bugün format kopyalama gözleme dayanıyor | Apify kredisi |

### 6.5 Kapsam dışı / gereksiz

#33 TikTok Boost (hesap yok, BLOKE) · #19 YT_Otomasyonu (ayrı hat) · #18 NOVASCEND (ayrı hat)
· #26/#27/#28 (iş kolu, kanal bağı sıfır) · #13 ve #14 (emekli/duraklatılmış, açmaya gerek yok).

---

## 7. ISSUES (bu koşuda bilinçli YAPILMAYANLAR)

- **I-A (yüksek):** Plan 1 ROCK 3 , `defaults: run: shell: bash -euo pipefail {0}` + `ok is
  not True` çıkışı, 4 workflow. Actions'ın yalan "success"'i nöbetçiyi kör ediyor (§6.3).
- **I-B (yüksek):** `critic.strengthen_prompt` (`critic.py:273`) Gemini'nin `fix_notes`'unu
  regen prompt'una AYNEN ekliyor ve o notlar olumsuzlama taşıyor (gerçek log: "Ensure no
  readable logos or text appear..."). Onarım yalnız İLK denemeyi kapsıyor. Motor kodu, dört
  kanal ortak.
- **I-C (orta):** Ghosting/çift pozlama ep07'nin baskın kusuru; kök neden ölçülmedi.
- **I-D (orta):** Bölüm kredi tavanı 1880, klip 126 → 14 klip. ep07 13 klipte öldü.
  Geçiş oranı yükselmezse tavan kararı gerekir.
- **I-E (düşük):** Müziksiz kesişte ton sıçraması kalırsa çözüm `acrossfade` değil
  (senkron kayar); ayrı tasarım gerekir.
- **I-F (düşük):** `from-scratch.yml` başlık yorumu iki doktrin sürümü bayat.
- **I-G:** R2-c "görünür eylem" satırının skorlanmaya terfisi (tetik §4'te).
- **I-H:** §6.4'teki dört otomasyon önerisi.
- Devralınanlar: usta için Kie referans-görseli, çekim 3→4 referans köprüsü, cross-shot QC.

---

## 8. DOKUNULMAZ (bu koşuda)

- `aimagine/from-scratch/plans/part01..part06.json` ve `published.json` , bit-değişmez.
- `series.json` → `next_part: 7`, `parts` bloğu, `status`, `publish_mode`.
- Diğer üç kanalın (sentinal_ihsan, shadowedhistory, galactic_experience) hiçbir dosyası.
- `series/critic.py` `_QC_SYSTEM` , motor kodu, dört kanal ortak (I-B ayrı karar).
- Kök `.gitignore`, `master.env`, `credentials/`.
- `core/ffmpeg_tools.py`'nin mevcut fonksiyonlarının imzaları , yalnız EKLEME yapılır
  (`measure_mean_volume`) ve `concatenate_audio_smooth`'a varsayılanı değişmeyen bir
  parametre GEÇİLİR (imza zaten `fade: float = 0.25` taşıyor, değiştirilmez).
