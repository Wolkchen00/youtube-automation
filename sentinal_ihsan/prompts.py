"""
Sentinal Ihsan — Visual Prompts & Style Constants

Based on @sentinal.ihsan.daily Instagram analysis:
  - Sentinal Ihsan (your face) appears in EVERY video
  - Settings: beaches, boats, ocean, cliffs, golden hour
  - Style: hyper-realistic, cinematic, emotional storytelling
  - Colors: deep ocean blues, golden sunset warmth, dramatic skies
  - Camera: POV/selfie angles, close-ups, handheld feel
"""

# Face reference is loaded from env: SENTINAL_FACE_REF

# ─── Frame Templates (fallback when Gemini fails) ─────────────────────────────

FRAME_TEMPLATES = {
    # Reaction/discovery shots (uses face reference)
    "reaction_shock": (
        "Close-up portrait of a young man with dark hair and beard, "
        "eyes wide with shock and amazement, mouth slightly open, "
        "standing on a beautiful beach at golden hour, ocean waves behind, "
        "cinematic lighting, photorealistic, 9:16 vertical, 4K"
    ),
    "reaction_awe": (
        "Close-up of a young man with dark hair and beard, "
        "looking down at something incredible in his hands with pure wonder, "
        "golden sunset light on his face, ocean background blurred, "
        "photorealistic, 9:16 vertical, 4K"
    ),
    "experiment_setup": (
        "Wide shot of a young man with dark hair and beard on a beach, "
        "kneeling next to something unusual on the wet sand, "
        "golden hour lighting, dramatic sky, waves lapping nearby, "
        "cinematic composition, photorealistic, 9:16 vertical, 4K"
    ),
    "action_shot": (
        "Dynamic action shot of a young man with dark hair and beard "
        "reaching into clear turquoise ocean water, splash visible, "
        "sunset colors reflecting on water, dramatic moment captured, "
        "photorealistic, 9:16 vertical, 4K"
    ),
    "result_reveal": (
        "Close-up of a young man holding something amazing up to camera, "
        "face showing pure excitement, ocean sunset behind, "
        "golden light illuminating both the man and the discovery, "
        "photorealistic, cinematic, 9:16 vertical, 4K"
    ),
    "mind_blown": (
        "Young man on a boat looking straight at camera with mind-blown expression, "
        "one hand on his head in disbelief, vast ocean stretching behind, "
        "dramatic sunset sky with orange and purple clouds, "
        "photorealistic, cinematic, 9:16 vertical, 4K"
    ),
    # Environment shots (no face needed)
    "ocean_wide": (
        "Dramatic aerial view of turquoise ocean with a small boat in the center, "
        "crystal clear water revealing sandy bottom, golden hour light, "
        "cinematic composition, 9:16 vertical, 4K"
    ),
    "beach_discovery": (
        "Something mysterious glowing on a wet sandy beach at sunset, "
        "ocean waves receding, footprints leading to the discovery, "
        "dramatic sky, cinematic lighting, 9:16 vertical, 4K"
    ),
    "underwater": (
        "Crystal clear underwater scene, shafts of golden sunlight piercing through, "
        "coral and marine life visible, turquoise water, "
        "photorealistic, cinematic, 9:16 vertical, 4K"
    ),
}

# ─── Video Transition Prompts ─────────────────────────────────────────────────

VIDEO_PROMPTS = {
    "discovery_reveal": (
        "Dramatic reveal moment — camera pulls back slowly showing the full scene, "
        "golden hour light, ocean sounds, emotional music swell. 8 seconds."
    ),
    "rescue_action": (
        "Intense action shot — reaching into water, splash effects, urgency, "
        "dramatic music, handheld camera movement, cinematic. 8 seconds."
    ),
    "ocean_beauty": (
        "Sweeping cinematic ocean shot — waves, sunset reflections, peaceful yet dramatic, "
        "golden hour light, slow camera drift. 8 seconds."
    ),
    "reaction_closeup": (
        "Slow zoom into face showing amazement and awe, golden light on face, "
        "ocean background blurred, emotional music. 8 seconds."
    ),
    "motorcycle_ride": (
        "POV motorcycle ride along coastal road, ocean view on one side, "
        "wind effect, golden hour, cinematic speed. 8 seconds."
    ),
}
