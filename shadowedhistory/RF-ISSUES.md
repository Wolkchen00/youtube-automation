# RF-ISSUES , flashpoints (bu kosuda ele alinmayanlar)

Tarih: 10 Eylul 2026 (Los Angeles)

## Bu kosuda OLDURULEN iki rock (gerekce burada)

### [OLDU] Sureyi 2 x 8 sn'ye (15 sn teslim) geri al

**Neden onerilmisti:** 29 yayinlanmis bolumun yt-dlp olcumu, teslim suresine gore:

| Teslim suresi | Bolum | Medyan izlenme |
|---|---|---|
| 15 sn (2 x 8) | 17 | 33 |
| 9-10 sn (tek cekim) | 5 | 23 |
| 7 sn (tek cekim) | 4 | 19,5 |
| 19 sn (2 x 10) | 3 | 19 |

**Neden olduruldu:** 2 x 8 -> 2 x 10 bir kayma degil, **Ihsan'in 2026-09-01 tarihli
v1.8 karari** (`shadowedhistory/KONSEPT.md:29-42`). Gerekcesi izleyici geri bildirimi:
*"konusmaci cok hizli konusuyor ve cumlesini bitiremeden video bitiyor."* v1.8 ayni
anda sunlari degistirdi: kelime butcesi 26-38 -> 26-36, register "hizli" -> "olculu
belgesel", "son cumle yarim birakilir" kurali IPTAL, miksor hizlandirma tavani
1.15x -> 1.05x. Sure artisi bu paketin tasiyici parcasi.

Geri almak:
1. Ihsan'in dokuz gun once acikca sikayet edilen kusuru geri getirir (26-36 kelime
   ~2 kelime/sn ile 13-18 sn konusma ister; 15 sn teslimde konusma penceresi ~14,3 sn
   kalir ve v1.8(f) uyarinca miksor sigmayan sureyi son kareyi klonlayarak eklerdi ,
   yani donmus son kare).
2. Sadece `shot_seconds` degil, doktrin metnini, kelime butcesini, register'i,
   `series.json` hash pinini ve iki mevcut testi de degistirmeyi gerektirir.
3. Kanit tarafi zayif: 19 sn kovasi n=3 ve hepsi 2-6 gunluk. Karsi kova (n=17)
   Ihsan'in kalite gerekcesiyle REDDETTIGI eski bicimin ta kendisi , yani o medyan
   "daha iyi bicim" degil, "terk edilmis bicim".

**Ne zaman tekrar bakilmali:** v1.8 bicimi ~10 bolume ulastiginda (su an 3). O zaman
karsilastirma n=10 vs n=17 olur ve tempo degiskeni sabittir. Olcum komutu bu kosuda
kullanilan yontemin aynisi: `published.json` -> yt-dlp -> izlenme + sure.

### [OLDU] fact_captions'i ac

**Neden onerilmisti:** kardes iki seri acik (`drowned-history`, `footnotes`) ve motorun
kendi belgesi (`series/bible.py:366-372`) *"faceless tarih Shorts'larinda izlenme/
paylasimi en cok artiran kaldirac"* diyor. 35 planin hicbirinde `fact` alani yok.

**Neden olduruldu , iki bagimsiz sebep:**

1. **Doktrin bilerek kaldirmis.** `KONSEPT.md:3-4` (v1.1): *"caption ve fact_captions
   kaldirildi (motor gercegi)"*. Yani bu bir unutma degil, verilmis bir karar.

2. **Iki cekimlik seride sozlesme kendi kendisiyle celisiyor.** `series/replenish.py:697-701`
   prompt'u modele *"NO 'fact' on the final resolve shot"* diyor; `replenish.py:1287`
   ise *"en az 2 cekimde 'fact' olmali"* diye REDDEDIYOR. flashpoints'te cekim sayisi 2'dir:
   kurala uyan model en fazla 1 fakt yazabilir ve partisi reddedilir.

   DUZELTME (Codex turu 2, hakli): ilk yazdigim "matematiksel olarak imkansiz, her
   parti RED" ifadesi FAZLA GUCLUYDU. Son-cekim yasagi yalnizca PROMPT'ta, kodda
   zorlanmiyor; iki cekime birden fakt yazan bir model dogrulamayi GECER. Yani sonuc
   imkansizlik degil **belirsizlik**: ayni konfigurasyon bazen gecer bazen kalir ve
   kalma sebebi log'da "modelin talimata uymasi" olarak gorunur. Sessiz, aralikli
   kuyruk kilitlenmesi , daha da kotu bir hata sinifi. Oldurme karari degismiyor;
   zaten doktrin gerekcesi tek basina yeterli.

**Ne gerekir:** `series/replenish.py` icinde ya esigi cekim sayisina bagli yapmak
(`min(2, shots - 1)`) ya da 2 cekimli serilerde son-cekim yasagini kaldirmak. Ortak
motor isi, bes oturumun ortasinda yapilmaz. Ayri bir rock.

---

## Ertelendi

- **[YUKSEK , IHSAN KARARI GEREKIYOR] Kanal doktrinin emrettigi onay modunda degil.**
  `KONSEPT.md:225` (v1.7 uygulama blogu) `publish_mode: approval` diyor ve `:165`
  *"YouTube gunde 1 (kurasyonlu, approval modu)"* diyor. `series.json` ise
  `"publish_mode": "auto"`. Doktrinin kendi risk maddesi (`:75`): *"tam-otomatik
  uret-yukle en riskli arketip; onay modu + gercek varyasyon + ..."*. Yani su anda
  kanal, doktrinin acikca "en riskli" dedigi modda calisiyor ve `:124`'te "ikinci
  kalkan" denen Telegram onayi devre disi. Bu bir hata mi yoksa sonradan alinmis
  bir karar mi, kod okumasindan anlasilmiyor , bu yuzden bu kosuda DEGISTIRILMEDI.
  Ihsan'in kararina birakildi. (Codex turu 2 bulgusu.)

- **[YUKSEK] Kati plan dogrulamasi kapali , cekim sayisi ve suresi hic denetlenmiyor.**
  `series/replenish.py:213-217` `strict_plan_validation_enabled()` su bes anahtardan
  birini ariyor: `chain_breaks`, `hook_shot`, `shot_plan`, `title_patterns`,
  `format_version`. flashpoints `auto_replenish`'inde HICBIRI yok, yani `:244`'teki
  *"cekim sayisi tam N olmali"* ve sure denetimi HIC calismiyor. Model 3-6 cekimlik
  bir plan uretse gecerdi. Rock 2'nin `min_shots: 2` esigi ALT siniri korur, UST
  siniri korumaz.

  **Neden bu kosuda yapilmadi:** duzeltme tek satir (`auto_replenish` icine
  `"hook_shot": 1`; 35 planin 35'i zaten `hook_shot: 1` ve 2 cekim tasiyor). Ama bu
  anahtar URETIM ONCESI fail-closed bir dogrulayici aciyor ve kuyruk su an 5 plan
  derinliginde. Bu depoda bunun emsali var: bir dogrulama kilidi konu havuzu
  cesitliligi bitince ikmali cozulemez hale getirmis ve kosu yine yesil donmustu.
  Dogru sira: once son N uretilmis plani bu dogrulayicidan RAPOR MODUNDA gecirip
  kacinin kalacagini olcmek, sonra acmak. Olcum yapilmadan acilmaz.
  (Codex turu 2 bulgusu, [FIX] demisti; olcum on kosuluyla ertelendi.)

- **[ORTA] `qc.revalidate_cache` kapali , dogrulanmamis cache "dogrulanmis" diye
  loglaniyor.** `series/produce.py:1569-1578`: cekim dosyasi varsa ve bos degilse
  `cache_ok = True` (kosulsuz), ve log satiri *"Cekim n dogrulanmis cache'de"* yaziyor
  , halbuki `revalidate_cache` kapaliyken hicbir sey dogrulanmiyor. Motor cozumu
  hazir tasiyor (`_revalidate_cached_shot`, `produce.py:407`: medya gecerliligi +
  ICERIK HASH'iyle eslesen bir `qc_pass` kaydi arar, bulamazsa dosyayi
  `_stale_<hash>` diye ayirir).

  QC REDDI bu deligi normalde kullanmaz , reddedilen klip `_qcfail<n>` olarak yeniden
  adlandiriliyor (`series/critic.py:1845-1848`), yani dosya yolu bosaliyor ve yeniden
  uretiliyor. DUZELTME (Codex turu 3, hakli): bu yalnizca yeniden adlandirma
  BASARILIYSA gecerli , `:1847-1849` hatayi yakalayip devam ediyor, yani basarisiz bir
  rename reddedilen klibi `shot_NN.mp4` olarak birakabilir. Artik risk olarak duruyor.

  YARIM/BOZUK INDIRME kolu ise bu kosuda `qc.harden_downloads: true` ile KAPATILDI
  (Rock 2'ye eklendi): atomik rename sayesinde yarim medya final yola hic ulasmiyor.
  Geriye kalan `revalidate_cache` acigi yalnizca "gecmiste QC gecmis ama kaydi
  eslesmeyen" klipler icin gecerli.

  NOT (Codex turu 3): gunluk kosu `ubuntu-latest` uzerinde taze is alaninda calisiyor
  (`.github/workflows/flashpoints.yml`, cekim cache'i geri yuklenmiyor), yani cross-run
  cache senaryosu CI'da zaten olusmuyor; risk yerel/elle kosulara ozgu. Ayrica 17
  gecmis `qc_pass` sayisi BUGUNKU yeniden kullanilabilir cache'i olcmez , acilacaksa
  olcum gercekten saklanan klipler uzerinden yapilmali.

  **Neden bu kosuda yapilmadi:** Rock 2 yeniden denemeleri ~%31'e cikariyor, yani bu
  yol cok daha sik islenecek , acmak icin gecerli bir gerekce. Ama `qc_pass_exists`
  ICERIK HASH'i esitligi ariyor ve bu kanalin log'unda 28 bolume karsilik yalnizca
  17 `qc_pass` kaydi var. Kaydi olmayan saglam bir cache'i de ayirip yeniden uretir,
  yani her yanlis karantina para yakar. Once "bugunku cache'in kaci `qc_pass_exists`'i
  gecer" olculmeli. (Codex turu 2 bulgusu.)

- **[DUSUK] Calisma zamani cekim dususunun `next_part`'i ilerletmedigi TESTLE degil
  kod okumasiyla dogrulandi.** `series_runner.py:791-796` ve flashpoints'te
  `state_machine_version` alaninin yoklugu. Tam bir `run_next` entegrasyon testi
  motoru mocklamayi gerektirir; bu kosunun kapsami disinda. (Codex turu 2 bulgusu.)

- **[YUKSEK] Dusen cekim kredi yakiyor ve artik bolumu de dusurecek.** Rock 2 sonrasi
  bir cekim reddedilirse bolum yayinlanmayacak ve ertesi kosuda bastan denenecek ,
  ama ilk kosuda harcanan kredi geri gelmez (Kie'de idempotency yok). Dogru cozum
  reddedilen cekimi yeni tohum/prompt ile YERINDE yeniden uretip bolumu tamamlamak.
  `series/produce.py` isi, kapsam disi. Gecmis oran: 29 bolumde 9 (~%31).

- **[YUKSEK] Konu tanınırligi hipotezi kanitlanmadi.** Rapor "tanınır konu kazaniyor"
  diyor ve iki ornege dayaniyor. 29 bolumluk tam veride hipotez zayif: Gladiators
  (0 izlenme), "Cleopatra Was Closer To The Moon Landing" (0), "Cleopatra Ruled Without
  Translators" (6) , ucu de son derece tanınır ve dip yaptilar. Buna karsilik "Nintendo
  Made Playing Cards" (795) ve "Romans Used Urine For Laundry" (105) tanınır ama
  BEKLENMEDIK. Ayirici degisken tanınırlik degil, muhtemelen beklenmediklik.
  Yapilacak is: 29 bolumu baslik kalibina gore siniflandirip (kalip: "The Real Reason X",
  "X: Fact Or Ancient Propaganda?", "How X Y'd In YYYY!", "Isim: Sifat") izlenmeye
  karsi cizmek. Veri zaten elde.

- **[ORTA] "Fact Or Ancient Propaganda?" kalibi tukenmis olabilir.** Dort ornek:
  Gladiators 0, Colosseum 143, Great Wall 25, Great Fire Of London 23 , medyan 24.

- **[ORTA] 15 sn teslim garanti degil.** micro_trim best-effort ve sure bandi ihlali
  yayindan once yalnizca UYARI uretiyor. Fail-closed bir "islenmis sure" kapisi
  `core/` veya `series/` degisikligi ister. (Codex turu 1 bulgusu.)

- **[ORTA] auto_replenish.shots: 2 yalnizca prompt talimati.** flashpoints'te kati
  plan dogrulamasini aciklayan anahtar yok, yani model 3-6 cekimlik bir plan
  uretirse gecebilir. Rock 2'nin `min_shots: 2` esigi ALT siniri korur, UST siniri
  korumaz. (Codex turu 1 bulgusu; dogrulanmasi gerek.)

- **[DUSUK] 11. bolum hic yayinlanmamis.** `published.json` part 11'i icermiyor
  (1-10 ve 12-30 var). `plans/part11.json` mevcut. Sebep arastirilmadi.

- **[DUSUK] Instagram ve TikTok hic yayinlanmamis.** `series.json` uc platform
  listeliyor; 29 kaydin tamaminda `instagram: null`, `tiktok: null`.

- **[ORTA] Kredi butcesi dort kanalda ortak.** `core/credit_gate.py:267-279`: kanallar
  ayni Kie cuzdanini ve aylik defteri paylasiyor. Rock 2'nin urettigi ek yeniden
  denemeler baska bir kanalin kredi ayirmasini engelleyebilir. Izlenmeli.
  (Codex turu 3 bulgusu.)

## Reddedildi (rapordaki madde, yapilmayacak)

- **"Baslik kartinin her videoda basildigini dogrula."** Dogrulandi: 35 planin
  35'inde de `title_card.title` dolu ve `bible.json` `title_card: true`
  (`series/bible.py:360-363` bool degeri `{"enabled": True}`'ya ceviriyor).
  Yapilacak is yok.

- **"Sifir kesmeli video birakma, tavan 4 saniye."** Kok neden kesme kurali degil,
  dusen cekim (Rock 2). Cekim dusmedigi surece her bolum zaten iki cekim / bir kesme
  tasiyor.

- **"Sureyi 12-18 saniyeye cek."** Yukaridaki [OLDU] maddesine bakiniz.
