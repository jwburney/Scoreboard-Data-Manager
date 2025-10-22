#!/bin/bash
# Build Mac executable for Scoreboard Data Manager
# This script must be run on macOS

set -e  # Exit on error

echo "========================================="
echo "Scoreboard Data Manager - Mac Build"
echo "========================================="
echo ""

# Check if running on Mac
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "ERROR: This script must be run on macOS"
    echo "Current OS: $OSTYPE"
    exit 1
fi

# Step 1: Check Python
echo "Step 1: Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3 from https://www.python.org/downloads/"
    exit 1
fi
python3 --version
echo ""

# Step 2: Install dependencies
echo "Step 2: Installing required Python packages..."
pip3 install --upgrade pip
pip3 install pyinstaller requests pyserial obsws-python pillow
echo ""

# Step 3: Create icons
echo "Step 3: Creating pennant icon..."
python3 create_icon.py
echo ""

# Step 4: Create .icns file
echo "Step 4: Converting to .icns format..."
bash create_icns.sh
echo ""

# Step 5: Build with PyInstaller
echo "Step 5: Building Mac application..."
echo "This may take a few minutes..."
echo ""

pyinstaller \
    --onefile \
    --windowed \
    --name "Scoreboard Data Manager" \
    --add-data "daktronics:daktronics" \
    --icon "pennant.icns" \
    --osx-bundle-identifier "com.scoreboardmanager.app" \
    "scoreboard_gui official version.py"

echo ""
echo "========================================="
echo "Build Complete!"
echo "========================================="
echo ""
echo "Your Mac application is ready:"
echo "  Location: dist/Scoreboard Data Manager.app"
echo ""
echo "You can now:"
echo "  1. Open the app from Finder"
echo "  2. Move it to your Applications folder"
echo "  3. Share it with others (they don't need Python installed)"
echo ""
echo "Note: On first run, you may need to right-click and select 'Open'"
echo "      to bypass Mac's security check for unsigned apps."
echo ""
