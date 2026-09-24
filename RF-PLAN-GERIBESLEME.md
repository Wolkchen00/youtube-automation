# RF-PLAN-GERIBESLEME: performans geri beslemesi + sehir istekleri

Tarih: 2026-09-24. Sahip: Ihsan. Visionary: Claude. Integrator: Codex.

## Core Focus

Bir videonun gercek sonucu (YouTube + Instagram + TikTok izlenmesi, kanalin KENDI
gecmisine gore) bir sonraki bolumu yazan planlayiciya ulassin; aimagine'de
izleyicinin yorumda istedigi sehirler sayilsin ve siradaki rota adayi olsun.

## Neden (olculen)

- `core/analytics.py` yalniz YouTube public view sayar, rapor Telegram'a gider; yeni
  bolumu yazan `series/replenish.py` bu veriyi HIC gormez. `gunluk_beyin` 15 Eyl'de
  donduruldu: rapor uretiyor, kimse kullanmiyordu. Ders: ciktiyi RAPOR degil,
  planlayicinin GIRDISI yap.
- Upload-Post per-post metrik veriyor, Instagram dahil (olculdu 24 Eyl, still-home
  Tokyo reel: `GET /api/uploadposts/post-analytics/<request_id>` ->
  `platforms.instagram.post_metrics = {views:140, reach:108, likes:5, comments:0,
  saves:2, shares:2}`). `GET /api/uploadposts/post-analytics?platform_post_id=..&
  platform=..&user=..` metrik DONMUYOR ama `request_id` donduruyor (iki adimli yol).
  Hiz siniri: 100 istek / 5 dk. Toplu: `GET /api/uploadposts/post-analytics/cached`.
- Seri kayit defteri `<kanal>/<slug>/published.json` platform post id'lerini tutuyor
  (`results: {youtube, instagram, tiktok}`), request_id TUTMUYOR.
- Yorum okuma: `GET /api/uploadposts/comments?platform=&user=&post_id=` Instagram ve
  YouTube'da CALISIYOR (olculdu), TikTok `400 tiktok_reconnect_required` donuyor
  (Ihsan hesabi yeniden baglayana kadar).
- Gec atesleme dersi (aimagine, olculdu): Burj 21. saatte 1 izlenme, 44. saatte 1.568.
  44 saat dolmadan bir video "tutmadi" sayilmaz.
- Yeni ariza (24 Eyl): IG caption artik tam gidiyor (a3576bc) ve still-home Kahire
  reel'i 14 etiketle cikti. Instagram tavani 5 (caption + yorum birlikte).

## Rocks (bagimlilik sirasiyla)

### Rock 1: Instagram etiket tavani

- `core/uploader.py` instagram dalinda, IG'ye giden caption (`title` ve
  `instagram_title`) en fazla 5 hashtag tasir: ilk 5 benzersiz etiket SIRASIYLA kalir,
  fazlasi metinden silinir, bosalan satir/bosluk toparlanir. Govde metni ve soru aynen
  kalir. YouTube ve TikTok metni DEGISMEZ.
- Etiket = `#` + harf/rakam/alt cizgi dizisi (Unicode harf dahil, `#STILLHOME2512`,
  `#İstanbul`). URL icindeki `#` ve tek basina `#` etiket sayilmaz.
- Done: still-home Kahire caption'i (14 etiket) IG'ye 5 etiketle gider, ilk 5 =
  `#Cairo #MagneticTransit #FutureCity #Giza #SmartInfrastructure`.
- Proof: `python -X utf8 -m pytest tests/test_ig_etiket_tavani.py tests/test_ig_caption_alani.py -q`

### Rock 2: Performans toplayici (`series/performans.py`)

- Girdi: bir seri slug'i. `published.json` her kayit icin platform basina post id.
- Her (part, platform) icin metrik: YouTube `views`, Instagram `views`, TikTok `views`
  (+ likes, comments, shares, saves, reach varsa). Yol: platform_post_id -> request_id
  (onbellege al, bir daha sorma) -> `post-analytics/<request_id>` -> ilgili platformun
  `post_metrics`'i. YouTube icin Upload-Post metrik vermezse `YOUTUBE_API_KEY` ile
  Data API `videos?part=statistics` yedegi.
- Depolama: `<data_dir(slug)>/performans.json` (git'te, kanal klasoru zaten
  persist ediliyor). Part basina: post id'ler, request_id'ler, yayin zamani, her olcum
  anindaki metrikler (`olcumler: [{ts, yas_saat, platform: {views,...}}]`), `donduruldu`.
- Kurallar: yayindan 44 saat gecmeden part "olculmemis" sayilir (metrik yine
  kaydedilir ama puanlamaya girmez). 8 gunden yasli ve en az bir olcumu olan part
  DONDURULUR, bir daha API'ye sorulmaz. Tek koşuda en fazla 60 API cagrisi; 429'da
  dur, elde olani yaz. Hicbir hata koşuyu dusurmez (exit 0, uyari log).
- Puan: her platformda serinin KENDI olculmus partlarinin medyani (en az 5 olculmus
  part yoksa o platform puansiz). `oran = views / medyan`. Part puani = platform
  oranlarinin EN BUYUGU. Etiket: `kazanan` (puan >= 2), `kaybeden` (tum puanli
  platformlarda oran <= 0,5), gerisi `orta`. Puan dosyaya yazilir.
- CLI: `python -m series.performans --series <slug> [--dry]`. `--dry` aga cikmaz,
  mevcut dosyadan puan tablosunu basar.
- Is akisi: `wild-encounter.yml`, `still-home.yml`, `galactic-daily.yml` icinde
  replenish adimindan ONCE, `continue-on-error: true` ile bir adim. galactic'te iki
  serit de (one-variable + flythrough) toplanir, hangisi bugun kosarsa kossun.
- Done: still-home icin kosu, 7 partin performans.json kaydini uretir; 44 saatten
  genc Kahire "olculmemis".
- Proof: `python -X utf8 -m pytest tests/test_performans.py -q` (ag mock'lu)

### Rock 3: Planlayiciya baglamak (`replenish.py`)

- Opt-in: series.json `"performance_feedback": true`. Bayraksiz seride istem BAYT
  BAYT ayni (golden testler yesil kalir).
- Bayrak varsa ve `performans.json`'da en az 6 olculmus part + en az bir kazanan
  ya da kaybeden varsa istem sonuna bir blok eklenir:
  `PERFORMANCE MEMORY (measured on this series' own history, not a universal target)`
  + en fazla 4 kazanan + en fazla 4 kaybeden: part no, title, synopsis, family/topic
  alanlari (planda varsa), platform basina views ve oran. Talimat: yeni partlari
  kazananlarin ORTAK ozelligine (konu turu, olcek, aile) yaklastir, kaybedenlerin
  ortak ozelliginden uzaklas, ayni konuyu/basligi TEKRARLAMA (mevcut benzersizlik
  kurallari aynen gecerli), tek ornekten kural cikarma.
- Sayilar yuvarlanir, blok 1.500 karakteri gecmez.
- Bayrak su 4 seride acilir: wild-encounter, still-home, one-variable, flythrough.
- Done: bayrakli seride istemde blok var, bayraksizda yok; veri yetersizse blok yok.
- Proof: `python -X utf8 -m pytest tests/test_performans_istem.py tests/test_rf_tekplan_golden.py tests/test_gercekcilik_rock2.py -q`

### Rock 4: aimagine sehir istekleri (`AImagine-Fear/tools/sehir_istekleri.py`)

- Kaynak: `AImagine-Fear/yayin.jsonl` son 14 gunun dogrulanmis yayinlari. Post id'ler
  kayittaki `results`'tan cikarilir (sekil degisken, iki kusagi da coz; YouTube
  `post_id`, Instagram/TikTok platform post id ya da request_id -> platform id).
  Upload-Post profil adi `core.config.UPLOAD_USERS["aimagine"]`.
- Her post icin yorumlar: Instagram + YouTube; TikTok `tiktok_reconnect_required`
  donerse sessizce atla. Kanalin kendi yorumlari (username == hesabin kendisi) sayilmaz.
- Sehir cikarimi: tum yorum metinleri TEK Gemini cagrisinda (repo'nun mevcut Gemini
  istemcisi/modeli), cikti JSON: `[{comment_id, city, landmark}]`, sehir Ingilizce
  kanonik ad; sehir yoksa null. Gemini yoksa/hata verirse dosya DEGISMEZ, uyari.
- Sayim: sehir basina BENZERSIZ kullanici sayisi. Zaten rotasi olan sehirler
  (`routes/*.md` basliklarindaki sehir alanlari ya da `tools/sehir_ekle.py` SEHIRLER)
  `var: true` diye isaretlenir ama listede kalir.
- Cikti: `AImagine-Fear/veri/sehir_istekleri.json` = `{guncellendi, kaynak_post_sayisi,
  yorum_sayisi, sehirler: [{sehir, kullanici_sayisi, ornek_yorumlar[<=3], var}]}`,
  kullanici sayisina gore sirali. stdout'a ilk 10.
- Is akisi: `fear-slide.yml` yayindan SONRA, `continue-on-error: true`; persist
  listesine `AImagine-Fear/veri/sehir_istekleri.json` eklenir.
- Kapsam disi: rota dosyasini otomatik yazmak. Rotayi Claude oturumu bu listeden secip
  `sehir_ekle.py` ile yazar (rota kurallari insan+denetim gerektiriyor).
- Done: yerelde gercek anahtarla bir kuru kosu listeyi uretir.
- Proof: `python -X utf8 -m pytest AImagine-Fear/tests/test_sehir_istekleri.py -q`

## Ortak kisitlar

- Hicbir yeni adim yayini durduramaz: toplayici/sayac hatasi -> uyari + exit 0.
- Yeni bagimlilik yok. Testlerde ag yok.
- `tests/` icinde HEAD'de zaten kirik 5 test var (test_experiment_runner x4,
  test_rock5_containment x1); yeni kirik olmamali.
- Kapsam disi: YouTube Analytics API (retention), baslik A/B, yorum cevaplama.
