# K8: yayina donus ve kill-gate penceresi

## Pencere acildi: 2026-08-28

| alan | deger |
|---|---|
| seri | unnatural-lab (sentinal.ihsan.daily) |
| stack parmak izi | `f55e28a30826a44b4ee3f1a33d4a33f41e9d9a2834357e378fdb08d72243b9d9` |
| acilis commit'i | `43c693b` |
| yayin modu | **auto** (Ihsan karari, 2026-08-28) |
| workflow | `unnatural-lab.yml` ENABLED, gunluk 18:30 UTC |
| ilk bolum | part22 (`next_part=22`) |
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
