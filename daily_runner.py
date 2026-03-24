"""
YouTube Multi-Channel Automation — Master Daily Runner

Runs all 4 channel pipelines with automatic retry for failed channels.
If a channel fails (e.g. Kie AI 500 error), it retries every hour
until all channels succeed or max retries reached.

Designed to be fully autonomous — run via Windows Task Scheduler at 9 AM daily.

Usage:
    python daily_runner.py                           # Run ALL channels (with auto-retry)
    python daily_runner.py --channel shadowedhistory  # Run one channel
    python daily_runner.py --no-retry                 # Run once, no retry
    python daily_runner.py --skip-upload              # Generate but don't publish
    python daily_runner.py --cost-only                # Show cost estimate only
"""

import argparse
import json
import time
from datetime import date, datetime
from pathlib import Path

from core.config import PROJECT_ROOT, CHANNEL_NAMES, logger, validate_api_keys
from core.kie_api import check_credit
from core.cost_tracker import print_cost_report, estimate_daily_total


REPORTS_FILE = PROJECT_ROOT / "logs" / "daily_reports.json"
RETRY_INTERVAL = 1800  # 30 minutes between retries (fits GitHub Actions 5h limit)
MAX_RETRIES = 4         # Max 4 retries (total ~2.5h retry window)


def run_channel(channel_name: str, dry_run: bool = False, skip_upload: bool = False) -> dict | None:
    """Run a single channel pipeline with error isolation."""
    try:
        if channel_name == "shadowedhistory":
            from shadowedhistory.pipeline import run_pipeline
        elif channel_name == "sentinal_ihsan":
            from sentinal_ihsan.pipeline import run_pipeline
        elif channel_name == "galactic_experiment":
            from galactic_experiment.pipeline import run_pipeline
        elif channel_name == "aimagine":
            from aimagine.pipeline import run_pipeline
        else:
            logger.error(f"Unknown channel: {channel_name}")
            return None

        return run_pipeline(dry_run=dry_run, skip_upload=skip_upload)

    except Exception as e:
        logger.error(f"{channel_name} PIPELINE ERROR: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def run_all(dry_run: bool = False, skip_upload: bool = False,
            channels: list = None, auto_retry: bool = True):
    """Run all channel pipelines with automatic retry for failures."""
    today = date.today().isoformat()
    start_time = time.time()
    target_channels = channels or CHANNEL_NAMES

    logger.info("\n" + "=" * 60)
    logger.info(f"YOUTUBE DAILY AUTOMATION - {today}")
    logger.info(f"Channels: {', '.join(target_channels)}")
    logger.info(f"Auto-retry: {'ON (every {RETRY_INTERVAL//60}min, max {MAX_RETRIES}x)' if auto_retry else 'OFF'}")
    logger.info("=" * 60)

    # Pre-flight checks
    validate_api_keys()

    credit = check_credit()
    if credit:
        logger.info(f"Credits: {credit} (${float(credit) * 0.005:.2f})")

    cost_report = estimate_daily_total()
    logger.info(f"Estimated daily cost: ~{cost_report['daily_credits']} credits (${cost_report['daily_dollars']:.2f})")

    if dry_run:
        logger.info("DRY RUN MODE - No API calls will be made.")

    # === MAIN LOOP WITH AUTO-RETRY ===
    reports = {}
    failed_channels = list(target_channels)
    attempt = 0

    while failed_channels and attempt <= MAX_RETRIES:
        if attempt > 0:
            logger.info(f"\n{'='*60}")
            logger.info(f"RETRY ATTEMPT {attempt}/{MAX_RETRIES} - {datetime.now().strftime('%H:%M')}")
            logger.info(f"Retrying {len(failed_channels)} failed channels: {', '.join(failed_channels)}")
            logger.info(f"{'='*60}")

        newly_failed = []

        for channel in failed_channels:
            logger.info(f"\n--- STARTING: {channel.upper()} (attempt {attempt + 1}) ---")

            report = run_channel(channel, dry_run=dry_run, skip_upload=skip_upload)
            reports[channel] = report

            if report:
                logger.info(f"OK {channel} completed successfully!")
            else:
                logger.error(f"FAIL {channel} failed!")
                newly_failed.append(channel)

        failed_channels = newly_failed
        attempt += 1

        # If there are still failures and retry is enabled, wait before next attempt
        if failed_channels and auto_retry and attempt <= MAX_RETRIES:
            wait_min = RETRY_INTERVAL // 60
            logger.info(f"\n{len(failed_channels)} channels failed. Waiting {wait_min} minutes before retry...")
            logger.info(f"Failed: {', '.join(failed_channels)}")
            logger.info(f"Next retry at: {datetime.now().strftime('%H:%M')} + {wait_min}min")
            time.sleep(RETRY_INTERVAL)
        elif failed_channels and not auto_retry:
            break

    # === SUMMARY ===
    elapsed = time.time() - start_time
    success = sum(1 for r in reports.values() if r)
    total = len(target_channels)

    logger.info("\n" + "=" * 60)
    logger.info(f"DAILY SUMMARY - {today}")
    logger.info("=" * 60)
    logger.info(f"  Success:  {success}/{total} channels")
    logger.info(f"  Duration: {elapsed/60:.1f} minutes")
    logger.info(f"  Retries:  {max(0, attempt - 1)}")

    for ch in target_channels:
        report = reports.get(ch)
        status = "OK" if report else "FAIL"
        title = report.get("title", "N/A") if report else "FAILED"
        logger.info(f"  [{status}] {ch}: {title[:50]}")

    remaining = check_credit()
    if remaining:
        logger.info(f"\nRemaining credits: {remaining} (${float(remaining) * 0.005:.2f})")

    # Save report
    daily_report = {
        "date": today,
        "channels": {ch: (reports.get(ch) or {"error": True}) for ch in target_channels},
        "success_count": success,
        "total_count": total,
        "retries": max(0, attempt - 1),
        "duration_min": round(elapsed / 60, 1),
    }

    try:
        history = []
        if REPORTS_FILE.exists():
            history = json.loads(REPORTS_FILE.read_text(encoding="utf-8"))
        history.append(daily_report)
        REPORTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        REPORTS_FILE.write_text(
            json.dumps(history[-90:], ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    except Exception as e:
        logger.warning(f"Could not save report: {e}")

    logger.info(f"\nDAILY AUTOMATION COMPLETE!")
    return daily_report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube Multi-Channel Daily Automation")
    parser.add_argument("--channel", type=str, help="Run specific channel only")
    parser.add_argument("--no-retry", action="store_true", help="Disable auto-retry on failure")
    parser.add_argument("--skip-upload", action="store_true", help="Generate but don't publish")
    parser.add_argument("--cost-only", action="store_true", help="Show cost estimate and exit")
    args = parser.parse_args()

    if args.cost_only:
        print_cost_report()
    elif args.channel:
        if args.channel not in CHANNEL_NAMES:
            print(f"Unknown channel: {args.channel}")
            print(f"Available: {', '.join(CHANNEL_NAMES)}")
        else:
            run_all(
                skip_upload=args.skip_upload,
                channels=[args.channel],
                auto_retry=not args.no_retry,
            )
    else:
        run_all(skip_upload=args.skip_upload, auto_retry=not args.no_retry)
