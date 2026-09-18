"""still-home kuyrugunu SILUET KURALINA gore denetle, para harcamadan.

Dayanak: shadowedhistory/KONSEPT.md 2.2.1 (v3.0, 18 Eylul 2026).

Olculen gerekce: part 3'un teknolojisi bir ISIKTI (Eyfel'in enerji omurgasi).
Isigin kapali hali oldugu icin motor once bugunun Paris'ini cizdi ve isigi
1,25 saniyede acti. Ilk kare bugunun drone fotografindan ayirt edilemiyordu
ve bolum 21 izlenmede kaldi (P1 648, P2 875). Bu denetim ayni kazayi bir
daha ucret odemeden yakalar.

Denetlenen bes kural:
  1. Cekim 1'de durum-gecisi dili YASAK (once/sonra hali olan her kalip).
  2. Zayiflik dili YASAK: kanca "subtle" olamaz.
  3. Isik surucu aileler (enerji mimarisi, yasayan malzeme) GECE ya da
     alacakaranlik gecer.
  4. HER cekimde pozitif dil (doktrin kural 9), SABLON on-eki dahil.
  5. Plan damgasi guncel doktrinle eslesir.

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

ISIK_SURUCU_AILELER = {"enerji mimarisi", "yasayan malzeme"}
KARANLIK = ["night", "dusk", "evening", "after dark", "twilight", "nightfall",
            "moonlit", "at dark"]


def _bulgular_prompt(metin: str, kalipar: list[str], etiket: str) -> list[str]:
    dusuk = metin.lower()
    return [f"{etiket}: {k!r}" for k in kalipar if k in dusuk]


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
    try:
        meta = json.loads((SERIES_DIR / "series.json").read_text(encoding="utf-8"))
        siradaki = int(meta.get("next_part") or 1)
    except Exception:
        siradaki = 1

    toplam = 0
    denetlenen = 0
    for plan_yolu in planlar:
        eslesme = PART_NAME.search(plan_yolu.name)
        if eslesme and not args.plan and int(eslesme.group(1)) < siradaki:
            continue
        denetlenen += 1
        bulgular = denetle(plan_yolu, guncel_damga)
        if bulgular:
            toplam += len(bulgular)
            print(f"\n[BULGU] {plan_yolu.name}")
            for b in bulgular:
                print(f"   - {b}")
        else:
            print(f"[temiz] {plan_yolu.name}")

    print(f"\nDenetlenen plan: {denetlenen} (part {siradaki} ve sonrasi), "
          f"bulgu: {toplam}")
    return 1 if toplam else 0


if __name__ == "__main__":
    raise SystemExit(main())
