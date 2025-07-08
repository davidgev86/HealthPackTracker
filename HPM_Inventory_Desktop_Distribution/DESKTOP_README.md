# HPM Inventory Tracker - Desktop Application

A standalone desktop version of the HPM Inventory Tracker that can be installed and run on Mac and Windows computers.

## Features

- **Standalone Application**: No need for external servers or internet connection
- **Cross-Platform**: Works on both macOS and Windows
- **User-Friendly Interface**: Simple desktop launcher with web-based interface
- **Data Management**: Automatic data folder creation and backup functionality
- **Complete Inventory System**: All features from the web version included

## Quick Start

### For End Users (Pre-built Application)

1. Download the appropriate version for your system:
   - **macOS**: `HPM_Inventory_Tracker` (no extension)
   - **Windows**: `HPM_Inventory_Tracker.exe`

2. Double-click the application to run it

3. Click "Open Inventory System" to access the web interface

4. Login with default credentials:
   - Username: `admin`
   - Password: `admin123`

### For Developers

#### Setup Development Environment

1. **Install Python 3.8+** (if not already installed)

2. **Clone/Download the project files**

3. **Run the setup script**:
   ```bash
   python setup_desktop.py
   ```

4. **Test the application**:
   ```bash
   python run_desktop.py
   ```

#### Build Executable

1. **Run the build script**:
   ```bash
   python build_desktop.py
   ```

2. **Find the executable in**:
   ```
   dist/HPM_Inventory_Installer/
   ```

## Data Storage

The application automatically creates a data folder in your home directory:

- **macOS**: `~/HPM_Inventory_Data/`
- **Windows**: `C:\Users\[username]\HPM_Inventory_Data\`

This folder contains:
- `inventory.csv` - Inventory items
- `users.csv` - User accounts
- `waste_log.csv` - Waste tracking records

## Application Architecture

### Desktop Layer (`desktop_app.py`)
- Tkinter GUI for desktop interface
- Flask server management
- Data directory setup
- Cross-platform file operations

### Web Layer (Flask Application)
- Complete inventory management system
- Role-based access control
- CSV-based data storage
- Mobile-responsive interface

### Build System
- PyInstaller for creating executables
- Automated packaging with dependencies
- Cross-platform build support

## System Requirements

### Minimum Requirements
- **macOS**: macOS 10.12 or later
- **Windows**: Windows 10 or later
- **RAM**: 2GB minimum
- **Storage**: 100MB for application + data

### Recommended Requirements
- **macOS**: macOS 11 or later
- **Windows**: Windows 11
- **RAM**: 4GB or more
- **Storage**: 500MB for application + data

## Features Overview

### Inventory Management
- Add, edit, and delete inventory items
- Track quantities and par levels
- Category-based organization
- Low stock alerts

### User Management
- Role-based access (Admin, Manager, Staff)
- Secure authentication
- Permission-based features

### Waste Tracking
- Log waste with reasons
- Automatic inventory adjustment
- Historical waste reports

### Data Management
- CSV import/export
- Backup functionality
- Data folder access

## Troubleshooting

### Application Won't Start
1. Check if Python is installed (for development)
2. Verify all dependencies are installed
3. Check for port conflicts (app will find free port automatically)

### Cannot Access Web Interface
1. Wait for server to fully start (2-3 seconds)
2. Check if firewall is blocking the application
3. Try restarting the application

### Data Not Saving
1. Check file permissions in data folder
2. Verify data folder exists and is writable
3. Check for disk space

### Login Issues
1. Use default credentials: admin/admin123
2. Check if users.csv file exists in data folder
3. Restart application to regenerate default user

## Building for Distribution

### Prerequisites
```bash
pip install pyinstaller
```

### Build Commands

**For macOS**:
```bash
python build_desktop.py
```

**For Windows**:
```bash
python build_desktop.py
```

### Distribution Package
The build creates a complete installer package in `dist/HPM_Inventory_Installer/` containing:
- Executable file
- README.txt with user instructions
- All necessary dependencies bundled

## Security Notes

- Application runs locally on your computer
- No internet connection required
- Data stored locally in user's home directory
- Default admin password should be changed after first login

## License

This application is proprietary software developed for Health Pack Meals.

## Support

For technical support, please contact Health Pack Meals IT department.