# RF-PLAN: Mukerrer yayin kapisi + gunluk farkli durak guvencesi

## Core Focus

Ayni baslik kanala ikinci kez cikamasin, ve kanal her gun FARKLI bir durakla
kendiliginden yayin yapmaya devam etsin.

## Olculen durum (tahmin degil)

**Gunluk boru hattinda durak tekrari ZATEN engelleniyor.** `replenish.py:1544`
plan gecmisinden `existing = {_norm_title(...)}` kuruyor, `_validate_batch:1004`
tekrar eden basligi reddediyor ("baslik tekrari"). Olculdu: next-stop'ta 9 plan,
9 benzersiz baslik. Kuyrukta 4 farkli durak var (Bifrost, Neo-Tokyo, Primordial
Sea, The Void), `min_queue=2` altina inince 5'lik parti uretiliyor. Yani ikinci
istek buyuk olcude KARSILANIYOR; eksik olan onun KANITI ve muhafizi.

**Gercek bosluk yayin anindadir.** Hicbir yerde "bu baslik kanalda zaten var mi"
diye bakilmiyor. Kanalda birikenler:
- "Next Stop: The Deep" x3 (2026-09-01 19:24 ep91 pilotu, 09-01 22:28 ep92
  pilotu, 09-02 19:54 benim elle yayinim)
- "Next Stop: Hell" x5 (2026-08-29)

Iki kacak yol var, ikisi de `_episode_history` disindan geciyor:
1. **Pilot/deney kosulari.** `output/experiments/<exp>/...` izole agacta uretiyor;
   `_episode_history` yalniz `plans_dir(slug)` okuyor, bu yuzden pilot basliklari
   dedup'a hic girmiyor. ep91 ve ep92 ikisi de "The Deep" oldu.
2. **Elle yayin.** `core.uploader.publish_video` dogrudan cagrildiginda hicbir
   kontrol yok. 2026-09-02'de tam bunu yaptim.

## Rock oncesi dogrulanan mekanikler

- `series_runner.py:820-825`: `publish_complete = bool(ok) and
  required_platforms.issubset(published_platforms)`. next-stop'ta
  `bible.required_platforms` BOS, yani tek bir platform bile gecerse bolum
  yayinlanmis sayilip ilerliyor. Kapi YouTube'u atlarsa IG/TikTok gecer, bolum
  ilerler, SONSUZ YENIDEN DENEME OLMAZ.
- `core/analytics.py:CHANNELS` kanal adi -> channel_id esleme zaten var;
  yeni bir esleme tablosu YAZILMAYACAK, o kullanilacak.
- Kanal yuklemeleri anahtarsiz okunabiliyor:
  `https://www.youtube.com/feeds/videos.xml?channel_id=<ID>` (son ~15 video).

## ROCK 1 , tek normalizasyon kaynagi

Kapi ile replenish AYNI normalizasyonu kullanmali. Ayrisirlarsa bir baslik
replenish'ten gecip kapida takilir ve gunluk video sessizce dusen bir platformla
cikar. Bu yuzden:

- `core/utils.py` icine `normalize_title(t: str) -> str` (kucuk harf, harf/rakam
  disi her sey bosluga, kirp). Emoji tamamen dusuyor, yani "The Deep 🚆🌊" ile
  "The Deep" ayni sayiliyor , istenen davranis bu.
- `series/replenish.py:_norm_title` bu fonksiyona DEVREDER (govdesi silinir,
  cagri kalir). Davranis birebir ayni, tek kaynak olur.

**PROOF:** `python -m pytest tests/test_publish_duplicate_gate.py -q`

## ROCK 2 , yayin kapisi

`core/uploader.py`:

- `channel_recent_titles(channel_name) -> set[str] | None`: kanalin RSS'ini oku,
  basliklari `normalize_title`den gecir, kume dondur. HERHANGI bir hatada
  (ag, zaman asimi, bozuk XML, bilinmeyen kanal) `None` don.
- `publish_video(..., allow_duplicate_title: bool = False)`:
  - Kapi YALNIZCA `youtube` platformuna uygulanir. Gerekce: RSS yalniz YouTube
    gorunurlugu veriyor; ayrica YouTube basarili olup IG/TikTok dustugunde
    yapilan yeniden deneme, tum yayini degil sadece YouTube'u atlamali.
  - Baslik kanalda varsa: o platform ATLANIR, `logger.error` ile acikca yazilir,
    sonuc sozlugune yukleme yapilmadigi belli olacak sekilde girer.
  - `channel_recent_titles` `None` donerse: `logger.warning` ile "kanal
    dogrulanamadi, yayina devam ediliyor" ve yayin SURER (fail-open).
  - `allow_duplicate_title=True` kapiyi bilerek atlar.

**Fail-open karari ve gerekcesi:** ag hatasinda yayini durdurmak, gunluk kanali
gecici bir DNS tokezlemesi yuzunden karartir. Mukerrer bir video, kacirilmis bir
gunden daha ucuzdur ve geri alinabilir. Bu bilincli bir takas; kapi bir emniyet
kemeridir, kilit degil.

**PROOF:** `python -m pytest tests/test_publish_duplicate_gate.py -q`

## ROCK 3 , muhafiz testleri

`tests/test_publish_duplicate_gate.py`:
- `normalize_title` emoji, noktalama, buyuk/kucuk harf ve bosluk farklarini
  ayni degere indiriyor.
- `replenish._norm_title` ile `normalize_title` AYNI sonucu veriyor (ayrisma
  muhafizi).
- Kanalda ayni baslik varken `publish_video` YouTube'a YUKLEMIYOR (ag cagrisi
  taklit edilir, gercek istek atilmaz).
- Ayni durumda instagram/tiktok YINE yukleniyor.
- `channel_recent_titles` `None` dondugunde (ag hatasi) yayin ENGELLENMIYOR.
- `allow_duplicate_title=True` kapiyi atliyor.
- next-stop kuyrugundaki tum plan basliklari benzersiz (gunluk farkli durak
  guvencesinin muhafizi).
- next-stop `status=active` ve cron'u canli, yani gunluk yayin gercekten koşuyor.

Mutasyon kanitlari: normalizasyon ayrisirsa, kapi kaldirilirsa ve kuyruga tekrar
eden baslik sokulursa testler KIRMIZI yanmali.

**PROOF:** `python -m pytest tests/test_publish_duplicate_gate.py -q`

## Kapsam disi (NON-GOALS)

- Kanaldaki mevcut mukerrerleri SILMEK. Ihsan karari 2026-09-02: izlenme
  aliyorlar, kalacaklar.
- Instagram/TikTok icin mukerrer kontrolu. O platformlarda kanal gorunurlugu yok.
- `output/experiments` pilot akisini degistirmek. Kapi zaten onlari da yakalar,
  cunku pilotlar da `publish_video` uzerinden yayinlaniyor.
- Zorunlu platform (`required_platforms`) politikasini degistirmek.
- from-scratch'i geri acmak.

## Tur 1 cevaplari (Visionary)

**KABUL , KILL hakliydi ve plani kurtardi.** Dogruladim: `series_runner.py:27`
`from core.uploader import pop_upload_failure, upload_to_platform` yapiyor ve
`:336` dogrudan onu cagiriyor; `publish_video` series_runner'da HIC gecmiyor.
Kapiyi `publish_video`ya koysaydim gunluk boru hattinda ve pilotlarda hic
calismayacakti , yalnizca benim elle yayinimi yakalayacakti. Yani plan tam da
onlemek istedigi iki kacak yolu acik birakacakti.

**ROCK 2 YENIDEN YAZILDI:** kapi `upload_to_platform` icine giriyor. Olculdu,
depodaki TEK tikanma noktasi o: cagiranlari `core/uploader.py:529`
(publish_video'nun kendisi), `series/series_runner.py:336` (gunluk boru hatti) ve
testler. Oraya konan kapi her uc yolu da kapsar.

**KABUL , paylasilan sicak yolda ag cagrisi.** Dort kanal ayni fonksiyondan
geciyor. Onlem: (a) kontrol YALNIZ `platform == "youtube"` icin calisir,
(b) istek zaman asimi 5 saniye, (c) kanal basina surec-ici onbellek, yani
3 platformluk bir yayin en fazla 1 istek atar. En kotu durum: bolum basina
+5 saniye. Kabul edilebilir.

**KABUL , "ag hatasi" tanimi belirsizdi.** Tanim insa yoluyla tam olacak:
`channel_recent_titles` govdesinin TAMAMI `try/except Exception` icinde; herhangi
bir istisna, 200 disi HTTP kodu, ayristirilamayan XML ya da bos akis `None`
dondurur ve `None` her zaman fail-open demektir. Sinif sinif saymaya gerek yok,
bilinmeyen her sey "dogrulanamadi" kovasina duser.

**KABUL AMA DEFER , RSS 15 video penceresi.** Kapi son ~15 yuklemeyi gorur.
Gozlemlenen ariza tam bu pencerede: "The Deep" 24 saat icinde 3 kez, "Hell" ayni
gun 5 kez. Daha eski tekrarlari replenish'in plan-gecmisi dedup'u zaten
kapsiyor (o TUM planlari gorur, pencere yok). Iki katman birbirini tamamliyor.
Kapi bir EMNIYET KEMERI, kilit degil; plan bunu artik acikca boyle yaziyor.

**KABUL , kanal kimligi eslemesi yok.** `upload_to_platform` `channel_name`
degil `user` (yukleme profili, aimagine icin "Youtube") aliyor. Cozum:
`core.config.UPLOAD_USERS` tersine cevrilerek profil -> kanal adi, sonra
`core.analytics.CHANNELS` ile kanal adi -> channel_id. `core.analytics` importu
dongusel import riskine karsi fonksiyon ICINDE yapilir. Yeni esleme tablosu
YAZILMAZ.

**KABUL , bayrak dogru katmana tasinmali.** Kapi artik `upload_to_platform`ta
oldugu icin `allow_duplicate_title` de orada tanimlanir; `publish_video` bayragi
oldugu gibi iletir.

**KABUL , mock'lanan test gercek RSS ayristirmasini dogrulamaz.** ROCK 3'e
eklendi: testlerden biri AG CAGRISI YAPMADAN, gercek YouTube RSS'inden alinmis
gomulu bir ornek metni ayristirir ve basliklari dogru cikardigini kanitlar.
Boylece ayristirma da gercekten sinaniyor.

**AKSIYON YOK , yalniz YouTube kapisi.** Nemotron kendi analizinde bunun kapsam
acisindan dogru oldugunu tespit etti. Degisiklik yok.

**KABUL , kapi tavsiye niteliginde.** Evet, fail-open oldugu icin garanti degil.
Bilincli takas ve plan bunu boyle belgeliyor.

**CEVAP , test dosyasi yok.** ROCK 3'un teslimati, mevcut dosya degil.

## ROCK 2 , YENIDEN YAZILDI

`core/uploader.py`:
- `channel_recent_titles(user: str) -> set[str] | None`: profil -> kanal adi ->
  channel_id cozer, RSS'i 5 sn zaman asimiyla ceker, basliklari
  `normalize_title`den gecirir. Govde tamamen try/except; her hatada `None`.
  Surec-ici onbellek.
- `upload_to_platform(..., allow_duplicate_title: bool = False)`:
  `platform == "youtube"` ve bayrak kapaliyken basligi kontrol eder. Kanalda
  varsa YUKLEMEZ, `logger.error` yazar ve `None` doner (mevcut basarisizlik
  sozlesmesiyle ayni sekil). `None` donerse `series_runner` o platformu
  `platforms_ok`a koymaz, `required_platforms` bos oldugu icin bolum yine ilerler.
- `publish_video(..., allow_duplicate_title: bool = False)` bayragi iletir.

## Tur 2 cevaplari (Visionary)

**CEVAP , onbellek nerede duracak.** Evet, niyet tam da o: onbellek
`core/uploader.py` icinde MODUL duzeyinde bir sozluk olacak
(`_channel_titles_cache: dict[str, set[str] | None]`), fonksiyon-yerel degil.
Boylece tek bir bolumun youtube/instagram/tiktok cagrilari arasinda yasar ve
bolum basina en fazla 1 RSS istegi atilir.

**CEVAP , zaman asimi acikca yazilacak.** `requests.get(..., timeout=5)`.
Varsayilan "zaman asimi yok" davranisina asla guvenilmeyecek; bu zaten sicak
yolu dort kanal icin kilitleyebilecek olan riskti.

**REDDEDILDI , bes KILL'in tamami "kod henuz yazilmadi" diyor.** `normalize_title`
yok, `channel_recent_titles` yok, `allow_duplicate_title` yok, test dosyasi yok,
kapi kodda yok , bunlarin hepsi ROCK 1, 2 ve 3'un TESLIMATI. Bir planin tanimi
"henuz yapilmamis is"tir; uygulanmis olsalardi plana gerek olmazdi. Bunlar plan
kusuru degil, planin icerigi. Ayni sey Tur 1'de de olmustu.

Nemotron'un kendi ozeti bunu zaten soyluyor: "The revised plan correctly fixes
the architectural flaws (gate at choke point, error taxonomy, channel
resolution, test with real RSS), but none of it is implemented."
