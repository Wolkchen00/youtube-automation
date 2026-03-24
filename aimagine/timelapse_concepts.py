"""
AImagine — AI Construction Timelapse Concepts

20+ viral construction timelapse concepts inspired by @cairo_ia (189K).
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
    # ─── 1. iPhone Pool ───────────────────────────────────────────────────────
    {
        "name": "iPhone Shaped Pool",
        "hook": "He Built the First iPhone-Shaped Pool in the World! 📱💦",
        "title": "Building a GIANT iPhone Pool From Scratch! 📱🏊",
        "description": "Watch this incredible transformation as we build a massive iPhone-shaped swimming pool from an empty backyard! Complete with camera lens jacuzzi and glowing Apple logo island.",
        "hashtags": "#shorts #construction #pool #iphone #timelapse #diy #satisfying #building",
        "frame_prompts": [
            f"{DRONE_VIEW} at a spacious suburban backyard. Green grass lawn about 400sqm surrounded by wooden fences. Adjacent houses, mature trees, concrete patio near the house. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. The backyard now has a large excavation in the shape of a giant iPhone, about 12 meters long. Excavator parked nearby, large dirt mounds on sides. 3 workers with shovels refining edges. Concrete foundation visible at the bottom. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. The iPhone-shaped pool structure is now 80% complete — smooth concrete walls, blue mosaic tile interior, plumbing pipes visible. A circular camera-lens shaped jacuzzi area at the top. Apple logo island forming in the center. Workers applying tiles. Wooden deck framing around exterior. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at blue hour/dusk. The completed iPhone pool is filled with crystal blue water. LED strips outline the entire pool shape in white light. The camera lens jacuzzi bubbles. Apple logo island glows with embedded LEDs. Finished wooden deck surrounds the pool. Fresh landscaping with palm trees. Absolutely stunning. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Fast-paced construction timelapse from above. Excavator digs iPhone shape into lawn. Earth removed rapidly, pit deepens. Workers move quickly. Fixed 45-degree drone angle. 8 seconds.",
            "Rapid construction timelapse. Concrete poured into iPhone-shaped excavation. Walls rise, tiles applied, plumbing installed. Workers in fast motion building deck around pool. Fixed camera angle. 8 seconds.",
            "Cinematic reveal timelapse. Pool fills with sparkling water. LED lights illuminate one by one outlining the iPhone shape. Transition from golden hour to blue dusk. Camera remains fixed at 45 degrees. Breathtaking transformation. 8 seconds.",
        ],
    },

    # ─── 2. Lamborghini Garage ────────────────────────────────────────────────
    {
        "name": "Lamborghini Garage",
        "hook": "He Built a Life-Size Lamborghini Garage from Scratch! 🏎️🔥",
        "title": "Building a LAMBORGHINI-Shaped Garage! 🏎️🔥",
        "description": "From empty lot to the most insane car garage ever built — shaped like a real Lamborghini Aventador! With LED-lit turntable inside.",
        "hashtags": "#shorts #lamborghini #garage #construction #timelapse #supercar #diy",
        "frame_prompts": [
            f"{DRONE_VIEW} at a spacious green suburban lawn. Wide open grassy area surrounded by wooden fence, adjacent houses visible. Afternoon sun. {CAMERA_NOTE}",
            f"{DRONE_VIEW}. The lawn now has a deep Lamborghini-shaped excavation, 2 meters deep. Mini excavator parked beside, dirt mounds on sides. Rebar reinforcement visible. Workers with shovels. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. A sleek metallic garage structure sits over the Lamborghini-shaped foundation. Black steel frame, large glass panels on sides. Flat modern roof following aerodynamic curves. Interior floor visible — polished black epoxy. Workers installing roof panels. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at blue hour. Completed Lamborghini garage glows with orange LED strips outlining the structure. Glass doors open revealing a gleaming yellow Lamborghini Aventador on an illuminated turntable inside. Landscaped driveway with floor lights. Spectacular against twilight sky. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Fast construction timelapse. Excavator digs Lamborghini shape into grass. Concrete poured, rebar placed. Workers move rapidly. Fixed 45-degree drone. 8 seconds.",
            "Rapid construction timelapse. Steel beams erected forming the garage. Glass panels installed. Interior finished with polished floor. Workers weld and bolt in fast motion. Fixed camera. 8 seconds.",
            "Cinematic reveal. LED strips illuminate the Lamborghini garage one by one. Glass doors open revealing a supercar on a glowing turntable. Lighting transitions to blue hour. Fixed angle. Breathtaking. 8 seconds.",
        ],
    },

    # ─── 3. PS5 Gaming Room ───────────────────────────────────────────────────
    {
        "name": "Giant PS5 Gaming Room",
        "hook": "He Turned His Basement into a GIANT PS5 Gaming Room! 🎮🤯",
        "title": "Building a PS5-Shaped Gaming Room! 🎮✨",
        "description": "The ultimate gaming setup — an entire room shaped like a PlayStation 5! LED-lit walls, massive screen, and a custom gaming throne inside.",
        "hashtags": "#shorts #ps5 #gaming #construction #timelapse #gamer #playstation",
        "frame_prompts": [
            f"{DRONE_VIEW} at an empty concrete basement/cellar room. Raw walls, exposed pipes, single bare bulb. Dusty floor. {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Half-demolished walls reshaped into curves matching the PS5 console shape. Workers installing metal framing. Electrical conduits routed. Debris and tools scattered. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Structure nearly complete — smooth white curved walls matching PS5 design. Black accent panels installed. A massive 120-inch screen mounted. Custom gaming chair platform in center. LED strips along ceiling edges (off). {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Completed PS5 gaming room in all its glory. Blue LED strips glow along the PS5 curves. The giant screen displays a vibrant game. Ambient RGB lighting reflects off the white walls. Gaming throne illuminated. Absolutely stunning futuristic gaming cave. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Workers demolish old walls, reshape them into PS5 curved forms. Metal framing installed. Fast motion, dust and sparks. Fixed camera angle. 8 seconds.",
            "Rapid construction timelapse. White panels applied, screen mounted, LED strips installed. Custom furniture placed. Workers moving quickly. Fixed 45-degree view. 8 seconds.",
            "Cinematic reveal. LED strips light up blue following PS5 curves. Screen powers on with vibrant display. RGB ambient lighting transitions create stunning glow. Camera remains fixed. 8 seconds.",
        ],
    },

    # ─── 4. Pirate Ship Treehouse ─────────────────────────────────────────────
    {
        "name": "Pirate Ship Treehouse",
        "hook": "He Built a REAL Pirate Ship Treehouse! 🏴‍☠️⚓",
        "title": "Building a Pirate Ship in a TREE! ☠️🌳",
        "description": "From a simple oak tree to an incredible pirate ship treehouse with sails, cannons, and a plank! The most epic treehouse ever constructed.",
        "hashtags": "#shorts #pirateship #treehouse #construction #timelapse #epic #diy",
        "frame_prompts": [
            f"{DRONE_VIEW} at a large backyard with a massive old oak tree in the center. Thick trunk, spreading canopy. Green lawn around. Suburban houses in background. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Wooden platform framework built among the oak tree branches. Scaffolding around the trunk. Workers hoisting lumber. The hull shape of a ship beginning to form. Sawdust and tools below. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Pirate ship structure 80% complete in the tree. Dark wood hull with port holes, a steering wheel visible, rope ladders hanging. A plank extends outward. Mast poles erected but no sails yet. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at golden hour. Completed pirate ship treehouse — dark weathered wood, white canvas sails unfurled, skull-and-crossbones flag flying. String lights along the rails. A rope bridge connects to a crow's nest. Magical warm lighting through the leaves. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Workers hoist lumber into the tree, building platform and hull frame. Scaffolding erected. Tools and sawdust fly. Fast motion. Fixed drone angle. 8 seconds.",
            "Rapid construction timelapse. Ship hull takes shape — planks nailed, portholes cut, steering wheel installed. Mast poles erected. Workers climbing and building. Fixed 45-degree view. 8 seconds.",
            "Cinematic reveal. White sails unfurl in the wind. String lights illuminate along the rails. Pirate flag raised. Golden hour light streams through the canopy. Fixed angle. Magical. 8 seconds.",
        ],
    },

    # ─── 5. Tesla Cybertruck House ────────────────────────────────────────────
    {
        "name": "Cybertruck House",
        "hook": "He Built a House Shaped Like a Tesla Cybertruck! 🔺🏠",
        "title": "Building a CYBERTRUCK-Shaped House! ⚡🏗️",
        "description": "From an empty lot to a futuristic home shaped like Tesla's Cybertruck! Stainless steel exterior, angular design, and LED-lit windows.",
        "hashtags": "#shorts #tesla #cybertruck #house #construction #timelapse #futuristic",
        "frame_prompts": [
            f"{DRONE_VIEW} at an empty suburban lot. Flat dirt ground, surveyor stakes marking boundaries. Adjacent houses on both sides. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Concrete foundation poured in angular Cybertruck shape. Steel frame rising with sharp geometric angles. A concrete mixer and crane nearby. Workers welding angular beams. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Angular structure nearly complete — brushed stainless steel panels cladding the exterior. Triangular windows cut. The distinct Cybertruck front end forming the main entrance. Interior visible through openings — modern minimalist. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at dusk. Completed Cybertruck house glowing. White LED strips outline every angular edge. Triangular windows glow warm from interior lights. A real Tesla Cybertruck parked in the angular driveway. Landscaped xeriscaping with modern desert plants. Futuristic and stunning. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Fast construction timelapse. Concrete poured in angular mold. Steel beams welded into sharp geometric shapes. Crane lifts panels. Fast motion. Fixed drone angle. 8 seconds.",
            "Rapid construction timelapse. Stainless steel panels bolted onto angular frame. Windows cut. Interior finishing visible. Workers move rapidly. Fixed 45-degree camera. 8 seconds.",
            "Cinematic reveal. LED strips illuminate every edge of the Cybertruck house. Windows glow warm. A real Cybertruck pulls into the angular driveway. Dusk lighting. Futuristic beauty. 8 seconds.",
        ],
    },

    # ─── 6. Dragon Slide Water Park ───────────────────────────────────────────
    {
        "name": "Dragon Water Slide",
        "hook": "He Built a DRAGON Water Slide in His Backyard! 🐉💦",
        "title": "Building a DRAGON-Shaped Water Slide! 🐉🌊",
        "description": "The most insane backyard water slide ever — a massive fire-breathing dragon! Riders slide through the dragon's body into a splash pool.",
        "hashtags": "#shorts #waterslide #dragon #construction #timelapse #summer #epic",
        "frame_prompts": [
            f"{DRONE_VIEW} at a large backyard with a gentle hillside slope. Green grass, wooden fence perimeter. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Metal framework of a dragon skeleton rising from the hillside. Workers welding curved ribs and spine structure. Foundation poured at the base for a splash pool. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Dragon structure 80% complete — scaled green exterior panels covering the body. Open jaws with teeth at the top start. Wings spread as decorative features. Enclosed tube slide running through the body. Splash pool excavated at the bottom. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at golden hour. Completed dragon water slide — gleaming green scales, fiery red LED eyes and throat glow. Water flowing through the dragon body slide into a crystal blue splash pool. Mist from the dragon's mouth. Landscaped tropical plants around the base. Epic and magical. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Metal framework shaped into dragon skeleton on hillside. Workers weld ribs and spine. Foundation poured below. Fast motion. Fixed drone. 8 seconds.",
            "Rapid construction. Green scale panels attached to dragon frame. Wings spread. Slide tube installed inside. Splash pool tiled. Workers climb scaffolding. Fixed view. 8 seconds.",
            "Cinematic reveal. Dragon's eyes glow red. Water rushes through the slide, splashing into the pool. Mist rises from dragon's mouth. Golden hour light. Fixed angle. Breathtaking. 8 seconds.",
        ],
    },

    # ─── 7. Pizza Oven Villa ──────────────────────────────────────────────────
    {
        "name": "Pizza Oven Villa",
        "hook": "He Built a House Shaped Like a Giant Pizza Oven! 🍕🏠",
        "title": "Building a PIZZA OVEN House! 🍕🔥",
        "description": "From countryside land to an incredible dome-shaped house that looks like a massive Italian pizza oven! With a real wood-fired pizza kitchen inside.",
        "hashtags": "#shorts #pizza #house #construction #timelapse #italian #dome",
        "frame_prompts": [
            f"{DRONE_VIEW} at a rural countryside lot with rolling green hills. Wildflowers, olive trees, a dirt path leading in. Tuscany-style landscape. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Circular foundation poured. Red brick dome structure rising — workers laying bricks in arched formation. Scaffolding around the dome. The shape resembling a giant pizza oven. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Dome structure nearly complete — rustic red brick exterior, arched doorway entrance with heavy wooden door. A chimney rising from the top. Small round windows. Stone path being laid to the entrance. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at golden hour. Completed pizza oven villa glowing warm. Smoke curling from the chimney. Warm light from inside through the arched doorway shows a cozy interior. String lights along the stone path. Olive trees framing the scene. A pizza being pulled from a real brick oven visible through a side window. Magical Tuscan charm. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Workers lay bricks in arched dome formation. Scaffolding circles the structure. Red brick dome grows taller. Fixed 45-degree drone. 8 seconds.",
            "Rapid construction. Dome completed, door installed, chimney built. Stone pathways laid. Workers add finishing touches. Fixed camera. 8 seconds.",
            "Cinematic reveal. Smoke curls from chimney. Warm interior glow through archway. String lights sparkle along path. Golden hour in Tuscany. Fixed angle. Italian charm. 8 seconds.",
        ],
    },

    # ─── 8. Minecraft House ───────────────────────────────────────────────────
    {
        "name": "Real Life Minecraft House",
        "hook": "He Built a REAL Minecraft House with REAL Blocks! 🟫⛏️",
        "title": "Minecraft House IRL! Building Block by Block! 🟫🏠",
        "description": "Every gamer's dream — a real-life Minecraft house built with actual cube-shaped blocks! Pixelated windows, door, and a creeper garden!",
        "hashtags": "#shorts #minecraft #house #gaming #construction #timelapse #irl",
        "frame_prompts": [
            f"{DRONE_VIEW} at a suburban backyard with flat green lawn. Simple wooden fence, adjacent houses. Clear sky. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Workers stacking large brown cube-shaped concrete blocks (like Minecraft dirt blocks) to form walls. The structure is half-height — clearly cubic/pixelated architecture. Power tools and a forklift placing blocks. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Minecraft house structure nearly complete — brown cube walls with pixelated stone trim. Square window openings with pixel-style frames. Flat roof made of green blocks (grass block look). A wooden plank-textured door. A small garden area with green cubic bushes shaped like Creeper heads. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Completed Minecraft house with pixel-perfect detail. Green grass-block roof, dirt-block walls, stone foundation. Square windows glow warm from inside. The door is open showing a pixelated interior. A Creeper statue guards the entrance. Torches (real flame LED) line the pathway. Magical blend of digital and real world. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Workers stack large cube blocks forming Minecraft-style walls. Forklift places blocks. Structure grows block by block. Fixed drone angle. 8 seconds.",
            "Rapid construction. Pixel windows installed, green roof blocks placed. Door crafted. Creeper statues built in garden. Workers add details. Fixed camera. 8 seconds.",
            "Cinematic reveal. Torch lights flicker along pathway. Windows glow warm. Door opens showing pixelated interior. Magical blend of Minecraft and reality. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 9. Guitar Swimming Pool ──────────────────────────────────────────────
    {
        "name": "Guitar Shaped Pool",
        "hook": "He Built a Guitar-Shaped Swimming Pool! 🎸💦",
        "title": "Building a GUITAR Pool From Scratch! 🎸🏊",
        "description": "Rock and roll meets swimming! An electric guitar-shaped pool with LED fret markers and a hot tub in the headstock!",
        "hashtags": "#shorts #guitar #pool #construction #timelapse #music #rockandroll",
        "frame_prompts": [
            f"{DRONE_VIEW} at a spacious backyard with trimmed green lawn. Stone patio area near the house. Mature landscaping. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Large guitar-shaped excavation in the lawn — the body is deep pool area, the neck extends outward. Excavator working on the headstock area. Dirt mounds, workers refining the fret board shape. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Guitar pool taking shape — body section tiled in sunburst pattern (dark center, orange edges like a Les Paul). Neck with raised concrete fret markers. Headstock area forming a circular hot tub. Plumbing and LED conduits being installed. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at dusk. Completed guitar pool filled with blue water. LED fret markers glow white along the neck. The body has underwater sunburst lighting. Hot tub in the headstock bubbles. String-shaped water jets cross the neck. Wooden deck surrounds everything. Rock and roll paradise. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Fast construction timelapse. Excavator digs guitar shape. Body deep, neck extends. Workers shape headstock. Fixed drone angle. 8 seconds.",
            "Rapid construction. Sunburst tiles applied to body. Fret markers built along neck. Hot tub formed in headstock. LED conduits installed. Fixed camera. 8 seconds.",
            "Cinematic reveal. Pool fills with water. LED frets glow white. Sunburst underwater lights illuminate. Hot tub bubbles. Dusk lighting. Rock paradise. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 10. Hobbit Hole House ────────────────────────────────────────────────
    {
        "name": "Hobbit Hole House",
        "hook": "He Built a REAL Hobbit House Underground! 🧙‍♂️🏠",
        "title": "Building a Hobbit Hole From Scratch! 🧙‍♂️🌿",
        "description": "Straight from Middle-Earth! A real underground hobbit hole with a round green door, circular windows, and a grass-covered roof!",
        "hashtags": "#shorts #hobbit #lotr #house #construction #timelapse #fantasy",
        "frame_prompts": [
            f"{DRONE_VIEW} at a gentle grassy hillside in a rural setting. Wildflowers, a winding stone path. Rolling green countryside. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Large circular excavation carved into the hillside. Concrete arch framework installed for the tunnel entrance. Workers building stone retaining walls. The circular shape of the hobbit door frame visible. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Structure built into the hillside — stone walls frame a circular entrance. Round wooden door (green, with brass handle) installed. Circular windows on either side. Interior visible — cozy wooden beams. Grass starting to grow back over the earth-covered roof. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at golden hour. Completed hobbit hole — the round green door gleams. Warm light spills from circular windows revealing a cozy interior with a fireplace. Smoke rises from a chimney disguised in the hillside. Flower garden along the stone walkway. Grass fully covers the rounded roof. Magical fairy-tale setting. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Workers carve circular tunnel into hillside. Stone walls rise. Arch framework installed. Fast motion. Fixed drone angle. 8 seconds.",
            "Rapid construction. Round door hung, circular windows installed. Interior beamed. Earth piled back over roof. Grass seed spread. Fixed camera. 8 seconds.",
            "Cinematic reveal. Warm light from windows. Smoke from hidden chimney. Flowers bloom along path. Golden hour magic. A hobbit house come to life. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 11-20: Quick concepts ────────────────────────────────────────────────
    {
        "name": "Dinosaur Playground",
        "hook": "He Built a T-Rex Playground for His Kids! 🦕🎢",
        "title": "Building a DINOSAUR Playground! 🦖🏗️",
        "description": "The world's coolest playground — a life-size T-Rex with slides, climbing walls, and a roaring sound system!",
        "hashtags": "#shorts #dinosaur #playground #construction #timelapse #kids #trex",
        "frame_prompts": [
            f"{DRONE_VIEW} at a large empty park area with flat grass and sandbox. Playground fence around perimeter. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Steel skeleton framework of a massive T-Rex, 8 meters tall. Workers welding limbs. Crane holding the head piece. Foundation poured for the base. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. T-Rex structure covered in green textured panels with realistic scales. Slide running from the mouth. Climbing wall on the belly. Tail is a balance beam. Eyes are windows. Net bridge between legs. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at golden hour. Completed T-Rex playground with kids playing. Green scales shimmer. Slide in use. LED eyes glow red. Soft rubber safety ground beneath. Landscaped with ferns and tropical plants. Epic prehistoric playground. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Crane lifts T-Rex steel skeleton pieces. Workers weld the frame together. Massive dinosaur shape rises. Fixed drone. 8 seconds.",
            "Rapid construction. Green scale panels cover the frame. Slide installed in mouth. Climbing wall built. Safety surface laid. Fixed camera. 8 seconds.",
            "Cinematic reveal. T-Rex playground complete. LED eyes glow. Kids slide and climb. Golden hour through the ferns. Fixed angle. Incredible. 8 seconds.",
        ],
    },
    {
        "name": "Sneaker House",
        "hook": "He Built a LIFE-SIZE Nike Air Jordan House! 👟🏠",
        "title": "Building a Sneaker-Shaped House! 👟🔥",
        "description": "The ultimate sneakerhead dream — a house shaped like a giant Air Jordan 1! Red, white and black exterior with shoelace rope bridge!",
        "hashtags": "#shorts #nike #airjordan #sneakers #construction #timelapse #house",
        "frame_prompts": [
            f"{DRONE_VIEW} at an empty suburban lot with flat terrain. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Foundation and walls rising in the shape of a massive sneaker — sole portion is the ground floor, the upper shoe shape rises 2 stories. Steel framework with curved sections. Workers and crane. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Sneaker house mostly complete — red and white panels on exterior matching Air Jordan 1 colorway. The Nike swoosh window cut into the side. Rubber-textured black sole base. Shoelace-style rope bridge to second floor. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at dusk. Completed sneaker house — iconic red/white/black Air Jordan colorway. Nike swoosh window glows from interior. LED outline traces the shoe shape. Giant shoelace rope bridge illuminated. Modern landscaping. Sneakerhead paradise. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Workers build giant sneaker framework. Curved walls rise. Crane lifts panels. Fast motion. Fixed drone. 8 seconds.",
            "Rapid construction. Red and white Air Jordan panels applied. Swoosh window cut. Rope bridge installed. Black sole textured. Fixed camera. 8 seconds.",
            "Cinematic reveal. Sneaker house lights up at dusk. Swoosh window glows. LED outlines the shoe shape. Rope bridge lit. Fixed angle. Incredible. 8 seconds.",
        ],
    },
]


# ─── Daily concept selection ──────────────────────────────────────────────────

def get_daily_concept() -> dict:
    """Pick a different concept each day based on date hash."""
    day_num = date.today().toordinal()
    idx = day_num % len(TIMELAPSE_CONCEPTS)
    concept = TIMELAPSE_CONCEPTS[idx]
    logger.info(f"🏗️ AImagine timelapse concept: {concept['name']}")
    return concept


# Need logger imported
from core.config import logger
