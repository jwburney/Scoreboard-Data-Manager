# Building Linux Executable - Instructions

This guide will help you create a standalone Linux executable for the Scoreboard Data Manager with a custom pennant icon.

## Quick Start (Automated)

### Build the Executable

```bash
./build_linux_app.sh
```

This will automatically:
1. Install all dependencies
2. Create the pennant icon (if needed)
3. Build the Linux executable
4. Create a desktop launcher file

Your executable will be in: `dist/scoreboard-data-manager`

### Install System-Wide (Optional)

```bash
./install_linux.sh
```

This interactive script lets you choose:
- **User install**: Installs to ~/.local/bin (no sudo needed)
- **System install**: Installs to /usr/local/bin (requires sudo)

After installation, you can launch from your application menu!

## Manual Build Process

If you prefer to build manually or troubleshoot:

### Prerequisites

- Linux (Ubuntu, Debian, Fedora, Arch, etc.)
- Python 3.7 or later
- pip (Python package manager)
- Internet connection

### Installing System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-tk
```

**Fedora:**
```bash
sudo dnf install python3 python3-pip python3-tkinter
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip tk
```

### Step-by-Step Instructions

#### 1. Install Python Dependencies

```bash
pip3 install pyinstaller requests pyserial obsws-python pillow
```

Or use pip with user flag to avoid sudo:
```bash
pip3 install --user pyinstaller requests pyserial obsws-python pillow
```

#### 2. Create the Pennant Icon (if needed)

```bash
python3 create_icon.py
```

This creates `pennant_icon.png` with a blue pennant flag design.

#### 3. Build the Executable

```bash
pyinstaller \
    --onefile \
    --windowed \
    --name "scoreboard-data-manager" \
    --add-data "daktronics:daktronics" \
    --icon "pennant_icon.png" \
    "scoreboard_gui official version.py"
```

#### 4. Test the Executable

```bash
chmod +x dist/scoreboard-data-manager
./dist/scoreboard-data-manager
```

## Installation Options

### Option 1: Run from Anywhere (User)

Add to your PATH:
```bash
mkdir -p ~/.local/bin
cp dist/scoreboard-data-manager ~/.local/bin/
```

Then add to your `~/.bashrc` or `~/.zshrc`:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

### Option 2: System-Wide Installation

```bash
sudo cp dist/scoreboard-data-manager /usr/local/bin/
```

Now anyone on the system can run: `scoreboard-data-manager`

### Option 3: Desktop Launcher

Create `~/.local/share/applications/scoreboard-data-manager.desktop`:

```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=Scoreboard Data Manager
Comment=Capture and export live scoreboard data
Exec=/path/to/scoreboard-data-manager
Icon=/path/to/pennant_icon.png
Terminal=false
Categories=Utility;Sports;
```

Replace `/path/to/` with actual paths, then:
```bash
chmod +x ~/.local/share/applications/scoreboard-data-manager.desktop
update-desktop-database ~/.local/share/applications/
```

## Distribution

### Sharing with Others

The executable can be shared with other Linux users on the **same architecture**:

- **x86_64** (64-bit Intel/AMD) - Most common
- **ARM** (Raspberry Pi, ARM servers)
- **i686** (32-bit Intel/AMD) - Older systems

Recipients need:
- Same architecture (x86_64, ARM, etc.)
- No Python installation required
- No dependencies required

### Creating an AppImage (Advanced)

For universal Linux compatibility, consider creating an AppImage:

```bash
# Install appimagetool
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

# Create AppDir structure
mkdir -p ScoreboardDataManager.AppDir/usr/bin
mkdir -p ScoreboardDataManager.AppDir/usr/share/icons/hicolor/256x256/apps

# Copy files
cp dist/scoreboard-data-manager ScoreboardDataManager.AppDir/usr/bin/
cp pennant_icon.png ScoreboardDataManager.AppDir/usr/share/icons/hicolor/256x256/apps/

# Create .desktop file
cat > ScoreboardDataManager.AppDir/scoreboard-data-manager.desktop << 'EOF'
[Desktop Entry]
Name=Scoreboard Data Manager
Exec=scoreboard-data-manager
Icon=pennant_icon
Type=Application
Categories=Utility;
EOF

# Create AppRun
cat > ScoreboardDataManager.AppDir/AppRun << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
exec "${HERE}/usr/bin/scoreboard-data-manager" "$@"
EOF
chmod +x ScoreboardDataManager.AppDir/AppRun

# Build AppImage
./appimagetool-x86_64.AppImage ScoreboardDataManager.AppDir
```

Now you have a universal `Scoreboard_Data_Manager-x86_64.AppImage` that works on any Linux distro!

## Troubleshooting

### "command not found: pyinstaller"

Make sure pip's bin directory is in your PATH:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

Or install system-wide:
```bash
sudo pip3 install pyinstaller
```

### "No module named 'tkinter'"

Install tkinter:
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

### Executable won't run - "Permission denied"

Make it executable:
```bash
chmod +x dist/scoreboard-data-manager
```

### "No module named 'daktronics'"

Make sure the `daktronics` folder is in the same directory when building.

### Serial ports not accessible

Add your user to the dialout group:
```bash
sudo usermod -a -G dialout $USER
```

Then log out and back in.

### Build fails with "Failed to execute script"

Try building without `--windowed` flag to see error messages:
```bash
pyinstaller --onefile --name "scoreboard-data-manager" \
    --add-data "daktronics:daktronics" \
    "scoreboard_gui official version.py"
```

## Technical Details

### Build Output

- `build/` - Temporary build files (can be deleted)
- `dist/` - Your finished executable
- `*.spec` - PyInstaller specification file

### Executable Size

The final executable will be approximately **15-30 MB** depending on architecture.

### What's Included

- Python interpreter
- All required libraries (requests, pyserial, obsws-python, tkinter)
- Daktronics module
- Your pennant icon

### Performance

- **Cold start**: 2-5 seconds (first run)
- **Warm start**: 1-2 seconds (subsequent runs)
- **Runtime**: Identical to Python script

## Platform-Specific Notes

### Ubuntu/Debian

Tkinter may not be included by default:
```bash
sudo apt install python3-tk
```

### Fedora/RHEL

Install development tools if you encounter build errors:
```bash
sudo dnf groupinstall "Development Tools"
```

### Arch Linux

All dependencies are usually in the repos:
```bash
sudo pacman -S python python-pip tk
```

### Raspberry Pi (ARM)

The build process is the same, but the executable will only work on other ARM devices (other Raspberry Pis).

## Clean Build

To completely rebuild from scratch:

```bash
rm -rf build dist *.spec
./build_linux_app.sh
```

## Uninstallation

### If installed via install_linux.sh

**User install:**
```bash
rm ~/.local/bin/scoreboard-data-manager
rm ~/.local/share/icons/scoreboard-data-manager.png
rm ~/.local/share/applications/scoreboard-data-manager.desktop
```

**System install:**
```bash
sudo rm /usr/local/bin/scoreboard-data-manager
sudo rm /usr/share/icons/hicolor/1024x1024/apps/scoreboard-data-manager.png
sudo rm /usr/share/applications/scoreboard-data-manager.desktop
```

## Advanced Options

### Building without Icon

Remove the `--icon` parameter:
```bash
pyinstaller --onefile --windowed --name "scoreboard-data-manager" \
    --add-data "daktronics:daktronics" "scoreboard_gui official version.py"
```

### Building with Console (for debugging)

Remove `--windowed`:
```bash
pyinstaller --onefile --name "scoreboard-data-manager" \
    --add-data "daktronics:daktronics" "scoreboard_gui official version.py"
```

This shows a console window with debug output.

### Building a Directory App Instead of Single File

Change `--onefile` to `--onedir`:
```bash
pyinstaller --onedir --windowed ... [rest of parameters]
```

This creates a folder with the app and libraries separate (larger but faster to launch).

## Creating a .deb Package (Debian/Ubuntu)

For easy installation on Debian-based systems:

```bash
# Install packaging tools
sudo apt install build-essential debhelper

# Create package structure
mkdir -p scoreboard-data-manager_1.0/DEBIAN
mkdir -p scoreboard-data-manager_1.0/usr/local/bin
mkdir -p scoreboard-data-manager_1.0/usr/share/applications
mkdir -p scoreboard-data-manager_1.0/usr/share/icons/hicolor/1024x1024/apps

# Copy files
cp dist/scoreboard-data-manager scoreboard-data-manager_1.0/usr/local/bin/
cp pennant_icon.png scoreboard-data-manager_1.0/usr/share/icons/hicolor/1024x1024/apps/
cp Scoreboard-Data-Manager.desktop scoreboard-data-manager_1.0/usr/share/applications/

# Create control file
cat > scoreboard-data-manager_1.0/DEBIAN/control << 'EOF'
Package: scoreboard-data-manager
Version: 1.0
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Your Name <your@email.com>
Description: Scoreboard Data Manager
 Capture and export live scoreboard data from Daktronics scoreboards.
EOF

# Build package
dpkg-deb --build scoreboard-data-manager_1.0

# Install with
sudo dpkg -i scoreboard-data-manager_1.0.deb
```

---

## Need Help?

- Check PyInstaller docs: https://pyinstaller.org
- Ensure you're using Python 3.7+
- Verify all source files are in the directory
- Try building without `--windowed` to see errors
- Check permissions on executable with `ls -l`
