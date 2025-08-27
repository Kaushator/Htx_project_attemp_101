@echo off
setlocal
cd /d "%~dp0.."
if not exist .venv (
  py -3 -m venv .venv
)
call .venv\Scripts\activate
python -m pip install --upgrade pip
if exist requirements.txt (
  pip install -r requirements.txt
)
echo Environment ready.
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8004
.venv\Scripts\python.exe -m pytest
pause