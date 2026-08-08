@echo off
setlocal
cd /d "%~dp0"

set "LORA_BOOTSTRAP_PYTHON="
where py >nul 2>nul && set "LORA_BOOTSTRAP_PYTHON=py -3"
if not defined LORA_BOOTSTRAP_PYTHON (
  where python >nul 2>nul && set "LORA_BOOTSTRAP_PYTHON=python"
)
if not defined LORA_BOOTSTRAP_PYTHON goto no_python

if not exist ".venv\Scripts\python.exe" (
  %LORA_BOOTSTRAP_PYTHON% -c "import sys;raise SystemExit(0 if sys.version_info>=(3,9) else 1)"
  if errorlevel 1 goto old_python
  echo First run: creating an isolated Python environment...
  %LORA_BOOTSTRAP_PYTHON% -m venv .venv
  if errorlevel 1 goto venv_failed
)

".venv\Scripts\python.exe" -c "import flask" >nul 2>nul
if errorlevel 1 (
  echo Installing WebUI components...
  ".venv\Scripts\python.exe" -m pip install --upgrade pip
  if errorlevel 1 goto install_failed
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
  if errorlevel 1 goto install_failed
)

".venv\Scripts\python.exe" lora_frame_picker_web.py
if errorlevel 1 goto app_failed
exit /b 0

:no_python
echo Python 3 was not found. Install Python 3.9 or newer from:
echo https://www.python.org/downloads/windows/
echo During setup, select "Add python.exe to PATH".
goto pause_error
:old_python
echo Python 3.9 or newer is required.
goto pause_error
:venv_failed
echo Could not create .venv. Check that this folder is writable.
goto pause_error
:install_failed
echo Dependency installation failed. Check your network or proxy settings.
goto pause_error
:app_failed
echo The WebUI exited with an error. Copy the full message above into a GitHub Issue.
:pause_error
pause
exit /b 1
