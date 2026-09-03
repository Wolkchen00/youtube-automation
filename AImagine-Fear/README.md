# AImagine Fear Slide

fearvisionofficiel kanalinin korku kaydiragi formatinin tersine muhendisligi ve
AImagine icin yeniden kurulmus prompt sistemi.

**Bir rota = bir prompt = bir video.** Klip zinciri yok, birlestirme yok. Kaynak kanal da
oyle yapiyor: olculdu, `reference/TERSINE-MUHENDISLIK.md`.

## Uretim

```powershell
python build.py --check
```

Butun rotalari yeniden uretir ve on iki kurala gore dogrular. Bir sey bozuksa rota adini,
bolumu ve satiri yazip 1 koduyla cikar.

Yapistirmaya hazir dosyalar:

- `out/vegas-strat-blue-rain/PROMPT.txt`
- `out/toronto-cn-red-dusk/PROMPT.txt`

Yaninda her rota icin `CAPTION.txt` (aciklama + etiketler) ve `VOICE.txt` (replik zaman
cizelgesi).

## Yeni sehir nasil eklenir

1. `routes/_TEMPLATE.md` dosyasini `<sehir>-<renk>-<hava>.md` adiyla kopyala.
2. Ust kisimdaki sekiz alani doldur: `SLUG`, `DESTINATION`, `LANDMARK`, `DURATION`,
   `NEON`, `LEGWEAR`, `WEATHER`, `SOURCE`.
3. `OPENING STATE`, `BEATS`, `END STATE`, `VOICE`, `CAPTION` bolumlerini Ingilizce yaz.
   BEATS 0.0'dan DURATION'a bosluksuz ve cakismasiz gitmeli, en az bes aralik olmali.
   Rota metinlerinin toplami 600-1000 kelime olmali.
4. `python build.py --check` calistir.

`canon/` degistirirsen butun rotalar degisir. Yeni sehir icin `canon/` dosyalarina
dokunman gerekmez.

## Neden bu kadar cok kural var

Formatin tamami yedi seye dayaniyor ve yedisi de kirilgan: yuzun hic gorunmemesi, balik
gozunun ufku bukmesi, kaydiragin seffaf olmasi, tek doygun rengin kadraji yonetmesi,
kameranin govdeye civatali olmasi, her seyin ulasilmadan once ileride gorunmesi, ve tek
kadin sesinin senaryosuz olmasi. Bunlarin hepsi `canon/MASTER-BLOCK.md` icinde madde madde
yazili ve her promptta AYNEN tekrarlaniyor. Dogrulama kurallari da yeni bir sehir yazan
kisinin bunlardan biriyle kavga etmesini engellemek icin var.

## Onemli not: kamera havuzu istisnasi

`Shorts_Dizi_Fabrikasi/stil_havuzu/kamera.json` balik gozunu ve elde kamerayi YASAKLIYOR,
cunku o motorda yuz referansa kilitli ve balik gozu yuzu bozuyor. Bu formatta **yuz hic
yok**, o yuzden yasak dusuyor. Bu, balik gozunun guvenli oldugu tek format. Iki katalogu
karistirma.

## Test edilmemis olan sey

Prompt uzunlugu yaklasik 2350 kelime. Bunun Veo/Sora uzerinde seyrelme yapip yapmadigi
OLCULMEDI. Ilk uretimden sonra videoyu indir, kontakt sayfasi cikar, kare kare bak:
sehir dogru mu, yuz sizmis mi, kaydirak seffaf kalmis mi, kesme olmus mu.
