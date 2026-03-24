"""
Galactic Experiment — Visual & Video Prompt Templates

UPDATED: Seamless planet exploration format.
Each day: Approach → Orbit → Atmosphere Entry → Surface Exploration
All frames feel like ONE continuous journey (no jumps/breaks).

Style: NASA-quality + cinematic CGI, VEO3 narration in background.
"""

# Base visual style
BASE_STYLE = (
    "photorealistic NASA-quality space visualization, 8K cinematic render, "
    "volumetric lighting, lens flare, deep space blacks, "
    "vibrant planetary colors, physically accurate, vertical 9:16 format"
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

# ─── Video Prompts (SEAMLESS transitions — single continuous journey) ─────────

VIDEO_PROMPTS = {
    "approach_to_orbit": (
        "Seamless cinematic journey — spacecraft approaches a planet. "
        "Stars streak past as speed increases. The planet fills the viewport. "
        "Camera smoothly transitions to orbital view. Single continuous shot. "
        "No cuts. Breathtaking scale revelation. 8 seconds."
    ),
    "orbit_to_descent": (
        "Continuous descent from orbit into atmosphere. "
        "The planet's surface detail increases as altitude drops. "
        "Atmospheric glow surrounds the frame edges. Clouds rush past. "
        "Single unbroken shot, no cuts. Building tension. 8 seconds."
    ),
    "descent_to_surface": (
        "Final descent to the planet's surface. Breaking through the last cloud layer. "
        "The alien landscape reveals itself. Camera lands smoothly and pans across "
        "the dramatic terrain. Single continuous shot. The journey is complete. 8 seconds."
    ),
    "cosmic_zoom": (
        "Cinematic zoom from deep space toward a specific object. "
        "Stars streak past like warp drive. Object grows larger. "
        "Awe-inspiring scale revelation. 8 seconds."
    ),
    "orbit_flyby": (
        "Slow orbital flyby around a celestial object. Camera circles showing angles. "
        "Sunlight creates dramatic shadows. Majestic and grand. 8 seconds."
    ),
    "explosion": (
        "Massive cosmic explosion. Shockwave expands outward. "
        "Debris and light scatter. Slow motion for dramatic effect. 8 seconds."
    ),
    "dramatic_reveal": (
        "Camera moves past obstruction to show something massive. "
        "Scale is overwhelming. Viewer realizes the enormous size. 8 seconds."
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
