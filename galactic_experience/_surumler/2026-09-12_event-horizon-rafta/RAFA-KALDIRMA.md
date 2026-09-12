# event-horizon RAFTA , 12 Eylül 2026

**Karar:** İhsan. "galacticexperimet kanalına aylardır video paylaşıyoruz ve bir yere
varamadık, izlenmeler çok kötü durumda, kanal konseptini değiştiriyoruz."

Bu klasör konseptin **rafa kaldırıldığı andaki tam hâlidir.** Silinmedi, donduruldu.

## Ölçülen durum (neden durduruldu)

| Ölçüm | Değer | Kaynak |
|---|---|---|
| Abone | 140 | `gunluk_beyin/kanallarimiz.md`, 10 Eylül 2026 |
| Yayınlanan video (kanal ömrü) | 199 | aynı |
| 30 günlük medyan izlenme | **88,5** | aynı |
| event-horizon defteri, medyan | 104 | `gunluk_beyin/kanallar/event-horizon/BEYIN.md` |
| event-horizon defteri, aralık | 24 , 393 | aynı |
| event-horizon bölüm sayısı | 33 yayınlandı (part01-33) | `published.json` |
| İlk yayın | 30 Temmuz 2026 | aynı |
| Son yayın | 12 Eylül 2026 | aynı |

Karşılaştırma: aynı motorun beslediği `unnatural-lab` şeridi 30 günlük medyan **1.292**
izlenme yapıyordu. Sorun motor değil, konsept.

Beyin ayrıca şunu söylüyordu: **n=11 tam kayıt, eşik 15.** Yani bu kanala özel kural
çıkarmaya yetecek temiz veri hiç birikmedi. Ek olarak iki eşik HİÇ uygulanmamıştı:
en uzun plan 4 sn tavanı (ölçülen 5,6) ve LUFS -16..-13 hedefi (ölçülen -22,1).
`master_lufs: -14` bible'a ancak 11 Eylül'de eklendi, yani yayınlanan 33 bölümün
neredeyse tamamı sessiz çıktı. **Yeni konseptte bu iki eşik ilk günden uygulanmalı.**

## Ne durduruldu

1. `galactic_experience/event-horizon/series.json`
   - `status`: `active` → `paused`
   - `auto_replenish.enabled`: `true` → `false`
   - `rafa_kaldirildi` bloğu eklendi
2. `.github/workflows/event-horizon.yml`
   - `schedule` bloğu yoruma alındı (eski cron: `30 16 * * *`)
   - `workflow_dispatch` duruyor, yani elle tetiklenebilir
3. `filo.json` cron envanterinden event-horizon kaydı çıkarıldı
   (pano artık bu şeridi "sessiz kaldı" diye alarma çevirmez)

## Ne DURMADI (bilerek)

- **YouTube'daki 33 video duruyor.** Kaldırma kararı verilmedi.
- Günlük beyin bu kanalı ölçmeye devam ediyor (`gunluk-beyin.yml`). Yeni konseptin
  karşılaştırma tabanı bu defter.
- `galacticexperimet` upload profili, kanal ID'si ve Upload-Post kaydı aynen duruyor.
- Motor (`series/`, `core/`) hiç değişmedi. Yeni konsept aynı motorla yazılabilir.

## Geri açmak için

```
# 1) series.json
status: "paused" -> "active"
auto_replenish.enabled: false -> true
rafa_kaldirildi bloğunu sil

# 2) .github/workflows/event-horizon.yml
"# schedule:" ve "#   - cron: ..." satırlarının yorumunu kaldır

# 3) filo.json cron listesine event-horizon kaydını geri ekle
```

Konu havuzu (`topic_pool`) 35 doğrulanmış tohum içeriyor ve içinde kalıyor. Part 34-35
planları üretilmiş ama yayınlanmamış durumda, `plans/` altında duruyorlar.

## Bu klasörde ne var

| Dosya | Nedir |
|---|---|
| `KONSEPT.md` | Kanal doktrini v1.5, rafa kaldırıldığı andaki hâli |
| `series.json` | Durdurulmadan önceki seri ayarı (topic_pool dahil) |
| `bible.json` | Görsel/ses reçetesi |
| `event-horizon.yml` | Cron açıkken çalışan workflow |
| `published.json` | Yayınlanan 33 bölümün kaydı (YouTube ID'leri dahil) |
| `BEYIN-son.md` | Kapanış anındaki günlük beyin raporu |
