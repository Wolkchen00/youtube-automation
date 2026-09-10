# RF-PLAN , shadowedhistory / flashpoints kanal duzeltmesi

Tarih: 10 Eylul 2026 (Los Angeles)
Dal: `codex-shadow-kanal` (worktree; ana agacta bes baska oturum calisiyor)
Kaynak: `shadowedhistory/REELYZE-RAPOR.md` + bu kosuda yapilan olcum
Revizyon: r2 (Codex Same Page turu 1 sonrasi , dort rock'tan ikisi oldu)

## Core Focus (tek cumle)

flashpoints'in yayinladigi hicbir bolum sessiz olmasin ve hicbir bolum anlattigi
faktı yarim birakmasin.

## Bu plan neyi COZMEZ

Erisim sorununu cozmez. Kanalin iki hitini (1.179 ve 509 izlenme) ne ses ne sure
acikladi. Bu plan yalnizca "yayinladigimiz sey butun ve duyulabilir olsun" sorununu
cozer. Sure, konu secimi ve ekran yazisi `RF-ISSUES.md`'ye tasindi.

---

## Olculen durum (bu kosuda dogrulandi, hepsi dosya:satir veya canli olcum)

### Kanit 1: mastering hic calismiyor

```
series/produce.py:2147   master_lufs = bible.master_lufs
series/produce.py:2148   if master_lufs is None:  ->  master_audio() HIC CAGRILMIYOR
```

`shadowedhistory/flashpoints/bible.json` `series` blogunda `master_lufs` alani YOK.
Filoda alani tanimli tek seri `sentinal_ihsan/unnatural-lab/bible.json:11` (`-14`) ve
olculen ciktisi -14,3 LUFS. flashpoints olculen: -20,5 ile -25,1 LUFS. Hedef -16..-13.

### Kanit 2: 29 bolumun 9'u YARIM yayinlandi

```
series/produce.py:126-130  _required_shot_count():
    bible.min_shots None ve require_all_shots False  ->  return 1
```

`flashpoints/bible.json` `qc` blogunda `min_shots` yok, `require_all_shots` yok.
Iki cekimlik bir plan TEK cekimle yayina cikabiliyor.

`qc_log.jsonl` -> `final_reject` 8 bolumde (4, 9, 22, 23, 24, 26, 27, 30). Yayinlanan
sure dagilimina gore toplam 9 bolum tek cekimle cikmis (part 6 QC disi bir yoldan
cekim kaybetmis).

Cekim dustugunde `produce.py:570-583` anlatimi otomatik kisaltiyor
(`shorten_narration_for_duration`). Plandaki 33-42 kelimelik anlatim ~12 kelimeye
iniyor. Bolum yayinlaniyor ama **anlattigi faktı bitirmiyor.**

Bu, doktrin v1.8(c)'nin ("anlatim daima TAM CUMLEYLE biter") sessizce ihlalidir:
Ihsan v1.8'de yarim biten cumleyi ACIKCA yasakladi, ama dusen cekim yolu ayni sonucu
arka kapidan uretiyor.

---

## Rock 1: Ses , mastering'i devreye al

**Sorun:** `bible.json` `series` blogunda `master_lufs` yok, mastering atlaniyor.

**Yapilacak:**
1. `shadowedhistory/flashpoints/bible.json` -> `series` blogunun icine
   `"master_lufs": -14`. Referans bicim: `sentinal_ihsan/unnatural-lab/bible.json:11`.
2. `tests/test_rocka_audio_master.py::test_only_unnatural_lab_has_master_lufs`
   guncelle: bu bir YASAK degil, bir KAYIT testidir , hangi serilerin mastering'e
   opt-in oldugunu tek yerde tutar. Beklenen liste iki girdiye cikar
   (flashpoints -14 ve unnatural-lab -14), siralamadan bagimsiz karsilastirilir.
   Test adi da kaydi yansitacak sekilde guncellenir.

**Done looks like:** `Bible.load("flashpoints").master_lufs == -14.0`; `produce.py:2148`
dali artik `master_audio()` cagiran kola giriyor; kayit testi iki seri bekliyor.

**Bilinen yan etkiler , UCU de dogrulandi ve kabul ediliyor:**

`master_lufs` sadece mastering'i acmaz; uc mikser anahtarini birden cevirir:

| Anahtar | Once | Sonra | Kaynak |
|---|---|---|---|
| `amix_normalize` | True | False | `produce.py:605` |
| `limit_mix_peak` | False | True | `test_master_true_peak.py:132` |
| `music_volume` (anlatimli) | 0.28 | **0.50** | `produce.py:656` |

Ucuncusunu ilk taslakta kacirdim; Codex turu 2 yakaladi. Motorun kendi yorumu
(`produce.py:654-655`) bunun tasarlanmis bir eslesme oldugunu soyluyor:
*"opt-in yatak 0.50'ye eslendi (foley/yatak +6,19 dB; anlatim/yatak degisimi +0,42 dB)"*.
Yani muzik yatagi yukseliyor ama anlatim/yatak DENGESI yalnizca +0,42 dB kayiyor,
cunku mastering tumunu -14'e geri normalize ediyor. Kabul ediliyor, ama proof bu
degeri de olcecek.

**Yigin parmak izi:** `master_lufs` parmak izine giriyor (`core/stack_fingerprint.py`),
`core/killgate.py` karsilastirma penceresi sifirlaniyor. Dogru davranis; uretimi
durdurmaz (`series_meta.py:133-135`: parmak izi yalniz olcum metadatasidir, hesabi
bozulursa uyari yazilir ve gecilir).

**YENI HATA MODU (Codex turu 2, dogrulandi):** mastering veya teslim dogrulamasi
basarisiz olursa `produce.py:2164` `_audio_master_hold(...)` doner; `series_runner.py:781-789`
bolumu `awaiting_approval` yapar, yayini bloke eder ve Telegram uyarisi gonderir.
Bu bolum OTOMATIK yeniden denenmez , elle mudahale ister. Bu fail-closed davranis
DOGRUDUR (masterlenmemis video yayinlamaktansa beklemek), ama Rock 1 oncesinde bu
yol flashpoints icin hic acik degildi. Kurtarma: Telegram uyarisi gelir, `series.json`
`parts.<n>.status` `awaiting_approval` olur; elle incelenip durum geri alinir.

**DOKUNMA:** `core/ffmpeg_tools.py`, `series/produce.py`, `series/bible.py`. Motor
dogru; eksik olan yalniz kanal konfigurasyonu. Baska kanalin bible dosyasina dokunma.

## Rock 2: Yarim bolum yayinlanmasin

**Sorun:** `min_shots` tanimsiz, esik 1'e dusuyor, iki cekimlik plan tek cekimle cikiyor.

**Yapilacak:** `bible.json` -> `qc` blogunun icine `"min_shots": 2`.

**Done looks like:** `_required_shot_count(bible, 2) == 2`. Bir cekim final_reject
alirsa `produce_episode` None doner, bolum yayinlanmaz.

**Operasyonel bedel , olculdu ve kabul edildi:**
- Bolum KAYBOLMAZ. `series/series_runner.py:794` , *"Part n uretilemedi, durum
  ilerletilmedi (sonraki calistirmada tekrar denenir)"* , ve Telegram uyarisi gider.
  flashpoints'te `state_machine_version` alani yok, yani basit yeniden-deneme yolu
  gecerli. Bedel bir gunluk gecikme, kayip degil.
- Harcanan kredi geri gelmez (bkz. `RF-ISSUES.md`). Gecmis oranla (~%29) bu, ayda
  birkac bolumluk gecikme demektir.
- Bu kural gecmiste uygulansaydi kanalin iki hiti (part 22 = 1.179, part 26 = 509)
  o gun yayinlanmaz, ertesi gun tam haliyle yayinlanirdi. Tek cekimli kovanin
  medyani 23, iki cekimli 15 sn kovasinin medyani 33: iki hit tek cekimin
  ustunlugunu gostermiyor, kovadaki diger yedi bolum 2-64 arasinda.

**DOKUNMA:** `series/preflight.py`, `series/produce.py`.

---

## OLDURULEN ROCK'LAR (Codex turu 1 bunlari yikti, gerekce `RF-ISSUES.md`'de)

- **Sureyi 15 saniyeye geri al.** Ihsan'in 2026-09-01'de izleyici geri bildirimiyle
  aldigi v1.8 kararini geri alirdi ve tam olarak sikayet edilen kusuru geri getirirdi.
- **fact_captions'i ac.** Doktrin v1.1'de bilerek kaldirilmis ve iki cekimlik seride
  dogrulayicisi matematiksel olarak saglanamaz , kanalin plan uretimini kilitlerdi.

---

## PROOF

### Yeni dosya: `tests/test_flashpoints_kanal_sozlesmesi.py`

Bir konfigurasyon sozlesme testi. Gerekcesi: bu depoda CI durum dosyalarini geri
yaziyor (`chore: flashpoints durumunu ilerlet [skip ci]`), yani `bible.json` ve
`series.json` otomatik islemlerin dokundugu dosyalar. Testsiz bir konfigurasyon
duzeltmesi sessizce geri alinabilir.

Test sunlari dogrulamali (gercek repo dosyalarini okuyarak, motoru mocklamadan):

1. `Bible.load("flashpoints").master_lufs == -14.0`
2. **Uc mikser yan etkisi olculur** (yalniz sayiyi degil davranisi kilitler):
   flashpoints bible'i ile `bible.master_lufs is None` False, yani
   `amix_normalize` False, `limit_mix_peak` True ve anlatimli yol `music_volume`
   0.50 secer (`produce.py:656` ifadesi birebir dogrulanir, 0.28 DEGIL)
3. `series.produce._required_shot_count(bible, 2) == 2`, VE kontrol capasi:
   `min_shots` alani cikarilmis bir bible kopyasinda ayni cagri `1` doner
4. **Bos gecmeyen min_shots kaniti:** `plans/part31.json`'un TEK cekimli bir kopyasi
   `series.preflight.validate_min_shots(bible, tek_cekimli_plan)` tarafindan
   REDDEDILIR (hata listesi bos degil, mesaj `min_shots` gecer); degistirilmemis
   iki cekimli part31 icin bos liste doner
5. **Kacis kapisi kapali kalsin , ham alan yoklugu** (Codex turu 2): `fact_captions`
   anahtari NE `bible.data["series"]` icinde NE de `SeriesMeta.load("flashpoints").auto_replenish`
   icinde bulunmali. `Bible.fact_captions == {}` tek basina yetmez: bayrak
   `auto_replenish`'te acilirsa bible bos donmeye devam eder ama replenish
   celiskiye girer. Iki dosya da denetlenir.
6. `SeriesMeta.load("flashpoints").auto_replenish["shot_seconds"] == "10"` , Rock 3
   oldurulmustur; doktrin v1.8 ile hizali kalindigini kilitler

Codex turu 1'in [KILL] dedigi iki assert (gecmis plan dosyalarinin degismedigi ve
kardes kanalin bozulmadigi) ve turu 2'nin [KILL] dedigi `title_card` assert'i test
dosyasindan CIKARILDI: bunlar Core Focus'u korumaz ve dogru araci git diff'tir.
Kapsam, Level 10 incelemesinde tam diff okunarak dogrulanacak.

**Kapsanamayan (durust sinir):** Codex turu 2 hakli olarak "calisma zamaninda cekim
dusunce `next_part` ilerlemiyor" iddiasinin test edilmedigini soyledi. Bu iddia bu
kosuda KOD OKUMASIYLA dogrulandi (`series_runner.py:791-796`, flashpoints'te
`state_machine_version` yok, legacy yol gecerli) ama testle kanitlanmadi , tam bir
`run_next` entegrasyon testi motoru mocklamayi gerektirir ve bu kosunun kapsami
disindadir. Bu sinir `RF-ISSUES.md`'ye yazildi.

### Calistirma (iki komut da yesil olmadan rock kapanmaz)

```
python -m pytest tests/test_flashpoints_kanal_sozlesmesi.py -q
```

```
python -m pytest tests/test_rocka_audio_master.py tests/test_doctrine_gate.py tests/test_min_shots.py tests/test_master_true_peak.py tests/test_stack_fingerprint.py -q
```

Ikinci komut regresyon kapisidir. `test_doctrine_gate.py` flashpoints icin
`shot_seconds == "10"` bekliyor , Rock 3 oldurudugu icin bu test DEGISMEDEN gecmeli.
Gecmiyorsa kapsam disina tasilmistir.

---

## Kapsam disi (bu kosuda ASLA dokunulmayacak)

- `core/` ve `series/` altindaki hicbir `.py` , motor dogru, dort kanali birden besliyor
  ve su anda bes ayri oturum ayni depoda calisiyor
- `shadowedhistory/KONSEPT.md` , doktrin metni; hash'i `series.json` ve her plana
  pinli (`series/replenish.py:428-432`). Bu kosuda doktrin degistirilmiyor, bu yuzden
  hash de degismiyor.
- `shadowedhistory/flashpoints/series.json` , Rock 3 oldu, dokunulmuyor
- `plans/part01.json` .. `plans/part35.json` , hicbiri duzenlenmiyor
- `sentinal_ihsan/`, `galactic_experience/`, `aimagine/`, `AImagine-Fear/` , baska
  oturumlarin sahasi
- `shadowedhistory/drowned-history/`, `footnotes/`, `secrets-anatolia/`
- `published.json`, `qc_log.jsonl`, `series_log.csv`, `calibration.json` , calisma
  zamani durumu, elle duzenlenmez
- Cozunurluk (1080x1920) ve fps (30) , dogru

**Bu kosuda degisen dosya sayisi: 3.** `flashpoints/bible.json`,
`tests/test_rocka_audio_master.py`, `tests/test_flashpoints_kanal_sozlesmesi.py` (yeni).
Arti bu iki artefakt. Baska hicbir sey.
