#!/usr/bin/env python3
"""
HPM Inventory Tracker - Desktop Application
A standalone desktop version of the HPM Inventory system
"""

import os
import sys
import threading
import webbrowser
import time
import socket
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

class HPMInventoryApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("HPM Inventory Tracker")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Set up data directory
        self.setup_data_directory()
        
        # Variables
        self.server_thread = None
        self.server_running = False
        self.port = self.find_free_port()
        
        # Setup GUI
        self.setup_gui()
        
        # Start server on app launch
        self.start_server()
    
    def setup_data_directory(self):
        """Create data directory in user's home folder"""
        home_dir = Path.home()
        self.data_dir = home_dir / "HPM_Inventory_Data"
        self.data_dir.mkdir(exist_ok=True)
        
        # Change working directory to data directory
        os.chdir(self.data_dir)
        
        # Initialize CSV files if they don't exist
        from utils import initialize_csv_files
        initialize_csv_files()
    
    def find_free_port(self):
        """Find a free port to run the server on"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
    
    def setup_gui(self):
        """Setup the main GUI window"""
        # Main frame
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="HPM Inventory Tracker", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Status
        self.status_label = tk.Label(main_frame, text="Starting server...", 
                                    font=("Arial", 10))
        self.status_label.pack(pady=(0, 20))
        
        # Buttons frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        # Open Browser button
        self.open_button = tk.Button(button_frame, text="Open Inventory System", 
                                   command=self.open_browser,
                                   font=("Arial", 12),
                                   bg="#007bff", fg="white",
                                   padx=20, pady=10,
                                   state=tk.DISABLED)
        self.open_button.pack(pady=5)
        
        # Data management frame
        data_frame = tk.LabelFrame(main_frame, text="Data Management", 
                                  font=("Arial", 10, "bold"))
        data_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Open data folder button
        open_data_button = tk.Button(data_frame, text="Open Data Folder", 
                                   command=self.open_data_folder,
                                   font=("Arial", 10))
        open_data_button.pack(pady=5)
        
        # Backup button
        backup_button = tk.Button(data_frame, text="Backup Data", 
                                command=self.backup_data,
                                font=("Arial", 10))
        backup_button.pack(pady=5)
        
        # Info frame
        info_frame = tk.LabelFrame(main_frame, text="Information", 
                                 font=("Arial", 10, "bold"))
        info_frame.pack(fill=tk.X, pady=(20, 0))
        
        info_text = f"""Data Location: {self.data_dir}
Server Port: {self.port}
Default Login: admin / admin123"""
        
        info_label = tk.Label(info_frame, text=info_text, 
                            font=("Arial", 9), justify=tk.LEFT)
        info_label.pack(pady=5)
        
        # Quit button
        quit_button = tk.Button(main_frame, text="Quit Application", 
                              command=self.quit_application,
                              font=("Arial", 10),
                              bg="#dc3545", fg="white",
                              padx=20, pady=5)
        quit_button.pack(pady=(20, 0))
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.quit_application)
    
    def start_server(self):
        """Start the Flask server in a separate thread"""
        def run_server():
            try:
                app.run(host='127.0.0.1', port=self.port, debug=False, 
                       use_reloader=False, threaded=True)
            except Exception as e:
                print(f"Server error: {e}")
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.server_running = True
        
        # Wait a moment for server to start, then update status
        self.root.after(2000, self.update_status)
    
    def update_status(self):
        """Update status and enable buttons once server is running"""
        try:
            # Test if server is responding
            import urllib.request
            urllib.request.urlopen(f'http://127.0.0.1:{self.port}/', timeout=1)
            self.status_label.config(text="Server running - Ready to use!")
            self.open_button.config(state=tk.NORMAL)
        except:
            self.status_label.config(text="Server starting...")
            self.root.after(1000, self.update_status)
    
    def open_browser(self):
        """Open the inventory system in the default web browser"""
        webbrowser.open(f'http://127.0.0.1:{self.port}/')
    
    def open_data_folder(self):
        """Open the data folder in the system file manager"""
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", str(self.data_dir)])
        elif sys.platform == "win32":  # Windows
            subprocess.run(["explorer", str(self.data_dir)])
        else:  # Linux
            subprocess.run(["xdg-open", str(self.data_dir)])
    
    def backup_data(self):
        """Create a backup of all data files"""
        try:
            backup_dir = filedialog.askdirectory(title="Select Backup Location")
            if backup_dir:
                import shutil
                from datetime import datetime
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_folder = Path(backup_dir) / f"HPM_Inventory_Backup_{timestamp}"
                backup_folder.mkdir(exist_ok=True)
                
                # Copy all CSV files
                for csv_file in self.data_dir.glob("*.csv"):
                    shutil.copy2(csv_file, backup_folder)
                
                messagebox.showinfo("Backup Complete", 
                                  f"Data backed up to:\n{backup_folder}")
        except Exception as e:
            messagebox.showerror("Backup Error", f"Failed to create backup:\n{e}")
    
    def quit_application(self):
        """Quit the application"""
        self.root.quit()
        self.root.destroy()
        sys.exit(0)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app_instance = HPMInventoryApp()
    app_instance.run()