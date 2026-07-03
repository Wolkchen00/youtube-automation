"""
Galactic Experiment — Space Topic Database (v2)

60 unique space topics for 30 days of dual-upload content.
Each topic designed for maximum viral potential.
"""

import json
import random
from datetime import date
from pathlib import Path

from core.config import PROJECT_ROOT, logger

HISTORY_FILE = PROJECT_ROOT / "logs" / "galactic_experiment_history.json"

TOPICS = {
    "deep_space": [
        "Voyager 1 just sent a mysterious signal from 15 BILLION miles away — and scientists can't fully explain it. It's the farthest human-made object ever. What did it detect?",
        "The Oort Cloud is the edge of our solar system — and it's 2 LIGHT YEARS away. A shell of trillions of icy objects we've never seen. What's hiding out there?",
        "There are THOUSANDS of hidden dwarf planets beyond Neptune in the Kuiper Belt. We've only mapped a fraction. An entire region of our solar system still unexplored",
        "The farthest human-made object is leaving the solar system RIGHT NOW at 38,000 mph. Voyager 1 launched in 1977 and it still sends data. It carries a golden record for aliens",
        "An ALIEN-like object called Oumuamua flew through our solar system in 2017. It accelerated without any visible propulsion. Scientists still debate what it was",
        "Getting to the nearest star Proxima Centauri would take 73,000 YEARS with current technology. It's only 4.2 light-years away. The universe is incomprehensibly vast",
    ],
    "what_if": [
        "What if Earth's magnetic field suddenly FLIPPED? It's happened before — 780,000 years ago. The poles reversed. Compasses pointed south. And it might happen again soon",
        "What if a teaspoon of neutron star material was dropped on Earth? That tiny amount weighs 6 BILLION tons. It would punch through the planet like a bullet through paper",
        "What if Earth's core cooled down completely? No more magnetic field. Solar wind strips away the atmosphere. Oceans evaporate. Earth becomes a dead rock like Mars",
        "What if a gamma-ray burst hit Earth directly? In SECONDS, half the ozone layer vanishes. UV radiation sterilizes the surface. One already hit Earth 450 million years ago",
        "What if we detonated every nuclear weapon inside a black hole? Absolutely nothing would happen. The black hole wouldn't even notice. That's how powerful gravity is",
        "What if Earth suddenly had Saturn's rings? Shadows would cover entire continents. Nighttime sky would be breathtaking. But satellite orbits would be impossible",
    ],
    "extreme_facts": [
        "The coldest place in the universe is the Boomerang Nebula at -272°C — just 1 degree above absolute zero. It's COLDER than the empty void of space itself",
        "It literally RAINS diamonds on Neptune and Uranus. Extreme pressure crushes carbon into diamond crystals that fall like hailstones. Billions of carats falling right now",
        "A magnetar's magnetic field is so powerful it could erase your credit card from the MOON. It would kill you from 1,000 miles away by rearranging your atoms",
        "A pulsar spins 716 times per SECOND. That's a star the size of a city rotating faster than a kitchen blender. The surface moves at 24% the speed of light",
        "The universe is 93 billion light-years across but only 13.8 billion years old. How? Space itself expanded FASTER than light. The math is mind-breaking",
        "There's a cloud of alcohol in space 1,000 times larger than our solar system. Sagittarius B2 contains enough ethanol to fill 400 trillion trillion pints of beer",
    ],
    "discovery": [
        "NASA found something STRANGE inside the Moon. When Apollo crews crashed a module into it, the Moon rang like a bell for over an hour. Is it hollow?",
        "James Webb telescope found a galaxy that SHOULDN'T exist. It's too massive, too early in the universe's history. Our models of galaxy formation might be wrong",
        "NASA confirmed there's WATER on the Moon. Not just traces — significant deposits of ice in permanently shadowed craters. Enough to support a lunar base",
        "Scientists found signs of LIFE on Venus — phosphine gas in the clouds. On Earth, only living organisms produce it. Could microbes be floating in Venus's atmosphere?",
        "We just photographed OUR black hole — Sagittarius A* — for the first time. It's 4 million times the mass of the Sun, sitting 26,000 light-years from Earth",
        "Mars is BREATHING. Methane levels spike and drop seasonally — just like biological processes on Earth. Something is producing methane on Mars right now",
    ],
    "survival": [
        "You'd die in 37 seconds on Venus. 900°F surface, 90 atmospheres of pressure, sulfuric acid clouds. The Soviet Venera probes lasted only 23 minutes before being crushed",
        "What happens to your body in space WITHOUT a suit? You have about 15 seconds of consciousness. Your blood doesn't boil — but the water in your lungs does",
        "Jupiter's magnetic field would KILL you instantly. Radiation levels near Jupiter are 1,000 times the lethal dose. The Juno probe's electronics are in a titanium vault",
        "Surviving on Titan means dealing with -179°C temperatures and methane rain. But you could actually FLY by strapping on wings — the atmosphere is thick enough",
        "Astronauts on the ISS age SLOWER than people on Earth — by about 0.01 seconds per year. Time dilation is real. GPS satellites have to correct for it",
    ],
    "black_hole": [
        "Time STOPS at the edge of a black hole's event horizon. From your perspective, you'd cross it instantly. But to an outside observer, you'd freeze forever at the boundary",
        "NASA recorded the actual SOUND of a black hole. It's a deep, haunting B-flat, 57 octaves below middle C. The pressure waves in the gas cloud create real sound",
        "We can HEAR two black holes crashing together — through gravitational waves. LIGO detected spacetime itself rippling. Einstein predicted this 100 years earlier",
        "A supermassive black hole is SHREDDING a star right now — astronomers caught it live. The star orbits closer and closer, stretched into spaghetti, before being consumed",
    ],
    "cosmic_mystery": [
        "The invisible force holding our galaxy together is dark matter. It makes up 27% of the universe but we've NEVER detected a single particle of it directly",
        "The universe might be filled with an invisible DARK FLUID — a combination of dark matter and dark energy. One substance explaining both. The math works",
        "Mysterious signals from deep space last only MILLISECONDS — fast radio bursts. We've detected thousands but only traced a few. Some repeat, some don't. What creates them?",
        "Our galaxy is EATING other galaxies right now. The Milky Way has consumed at least 11 smaller galaxies. And in 4.5 billion years, Andromeda will eat us",
    ],
    "collision": [
        "Our galaxy is CRASHING into Andromeda RIGHT NOW. They're approaching at 68 miles per second. In 4.5 billion years they'll merge. But no stars will actually collide",
        "The Moon was born from a PLANET crashing into Earth. 4.5 billion years ago, a Mars-sized body called Theia slammed into proto-Earth. The debris formed our Moon",
    ],
    "moon_exploration": [
        "IO has 400 ACTIVE volcanoes erupting right now. Jupiter's gravity squeezes this moon so hard, its surface is constantly melting and reforming. The most violent world we know",
        "Swimming in Titan's methane ocean would look surreal. Orange sky, no waves, thick atmosphere. You could theoretically float. Saturn hangs enormous in the sky above",
        "What's on the DARK SIDE of the Moon? China's Chang'e missions finally revealed it — ancient lava plains, massive craters, and a surprisingly different geology from the near side",
        "NASA is sending a HELICOPTER to Saturn's moon Titan in 2034. Dragonfly will fly between landing sites, sampling for organic chemistry. It could find signs of life",
        "There's a warm OCEAN hidden under Enceladus's ice shell. Hydrothermal vents on the ocean floor shoot water geysers through cracks in the ice into space. Life could thrive there",
    ],
    "perspective": [
        "What you'd see leaving Earth at the speed of light — continents shrink in seconds, the Moon passes in 1.3 seconds, Mars in 3 minutes, Jupiter in 35 minutes. Then darkness for years",
        "We're moving through space at 514,000 MPH right now. Earth orbits the Sun. The Sun orbits the galaxy. The galaxy rushes toward the Great Attractor. You're never standing still",
        "We took a PHOTO of the universe when it was a baby — the Cosmic Microwave Background. It shows the universe at 380,000 years old. Every direction looks almost identical",
    ],
    "stellar_death": [
        "This is how our Sun will DIE. In 5 billion years it'll swell to a red giant, swallowing Mercury and Venus. Then collapse into a white dwarf the size of Earth",
        "Betelgeuse could EXPLODE any minute. This red supergiant is 700 times the Sun's diameter and unstable. When it goes supernova, you'll see it in daylight for weeks",
        "We watched a star SHRED a planet into pieces. The white dwarf WD 1145+017 is actively destroying an orbiting rocky body. We can see the debris cloud transiting",
    ],
    "megastructure": [
        "Could we build a SHELL around the Sun for infinite energy? A Dyson Sphere would capture ALL the Sun's output — 400 trillion trillion watts. The engineering is theoretically possible",
        "Could we build an ELEVATOR to space? Carbon nanotubes might be strong enough. A 36,000 km cable from Earth's surface to geostationary orbit. It would revolutionize space travel",
    ],
    "physics": [
        "Fire in space burns in a PERFECT sphere. Without gravity, there's no convection — flame doesn't rise. NASA studies these spherical flames to improve combustion on Earth",
        "Astronauts age SLOWER than people on Earth. It's real — Scott Kelly aged 0.01 seconds less than his twin brother Mark after a year in space. Time dilation is not science fiction",
    ],
    "near_earth": [
        "Asteroid Apophis will pass CLOSER than our satellites in 2029. On April 13, this 370-meter rock will fly just 19,000 miles from Earth. Visible to the naked eye. No impact risk — this time",
        "The EXACT years asteroids might hit Earth — NASA tracks 2,350+ potentially hazardous objects. Bennu has a 1-in-2,700 chance of impact in 2182. We're building DART to deflect them",
    ],
    "civilization": [
        "Humans are a Type 0.7 civilization on the Kardashev scale. Type 1 controls ALL planetary energy. Type 2 harnesses an entire star. Type 3 controls a galaxy. We're not even Type 1 yet",
        "Should Pluto be a planet again? The debate is BACK. New research says the IAU's 2006 decision was based on flawed criteria. Pluto has mountains, glaciers, and a possible subsurface ocean",
    ],
    "cosmology": [
        "Dark energy is RIPPING the universe apart — and it's accelerating. 68% of the universe is this mysterious force pushing everything away. In trillions of years, even atoms will be torn apart",
        "3 ways the universe could END — Big Freeze: everything stops. Big Rip: dark energy tears matter apart. Big Crunch: gravity reverses expansion. Current evidence points to Big Freeze",
    ],
    "sun": [
        "The Sun is PAINTING Earth's sky every night. Solar wind particles hit nitrogen and oxygen in our atmosphere, exciting electrons that release photons — creating the aurora borealis",
    ],
    "exoplanet": [
        "These Super-Earth planets are BETTER for life than Earth. Slightly larger, more gravity, thicker atmospheres, more stable tectonics. Earth might not even be the best planet for life",
        "A day on the nearest Earth-like planet Proxima b — one side always faces the star, permanently bright. The other side is eternal darkness. Life would cluster in the twilight zone between",
    ],
    "speed": [
        "A blazar jet moves at 99.99% the speed of light. These beams of plasma shoot from supermassive black holes across millions of light-years. The fastest sustained objects in the universe",
    ],
    "origin": [
        "SpaceX plans to get humans to Mars in 6 months. Here's the EXACT route — launch during the Hohmann transfer window, coast for 180 days, aerobrake into Mars orbit, land with Starship",
    ],
}


def get_all_topics() -> list[str]:
    all_t = []
    for topics in TOPICS.values():
        all_t.extend(topics)
    return all_t


def get_daily_topic(exclude_recent: int = 60) -> dict:
    """Select a daily space topic — TRENDING FIRST, static fallback.

    Priority:
      1. Trending topic from Gemini (based on today's trends + viral patterns)
      2. Static TOPICS dict (if Gemini fails)
    """
    # Try trending topic first
    from core.trending import generate_trending_topic

    trending = generate_trending_topic("galactic_experiment")
    if trending and trending.get("topic"):
        logger.info(f"🔥 Galactic Experiment trending topic: {trending.get('title', '')[:50]}")
        recent = []
        if HISTORY_FILE.exists():
            try:
                recent = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
            except Exception:
                recent = []
        recent.append(trending["topic"])
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        HISTORY_FILE.write_text(json.dumps(recent[-120:], ensure_ascii=False), encoding="utf-8")
        return {
            "topic": trending["topic"],
            "category": trending.get("category", "trending"),
        }

    # Fallback: static list
    logger.info("📋 Trending failed, using static topic list...")
    recent = []
    if HISTORY_FILE.exists():
        try:
            recent = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            recent = []

    recent_set = set(recent[-exclude_recent:])
    available = []
    for cat, topics in TOPICS.items():
        for t in topics:
            if t not in recent_set:
                available.append({"topic": t, "category": cat})

    if not available:
        available = [{"topic": t, "category": c} for c, ts in TOPICS.items() for t in ts]

    chosen = random.choice(available)

    recent.append(chosen["topic"])
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(recent[-120:], ensure_ascii=False), encoding="utf-8")

    logger.info(f"🎲 Galactic Experiment topic (static): {chosen['topic'][:60]}...")
    return chosen
