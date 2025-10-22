# Building Mac Executable - Instructions

This guide will help you create a standalone Mac application (.app) for the Scoreboard Data Manager with a custom pennant icon.

## Quick Start (Automated)

If you're on a Mac, simply run:

```bash
./build_mac_app.sh
```

This will automatically:
1. Install all dependencies
2. Create the pennant icon
3. Build the Mac application

Your app will be in: `dist/Scoreboard Data Manager.app`

## Manual Build Process

If you prefer to build manually or troubleshoot:

### Prerequisites

- macOS computer
- Python 3.7 or later
- Internet connection (for downloading packages)

### Step-by-Step Instructions

#### 1. Install Dependencies

```bash
pip3 install pyinstaller requests pyserial obsws-python pillow
```

#### 2. Create the Pennant Icon

```bash
python3 create_icon.py
./create_icns.sh
```

This creates `pennant.icns` with a blue pennant flag design.

#### 3. Build the Application

```bash
pyinstaller \
    --onefile \
    --windowed \
    --name "Scoreboard Data Manager" \
    --add-data "daktronics:daktronics" \
    --icon "pennant.icns" \
    --osx-bundle-identifier "com.scoreboardmanager.app" \
    "scoreboard_gui official version.py"
```

#### 4. Find Your Application

The finished app will be in: `dist/Scoreboard Data Manager.app`

## Using the Application

### First Launch

1. Navigate to the `dist` folder
2. Right-click on `Scoreboard Data Manager.app`
3. Select "Open" from the menu
4. Click "Open" when prompted about an unsigned app

(This is only needed the first time because the app isn't signed with an Apple Developer certificate)

### Moving to Applications

You can drag the app to your Applications folder or anywhere else. It's completely self-contained.

### Sharing with Others

You can share the `.app` file with other Mac users. They don't need:
- Python installed
- Any dependencies
- Any setup process

Just send them the .app file and they can run it!

## Customizing the Icon

The pennant icon is created by `create_icon.py`. To customize it:

1. Edit `create_icon.py`
2. Modify the colors:
   - `pennant_color`: Main pennant color
   - `outline_color`: Border color
   - `pole_color`: Flagpole color
3. Re-run: `python3 create_icon.py && ./create_icns.sh`
4. Rebuild the app

## Troubleshooting

### "command not found: pyinstaller"

Make sure you've installed it:
```bash
pip3 install pyinstaller
```

If still not found, try:
```bash
python3 -m PyInstaller [rest of command]
```

### "iconutil: command not found"

This command should be available on all Macs by default. Make sure you're running on macOS.

### Build fails with "No module named 'daktronics'"

Make sure the `daktronics` folder is in the same directory as the script.

### App won't open - "damaged or incomplete"

This happens when the build fails partway through. Delete the `build` and `dist` folders and rebuild:
```bash
rm -rf build dist
./build_mac_app.sh
```

### Serial ports not detected in built app

The built app should work with serial ports. If you have issues:
1. Make sure you've installed pyserial before building
2. Check that your USB-serial adapter drivers are installed on the Mac

## Technical Details

**Build Output:**
- `build/` - Temporary build files (can be deleted)
- `dist/` - Your finished application
- `*.spec` - PyInstaller specification file

**Application Size:**
The final .app will be approximately 15-25 MB.

**What's Included:**
- Python interpreter
- All required libraries (requests, pyserial, obsws-python, tkinter)
- Daktronics module
- Your pennant icon

## Advanced Options

### Building without Icon

Remove the `--icon` parameter:
```bash
pyinstaller --onefile --windowed --name "Scoreboard Data Manager" \
    --add-data "daktronics:daktronics" "scoreboard_gui official version.py"
```

### Building a Folder App Instead of Single File

Change `--onefile` to `--onedir`:
```bash
pyinstaller --onedir --windowed ... [rest of parameters]
```

This creates a folder with the app and libraries separate (larger but faster to launch).

### Adding a Splash Screen

Create a splash image and add:
```bash
--splash "splash.png"
```

## Clean Build

To completely rebuild from scratch:

```bash
rm -rf build dist *.spec
./build_mac_app.sh
```

---

## Need Help?

- Check the PyInstaller docs: https://pyinstaller.org
- Make sure you're using Python 3.7+
- Ensure all source files are in the directory
