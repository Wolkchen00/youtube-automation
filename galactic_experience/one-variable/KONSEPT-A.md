# PLANET SCALE , KONSEPT A DOKTRINI v2.0 (dogal afet antolojisi)

**Tarih:** 14 Eylul 2026 · **Karar sahibi:** Ihsan · **Statu:** CANLI
**Kanal:** galacticexperimet · **Serit slug:** `one-variable` (slug KORUNDU, konsept daraldi)
**Onceki surum:** v1.0 "tek degisken deneyi", `galactic_experience/KONSEPT.md` v2.0 icinde.
**Olcum kaynagi:** `REELYZE-RAPOR.md` EK 8 (uc konseptin bake-off sonucu).

> Slug neden degismedi: `published.json`, `last_run.json`, workflow ve `filo.json`
> hepsi bu slug'a bagli. Yeniden adlandirmak dort yerde kirilma riski, kazanci
> yalniz isim estetigi. Slug ic isimdir, izleyici gormez.

---

## 1. Ihsan'in direktifi (14 Eylul)

"Tsunami ve girdabi birlestiriyoruz: dev dalgalar, kiyi kasabasi, sahil sehri.
Insanlar dunyada olan dogal felaketleri izliyorlar. Her gun degisik bir dogal
felaket uretmeni istiyorum. Buyuk kasirgalar, uzaydan cekilmis devasa bulutlar,
dunyada acilmis yariklar, deprem gibi felaketler. Hepsi ayni kalitede, yuksek
cozunurluklu ve tek video seklinde olmali."

## 2. FORMUL

**Gercek ve ilk bakista taninabilir bir yerde, gercek bir dogal afet turu,
IMKANSIZ olcekte, tek kesintisiz 8 saniyelik sabit planda, yukaridan.**

Konsept v1.0'dan farki: artik "tek fiziksel degisken degistirilir" demiyoruz.
Ozne bir DENEY degil, bir AFET. Deney dili caption'da kalir, kadrajda afet vardir.

## 3. Neden bu formul , OLCULDU

Bake-off'ta bu formulden iki bolum cikti, ikisi de tuttu:

| bolum | YouTube | TikTok | kanal medyani |
|---|---:|---:|---:|
| One Wave Along the Whole Coast | 1.060 | **9.545** | 104 |
| One Whirlpool That Never Closes | **1.676** | 367 | 104 |

Ayni kanalda ayni gunlerde yayinlanan uydurma geometri (Infinite Neighborhood)
77 izlenmede kaldi, yani rafa kalkan olu formatin bile altinda. Teknik olcumlerin
BESI (ses seviyesi, ses zarfi, hareket, parlaklik, yayin saati) o cokusu
aciklamadi. Ayiran tek sey oznenin GERCEK olmasiydi.

Bu bulgu filoda dorduncu kez dogrulandi: `still-home`da taninan sehir 46.042
begeni / isimsiz kubbe 124; `AImagine-Fear`de ikonik landmark 4/4 tuttu,
uydurma rota 3/3 kaybetti.

## 4. OLCULEN KURALLAR , kazanan iki promptun anatomisi

1. **TEK KESINTISIZ 8 SANIYE, 24 fps.** Kesme, gecis, fade, sahne sifirlamasi yok.
2. **KAMERA TAMAMEN KILITLI.** Ayni dunya koordinati, yukseklik, bakis yonu, odak
   uzakligi, netlik mesafesi ve pozlama sekiz saniye boyunca AYNI. Pan, tilt, zoom,
   orbit, takip, sarsinti yok. Kazanan iki promptta da bu cumle iki kez geciyor:
   bir kez onekte, bir kez ozgun paragrafta. Tekrari KORU.
3. **ILK KAREDE AFET ZATEN TAM GUCUNDE.** Kurulum, yaklasma, once normal halini
   gosterme yasak. Tsunami promptunda dalga duvari "fills the frame from the very
   first moment"; girdapta vorteks "already at full size and full depth in the very
   first frame".
4. **OLCEK REFERANSI ZORUNLU.** Afetin buyuklugu ancak taninan bir insan yapisiyla
   okunur. Tsunamide liman vincleri, kule bloklari, kopruler; girdapta kiyi kasabasi,
   dalgakiran, plaj. Olcek referansi olmayan kare "buyuk" degil sadece "soyut" olur.
5. **GERCEK COGRAFYA, EN AZ UC CIPA.** Kiyi bicimi, dag sirasi, nehir agzi, ada yayi,
   liman, sehir isigi agi. Uydurma yer adi yasak.
6. **SES OLAYIN SEKLINI IZLER.** Iki ayri egri var ve dogru olani secmek zorunlu:
   - **Tek carpma olayi** (tsunami, meteor, coku): 0-1 sn duyulur taban, 3-5 sn
     sessizlige yakin incelme, 6-8 sn en guclu tok darbe. Kazanan tsunamide olculen
     salinim +17,0 dB.
   - **Suregiden olay** (girdap, kasirga, lav akisi): tek duz, gur, kesintisiz
     seviye, 0'dan 8'e. Girdapta olculen LRA 0,9.
   Yanlis egriyi secmek bolumu duzler.
7. **DIEGETIC SES TEK KATMAN.** Anlatim yok, konusma yok, muzik yok. Ses -14 LUFS'a
   masterlanir, true peak tavani -1,0 dBTP.
8. **SON KARE DEVAM EDEN FIZIKSEL DURUM.** Kapanis hareketi yok, donguye uygun biter.

## 5. YASAKLAR

- Insan figuru, yuz, beden, panik kalabalik. **Bu bir yayin guvenligi kuralidir,
  gevsetilmez.** Kanal fizigi ve olcegi gosterir, can kaybini degil.
- Meskun bina yikiminin yakin plani. Genis havadan gorulen sehir silueti serbest,
  tek binanin icine giren plan degil.
- Okunabilir yazi, altyazi, kunye, logo, filigran, imza, kapanis karti.
- Uydurma yer adi, uydurma cografya, genel "bir gezegen" manzarasi.
- Ikinci bir afet ya da bagimsiz ikinci olay. Kadrajda TEK afet vardir.
- Kamera hareketi, kesme, gecis.
- Yayinlanmis bir afet-yer ciftinin tekrari.

## 6. AILELER

Ardisik iki bolum ayni aileden olamaz.

| aile | kapsam |
|---|---|
| `su afeti` | tsunami, girdap, dev sel dalgasi, kiyi basmasi |
| `atmosfer afeti` | kasirga, hortum, kum duvari, yorungeden gorulen dev bulut sistemi |
| `yer afeti` | deprem, acilan yarik, heyelan, coku |
| `ates afeti` | volkan patlamasi, lav akisi, piroklastik akinti |
| `buz afeti` | buzul cokusu, buz rafi kirilmasi, kar firtinasi |
| `gok afeti` | simsek firtinasi, meteor, kutup firtinasi |

## 7. OLCUM

- Degerlendirme penceresi 44 saat (kanal dersi: gec atesleme gercek, 21. saatte
  olu gorunen video 44. saatte patlayabiliyor).
- Ana sinyal izlenme. Yorum orani bu kanalda HENUZ calismadi: bake-off'un dort
  videosunda da yorum 0-3 geldi, karar izlenmeyle verildi.
- Her bolumun LUFS, true peak ve ses zarfi degeri deftere yazilir.
- Platform ayrisiyor: ayni konseptin iki bolumu iki ayri platformda patladi.
  **Tek platforma bakip bolum elemeyin.**
