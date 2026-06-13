@echo off
cd /d "%~dp0"
echo  Starting VoiceScribe...
IF NOT EXIST venv\Scripts\activate.bat (
    echo  [ERROR] Virtual environment not found. Run setup.bat first.
    pause
    exit /b 1
)
call venv\Scripts\activate.bat
python app.py
pause
