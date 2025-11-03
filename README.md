# Scoreboard Data Manager

A desktop application for capturing live scoreboard data from Daktronics scoreboards and exporting it in multiple formats for streaming, broadcasting, and data visualization.

## Download & Installation

### Easy Installation (Recommended)

Download the pre-built executable for your operating system from the [latest release](https://github.com/jwburney/Scoreboard-Data-Manager/releases/tag/latest):

- **Windows**: Download `ScoreboardManager-Windows.exe`
- **macOS**: Download `ScoreboardManager-macOS`
- **Linux**: Download `ScoreboardManager-Linux`

**Important**: Make sure the `scoreboard_settings.json` file is in the same folder as the executable.

#### macOS/Linux Users
After downloading, you may need to make the file executable:
```bash
chmod +x ScoreboardManager-macOS
```

### Alternative: Run from Python

If you prefer to run from source code:

1. Install Python 3.11 or later
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python scoreBoardDataManager.py
   ```

### Build Your Own Executable

You can create a standalone executable for Linux, Windows, or macOS using PyInstaller. This allows you to distribute the application to others without requiring Python installation.

**For Linux:**
```bash
chmod +x build_linux_executable.sh
./build_linux_executable.sh
```
Executable will be created at: `./dist/ScoreboardDataManager`

**For Windows:**
```cmd
build_windows_executable.bat
```
Executable will be created at: `.\dist\ScoreboardDataManager.exe`

**Quick Reference:** See [PYINSTALLER_QUICK_GUIDE.md](PYINSTALLER_QUICK_GUIDE.md)

**Detailed Guide:** See [BUILD_LINUX_EXECUTABLE.md](BUILD_LINUX_EXECUTABLE.md)

## Quick Start Guide

### 1. Connect Your Scoreboard

1. Connect your Daktronics scoreboard to your computer via USB or serial cable
2. Launch Scoreboard Data Manager
3. Click the **Refresh** button next to the serial port dropdown
4. Select your scoreboard's port from the list
5. Click **Connect**

### 2. Choose Your Output Format

The application supports multiple output formats:

- **JSON** - Save to file or send to an API endpoint
- **OBS WebSocket** - Update OBS text sources in real-time
- **XML** - Standard XML or vMix-compatible format
- **CSV** - Spreadsheet-compatible format
- **Text Files** - Individual .txt files for each field

### 3. Configure Auto-Updates

- **Auto-Update**: Enable to automatically export data at regular intervals (0.1-60 seconds)
- **Update on Change Only**: Export only when scoreboard data changes (more efficient)

### 4. Select Data Fields

Go to the **Data Options** tab to choose which scoreboard fields to include in your export. Use **Select All** or **Deselect All** for quick setup.

## Output Format Setup

### JSON (File)
- Click **Browse** to select where to save the JSON file
- File updates automatically based on your update settings

### JSON (API)
- Enter your API endpoint URL
- Data is sent via HTTP PUT request as JSON
- Perfect for web dashboards and real-time applications

### OBS WebSocket
1. In OBS, enable WebSocket server (Tools → WebSocket Server Settings)
2. Create text sources named to match scoreboard fields (e.g., "Home_Team_Score")
3. In Scoreboard Data Manager, enter:
   - **Host**: Usually `localhost`
   - **Port**: Default is `4455`
   - **Password**: Match your OBS WebSocket password
4. Click **Connect to OBS**

**Tip**: Replace spaces with underscores in OBS text source names (e.g., "Home Team Score" becomes "Home_Team_Score")

### vMix XML
- Choose this format for vMix DataSource integration
- Click **Browse** to select save location
- In vMix, add the XML file as a DataSource to your title

### Text Files
- Creates individual .txt files for each scoreboard field
- Useful for streaming software that reads text files
- Click **Browse** to select the folder for the text files

## Supported Sports

The application supports **20 sports** with complete data field definitions. All sports are accessible through the sport dropdown, with popular sports listed first for convenience.

**Popular Sports (Listed First in Dropdown):**
1. Football
2. Basketball
3. Baseball
4. Soccer
5. Hockey/Lacrosse
6. Volleyball
7. Wrestling
8. Waterpolo

**Additional Sports (Alphabetically Organized):**
- Auto Racing
- Cricket
- Event Counter
- Judo
- Karate
- Lane Timer
- Pitch and Speed
- Rodeo
- Strike Out Count
- Taekwondo
- Tennis
- Track

**Testing Status:**
- **Fully Tested:** Football
- **Validated (Software Testing):** Basketball, Hockey/Lacrosse, Wrestling
- **Supported (Implementation Complete):** All remaining sports

Each sport provides access to team scores, game clock, period/quarter info, statistics, and sport-specific data. The sport list is dynamically generated from the Daktronics library, ensuring all available sports are always accessible.

## Demo Mode

Click **Load Demo Data** to test the application with sample football data without connecting to a physical scoreboard. Great for:
- Learning how the application works
- Testing your output format setup
- Training and demonstrations

## Troubleshooting

### No Serial Ports Detected
- Make sure your scoreboard is connected via USB/serial cable
- Click the **Refresh** button after connecting
- You may need to install USB driver software (FTDI or CH340 drivers)

### OBS Connection Failed
- Verify OBS WebSocket is enabled in OBS
- Check that host, port, and password match your OBS settings
- Make sure OBS is running when you try to connect

### Python Version Issues
If running from source, the application requires:
- Python 3.11 or later
- PySerial (for serial communication)
- obsws-python (for OBS integration)
- requests (for API uploads)

Install missing packages with:
```bash
pip install -r requirements.txt
```

### Settings Not Saving
Settings are automatically saved to `scoreboard_settings.json` in the same folder as the application. Make sure the application has write permissions to this folder.

## Use Cases

- **Live Streaming**: Export to OBS for on-screen graphics overlays
- **Broadcasting**: Feed data to production software
- **Web Dashboards**: Send real-time updates to web applications via API
- **vMix Graphics**: Use with vMix titles and DataSource
- **Data Logging**: Save game data for analysis and record-keeping
- **Multi-Platform Broadcasting**: Use multiple output formats simultaneously

## System Requirements

- **Windows**: Windows 10 or later
- **macOS**: macOS 10.13 or later
- **Linux**: Most modern distributions
- **Connection**: USB port or serial port adapter
- **Scoreboard**: Daktronics scoreboard with RTD (Real-Time Data) output capability

## Support & Documentation

- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/jwburney/Scoreboard-Data-Manager/issues)
- **Source Code**: Available on [GitHub](https://github.com/jwburney/Scoreboard-Data-Manager)

## License

This application is provided as-is for use with Daktronics scoreboard systems.

## Version Information

Executables are automatically built from the latest code. Check the [releases page](https://github.com/jwburney/Scoreboard-Data-Manager/releases/tag/latest) for the most recent build date and commit information.
