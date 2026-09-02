# RF-PLAN: Sentinal yayin acil kurtarma (2026-09-02) , r2

## Core Focus (tek cumle)

sentinalihsandaily kanali 28 Agustos'tan beri yayin yapamiyor; QC kapisinin kendi
kendini imkansiz kilan tuzaklari temizlenip hat bugun tek kosuda bolum yayinlar
hale getirilecek.

## Kanit (kod + canli kosu gunlukleri)

Son yayin: part 22, 2026-08-28. Sonra dort bolum ust uste oldu:

| Part | Durum | Olum nedeni |
|---|---|---|
| 23 | skipped | icerik reddi + imgbb kesintisi, 436/800 kredi yandi |
| 24 | skipped | cekim 2 sureklilik reddi x2, 512/800 kredi yandi |
| 25 | budget_exhausted | Gemini 429 + 503, zorunlu ses kapisi degerlendirilemedi |
| 26 | qc_retry 2/3 | 05:04 cekim 2 sureklilik reddi, 05:30 cekim 4 sureklilik reddi |

Yayin kapisi `sentinal_ihsan/unnatural-lab/bible.json` icinde
`series.qc.require_all_shots: true`. Bu bayrak `series/produce.py` uc yerde bolumu
komple iptal ettiriyor: satir 1527, satir 1679 (`return None`) ve satir 1717
(`len(shot_files) != len(plan["shots"])`). Tek cekim dusunce yayin yok.

### T1: Zincir karesi YANLIS gerekcelerle sifirlaniyor (asil kok)

`series/critic.py` `review_chain_frame()` bir cekimin son karesini "sonraki cekime
baslangic olarak uygun mu" diye denetlerken statik obje referansini olcut aliyor.
Ama bu serinin FORMATI objenin bozulmasi. part26 planinda cekim 3'un
`state_carry` degeri: `"the tines stretched long and empty above the counter"`.
Yani catalin uzamis ve bos olmasi KASITLI terminal hal. Denetim bunu pirupak
catal referansiyla kiyaslayip "uygunsuz" diyor.

`series/produce.py:250` bunun uzerine `reset_or_fail("unsuitable", ...)` calisir,
zincir karesi `None`'a duser. Sonraki cekim sureklilik cipasi OLMADAN uretilir.
Ardindan ayni bolumde `qc.require_continuity: true` o cekimi "cekimler arasi
tezgah, isik veya obje-durumu surekliligi bozuk" diye reddeder. Regen de cipasiz
calistigi icin ikinci ve ucuncu deneme ayni duvara carpar.

Canli kanit, kosu 33594947982 (2026-09-02 05:30 UTC):
```
05:43:04 WARNING  Zincir karesi sifirlandi: cekim 3 -> 4; neden=unsuitable, kanonik=omni_image_references
05:45:43 WARNING  QC RED: cekim 4 (deneme 0): ... cekimler arasi ... surekliligi bozuk
05:48:03 WARNING  QC RED: cekim 4 (deneme 1): cekimler arasi ... surekliligi bozuk
05:50:31 WARNING  QC RED: cekim 4 (deneme 2): cekimler arasi ... surekliligi bozuk
05:50:31 ERROR    QC: cekim 4 esigi gecemedi -> cekim bolumden dusuruldu
05:50:33 WARNING  Part 26 qc_retry (2/3); exit 1
```
Cekim 1, 2, 3 ayni kosuda QC'yi GECTI. Yalniz zinciri sifirlanan cekim 4 oldu.

Onemli: part26 cekimlerinde `chain` alani YOK. `decide_shot_chain()` bu durumda
legacy dala girer ve `chain_decision.error` uretmez. Dolayisiyla produce.py:1452
icindeki `chain_reset_pending` dali HIC DANISILMAZ; degisken 1480'de sessizce
sifirlanir. Reset bilgisi bugun bir sonraki cekime hic ulasmiyor.

### T2: Ucretsiz Gemini kotasi matematiksel olarak yetmiyor

`qc.native_audio_review: true` zorunlu kapi. Anahtar ucretsiz katmanda:
`generate_content_free_tier_requests, limit: 20` istek/gun. Olculen gercek yuk
(`qc_log.jsonl`, `qc_api_attempt` olaylari): 2026-08-28 61 cagri, 09-01 32 cagri
(17 ses + 15 gorsel), 09-02 33 cagri (21 ses + 12 gorsel). Temiz bir bolum bile
~10 cagri istiyor, regen girince 30+. 20/gun tavani ile bu hat asla duzenli yayin
yapamaz.

Bekleme merdiveni de sabirsiz ve UC KOPYA halinde duruyor (gorsel denetim
critic.py ~467-495, ham ses ~1126-1160, teslimat sesi ~1207-1241). Uctu de
`time.sleep(min(5 * attempt, 15))` kullaniyor ve 429 govdesindeki `retryDelay`
alanini hic okumuyor.

### T3: Kismi ilerleme tasinmiyor (bu turda DEFER)

QC'den gecmis cekimler basarisiz kosuda cope gidiyor. Kosu 33594947982 alti klip
x 84 kredi = 504 kredi yakti, sifir yayin. GitHub runner efemer:
`.github/workflows/unnatural-lab.yml` yalniz `logs/` ve ses stem'lerini artifact
yapiyor, `output/` kalici degil. Kosular arasi cekim tasimak ayri kalici depo
ister. ROCK 1-3 + faturalandirma ile bolumun TEK kosuda bitmesi hedefleniyor, o
zaman tasima gereksiz kalir. ISSUES'a yazildi.

## Ihsan kararlari (2026-09-02)

1. QC kotasi: **faturalandirma acilacak** (ucretli katman). Elle adim, asagida.
2. Regen'e ragmen gecemeyen cekim: **kalan cekimlerle yayinlansin**, alarm gitsin.

## Duzeltilen yanlis varsayimlar (Codex tur-1)

- **"Sessiz seri" YANLIS.** `.github/workflows/unnatural-lab.yml` yorumu bayat.
  Canli gercek: `bible.narration = {"channel": "sentinal_vlog",
  "native_mix_level": 0.5}` ve part26 tam bir anlatim metni tasiyor. Cekim
  dusurmek videoyu kisaltir, anlatim sesi videodan uzun kalir. ROCK 2 bunu
  ele almak zorunda.
- **Test takimi ZATEN KIRMIZI.** `origin/main` uzerinde `pytest tests/ -q`
  sonucu 2 failed, 599 passed. Ikisi de dunku bilincli kararlarla celisen bayat
  testler. Proof komutu bu haliyle asla gecemezdi. ROCK 4 eklendi.
- **`retry_count` neden kodundan bagimsiz artiyor.** `series_runner.py:474`
  civari: kod ne olursa olsun sayac artar, 3'te `needs_human`. "QUOTA sayilmaz"
  iddiasi yanlisti, cikarildi.

Codex tur-2 sonrasi (hepsi kodda dogrulandi):

- **"SERIES EXEMPTION zincir denetimine uygulanmiyor" YANLIS.** critic.py:660
  `config.get("notes")` degerini `_review_frames`'e zaten geciriyor. Iddia
  plandan cikarildi, yerine regresyon testi kondu.
- **Tek basina `state_carry_expected` eklemek YETMEZ.** critic.py:610-615
  `_decide()` `object_match=false` gelince sert red veriyor ve
  `review_chain_frame` `require_object_match`'i true geciriyor. ROCK 1a
  kimlik sozlesmesi olarak yeniden yazildi.
- **Yayin kurali platform ayrimi yapmiyor.** series_runner.py:753 `if ok:`
  herhangi bir platform basarisini yayin sayiyor. ROCK 2'ye zorunlu platform
  eklendi.
- **Anlatim sigmama riski olculdu.** ffmpeg_tools.py:207-209 sabitleriyle
  18 sn'lik varyantta donuk kare + yarim cumle olusuyor. ROCK 2'ye tam
  sigdirma sarti eklendi.

## Non-goals

- Kosular arasi cekim tasima (T3). ISSUES'a.
- QC kalite esiklerini gevsetmek. Esikler aynen kalir.
- `hook_teaser` icin genel yedek mekanizma (canli `hook_teaser.enabled=false`).
  ISSUES'a.
- Diger hatlarin (aimagine, galactic_experience, shadowedhistory) davranisini
  degistirmek. Yeni davranislar opt-in alan olarak gelir, varsayilan bugunku
  davranistir.
- Fail-open. QC API tukendiginde bolum yine `hold` olur, denetimsiz yayin YOK.

## Kisitlar

- Python 3.11, mevcut bagimlilklar. Yeni paket yok.
- Degisebilecek kod dosyalari: `series/produce.py`, `series/critic.py`,
  `series/bible.py`, `series/series_runner.py`, `series/series_meta.py`,
  `series/preflight.py`, `core/narration.py`, `tests/`, ve
  `sentinal_ihsan/unnatural-lab/bible.json` + `series.json`. Baska kod dosyasi
  degismesin. `core/ffmpeg_tools.py` sabitleri (NARRATION_MAX_TEMPO,
  NARRATION_MAX_EXTEND) DEGISTIRILMEZ; anlatim metni kisaltilarak sigdirilir.
- Turkce log/alarm metinleri mevcut usluba uysun.
- Em dash karakteri kullanilmayacak.

---

## ROCK 1: Zincir karesi kasitli terminal hali "bozuk" saymaz + reset tek cekimlik muafiyet acar

**Done looks like:** iki katman:

**1a (kok): zincir karesinin KIMLIK sozlesmesi.** Asil arizanin tek basina
`state_carry_expected` eklemekle COZULMEDIGI dogrulandi. `review_chain_frame()`
(critic.py:653) `_decide()` cagrisina `require_object_match` degerini TRUE olarak
geciriyor; `_decide()` critic.py:610-615'te `object_match` alani false gelince
"obje referansla ayni fiziksel obje degil" diyip sert red veriyor. Kasitli
deformasyon (uzamis catal) referans fotoyla ayni obje gorunmedigi icin bu kapi
her turlu kapaniyor.

Gereken: zincir karesine OZGU kimlik sozlesmesi. Kaynak cekimin `state_carry`
beklentisi denetime verilir, ve kasitli terminal hal ile gercek kimlik kaymasi
ayrilir. Canli sekil olan `object_match=false` + `state_carry_ok=true` +
`chain_frame_suitable=true` GECMELIDIR. Gercek uretim kusuru (bulanik kare,
kirpilmis kadraj, cozunmus el/yuzey) ve gercek kimlik kaymasi (bambaska bir
obje) hala REDDEDILIR.

`bible.series.qc.notes` icindeki SERIES EXEMPTION metni bu denetime BUGUN ZATEN
uygulaniyor (critic.py:660 `config.get("notes")` degerini `_review_frames`'e
geciriyor). Buraya yeni wiring EKLENMEZ; mevcut aktarim regresyon testiyle
kilitlenir.

**1b (emniyet agi):** zincir GERCEKTEN sifirlandiginda (kare cikarilamadi,
yukleme basarisiz, API tukendi veya dogrulanmis uygunsuzluk), BIR SONRAKI cekimin
QC'sinde sureklilik olcutu red sebebi OLAMAZ. Muafiyet hem `continuity_ok=false`
hem de alanin eksik/degerlendirilemez oldugu durumu kapsar, ve o cekimin butun
review + regen dongusu boyunca gecerlidir.

**Bookkeeping:** yeni durum degiskeni YARATILMAZ. Mevcut `chain_reset_pending`
(produce.py:1519, 1707, 1868'de `next_frame.canonical_reset` ile yaziliyor)
1480'de sifirlanmadan ONCE yerel snapshot'i alinir ve o cekimin `qc_context`'ine
konur. `previous_shot_dropped` ile birlikte TEK "kirik cipa" sinyali olur, ve ilk
basarili zincirde temizlenir. Boylece tek cekim dususu domino olmaz.

**Dikkat:** muafiyet TEK cekimliktir. Cekim 3 -> 4 sifirlandiysa yalniz cekim 4
muaf olur; cekim 4 -> 5 zinciri saglamsa cekim 5 yine sert kapiya girer.

**Proof:** `python -m pytest tests/test_chain_reset_continuity.py -q` (yeni).
Vakalar: (a) CANLI SEKIL `object_match=false` + `state_carry_ok=true` +
`chain_frame_suitable=true` zincir denetiminden GECER; (b) gercek uretim kusuru
(dusuk artifact skoru, bulanik/kirpilmis kare) hala uygunsuz sayilir;
(c) gercek kimlik kaymasi (`state_carry_ok=false` + `object_match=false`) hala
REDDEDILIR; (d) reset sonrasi sonraki cekim `continuity_ok=false` ile GECER;
(e) reset sonrasi `continuity_ok` alani hic gelmezse yine GECER; (f) reset
YOKKEN `continuity_ok=false` hala REDDEDILIR; (g) muafiyet ikinci cekime sizmaz;
(h) REGRESYON: `qc.notes` (SERIES EXEMPTION) zincir denetimine gecirilmeye
devam eder.

---

## ROCK 2: Eksik cekim tabani (min_shots), bolum kalan cekimlerle yayinlanir

**Done looks like:** `bible.series.qc.min_shots` opt-in tam sayi alani. Alan
yoksa bugunku `require_all_shots` davranisi aynen surer. `unnatural-lab` icin
`min_shots: 3`.

**Tek turetilmis esik:** uc kapiya ayri ayri kontrol YAZILMAZ. Tek bir
`required_shot_count` turetilir. Erken cikis SADECE matematiksel olarak imkansiz
oldugunda olur: `accepted + remaining < required`. Son kapi `accepted >= required`
olarak uygulanir. Boylece 4 cekimin 2. sinda dusen bir cekim, 3/4 hala mumkunken
bolumu iptal ettirmez.

**Dogrulama:** `min_shots` preflight'ta denetlenir: `bool` OLMAYAN gercek `int`,
ve `1 <= min_shots <= len(plan["shots"])`. Gecersizse UCRETLI cagri baslamadan
once net hatayla durulur.

**Anlatim ve sure (olculmus risk, sessiz kalite kaybi):** seri anlatimli.
`core/ffmpeg_tools.py:207-209` sabitleri: `NARRATION_MAX_TEMPO = 1.05`,
`NARRATION_MAX_EXTEND = 3.0`, `NARRATION_TAIL_PAD = 0.4`. Hesap: 24 sn'lik
bolumden 6 sn'lik tek cekim dusunce video ~18 sn olur; 24 sn icin yazilmis
anlatim 1.05x ile ancak ~22.9 sn'ye iner, gereken uzatma ~5.3 sn ve bu 3.0 sn
tavanini asar. Sonuc `mix_voiceover()` icinde `capped=True`: video sonuna 3
saniyelik DONUK KLON KARE eklenir ve anlatim CUMLE ORTASINDA kesilir.

Bu kabul edilemez. Kural: kismi yayin yolunda anlatim TAM olarak sigmali.
Cekim dustugunde anlatim metni kisaltilmis sureye gore yeniden uretilir
(`core/narration.py` zaten Gemini ile metin uretiyor, kredi harcamaz). Yeniden
uretim basarisiz olursa bolum muzik-only yayinlanir (pipeline bu yolu zaten
destekliyor ve alarm atiyor). Yarim cumle ile ASLA yayinlanmaz.

Kisalan videoya gore muzik/master zinciri tutarli kalmali (`shot_offsets`,
`running`, `audio_smooth`, `micro_trim`). Bolum suresi ve ses uzunlugu final
master'da uyusmali.

**Zorunlu platform (kanal karanlik kalmasin):** `series_runner.py:753`
bugun `ok = _publish_part(...)` sonrasi `if ok:` diyor; HERHANGI bir platform
basariliysa part `published` isaretlenip `next_part` ilerliyor. Instagram
basarili + YouTube basarisiz senaryosunda hedef kanal karanlik kalir, isaretci
ilerler ve ~500 kredi harcanmis olur. Bu hat icin opt-in `required_platforms`
tanimlanir ve `unnatural-lab` icin `["youtube"]` yazilir: `published` ve
`advance` YALNIZ YouTube dogrulaninca calisir. Alan yoksa bugunku davranis
aynen surer (diger hatlar etkilenmez).

**Rol kaybi gorunur olmali:** cekim 1 dusarsa cold-open, cekim 4 dusarse loop
seam kaybolur. Bu bilgi alarmda ve part kaydinda ACIKCA yazilir; sessizce
yutulmaz.

**Alarm ve kayit dogru katmanda:** `produce.py` gercek upload sonucunu bilmez.
Dusen cekim listesi `ProduceResult` uzerinde `dropped_shots` olarak tasinir;
BASARILI yayindan sonra `series_runner.py` tek alarm gonderir ve part kaydina
yazar. Boylece yayinlanmamis bolum icin "yayinlandi" alarmi gitmez.

**Proof:** `python -m pytest tests/test_min_shots.py -q` (yeni). Vakalar:
(a) 3/4 + min_shots=3 -> bolum birlesir, `dropped_shots` dolu;
(b) 2/4 + min_shots=3 -> iptal; (c) min_shots alani yok + 3/4 -> bugunku gibi
iptal (geriye donuk uyum); (d) dort dusus konumunun DORDU de ayri test edilir
(cekim 1, 2, 3, 4); (e) `min_shots` bool/sifir/negatif/cekim sayisindan buyuk ->
preflight ucretli cagri oncesi reddeder;
(f) part26'nin 18 saniyelik varyantinda anlatimin TAMAMI yerlesir: truncation
uyarisi YOK ve `NARRATION_MAX_EXTEND` tavanina CARPILMAZ (yalniz "ses videodan
uzun degil" demek YETMEZ, cunku kesilmis anlatim da o testi gecer);
(g) anlatim sigdirilamazsa bolum muzik-only cikar ve alarm atilir, yarim cumle
ile yayinlanmaz; (h) YouTube basarisiz + Instagram basarili -> part `published`
OLMAZ, `next_part` ILERLEMEZ; (i) `required_platforms` alani yokken bugunku
"herhangi bir platform" davranisi aynen surer.

---

## ROCK 3: Altyapi arizasi ile icerik reddi ayrilir

**Done looks like:**

**3a:** uc kopya retry merdiveni (gorsel, ham ses, teslimat sesi) TEK ortak
yardimciya toplanir. Yardimci sunucunun soyledigi `retryDelay` degerini okur
(SDK metadata, yoksa metin fallback; parse hatasinda sabit merdivene duser).
Iki tavan zorunlu: tek bekleme tavani ve TOPLAM QC bekleme tavani.

Toplam tavan CAGRI BASINA DEGIL, BOLUM GENELINDE PAYLASILAN tek butcedir. Bir
bolumde yaklasik on QC isi var; cagri basina tavan bunlarla carpilip 120
dakikalik workflow limitini yine asardi. Paylasilan butce, video uretimi,
post-process ve upload icin acik zaman tamponu birakacak sekilde secilir.

**3b:** GUNLUK kota tukenmesinde bosuna uyunmaz. 20/gun tavani saniyeler icinde
acilmaz; gunluk kota sinyali gelirse merdiven kisa devre yapar ve hold'a gecer.

**3c:** hold davranisi DEGISMEZ (fail-open yok). Ama siniflandirma duzelir:
sunucu kaynakli hold `QUOTA` diye ADLANDIRILMAZ. Ayri tipli altyapi kodu
eklenir (ornegin `TRANSIENT_INFRA`), `QUOTA` yalniz gercek kota icin kalir.
Teshis bozulmaz.

**3d:** icerik ve altyapi sayaclari AYRILIR. Altyapi kaynakli hold, icerik
`retry_count` sayacini yakmaz. Ancak altyapinin da SONLU butcesi olur (deneme
sayisi ve yas esigi); o esik asilinca insan alarmi ve `needs_human` yine devreye
girer. Kalici billing arizasinda sonsuz gunluk retry dongusu OLUSMAZ.

**Proof:** `python -m pytest tests/test_qc_backoff.py -q` (yeni). Vakalar:
(a) 429 govdesi `retryDelay: 9s` verdiginde merdiven o sureye uyar;
(b) `retryDelay` parse edilemezse sabit merdivene duser; (c) tek ve toplam
bekleme tavanlari asilmaz; (d) gunluk kota sinyalinde bosuna uyunmaz;
(e) once 429 sonra fallback 503 karisik zincirinin NIHAI nedeni ve runner sonucu
dogru siniflanir; (f) altyapi hold'u `retry_count` artirmaz; (g) altyapi butcesi
tukenince `needs_human` ve alarm YINE tetiklenir.

---

## ROCK 4: Bayat kirmizi testler onarilir, takim gercek kapi olur

**Done looks like:** `origin/main` uzerindeki iki basarisiz test, dunku bilincli
kararlari yansitacak sekilde guncellenir:

- `tests/test_gercekcilik_rock3.py::test_installed_series_enables_only_measure_scene_scan_and_800_cap`
  canli 1000 kredi tavanini bilmiyor. Gecici 1000 karari ve 800'e donus kosulu
  test sozlesmesine acikca islenir.
- `tests/test_shot_conditioning_adversarial.py::test_unnatural_lab_got_scope_but_NOT_chaining`
  `chain_frames` kapali olmasini sart kosuyor; commit 84a9192 onu bilincli acti.
  Test yeni gercege gore guncellenir, kapsam korumasi (chain_scope) korunur.

Testlerin KORUDUGU davranis silinmez, yalnizca bugunku bilincli karara
hizalanir. Kapsam korumasi zayiflatilmaz.

**Proof:** `python -m pytest tests/ -q` -> 0 failed.

---

## Elle adim (Ihsan): QC projesinde faturalandirma

`GEMINI_API_KEY_QC_UNNATURAL_LAB` hangi Google Cloud projesine aitse o projede
billing acilacak. Ucretsiz katman 20 istek/gun; hat gunde 30+ istek istiyor.
Ucretli katmanda bolum basina maliyet ~$0.01 ile $0.05 arasi.

1. https://aistudio.google.com/apikey adresinde ilgili anahtarin projesini bul.
2. Proje adina tikla, Google Cloud Console'da "Billing" bolumune gec.
3. "Link a billing account" ile kart bagli hesabi iliskilendir.
4. Bagladiktan sonra kota otomatik olarak ucretli katmana gecer, kod degisikligi
   gerekmez (ayni anahtar calisir).

Bu adim ROCK 1-4'ten bagimsizdir, kodun duzelmesini beklemez.

## Kapanis adimlari (kod bittikten sonra, SIRAYLA)

1. **Billing go/no-go kapisi.** Tetiklemeden ONCE ucretli katmana gecildigi
   dogrulanir. DIKKAT: tek ucuz Gemini cagrisinin basarili olmasi ucretli
   katmani KANITLAMAZ; ucretsiz kotada kalan son cagri da basarili doner. Test
   cagrisi yalnizca anahtar/auth kontrolu sayilir. Gercek kanit Cloud
   projesinin billing/tier durumu ve free-tier kota metrigidir. Gecmediyse
   tetikleme YAPILMAZ; aksi halde yuzlerce video kredisi yanar ve part 26
   ucuncu basarisizlikta `needs_human` olur.
2. **Part 26 durum onarimi, durustce.** Sayac sifirlama "iki basarisizlik da
   altyapiydi" diye YAZILMAZ; depo kaniti bunu yalanliyor (iki kosu da
   continuity `final_reject` ile bitti). Kayit, yeni kismi-yayin politikasi
   geregi verilmis ACIK OPERATOR OVERRIDE olarak yazilir. `retry_count` ile
   birlikte `last_reason_code`, `hold_reason`, `first_held_at` alanlari atomik
   temizlenir veya `retry_history` altinda arsivlenir; basarili yayin kaydinda
   bayat alan kalmaz.
3. Hat elle tetiklenir, kosu izlenir.
4. **Kabul kaniti (unit testler YETMEZ), kesin tanim.** Tek kosuda HEPSI:
   - `series.json` part 26 durumu `published`
   - part kaydindaki `platforms_ok` listesi `youtube` ICERIR
   - `published.json` son kaydinda `results.youtube` NULL DEGIL (gercek video
     kimligi), ve bu kimlik YouTube'da acilan gercek bir videoya karsilik gelir
   - `next_part` 27
   - final medya suresi ve ses uzunlugu olculup uyusuyor
   - dusen cekim varsa part kaydinda ve alarmda yazili
5. **Video INDIRILIP izlenir**, kontakt sayfasi cikarilir. Pipeline'in
   "basarili" demesi kalite kaniti degildir.
