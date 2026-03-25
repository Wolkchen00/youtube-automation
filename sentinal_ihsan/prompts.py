"""
Sentinal Ihsan — Visual Prompts & Style Constants

ENHANCED with key techniques from professional VEO 3.1 multi-scene workflow:
  ✅ IDENTITY_LOCK: Reference image anchor sentence for face consistency
  ✅ FRONT_CAMERA_POV: Smartphone front-camera POV (not cinematic)
  ✅ QUALITY_GUARD: No extra hands/fingers, no phone/device visible
  ✅ OUTFIT_LOCK: Same outfit across all scenes
  ✅ INDIRECT_SPEECH: Describe dialogue indirectly, no quotation marks
  ✅ SCENE_CONTINUITY: Each scene naturally continues from the previous
"""

# ─── Identity Lock (prepended to EVERY frame prompt for face consistency) ─────

IDENTITY_LOCK = (
    "Use the provided reference image as the main character. "
    "The person in the reference image must stay exactly the same person: "
    "same face, age, skin tone, hair color and overall appearance. "
    "Do NOT change them into a different person."
)

# ─── Character description (when reference image is not available) ────────────

CHARACTER_ANCHOR = (
    "A 25-year-old young man with short dark hair and light stubble beard. "
    "Youthful face, smooth skin, NO wrinkles, NO aging. "
    "Athletic build, wearing a casual t-shirt."
)

# ─── Front Camera POV (replaces cinematic camera descriptions) ────────────────

CAMERA_POV = (
    "Handheld smartphone front camera point-of-view, vertical 9:16 format, "
    "close-up or medium portrait framing from the front camera's view, "
    "with slight natural hand shake. "
    "The phone, any camera device, selfie stick, or hands holding a device "
    "are NOT visible in the frame — we only see what the front camera sees."
)

# ─── Anti-artifact rules ─────────────────────────────────────────────────────

QUALITY_GUARD = (
    "STRICT RULES: The character must have EXACTLY 2 hands and 5 fingers per hand. "
    "NO third hand, NO sixth finger, NO merged fingers, NO extra limbs. "
    "Face must remain consistent and youthful (25 years old). "
    "Realistic unedited smartphone UGC front-camera video frame, "
    "natural lighting, no cinematic lighting, no heavy depth of field."
)

# ─── Frame Templates (front-camera POV, concept-adaptive) ────────────────────

FRAME_TEMPLATES = {
    "intro_talking": (
        f"{IDENTITY_LOCK} "
        f"{CAMERA_POV} "
        f"{CHARACTER_ANCHOR} looking directly at the camera with excited expression, "
        f"gesturing naturally with one hand while explaining the concept. "
        f"Background matches the current concept setting. "
        f"Wearing the exact same outfit as in the reference image. "
        f"{QUALITY_GUARD}"
    ),
    "concept_reveal": (
        f"{IDENTITY_LOCK} "
        f"{CAMERA_POV} "
        f"{CHARACTER_ANCHOR} adjusting the phone angle to show the concept object/setting "
        f"behind and around him. Looking between the camera and the concept with wide eyes. "
        f"The concept is clearly visible and well-lit in the background. "
        f"Still wearing the exact same outfit as in the reference image. "
        f"{QUALITY_GUARD}"
    ),
    "interaction": (
        f"{IDENTITY_LOCK} "
        f"{CAMERA_POV} "
        f"{CHARACTER_ANCHOR} actively interacting with the concept — touching, holding, "
        f"sitting in, or examining it closely while keeping the front camera on himself. "
        f"Both hands visible doing something natural. "
        f"Still wearing the exact same outfit. Concept fills the background. "
        f"{QUALITY_GUARD}"
    ),
    "reaction_close": (
        f"{IDENTITY_LOCK} "
        f"{CAMERA_POV} "
        f"Extreme close-up of {CHARACTER_ANCHOR}'s face showing strong emotion — "
        f"shock, amazement, disgust, or laughter depending on the concept. "
        f"Shallow depth of field, concept blurred in background. "
        f"Same outfit, same person, direct eye contact with camera. "
        f"{QUALITY_GUARD}"
    ),
    "final_reveal": (
        f"{IDENTITY_LOCK} "
        f"{CAMERA_POV} "
        f"{CHARACTER_ANCHOR} pulling the phone back to show a wider view of the full concept. "
        f"The scale of the concept is fully visible. Character gestures toward it with one hand. "
        f"Still wearing the exact same outfit as in every previous scene. "
        f"This is the money shot — the most impressive angle. "
        f"{QUALITY_GUARD}"
    ),

    # Environment detail shot (no character needed)
    "concept_detail": (
        "Extreme close-up of the concept object/material showing texture and detail. "
        "Macro photography style. High detail, sharp focus. "
        "Natural smartphone camera quality. 9:16 vertical."
    ),
}

# ─── Video Prompts (front-camera POV, indirect speech, 8-second scenes) ──────

VIDEO_PROMPTS = {
    "hook_intro": (
        "Handheld vertical 9:16 front-facing camera point-of-view, as if the viewer "
        "is the phone itself at arm's length. Throughout the clip, the recording device "
        "and his hands holding it are never visible in the frame. "
        "The young man opens the video with a short, attention-grabbing hook line "
        "that immediately creates curiosity about the shocking situation. "
        "He speaks in English in an excited, energetic young male voice. "
        "His lip movements are naturally synced to his speech. "
        "He gestures naturally with one hand while keeping the phone steady. "
        "Natural ambient sound from the environment. 8 seconds."
    ),
    "concept_interaction": (
        "Same handheld vertical 9:16 front camera POV. The recording device is never visible. "
        "The young man interacts with the concept object — same person, same outfit. "
        "He describes what he is experiencing in English, reacting genuinely. "
        "Camera has slight natural hand shake as he moves. "
        "The concept object remains stable and consistent throughout the clip. "
        "Natural ambient sound. 8 seconds."
    ),
    "reaction_reveal": (
        "Same front camera POV continuous shot. The recording device is never visible. "
        "The young man pulls back to reveal the full scale of the concept, "
        "then reacts with genuine emotion — shock, disbelief, or amazement. "
        "He speaks to the camera in English describing what he sees. "
        "Same outfit, same person, natural camera movement. 8 seconds."
    ),
    "choice_question": (
        "Same front camera POV. The recording device is never visible. "
        "The young man shows three options to the camera and asks the viewers which one "
        "they would pick, in an excited voice in English. "
        "He points to each option with one hand. "
        "Same outfit, same person. Natural ambient sound. 8 seconds."
    ),
}
