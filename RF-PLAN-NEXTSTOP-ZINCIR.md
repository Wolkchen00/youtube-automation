# RF-PLAN: Next Stop zincir kırılganlığı

## Core Focus

Next Stop, aimagine kanalının tek şeridi olarak her gün yayınlayabilsin: tek bir
kötü kare bütün bölümü öldürmesin.

## Teşhis (ölçüldü, tahmin değil)

2026-09-02 koşusu, bölüm 5, `qc_log.jsonl` kaydı aynen:

```json
{"event": "chain_frame_failure", "episode": 5, "shot": 1, "next_shot": 2,
 "verdict": "fail_closed", "reason": "unsuitable",
 "reasons": ["anatomi bozuk",
   "The hand of the rightmost passenger is unnatural and could be amplified if used as a conditioning frame."],
 "canonical_source": null}
```

Zincir şöyle çalışıyor (`series/produce.py:_next_chain_frame`, `reset_or_fail`):

1. Her kabul edilen çekimin SON KARESİ ayrıca QC'den geçer (bir sonraki çekime
   koşullama görseli olacağı için).
2. Kare uygunsuzsa `reset_or_fail("unsuitable")` çağrılır.
3. `reset_or_fail`, bir sonraki çekimin KANONİK GÖRSELİ varsa zinciri sıfırlar ve
   üretim devam eder (yalnız uyarı).
4. Kanonik görsel YOKSA kapı kapanır (fail-closed) ve **bölüm ölür**.

`canonical_source`, `_canonical_scene_source()` ile bulunuyor: omni motorunda
`resolve_shot(...)["kwargs"]["image_urls"]` boş değilse "omni_image_references".
`image_urls` ise yalnız üç yerden dolar (`series/shots.py`):
`bible.environments[env_id].ref_image_url`, `props[].ref_image_url`,
`characters[].ref_image_url`.

**Kök neden:** next-stop bible'ında `environments`, `props`, `characters`
ÜÇÜ DE BOŞ (`[]`), ve planlardaki çekimler `environment`/`props` alanı hiç
taşımıyor (çekim anahtarları yalnız `n, duration, prompt, seed, chain`).
Dolayısıyla `image_urls` HER ZAMAN boş, `canonical_source` HER ZAMAN `None`.

Sonuç: bölümdeki 5 zincir sıçramasının (çekim 1→2, 2→3, 3→4, 4→5, 5→6) HER BİRİ
tek başına bütün bölümü öldürebilen bir tekil arıza noktası. Yedek yok.
`style_ref_url` bu boşluğu KAPATMIYOR: bible'da tanımlı ama `resolve_shot`
tarafından hiç okunmuyor (yalnız `bible.py` ve `stack_fingerprint.py` biliyor).

## Kapsam dışı olduğu doğrulananlar

- Doktrin kapısı risk değil: `doctrine_sha256` KONSEPT.md'yi hashliyor
  (`series/bible.py:doctrine_path`), bible.json'u değil. `environments` eklemek
  pin'i bozmaz.
- Kredi maliyeti yok: referans görsel Kie'ye ek üretim çağrısı değil, koşullama
  görseli. Bölüm bütçesi (`EPISODE_CREDIT_CAP=1900`) değişmiyor.

## ROCK 1 ,  Kanonik vagon referansı

**Ne:** next-stop'a bir `environment` referansı tanımla, böylece zincir karesi
reddedilince üretim kanonik görsele sıfırlansın, ölmesin.

Referans kare seçildi (Visionary kararı): `ep92_hooked.mp4` @ 20.0 sn. Gerekçe:
vagon kimliğinin en çok göründüğü kare (tekrarlayan kemerli pencere çerçeveleri,
tavan şerit aydınlatması, dikey tutamak borusu, zemin ızgarası, cam tavan),
pozlama dengeli, ve tutamağı kavrayan el anatomik olarak TEMİZ. Bu bölüm
2026-09-02'de yayınlandı, yani kanonik görünüm zaten onaylı.

- Kareyi çıkar, imgbb'ye yükle (`core/imgbb.py`, `IMGBB_API_KEY` mevcut).
- `aimagine/next-stop/bible.json` içine ekle:
  `environments: [{"id": "carriage", "ref_image_url": "<imgbb url>",
   "description": "..." }]`
- `aimagine/next-stop/plans/part05.json` ... `part09.json` içindeki HER çekime
  `"environment": "carriage"` ekle.

**Done looks like:** `_canonical_scene_source(bible, shot, plan, "omni")` bekleyen
her çekim için `"omni_image_references"` döndürür, `None` değil.

**PROOF:** `python -m pytest tests/test_nextstop_chain_fallback.py -q`

## ROCK 2 ,  Gelecek bölümler de referansı taşısın

`series/replenish.py` Gemini'ye yazdırdığı plan şablonunda her çekime
`"environment": "carriage"` koysun. Yoksa ROCK 1 yalnız part05-09'u kurtarır,
part10'dan sonra arıza geri gelir.

**Done looks like:** replenish'in ürettiği yeni plan çekimleri `environment`
alanı taşır.

**PROOF:** `python -m pytest tests/test_nextstop_chain_fallback.py -q`

## ROCK 3 ,  Muhafız

Bu tekil arıza noktası sessizce geri gelemesin.

- next-stop'un her aktif plan çekimi için kanonik kaynağın `None` OLMADIĞINI
  doğrulayan test.
- `bible.environments` boş bırakılırsa testin KIRMIZI yandığını mutasyonla
  kanıtla.

**PROOF:** `python -m pytest tests/test_nextstop_chain_fallback.py -q`

## Kapsam dışı (NON-GOALS)

- Zincir QC eşiğini gevşetmek. Kare gerçekten bozuksa reddedilmeli; çözüm
  yedek yol açmak, denetimi körleştirmek değil.
- `produce.py` motor kodunu değiştirmek. `reset_or_fail` zaten doğru çalışıyor;
  eksik olan veri, mantık değil. Dört kanal ortak motoru riske atma.
- from-scratch'i geri açmak.
- Yayınlanmış part 1-4 durumuna dokunmak.
- Bölüm 5'i bu planın parçası olarak üretmek/yayınlamak. Üretim ayrı bir karar.

## Tur 1 cevaplari (Visionary)

**KABUL , ortam referansi HER cekimin uretimini degistiriyor.** Dogru tespit,
`shots.py:257` chain_url'i de `image_references`e ekliyor, yani zincirli bir cekim
bugun 1 kosullama gorseli aliyor, referans eklenince 2 alacak. Bu bir davranis
degisikligi ve plan bunu artik acikca kabul ediyor.

Ihsan karari 2026-09-02: referans eklenecek. Gerekce:
- Bu seride "oda" vagonun ta kendisi ve kanon zaten her cekimde AYNI vagoni sart
  kosuyor (kilitli kadraj, kamera vagondan hic cikmiyor). Referansin etiketi de
  tam bunu soyluyor: "is the room and surface: keep the same surface and light."
  Yani referans gorunumu kaydirmiyor, kanonun zaten istedigi seyi sikilastiriyor.
- Olculmus kanit: v3 pilotunda (ep91) vagon kimligi bolumun ortasinda kopuyor,
  ilk uctelik aydinlik vagonda oturan yolcular, son uctelik tamamen farkli koyu
  vagonda ayakta yolcular. Vagon referansi tam bu kusura karsi calisir.
- Geri alinmasi tek satir: `bible.environments` bosaltilir, eski davranis doner.
  Motor koduna dokunulmadigi icin diger uc kanal hicbir sekilde etkilenmez.

**KABUL , part10+ bosluğu.** ROCK 2 bu dongude ZORUNLU, opsiyonel degil. ROCK 1
tek basina teslim edilemez. ROCK 3 muhafizi yalnizca mevcut planlari degil,
replenish'in urettigi YENI plan sablonunu da denetlemeli.

**CEVAP , "ep92 bir yazim hatasi mi?"** Hayir. part90/91/92 pilot deney
numaralari, kuyruk bolumu degil: nextstop-v2-pilot=part90, v3-pilot=part91,
v31-pilot=part92. ep92 su anki kanon v3.1'in pilotu ve 2026-09-02'de
"Next Stop: The Deep" adiyla yayinlandi. Yani referans karesi seride SU AN
gecerli olan gorunumu tasiyor, part05-09 ile ayni kanon.

**REDDEDILDI , KILL.** Core Focus zaten "tek kotu kare bolumu oldurmesin"
diyor, yedek yol acmak bu odagin ta kendisi. Motor kodunu degistirmek (kanonigi
yalniz sifirlamada kullanmak) daha temiz olurdu ama `produce.py` dort kanalin
ORTAK motoru; oradaki bir hata Sentinal, Galactic ve Shadowed History'yi de
dusurur. Veri duzeyi kaldirac, patlama yaricapi en kucuk olani. Ihsan bu takasi
gorup referansi sectti.

**COZULDU , doktrin override kontrolu.** Olculdu: `aimagine/next-stop/series.json`
icinde ne `doctrine` ne de `doctrine_sha256` anahtari VAR (ikisi de yok, null
degil, hic yok). Yani bu seride doktrin kapisi zaten atil ve `environments`
eklemek onu tetiklemez.

**CEVAP , "muhafiz testi henuz yok".** Dogru, cunku o ROCK 3'un teslimati.
Testin gercekten yakaladigini iddia etmekle yetinmeyecegim: `bible.environments`
bosaltilarak mutasyon testi kosulacak ve testin KIRMIZI yandigi gosterilecek.

## ROCK 3 , revize edilmis kapsam

Muhafiz testi su ucunu birden denetler:
  a) next-stop bible'inda `environments` icinde `carriage` var ve
     `ref_image_url` dolu.
  b) Mevcut TUM aktif planlarda (part05..part09) her cekim `environment` alani
     tasiyor.
  c) `_canonical_scene_source` bu cekimler icin `None` DONDURMUYOR. Gercek kod
     yolu cagrilir, alan varligina bakip gecmek yeterli degildir.
  d) replenish'in urettigi plan sablonu `environment` alanini tasiyor
     (ROCK 2'nin kalici kaniti, part10+ boslugu geri gelemez).

Mutasyon kanitlari: (1) `environments` bosaltilirsa test kirmizi, (2) bir
plandan `environment` alani silinirse test kirmizi.

## Tur 2 cevaplari (Visionary)

**KABUL VE COK DEGERLI , ROCK 2 kod degil KONFIG isiymis.** Dogruladim:
`series/replenish.py:550` `shot_refs = bool(cfg.get("shot_refs")) and not
bible.omit_character_refs`; `:595-596` yalniz `shot_refs` dogruysa shot_fields'a
`"environment"` ekliyor; `:1163-1167` uretilen cekimde `environment`i ancak
bible'da o id varsa koruyor; `:916-925` `shot_refs` dogruysa prompta
"AVAILABLE REFERENCES (use these ids only)" blogunu basiyor.
Olculdu: next-stop `auto_replenish` icinde `shot_refs` anahtari HIC YOK,
`bible.omit_character_refs` False.

ROCK 2 bu yuzden YENIDEN YAZILDI: `series/replenish.py`'ye DOKUNULMAYACAK.
Sadece `aimagine/next-stop/series.json` -> `auto_replenish` icine
`"shot_refs": true` eklenecek. Bu, dort kanalin ortak replenish kodunu riske
atmadan ayni sonucu veriyor. Patlama yaricapi kod degisikligine gore cok daha
kucuk; bu bulgu plani daha guvenli hale getirdi.

**YENI RISK (bu turda bulundu, kapatiliyor).** `:596` sablonu environment'i
"optional" diye yaziyor, yani Gemini bazi cekimlerde alani atlayabilir; o
cekimler yine kanonik kaynaksiz kalir ve arıza geri doner. ROCK 2 bu yuzden
ikinci bir KONFIG degisikligi daha icerir: `auto_replenish.brief` sonuna
zorunlu bir kural eklenir , her cekim `"environment": "carriage"` yazmak
ZORUNDADIR, atlanamaz. brief bir konfig dizesidir, kod degil.

**CEVAP , referans karesi part05-09 kanonuyla eslesiyor mu?** Eslesiyor, ve
yayinlanmis part 1-4'ten DAHA iyi esleşiyor. Gerekce olculdu:
- part05-09 henuz video olarak URETILMEDI (next_part=5). Uretildiklerinde su
  anki bible ile uretilecekler.
- Su anki bible kanon v3.1: `auto_replenish.brief` icinde
  "(20) CANON YANKISI (v3.1)" maddesi var (dogrulandi).
- ep92 tam da bu v3.1 kanonunun pilotu. Yayinlanmis part 1-4 ise v3.1 ONCESI
  kanonla uretildi. Yani part05-09'un gorunumune en yakin ornek ep92'dir.
- `art_style` "THE CARRIAGE IS A GLASS OBSERVATION CAR: the LEFT wall is one
  continuous..." diyor; sectigim kare tam bunu gosteriyor: solda cam duvar,
  tavana kavis yapan cam, sag kenarda direge tutunan ayakta yolcular.

**KABUL , ROCK 3'un proof komutu henuz var olmayan bir dosyayi gosteriyor.**
Dogru. Plan artik acikca soyluyor: `tests/test_nextstop_chain_fallback.py`
ROCK 3'un TESLIMATIDIR, mevcut bir dosya degil. Proof ancak ROCK 3 bittikten
sonra anlamlidir.

## ROCK 2 , YENIDEN YAZILDI (yalniz konfig)

`aimagine/next-stop/series.json` icinde `auto_replenish`:
  1. `"shot_refs": true` ekle.
  2. `brief` sonuna zorunlu kural ekle: her cekim `"environment": "carriage"`
     tasimak zorundadir.

`series/replenish.py` DEGISMEZ. Hicbir motor dosyasi degismez.

**Done looks like:** replenish'in urettigi yeni plan cekimleri `environment`
alanini tasir ve deger `carriage`tir.

## Tur 3 cevaplari (Visionary)

**KABUL AMA DEFER , brief kurali kodla dayatilmiyor.** Dogru: `_validate_batch`
`environment` alanini varsa korur, ZORUNLU KILMAZ. Alani tasimayan bir plan
dogrulamadan gecip kuyruga girebilir. Bu gercek bir bosluk, ancak:
- Bosluk durumu BUGUNKU davranisin AYNISI: o cekim kanonik kaynaksiz kalir.
  Yani en kotu ihtimalle bugune donuyoruz, daha kotusune degil. Regresyon yok.
- Onumuzdeki bes bolum (part05-09) ROCK 1'de ELLE yamalaniyor, yani replenish'in
  davranisindan bagimsiz olarak kanonik kaynakli.
- ROCK 3 muhafizi CI'da her push'ta kosuyor; alani dusuren bir plan bir sonraki
  kosuda kirmizi yanar.
- Kodla dayatmak `replenish.py` demek, o da dort kanalin ORTAK dosyasi. Bu
  dongude bilerek ISSUES'a birakiliyor.
ISSUES kaydi: "replenish `environment` alanini zorunlu dogrulamiyor; next-stop
disindaki seriler icin de gecerli, motor dokunusu gerektirdiginden ertelendi."

**REDDEDILDI , "shot_refs henuz eklenmemis" ve "brief kurali henuz yok".**
Bunlar plan kusuru degil: bir PLANIN tanimi zaten "henuz uygulanmamis is"tir.
Ikisi de ROCK 2'nin teslimati olarak yaziliyor. Uygulanmis olsalardi plana
gerek kalmazdi.

**REDDEDILDI (zaten cevaplandi) , proof dosyasi yok.** Plan bunu Tur 2'de
acikca kabul etti: dosya ROCK 3'un teslimati. Ayni bulguyu tekrar gundeme
getirmek yerlesmis bir noktayi yeniden tartismaktir.
