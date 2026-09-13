# RF-PLAN ,  wild-encounter: 3×8 sn'den TEK PLAN 10 sn'ye

Revizyon 4 (Same Page Meeting round 1–3 bulguları uygulandı; rock'lar güvenli
uygulama sırasına göre yeniden numaralandı).

## Core Focus (tek cümle)

wild-encounter serisini, ölçülmüş referans formatına (tek kesintisiz 10 saniyelik
çekim, sissiz, mavi perdeli, minimal setli) çevir; İhsan'ın yüzü kalsın, cron
dosyasına dokunma, elle üretilebilir tek test bölümü hazır olsun.

## Ölçüm dayanağı

Tam rapor: `sentinal_ihsan/wild-encounter/REFERANS-AYUSH-ANALIZ.md`.

- @ayush_0_ai'nin 11 reeli: **11/11 → 10,01 sn, 24 fps, 1080×1920, 0 sahne kesmesi**
- Patlayanlar: anakonda 675.316 beğeni, shoebill ~148.000, minyatür 16.691, kaplan 6.076
- Ölüler: zürafa 135, kobra 134, kurt 130, T-Rex 126, örümcek 72, ahtapot 64, ejderha 42
- Kazananı ayıran: **sis yok**, **yaratık insanı ağzına alır**, **sonda ekip açar ve
  insan çıkar**, **tanıdık gerçek hayvan**
- Görsel gramer: mavi perde + tracking marker, stüdyo betonu üstünde kum adası,
  minimal kaya/ot, tepede beyaz difüzyon ızgarası, tek plan içinde yavaş push-in

İç kanıt: `series/replenish.py:190-196` yorumu, `shots=1`'in 12 Eylül 2026'da
"kesme sayısı arttıkça performans düşüyor" ölçümüyle açıldığını yazıyor.

## Ne değişmiyor (NON-GOALS)

- **`.github/workflows/wild-encounter.yml` dosyasına dokunma.**
- **İhsan'ın yüzü kalır.** `characters[0].ihsan_field`, `character_id`,
  `ref_image_url` aynen durur, kadrajda net görünür.
- **`PLATO_FORMAT = "plato-3x8"` sabiti DEĞİŞMEZ** (davranış anahtarı, sadece etiket değil).
- **`auto_replenish.families` DEĞİŞMEZ** (bu döngüde; gerekçe RF-ISSUES'ta).
- **`series.audio_smooth` DEĞİŞMEZ.** Doğrulandı: `core/ffmpeg_tools.py:619-621`
  tek dosyada doğrudan `concatenate_simple`'a düşüyor, yani fade ve loudnorm
  uygulanmıyor. Ayarı değiştirmek gereksizdi.
- Yayınlanmış part01–07 silinmez, yeniden üretilmez, `published.json` değişmez.
- Anlatım ve müzik yok kuralı, başlık kalıbı, kredi tavanları aynı kalır.
- Çok çekimli serilerin (`tek-obje-4x6` ve diğerleri) ve **üç çekimli Plato metninin**
  prompt çıktısı **bit-bit korunur**.
- Gerçek API çağrısı yok, kredi harcanmaz.

## Uygulama sırası neden böyle

Mevcut canlı sözleşme testi üç çekim, `active` durum ve 8 saniyeyi pinliyor
(`tests/test_wild_encounter_contract.py:57-61,75-83`). Yapılandırmayı testlerden
önce değiştirmek paketi kırmızıya çevirir ve aradaki rock'ların "tam yeşil" kanıtını
geçersiz kılar. Bu yüzden **yapılandırma en sona bırakıldı ve kendi test göçüyle
aynı rock içinde, atomik olarak** uygulanır.

---

### Rock 1 ,  Altın kopya taban çizgisi (kod değişmeden)

Mevcut davranışın tam metin kaydı alınır: `_build_prompt` çıktısı ve
`_validate_batch` hata listeleri, şu üç yapılandırma için:

1. **üç çekimli Plato** (mevcut wild-encounter hâli)
2. `tek-obje-4x6`
3. formatsız (format_version tanımsız) çok çekimli bir seri

`tests/fixtures/rf_tekplan_golden/` altına yazılır ve bunları **tam string**
karşılaştırmasıyla denetleyen çalışır bir regresyon testi eklenir.

**Done looks like:** üç altın kopya diskte; regresyon testi var ve **şu an yeşil**.

**Proof:** `python -m pytest tests/ -q` tam yeşil (yeni regresyon testi dahil).

### Rock 2 ,  Motor: tek çekim gerçekten kabul edilsin

Hepsi **çekim sayısına koşullu** (`single_shot` / `expected_shots == 1`); çok çekimli
yol birebir korunur. Bu rock kendi tek-çekim testlerini de getirir.

1. **`replenish.py:1352-1354`** ,  batch doğrulayıcı 2–6 çekim istiyor, tek çekimli
   her yanıtı reddeder. Alt sınır **1** olur.
2. **`replenish.py:100-126` (`PLATO_OBJECT_RULE`) ,  tek çekim varyantı.**
   Mevcut metin üç çekim formatı için doğru ama tek çekimle üç yerden çelişiyor:
   - `"Camera rigs, crew, haze and a painted backdrop ... stay welcome in every shot"`
     → **sis artık hoş karşılanmaz** (ölçüm: sis kaybedenlerde var)
   - `"framing: one sentence for the locked-off studio camera"` → **yavaş push-in**
   - `"shots 1 and 2 ... revealed only in shot 3"` ve `"KEEP CONSTRUCTION LANGUAGE
     OUT of ... the shot 1 and shot 2 prompts"` → tek çekimde anlamsız
   Tek çekim için ayrı bir kural metni yazılır: mavi perde, sis yok, yavaş kesintisiz
   push-in, ifşa aynı çekimde. Yapım dili yaratık **kimlik alanlarında** yasak kalır.
   **Üç çekimli metin harfi harfine korunur** (Rock 1 altın kopyası kanıtlar).
3. **`replenish.py:754-765`** ,  `humans="featured"` dalı tek-çekim başlığını eziyor
   ve "tek ses müzikal skordur" diyor; serinin "yalnız ortam sesi" kuralıyla çelişir.
   Tek çekim + featured insan için doğru başlık eklenir.
4. **`replenish.py:716-719` sızıntısı ,  DAR KAPSAM.** `formatted_object` aynı zamanda
   yapısal doğrulama ve normalizasyonun sahibi (`1344-1346,1420,1442,1553`); bunlar
   Plato için **korunur**. Yalnız **sabit-obje prompt dalları** (`786-803`, `899-903`,
   `984-1009`) Plato'dan ayrılır ve Plato'ya kendi JSON şekli verilir.
5. **`replenish.py:925-928` zincir dalı** ,  Rock 2.4 bölmesinden sonra Plato'nun
   düşeceği bu dal da sabit kamera dayatıyor. Tek çekimli Plato için push-in'le
   uyumlu bir zincir/kamera metni verilir.

6. **`replenish.py:984-992` `episode_arc_rule`, mevcut `single_shot` dali bizim
   formatimizi DOGRUDAN yasakliyor.** Metin aynen soyle: *"No slow build-up, **no
   withheld reveal**, no closing gesture, there is no time for setup in one shot."*
   Oysa bu formatin tamami **saklanan ifsa** uzerine kurulu: yaratik canli sanilir,
   son saniyelerde kukla oldugu ortaya cikar. Plato'ya ozel tek-cekim yay kurali
   yazilir: ilk kare tum onermeyi gosterir, ama **sirali tehdit -> agza alinma ->
   ekip acar, Ihsan cikar** odulu korunur ve ifsa son saniyelere aittir.
   Genel (Plato disi) `single_shot` metni **degismez**.
7. **`replenish.py:882-886` `humans_featured` dali**, "(the voice is added later as
   narration)" diyor. Bu seride **anlatim yok, ses setin kendi sesidir**. Plato icin
   anlatim vaadi olmayan, ortam sesli bir varyant yazilir.

**Yeni testler (bu rock'ta):** tek çekimli batch yanıtı `_validate_batch`'ten geçer;
tek çekim + `humans="featured"` + ortam sesi başlığı birlikte doğru üretilir; tek
çekim prompt'unda "haze"/"locked-off"/"shot 3" geçmez, "blue screen" ve push-in geçer;
Plato prompt'unda sabit-obje talimatları yok ama yapısal doğrulama duruyor.
**Ayrica nihai sistem promptunda su uc ifade GECMEMELI:**
`"voice is added later as narration"`, `"no withheld reveal"`, `"no closing gesture"`.

**Done looks like:** tek çekimli Plato yanıtı doğrulayıcılardan geçiyor; Rock 1'in
üç altın kopyası **tam string** olarak değişmemiş.

**Proof:** `python -m pytest tests/ -q` tam yeşil.

### Rock 3 ,  Referans görsel plakası: mavi perde, sissiz, statik

**`produce.py:1238-1243`** Plato set-referans şablonu **kodun içinde** "locked-off
view, green screen, practical haze" yazıyor. Bible değişse bile üretilen referans
görsel sisli yeşil set olurdu ve o görsel prompt'a besleniyor.

- Şablon **mavi perde + tracking marker + sissiz minimal set**e çevrilir.
- **Kamera hareketi buraya YAZILMAZ.** Bu metin `generate_image`'a gidiyor
  (`produce.py:1047-1051,1232-1249`); hareket dili orada anlamsız. Temiz, geniş,
  **statik set plakası** olur; "locked-off" ifadesi de çıkar. Push-in yalnız video
  tarafında (`art_style` + çekim promptu) yaşar.
- **`PLATO_REF_TEMPLATE_VERSION` (`produce.py:782`) artırılır.** Doğrulandı: yaratık
  ve ortam hash'leri bu sürümü içeriyor (`produce.py:1305-1310`), sürüm artışı
  önbelleği geçersiz kılmaya yeter; yerel PNG yeniden kullanılmıyor.
- İlgili anchor testleri bu rock'ta güncellenir.

**Done looks like:** şablonda "green screen", "haze", "locked-off" yok; "blue screen"
var; sürüm sabiti artmış.

**Proof:** `python -m pytest tests/ -q` tam yeşil.

### Rock 4 ,  ATOMİK: yapılandırma + test göçü + tek çekimli part08

Bu üçü **tek rock içinde birlikte** yapılır; ayrılırsa paket kırmızıya düşer.

**(a) `series.json` → `auto_replenish`:**

- `shots: 3` → **`1`**; `shot_seconds: 8` → **`"10"`**
- `format_version`: **`"plato-3x8"` KALIR**
- `shot_plan`: üç paragraflık dizi → **tek elemanlı dizi**; o paragraf üç vuruşu da
  taşır (tehdit → ağza alınma → ekip açar, insan çıkar)
- `brief`: kural 8 → "**tek kesintisiz çekim, 10 saniye**". Kural 7 (SET): **mavi
  perde**, **sis YASAK**, minimal dekor (stüdyo betonu görünür + kum adası + birkaç
  kaya/kütük/seyrek ot), tepede beyaz difüzyon ızgarası. Kural 3 "her çekim promptu"
  → "tek çekim promptu". Yeni **KAMERA** kuralı: tek kesintisiz elde/gimbal plan,
  geniş kuruluştan yakına yavaş push-in; kesme yok.

**(b) `series.json` → üst düzey:**

- `status: "active"` → **`"paused"`**. Cron dosyasına dokunmadan otomatik yayını
  durdurur (`replenish.py:1959-1961`, `series_runner.py:949-958`); elle üretimi
  engellemez (`cli.py:94-103` → `produce_episode`, `meta.status` okunmaz).
- `next_part` **8 kalır**.

**(c) `bible.json`:**

- `art_style`: `practical haze` çıkar; `green screen wall` → **mavi perde + soluk mavi
  artı tracking marker**; "one continuous uncut shot" ve **yavaş push-in** eklenir;
  set tarifi minimal olur.
- `series.duration_band`: `[12, 26]` → **`[9, 11]`**
- `series.chain_frames`: `true` → **`false`** (doğrulandı: güvenli; `shot_refs` ve
  kilitli karakter bağımsız çözülür). `chain_note` yeniden yazılır.
- `series.micro_trim`: `0.25` → **`0`**
- `series.qc.min_shots`: `3` → **`1`**
- `series.qc.scene_cut_fail`: **`false` KALIR** (ayar ölü: `critic.py:1217-1231` her
  zaman `"gated": False`, eşik 0,2'ye gömülü ve kalibre değil → RF-ISSUES).
- `series.qc.notes`: üç paragraf sözleşmesi → **tek çekim sözleşmesi**; yaratık
  muafiyeti ve "yapım görünür olmalı" korunur; `haze` beklenen öğe olmaktan çıkar.
- `environments`: üçü de mavi perdeye ve sissiz minimal tarife çevrilir; tarif
  değiştiği için dolu `ref_image_url` alanları **boşaltılır**.
- `format_note`, `duration_note`: yeni ölçüm ve gerekçe eklenir; eskisi "ESKİ KAYIT"
  olarak altta kalır.

**(d) `DOKTRIN.md`:** yalnız **GÜNCEL FORMAT** bölümü yeniden yazılır.
**Tarihsel bölümler olduğu gibi kalır** ,  oradaki "yeşil perde"/"sis" geçişleri
kasıtlı derslerdir (`DOKTRIN.md:117-123,235-248`).

**(e) Planlar:** `plans/part08.json` … `part11.json` (üretilmemiş) **`plans/_arsiv_3x8/`**
altına taşınır, silinmez. part07 yayınlanmıştır, yerinde kalır. `published.json`
**değişmez**. Yerine **elle yazılmış tek çekimli `plans/part08.json`** eklenir:
`format_version: "plato-3x8"`, tek çekim, `duration: "10"`, mavi perde, sissiz set,
İhsan'ın kilitli karakteri, tanıdık gerçek hayvan (çenesi bir insanı alacak ölçekte),
**tam bir `object_card`** (`produce.py:1278-1281` Plato capasi object_card'siz
plani REDDEDIYOR ve preflight bunu denetlemiyor: `preflight.py:121-134`,
`shots.py:67-70`), ve **yeni DOKTRIN'e gore `doctrine_sha256` damgasi** (`produce.py:1560-1569` bayat
hash'i reddediyor).

**(f) Sözleşme testlerinin göçü:** `test_wild_encounter_contract.py:57-61,75-83`,
`test_replenish_plato.py:112-129,194-202`, `test_plato_anchors.py:54-57` yeni
sözleşmeye göre yazılır. Ayrıca **mock'lu uçtan uca test**: ücretli fonksiyonlar
mock'lanip uretim yolu cagrilir ve **tam Omni payload'i** dogrulanir. Test
**gercek `plans/part08.json` dosyasini yukler** ve **capa hazirligindan gecer**
(sentetik plan kullanmaz, capa katmanini mock'lamaz). **Ama gercek part08'i
YERINDE kullanmaz:** capa hazirligi plan dosyasina geri yaziyor
(`produce.py:1643-1646` -> `1373-1375` `atomic_write_json(plan_path, plan)`), yani
gercek part08 mock URL'lerle kirlenirdi. Test, part08 baytlarini **gecici bir plan
yoluna kopyalar**, uretimi o kopya ve gecici `output_area` uzerinde kosar, ve
sonunda **izlenen part08 ile bible baytlarinin degismedigini** dogrular (tek çekim,
`duration="10"`, kilitli `character_id`, ortam sesi cümlesi). CLI çıkış kodu kanıt
sayılmaz (`produce.py:2175-2177` None dönse de `cli.py:101-103` başarı döndürüyor).

**(g) `tools/rf_tekplan_kontrol.py`:** tüm alanları, normalize edilmiş yasak/zorunlu
terimleri, `published.json` hash'ini ve doctrine hash eşleşmesini tek seferde
denetleyen, çıkış kodu 0/1 veren betik. Yasak terimler **büyük/küçük harf ve Türkçe
aksan normalize edilerek**: `haze`, `fog`, `smoke`, `green screen`, `greenscreen`,
`sis`, `duman`, `yesil perde`. Zorunlu: `blue screen`. Denetim kapsamı **aktif prompt
taşıyan alanlar ve DOKTRIN'in GÜNCEL FORMAT bölümü**.

**Done looks like:** `shots==1`, `shot_seconds=="10"`, `shot_plan` tek elemanlı,
`status=="paused"`, `duration_band==[9,11]`, `chain_frames==false`, `micro_trim==0`,
`qc.min_shots==1`; `character_id` ve `ref_image_url` değişmemiş; `published.json`
SHA-256'sı değişmemiş; part08 preflight'tan geçiyor ve doctrine hash'i birebir tutuyor.

**Proof:**
1. `python -m pytest tests/ -q` tam yeşil
2. `python tools/rf_tekplan_kontrol.py` çıkış 0
3. `python -m series.preflight --series wild-encounter --plan sentinal_ihsan/wild-encounter/plans/part08.json`
   → `PREFLIGHT OK`

---

## Bundan sonrası (bu planın dışında, İhsan'ın onayıyla)

Elle tek test bölümü üretimi (ücretli, ~100 kredi, yayınlamaz, `next_part` ilerletmez):

```
python -X utf8 -m series.cli produce wild-encounter sentinal_ihsan/wild-encounter/plans/part08.json
```

## Kısıtlar

- Python 3.12, mevcut bağımlılıklar. Yeni paket yok.
- Türkçe yorum ve mesaj dili; üretilen prompt'lar İngilizce.
- Başka serilerin dosyalarına ve davranışına dokunma.
- `.github/workflows/` altına dokunma.
- Gerçek API çağrısı yapma, kredi harcama.
