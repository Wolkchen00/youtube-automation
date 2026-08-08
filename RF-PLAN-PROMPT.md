# RF-PLAN-PROMPT , AImagine prompt yüzeylerinin elden geçirilmesi

**Tarih:** 2026-08-08 · **Karar sahibi:** İhsan · **Statü:** Same Page Meeting'e girecek taslak
**Kapsam:** yalnız `aimagine/from-scratch`. Diğer üç kanal (sentinal_ihsan, shadowed_history,
galactic_experience) yayınlıyor, onların prompt'larına DOKUNULMAZ.

## CORE FOCUS

AImagine bölümlerinin QC'den geçmesini sağlamak: deneme başına geçme oranını ölçülen %24'ten
en az %80'e çıkarmak, bunu prompt metnini değiştirerek yapmak, ve bunu yaparken cairo_ia +
buildingwithtan'ın kanıtlanmış görsel mekaniklerini formata almak.

---

## 1. ÖLÇÜM: neden yayınlanamıyor

Kaynak: `aimagine/from-scratch/qc_log.jsonl` (48 kayıt, 27 inceleme) + canlı koşu 31263243153
(2026-08-08 14:57). Actions "success" yazıyor ama gerçek sonuç `❌ Part 6 üretilemedi`.

**İlk denemede geçen çekim: 4/17 (%23,5).** `require_all_shots: true` açık olduğu için
6 çekiğin hepsi geçmek zorunda.

| Red sebebi | Adet | Kaynağı |
|---|---|---|
| prompt'un yasakladığı öğe görünüyor | 17 | `forbidden_elements` |
| artifact skoru ≥6 | 20 | `artifact_score` |
| anatomi bozuk | 14 | `anatomy_ok` |
| gömülü yazı/watermark | 8 | `unwanted_text` |

**Kritik ayrım:** 21 redden yalnız **2 tanesi** sadece artifact skorundan. QC eşiğini
gevşetmek işi çözmez. Sebep prompt metninin kendisidir.

### 1.1 Dört kök neden, her biri bir düzenlemeye bağlanır

**KN-1 , Yasak listesi üretim prompt'unun İÇİNDE.**
`critic.py:118` `forbidden_elements`'i şöyle tanımlıyor: *"the prompt explicitly forbids
elements ... and a frame clearly shows one."* From-scratch'in her çekim prompt'u
"never in face close-up" taşıyor, çekim 6 ayrıca "never celebrates, looks at camera, poses
'ta-da,' speaks". Aynı yasaklar dört ayrı yerde tekrarlanıyor: `shot_plan`, `brief`,
`art_style`, `qc.notes`. Her tekrar iki zarar veriyor: (a) video modeli negasyonu güvenilir
şekilde uygulamaz, "face close-up" ifadesi koşullamaya girer; (b) QC'ye yeni bir ceza maddesi
eklenir. Yayınlayan üç kanalda bu duvar YOK.

**KN-2 , Bölüm yazarı yasakları görmüyor, yasaklı şeyi sipariş ediyor.**
part06 çekim 3 prompt'u: *"install ... illuminated signage"*. Doktrin "okunur yazı, logo,
watermark" yasaklıyor. Yazar LLM'e ulaşan `brief` metninde yasak var ama üretilen sahne
tabelayı, ekranı, "large display panel"i rahatça yazıyor. ARCADE bölümünde bu garanti kayıp.

**KN-3 , Her çekimde insan + ince motor iş = anatomi vergisi.**
Doktrin USTA'yı 6 çekimin hepsinde istiyor. Yazar ona "guiding a crane", "placing a large
display panel", "connecting a final power cable" veriyor. `critic.py:74-84`'teki kendi
prompt linter'ı el/parmak yakın planını zaten riskli sayıyor.

**KN-4 , QC notu `artifact_score`'u yeniden tanımlıyor.**
`bible.json` → `qc.notes`: *"Any locked-camera drift ... or composition-lock violation within
a chained shot is an artifact."* Ama `critic.py:119` `artifact_score`'u *"morphing/melting
geometry, duplicated or broken objects, impossible physics, glitch frames"* diye tanımlıyor.
Doktrin uyumu artifact değildir. Zincirli çekimde kayma kaçınılmaz olduğu için skor 8-9'a
fırlıyor ve eşik 6'yı otomatik aşıyor. Kanıt: aynı bölümde çekim 1 (zincirsiz) 0/10 alırken
zincirli çekimler 6-9/10 alıyor. Bu, KONSEPT.md §7'de yazılı kasıtlı bir tasarımdır; bu plan
onu kategori hatası olarak değiştirmeyi önerir.

---

## 2. REFERANS KEŞFİ (İhsan talimatı 2026-08-08)

İki hesap Playwright ile ziyaret edildi, grid ekran görüntüleri okundu.

### 2.1 cairo_ia , 695K takipçi
- **Tekrarlayan insan başrol, YÜZÜ AÇIK.** Aynı adam: siyah şapka, güneş gözlüğü, siyah uzun
  kollu. Ön planda, orta ve yakın planlarda, elleri işin içinde.
- **Absürt ölçekli tek yapı:** çölde lastik duvarlı havuz, buzdağını kazma ile oyma, okyanusta
  paslı deniz feneri, mangrov bataklığında ahşap silindir kuyu.
- **Bölünmüş kare (split-screen) kanca:** sol yarı bakımsız "önce", sağ yarı bitmiş "sonra".
- **Altyazı formülü (canlı örnek):** `Insane Tech Backyard Makeover: Apple vs Android!😲`
  , kısa, iki nokta, tek emoji, TARAF TUTTURAN karşılaştırma.
- Kamera sabit değil, hareket ediyor.

### 2.2 buildingwithtan , 505K takipçi
- **İlk karede BÜYÜK bindirme yazı:** `THE INSIDE`, `FROM RUSTY WRECK... ...TO SHOW CAR!`,
  `BEFORE | AFTER`. Kalın, beyaz/sarı, gölgeli. Bu yazı POST'ta ekleniyor, üretilen klipte yok.
- **Köşe kutusu + ok:** sağ üstte küçük iç mekân görüntüsü, ona işaret eden turuncu kavisli ok.
  "Ödül var, izlemeye devam et" cihazı.
- **Sert dikey ayraçlı böl-ve-göster kompozisyonu.**
- **Yüksek doygunluklu kıyafet:** kırmızı kapüşonlu, turuncu kapüşonlu, mavi. Toprak/yeşil
  zeminden ayrışıyor. Çoğunlukla arkadan, ama insanı okutacak kadar yakın.
- Absürt ölçekli nesne: hendeğe indirilen dev beton boru, dev ahşap boru, mağara-ağzı kapı.

### 2.3 Doktrin sınırı
KONSEPT.md §3.5 (İhsan kararı): cairo_ia'nın **FORMATI** kopyalanır; videoları, yapıları,
karakter kimliği KOPYALANMAZ. Bu plan yalnız mekanik kopyalar: insan-ölçek çapası, absürt
ölçek, böl-ve-göster kancası, doygun kıyafet. cairo'nun yüzü, marka logolu havuzu
(Apple/Android) ve tan'ın kimliği KULLANILMAZ.

---

## 3. AÇIKÇA SÖYLENMESİ GEREKEN: bugün kopyalayamadığımız şey

Her iki referansın da en güçlü tek öğesi **tanınan, tutarlı bir insan başrol**. Bizde bu
BUGÜN mümkün değil, tercih meselesi değil mühendislik gerçeği:

`bible.json` → `characters: []` boş. `critic.py:149` `_fetch_ref_face()` yüz referansını
karakter kaydındaki `ref_image_url`'den okuyor. Referans yoksa `face_match` null kalıyor,
yani bölümden bölüme aynı yüz garanti edilemiyor. KONSEPT §3.1 yüzü tam bu yüzden gizliyor:
"yüz tutarlılığı riski tasarımla sıfırlanır".

Yani "yüzü öne çıkaralım" kararının ÖN KOŞULU var: USTA için sabit bir referans görsel
üretilip `characters`'a kaydedilmesi. Bu KONSEPT.md'nin kendi ISSUES listesinde zaten var
("usta için Kie referans-görsel/characterId kaydı"). Bu plan onu ROCK yapmaz, ISSUES'a yazar
ve İhsan'ın kararına bırakır. Bu plan yüzü açmaz; USTA'yı arkadan/orta mesafede tutar ama
**okunur ve ayrışır** hale getirir.

Aynı şekilde tan'ın bindirme yazısı ve köşe kutusu POST işidir, prompt işi değil. Hattımızda
post bindirme katmanı YOK. ISSUES'a gider.

---

## ROCK 1 , Prompt yüzeylerini negasyondan arındır (yalnız veri dosyaları)

**Dosyalar:** `aimagine/from-scratch/series.json`, `aimagine/from-scratch/bible.json`

### 1a. `series.json` → `auto_replenish.shot_plan` (6 satır)
Her satır şu üç kurala uyacak şekilde yeniden yazılır:

1. **Sıfır negasyon.** "never", "no", "avoid", "without" ve türevleri shot_plan'da GEÇMEZ.
   Her kısıt olumlu bir betimlemeye çevrilir.
   - `"seen from behind or mid-distance, never in face close-up"`
     → `"framed from behind at mid-distance, head and shoulders small in frame"`
   - `"never celebrates, looks at camera, poses 'ta-da,' speaks"`
     → `"keeps working steadily and stays turned toward the structure"`
   - `"only slow zoom allowed"` → `"the only camera change is a slow zoom"`
2. **Kısalık.** Her satır en fazla 45 kelime. Bugün satırlar 60-90 kelime ve aynı kamera
   kuralını üç kez tekrarlıyor; bölüm sahnesi bu tekrarın altında boğuluyor.
3. **USTA tarifi tek yerde, doygun renkli.** Kıyafet tarifi 6 satırda 6 kez tekrar etmez;
   `art_style`'da bir kez tanımlanır. Renk `dark cap, dark crew-neck` yerine
   **`bright safety-orange hooded jacket, dark work trousers, dark cap`** olur. Gerekçe:
   buildingwithtan'ın doygun kıyafeti figürü toprak/yeşil zeminden ayırıyor; ayrıca koyu
   üzerine koyu, QC'nin "anatomi" okumasını zorlaştıran düşük kontrastı üretiyor.
4. **İnce motor iş yasak, ama olumlu dille.** Çekim satırları USTA'ya el yakın planı
   gerektiren görev vermez; USTA "walks", "carries", "gestures toward" gibi tam-vücut
   eylemleri yapar. Bu, KN-3'ün doğrudan karşılığı.

### 1b. `series.json` → `auto_replenish.brief`
- YASAKLAR maddesi (7) üretim diline değil, **yazara verilen olumlu sipariş listesine** çevrilir:
  "sahnede tabela, ekran, marka logosu, okunur yazı, pano BULUNMAZ" yerine
  **"yüzeyler boyalı, dokulu ve yazısızdır; aydınlatma ışık kaynağıyla anlatılır"**.
- Yazara açık bir NEGATİF SİPARİŞ LİSTESİ eklenir (bu liste yalnız YAZARA gider, üretilen
  çekim prompt'una GEÇMEZ): `signage, screens, monitors, displays, billboards, brand logos,
  license plates, posters, banners, scoreboards, neon lettering`. Bu KN-2'nin doğrudan
  karşılığı: ARCADE bölümü "illuminated signage" siparişini bu liste yüzünden yazamaz.
- Absürt-ölçek maddesi eklenir (referans kanıtı): her bölümün yapısında insan boyuyla
  kıyaslanabilen tek bir ÖLÇEK ÇAPASI bulunur (dev boru, dev kapı, dev merdiven), USTA onun
  yanında durur. Bu hem cairo hem tan'ın ortak mekaniği.

### 1c. `bible.json` → `art_style`
- `"No CGI sheen, no text, no logos, no watermarks"` cümlesi KALDIRILIR (KN-1). Yerine
  olumlu: `"matte real-world surfaces, clean unmarked materials, natural signage-free
  architecture"`.
- USTA tarifi buraya taşınır ve doygun renge çevrilir (tek kaynak).

### 1d. `bible.json` → `qc.notes` , KN-4'ün düzeltmesi
- `"... is an artifact"` ifadesi çıkar. Kamera kayması, USTA görünüm değişimi ve stil kopması
  **`issues` listesine yazılacak gözlem** olarak tarif edilir, `artifact_score`'a değil.
- `artifact_score`'un `critic.py:119`'daki tanımı notta AÇIKÇA tekrarlanır: yalnız eriyen
  geometri, kopuk/çift nesne, imkânsız fizik, glitch kare.
- Kutlama/ta-da/okunur yazı yasakları notta KALIR (QC'nin görmesi gerekir) ama üretim
  prompt'undan çıkar. Ayrım budur: **yasak QC'nin işi, üretim prompt'unun değil.**

**Done looks like:** dört dosya alanında da negasyon sıfır; USTA tarifi tek kaynakta; QC notu
artifact tanımını bozmuyor.

**PROOF:** (baseline 2026-08-08: `128 passed, 34 subtests passed`, `PREFLIGHT OK`)
```
python -X utf8 -m pytest tests/ -q
python -X utf8 -m series.preflight --series from-scratch --plan aimagine/from-scratch/plans/part06.json
python -X utf8 tools/rf_prompt_lint.py aimagine/from-scratch
```
Üçüncü komut bu rock'ta YAZILACAK yeni bir denetçidir (aşağıda). `tools/` klasörü henüz yok.

### 1e. `tools/rf_prompt_lint.py` , makine denetçisi (yeni dosya)
Kural metni yerine çalıştırılabilir kanıt. Verilen seri klasörü için sıfır-dışı çıkar eğer:
- `shot_plan` satırlarının herhangi birinde negasyon kalıbı varsa
  (`\bnever\b`, `\bno\b`, `\bnot\b`, `\bavoid\b`, `\bwithout\b`, `\bdon't\b`, `\bnor\b`)
- `art_style` içinde aynı kalıplar varsa
- herhangi bir `shot_plan` satırı 45 kelimeyi aşarsa
- `plans/*.json` içindeki herhangi bir çekim prompt'unda negasyon kalıbı varsa
- `qc.notes` içinde `artifact` kelimesi doktrin-uyum bağlamında geçiyorsa
  (basit kural: `is an artifact` ifadesi yasak)

Bu denetçi CI'a bağlanmaz (kapsam dışı), elle koşulur. Testi `tests/test_rf_prompt_lint.py`.

---

## ROCK 2 , Bayat planları yeniden üret

ROCK 1 doktrini değiştirdiği için `KONSEPT.md` de güncellenir (§3.1 tablosu, §3.5 USTA rengi),
bu da `doctrine_sha256`'yı değiştirir. Bekleyen `plans/part06..part10.json` eski damgayı
taşıdığı için `produce` onları zaten reddeder. Yeniden üretilmeleri gerekir.

**Bilinen tuzak (KONSEPT §7'de yazılı, bir kez yaşandı):** planlar silinmeden `total_parts`
geçici olarak 5'e çekilmezse replenish beş "bekleyen" part görür ve NO-OP kalır.

Sıra:
1. `plans/part06.json` .. `part10.json` silinir.
2. `series.json` → `total_parts: 5` (geçici), `next_part: 6` DEĞİŞMEZ.
3. `series.json` → `doctrine_sha256` yeni değere pinlenir. Değer **motorun kendi
   fonksiyonuyla** hesaplanır (`series.bible.doctrine_sha256`), elle `sha256sum` ile DEĞİL
   (LF normalizasyonu; KONSEPT §7 kuralı).
4. replenish koşar, part 6-10 üretilir, `total_parts` 10'a geri taşınır.
5. `parts` 1-5 ve `published.json` DOKUNULMAZ.

**Done looks like:** `plans/part06..10.json` yeni damgayla var; `rf_prompt_lint.py` plan
prompt'larında negasyon bulmuyor; `preflight` sıfırla çıkıyor.

**PROOF:**
```
python -X utf8 -m pytest tests/ -q
python -X utf8 -m series.preflight --series from-scratch --plan aimagine/from-scratch/plans/part06.json
python -X utf8 tools/rf_prompt_lint.py aimagine/from-scratch
```

---

## 4. BÜTÇE ARİTMETİĞİ , planın kabul ettiği gerçek

`require_all_shots: true` + 6 çekim = bölüm başarısı deneme-başı oranın 6. kuvveti.
ROCK 5'in adil payı çekim başına 1 regen veriyor (bölüm hakkı 6 ÷ 6 çekim).

| Deneme başına geçiş | Çekim başına (2 deneme) | Bölüm (6 çekim) |
|---|---|---|
| %24 (bugün) | %42 | **%0,6** |
| %60 | %84 | %35 |
| %75 | %94 | %69 |
| %85 | %98 | **%87** |

Yani prompt düzeltmesi deneme-başı oranı en az %80'e taşımak zorunda. Taşımazsa ikinci kaldıraç
regen hakkıdır ve o kredi demektir (`EPISODE_CREDIT_CAP` bugün 1900).

**Bu plan kredi tavanını DEĞİŞTİRMEZ.** Önce prompt düzeltmesinin gerçek oranı ölçülür, sonra
tavan kararı verilir. Ölçüm = ROCK 2 sonrası TEK bölüm koşusu, `qc_log.jsonl`'den okunur.

---

## 5. NON-GOALS (bu turda kesinlikle yapılmaz)

- `critic.py`, `produce.py`, `replenish.py`, `series_runner.py` ve diğer motor kodu , dört
  kanal ortak kullanıyor, blast radius kabul edilemez.
- `_QC_SYSTEM` sistem prompt'u , yayınlayan üç kanalda çalışıyor.
- `require_all_shots: true` , İhsan'ın 2026-08-04 doktrin kararı, bu turda dokunulmaz.
- `EPISODE_CREDIT_CAP` , ölçümden önce değiştirilmez (bkz. §4).
- `title_patterns` regex'leri ve `title_style` , başlık hattı çalışıyor.
- Diğer üç kanalın hiçbir dosyası.
- Kredi harcayan gerçek üretim koşusu , İhsan onayına bağlı, build'in parçası değil.

---

## 6. ISSUES (bu turda değil, kayda geçer)

- **I-1 (yüksek):** USTA için sabit referans görsel + `characters` kaydı. İki referans
  hesabın da en güçlü öğesi tanınan insan başrol; bizde ön koşul eksik (bkz. §3).
- **I-2 (yüksek):** Post bindirme katmanı: ilk kareye büyük yazı + köşe kutusu + ok
  (buildingwithtan mekaniği). Ham klip temiz kalır, bindirme post'ta eklenir. Kod işi.
- **I-3 (orta):** Böl-ve-göster (split-screen önce/sonra) kancası. Hem cairo hem tan
  kullanıyor. Ya kurgu katmanı ya da çekim 1 kompozisyon kuralı olarak.
- **I-4 (orta):** Altyazı/başlık formülüne cairo'nun taraf-tutturan kalıbı
  (`... : A vs B!😲`) eklenmesi. `title_patterns` değişikliği gerektirir.
- **I-5 (düşük):** `artifact_threshold: 6` kalibrasyonu , ROCK 1 sonrası yeniden ölçülmeli.
