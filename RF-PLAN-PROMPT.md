# RF-PLAN-PROMPT , AImagine prompt yüzeylerinin elden geçirilmesi

**Tarih:** 2026-08-08 · **Karar sahibi:** İhsan · **Statü:** Same Page Meeting tur 4'e giren revizyon
**Kapsam:** yalnız `aimagine/from-scratch`. Diğer üç kanal yayınlıyor, prompt'larına DOKUNULMAZ.

## CORE FOCUS

AImagine bölümlerinin QC'den geçmesini sağlamak: ölçülen ilk-deneme geçme oranını %23,5'ten
en az %80'e çıkarmak, bunu yalnız veri dosyalarındaki prompt metnini değiştirerek yapmak.

> **REVİZYON GEÇMİŞİ.** T1: red tablosu `final_reject`'i çift sayıyordu; "yasakları `qc.notes`'a
> taşı" hamlesi kanıtın tersiydi. T2: yüzey haritası yanlıştı, Gemini `art_style`'ı GÖRÜYOR;
> olasılık tablosu formülsüzdü; kabul kapısı kendi hedefinin altındaydı. T3: plan uygulanabilir
> değildi çünkü **gerçek prompt metnini içermiyordu** , metin deneyin kendisi, tasarımı
> Visionary'nin işi. Bu sürüm birebir metinleri taşır.

---

## 1. ÖLÇÜM

Kaynak: `aimagine/from-scratch/qc_log.jsonl` , 48 kayıt, **27'si `event="review"`**.
Yalnız `review` sayılır; `final_reject` son incelemenin sebeplerini tekrarlar.

**İlk deneme geçme oranı: 4/17 = %23,5.** (Tüm denemeler: 6/27 = %22,2. Tek ölçüt ilk denemedir.)

| Red sebebi | Adet / 27 | QC alanı |
|---|---|---|
| artifact skoru ≥6 | 13 | `artifact_score` |
| prompt'un yasakladığı öğe görünüyor | 11 | `forbidden_elements` |
| anatomi bozuk | 9 | `anatomy_ok` |
| gömülü yazı/watermark | 6 | `unwanted_text` |

Canlı doğrulama: koşu 31263243153 (2026-08-08 14:57) Actions'ta "success", gerçek sonuç
`❌ Part 6 üretilemedi`; çekim 1 geçti, 2-3-4-5 düştü, çekim 6 kredi tavanında (1880/1900) kaldı.

### 1.1 Prompt yüzey haritası (T2'de kod okumasıyla düzeltildi)

| Yüzey | Kie görür | Gemini görür | Kanıt |
|---|---|---|---|
| `bible.art_style` | EVET | **EVET** | `shots.py:48,137` `f"{art}\n\n{base_prompt}"`; `produce.py:897` `qc_shot(..., kwargs["prompt"], ...)` |
| çekim `prompt` | EVET | EVET | aynı çözülmüş metin |
| `series.qc.notes` | HAYIR | EVET | `critic.py:196` |
| `auto_replenish.brief` | HAYIR | HAYIR | yalnız yazar LLM'e |

`produce.py:832`'deki *"HAM çekim promptu"* yorumu yalnız ücretsiz ön-linter `critic.lint_prompt`
içindir. Bu, düzeltmeyi basitleştirir: `art_style` tek hamlede iki yüzeyi birden temizler.

### 1.2 Gemini'nin kendi gerekçeleri (`issues`)

`The 'CAT' logo is visible on the excavators` · `Readable logo 'WORKSAFE' on worker's glove`
· `Logo/text 'solozem' visible on wheelbarrow` · `A readable 'DANGER' sign is visible on the
fence` · `The text on the gate is misspelled as 'JURASSICK PARK'` · `Open flames (torches) are
present on the gate ... explicitly forbidden` · `Workers' hands and fingers are frequently
distorted, appearing blobby or fused` · `Workers are cloned and appear inconsistently` ·
`Workers in the final frame are making celebratory/presentation gestures, which is explicitly
forbidden by the channel-specific notes` · `The scene abruptly morphs and blends between
construction and finished states`

### 1.3 Kök nedenler

**KN-1 , Fotoreal inşaat marka logosu üretir; yasak, logoyu SAYDIRAN şeydir.** `critic.py:117`:
sahne içindeki doğal yazı `unwanted_text` DEĞİLDİR, *"unless the prompt explicitly forbids it"*.
Yasak cümlesi doğal bir CAT logosunu başarısızlığa çevirir.
**KN-1a , atıf belirsiz:** yasak iki kritik-görünür yüzeyde birden (`art_style` + `qc.notes`);
plan tek kaynak iddia etmez, ikisinden birden kaldırır.
**KN-1b , `unwanted_text` sıfırlanmayabilir:** `_QC_SYSTEM` bindirme yazısını yasaktan bağımsız
reddeder ve marka izini "bindirme" diye sınıflayabilir. HİPOTEZDİR; §4.1 ayrı sayar.

**KN-2 , Kalabalık = anatomi vergisi.** Log çoğul "workers" suçluyor. İki kaynak: doktrinin
"yardımcı işçiler görünebilir" izni ve `art_style`'ın her prompt'a eklediği
`skilled hands and crews in safe working conditions`.

**KN-3 , `qc.notes` `artifact_score` tanımını bozuyor.** Not *"...is an artifact"* diyor,
`critic.py:119` ise skoru yalnız *"morphing/melting geometry, duplicated or broken objects,
impossible physics, glitch frames"* diye tanımlıyor. KONSEPT §7'de yazılı kasıtlı karar , KARAR-1.

**KN-4 , Açık alev de aynı tuzak.** Notlardaki güvenlik yasağı `forbidden_elements` tetikledi
(JURASSIC PARK kapısındaki meşaleler). Çözüm yasağı güçlendirmek değil, sahneye alev koymamak.

---

## 2. REFERANS KEŞFİ (İhsan talimatı 2026-08-08)

Playwright ile ziyaret edildi, grid ekran görüntüleri okundu.

**cairo_ia , 695K:** tek insan başrol, yüzü açık, ön planda. Absürt ölçekli TEK yapı. Bölünmüş
kare önce/sonra kancası. Altyazı: `Insane Tech Backyard Makeover: Apple vs Android!😲`.

**buildingwithtan , 505K:** ilk karede büyük POST bindirme yazısı (`THE INSIDE`,
`FROM RUSTY WRECK... ...TO SHOW CAR!`, `BEFORE | AFTER`), sağ üst köşe kutusu + turuncu ok,
sert dikey ayraç. Yüksek doygunluklu tek figür, arkadan ama okunacak kadar yakın.

**Bu turda alınan TEK mekanik: kadrada TEK FİGÜR.** Gerekçe estetik değil ölçüm: iki referansta
da bir kişi var, bizde kalabalık var, ve kalabalık KN-2'nin ta kendisi.

**ISSUES'a gidenler** (T2: aynı turda ikinci deney ölçümü kirletir): doygun turuncu kıyafet
(I-8), absürt ölçek (I-5), post bindirme + köşe kutusu (I-2), bölünmüş kare (I-3), taraf
tutturan başlık (I-4).

**Doktrin sınırı:** KONSEPT §3.5 , format kopyalanır; videolar, yapılar, karakter kimliği
kopyalanmaz. cairo'nun yüzü ve marka logolu havuzu KULLANILMAZ.

---

## 3. BUGÜN KOPYALANAMAYAN ŞEY

`bible.json` → `characters: []` boş; `critic.py:149` yüz referansını `ref_image_url`'den okur;
referans yoksa `face_match` null kalır. Tanınan başrol için ön koşul: USTA referans görseli
(I-1). **Bu plan yüzü AÇMAZ.**

---

## ROCK 1 , Yasakları kaldır, kalabalığı kaldır, QC notunu düzelt

**Dosyalar:** `aimagine/from-scratch/bible.json`, `aimagine/from-scratch/series.json`,
`aimagine/KONSEPT.md`, yeni `tools/rf_prompt_lint.py`, yeni `tests/test_rf_prompt_lint.py`

Aşağıdaki bloklar **birebir kopyalanacak metinlerdir** (T3 F-1). Uygulayıcı bunları yeniden
tasarlamaz; JSON'a gömerken yalnız kaçış karakterlerini düzenler.

### 1a. `bible.json` → `art_style` , TAM DEĞİŞTİRME

```
Photoreal construction timelapse realism in vertical 9:16, bright daylight, saturated but believable color, tactile real materials with matte weathered surfaces, coherent site geography, and satisfying build progression. LOCKED-OFF TRIPOD camera: one fixed position and angle held through the shot, with a slow zoom as its single camera move. A single silent builder works alone at mid-distance in a dark cap, dark crew-neck and work gloves, framed from behind or in profile with the full body inside the frame.
```

Çıkanlar: `skilled hands and crews in safe working conditions` (KN-2),
`No CGI sheen, no text, no logos, no watermarks` (KN-1), `face never in close-up` (negasyon),
`only slow zoom allowed` (kısıtlama dili). Kıyafet rengi bu turda DEĞİŞMEZ (I-8).

### 1b. `bible.json` → `series.qc.notes` , TAM DEĞİŞTİRME

```
This channel builds exactly one structure and delivers exactly one final reveal; record any second structure or second reveal under issues. Camera-lock drift across a chained shot, a change in the recurring builder's cap, crew-neck, gloves or established look, and a break in the structure's material or design language are continuity observations: record them under issues. Reserve the numeric score for genuine generation defects as defined in your instructions. Celebration, presentation gestures, looking at camera and ta-da poses are forbidden in this channel. hook_shot is 6 and the hook teaser comes from near the end of shot 6 while the finished exterior is visible.
```

Çıkanlar: `readable text, logo, caption, or watermark` yasağı (KN-1a), `is an artifact`
ifadesi (KN-3), güvenlik yasağı (KN-4 , sahne tasarımına taşındı, brief madde 8).
**Dikkat:** üçüncü cümle bilerek `artifact` kelimesini KULLANMAZ ("the numeric score"), çünkü
denetçi kuralı (d) `artifact` ile süreklilik kelimelerinin aynı cümlede geçmesini reddeder ve
notun kendisi de bu kurala uymak zorundadır.

### 1c. `series.json` → `auto_replenish.shot_plan` , TAM DEĞİŞTİRME

Aşağıdaki **JSON dizisi doğrudan `auto_replenish.shot_plan` değerinin yerine geçer.** Numara
etiketi, madde işareti veya başka hiçbir ek YOKTUR; dizi olduğu gibi kopyalanır (T4 F-1: etiketli
sürümde çekim 6 kelime sınırını 46'ya çıkarıyordu). Her satır ≤45 kelimedir.

```json
[
  "CAMERA A, CHAIN BREAK: open a fresh exterior scene in a locked-off tripod wide shot, with a slow zoom as its single camera move. Grade an empty lot, lay out road, fence and landscaping first, then mark the foundation. The builder arrives with materials.",
  "CAMERA A, CHAINED: continue from shot 1's final frame in the same locked-off tripod framing, with a slow zoom as its single camera move. Raise foundation, walls and roof frame inside that same composition with accelerating timelapse energy and satisfying material flow.",
  "CAMERA A, CHAINED: continue from shot 2's final frame in the same locked-off tripod framing, with a slow zoom as its single camera move. Finish cladding, roof, paint, exterior lighting and landscaping until the completed exterior stands clearly in frame.",
  "CAMERA B, CHAIN BREAK: open a fresh interior wide scene on a locked-off tripod, with a slow zoom as its single camera move. Build interior walls, lay flooring, install utilities and lighting infrastructure, carrying the exterior's materials and design language inside.",
  "CAMERA B, CHAINED: continue from shot 4's final frame in the same locked-off tripod framing, with a slow zoom as its single camera move. Install furniture and decor, bring the lighting up, and finish the interior until it looks ready to live in.",
  "REVEAL TOUR, CHAINED FROM CAMERA B: continue from shot 5's final frame with the tripod lock released for one unbroken move that begins inside, passes through a door or window, and settles on a wide exterior of the finished structure while the builder keeps working."
]
```

Kıyafet tarifi altı satırdan da çıktı (artık `art_style`'da, tek kaynak). Negasyon sıfır.
İnce motor iş sıfır.

### 1d. `series.json` → `auto_replenish.brief` , TAM DEĞİŞTİRME

```
FROM SCRATCH üretim brief'i (dayanak: aimagine/KONSEPT.md v2.1, 2026-08-08). >>> ÇIKTI DİLİ İNGİLİZCE <<< Bu brief Türkçedir ama bölüm başlığı, synopsis, tüm çekim prompt'ları ve müzik tarifi İngilizce yazılır. DEĞİŞMEZ KURALLAR: (1) İMZA FORMAT: Tek yapı, altı çekim, yaklaşık 60 saniye. Çekim 1 boş arsada çevre ve zeminle başlar; çekim 2 gövdeyi yükseltir; çekim 3 dışı tamamen bitirir; çekim 4 bağımsız iç zinciri kurar; çekim 5 içi tamamen döşer; çekim 6 içeriden dış geniş finale akan tek kesintisiz reveal turudur ve hook_shot her zaman 6'dır. (2) SABİT KARE + ZİNCİR: Kamera-A çekim 1-3'te, Kamera-B çekim 4-5'te tripod kilidindedir; yalnız yavaş zoom serbesttir. Çekim 1 ve 4 yeni sahne açar, diğerleri önceki son kareden zincirlenir. Bölümler arasında zincir yoktur. (3) TEK FİGÜR: Kadroda TEK bir sessiz usta vardır. Yardımcı işçi, ekip, kalabalık, izleyici YAZILMAZ. Usta arkadan, yandan veya orta mesafeden TAM VÜCUT kadrajda görünür; kıyafeti bible art_style'da tanımlıdır ve çekim prompt'unda TEKRARLANMAZ. Ustaya el veya parmak yakın planı gerektiren ince motor iş verilmez; yürür, taşır, işaret eder, gözlemler. (4) AİLE ROTASYONU: family yalnız altı kanonik aileden biri olur ve aynı aile art arda kullanılamaz. Bölüm başına tek yapı ve tek reveal vardır; iç mekan aynı yapının içidir. Doktrin bölüm 6 yalnız ilham konularıdır; seed_id ve topic_pool yoktur. Başlık her zaman beş title_style kalıbından üretilir, aile kısıtına uyar, boşluklar ve emojiler dahil en fazla 60 karakterdir; değer kancasını korumak için <X>/<Y> kısaltılır, $<N> atılmaz. (5) SES: Narration ve voiceover yoktur; tek ses inşaat ritmine senkron sabit tempolu perküsif müziktir. Çekim 5 sonunda tek vuruş yumuşar, çekim 6'da açılır, yumuşak kapanır; loop dikişi yoktur. (6) YORUM YEMİ: Bölüm başına en fazla bir yarım-soru; rage-bait yasaktır. (7) SAHNE TASARIMI, YASAK CÜMLESİ DEĞİL: Aşağıdaki nesneler sahneye HİÇ KONULMAZ, çünkü fotoreal üretimde marka izi ve okunur yazı doğururlar: signage, sign, billboard, poster, banner, scoreboard, lettering, screen, monitor, display, logo, brand mark, license plate, number plate, branded machinery. Yerine: yüzeyler boyalı ve dokuludur, aydınlatma ışık kaynağının kendisiyle anlatılır, makineler sade ve markasızdır. ÇOK ÖNEMLİ: bu liste YAZARA aittir. Üretilen çekim prompt'unda bu kelimelerin HİÇBİRİ geçmez ve hiçbir yasak/olumsuzlama cümlesi ("no", "never", "without", "avoid") YAZILMAZ; sahne bu nesneler olmadan kurulur. (8) GÜVENLİK, SAHNE TASARIMIYLA: korumasız elektrik işi, güvenliksiz derin kazı ve açık alev (meşale, ateş, kaynak alevi) sahneye KONULMAZ; yapı fantastik ama güvenli görünür. (9) ÇEKİM PROMPT'U YAZIMI: her çekim prompt'unun gövdesi yalnız O BÖLÜME ÖZGÜ sahneyi anlatır. shot_plan öneki motor tarafından zaten eklenir; önekin kamera, faz veya usta cümlelerini kendi sözcüklerinle TEKRARLAMA. Gövde en fazla 60 kelimedir.
```

Madde 9 tekrar sorununun (denetçi kuralı e) kaynağına iner: bugün yazar öneki kendi
sözcükleriyle tekrarlıyor ve normalizasyon yalnız birebir yankıyı kırpıyor.

### 1e. `aimagine/KONSEPT.md` , iki paragraf + sürüm

Başlık satırı `v2.0` → `v2.1` ve şu not eklenir:
```
**v2.1 (2026-08-08, prompt onarımı):** Kadroda tek figür (yardımcı işçi izni kalktı);
okunur yazı/logo yasağı art_style ve qc.notes'tan kaldırıldı (üretim yasağı değil, sahne
tasarımı kuralı oldu); qc.notes artık süreklilik sapmasını artifact skoruna yazdırmıyor;
güvenlik kuralı yasak cümlesinden sahne tasarımına taşındı. Gerekçe: 27 QC incelemesinde
ilk-deneme geçişi %23,5 ve dört red sebebinin dördü de bu kurallardan besleniyordu.
```

§3.1 USTA paragrafı TAM DEĞİŞTİRME:
```
**USTA (tek tekrarlayan figür, KADRODA TEK KİŞİ):** Her bölümde AYNI sessiz usta çalışır: koyu
bere/şapka, koyu üst, iş eldivenleri; arkadan, yandan veya orta mesafeden TAM VÜCUT kadrajda
görünür , yüz yakın planı yoktur (humans "allowed" motor kuralı; yüz tutarlılığı riski
tasarımla sıfırlanır). **Yardımcı işçi, ekip veya kalabalık YAZILMAZ** (v2.1, 2026-08-08;
gerekçe ölçüm: 27 QC incelemesinin 9'unda anatomi redi var ve Gemini'nin gerekçeleri çoğul
"workers" figürlerini suçluyor , klonlanmış, bulanık, füzyon parmaklı). Usta konuşmaz,
kameraya bakmaz, ince motor iş yapmaz.
```

§3.5'teki **Güvenlik** maddesi TAM DEĞİŞTİRME (T4 F-2: KARAR-1 madde 4'ün karşılığı):
```
- **Güvenlik (v2.1: yasak cümlesi değil, sahne tasarımı):** tehlikeli inşaat pratiği
  özendirilmez. Korumasız elektrik işi, güvenliksiz derin kazı ve açık alev (meşale, ateş,
  kaynak alevi) SAHNEYE KONULMAZ; bu kural brief madde 8 ile yazara verilir, QC notunda yasak
  cümlesi olarak DURMAZ (gerekçe: JURASSIC PARK kapısındaki meşaleler tam bu yasak yüzünden
  `forbidden_elements` redi aldı). Sahne fantastik ama güvenli görünür.
```

§3.5'in geri kalan maddeleri (başlık kalıpları, hashtag, AI disclosure, esinlenme sınırı)
BAYT DEĞİŞMEZ.

§7'deki `bible.json` maddesinin `qc.notes` cümlesi TAM DEĞİŞTİRME:
```
`qc.notes` v2.1: süreklilik gözlemleri (kamera kilidi kayması, usta görünüm değişimi, yapı
stil kopması) `issues` alanına yazılır, sayısal skora GİRMEZ; okunur yazı/logo/watermark
yasağı nottan KALDIRILDI (bindirme denetimi _QC_SYSTEM'in kendi tanımıyla yapılır); kutlama/
ta-da/kameraya bakış yasağı KALIR; hook_shot=6 + teaser kaynağı çekim 6.
```

### 1f. `tools/rf_prompt_lint.py` , makine denetçisi (yeni)

**Kapsam (T2 F-7):** `art_style` ve `qc.notes` her zaman denetlenir. Plan denetimleri YALNIZ
**bekleyen `plans/part06.json`..`part10.json`**'a uygulanır; part 1-5 eski dört-çekim
doktrininin yayınlanmış planlarıdır.

**Normalizasyon (T2 F-4, T3 F-2):** NFKC → küçük harf → `’`/`‘` → `'`. Yasaklı-nesne
taraması TİRE KORUNARAK yapılır (`-free` soneki için), sonra `[^a-z0-9'-]` → boşluk. Sözcük
eşleşmesi `\b<kök>s?\b` (tekil+çoğul), büyük/küçük harf duyarsız.

**KANONİK YASAKLI NESNE LİSTESİ** , brief madde 7 ile BİREBİR AYNI olmak zorundadır
(T3 F-2; denetçi bu listeyi tek bir sabitten okur ve test bu eşitliği doğrular):
```
signage, sign, billboard, poster, banner, scoreboard, lettering, screen, monitor,
display, logo, brand mark, license plate, number plate, branded machinery
```

Sıfır-dışı çıkar eğer:
- **(a) Negasyon** , çözülmüş yükte (`art_style + "\n\n" + shot.prompt`, `shots.py:48` ile
  birebir aynı kurulur): `never | no | not | nor | none | avoid | without | exclude | lacking
  | devoid | only | sole` kelime sınırıyla, artı `free of`, artı `-free` soneki, artı `don't`.
- **(b) Yasaklı sahne nesnesi** , bekleyen plan GÖVDELERİNDE (önek çıkarıldıktan sonra),
  yukarıdaki kanonik listeden. Bugünkü `part08` çekim 4 (`holographic display systems`)
  ZORUNLU başarısız fixture'dır.
- **(c) Uzunluk** , `shot_plan` satırı > 45 kelime, veya plan gövdesi > 60 kelime.
- **(d) QC notu skor kirlenmesi** , `qc.notes` cümlelere bölünür; bir cümlede `artifact`
  kelimesi ile `drift | composition | consistency | wardrobe | appearance | style | geography
  | lock | continuity` kelimelerinden biri birlikte geçiyorsa hata.
- **(e) Tekrar** , her çekim için `_prompt_content`'in eklediği `shot_plan` öneki gövdeden
  ayrılır; iki metin (a)-normalizasyonundan geçer; 8-kelimelik n-gram KÜMELERİ çıkarılır;
  `|önek ∩ gövde| / |gövde|` > 0,30 ise hata. Bugünkü `part06` çekimleri ZORUNLU başarısız
  fixture'dır (gövde öneki kendi sözcükleriyle tekrarlıyor).

**Dürüstlük maddesi (T1 F-8):** denetçi yalnız İLK denemeyi kapsar. `critic.strengthen_prompt`
(`critic.py:273`) Gemini'nin `fix_notes`'unu aynen ekler ve o notlar negasyon içerir , log'daki
gerçek örnek: `"Ensure no readable logos or text appear on clothing or equipment within the
scene."` Düzeltmesi motor kodudur, dört kanal ortak , I-6.

**`tests/test_rf_prompt_lint.py` en az şunları kanıtlar:** (a) bugünkü `art_style` düşer,
yenisi geçer; (b) `part08` çekim 4 `display` yüzünden düşer; (c) `part06` tekrar oranından
düşer; (d) bugünkü `qc.notes` düşer, yenisi geçer; (e) denetçinin kanonik listesi brief madde
7'deki listeyle birebir aynıdır; (f) `north`, `nozzle`, `design language`, `nothing` gibi
yanlış-pozitif tuzakları geçer; (g) `signage-free` yakalanır.

**Done looks like:** denetçi (a)-(e)'nin hiçbirini bulmuyor; 128 test + yeni testler yeşil;
preflight OK.

**PROOF:** (baseline 2026-08-08: `128 passed, 34 subtests passed`, `PREFLIGHT OK`)
```
python -X utf8 -m pytest tests/ -q
python -X utf8 -m series.preflight --series from-scratch --plan aimagine/from-scratch/plans/part06.json
python -X utf8 tools/rf_prompt_lint.py aimagine/from-scratch
```

---

## ROCK 2 , Bayat planları yeniden üret

ROCK 1 `KONSEPT.md`'yi değiştirir → `doctrine_sha256` değişir → bekleyen `plans/part06..10.json`
eski damgalıdır ve `produce` onları zaten reddeder.

**Bilinen tuzak (KONSEPT §7):** planlar silinmeden `total_parts` 5'e çekilmezse replenish beş
"bekleyen" part görür ve NO-OP kalır.
**T1 F-15/F-16:** `replenish.py:1195` `total_parts`'ı kendi kaydeder; `_adopt_orphans`
(`replenish.py:334`) yarım dosyaları sahiplenir. Elle geri taşıma adımı KALDIRILDI.

### 2a. `tools/rf_transition_check.py` (yeni, çalıştırılabilir kapı)

- `--snapshot` : `series.json`'ın `parts` alt ağacını **kanonik JSON** (`sort_keys=True`,
  `ensure_ascii=False`, `separators=(",",":")`) olarak SHA-256'lar, `published.json`'ı ham
  bayt olarak SHA-256'lar, ikisini + `total_parts` + `next_part` + geçerli `doctrine_sha256`'yı
  `aimagine/from-scratch/.rf_transition.json` sidecar'ına yazar. Dosya varsa ÜZERİNE YAZAR ve
  eski değeri `previous` alanında saklar.
- `--verify` : sidecar YOKSA veya `doctrine_sha256` alanı güncel doktrinle eşleşmiyorsa
  (bayat snapshot) hata verir. Ayrıca sıfır-dışı çıkar eğer:
  - `plans/part06..10.json` beşi de yok, VEYA
  - beşinden biri güncel `doctrine_sha256`'yı taşımıyor, VEYA
  - `plans/` içinde numarası **10'dan büyük** herhangi bir plan var (T3 F-4: taşma), VEYA
  - `total_parts != 10` veya `next_part != 6`, VEYA
  - `parts` kanonik SHA'sı ya da `published.json` SHA'sı snapshot'tan farklı, VEYA
  - beş planın herhangi biri `series.preflight`'tan geçmiyor.

### 2b. Sıra
0. **ROCK 1 kontrol noktası (T4 F-3, ZORUNLU):** ROCK 1 bitip kanıtı geçtiğinde commit atılır
   (`chore: rock1 checkpoint`). ROCK 2 bu commit ATILMADAN başlamaz. `--snapshot` bu commit'in
   SHA'sını `git rev-parse HEAD` ile okuyup sidecar'a `checkpoint_sha` alanına yazar.
1. `python -X utf8 tools/rf_transition_check.py aimagine/from-scratch --snapshot`
2. `plans/partNN.json` , **NN ≥ 6 olan HEPSİ** silinir (T3 F-4).
3. `series.json` → `total_parts: 5`. `next_part: 6` DEĞİŞMEZ.
4. ~~`doctrine_sha256` yeniden pinlenir~~ , **ROCK 1'e TAŞINDI (Visionary kararı 2026-08-08).**
   Gerekçe: `KONSEPT.md`'yi değiştirip pin'i bayat bırakmak bir işlem sınırı değil, yarım kalmış
   bir düzenlemedir; bayat pin `test_doctrine_gate`'i kırıyor ve ROCK 1 kanıtı yeşil olamıyordu.
   ROCK 1'de motorun kendi fonksiyonuyla pinlendi:
   `918032a5eeb81fd9d5e55f210be5c54659874a62530cb02177028192630df6f3`.
5. replenish koşar; `total_parts`'ı kendisi 10'a taşır.
6. `--verify` koşar.

### 2c. Kurtarma (T3 F-4, F-5)
- **Plan/sayaç uyuşmazlığı:** `NN ≥ 6` olan TÜM plan dosyaları silinir, `total_parts` 5'e
  döner, replenish yeniden koşar. Kısmi durum asla ileri taşınmaz.
- **Korunan veri uyuşmazlığı** (`parts` 1-5 veya `published.json` değişmiş): replenish
  YENİDEN KOŞULMAZ. Snapshot yalnız hash tutar, onarım yapamaz. Geri alma, sidecar'daki
  `checkpoint_sha`'yı kullanarak ve **yalnız korunan iki dosyayı** hedefleyerek yapılır, böylece
  ROCK 1'in geri kalanı silinmez:
  `git checkout <checkpoint_sha> -- aimagine/from-scratch/series.json aimagine/from-scratch/published.json`
  Sonra durulur ve rapor edilir.

**PROOF:**
```
python -X utf8 -m pytest tests/ -q
python -X utf8 tools/rf_transition_check.py aimagine/from-scratch --verify
python -X utf8 tools/rf_prompt_lint.py aimagine/from-scratch
```

---

## 4. BÜTÇE ARİTMETİĞİ

`require_all_shots: true`, 6 çekim, adil pay çekim başına **1** regen (`6 // 6`), ve
`EPISODE_CREDIT_CAP = 1900` = 80 müzik + 6×200 ana + **yalnız 3×200 regen**.

```
P = p^6 · Σ_{k=0..3} C(6,k)·q^k        (p = ilk deneme geçişi, q = 1-p)
```
6 çekimden en fazla 3'ü ilk denemede düşebilir ve düşenlerin hepsi tek regen hakkıyla geçmeli.
**VARSAYIM:** ilk deneme ve regen aynı, bağımsız `p`'ye sahip. Bu ölçülmedi.

| İlk deneme `p` | Bölüm başarısı |
|---|---|
| %23,5 (bugün) | **%0,4** |
| %50 | %16,0 |
| %60 | %33,0 |
| %75 | %66,7 |
| %80 | %77,6 |
| %85 | **%86,9** |
| %90 | %94,1 |

**Bu plan kredi tavanını DEĞİŞTİRMEZ.**

### 4.1 Kabul kapısı , geçici kanarya
- **Örneklem:** ROCK 2 sonrası ardışık **3 bölüm** (18 çekim). Bu bir kanaryadır; sürdürülebilir
  ≥%80 iddiası DEĞİLDİR (T2 F-13).
- **Hijyen (T2 F-12):** koşudan ÖNCE `qc_log.jsonl` satır sayısı kaydedilir, yalnız yeni
  satırlar sayılır. Her yeni bölümde TAM 6 ayrı `shot` beklenir.
- **Skorlama:** çekim başına `attempt=0`'ın SON `skip`-olmayan kararı alınır. `attempt=0`'da
  hiç `skip`-olmayan karar yoksa o çekim **BAŞARISIZ** sayılır (T3 F-7). 18 çekimden azı
  toplanırsa kanarya **KALDI** sayılır.
- **Geçti:** ≥ **15/18** (%83,3). **Kaldı:** < 15/18. Ara bant YOK.
- **Ayrı raporlanır:** `forbidden_elements` sayısı, `unwanted_text` sayısı (KN-1b), ve
  yalnız-sapma vakalarının `artifact_score`'u.
- **Yalnız-sapma tanımı (T3 F-6):** bir inceleme, `issues` metinlerinin HEPSİ
  `drift|camera|composition|continuity|geography|material|design language|appearance`
  anahtarlarından birini içeriyor VE hiçbiri `morph|melt|ghost|duplicat|clone|fused|distort|
  glitch|physics|anatomy|hand|finger` içermiyorsa "yalnız-sapma"dır. Sınıflama otomatik
  yapılır ve HER vaka insan gözüyle doğrulanır; anlaşmazlıkta insan kararı geçer.
- Elle koşulur, kredi harcar , İhsan onayına bağlı.

---

## 5. NON-GOALS

- `critic.py`, `produce.py`, `replenish.py`, `series_runner.py`, `shots.py` , dört kanal ortak.
- `_QC_SYSTEM` ve `strengthen_prompt` (bkz. I-6).
- `require_all_shots: true` , İhsan'ın 2026-08-04 doktrin kararı.
- `EPISODE_CREDIT_CAP` , ölçümden önce değişmez.
- `title_patterns`, `title_style`, `music_style`, `families`, `chain_breaks`, `hook_shot`.
- Diğer üç kanalın hiçbir dosyası.
- Kredi harcayan gerçek üretim koşusu , İhsan onayına bağlı, build'in parçası değil.
- Denetçilerin CI'a bağlanması.

---

## KARAR-1 , İhsan onayı (build ÖN KOŞULU, T3 F-8)

ROCK 1 dört doktrin kuralını değiştiriyor; hepsi KONSEPT.md'de yazılı kasıtlı kararlardı:
1. `qc.notes` kamera kaymasını artık sayısal skora yazdırmayacak (§7).
2. Okunur yazı/logo yasağı hem `qc.notes`'tan hem `art_style`'dan çıkacak (§7).
3. Yardımcı işçi izni kalkacak, kadrada tek figür kalacak (§3.1).
4. Güvenlik kuralı yasak cümlesinden sahne tasarımına taşınacak (§3.5) , içerik standardı
   AYNEN korunur, yalnız uygulama yeri değişir.

**KARAR (İhsan, 2026-08-08): DÖRDÜ DE ONAYLANDI.** Build ön koşulu karşılandı. `KONSEPT.md`
v2.1'e çıkar ve `doctrine_sha256` yeniden pinlenir.

---

## 6. ISSUES

- **I-1 (yüksek):** USTA için sabit referans görsel + `characters` kaydı (§3).
- **I-2 (yüksek):** Post bindirme katmanı: ilk kareye büyük yazı + köşe kutusu + ok.
- **I-3 (orta):** Böl-ve-göster (split-screen önce/sonra) kancası.
- **I-4 (orta):** Taraf-tutturan başlık kalıbı (`... : A vs B!😲`).
- **I-5 (orta):** Absürt ölçek çapası (dev boru/kapı + yanında USTA).
- **I-6 (yüksek):** `strengthen_prompt` negasyonlu `fix_notes`'u regen prompt'una ekliyor.
- **I-7 (düşük):** `artifact_threshold: 6` kalibrasyonu.
- **I-8 (orta):** USTA kıyafetini doygun turuncuya çevirme , QC faydası kanıtsız, ROCK 1 ile
  aynı turda değiştirmek ölçümü kirletir.
