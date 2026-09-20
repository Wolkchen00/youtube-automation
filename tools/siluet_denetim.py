"""still-home kuyrugunu SILUET KURALINA gore denetle, para harcamadan.

Dayanak: shadowedhistory/KONSEPT.md 2.2.1 (v3.0, 18 Eylul 2026).

Olculen gerekce: part 3'un teknolojisi bir ISIKTI (Eyfel'in enerji omurgasi).
Isigin kapali hali oldugu icin motor once bugunun Paris'ini cizdi ve isigi
1,25 saniyede acti. Ilk kare bugunun drone fotografindan ayirt edilemiyordu
ve bolum 21 izlenmede kaldi (P1 648, P2 875). Bu denetim ayni kazayi bir
daha ucret odemeden yakalar.

Denetlenen yedi kural:
  1. Cekim 1'de durum-gecisi dili YASAK (once/sonra hali olan her kalip).
  2. Zayiflik dili YASAK: kanca "subtle" olamaz.
  3. Isik surucu aileler (enerji mimarisi, yasayan malzeme) GECE ya da
     alacakaranlik gecer.
  4. HER cekimde pozitif dil (doktrin kural 9), SABLON on-eki dahil.
  5. Plan damgasi guncel doktrinle eslesir.
  6. KISI BICIMLI ANIT ya da gercek kisi adi YASAK (doktrin kural 7).
  7. Caption IKI DILLI (kural 14). Bu kural UYARI uretir, cikis kodunu
     etkilemez: eksik caption yayini durdurmaz, yalniz erisimi yariya
     dusurur. Sert kapisi tests/test_yayin_durdu_2026_09_20.py icinde.

Kural 6'nin olculen gerekcesi (19 Eylul 2026, kosu 35473217835): part 5
Rio'nun cekim 1 ve cekim 3 prompt'lari "Christ the Redeemer" yaziyordu.
Doktrin 7 zaten "gercek kisi YOK" diyordu ama hicbir kapi bunu denetlemiyordu.
Cekim 3'un regen'i saglayicida "flagged for containing a prominent public
figure" ile 5/5 bloklandi, cekim dustu, min_shots=4 kapisi bolumu oldurdu ve
kanal o gun karanlik kaldi. Ayni sinif KONSEPT 8.1'de zaten yaziliydi:
qc.notes'un (ve doktrinin) YASAKLADIGINI prompt ISTEYEMEZ.

Kullanim:
    py -X utf8 tools/siluet_denetim.py
    py -X utf8 tools/siluet_denetim.py --plan shadowedhistory/still-home/plans/part04.json

Cikis kodu:
    0  temiz
    1  en az bir bulgu
    2  denetimin kendisi kosamadi
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

SERIES_DIR = REPO / "shadowedhistory" / "still-home"
PART_NAME = re.compile(r"part(\d+)\.json$")

# Hepsinin bir ONCE hali vardir; motor onceyi de cizer.
DURUM_GECISI = [
    "begins to", "starts to", "gradually", "slowly reveals", "comes to life",
    "springs to life", "powers up", "powering up", "activates", "activating",
    "lights up", "lighting up", "flickers", "awakens", "awakening",
    "switches on", "turns on", "comes online", "unfolds", "unfolding",
    "assembles", "assembling", "brightens", "brightening", "rises into view",
    "emerges", "emerging", "fades in", "reveals itself",
]

# Kanca zayif olamaz.
ZAYIFLIK = ["subtle", "subtly", "softly", "gently", "faintly", "barely", "hint of"]

# Doktrin kural 9: gorsel prompt yalniz kadrajda BULUNAN seyleri soyler.
# Difuzyon olumsuzu cizer. Bu liste TAM prompt'a uygulanir (sablon on-eki
# DAHIL), cunku forbidden_phrases yalniz modelin yazdigi kisma bakar ve
# 18 Eylul'de sablonun kendisi kurali uc kez cignedi.
OLUMSUZ_DIL = (
    "no", "not", "never", "nothing", "neither", "nor", "without",
    "avoid", "cannot", "absent", "lacks", "lacking",
)

# Doktrin kural 7: "Marka, gercek sirket logosu, gercek kisi YOK".
# Liste TEK yerde durur (series/omni_api.py), cunku ayni adlar calisma aninda
# da temizleniyor. Kapi ile kurtarma yolunun ayni listeyi gormesi sarttir.
try:
    from series.omni_api import PUBLIC_FIGURE_SUBJECTS
except Exception:                      # denetim, import yuzunden COKMEZ
    PUBLIC_FIGURE_SUBJECTS = ()

# Caption kural 14: once INGILIZCE blok, sonra SEHRIN KENDI DILI.
# Bu kusur yayini DURDURMAZ, erisimi yariya dusurur, bu yuzden UYARI olarak
# raporlanir ve cikis kodunu etkilemez: gunun videosunu eksik caption yuzunden
# oldurmek daha kotu bir takas olurdu. Sert kapi testlerdedir
# (tests/test_yayin_durdu_2026_09_20.py).
#
# Olculen gerekce (20 Eylul 2026): part05 (Rio/Portekizce) ve part06
# (Tokyo/Japonca) caption'lari TEK DILLIYDI, yani kural 14 kuyrukta iki kez
# cignenmisti ve hicbir kapi bakmiyordu.
# Caption kural 14: once INGILIZCE blok, sonra SEHRIN KENDI DILI.
# Kural ve yazi sistemi tablosu series/replenish.py icinde TEK yerde durur;
# burada yalniz kunye cumlesi tutulur, cunku o seriye aittir.
#
# Bu kusur yayini DURDURMAZ, erisimi yariya dusurur: bu yuzden UYARI olarak
# raporlanir ve cikis kodunu etkilemez. Gunun videosunu eksik caption yuzunden
# oldurmek daha kotu bir takas olurdu. Sert kapi testlerdedir
# (tests/test_yayin_durdu_2026_09_20.py) ve ikmal dongusundedir.
#
# Olculen gerekce (20 Eylul 2026): part05 (Rio/Portekizce) ve part06
# (Tokyo/Japonca) caption'lari TEK DILLIYDI ve hicbir kapi bakmiyordu.
INGILIZCE_KUNYE = "A fictional future, created with AI."

ISIK_SURUCU_AILELER = {"enerji mimarisi", "yasayan malzeme"}
KARANLIK = ["night", "dusk", "evening", "after dark", "twilight", "nightfall",
            "moonlit", "at dark"]


def _bulgular_prompt(metin: str, kalipar: list[str], etiket: str) -> list[str]:
    dusuk = metin.lower()
    return [f"{etiket}: {k!r}" for k in kalipar if k in dusuk]


def caption_uyarilari(plan: dict, havuz: list) -> list[str]:
    """Kural 14 uyarilari. Kural TEK YERDE yasar: series/replenish.py.

    Burada kopyalanmaz, cunku ayni kuralin iki kopyasi kacinilmaz olarak
    ayrisir. Ikmal dongusu ayni fonksiyonu HATA olarak, bu arac UYARI olarak
    kullanir: eksik caption yayini durdurmaz, yalniz erisimi yariya dusurur.
    """
    try:
        from series.replenish import caption_language_errors
    except Exception as hata:          # denetim, import yuzunden COKMEZ
        return [f"caption denetimi yuklenemedi: {hata}"]
    cfg = {
        "topic_pool": havuz or [],
        "caption_bilingual_disclosure": INGILIZCE_KUNYE,
    }
    return caption_language_errors(plan, cfg)


def denetle(plan_yolu: pathlib.Path, guncel_damga: str | None) -> list[str]:
    """Tek bir plan dosyasi icin bulgu listesi dondur."""
    try:
        plan = json.loads(plan_yolu.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as hata:
        return [f"plan okunamadi: {hata}"]

    bulgular: list[str] = []
    cekimler = plan.get("shots") or []
    if not cekimler:
        return ["planda cekim yok"]

    cekim1 = str(cekimler[0].get("prompt") or "")
    bulgular += _bulgular_prompt(cekim1, DURUM_GECISI, "cekim 1 durum-gecisi dili")
    bulgular += _bulgular_prompt(cekim1, ZAYIFLIK, "cekim 1 zayiflik dili")

    # Kural 9, HER cekimde ve TAM prompt uzerinde (sablon on-eki dahil).
    for cekim in cekimler:
        n = cekim.get("n") or "?"
        metin = str(cekim.get("prompt") or "")
        hits = sorted({
            kelime for kelime in OLUMSUZ_DIL
            if re.search(rf"\b{re.escape(kelime)}\b", metin, re.I)
        })
        if hits:
            bulgular.append(
                f"cekim {n} olumsuz dil (doktrin kural 9): " + ", ".join(repr(h) for h in hits)
            )

    # Kural 7: kisi bicimli anit / gercek kisi. Prompt'un yani sira caption ve
    # kunye de denetlenir, cunku ad oralardan da sizabilir.
    for etiket, metin in (
        [(f"cekim {c.get('n') or '?'}", str(c.get("prompt") or "")) for c in cekimler]
        + [("caption", str(plan.get("caption") or "")),
           ("kunye", json.dumps(plan.get("title_card") or {}, ensure_ascii=False))]
    ):
        dusuk = metin.lower()
        adlar = sorted({ad for ad in PUBLIC_FIGURE_SUBJECTS if ad in dusuk})
        if adlar:
            bulgular.append(
                f"{etiket} kisi bicimli anit/gercek kisi adi geciyor "
                "(doktrin kural 7, saglayici bunu 'prominent public figure' diye "
                "bloklar): " + ", ".join(repr(a) for a in adlar)
            )

    aile = str(plan.get("family") or "")
    if aile in ISIK_SURUCU_AILELER:
        govde = (cekim1 + " " + str(plan.get("synopsis") or "")).lower()
        if not any(k in govde for k in KARANLIK):
            bulgular.append(
                f"aile {aile!r} isik surucudur ve GECE/alacakaranlik gecmek "
                "zorundadir; cekim 1 ve sinopsiste karanlik isareti yok"
            )

    if guncel_damga:
        damga = str(plan.get("doctrine_sha256") or "").strip().lower()
        if damga != guncel_damga:
            bulgular.append("plan doktrin damgasi guncel KONSEPT.md ile eslesmiyor")

    return bulgular


def main(argv: list[str] | None = None) -> int:
    ayristirici = argparse.ArgumentParser(
        description="still-home kuyrugunu siluet kuralina gore denetle")
    ayristirici.add_argument("--plan", action="append", default=None,
                             help="tek bir plan dosyasi (yinelenebilir)")
    ayristirici.add_argument("--next-only", action="store_true",
                             help="yalniz next_part'i denetle (uretim oncesi sert kapi)")
    args = ayristirici.parse_args(argv)

    try:
        from series.bible import doctrine_path, doctrine_sha256
        yol = doctrine_path("still-home")
        guncel_damga = doctrine_sha256(yol) if yol else None
    except Exception as hata:          # denetim, doktrin okunamadi diye COKMEZ
        print(f"UYARI: doktrin damgasi okunamadi: {hata}")
        guncel_damga = None

    if args.plan:
        planlar = [pathlib.Path(p) for p in args.plan]
    else:
        plan_dizini = SERIES_DIR / "plans"
        if not plan_dizini.is_dir():
            print(f"HATA: plan dizini yok: {plan_dizini}")
            return 2
        planlar = sorted(p for p in plan_dizini.glob("part*.json")
                         if PART_NAME.search(p.name))

    if not planlar:
        print("HATA: denetlenecek plan bulunamadi")
        return 2

    # Yalniz kuyrukta bekleyen bolumleri denet: yayinlanmis bolumu geri
    # donup suclamak yanlis alarm uretir.
    havuz: list = []
    try:
        meta = json.loads((SERIES_DIR / "series.json").read_text(encoding="utf-8"))
        siradaki = int(meta.get("next_part") or 1)
        havuz = (meta.get("auto_replenish") or {}).get("topic_pool") or []
    except Exception:
        siradaki = 1

    # --next-only: yalniz BU KOSUDA uretilecek bolum. Uretim oncesi sert kapi
    # boyle kurulur, cunku kuyrugun ilerisindeki bir bulgu bu gecenin yayinini
    # oldurmemeli; para harcanacak bolum neyse kapi onu denetler.
    if args.next_only and not args.plan:
        hedef = SERIES_DIR / "plans" / f"part{siradaki:02d}.json"
        if not hedef.is_file():
            print(f"HATA: siradaki bolum plani yok: {hedef}")
            return 2
        planlar = [hedef]
        print(f"Sert kapi: yalniz part {siradaki} denetleniyor (uretilecek bolum).")

    toplam = 0
    toplam_uyari = 0
    denetlenen = 0
    for plan_yolu in planlar:
        eslesme = PART_NAME.search(plan_yolu.name)
        if (eslesme and not args.plan and not args.next_only
                and int(eslesme.group(1)) < siradaki):
            continue
        denetlenen += 1
        bulgular = denetle(plan_yolu, guncel_damga)
        try:
            plan = json.loads(plan_yolu.read_text(encoding="utf-8"))
            uyarilar = caption_uyarilari(plan, havuz)
        except Exception as hata:
            uyarilar = [f"caption denetlenemedi: {hata}"]
        if bulgular:
            toplam += len(bulgular)
            print(f"\n[BULGU] {plan_yolu.name}")
            for b in bulgular:
                print(f"   - {b}")
        elif not uyarilar:
            print(f"[temiz] {plan_yolu.name}")
        # Caption kusuru yayini DURDURMAZ: UYARI olarak basilir ve cikis
        # kodunu etkilemez. Sert kapi testlerdedir.
        if uyarilar:
            toplam_uyari += len(uyarilar)
            print(f"[UYARI] {plan_yolu.name}")
            for u in uyarilar:
                print(f"   ! {u}")

    print(f"\nDenetlenen plan: {denetlenen} (part {siradaki} ve sonrasi), "
          f"bulgu: {toplam}, uyari: {toplam_uyari}")
    return 1 if toplam else 0


if __name__ == "__main__":
    raise SystemExit(main())
