"""
AImagine — AI Construction Timelapse Concepts (v2)

30 unique concepts for 15 days of dual-upload content.
Each concept: empty land → excavation → construction → final reveal.
4 frames → 3 video clips → ~24s seamless timelapse.

Cost: ~128 credits ($0.64) per video.
"""

import random
from datetime import date

# ─── Shared constants ─────────────────────────────────────────────────────────

DRONE_VIEW = "photorealistic aerial drone photograph at 45-degree angle looking down"
CAMERA_NOTE = "Shot on DJI Mavic 3 Pro. Vertical 9:16 aspect ratio."
CONSISTENCY = "Maintain EXACT same camera angle and surrounding environment. ONLY modify the construction area."
LIGHTING = "Natural afternoon sunlight, consistent shadow direction, hyper-realistic textures."

TIMELAPSE_CONCEPTS = [
    # ─── 1. Rubik's Cube House ────────────────────────────────────────────────
    {
        "name": "Rubik's Cube House",
        "hook": "He Built a RUBIK'S CUBE You Can Live In! 🟥🟦",
        "title": "Building a RUBIK'S CUBE House! 🟥🟦🏠",
        "description": "A real house shaped like a giant Rubik's cube with rotating colored panels and LED-lit grid lines!",
        "hashtags": "#shorts #rubikscube #house #construction #timelapse #puzzle #satisfying",
        "frame_prompts": [
            f"{DRONE_VIEW} at an empty suburban lot. Flat terrain, green grass, wooden fence. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Square foundation 10x10m poured. Steel frame rising in perfect cubic shape. Workers welding grid structure. Crane nearby. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Cube structure 80% complete. Colored square panels being attached — red, blue, green, yellow, white, orange faces. Grid lines visible between panels. Windows cut into some squares. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at dusk. Completed Rubik's cube house — 6 colored faces perfect. LED strips glow white along grid lines. Some panels appear rotated. Warm interior light through windows. Modern landscaping. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Fast construction timelapse. Foundation poured in square. Steel cube frame rises. Workers weld grid. Fixed drone angle. 8 seconds.",
            "Rapid construction. Colored panels bolted to cube. Red, blue, green faces take shape. Windows installed. Fixed camera. 8 seconds.",
            "Cinematic reveal. LED grid lines glow. Colored faces vivid at dusk. Interior warm through windows. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 2. Cold War Bunker → Luxury SPA ──────────────────────────────────────
    {
        "name": "Bunker to Luxury SPA",
        "hook": "Cold War BUNKER → Underground Luxury SPA! 🧖✨",
        "title": "Abandoned Bunker → LUXURY Underground SPA! 🧖‍♂️",
        "description": "A forgotten Cold War bunker transformed into an underground luxury spa with hot pools, steam rooms, and ambient lighting!",
        "hashtags": "#shorts #bunker #spa #luxury #transformation #renovation #underground",
        "frame_prompts": [
            f"{DRONE_VIEW} at an overgrown concrete bunker entrance in a field. Rusted blast door, moss-covered walls, debris. Cold War era. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Bunker entrance cleared. Workers inside demolishing old walls. New waterproofing being applied. Plumbing roughed in for pools. Ventilation ducts upgraded. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Underground spa taking shape — stone tile walls, two soaking pools carved out, steam room glass doors installed. Fiber optic ceiling panels. Heated floors. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at dusk. Completed spa — warm turquoise pools glow from below. Steam wisps from hot room. Ambient amber lighting on stone walls. Bamboo accents. Entrance modernized with glass doors. Serene underground paradise. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Workers clear bunker. Walls demolished. Waterproofing applied. Pools excavated. Fast motion. Fixed drone. 8 seconds.",
            "Rapid construction. Stone tiles placed. Pools tiled. Glass steam room built. Ceiling fiber optics installed. Fixed camera. 8 seconds.",
            "Cinematic reveal. Pools glow turquoise. Steam rises. Amber lights warm stone. Underground luxury. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 3. Giant Eye Tower ───────────────────────────────────────────────────
    {
        "name": "Giant Eye Tower",
        "hook": "He Built a GIANT EYE Tower That Watches Everything! 👁️",
        "title": "Building a GIANT EYE Observation Tower! 👁️🏗️",
        "description": "A surreal observation tower shaped like a massive human eye with a rotating iris dome and pupil skylight!",
        "hashtags": "#shorts #eye #tower #surreal #construction #timelapse #architecture",
        "frame_prompts": [
            f"{DRONE_VIEW} at an open hilltop with panoramic views. Green grass, winding path. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Oval foundation poured. Steel framework rising in eye shape — almond curve. Workers building the iris dome support ring. Crane. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Eye structure taking shape — white sclera panels on outer shell. Blue-green iris dome forming with radial pattern. Dark pupil circle in center is a glass skylight. Eyelid overhang shades the observation deck. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at dusk. Completed eye tower — white shell gleams. Blue iris dome lit with radial LED strips. Pupil skylight glows warm from interior. The eye seems to watch the landscape. Winding lit path leads up. Surreal and stunning. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Fast construction. Oval foundation. Eye-shaped steel frame rises. Iris ring constructed. Fixed drone. 8 seconds.",
            "Rapid construction. White panels on shell. Blue iris dome assembled. Pupil skylight installed. Fixed camera. 8 seconds.",
            "Cinematic reveal. Iris LEDs glow blue concentric rings. Pupil warm. Eye watches landscape at dusk. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 4. Bank Vault → Whiskey Bar ──────────────────────────────────────────
    {
        "name": "Bank Vault Whiskey Bar",
        "hook": "Abandoned Bank Vault → Secret WHISKEY Bar! 🥃🔐",
        "title": "He Turned a BANK VAULT Into a Whiskey Bar! 🥃",
        "description": "A forgotten bank vault transformed into an exclusive whiskey bar with the original vault door as the entrance!",
        "hashtags": "#shorts #vault #whiskey #bar #transformation #luxury #speakeasy",
        "frame_prompts": [
            f"{DRONE_VIEW} at an abandoned bank interior. Massive vault door standing open, dusty marble floors, broken teller windows. Dark and forgotten. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Vault interior being gutted. Workers installing new flooring, bar counter framework rising along the back wall. Electrical rewired. Safe deposit boxes being cleaned. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Whiskey bar taking shape — dark walnut bar counter with brass rail. Restored safe deposit boxes now display whiskey bottles. Leather booth seating. Edison bulb lighting. Original vault door polished. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at evening. Completed whiskey bar — vault door gleams as entrance. Warm Edison glow inside. Whiskey bottles shimmer in old safe boxes. Leather seats filled. Brass accents everywhere. Speakeasy perfection. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Vault cleared. Bar framework rises. Flooring laid. Wiring installed. Fixed drone. 8 seconds.",
            "Rapid construction. Walnut bar built. Whiskey displayed in safe boxes. Leather booths placed. Edison bulbs hung. Fixed camera. 8 seconds.",
            "Cinematic reveal. Vault door gleams. Edison glow warm. Whiskey bottles shimmer amber. Speakeasy atmosphere. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 5. Chess Rook Tower House ────────────────────────────────────────────
    {
        "name": "Chess Rook Tower",
        "hook": "Living Inside a Giant CHESS ROOK Tower! ♜🏰",
        "title": "Building a CHESS ROOK Tower House! ♜🏗️",
        "description": "A medieval-style tower house shaped like a chess rook piece with battlements, spiral staircase, and a rooftop terrace!",
        "hashtags": "#shorts #chess #tower #castle #construction #timelapse #medieval",
        "frame_prompts": [
            f"{DRONE_VIEW} at a rural plot with rolling hills. Stone wall boundary. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Circular stone foundation. Thick cylindrical walls rising course by course. Workers laying stone blocks. Scaffolding wraps the cylinder. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Rook tower 80% complete — grey stone cylinder with narrow arrow-slit windows. Crown-shaped battlements being constructed at top with merlons and crenels. Heavy oak door at base. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at golden hour. Completed chess rook — perfect stone cylinder with crown battlements. Warm light from arrow slits. Rooftop terrace visible between merlons with furniture. Flag flying from one corner. Medieval meets modern. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Stone walls rise circular. Workers lay blocks course by course. Scaffolding climbs. Fixed drone. 8 seconds.",
            "Rapid construction. Battlements crown the top. Windows cut. Oak door hung. Stone completed. Fixed camera. 8 seconds.",
            "Cinematic reveal. Golden light through arrow slits. Flag waves. Rooftop terrace cozy. Medieval tower at sunset. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 6. Abandoned Mine → Crystal Pool ─────────────────────────────────────
    {
        "name": "Mine to Crystal Pool",
        "hook": "Abandoned MINE → Crystal Underground Pool! 💎🏊",
        "title": "He Turned an Abandoned Mine Into a POOL! 💎",
        "description": "A forgotten mine shaft transformed into a crystal-clear underground swimming pool with mineral rock walls and LED lighting!",
        "hashtags": "#shorts #mine #pool #underground #transformation #luxury #crystal",
        "frame_prompts": [
            f"{DRONE_VIEW} at an abandoned mine entrance. Rusty rail tracks, collapsed timber supports, overgrown with weeds. Dark tunnel mouth. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Mine entrance reinforced with steel. Workers inside excavating and waterproofing a cavern space. Natural rock walls retained. Pool basin forming. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Underground pool taking shape — natural rock walls with crystal formations preserved. Turquoise tiled pool basin. LED strips along rock edges. Wooden deck platform. Stone steps leading down. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at evening. Completed mine pool — crystal rock walls glow with blue and purple LEDs. Turquoise water perfectly still. Wooden deck with loungers. Mine entrance modernized with glass. Underground crystal paradise. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Mine reinforced. Cavern excavated. Pool basin formed. Rock walls cleaned. Fixed drone. 8 seconds.",
            "Rapid construction. Tiles laid. LED strips installed in rock. Deck built. Steps carved. Fixed camera. 8 seconds.",
            "Cinematic reveal. Crystal walls glow purple. Turquoise water shimmers. Underground pool paradise. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 7. Cactus Desert House ───────────────────────────────────────────────
    {
        "name": "Cactus Desert House",
        "hook": "He Built a CACTUS-Shaped Desert House! 🌵🏠",
        "title": "Building a CACTUS House in the Desert! 🌵",
        "description": "A desert home shaped like a massive saguaro cactus with arm-shaped rooms and a spine-textured green exterior!",
        "hashtags": "#shorts #cactus #desert #house #construction #timelapse #unique",
        "frame_prompts": [
            f"{DRONE_VIEW} at a desert lot. Sandy terrain, scattered desert plants, distant mountains. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Cylindrical concrete core rising with two arm branches extending at different heights. Steel framework. Workers shaping curved forms. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Cactus house structure covered in green textured panels with vertical spine ridges. Circular windows. Arm rooms have rounded ends. Terrace on top of main trunk. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at golden hour. Completed cactus house — green exterior with realistic spine texture. Warm light from circular windows. Rooftop terrace with desert views. Desert garden landscaped around base. Stunning against sunset sky. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Fast construction. Cylindrical core rises. Arms branch out. Steel formed. Fixed drone. 8 seconds.",
            "Rapid construction. Green panels with spines applied. Windows cut. Terrace built. Fixed camera. 8 seconds.",
            "Cinematic reveal. Green cactus glows in golden hour. Windows warm. Desert sunset behind. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 8. Bowling Alley → Surf Pool ─────────────────────────────────────────
    {
        "name": "Bowling Alley to Surf Pool",
        "hook": "Abandoned Bowling Alley → Indoor SURF Pool! 🏄🌊",
        "title": "He Turned a Bowling Alley Into a SURF POOL! 🏄",
        "description": "An abandoned bowling alley transformed into an indoor wave pool with artificial surf, neon lighting, and a beach bar!",
        "hashtags": "#shorts #bowling #surfpool #transformation #waves #renovation #epic",
        "frame_prompts": [
            f"{DRONE_VIEW} at an abandoned bowling alley interior. Dusty lanes, broken pin machines, peeling wallpaper, ceiling tiles missing. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Bowling lanes ripped out. Deep pool excavation where lanes were. Workers waterproofing. Wave generation machinery being installed at one end. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Surf pool 80% complete — long rectangular pool with wave machine. Sandy beach entry at one end. Neon tube lighting on ceiling. Beach bar counter along one wall. Tropical murals. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at evening. Completed indoor surf pool — perfect waves rolling down the lane. Neon pink and blue lighting. Sandy beach area. Beach bar glowing warm. Surfboards mounted on walls. Tropical paradise inside. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Lanes demolished. Pool excavated. Wave machine installed. Fixed drone. 8 seconds.",
            "Rapid construction. Pool tiled. Sand beach created. Neon lights hung. Bar built. Murals painted. Fixed camera. 8 seconds.",
            "Cinematic reveal. Waves roll perfectly. Neon pink and blue glow. Beach bar warm. Indoor surf paradise. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 9. Periscope House ───────────────────────────────────────────────────
    {
        "name": "Periscope House",
        "hook": "He Built a PERISCOPE House — See Everything! 🔭",
        "title": "Building a PERISCOPE-Shaped House! 🔭🏠",
        "description": "A tall house shaped like a submarine periscope with a rotating observation room at the top and mirror-glass angled windows!",
        "hashtags": "#shorts #periscope #house #construction #timelapse #military #unique",
        "frame_prompts": [
            f"{DRONE_VIEW} at a coastal lot overlooking the ocean. Grassy cliff edge. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Tall cylindrical steel framework rising 12 meters. Workers building the angled top section typical of a periscope shape. Foundation deep. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Periscope structure clad in matte grey panels. Angular top section with large angled mirror-glass windows. Observation room at top. Ladder rungs as decorative exterior element. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at dusk. Completed periscope house — grey military-style exterior. Angled glass windows reflect sunset. Observation room glows warm from interior. Ocean panorama visible. Coastal garden below. Striking silhouette. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Fast construction. Tall cylinder rises. Angled top section assembled. Workers climb scaffolding. Fixed drone. 8 seconds.",
            "Rapid construction. Grey panels applied. Mirror glass windows installed. Observation room finished. Fixed camera. 8 seconds.",
            "Cinematic reveal. Glass reflects sunset. Observation room glows. Ocean behind. Dusk silhouette. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 10. Windmill → Rotating Restaurant ───────────────────────────────────
    {
        "name": "Windmill to Restaurant",
        "hook": "200-Year-Old WINDMILL → Rotating Restaurant! 🌬️🍽️",
        "title": "He Turned an Old Windmill Into a RESTAURANT! 🌬️",
        "description": "A crumbling 200-year-old windmill transformed into a rotating restaurant with panoramic views and restored sails!",
        "hashtags": "#shorts #windmill #restaurant #transformation #renovation #panoramic",
        "frame_prompts": [
            f"{DRONE_VIEW} at an old stone windmill in a wheat field. Crumbling walls, broken sails, missing cap. Heritage structure barely standing. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Windmill walls reinforced. Workers rebuilding upper floors. New steel structure inside for rotating platform. Sails being restored with new timber. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Restaurant taking shape — stone walls restored. Large panoramic windows cut into upper level. Rotating floor mechanism installed. New wooden sails complete. Interior visible — dining tables. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at golden hour. Completed windmill restaurant — beautiful stone exterior restored. Sails turn slowly. Panoramic windows show warm dining room. Diners visible. Wheat field glows golden. String lights on terrace. Magical. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Walls reinforced. Floors rebuilt. Rotating platform installed. Sails restored. Fixed drone. 8 seconds.",
            "Rapid construction. Windows cut. Dining interior finished. Sails mounted. Terrace built. Fixed camera. 8 seconds.",
            "Cinematic reveal. Sails turn slowly. Warm dining glow. Golden wheat field. String lights sparkle. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 11. Ice Cube Cabin ───────────────────────────────────────────────────
    {
        "name": "Ice Cube Cabin",
        "hook": "He Built an ICE CUBE Cabin in the Mountains! ❄️",
        "title": "Building an ICE CUBE Mountain Cabin! ❄️🏔️",
        "description": "A mountain cabin shaped like a giant ice cube with translucent glass walls, frost-effect panels, and a warm glowing interior!",
        "hashtags": "#shorts #icecube #cabin #winter #construction #timelapse #mountains",
        "frame_prompts": [
            f"{DRONE_VIEW} at a snowy mountain clearing. Pine trees, snow-covered ground, mountain peaks. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Cube foundation on timber piles. Steel frame rising in perfect cubic shape. Workers installing structural glass panels. Snow around construction site. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Ice cube cabin structure — frosted translucent glass panels creating icy blue appearance. Internal wooden structure visible as shadows. Flat roof with snow. Heated glass prevents snow sticking to walls. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at blue hour. Completed ice cube cabin — translucent walls glow warm amber from interior fireplace. Ice-blue exterior against white snow. Pine forest frames the scene. Moonlight reflects off glass. Magical winter wonderland. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Fast construction. Foundation on snow. Cube frame rises. Glass panels installed. Fixed drone. 8 seconds.",
            "Rapid construction. Frosted panels applied. Interior built. Roof completed. Snow on surroundings. Fixed camera. 8 seconds.",
            "Cinematic reveal. Warm amber glow through ice-blue walls. Snow sparkles. Blue hour magic. Mountain cabin paradise. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 12. Water Tower → Sky House ──────────────────────────────────────────
    {
        "name": "Water Tower Sky House",
        "hook": "Abandoned Water Tower → Panoramic SKY HOUSE! 🏠☁️",
        "title": "He Turned a Water Tower Into a SKY HOUSE! ☁️",
        "description": "A rusted old water tower transformed into a stunning panoramic living space with 360-degree views and a wrap-around deck!",
        "hashtags": "#shorts #watertower #skyhouse #transformation #panoramic #renovation",
        "frame_prompts": [
            f"{DRONE_VIEW} at an old rusted water tower on steel legs. Peeling paint, bird nests, overgrown base. Rural setting, wide open views. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Tower legs reinforced with new steel. Workers cutting windows into the tank body. New floor structure being installed inside. Spiral staircase frame going up one leg. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Sky house taking shape — tank repainted white. Large panoramic windows all around. Wrap-around deck with railing. Interior visible — modern bedroom, kitchen. Spiral staircase complete. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at sunset. Completed sky house — white tank with panoramic windows glowing warm. Wrap-around deck with string lights. 360-degree sunset views. Modern interior visible. Spiral staircase lit. Living above the world. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Legs reinforced. Windows cut in tank. Floors installed. Staircase built. Fixed drone. 8 seconds.",
            "Rapid construction. White paint applied. Deck built around tank. Interior finished modern. Fixed camera. 8 seconds.",
            "Cinematic reveal. Panoramic sunset through windows. String lights on deck. 360 views. Sky house glows. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 13. AirPods Podcast Studio ───────────────────────────────────────────
    {
        "name": "AirPods Podcast Studio",
        "hook": "He Built a PODCAST Studio Shaped Like AirPods! 🎙️",
        "title": "Building an AIRPODS-Shaped Podcast Studio! 🎙️🏗️",
        "description": "A podcast studio shaped like a giant pair of AirPods with sound-insulated recording booths in each ear piece!",
        "hashtags": "#shorts #airpods #podcast #studio #construction #timelapse #tech",
        "frame_prompts": [
            f"{DRONE_VIEW} at a commercial lot. Flat terrain. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Two teardrop-shaped foundations with connecting walkway. Steel framework rising in AirPod ear shapes. Workers bending panels for smooth curves. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. AirPod structures covered in glossy white panels. Smooth curves matching the real product. Speaker grille mesh at bottom of each piece. Glass entrance door on connecting stem walkway. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at dusk. Completed AirPod studio — glossy white bodies glow. Blue ambient LED ring on each piece. One ear is the recording booth, other is the lounge. Stem walkway connects them. Modern tech aesthetic. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Fast construction. Two teardrop foundations. Frames rise in ear shapes. Smooth curves formed. Fixed drone. 8 seconds.",
            "Rapid construction. White panels applied. Grille mesh installed. Walkway built. Fixed camera. 8 seconds.",
            "Cinematic reveal. White bodies glow. Blue LED rings. Tech aesthetic at dusk. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 14. Train Station → Co-Working ───────────────────────────────────────
    {
        "name": "Station to Co-Working",
        "hook": "Ghost Train Station → Modern CO-WORKING Hub! 🚉💼",
        "title": "Abandoned Train Station → CO-WORKING Space! 🚉",
        "description": "A forgotten train station transformed into a modern co-working hub with the original platform as an open workspace!",
        "hashtags": "#shorts #trainstation #coworking #transformation #renovation #modern",
        "frame_prompts": [
            f"{DRONE_VIEW} at an abandoned train station. Broken glass canopy, overgrown tracks, faded signage, pigeons. Victorian-era brick building. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Station being restored. Glass canopy repaired. Tracks removed and platform being converted to floor space. Interior walls cleaned. New electrical. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Co-working space taking shape — restored brick walls. Long communal desk where tracks once were. Glass meeting pods on platform. Restored clock. Modern furniture mixed with heritage. Plants everywhere. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at evening. Completed co-working — glass canopy beautifully restored, lit warm. Workers at communal desks. Meeting pods glow. Restored clock shows time. Original signage preserved. Heritage meets modern. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Station cleared. Canopy repaired. Tracks removed. Platform converted. Fixed drone. 8 seconds.",
            "Rapid construction. Brick cleaned. Desks placed. Meeting pods installed. Clock restored. Plants added. Fixed camera. 8 seconds.",
            "Cinematic reveal. Canopy glows warm. Clock ticks. Workers at desks. Heritage beauty. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 15. Soccer Ball Sports Center ────────────────────────────────────────
    {
        "name": "Soccer Ball Sports Center",
        "hook": "He Built a SOCCER BALL-Shaped Sports Center! ⚽🏟️",
        "title": "Building a SOCCER BALL Sports Center! ⚽🏗️",
        "description": "A massive sports center shaped like a giant soccer ball with hexagonal and pentagonal panel windows!",
        "hashtags": "#shorts #soccer #football #sports #construction #timelapse #stadium",
        "frame_prompts": [
            f"{DRONE_VIEW} at a large sports field area. Flat ground w grass. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Geodesic dome framework rising — steel hexagons and pentagons forming soccer ball pattern. Crane lifts top sections. Workers weld joints. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Soccer ball structure 80% complete — white hexagonal panels and black pentagonal panels creating classic football pattern. Some panels are glass windows. Main entrance through one pentagon. Indoor court visible. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at dusk. Completed soccer ball sports center — iconic black and white geodesic pattern. Glass pentagon windows glow green from indoor turf below. White LED outlines hexagons. Landscaped sports fields around. Massive and stunning. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Fast construction. Geodesic dome frame rises. Hexagons and pentagons welded. Crane lifts top. Fixed drone. 8 seconds.",
            "Rapid construction. White and black panels applied. Glass windows installed. Court built inside. Fixed camera. 8 seconds.",
            "Cinematic reveal. Black and white pattern perfect. Green glow from indoor turf. LED outlines hexagons. Dusk. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 16. Lighthouse → Observatory ─────────────────────────────────────────
    {
        "name": "Lighthouse to Observatory",
        "hook": "Abandoned Lighthouse → Private OBSERVATORY! 🔭🌌",
        "title": "He Turned a Lighthouse Into an OBSERVATORY! 🔭",
        "description": "A decommissioned lighthouse transformed into a private astronomical observatory with retractable dome and telescope!",
        "hashtags": "#shorts #lighthouse #observatory #astronomy #transformation #stars",
        "frame_prompts": [
            f"{DRONE_VIEW} at a coastal lighthouse on rocky cliffs. White tower with broken light housing. Peeling paint, rusted railing. Ocean crashing below. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Lighthouse being restored. Workers replacing the light housing with a retractable dome mechanism. Interior floors reinforced for telescope mount. Windows cleaned. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Observatory taking shape — fresh white paint on tower. Retractable dome at top with slit opening visible. Large refractor telescope inside. Lower levels converted to library and control room. Railing restored. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at night. Completed observatory — white tower against starry sky. Dome open showing telescope pointing at stars. Warm control room glow from lower windows. Ocean reflects moonlight. A stargazer's dream. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Lighthouse restored. Dome mechanism installed. Telescope mounted. Paint applied. Fixed drone. 8 seconds.",
            "Rapid construction. Dome installed at top. Telescope visible. Library built below. Railing restored. Fixed camera. 8 seconds.",
            "Cinematic reveal. Dome opens to stars. Telescope points up. Moonlit ocean. Warm interior glow. Night magic. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 17. Pringles Can Store ───────────────────────────────────────────────
    {
        "name": "Pringles Can Store",
        "hook": "He Built a PRINGLES CAN Convenience Store! 🥫",
        "title": "Building a PRINGLES CAN Store! 🥫🏗️",
        "description": "A convenience store shaped like a massive Pringles tube with the mustache logo as the entrance awning!",
        "hashtags": "#shorts #pringles #store #food #construction #timelapse #creative",
        "frame_prompts": [
            f"{DRONE_VIEW} at a street corner commercial lot. Sidewalk and parking. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Large cylindrical steel framework rising. Workers curving panels for the tube body. A semicircle awning frame at the bottom for the mustache logo entrance. Cap structure at top. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Pringles tube structure covered in red glossy panels. Yellow band at bottom with mustache-shaped entrance awning. Green cap structure on top houses HVAC. Product graphics being applied. Shelving visible inside through glass door. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at dusk. Completed Pringles store — vibrant red tube with yellow band. Mustache entrance lit with LED. Green cap glows. Interior shelves stocked and lit. Neon OPEN sign. Parking spots painted. Eye-catching. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Fast construction. Cylinder rises. Curved panels formed. Awning frame built. Fixed drone. 8 seconds.",
            "Rapid construction. Red panels applied. Yellow band painted. Green cap placed. Graphics added. Fixed camera. 8 seconds.",
            "Cinematic reveal. Red tube vibrant. Mustache entrance glows. Neon sign on. Dusk lighting. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 18. Dam → Bungee Platform ────────────────────────────────────────────
    {
        "name": "Dam to Bungee Platform",
        "hook": "Abandoned Dam → Extreme BUNGEE Platform! 🪂",
        "title": "He Turned an Abandoned Dam Into BUNGEE JUMPING! 🪂",
        "description": "A decommissioned dam transformed into an extreme bungee jumping platform with glass observation deck and jump point!",
        "hashtags": "#shorts #dam #bungee #extreme #transformation #adventure #adrenaline",
        "frame_prompts": [
            f"{DRONE_VIEW} at an abandoned concrete dam. Cracked spillway, dry reservoir, overgrown walls. Impressive height. Mountain canyon. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Dam face being reinforced. Workers building a steel platform extending over the edge. Glass floor sections being installed. Safety railing. Staircase to top. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Bungee platform taking shape — steel and glass platform jutting out from dam face. Jump point with harness station. Glass observation deck below. Safety nets. LED runway lights on the platform edge. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at golden hour. Completed bungee platform — steel structure gleams against canyon. Glass platform reflects sky. LED runway lights marking jump zone. A jumper mid-leap silhouetted against sunset. Canyon river below. Extreme and beautiful. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Dam reinforced. Steel platform extends over edge. Glass floor installed. Fixed drone. 8 seconds.",
            "Rapid construction. Jump point built. Safety harness station. LED lights installed. Observation deck glassed. Fixed camera. 8 seconds.",
            "Cinematic reveal. Platform gleams at sunset. LED runway lights glow. Canyon below. Jumper silhouette. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 19. Octopus Restaurant ───────────────────────────────────────────────
    {
        "name": "Octopus Restaurant",
        "hook": "He Built an OCTOPUS Restaurant on the Water! 🐙🍽️",
        "title": "Building an OCTOPUS Restaurant! 🐙🏗️",
        "description": "A seafood restaurant shaped like a massive octopus sitting on the waterfront with tentacle-shaped dining extensions over the water!",
        "hashtags": "#shorts #octopus #restaurant #seafood #construction #timelapse #ocean",
        "frame_prompts": [
            f"{DRONE_VIEW} at a waterfront pier area. Wooden dock, calm bay water. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Dome-shaped central structure on pylons over water. Workers building 8 curved tentacle extensions radiating outward, supported by underwater pylons. Each tentacle curves differently. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Octopus structure covered — coral-red dome body with two large porthole windows as eyes. 8 tentacle dining extensions with suction cup details. Glass floors on tentacles to see water below. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at dusk. Completed octopus restaurant — coral-red body glows warm. Tentacle dining rooms lit with lanterns. Porthole eyes glow yellow. Water reflects all lights. Boats docked nearby. Surreal seafood paradise. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Fast construction. Dome rises on pylons. 8 tentacles extend over water. Workers build curves. Fixed drone. 8 seconds.",
            "Rapid construction. Red panels applied. Eyes installed. Suction cups added. Glass floors in tentacles. Fixed camera. 8 seconds.",
            "Cinematic reveal. Tentacles glow with lanterns. Eyes yellow. Water reflects. Dusk on the bay. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 20. Farm Silo → Spiral Library ───────────────────────────────────────
    {
        "name": "Silo to Spiral Library",
        "hook": "Abandoned Farm Silo → Spiral LIBRARY Tower! 📚",
        "title": "He Turned a Silo Into a SPIRAL LIBRARY! 📚",
        "description": "An old grain silo transformed into a stunning spiral library with books lining the cylindrical walls floor to ceiling!",
        "hashtags": "#shorts #silo #library #books #transformation #renovation #spiral",
        "frame_prompts": [
            f"{DRONE_VIEW} at a rusted farm grain silo. Corroded metal, surrounding farmland. Concrete base cracking. Adjacent barn ruins. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Silo exterior being replaced with new panels. Inside: workers building a spiral wooden staircase along the cylinder wall. Book shelves being installed in spiral. Skylight cut in roof. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Library silo structure — fresh exterior with vertical window strips. Interior: spiral staircase winding 5 stories up lined with floor-to-ceiling bookshelves. Reading nooks at each level. Skylight at top floods light down. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at golden hour. Completed spiral library — warm light from skylight pours down through the spiral. Thousands of books lining walls. Reading nooks glow with desk lamps. Vertical windows cast light strips. Books and warmth. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Silo restored. Spiral staircase built inside. Shelves installed around walls. Fixed drone. 8 seconds.",
            "Rapid construction. Books shelved floor to ceiling. Skylight cut. Reading nooks furnished. Lamps placed. Fixed camera. 8 seconds.",
            "Cinematic reveal. Golden light streams through skylight down spiral. Books glow warm. Desk lamps twinkle. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 21. Upside Down House ────────────────────────────────────────────────
    {
        "name": "Upside Down House",
        "hook": "He Built a House UPSIDE DOWN! 🙃🏠",
        "title": "Building an UPSIDE DOWN House! 🙃🏗️",
        "description": "A house built completely upside down — roof on the ground, foundation in the sky, inverted furniture inside!",
        "hashtags": "#shorts #upsidedown #house #illusion #construction #timelapse #crazy",
        "frame_prompts": [
            f"{DRONE_VIEW} at a suburban lot with flat ground. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. An inverted roof structure sits on the ground as foundation. Walls rising upward but with windows and door frames placed upside down. Workers building the house in reverse orientation. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Upside down house nearly complete — pitched roof on ground, foundation slab visible at top. Windows, shutters, door all inverted. A chimney points down from the roof-ground. Garden and mailbox also upside down. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at dusk. Completed upside down house — mind-bending perspective. Warm light from inverted windows. Front door is above eye level. Chimney in the ground. Garden fence points down. Visitors staring in disbelief. Viral optical illusion. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Fast construction. Roof placed on ground. Walls rise inverted. Everything built upside down. Fixed drone. 8 seconds.",
            "Rapid construction. Inverted windows, shutters, door installed. Chimney points down. Garden inverted. Fixed camera. 8 seconds.",
            "Cinematic reveal. Inverted house glows at dusk. Mind-bending perspective. Visitors stare. Optical illusion magic. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 22. Pier → Floating Cinema ───────────────────────────────────────────
    {
        "name": "Pier to Floating Cinema",
        "hook": "Abandoned Pier → Floating CINEMA on Water! 🎬🌊",
        "title": "He Built a FLOATING Cinema on an Old Pier! 🎬",
        "description": "An abandoned wooden pier transformed into a floating outdoor cinema with a massive screen over the water!",
        "hashtags": "#shorts #pier #cinema #floating #transformation #movies #outdoor",
        "frame_prompts": [
            f"{DRONE_VIEW} at an abandoned wooden pier. Broken planks, collapsed sections, rusted bollards. Calm harbor water. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Pier rebuilt with new hardwood decking. Workers erecting a large screen frame over the water at the end. Floating pontoon seating platforms being anchored. Electrical being run. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Floating cinema taking shape — massive inflatable screen at pier end over water. Rows of lounger seating on floating decks. String lights along new railings. Concession stand on the pier. Speakers on posts. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at night. Completed floating cinema — massive screen playing vivid movie over dark water. Guests on floating loungers watching. String lights reflect in water. Concession stand glowing. Stars above. Moonlit harbor. Magical outdoor cinema. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Pier rebuilt. Screen frame erected. Floating platforms anchored. Fixed drone. 8 seconds.",
            "Rapid construction. Screen inflated. Loungers placed. String lights hung. Speakers mounted. Fixed camera. 8 seconds.",
            "Cinematic reveal. Movie plays on screen. Lights reflect on water. Stars above. Night cinema magic. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 23. Honeycomb Hotel ──────────────────────────────────────────────────
    {
        "name": "Honeycomb Hotel",
        "hook": "He Built a HONEYCOMB Hotel — Each Room is a Cell! 🐝🍯",
        "title": "Building a HONEYCOMB Hotel! 🐝🏗️",
        "description": "A boutique hotel shaped like a giant honeycomb with hexagonal rooms, golden exterior, and a rooftop honey bar!",
        "hashtags": "#shorts #honeycomb #hotel #bee #construction #timelapse #unique",
        "frame_prompts": [
            f"{DRONE_VIEW} at a green hillside with wildflowers. Rolling meadow. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Steel hexagonal cells being stacked and welded in honeycomb pattern — 3 stories, each cell a room. Crane positions top cells. Workers inside finishing interiors. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Honeycomb hotel structure — golden amber panels on hexagonal cells. Each cell has a round porthole window. Shared corridors between cells. Rooftop terrace being built. Bee wing-shaped awning over entrance. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at golden hour. Completed honeycomb hotel — golden amber cells glow warm. Round windows lit from inside. Rooftop honey bar with golden canopy. Wildflower garden surrounds. Perfectly organic architecture merging with nature. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Fast construction. Hexagonal cells stacked by crane. Honeycomb pattern forms. Workers inside. Fixed drone. 8 seconds.",
            "Rapid construction. Golden panels applied. Porthole windows installed. Rooftop bar built. Fixed camera. 8 seconds.",
            "Cinematic reveal. Golden cells glow warm. Portholes lit. Wildflowers surround. Golden hour perfection. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 24. Stadium → Festival Venue ─────────────────────────────────────────
    {
        "name": "Stadium to Festival",
        "hook": "Abandoned Stadium → Music FESTIVAL Venue! 🎪🎶",
        "title": "He Turned a Stadium Into a FESTIVAL Venue! 🎪",
        "description": "An abandoned sports stadium transformed into a permanent music festival venue with multiple stages, art installations, and food courts!",
        "hashtags": "#shorts #stadium #festival #music #transformation #concert #epic",
        "frame_prompts": [
            f"{DRONE_VIEW} at an abandoned sports stadium. Overgrown pitch, broken seats, graffiti, collapsed press box. Concrete crumbling. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Stadium being renovated. Workers building a main stage at one end. Art installation frames going up on the pitch. Food court structures along the sides. Seating areas cleared and painted. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Festival venue taking shape — massive main stage with LED wall and speaker arrays. Colorful art installations on the pitch. Food court containers along sides. VIP area with couches. Entrance arch. Ferris wheel in one corner. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at night. Completed festival venue — main stage blazing with LED colors. Crowd fills the pitch. Ferris wheel lit with rainbow lights. Food courts glow warm. Laser beams cut the sky. Art installations pulse with light. Electric atmosphere. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Stadium cleared. Stage built. Art installed. Food courts constructed. Fixed drone. 8 seconds.",
            "Rapid construction. LED wall mounted. Ferris wheel assembled. VIP built. Entrance arch raised. Fixed camera. 8 seconds.",
            "Cinematic reveal. Stage blazes color. Ferris wheel rainbow. Lasers cut sky. Crowd fills pitch. Night energy. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 25. Pencil Art School ────────────────────────────────────────────────
    {
        "name": "Pencil Art School",
        "hook": "He Built a PENCIL-Shaped Art School! ✏️🎨",
        "title": "Building a PENCIL-Shaped Art School! ✏️🏗️",
        "description": "An art school shaped like a massive pencil laid on its side with a sharpened tip entrance and eraser-end gallery!",
        "hashtags": "#shorts #pencil #art #school #construction #timelapse #creative",
        "frame_prompts": [
            f"{DRONE_VIEW} at an educational campus area. Flat ground, paved paths. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Long hexagonal steel framework laid horizontally — pencil body shape. Workers building the conical tip section and cylindrical eraser end. Scaffold around. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Pencil building 80% complete — yellow hexagonal body panels with black band stripe. Conical wood-colored tip with graphite-grey point as entrance. Pink eraser cylinder end housing gallery. Windows along body. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at dusk. Completed pencil art school — vibrant yellow body. Graphite tip entrance lit warm. Pink eraser gallery glowing. Black band has the school name. Interior lit showing art studios. Colorful landscaping with paintbrush benches. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Fast construction. Hexagonal body frame laid. Tip cone built. Eraser cylinder at end. Fixed drone. 8 seconds.",
            "Rapid construction. Yellow panels applied. Graphite tip finished. Pink eraser gallery. Windows cut. Fixed camera. 8 seconds.",
            "Cinematic reveal. Yellow body vibrant. Tip entrance warm. Eraser glows pink. Art studios lit. Dusk. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 26. Fire Tower → Mountain Airbnb ─────────────────────────────────────
    {
        "name": "Fire Tower Airbnb",
        "hook": "Abandoned Fire Tower → Mountain TOP Airbnb! 🏔️🔥",
        "title": "He Turned a Fire Tower Into an AIRBNB! 🏔️",
        "description": "A decommissioned forest fire lookout tower transformed into a luxury mountain Airbnb with panoramic views!",
        "hashtags": "#shorts #firetower #airbnb #mountain #transformation #luxury #views",
        "frame_prompts": [
            f"{DRONE_VIEW} at an old wooden fire lookout tower on a mountain peak. Weathered timber, broken windows, overgrown stairs. Pine forest below. Mountain panorama. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Tower structure being reinforced. New timber replacing rotted sections. Windows being upgraded to double-pane glass. Interior being insulated. New stairs with proper railing. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Airbnb tower taking shape — fresh stained timber. Large panoramic windows on all sides. Cozy interior visible — bed, mini kitchen, wood stove. Wrap-around deck restored. Solar panel on roof. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at sunset over mountains. Completed fire tower Airbnb — warm timber glows. Panoramic windows reflect mountain sunset. Warm interior with fireplace glow. Deck has two chairs facing the view. Solar panel gleams. Pine forest carpet below. Ultimate mountain retreat. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Tower reinforced. New timber replacing old. Windows upgraded. Stairs rebuilt. Fixed drone. 8 seconds.",
            "Rapid construction. Interior insulated. Furniture placed. Wood stove installed. Deck restored. Fixed camera. 8 seconds.",
            "Cinematic reveal. Mountain sunset through windows. Fireplace glows. Two chairs on deck. Pine forest below. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 27. Mushroom Fairy Tale House ────────────────────────────────────────
    {
        "name": "Mushroom House",
        "hook": "He Built a MUSHROOM House From a Fairy Tale! 🍄🏡",
        "title": "Building a MUSHROOM Fairy Tale House! 🍄",
        "description": "A whimsical house shaped like a giant mushroom with a red-spotted cap roof and a cozy stem living space!",
        "hashtags": "#shorts #mushroom #fairytale #house #construction #timelapse #fantasy",
        "frame_prompts": [
            f"{DRONE_VIEW} at a woodland clearing surrounded by oak trees. Mossy ground, dappled sunlight. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Cylindrical concrete stem structure rising 2 stories. Workers building the wide dome framework for the mushroom cap on top. Scaffolding surrounds. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Mushroom house nearly complete — white stem walls with small round windows and a hobbit-style arched door. Red dome cap roof with white polka dot patterns. Gills visible under the cap overhang. Stone pathway. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at golden hour. Completed mushroom house — white stem glows warm. Red cap with white spots vivid against green forest. Warm light from round windows. Fairy garden with tiny mushroom lights along stone path. Magical, whimsical perfection. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Fast construction. Cylindrical stem rises. Dome cap framework built on top. Fixed drone. 8 seconds.",
            "Rapid construction. White walls painted. Red cap with white dots applied. Arched door hung. Stone path laid. Fixed camera. 8 seconds.",
            "Cinematic reveal. Red cap vivid. Warm glow from windows. Fairy lights along path. Golden hour forest magic. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 28. Hospital → Wellness Center ───────────────────────────────────────
    {
        "name": "Hospital to Wellness",
        "hook": "Abandoned Hospital → Luxury WELLNESS Center! 🏥→🧘",
        "title": "He Turned a Hospital Into a WELLNESS Center! 🧘",
        "description": "An abandoned hospital transformed into a luxury wellness center with yoga studios in former operating rooms and a rooftop meditation garden!",
        "hashtags": "#shorts #hospital #wellness #spa #transformation #renovation #yoga",
        "frame_prompts": [
            f"{DRONE_VIEW} at an abandoned hospital building. Broken windows, overgrown courtyard, faded red cross sign. Multi-story concrete building deteriorating. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Hospital being gutted and renovated. Workers removing old fixtures. New bamboo flooring being installed. Large windows being cut. Rooftop being cleared for garden. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Wellness center taking shape — clean white walls with natural wood accents. Former wards now yoga halls with mirrors. Hydrotherapy pool in old basement. Rooftop garden with meditation pods. Bamboo and stone throughout. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at golden hour. Completed wellness center — serene white exterior. Rooftop meditation garden with zen stones and bamboo. Yoga practitioners visible through large windows. Hydrotherapy pool glows blue. Water features in courtyard. Tranquil paradise. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Hospital gutted. New floors installed. Windows enlarged. Rooftop cleared. Fixed drone. 8 seconds.",
            "Rapid construction. Yoga halls finished. Pool built. Rooftop garden planted. Meditation pods placed. Fixed camera. 8 seconds.",
            "Cinematic reveal. Rooftop garden serene. Yoga through windows. Pool glows blue. Golden hour peace. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 29. Teapot Tea House ─────────────────────────────────────────────────
    {
        "name": "Teapot Tea House",
        "hook": "He Built a TEAPOT-Shaped Tea House! 🫖",
        "title": "Building a TEAPOT Tea House! 🫖🏗️",
        "description": "A charming tea house shaped like a giant ceramic teapot with a spout entrance canopy and lid-shaped rooftop terrace!",
        "hashtags": "#shorts #teapot #teahouse #construction #timelapse #cozy #unique",
        "frame_prompts": [
            f"{DRONE_VIEW} at a garden area with hedgerows and flower beds. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Round bulbous structure rising — the teapot body. Workers building the curved spout extension and handle arch on opposite sides. Scaffolding wraps around. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Teapot structure covered in cream ceramic-look panels. Handle is a decorative arch with seating underneath. Spout extends as an entrance canopy. Removable lid at top is a terrace. Round windows. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at golden hour. Completed teapot tea house — warm cream body. Spout entrance with guests entering. Handle arch with cozy bench. Lid terrace has outdoor seating. Round windows glow warm from tea room inside. Rose garden surrounds. English charm. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Fast construction. Round body rises. Spout and handle formed. Lid built on top. Fixed drone. 8 seconds.",
            "Rapid construction. Cream panels applied. Round windows cut. Interior furnished. Garden planted. Fixed camera. 8 seconds.",
            "Cinematic reveal. Teapot glows cream. Spout entrance inviting. Rose garden blooms. Golden hour warmth. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 30. Submarine Base → Dive Center ─────────────────────────────────────
    {
        "name": "Sub Base to Dive Center",
        "hook": "Abandoned Submarine Base → SCUBA Diving Center! 🤿",
        "title": "He Turned a Sub Base Into a DIVE CENTER! 🤿",
        "description": "A Cold War submarine base transformed into a scuba diving center with underwater training pools in the old sub pens!",
        "hashtags": "#shorts #submarine #diving #scuba #transformation #military #underwater",
        "frame_prompts": [
            f"{DRONE_VIEW} at an abandoned submarine pen — massive concrete bunker opening to water. Rusted blast doors, crumbling walkways, flooded sub berths. Cold War era. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Sub pens being renovated. Workers cleaning pools, reinforcing walls. New filtration systems. Underwater lighting being installed. Office spaces being built on upper catwalks. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Dive center taking shape — crystal clear water in sub pens. Underwater LED lighting showing artificial reef structures. Training platforms at different depths. Equipment storage racks. Modern reception on upper level. Glass viewing windows. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at dusk. Completed dive center — sub pen water glows turquoise from underwater LEDs. Artificial reefs visible below surface. Divers training with bubbles rising. Modern reception lit warm above. Historic concrete structure beautifully repurposed. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Sub pens cleared. Pools cleaned. Filtration installed. Walls reinforced. Fixed drone. 8 seconds.",
            "Rapid construction. Underwater lights placed. Reef structures sunk. Training platforms built. Reception finished. Fixed camera. 8 seconds.",
            "Cinematic reveal. Turquoise water glows. Divers bubble below. Reception warm above. Historic meets modern. Fixed angle. 8 seconds.",
        ],
    },
]


# ─── Daily concept selection ──────────────────────────────────────────────────

import json
from core.config import PROJECT_ROOT, logger

HISTORY_FILE = PROJECT_ROOT / "logs" / "aimagine_history.json"


def get_daily_concept() -> dict:
    """Pick a random concept, avoiding recent repeats using history file."""
    # Load history
    recent = []
    if HISTORY_FILE.exists():
        try:
            recent = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            recent = []

    # Find concepts not recently used (last 30 days)
    recent_set = set(recent[-30:])
    available = [c for c in TIMELAPSE_CONCEPTS if c["name"] not in recent_set]

    if not available:
        # All concepts used, reset and pick any
        available = list(TIMELAPSE_CONCEPTS)

    chosen = random.choice(available)

    # Save to history
    recent.append(chosen["name"])
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(recent[-60:], ensure_ascii=False), encoding="utf-8")

    logger.info(f"🏗️ AImagine concept: {chosen['name']} (pool: {len(available)}/{len(TIMELAPSE_CONCEPTS)} available)")
    return chosen
