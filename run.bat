@echo off
REM One-command launcher for Windows
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo Python not found. Install from python.org first.
  pause
  exit /b 1
)

echo Installing dependencies (first run only)...
python -m pip install -q -r requirements.txt

echo Launching Job Search Agent...
echo Open the URL shown below in your browser.
echo.
python -m streamlit run app.py
pause
