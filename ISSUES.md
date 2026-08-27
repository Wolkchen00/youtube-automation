# ISSUES, AIMAGINE sabit-kare pivotu, ertelenenler

- [med] USTA için Kie referans-görsel / characterId kaydı (bible.characters): yüz/kıyafet
  tutarlılığını metin kilidinden görsel kilide yükseltir; ilk 25 bölüm ölçümünden sonra.
- [med] Şot 3→4 köprü deneyi (Codex tur-1 CLARIFY): dış cephenin son karesini şot 4'e ek
  REFERANS görsel (start-frame değil) olarak vermek iç/dış stil sürekliliğini
  güçlendirebilir; kanıtsız, ayrı A/B deneyi ister.
- [med] Sınır-ötesi (cross-shot) QC incelemesi (Codex tur-2): critic bugün tek klip inceler,
  çekim sınırındaki kompozisyon/stil kopmasını göremez; iki komşu klibin sınır karelerini
  birlikte inceleyen bir QC modu ayrı iştir.
- [med] Diegetik inşaat foley'i (çekiç, testere, matkap) müzik altına; Sentinal foley işiyle ortak.
- [low] `core/config.py` aimagine süre bandı {min:15, max:30}: seri hattı okumuyorsa bayat;
  legacy pipeline temizliğiyle birlikte ele alınır.
- [low] the-vast / the-drift emeklilik kararı (İhsan): auto_replenish.enabled hâlâ true,
  status paused; dosya düzeyi kapatma netleşmeli.
- [low] KANAL_ENTEGRASYON_PLANI_v2.md'deki aimagine doktrin özeti (24-32 sn + tek ödül)
  v2.0'dan sonra bayat kalır; plan dokümanı ayrı klasörde, İhsan onayıyla güncellenir.

## ROCK A (ses master) sonrası ertelenenler — 2026-08-27

- **[orta] Üretim yalnız LUFS/TP kapısı koşuyor.** `_verify_audio_master` teslimatı yalnız entegre
  loudness ve true-peak için doğruluyor; foley varlığı ve dinamik sıkışma kapıları
  `tools/audio_master_check.py` içinde, yani üretim yolunda DEĞİL. Foley'i gömülmüş bir bölüm
  bugün yayına çıkabilir (Seviye-10'da sabotaj dosyasıyla kanıtlandı: araç yakalıyor, üretim yakalamıyor).
  Öneri: pilot-2 penceresinde tam denetimi üretimde fail-closed koştur (premaster + referanslar
  zaten `produce.py` içinde mevcut).
- **[düşük] Yatak seviyesi 0.50 kapıya çok yakın.** Opt-in yolda foley/yatak marjı pilot malzemesinde
  6,195 dB, kapı 6,0 dB → 0,2 dB pay. Pilot-2 malzemesi biraz farklı gelirse araç FAIL raporlar.
  Öneri: pilot-2 ölçümünden sonra ya eşiği ya da yatak seviyesini seri bazlı ayarlanabilir yap.
- **[düşük] Opt-in seride upscale hatası artık `qc_hold` üretiyor.** Topaz dış servis ve kırılgan;
  bugün `unnatural-lab` için `upscale` kapalı olduğundan etkisiz, ama K-FILO yayılımında
  1080p teslimatı olan bir seriyi durdurabilir. Öneri: K-FILO öncesi "4K üretilemedi ama 1080p
  master doğrulandı" durumunu ayrı sınıflandır.
