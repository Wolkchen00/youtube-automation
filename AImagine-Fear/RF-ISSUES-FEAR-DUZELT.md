# RF-ISSUES-FEAR-DUZELT , bu kosuda YAPILMAYANLAR

Tarih: 10 Eylul 2026 (Los Angeles)
Plan: `RF-PLAN-FEAR-DUZELT.md`

## Elle yapilacak (kod degil, Ihsan'in isi)

| # | Is | Neden kod degil |
|---|---|---|
| 1 | YouTube kategorisini "Travel & Events" ya da "Entertainment" yap | `core/uploader.py` kategori/`categoryId` alanini HIC desteklemiyor. Upload-Post yolu bunu gecirmiyor. YouTube Studio'dan elle, ya da ayri bir rock olarak uploader'a alan eklenmeli (dort kanali birden etkiler). |
| 2 | "Next Stop" serisini `aimagine` kanalindan ayir | YouTube hesap islemi. 56 saniyelik Next Stop (3-17 izlenme) ile 15 saniyelik POV kaydiragi ayni kanalda; algoritma kanaldan ne bekleyecegini bilmiyor. |
| 3 | 1080p'nin gercek kredi maliyetini olc | Ilk gercek kosuda `kie_uret.py` "harcanan" satirini oku. Tarifeye OLCULMEDEN yazma. |
| 4 | Palet A/B sonucunu oku | Rock 5 damgayi kuruyor; karsilastirma en az 6 yayindan sonra IG Insights ile yapilir. |

## Olculemedi (veri yok)

- IG gercek izlenme sayilari (Insights gerekiyor; 371.000 begeniden tahmin edildi)
- Retention egrileri (YouTube Studio / IG Insights)

## Ertelendi (ayri plan)

- Filo geneli yayin oncesi skor karti: `RF-PLAN-REELYZE.md` Faz 2
- Reelyze trend hasati ve kanca uretici: `RF-PLAN-REELYZE.md` Faz 3

## Round 1 sonrasi eklenenler (Codex bulgulari, bu kosuda YAPILMIYOR)

| # | Is | Neden bu kosuda degil |
|---|---|---|
| 5 | Platform basina yeniden deneme: YouTube gecip IG duserse yalniz IG'yi tekrar dene | `yayinla.py`'nin sha ve ayni-gun kapilari tum kosuyu blokluyor. Gercek bir davranis degisikligi ve dort kanalin ortak yukleyicisine yakin. Bu kosuda yalnizca donusumun YouTube basarisina baglanmasi yapildi. |
| 6 | Otomatik goruntu/kanon uyum kapisi (kare farki, OCR, sahne tespiti) | Teknik kapi 1080x1920/30fps/sesli HERHANGI bir klibi gecirir. Bu kosuda yerine `--yayinlama` + kontakt sayfasi ile INSAN onayi kondu. Otomatik surumu `RF-PLAN-REELYZE.md` Faz 2'nin isi. |
| 7 | Ucuncu sicak rota (yeniden boyanmis Sanghay) | Kanon metnini toplu renk degistirerek yeniden yazmak Codex'in isi degil; Ihsan yazmali. Palet A/B su an 2 sicak / 7 neon ile yuruyor. |
| 8 | **`seedance-2` kanarya kosusu** | `seedance-2`'nin 1080p ve 15sn ustu destegi BILINMIYOR (`core/kie_api.py:489` notu `seedance-2-fast`'e ait). Kredi harcar, Ihsan'in karari. Rock 1b'nin `--yayinlama` modu bu kanaryayi yayinlamadan kosmak icin var. |
