# RF-PLAN-YAYIN-SAATI: her kanal kendi izleyici saatinde yayinlasin

Tarih: 2026-09-24. Sahip: Ihsan. Visionary: Claude. Integrator: Codex.

## Core Focus

Her kanal, GitHub cron gecikmesinden bagimsiz olarak kendi hedef saatinde yayinlasin;
beklerken paylasilan `kie-uretim` sirasini tutmasin; bugunku kanitlanmis yayin yolu
(caption + soru + ilk yorum + kayit defteri + gunluk kilitler + kosu sonucu kaniti)
DEGISMESIN, yalniz ZAMANI degissin.

## Olculen gercekler (24 Eyl 2026)

- Hedef saatler (Instagram takipci ulkeleri + YouTube goruntulenme ulkeleri + sentinal
  icin YouTube Studio gercek saat tablosu; model sentinal'de 2 saat gec ciktigi icin -2s
  kalibre edildi). UTC:
  - wild-encounter (sentinal): **11:00**
  - fear-slide (aimagine): **15:00**
  - still-home (shadowedhistory): **15:30**
  - galactic-daily (one-variable ve flythrough, galactic): **16:00**
  - The Unfinished: DEGISMEZ (yerelden Upload-Post `scheduled_date` 18:00 UTC).
- GitHub cron gecikmesi (son 2 hafta, `gh run list`): fear-slide 13:20 -> 16:33..18:47
  basladi; wild 18:30 -> 20:53..22:06; still-home 20:30 -> 22:23..23:28; galactic
  16:30 -> 18:40..20:28. Yani 2,0..5,5 saat gec ve gunden gune +-1,5 saat oynuyor.
- Uretim suresi (kosu baslangici -> bitisi): 5..30 dk.
- Depo PUBLIC: Actions dakikasi ucretsiz, uzun bekleme maliyetsiz. Barindirilan
  runner'da is basina tavan 360 dk.
- DORT is akisi da is akisi duzeyinde `concurrency: {group: kie-uretim,
  cancel-in-progress: false}` paylasiyor (Kie kredi guvenligi). GitHub bir grupta en
  fazla 1 calisan + 1 bekleyen tutar; yeni bekleyen eskisini IPTAL eder. Yani grubu
  tutarak saatlerce bekleyen bir is diger hatlari kilitler/iptal ettirir.
- "Uret simdi, sonra yayinla" altyapisi kismen var: onay modu (`publish_mode:
  "approval"`) uretilen videoyu GitHub Release'e koyar, `series/approver.py` sonradan
  indirip `series_runner._publish_part` ile yayinlar. ROCK E `series/durable_artifact.py`
  auto modda da kalici eser kimligi uretir. AMA approver yolu caption/soru/ilk yorum
  GECIRMIYOR (bagimsiz incelemede bulundu) ,  bekleyen yayin bu yolu kullanacaksa
  auto moddaki metin yolunun aynisini tasimali.
- fear-slide seri motoru DEGIL: `AImagine-Fear/tools/gunluk.py` uretir ve
  `tools/yayinla.py`'yi alt surec olarak cagirir; kendi defteri `AImagine-Fear/yayin.jsonl`,
  ayni-gun kapisi LA tarihine gore, `kullanildi` YouTube kimliginden turer. 21:30 UTC
  telafi cron'u var.

## Tasarim

1. Yapilandirma (opt-in, yoksa bugunku davranis):
   - seri hatlari: `series.json` -> `"yayin_saati_utc": "HH:MM"` (4 seride).
   - fear-slide: `AImagine-Fear/canon/YAYIN_SAATI.json` -> `{"yayin_saati_utc": "15:00"}`.
2. Her is akisi IKI isa bolunur; concurrency is akisi duzeyinden IS duzeyine iner:
   - `uret` isi: `concurrency: kie-uretim` (bugunku gibi). Uretir. Hedef saat
     simdiden >10 dk ilerideyse YAYINLAMAZ: videoyu ve yayin icin gereken her seyi
     (seri: part no + dosyalar; fear-slide: master + slug + baslik + etiket + uretim
     kaydi) `actions/upload-artifact` ile birakir, durumu "yayin_bekliyor" olarak
     isaretleyip persist eder. Hedef saat gecmisse ya da `workflow_dispatch` ile
     `bekle` girdisi false geldiyse (varsayilan) BUGUNKU GIBI hemen yayinlar.
   - `yayinla` isi: `needs: uret`, yalniz uret "bekliyor" ciktisi verdiyse kosar;
     `concurrency: yayin-<hat>`; `timeout-minutes: 350`. Artifact'i indirir, hedef
     saate kadar uyur (en fazla 330 dk; hedef gecmisse hemen), sonra BUGUNKU auto
     yayin yolunun AYNISIYLA yayinlar (ayni fonksiyon; caption/soru/ilk yorum/kayit/
     kilitler/kosu sonucu). Sonra persist + kosu sonucu kaniti.
3. Kurtarma: `yayinla` dustuyse ya da iptal edildiyse, ertesi gunun `uret`i
   "yayin_bekliyor" partini gorur. Artifact artik erisilemez olabilir; bu yuzden `uret`
   bekletme kararinda videoyu AYRICA kalici depoya (mevcut Release mekanizmasi) koyar
   ve ertesi gun once o parti yayinlar (yeniden uretmez, kredi harcamaz), sonra
   normal akisa devam eder. Gunde-1 kanal kilidi bu durumda ikinci yayini engeller.
4. Cron = hedef - 5,5 saat: wild `30 5`, fear-slide `30 9` (+ `30 21` telafi kalir),
   still-home `0 10`, galactic `30 10`.
5. Gozlem: `yayinla` basinda "hedef HH:MM UTC, simdi .., bekleme N dk", sonunda
   "hedef .., gercek .., sapma N dk" loglanir ve kosu sonucu kaydina `hedef_saat`,
   `gercek_saat` yazilir.

## Rocks

### Rock 1: seri motoru (series/series_runner.py + ilgili)
- `run_next` / CLI: hedef saat ileride ise uret-ama-yayinlama modu: videoyu kalici
  depoya koy, part durumunu `yayin_bekliyor` + `hedef_saat_utc` yap, artifact icin
  dosya yollarini bir manifest'e yaz (`output/yayin_bekliyor.json`).
- Yeni CLI `python -m series.series_runner --series <slug> --bekleyeni-yayinla
  [--bekle]`: manifest'i (yoksa kalici depodaki eseri) bulur, `--bekle` verildiyse hedef
  saate kadar uyur, sonra run_next'in auto yayin yolunun AYNISINI calistirir (caption
  birlestirme, soru, ilk yorum, `_publish_part`, `_append_publish_registry`, durum
  guncellemesi). Kod tekrari YOK: ortak yayin kismi tek fonksiyona cikarilir.
- Ertesi gun kurtarma: `run_next` basinda `yayin_bekliyor` part varsa once onu yayinlar.
- Done: yayin_saati_utc yokken davranis bayt bayt ayni (mevcut testler yesil);
  varken uret -> bekleyen -> yayinla zinciri testte tek parti bir kez yayinlar.
- Proof: `python -X utf8 -m pytest tests/test_yayin_saati.py tests/test_ilk_yorum.py tests -q`
  (HEAD'de zaten kirik 5 test: test_experiment_runner x4, test_rock5_containment x1).

### Rock 2: seri is akislari (wild-encounter.yml, still-home.yml, galactic-daily.yml)
- Iki is, is-duzeyi concurrency, artifact devri, `bekle` girdisi, yeni cron'lar.
- galactic-daily'de gun paritesi secimi `uret` isinde kalir, secilen serit `yayinla`ya
  cikti olarak gecer.
- Proof: YAML parse + `tests/test_yayin_saati_workflow.py` (metin/yapi denetimi:
  concurrency is duzeyinde, yayinla timeout 350, cron'lar dogru, persist yollari).

### Rock 3: fear-slide (AImagine-Fear/tools/gunluk.py + fear-slide.yml)
- `gunluk.py --yalniz-uret` (hedef ileride ise yayinlamaz, master + yayin argumanlari
  manifest'e) ve `gunluk.py --bekleyeni-yayinla [--bekle]` (ayni `yayinla` fonksiyonu,
  ayni argumanlar, ayni defter). Telafi cron'u bekleyeni varsa once onu yayinlar.
- Is akisi ayni iki-is yapisina gecer; sehir istekleri adimi yayinla isinin sonuna tasinir.
- Proof: `python -X utf8 -m pytest AImagine-Fear/tests -q` + `python -X utf8 AImagine-Fear/build.py --check`.

## Kisitlar

- Yayin yolu tek: bekleyen yayin ile hemen yayin AYNI fonksiyonu cagirir.
- Hicbir yol ayni partin iki kez yayinlanmasina izin vermez (manifest + durum + defter).
- `yayin_saati_utc` olmayan seri/hat bugunku gibi davranir.
- Yeni bagimlilik yok. Testlerde ag yok. Golden testler yesil kalir.
- The Unfinished'a dokunulmaz.
