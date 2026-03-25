"""
Sentinal Ihsan — Competitor Analysis & Trending Topics

UPDATED: Dialogue-driven concepts with character interaction.
Inspired by @rzmertsc, @melihzyrkk, "Cursed Beds" (DV93g2qjEg9)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BRAND DNA:
  1. 25-year-old character speaks TO CAMERA in every video
  2. Character interacts WITH the concept (sits in it, holds it, drives it)
  3. Dialogue format: "Hey guys, today I'm [doing X]... look at this!"
  4. Setting matches concept (NOT always beach)
  5. Concept object stays consistent — no shape-shifting or breaking
  6. Choice format: "Which one? 1, 2, or 3?" for engagement
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from datetime import date
from core.config import logger
from core.script_generator import generate_script

# ─── Pre-built Viral Topics (DIALOGUE-DRIVEN concepts) ────────────────────────

VIRAL_TOPICS = [
    # === CURSED EXPERIENCE (character interacts with concept) ===
    {"topic": "I'm sleeping in a bed made entirely of live mice tonight — how does it feel?",
     "category": "cursed_experience", "setting": "bedroom"},
    {"topic": "I filled my entire car with cola and I'm driving in it — this is insane",
     "category": "cursed_experience", "setting": "car_interior"},
    {"topic": "I'm taking a bath in a tub full of jelly — this is the weirdest thing I've ever done",
     "category": "cursed_experience", "setting": "bathroom"},
    {"topic": "I built a couch entirely out of marshmallows and I'm sitting on it right now",
     "category": "cursed_experience", "setting": "living_room"},
    {"topic": "I'm eating dinner at a table made entirely of chocolate — everything is melting",
     "category": "cursed_experience", "setting": "dining_room"},
    {"topic": "I filled my swimming pool with bouncy balls and jumped in",
     "category": "cursed_experience", "setting": "backyard_pool"},
    {"topic": "I'm sleeping on a bed made of live snakes tonight — worst idea ever",
     "category": "cursed_experience", "setting": "bedroom"},
    {"topic": "I wrapped my entire room in aluminum foil — everything, even the furniture",
     "category": "cursed_experience", "setting": "bedroom"},

    # === CHOICE FORMAT (pick 1, 2, or 3) ===
    {"topic": "3 mystery boxes — one has $10,000, one has spiders, one has slime. Which do you pick?",
     "category": "cursed_choice", "setting": "warehouse"},
    {"topic": "3 beds: one made of feathers, one of cactus, one of ice. Which are you sleeping in?",
     "category": "cursed_choice", "setting": "bedroom"},
    {"topic": "3 pools: one of honey, one of paint, one of milk. Which one are you jumping in?",
     "category": "cursed_choice", "setting": "backyard"},
    {"topic": "3 cars: one filled with sand, one with water, one with popcorn. Which one do you drive?",
     "category": "cursed_choice", "setting": "parking_lot"},
    {"topic": "3 meals: one is alive, one is frozen solid, one is invisible. Which do you eat?",
     "category": "cursed_choice", "setting": "restaurant"},

    # === MATERIAL TRANSFORMATION (object changes texture) ===
    {"topic": "What if my entire house was made of glass — I can see through everything",
     "category": "transformation", "setting": "glass_house"},
    {"topic": "I turned all my furniture into gold — my room is now worth millions",
     "category": "transformation", "setting": "luxury_room"},
    {"topic": "Everything in my kitchen is now made of rubber — nothing works anymore",
     "category": "transformation", "setting": "kitchen"},
    {"topic": "My clothes are made of paper today — one wrong move and they tear",
     "category": "transformation", "setting": "city_street"},

    # === DISCOVERY / REVEAL ===
    {"topic": "I found a box in my attic that's been sealed for 50 years — opening it now",
     "category": "discovery", "setting": "attic"},
    {"topic": "There's a secret room behind my bookshelf that I never knew existed",
     "category": "discovery", "setting": "library_room"},
    {"topic": "I bought an abandoned storage unit for $100 — you won't believe what's inside",
     "category": "discovery", "setting": "storage_unit"},
    {"topic": "I found a working phone from 1990 in a thrift store — look what's saved on it",
     "category": "discovery", "setting": "thrift_store"},

    # === WEIRD EXPERIMENT ===
    {"topic": "What happens when you microwave 100 glow sticks at once",
     "category": "experiment", "setting": "garage_workshop"},
    {"topic": "I froze every liquid in my fridge and tried to eat them as popsicles",
     "category": "experiment", "setting": "kitchen"},
    {"topic": "What happens when you drop a watermelon from the 10th floor into a pool of paint",
     "category": "experiment", "setting": "rooftop"},
    {"topic": "I put my phone in concrete for 24 hours — will it survive?",
     "category": "experiment", "setting": "garage_workshop"},

    # === EMOTIONAL/RESCUE (kept as brand anchor) ===
    {"topic": "I found a tiny kitten abandoned in a cardboard box in the rain — rescuing it now",
     "category": "rescue", "setting": "rainy_street"},
    {"topic": "This baby bird fell from its nest into traffic — I stopped my car to save it",
     "category": "rescue", "setting": "city_road"},
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
    """Generate a trending topic using Gemini (based on your brand DNA)."""
    try:
        result = generate_script("sentinal_ihsan", "Generate a viral topic idea")
        if result and result.get("title"):
            return {
                "topic": result["title"],
                "category": "gemini_trending",
            }
    except Exception:
        pass
    return None
