"""
Sentinal Ihsan — Competitor Analysis & Trending Topics

UPDATED based on analysis of:
  @rzmertsc (102K) — Shock value + hybrid real/AI + discovery hooks
  @melihzyrkk (192K) — Futuristic tech discovery + "look what I found"
  DV93g2qjEg9 — "Cursed beds" (173K likes) — choice question format

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUR EVOLVED BRAND DNA:
  1. Sentinal Ihsan appears in EVERY video (face reference active)
  2. DISCOVERY HOOK: "I found this on the beach..." + impossible AI reveal
  3. HYBRID FORMAT: Real-looking anchor + mind-blowing AI element
  4. SHOCK/DISGUST: Cursed objects, material transformations, "uncanny valley"
  5. CHOICE QUESTION: "Which one? 1, 2, or 3?" → comment engagement bomb
  6. Settings: Beaches, ocean, abandoned places, junkyards, mystery locations
  7. Colors: Deep ocean blues, golden sunset, neon accents, surreal glow
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from datetime import date
from core.config import logger
from core.script_generator import generate_script

# ─── Pre-built Viral Topics (EVOLVED: discovery + shock + choice) ──────────────

VIRAL_TOPICS = [
    # === OCEAN DISCOVERY (brand core — enhanced) ===
    {"topic": "Found a giant glowing jellyfish washed up on the beach at sunset — it pulsed with alien light", "category": "ocean_discovery"},
    {"topic": "Rescued a baby dolphin tangled in fishing nets — it clicked at me like saying thank you", "category": "animal_rescue"},
    {"topic": "Found an impossible crystal formation inside a sea cave — it grew in perfect geometric shapes", "category": "ocean_discovery"},
    {"topic": "A massive sea turtle came to me for help — there was something attached to its shell", "category": "animal_rescue"},
    {"topic": "Discovered a mysterious glowing artifact buried in the wet sand at low tide", "category": "beach_discovery"},
    {"topic": "Found an underwater cave with bioluminescent creatures no scientist has documented", "category": "ocean_discovery"},
    {"topic": "Rescued a baby seal trapped between rocks — watch what happened next", "category": "animal_rescue"},

    # === HYBRID REAL+AI DISCOVERY (@rzmertsc style) ===
    {"topic": "Found a fish on the beach that has human-like teeth — what is this creature", "category": "shock_discovery"},
    {"topic": "This tide pool has a creature that changes into 3 different animals", "category": "shock_discovery"},
    {"topic": "Found a rock that splits open to reveal a living heart beating inside", "category": "shock_discovery"},
    {"topic": "Picked up a coconut on the beach — it opened to reveal a miniature ocean world inside", "category": "surreal_find"},
    {"topic": "Found a barnacle that plays music when you hold it to your ear", "category": "surreal_find"},
    {"topic": "This crab I found has a shell that looks exactly like a human skull", "category": "shock_discovery"},
    {"topic": "Opened a clam on the beach and found a pearl that glows like a tiny sun", "category": "surreal_find"},

    # === CURSED/SURREAL (@DV93g2qjEg9 style — choice format) ===
    {"topic": "Found 3 mysterious eggs on the beach — which one would you open? 1, 2, or 3?", "category": "cursed_choice"},
    {"topic": "3 underwater caves — each contains something impossible. Which do you explore?", "category": "cursed_choice"},
    {"topic": "Found 3 bottles washed up on shore — one contains a wish, one a curse, one a map. Which do you pick?", "category": "cursed_choice"},
    {"topic": "3 glowing objects in the tide pool — gold, silver, and obsidian. Something is wrong with one of them", "category": "cursed_choice"},
    {"topic": "Which ocean creature would you never want to encounter? This one, this one, or THIS one", "category": "cursed_choice"},

    # === MATERIAL TRANSFORMATION (shock value) ===
    {"topic": "Dropped liquid metal into the ocean and it formed into a perfect sculpture", "category": "weird_experiment"},
    {"topic": "What happens when you pour molten glass into freezing ocean water", "category": "weird_experiment"},
    {"topic": "Put a camera in a waterproof case and dropped it into the deepest point I could find", "category": "weird_experiment"},
    {"topic": "What happens when you throw 1000 glowsticks into the ocean at night", "category": "weird_experiment"},

    # === FUTURISTIC TECH DISCOVERY (@melihzyrkk style) ===
    {"topic": "Found an old device washed up on the beach — when I turned it on, it showed a hologram", "category": "tech_discovery"},
    {"topic": "This stone I pulled from the ocean has circuits running through it — ancient tech?", "category": "tech_discovery"},
    {"topic": "Found a piece of metal on the seafloor that repairs itself when you break it", "category": "tech_discovery"},

    # === EMOTIONAL RESCUE (evergreen) ===
    {"topic": "A baby bird fell from its nest into the ocean — I dove in from my boat to save it", "category": "animal_rescue"},
    {"topic": "Found a dog swimming alone 2 miles from shore — someone had to save it", "category": "animal_rescue"},
    {"topic": "This hermit crab was trapped in plastic. Watch the moment I set it free", "category": "animal_rescue"},
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
