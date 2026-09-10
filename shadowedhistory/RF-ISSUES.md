# RF-ISSUES , flashpoints (bu kosuda ele alinmayanlar)

Tarih: 10 Eylul 2026 (Los Angeles)

## Ertelendi

- **[YUKSEK] Konu tanınırligi hipotezi kanitlanmadi.** Rapor "tanınır konu kazaniyor"
  diyor ve iki ornege dayaniyor. 29 bolumluk tam veride hipotez zayif: Gladiators
  (0 izlenme), "Cleopatra Was Closer To The Moon Landing" (0), "Cleopatra Ruled Without
  Translators" (6) , ucu de son derece tanınır konular ve dip yaptilar. Buna karsilik
  "Nintendo Made Playing Cards" (795) ve "Romans Used Urine For Laundry" (105) tanınır
  ama beklenmedik. Ayirici degisken tanınırlik degil, muhtemelen **beklenmediklik**.
  Yapilacak is: rapordaki 4+4 A/B testi degil, once 29 bolumun baslik kalibini
  siniflandirip (kalip: "The Real Reason X", "X: Fact Or Ancient Propaganda?",
  "How X Y'd In YYYY!", "Isim: Sifat") izlenmeye karsi cizmek. `published.json` +
  yt-dlp verisi zaten elde; olcum bir kosuluk is.

- **[ORTA] "Fact Or Ancient Propaganda?" kalibi tukenmis olabilir.** Uc ornek:
  Gladiators 0, Colosseum 143, Great Wall 25, Great Fire Of London 23. Ayni kalip
  dort kez kullanilmis, medyan 24. Kalip rotasyonu `series.json` `title_patterns`
  benzeri bir alanla sinirlandirilabilir.

- **[ORTA] Kredi kaybi: final_reject sonrasi bolum yayinlaniyordu, artik yayinlanmayacak.**
  Rock 2 sonrasi bir cekim reddedilirse bolum dusecek ve o gun yayin olmayacak.
  Harcanan kredi geri gelmez (bkz. hafiza: Kie API idempotency yok). Alternatif:
  reddedilen cekimi ertesi kosuda yeni tohum/prompt ile yeniden uretip bolumu
  tamamlamak. Bu motor isi (`series/produce.py`), bu kosuda kapsam disi.

- **[DUSUK] 11. bolum hic yayinlanmamis.** `published.json` part 11'i icermiyor
  (1-10 ve 12-30 var). `plans/part11.json` mevcut. Sebep arastirilmadi.

- **[DUSUK] Instagram ve TikTok hic yayinlanmamis.** `series.json` `platforms`
  uc platform listeliyor; `published.json` icindeki 29 kaydin tamaminda
  `instagram: null`, `tiktok: null`. Kanal tek platformda calisiyor ama uc platform
  icin ayarli. Ayri bir is.

## Reddedildi (rapordaki madde, bu kosuda yapilmayacak)

- **"Baslik kartinin her videoda basildigini dogrula."** Dogrulandi: 35 planin
  35'inde de `title_card.title` dolu ve `bible.json` `title_card: true`. Yapilacak
  is yok, rock listesinden dusuruldu.

- **"Sifir kesmeli video birakma, tavan 4 saniye."** Kok neden kesme kurali degil,
  dusen cekim (Rock 2). Cekim dusmedigi surece her bolum zaten iki cekim / bir kesme
  tasiyor. Ayrica 15 saniyelik kova (tek kesme) kanalin en iyi kovasi , 4 saniyede
  bir kesme dayatmak calisan bicimden uzaklasmak olur.
