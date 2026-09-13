# RF-PLAN ,  wild-encounter: 3×8 sn'den TEK PLAN 10 sn'ye

## Core Focus (tek cümle)

wild-encounter serisini, ölçülmüş referans formatına (tek kesintisiz 10 saniyelik
çekim, sissiz, mavi perdeli, minimal setli) çevir; İhsan'ın yüzü kalsın, cron'a
dokunma, tek test bölümü üretilebilir olsun.

## Ölçüm dayanağı

Tam rapor: `sentinal_ihsan/wild-encounter/REFERANS-AYUSH-ANALIZ.md` (bu dalda mevcut).
Özet: @ayush_0_ai hesabının 11 reeli indirildi ve ölçüldü.

- 11/11 video: **10,01 sn, 24 fps, 1080×1920, 0 sahne kesmesi (tek plan)**
- Patlayanlar: anakonda 675.316 beğeni, shoebill ~148.000, minyatür set 16.691, kaplan 6.076
- Ölüler: zürafa 135, kobra 134, kurt 130, T-Rex 126, örümcek 72, ahtapot 64, ejderha 42
- Caption kalıbı 11/11 aynı → ayırt edici değil
- Kazananı ayıran dört şey: **(a) sis yok** (ölülerde var), **(b) yaratık insanı
  fiziksel olarak ağzına alır** (ölülerde temas yok), **(c) sonda ekip yaratığı açar,
  insan çıkar**, **(d) tanıdık gerçek hayvan** (uydurma yaratık değil)
- Görsel gramer: mavi perde + tracking marker, stüdyo betonu üstünde kum adası,
  minimal kaya/ot, tepede beyaz difüzyon ızgarası, 4–10 kişilik ekip, dolly rayı,
  tek plan içinde yavaş push-in (geniş → yakın)

İç kanıt: `series/replenish.py:190-196` yorumu, `shots=1`'in 12 Eylül 2026'da
"kesme sayısı arttıkça performans düşüyor" ölçümüyle açıldığını yazıyor.
Aynı sonuca bağımsız olarak bu hesapta da varıldı.

## Ne değişmiyor (NON-GOALS)

- **Cron'a dokunma.** `.github/workflows/wild-encounter.yml` aynı kalır.
  Test bölümü elle üretilecek.
- **İhsan'ın yüzü kalır.** `characters[0].ihsan_field`, `character_id`,
  `ref_image_url` aynen durur. Kadrajda net görünür.
- Yayınlanmış part01–07 silinmez, yeniden üretilmez.
- Anlatım ve müzik yok kuralı aynen sürer.
- Başlık kalıbı (`This <ANIMAL> Is NOT Real`) aynı kalır.
- Kredi tavanları (`credit_hard_cap_value: 1000`) aynı kalır.

## Rocks

### Rock 1 ,  Format anahtarı: tek çekim, 10 saniye

`sentinal_ihsan/wild-encounter/series.json` → `auto_replenish`:

- `shots: 3` → **`1`**
- `shot_seconds: 8` → **`"10"`**
- `format_version: "plato-3x8"` → yeni değer (aşağıdaki AÇIK SORU 1'e bak)
- `shot_plan`: üç paragraflık dizi → **tek elemanlı dizi**. O tek paragraf üç
  vuruşu da tek kesintisiz planda taşır. Referansın 675K'lık videosunda üç vuruş
  10 saniyeye sığıyor (ölçüldü), yani vuruşlar kısalır, kaybolmaz.
- `families`: `insect-giant` **çıkar** (örümcek = 72 beğeni; ayrıca ağza-alınma
  vuruşunu anatomik olarak yapamıyor, bu daha önce de ölçülmüştü).
  Kalan: `reptile`, `sea-giant`, `mammal-giant`, `bird-giant`.
- `brief`: kural 8 "üç çekim, her biri 8 saniye" → "**tek kesintisiz çekim, 10 saniye**".
  Kural 7 (SET) yeniden yazılır: **yeşil perde değil MAVİ perde**, sis YASAK,
  dekor minimal (stüdyo betonu görünür + kum adası + birkaç kaya/kütük/seyrek ot),
  tepede beyaz difüzyon ızgarası. Kural 3 (üç vuruş, sırası değişmez) korunur ama
  "her çekim promptu" → "tek çekim promptu" olarak düzeltilir.
- Yeni kural: **KAMERA** ,  tek kesintisiz elde/gimbal plan, geniş kuruluş
  kadrajından yakın plana yavaş push-in. Kesme, geçiş, hızlanma yok.

**Done looks like:** `series.json` geçerli JSON; `shots=1`, `shot_seconds="10"`;
`shot_plan` tek elemanlı; brief'te "haze"/"fog"/"green screen" geçmiyor.

**Proof:** `python -c "import json;d=json.load(open('sentinal_ihsan/wild-encounter/series.json',encoding='utf-8'))['auto_replenish'];assert d['shots']==1 and str(d['shot_seconds'])=='10' and len(d['shot_plan'])==1"`

### Rock 2 ,  bible.json: sis çıkar, mavi perde gelir, tek plan kapıları

`sentinal_ihsan/wild-encounter/bible.json`:

- `art_style`: `with practical haze` **çıkar**; `green screen wall` → **`blue screen
  wall with pale blue cross tracking markers`**; "one continuous uncut shot" eklenir;
  set tarifi minimal olur (stüdyo betonu görünür + kum adası).
- `series.duration_band`: `[12, 26]` → **`[9, 11]`**
- `series.chain_frames: true` → **`false`** (tek çekimde zincirlenecek çekim yok)
  ve `chain_scope` ile ilgili alanlar tutarlı bırakılır.
- `series.qc.min_shots: 3` → **`1`**
- `series.qc.scene_cut_fail: false` → **`true`**. Tek plan sözünün tek gerçek
  bekçisi bu. ep07 kesik çıktığında kapı kesmeyi yakalamış ama `gated=false`
  olduğu için yayınlanmıştı. Tek plan formatında kesme = ret.
- `series.qc.notes`: "SHOT 1/2/3" üç paragraf sözleşmesi → tek çekim sözleşmesi.
  Yaratık muafiyeti (artifact_score) ve "yapım görünür olmalı" kuralı korunur.
  **Sis artık beklenen set öğesi değil**; notlardaki `haze` ifadesi çıkar.
- `environments`: üçü de mavi perdeye ve sissiz tarife çevrilir. `jungle_set`'in
  "dense practical foliage / low drifting haze" tarifi referansla çelişiyor;
  minimal kum/kaya setine dönüşür. `ref_image_url` dolu olan varsa, tarif
  değiştiği için o referans görseli **geçersizdir, boşaltılır** (aksi halde eski
  sisli orman görseli yeni prompt'a sızar).
- `series.format_note` ve `series.duration_note`: yeni ölçüm ve gerekçe yazılır;
  eski gerekçe silinmez, "ESKİ KAYIT" olarak altta kalır.

**Done looks like:** bible geçerli JSON; `duration_band==[9,11]`; `qc.min_shots==1`;
`qc.scene_cut_fail==true`; `chain_frames==false`; `art_style` içinde "haze" ve
"green screen" geçmiyor, "blue screen" geçiyor.

**Proof:** `python -m pytest tests/test_wild_encounter_contract.py -q` ve
`python -m series.cli preflight --series wild-encounter` (varsa; yoksa Rock 5'teki
dry-run bunu kapsar).

### Rock 3 ,  Kuyruktaki eski planları temizle

`sentinal_ihsan/wild-encounter/plans/part07.json` … `part11.json` hepsi
`plato-3x8` formatında, 3 çekimli. `replenish.py:1346` plan `format_version`
uyuşmazlığını hata sayıyor, yani format değişince bu planlar **fail-closed** olur.

- Üretilmemiş planlar (`published.json`'da olmayanlar) `plans/_arsiv_3x8/` altına
  taşınır. Silinmez.
- `series.json` → `next_part` ve `parts` alanları tutarlı bırakılır.

**Done looks like:** `plans/` altında 3 çekimli plan kalmaz; taşınanlar arşivde durur;
`published.json` değişmez.

**Proof:** `python -c "import json,glob;[__import__('sys').exit('3x8 kaldi: '+p) for p in glob.glob('sentinal_ihsan/wild-encounter/plans/part*.json') if len(json.load(open(p,encoding='utf-8')).get('shots',[]))!=1]"`

### Rock 4 ,  Kod tarafı: format sabiti ve tek-çekim uyumu

`series/shots.py:38` → `PLATO_FORMAT = "plato-3x8"`.

- AÇIK SORU 1'in kararına göre sabit güncellenir ya da korunur.
- `replenish.py` içindeki plato dalları (`719`, `1215`, `1446`, `1496`) ve
  `produce.py:1227` tek çekimle uyumlu mu, **okunarak** doğrulanır. Özellikle:
  - `PLATO_SOUND_LINE` kontrolü tek çekimde de çalışmalı
  - `shot_plan` tek elemanlı olunca prompt birleştirme bozulmamalı
  - `replenish.py:681` `shot_word = "shot" if single_shot else "shots"` yolu tek
    çekimde doğru metni üretmeli
- Bozan bir yer varsa **en küçük düzeltme** yapılır. Yeni soyutlama, yeni yapı yok.

**Done looks like:** tek çekimli wild-encounter yapılandırması preflight ve
replenish doğrulamalarından geçiyor; başka seri etkilenmiyor.

**Proof:** `python -m pytest tests/ -q -k "wild or plato or replenish or preflight"`

### Rock 5 ,  Uçtan uca kanıt: ücretsiz dry-run

Gerçek video üretmeden, ücretli çağrı yapmadan:

- `replenish` doğrulama yolu tek çekimli bir plan şemasını kabul ediyor mu
- `preflight` yeni bible ile temiz geçiyor mu
- tüm test paketi yeşil mi

**Done looks like:** `python -m pytest tests/ -q` tam yeşil, ve tek çekimli bir
örnek plan üzerinde doğrulama fonksiyonları hata döndürmüyor.

**Proof:** `python -m pytest tests/ -q` (tam paket) çıktısı.

## Açık sorular (Codex'in cevaplaması istenen)

1. **`PLATO_FORMAT` adı.** Sabit `"plato-3x8"` ve kod içinde dallanma anahtarı.
   Yeni ada (`"plato-tek-plan-10"`) çevirmek okunabilirlik kazandırır ama
   `plans/*.json` ve `published.json` içindeki eski `format_version` değerleriyle
   uyuşmazlık yaratır. **Adı korumak mı, çevirmek mi?** Çevirmekse geriye dönük
   uyum nerede kırılır, tam dosya:satır ver.

2. **`chain_frames: false`** yapmanın yan etkisi var mı? `preflight.py:125` ve
   `142` chain ile ilgili kontroller yapıyor; `produce.py:153 decide_shot_chain`
   tek çekimde ne yapar? Çekim referansı (`shot_refs: true`) bundan etkilenir mi?

3. **`scene_cut_fail: true`** açmanın yanlış-ret riski. Veo'nun 10 saniyelik tek
   çekiminde `scene=0.3` eşiği toz bulutu / hızlı kamera hareketini kesme sanabilir
   (bilinen tuzak). Eşik ayarlanmalı mı, yoksa `true` bırakılıp ilk ret ölçülmeli mi?

4. Gözden kaçan bağımlılık var mı? Özellikle `episode_coherence.py` duration_band
   kullanımı ve `micro_trim: 0.25` ayarının 10 saniyelik tek planda anlamı.

## Kısıtlar

- Python 3.12, mevcut bağımlılıklar. Yeni paket yok.
- Türkçe yorum ve mesaj dili; üretilen prompt'lar İngilizce (mevcut konvansiyon).
- Bu depo otomasyon `[skip ci]` commit'leriyle ilerliyor; başka serilerin
  dosyalarına dokunma.
- Gerçek API çağrısı yapma, kredi harcama. Tüm kanıt ücretsiz yollardan.
