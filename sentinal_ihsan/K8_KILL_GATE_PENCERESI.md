# K8: yayina donus ve kill-gate penceresi

## Pencere acildi: 2026-08-28

| alan | deger |
|---|---|
| seri | unnatural-lab (sentinal.ihsan.daily) |
| stack parmak izi | `9f3416d23977da4a3af72bd74887fa0e78e45fb748115f3efeac4c34fe8ddacd` (sf2) |
| acilis commit'i | `43c693b` (parmak izi son kod dondurmasiyla guncellendi) |
| yayin modu | **auto** (Ihsan karari, 2026-08-28) |
| workflow | `unnatural-lab.yml` ENABLED, gunluk 18:30 UTC |
| ilk bolum | **part22 YAYINLANDI** 2026-08-28T21:06 UTC, youtube+instagram+tiktok |
| pencere | 10 ardisik yayin |
| son tarih | 2026-09-16 |

## Ihsan'in karari ve kayda gecen cekince

Plandaki K8 varsayilani (b) idi: uc yeni QC alani (anomaly_match, violation_reads,
state_carry_ok) hala log-only oldugu icin 10 bolumun tamami insan onayli olacakti.
Ihsan 2026-08-28'de **dogrudan otomatik** yayini secti; sunulan cekince kayittadir:

> ROCK B'nin prompt degisiklikleri (anomaly_descriptor'in hem cekim prompt'larina hem
> hero referansina enjekte edilmesi) GERCEK bir bolumde uctan uca dogrulanmadi.
> pilot-2 uc denemede de bolum uretemedi; ucunde de sebep PLAN kusuruydu, kod degil.

Bu yuzden ilk 2-3 bolum ELDEN izlenmelidir. Bir bolum `qc_hold`'a duser ya da
cekim dusurulurse, once `sentinal_ihsan/unnatural-lab/qc_log.jsonl` okunur.

## Pencere kurallari

1. **Stack DONDU.** `core/stack_fingerprint.py > STACK_SOURCES` listesindeki dosyalar,
   serinin `bible.json`'i ve `series.json`'un cikti blogu pencere boyunca
   DEGISTIRILMEZ. Degisirse parmak izi kayar ve `killgate_report` karar vermeyi
   REDDEDER (`karar_yok`, gerekce "pencerede N farkli stack var").
   Mevcut parmak izini gormek icin:
       py -X utf8 tools/killgate_report.py --series unnatural-lab --stack
2. Kuyruk her ikmalden sonra 0 kredi ile denetlenir:
       py -X utf8 tools/plan_lint.py --series unnatural-lab
3. Olcum sabit yastadir (72 saat). Rapor:
       py -X utf8 tools/killgate_report.py --series unnatural-lab --window 10
   Cikis kodu: 0 karar uretildi, 1 oldur/alarm, 2 karar verilemedi.

## Esikler (degismedi)

* **Oldur:** L/1k medyani < 10 -> icerik havuzu yeniden ele alinir
* **Basari:** L/1k >= 30 VE C/1k >= 1.0
* **Ara bant:** L/1k 10-29 -> en fazla BIR ek karar penceresi
* **Yorum alarmi (bagimsiz):** C/1k medyani < 0.3

## Degisiklik oncesi taban (2026-08-27 olcumu, 10 yayin)

medyan L/1k **10.2** (oldur esigi 10 - kanal esigin 0.2 puan ustunde)
medyan C/1k **0.00** (10 bolumun 9'unda sifir yorum -> yorum motoru olu)

Bu taban parmak izi OLMAYAN bolumlerden geldigi icin kill-gate karari VERILMEDI;
karsilastirma referansi olarak durur.

## Pencere sirasinda bilinen sinirlar (kayit)

* **Cekim 1'in tek regen hakki.** Bolum sert tavani 800 (bible
  `credit_hard_cap_value`). Tahsisatci aritmetigi: cekim 1'in ikinci regeni icin
  100 (istek) + 300 (cekim 2-4 ana) + 300 (cekim 2-4 ilk regen) = 700 gerekir, ama
  ana+ilk regen sonrasi 600 kalir. Yani **cekim 1 yapisal olarak yalniz BIR regen
  alabilir** - ustelik kapak karesini tasiyan ve ilk-kare kapisiyla sinanan cekim odur.
  Parts 14-21 bu tavanla sorunsuz yayinlandi, o yuzden calisan parametre
  degistirilmedi. Pencerede cekim-1 dususleri TEKRARLARSA cozum kapiyi gevsetmek
  DEGIL, tavani yukseltmektir.
* **D0 ucusta sizinti.** `series/experiment.py` `authorize_spend`'in dondurdugu
  `inflight_id`'yi birakmiyor; kayitlar 900 sn TTL ile dusuyor. Yalniz DENEY yolunu
  etkiler ve taban uretimde KAPALI oldugu icin pencereyi etkilemez. Onarim beklemede.
* **Planlayici kurali beklemede:** descriptor ile anomaly_descriptor ayni obje
  durumunu tarif etmeli (part23'un uc dususunun sebebi). Kuyruktaki part24-26 bu
  celiskiyi TASIMIYOR, ama ikmal yeni bolum yazdiginda kural henuz ogretilmemis olur.

## Parmak izi gecmisi

| an | parmak izi | sebep |
|---|---|---|
| E2 merge sonrasi | `43a0e535...` | stack parmak izi ozelligi eklendi |
| E3 merge sonrasi | `f55e28a3...` | shots.py + replenish.py: shot-1 onset kurali |
| **pencere baslangici** | `ba617381...` | replenish.py: descriptor-anomali uyum kurali |

Pencere HENUZ bolum uretmedi (part22 bu gece 18:30 UTC'de uretilecek), bu yuzden bu
guncellemeler pencereyi kirletmedi. **Bu noktadan itibaren STACK_SOURCES dondu.**

## 2026-08-28: sf1 -> sf2, CANLI YAYINDA BULUNAN KUSUR

part22'nin manuel yayini parmak izi mekanizmasinin kendisini sinadi ve BIR KUSUR
BULDU. Kosu bible'a `kitchen_counter.ref_image_url` yazdi ve parmak izi
`ba617381` -> `6c18a9c5` kaydi. Sebep: sf1'in ucucu alan listesi `ref_url` diyordu,
oysa `produce.py` gercekte **`ref_image_url`** yaziyor. Liste bible'a bakilarak degil
EZBERDEN yazilmisti (Visionary hatasi; Codex spec'i sadik uyguladi).

Duzeltilmeseydi: part23 yarin `bathroom_sink` referansini yazacak, pencere iki farkli
stack gorecek ve kill-gate **sonsuza dek `karar_yok`** verecekti. Olcum sessizce
olurdu; kimse fark etmezdi.

Onarim: ucucu liste artik YAZAN KOD SATIRLARINDAN cikarilmistir
(`ref_image_url`, `ref_image_local`, `kie_audio_id` eklendi). Operator girdileri
BILEREK disarida birakilmadi (`style_ref_url`, `voice.audio_id`). Algoritma
degistigi icin `STACK_VERSION` sf1 -> **sf2**.

`tests/test_stack_fingerprint_volatile.py` bu SINIFI yakalar: canli bible'i tarar ve
uretim-gorunumlu (`*_url`, `*_id`, `*_local`, `registered`) her anahtarin acikca
siniflandirilmis olmasini sart kosar. Yeni bir uretim alani eklenirse test duser.

### part22'nin kaydi neden yeniden hesaplandi

part22 sf1 ile `6c18a9c5` kaydetmisti; kayit sf2 ile `9f3416d2...` olarak
guncellendi. Bu bir uydurma DEGIL sadik bir yeniden hesaptir ve kanitlandi: sf2,
part22 uretiminden **ONCE** ve **SONRA** ayni degeri veriyor (aradaki tek bible
degisikligi sf2'nin disarida biraktigi `ref_image_url`). Video ve uretim tarifi
degismedi; yalniz hangi alanlarin hash'lendigi duzeltildi. Kayitta
`stack_recomputed` alani bunu belgeler.

## Pencere durumu

part22 = **1/10**. Kalan 9 bolum gunluk 18:30 UTC kosusuyla gelir.
Bugunun kosusu gunde-1 kilidi sayesinde tekrar uretmeyecek.

**PENCERE STACK'I: `9f3416d23977da4a3af72bd74887fa0e78e45fb748115f3efeac4c34fe8ddacd`**


## 2026-08-28 (aksam): INSTAGRAM DUSMEDI + PENCERE YENIDEN BASLIYOR

### Olan
part22 YouTube ve TikTok'a dustu, **Instagram'a DUSMEDI**, ama defter uc platformu da
`platforms_ok` yazdi. upload-post'un hata kaydi:

    error_code    : account_reauth_required
    failure_stage : precheck
    error_message : "Error validating access token: The session has been invalidated
                     because the user changed their password or Facebook has changed
                     the session for security reasons. Please reconnect your Instagram
                     account at https://app.upload-post.com/manage-users"

Muhtemel tetikleyici: ayni gun Facebook profilinin upload-post'a baglanmasi. Meta,
bagli hesabin oturumu degisince mevcut Instagram oturumlarini iptal ediyor.
part21 (08-23) sorunsuz dusmustu.

**Dikkat:** `/api/uploadposts/users` hala `reauth_required: False` diyor. O bayrak
GUVENILMEZ; dogrulama is kaydindan yapilmali.

### Neden fark edilmedi
upload-post buyuk yuklemeleri arka plan worker'ina devrediyor ve yanitta ACIKCA
"durumu sorgula" diyor. Bizim uploader `success: True`'yu yayin sayiyordu; o alan
KABUL EDILDI demek. ROCK F1 bunu onardi: platform ancak durum endpoint'i gercek
yayini dogruladiginda OK sayilir, belirsizlik fail-closed'dir, dogrulanamayan is
telafi turunda yeniden POST EDILMEZ (cift yayin riski) ve request_id'li alarm gider.

part22 kaydi duzeltildi: `platforms_ok: ["youtube","tiktok"]`, instagram
`unconfirmed` alaninda request_id'siyle duruyor.

### Pencere yeniden basliyor
ROCK F1 `series/series_runner.py`'yi degistirdi ve o dosya STACK_SOURCES icinde:
parmak izi `9f3416d2...` -> `e1d24f81...`.

"Bu degisiklik yalniz yayin yolunu ilgilendirir, videoyu etkilemez" deyip part22'yi
yeniden damgalayabilirdim. YAPILMADI: olcumu degersizlestiren sey tam olarak bu akil
yurutmedir. Bir bolum kaybetmek, karisik veriyle karar vermekten iyidir.

| | |
|---|---|
| part22 | YAYINLANDI, pencere DISI (stack `9f3416d2`, Instagram'siz) |
| **pencere baslangici** | **part23**, stack `e1d24f8156538747b0fbce02e00649f8c96cc7897c84ccc1b068e7fcb703f0c3` |
| pencere | part23 - part32, ~2026-09-07'de dolar (son tarih 2026-09-16) |

**BU NOKTADAN ITIBAREN STACK_SOURCES DONDU.** Listedeki bir dosyaya dokunmak
pencereyi yeniden baslatir; once
`py -X utf8 tools/killgate_report.py --series unnatural-lab --stack` ile kontrol et.
