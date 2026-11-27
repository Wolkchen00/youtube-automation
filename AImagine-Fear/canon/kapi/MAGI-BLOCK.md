# MAGI BLOCK , KAPI KONSEPTI (MAGI-2 surumu)

27 Kasim 2026, Ihsan karari: aimagine MAGI-2'ye (Kie magi-2/image-to-video, 1080p,
17,6 kredi/sn, 15 sn = 264 kredi) gecti. Bu dosya `KONSEPT: kapi` rotalarinin MAGI-2
promptunu kurar (build.py `PROMPT_MAGI.txt`). Seedance promptu (`MASTER-BLOCK.md`,
`PROMPT.txt`) dokunulmadan duruyor; profil `720p` ile eski yol hala calisir.

Neden ayri dil. 26 Kasim karsilastirmasinda MAGI-2 promptdaki zaman araliklarini AYRI
CEKIM sayip tam o sinirda sicradi: "[2.0-4.0]" sinirinda, 2,0 sn'de, yurume yolundan
kaydirak agzina kesme gibi gecti. Sand AI'nin kendi prompt yeniden yazicisi
(MAGI-2-preview inference/prompt_enhancement t2v.md, i2v.md) da ayni seyi soyluyor:
kesme sayisi olay sayisini izler; tek kesintisiz plan "tek ana olay, tek bagli ortam,
tek basit kamera davranisi" ister; ilk kare mutlak taban; olumsuz dil yerine olumlu
hedef. Kurallar:

1. Hicbir yerde saniye, zaman araligi, vurus etiketi YOK. build.py rotanin BEATS ve
   VOICE satirlarindaki [a-b] araliklarini siler ve sirayla tek akista birlestirir.
2. Butun video TEK olay: tek kaydirakta tek kesintisiz inis. Yuruyus de o hareketin
   parcasi, ayri sahne degil.
3. Olumlu dil. Dislama yalniz sondaki kisa KEEP OUT blogunda.
4. Ses satiri "continuing to the very last frame" ile biter.
5. Prompt 15.000 karakter sinirinin altinda kalir (build --check 14.800'de durdurur).
6. (27 Kas test 1) "harness", "buckle", "strap" ismi YAZILMAZ: model ismi gorup
   gogse toka cizdi (ilk kare temizdi). Kadrajin alt kenari olumlu tarif edilir.

Tokenlar MASTER-BLOCK.md ile ayni: <<DURATION>>, <<NEON>>,
<<LEGWEAR>>, <<WEATHER>>, <<CITY>>, <<LANDMARK>>, <<FELAKET>>. Cozunurluk sabit
1080x1920: MAGI-2 yalniz 1080p uretir.

## FORMAT

A single continuous <<DURATION>>-second vertical 9:16 shot at 1080x1920, one unbroken real-time take from the first frame to the last, recorded by a waterproof action camera fixed to the rider's chest during one real ride. Natural documentary footage: photorealistic live action with real light and real materials, restrained true-to-life saturation, protected highlights, open shadow detail, stable exposure apart from natural auto-exposure pumping, fine real action-camera grain.

The shot starts exactly on the provided starting image and keeps its framing, lens, colours and exposure: the rider walking barefoot, mid-stride, along a narrow walkway of clear glass high above <<LANDMARK>> in <<CITY>>, her two separate bare legs and feet stepping forward in the lower half of the frame, the open mouth of the transparent slide with its two <<NEON>> rims a few steps ahead, diving down toward a sea of cloud. Motion is already under way in the first frame: she is walking, and the walk flows straight into the ride as one movement.

## CAMERA

The camera is a waterproof action camera rigidly fixed to the rider's chest, pointing forward and steeply down along her body, so her legs and feet run away from the camera toward the centre of the frame. The bottom edge of the frame shows only the plain, smooth, seamless fabric of her swimwear at her hips, one even colour from edge to edge. Ultra-wide fisheye lens of roughly 150 degrees with strong barrel distortion: the horizon is visibly bowed in every frame, curving down at the left and right edges and lifting in the middle.

The camera moves only with the rider's torso. It bobs gently with each walking step and settles the moment she sits. When the slide banks, the whole world rotates around her legs while the legs stay in the same place in the frame. When the slide drops, the horizon is thrown up toward the top of the frame. The view always looks forward along her body.

Real action-camera artefacts: rolling-shutter skew in fast rotation, auto-exposure pumping between bright sky and dark cloud, lens flare, water beads and grit sitting on the lens and streaking away, brief blur when spray hits the glass, smeared real-time motion blur.

## RIDER

Her lower body is the only part of the rider in the frame, and it is visible in every frame. While she walks, the camera looks down at her two bare legs and feet stepping forward one after the other on the clear glass, each wet sole landing flat with a small splash. Once she sits in the slide, her two legs run from the bottom edge of the frame toward the centre, converging in perspective, two bare feet close together at the end of them, soles away from the camera, toes pointing up and forward. Light tan wet skin shines with the colour of the <<NEON>> rims. The legs are symmetrical around the vertical centre line of the frame.

She wears <<LEGWEAR>>, soaked. Her feet and ankles are bare skin.

In every frame there are exactly two legs with a clear gap between them and two separately visible bare feet, inside the cloud and inside the disaster alike. A thin bright <<NEON>> edge-light runs down the inner edge of each leg, so the two legs are always separated by light.

The legs react physically and continuously: toes flex and splay on a drop, ankles roll on a bank, knees lift slightly on impact, the whole lower body slides a few centimetres left or right in a hard turn and settles back. She is alone on the slide.

## SLIDE

The slide is a fully transparent clear acrylic half-pipe, wide enough for one rider. Its solid walls rise on both sides from beside her hips and curve up into the lower left and lower right corners of the frame. Through its clear floor the empty air and the land directly beneath her feet are visible at all times; this transparency is the single most important element of the shot.

Each of the two upper rims carries one continuous <<NEON>> electroluminescent strip built into the acrylic itself, exactly two strips, running away from the camera and converging at the vanishing point ahead. Both are lit at full strength in every frame, inside the cloud and inside the disaster. These two rims are the only glowing lines in the frame, and both stay on the slide surface.

A thin sheet of water runs down the slide with her. It fans out around her hips, throws spray up past her shins and onto the lens, and the faster the ride, the more spray.

The slide is one continuous physical object. Every drop and turn is visible ahead before she reaches it, grows steadily as she approaches, and is then actually travelled.

## THE RIDE

The whole video is one continuous ride on this one slide, from the glass walkway down through the cloud into the disaster over the same city, seen through the same chest camera without a break. The walk is short and brisk: a few steps, and in one fluid movement she sits straight down into the slide mouth feet first and pushes off, so walking and sliding are one unbroken motion. The walkway is a narrow flat strip of clear glass in open air, and through it there is only empty air and the land far below.

From the moment she sits she is always moving forward and downward and always accelerating until the end. The slide pitches steeply down like the first plunge of a giant water slide and keeps plunging, banking hard left and right between drops so the whole world tilts around her legs, with near objects rushing past close to the slide so the speed is obvious.

Everything she meets, cloud, buildings, rock, water, storm and debris, is visible ahead first, grows steadily as she closes on it, and passes beside or beneath the slide.

The cloud bank she dives into is a gate between two worlds. Above it is <<WEATHER>>. Inside it the frame becomes a brief, even, flat grey-white murk where only her two legs, both feet and the two <<NEON>> rims stay readable. She drops out of its underside and the same place lies below, caught in <<FELAKET>>. The world changes only inside the cloud.

## WORLD

<<CITY>>, real, recognisable and photorealistic, seen from high above and in front of <<LANDMARK>>. In every clear moment of the ride <<LANDMARK>> stands beyond her feet near the centre of the frame, so the viewer always knows exactly where they are, and it stays recognisable even inside the disaster.

Above the cloud the weather is <<WEATHER>>. Below the cloud the same place is caught in <<FELAKET>>: darker, harder and more contrasted, a dark sky, dark debris and one bright hazard, so every threat reads clearly against its background. Real atmospheric depth and honest scale.

## SOUND

Raw waterproof action-camera microphone close to her chest, slightly clipped and compressed, carrying only the real sounds of the ride: wet bare footsteps slapping on the glass and loud high wind from the first moment, wind roar rising with speed, water hissing directly under her body, the acrylic rumbling and creaking, open calm air above the cloud, a muffled hush inside it, and below it the roar of the disaster growing louder and closer until the end.

The rider's only sounds are wordless breath and voice from the same chest microphone: gasps, ragged panting, held breath and short wordless screams. She says no words. The overall loudness climbs from start to end.

## KEEP OUT

One unbroken take with music-free, speech-free sound. Keep out of the frame and the sound: any edit, transition or jump in time; slow motion or a frozen moment; music or spoken words; the rider's face, head, hair, hands, arms, shoulders or torso; any other person; any gear or equipment worn on her body; a drone, aerial or outside view of the slide; a railing, an opaque slide or an opaque walkway; glowing lines in open air; on-screen text, captions, logos or watermarks; a cartoon, CGI or video-game look; extra, fused or warped legs or feet; shoes or bindings on the feet; a ride that stops, reverses or floats; a landing pool or a happy ending.
