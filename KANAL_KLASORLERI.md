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
│   ├── the-vast/           (aktif)
│   ├── infinite-trip/  the-drift/
├── galactic_experience/  # profil: galacticexperimet — HENÜZ BOŞ, aşağıya bak
├── shadowedhistory/      # profil: shad0wedhistory
│   ├── footnotes/          (aktif)
│   ├── drowned-history/  secrets-anatolia/
├── series_data/          # ESKİ konum — sadece galactic serileri kaldı
│   ├── planetfall/  ava-voyage/
└── core/ series/ .github/ output/ ...   # motor (dokunma)
```

## Motor iki konumu da tanır

`series/bible.py` → `data_dir(slug)` önce kanal klasörlerinde, sonra
`series_data/` içinde arar; `all_series_dirs()` hepsini tarar. Yani bir seri
klasörünü `git mv` ile kanal klasörüne taşımak YETERLİDİR — başka kod
değişikliği gerekmez. Workflow'lar (`git add`) beş klasörü de commit'ler.

Yeni seri kurulumu varsayılan olarak `series_data/` altında açılır; kurulum
bitince ilgili kanal klasörüne `git mv` ile alın.

## GALACTIC TAŞIMASI — paralel oturuma not

`planetfall` (aktif, 12/15) ve `ava-voyage` şu an galactic üzerinde çalışan
oturum yüzünden BİLEREK taşınmadı (İhsan kararı: "galactic'i en son taşıyın").
Galactic işin bitince şunu çalıştır ve commit'le:

```
git mv series_data/planetfall  galactic_experience/planetfall
git mv series_data/ava-voyage  galactic_experience/ava-voyage
```

Taşıma sonrası `series_data/` boşalır ve silinebilir (git boş klasörü zaten
izlemez). İSTERSEN `series/bible.py` içindeki `SERIES_DATA_DIR` geriye-uyum
kodu da kalabilir — zararı yok, yeni seri kurulumunda hâlâ kullanılıyor.
