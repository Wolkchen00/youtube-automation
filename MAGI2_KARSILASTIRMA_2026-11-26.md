# MAGI-2 karsilastirmasi, canli seritler (26 Kasim 2026)

Amac: Ihsan "butun sistemleri MAGI-2'ye cevirelim" dedi. Once her canli seritte ayni girdiyle TEK MAGI-2 uretimi
yapildi, mevcut yayinlanmis klip ile yan yana kondu. Yalniz kazanan seride gecis onerilir. Hicbir bible, workflow,
profil ya da yayin degistirilmedi. Mini dizi (Shorts_Dizi_Fabrikasi) baska oturumda, buna dokunulmadi.

## Nasil yapildi

- Yardimci: `core/kie_api.py` icine `generate_magi2_video()` eklendi (mevcut createTask/poll kodunu kullanir; ilk kare
  varsa `magi-2/image-to-video`, referans gorsel varsa `magi-2/reference-to-video`, yoksa `magi-2/text-to-video`).
  Hicbir cagiran ona baglanmadi.
- Girdi: her seridin son yayinlanan bolumunun plani origin/main'den alindi, prompt `series.shots.resolve_shot` ile
  motorun gonderdigi haliyle yeniden kuruldu. Ayni sure, 9:16, ses ayari ayni (dark-fact serileri sessiz uretir, sonra muzik eklenir).
- Orijinal klipler: series_log.csv'deki ham Kie adresleri (hepsi hala indirilebiliyordu); fear-slide icin hazir/ kuyrugundaki master.
- Olcum: ffprobe, ebur128, sahne kesmesi (select gt(scene,0.25)), 1 fps kontakt sayfasi, kesme anlarinda tek kare. Kareler gozle bakildi.
- Dosyalar: `output/magi2_karsilastirma/<serit>/` (orijinal, magi2.mp4, yan_yana.mp4 [sol orijinal, sag MAGI-2,
  ses MAGI-2'den, yoksa orijinalden], kontakt_*.jpg, magi2_istek_prompt.txt), `kosu_sonuc.json`, `kosu.log`.

## Sonuc tablosu

| Serit | Simdiki model | Kredi simdi | Kredi MAGI-2 | Fark | Karar | Somut sebep |
|---|---|---|---|---|---|---|
| one-variable (galactic) | Omni, 8 sn, 1080p | 105 | 140,8 | +34% | **DAHA KOTU** | Fotogercek yorunge goruntusu yerine harita grafigi: ulke sinirlari cizili, bulut ortusu yok, olcek icin insan yapisi (istasyon) yok. Omni istenen sahneyi verdi. |
| flythrough (galactic) | Seedance 2 fast, 15 sn, 720p | 372 | 264 | -29% | **DAHA KOTU** | 4,08 sn'de sert kesme (bant "kesme yok" diyor), ilk 4 sn kamera neredeyse duruyor (bant "asla durmaz"), Carina Bulutsusu bolumune uydurma bantli gaz devi koydu (bant "gercek cisim"). 1080p ve ucuz ama format kurallarinin ucunu bozdu. |
| dark-fact-a (shadowedhistory) | Omni, 10 sn, sessiz | 126 | 176 | +40% | **AYNI / KARISIK** | Daha dramatik isik (mesale, alacakaranlik), istenen yanal kayma var. Ama Roma betonu bolumune yelkenli kalyon (cag hatasi) ve sonradan rihtim, at, insanlar ekledi; dijital render hissi. Omni daha sade ama hatasiz. %40 fazla odemeye degmez. |
| dark-fact-b (shadowedhistory) | Omni, 4 x 4 sn ayri uretim, sessiz | 252 (4 is) | 281,6 (1 is) | +12% | **DAHA IYI (kosullu)** | Tek uretimde 4 cekim, kesmeler 4,6 / 8,52 / 12,6 sn'de (plan 4/8/12). Sise ayni sise kaliyor (mantar, pas lekeleri 1-2-4. cekimde ayni); Omni'de her cekim ayri uretildigi icin sise degisiyor ve 4. cekimde istenmeyen ek kesme var (13,02 sn). Eksi: daha keskin ve doygun, "grenli arsiv 16mm" hissi zayif; tanecik/renk sondurme filtresi ya da prompt ayari gerekir. |
| fear-slide (aimagine) | Seedance 2, 15 sn, 720p | 615 | 264 | **-57%** | **SIMDILIK DAHA KOTU, tekrar denenmeli** | 1080p, keskin, piramit ve kum firtinasi vurusu iyi, ilk kareden basliyor. Ama 2,0 sn'de sicrama: yurume yolundan kaydirak agzina oturma, kesme gibi (bant "tek kesintisiz cekim, isinlanma yok"). Gogus kayisi tokasi kadrajda (prompt yasakliyor). Not: yayinlanan orijinal 1 Ekim'deki eski ilk kare ve promptla uretilmisti; MAGI-2 bugunku onayli ilk kare + 15 Kasim promptuyla uretildi, yani birebir ayni girdi degil. |

Ses: dark-fact iki seritte bilerek kapali. Digerlerinde MAGI-2 ses akisi var (one-variable -13,6, flythrough -11,2,
fear-slide -12,9 LUFS); icerigi (muzik/konusma var mi) dinlenmedi, yalniz varligi olculdu.
Cozunurluk: MAGI-2 hep 1080p (fear-slide ilk kare oranini izledi: 768x1376 kare -> 1076x1928 cikti). Kare hizi 25 fps (bizimkiler 24).
Sure: her MAGI-2 isi ~16-19 dk surdu (5'i paralel).

## Butce

- Bakiye once 10.294,69, sonra 8.341,09 (fark 1.953,6).
- Bu isin harcadigi (Kie creditsConsumed, 5 is): 140,8 + 176 + 281,6 + 264 + 264 = **1.126,4 kredi** (tavan 1.200). Basarisiz is yok.
- Aradaki 827,2 kredi ayni hesaptaki BASKA bir tuketiciden (ayni 19 dk icinde; muhtemelen paralel mini dizi oturumu ya da CI).

## Oneri (gecis listesi)

1. **dark-fact-b**: MAGI-2'ye gecmeye aday. Once 1-2 bolum daha deneme + arsiv tanecigi (ffmpeg noise/eq) ile. Kazanc: 4 is yerine 1 is, ayni nesne, planli kesmeler; maliyet +%12.
2. **fear-slide**: maliyet acisindan en guclu aday (-%57, 1080p) ama tek ornek tek-cekim kuralini bozdu. 2 ornek daha uretmeden gecme. (Tavan doldugu icin bu kosuda yapilmadi.)
3. **one-variable, flythrough, dark-fact-a**: mevcut modelde kal.

## Kazanan seritler icin gereken baglanti degisiklikleri (yapilmadi)

- dark-fact-b: `shadowedhistory/dark-fact-b/bible.json` -> `series.engine` icin yeni deger (or. `"magi2"`). Motor bunu tanimiyor:
  `series/produce.py` cekim dagitimina (`if shot_engine == "omni":` blogu, ~1877) bir magi2 dali, `series/replenish.py`
  `valid_durations()` (~210) icin MAGI-2 4-30 sn, `series/bible.py` `engine` (~191) dokumani, `core/cost_tracker.py` model haritasina
  `magi-2/*`. Planlayicinin 4 cekimi tek klip olarak (zaman damgali "Shot N (from a s to b s)") istemesi gerekir.
- fear-slide: `AImagine-Fear/tools/gunluk.py` `MODEL` (satir 45) ve `AImagine-Fear/tools/kie_uret.py` model dalina `magi-2/image-to-video`
  govdesi (first_frame_url, duration int, resolution "1080p", generate_audio; prompt siniri 15.000). Bugunku PROMPT.txt 15.572
  karakter, siniri asiyor (bu testte INDEPENDENCE NOTE ve 3 dusuk onemli NO satiri cikarildi, 14.993). Profil kanaryasi
  (`profil_onay.json`, `profil.py`) yeni anahtarla bir kez kosup kendini damgalar; olcum kapisi 1080x1920 beklerse 1076x1928 cikis takilabilir.

## 27 Kasim 2026: gecis kararlari ve MAGI tarif dili

Ihsan karari: "magi 2 anlayacagi sekilde promtu yazalim, fiyattan kar ettigimiz her kanali transfer edelim,
shadowedhistory'yi askiya alalim, galactic ve aimagine MAGI 2'ye uyacak sekilde degissin; kalite bozulursa duzeltecegiz".

- shadowedhistory: ASKIDA. dark-fact.yml cron yorumda + GitHub'da disabled_manually (id 372517391), iki seri paused, ikmal kapali (9e248bb).
- galactic: iki serit MAGI-2 (59d9454). Kanal toplami 477 -> 404,8 kredi / 2 gun.
- aimagine: ayri calisma (fear-slide MAGI-2 image-to-video, 615 -> 264).

**Kesmenin sebebi bulundu:** 26 Kas'taki kesmeler tam promptun zaman araliklarinda (flythrough "Seconds 4-6" -> 4,08 sn,
fear-slide "[2.0-4.0]" -> 2,0 sn). Sand AI MAGI-2-preview prompt_enhancement (t2v.md, i2v.md): kesme sayisi olay sayisini
izler; tek plan = tek ana olay + tek bagli ortam + tek basit kamera davranisi; ilk kare mutlak taban; olumlu dil.
Kural kodda: `series/replenish.py` MAGI2_PROMPT_RULE (planlayiciya) + `magi2_time_segments` kapisi (zaman araligi
yazan plan kredi harcanmadan durur), test `tests/test_magi2_motor.py`.

**Yeni tarifle deneme (yayin yok, 404,8 kredi):** `output/magi2_gecis_2026-11-27/`
| Plan | Sonuc |
|---|---|
| one-variable p118 (Zeeland, 8 sn, 140,8) | IYI: fotogercek ISS bakisi, gercek bulut ve golgeler, harita/sinir yok, kamera kilitli, en yuksek sahne skoru 0,016 (kesme yok), sel tek yonde ilerliyor. |
| flythrough p23 (Vesta, 15 sn, 264) | IYI (kucuk kusur): kesme yok (en yuksek 0,218, hizli hareket), ilk kareden ileri gidiyor ve hizlaniyor, kaya alani + sonda carpma. Ilk ~3 sn sol ufukta uydurma halkali gezegen yayi; art_style'a "tek gok cismi" cumlesi eklendi. |

