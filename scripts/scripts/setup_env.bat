@echo off
setlocal
cd /d "E:\Htx_project_attemp_101"
if not exist .venv (
  py -3 -m venv .venv
)
call .venv\Scripts\activate
python -m pip install --upgrade pip
if exist requirements.txt (
  pip install -r requirements.txt
)
echo Environment ready.
pause