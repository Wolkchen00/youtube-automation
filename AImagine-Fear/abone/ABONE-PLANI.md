# aimagine abone (Instagram Subscriptions) plani

29 Ekim 2026. Abonelik acildi, icerik yokken 1 abone geldi (ucretsiz denemede).
Hedef: denemedeki aboneyi tutmak, ilk odeyen aboneleri kazanmak. Kural: abone
icerigi neredeyse BEDAVA olmali, cunku her ek Seedance videosu ~615 kredi (~3 dolar)
ve 1 aboneyle bu donmez.

## Ne paylasilir (maliyete gore)

**Bedava, hemen (her gun uretilen isin yan urunu):**
1. **Hangi baslangic?** Her rotanin ilk karesi icin iki aday uretiliyor
   (`out/<slug>/yuruyus_aday*.png`), biri secilir. Aboneye ikisi A/B olarak sorulur,
   ertesi gun cevap: "yayindaki B idi". Hikaye + anket cikartmasi.
2. **Nasil yapildi, saniye saniye.** Tutan bir videonun 6 karesi + tek satir not.
   Karusel, yalniz abonelere.
3. **Siradaki yolculugu abone secer.** Rota stokundan iki yer, abone anketi. Kazanan
   ertesi gunun herkese acik videosu olur ve caption'a "Chosen by subscribers" eklenir.
   Bu ayni zamanda herkese acik akista abonelik reklamidir.
4. **Yapay zeka hatalari (blooper).** Bozuk bacak, aynali yazi, yanlis yerde yanardag
   gibi elenen uretimler. Komik ve bize ozel.

**Ucuz, abone 5'i gecince (haftada 1 ek uretim, ~3 dolar):**
5. **Haftanin uzun yolculugu.** 30 sn iki parcali surum, yalniz abonelere.
   30 sn KURALI gecerli: korku basladiktan sonra ikinci parca aydinlik acilamaz.

**Ikinci tur (29 Ekim, Ihsan "insanlari iceri cekmemiz lazim"):**

Olculen: IG yorumlari, 8 reel, 159 yorum (giris yapmis tarayici, media/comments).
En cok begenilen yorumlarin neredeyse hepsi RUYA: Taipei "The types of dream I'm
having" 12.748 begeni, Arapca "ikindi uykusunda ruyalarim" 6.018, Burj "POV: How my
dreams be like" 4.687; ayrica "I wish that was real" 2.371, "I hate that its ai cause it
look so fun". "Hangi uygulama / prompt" soran yorum YOK: kitle yapay zeka ureticisi
degil, genis ve cok dilli (Arapca, Portekizce, Tayca, Endonezce). Afet videolarinda
yorum cok az (4-10). Abone teklifi teknik degil, duygusal olmali.

Kural: abone icerigi disaridan gorunmezse kimseyi iceri cekmez. Her teklifin herkese
acik akista bir PENCERESI olmali.

A. **ONERILEN: "Ruyani gonder, kaydiralim."** Abone tek cumleyle ruyasini yazar
   ("Istanbul'un ustunde pamuk sekeri bulutlarin icinden kayiyorum"). Haftada biri
   secilir, video olur. Herkese acik caption: "This was a subscriber's dream. Send me
   yours." Pencere: herkese acik video. ~615 kredi/hafta.
B. **"Adin kaydirakta."** Her gunun herkese acik videosunda bir abonenin adi cam
   yolda ya da gokyuzunde yazar; caption'da tesekkur. Ek uretim YOK, ilk kareye yazilir.
   Ayni zamanda her gun farkli ilk kare (tekrar algisina karsi). Yazi bozulabilir, ilk
   kare gozle kontrol. Atina testi okunmadan BASLAMAZ.
C. Asagidaki Part 2 (7) abonenin KALMASI icin, cekmek icin degil.

**30 Ekim Ihsan kararlari:**
- A (ruya) BEKLER: 10-20 abone olunca acilir, insanlar sirayla istesin, deger kazansin.
  Tek aboneye mesaj atilmadi (gerek kalmadi; zaten Chrome'daki hesap aimagine degil).
- B ABONE DEGIL TAKIPCI icin: "Takip et, adini yorum yaz, sonraki kaydirakta senin adin."
  Tek deneme, tutarsa devam.

**30 Ekim Ihsan duzeltmesi (gecerli olan bu):** tek ad DEGIL. "NEW FOLLOWERS" basligi
ve altinda 10-20 yeni takipcinin adi; ilk 3 saniyede slide'in zemininde, kadin kayarken
de gorunsun. Gerekce: birden fazla ad = herkes "benim adim da cikar" der, daha cok takip.
- Adlar: aimagine357 takipci listesinin ilk sayfasi (Instagram'in en yeni sirasi), 30 Ekim.
  Okunakli Latin adi olan 12 kisi, yalniz ad: Ange, Edgar, Michael, Dave, Bilal, Maria,
  Bella, Helia, Fernanda, Ashok, Pallavi, George. Isletme ve yapay zeka sayfalari alinmadi.
- Gorsel: nano-banana listeyi iki kez yazdi (slide agzi + yuruyus yolu); yalniz slide
  agzindaki parca orijinal karenin ustune maskeyle kondu. 12 ad yakindan kontrol edildi.
- Video 30 Ekim'de elle uretildi (gunluk.py --yayinlama, 627 kredi). Kare kare: kazili
  liste 0-0,79 sn net, ama kadin 1. saniyede oturuyor ve Seedance listeyi 20. karede
  (0,83 sn) birakiyor. Ihsan 3 sn + kayarken istedi: ayni liste 20. karede ayni yerde
  devralinip yukari suzulur, 3,2 sn'ye kadar ekranda kalir, soner (ffmpeg katmani,
  Arial Bold, beyaz + isik). Ust uste binen kare yok. Gerisi: Eyfel, bulut, firtina,
  dev beyaz dolu duvari, karanlik son; bacaklarda hafif pembe cizgi artefakti.
- `hazir/paris-eyfel-dolu.mp4` + takvim 2026-10-31: CI o gun uretmez, bunu yayinlar
  (YouTube, Instagram, TikTok), ilk yorum ISIM_KAYDIRAK.json'dan.
- Devam ederse: Seedance kazili adi ~0,8 sn tutuyor; ayni katman yontemi her gun
  kullanilir (kazi + devralma). Ad listesi her gun takipci listesinin ilk sayfasindan
  ve "comment your name" yorumlarindan.

Asagidaki MIGUEL tasarimi bunun yerine gecti (tarihce):

**B denemesi (ilk tasarim, iptal): 31 Ekim Paris, ad MIGUEL** (@miguelangel_blancog,
Giza ve Roma'ya tekrar tekrar "Excelente video" yazan takipci).
- Ad slide agzinin seffaf zeminine kazili, beyaz parlak. 4 gorsel denendi (~64 kredi):
  yuruyus yoluna yazilinca bacak "G"yi kapatti ("MIUEL"); slide agzinda tek ve tam okunan
  secildi -> `ilk_kare/paris-eyfel-dolu.jpg` (eski onayli gorsel git gecmisinde).
- Rota OPENING STATE + [0-2] + [2-4] adi anar (Seedance silmesin). Kanon NEGATIVE
  "NO on-screen text" diyor; ad sahnenin parcasi olarak yazildi. Risk: video adi
  bozabilir, yayindan sonra ilk 2 sn gozle bakilacak.
- Caption "You're" ile baslar (kural), tesekkur + cagri ikinci paragraf. Ilk yorum
  `canon/ISIM_KAYDIRAK.json`'dan: "Comment your name 👇 The next slide could carry it."
- Olcut (48 saat): ad yazan yorum sayisi. Son reel'lerde yorum 0-10 arasi. 15+ ad
  yorumu = TUTTU, devam (her gun bir takipci adi). 5'ten az = birakilir.
  Ek: takipci 29 Ekim 16,3K, gunluk artisa bak.

**Ilk tur:**
7. **"Kapinin obur tarafi" (Part 2).** Herkese acik video karanlikta biter;
   abone devamini gorur: kasirganin gozunun ici, kraterin ici, selin alti. Herkese
   acik videonun SON karesinden baslar, korku surer, aydinliga DONMEZ (30 sn kurali).
   Her herkese acik video aboneligin reklami olur: caption'a tek satir
   "Part 2 is for subscribers." Bu satir Atina testi (30 Ekim) okunana kadar EKLENMEZ,
   iki degisken ayni anda degismesin. ~615 kredi, haftada 1.
8. **Yasak rotalar.** Kimsenin gidemeyecegi yerler: Mariana Cukuru dibine cam tup,
   Bermuda Seytan Ucgeni, Antarktika buzul yarigi, Buyuk Piramit'in kapali odasi,
   kasirganin gozu. Herkese acik rota stogunu harcamaz. ~615 kredi.

**Abone 20'yi gecince:**
6. **Senin sehrin.** Ayda bir, bir abonenin istedigi yer, caption'da adiyla.

## YAPILMAYACAK

- Herkese acik reel'in AYNISINI abonelere once reel olarak koymak. Ayni dosyanin iki
  kez reel olmasi tekrar sayilabilir (29 Ekim olcumu: ilk 2 saniyesi onceki videoyla
  ayni olan tekrarlar 6/6 coktu). Erken erisim gerekiyorsa hikayede 5 sn'lik parca.

## Paylasma

Abonelere ozel gonderi Instagram uygulamasindan elle atilir (yukleme servisi bu
secenegi desteklemiyor). Hazir dosyalar `abone/<tarih>/` altinda, metinleri asagida.

### 2026-10-30 paketi

- `1_hikaye_hangi_baslangic.jpg`: Hikaye, "Yalnizca aboneler" secili. Alttaki bosluga
  anket cikartmasi: secenekler `A` ve `B`. Ertesi gun cevap hikayesi: "It was B. B went
  public and got 154K views."
- `2_karusel_1_kapak.jpg`, `2_karusel_2.jpg`, `2_karusel_3.jpg`: abonelere ozel gonderi.
  Metin: "How a 154K ride is built, second by second. Subscribers see the making of
  every ride. Tell me which landmark should be next."
