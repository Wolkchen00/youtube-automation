"""Bir videonun son karesini cikarir, Kie gecici deposuna yukler, URL'yi basar.

Zincir icin: B30_2 uretimi bu URL'yi --first-frame-url olarak alir.
Seedance son kareyi tek basina kabul etmez ama ILK kare olarak alir.
Kullanim: python son_kare_yukle.py <video.mp4>
"""
import subprocess
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
import kie_uret  # noqa: E402

YUKLEME = "https://kieai.redpandaai.co/api/file-stream-upload"


def main() -> int:
    video = Path(sys.argv[1]).resolve()
    kare = video.with_name(video.stem + "_sonkare.png")
    # -sseof ile sondan 0,1 sn geri git, kalan karelerin sonuncusunu yaz (-update 1).
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.1", "-i", str(video),
                    "-update", "1", "-frames:v", "1", str(kare)], check=True)
    print("son kare  :", kare, "%.0f KB" % (kare.stat().st_size / 1024))
    with kare.open("rb") as f:
        r = requests.post(
            YUKLEME,
            headers={"Authorization": "Bearer " + kie_uret.api_key()},
            files={"file": (kare.name, f, "image/png")},
            data={"uploadPath": "images", "fileName": kare.name},
            timeout=300,
        )
    d = r.json()
    veri = d.get("data") or d
    url = veri.get("downloadUrl") or veri.get("fileUrl") or veri.get("file_url")
    if not url:
        print("yukleme hatasi:", str(d)[:300])
        return 1
    print("URL       :", url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
