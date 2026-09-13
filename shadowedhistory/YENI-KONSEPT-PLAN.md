# shadowedhistory , YENI KONSEPT PLANI (13 Eylul 2026)

Durum: TASLAK. Ihsan onaylayana kadar hicbir sey uretilmez.
Yazan: Claude (Vizyoner). Uygulayacak: Codex (Entegrator).

Ihsan karari: tarih konsepti arsivde (`_arsiv/shadowedhistory_2026-09-13/`),
kanal gelecek temali ve ANLATIMSIZ bir konsepte geciyor.
Referans: `instagram.com/one__create`, 5 video olculdu.
Butun olcumler: `REELYZE-RAPOR.md` , "EK , @one__create referans analizi".

---

## 1. Konsept , STILL HOME

**Tek cumle:** Gercek, taninan bir sehrin 2512'deki hali , ve icinde hala
siradan hayat surdugunu gosteren iki cekim.

Duygusal motor DISTOPYA DEGIL, **SUREKLILIK**. Referansin kendi caption'i
bunu acikca soyluyor: "They didn't leave the wall. They built homes inside it.
For them, this isn't a shelter anymore. It's home."

Yani her bolum sunu der: dunya degisti, insanlar gitmedi. Kaldilar ve orayi
ev yaptilar. Carsi kuruldu, isiklar yandi, cocuklar buyudu.

Bu ton zorunludur: sicak pencere isiklari, kalabalik, gunluk hayat.
Harabe, ceset, panik, savas, olum YOK.

### Yil: 2512

Ihsan karari (13 Eylul): 2190 "cok yakin", daha uzak bir yil istendi.
2512 secildi , ~490 yil sonrasi, yuvarlak degil (belirli yil "gercek kayit"
hissi verir, referansin 2247'si de oyle), 2247'den net ayrisiyor.

Uzaklik konsepti GUCLENDIRIYOR: "500 yil sonra Ayasofya hala orada" cumlesi
165 yildan daha vurucu. Bu ayni zamanda bilincli bir gerilim: 2. bolumdeki
"taninir yapi" kurali ile "bu kadar uzak gelecekte o yapi ayakta mi" sorusu
karsi karsiya. Cevap kanonik: **yapi ayakta, ama donusmus.** Ayasofya bir
ortunun altinda, Eyfel bir tarim kulesinin iskeleti. Taninirlik korunur,
zaman gecmisligi de okunur.

## 2. Olculen bicim sozlesmesi , referanstan birebir

| Alan | Deger | Kaynak |
|---|---|---|
| Sure | 9 sn (band 8-10) | referans 5,5-10,1; kazanan 10,1 |
| Cekim | **2** | referansin 5/5'i |
| Cekim 1 | ~5 sn, tanri-gozu genis | kazananda kesme 5,04 sn'de |
| Cekim 2 | ~4 sn, alcak / insan olcegi | ,  |
| Kesme | SERT, eslesen hareket DEGIL | ayni yerin cok farkli iki acisi |
| fps | 24 | referansin 4/5'i |
| Cozunurluk | 1080x1920 | ,  |
| **Anlatim** | **YOK** | desifre 0 kelime, 5/5 |
| Ses | derin drone, **-14 LUFS, LRA < 2** | 5/5 videoda -14,0..-14,1 |
| Ses bandi | ~2 kHz'de kesik | 2-8kHz 29 dB asagi, 8k ustu yok |
| Kunye | **SEHIR + 2512**, daktilo | kazanan tek sehir-adli video |

## 3. Iki degismez kural , olculen kazanma sartlari

**(1) TANINIR GERCEK SEHIR ZORUNLU.** Referansta 46.042 begeni ile 124 begeni
arasinda 371 kat fark var, ayni kanal ve ayni formatta. Ayiran degisken:
kazananda Tokyo Kulesi ve Skytree kadrajda. Kaybedenler isimsiz kubbe, isimsiz
col, isimsiz ova.

Bu bizim kendi aimagine olcumumuzle BAGIMSIZ olarak ortusuyor (ikonlar 4/4
tuttu, tekrarlanan jenerik 3/3 kaybetti). Iki ayri kanal, ayni yon.

Yani: **her bolumde en az bir dunyaca bilinen yapi ya da siluet kadrajda.**
Uydurma sehir, isimsiz kubbe, jenerik sci-fi manzara YASAK.

**(2) ILK KARE TANRI-GOZU GENIS.** Imkansiz yapi TEK karede okunmali.
Referansin en kotusu (124 begeni) zaten ICERIDE basliyor, genis kurulus yok.

## 4. Kunye , yeni motor yetenegi

Referansta olculen davranis:
- Sol ust, ~%6 sol kenar boslugu, ~%20 ustten
- Tamami buyuk harf, kalin sikisik grotesk
- **Harf harf yaziliyor, ~0,5 sn'de tamamlaniyor** (`TO` > `TOKYO 22` > `TOKYO 2247`)
- Ilk cekim boyunca duruyor, **kesmede ~0,4 sn'de soluyor**
- Renk kontrasta gore: acik zeminde SIYAH (4/5), koyu zeminde BEYAZ (1/5)
- Arkada kutu YOK

Mevcut `core/ffmpeg_tools.py:title_card_overlay` bunun cogunu yapiyor:
`y=px(320)` (=%16,7, referansin %20'sine cok yakin) ve son 0,5 sn'de soluyor.

**Eksikler:** ortali hizalama (`x=(w-text_w)/2`, satir 1484), sabit beyaz renk
(satir 1469-1471), `box=1` kutusu (satir 1484), daktilo yok.

Gereken: mevcut davranisi BOZMADAN opt-in bir mod. Detay Bolum 7'de.

## 5. Bunu one-variable'dan ayiran sey , CAKISMA UYARISI

galactic kanalindaki `one-variable` de "gercek yer + anlatimsiz + -14 LUFS".
Iki kanal birbirine benzemesin diye farklar ZORUNLU:

| | one-variable (galactic) | still-home (shadowedhistory) |
|---|---|---|
| Konu | gercek yere TEK fiziksel degisken | gercek sehrin YASANAN gelecegi |
| Zaman | simdi | 2512 |
| Plan | 1 kesintisiz 8 sn, kamera KILITLI | **2 cekim**, sert kesme |
| Kunye | KAPALI | **ACIK**, daktilo, SEHIR + 2512 |
| Insan | **YASAK** | **ZORUNLU** , carsi, kalabalik, isik |
| Ses | diegetic, ~16 dB salinim | **sabit derin drone, LRA < 2** |
| Duygu | fizik ve olcek | sureklilik, ev |

Bu tablo kanonik. Bir bolum bu farklardan birini kaybederse
one-variable'in kopyasi olur.

## 6. Uretilecekler

| # | Is | Yer |
|---|---|---|
| 1 | `KONSEPT.md` doktrini + SHA-256 pin | `shadowedhistory/KONSEPT.md` |
| 2 | `series.json` (status=draft, cron kapali) | `shadowedhistory/still-home/` |
| 3 | `bible.json` | ayni |
| 4 | 5 launch bolum plani | `still-home/plans/` |
| 5 | Konu havuzu + replenish brief | `series.json` icinde |
| 6 | Daktilo kunye modu | `core/ffmpeg_tools.py` |
| 7 | Workflow yml (cron YORUMDA) | `.github/workflows/still-home.yml` |
| 8 | Testler | `tests/` |
| 9 | beyin.py + tamlik.py slug haritasi | `gunluk_beyin/` |
| 10 | filo.json kaydi | `Projeler/Youtube/filo.json` |

## 7. Daktilo kunye , teknik sozlesme

`title_card_overlay`'e opt-in alanlar. **Varsayilanlar mevcut davranisi
birebir korur** , next-stop ve diger kanallar etkilenmez.

```
bible.series.title_card = {
  "enabled": true,
  "duration": 5.0,          # cekim 1 kadar; kesmede soluyor
  "typewriter": 0.5,        # 0 / yok = kapali (varsayilan), mevcut davranis
  "align": "left",          # varsayilan "center"
  "margin_pct": 6,          # sol kenar boslugu, align=left iken
  "color": "black",         # varsayilan "white"
  "box": false,             # varsayilan true
  "preserve_case": false
}
```

Daktilo uygulamasi: harf sayisi kadar `drawtext`, her biri kendi
`enable='gte(t,<harfin_zamani>)'` ile. Tek gecis, ek kodek yok.

`_drawtext_escape` ZATEN var, kullan. Windows surucu iki noktasi kacisi
(`fontfile` satiri, 1452) korunacak , bozarsan Windows'ta kunye olur.

Hata halinde mevcut davranis aynen: `required` degilse orijinali kopyala,
yayin bloke olmasin.

## 8. 5 launch bolumu , hepsi taninir sehir

| # | Sehir | Kunye | Cekim 1 (tanri-gozu) | Cekim 2 (insan olcegi) |
|---|---|---|---|---|
| 1 | Istanbul | ISTANBUL 2512 | Bogaz'in ustu kapanmis, Ayasofya ve Sultanahmet siluetleri camli bir ortu altinda | ortunun altinda vapur iskelesi, carsi isiklari, kalabalik |
| 2 | New York | NEW YORK 2512 | Manhattan su seviyesinin ustune kaldirilmis platformlarda, Empire State hala ayakta | platform altinda tekne mahallesi, sicak pencereler |
| 3 | Paris | PARIS 2512 | Eyfel bir dikey tarim kulesinin iskeleti olmus, sehir yesil teraslarla kapli | kule dibinde pazar, satici tezgahlari |
| 4 | Dubai | DUBAI 2512 | Burj Khalifa kum cephesinin icinde, sehir yer altina inmis | yer alti bulvari, isikli vitrinler, kalabalik |
| 5 | Tokyo | TOKYO 2512 | **Referansin sehri , EN SONA.** Kendi yorumumuz, kopya degil | ,  |

Tokyo bilerek 5. sirada: referansin kazanan sehrini birinci bolumde kullanmak
dogrudan kopya gorunur.

## 9. Caption , hikayeyi YAZI tasir

Anlatim olmadigi icin hikaye caption'da. Referansin kalibi:
- Ingilizce + ikinci dil (referans Japonca kullaniyor)
- Kisa satirlar, 60-120 kelime
- "A fictional future world created with AI" ibaresi ACIKCA
- Hashtag'te yil marka olarak: #STILLHOME2512

Ikinci dil karari Ihsan'a birakilir (referans Japonca; bizde Turkce ya da
hic olmayabilir).

## 10. ACIK , Ihsan karari bekleyenler

1. **Kanal adi.** Ihsan "kanal adini degistir, handle kalsin" dedi.
   Onerilen ad: **Still Home**. Alternatif: Earth 2512.
2. **Caption ikinci dili.** Turkce mi, Japonca mi, yok mu.
3. **Yayin ritmi.** Eski serit gunluk 20:30 UTC idi. Ayni kalsin mi.

## 11. OLCULMEMIS , iddia etme

- IG oynatma sayilari cekilemedi (giris duvari), yalniz begeni alindi.
  Ihsan'in soyledigi 5,6M onun beyani, bizim olcumumuz degil.
- n=5. "Taninir sehir kazandirir" bir KORELASYON, kanit degil. Ama iki ayri
  kanalda ayni yone isaret ediyor.
- "2x5 sn kazandirir" hipotezi n=5'te ayirt edilemedi, test edilmeli.
- Referansin yazi tipi teshis edilemedi. Anton / Archivo Black ailesine
  benziyor, kesin ad iddia edilmiyor.
- Referansin hangi AI modeliyle uretildigi bilinmiyor.
