"""
AImagine — Visual Style Constants (DIY Crafts Fixed-Camera Style)

Inspired by @diycraftstvofficial (5.2M IG followers, 319K YouTube subs):
  - Fixed tripod camera, single area, ground-level angle
  - 1-2 people working (seen from behind or mid-distance)
  - Transformation: empty/messy → beautiful finished result
  - No narration, ambient music only
  - Categories: garden, room, pergola, topiary, outdoor kitchen, etc.

Key AI insight: YouTube description says "Altered or synthetic content"
→ They use AI image/video generation (likely Kling/Runway/VEO)
→ Fixed camera + distant workers = hides AI artifacts perfectly
"""

# ─── Base style for fixed-camera DIY frames ─────────────────────────────────
# Critical: FIXED tripod camera, same angle all 4 frames
BASE_STYLE = (
    "ultra high quality, 4K resolution, photorealistic ground-level photograph, "
    "fixed tripod camera angle, stationary perspective, "
    "natural daylight, golden hour warmth, slight depth of field, "
    "9:16 vertical format, "
    "the EXACT same camera position and angle in every frame"
)

# Worker/person style — key to realism
# They appear mid-distance, usually from behind, wearing casual work clothes
PERSON_STYLE = (
    "1-2 people working, seen from behind or side angle at mid-distance (3-5 meters away), "
    "wearing casual dark work clothes (black t-shirt, work pants, work gloves), "
    "physically doing hands-on work — planting, building, arranging, decorating, "
    "NOT posing, NOT looking at camera, naturally absorbed in their task, "
    "slightly blurred due to movement (timelapse feel)"
)

# Video generation style — fixed camera timelapse
VIDEO_STYLE = (
    "fixed tripod camera, absolutely stationary perspective, no camera movement at all, "
    "time-lapse style with workers moving at 4x speed, "
    "natural daylight subtly changing, clouds moving in sky, "
    "construction/decoration progress visible, satisfying transformation, "
    "photorealistic, 9:16 vertical format"
)

# Environment categories
GARDEN_ENV = "lush green lawn, well-maintained landscaping, modern house in background"
BACKYARD_ENV = "spacious backyard with fence, trees, natural setting"
FRONTYARD_ENV = "front yard of modern home, driveway visible, street trees"
INDOOR_ENV = "empty room with clean walls, hardwood floor, natural window light"
OUTDOOR_DINING_ENV = "outdoor patio area, string lights, tropical plants"
LUXURY_ENV = "luxury villa exterior, manicured grounds, palm trees, warm stone walls"

# Caption templates — simple, descriptive, no hype
CAPTION_TEMPLATES = [
    "Front Yard Landscaping Transformation 🌿",
    "Backyard Pergola Lounge Build 🏡",
    "Backyard Border Turned Into a Stunning Garden 🌷",
    "Luxury Topiary Garden Transformation 🦚",
    "Room Makeover From Start to Finish ✨",
    "Outdoor Kitchen Build Complete 🍳",
    "Dream Garden Created From Scratch 🌺",
    "Patio Transformation in One Day ☀️",
]
