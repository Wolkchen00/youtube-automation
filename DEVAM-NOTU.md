# DEVAM NOTU — 2026-07-02 AKŞAM güncellemesi (İhsan + Claude oturumu)

> ÖNCEKİ bekleyen karar ÇÖZÜLDÜ: İhsan yeni seri olarak **Room 408**'i seçti.
> Seri kuruldu, push edildi (`e4351b5`). Ayrıca İhsan kararıyla motora
> **GÜNDE-1 ÜRETİM TAVANI** eklendi — artık cron her gün TEK seri üretir.

---

## 1) YENİ DURUM — Room 408 (sentinal_ihsan) CANLI

- **Seri:** `series_data/room-408/` — 5 bölümlük otel hayalet-gerilimi ("film tadında").
  Halden Grand Oteli; 30 yıldır mühürlü 408 odasından her gece 03:00'te resepsiyona
  telefon geliyor; yeni gece memuru Deniz Aksoy'a tek kural: ASLA cevap verme.
  Bölümler: 1 Never Answer 408 · 2 It Rang Twice · 3 The Fourth Floor ·
  4 The Guest Who Never Left · 5 Check-Out. Her bölüm ~52-56 sn, 6 çekim,
  cliffhanger sonlu; hook_teaser + micro_trim 0.25 + audio_smooth + music;
  anlatım `sentinal_ihsan` (Charon, kısık/gergin); KONUŞAN İNSAN YOK (filtre riski yok).
- Referanslar HAZIR ve bible'a gömülü (8 görsel ImgBB + 2 karakter Omni kaydı:
  Deniz `eb560ec1...`, Yusuf `7c80724c...`). Kurulum ~40 kredi yedi.
- `status=active`, `priority=1`, `publish_mode=auto`, profil `sentinalihsandaily`.
- **Part 1 YARIN (03 Tem) 14:30 UTC cron'da üretilip yayınlanacak.** Bugün yayın
  yapılmadı (İhsan kuralı korundu).

## 2) MOTOR DEĞİŞİKLİĞİ — Günde-1 üretim tavanı (İhsan kararı, 2026-07-02)

- İhsan: "3 seri değil sadece 1 seri; günde 1 üretilip paylaşılsın; diğer seriler
  sonraki günlerde otomatik aksın."
- `series_runner.run_all` artık aktif serileri `series.json["priority"]` ile sıralar
  (küçük=önce, eşitlikte slug) ve **yalnız İLK seriyi** üretir+yayınlar. Biten seri
  listeden düşünce ertesi gün sıradaki OTOMATIK devreye girer. Üretim başarısız
  olursa başka seriye GEÇİLMEZ (çifte kredi olmasın); ertesi gün aynı seri
  kaldığı çekimden devam eder (idempotent).
- `--series <slug>` (workflow_dispatch) tavandan etkilenmez — elle tek seri koşulabilir.
- **Mevcut sıra:** room-408 (p1-5, ~5 gün) → night-shift (priority=2, p2-5, ~4 gün)
  → infinite-trip (priority yok=100, oto-ikmalle sonsuz, sıra ona gelince günlük).
- `SeriesMeta.priority` eklendi (`series/series_meta.py`). infinite-trip dosyalarına
  DOKUNULMADI (paralel oturum alanı) — varsayılan 100 ile kuyruğun sonunda.

## 3) KREDİ / MANUEL İŞLER

- Bakiye: **4.261** (2026-07-02 21:57 UTC). Room 408 bölümü ~670-900 kredi →
  5 bölüm ≈ 3.400-4.500: bakiye Room 408'i ANCA karşılar. night-shift'in sırası
  gelmeden (≈5-6 gün içinde) **Kie'ye kredi yüklenmeli** (night-shift ~1.518/bölüm).
- İhsan manuel: YouTube Studio "altered/synthetic content" kanal varsayılanı; Kie kredi.

## 4) DOKUNMA — paralel oturumun alanı (değişmedi)

`series/replenish.py`, `series_data/infinite-trip/*` başka oturumun işi; commit'lerken
STAGE'leme. NOT: `run_all` günde-1 tavanı replenish'i etkilemez (her koşuda yine çağrılır,
Gemini plan yazımı kredisizdir) — sadece infinite-trip'in ÜRETİM sırası kuyruk sonuna geçti.

## 5) YEDEKTE — the-sleepwalkers (draft)

Dedektif hikâyesi taslağı (`series_data/the-sleepwalkers/`, status=draft, git'e girmedi,
3 referans üretilmiş durumda) İLERİDE kullanılabilir: Room 408 bitince aktive etmek
istersen `status: "active"` + `priority: 2` yap, kalan referansları `setup-refs` ile
tamamla, commit — sıraya kendiliğinden girer.

## 6) HIZLI YOLLAR

- Repo: `C:\Users\ihsan\Desktop\Antigravity\Projects\Youtube` (Wolkchen00/youtube-automation,
  cron `.github/workflows/series.yml` 14:30 UTC — makine saati PDT'dir, UTC-7!)
- Seri durumları: `series_data/<slug>/series.json` · loglar: Actions artifacts +
  `series_data/<slug>/series_log.csv` · kredi: `python -m series.cli credit` (venv: `.venv`)
- Kanal profilleri: sentinal_ihsan→`sentinalihsandaily`, aimagine/infinite-trip→`Youtube`

---

## 7) YENİ — KANAL KLASÖRLERİ (2026-07-18, İhsan kararı)

Seriler artık repo kökünde KANAL klasörlerinde: `sentinal_ihsan/`, `aimagine/`,
`shadowedhistory/` taşındı; motor (`series/bible.py: data_dir/all_series_dirs`)
hem kanal klasörlerini hem eski `series_data/`'yı tanır, workflow'lar beş klasörü
de commit'ler. **GALACTIC serileri (`series_data/planetfall`, `series_data/ava-voyage`)
BİLEREK taşınmadı** — galactic üzerinde çalışan oturum işini bitirince
`git mv` ile `galactic_experience/` altına alacak. Detay: `KANAL_KLASORLERI.md`.
