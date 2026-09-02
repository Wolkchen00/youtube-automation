# RF-PLAN: Sentinal yayin acil kurtarma (2026-09-02)

## Core Focus (tek cumle)

sentinalihsandaily kanali 28 Agustos'tan beri yayin yapamiyor; QC kapisinin kendi
kendini imkansiz kilan iki tuzagi temizlenip hat bugun tek kosuda bolum yayinlar
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

Bu "hep ya da hic" kapisinin onunde uc tuzak var:

### T1: Sureklilik kapisi kendi cipasini yok ediyor

`series/produce.py:250` `_next_chain_frame()` icinde: onceki cekimin son karesi
uygunsuz bulunursa `reset_or_fail("unsuitable", ...)` calisir ve zincir karesi
`None`'a duser (`chain_frame_reset`). Sonraki cekim boylece sureklilik cipasi
OLMADAN uretilir. Ardindan ayni bolumde `qc.require_continuity: true` o cekimi
"cekimler arasi tezgah, isik veya obje-durumu surekliligi bozuk" diye reddeder.
Regen de cipasiz calistigi icin ikinci ve ucuncu deneme de ayni duvara carpar.

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

### T2: Ucretsiz Gemini kotasi matematiksel olarak yetmiyor

`qc.native_audio_review: true` zorunlu kapi. Anahtar ucretsiz katmanda:
`generate_content_free_tier_requests, limit: 20` istek/gun. Olculen gercek yuk
(`sentinal_ihsan/unnatural-lab/qc_log.jsonl`, `qc_api_attempt` olaylari):

```
2026-08-28  61 cagri
2026-09-01  32 cagri  (17 ses + 15 gorsel)
2026-09-02  33 cagri  (21 ses + 12 gorsel)
```

Temiz bir bolum bile 4 cekim x 2 kapi + zincir denetimleri = ~10 cagri. Regen
girince 30+. Yani 20/gun tavani ile bu hat asla duzenli yayin yapamaz. Kota
bitince `critic.py:1517` "QC HOLD: zorunlu kapida degerlendirilemedi" der,
`produce.py` `ProduceResult("qc_hold")` doner ve bolum olur. Altyapi arizasi
icerik reddi gibi islenmis oluyor.

Bekleme merdiveni de sabirsiz: 429 govdesi `retryDelay: 9s` derken merdiven
5s ve 10s bekleyip pes ediyor.

### T3: Kismi ilerleme tasinmiyor (bu turda DEFER)

QC'den gecmis cekimler basarisiz kosuda cope gidiyor. Kosu 33594947982 alti klip
x 84 kredi = 504 kredi yakti, sifir yayin. Ayni bolum ertesi kosuda sifirdan
uretiliyor; part 23 ve 24 tam bu yuzden `budget_exhausted` oldu.

GitHub runner efemer: `.github/workflows/unnatural-lab.yml` yalniz `logs/` ve ses
stem'lerini artifact yapiyor, `output/` hicbir yere kalici yazilmiyor;
`scripts/persist_state.sh` sadece durum klasorlerini commit'liyor. Kosular arasi
cekim tasimak icin ayri bir kalici depo (Release veya artifact indirme) gerekir.
Bu acil turun kapsami disinda: ROCK 1-3 + faturalandirma ile bolumun TEK kosuda
bitmesi hedefleniyor, o zaman tasima gereksiz kalir. ISSUES'a yazildi.

## Ihsan kararlari (2026-09-02)

1. QC kotasi: **faturalandirma acilacak** (ucretli katman). Elle adim, asagida.
2. Regen'e ragmen gecemeyen cekim: **kalan cekimlerle yayinlansin**, alarm gitsin.

## Non-goals

- Kosular arasi cekim tasima (T3). ISSUES'a.
- QC kalite esiklerini gevsetmek. Esikler aynen kalir; sadece kendi kendisiyle
  celisen kapi ve altyapi arizasinin icerik reddi sayilmasi duzeltilir.
- Diger hatlarin (aimagine, galactic_experience, shadowedhistory) davranisini
  degistirmek. Yeni davranislar opt-in alan olarak gelir, varsayilan bugunku
  davranistir.
- Yeni bolum icerigi yazmak, plan/bible metni degistirmek.

## Kisitlar

- Python 3.11, mevcut bagimlilklar. Yeni paket yok.
- `series/produce.py` ve `series/critic.py` disinda kod dosyasi degismesin
  (bible.json ve testler haric).
- Turkce log/alarm metinleri mevcut usluba uysun.
- Em dash karakteri kullanilmayacak.

---

## ROCK 1: Sifirlanan zincir, sureklilik kapisini muaf tutar

**Done looks like:** `_next_chain_frame()` bir cekim icin `chain_frame_reset`
urettiginde, BIR SONRAKI cekimin QC'sinde sureklilik olcutu red sebebi olamaz.
Sureklilik gozlemi gunluge yazilmaya devam eder (`continuity_ok` alani korunur),
ama `verdict` sadece o olcut yuzunden `fail` olmaz. Zincir normal aktiginda
sureklilik kapisi bugunku gibi sert kalir.

**Neden:** cipayi sistem kendi kaldiriyor, sonra cipanin urunu olan surekliligi
sart kosuyor. Regen bunu asla cozemez, sadece kredi yakar.

**Kapsam:** `series/produce.py` (reset bayragini bir sonraki cekimin qc_context'ine
tasi), `series/critic.py` (bayrak varken sureklilik olcutunu red sebebi olmaktan
cikar, gozlem olarak logla).

**Dikkat:** bayrak TEK cekim icin gecerlidir. Cekim 3 -> 4 sifirlandiysa yalniz
cekim 4 muaf olur; cekim 4 -> 5 zinciri saglamsa cekim 5 yine sert kapiya girer.
Bayrak kalici olmamali, bir sonraki basarili zincirde temizlenmeli.

**Proof:** `python -m pytest tests/test_chain_reset_continuity.py -q` (yeni dosya)
ve mevcut takim: `python -m pytest tests/ -q`.

---

## ROCK 2: Eksik cekim tabani (min_shots), bolum kalan cekimlerle yayinlanir

**Done looks like:** `bible.series.qc.min_shots` (tam sayi) opt-in alani eklenir.
Alan yoksa bugunku `require_all_shots` davranisi aynen surer (diger hatlar
etkilenmez). Alan varsa: QC'den gecen cekim sayisi `min_shots` degerine esit veya
buyukse bolum kalan cekimlerle birlestirilir ve yayinlanir; altindaysa bolum
bugunku gibi iptal edilir. `unnatural-lab` icin `min_shots: 3` yazilir.

Yayin gerceklestiginde Telegram'a dusen cekim numarasini ve nedenini soyleyen
alarm gider, ve part kaydina hangi cekimin dustugu yazilir.

**Neden:** dort cekimden ucu gecmisken kanalin karanlik kalmasi, 18 saniyelik
bolumden daha kotu.

**Kapsam:** `series/bible.py` (yeni ozellik), `series/produce.py` (satir 1527,
1679, 1717 uc kapinin da min_shots'u dikkate almasi),
`sentinal_ihsan/unnatural-lab/bible.json` (`min_shots: 3`).

**Dikkat:** `shot_offsets` ve sure hesabi eksik cekimle tutarli kalmali; sessiz
seri oldugu icin anlatim hizalamasi yok, ama muzik ve master sure hesabi kirilmamali.

**Proof:** `python -m pytest tests/test_min_shots.py -q` (yeni dosya). En az uc
vaka: 3/4 gecti + min_shots=3 -> bolum birlesir; 2/4 gecti + min_shots=3 -> iptal;
min_shots alani yok + 3/4 -> bugunku gibi iptal (geriye donuk uyum).

---

## ROCK 3: Altyapi arizasi icerik reddi degildir (sabirli merdiven)

**Done looks like:** QC API bekleme merdiveni sunucunun soyledigi sureye uyar.
429 govdesindeki `retryDelay` alani okunur ve o kadar beklenir (ust sinir ile),
deneme sayisi bugunkunden fazladir. Merdiven tukendiginde davranis DEGISMEZ
(`hold` kalir, fail-open YOK), ama `hold` sebebi tipli kod olarak dogru yazilir:
kota veya sunucu kaynakli hold `UNKNOWN` degil `QUOTA` olarak kaydedilir, boylece
`retry_count` altyapi arizasi yuzunden `needs_human` esigine dogru yurumez.

**Neden:** Ihsan faturalandirmayi aciyor, bu 429'lari bitirir. Ama 503
UNAVAILABLE (model yogunlugu) faturali katmanda da olur. 5s + 10s bekleyip pes
eden merdiven, sunucu "9.5 saniye sonra tekrar dene" derken bolumu olduruyor.

**Kapsam:** `series/critic.py` (merdiven ve reason_code siniflandirmasi).

**Dikkat:** part 26 kaydinda `last_reason_code: "UNKNOWN"` ve `retry_count: 2`
var; bu yanlis siniflandirmanin urunu. Kod duzeldikten sonra bu kayit
elle duzeltilecek (asagida kapanis adimi).

**Proof:** `python -m pytest tests/test_qc_backoff.py -q` (yeni dosya): 429 govdesi
`retryDelay: 9s` verdiginde merdivenin o sureye uydugu, ve tukenen kota
holdunun `QUOTA` kodu urettigi.

---

## Elle adim (Ihsan): QC projesinde faturalandirma

`GEMINI_API_KEY_QC_UNNATURAL_LAB` hangi Google Cloud projesine aitse o projede
billing acilacak. Ucretsiz katman 20 istek/gun; hat gunde 30+ istek istiyor.
Ucretli katmanda bolum basina maliyet ~$0.01 ile $0.05 arasi.

1. https://aistudio.google.com/apikey adresinde ilgili anahtarin projesini bul.
2. Proje adina tikla, Google Cloud Console'da "Billing" bolumune gec.
3. "Link a billing account" ile kart bagli hesabi ili$kilendir.
4. Bagladiktan sonra kota otomatik olarak ucretli katmana gecer, kod degisikligi
   gerekmez (ayni anahtar calisir).

Bu adim ROCK 1-3'ten bagimsizdir; kodun duzelmesi icin beklemez.

## Kapanis adimlari (kod bittikten sonra)

1. `sentinal_ihsan/unnatural-lab/series.json` part 26 kaydinda `retry_count` 0'a
   cekilir (iki basarisizlik da altyapi kaynakliydi, icerik reddi degildi).
2. Hat elle tetiklenir, kosu izlenir.
3. Uretilen video INDIRILIP izlenir; kontakt sayfasi cikarilir. Pipeline'in
   "basarili" demesi kalite kaniti degildir.
