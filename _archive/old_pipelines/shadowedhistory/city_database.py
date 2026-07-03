"""
ShadowedHistory — City & Location Database (v1)

Comprehensive database of historical cities, lost civilizations, and
mysterious locations optimized for viral YouTube Shorts content.

Each entry includes:
  - name: City/location name
  - location: Modern-day country/region
  - era: Historical period
  - hook: Viral-optimized one-liner
  - visual_style: Key visual elements for AI generation
  - category: Content category for scene sequence matching
"""

# ─── LOST & ABANDONED CITIES ──────────────────────────────────────────────────
# Our #1 viral category! North Brother Island got 4.3K views

LOST_CITIES = [
    {
        "name": "Pripyat",
        "location": "Ukraine",
        "era": "1970-1986",
        "hook": "50,000 people evacuated in 3 HOURS — this city has been frozen in time since 1986",
        "visual_style": "abandoned Soviet apartment blocks, overgrown amusement park, Ferris wheel in fog, nature reclaiming concrete",
        "category": "lost_city",
    },
    {
        "name": "Pompeii",
        "location": "Italy",
        "era": "79 AD",
        "hook": "A city FROZEN in the moment of death — people preserved mid-scream for 2,000 years",
        "visual_style": "volcanic ash-covered streets, plaster casts of victims, Roman frescoes, Mount Vesuvius looming",
        "category": "disaster",
    },
    {
        "name": "Angkor Wat",
        "location": "Cambodia",
        "era": "12th century",
        "hook": "The LARGEST temple on Earth was swallowed by jungle for 400 years — a French explorer found it in 1860",
        "visual_style": "massive stone temples, tree roots engulfing walls, morning mist, intricate bas-reliefs, jungle canopy",
        "category": "lost_city",
    },
    {
        "name": "Machu Picchu",
        "location": "Peru",
        "era": "15th century",
        "hook": "The Incas ABANDONED their cloud city at 7,970 feet — the Spanish never found it. Nobody knows why they left",
        "visual_style": "mountain-top terraces, Andes peaks, morning clouds below, precise stone masonry, llamas",
        "category": "lost_city",
    },
    {
        "name": "Petra",
        "location": "Jordan",
        "era": "4th century BC",
        "hook": "A city carved INSIDE mountains — hidden for 1,000 years until a Swiss explorer tricked his way in",
        "visual_style": "rose-red sandstone facades, narrow Siq canyon, Treasury building at golden hour, torch-lit interiors",
        "category": "lost_city",
    },
    {
        "name": "Cahokia",
        "location": "Illinois, USA",
        "era": "1050-1350 AD",
        "hook": "America's FORGOTTEN pyramid city was bigger than London in 1100 AD — then everyone vanished",
        "visual_style": "massive earthen mounds, wooden palisades, Mississippi River, ceremonial plaza, sunrise alignment",
        "category": "lost_city",
    },
    {
        "name": "Derinkuyu",
        "location": "Cappadocia, Turkey",
        "era": "8th century BC",
        "hook": "An underground city for 20,000 people was hidden beneath Turkey for CENTURIES — 18 stories deep",
        "visual_style": "carved tunnels, underground chambers, ventilation shafts, stone doors, candlelit passages",
        "category": "engineering",
    },
    {
        "name": "Teotihuacan",
        "location": "Mexico",
        "era": "100 BC - 550 AD",
        "hook": "The Aztecs found this MASSIVE city already abandoned — they thought GODS built it. We still don't know who did",
        "visual_style": "Pyramid of the Sun, Avenue of the Dead, obsidian masks, murals, vast plaza at sunset",
        "category": "mystery",
    },
    {
        "name": "Great Zimbabwe",
        "location": "Zimbabwe",
        "era": "11th-15th century",
        "hook": "European colonizers REFUSED to believe Africans built this. The stone city that rewrote history",
        "visual_style": "massive granite walls without mortar, conical tower, hilltop enclosure, African savanna backdrop",
        "category": "lost_city",
    },
    {
        "name": "Mohenjo-daro",
        "location": "Pakistan",
        "era": "2500 BC",
        "hook": "This 4,500-year-old city had BETTER plumbing than most of medieval Europe — then it vanished overnight",
        "visual_style": "grid-pattern streets, Great Bath, brick buildings, Indus River, ancient drainage systems",
        "category": "mystery",
    },
    {
        "name": "Palmyra",
        "location": "Syria",
        "era": "1st-3rd century AD",
        "hook": "Rome built a PARADISE in the Syrian desert — a crossroads city of 200,000 destroyed twice: once by Rome, once by ISIS",
        "visual_style": "Roman colonnades in desert, Temple of Baal, golden sandstone, dramatic desert sunset",
        "category": "lost_city",
    },
    {
        "name": "Hashima Island (Gunkanjima)",
        "location": "Japan",
        "era": "1887-1974",
        "hook": "The most DENSELY populated place on Earth — abandoned overnight. Now a concrete ghost island",
        "visual_style": "concrete apartment blocks on tiny island, crumbling stairways, ocean waves crashing, eerie silence",
        "category": "lost_city",
    },
    {
        "name": "Centralia",
        "location": "Pennsylvania, USA",
        "era": "1962-present",
        "hook": "An underground fire has been burning beneath this town for 60+ YEARS — smoke still rises from cracks",
        "visual_style": "cracked roads with steam, abandoned houses, barren landscape, eerie fog, warning signs",
        "category": "disaster",
    },
    {
        "name": "Varosha",
        "location": "Famagusta, Cyprus",
        "era": "1974-present",
        "hook": "A luxury beach resort FROZEN in 1974 — hotels still have suitcases in rooms, cars in garages",
        "visual_style": "crumbling high-rise hotels, empty beach, rusting cars, fenced perimeter, Mediterranean sun",
        "category": "lost_city",
    },
    {
        "name": "Nan Madol",
        "location": "Micronesia",
        "era": "8th-13th century",
        "hook": "A city built on WATER in the middle of the Pacific — 92 artificial islands connected by canals. How?",
        "visual_style": "basalt log walls rising from lagoon, tropical vegetation, coral reefs, mysterious stone structures",
        "category": "mystery",
    },
]

# ─── ANCIENT EMPIRE CAPITALS ──────────────────────────────────────────────────

EMPIRE_CAPITALS = [
    {
        "name": "Constantinople",
        "location": "Istanbul, Turkey",
        "era": "330-1453 AD",
        "hook": "The city that was the CAPITAL of the world for 1,100 years — it fell in a single day",
        "visual_style": "Hagia Sophia, Theodosian Walls, Golden Horn, Ottoman cannons, Byzantine mosaics",
        "category": "empire",
    },
    {
        "name": "Babylon",
        "location": "Iraq",
        "era": "1894-539 BC",
        "hook": "The Hanging Gardens, the Tower of Babel, the Ishtar Gate — this city was the CENTER of the ancient world",
        "visual_style": "Ishtar Gate blue tiles, ziggurat, Euphrates River, lush gardens, golden statues",
        "category": "legend",
    },
    {
        "name": "Rome",
        "location": "Italy",
        "era": "753 BC - 476 AD",
        "hook": "An empire that lasted 1,200 YEARS and ruled 70 million people — destroyed from the inside",
        "visual_style": "Colosseum, Roman Forum, aqueducts, legionnaire formations, marble temples at sunset",
        "category": "empire",
    },
    {
        "name": "Persepolis",
        "location": "Iran",
        "era": "515-330 BC",
        "hook": "Alexander the Great BURNED the most magnificent city on Earth in a single drunken night of revenge",
        "visual_style": "massive stone columns, bull capitals, grand staircase, fire and destruction, Persian guards",
        "category": "warfare",
    },
    {
        "name": "Carthage",
        "location": "Tunisia",
        "era": "814-146 BC",
        "hook": "Rome was so AFRAID of this city they destroyed it completely and salted the earth so nothing would grow",
        "visual_style": "harbor with war ships, Tophet sanctuary, burning city, Roman siege, Mediterranean coast",
        "category": "warfare",
    },
    {
        "name": "Tenochtitlan",
        "location": "Mexico City, Mexico",
        "era": "1325-1521",
        "hook": "The Aztec capital was built on a LAKE — bigger than any European city. The Spanish buried it under Mexico City",
        "visual_style": "island city with causeways, Templo Mayor, floating gardens, eagle warriors, lake reflections",
        "category": "empire",
    },
    {
        "name": "Memphis",
        "location": "Egypt",
        "era": "3100-332 BC",
        "hook": "The FIRST capital of unified Egypt ruled for 3,000 years — now completely buried under farmland",
        "visual_style": "colossal Ramesses statue, palm groves, Nile floodplain, Step Pyramid in distance, ancient temples",
        "category": "lost_city",
    },
    {
        "name": "Cusco",
        "location": "Peru",
        "era": "13th-16th century",
        "hook": "The Inca capital's walls fit so PERFECTLY that a knife blade can't pass between stones — no mortar, no tools we understand",
        "visual_style": "precisely fitted stone walls, Sacsayhuaman fortress, Andes mountains, golden temples, terraced hills",
        "category": "engineering",
    },
    {
        "name": "Nineveh",
        "location": "Mosul, Iraq",
        "era": "7th century BC",
        "hook": "The LARGEST city in the world for 50 years — the Assyrian capital that terrorized the ancient world",
        "visual_style": "massive walls, lamassu gate guardians, royal palace, library of Ashurbanipal, cuneiform tablets",
        "category": "empire",
    },
    {
        "name": "Chang'an (Xi'an)",
        "location": "China",
        "era": "202 BC - 904 AD",
        "hook": "The eastern end of the Silk Road — a city of ONE MILLION people when London had 15,000",
        "visual_style": "Tang Dynasty pagodas, city walls, Silk Road caravans, terracotta warriors nearby, bustling markets",
        "category": "empire",
    },
    {
        "name": "Samarkand",
        "location": "Uzbekistan",
        "era": "7th century BC - present",
        "hook": "Tamerlane made this city the CENTER of the world — he brought craftsmen from every conquered nation to build it",
        "visual_style": "turquoise domes, Registan Square, intricate tilework, Silk Road oasis, desert sunset",
        "category": "empire",
    },
    {
        "name": "Karakorum",
        "location": "Mongolia",
        "era": "1220-1260",
        "hook": "The capital of the LARGEST empire in history — Genghis Khan's city. Now there's almost nothing left",
        "visual_style": "vast Mongolian steppe, yurt camps, stone turtle monuments, trade caravans, snow-capped mountains",
        "category": "empire",
    },
]

# ─── MYSTERIOUS & SACRED SITES ────────────────────────────────────────────────

MYSTERIOUS_SITES = [
    {
        "name": "Göbekli Tepe",
        "location": "Turkey",
        "era": "9500 BC",
        "hook": "Built 6,000 years BEFORE Stonehenge — the oldest temple on Earth was deliberately BURIED. Why?",
        "visual_style": "T-shaped pillars with animal carvings, circular enclosures, Turkish highlands, archaeological excavation",
        "category": "mystery",
    },
    {
        "name": "Stonehenge",
        "location": "England",
        "era": "3000-2000 BC",
        "hook": "The stones were transported 150 MILES — some weigh 25 tons. Nobody knows exactly how or why",
        "visual_style": "stone circle at sunrise, Salisbury Plain, solstice light alignment, dramatic sky, ancient landscape",
        "category": "mystery",
    },
    {
        "name": "Easter Island (Rapa Nui)",
        "location": "Chile",
        "era": "1250-1500 AD",
        "hook": "887 giant stone heads on a tiny island — the civilization that DESTROYED itself building them",
        "visual_style": "Moai statues at sunset, volcanic landscape, Pacific Ocean, quarry at Rano Raraku, grassy hills",
        "category": "mystery",
    },
    {
        "name": "Baalbek",
        "location": "Lebanon",
        "era": "9000 BC - 1st century AD",
        "hook": "These stone blocks weigh 1,000 TONS each — even modern cranes can't lift them. How did the ancients do it?",
        "visual_style": "colossal Roman temple columns, impossibly large stone blocks, Bekaa Valley, dramatic scale comparison",
        "category": "engineering",
    },
    {
        "name": "Newgrange",
        "location": "Ireland",
        "era": "3200 BC",
        "hook": "Older than the Pyramids — for 17 minutes on the winter solstice, sunlight penetrates a 60-foot passage PERFECTLY",
        "visual_style": "spiral-carved entrance stone, mound structure, sunlight beam in passage, Irish green landscape, dawn",
        "category": "mystery",
    },
    {
        "name": "Nazca Lines",
        "location": "Peru",
        "era": "500 BC - 500 AD",
        "hook": "Massive drawings carved into the desert — only visible from ABOVE. Some are 1,200 feet long. Who were they for?",
        "visual_style": "aerial view of geoglyphs, hummingbird/spider/monkey shapes, desert plateau, mysterious lines",
        "category": "mystery",
    },
    {
        "name": "Ellora Caves",
        "location": "India",
        "era": "600-1000 AD",
        "hook": "A temple carved from a SINGLE rock from top to bottom — they removed 200,000 TONS of stone by hand",
        "visual_style": "monolithic Kailasa temple, intricate carvings, elephant sculptures, dramatic cliff face, torchlight",
        "category": "engineering",
    },
    {
        "name": "Sigiriya",
        "location": "Sri Lanka",
        "era": "5th century AD",
        "hook": "A palace built on top of a 660-foot ROCK — by a king who murdered his father and feared his brother's revenge",
        "visual_style": "massive rock fortress, lion's paw entrance, frescoes, mirror wall, jungle surroundings, aerial view",
        "category": "engineering",
    },
    {
        "name": "Skellig Michael",
        "location": "Ireland",
        "era": "6th-8th century",
        "hook": "Monks lived on this IMPOSSIBLE rock island for 600 years — 600 stairs up a cliff in the Atlantic Ocean",
        "visual_style": "beehive stone huts on cliff, Atlantic waves crashing, steep stone stairs, puffins, dramatic sky",
        "category": "mystery",
    },
    {
        "name": "Timbuktu",
        "location": "Mali",
        "era": "12th-16th century",
        "hook": "The city of GOLD and knowledge — 700,000 manuscripts, one of the world's first universities. Europeans thought it was a myth",
        "visual_style": "Djinguereber Mosque, mud-brick architecture, ancient manuscripts, Sahara Desert edge, caravan routes",
        "category": "lost_city",
    },
]

# ─── UNDERWATER & SUNKEN CITIES ───────────────────────────────────────────────

UNDERWATER_CITIES = [
    {
        "name": "Dwarka",
        "location": "India (underwater)",
        "era": "15,000-9,000 BC (disputed)",
        "hook": "The city of LORD KRISHNA found underwater — structures 9,000 years old that shouldn't exist",
        "visual_style": "underwater stone structures, coral-covered walls, diver with flashlight, murky blue depths",
        "category": "mystery",
    },
    {
        "name": "Port Royal",
        "location": "Jamaica",
        "era": "1692",
        "hook": "The WICKEDEST city on Earth — swallowed by the sea in an earthquake. 2,000 dead in 2 minutes",
        "visual_style": "sunken pirate port, underwater buildings, Caribbean waters, treasure chests, coral growth",
        "category": "disaster",
    },
    {
        "name": "Heracleion (Thonis)",
        "location": "Egypt (underwater)",
        "era": "8th century BC - 8th century AD",
        "hook": "A massive Egyptian port city was LOST for 1,200 years — found underwater with giant statues still standing",
        "visual_style": "underwater colossal statues, sunken temples, diver illuminating artifacts, Mediterranean seabed",
        "category": "discovery",
    },
    {
        "name": "Pavlopetri",
        "location": "Greece (underwater)",
        "era": "3500-1100 BC",
        "hook": "The world's OLDEST underwater city — 5,000 years old with streets, buildings, and tombs still intact",
        "visual_style": "underwater ruins visible from surface, clear Mediterranean water, stone foundations, Greek coast",
        "category": "discovery",
    },
    {
        "name": "Shi Cheng (Lion City)",
        "location": "China (underwater)",
        "era": "25-200 AD, flooded 1959",
        "hook": "China deliberately DROWNED this 1,300-year-old city to build a dam — it's perfectly preserved underwater",
        "visual_style": "underwater Chinese architecture, carved stone dragons, diving lights, clear lake water, pagoda tops",
        "category": "lost_city",
    },
]

# ─── FORTRESS & MILITARY CITIES ───────────────────────────────────────────────

FORTRESS_CITIES = [
    {
        "name": "Masada",
        "location": "Israel",
        "era": "1st century AD",
        "hook": "960 Jewish rebels chose DEATH over surrender — they drew lots and killed each other on this cliff fortress",
        "visual_style": "cliff-top fortress, Dead Sea below, Roman siege ramp, desert landscape, dramatic sunrise",
        "category": "warfare",
    },
    {
        "name": "Krak des Chevaliers",
        "location": "Syria",
        "era": "1142-1271",
        "hook": "The most PERFECT medieval castle ever built — Crusader knights held it for 129 years against impossible odds",
        "visual_style": "concentric castle walls, Syrian hills, massive towers, inner courtyard, dramatic storm clouds",
        "category": "warfare",
    },
    {
        "name": "Troy",
        "location": "Turkey",
        "era": "3000-500 BC",
        "hook": "Everyone said it was MYTH — then we dug it up. 9 cities built on top of each other. The Trojan War was REAL",
        "visual_style": "layered archaeological ruins, wooden horse reconstruction, Aegean coast, ancient walls, battle scene",
        "category": "discovery",
    },
    {
        "name": "Alamut Castle",
        "location": "Iran",
        "era": "1090-1256",
        "hook": "The fortress of the ASSASSINS — built on an impossible cliff. Hassan-i Sabbah's warriors changed history from here",
        "visual_style": "cliff-top castle ruins, Alborz Mountains, misty valleys, narrow mountain paths, eagle's nest position",
        "category": "warfare",
    },
    {
        "name": "Malbork Castle",
        "location": "Poland",
        "era": "1274-present",
        "hook": "The LARGEST castle ever built — by the Teutonic Knights. 52 acres of medieval fortress. Still standing",
        "visual_style": "massive red brick castle, Nogat River, Gothic architecture, vast courtyards, winter snowfall",
        "category": "engineering",
    },
]

# ─── CURSED & DARK HISTORY LOCATIONS ──────────────────────────────────────────

DARK_LOCATIONS = [
    {
        "name": "Aokigahara Forest",
        "location": "Japan",
        "era": "modern",
        "hook": "Japan's SEA OF TREES at the base of Mount Fuji — so dense that compasses stop working inside",
        "visual_style": "dense twisted trees, volcanic rock floor, moss-covered roots, eerie mist, filtered green light",
        "category": "dark_history",
    },
    {
        "name": "Catacombs of Paris",
        "location": "France",
        "era": "1786-present",
        "hook": "The bones of 6 MILLION people line the tunnels beneath Paris — moved there when cemeteries overflowed",
        "visual_style": "walls of stacked skulls and bones, underground tunnels, dim lighting, stone archways, eerie atmosphere",
        "category": "dark_history",
    },
    {
        "name": "Poveglia Island",
        "location": "Italy",
        "era": "1776-1968",
        "hook": "Plague victims, then an insane asylum with a MAD doctor — Italy's most haunted island is BANNED from visitors",
        "visual_style": "abandoned asylum buildings, overgrown island, Venetian lagoon, crumbling walls, foggy atmosphere",
        "category": "dark_history",
    },
    {
        "name": "Cappadocia Underground Cities",
        "location": "Turkey",
        "era": "8th-7th century BC",
        "hook": "36 underground cities connected by TUNNELS — entire civilizations lived beneath the earth to survive invasions",
        "visual_style": "fairy chimney landscape above, carved underground rooms, stone rolling doors, ventilation shafts",
        "category": "engineering",
    },
    {
        "name": "The Door to Hell (Darvaza)",
        "location": "Turkmenistan",
        "era": "1971-present",
        "hook": "Soviet scientists lit a gas crater on fire expecting it to burn out in weeks — it's been burning for 50+ YEARS",
        "visual_style": "massive flaming crater at night, desert landscape, orange glow against dark sky, heat distortion",
        "category": "disaster",
    },
]


# ─── Helper: Flatten all cities into topic format ─────────────────────────────

ALL_CITY_COLLECTIONS = [
    ("lost_city", LOST_CITIES),
    ("empire_capital", EMPIRE_CAPITALS),
    ("mysterious_site", MYSTERIOUS_SITES),
    ("underwater_city", UNDERWATER_CITIES),
    ("fortress_city", FORTRESS_CITIES),
    ("dark_location", DARK_LOCATIONS),
]


def get_all_cities() -> list[dict]:
    """Get flat list of all city entries."""
    cities = []
    for collection_name, collection in ALL_CITY_COLLECTIONS:
        for city in collection:
            cities.append({
                **city,
                "collection": collection_name,
            })
    return cities


def get_city_topic_string(city: dict) -> str:
    """Convert a city dict into a topic string for the pipeline."""
    return (
        f"{city['hook']} "
        f"[LOCATION: {city['name']}, {city['location']}] "
        f"[ERA: {city['era']}] "
        f"[VISUAL: {city['visual_style']}]"
    )


def get_cities_by_category(category: str) -> list[dict]:
    """Get cities filtered by category."""
    return [c for c in get_all_cities() if c.get("category") == category]


def get_random_city(exclude_names: list[str] = None) -> dict | None:
    """Get a random city, optionally excluding already-used ones."""
    import random
    cities = get_all_cities()
    if exclude_names:
        cities = [c for c in cities if c["name"] not in exclude_names]
    return random.choice(cities) if cities else None
