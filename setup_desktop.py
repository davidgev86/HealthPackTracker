#!/usr/bin/env python3
"""
Setup script for HPM Inventory Tracker Desktop Application
Installs dependencies and prepares the environment
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing desktop application requirements...")
    
    try:
        # Install desktop requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_desktop.txt"])
        print("✅ Desktop requirements installed successfully")
        
        # Install existing web app requirements if they exist
        if os.path.exists("requirements.txt"):
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Web app requirements installed successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        sys.exit(1)

def setup_environment():
    """Setup development environment"""
    print("Setting up development environment...")
    
    # Create necessary directories
    os.makedirs("dist", exist_ok=True)
    os.makedirs("build", exist_ok=True)
    
    print("✅ Environment setup complete")

def main():
    """Main setup function"""
    print("HPM Inventory Tracker Desktop Application Setup")
    print("=" * 50)
    
    install_requirements()
    setup_environment()
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Test the app: python run_desktop.py")
    print("2. Build executable: python build_desktop.py")
    print("3. Distribute the files in dist/HPM_Inventory_Installer/")

if __name__ == "__main__":
    main()