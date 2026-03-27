"""
Sentinal Ihsan — Competitor Analysis & Viral Topic Database

VIRAL RECREATION STRATEGY:
  ✅ Recreate PROVEN viral videos with our character's face
  ✅ Each topic has specific ACTION STEPS (what the character physically does)
  ✅ Settings matched to concept (NOT random)
  ✅ Topics sorted by viral potential (proven recreations first)

REFERENCE CHANNELS:
  @bayburra (565K) — Chrome paint, satisfying reveals (625K+ likes per video)
  @rzmertsc — Object discovery, shock reveals
  @melihzyrkk — Product interaction, cursed experiences
"""

from datetime import date
from core.config import logger
from core.script_generator import generate_script

# ─── VIRAL TOPICS (PROVEN RECREATIONS + ORIGINAL CONCEPTS) ─────────────────────

VIRAL_TOPICS = [
    # === PROVEN VIRAL RECREATIONS (highest priority) ===
    # @bayburra chrome paint video: 625K likes
    {"topic": "Painting a wall with chrome mirror paint — the result is so reflective he can see himself in it",
     "category": "viral_recreation", "setting": "garage_or_room",
     "action_steps": "picks up roller, dips in chrome paint, rolls onto dark wall, paint turns mirror-like, sees reflection"},

    {"topic": "Pouring liquid chrome over a plain white sneaker — it becomes a mirror shoe",
     "category": "viral_recreation", "setting": "workshop_table",
     "action_steps": "places white shoe on table, opens chrome paint can, slowly pours over shoe, shoe transforms to chrome mirror"},

    {"topic": "Dipping ordinary objects into liquid gold paint — everything becomes luxury",
     "category": "viral_recreation", "setting": "workshop_table",
     "action_steps": "shows normal objects (phone case, sunglasses), dips each one into gold paint bucket, pulls them out gleaming"},

    {"topic": "Spraying an old rusty car door with chrome paint — instant transformation from junk to luxury",
     "category": "viral_recreation", "setting": "garage",
     "action_steps": "shows rusty door, sprays chrome paint, watches it transform, sees reflection in the painted surface"},

    {"topic": "Mixing 100 different paint colors together — what color will it make?",
     "category": "viral_recreation", "setting": "paint_room",
     "action_steps": "pours different paint colors one by one into bucket, stirs, the result is unexpected color"},

    # === SATISFYING TRANSFORMATION (high engagement) ===
    {"topic": "Filling a transparent phone case with liquid glitter — it looks like a galaxy inside",
     "category": "transformation", "setting": "desk",
     "action_steps": "shows clear case, slowly pours glitter fluid inside, tilts and shakes, galaxy effect forms"},

    {"topic": "Pressing a hydraulic press on everyday objects — watching them get crushed in slow motion",
     "category": "transformation", "setting": "workshop",
     "action_steps": "places object under press, activates press, watches object crush and deform, examines result"},

    {"topic": "Pouring molten aluminum into a watermelon — the metal fills every space inside",
     "category": "transformation", "setting": "outdoor_firepit",
     "action_steps": "cuts open watermelon, heats aluminum, pours molten metal inside, waits, cracks open the result"},

    {"topic": "Making a knife out of chocolate — can it actually cut things?",
     "category": "transformation", "setting": "kitchen",
     "action_steps": "melts chocolate, pours into knife mold, freezes it, takes out chocolate knife, tries cutting food"},

    # === CURSED EXPERIENCE (character interaction) ===
    {"topic": "I filled my entire bathtub with orbeez — 10,000 water beads and jumping in",
     "category": "cursed_experience", "setting": "bathroom",
     "action_steps": "shows empty tub, pours bags of orbeez, adds water, beads expand, character jumps in and describes feeling"},

    {"topic": "Sleeping in a bed made entirely of bubble wrap tonight — every move makes noise",
     "category": "cursed_experience", "setting": "bedroom",
     "action_steps": "covers bed with bubble wrap, lies down, every movement pops bubbles, tries to sleep"},

    {"topic": "I filled my car with popcorn kernels and turned on the heat — they started popping everywhere",
     "category": "cursed_experience", "setting": "car_interior",
     "action_steps": "pours kernels, turns on max heat, kernels start popping, car fills with popcorn"},

    {"topic": "Covering my entire room floor with legos and walking across barefoot",
     "category": "cursed_experience", "setting": "bedroom",
     "action_steps": "dumps boxes of legos on floor, takes off shoes, attempts to walk across, reacts to pain"},

    {"topic": "I wrapped every single item in my room with aluminum foil — everything",
     "category": "cursed_experience", "setting": "bedroom",
     "action_steps": "wraps furniture, phone, lamp, bed with foil one by one, reveals the final all-foil room"},

    # === CHOICE FORMAT (pick 1, 2, or 3) ===
    {"topic": "3 mystery boxes: one has $10,000 cash, one has live spiders, one has slime inside",
     "category": "cursed_choice", "setting": "warehouse",
     "action_steps": "shows 3 boxes, opens each one with suspense, reacts to contents, asks viewers"},

    {"topic": "3 pools: one filled with honey, one with paint, one with milk — which one would you swim in?",
     "category": "cursed_choice", "setting": "backyard",
     "action_steps": "shows three kiddie pools filled with different liquids, touches each one, asks viewers to pick"},

    {"topic": "3 sofas: one made of cactus, one of ice blocks, one of marshmallows — which would you sit on?",
     "category": "cursed_choice", "setting": "warehouse",
     "action_steps": "shows three sofas, sits on each and reacts, asks viewers to comment their choice"},

    # === DISCOVERY / REVEAL ===
    {"topic": "I bought an abandoned storage unit for $100 — opening it and finding something incredible inside",
     "category": "discovery", "setting": "storage_unit",
     "action_steps": "cuts lock, opens door, explores contents, finds something valuable/weird, reacts"},

    {"topic": "I found a sealed box from 1950 at a garage sale — opening it for the first time in 74 years",
     "category": "discovery", "setting": "garage",
     "action_steps": "shows aged box, carefully opens it, examines contents one by one, shocked by what's inside"},

    # === WEIRD EXPERIMENT ===
    {"topic": "What happens when you drop 100 bath bombs into a pool at the same time",
     "category": "experiment", "setting": "backyard_pool",
     "action_steps": "shows pile of bath bombs, drops them all at once into clear pool, water explodes with colors"},

    {"topic": "Freezing a bottle of cola to exactly -2 degrees then opening it — instant freeze magic",
     "category": "experiment", "setting": "kitchen",
     "action_steps": "takes supercooled bottle from freezer, cracks it open, cola instantly freezes solid"},
]


def get_daily_topic() -> dict:
    """Select today's topic from pre-built viral list."""
    today = date.today()
    day_num = today.toordinal()
    idx = day_num % len(VIRAL_TOPICS)
    topic = VIRAL_TOPICS[idx]
    logger.info(f"🎬 Sentinal Ihsan topic: {topic['topic'][:60]}...")
    return topic


def get_trending_with_gemini() -> dict | None:
    """Generate a trending topic using Gemini (based on brand DNA)."""
    try:
        result = generate_script("sentinal_ihsan", "Generate a viral topic idea")
        if result and result.get("title"):
            return {
                "topic": result["title"],
                "category": "gemini_trending",
                "setting": "generic",
            }
    except Exception:
        pass
    return None
