@echo off
REM PropellerAds API Encyclopedia - Windows Launcher
title PropellerAds API Encyclopedia

echo 🚀 PropellerAds API Encyclopedia Launcher
echo ==================================================

REM Change to script directory
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

REM Run the Python launcher
python launch_app.py

pause
