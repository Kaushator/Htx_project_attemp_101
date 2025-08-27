@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0.."
git rev-parse --is-inside-work-tree >NUL 2>&1
if errorlevel 1 (
  echo Not a git repository in %cd%
  pause
  exit /b 1
)
git add -A
for /f "tokens=*" %%i in ('git status --porcelain') do ( set changes=1 )
if not defined changes (
  echo No changes to commit.
) else (
  set msg=Auto: %date% %time%
  if not "%~1"=="" set msg=%~1
  git commit -m "!msg!"
)
git push
if errorlevel 1 (
  echo Push failed.
  pause
  exit /b 1
)
echo Push up done!
REM Log to journal (relative to repo root)
python "%~dp0..\journal_roadmap\logger.py" --log "git push" --result "success"
pause