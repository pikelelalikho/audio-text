@echo off
echo.
echo  ============================================
echo   VoiceScribe — Setup
echo  ============================================
echo.

REM Check Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo  [ERROR] Python not found.
    echo  Download from https://www.python.org/downloads/
    echo  Make sure to tick "Add Python to PATH" during install.
    pause
    exit /b 1
)

echo  [1/4] Creating virtual environment...
python -m venv venv
IF %ERRORLEVEL% NEQ 0 ( echo [ERROR] Failed to create venv & pause & exit /b 1 )

echo  [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo  [3/4] Installing dependencies (this may take a few minutes)...
pip install --upgrade pip -q
pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 ( echo [ERROR] Install failed & pause & exit /b 1 )

echo  [4/4] Done!
echo.
echo  ============================================
echo   Setup complete. Run  start.bat  to launch.
echo  ============================================
echo.
pause
