# DEVIR 2026-09-24: performans geri beslemesi + sehir istekleri

Durum (GUNCEL 24 Eyl gece): dort rock da CANLIDA, main 02ebdb4 push edildi. Asagidaki eski durum notu: dort rock `codex-geribesleme`
dalinda (Projeler/Youtube deposu), main'e alinmadi, push edilmedi.
Plan: `RF-PLAN-GERIBESLEME.md` (ayni dalda). Kod Codex'e yazdirildi (Ihsan istegi),
Claude her rock'i satir satir okudu ve kendisi kostu.

## Dal

```
2cebdf8 Rock 4  aimagine sehir istekleri sayaci   <- SON DENETIM BEKLIYOR
77ed8b6 Rock 3  performans hafizasi -> replenish istemi (opt-in, 4 seride acik)
f1ce43c Rock 2  series/performans.py uc platform izlenme toplayici
0ce158e Rock 1  Instagram caption'i en fazla 5 etiket
13f5f79 plan
```

Worktree gecici klasordeydi (`/tmp/wt.kqzzWg/yt`); silinmis olabilir, DAL kalir:
`git worktree add <yeni-yol> codex-geribesleme`.

## Siradaki adimlar (sirasiyla)

1. Rock 4 duzeltme turunun diff'ini OKU (`git show 2cebdf8 -- AImagine-Fear/tools/sehir_istekleri.py`).
   Duzeltilenler: sayfalama parametresi `after` (cursor DEGIL), bos sayfa korumasi,
   IG'de yorumcu adi yok -> yorum basina sayim + `kimlik_notu`, bos yorumda Gemini
   cagrilmaz, 5 harften kisa sehirde dosya-adi eslesmesi yok.
2. Sayaci gercek anahtarla tekrar kos (`.env`'i gecici kopyala, sonra SIL):
   `python -X utf8 AImagine-Fear/tools/sehir_istekleri.py`. Beklenen: ~78 benzersiz
   IG yorumu, kopya id yok. Ilk kosuda tek sehir cikti: Jakarta (1).
3. Tum testler: `python -X utf8 -m pytest tests -q` (HEAD'de de kirik 5 test var:
   test_experiment_runner x4, test_rock5_containment x1; yeni kirik olmamali),
   `pytest AImagine-Fear/tests -q`, `AImagine-Fear/build.py --check`,
   `AImagine-Fear/tools/rota_denetim.py`.
4. Main'e al: main'i `git pull --rebase` ile guncelle, dalin 5 commit'ini cherry-pick et,
   push. Sonra dal + worktree temizligi.
5. Ertesi gunun kosularinda dogrula: `series.performans` adimi loglari,
   `<kanal>/<seri>/performans.json` olustu mu, fear-slide sonrasi
   `AImagine-Fear/veri/sehir_istekleri.json` olustu mu, still-home IG caption'i 5 etiket mi.

## Olculen gercekler (24 Eyl, canli)

- Ilk yorum (992f387) CALISIYOR: still-home Kahire videosunda YouTube'da ve Instagram'da
  kanalin kendi yorumu var. TikTok: `tiktok_reconnect_required`, Ihsan'in Upload-Post
  Manage Users'tan TikTok hesaplarini yeniden baglamasi gerekiyor.
- Sabitleme: Upload-Post'ta YALNIZ TikTok'ta var (`comments/action` pin). YouTube ve
  Instagram'da yok. TikTok yeniden baglaninca ilk yorum orada sabitlenebilir.
- Instagram caption artik tam gidiyor (a3576bc) ama still-home 14 etiketle cikti;
  Rock 1 canliya alininca 5'e iner.
- Performans verisi: `post-analytics?platform_post_id=` metrik DONMEZ ama request_id
  doner; `post-analytics/<request_id>` IG dahil views/likes/comments/saves/shares verir.
  Canli olcum ornegi: wild-encounter part 9 YouTube 35.900 (12,5x), part 13 IG 5.968 (4,2x);
  still-home part 2 TikTok 6.616 (6,8x). Ayni video platformdan platforma cok farkli gidiyor.
- Yorum okuma: IG baskasinin yorumunda kullanici adi/id VERMIYOR (null). YouTube
  `author` + `author_channel_id` veriyor. aimagine YouTube videolarinda hic yorum yok
  (Data API ile de teyit).

## Buyuk listenin kalanı (Ihsan: "1'den 4'e hepsini tamamlayacagiz")

AgentTube kiyasindan cikan eksikler. 1 = bu dal (performans -> planlayici) ve
sehir istekleri. Kalan:
- 2: izleyicinin hangi saniyede kactigi (YouTube Analytics API, her kanal icin
  `yt-analytics.readonly` izni gerekir; Ihsan'in bir kez izin vermesi lazim).
- 3: yorumlardan fikir cikarma butun kanallarda (sehir sayacinin genellestirilmesi;
  soru/istek/duygu siniflandirma, 3+ kisi ayni seyi isterse fikir listesine).
- 4: baslik denemesi (kisa videoda etkisi sinirli, en sona).

## Acik uclar

- The Unfinished ilk yorumu (kok depo b20bae2) calisma agacinda BASKA bir oturum
  tarafindan geri alinmis gorunuyor (`tools/kg_paylas.py`, `tools/gunluk_zamanla.py`
  staged degisiklikler). O oturum bitince yeniden uygula; soru havuzu
  `seriler/bir-kez-olsun/etkilesim.json` yerelde duruyor.
- aimagine rota stogu ~27 Eyl'de bitiyor; yeni rota yazarken `veri/sehir_istekleri.json`
  listesinden sec.


## GUNCEL SIRA (24 Eyl gece, Codex'in plani)

Dort rock CANLIDA (02ebdb4). Kalan isin frozen plani Codex'e yazdirildi:
`RF-PLAN-GERIBESLEME-2.md` (read-only kosu, thread 01a0d1ff-ebc6-75c2-845f-ffda94a2baf4).
Ihsan karari: kalan isler CODEX ile yurutulecek (/codex BUILD A ROCK, her rock sonrasi
Claude diff okur + kanitlari kendisi kosar).

Sira: (1) plandaki 8 uretim duzeltmesi (IG baslik dalinda etiket tavani, performans yas
karsilastirilabilirligi 48h/7d adli anlik goruntuler, erken olcumle donma, izlenme sure
alanlari atiliyor, bozuk performans.json gecmisi silebilir, 6-part kapisi retention'i
gizler, yorum sayfasi limit=50, Gemini eksik id kontrolu) -> (2) A1 izin + yetenek
yoklamasi -> (3) A2 retention -> (4) B1 bes kanal yorum madenciligi -> (5) B2 tuketiciler
-> (6) C1 baslik: otomatik A/B KILL (Shorts Test&Compare'e girmiyor), yerine tek/cift part
iki sabit baslik kalibi.

Ihsan'in elle yapacaklari (A1 icin): Google Cloud'da YouTube Analytics + Data API ac,
OAuth izin ekranini "production" yap (Testing'de token 7 gunde olur), bes kanal icin
izin yardimcisini kos, GitHub secret'lari ekle; TikTok'u Upload-Post'ta yeniden bagla.


## ILERLEME 24 Eyl ogleden sonra

- ADIM 1 BITTI (1b507f4, push): 7 uretim duzeltmesi + taze goz 6 bulgusu. Kohortlar: s48 ve
  oturmus (s7g, yoksa omur). Canli: wild-encounter kutup ayisi/anakonda kazanan, peygamber
  devesi kaybeden -> planlayiciya gidiyor; still-home yeterli oturmus part yok (birkac gun).
- OLCULDU: Upload-Post post_metrics'te izlenme SURESI/retention YOK (IG: views/reach/likes/
  comments/saves/shares/impressions; YT: views/likes/comments/favorites; TikTok: views/likes/
  comments/shares). Yani A1 icin YouTube Analytics OAuth ZORUNLU.
- SIRADAKI: A1 (Ihsan'in Google Cloud OAuth + kanal izinleri). Ihsan'a adim adim anlatilacak.


## ILERLEME 24 Eyl aksam

- A1 izin: shadowedhistory, sentinal_ihsan, galactic_experiment, aimagine CANLI izin verildi
  (secrets_local/, git disi). YouTube Analytics API proje 114387446382'de acildi; cok
  izlenen videolarda 100 noktalik retention geliyor. ACIK: OAuth izin ekrani "Testing"
  ise tokenlar 7 gunde duser (Ihsan kontrol edecek); GitHub secret'lara yukleme Ihsan
  onayi ile A2'de. CraftCalm ve The Unfinished izni alinmadi.
- YAYIN SAATLERI CANLI (5e3e7d4): sentinal 11:00, aimagine 15:00, shadowedhistory 15:30,
  galactic 16:00 UTC hedef; cron = hedef - olculen gecikme; kie-uretim queue: max.
  Tam dakika tasarimi ertelendi: RF-PLAN-YAYIN-SAATI.md + RF-SAME-PAGE-LOG-YAYIN-SAATI.md.
  Iki hafta sonra: performans.json yayin zamanlari + goruntulenmeleri eski saatlerle kiyasla.
- CANLI BULGU: aimagine Instagram'da ilk yorum SESSIZCE dusmuyor (uyari yok); YouTube'da
  var. galactic/shadowedhistory IG'de calisiyor. Olasi sebep: aimagine IG baglantisi
  yorum izni olmadan yapilmis -> Upload-Post Manage Users'ta yeniden bagla (TikTok ile).
- SIRADAKI (Codex ile): A2 retention toplayici + PERFORMANCE MEMORY'ye "izleyici nerede
  kaciyor", sonra B1/B2 bes kanal yorum madenciligi, C1 tek/cift baslik kalibi.
