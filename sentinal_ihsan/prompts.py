"""
Sentinal Ihsan — Visual Prompts & Style Constants

UPDATED based on user feedback:
  ✅ Character: 25-year-old young man (NOT old/wrinkled)
  ✅ Hands: Strictly 2 hands with 5 fingers each (no extra limbs)
  ✅ Settings: Dynamic — matches the concept (NOT always beach)
  ✅ Coherence: All frames describe ONE continuous scene/action
  ✅ Dialogue: Character speaks to camera, interacts with concept object
  ✅ Face consistency: Use face reference, maintain identity across frames
"""

from core.config import SENTINAL_FACE_REF

# ─── Character anchor prompt (used in ALL frames for consistency) ─────────────

CHARACTER_ANCHOR = (
    "A 25-year-old young man with short dark hair and light stubble beard. "
    "Youthful face, smooth skin, NO wrinkles, NO aging. "
    "Athletic build, wearing a casual t-shirt. "
    "CRITICAL: Exactly 2 hands with exactly 5 fingers each. "
    "No extra hands, no extra fingers, no deformed limbs. "
    "Anatomically correct human body at all times."
)

# Anti-artifact instructions appended to every prompt
QUALITY_GUARD = (
    "STRICT RULES: The character must have EXACTLY 2 hands and 5 fingers per hand. "
    "NO third hand, NO sixth finger, NO merged fingers, NO extra limbs. "
    "Face must remain consistent and youthful (25 years old). "
    "Photorealistic, 9:16 vertical, 4K, cinematic lighting."
)

# ─── Frame Templates (concept-adaptive, NOT beach-locked) ─────────────────────

FRAME_TEMPLATES = {
    # === CHARACTER + CONCEPT interaction frames ===
    "intro_talking": (
        f"{CHARACTER_ANCHOR} looking directly at the camera with excited expression, "
        f"gesturing with one hand while explaining something. "
        f"Background matches the current concept setting. "
        f"Medium close-up shot, eye-level camera. "
        f"{QUALITY_GUARD}"
    ),
    "concept_reveal": (
        f"{CHARACTER_ANCHOR} standing next to or sitting beside the concept object/setting. "
        f"Looking at the object with wide eyes, amazed expression. "
        f"The concept object is clearly visible and well-lit. "
        f"Full body or waist-up shot. "
        f"{QUALITY_GUARD}"
    ),
    "interaction": (
        f"{CHARACTER_ANCHOR} actively interacting with the concept — touching, holding, "
        f"sitting in, or examining it closely. "
        f"Both hands visible doing something natural. "
        f"Dynamic action pose. Concept fills the background. "
        f"{QUALITY_GUARD}"
    ),
    "reaction_close": (
        f"Extreme close-up of {CHARACTER_ANCHOR}'s face showing strong emotion — "
        f"shock, amazement, disgust, or laughter depending on the concept. "
        f"Shallow depth of field, concept object blurred in background. "
        f"Eye-level, direct to camera. "
        f"{QUALITY_GUARD}"
    ),
    "final_reveal": (
        f"Wide shot showing {CHARACTER_ANCHOR} and the full concept together. "
        f"The scale of the concept is fully visible. Character gestures toward it. "
        f"Dramatic lighting highlighting both character and concept. "
        f"This is the 'money shot' — the most impressive angle. "
        f"{QUALITY_GUARD}"
    ),

    # === Environment shots (no character needed) ===
    "concept_detail": (
        "Extreme close-up of the concept object/material showing texture and detail. "
        "Macro photography style. High detail, sharp focus. "
        "The material or surface is clearly identifiable. "
        "4K, photorealistic, 9:16 vertical."
    ),
    "environment_wide": (
        "Wide establishing shot of the environment matching the current concept. "
        "Could be: a bedroom, a car interior, a kitchen, a laboratory, a warehouse, "
        "an abandoned building, a garden, a city street — whatever fits the concept. "
        "Cinematic composition, dramatic lighting. "
        "4K, photorealistic, 9:16 vertical."
    ),
}

# ─── Video Transition Prompts (SEAMLESS — same scene continues) ───────────────

VIDEO_PROMPTS = {
    "talking_to_camera": (
        "The young man talks directly to camera, gesturing naturally with both hands. "
        "His mouth moves as he speaks. Background stays consistent. "
        "Camera is steady, eye-level. EXACTLY 2 hands visible. "
        "Smooth continuous motion. 8 seconds."
    ),
    "concept_interaction": (
        "The young man interacts with the concept object — touching, examining, reacting. "
        "Camera follows the action smoothly. Both hands visible, natural movement. "
        "The concept object remains stable and consistent throughout. "
        "Single continuous shot. 8 seconds."
    ),
    "reveal_reaction": (
        "Dramatic reveal — camera pulls back showing the full scale of the concept. "
        "The young man reacts with genuine emotion. "
        "Smooth camera movement, cinematic lighting. "
        "8 seconds."
    ),
    "close_up_emotion": (
        "Slow zoom into the young man's face showing intense emotion. "
        "Eyes wide, expression matching the concept mood. "
        "Shallow depth of field, smooth camera. "
        "8 seconds."
    ),
}
