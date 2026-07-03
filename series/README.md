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

## 4K master (opt-in: `bible.series.upscale`)
```json
"upscale": {"enabled": true, "factor": "2", "provider": "topaz"}
```
- Final video (kanca dahil her şey bittikten sonra) **×2 büyütülür**: 1080x1920 → **2160x3840**.
  YouTube 4K bitrate merdivenine girer → izleyiciye belirgin daha temiz görüntü + "4K" rozeti.
- `provider: "topaz"` (varsayılan) — Kie `topaz/video-upscale`, kareyi yeniden inşa eder
  (gerçek detay). **Ölçülen maliyet ~8 kredi/sn** (2026-07-03: 4sn=32 kredi → 40sn ≈ 320 kredi).
  Akış: final → Kie dosya deposu (`kieai.redpandaai.co`, 3 gün) → görev → indir.
  >50MB girdi otomatik bitrate-kapaklı kopyayla gönderilir; ~100Mbps çıktı ~9.5Mbps'e
  normalize edilir (Upload-Post ~80MB limiti).
- `provider: "lanczos"` — bedava yerel ffmpeg ×2 (detay sentezlemez ama YouTube'un 4K
  encode kazancını yine tetikler). Topaz başarısız olursa da otomatik bu yola düşülür.
- **IG/TikTok her durumda 1080p alır** (`episodes/epNN/delivery_1080.mp4`) — iki platform
  da videoyu zaten 1080p'ye yeniden kodluyor; 4K yalnız YouTube'a gider.
- Hiçbir yol çalışmazsa 1080p yayınlanır — yayın durmaz (best-effort).

## Notlar
- Üretim **Kie kredisi harcar** (Omni ücretli). Gerçek maliyet API'den (`creditsConsumed`)
  okunur ve rapora yazılır. Kurulum/dry-run ücretsizdir.
- Format dikey **9:16**, çözünürlük **1080p** (720p ile aynı fiyat).
- Çok-konuşmacılı sahnelerde sesin doğru eşlenmesi için çekim başına ≤2-3 konuşmacı tutun.
