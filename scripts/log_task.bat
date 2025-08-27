@echo off
setlocal
REM Usage: log_task.bat "Your prompt" "Your result"
python "%~dp0..\journal_roadmap\logger.py" --log %~1 --result %~2