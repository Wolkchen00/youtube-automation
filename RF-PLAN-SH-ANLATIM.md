# RF-PLAN: shadowedhistory anlatim temposu ve cumle butunlugu

Tek ROCK. Kanal: shadowedhistory / seri: flashpoints.
Core Focus: **Anlatici yavas ve dogal konussun, cumlesini HER ZAMAN video
bitmeden bitirsin; iki cekim tek kesintisiz konusmanin ustunde aksin.**

## Tespit (kodda dogrulandi, tahmin degil)

Uc sikayet tek zincirden geliyor:

1. `shadowedhistory/flashpoints/series.json` -> `auto_replenish`:
   `shots: 2`, `shot_seconds: "8"` = 16.0 sn ham.
   `bible.json` -> `micro_trim: 0.25` -> her cekimden bas+son 0.25 sn kirpilir
   = cekim basina 0.5 sn, iki cekimde 1.0 sn. **Final video 15.0 sn.**
2. Ayni cfg: `narration: {min_words: 26, max_words: 38}`.
   38 kelime / 15.0 sn = **2.53 kelime/sn**. Bu zaten kosar adim tempo.
3. `core/narration.py` -> `CHANNEL_NARRATION_CONFIG["shadowedhistory"]`
   TTS'e acikca hizli konusmasini soyluyor:
   "Deliver hard historical facts **fast**", "Keep the **pace tight** for a
   roughly 16-second video", "**No** heavy documentary delivery and **no long
   dramatic pauses**".
4. `core/ffmpeg_tools.py` -> `mix_voiceover`: ses videodan uzunsa once
   `atempo` ile **1.15x'e kadar hizlandiriyor**, yetmezse
   `amix duration=first` + `-shortest` ile **cumlenin ortasindan kesiyor**.

Yani: metin zaten sigmiyor -> once hizlandiriliyor -> sonra sonu kesiliyor.
Ikisi de kullanicinin sikayeti.

## Karar (Ihsan, 2026-09-01)

Metni kisaltmak yerine **videoyu uzat**: `shot_seconds` 8 -> 10.
Final video 20.0 - 1.0 = **19.0 sn**. Kredi 2x160+80=400 -> 2x200+80=**480**
(bolum tavani 900, QC regen dahil en kotu 680 < 900).

## Rock kapsami

### R1 - TTS artik yavas konussun (`core/narration.py`)
`CHANNEL_NARRATION_CONFIG["shadowedhistory"]["instruction"]` bastan yazilir:
olculu belgesel temposu, net telaffuz, twist oncesi dogal bir duraklama,
asla acele etmeyen teslim. "fast" / "pace tight" / "no long dramatic pauses"
ifadeleri KALKAR. Sure referansi 16 sn degil ~19 sn olur.
SADECE shadowedhistory anahtari degisir; galactic_experiment, aimagine,
sentinal_ihsan, sentinal_vlog anahtarlarina DOKUNULMAZ.

### R2 - Video anlatima yer acsin (`shadowedhistory/flashpoints/series.json`)
- `auto_replenish.shot_seconds`: `"8"` -> `"10"`.
- `auto_replenish.narration`: `{min_words: 26, max_words: 38}` ->
  `{min_words: 26, max_words: 36}` (asagidaki degismez kurala uymak icin).
- `logline` icindeki "hardest 14 seconds" -> "hardest 20 seconds"
  (metin Gemini prompt'una giriyor, sure ile celismesin).
- `shots: 2` DEGISMEZ. `topic_pool`, `families`, `music_style` DEGISMEZ.

**Degismez kural (test edilecek):**
`max_words <= floor((shots*shot_seconds - shots*2*micro_trim - 0.7) * 2.05)`
Yeni degerlerle: (20 - 1.0 - 0.7) * 2.05 = 37.5 -> 37, yani 36 gecerli.
Eski degerlerle: (16 - 1.0 - 0.7) * 2.05 = 29.3 -> 29, yani 38 GECERSIZDI.
2.05 = yavas belgesel temposunun kelime/sn tavani. 0.7 = ilk kelime oncesi
0.3 sn giris + son kelimeden sonra 0.4 sn nefes payi.

### R3 - Kuyruktaki bolumler de 10 sn olsun
`shadowedhistory/flashpoints/plans/part22.json` ... `part25.json`
(series.json `next_part: 22`, `total_parts: 25`; 21 ve oncesi yayinlandi):
her `shots[*].duration` degeri `"8"` -> `"10"`. Baska HICBIR alan degismez
(prompt metni, narration, seed, music, title_card aynen kalir).
part21 ve oncesine DOKUNULMAZ.

### R4 - Anlatim ASLA kesilmesin (`core/ffmpeg_tools.py: mix_voiceover`)
Strateji tersine cevrilir: ses videoya sigdirilmaz, **video sese yer acar**.

Sabitler (modul duzeyinde, isimli):
- `NARRATION_TAIL_PAD = 0.4`   son kelimeden sonraki nefes payi (sn)
- `NARRATION_MAX_TEMPO = 1.05` duyulmayan hizlandirma tavani (eski 1.15)
- `NARRATION_MAX_EXTEND = 3.0` videoyu uzatma tavani (sn)

Davranis:
1. `vid_dur`, `vo_dur` olculur. Olculemezse bugunku best-effort davranis
   aynen korunur (fonksiyon patlamaz, video kopyalanir).
2. `need = vo_dur + NARRATION_TAIL_PAD`.
   `need <= vid_dur` ise: hicbir sey yapilmaz (atempo YOK, uzatma YOK).
   Bu, bugun sigan bolumlerin ciktisini bit-bit ayni tutar.
3. Sigmiyorsa once en fazla `NARRATION_MAX_TEMPO` kadar hizlandirilir.
   Gereken tempo 1.05'ten buyukse tempo 1.05'te SABITLENIR; daha fazla
   hizlandirma YAPILMAZ (kullanici sikayeti tam olarak buydu).
4. Kalan acik `ext = min(need - vid_dur*, NARRATION_MAX_EXTEND)` kadar
   video sonu uzatilir: son kare klonlanarak tutulur
   (`tpad=stop_mode=clone:stop_duration=<ext>`), ham ses `apad` ile
   uzatilir, karisim `amix duration=longest` ile alinir ve `-shortest`
   KALDIRILIR. Boylece son kelime her zaman ekranda biter.
5. `ext` tavana dayaniyorsa (yani 3.0 sn de yetmiyorsa) WARNING loglanir ve
   kalan kisim bugunku gibi kesilir. Sessiz basarisizlik olmaz.
6. Uzatma gerektiginde video bir kez yeniden kodlanir; kodlama ayarlari
   projenin mevcut sabitleriyle AYNI olur (`FFMPEG_CRF`, `FFMPEG_PRESET`,
   `FFMPEG_AUDIO_BITRATE`). Uzatma gerekmiyorsa `-c:v copy` yolu korunur.
7. Fonksiyon imzasi ve donus tipi (`Path`) DEGISMEZ; `voice_volume`,
   `bg_duck`, `amix_normalize` parametreleri aynen calisir. Cagiran taraf
   (`series/produce.py`) DEGISTIRILMEZ.

Bu degisiklik anlatimli TUM kanallari etkiler (sentinal_ihsan, aimagine,
galactic, unnatural-lab). Etki tek yonlu iyilesmedir: hicbir kanalda konusma
artik kesilmez. Bilerek global.

### R5 - Iki cekim tek konusmanin ustunde aksin (`series/replenish.py`)
`narrated` dalindaki showrunner prompt'u (su an ~540. satir) uc kural kazanir:
1. Anlatim metni **yavas belgesel temposunda, saniyede ~2 kelime** okunacak;
   toplam konusma penceresi `<speech_window>` saniyedir ve metin bu pencereye
   sigmalidir. `speech_window` cfg'den hesaplanir:
   `shots*shot_seconds - shots*2*micro_trim - 0.7`.
2. Metin TEK kesintisiz akistir ve **tam bir cumleyle biter**; yarim cumle,
   uc nokta ile asilma, "..." veya cliffhanger fragmani yasaktir.
3. Cekimler sessiz kesitlerdir ve tek bir kesintisiz seslendirmenin altinda
   akar: **cekim 2, cekim 1'in ayni anini/sahnesini dogrudan surdurur**;
   kesitte mekan sifirlanmaz, yeni bir sahne acilmaz. Kesme aninda soylenen
   cumle bolunmemis duyulmalidir.

Kural metinleri sadece `narrated` dalina eklenir; anlatimsiz (`humans_present`
ve visual-only) dallar DEGISMEZ.

## Kapsam disi (NON-GOALS)

- `series/produce.py`, `series/series_runner.py`, `series/shots.py` degismez.
- Diger kanallarin series.json / bible.json dosyalari degismez.
- `shots` sayisi 2 kalir; ucuncu cekim eklenmez.
- Yeni bagimlilik eklenmez.
- Yayin/onay akisi, QC kapilari, kredi kapilari degismez.
- `micro_trim`, `audio_smooth`, `title_card` degerleri degismez.
- Yayinlanmis planlara (part21 ve oncesi) dokunulmaz.

## PROOF

Yeni dosya: `tests/test_sh_anlatim_temposu.py`. Su yedi seyi kanitlar
(1-4 gercek ffmpeg calistirir, sentetik dosyalarla, agsiz ve ucretsiz):

1. **Kesme yok**: 3.0 sn sessiz video + 6.0 sn ton wav -> `mix_voiceover`
   ciktisinin suresi >= 6.4 sn ve ses akisi >= 6.0 sn.
2. **Hizlandirma tavani**: ayni senaryoda uretilen ffmpeg komutunda `atempo`
   carpani 1.05'i ASMAZ.
3. **Sigan durum bozulmaz**: 10.0 sn video + 3.0 sn wav -> cikti suresi
   ~10.0 sn (+-0.2) ve filtre zincirinde `atempo` YOK, `tpad` YOK.
4. **Uzatma tavani**: 3.0 sn video + 30.0 sn wav -> cikti suresi
   <= 3.0 + `NARRATION_MAX_EXTEND` + 0.2 ve WARNING loglanir.
5. **Kelime butcesi degismez kurali**: flashpoints series.json okunur,
   `max_words <= floor((shots*sec - shots*2*micro_trim - 0.7) * 2.05)`.
6. **TTS talimati**: `CHANNEL_NARRATION_CONFIG["shadowedhistory"]["instruction"]`
   icinde "fast", "pace tight", "no long dramatic pauses" GECMEZ; olculu
   tempo ifadesi GECER. Diger dort kanalin talimati degismemistir.
7. **Kuyruk**: part22..part25 planlarinda her `shots[*].duration == "10"`;
   part21'de hala `"8"`.

Proof komutu:

    python -X utf8 -m pytest tests/test_sh_anlatim_temposu.py -q

Regresyon komutu (mevcut ses testleri kirilmamali):

    python -X utf8 -m pytest tests/test_rocka_audio_master.py tests/test_diegetic_audio.py tests/test_doctrine_gate.py -q
