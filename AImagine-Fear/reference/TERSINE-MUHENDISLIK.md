# fearvisionofficiel, tersine muhendislik raporu

Tarih: 2026-09-03. Iki kaynak video indirildi, kare kare ve ses seviyesi olcumu ile incelendi.
Bu dosya tahmin degil, olculen sey. Her iddianin yaninda nasil olculdugu yaziyor.

## Kaynaklar

| | Video 1 | Video 2 |
|---|---|---|
| URL | instagram.com/reel/DcynI6Oj8rA/ | instagram.com/reel/Dcv7cfVDQi0/ |
| Yayin | 2026-09-02 | 2026-09-01 |
| Begeni / yorum | 182.827 / 633 | (alinmadi) |
| Iddia edilen mekan | STRAT Tower, Las Vegas | CN Tower, Toronto |
| Rota dosyasi | routes/vegas-strat-blue-rain.md | routes/toronto-cn-red-dusk.md |
| Kontakt sayfasi | reference/kaynak-01-vegas-kontakt.png | reference/kaynak-02-toronto-kontakt.png |

## Olculen teknik kimlik

`ffprobe` ile:

- Ikisi de **20,053 saniye**, **1080x1920**, **30 fps**, ses 48 kHz stereo.
- Sure ikisinde de **tamamen ayni**. Bu tesaduf degil, sabit bir kalip.

`ffmpeg` sahne kesme dedektoru (esik 0,25) ile:

- **Video 2: sifir sahne kesmesi.** 20 saniye boyunca tek kesintisiz cekim.
- Video 1: 7,4-8,1 arasi ve 11,63'te tetikleme var. Karelere bakildiginda bunlarin kesme
  degil **beyaz su patlamasi** ve **binalar arasina giris** oldugu gorulduı; kadraj
  devamli, bacaklar yerinden oynamiyor.

**Sonuc: format tek kesintisiz cekim.** Iki klip birlestirilmiyor, kaynak tek promptla
tek video uretiyor. Bizim sistem de oyle kurgulandi.

## Olculen ses kimligi

`faster-whisper` (small) transkripti:

Video 1:
```
[ 0.00 -  4.00]  Oh my god. Look down.
[10.00 - 12.00]  This is insane!
[14.00 - 16.00]  (anlasilmayan panik bagirisi)
```

Video 2:
```
[ 0.60 -  2.60]  Oh my god
[ 8.52 - 13.32]  This is so high this is so high this is so high
```

`astats` RMS egrisi ile:

- Ses seviyesi Video 1'de t=0'da yaklasik **-33 dB**, t=10'da **-17,8 dB**, sonuna kadar
  orada kaliyor. Video 2'de -33 dB'den -17,6 dB'ye ayni sekilde tirmaniyor.
- **Egri hic dusmuyor, hic sessizlik yok, hic fade yok.** Muzik yok.
- Yani ses tasarimi da tek parca: hiz arttikca ruzgar ve su sesi monoton olarak buyuyor.
  Bu, kesme olmadiginin ikinci bagimsiz kaniti.

## Kare kare gorulen sahne mimarisi

Iki videoda da **ayni bes bolum**, ayni zamanlarda:

| Zaman | Bolum | Ne yapiyor |
|---|---|---|
| 0,0-2,5 | **Esik** | Hareket yok. Ciplak ayaklar cam zeminde, sehir ayaklarin altinda. Korku burada kuruluyor, harekette degil. |
| 2,5-5,0 | **Agza yurume** | Seffaf kaydirak agzi buyuyor. Yaklasma kesintisiz, hicbir yerde sicrama yok. |
| 5,0-10,0 | **Ilk dusus** | Ufuk kadrajin ustunden disari firlatiliyor. Ilk beyaz su patlamasi. |
| 10,0-15,0 | **Tirbuson** | Butun sehir bacaklarin etrafinda bir tam tur donuyor. En yuksek, en aciktaki an. |
| 15,0-20,0 | **Havuz** | Havuz seffaf zeminden onceden gorunuyor, buyuyor, carpma, su alti, yuzeye cikis. |

## Formulun tasidigi yedi kural

Kanali kopyalanabilir yapan sey bu yedi sey. Kanonda (canon/MASTER-BLOCK.md) hepsi
madde madde yazili.

1. **Yuz yok.** Hicbir karede yuz, sac, el, kol, govde yok. Sadece iki bacak, iki ciplak
   ayak, kadrajin alt ucte birinde, merkeze dogru daralarak.
2. **Balik gozu zorunlu.** Yaklasik 150 derece, ufuk gorunur sekilde **bukuluyor**. Bu,
   yukseklik hissini ureten sey. Not: bizim `stil_havuzu/kamera.json` balik gozunu
   yasakliyor cunku yuzu bozuyor. Burada **yuz olmadigi icin** yasak dusuyor; bu format
   balik gozunun guvenli oldugu tek yer.
3. **Kaydirak seffaf.** Ayaklarin altindan bosluk ve sehir surekli gorunuyor. Korkuyu
   ureten sey kaydiragin kendisi degil, **altinin gorunmesi**.
4. **Tek doygun renk kadraji yonetiyor.** Video 1 camgobegi mavi, Video 2 kirmizi. Renk
   kaydiragin kenar seridinden geliyor, sonradan filtreyle degil.
5. **Kamera govdeye civatali.** Viraj alirken bacaklar kadrajda yerinde duruyor, **dunya**
   bacaklarin etrafinda donuyor. Gimbal yok, yumusatma yok.
6. **Yaklasma kurali.** Her donme, her bina, havuz dahil, ulasilmadan once ileride
   gorunuyor ve kesintisiz buyuyor. Hicbir sey aniden belirmiyor. Sacmaligi oldüren kural
   bu.
7. **Tek kadin sesi, senaryosuz.** Tepede korku, dususte panik, havuza girince kesilen
   ciglik, yuzeye cikinca kahkaha. Gogsundeki ucuz mikrofondan, hep.

## Aciklama metni kalibi

Iki aciklama ayni kalibi kullaniyor:

```
You're <fiil-ing> <edat> the <LANDMARK> on a transparent water slide above <CITY>.
Every <birim> <takes/gets> you <sifat>, <sifat>, and <sifat>. <iki emoji>

#MegaSlideFear #<LandmarkEtiketi> #WaterSlide #POVReels #CGIAdventure #ViralReels
```

Alti etiketin besi her videoda sabit; sadece landmark etiketi degisiyor.

## Bir uyari

Video 1'in aciklamasi Las Vegas STRAT diyor ama karelerdeki sehir dokusu, isinsal genis
bulvarlari ve yagmuru ile Vegas'a guclu bir benzerlik gostermiyor. Video 2'de ise Ontario
Golu ve Toronto Adalari acikca secilebiliyor, yani orada iddia ile goruntu ortusuyor.
Kanal muhtemelen landmark adini modele soyluyor ama modelin sehir sadakatini kontrol
etmiyor. Biz uretirken bunu dogrulamaliyiz: uretilen videoyu indirip kontakt sayfasindan
sehri gozle teyit et.
