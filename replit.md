# HPM Inventory Tracker

## Overview

The HPM Inventory Tracker is a web-based inventory management system built with Flask for managing food inventory in a commercial kitchen or restaurant setting. The application provides role-based access control with different permission levels for staff, managers, and administrators. It features inventory tracking, waste logging, and import/export capabilities using CSV files for data persistence.

## System Architecture

The application follows a simple MVC (Model-View-Controller) pattern built on Flask:

### Backend Architecture
- **Flask Web Framework**: Lightweight Python web framework serving as the application foundation
- **CSV-based Data Storage**: File-based storage system using CSV files instead of a traditional database
- **Session-based Authentication**: Uses Flask sessions for user authentication and authorization
- **Role-based Access Control**: Three-tier permission system (admin, manager, staff)

### Frontend Architecture
- **Jinja2 Templates**: Server-side rendering with Flask's built-in template engine
- **Bootstrap 5**: CSS framework for responsive design with dark theme
- **Font Awesome**: Icon library for user interface enhancement
- **Mobile-first Responsive Design**: Optimized for both desktop and mobile devices

## Key Components

### Authentication System
- **Session Management**: Flask sessions handle user authentication state
- **Password Hashing**: Werkzeug's security utilities for password protection
- **Role-based Permissions**: Decorators enforce access control at the route level
- **Default Admin Account**: Pre-configured admin user (username: admin, password: admin123)

### Inventory Management
- **Item Tracking**: Name, quantity, unit, par level, and category management
- **Low Stock Alerts**: Automatic identification of items below par levels
- **Category Organization**: Predefined categories for food items and supplies
- **Last Updated Tracking**: Timestamps for inventory changes
- **HPM Items Isolation**: Dedicated page for HPM vendor items with separate inventory management

### Waste Logging
- **Waste Entry Recording**: Track wasted inventory with quantity, reason, and timestamp
- **User Attribution**: Log which user recorded each waste entry
- **Inventory Integration**: Automatic inventory adjustment when waste is logged
- **HPM Waste Tracking**: Isolated waste logging for HPM items with dedicated interface

### Vendor Management
- **Vendor Information**: Contact details, phone, email, and address tracking
- **Shopping List Exclusion**: Option to exclude specific vendors from shopping lists and PDF reports
- **Usage Tracking**: Visual indicators showing which vendors are actively used

### Data Import/Export
- **CSV Export**: Download current inventory data for backup or external use
- **CSV Import**: Bulk upload inventory data with validation
- **Data Validation**: Ensures imported data meets required format standards

## Data Flow

1. **User Authentication**: Users log in through the login page, creating a session
2. **Permission Check**: Route decorators verify user permissions before page access
3. **CSV Data Access**: Utility functions read/write inventory and user data to CSV files
4. **Data Processing**: Models validate and transform data between CSV and application formats
5. **Template Rendering**: Jinja2 templates render dynamic content based on user data and permissions

## External Dependencies

### Python Packages
- **Flask**: Web framework and routing
- **Werkzeug**: WSGI utilities and security functions
- **Jinja2**: Template engine (included with Flask)

### Frontend Libraries (CDN)
- **Bootstrap 5**: CSS framework with dark theme
- **Font Awesome 6**: Icon library
- **Bootstrap JavaScript**: Interactive components

### File Dependencies
- **CSV Files**: inventory.csv, users.csv, waste_log.csv for data persistence
- **Static Assets**: Custom CSS for mobile responsiveness

## Desktop Application

A standalone desktop version has been created that can run on both macOS and Windows computers:

### Desktop Architecture
- **Tkinter GUI**: Simple desktop launcher interface
- **Local Flask Server**: Embedded web server running on localhost
- **Data Management**: Automatic data folder creation in user's home directory
- **PyInstaller**: Creates standalone executables for distribution

### Desktop Features
- Cross-platform compatibility (macOS and Windows)
- No internet connection required
- Automatic data backup functionality
- Simple one-click launcher
- User-friendly installation process

### Distribution Package
- Complete source code with installation scripts
- ZIP file for easy distribution
- Platform-specific installation instructions
- Automated dependency installation

## Deployment Strategy

The application is designed for simple deployment with minimal infrastructure requirements:

### Development Setup
- **Local Development**: Flask development server on port 5000
- **Debug Mode**: Enabled for development with auto-reload
- **Environment Variables**: SESSION_SECRET for session security

### Production Considerations
- **WSGI Deployment**: ProxyFix middleware configured for reverse proxy setup
- **File Permissions**: Ensure write access to CSV files
- **Session Security**: Use strong SESSION_SECRET in production
- **Data Backup**: Regular CSV file backups recommended

### Scalability Limitations
- **CSV Storage**: Not suitable for high-concurrency or large datasets
- **No Database**: Consider migrating to proper database for production scale
- **Session Storage**: In-memory sessions don't persist across server restarts

## Changelog
- July 27, 2025. Added "Add HPM Item" functionality directly from HPM Items page with comprehensive form and HPM vendor auto-assignment
- July 27, 2025. Added category management functionality to HPM Items page allowing managers/admins to add and delete categories (including default categories)
- July 27, 2025. Removed restrictions on deleting default categories per user preference for full customization control
- July 27, 2025. Added search bar functionality to HPM Items page for easy meal finding within categories
- July 15, 2025. Added manual "Generate Report" button for admin users to force create weekly inventory reports
- July 15, 2025. Added weekly inventory cost tracking system with WeeklyInventoryReport model for spending analysis
- July 15, 2025. Enhanced weekly waste reports page to include inventory cost tracking with week-to-week comparisons
- July 15, 2025. Implemented automated weekly inventory report generation every 7 days (excluding HPM items)
- July 15, 2025. Created dedicated HPM Items page with isolated inventory management and waste logging for HPM vendor items
- July 15, 2025. Added vendor exclusion feature for shopping lists with checkbox controls in vendor management
- July 15, 2025. Made all page headers consistent throughout the application to match homepage design
- July 15, 2025. Enhanced weekly waste reports with meaningful data visualization and category comparisons
- July 15, 2025. Implemented comprehensive decimal quantity support across all inventory and waste operations
- July 14, 2025. Updated waste log with full CRUD capabilities and modern card-based interface
- July 14, 2025. Removed meal planner and recipes functionality per user request
- July 08, 2025. Created standalone desktop application version
- July 07, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.
Desktop Application: User wants standalone desktop application for Mac and Windows computers.