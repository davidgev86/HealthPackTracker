#!/bin/bash
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
