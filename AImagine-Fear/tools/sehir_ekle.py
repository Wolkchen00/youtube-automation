"""Sehir tanimindan tam bir rota dosyasi uretir.

Neden var: denetim, en olasi hatanin "mevcut rotayi kopyalayip sadece ust bloktaki
alanlari degistirmek" oldugunu gosterdi. O zaman prompt icinde Paris/Las Vegas,
acid green/cyan gibi celiskiler yan yana duruyor ve build.py bunu yakalamiyor.
Burada govde metni PARAMETRELI, yani celiski YAPISAL OLARAK imkansiz.

Kullanim:
    python tools/sehir_ekle.py --liste
    python tools/sehir_ekle.py dubai-burj-altin
    python tools/sehir_ekle.py --hepsi
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
# 2026-09-14 Ihsan karari: bacaklar ciplak (rota dosyalari bu yazimi tasiyor).
LEGWEAR = "a black high-cut one-piece swimsuit, legs bare from the hip down"

# Her sehir: slug, sehir, landmark, neon rengi, hava, bacak giysisi, havuz rengi,
# manzara imzasi (o sehri o sehir yapan tek fiziksel detay), aciklama fiili/birimi.
SEHIRLER = {
    "vegas-strat-blue-rain": None,   # zaten var, elle yazildi
    "toronto-cn-red-dusk": None,     # zaten var, elle yazildi
    "dubai-burj-altin": dict(
        # 24,5M (6 Eyl). Alanlar 15 Kas'ta bugunku rota dosyasina esitlendi.
        sehir="Dubai", landmark="the Burj Khalifa", neon="ember orange",
        palet="sicak", anahtar="Burj", isik="mavi-beyaz",
        hava="a clear hot night with dust haze on the horizon",
        havuz="gold-lit", etiket="#DubaiBurjKhalifa",
        imza="the dead-straight strip of Sheikh Zayed Road running to the horizon and the black "
             "emptiness of the desert beyond the last towers",
        alt_imza="the artificial islands sitting in the dark gulf water to one side",
        fiil="falling past", birim="second", sifatlar="faster, hotter, and higher",
        emoji="\U0001F311\U0001F4A6",
        basliklar=(
            "Burj Khalifa 828m drop #shorts",
            "I slid off the Burj tonight #shorts",
            "Burj Khalifa, no floor #shorts",
        ),
    ),
    "newyork-empire-magenta-kar": dict(
        sehir="New York", landmark="the Empire State Building", neon="hot magenta-pink",
        hava="heavy night snow, fat flakes crossing the lens",
        giysi="black glossy wet-look leggings with the hem at mid-shin",
        havuz="pink-lit", etiket="#NYCEmpireState",
        imza="the perfect rectangular grid of Manhattan avenues glowing amber to the water on "
             "both sides",
        alt_imza="the black rectangle of Central Park cut into the grid",
        fiil="dropping past", birim="second", sifatlar="colder, faster, and steeper",
        emoji="❄️\U0001F4A6",
    ),
    "tokyo-skytree-mor-yagmur": dict(
        sehir="Tokyo", landmark="the Tokyo Skytree", neon="electric violet",
        hava="warm night rain, the whole city under a low orange cloud lid",
        giysi="black glossy wet-look leggings with the hem at mid-shin",
        havuz="violet-lit", etiket="#TokyoSkytree",
        imza="the endless low grey sprawl with no grid at all, cut by white expressway lines "
             "curving between the blocks",
        alt_imza="a dense knot of coloured signage glowing in one district below",
        fiil="falling through", birim="second", sifatlar="wetter, faster, and louder",
        emoji="\U0001F327️\U0001F4A6",
    ),
    "sanghay-inci-yesil-sis": dict(
        sehir="Shanghai", landmark="the Oriental Pearl Tower", neon="acid green",
        hava="thick night fog sitting between the towers",
        giysi="black glossy wet-look leggings with the hem at mid-shin",
        havuz="green-lit", etiket="#ShanghaiPearl",
        imza="the wide black curve of the Huangpu river splitting the lights, with the old low "
             "waterfront on one bank and the tower cluster on the other",
        alt_imza="ship lights crawling along the black water far below",
        fiil="sliding down past", birim="turn", sifatlar="blinder, faster, and colder",
        emoji="\U0001F32B️\U0001F4A6",
    ),
    "paris-eyfel-beyaz-cise": dict(
        sehir="Paris", landmark="the Eiffel Tower", neon="cold white-blue",
        hava="fine night drizzle, every street lamp wearing a halo",
        giysi="black glossy wet-look leggings with the hem at mid-shin",
        havuz="white-lit", etiket="#ParisEiffel",
        imza="the pale stone rooftops all at the same low height, cut by wide boulevards that "
             "radiate outward from single points like spokes",
        alt_imza="the dark curve of the Seine with its bridges lit end to end",
        fiil="dropping past", birim="second", sifatlar="faster, lower, and colder",
        emoji="\U0001F4A7\U0001F4A6",
    ),
    # 2026-11-15 Ihsan: "eski duzene donelim / milyon izlenen videoya bakalim".
    # Eylul'un dort buyugu (24,5M / 8,9M / 796K / 444K) hep bu bicimdi: gece, kenarda
    # duraganlik, parlayan kaydirak agzi, kuleler arasi dusus, cati havuzu + kahkaha.
    # Kasim KAPI bicimi (gunduz, cam yol, felaket, siyah bitis) bunlarin hicbirini
    # tasimiyordu. Yeni yerler, gece silueti olan kuresel sehirler.
    "dubai-marina-gece": dict(
        sehir="Dubai", landmark="Dubai Marina's tallest tower", neon="blush gold",
        palet="sicak", anahtar="Dubai Marina", isik="sodyum-amber",
        hava="a warm humid night with a light sea breeze off the gulf",
        havuz="rose-lit", etiket="#DubaiMarina",
        imza="the glowing curve of the Dubai Marina canal lined with lit towers on both "
             "sides, white yachts moored along the water, and the fronds of the Palm Jumeirah "
             "spreading into the black sea beyond",
        alt_imza="the lit decks of the yachts in the marina",
        fiil="falling past", birim="second", sifatlar="faster, wetter, and higher",
        emoji="\U0001F303\U0001F4A6",
        basliklar=(
            "Dubai Marina, no railing #shorts",
            "Dubai Marina tower drop #shorts",
            "I slid off Dubai Marina #shorts",
        ),
    ),
    "newyork-timessquare-gece": dict(
        sehir="New York", landmark="One Times Square", neon="laser blue",
        palet="neon", anahtar="Times Square", isik="renkli-yikama",
        hava="a crisp clear night, the air cold and still",
        havuz="blue-lit", etiket="#TimesSquare",
        imza="the blazing canyon of Times Square straight below, every wall covered in giant "
             "glowing billboards, yellow taxis crawling through the crossroads and Broadway "
             "cutting diagonally through the grid",
        alt_imza="the wall of giant glowing billboards",
        fiil="dropping past", birim="second", sifatlar="brighter, faster, and louder",
        emoji="\U0001F695\U0001F4A6",
        basliklar=(
            "Times Square, no railing #shorts",
            "Times Square billboard drop #shorts",
            "I slid down Times Square #shorts",
        ),
    ),
    "chicago-willis-gece": dict(
        sehir="Chicago", landmark="the Willis Tower", neon="neon peach",
        palet="neon", anahtar="Willis Tower", isik="buz-mavi",
        hava="a cold windy night off the lake, the sky clear",
        havuz="teal-lit", etiket="#WillisTower",
        imza="the endless orange street grid of Chicago running dead flat to the horizon, cut "
             "off on one side by the black void of Lake Michigan, the river winding between "
             "the towers",
        alt_imza="the lit bridges crossing the river",
        fiil="dropping past", birim="second", sifatlar="colder, faster, and steeper",
        emoji="\U0001F306\U0001F4A6",
        basliklar=(
            "Willis Tower, no floor #shorts",
            "Willis Tower 442m drop #shorts",
            "I slid off the Willis Tower #shorts",
        ),
    ),
    "seul-lotte-gece": dict(
        sehir="Seoul", landmark="the Lotte World Tower", neon="acid yellow",
        palet="neon", anahtar="Lotte World Tower", isik="mor-tabela",
        hava="a cool clear autumn night",
        havuz="violet-lit", etiket="#LotteWorldTower",
        imza="the wide black band of the Han River curving through the city, crossed by a "
             "chain of lit bridges, and endless rows of glowing apartment towers running to "
             "the dark mountains",
        alt_imza="the lit arches of the bridges over the Han River",
        fiil="falling past", birim="second", sifatlar="faster, colder, and higher",
        emoji="\U0001F1F0\U0001F1F7\U0001F4A6",
        basliklar=(
            "Lotte World Tower, no floor #shorts",
            "Lotte World Tower 555m drop #shorts",
            "Seoul, Lotte World Tower drop #shorts",
        ),
    ),
    "bangkok-mahanakhon-gece": dict(
        sehir="Bangkok", landmark="the MahaNakhon tower", neon="mango orange",
        palet="sicak", anahtar="Bangkok", isik="mum-amber",
        hava="a hot humid night after the rain, the streets still wet",
        havuz="amber-lit", etiket="#Bangkok",
        imza="the wide gold-lit curve of the Chao Phraya river snaking through the city, "
             "glowing temple roofs scattered between the towers, and rivers of headlights "
             "streaming through the streets",
        alt_imza="the glowing golden roofs of a temple",
        fiil="falling past", birim="second", sifatlar="hotter, faster, and wetter",
        emoji="\U0001F6FA\U0001F4A6",
        basliklar=(
            "Bangkok skyscraper drop #shorts",
            "Bangkok, no railing #shorts",
            "I slid off a Bangkok tower #shorts",
        ),
    ),
    "kualalumpur-merdeka-gece": dict(
        sehir="Kuala Lumpur", landmark="Merdeka 118", neon="plasma pink",
        palet="neon", anahtar="Merdeka 118", isik="civa-beyaz",
        hava="a warm tropical night with thin cloud drifting between the towers",
        havuz="pink-lit", etiket="#Merdeka118",
        imza="the twin Petronas Towers glowing silver far below, the city's lit highways "
             "winding around them and the dark jungle hills beyond the last towers",
        alt_imza="the silver spires of the Petronas Towers",
        fiil="falling past", birim="second", sifatlar="faster, hotter, and higher",
        emoji="\U0001F3D9\uFE0F\U0001F4A6",
        basliklar=(
            "Merdeka 118, no floor #shorts",
            "Merdeka 118 678m drop #shorts",
            "Above the Petronas, Merdeka 118 #shorts",
        ),
    ),
    "tokyo-shibuya-gece": dict(
        sehir="Tokyo", landmark="Shibuya Sky", neon="electric jade",
        palet="neon", anahtar="Shibuya", isik="kirmizi-tabela",
        hava="a warm night with fine rain making every street shine",
        havuz="green-lit", etiket="#Shibuya",
        imza="the famous Shibuya scramble crossing directly below, crowds pouring across it "
             "in every direction under walls of giant glowing screens, trains sliding into "
             "the station beside it",
        alt_imza="the giant glowing screens over the crossing",
        fiil="falling past", birim="second", sifatlar="wetter, faster, and louder",
        emoji="\U0001F5FC\U0001F4A6",
        basliklar=(
            "Shibuya Crossing, no floor #shorts",
            "Shibuya Sky slide drop #shorts",
            "I slid over Shibuya Crossing #shorts",
        ),
    ),
}

GOVDE = """# ROUTE

SLUG: {slug}
DESTINATION: {sehir}
LANDMARK: {landmark}
DURATION: 15
NEON: {neon}
PALET: {palet}
TITLE_KEYWORD: {anahtar}
SEHIR_ISIGI: {isik}
LEGWEAR: {giysi}
WEATHER: {hava}
SOURCE: tools/sehir_ekle.py ile uretildi; fearvisionofficiel formatinin AImagine uyarlamasi

## OPENING STATE

The rider stands barefoot at the outer lip of a black glass observation deck on the very top of {landmark} in {sehir}, at night. The weather is {hava}. Her two bare legs and bare feet fill the bottom third of the frame, wet and shining. Beyond the deck edge the frame is filled entirely by {sehir}, seen from vertically above: {imza}. Far ahead on the deck, small in the distance, sits the open mouth of a fully transparent acrylic slide, its two upswept rims outlined by a continuous {neon} electroluminescent strip. There is no railing anywhere between her feet and the drop.

## BEATS

[0.0-2.0] The rider stands still at the edge and the camera on her chest holds the drop dead centre. Her toes flex against the wet black deck. The transparent slide mouth waits ahead of her, its {neon} rims the only saturated colour in the frame. The whole of {sehir} lies directly beneath her feet, {imza}, and nothing separates her from it. She does not move yet. The stillness is the fear.

[2.0-4.0] She edges forward toward the mouth in short unsteady steps. The mouth grows continuously and never jumps in size: first a small outline, then a pair of upswept transparent rims taller than her shins, then a wide open throat. Behind it {sehir} keeps its exact place in the frame, sliding down slightly as she closes on the edge. Her legs shake visibly.

[4.0-6.0] She sits and drops into the throat of the slide. The deck leaves the frame entirely and does not come back. The two {neon} rims snap into hard converging perspective, running away from her hips to a vanishing point far below, and the solid clear floor between them is readable the whole way down. Through it there is nothing but open air and the lights of {sehir} directly under her. The first steep pitch takes her and the horizon is thrown up and out of the top of the frame.

[6.0-8.0] The slide bottoms out and a wall of white water bursts up around her hips and across the lens. Spray floods the frame for a moment, lit {neon} from beneath by the rims, then clears in streaks. Her legs are soaked and both feet stay separately visible through it. The camera pumps its exposure as the frame swings from dark sky to bright water and back. Speed becomes obvious: the two rims are now streaming past the frame edges.

[8.0-10.0] The slide banks hard and the entire city rotates around her legs while her legs stay in the same place in the frame. {imza_cumle} tilts up one side of the frame and the night sky fills the other. Ahead and already visible, the slide runs into one long continuous banked curve carried on thin support struts, growing as she closes on it.

[10.0-11.5] She holds that curve and the city rolls all the way around the frame, once, continuously, never cutting and never jumping. Spray flies outward along the wall of the turn. Coming out of it the horizon settles far lower than before, and {sehir} is no longer beneath her but rising around her: {alt_imza} now sits level with the slide.

[11.5-13.0] The slide drops into a canyon between two dark towers. Lit windows stream past on both sides of the frame, close and fast, throwing warm rectangles across the wet acrylic and across her legs. Straight ahead and below, already visible and growing, a rectangular {havuz} rooftop pool waits between the buildings. The final chute aims directly at it.

[13.0-15.0] She hits the water. The frame goes to churning white for a beat, then punches through into the pool: bright, bubble-filled, muffled under the surface. She rises and breaks through. The lens clears in streaks and the last thing in the frame is her two bare feet floating in {havuz} water with the towers of {sehir} standing around the pool.

## END STATE

The rider is floating on her back in a {havuz} rooftop pool between dark towers in {sehir}. Her two bare feet break the surface in the lower third of the frame, wet and lit by the pool lights. Water still churns from her entry. The bowed fisheye horizon is filled with lit building windows and, far above and behind, {landmark} she started from.

## VOICE

[0.0-3.0] "Oh my god. Look down."
[7.5-9.5] "This is so high, this is so high!"
[10.5-12.0] An unintelligible panicked shout, torn by wind and half swallowed by spray.
[13.0-13.8] A raw terrified scream cut off the instant she hits the water.
[14.2-15.0] She surfaces gasping and the terror has turned into a laugh.

## CAPTION

You're {fiil} {landmark} on a transparent slide above {sehir}. Every {birim} gets {sifatlar}. {emoji}

#MegaSlideFear {etiket} #WaterSlide #POVReels #CGIAdventure

## TITLE

{basliklar}
"""


def rota_yaz(slug: str, spec: dict) -> Path:
    imza_cumle = spec["imza"][0].upper() + spec["imza"][1:]
    # PALET spec'te yoksa "neon" varsayilir: uretilen rotalarin cogu doygun neon
    # ve yanlis etiket A/B olcumunu sessizce bozar. Sicak bir rota yaziyorsan
    # spec'e acikca "palet": "sicak" koy.
    alanlar = {"palet": "neon", "giysi": LEGWEAR, **spec}
    eksik = [k for k in ("anahtar", "isik", "basliklar") if k not in alanlar]
    if eksik:
        # 2026-11-15: eski kayitlarin dosyalari elle guncellendi; eksik alanla
        # yeniden uretmek o duzeltmeleri ezer.
        raise SystemExit("%s: eksik alan %s; eski kayit, dosyayi ezme" % (slug, eksik))
    alanlar["basliklar"] = "\n".join(alanlar["basliklar"])
    metin = GOVDE.format(slug=slug, imza_cumle=imza_cumle, **alanlar)
    yol = KOK / "routes" / (slug + ".md")
    yol.write_text(metin, encoding="utf-8")
    return yol


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("slug", nargs="?")
    p.add_argument("--liste", action="store_true")
    p.add_argument("--hepsi", action="store_true")
    a = p.parse_args()

    uretilebilir = {k: v for k, v in SEHIRLER.items() if v}
    if a.liste:
        for k, v in SEHIRLER.items():
            print("%-30s %s" % (k, "elle yazilmis" if v is None else v["sehir"]))
        return 0
    if a.hepsi:
        for k, v in uretilebilir.items():
            print("yazildi:", rota_yaz(k, v).name)
        return 0
    if not a.slug:
        p.error("slug ver ya da --liste / --hepsi kullan")
    if a.slug not in uretilebilir:
        sys.exit("Bilinmeyen ya da elle yazilmis slug: %r. --liste ile bak." % a.slug)
    print("yazildi:", rota_yaz(a.slug, uretilebilir[a.slug]).name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
