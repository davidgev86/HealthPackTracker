#!/usr/bin/env python3
"""
HPM Inventory Tracker - Easy Installer
One-click installer that handles everything automatically
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
import winreg
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import time

class EasyInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("HPM Inventory Tracker - Easy Installer")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Variables
        self.install_path = Path.home() / "HPM_Inventory"
        self.python_installed = False
        self.status_text = tk.StringVar()
        self.progress = tk.StringVar()
        
        self.setup_gui()
        self.check_system()
    
    def setup_gui(self):
        """Setup the installer GUI"""
        # Main frame
        main_frame = tk.Frame(self.root, padx=30, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, 
                              text="HPM Inventory Tracker\nEasy Installer", 
                              font=("Arial", 16, "bold"),
                              fg="#2c3e50")
        title_label.pack(pady=(0, 20))
        
        # Description
        desc_text = """This installer will automatically:
• Download and install Python (if needed)
• Install the HPM Inventory Tracker
• Create desktop shortcuts
• Set up your data folder
• Start the application when complete

Installation location: """ + str(self.install_path)
        
        desc_label = tk.Label(main_frame, text=desc_text, 
                             font=("Arial", 10), justify=tk.LEFT,
                             wraplength=450)
        desc_label.pack(pady=(0, 20))
        
        # Status frame
        status_frame = tk.LabelFrame(main_frame, text="Installation Status", 
                                   font=("Arial", 10, "bold"))
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.status_label = tk.Label(status_frame, textvariable=self.status_text,
                                   font=("Arial", 9), wraplength=400,
                                   justify=tk.LEFT)
        self.status_label.pack(pady=10, padx=10)
        
        # Progress bar (text-based)
        self.progress_label = tk.Label(status_frame, textvariable=self.progress,
                                     font=("Arial", 9, "bold"), fg="#27ae60")
        self.progress_label.pack(pady=(0, 10))
        
        # Buttons frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        # Install button
        self.install_button = tk.Button(button_frame, 
                                      text="Install HPM Inventory Tracker", 
                                      command=self.start_installation,
                                      font=("Arial", 12, "bold"),
                                      bg="#3498db", fg="white",
                                      padx=30, pady=10)
        self.install_button.pack(pady=5)
        
        # Custom location button
        location_button = tk.Button(button_frame, 
                                  text="Choose Different Location", 
                                  command=self.choose_location,
                                  font=("Arial", 9))
        location_button.pack(pady=5)
        
        # Exit button
        exit_button = tk.Button(button_frame, text="Exit", 
                              command=self.root.destroy,
                              font=("Arial", 9))
        exit_button.pack(pady=5)
    
    def check_system(self):
        """Check system requirements"""
        self.status_text.set("Checking system requirements...")
        
        # Check Python
        try:
            result = subprocess.run([sys.executable, "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                self.python_installed = True
                self.status_text.set(f"✓ Python found: {version}\nReady to install!")
            else:
                self.status_text.set("Python not found. Will be installed automatically.")
        except:
            self.status_text.set("Python not found. Will be installed automatically.")
    
    def choose_location(self):
        """Let user choose installation location"""
        folder = filedialog.askdirectory(title="Choose Installation Folder")
        if folder:
            self.install_path = Path(folder) / "HPM_Inventory"
            self.status_text.set(f"Installation location changed to:\n{self.install_path}")
    
    def start_installation(self):
        """Start the installation process"""
        self.install_button.config(state=tk.DISABLED, text="Installing...")
        
        # Run installation in separate thread to avoid blocking GUI
        install_thread = threading.Thread(target=self.run_installation)
        install_thread.daemon = True
        install_thread.start()
    
    def update_status(self, message, progress_text=""):
        """Update status message"""
        self.status_text.set(message)
        self.progress.set(progress_text)
        self.root.update()
    
    def run_installation(self):
        """Run the complete installation process"""
        try:
            # Step 1: Create installation directory
            self.update_status("Creating installation directory...", "Step 1/6")
            self.install_path.mkdir(parents=True, exist_ok=True)
            time.sleep(1)
            
            # Step 2: Install Python if needed
            if not self.python_installed:
                self.update_status("Downloading and installing Python...\n(This may take a few minutes)", "Step 2/6")
                self.install_python()
            else:
                self.update_status("Python already installed, skipping...", "Step 2/6")
            time.sleep(1)
            
            # Step 3: Copy application files
            self.update_status("Copying application files...", "Step 3/6")
            self.copy_application_files()
            time.sleep(1)
            
            # Step 4: Install dependencies
            self.update_status("Installing application dependencies...", "Step 4/6")
            self.install_dependencies()
            time.sleep(1)
            
            # Step 5: Create shortcuts
            self.update_status("Creating desktop shortcuts...", "Step 5/6")
            self.create_shortcuts()
            time.sleep(1)
            
            # Step 6: Complete
            self.update_status("Installation complete!\nHPM Inventory Tracker is ready to use.", "Step 6/6 - DONE!")
            
            # Show completion dialog
            self.root.after(100, self.show_completion_dialog)
            
        except Exception as e:
            self.update_status(f"Installation failed: {str(e)}", "ERROR")
            self.install_button.config(state=tk.NORMAL, text="Retry Installation")
    
    def install_python(self):
        """Download and install Python automatically"""
        python_url = "https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe"
        python_installer = self.install_path / "python_installer.exe"
        
        # Download Python installer
        urllib.request.urlretrieve(python_url, python_installer)
        
        # Run Python installer silently
        subprocess.run([
            str(python_installer),
            "/quiet",
            "InstallAllUsers=0",
            "PrependPath=1",
            "Include_test=0"
        ], check=True)
        
        # Clean up installer
        python_installer.unlink()
        
        # Update Python path
        self.python_installed = True
    
    def copy_application_files(self):
        """Copy all application files to installation directory"""
        # List of files to copy (these should be in the same directory as this installer)
        files_to_copy = [
            "desktop_app.py", "app.py", "main.py", "models.py", "routes.py", "utils.py",
            "requirements_desktop.txt", "DESKTOP_README.md", "WORKFLOW_GUIDE.md",
            "WORKFLOW_QUICK_REFERENCE.md", "GOOGLE_SHEETS_TEMPLATE.csv"
        ]
        
        current_dir = Path(__file__).parent
        
        for file_name in files_to_copy:
            src = current_dir / file_name
            if src.exists():
                shutil.copy2(src, self.install_path / file_name)
        
        # Copy directories
        for dir_name in ["templates", "static"]:
            src_dir = current_dir / dir_name
            if src_dir.exists():
                shutil.copytree(src_dir, self.install_path / dir_name, dirs_exist_ok=True)
    
    def install_dependencies(self):
        """Install Python dependencies"""
        requirements_file = self.install_path / "requirements_desktop.txt"
        if requirements_file.exists():
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True, capture_output=True)
    
    def create_shortcuts(self):
        """Create desktop shortcuts"""
        try:
            desktop = Path.home() / "Desktop"
            
            # Create batch file to run the application
            batch_file = self.install_path / "HPM_Inventory.bat"
            batch_content = f"""@echo off
cd /d "{self.install_path}"
python desktop_app.py
pause"""
            
            with open(batch_file, "w") as f:
                f.write(batch_content)
            
            # Create desktop shortcut (Windows)
            if sys.platform == "win32":
                import win32com.client
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(str(desktop / "HPM Inventory Tracker.lnk"))
                shortcut.Targetpath = str(batch_file)
                shortcut.WorkingDirectory = str(self.install_path)
                shortcut.IconLocation = str(batch_file)
                shortcut.save()
        except ImportError:
            # Fallback: just create the batch file
            pass
    
    def show_completion_dialog(self):
        """Show installation completion dialog"""
        result = messagebox.askyesno(
            "Installation Complete",
            "HPM Inventory Tracker has been installed successfully!\n\n"
            f"Installation location: {self.install_path}\n\n"
            "Would you like to start the application now?",
            icon="question"
        )
        
        if result:
            # Start the application
            subprocess.Popen([sys.executable, str(self.install_path / "desktop_app.py")],
                           cwd=str(self.install_path))
        
        self.root.destroy()
    
    def run(self):
        """Start the installer"""
        self.root.mainloop()

if __name__ == "__main__":
    try:
        installer = EasyInstaller()
        installer.run()
    except Exception as e:
        # Fallback error dialog
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Installer Error", f"Failed to start installer: {e}")
        root.destroy()