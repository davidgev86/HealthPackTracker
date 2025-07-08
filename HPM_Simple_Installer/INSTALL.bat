@echo off
echo HPM Inventory Tracker - Simple Installer
echo ==========================================
echo.
echo This will install HPM Inventory Tracker on your computer.
echo.
pause

echo Checking for Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Installing Python...
    echo Please wait, this may take a few minutes...
    
    REM Download and install Python
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe' -OutFile 'python_installer.exe'"
    python_installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
    del python_installer.exe
    
    echo Python installation complete.
) else (
    echo Python found.
)

echo.
echo Installing HPM Inventory Tracker...

REM Create installation directory
set INSTALL_DIR=%USERPROFILE%\HPM_Inventory
mkdir "%INSTALL_DIR%" 2>nul

REM Copy files
echo Copying application files...
xcopy /s /e /y * "%INSTALL_DIR%\" >nul

REM Install dependencies
echo Installing dependencies...
cd /d "%INSTALL_DIR%"
python -m pip install flask werkzeug >nul 2>&1

REM Create desktop shortcut
echo Creating desktop shortcut...
echo @echo off > "%INSTALL_DIR%\HPM_Inventory.bat"
echo cd /d "%INSTALL_DIR%" >> "%INSTALL_DIR%\HPM_Inventory.bat"
echo python desktop_app.py >> "%INSTALL_DIR%\HPM_Inventory.bat"

copy "%INSTALL_DIR%\HPM_Inventory.bat" "%USERPROFILE%\Desktop\HPM Inventory Tracker.bat" >nul 2>&1

echo.
echo ==========================================
echo Installation Complete!
echo ==========================================
echo.
echo HPM Inventory Tracker has been installed to:
echo %INSTALL_DIR%
echo.
echo A shortcut has been created on your desktop.
echo.
echo Default login:
echo Username: admin
echo Password: admin123
echo.
set /p START_NOW=Would you like to start the application now? (y/n): 
if /i "%START_NOW%"=="y" (
    start "" "%INSTALL_DIR%\HPM_Inventory.bat"
)

echo.
echo Thank you for using HPM Inventory Tracker!
pause
