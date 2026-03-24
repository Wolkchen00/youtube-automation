"""
Windows Task Scheduler Setup — Daily 9 AM Automation

Creates a Windows scheduled task that runs all 4 YouTube channels
every morning at 9:00 AM.

Usage:
    python setup_scheduler.py --install    # Create the scheduled task
    python setup_scheduler.py --remove     # Remove the scheduled task
    python setup_scheduler.py --test       # Run immediately (test)
    python setup_scheduler.py --status     # Check task status
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
TASK_NAME = "YouTubeAutomation_DailyRunner"
PYTHON_PATH = sys.executable
SCRIPT_PATH = PROJECT_ROOT / "daily_runner.py"
LOG_PATH = PROJECT_ROOT / "logs" / "scheduler.log"


def install_task(hour: int = 9, minute: int = 0):
    """Create a Windows scheduled task for daily execution."""
    print(f"\n{'='*60}")
    print(f"📅 Installing daily task: {TASK_NAME}")
    print(f"   Time: {hour:02d}:{minute:02d} AM every day")
    print(f"   Script: {SCRIPT_PATH}")
    print(f"   Python: {PYTHON_PATH}")
    print(f"{'='*60}")

    # Build the scheduled task command
    # -X utf8 fixes Windows emoji/unicode encoding issues
    action_cmd = f'"{PYTHON_PATH}" -X utf8 "{SCRIPT_PATH}"'

    cmd = [
        "schtasks", "/Create",
        "/TN", TASK_NAME,
        "/TR", action_cmd,
        "/SC", "DAILY",
        "/ST", f"{hour:02d}:{minute:02d}",
        "/F",  # Force overwrite if exists
        "/RL", "HIGHEST",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"\n✅ Scheduled task created successfully!")
            print(f"   Task: {TASK_NAME}")
            print(f"   Schedule: Daily at {hour:02d}:{minute:02d}")
            print(f"\n   To check: schtasks /Query /TN {TASK_NAME}")
            print(f"   To run now: schtasks /Run /TN {TASK_NAME}")
            print(f"   To remove: python setup_scheduler.py --remove")
        else:
            print(f"\n❌ Failed to create task!")
            print(f"   Error: {result.stderr}")
            print(f"\n   TIP: Run as Administrator if permission denied.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"   TIP: Run PowerShell as Administrator.")


def remove_task():
    """Remove the scheduled task."""
    cmd = ["schtasks", "/Delete", "/TN", TASK_NAME, "/F"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Task '{TASK_NAME}' removed.")
        else:
            print(f"❌ Could not remove task: {result.stderr}")
    except Exception as e:
        print(f"❌ Error: {e}")


def check_status():
    """Check the scheduled task status."""
    cmd = ["schtasks", "/Query", "/TN", TASK_NAME, "/V", "/FO", "LIST"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"\n📅 Task Status for: {TASK_NAME}")
            print(result.stdout)
        else:
            print(f"❌ Task not found. Run: python setup_scheduler.py --install")
    except Exception as e:
        print(f"❌ Error: {e}")


def run_test():
    """Run the pipeline immediately for testing."""
    print(f"\n🚀 Running test (all channels, skip upload)...")
    cmd = [PYTHON_PATH, "-X", "utf8", str(SCRIPT_PATH), "--skip-upload"]
    subprocess.run(cmd, cwd=str(PROJECT_ROOT))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube Automation Scheduler")
    parser.add_argument("--install", action="store_true", help="Install daily 9 AM task")
    parser.add_argument("--remove", action="store_true", help="Remove scheduled task")
    parser.add_argument("--status", action="store_true", help="Check task status")
    parser.add_argument("--test", action="store_true", help="Run immediately (test)")
    parser.add_argument("--hour", type=int, default=9, help="Hour to run (24h format, default: 9)")
    parser.add_argument("--minute", type=int, default=0, help="Minute to run (default: 0)")
    args = parser.parse_args()

    if args.install:
        install_task(hour=args.hour, minute=args.minute)
    elif args.remove:
        remove_task()
    elif args.status:
        check_status()
    elif args.test:
        run_test()
    else:
        print("Usage:")
        print("  python setup_scheduler.py --install          # Daily 9 AM")
        print("  python setup_scheduler.py --install --hour 8 # Daily 8 AM")
        print("  python setup_scheduler.py --remove           # Remove task")
        print("  python setup_scheduler.py --status           # Check status")
        print("  python setup_scheduler.py --test             # Run now (test)")
