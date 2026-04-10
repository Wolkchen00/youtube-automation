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

    # ─── 13. Giant Basketball Court ───────────────────────────────────────────
    {
        "name": "Basketball Shaped Pool",
        "hook": "He Built a BASKETBALL-Shaped Pool with Real Hoops! 🏀💦",
        "title": "Building a BASKETBALL Pool! 🏀🏊",
        "description": "The ultimate sports fan pool — shaped like a giant basketball with real hoops on each end! Orange tiles and black line details!",
        "hashtags": "#shorts #basketball #pool #construction #timelapse #nba #sports",
        "frame_prompts": [
            f"{DRONE_VIEW} at a large flat backyard with green grass. Sports equipment shed visible. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Circular excavation in the lawn forming a giant basketball shape. Workers marking the curved line patterns. Excavator digging. Dirt piles around. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Pool structure taking shape — orange mosaic tiles covering the interior. Black line details matching basketball seam pattern. Two basketball hoops being installed at opposite ends. Concrete deck forming around. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at golden hour. Completed basketball pool filled with crystal water. Orange LED glow from underwater. Black seam lines perfectly visible. Two hoops with nets. Wooden deck with bleacher seating. Sports paradise. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Fast construction timelapse. Excavator digs circular basketball shape. Workers mark seam lines. Earth removed rapidly. Fixed drone angle. 8 seconds.",
            "Rapid construction. Orange tiles applied in basketball pattern. Black seam lines laid. Hoops installed. Deck built. Fixed camera. 8 seconds.",
            "Cinematic reveal. Pool fills with water. Orange LEDs illuminate. Hoops gleam. Golden hour light reflects off water. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 14. Giant Camera House ───────────────────────────────────────────────
    {
        "name": "Camera Shaped Studio",
        "hook": "He Built a Studio Shaped Like a GIANT Camera! 📷🏠",
        "title": "Building a CAMERA-Shaped Photography Studio! 📷✨",
        "description": "A photographer's dream — an entire studio shaped like a massive DSLR camera with a lens-shaped entrance and viewfinder rooftop terrace!",
        "hashtags": "#shorts #camera #photography #construction #timelapse #studio #creative",
        "frame_prompts": [
            f"{DRONE_VIEW} at an empty commercial lot. Flat concrete ground. Chain link fence around perimeter. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Foundation poured in rectangular camera body shape. A cylindrical structure rising for the lens section. Steel framework. Crane positioning roof pieces. Workers welding. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Camera studio 80% complete — matte black exterior panels. The cylindrical lens entrance has concentric glass rings. A raised viewfinder bump on top forms a rooftop terrace. Flash unit shaped chimney. Grip texture on sides. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at blue hour. Completed camera studio glowing. Lens entrance lit with concentric LED rings. Viewfinder terrace has warm lighting. Red recording light on top blinks. Interior visible through lens — professional photography studio with lights. Stunning. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Fast construction timelapse. Foundation poured. Cylindrical lens structure rises. Steel frame assembled. Crane lifts pieces. Fixed drone. 8 seconds.",
            "Rapid construction. Black panels applied. Glass lens rings installed. Viewfinder terrace built. Flash chimney erected. Fixed camera. 8 seconds.",
            "Cinematic reveal. Lens LED rings glow concentric circles. Red light blinks. Studio interior visible. Blue hour atmosphere. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 15. Coca-Cola Can Pool ───────────────────────────────────────────────
    {
        "name": "Coca-Cola Can Pool",
        "hook": "He Built a GIANT Coca-Cola Can Swimming Pool! 🥤💦",
        "title": "Building a COCA-COLA Can Pool! 🥤🏊",
        "description": "The most refreshing pool ever — shaped like a massive Coca-Cola can with the iconic red and white design! Complete with a bubble jacuzzi!",
        "hashtags": "#shorts #cocacola #pool #construction #timelapse #satisfying #iconic",
        "frame_prompts": [
            f"{DRONE_VIEW} at a backyard space with trimmed lawn and patio area. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Large cylindrical excavation in the yard. Workers building curved concrete walls. The circular shape clearly defined. Rebar visible. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Cylindrical pool taking shape — red mosaic tiles on exterior walls visible above ground. White wave stripe being applied. Workers installing the pull-tab shaped diving platform at one end. Interior blue tiles. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at dusk. Completed Coca-Cola can pool — iconic red with white swirl stripe. Pull-tab diving board. Bubble jets create fizzing effect. Red LED underglow. Silver rim at top edge. Landscaped with tropical plants. Refreshing paradise. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Fast construction timelapse. Workers dig cylindrical pool. Curved walls rise. Rebar framework. Fixed drone angle. 8 seconds.",
            "Rapid construction. Red tiles applied. White stripe painted. Pull-tab platform built. Interior finished blue. Fixed camera. 8 seconds.",
            "Cinematic reveal. Pool fills. Bubble jets fizz. Red LED glow. Pull-tab diving board gleams. Dusk lighting. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 16. Football Stadium Pool ────────────────────────────────────────────
    {
        "name": "Football Stadium Pool",
        "hook": "He Built a Mini Football Stadium Pool in His Yard! ⚽🏟️",
        "title": "Building a FOOTBALL STADIUM Pool! ⚽💦",
        "description": "A miniature football stadium with a real pool as the field! Terraced seating, floodlights, and goal posts included!",
        "hashtags": "#shorts #football #stadium #pool #construction #timelapse #soccer",
        "frame_prompts": [
            f"{DRONE_VIEW} at a large backyard with flat terrain. Wide open space. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Rectangular excavation with stepped terracing on all sides. Workers building concrete bleacher forms. The field area deepens for the pool. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Stadium taking shape — green artificial turf tiles on terraces. White lane markings in pool floor. Goal nets at each end. Four floodlight poles being erected at corners. Miniature scoreboard. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at night. Completed mini stadium — floodlights blaze white. Pool glows blue with painted pitch lines underwater. Goal nets stand at each end. Green terraces with tiny spectator figures. Scoreboard lit. Electric atmosphere. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Fast construction. Rectangular pit dug with terraced steps. Concrete poured for bleachers. Field area deepens. Fixed drone. 8 seconds.",
            "Rapid construction. Green turf on terraces. White lines painted. Goals erected. Floodlight poles installed. Fixed camera. 8 seconds.",
            "Cinematic reveal. Floodlights blaze on. Pool fills with blue water. Pitch lines glow underwater. Night atmosphere. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 17. Giant Donut Shop ─────────────────────────────────────────────────
    {
        "name": "Giant Donut Shop",
        "hook": "He Built a Shop Inside a GIANT Donut! 🍩🏠",
        "title": "Building a GIANT DONUT Shop! 🍩✨",
        "description": "The sweetest building ever — a donut shop built inside a massive donut with sprinkle decorations and a glazed roof!",
        "hashtags": "#shorts #donut #shop #construction #timelapse #food #creative",
        "frame_prompts": [
            f"{DRONE_VIEW} at a small commercial corner lot. Sidewalk and street visible. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Circular torus-shaped steel framework rising. Workers bending steel into the donut ring shape. The hole in the center will be the entrance. Foundation poured. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Donut structure covered in smooth pink panels (strawberry glaze). Colorful sprinkle-shaped decorations being attached to exterior. The center hole serves as a walk-through entrance. Glass display windows cut. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at golden hour. Completed giant donut shop — glossy pink glaze exterior with rainbow sprinkles. Warm golden light from interior shows display cases of donuts. Neon 'OPEN' sign glowing. Small outdoor seating with donut-shaped chairs. Sweet paradise. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Steel bent into donut torus shape. Framework rises circular. Workers weld. Fixed drone angle. 8 seconds.",
            "Rapid construction. Pink panels applied. Sprinkle decorations attached. Windows installed. Interior fitted. Fixed camera. 8 seconds.",
            "Cinematic reveal. Neon sign glows. Interior lights warm. Sprinkles shimmer in golden hour. Donut chairs placed. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 18. Shark Aquarium House ─────────────────────────────────────────────
    {
        "name": "Shark Aquarium House",
        "hook": "He Built a House with a SHARK TUNNEL Inside! 🦈🏠",
        "title": "Building a SHARK Aquarium House! 🦈💦",
        "description": "Living with sharks! A house with an actual walk-through shark tunnel aquarium as the main hallway!",
        "hashtags": "#shorts #shark #aquarium #house #construction #timelapse #ocean",
        "frame_prompts": [
            f"{DRONE_VIEW} at a beachfront lot with sandy terrain. Ocean visible in background. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Modern house foundation with a unique glass tunnel structure running through the center. Workers installing thick acrylic panels. Filtration equipment visible. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. House structure rising around the central aquarium tunnel. White modern walls, flat roof. The glass tunnel visible from above — thick acrylic filled with blue water. Filtration room built adjacent. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at dusk. Completed beach house with sharks visible through the glass tunnel from above. Blue aquarium glow emanates from the center. Modern white exterior lit warmly. Ocean waves in background. Tropical landscaping. Incredible fusion of architecture and marine life. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Foundation poured with glass tunnel channel. Acrylic panels craned in. Workers seal joints. Fixed drone. 8 seconds.",
            "Rapid construction. Walls rise around tunnel. Roof completed. Water fills tunnel blue. House finished white. Fixed camera. 8 seconds.",
            "Cinematic reveal. Sharks swim in glowing blue tunnel. House glows warm. Ocean backdrop at dusk. Fixed angle. Breathtaking. 8 seconds.",
        ],
    },

    # ─── 19. Giant Headphones Pavilion ────────────────────────────────────────
    {
        "name": "Headphones Music Pavilion",
        "hook": "He Built a GIANT Headphones Music Stage! 🎧🎶",
        "title": "Building GIANT Headphones Music Stage! 🎧🔥",
        "description": "The ultimate music venue — a stage shaped like massive headphones! The ear cups are performance areas with LED sound visualizers!",
        "hashtags": "#shorts #headphones #music #construction #timelapse #stage #dj",
        "frame_prompts": [
            f"{DRONE_VIEW} at an open field area. Flat ground with grass. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Two circular foundation areas connected by a curved arch structure. Workers building the headband arch. Scaffolding around the ear cup foundations. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Headphones structure taking shape — two large circular ear cup stages with padded exterior texture. The curved headband arch connecting them at 8 meters high. Speaker grille pattern on inner walls. Sound equipment visible. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at night. Completed headphones stage — RGB LED rings on both ear cups pulse with color. Sound waves visualized on inner grille panels. The headband arch has chasing lights. DJ booth in one ear cup, seating in the other. Fog effects. Epic music venue. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Two circular stages built. Arch headband structure rises connecting them. Scaffolding up. Fixed drone. 8 seconds.",
            "Rapid construction. Ear cup panels applied. Speaker grille pattern cut. Sound equipment installed. Headband completed. Fixed camera. 8 seconds.",
            "Cinematic reveal. RGB LEDs pulse on ear cups. Sound visualizer animations. Chasing lights on headband. Fog rolls. Night magic. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 20. Rolex Watch Pool ─────────────────────────────────────────────────
    {
        "name": "Rolex Watch Pool",
        "hook": "He Built a ROLEX-Shaped Swimming Pool! ⌚💦",
        "title": "Building a ROLEX Watch Pool! ⌚🏊",
        "description": "Luxury meets swimming! A pool shaped like a Rolex Submariner with a rotating bezel hot tub and gold-tiled hour markers!",
        "hashtags": "#shorts #rolex #luxury #pool #construction #timelapse #watches",
        "frame_prompts": [
            f"{DRONE_VIEW} at a luxury estate backyard. Manicured lawn, stone pathways. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Large circular excavation with an outer ring channel for the bezel. Workers building the dial area deeper. Hour marker positions staked. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Watch pool taking shape — circular main pool with raised bezel rim. Gold mosaic tiles at hour marker positions. Black dial-colored tiles in center area. Crown winder shaped hot tub at 3 o'clock position. Cyclops lens over date window. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at dusk. Completed Rolex pool — green bezel rim lit with emerald LEDs. Gold hour markers glow. Black dial center with luminous hands pattern underwater. Crown hot tub bubbles. Luxury deck with loungers. Diamond-like stars above. Opulent paradise. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Fast construction. Circular pool with outer bezel ring excavated. Workers build layers. Gold markers placed. Fixed drone. 8 seconds.",
            "Rapid construction. Green bezel tiles applied. Gold hour markers installed. Black dial tiles laid. Crown hot tub built. Fixed camera. 8 seconds.",
            "Cinematic reveal. Emerald bezel LEDs glow. Gold markers illuminate. Crown hot tub bubbles. Luxury dusk atmosphere. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 21. Rocket Ship Playhouse ────────────────────────────────────────────
    {
        "name": "Rocket Ship Playhouse",
        "hook": "He Built a 10-Meter ROCKET SHIP in His Backyard! 🚀🏠",
        "title": "Building a ROCKET SHIP Playhouse! 🚀✨",
        "description": "3... 2... 1... Liftoff! A massive rocket-shaped playhouse with spiral slide, observation deck, and LED flame exhaust!",
        "hashtags": "#shorts #rocket #space #playhouse #construction #timelapse #kids",
        "frame_prompts": [
            f"{DRONE_VIEW} at a spacious backyard with green lawn. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Cylindrical steel framework rising 10 meters tall. Workers on scaffolding welding sections. Nose cone frame at top. Fin structures at base. Concrete foundation. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Rocket structure covered in white and red panels. Nose cone completed. Circular windows along the body. Spiral slide wrapping around exterior. Three fin stabilizers at base. Door at ground level. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at dusk. Completed rocket — white with red trim, stars painted on. Observation deck windows glow warm from inside. Spiral slide gleams. LED flame effect at exhaust nozzle flickers orange and red. American flag decal. Landscaped with astro-turf moon surface. Epic. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Fast construction. Cylindrical tower rises. Scaffolding and welding. Nose cone lifted by crane. Fins welded at base. Fixed drone. 8 seconds.",
            "Rapid construction. White panels applied. Red trim painted. Spiral slide installed. Windows cut. Fins finished. Fixed camera. 8 seconds.",
            "Cinematic reveal. LED exhaust flames flicker. Windows glow. Slide gleams in dusk light. Stars appear above the rocket. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 22. Diamond Ring Fountain ────────────────────────────────────────────
    {
        "name": "Diamond Ring Fountain",
        "hook": "He Built a GIANT Diamond Ring Fountain! 💍💦",
        "title": "Building a DIAMOND RING Fountain! 💎✨",
        "description": "The most romantic fountain ever — a massive diamond engagement ring with water cascading from the diamond and LED-lit band!",
        "hashtags": "#shorts #diamond #ring #fountain #construction #timelapse #luxury",
        "frame_prompts": [
            f"{DRONE_VIEW} at a public park plaza with stone pavement. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Circular foundation poured for the ring base. A curved steel arch rising for the band. Workers welding the prong setting structure at the top for the diamond. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Ring structure nearly complete — polished silver-chrome panels on the band. Crystal glass diamond shape at top held in prong settings. Water pipes running through the band to the diamond. Basin pool around the base. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at blue hour. Completed diamond ring fountain — chrome band gleams. Crystal diamond refracts colored LED light creating rainbow projections. Water cascades from the diamond down the band into the circular pool. Underwater lights shimmer. Romantic paradise. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Circular base poured. Chrome arch band rises. Prong settings welded at top. Fixed drone. 8 seconds.",
            "Rapid construction. Chrome panels applied to band. Crystal diamond mounted in prongs. Water pipes installed. Basin tiled. Fixed camera. 8 seconds.",
            "Cinematic reveal. Water cascades from diamond. Rainbow LED refractions. Chrome band gleams. Blue hour magic. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 23. Sushi Restaurant ─────────────────────────────────────────────────
    {
        "name": "Giant Sushi Roll Restaurant",
        "hook": "He Built a Restaurant Inside a GIANT Sushi Roll! 🍣🏠",
        "title": "Building a GIANT SUSHI Restaurant! 🍣🔥",
        "description": "Itadakimasu! A restaurant shaped like a massive maki sushi roll with nori walls, rice texture exterior, and salmon-colored roof!",
        "hashtags": "#shorts #sushi #restaurant #japan #construction #timelapse #food",
        "frame_prompts": [
            f"{DRONE_VIEW} at a commercial street corner lot. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Cylindrical framework rising horizontally. Workers building the roll shape. Dark green exterior panels (nori seaweed) being attached to the lower half. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Sushi roll structure taking shape — dark green nori wrap exterior on bottom half. White rice-textured upper panels. Cross-section entrance reveals colorful interior zones (salmon pink, avocado green, cucumber). Chopstick-shaped sign posts. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at golden hour. Completed sushi roll restaurant — nori exterior gleams. Cross-section entrance glows with warm light showing colorful interior. Giant chopsticks sign. Japanese lanterns along walkway. Bonsai trees flanking entrance. Appetizing and incredible. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Cylindrical horizontal framework built. Dark nori panels applied. Workers shape the roll. Fixed drone. 8 seconds.",
            "Rapid construction. Rice texture panels on top. Colorful interior sections built. Chopstick signs erected. Fixed camera. 8 seconds.",
            "Cinematic reveal. Cross-section entrance glows warm. Japanese lanterns light up. Bonsai trees placed. Golden hour glow. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 24. Piano Pool ───────────────────────────────────────────────────────
    {
        "name": "Grand Piano Pool",
        "hook": "He Built a GRAND PIANO Swimming Pool! 🎹💦",
        "title": "Building a PIANO-Shaped Pool! 🎹🏊",
        "description": "Music meets water! A grand piano-shaped pool with black and white key steps, string-pattern lane dividers, and a lid-shaped sun shade!",
        "hashtags": "#shorts #piano #music #pool #construction #timelapse #luxury",
        "frame_prompts": [
            f"{DRONE_VIEW} at an estate backyard with a stone terrace. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Grand piano shaped excavation — the curved body for the main pool, the keyboard section stepped for a wading area. Workers refining the distinctive piano curves. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Piano pool structure complete — glossy black tiles on the body, alternating black and white steps at the keyboard end. Gold string-pattern lights running lengthwise. A curved shade structure mimicking an open piano lid. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at dusk. Completed piano pool — glossy black body reflects the sky. White and black key steps cascade into the water. Gold string lights glow underwater. Piano lid shade has ambient lighting. Classical music notes projected in light on the deck. Elegant paradise. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Fast construction. Piano curve excavated. Keyboard steps formed. Workers shape the distinctive outline. Fixed drone. 8 seconds.",
            "Rapid construction. Black tiles applied to body. White key steps installed. Gold strings placed. Lid shade erected. Fixed camera. 8 seconds.",
            "Cinematic reveal. Water fills the piano. Gold strings glow. Key steps shimmer. Lid shade illuminates. Dusk elegance. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 25. Submarine Underwater Room ────────────────────────────────────────
    {
        "name": "Submarine Underwater Room",
        "hook": "He Built an UNDERWATER Submarine Room! 🚢🌊",
        "title": "Building an UNDERWATER Submarine Room! 🚢💦",
        "description": "Dive deep! An underground room shaped like a submarine hull with porthole windows looking into a surrounding aquarium!",
        "hashtags": "#shorts #submarine #underwater #construction #timelapse #ocean #room",
        "frame_prompts": [
            f"{DRONE_VIEW} at a backyard with a digging site marked out. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Deep rectangular excavation. Workers building a submarine hull-shaped steel frame inside the pit. Waterproofing membrane being applied. Drainage pipes visible. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Submarine hull installed underground — grey military-style exterior with rivets. Round porthole windows. Periscope tube rising above ground. Surrounding pit being filled with water and aquarium glass walls. Hatch entrance on top. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at dusk. Completed submarine room — periscope rises above a glass-enclosed water feature. Through the glass you can see the submarine hull with glowing porthole windows. Fish swimming in the surrounding water. Hatch entrance lit. Above ground looks like a mini naval base. Incredible engineering. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Deep pit dug. Submarine hull frame assembled inside. Waterproofing applied. Fixed drone. 8 seconds.",
            "Rapid construction. Grey hull panels attached. Portholes installed. Periscope tube rises. Aquarium glass walls placed. Fixed camera. 8 seconds.",
            "Cinematic reveal. Portholes glow blue underwater. Fish swim around hull. Periscope rises above. Hatch illuminated. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 26. Baseball Glove Dugout ────────────────────────────────────────────
    {
        "name": "Baseball Glove Dugout",
        "hook": "He Built a GIANT Baseball Glove Dugout! ⚾🧤",
        "title": "Building a BASEBALL GLOVE Dugout! ⚾✨",
        "description": "Play ball! A dugout shaped like a massive baseball glove catching a real-size baseball! Leather texture exterior and stitching details!",
        "hashtags": "#shorts #baseball #sports #construction #timelapse #dugout #mlb",
        "frame_prompts": [
            f"{DRONE_VIEW} at the edge of a baseball field diamond. Green grass, dirt infield visible. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Curved framework rising in the shape of an open baseball glove. Workers bending steel ribs to form the finger sections. A large sphere framework for the baseball in the pocket area. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Glove structure covered in brown leather-textured panels. Visible stitching lines. The baseball in the pocket is a white dome with red stitching. Dugout seating inside the palm area. Webbing between fingers is mesh netting. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at golden hour. Completed baseball glove dugout — rich brown leather texture gleaming. Red stitching details perfect. White baseball dome glows with interior lights. Players sitting in the palm area dugout. American flag nearby. Field lights warming up. Classic Americana. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Curved finger framework rises. Steel bent into glove shape. Baseball sphere framework built. Fixed drone. 8 seconds.",
            "Rapid construction. Brown leather panels applied. Stitching details added. White baseball dome finished. Dugout seating installed. Fixed camera. 8 seconds.",
            "Cinematic reveal. Leather glove gleams in golden light. Baseball dome glows. Dugout lit warmly. Field lights turn on. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 27. Gaming Controller Pool ───────────────────────────────────────────
    {
        "name": "Gaming Controller Pool",
        "hook": "He Built a GIANT Xbox Controller Pool! 🎮💦",
        "title": "Building a GAMING CONTROLLER Pool! 🎮🏊",
        "description": "Game on! A swimming pool shaped like a massive gaming controller with button-shaped hot tubs and joystick fountains!",
        "hashtags": "#shorts #gaming #xbox #pool #construction #timelapse #gamer",
        "frame_prompts": [
            f"{DRONE_VIEW} at a flat backyard with plenty of space. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Controller-shaped excavation — main body pool with bumper grip extensions. Four circular pits for buttons at right end. Two deeper circles for joystick areas. Workers refining shapes. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Controller pool taking shape — dark grey tiles on the body. Four button circles tiled in A(green) B(red) X(blue) Y(yellow). Joystick areas have rotating fountain mechanisms. D-pad shaped wading area. Xbox logo center. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at night. Completed controller pool — body lit with dark ambient glow. A/B/X/Y buttons are illuminated hot tubs in their signature colors. Joystick fountains spin water in circles. Xbox logo glows green center. RGB LED strips outline everything. Ultimate gamer paradise. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Fast construction. Controller shape excavated. Button circles and joystick areas dug. Fixed drone angle. 8 seconds.",
            "Rapid construction. Grey tiles on body. Colored button tiles applied. Joystick mechanisms installed. Xbox logo placed. Fixed camera. 8 seconds.",
            "Cinematic reveal. Buttons glow their colors. Joystick fountains spin. Xbox logo green. RGB outlines. Night magic. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 28. Whale Playground ─────────────────────────────────────────────────
    {
        "name": "Blue Whale Playground",
        "hook": "He Built a BLUE WHALE Playground for Kids! 🐳🎢",
        "title": "Building a BLUE WHALE Playground! 🐋✨",
        "description": "The ocean's gentle giant as the world's coolest playground! Kids slide through the whale's mouth and climb the tail fin!",
        "hashtags": "#shorts #whale #playground #ocean #construction #timelapse #kids",
        "frame_prompts": [
            f"{DRONE_VIEW} at a beachside park area. Sand and grass visible. Ocean in background. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Massive steel framework in whale shape — 15 meters long. Workers building the ribcage structure. Tail fin frame rises at one end. Mouth opening at the other. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Whale covered in blue textured panels — darker on top, lighter on belly. Baleen filter slide in the mouth. Blowhole climbing tower on top. Tail fin climbing wall. Flipper-shaped benches. Water spray features along the back. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at golden hour. Completed blue whale playground — majestic blue body gleams. Kids sliding through the mouth. Water sprays from the blowhole. Tail fin casting dramatic shadow. Ocean waves in background perfectly framing the scene. Magical marine playground. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Whale ribcage framework rises. Tail fin welded. Workers shape the massive body. Fixed drone. 8 seconds.",
            "Rapid construction. Blue panels cover the whale. Slide installed in mouth. Blowhole tower built. Water features added. Fixed camera. 8 seconds.",
            "Cinematic reveal. Water sprays from blowhole. Kids play on slides. Blue whale gleams in golden light. Ocean behind. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 29. Drum Set Hot Tub ─────────────────────────────────────────────────
    {
        "name": "Drum Set Hot Tubs",
        "hook": "He Built HOT TUBS Shaped Like a Drum Set! 🥁💦",
        "title": "Building DRUM SET Hot Tubs! 🥁🔥",
        "description": "Rock and relax! A collection of hot tubs shaped like a complete drum kit — bass drum, toms, snare, and cymbal shower heads!",
        "hashtags": "#shorts #drums #music #hottub #construction #timelapse #rockstar",
        "frame_prompts": [
            f"{DRONE_VIEW} at a rooftop terrace of a modern building. Flat concrete deck. City skyline in background. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Multiple circular excavations on the rooftop in drum kit arrangement — one large (bass drum), two medium (rack toms), one medium (floor tom), one small (snare). Workers waterproofing. Cymbal-shaped structures on poles. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Drum kit hot tubs taking shape — bass drum (large red tub), rack toms (blue tubs), floor tom (green), snare (chrome). Drumstick-shaped water jets between tubs. Cymbal-shaped shower heads on tall poles. Chrome hardware connecting everything. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at night. Completed drum set hot tubs — each drum glows its color from underwater LEDs. Steam rises from hot water. Cymbal showers spray water catching the light. Chrome hardware gleams. City skyline sparkles behind. Drumstick jets arc water between tubs. Rock star retreat. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Multiple circular tubs dug on rooftop. Waterproofing applied. Cymbal poles erected. Fixed drone. 8 seconds.",
            "Rapid construction. Colored drum panels applied. Chrome hardware installed. Drumstick jets positioned. Cymbal showers mounted. Fixed camera. 8 seconds.",
            "Cinematic reveal. Drums glow with color LEDs. Steam rises. Cymbal showers sparkle. City skyline behind. Night magic. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 30. Volcano Hot Spring ───────────────────────────────────────────────
    {
        "name": "Volcano Hot Spring Pool",
        "hook": "He Built a VOLCANO with a Hot Spring INSIDE! 🌋💦",
        "title": "Building a VOLCANO Hot Spring! 🌋🔥",
        "description": "Nature's fury meets relaxation! A realistic volcano structure with a hot spring pool inside the crater and lava-flow water slides!",
        "hashtags": "#shorts #volcano #hotspring #pool #construction #timelapse #nature",
        "frame_prompts": [
            f"{DRONE_VIEW} at a resort-like backyard with tropical landscaping. Palm trees, stone pathways. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Workers building a conical mountain structure from stone and concrete. About 6 meters tall. Crater depression at top. Channels carved down the sides for lava slides. Pump room built inside. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Volcano structure rendered with realistic volcanic rock texture. Dark grey and brown. Orange-painted channels (lava flows) zigzag down sides forming water slides. Crater at top has a pool being tiled. Steam vents installed. Tropical plants growing on lower slopes. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at dusk. Completed volcano — realistic craggy rock exterior. The crater pool steams with warm turquoise water. Orange LED lava flows cascade down the sides as water slides. Steam jets periodically erupt from vents. Tropical garden surrounds the base. Fire torches along pathways. A volcanic paradise. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Stone volcano built layer by layer. Workers stack rocks. Crater forms at top. Channels carved. Fixed drone. 8 seconds.",
            "Rapid construction. Rock texture panels applied. Lava channels painted orange. Crater pool tiled. Steam vents installed. Plants placed. Fixed camera. 8 seconds.",
            "Cinematic reveal. Crater steams turquoise. Orange lava slides cascade water. Steam erupts from vents. Fire torches flicker. Dusk magic. Fixed angle. 8 seconds.",
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # ABANDONED TO LUXURY — Inspired by @rebornspacestv (376K, 212M views)
    # Format: Ruined/abandoned space → excavation → construction → luxury reveal
    # ══════════════════════════════════════════════════════════════════════════

    # ─── 31. Abandoned Pool → Luxury Resort ──────────────────────────────────
    {
        "name": "Abandoned Pool to Luxury Resort",
        "hook": "From ABANDONED to LUXURY in 24 seconds! 🏚️→🏊",
        "title": "He Turned an ABANDONED Pool Into PARADISE! 🏊✨",
        "description": "Watch this incredible transformation from a ruined, overgrown pool into an ultra-luxury resort pool with infinity edge and underwater lighting!",
        "hashtags": "#shorts #abandoned #luxury #pool #transformation #renovation #satisfying",
        "frame_prompts": [
            f"{DRONE_VIEW} at an abandoned overgrown backyard. A cracked, empty swimming pool filled with debris, leaves, and green algae. Broken tiles, rusty ladder.  Weeds growing through concrete. Abandoned deck furniture tipped over. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Workers have cleared the debris. Excavator deepening the pool. Old tiles jackhammered out. Fresh concrete being poured for new walls. Rebar visible. Construction crew active. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Pool structure rebuilt — smooth infinity edge on one side. White marble tiles being installed. Underwater LED tracks visible. A jacuzzi section added. Modern wooden deck framing around. Plumbing complete. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at golden hour. Completed luxury resort pool — crystal turquoise water with infinity edge overlooking the garden. Underwater LED strips glow warm. Jacuzzi bubbles. Fire bowls on deck corners. Tropical plants, loungers with white cushions. From ruin to paradise. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Workers clear debris from abandoned pool. Excavator removes old concrete. Pool deepens. Fast motion. Fixed drone. 8 seconds.",
            "Rapid construction. New concrete walls, marble tiles applied. Infinity edge built. LED tracks installed. Workers move fast. Fixed camera. 8 seconds.",
            "Cinematic reveal. Pool fills with turquoise water. LED lights glow. Fire bowls ignite. Infinity edge overflows. Golden hour magic. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 32. Ruined Basement → Underground Cinema ────────────────────────────
    {
        "name": "Basement to Underground Cinema",
        "hook": "From FLOODED Basement to CINEMA ROOM! 🎬🍿",
        "title": "He Turned a RUINED Basement Into a HOME CINEMA! 🎬✨",
        "description": "From a dark, flooded basement to the ultimate underground home cinema with a 200-inch screen, recliner seats, and starlight ceiling!",
        "hashtags": "#shorts #basement #cinema #hometheater #transformation #renovation #luxury",
        "frame_prompts": [
            f"{DRONE_VIEW} at a dark, flooded basement. Standing water on the concrete floor. Exposed pipes, peeling paint, mold on walls. A single bare bulb swinging. Debris and old boxes. Depressing and abandoned. {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Basement drained and partially demolished. Workers waterproofing walls with membrane. New concrete floor poured. Electrical conduits routed for screen and sound. Framing for stepped floor visible. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Cinema room taking shape — dark acoustic panels on walls. A massive 200-inch screen frame mounted. Stepped platform for 3 rows of seating. Ceiling being fitted with fiber optic starlight panels. Sound equipment racks on side walls. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Completed home cinema — luxurious dark velvet walls with LED accent strips. Massive screen showing a vivid movie scene. Three rows of leather recliners with cupholders. Fiber optic ceiling creates a starfield. Ambient purple LED lighting. Popcorn machine glowing in the corner. Absolute luxury. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Workers pump water out, demolish old walls. Waterproofing applied. New floor poured. Fast motion. Fixed angle. 8 seconds.",
            "Rapid construction. Acoustic panels installed. Screen mounted. Recliners placed. Starlight ceiling fitted. Workers move fast. Fixed camera. 8 seconds.",
            "Cinematic reveal. Screen powers on with vivid image. LED accents glow purple. Starlight ceiling twinkles. Recliners ready. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 33. Empty Rooftop → Sky Garden Pool ─────────────────────────────────
    {
        "name": "Rooftop to Sky Garden",
        "hook": "He Turned an EMPTY Rooftop Into a SKY GARDEN! 🌿🏊",
        "title": "From BORING Rooftop to SKY GARDEN Paradise! 🌿✨",
        "description": "An empty concrete rooftop transformed into a stunning sky garden with a plunge pool, vertical garden walls, and a sunset lounge!",
        "hashtags": "#shorts #rooftop #skygarden #pool #transformation #luxury #city",
        "frame_prompts": [
            f"{DRONE_VIEW} at a bare concrete rooftop. Grey, flat, empty. AC units and water tanks. No greenery. City skyline in background. Boring and utilitarian. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Workers installing raised planter beds and waterproof membrane. Small plunge pool excavation framed. Vertical garden framework on walls. Electrical and plumbing roughed in. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Sky garden taking shape — lush vertical green walls, wooden deck flooring, plunge pool tiled in dark stone tiles. Pergola frame with retractable shade. Built-in outdoor kitchen counter. Ambient lighting conduits. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at sunset. Completed sky garden paradise — lush vertical walls of tropical plants. Small plunge pool glows turquoise. Pergola with warm string lights. Outdoor kitchen with grill. Cozy lounge furniture. City skyline glowing in sunset behind. Breathtaking urban oasis. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Workers install planter beds. Pool frame built. Vertical garden mounted. Deck laid. Fast motion. Fixed drone. 8 seconds.",
            "Rapid construction. Plants fill vertical walls. Pool tiled. Pergola raised. Kitchen built. String lights hung. Fixed camera. 8 seconds.",
            "Cinematic reveal. Pool glows turquoise. String lights sparkle. Vertical garden lush green. Sunset skyline behind. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 34. Old Garage → Smart Home Studio ──────────────────────────────────
    {
        "name": "Garage to Smart Home Studio",
        "hook": "From DIRTY Garage to SMART HOME! 🏠💡",
        "title": "He Turned a MESSY Garage Into a SMART HOME! 🏠✨",
        "description": "A cluttered, oil-stained garage transformed into a futuristic smart home studio with voice control, LED walls, and automated furniture!",
        "hashtags": "#shorts #garage #smarthome #transformation #renovation #technology #luxury",
        "frame_prompts": [
            f"{DRONE_VIEW} at a cluttered two-car garage. Oil-stained concrete floor. Rusty shelves with junk. Old workbench covered in tools. Spider webs. A broken garage door. Messy and forgotten. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Garage cleared out. Workers installing insulation in walls. New concrete floor poured smooth. Electrical panels upgraded. Smart home wiring conduits running everywhere — speakers, screens, sensors. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Smart home studio taking shape — clean white walls with embedded LED strip channels. A Murphy bed folding unit against one wall. Drop-down projector and screen. Motorized storage cabinets. Kitchen nook with smart appliances. Polished concrete floor with radiant heating. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at blue hour. Completed smart home — LED wall strips glow in customizable colors. Murphy bed is stowed away revealing a living room. Projector displays a large screen. Voice-activated lights transition colors. Kitchen appliances gleam. Minimalist and futuristic. The garage door is now a modern glass wall. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Garage cleared. Insulation, wiring, and smart conduits installed. Floor poured. Fast motion. Fixed drone. 8 seconds.",
            "Rapid construction. White walls finished. Murphy bed installed. Projector mounted. Smart appliances placed. Fixed camera. 8 seconds.",
            "Cinematic reveal. LED walls glow colors. Projector activates. Glass wall reveals blue hour sky. Futuristic smart home. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 35. Backyard → Japanese Zen Garden ──────────────────────────────────
    {
        "name": "Backyard to Zen Garden",
        "hook": "OVERGROWN Backyard → JAPANESE Zen Garden! 🎋🪷",
        "title": "From JUNGLE Backyard to ZEN GARDEN Paradise! 🎋✨",
        "description": "An overgrown, weedy backyard transformed into a serene Japanese zen garden with koi pond, bamboo water feature, and stone pathways!",
        "hashtags": "#shorts #zengarden #japanese #backyard #transformation #peaceful #satisfying",
        "frame_prompts": [
            f"{DRONE_VIEW} at a neglected overgrown backyard. Knee-high weeds, dead grass patches, fallen tree branches. A broken old fence. Scattered trash. Wild and unkempt. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Ground cleared completely. Workers excavating a koi pond shape. Gravel being spread and raked. Large boulders being positioned. Bamboo screening installed along the perimeter. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Zen garden 80% complete — raked white gravel with concentric circle patterns. Natural stone stepping path. Koi pond with waterfall rocks. Bamboo water feature (shishi-odoshi). Small red bridge over pond. Japanese maple trees planted. Wooden bench area. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at golden hour. Completed Japanese zen garden — perfectly raked white gravel circles. Koi fish visible in crystal clear pond. Bamboo water feature clicks rhythmically. Red bridge reflects in water. Japanese lanterns glow softly along the stone path. Cherry blossom tree petals on the ground. Absolute serenity. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Overgrown weeds cleared. Gravel spread. Koi pond excavated. Boulders positioned. Fast motion. Fixed drone. 8 seconds.",
            "Rapid construction. White gravel raked in circles. Stone path laid. Red bridge built. Trees planted. Lanterns placed. Fixed camera. 8 seconds.",
            "Cinematic reveal. Koi swim in clear pond. Bamboo feature clicks. Lanterns glow. Cherry blossoms float. Golden serenity. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 36. Abandoned Warehouse → Loft Apartment ────────────────────────────
    {
        "name": "Warehouse to Luxury Loft",
        "hook": "ABANDONED Warehouse → $2M LOFT! 🏚️→🏠",
        "title": "From ABANDONED Warehouse to LUXURY LOFT! 🏗️✨",
        "description": "A decaying industrial warehouse transformed into a stunning luxury loft apartment with exposed brick, mezzanine bedroom, and floor-to-ceiling windows!",
        "hashtags": "#shorts #warehouse #loft #luxury #transformation #renovation #architecture",
        "frame_prompts": [
            f"{DRONE_VIEW} at an abandoned industrial warehouse. Broken windows, graffiti on walls, rusted metal roof. Pigeons nesting. Weeds growing through cracked floor. Dark and eerie interior visible. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Warehouse being gutted. New steel beams reinforcing structure. Floor-to-ceiling window frames installed. Mezzanine floor framing in progress. Exposed brick walls cleaned and sealed. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Loft taking shape — open plan living with exposed brick walls. Polished concrete floors. Industrial-style kitchen island. Mezzanine bedroom with glass railings. Spiral staircase. Large windows flooding light in. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at blue hour. Completed luxury loft — warm ambient lighting. Exposed brick glows in candlelight. Floor-to-ceiling windows reflect city lights. Mezzanine bedroom cozy with soft lighting. Designer furniture. Art on walls. Potted plants. Industrial meets luxury perfection. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Warehouse gutted. Steel beams installed. Windows framed. Mezzanine built. Fast motion. Fixed drone. 8 seconds.",
            "Rapid construction. Brick cleaned. Concrete polished. Kitchen installed. Staircase built. Furniture placed. Fixed camera. 8 seconds.",
            "Cinematic reveal. Warm lights glow. City reflects in windows. Mezzanine cozy. Brick and steel harmony. Blue hour. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 37. Muddy Lot → Luxury Outdoor Kitchen ─────────────────────────────
    {
        "name": "Mud Lot to Outdoor Kitchen",
        "hook": "From MUD PIT to LUXURY Outdoor Kitchen! 🍳🔥",
        "title": "He Turned a MUD LOT Into an EPIC Outdoor Kitchen! 🍳✨",
        "description": "A muddy empty lot transformed into the ultimate outdoor kitchen with stone pizza oven, grill station, bar seating, and a fire pit!",
        "hashtags": "#shorts #outdoorkitchen #bbq #transformation #renovation #luxury #cooking",
        "frame_prompts": [
            f"{DRONE_VIEW} at a bare muddy lot. Puddles, tire tracks in mud, no grass. A pile of old bricks. Flat and depressing. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Workers laying stone foundation. Post holes for pergola. Pizza oven dome being built with firebricks. Grill counter framework rising. Gas and water lines being run. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Outdoor kitchen taking shape — natural stone countertops with built-in gas grill and side burner. Brick pizza oven dome completed. U-shaped bar with stone base and teak bar top. Pergola frame up. Fire pit circle dug. Stone paver flooring laid. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at dusk. Completed outdoor kitchen — warm glow from pizza oven fire. Gas grill ignited. Bar stools along teak counter. String lights under pergola. Fire pit crackling in center of seating area. Stone pavers gleam. Potted herbs on counter. Ultimate hosting setup. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Foundation laid. Pizza oven dome rises brick by brick. Grill counter framed. Fixed drone. 8 seconds.",
            "Rapid construction. Stone counters placed. Pergola built. Fire pit dug. Bar stools placed. Pavers laid. Fixed camera. 8 seconds.",
            "Cinematic reveal. Pizza oven fire glows. Grill flames. String lights sparkle. Fire pit crackles. Dusk warmth. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 38. Broken Shed → Cozy Tiny Home ────────────────────────────────────
    {
        "name": "Shed to Cozy Tiny Home",
        "hook": "BROKEN Shed → COZY Tiny Home! 🏚️→🏡",
        "title": "He Turned a BROKEN SHED Into a Tiny Home! 🏡✨",
        "description": "A collapsing garden shed transformed into a charming tiny home with a loft bed, mini kitchen, and a covered porch!",
        "hashtags": "#shorts #tinyhouse #shed #transformation #renovation #cozy #diy",
        "frame_prompts": [
            f"{DRONE_VIEW} at a dilapidated garden shed. Rotting wood panels, sagging roof, door hanging off hinges. Overgrown ivy climbing up. Rusty tools scattered around. Too small to even enter. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Shed demolished. New foundation poured slightly larger. Workers framing walls with treated lumber. Roof trusses going up. Everything new and sturdy. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Tiny home structure nearly complete — cedar shake exterior. A covered front porch with railing. Bay window on one side. Small chimney pipe. Interior visible through windows — loft bed platform, mini kitchen cabinetry. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at golden hour. Completed tiny home — warm cedar exterior with white trim. Covered porch with two chairs and a lantern. Bay window glows warm from interior. Smoke wisps from chimney. Flower boxes under windows. Stone pathway leading to it. String lights on porch. Fairy-tale cottage beauty. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Old shed demolished. New foundation and walls rise. Roof trusses up. Fast motion. Fixed drone. 8 seconds.",
            "Rapid construction. Cedar panels applied. Porch built. Windows installed. Interior visible — loft and kitchen done. Fixed camera. 8 seconds.",
            "Cinematic reveal. Porch light glows. Smoke from chimney. String lights sparkle. Flower boxes bloom. Golden hour fairy tale. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 39. Cracked Patio → Luxury Lounge ───────────────────────────────────
    {
        "name": "Patio to Luxury Lounge",
        "hook": "CRACKED Patio → LUXURY Lounge Area! 👑✨",
        "title": "From CRACKED PATIO to LUXURY Lounge! 👑🔥",
        "description": "A crumbling concrete patio transformed into a luxury outdoor lounge with L-shaped sofa, fire table, water feature, and mood lighting!",
        "hashtags": "#shorts #patio #luxury #lounge #transformation #renovation #outdoor",
        "frame_prompts": [
            f"{DRONE_VIEW} at a cracked concrete patio. Large cracks with weeds growing through. Faded, stained concrete. Rusty patio furniture. A dead potted plant. Adjacent to house. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Workers jackhammering old concrete. New gravel base being leveled. Drainage system installed. Large format tile layout marked. Electrical conduits for lighting. Water supply for feature. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Luxury lounge taking shape — large format dark stone tiles. L-shaped built-in concrete bench with waterproof cushion slots. Fire table in center. Linear water feature along one wall. Planters with ornamental grasses. Step lighting installed. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at dusk. Completed luxury lounge — dark tiles gleam. L-shaped sofa with plush white cushions. Fire table dancing with orange flame. Water feature cascading with LED blue glow. Step lights create pathway. Ornamental grasses sway. Wine glasses on fire table. Premium outdoor living. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Old concrete demolished. New base leveled. Tiles laid in pattern. Fire table base built. Fast motion. Fixed drone. 8 seconds.",
            "Rapid construction. Dark tiles placed. Bench built. Water feature installed. Planters filled. Step lights wired. Fixed camera. 8 seconds.",
            "Cinematic reveal. Fire table ignites. Water feature glows blue. Step lights guide path. White cushions placed. Dusk luxury. Fixed angle. 8 seconds.",
        ],
    },

    # ─── 40. Forgotten Courtyard → Secret Garden ─────────────────────────────
    {
        "name": "Courtyard to Secret Garden",
        "hook": "FORGOTTEN Courtyard → SECRET GARDEN! 🌸🗝️",
        "title": "From ABANDONED Courtyard to SECRET GARDEN! 🌸✨",
        "description": "A forgotten, weed-covered courtyard transformed into a magical secret garden with fountain, climbing roses, and fairy lights!",
        "hashtags": "#shorts #garden #secretgarden #courtyard #transformation #magical #flowers",
        "frame_prompts": [
            f"{DRONE_VIEW} at a neglected enclosed courtyard. High walls covered in dead ivy. Cracked stone floor strewn with debris. A broken birdbath in the center. Rusty iron gate. Everything grey and lifeless. {LIGHTING} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Workers repairing stone floor. Old birdbath removed, new fountain base being built. Walls cleaned, trellis structures mounted. Garden beds excavated. Iron gate restored and repainted. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW}. Secret garden forming — restored stone pathways with moss growing between. Central tiered fountain with running water. Climbing roses on trellises cover the walls. Lavender beds, boxwood hedges. Iron gate painted glossy black. Archway covered in wisteria. {CONSISTENCY} {CAMERA_NOTE}",
            f"{DRONE_VIEW} at golden hour. Completed secret garden — roses climb the walls in full bloom. Tiered fountain sparkles. Fairy lights woven through the wisteria archway. Lavender and jasmine scent-implied by lush growth. Butterflies visible. Iron gate inviting. Cobblestone path glows. Enchanted paradise. {CONSISTENCY} {CAMERA_NOTE}",
        ],
        "video_prompts": [
            "Construction timelapse. Dead ivy removed. Walls cleaned. Fountain base built. Trellis mounted. Garden beds dug. Fixed drone. 8 seconds.",
            "Rapid construction. Stone paths laid. Roses planted on trellis. Fountain tiers stacked. Hedges placed. Archway built. Fixed camera. 8 seconds.",
            "Cinematic reveal. Fountain sparkles. Roses bloom on walls. Fairy lights glow. Butterflies flutter. Golden garden magic. Fixed angle. 8 seconds.",
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
    HISTORY_FILE.write_text(json.dumps(recent[-100:], ensure_ascii=False), encoding="utf-8")

    logger.info(f"🏗️ AImagine concept: {chosen['name']} (pool: {len(available)}/{len(TIMELAPSE_CONCEPTS)} available)")
    return chosen

