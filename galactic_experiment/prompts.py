"""
Galactic Experiment — Visual & Video Prompt Templates

OTHERWORLDLY COSMIC CONTENT
Inspired by @winterpens.art (bioluminescent spiritual energy, perfect loops)
and @natia_ai (cinematic sci-fi megastructures, epic scale).

Style: Supernatural, ethereal space art — like being in another dimension.
Colors: Deep midnight blues, bioluminescent cyan/gold/pink, nebula purples.
Feel: Every frame is wallpaper-worthy.
"""

# Base visual style — otherworldly cosmic dreamscape
BASE_STYLE = (
    "otherworldly cosmic art, 8K cinematic render, supernatural atmosphere, "
    "deep midnight blues and purples with bioluminescent highlights (neon cyan, glowing gold, soft pink), "
    "glowing bokeh particles floating through space, ethereal mist and nebula clouds, "
    "volumetric lighting with god rays, lens flare from distant stars, "
    "every surface has subtle glow, crystalline and bioluminescent textures, "
    "spiritual serene magical atmosphere, vertical 9:16 format, wallpaper-worthy composition"
)

# Seamless loop constants
LOOP_AESTHETIC = (
    "Background elements in constant subtle motion: star particles drifting slowly, "
    "gas clouds flowing, energy pulses rippling, glowing particles rising. "
    "Camera performs slow drift. Colors shift through the spectrum. "
    "Entire scene breathes with cosmic energy — alive, not static."
)

# ─── Planet Tour Frame Templates (SEAMLESS single-journey feel) ───────────────

PLANET_TOUR_FRAMES = {
    "approach": (
        "Photorealistic view from a spacecraft approaching {planet}. "
        "The planet grows larger in the viewport, stars visible around it. "
        "Subtle engine glow reflects off the hull. Distance: 100,000 km. "
        "The planet's {atmospheric_detail} visible ahead. "
        f"{BASE_STYLE}"
    ),
    "orbit": (
        "Orbital view of {planet} from 500km altitude. "
        "{surface_detail} visible below. "
        "The curvature of the planet fills the frame. "
        "{special_feature} dramatically visible. "
        "Sunlight creates a sharp terminator line between day and night side. "
        f"{BASE_STYLE}"
    ),
    "atmosphere_entry": (
        "Descending through {planet}'s atmosphere. "
        "{atmosphere_description}. "
        "Plasma trail from atmospheric friction glowing around the edges of frame. "
        "The surface becomes increasingly detailed below. "
        "A sense of speed and discovery. "
        f"{BASE_STYLE}"
    ),
    "surface": (
        "Standing on the surface of {planet}. "
        "{surface_scene}. "
        "The sky shows {sky_description}. "
        "Dramatic panoramic view stretching to the horizon. "
        "This is what it actually looks like on this world. "
        f"{BASE_STYLE}"
    ),
}

# ─── Generic Frame Templates (for What-If scenarios and general topics) ───────

FRAME_TEMPLATES = {
    "earth_from_space": (
        f"Photorealistic view of Earth from low orbit. Blue oceans, white clouds, "
        f"thin atmosphere glowing at the edge. Stars visible in background. "
        f"ISS perspective. Dramatic sunlight. {BASE_STYLE}"
    ),
    "black_hole": (
        f"Photorealistic supermassive black hole with accretion disk. "
        f"Glowing orange-red plasma spiraling inward. Gravitational lensing visible. "
        f"Event horizon impossibly dark. Einstein ring. {BASE_STYLE}"
    ),
    "nebula": (
        f"Vast colorful nebula — pillars of creation style. "
        f"Glowing gas clouds in purple, teal, and gold. Newborn stars within. "
        f"JWST quality. Breathtaking cosmic beauty. {BASE_STYLE}"
    ),
    "planet_surface": (
        f"Alien planet surface at golden hour. Dramatic rocky terrain, "
        f"two moons in sky, gas giant on horizon. Volcanic activity in distance. "
        f"{BASE_STYLE}"
    ),
    "sun_closeup": (
        f"Extreme close-up of the Sun's surface. Solar prominences erupting, "
        f"magnetic field lines as glowing arcs. Convection cells boiling. "
        f"Parker Solar Probe view. Terrifying and beautiful. {BASE_STYLE}"
    ),
    "galaxy_collision": (
        f"Two spiral galaxies merging. Tidal tails of stars streaming out. "
        f"Billions of stars in motion. Cosmic destruction and creation. {BASE_STYLE}"
    ),
    "asteroid_impact": (
        f"Massive asteroid entering Earth's atmosphere. Glowing red from friction, "
        f"trail of fire and debris. Earth's curvature below. {BASE_STYLE}"
    ),
    "deep_space": (
        f"Ultra-deep field view of thousands of galaxies. Spirals, ellipticals. "
        f"Gravitational lensing arcs. The vastness of the cosmos. JWST quality. {BASE_STYLE}"
    ),
    "supernova": (
        f"Star going supernova — massive explosion of light and matter. "
        f"Shockwave expanding outward. Remnant neutron star glowing blue. {BASE_STYLE}"
    ),
}

# ─── Video Prompts (OTHERWORLDLY + SEAMLESS LOOP) ─────────────────────────────

VIDEO_PROMPTS = {
    "approach_to_orbit": (
        "Cinematic spacecraft approach to a planet. "
        "Bioluminescent particles drift past the camera like cosmic fireflies. "
        "The planet grows larger, glowing with ethereal energy at its edges. "
        "Stars streak past, nebula clouds in background shift colors slowly. "
        f"{LOOP_AESTHETIC} "
        "Single continuous shot. 8 seconds."
    ),
    "orbit_to_descent": (
        "Descending from orbit into an alien atmosphere. "
        "Aurora-like energy ribbons wrap around the planet. "
        "Glowing particles swirl in the atmospheric currents. "
        "Crystal structures visible on the surface below, catching starlight. "
        f"{LOOP_AESTHETIC} "
        "Building wonder and awe. 8 seconds."
    ),
    "descent_to_surface": (
        "Landing on an alien world. The surface is alive with bioluminescent detail. "
        "Crystalline formations glow from within, alien flora pulses with light. "
        "Ethereal mist rolls across the terrain. Two moons visible in the alien sky. "
        f"{LOOP_AESTHETIC} "
        "Jaw-dropping alien landscape reveal. 8 seconds."
    ),
    "cosmic_zoom": (
        "Cosmic zoom from deep space toward a celestial object. "
        "Stars and galaxies streak past like warp speed. Glowing particles trail behind. "
        "Massive scale revelation — the object is impossibly large. "
        f"{LOOP_AESTHETIC} "
        "Awe-inspiring scale. 8 seconds."
    ),
    "orbit_flyby": (
        "Slow majestic flyby around a cosmic structure. "
        "Bioluminescent nebula clouds frame the scene. "
        "Light shifts through blue → purple → cyan spectrum. "
        "Subtle god rays pierce through cosmic dust. "
        f"{LOOP_AESTHETIC} "
        "Wallpaper-worthy cinematic beauty. 8 seconds."
    ),
    "explosion": (
        "Massive cosmic event — supernova, collision, or energy burst. "
        "Shockwave of glowing particles expands outward. "
        "Colors shift from white-hot center to deep purple edges. "
        "Debris becomes glowing bioluminescent fragments. "
        f"{LOOP_AESTHETIC} "
        "Dramatic slow motion. 8 seconds."
    ),
    "dramatic_reveal": (
        "Camera drifts past cosmic dust to reveal something impossibly massive. "
        "A megastructure, a celestial body, or an alien world. "
        "Scale is overwhelming — tiny particles in foreground show how big it is. "
        "Everything glows with ethereal energy. "
        f"{LOOP_AESTHETIC} "
        "The viewer gasps. 8 seconds."
    ),
}

# ─── Scene Sequences ──────────────────────────────────────────────────────────

SCENE_SEQUENCES = {
    "default": ["earth_from_space", "deep_space", "nebula", "supernova"],
    "planet_tour": ["approach", "orbit", "atmosphere_entry", "surface"],
    "what_if_scenarios": ["earth_from_space", "sun_closeup", "asteroid_impact", "deep_space"],
    "cosmic_phenomena": ["nebula", "deep_space", "supernova", "galaxy_collision"],
    "black_holes": ["deep_space", "black_hole", "galaxy_collision", "black_hole"],
    "solar_system": ["earth_from_space", "planet_surface", "sun_closeup", "deep_space"],
    "universe_scale": ["deep_space", "nebula", "galaxy_collision", "deep_space"],
    "space_exploration": ["earth_from_space", "planet_surface", "nebula", "deep_space"],
    "terrifying_space": ["earth_from_space", "asteroid_impact", "supernova", "black_hole"],
}


def get_scene_sequence(category: str) -> list[str]:
    return SCENE_SEQUENCES.get(category, SCENE_SEQUENCES["default"])
