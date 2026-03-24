"""
AImagine — Viral Loop Concepts (Inspired by @hellopersonality style)

Analysis of @hellopersonality (2.3M followers, 8.2M+ likes):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VIRAL FORMULA:
  1. POV (first-person) immersive experiences
  2. Real → surreal fractal morphing transitions
  3. Neon cyber palette (electric blues, deep purples, neon magentas)
  4. High-velocity movement (driving, cycling, flying)
  5. Hypnotic seamless loops (10-15 seconds)
  6. Minimal captions (1-3 words)

Each concept generates a seamless looping video:
  anchor frame (start = end) → intermediate morphs → forward + reverse = loop
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from datetime import date
from core.config import logger

# ─── Viral Loop Concepts (@hellopersonality style) ─────────────────────────────

LOOP_CONCEPTS = [
    # === POV IMMERSIVE DRIVES (highest viral potential) ===
    {
        "name": "Neon Forest Drive",
        "title": "What you see when dreams drive 🌌",
        "description": "POV neon forest drive #aiart #psychedelic #trippy #viral #shorts",
        "hashtags": "#aiart #psychedelic #fractal #neon #dreamy #trippy #shorts #viral",
        "anchor_prompt": "POV dashcam view driving through a dark forest road at night, "
                         "trees lining both sides, headlights illuminating the path, "
                         "mysterious fog, cinematic 9:16 vertical, photorealistic, 4K",
        "intermediate_prompts": [
            "POV driving through forest as trees begin morphing into glowing neon fractal patterns, "
            "branches transforming into electric blue and purple energy streams, fog turning into "
            "luminescent particles, road surface rippling with bioluminescent waves, 9:16 vertical",

            "POV driving through peak psychedelic forest, trees fully transformed into massive "
            "fractal crystal structures glowing neon magenta and electric teal, the road is a "
            "river of liquid light, entire sky filled with geometric aurora patterns, "
            "particles of light streaming past camera at high speed, 9:16 vertical",

            "POV driving as the fractal world begins dissolving back to reality, glowing patterns "
            "fading into normal trees, neon colors dimming to moonlight, but traces of "
            "luminescence still shimmer on leaves, leading back to the dark forest road, 9:16 vertical",
        ],
        "video_prompts": [
            "Camera moving forward through dark forest road, trees starting to glow and morph, "
            "smooth forward motion, particles appearing, neon colors emerging. 8 seconds.",
            "Fast forward movement through peak psychedelic fractal forest, everything glowing, "
            "light streaks passing camera, hypnotic rhythmic motion. 8 seconds.",
            "Forward movement as fractal world dissolves, colors fading, returning to dark "
            "forest road, smooth deceleration to match starting frame. 8 seconds.",
        ],
    },
    {
        "name": "Cyberpunk City Ride",
        "title": "POV: entering another dimension 🏙️",
        "description": "Cyberpunk city morphing into fractals #aiart #cyberpunk #trippy #shorts",
        "hashtags": "#cyberpunk #neon #aiart #psychedelic #fractal #trippy #shorts",
        "anchor_prompt": "POV motorcycle ride through rainy cyberpunk city street at night, "
                         "neon signs reflecting on wet asphalt, tall buildings on both sides, "
                         "steam rising from manholes, cinematic 9:16 vertical, 4K",
        "intermediate_prompts": [
            "POV motorcycle ride as neon signs begin melting and stretching into fractal patterns, "
            "building facades morphing into geometric crystal structures, rain drops frozen in air "
            "turning into tiny prismatic gems, road surface becoming a mirror of infinite reflections, "
            "9:16 vertical",

            "POV high-speed ride through fully transformed cyber-fractal citywscape, buildings are "
            "towering fractal spires of pure light, sky filled with geometric constellations, "
            "road is a tunnel of neon energy, everything pulsing with electric purple and hot "
            "pink light, motion blur streaks of cyan and magenta, 9:16 vertical",

            "POV ride decelerating as fractal city begins resolving back to neon cyberpunk reality, "
            "crystal structures condensing back into buildings, light patterns dimming to neon signs, "
            "rain resuming, wet asphalt reflecting city lights normally, 9:16 vertical",
        ],
        "video_prompts": [
            "POV forward motorcycle motion through cyberpunk city, neon signs starting to warp and "
            "stretch, rain slowing, reflections intensifying. Smooth acceleration. 8 seconds.",
            "High-speed POV through peak fractal city, everything glowing, light streaks, "
            "geometric patterns flying past, intense hypnotic motion. 8 seconds.",
            "POV decelerating as fractal city dissolves back to normal cyberpunk scene, "
            "colors settling, rain resuming. Smooth transition to starting frame. 8 seconds.",
        ],
    },
    {
        "name": "Ocean Fractal Dive",
        "title": "Diving into another world 🌊",
        "description": "Deep sea morphing into fractal universe #aiart #ocean #trippy #shorts",
        "hashtags": "#ocean #fractal #aiart #psychedelic #underwater #trippy #shorts",
        "anchor_prompt": "POV underwater view just below ocean surface, sunlight filtering through "
                         "crystal clear turquoise water, tiny bubbles rising, calm peaceful scene, "
                         "fish silhouettes in distance, cinematic 9:16 vertical, 4K",
        "intermediate_prompts": [
            "POV diving deeper as water transforms into liquid neon, fish morphing into glowing "
            "fractal creatures made of light, coral becoming crystal geometric formations, "
            "bubbles turning into floating orbs of energy, deep teal and electric blue palette, "
            "9:16 vertical",

            "POV deep in fractal ocean, surrounded by massive bioluminescent fractal jellyfish, "
            "coral reefs of pure geometric crystal glowing neon magenta and gold, light rays "
            "splitting into prismatic fractal patterns, entire ocean is alive with pulsing "
            "mathematical patterns, 9:16 vertical",

            "POV ascending back through fractal ocean as patterns dissolve, creatures fading "
            "back to normal fish shapes, crystals softening to coral, neon dimming to sunlight, "
            "rising toward the surface with normal turquoise water, 9:16 vertical",
        ],
        "video_prompts": [
            "POV diving deeper, water color shifting, fish starting to glow, coral transforming, "
            "smooth downward camera motion. 8 seconds.",
            "POV in deep fractal ocean, surrounded by glowing creatures and crystal formations, "
            "slow circular camera drift, mesmerizing. 8 seconds.",
            "POV rising upward through dissolving fractal ocean, returning to normal water, "
            "sunlight growing brighter, matching starting frame. 8 seconds.",
        ],
    },

    # === NATURE MORPHING (high engagement) ===
    {
        "name": "Aurora Explosion",
        "title": "When the sky breaks open ✨",
        "description": "Northern lights morphing into fractals #aurora #aiart #trippy #shorts",
        "hashtags": "#aurora #northernlights #fractal #aiart #psychedelic #shorts",
        "anchor_prompt": "Wide angle view of snow-covered mountain landscape under dark night sky, "
                         "faint green aurora borealis beginning to appear on horizon, stars visible, "
                         "silhouette of pine trees, peaceful and vast, cinematic 9:16 vertical, 4K",
        "intermediate_prompts": [
            "Same landscape as aurora intensifies dramatically, ribbons of green and purple light "
            "dancing across sky, light reflecting off snow, aurora beginning to form geometric "
            "patterns, stars pulsing brighter, 9:16 vertical",

            "Aurora has fully transformed into massive fractal light show, sky filled with "
            "geometric aurora patterns in neon green, electric purple, and hot pink, mountains "
            "reflecting the colors, snow glowing with bioluminescence, stars replaced by "
            "geometric constellations, 9:16 vertical",

            "Fractal aurora beginning to calm, geometric patterns softening back to natural "
            "aurora ribbons, mountains returning to moonlit silhouettes, stars normalizing, "
            "fading back to the quiet night sky with faint aurora, 9:16 vertical",
        ],
        "video_prompts": [
            "Aurora growing brighter and more active, light ribbons dancing, stars pulsing, "
            "time-lapse feel, smooth upward camera tilt. 8 seconds.",
            "Peak fractal aurora exploding across sky, intense geometric light patterns, "
            "snow pulsing with reflected colors, hypnotic. 8 seconds.",
            "Aurora calming down, fractals dissolving to natural aurora, quiet night returning, "
            "gentle camera settling to original position. 8 seconds.",
        ],
    },
    {
        "name": "Flower Bloom Fractal",
        "title": "Nature's code revealed 🌸",
        "description": "Flowers blooming into fractal universes #flowers #aiart #trippy #shorts",
        "hashtags": "#flowers #fractal #nature #aiart #satisfying #shorts #viral",
        "anchor_prompt": "Extreme close-up macro shot of a closed flower bud with dewdrops, "
                         "soft morning light, shallow depth of field, dark green background "
                         "slightly blurred, cinematic 9:16 vertical, 4K",
        "intermediate_prompts": [
            "Flower bud beginning to open, petals unfurling in slow motion, but each petal "
            "reveals fractal geometric patterns instead of normal veins, dewdrops turning "
            "into tiny prismatic diamonds, soft neon glow emerging from center, 9:16 vertical",

            "Flower fully bloomed into massive fractal structure, each petal a galaxy of "
            "geometric patterns in neon pink, electric purple, and gold, center of flower "
            "is a spiral fractal vortex of light, pollen particles are floating geometric "
            "shapes, entire frame filled with mathematical beauty, 9:16 vertical",

            "Fractal flower beginning to close back up, geometric patterns fading back to "
            "natural flower textures, neon glow dimming to soft morning light, petals "
            "curling back into bud shape, dewdrops reforming, 9:16 vertical",
        ],
        "video_prompts": [
            "Slow macro zoom in as flower bud opens, petals revealing fractal patterns, "
            "dewdrops transforming, soft glow appearing. 8 seconds.",
            "Rotating macro view of fully bloomed fractal flower, geometric patterns pulsing, "
            "light emanating from center, mesmerizing detail. 8 seconds.",
            "Slow zoom out as fractal flower closes, patterns fading, returning to "
            "natural flower bud with dewdrops. 8 seconds.",
        ],
    },

    # === ABSTRACT PSYCHEDELIC (brand signature) ===
    {
        "name": "Tunnel of Consciousness",
        "title": "Where do you go when you close your eyes? 🧠",
        "description": "Flying through a tunnel of consciousness #consciousness #aiart #trippy",
        "hashtags": "#consciousness #fractal #tunnel #aiart #psychedelic #trippy #shorts",
        "anchor_prompt": "POV inside perfectly circular dark tunnel, faint light at the far end, "
                         "smooth metallic walls with subtle reflections, feeling of moving forward, "
                         "cinematic 9:16 vertical, 4K, mysterious atmosphere",
        "intermediate_prompts": [
            "POV accelerating through tunnel as walls begin fracturing into geometric patterns, "
            "cracks filled with neon light, tunnel expanding and contracting rhythmically, "
            "light at the end growing brighter and splitting into prismatic colors, "
            "speed lines appearing, 9:16 vertical",

            "POV at maximum speed through fully psychedelic fractal tunnel, walls are infinite "
            "geometric fractals of electric blue, neon magenta, and gold, tunnel spiraling "
            "and breathing, light patterns streaming past at incredible speed, "
            "feeling of transcendence, 9:16 vertical",

            "POV decelerating through tunnel as fractal patterns simplify, colors dimming, "
            "walls smoothing back to metallic surface, light at end condensing back to "
            "single point, speed reducing to match starting frame, 9:16 vertical",
        ],
        "video_prompts": [
            "POV forward motion accelerating through tunnel, walls starting to crack and glow, "
            "speed increasing, light growing. 8 seconds.",
            "Maximum speed POV through fractal tunnel, everything glowing and spinning, "
            "light streaks, overwhelming visual intensity. 8 seconds.",
            "POV decelerating through tunnel, patterns fading, walls smoothing, "
            "returning to calm dark tunnel. 8 seconds.",
        ],
    },
    {
        "name": "Galaxy Birth Zoom",
        "title": "A universe in a raindrop 💧",
        "description": "Zooming into a raindrop to find a galaxy #galaxy #aiart #trippy #shorts",
        "hashtags": "#galaxy #universe #raindrop #aiart #fractal #trippy #shorts",
        "anchor_prompt": "Single perfect raindrop on a dark glass surface, city lights blurred "
                         "in background bokeh, the raindrop reflecting a miniature world inside, "
                         "moody cinematic lighting, 9:16 vertical, 4K",
        "intermediate_prompts": [
            "Extreme macro zooming into the raindrop, the reflected city inside dissolving into "
            "cosmic nebula patterns, the water surface becoming a window into space, "
            "stars beginning to appear inside the drop, edge of drop glowing neon blue, "
            "9:16 vertical",

            "Fully zoomed into raindrop galaxy — inside is a complete spiral galaxy with "
            "billions of stars, neon nebula clouds in purple and teal, a black hole at center "
            "with gravitational lensing, cosmic dust streaming, all contained within the "
            "spherical boundary of the water drop, 9:16 vertical",

            "Zooming back out from galaxy, stars condensing back to city light reflections, "
            "nebula colors fading to urban neon, raindrop boundary becoming visible again, "
            "returning to the single drop on dark glass, 9:16 vertical",
        ],
        "video_prompts": [
            "Smooth macro zoom into raindrop, reflections dissolving into cosmic patterns, "
            "stars appearing, neon glow emerging. 8 seconds.",
            "Inside the raindrop galaxy, slow spiral rotation, stars and nebula visible, "
            "awe-inspiring cosmic scale. 8 seconds.",
            "Pulling back out of raindrop, galaxy condensing to city reflections, "
            "returning to single drop on glass. 8 seconds.",
        ],
    },

    # === HIGH-VELOCITY IMMERSIVE ===
    {
        "name": "Warp Speed Forest",
        "title": "Warp speed through nature 🌲⚡",
        "description": "Hyperspeed through forest turning psychedelic #forest #warp #shorts",
        "hashtags": "#warp #forest #hyperspeed #aiart #psychedelic #fractal #shorts",
        "anchor_prompt": "POV standing on a forest path, tall redwood trees stretching upward, "
                         "golden sunlight filtering through canopy, green ferns on ground, "
                         "peaceful morning atmosphere, cinematic 9:16 vertical, 4K",
        "intermediate_prompts": [
            "POV bursting forward at incredible speed through forest, trees stretching into "
            "motion blur streaks of green and gold, sunlight shattering into prismatic beams, "
            "ground rushing beneath, fallen leaves spiraling upward in wake, 9:16 vertical",

            "POV hyperspeed through forest as trees transform into columns of pure neon energy, "
            "green replaced by electric blue and magenta, ground is a river of light, canopy "
            "fractals into geometric dome of pulsing patterns, speed lines of every color "
            "streaming past, 9:16 vertical",

            "POV decelerating through forest as neon energy columns soften back to trees, "
            "colors shifting from neon back to natural green and gold, sunlight normalizing, "
            "speed reducing until standing still on the same forest path, 9:16 vertical",
        ],
        "video_prompts": [
            "Sudden acceleration from standstill, trees beginning to blur, sunlight fracturing, "
            "explosive forward motion through forest. 8 seconds.",
            "Maximum hyperspeed through neon fractal forest, everything is streaks of light, "
            "tunnel vision effect, overwhelming speed. 8 seconds.",
            "Rapid deceleration, neon fading to natural colors, trees resolving, slowing to "
            "standstill on the same forest path. 8 seconds.",
        ],
    },
    {
        "name": "Lava River Morphing",
        "title": "When fire becomes art 🔥",
        "description": "Lava flows morphing into fractal light patterns #lava #fire #aiart #shorts",
        "hashtags": "#lava #fire #fractal #aiart #psychedelic #satisfying #shorts",
        "anchor_prompt": "Close-up aerial view of flowing lava river, bright orange and red molten "
                         "rock slowly moving, dark cooled crust cracking to reveal glowing beneath, "
                         "heat shimmer visible, volcanic landscape, cinematic 9:16 vertical, 4K",
        "intermediate_prompts": [
            "Lava flow intensifying, orange glow becoming more electric, cracks in crust forming "
            "geometric patterns like circuit boards, lava surface starting to show fractal "
            "branching patterns in neon orange and gold, heat shimmer becoming prismatic, "
            "9:16 vertical",

            "Lava fully transformed into flowing fractal energy river, the orange replaced by "
            "every neon color — electric blue, magenta, gold, teal — all flowing in mathematical "
            "patterns, cooled surface is obsidian with geometric inlays of light, entire "
            "landscape pulsing with energy, 9:16 vertical",

            "Fractal energy cooling back to natural lava, neon colors warming back to orange "
            "and red, geometric patterns simplifying to natural cracks, heat shimmer returning "
            "to normal, flowing lava river resuming its natural appearance, 9:16 vertical",
        ],
        "video_prompts": [
            "Slow aerial drift over lava, cracks forming geometric patterns, colors intensifying, "
            "heat shimmer growing, smooth camera movement. 8 seconds.",
            "Aerial view of fractal energy lava river, every color flowing in patterns, "
            "pulsing and breathing, mesmerizing aerial drift. 8 seconds.",
            "Fractal energy cooling to normal lava, colors warming, cracks simplifying, "
            "returning to natural flowing lava river. 8 seconds.",
        ],
    },
    {
        "name": "Desert Storm Psychedelic",
        "title": "The desert whispers in colors 🏜️",
        "description": "Sand storm becoming fractal light show #desert #storm #aiart #shorts",
        "hashtags": "#desert #sandstorm #fractal #aiart #psychedelic #trippy #shorts",
        "anchor_prompt": "POV standing in vast desert, golden sand dunes stretching to horizon, "
                         "clear blue sky, single dramatic cloud casting shadow, heat haze visible, "
                         "cinematic 9:16 vertical, 4K, epic landscape",
        "intermediate_prompts": [
            "Sand beginning to lift from dunes in spiraling columns, but instead of brown sand "
            "particles are golden light motes, sky shifting from blue to deep purple, cloud "
            "expanding with neon edges, geometric patterns forming in sand ripples, 9:16 vertical",

            "Full psychedelic desert storm, sand particles are streams of golden fractal light "
            "spiraling upward, sky is deep cosmic purple with geometric constellation patterns, "
            "dunes transformed into waves of flowing neon energy, everything pulsing and "
            "breathing with mathematical precision, 9:16 vertical",

            "Storm calming, fractal light particles settling back as sand grains, sky lightening "
            "from purple back to blue, dunes solidifying, geometric patterns smoothing back to "
            "natural ripples, returning to quiet golden desert, 9:16 vertical",
        ],
        "video_prompts": [
            "Sand beginning to float upward in spirals, sky darkening, colors shifting, "
            "surreal transformation beginning. 8 seconds.",
            "Full psychedelic sand storm, golden light streams, cosmic sky, everything alive "
            "with fractal energy, epic and overwhelming. 8 seconds.",
            "Storm calming, sand settling, sky clearing, colors returning to natural golden "
            "desert under blue sky. 8 seconds.",
        ],
    },

    # === INTIMATE / SATISFYING (high save-rate) ===
    {
        "name": "Crystal Cave Discovery",
        "title": "Found this in a dream.. 💎",
        "description": "Exploring crystal cave that becomes alive #crystals #cave #aiart #shorts",
        "hashtags": "#crystals #cave #fractal #aiart #satisfying #dreamy #shorts",
        "anchor_prompt": "POV entering a dark cave, flashlight beam revealing massive amethyst "
                         "crystal formations on walls, purple reflections, dripping water, "
                         "mysterious and beautiful, cinematic 9:16 vertical, 4K",
        "intermediate_prompts": [
            "POV deeper in cave as crystals begin glowing from within, no flashlight needed, "
            "amethyst pulsing with inner purple light, new crystal colors appearing — teal, "
            "gold, magenta — water droplets frozen mid-air like gems, cave walls starting to "
            "show fractal geometric growth patterns, 9:16 vertical",

            "POV in heart of fractal crystal cave, massive crystals of every neon color growing "
            "in real-time following geometric patterns, walls are living fractal structures, "
            "ceiling is a dome of prismatic light, ground covered in luminescent crystal garden, "
            "everything glowing and pulsing rhythmically, 9:16 vertical",

            "POV as crystal cave activity slows, colors dimming, crystals shrinking back to "
            "natural amethyst size, glow fading to flashlight illumination, water drops "
            "resuming fall, returning to natural crystal cave entrance, 9:16 vertical",
        ],
        "video_prompts": [
            "POV walking deeper into cave, crystals beginning to glow, colors emerging, "
            "flashlight becoming unnecessary, wonderment. 8 seconds.",
            "Inside fractal crystal heart, everything growing and glowing, slow 360 camera "
            "drift, overwhelming beauty. 8 seconds.",
            "Crystals dimming and shrinking, cave returning to natural state, flashlight "
            "cone reappearing, backing toward entrance. 8 seconds.",
        ],
    },
    {
        "name": "Snow to Stardust",
        "title": "When snowflakes become stars ❄️✨",
        "description": "Falling snow transforming into stardust #snow #stardust #aiart #shorts",
        "hashtags": "#snow #stardust #stars #aiart #fractal #satisfying #dreamy #shorts",
        "anchor_prompt": "Close-up slow motion of snowflakes falling against dark sky background, "
                         "each flake visible with crystalline detail, soft bokeh lights in "
                         "background, gentle peaceful snowfall, cinematic 9:16 vertical, 4K",
        "intermediate_prompts": [
            "Snowflakes growing larger and more geometric, each one becoming a perfect fractal "
            "crystal with inner glow, background bokeh transforming into star clusters, "
            "some flakes connected by threads of light, air shimmering with energy, 9:16 vertical",

            "Each snowflake is now a glowing fractal star, falling upward instead of down, "
            "background is deep space nebula in neon purple and teal, the flakes/stars trail "
            "light as they rise, creating a river of stardust flowing upward, "
            "entire frame is a cascade of ascending light, 9:16 vertical",

            "Stardust slowing and beginning to fall back down, glowing fractal shapes simplifying "
            "back to hexagonal snowflakes, nebula background fading to dark sky with bokeh, "
            "normal gentle snowfall resuming, peaceful and quiet, 9:16 vertical",
        ],
        "video_prompts": [
            "Snowflakes growing more geometric and glowing, background transforming, "
            "slow motion getting slower, magical. 8 seconds.",
            "Fractal star-flakes rising upward through nebula, trailing light, river of "
            "ascending stardust, breathtaking cosmic beauty. 8 seconds.",
            "Stars slowing and falling back down as snowflakes, nebula fading to night sky, "
            "peaceful snowfall returning. 8 seconds.",
        ],
    },
]


def get_daily_concept() -> dict:
    """Select today's concept based on date, avoiding recent repeats."""
    today = date.today()
    day_num = today.toordinal()
    idx = day_num % len(LOOP_CONCEPTS)

    concept = LOOP_CONCEPTS[idx]
    logger.info(f"🔁 AImagine concept: {concept['name']}")
    return concept
