"""Mevsim kapisi A/B ornekleri icin uc promptu yazar (A 15 sn, B 30 sn = iki uretim).

Ortak bloklar (CAMERA, RIDER, SLIDE, WORLD, AUDIO, NEGATIVE) uc promptta BIREBIR
ayni olsun diye tek yerden birlestirilir. CAMERA, RIDER ve SLIDE kanondan
(canon/MASTER-BLOCK.md) uyarlandi; sehir yerine dag, havuz bitisi yerine tehlike bitisi.
Kaynak analiz: ../TERSINE-MUHENDISLIK.md
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
NEON = "electric cyan"
LEGWEAR = "a black high-cut one-piece swimsuit, legs bare from the hip down"

FORMAT_ILK = """## FORMAT

Create a single continuous 15-second vertical 9:16 video at 720p, 24 frames per second. Photorealistic live-action action-camera footage, not animation, not a render, not a game. ONE SINGLE UNBROKEN CONTINUOUS TAKE from the first frame to the last.

The video begins EXACTLY on the provided first image: the rider at the top of a steep drop high above Mount Fuji at sunrise, her two separate bare legs in the lower half of the frame, the transparent slide with its two {neon} rims diving straight down into a white sea of cloud, the red five-storey pagoda among pink cherry blossom just right of centre, Mount Fuji's white-tipped cone at the top of the frame. From that first frame she is already sliding fast down the drop. The camera, the legs and the slide keep exactly the look of that first image for the whole video."""

FORMAT_DEVAM = """## FORMAT

Create a single continuous 15-second vertical 9:16 video at 720p, 24 frames per second. Photorealistic live-action action-camera footage, not animation, not a render, not a game. ONE SINGLE UNBROKEN CONTINUOUS TAKE from the first frame to the last.

The video begins EXACTLY on the provided first image: the rider is inside a dark grey storm cloud, sliding fast down the transparent slide, her two bare legs and both feet in the lower third of the frame, the two {neon} rims converging ahead. Continue that same ride from that exact frame with the same camera, the same legs, the same slide and the same speed. Nothing about the camera, the rider or the slide changes."""

CAMERA = """## CAMERA

The camera is a waterproof action camera rigidly strapped to the rider's own chest. It points forward and slightly down, along the rider's own body, so the rider's legs and feet run away from the camera toward the centre of the frame.

Use an ultra-wide fisheye lens of roughly 150 degrees with strong barrel distortion. The horizon is visibly BOWED: it curves downward at the left and right edges of the frame and lifts in the middle. This bowing is present in every single frame.

The camera is bolted to the rider's torso and never moves independently of it. There is no pan, no tilt, no zoom, no dolly, no gimbal smoothing, no cinematic stabilisation. When the slide banks, the ENTIRE WORLD rotates around the rider's legs while the legs stay in the same place in the frame. When the slide drops, the horizon is thrown up and out of the top of the frame.

The camera NEVER turns back to look at the rider. No face is ever visible. No selfie angle. No mirror. No third-person view. No drone view. No exterior shot of the slide.

Keep real action-camera artefacts: rolling-shutter skew in fast rotation, auto-exposure pumping when the frame swings from dark cloud to bright sky, lens flare, water beads and snowflakes sitting on the lens and streaking away, brief blur when spray or snow hits the glass, smeared real-time motion blur."""

RIDER = """## RIDER

The only visible part of the rider is the lower body, and it is visible in every frame.

Two legs run from the bottom edge of the frame toward the centre, converging in perspective. Two bare feet sit at the end of them, close together, soles away from the camera, toes pointing up and forward. The skin is light tan, wet, and shines with the reflected colour of the slide's {neon} strips. The legs are symmetrical around the vertical centre line of the frame.

The rider wears {legwear}, soaked. Nothing else is visible. The feet and ankles are completely bare: nothing on them, no straps, no shoes, no sandals, no bindings, nothing tying the legs together.

NEVER show hands, arms, shoulders, torso, hair, or a face. There is no other person anywhere in the shot.

THE TWO LEGS ARE ALWAYS TWO. In every single frame the left leg and the right leg are separately readable, with a visible gap between them, and BOTH bare feet are separately visible. They never merge into one dark mass and never lose a foot, not even inside a cloud, a storm or a blizzard.

A thin bright {neon} edge-light runs down the inner edge of each leg, so the two legs are separated by light and never by darkness alone.

The legs react physically and continuously: toes flex and splay on a drop, ankles roll on a bank, knees lift slightly on impact, the whole lower body slides a few centimetres left or right in a hard turn and settles back."""

SLIDE = """## SLIDE

The slide is a fully TRANSPARENT clear acrylic half-pipe, wide enough for one rider. Its solid walls rise on both sides from beside the rider's hips and curve up into the lower left and lower right corners of the frame. You look straight THROUGH its floor and see the empty air and the land directly beneath the rider's feet at all times. This transparency is the single most important element in the shot and must never be lost.

Both upper rims of the half-pipe carry a continuous {neon} electroluminescent strip built into the acrylic itself. There are exactly TWO such strips, one per rim. They run away from the camera and converge at the vanishing point ahead. They are lit in EVERY SINGLE FRAME from the first to the last, at full strength, inside every cloud and every storm. Every glowing line in the frame is one of these two rims. Nothing glows in open air: there is no glowing bar across the frame, no web of extra lines, no third strip.

A thin sheet of water runs down the slide with the rider. It fans out around the hips, throws spray up past the shins, and hits the lens. The faster the ride, the more spray.

The slide is one continuous physical object. Every drop and turn is visible AHEAD before the rider reaches it, grows continuously during the approach, and is then actually travelled. It never appears out of nowhere and never breaks."""

MOTION = """## MOTION AND GRAVITY

THE RIDER IS ALWAYS MOVING FORWARD AND DOWNWARD AND ALWAYS ACCELERATING, from the very first frame to the last. The slide pitches steeply DOWN, like the first plunge of a giant water slide, and keeps plunging, banking hard left and right between drops so the whole world tilts around the legs. Near objects (trees, rocks, branches, the pagoda roof) rush past close to the slide so the speed is obvious. There is no standing start and no waiting at an edge. The ride never stops, never slows to a halt, never reverses and never floats.

THE APPROACH RULE: every cloud bank, lake, pagoda, storm, forest and snow slope must already be visible ahead before it is reached, must grow continuously as the rider closes on it, and must pass alongside or beneath the slide. Nothing appears suddenly. Nothing teleports.

THE CLOUD GATE RULE: every cloud bank the slide dives into separates two seasons. Above the cloud is one season. Inside the cloud the frame becomes an even, flat, featureless grey-white murk in which only the two legs, both feet and the two {neon} rims stay readable. Then the slide drops out of the underside of the cloud and the SAME mountain lies below in a DIFFERENT season. The season changes only inside the cloud, never in clear view."""

WORLD = """## WORLD

Mount Fuji, Japan, real, recognisable and photorealistic: the single perfect volcanic cone, seen from high above and in front of it, with a lake at its foot and the five-storey red pagoda on the wooded hillside facing it. In every clear section of the ride Mount Fuji stands beyond the rider's feet, near the centre of the frame, so the viewer always knows exactly where they are. Real atmospheric depth and honest scale: the pagoda is a small red mark, the lake is a mirror, forests are texture."""

AUDIO = """## AUDIO

No music. Ever. No soundtrack, no score, no beat.

Raw waterproof action-camera microphone, close to the rider's chest, slightly clipped and compressed. Wind roar rises continuously with speed. Water hisses directly under the rider's body. The acrylic tube rumbles and creaks. Every season sounds different: spring is soft wind and birds far below, summer is thunder and rain hammering the tube, autumn is a howling gale with leaves rattling against the acrylic, winter is a screaming blizzard and the deep growing rumble of moving snow.

THE RIDER NEVER SPEAKS. No words in any language. No talking, no narration, no counting, no exclamations made of words. Her only sounds are breath and wordless voice from the same cheap chest microphone: a sharp gasp, ragged panting, a held breath, short wordless screams.

The overall loudness climbs from the first frame to the last."""

NEGATIVE = """## NEGATIVE

NO music of any kind. NO soundtrack, score or beat.
NO spoken words, NO talking, NO narration, NO dialogue in any language. Only gasps, breathing and wordless screams.
NO edit, NO transition effect, NO jump in time. The clip is one unbroken take.
NO face. NO head. NO hair. NO hands. NO arms. NO shoulders. NO torso. NO mirror or reflection showing a person.
NO second rider. NO other people anywhere in the frame.
NO drone view. NO aerial camera. NO exterior view of the slide. NO shot showing the camera or its mount.
NO pan, NO tilt, NO zoom, NO dolly, NO orbit, NO gimbal smoothing, NO camera that moves independently of the rider's body.
NO opaque slide. NO solid floor under the rider. NO glowing line that leaves the slide surface.
NO speed ramp. NO frozen moment. NO bullet time.
NO on-screen text. NO caption. NO watermark. NO logo. NO UI.
NO flat midday lighting.
NO morphing, NO teleporting geography, NO season change in clear view: seasons change only inside a cloud.
NO cartoon, NO 3D render look, NO video-game look, NO CGI sheen, NO anime, NO illustration.
NO warped or duplicated feet. NO extra limbs. NO more than two legs. NO more than two feet.
NO ride that stops, slows to a halt, reverses or floats.
NO landing pool. NO splash-down into water at the end.
NO straps, bindings, shoes or sandals on the feet or ankles. NO legs fused into one shape.
NO action camera, chest mount or harness visible in the frame."""

ACILIS_BAHAR = """[0.0-2.5] From the very first frame the rider is already dropping fast down the steep plunge. Mount Fuji's white-tipped cone glows at sunrise at the top of the frame. The red five-storey pagoda among pink cherry blossom rushes up and past on the right, close enough to see its roof tiles. Loose pink petals stream up past her shins and across the lens. Below, the white sea of cloud rushes up toward her and the slide dives straight into it."""

TIMELINE_A = ACILIS_BAHAR + """

[2.5-5.0] The slide plunges into the cloud. The frame becomes an even, flat grey-white murk; only her two legs, both feet and the two {neon} rims stay readable. The air turns cold and the light turns blue. The first snowflakes start to hit the lens.

[5.0-7.5] She drops out of the underside of the cloud into deep winter in a full blizzard. It is the same mountain: Mount Fuji now stands entirely white, its slopes buried in snow, the pagoda below a dark shape under heavy snow, the cherry trees bare black branches. Snow streams sideways past the lens and ice crust grows along the slide rims. The storm sky is dark slate grey, so Fuji's white cone stands out clearly against it, and black bare trees and dark rocks rush past beside the slide. Mount Fuji stays visible ahead through the blizzard the whole time.

[7.5-10.0] Thundersnow: a violet-white bolt of lightning strikes the snow slope ahead and lights the whole storm for an instant, and the boom shakes the slide. A crack runs through the clear acrylic under her feet and she can see the drop through it.

[10.0-12.5] High on Fuji's flank a huge slab of snow breaks away. An avalanche pours down the mountainside toward the slide from the upper right of the frame: a towering rolling wall of snow with dark rocks and snapped black tree trunks tumbling inside it, clearly readable against the dark sky, growing every second and filling more and more of the frame.

[12.5-15.0] The slide runs straight into it. The avalanche overtakes the slide and slams into the camera: white powder smashes across the lens, the frame goes pure white, then dims to deep blue-black as the snow packs over the lens and buries the camera."""

VOICE_A = """## VOICE

[0.0-1.5] A sharp gasp, then a held breath.
[3.0-5.0] Ragged panting inside the cloud.
[7.6-8.4] A short wordless scream at the lightning crack.
[12.5-15.0] A long wordless scream swallowed by the roar of the snow, cut off as the snow buries the camera."""

END_A = """## END STATE

The camera is buried under the avalanche. The frame is almost black, with only the faint blue of packed snow pressed against the lens. The roar is dying away, muffled."""

TIMELINE_B1 = ACILIS_BAHAR + """

[2.5-4.5] The slide plunges into the cloud. The frame becomes an even, flat grey-white murk; only her two legs, both feet and the two {neon} rims stay readable. The light inside turns warm.

[4.5-7.5] She drops out of the underside of the cloud into high summer. It is the same mountain: Mount Fuji now stands dark blue-grey with no snow at all, the hills around the lake deep green, the lake glittering, heat haze over the forest. The slide sweeps low over the water.

[7.5-10.5] A summer thunderstorm towers ahead over the mountain, a black anvil cloud. Lightning bolts strike the lake beside the slide, rain hammers the acrylic and runs across the lens, and the slide bucks in the wind.

[10.5-13.0] The slide drives straight down into the black storm cloud, which grows until it fills the whole frame.

[13.0-15.0] Inside the storm cloud: an even, flat, featureless dark grey murk. Only her two legs, both feet and the two {neon} rims are readable. The slide keeps dropping, fast and straight."""

VOICE_B1 = """## VOICE

[0.0-1.5] A sharp gasp, then a held breath.
[3.0-4.5] Ragged panting inside the cloud.
[8.2-9.0] A short wordless scream as lightning hits the lake beside her.
[13.0-15.0] Fast panting in the dark cloud."""

END_B1 = """## END STATE

The rider is inside the storm cloud, still sliding fast. The frame is an even, flat dark grey murk. Her two bare legs and both feet sit in the lower third, wet and lit by the two {neon} rims that converge straight ahead into the grey. Nothing else is visible."""

TIMELINE_B2 = """[0.0-2.0] Still inside the grey murk, the slide keeps dropping. A warm orange glow grows below and the first red leaves fly up through the fog past her shins.

[2.0-5.0] She drops out of the underside of the cloud into deep autumn. It is the same mountain: Mount Fuji with a fresh white cap, its lower slopes and the lakeside blazing red and gold with maples, the red pagoda glowing among them. A gale whips a torrent of red leaves across the lens and the slide shakes in the wind.

[5.0-7.0] A violent gust: a whole wall of leaves and snapped twigs hits the slide and the lens. Ahead, already visible, a heavy white snow cloud lies across the slope, and the slide dives into it.

[7.0-8.5] Inside the snow cloud: an even, flat white murk. Only her two legs, both feet and the two {neon} rims stay readable. Snowflakes start to hit the lens.

[8.5-11.0] She drops out into deep winter in a full blizzard. Mount Fuji stands entirely white against a dark slate storm sky, the pagoda a dark shape under heavy snow, the maples bare black branches rushing past beside the slide. Thundersnow: a violet-white bolt strikes the slope ahead and the boom shakes the slide. A crack runs through the acrylic under her feet.

[11.0-13.0] High on Fuji's flank a huge slab of snow breaks away. An avalanche pours down the mountainside toward the slide from the upper right of the frame: a towering rolling wall of snow with dark rocks and snapped black tree trunks tumbling inside it, clearly readable against the dark sky, growing every second.

[13.0-15.0] The slide runs straight into it. The avalanche slams into the camera: white powder smashes across the lens, the frame goes pure white, then dims to deep blue-black as the snow packs over the lens and buries the camera."""

VOICE_B2 = """## VOICE

[0.0-2.0] Fast panting.
[5.0-5.8] A short wordless scream as the gust hits.
[9.5-10.2] A sharp wordless cry at the lightning crack.
[13.0-15.0] A long wordless scream swallowed by the roar of the snow, cut off as the snow buries the camera."""


def birlestir(*bloklar: str) -> str:
    metin = "\n\n".join(b.strip() for b in bloklar)
    return metin.format(neon=NEON, legwear=LEGWEAR) + "\n"


def main() -> None:
    ortak = [CAMERA, RIDER, SLIDE, MOTION, WORLD, AUDIO]
    promptlar = {
        "PROMPT_A15.txt": birlestir(FORMAT_ILK, *ortak,
                                    "## TIMELINE\n\n" + TIMELINE_A, VOICE_A, END_A, NEGATIVE),
        "PROMPT_B30_1.txt": birlestir(FORMAT_ILK, *ortak,
                                      "## TIMELINE\n\n" + TIMELINE_B1, VOICE_B1, END_B1, NEGATIVE),
        "PROMPT_B30_2.txt": birlestir(FORMAT_DEVAM, *ortak,
                                      "## TIMELINE\n\n" + TIMELINE_B2, VOICE_B2, END_A, NEGATIVE),
    }
    # build.py'deki uc liste: C (tetikleyici) tum metinde, A tum metinde, B rota bolumlerinde.
    liste_c = ("loop", "corkscrew", "spiral", "ribbon", "curl", "hoop", "coil", "swirl")
    liste_a = ("clip 1", "clip 2", "next clip", "previous clip", "part 1", "part 2",
               "part one", "part two", "first clip", "second clip")
    liste_b = ("cut to", "slow motion", "slow-motion", "time lapse", "timelapse", "drone shot",
               "selfie", "voiceover", "voice-over", "background music", "soundtrack",
               "third person", "third-person")
    for ad, metin in promptlar.items():
        (HERE / ad).write_text(metin, encoding="utf-8")
        tum = metin.casefold()
        rota = tum.split("## timeline")[1].split("## negative")[0]
        bulunan = ([y for y in liste_c + liste_a if y in tum]
                   + [y for y in liste_b if y in rota])
        print("%-18s %5d kelime %6d karakter  yasak:%s" % (ad, len(metin.split()), len(metin), bulunan or "yok"))


if __name__ == "__main__":
    main()
