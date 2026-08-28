# PILOT 2 ve ROCK A uretim yolu olcumleri (2026-08-28)

Ham kanit. Yorum degil, olculen sayilar.

## 1. ROCK A ses master zinciri, URETIM fonksiyonlariyla, 0 kredi

`core.ffmpeg_tools.master_audio` + `series.produce._verify_audio_master`, pilot-1'in
gercek ciktisi uzerinde (`ep22_narrated_music.mp4`):

| asama | integrated | true-peak |
|---|---|---|
| ham (filo geneli kusur) | **-24,5 LUFS** | -6,3 dBTP |
| master sonrasi | **-14,3 LUFS** | -1,3 dBTP |

`_verify_audio_master(out, -14.0)` -> **True**. Sure: 1,5 sn.
Esikler (-14 +/-1 LUFS, TP <= -1,0 dBTP) saglaniyor.

Serinin cozulmus ayari: `upscale = {}` (falsy) -> 4K dali ATLANIYOR; uretim yolu
`master_audio` -> `_verify_audio_master`. `required_layers = []` -> native_audio
dogrulamasi kosmuyor. Yani yukaridaki iki cagri, kanalin GERCEK ses yolunun tamamidir.

## 2. Pilot-2 kosulari

### Kosu A (basarisiz, 184 kr) - ilk kare
Cekim 1 `first_frame_ok=false`, iki denemede de. Sebep KOD DEGIL PLAN: prompt
"the soap ... begins to crack like glass" diyordu; brief kural (4) shot 1'de
tetikleyici fiili yasaklar (anomali kameradan ONCE baslamis olmali), kural (15)
ihlalin ilk karede UC halinde gorunmesini ister.

Bu kosunun kanitladiklari:
* ROCK C1 canli: 5 `qc_api_attempt` olayinin 5'i de `qc_api_result` ile eslesti.
* ROCK C2 canli: `QC anahtar kaynagi: GEMINI_API_KEY_QC` (uretim havuzundan ayri).
* ROCK B sinyal uretti: deneme 1'de `anomaly_match {value:false, visible:true,
  confidence:0.9}` - planda tasarlanan "gorunur ama yok" vakasinin ta kendisi.
* ROCK D0 canli: taban acikken her yetkilendirmede TAZE bakiye okundu.

### Kosu B (basarisiz, 268 kr) - sureklilik
Cekim 1 ILK denemede gecti (artifact 0/10): plan duzeltmesi tuttu.
Cekim 2 iki kez red: "obje referansla ayni fiziksel obje degil" + sureklilik bozuk.
Sebep yine PLAN, ve bu kez duzeltmenin YAN ETKISI: cekim 1'i "zaten kirilmis" yaptim
ama cekim 2 hala SAGLAM bir sabunu tarif ediyordu. Onarim: cekim 1'e
`state_carry = "a bright conchoidal fracture face on the pink bar"` eklendi ve cekim 2
bu izi birebir tasiyacak sekilde yeniden yazildi.

### Tahsisatci: HATA YOK (supheyi olcum curuttu)
"dinamik kredi payi doldu" mesaji tavan hatasi gibi gorunuyordu. Gercek aritmetik:

    remaining = min(bolum tavani kalan 532, ASAMA tavani kalan 448) = 448
    gereken   = 100 (istek) + 200 (cekim 3-4 ana) + 200 (cekim 3-4 ilk regen) = 500
    448 < 500 -> RED

Baglayan kisit bolum tavani DEGIL, deney asama tavaniydi: ilk basarisiz kosunun 184
kredisi asamadan yenmisti. URETIMDE asama kapisi YOKTUR; orada remaining 532 olur ve
ikinci regen VERILIR. Yani canli kanal bu davranistan etkilenmiyor.
Operasyonel onarim: pilot2 asama tavani 900 -> 1300 (tahsis 3000/4000; bake-off 0,
K1-B korundu).

## 3. Kill-gate penceresi (ROCK E2 sonrasi)

Mevcut stack parmak izi: `tools/killgate_report.py --series unnatural-lab --stack`.
Son 10 yayinin tamami `stack=yok` -> **karar_yok** (hepsi parmak izinden onceki
bolumler; dogru davranis). Yorum alarmi bu redde ragmen GORUNUR kaliyor:
C/1k medyani 0,00 < 0,3.
Sonuc: kill-gate penceresi SIFIRDAN, yeni stack ile baslamalidir.
