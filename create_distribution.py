#!/usr/bin/env python3
"""
Create distribution package for HPM Inventory Tracker Desktop Application
"""

import os
import shutil
import zipfile
from pathlib import Path
import sys

def create_distribution():
    """Create a distribution package for the desktop application"""
    
    print("Creating HPM Inventory Tracker distribution package...")
    
    # Create distribution directory
    dist_dir = Path("HPM_Inventory_Desktop_Distribution")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    # List of files to include in distribution
    files_to_include = [
        "desktop_app.py",
        "run_desktop.py",
        "setup_desktop.py",
        "build_desktop.py",
        "requirements_desktop.txt",
        "DESKTOP_README.md",
        "WORKFLOW_GUIDE.md",
        "WORKFLOW_QUICK_REFERENCE.md",
        "GOOGLE_SHEETS_TEMPLATE.csv",
        "app.py",
        "main.py",
        "models.py",
        "routes.py",
        "utils.py",
        "templates/",
        "static/"
    ]
    
    # Copy files to distribution directory
    for item in files_to_include:
        src = Path(item)
        if src.exists():
            if src.is_file():
                shutil.copy2(src, dist_dir / src.name)
            else:  # Directory
                shutil.copytree(src, dist_dir / src.name)
    
    # Create installation script for each platform
    
    # Windows installation script
    windows_install = """@echo off
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
"""
    
    # macOS/Linux installation script
    unix_install = """#!/bin/bash
echo "Installing HPM Inventory Tracker..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or later"
    exit 1
fi

# Install dependencies
echo "Installing required packages..."
python3 -m pip install -r requirements_desktop.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo
echo "Installation complete!"
echo
echo "To run the application:"
echo "  python3 run_desktop.py"
echo
echo "To build a standalone executable:"
echo "  python3 build_desktop.py"
echo
"""
    
    # Write installation scripts
    with open(dist_dir / "install_windows.bat", "w") as f:
        f.write(windows_install)
    
    with open(dist_dir / "install_unix.sh", "w") as f:
        f.write(unix_install)
    
    # Make Unix script executable
    os.chmod(dist_dir / "install_unix.sh", 0o755)
    
    # Create quick start guide
    quick_start = """# HPM Inventory Tracker - Quick Start Guide

## Installation

### Windows
1. Ensure Python 3.8+ is installed
2. Double-click `install_windows.bat`
3. Follow the prompts

### macOS/Linux
1. Ensure Python 3.8+ is installed
2. Run `chmod +x install_unix.sh && ./install_unix.sh`

## Running the Application

### Development Mode (Recommended for first-time users)
```bash
# Windows
python run_desktop.py

# macOS/Linux
python3 run_desktop.py
```

### Building Standalone Executable
```bash
# Windows
python build_desktop.py

# macOS/Linux
python3 build_desktop.py
```

## Default Login
- Username: admin
- Password: admin123

## Features
- Complete inventory management
- Waste tracking and logging
- CSV import/export
- Role-based access control
- Mobile-friendly interface
- Automatic data backup

## Data Location
Your data will be stored in:
- Windows: `C:\\Users\\[username]\\HPM_Inventory_Data\\`
- macOS/Linux: `~/HPM_Inventory_Data/`

## Support
For technical support, please refer to DESKTOP_README.md or contact your system administrator.
"""
    
    with open(dist_dir / "QUICK_START.md", "w") as f:
        f.write(quick_start)
    
    # Create ZIP file for easy distribution
    zip_path = "HPM_Inventory_Desktop_v1.0.zip"
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, dist_dir.parent)
                zipf.write(file_path, arcname)
    
    print(f"✅ Distribution package created: {dist_dir.absolute()}")
    print(f"✅ ZIP file created: {zip_path}")
    print("\nDistribution contents:")
    for item in sorted(dist_dir.rglob("*")):
        if item.is_file():
            print(f"  📄 {item.relative_to(dist_dir)}")
    
    print(f"\n🎉 Ready for distribution!")
    print(f"Send the ZIP file or folder to users along with installation instructions.")

if __name__ == "__main__":
    create_distribution()