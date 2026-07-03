# _archive — Eski Sistem Arşivi

**Arşivlenme tarihi:** 2026-07-03 (İhsan kararı — "eski sistem önümüze çıkmasın, gerekirse arşivden bakarız")

Buradaki hiçbir şey CANLI DEĞİLDİR ve hiçbir cron/workflow tarafından çağrılmaz.
Canlı sistem: `series/` motoru + `series_data/` + `.github/workflows/series.yml` (günlük 14:30 UTC).

## İçerik

### old_pipelines/ — Eski kanal pipeline'ları (VEO3/Kling dönemi)
| Klasör | Kanal | Yerine geçen |
|---|---|---|
| `sentinal_ihsan/` | sentinalihsan "viral deney" UGC motoru | the-signal → night-shift → room-408 serileri (series motoru) |
| `shadowedhistory/` | Shadowed History | secrets-anatolia serisi |
| `galactic_experiment/` | Galactic Experiment | ava-voyage serisi |
| `aimagine/` | AImagine | infinite-trip serisi |
| `daily_runner.py` | 4 kanalı çalıştıran eski master runner | `series/series_runner.py` (günde-1 tavanı) |

### old_workflows/ — Kapatılmış GitHub Actions workflow'ları
- `morning.yml`, `evening.yml` — eski kanal pipeline cron'ları. Arşivlenmeden önce de
  tamamen kapalıydılar (cron yorumda + tüm job'lar `if: false`).

### old_series_data/ — Ölü seri verileri
- `viral-detective/` — sentinalihsan'ın ilk seri denemesi (status=paused, 3 bölüm yayınlandı,
  yerini the-signal aldı). `_HANDOFF.md` içinde dönem notları var.
- `yaris-demo/` — motor test demosu (status=draft, hiç üretilmedi).

### logs/
- `_setup_viral.log` — 2026-06-14 eski kurulum logu.

## Arşivle birlikte yapılan güvenlik değişikliği
- `series_data/the-signal/series.json`: status `completed` → **`paused`**.
  Sebep: ikmal motoru (`series/replenish.py`) "completed" serileri otomatik diriltebiliyor;
  "paused" insan kararıdır ve ASLA diriltilmez. Uzaylı serisinin kendiliğinden geri
  dönmesini engeller. (the-signal'ın yayın geçmişi `series_data/the-signal/` içinde duruyor.)

## Geri getirme
Bir parçaya ihtiyaç olursa ilgili klasörü eski yerine `git mv` ile taşımak yeterli:
- pipeline'lar → repo kökü, workflow'lar → `.github/workflows/`, seri verileri → `series_data/`.
- Eski pipeline'ları çalıştırmak için ayrıca `core/config.py`'daki `CHANNEL_NAMES`/kanal
  config'lerinin hâlâ durduğunu bil (core'a dokunulmadı).
