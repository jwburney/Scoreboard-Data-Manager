import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import json
import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom
import threading
from concurrent.futures import ThreadPoolExecutor
import time
from pathlib import Path
from datetime import datetime
import requests

# Import serial port tools
try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("Warning: pyserial not found. Install with: pip install pyserial")

# Import OBS WebSocket
try:
    import obsws_python as obs
    OBS_AVAILABLE = True
    print("OBS WebSocket library loaded successfully")
except ImportError as e:
    OBS_AVAILABLE = False
    print(f"OBS WebSocket not available: {e}")
    print("Install with: pip install obsws-python")

# Import Daktronics
try:
    from daktronics import DakSerial, Daktronics, dakSports
    DAK_AVAILABLE = True
except ImportError:
    DAK_AVAILABLE = False
    dakSports = {}
    print("Warning: daktronics module not found.")


class ScoreboardDataManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Scoreboard Data Manager")
        self.root.geometry("1000x700")
        
        # Settings file path
        self.settings_file = Path("scoreboard_settings.json")
        
        # Threading for non-blocking API sends
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.data_lock = threading.Lock()
        
        # Data variables
        self.current_data = {}
        self.previous_data = {}
        self.auto_save_enabled = tk.BooleanVar(value=False)
        self.auto_save_interval = tk.DoubleVar(value=1.0)
        self.update_on_change = tk.BooleanVar(value=False)
        self.selected_format = tk.StringVar(value="JSON")
        self.selected_sport = tk.StringVar(value="football")
        self.selected_port = tk.StringVar(value="")
        self.available_ports = []
        self.save_path = tk.StringVar(value="")
        self.api_url = tk.StringVar(value="")
        self.obs_host = tk.StringVar(value="localhost")
        self.obs_port = tk.StringVar(value="4455")
        self.obs_password = tk.StringVar(value="")
        self.is_running = False
        self.dak = None
        self.dak_thread = None
        self.obs_client = None
        self.selected_fields = []  # Fields to include in output
        self.all_available_fields = []  # All fields for current sport
        
        # Configure root grid
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        
        # Main container with notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Create pages
        self.main_page = ttk.Frame(self.notebook)
        self.fields_page = ttk.Frame(self.notebook)
        
        self.notebook.add(self.main_page, text="Main")
        self.notebook.add(self.fields_page, text="Data Options")
        
        # Setup main page
        main_frame = ttk.Frame(self.main_page)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Left side - Controls
        left_frame = ttk.Frame(main_frame, padding="10")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Right side - Data display
        right_frame = ttk.Frame(main_frame, padding="10")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Setup GUI
        self.setup_connection_controls(left_frame)
        self.setup_save_controls(left_frame)
        self.setup_action_buttons(left_frame)
        self.setup_data_display(right_frame)
        self.setup_field_filter_page()
        
        # Status bar (must be created before load_settings)
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Load saved settings AFTER GUI is created
        self.load_settings()
        
        # Initial port scan
        self.scan_ports()
        
        # Populate fields based on selected sport
        self.update_available_fields()
        
        # Save settings on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_connection_controls(self, parent):
        connection_frame = ttk.LabelFrame(parent, text="Scoreboard Connection", padding="10")
        connection_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Sport selection
        ttk.Label(connection_frame, text="Sport:").grid(row=0, column=0, sticky=tk.W, pady=2)
        sport_combo = ttk.Combobox(connection_frame, textvariable=self.selected_sport,
                                  values=["football", "hockey/lacrosse", "basketball", "baseball",
                                         "soccer", "volleyball", "waterpolo", "wrestling"],
                                  state="readonly", width=23)
        sport_combo.grid(row=0, column=1, sticky=tk.W, pady=2)
        sport_combo.bind('<<ComboboxSelected>>', self.on_sport_changed)
        
        # Serial port selection
        ttk.Label(connection_frame, text="Serial Port:").grid(row=1, column=0, sticky=tk.W, pady=2)
        
        port_frame = ttk.Frame(connection_frame)
        port_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        self.port_combo = ttk.Combobox(port_frame, textvariable=self.selected_port, 
                                       width=25, state="readonly")
        self.port_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.port_combo.bind('<<ComboboxSelected>>', self.on_port_selected)
        
        self.refresh_btn = ttk.Button(port_frame, text="↻", command=self.scan_ports, width=3)
        self.refresh_btn.pack(side=tk.LEFT, padx=2)
        
        # Connection status
        ttk.Label(connection_frame, text="Status:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.connection_status = ttk.Label(connection_frame, text="Disconnected", foreground="red")
        self.connection_status.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Connect button
        self.connect_btn = ttk.Button(connection_frame, text="Connect", command=self.toggle_connection)
        self.connect_btn.grid(row=3, column=0, columnspan=2, pady=5)
        self.connect_btn.config(state='disabled')
        
        # Status messages
        if not SERIAL_AVAILABLE:
            ttk.Label(connection_frame, text="PySerial not installed", 
                     foreground="orange", wraplength=250).grid(row=4, column=0, columnspan=2)
            self.connect_btn.config(state='disabled')
        elif not DAK_AVAILABLE:
            ttk.Label(connection_frame, text="Daktronics module not available", 
                     foreground="orange", wraplength=250).grid(row=4, column=0, columnspan=2)
        
    def setup_save_controls(self, parent):
        save_frame = ttk.LabelFrame(parent, text="Save Settings", padding="10")
        save_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Format selection
        ttk.Label(save_frame, text="Output Format:").grid(row=0, column=0, sticky=tk.W, pady=2)
        format_combo = ttk.Combobox(save_frame, textvariable=self.selected_format, 
                                    values=["JSON", "JSON (API)", "OBS WebSocket", "XML", "CSV", "Text Files", "vMix XML"], 
                                    state="readonly", width=15)
        format_combo.grid(row=0, column=1, sticky=tk.W, pady=2)
        format_combo.bind('<<ComboboxSelected>>', self.on_format_changed)
        
        # Save path
        ttk.Label(save_frame, text="Save Location:").grid(row=1, column=0, sticky=tk.W, pady=2)
        path_frame = ttk.Frame(save_frame)
        path_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        self.path_entry = ttk.Entry(path_frame, textvariable=self.save_path, width=20)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.browse_btn = ttk.Button(path_frame, text="Browse", command=self.browse_save_location, width=8)
        self.browse_btn.pack(side=tk.LEFT, padx=2)
        
        # API URL (shown when JSON (API) is selected)
        self.api_frame = ttk.Frame(save_frame)
        self.api_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.api_frame.grid_remove()
        
        ttk.Label(self.api_frame, text="API URL:").pack(side=tk.LEFT, padx=(0, 5))
        api_entry = ttk.Entry(self.api_frame, textvariable=self.api_url)
        api_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # OBS WebSocket settings (shown when OBS WebSocket is selected)
        self.obs_frame = ttk.LabelFrame(save_frame, text="OBS WebSocket Settings", padding="5")
        self.obs_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.obs_frame.grid_remove()
        
        obs_host_frame = ttk.Frame(self.obs_frame)
        obs_host_frame.pack(fill=tk.X, pady=2)
        ttk.Label(obs_host_frame, text="Host:", width=10).pack(side=tk.LEFT)
        ttk.Entry(obs_host_frame, textvariable=self.obs_host, width=20).pack(side=tk.LEFT, padx=5)
        
        obs_port_frame = ttk.Frame(self.obs_frame)
        obs_port_frame.pack(fill=tk.X, pady=2)
        ttk.Label(obs_port_frame, text="Port:", width=10).pack(side=tk.LEFT)
        ttk.Entry(obs_port_frame, textvariable=self.obs_port, width=20).pack(side=tk.LEFT, padx=5)
        
        obs_pass_frame = ttk.Frame(self.obs_frame)
        obs_pass_frame.pack(fill=tk.X, pady=2)
        ttk.Label(obs_pass_frame, text="Password:", width=10).pack(side=tk.LEFT)
        ttk.Entry(obs_pass_frame, textvariable=self.obs_password, width=20, show="*").pack(side=tk.LEFT, padx=5)
        
        if not OBS_AVAILABLE:
            ttk.Label(self.obs_frame, text="Install obsws-python for OBS support", 
                     foreground="orange", font=('TkDefaultFont', 8)).pack(pady=2)
        
        # Auto-save options
        ttk.Separator(save_frame, orient=tk.HORIZONTAL).grid(row=3, column=0, columnspan=2, 
                                                             sticky=(tk.W, tk.E), pady=10)
        
        auto_save_check = ttk.Checkbutton(save_frame, text="Enable Auto-Update", 
                                         variable=self.auto_save_enabled,
                                         command=self.toggle_auto_save)
        auto_save_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        interval_frame = ttk.Frame(save_frame)
        interval_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        ttk.Label(interval_frame, text="Update interval:").pack(side=tk.LEFT)
        interval_spin = ttk.Spinbox(interval_frame, from_=0.1, to=60, increment=0.1,
                                   textvariable=self.auto_save_interval, width=8, format="%.1f")
        interval_spin.pack(side=tk.LEFT, padx=5)
        ttk.Label(interval_frame, text="seconds").pack(side=tk.LEFT)
        
        # Update on change option
        change_check = ttk.Checkbutton(save_frame, text="Update on Change Only", 
                                      variable=self.update_on_change,
                                      command=self.toggle_update_on_change)
        change_check.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        ttk.Label(save_frame, text="(Sends data only when field values change)", 
                 font=('TkDefaultFont', 8), foreground='gray').grid(row=7, column=0, columnspan=2, sticky=tk.W, padx=20)
        
    def setup_action_buttons(self, parent):
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
        
        self.save_now_btn = ttk.Button(button_frame, text="Send Data", 
                                       command=self.save_data_now, state='disabled')
        self.save_now_btn.pack(fill=tk.X, pady=2)
        
        ttk.Button(button_frame, text="Load Demo Data", 
                  command=self.load_demo_data).pack(fill=tk.X, pady=2)
        
        ttk.Button(button_frame, text="Clear Preview", 
                  command=self.clear_preview).pack(fill=tk.X, pady=2)
        
    def setup_data_display(self, parent):
        # Current data display
        data_frame = ttk.LabelFrame(parent, text="Current Scoreboard Data", padding="10")
        data_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        data_frame.rowconfigure(0, weight=1)
        data_frame.columnconfigure(0, weight=1)
        
        self.data_text = scrolledtext.ScrolledText(data_frame, height=12, width=50, 
                                                   wrap=tk.WORD, state='disabled')
        self.data_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Preview display
        preview_frame = ttk.LabelFrame(parent, text="Output Preview", padding="10")
        preview_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        preview_frame.rowconfigure(0, weight=1)
        preview_frame.columnconfigure(0, weight=1)
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=15, width=50, 
                                                     wrap=tk.WORD, state='disabled')
        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        parent.rowconfigure(0, weight=2)
        parent.rowconfigure(1, weight=3)
    
    def setup_field_filter_page(self):
        """Setup the field filtering page"""
        filter_frame = ttk.Frame(self.fields_page, padding="10")
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.fields_page.rowconfigure(0, weight=1)
        self.fields_page.columnconfigure(0, weight=1)
        filter_frame.rowconfigure(2, weight=1)
        filter_frame.columnconfigure(0, weight=1)
        
        # Instructions
        ttk.Label(filter_frame, text="Select fields to include in output:", 
                 font=('TkDefaultFont', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Button frame
        button_frame = ttk.Frame(filter_frame)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(button_frame, text="Select All", 
                  command=self.select_all_fields).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Deselect All", 
                  command=self.deselect_all_fields).pack(side=tk.LEFT, padx=5)
        ttk.Label(button_frame, text="(Changes apply immediately)", 
                 foreground="gray").pack(side=tk.LEFT, padx=10)
        
        # Scrollable field list
        scroll_container = ttk.Frame(filter_frame)
        scroll_container.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        canvas = tk.Canvas(scroll_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        self.fields_list_frame = ttk.Frame(canvas)
        
        self.fields_list_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.fields_list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.field_checkboxes = {}
    
    def on_sport_changed(self, event=None):
        """Called when sport selection changes"""
        self.update_available_fields()
    
    def update_available_fields(self):
        """Update the list of available fields based on selected sport"""
        sport = self.selected_sport.get()
        
        if DAK_AVAILABLE and sport in dakSports:
            self.all_available_fields = [key for key in dakSports[sport].keys() if key != 'dakSize']
        else:
            self.all_available_fields = []
        
        # If no fields selected yet, select all by default
        if not self.selected_fields:
            self.selected_fields = list(self.all_available_fields)
        else:
            # Keep only fields that exist in the new sport
            self.selected_fields = [f for f in self.selected_fields if f in self.all_available_fields]
            # If none left, select all
            if not self.selected_fields:
                self.selected_fields = list(self.all_available_fields)
        
        self.populate_field_checkboxes()
    
    def populate_field_checkboxes(self):
        """Create checkboxes for all available fields"""
        # Clear existing
        for widget in self.fields_list_frame.winfo_children():
            widget.destroy()
        self.field_checkboxes.clear()
        
        if not self.all_available_fields:
            ttk.Label(self.fields_list_frame, text="No fields available for selected sport",
                     foreground="gray").pack(pady=20)
            return
        
        # Create checkboxes
        for field in sorted(self.all_available_fields):
            var = tk.BooleanVar(value=field in self.selected_fields)
            var.trace_add('write', lambda *args, f=field, v=var: self.on_field_toggled(f, v))
            cb = ttk.Checkbutton(self.fields_list_frame, text=field, variable=var)
            cb.pack(anchor=tk.W, pady=2, padx=10)
            self.field_checkboxes[field] = var
    
    def on_field_toggled(self, field, var):
        """Called when a field checkbox is toggled"""
        if var.get():
            if field not in self.selected_fields:
                self.selected_fields.append(field)
        else:
            if field in self.selected_fields:
                self.selected_fields.remove(field)
        
        # Save settings
        self.save_settings()
    
    def select_all_fields(self):
        """Select all field checkboxes"""
        for field, var in self.field_checkboxes.items():
            var.set(True)
    
    def deselect_all_fields(self):
        """Deselect all field checkboxes"""
        for field, var in self.field_checkboxes.items():
            var.set(False)
    
    def on_format_changed(self, event=None):
        """Called when output format changes"""
        format_type = self.selected_format.get()
        
        # Hide all special frames first
        self.api_frame.grid_remove()
        self.obs_frame.grid_remove()
        
        # Show/hide appropriate fields based on format
        if format_type == "JSON (API)":
            self.api_frame.grid()
            self.path_entry.config(state='disabled')
            self.browse_btn.config(state='disabled')
        elif format_type == "OBS WebSocket":
            self.obs_frame.grid()
            self.path_entry.config(state='disabled')
            self.browse_btn.config(state='disabled')
        else:
            self.path_entry.config(state='normal')
            self.browse_btn.config(state='normal')
        
        self.update_preview()
    
    def scan_ports(self):
        """Scan for available serial ports"""
        if not SERIAL_AVAILABLE:
            return
            
        self.available_ports = []
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            # Create descriptive port name
            if port.description and port.description != port.device:
                port_name = f"{port.device} - {port.description}"
            else:
                port_name = port.device
            self.available_ports.append((port.device, port_name))
        
        # Update combobox
        if self.available_ports:
            port_names = [name for _, name in self.available_ports]
            self.port_combo['values'] = port_names
            
            # Don't auto-select, user must choose
            self.port_combo.set("-- Select a serial port --")
            self.update_status(f"Found {len(self.available_ports)} serial port(s). Please select one.")
            self.connect_btn.config(state='disabled')
        else:
            self.port_combo['values'] = ["No ports found"]
            self.port_combo.set("No ports found")
            self.update_status("No serial ports detected. Click refresh after connecting device.")
            self.connect_btn.config(state='disabled')
    
    def on_port_selected(self, event=None):
        """Called when user selects a port from dropdown"""
        selected_index = self.port_combo.current()
        if selected_index >= 0 and selected_index < len(self.available_ports):
            device, name = self.available_ports[selected_index]
            self.connect_btn.config(state='normal')
            self.update_status(f"Selected: {device}")
        else:
            self.connect_btn.config(state='disabled')
    
    def get_selected_port_device(self):
        """Get the actual device path from the selected port"""
        selected_index = self.port_combo.current()
        if selected_index >= 0 and selected_index < len(self.available_ports):
            return self.available_ports[selected_index][0]
        return None
    
    def toggle_connection(self):
        if not self.is_running:
            self.start_connection()
        else:
            self.stop_connection()
            
    def start_connection(self):
        try:
            # Get the selected port device
            port_device = self.get_selected_port_device()
            if not port_device:
                messagebox.showerror("Connection Error", "Please select a valid serial port")
                return
            
            if not DAK_AVAILABLE:
                messagebox.showerror("Connection Error", "Daktronics module not available")
                return
            
            # Get selected sport
            sport = self.selected_sport.get()
            
            # Initialize Daktronics exactly like your example
            try:
                from daktronics import DakSerial, Daktronics
                # Pass port string directly to DakSerial
                dak_serial = DakSerial(port_device)
                # Create Daktronics object with sport string
                self.dak = Daktronics(sport, dak_serial)
                
            except Exception as e:
                messagebox.showerror("Connection Error", f"Could not initialize Daktronics: {str(e)}")
                return
            
            # Start listening thread
            self.is_running = True
            self.previous_data = {}
            self.dak_thread = threading.Thread(target=self.listen_for_data, daemon=True)
            self.dak_thread.start()
            
            self.connection_status.config(text="Listening", foreground="green")
            self.connect_btn.config(text="Stop Listening")
            self.port_combo.config(state='disabled')
            self.refresh_btn.config(state='disabled')
            self.save_now_btn.config(state='normal')
            
            self.update_status(f"Listening for {sport} data on {port_device}")
            
        except Exception as e:
            self.update_status(f"Connection error: {str(e)}")
            messagebox.showerror("Connection Error", str(e))
    
    def stop_connection(self):
        self.is_running = False
        
        # Disconnect OBS if connected
        if self.obs_client:
            try:
                self.obs_client.disconnect()
            except:
                pass
            self.obs_client = None
        
        self.connection_status.config(text="Disconnected", foreground="red")
        self.connect_btn.config(text="Connect")
        self.port_combo.config(state='readonly')
        self.refresh_btn.config(state='normal')
        self.update_status("Stopped listening")
            
    def listen_for_data(self):
        """Continuously call dak.update() and extract data"""
        last_save_time = time.time()
        
        while self.is_running:
            try:
                # Call dak.update() to read from serial port
                self.dak.update()
                
                # Extract data from dak object using dictionary-style access
                # Use lock for thread-safe access
                with self.data_lock:
                    self.current_data = {}
                    
                    # Only include selected fields
                    fields_to_use = self.selected_fields if self.selected_fields else list(self.dak.sport.keys())
                    
                    for key in fields_to_use:
                        if key != 'dakSize' and key in self.dak.sport:
                            # Access data using dak['fieldname']
                            value = self.dak[key]
                            if value and value.strip():
                                self.current_data[key] = value.strip()
                
                # Update display if we have data
                if self.current_data:
                    self.update_data_display()
                    self.update_preview()
                    
                    # Handle auto-update or update-on-change
                    if self.update_on_change.get():
                        if self.has_data_changed():
                            self.save_data()
                            self.previous_data = dict(self.current_data)
                    elif self.auto_save_enabled.get():
                        current_time = time.time()
                        if current_time - last_save_time >= self.auto_save_interval.get():
                            self.save_data()
                            last_save_time = current_time
                
                # Small delay to prevent overwhelming the CPU
                time.sleep(0.05)
            except Exception as e:
                self.update_status(f"Read error: {str(e)}")
                print(f"Error details: {e}")
                time.sleep(1)
    
    def has_data_changed(self):
        """Check if any field value has changed from previous data"""
        # If no previous data, consider it changed
        if not self.previous_data:
            return True
        
        # Check if any field is different
        for key, value in self.current_data.items():
            if key not in self.previous_data or self.previous_data[key] != value:
                return True
        
        # Check if any field was removed
        for key in self.previous_data:
            if key not in self.current_data:
                return True
        
        return False
    
    def load_demo_data(self):
        """Load demo data for testing without hardware"""
        self.current_data = {
            'Home Team Name': 'BULLDOGS',
            'Guest Team Name': 'WILDCATS',
            'Home Team Score': '21',
            'Guest Team Score': '17',
            'Main Clock Time [mm:ss.t]': '8:45.2',
            'Quarter Text': '3RD',
            'Quarter': '3',
            'Down': '2',
            'To Go': '7',
            'Ball On': '35',
            'Home Time Outs Left - Total': '2',
            'Guest Time Outs Left - Total': '3',
        }
        self.update_data_display()
        self.update_preview()
        self.save_now_btn.config(state='normal')
        self.update_status("Demo data loaded")
        
    def update_data_display(self):
        self.data_text.config(state='normal')
        self.data_text.delete(1.0, tk.END)
        
        for key, value in sorted(self.current_data.items()):
            self.data_text.insert(tk.END, f"{key}: {value}\n")
            
        self.data_text.config(state='disabled')
        
    def update_preview(self):
        if not self.current_data:
            return
            
        format_type = self.selected_format.get()
        preview_content = ""
        
        try:
            if format_type == "JSON" or format_type == "JSON (API)":
                preview_content = json.dumps(self.current_data, indent=2)
            elif format_type == "XML":
                preview_content = self.format_as_xml(self.current_data)
            elif format_type == "vMix XML":
                preview_content = self.format_as_vmix_xml(self.current_data)
            elif format_type == "CSV":
                preview_content = self.format_as_csv_preview(self.current_data)
            elif format_type == "Text Files":
                preview_content = self.format_as_text_preview(self.current_data)
            elif format_type == "OBS WebSocket":
                preview_content = "OBS WebSocket Mode\n\n"
                preview_content += "Data will be sent to OBS text sources:\n\n"
                for key in list(self.current_data.keys())[:10]:
                    safe_name = key.replace(' ', '_').replace('[', '').replace(']', '').replace('/', '_')
                    preview_content += f"{safe_name}\n"
                if len(self.current_data) > 10:
                    preview_content += f"... and {len(self.current_data) - 10} more fields"
                
            self.preview_text.config(state='normal')
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, preview_content)
            self.preview_text.config(state='disabled')
            
        except Exception as e:
            self.update_status(f"Preview error: {str(e)}")
            
    def format_as_xml(self, data):
        root = ET.Element("ScoreboardData")
        root.set("timestamp", datetime.now().isoformat())
        
        for key, value in data.items():
            field = ET.SubElement(root, "Field")
            field.set("name", key)
            field.text = str(value)
            
        xml_str = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent="  ")
        
    def format_as_vmix_xml(self, data):
        """Format for vMix DataSource"""
        root = ET.Element("vmix")
        
        for key, value in data.items():
            # Create vMix-friendly field names
            safe_key = key.replace(' ', '_').replace('[', '').replace(']', '').replace('/', '_')
            field = ET.SubElement(root, safe_key)
            field.text = str(value)
            
        xml_str = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent="  ")
        
    def format_as_csv_preview(self, data):
        preview = "Field,Value\n"
        for key, value in data.items():
            preview += f'"{key}","{value}"\n'
        return preview
        
    def format_as_text_preview(self, data):
        preview = "Each field will be saved as a separate .txt file:\n\n"
        for key in list(data.keys())[:5]:
            safe_name = key.replace(' ', '_').replace('[', '').replace(']', '')
            preview += f"{safe_name}.txt\n"
        if len(data) > 5:
            preview += f"... and {len(data) - 5} more files"
        return preview
        
    def browse_save_location(self):
        format_type = self.selected_format.get()
        
        if format_type == "Text Files":
            directory = filedialog.askdirectory(title="Select folder for text files")
            if directory:
                self.save_path.set(directory)
        else:
            extensions = {
                "JSON": [("JSON files", "*.json")],
                "XML": [("XML files", "*.xml")],
                "vMix XML": [("XML files", "*.xml")],
                "CSV": [("CSV files", "*.csv")]
            }
            
            filename = filedialog.asksaveasfilename(
                title="Select save location",
                filetypes=extensions.get(format_type, [("All files", "*.*")]),
                defaultextension=extensions.get(format_type, [("", "")])[0][1]
            )
            if filename:
                self.save_path.set(filename)
                
    def save_data_now(self):
        self.save_data()
        
    def save_data(self):
        if not self.current_data:
            self.update_status("No data to save")
            return
        
        format_type = self.selected_format.get()
        
        # Handle API upload for JSON (API) - SUBMIT TO THREAD (non-blocking)
        if format_type == "JSON (API)":
            if not self.api_url.get():
                self.update_status("Please enter an API URL")
                return
            # Submit to thread pool instead of blocking
            self.executor.submit(self.upload_to_api_async)
            return
        
        # Handle OBS WebSocket
        if format_type == "OBS WebSocket":
            return self.send_to_obs()
        
        # For file-based formats, check save path
        if not self.save_path.get():
            self.update_status("Please select a save location")
            return
            
        try:
            if format_type == "JSON":
                with open(self.save_path.get(), 'w') as f:
                    json.dump(self.current_data, f, indent=2)
                    
            elif format_type == "XML":
                xml_content = self.format_as_xml(self.current_data)
                with open(self.save_path.get(), 'w') as f:
                    f.write(xml_content)
                    
            elif format_type == "vMix XML":
                xml_content = self.format_as_vmix_xml(self.current_data)
                with open(self.save_path.get(), 'w') as f:
                    f.write(xml_content)
                    
            elif format_type == "CSV":
                with open(self.save_path.get(), 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Field', 'Value'])
                    for key, value in self.current_data.items():
                        writer.writerow([key, value])
                        
            elif format_type == "Text Files":
                save_dir = Path(self.save_path.get())
                save_dir.mkdir(exist_ok=True)
                for key, value in self.current_data.items():
                    safe_name = key.replace(' ', '_').replace('[', '').replace(']', '').replace('/', '_')
                    file_path = save_dir / f"{safe_name}.txt"
                    with open(file_path, 'w') as f:
                        f.write(str(value))
                        
            self.update_status(f"Data saved successfully at {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.update_status(f"Save error: {str(e)}")
    
    def upload_to_api_async(self):
        """
        Upload JSON data to API endpoint (runs in background thread).
        
        This method is thread-safe:
        - Acquires lock before accessing current_data
        - Makes a copy of data to avoid conflicts with main thread
        - Releases lock immediately
        - Performs network operation without blocking main thread
        """
        try:
            # Thread-safe: Lock before accessing current_data
            with self.data_lock:
                # Make a copy to avoid conflicts if main thread modifies data
                data_to_send = dict(self.current_data)
            
            # Network operation happens WITHOUT lock (fast)
            response = requests.put(
                self.api_url.get(),
                json=data_to_send,
                timeout=5
            )
            
            if response.status_code in [200, 201, 204]:
                self.update_status(f"API upload successful at {datetime.now().strftime('%H:%M:%S')}")
                return True
            else:
                self.update_status(f"API error: {response.status_code} - {response.text[:50]}")
                return False
                
        except requests.exceptions.Timeout:
            self.update_status("API upload timeout")
            return False
        except requests.exceptions.RequestException as e:
            self.update_status(f"API upload error: {str(e)}")
            return False
    
    def upload_to_api(self):
        """
        DEPRECATED: Use upload_to_api_async() instead.
        Kept for backward compatibility with manual "Send Data" button.
        """
        return self.upload_to_api_async()
    
    def send_to_obs(self):
        """Send data to OBS via WebSocket"""
        if not OBS_AVAILABLE:
            self.update_status("OBS WebSocket library not installed")
            messagebox.showerror("OBS Error", "Please install obsws-python: pip install obsws-python")
            return False
        
        try:
            # Connect to OBS if not already connected
            if not self.obs_client:
                try:
                    port = int(self.obs_port.get())
                    password = self.obs_password.get() if self.obs_password.get() else None
                    self.obs_client = obs.ReqClient(host=self.obs_host.get(), port=port, password=password)
                    self.update_status("Connected to OBS WebSocket")
                except Exception as e:
                    self.update_status(f"OBS connection error: {str(e)}")
                    messagebox.showerror("OBS Connection Error", f"Could not connect to OBS:\n{str(e)}")
                    return False
            
            # Send each field as a text source update
            for field_name, field_value in self.current_data.items():
                try:
                    # Create a safe source name from field name
                    source_name = field_name.replace(' ', '_').replace('[', '').replace(']', '').replace('/', '_')
                    
                    # Try to update the text source
                    self.obs_client.set_input_settings(
                        source_name,
                        {"text": str(field_value)},
                        overlay=True
                    )
                except Exception as e:
                    # Source might not exist, continue with others
                    pass
            
            self.update_status(f"Data sent to OBS at {datetime.now().strftime('%H:%M:%S')}")
            return True
            
        except Exception as e:
            self.update_status(f"OBS send error: {str(e)}")
            return False
            
    def toggle_auto_save(self):
        if self.auto_save_enabled.get():
            # Disable update on change if auto-update is enabled
            if self.update_on_change.get():
                self.update_on_change.set(False)
            
            format_type = self.selected_format.get()
            if format_type == "JSON (API)":
                if not self.api_url.get():
                    result = messagebox.askyesno("API URL Required", 
                                               "No API URL configured. Would you like to enter one now?")
                    if not result:
                        self.auto_save_enabled.set(False)
                        return
            elif format_type == "OBS WebSocket":
                if not OBS_AVAILABLE:
                    messagebox.showerror("OBS Not Available", 
                                       "Please install obsws-python: pip install obsws-python")
                    self.auto_save_enabled.set(False)
                    return
            elif not self.save_path.get():
                self.browse_save_location()
                if not self.save_path.get():
                    self.auto_save_enabled.set(False)
    
    def toggle_update_on_change(self):
        if self.update_on_change.get():
            # Disable auto-update if update on change is enabled
            if self.auto_save_enabled.get():
                self.auto_save_enabled.set(False)
            
            # Reset previous data so first update will trigger
            self.previous_data = {}
            
            format_type = self.selected_format.get()
            if format_type == "JSON (API)":
                if not self.api_url.get():
                    result = messagebox.askyesno("API URL Required", 
                                               "No API URL configured. Would you like to enter one now?")
                    if not result:
                        self.update_on_change.set(False)
                        return
            elif format_type == "OBS WebSocket":
                if not OBS_AVAILABLE:
                    messagebox.showerror("OBS Not Available", 
                                       "Please install obsws-python: pip install obsws-python")
                    self.update_on_change.set(False)
                    return
            elif not self.save_path.get():
                self.browse_save_location()
                if not self.save_path.get():
                    self.update_on_change.set(False)
        
    def clear_preview(self):
        self.preview_text.config(state='normal')
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.config(state='disabled')
        
    def update_status(self, message):
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    def load_settings(self):
        """Load saved settings from file"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                
                # Load settings into variables
                self.selected_format.set(settings.get('output_format', 'JSON'))
                self.selected_sport.set(settings.get('sport', 'football'))
                self.save_path.set(settings.get('save_path', ''))
                self.api_url.set(settings.get('api_url', ''))
                self.obs_host.set(settings.get('obs_host', 'localhost'))
                self.obs_port.set(settings.get('obs_port', '4455'))
                self.auto_save_interval.set(settings.get('auto_save_interval', 1.0))
                self.selected_fields = settings.get('selected_fields', [])
                
                self.update_status("Settings loaded")
            except Exception as e:
                self.update_status(f"Could not load settings: {str(e)}")
    
    def save_settings(self):
        """Save current settings to file"""
        try:
            settings = {
                'output_format': self.selected_format.get(),
                'sport': self.selected_sport.get(),
                'save_path': self.save_path.get(),
                'api_url': self.api_url.get(),
                'obs_host': self.obs_host.get(),
                'obs_port': self.obs_port.get(),
                'auto_save_interval': self.auto_save_interval.get(),
                'selected_fields': self.selected_fields
            }
            
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
                
        except Exception as e:
            print(f"Could not save settings: {str(e)}")
    
    def on_closing(self):
        """Called when window is closing"""
        # Stop connection if running
        if self.is_running:
            self.stop_connection()
        
        # Save settings
        self.save_settings()
        
        # Close window
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ScoreboardDataManager(root)
    root.mainloop()