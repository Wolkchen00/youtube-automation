"""
Sentinal Ihsan — Competitor Analysis & Trending Topics

Based on @sentinal.ihsan.daily Instagram analysis:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUR BRAND DNA:
  1. Sentinal Ihsan appears in EVERY video (face consistency key)
  2. Themes: Ocean discovery, animal rescue, surreal nature finds
  3. Setting: Beaches, boats, ocean, golden hour lighting
  4. Style: POV/selfie cam, hyper-realistic AI, emotional hooks
  5. Hooks: "I found an impossible...", "You won't believe...", "Far offshore..."
  6. Colors: Deep ocean blues, golden sunset tones, cinematic warm light
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from datetime import date
from core.config import logger
from core.script_generator import generate_script

# ─── Pre-built Viral Topics (based on your actual content style) ───────────────

VIRAL_TOPICS = [
    # === OCEAN DISCOVERY (your brand signature) ===
    {"topic": "Found a giant glowing jellyfish washed up on the beach at sunset", "category": "ocean_discovery"},
    {"topic": "Rescued a baby dolphin tangled in fishing nets near my boat", "category": "animal_rescue"},
    {"topic": "Found an impossible crystal formation inside a sea cave", "category": "ocean_discovery"},
    {"topic": "A massive sea turtle came to me for help on the beach", "category": "animal_rescue"},
    {"topic": "Discovered a mysterious ancient artifact buried in the sand", "category": "beach_discovery"},
    {"topic": "A whale shark swam right next to my small boat", "category": "ocean_encounter"},
    {"topic": "Found an underwater cave glowing with bioluminescent creatures", "category": "ocean_discovery"},
    {"topic": "Rescued a baby seal trapped between rocks", "category": "animal_rescue"},
    {"topic": "A giant octopus climbed onto my boat while fishing", "category": "ocean_encounter"},
    {"topic": "Found a perfectly intact ancient ship anchor on the ocean floor", "category": "ocean_discovery"},

    # === SURREAL NATURE FINDS ===
    {"topic": "This rock I found on the beach glows in the dark", "category": "surreal_find"},
    {"topic": "Found a flower that changes color when you touch it", "category": "surreal_find"},
    {"topic": "This tide pool has a creature nobody has ever seen before", "category": "ocean_discovery"},
    {"topic": "I found a cave where water flows upward", "category": "surreal_find"},
    {"topic": "Discovered a fish that can walk on land and followed me", "category": "surreal_find"},

    # === MOTORCYCLE/ADVENTURE ===
    {"topic": "Riding my motorcycle through a tunnel and found a hidden beach", "category": "adventure"},
    {"topic": "Found an abandoned lighthouse with something incredible inside", "category": "adventure"},
    {"topic": "Exploring a cliff edge when I spotted something impossible in the ocean below", "category": "adventure"},

    # === EMOTIONAL RESCUE ===
    {"topic": "This starfish was dying on the hot sand, watch what happened when I put it back", "category": "animal_rescue"},
    {"topic": "A baby bird fell from its nest into the ocean, I dove in to save it", "category": "animal_rescue"},
    {"topic": "Found a dog swimming alone far from shore, had to rescue it", "category": "animal_rescue"},
    {"topic": "A pelican with a broken wing came to me on the beach", "category": "animal_rescue"},

    # === WEIRD/VIRAL ===
    {"topic": "What happens when you pour honey into the ocean at sunset", "category": "weird_experiment"},
    {"topic": "I found the most perfect sand dollar ever and it started glowing", "category": "surreal_find"},
    {"topic": "This hermit crab chose the most unexpected shell you've ever seen", "category": "ocean_discovery"},
    {"topic": "I left my camera underwater overnight, look what showed up", "category": "ocean_discovery"},
    {"topic": "The smoothest stone skipping you've ever seen, it bounced 20 times", "category": "weird_experiment"},
    {"topic": "Put a waterproof camera inside a coconut and threw it in the ocean", "category": "weird_experiment"},
    {"topic": "What happens when a wave hits perfectly stacked rocks", "category": "weird_experiment"},
    {"topic": "Found a message in a bottle that's 50 years old", "category": "beach_discovery"},
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
