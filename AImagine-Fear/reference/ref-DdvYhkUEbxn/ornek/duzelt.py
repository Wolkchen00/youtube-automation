"""ilk_kare_2'deki gogus kamerasini sil (nano-banana-2 duzenleme)."""
import os, sys
from pathlib import Path
import requests
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3])); sys.path.insert(0, str(HERE.parents[2] / "tools"))
import kie_uret
os.environ.setdefault("KIE_AI_API_KEY", kie_uret.api_key())
from core import kie_api
KAYNAK = sys.argv[1]
PROMPT = ("Edit this photo. Remove the black action camera at the bottom centre of the frame completely. "
          "In its place show only the black high-cut one-piece swimsuit at the hips and the clear transparent slide. "
          "Keep everything else exactly identical: the two bare legs, the feet, the slide, the cyan rims, "
          "Mount Fuji, the pagoda, the cherry blossom, the clouds, the light, the framing.")
url = kie_api.generate_image(PROMPT, reference_url=KAYNAK, model="nano-banana-2", aspect_ratio="9:16")
print("URL   :", url)
(HERE / "ilk_kare_2b.png").write_bytes(requests.get(url, timeout=120).content)
