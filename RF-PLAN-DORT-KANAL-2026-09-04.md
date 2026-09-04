# RF-PLAN , dort kanalin gunluk otomatik yayini geri gelsin

**Tarih:** 2026-09-04 · **Surucu:** Claude (Visionary) · **Inceleyen:** Codex (Integrator)
**Kapsam:** `Wolkchen00/youtube-automation`, dort kanal: sentinal ihsan, AImagine,
Galactic Experiment, shad0wedhistory.
**Not:** Bu plan bugun bu makinede olculen canli kanitlara dayanir. Her olgu
asagida kosu numarasi, dosya:satir veya API cevabiyla birlikte verilmistir.

## CORE FOCUS (tek cumle)

Dort kanal da her gun otomatik yayin yapsin; yayin durursa sistem YESIL
gostermesin ve durus 24 saat icinde gorunur olsun.

---

## 1. TESHIS , canli kanit zinciri (2026-09-04, ~18:50 UTC olculdu)

### Olgu 0 , kanallarin gercek durumu (YouTube'un kendi RSS'i, pipeline degil)

| Kanal | Son yayin | Sessizlik |
|---|---|---|
| shad0wedhistory | 2026-09-03T22:52Z | 0.8 gun (saglikli) |
| AImagine | 2026-09-03T21:45Z | 0.9 gun (tek bacagi kirik) |
| sentinal ihsan | 2026-09-02T17:46Z | **2.0 gun** |
| Galactic Experiment | 2026-08-31T21:52Z | **3.9 gun** |

### Olgu 1 , Galactic sessizce oldu, uc kosu YESIL dondu

`gh run list`: Event Horizon Daily 09-01T19:29, 09-02T19:27, 09-03T19:22 , ucu de
`success`. Ayni gunlerde kanala **sifir video** cikti.

Kosu 33796096381'in uretim logu birebir:

    'event-horizon' Part 26: onay bekleyen yok (status=planned).
    🔁 event-horizon: kuyruk 0 < 2 → Gemini part 26-27 yaziyor…
    ⚠️ Ikmal dogrulamasi gecmedi (1. deneme): ['part 26: seed_id bu kosunun kart havuzunda yok (n15-32hex)']
    ⚠️ Ikmal dogrulamasi gecmedi (2. deneme): [... 'anlatim 53 kelime , hedef 30-44 disinda']
    ⚠️ Ikmal dogrulamasi gecmedi (3. deneme): ['part 26: seed_id konu havuzunda yok (999)']
    ⚠️ Ikmal dogrulamasi gecmedi (4. deneme): ['part 26: seed_id konu havuzunda yok (1000)']
    ⚠️ Ikmal dogrulamasi gecmedi (5. deneme): [... 'ardisik iki part ayni family ... (ölçek şoku)']
    ⚠️ Ikmal dogrulamasi gecmedi (6. deneme): ['part 26: seed_id konu havuzunda yok (99)']
    ❌ event-horizon oto-ikmal basarisiz: Gemini planlari dogrulamadan gecemedi
    ✅ 'event-horizon' tamamlandi (part 25/25).

Kosu exit 0 ile bitti.

### Olgu 2 , ikmalin gecememesinin KOKU: konu havuzu bos

`galactic_experience/event-horizon/calibration.json` -> `"extra_topics": []` (0 kayit),
`generated_at: 2026-08-30`.

`extra_topics` `series/calibrate.py:885` icinde `_bridge_notion` ile Notion'dan doldurulur.
Notion konu veritabani bugun salt-okunur sorgulandi (`NOTION_DB_GALACTIC_KONU`):

    toplam kart: 4 | has_more: False
    Durum dagilimi:  Durum=Aday  4

`series/calibrate.py:646-648` koprunun **`Onaylandı`** durumundaki kartlari aradigini
gosterir. Veritabaninin `Durum` secenekleri mevcut ve dogru
(`Aday, Onaylandi, Reddedildi, Uretildi, Claimed`), sema saglam. **Onayli tek kart yok**,
bu yuzden kopru sifir dondurdu, `extra_topics` bos kaldi, Gemini secebilecegi gecerli
bir `seed_id` bulamadi (`series/replenish.py:1047,1059` reddediyor).

**Bu bir kod hatasi degil, bos girdi. Ama kod bos girdiyi SESSIZ yutuyor.**

### Olgu 3 , yesil isigin tam yeri

`series/series_runner.py:604-607`:

    def run_next(slug, dry_run=False, publish=True, force=False) -> bool:
        meta = SeriesMeta.load(slug)
        if not meta:
            return False
        if meta.status != "active" or meta.next_part > meta.total_parts:
            logger.info(f"✅ '{slug}' tamamlandi (part {meta.total_parts}/{meta.total_parts}).")
            return True

Hicbir sey uretmeyen ve yayinlamayan kosu `True` doner, workflow adimi yesil olur,
nobetci sagliklı sanir. Ayni dosyadaki `_continue_after_terminal` docstring'i tam
tersini soyluyor: *"Kuyrukta bolum kaldiysa devam et; yoksa terminal hatayi basari
diye sunma."* Niyet var, bu yol onu ihlal ediyor.

### Olgu 4 , ayni ucurum shad0wedhistory'yi de bekliyor

`shadowedhistory/flashpoints/series.json`: `status=active`, `next_part=25`,
`total_parts=25`, `calibration.json -> extra_topics: 0`.
Yani **bir sonraki bolum sonuncusu**; ardindan flashpoints de event-horizon'un
dustugu yere duser. Kanal bugun saglikli gorunuyor, 1-2 gun sonra olur.

`series/calibrate.py` icinde `_bridge_notion` govdesinin ilk satiri:

    if slug != "event-horizon" or not enabled:
        return retained, notes

Kopru **yalnizca event-horizon icin** calisiyor. Diger uc serinin havuzu hicbir zaman
dolmuyor, sadece tukeniyor.

### Olgu 5 , AImagine tek bacakta ve o bacak kirik

`.github/workflows/from-scratch.yml` ve `next-stop.yml`: `schedule` bloklari
Ihsan kararlariyla (02.09 ve 03.09) yorum satirina alinmis, seriler `paused`.
Geriye aimagine kanalinin **tek gunluk seridi** kaldi: Fear Slide Daily.

Kosu 33897545943 (2026-09-04T16:52) birebir:

    ##[group]Run python -X utf8 AImagine-Fear/build.py --check
    Built and validated 9 routes.
    ##[group]Run python -X utf8 -m pytest AImagine-Fear/tests -q
    /opt/hostedtoolcache/Python/3.11.16/x64/bin/python: No module named pytest
    ##[error]Process completed with exit code 1.

`requirements.txt` icinde pytest YOK; `fear-slide.yml:80` pytest cagiriyor.
Kardes is akisi `fear-slide-hazir.yml` pytest cagirmadigi icin basarili.
Uretim adimina hic gelinmedi, kredi harcanmadi, video cikmadi.

### Olgu 6 , Sentinal'in tikanikligi: master ses kirpiyor

`sentinal_ihsan/unnatural-lab/series.json` part 28:
`{"status": "qc_retry", "retry_count": 1, "last_reason_code": "AUDIO_MASTER",
"hold_reason": "final ses dogrulamasi basarisiz"}`

Kosu 33806993734 logu birebir:

    🎚️ Ses master dogrulamasi ep28_narrated_music_mastered.mp4: I=-14.3 LUFS, TP=0.1 dBTP
    ❌ Ses master teslimati QC hold: final ses dogrulamasi basarisiz

`series/produce.py:_verify_audio_master` kapisi:
`abs(loudness - target_lufs) <= 1.0 and true_peak <= -1.0`.
LUFS gecti (0.3 sapma), **true-peak +0.1 dBTP ile kaldi** (tavan -1.0).
Yani teslim gercekten kirpiyor, kapi hakli.

`core/ffmpeg_tools.py:master_audio` zinciri: iki gecisli loudnorm ->
`aresample=96000, alimiter=limit=<target_tp - 2 dB>` -> `aresample=48000` -> AAC.
Limiter -3 dBTP'ye sinirliyor ama teslim +0.1 olcusuyor: **3.1 dB tasma**.
2 dB guvenlik payi bu malzemede yetmedi. ep27 ayni zincirden gecip yayinlandi,
yani tasma icerige bagli, sistematik degil.

### Olgu 7 , panonun korlugu (BU CEVRIMDE ZATEN DUZELTILDI, kayit icin)

Panonun okudugu yerel klon origin/main'in 51 commit gerisindeydi; 30 dakikada bir
kosan senkron gorevi her seferinde `fast-forward basarisiz: your local changes would
be overwritten` veriyordu. Pano bu yuzden Galactic'i YESIL gosteriyordu.
Yerel degisiklikler olculdu (9 dosyanin 7'si origin ile birebir ayni, `AImagine-Fear`
farklarinin 15/16'si sadece CRLF, `yayin.jsonl` yerel icerigi origin'in tam alt kumesi),
tamami yedeklendi, ff-merge yapildi, pano yeniden uretildi.
Pano artik Galactic'i KIRMIZI gosteriyor. Bu plana ROCK olarak girmez.

---

## 2. ROCK'LAR (bagimlilik sirasinda)

### ROCK 1 , Fear Slide test kapisi acilsin (AImagine bugun geri gelsin)

**Neden:** aimagine kanalinin TEK gunluk seridi eksik bir gelistirme bagimliligi
yuzunden uretime hic baslamadan oluyor.

**Ne yapilacak:** `.github/workflows/fear-slide.yml` "Install dependencies" adimina
pytest kurulumu eklenecek. Test kapisi KALIYOR (kredi harcamadan once kosuyor,
degerli). `requirements.txt` calisma zamani bagimlilik listesidir, pytest oraya
EKLENMEZ; is akisinda ayrica kurulur.

**Done looks like:** `fear-slide.yml` pytest kuruyor; YAML gecerli; test kapisi
yerelde gecıyor.

**PROOF:** `python -X utf8 AImagine-Fear/build.py --check && python -X utf8 -m pytest AImagine-Fear/tests -q`
(beklenen: `Built and validated 9 routes.` + `28 passed`)

### ROCK 2 , Yesil yalani bitsin (hicbir sey yayinlamayan kosu YESIL olmasin)

**Neden:** Olgu 1 + Olgu 3. Galactic dort gun oldu ve her gun "success" raporlandi.
Bu tek basina en pahali kusur: teshis edilemeyen olum.

**Ne yapilacak:** `series/series_runner.py` icindeki erken donus, uc durumu
BIRBIRINDEN AYIRACAK:

1. `status != "active"` (Ihsan bilerek `paused`/`completed` yapmis) -> bu bir
   BASARI degil ama HATA da degil. "yapacak is yok" olarak raporlanir, kosu
   yesil kalabilir ama log ve `last_run.json` bunu **acikca** yazar.
2. `status == "active"` ve `next_part > total_parts` (seri tukendi, ikmal
   yapilamadi) -> **BASARISIZLIK**. Kosu kirmizi olmali, Telegram alarmi gitmeli.
   Bu tam olarak Galactic'in durumu.
3. Normal uretim yolu , degismez.

**Kritik kisit:** `paused` seriler (from-scratch, next-stop ve 10+ pasif seri)
kirmizi YANMAMALI. Ihsan onlari bilerek durdurdu; hepsini kirmiziya cevirmek
alarm gurultusu yaratir ve gercek alarmi bogar. Ayrim `status` uzerinden yapilir.

**Done looks like:** aktif ama tukenmis seri icin `run_next` basarisizlik
raporlar; pasif seri icin sessiz "yapacak is yok" raporlar; mevcut testler yesil.

**PROOF:** `python -X utf8 -m pytest tests/ -q -k "runner or exhaust or replenish or hold"`
artı yeni test dosyasi `tests/test_tukenmis_seri_yesil_degil.py` (bu rock'ta
yazilacak): aktif+tukenmis -> basarisiz, paused -> basarisiz DEGIL.

### ROCK 3 , Pist uzunlugu alarmi (ucuruma DUSMEDEN once haber ver)

**Neden:** Olgu 4. flashpoints su an 25/25; hicbir sey onu ucurumdan once
bildirmiyor. Galactic'te de bildirmedi.

**Ne yapilacak:** Aktif her seri icin "pist" olculecek:
`kalan_bolum = total_parts - next_part + 1` ve `havuzdaki_kullanilabilir_konu`
(calibration.json `extra_topics` icinden henuz kullanilmamis olanlar).
Pist esigin altina duserse (varsayilan 3 gun) UYARI uretilir ve Telegram'a gider.
Pist 0 ise bu ROCK 2'nin basarisizlik yoluyla ayni sinifta raporlanir.

**Done looks like:** tek bir fonksiyon/CLI aktif serilerin pistini raporlar;
flashpoints bugun "pist 1 bolum, havuz 0" diye UYARI verir; unnatural-lab
"pist 4 bolum, havuz 0" verir.

**PROOF:** yeni `tests/test_pist_alarmi.py` + gercek repo verisiyle elle kosu:
komut flashpoints ve unnatural-lab icin uyari basar.

### ROCK 4 , Master ses true-peak tavani gercekten tutsun (Sentinal geri gelsin)

**Neden:** Olgu 6. Kapi hakli, teslim kirpiyor; part 28 bu yuzden asili.

**Ne yapilacak:** `core/ffmpeg_tools.py:master_audio` teslim zincirinde true-peak
tavani AAC kodlamasindan SONRA da tutmali. Kok neden arastirilacak:
limiter'dan sonraki `aresample=48000` yeniden ornekleme tasmasi mi, AAC codec
tasmasi mi, yoksa guvenlik payi mi yetersiz. Cozum olcumle secilecek, tahminle degil.

**Kritik kisit:** Ses hedefi degistirilmeyecek (I=-14 LUFS, TP<=-1.0 dBTP sozlesme).
Kapi (`_verify_audio_master`) GEVSETILMEYECEK; kapiyi gevsetmek kirpan videoyu
yayinlamak demektir. Duzeltme uretim tarafinda olacak.

**Done looks like:** ayni girdi malzemesinden uretilen master `TP <= -1.0 dBTP`
olcusuyor ve `_verify_audio_master` geciyor.

**PROOF:** yeni `tests/test_master_true_peak.py`: ffmpeg ile sentetik yuksek-tepe
bir girdi uretir, `master_audio` cagirir, `measure_audio_loudness` ile olcer,
`true_peak <= -1.0` dogrular. Ek olarak mevcut ses testleri yesil kalir.

---

## 3. NON-GOALS (bu cevrimde YAPILMAYACAK)

- Notion'daki 4 konu kartini onaylamak. Bu **icerik karari** ve kredi harcatir;
  Ihsan'a soruldu, kod tarafi degil.
- `_bridge_notion`'i diger uc seriye acmak. Her kanalin ayri konu veritabani
  olup olmadigi belirsiz (`.env` icinde yalniz `NOTION_DB_GALACTIC_KONU` var).
  Once Ihsan'a sorulacak, sonra ayri cevrimde yapilacak. ISSUES'a yazildi.
- `from-scratch` / `next-stop` serilerini yeniden acmak. Ihsan bilerek durdurdu.
- Pano (`Proje_Dashboard`) kodu. Ayri repo, ayri is; bu cevrimde yalnizca
  senkronu kurtarildi.
- Kanallara elle video yayinlamak.
- Kie/Gemini kota ve butce mimarisi (`budget_exhausted` part 25-26). ISSUES'a yazildi.

## 4. KISITLAR

- Bu depo CANLI uretim yapar ve gercek para harcar. Hicbir rock uretim tetiklemez.
- Calisma dizini bir git worktree'dir; ana agac baska oturumlarca kullaniliyor olabilir.
- Mevcut testler yesil kalmali: `python -X utf8 -m pytest tests/ -q`.
- `.github/workflows/` icindeki cron saatleri DEGISTIRILMEYECEK.
- Turkce log/yorum uslubu korunacak; dosyalarda em-dash kullanilmayacak.
