#!/usr/bin/env python3
"""
Development runner for HPM Inventory Tracker Desktop Application
Use this for testing the desktop app during development
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from desktop_app import HPMInventoryApp

if __name__ == "__main__":
    print("Starting HPM Inventory Tracker Desktop Application...")
    print("This is the development version - use build_desktop.py to create a distributable version")
    
    app = HPMInventoryApp()
    app.run()