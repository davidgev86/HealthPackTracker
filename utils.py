"""
Utility functions for CSV operations and data management.
"""
import csv
import os
import shutil
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, InventoryItem, WasteEntry, Vendor, Category, WeeklyWasteReport, DEFAULT_VENDORS, DEFAULT_CATEGORIES
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from io import BytesIO

# File paths
INVENTORY_FILE = 'inventory.csv'
USERS_FILE = 'users.csv'
WASTE_LOG_FILE = 'waste_log.csv'
VENDORS_FILE = 'vendors.csv'
CATEGORIES_FILE = 'categories.csv'
WASTE_ARCHIVE_DIR = 'waste_archive'
WEEKLY_REPORTS_FILE = 'weekly_waste_reports.csv'

def initialize_csv_files():
    """Initialize CSV files with headers if they don't exist"""
    
    # Initialize inventory.csv
    if not os.path.exists(INVENTORY_FILE):
        with open(INVENTORY_FILE, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['name', 'unit', 'quantity', 'par_level', 'category', 'unit_cost', 'vendors', 'last_updated'])
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
    
    # Initialize vendors.csv with default vendors
    if not os.path.exists(VENDORS_FILE):
        with open(VENDORS_FILE, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['name', 'contact_info', 'address', 'phone', 'email'])
            writer.writeheader()
            for vendor_name in DEFAULT_VENDORS:
                vendor = {
                    'name': vendor_name,
                    'contact_info': '',
                    'address': '',
                    'phone': '',
                    'email': ''
                }
                writer.writerow(vendor)
    

    # Initialize categories.csv with default categories
    if not os.path.exists(CATEGORIES_FILE):
        with open(CATEGORIES_FILE, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['name', 'description', 'created_date'])
            writer.writeheader()
            # Add default categories
            for category_name in DEFAULT_CATEGORIES:
                writer.writerow({
                    'name': category_name,
                    'description': f'Default {category_name} category',
                    'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

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
                    vendors=row.get('vendors', ''),
                    last_updated=row.get('last_updated', '')
                )
                items.append(item)
    except FileNotFoundError:
        pass
    return items

def write_inventory(items: List[InventoryItem]):
    """Write inventory items to CSV file"""
    with open(INVENTORY_FILE, 'w', newline='') as file:
        fieldnames = ['name', 'unit', 'quantity', 'par_level', 'category', 'unit_cost', 'vendors', 'last_updated']
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
                try:
                    # Clean up the unit_cost field to handle any parsing issues
                    unit_cost_str = row.get('unit_cost', '0.0')
                    # Extract only numeric characters and decimal point
                    import re
                    unit_cost_clean = re.match(r'^[\d.]+', str(unit_cost_str))
                    unit_cost = float(unit_cost_clean.group()) if unit_cost_clean else 0.0
                    
                    entry = WasteEntry(
                        item_name=row['item_name'],
                        quantity=float(row['quantity']),
                        unit=row['unit'],
                        reason=row['reason'],
                        date=row['date'],
                        logged_by=row['logged_by'],
                        unit_cost=unit_cost
                    )
                    entries.append(entry)
                except (ValueError, KeyError) as e:
                    # Skip malformed entries and log the error
                    print(f"Skipping malformed waste log entry: {row}, Error: {e}")
                    continue
    except FileNotFoundError:
        pass
    return entries

def add_waste_entry(entry: WasteEntry):
    """Add a new waste log entry"""
    # Read existing entries
    entries = read_waste_log()
    # Add new entry
    entries.append(entry)
    # Write all entries back to ensure proper formatting
    write_waste_log(entries)

def write_waste_log(entries: List[WasteEntry]):
    """Write waste log entries to CSV file"""
    with open(WASTE_LOG_FILE, 'w', newline='') as file:
        fieldnames = ['item_name', 'quantity', 'unit', 'reason', 'date', 'logged_by', 'unit_cost']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for entry in entries:
            writer.writerow(entry.to_dict())

def update_waste_entry(entry_index: int, updated_entry: WasteEntry) -> bool:
    """Update a waste log entry by index"""
    try:
        entries = read_waste_log()
        if 0 <= entry_index < len(entries):
            entries[entry_index] = updated_entry
            write_waste_log(entries)
            return True
        return False
    except Exception:
        return False

def delete_waste_entry(entry_index: int) -> bool:
    """Delete a waste log entry by index"""
    try:
        entries = read_waste_log()
        if 0 <= entry_index < len(entries):
            entries.pop(entry_index)
            write_waste_log(entries)
            return True
        return False
    except Exception:
        return False

def get_waste_entry(entry_index: int) -> Optional[WasteEntry]:
    """Get a specific waste log entry by index"""
    try:
        entries = read_waste_log()
        if 0 <= entry_index < len(entries):
            return entries[entry_index]
        return None
    except Exception:
        return None

def get_low_stock_items() -> List[InventoryItem]:
    """Get all items that are below par level"""
    items = read_inventory()
    return [item for item in items if item.is_low_stock()]

def export_inventory_csv() -> str:
    """Export inventory data as CSV string"""
    items = read_inventory()
    if not items:
        return ""
    
    output = "name,unit,quantity,par_level,category,unit_cost,vendors,last_updated\n"
    for item in items:
        output += f"{item.name},{item.unit},{item.quantity},{item.par_level},{item.category},{item.unit_cost},{item.vendors},{item.last_updated}\n"
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
                    vendors=row_data.get('vendors', '').strip(),
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

# Vendor management functions
def read_vendors() -> List[Vendor]:
    """Read vendors from CSV file"""
    vendors = []
    try:
        with open(VENDORS_FILE, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                vendor = Vendor(
                    name=row['name'],
                    contact_info=row.get('contact_info', ''),
                    address=row.get('address', ''),
                    phone=row.get('phone', ''),
                    email=row.get('email', '')
                )
                vendors.append(vendor)
    except FileNotFoundError:
        pass
    return vendors

def write_vendors(vendors: List[Vendor]):
    """Write vendors to CSV file"""
    with open(VENDORS_FILE, 'w', newline='') as file:
        fieldnames = ['name', 'contact_info', 'address', 'phone', 'email']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for vendor in vendors:
            writer.writerow(vendor.to_dict())

def get_vendor(name: str) -> Optional[Vendor]:
    """Get a specific vendor by name"""
    vendors = read_vendors()
    for vendor in vendors:
        if vendor.name == name:
            return vendor
    return None

def add_vendor(vendor: Vendor) -> bool:
    """Add a new vendor"""
    vendors = read_vendors()
    # Check if vendor already exists
    if any(v.name == vendor.name for v in vendors):
        return False
    vendors.append(vendor)
    write_vendors(vendors)
    return True

def update_vendor(old_name: str, updated_vendor: Vendor) -> bool:
    """Update an existing vendor"""
    try:
        vendors = read_vendors()
        for i, vendor in enumerate(vendors):
            if vendor.name == old_name:
                vendors[i] = updated_vendor
                write_vendors(vendors)
                return True
        return False
    except Exception:
        return False

def delete_vendor(name: str) -> bool:
    """Delete a vendor"""
    try:
        vendors = read_vendors()
        vendors = [vendor for vendor in vendors if vendor.name != name]
        write_vendors(vendors)
        return True
    except Exception:
        return False

def is_vendor_in_use(vendor_name: str) -> bool:
    """Check if a vendor is being used by any inventory items"""
    items = read_inventory()
    for item in items:
        if vendor_name in item.get_vendors():
            return True
    return False



# Filtering and search functions
def filter_inventory(category: str = None, vendor: str = None, low_stock_only: bool = False) -> List[InventoryItem]:
    """Filter inventory items based on criteria"""
    items = read_inventory()
    
    if category:
        items = [item for item in items if item.category == category]
    
    if vendor:
        items = [item for item in items if vendor in item.get_vendors()]
    
    if low_stock_only:
        items = [item for item in items if item.is_low_stock()]
    
    return items

def get_shopping_list_items() -> List[InventoryItem]:
    """Get items that need to be restocked (low stock items)"""
    return filter_inventory(low_stock_only=True)



# PDF generation functions
def generate_shopping_list_pdf() -> bytes:
    """Generate shopping list PDF for low stock items"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.darkblue
    )
    story.append(Paragraph("Health Pack Meals - Shopping List", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Get low stock items
    low_stock_items = get_shopping_list_items()
    
    if not low_stock_items:
        story.append(Paragraph("No items are currently low in stock.", styles['Normal']))
    else:
        # Group items by vendor
        vendor_groups = {}
        for item in low_stock_items:
            vendors = item.get_vendors() if item.get_vendors() else ['No Vendor Assigned']
            for vendor in vendors:
                if vendor not in vendor_groups:
                    vendor_groups[vendor] = []
                vendor_groups[vendor].append(item)
        
        # Create table for each vendor
        for vendor, items in vendor_groups.items():
            story.append(Paragraph(f"Vendor: {vendor}", styles['Heading2']))
            
            # Table data
            table_data = [['Item Name', 'Current Stock', 'Par Level', 'Needed', 'Unit', 'Unit Cost', 'Total Cost']]
            total_cost = 0
            
            for item in items:
                needed = item.quantity_needed()
                item_cost = needed * item.unit_cost
                total_cost += item_cost
                
                table_data.append([
                    item.name,
                    str(item.quantity),
                    str(item.par_level),
                    str(needed),
                    item.unit,
                    f"${item.unit_cost:.2f}",
                    f"${item_cost:.2f}"
                ])
            
            # Add total row
            table_data.append(['', '', '', '', '', 'Total:', f"${total_cost:.2f}"])
            
            # Create table
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
    
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes



# Category Management Functions
def read_categories() -> List[Category]:
    """Read categories from CSV file"""
    categories = []
    try:
        with open(CATEGORIES_FILE, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                category = Category(
                    name=row['name'],
                    description=row.get('description', ''),
                    created_date=row.get('created_date', '')
                )
                categories.append(category)
    except FileNotFoundError:
        # If file doesn't exist, return default categories
        for category_name in DEFAULT_CATEGORIES:
            categories.append(Category(
                name=category_name,
                description=f'Default {category_name} category',
                created_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
    return categories

def write_categories(categories: List[Category]):
    """Write categories to CSV file"""
    with open(CATEGORIES_FILE, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['name', 'description', 'created_date'])
        writer.writeheader()
        for category in categories:
            writer.writerow(category.to_dict())

def get_category(name: str) -> Optional[Category]:
    """Get a specific category by name"""
    categories = read_categories()
    for category in categories:
        if category.name == name:
            return category
    return None

def add_category(category: Category) -> bool:
    """Add a new category"""
    try:
        categories = read_categories()
        # Check if category already exists
        for existing_category in categories:
            if existing_category.name == category.name:
                return False
        categories.append(category)
        write_categories(categories)
        return True
    except Exception:
        return False

def update_category(old_name: str, updated_category: Category) -> bool:
    """Update an existing category"""
    try:
        categories = read_categories()
        for i, category in enumerate(categories):
            if category.name == old_name:
                categories[i] = updated_category
                write_categories(categories)
                return True
        return False
    except Exception:
        return False

def delete_category(name: str) -> bool:
    """Delete a category"""
    try:
        categories = read_categories()
        categories = [cat for cat in categories if cat.name != name]
        write_categories(categories)
        return True
    except Exception:
        return False

def get_category_names() -> List[str]:
    """Get list of all category names"""
    categories = read_categories()
    return [category.name for category in categories]

def is_category_in_use(category_name: str) -> bool:
    """Check if a category is being used by any inventory items"""
    items = read_inventory()
    for item in items:
        if item.category == category_name:
            return True
    return False

# Waste Log Archival Functions

def initialize_waste_archive():
    """Initialize waste archive directory and weekly reports file"""
    if not os.path.exists(WASTE_ARCHIVE_DIR):
        os.makedirs(WASTE_ARCHIVE_DIR)
    
    if not os.path.exists(WEEKLY_REPORTS_FILE):
        with open(WEEKLY_REPORTS_FILE, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['week_start', 'week_end', 'total_entries', 'total_value', 'by_category', 'by_reason', 'by_item'])
            writer.writeheader()

def should_archive_waste_log() -> bool:
    """Check if waste log should be archived (7 days old)"""
    if not os.path.exists(WASTE_LOG_FILE):
        return False
    
    # Check if file has any entries
    entries = read_waste_log()
    if not entries:
        return False
    
    try:
        # Check if oldest entry is 7+ days old
        oldest_entry_date = min(datetime.strptime(entry.date, '%Y-%m-%d %H:%M:%S') for entry in entries)
        return (datetime.now() - oldest_entry_date).days >= 7
    except (ValueError, TypeError):
        # If there's an issue parsing dates, don't archive
        return False

def generate_weekly_report(entries: List[WasteEntry], week_start: str, week_end: str) -> WeeklyWasteReport:
    """Generate weekly waste report from entries"""
    total_entries = len(entries)
    total_value = sum(entry.waste_value() for entry in entries)
    
    # Group by category (get category from inventory)
    by_category = {}
    inventory_items = {item.name: item for item in read_inventory()}
    
    for entry in entries:
        item = inventory_items.get(entry.item_name)
        category = item.category if item else 'Unknown'
        by_category[category] = by_category.get(category, 0) + entry.waste_value()
    
    # Group by reason
    by_reason = {}
    for entry in entries:
        by_reason[entry.reason] = by_reason.get(entry.reason, 0) + entry.waste_value()
    
    # Group by item
    by_item = {}
    for entry in entries:
        by_item[entry.item_name] = by_item.get(entry.item_name, 0) + entry.waste_value()
    
    return WeeklyWasteReport(
        week_start=week_start,
        week_end=week_end,
        total_entries=total_entries,
        total_value=total_value,
        by_category=by_category,
        by_reason=by_reason,
        by_item=by_item
    )

def archive_waste_log():
    """Archive current waste log and generate weekly report"""
    entries = read_waste_log()
    if not entries:
        return
    
    # Initialize archive if needed
    initialize_waste_archive()
    
    # Determine week boundaries
    now = datetime.now()
    week_start = now - timedelta(days=7)
    week_end = now
    
    # Generate weekly report
    report = generate_weekly_report(entries, week_start.strftime('%Y-%m-%d'), week_end.strftime('%Y-%m-%d'))
    
    # Save weekly report
    save_weekly_report(report)
    
    # Archive waste log file
    archive_filename = f"waste_log_{week_start.strftime('%Y%m%d')}_{week_end.strftime('%Y%m%d')}.csv"
    archive_path = os.path.join(WASTE_ARCHIVE_DIR, archive_filename)
    shutil.copy2(WASTE_LOG_FILE, archive_path)
    
    # Clear current waste log
    with open(WASTE_LOG_FILE, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['item_name', 'quantity', 'unit', 'reason', 'date', 'logged_by', 'unit_cost'])
        writer.writeheader()

def save_weekly_report(report: WeeklyWasteReport):
    """Save weekly report to file"""
    with open(WEEKLY_REPORTS_FILE, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['week_start', 'week_end', 'total_entries', 'total_value', 'by_category', 'by_reason', 'by_item'])
        writer.writerow(report.to_dict())

def read_weekly_reports() -> List[WeeklyWasteReport]:
    """Read weekly waste reports from file"""
    reports = []
    if not os.path.exists(WEEKLY_REPORTS_FILE):
        return reports
    
    try:
        with open(WEEKLY_REPORTS_FILE, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Parse dictionary strings back to dicts
                by_category = eval(row['by_category']) if row['by_category'] else {}
                by_reason = eval(row['by_reason']) if row['by_reason'] else {}
                by_item = eval(row['by_item']) if row['by_item'] else {}
                
                report = WeeklyWasteReport(
                    week_start=row['week_start'],
                    week_end=row['week_end'],
                    total_entries=int(row['total_entries']),
                    total_value=float(row['total_value']),
                    by_category=by_category,
                    by_reason=by_reason,
                    by_item=by_item
                )
                reports.append(report)
    except Exception:
        pass
    
    return reports

def get_week_comparison(weeks_back: int = 1) -> Tuple[Optional[WeeklyWasteReport], Optional[WeeklyWasteReport]]:
    """Get comparison between current week and previous week(s)"""
    reports = read_weekly_reports()
    if len(reports) < weeks_back + 1:
        return None, None
    
    current_report = reports[-1]
    previous_report = reports[-(weeks_back + 1)]
    
    return current_report, previous_report

def check_and_archive_if_needed():
    """Check if archival is needed and perform it"""
    try:
        if should_archive_waste_log():
            archive_waste_log()
            return True
        return False
    except Exception:
        # If archival fails, don't break the application
        return False
