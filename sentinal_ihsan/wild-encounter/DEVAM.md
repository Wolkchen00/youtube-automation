# DEVAM: wild-encounter (11 Eylul 2026, 15:20 PDT)

Once oku: `DOKTRIN.md` (en ustte GUNCEL FORMAT, altta olculmus dersler) ve repo
kokunde `RF-ISSUES-WILD-ENCOUNTER.md`.

## Bugun ne oldu

- **ep05** (ahtapot) ve **ep06** (timsah) uc platformda yayinda.
  ep06: https://www.youtube.com/watch?v=TiJ8Uv7vhzs ,
  https://www.instagram.com/reel/DdKF60UHRsp/ ,
  https://www.tiktok.com/@sentinal.ihsan.daily/video/7684351502235831566
  ep06 maliyeti 436 kredi (~$2,18); 105'i QC'nin yanlis "gomulu yazi" retinden.
  Olcum (15:00 PDT): ep05 12. saat 1.657 izlenme / 9 begeni; ep06 3. saat 883 / 13.
- **Rock 1-5 + Codex incelemesi (SPM 2b)** main'de ve push'li (c99d80b):
  muzik yatagi kalkti (master muziksiz govdede -14 LUFS), prompt ve QC metinleri
  plato-3x8'e hizalandi, yaratik ve set referans gorselleriyle capalaniyor,
  arsivlemenin kirdigi 60 test fixture'a tasindi, seri gunluk otomasyona baglandi.
  Tam takim: 1463 passed, 0 failed.
- **Seri artik GUNLUK OTOMATIK YAYINDA**: `.github/workflows/wild-encounter.yml`,
  18:30 UTC = 11:30 PDT. GitHub serididi tanidi ("Wild Encounter Daily", aktif).
  Kuyrukta part07-11: peygamber devesi, kopekbaligi (okyanus tanki), boz ayi,
  baykus, komodo ejderi.

## Yarin ILK IS: ilk bulut kosusunu denetle (12 Eylul 11:30 PDT sonrasi)

1. Kosu: `gh run list --workflow=wild-encounter.yml` ve son kosunun loglari.
2. Videoyu KENDIN izle (log "basarili" demesi kanit degil):
   `output/series/wild-encounter/episodes/ep07/` icindeki master dosya; 1,5 fps
   kontakt sayfasi cikar, uc vurusu ve seti kare kare dogrula.
3. Ses: `-14 +/- 1 LUFS`, true peak `<= -1 dBTP`; muzik yatagi OLMAMALI.
4. Yeni kapi: `require_continuity` YANLIS RET verdi mi? `qc_log.jsonl` icinde ep7
   "review" olaylarina bak. Iki regen yakip bolum dustuyse kapiyi gozden gecir
   (gerekce bible.series.qc.continuity_note'ta).
5. Maliyet: `credits_ledger.json` -> `wild-encounter:7` (~436 bekleniyor).
   Bakiye: `python -c "from core.kie_api import check_credit; print(check_credit())"`.

## Bekleyen kararlar ve isler

- **KREDI (Ihsan):** bakiye ~1.087 kredi = ~2 bolum. Gunluk tempo ayda ~13.000
  kredi (~$65). Bitince kosu kredi kapisinda KIRMIZI durur, Telegram'a hata gider.
- ep05 ve ep06 icin 24 saatlik olcum: YouTube Data API v3 kullan; **yt-dlp artik
  YouTube'da bot kontrolune takiliyor** (TikTok'ta calisiyor).
- `RF-ISSUES-WILD-ENCOUNTER.md` sirasi: QC "gomulu yazi" yanlis alarmi (regen
  oncesi tam cozunurlukte ikinci bakis), capa odeme penceresi, yayin-durumu
  yaziminin yutulmasi, `require_object_match` karari (ep07 olculdukten sonra).
- Gunluk beyin hala `unnatural-lab` uzerinden kurulu; wild-encounter'a
  gecirilmeli. DIKKAT: `gunluk_beyin/kanallarimiz.md` baska bir oturumda kirli.

## Tuzaklar (olculdu)

- **DOKTRIN.md degisince** kuyruktaki planlarin doktrin damgasi bayatlar ve uretim
  "legacy plan doktrin damgasi..." diyerek durur. Doktrine dokunduysan
  `python -m series.replenish --series wild-encounter` ile kuyrugu yeniden yazdir.
- Uretim logundaki "N kredi" satiri SERI toplamidir, bolum maliyeti degil;
  bolum maliyeti `credits_ledger.json`'da.
- Codex oturumu (plan + insa incelemesi): thread
  `01a09164-cb78-7ae3-aad2-81fcf43a42d1`; plan/karar kaydi repo kokunde
  `RF-PLAN-WILD-ENCOUNTER.md` ve `RF-SAME-PAGE-LOG-WILD-ENCOUNTER.md`.
