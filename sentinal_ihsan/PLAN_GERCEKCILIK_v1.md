# PLAN_GERCEKCILIK_v1 ,  sentinal.ihsan.daily / Unnatural Lab

Tarih: 2026-08-24 · Durum: TASLAK r5 (Same Page Meeting, tur 5) · Sahibi: İhsan
Kaynak: 6 keşif raporu (analitik, pipeline denetimi, kare-kare görsel inceleme, model pazarı, içerik araştırması, tutarlılık reçeteleri) ,  2026-08-23, scratchpad `01..06_*.md`. Tur 1-3 Integrator (Codex) bulguları işlendi.

## CORE FOCUS (tek cümle)

Bölüm başına ~$2-4 üretim bütçesi içinde (video + tüm keyframe/referans görselleri + upscale; Suno ayrı aylık kalemde), Unnatural Lab bölümlerini obje/ortam tutarlılığı ve gerçekçilikte izleyicinin 0,5 saniyede "AI" diye kaydırmayacağı, beğeni ve yorum üreten videolara dönüştürmek.

## 0. TEŞHİS (ölçülmüş; ayrıntı ve kanıt raporlarda)

1. **İzlenme sorunu değil, etkileşim sorunu.** Her bölüm feed'den ~1,0-1,3K'lık bir "seed testi" alıyor ve 12-60 saatte donuyor; ikinci dağıtım dalgası hiç gelmedi. like/view **%0,74** (sağlıklı bant %3-6), comment/view **%0,032** (~10x altında), 15/19 video sıfır yorum. View konsept başarısını ölçmüyor; L/1k ve yorum ölçüyor.
2. **Obje tutarsızlığının kökü motor değil, konfigürasyon.** `bible.json`: `chain_frames:false`, `props:[]`, `environments:[]` → 4 çekim, tek ortak bağı `character_id` (yalnız YÜZ) olan 4 bağımsız text-to-video çağrısı. Obje çekim 2-4'te tarifsiz ("the key"); planlayıcı her çekimde YENİ açı açmayı teşvik ediyor (`replenish.py:618-621, 701-704`). props→`image_urls` mekanizması kısmen hazır (`shots.py:80-87`) ama bölüm-başı akış YOK; planlayıcı `props` yazmıyor, yazsa da düşürülüyor (`replenish.py:944-961`).
3. **QC çekimler-arası tutarlılığı göremiyor** (`critic.py:254-270` tek klip), **fail-open** (Gemini hatasında `qc_skip_accepted`) ve ham klipte, `micro_trim` ÖNCESİ çalışıyor (izleyicinin gördüğü kareler denetlenmiyor). Görsel inceleme: 13/16 çok-çekimli bölümde obje kimliği değişiyor.
4. **Gerçekçilikte en büyük ve en ucuz kayıp: ses.** Omni'nin ürettiği doğal foley `produce.py:244-245` `bg_duck=0.0` ile %100 siliniyor → steril TTS+müzik. İkinci kayıp: önden AI-mükemmel yüz (7 bölümün 6'sında). Üçüncü: ışık/duman/parıltı fenomenleri VFX gibi çiziliyor.
5. **En kötülerin ortak noktası eksik çekim + okunmayan ilk kare.** 7/17 bölüm eksik çekimle yayınlandı (2'si 5 sn); 17 bölümde ilk karede anomalinin net okunduğu TEK bölüm var (ep16). En iyiler: CLAY 2.628, BOTTLE 2.281, ROCK 1.728 ,  ROCK'un ilk karesi 0,5 sn'de okunuyor.
6. **Mevcut motor:** Kie `gemini-omni-video` (Gemini Omni Flash), 84 kredi = $0,42/6 sn; bölüm gerçek ortalaması 458 kredi = **$2,29**. `image_urls` gevşek referanstır, first-frame değildir; zincir Omni'de kanıtlı işe yaramadı (from-scratch: 99/150 fail).
7. **İçerik: obje sınıfı yanlış.** 2026 zirvesi (TikTok AI ASMR ilk 30): yiyecek/içecek + su/buz + arzu objeleri; ilk 30'da araç-gereç objesi YOK. Bizim havuz arzu uyandırmıyor; ses/ışık ihlalleri sessiz feed'de satılamıyor; videolarda cevaplanacak soru yok.

## İLKELER

- **P1 ,  Kilidi metinden piksele taşı:** obje/ortam/kadraj referans görselle ve karakter-karakter aynı tarifle kilitlenir.
- **P2 ,  Ölçemediğini düzeltemezsin:** tutarlılık ve ilk-kare önce QC metriği olur; kapılar **fail-closed** ve İZLEYİCİNİN GÖRDÜĞÜ karelerde (trim sonrası/final master) doğrulanır; her kapının insan-etiketli fixture seti ve alan-bazlı kabul eşiği vardır.
- **P3 ,  Motor değişikliği ancak ölçümle:** bake-off adil (regen kapalı, kol başı sabit bütçe, aynı gerçek master süresi, taze çıktılar, kör puanlama), yayınsız ve **ön eleme**dir; kalıcı motor değişikliği ikinci bir holdout obje sınıfında tekrar ister.
- **P4 ,  Etkileşim içerikten gelir:** yorum obje sınıfı + soru + seçim tasarımından gelir; tutarlılık düzeltmesi yalnız "AI" hissini azaltır.
- **P5 ,  chain_frames Omni'de AÇILMAZ.** Zincirin yerini keyframe/referans kilidi alır. KONSEPT_v3 FAZ-2 REVİZE: **bu çevrim LOOP; REVEAL sonraki çevrimde** test edilir.
- **P6 ,  Deney ile yayın ayrılır:** test/pilot/bake-off çıktıları YAYINLANMAZ; deneyler üretim durumuna dokunmayan experiment-runner'da, kalıcı `experiment_id` defteri ve toplam deney kapısıyla koşar. Kill-gate ölçümü donmuş stack'te 10 ardışık yayında.

---

## ROCK 1 ,  Ses + hızlı gerçekçilik (kod işi 0 kredi; test bölümü deney bütçesinden)

**Ne:**
1. `produce.py:245` `bg_duck` 0.0 → **0.5**; bible alanı **`narration.native_mix_level`** (sabit çarpan olduğu adında bellidir; sidechain ducking Ertelenenler'de).
2. **Ham ses denetimi mikse girmeden + yaptırım haritası:** her klibin HAM native sesi miks öncesi genel şemayla denetlenir. Fail-closed yaptırım AÇIKÇA tanımlı: **istenmeyen konuşma/müzik → fail → cap-aware regen hakkından düşer; foley yokluğu → fail DEĞİL, loglanır** (ilk 5 bölümde taban ölçülür, sonra eşik kararı). Ham stem'ler süreli **Actions artifact** olarak saklanır (`output/` koşu sonunda uçar).
3. `art_style` yeniden yazılır: 198 kelime doktrin → ~80 kelime salt görsel kayıt dili; ekipman adı yasak. ("photoreal" yasağı Ertelenenler'de A/B.)
4. **Yüz politikası MEKANİK:** `humans_featured` teşviki kapatılır; kill-gate boyunca planlar `face_visible:false`. Niyet yetmez: **bu çevrimde çekimlerden `character_id` referansı ÇIKARILIR** (tek işlevi yüz kilidiydi ve modeli yüz göstermeye itiyor; eller kadrajında işlevsiz) ve **QC'ye zorunlu görsel kapı `face_present=false`** eklenir (yüz görünüyorsa fail).

**Done:** 1 yayınsız test bölümü native foley'li, yüzsüz, yeni art_style ile üretildi; TTS anlaşılır, çekim sınırında "pop" yok.
**Proof:** entegrasyon testi: bible `native_mix_level` değerinin `mix_voiceover` çağrısına ulaştığı + çıktıda native ses varlığı assert edilir; HAM stem üzerinde `ffmpeg -af astats` + konuşmasız/müziksiz fixture; ses-fail yaptırım testi (sahte "konuşmalı" stem → regen yolu).

## ROCK 2 ,  Obje kartı + referans kilidi (Omni içinde; +8-24 kredi/bölüm)

**Ne:**
1. **Obje kartı:** plan şemasına `object_card {name, descriptor, environment, framing}` + `format_version`. `descriptor` (renk+malzeme+boyut+1 işaret, ≥12 kelime) 4 çekimde birebir; tek framing cümlesi. Doğrulama **format-bazlı fail-closed**: `"tek-obje-4x6"` = tam 4×6 sn + tek kart + environment id + descriptor tekrar; ROCK 6 formatları kendi doğrulayıcısını getirir.
2. **Bölüm-başı obje referansı ,  idempotent, maliyet-kapılı:** `ensure_episode_refs`: NB2 hero (+1 detay) → ImgBB → URL'ler plan dosyasına **atomik/kalıcı** (kaydet→yeniden yükle→sıra+tekrar-üretmeme testi); `resolve_shot` sabit sırada enjekte eder. **Her NB2 çağrısı bölüm hard-cap'i ve deney kapısından authorize edilir, kalıcı deftere yazılır.**
3. **Ortam referansı:** bible'a 1-2 `environments`. Gerçek fotoğrafta **mahremiyet kuralı**: ham fotoğraf commit edilmez, EXIF temizlenir, yalnız onaylı kırpılmış varlık; ImgBB'nin herkese açık olduğu bilinerek (alternatif: NB2 üretimi). `ref_image_local` yol çözümü onarılır + cron setup adımı + URL bible'a kalıcı.
4. **Planlayıcı çelişkileri:** SCENE FLOW "yeni açı" ve "camera flow/EPISODE ARC" kapatılır; "ihsan_maker's hand" sızıntısı isimle değiştirilir.

**Done:** plan JSON'larında object_card + prop_ref_urls; 2 yayınsız test bölümünde 4 çekimde aynı obje/tezgâh.
**Proof:** (a) uçtan uca test: ham LLM cevabı → `_validate_batch` → atomik kayıt → yeniden yükleme → `resolve_shot` → Omni payload zincirinde descriptor birebir + URL sırası doğru; (b) 2 test bölümünde **4/4 `object_match=true` (non-null)**.

## ROCK 3 ,  QC + yayın kapıları: fail-closed (0 kredi, Gemini ücretsiz katman)

**Ne:**
1. **Obje kimlik denetimi:** `object_match: bool|null` + `object_notes`; [REFERENCE OBJECT] review'a girer; false → fail.
2. **Süreklilik:** önceki çekimin son karesi → `continuity_ok`; zorunluluk yalnız çekim 2-4; çekim 1 N/A (skip/null'dan ayrı).
3. **İlk-kare kapısı izleyicinin gördüğü karede:** `first_frame_ok` + obje doluluk + yerel kontrast, TRİMLENMİŞ sınırlarda ve final master'da. **Kalibrasyon DÖRT zorunlu alan için** (`object_match`, `continuity_ok`, `first_frame_ok`, `face_present`; yüzlü/yüzsüz adversarial örnekler dahil): alan başına adversarial pozitif/negatif fixture seti; **yanlış-GEÇİŞİ ayrıca ölçen** alan-bazlı kabul eşikleri (çoklu kapıda %80 genel doğruluk yetmez ,  yanlış-red kadar yanlış-geçiş de hedeflenir; eşikler fixture ölçümüyle konur, tek sayı dayatılmaz). Thumbnail = ilk kare.
4. **FAIL-CLOSED durum makinesi:** dört zorunlu alandan (`object_match`, `continuity_ok`, `first_frame_ok`, `face_present`) biri null/skip → `produce_episode` tipli dönüş **`ok | qc_hold | generation_fail`**; `qc_hold → awaiting_approval`. **`awaiting_approval` YAYIN MODUNDAN BAĞIMSIZ bloke eder** (bugün yalnız approval modunda duruyor; auto modda ertesi cron yeniden üretim/yayına girebilirdi) ,  ardışık İKİ cron'u kapsayan state-machine testi.
5. **Cache doğrulaması:** `produce.py` bugün diskteki nonzero çekim dosyasını doğrudan kurguya alıyor → cache hit'te medya yeniden doğrulanır ve **içerik hash'iyle eşleşen QC-pass kaydı yoksa QC yeniden koşar** (eski/yarım dosya yeni kapıları atlayamaz).
6. **Çekim-içi kesme dedektörü:** önce 48 ham klipte salt-ölçüm + fixture kalibrasyonu, sonra hard-fail.
7. **Yayın kapıları:** **`require_all_shots:true`**; `download_file` geçici dosya + 3 retry + medya doğrulama + atomik rename; **regen bütçesi dinamik**: sabit "8 hak" değil, kalan bölüm bütçesinden hesaplanır (84 kr/çekimle bugünkü fiili üst sınır ~5 regen; tahmin tablosu ölçülen fiyat + **güvenlik payı** + son-doğrulama tarihiyle tutulur ,  tek ölçümü mutlak yazmak fiyat değişiminde tavanı deldirir); cap-aware iki-geçişli dağıtım (önce her çekime 1 hak); `strengthen_prompt` düzeltmeleri yapılandırılmış olumlu-dil `correction` alanıyla.

**Done:** denetleyemeyen koşu yayınlayamaz; qc_log'da yeni alanlar; eksik çekimli yayın imkânsız; cache bypass kapalı.
**Proof:** kasıtlı senaryolar: 1 çekim FAIL → KIRMIZI; Gemini timeout → `qc_hold`+`awaiting_approval` (iki-cron testi: ertesi koşu yeniden üretmez/yayınlamaz); bozuk cache dosyası → yeniden QC; scene-cut kalibrasyon raporu; DÖRT zorunlu QC alanının (`object_match`, `continuity_ok`, `first_frame_ok`, `face_present`) her biri için ayrı fixture ölçüm raporu (yanlış-geçiş oranları dahil) ,  dördü de raporlanmadan ROCK 3 Done ilan edilemez.

## ROCK 4 ,  İçerik pivotu: arzu edilen obje + okunur ihlal + soru (0 kredi)

**Ne:**
1. **Obje havuzu:** A yiyecek/içecek · B su/buz · C kanonik sert obje. ELENİR: araç-gereç + ses/ışık/parıltı ihlalleri. Tekinsiz 5'te 1.
2. **İhlal kuralı:** fiziksel + sürekli + TEK KAREDE okunur; ilk karede UÇ halinde; obje ≥%40 kadraj.
3. **Turnusol-1 → 1a mekanizma / 1b obje** (K4): obje arzu edilebilir, ihlal satın alınamaz.
4. **Başlık kalıpları:** zorunlu seçim · doğrulanabilir iddia (klipte sayılamayan kesin rakam YASAK; "It Kept Bouncing" gibi) · ilk-fark-ettiğin. "Real or AI?" yazılmaz. **Seed sorusu bu çevrimde BAŞLIKTA taşınır** (otomatik yorum yazımı Ertelenenler'de ,  Analytics OAuth'u salt-okunur kalır, yazma yetkisi ayrı güvenlik incelemesi ister).
5. **Part21-25 geçişi mekanik doğru yolla:** aynı commit'te plan dosyaları kaldırılır + `total_parts:20`; ikmal ROCK 2 şeması devredeyken (beşi birden; 21 ve 23 de A/B/C dışıydı). 30 fikirlik havuz hazır (rapor 05 §5).

**Done:** brief + KONSEPT güncel; yeni 5'lik parti yeni şemayla planlandı.
**Proof:** yeni 5 plan format doğrulayıcısından geçer; L/1k + C/1k trendi kill-gate penceresinde raporlanır.

## ROCK 5 ,  Motor bake-off (ön eleme) + karar kapısı (kol başı sabit bütçe; YAYINSIZ; experiment-runner'da)

**Ne:**
1. **Ön koşul kod işi (Veo hattı uçtan uca):** `kie_api.py:196-202` güncel sözleşmeye (`imageUrls`, `generationType`, `successFlag`/`data.response.resultUrls`) taşınır; contract-fixture'lar Kie doküman örneklerinden. Motor soyutlamasına `generation_mode` + sıralı görsel listesi. Ucuz dalda karakter fotoğrafının ilk-kare basılması kapatılır. (Kling retry bug'ı: Ertelenenler.)
2. **Fiyat preflight ,  sessiz pencerede:** her kolda 1 çekim; **`kie-uretim` concurrency grubunda, başka workflow/proje çağrısı yokken** koşar (bakiye-farkı ölçümü eşzamanlı kullanımda yanlış çıkar); her kol öncesi kalan-deney + filo rezervi yeniden kontrol. Veo Fast 8 sn 60 mı 80 mi burada netleşir.
3. **Bake-off (4 kol; aynı plan + aynı obje sheet + aynı prompt'lar; AUTO REGEN KAPALI; bake-off alt-tavanı 2.400 kr, kol bütçeleri gerçek tahmine göre pay edilir; native-audio politikası TÜM kollarda DONUK: AÇIK, preflight/TCO'ya dahil ve aynı ham-ses QC'sinden geçer; hepsi experiment kapısından authorize):**
   - **Omni + obje ref ,  TAZE, ilk-deneme, regen-kapalı üretim** (ROCK 2 pilot çıktısı KULLANILMAZ ,  pilot regen görmüşse seçilim avantajı olurdu).
   - **Veo 3.1 Fast REFERENCE_2_VIDEO** (8 sn sabit; 9:16+1080p önce 1 çekimle doğrulanır). Bu modda first/last keyframe YOKTUR (ingredient referansı vardır), dolayısıyla "son keyframe kesilir" endişesi bu kola uygulanmaz: kol, önceden tanımlı 8→6 sn retime ile diğerleriyle EŞİTLENİR; eşitlenemiyorsa kazanan karşılaştırmasından çıkar (ayrı süre sınıfı yoktur; aynı-master kuralı mutlaktır).
   - **Veo 3.1 Fast FIRST_AND_LAST_FRAMES, GERÇEK 6 sn** + NB2 keyframe hattı (mevcut kod 6'yı 10'a çeviriyor, `kie_api.py:193`; adapter gerçek 6 sn'yi `ffprobe` ile zorlar; desteklenmezse uç-kare koruyan retime, o da olmazsa kol karar karşılaştırmasından çıkar); shot4 last=shot1 keyframe; bu modda shot1 başı/shot4 sonu `micro_trim` kapalı; dikiş optical-flow + kör insan loop skoruyla doğrulanır.
   - **Seedance 2.0 Fast 720p keyframe I2V, 6 sn native** (+lanczos upscale).
   - Karşılaştırma **aynı gerçek master süresinde** yapılır; kırpma kuralı kol başına açıkça raporlanır.
4. **Ölçüm ve karar:** (a) QC alanları, (b) kamera/viewpoint issue, (c) **KÖR puanlama**: karıştırılmış kimlikler + yazılı rubrik (tek kişilik açık-etiketli 1-5 skor kalıcı karar için yetmez), (d) **bölüm başı TOPLAM kredi** (video + keyframe/ref görselleri + upscale dahil ,  Core Focus hesabıyla aynı tanım). **Sonuç ÖN ELEMEdir:** kazanan, İKİNCİ bir holdout obje sınıfında **Omni baseline KONTROL koluyla birlikte** (aynı bütçe, aynı süre, aynı kör rubrik) tekrar üretilip karşılaştırılmadan `bible.engine` kalıcı değişmez.
5. **Deney kapısı mekanik:** kalıcı `experiment_id` defteri; her ücretli çağrı (video+görsel) toplam deney tavanından (4.000 kr) authorize edilir; taşma testi (tavan dolunca çağrı reddedilir).

**Done:** bake-off + holdout doğrulaması skor tablolarıyla bitti; motor kararı İhsan onaylı.
**Proof:** kol karşılaştırma tablosu (toplam kredi sütunuyla); kol/deney bütçe aşımında koşu durur; Veo contract-testleri yeşil; kör puanlama rubriği ve puanlar ekte.

## ROCK 6 ,  Format karşılaştırması + etkileşim motoru (ROCK 1-5 sonrası)

**Ne:**
1. **Paket karşılaştırması (6+6; nedensel A/B değil, öyle adlandırılır):** TEK-OBJE 2×8 sn vs SEÇ-BİRİNİ 4×6 sn (5'te ≤2 ,  K3). SEÇ-BİRİNİ: çekim başına ayrı object_card+ref (`format_version:"sec-birini-4x6"`); obje `continuity_ok` bu formatta kapalı. Önceden atanmış dengeli takvim; sabit ölçüm yaşı; MDE/kararsız-sonuç kuralı baştan yazılır.
2. **Karar metriği:** birincil sabit-yaş **averageViewPercentage** (OAuth Analytics, SALT-OKUNUR scope); `engagedViews` yalnız normalize/dağıtım metriği; etkileşim/kredi ikincil. "viewed vs swiped" haftalık manuel Studio girdisi. **Ölçüm altyapısı işi:** mevcut `core/analytics.py` yalnız `views_48h` hesaplıyor → aynı 72 sa snapshot'ından views/likes/comments alan, **eksik olgunlukta karar VERMEYEN** raporlayıcı + fixture eklenir (kill-gate de bunu kullanır).

**Done:** 12 bölümlük karşılaştırma raporu çıktı.
**Proof:** kol başına sabit-yaş metrik tablosu; MDE kuralına göre karar veya "kararsız" beyanı; format kararı İhsan onaylı.

---

## YAYIN MODU VE KILL-GATE

- **Geçiş bakım kapısı (İLK commit):** bu serinin canlı cron yayını mekanik olarak askıya alınır (workflow pause + publish kapısı); eski part21-25 planları veya yarım stack geçiş sırasında YAYINLANAMAZ. Kanal K8 prosedürüne kadar (takvimle uyumlu, en fazla 3 hafta) yayınsız kalır; bu süre K8 onayının açık parçasıdır.
- Test/pilot/bake-off çıktıları YAYINLANMAZ; experiment-runner üretim durumuna dokunmaz.
- **K8 iki seçenekli ve İhsan seçer:** (a) kill-gate'in ilk 3 bölümü approval, temizse kalan 7 auto (önerilen; KONSEPT_v3'ün "faz boyunca insan onayı" şartını 3 bölümle sınırlar ,  bu sınırlama K8 onayının AÇIK parçasıdır); (b) 10 bölümün tamamı approval (KONSEPT_v3'e sadık, günlük 1 tık maliyetli). Auto'ya dönüşün ön şartı her iki seçenekte de: DÖRT zorunlu QC alanı (`face_present` dahil) canlı, fail-closed ve fixture setinde yanlış-geçiş testi verilmiş.
- **Kill-gate (donmuş stack, 10 ardışık yayın, her video 72 saat yaşında ölçülür):**
  - **Öldür:** L/1k medyan <10 → içerik havuzu yeniden ele alınır.
  - **Alarm:** C/1k medyan <0,3 (bugünkü seviye) → beğeni gelse bile yorum motoru çalışmıyor demektir; ROCK 4 soru/seçim tasarımı revize edilir.
  - **Başarı:** L/1k ≥30 VE C/1k ≥1,0.
  - **Ara bant (L/1k 10-29):** "ilerleme var" ,  en fazla BİR ek 10-bölümlük karar penceresi; ikinci pencere sonunda hâlâ ara banttaysa içerik havuzu kararına gidilir (süresiz devam yok).

## BÜTÇE (taban / beklenen / p95)

| Kalem | Taban | Beklenen | p95 | Not |
|---|---|---|---|---|
| Mevcut bölüm (video kredi) | 336 kr / $1,68 | 458 kr / $2,29 | ~1.100 kr / $5,50 | ölçülmüş |
| ROCK 1-4 sonrası bölüm (TOPLAM: video+görsel) | 352 kr / $1,76 | 390-470 kr / $1,95-2,35 | ≤800 kr / $4,00 | regen azalması varsayılmaz |
| Deney bütçesi (ayrı kalem, mekanik kapılı) | ,  | ~3.000 kr / $15 | **azami 4.000 kr / $20** | 2 ENTEGRE pilot + preflight + bake-off + holdout; aşama alt-tavanları BAŞLANGIÇ değerleridir (pilot 800 / preflight 300 / bake-off 2.400 / holdout 500): preflight fiyat ölçümünden sonra DİNAMİK yeniden pay edilir, TAM holdout rezervi (Omni baseline + kazanan çifti, gerçek fiyatla) bake-off başlamadan KİLİTLENİR; toplam 4.000'e sığmıyorsa K1 yeniden kararı olmadan başlanmaz; `experiment_id` defteri zorlar |
| Veo 3.1 Fast'e geçilirse (TOPLAM) | preflight ölçümüyle | ~300-400 kr | ≤800 kr | keyframe NB2 + olası upscale DAHİL |
| Kademe B (yalnız test edilen varyant: Seedance **Fast** 720p, TOPLAM) | ~650 kr / $3,25 | ~700 kr / $3,50 | ≤800 kr | (Tur-3 kararı: 984 kr'lık Seedance **Standard** seçeneği KALDIRILDI ,  800 tavanını ve $4'ı aşıyordu, test edilen varyant da değildi) |
| Aylık (30 bölüm, Kademe A) | ~$53 | ~$59-71 | ,  | + Suno ~$12/ay AYRI kalem |

**Mekanik tavanlar:** bölüm `credit_hard_cap` fail-closed **800 kr = video + obje/keyframe görselleri** (NB2 dahil authorize); Suno dışarıda. Tavan muhasebesi kalıcı `credits_ledger.json`'da (commit edilmeyen `logs/cost_tracking.json` part'ın ertesi gün denemesinde sıfırlanıyordu). Tahmin tablosu ölçülen fiyat + güvenlik payı + son-doğrulama tarihiyle (Omni 6 sn: 84 ölçüldü 2026-08-23). Deney toplamı `experiment_id` defteriyle 4.000 kr'de kapılı. **Defter dayanıklılığı:** mevcut `credit_gate._load()` bozuk defteri boş defterle değiştirip fail-open kalıyor; bozuk defter, ücretli çağrıları durduran FATAL durum olur ve hem bölüm hem deney tavanı "koşu-1 persist → koşu-2 taze checkout → kümülatif ret" testiyle doğrulanır. **Aylık seri tavanı (Kademe A) MEKANİK:** 14.000 kr/ay (video+görsel; ledger aylık toplamından fail-closed). "Beklenen ~$60" bir tavan değildir; 30 bölümün hepsi 800'de koşarsa $120 olurdu, aylık kapı bunu keser.
**Ortak havuz koruması:** filo gerçek tüketimi ~1.550 kr/gün ≈ 11.000 kr/hafta → bake-off başlangıç eşiği: bakiye ≥ **15.000 kr** (deney azamisi + 7 günlük rezerv); her kol öncesi yeniden kontrol; preflight'lar sessiz pencerede. Kalıcı çözüm (ayrı anahtar / merkezi rezervasyon): Ertelenenler.

## SIRA VE ZAMAN

1. **Hafta 1:** İLK commit: geçiş bakım kapısı (bu serinin yayını askıda) + ROCK 1 kod işi.
2. **Hafta 1-2:** ROCK 2 → ROCK 3 → ENTEGRE PİLOT 1 (yayınsız; ses + kart + referans + QC birlikte).
3. **Hafta 2:** ROCK 4 → ENTEGRE PİLOT 2 (tam stack; yayınsız). Pilot alt-tavanı toplam 800 kr.
4. **Hafta 2-3:** ROCK 5 (K1 onayıyla) → ön eleme + holdout → motor kararı.
5. **Hafta 3:** stack dondurulur → K8 prosedürü → 10 bölümlük kill-gate.
6. **Hafta 5+:** ROCK 6 → format kararı.

## İHSAN KARAR MADDELERİ

- **K1:** Deney bütçesi ,  beklenen ~$15, **mekanik azami $20 (4.000 kr, defter kapılı)** ,  önerim: EVET.
- **K2:** Aylık tavan: Kademe A (MEKANİK 14.000 kr/ay video+görsel + Suno ~$12 ayrı) mı, kanıt gelirse Kademe B (yalnız Seedance Fast; mekanik aylık tavan yeniden belirlenir) mi? Önerim: bake-off+holdout kanıtına kadar A.
- **K3:** SEÇ-BİRİNİ kotası (5'te 2) ,  önerim: EVET.
- **K4:** Turnusol-1'in 1a/1b ayrımı (KONSEPT doktrin değişikliği) ,  önerim: EVET.
- **K5:** Yüz politikası: bu çevrim `face_visible:false` + çekimlerden `character_id` çıkarılır + QC `face_present=false` kapısı ,  önerim: EVET.
- **K7:** KONSEPT_v3 FAZ-2 revizyonu: zincir yerine keyframe/referans kilidi; LOOP kalır, REVEAL sonraki çevrim ,  önerim: EVET.
- **K8:** Yayına dönüş modeli ,  (a) 3 approval + 7 auto (KONSEPT_v3'ün onay şartını açıkça sınırlar) VEYA (b) 10 bölüm tamamen approval. Önerim: (a); İhsan seçer. Toplam yayınsız geçiş süresi takvimle uyumlu EN FAZLA 3 hafta; bu süre ve KONSEPT onay şartının sınırlanması K8 onayının açık parçasıdır.

## ERTELENENLER (Issues)

- MiniMax H3 adapter'ı; Kling retry düzeltmesi; IG/TikTok kimlik onarımı; "photoreal" A/B; sidechain ducking + LUFS; ayrı KIE anahtarı / merkezi rezervasyon; REVEAL testi; yüz-geri deneyi (`face_visible` kota mekanizması); **otomatik seed-yorum yazımı (YouTube yazma yetkisi ayrı güvenlik incelemesiyle)**; foley-yokluğu eşiği (ilk 5 bölüm ölçümünden sonra).

## BU PLANIN DEĞİŞTİRMEDİKLERİ

Günde 1 bölüm temposu (test haftaları hariç ,  K8); Suno hattı; karakter kimliği (bu çevrimde yalnız eller kadrajda, `character_id` referansı askıda); KONSEPT çekirdeği (sıradan obje + TEK fizik ihlali + kilitli bakış + döngü).
