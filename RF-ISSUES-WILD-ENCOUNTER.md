# RF-ISSUES-WILD-ENCOUNTER

State of the Company, 2026-09-11. Her madde tek satir, etki yuksek/orta/dusuk.
Bu turun rocklari RF-PLAN-WILD-ENCOUNTER.md'de; burada kalanlar ertelendi.

## Bu tura alinanlar (Ihsan secti)

- [yuksek] 60 test arsivleme yuzunden kirik; canli kanal config'ini fixture sayiyor -> ROCK 1
- [yuksek] Muzik yatagi ep05'te ortam sesini basti; Ihsan kaldirilmasini istedi -> ROCK 2
- [yuksek] art_style her cekim promptuna "real outdoor, handheld, hybrid" ekliyor, format stüdyo seti -> ROCK 3
- [yuksek] QC notu 3. vurusu "kapak" diye tarif ediyor, part06 agizdan cikis; dogru video yanlis sebeple reddedilir -> ROCK 3
- [orta] brief, logline, title_patterns, bayat bible notlari eski 2x8 kovalama formatini anlatiyor -> ROCK 3
- [orta] Yaratigin kimlik capasi yok; uc cekim boyunca kayabilir -> ROCK 4
- [orta] Hicbir ortamda referans gorsel yok (ref_image_url null) -> ROCK 4

## Ertelenenler

- [orta] require_continuity / require_object_match tek-set formatta yeniden acilabilir; ep06 olculmeden acilmaz (yanlis ret = kredi)
- [orta] native_audio_review icinde muzigi (modelin kendi urettigi) ayri bir ret sebebi yapmak; once ep06'da olc
- [orta] families listesi melez donemin kategorileri; BTS formatina gore yeniden adlandirma
- [dusuk] alert_outbox Telegram'a gitmiyor (TELEGRAM_BOT_TOKEN yerelde yok); bulutta var mi kontrol
- [dusuk] IG izlenme olcumu (ig_kaz.py, 12 cagrida 429) ep05 icin 24. saatte
- [dusuk] series.json `parts` bos ve `next_part` 1: yayinlanan bolumler kayit disi (bkz. hafiza: yayindan once kanali kontrol et)
- [orta] Yaratigi Kie'de karakter olarak kaydetmek (register_character): insan olmayan ozne ve ucret dogrulanmadi, idempotency yok. Deney: ep06'nin yaratik referans gorseliyle TEK kayit cagrisi, oncesi/sonrasi bakiye olcumu, yaniti kaydet; kabul ederse ayri bir cekimle gorsel-yalniz vs gorsel+kimlik karsilastirmasi. (SPM tur 1)
- [dusuk] Testlerin izlenen series_data/advers/hold_log.jsonl dosyasina yazmasi ana agacta da kirlilik biriktiriyor (ana agacta su an M). Rock 1 test tarafini duzeltir; ana agactaki birikmis satirlar ayrica temizlenmeli.
