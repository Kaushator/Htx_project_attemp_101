@echo off
setlocal enabledelayedexpansion
cd /d "E:\Htx_project_attemp_101"
git rev-parse --is-inside-work-tree >NUL 2>&1
if errorlevel 1 (
  echo Not a git repository: E:\Htx_project_attemp_101
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
python "/mnt/data/cursor_starter_pack/journal_roadmap\\logger.py" --log "git push" --result "success"
pause