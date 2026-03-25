"""
ShadowedHistory — Topic Database & Daily Selector

100+ forgotten history topics across categories.
Ensures no repeats for the last 30 days.
"""

import json
import random
from datetime import date
from pathlib import Path

from core.config import PROJECT_ROOT, logger

HISTORY_FILE = PROJECT_ROOT / "logs" / "shadowedhistory_history.json"

# ─── Topic Categories ──────────────────────────────────────────────────────────

TOPICS = {
    "lost_civilizations": [
        "The Indus Valley Civilization vanished without a trace — 5 million people gone",
        "Göbekli Tepe was built 12,000 years ago — 6,000 years before Stonehenge",
        "The Minoans had indoor plumbing 4,000 years ago — then disappeared overnight",
        "Norte Chico civilization built pyramids while Egypt was still in chaos",
        "The Sea Peoples destroyed the entire Bronze Age world — nobody knows who they were",
        "Cahokia was bigger than London in 1100 AD — then everyone left",
        "The Kingdom of Aksum claimed to hold the Ark of the Covenant",
        "The Nabataeans carved Petra into solid rock — their water engineering was centuries ahead",
        "The Khmer Empire built Angkor Wat — the largest religious structure ever — then abandoned it",
        "Tartessos — the ancient civilization the Greeks called 'beyond wealthy' that vanished",
    ],
    "forgotten_inventions": [
        "The Baghdad Battery — a 2,000-year-old device that could generate electricity",
        "Greek Fire — the Byzantine Empire's secret weapon nobody could replicate",
        "The Antikythera Mechanism — a 2,100-year-old analog computer found in a shipwreck",
        "Nikola Tesla's Wardenclyffe Tower — free wireless energy that got shut down by JP Morgan",
        "The Roman concrete recipe — stronger than modern concrete, lost for 1,500 years",
        "Damascus Steel — a metal so sharp it could cut through rifle barrels, recipe lost forever",
        "Starlite — a plastic that could withstand nuclear temperatures, inventor took secret to grave",
        "The Lycurgus Cup — Romans made nanotech glass 1,700 years ago",
        "Heron's steam engine was built in 1st century AD — but Romans ignored it",
        "The Inca quipu — a 3D binary code system made of knotted strings",
    ],
    "mysterious_disappearances": [
        "The entire crew of the Mary Celeste vanished — dinner was still on the table",
        "The Roanoke Colony — 115 people disappeared, only the word 'Croatoan' remained",
        "Flight 19 — five Navy bombers vanished in the Bermuda Triangle in 1945",
        "The Flannan Isles lighthouse keepers — three men vanished from a locked lighthouse",
        "The Sodder Children — five kids vanished during a house fire, bodies never found",
        "The Amber Room — an entire room of amber and gold stolen by Nazis, never recovered",
        "DB Cooper hijacked a plane, jumped with $200,000, and was never seen again",
        "The Lost Colony of Greenland — 5,000 Norse settlers vanished in the 15th century",
        "Amelia Earhart's disappearance — did she crash, get captured, or survive?",
        "Percy Fawcett vanished searching for the Lost City of Z in the Amazon",
    ],
    "dark_secrets": [
        "The Vatican has 53 miles of secret archives underground — some documents sealed for 75 more years",
        "Operation Paperclip — the US smuggled 1,600 Nazi scientists into America after WWII",
        "MK-Ultra — the CIA dosed unwitting civilians with LSD in secret labs for mind control",
        "The Catacombs of Paris hold the bones of 6 million people stacked in tunnels beneath the city",
        "Pompeii's bodies were frozen in volcanic ash — their last moments preserved for 2,000 years",
        "The Tower of London held prisoners for 900 years — executions happened on the grounds",
        "The Terracotta Army — 8,000 life-sized clay soldiers buried with China's first emperor",
        "Derinkuyu — an underground city in Turkey that held 20,000 people 18 stories deep",
        "The Skull Tower of Niš — an Ottoman tower built from 952 human skulls as a warning",
        "The Sedlec Ossuary — a Czech church decorated with the bones of 40,000 people",
    ],
    "suppressed_discoveries": [
        "Ignaz Semmelweis discovered handwashing saves lives — was sent to an asylum for it",
        "Alfred Wegener proposed continental drift in 1912 — was laughed at for 50 years",
        "Rosalind Franklin discovered DNA's structure — Watson and Crick got the Nobel Prize",
        "The Voynich Manuscript — a 600-year-old book in a language nobody can read",
        "The Library of Alexandria held all human knowledge — burned down by accident or conquest",
        "Tesla's death ray patent — was it real? The FBI seized all his files when he died",
        "The Piri Reis map from 1513 shows Antarctica without ice — how?",
        "The Wow! Signal — a 72-second signal from space in 1977 that was never explained",
        "Ancient Egyptians may have used electricity — the Dendera Light mystery",
        "The Baghdad hanging gardens — did they really exist or was it propaganda?",
    ],
    "ancient_warfare": [
        "Hannibal crossed the Alps with 37 war elephants — one of history's greatest military feats",
        "The Battle of Thermopylae — 300 Spartans held off 300,000 Persians",
        "Genghis Khan killed so many people that global CO2 levels actually dropped",
        "Medieval castles had murder holes — boiling oil poured on attackers from above",
        "The Aztecs sacrificed 84,000 people in four days during the Great Temple dedication",
        "Viking Berserkers fought in a trance-like fury — possibly from eating magic mushrooms",
        "The Byzantine Empire used a flamethrower-like weapon called 'Greek Fire' for 700 years",
        "Vlad the Impaler put 20,000 people on stakes — inspired the Dracula legend",
        "The Mongols catapulted plague-infected corpses into enemy cities — first biological warfare",
        "The Swiss Guard was so fierce that the Pope hired them — they still protect the Vatican today",
    ],
    "forgotten_events": [
        "The eruption of Krakatoa in 1883 — the loudest sound in recorded history, heard 3,000 miles away",
        "The Tunguska Event — a mysterious explosion flattened 80 million trees across 2,150 sq km in Siberia",
        "The sinking of the Titanic — 1,500 people died in the freezing Atlantic in 1912",
        "The Great Fire of London 1666 — 13,200 houses and 87 churches burned for 4 days",
        "The fall of Constantinople 1453 — massive siege walls breached by the world's largest cannon",
        "The eruption of Mount Vesuvius — buried Pompeii and Herculaneum in 20 feet of ash",
        "The Colosseum held 50,000 spectators watching gladiators fight to the death for 400 years",
        "The Hagia Sophia — built in just 5 years in 537 AD, it was the world's largest building for 1,000 years",
        "The construction of the Panama Canal — 25,000 workers died building it over 10 years",
        "The Halifax Explosion of 1917 — the largest man-made blast before the atomic bomb flattened a city",
    ],
    "hidden_knowledge": [
        "Ancient Sumerians described 12 planets in our solar system 6,000 years ago",
        "The Emerald Tablet — the alchemists' most sacred text, origin unknown",
        "The Dead Sea Scrolls contained texts that were deliberately excluded from the Bible",
        "The Dogon Tribe in Africa knew about Sirius B — a star invisible to the naked eye",
        "The Moai of Easter Island — 887 massive statues carved by a civilization that collapsed",
        "The Nazca Lines can only be seen from the air — who were they made for?",
        "Coral Castle — one man moved 1,100 tons of coral blocks alone, refused to explain how",
        "The Stone Spheres of Costa Rica — perfectly round, some weigh 16 tons, nobody knows why",
        "The Voynich Manuscript contains botanical drawings of plants that don't exist",
        "The Phaistos Disc — a 4,000-year-old clay tablet with symbols nobody can decipher",
    ],
}


def get_all_topics() -> list[str]:
    """Get a flat list of all topics."""
    all_topics = []
    for category, topics in TOPICS.items():
        all_topics.extend(topics)
    return all_topics


def get_daily_topic(exclude_recent: int = 30) -> dict:
    """Select a daily topic, avoiding recent repeats.

    Returns:
        {"topic": str, "category": str}
    """
    # Load history
    recent = []
    if HISTORY_FILE.exists():
        try:
            recent = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            recent = []

    # Find available topics
    recent_set = set(recent[-exclude_recent:])
    available = []
    for category, topics in TOPICS.items():
        for topic in topics:
            if topic not in recent_set:
                available.append({"topic": topic, "category": category})

    if not available:
        # Reset if all used
        available = [{"topic": t, "category": c} for c, ts in TOPICS.items() for t in ts]

    chosen = random.choice(available)

    # Save to history
    recent.append(chosen["topic"])
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(recent[-100:], ensure_ascii=False), encoding="utf-8")

    logger.info(f"🎲 ShadowedHistory topic: {chosen['topic'][:60]}...")
    return chosen
