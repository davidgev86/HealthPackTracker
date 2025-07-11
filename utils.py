"""
Utility functions for CSV operations and data management.
"""
import csv
import os
from datetime import datetime
from typing import List, Optional
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, InventoryItem, WasteEntry

# File paths
INVENTORY_FILE = 'inventory.csv'
USERS_FILE = 'users.csv'
WASTE_LOG_FILE = 'waste_log.csv'

def initialize_csv_files():
    """Initialize CSV files with headers if they don't exist"""
    
    # Initialize inventory.csv
    if not os.path.exists(INVENTORY_FILE):
        with open(INVENTORY_FILE, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['name', 'unit', 'quantity', 'par_level', 'category', 'unit_cost', 'last_updated'])
            writer.writeheader()
    
    # Initialize users.csv with default admin user
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['username', 'password_hash', 'role', 'email'])
            writer.writeheader()
            # Create default admin user
            admin_user = {
                'username': 'admin',
                'password_hash': generate_password_hash('admin123'),
                'role': 'admin',
                'email': 'admin@healthpackmeals.com'
            }
            writer.writerow(admin_user)
    
    # Initialize waste_log.csv
    if not os.path.exists(WASTE_LOG_FILE):
        with open(WASTE_LOG_FILE, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['item_name', 'quantity', 'unit', 'reason', 'date', 'logged_by', 'unit_cost'])
            writer.writeheader()

def read_inventory() -> List[InventoryItem]:
    """Read inventory items from CSV file"""
    items = []
    try:
        with open(INVENTORY_FILE, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                item = InventoryItem(
                    name=row['name'],
                    unit=row['unit'],
                    quantity=int(row['quantity']),
                    par_level=int(row['par_level']),
                    category=row.get('category', 'General'),
                    unit_cost=float(row.get('unit_cost', 0.0)),
                    last_updated=row.get('last_updated', '')
                )
                items.append(item)
    except FileNotFoundError:
        pass
    return items

def write_inventory(items: List[InventoryItem]):
    """Write inventory items to CSV file"""
    with open(INVENTORY_FILE, 'w', newline='') as file:
        fieldnames = ['name', 'unit', 'quantity', 'par_level', 'category', 'unit_cost', 'last_updated']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for item in items:
            writer.writerow(item.to_dict())

def get_inventory_item(name: str) -> Optional[InventoryItem]:
    """Get a specific inventory item by name"""
    items = read_inventory()
    for item in items:
        if item.name == name:
            return item
    return None

def update_inventory_item(name: str, updated_item: InventoryItem) -> bool:
    """Update a specific inventory item"""
    items = read_inventory()
    for i, item in enumerate(items):
        if item.name == name:
            items[i] = updated_item
            write_inventory(items)
            return True
    return False

def delete_inventory_item(name: str) -> bool:
    """Delete a specific inventory item"""
    items = read_inventory()
    original_length = len(items)
    items = [item for item in items if item.name != name]
    if len(items) < original_length:
        write_inventory(items)
        return True
    return False

def read_users() -> List[User]:
    """Read users from CSV file"""
    users = []
    try:
        with open(USERS_FILE, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                user = User(
                    username=row['username'],
                    password_hash=row['password_hash'],
                    role=row['role'],
                    email=row.get('email', '')
                )
                users.append(user)
    except FileNotFoundError:
        pass
    return users

def get_user(username: str) -> Optional[User]:
    """Get a specific user by username"""
    users = read_users()
    for user in users:
        if user.username == username:
            return user
    return None

def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate user with username and password"""
    user = get_user(username)
    if user and check_password_hash(user.password_hash, password):
        return user
    return None

def read_waste_log() -> List[WasteEntry]:
    """Read waste log entries from CSV file"""
    entries = []
    try:
        with open(WASTE_LOG_FILE, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                entry = WasteEntry(
                    item_name=row['item_name'],
                    quantity=int(row['quantity']),
                    unit=row['unit'],
                    reason=row['reason'],
                    date=row['date'],
                    logged_by=row['logged_by'],
                    unit_cost=float(row.get('unit_cost', 0.0))
                )
                entries.append(entry)
    except FileNotFoundError:
        pass
    return entries

def add_waste_entry(entry: WasteEntry):
    """Add a new waste log entry"""
    with open(WASTE_LOG_FILE, 'a', newline='') as file:
        fieldnames = ['item_name', 'quantity', 'unit', 'reason', 'date', 'logged_by', 'unit_cost']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow(entry.to_dict())

def get_low_stock_items() -> List[InventoryItem]:
    """Get all items that are below par level"""
    items = read_inventory()
    return [item for item in items if item.is_low_stock()]

def export_inventory_csv() -> str:
    """Export inventory data as CSV string"""
    items = read_inventory()
    if not items:
        return ""
    
    output = "name,unit,quantity,par_level,category,unit_cost,last_updated\n"
    for item in items:
        output += f"{item.name},{item.unit},{item.quantity},{item.par_level},{item.category},{item.unit_cost},{item.last_updated}\n"
    return output

def import_inventory_csv(csv_data: str) -> tuple[bool, str]:
    """Import inventory data from CSV string"""
    try:
        lines = csv_data.strip().split('\n')
        if len(lines) < 2:
            return False, "CSV must have at least a header and one data row"
        
        # Parse header
        header = lines[0].split(',')
        required_fields = ['name', 'unit', 'quantity', 'par_level']
        
        for field in required_fields:
            if field not in header:
                return False, f"Missing required field: {field}"
        
        # Parse data rows
        items = []
        for i, line in enumerate(lines[1:], 2):
            try:
                values = line.split(',')
                if len(values) != len(header):
                    return False, f"Row {i}: Number of values doesn't match header"
                
                row_data = dict(zip(header, values))
                item = InventoryItem(
                    name=row_data['name'].strip(),
                    unit=row_data['unit'].strip(),
                    quantity=int(row_data['quantity']),
                    par_level=int(row_data['par_level']),
                    category=row_data.get('category', 'General').strip(),
                    unit_cost=float(row_data.get('unit_cost', 0.0)),
                    last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
                items.append(item)
            except ValueError as e:
                return False, f"Row {i}: Invalid data format - {str(e)}"
        
        # Write to file
        write_inventory(items)
        return True, f"Successfully imported {len(items)} items"
        
    except Exception as e:
        return False, f"Error parsing CSV: {str(e)}"
