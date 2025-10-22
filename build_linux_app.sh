#!/bin/bash
# Build Linux executable for Scoreboard Data Manager

set -e  # Exit on error

echo "========================================="
echo "Scoreboard Data Manager - Linux Build"
echo "========================================="
echo ""

# Step 1: Check Python
echo "Step 1: Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Install with: sudo apt install python3 python3-pip"
    exit 1
fi
python3 --version
echo ""

# Step 2: Install dependencies
echo "Step 2: Installing required Python packages..."
pip3 install --user pyinstaller requests pyserial obsws-python pillow 2>/dev/null || \
pip3 install pyinstaller requests pyserial obsws-python pillow
echo ""

# Step 3: Create icon if it doesn't exist
if [ ! -f "pennant_icon.png" ]; then
    echo "Step 3: Creating pennant icon..."
    python3 create_icon.py
    echo ""
else
    echo "Step 3: Icon already exists, skipping..."
    echo ""
fi

# Step 4: Build with PyInstaller
echo "Step 4: Building Linux executable..."
echo "This may take a few minutes..."
echo ""

pyinstaller \
    --onefile \
    --windowed \
    --name "scoreboard-data-manager" \
    --add-data "daktronics:daktronics" \
    --icon "pennant_icon.png" \
    "scoreboard_gui official version.py"

echo ""
echo "========================================="
echo "Build Complete!"
echo "========================================="
echo ""
echo "Your Linux executable is ready:"
echo "  Location: dist/scoreboard-data-manager"
echo ""
echo "You can now:"
echo "  1. Run it directly: ./dist/scoreboard-data-manager"
echo "  2. Move it to /usr/local/bin for system-wide access"
echo "  3. Create a desktop launcher (see instructions)"
echo "  4. Share it with other Linux users"
echo ""
echo "Note: Recipients must have the same architecture (x86_64, ARM, etc.)"
echo ""

# Step 5: Make executable
chmod +x dist/scoreboard-data-manager

# Step 6: Create .desktop file
echo "Creating desktop launcher file..."
cat > "Scoreboard-Data-Manager.desktop" << 'DESKTOP_EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Scoreboard Data Manager
Comment=Capture and export live scoreboard data from Daktronics scoreboards
Exec=INSTALL_PATH/scoreboard-data-manager
Icon=INSTALL_PATH/pennant_icon.png
Terminal=false
Categories=Utility;Sports;
Keywords=scoreboard;daktronics;sports;streaming;obs;
DESKTOP_EOF

echo ""
echo "Desktop launcher created: Scoreboard-Data-Manager.desktop"
echo ""
echo "To install the desktop launcher:"
echo "  1. Copy the executable and icon to a permanent location"
echo "  2. Edit Scoreboard-Data-Manager.desktop and replace INSTALL_PATH with the actual path"
echo "  3. Copy the .desktop file to ~/.local/share/applications/"
echo ""
