@echo off
setlocal
REM Usage: log_task.bat "Your prompt" "Your result"
python "/mnt/data/cursor_starter_pack/journal_roadmap\\logger.py" --log %~1 --result %~2