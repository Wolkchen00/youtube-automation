# PLAN, AIMAGINE "SABİT KARE" pivotu (cairo_ia formatı), rev.4 (Same Page tur 1-3 işlendi)

**Core Focus:** Aimagine'ın from-scratch hattını cairo_ia'nın sabit-kare hipnotik inşaat
formatına taşı: tek sabit karede sıfırdan dış+iç inşaat, kare-zinciriyle MEKANİK tutarlılık,
60 saniyelik bölümler. Kanonik doktrin: `aimagine/KONSEPT.md` v2.0 (alan değerleri ve motor
semantiği §7'de; bu plan §7'yi kayalara böler).

**Bağlam:** from-scratch CANLI (part 1-5 yayınlandı, publish_mode=auto, günlük cron 14:30 UTC).
Pivot part 6'dan girer. Branch `codex-cairo` (origin/main'den); merge + push İhsan kapısı.

**Değişmezler (tüm kayalar):**
- `series/` motoru dört kanal ortak. Yeni davranışlar OPT-IN cfg anahtarlarıyla; anahtar
  kullanmayan serilerin prompt/plan/video çıktısı BİT DEĞİŞMEZ (pre-change golden ile kanıt).
- Kie kredisi harcayan çağrı YOK (replenish Gemini flash serbest; produce yalnız dry-run/birim).
- Testler `tests/test_*.py` DOĞRUDAN koşulur (pytest yok); TÜM test dosyaları koşulur.
- Doktrin SHA fail-closed zinciri korunur; SHA yalnız motorun kendi fonksiyonuyla hesaplanır
  (LF normalizasyonu; elle sha256sum YASAK).

---

## Rock 1, Motor: zincir semantiği + cfg-güdümlü şema/doğrulama + kapılar + preflight

**Dosyalar:** `series/produce.py`, `series/replenish.py`, `series/series_runner.py`,
`series/critic.py`, `series/credit_gate.py` (veya gerçek muhasebe noktası), yeni preflight CLI
modülü, yeni `tests/test_fixedframe.py`, pre-change golden fixture'ları.

**İş (KONSEPT §7 "Motor" bloğunu uygular):**
0. KOD DEĞİŞMEDEN ÖNCE golden dondur: yeni anahtar kullanmayan tüm kurulu serilerin
   `_build_prompt` çıktıları (contents + system_instruction) fixture dosyalarına yazılır.
1. Zincir kararı saf fonksiyona alınır: chain=false çekim önce zincir durumunu SIFIRLAR;
   chain=true çekim önceki son kare yoksa FAIL-CLOSED; son-kare çıkarımı/imgbb yüklemesi
   yalnız SONRAKİ çekim zincirliyse (lookahead); idempotent skip dalı aynı kurallara uyar;
   `chain` alanı yoksa bugünkü davranış.
2. `chain_scope: "episode"` bible.json `series` bloğunda; `series_runner.py` bu seride önceki
   bölümün last_frame_url'ünü aktarmaz; varsayılan "series" bugünkü davranış.
3. `require_all_shots: true` (bible qc, opt-in): herhangi bir çekim eksik/QC-düşmüş ise bölüm
   birleştirilmez, yayınlanmaz. Bu modda QC "skip" BAŞARISIZ sayılır; `critic.py` pass/skip/
   fail'i ayırt eden açık durum döndürür; diğer serilerde skip davranışı değişmez.
4. Üretim-tarafı doğrulama (kredi öncesi): çekim sayısı, süreler, chain ↔ chain_breaks,
   hook_shot, çekim numaraları TAM [1..shots]; 7-birim kotası zincir karesi eklendikten
   SONRAKİ nihai kwargs üzerinde.
5. `credit_hard_cap: true` (opt-in): her ücretli çağrıdan (ana çekim + QC regen + müzik/Suno)
   önce kalan bütçe, SIRADAKİ çağrının tahmini maliyetiyle denetlenir. Tahmin kaynağı: tek
   yerde tanımlı, motor+süre bazlı MUHAFAZAKÂR maliyet tablosu; tabloda karşılığı olmayan
   çağrı türü = fail-closed. Ücretli müzik çağrısı da muhasebeye girer (kredi dönmese bile
   tablo tahmini harcanmış sayılır). Diğer serilerde eski davranış.
6. `required_layers: ["hook_teaser","music"]` (bible series, opt-in): bu katmanlardan biri
   üretilemezse bölüm fail-closed durur ve YAYINLANMAZ (bugün teaser hatası yutuluyor,
   `produce.py` "video kancasız yayınlanır" diyor). Anahtar yoksa bugünkü davranış.
7. `replenish.py`: chain_breaks (şema alanı + SEGMENTED CHAIN kuralı + katı doğrulayıcı +
   normalizer chain'i korur), hook_shot cfg (cfg yokken ESKİ slug dalı AYNEN), shot_plan
   (sistem talimatına girer + normalize sırasında per-shot deterministik önek), cfg-yükleme
   doğrulayıcısı, katı çekim sayısı + süre + numara eşitliği, `title_patterns` (yapılı
   `{regex, families}` kuralları: cfg yüklenirken DERLENİR, başlık **fullmatch** eder ve
   bölümün family'si o kuralın izinli ailelerinde olmalı; uymayan batch fix-turuna reddedilir).
8. Preflight CLI: meta + bible + plan yükler; doktrin SHA kapısı + cfg-uyum doğrulaması +
   çekim başına zincir kararı izi; HERHANGİ ihlalde sıfır-dışı çıkış.
9. `tests/test_fixedframe.py` (kanıt matrisi; her madde AYRI test):
   - Zincir kararı: normal akış, idempotent-skip dalı, cross-episode-start, bayat-kare
     sızıntısı, önceki kare yokken fail-closed.
   - Replenish doğrulayıcı: çekim sayısı, süre, numara kümesi [1..shots], chain ↔
     chain_breaks, hook_shot, başlık fullmatch, başlık-family kısıtı (kalıp 3/4 aile dışı
     kullanımı RED), bozuk regex = cfg hatası.
   - Normalizer `chain` alanını korur; shot_plan öneki her çekim prompt'unda.
   - Critic: pass / skip / fail üçü ayrı durum döner; bu modda skip = yayın engeli.
   - Kredi sert tavanı, YOL YOL ayrı: (a) ana Omni çekimi, (b) QC regen, (c) ücretli müzik
     (Suno) ,  her biri için sınır-altı GEÇER + sınır-aşımı ENGELLER testi; ayrıca tabloda
     olmayan çağrı türü = fail-closed.
   - `required_layers` KATMAN KATMAN: hook_teaser üretilemediğinde yayın engellenir VE music
     üretilemediğinde yayın engellenir (iki ayrı test; birinin geçmesi diğerini kanıtlamaz).
   - Davranış-nötrlük regresyonu (yalnız golden'a güvenilmez): `credit_hard_cap` YOKKEN eski
     fail-open kredi davranışı korunur; `required_layers` YOKKEN teaser/müzik hatası bölümü
     hâlâ yayınlatır (bugünkü fail-open post-process davranışı).
   - GOLDEN prompt eşitliği + yeni alanların anahtarsız serilerde YOKLUĞU.

**PROOF:** `python tests/test_fixedframe.py` + mevcut TÜM `tests/test_*.py` yeşil +
`python -m compileall series core` temiz.

## Rock 2, Veri: doktrin v2.0 alanları + SHA + plan geçişi

**Dosyalar:** `aimagine/from-scratch/series.json`, `aimagine/from-scratch/bible.json`,
`aimagine/from-scratch/plans/part06..10.json` (sil), `.github/workflows/from-scratch.yml`,
etkilenen test fixture'ları.

**İş (KONSEPT §7 "Veri" bloğunu AYNEN uygular):**
1. series.json auto_replenish: shots 6, shot_seconds "10", hook_shot 6, chain_breaks [1,4],
   ALTI aile, shot_plan (§3.1 İngilizce kural satırları, USTA + kamera kilidi dahil),
   music_style v2, title_style (BEŞ kalıp), title_patterns (beş kalıbın `{regex, families}`
   hali), credit_hard_cap true, brief v2; kök hashtags "#shorts #satisfying #construction #diy".
2. bible.json series bloğu: chain_frames true, chain_scope "episode",
   required_layers ["hook_teaser","music"]; art_style v2 (LOCKED-OFF TRIPOD + usta kilidi);
   hook_teaser offset_in_shot 7.0; qc.require_all_shots true; qc.notes v2.
3. plans/part06..10.json SİL + `total_parts: 5` (replenish 6-10'u üretip 10'a geri taşır;
   next_part 6 kalır; parts 1-5 + published.json dokunulmaz).
4. doctrine_sha256: motorun hash fonksiyonuyla yeni KONSEPT.md'den; CRLF/LF eşdeğerlik testi.
5. from-scratch.yml: bayat "approval" yorumunu düzelt; `EPISODE_CREDIT_CAP` TAM 1400 olur.
6. Eski 4×8/beş-aile bekleyen test fixture'larını güncelle.

**PROOF:** TÜM `tests/test_*.py` yeşil + doğrulama betiği: json-load; doctrine_sha256 ==
motor fonksiyonunun KONSEPT.md çıktısı; plans/ altında part06-10 yok; shots=6, hook_shot=6,
chain_breaks==[1,4], chain_scope=="episode", require_all_shots==true, credit_hard_cap==true,
`required_layers` TAM OLARAK `["hook_teaser","music"]` (varlık değil, eşitlik), title_patterns
kuralları derlenebilir + aile adları kanonik ALTI listeden; from-scratch.yml içindeki
EPISODE_CREDIT_CAP değeri TAM "1400".

## Rock 3, Uçtan uca kanıt: gerçek replenish (6-10) + preflight + dry-run

**Dosyalar:** yalnız veri çıktıları (plans/part06..10.json, series.json state alanları).
Motor koduna DOKUNULMAZ (bulgu çıkarsa fix-round).

**İş:**
1. `.env` worktree kökünde hazır (Visionary koydu; GEMINI anahtarı var).
2. Gerçek replenish: CI'daki gerçek entrypoint ile part 6-10 planları yeni doktrinle üretilir
   (yalnız Gemini flash; Kie yok). total_parts 10'a döner.
3. Üretilen 5 planda doğrula: 6 çekim × "10", numaralar [1..6]; hook_shot 6; chain [1,4]
   kırılımlı; doctrine_sha256 yeni; family altı kanonik addan, ardışık tekrar yok; başlıklar
   title_patterns'e fullmatch + aile kısıtına uyar; prompt'lar shot_plan önekini taşır.
4. Preflight CLI part06 planında temiz (exit 0); kasten bozulmuş kopyada sıfır-dışı.
5. Produce dry-run: produce_episode doğrudan çağrılır (runner exit-code'una güvenilmez);
   log 6 çekim, hata yok. Dry-run'ın gösteremediği zincir/kapı davranışı test_fixedframe
   birim kanıtıyla kapatılır (rapora yazılır).

**PROOF:** replenish + doğrulama + preflight (pozitif ve negatif) + dry-run tam çıktıları;
`python tests/test_fixedframe.py` yeniden yeşil.

---

**Sıra:** 1 → 2 → 3. **Fix-round tavanı:** kaya başına 2. **Same Page tavanı:** 5 tur.
**Merge + push:** İhsan kapısı. Push sonrası ilk 14:30 UTC cron part 6'yı yeni formatta üretir
ve publish_mode=auto gereği OTOMATİK yayınlar (İhsan isterse push öncesi approval'a çevirir).
