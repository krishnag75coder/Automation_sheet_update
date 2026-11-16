@echo off
title Production Task Entry Automation
color 0A

echo ========================================================
echo   Starting Production Task Entry Automation Web App...
echo ========================================================
echo.

python -c "import flask" 2>nul
if %errorlevel% neq 0 (
    echo Flask is not installed. Installing flask...
    pip install flask
)

echo Starting server and launching browser...
python app.py

pause
