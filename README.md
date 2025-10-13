# Scoreboard Data Manager

A Python application for capturing live scoreboard data from Daktronics scoreboards and exporting it in multiple formats for use in streaming, broadcasting, and data visualization applications.

## Features

- **Real-time Data Capture**: Connects to Daktronics scoreboards via serial port to capture live game data
- **Flexible Output Formats**:
  - JSON (File or API upload)
  - XML (Standard or vMix)
  - CSV
  - Text Files (individual files per field)
  - OBS WebSocket (direct integration)
- **Customizable Field Selection**: Choose which data fields to include in your output
- **Auto-Update Options**:
  - Time-based updates at configurable intervals
  - Change-based updates (only when data changes)
- **Live Preview**: View current scoreboard data and formatted output in real-time

## Easy Setup (For Non-Technical Users)

If you want to create a standalone executable file (.exe) that doesn't require Python to be installed:

1. **Install PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

2. **Install all dependencies**:
   ```bash
   pip install requests pyserial obsws-python
   ```

3. **Create the executable**:
   ```bash
   pyinstaller --onefile --windowed --name "Scoreboard Data Manager" --add-data "daktronics:daktronics" "scoreboard_gui official version.py"
   ```

   **Note**: On Windows, use semicolon instead of colon in the `--add-data` parameter:
   ```bash
   pyinstaller --onefile --windowed --name "Scoreboard Data Manager" --add-data "daktronics;daktronics" "scoreboard_gui official version.py"
   ```

4. **Find your executable**:
   - The `.exe` file will be created in the `dist` folder
   - You can now copy this file to any Windows computer and run it without installing Python

5. **Optional - Create an icon**:
   - If you have an icon file (.ico), add `--icon=your_icon.ico` to the pyinstaller command

## Requirements

### Required Dependencies
```bash
pip install tkinter  # Usually included with Python
pip install requests
```

### Optional Dependencies
```bash
pip install pyserial              # For serial port communication
pip install obsws-python          # For OBS WebSocket support
```

### Daktronics Module
The application requires the `daktronics` module (included in the `daktronics/` directory) for scoreboard communication.

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install requests
   ```
3. Install optional dependencies based on your needs:
   ```bash
   pip install pyserial obsws-python
   ```
4. Ensure the `daktronics` module is in the same directory as the main application

## Usage

### Starting the Application
```bash
python "scoreboard_gui official version.py"
```

### Connecting to a Scoreboard

1. **Select Serial Port**:
   - Click the refresh button to scan for available ports
   - Select the port connected to your Daktronics scoreboard
2. **Connect**: Click the "Connect" button to start receiving data

### Configuring Output

#### Main Tab
1. **Output Format**: Choose your desired export format
2. **Save Location**:
   - For file-based formats: Browse to select a save location
   - For JSON (API): Enter your API endpoint URL
   - For OBS WebSocket: Configure connection settings
3. **Auto-Update Settings**:
   - Enable Auto-Update for time-based exports
   - Set update interval (0.1-60 seconds)
   - Or enable "Update on Change Only" to export only when data changes

#### Data Options Tab
- Select which scoreboard fields to include in your output
- Use "Select All" or "Deselect All" for quick configuration
- Changes apply immediately

### Output Formats Explained

#### JSON
Standard JSON format for easy integration with web applications and APIs.

#### JSON (API)
Sends JSON data via HTTP PUT request to a specified API endpoint. Perfect for real-time web dashboards.

#### OBS WebSocket
Directly updates OBS text sources with scoreboard data. Text sources should be named to match field names (spaces replaced with underscores).

**OBS Setup**:
1. Enable WebSocket server in OBS (Tools → WebSocket Server Settings)
2. Create text sources with names matching scoreboard fields (e.g., `Home_Team_Score`)
3. Configure host, port, and password in the application

#### XML
Standard XML format with timestamp.

#### vMix XML
Formatted specifically for vMix DataSource functionality. Fields use underscore-separated names compatible with vMix titles.

#### CSV
Comma-separated values with Field/Value columns.

#### Text Files
Creates individual .txt files for each field. Useful for applications that read text files directly (e.g., some streaming software).

## Demo Mode

Click "Load Demo Data" to populate the application with sample football data for testing output formats without connecting to physical hardware.

## Settings Persistence

The application automatically saves your settings to `scoreboard_settings.json`, including:
- Output format
- Save paths
- API URLs
- OBS connection settings
- Selected fields
- Auto-update interval

## Supported Scoreboard Fields

The application captures various scoreboard data fields, including:
- Team Names and Scores
- Game Clock and Play Clock
- Quarter/Period
- Down, Distance, and Ball Position
- Time Outs Remaining
- Team Statistics (Rushing Yards, Passing Yards, etc.)
- Possession Indicators
- Ad Panel/Caption Data

## Troubleshooting

### "PySerial not installed" Warning
Install pyserial to enable serial port communication:
```bash
pip install pyserial
```

### "Daktronics module not available" Warning
Ensure the `daktronics` folder is in the same directory as the application.

### "No serial ports detected"
- Verify your Daktronics scoreboard is connected via USB or serial cable
- Click the refresh button after connecting the device
- Check device drivers (may need FTDI or CH340 drivers depending on adapter)

### OBS WebSocket Connection Failed
- Verify OBS WebSocket server is enabled
- Check host and port settings (default: localhost:4455)
- Ensure password matches OBS WebSocket password
- Install obsws-python: `pip install obsws-python`

### API Upload Errors
- Verify the API endpoint URL is correct
- Ensure your API accepts PUT requests with JSON body
- Check network connectivity
- Review API server logs for error details

## Use Cases

- **Live Streaming**: Export scoreboard data to OBS for on-screen graphics
- **Broadcasting**: Feed data to production software via XML or API
- **vMix Integration**: Use vMix XML format for title overlays
- **Web Dashboards**: Send JSON to web applications for real-time updates
- **Data Logging**: Save CSV or JSON files for post-game analysis
- **Statistics Tracking**: Export data to databases or spreadsheets

## Technical Details

- **Framework**: Python Tkinter GUI
- **Serial Communication**: PySerial library
- **Data Update Rate**: Configurable from 0.1 to 60 seconds
- **Supported Baud Rates**: Determined by Daktronics module
- **Threading**: Non-blocking serial communication with background threads

## License

This application is provided as-is for use with Daktronics scoreboard systems.

## Credits

Built using the Daktronics serial communication protocol and libraries.

## Version Information

Current Version: Official Release

## Support

For issues related to:
- **Serial Communication**: Check Daktronics hardware documentation
- **OBS Integration**: Refer to OBS WebSocket protocol documentation
- **vMix Integration**: Consult vMix DataSource documentation
