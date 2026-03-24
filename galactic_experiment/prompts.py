"""
Galactic Experiment — Visual & Video Prompt Templates

NASA-quality, cinematic space visuals. Photorealistic cosmic scenes.
"""

BASE_STYLE = (
    "photorealistic NASA-quality space visualization, 8K cinematic render, "
    "volumetric lighting, lens flare, deep space blacks, "
    "vibrant nebula colors, physically accurate, vertical 9:16 format"
)

FRAME_TEMPLATES = {
    "earth_from_space": (
        f"Photorealistic view of Earth from low orbit. Blue oceans, white clouds, "
        f"thin atmosphere glowing at the edge. Stars visible in the background. "
        f"ISS-like perspective. Dramatic sunlight. "
        f"{BASE_STYLE}"
    ),
    "black_hole": (
        f"Photorealistic supermassive black hole with accretion disk. "
        f"Glowing orange-red plasma spiraling inward. Gravitational lensing of background stars. "
        f"Event horizon impossibly dark. Einstein ring visible. "
        f"{BASE_STYLE}"
    ),
    "nebula": (
        f"Vast colorful nebula — pillars of creation style. "
        f"Glowing gas clouds in purple, teal, and gold. "
        f"Newborn stars sparkling within. Infinite depth. "
        f"Hubble/JWST quality. Breathtaking cosmic beauty. "
        f"{BASE_STYLE}"
    ),
    "planet_surface": (
        f"Alien planet surface at golden hour. Dramatic rocky terrain, "
        f"two moons visible in the sky, a gas giant dominating the horizon. "
        f"Atmospheric haze, volcanic activity in the distance. "
        f"{BASE_STYLE}"
    ),
    "sun_closeup": (
        f"Extreme close-up of the Sun's surface. Solar prominences erupting, "
        f"magnetic field lines visible as glowing arcs. "
        f"Convection cells boiling on the photosphere. "
        f"Parker Solar Probe perspective. Terrifying and beautiful. "
        f"{BASE_STYLE}"
    ),
    "galaxy_collision": (
        f"Two spiral galaxies in the process of merging. "
        f"Tidal tails of stars streaming outward. "
        f"Gravitational interaction creating beautiful spiraling patterns. "
        f"Billions of stars in motion. Cosmic destruction and creation. "
        f"{BASE_STYLE}"
    ),
    "asteroid_impact": (
        f"Massive asteroid entering Earth's atmosphere. "
        f"Glowing red from friction, trail of fire and debris. "
        f"Earth's curvature visible below. "
        f"Dramatic lighting, terrifying perspective. "
        f"{BASE_STYLE}"
    ),
    "deep_space": (
        f"Ultra-deep field view of thousands of galaxies at various distances. "
        f"Spirals, ellipticals, and irregular galaxies. "
        f"Faint gravitational lensing arcs. The vastness of the cosmos. "
        f"JWST-quality deep field imagery. "
        f"{BASE_STYLE}"
    ),
    "supernova": (
        f"Star going supernova — massive explosion of light and matter. "
        f"Shockwave expanding outward in a sphere. "
        f"Surrounding nebula illuminated by the blast. "
        f"Remnant neutron star at the center glowing blue. "
        f"{BASE_STYLE}"
    ),
}

VIDEO_PROMPTS = {
    "cosmic_zoom": (
        "Cinematic zoom from deep space toward a specific object. "
        "Stars streak past like warp drive. Object grows larger and more detailed. "
        "Awe-inspiring scale revelation. 8 seconds."
    ),
    "orbit_flyby": (
        "Slow orbital flyby around a celestial object. "
        "Camera circles revealing different angles. "
        "Sunlight creates dramatic shadows and highlights. "
        "Majestic and grand. 8 seconds."
    ),
    "explosion": (
        "Massive cosmic explosion — supernova, impact, or eruption. "
        "Shockwave expands outward. Debris and light scatter. "
        "Slow motion for dramatic effect. Camera shakes subtly. 8 seconds."
    ),
    "time_lapse": (
        "Cosmic time-lapse — millions of years compressed. "
        "Stars move, orbits shift, structures form and disintegrate. "
        "Ethereal and contemplative. A universe in motion. 8 seconds."
    ),
    "dramatic_reveal": (
        "Dramatic reveal — camera moves past an obstruction to show something massive. "
        "Slow push-in with building music. Scale is overwhelming. "
        "Viewer realizes how enormous the object is. Breathtaking. 8 seconds."
    ),
}

SCENE_SEQUENCES = {
    "default": ["earth_from_space", "deep_space", "nebula", "supernova"],
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
