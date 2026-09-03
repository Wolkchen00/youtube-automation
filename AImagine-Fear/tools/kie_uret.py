"""out/<slug>/PROMPT.txt dosyasini Kie AI'ya gonderir, bekler, videoyu indirir.

Kullanim:
    python tools/kie_uret.py vegas-strat-blue-rain-25 --model sora-2-pro-storyboard --n-frames 25

UYARI: Kie cuzdani dort canli kanalla ORTAK. Buradan harcanan kredi onlardan gider.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://api.kie.ai/api/v1"
# Yerelde Shorts_Dizi'nin .env'i, CI'da depo kokundeki .env (workflow yaziyor).
FALLBACK_ENVS = [
    ROOT.parent / ".env",
    Path.home() / "Desktop/Antigravity/Projeler/Shorts_Dizi_Fabrikasi/.env",
]
# CI secret adi KIE_AI_API_KEY, yerel .env'de KIE_API_KEY. Ikisini de kabul et.
ANAHTAR_ADLARI = ("KIE_API_KEY", "KIE_AI_API_KEY")
TERMINAL_OK = {"success", "succeeded", "completed"}
TERMINAL_BAD = {"fail", "failed", "error"}


def api_key() -> str:
    import os

    for ad in ANAHTAR_ADLARI:
        key = os.environ.get(ad, "").strip()
        if key:
            return key
    for env in FALLBACK_ENVS:
        if not env.exists():
            continue
        text = env.read_text(encoding="utf-8", errors="ignore")
        for ad in ANAHTAR_ADLARI:
            match = re.search(r"^%s=(.+)$" % ad, text, re.M)
            if match and match.group(1).strip():
                return match.group(1).strip()
    sys.exit("Kie anahtari bulunamadi. Aranan: %s (ortam degiskeni ya da %s)"
             % (", ".join(ANAHTAR_ADLARI), ", ".join(str(e) for e in FALLBACK_ENVS)))


def credits(headers: dict) -> float | None:
    response = requests.get(BASE + "/chat/credit", headers=headers, timeout=30)
    if response.status_code != 200:
        return None
    return (response.json() or {}).get("data")


def create_task(headers: dict, payload: dict) -> str:
    response = requests.post(BASE + "/jobs/createTask", headers=headers, json=payload, timeout=90)
    body = response.text[:1200]
    if response.status_code >= 400:
        sys.exit("createTask HTTP %s\n%s" % (response.status_code, body))
    data = response.json()
    if str(data.get("code")) not in ("200", "0"):
        sys.exit("createTask reddetti: %s" % body)
    task_id = (data.get("data") or {}).get("taskId")
    if not task_id:
        sys.exit("taskId yok: %s" % body)
    return task_id


def poll(headers: dict, task_id: str, max_wait: int) -> dict:
    started = time.time()
    last_state = ""
    while time.time() - started < max_wait:
        response = requests.get(
            BASE + "/jobs/recordInfo", headers=headers, params={"taskId": task_id}, timeout=60
        )
        if response.status_code >= 500:
            print("  upstream %s, tekrar deneniyor" % response.status_code, flush=True)
            time.sleep(10)
            continue
        data = (response.json() or {}).get("data") or {}
        state = str(data.get("state") or data.get("status") or "").lower()
        if state != last_state:
            print("  [%4ds] durum: %s" % (int(time.time() - started), state or "bilinmiyor"), flush=True)
            last_state = state
        if state in TERMINAL_OK:
            return data
        if state in TERMINAL_BAD:
            sys.exit("Uretim basarisiz: %s" % json.dumps(data, ensure_ascii=False)[:1200])
        time.sleep(10)
    sys.exit("Zaman asimi: %ds icinde bitmedi. taskId=%s" % (max_wait, task_id))


def result_urls(data: dict) -> list[str]:
    raw = data.get("resultJson") or data.get("result") or {}
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            raw = {}
    urls = raw.get("resultUrls") or data.get("resultUrls") or []
    if isinstance(urls, str):
        urls = [urls]
    return [u for u in urls if isinstance(u, str) and u.startswith("http")]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("slug")
    parser.add_argument("--model", default="sora-2-pro-storyboard")
    parser.add_argument("--n-frames", default="25", help="sure, saniye")
    parser.add_argument("--aspect", default="portrait")
    parser.add_argument("--resolution", default="720p", help="480p, 720p, 1080p")
    parser.add_argument("--prompt-file", help="PROMPT.txt yerine bu dosyayi kullan")
    parser.add_argument("--tag", default="", help="cikti dosya adina eklenecek etiket")
    parser.add_argument("--max-wait", type=int, default=1500)
    parser.add_argument("--dry", action="store_true", help="istek govdesini yaz, gonderme")
    args = parser.parse_args()

    if args.prompt_file:
        prompt_path = Path(args.prompt_file)
        if not prompt_path.is_absolute():
            prompt_path = ROOT / prompt_path
    else:
        prompt_path = ROOT / "out" / args.slug / "PROMPT.txt"
    if not prompt_path.exists():
        sys.exit("Prompt bulunamadi: %s" % prompt_path)
    prompt = prompt_path.read_text(encoding="utf-8").strip()

    # Her modelin input govdesi farkli. Kaynak: _skills/kie-ai-video-production/models/
    model = args.model
    if model.startswith("bytedance/seedance-2"):
        block = {
            "prompt": prompt,
            "duration": int(args.n_frames),
            "aspect_ratio": "9:16",
            "resolution": args.resolution,
            "generate_audio": True,
        }
        # 2500 DEGIL. Yerel _skills/kie-ai-video-production/models/seedance-2.0.md
        # dosyasindaki "max 2500 karakter" satiri YANLIS ve bu projeyi yanlis
        # yonlendirdi: kanon gereksiz yere kirpildi ve orta ucte bir bozuldu.
        # docs.kie.ai ve playground textarea maxLength=20000 diyor.
        limit = 20000
    elif model.startswith("kling"):
        block = {
            "prompt": prompt,
            "duration": str(args.n_frames),
            "aspect_ratio": "9:16",
            "mode": "pro",
            "multi_shots": False,
            "sound": True,
        }
        limit = None
    else:
        block = {
            "prompt": prompt,
            "n_frames": str(args.n_frames),
            "aspect_ratio": args.aspect,
        }
        limit = None

    payload = {"model": model, "input": block}
    print("model      : %s" % model)
    print("slug       : %s" % args.slug)
    print("prompt     : %s" % prompt_path.name)
    print("sure       : %s sn" % args.n_frames)
    print("uzunluk    : %d kelime, %d karakter%s"
          % (len(prompt.split()), len(prompt),
             (" (sinir %d)" % limit) if limit else ""))
    if limit and len(prompt) > limit:
        sys.exit("Prompt %d karakter, model sinirı %d. Kisalt." % (len(prompt), limit))

    if args.dry:
        print(json.dumps(payload, ensure_ascii=False)[:800])
        return 0

    headers = {"Authorization": "Bearer " + api_key(), "Content-Type": "application/json"}
    before = credits(headers)
    print("kredi once : %s" % before)

    task_id = create_task(headers, payload)
    print("taskId     : %s" % task_id)
    print("bekleniyor (10sn araliklarla, en fazla %ds)" % args.max_wait, flush=True)

    data = poll(headers, task_id, args.max_wait)
    urls = result_urls(data)
    if not urls:
        sys.exit("Sonuc URL yok: %s" % json.dumps(data, ensure_ascii=False)[:1200])

    out_dir = ROOT / "out" / args.slug / "video"
    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = ("_" + args.tag) if args.tag else ""
    saved = []
    for index, url in enumerate(urls, start=1):
        target = out_dir / ("%s%s_%02d.mp4" % (args.slug, suffix, index))
        with requests.get(url, stream=True, timeout=600) as response:
            response.raise_for_status()
            with target.open("wb") as handle:
                for chunk in response.iter_content(1 << 20):
                    handle.write(chunk)
        saved.append(target)
        print("indirildi  : %s (%.1f MB)" % (target, target.stat().st_size / 1e6))

    after = credits(headers)
    print("kredi sonra: %s" % after)
    if before is not None and after is not None:
        print("harcanan   : %.1f kredi" % (before - after))
    print("taskId     : %s" % task_id)
    return 0 if saved else 1


if __name__ == "__main__":
    raise SystemExit(main())
