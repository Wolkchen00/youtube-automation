"""KAPI konseptinin rota dosyalarini veriden uretir.

Neden var: sehir_ekle.py ile ayni sebep. Govde iskeleti (bulut kapisi, bacak ve
rim cumleleri, bitisteki kararma) her rotada AYNI olmali; rota yalniz yerini,
havasini ve felaketini getirir. Iskelet 2026-10-01 mevsim kapisi A v2'nin
(reference/ref-DdvYhkUEbxn/ornek/PROMPT_A15.txt) zaman cizelgesidir; o video
Ihsan'in sectigi format.

2026-10-09 Ihsan: video YURUYUSLE acilir. Ilk 2 sn rider cam yolda kaydiragin
agzina yurur (iskelette, rota verisi gerekmez), sonra oturup kayar. Eski bulut
rotalarindaki yuruyus izleyiciyi "nereye yuruyor" merakiyla tutuyordu; dogrudan
kayarak acilan KAPI videolarinda Instagram'da baslangic izlenmesi dustu. Kayis
kalan 13 sn'ye sikisir; rota verisindeki ses zamanlari eski 0-15 cizelgesine
gore yazili, YURUYUS_HARITASI ile yeni cizelgeye tasinir.

Rota alanlari:
  sehir, landmark, neon, palet, anahtar (TITLE_KEYWORD), isik (SEHIR_ISIGI: bu
  konseptte FELAKET dunyasinin baskin renk ailesi, renk ardisikligi kurali icin),
  hava (bulutun ustu), felaket (bulutun alti, kisa ad),
  ilk_kare  : baslangic gorselinde uzakta ne var (landmark, isik, mevsim)
  (yuruyus) : [0.0-2.0] cam yolda kaydiragin agzina yuruyus (iskelet)
  acilis    : [2.0-4.0] oturur, ilk dusus, landmark yakindan
  kapi_ici  : [4.0-6.0] bulutun icinde felaketin ilk isareti
  ortaya    : [6.0-8.5] bulutun altinda AYNI yer felaketin icinde
  tirmanis  : [8.5-10.5] felaket buyur, kaydiraga ilk darbe
  doruk     : [10.5-13.0] asil tehdit yaklasir, kareyi doldurur
  son       : [13.0-15.0] tehdit kamerayi yutar (kararma iskelette)
  son_durum : END STATE
  ses       : VOICE icin kelimesiz uc an (ESKI 0-15 cizelgesinin zamanlariyla;
              rota_metni yeni cizelgeye tasir ve yuruyus nefesini kendisi ekler)
  caption   : "You're ..." ile baslar, sehir adini gecer, soruyla biter
  emoji, etiket (#LandmarkEtiketi), basliklar (2-5, #shorts, anahtar ilk 40 karakterde)

Kullanim:
    python tools/kapi_ekle.py --liste
    python tools/kapi_ekle.py --hepsi          # routes/<slug>.md yazar (varsa ustune)
    python tools/kapi_ekle.py giza-piramit-kum-firtinasi
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
LEGWEAR = "a black high-cut one-piece swimsuit, legs bare from the hip down"
SABIT_ETIKETLER = "#WaterSlide #POVReels #CGIAdventure"

ROTALAR: dict[str, dict] = {
    "giza-piramit-kum-firtinasi": dict(
        sehir="Giza", landmark="the Great Pyramid of Giza", neon="electric cyan",
        palet="sicak", anahtar="Pyramids", isik="sodyum-amber",
        hava="a still golden desert sunrise, the air clear and cool",
        felaket="a towering haboob sandstorm with lightning inside it",
        ilk_kare=(
            "Far below and ahead, filling the upper half of the frame: the three Pyramids of "
            "Giza at sunrise, the Great Pyramid largest and nearest, its stone faces glowing "
            "gold, long blue shadows stretching west across the sand. The low sun sits just "
            "above the desert horizon. The green band of the Nile and the edge of Cairo lie "
            "far beyond. A thick white cloud bank lies across the desert below the slide, and "
            "the slide dives down toward it."
        ),
        acilis=(
            "The Great Pyramid fills the centre of the frame, its gold stone faces sharp in the "
            "low sun, the two smaller pyramids beside it and their long shadows across the "
            "sand. The slide drops past the very tip of the Great Pyramid close enough to see "
            "the individual stone blocks rush up and past on the left."
        ),
        kapi_ici=(
            "The air turns hot and dry, the light inside the cloud turns dirty yellow, and the "
            "first grains of sand start to tick against the lens."
        ),
        ortaya=(
            "the same desert swallowed by a haboob. The three pyramids stand dark against a "
            "wall of rolling brown sand taller than the Great Pyramid itself, filling the "
            "whole horizon and boiling forward. The sky above it is black-brown. Sand streams "
            "sideways across the lens and drums on the acrylic."
        ),
        tirmanis=(
            "Lightning flickers violet-white deep inside the sand wall and lights the pyramids "
            "for an instant, every stone edge flashing white. Gusts throw grit across the frame "
            "in long streaks, the slide shudders and bucks in the wind, and sand hisses over the "
            "clear floor under her feet. The Great Pyramid's apex is already disappearing into "
            "the brown, and the desert floor below goes dark as the shadow of the storm races "
            "across it."
        ),
        doruk=(
            "The sand wall reaches the pyramids and swallows the two smaller ones whole. It "
            "rolls straight toward the slide from the right side of the frame, a boiling cliff "
            "of dark sand with torn palm fronds and flying debris inside it, growing every "
            "second and filling more and more of the frame."
        ),
        son=(
            "The sand wall slams into the camera: grit blasts across the lens, the frame goes "
            "solid dirty brown, then dims to near black as sand piles over the lens."
        ),
        son_durum=(
            "The camera is buried inside the sandstorm. The frame is almost black, with only a "
            "faint brown glow through the sand pressed against the lens. The roar of the wind "
            "is muffled and fading."
        ),
        ses=(
            ("0.0-1.5", "A sharp gasp, then a held breath."),
            ("3.0-5.0", "Ragged panting inside the cloud."),
            ("7.6-8.4", "A short wordless scream at the lightning flash."),
            ("12.5-15.0", "A long wordless scream swallowed by the roar of the sand, cut off "
                          "as the sand buries the camera."),
        ),
        caption=(
            "You're sliding off the Great Pyramid of Giza at sunrise, straight through a cloud "
            "and into a sandstorm taller than the pyramids. Would you ride this?"
        ),
        emoji="\U0001F3DC️\U0001F32A️", etiket="#GizaPyramids",
        basliklar=(
            "Pyramids of Giza sandstorm drop #shorts",
            "Pyramids slide into a haboob #shorts",
            "Pyramids, no floor, sand wall #shorts",
        ),
    ),
    "newyork-ozgurluk-kasirga": dict(
        sehir="New York", landmark="the Statue of Liberty", neon="hot orange",
        palet="neon", anahtar="Liberty", isik="buz-mavi",
        hava="a clear blue autumn morning over the harbour, the water flat and bright",
        felaket="a hurricane driving a storm surge up the harbour",
        ilk_kare=(
            "Far below and ahead, filling the upper half of the frame: the Statue of "
            "Liberty on its small island in New York Harbor on a clear autumn morning, the "
            "pale green copper statue lit gold on one side, torch raised high, standing on "
            "its granite pedestal inside the star-shaped walls of the old fort. The flat "
            "blue harbour water sparkles all around the island. The towers of Lower "
            "Manhattan stand far beyond. A thick white cloud bank lies across the harbour "
            "below the slide, and the slide dives down toward it."
        ),
        acilis=(
            "The Statue of Liberty fills the centre of the frame, her pale green copper "
            "robes catching the low morning sun, the seven spikes of her crown sharp "
            "against the blue sky. The slide drops past the raised torch close enough to "
            "see its gold flame glint and the green copper folds of the raised arm rush up "
            "and past on the left, the granite pedestal and the star-shaped fort walls far "
            "below."
        ),
        kapi_ici=(
            "The air turns cold and wet, the murk inside the cloud darkens to steel grey, "
            "and the first heavy drops of salt rain streak sideways across the lens."
        ),
        ortaya=(
            "the same harbour torn apart by a hurricane. The Statue of Liberty stands dark "
            "green against a black sky, her torch still raised, while the harbour below "
            "heaves with grey water and white foam. Rain blows sideways in sheets across "
            "the lens. Far out past the island a long dark ridge of water is rising, a "
            "storm surge rolling up the harbour toward the statue."
        ),
        tirmanis=(
            "A gust slams the slide sideways and the whole tube shudders and flexes, the "
            "acrylic groaning. Spray tears off the wave tops and blasts across the clear "
            "floor under her feet. Broken tree branches and torn planks tumble through the "
            "air past the slide. The storm surge reaches the island and climbs the "
            "star-shaped fort walls, white water exploding up the granite pedestal toward "
            "the statue's feet."
        ),
        doruk=(
            "The surge buries the pedestal and the green statue stands alone in boiling "
            "white foam, lit icy blue by lightning. A second, taller wave rises in the "
            "harbour and rolls straight toward the slide from the left side of the frame, a "
            "dark grey wall of water with broken piers, planks and uprooted trees inside "
            "it, its blue-white crest growing every second and filling more and more of the "
            "frame."
        ),
        son=(
            "The wave crashes over the camera: foaming water slams across the lens, the "
            "frame floods icy blue-grey, then dims to near black as the water closes over "
            "the lens and drags it under."
        ),
        son_durum=(
            "The camera is under the storm surge. The frame is almost black, with only a "
            "faint blue-grey glow through the churning water pressed against the lens and a "
            "few rising bubbles. The roar of the hurricane is muffled and fading."
        ),
        ses=(
            ("0.0-1.5", "A sharp gasp, then a held breath."),
            ("3.0-5.0", "Fast shaky breathing inside the cold cloud."),
            ("7.6-8.6", "A short wordless scream as the gust slams the slide."),
            ("12.5-15.0", "A long wordless scream drowned by the roar of the wave, cut off "
                          "as the water closes over the camera."),
        ),
        caption=(
            "You're sliding past the torch of the Statue of Liberty in New York, straight "
            "through a cloud and into a hurricane storm surge. Would you ride this one?"
        ),
        emoji="\U0001F5FD\U0001F30A", etiket="#StatueOfLiberty",
        basliklar=(
            "Liberty slide into a hurricane #shorts",
            "Liberty's torch, then the surge #shorts",
            "Statue of Liberty storm drop #shorts",
        ),
    ),
    "roma-kolezyum-dolu": dict(
        sehir="Rome", landmark="the Colosseum", neon="ultraviolet",
        palet="neon", anahtar="Colosseum", isik="led-beyaz",
        hava="a warm summer sunset, the sky soft orange and pink",
        felaket="a giant hailstorm under a green-black sky",
        ilk_kare=(
            "Far below and ahead, filling the upper half of the frame: the Colosseum in "
            "Rome at sunset, its great oval of stacked stone arches glowing warm orange, "
            "the taller broken side of the outer wall casting a long shadow across the open "
            "arena and the maze of stone passages under its missing floor. The low sun sits "
            "just above the hills on the horizon. The ruins of the Forum and the umbrella "
            "pines of the Palatine Hill lie beyond. A thick white cloud bank lies across "
            "the city below the slide, and the slide dives down toward it."
        ),
        acilis=(
            "The Colosseum fills the centre of the frame, its three tiers of arches and the "
            "solid top wall glowing orange in the sunset, every arch a dark window. The "
            "slide drops past the jagged top of the tall outer wall close enough to see the "
            "weathered travertine blocks and the holes in the stone rush up and past on the "
            "right, the empty arena wide open far below."
        ),
        kapi_ici=(
            "The air turns suddenly cold, the murk inside the cloud turns a sickly "
            "green-grey, and the first small pellets of ice crack against the acrylic and "
            "bounce off the lens."
        ),
        ortaya=(
            "the same city under a giant hailstorm. The Colosseum stands pale against a "
            "green-black sky, its arches lit hard white by flashes inside the clouds. "
            "Hailstones the size of fists pour down in dense white streaks, smashing into "
            "the arena and bouncing high off the stone tiers. The umbrella pines beyond are "
            "being shredded and the ground is turning white."
        ),
        tirmanis=(
            "The hail gets bigger. Lumps of ice hammer the slide, crack white stars into "
            "the acrylic beside her shins and bounce off the rims, and one skids across the "
            "clear floor between her feet. A bolt of lightning lights the whole oval of the "
            "Colosseum white for an instant, and chunks of ice and broken stone break off "
            "the top of the outer wall and drop through the arches."
        ),
        doruk=(
            "The hail turns into a solid curtain. A dense white column of falling ice the "
            "size of rocks sweeps across the Colosseum toward the slide from the right side "
            "of the frame, hiding the arches one tier at a time, with shattered roof tiles "
            "and torn pine branches tumbling inside it under the black sky, growing every "
            "second and filling more and more of the frame."
        ),
        son=(
            "The hail curtain hits the camera: ice hammers the lens, cracks spread across "
            "the glass, the frame goes blinding white, then dims to near black as "
            "hailstones pile up over the lens and bury it."
        ),
        son_durum=(
            "The camera lies buried under a heap of hailstones. The frame is almost black, "
            "with only a faint cold white glow through the packed ice pressed against the "
            "cracked lens. The drumming of the hail is muffled and fading."
        ),
        ses=(
            ("0.0-1.5", "A delighted gasp, then a held breath."),
            ("3.0-5.0", "Short sharp breaths as the first ice hits."),
            ("7.6-8.6", "A wordless yelp as a hailstone cracks the acrylic."),
            ("12.5-15.0", "A long wordless scream under the hammering ice, cut off as the "
                          "hail buries the camera."),
        ),
        caption=(
            "You're sliding over the Colosseum in Rome at sunset, then dropping through a "
            "cloud into hail the size of fists. Would you take this slide?"
        ),
        emoji="\U0001F3DB️\U0001F9CA", etiket="#Colosseum",
        basliklar=(
            "Colosseum hail the size of fists #shorts",
            "Colosseum sunset, then the hail #shorts",
            "Colosseum drop into an ice storm #shorts",
        ),
    ),
    "losangeles-hollywood-yangin": dict(
        sehir="Los Angeles", landmark="the Hollywood sign", neon="glacier blue",
        palet="sicak", anahtar="Hollywood", isik="kirmizi-tabela",
        hava="a hazy golden afternoon over the dry hills",
        felaket="a wildfire firestorm racing over the hills",
        ilk_kare=(
            "Far below and ahead, filling the upper half of the frame: the Hollywood sign "
            "seen from the FRONT, from the city side, its nine giant white letters facing "
            "the camera and reading HOLLYWOOD correctly from left to right, never mirrored. "
            "The sign stands on the dry brown slope of Mount Lee in the hazy golden "
            "afternoon sun, the scrub-covered ridges rising behind it and folding away on "
            "both sides. The white domes of the Griffith Observatory sit on a ridge to one "
            "side. A thick white cloud bank lies across the foothills below the slide, and "
            "the slide dives down toward it."
        ),
        acilis=(
            "The Hollywood sign fills the centre of the frame, the nine white letters "
            "standing tall on their steel frames on the steep golden hillside, dry grass "
            "and brush between them. The slide drops past the top of the big H close enough "
            "to see the white sheet metal faces of the letters rush up and past on the left, "
            "the word still reading correctly, the dusty ridge trail running below."
        ),
        kapi_ici=(
            "The air turns hot and smoky, the murk inside the cloud glows dull orange, and "
            "the first flakes of grey ash and tiny red sparks drift across the lens."
        ),
        ortaya=(
            "the same hills on fire. A firestorm is racing up the slopes toward the "
            "Hollywood sign, a ragged front of bright orange flame leaping through the dry "
            "brush under a dark red sky choked with black smoke. The white letters stand "
            "out stark against the glow. Embers rain down past the slide like burning snow "
            "and bounce on the clear acrylic."
        ),
        tirmanis=(
            "The flames reach the foot of the sign and race up the hillside between the "
            "letters, the dry scrub exploding into fire one bush after another. A gust "
            "throws a storm of red embers across the frame in long glowing streaks, the "
            "slide shudders in the rising heat, and burning leaves skid over the clear "
            "floor under her feet. Behind the sign a pillar of black smoke towers into the "
            "red sky."
        ),
        doruk=(
            "The fire jumps the ridge and swallows the first letters, the white H and O "
            "scorched black against the flames. A rolling wall of fire and black smoke "
            "surges straight toward the slide from the right side of the frame, a towering "
            "front of orange flame with burning branches and dark charred debris tumbling "
            "inside it, growing every second and filling more and more of the frame."
        ),
        son=(
            "The fire wall rolls over the camera: flame washes across the lens, the frame "
            "floods blinding orange-red, then dims to near black as thick black smoke and "
            "soot cover the lens."
        ),
        son_durum=(
            "The camera is inside the smoke behind the fire front. The frame is almost "
            "black, with only a faint dull red glow through the soot smeared across the "
            "lens. The roar of the fire is muffled and fading."
        ),
        ses=(
            ("0.0-1.5", "A happy gasp, then a held breath."),
            ("3.0-5.0", "Coughing breaths in the hot smoky cloud."),
            ("8.0-9.0", "A short wordless scream as the embers hit."),
            ("12.5-15.0", "A long wordless scream swallowed by the roar of the fire, cut "
                          "off as the smoke covers the camera."),
        ),
        caption=(
            "You're sliding past the Hollywood sign in Los Angeles, then through a cloud "
            "and straight into a wildfire. Would you hold on?"
        ),
        emoji="\U0001F3AC\U0001F525", etiket="#HollywoodSign",
        basliklar=(
            "Hollywood sign slide into fire #shorts",
            "Hollywood hills, then the fire #shorts",
            "Hollywood ember rain drop #shorts",
        ),
    ),
    "sydney-opera-tsunami": dict(
        sehir="Sydney", landmark="the Sydney Opera House", neon="sunset coral",
        palet="neon", anahtar="Opera House", isik="mavi-beyaz",
        hava="a crisp spring morning over the harbour, the sky clean blue",
        felaket="a tsunami rising in the harbour",
        ilk_kare=(
            "Far below and ahead, filling the upper half of the frame: the Sydney Opera "
            "House on its point at the edge of the harbour on a crisp spring morning, its "
            "white sail-shaped shells shining in the sun, the grey steel arch of the "
            "Harbour Bridge beyond it. The harbour water is calm and deep blue, and green "
            "parkland and the towers of the city lie beyond. A thick white cloud bank lies "
            "across the harbour below the slide, and the slide dives down toward it."
        ),
        acilis=(
            "The Sydney Opera House fills the centre of the frame, its white shells "
            "overlapping like raised sails, the cream tiles glittering in the morning sun, "
            "the wide granite steps and the forecourt below them. The slide drops past the "
            "tip of the tallest shell close enough to see the individual glossy tiles rush "
            "up and past on the right, the calm harbour water sparkling far below."
        ),
        kapi_ici=(
            "The air turns cold and salty, the murk inside the cloud darkens to blue-grey, "
            "and a fine spray of sea water beads across the lens."
        ),
        ortaya=(
            "the same harbour as the sea pulls away. The water is draining out from around "
            "the Opera House, exposing dark rocks and mud below the forecourt, and the "
            "white shells stand pale against a dark slate sky. Far out at the harbour "
            "mouth, between the headlands, a dark line of water is rising across the whole "
            "width of the harbour."
        ),
        tirmanis=(
            "The line becomes a tsunami, a dark blue wall of water climbing higher every "
            "second as it rushes in past the headlands, its crest torn white by the wind. "
            "It swallows the shoreline parks and lifts broken jetties and floating trees on "
            "its face. Spray blasts across the slide, the acrylic shudders, and the clear "
            "floor under her feet streams with sea water."
        ),
        doruk=(
            "The tsunami slams into the Opera House and white water explodes up over the "
            "shells, burying the lower sails. The wave keeps coming straight toward the "
            "slide from the left side of the frame, a towering dark blue wall with broken "
            "timber, uprooted trees and shattered jetty planks churning inside it, its "
            "blue-white crest growing every second and filling more and more of the frame."
        ),
        son=(
            "The wave breaks over the camera: a mass of white water smashes across the "
            "lens, the frame floods blue-white, then dims to near black as the sea closes "
            "over the lens and pulls it deep under."
        ),
        son_durum=(
            "The camera is deep under the tsunami. The frame is almost black, with only a "
            "faint blue glow far above through the churning water and a stream of bubbles "
            "crossing the lens. The roar of the wave is muffled and fading."
        ),
        ses=(
            ("0.0-1.5", "A bright gasp, then a held breath."),
            ("3.0-5.0", "Quick nervous breaths in the cold cloud."),
            ("7.5-9.5", "Fast panting as the wave rises."),
            ("12.5-15.0", "A long wordless scream swallowed by the crash of the wave, cut "
                          "off as the water closes over the camera."),
        ),
        caption=(
            "You're sliding over the Sydney Opera House on a perfect spring morning, then "
            "through a cloud toward a tsunami. Would you go down?"
        ),
        emoji="\U0001F3AD\U0001F30A", etiket="#SydneyOperaHouse",
        basliklar=(
            "Opera House slide into a tsunami #shorts",
            "Opera House, then the sea rises #shorts",
            "Sydney Opera House tsunami drop #shorts",
        ),
    ),
    "rushmore-hortum": dict(
        sehir="South Dakota", landmark="Mount Rushmore", neon="electric magenta",
        palet="neon", anahtar="Rushmore", isik="yesil-civa",
        hava="a warm summer evening over the prairie and the pine hills",
        felaket="a supercell tornado under a green sky",
        ilk_kare=(
            "Far below and ahead, filling the upper half of the frame: Mount Rushmore on a "
            "warm summer evening, the four colossal carved heads in the pale granite cliff "
            "glowing gold in the low sun, a grey slope of broken rock spilling below them. "
            "Dark green pine forest covers the Black Hills all around, and the open prairie "
            "stretches flat and golden beyond to the horizon. A thick white cloud bank lies "
            "across the hills below the slide, and the slide dives down toward it."
        ),
        acilis=(
            "Mount Rushmore fills the centre of the frame, the four colossal carved heads "
            "of pale granite lit warm gold by the evening sun, deep shadows in their eyes "
            "and under their brows. The slide drops past the top of the cliff close enough "
            "to see the cracks and the rough chisel marks in the stone rush up and past on "
            "the left, the pine forest and the slope of broken rock far below."
        ),
        kapi_ici=(
            "The air turns heavy and humid, the murk inside the cloud takes on a strange "
            "green tint, and big warm raindrops begin to splatter across the lens."
        ),
        ortaya=(
            "the same hills under a supercell. The four carved heads of Mount Rushmore "
            "stand pale against a green-black sky, a huge dark storm base hanging low over "
            "the Black Hills and slowly rotating. Lightning flickers inside it. Out on the "
            "prairie beyond, a dark funnel drops out of the cloud and touches the ground, "
            "throwing up a skirt of brown dust."
        ),
        tirmanis=(
            "The funnel thickens into a wide tornado and turns toward the mountain, tearing "
            "across the prairie and into the pine forest, whole trees lifting into the air "
            "and flying apart. The wind howls, rain and hail blast sideways across the "
            "frame, and the slide shudders and sways as the gusts hit it. Pine needles and "
            "shredded bark streak across the clear floor under her feet."
        ),
        doruk=(
            "The tornado reaches the foot of the cliff and climbs the rock slope, a "
            "churning black column of wind wrapping around the carved heads and blasting "
            "dust off the granite. It veers straight toward the slide from the right side "
            "of the frame, a rotating dark wall with uprooted pines, broken branches and "
            "rocks flying inside it, growing every second and filling more and more of the "
            "frame."
        ),
        son=(
            "The tornado swallows the camera: debris and rain blast across the lens, the "
            "frame floods dark green-grey, then dims to near black as mud and shredded "
            "leaves plaster over the lens."
        ),
        son_durum=(
            "The camera is caught inside the tornado. The frame is almost black, with only "
            "a faint green-grey flicker through the mud and torn leaves stuck to the lens. "
            "The freight-train roar of the wind is muffled and fading."
        ),
        ses=(
            ("0.0-1.5", "A soft gasp, then a held breath."),
            ("3.0-5.0", "Uneasy shallow breathing inside the green cloud."),
            ("7.8-8.8", "A short wordless scream as the funnel turns toward her."),
            ("12.5-15.0", "A long wordless scream lost in the freight-train roar, cut off "
                          "as the tornado swallows the camera."),
        ),
        caption=(
            "You're sliding over Mount Rushmore in South Dakota on a summer evening, then "
            "down through a cloud into a tornado. Would you dare?"
        ),
        emoji="\U0001F3D4️\U0001F32A️", etiket="#MountRushmore",
        basliklar=(
            "Rushmore slide into a tornado #shorts",
            "Mount Rushmore under a green sky #shorts",
            "Rushmore, then the funnel drops #shorts",
        ),
    ),
    "napoli-vezuv-yanardag": dict(
        sehir="Naples", landmark="Mount Vesuvius", neon="frost blue",
        palet="neon", anahtar="Vesuvius", isik="kirmizi-tabela",
        hava="a calm spring morning over the bay and the lemon groves",
        felaket="a volcanic eruption with a pyroclastic flow",
        ilk_kare=(
            "Far below and ahead, filling the upper half of the frame: Mount Vesuvius "
            "rising above the Bay of Naples on a calm spring morning, its broad grey-green "
            "slopes and the wide broken rim of its summit crater sharp against a clear blue "
            "sky. Terraced lemon groves and vineyards cover the lower slopes, and the blue "
            "bay curves away beyond with the city of Naples along its shore. A thick white "
            "cloud bank lies across the slopes below the slide, and the slide dives down "
            "toward it."
        ),
        acilis=(
            "Mount Vesuvius fills the centre of the frame, its summit crater a wide grey "
            "bowl with steep rock walls and a thin wisp of steam rising from one side. The "
            "slide drops past the jagged crater rim close enough to see the loose dark "
            "gravel and the reddish rock layers rush up and past on the right, the green "
            "lemon terraces and the bright blue bay far below."
        ),
        kapi_ici=(
            "The air turns hot and smells of sulphur, the murk inside the cloud darkens to "
            "dirty grey, and the first fine grains of ash start to settle on the lens."
        ),
        ortaya=(
            "the same mountain erupting. A towering black column of ash blasts out of the "
            "crater of Vesuvius into a dark brown sky, lit from below by fountains of "
            "orange lava. Lightning crackles inside the ash cloud. Glowing lava bombs arc "
            "out of the summit and smash into the lemon groves on the slopes, setting the "
            "trees on fire."
        ),
        tirmanis=(
            "The column grows taller and starts to sag. Ash rains down thickly, grey flakes "
            "streaking across the frame, and red-hot stones thud onto the slide, bouncing "
            "off the rims and leaving glowing scorch marks on the acrylic. A lava bomb "
            "smashes into the hillside right beside the slide and bursts in a shower of "
            "sparks. On the far slope a river of orange lava pours down through the "
            "vineyards."
        ),
        doruk=(
            "Part of the ash column falls back onto the mountain and becomes a pyroclastic "
            "flow, a boiling avalanche of grey-black ash and hot gas pouring down the slope "
            "of Vesuvius toward the slide from the left side of the frame, glowing red at "
            "its base, with burning trees and black rocks tumbling inside it, growing every "
            "second and filling more and more of the frame."
        ),
        son=(
            "The pyroclastic flow rolls over the camera: hot ash blasts across the lens, "
            "the frame floods glowing red-orange, then dims to near black as thick grey ash "
            "settles over the lens and buries it."
        ),
        son_durum=(
            "The camera lies buried under the ash. The frame is almost black, with only a "
            "faint dull red glow through the hot ash pressed against the lens. The rumble "
            "of the eruption is muffled and fading."
        ),
        ses=(
            ("0.0-1.5", "A sharp gasp, then a held breath."),
            ("3.0-5.0", "Coughing, ragged breaths in the hot grey cloud."),
            ("8.0-9.0", "A short wordless scream as the lava bomb bursts."),
            ("12.5-15.0", "A long wordless scream swallowed by the roar of the flow, cut "
                          "off as the ash buries the camera."),
        ),
        caption=(
            "You're sliding over Mount Vesuvius above Naples on a spring morning, then "
            "dropping through a cloud into a full eruption. Would you still ride it?"
        ),
        emoji="\U0001F30B\U0001F525", etiket="#Vesuvius",
        basliklar=(
            "Vesuvius slide into an eruption #shorts",
            "Vesuvius drop into lava bombs #shorts",
            "Vesuvius erupts under the slide #shorts",
        ),
    ),
    "grandcanyon-yildirim": dict(
        sehir="Arizona", landmark="the Grand Canyon", neon="laser lime",
        palet="sicak", anahtar="Grand Canyon", isik="mor-tabela",
        hava="a golden sunrise over the canyon rims, the air clear and still",
        felaket="a violet dry-lightning supercell and a flash flood",
        ilk_kare=(
            "Far below and ahead, filling the upper half of the frame: the Grand Canyon at "
            "sunrise, layer after layer of red, orange and cream rock cliffs stepping down "
            "into the deep gorge, the stone buttes and towers inside it glowing in the "
            "first light. The low sun sits just above the far North Rim. The thin green "
            "thread of the Colorado River runs along the canyon floor far below. A thick "
            "white cloud bank lies across the canyon below the slide, and the slide dives "
            "down toward it."
        ),
        acilis=(
            "The Grand Canyon fills the centre of the frame, its banded red and orange "
            "walls lit gold by the sunrise, deep purple shadows filling the side gorges. "
            "The slide drops over the edge of the South Rim close enough to see the pale "
            "limestone ledge and the twisted juniper trees on it rush up and past on the "
            "left, then plunges into the open air above the canyon, the river a thin line "
            "far below."
        ),
        kapi_ici=(
            "The air turns dry and electric, the murk inside the cloud flickers violet from "
            "somewhere below, and a low rumble of thunder shakes the acrylic."
        ),
        ortaya=(
            "the same canyon under a violet supercell. A huge black storm base hangs low "
            "over the Grand Canyon, the red rock walls gone dark and cold beneath it. Bolts "
            "of violet-white lightning crack down out of the cloud and strike the buttes "
            "and the rims one after another, each flash lighting the whole canyon for an "
            "instant. Dry wind whips red dust off the ledges."
        ),
        tirmanis=(
            "A bolt strikes the rim right beside the slide and blasts rock and sparks into "
            "the air, the flash burning the frame white for an instant, and the juniper "
            "trees on the rim burst into flame. Thunder shakes the slide as it dives deeper "
            "between the red walls, and grit and pebbles rattle across the clear floor "
            "under her feet. Far below, brown flood water is pouring into the canyon from "
            "the side gorges."
        ),
        doruk=(
            "The flash flood comes roaring down the main gorge toward the slide from the "
            "right side of the frame, a churning wall of dark brown water and mud with "
            "uprooted trees and tumbling boulders inside it, lit violet by the lightning "
            "above, filling the canyon from wall to wall and rising up the red cliffs, "
            "growing every second and filling more and more of the frame."
        ),
        son=(
            "The flood wall smashes into the camera: brown water and mud surge across the "
            "lens, the frame floods dark muddy brown under one last violet flash, then dims "
            "to near black as the water closes over the lens."
        ),
        son_durum=(
            "The camera is under the flash flood. The frame is almost black, with only a "
            "faint brown glow through the silty water pressed against the lens and a dim "
            "violet flicker far above. The roar of the flood and the thunder is muffled and "
            "fading."
        ),
        ses=(
            ("0.0-1.5", "A thrilled gasp, then a held breath."),
            ("3.0-5.0", "Tight, shallow breathing in the dark cloud."),
            ("7.5-8.5", "A short wordless scream at the lightning strike."),
            ("12.5-15.0", "A long wordless scream drowned by the roar of the flood, cut "
                          "off as the water closes over the camera."),
        ),
        caption=(
            "You're sliding over the Grand Canyon in Arizona at sunrise, then through a "
            "cloud into a lightning storm and a flash flood. Would you try this?"
        ),
        emoji="\U0001F3DE️⚡", etiket="#GrandCanyon",
        basliklar=(
            "Grand Canyon drop into lightning #shorts",
            "Grand Canyon flash flood ride #shorts",
            "Grand Canyon, violet storm drop #shorts",
        ),
    ),
    "moskova-vasil-buz-firtinasi": dict(
        sehir="Moscow", landmark="St. Basil's Cathedral", neon="neon tangerine",
        palet="neon", anahtar="St. Basil", isik="civa-beyaz",
        hava="a golden autumn evening on Red Square, the air crisp and still",
        felaket="an Arctic blizzard and ice storm with thundersnow",
        ilk_kare=(
            "Far below and ahead, filling the upper half of the frame: St. Basil's "
            "Cathedral at the end of Red Square on a golden autumn evening, its onion domes "
            "striped and patterned in red, green, blue and gold, glowing in the low sun. "
            "The red brick Kremlin wall and its pointed towers run along one side of the "
            "empty cobbled square. Golden birch trees and the river lie beyond. A thick "
            "white cloud bank lies across the square below the slide, and the slide dives "
            "down toward it."
        ),
        acilis=(
            "St. Basil's Cathedral fills the centre of the frame, its bright onion domes "
            "clustered around the tall central tent spire, each dome painted in bold stripes "
            "and zigzags of red, green, yellow and blue. The slide drops past the gold "
            "cross on top of the spire close enough to see the glazed tiles and the gilded "
            "trim rush up and past on the right, the empty cobbles of Red Square glowing "
            "far below."
        ),
        kapi_ici=(
            "The air turns bitterly cold, the murk inside the cloud turns a hard bluish "
            "white, and the first needles of sleet freeze into a white crust along the "
            "edges of the lens."
        ),
        ortaya=(
            "the same square in an Arctic blizzard. Snow drives sideways across Red Square "
            "in dense white streaks under a dark slate sky, and the bright domes of St. "
            "Basil's are already crusted with ice, their colours glowing through a glassy "
            "glaze. The Kremlin wall disappears and reappears behind the snow. Freezing "
            "rain hisses across the acrylic and turns to ice where it lands."
        ),
        tirmanis=(
            "Thundersnow: a bolt of white lightning flashes inside the blizzard and lights "
            "the whole square and every iced dome blinding white for an instant, followed "
            "by a deep boom. The slide stiffens and creaks as ice builds along the rims, "
            "and the water under her hips turns to slush. Icicles snap off the Kremlin "
            "towers and fly away in the wind, and hard ice pellets rattle over the clear "
            "floor under her feet."
        ),
        doruk=(
            "The blizzard thickens into a solid white-out. A towering front of wind-driven "
            "snow and ice rolls across Red Square toward the slide from the left side of "
            "the frame, swallowing the domes one by one, with broken icicles, snapped "
            "branches and chunks of ice inside it, its hard white glare growing every "
            "second and filling more and more of the frame."
        ),
        son=(
            "The ice storm hits the camera: snow and freezing rain blast across the lens, "
            "the frame floods hard white, then dims to near black as a thick layer of ice "
            "glazes over the lens and snow drifts over it."
        ),
        son_durum=(
            "The camera is frozen inside the blizzard. The frame is almost black, with only "
            "a faint cold white glow through the thick ice glazed over the lens. The howl "
            "of the wind is muffled and fading."
        ),
        ses=(
            ("0.0-1.5", "A sharp gasp of cold air, then a held breath."),
            ("3.0-5.0", "Shivering, chattering breaths in the frozen cloud."),
            ("7.6-8.6", "A short wordless scream at the thundersnow flash."),
            ("12.5-15.0", "A long wordless scream lost in the howl of the blizzard, cut "
                          "off as the ice seals over the camera."),
        ),
        caption=(
            "You're sliding over St. Basil's Cathedral in Moscow on an autumn evening, then "
            "down through a cloud into an Arctic blizzard. Would you stay on?"
        ),
        emoji="❄️\U0001F328️", etiket="#StBasilsCathedral",
        basliklar=(
            "St. Basil's domes in a blizzard #shorts",
            "St. Basil's, then thundersnow #shorts",
            "St. Basil drop into an ice storm #shorts",
        ),
    ),
    "machupicchu-heyelan": dict(
        sehir="Peru", landmark="Machu Picchu", neon="hot pink",
        palet="neon", anahtar="Machu Picchu", isik="yesil-civa",
        hava="a misty green dawn over the ruins and the peaks",
        felaket="torrential rain and a landslide of mud and rock",
        ilk_kare=(
            "Far below and ahead, filling the upper half of the frame: Machu Picchu at "
            "dawn, its grey stone terraces and roofless granite houses spread across the "
            "green saddle of the ridge, the steep green peak of Huayna Picchu rising "
            "sharply behind it. Thin bands of mist drift through the deep green valleys "
            "around it, and the first pink light touches the peaks. The Urubamba river runs "
            "far below in the gorge. A thick white cloud bank lies across the valley below "
            "the slide, and the slide dives down toward it."
        ),
        acilis=(
            "Machu Picchu fills the centre of the frame, its stepped stone terraces and the "
            "grey walls of the old houses sharp in the soft dawn light, bright green lawns "
            "between them, Huayna Picchu standing tall and dark green behind. The slide "
            "drops past the top of a terrace wall close enough to see the tightly fitted "
            "granite blocks rush up and past on the right, the sheer green drop to the "
            "river far below."
        ),
        kapi_ici=(
            "The air turns wet and heavy, the murk inside the cloud darkens to grey-green, "
            "and warm rain begins to stream down the lens."
        ),
        ortaya=(
            "the same mountain drowning in torrential rain. The grey terraces of Machu "
            "Picchu stand out under a black-green sky, water pouring off every terrace edge "
            "in brown waterfalls. Huayna Picchu is half hidden in rain. On the steep slope "
            "above the ruins the green jungle is starting to crack and slip, raw brown mud "
            "showing through the torn plants."
        ),
        tirmanis=(
            "Rain hammers the acrylic so hard the clear floor under her feet runs with "
            "brown water. A whole section of slope tears loose above the ruins and pours "
            "down in a river of mud, snapping trees and burying the upper terraces. "
            "Boulders bounce down the green slope past the slide, and a lightning flash "
            "lights the wet granite walls of Machu Picchu white for an instant."
        ),
        doruk=(
            "The main landslide breaks away from the mountainside and pours down toward the "
            "slide from the right side of the frame, a churning wall of dark brown mud and "
            "grey rock with uprooted trees, stone blocks and broken branches tumbling "
            "inside it, sweeping over the terraces, growing every second and filling more "
            "and more of the frame."
        ),
        son=(
            "The landslide hits the camera: mud and gravel smash across the lens, the frame "
            "floods dark brown, then dims to near black as thick wet mud covers the lens "
            "and buries it."
        ),
        son_durum=(
            "The camera is buried in the landslide. The frame is almost black, with only a "
            "faint green-brown glow through the wet mud pressed against the lens. The "
            "grinding roar of the rock is muffled and fading."
        ),
        ses=(
            ("0.0-1.5", "A soft amazed gasp, then a held breath."),
            ("3.0-5.0", "Wet, shaky breaths inside the rain cloud."),
            ("8.0-9.0", "A short wordless scream as the slope tears loose."),
            ("12.5-15.0", "A long wordless scream swallowed by the roar of the mud, cut "
                          "off as the landslide buries the camera."),
        ),
        caption=(
            "You're sliding over Machu Picchu in Peru at dawn, then through a cloud into a "
            "storm that brings the mountain down. Would you go first?"
        ),
        emoji="⛰️\U0001F327️", etiket="#MachuPicchu",
        basliklar=(
            "Machu Picchu landslide drop #shorts",
            "Machu Picchu at dawn, then mud #shorts",
            "Machu Picchu in a river of mud #shorts",
        ),
    ),
    "cinseddi-deprem": dict(
        sehir="China", landmark="the Great Wall of China", neon="electric teal",
        palet="sicak", anahtar="Great Wall", isik="mum-amber",
        hava="a golden autumn afternoon over the ridges",
        felaket="an earthquake tearing the mountain ridge apart",
        ilk_kare=(
            "Far below and ahead, filling the upper half of the frame: the Great Wall of "
            "China running along the crest of steep mountain ridges on a golden autumn "
            "afternoon, its grey stone walkway and square watchtowers rising and falling "
            "with every peak. The hillsides are covered in red, orange and yellow autumn "
            "trees. Ridge after ridge fades into a soft blue haze beyond. A thick white "
            "cloud bank lies across the valley below the slide, and the slide dives down "
            "toward it."
        ),
        acilis=(
            "The Great Wall fills the centre of the frame, snaking up and over the ridges "
            "in both directions, its notched parapets and square stone watchtowers glowing "
            "warm in the afternoon sun. The slide drops past the top of a watchtower close "
            "enough to see the grey bricks and the arched windows rush up and past on the "
            "left, the steep stone steps of the walkway and the blazing autumn trees below."
        ),
        kapi_ici=(
            "A deep low rumble rises from somewhere beneath the cloud, the slide trembles, "
            "and the murk inside the cloud turns a dusty amber."
        ),
        ortaya=(
            "the same ridges shaking apart. The Great Wall runs along the crest under a "
            "dark brown sky thick with dust, the whole mountain shuddering. A long crack is "
            "tearing open along the ridge beside it, and a watchtower ahead leans and "
            "crumbles, its bricks sliding down the hillside in a cloud of tan dust. The "
            "autumn trees shake and sway."
        ),
        tirmanis=(
            "The ground lurches. A whole section of the wall breaks away and slides down "
            "the slope in a cascade of grey bricks and stones, and the crack in the ridge "
            "opens into a deep dark gap, low amber sunlight blazing through the dust above "
            "it. Rocks bounce down the hillside and clatter across the slide, the acrylic "
            "shudders, and the clear floor under her feet fills with grit and gravel."
        ),
        doruk=(
            "The mountainside collapses. A massive rockfall pours down toward the slide "
            "from the right side of the frame, a roaring avalanche of grey boulders, broken "
            "wall stones and splintered trees inside a towering cloud of amber dust, the "
            "watchtowers of the Great Wall toppling into it one after another, growing "
            "every second and filling more and more of the frame."
        ),
        son=(
            "The rockfall hits the camera: stones and dust blast across the lens, the frame "
            "floods choking amber, then dims to near black as gravel and dust pile over the "
            "lens and bury it."
        ),
        son_durum=(
            "The camera is buried under the rubble. The frame is almost black, with only a "
            "faint amber glow through the dust and gravel pressed against the lens. The "
            "rumble of the earthquake is muffled and fading."
        ),
        ses=(
            ("0.0-1.5", "A happy gasp, then a held breath."),
            ("3.0-5.0", "Nervous breathing as the rumble grows."),
            ("7.5-8.5", "A short wordless scream as the wall breaks away."),
            ("12.5-15.0", "A long wordless scream swallowed by the roar of the rockfall, "
                          "cut off as the rubble buries the camera."),
        ),
        caption=(
            "You're sliding along the Great Wall of China on an autumn afternoon, then "
            "through a cloud into an earthquake. Would you ride this?"
        ),
        emoji="\U0001F9F1\U0001F4A5", etiket="#GreatWallOfChina",
        basliklar=(
            "Great Wall earthquake drop #shorts",
            "The Great Wall starts to fall #shorts",
            "Great Wall slide, rockfall below #shorts",
        ),
    ),
    "barselona-sagrada-hortum": dict(
        sehir="Barcelona", landmark="the Sagrada Familia", neon="solar yellow",
        palet="neon", anahtar="Sagrada Familia", isik="mor-tabela",
        hava="a warm Mediterranean evening, the sea calm and gold",
        felaket="a lightning storm with a waterspout coming in off the sea",
        ilk_kare=(
            "Far below and ahead, filling the upper half of the frame: the Sagrada Familia "
            "rising above the city grid of Barcelona on a warm Mediterranean evening, its "
            "tall pierced stone spires topped with bright mosaic tips, glowing honey gold "
            "in the low sun. The flat rooftops of the city stretch down to the calm golden "
            "sea beyond, and the green hills rise behind. A thick white cloud bank lies "
            "across the city below the slide, and the slide dives down toward it."
        ),
        acilis=(
            "The Sagrada Familia fills the centre of the frame, its cluster of tall pierced "
            "spires rising like stone honeycombs, the carved facade below covered in "
            "stone leaves and fruit. The slide drops past the top of a spire close enough "
            "to see the bright mosaic fruit on its tip and the pierced stonework rush up "
            "and past on the right, the straight city streets far below."
        ),
        kapi_ici=(
            "The air turns warm and heavy with salt, the murk inside the cloud flickers "
            "violet, and thunder rolls somewhere below as rain begins to spatter the lens."
        ),
        ortaya=(
            "the same city under a violet lightning storm. The spires of the Sagrada "
            "Familia stand dark against a purple-black sky, lit violet with every flash. "
            "Out at sea a dark funnel hangs from the storm cloud down to the water, a "
            "waterspout throwing up a ring of white spray, and it is moving toward the "
            "shore."
        ),
        tirmanis=(
            "The waterspout reaches the beach and keeps coming over the rooftops, a grey "
            "column of rotating water and wind tearing up palm trees and roof tiles. "
            "Lightning strikes the tallest spire of the Sagrada Familia and lights the "
            "stone violet-white. Rain and spray blast across the frame, and the slide "
            "shudders and sways in the gusts as water streams over the clear floor under "
            "her feet."
        ),
        doruk=(
            "The waterspout turns straight toward the basilica and the slide, crossing the "
            "city from the left side of the frame, a towering dark column of churning water "
            "and wind with palm fronds, roof tiles and broken shutters spinning inside it, "
            "lit violet by the lightning, growing every second and filling more and more of "
            "the frame."
        ),
        son=(
            "The waterspout swallows the camera: sea water and debris blast across the "
            "lens, the frame floods violet-grey, then dims to near black as the dark water "
            "wraps around the lens and covers it."
        ),
        son_durum=(
            "The camera is inside the waterspout. The frame is almost black, with only a "
            "faint violet flicker of lightning through the water streaming over the lens. "
            "The roar of the wind and the sea is muffled and fading."
        ),
        ses=(
            ("0.0-1.5", "A delighted gasp, then a held breath."),
            ("3.0-5.0", "Quick uneasy breaths in the flickering cloud."),
            ("8.0-9.0", "A short wordless scream as lightning hits the spire."),
            ("12.5-15.0", "A long wordless scream lost in the roar of the waterspout, cut "
                          "off as the water covers the camera."),
        ),
        caption=(
            "You're sliding past the spires of the Sagrada Familia in Barcelona, then "
            "through a cloud into a waterspout and a lightning storm. Would you scream too?"
        ),
        emoji="⛪⛈️", etiket="#SagradaFamilia",
        basliklar=(
            "Sagrada Familia waterspout drop #shorts",
            "Sagrada Familia, then lightning #shorts",
            "Sagrada Familia in a sea storm #shorts",
        ),
    ),
    "stonehenge-meteor": dict(
        sehir="Wiltshire", landmark="Stonehenge", neon="starlight white",
        palet="neon", anahtar="Stonehenge", isik="renkli-yikama",
        hava="a calm midsummer twilight over the plain, the sky deep blue and gold",
        felaket="a meteor storm with fireballs striking the plain",
        ilk_kare=(
            "Far below and ahead, filling the upper half of the frame: Stonehenge standing "
            "alone on the open green plain of Wiltshire at midsummer twilight, its ring of "
            "tall grey standing stones and the heavy lintels laid across their tops dark "
            "against a glowing sky. The sun has just set, leaving a gold band on the "
            "horizon under a deep blue sky with the first stars. Soft rolling grassland and "
            "low burial mounds stretch away beyond. A thick white cloud bank lies across "
            "the plain below the slide, and the slide dives down toward it."
        ),
        acilis=(
            "Stonehenge fills the centre of the frame, the great circle of grey sarsen "
            "stones with their lintels and the huge stone arches in the middle, soft "
            "shadows on the grass inside. The slide drops past the top of a tall standing "
            "stone close enough to see the pale lichen and the rough worn surface of the "
            "rock rush up and past on the left, the silver grass of the plain far below."
        ),
        kapi_ici=(
            "The cloud turns strangely warm, the murk inside it flashes green and magenta "
            "from somewhere above, and a deep crackling hiss grows in the air."
        ),
        ortaya=(
            "the same plain under a meteor storm. Stonehenge stands black against a dark "
            "sky streaked with fireballs, dozens of glowing meteors falling at once, each "
            "trailing smoke and burning green, magenta and white. One strikes the plain far "
            "beyond the stones and throws up a dome of fire and dirt."
        ),
        tirmanis=(
            "The meteors fall closer and bigger. A fireball streaks past the slide close "
            "enough to light the acrylic blinding green, and burning fragments rattle over "
            "the clear floor under her feet. Another one strikes the grass right beside "
            "Stonehenge, the blast lighting every standing stone magenta, and a shockwave "
            "of dust and burning turf rolls across the plain. Craters smoke everywhere."
        ),
        doruk=(
            "The biggest meteor yet comes down out of the black sky toward the slide from "
            "the right side of the frame, a huge blazing rock wrapped in green and magenta "
            "fire, trailing a thick column of black smoke with dark burning fragments "
            "breaking off it, its glare lighting the stones of Stonehenge in hard colour, "
            "growing every second and filling more and more of the frame."
        ),
        son=(
            "The fireball hits the ground right in front of the camera: a blast of fire and "
            "earth slams across the lens, the frame floods blinding magenta-white, then "
            "dims to near black as soil and smoking ash rain down and bury the lens."
        ),
        son_durum=(
            "The camera is buried under the blast debris. The frame is almost black, with "
            "only a faint green and magenta glow through the smoking soil pressed against "
            "the lens. The roar of the impact is muffled and fading."
        ),
        ses=(
            ("0.0-1.5", "A soft awed gasp, then a held breath."),
            ("3.0-5.0", "Fast breathing as the hissing grows."),
            ("7.6-8.6", "A short wordless scream as the fireball streaks past."),
            ("12.5-15.0", "A long wordless scream swallowed by the roar of the impact, cut "
                          "off as the earth buries the camera."),
        ),
        caption=(
            "You're sliding over Stonehenge in Wiltshire at midsummer twilight, then "
            "through a cloud into a sky full of falling fireballs. Would you keep going?"
        ),
        emoji="☄️\U0001F525", etiket="#Stonehenge",
        basliklar=(
            "Stonehenge under a meteor storm #shorts",
            "Stonehenge slide into fireballs #shorts",
            "Stonehenge, then the sky falls #shorts",
        ),
    ),
    "petra-hazine-sel": dict(
        sehir="Petra", landmark="the Treasury at Petra", neon="plasma blue",
        palet="neon", anahtar="Petra", isik="mavi-beyaz",
        hava="a cold clear night under the Milky Way above the rose-red cliffs",
        felaket="a night flash flood roaring down the Siq canyon",
        ilk_kare=(
            "Far below and ahead, filling the upper half of the frame: the Treasury at "
            "Petra on a cold clear night, its tall columned facade carved straight into the "
            "rose-red cliff, glowing soft pink in the light of a low half moon. The narrow "
            "dark crack of the Siq canyon winds up to it through the sandstone. Above, the "
            "Milky Way arches bright across a black sky full of stars over the rocky desert "
            "mountains. A thick white cloud bank lies across the canyons below the slide, "
            "and the slide dives down toward it."
        ),
        acilis=(
            "The Treasury fills the centre of the frame, its two stacked rows of carved "
            "columns and the round urn-topped temple on the upper level glowing rose pink "
            "in the moonlight, framed by the dark canyon walls. The slide drops past the "
            "carved urn on top of the facade close enough to see the worn sandstone layers "
            "of pink, orange and cream rush up and past on the right, the empty sand plaza "
            "in front of it far below."
        ),
        kapi_ici=(
            "The air turns damp and cold, the murk inside the cloud flashes blue-white, and "
            "the first heavy drops of rain streak across the lens as thunder booms."
        ),
        ortaya=(
            "the same canyon in a night storm. The Treasury stands pale against a black sky "
            "split by blue-white lightning, each flash lighting the carved columns and the "
            "red cliffs in hard cold light. Rain pours down the cliff faces in sheets and "
            "runs off the rock in dozens of thin waterfalls into the dark crack of the Siq."
        ),
        tirmanis=(
            "The water in the Siq rises fast. A brown torrent is surging through the narrow "
            "canyon toward the Treasury, pounding off the walls and throwing up spray, lit "
            "blue-white by the lightning, and rocks break off the cliff and splash into it. "
            "Thunder shakes the slide as it dives down between the red canyon walls toward "
            "the plaza, and rain streams over the clear floor under her feet."
        ),
        doruk=(
            "The flash flood bursts out of the mouth of the Siq into the plaza in front of "
            "the Treasury and roars toward the slide from the left side of the frame, a "
            "churning wall of dark brown water and red mud with boulders, broken palm "
            "trunks and uprooted bushes inside it, its foaming crest lit blue-white by "
            "lightning, growing every second and filling more and more of the frame."
        ),
        son=(
            "The flood hits the camera: brown water slams across the lens, the frame floods "
            "blue-white with one last lightning flash, then dims to near black as the muddy "
            "water closes over the lens and drags it under."
        ),
        son_durum=(
            "The camera is under the flood water. The frame is almost black, with only a "
            "faint blue-white flicker of lightning through the muddy water pressed against "
            "the lens. The roar of the flood is muffled and fading."
        ),
        ses=(
            ("0.0-1.5", "A quiet gasp in the cold night air, then a held breath."),
            ("3.0-5.0", "Shaky breathing as thunder booms in the cloud."),
            ("7.6-8.6", "A short wordless scream at the lightning flash."),
            ("12.5-15.0", "A long wordless scream swallowed by the roar of the flood, cut "
                          "off as the water closes over the camera."),
        ),
        caption=(
            "You're sliding over the Treasury at Petra under the Milky Way, then through a "
            "cloud into a flash flood in the canyon. Would you ride this at night?"
        ),
        emoji="\U0001F30C\U0001F30A", etiket="#PetraTreasury",
        basliklar=(
            "Petra Treasury flash flood drop #shorts",
            "Petra stars, then the flood #shorts",
            "Petra canyon flood at night #shorts",
        ),
    ),
    # 2026-10-29 ikinci KAPI dalgasi (14 rota). Stok 17 Ekim'de bitti, 18 Ekim'den
    # beri tekrar yayinlaniyordu ve ayni ilk kareyle acilan tekrarlar 6/6 coktu
    # (Grand Canyon 144K -> 5K). Felaketler olculen kazanan turlerden: dev, okunur,
    # bulut cikisinda (6.0-8.5) gorunen TEK tehdit; deprem, hortum, tsunami, meteor,
    # yangin, tipi YOK. Sira ve renk kurallari gunluk.py SIRA yorumunda.
    "atina-akropol-toz-firtinasi": dict(
        sehir="Athens", landmark="the Acropolis", neon="electric blue",
        palet="sicak", anahtar="Acropolis", isik="sodyum-amber",
        hava="a clear golden spring morning over the city, the sky soft blue",
        felaket="an orange Saharan dust storm, a towering wall of dust with lightning inside it",
        ilk_kare=(
            "Far below and ahead, filling the upper half of the frame: the Acropolis of "
            "Athens seen from the FRONT on a clear golden spring morning, the great rock "
            "rising out of the city with the Parthenon on its flat summit, its long row of "
            "pale marble columns facing the camera and glowing gold in the low sun. Steep "
            "cliffs of grey rock and silver olive trees ring the hill. The white city spreads "
            "in every direction beyond, with the pointed green hill of Lycabettus behind it "
            "and the blue sea far off on one side. A thick white cloud bank lies across the "
            "city below the slide, and the slide dives down toward it."
        ),
        acilis=(
            "The Acropolis fills the centre of the frame, the Parthenon standing on the "
            "summit of its rock, every fluted marble column and the broken stone gable sharp "
            "in the morning sun. The slide drops past the corner of the Parthenon close "
            "enough to see the cracked honey-coloured marble blocks and the grooves of the "
            "columns rush up and past on the left, the ancient stone stairs and the olive "
            "trees on the slopes far below."
        ),
        kapi_ici=(
            "The air turns hot and dry, the murk inside the cloud turns a dusty orange, and "
            "the first fine grains of grit start to hiss against the lens."
        ),
        ortaya=(
            "the same city swallowed by a Saharan dust storm. The Parthenon stands pale on "
            "its rock under a deep orange sky, and beyond it a towering wall of orange dust "
            "taller than the Acropolis rolls in from the sea across the whole horizon, "
            "burying the white city street by street. Lightning flickers inside the wall. "
            "Dust streams sideways across the lens."
        ),
        tirmanis=(
            "Lightning cracks out of the dust wall and strikes the hillside below the "
            "Acropolis, lighting every marble column white for an instant, and thunder "
            "shakes the slide. Gusts throw grit across the frame in long orange streaks, the "
            "slide shudders and bucks, and dust hisses over the clear floor under her feet. "
            "Lycabettus is already gone inside the orange, and the shadow of the storm races "
            "across the rooftops toward the rock."
        ),
        doruk=(
            "The dust wall reaches the foot of the Acropolis and climbs the cliffs, "
            "swallowing the olive trees and the old stone walls. It rolls straight toward "
            "the slide from the right side of the frame, a boiling cliff of dark orange dust "
            "with torn branches, roof tiles and flying grit inside it, lit by flickers of "
            "lightning, growing every second and filling more and more of the frame."
        ),
        son=(
            "The dust wall slams into the camera: grit blasts across the lens, the frame "
            "goes solid burning orange, then dims to near black as dust piles over the lens."
        ),
        son_durum=(
            "The camera is buried inside the dust storm. The frame is almost black, with "
            "only a faint orange glow through the dust pressed against the lens. The roar of "
            "the wind is muffled and fading."
        ),
        ses=(
            ("0.0-1.5", "A sharp gasp at the height, then a held breath."),
            ("3.0-5.0", "Dry, ragged breaths inside the dusty cloud."),
            ("7.6-8.6", "A short wordless scream as the lightning strikes."),
            ("12.5-15.0", "A long wordless scream swallowed by the roar of the dust, cut "
                          "off as the dust buries the camera."),
        ),
        caption=(
            "You're sliding past the Parthenon on the Acropolis in Athens, then through a "
            "cloud into an orange dust storm taller than the hill. Would you keep your eyes "
            "open?"
        ),
        emoji="\U0001F3DB️⚡", etiket="#Acropolis",
        basliklar=(
            "Acropolis drop into a dust storm #shorts",
            "Acropolis, then the orange wall #shorts",
            "Acropolis under an orange sky #shorts",
        ),
    ),
    "paris-eyfel-dolu": dict(
        sehir="Paris", landmark="the Eiffel Tower", neon="electric fuchsia",
        palet="neon", anahtar="Eiffel Tower", isik="yesil-civa",
        hava="a soft summer evening over the Seine, the sky clear and pale gold",
        felaket="a giant hail supercell under a green-black sky",
        ilk_kare=(
            "Far below and ahead, filling the upper half of the frame: the Eiffel Tower "
            "seen from the FRONT, from across the river, on a soft summer evening, its brown "
            "iron lattice glowing warm in the low sun and its four great legs arching over "
            "the long green lawns of the Champ de Mars. The Seine runs in front of it under "
            "its stone bridges. The grey rooftops of Paris stretch away to the horizon on "
            "every side. A thick white cloud bank lies across the city below the slide, and "
            "the slide dives down toward it."
        ),
        acilis=(
            "The Eiffel Tower fills the centre of the frame, its iron lattice narrowing to "
            "the slender top, the three platforms stacked one above the other, the evening "
            "sun glinting on every rivet. The slide drops past the very top of the tower "
            "close enough to see the criss-crossed brown girders and the bolts rush up and "
            "past on the right, the long green lawns of the Champ de Mars far below."
        ),
        kapi_ici=(
            "The air turns suddenly cold, the murk inside the cloud turns a sickly "
            "green-grey, and the first pellets of ice crack against the acrylic and bounce "
            "off the lens."
        ),
        ortaya=(
            "the same city under a giant hail supercell. The Eiffel Tower stands black "
            "against a green-black sky, a vast storm cloud hanging low over Paris with a "
            "white curtain of hail pouring from its base. Hailstones the size of golf balls "
            "smash onto the rooftops and bounce high off the streets, and the lawns of the "
            "Champ de Mars are turning white."
        ),
        tirmanis=(
            "The hail gets bigger. Lumps of ice the size of fists hammer the slide, crack "
            "white stars into the acrylic beside her shins and bounce off the rims, and one "
            "skids across the clear floor between her feet. A bolt of lightning strikes the "
            "top of the Eiffel Tower and lights the whole lattice white for an instant, and "
            "windows burst along the boulevards as the ice hits them."
        ),
        doruk=(
            "The hail curtain sweeps down the Seine toward the slide from the left side of "
            "the frame, a towering white wall of falling ice under the green-black cloud, "
            "hiding the bridges and then the legs of the tower, with shattered roof slates, "
            "shutters and torn chestnut branches tumbling inside it, growing every second "
            "and filling more and more of the frame."
        ),
        son=(
            "The hail wall hits the camera: ice hammers the lens, cracks spread across the "
            "glass, the frame goes blinding white, then dims to near black as hailstones "
            "pile up over the lens and bury it."
        ),
        son_durum=(
            "The camera lies buried under a heap of hailstones. The frame is almost black, "
            "with only a faint green-white glow through the packed ice pressed against the "
            "cracked lens. The drumming of the hail is muffled and fading."
        ),
        ses=(
            ("0.0-1.5", "A nervous gasp at the height, then a held breath."),
            ("3.0-5.0", "Short sharp breaths as the first ice hits."),
            ("7.6-8.6", "A wordless yelp as a hailstone cracks the acrylic."),
            ("12.5-15.0", "A long wordless scream under the hammering ice, cut off as the "
                          "hail buries the camera."),
        ),
        caption=(
            "You're sliding over the top of the Eiffel Tower in Paris on a summer evening, "
            "then through a cloud into hail the size of fists. Would you still go down?"
        ),
        emoji="⛈️\U0001F9CA", etiket="#EiffelTower",
        basliklar=(
            "Eiffel Tower slide into hail #shorts",
            "Eiffel Tower, then the green sky #shorts",
            "Eiffel Tower under a hail storm #shorts",
        ),
    ),
    "fuji-yanardag": dict(
        sehir="Japan", landmark="Mount Fuji", neon="arctic blue",
        palet="neon", anahtar="Mount Fuji", isik="kirmizi-tabela",
        hava="a clear late autumn afternoon, the air crisp and still",
        felaket="a volcanic eruption of Mount Fuji with a pyroclastic flow",
        ilk_kare=(
            "Far below and ahead, filling the upper half of the frame: Mount Fuji seen from "
            "the FRONT on a clear late autumn afternoon, its perfect cone rising alone above "
            "the plain, the upper slopes capped with bright white snow and the dark volcanic "
            "rock below streaked with long white gullies. Forests of red and gold autumn "
            "maples and dark green pines cover its lower slopes, and small towns and fields "
            "spread around its foot. A thick white cloud bank lies across the foothills "
            "below the slide, and the slide dives down toward it."
        ),
        acilis=(
            "Mount Fuji fills the centre of the frame, its snow-capped summit and the wide "
            "jagged rim of the crater sharp against the blue sky, long streaks of snow "
            "running down the dark rock. The slide drops past the crater rim close enough to "
            "see the loose black cinders, the frozen snow crust and the red-brown lava rock "
            "rush up and past on the left, the autumn forests far below."
        ),
        kapi_ici=(
            "The air turns hot and smells of sulphur, the murk inside the cloud darkens to "
            "dirty grey, and a deep rumble shakes the acrylic as fine ash settles on the lens."
        ),
        ortaya=(
            "the same mountain erupting. A towering black column of ash blasts out of the "
            "summit crater of Mount Fuji into a dark brown sky, lit from below by fountains "
            "of orange lava, and the snow on the upper slopes is bursting into white steam. "
            "Lightning crackles inside the ash cloud. Glowing lava bombs arc out of the "
            "crater and smash into the autumn forests, setting them on fire."
        ),
        tirmanis=(
            "The column grows taller and starts to sag. Ash rains down thickly, grey flakes "
            "streaking across the frame, and red-hot stones thud onto the slide, bouncing "
            "off the rims and leaving glowing scorch marks on the acrylic. A lava bomb bursts "
            "on the slope right beside the slide in a shower of sparks, and a river of orange "
            "lava pours down through the snow, throwing up white steam where it meets the ice."
        ),
        doruk=(
            "Part of the ash column falls back onto the mountain and becomes a pyroclastic "
            "flow, a boiling avalanche of grey-black ash, steam and hot gas pouring down the "
            "snowy cone of Mount Fuji toward the slide from the right side of the frame, "
            "glowing red at its base, with burning pines and black rocks tumbling inside it, "
            "growing every second and filling more and more of the frame."
        ),
        son=(
            "The pyroclastic flow rolls over the camera: hot ash blasts across the lens, the "
            "frame floods glowing red-orange, then dims to near black as thick grey ash "
            "settles over the lens and buries it."
        ),
        son_durum=(
            "The camera lies buried under the ash on the slopes of Mount Fuji. The frame is "
            "almost black, with only a faint dull red glow through the hot ash pressed "
            "against the lens. The rumble of the eruption is muffled and fading."
        ),
        ses=(
            ("0.0-1.5", "A sharp gasp at the height, then a held breath."),
            ("3.0-5.0", "Coughing, frightened breaths in the hot grey cloud."),
            ("8.0-9.0", "A short wordless scream as the lava bomb bursts."),
            ("12.5-15.0", "A long wordless scream swallowed by the roar of the flow, cut "
                          "off as the ash buries the camera."),
        ),
        caption=(
            "You're sliding over the snowy crater of Mount Fuji in Japan, then through a "
            "cloud as the mountain erupts beneath you. Would you dare look down?"
        ),
        emoji="\U0001F5FB\U0001F30B", etiket="#MountFuji",
        basliklar=(
            "Mount Fuji drop into an eruption #shorts",
            "Mount Fuji erupts under you #shorts",
            "Mount Fuji, snow to lava #shorts",
        ),
    ),
    "dubai-burj-yildirim": dict(
        sehir="Dubai", landmark="the Burj Khalifa", neon="electric chartreuse",
        palet="sicak", anahtar="Burj Khalifa", isik="mor-tabela",
        hava="a hazy golden desert evening, the air hot and still",
        felaket="a desert lightning supercell with violet lightning, hail and a wall of dust",
        ilk_kare=(
            "Far below and ahead, filling the upper half of the frame: the Burj Khalifa in "
            "Dubai seen from the FRONT on a hazy golden desert evening, the tallest tower on "
            "Earth rising in stepped silver tiers to a needle-thin spire, its glass catching "
            "the low sun. The glittering towers of downtown Dubai cluster around its foot, "
            "the pale desert stretches away to the horizon on one side and the calm blue "
            "Gulf lies on the other. A thick white cloud bank lies across the city below the "
            "slide, and the slide dives down toward it."
        ),
        acilis=(
            "The Burj Khalifa fills the centre of the frame, its silver glass tiers stepping "
            "inward toward the spire, gold light sliding over the panels. The slide drops "
            "past the very top of the spire close enough to see the steel ribs, the red "
            "warning lights and the glass panels rush up and past on the left, the tops of "
            "the other skyscrapers tiny far below."
        ),
        kapi_ici=(
            "The air turns hot and electric, the murk inside the cloud flickers violet from "
            "somewhere below, and a deep rumble of thunder shakes the acrylic."
        ),
        ortaya=(
            "the same city under a desert supercell. A huge black storm cloud hangs low over "
            "Dubai, its base flickering violet, and the Burj Khalifa stands dark beneath it. "
            "Bolts of violet-white lightning crack down out of the cloud and strike the spire "
            "again and again, each flash lighting the whole tower for an instant. Far out "
            "over the desert a brown wall of dust is rising under the storm."
        ),
        tirmanis=(
            "A bolt strikes the spire right beside the slide and the flash burns the frame "
            "white for an instant, sparks raining down the glass. Thunder shakes the slide, "
            "hailstones crack against the acrylic and bounce off the rims, and grit and ice "
            "rattle across the clear floor under her feet. The dust wall rolls in from the "
            "desert and swallows the outer towers one after another."
        ),
        doruk=(
            "The core of the storm sweeps across the city toward the slide from the right "
            "side of the frame, a towering black-violet wall of hail, rain and dust taller "
            "than the Burj Khalifa, lit from inside by violet lightning, with torn palm "
            "fronds, shattered glass panels and flying debris inside it, growing every "
            "second and filling more and more of the frame."
        ),
        son=(
            "The storm wall slams into the camera: hail and dust blast across the lens, the "
            "frame floods violet-white under one last lightning flash, then dims to near "
            "black as mud and ice cover the lens."
        ),
        son_durum=(
            "The camera is buried inside the storm. The frame is almost black, with only a "
            "faint violet flicker of lightning through the mud and ice pressed against the "
            "lens. The roar of the wind and the thunder is muffled and fading."
        ),
        ses=(
            ("0.0-1.5", "A sharp gasp at the height, then a held breath."),
            ("3.0-5.0", "Tight, shallow breathing in the flickering cloud."),
            ("7.6-8.6", "A short wordless scream as the lightning hits the spire."),
            ("12.5-15.0", "A long wordless scream drowned by the roar of the storm, cut "
                          "off as the storm wall buries the camera."),
        ),
        caption=(
            "You're sliding past the spire of the Burj Khalifa in Dubai, then through a "
            "cloud into a lightning storm over the desert. Would you take this ride?"
        ),
        emoji="\U0001F3D9️⚡", etiket="#BurjKhalifa",
        basliklar=(
            "Burj Khalifa struck by lightning #shorts",
            "Burj Khalifa slide into a storm #shorts",
            "Burj Khalifa, then a violet sky #shorts",
        ),
    ),
    "sanfrancisco-goldengate-dev-dalga": dict(
        sehir="San Francisco", landmark="the Golden Gate Bridge", neon="electric gold",
        palet="neon", anahtar="Golden Gate", isik="buz-mavi",
        hava="a bright clear winter morning over the bay, the water calm and blue",
        felaket="a Pacific storm driving giant storm waves through the Golden Gate",
        ilk_kare=(
            "Far below and ahead, filling the upper half of the frame: the Golden Gate "
            "Bridge seen from the FRONT, from the ocean side, on a bright clear winter "
            "morning, its two tall red-orange towers and the long sweep of its cables "
            "spanning the strait, the green Marin Headlands on the left and the city of San "
            "Francisco on the right. The calm blue water of the strait sparkles beneath it, "
            "and the bay opens out beyond. A thick white cloud bank lies across the strait "
            "below the slide, and the slide dives down toward it."
        ),
        acilis=(
            "The Golden Gate Bridge fills the centre of the frame, its two red-orange towers "
            "rising high above the deck, the great cables sagging between them and hundreds "
            "of thin cables hanging straight down to the road. The slide drops past the top "
            "of the nearest tower close enough to see the riveted steel panels and the red "
            "paint rush up and past on the left, the calm blue strait far below."
        ),
        kapi_ici=(
            "The air turns cold and salty, the murk inside the cloud darkens to blue-grey, "
            "and the first heavy drops of rain and sea spray streak sideways across the lens."
        ),
        ortaya=(
            "the same strait in a Pacific storm. The Golden Gate Bridge stands dark red "
            "against a black sky, rain blowing sideways in sheets, and the strait below "
            "heaves with grey water and white foam. Far out at sea a huge dark ridge of water "
            "is rising, a giant storm wave rolling in from the Pacific toward the bridge."
        ),
        tirmanis=(
            "A gust slams the slide sideways and the whole tube shudders and flexes, the "
            "acrylic groaning. Spray tears off the waves and blasts across the clear floor "
            "under her feet. The first big swell bursts against the foot of the south tower "
            "and explodes white up the steel, and the bridge deck sways as the wind howls "
            "through the cables. Out at sea the giant wave keeps rising, taller every second."
        ),
        doruk=(
            "The giant wave rolls through the Golden Gate toward the slide from the left "
            "side of the frame, a towering dark grey wall of sea water higher than the bridge "
            "deck, with broken pier timbers, floating logs and a capsized fishing boat inside "
            "it, its icy blue-white crest breaking, growing every second and filling more "
            "and more of the frame."
        ),
        son=(
            "The wave crashes over the camera: foaming water slams across the lens, the "
            "frame floods icy blue-grey, then dims to near black as the sea closes over the "
            "lens and drags it under."
        ),
        son_durum=(
            "The camera is deep under the storm wave. The frame is almost black, with only a "
            "faint blue-grey glow far above through the churning water and a stream of "
            "bubbles crossing the lens. The roar of the sea is muffled and fading."
        ),
        ses=(
            ("0.0-1.5", "A sharp gasp at the height, then a held breath."),
            ("3.0-5.0", "Fast shaky breathing inside the cold cloud."),
            ("7.6-8.6", "A short wordless scream as the gust slams the slide."),
            ("12.5-15.0", "A long wordless scream drowned by the roar of the wave, cut off "
                          "as the sea closes over the camera."),
        ),
        caption=(
            "You're sliding past the towers of the Golden Gate Bridge in San Francisco, then "
            "through a cloud toward a giant storm wave. Would you go under it?"
        ),
        emoji="\U0001F309\U0001F30A", etiket="#GoldenGateBridge",
        basliklar=(
            "Golden Gate, a giant wave below #shorts",
            "Golden Gate Bridge, then a wave #shorts",
            "Golden Gate storm wave drop #shorts",
        ),
    ),
    "everest-cig": dict(
        sehir="Nepal", landmark="Mount Everest", neon="neon scarlet",
        palet="neon", anahtar="Everest", isik="civa-beyaz",
        hava="a clear cold morning high in the Himalaya, the sky deep blue",
        felaket="a colossal avalanche pouring down the face of the mountain",
        ilk_kare=(
            "Far below and ahead, filling the upper half of the frame: Mount Everest seen "
            "from the FRONT on a clear cold morning, its dark rock summit pyramid rising "
            "above every other peak, a long white plume of snow blowing off the top into the "
            "deep blue sky. The huge ice walls of Lhotse and Nuptse stand beside it, and the "
            "broken white river of the Khumbu glacier runs down from its foot. A thick white "
            "cloud bank lies across the valley below the slide, and the slide dives down "
            "toward it."
        ),
        acilis=(
            "Mount Everest fills the centre of the frame, its black rock summit pyramid "
            "streaked with snow and ice, the plume of blowing snow glittering in the sun. The "
            "slide drops past the summit ridge close enough to see the wind-carved snow, the "
            "blue ice and the dark bands of rock rush up and past on the right, the white "
            "glaciers thousands of metres below."
        ),
        kapi_ici=(
            "The air turns bitterly cold and thin, the murk inside the cloud turns a hard "
            "bluish white, and frost spreads in feathers across the edges of the lens."
        ),
        ortaya=(
            "the same mountain as the snow lets go. A grey storm sky hangs over Everest, and "
            "across its huge white face a long crack has torn open in the snow. A whole slab "
            "of the mountain breaks away and a white avalanche begins pouring down the face, "
            "throwing up a rising cloud of snow taller than the ridge."
        ),
        tirmanis=(
            "The avalanche thunders down the face and grows, its white cloud boiling higher "
            "than the summit, blocks of blue ice the size of houses tumbling at its front. "
            "The blast of air ahead of it hits the slide, the tube shudders and creaks, and "
            "ice crystals and snow streak across the clear floor under her feet. The glacier "
            "below disappears under the white."
        ),
        doruk=(
            "The avalanche crosses the valley and pours toward the slide from the left side "
            "of the frame, a towering white wall of snow and ice with blue ice blocks, broken "
            "rock and black stones tumbling inside it, its hard white glare growing every "
            "second and filling more and more of the frame."
        ),
        son=(
            "The avalanche hits the camera: snow blasts across the lens, the frame floods "
            "blinding white, then dims to near black as packed snow buries the lens."
        ),
        son_durum=(
            "The camera lies buried deep under the avalanche. The frame is almost black, "
            "with only a faint cold blue-white glow through the packed snow pressed against "
            "the lens. The roar of the snow is muffled and fading."
        ),
        ses=(
            ("0.0-1.5", "A sharp gasp of thin cold air, then a held breath."),
            ("3.0-5.0", "Shivering, shallow breaths in the frozen cloud."),
            ("7.0-8.0", "A short wordless scream as the slope breaks away."),
            ("12.5-15.0", "A long wordless scream lost in the roar of the snow, cut off as "
                          "the avalanche buries the camera."),
        ),
        caption=(
            "You're sliding over the summit of Mount Everest in Nepal, then through a cloud "
            "as the whole mountain face comes down. Would you still jump in?"
        ),
        emoji="\U0001F3D4️❄️", etiket="#MountEverest",
        basliklar=(
            "Everest slide into an avalanche #shorts",
            "Everest summit, then it falls #shorts",
            "Mount Everest avalanche drop #shorts",
        ),
    ),
    "tokyo-kule-tayfun": dict(
        sehir="Tokyo", landmark="Tokyo Tower", neon="neon mint",
        palet="neon", anahtar="Tokyo Tower", isik="kirmizi-tabela",
        hava="a clear blue late-summer afternoon over the bay",
        felaket="a super typhoon with a towering wall of wind-driven rain",
        ilk_kare=(
            "Far below and ahead, filling the upper half of the frame: Tokyo Tower seen from "
            "the FRONT on a clear blue late-summer afternoon, its orange-red and white steel "
            "lattice rising from a green park, the curved grey temple roofs of Zojo-ji at "
            "its foot. The endless grey and white city of Tokyo spreads to the horizon "
            "around it, and the blue water of Tokyo Bay lies beyond, crossed by a long white "
            "suspension bridge. A thick white cloud bank lies across the city below the "
            "slide, and the slide dives down toward it."
        ),
        acilis=(
            "Tokyo Tower fills the centre of the frame, its orange and white bands of steel "
            "narrowing toward the antenna, the two observation decks wrapped in glass. The "
            "slide drops past the upper observation deck close enough to see the painted "
            "steel beams, the rivets and the red warning lights rush up and past on the "
            "right, the green park and the temple roofs far below."
        ),
        kapi_ici=(
            "The air turns warm and soaking wet, the murk inside the cloud darkens to slate "
            "grey, and rain begins to blast sideways across the lens."
        ),
        ortaya=(
            "the same city in a super typhoon. Tokyo Tower glows orange-red against a black "
            "sky, its lights blazing, while rain blows sideways across the city in grey "
            "sheets and the streets below run like rivers. Out over Tokyo Bay a towering "
            "black wall of wind and rain, taller than the tower, is marching toward the "
            "city, tearing the sea white beneath it."
        ),
        tirmanis=(
            "A gust slams the slide sideways and the whole tube bends and groans. Signboards, "
            "roof panels and umbrellas tear loose from the buildings and tumble through the "
            "air past the slide, and the trees in the park lie flat. The red warning lights "
            "of the tower flash through the rain, water streams over the clear floor under "
            "her feet, and the bridge over the bay disappears into the black wall."
        ),
        doruk=(
            "The typhoon wall crosses the bay and rolls over the city toward the slide from "
            "the left side of the frame, a towering black-grey wall of driven rain and wind, "
            "lit orange-red by the glow of the tower, with roof panels, shattered glass and "
            "torn signboards flying inside it, growing every second and filling more and "
            "more of the frame."
        ),
        son=(
            "The typhoon wall hits the camera: rain and debris blast across the lens, the "
            "frame floods dark orange-grey, then dims to near black as water and torn leaves "
            "plaster over the lens."
        ),
        son_durum=(
            "The camera is caught inside the typhoon. The frame is almost black, with only a "
            "faint orange-red glow of the tower through the water streaming over the lens. "
            "The howl of the wind is muffled and fading."
        ),
        ses=(
            ("0.0-1.5", "A sharp gasp at the height, then a held breath."),
            ("3.0-5.0", "Fast, frightened breathing in the soaking cloud."),
            ("7.6-8.6", "A short wordless scream as the gust slams the slide."),
            ("12.5-15.0", "A long wordless scream lost in the howl of the typhoon, cut off "
                          "as the storm swallows the camera."),
        ),
        caption=(
            "You're sliding past Tokyo Tower on a summer afternoon, then through a cloud "
            "into a super typhoon over Tokyo. Would you stay on the slide?"
        ),
        emoji="\U0001F5FC\U0001F300", etiket="#TokyoTower",
        basliklar=(
            "Tokyo Tower slide into a typhoon #shorts",
            "Tokyo Tower, then the black wall #shorts",
            "Tokyo Tower super typhoon drop #shorts",
        ),
    ),
    "agra-tacmahal-sel": dict(
        sehir="Agra", landmark="the Taj Mahal", neon="neon saffron",
        palet="sicak", anahtar="Taj Mahal", isik="led-beyaz",
        hava="a soft golden sunrise over the river, the air warm and hazy",
        felaket="a monsoon flash flood of the Yamuna river under a black sky",
        ilk_kare=(
            "Far below and ahead, filling the upper half of the frame: the Taj Mahal seen "
            "from the FRONT, from the end of its long garden, at a soft golden sunrise, the "
            "white marble dome and the four slender minarets glowing pale pink and gold, "
            "perfectly centred and symmetrical. A long straight water channel and rows of "
            "dark cypress trees lead up to it through the green garden, and a red sandstone "
            "mosque stands on one side. The wide brown Yamuna river runs behind it. A thick "
            "white cloud bank lies across the garden below the slide, and the slide dives "
            "down toward it."
        ),
        acilis=(
            "The Taj Mahal fills the centre of the frame, its great white onion dome rising "
            "over the tall arched gateway of the main hall, the four minarets standing at the "
            "corners of the marble platform. The slide drops past the gold finial on top of "
            "the dome close enough to see the white marble panels and the inlaid flowers of "
            "coloured stone rush up and past on the left, the long garden and the cypress "
            "trees far below."
        ),
        kapi_ici=(
            "The air turns heavy and steaming wet, the murk inside the cloud darkens to "
            "slate grey, and warm monsoon rain starts to stream down the lens."
        ),
        ortaya=(
            "the same garden in a monsoon cloudburst. The Taj Mahal glows pale white against "
            "a black sky, lit hard white by lightning, and rain pours down in grey sheets. "
            "Behind it the Yamuna has burst its banks: a wide brown flood is sweeping down "
            "the river and pouring over the riverside walls into the garden."
        ),
        tirmanis=(
            "The flood water rises fast. A brown surge pours through the garden, swallowing "
            "the water channel and the cypress trees and climbing the steps of the marble "
            "platform, and lightning lights the white dome for an instant. Rain hammers the "
            "acrylic so hard that brown water runs over the clear floor under her feet, and "
            "uprooted trees roll past on the current below."
        ),
        doruk=(
            "The main flood wave comes roaring down the Yamuna and over the walls toward the "
            "slide from the right side of the frame, a churning wall of brown water and mud "
            "rising up the marble platform, with uprooted trees, broken boats and wooden "
            "debris tumbling inside it, its foaming crest lit white by lightning, growing "
            "every second and filling more and more of the frame."
        ),
        son=(
            "The flood wave smashes into the camera: brown water surges across the lens, the "
            "frame floods dark muddy brown under one last white flash, then dims to near "
            "black as the water closes over the lens."
        ),
        son_durum=(
            "The camera is under the flood. The frame is almost black, with only a faint "
            "white flicker of lightning through the silty water pressed against the lens. "
            "The roar of the river is muffled and fading."
        ),
        ses=(
            ("0.0-1.5", "A soft nervous gasp, then a held breath."),
            ("3.0-5.0", "Wet, shaky breaths inside the monsoon cloud."),
            ("7.6-8.6", "A short wordless scream as the lightning flashes."),
            ("12.5-15.0", "A long wordless scream drowned by the roar of the flood, cut off "
                          "as the water closes over the camera."),
        ),
        caption=(
            "You're sliding over the dome of the Taj Mahal in Agra at sunrise, then through "
            "a cloud into a monsoon flood. Would you keep sliding?"
        ),
        emoji="\U0001F54C\U0001F30A", etiket="#TajMahal",
        basliklar=(
            "Taj Mahal slide into a flood #shorts",
            "Taj Mahal, then the river rises #shorts",
            "Taj Mahal under a monsoon sky #shorts",
        ),
    ),
    "rio-cristo-yildirim": dict(
        sehir="Rio de Janeiro", landmark="Christ the Redeemer", neon="neon green",
        palet="neon", anahtar="Christ the Redeemer", isik="mavi-beyaz",
        hava="a warm humid afternoon over the bay, the sky bright and blue",
        felaket="a tropical lightning storm striking the statue",
        ilk_kare=(
            "Far below and ahead, filling the upper half of the frame: Christ the Redeemer "
            "seen from the FRONT on a warm afternoon, the huge pale stone statue standing "
            "with its arms spread wide on the summit of the steep granite peak of Corcovado, "
            "its face toward the camera. Thick green rainforest pours down the steep slopes "
            "around it, and the city of Rio de Janeiro, its beaches and the blue sea curve "
            "along the shore far below. A thick white cloud bank lies across the city below "
            "the slide, and the slide dives down toward it."
        ),
        acilis=(
            "Christ the Redeemer fills the centre of the frame, the pale stone statue "
            "standing tall on its pedestal, arms stretched straight out to each side, the "
            "folds of its robe sharp in the afternoon sun. The slide drops past its "
            "outstretched right hand close enough to see the small pale soapstone tiles and "
            "the thin lightning rods on the fingers rush up and past on the left, the green "
            "forest dropping away far below."
        ),
        kapi_ici=(
            "The air turns hot and heavy, the murk inside the cloud flashes blue-white, and "
            "thunder booms so close that the acrylic buzzes under her legs."
        ),
        ortaya=(
            "the same mountain under a tropical lightning storm. Christ the Redeemer stands "
            "pale against a black sky, and bolts of blue-white lightning crack down out of "
            "the storm and strike the head and the outstretched arms of the statue one after "
            "another, each flash lighting it blinding white. Rain pours off the arms in "
            "streams and the rainforest below thrashes in the wind."
        ),
        tirmanis=(
            "A bolt strikes the hand of the statue right beside the slide and blasts sparks "
            "and chips of stone into the air, the flash burning the frame white for an "
            "instant. Thunder shakes the slide, the gusts bend the forest flat, and rain "
            "streams over the clear floor under her feet. Behind the statue the black core "
            "of the storm is coming over the mountains, swallowing the peaks."
        ),
        doruk=(
            "The black storm core rolls over Corcovado toward the slide from the right side "
            "of the frame, a towering wall of dark cloud and torrential rain crackling with "
            "blue-white bolts, with shredded palm fronds, broken branches and flying leaves "
            "inside it, swallowing the arms of the statue, growing every second and filling "
            "more and more of the frame."
        ),
        son=(
            "A last bolt strikes the slide right in front of the camera: the frame flashes "
            "blinding blue-white, rain and sparks blast across the lens, then it dims to near "
            "black as the black storm closes over the lens."
        ),
        son_durum=(
            "The camera is inside the black storm cloud. The frame is almost black, with "
            "only a faint blue-white flicker of lightning through the water streaming over "
            "the lens. The crash of the thunder is muffled and fading."
        ),
        ses=(
            ("0.0-1.5", "A sharp gasp at the height, then a held breath."),
            ("3.0-5.0", "Fast, uneasy breaths as thunder booms in the cloud."),
            ("7.6-8.6", "A short wordless scream as the bolt strikes the hand."),
            ("12.5-15.0", "A long wordless scream swallowed by the thunder, cut off as the "
                          "storm closes over the camera."),
        ),
        caption=(
            "You're sliding past the outstretched hand of Christ the Redeemer in Rio de "
            "Janeiro, then through a cloud into a lightning storm. Would you hold your breath?"
        ),
        emoji="⛈️⚡", etiket="#ChristTheRedeemer",
        basliklar=(
            "Christ the Redeemer storm drop #shorts",
            "Christ the Redeemer in lightning #shorts",
            "Christ the Redeemer, then a bolt #shorts",
        ),
    ),
    "venedik-sanmarco-taskin": dict(
        sehir="Venice", landmark="St. Mark's Square", neon="sapphire blue",
        palet="neon", anahtar="Venice", isik="sodyum-amber",
        hava="a calm golden autumn afternoon over the lagoon, the water flat and bright",
        felaket="a storm surge flood driven in from the lagoon by a gale",
        ilk_kare=(
            "Far below and ahead, filling the upper half of the frame: St. Mark's Square in "
            "Venice seen from the FRONT, from the lagoon, on a calm golden autumn afternoon: "
            "the tall red brick bell tower of the Campanile with its green pointed spire and "
            "gold angel, the pink and white arches of the Doge's Palace along the waterfront, "
            "and the domes of St. Mark's Basilica behind. Black gondolas are moored in a row "
            "along the stone quay, and the flat lagoon sparkles in front. A thick white cloud "
            "bank lies across the lagoon below the slide, and the slide dives down toward it."
        ),
        acilis=(
            "St. Mark's Square fills the centre of the frame, the Campanile rising high above "
            "the rooftops, the long arcades of the Doge's Palace and the gold mosaics of the "
            "basilica glowing in the low sun. The slide drops past the top of the Campanile "
            "close enough to see the gold angel, the green copper spire and the white stone "
            "arches of the belfry rush up and past on the right, the gondolas tiny on the "
            "quay far below."
        ),
        kapi_ici=(
            "The air turns cold and wet, a hard wind howls inside the cloud, the murk darkens "
            "to grey-green, and salt spray beads across the lens."
        ),
        ortaya=(
            "the same city drowning in a storm surge. The lagoon has risen over the quay and "
            "St. Mark's Square is a lake of black water under a dark slate sky, the lamps of "
            "the arcades glowing amber over it. A gale is driving the sea in from the lagoon, "
            "and far out a long grey ridge of water is rising and rolling toward the city."
        ),
        tirmanis=(
            "Waves smash over the waterfront and throw the gondolas against the Doge's "
            "Palace, splintering them, and water pours through the arcades. A gust slams the "
            "slide sideways and the acrylic groans, spray blasts across the frame, and sea "
            "water streams over the clear floor under her feet. The amber lamps flicker out "
            "one by one as the flood climbs the columns."
        ),
        doruk=(
            "The storm surge rolls across the lagoon toward the slide from the left side of "
            "the frame, a towering grey-green wall of sea water higher than the arcades, with "
            "broken gondolas, mooring poles and shattered wooden boats inside it, its white "
            "crest breaking, growing every second and filling more and more of the frame."
        ),
        son=(
            "The surge crashes over the camera: foaming sea water slams across the lens, the "
            "frame floods grey-green, then dims to near black as the water closes over the "
            "lens and drags it under."
        ),
        son_durum=(
            "The camera is under the flood water in the square. The frame is almost black, "
            "with only a faint amber glow of a drowned lamp through the churning water and a "
            "few rising bubbles. The roar of the sea is muffled and fading."
        ),
        ses=(
            ("0.0-1.5", "A sharp gasp at the height, then a held breath."),
            ("3.0-5.0", "Cold, shaky breaths in the howling cloud."),
            ("7.6-8.6", "A short wordless scream as the waves smash the gondolas."),
            ("12.5-15.0", "A long wordless scream drowned by the roar of the surge, cut off "
                          "as the water closes over the camera."),
        ),
        caption=(
            "You're sliding past the bell tower of St. Mark's Square in Venice, then through "
            "a cloud as the lagoon rises over the city. Would you ride it?"
        ),
        emoji="\U0001F6F6\U0001F30A", etiket="#Venice",
        basliklar=(
            "Venice slide into a storm surge #shorts",
            "Venice drowns under the slide #shorts",
            "Venice, then the lagoon rises #shorts",
        ),
    ),
    "lasvegas-strip-kum-firtinasi": dict(
        sehir="Nevada", landmark="the Las Vegas Strip", neon="cherry red",
        palet="sicak", anahtar="Las Vegas", isik="renkli-yikama",
        hava="a hot golden desert evening, the sky clear and orange",
        felaket="a haboob, a towering wall of desert dust rolling over the city",
        ilk_kare=(
            "Far below and ahead, filling the upper half of the frame: the Las Vegas Strip "
            "seen from the FRONT, from the south end, on a hot golden desert evening, the "
            "long boulevard of giant casino hotel towers in gold glass and white concrete "
            "running straight away from the camera, their bright signs and giant screens "
            "just lighting up pink, green and blue. The bare brown desert and the rocky "
            "mountains surround the city on every side under a clear orange sky. A thick "
            "white cloud bank lies across the desert below the slide, and the slide dives "
            "down toward it."
        ),
        acilis=(
            "The Las Vegas Strip fills the centre of the frame, a canyon of giant curved "
            "hotel towers lining the boulevard, the casino lights and giant screens glowing "
            "pink, green and blue in the dusk. The slide drops past the roof of the tallest "
            "gold tower close enough to see the gold glass panels and the roof lights rush up "
            "and past on the left, the traffic on the boulevard far below."
        ),
        kapi_ici=(
            "The air turns hot and dry, the murk inside the cloud turns a dirty brown, and "
            "the first grains of sand start to tick against the lens."
        ),
        ortaya=(
            "the same city swallowed by a haboob. A wall of rolling brown dust taller than "
            "the casino towers fills the whole horizon and boils across the desert toward "
            "the Strip, the sky above it black-brown. The signs and giant screens of the "
            "boulevard blaze pink, green and blue against the dark. Sand streams sideways "
            "across the lens."
        ),
        tirmanis=(
            "The dust wall hits the far end of the Strip and swallows the towers one after "
            "another, their lights glowing pink and green through the brown for an instant "
            "before they vanish. Gusts throw grit across the frame in long streaks, the slide "
            "shudders and bucks, and sand hisses over the clear floor under her feet. Palm "
            "trees bend flat along the boulevard and a giant screen tears loose and falls."
        ),
        doruk=(
            "The haboob rolls down the Strip straight toward the slide from the right side "
            "of the frame, a boiling cliff of dark brown dust lit from inside by flickering "
            "pink and green casino lights, with torn palm fronds, broken signs and flying "
            "debris inside it, growing every second and filling more and more of the frame."
        ),
        son=(
            "The dust wall slams into the camera: grit blasts across the lens, the frame goes "
            "solid dirty brown with a last smear of pink light, then dims to near black as "
            "sand piles over the lens."
        ),
        son_durum=(
            "The camera is buried inside the haboob. The frame is almost black, with only a "
            "faint pink and green glow of the drowned casino lights through the sand pressed "
            "against the lens. The roar of the wind is muffled and fading."
        ),
        ses=(
            ("0.0-1.5", "A sharp gasp at the height, then a held breath."),
            ("3.0-5.0", "Dry, ragged breaths inside the dusty cloud."),
            ("8.0-9.0", "A short wordless scream as the towers vanish."),
            ("12.5-15.0", "A long wordless scream swallowed by the roar of the sand, cut off "
                          "as the sand buries the camera."),
        ),
        caption=(
            "You're sliding over the Las Vegas Strip in Nevada at sunset, then through a "
            "cloud into a sandstorm taller than the casinos. Would you take this bet?"
        ),
        emoji="\U0001F3B0\U0001F32A️", etiket="#LasVegasStrip",
        basliklar=(
            "Las Vegas swallowed by a haboob #shorts",
            "Las Vegas Strip sandstorm drop #shorts",
            "Las Vegas, then the dust wall #shorts",
        ),
    ),
    "chichenitza-piramit-kasirga": dict(
        sehir="Mexico", landmark="the pyramid of Chichen Itza", neon="sunflower yellow",
        palet="neon", anahtar="Chichen Itza", isik="buz-mavi",
        hava="a bright humid morning over the jungle, the sky clear and blue",
        felaket="a major hurricane, its eyewall tearing across the jungle",
        ilk_kare=(
            "Far below and ahead, filling the upper half of the frame: the great stepped "
            "pyramid of Chichen Itza seen from the FRONT on a bright morning, its nine grey "
            "stone terraces rising to the square temple on top, the steep central staircase "
            "facing the camera with carved stone serpent heads at its foot. Wide green lawns "
            "surround it, and flat green jungle stretches away to the horizon on every side, "
            "with other ancient stone ruins half hidden among the trees. A thick white cloud "
            "bank lies across the jungle below the slide, and the slide dives down toward it."
        ),
        acilis=(
            "The pyramid of Chichen Itza fills the centre of the frame, its stepped grey "
            "terraces sharp in the morning sun, the four staircases climbing to the temple on "
            "its summit. The slide drops past the top of the temple close enough to see the "
            "carved stone doorway, the weathered limestone blocks and the moss in the cracks "
            "rush up and past on the left, the green lawn and the jungle far below."
        ),
        kapi_ici=(
            "The air turns warm, wet and roaring with wind, the murk inside the cloud darkens "
            "to steel grey, and rain begins to blast sideways across the lens."
        ),
        ortaya=(
            "the same jungle in the grip of a hurricane. The grey pyramid stands dark under a "
            "black sky, the jungle around it thrashing and bending flat in the wind, rain "
            "driving sideways in sheets. Beyond it the eyewall of the hurricane is coming: a "
            "towering grey wall of rain and wind taller than the pyramid, stretching across "
            "the whole horizon and flattening the forest as it comes."
        ),
        tirmanis=(
            "A gust slams the slide sideways and the whole tube shudders and flexes, the "
            "acrylic groaning. Whole trees rip out of the ground and tumble across the lawn "
            "past the pyramid, palm fronds and branches streak through the air, and rain "
            "blasts across the clear floor under her feet. Lightning flashes inside the "
            "eyewall and lights the stone terraces steel blue for an instant."
        ),
        doruk=(
            "The eyewall reaches the pyramid and swallows the temple on its summit. It rolls "
            "straight toward the slide from the right side of the frame, a towering "
            "steel-grey wall of driven rain and wind with uprooted trees, broken branches and "
            "flying stones inside it, growing every second and filling more and more of the "
            "frame."
        ),
        son=(
            "The eyewall slams into the camera: rain and debris blast across the lens, the "
            "frame floods steel blue-grey, then dims to near black as mud and shredded leaves "
            "plaster over the lens."
        ),
        son_durum=(
            "The camera is caught inside the hurricane. The frame is almost black, with only "
            "a faint steel-grey flicker through the mud and torn leaves stuck to the lens. "
            "The howl of the wind is muffled and fading."
        ),
        ses=(
            ("0.0-1.5", "A sharp gasp at the height, then a held breath."),
            ("3.0-5.0", "Fast, shaky breathing in the roaring cloud."),
            ("7.6-8.6", "A short wordless scream as the gust slams the slide."),
            ("12.5-15.0", "A long wordless scream lost in the howl of the hurricane, cut off "
                          "as the eyewall swallows the camera."),
        ),
        caption=(
            "You're sliding over the pyramid of Chichen Itza in Mexico, then through a cloud "
            "into the wall of a hurricane. Would you ride it out?"
        ),
        emoji="\U0001F334\U0001F300", etiket="#ChichenItza",
        basliklar=(
            "Chichen Itza, into a hurricane #shorts",
            "Chichen Itza, then the eyewall #shorts",
            "Chichen Itza hurricane drop #shorts",
        ),
    ),
    "bavyera-neuschwanstein-heyelan": dict(
        sehir="Bavaria", landmark="Neuschwanstein Castle", neon="flamingo pink",
        palet="neon", anahtar="Neuschwanstein", isik="yesil-civa",
        hava="a fresh early autumn morning in the Alps, the sky clear and pale blue",
        felaket="an Alpine cloudburst and a landslide of mud and rock",
        ilk_kare=(
            "Far below and ahead, filling the upper half of the frame: Neuschwanstein Castle "
            "seen from the FRONT, from the valley meadows, on a fresh early autumn morning, "
            "its white limestone walls, tall slender towers and grey-blue pointed roofs "
            "standing on a rocky ridge above a deep wooded gorge. Steep Alpine mountains "
            "covered in dark green pine and golden beech forest rise right behind it, and "
            "green meadows and a blue lake lie in the valley below. A thick white cloud bank "
            "lies across the valley below the slide, and the slide dives down toward it."
        ),
        acilis=(
            "Neuschwanstein Castle fills the centre of the frame, its white towers and "
            "turrets crowding along the narrow ridge, the gilded weather vanes and the "
            "grey-blue slate roofs bright in the morning sun. The slide drops past the top of "
            "the tallest tower close enough to see the white stone, the arched windows and "
            "the slate tiles rush up and past on the right, the deep wooded gorge and its "
            "waterfall far below."
        ),
        kapi_ici=(
            "The air turns wet and heavy, the murk inside the cloud darkens to grey-green, "
            "and cold rain begins to stream down the lens."
        ),
        ortaya=(
            "the same castle in an Alpine cloudburst. Neuschwanstein stands white against a "
            "black-green sky, rain pouring down in sheets, and the waterfall in the gorge "
            "below has turned into a roaring brown torrent. On the steep forested mountainside "
            "right behind the castle the slope is starting to crack and slip, raw brown mud "
            "showing through the torn trees."
        ),
        tirmanis=(
            "Rain hammers the acrylic so hard that brown water runs over the clear floor "
            "under her feet. A whole section of the mountainside tears loose above the castle "
            "and pours down in a river of mud and rock, snapping pines and hurling them into "
            "the air. Boulders bounce down the slope past the slide, and a lightning flash "
            "lights the white towers for an instant."
        ),
        doruk=(
            "The main landslide breaks away from the mountain and pours down toward the slide "
            "from the left side of the frame, a churning wall of dark brown mud and grey rock "
            "with uprooted pines, boulders and broken timber tumbling inside it, sweeping "
            "toward the castle walls, growing every second and filling more and more of the "
            "frame."
        ),
        son=(
            "The landslide hits the camera: mud and gravel smash across the lens, the frame "
            "floods dark brown, then dims to near black as thick wet mud covers the lens and "
            "buries it."
        ),
        son_durum=(
            "The camera is buried in the landslide. The frame is almost black, with only a "
            "faint green-brown glow through the wet mud pressed against the lens. The "
            "grinding roar of the rock is muffled and fading."
        ),
        ses=(
            ("0.0-1.5", "A sharp gasp at the height, then a held breath."),
            ("3.0-5.0", "Wet, shaky breaths inside the rain cloud."),
            ("8.0-9.0", "A short wordless scream as the mountainside tears loose."),
            ("12.5-15.0", "A long wordless scream swallowed by the roar of the mud, cut off "
                          "as the landslide buries the camera."),
        ),
        caption=(
            "You're sliding past the towers of Neuschwanstein Castle in Bavaria, then through "
            "a cloud as the mountain behind it comes down. Would you go down this one?"
        ),
        emoji="\U0001F3F0\U0001F327️", etiket="#Neuschwanstein",
        basliklar=(
            "Neuschwanstein landslide drop #shorts",
            "Neuschwanstein, then the mountain falls #shorts",
            "Neuschwanstein in a river of mud #shorts",
        ),
    ),
    "londra-bigben-yildirim": dict(
        sehir="London", landmark="Big Ben", neon="electric amber",
        palet="neon", anahtar="Big Ben", isik="mor-tabela",
        hava="a bright clear summer evening over the Thames, the sky soft blue",
        felaket="a violet lightning supercell over Westminster",
        ilk_kare=(
            "Far below and ahead, filling the upper half of the frame: Big Ben seen from the "
            "FRONT, from across the river Thames, on a bright clear summer evening, the tall "
            "golden stone clock tower with its pointed green and gold spire, its clock face "
            "toward the camera and reading correctly, never mirrored. It stands at the end of "
            "the long gothic Houses of Parliament, which stretch away to its left along the "
            "water, and Westminster Bridge crosses the river at its foot. A thick white cloud "
            "bank lies across the river below the slide, and the slide dives down toward it."
        ),
        acilis=(
            "Big Ben fills the centre of the frame, the great clock face toward the camera "
            "with its black hands, the carved golden stone of the tower glowing in the "
            "evening sun. The slide drops past the gilded spire on top of the tower close "
            "enough to see the gold crosses, the green iron roof tiles and the carved stone "
            "rush up and past on the right, the river and the bridge far below."
        ),
        kapi_ici=(
            "The air turns warm and electric, the murk inside the cloud flickers violet from "
            "somewhere below, and a low roll of thunder shakes the acrylic."
        ),
        ortaya=(
            "the same city under a violet supercell. A huge black storm base hangs low over "
            "Westminster, its underside flickering, and Big Ben stands dark gold beneath it "
            "with its clock faces glowing. Bolts of violet-white lightning crack down out of "
            "the cloud into the river and onto the rooftops, each flash lighting the whole "
            "Houses of Parliament for an instant. The Thames below is whipped white by the "
            "wind."
        ),
        tirmanis=(
            "A bolt strikes the spire of Big Ben right beside the slide and blasts sparks "
            "into the air, the flash burning the frame white for an instant, and the clock "
            "faces go dark. Thunder shakes the slide, rain and hail rattle across the clear "
            "floor under her feet, and the gust front tears across the river, stripping the "
            "trees on the embankment and throwing spray over the bridge."
        ),
        doruk=(
            "The black core of the storm rolls down the Thames toward the slide from the left "
            "side of the frame, a towering violet-black wall of rain and hail under the low "
            "storm base, lit from inside by bolt after bolt of lightning, with torn branches, "
            "roof slates and shattered glass flying inside it, growing every second and "
            "filling more and more of the frame."
        ),
        son=(
            "The storm wall slams into the camera: rain and hail blast across the lens, the "
            "frame floods violet-white under one last lightning flash, then dims to near "
            "black as water and ice cover the lens."
        ),
        son_durum=(
            "The camera is inside the black core of the storm. The frame is almost black, "
            "with only a faint violet flicker of lightning through the water and ice "
            "streaming over the lens. The crash of the thunder is muffled and fading."
        ),
        ses=(
            ("0.0-1.5", "A sharp gasp at the height, then a held breath."),
            ("3.0-5.0", "Tight, shallow breathing in the flickering cloud."),
            ("7.6-8.6", "A short wordless scream as the lightning hits the tower."),
            ("12.5-15.0", "A long wordless scream drowned by the thunder, cut off as the "
                          "storm swallows the camera."),
        ),
        caption=(
            "You're sliding past the clock of Big Ben in London, then through a cloud into a "
            "violet lightning storm. Would you go through it?"
        ),
        emoji="\U0001F570️⚡", etiket="#BigBen",
        basliklar=(
            "Big Ben struck by lightning #shorts",
            "Big Ben drop into a violet storm #shorts",
            "Big Ben under a violet sky #shorts",
        ),
    ),
}


# Eski kayis cizelgesinin kirilma noktalari -> yuruyuslu cizelgedeki karsiliklari.
# Kayis 0.0'da degil 2.0'da baslar; aradaki her an dogrusal tasinir.
YURUYUS_HARITASI = (
    (0.0, 2.0), (2.5, 4.0), (5.0, 6.0), (7.5, 8.5), (10.0, 10.5), (12.5, 13.0), (15.0, 15.0),
)
YURUYUS_SESI = ("0.0-1.8", "Quick nervous breathing in time with her bare footsteps on the glass.")


def yuruyus_zamani(eski: float) -> float:
    """Eski 0-15 kayis cizelgesindeki bir ani yuruyuslu cizelgeye tasir."""
    for (e0, y0), (e1, y1) in zip(YURUYUS_HARITASI, YURUYUS_HARITASI[1:]):
        if e0 <= eski <= e1:
            return round(y0 + (eski - e0) * (y1 - y0) / (e1 - e0), 1)
    raise ValueError("zaman 0-15 disinda: %s" % eski)


def yuruyus_sesleri(ses: tuple) -> list[tuple[str, str]]:
    tasinan = [YURUYUS_SESI]
    for zaman, metin in ses:
        bas, bit = (float(parca) for parca in zaman.split("-"))
        tasinan.append(("%.1f-%.1f" % (yuruyus_zamani(bas), yuruyus_zamani(bit)), metin))
    return tasinan


def rota_metni(slug: str, r: dict) -> str:
    """Bir rotanin tam markdown metni. Iskelet sabit, degisken yalniz r."""
    neon = r["neon"]
    acilis_durumu = (
        "The rider is already walking briskly, barefoot and mid-stride, along a narrow "
        "walkway of clear glass high above %s in %s, a few steps from the open mouth of the "
        "transparent slide. %s Her two separate bare legs and bare feet step forward in the "
        "lower half of the frame, wet and shining, and just ahead the two %s rims of the "
        "slide mouth run away and down toward the cloud below. There is no railing. The "
        "weather is %s."
        % (r["landmark"], r["sehir"], r["ilk_kare"], neon, r["hava"])
    )
    beats = [
        ("0.0-2.0",
         "From the very first moment the rider is already walking briskly barefoot along the "
         "narrow glass walkway toward the slide, left foot, right foot, never stopping. "
         "Through the clear glass under her feet there is only empty air and the land far "
         "below. The open mouth of the slide grows with every step, its two %s rims curving "
         "away and down toward the cloud, and %s waits far below and ahead beyond it. She "
         "never stands still and never hesitates." % (neon, r["landmark"])),
        ("2.0-4.0",
         "She reaches the mouth, sits straight down into it feet first and pushes off, and the "
         "slide takes her at once into the steep plunge. "
         + r["acilis"] + " Below, the white sea of cloud rushes up toward her and the slide "
         "dives straight into it."),
        ("4.0-6.0",
         "The slide plunges into the cloud. The frame becomes an even, flat grey-white murk; "
         "only her two legs, both feet and the two %s rims stay readable. " % neon
         + r["kapi_ici"]),
        ("6.0-8.5",
         "She drops out of the underside of the cloud into " + r["ortaya"]),
        ("8.5-10.5", r["tirmanis"]),
        ("10.5-13.0", r["doruk"]),
        ("13.0-15.0",
         "The slide runs straight into it, both legs and both feet still separately visible "
         "and the two %s rims still burning. " % neon + r["son"]),
    ]
    ses = "\n".join("[%s] %s" % (zaman, metin) for zaman, metin in yuruyus_sesleri(r["ses"]))
    caption = "%s %s\n\n#MegaSlideFear %s %s" % (
        r["caption"], r["emoji"], r["etiket"], SABIT_ETIKETLER)
    return "\n".join([
        "# ROUTE",
        "",
        "SLUG: %s" % slug,
        "KONSEPT: kapi",
        "DESTINATION: %s" % r["sehir"],
        "LANDMARK: %s" % r["landmark"],
        "DURATION: 15",
        "NEON: %s" % neon,
        "PALET: %s" % r["palet"],
        "TITLE_KEYWORD: %s" % r["anahtar"],
        "SEHIR_ISIGI: %s" % r["isik"],
        "LEGWEAR: %s" % LEGWEAR,
        "WEATHER: %s" % r["hava"],
        "FELAKET: %s" % r["felaket"],
        "SOURCE: tools/kapi_ekle.py ile uretildi; mevsim kapisi A (2026-10-01) iskeleti, "
        "yuruyus acilisi (2026-10-09)",
        "",
        "## ILK KARE",
        "",
        r["ilk_kare"],
        "",
        "## OPENING STATE",
        "",
        acilis_durumu,
        "",
        "## BEATS",
        "",
        "\n\n".join("[%s] %s" % (zaman, metin) for zaman, metin in beats),
        "",
        "## END STATE",
        "",
        r["son_durum"],
        "",
        "## VOICE",
        "",
        ses,
        "",
        "## CAPTION",
        "",
        caption,
        "",
        "## TITLE",
        "",
        "\n".join(r["basliklar"]),
        "",
    ])


def yaz(slug: str) -> Path:
    hedef = KOK / "routes" / (slug + ".md")
    hedef.write_text(rota_metni(slug, ROTALAR[slug]), encoding="utf-8", newline="\n")
    return hedef


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", nargs="?")
    ap.add_argument("--hepsi", action="store_true")
    ap.add_argument("--liste", action="store_true")
    args = ap.parse_args(argv)
    if args.liste:
        for slug in ROTALAR:
            print(slug)
        return 0
    hedefler = list(ROTALAR) if args.hepsi else [args.slug] if args.slug else []
    if not hedefler:
        ap.error("slug ya da --hepsi ver")
    for slug in hedefler:
        if slug not in ROTALAR:
            print("bilinmeyen rota: %s" % slug, file=sys.stderr)
            return 1
        print("yazildi: %s" % yaz(slug))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
