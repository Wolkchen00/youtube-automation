# RF-PLAN - NEXT STOP canon v3 (rev.4, Codex turu 1 + 2 + 3 uygulandi)

**Core Focus (tek cumle):** Next Stop bolumleri, referans kanallardaki gibi her iki-uc saniyede
bir ortamin KENDISI cami opak olarak kapatarak degisen, cam tavanli bir gozlem vagonundan
izlenen, icerideki yolcularin her darbede gorunur sekilde savruldugu ve duragin kendisinin bir
kez trene tepki verdigi, tek cekim gibi duran 56 saniyelik imkansiz tren yolculuklari olmali.

**Non-goals (bu dongude kesinlikle yok):** pipeline kodu degisikligi (series/*.py), motor
degisikligi (Kie Gemini Omni kalir), cekim sayisi / sure / chain mimarisi degisikligi,
title_patterns / families / batch / min_queue / credit_hard_cap degisikligi, CI workflow
degisikligi, yayinlanmis part 1-3'e dokunmak, KONSEPT.md doktrinini tazelemek (ISSUES'a alindi).

**Degisen tek URETIM SOZLESMESI:** bible.json.art_style ve
series.json.auto_replenish.shot_plan + .brief - **uc string.** Bunun disinda degismesi BEKLENEN
dosyalar (Codex turu 2): series.json.total_parts (Rock 4), aimagine/next-stop/plans/*.json
(yeniden uretilir), tools/assert_canon_v3.py + tools/assert_cadence_v3.py +
tools/assert_queue_v3.py + tools/measure_pilot.py (yeni), output/experiments/nextstop-v3-pilot/**
(pilot artifact, commit edilmez), RF-PLAN-NEXTSTOP-V3.md + RF-SAME-PAGE-LOG-NEXTSTOP-V3.md.

---

## 0. Kanit - referans videolar olculdu, tahmin edilmedi

Dort reels indirildi (yt_dlp), kontakt sayfalari cikarildi (ffmpeg fps=N tile=CxR), gecisler
8 fps'te buyutuldu, luma ve kare-farki izi alindi.

| Referans | Sure | Olculen yapi |
|---|---|---|
| Dcnl5-oTxjq "dino" | 30.1s / 1440x2560 | Siradan dunya **3.4s**te bitiyor. Orman-lagun 7-13s, volkanik ova 14.5-20s, col 20-22s, okyanus 22-25s, firtina 25-27.5s, meteor finali 27.5-30s. Ikinci yaride ortam **~2.5s**te bir degisiyor. |
| DcTnR3KgJJe "tak tak" | 56.9s / 1080x1920 | Tarla, dag, bulut, yorunge, uydu, derin uzay, galaksi, **beyaz patlama**, cizgi film dunyasi, ev, odalar. Gec bolumde ~1.5-3s. Kesintisiz fiziksel yolculuk. |
| DcIeBv-ObPf "smooth" | 30.0s / 1920x1080 | Kiyi 0-7.5s, **su cama vuruyor**, yesil su, karanlik dalis, balina karanliktan cikiyor, **magma cami yaliyor** 21.5-26s, gece sehri 27-30s. |
| DcWYwCjCYEu "bikini bottom" | 12.5s / 1080x1920 | NYC 0-3.5s, tunel 3.3s, Bikini Bottom 7-12.5s. Mevcut kadrajimiza en yakin olan. |

### 0.1 Gecislerin gercek suresi: 1-2 KARE

dino.mp4, 8 fps'te buyutulmus 13.0-16.0s araligi:

- 13.000s orman, sauropod bacaklari
- 13.125s **tek kare: soluk gri toz-sis duvari cami tamamen kapatiyor**
- 13.250s zaten volkanik ova

24.4s'te ayni sey: gecen bir yaratigin govdesi bir kare cami kapatiyor, sonraki karede yeni
dunya. **Maske 0.125-0.25 saniye.** Kullanicinin "tak tak" dedigi sey bu.

### 0.2 Ortamin kendisi maskeliyor

Cami kapatan sey tunel duvari degil, **ortamin maddesi**: toz duvari, su serpintisi, buhar, kul,
dalga, yaratigin govdesi. smooth.mp4 20.5-23.0s: magma uzaktan degil **cama yapisik** akiyor,
tum pencereyi dolduruyor, vagon icini kirmiziya boyuyor.

### 0.3 Yolcular gorunur ve tepki veriyor

dino ve tak tak: yolcularin govdeleri, telefonla cekmeleri, yukari bakmalari net gorunuyor.
smooth: magmaya karsi kenar isigiyla siluet okunuyor; kollar, omuzlar, askiya tutunan eller secili.

### 0.4 Cam tavan

dino ve tak tak'ta pencere yan duvardan **kavis yaparak tavana** cikiyor; kavisli kaburgalar
yolcularin ustunden geciyor. Gokyuzu, kuleler, ucan yaratiklar kamera hic oynamadan goruluyor.
Kullanicinin "trenin ust kismi full cam" dedigi sey tam olarak bu.

---

## 1. Kendi pilotumuzun kusuru - v2 nerede kaldi

v2 pilotu (output/experiments/nextstop-v2-pilot/next-stop-part90, 6 cekim, ~756 kredi)
2 fps kontakt sayfalariyla kare kare izlendi. Cekim 1-2 gecti. Cekim 3-6'da olculenler:

| Kusur | Kanit |
|---|---|
| **Olu hava** | Cekim 5'in son ~2 saniyesi ve cekim 6'nin son **~5 saniyesi** neredeyse ayni goruntu. "Cok yavas" sikayeti tam burada. |
| **Kontrast yikanmasi** | Cekim 4'un ucuncu vistasinda gok soluk mavi-gri. |
| **Zincir tekrari** | Cekim 4, cekim 3'un acilis vistasiyla (ayni dokum kulesi) aciliyor. |
| **Maske cesitliligi yok** | Tum maskeler yapisal. Ortam maddesi hic kullanilmamis, cunku v2 canon'u bunu ACIKCA YASAKLIYOR. |

v2 canon'unun sucu isleyen cumlesi:

> "walls of foliage, smoke, spray and embers may lash the glass for texture, but they never change the scene"

Bu cumle kullanicinin istedigi gecisin ta kendisini yasakliyor. v3'un en onemli duzeltmesi bu.

---

## 2. v3'te degisen dort kural

| # | Referans kaniti | v2 canon'u | v3 duzeltmesi |
|---|---|---|---|
| **A** | Cam tavanli gozlem vagonu | "tek dikdortgen YAN pencere", "ustundeki panel ciplak" | Yan cam kavis yaparak **cam tavana** donusuyor; kaburgalar tepede; kamera hafif yukari egik |
| **B** | Maske = ortamin maddesi, 0.125-0.25s | ortam maddesi "sahneyi DEGISTIRMEZ" | **Kadansi belirleyen her sifirlama opak ortam ortmesidir**; bolum basina en fazla bir yapisal ortucu, o da sayilmaz |
| **C** | Yolcular okunur, tepkili | "karanlik, odak disi, yuzu hic secilmeyen" | **Kenar isigi:** govde ve hareket okunur, yuz hicbir mesafede secilmez, kiyafet ve yer bolum boyunca surekli |
| **D** | Ortam ~2.5s'te degisir, maske <0.4s | maske suresi yazilmamis, olu hava yasaklanmamis | **Ortme ~0.25s**; **OLU HAVA YOK**; uzun karanlik istisnasi **yok** |

---

## 3. ROCK 1 - bible.json.art_style = canon v3

Sadece art_style degisir. Diger tum anahtarlar bayt bayt ayni kalir.

**Boyut hedefi: ~5600 karakter** (v2 = 5397, kanitlanmis calisir boyut). Tur 1'de Codex'in
seyrelme uyarisi kabul edildi: 19 madde **15'e** indirildi, kamera kara listesi ve ornek
listeleri sikistirildi, "bir sey trene dikkat eder" maddesi canon'dan cikarilip brief'e tasindi.

Canon v3'un icermesi ZORUNLU 15 maddesi:

1. Raw photorealistic amateur smartphone footage, tek kesintisiz el kamerasi, dikey 9:16, asiri
   hizli trenin icinde. Egri kadraj, el titremesi, rolling-shutter, otofokus arayisi, parlama,
   golge gurultusu, dusuk bitrate, hareket bulanmasi. **Bu kusurlar disariyi asla gizlemez ve
   asla sahne degistirmez.**
2. **THE CARRIAGE IS A GLASS OBSERVATION CAR** - sol duvar tek surekli bir cam yuzey olarak
   basliyor ve **kavis yaparak tavana cikiyor**; ince koyu kaburgalar birkac metrede bir tepeden
   geciyor. Cam karenin en az dortte ucunu kapliyor ve yolcularin ustunden devam ediyor, boylece
   gok ve yuksek olan her sey kamera oynamadan goruluyor. Kamera gidis yonune ~90 derece bakar,
   hafif yukari egiktir. Ileri/geri bakmak, vagonu terk etmek, disini gostermek, kus bakisi,
   ucuncu sahis, zoom, sinematik hareket, stabilizasyon: yasak.
3. **PASSENGERS RIDE INSIDE, AND YOU SEE THEM REACT** - kamerayla cam arasinda, alt ve sag
   kenarda birkac siradan yolcu, camdan daha yakin. Disaridaki isik onlari **yalnizca kenardan**
   aydinlatir: sadece kenar isigiyla cizilen siluet ve govde hareketi okunur, **yuzler ve ic
   yuzeyler az pozlanmis kalir. Yuz hatlari ve kimlik hicbir mesafede secilmez.** Yolcularin
   yeri ve kiyafeti bolum boyunca **sureklidir** (tek cekim yanilsamasi). Karenin en fazla alt
   ucte birini kaplarlar. **Camin otesinde yalniz dunya vardir:** hicbir insan, govde ya da
   insan yansimasi camin ote tarafinda ya da camda gorunmez.
4. **THE PASSENGERS ARE THE SEISMOGRAPH** - her sarsinti govdelerinden okunur; sert darbelerde
   yana savrulur, direge yapisir, egilir, geri cekilir, nefesi kesilir ya da kisa ciglik atar,
   biri telefonu kaldirip ceker; darbeler arasinda yorgun banliyo durgunlugu.
5. **SPEED** - tren asla durmaz, yavaslamaz, varmaz; surekli yuksek frekansli titresim; on
   metreden yakin her sey kareyi saniyenin beste birinden kisa surede gecer; orta mesafe bir
   saniyenin altinda; sadece ufuk suzulur.
6. **THE VIEW CHANGES EVERY TWO OR THREE SECONDS** - yolculuk cekimin ICINDE, kurgu ile degil
   ortme olaylariyla kesilir. Cam acildiginda ayni duragin **baska bir kesiti** gorunur.
7. **THE WORLD ITSELF DOES THE COVERING** - tercih edilen ortucu duragin **kendi maddesidir**:
   toz duvari, serpinti, buhar, kul perdesi, dalga, kar, suru, bulut ya da bir metre otede gecen
   devasa bir govde. Cama carpar, tamamen orter, gider. **Kadansi belirleyen her sifirlama ortam
   maddesiyle olur. Bir bolumde en fazla BIR yapisal ortucu (tunel agzi, kopru ayagi, gecen tren)
   kullanilabilir ve o da kadansa sayilmayan bir ekstradir.**
8. **THE COVER IS BRIEF AND TOTAL** - cam **saniyenin sekizde biri ile dortte biri** kadar tam kapali
   kalir, asla tam bir saniye degil. Tren tunelde, duvarin arkasinda ya da karanlikta **beklemez**. **Sifirlama
   yalnizca disarinin TAMAMEN opak oldugu, hicbir landmark, ufuk ya da eski vista izinin
   kalmadigi, **0.125-0.25 saniyelik** bir anda olabilir; yari saydam ya da kismi ortme asla
    sifirlama izni vermez.**
9. **EVERY COVER IS AN IMPACT** - ortme ile fiziksel darbe gelir: vagon sarsilir, kamera
   silkelenir, direkler takirdar, cam gumburder, yolcular savrulur ve bagirir.
10. **NO DEAD AIR INSIDE A VISTA** - iki ortme arasinda **her zaman** bir sey pencerenin on
    kenarindan girer, cam boyunca buyur ve arka kenardan siddetli paralaksla cikar; ya da buyuk
    bir olay patlar. **Yaklasan ortucunun kendisi bu sarti karsilar: uzakta belirir, camda
    buyur ve arka kenardan CIKMAZ, kareyi tamamen doldurarak ortmeye donusur.** Sabit genis
    plan yok, oylece duran manzara yok.
11. Sahne yalniz cam tamamen kapaliyken sifirlanir. Disarida hicbir sey donusmez, erimez,
    isinlanmaz. Ortme ayni rotanin yalniz kisa bir araligini gizler.
12. **SEAM RULE** - ilk cekim disindaki her cekim onceki vistanin ICINDE, sarsinti ortasinda
    acilir ve ilk tam ortmesi ilk bir bucuk saniye icinde gelir. **Cekim onekindeki saatler
    baglayicidir; govde metni onlari gecersiz kilamaz.** Her cekimin **son saniyesi** cami temiz
    ve okunur bir karede birakir (sonraki cekim o kareden zincirlenir).
13. **TRANSIT PHYSICS** - rota fiziksel olarak gercektir, yonu vagonda hissedilir. Cekimin kendi
    metni yonu soyler; baska bir yolculuk turu icat edilmez.
14. **CONTRAST CLIMBS, IT NEVER WASHES OUT** - esikten sonra gok **manzaranin en karanlik
    bolgesidir**, dis isik asagidan ya da landmark'lardan gelir, vagon ici ondan da karanliktir.
    Her cekim oncekinden daha karanlik tepeli ve daha sicak isiklidir. Soluk kapali hava, beyaz
    pus, duz gun isigi, dusuk kontrast: esikten sonra yasak.
15. **NO TEXT ANYWHERE**; ses yalniz diegetic (hum, gumburtu, takirdayan direkler, titresen cam,
    yolcularin nefesi ve kisa cigliklari), muzik yok; kan, yaralanma, gercek dini figur, tescilli
    mulk yok.

**Done looks like:** art_style gecerli JSON string, **5300-6000 karakter**, 15 maddenin hepsi
metinde, bible.json'un diger anahtarlari degismemis, **em-dash yok** (formatter hook em-dash'i
bozuyor - yalniz ASCII noktalama).

**PROOF:** `python -X utf8 tools/assert_canon_v3.py`
(JSON parse + zorunlu ifade listesi + diger anahtarlarin SHA karsilastirmasi + em-dash taramasi
+ karakter araligi; hepsi gecerse `CANON V3 OK`)

> **Not (Codex turu 1):** Rock 1 ve Rock 2 proof'lari yalnizca **yapilandirma butunlugu**
> kontrolleridir; anlamsal boslukları (kadans, yuz, opaklik) yakalayamazlar. **Yayin kapisi
> Rock 3'tur.**

---

## 4. ROCK 2 - shot_plan + brief = kadans v3

### 4.1 Zamanlama sozlesmesi v3

micro_trim 0.45 -> her ham cekimin kullanilabilir araligi **0.45-9.55s**. Kritik hicbir olay
ilk 0.5 ve son 0.6 saniyeye yazilmaz.

| Cekim | Ortme saatleri | Vista uzunluklari | Not |
|---|---|---|---|
| 1 HOOK | ~2.5, ~5.0, ~7.5 | 2.5 / 2.5 / 2.5 / 2.0 | **Siradan dunya en fazla 2.5 saniye.** Cinlama ~1.2s. |
| 2 THRESHOLD | ~1.0, ~4.0, ~7.0 | 0.55 / 3.0 / 3.0 / 2.55 | ~1.0 dikis ortmesi; siradan dunya temelli biter. |
| 3 SCALE | ~1.0, ~4.0, ~7.0 | ayni | |
| 4 FLYTHROUGH | ~1.0, ~4.0, ~7.0 | ayni | "Bir sey trene dikkat eder" beati burada ya da 5'te. |
| 5 DEEPEST | ~1.0, ~4.0, ~7.0 | ayni | Bolumun en sert darbesi ~1.0'da. |
| 6 HEART | ~1.0, **~3.6**, ~6.8 | 0.55 / 2.6 / 3.2 / 2.75 | Varis anonsu ~8.0; "Next stop-" 9.0'dan hemen sonra kesilir. |

Toplam **18 ortme**. Zincirli bes cekimin acilis dilimi onceki vistanin DEVAMIDIR, yeni vista
degildir (Codex turu 2 duzeltmesi), dolayisiyla gercek sayi **19 ayri vista**: 56.2 / 19 =
ortalama **2.96 saniye**, **en buyuk sifirlama-arasi aralik 3.2 saniye**. Referans olcumu
~2.5-3.5 saniye bandinda.

**Cekim 6'nin ortme saatleri neden ~1.0 / ~3.6 / ~6.8:** `bible.json` hook_teaser
`offset_in_shot: 4.5`, `duration: 1.4` ve `produce.py:1727` kesiti **birlestirilmis bolumdeki**
cekim 6 offset'inden aliyor; micro_trim 0.45 ile bu **ham cekimde ~4.95-6.35s** araligina denk
duser. Codex once ~5.5 onerdi; oraya ortme koymak **kancanin ortasina karartma** koyardi, bu
yuzden ucuncu ortme ~6.8'e alindi. Ilk taslakta ikinci ortme ~3.0'daydi ve 3.0-6.8 arasi
**3.8 saniyelik** bir bosluk biraliyordu; Codex turu 2 bunun kendi koydugum 3.2 saniyelik
yayin kapisini ihlal ettigini gosterdi - hakli. Ikinci ortme **~3.6**'ya alindi: aralıklar
**2.6 ve 3.2 saniye**, teaser penceresi (4.95-6.35) 3.6-6.8 arasindaki temiz bakisin **tam
icinde** kaliyor. Bolumde artik 3.2 saniyeyi asan tek bir vista yok.

### 4.2 Neden 4 degil 3 ortme

Ilk taslak cekim 3-5 icin dort ortme yaziyordu ("fazladan yaz ki dususler emilsin"). Codex bunun
tersine calistigini soyledi ve **hakli**: v2 pilotu zaten uc ortme istiyordu, model bir kismini
birlestirdi. Asil kusur ortme sayisi degil, **aralardaki olu havaydi**. Uc ortmede kalindi ve
kazanilan talimat butcesi su ikiye harcandi:

1. **Olu hava yasagi** (canon 10) - bosluk doldurma isi ortmeye birakilmiyor.
2. **Ikili gorev** - yaklasan ortucunun kendisi o vistanin hareketini sagliyor: uzakta belirir,
   camda buyur, carpar, orter. Tek olay hem hareketi hem gecisi tasiyor.
3. **Ortucuyu kolaylastirmak** - "toz duvari cama carpar", modelin uretmesi "karsi agirlik kafesi
   gumburderek gecer"den cok daha kolay ve referanslarda gercekten kullanilan sey bu.

### 4.3 shot_plan onekleri ve canon yankisi

Alti onek yeniden yazilir. Her onek: rolu, ortme saatlerini, her vistada ne olmasi gerektigini,
darbenin yolcularda nasil okundugunu yazar.

**Yeni (Codex turu 1):** `shots.py` prompt'u `art_style + "\n\n" + shot_prompt` olarak kuruyor,
yani canon **basta**, govde **sonda**; sonra gelen metin canon'u ezebiliyor. Cozum tek cumlelik
bir **canon yankisi**: cam tavan / opak ortam ortmesi / ~ceyrek saniye / asla duran kare.

Turu 2'de Codex hakli olarak gosterdi ki yankiyi **onegin sonuna** koymak yetmez: onek prompt'un
BASINDA, arkasindan ~1500 karakterlik uretilmis govde geliyor ve onu da ezebiliyor. Bu yuzden
kural: **her tam cekim prompt'u ayni yanki cumlesiyle BITMEK zorunda.** Boylece prompt'un hem
basi (onek dogrulayicisi) hem sonu (yanki son eki) sabitlenmis olur ve dort kritik kural uretime
**en yakin** konumda durur. `assert_cadence_v3.py` bu son eki birebir dogrular.

`replenish.py:~244` her cekim prompt'unun kendi onegiyle **BIREBIR** baslamasini dogruluyor;
onek degisince kuyruktaki tum planlar yeniden uretilmeli (ROCK 4).

### 4.4 brief degisiklikleri

- Yolcular: siluet zorunlulugu yerine **kenar isigi + okunur hareket + surekli kiyafet/yer**.
- Kadans: cekim basina ortme saatleri yukaridaki tabloya gore.
- **Yeni:** ortucu kurali (Rock 3 kapisiyla birebir ayni ifade) - **kadansi belirleyen her
  sifirlama ortam maddesiyle olur; bolum basina en fazla bir yapisal ortucu ve o da sayilmaz.**
- **Yeni:** ortme ~0.25s, tunelde bekleme yok, **uzun karanlik istisnasi yok**.
- **Yeni:** olu hava yasagi.
- **Yeni:** cam tavan - her bolumde en az bir vista **yukariyi** kullanmali.
- **Yeni:** **"bir sey trene dikkat eder"** beati (canon'dan tasindi) - yalniz cekim 4 ya da 5'in
  govdesinde, bir kez: donup bakar, yanisira kosar, sahlanir, camin yakinina vurur. Trene asla
  degmez; tren asla yavaslamaz.
- **Yeni:** zincir tekrari yasagi - her cekimin **ilk tam ortmesinden sonra acilan** vistasi,
  onceki cekimin kapanis vistasindan baskin sekil VE derinlik olarak farkli olmali.
- Kontrast: cekim 3-6 govdelerinde karanlik acikca yazilir (pilotta cekim 4 yikandi).

**Done looks like:** shot_plan 6 elemanli, her eleman kendi ortme saatlerini ve canon yankisini
iceriyor; brief yukaridaki maddeleri iceriyor; families, title_style, title_patterns, batch,
min_queue, shots, shot_seconds, hook_shot, chain_breaks, credit_hard_cap **bayt bayt degismemis**;
em-dash yok.

**PROOF:** `python -X utf8 tools/assert_cadence_v3.py`
Script yalniz onek eslesmesine bakmaz (dogrulayici zaten onu yapiyor); **govdeleri de tarar:**
onekle celisen fazladan saat, yapisal-varsayilan dili, bir saniyeyi asan ortme ifadeleri, ve yari
saydam ortucuyle sifirlama ifadeleri.

**Bosluk (Codex turu 3):** script **onek VE yanki son ekini soyup**, aralarinda gercek bolume ozgu
vista icerigi kaldigini dogrulamali. Codex bunu "mevcut asgari govde uzunlugu dogrulamasi"
varsayarak soyledi; **kodu okudum, boyle bir dogrulama YOK** (`replenish.py:243-245` yalnizca
`prompt.startswith(prefix + "

")` bakiyor). Dolayisiyla bosluk Codex'in sandigindan **daha
genis**: onek + yanki'dan ibaret, govdesiz bir prompt bugun tum yapilandirma kontrollerinden
gecer. Bu yuzden soyma-ve-icerik-arama kurali zorunlu.

---

## 5. ROCK 3 - Pilot B (gercek 6 cekim, izole, yayinlanmaz) - YAYIN KAPISI

    python -X utf8 -m series.experiment run next-stop \
      --plan <pilot_plan_v3.json> --experiment-id nextstop-v3-pilot --stage pilot

Yeni bir durak secilir (v2 pilotunun "Hell"i degil; cam tavani ve ortam ortmelerini zorlayan,
yukari bakmayi gerektiren katmanli bir yer).

**Maliyet:** ~756 kredi, yaklasik **$3.80**.

**Gecme olcutleri (Codex turu 1'de tamami yeniden yazildi):**

| # | Olcut | Nasil olculur |
|---|---|---|
| 1 | **Sifirlama-arasi aralik** birlestirilmis bolumun **tamami** boyunca, bas ve son sinir dahil, **3.2 saniyeyi asmiyor** | ep90 benzeri birlesik dosyada ortme zaman damgalari, ardisik farklar |
| 2 | Her kabul edilen ortme karesinde **disarinin tamami gizli**: landmark, ufuk, eski vista izi yok | kare duzeyinde, ortme karesi tek tek okunur |
| 3 | **Kadansi belirleyen her sifirlama ortam maddesi** (toz/su/buhar/kul/kar/govde); en fazla **bir** yapisal ortme, o da sayilmayan ekstra | kontakt sayfasi, kare kare |
| 4 | Donmus vista yok: anlamli sahne icerigi **hicbir yerde durmuyor** (titresim/parcacik pikselleri sayilmaz) | yapisal/optik akis olcumu **+ kontakt sayfasini kendim okurum** |
| 5 | Kavisli yan-tavan cami ve tepe kaburgalar **alti cekimin altisinda** (tam ortme kareleri disinda) secilebiliyor | kontakt sayfasi |
| 6 | **Her kabul edilen ortmede** es zamanli gorunur yolcu savrulmasi/tutunmasi var; tek tek puanlanir | kontakt sayfasi |
| 7 | Yuz hatlari hicbir mesafede secilmiyor; camin otesinde insan yok; camda insan yansimasi yok | kontakt sayfasi |
| 8 | Esikten sonra hicbir vistada soluk gri/mavi gok yok | kontakt sayfasi |
| 9 | Her cekimin **ilk tam ortmesinden sonraki** vistasi, onceki cekimin kapanis vistasindan farkli | son kare vs ortme sonrasi kare |
| 10 | Birlestirilmis bolum **~56s** ve **her zincir dikisi tam kare hizinda** temiz | ffprobe suresi + dikis noktalarinda 24 fps kontakt |

**PROOF:** 1, 4, 10 icin `tools/measure_pilot.py`; **2, 3, 5, 6, 7, 8, 9 icin kontakt
sayfalarini ben kendim kare kare okurum.** Olcut 2 (tam opaklik) turu 2'de script'ten insan
incelemesine tasindi: bir script karenin duz koyu/parlak oldugunu olcebilir ama "ufuk izi kaldi
mi" **anlamsal** bir yargidir, gozle dogrulanir. Pipeline'in "basarili" demesi kanit degildir.

---

## 6. ROCK 4 - Kuyrugu yeni canon ile yeniden uret

Kuyruktaki planlar **eski** oneklerle yazilmis; yeni shot_plan ile replenish'in birebir onek
dogrulamasindan gecemezler.

1. `git pull` (CI part 4'u uretmis olabilir).
2. **Yayin durumunu oku**, ilk yayinlanmamis part numarasini **kesfet** (sabit "part04" yazma).
3. O numaradan yukari dogru **KESINTISIZ blok** halinde plan dosyalarini sil.
   **Kesin tehlike (`replenish.py:359` okundu):** `_adopt_orphans` `total_parts+1`den baslayip
   **ardisik** dosya varken sayaci ilerletir. Bosluk birakan bir silme (ornegin part04 silinip
   part06 birakilmasi) yuruyusu hemen durdurur, part06 **sonsuza kadar yetim** kalir ve ileride
   numara catismasi yaratir. **total_parts'in ustunde hicbir dosya kalmamali.**
4. total_parts'i son yayinlanmis parta esitle.
5. `python -X utf8 -m series.replenish --series next-stop` (Gemini yazar, Kie kredisi harcanmaz).
6. **Dogrula:** her yeni planin her cekim prompt'u kendi onegiyle birebir basliyor; 6 cekim;
   hook_shot 6; baslik title_patterns'e uyuyor; sureler 4/6/8/10.

**TOCTOU (turu 2'de siklastirildi):** CI kosusu gunde bir kez 13:20 UTC ve yayin durumunu
**uzaga** commit'liyor; yalniz yerel `series.json`'i tekrar okumak bu yarisi yakalamaz. Bu
yuzden **silmeden hemen once** ve **push'tan hemen once** ikisi de: `git fetch` + **uzaktaki**
`series.json`'un yayinlanmis part durumunu yerelle karsilastir. Yayinlanmis part degismisse
**dur**: rebase et, ilk yayinlanmamis numarayi yeniden kesfet ve kuyrugu yeniden uret. (Codex "uretici dondurulsun" dedi; workflow'u devre disi
birakmak unutulursa yayini tumden durdurur ve non-goal olan CI degisikligine girer, bu yuzden
iki noktali yeniden okuma tercih edildi.)

**PROOF:**

    python -X utf8 tools/assert_queue_v3.py     # ilk yayinlanmamis plani KESFEDER, dry-run eder

---

## 7. ROCK 5 - Kanitlar ve commit

1. Uc proof scriptini **ben** calistiririm (Codex'in ciktisi kanit degil).
2. Pilot B kontakt sayfalarini **ben** okurum.
3. `git status --short` ile **yalniz bu isin dosyalarini** stage'lerim. **`git add -A` ve
   `git commit -a` yasak** - ayni agacta baska oturumlar calisiyor.
4. Push sonrasi: `git fetch` + **HEAD'in origin/main'in atasi ya da esiti oldugu** dogrulanir
   (`git log origin/main -1` alakasiz bir uzak commit gosterebilir, kanit degildir).
5. Sinir: **2026-09-02 13:20 UTC** (su an 2026-09-01 15:36 UTC, ~21 saat).

---

## 8. ISSUES (bu dongude ele alinmaz)

- **Doktrin dosyasi bayat.** `aimagine/KONSEPT.md` hala eski AImagine konseptini anlatiyor
  (ev/insaat: "IC ISKELET", "REVEAL TUR", "GLASS DOME Home"). `replenish.py` bu metni Gemini
  prompt'una **enjekte etmiyor** - yalniz varlik/pin kapisi calistiriyor ve hash'i plana
  damgaliyor (`_doctrine_gate`, `replenish.py:373`). Uretimi bozmuyor; provenance/dokumantasyon
  borcu. Ayri bir dongude tazelenmeli.
- **`doctrine_sha256` pini yok** (kontrol edildi) - art_style degisimi kapiyi kirmiyor.

---

## 9. Kabul edilen riskler

| Risk | Neden kabul |
|---|---|
| Cam tavan, yayinlanmis part 1-3'un gorunumunden sapiyor | Kullanici acikca istedi; dizi "her bolum yeni durak" formatinda, gorsel kimlik camin bicimi degil pencereden bakma disiplini. |
| Yolcularin gorunur olmasi "AI yuz" riski | Yuz hatlari **hicbir mesafede** secilmiyor; yalniz kenar isigiyla cizilen govde ve hareket okunuyor. |
| Pilot B ~$3.80 | Canon her gelecek bolumu yonetiyor; olcumsuz degistirmek daha pahali. |
