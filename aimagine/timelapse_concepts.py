"""
AImagine — Build & Reveal Concepts (BuildCraft Style)

Inspired by @buildcraft.official (427K followers).
Format: Exterior Build → Enter Inside → Luxury Interior Reveal.

4 frames (2 exterior + 2 interior) → 3 video clips → ~24s.
Cost: ~128 credits ($0.64) per video.
"""

import random
from datetime import date

# ─── Shared constants ─────────────────────────────────────────────────────────
# Inspired by @structural.vibes — close-up workers + sped-up timelapse feel

AERIAL = "photorealistic aerial drone photograph, 45-degree angle, DJI Mavic 3 Pro"
INTERIOR = "photorealistic wide-angle interior photograph, natural light, 9:16 vertical"
CINEMATIC = "cinematic smooth camera movement, photorealistic, 9:16 vertical"
STYLE = "hyper-realistic, 8K detail, natural lighting, architectural photography"

# Worker realism — makes AI construction look authentic (structural.vibes style)
WORKERS = (
    "Multiple construction workers visible — wearing hard hats, high-vis vests, work boots. "
    "Close-up of hands working: laying bricks, pouring concrete, welding steel, tying rebar. "
    "Workers are physically building — NOT posing, NOT standing still. "
    "Looks like a sped-up timelapse of real construction footage. "
    "Natural imperfections: slightly uneven concrete, dust in the air, tool marks visible. "
    "Construction debris, scaffolding, wheelbarrows, hand tools scattered realistically."
)

TIMELAPSE_MOTION = (
    "Sped-up timelapse effect — workers move quickly like 10x fast-forward. "
    "Clouds racing across sky, shadows moving fast on ground. "
    "Construction progresses visibly between each moment. "
    "Slight motion blur on fast-moving workers adds to timelapse authenticity."
)

TIMELAPSE_CONCEPTS = [
    # 1
    {
        "name": "Boeing 747 Underground Mansion",
        "hook": "They buried a BOEING 747 and built a mansion inside! ✈️🏠",
        "title": "Boeing 747 → Underground LUXURY Mansion! ✈️",
        "description": "A decommissioned Boeing 747 lowered into a massive excavation and converted into an underground luxury mansion with infinity pool!",
        "hashtags": "#shorts #boeing747 #mansion #underground #luxury #architecture #ai",
        "frame_prompts": [
            f"{AERIAL}. Massive Boeing 747 fuselage being lowered by giant cranes into deep excavation pit. Construction workers, dirt piles, dramatic scale. Green countryside surrounds. {STYLE}",
            f"{AERIAL}. Completed Boeing 747 mansion from above — fuselage half buried, landscaped garden on top, infinity pool extending from cockpit area. Solar panels on wings. Modern entrance. {STYLE}",
            f"{INTERIOR}. Inside the Boeing 747 fuselage converted to luxury living room. Curved ceiling with warm wood paneling following fuselage shape. Floor-to-ceiling windows cut in hull. Designer furniture, fireplace. {STYLE}",
            f"{INTERIOR}. Master bedroom inside Boeing 747 tail section. Panoramic curved windows, king bed, ambient lighting along curved walls. Luxury bathroom visible through glass partition. {STYLE}",
        ],
        "video_prompts": [
            f"{CINEMATIC}. Slow aerial orbit around completed Boeing 747 mansion. Pool sparkles, garden lush, fuselage half-buried. Golden hour. 8 seconds.",
            f"{CINEMATIC}. Walking through modern entrance door into the fuselage. Camera reveals the curved luxury interior. Light floods through hull windows. 8 seconds.",
            f"{CINEMATIC}. Slow interior pan through living room to bedroom. Warm wood, designer furniture, curved hull ceiling. Cozy luxury. 8 seconds.",
        ],
    },
    # 2
    {
        "name": "Cargo Ship Cliff Fortress",
        "hook": "A CARGO SHIP turned into a cliff fortress! 🚢🏔️",
        "title": "Giant Cargo Ship → Cliff FORTRESS! 🚢",
        "description": "A massive cargo ship embedded into a coastal cliff, transformed into a luxury fortress with ocean views from every room!",
        "hashtags": "#shorts #cargoship #fortress #cliff #luxury #architecture #ai",
        "frame_prompts": [
            f"{AERIAL}. Giant cargo ship being pushed into cliff face by tugboats. Massive excavation in cliff side. Construction cranes on cliff top. Ocean waves below. Dramatic engineering. {STYLE}",
            f"{AERIAL}. Completed cargo ship fortress — ship embedded in cliff, bow jutting out over ocean. Rooftop garden on ship deck. Glass observation rooms added. Helicopter pad. {STYLE}",
            f"{INTERIOR}. Luxury open-plan living area inside cargo ship hull. Double-height ceiling. Massive floor-to-ceiling ocean view windows cut in ship side. Modern kitchen island, concrete and wood. {STYLE}",
            f"{INTERIOR}. Glass-bottom infinity pool inside the ship bow, suspended over the ocean below. Loungers, tropical plants, ocean visible through transparent floor. {STYLE}",
        ],
        "video_prompts": [
            f"{CINEMATIC}. Aerial approach to cargo ship fortress in cliff. Waves crash below. Ship bow extends over ocean. Golden light. 8 seconds.",
            f"{CINEMATIC}. Walking through reinforced entrance into ship hull. Camera reveals massive double-height living space with ocean panorama. 8 seconds.",
            f"{CINEMATIC}. Slow pan from living room to glass-bottom pool. Ocean visible below. Luxury everywhere. 8 seconds.",
        ],
    },
    # 3
    {
        "name": "Shipping Container Treehouse",
        "hook": "40 SHIPPING CONTAINERS stacked into a treehouse! 📦🌲",
        "title": "40 Containers → Giant TREEHOUSE! 📦🌲",
        "description": "40 shipping containers stacked around ancient oak trees creating a multi-level luxury treehouse compound in the forest!",
        "hashtags": "#shorts #container #treehouse #forest #luxury #offgrid #architecture",
        "frame_prompts": [
            f"{AERIAL}. Crane lifting shipping containers, stacking them around massive oak trees in a forest clearing. 20 containers already placed at angles, connected by walkways. Construction chaos. {STYLE}",
            f"{AERIAL}. Completed container treehouse — 40 containers stacked organically around trees. Connected by glass walkways and steel bridges. Green roofs, solar panels. Trees grow through the structure. {STYLE}",
            f"{INTERIOR}. Inside a container converted to luxury lounge. Exposed corrugated steel walls painted white. Oak tree trunk growing through the room. Designer mid-century furniture. Warm pendant lights. {STYLE}",
            f"{INTERIOR}. Container master suite with glass floor showing forest canopy below. Freestanding bathtub by panoramic window. Trees at eye level outside. Cozy wood and white interior. {STYLE}",
        ],
        "video_prompts": [
            f"{CINEMATIC}. Drone rising up through the container treehouse structure. Containers at various angles, glass bridges connecting them. Forest canopy. 8 seconds.",
            f"{CINEMATIC}. Walking across glass bridge between containers, entering through steel door into white luxury interior. Tree trunk inside. 8 seconds.",
            f"{CINEMATIC}. Interior tour — lounge to bedroom. Glass floor, bathtub, forest views. Warm cozy lighting. 8 seconds.",
        ],
    },
    # 4
    {
        "name": "Military Tank Bunker Home",
        "hook": "He buried 5 TANKS and built a home inside! 🪖🏠",
        "title": "5 Military Tanks → Underground HOME! 🪖",
        "description": "Five decommissioned military tanks buried underground and connected by tunnels into an off-grid luxury survival bunker!",
        "hashtags": "#shorts #tank #bunker #survival #underground #luxury #offgrid",
        "frame_prompts": [
            f"{AERIAL}. Five military tanks being lowered into deep trenches by cranes. Earth movers around. Green field with excavation. Tanks positioned in a star pattern connected by tunnels. {STYLE}",
            f"{AERIAL}. Completed tank bunker from above — grass-covered mounds hide the tanks. Only turrets visible as skylights. Central courtyard with garden. Solar panels. Secret entrance. {STYLE}",
            f"{INTERIOR}. Inside a tank hull converted to modern kitchen/dining. Rounded armored walls with warm wood cladding. Turret hatch is now a skylight flooding light. Industrial-luxury design. {STYLE}",
            f"{INTERIOR}. Underground tunnel connecting two tanks — transformed into a luxury lounge corridor. LED strip lighting, concrete walls with art, wine cellar alcoves. {STYLE}",
        ],
        "video_prompts": [
            f"{CINEMATIC}. Aerial over peaceful green mounds. Only tank turrets visible. Camera descends toward hidden entrance. 8 seconds.",
            f"{CINEMATIC}. Descending stairs into bunker. Camera reveals tank hull interior — warm wood, skylight through turret, modern kitchen. 8 seconds.",
            f"{CINEMATIC}. Walking through tunnel corridor to lounge. Wine cellar, art walls, LED ambiance. Underground luxury. 8 seconds.",
        ],
    },
    # 5
    {
        "name": "Submarine Coastal Villa",
        "hook": "A SUBMARINE became a luxury coastal villa! 🛥️🏖️",
        "title": "Nuclear Submarine → Coastal VILLA! 🛥️",
        "description": "A decommissioned submarine half-submerged on a beach, converted into a luxury coastal villa with underwater viewing rooms!",
        "hashtags": "#shorts #submarine #villa #coastal #luxury #underwater #architecture",
        "frame_prompts": [
            f"{AERIAL}. Huge submarine being beached by tugboats onto white sand beach. Workers securing hull. Crane removing conning tower panels. Palm trees, turquoise water. {STYLE}",
            f"{AERIAL}. Completed submarine villa — hull on beach, conning tower has glass observation deck. Wooden deck wraps hull top. Infinity pool off the stern. Tropical garden. {STYLE}",
            f"{INTERIOR}. Inside submarine hull — curved walls with porthole windows showing ocean. Luxury open living space with curved white sofa, marble floors. Torpedo tubes are now wine storage. {STYLE}",
            f"{INTERIOR}. Underwater viewing room in submarine bow — glass panels reveal coral reef and fish. Circular seating, blue ambient light. Half below waterline. {STYLE}",
        ],
        "video_prompts": [
            f"{CINEMATIC}. Aerial orbit of submarine villa on beach. Pool sparkles at stern. Palm trees sway. Turquoise water. 8 seconds.",
            f"{CINEMATIC}. Walking through hatch entrance into curved submarine interior. Portholes show ocean. White luxury reveals. 8 seconds.",
            f"{CINEMATIC}. Moving to bow viewing room. Glass reveals underwater world. Fish swim past. Blue ambient glow. 8 seconds.",
        ],
    },
    # 6
    {
        "name": "Train Cars Mountain Lodge",
        "hook": "12 TRAIN CARS became a mountain lodge! 🚂🏔️",
        "title": "12 Train Cars → Mountain LODGE! 🚂",
        "description": "Twelve vintage train cars arranged on a mountainside, connected and converted into a luxury mountain lodge with panoramic views!",
        "hashtags": "#shorts #train #mountain #lodge #luxury #vintage #architecture",
        "frame_prompts": [
            f"{AERIAL}. Helicopter lifting vintage train cars onto mountain slope. Cars being placed on stone foundations at different levels. Alpine meadow, snow peaks behind. {STYLE}",
            f"{AERIAL}. Completed train lodge — 12 train cars arranged in terraced formation on mountainside. Glass corridors connect them. Observation deck at top car. Mountain panorama. {STYLE}",
            f"{INTERIOR}. Inside a Pullman car converted to luxury bedroom suite. Restored wood paneling, velvet drapes. Panoramic window shows mountain valley below. Four-poster bed, fireplace. {STYLE}",
            f"{INTERIOR}. Dining car restored as gourmet restaurant. Original brass fixtures polished. Candlelit tables. Mountain sunset through arched windows. {STYLE}",
        ],
        "video_prompts": [
            f"{CINEMATIC}. Drone ascending along the terraced train lodge. Cars stepping up the mountain. Snow peaks behind. 8 seconds.",
            f"{CINEMATIC}. Entering vintage train door. Camera reveals restored Pullman suite. Wood, velvet, mountain views through window. 8 seconds.",
            f"{CINEMATIC}. Walking through corridor to dining car. Brass, candles, sunset through arched windows. 8 seconds.",
        ],
    },
    # 7
    {
        "name": "Oil Rig Ocean Estate",
        "hook": "Abandoned OIL RIG → Ocean Luxury Estate! 🛢️🌊",
        "title": "Abandoned Oil Rig → LUXURY Ocean Estate! 🛢️",
        "description": "An abandoned offshore oil platform completely transformed into a floating luxury estate with pool, helipad, and underwater suites!",
        "hashtags": "#shorts #oilrig #ocean #luxury #estate #offshore #architecture",
        "frame_prompts": [
            f"{AERIAL}. Workers renovating massive offshore oil rig platform. Cranes removing old equipment. New glass structures being built on deck. Deep blue ocean all around. {STYLE}",
            f"{AERIAL}. Completed oil rig estate — platform has infinity pool, helicopter pad, glass penthouses. Lower deck has marina for boats. Lush garden on main deck. {STYLE}",
            f"{INTERIOR}. Glass penthouse on oil rig. 360-degree ocean views. Minimalist white interior, marble floors. Open kitchen with sea breeze. Sunset reflecting on water. {STYLE}",
            f"{INTERIOR}. Underwater suite below the platform waterline. Glass walls show open ocean. Schools of fish swim by. King bed faces the deep blue. Ambient underwater lighting. {STYLE}",
        ],
        "video_prompts": [
            f"{CINEMATIC}. Aerial orbit around oil rig estate at sunset. Pool glows, helipad, glass buildings on platform. Ocean endless. 8 seconds.",
            f"{CINEMATIC}. Helicopter landing, walking into glass penthouse. 360 ocean panorama reveals. White marble interior. 8 seconds.",
            f"{CINEMATIC}. Descending to underwater suite. Glass walls, fish swimming, deep blue. Luxury bed faces ocean depths. 8 seconds.",
        ],
    },
    # 8
    {
        "name": "School Bus Compound",
        "hook": "20 SCHOOL BUSES became an off-grid compound! 🚌🌿",
        "title": "20 School Buses → Off-Grid COMPOUND! 🚌",
        "description": "Twenty retired school buses arranged in a circle forming a compound with shared courtyard, pool, and luxury converted interiors!",
        "hashtags": "#shorts #schoolbus #offgrid #compound #conversion #sustainable #tiny",
        "frame_prompts": [
            f"{AERIAL}. Cranes positioning yellow school buses in a circular arrangement on rural land. Some buses already placed, others being modified. Central area being excavated for pool. {STYLE}",
            f"{AERIAL}. Completed bus compound — 20 buses in circle with shared courtyard garden and pool center. Some buses stacked double height. Green roofs, solar panels. Cozy community. {STYLE}",
            f"{INTERIOR}. Inside a school bus converted to luxury tiny home. Bus ceiling raised with dormer windows. Full kitchen with butcher block counters. Reclaimed wood throughout. Twinkle lights. {STYLE}",
            f"{INTERIOR}. Double-decker bus master bedroom on upper level. Skylight bed, wraparound windows showing countryside. Cozy blankets, reading nook. Morning light. {STYLE}",
        ],
        "video_prompts": [
            f"{CINEMATIC}. Aerial over circular bus compound. Pool sparkles in center. Solar panels, green roofs. Rural setting. 8 seconds.",
            f"{CINEMATIC}. Opening bus door, stepping into luxury tiny kitchen. Warm wood, twinkle lights reveal. 8 seconds.",
            f"{CINEMATIC}. Climbing stairs to upper bedroom. Skylight, countryside views, cozy blankets. Morning glow. 8 seconds.",
        ],
    },
    # 9
    {
        "name": "Water Tower Penthouse",
        "hook": "Abandoned WATER TOWER → Sky Penthouse! 🏠☁️",
        "title": "Old Water Tower → Sky PENTHOUSE! ☁️",
        "description": "A rusted old water tower on steel legs renovated into a stunning sky penthouse with 360-degree panoramic views!",
        "hashtags": "#shorts #watertower #penthouse #sky #panoramic #renovation #luxury",
        "frame_prompts": [
            f"{AERIAL}. Workers on scaffolding renovating rusted water tower on tall steel legs. New windows being cut into tank wall. Spiral staircase frame going up one leg. Rural setting, wide views. {STYLE}",
            f"{AERIAL}. Completed water tower penthouse — tank repainted matte black. Panoramic windows all around. Wraparound deck with string lights. Solar panel on top. Dramatic against sunset. {STYLE}",
            f"{INTERIOR}. Inside the water tower tank — circular living space with 360-degree windows. Floating kitchen island center. Polished concrete floor, minimal design. Endless sky views. {STYLE}",
            f"{INTERIOR}. Water tower bedroom level — circular room, king bed centered. Curved glass walls show sunrise. Freestanding copper bathtub by window. Cloud-level living. {STYLE}",
        ],
        "video_prompts": [
            f"{CINEMATIC}. Aerial orbit around black water tower penthouse. String lights glow. Sunset paints the sky. Rural landscape below. 8 seconds.",
            f"{CINEMATIC}. Climbing spiral staircase into tank. Door opens to 360-degree sky view living room. Jaw-dropping reveal. 8 seconds.",
            f"{CINEMATIC}. Pan from kitchen to bedroom level. Copper tub, sunrise through curved glass. Living in the clouds. 8 seconds.",
        ],
    },
    # 10
    {
        "name": "Concrete Bunker Spa Resort",
        "hook": "Cold War BUNKER → Underground Spa Resort! 🧖💎",
        "title": "Military Bunker → LUXURY Spa Resort! 🧖",
        "description": "A massive Cold War military bunker transformed into an underground luxury spa resort with hot springs, steam rooms, and crystal pools!",
        "hashtags": "#shorts #bunker #spa #luxury #underground #coldwar #resort",
        "frame_prompts": [
            f"{AERIAL}. Abandoned concrete military bunker entrance in forest clearing. Heavy blast door, guard towers. Workers clearing rubble, new ventilation being installed. {STYLE}",
            f"{AERIAL}. Completed spa resort — bunker entrance modernized with glass and stone entrance pavilion. Landscaped zen garden above. Steam rising from underground vents. Peaceful forest setting. {STYLE}",
            f"{INTERIOR}. Former weapons storage hall now turquoise mineral pool. Original concrete arched ceiling with dramatic uplighting. Natural stone edges, tropical plants. Steam wisps. {STYLE}",
            f"{INTERIOR}. Private treatment room in former command center. Concrete walls softened with warm wood panels. Massage table, candles, heated stone floor. Intimate and luxurious. {STYLE}",
        ],
        "video_prompts": [
            f"{CINEMATIC}. Aerial descending toward bunker entrance. Zen garden above, steam rises. Forest surrounds. 8 seconds.",
            f"{CINEMATIC}. Walking through blast door into renovated corridor. Light grows. Reveal: turquoise pool under concrete arches. 8 seconds.",
            f"{CINEMATIC}. Slow tour from pool to treatment room. Candles, warm wood, heated stone. Underground serenity. 8 seconds.",
        ],
    },
    # 11
    {
        "name": "Helicopter Inside Mountain",
        "hook": "A HELICOPTER hangar inside a mountain! 🚁⛰️",
        "title": "Secret Helicopter Base Inside a MOUNTAIN! 🚁",
        "description": "A secret helipad and luxury hangar carved inside a mountain with retractable roof, living quarters, and underground garage!",
        "hashtags": "#shorts #helicopter #mountain #secret #base #luxury #bunker",
        "frame_prompts": [
            f"{AERIAL}. Mountain peak with retractable roof panels opening. Helicopter ascending from inside the mountain. Construction cranes visible inside the cavern. Alpine landscape. {STYLE}",
            f"{AERIAL}. Mountain hangar — retractable roof open showing helicopter on pad inside. Glass observation windows cut into mountain face. Hidden road entrance below. {STYLE}",
            f"{INTERIOR}. Inside mountain hangar — polished concrete floor, helicopter parked. Glass wall office overlooking the pad. Luxury lounge area with mountain view through carved window. {STYLE}",
            f"{INTERIOR}. Living quarters deep inside mountain — bedroom suite carved from rock. Warm wood ceiling, natural stone walls. Aquarium wall with mountain spring water. Fireplace. {STYLE}",
        ],
        "video_prompts": [
            f"{CINEMATIC}. Aerial approach to mountain. Roof panels retract revealing helipad inside. Dramatic engineering reveal. 8 seconds.",
            f"{CINEMATIC}. Walking into mountain hangar. Helicopter parked. Glass office reveals. Mountain view through carved window. 8 seconds.",
            f"{CINEMATIC}. Deeper into mountain — bedroom suite in rock. Warm wood, aquarium wall, fireplace. Underground luxury. 8 seconds.",
        ],
    },
    # 12
    {
        "name": "Jumbo Jet Hilltop Villa",
        "hook": "An A380 on a hilltop became a VILLA! ✈️🏡",
        "title": "Airbus A380 → Hilltop Luxury VILLA! ✈️",
        "description": "An Airbus A380 superjumbo placed on a hilltop and converted into a multi-level luxury villa with pool on the wing!",
        "hashtags": "#shorts #a380 #airbus #villa #hilltop #luxury #conversion",
        "frame_prompts": [
            f"{AERIAL}. Massive Airbus A380 fuselage being transported up a hill by heavy machinery. Workers preparing foundations. Scenic coastal hilltop with ocean views. {STYLE}",
            f"{AERIAL}. Completed A380 villa on hilltop — fuselage with extended glass walls. Pool built on wing structure. Rooftop terrace on fuselage top. Ocean panorama. Landscaped garden. {STYLE}",
            f"{INTERIOR}. Upper deck of A380 converted to open-plan living. Curved ceiling 3 meters high. Full glass nose showing 180-degree ocean panorama. White marble, designer sofas. {STYLE}",
            f"{INTERIOR}. Lower deck spa level — long narrow pool along fuselage. Porthole windows show garden outside. Steam room at tail end. Mosaic tiles, warm lighting. {STYLE}",
        ],
        "video_prompts": [
            f"{CINEMATIC}. Aerial orbit around A380 on hilltop. Wing pool sparkles. Ocean behind. Sunset colors. 8 seconds.",
            f"{CINEMATIC}. Entering through first-class door. Upper deck reveals — curved ceiling, ocean through glass nose. White marble luxury. 8 seconds.",
            f"{CINEMATIC}. Descending to lower deck spa. Long pool, portholes, steam room. Fuselage luxury spa. 8 seconds.",
        ],
    },
    # 13
    {
        "name": "Grain Silo Loft Complex",
        "hook": "6 GRAIN SILOS → Luxury Loft Complex! 🌾🏢",
        "title": "Abandoned Silos → LUXURY Loft Complex! 🌾",
        "description": "Six abandoned grain silos connected and converted into a luxury loft complex with cylindrical rooms, sky bridges, and rooftop gardens!",
        "hashtags": "#shorts #silo #loft #luxury #conversion #industrial #architecture",
        "frame_prompts": [
            f"{AERIAL}. Six tall grain silos being renovated. Workers cutting windows. Glass sky bridges connecting silos at different levels. Scaffolding on concrete cylinders. Farmland surrounds. {STYLE}",
            f"{AERIAL}. Completed silo complex — six cylinders with floor-to-ceiling windows at various levels. Glass bridges connect them. Green rooftop gardens on each. Warm lights glowing from inside. {STYLE}",
            f"{INTERIOR}. Inside a silo — cylindrical living room, curved walls with exposed concrete. Spiral staircase center. Double-height curved windows. Industrial-luxury furniture. {STYLE}",
            f"{INTERIOR}. Sky bridge between silos — glass floor and walls. Outdoor lounge furniture. Stars visible through glass ceiling at night. Warm lighting. {STYLE}",
        ],
        "video_prompts": [
            f"{CINEMATIC}. Aerial rising between the six silos. Bridges connect them. Rooftop gardens green. Warm interior glow. 8 seconds.",
            f"{CINEMATIC}. Entering silo through industrial door. Curved concrete walls, spiral staircase, double-height windows reveal. 8 seconds.",
            f"{CINEMATIC}. Walking across glass sky bridge. Stars above, landscape below. Arriving at lounge. 8 seconds.",
        ],
    },
    # 14
    {
        "name": "Aircraft Carrier Island",
        "hook": "An AIRCRAFT CARRIER became a private island! ⚓🏝️",
        "title": "Aircraft Carrier → Private ISLAND Resort! ⚓",
        "description": "A decommissioned aircraft carrier anchored as a private island resort with beach club, pool, helipad, and luxury suites!",
        "hashtags": "#shorts #aircraftcarrier #island #resort #luxury #navy #conversion",
        "frame_prompts": [
            f"{AERIAL}. Massive aircraft carrier anchored in turquoise tropical water. Workers on flight deck building pool and gardens. Island profile emerging. Palm trees being planted. {STYLE}",
            f"{AERIAL}. Completed carrier island — flight deck has infinity pool, palm trees, beach club area. Control tower is glass penthouse. Marina on stern. Lagoon surrounds. {STYLE}",
            f"{INTERIOR}. Former officers quarters now luxury hotel suite. Porthole windows enlarged to panoramic ocean views. Naval details preserved. King bed, teak floors, brass fixtures. {STYLE}",
            f"{INTERIOR}. Flight deck beach club — sand floor, tiki bar, pool edge. Open sky above, ocean visible over deck railing. DJ booth in old weapons elevator. Sunset party atmosphere. {STYLE}",
        ],
        "video_prompts": [
            f"{CINEMATIC}. Aerial approach to carrier island. Pool glows on deck. Palm trees, glass tower. Turquoise lagoon. 8 seconds.",
            f"{CINEMATIC}. Entering through reinforced door. Naval corridor opens to luxury suite. Ocean panorama through enlarged portholes. 8 seconds.",
            f"{CINEMATIC}. Ascending to flight deck. Beach club reveals — sand, pool, tiki bar, sunset over ocean. 8 seconds.",
        ],
    },
    # 15
    {
        "name": "Space Shuttle Hangar Home",
        "hook": "He lives inside a SPACE SHUTTLE hangar! 🚀🏠",
        "title": "NASA Hangar → LUXURY Shuttle Home! 🚀",
        "description": "A decommissioned NASA shuttle hangar with a real shuttle inside, converted into the ultimate aerospace-themed luxury home!",
        "hashtags": "#shorts #spaceshuttle #nasa #hangar #luxury #home #space",
        "frame_prompts": [
            f"{AERIAL}. Massive NASA hangar being renovated. Shuttle visible inside through open bay doors. Workers building residential structures around and inside the shuttle. Desert landscape. {STYLE}",
            f"{AERIAL}. Completed shuttle hangar home — hangar doors now glass walls. Shuttle inside lit dramatically. Pool extends from hangar onto tarmac. Modernist additions on sides. {STYLE}",
            f"{INTERIOR}. Inside the hangar — shuttle as centerpiece with living areas built around it. Double-height ceiling. Modern kitchen under the wing. Shuttle cargo bay opened as loft bedroom. {STYLE}",
            f"{INTERIOR}. Inside the shuttle cockpit restored as study/office. Original NASA controls preserved behind glass. Leather captain's chair as desk seat. Earth photos on screens. {STYLE}",
        ],
        "video_prompts": [
            f"{CINEMATIC}. Aerial approaching glass hangar. Shuttle visible inside, dramatically lit. Pool on tarmac. Desert sunset. 8 seconds.",
            f"{CINEMATIC}. Walking through glass doors into hangar. Shuttle towers above. Kitchen under the wing. Scale is breathtaking. 8 seconds.",
            f"{CINEMATIC}. Climbing into shuttle, entering restored cockpit. NASA controls, leather chair, Earth photos. Living in space history. 8 seconds.",
        ],
    },
    # 16
    {"name": "Yacht in Forest", "hook": "A SUPERYACHT in the middle of a forest! 🛥️🌲", "title": "Superyacht → Forest MANSION! 🛥️🌲", "description": "A 60m superyacht transported and placed in a forest clearing, converted into a luxury forest mansion!", "hashtags": "#shorts #yacht #forest #mansion #luxury #conversion #architecture",
     "frame_prompts": [f"{AERIAL}. 60-meter superyacht being transported on massive trucks through forest road to clearing. Trees tower around. Crane preparing to position. {STYLE}", f"{AERIAL}. Completed yacht mansion in forest clearing — white hull contrasts green trees. Deck furniture, pool on aft deck. Forest garden landscaping around hull. {STYLE}", f"{INTERIOR}. Yacht salon converted to forest lodge living room. Floor-to-ceiling windows show pine forest instead of ocean. Warm wood, cream leather, gold accents. {STYLE}", f"{INTERIOR}. Yacht master cabin — panoramic windows framing forest canopy. King bed, en-suite marble bathroom. Morning mist between trees outside. {STYLE}"],
     "video_prompts": [f"{CINEMATIC}. Aerial orbit around white yacht in green forest. Pool on deck, trees surround. Surreal beauty. 8 seconds.", f"{CINEMATIC}. Walking up gangway into yacht salon. Forest through windows instead of ocean. Warm luxury reveals. 8 seconds.", f"{CINEMATIC}. Pan to master cabin. Forest mist through panoramic windows. Marble bathroom. 8 seconds."]},
    # 17
    {"name": "Fire Truck Station House", "hook": "An old FIRE STATION → Family Dream Home! 🚒🏠", "title": "Abandoned Fire Station → Dream HOME! 🚒", "description": "A historic fire station with original brass poles and garage doors converted into an open-concept luxury family home!", "hashtags": "#shorts #firestation #home #conversion #brass #firehouse #luxury",
     "frame_prompts": [f"{AERIAL}. Workers renovating a brick fire station. Bay doors being replaced with glass. Scaffolding on clock tower. Vintage fire truck parked outside. {STYLE}", f"{AERIAL}. Completed fire station home — restored brick exterior, glass bay doors showing interior. Rooftop terrace with hot tub. Original clock tower preserved. Landscaped courtyard. {STYLE}", f"{INTERIOR}. Former truck bay now double-height living room. Original brass fire pole preserved as decorative element. Industrial ceiling beams, polished concrete floor, modern furniture. {STYLE}", f"{INTERIOR}. Upstairs dormitory converted to master suite. Exposed brick walls, iron bed frame, brass pole access to living room below. Clawfoot tub by arched window. {STYLE}"],
     "video_prompts": [f"{CINEMATIC}. Aerial of restored fire station. Glass bay doors glowing warm. Clock tower lit. Cozy exterior. 8 seconds.", f"{CINEMATIC}. Glass bay doors open. Camera enters double-height living room. Brass pole, industrial beams, modern furniture. 8 seconds.", f"{CINEMATIC}. Climbing to master suite. Exposed brick, brass pole, clawfoot tub by arched window. 8 seconds."]},
    # 18
    {"name": "Cruise Ship Mountain Lodge", "hook": "A CRUISE SHIP on top of a mountain! 🚢🏔️", "title": "Cruise Ship → Mountain Top LODGE! 🚢⛰️", "description": "A cruise ship section airlifted to a mountain peak and converted into the world's highest luxury lodge!", "hashtags": "#shorts #cruise #mountain #lodge #luxury #extreme #architecture",
     "frame_prompts": [f"{AERIAL}. Heavy-lift helicopters placing cruise ship section on mountain peak. Workers securing structure to rock foundation. Snow-capped peaks panorama. {STYLE}", f"{AERIAL}. Completed mountain cruise lodge — white ship section perched on peak. Glass observation deck at bow. Pool on lido deck with mountain views. Snow all around. {STYLE}", f"{INTERIOR}. Cruise ship atrium now mountain lodge lobby. Grand staircase, chandelier. But through the windows: snow-capped peaks instead of ocean. Cozy fireplaces added. {STYLE}", f"{INTERIOR}. Balcony stateroom with mountain panorama. Luxury bed facing floor-to-ceiling windows. Clouds float below. Hot chocolate on nightstand. Alpine paradise. {STYLE}"],
     "video_prompts": [f"{CINEMATIC}. Aerial orbit around cruise ship on mountain peak. Snow, clouds, pool on deck. Surreal location. 8 seconds.", f"{CINEMATIC}. Entering grand atrium. Staircase, chandelier, but mountains through windows. Fire crackling. 8 seconds.", f"{CINEMATIC}. Walking to stateroom. Balcony reveals mountain panorama. Clouds below. Alpine luxury. 8 seconds."]},
    # 19
    {"name": "Prison to Boutique Hotel", "hook": "Abandoned PRISON → 5-Star Boutique Hotel! 🔒✨", "title": "Old Prison → LUXURY Boutique Hotel! 🔒", "description": "A century-old prison with original cell blocks transformed into a luxury boutique hotel where each cell is a designer suite!", "hashtags": "#shorts #prison #hotel #boutique #luxury #conversion #historic",
     "frame_prompts": [f"{AERIAL}. Century-old stone prison being renovated. New glass roof over courtyard. Workers restoring cell blocks. Guard towers being converted to observation restaurants. {STYLE}", f"{AERIAL}. Completed prison hotel — stone walls preserved, glass roof over courtyard garden. Guard tower restaurants lit warmly. Pool in former exercise yard. Elegant entrance. {STYLE}", f"{INTERIOR}. Former prison cell converted to luxury micro-suite. Original iron bars as decorative headboard. Stone walls with velvet wallpaper accent. Rainfall shower where toilet was. {STYLE}", f"{INTERIOR}. Central courtyard under glass ceiling — now a tropical garden atrium. Dining tables among palms. Original cell block walkways as balconies above. Evening ambience. {STYLE}"],
     "video_prompts": [f"{CINEMATIC}. Aerial over prison hotel. Glass courtyard roof, guard tower restaurants, pool in yard. Historic beauty. 8 seconds.", f"{CINEMATIC}. Walking past iron gates into cell suite. Bars become headboard. Velvet walls, rainfall shower. Luxury in confinement. 8 seconds.", f"{CINEMATIC}. Emerging to courtyard garden. Palms, dining, cell block balconies above. Tropical prison paradise. 8 seconds."]},
    # 20
    {"name": "Double Decker Bus Hotel", "hook": "10 DOUBLE DECKER BUSES → Roadside Hotel! 🚌🏨", "title": "London Buses → Roadside HOTEL! 🚌", "description": "Ten retired London double-decker buses converted and arranged into a quirky roadside hotel with themed rooms!", "hashtags": "#shorts #doubledecker #bus #hotel #london #quirky #conversion",
     "frame_prompts": [f"{AERIAL}. Ten red London double-decker buses being arranged in a U-shape on a countryside hill. Workers modifying interiors. Central courtyard forming. {STYLE}", f"{AERIAL}. Completed bus hotel — 10 red buses in U-shape around courtyard with fire pit and fairy lights. Each bus a unique themed room. Green roofs on some buses. Reception bus at entrance. {STYLE}", f"{INTERIOR}. Inside a bus converted to luxury room — upper deck is bedroom with skylight roof. Restored original seats as reading nook. Warm wood floors, boutique hotel quality. {STYLE}", f"{INTERIOR}. Driver's area converted to romantic ensuite — freestanding tub where driver sat. Original steering wheel preserved. Views through windshield of rolling hills. {STYLE}"],
     "video_prompts": [f"{CINEMATIC}. Aerial over red bus hotel. Fairy lights, fire pit courtyard, countryside. Charming quirky. 8 seconds.", f"{CINEMATIC}. Stepping onto bus. Camera ascends stairs to upper deck bedroom. Skylight, warm wood, cozy bed. 8 seconds.", f"{CINEMATIC}. Moving to driver area — bathtub where wheel was. Hills through windshield. Unique luxury. 8 seconds."]},
    # 21-30: Short-form concepts
    {"name": "Lighthouse Cliff Mansion", "hook": "Abandoned LIGHTHOUSE → Cliff Edge Mansion! 🏮🏖️", "title": "Old Lighthouse → Cliff MANSION! 🏮", "description": "A decommissioned lighthouse on dramatic sea cliffs transformed into a luxury mansion with the light room as master bedroom!", "hashtags": "#shorts #lighthouse #cliff #mansion #luxury #ocean #renovation",
     "frame_prompts": [f"{AERIAL}. Workers renovating white lighthouse on dramatic sea cliffs. Glass additions being built around base. Crane on cliff edge. Waves crash below. {STYLE}", f"{AERIAL}. Completed lighthouse mansion — white tower with glass base additions. Wraparound terrace on cliff edge. Infinity pool overlooking ocean. Dramatic sunset. {STYLE}", f"{INTERIOR}. Light room converted to circular master bedroom. 360-degree ocean views. Original Fresnel lens preserved as art piece. King bed center. Sunrise position. {STYLE}", f"{INTERIOR}. Glass extension living room at base. Open to cliff edge through floor-to-ceiling windows. Waves visible below. White minimalist interior with driftwood accents. {STYLE}"],
     "video_prompts": [f"{CINEMATIC}. Aerial around lighthouse on cliffs. Pool on edge. Waves crash. Golden hour. 8 seconds.", f"{CINEMATIC}. Climbing spiral stairs to light room. 360 ocean reveals. Fresnel lens art. Bed in the sky. 8 seconds.", f"{CINEMATIC}. Descending to glass living room. Cliff edge views. Waves below. White luxury. 8 seconds."]},
    # 22
    {"name": "Airplane Graveyard Resort", "hook": "An AIRPLANE GRAVEYARD → Desert Resort! ✈️🏜️", "title": "Airplane Graveyard → Desert RESORT! ✈️🏜️", "description": "Multiple aircraft in a desert boneyard each converted into unique luxury suites forming an aviation-themed desert resort!", "hashtags": "#shorts #airplane #desert #resort #graveyard #aviation #luxury",
     "frame_prompts": [f"{AERIAL}. Desert airplane graveyard — five aircraft being renovated. Workers on each plane. Central pool being built between them. Desert mountains behind. {STYLE}", f"{AERIAL}. Completed resort — five aircraft as luxury suites around turquoise pool. Desert garden. Control tower as restaurant. Runway as entertainment strip. Night lights. {STYLE}", f"{INTERIOR}. Inside a 737 converted to luxury suite — business class seats removed, king bed installed. Original overhead bins now shelving. Ambient blue mood lighting. Desert views through windows. {STYLE}", f"{INTERIOR}. Cockpit converted to private hot tub room. Controls preserved behind glass. Bubble bath with desert sunset through cockpit windows. Ultimate aviation luxury. {STYLE}"],
     "video_prompts": [f"{CINEMATIC}. Aerial over airplane resort at sunset. Five planes, pool, desert mountains. Unique oasis. 8 seconds.", f"{CINEMATIC}. Entering 737 door. Business class now bedroom. Blue mood lighting, desert through windows. 8 seconds.", f"{CINEMATIC}. Moving forward to cockpit hot tub. Controls preserved, sunset through cockpit glass. 8 seconds."]},
    # 23
    {"name": "Castle Ruin Modern Villa", "hook": "Medieval CASTLE RUIN → Modern Luxury Villa! 🏰✨", "title": "Castle Ruin → MODERN Luxury Villa! 🏰", "description": "A crumbling medieval castle ruin with modern glass and steel additions creating a stunning historic-meets-contemporary villa!", "hashtags": "#shorts #castle #ruin #modern #luxury #villa #medieval #glass",
     "frame_prompts": [f"{AERIAL}. Medieval stone castle ruin with modern glass cube additions being built within the walls. Workers bridging old and new. Ancient towers, new steel beams. {STYLE}", f"{AERIAL}. Completed castle villa — ancient stone walls preserved, modern glass cubes inserted inside. Rooftop terrace on old tower. Pool in former courtyard. {STYLE}", f"{INTERIOR}. Modern glass living room inserted between ancient stone walls. Sleek furniture against 800-year-old masonry. Fireplace in original medieval hearth. {STYLE}", f"{INTERIOR}. Bedroom in restored tower — circular room, original arrow slit windows plus new panoramic glass. Four-poster modern bed. Stone spiral staircase. {STYLE}"],
     "video_prompts": [f"{CINEMATIC}. Aerial around castle villa. Ancient walls, modern glass. Pool in courtyard. Historic beauty. 8 seconds.", f"{CINEMATIC}. Walking through stone arch into glass living room. Medieval walls meet modern design. Fireplace in ancient hearth. 8 seconds.", f"{CINEMATIC}. Ascending tower staircase to circular bedroom. Arrow slits and panoramic glass. 800 years of history. 8 seconds."]},
    # 24
    {"name": "Missile Silo Smart Home", "hook": "Nuclear MISSILE SILO → Ultimate Smart Home! ☢️🏠", "title": "Missile Silo → Underground SMART Home! ☢️", "description": "A decommissioned nuclear missile silo 60 feet underground converted into an AI-powered smart home with blast door entrance!", "hashtags": "#shorts #missilesilo #smarthome #nuclear #underground #luxury #bunker",
     "frame_prompts": [f"{AERIAL}. Concrete missile silo cap in Kansas prairie. Heavy blast door being reinforced. Workers descending into shaft. Flat farmland stretches to horizon. {STYLE}", f"{AERIAL}. Completed silo home — surface level has dome greenhouse, solar array, small pool. Blast door entrance polished steel. Underground luxury invisible from above. {STYLE}", f"{INTERIOR}. 60 feet underground in the silo — multi-level open atrium with central void. Living room with vertical garden wall. Smart home screens and automated lighting. {STYLE}", f"{INTERIOR}. Silo bedroom level — curved concrete walls with LED sky ceiling simulating daylight. King bed, walk-in closet. AI voice assistant panel. 8 seconds from surface. {STYLE}"],
     "video_prompts": [f"{CINEMATIC}. Aerial over prairie. Small structures, blast door. Underground luxury invisible. Descending. 8 seconds.", f"{CINEMATIC}. Blast door opens with hydraulics. Elevator descends 60 feet. Atrium reveals, vertical garden, smart screens. 8 seconds.", f"{CINEMATIC}. Moving to bedroom level. LED sky ceiling, smart controls. Underground luxury technology. 8 seconds."]},
    # 25
    {"name": "Fishing Trawler Villa", "hook": "Old FISHING TRAWLER → Coastal Luxury Villa! 🚢🏡", "title": "Rusty Trawler → LUXURY Coastal Villa! 🚢", "description": "A decommissioned fishing trawler beached and converted into a coastal villa with the wheelhouse as master suite!", "hashtags": "#shorts #trawler #fishing #coastal #villa #luxury #beach #conversion",
     "frame_prompts": [f"{AERIAL}. Rusty fishing trawler being beached by crane on sandy coast. Workers removing fishing equipment. Coastal dunes, beach grass. {STYLE}", f"{AERIAL}. Completed trawler villa — hull painted navy blue, deck has outdoor living area. Wheelhouse has panoramic glass. Dune garden around. Beach access stairs. {STYLE}", f"{INTERIOR}. Ship hold converted to open-plan coastal living. White shiplap walls, porthole windows, nautical details preserved. Driftwood dining table, sea views. {STYLE}", f"{INTERIOR}. Wheelhouse master suite — original ship wheel preserved. Panoramic ocean views from captain's windows. King bed, maritime brass fixtures. Sunrise room. {STYLE}"],
     "video_prompts": [f"{CINEMATIC}. Aerial around navy trawler on beach. Deck living, dune garden. Coastal charm. 8 seconds.", f"{CINEMATIC}. Entering through hull door. White shiplap living room, portholes, nautical detail. Coastal luxury. 8 seconds.", f"{CINEMATIC}. Climbing to wheelhouse suite. Ship wheel, panoramic ocean. Captain's quarters luxury. 8 seconds."]},
    # 26
    {"name": "Stadium Underground City", "hook": "Abandoned STADIUM → Underground City! 🏟️🌆", "title": "Old Stadium → Underground CITY! 🏟️", "description": "A massive abandoned sports stadium with underground levels converted into a self-sustaining underground city with shops, homes, and gardens!", "hashtags": "#shorts #stadium #underground #city #conversion #survival #community",
     "frame_prompts": [f"{AERIAL}. Abandoned stadium being excavated beneath. Workers digging multi-level underground complex. Stadium superstructure provides the roof. Massive scale project. {STYLE}", f"{AERIAL}. Completed stadium city — arena floor is now a garden park. Underground levels visible through glass atriums. Stadium seating areas converted to terraced apartments. {STYLE}", f"{INTERIOR}. Underground shopping street beneath stadium — arched concrete ceilings with skylights to pitch above. Boutique shops, cafes. Plants hang from above. Warm lighting. {STYLE}", f"{INTERIOR}. Terraced apartment in former seating area — panoramic view of the garden arena below. Modern kitchen, living room. View of entire underground city from balcony. {STYLE}"],
     "video_prompts": [f"{CINEMATIC}. Aerial over stadium city. Garden arena floor, glass atriums, terraced apartments. Living city inside. 8 seconds.", f"{CINEMATIC}. Descending into underground shopping street. Arched ceiling, boutiques, cafes, skylights. Subterranean life. 8 seconds.", f"{CINEMATIC}. Entering terraced apartment. Balcony overlooks entire arena city below. Modern comfort. 8 seconds."]},
    # 27
    {"name": "Gondola Cable Car Hotel", "hook": "Cable Car GONDOLAS → Sky Hotel Suites! 🚡🏨", "title": "Cable Cars → SKY Hotel Suites! 🚡", "description": "Luxury hotel where each suite is a suspended cable car gondola with glass floors and mountain panoramas!", "hashtags": "#shorts #cablecar #gondola #hotel #sky #mountains #luxury",
     "frame_prompts": [f"{AERIAL}. Workers installing oversized luxury gondolas on cable car system over mountain valley. Each gondola the size of a small apartment. Alpine scenery. {STYLE}", f"{AERIAL}. Completed gondola hotel — 8 luxury gondolas suspended over valley at different heights. Central mountain station as lobby/restaurant. Snow peaks behind. Lights twinkling at dusk. {STYLE}", f"{INTERIOR}. Inside a gondola suite — glass floor showing valley 500m below. King bed with mountain view. Mini kitchen, rainfall shower in corner. Clouds at eye level. {STYLE}", f"{INTERIOR}. Mountain station restaurant — glass walls 360 degrees. Gourmet dining with alpine panorama. Original cable machinery preserved as industrial art. {STYLE}"],
     "video_prompts": [f"{CINEMATIC}. Aerial through gondola suites hanging over valley. Snow peaks, twinkling lights. Sky living. 8 seconds.", f"{CINEMATIC}. Entering gondola suite. Glass floor reveals valley below. Bed, mountain views, clouds. Vertigo luxury. 8 seconds.", f"{CINEMATIC}. Arriving at mountain station. Glass restaurant, 360 alpine views. Cable machinery art. 8 seconds."]},
    # 28
    {"name": "Cement Factory Loft", "hook": "Abandoned CEMENT FACTORY → Brutalist Luxury Loft! 🏭🏠", "title": "Cement Factory → LUXURY Brutalist Loft! 🏭", "description": "A massive abandoned cement factory with silos and smokestacks converted into a stunning brutalist luxury residence and art space!", "hashtags": "#shorts #cementfactory #brutalist #loft #luxury #industrial #architecture",
     "frame_prompts": [f"{AERIAL}. Massive abandoned cement factory — silos, conveyors, smokestacks. Workers cleaning and renovating. New glass additions visible. Industrial scale enormous. {STYLE}", f"{AERIAL}. Completed factory loft — concrete silos as tower rooms, main hall has glass roof. Gardens growing from old concrete. Pool in mixing basin. Dramatic brutalist beauty. {STYLE}", f"{INTERIOR}. Main hall — towering concrete space with glass roof. 20m ceiling. Living area dwarfed by industrial scale. Tropical garden bed, minimal furniture, art installations. {STYLE}", f"{INTERIOR}. Silo bedroom — circular concrete room, raw walls. Skylight at top. Floating bed, monstera plants. Rainfall shower in alcove. Monastic industrial luxury. {STYLE}"],
     "video_prompts": [f"{CINEMATIC}. Aerial over cement factory estate. Silos, glass roof, garden growing from concrete. Brutalist beauty. 8 seconds.", f"{CINEMATIC}. Entering main hall. 20m concrete ceiling, glass roof. Tiny furniture, massive space. Tropical garden. Breathtaking scale. 8 seconds.", f"{CINEMATIC}. Inside silo bedroom. Circular concrete, skylight beam, floating bed. Monastic luxury. 8 seconds."]},
    # 29
    {"name": "Tanker Truck Motel", "hook": "He parked 15 TANKER TRUCKS and made a motel! 🛢️🏨", "title": "15 Tanker Trucks → Roadside MOTEL! 🛢️", "description": "Fifteen fuel tanker trucks converted and parked in a row at a desert gas station, each one a unique luxury motel room!", "hashtags": "#shorts #tanker #truck #motel #desert #roadside #conversion",
     "frame_prompts": [f"{AERIAL}. Fifteen tanker trucks being positioned in a row at a desert gas station. Workers cutting doors and windows into cylindrical tanks. Route 66 vibes. {STYLE}", f"{AERIAL}. Completed tanker motel — 15 chrome tankers in row, each with round porthole windows and doors cut in. Neon MOTEL sign. Pool between rows. Desert sunset. Americana aesthetic. {STYLE}", f"{INTERIOR}. Inside a tanker room — cylindrical space with curved walls. Cozy queen bed with custom curved headboard. LED strip along ceiling curve. Porthole window shows desert. {STYLE}", f"{INTERIOR}. Tanker bathroom — wet room with curved walls. Rainfall shower, brushed chrome fixtures matching tank exterior. Round mirror. Industrial chic. {STYLE}"],
     "video_prompts": [f"{CINEMATIC}. Aerial over chrome tanker motel at sunset. Neon sign glows, pool sparkles, desert stretches. Americana. 8 seconds.", f"{CINEMATIC}. Opening tanker door. Curved interior reveals — cozy bed, LED strips, porthole desert view. Unique room. 8 seconds.", f"{CINEMATIC}. Into curved bathroom. Rainfall shower, chrome fixtures. Industrial luxury in a tank. 8 seconds."]},
    # 30
    {"name": "Wind Turbine Tower Home", "hook": "A WIND TURBINE became a tower home! 💨🏠", "title": "Wind Turbine → TOWER Living Space! 💨", "description": "A decommissioned wind turbine tower converted into a multi-level cylindrical home with the nacelle as a sky observation room!", "hashtags": "#shorts #windturbine #tower #home #sustainable #sky #conversion",
     "frame_prompts": [f"{AERIAL}. Workers converting a wind turbine — blades removed, nacelle being modified with glass windows. Platforms being added at multiple heights. Green energy farm around. {STYLE}", f"{AERIAL}. Completed turbine home — white tower with round windows at various levels. Nacelle at top has full glass walls as observation room. Rooftop garden ring. Spiral exterior staircase. {STYLE}", f"{INTERIOR}. Mid-tower cylindrical living room — curved white walls, porthole windows at 50m height. Custom curved sofa, central kitchen pod. Views for miles in every direction. {STYLE}", f"{INTERIOR}. Nacelle observation room at top — 80m up. Full glass walls, 360-degree views. Meditation space with floor cushions. Clouds drift past. Above the world. {STYLE}"],
     "video_prompts": [f"{CINEMATIC}. Aerial ascending along white turbine tower. Windows at levels, nacelle at top glowing. Wind farm around. 8 seconds.", f"{CINEMATIC}. Entering tower, elevator up. Mid-level living room reveals. Curved walls, panoramic views at 50m. 8 seconds.", f"{CINEMATIC}. Ascending to nacelle. Glass room 80m up. 360 views. Clouds drift past. Sky living. 8 seconds."]},
]


# ─── Daily concept selection ──────────────────────────────────────────────────

import json
from core.config import PROJECT_ROOT, logger

HISTORY_FILE = PROJECT_ROOT / "logs" / "aimagine_history.json"


def get_daily_concept() -> dict:
    """Pick a concept — TRENDING FIRST, static fallback.

    Priority:
      1. AI-generated trending concept (Gemini + viral patterns)
      2. Static TIMELAPSE_CONCEPTS list (if Gemini fails)
    """
    # Try trending concept first
    trending = _generate_trending_concept()
    if trending:
        # Save to history
        recent = []
        if HISTORY_FILE.exists():
            try:
                recent = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
            except Exception:
                recent = []
        recent.append(trending["name"])
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        HISTORY_FILE.write_text(json.dumps(recent[-60:], ensure_ascii=False), encoding="utf-8")
        logger.info(f"🔥 AImagine trending concept: {trending['name']}")
        return trending

    # Fallback: static list
    logger.info("📋 Trending failed, using static concept list...")
    recent = []
    if HISTORY_FILE.exists():
        try:
            recent = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            recent = []

    recent_set = set(recent[-30:])
    available = [c for c in TIMELAPSE_CONCEPTS if c["name"] not in recent_set]

    if not available:
        available = list(TIMELAPSE_CONCEPTS)

    chosen = random.choice(available)

    recent.append(chosen["name"])
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(recent[-60:], ensure_ascii=False), encoding="utf-8")

    logger.info(f"🏗️ AImagine concept (static): {chosen['name']} (pool: {len(available)}/{len(TIMELAPSE_CONCEPTS)} available)")
    return chosen


def _generate_trending_concept() -> dict | None:
    """Generate a trending construction concept using Gemini + viral format analytics.

    Produces a full concept dict compatible with the pipeline (name, hook, title,
    frame_prompts, video_prompts).
    """
    from core.trending import generate_trending_topic
    import google.generativeai as genai
    from core.config import GEMINI_API_KEY

    # Step 1: Get trending topic
    trending = generate_trending_topic("aimagine")
    if not trending or not trending.get("topic"):
        return None

    if not GEMINI_API_KEY:
        return None

    # Step 2: Generate full concept with frame/video prompts
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")

        concept_prompt = f"""You are a viral AI construction timelapse content creator.
        
Based on this trending topic, create a COMPLETE construction timelapse concept:

TOPIC: {trending['topic']}
TITLE: {trending.get('title', '')}

You must generate a full concept with frame prompts and video prompts.
The construction follows this format:
- Frame 1: Aerial view of construction site beginning (excavation, cranes, workers)
- Frame 2: Aerial view of completed structure (exterior beauty shot)
- Frame 3: Interior wide-angle shot of main living area
- Frame 4: Interior shot of most impressive room/feature

Use these constants in your prompts:
- AERIAL = "photorealistic aerial drone photograph, 45-degree angle, DJI Mavic 3 Pro"
- INTERIOR = "photorealistic wide-angle interior photograph, natural light, 9:16 vertical"
- CINEMATIC = "cinematic smooth camera movement, photorealistic, 9:16 vertical"
- STYLE = "hyper-realistic, 8K detail, natural lighting, architectural photography"

Return ONLY valid JSON with these exact keys:
{{
    "name": "Short concept name (3-5 words)",
    "hook": "Hook text with emoji (under 60 chars)",
    "title": "YouTube title with emoji (under 80 chars)",
    "description": "YouTube description (1-2 sentences)",
    "hashtags": "#shorts #construction #luxury #architecture #ai",
    "frame_prompts": ["frame1_prompt", "frame2_prompt", "frame3_prompt", "frame4_prompt"],
    "video_prompts": ["video1_prompt", "video2_prompt", "video3_prompt"]
}}"""

        response = model.generate_content(
            concept_prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.8,
            ),
        )

        result = json.loads(response.text)

        if result and result.get("name") and result.get("frame_prompts"):
            # Validate structure
            if len(result.get("frame_prompts", [])) >= 4 and len(result.get("video_prompts", [])) >= 3:
                logger.info(f"🔥 Generated trending concept: {result['name']}")
                return result
            else:
                logger.warning("⚠️ Trending concept missing required prompts")

    except Exception as e:
        logger.warning(f"⚠️ Trending concept generation failed: {e}")

    return None
