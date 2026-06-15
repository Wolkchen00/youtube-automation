# series — Gemini Omni Mini-Dizi Motoru

Kie AI **Gemini Omni Video** ile tutarlı karakter/ortam/ses kullanarak ardışık klipler
üretir, birleştirir → **bölüm**; bölümleri birleştirir → **dizi serisi**.

Mevcut `core/` altyapısını yeniden kullanır (kie_api, imgbb, ffmpeg_tools, cost_tracker).

## Nasıl çalışır (Claude yönetir)
1. **İhsan senaryoyu verir** (sohbette).
2. **Claude iki dosya yazar:**
   - `output/series/<slug>/bible/bible.json` — karakterler, ortamlar, aksesuarlar, sanat tarzı, sesler
   - `output/series/<slug>/episode_plan.json` — çekim listesi (her çekim: prompt, süre, karakter, ses, ortam, aksesuar)
   Şablonlar: `series/templates/bible.example.json`, `series/templates/episode_plan.example.json`
3. **Referanslar hazırlanır** (görseller üret/yükle + karakter & ses kaydı):
   `python -m series.cli setup-refs <slug>`
4. **Bölüm üretilir** (klipler + birleştirme + rapor):
   `python -m series.cli produce <slug> output/series/<slug>/episode_plan.json`

## Komutlar
```
python -m series.cli                       # interaktif menü (İhsan için)
python -m series.cli credit                # Kie kredi bakiyesi (ücretsiz)
python -m series.cli voices [erkek|kadın]  # preset ses tablosu
python -m series.cli list                  # diziler
python -m series.cli setup-refs <slug> [--dry-run]
python -m series.cli produce <slug> <plan.json> [--dry-run]
python -m series.cli cost-report <slug>
```
`--dry-run`: hiçbir API/kredi harcamadan adımları ve istek gövdelerini gösterir.

## Referans → Omni eşlemesi
| Referans | Omni özelliği |
|----------|---------------|
| Karakter (görsel + görünüm + ses) | `omni/character/create` → `character_id` |
| Ortam | referans görsel → `image_urls` |
| Aksesuar | referans görsel → `image_urls` |
| Sanat tarzı | her prompt'a eklenen stil ön-metni |
| Süre | çekim başına 4/6/8/10 sn |

**Kota:** (görsel) + (video×2) + (karakter) ≤ 7 / istek.
**Sesler:** çekim başına ≤ 3 `audio_ids`.

## Çıktılar
```
output/series/<slug>/
  bible/bible.json + characters/ environments/ props/ style/
  episodes/ep01/shots/shot_01.mp4 ...  ep01.mp4   (birleşik bölüm)
  series_log.csv / series_log.xlsx                 (üretim raporu)
```

## Notlar
- Üretim **Kie kredisi harcar** (Omni ücretli). Gerçek maliyet API'den (`creditsConsumed`)
  okunur ve rapora yazılır. Kurulum/dry-run ücretsizdir.
- Format dikey **9:16**, çözünürlük **1080p** (720p ile aynı fiyat).
- Çok-konuşmacılı sahnelerde sesin doğru eşlenmesi için çekim başına ≤2-3 konuşmacı tutun.
