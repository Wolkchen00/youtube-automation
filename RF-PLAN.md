# RF-PLAN ,  Video hattı onarımı (Plan 1'in repo A rock'ları)

Kaynak: `Projeler\PLAN_1_VIDEO_YENIDEN_BASLATMA_2026-08-07.md`, İhsan tarafından 2026-08-07'de onaylandı.
Bu dosya o planın **yalnız bu repoda kod değişikliği gerektiren** maddelerini rock'lara böler.

**Core Focus:** Dört kanal her gün, sessizce durmadan, bütçe içinde bir video yayınlasın.

Bugünün somut hedefi: dört kanalda da bugün birer video yayınlanmış olsun ve üretimin
sorunsuz çalıştığı kanıtlansın.

---

## ROCK 1 ,  AImagine üretim kapısını aç (BUGÜN, kritik yol)

`from-scratch` hattı şu an matematiksel olarak fail-closed. Kredi kapısı açık olsa bile
bölüm üretemiyor. Üç ayrı değişiklik gerekiyor.

### R1.1 ,  Bölüm kredi tavanı 1400 → 1900

`.github/workflows/from-scratch.yml`, `Create .env` adımındaki `EPISODE_CREDIT_CAP` satırı.

Dayanak (ölçüldü, tahmin değil):

```
zorunlu müzik (suno)                        80
6 ana çekim x omni 10 sn x 200            1200
bölüm regen bütçesi 3 x 200                600     (qc_budget = round(6/2) = 3)
                                   toplam 1880
yeni tavan                                1900
```

Eski tavan 1400 ile: 1200 + 1 regen 200 = 1400, ardından zorunlu müzik 80 bloklanıyor ve
`produce()` `None` dönüp bölümü tamamen düşürüyor.

**Done looks like:** dosyada `EPISODE_CREDIT_CAP=1900` yazıyor, satırın üstündeki yorum
yeni hesabı açıklıyor.

### R1.2 ,  Zorunlu müzik çekimlerden ÖNCE rezerve edilsin

Bugün `produce.py` müziği çekim döngüsünden **sonra** yetkilendiriyor (müzik `authorize`
çağrısı satır ~248, çağıran fonksiyon satır ~995'te koşuyor). Müzik `required_layers`
içinde, yani zorunlu bir katman. Bütçe biterse **isteğe bağlı** bir QC regen'i yüzünden
**zorunlu** müzik bloklanıyor ve bölüm ölüyor.

**Değişmez kural 1:** Müzik, hiçbir ana çekim harcamasından önce rezerve edilir.
**Değişmez kural 2:** Müzik tavana karşı **tam olarak bir kez** sayılır. Ön rezervasyon
sonradan ikinci kez ücretlendirilmez.
**Değişmez kural 3:** Plan müziksizse (müzik prompt'u yok) hiçbir rezervasyon yapılmaz ve
davranış bugünküyle aynı kalır.

Mekanizmayı sen seç. Sözleşme bu üç değişmez kuraldır.

**Done looks like:** Simülasyonda sıra `müzik → 6 çekim → 3 regen` olur ve 1900 tavanına
sığar. Müzik bütçe yetersizliğinden bloklanamaz.

### R1.3 ,  QC "skip" bölümü öldürmesin, yalnız gerçek RED öldürsün

`critic.py` iki farklı şeyi aynı kovaya koyuyor:

- `_review_clip` satır ~259: denetim karesi çıkarılamadı → `"skip"`
- `_review_clip` satır ~263: Gemini denetimi başarısız (rate limit, 5xx, zaman aşımı) → `"skip"`
- `review_and_regen` satır ~361-370: `require_all_shots` açıkken `"skip"` gelirse klip
  `_qcskip` diye yeniden adlandırılıyor ve `None` dönüyor → **tüm bölüm düşüyor**

`from-scratch` bible'ında `qc.require_all_shots = true`. Yani tek bir geçici Gemini hatası
~1.280 krediyi yakıp sıfır video üretiyor. Bu davranış canlıda hiç test edilmedi.

**Gereken davranış:**

1. `"skip"` verdict'i alındığında denetim **yeniden denenir**: varsayılan 2 ek deneme,
   denemeler arasında kısa bekleme. Ayar adı `qc_review_retries`, `QC_DEFAULTS` içinde
   varsayılan `2`, `bible.json` → `series.qc` üzerinden geçersiz kılınabilir.
2. Yeniden denemede `"pass"` veya `"fail"` gelirse o sonuç normal akışta işlenir.
3. Denemeler bittiği hâlde hâlâ `"skip"` ise: **klip kabul edilir** (yol döndürülür,
   durum `"skip"`), `require_all_shots` açık olsa bile bölüm düşürülmez. Uyarı loglanır
   ve bildirim gönderilir; olay `_log_event` ile `qc_skip_accepted` olarak kaydedilir.
4. `"fail"` davranışı **hiç değişmez**: gerçek RED, regen hakkı bitince bugünkü gibi
   çekimi bölümden düşürür.

Gerekçe (onaylı plan K7): denetlenemeyen klip ile RED alan klip aynı şey değildir.

**Done looks like:** Geçici denetim hatası bölümü öldürmez; ısrarlı gerçek RED öldürür.

### ROCK 1 PROOF

```
python -X utf8 tests/test_fixedframe.py
python -X utf8 tests/test_credit_gate.py
python -X utf8 tests/test_doctrine_gate.py
python -X utf8 tests/test_rock1_budget_and_qcskip.py
```

Dördü de `OK` vermeli. Son dosya bu rock'ta yazılacak yeni testtir ve şunları kanıtlamalı:

| # | Test | İddia |
|---|---|---|
| T1 | Gerçek `aimagine/from-scratch/plans/part06.json` ile 1900 tavanlı `HardCreditCap`, müzik + 6 çekim + 3 regen sırasını **bloklanmadan** geçirir | R1.1 + R1.2 |
| T2 | Aynı senaryo 1400 tavanıyla bloklanır (regresyon nöbetçisi: tavan sessizce geri düşerse test kırmızı olur) | R1.1 |
| T3 | Müzik tavana tam bir kez sayılır: ön rezervasyon + sonraki müzik çağrısı toplamda 80 kredi harcar, 160 değil | R1.2 değişmez kural 2 |
| T4 | Müziksiz plan hiç müzik rezervasyonu yapmaz | R1.2 değişmez kural 3 |
| T5 | İlk denetim `"skip"`, ikinci deneme `"pass"` → klip kullanılır, bölüm düşmez, tek regen bile harcanmaz | R1.3 madde 1-2 |
| T6 | Tüm denemeler `"skip"` + `require_all_shots=True` → klip **kabul edilir**, dönüş yolu `None` DEĞİLDİR | R1.3 madde 3 |
| T7 | Israrlı `"fail"` + regen hakkı bitti → çekim bugünkü gibi düşürülür (davranış değişmedi) | R1.3 madde 4 |

Testler tamamen çevrimdışı olmalı: ağ yok, Gemini yok, Kie yok. Mevcut
`tests/test_fixedframe.py` bu repoda kabul edilen mock desenini gösteriyor, onu izle.

---

## ROCK 2 ,  Shadowed oto-ikmali (yarın 20:30 UTC'den önce)

`shadowedhistory/flashpoints` kuyruğunda tek bölüm kaldı (part 5/5). Oto-ikmal
2026-07-29'dan beri her koşuda çöküyor, son üç koşuda aynı hatayla:
`part 6: ardışık iki part aynı family değerini kullanamaz`.

Kök neden: ikmal prompt'u "ardışık iki bölüm aynı `family` olamaz" diyor ama **hangi
family'nin yasak olduğunu söylemiyor**. Doğrulayıcı biliyor, üretici bilmiyor.

- Yasak `family` değeri prompt'a açıkça yazılır.
- Kullanılmamış konu havuzu, yasak family elenmiş hâlde verilir.
- Deneme sayısı 2'den 3'e çıkar.

**PROOF:** `python -m series.replenish --series flashpoints` başarılı döner,
`shadowedhistory/flashpoints/plans/part06.json` yazılır,
`python -m series.preflight --series flashpoints --plan 6` OK verir.
Ek olarak ROCK 1'in dört test dosyası hâlâ `OK` vermeli.

---

## ROCK 3 ,  Sessiz başarı üçlüsü (bugünkü üretim doğrulandıktan SONRA)

Onaylı plan KARAR 4: bu rock bugünkü manuel üretim doğrulanmadan uygulanmaz, çünkü
pipefail bugüne dek gizlenmiş başka hataları da kırmızıya çevirebilir.

- Dört workflow'a `defaults: run: shell: bash -euo pipefail {0}`.
- `series_runner.main()`: `if not dry and ok is not True: sys.exit(1)`.
- `last_run.json` gerçek iş çıktısından yazılsın: `published` / `blocked_credit` /
  `series_completed` / `daily_lock`.

**PROOF:** Kredi kapısı kapalı simüle edilmiş bir koşu kırmızı düşer ve
`last_run.json`'a `blocked_credit` yazar.

---

## ROCK 4 ,  Alarm metni ve watchdog eşik senkronu

- `_alert()` metnine sonuç yazılır: kanal adı + "bugün video ÇIKMAYACAK" + son video kaç gün önce.
- Watchdog nabız eşiği 18 saatten 30 saate çıkar (her sabah garantili sahte KRİTİK alarmı biter).
- `KIE_CRIT_BALANCE` en yüksek hat eşiğinden türetilir (bugün sabit 1350, oysa from-scratch kapısı 2850 olacak).

**PROOF:** Yeni kurallar 08-04..08-07 koşu geçmişine karşı denendiğinde en az dört ihlal üretir.

---

## Bu planda OLMAYANLAR (bilerek)

- Maliyet tablosu kalibrasyonu (K3): bugünkü gerçek koşunun ölçümü gerekiyor, S9'da.
- Aylık tavan, `published.json` düzeltmesi, telafi koşusu (K8, K9, K10): Eylül başına.
- Plan 2'nin tamamı: farklı repo (`yt-yorum-otomasyonu`), ayrı çalışma.
