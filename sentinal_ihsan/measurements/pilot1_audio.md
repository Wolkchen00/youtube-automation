# PİLOT-1 (part22) ÖLÇÜM KANITLARI

Ölçen: Visionary (Claude Opus 5) · Tarih: 2026-08-27 · Makine: Windows 11, ffmpeg 8.0.1-full_build
(gyan.dev, gcc 15.2.0), Python 3.14.3. Ölçülen dosya:
`output/experiments/exp-2026-08-gerceklik/unnatural-lab-part22/ep22_narrated_music.mp4`
(22,293 sn; h264 1080x1920 30fps; aac 96 kHz stereo).

Bu dosya `PLAN_PILOT_SONRASI_v1.md` Bölüm 0'daki B1-B9 bulgularının ham kanıtıdır. Üreten koşunun
kendi raporu kanıt sayılmamıştır; her sayı burada yeniden koşulan komutlardan gelir.

---

## 1. Master loudness (B1)

```
ffmpeg -hide_banner -nostats -i ep22_narrated_music.mp4 -af ebur128=peak=true -f null -
```

```
Integrated loudness:
  I:         -24.5 LUFS
  Threshold: -34.7 LUFS
Loudness range:
  LRA:         8.3 LU
  Threshold: -44.7 LUFS
```

Sosyal platform normu ~-14 LUFS → **10,5 LU düşük master**.

## 2. amix `normalize` kontrollü deneyi (B1, kök i)

`core/ffmpeg_tools.mix_voiceover` filtre zinciri birebir taklit edildi (iki sinüs girdi, aynı
seviyeler, aynı amix parametreleri):

```
ffmpeg -y -f lavfi -i "sine=frequency=440:duration=3:sample_rate=48000" -c:a pcm_s16le a.wav
ffmpeg -y -f lavfi -i "sine=frequency=880:duration=3:sample_rate=48000" -c:a pcm_s16le b.wav

# üretimdeki hâli (normalize parametresi YOK -> ffmpeg varsayılanı 1)
ffmpeg -y -i a.wav -i b.wav -filter_complex \
  "[0:a]volume=0.5[bg];[1:a]volume=1.0[vo];[bg][vo]amix=inputs=2:duration=first:dropout_transition=2[out]" \
  -map "[out]" mix_default.wav

# önerilen hâli
ffmpeg -y -i a.wav -i b.wav -filter_complex \
  "[0:a]volume=0.5[bg];[1:a]volume=1.0[vo];[bg][vo]amix=inputs=2:duration=first:dropout_transition=2:normalize=0[out]" \
  -map "[out]" mix_n0.wav
```

| Ölçüm | Integrated |
|---|---|
| girdi A tek başına (volume 1.0) | -21,8 LUFS |
| amix, `normalize` varsayılan (üretimdeki hâl) | **-26,5 LUFS** |
| amix, `normalize=0` | **-20,4 LUFS** |

→ **6,1 LU sistematik kayıp**, doğrudan `normalize=0` eksikliğinden.

## 3. Katman doğrulaması: anlatım / native foley / müzik mikste mi? (Bölüm 0 "GEÇEN")

Yöntem: her varyant `-ac 1 -ar 8000 -f s16le` ile ham PCM'e çözüldü, 100 ms pencerelerde RMS zarfı
çıkarıldı (Python `array`, harici bağımlılık yok). Karşılaştırılan dosyalar: `ep22_raw.mp4` (yalnız
native), `ep22_narrated.mp4` (native+anlatım), `ep22_music.mp4` (native+müzik), `ep22_narrated_music.mp4`
(final), `narration.wav` (TTS), `bg_music.mp3` (yatak).

| Ölçüm | Sonuç | Yorum |
|---|---|---|
| genel RMS: final / raw / narrated / music | -29,99 / -27,23 / -31,66 / -25,76 dB | final -60 dB altı sessiz pencere: **0** |
| (final − müziksiz) zarfı ↔ TTS zarfı korelasyonu | **0,630** | anlatım mikste |
| konuşma pencerelerinde ortalama fark | -36,9 dB | konuşmasız pencerelerde -54,2 dB → **+17,2 dB** |
| final > narrated (müziksiz) olan pencere | **196 / 219** | müzik yatağı mikste |
| konuşmasız pencerelerde final ↔ raw korelasyonu | **0,709** | native foley mikste (ROCK 1 çalışıyor) |

**Uyarı (Codex tur-1 bulgusu, kabul edildi):** korelasyon kazançtan bağımsızdır; foley'in DUYULUR
seviyede olduğunu tek başına kanıtlamaz. `tools/audio_master_check.py` mutlak seviye eşiği de ölçecek.

## 4. Teslim zinciri sırası (ROCK A'nın "gerçek master noktası")

`series/produce.py` içinde ölçülen sıra:

```
1609  final_ep = work_dir / epNN.mp4
1613  final_ep = _post_process(...)        # anlatım (mix_voiceover) + müzik (mix_background_music)
1638  hook_teaser -> concatenate_simple    # ses YENİDEN KODLANIR
1665  title_card_overlay
1703  fact_captions_overlay
1713  final_ep = _upscale_master(...)      # yan ürün delivery_1080.mp4 (satır 504), dönüş 4K
1740  return final_ep
```

→ `_post_process` içine konacak bir master aşaması teaser/overlay/upscale sonrasını kapsamaz.

## 5. QC çağrı hacmi (B7, düzeltilmiş)

```
qc_log.jsonl, episode == 22
```

| Tarih | Olaylar |
|---|---|
| 2026-08-24 (pilotla ilgisiz artık) | review 2, regen 1 |
| 2026-08-26 (pilot koşusu) | **review 18, native_audio_review 18**, scene_cut_scan 15, regen 9, final_reject 4, qc_pass 4, qc_hold 1 |

`scene_cut_scan` kaydı Gemini değil yerel ffmpeg ölçümüdür (örnek kayıt alanları:
`threshold: 0.2, height: 270, count: 0, timestamps: [], status: "measured", gated: false`).
→ Loglanan gerçek Gemini çağrısı: **36**. Yeniden denemeler, yedek model çağrıları ve 429'lar
loglanmıyor; gerçek API deneme sayısı bilinmiyor (ROCK C bunu ölçülebilir yapar).

## 6. Kredi durumu (B8)

```
py -X utf8 -c "from dotenv import load_dotenv; load_dotenv(); from core import kie_api; print(kie_api.check_credit())"
2026-08-27 08:50 → 5999.0
```

Öncül planın ölçtüğü filo tüketimi ~1.550 kr/gün → **~4 günlük ömür**. Watchdog eşikleri 4.800 / 2.850.
Bake-off ön koşulu (≥15.000) karşılanmıyor. Pilot-1 harcaması `experiments_ledger.json`'a göre
**1.584 kr** (27 rezervasyon, `pilot` aşama tavanı 1.700 → kalan 116).

## 7. Görsel denetim (kare kanıtları)

Kareler `ep22_narrated_music.mp4` üzerinden çekildi (t = 0,05 / 15,2 / 21,0 sn):
ilk karede anomali okunuyor; mutfak yaşanmış; yüz yok; kahraman obje 4 çekimde aynı.
Bulgular B2 (anomali iç yapısı çekim 1/3/4'te farklı), B3 (çekim 3'te su limonun altından sızıp
tezgâhta birikiyor), B4 (birikinti çekim 4'te yok), B5 (çekim 4 daha yakın ve alçak açı) bu
karelerden okundu.
