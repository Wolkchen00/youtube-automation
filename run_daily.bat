@echo off
echo ============================================
echo YouTube Daily Automation - Starting...
echo ============================================
cd /d "c:\Users\ihsan\Desktop\Antigravity\Projects\Youtube"
python -X utf8 daily_runner.py >> logs\scheduler_output.log 2>&1
echo Done at %date% %time%
