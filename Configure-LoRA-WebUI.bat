@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run Start-LoRA-WebUI.bat once before configuring folders.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" lora_frame_picker_web.py --configure
if errorlevel 1 pause
