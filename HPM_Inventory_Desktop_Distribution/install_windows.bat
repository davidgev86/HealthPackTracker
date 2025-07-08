@echo off
echo Installing HPM Inventory Tracker...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or later from https://python.org
    pause
    exit /b 1
)

REM Install dependencies
echo Installing required packages...
python -m pip install -r requirements_desktop.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Installation complete!
echo.
echo To run the application:
echo   python run_desktop.py
echo.
echo To build a standalone executable:
echo   python build_desktop.py
echo.
pause
