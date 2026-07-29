# KANAL KLASÖRLERİ — repo yerleşimi (2026-07-18, İhsan kararı)

Her kanalın serileri repo kökünde KENDİ klasöründe durur; İhsan kanalları
buradan ayrı ayrı takip eder. Eski `series_data/` GEÇİŞ konumudur.

## Yapı

```
Youtube/
├── sentinal_ihsan/       # profil: sentinalihsandaily
│   ├── could-you-survive/  (aktif)
│   ├── night-archive/  night-shift/  room-408/  the-signal/  time-witness/
│   └── the-sleepwalkers/   (draft — git'e GİRMEZ, bilerek untracked)
├── aimagine/             # profil: Youtube
│   ├── from-scratch/       (aktif, approval)
│   ├── the-vast/           (paused)
│   ├── infinite-trip/  the-drift/
├── galactic_experience/  # profil: galacticexperimet
│   ├── event-horizon/      (aktif, approval)
│   ├── planetfall/         (paused, replenish kapalı)
│   └── ava-voyage/         (completed)
├── shadowedhistory/      # profil: shad0wedhistory
│   ├── flashpoints/        (aktif, approval)
│   ├── footnotes/          (paused)
│   ├── drowned-history/  secrets-anatolia/
├── series_data/          # boş; yeni seri kurulumunda geçici konum
└── core/ series/ .github/ output/ ...   # motor (dokunma)
```

## Motor iki konumu da tanır

`series/bible.py` → `data_dir(slug)` önce kanal klasörlerinde, sonra
`series_data/` içinde arar; `all_series_dirs()` hepsini tarar. Yani bir seri
klasörünü `git mv` ile kanal klasörüne taşımak YETERLİDİR — başka kod
değişikliği gerekmez. Workflow'lar (`git add`) beş klasörü de commit'ler.

Yeni seri kurulumu varsayılan olarak `series_data/` altında açılır; kurulum
bitince ilgili kanal klasörüne `git mv` ile alın.

## GALACTIC TAŞIMASI

2026-07-29 tarihinde `planetfall` ve `ava-voyage`, `git mv` ile
`galactic_experience/` altına taşındı. `series_data/` artık boştur ve yeni seri
kurulumunda geçici konum olarak kalır. `series/bible.py` içindeki geriye uyum
kodu bu kurulum akışı için korunur.
