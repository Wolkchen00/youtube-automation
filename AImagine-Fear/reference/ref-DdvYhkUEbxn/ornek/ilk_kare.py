"""Mevsim kapisi icin ILK KARE fotografi uretir (nano-banana-2, 9:16, 2K).

Neden: metinden video (A15 v1, B30_1 v1) bacaklari ve kaydiragi bozdu: bileklerde
siyah kayis, kaynasmis tek bacak, kaydiraga ait olmayan yatay isik cizgisi, dik
olmayan egim. Ilk kare kilidi kompozisyonu birinci kareden sabitler; A ve B ayni
kareden baslarsa A/B karsilastirmasi da adil olur.
Kullanim: python ilk_kare.py <etiket>   -> ornek/ilk_kare_<etiket>.png
"""
import sys
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3]))  # Projeler/Youtube
sys.path.insert(0, str(HERE.parents[2] / "tools"))
import kie_uret  # noqa: E402

PROMPT = """Photorealistic still frame from a real waterproof action camera, vertical 9:16. Ultra-wide 150-degree fisheye lens with strong barrel distortion; the horizon is bowed and sits in the top fifth of the frame.

The camera is strapped to a rider's chest and looks forward and steeply DOWN along her own body. She is lying feet-first on a fully transparent clear acrylic half-pipe water slide that drops away in front of her at a steep angle, like the first plunge of a giant water slide. You can see straight through the clear slide floor to empty air and the land far below.

Exactly two separate bare legs run from the bottom edge of the frame toward the centre, with a clear gap of transparent slide between them. Two bare feet at the end, toes pointing up, light tan wet shining skin. Only the bottom edge of a black high-cut one-piece swimsuit is visible at the hips. The feet and ankles are completely bare: nothing on them, no straps, no shoes, no bindings.

Exactly two thin electric cyan glowing strips are built into the two upper rims of the slide; they run away from the camera and converge at a single vanishing point far below. A thin sheet of water runs down the slide around her hips.

Far below and ahead, filling the upper half of the frame: Mount Fuji's perfect volcanic cone with a white tip, at sunrise, golden sky, the sun low beside the mountain. A lake shines gold at its foot. On the wooded hillside in the middle distance stands the five-storey red Chureito pagoda surrounded by pink cherry blossom. Pink petals fly through the air and a few sit on the lens. A thick white cloud bank lies across the lower slopes far below, and the slide dives down toward it.

No hands, no arms, no face, no other people, no text, no watermark, no logo. No glowing line anywhere except the two slide rims."""


def main() -> int:
    etiket = sys.argv[1] if len(sys.argv) > 1 else "1"
    from core import kie_api

    url = kie_api.generate_image(PROMPT, model="nano-banana-2", aspect_ratio="9:16")
    if not url:
        print("gorsel uretilemedi")
        return 1
    hedef = HERE / ("ilk_kare_%s.png" % etiket)
    hedef.write_bytes(requests.get(url, timeout=120).content)
    print("URL   :", url)
    print("dosya :", hedef)
    return 0


if __name__ == "__main__":
    import os
    os.environ.setdefault("KIE_AI_API_KEY", kie_uret.api_key())
    raise SystemExit(main())
