"""
ShadowedHistory — Visual & Video Prompt Templates

Dark academia aesthetic: dusty archives, candlelit libraries, ancient manuscripts.
"""

# Base visual style for all ShadowedHistory frames
BASE_STYLE = (
    "cinematic dark academia aesthetic, photorealistic, 8K quality, "
    "dusty atmospheric lighting, warm candlelight glow, "
    "ancient stone textures, mysterious shadows, vertical 9:16 format"
)

# Frame prompt templates
FRAME_TEMPLATES = {
    "opening": (
        f"Close-up of an ancient leather-bound book opening slowly on a dusty wooden desk. "
        f"Candlelight flickers, dust particles float in the air. "
        f"Faded handwritten text and old maps visible on yellowed pages. "
        f"{BASE_STYLE}"
    ),
    "archive": (
        f"Vast underground archive with endless towering bookshelves disappearing into darkness. "
        f"Single beam of light illuminates floating dust. Ancient scrolls and manuscripts. "
        f"Cathedral-like stone ceiling with cobwebs. "
        f"{BASE_STYLE}"
    ),
    "artifact": (
        f"Ancient mysterious artifact displayed on velvet cloth in a dimly lit museum vault. "
        f"Golden light reflection, intricate engravings visible. "
        f"Locked iron door in the background. Top-secret classified feeling. "
        f"{BASE_STYLE}"
    ),
    "map_reveal": (
        f"Overhead shot of an ancient world map spread across a massive oak table. "
        f"Red pins mark secret locations. Compass rose and sea monsters on edges. "
        f"Candles casting warm circles of light. Explorer's tools scattered nearby. "
        f"{BASE_STYLE}"
    ),
    "ruins": (
        f"Dramatic wide shot of ancient ruins at golden hour. "
        f"Crumbling stone columns, overgrown with vines. "
        f"Mysterious fog rolling through. Shaft of sunlight breaking through clouds. "
        f"Lost civilization feel. Breathtaking and haunting. "
        f"{BASE_STYLE}"
    ),
    "manuscript": (
        f"Extreme close-up of an ancient manuscript with mysterious symbols and diagrams. "
        f"Illuminated letters in gold and red ink. Quill pen resting beside an inkwell. "
        f"Magnifying glass revealing hidden details. "
        f"{BASE_STYLE}"
    ),
    "secret_chamber": (
        f"Reveal of a hidden chamber behind a bookshelf in an old library. "
        f"Torchlight illuminates stone walls covered in ancient writings. "
        f"Gold artifacts and mysterious objects on stone shelves. "
        f"Dramatic shadows, sense of discovery. "
        f"{BASE_STYLE}"
    ),
}

# Video transition prompts
VIDEO_PROMPTS = {
    "book_opening": (
        "Cinematic slow-motion. Ancient book pages turn by themselves. "
        "Dust particles sparkle in candlelight. Camera slowly pushes in. "
        "Mysterious atmospheric music. 8 seconds."
    ),
    "archive_exploration": (
        "Smooth dolly shot through dark archive corridors. "
        "Camera moves past towering bookshelves. Light reveals hidden details. "
        "Atmospheric fog drifts through. 8 seconds."
    ),
    "artifact_reveal": (
        "Dramatic reveal. Light sweeps across ancient artifact surface. "
        "Camera circles slowly showing intricate details. "
        "Golden reflections dance on surrounding surfaces. 8 seconds."
    ),
    "map_zoom": (
        "Overhead camera slowly zooms into ancient map. Details become visible. "
        "Candle flame flickers casting moving shadows. "
        "Hidden paths and markings emerge. 8 seconds."
    ),
    "ruins_pan": (
        "Wide cinematic pan across ancient ruins. "
        "Golden hour light breaks through clouds. "
        "Fog rolls between stone columns. Birds scatter. 8 seconds."
    ),
}

# Scene sequence templates for different topic categories
SCENE_SEQUENCES = {
    "default": ["opening", "archive", "artifact", "ruins"],
    "lost_civilizations": ["ruins", "artifact", "map_reveal", "secret_chamber"],
    "forgotten_inventions": ["opening", "manuscript", "artifact", "archive"],
    "mysterious_disappearances": ["archive", "map_reveal", "ruins", "secret_chamber"],
    "dark_secrets": ["opening", "secret_chamber", "manuscript", "artifact"],
    "suppressed_discoveries": ["manuscript", "archive", "artifact", "ruins"],
    "ancient_warfare": ["ruins", "artifact", "map_reveal", "archive"],
    "forgotten_events": ["opening", "archive", "artifact", "ruins"],
    "hidden_knowledge": ["manuscript", "secret_chamber", "artifact", "map_reveal"],
}


def get_scene_sequence(category: str) -> list[str]:
    """Get the appropriate scene sequence for a topic category."""
    return SCENE_SEQUENCES.get(category, SCENE_SEQUENCES["default"])
