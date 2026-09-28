@echo off
REM Windows startup script for p1-client-intake
REM Double-click this file to set up and launch the Streamlit app.
setlocal enabledelayedexpansion

echo ============================================
echo  Client Intake & Scoping - Quick Start
echo ============================================

REM Determine project root (directory where this script lives)
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

REM Create virtual environment if missing
if not exist "venv\" (
    echo [1/4] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create venv. Check Python installation.
        pause
        exit /b 1
    )
)

REM Activate and install deps
echo [2/4] Installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: pip install failed.
    pause
    exit /b 1
)

REM Start Streamlit
echo [3/4] Starting Streamlit dashboard...
echo.
echo Dashboard will open at http://localhost:8501
echo Press Ctrl+C to stop.
echo.
start "" http://localhost:8501

streamlit run app.py
pause
