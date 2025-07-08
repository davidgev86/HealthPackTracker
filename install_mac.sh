#!/bin/bash

# HPM Inventory Tracker - macOS Installation Script

echo "HPM Inventory Tracker - macOS Installer"
echo "========================================"
echo ""

# Set installation directory
INSTALL_DIR="$HOME/HPM_Inventory"
echo "Installation directory: $INSTALL_DIR"
echo ""

# Create installation directory
mkdir -p "$INSTALL_DIR"

# Check if Python 3 is installed
if command -v python3 &> /dev/null; then
    echo "✓ Python 3 found"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | grep -o "3\.[0-9]")
    if [ ! -z "$PYTHON_VERSION" ]; then
        echo "✓ Python 3 found"
        PYTHON_CMD="python"
    else
        echo "❌ Python 3 not found"
        PYTHON_CMD=""
    fi
else
    echo "❌ Python not found"
    PYTHON_CMD=""
fi

# Install Python if needed
if [ -z "$PYTHON_CMD" ]; then
    echo ""
    echo "Installing Python 3..."
    
    # Check if Homebrew is installed
    if command -v brew &> /dev/null; then
        echo "Using Homebrew to install Python..."
        brew install python3
        PYTHON_CMD="python3"
    else
        echo "Homebrew not found. Please install Python 3 manually from:"
        echo "https://www.python.org/downloads/macos/"
        echo ""
        read -p "Press Enter after installing Python 3..."
        
        # Check again
        if command -v python3 &> /dev/null; then
            PYTHON_CMD="python3"
        else
            echo "❌ Python 3 still not found. Installation failed."
            exit 1
        fi
    fi
fi

echo ""
echo "Copying application files..."

# Copy all files to installation directory
cp -r * "$INSTALL_DIR/"

# Install Python dependencies
echo "Installing dependencies..."
cd "$INSTALL_DIR"
$PYTHON_CMD -m pip install flask werkzeug --user

# Create launch script
echo "Creating launch script..."
cat > "$INSTALL_DIR/launch_hpm.sh" << 'EOL'
#!/bin/bash
cd "$(dirname "$0")"
if command -v python3 &> /dev/null; then
    python3 desktop_app.py
else
    python desktop_app.py
fi
EOL

# Make launch script executable
chmod +x "$INSTALL_DIR/launch_hpm.sh"

# Create desktop shortcut
echo "Creating desktop shortcut..."
DESKTOP_DIR="$HOME/Desktop"
if [ -d "$DESKTOP_DIR" ]; then
    # Create .app bundle for better macOS integration
    APP_NAME="HPM Inventory Tracker.app"
    APP_PATH="$DESKTOP_DIR/$APP_NAME"
    
    mkdir -p "$APP_PATH/Contents/MacOS"
    mkdir -p "$APP_PATH/Contents/Resources"
    
    # Create Info.plist
    cat > "$APP_PATH/Contents/Info.plist" << 'EOL'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>HPM_Inventory</string>
    <key>CFBundleIdentifier</key>
    <string>com.hpm.inventory</string>
    <key>CFBundleName</key>
    <string>HPM Inventory Tracker</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
</dict>
</plist>
EOL

    # Create executable
    cat > "$APP_PATH/Contents/MacOS/HPM_Inventory" << EOL
#!/bin/bash
cd "$INSTALL_DIR"
if command -v python3 &> /dev/null; then
    python3 desktop_app.py
else
    python desktop_app.py
fi
EOL

    chmod +x "$APP_PATH/Contents/MacOS/HPM_Inventory"
fi

echo ""
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "HPM Inventory Tracker has been installed to:"
echo "$INSTALL_DIR"
echo ""
echo "To start the application:"
echo "1. Double-click 'HPM Inventory Tracker' on your desktop, OR"
echo "2. Run: $INSTALL_DIR/launch_hpm.sh"
echo ""
echo "Default login credentials:"
echo "Username: admin"
echo "Password: admin123"
echo ""
echo "Your inventory data will be stored in:"
echo "$HOME/HPM_Inventory_Data/"
echo ""

read -p "Would you like to start the application now? (y/n): " START_NOW
if [ "$START_NOW" = "y" ] || [ "$START_NOW" = "Y" ]; then
    echo "Starting HPM Inventory Tracker..."
    cd "$INSTALL_DIR"
    $PYTHON_CMD desktop_app.py &
fi

echo ""
echo "Installation complete! Thank you for using HPM Inventory Tracker."