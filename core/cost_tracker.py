"""
Cost Tracking — Kie AI Credit & Dollar Cost Calculator

Based on real Kie AI pricing: $0.005 per credit.

CONFIRMED PRICING (March 2026):
─────────────────────────────────────────────────────────
IMAGE MODELS:
  Nano Banana 2 (1K)        8 credits   = $0.04/image
  Nano Banana 2 (2K)       12 credits   = $0.06/image
  Nano Banana 2 (4K)       18 credits   = $0.09/image
  GPT Image 1.5            ~20 credits  = $0.10/image   ← expensive
  Seedream 5.0 Lite        5.5 credits  = $0.028/image  ← cheapest

VIDEO MODELS:
  Kling 3.0 std (8s)       ~48 credits  = $0.24/clip
  Kling 3.0 pro (8s)       ~150 credits = $0.75/clip    ← 3x more!
  Veo 3.1 fast (8s)         60 credits  = $0.30/clip
  Veo 3.1 quality (8s)     250 credits  = $1.25/clip    ← premium
  Seedance 2.0             ~40 credits  = $0.20/clip

FREE:
  Gemini 2.0 Flash          0           = $0.00 (free tier)
  ImgBB                     0           = $0.00 (free)
─────────────────────────────────────────────────────────
"""

import json
from datetime import date
from pathlib import Path

from .config import PROJECT_ROOT, logger

COST_LOG = PROJECT_ROOT / "logs" / "cost_tracking.json"

DOLLAR_PER_CREDIT = 0.005  # $0.005 per Kie AI credit

# ─── Per-Operation Credit Costs (confirmed) ────────────────────────────────────

CREDIT_COSTS = {
    # Image models
    "nano-banana-2_1k": 8,
    "nano-banana-2_2k": 12,
    "nano-banana-2_4k": 18,
    "gpt-image-1.5": 20,
    "seedream-5.0-lite": 5.5,

    # Video models (8 second clips)
    "kling-3.0_std_8s": 48,
    "kling-3.0_pro_8s": 150,
    "veo3_fast_8s": 60,
    "veo3_quality_8s": 250,
    "seedance-2.0_8s": 40,

    # Free
    "gemini_flash": 0,
    "imgbb": 0,
}


# ─── Per-Channel Cost Breakdown ────────────────────────────────────────────────

CHANNEL_COSTS = {
    "shadowedhistory": {
        "images": {"model": "Nano Banana 2 (1K)", "count": 4, "credits_each": 8},
        "videos": {"model": "Kling 3.0 std (8s)", "count": 3, "credits_each": 48},
        "scripts": {"model": "Gemini Flash", "count": 2, "credits_each": 0},
    },
    "sentinal_ihsan": {
        "images": {"model": "Nano Banana 2 (1K)", "count": 4, "credits_each": 8},
        "videos": {"model": "Kling 3.0 std (8s)", "count": 3, "credits_each": 48},
        "scripts": {"model": "Gemini Flash", "count": 2, "credits_each": 0},
    },
    "galactic_experiment": {
        "images": {"model": "Nano Banana 2 (1K)", "count": 4, "credits_each": 8},
        "videos": {"model": "Kling 3.0 std (8s)", "count": 3, "credits_each": 48},
        "scripts": {"model": "Gemini Flash", "count": 2, "credits_each": 0},
    },
    "aimagine": {
        "images": {"model": "Nano Banana 2 (1K)", "count": 4, "credits_each": 8},
        "videos": {"model": "Kling 3.0 std (8s)", "count": 3, "credits_each": 48},
        "scripts": {"model": "Gemini Flash", "count": 1, "credits_each": 0},
    },
}


def estimate_channel_cost(channel: str) -> dict:
    """Calculate the dollar cost for one channel per day."""
    ch = CHANNEL_COSTS.get(channel, CHANNEL_COSTS["shadowedhistory"])

    img_credits = ch["images"]["count"] * ch["images"]["credits_each"]
    vid_credits = ch["videos"]["count"] * ch["videos"]["credits_each"]
    script_credits = ch["scripts"]["count"] * ch["scripts"]["credits_each"]
    total_credits = img_credits + vid_credits + script_credits
    total_dollars = total_credits * DOLLAR_PER_CREDIT

    return {
        "images": {
            "model": ch["images"]["model"],
            "count": ch["images"]["count"],
            "credits": img_credits,
            "dollars": round(img_credits * DOLLAR_PER_CREDIT, 2),
        },
        "videos": {
            "model": ch["videos"]["model"],
            "count": ch["videos"]["count"],
            "credits": vid_credits,
            "dollars": round(vid_credits * DOLLAR_PER_CREDIT, 2),
        },
        "total_credits": total_credits,
        "total_dollars": round(total_dollars, 2),
    }


def estimate_daily_total() -> dict:
    """Full daily cost estimate across all 4 channels in dollars."""
    channels = {}
    total_credits = 0
    total_dollars = 0.0

    for ch_name in ["shadowedhistory", "sentinal_ihsan", "galactic_experiment", "aimagine"]:
        cost = estimate_channel_cost(ch_name)
        channels[ch_name] = cost
        total_credits += cost["total_credits"]
        total_dollars += cost["total_dollars"]

    monthly_dollars = round(total_dollars * 30, 2)

    return {
        "channels": channels,
        "daily_credits": total_credits,
        "daily_dollars": round(total_dollars, 2),
        "monthly_credits": total_credits * 30,
        "monthly_dollars": monthly_dollars,
    }


def log_cost(channel: str, operation: str, model: str, credits_used: float):
    """Log a credit expenditure."""
    entry = {
        "date": date.today().isoformat(),
        "channel": channel,
        "operation": operation,
        "model": model,
        "credits": credits_used,
        "dollars": round(credits_used * DOLLAR_PER_CREDIT, 3),
    }

    history = []
    if COST_LOG.exists():
        try:
            history = json.loads(COST_LOG.read_text(encoding="utf-8"))
        except Exception:
            history = []

    history.append(entry)
    COST_LOG.parent.mkdir(parents=True, exist_ok=True)
    COST_LOG.write_text(json.dumps(history[-1000:], ensure_ascii=False, indent=2), encoding="utf-8")


def print_cost_report():
    """Print detailed cost report in dollars."""
    report = estimate_daily_total()

    logger.info("\n" + "=" * 65)
    logger.info("💰 GÜNLÜK MALİYET RAPORU (USD)")
    logger.info("=" * 65)

    for ch_name, cost in report["channels"].items():
        logger.info(f"\n  📺 {ch_name.upper()}")
        img = cost["images"]
        vid = cost["videos"]
        logger.info(f"     🖼️ Görseller: {img['count']}x {img['model']} = {img['credits']} cr = ${img['dollars']:.2f}")
        logger.info(f"     🎬 Videolar:  {vid['count']}x {vid['model']} = {vid['credits']} cr = ${vid['dollars']:.2f}")
        logger.info(f"     📝 Script:    Gemini Flash = FREE")
        logger.info(f"     💵 TOPLAM:    {cost['total_credits']} kredi = ${cost['total_dollars']:.2f}")

    logger.info(f"\n{'─'*65}")
    logger.info(f"  📊 GÜNLÜK TOPLAM:  {report['daily_credits']} kredi = ${report['daily_dollars']:.2f}")
    logger.info(f"  📊 AYLIK TOPLAM:   {report['monthly_credits']} kredi = ${report['monthly_dollars']:.2f}")
    logger.info("=" * 65)

    logger.info("\n💡 MALİYET OPTİMİZASYONU:")
    logger.info("  ✅ Nano Banana 2 (8cr/$0.04) — GPT Image 1.5 (20cr/$0.10) yerine")
    logger.info("  ✅ Kling 3.0 std (48cr/$0.24) — pro (150cr/$0.75) yerine")
    logger.info("  ✅ Gemini Flash = ÜCRETSİZ")
    logger.info("  ✅ ImgBB = ÜCRETSİZ")

    return report
