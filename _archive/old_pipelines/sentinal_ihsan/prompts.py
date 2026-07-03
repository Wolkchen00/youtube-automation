"""
Sentinal Ihsan — Visual Prompts & Style Constants (VEO3 Lite)

4-SCENE FLOW:
  Scene 1: SETUP — Character silently prepares the materials to start the process
  Scene 2: ACTION — Actively working on it, full body visible, no speaking
  Scene 3: PROGRESS — Close to finishing, focused and satisfied, no speaking
  Scene 4: REVEAL — Final completed result is clearly shown at the end

VEO3-SPECIFIC:
  ✅ Each video prompt describes silent physical action (NO speech)
  ✅ Continuous physical motion in every clip
  ✅ Front-camera POV with natural handheld shake
  ✅ Identity lock + quality guard on every frame

REALISM UPDATE (v2):
  Inspired by @talswildworld + @engndnsmn — outdoor UGC selfie style.
  Key changes: iPhone 15 Pro RAW quality, real outdoor locations,
  authentic product textures, natural lighting with imperfections.
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
    "Youthful face, smooth skin with subtle natural pores, NO wrinkles, NO aging. "
    "Athletic build, wearing a casual black t-shirt with realistic fabric wrinkles."
)

# ─── Front Camera POV (REALISM UPDATE) ────────────────────────────────────────

CAMERA_POV = (
    "Shot on iPhone 15 Pro Max, ProRAW, vertical 9:16 format, front camera selfie. "
    "Close-up or medium portrait framing from the front camera's perspective. "
    "Slight natural hand shake, subtle lens flare from sun, "
    "micro motion blur on fast movements. "
    "The phone, any camera device, selfie stick, or hands holding a device "
    "are NOT visible in the frame — we only see what the front camera sees. "
    "NOT a 3D render, NOT CGI — real smartphone UGC photography."
)

# ─── Quality Guard (REALISM UPDATE) ──────────────────────────────────────────

QUALITY_GUARD = (
    "STRICT: EXACTLY 2 hands, 5 fingers each. "
    "NO third hand, NO sixth finger, NO merged fingers. "
    "Face must stay youthful (25 years old), consistent across scenes. "
    "Real iPhone photo quality: subtle skin blemishes, natural pores, "
    "realistic fabric wrinkles on clothing, authentic shadows. "
    "Natural outdoor lighting — golden hour warmth or overcast diffusion. "
    "NOT studio lighting, NOT perfect plastic skin."
)

# ─── Realism Constants (NEW) ─────────────────────────────────────────────────

REALISM_OUTDOOR = (
    "Real outdoor location — NOT a studio set. "
    "Authentic environment: backyard, rooftop, park, street, beach, or forest. "
    "Natural ambient elements: wind in hair, real sky with clouds, "
    "grass or concrete texture, environmental depth and distance. "
    "Background has natural blur (bokeh) from phone camera."
)

REALISM_PRODUCT = (
    "The product/material is REAL and AUTHENTIC — not toy-like or CGI. "
    "Real liquid has natural viscosity, splash physics, and reflections. "
    "Real metal has authentic weight, scratches, and surface reflections. "
    "Real paint has drips, uneven coverage, and genuine color saturation. "
    "Products have brand labels, manufacturing imperfections, and realistic scale. "
    "Materials interact with light naturally — matte vs glossy vs metallic surfaces."
)

# ─── 4 Frame Templates (SETUP → ACTION → PROGRESS → REVEAL) ─────────────────

FRAME_TEMPLATES = {
    "hook_intro": (
        f"{IDENTITY_LOCK} "
        f"{CAMERA_POV} "
        f"{CHARACTER_ANCHOR} preparing the materials with a focused and determined expression. "
        f"He is in a real outdoor location that matches the concept. "
        f"{REALISM_OUTDOOR} "
        f"He is completely silent, NOT speaking. "
        f"The concept item/product is visible beside him — real, tangible, with authentic texture. "
        f"{REALISM_PRODUCT} "
        f"Wearing the exact same outfit as in the reference image. "
        f"{QUALITY_GUARD}"
    ),
    "action_start": (
        f"{IDENTITY_LOCK} "
        f"{CAMERA_POV} "
        f"{CHARACTER_ANCHOR} is actively engaged in the physical action (pouring, painting, placing, touching, opening). "
        f"CRITICAL: His whole body is visible and his arms are naturally connected to his torso. NO floating arms, NO disembodied hands. "
        f"Both hands are naturally engaged with realistic grip and finger positioning. "
        f"{REALISM_PRODUCT} "
        f"The concept is changing due to his action — real physics: liquid flows, paint drips, "
        f"material deforms naturally. {REALISM_OUTDOOR} "
        f"His face shows effort and concentration. He is silent, NOT speaking. Same outfit. "
        f"{QUALITY_GUARD}"
    ),
    "progress_check": (
        f"{IDENTITY_LOCK} "
        f"{CAMERA_POV} "
        f"Close-up of {CHARACTER_ANCHOR} face showing satisfaction and focus as he nears completion of the process. "
        f"He is smiling slightly at the progress. NO shocked expression, NO wide eyes, NO open mouth. "
        f"The concept result is partially visible in the background with realistic detail. "
        f"{REALISM_OUTDOOR} "
        f"Sweat or excitement flush on face for authenticity. He is silent, NOT speaking. "
        f"Same outfit. "
        f"{QUALITY_GUARD}"
    ),
    "final_reveal": (
        f"{IDENTITY_LOCK} "
        f"{CAMERA_POV} "
        f"{CHARACTER_ANCHOR} has pulled back to show the FULL result in a wider frame. "
        f"The complete concept transformation is clearly and fully visible — impressive, detailed, and shareable. "
        f"{REALISM_PRODUCT} "
        f"He is gesturing toward it proudly with natural hand positioning. He is silent, NOT speaking. "
        f"{REALISM_OUTDOOR} "
        f"Same outfit. Golden hour lighting highlights the result beautifully. "
        f"This is the money shot — the most impressive, photorealistic angle showing exactly what was made. "
        f"{QUALITY_GUARD}"
    ),
}

# ─── 4 VEO3 Video Prompts (silent action + continuous motion) ──────────────────

VIDEO_PROMPTS = {
    "hook_video": (
        "Handheld vertical 9:16 front-camera POV, shot on iPhone 15 Pro Max, natural hand shake. "
        "Real outdoor location with natural ambient sound — wind, birds, distant traffic. "
        "Throughout the clip, no phone or recording device is visible. "
        "The young man silently prepares to start the process, showing the materials to the camera. "
        "He is completely silent, NOT speaking, just focused on the setup. "
        "He gestures with one hand while the concept item is visible beside him. "
        "Real sunlight creates natural shadows on his face. "
        "He has a determined, focused expression. 5 seconds."
    ),
    "action_video": (
        "Same iPhone front camera POV. Same outdoor location. No recording device visible. "
        "The young man is actively interacting with the concept (pouring, painting, placing, opening). "
        "CRITICAL: His full torso is visible and his arms are connected naturally to his body. NO floating arms. "
        "He is completely silent, NOT speaking. "
        "IMPORTANT: The product/material behaves with REAL physics — liquid splashes naturally, "
        "paint drips realistically, metal clinks with authentic sound. "
        "Camera has natural shake from his movement. The concept visibly changes with realistic detail. "
        "Same outfit, same environment. Continuous scene — no jump cuts. 5 seconds."
    ),
    "reaction_video": (
        "Same iPhone front camera POV. Same outdoor location. No recording device visible. "
        "The young man continues working, pausing slightly to look at the progress with satisfaction. "
        "He is completely silent, NOT speaking. "
        "His facial expression is calm, focused, and slightly smiling — NO shocked face, NO open mouth. "
        "He looks between the camera and the result naturally. "
        "Wind moves his hair slightly. "
        "Same outfit, same environment, same natural lighting. 5 seconds."
    ),
    "payoff_video": (
        "Same iPhone front camera POV. Same outdoor location. No recording device visible. "
        "The young man pulls back to clearly show the final result in a wider shot — revealing the "
        "full, completed transformation exactly as it is finished. "
        "He is completely silent, NOT speaking. "
        "He gestures toward the result proudly, then looks back at camera with a natural smile. "
        "The result looks REAL, IMPRESSIVE, and SHAREABLE — perfect final shot showing what was made. "
        "Golden hour sunlight highlights everything. Natural hand movements. "
        "Same outfit, same environment. 5 seconds."
    ),
}
