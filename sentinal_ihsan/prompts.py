"""
Sentinal Ihsan — Visual Prompts & Style Constants (VEO3 Overhaul)

6-SCENE FLOW:
  Scene 1: HOOK — Character grabs attention, explains concept
  Scene 2: SETUP — Shows the concept/product/material to camera
  Scene 3: ACTION 1 — Starts interacting (pouring, painting, building)
  Scene 4: ACTION 2 — Deeper interaction (fully immersed, touching, feeling)
  Scene 5: REACTION — Genuine surprise/shock at the result
  Scene 6: PAYOFF — Final reveal + call-to-action ("which would you pick?")

VEO3-SPECIFIC:
  ✅ Each video prompt includes speech description (VEO3 generates audio)
  ✅ Continuous physical motion in every clip
  ✅ Front-camera POV with natural handheld shake
  ✅ Identity lock + quality guard on every frame
"""

# ─── Identity Lock (prepended to EVERY frame prompt for face consistency) ─────

IDENTITY_LOCK = (
    "Use the provided reference image as the main character. "
    "The person in the reference image must stay exactly the same person: "
    "same face, age, skin tone, hair color and overall appearance. "
    "Do NOT change them into a different person."
)

# ─── Character description ────────────────────────────────────────────────────

CHARACTER_ANCHOR = (
    "A 25-year-old young man with short dark hair and light stubble beard. "
    "Youthful face, smooth skin, NO wrinkles, NO aging. "
    "Athletic build, wearing a casual t-shirt."
)

# ─── Front Camera POV ─────────────────────────────────────────────────────────

CAMERA_POV = (
    "Handheld smartphone front camera point-of-view, vertical 9:16 format, "
    "close-up or medium portrait framing from the front camera's view, "
    "with slight natural hand shake. "
    "The phone, any camera device, selfie stick, or hands holding a device "
    "are NOT visible in the frame — we only see what the front camera sees."
)

# ─── Quality Guard ────────────────────────────────────────────────────────────

QUALITY_GUARD = (
    "STRICT: EXACTLY 2 hands, 5 fingers each. "
    "NO third hand, NO sixth finger, NO merged fingers. "
    "Face must stay youthful (25 years old), consistent across scenes. "
    "Realistic smartphone UGC quality, natural lighting."
)

# ─── 6 Frame Templates (HOOK → SETUP → ACTION × 2 → REACTION → PAYOFF) ──────

FRAME_TEMPLATES = {
    "hook_intro": (
        f"{IDENTITY_LOCK} "
        f"{CAMERA_POV} "
        f"{CHARACTER_ANCHOR} looking directly at the camera with an excited, wide-eyed expression. "
        f"He is in a specific setting that matches the concept. "
        f"His mouth is slightly open as if starting to speak. "
        f"Background clearly shows the setting and environment. "
        f"Wearing the exact same outfit as in the reference image. "
        f"{QUALITY_GUARD}"
    ),
    "concept_setup": (
        f"{IDENTITY_LOCK} "
        f"{CAMERA_POV} "
        f"{CHARACTER_ANCHOR} has turned the phone to also show the concept object/material/setup "
        f"behind and around him. He is pointing or gesturing toward it with one hand. "
        f"The concept is clearly visible, well-lit, and recognizable. "
        f"His expression shows anticipation. Same outfit. "
        f"{QUALITY_GUARD}"
    ),
    "action_start": (
        f"{IDENTITY_LOCK} "
        f"{CAMERA_POV} "
        f"{CHARACTER_ANCHOR} has started the physical action — his hands are actively "
        f"interacting with the concept (pouring, painting, placing, touching, opening). "
        f"Both hands are naturally engaged. The concept is changing due to his action. "
        f"His face shows effort and concentration. Same outfit. "
        f"{QUALITY_GUARD}"
    ),
    "action_deep": (
        f"{IDENTITY_LOCK} "
        f"{CAMERA_POV} "
        f"{CHARACTER_ANCHOR} is now deeply interacting with the concept — sitting in it, "
        f"surrounded by it, or holding the result. The transformation/effect is clearly visible. "
        f"His expression shifts between shock and excitement. Same outfit. "
        f"{QUALITY_GUARD}"
    ),
    "reaction_shock": (
        f"{IDENTITY_LOCK} "
        f"{CAMERA_POV} "
        f"Close-up of {CHARACTER_ANCHOR} face showing intense reaction — jaw dropped, "
        f"wide eyes, hand over mouth, looking between the camera and the concept result. "
        f"The concept result is partially visible in the background. "
        f"Same outfit. Genuine emotional reaction. "
        f"{QUALITY_GUARD}"
    ),
    "final_reveal": (
        f"{IDENTITY_LOCK} "
        f"{CAMERA_POV} "
        f"{CHARACTER_ANCHOR} has pulled back to show the FULL result in a wider frame. "
        f"The complete concept transformation is visible — impressive and shareable. "
        f"He is gesturing toward it proudly. Same outfit. "
        f"This is the money shot — the most impressive angle. "
        f"{QUALITY_GUARD}"
    ),
}

# ─── 6 VEO3 Video Prompts (with speech + continuous motion) ──────────────────

VIDEO_PROMPTS = {
    "hook_video": (
        "Handheld vertical 9:16 front-camera POV, natural hand shake. "
        "Throughout the clip, no phone or recording device is visible. "
        "The young man speaks directly to the front camera in English in an excited, "
        "energetic voice. He opens with a short attention-grabbing hook line that "
        "immediately creates curiosity about what he is about to do. "
        "His lip movements are naturally synced to speech. "
        "He gestures with one hand while keeping the phone steady. "
        "His eyes are wide with excitement. Natural ambient sound. 8 seconds."
    ),
    "setup_video": (
        "Same handheld vertical front camera POV. No recording device visible. "
        "The young man adjusts the camera angle to reveal the concept setup behind him. "
        "He walks toward it, still talking in English, describing what it is and what he plans to do. "
        "The camera moves with him — natural walking motion with handheld shake. "
        "He points at the concept and looks between camera and the concept. "
        "Same outfit, same voice. Natural ambient sound. 8 seconds."
    ),
    "action_start_video": (
        "Same front camera POV. No recording device visible. "
        "The young man starts the physical action — he is actively interacting with "
        "the concept (pouring, painting, placing, opening). Both his hands do something natural. "
        "He narrates what he is doing in English — describing the texture, the feeling, the weight. "
        "Camera has natural shake from his movement. The concept visibly changes. "
        "Same outfit, same voice. Ambient sound of the action. 8 seconds."
    ),
    "action_deep_video": (
        "Same front camera POV. No recording device visible. "
        "The young man is now deeply immersed in the interaction — he continues "
        "the physical action and reacts to the result. He speaks in English describing "
        "what is happening, how it feels, and his genuine surprise. "
        "His body movement is natural — shifting weight, leaning in, stepping back. "
        "The concept transformation is clearly visible and progressing. "
        "Same outfit, same voice. 8 seconds."
    ),
    "reaction_video": (
        "Same front camera POV. No recording device visible. "
        "The young man stops the action and looks at the result with genuine shock. "
        "He speaks in English — reacting to what just happened with disbelief and excitement. "
        "His facial expressions are dramatic — jaw drop, wide eyes, hand over mouth. "
        "He looks between the camera and the result multiple times. "
        "His voice gets higher with surprise. Same outfit. 8 seconds."
    ),
    "payoff_video": (
        "Same front camera POV. No recording device visible. "
        "The young man pulls back to show the final result in a wider shot. "
        "He speaks in English — wrapping up, showing off the complete transformation, "
        "and asking viewers to comment their reaction or choose between options. "
        "He gestures toward the result proudly, then looks back at camera with a smile. "
        "Natural hand movements and body language. Same outfit, same voice. 8 seconds."
    ),
}
