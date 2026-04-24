"""
AImagine — DIY Crafts Fixed-Camera Concepts
Inspired by @diycraftstvofficial (5.2M IG, 319K YT)
Format: 4 frames (empty → progress → more progress → finished) → 3 clips → ~24s
Fixed tripod camera, 1-2 workers, satisfying transformation
"""

import random
import json
from datetime import date
from .prompts import BASE_STYLE, PERSON_STYLE, VIDEO_STYLE, GARDEN_ENV, BACKYARD_ENV, FRONTYARD_ENV, INDOOR_ENV, OUTDOOR_DINING_ENV, LUXURY_ENV

# Short helpers
F = lambda desc, env: f"{BASE_STYLE}. {desc}. {env}. {PERSON_STYLE}"
V = VIDEO_STYLE

DIY_CONCEPTS = [
    # 1
    {"name": "Front Yard Landscaping Transformation",
     "hook": "Front yard landscaping transformation 🌿✨",
     "title": "Front Yard Landscaping Transformation 🌿",
     "description": "Watch this incredible front yard go from bare dirt to a stunning landscaped garden!",
     "hashtags": "#shorts #landscaping #garden #transformation #diy #satisfying",
     "frame_prompts": [
         F("Bare dirt front yard with dead grass patches, a person in dark work clothes standing surveying the empty yard, wheelbarrow and garden tools nearby", FRONTYARD_ENV),
         F("Same yard, person kneeling planting small shrubs along the walkway, fresh soil turned over, some plants already in ground, bags of mulch open", FRONTYARD_ENV),
         F("Same yard now half-finished, person spreading mulch around planted bushes, flower bed taking shape with colorful flowers, stone edging partially laid", FRONTYARD_ENV),
         F("Stunning finished front yard, lush green lawn, colorful flower beds with roses and lavender, stone pathway, decorative lighting, manicured hedges, golden hour light", FRONTYARD_ENV),
     ],
     "video_prompts": [V + ". Person raking dirt and preparing soil in front yard. Timelapse speed. 8 seconds.",
                       V + ". Person planting flowers and shrubs, spreading mulch. Garden taking shape. 8 seconds.",
                       V + ". Final landscaping touches, watering new plants, yard transforming to lush garden. 8 seconds."]},
    # 2
    {"name": "Backyard Pergola Lounge Build",
     "hook": "Building a dream backyard pergola lounge 🏡☀️",
     "title": "Backyard Pergola Lounge Build 🏡",
     "description": "Empty backyard transformed into a stunning pergola lounge with outdoor furniture and string lights!",
     "hashtags": "#shorts #pergola #backyard #diy #build #outdoor #satisfying",
     "frame_prompts": [
         F("Empty grass backyard, two people measuring and marking ground with stakes and string, wooden beams and tools laid out on grass", BACKYARD_ENV),
         F("Same backyard, two people building wooden pergola frame, vertical posts already up, one person on ladder attaching horizontal beam", BACKYARD_ENV),
         F("Same backyard, pergola frame complete, one person hanging white outdoor curtains on one side, outdoor rug being rolled out underneath", BACKYARD_ENV),
         F("Beautiful finished pergola lounge, white curtains flowing in breeze, cozy outdoor sofa with throw pillows, coffee table, string lights overhead glowing warmly, potted plants around, evening atmosphere", BACKYARD_ENV),
     ],
     "video_prompts": [V + ". Two people digging post holes and raising wooden pergola posts. Construction timelapse. 8 seconds.",
                       V + ". Attaching pergola beams overhead, frame taking shape. Fast motion building. 8 seconds.",
                       V + ". Adding curtains, furniture, string lights. Bare pergola becoming cozy lounge. 8 seconds."]},
    # 3
    {"name": "Tulip Garden Border Makeover",
     "hook": "Backyard border turned into stunning tulip garden 🌷",
     "title": "Backyard Border → Stunning Tulip Garden 🌷",
     "description": "A neglected backyard border transformed into a breathtaking tulip garden paradise!",
     "hashtags": "#shorts #tulips #garden #makeover #flowers #satisfying #spring",
     "frame_prompts": [
         F("Neglected weedy garden border along wooden fence, one person pulling weeds by hand, pile of weeds nearby, bare muddy soil showing", BACKYARD_ENV),
         F("Same border cleared of weeds, person kneeling planting tulip bulbs in neat rows, bags of bulbs and bone meal beside them, soil freshly turned", BACKYARD_ENV),
         F("Same border with green tulip shoots emerging from soil, person adding decorative stone edging along the border, mulch being spread", BACKYARD_ENV),
         F("Magnificent tulip garden in full bloom, hundreds of red yellow pink and purple tulips in rows, neat stone edging, fresh mulch, butterflies, golden sunlight", BACKYARD_ENV),
     ],
     "video_prompts": [V + ". Person clearing weeds from garden border, turning soil. Timelapse gardening. 8 seconds.",
                       V + ". Planting tulip bulbs in rows, covering with soil and mulch. Satisfying planting. 8 seconds.",
                       V + ". Tulips growing and blooming in timelapse, garden coming alive with color. 8 seconds."]},
    # 4
    {"name": "Living Room Complete Makeover",
     "hook": "Empty room to dream living room ✨🛋️",
     "title": "Room Makeover From Start to Finish ✨",
     "description": "An empty white room transformed into a cozy modern living room with stunning decor!",
     "hashtags": "#shorts #roommakeover #interiordesign #homedecor #transformation #satisfying",
     "frame_prompts": [
         F("Completely empty white room with hardwood floor, person standing with paint roller looking at blank walls, paint cans and drop cloths on floor", INDOOR_ENV),
         F("Same room, walls painted warm sage green, person assembling a modern gray sectional sofa in center of room, packaging materials around", INDOOR_ENV),
         F("Same room, sofa in place with throw pillows, person hanging large abstract art on wall, floating shelves already mounted with books and plants", INDOOR_ENV),
         F("Stunning finished living room, sage green walls, gray sectional with cozy throw blankets, gallery wall art, floating shelves with plants and books, warm rug, floor lamp glowing, coffee table with candles, cozy evening light through windows", INDOOR_ENV),
     ],
     "video_prompts": [V + ". Person painting walls with roller, transforming white room. Satisfying paint strokes. 8 seconds.",
                       V + ". Assembling furniture, placing sofa, rolling out rug. Room taking shape. 8 seconds.",
                       V + ". Adding final decor touches, art, plants, lighting up. Cozy room reveal. 8 seconds."]},
    # 5
    {"name": "Outdoor Kitchen Build",
     "hook": "Building an outdoor kitchen from scratch 🍳🔥",
     "title": "Outdoor Kitchen Build Complete 🍳",
     "description": "A bare patio transformed into a fully functional outdoor kitchen with grill, counter, and bar seating!",
     "hashtags": "#shorts #outdoorkitchen #diy #build #grill #patio #satisfying",
     "frame_prompts": [
         F("Bare concrete patio, two people laying concrete blocks in L-shape for kitchen base, bags of mortar, level tool, trowel in use", OUTDOOR_DINING_ENV),
         F("Same patio, block base built, one person applying stone veneer to front of counter, other person dry-fitting granite countertop slab", OUTDOOR_DINING_ENV),
         F("Same patio, stone counter complete with granite top, person installing built-in gas grill into counter opening, sink being connected", OUTDOOR_DINING_ENV),
         F("Beautiful finished outdoor kitchen, stone veneer counter with granite top, built-in grill with flames, bar stools, pendant lights hanging from pergola above, tropical plants, evening ambiance with string lights", OUTDOOR_DINING_ENV),
     ],
     "video_prompts": [V + ". Two people laying concrete blocks and building counter base. Construction timelapse. 8 seconds.",
                       V + ". Applying stone veneer and placing granite countertop. Kitchen taking form. 8 seconds.",
                       V + ". Installing grill, adding bar stools, lighting string lights. Kitchen comes alive. 8 seconds."]},
    # 6
    {"name": "Topiary Peacock Garden",
     "hook": "Creating a giant peacock topiary garden 🦚🌿",
     "title": "Luxury Topiary Garden Transformation 🦚",
     "description": "An ordinary hedge transformed into a magnificent peacock topiary with stunning tail display!",
     "hashtags": "#shorts #topiary #peacock #garden #art #satisfying #luxury",
     "frame_prompts": [
         F("Overgrown untrimmed hedge bushes in garden, person with large hedge shears beginning to shape the bush, wire topiary frame leaning nearby", GARDEN_ENV),
         F("Same bushes, wire peacock frame now placed over the hedge, person using electric trimmer to shape body section, rough bird shape emerging", GARDEN_ENV),
         F("Same area, peacock body well shaped, person carefully hand-trimming tail feather detail, fan tail shape spreading out beautifully", GARDEN_ENV),
         F("Magnificent completed peacock topiary in full display, perfectly shaped green body and dramatic fan tail, surrounded by manicured lawn and flower beds, golden hour light casting long shadows", GARDEN_ENV),
     ],
     "video_prompts": [V + ". Person trimming and shaping hedge into rough peacock form. Satisfying cutting. 8 seconds.",
                       V + ". Detailed shaping of peacock tail feathers, leaves flying. Artistry timelapse. 8 seconds.",
                       V + ". Final trimming touches, stepping back to reveal magnificent peacock topiary. 8 seconds."]},
    # 7
    {"name": "Japanese Zen Garden Creation",
     "hook": "Creating a Japanese zen garden from nothing 🪨🌸",
     "title": "Japanese Zen Garden Created From Scratch 🪨",
     "description": "An empty corner transformed into a serene Japanese zen garden with raked gravel, stone lantern, and bonsai!",
     "hashtags": "#shorts #zengarden #japanese #garden #peaceful #satisfying #diy",
     "frame_prompts": [
         F("Empty dirt corner of garden, person laying down landscape fabric, wheelbarrow with white gravel nearby, wooden border pieces stacked", GARDEN_ENV),
         F("Same corner, wooden border installed, person spreading white gravel and raking it into circular zen patterns with traditional wooden rake", GARDEN_ENV),
         F("Same corner, raked gravel base done, person carefully placing large natural stones in asymmetric grouping, small bamboo fountain being positioned", GARDEN_ENV),
         F("Serene finished zen garden, perfectly raked white gravel with circular patterns, three moss-covered stones, bamboo water fountain trickling, stone lantern, small Japanese maple tree, bonsai on stone pedestal, peaceful morning mist", GARDEN_ENV),
     ],
     "video_prompts": [V + ". Person laying fabric and spreading white gravel. Zen garden foundation. 8 seconds.",
                       V + ". Raking beautiful circular patterns in gravel, placing stones. Meditative timelapse. 8 seconds.",
                       V + ". Adding bamboo fountain, lantern, bonsai. Tranquil garden completing. 8 seconds."]},
    # 8
    {"name": "Patio Fire Pit Lounge",
     "hook": "Dream patio fire pit lounge in one day ☀️🔥",
     "title": "Patio Transformation in One Day ☀️",
     "description": "A bare backyard corner transformed into a cozy fire pit lounge with stone seating and ambient lighting!",
     "hashtags": "#shorts #firepit #patio #lounge #diy #outdoor #cozy #satisfying",
     "frame_prompts": [
         F("Bare grass area in backyard, person using spray paint to mark a large circle on grass, pile of flagstones and fire pit ring nearby", BACKYARD_ENV),
         F("Same area, grass removed in circle, person laying flagstones in circular pattern, fire pit ring placed in center, gravel being spread between stones", BACKYARD_ENV),
         F("Same area, flagstone patio complete, person building curved stone bench around one side, another person placing outdoor cushions on completed section", BACKYARD_ENV),
         F("Gorgeous finished fire pit lounge at dusk, crackling fire in stone ring, curved stone bench with plush cushions and throw blankets, lanterns and string lights glowing, marshmallow roasting sticks, wine glasses on stone side table, warm cozy atmosphere", BACKYARD_ENV),
     ],
     "video_prompts": [V + ". Person removing grass and laying flagstone patio in circle. Foundation work. 8 seconds.",
                       V + ". Building fire pit ring and stone seating bench. Structure rising. 8 seconds.",
                       V + ". Adding cushions, lighting fire, string lights turning on. Cozy evening reveal. 8 seconds."]},
    # 9
    {"name": "Vertical Herb Wall Kitchen",
     "hook": "DIY vertical herb garden on kitchen wall 🌿🍳",
     "title": "Kitchen Herb Wall Garden Build 🌿",
     "description": "A blank kitchen wall transformed into a beautiful living vertical herb garden!",
     "hashtags": "#shorts #herbgarden #vertical #kitchen #diy #plants #satisfying",
     "frame_prompts": [
         F("Blank white kitchen wall next to window, person holding up wooden pallet frame measuring for placement, drill and mounting hardware on counter", INDOOR_ENV),
         F("Same wall, wooden frame mounted, person attaching small terracotta pots into frame slots using metal rings, row of empty pots mounted", INDOOR_ENV),
         F("Same wall, all pots mounted in grid pattern, person carefully planting herb seedlings — basil rosemary thyme mint — into each pot, soil on counter", INDOOR_ENV),
         F("Beautiful finished herb wall, lush green herbs growing in terracotta pots on wooden frame, hand-written chalkboard labels on each pot, small LED grow light strip above, kitchen counter below with cutting board and fresh herbs being used for cooking", INDOOR_ENV),
     ],
     "video_prompts": [V + ". Person mounting wooden frame and pot holders on kitchen wall. Building structure. 8 seconds.",
                       V + ". Planting herb seedlings into each pot, filling wall with green. Satisfying planting. 8 seconds.",
                       V + ". Herbs growing lush, person picking fresh basil for cooking. Living wall complete. 8 seconds."]},
    # 10
    {"name": "Luxury Rose Archway Garden",
     "hook": "Building a dreamy rose archway in the garden 🌹✨",
     "title": "Dream Rose Archway Garden Build 🌹",
     "description": "A plain garden path transformed with a stunning climbing rose archway entrance!",
     "hashtags": "#shorts #roses #archway #garden #romantic #diy #satisfying",
     "frame_prompts": [
         F("Plain garden path between flower beds, person assembling white metal arch frame at the entrance, tools and ties on the ground", GARDEN_ENV),
         F("Same path, white metal arch installed and anchored, person planting climbing rose bushes at each base of the arch, fresh soil mounded", GARDEN_ENV),
         F("Same path, rose bushes growing up the arch with green vines, person carefully training and tying rose canes to arch frame with garden twine", GARDEN_ENV),
         F("Breathtaking finished rose archway, hundreds of pink and white climbing roses covering the entire arch in full bloom, petals scattered on stone path below, late afternoon golden light filtering through blooms, enchanting fairy-tale garden entrance", GARDEN_ENV),
     ],
     "video_prompts": [V + ". Person assembling and installing white metal garden arch. Building framework. 8 seconds.",
                       V + ". Planting roses at base, training vines up the arch. Growth timelapse. 8 seconds.",
                       V + ". Roses blooming and covering entire arch, petals falling. Magical reveal. 8 seconds."]},
    # 11
    {"name": "Backyard Pond and Waterfall",
     "hook": "Building a backyard pond with waterfall 💧🌿",
     "title": "DIY Backyard Pond & Waterfall Build 💧",
     "description": "Digging and building a beautiful backyard pond with a natural stone waterfall from scratch!",
     "hashtags": "#shorts #pond #waterfall #backyard #diy #water #satisfying",
     "frame_prompts": [
         F("Person digging kidney-shaped hole in backyard with shovel, dirt piled to one side, garden hose marking the outline shape", BACKYARD_ENV),
         F("Same area, hole dug and lined with black pond liner, person stacking natural stones around the edge and building up waterfall rock formation at one end", BACKYARD_ENV),
         F("Same area, stones in place, person positioning pond pump and filling with water from hose, water starting to trickle over waterfall rocks", BACKYARD_ENV),
         F("Stunning finished backyard pond with crystal clear water, natural stone waterfall cascading, water lilies floating, koi fish swimming, lush ferns and ornamental grasses planted around edges, subtle underwater LED lights glowing, peaceful evening scene", BACKYARD_ENV),
     ],
     "video_prompts": [V + ". Person digging pond shape, removing soil. Earth moving timelapse. 8 seconds.",
                       V + ". Laying liner, stacking stones, building waterfall formation. 8 seconds.",
                       V + ". Water filling pond, waterfall flowing, fish released. Living pond reveal. 8 seconds."]},
    # 12
    {"name": "Outdoor Movie Theater Setup",
     "hook": "DIY outdoor movie theater in the backyard 🎬🍿",
     "title": "Backyard Movie Theater Setup 🎬",
     "description": "Transforming a backyard into a magical outdoor movie theater with projector screen and cozy seating!",
     "hashtags": "#shorts #outdoormovie #backyard #diy #movienight #cozy #satisfying",
     "frame_prompts": [
         F("Empty backyard lawn, person hammering wooden frame posts into ground for projector screen, white sheet fabric draped over arm", BACKYARD_ENV),
         F("Same yard, white screen stretched on wooden frame, person laying out thick outdoor blankets and large floor cushions in rows on the grass", BACKYARD_ENV),
         F("Same yard, seating arranged, person hanging mason jar lights on string between poles, small projector on table being aimed at screen", BACKYARD_ENV),
         F("Magical outdoor movie theater at night, large white screen with movie playing, cozy blankets and cushions with people silhouettes, mason jar string lights glowing warmly, popcorn bowls, starry sky above, dreamy atmosphere", BACKYARD_ENV),
     ],
     "video_prompts": [V + ". Building screen frame and stretching white fabric. Setup timelapse. 8 seconds.",
                       V + ". Laying blankets, cushions, hanging string lights. Cozy setup. 8 seconds.",
                       V + ". Projector turning on, lights dimming, movie starting under stars. Magic reveal. 8 seconds."]},
    # 13
    {"name": "Bathroom Spa Renovation",
     "hook": "Old bathroom to luxury spa retreat 🧖✨",
     "title": "Bathroom Spa Renovation Complete 🧖",
     "description": "A dated bathroom completely renovated into a serene luxury spa-like retreat!",
     "hashtags": "#shorts #bathroom #renovation #spa #luxury #homedecor #satisfying",
     "frame_prompts": [
         F("Dated bathroom with old tiles being demolished, person using pry bar to remove old wall tiles, debris on floor, protective sheets down", INDOOR_ENV),
         F("Same bathroom stripped bare, person applying thin-set mortar and laying new large format white marble tiles on wall, tile spacers visible", INDOOR_ENV),
         F("Same bathroom, marble tiles grouted, person installing modern rainfall showerhead and brushed gold fixtures, freestanding white tub being positioned", INDOOR_ENV),
         F("Stunning finished spa bathroom, floor-to-ceiling white marble, freestanding soaking tub, rainfall shower with glass partition, brushed gold fixtures, eucalyptus hanging from showerhead, candles lit, fluffy white towels, warm ambient lighting, steam wisps", INDOOR_ENV),
     ],
     "video_prompts": [V + ". Person demolishing old tiles, stripping bathroom bare. Demolition timelapse. 8 seconds.",
                       V + ". Laying marble tiles, installing fixtures. Renovation progress. 8 seconds.",
                       V + ". Adding final touches, candles lit, steam rising. Spa bathroom reveal. 8 seconds."]},
    # 14
    {"name": "Raised Garden Bed Vegetable Plot",
     "hook": "Building raised garden beds for vegetables 🥕🌱",
     "title": "Raised Bed Vegetable Garden Build 🥕",
     "description": "Empty yard corner transformed into a productive raised bed vegetable garden!",
     "hashtags": "#shorts #raisedbed #vegetablegarden #gardening #diy #grow #satisfying",
     "frame_prompts": [
         F("Empty sunny corner of yard, person measuring and cutting cedar planks on sawhorses, screws and drill nearby, garden layout stakes in ground", BACKYARD_ENV),
         F("Same corner, three cedar raised beds assembled in neat row, person shoveling compost and garden soil mix into the beds from wheelbarrow", BACKYARD_ENV),
         F("Same corner, beds filled with rich dark soil, person planting vegetable seedlings in neat rows — tomatoes peppers lettuce herbs — plant labels being placed", BACKYARD_ENV),
         F("Thriving finished vegetable garden, three raised cedar beds overflowing with ripe tomatoes, peppers, leafy greens, climbing beans on trellis, herbs, neat gravel paths between beds, person picking ripe red tomato, abundant harvest", BACKYARD_ENV),
     ],
     "video_prompts": [V + ". Person cutting cedar planks and assembling raised bed frames. Building timelapse. 8 seconds.",
                       V + ". Filling beds with soil, planting seedlings in rows. Garden taking shape. 8 seconds.",
                       V + ". Vegetables growing and ripening, harvesting fresh produce. Garden bounty. 8 seconds."]},
    # 15
    {"name": "Luxury Villa Garden Makeover",
     "hook": "Luxury villa garden transformation 🌺🏡",
     "title": "Dream Garden Created From Scratch 🌺",
     "description": "A bare luxury villa exterior transformed into a lush Mediterranean garden paradise!",
     "hashtags": "#shorts #luxury #garden #villa #mediterranean #landscaping #satisfying",
     "frame_prompts": [
         F("Bare dry landscape around luxury villa, person operating small excavator creating garden bed shapes, irrigation pipes being laid in trenches", LUXURY_ENV),
         F("Same area, garden beds shaped and soil amended, two people planting large olive trees and bougainvillea bushes, stone pathway being laid between beds", LUXURY_ENV),
         F("Same area, trees and major plants in, person installing drip irrigation emitters, another planting lavender and rosemary borders along the stone path", LUXURY_ENV),
         F("Breathtaking finished Mediterranean garden, mature olive trees, cascading purple bougainvillea over stone walls, lavender borders buzzing with bees, stone pathways, terracotta pots with citrus trees, fountain centerpiece, warm golden evening light, villa glowing in background", LUXURY_ENV),
     ],
     "video_prompts": [V + ". Excavating garden beds, laying irrigation around luxury villa. Groundwork. 8 seconds.",
                       V + ". Planting olive trees, bougainvillea, laying stone paths. Mediterranean garden forming. 8 seconds.",
                       V + ". Garden maturing, flowers blooming, fountain running. Paradise garden reveal. 8 seconds."]},
]

# Alias for backward compatibility
TIMELAPSE_CONCEPTS = DIY_CONCEPTS


# ─── Daily concept selection ──────────────────────────────────────────────────
from core.config import PROJECT_ROOT, logger

HISTORY_FILE = PROJECT_ROOT / "logs" / "aimagine_history.json"


def get_daily_concept() -> dict:
    """Pick a concept — TRENDING FIRST, static fallback."""
    trending = _generate_trending_concept()
    if trending:
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
    available = [c for c in DIY_CONCEPTS if c["name"] not in recent_set]
    if not available:
        available = list(DIY_CONCEPTS)

    chosen = random.choice(available)
    recent.append(chosen["name"])
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(recent[-60:], ensure_ascii=False), encoding="utf-8")
    logger.info(f"🏗️ AImagine concept (static): {chosen['name']} (pool: {len(available)}/{len(DIY_CONCEPTS)} available)")
    return chosen


def _generate_trending_concept() -> dict | None:
    """Generate a trending DIY concept using Gemini."""
    from core.trending import generate_trending_topic
    import google.generativeai as genai
    from core.config import GEMINI_API_KEY

    trending = generate_trending_topic("aimagine")
    if not trending or not trending.get("topic"):
        return None
    if not GEMINI_API_KEY:
        return None

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")

        concept_prompt = f"""You are a viral DIY/crafts content creator inspired by @diycraftstvofficial.

Based on this trending topic, create a COMPLETE DIY transformation concept:

TOPIC: {trending['topic']}
TITLE: {trending.get('title', '')}

Format rules:
- Fixed tripod camera, ground-level angle, SAME position all 4 frames
- 1-2 people working (seen from behind/side, mid-distance, dark work clothes)
- Transformation: empty/messy → beautiful finished result
- Categories: garden landscaping, room makeover, outdoor build, topiary, patio, kitchen

Frame sequence:
- Frame 1: Empty/before state, person starting work
- Frame 2: Early progress, person actively working
- Frame 3: Major progress, nearly complete
- Frame 4: Stunning finished result, no people, beauty shot

Return ONLY valid JSON:
{{
    "name": "Short concept name (3-5 words)",
    "hook": "Hook text with emoji (under 60 chars)",
    "title": "YouTube title with emoji (under 80 chars)",
    "description": "YouTube description (1-2 sentences)",
    "hashtags": "#shorts #diy #transformation #satisfying",
    "frame_prompts": ["frame1", "frame2", "frame3", "frame4"],
    "video_prompts": ["video1 8 seconds.", "video2 8 seconds.", "video3 8 seconds."]
}}"""

        response = model.generate_content(
            concept_prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.8,
            ),
        )
        result = json.loads(response.text)
        if result and result.get("name") and len(result.get("frame_prompts", [])) >= 4 and len(result.get("video_prompts", [])) >= 3:
            logger.info(f"🔥 Generated trending DIY concept: {result['name']}")
            return result
    except Exception as e:
        logger.warning(f"⚠️ Trending concept generation failed: {e}")
    return None
