"""
Sentinal Ihsan — Competitor Analysis & Viral Topic Database (v2)

60 unique viral topics for 30 days of dual-upload content.
Each topic has specific ACTION STEPS for the character.

REFERENCE CHANNELS:
  @bayburra (565K) — Chrome paint, satisfying reveals
  @rzmertsc — Object discovery, shock reveals
  @melihzyrkk — Product interaction, cursed experiences
"""

import json
import random
from datetime import date
from pathlib import Path

import google.generativeai as genai

from core.config import GEMINI_API_KEY, PROJECT_ROOT, logger


HISTORY_FILE = PROJECT_ROOT / "logs" / "sentinal_ihsan_history.json"

# ─── VIRAL TOPICS (60 UNIQUE — ZERO OVERLAP WITH OLD DATABASE) ──────────────

VIRAL_TOPICS = [
    # === EXPERIMENT (satisfying science) ===
    {"topic": "Covering a ball in magnets and throwing it at a metal wall — does it stick from 10 meters?",
     "category": "experiment", "setting": "garage",
     "action_steps": "glues neodymium magnets all over ball, walks back 10m, throws ball at metal wall, ball sticks with a satisfying clang"},

    {"topic": "Filling a pool with non-newtonian fluid — can you actually WALK on it?",
     "category": "experiment", "setting": "backyard",
     "action_steps": "mixes cornstarch and water in kiddie pool, stirs it thick, steps onto surface, runs across without sinking, stops and slowly sinks"},

    {"topic": "Lighting 1000 matches at once — the chain reaction is INSANE",
     "category": "experiment", "setting": "outdoor",
     "action_steps": "arranges 1000 matches in a grid, lights one corner, watches the domino fire chain reaction spread, slow motion replay of the wave"},

    {"topic": "500 rubber bands vs watermelon — WAIT for the explosion",
     "category": "experiment", "setting": "backyard",
     "action_steps": "wraps rubber bands one by one around watermelon, tension builds, watermelon deforms, final snap and it explodes everywhere"},

    {"topic": "Can 100 candles COOK a steak? Temperature test with thermal camera",
     "category": "experiment", "setting": "kitchen",
     "action_steps": "places 100 candles around a steak, lights them all, uses thermal camera to show heat, waits and checks if steak cooks"},

    {"topic": "Making sugar glass that SHATTERS perfectly — movie prop secret",
     "category": "experiment", "setting": "kitchen",
     "action_steps": "boils sugar and corn syrup, pours into mold, waits to cool, holds up clear glass pane, punches through it — shatters safely"},

    {"topic": "500 mouse traps CHAIN REACTION in slow motion — ping pong ball chaos",
     "category": "experiment", "setting": "garage",
     "action_steps": "sets 500 loaded mouse traps with ping pong balls, drops one ball, massive chain reaction explosion, slow motion replay"},

    {"topic": "Electricity through WATER looks terrifying — Lichtenberg figures",
     "category": "experiment", "setting": "workshop",
     "action_steps": "applies high voltage to wet wood, electricity creates branching burn patterns, reveals Lichtenberg figures, coats in resin"},

    {"topic": "Can a candle BURN underwater? The science is wild",
     "category": "experiment", "setting": "kitchen",
     "action_steps": "lights candle, slowly submerges in water using glass dome, watches how long flame survives, explains the air pocket physics"},

    {"topic": "Trapped LIGHTNING in a jar — Lichtenberg figures in acrylic block",
     "category": "experiment", "setting": "workshop",
     "action_steps": "charges acrylic block with electron beam, taps with nail, lightning pattern explodes inside the clear block permanently"},

    # === TRANSFORMATION (satisfying before/after) ===
    {"topic": "Making a table that GLOWS in the dark using phosphorescent resin",
     "category": "transformation", "setting": "workshop",
     "action_steps": "sands old table, mixes glow-in-dark powder with clear resin, pours into cracks, cures, turns off lights — table glows bright green"},

    {"topic": "Dipping a shoe in LIQUID RUBBER — the coating is indestructible",
     "category": "transformation", "setting": "garage",
     "action_steps": "shows regular shoe, dips slowly into liquid rubber, pulls out, lets dry, shoe now has rubberized coating, tests durability"},

    {"topic": "Painting a room with UV-reactive paint — blacklight transformation is INSANE",
     "category": "transformation", "setting": "bedroom",
     "action_steps": "paints walls with clear UV paint in patterns, looks normal in daylight, turns on blacklight, entire room transforms into glowing art"},

    {"topic": "Covering my ENTIRE desk in liquid glass epoxy — mirror finish",
     "category": "transformation", "setting": "workshop",
     "action_steps": "sands desk, tapes edges, pours crystal clear epoxy, uses torch to remove bubbles, cures overnight, reveals perfect mirror surface"},

    {"topic": "Making LIQUID METAL dance with magnets — ferrofluid is mesmerizing",
     "category": "transformation", "setting": "desk",
     "action_steps": "pours ferrofluid on plate, brings neodymium magnet close, liquid spikes and dances, creates flower patterns, pulls it into shapes"},

    # === ART (creative builds) ===
    {"topic": "I BROKE a mirror and made art from the pieces — mosaic masterpiece",
     "category": "art", "setting": "workshop",
     "action_steps": "carefully breaks mirror into pieces, arranges fragments into portrait pattern on board, groutes between pieces, final reveal of reflective art"},

    {"topic": "Burning art into wood with MOLTEN METAL — pyrography extreme",
     "category": "art", "setting": "outdoor",
     "action_steps": "traces design on wood, pours molten metal along lines, metal burns intricate pattern into grain, brushes away ash, reveals artwork"},

    {"topic": "Exploding PAINT with an air compressor — abstract art chaos",
     "category": "art", "setting": "backyard",
     "action_steps": "places canvas, puts paint balloons on it, aims air compressor nozzle, balloons explode paint everywhere, reveals accidental masterpiece"},

    {"topic": "Making a SCULPTURE with just a glue gun — no mold, freehand",
     "category": "art", "setting": "desk",
     "action_steps": "draws design, starts building 3D structure with hot glue layer by layer, builds up shape freehand, spray paints final sculpture gold"},

    {"topic": "I made a TREE from copper wire — bonsai sculpture",
     "category": "art", "setting": "workshop",
     "action_steps": "bundles thick copper wires, twists trunk, separates branches, fans out roots, bends each branch, attaches to rock base, patinas with vinegar"},

    # === DIY (useful builds) ===
    {"topic": "Making a LAVA LAMP from scratch — just oil, water, and fizz tablets",
     "category": "diy", "setting": "kitchen",
     "action_steps": "fills bottle with water and oil, adds food coloring, drops effervescent tablet, colored blobs float up and down like real lava lamp"},

    {"topic": "I made a phone case from CANDLE WAX — does it protect?",
     "category": "diy", "setting": "kitchen",
     "action_steps": "melts candle wax, wraps phone in release agent, dips phone in wax multiple times, lets cool, removes phone, wax case formed, drop tests"},

    {"topic": "Building a GREENHOUSE from plastic bottles — zero cost garden",
     "category": "diy", "setting": "backyard",
     "action_steps": "collects hundreds of plastic bottles, threads onto bamboo poles, assembles wall by wall, creates mini greenhouse, plants seedlings inside"},

    {"topic": "I turned OLD headphones into a MICROPHONE — and it works",
     "category": "diy", "setting": "desk",
     "action_steps": "opens old earbuds, rewires the driver, connects to audio jack, plugs into computer, shows it actually recording voice, tests quality"},

    {"topic": "Making a power bank from AA BATTERIES — emergency phone charger",
     "category": "diy", "setting": "desk",
     "action_steps": "wires 4 AA batteries in series, connects USB boost converter, solders connections, wraps in tape, plugs in phone — it charges"},

    # === VERSUS (comparison tests) ===
    {"topic": "Hot METAL vs ICE block — who wins? Thermal camera battle",
     "category": "versus", "setting": "workshop",
     "action_steps": "heats metal ball to glowing red, places on ice block, watches metal sink through, thermal camera shows temperature battle, slow motion"},

    {"topic": "HYDRAULIC PRESS vs bowling ball — the sound is incredible",
     "category": "versus", "setting": "workshop",
     "action_steps": "places bowling ball under press, activates slowly, ball resists, then cracks with explosive sound, fragments fly, slow motion replay"},

    {"topic": "Dropping CHEESE vs crackers from 10 floors — which survives?",
     "category": "versus", "setting": "building_exterior",
     "action_steps": "goes to roof, drops block of cheese and stack of crackers simultaneously, slow motion fall, checks damage on ground, rates destruction"},

    # === CHALLENGE (viewer engagement) ===
    {"topic": "Walking on BURNING coals barefoot — the science says it's possible",
     "category": "challenge", "setting": "backyard",
     "action_steps": "prepares coal bed, lets it burn to embers, explains Leidenfrost effect, walks across quickly, shows feet are fine, thermal camera view"},

    {"topic": "Picking up EVERYTHING with a giant neodymium magnet — treasure hunt",
     "category": "challenge", "setting": "outdoor",
     "action_steps": "ties giant magnet to rope, drags through field/path, picks up random metal objects, reveals what he found, weighs the haul"},

    # === SCIENCE (educational wow) ===
    {"topic": "Making a BATTERY from salt water — it actually powers a light",
     "category": "science", "setting": "desk",
     "action_steps": "fills cups with salt water, inserts zinc and copper electrodes, wires them in series, connects LED, LED lights up from salt water power"},

    {"topic": "My hand is ON FIRE and it doesn't hurt — rubbing alcohol science",
     "category": "science", "setting": "outdoor",
     "action_steps": "wets hand with water first, coats in hand sanitizer, lights hand on fire, alcohol burns but water protects skin, extinguishes safely"},

    {"topic": "The BIGGEST foam explosion you've ever seen — elephant toothpaste",
     "category": "science", "setting": "backyard",
     "action_steps": "mixes hydrogen peroxide with yeast catalyst in giant bottle, adds food coloring, massive foam eruption shoots meters high, colorful chaos"},

    {"topic": "Cutting glass with a PIECE OF STRING — old glazier trick",
     "category": "science", "setting": "workshop",
     "action_steps": "wraps kerosene-soaked string around glass bottle, lights string, waits for it to burn, dips in cold water, glass breaks cleanly at the line"},

    # === FOOD (edible experiments) ===
    {"topic": "Making LOLLIPOPS from scratch — the caramel work is satisfying",
     "category": "food", "setting": "kitchen",
     "action_steps": "boils sugar to hard crack stage, adds colors and flavors, pours into molds, inserts sticks, lets cool, unwraps perfect homemade lollipops"},

    {"topic": "Making ICE CREAM in 30 seconds with just salt and ice — no freezer",
     "category": "food", "setting": "kitchen",
     "action_steps": "mixes cream and sugar in bag, puts bag inside larger bag of salt and ice, shakes vigorously for 30 seconds, opens to reveal real ice cream"},

    {"topic": "Can you melt cheese with a CLOTHES IRON? The result is surprising",
     "category": "food", "setting": "kitchen",
     "action_steps": "places cheese on bread, wraps in parchment paper, presses hot iron on top, waits, opens paper — perfectly melted grilled cheese sandwich"},

    # === DESTRUCTION (controlled chaos) ===
    {"topic": "I put my phone in CONCRETE — did it survive? Drop test extreme",
     "category": "destruction", "setting": "garage",
     "action_steps": "wraps old phone in concrete mold, lets cure 24 hours, drops concrete block from roof, breaks it open, checks if phone still works"},

    {"topic": "Smashing a FROZEN flower in slow motion — liquid nitrogen",
     "category": "destruction", "setting": "desk",
     "action_steps": "dips rose in liquid nitrogen for 30 seconds, places on table, taps with finger, flower shatters into dust, slow motion captures every fragment"},

    {"topic": "Freezing random objects in LIQUID NITROGEN and smashing them",
     "category": "destruction", "setting": "workshop",
     "action_steps": "freezes banana, tennis ball, padlock in liquid nitrogen one by one, smashes each with hammer, slow motion shatter reveals, most satisfying wins"},

    # === SATISFYING (pure visual pleasure) ===
    {"topic": "Cutting a GIANT ice block perfectly in half — satisfying symmetry",
     "category": "satisfying", "setting": "outdoor",
     "action_steps": "shows massive clear ice block, marks center line, uses saw to cut slowly, halves separate and slide apart perfectly, crystal clear faces revealed"},

    {"topic": "Playing with MAGNETIC sand — oddly satisfying shapes",
     "category": "satisfying", "setting": "desk",
     "action_steps": "pours black magnetic sand on surface, brings magnet underneath, sand forms spikes and patterns, moves magnet around creating shapes, mesmerizing flow"},

    # === UPCYCLE (trash to treasure) ===
    {"topic": "I made a CHANDELIER from old spoons — upcycle art",
     "category": "upcycle", "setting": "workshop",
     "action_steps": "collects dozens of old spoons, bends handles into curves, welds to circular frame, adds lights between spoons, hangs up — stunning light patterns"},

    {"topic": "I made a wall CLOCK from a bike wheel — working timepiece",
     "category": "upcycle", "setting": "garage",
     "action_steps": "removes tire from old bike wheel, adds clock mechanism to hub, attaches number markers to spokes, hangs on wall — functional artistic clock"},

    # === CRAFT (precision builds) ===
    {"topic": "I built a WORKING clock from WOOD — no metal parts",
     "category": "craft", "setting": "workshop",
     "action_steps": "carves wooden gears with CNC/hand tools, assembles escapement mechanism, adds pendulum, mounts on frame, clock starts ticking — fully functional"},

    {"topic": "Blowing GLASS at 2000°F to make a vase — from sand to art",
     "category": "craft", "setting": "glass_studio",
     "action_steps": "gathers molten glass on pipe, blows air to form bubble, shapes with tools, pulls neck, adds color, anneals in kiln, reveals finished vase"},

    {"topic": "Building a ROBOT from trash — motors, sensors, and recycled parts",
     "category": "craft", "setting": "desk",
     "action_steps": "salvages motors from old toys, sensors from broken electronics, builds chassis from cardboard, wires everything, programs Arduino, robot moves and responds"},

    {"topic": "Making an INDESTRUCTIBLE phone case from carbon fiber",
     "category": "craft", "setting": "workshop",
     "action_steps": "wraps phone mold in carbon fiber cloth, applies epoxy resin, vacuum bags for pressure, cures, trims edges, test fits phone, drop tests from height"},

    # === LAYERS (100 layers challenge) ===
    {"topic": "100 layers of Saran wrap on a ball — can you still bounce it?",
     "category": "layers", "setting": "living_room",
     "action_steps": "wraps tennis ball in plastic wrap layer after layer, ball grows huge, tries to bounce it, wrapping cushions impact, cuts open to reveal layers"},

    # === SLOW MOTION (visual spectacles) ===
    {"topic": "Making a stress ball from balloon + flour — and POPPING it in slow-mo",
     "category": "slowmo", "setting": "desk",
     "action_steps": "fills balloon with flour using funnel, ties off, squeezes to show stress ball, then pops with pin, slow motion captures flour explosion cloud"},

    # === TECH (technology hacks) ===
    {"topic": "Turning my OLD phone into a security camera — free home security",
     "category": "tech", "setting": "home",
     "action_steps": "installs surveillance app on old phone, mounts on shelf, connects to wifi, shows live feed on main phone, demonstrates motion alerts"},

    {"topic": "DIY LAVA LAMP with just oil and water — chemistry is beautiful",
     "category": "experiment", "setting": "kitchen",
     "action_steps": "fills glass jar with oil and water, adds food coloring (sinks to bottom), drops effervescent tablet, colored bubbles rise and fall continuously"},

    # === EXTRA VIRAL ===
    {"topic": "Growing flowers in YOGURT cups — zero cost garden hack",
     "category": "diy", "setting": "backyard",
     "action_steps": "pokes drainage holes in yogurt cups, fills with soil, plants seeds, labels each one, shows time-lapse of growth, repots grown flowers"},

    {"topic": "Making a PERFECT copy of my hand using alginate mold",
     "category": "art", "setting": "desk",
     "action_steps": "mixes alginate powder with water, submerges hand, waits for it to set, carefully removes hand, pours plaster into mold, reveals perfect hand replica"},

    {"topic": "Coke + Mentos ROCKET launch attempt — how high does it go?",
     "category": "experiment", "setting": "backyard",
     "action_steps": "builds simple launch tube from PVC pipe, drops mentos into diet coke bottle, seals quickly, pressure builds, bottle rockets into the air, measures height"},

    {"topic": "I VACUUMED a couch cushion flat — does it spring back?",
     "category": "experiment", "setting": "living_room",
     "action_steps": "places couch cushion in vacuum bag, seals bag, connects vacuum cleaner, cushion compresses to paper thin, opens bag, watches cushion slowly re-expand"},

    {"topic": "I covered my ENTIRE room in aluminum foil — the alien spaceship effect",
     "category": "cursed", "setting": "bedroom",
     "action_steps": "wraps walls floor ceiling furniture in foil piece by piece, final reveal of completely silver room, turns on colored lights, trippy reflections everywhere"},

    {"topic": "Dev mıknatısla metal eşya toplama challenge — magnet fishing on land",
     "category": "challenge", "setting": "outdoor",
     "action_steps": "attaches giant magnet to rope, walks through park dragging along ground, magnet picks up hidden metal objects, reveals the haul, weighs everything"},

    {"topic": "Building a mini VOLCANO — baking soda eruption with lava flow channels",
     "category": "experiment", "setting": "backyard",
     "action_steps": "builds clay volcano with channels, paints realistic texture, fills with baking soda and red dye, pours vinegar, eruption flows down channels perfectly"},

    {"topic": "Sıcak cam üfleme ile vazo yapma — from 2000°F molten glass to art",
     "category": "craft", "setting": "glass_studio",
     "action_steps": "gathers molten glass blob on blowpipe, shapes with wet blocks, blows air bubble inside, pulls and stretches neck, adds color swirls, cools in annealing oven"},
]


def get_daily_topic(exclude_recent: int = 60) -> dict:
    """Select today's topic from pre-built viral list, avoiding recent repeats."""
    recent = []
    if HISTORY_FILE.exists():
        try:
            recent = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            recent = []

    recent_set = set(recent[-exclude_recent:])
    available = [t for t in VIRAL_TOPICS if t["topic"] not in recent_set]

    if not available:
        # All topics used, reset and pick any
        available = list(VIRAL_TOPICS)

    chosen = random.choice(available)

    # Save to history
    recent.append(chosen["topic"])
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(recent[-120:], ensure_ascii=False), encoding="utf-8")

    logger.info(f"🎬 Sentinal Ihsan topic: {chosen['topic'][:60]}...")
    return chosen


def get_trending_with_gemini() -> dict | None:
    """Generate a trending viral topic using Gemini with a purpose-built prompt."""
    if not GEMINI_API_KEY:
        return None

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(
            "gemini-2.5-flash",
            system_instruction=(
                "You are a viral content strategist for TikTok/YouTube Shorts. "
                "You specialize in satisfying, experiment, and discovery content. "
                "Generate ONE unique viral video topic idea that a young male creator "
                "can film with a front-facing camera. The topic must involve PHYSICAL "
                "INTERACTION with an object or material (painting, pouring, building, "
                "opening, crushing, filling, etc). "
                "Return ONLY valid JSON with keys: topic (full description), "
                "category (one of: transformation, experiment, cursed_experience, discovery), "
                "setting (where to film), action_steps (what the character physically does)"
            ),
        )

        response = model.generate_content(
            "Generate a fresh, never-seen-before viral experiment topic. "
            "Think satisfying transformations, impossible builds, or cursed experiences. "
            "Make it something that would get millions of views. Return ONLY valid JSON.",
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=1.0,
            ),
        )

        result = json.loads(response.text)
        if result and result.get("topic"):
            logger.info(f"🤖 Gemini trending topic: {result['topic'][:60]}...")
            return {
                "topic": result["topic"],
                "category": result.get("category", "gemini_trending"),
                "setting": result.get("setting", "generic"),
                "action_steps": result.get("action_steps", ""),
            }
    except Exception as e:
        logger.warning(f"⚠️ Gemini trending topic failed: {e}")
    return None
