"""wild-encounter tek plan 10 sn sozlesmesini tek komutta denetler.

RF-PLAN-TEKPLAN10.md Rock 4(g). Salt okunur: hicbir dosyayi degistirmez.
Cikis 0 = temiz, 1 = en az bir ihlal.

Kullanim (depo kokunden):
    python tools/rf_tekplan_kontrol.py

Neden var: Rock 1'in ilk hali yalnizca sayilari kontrol ediyordu ve bayat
"haze"/"green screen" metniyle YESIL gecerdi. Bu betik alan degerlerini,
yasak/zorunlu terimleri, yayin defterinin degismezligini ve doktrin damgasini
birlikte denetler.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unicodedata
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
SERI = KOK / "sentinal_ihsan" / "wild-encounter"

# Olculmus bulgu (REFERANS-AYUSH-ANALIZ.md): sis kaybeden videolarda var,
# kazananlarda yok; perde MAVI. Hem Ingilizce hem Turkce karsiliklari yasak.
YASAK_TERIMLER = [
    "haze", "fog", "smoke",
    "green screen", "greenscreen",
    "sis", "duman", "yesil perde",
]
ZORUNLU_TERIM = "blue screen"

# "sis" gibi kisa terimler kelime icinde yanlis eslesmesin (ornek: "consist").
KELIME_SINIRI_GEREKTIREN = {"sis", "duman", "fog", "haze", "smoke"}


def normalize(metin: str) -> str:
    """Buyuk/kucuk harf ve Turkce aksan farkini kaldirir."""
    metin = metin.replace("ı", "i").replace("İ", "i")
    metin = unicodedata.normalize("NFKD", metin)
    metin = "".join(ch for ch in metin if not unicodedata.combining(ch))
    return metin.lower()


def yasak_bul(metin: str) -> list[str]:
    import re
    d = normalize(metin)
    bulunan = []
    for terim in YASAK_TERIMLER:
        t = normalize(terim)
        if t in KELIME_SINIRI_GEREKTIREN:
            if re.search(rf"\b{re.escape(t)}\b", d):
                bulunan.append(terim)
        elif t in d:
            bulunan.append(terim)
    return bulunan


def guncel_format_bolumu(doktrin: str) -> str:
    """DOKTRIN'in YALNIZ GUNCEL FORMAT bolumu.

    Tarihsel bolumler kasitli olarak eski yesil-perde/sis derslerini tasir;
    onlari denetlemek yanlis alarm olur.
    """
    bas = doktrin.index("## GUNCEL FORMAT")
    kalan = doktrin[bas + 10:]
    sonraki = kalan.find("\n## ")
    return doktrin[bas:bas + 10 + sonraki] if sonraki != -1 else doktrin[bas:]


def main() -> int:
    hatalar: list[str] = []

    bible = json.loads((SERI / "bible.json").read_text(encoding="utf-8"))
    series = json.loads((SERI / "series.json").read_text(encoding="utf-8"))
    doktrin = (SERI / "DOKTRIN.md").read_text(encoding="utf-8")
    s = bible["series"]
    ar = series["auto_replenish"]

    # ---------------------------------------------------------------- alanlar
    beklenen = [
        ("series.json auto_replenish.shots", ar.get("shots"), 1),
        ("series.json auto_replenish.shot_seconds", str(ar.get("shot_seconds")), "10"),
        ("series.json auto_replenish.format_version", ar.get("format_version"), "plato-3x8"),
        ("series.json status", series.get("status"), "paused"),
        ("bible.json series.duration_band", s.get("duration_band"), [9, 11]),
        ("bible.json series.chain_frames", s.get("chain_frames"), False),
        ("bible.json series.micro_trim", s.get("micro_trim"), 0),
        ("bible.json series.qc.min_shots", s["qc"].get("min_shots"), 1),
        ("bible.json series.qc.scene_cut_fail", s["qc"].get("scene_cut_fail"), False),
    ]
    for ad, gelen, bkl in beklenen:
        if gelen != bkl:
            hatalar.append(f"{ad}: {gelen!r} olmali {bkl!r}")

    if len(ar.get("shot_plan") or []) != 1:
        hatalar.append(
            f"series.json auto_replenish.shot_plan: {len(ar.get('shot_plan') or [])} oge, 1 olmali"
        )

    # Ihsan'in yuzu DEGISMEZ (Ihsan karari, 13 Eylul).
    kar = (bible.get("characters") or [{}])[0]
    if kar.get("character_id") != "92369a8131e7497abf00c3b5ba1c92c9":
        hatalar.append("bible.json characters[0].character_id degismis (Ihsan'in yuzu)")
    if not str(kar.get("ref_image_url") or "").startswith("https://"):
        hatalar.append("bible.json characters[0].ref_image_url bos ya da bozuk")

    # ---------------------------------------------------- yasak / zorunlu dil
    # SIKI alanlar SAHNEYI TARIF EDER: terim hic gecmemeli.
    siki = {
        "bible.json art_style": bible.get("art_style", ""),
        "series.json auto_replenish.shot_plan[0]": (ar.get("shot_plan") or [""])[0],
    }
    for e in bible.get("environments", []):
        siki[f"bible.json environments[{e['id']}].desc"] = e.get("desc", "")

    for ad, metin in siki.items():
        bulunan = yasak_bul(metin)
        if bulunan:
            hatalar.append(f"{ad}: yasak terim {bulunan}")

    for ad in ("bible.json art_style", "series.json auto_replenish.shot_plan[0]"):
        if ZORUNLU_TERIM not in normalize(siki[ad]):
            hatalar.append(f"{ad}: zorunlu terim {ZORUNLU_TERIM!r} yok")

    # KURAL alanlari sisi YASAKLAMAK icin anabilir ("sis YASAK", "haze are NOT
    # expected"). Burada aranan sey terimin varligi degil, OLUMLAYICI kullanimi.
    kural = {
        "bible.json series.qc.notes": s["qc"].get("notes", ""),
        "series.json auto_replenish.brief": ar.get("brief", ""),
        "DOKTRIN.md GUNCEL FORMAT": guncel_format_bolumu(doktrin),
    }
    OLUMLAYICI = [
        "haze are expected", "haze and lens flare are intended",
        "stay welcome", "haze is expected", "sis serbest", "sis vardir",
        "with practical haze", "green screen wall",
    ]
    for ad, metin in kural.items():
        d = normalize(metin)
        gecen = [k for k in OLUMLAYICI if normalize(k) in d]
        if gecen:
            hatalar.append(f"{ad}: sis/yesil perde OLUMLAYICI kullanim {gecen}")
    # Kural metinleri sisi acikca yasaklamis olmali (sessizce dusurulmus olmasin).
    for ad, metin in kural.items():
        d = normalize(metin)
        if not any(k in d for k in ("air is clear", "sis, duman", "sis yasak",
                                    "not expected set elements")):
            hatalar.append(f"{ad}: sis yasagi acikca yazili degil")

    # Tarif degisti: eski sisli/yesil gorseller yeni prompta sizmamali.
    for e in bible.get("environments", []):
        if e.get("ref_image_url"):
            hatalar.append(
                f"bible.json environments[{e['id']}].ref_image_url dolu; "
                "tarif degistigi icin bosaltilmaliydi"
            )

    # ---------------------------------------------------------- part08 plani
    p08 = SERI / "plans" / "part08.json"
    if not p08.exists():
        hatalar.append("plans/part08.json yok")
    else:
        plan = json.loads(p08.read_text(encoding="utf-8"))
        if len(plan.get("shots") or []) != 1:
            hatalar.append(f"part08: {len(plan.get('shots') or [])} cekim, 1 olmali")
        elif str(plan["shots"][0].get("duration")) != "10":
            hatalar.append(f"part08: sure {plan['shots'][0].get('duration')!r}, '10' olmali")
        if not isinstance(plan.get("object_card"), dict):
            hatalar.append("part08: object_card yok (produce.py Plato capasini reddeder)")
        else:
            for alan in ("name", "descriptor", "environment", "framing", "anomaly_descriptor"):
                if not str(plan["object_card"].get(alan) or "").strip():
                    hatalar.append(f"part08: object_card.{alan} bos")
        # doktrin damgasi guncel DOKTRIN ile birebir eslesmeli
        sys.path.insert(0, str(KOK))
        from series.bible import doctrine_sha256  # noqa: E402
        guncel = doctrine_sha256(SERI / "DOKTRIN.md")
        if str(plan.get("doctrine_sha256") or "").lower() != guncel:
            hatalar.append(
                f"part08: doctrine_sha256 bayat ({plan.get('doctrine_sha256')}), "
                f"guncel {guncel}"
            )

    # kuyrukta cok cekimli uretilmemis plan kalmamali
    for yol in sorted((SERI / "plans").glob("part*.json")):
        n = int(yol.stem.replace("part", ""))
        if n < 8:
            continue  # part05-07 yayinlandi, tarihi kayit
        plan = json.loads(yol.read_text(encoding="utf-8"))
        if len(plan.get("shots") or []) != 1:
            hatalar.append(f"{yol.name}: kuyrukta {len(plan.get('shots') or [])} cekimli plan var")

    # ------------------------------------------------- yayin defteri degismez
    pub = SERI / "published.json"
    ozet = hashlib.sha256(pub.read_bytes()).hexdigest()
    try:
        r = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", str(pub.relative_to(KOK))],
            cwd=KOK, capture_output=True,
        )
        if r.returncode == 1:
            hatalar.append("published.json DEGISMIS; yayin defteri dokunulmaz olmaliydi")
    except OSError:
        pass  # git yoksa sessiz gec, ozet yine de basilir

    # ----------------------------------------------------------------- rapor
    if hatalar:
        print("TEK PLAN KONTROL: BASARISIZ")
        for h in hatalar:
            print("  -", h)
        return 1

    print("TEK PLAN KONTROL: TEMIZ")
    print(f"  cekim=1 sure=10sn band={s['duration_band']} status={series['status']}")
    print(f"  zincir={s['chain_frames']} micro_trim={s['micro_trim']} min_shots={s['qc']['min_shots']}")
    print(f"  part08={json.loads(p08.read_text(encoding='utf-8'))['episode']['title']}")
    print(f"  published.json sha256={ozet[:16]}... (degismedi)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
