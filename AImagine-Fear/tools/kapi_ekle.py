"""KAPI konseptinin rota dosyalarini veriden uretir.

Neden var: sehir_ekle.py ile ayni sebep. Govde iskeleti (bulut kapisi, bacak ve
rim cumleleri, bitisteki kararma) her rotada AYNI olmali; rota yalniz yerini,
havasini ve felaketini getirir. Iskelet 2026-10-01 mevsim kapisi A v2'nin
(reference/ref-DdvYhkUEbxn/ornek/PROMPT_A15.txt) zaman cizelgesidir; o video
Ihsan'in sectigi format.

Rota alanlari:
  sehir, landmark, neon, palet, anahtar (TITLE_KEYWORD), isik (SEHIR_ISIGI: bu
  konseptte FELAKET dunyasinin baskin renk ailesi, renk ardisikligi kurali icin),
  hava (bulutun ustu), felaket (bulutun alti, kisa ad),
  ilk_kare  : baslangic gorselinde uzakta ne var (landmark, isik, mevsim)
  acilis    : [0.0-2.5] ilk dusus, landmark yakindan
  kapi_ici  : [2.5-5.0] bulutun icinde felaketin ilk isareti
  ortaya    : [5.0-7.5] bulutun altinda AYNI yer felaketin icinde
  tirmanis  : [7.5-10.0] felaket buyur, kaydiraga ilk darbe
  doruk     : [10.0-12.5] asil tehdit yaklasir, kareyi doldurur
  son       : [12.5-15.0] tehdit kamerayi yutar (kararma iskelette)
  son_durum : END STATE
  ses       : VOICE icin kelimesiz uc an (kendi zamanlariyla)
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
}


def rota_metni(slug: str, r: dict) -> str:
    """Bir rotanin tam markdown metni. Iskelet sabit, degisken yalniz r."""
    neon = r["neon"]
    acilis_durumu = (
        "The rider is already sliding fast, feet first, at the top of a steep plunge on the "
        "transparent slide high above %s in %s. %s Her two separate bare legs and bare feet "
        "fill the lower half of the frame, wet and shining, the two %s rims converging ahead "
        "toward the cloud below. The weather is %s."
        % (r["landmark"], r["sehir"], r["ilk_kare"], neon, r["hava"])
    )
    beats = [
        ("0.0-2.5",
         "From the very first moment the rider is already dropping fast down the steep plunge. "
         + r["acilis"] + " Below, the white sea of cloud rushes up toward her and the slide "
         "dives straight into it."),
        ("2.5-5.0",
         "The slide plunges into the cloud. The frame becomes an even, flat grey-white murk; "
         "only her two legs, both feet and the two %s rims stay readable. " % neon
         + r["kapi_ici"]),
        ("5.0-7.5",
         "She drops out of the underside of the cloud into " + r["ortaya"]),
        ("7.5-10.0", r["tirmanis"]),
        ("10.0-12.5", r["doruk"]),
        ("12.5-15.0",
         "The slide runs straight into it, both legs and both feet still separately visible "
         "and the two %s rims still burning. " % neon + r["son"]),
    ]
    ses = "\n".join("[%s] %s" % (zaman, metin) for zaman, metin in r["ses"])
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
        "SOURCE: tools/kapi_ekle.py ile uretildi; mevsim kapisi A (2026-10-01) iskeleti",
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
