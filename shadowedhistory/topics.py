"""
ShadowedHistory — Topic Database & Daily Selector (v2)

60 unique forgotten history topics for 30 days of dual-upload content.
Each topic designed for maximum viral potential and engagement.
"""

import json
import random
from datetime import date
from pathlib import Path

from core.config import PROJECT_ROOT, logger

HISTORY_FILE = PROJECT_ROOT / "logs" / "shadowedhistory_history.json"

# ─── Topic Categories ──────────────────────────────────────────────────────────

TOPICS = {
    "disaster": [
        "The last 18 minutes of Pompeii — a rain of fire and ash buried 20,000 people alive in 79 AD. Recent excavations found people frozen mid-scream",
        "The Chernobyl disaster was caused by a SAFETY TEST gone wrong. Reactor 4 exploded during a routine test, releasing 400 times more radiation than Hiroshima",
        "The Tunguska event of 1908 — something exploded over Siberia with 1,000 times the force of Hiroshima. Flattened 80 million trees. No crater. No debris. Still unexplained",
        "The collapse of the Bronze Age — around 1200 BC, every major civilization fell within 50 years. Egypt weakened, Hittites vanished, Mycenaeans destroyed. Nobody knows exactly why",
        "The Halifax Explosion of 1917 — a weapons ship detonated in Halifax harbor, killing 2,000 people. The largest man-made explosion before the atomic bomb",
    ],
    "mystery": [
        "Who REALLY burned the Library of Alexandria? There are 3 different suspects across 600 years — Julius Caesar, Christian mobs, and Muslim conquerors. The truth is more complex",
        "The Nazca Lines — massive drawings carved into the Peruvian desert, only visible from above. 2,000 years old. Some are 1,200 feet long. Who made them and why?",
        "Genghis Khan's tomb has NEVER been found. He ordered 2,500 soldiers to kill everyone at his burial site. Then those soldiers were killed too. The location died with them",
        "The Voynich Manuscript — a 600-year-old book written in a language no one can read. Filled with drawings of unknown plants. The world's most mysterious document",
        "The Wow! Signal — a 72-second radio signal from space in 1977 exactly matching what alien communication would look like. Never repeated. Never explained",
    ],
    "warfare": [
        "The Ottoman Empire dragged 70 ships OVER A MOUNTAIN to conquer Constantinople in 1453. They greased wooden logs, 50,000 soldiers pulled the ships overland. Genius",
        "Spartacus led 70,000 slaves against the ENTIRE Roman Empire. For 2 years they defeated every Roman army sent against them. The greatest slave revolt in history",
        "Hannibal crossed the ALPS with 37 war elephants to attack Rome from behind. He marched through snow and cliffs, losing half his army. But he won every battle for 15 years",
        "Japan attacked America with 9,000 BALLOONS in WW2. Each carried incendiary bombs, launched from Japan to ride the jet stream across the Pacific. Some reached Oregon",
        "The Battle of Thermopylae — 300 Spartans held a narrow pass against 300,000 Persians for 3 days. They knew they would die. They fought anyway",
        "Attila the Hun made Rome PAY him NOT to attack. The Romans paid 2,100 pounds of gold annually as tribute. The most powerful empire in history — bribed into survival",
        "The Scythians had FEMALE warriors 2,500 years ago. DNA analysis of burial mounds proves Amazon warriors were real — not myth. Women buried with swords and bows",
        "Rome was so AFRAID of Carthage, they salted the earth. After 3 wars over 100 years, Rome destroyed the city completely and poured salt so nothing would ever grow there",
    ],
    "engineering": [
        "How the Pyramids were ACTUALLY built — not aliens. A newly discovered ramp system, water-lubricated sleds, and 20,000 skilled workers. The real story is more impressive than myth",
        "Roman concrete HEALS ITSELF. Modern concrete cracks in 50 years — Roman concrete gets STRONGER. Scientists finally discovered the secret: volcanic ash and seawater react to fill cracks",
        "An Underground City for 20,000 people was hidden in Turkey for CENTURIES. Derinkuyu goes 18 stories deep. Ventilation shafts, wine presses, churches. All carved from solid rock 3,000 years ago",
        "This 2,000-year-old iron pillar in Delhi has NEVER rusted. In constant rain and humidity for 1,600 years. The ancient Indians knew a metallurgy technique we still don't fully understand",
    ],
    "discovery": [
        "Vikings reached America 500 YEARS before Columbus. L'Anse aux Meadows in Newfoundland proves Norse settlement around 1000 AD. Columbus wasn't even close to being first",
        "China explored the world 87 years BEFORE Columbus. Admiral Zheng He commanded a fleet of 300 ships and 28,000 men. His flagship was 5x larger than Columbus's Santa María",
        "Was the Trojan War REAL? We found the evidence. Heinrich Schliemann excavated a city matching Homer's description. Layers of destruction. Arrowheads in walls. Troy was real",
        "The Tollund Man — a 2,400-year-old body found in a Danish bog looking like he died YESTERDAY. Perfectly preserved skin, hair, fingerprints. His last meal was still in his stomach",
    ],
    "tomb": [
        "8,000 terracotta soldiers were built to guard ONE tomb. Emperor Qin Shi Huang's burial complex. Each face is unique. And the main tomb has NEVER been opened — mercury rivers inside",
        "Everyone who opened Tutankhamun's tomb DIED within years. Lord Carnarvon, his dog, 6 expedition members. Coincidence? Or an ancient fungal bio-weapon?",
        "Only 1 of 63 Royal Tombs in Egypt's Valley of Kings was found UNTOUCHED — Tutankhamun's. Every other pharaoh was robbed, sometimes within years of burial",
        "There are STILL unopened chambers in China's 2,200-year-old Terracotta Army tomb. Ground-penetrating radar shows massive voids. China says we don't have the technology to excavate safely — yet",
    ],
    "biography": [
        "Imhotep — the first GENIUS in recorded history. Most people never heard of him. He designed the first pyramid, practiced medicine, wrote poetry. 2,700 years before Leonardo da Vinci",
        "This Pharaoh tried to ERASE all the gods. Akhenaton forced Egypt to worship only one god — the sun disk Aten. He moved the capital, destroyed temples. After his death, they erased HIM",
        "Mansa Musa was so RICH he crashed Egypt's economy by visiting. His 1324 pilgrimage to Mecca with 60,000 men and 12 tons of gold caused 10 years of inflation in Cairo",
        "Cleopatra lived CLOSER to the Moon landing than to the building of the Pyramids. The Pyramids were already 2,500 years old when she ruled. Time is not what you think",
    ],
    "legend": [
        "We might have FOUND Atlantis. 3 locations match Plato's description — Santorini, the Richat Structure in Sahara, and a site off Spain's coast. New sonar data is compelling",
        "The Hanging Gardens of Babylon — real or a 2,500-year LIE? No archaeological evidence has ever been found in Babylon. Some scholars think they were actually in Nineveh, 300 miles north",
        "The Tower of Babel was REAL. We found the ruins. A massive ziggurat called Etemenanki stood in Babylon — 91 meters tall. The biblical story may be based on this actual structure",
    ],
    "lost_city": [
        "America's FORGOTTEN Pyramid City — Cahokia — was bigger than London in 1100 AD. 20,000 people, massive mounds, complex astronomy. Then everyone simply left. Nobody knows why",
        "Why the Incas ABANDONED their cloud city Machu Picchu. Built at 7,970 feet in the Andes, it was occupied for barely 100 years. Spanish invasion never reached it. They just left",
        "The largest temple on Earth — Angkor Wat — was ABANDONED for 400 years. Swallowed by jungle. Rediscovered by a French explorer in 1860 who couldn't believe what he found",
        "Cities worth BILLIONS were swallowed by the Sahara Desert along the Silk Road. Entire trading empires buried under sand. Some are just now being found by satellite imaging",
        "Rome built a PARADISE in the middle of the Syrian desert. Palmira was a crossroads of civilizations — Greek, Roman, Persian. A city of 200,000. Now mostly ruins after 2015 destruction",
    ],
    "invention": [
        "Vikings used a SECRET crystal to navigate the ocean — a calcite stone that could find the sun even through clouds. This was how they crossed the Atlantic without a compass",
        "Da Vinci designed TANKS 400 years before they existed. His notebooks contain helicopters, submarines, and robot knights. He deliberately reversed the gear design so nobody could build them",
        "Ancient Egyptians performed BRAIN surgery 5,000 years ago. Trepanation — drilling holes in the skull — with survival rates over 75%. They understood brain anatomy millennia before Hippocrates",
    ],
    "espionage": [
        "Poland cracked the Nazi Enigma code machine BEFORE anyone else. Three Polish mathematicians figured it out in 1932 — 7 years before WW2. They gave their work to the British",
        "The Stasi — East Germany's secret police — employed 1 in every 63 citizens as informants. They had files on 5.6 million people — one third of the population. Big Brother was real",
    ],
    "myth_busted": [
        "The Great Wall of China can NOT be seen from space. Astronauts confirmed it. It's only 15-30 feet wide — far too narrow. But you CAN see highways and airports",
        "The Ottoman Harem was NOT what you think. It wasn't a pleasure palace — it was the administrative center of the empire. Women held enormous political power. Some ruled as regents",
    ],
    "dark_history": [
        "They BLAMED an entire religion for the Black Plague. Across Europe, Jewish communities were massacred — accused of poisoning wells. Over 200 communities destroyed in 2 years",
        "Kamikaze pilots wrote their LAST letters before flying. Many were college students forced to volunteer. Their final words reveal not fanaticism — but heartbreak and resignation",
        "Alexander the Great BURNED Persepolis to the ground. The most magnificent city in the world, capital of the Persian Empire. He destroyed it in a single drunken night of revenge",
    ],
    "lifestyle": [
        "Gladiators were the ROCK STARS of Ancient Rome. They had fans, endorsement deals, and groupies. Their sweat was bottled and sold as an aphrodisiac. Some became millionaires",
        "Ancient Romans had FAST FOOD restaurants 2,000 years ago. Called thermopolia — 80 have been found in Pompeii alone. They served wine, bread, cheese, and hot stews over a counter",
        "The first COMPLAINT letter was written 4,000 years ago in Sumer. A customer named Nanni wrote to copper merchant Ea-Nasir demanding a refund for low-quality ingots. The original Karen",
    ],
    "diplomacy": [
        "The world's FIRST peace treaty was signed 3,000 years ago between Egypt and the Hittites. The Treaty of Kadesh in 1259 BC. A copy hangs in the United Nations building today",
    ],
    "ritual": [
        "The Aztecs sacrificed 80,000 people in ONE ceremony — the re-consecration of the Great Temple in 1487. Prisoners were lined up for miles. The rivers ran red for days",
    ],
    "empire": [
        "The Göktürk Empire controlled the ENTIRE Silk Road. From Mongolia to the Black Sea, these Turkic nomads built the first empire to unify Central Asia. Founded in 552 AD",
        "The Byzantine Empire's fall — the LAST day. May 29, 1453. Constantinople fell to Ottoman cannon fire. The walls that held for 1,000 years finally broke. The end of Rome — 2,200 years after its founding",
    ],
    "archaeology": [
        "Easter Island statues were WALKED into position. For decades scientists argued over how. Recent experiments proved the Moai were rocked back and forth — literally walked — using ropes",
        "A Samurai sword takes 3 MONTHS to make. Over a million hammer strikes fold the steel 16 times — creating 65,000 layers. Each blade is a unique work of art and lethal engineering",
    ],
}


def get_all_topics() -> list[str]:
    """Get a flat list of all topics."""
    all_topics = []
    for category, topics in TOPICS.items():
        all_topics.extend(topics)
    return all_topics


def get_daily_topic(exclude_recent: int = 60) -> dict:
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
    HISTORY_FILE.write_text(json.dumps(recent[-120:], ensure_ascii=False), encoding="utf-8")

    logger.info(f"🎲 ShadowedHistory topic: {chosen['topic'][:60]}...")
    return chosen
