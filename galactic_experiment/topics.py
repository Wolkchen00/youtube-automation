"""
Galactic Experiment — Space Topic Database

100+ space topics: hypothetical scenarios, real events, cosmic phenomena.
"""

import json
import random
from datetime import date
from pathlib import Path

from core.config import PROJECT_ROOT, logger

HISTORY_FILE = PROJECT_ROOT / "logs" / "galactic_experiment_history.json"

TOPICS = {
    "planet_tours": [
        "PLANET TOUR: Mercury — the closest planet to the Sun. No atmosphere, surface temperature swings from -180°C to 430°C. Craters everywhere. 0% water. One day lasts 59 Earth days",
        "PLANET TOUR: Venus — Earth's evil twin. 96% CO2 atmosphere, 900°F surface, sulfuric acid rain. Atmospheric pressure 90x Earth. Rotates BACKWARDS. The hottest planet in our solar system",
        "PLANET TOUR: Mars — the Red Planet. 95% CO2 atmosphere, -60°C average. Has the tallest volcano (Olympus Mons, 3x Everest). Evidence of ancient rivers. 0.38g gravity. Could humans live here?",
        "PLANET TOUR: Jupiter — the gas giant king. 89% hydrogen, 10% helium. The Great Red Spot is a 400-year-old storm larger than Earth. 79 moons. 2.5x gravity. Magnetic field 20,000x Earth's",
        "PLANET TOUR: Saturn — the ringed beauty. Rings are 99.9% water ice. Density so low it would float in water. Wind speeds of 1,800 km/h. 146 moons. Titan has liquid methane lakes",
        "PLANET TOUR: Uranus — the sideways planet. Rotates at 98° tilt, literally rolling through space. -224°C. Methane atmosphere gives it ice-blue color. 27 moons. Wind speeds of 900 km/h",
        "PLANET TOUR: Neptune — the ice giant. Wind speeds of 2,100 km/h — the fastest in the solar system. -214°C. Diamond rain in the atmosphere. Dark blue due to methane. 14 moons",
        "PLANET TOUR: Titan — Saturn's largest moon. The only moon with a thick atmosphere. Lakes of liquid methane. Orange haze. -179°C. Could harbor alien life in its subsurface ocean",
        "PLANET TOUR: Europa — Jupiter's icy moon. Under 15km of ice lies an ocean with MORE water than all of Earth's oceans combined. Potential for alien life. Geysers of water vapor",
        "PLANET TOUR: Io — Jupiter's volcanic moon. 400+ active volcanoes erupting RIGHT NOW. Sulfur lava. Tidally heated by Jupiter's gravity. The most geologically active body in our solar system",
        "PLANET TOUR: Proxima Centauri b — the closest exoplanet to Earth (4.2 light-years). In the habitable zone. Tidally locked — one side always day, one always night. Could have liquid water",
        "PLANET TOUR: TRAPPIST-1e — one of 7 Earth-sized planets orbiting a red dwarf. In the habitable zone. 39 light-years away. Possible liquid water. A year lasts only 6.1 Earth days",
        "PLANET TOUR: Kepler-442b — the most Earth-like planet we've found. 1.3x Earth's size. In the habitable zone. 1,206 light-years away. 60% chance of being rocky with liquid water",
        "PLANET TOUR: 55 Cancri e — the diamond planet. Surface covered in graphite and diamond. 2,000°C surface temperature. So close to its star, a year lasts only 18 hours. 40 light-years away",
        "PLANET TOUR: HD 189733 b — the planet where it rains GLASS sideways. 1,000°C atmosphere with 7,000 km/h winds. The glass rain is silicate particles. Beautiful deep blue color from 63 light-years",
    ],
    "what_if_scenarios": [
        "What if the Sun disappeared right now?",
        "What if a black hole appeared near Earth?",
        "What if the Moon was twice as close to Earth?",
        "What if Earth had rings like Saturn?",
        "What if we could travel at the speed of light?",
        "What if Jupiter was a star instead of a planet?",
        "What if Earth stopped rotating for one second?",
        "What if the Sun was twice as big?",
        "What if gravity was twice as strong?",
        "What if Earth had two moons?",
        "What if a neutron star entered our solar system?",
        "What if we nuked a black hole?",
        "What if the Milky Way and Andromeda collided tomorrow?",
        "What if every star in the universe went supernova at once?",
        "What if you fell into a white hole?",
    ],
    "cosmic_phenomena": [
        "A magnetar — the most powerful magnet in the universe",
        "Gamma-ray bursts — the most violent explosions since the Big Bang",
        "Rogue planets — planets flying through space with no star",
        "Neutron stars — a teaspoon weighs 6 billion tons",
        "The Great Attractor — something is pulling our entire galaxy toward it",
        "Dark energy is ripping the universe apart — and it's accelerating",
        "Quasars — objects brighter than entire galaxies",
        "Pulsars — cosmic lighthouses spinning 716 times per second",
        "The Boötes Void — a region of space with almost nothing in it for 330 million light-years",
        "Cosmic strings — theoretical cracks in space-time itself",
        "Fast Radio Bursts — mysterious signals from billions of light-years away",
        "The oldest light in the universe — the Cosmic Microwave Background",
    ],
    "black_holes": [
        "The largest black hole ever discovered — TON 618, 66 billion solar masses",
        "What happens inside a black hole — spaghettification explained",
        "Sagittarius A* — the supermassive black hole at the center of our galaxy",
        "Can a black hole destroy the universe? The information paradox",
        "Primordial black holes — born right after the Big Bang",
        "What if two supermassive black holes collided?",
        "Hawking Radiation — black holes slowly evaporate over time",
        "The first-ever photo of a black hole — M87's shadow explained",
        "Stellar black holes — created when massive stars die",
        "Can black holes be used as time machines?",
    ],
    "solar_system": [
        "Venus rains sulfuric acid and has surface temperatures of 900°F",
        "Enceladus — Saturn's moon with a warm ocean under the ice, possible life",
        "The Great Red Spot — a storm on Jupiter bigger than Earth, raging for 400+ years",
        "Mars' Olympus Mons — the largest volcano in the solar system, 3x taller than Everest",
        "The Kuiper Belt — billions of icy objects beyond Neptune",
        "The Oort Cloud — a shell of trillions of comets surrounding our solar system",
        "Pluto was demoted from planet status — but some scientists want it back",
        "The asteroid belt between Mars and Jupiter contains millions of space rocks",
        "Mercury has ice at its poles despite being closest to the Sun",
        "Ceres — the largest object in the asteroid belt has a mysterious bright spot",
    ],
    "universe_scale": [
        "The Observable Universe is 93 billion light-years across — and still expanding",
        "There are more stars in the universe than grains of sand on Earth",
        "The Laniakea Supercluster — our address in the cosmos",
        "The Cosmic Web — galaxies are connected by filaments of dark matter",
        "Empty space isn't empty — virtual particles pop in and out of existence constantly",
        "The Universe is 13.8 billion years old — here's everything that happened",
        "If the universe is a simulation, what are the pixels made of?",
        "Parallel universes — could infinite versions of you exist right now?",
        "The heat death of the universe — how everything ends",
        "Before the Big Bang — what was there? The answer might blow your mind",
    ],
    "space_exploration": [
        "Voyager 1 is STILL transmitting — from 15 billion miles away",
        "The James Webb Space Telescope — seeing the first galaxies ever formed",
        "The ISS is the most expensive thing humans have ever built — $150 billion",
        "Elon Musk's plan to put 1 million people on Mars by 2050",
        "The Artemis Program — NASA's plan to return humans to the Moon",
        "TRAPPIST-1 — a star with 7 Earth-like planets in its habitable zone",
        "The Kepler Space Telescope found over 2,700 exoplanets before retiring",
        "Parker Solar Probe — the fastest man-made object, touching the Sun",
        "The Rosetta mission — we landed on a COMET for the first time in 2014",
        "SETI — 60 years of searching for alien signals and still listening",
    ],
    "terrifying_space": [
        "A coronal mass ejection could destroy all electronics on Earth in seconds",
        "The Sun will expand into a red giant in 5 billion years — engulfing Mercury and Venus",
        "Asteroid Apophis will pass closer than our satellites in 2029",
        "A supernova within 50 light-years could sterilize our planet",
        "The vacuum metastability event — the universe could self-destruct at any moment",
        "The Fermi Paradox — where is everyone? The terrifying answer",
        "A wandering star could disrupt our solar system within a million years",
        "Space is slowly getting darker — stars are being born slower than they die",
        "If a gamma-ray burst hit Earth, half the atmosphere would disappear instantly",
        "The universe might be collapsing and we wouldn't know until it's too late",
    ],
}


def get_all_topics() -> list[str]:
    all_t = []
    for topics in TOPICS.values():
        all_t.extend(topics)
    return all_t


def get_daily_topic(exclude_recent: int = 30) -> dict:
    """Select a daily space topic, avoiding repeats."""
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
    HISTORY_FILE.write_text(json.dumps(recent[-100:], ensure_ascii=False), encoding="utf-8")

    logger.info(f"🎲 Galactic Experiment topic: {chosen['topic'][:60]}...")
    return chosen
