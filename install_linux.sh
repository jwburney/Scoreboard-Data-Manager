#!/bin/bash
# Install Scoreboard Data Manager to Linux system

set -e

echo "========================================="
echo "Scoreboard Data Manager - Installer"
echo "========================================="
echo ""

# Check if executable exists
if [ ! -f "dist/scoreboard-data-manager" ]; then
    echo "ERROR: Executable not found!"
    echo "Please run ./build_linux_app.sh first"
    exit 1
fi

# Determine install location
echo "Choose installation type:"
echo "  1) User install (no sudo required) - ~/.local/bin"
echo "  2) System install (requires sudo) - /usr/local/bin"
echo ""
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        INSTALL_DIR="$HOME/.local/bin"
        ICON_DIR="$HOME/.local/share/icons"
        DESKTOP_DIR="$HOME/.local/share/applications"
        NEEDS_SUDO=false
        echo ""
        echo "Installing for current user only..."
        ;;
    2)
        INSTALL_DIR="/usr/local/bin"
        ICON_DIR="/usr/share/icons/hicolor/1024x1024/apps"
        DESKTOP_DIR="/usr/share/applications"
        NEEDS_SUDO=true
        echo ""
        echo "Installing system-wide (requires sudo)..."
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

# Create directories
if [ "$NEEDS_SUDO" = true ]; then
    sudo mkdir -p "$INSTALL_DIR"
    sudo mkdir -p "$ICON_DIR"
    sudo mkdir -p "$DESKTOP_DIR"
else
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$ICON_DIR"
    mkdir -p "$DESKTOP_DIR"
fi

echo ""
echo "Installing files..."

# Copy executable
if [ "$NEEDS_SUDO" = true ]; then
    sudo cp dist/scoreboard-data-manager "$INSTALL_DIR/"
    sudo chmod +x "$INSTALL_DIR/scoreboard-data-manager"
else
    cp dist/scoreboard-data-manager "$INSTALL_DIR/"
    chmod +x "$INSTALL_DIR/scoreboard-data-manager"
fi
echo "  ✓ Executable installed to $INSTALL_DIR"

# Copy icon
if [ "$NEEDS_SUDO" = true ]; then
    sudo cp pennant_icon.png "$ICON_DIR/scoreboard-data-manager.png"
else
    cp pennant_icon.png "$ICON_DIR/scoreboard-data-manager.png"
fi
echo "  ✓ Icon installed to $ICON_DIR"

# Create desktop file
DESKTOP_FILE=$(mktemp)
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Scoreboard Data Manager
Comment=Capture and export live scoreboard data from Daktronics scoreboards
Exec=$INSTALL_DIR/scoreboard-data-manager
Icon=scoreboard-data-manager
Terminal=false
Categories=Utility;Sports;
Keywords=scoreboard;daktronics;sports;streaming;obs;
EOF

if [ "$NEEDS_SUDO" = true ]; then
    sudo cp "$DESKTOP_FILE" "$DESKTOP_DIR/scoreboard-data-manager.desktop"
    sudo chmod +x "$DESKTOP_DIR/scoreboard-data-manager.desktop"
else
    cp "$DESKTOP_FILE" "$DESKTOP_DIR/scoreboard-data-manager.desktop"
    chmod +x "$DESKTOP_DIR/scoreboard-data-manager.desktop"
fi
rm "$DESKTOP_FILE"
echo "  ✓ Desktop launcher installed to $DESKTOP_DIR"

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    if [ "$NEEDS_SUDO" = true ]; then
        sudo update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    else
        update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    fi
fi

echo ""
echo "========================================="
echo "Installation Complete!"
echo "========================================="
echo ""
echo "You can now:"
echo "  • Run from command line: scoreboard-data-manager"
echo "  • Launch from application menu: Search for 'Scoreboard Data Manager'"
echo "  • Find it in your application launcher (may need to log out/in)"
echo ""
echo "To uninstall:"
if [ "$NEEDS_SUDO" = true ]; then
    echo "  sudo rm $INSTALL_DIR/scoreboard-data-manager"
    echo "  sudo rm $ICON_DIR/scoreboard-data-manager.png"
    echo "  sudo rm $DESKTOP_DIR/scoreboard-data-manager.desktop"
else
    echo "  rm $INSTALL_DIR/scoreboard-data-manager"
    echo "  rm $ICON_DIR/scoreboard-data-manager.png"
    echo "  rm $DESKTOP_DIR/scoreboard-data-manager.desktop"
fi
echo ""
