"""
ShadowedHistory — Visual & Video Prompt Templates

Cinematic historical scene recreation inspired by @lmg2kool (880K followers).
Style: Photorealistic AI scenes of famous historical moments.
Close-up emotion, dramatic lighting, "was this real?" engagement.
NO face reference — purely AI-generated historical characters.
"""

# Base visual style — cinematic historical recreation
BASE_STYLE = (
    "cinematic photorealistic historical scene recreation, 8K ultra detail, "
    "dramatic golden hour lighting with volumetric god rays, "
    "extreme close-up emotional detail (sweat, tears, dust), "
    "ancient textures and authentic period costumes, "
    "hyper-realistic skin pores and fabric textures, "
    "vertical 9:16 format, shot on ARRI Alexa"
)

# Frame prompt templates — @lmg2kool inspired cinematic history scenes
FRAME_TEMPLATES = {
    "epic_establishing": (
        f"Breathtaking wide aerial shot of an ancient historical location at golden hour. "
        f"Massive stone structures, thousands of people visible as tiny figures. "
        f"Dust and smoke rising. Volumetric sunlight cutting through clouds. "
        f"Scale is overwhelming — this is a pivotal moment in history. "
        f"{BASE_STYLE}"
    ),
    "dramatic_close_up": (
        f"Extreme cinematic close-up of a historical figure's face in intense emotion. "
        f"Sweat beads on forehead, sun-cracked lips, piercing determined eyes. "
        f"Dust particles floating in warm light. Background blurred (shallow depth of field). "
        f"This is the face of someone changing history. "
        f"{BASE_STYLE}"
    ),
    "artifact_reveal": (
        f"Dramatic reveal shot of an ancient artifact or monument. "
        f"Golden light sweeps across intricate carvings and engravings. "
        f"Camera angle is low, looking up — making the subject feel powerful. "
        f"Dust motes dance in the light beam. Museum-grade detail. "
        f"{BASE_STYLE}"
    ),
    "battle_scene": (
        f"Cinematic wide shot of an ancient battlefield. "
        f"Thousands of warriors in formation, banners waving, dust clouds rising. "
        f"Golden sunlight breaking through storm clouds creates dramatic lighting. "
        f"Scale is massive — this battle changed the world forever. "
        f"{BASE_STYLE}"
    ),
    "construction_scene": (
        f"Photorealistic scene of ancient construction — workers hauling massive stone blocks. "
        f"Ropes, wooden scaffolding, bronze tools. Thousands of laborers in coordinated effort. "
        f"A colossal structure rises in the background, half-complete. "
        f"The engineering genius of the ancient world on full display. "
        f"{BASE_STYLE}"
    ),
    "hidden_chamber": (
        f"Torchlight illuminates a hidden underground chamber discovered after centuries. "
        f"Gold artifacts gleam on stone shelves. Ancient murals cover the walls. "
        f"A figure holds a torch, standing in awe at the doorway. "
        f"Dust has not settled — this was just opened. "
        f"{BASE_STYLE}"
    ),
    "ruins_discovery": (
        f"Overgrown ancient ruins emerging from dense jungle at dawn. "
        f"Massive stone faces covered in moss and vines. "
        f"Morning mist swirls through crumbling corridors. "
        f"A lost civilization waiting to be found. Haunting and beautiful. "
        f"{BASE_STYLE}"
    ),
    "scroll_manuscript": (
        f"Extreme close-up of ancient hands unrolling a forbidden manuscript. "
        f"Intricate illustrations and mysterious symbols in faded ink. "
        f"Candlelight casts warm golden glow on yellowed papyrus. "
        f"This document was hidden for a reason. "
        f"{BASE_STYLE}"
    ),
    "crowd_scene": (
        f"Massive crowd of ancient people gathered for a historic event. "
        f"Thousands of faces showing emotion — awe, fear, reverence. "
        f"A central figure stands elevated, commanding attention. "
        f"The atmosphere is electric — something world-changing is happening. "
        f"{BASE_STYLE}"
    ),
    "disaster_moment": (
        f"The exact moment of a historical catastrophe captured cinematically. "
        f"Structures crumbling, people fleeing, nature unleashing fury. "
        f"Dramatic light cuts through chaos — fire, smoke, dust. "
        f"This is the moment everything changed. "
        f"{BASE_STYLE}"
    ),
}

# Video transition prompts — cinematic, dramatic pacing
VIDEO_PROMPTS = {
    "epic_dolly": (
        "Cinematic slow dolly forward through a historical scene. "
        "Camera glides past people, structures, and details. "
        "Golden sunlight streams through dust. Dramatic orchestral feel. 8 seconds."
    ),
    "emotional_close": (
        "Extreme slow-motion close-up. Sweat drops fall, eyes narrow with determination. "
        "Shallow depth of field, background melts into golden bokeh. "
        "Every pore visible. This is history being made. 8 seconds."
    ),
    "reveal_pan": (
        "Dramatic camera pan reveals the full scale of the historical scene. "
        "Starting from a detail, pulling back to show the overwhelming scope. "
        "Thousands of people, massive structures. Breathtaking. 8 seconds."
    ),
    "time_transition": (
        "Visual timelapse showing centuries passing. Stone ages, structures crumble and rebuild. "
        "Nature reclaims then releases. Day turns to night turns to centuries. "
        "The passage of time is beautiful and terrifying. 8 seconds."
    ),
    "destruction_sequence": (
        "Cinematic destruction captured in dramatic slow motion. "
        "Ancient structures break apart, dust clouds billow, the world shakes. "
        "Camera remains steady as chaos unfolds. 8 seconds."
    ),
}

# Scene sequence templates based on topic category
SCENE_SEQUENCES = {
    "default": ["epic_establishing", "dramatic_close_up", "artifact_reveal", "ruins_discovery"],
    "lost_civilizations": ["ruins_discovery", "construction_scene", "crowd_scene", "disaster_moment"],
    "forgotten_inventions": ["scroll_manuscript", "dramatic_close_up", "artifact_reveal", "hidden_chamber"],
    "mysterious_disappearances": ["epic_establishing", "crowd_scene", "disaster_moment", "ruins_discovery"],
    "dark_secrets": ["hidden_chamber", "scroll_manuscript", "dramatic_close_up", "artifact_reveal"],
    "suppressed_discoveries": ["scroll_manuscript", "artifact_reveal", "hidden_chamber", "dramatic_close_up"],
    "ancient_warfare": ["epic_establishing", "battle_scene", "dramatic_close_up", "disaster_moment"],
    "forgotten_events": ["crowd_scene", "disaster_moment", "dramatic_close_up", "ruins_discovery"],
    "hidden_knowledge": ["scroll_manuscript", "hidden_chamber", "artifact_reveal", "epic_establishing"],
}


def get_scene_sequence(category: str) -> list[str]:
    """Get the appropriate scene sequence for a topic category."""
    return SCENE_SEQUENCES.get(category, SCENE_SEQUENCES["default"])
