# ISSUES, AIMAGINE sabit-kare pivotu, ertelenenler

- [med] USTA için Kie referans-görsel / characterId kaydı (bible.characters): yüz/kıyafet
  tutarlılığını metin kilidinden görsel kilide yükseltir; ilk 25 bölüm ölçümünden sonra.
- [med] Şot 3→4 köprü deneyi (Codex tur-1 CLARIFY): dış cephenin son karesini şot 4'e ek
  REFERANS görsel (start-frame değil) olarak vermek iç/dış stil sürekliliğini
  güçlendirebilir; kanıtsız, ayrı A/B deneyi ister.
- [med] Sınır-ötesi (cross-shot) QC incelemesi (Codex tur-2): critic bugün tek klip inceler,
  çekim sınırındaki kompozisyon/stil kopmasını göremez; iki komşu klibin sınır karelerini
  birlikte inceleyen bir QC modu ayrı iştir.
- [med] Diegetik inşaat foley'i (çekiç, testere, matkap) müzik altına; Sentinal foley işiyle ortak.
- [low] `core/config.py` aimagine süre bandı {min:15, max:30}: seri hattı okumuyorsa bayat;
  legacy pipeline temizliğiyle birlikte ele alınır.
- [low] the-vast / the-drift emeklilik kararı (İhsan): auto_replenish.enabled hâlâ true,
  status paused; dosya düzeyi kapatma netleşmeli.
- [low] KANAL_ENTEGRASYON_PLANI_v2.md'deki aimagine doktrin özeti (24-32 sn + tek ödül)
  v2.0'dan sonra bayat kalır; plan dokümanı ayrı klasörde, İhsan onayıyla güncellenir.

## ROCK A (ses master) sonrası ertelenenler — 2026-08-27

- **[orta] ROCK B kareler-arası belirgin durum karşılaştırması.** Aynı örneklem içinde ihlal
  sonucu ile ona aykırı belirgin bir sonucu kareden kareye izleyen ayrı karşılaştırma sistemi bu
  çevrimde kurulmadı; Pilot 2 sonrasında fixture verisiyle tasarlanacak. Bugünkü dar onarım,
  mevcut QC çağrısındaki talimata çelişki görülünce `value=false` deme kuralını ekler.

- **[orta] Üretim yalnız LUFS/TP kapısı koşuyor.** `_verify_audio_master` teslimatı yalnız entegre
  loudness ve true-peak için doğruluyor; foley varlığı ve dinamik sıkışma kapıları
  `tools/audio_master_check.py` içinde, yani üretim yolunda DEĞİL. Foley'i gömülmüş bir bölüm
  bugün yayına çıkabilir (Seviye-10'da sabotaj dosyasıyla kanıtlandı: araç yakalıyor, üretim yakalamıyor).
  Öneri: pilot-2 penceresinde tam denetimi üretimde fail-closed koştur (premaster + referanslar
  zaten `produce.py` içinde mevcut).
- **[düşük] Yatak seviyesi 0.50 kapıya çok yakın.** Opt-in yolda foley/yatak marjı pilot malzemesinde
  6,195 dB, kapı 6,0 dB → 0,2 dB pay. Pilot-2 malzemesi biraz farklı gelirse araç FAIL raporlar.
  Öneri: pilot-2 ölçümünden sonra ya eşiği ya da yatak seviyesini seri bazlı ayarlanabilir yap.
- **[düşük] Opt-in seride upscale hatası artık `qc_hold` üretiyor.** Topaz dış servis ve kırılgan;
  bugün `unnatural-lab` için `upscale` kapalı olduğundan etkisiz, ama K-FILO yayılımında
  1080p teslimatı olan bir seriyi durdurabilir. Öneri: K-FILO öncesi "4K üretilemedi ama 1080p
  master doğrulandı" durumunu ayrı sınıflandır.

## ROCK D0 (kredi tabani) sonrasi ertelenenler , 2026-08-27

- **[yuksek, taban ACILMADAN once yapilmali] Kosular arasi kalicilik.** `kie_reservations.json`
  yerel dosyadir. Ayni makinede (VPS, yerel) koşan islemler kilit sayesinde birbirini gorur; ancak
  her GitHub Actions kosusu TAZE checkout ile baslar, yani iki Actions kosusu birbirinin ucusta
  kaydini goremez. Taban su an KAPALI (`KIE_BALANCE_FLOOR` tanimsiz) oldugu icin bu bir aciklik
  degil, bir on kosuldur: taban acilmadan once defterin paylasilmasi gerekir (credits_ledger.json
  gibi commit edilerek ya da VPS uzerinde tek kopya tutularak).
- **[orta] Ucusta TTL'i (900 sn) olculmedi.** Uzun Omni kosularinda tek cagri bu sureyi asarsa
  koruma erken dusebilir; pilot-2 sirasinda gercek cagri sureleri olculup deger buna gore konmali.

## ROCK C2 model kanidi (2026-08-27)

Anahtarin gordugu model sayisi: 53. Flash ailesinde mevcut olanlar arasinda
`gemini-3.5-flash`, `gemini-3.6-flash`, `gemini-3.7-flash` ve `gemini-flash-latest` var;
QC hala `gemini-2.5-flash` (birincil) + `gemini-flash-latest` (yedek) kullaniyor.

**Karar: model DEGISTIRILMEDI.** Gerekce: (a) model degistirmek kota stratejisi degildir,
ayni proje ayni havuzdur , kotayi ayiran sey ayri anahtar/projedir (bu rock'in asil isi);
(b) QC modelini degistirmek 18 serinin verdict dagilimini OLCUMSUZ kaydirir. Model
karsilastirmasi P7 fixture seti hazir olunca (pilot-2 sonrasi) yapilmalidir , ayni
etiketli kareler uzerinde yanlis-gecis/yanlis-red karsilastirmasi olmadan "daha yeni model
daha iyidir" bir varsayimdir.

- **[orta] QC model karsilastirmasi (P7 sonrasi):** gemini-2.5-flash vs 3.x, ayni held-out
  fixture setinde; kazanan olcumle secilir.

## Sentinal dirilis cevriminden ERTELENENLER (2026-09-01, Codex Same Page tur 1-3)

Kaynak: `RF-PLAN-SENTINAL-DIRILIS.md` bolum 6. Bu cevrimde bilerek yapilmadi.

- **[yuksek] `kie-uretim` concurrency kuyrugu doyuma ulasti.** Olculdu (persist commit
  saatleri vs cron): gecikmeler 20-24 Ag'da +40 dk iken 30-31 Ag'da **+119..+397 dk**.
  28 Ag'da eklenen next-stop bes ardisik seri hatti yapti; bes hat tek seri grupta.
  1 Eyl 16:45 itibariyle next-stop (13:20), from-scratch (14:30) ve event-horizon (16:30)
  o gun henuz kosmamisti. ROCK 3'un nobet toleransi bu olcume BAGIMLIDIR (3 saatlik
  tolerans yetersiz) , kuyruk yeniden tasarlanmasa bile kuyrukta/kosuyor/patladi durum
  ayrimi ROCK 3 kapsamindadir.
- **[yuksek] Ayni olum durumu diger hatlarda da acik.** `awaiting_approval` kuyusu,
  Markdown alarm kirilmasi ve yalanci-yesil `last_run.json` ortak motorda; 12 workflow
  `series_runner`'i cagiriyor, 5'i sema yaziyor. ROCK 1-3 filoya yayilana kadar her hat
  ayni sekilde sessizce olebilir.
- **[orta] `environments[].ref_image_url` bosluklari:** `living_room_table` ve
  `workbench_main` icin `None`. `plan_lint` part25'te dort cekimde de uyari veriyor.
- **[orta] Yayin ILERLETME kurali platform ayrimi yapmiyor:** herhangi bir platform
  basarisi yayin sayiliyor; YouTube basarisiz olsa da ilerliyor (ROCK 3 olcumu baglar,
  ilerletme davranisini degistirmez).
- **[dusuk] Duraklatilmis 6 Sentinal serisi** (could-you-survive, night-archive,
  night-shift, room-408, the-signal, time-witness) , once tek hat saglam calissin.
- **[dusuk] Sonraki cevrim adaylari:** `higgsfield.video_analysis_create` ile elle
  gerceklik denetimini otomatige cevirmek, `upscale_video`, `apify` ile obje/kanca
  havuzunu olcuye baglamak, TikTok boost (#33).
- **[bilgi] `fal-ai` MCP sunucusu 2026-09-01 oturumunda 401 (AUTH_HEADER_REJECTED) ile
  baglanamadi.** Higgsfield ve Apify calisiyor.

- **[orta, Codex tur-4 DEFER] Yapisal "kurulmus ilk kare" dogrulamasi.**
  `series/shots.py:46-50` `SHOT1_ONSET_LANGUAGE` yalniz `begins/starts to` kaliplarini
  yakaliyor. part24 ("tilt the mug... streams out... curving upward"), part25 ("drop the
  ball... immediately crushes") ve part26 ("the tines slowly curl inward") ucu de
  `plan_lint`'ten TEMIZ gecip gorme QC'sinde dustu; ucu de elle duzeltildi.
  **Regex'i buyutmek cozum DEGIL** (sinirsiz yama; kendi tarama denemem duzeltilmis
  part24/25'i bile yanlis isaretledi , anahtar kelime "the stream climbs" ile "liquid
  streams out" arasini ayiramiyor). Gereken: cekim 1'in SUREN BIR DURUM mu yoksa BASLAYAN
  BIR OLAY mi tarif ettigini anlayan yapisal/anlamsal dogrulama.

- **[yuksek, YAYIN ACIL turu DEFER] Kosular arasi kismi ilerleme tasinmiyor.**
  QC'den gecmis cekimler basarisiz kosuda cope gidiyor; ayni bolum ertesi kosuda
  sifirdan uretiliyor. Kosu 33594947982 alti klip x 84 = 504 kredi yakti, sifir
  yayin; part 23 ve 24 tam bu yuzden butce tuketip dustu. GitHub runner efemer:
  `unnatural-lab.yml` yalniz `logs/` ve ses stem'lerini artifact yapiyor,
  `output/` kalici degil, `persist_state.sh` sadece durum klasorlerini
  commit'liyor. Cozum ayri kalici depo ister (Release veya artifact indirme).
  Acil turda kapsam disi birakildi: ROCK 1-4 + faturalandirma ile bolumun TEK
  kosuda bitmesi hedeflendi, o zaman tasima gereksiz kalir. Hedef tutmazsa bu
  madde bir sonraki cevrimin ilk rock'i olmali.
- **[dusuk, YAYIN ACIL turu DEFER] `hook_shot` dusunce teaser yedegi yok.**
  Kismi yayinda hook olarak isaretli cekim (part26'da cekim 3) dusebilir ve
  teaser uretilemez. Canli `hook_teaser.enabled=false` oldugu icin bugun zararsiz;
  teaser acilirsa once bu yedek yazilmali.

- **[COZULDU 2026-09-02, izlenmeye devam] Oto-ikmal Gemini'si sert dogrulamadan gecemiyor.**
  Kuyruk sayimi 2026-09-02'de duzeldi ve ikmal artik Gemini'yi CAGIRIYOR, ama
  uretilen planlar ALTI denemenin altisinda da reddediliyor. Iki ayri canli
  kosuda (33658009710 ve elle calistirma) ayni tablo:
  baskin sebep `cekim N prompt'u yalniz olumlu gorsel dil kullanmali`
  (NEGATIVE_VIDEO_LANGUAGE), ardindan `anlatim 34-43 kelime` (tavan 28) ve
  `violation_observation ... zaman-otesi iddia yasak` (TEMPORAL_OVERREACH).
  Dogrulayici DOGRU calisiyor; sorun uretim tarafinda.
  Denenen ve GERI ALINAN yama: prompt'a kelime sayma zorunlulugu + TEMPORAL
  kelime listesi eklendim; (a) sorunu cozmedi, (b) planner prompt'unun
  bayt-bayt sabit kalmasini koruyan golden testleri kirdi (8 test). Prompt
  dort kanal tarafindan paylasiliyor, o yuzden gelisigüzel degistirilemez.
  Dogru cozum muhtemelen: uretim sonrasi OTOMATIK DUZELTME katmani (reddedilen
  alanlari kural bazinda yeniden yazip tekrar dogrulamak), ya da yalniz bu
  seriye ozel bir prompt eki. Golden testler once guncellenmeli.
  Ara cozum: part 27 ve 28 planlari ELLE yazildi (plan_lint TEMIZ). Kuyruk
  29'da yine bitecek, yani bu madde cozulmezse kanal tekrar kararir.
- **[orta] `credit_hard_cap_value` 1000'de birakildi.** chain_frames deneyi
  bitti ve part 27 yayinlandi; `credit_cap_note` 800'e donusu sart kosuyor.
  test_gercekcilik_rock3 artik 1000'e izin veriyor ama SADECE note geri donus
  kosulunu yaziyorsa. Deney degerlendirilip 800'e donulmeli.

  **COZUM (2026-09-02):** iki katman eklendi. (1) Parti artik HEP-YA-HIC degil:
  dogrulamayi tek basina gecen en uzun BAS PARCA kabul ediliyor (bosluk
  acilmiyor, cunku uretim sirayla isler). (2) Mekanik ihlaller (olumsuz dil,
  zaman-otesi violation_observation, anlatim kelime butcesi) alan alan yeniden
  yazdirilip onariliyor; tespit dogrulayicinin KENDI regexleriyle yapiliyor ve
  her onarim kabul edilmeden once ayni regexten geciyor, yani onarim durumu
  kotulestiremiyor. Onarim butcesi calistirma basina 20 cagri ile sinirli.
  Paylasilan planner prompt'una DOKUNULMADI, golden testler bozulmadi.
  Canli sonuc: onceden 0 bolum + sert hata; simdi part 29-32 (4/5) yazildi,
  besi de plan_lint TEMIZ.
  **Kalan:** kok neden hala uretim tarafinda. Ozellikle cekim 1'in "anomali
  zaten suruyor" kurali modeli olumsuz kurmaya itiyor ("the ice does not
  melt"), doğrulayici da tam onu yasakliyor. Onarim bunu tedavi ediyor ama
  ortadan kaldirmiyor; kalici cozum bu geriliminin prompt tarafinda
  cozulmesidir (golden testler once guncellenmeli).
## I-9 (orta) , replenish `environment` alanini zorunlu dogrulamiyor

`series/replenish.py:_validate_batch` (1163-1167) uretilen cekimde `environment`
alanini VARSA korur, ZORUNLU KILMAZ. Alani tasimayan bir plan dogrulamadan gecip
kuyruga girebilir; o cekim zincir yedeksiz kalir.

Bu dongude ertelendi (Same Page Meeting tur 3, Nemotron bulgusu). Gerekce: en
kotu ihtimalde bugunku davranisa donuluyor, regresyon degil; part05-09 elle
yamalandi; muhafiz testi CI'da yakaliyor; kodla dayatmak `replenish.py` demek,
o da dort kanalin ORTAK dosyasi. Kalici cozum icin motor dokunusu gerekiyor.
