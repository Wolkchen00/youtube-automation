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

import json
import random
from datetime import date
from pathlib import Path

import google.generativeai as genai

from core.config import GEMINI_API_KEY, PROJECT_ROOT, logger


HISTORY_FILE = PROJECT_ROOT / "logs" / "sentinal_ihsan_history.json"

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

    # === EXTRA VIRAL TOPICS (expanded pool to avoid repeats) ===
    {"topic": "Filling a room with 10,000 balloons and then vacuuming them all at once",
     "category": "cursed_experience", "setting": "living_room",
     "action_steps": "fills room with balloons, shows the sea of balloons, turns on industrial vacuum, balloons get sucked in"},

    {"topic": "Making a mirror out of melted candy — does it actually reflect?",
     "category": "transformation", "setting": "kitchen",
     "action_steps": "melts candy, pours into flat mold, waits for it to cool, polishes surface, checks reflection"},

    {"topic": "Building a chair entirely out of hot glue sticks — can it hold his weight?",
     "category": "experiment", "setting": "workshop",
     "action_steps": "glues sticks together layer by layer, builds chair shape, lets it dry, sits down carefully, tests weight"},

    {"topic": "Covering a basketball with magnets and dropping it near a metal wall",
     "category": "experiment", "setting": "garage",
     "action_steps": "glues magnets all over basketball, brings it near metal wall, ball sticks, tries to pull it off"},

    {"topic": "Filling shoes with concrete and trying to walk in them",
     "category": "cursed_experience", "setting": "backyard",
     "action_steps": "pours wet concrete into shoes, waits for it to set, puts feet in, tries to walk and lift legs"},

    {"topic": "What happens if you put 50 rubber bands on a watermelon until it explodes",
     "category": "experiment", "setting": "backyard",
     "action_steps": "places rubber bands one by one around watermelon, tension builds, watermelon deforms, finally explodes"},

    {"topic": "Making an entire outfit out of duct tape and wearing it in public",
     "category": "cursed_experience", "setting": "garage",
     "action_steps": "wraps duct tape into shirt, pants, shoes, puts outfit on, walks around, shows reactions"},
]


def get_daily_topic(exclude_recent: int = 30) -> dict:
    """Select today's topic from pre-built viral list, avoiding recent repeats."""
    recent = []
    if HISTORY_FILE.exists():
        try:
            recent = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            recent = []

    recent_set = set(recent[-exclude_recent:])
    available = [t for t in VIRAL_TOPICS if t["topic"] not in recent_set]

    if not available:
        # All topics used, reset and pick any
        available = list(VIRAL_TOPICS)

    chosen = random.choice(available)

    # Save to history
    recent.append(chosen["topic"])
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(recent[-100:], ensure_ascii=False), encoding="utf-8")

    logger.info(f"🎬 Sentinal Ihsan topic: {chosen['topic'][:60]}...")
    return chosen


def get_trending_with_gemini() -> dict | None:
    """Generate a trending viral topic using Gemini with a purpose-built prompt."""
    if not GEMINI_API_KEY:
        return None

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(
            "gemini-2.5-flash",
            system_instruction=(
                "You are a viral content strategist for TikTok/YouTube Shorts. "
                "You specialize in satisfying, experiment, and discovery content. "
                "Generate ONE unique viral video topic idea that a young male creator "
                "can film with a front-facing camera. The topic must involve PHYSICAL "
                "INTERACTION with an object or material (painting, pouring, building, "
                "opening, crushing, filling, etc). "
                "Return ONLY valid JSON with keys: topic (full description), "
                "category (one of: transformation, experiment, cursed_experience, discovery), "
                "setting (where to film), action_steps (what the character physically does)"
            ),
        )

        response = model.generate_content(
            "Generate a fresh, never-seen-before viral experiment topic. "
            "Think satisfying transformations, impossible builds, or cursed experiences. "
            "Make it something that would get millions of views. Return ONLY valid JSON.",
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=1.0,
            ),
        )

        result = json.loads(response.text)
        if result and result.get("topic"):
            logger.info(f"🤖 Gemini trending topic: {result['topic'][:60]}...")
            return {
                "topic": result["topic"],
                "category": result.get("category", "gemini_trending"),
                "setting": result.get("setting", "generic"),
                "action_steps": result.get("action_steps", ""),
            }
    except Exception as e:
        logger.warning(f"⚠️ Gemini trending topic failed: {e}")
    return None
