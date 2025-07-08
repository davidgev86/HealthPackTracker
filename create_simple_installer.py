#!/usr/bin/env python3
"""
Create a simple one-click installer for Windows users
"""

import os
import shutil
import zipfile
from pathlib import Path

def create_simple_installer():
    """Create a simple installer package"""
    
    print("Creating simple installer package...")
    
    # Create installer directory
    installer_dir = Path("HPM_Simple_Installer")
    if installer_dir.exists():
        shutil.rmtree(installer_dir)
    installer_dir.mkdir()
    
    # Copy the easy installer
    shutil.copy2("easy_installer.py", installer_dir / "INSTALL_HPM_INVENTORY.py")
    
    # Copy all application files
    files_to_include = [
        "desktop_app.py", "app.py", "main.py", "models.py", "routes.py", "utils.py",
        "requirements_desktop.txt", "DESKTOP_README.md", "WORKFLOW_GUIDE.md",
        "WORKFLOW_QUICK_REFERENCE.md", "GOOGLE_SHEETS_TEMPLATE.csv"
    ]
    
    for file_name in files_to_include:
        src = Path(file_name)
        if src.exists():
            shutil.copy2(src, installer_dir / file_name)
    
    # Copy directories
    for dir_name in ["templates", "static"]:
        src_dir = Path(dir_name)
        if src_dir.exists():
            shutil.copytree(src_dir, installer_dir / dir_name)
    
    # Create simple batch installer for Windows
    batch_installer = """@echo off
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
set INSTALL_DIR=%USERPROFILE%\\HPM_Inventory
mkdir "%INSTALL_DIR%" 2>nul

REM Copy files
echo Copying application files...
xcopy /s /e /y * "%INSTALL_DIR%\\" >nul

REM Install dependencies
echo Installing dependencies...
cd /d "%INSTALL_DIR%"
python -m pip install flask werkzeug >nul 2>&1

REM Create desktop shortcut
echo Creating desktop shortcut...
echo @echo off > "%INSTALL_DIR%\\HPM_Inventory.bat"
echo cd /d "%INSTALL_DIR%" >> "%INSTALL_DIR%\\HPM_Inventory.bat"
echo python desktop_app.py >> "%INSTALL_DIR%\\HPM_Inventory.bat"

copy "%INSTALL_DIR%\\HPM_Inventory.bat" "%USERPROFILE%\\Desktop\\HPM Inventory Tracker.bat" >nul 2>&1

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
    start "" "%INSTALL_DIR%\\HPM_Inventory.bat"
)

echo.
echo Thank you for using HPM Inventory Tracker!
pause
"""
    
    with open(installer_dir / "INSTALL.bat", "w") as f:
        f.write(batch_installer)
    
    # Create user instructions
    instructions = """# HPM Inventory Tracker - Installation Instructions

## For Non-Technical Users (EASIEST METHOD)

### Option 1: One-Click Installation
1. Double-click "INSTALL.bat"
2. Follow the prompts
3. Wait for installation to complete
4. Start using the application!

### Option 2: Python Installation (if Option 1 doesn't work)
1. Double-click "INSTALL_HPM_INVENTORY.py"
2. Click "Install HPM Inventory Tracker"
3. Wait for installation to complete

## What This Installs

- HPM Inventory Tracker application
- Python (if not already installed)
- Desktop shortcut
- Data folder in your user directory

## After Installation

1. Double-click the "HPM Inventory Tracker" shortcut on your desktop
2. Click "Open Inventory System" in the window that appears
3. Login with:
   - Username: admin
   - Password: admin123
4. Start managing your inventory!

## Your Data Location

Your inventory data will be stored at:
C:\\Users\\[YourName]\\HPM_Inventory_Data\\

## Need Help?

- Check the WORKFLOW_GUIDE.md file for detailed instructions
- Use the GOOGLE_SHEETS_TEMPLATE.csv to set up team collaboration
- Contact your IT support if you encounter issues

## Default Features Included

✓ Complete inventory management
✓ User accounts with different access levels
✓ Waste tracking and logging
✓ Import/Export with Google Sheets
✓ Mobile-friendly web interface
✓ Automatic data backup tools
"""
    
    with open(installer_dir / "README.txt", "w") as f:
        f.write(instructions)
    
    # Create ZIP file
    zip_path = "HPM_Inventory_Simple_Installer.zip"
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(installer_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, installer_dir.parent)
                zipf.write(file_path, arcname)
    
    print(f"✅ Simple installer created: {installer_dir.absolute()}")
    print(f"✅ ZIP file created: {zip_path}")
    print("\n📁 Installer contents:")
    for item in sorted(installer_dir.rglob("*")):
        if item.is_file():
            print(f"  📄 {item.relative_to(installer_dir)}")
    
    print(f"\n🎉 Ready for distribution!")
    print(f"Send the ZIP file to users with these simple instructions:")
    print(f"1. Extract the ZIP file")
    print(f"2. Double-click INSTALL.bat")
    print(f"3. Follow the prompts")

if __name__ == "__main__":
    create_simple_installer()