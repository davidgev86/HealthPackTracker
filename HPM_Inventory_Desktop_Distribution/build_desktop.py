#!/usr/bin/env python3
"""
Build script for HPM Inventory Tracker Desktop Application
Creates standalone executables for macOS and Windows
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_desktop_app():
    """Build the desktop application using PyInstaller"""
    
    print("Building HPM Inventory Tracker Desktop Application...")
    
    # Clean previous builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=HPM_Inventory_Tracker",
        "--add-data=templates:templates",
        "--add-data=static:static",
        "--hidden-import=werkzeug.security",
        "--hidden-import=csv",
        "--hidden-import=datetime",
        "desktop_app.py"
    ]
    
    # Platform-specific options
    if sys.platform == "darwin":  # macOS
        cmd.extend([
            "--icon=icon.icns",  # Add icon if available
            "--osx-bundle-identifier=com.healthpackmeals.inventory"
        ])
    elif sys.platform == "win32":  # Windows
        cmd.extend([
            "--icon=icon.ico",  # Add icon if available
        ])
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build successful!")
            print(f"Executable created in: {Path('dist').absolute()}")
            
            # Create installer folder with additional files
            installer_dir = Path("dist/HPM_Inventory_Installer")
            installer_dir.mkdir(exist_ok=True)
            
            # Copy executable
            exe_name = "HPM_Inventory_Tracker.exe" if sys.platform == "win32" else "HPM_Inventory_Tracker"
            shutil.copy2(f"dist/{exe_name}", installer_dir)
            
            # Create README for users
            readme_content = """# HPM Inventory Tracker

## Installation Instructions

1. Copy the HPM_Inventory_Tracker executable to your desired location
2. Double-click to run the application
3. The application will create a data folder in your home directory
4. Click "Open Inventory System" to access the web interface
5. Default login: admin / admin123

## Data Location

Your inventory data is stored in:
- macOS: ~/HPM_Inventory_Data/
- Windows: C:\\Users\\[username]\\HPM_Inventory_Data\\

## Features

- Complete inventory management system
- Role-based user access (Admin, Manager, Staff)
- Waste logging and tracking
- CSV import/export capabilities
- Mobile-friendly web interface
- Automatic data backup functionality

## Support

For support, please contact Health Pack Meals technical support.
"""
            
            with open(installer_dir / "README.txt", "w") as f:
                f.write(readme_content)
            
            print(f"📁 Installer package created in: {installer_dir.absolute()}")
            
        else:
            print("❌ Build failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            
    except Exception as e:
        print(f"❌ Build error: {e}")

if __name__ == "__main__":
    build_desktop_app()