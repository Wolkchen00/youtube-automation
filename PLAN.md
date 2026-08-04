# PLAN ,  AIMAGINE "SABİT KARE" pivotu (cairo_ia formatı)

**Core Focus:** Aimagine'ın from-scratch hattını cairo_ia'nın sabit-kare hipnotik inşaat
formatına taşı: tek sabit karede sıfırdan dış+iç inşaat, kare-zinciriyle MEKANİK tutarlılık,
60 saniyelik bölümler. Kanonik doktrin: `aimagine/KONSEPT.md` v2.0 (bu planın tek gerçeği;
alan değerleri §7'de).

**Bağlam:** Repo `youtube-automation`; from-scratch serisi CANLI (part 1-5 yayınlandı,
publish_mode=auto, günlük cron 14:30 UTC). Pivot part 6'dan itibaren devreye girer. Bu branch
(`codex-cairo`) origin/main'den açıldı; merge + push İhsan kapısındadır.

**Değişmezler (tüm kayalar için):**
- `series/` motoru DÖRT kanal tarafından paylaşılır. Yeni davranışların tümü OPT-IN cfg
  anahtarlarıyla gelir; yeni anahtar kullanmayan serilerin ürettiği prompt/plan/video
  BİT DEĞİŞMEZ (golden-test ile kanıtlanır).
- Kie kredisi harcayan hiçbir çağrı yapılmaz (replenish Gemini flash = serbest; produce
  yalnız dry-run).
- `python`/`py` Windows'ta koşar; testler `tests/test_*.py` DOĞRUDAN çalıştırılır (pytest yok).
- Doktrin SHA fail-closed zinciri korunur: KONSEPT.md değişti → series.json `doctrine_sha256`
  ve tüm bekleyen plan damgaları güncel SHA ile eşleşmeli, yoksa üretim durur.

---

## Rock 1 ,  Motor: çekim-bazlı zincir + cfg-güdümlü hook/şema kuralları

**Dosyalar:** `series/produce.py`, `series/replenish.py` (gerekirse `series/shots.py`).

**İş:**
1. `produce.py`: plan çekimindeki `"chain": false` alanı o çekim için zincir referansı
   kullanımını kapatır (omni dalında `image_urls`'e chain_url EKLENMEZ; ucuz motor dalında
   `resolve_visual_shot`'a chain_url GEÇİRİLMEZ). Çekim sonrası son-kare çıkarımı ve
   chain_url güncellemesi HER durumda sürer (sonraki çekim zincirlenebilsin). Alan yokken
   (None) davranış bugünkünün aynısı. İdempotent "çekim zaten var" dalı da tutarlı davranır.
2. `replenish.py`:
   - `auto_replenish.chain_breaks: [int,...]` (opt-in): şemadaki shot alanlarına
     `"chain": <true|false>` eklenir; sistem talimatına kural yazılır (listedeki n'ler
     chain=false + taze sahne kurar; diğerleri önceki çekimin son karesinden devam eder);
     doğrulayıcı chain alanlarını chain_breaks'e göre ZORLAR; normalizer (`clean = {...}`)
     `chain` alanını DÜŞÜRMEZ (yalnız chain_breaks tanımlı cfg'de).
   - `auto_replenish.hook_shot: <int>` (opt-in): `meta.slug == "from-scratch"` hard-code'u
     kaldırılır; cfg değeri varsa "hook_shot MUST be <n>" kuralı + doğrulayıcı bu değeri
     zorlar; cfg yoksa eski genel kural. (from-scratch'in yeni cfg'si 6 verecek ,  Rock 2.)
   - `auto_replenish.shot_plan: [str,...]` (opt-in): sistem talimatına "SHOT PLAN (follow
     exactly, one line per shot)" bloğu olarak numaralı girer; doğrulayıcı yalnız uzunluğun
     shots ile eşleştiğini cfg-yükleme anında kontrol eder.
   - chain_breaks tanımlıyken zincir anlatım kuralı (SEAMLESS CHAIN / SCENE FLOW ikilisi)
     yerine SEGMENTED CHAIN metni kullanılır: zincirli çekim önceki son kareden DEVAM eder,
     chain=false çekim YENİ sabit kare kurar.
3. Yeni test dosyası `tests/test_fixedframe.py` (repo test stilinde, doğrudan koşulur):
   - produce zincir kararı: chain=false çekim chain_url almaz, sonrakiler alır (birim
     seviyesinde; ffmpeg/ağ çağrısı mock/atlanır).
   - replenish doğrulayıcı: chain_breaks uyumsuzluğu, hook_shot cfg zorlaması, normalizer'ın
     chain alanını koruması.
   - GOLDEN: yeni cfg anahtarları OLMADAN `_build_prompt` çıktısı (system_instruction +
     contents) bugünkü metinle birebir aynı (eski davranış bit-değişmez kanıtı).

**Done looks like:** yeni anahtarlar cfg'de yokken tüm mevcut seriler için davranış aynı;
varken şema/kural/doğrulama yukarıdaki gibi.
**PROOF:** `python tests/test_fixedframe.py && python tests/test_doctrine_gate.py &&
python -m compileall series core` hepsi temiz çıkar.

## Rock 2 ,  Veri: doktrin v2.0 alanları + SHA + bayat plan temizliği

**Dosyalar:** `aimagine/from-scratch/series.json`, `aimagine/from-scratch/bible.json`,
`aimagine/from-scratch/plans/part06..part10.json` (silinecek), `.github/workflows/from-scratch.yml`
(yalnız bayat başlık yorumu).

**İş:** KONSEPT.md v2.0 §7 "Veri" bloğunu AYNEN uygula:
1. `series.json.auto_replenish`: `shots: 6`, `shot_seconds: "10"`, `hook_shot: 6`,
   `chain_breaks: [1, 4]`, `families` = §3.2 ALTI kanonik ad (altıncısı:
   "geri dönüşüm/off-grid dönüşüm"), `shot_plan` = §3.1 tablosunun 6 satırlık İngilizce
   kural hali (kamera + zincir + faz içerikleri; USTA tanımı dahil), `music_style` = §3.4'e
   uygun YENİ İngilizce string (loop bitişi yok), `title_style` = §3.5 BEŞ kalıp, `brief` =
   §3'ü taşıyan Türkçe DEĞİŞMEZ KURALLAR v2 (çıktı dili İngilizce notu + tek yapı + aile
   rotasyonu + güvenlik + yorum-yemi + USTA + kamera doktrini + yeni tohum konu listesi §6),
   `hashtags` = `#shorts #satisfying #construction #diy` (series.json kökündeki alan).
2. `bible.json`: `chain_frames: true`; `art_style` = §7'deki sabit-kamera + usta kilidi
   cümleleriyle YENİ string; `hook_teaser.offset_in_shot: 7.0` (duration 1.2 kalır);
   `qc.notes` = §7'ye göre yeniden (sabit kamera kayması, usta görünüm değişimi, yapı stil
   kopması, kutlama/okunur yazı yasakları, hook_shot=6, teaser kaynağı çekim 6).
3. `plans/part06.json`..`part10.json` SİL (eski doktrin damgalı; produce zaten reddederdi).
   `parts` 1-5 kayıtlarına ve `published.json`'a DOKUNULMAZ; `total_parts: 10`, `next_part: 6` kalır.
4. KONSEPT.md v2.0'ın SHA-256'sını hesapla → `series.json.doctrine_sha256` güncelle.
5. `from-scratch.yml` üstündeki bayat "ONAY GELMEDEN..." yorum satırını canlı gerçeğe çevir
   (publish_mode=auto, İhsan 2026-07-30). Cron/adımlar DEĞİŞMEZ.

**Done looks like:** doktrin-veri zinciri tutarlı; hiçbir bayat damga kalmadı.
**PROOF:** `python tests/test_doctrine_gate.py` + tek satırlık doğrulama betiği:
series.json/bible.json json-load olur; doctrine_sha256 == KONSEPT.md'nin gerçek SHA-256'sı;
plans/ altında part06-10 yok; shots=6/hook_shot=6/chain_breaks=[1,4] okunur.

## Rock 3 ,  Uçtan uca kanıt: gerçek replenish (6-10) + produce dry-run

**Dosyalar:** yalnız veri çıktıları (`aimagine/from-scratch/plans/part06..10.json`,
series.json güncellemeleri). Motor koduna DOKUNULMAZ (bulgular fix-round'a gider).

**İş:**
1. `.env` worktree köküne kopyalanmış olacak (Visionary hazırlar; GEMINI anahtarı içerir).
2. Gerçek replenish koşusu: CI'daki modül çağrısıyla aynı yol (`python -m series.replenish
   from-scratch` veya repodaki gerçek entrypoint neyse o) ,  part 6-10 planları YENİ doktrinle
   üretilir. Kie kredisi HARCANMAZ (yalnız Gemini flash metin).
3. Üretilen 5 planda doğrula: 6 çekim × "10"; hook_shot=6; çekim 1 ve 4 `chain: false`,
   diğerleri `chain: true`; doctrine_sha256 yeni SHA; family altı kanonik addan; ardışık
   bölümlerde aynı family yok; başlıklar §3.5 kalıplarından; prompt'larda sabit kamera dili.
4. `python -m series.produce from-scratch <part06 plan yolu> --dry-run` (veya repodaki gerçek
   dry-run çağrısı): log 6 çekim gösterir, hata yok; dry-run çıktısında çekim 1/4'ün zincir
   almadığı, 2/3/5/6'nın aldığı görünür (dry-run zincir görünürlüğü sınırlıysa test_fixedframe
   birim kanıtı yeterli sayılır, rapora yazılır).

**Done looks like:** yeni doktrinle üretilmiş 5 gerçek plan + temiz dry-run.
**PROOF:** yukarıdaki replenish + doğrulama + dry-run komutlarının tam çıktısı; ayrıca
`python tests/test_fixedframe.py` yeniden yeşil.

---

**Kayalar sırayla:** 1 → 2 → 3 (3, 1 ve 2'nin çıktısına bağımlı).
**Fix-round tavanı:** kaya başına 2. **Same Page tavanı:** 5 tur.
**Merge + push:** İhsan kapısı (canlı cron'u yeni formata geçirir; sonraki 14:30 UTC koşusu
part 6'yı yeni formatta üretir ve OTOMATİK yayınlar).
