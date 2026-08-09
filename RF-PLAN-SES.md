# RF-PLAN-SES , AImagine: diegetik ses + görünür işçilik

**Tarih:** 2026-08-09 · **Sürücü:** Claude (Visionary) / Codex (Integrator) · **Kanal:** AImagine
`from-scratch` · **Sürüm:** r2 (Codex tur-1'in 22 bulgusu işlendi) · Log:
`RF-SAME-PAGE-LOG-SES.md`

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

## 1. ÖLÇÜM , bugünkü gerçek durum

Kaynak: `qc_log.jsonl` (yalnız `event="review"`; `final_reject` aynı sebepleri tekrarlar) +
Actions koşuları 31281224993, 31319930400 + `series_log.csv`.

| Bölüm | Koşu | İlk-deneme QC | Sonuç |
|---|---|---|---|
| ep06 | 08-08 22:14 | 4/6 (çekim 6'nın ilk incelemesi Gemini API hatası, üretim kusuru değil → kalite bazında 5/6) | ✅ **YAYINLANDI** |
| ep07 | 08-09 15:00 | **0/5** | ❌ **"Part 7 üretilemedi"** |

**Dünkü "%83,3" rakamı yalnız ep06 içindi. Bugünkü ep07 çöktü, kanal bugün yayın yapmadı.**
İki bölüm birleşik 4-5/11; varyans çok yüksek.

### 1.1 KANIT A , native ses ZATEN doğru sesi taşıyor (bugün ölçüldü)

`series_log.csv`'deki canlı Kie URL'inden bugünkü ep07 klibi indirildi
(`2d3c1b9a...1786288937.mp4`, 10 sn):

```
ffprobe → stream 1: aac, 48000 Hz, 2 kanal          (ses akışı VAR)
ffmpeg volumedetect → mean_volume: -29.7 dB, max_volume: -1.2 dB   (dolu, sessiz değil)
Gemini 2.5 Flash (ses girdisi) → {"has_music": false, "speech": false,
  "construction_sounds": ["thud","whirring"], "dominant_content": "construction sounds",
  "silent_fraction_estimate": 0.0}
```

**Boru hattı İhsan'ın istediği sesi zaten üretiyor, sonra siliyor.** Bu ölçüm, tur-1'in
F-1 bulgusunu (kod alıntısı yanlıştı) düzeltirken ROCK 1'in temelini de sağlamlaştırır:
artık varsayım değil, ölçüm.

### 1.2 KANIT B , Gemini'nin kendi cümleleri (`issues`, ep06-ep07)

- "Materials (wagon, wood, crystals) **appear abruptly without continuous movement or
  arrival**, breaking the satisfying build progression."
- "Furniture and decor **appear abruptly rather than being smoothly installed**."
- "**Lack of smooth, continuous build progression; stages appear to jump rather than flow.**"
- "The roof elements **appear and disappear non-linearly**."

İhsan'ın 3. maddesinin birebir makine kaydı. Yan bulgular: ghosting/çift pozlama (yeni baskın
kusur), birden fazla usta (3 kayıt), kamera kayması, ve "conflicting lighting descriptions".

---

## 2. KÖK NEDENLER (kod ve ölçümle doğrulanmış)

### KN-1 , İnşaat sesi üretiliyor ve SİLİNİYOR

- Kanıt A: Omni klipleri dolu, müziksiz inşaat sesi taşıyor.
  (Not: `build_omni_payload` , `omni_api.py:110-130` , bir ses bayrağı GÖNDERMEZ; Omni
  modeli sesi varsayılan üretiyor. `sound=bible.native_audio` , `produce.py:951,979` ,
  **ucuz görsel motor dalıdır** ve from-scratch `engine: "omni"` olduğu için o dala HİÇ
  girmez. Tur-1 F-1 haklıydı; payload'a bilinmeyen bir alan EKLEMİYORUZ.)
- AImagine'de anlatım yok → `produce.py:236` bloğu atlanır → `narration_ok=False`.
- `produce.py:292-295` bu durumda
  `mix_background_music(..., music_volume=0.9, replace_original=True)` çağırır.
- `ffmpeg_tools.py:748-750`: `replace_original=True` → filtre yalnız `[bed][aout]`, yani
  **klibin kendi ses kanalı tamamen düşürülür** ve Suno tek ses olur.

Tasarım kasıtlıydı (`produce.py:219-227`): native ses kesişlerde "pop"lar; müzik bedi
maskeliyordu. Müzik kalkınca bu dikiş sorunu geri gelir , ROCK 1 ayrıca çözer.

### KN-2 , Altı çekimin hiçbirinde ustanın YAPTIĞI iş yazmıyor

Yürürlükteki `shot_plan` özneyi düşüren edilgen çatıdır: "An empty lot **is graded**",
"the foundation **is marked**", "Foundation, walls and roof frame **rise**",
"Cladding, roof, paint ... **are finished**", "Furniture and decor **are installed**",
"the lighting **comes up**". Ustanın özne olduğu tek cümle: "The builder arrives with
materials." Model kendisine yazılanı üretiyor.

### KN-3 , Doktrin ustaya iş yapmayı açıkça YASAKLIYOR

`art_style`: "Photoreal construction **timelapse** realism". `brief` madde (3): "Ustaya el
veya parmak yakın planı gerektiren ince motor iş verilmez; **yürür, taşır, işaret eder,
gözlemler**." 2026-08-08'de anatomi redini azaltmak için kondu; İhsan'ın bugün reddettiği
görüntü tam olarak budur.

### KN-4 , QC yüzeyinde iki kendi kendini vuran yasak KALDI

`critic.py:118`: `forbidden_elements` = *"the prompt explicitly forbids elements ... and a
frame clearly shows one."* İki kaynak açık:
1. `qc.notes`: "ta-da poses **are forbidden**" → Gemini logu: *"standing back and observing
   the finished work, **could be interpreted as a forbidden presentation**"*. İnşaat bitince
   ustanın geri çekilmesi bu türün en doğal karesidir.
2. `art_style`: "**Exactly one** silent builder is present" → Gemini logu 3 kez:
   *"violating the 'exactly one silent builder' rule"*.

### KN-5 , `art_style` ışığı sabitliyor, sahneyle çelişiyor

"bright daylight" + yazarın neon gece sahnesi = kendi kendisiyle çelişen prompt.

### KN-6 , ep07'yi öldüren şey QC DEĞİL, KREDİ TAVANIYDI (tur-1 F-21, doğrulandı)

- `.github/workflows/from-scratch.yml:56` → `EPISODE_CREDIT_CAP=1900`.
- `core/cost_tracker.py:67` → muhafazakâr tahmin `omni` 10 sn = **200** kredi
  (gözlenen gerçek maliyet 126; tavan bilerek yüksek tutulmuş).
- `CONSERVATIVE_FIXED_CREDITS[("music","suno")] = 80`.
- `HardCreditCap.authorize` (`credit_gate.py:257`) her çağrıda **tahmini** ekler.

ep07'nin gerçek akışı: müzik 80 → çekim 1 ana 200 (280) → regen (480) → çekim 2 ana (680)
→ regen (880) → çekim 3 ana (1080) → regen (1280) → çekim 4 ana (1480) → regen (1680) →
çekim 5 ana (1880) → çekim 5 regen 2080 > 1900 **reddedildi (isteğe bağlı)** → **çekim 6
ana 2080 > 1900 → ENGELLENDİ → `return None` → "Part 7 üretilemedi"**.

`qc_log`'daki 9 inceleme (6 ana + 3 regen) bu aritmetiği birebir doğrular.

**Yapısal kusur:** erken çekimlerin isteğe bağlı regen'leri, sonraki ZORUNLU ana çekimleri
aç bırakabiliyor. Müziği kaldırmak 80 kredi kazandırır ama `floor(1900/200)=9` çağrı sayısını
değiştirmez , tek başına bu ölümü ÖNLEMEZ. ROCK 3 bunu çözer.

---

## 3. ROCK 1 , DİEGETİK SES

**Done looks like:** AImagine bölümünün tek sesi kliplerin kendi inşaat sesidir; Suno hiç
çağrılmaz; teslim edilen dosyada müzik OLMADIĞI ve inşaat sesi OLDUĞU makineyle doğrulanır;
doğrulanamıyorsa bölüm fail-closed durur.

### Değişiklikler

**R1-a** `aimagine/from-scratch/bible.json` kök: `"music": false`.

**R1-b** `bible.json` → `series.required_layers`: `["hook_teaser", "native_audio"]`.

**R1-c** `bible.json` → `series.audio_fade: 0.06` (YENİ opt-in anahtar).
`concatenate_audio_smooth` varsayılan `fade=0.25` her kesişte 0,25 in + 0,25 out yapar; bu
müzik bedinin altında saklanmak için seçilmişti. Bed kalkınca bölüm başına beş duyulur çukur
olur. 0,06 tıkırtıyı keser, delik açmaz.

**R1-d** `series/bible.py`: yeni `audio_fade` property, varsayılan **0.25**
(anahtarı kullanmayan HER seri bit-değişmez), float, `0.0 <= v <= 1.0` dışı cfg hatası.

**R1-e** `series/produce.py:1054`: `concatenate_audio_smooth(..., fade=bible.audio_fade)`.

**R1-f** `core/ffmpeg_tools.py`: yeni `measure_mean_volume(path) -> float | None`.
`ffmpeg -i <p> -af volumedetect -f null -` çıktısından `mean_volume: -XX.X dB` ayrıştırır.
Ses akışı yok / ayrıştırılamıyor / ffmpeg patlıyor → `None`.

**R1-g** `series/critic.py`: yeni `qc_audio(path) -> dict | None`.
- ffmpeg ile ilk 60 sn'yi 16 kHz mono mp3'e çıkarır (geçici dosya, sonra silinir).
- `_review_frames`'in retry/yedek-model kalıbıyla Gemini'ye verir, ZORUNLU JSON:
  `{"has_music": bool, "speech": bool, "construction_sounds": [string],
    "silent_fraction_estimate": float}`.
- API hatası / anahtar yok → `None` (pass-through; `qc_shot`'ın "skip" felsefesi , Gemini
  kesintisi bir bölümü öldürmez).
- Sonuç `qc_log.jsonl`'a `{"event": "audio", ...}` olarak yazılır (ölçülebilir olsun).

**R1-h** `series/produce.py:674`: `unknown_layers` beyaz listesi
`{"hook_teaser", "music", "native_audio"}`.

**R1-i** `series/preflight.py:78`: **AYNI** beyaz liste orada da güncellenir.
(Tur-1 F-6: preflight'ın kendi kopyası var; yalnız produce'u güncellemek preflight'ı
kırar.)

**R1-j** Kapı, TÜM dönüşümlerden SONRA, YAYINLANACAK dosya üzerinde koşar
(tur-1 F-4). Sıra: birleştirme → `_post_process` (anlatım/müzik) → hook teaser →
**ses kapısı** → yükleme. Kapı `produce`'un final dosyayı döndürdüğü noktadan hemen önce
çağrılır, `_post_process`'in içinden değil.

Kapı mantığı (`native_audio` zorunlu katmandaysa):
1. `measure_mean_volume(final)` → `None` veya `< -50.0 dB` ise **FAIL**.
2. `critic.qc_audio(final)`:
   - `None` → geçir, `logger.warning` (Gemini kesintisi bölüm öldürmez).
   - `has_music is True` → **FAIL** (İhsan'ın 1 numaralı şartı).
   - `speech is True` → **FAIL** (kanalda konuşma yok).
   - `construction_sounds` boş **VE** `silent_fraction_estimate > 0.5` → **FAIL**.
3. FAIL → `logger.error` + `notifier` mesajı + `return None` (durum ilerlemez).
   Ölçülen değerler her hâlükârda loglanır.

**Tur-1 F-5 kararı (kabul, farklı çözümle):** ses kapısı düşerse çekim dosyaları
önbellekte kalır ve sonraki koşu aynı sonuca varır. Klipleri otomatik silmiyoruz , 6 klip
yeniden üretmek ~1200 kredidir ve aynı sonucu vermesi beklenir. Bunun yerine kapı düştüğünde
**Telegram uyarısı** gider ve mesaj "ELLE BAK" der. Sessiz döngü yerine gürültülü durma.

**R1-k** `series.json`: `auto_replenish.music_prompt: false`, `auto_replenish.music_style`
anahtarı SİLİNİR.

**R1-l** `brief` madde (5):
```
(5) SES: Müzik yoktur ve müzik prompt'u yazılmaz. Bölümün tek sesi sahnenin kendi sesidir:
aletin darbesi, motorun uğultusu, malzemenin sürtünmesi, açık hava şantiye ortamı. Her çekim
prompt'unun gövdesinde EN AZ BİR duyulur alet eylemi bulunur ve bu eylem ustanın yaptığı
işle aynı cümledededir.
```

**R1-m** Ses yönü `art_style`'a OLUMLU cümleyle girer (R2-a içinde).

### Riskler

- Doktrin §3.4 "müzik = hipnozun yarısı" diyordu; İhsan'ın açık kararıyla iptal, v2.3'te
  güncellenir.
- Dikiş: R1-c azaltır, sıfırlamaz. Kalırsa çözüm `acrossfade` DEĞİL (video ile senkron
  kayar) , ISSUES I-E.
- `qc_audio` bölüm başına 1 Gemini çağrısı ekler (ücretsiz kotada, ihmal edilebilir).

### PROOF

1. `python -m pytest tests/ -q` , tamamı yeşil.
2. `python tools/rf_prompt_lint.py aimagine/from-scratch` , 0 ihlal.
   (Tur-1 F-19: araç **konumsal** `series_dir` alır, `--series` DEĞİL.)
3. YENİ `tests/test_diegetic_audio.py` (ffmpeg yoksa `skip`):
   - ffmpeg ile 440 Hz tonlu ve tam sessiz 2 sn'lik klipler üretilir;
     `measure_mean_volume` tonluda > -50 dB, sessizde `< -50 dB` veya `None`.
   - Ses akışı HİÇ olmayan dosyada `measure_mean_volume` → `None` (patlamaz).
   - `bible.audio_fade` anahtarsız serilerde 0.25; `concatenate_audio_smooth` o değerle
     çağrılır (mock ile kanıt).
   - `qc_audio` sahte Gemini yanıtlarıyla: `has_music=True` → kapı FAIL;
     `has_music=False, construction_sounds=["hammer"]` → kapı PASS; `None` → kapı PASS +
     uyarı.
   - Zorunlu katman `native_audio` iken sessiz final → üretim `None` döner.
4. Makine iddiası: `bible.music is False`; `"music" not in required_layers`;
   `"native_audio" in required_layers`; `aimagine/`, `sentinal_ihsan/`, `shadowedhistory/`,
   `galactic_experience/` altındaki DİĞER hiçbir bible'da `audio_fade` anahtarı yok.

---

## 4. ROCK 2 , GÖRÜNÜR İŞÇİLİK

**Done looks like:** Altı çekimin altısında da ustanın özne olduğu, adı konmuş bir ALETLE
yapılan bir iş vardır; malzeme çekim 1'de sahneye taşınarak girer; QC yüzeyinde red üreten
yasak cümlesi kalmaz; hepsi makineyle denetlenir.

### Değişiklikler

**R2-a** `bible.json` → `art_style` TAMAMEN şu metinle değişir (bu string HEM Kie'ye HEM
Gemini'ye gider , `shots.py:48,137` + `produce.py:897`):

```
Photoreal construction realism in vertical 9:16, natural light that matches the scene, saturated but believable color, tactile real materials with matte weathered surfaces, coherent site geography, and continuous hands-on build progression in briskly accelerated real time. The viewpoint stays fixed for the whole shot: one unchanging position and angle, with a slow zoom as its single movement. The build is carried out by one recurring builder who does every task himself, working at mid-distance in a dark cap, dark crew-neck and work gloves, framed from behind or in profile with the full body inside the frame. Every change in the structure comes from his visible action in the same shot: he carries each piece in, sets it in place and fastens it with a real tool before it becomes part of the build. The soundtrack is the work itself, close and dry: tool impacts, motor whine, material scrape and open-air site ambience.
```

| Ne değişti | Neden |
|---|---|
| `timelapse` → `continuous hands-on build progression in briskly accelerated real time` | Hız korunur, sıçrama gider (Gemini: "stages jump rather than flow") |
| `bright daylight` → `natural light that matches the scene` | KN-5 çelişkisi biter |
| `Exactly one silent builder is present` → `The build is carried out by one recurring builder who does every task himself` | KN-4/2: dışlama cümlesi değil, tarif |
| YENİ nedensellik cümlesi | KN-2'nin panzehiri |
| YENİ ses cümlesi | R1-m |

**Tur-1 F-12 kısmen kabul:** "one recurring builder" hâlâ tekillik ima eder ve Gemini bunu
ihlal olarak okuyabilir. Tam çözüm yok: cümleyi tamamen atarsak Kie yine kalabalık üretir
(v2.1'de ölçüldü). "exactly one" / "alone" gibi dışlama sözcükleri çıkarıldı; ikinci figür
artık `qc.notes` ile `issues`'a yönlendiriliyor. Kalan risk kabul edildi ve ölçülecek.

**R2-b** `series.json` → `auto_replenish.shot_plan`, ETİKETSİZ JSON dizisi (numaralandırma
prompt'a yazı olarak sızıyor , v2.2 dersi). Hepsi etken çatı + ustanın öznesi + adı konmuş
ALET + duyulan ses; hepsi ≤45 kelime:

```json
[
  "A fresh exterior wide scene, position and angle fixed, slow zoom the only movement. A loaded trailer rolls in; the builder unloads timber, panels and sacks by hand, rakes the lot level, then drives marker stakes with a ringing mallet.",
  "The same fixed exterior view continues from the previous final frame, slow zoom the only movement. The builder pours and levels the footing, raises wall frames one by one, and nails the roof rafters with a hammer and a screaming circular saw.",
  "The same fixed exterior view continues from the previous final frame, slow zoom the only movement. The builder screws on cladding with a whining drill, lays roofing, rolls paint across the walls, mounts exterior lamps, then plants and waters the landscaping.",
  "A fresh interior wide scene, position and angle fixed, slow zoom the only movement. The builder carries in boards, screws up interior walls, snaps flooring together with a rubber mallet, and runs conduit and lighting cable, matching the exterior materials.",
  "The same fixed interior view continues from the previous final frame, slow zoom the only movement. The builder hauls furniture in, assembles it with a clicking screwdriver, hangs decor, fits the lamps, flips the switch, and wipes the surfaces clean.",
  "Continuing from the previous final frame, the viewpoint is released for one unbroken move that begins inside, passes through a door or window, and settles on a wide exterior of the finished structure while the builder fastens the last trim with a whining screwdriver."
]
```

Çekim 1 İhsan'ın 4. maddesini birebir karşılar: yüklü römork gelir, usta malzemeyi ELLE
indirir, sonra inşaata başlar. Çekim 6'ya tur-1 F-11 gereği gerçek alet + ses eklendi.

**R2-c** `bible.json` → `series.qc.notes` TAMAMEN şu metinle değişir:

```
This channel builds one structure and delivers one final reveal; record any second structure or second reveal under issues. A second figure in the frame, camera-lock drift across a chained shot, a change in the recurring builder's cap, crew-neck, gloves or established look, and a break in the structure's material or design language are continuity observations: record them under issues. A celebration pose, a presentation gesture or a look at camera is also a continuity observation for this channel: record it under issues. Reserve the numeric score for genuine generation defects as defined in your instructions. When the structure changes state with no visible action causing it, record that under issues as well. hook_shot is 6 and the hook teaser comes from near the end of shot 6 while the finished exterior is visible.
```

- "forbidden" tamamen çıktı (KN-4/1); ikinci figür `issues` gözlemi (KN-4/2).
- `qc.notes` yalnız Gemini'ye gider, Kie'ye GİTMEZ → içindeki "camera" kelimesi yasaklı-nesne
  taramasına GİRMEZ. Denetçi kuralı (b) `qc.notes`'a uygulanmayacak.

**Tur-1 F-7 [KILL] REDDEDİLDİ, gerekçeli.** Codex "kendi kendine inşa" gözlemini HEMEN
fail-closed skora çevirmek istiyor. Üç sebeple hayır:
1. `_QC_SYSTEM` (`critic.py:119`) `artifact_score`'u zaten "impossible physics" ile tanımlar;
   yoktan beliren nesne bunun içindedir ve ep07'nin 7-9 skorları kısmen buradan geldi. Yani
   şu an bile TAMAMEN skorsuz değil.
2. Birincil kaldıraç prompt'tur (R2-a/b). Yeni bir sert red sınıfı, kredi tavanı bu kadar
   darken (KN-6) "sıfır video" gününü garantiler. Bir kusurlu video, sıfır videodan daha
   iyi Core Focus'a hizmet eder.
3. Ölçüm gözü kapalı kalmıyor: satır `issues`'a yazıyor, yani terfi kararı VERİYLE alınacak.
   **Terfi tetiği:** ardışık iki bölümde hâlâ "appear abruptly / jump rather than flow"
   sınıfı kayıt varsa satır skorlanır (ISSUES I-G).

**R2-d** `series.json` → `auto_replenish.brief`:
- Madde (3) sonu: "ince motor iş verilmez; yürür, taşır, işaret eder, gözlemler" **→**
  `Usta işi KENDİ ELİYLE yapar: malzemeyi indirir, taşır, yerine koyar, aletle sabitler.
  İş ORTA MESAFEDEN, tam vücut kadrajda görünür; el veya parmak makro yakın planı yoktur.`
- Madde (5) → R1-l.
- Madde (9) netleştirilir (tur-1 F-10): `Öneki KELİME KELİME tekrarlama; ama gövdede
  ustanın O SAHNEDE yaptığı işi kendi sözcüklerinle YAZ. Önekle gövdenin ortak 8-kelimelik
  dizisi olmamalı, ustanın özne olması ise ZORUNLUDUR.`
- YENİ madde (10):
  `(10) ETKEN ÇATI: Her çekim prompt'unun gövdesinde usta ÖZNEDİR ve bir iş yapar
  ("the builder <fiil>"). Gövdede en az bir ALET adı geçer. Yapının kendi kendine
  değiştiğini anlatan öznesiz cümle ("rise", "go up", "are installed", "are finished",
  "is laid", "appear") YAZILMAZ.`

**R2-e** `tools/rf_prompt_lint.py` iki yeni kural (tur-1 F-9/F-11 ile sertleştirildi):

- **Kural (f) ETKEN İNŞA.** `shot_plan` satırlarının HER BİRİ ve her plan çekim GÖVDESİ
  (önek ayrıldıktan sonra) üç şartı birden karşılamalı:
  1. `the builder` + (en fazla 2 sözcük) + `BUILD_VERBS` içinden bir fiil;
  2. `TOOL_NOUNS` içinden en az bir ALET adı (malzeme adı yetmez , F-11);
  3. `AUTONOMOUS_CLAUSES` blokajından temiz olmalı.
  `AUTONOMOUS_CLAUSES` ölçülmüş ihlallerden oluşan AÇIK bir listedir, genel bir edilgen
  dedektörü DEĞİLDİR (genel dedektör yanlış pozitif üretir; "the viewpoint is released"
  meşrudur): `rise, rises, rising, go up, goes up, going up, come up, comes up, coming up,
  is installed, are installed, is finished, are finished, is laid, are laid, is graded,
  are graded, is marked, are marked, appear, appears, appearing, assembles itself,
  builds itself`.
  Sabitler modül başında demet, `PROHIBITED_NOUNS` ile aynı stilde, `normalize()` üzerinden
  **sözcük-sınırı** eşleşmesiyle (`rebuilder` → `builder` eşleşmesi OLMAYACAK).
- **Kural (g) QC YÜZEYİNDE YASAK YOK.** `art_style` ve `qc.notes` içinde
  `forbidden`, `prohibited`, `exactly one`, `must not`, `is not allowed`, `are not allowed`
  kalıpları ihlaldir. Gerekçe kod: `critic.py:118`.

**R2-f** `aimagine/KONSEPT.md` → **v2.3**: başlık bloğuna v2.3 satırı; §3.1 tablosunun her
"Kural" hücresi ustanın yaptığı işle yeniden yazılır (çekim 1'e malzeme teslimatı girer);
§3.1 USTA paragrafı "işi kendi eliyle yapar, orta mesafeden"; §3.4 SES tamamen yeniden
(müzik YOK, diegetik ses TEK ses; ISSUES'taki "diegetik foley" maddesi kapanır); §3.5'te
"ta-da YASAK" ifadesi sahne tasarımı kuralı olarak yeniden ifade edilir; §7 veri bölümü
R1/R2/R3 anahtarlarıyla güncellenir. `doctrine_sha256` **motorun kendi fonksiyonuyla**
(`series/bible.py:97`) yeniden pinlenir , elle `sha256sum` KULLANILMAZ.

### Riskler

- **Anatomi:** alet kullanan usta anatomi redini artırabilir. Karşı veri: iş yaptırmayan
  bugünkü prompt'la ep07'de zaten 3 anatomi redi var. Panzehir: orta mesafe + tam vücut.
  **Geri dönüş tetiği:** ardışık iki bölümde anatomi redi ≥5 ise R2-d madde (3) eski hâline
  döner (tek satır).
- **Ghosting:** ep07'nin baskın kusuru; kök neden ölçülmedi. Etken çatının sürekli hareket
  üretip morphing'i azaltması BEKLENTİDİR, iddia değil (ISSUES I-C).

### PROOF

1. `python -m pytest tests/ -q` , tamamı yeşil.
2. `python tools/rf_prompt_lint.py aimagine/from-scratch` , 0 ihlal, (f) ve (g) AÇIK.
3. Benim yazacağım `tests/test_rf_active_build_adversarial.py`:
   edilgen satır reddedilir; "the builder" yalnız ÖNEKte geçip gövdede geçmiyorsa reddedilir;
   `rebuilder`/`reappears` sözcük-sınırı tetiklemez; yalnız MALZEME adı olup ALET olmayan
   satır reddedilir (F-11); kural (e) tekrar eşiğini geçmeyen ama kural (f)'i sağlayan gövde
   İKİSİNDEN DE geçer (F-10 çelişkisinin kanıtı); `qc.notes` içindeki "exactly one" yakalanır
   ama "one final reveal" yakalanmaz; boş/None/Türkçe girdi patlamaz; 45/46 kelime sınırı.
4. Doktrin SHA: `series.json` pini `bible.py`'nin kendi fonksiyonunun çıktısına eşit.

---

## 5. ROCK 3 , ZORUNLU ANA ÇEKİM REZERVASYONU (bölüm gerçekten çıksın)

**Kapsam gerekçesi:** Bu rock İhsan'ın cümlelerinde yok. Ekliyorum çünkü KN-6 ölçümü
gösteriyor ki bölüm ne kadar iyi yazılırsa yazılsın, erken regen'ler son çekimin bütçesini
yiyorsa video HİÇ çıkmıyor. Doğru ses ve doğru işçilik, ancak yayınlanan bir videoda görülür.

**Done looks like:** Bir bölümün altı ANA çekimi her zaman finanse edilir; isteğe bağlı
QC regen'leri yalnız arta kalan bütçeden harcanır.

- **R3-a** `series/credit_gate.py` → `HardCreditCap.authorize(..., reserve: float = 0.0)`.
  `optional=True` çağrılarda koşul `spent + estimate + reserve <= cap` olur.
  Varsayılan `0.0` → diğer TÜM çağrılar ve seriler **bit-değişmez**.
- **R3-b** `series/produce.py`: `qc_regen` yetkilendirmesinden önce `reserve` hesaplanır =
  o çekimden SONRAKİ zorunlu ana çekimlerin muhafazakâr tahmin toplamı.
  Herhangi birinin tahmini `None` (bilinmeyen maliyet) ise `reserve = math.inf` → hiçbir
  isteğe bağlı regen yetkilendirilmez (fail-closed, sessizce geçilmez).
- **R3-c** Etki `logger.info` ile yazılır: `"regen bütçesi: kalan=X, sonraki ana çekimler
  için ayrılan=Y"`.

**Kanıtlanabilir etki (ep07 senaryosu, cap 1900, müziksiz):**

| | Bugünkü davranış | R3 sonrası |
|---|---|---|
| Üretilen ana çekim | 5/6 (çekim 6 engellendi) | **6/6** |
| Kullanılan regen | 3 | 3 |
| Bölüm sonucu | ❌ üretilemedi | ✅ birleşir ve yayınlanır |

**PROOF:** YENİ `tests/test_main_shot_reserve.py` , yukarıdaki tabloyu birebir simüle eden
bir test (cap 1900, omni 10 sn, 6 çekim, 1-4 arası birer regen): R3 öncesi çekim 6 bloklanır,
R3 sonrası bloklanmaz; `reserve=0.0` varsayılanıyla eski davranış bit-değişmez;
tahmin `None` iken isteğe bağlı çağrı reddedilir.
Ek: `python -m pytest tests/test_credit_gate.py -q` yeşil.

---

## 6. ROCK 4 , ARAÇ ONARIMI + PLAN YENİLEME

Tur-1'in F-13..F-20 bulgularının tamamı buraya toplandı. Araçlar önce onarılır, sonra
planlar yeniden üretilir , yoksa "kanıt" yalan söyler.

- **R4-a** `tools/rf_prompt_lint.py`: `_PENDING_PARTS = range(6, 11)` sabiti KALKAR; denetim
  kapsamı `series.json`'daki `next_part`'tan türetilir (`next_part`..`total_parts`).
  part06 artık YAYINLANMIŞ ve korunmuş veridir; yeni kuralla denetlenmesi hem yanlış hem
  imkânsızdır (F-13).
- **R4-b** `tools/rf_transition_check.py:170`: `next_part != 6` sabiti KALKAR; `--verify`
  değeri **snapshot'takiyle** karşılaştırır (F-17). Canlı durum zaten 7; bugün `--verify`
  hatalı çalışıyor.
- **R4-c** `tools/rf_transition_check.py`: snapshot artık korunan plan DOSYALARININ ham
  SHA-256'sını da alır (`plans/part01..part<next_part-1>.json`) ve `--verify` bunları
  bire bir karşılaştırır (F-18). Bugün yalnız `series.json.parts` metadata'sı ve
  `published.json` mühürleniyor, yani korunan plan dosyası değişse kanıt yine geçiyor.
- **R4-d** `--verify` korunan planlarda `doctrine_sha256` eşitliği ARAMAZ; yayınlanmış
  part06 eski damgayı taşır ve taşımaya devam edecektir (F-14). Yeni damga yalnız yeniden
  üretilen part07-10 için zorunludur.
- **R4-e** Var olan test beklentileri güncellenir (F-20) , İZİN VERİLEN TAM LİSTE:
  - `tests/test_doctrine_gate.py:493` , `required_layers` beklentisi
    `["hook_teaser", "native_audio"]`.
  - `tests/test_doctrine_gate.py` içindeki from-scratch **müzik çağrısı** iddiası
    (`generate_background_music` çağrıldı + `MUSIC_PROMPT_ALIASES`) , müziğin ARTIK
    çağrılmadığını iddia edecek şekilde çevrilir.
  - `tests/test_doctrine_gate.py:472` from-scratch cfg üçlüsündeki `music_prompt` beklentisi.
  - `tests/test_rf_transition_check.py:32,88` , `next_part` fikstürü.
  Bu dört yer DIŞINDA hiçbir mevcut test iddiası değiştirilmez. Başka bir test kırılırsa
  Codex `BLOCKED:` yazıp DURUR (test yeniden yazmak yasak).
- **R4-f** Plan geçişi, `finally` ile geri alınabilir tek bir betikle (F-15/F-16):
  1. `python tools/rf_transition_check.py aimagine/from-scratch --snapshot`
  2. `series.json` yedeklenir.
  3. `plans/part07..part10.json` silinir.
  4. `total_parts: 6` **ve** `auto_replenish.batch: 4` geçici olarak yazılır
     (batch 5 kalırsa part11 üretilir , F-15).
  5. Replenish koşar.
  6. `total_parts: 10`, `batch: 5`, `next_part: 7` **doğrulanır ve geri yazılır**.
     Herhangi bir adım patlarsa `series.json` yedekten geri yüklenir , `next_part 7 >
     total_parts 6` çökme durumu diske KALICI olarak yazılmaz (F-16).
  7. Son kontrol: `next_part == 7`, `total_parts == 10`, `batch == 5`, plans 7-10 var,
     11 YOK.
- **R4-g** Her yeni plan için
  `python -m series.preflight --series from-scratch --plan aimagine/from-scratch/plans/partNN.json`
  exit 0 (F-19: `--plan` gerçek dosya yolu ister).
- **R4-h** `python tools/rf_prompt_lint.py aimagine/from-scratch` , 0 ihlal.
- **R4-i** `python tools/rf_transition_check.py aimagine/from-scratch --verify` , parts 1-6
  ve `published.json` bit-değişmez.

---

## 7. CANLI KAPI , ölçüm (kod işi değil)

**Tur-1 F-22 kabul.** Sentetik ffmpeg testleri Omni'nin gerçek davranışını kanıtlamaz.
Bu yüzden build'den sonra, cron'un bir sonraki koşusundan ÖNCE, İhsan onayıyla **tek klip
canary'si**: yeni `art_style` + yeni çekim-2 prompt'uyla tek bir 10 sn Omni klibi üretilir
(~126 kredi), inip ffprobe + Gemini ses denetimi + Gemini görüntü denetiminden geçirilir.
Alet sesi yoksa veya inşa hâlâ kendi kendine oluyorsa, tam bölüm hiç harcanmadan dönülür.

Sonraki iki canlı bölümün kapısı:

| Metrik | Hedef | Bugün |
|---|---|---|
| İlk-deneme QC geçişi (2 bölüm) | ≥ 8/12 | 4-5/11 |
| Yayınlanan bölüm | 2/2 (R3 sonrası artık bütçe öldürmemeli) | 1/2 |
| `issues`'ta "appear abruptly / jump rather than flow" | 0 | 5 |
| `event="audio"` kaydında `has_music` | false | ölçülmüyor |
| `event="audio"` kaydında `construction_sounds` | boş değil | ölçülmüyor |

---

## 8. OTOMASYON DENETİMİ (İhsan'ın 5. maddesi)

### 8.1 AImagine'e ZATEN entegre olanlar (dosyadan doğrulandı)

| # | Proje | Bağ | Durum |
|---|---|---|---|
| , | **Motor** (`Projeler/Youtube`) | `.github/workflows/from-scratch.yml`, günlük cron | ✅ CANLI (bugün başarısız) |
| , | **Upload-Post** | motor içinden YouTube + Instagram + TikTok | ✅ CANLI (ep06 üçüne de gitti) |
| 6 | YouTube_Yorum_Otomasyonu | `.github/workflows/aimagine.yml`, `YOUTUBE_CHANNEL_ID: UCCgbHTzYKYawUT6zEo0nlDg`, cron `0 7 * * *`, `YT_PHASE: "1"` | ✅ CANLI (Faz-1 salt-rapor) |
| 35 | Akilli_Watchdog | `config.py:139` → `#19 YouTube Otomasyonu`, repo `youtube-automation` | ⚠️ İZLİYOR ama `cron_hint: []` |
| 36 | Proje_Dashboard | `config/projects.yaml` | ✅ CANLI |
| 13 | YT_Aciklama_Otomasyonu | AImagine kanalına kurulu | 🚫 EMEKLİ (cron YAML'da yorumlu) |
| 14 | Gizli_Video_Otomasyonu | `aimagine_oauth_kur.py`, kanal ID bağlı | 🚫 DURAKLATILDI (schedule yorumlu; kanal `publish_mode=auto` ile doğrudan public yayınlıyor) |

### 8.2 Bu talep için gereken YENİ otomasyon: YOK

Ses ve işçilik sorunu motorun kendi prompt yüzeyinde ve teslim zincirinde çözülür. Yeni bir
servis kurmak bu iki soruna dokunmaz.

### 8.3 Gerçek boşluk , nöbetçi bu kanalın başarısızlığını GÖREMİYOR

Bugün ep07 çöktü, Actions "success" yazdı. `from-scratch.yml`'de `python ... | tee log`
boru hattı `pipefail` olmadan koşuyor, çıkış kodu maskeleniyor. Nöbetçi (#35) bu repoyu
izliyor ama baktığı sinyal yalan. **Dört kanalın üretim başarısızlığı nöbetçinin kör
noktasında** , hafızadaki "3,8 günlük 4-kanal sessizliği" olayının tam mekanizması.
Onaylı Plan 1 ROCK 3 bunu çözüyor ve hâlâ yapılmadı (ISSUES I-A).

### 8.4 Eklemeye DEĞER (öneri, bu koşunun kapsamı dışında)

| Öneri | Ne kazandırır | Maliyet |
|---|---|---|
| **#9 Notion Performans'ı AImagine'e klonla** | KONSEPT §5 kill-gate'i 7-günlük olgun performans verisi olmadan ÇALIŞMAZ | 1 saat, reçete hazır |
| **#34 İtibar Radarı'nı AImagine'e aç** (FAZ 6) | "Bu adam hiçbir şey yapmıyor" tipi yorum bu şikâyetin ERKEN uyarısıydı | 3-4 saat |
| **Higgsfield `video_analysis_create` / `virality_predictor`** (#27 eklentisinde kurulu) | Yayınlanan bölümü makineye izletmek. ROCK 1'in `qc_audio`'su bunun ses yarısını zaten getiriyor | kredi + oturum doğrulaması yapılmadı |
| **Apify `scraptik--tiktok-api`** | Referans hesapların gerçek viral verisi; bugün format kopyalama gözleme dayanıyor | Apify kredisi |

### 8.5 Kapsam dışı

#33 TikTok Boost (hesap yok) · #19 · #18 NOVASCEND · #26/#27/#28 (iş kolu) · #13 ve #14
(emekli/duraklatılmış).

---

## 9. İHSAN'A AÇIK SORULAR (bloke etmez, ayrı karar)

1. **Tek klip canary'si (~126 kredi)** , tam bölüm harcanmadan önce yeni prompt'un
   sesini ve işçiliğini doğrulamak. Öneri: EVET.
2. **`EPISODE_CREDIT_CAP` 1900 → 2200?** ROCK 3 bölümün çıkmasını garantiler ama regen
   sayısı 3'te kalır. 2200, 6 ana + 5 regen finanse eder (gerçek maliyet ~126/klip olduğu
   için beklenen artış ~250 kredi/bölüm). Öneri: ROCK 3'ün etkisi ölçülene kadar BEKLE.

---

## 10. ISSUES (bilinçli YAPILMAYANLAR)

- **I-A (yüksek):** Plan 1 ROCK 3 , `bash -euo pipefail` + `ok is not True` çıkışı, 4
  workflow. Actions'ın yalan "success"'i nöbetçiyi kör ediyor (§8.3).
- **I-B (yüksek):** `critic.strengthen_prompt` (`critic.py:273`) Gemini'nin `fix_notes`'unu
  regen prompt'una AYNEN ekliyor, notlar olumsuzlama taşıyor. Onarım yalnız İLK denemeyi
  kapsıyor. Motor kodu, dört kanal ortak.
- **I-C (orta):** Ghosting/çift pozlama ep07'nin baskın kusuru; kök neden ölçülmedi.
- **I-D (orta):** Kredi tavanı kararı (§9.2).
- **I-E (düşük):** Müziksiz kesişte ton sıçraması kalırsa `acrossfade` çözüm değil
  (senkron kayar); ayrı tasarım gerekir.
- **I-F (düşük):** `from-scratch.yml` başlık yorumu iki doktrin sürümü bayat.
- **I-G:** R2-c "görünür eylem" satırının skorlanmaya terfisi (tetik §7).
- **I-H:** §8.4'teki dört otomasyon önerisi.
- **I-I:** Ses kapısı düşerse klipler önbellekte kalır ve sonraki koşu aynı sonuca varır;
  bilinçli olarak otomatik silmiyoruz, gürültülü duruyoruz (tur-1 F-5).
- Devralınanlar: usta için Kie referans-görseli, çekim 3→4 referans köprüsü, cross-shot QC.

---

## 11. DOKUNULMAZ

- `aimagine/from-scratch/plans/part01..part06.json` ve `published.json` , bit-değişmez.
- `series.json` → `next_part: 7`, `parts` bloğu, `status`, `publish_mode`, `priority`.
- Diğer üç kanalın (sentinal_ihsan, shadowedhistory, galactic_experience) hiçbir dosyası.
- `series/critic.py` `_QC_SYSTEM` metni , motor kodu, dört kanal ortak (I-B ayrı karar).
- `series/omni_api.py` `build_omni_payload` , Kie API'sine bilinmeyen alan EKLENMEZ.
- `core/cost_tracker.py` maliyet tabloları , tahminler bilerek muhafazakâr.
- Kök `.gitignore`, `master.env`, `credentials/`.
- Mevcut fonksiyon imzaları , yalnız EKLEME yapılır; `concatenate_audio_smooth`'un
  `fade: float = 0.25` varsayılanı DEĞİŞMEZ.
- R4-e'de listelenen dört yer dışında hiçbir mevcut test iddiası değiştirilmez.
